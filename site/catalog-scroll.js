/* Разблокировка прокрутки каталога внутри Tilda и других обёрток с overflow:hidden. */
(function () {
  var root = document.querySelector('.cover-grid');
  if (!root) return;
  document.documentElement.classList.add('catalog-page');
  document.body.classList.add('catalog-page');
  document.documentElement.style.overflowY = 'auto';
  document.body.style.overflowY = 'auto';
  document.documentElement.style.height = 'auto';
  document.body.style.height = 'auto';
  var el = root.parentElement;
  for (var i = 0; i < 12 && el; i++, el = el.parentElement) {
    if (el === document.body || el === document.documentElement) break;
    el.style.setProperty('overflow', 'visible', 'important');
    el.style.setProperty('overflow-y', 'visible', 'important');
    el.style.setProperty('height', 'auto', 'important');
    el.style.setProperty('max-height', 'none', 'important');
  }
})();
