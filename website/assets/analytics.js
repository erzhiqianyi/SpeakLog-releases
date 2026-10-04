// Google Analytics 4 衡量 ID。
window.SPEAKLOG_GA_ID = 'G-MB3812Z1TL';

window.dataLayer = window.dataLayer || [];
function gtag() { dataLayer.push(arguments); }
(function () {
  var id = window.SPEAKLOG_GA_ID;
  if (!id || /^G-X+$/.test(id)) return;
  var s = document.createElement('script');
  s.async = true;
  s.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(id);
  document.head.appendChild(s);
  gtag('js', new Date());
  gtag('config', id, { page_language: document.documentElement.lang });
})();
