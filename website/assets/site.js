// 逐词高亮演示
(function () {
  var words = Array.prototype.slice.call(document.querySelectorAll('#karaoke .w'))
    .filter(function (w) { return !/^[、。，,.!?！？]$/.test(w.textContent.trim()); });
  var fill = document.getElementById('fill');
  var tc = document.getElementById('tc');
  if (!words.length) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    words[words.length - 1].classList.add('on');
    return;
  }
  var i = 0;
  setInterval(function () {
    words.forEach(function (w) { w.classList.remove('on'); });
    if (i < words.length) words[i].classList.add('on');
    var p = Math.min(i / words.length, 1);
    fill.style.width = (p * 100) + '%';
    tc.textContent = '0:0' + Math.floor(p * 4);
    i = (i + 1) % (words.length + 2);
  }, 520);
})();

// GA4 事件：带 data-track 的链接、FAQ 展开
document.addEventListener('click', function (e) {
  var el = e.target.closest('[data-track]');
  if (!el) return;
  gtag('event', el.getAttribute('data-track'), {
    location: el.getAttribute('data-track-location') || '',
    link_text: el.textContent.trim()
  });
});
document.querySelectorAll('.faq details').forEach(function (d) {
  d.addEventListener('toggle', function () {
    if (d.open) gtag('event', 'faq_open', { question: d.querySelector('summary').textContent.trim() });
  });
});
