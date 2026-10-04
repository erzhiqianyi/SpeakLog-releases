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
