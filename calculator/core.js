/* ================================================================
   ОБЩИЕ ДАННЫЕ И УТИЛИТЫ
   ================================================================ */

window.FILLING_PRICES = {
  "яблочный синнабон":3000,"шоколадный с шоколадом":2800,"ванильный с клубникой":2800,
  "ванильный с вишней":2800,"кукис энд крим":3000,"мак-лимон":3000,
  "фундук-кофе шоколад":3600,"фисташка-малина":3600,"шоколад-кокос":3000,
  "морковный":2800,"сникерс":3000,"дорблю груша-грецкий орех":3600,
  "апельсин-манго-маракуйя":3000,"черника-шоколад":3600,
  "фисташковый чизкейк":3000,"чизкейк орео":3000,"чизкейк Нью Йорк":3000,"тирамису":3000
};

const _BASE = ["яблочный синнабон","шоколадный с шоколадом","ванильный с клубникой","ванильный с вишней","кукис энд крим","мак-лимон","фундук-кофе шоколад","фисташка-малина","шоколад-кокос","морковный","сникерс","дорблю груша-грецкий орех","апельсин-манго-маракуйя"];

window.FILLING_SETS = {
  BASE: _BASE,
  PLUS_CHERNIKA: [..._BASE, "черника-шоколад"],
  PLUS_CHEESECAKE: [..._BASE, "черника-шоколад", "чизкейк Нью Йорк", "чизкейк орео", "фисташковый чизкейк"],
  NO_SNICKERS_NO_DORBLU: ["яблочный синнабон","шоколадный с шоколадом","ванильный с клубникой","ванильный с вишней","кукис энд крим","мак-лимон","фундук-кофе шоколад","фисташка-малина","шоколад-кокос","морковный","апельсин-манго-маракуйя"],
  TYPE3_LOVE: ["яблочный синнабон","шоколадный с шоколадом","ванильный с клубникой","ванильный с вишней","кукис энд крим","мак-лимон","фундук-кофе шоколад","фисташка-малина","шоколад-кокос","морковный","дорблю груша-грецкий орех","апельсин-манго-маракуйя"],
  TIRAMISU: ["тирамису"]
};

window.fmtMoney  = n => Math.round(n).toLocaleString('ru-RU').replace(/,/g,' ') + 'р';
window.fmtWeight = w => Number.isInteger(w) ? w.toFixed(1) : w.toString();
window.range     = (min, max, price) => ({min, max, price});
window.decorForWeight = (table, w) => {
  for (const r of table) if (w >= r.min && w <= r.max) return r.price;
  return table[table.length-1].price;
};

window.sendOrder = (payload) => {
  console.log('[ORDER]', payload);
  alert('Заказ собран (см. консоль). На втором заходе подключим Google Sheets / Telegram-бот.\n\n' + JSON.stringify(payload, null, 2));
};

/* ================================================================
   broadcastCake — на каждом изменении калькулятора шлёт текущие
   данные торта во все возможные каналы. Их слушает блок «Доставка».

   Каналы:
     1) CustomEvent 'kosmos-cake' на window — если калькулятор и доставка
        живут на ОДНОЙ странице (мобильная объединённая версия).
     2) BroadcastChannel('kosmos-cake') — между блоками на одной странице.
     3) window.parent.postMessage — на случай, если родительская страница
        сама ловит и роняет в доставку.

   Payload:
     { type:'kosmos-cake', total, cake, weight, tiers, pieces, filling, tiered }
   ================================================================ */
/* ================================================================
   БАЗА ПУТЕЙ К assets/ (bow, class-icons) — от каталога core.js
   ================================================================ */
function kosmosCalcBase(){
  if (window.KOSMOS_CALC_BASE){
    return String(window.KOSMOS_CALC_BASE).replace(/\/$/, '');
  }
  var s = document.querySelector('script[src*="core.js"]');
  if (s && s.src){
    return s.src.replace(/\/core\.js(?:\?.*)?$/i, '');
  }
  return '';
}
function kosmosAssetUrl(file){
  var base = kosmosCalcBase();
  return (base ? base + '/assets/' : 'assets/') + file;
}

/* ================================================================
   ДИНАМИЧЕСКИЙ МАСШТАБ КАЛЬКУЛЯТОРА (узкая колонка / мобилка)
   ================================================================ */
var KOSMOS_BASE_W = 380;
window.__kosmosApplyScale = function(){
  try {
    var root = document.getElementById('root') || document.querySelector('.calc-scroll');
    if (!root) return;
    var w = (document.documentElement && document.documentElement.clientWidth) || window.innerWidth || 0;
    if (!w) return;
    if (w >= KOSMOS_BASE_W){
      root.style.transform = '';
      root.style.transformOrigin = '';
      root.style.width = '';
      root.style.marginLeft = '';
      if (document.body){ document.body.style.height = ''; document.body.style.minHeight = ''; }
    } else {
      var k = w / KOSMOS_BASE_W;
      root.style.transformOrigin = 'top center';
      root.style.transform = 'scale(' + k.toFixed(4) + ')';
      root.style.width = KOSMOS_BASE_W + 'px';
      /* offsetLeft при transform: scale не меняется, поэтому центруем
         руками — двигаем root через margin-left. */
      var left = Math.max(0, (w - KOSMOS_BASE_W) / 2);
      root.style.marginLeft = left + 'px';
    }
  } catch(_){}
};
window.addEventListener('resize', function(){
  if (typeof window.__kosmosApplyScale === 'function') window.__kosmosApplyScale();
});
document.addEventListener('DOMContentLoaded', function(){
  if (typeof window.__kosmosApplyScale === 'function') window.__kosmosApplyScale();
});

window.__kosmosBC = null;
window.broadcastCake = function(payload){
  payload = Object.assign({ type:'kosmos-cake' }, payload || {});
  try { window.dispatchEvent(new CustomEvent('kosmos-cake', { detail: payload })); } catch(_){}
  try {
    if (!window.__kosmosBC) window.__kosmosBC = new BroadcastChannel('kosmos-cake');
    window.__kosmosBC.postMessage(payload);
  } catch(_){}
  try { if (window.parent && window.parent !== window) window.parent.postMessage(payload, '*'); } catch(_){}
};

/* ================================================================
   SVG-ИКОНКИ (инлайн)
   ================================================================ */
const SVG_MINUS   = '<svg viewBox="0 0 100 30" xmlns="http://www.w3.org/2000/svg"><rect width="100" height="30" rx="15"/></svg>';
const SVG_PLUS    = '<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><rect x="33" width="34" height="100" rx="14"/><rect y="33" width="100" height="34" rx="14"/></svg>';
const SVG_SPARKLE = '<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><path d="M50 4 C52 38, 62 48, 96 50 C62 52, 52 62, 50 96 C48 62, 38 52, 4 50 C38 48, 48 38, 50 4 Z"/></svg>';

/* ================================================================
   КЛАССЫ НАЧИНОК (символы «космос база / классик / люкс»)
   Класс определяется по цене начинки:
     2800р/кг → база, 3000р/кг → классик, 3600р/кг → люкс.
   Картинки лежат рядом с core.js: assets/class-base.svg / class-classic.svg / class-lux.svg.
   ВАЖНО (на случай если перепутаны имена файлов):
     если визуально в плоском калькуляторе под ценой появляется не та надпись —
     просто переименуйте файлы в папке assets/ местами.
     В ярусных тортах показываются все три рядом — там подсказка статичная.
   ================================================================ */
const CLASS_ORDER = ['base', 'classic', 'lux'];

function fillingClass(filling){
  const p = (window.FILLING_PRICES && FILLING_PRICES[filling]) || 0;
  if (p >= 3500) return 'lux';
  if (p >= 3000) return 'classic';
  return 'base';
}

const CLASS_TIPS = {
  base:    'космос база — от 2\u202f800\u00a0р/кг',
  classic: 'космос классика — от 3\u202f000\u00a0р/кг',
  lux:     'космос люкс — от 3\u202f600\u00a0р/кг'
};

function classBadge(cls){
  const tip = CLASS_TIPS[cls] || cls;
  return `<div class="fill-class"><div class="fill-class__ico is-${cls}" title="${tip}" aria-label="класс начинки: ${cls}"></div></div>`;
}

function classBadgeAll(){
  return `<div class="fill-class fill-class--all">
    ${CLASS_ORDER.map(c => `<div class="fill-class__ico is-${c}" title="${CLASS_TIPS[c]||c}" aria-label="класс начинки: ${c}"></div>`).join('')}
  </div>`;
}

/* ================================================================
   ЗАГОЛОВОК: каждое слово на отдельной строке + автоматический подбор размера
   так, чтобы каждое слово растягивалось почти на всю ширину контейнера.
   ================================================================ */
function buildTitleHTML(title){
  if (!title) return '';
  const ws = String(title).trim().split(/\s+/);
  const groups = (ws.length >= 4)
    ? ws.reduce((a, w, i) => { if (i % 2 === 0) a.push([w]); else a[a.length-1].push(w); return a; }, []).map(g => g.join('\u00a0'))
    : ws;
  return groups.map(w => `<span class="word">${w}</span>`).join('');
}

function fitTitle(titleEl, opts){
  if (!titleEl) return;
  const o = Object.assign({ max:96, min:26, target:0.96 }, opts || {});
  const containerWidth = titleEl.clientWidth;
  if (!containerWidth) return;
  const words = titleEl.querySelectorAll('.word');
  words.forEach(word => {
    word.style.fontSize = o.max + 'px';
    const w = word.scrollWidth;
    if (!w) return;
    let size = o.max * (containerWidth * o.target / w);
    size = Math.max(o.min, Math.min(o.max, size));
    word.style.fontSize = size + 'px';
  });
}

/* ================================================================
   КАСТОМНЫЙ ДРОПДАУН
   Превращает <select> в кастомный компонент: розовая обводка,
   розовая подложка hover, красный текст hover.
   ================================================================ */
function mountCustomSelect(selectEl){
  if (!selectEl || selectEl.dataset.mounted === '1') return;
  selectEl.dataset.mounted = '1';
  selectEl.style.display = 'none';

  const wrap = document.createElement('div');
  wrap.className = 'csel';

  const trigger = document.createElement('button');
  trigger.type = 'button';
  trigger.className = 'csel__trigger';
  trigger.textContent = selectEl.value;

  const list = document.createElement('div');
  list.className = 'csel__list';

  [...selectEl.options].forEach(opt => {
    const item = document.createElement('div');
    item.className = 'csel__opt' + (opt.value === selectEl.value ? ' is-selected' : '');
    item.textContent = opt.textContent;
    item.dataset.value = opt.value;
    item.onclick = (e) => {
      e.stopPropagation();
      selectEl.value = opt.value;
      trigger.textContent = opt.textContent;
      list.querySelectorAll('.csel__opt').forEach(x => x.classList.remove('is-selected'));
      item.classList.add('is-selected');
      wrap.classList.remove('is-open');
      selectEl.dispatchEvent(new Event('change', { bubbles:true }));
    };
    list.appendChild(item);
  });

  trigger.onclick = (e) => {
    e.stopPropagation();
    const wasOpen = wrap.classList.contains('is-open');
    document.querySelectorAll('.csel.is-open').forEach(c => c.classList.remove('is-open'));
    if (!wasOpen) wrap.classList.add('is-open');
  };

  wrap.appendChild(trigger);
  wrap.appendChild(list);
  selectEl.parentNode.insertBefore(wrap, selectEl.nextSibling);
}

document.addEventListener('click', () => {
  document.querySelectorAll('.csel.is-open').forEach(c => c.classList.remove('is-open'));
});

/* ================================================================
   ХЕДЕР
   ================================================================ */
function descSentencesHTML(text){
  if (!text) return '';
  return String(text).trim()
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/\n/g, '<br>');
}

function renderHeader(cake){
  if (cake.mobile) return '';
  if (!cake.title && !cake.desc && !cake.subtitle) return '';
  return `
    <header class="cake-header">
      ${cake.title    ? `<h1 class="cake-title">${buildTitleHTML(cake.title)}</h1>` : ''}
      ${cake.desc     ? `<p class="cake-desc">${descSentencesHTML(cake.desc)}</p>` : ''}
      ${cake.subtitle ? `<p class="cake-subtitle">${cake.subtitle}</p>` : ''}
      ${cake.details ? `<p class="cake-details">${cake.details}</p>` : ''}
    </header>
  `;
}

/* ================================================================
   На узком экране (≤900px) блок доставки идёт сразу под калькулятором
   (см. style.css). На десктопе «далее» открывает блок доставки.
   ================================================================ */
function isMobileCtx(){
  try {
    if (window.__kosmosForceMobile) return true;
    return new URLSearchParams(location.search).get('ctx') === 'mobile';
  } catch(_) { return false; }
}
window.setKosmosMobileCtx = function(on){
  var next = !!on;
  if (window.__kosmosForceMobile === next) return;
  window.__kosmosForceMobile = next;
  if (typeof window.__kosmosRedraw === 'function') window.__kosmosRedraw();
};

function nextBtnHTML(){
  if (isMobileCtx()) {
    return '';
  }
  return `
    <div class="send-row">
      <button id="send" class="next-btn" type="button">далее</button>
    </div>
  `;
}

/* Бантик идёт сразу после кнопки «далее» внутри самого калькулятора.
   Так бантик гарантированно «прилипает» к «далее» — даже если родительская
   страница торта кэшировала старую версию стилей. На мобильной cake-странице
   бантик не нужен — там сразу под калькулятором идёт блок доставки. */
function endBowHTML(){
  if (isMobileCtx()) return '';
  return '<img class="end-bow" src="' + kosmosAssetUrl('bow.svg') + '" alt="" aria-hidden="true">';
}

function totalHTML(total){
  return `
    <div class="total-wrap">
      <div class="total-meta">стоимость торта</div>
      <div class="total-row">
        <span class="sparkle">${SVG_SPARKLE}</span>
        <div class="total-value">${fmtMoney(total)}</div>
        <span class="sparkle">${SVG_SPARKLE}</span>
      </div>
    </div>
  `;
}

/* ================================================================
   ПОСТ-ОБРАБОТКА после draw()
   ================================================================ */
function postDraw(root){
  root.querySelectorAll('select.to-custom').forEach(mountCustomSelect);
  const title = root.querySelector('.cake-title');
  if (title) {
    fitTitle(title);
    if (!title.dataset.resizeBound){
      title.dataset.resizeBound = '1';
      window.addEventListener('resize', () => fitTitle(title));
    }
  }
  // кнопка «далее» — просит родителя открыть блок доставки
  const send = root.querySelector('#send');
  if (send && !send.dataset.bound){
    send.dataset.bound = '1';
    send.addEventListener('click', () => {
      try { window.dispatchEvent(new CustomEvent('kosmos-next')); } catch(_){}
    });
  }
  if (typeof window.__kosmosApplyScale === 'function'){
    requestAnimationFrame(window.__kosmosApplyScale);
  }
}

/* ================================================================
   ТИП 1 — ОДИН ЯРУСНЫЙ ТОРТ
   total = ярусы × декорPerTier  +  вес × 3200
   Поля выбора начинок отсутствуют (и в десктопе, и в мобилке):
   стоимость начинки в ярусных тортах фиксированная — 3 200 р/кг.
   ================================================================ */
window.renderTieredCake = function(cake){
  const FILLING_RATE = 3200;
  const state = {
    weight: cake.minWeight,
    tiers:  cake.minTiers
  };
  const root = document.getElementById('root');

  function calc(){
    return {
      decor:   state.tiers * cake.decorPerTier,
      filling: state.weight * FILLING_RATE,
      total:   state.tiers * cake.decorPerTier + state.weight * FILLING_RATE
    };
  }

  function draw(){
    const r = calc();
    root.innerHTML = `
      ${renderHeader(cake)}
      <div class="label">Сколько килограмм?</div>
      <div class="stepper">
        <button class="step-btn minus" data-act="w-" aria-label="минус" type="button">${SVG_MINUS}</button>
        <div class="value">${fmtWeight(state.weight)}</div>
        <button class="step-btn plus"  data-act="w+" aria-label="плюс" type="button">${SVG_PLUS}</button>
      </div>
      <div class="label">Сколько ярусов?</div>
      <div class="stepper">
        <button class="step-btn minus" data-act="t-" aria-label="минус" type="button">${SVG_MINUS}</button>
        <div class="value">${state.tiers}</div>
        <button class="step-btn plus"  data-act="t+" aria-label="плюс" type="button">${SVG_PLUS}</button>
      </div>
      <div class="hint">От ${cake.minTiers} ярус${cake.minTiers===1?'а':'ов'}. От ${fmtWeight(cake.minWeight)} кг.${cake.note?'<br>'+cake.note:''}</div>
      <div class="hint hint--big">Стоимость начинки в ярусных тортах фиксированная — 3&nbsp;200&nbsp;р/кг.</div>
      ${totalHTML(r.total)}
      ${nextBtnHTML()}
      ${endBowHTML()}
    `;

    root.querySelectorAll('button[data-act]').forEach(b => {
      b.onclick = () => {
        const a = b.dataset.act;
        if (a==='w+') state.weight = +(state.weight + 0.5).toFixed(1);
        if (a==='w-') state.weight = Math.max(cake.minWeight, +(state.weight - 0.5).toFixed(1));
        if (a==='t+') state.tiers++;
        if (a==='t-') state.tiers = Math.max(cake.minTiers, state.tiers - 1);
        draw();
      };
    });
    broadcastCake({
      cake: cake.name, total: r.total,
      weight: fmtWeight(state.weight), tiers: state.tiers,
      tiered: true
    });
    window.__kosmosRedraw = draw;
    postDraw(root);
  }

  draw();
};

/* ================================================================
   ТИП 2 — ФИКС. ВЕС
   total = вес × цена_начинки  +  декор(вес)
   ================================================================ */
window.renderFixedCake = function(cake){
  const state = { weight:2.5, filling:cake.fillings[0] };
  const root = document.getElementById('root');

  function calc(){
    const decor = cake.decor[state.weight];
    const filling = state.weight * FILLING_PRICES[state.filling];
    return { decor, filling, total: decor + filling };
  }

  function draw(){
    if (!cake.fillings.includes(state.filling)) state.filling = cake.fillings[0];
    const r = calc();
    root.innerHTML = `
      ${renderHeader(cake)}
      <div class="label">Сколько килограмм?</div>
      <div class="fixed-row" data-w="2.5">
        <button class="radio-big ${state.weight===2.5?'checked':''}" aria-label="2.5 кг" type="button"></button>
        <span class="value">2.5</span>
      </div>
      <div class="fixed-row" data-w="3.5">
        <button class="radio-big ${state.weight===3.5?'checked':''}" aria-label="3.5 кг" type="button"></button>
        <span class="value">3.5</span>
      </div>
      <div class="label">Начинка</div>
      <div class="tier-row">
        <select class="to-custom" id="filling">
          ${cake.fillings.map(f=>`<option ${f===state.filling?'selected':''}>${f}</option>`).join('')}
        </select>
      </div>
      ${classBadge(fillingClass(state.filling))}
      ${totalHTML(r.total)}
      ${nextBtnHTML()}
      ${endBowHTML()}
    `;
    root.querySelectorAll('.fixed-row[data-w]').forEach(row => {
      row.onclick = () => { state.weight = parseFloat(row.dataset.w); draw(); };
    });
    root.querySelector('#filling').onchange = e => { state.filling = e.target.value; draw(); };
    broadcastCake({
      cake: cake.name, total: r.total,
      weight: fmtWeight(state.weight), filling: state.filling,
      tiered: false
    });
    window.__kosmosRedraw = draw;
    postDraw(root);
  }
  draw();
};

/* ================================================================
   ТИП 3 — ПЛОСКИЙ ПО ВЕСУ
   total = вес × цена_начинки  +  декор(вес)
   ================================================================ */
window.renderWeightCake = function(cake){
  const state = { weight: cake.minWeight, filling: cake.fillings[0] };
  const root = document.getElementById('root');

  function calc(){
    const decor = decorForWeight(cake.decorTable, state.weight);
    const filling = state.weight * FILLING_PRICES[state.filling];
    return { decor, filling, total: decor + filling };
  }

  function decorHint(){
    if (cake.id === 'berry-fields') return `От ${fmtWeight(cake.minWeight)} кг. Цена декора растёт по 1 кг — от 3 000р до 24 000р.`;
    if (cake.id === 'tiramisu')     return `Стоимость только начинки — 3 000р/кг.`;
    const parts = cake.decorTable.map(r => {
      if (r.min === r.max) return `${r.min} кг — ${r.price.toLocaleString('ru-RU').replace(/,/g,' ')}р`;
      return `${fmtWeight(r.min)}–${fmtWeight(r.max)} кг — ${r.price.toLocaleString('ru-RU').replace(/,/g,' ')}р`;
    });
    return `От ${fmtWeight(cake.minWeight)} кг. Декор: ${parts.join(' · ')}.`;
  }

  function draw(){
    if (!cake.fillings.includes(state.filling)) state.filling = cake.fillings[0];
    const hasFillingPicker = cake.fillings.length > 1;
    const r = calc();
    root.innerHTML = `
      ${renderHeader(cake)}
      <div class="label">Сколько килограмм?</div>
      <div class="stepper">
        <button class="step-btn minus" data-act="w-" aria-label="минус" type="button">${SVG_MINUS}</button>
        <div class="value">${fmtWeight(state.weight)}</div>
        <button class="step-btn plus"  data-act="w+" aria-label="плюс" type="button">${SVG_PLUS}</button>
      </div>
      ${hasFillingPicker ? `
        <div class="label">Начинка</div>
        <div class="tier-row">
          <select class="to-custom" id="filling">
            ${cake.fillings.map(f=>`<option ${f===state.filling?'selected':''}>${f}</option>`).join('')}
          </select>
        </div>
        ${classBadge(fillingClass(state.filling))}
      ` : ''}
      <div class="hint">${decorHint()}${cake.note?'<br>'+cake.note:''}</div>
      ${totalHTML(r.total)}
      ${nextBtnHTML()}
      ${endBowHTML()}
    `;
    root.querySelectorAll('button[data-act]').forEach(b => {
      b.onclick = () => {
        const a = b.dataset.act;
        if (a==='w+') state.weight = +Math.min(cake.maxWeight, state.weight + 0.5).toFixed(1);
        if (a==='w-') state.weight = +Math.max(cake.minWeight, state.weight - 0.5).toFixed(1);
        draw();
      };
    });
    const fillSel = root.querySelector('#filling');
    if (fillSel) fillSel.onchange = e => { state.filling = e.target.value; draw(); };
    broadcastCake({
      cake: cake.name, total: r.total,
      weight: fmtWeight(state.weight), filling: state.filling,
      tiered: false
    });
    window.__kosmosRedraw = draw;
    postDraw(root);
  }
  draw();
};
