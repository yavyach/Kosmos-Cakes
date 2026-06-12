/* Универсальная полоска точек: карусели и выбор зоны доставки. */
(function(global){
  function visibleDots(container){
    return Array.prototype.filter.call(
      container.querySelectorAll('.kosmos-dot'),
      function(d){ return !d.classList.contains('is-hidden'); }
    );
  }

  function mount(container, options){
    if (!container) return null;
    options = options || {};
    var variant = options.variant || 'carousel';
    var extra = options.modifier || '';
    var preserved = (container.getAttribute('class') || '').split(/\s+/).filter(function(c){
      return c && c !== 'kosmos-dots' && !/^kosmos-dots--/.test(c) &&
        c !== 'is-hidden' && c !== 'kosmos-dots--empty';
    });
    preserved.push('kosmos-dots', 'kosmos-dots--' + variant);
    if (extra) preserved.push(extra);
    container.className = preserved.join(' ');
    container.innerHTML = '';

    var items = options.items || [];
    var dots = [];
    for (var i = 0; i < items.length; i++){
      var item = items[i];
      var dot = document.createElement('button');
      dot.type = 'button';
      dot.className = 'kosmos-dot';
      if (variant === 'zones'){
        dot.classList.add(item.cls);
        dot.dataset.key = item.key;
        dot.dataset.rate = String(item.rate);
        dot.dataset.name = item.name;
        if (item.pickup) dot.dataset.pickup = '1';
        dot.setAttribute('aria-label', item.name);
      } else {
        dot.setAttribute('aria-label', 'к слайду ' + (i + 1));
        dot.style.pointerEvents = 'auto';
      }
      container.appendChild(dot);
      dots.push(dot);
    }
    syncLayout(container);
    return {
      dots: dots,
      syncLayout: function(){ syncLayout(container); },
      setActive: function(index){
        dots.forEach(function(d, i){
          d.classList.toggle('is-active', i === index);
        });
      },
      setHidden: function(key, hidden){
        var d = container.querySelector('[data-key="' + key + '"]');
        if (d) d.classList.toggle('is-hidden', !!hidden);
        syncLayout(container);
      },
      getButton: function(key){
        return container.querySelector('[data-key="' + key + '"]');
      }
    };
  }

  function syncLayout(container){
    var n = visibleDots(container).length;
    container.classList.toggle('kosmos-dots--empty', n === 0);
  }

  function bindCarousel(carouselId, dotsId){
    var car = document.getElementById(carouselId);
    var dotsBox = document.getElementById(dotsId);
    if (!car || !dotsBox) return null;
    var meta = car.__kLoop;
    var originals = meta ? meta.kids : Array.prototype.slice.call(car.children);
    if (!originals.length || originals.length < 2) return null;

    var isSmall = dotsBox.classList.contains('mob-dots--small') ||
      dotsBox.classList.contains('kosmos-dots--small');
    var strip = mount(dotsBox, {
      variant: 'carousel',
      modifier: isSmall ? 'kosmos-dots--small' : '',
      items: originals.map(function(){ return {}; })
    });
    if (!strip) return null;

    strip.dots.forEach(function(dot, i){
      dot.addEventListener('click', function(){
        var target = originals[i];
        if (target && target.scrollIntoView){
          target.scrollIntoView({behavior:'smooth', block:'nearest', inline:'center'});
        }
      });
    });
    strip.setActive(0);

    var prev = 0;
    function update(){
      var w = car.clientWidth || 1;
      var idxRaw = Math.round(car.scrollLeft / w);
      var i = ((idxRaw % originals.length) + originals.length) % originals.length;
      if (i === prev) return;
      strip.setActive(i);
      prev = i;
    }
    car.addEventListener('scroll', function(){
      window.requestAnimationFrame(update);
    }, {passive:true});
    return strip;
  }

  global.Kosmos = global.Kosmos || {};
  global.Kosmos.Dots = {
    mount: mount,
    syncLayout: syncLayout,
    bindCarousel: bindCarousel
  };
})(window);
