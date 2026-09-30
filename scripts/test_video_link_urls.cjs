#!/usr/bin/env node
/* Execute the actual carousel script in a small DOM fixture. These are unit
 * tests of URL/event routing, not a replacement for the browser/HTTP tests. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const source = fs.readFileSync(path.resolve(__dirname, '../assets/js/carousel.js'), 'utf8');
const report = { scope: 'Actual production JS in a Node VM DOM fixture; URL/event-routing unit tests only', checks: [], failures: [] };
function fixture(base = '/repository-name') {
  const location = new URL('https://username.github.io' + base + '/thesis/chapter-06/?view=test');
  const events = {}, docEvents = {}, frames = new Map();
  let nextFrame = 0, scrolls = 0;
  const target = { nodeType: 1, parentElement: null,
    matches: s => s === '.media-video', querySelector: () => null,
    getBoundingClientRect: () => ({ height: 200 }),
    scrollIntoView: () => { scrolls += 1; } };
  const document = {
    baseURI: location.href, documentElement: { dataset: {} },
    querySelectorAll: () => [], getElementById: id => id === 'ch06-6-10' ? target : null,
    addEventListener: (name, handler) => { docEvents[name] = handler; }
  };
  const window = { location, innerHeight: 900, setTimeout: () => 1, clearTimeout: () => {},
    addEventListener: (name, handler) => { events[name] = handler; },
    requestAnimationFrame: fn => { frames.set(++nextFrame, fn); return nextFrame; },
    cancelAnimationFrame: id => frames.delete(id) };
  vm.runInNewContext(source, { document, window, console, URL }, { filename: 'carousel.js' });
  function click(href, attrs = {}, eventChanges = {}) {
    const anchor = { nodeType: 1, parentElement: null, matches: s => s === 'a[href]',
      getAttribute: name => name === 'href' ? href : (attrs[name] ?? null),
      hasAttribute: name => Object.prototype.hasOwnProperty.call(attrs, name) };
    const event = { target: anchor, button: 0, defaultPrevented: false,
      ctrlKey: false, metaKey: false, altKey: false, shiftKey: false,
      preventDefault() { this.defaultPrevented = true; }, ...eventChanges };
    docEvents.click(event);
    for (const fn of [...frames.values()]) fn();
    frames.clear();
    return { prevented: event.defaultPrevented, hash: location.hash, scrolls };
  }
  return { click, location, events };
}
function test(name, fn) {
  try { fn(); report.checks.push({ test: name, status: 'passed' }); }
  catch (e) { report.failures.push({ test: name, error: e.message }); }
}
for (const base of ['', '/repository-name']) {
  const current = 'https://username.github.io' + base + '/thesis/chapter-06/?view=test';
  for (const [name, href] of [
    ['fragment', '#ch06-6-10'],
    ['encoded fragment', '#ch06%2D6%2D10'],
    ['absolute same-page URL', current + '#ch06-6-10'],
    ['root-relative same-page URL', base + '/thesis/chapter-06/?view=test#ch06-6-10'],
    ['page-relative same-page URL', './?view=test#ch06-6-10'],
  ]) {
    test(name + ' at ' + (base || '/'), () => {
      const result = fixture(base).click(href);
      assert.equal(result.prevented, true);
      assert.equal(decodeURIComponent(result.hash), '#ch06-6-10');
      assert.equal(result.scrolls, 1);
    });
  }
}
for (const [name, href, attrs, event] of [
  ['external origin', 'https://elsewhere.example/thesis/chapter-06/#ch06-6-10', {}, {}],
  ['different page', '/repository-name/thesis/chapter-05/#ch06-6-10', {}, {}],
  ['different query', '?view=other#ch06-6-10', {}, {}],
  ['new tab', '#ch06-6-10', { target: '_blank' }, {}],
  ['named frame', '#ch06-6-10', { target: 'another-frame' }, {}],
  ['download', '#ch06-6-10', { download: '' }, {}],
  ['Control click', '#ch06-6-10', {}, { ctrlKey: true }],
  ['Command click', '#ch06-6-10', {}, { metaKey: true }],
  ['Shift click', '#ch06-6-10', {}, { shiftKey: true }],
  ['Alt click', '#ch06-6-10', {}, { altKey: true }],
  ['middle click', '#ch06-6-10', {}, { button: 1 }],
  ['right click', '#ch06-6-10', {}, { button: 2 }],
  ['unknown anchor', '#nonexistent', {}, {}],
  ['malformed encoding', '#%E0%A4%A', {}, {}],
  ['empty fragment', '#', {}, {}],
  ['unsafe scheme left unintercepted', 'javascript:void(0)', {}, {}],
]) {
  test('leave browser default intact: ' + name, () => {
    const result = fixture().click(href, attrs, event);
    assert.equal(result.prevented, false);
    assert.equal(result.hash, '');
    assert.equal(result.scrolls, 0);
  });
}
test('explicit _self remains an ordinary deep link', () => {
  const result = fixture().click('#ch06-6-10', { target: '_self' });
  assert.equal(result.prevented, true); assert.equal(result.scrolls, 1);
});
test('previously cancelled click is not processed', () => {
  const result = fixture().click('#ch06-6-10', {}, { defaultPrevented: true });
  assert.equal(result.hash, ''); assert.equal(result.scrolls, 0);
});
test('hash/history/restore listeners are registered once', () => {
  const f = fixture(); for (const name of ['hashchange', 'pageshow', 'popstate']) assert.equal(typeof f.events[name], 'function');
});
report.passed = report.checks.length;
report.failed = report.failures.length;
console.log(JSON.stringify(report, null, 2));
process.exitCode = report.failed ? 1 : 0;
