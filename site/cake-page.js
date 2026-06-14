/* Меню удалено: кнопка «К» теперь — простая ссылка-каталог (см. шаблон). */

  (function setupEmbedBack(){
    const back = document.querySelector('.back-to-catalog');
    if (!back) return;
    if (new URLSearchParams(location.search).get('embed') !== 'kosmos') return;
    back.setAttribute('href', '#');
    back.addEventListener('click', (e) => {
      e.preventDefault();
      if (window.parent !== window) window.parent.postMessage('kosmos-close-cake', '*');
      else location.href = 'https://kosmos-cake.ru/';
    });
  })();

  (function fitCakeTitle(){
    const title = document.querySelector('.col-info .cake-title');
    if (!title) return;
    const raw = title.textContent.trim();
    const ws = raw.split(/\s+/);
    const groups = (ws.length >= 4)
      ? ws.reduce((a, w, i) => { if (i % 2 === 0) a.push([w]); else a[a.length-1].push(w); return a; }, []).map(g => g.join('\u00a0'))
      : ws;
    title.innerHTML = groups.map(w => `<span class="word">${w}</span>`).join('');
    const mq = window.matchMedia('(max-width: 900px)');
    function fit(){
      const isMob = mq.matches;
      const MAX = isMob ? 200 : 160, MIN = isMob ? 32 : 28, TARGET = isMob ? 0.94 : 0.96;
      const cw = title.clientWidth;
      if (!cw) return;
      title.querySelectorAll('.word').forEach(word => {
        word.style.fontSize = MAX + 'px';
        const w = word.scrollWidth;
        if (!w) return;
        let size = MAX * (cw * TARGET / w);
        size = Math.max(MIN, Math.min(MAX, size));
        word.style.fontSize = size + 'px';
      });
    }
    fit();
    window.addEventListener('resize', fit);
    if (mq.addEventListener) mq.addEventListener('change', fit);
    else if (mq.addListener) mq.addListener(fit);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(fit).catch(()=>{});
  })();

  const SPARKLE = '<svg viewBox="0 0 100 100"><path d="M50 4 C52 38, 62 48, 96 50 C62 52, 52 62, 50 96 C48 62, 38 52, 4 50 C38 48, 48 38, 50 4 Z"/></svg>';
  const CLOSE_X  = '<svg viewBox="0 0 22 21" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">' +
    '<path d="M0.877209 0.877275C2.04698 -0.292499 3.94367 -0.292351 5.11354 0.877275L10.5657 6.32942L16.012 0.883134C17.1818 -0.286425 19.0785 -0.286409 20.2483 0.883134C21.4181 2.05291 21.4179 3.9496 20.2483 5.11946L14.802 10.5658L20.1174 15.8812C21.2873 17.051 21.2873 18.9477 20.1174 20.1175C18.9476 21.2872 17.0509 21.2873 15.8811 20.1175L10.5657 14.8021L5.2444 20.1234C4.07455 21.2932 2.17792 21.2932 1.00807 20.1234C-0.161545 18.9535 -0.161701 17.0568 1.00807 15.887L6.32936 10.5658L0.877209 5.1136C-0.292372 3.94378 -0.292433 2.04706 0.877209 0.877275Z"/>' +
    '</svg>';
  const MAX_OPEN = 3;
  const openStack = [];
  const CLASS_SLUG = {
    'космос база':'base', 'космос классика':'classic', 'космос люкс':'lux'
  };

  function buildBubble(name){
    const f = (window.KOSMOS_FILLINGS || {})[name];
    if (!f) return null;
    const bubble = document.createElement('div');
    bubble.className = 'filling-bubble';
    bubble.insertAdjacentHTML('beforeend',
      `<span class="spark left"  aria-hidden="true">${SPARKLE}</span>` +
      `<span class="spark right" aria-hidden="true">${SPARKLE}</span>`);
    const h3 = document.createElement('h3');
    if (f.display){
      h3.innerHTML = f.display;
      const lines = (f.display.match(/<br\s*\/?>/gi) || []).length + 1;
      if (lines === 2) bubble.classList.add('is-title-2');
      if (lines >= 3) bubble.classList.add('is-title-3');
    } else {
      h3.textContent = name;
    }
    bubble.appendChild(h3);
    const desc = document.createElement('p');
    desc.className = 'desc';
    desc.textContent = f.desc;
    bubble.appendChild(desc);
    const slug = CLASS_SLUG[f.cls];
    if (slug){
      const cls = document.createElement('img');
      cls.className = 'bb-class';
      cls.src = `../assets/class-${slug}.svg?v=${window.KOSMOS_CLASS_V || ''}`;
      cls.alt = f.cls;
      cls.title = f.cls;
      bubble.appendChild(cls);
    }
    const price = document.createElement('p');
    price.className = 'bb-price';
    price.textContent = f.price;
    bubble.appendChild(price);
    const close = document.createElement('button');
    close.type = 'button';
    close.className = 'close';
    close.setAttribute('aria-label', 'закрыть');
    close.innerHTML = CLOSE_X;
    bubble.appendChild(close);
    return bubble;
  }
  function closeWrap(wrap){
    wrap.classList.remove('is-open');
    const b = wrap.querySelector('.filling-bubble');
    if (b) b.remove();
    const i = openStack.indexOf(wrap);
    if (i !== -1) openStack.splice(i, 1);
  }
  function openWrap(wrap, name){
    if (wrap.classList.contains('is-open')) return;
    if (openStack.length >= MAX_OPEN) closeWrap(openStack[0]);
    const bubble = buildBubble(name);
    if (!bubble) return;
    wrap.appendChild(bubble);
    wrap.classList.add('is-open');
    openStack.push(wrap);
    bubble.addEventListener('click', () => closeWrap(wrap));
  }

  function fillingSets(){
    return window.KOSMOS_FILLING_SETS || window.FILLING_SETS || {};
  }
  function resolveFillings(raw){
    if (!raw) return [];
    const sets = fillingSets();
    const list = sets[raw] ? sets[raw] : raw.split(',').map(s => s.trim()).filter(Boolean);
    return typeof window.sortByCanonical === 'function' ? window.sortByCanonical(list) : list;
  }
  function buildSlice(name){
    const f = (window.KOSMOS_FILLINGS || {})[name];
    const wrap = document.createElement('div');
    wrap.className = 'slice-wrap';
    wrap.dataset.filling = name;
    const img = document.createElement('img');
    img.className = 'slice'; img.alt = name; img.loading = 'lazy';
    img.src = f && f.photo
      ? `../fillings/photos/${f.photo}`
      : '../photos/fairy-cake/slice-1.jpg';
    wrap.appendChild(img);
    const dot = document.createElement('button');
    dot.type = 'button'; dot.className = 'info-dot';
    dot.setAttribute('aria-label', name + ' — описание');
    dot.innerHTML = SPARKLE;
    wrap.appendChild(dot);
    return wrap;
  }

  /* Делегирование кликов по точкам начинок: работает и для оригиналов,
     и для клонов (которые добавляются автокаруселью для бесшовного цикла). */
  function bindFillingDelegation(container){
    if (!container || container.__kDeleg) return;
    container.__kDeleg = true;
    container.addEventListener('click', (e) => {
      const dot = e.target.closest('.info-dot');
      if (!dot) return;
      const wrap = dot.closest('.slice-wrap');
      if (!wrap) return;
      const name = wrap.dataset.filling;
      if (!name) return;
      openWrap(wrap, name);
    });
  }

  function mountFillings(el){
    if (!el || !el.dataset.fillings || el.dataset.mounted === '1') return;
    if (!window.KOSMOS_FILLINGS || !Object.keys(fillingSets()).length) return false;
    el.dataset.mounted = '1';
    resolveFillings(el.dataset.fillings).forEach(name => el.appendChild(buildSlice(name)));
    bindFillingDelegation(el);
    layoutReady(kosmoLoopScroll);
    return true;
  }
  (function bootFillings(){
    var el = document.getElementById('fillings-col');
    if (!el || !el.dataset.fillings) return;
    if (mountFillings(el)) return;
    var n = 0;
    (function retry(){
      if (mountFillings(el) || ++n > 120) return;
      setTimeout(retry, 50);
    })();
  })();

  const page = document.querySelector('.cake-page');
  const deliveryCol = document.getElementById('delivery-col');
  function openDeliveryPanel(){
    if (!page || !deliveryCol) return;
    page.classList.add('is-delivery');
    deliveryCol.setAttribute('aria-hidden','false');
    if (window.matchMedia('(max-width:900px)').matches){
      deliveryCol.scrollIntoView({behavior:'smooth', block:'start'});
    }
  }
  if (page && deliveryCol){
    window.addEventListener('kosmos-next', openDeliveryPanel);
    const dBack = document.getElementById('delivery-back');
    if (dBack){
      dBack.addEventListener('click', () => {
        page.classList.remove('is-delivery');
        deliveryCol.setAttribute('aria-hidden','true');
      });
    }
  }

  /* Боковые колонки — тот же Kosmo.Drum, что и на главной. */
  function kosmoLoop(el, vert, speed){
    if (!el || !window.Kosmo || !Kosmo.Drum) return null;
    return Kosmo.Drum.bind({
      scrollEl: el,
      stripEl: el,
      axis: vert ? 'y' : 'x',
      speed: speed,
      pauseOnClick: '.info-dot, .filling-bubble, button, a, .close'
    });
  }

  var _loopMq = window.matchMedia('(max-width:900px)');
  var _loopHandles = [];
  function killLoops(){
    _loopHandles.forEach(h => { if (h.kill) h.kill(); });
    _loopHandles = [];
    ['cake-photos','fillings-col'].forEach(id => {
      const el = document.getElementById(id);
      if (el){
        delete el.__kDrum;
        delete el.__kLoop;
        el.classList.remove('k-loop-auto', 'k-loop-native', 'k-loop-dragging');
      }
    });
    const cp = document.querySelector('.col-photo');
    if (cp) delete cp.__kLoop;
  }
  var _loopMode = '';
  function kosmoLoopScroll(){
    var ph = document.getElementById('cake-photos');
    var fc = document.getElementById('fillings-col');
    var mode = _loopMq.matches ? 'mob' : 'desk';
    var fcNeeded = !!(fc && (fc.dataset.fillings || fc.classList.contains('col-fillings--photos')));
    var vert = !_loopMq.matches;
    if (_loopMode === mode && ph && ph.__kLoop && (!fcNeeded || (fc && fc.__kLoop))) return;
    _loopMode = mode;
    killLoops();
    if (_loopMq.matches){
      if (ph){ var h = kosmoLoop(ph, false, 2.6); if (h) _loopHandles.push(h); }
      if (fc && fc.dataset.fillings){ var h2 = kosmoLoop(fc, false, 2.2); if (h2) _loopHandles.push(h2); }
    } else {
      if (ph){ var h3 = kosmoLoop(ph, true, 1.6); if (h3) _loopHandles.push(h3); }
      if (fc && (fc.classList.contains('col-fillings--photos') || fc.dataset.fillings)){
        var h4 = kosmoLoop(fc, true, 1.4); if (h4) _loopHandles.push(h4);
      }
    }
  }
  function watchCarouselImages(cb){
    ['cake-photos','fillings-col'].forEach(function(id){
      var root = document.getElementById(id);
      if (!root) return;
      root.querySelectorAll('img').forEach(function(img){
        if (img.complete) return;
        function retry(){
          if (!root.__kLoop) cb();
        }
        img.addEventListener('load', retry, {once:true});
        img.addEventListener('error', retry, {once:true});
      });
    });
  }
  function carouselReady(el, vert){
    if (!el) return false;
    if (vert) return el.clientHeight > 40 && el.scrollHeight > el.clientHeight + 8;
    return el.clientWidth > 40 && el.scrollWidth > el.clientWidth + 8;
  }
  function layoutReady(cb){
    var tries = 0;
    var vert = !_loopMq.matches;
    function go(){
      var ph = document.getElementById('cake-photos');
      if (carouselReady(ph, vert)){
        cb();
        return;
      }
      if (++tries < 80) requestAnimationFrame(go);
      else cb();
    }
    go();
  }

  function startLoopsWhenReady(){
    function boot(){ layoutReady(kosmoLoopScroll); }
    watchCarouselImages(boot);
    if (document.fonts && document.fonts.ready){
      document.fonts.ready.then(boot).catch(boot);
    } else {
      boot();
    }
    window.addEventListener('load', boot, {once:true});
    window.requestAnimationFrame(function(){
      window.requestAnimationFrame(boot);
    });
    if (new URLSearchParams(location.search).get('embed') === 'kosmos'){
      [120, 400, 1000, 2500].forEach(function(ms){
        setTimeout(boot, ms);
      });
    }
    var page = document.querySelector('.cake-page');
    if (page && window.ResizeObserver){
      var roTimer;
      new ResizeObserver(function(){
        clearTimeout(roTimer);
        roTimer = setTimeout(boot, 80);
      }).observe(page);
    }
  }
  startLoopsWhenReady();
  if (_loopMq.addEventListener) _loopMq.addEventListener('change', function(){ layoutReady(kosmoLoopScroll); });
  else if (_loopMq.addListener) _loopMq.addListener(function(){ layoutReady(kosmoLoopScroll); });

  function kosmoDots(carouselId, dotsId){
    if (window.Kosmos && window.Kosmos.Dots && window.Kosmos.Dots.bindCarousel){
      return window.Kosmos.Dots.bindCarousel(carouselId, dotsId);
    }
    const car = document.getElementById(carouselId);
    const dotsBox = document.getElementById(dotsId);
    if (!car || !dotsBox) return;
    const meta = car.__kLoop;
    const originals = meta ? meta.kids : Array.prototype.slice.call(car.children);
    if (!originals.length || originals.length < 2) return;
    dotsBox.innerHTML = '';
    const dots = [];
    for (let i = 0; i < originals.length; i++){
      const dot = document.createElement('button');
      dot.type = 'button';
      dot.className = 'dot';
      dot.setAttribute('aria-label', 'к слайду ' + (i + 1));
      if (i === 0) dot.classList.add('active');
      dot.style.pointerEvents = 'auto';
      dot.addEventListener('click', () => {
        const target = originals[i];
        if (target && target.scrollIntoView){
          target.scrollIntoView({behavior:'smooth', block:'nearest', inline:'center'});
        }
      });
      dotsBox.appendChild(dot);
      dots.push(dot);
    }
    let prev = 0;
    function update(){
      const w = car.clientWidth || 1;
      const idxRaw = Math.round(car.scrollLeft / w);
      const i = ((idxRaw % originals.length) + originals.length) % originals.length;
      if (i === prev) return;
      dots[prev].classList.remove('active');
      dots[i].classList.add('active');
      prev = i;
    }
    car.addEventListener('scroll', () => {
      window.requestAnimationFrame(update);
    }, {passive:true});
  }
  setTimeout(() => {
    if (window.matchMedia('(max-width:900px)').matches){
      kosmoDots('cake-photos', 'cake-photo-dots');
      kosmoDots('fillings-col', 'cake-fillings-dots');
    }
  }, 30);

  (function syncCalcMobileCtx(){
    const mq = window.matchMedia('(max-width: 900px)');
    function apply(){
      if (typeof window.setKosmosMobileCtx === 'function'){
        window.setKosmosMobileCtx(mq.matches);
      }
    }
    apply();
    if (mq.addEventListener) mq.addEventListener('change', apply);
    else if (mq.addListener) mq.addListener(apply);
  })();
