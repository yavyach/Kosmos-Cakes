/* Каталог: viewport + Tilda unlock → Kosmo.Drum */
(function () {
  var grid = document.querySelector('.cover-grid');
  if (!grid) return;

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

  var parent = grid.parentElement;
  var embed = parent && parent.classList.contains('kosmos-catalog-embed') ? parent : null;
  var viewport = document.getElementById('catalog-scroll-viewport');
  if (!viewport) {
    viewport = document.createElement('div');
    viewport.id = 'catalog-scroll-viewport';
    viewport.className = 'catalog-scroll-viewport';
    if (embed) {
      embed.insertBefore(viewport, grid);
    } else {
      document.body.insertBefore(viewport, grid);
    }
    viewport.appendChild(grid);
  }

  document.documentElement.classList.add('catalog-ready');
  document.body.classList.add('catalog-ready');

  var el = viewport.parentElement;
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

  grid.querySelectorAll('.cover-grid__clone').forEach(function (node) { node.remove(); });

  if (!window.Kosmo || !Kosmo.Drum) {
    console.error('Kosmos.Drum не загружен — проверьте catalog-init.js / kosmo-drum.js');
    return;
  }

  Kosmo.Drum.bind({
    scrollEl: viewport,
    stripEl: grid,
    axis: 'y',
    speed: 2,
    pauseOnHidden: false
  });
})();
