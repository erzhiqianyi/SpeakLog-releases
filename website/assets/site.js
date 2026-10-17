// The example illustrates subtitle styling; it is not an app screenshot.
(function () {
  var words = Array.prototype.slice.call(document.querySelectorAll('#karaoke .w'))
    .filter(function (w) { return !/^[、。，,.!?！？]$/.test(w.textContent.trim()); });
  var fill = document.getElementById('fill');
  var tc = document.getElementById('tc');
  if (!words.length || !fill || !tc) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    words[words.length - 1].classList.add('on');
    return;
  }
  var i = 0;
  // A single pass finishes within four active seconds; no endless animation.
  var timer = setInterval(function () {
    if (document.hidden) return;
    words.forEach(function (w) { w.classList.remove('on'); });
    if (i < words.length) words[i].classList.add('on');
    i += 1;
    var p = Math.min(i / words.length, 1);
    fill.style.width = (p * 100) + '%';
    tc.textContent = '0:0' + Math.floor(p * 4);
    if (i >= words.length) clearInterval(timer);
  }, Math.min(400, 4000 / words.length));
})();

// Analytics is optional. Blocking it must never break navigation or the FAQ.
(function () {
  function track(name, parameters) {
    if (typeof window.gtag !== 'function') return;
    parameters.page_language = document.documentElement.lang;
    try { window.gtag('event', name, parameters); } catch (_) { /* Best effort. */ }
  }
  document.addEventListener('click', function (e) {
    var target = e.target;
    var el = target && typeof target.closest === 'function' ? target.closest('[data-track]') : null;
    if (!el) return;
    track(el.getAttribute('data-track'), {
      location: el.getAttribute('data-track-location') || '',
      link_text: el.textContent.trim()
    });
  });
  document.querySelectorAll('.faq details').forEach(function (d) {
    d.addEventListener('toggle', function () {
      var summary = d.querySelector('summary');
      if (d.open && summary) track('faq_open', { question: summary.textContent.trim() });
    });
  });
})();

// Total installer downloads across all GitHub releases. Hidden until the count arrives.
(function () {
  var els = document.querySelectorAll('[data-downloads]');
  if (!els.length || typeof fetch !== 'function') return;
  var key = 'speaklog-downloads';
  function show(total) {
    if (!(total > 0)) return;
    var n = new Intl.NumberFormat(document.documentElement.lang).format(total);
    els.forEach(function (el) {
      el.textContent = el.getAttribute('data-label').replace('{n}', n) + ' · ';
      el.hidden = false;
    });
  }
  try {
    var cached = JSON.parse(sessionStorage.getItem(key) || 'null');
    if (cached && Date.now() - cached.at < 3600000) return show(cached.total);
  } catch (_) { /* Storage may be unavailable. */ }
  fetch('https://api.github.com/repos/erzhiqianyi/SpeakLog-releases/releases?per_page=100')
    .then(function (r) { return r.ok ? r.json() : Promise.reject(r.status); })
    .then(function (releases) {
      var total = 0;
      releases.forEach(function (release) {
        (release.assets || []).forEach(function (a) {
          if (/\.(pkg|dmg)$/i.test(a.name)) total += a.download_count || 0;
        });
      });
      try { sessionStorage.setItem(key, JSON.stringify({ total: total, at: Date.now() })); } catch (_) { /* Ignore. */ }
      show(total);
    })
    .catch(function () { /* Leave the count hidden. */ });
})();
