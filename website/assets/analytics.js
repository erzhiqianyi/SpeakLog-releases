// Google Analytics 4。上线前把下面的占位符换成真实的衡量 ID；
// 还是占位符时不会加载任何 Google 脚本，gtag() 调用只进本地 dataLayer。
window.SPEAKLOG_GA_ID = 'G-XXXXXXXXXX';

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
