/* Общий «барабан»: бесшовный автоскролл + пауза при жесте пользователя. */
(function (global) {
  var Kosmo = global.Kosmo = global.Kosmo || {};

  function bind(opts) {
    var scrollEl = opts && opts.scrollEl;
    var stripEl = (opts && opts.stripEl) || scrollEl;
    if (!scrollEl || !stripEl) return null;
    if (scrollEl.__kDrum) return scrollEl.__kDrum;

    var vert = opts.axis !== 'x';
    var speed = opts.speed != null ? opts.speed : 2;
    var cloneClass = opts.cloneClass || 'k-loop-clone';
    var autoClass = opts.autoClass || 'k-loop-auto';
    var userPauseMs = opts.userPauseMs != null ? opts.userPauseMs : 1000;
    var userScrollMin = opts.userScrollMin != null ? opts.userScrollMin : 2;
    var touchThreshold = opts.touchThreshold != null ? opts.touchThreshold : 8;
    var pauseOnClick = opts.pauseOnClick;

    Array.prototype.slice.call(stripEl.children).forEach(function (c) {
      if (c.classList.contains(cloneClass)) c.remove();
    });

    var kids = Array.prototype.slice.call(stripEl.children);
    if (!kids.length) return null;

    scrollEl.classList.add(autoClass);
    kids.forEach(function (node) {
      var clone = node.cloneNode(true);
      clone.classList.add(cloneClass);
      clone.setAttribute('aria-hidden', 'true');
      stripEl.appendChild(clone);
    });

    var killed = false;
    var paused = false;
    var scrollPos = 0;
    var byCode = false;
    var pauseTimer = null;
    var rafId = null;
    var lastTs = 0;
    var lastUserPos = 0;

    function fullSize() {
      return vert ? scrollEl.scrollHeight : scrollEl.scrollWidth;
    }

    function origSize() {
      if (!stripEl.querySelector('.' + cloneClass)) {
        return fullSize();
      }
      return Math.round(fullSize() / 2);
    }

    function wrapFloat(c) {
      var sz = origSize();
      if (sz < 8) return c;
      c = c % sz;
      if (c < 0) c += sz;
      return c;
    }

    function getScroll() {
      return vert ? scrollEl.scrollTop : scrollEl.scrollLeft;
    }

    function writeScroll(c) {
      if (origSize() < 8) return;
      byCode = true;
      scrollPos = wrapFloat(c);
      if (vert) scrollEl.scrollTop = scrollPos;
      else scrollEl.scrollLeft = scrollPos;
      lastUserPos = scrollPos;
      byCode = false;
    }

    function schedulePause() {
      paused = true;
      clearTimeout(pauseTimer);
      pauseTimer = setTimeout(function () { paused = false; }, userPauseMs);
    }

    function tick(ts) {
      if (killed) return;
      rafId = global.requestAnimationFrame(tick);
      if (!lastTs) { lastTs = ts; return; }
      var dt = Math.min(ts - lastTs, 48) / 16;
      lastTs = ts;
      if (origSize() < 8) return;
      if (!paused) {
        writeScroll(scrollPos + speed * dt);
      } else {
        scrollPos = getScroll();
      }
    }

    function onScroll() {
      if (byCode) return;
      var c = getScroll();
      if (Math.abs(c - scrollPos) < userScrollMin) return;
      if (Math.abs(c - lastUserPos) < userScrollMin) return;
      lastUserPos = c;
      scrollPos = wrapFloat(c);
      if (Math.abs(scrollPos - c) > 0.5) writeScroll(scrollPos);
      schedulePause();
    }

    scrollEl.addEventListener('scroll', onScroll, {passive: true});

    var touchStart = 0;
    var touchMoved = false;
    scrollEl.addEventListener('touchstart', function (e) {
      if (!e.changedTouches || !e.changedTouches[0]) return;
      touchMoved = false;
      touchStart = vert ? e.changedTouches[0].clientY : e.changedTouches[0].clientX;
    }, {passive: true});
    scrollEl.addEventListener('touchmove', function (e) {
      if (!e.changedTouches || !e.changedTouches[0]) return;
      var pos = vert ? e.changedTouches[0].clientY : e.changedTouches[0].clientX;
      if (!touchMoved && Math.abs(pos - touchStart) > touchThreshold) {
        touchMoved = true;
        schedulePause();
      }
    }, {passive: true});
    scrollEl.addEventListener('touchend', function () {
      if (touchMoved) schedulePause();
      touchMoved = false;
    }, {passive: true});

    if (pauseOnClick) {
      scrollEl.addEventListener('click', function (e) {
        if (e.target.closest && e.target.closest(pauseOnClick)) schedulePause();
      }, {passive: true});
    }

    var pauseOnHidden = opts.pauseOnHidden !== false;

    function onVisibility() {
      if (!pauseOnHidden) return;
      if (document.hidden) paused = true;
      else paused = false;
    }
    document.addEventListener('visibilitychange', onVisibility);

    function boot() {
      scrollPos = getScroll();
      lastUserPos = scrollPos;
      var dim = vert ? scrollEl.clientHeight : scrollEl.clientWidth;
      if (dim < 40 || origSize() < 8) return;
      if (!rafId && !killed) {
        lastTs = 0;
        rafId = global.requestAnimationFrame(tick);
      }
    }

    function kill() {
      killed = true;
      clearTimeout(pauseTimer);
      document.removeEventListener('visibilitychange', onVisibility);
      if (rafId) global.cancelAnimationFrame(rafId);
      rafId = null;
      Array.prototype.slice.call(stripEl.children).forEach(function (c) {
        if (c.classList.contains(cloneClass)) c.remove();
      });
      scrollEl.classList.remove(autoClass, 'k-loop-dragging');
      delete scrollEl.__kDrum;
      delete scrollEl.__kLoop;
    }

    scrollPos = getScroll();
    lastUserPos = scrollPos;
    rafId = global.requestAnimationFrame(tick);

    if (opts.watchResize !== false) {
      if (global.ResizeObserver) {
        var ro = new global.ResizeObserver(boot);
        ro.observe(scrollEl);
        if (stripEl !== scrollEl) ro.observe(stripEl);
      }
      global.addEventListener('resize', boot, {passive: true});
    }

    stripEl.querySelectorAll('img').forEach(function (img) {
      if (img.complete) return;
      img.addEventListener('load', boot, {once: true});
      img.addEventListener('error', boot, {once: true});
    });
    if (global.document && global.document.fonts && global.document.fonts.ready) {
      global.document.fonts.ready.then(boot).catch(boot);
    }
    global.addEventListener('load', boot, {once: true});
    global.requestAnimationFrame(function () { global.requestAnimationFrame(boot); });

    var api = { kids: kids, origSize: origSize, kill: kill, boot: boot };
    scrollEl.__kDrum = api;
    scrollEl.__kLoop = api;
    return api;
  }

  Kosmo.Drum = { bind: bind };
})(typeof window !== 'undefined' ? window : this);
