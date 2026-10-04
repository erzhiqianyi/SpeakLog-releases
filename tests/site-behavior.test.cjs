// No DOM library, browser installation, network requests or analytics transmission.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const site = fs.readFileSync(path.join(__dirname, '../website/assets/site.js'), 'utf8');
const analytics = fs.readFileSync(path.join(__dirname, '../website/assets/analytics.js'), 'utf8');

function word(text) {
  const classes = new Set();
  return { textContent: text, classList: { add: c => classes.add(c), remove: c => classes.delete(c), contains: c => classes.has(c) } };
}
function setup(options = {}) {
  const handlers = {}, events = [], timers = [], scripts = [];
  const words = options.words || [];
  const fill = options.missingFill ? null : { style: { width: '0%' } };
  const tc = options.missingTime ? null : { textContent: '0:00' };
  const faq = { open: false, textContent: 'Answer', listeners: {},
    addEventListener(name, fn) { this.listeners[name] = fn; },
    querySelector() { return options.missingSummary ? null : { textContent: '  Why SpeakLog?  ' }; } };
  const document = {
    hidden: false, documentElement: { lang: options.lang || 'en' },
    querySelectorAll(selector) { return selector === '#karaoke .w' ? words : selector === '.faq details' ? [faq] : []; },
    getElementById(id) { return id === 'fill' ? fill : id === 'tc' ? tc : null; },
    addEventListener(name, fn) { handlers[name] = fn; },
    createElement(tag) { return { tagName: tag }; },
    head: { appendChild(script) { scripts.push(script); } },
  };
  const context = { document, console, Date, encodeURIComponent,
    location: { hostname: options.hostname || 'speak.erzhiqian.cc' },
    matchMedia() { return { matches: Boolean(options.reducedMotion) }; },
    setInterval(fn, delay) { timers.push({ fn, delay, active: true }); return timers.length; },
    clearInterval(id) { if (timers[id - 1]) timers[id - 1].active = false; },
  };
  context.window = context;
  if (options.analytics !== false) {
    context.gtag = (...args) => {
      if (options.analyticsThrows) throw new Error('Blocked analytics');
      events.push(args);
    };
  }
  vm.createContext(context);
  vm.runInContext(site, context, { timeout: 1000 });
  return { context, document, words, fill, tc, faq, handlers, events, timers, scripts };
}
function click(env, event, location = 'hero') {
  const link = { textContent: '  Download for Mac  ', getAttribute(name) { return { 'data-track': event, 'data-track-location': location }[name]; } };
  env.handlers.click({ target: { closest(selector) { assert.equal(selector, '[data-track]'); return link; } } });
}

test('content-only pages attach analytics without a demo timer', () => {
  const env = setup();
  assert.equal(env.timers.length, 0);
  assert.equal(typeof env.handlers.click, 'function');
});
test('partial demo DOM never crashes or starts a timer', () => {
  for (const missing of ['missingFill', 'missingTime']) {
    const env = setup({ words: [word('hello')], [missing]: true });
    assert.equal(env.timers.length, 0);
  }
});
test('reduced motion shows a static word and creates no animation timer', () => {
  const words = [word('hello'), word('world')];
  const env = setup({ words, reducedMotion: true });
  assert.equal(env.timers.length, 0);
  assert.equal(words[1].classList.contains('on'), true);
});
test('animation skips punctuation, pauses hidden tabs and stops after one pass', () => {
  const words = [word('hello'), word('、'), word('world')];
  const env = setup({ words });
  assert.equal(env.timers.length, 1);
  const tick = env.timers[0].fn;
  tick();
  assert.equal(words[0].classList.contains('on'), true);
  assert.equal(env.fill.style.width, '50%');
  assert.equal(env.tc.textContent, '0:02');
  env.document.hidden = true;
  tick();
  assert.equal(words[0].classList.contains('on'), true);
  assert.equal(env.timers[0].active, true);
  assert.equal(env.fill.style.width, '50%');
  env.document.hidden = false;
  tick();
  assert.equal(words[0].classList.contains('on'), false);
  assert.equal(words[1].classList.contains('on'), false);
  assert.equal(words[2].classList.contains('on'), true);
  assert.equal(env.fill.style.width, '100%');
  assert.equal(env.tc.textContent, '0:04');
  assert.equal(env.timers[0].active, false);
  assert.ok(env.timers[0].delay * 2 <= 4000);
});
test('long demo still finishes within four active seconds and clears its timer', () => {
  const words = Array.from({ length: 100 }, () => word('hello'));
  const env = setup({ words });
  const timer = env.timers[0];
  assert.ok(timer.delay * words.length <= 4000);
  for (let i = 0; i < words.length; i++) {
    assert.equal(timer.active, true);
    timer.fn();
  }
  assert.equal(timer.active, false);
  assert.equal(env.fill.style.width, '100%');
});
test('package and release clicks stay distinct and include page language', () => {
  const env = setup({ lang: 'ja' });
  click(env, 'package_download_click', 'download');
  click(env, 'release_page_click', 'releases');
  assert.deepEqual(env.events.map(e => e[1]), ['package_download_click', 'release_page_click']);
  assert.equal(env.events[0][2].location, 'download');
  assert.equal(env.events[0][2].link_text, 'Download for Mac');
  assert.equal(env.events[0][2].page_language, 'ja');
});
test('click tracking never calls preventDefault and handles untracked or non-element targets', () => {
  const env = setup();
  for (const target of [null, {}, { closest: () => null }]) {
    assert.doesNotThrow(() => env.handlers.click({ target, preventDefault() { throw new Error('Navigation blocked'); } }));
  }
  assert.equal(env.events.length, 0);
});
test('missing or throwing analytics cannot break clicks or FAQ interaction', () => {
  for (const options of [{ analytics: false }, { analyticsThrows: true }]) {
    const env = setup(options);
    assert.doesNotThrow(() => click(env, 'package_download_click'));
    env.faq.open = true;
    assert.doesNotThrow(() => env.faq.listeners.toggle());
  }
});
test('FAQ emits only on opening and tolerates a missing summary', () => {
  const env = setup();
  env.faq.listeners.toggle();
  assert.equal(env.events.length, 0);
  env.faq.open = true;
  env.faq.listeners.toggle();
  assert.equal(env.events.length, 1);
  assert.equal(env.events[0][1], 'faq_open');
  assert.equal(env.events[0][2].question, 'Why SpeakLog?');
  env.faq.open = false;
  env.faq.listeners.toggle();
  assert.equal(env.events.length, 1);
  const malformed = setup({ missingSummary: true });
  malformed.faq.open = true;
  assert.doesNotThrow(() => malformed.faq.listeners.toggle());
});
test('analytics initialization preserves queued events and adds language to page config', () => {
  const env = setup({ analytics: false, lang: 'zh-CN' });
  const previous = ['previous'];
  env.context.dataLayer = [previous];
  vm.runInContext(analytics, env.context, { timeout: 1000 });
  assert.equal(env.context.dataLayer[0], previous);
  assert.equal(env.scripts.length, 1);
  assert.match(env.scripts[0].src, /^https:\/\/www\.googletagmanager\.com\/gtag\/js\?id=G-/);
  assert.equal(env.scripts[0].async, true);
  const config = env.context.dataLayer.find(args => args[0] === 'config');
  assert.equal(config[2].page_language, 'zh-CN');
});
test('local and preview pages do not inject remote analytics or send page views', () => {
  for (const hostname of ['localhost', '127.0.0.1', 'preview.speaklog.pages.dev', 'speaklog.pages.dev']) {
    const env = setup({ analytics: false, hostname });
    vm.runInContext(analytics, env.context, { timeout: 1000 });
    assert.equal(env.scripts.length, 0, hostname);
    assert.equal(env.context.dataLayer.length, 0, hostname);
  }
});
