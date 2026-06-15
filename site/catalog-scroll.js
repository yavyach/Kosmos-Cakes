/* Каталог: разблокировка Tilda, без автоскролла (барабан только на карточках торта). */
(function () {
  var grid = document.querySelector('.cover-grid');
  if (!grid) return;

  document.documentElement.classList.add('catalog-page', 'catalog-ready');
  document.body.classList.add('catalog-page', 'catalog-ready');

  function unlock(el) {
    if (!el) return;
    el.style.setProperty('overflow-x', 'hidden', 'important');
    el.style.setProperty('overflow-y', 'auto', 'important');
    el.style.setProperty('height', 'auto', 'important');
    el.style.setProperty('min-height', '100%', 'important');
    el.style.setProperty('max-height', 'none', 'important');
  }

  unlock(document.getElementById('allrecords'));

  var viewport = document.getElementById('catalog-scroll-viewport');
  if (viewport && viewport.__kDrum && viewport.__kDrum.kill) viewport.__kDrum.kill();
  if (viewport && grid.parentElement === viewport) {
    viewport.parentElement.insertBefore(grid, viewport);
    viewport.remove();
  }

  grid.querySelectorAll('.cover-grid__clone, .k-loop-clone').forEach(function (node) {
    node.remove();
  });
  grid.classList.remove('k-loop-auto', 'k-loop-dragging');
  if (grid.__kDrum && grid.__kDrum.kill) grid.__kDrum.kill();

  grid.querySelectorAll('.cover img').forEach(function (img) {
    img.style.animation = 'none';
    img.style.transform = 'none';
    img.style.willChange = 'auto';
    img.style.height = '100%';
  });

  var el = grid.parentElement;
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
