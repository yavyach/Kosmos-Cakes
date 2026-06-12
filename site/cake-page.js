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

  function resolveFillings(raw){
    if (!raw) return [];
    const sets = window.KOSMOS_FILLING_SETS || {};
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
    if (!el || !el.dataset.fillings) return;
    resolveFillings(el.dataset.fillings).forEach(name => el.appendChild(buildSlice(name)));
    bindFillingDelegation(el);
  }
  mountFillings(document.getElementById('fillings-col'));

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

  /* Бесконечная авто-карусель: клонируем оригинальный набор детей один раз
     и крутим только в одну сторону. При прохождении длины оригинала вычитаем
     её — позиция «обнуляется» без рывка, потому что клон выглядит идентично.
     Используется и для горизонтальных карусели (mob-photos, mob-fillings),
     и для вертикальной «колбасы» начинок и фото на десктопе.
     Взаимодействие (клик, колесо, драг) ставит авто-прокрутку на паузу на 5 с,
     затем плавно возвращает обычную скорость. Драг ЛКМ даёт инерцию с затуханием. */
  function kosmoLoop(el, vert, speed){
    if (!el) return null;
    if (el.__kLoop) return el.__kLoop;
    var kids = Array.prototype.slice.call(el.children);
    if (!kids.length) return null;
    function origSize(){
      var t = 0;
      for (var i = 0; i < kids.length; i++) t += vert ? kids[i].offsetHeight : kids[i].offsetWidth;
      return t;
    }
    function viewSize(){ return vert ? el.clientHeight : el.clientWidth; }
    var safety = 0;
    while (origSize() < viewSize() * 2 + 4 && safety++ < 8){
      kids.forEach(function(c){ el.appendChild(c.cloneNode(true)); });
    }

    var baseSp = speed || (vert ? 0.55 : 0.9);
    var RESUME_MS = 5000;
    var RAMP_FRAMES = 48;
    var killed = false;
    var paused = false;
    var ramp = 1;
    var momentum = 0;
    var resumeTimer = null;
    var rafId = null;
    var lastTs = 0;

    function getScroll(){ return vert ? el.scrollTop : el.scrollLeft; }
    function setScroll(c){
      var sz = origSize();
      if (sz < 8) return;
      while (c >= sz) c -= sz;
      while (c < 0) c += sz;
      if (vert) el.scrollTop = c; else el.scrollLeft = c;
    }
    function pauseNow(){
      clearTimeout(resumeTimer);
      paused = true;
      ramp = 0;
    }
    function scheduleResume(){
      clearTimeout(resumeTimer);
      resumeTimer = setTimeout(function(){
        paused = false;
      }, RESUME_MS);
    }
    function isInteractive(target){
      return target && target.closest && target.closest('.info-dot, .filling-bubble, button, a, .close');
    }

    function tick(ts){
      if (killed) return;
      rafId = requestAnimationFrame(tick);
      if (!lastTs){ lastTs = ts; return; }
      var dt = Math.min(ts - lastTs, 48) / 30;
      lastTs = ts;
      if (origSize() < 8) return;

      if (Math.abs(momentum) > baseSp * 0.12){
        setScroll(getScroll() + momentum * dt);
        momentum *= Math.pow(0.94, dt);
        if (Math.abs(momentum) <= baseSp * 0.12) momentum = 0;
      } else if (!paused && !dragActive){
        if (ramp < 1) ramp = Math.min(1, ramp + dt / RAMP_FRAMES);
        var ease = ramp * ramp * (3 - 2 * ramp);
        setScroll(getScroll() + baseSp * ease * dt);
      }
    }
    rafId = requestAnimationFrame(tick);

    var dragActive = false;
    var dragPointerId = null;
    var dragStartPos = 0;
    var dragStartScroll = 0;
    var lastDragPos = 0;
    var lastDragTs = 0;
    var dragVel = 0;

    el.addEventListener('wheel', function(){
      momentum = 0;
      pauseNow();
      scheduleResume();
    }, {passive:true});
    el.addEventListener('touchstart', function(){
      momentum = 0;
      pauseNow();
      scheduleResume();
    }, {passive:true});

    el.addEventListener('pointerdown', function(e){
      if (e.button !== 0) return;
      if (isInteractive(e.target)){
        pauseNow();
        scheduleResume();
        return;
      }
      pauseNow();
      dragPointerId = e.pointerId;
      dragActive = false;
      dragStartPos = vert ? e.clientY : e.clientX;
      dragStartScroll = getScroll();
      lastDragPos = dragStartPos;
      lastDragTs = e.timeStamp;
      dragVel = 0;
      momentum = 0;
    });

    el.addEventListener('pointermove', function(e){
      if (e.pointerId !== dragPointerId) return;
      var pos = vert ? e.clientY : e.clientX;
      var delta = pos - dragStartPos;
      if (!dragActive && Math.abs(delta) > 5){
        dragActive = true;
        el.classList.add('k-loop-dragging');
        try { el.setPointerCapture(e.pointerId); } catch (_) {}
      }
      if (!dragActive) return;
      e.preventDefault();
      setScroll(dragStartScroll - delta);
      var now = e.timeStamp;
      var dt = now - lastDragTs;
      if (dt > 0) dragVel = (pos - lastDragPos) / dt;
      lastDragPos = pos;
      lastDragTs = now;
    }, {passive:false});

    function endDrag(e){
      if (e.pointerId !== dragPointerId) return;
      dragPointerId = null;
      if (dragActive){
        el.classList.remove('k-loop-dragging');
        try { el.releasePointerCapture(e.pointerId); } catch (_) {}
        momentum = -dragVel * 30 * 2.8;
        var cap = baseSp * 28;
        if (momentum > cap) momentum = cap;
        if (momentum < -cap) momentum = -cap;
        ramp = 0;
      }
      dragActive = false;
      scheduleResume();
    }
    el.addEventListener('pointerup', endDrag);
    el.addEventListener('pointercancel', endDrag);

    function kill(){
      killed = true;
      clearTimeout(resumeTimer);
      if (rafId) cancelAnimationFrame(rafId);
    }
    el.__kLoop = { kids: kids, origSize: origSize, kill: kill };
    return el.__kLoop;
  }

  var _loopMq = window.matchMedia('(max-width:900px)');
  var _loopHandles = [];
  function killLoops(){
    _loopHandles.forEach(h => { if (h.kill) h.kill(); });
    _loopHandles = [];
    ['cake-photos','fillings-col'].forEach(id => {
      const el = document.getElementById(id);
      if (el) delete el.__kLoop;
    });
    const cp = document.querySelector('.col-photo');
    if (cp) delete cp.__kLoop;
  }
  function kosmoLoopScroll(){
    killLoops();
    var ph = document.getElementById('cake-photos');
    var cp = document.querySelector('.col-photo');
    var fc = document.getElementById('fillings-col');
    if (_loopMq.matches){
      if (ph){ var h = kosmoLoop(ph, false, 1.0); if (h) _loopHandles.push(h); }
      if (fc && fc.dataset.fillings){ var h2 = kosmoLoop(fc, false, 0.9); if (h2) _loopHandles.push(h2); }
    } else {
      if (cp){ var h3 = kosmoLoop(cp, true, 0.55); if (h3) _loopHandles.push(h3); }
      if (fc && (fc.classList.contains('col-fillings--photos') || fc.dataset.fillings)){
        var h4 = kosmoLoop(fc, true, 0.55); if (h4) _loopHandles.push(h4);
      }
    }
  }
  kosmoLoopScroll();
  if (_loopMq.addEventListener) _loopMq.addEventListener('change', kosmoLoopScroll);
  else if (_loopMq.addListener) _loopMq.addListener(kosmoLoopScroll);

  function kosmoDots(carouselId, dotsId){
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
