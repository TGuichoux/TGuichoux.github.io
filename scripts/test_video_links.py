#!/usr/bin/env python3
"""Stress-test permanent video anchors against an actual Jekyll build.

Dependencies (tests only): playwright, beautifulsoup4, Pillow. Normal mode serves the
unchanged build over HTTP. --offline-dom loads the exact rendered HTML with
set_content, rewriting only root-relative resource URLs to a routed test origin.
It tests actual JS/CSS/HTML/images and native same-document history, but NOT
HTTP browser navigation, real Back/Forward-cache restores, or Safari.
All MP4 requests are rejected and counted: opening a poster/deep link must not
fetch a movie. MathJax is stubbed; live external services are outside this test.
"""
from __future__ import annotations

import argparse
import functools
import http.server
import io
import json
import mimetypes
from pathlib import Path
import re
import threading
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup
from PIL import Image, ImageChops, ImageOps, ImageStat
from playwright.sync_api import sync_playwright


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site', type=Path, default=Path('_site'))
    parser.add_argument('--baseurl', default='')
    parser.add_argument('--browser-executable')
    parser.add_argument('--offline-dom', action='store_true')
    parser.add_argument('--widths', default='375,390,640,768,1024,1440')
    parser.add_argument('--initial-widths', default='390,1440')
    parser.add_argument('--report', type=Path, default=Path('docs/validation/stage3-video-links.json'))
    parser.add_argument('--screenshots', type=Path)
    args = parser.parse_args()
    root = args.site.resolve()
    if not (root/'index.html').is_file():
        parser.error('Build Jekyll first; --site must point to the generated site.')
    base = args.baseurl.rstrip('/')
    widths = [int(x) for x in args.widths.split(',') if x]
    initial_widths = [int(x) for x in args.initial_widths.split(',') if x]
    report = {
        'mode': 'offline rendered DOM + native same-document history' if args.offline_dom else 'localhost HTTP browser navigation',
        'baseurl': base, 'widths': widths, 'initial_widths': initial_widths,
        'limitations': ['Live MP4 services and MathJax are not tested.',
                        'pageshow persisted is simulated, not a real bfcache restoration.',
                        'Chromium only; no macOS Safari or iOS device certification.'],
        'checks': [], 'failures': [], 'inventory': []}
    inventory = {}
    for file in sorted(root.rglob('*.html')):
        relative = file.relative_to(root).as_posix()
        soup = BeautifulSoup(file.read_text(encoding='utf-8'), 'html.parser')
        ids = [node['id'] for node in soup.select('[id]')]
        if len(ids) != len(set(ids)):
            report['failures'].append({'test': 'unique IDs in HTML document', 'page': relative})
        entries = []
        for figure in soup.select('figure.media-video[id]'):
            group = figure.find_parent(attrs={'data-video-carousel': True})
            slide = figure.find_parent(attrs={'data-carousel-slide': True})
            index = group.select('[data-carousel-slide]').index(slide) if slide else None
            player = figure.select_one('video')
            entry = {'id': figure['id'], 'carousel': group['id'] if group else None,
                     'index': index, 'poster': player.get('poster', ''),
                     'src': player.select_one('source')['src'],
                     'path': base+'/'+relative.removesuffix('index.html')+'#'+figure['id']}
            assert entry['poster'], f'Missing static poster in {relative}#{entry["id"]}'
            entries.append(entry)
            report['inventory'].append(dict(page=relative, **entry))
        if entries:
            inventory[relative] = entries

    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def do_GET(self):
            if base and self.path.startswith(base+'/'):
                self.path = self.path[len(base):]
            super().do_GET()

    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Handler, directory=str(root)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = 'https://site.test' if args.offline_dom else f'http://127.0.0.1:{server.server_port}'
    try:
        with sync_playwright() as pw:
            options = {'headless': True}
            if args.browser_executable:
                options['executable_path'] = args.browser_executable
            browser = pw.chromium.launch(**options)
            report['browser'] = 'Chromium '+browser.version

            def session(width, javascript=True, block_menu=False, hold_math=False, legacy=False):
                context = browser.new_context(viewport={'width': width, 'height': 900},
                                              is_mobile=width <= 640, has_touch=width <= 640,
                                              java_script_enabled=javascript)
                page = context.new_page()
                page.set_default_timeout(4000)
                state = {'errors': [], 'movies': [], 'missing': [], 'pending': []}
                page.on('pageerror', lambda error: state['errors'].append(str(error)))
                if legacy:
                    script='window.ResizeObserver=undefined;window.IntersectionObserver=undefined;'
                    page.add_init_script(script)
                    if args.offline_dom:
                        page.evaluate(script)

                def route_request(route):
                    url = urlparse(route.request.url)
                    if url.path.lower().endswith('.mp4'):
                        state['movies'].append(route.request.url)
                        route.fulfill(status=503, body='MP4 requests are not allowed in a static-poster test.')
                    elif url.netloc == 'cdn.jsdelivr.net':
                        if hold_math:
                            state['pending'].append(route)
                        else:
                            route.fulfill(body='/* MathJax excluded from media-link QA. */',content_type='application/javascript')
                    elif url.netloc == 'site.test':
                        path = unquote(url.path)
                        if base and path.startswith(base+'/'):
                            path=path[len(base):]
                        resource=root/path.lstrip('/')
                        if block_menu and resource.name == 'site.js':
                            route.abort()
                        elif resource.is_file():
                            route.fulfill(path=str(resource), content_type=mimetypes.guess_type(resource)[0] or 'application/octet-stream')
                        else:
                            state['missing'].append(route.request.url)
                            route.fulfill(status=404,body='Missing local test resource')
                    elif block_menu and url.path.endswith('/assets/js/site.js'):
                        route.abort()
                    else:
                        route.continue_()
                page.route('**/*',route_request)
                return context,page,state

            def close(context,state):
                for route in state['pending']:
                    try:
                        route.abort()
                    except Exception:
                        pass
                context.close()

            def load(page,relative,hash_value='',held=False):
                if args.offline_dom:
                    page.evaluate('(h)=>history.replaceState(null,"",h||"#")',hash_value)
                    text=(root/relative).read_text(encoding='utf-8')
                    text=re.sub(r'\b(src|href|poster)="(/[^\"]*)"',lambda m:f'{m[1]}="{origin}{m[2]}"',text)
                    page.set_content(text,wait_until='commit' if held else 'load',timeout=15000)
                else:
                    page.goto(origin+base+'/'+relative.removesuffix('index.html')+hash_value,
                              wait_until='commit' if held else 'load',timeout=15000)

            def verify(page, entry, enhanced=True):
                ident=entry['id']
                page.wait_for_function('id=>document.getElementById(id)!==null',arg=ident)
                if enhanced:
                    page.wait_for_function("document.documentElement.dataset.carouselVersion === '3.2.0'")
                # The production handler uses a frame after fragment scrolling.
                page.wait_for_function('''a=>{
                    const f=document.getElementById(a.id), v=f.querySelector('video');
                    const r=v.getBoundingClientRect();
                    if (r.bottom<=0 || r.top>=innerHeight || r.left < -2 || r.right > innerWidth+2) return false;
                    if (r.height<innerHeight-50 && (r.top < -2 || r.bottom > innerHeight+2)) return false;
                    const c=f.closest('[data-video-carousel]');
                    if(!c || !a.enhanced) return true;
                    const t=c.querySelector('[data-carousel-slides]'),s=f.closest('[data-carousel-slide]');
                    return c.dataset.activeSlide===String(a.index+1) &&
                        Math.abs(s.getBoundingClientRect().left-t.getBoundingClientRect().left)<2;
                }''',arg={'id':ident,'index':entry['index'],'enhanced':enhanced})
                result=page.evaluate('''a=>{
                    const f=document.getElementById(a.id),v=f.querySelector('video'),c=f.closest('[data-video-carousel]');
                    const t=c&&c.querySelector('[data-carousel-slides]');
                    const s=f.closest('[data-carousel-slide]'),r=v.getBoundingClientRect();
                    return {paused:v.paused,time:v.currentTime,preload:v.preload,poster:v.getAttribute('poster'),
                        hidden:f.hidden||!!(s&&s.hidden),playing:[...document.querySelectorAll('video')].filter(v=>!v.paused).length,
                        counter:c&&c.querySelector('[data-carousel-counter]').textContent.trim(),
                        select:c&&c.querySelector('select').value,count:c&&c.querySelectorAll('[data-carousel-slide]').length,
                        left:s?Math.abs(s.getBoundingClientRect().left-t.getBoundingClientRect().left):0,
                        overflow:document.documentElement.scrollWidth>innerWidth+2,rect:{top:r.top,bottom:r.bottom}};
                }''',{'id':ident})
                assert result['paused'] and result['time']==0 and result['playing']==0, result
                assert result['preload']=='none' and result['poster'] and not result['hidden'],result
                assert not result['overflow'] and result['left']<2,result
                if entry['carousel'] and enhanced:
                    assert result['select']==str(entry['index']),result
                    assert result['counter']==f"{entry['index']+1} / {result['count']}",result
                # Decode the real JPEG. Script-created Image loads are not
                # available when scripting is disabled; compare actual rendered
                # player pixels to the JPEG in that case instead.
                if enhanced:
                    page.evaluate("id=>{window.__qaPoster=new Image();window.__qaPoster.src=document.getElementById(id).querySelector('video').poster;}",ident)
                    page.wait_for_function("window.__qaPoster.complete && window.__qaPoster.naturalWidth>0")
                    dimensions=page.evaluate("[window.__qaPoster.naturalWidth,window.__qaPoster.naturalHeight]")
                    page.evaluate("delete window.__qaPoster")
                    assert min(dimensions)>0,dimensions
                else:
                    player=page.locator('#'+ident+' video')
                    actual=Image.open(io.BytesIO(player.screenshot())).convert('RGB')
                    poster_path=unquote(urlparse(entry['poster']).path)
                    if base and poster_path.startswith(base+'/'):
                        poster_path=poster_path[len(base):]
                    with Image.open(root/poster_path.lstrip('/')) as poster:
                        fitted=ImageOps.contain(poster.convert('RGB'),actual.size,Image.Resampling.LANCZOS)
                    expected=Image.new('RGB',actual.size,(23,36,43))
                    expected.paste(fitted,((actual.width-fitted.width)//2,(actual.height-fitted.height)//2))
                    crop=(int(actual.width*.1),int(actual.height*.1),int(actual.width*.9),int(actual.height*.65))
                    error=sum(ImageStat.Stat(ImageChops.difference(actual.crop(crop),expected.crop(crop))).mean)/3
                    assert error<18,{'poster_pixel_mean_absolute_error':error,'limit':18}

            def record(name,fn,**metadata):
                try:
                    fn()
                    report['checks'].append(dict(test=name,status='passed',**metadata))
                except Exception as error:
                    report['failures'].append(dict(test=name,error=str(error),**metadata))
                    print('FAIL',name,metadata,error,flush=True)
                    import traceback
                    traceback.print_exc()

            def clean(state):
                assert not state['errors'],state['errors']
                assert not state['movies'],state['movies']
                assert not state['missing'],state['missing']

            for width in initial_widths:
                for relative,entries in inventory.items():
                    for entry in entries:
                        context,page,state=session(width)
                        def check_initial():
                            load(page,relative,'#'+entry['id'])
                            verify(page,entry);clean(state)
                        record('initial fragment before carousel initialization',check_initial,page=relative,id=entry['id'],width=width)
                        close(context,state)
                print('Initial-link matrix completed:',width,flush=True)

            for width in widths:
                for relative,entries in inventory.items():
                    context,page,state=session(width)
                    load(page,relative)
                    for entry in reversed(entries):
                        def change_hash():
                            page.evaluate('hash=>{location.hash=hash}',entry['id'])
                            verify(page,entry);clean(state)
                        record('same-document hash change',change_hash,page=relative,id=entry['id'],width=width)
                    close(context,state)
                print('Hash-change matrix completed:',width,flush=True)

            chapter='thesis/chapter-06/index.html'
            entries={e['id']:e for e in inventory[chapter]}
            first,last,middle=entries['ch06-6-1'],entries['ch06-6-10'],entries['ch06-6-5']
            for width in (390,1440):
                context,page,state=session(width)
                load(page,chapter,'#'+first['id']);verify(page,first)
                def history_check():
                    for entry in (middle,last):
                        page.evaluate('hash=>{location.hash=hash}',entry['id']);verify(page,entry)
                    page.evaluate('history.back()');verify(page,middle)
                    page.evaluate('history.back()');verify(page,first)
                    page.evaluate('history.forward()');verify(page,middle)
                    page.evaluate('history.forward()');verify(page,last)
                    clean(state)
                record('native same-document Back and Forward',history_check,width=width)
                def same_link():
                    page.evaluate('''id=>{let a=document.createElement('a');a.id='qa-link';a.href='#'+id;a.textContent='Video';document.body.prepend(a)}''',last['id'])
                    page.locator('[data-video-carousel]').first.locator('select').select_option('0')
                    before=page.evaluate('history.length')
                    page.locator('#qa-link').click();verify(page,last)
                    assert page.evaluate('history.length')==before
                    page.locator('#qa-link').evaluate('a=>a.remove()');clean(state)
                record('same hash reselects video without a duplicate history entry',same_link,width=width)
                def duplicate_source():
                    assert entries['ch06-6-8']['src']==entries['ch06-6-11']['src']
                    for ident in ('ch06-6-8','ch06-6-11','ch06-6-6','ch06-6-12','ch06-6-10','ch06-6-13'):
                        page.evaluate('hash=>{location.hash=hash}',ident);verify(page,entries[ident])
                    clean(state)
                record('duplicate MP4s have independently addressable occurrences',duplicate_source,width=width)
                def encoded():
                    page.evaluate("location.hash='ch06%2D6%2D10'");verify(page,last);clean(state)
                record('percent-encoded valid fragment',encoded,width=width)
                def malformed():
                    for fragment in ('#unknown-video','#%E0%A4%A','#%ZZ','#[]:not(*)','#%00','#main-content','#'):
                        page.evaluate('hash=>{location.hash=hash}',fragment)
                        page.wait_for_timeout(25)
                    clean(state)
                    page.evaluate('hash=>{location.hash=hash}',middle['id']);verify(page,middle)
                record('invalid and non-video fragments are harmless',malformed,width=width)
                def rapid():
                    page.evaluate('''ids=>{for(let i=0;i<60;i++){
                        history.replaceState(null,'','#'+ids[i%ids.length]);
                        window.dispatchEvent(new HashChangeEvent('hashchange'));
                    } history.replaceState(null,'','#ch06-6-5');window.dispatchEvent(new HashChangeEvent('hashchange'));}''',list(entries))
                    verify(page,middle);clean(state)
                record('61 rapid fragment notifications resolve to the latest target',rapid,width=width)
                def restoration():
                    page.locator('[data-video-carousel]').first.locator('select').select_option('0')
                    page.evaluate("window.dispatchEvent(new PageTransitionEvent('pageshow',{persisted:true}))")
                    verify(page,middle);clean(state)
                record('simulated persisted pageshow restores the linked slide',restoration,width=width)
                def no_late_jump():
                    page.locator('[data-video-carousel]').first.locator('select').select_option('0')
                    page.evaluate("window.dispatchEvent(new PageTransitionEvent('pageshow',{persisted:false}))")
                    page.wait_for_timeout(100)
                    assert page.locator('[data-video-carousel]').first.get_attribute('data-active-slide')=='1'
                record('ordinary late pageshow does not undo manual carousel navigation',no_late_jump,width=width)
                def resizes():
                    page.evaluate('hash=>{location.hash=hash}',last['id']);verify(page,last)
                    for w in (375,1440,768,390,width):
                        page.set_viewport_size({'width':w,'height':900})
                        # Responsive reflow preserves selection; reveal via hash
                        # is not needed to preserve horizontal alignment.
                        page.wait_for_function("document.querySelector('[data-video-carousel]').dataset.activeSlide==='10'")
                        offset=page.locator('#'+last['id']).evaluate("f=>Math.abs(f.getBoundingClientRect().left-f.closest('[data-carousel-slides]').getBoundingClientRect().left)")
                        if offset>2:
                            page.wait_for_timeout(150)
                            offset=page.locator('#'+last['id']).evaluate("f=>Math.abs(f.getBoundingClientRect().left-f.closest('[data-carousel-slides]').getBoundingClientRect().left)")
                        assert offset<=2,offset
                    clean(state)
                record('linked slide survives repeated responsive resizes',resizes,width=width)
                def visibility():
                    page.evaluate('hash=>{location.hash=hash}',middle['id']);verify(page,middle)
                    page.evaluate("window.dispatchEvent(new HashChangeEvent('hashchange'))")
                    verify(page,middle)
                    if args.screenshots:
                        args.screenshots.mkdir(parents=True,exist_ok=True)
                        page.screenshot(path=str(args.screenshots/f'deep-link-{width}.png'))
                    clean(state)
                record('target video fully visible and static poster decoded',visibility,width=width)
                def lazy_shift():
                    page.evaluate('hash=>{location.hash=hash}',entries['ch06-6-13']['id'])
                    verify(page,entries['ch06-6-13'])
                    page.evaluate("(()=>{const gap=document.createElement('div');gap.id='qa-layout-shift';gap.style.height='600px';document.getElementById('ch06-6-13').before(gap);})()")
                    verify(page,entries['ch06-6-13']);clean(state)
                    page.locator('#qa-layout-shift').evaluate('e=>e.remove()')
                record('arrival corrects a late 600px layout shift',lazy_shift,width=width)
                def manual_wins():
                    page.evaluate('hash=>{location.hash=hash}',last['id']);verify(page,last)
                    page.locator('[data-video-carousel]').first.locator('select').select_option('0')
                    page.evaluate("(()=>{const gap=document.createElement('div');gap.id='qa-manual-shift';gap.style.height='200px';document.querySelector('main').prepend(gap);})()")
                    page.wait_for_timeout(150)
                    assert page.locator('[data-video-carousel]').first.get_attribute('data-active-slide')=='1'
                    page.locator('#qa-manual-shift').evaluate('e=>e.remove()');clean(state)
                record('manual carousel choice cancels arrival realignment',manual_wins,width=width)
                close(context,state)

            for name,options in [('menu script unavailable',{'block_menu':True}),
                                 ('legacy observer fallbacks',{'legacy':True}),
                                 ('MathJax pending',{'hold_math':True})]:
                context,page,state=session(768 if options.get('legacy') else 390,**options)
                def unavailable():
                    destination=entries['ch06-6-13'] if options.get('legacy') else last
                    load(page,chapter,'#'+destination['id'],held=options.get('hold_math',False))
                    verify(page,destination);clean(state)
                    if options.get('hold_math'):
                        assert state['pending'],'No MathJax request was held.'
                record('initial link with '+name,unavailable)
                close(context,state)

            # Native link fallback with scripts disabled; no enhanced counter is promised.
            for width in (390,1440):
                context,page,state=session(width,javascript=False)
                def no_js():
                    load(page,chapter)
                    page.evaluate('''()=>{const a=document.createElement('a');a.href='#ch06-6-10';a.id='qa-native';a.textContent='Video';document.body.prepend(a)}''')
                    page.locator('#qa-native').click()
                    page.wait_for_timeout(200)  # Let native fragment navigation finish.
                    verify(page,last,enhanced=False);clean(state)
                    assert not page.locator('[data-carousel-controls]').first.is_visible()
                record('native deep-link navigation with JavaScript disabled',no_js,width=width)
                close(context,state)
            browser.close()
    finally:
        server.shutdown()
    report['passed']=len(report['checks']);report['failed']=len(report['failures'])
    report['video_occurrences']=sum(map(len,inventory.values()))
    report['unique_video_ids']=len({e['id'] for rows in inventory.values() for e in rows})
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(f"{report['passed']} passed; {report['failed']} failed. {args.report}")
    return int(bool(report['failed']))


if __name__=='__main__':
    raise SystemExit(main())
