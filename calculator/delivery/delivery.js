/* ============================================================
   delivery.js — универсальный модуль «Доставка».

   Использование:
     <link rel="stylesheet" href="delivery.css">
     <div id="dlv"></div>
     <script src="delivery.js"></script>
     <script>Kosmos.mountDelivery(document.getElementById('dlv'));</script>

   Получает данные о торте через ЛЮБОЙ из 3-х каналов одновременно:
     1) URL params         (?total=..&cake=..&weight=..&tiers=..&filling=..&tiered=0|1)
     2) BroadcastChannel   'kosmos-cake' — для блоков на одной странице
     3) window 'message'   — postMessage из родителя
     4) window 'kosmos-cake' CustomEvent — если калькулятор и доставка на одной странице

   core.js на каждом изменении торта дёргает broadcastCake() — оно
   пуляет одно и то же payload во все 3 канала (см. core.js).
   ============================================================ */

(function(global){
  var TELEGRAM_URL = 'https://t.me/kosmoscake';

  var SPARKLE_SVG = '<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">' +
    '<path d="M50 4 C52 38, 62 48, 96 50 C62 52, 52 62, 50 96 C48 62, 38 52, 4 50 C38 48, 48 38, 50 4 Z"/>' +
    '</svg>';

  var MAP_SRC = 'https://yandex.ru/map-widget/v1/?um=constructor%3Aee06b09908881d0ce064970f14ef714b8a4b7933a37782ec96d3e0c4c7e4b9ab&source=constructor';

  var ZONES = [
    {key:'orange', cls:'dlv-z-orange', rate:1000, name:'оранжевая зона'},
    {key:'green',  cls:'dlv-z-green',  rate:600, name:'зелёная зона'},
    {key:'purple', cls:'dlv-z-purple', rate:0,    name:'самовывоз', pickup:true},
    {key:'brown',  cls:'dlv-z-brown',  rate:3500, name:'коричневая зона'},
    {key:'blue',   cls:'dlv-z-blue',   rate:2000, name:'голубая зона'},
    {key:'red',    cls:'dlv-z-red',    rate:1500, name:'красная зона'}
  ];

  function fmtRub(n){
    n = Math.round(+n || 0);
    return n.toLocaleString('ru-RU').replace(/\u00a0|\s/g,'\u00a0') + 'р';
  }

  function getUrlParams(){
    var p;
    try { p = new URLSearchParams(location.search); } catch(_){ return {}; }
    return {
      total  : parseInt(p.get('total'),  10) || 0,
      cake   : (p.get('cake')   || '').trim(),
      weight : (p.get('weight') || '').trim(),
      tiers  : (p.get('tiers')  || '').trim(),
      pieces : (p.get('pieces') || '').trim(),
      filling: (p.get('filling')|| '').trim(),
      tiered : p.get('tiered') === '1' || p.get('tiered') === 'true'
    };
  }

  function buildTemplate(){
    var zonesHTML = ZONES.map(function(z){
      var pickup = z.pickup ? ' data-pickup="1"' : '';
      return '<button class="dlv-zone ' + z.cls +'" data-key="'+z.key+
             '" data-rate="'+z.rate+'" data-name="'+z.name+'"'+pickup+
             ' type="button">'+(z.label||'')+'</button>';
    }).join('');
    return ''+
'<div class="dlv-frame">'+
'  <div class="dlv-map"><iframe src="'+MAP_SRC+'" title="Зоны доставки"   allowfullscreen></iframe></div>'+
'  <p class="dlv-title">Мы бережно доставляем торты по всей Москве и до 20 км от МКАД.</p>'+
'  <div class="dlv-zone-label">выберите зону</div>'+
'  <div class="dlv-zones" data-role="zones">'+zonesHTML+'</div>'+
'  <div class="dlv-cost"><div class="lbl" data-role="delivery-lbl">стоимость доставки</div><div class="val" data-role="delivery-val">—</div></div>'+
'  <div class="dlv-total"><div class="lbl">итоговая стоимость</div>'+
'    <div class="val-row"><span class="sparkle">'+SPARKLE_SVG+'</span><div class="val" data-role="final-val">—</div><span class="sparkle">'+SPARKLE_SVG+'</span></div>'+
'  </div>'+
'  <button class="dlv-cta" data-role="cta" type="button" disabled>продолжить заказ<br>с администратором</button>'+
'</div>'+
'<div class="dlv-toast" data-role="toast"></div>';
  }

  function mountDelivery(host, options){
    if (!host) return null;
    options = options || {};

    host.innerHTML = buildTemplate();

    var $zones      = host.querySelector('[data-role="zones"]');
    var $deliveryL  = host.querySelector('[data-role="delivery-lbl"]');
    var $deliveryV  = host.querySelector('[data-role="delivery-val"]');
    var $finalV     = host.querySelector('[data-role="final-val"]');
    var $cta        = host.querySelector('[data-role="cta"]');
    var $toast      = host.querySelector('[data-role="toast"]');

    var state = {
      params: Object.assign({total:0,cake:'',weight:'',tiers:'',pieces:'',filling:'',tiered:false}, getUrlParams(), options.initialPayload||{}),
      rate  : null,
      name  : null,
      pickup: false
    };

    function applyTieredLock(){
      var purple = $zones.querySelector('[data-key="purple"]');
      if (!purple) return;
      if (state.params.tiered){
        // для ярусных тортов самовывоз не предлагаем — прячем кружок целиком
        purple.style.display = 'none';
        if (purple.classList.contains('is-active')){
          purple.classList.remove('is-active');
          state.rate = null; state.name = null; state.pickup = false;
        }
      } else {
        purple.style.display = '';
        purple.removeAttribute('disabled');
        purple.removeAttribute('title');
      }
    }
    applyTieredLock();

    function render(){
      if (state.rate === null){
        $deliveryL.textContent = 'стоимость доставки';
        $deliveryV.textContent = '—';
        $finalV.textContent    = fmtRub(state.params.total);
        $cta.setAttribute('disabled','disabled');
        return;
      }
      if (state.pickup){
        // при выборе самовывоза переписываем и лейбл, и значение
        $deliveryL.textContent = 'самовывоз';
        $deliveryV.textContent = 'бесплатно';
      } else {
        $deliveryL.textContent = 'стоимость доставки';
        $deliveryV.textContent = fmtRub(state.rate);
      }
      $finalV.textContent    = fmtRub(state.params.total + state.rate);
      $cta.removeAttribute('disabled');
    }

    $zones.addEventListener('click', function(e){
      var btn = e.target.closest('.dlv-zone');
      if (!btn || btn.hasAttribute('disabled')) return;
      $zones.querySelectorAll('.dlv-zone').forEach(function(b){ b.classList.remove('is-active'); });
      btn.classList.add('is-active');
      state.rate   = parseInt(btn.dataset.rate, 10) || 0;
      state.name   = btn.dataset.name || '';
      state.pickup = btn.dataset.pickup === '1';
      render();
    });

    function toast(msg){
      $toast.textContent = msg;
      $toast.classList.add('show');
      clearTimeout(toast._t);
      toast._t = setTimeout(function(){ $toast.classList.remove('show'); }, 3200);
    }

    function buildOrderText(){
      var p = state.params;
      var lines = [];
      lines.push('Здравствуйте! Хочу оформить заказ на торт.');
      if (p.cake)    lines.push('Торт: ' + p.cake);
      if (p.weight)  lines.push('Кг: ' + p.weight);
      if (p.tiers)   lines.push('Ярусов: ' + p.tiers);
      if (p.pieces)  lines.push('Порций: ' + p.pieces);
      if (p.filling) lines.push('Начинка: ' + p.filling);
      if (state.pickup){
        lines.push('Доставка: самовывоз (бесплатно)');
      } else {
        lines.push('Доставка: ' + state.name + ' — ' + fmtRub(state.rate));
      }
      lines.push('Итого: ' + fmtRub(p.total + (state.rate || 0)));
      return lines.join('\n');
    }

    $cta.addEventListener('click', function(){
      if ($cta.hasAttribute('disabled')) return;
      var text = buildOrderText();
      function done(ok){
        toast(ok ? 'Сообщение скопировано — вставьте его в чате'
                 : 'Перешлите детали администратору');
        setTimeout(function(){ window.open(TELEGRAM_URL, '_blank', 'noopener'); }, 400);
      }
      if (navigator.clipboard && navigator.clipboard.writeText){
        navigator.clipboard.writeText(text).then(function(){ done(true); }).catch(function(){ done(false); });
        return;
      }
      var ta = document.createElement('textarea');
      ta.value = text; ta.style.position='fixed'; ta.style.left='-9999px';
      document.body.appendChild(ta); ta.select();
      var ok = false;
      try { ok = document.execCommand('copy'); } catch(_){}
      document.body.removeChild(ta);
      done(ok);
    });

    /* ====== ВНЕШНИЕ ОБНОВЛЕНИЯ ОТ КАЛЬКУЛЯТОРА ====== */
    function setPayload(payload){
      if (!payload || typeof payload !== 'object') return;
      state.params.total   = parseInt(payload.total, 10) || 0;
      state.params.cake    = (payload.cake    || '').toString().trim();
      state.params.weight  = (payload.weight  || '').toString().trim();
      state.params.tiers   = (payload.tiers   || '').toString().trim();
      state.params.pieces  = (payload.pieces  || '').toString().trim();
      state.params.filling = (payload.filling || '').toString().trim();
      state.params.tiered  = !!payload.tiered;
      applyTieredLock();
      render();
    }

    // 1) CustomEvent — когда калькулятор живёт в той же window (full mobile)
    window.addEventListener('kosmos-cake', function(e){ setPayload(e.detail); });

    // 2) BroadcastChannel — между блоками на одной странице
    try {
      var ch = new BroadcastChannel('kosmos-cake');
      ch.addEventListener('message', function(e){ setPayload(e.data); });
    } catch(_){}

    // 3) postMessage — извне (родительская страница)
    window.addEventListener('message', function(e){
      if (!e.data || typeof e.data !== 'object') return;
      if (e.data.type !== 'kosmos-cake') return;
      setPayload(e.data);
    });

    render();

    return { setPayload: setPayload };
  }

  global.Kosmos = global.Kosmos || {};
  global.Kosmos.mountDelivery = mountDelivery;
})(window);
