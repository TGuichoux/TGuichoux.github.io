#!/usr/bin/env python3
"""Regression tests for title precedence, escaping, poster fallbacks and launch checks.

By default builds with bundle exec jekyll from the real project directory.
All fixture edits are confined to a temporary copy; research content is untouched.
Requires PyYAML and BeautifulSoup4 (test dependencies only).
--build-driver is an optional external Ruby QA driver for restricted environments;
it is not used for normal local builds or the deployed website.
"""
import argparse
from pathlib import Path
import json, shutil, subprocess, tempfile, yaml
from bs4 import BeautifulSoup

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source',type=Path,default=Path(__file__).resolve().parent.parent)
parser.add_argument('--build-driver',type=Path)
parser.add_argument('--report',type=Path)
args=parser.parse_args()
source=args.source.resolve()
builder=args.build_driver.resolve() if args.build_driver else None
report={'checks':[], 'failures':[], 'scope':('Jekyll through external offline build driver' if builder else 'bundle exec jekyll build')+'; all fixture changes are temporary.'}
with tempfile.TemporaryDirectory(prefix='poster-title-fixtures-') as temp:
    root=Path(temp)/'website with spaces'
    shutil.copytree(source, root, ignore=shutil.ignore_patterns('docs', '__pycache__', '.jekyll-cache', '.bundle', 'vendor', '.git', '_site', '_site-*'))
    original_front=(root/'_data/frontpage.yml').read_text()
    original_videos=(root/'_data/videos.yml').read_text()
    original_config=(root/'_config.yml').read_text()
    base='/repository-test'
    output=Path(temp)/'output'
    def reset():
        (root/'_data/frontpage.yml').write_text(original_front)
        (root/'_data/videos.yml').write_text(original_videos)
        (root/'_config.yml').write_text(original_config)
        (root/'_data/video_posters.yml').unlink(missing_ok=True)
    def build():
        command=(['ruby',str(builder),str(root),str(output),base] if builder else
                 ['bundle','exec','jekyll','build','--source',str(root),'--destination',str(output),'--baseurl',base])
        result=subprocess.run(command,cwd=source,text=True,capture_output=True)
        assert result.returncode==0, result.stdout+result.stderr
        return BeautifulSoup((output/'index.html').read_text(),'html.parser')
    def first_video():
        return BeautifulSoup((output/'thesis/chapter-02/index.html').read_text(),'html.parser').video
    def test(name, fn):
        reset()
        try:
            details=fn()
            report['checks'].append({'test':name,'status':'passed','details':details})
        except Exception as e:
            report['failures'].append({'test':name,'error':str(e)})
    def title_case(value, expected, remove=False, config_title=None):
        if remove:
            (root/'_data/frontpage.yml').unlink()
        else:
            (root/'_data/frontpage.yml').write_text(yaml.safe_dump({'title':value},allow_unicode=True))
        if config_title is not None:
            cfg=yaml.safe_load(original_config); cfg['title']=config_title
            (root/'_config.yml').write_text(yaml.safe_dump(cfg,allow_unicode=True))
        doc=build()
        assert doc.select_one('#home-title').get_text(strip=True)==expected
        assert doc.title.get_text(strip=True)==expected
        assert not doc.select_one('#home-title').find(True)
        result=subprocess.run(['ruby',str(root/'scripts/check.rb'),'--baseurl',base,str(output)],text=True,capture_output=True)
        assert result.returncode==0,result.stdout+result.stderr
        return {'expected_title':expected,'heading_and_tab_match':True}
    title='Changed title — <Research> & "Demos"'
    test('edited title and HTML escaping',lambda:title_case(title,title))
    test('blank title falls back to site title',lambda:title_case('   ','Academic supplementary material'))
    test('missing frontpage file falls back to site title',lambda:title_case(None,'Academic supplementary material',remove=True))
    test('both titles blank fall back to Home',lambda:title_case('','Home',config_title=''))
    def poster_case(mode):
        data=yaml.safe_load(original_videos); item=data['ch02-2_1']; old_poster=item['poster']
        if mode!='explicit': item['poster']=''
        manifest={'ch02-2_1':{'src':item['src'],'poster':'/assets/posters/A-421.jpg'}}
        if mode=='stale': manifest['ch02-2_1']['src']='https://example.test/different.mp4'
        (root/'_data/videos.yml').write_text(yaml.safe_dump(data,sort_keys=False,allow_unicode=True))
        (root/'_data/video_posters.yml').write_text(yaml.safe_dump(manifest))
        build(); player=first_video()
        if mode=='stale':
            assert not player.get('poster')
            assert player.has_attr('data-first-frame')
        else:
            expected=base+(old_poster if mode=='explicit' else '/assets/posters/A-421.jpg')
            assert player['poster'].split('?')[0]==expected
            assert not player.has_attr('data-first-frame')
        return {'poster':player.get('poster'),'dynamic_fallback':player.has_attr('data-first-frame')}
    test('explicit poster wins over generated manifest',lambda:poster_case('explicit'))
    test('matching generated poster fallback',lambda:poster_case('matching'))
    test('stale generated poster is ignored',lambda:poster_case('stale'))
    def url_case(poster, expected_prefix):
        data=yaml.safe_load(original_videos); data['ch02-2_1']['poster']=poster
        (root/'_data/videos.yml').write_text(yaml.safe_dump(data,sort_keys=False))
        build(); actual=first_video()['poster']
        assert actual.startswith(expected_prefix),actual
        assert '&amp;' not in actual,actual
        if poster.startswith('https://'): assert actual==poster
        return {'poster':actual}
    test('local poster query and baseurl escaped once',lambda:url_case('/assets/posters/A-421.jpg?a=1&b=2',base+'/assets/posters/A-421.jpg?a=1&b=2&v='))
    test('external poster URL is not prefixed or altered',lambda:url_case('https://images.example.test/cover.jpg?a=1&b=2','https://images.example.test/cover.jpg?a=1&b=2'))
    def fail_missing():
        (root/'assets/posters/A-421.jpg').rename(root/'assets/posters/A-421.hidden')
        try:
            r=subprocess.run(['ruby',str(root/'scripts/check.rb'),'--source-only'],text=True,capture_output=True)
            assert r.returncode!=0 and 'missing local asset /assets/posters/A-421.jpg' in r.stderr
            return 'Validator rejected missing image as intended.'
        finally:
            (root/'assets/posters/A-421.hidden').rename(root/'assets/posters/A-421.jpg')
    test('source checker rejects missing poster',fail_missing)
    def fail_heading():
        build()
        p=output/'index.html'; text=p.read_text(); soup=BeautifulSoup(text,'html.parser')
        current=str(soup.select_one('#home-title'))
        # The source renderer escapes the apostrophe numerically, so replace by tag boundaries.
        import re
        p.write_text(re.sub(r'(<h1 id="home-title">).*?(</h1>)',r'\g<1>Wrong title\g<2>',text))
        r=subprocess.run(['ruby',str(root/'scripts/check.rb'),'--baseurl',base,str(output)],text=True,capture_output=True)
        assert r.returncode!=0 and 'home heading does not match' in r.stderr,r.stdout+r.stderr
        return 'Validator rejected incorrect built H1 as intended.'
    test('build checker rejects incorrect heading',fail_heading)
    def launcher():
        # Validate wrapper orchestration using a fake bundle, not a real server claim.
        fake=Path(temp)/'bin'; fake.mkdir(exist_ok=True)
        command=fake/'bundle'; command.write_text('#!/usr/bin/env bash\nprintf "%s|%s\\n" "$PWD" "$*" >> "$COMMAND_LOG"\nexit 0\n'); command.chmod(0o755)
        import os
        log=Path(temp)/'commands.log'
        env=dict(os.environ,PATH=str(fake)+':'+os.environ['PATH'],COMMAND_LOG=str(log))
        r=subprocess.run(['bash',str(root/'scripts/serve.sh'),'--port','4100'],cwd=temp,env=env,text=True,capture_output=True)
        assert r.returncode==0,r.stdout+r.stderr
        lines=log.read_text().splitlines()
        assert all(s.startswith(str(root)+'|') for s in lines),lines
        assert lines[-1].endswith('exec jekyll serve --livereload --baseurl  --port 4100'),lines
        return {'commands':lines,'scope':'wrapper only; bundle mocked; real source validator executed'}
    test('launcher pins directory with spaces and forwards arguments',launcher)
report['passed']=len(report['checks']); report['failed']=len(report['failures'])
output=args.report or source/'docs/validation/poster-title-fixtures.json'
output.parent.mkdir(parents=True,exist_ok=True)
output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(report,indent=2,ensure_ascii=False))
raise SystemExit(bool(report['failures']))
