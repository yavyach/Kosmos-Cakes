/* Прокрутка каталога на kosmos-cake.ru (Tilda): #allrecords по умолчанию overflow:hidden. */
(function () {
  var root = document.querySelector('.cover-grid');
  if (!root) return;

  document.documentElement.classList.add('catalog-page');
  document.body.classList.add('catalog-page');

  function unlock(el) {
    if (!el) return;
    el.style.setProperty('overflow-x', 'hidden', 'important');
    el.style.setProperty('overflow-y', 'auto', 'important');
    el.style.setProperty('height', 'auto', 'important');
    el.style.setProperty('min-height', '100%', 'important');
    el.style.setProperty('max-height', 'none', 'important');
  }

  unlock(document.getElementById('allrecords'));
  unlock(document.documentElement);
  unlock(document.body);

  var el = root.parentElement;
  for (var i = 0; i < 16 && el; i++, el = el.parentElement) {
    if (el === document.documentElement) break;
    if (el.id === 'allrecords') {
      unlock(el);
      continue;
    }
    if (el.classList && (
      el.classList.contains('t-rec') ||
      el.classList.contains('t396') ||
      el.classList.contains('r') ||
      el.classList.contains('kosmos-catalog-embed')
    )) {
      el.style.setProperty('overflow', 'visible', 'important');
      el.style.setProperty('height', 'auto', 'important');
      el.style.setProperty('max-height', 'none', 'important');
    }
  }
})();
