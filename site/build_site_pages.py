# -*- coding: utf-8 -*-
"""
Генерирует адаптивные страницы тортов site/cakes/*.html (десктоп + мобилка в одном HTML)
по данным calculator/build_cakes.py.

Перед сборкой страниц вызывает calculator/build_cakes.py (единые калькуляторы).

Также: site/index.html (каталог), site/preview.html, синхрон fillings/data.js.

Запуск из корня репозитория kosmos_calc:
  python build.py
  python site/build_site_pages.py
"""
from __future__ import annotations

import html
import importlib.util
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
BC = ROOT / "calculator" / "build_cakes.py"
PH = SITE / "photos"
CALC = ROOT / "calculator"


def get_class_assets_version() -> int:
    """Максимальный mtime среди class-base/classic/lux.svg — используется для
    cache-bust bb-class img src в filling bubble JS (placeholder __CLASS_V__)."""
    v = 0
    for name in ("class-base.svg", "class-classic.svg", "class-lux.svg"):
        f = CALC / "assets" / name
        if f.exists():
            v = max(v, int(f.stat().st_mtime))
    return v


def bust_class_svg_cache():
    """Подменяет ?v=... в calculator/style.css на mtime соответствующего SVG-файла,
    чтобы после ручной замены картинки в assets/ браузер не отдавал старую версию
    из кэша. Версия = int(mtime), уникальна для каждого файла. """
    css = CALC / "style.css"
    if not css.exists():
        return
    text = css.read_text(encoding="utf-8")
    for name in ("class-base.svg", "class-classic.svg", "class-lux.svg"):
        f = CALC / "assets" / name
        if not f.exists():
            continue
        v = int(f.stat().st_mtime)
        text = re.sub(
            rf"(url\('assets/{re.escape(name)})\?v=\d+('\))",
            lambda m, v=v: f"{m.group(1)}?v={v}{m.group(2)}",
            text,
        )
    css.write_text(text, encoding="utf-8")


def import_build_cakes():
    spec = importlib.util.spec_from_file_location("build_cakes_inline", BC)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def calc_asset_versions() -> tuple[str, str, str, str]:
    css = CALC / "style.css"
    js = CALC / "core.js"
    dcss = CALC / "delivery" / "delivery.css"
    djs = CALC / "delivery" / "delivery.js"
    return tuple(
        str(int(p.stat().st_mtime)) if p.exists() else ""
        for p in (css, js, dcss, djs)
    )


def page_embed_snippet(rel_path: str, public_site: str) -> str:
    """Тело страницы для вставки в Tilda: абсолютные URL на GitHub Pages."""
    path = SITE / rel_path
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    m = re.search(r"<body[^>]*>([\s\S]*)</body>", text, re.IGNORECASE)
    body = m.group(1).strip() if m else text
    repo = public_site.rstrip("/").rsplit("/site", 1)[0]
    body = body.replace("../../calculator/", f"{repo}/calculator/")
    body = body.replace("../", f"{public_site.rstrip('/')}/")
    return body


def bust_calc_asset_cache():
    """Дописывает ?v=<mtime> к style.css / core.js в отдельных страницах калькулятора."""
    css = CALC / "style.css"
    js = CALC / "core.js"
    css_v = int(css.stat().st_mtime) if css.exists() else 0
    js_v = int(js.stat().st_mtime) if js.exists() else 0
    targets: list[Path] = []
    for sub in ("cakes",):
        d = CALC / sub
        if d.is_dir():
            targets.extend(d.rglob("*.html"))
    for p in targets:
        text = p.read_text(encoding="utf-8")
        new = text
        new = re.sub(
            r'(href=")(\.\./\.\./style\.css)(?:\?v=\d+)?(")',
            lambda m: f'{m.group(1)}{m.group(2)}?v={css_v}{m.group(3)}',
            new,
        )
        new = re.sub(
            r'(src=")(\.\./\.\./core\.js)(?:\?v=\d+)?(")',
            lambda m: f'{m.group(1)}{m.group(2)}?v={js_v}{m.group(3)}',
            new,
        )
        if new != text:
            p.write_text(new, encoding="utf-8")

# Порядок на главной (как договорились с заказчиком)
CATALOG_ORDER = [
    "fairy-cake", "tiramisu", "lumiere", "letter", "big-cherry-fairy-cake",
    "swan-lake", "babylon", "love-in-mood", "dancing-queen", "secret-garden",
    "chapito", "anna", "bell", "bohemian-rhapsody", "totoro", "kelly",
    "la-la-land", "darcy", "shine-bright", "green-day", "orpheus",
    "cherry-orchard", "elizabeth", "berry-fields", "kuinji", "faberge",
    "sailor-moon", "apollo", "blueberry-hill", "fuji"
]

_RE_MENU_CAKE_SHELL = re.compile(
    r'\s*<li class="menu-cake-shell"[\s\S]*?</li>\s*',
    re.IGNORECASE,
)


def strip_menu_cake_shell(head: str) -> str:
    """Меню-«тортик» было удалено по требованию пользователя. При регенерации
    каталога вычищаем его, если он там ещё остался от старых сборок."""
    return _RE_MENU_CAKE_SHELL.sub("\n", head, count=1)


def patch_catalog_head(head: str) -> str:
    """Дополнительные правки <head>+<body-начало> каталога, чтобы пересборка
    не возвращала старые версии:
      • убираем верхнюю «серую полосу» (padding:64px → 0, padding:56px → 0);
      • заменяем «лучший тортик» на «лучший вариант»;
      • удаляем устаревший li.menu-cake-shell;
      • меню (popup) убрано полностью: <button class="menu-btn"> → <a>-ссылка
        на сам каталог, <ul class="menu-list"> вырезано.
    """
    head = strip_menu_cake_shell(head)
    head = re.sub(r"padding:\s*64px\s*0\s*0", "padding:0", head)
    head = re.sub(r"padding:\s*56px\s*0\s*0", "padding:0", head)
    head = head.replace("подберет лучший тортик", "подберёт лучший вариант")
    head = strip_menu_list(head)
    head = convert_menu_btn_to_link(head, href="index.html")
    return head


_RE_MENU_LIST = re.compile(
    r'<ul[^>]*class="menu-list"[^>]*>[\s\S]*?</ul>\s*',
    re.IGNORECASE,
)


def strip_menu_list(html_text: str) -> str:
    """Вырезает popup-меню <ul class="menu-list"> вместе со всеми пунктами. """
    return _RE_MENU_LIST.sub("", html_text)


_RE_MENU_BTN_BUTTON = re.compile(
    r'<button([^>]*\sclass="menu-btn"[^>]*)>([\s\S]*?)</button>',
    re.IGNORECASE,
)


def convert_menu_btn_to_link(html_text: str, href: str) -> str:
    """<button class="menu-btn">…</button> → <a class="menu-btn" href="…">…</a>.
    Убирает <span class="menu-label">меню</span> из содержимого и заменяет
    type="button"/aria-label="меню". """
    def repl(m):
        attrs = m.group(1)
        inner = m.group(2)
        attrs = re.sub(r'\stype="button"', "", attrs)
        attrs = re.sub(r'\saria-label="[^"]*"', "", attrs)
        inner = re.sub(
            r'<span[^>]*class="menu-label"[^>]*>[\s\S]*?</span>\s*',
            "",
            inner,
        )
        return f'<a{attrs} href="{href}" aria-label="каталог">{inner}</a>'
    return _RE_MENU_BTN_BUTTON.sub(repl, html_text)


_RE_FIT_IIFE = re.compile(
    r"\s*<script>\s*(?:/\*[\s\S]*?\*/\s*)?\(function\(\)\{[\s\S]*?fitCovers[\s\S]*?\}\)\(\);\s*</script>",
    re.IGNORECASE,
)


def strip_fit_script(foot: str) -> str:
    """Раньше в каталоге подбирался размер подписи JS-ом. Теперь шрифт фиксированный —
    подчищаем старый код fitCovers, как отдельный IIFE-скрипт, так и inline-функцию
    внутри основного <script>. Для inline-варианта режем от предшествующего комментария
    до строки с .then(fitCovers).catch(...). """
    foot = _RE_FIT_IIFE.sub("", foot)
    foot = strip_menu_js(foot)
    if "fitCovers" not in foot:
        return foot
    lines = foot.splitlines(keepends=True)
    start = end = None
    for i, ln in enumerate(lines):
        if start is None and ln.lstrip().startswith("/*") and "fitCovers" in "".join(lines[i:i + 6]):
            start = i
        if start is not None and "fitCovers" in ln and ".catch" in ln:
            end = i
            break
    if start is not None and end is not None and end >= start:
        del lines[start:end + 1]
        foot = "".join(lines)
    return foot


_MENU_JS_MARKERS = (
    "menu-toggle",
    "menu-list",
    "menu-close",
    ".classList.toggle('is-open')",
    '.classList.toggle("is-open")',
    ".classList.remove('is-open')",
    '.classList.remove("is-open")',
    "menuList",
    "menuBtn",
)

# «Мусорные» строки внутри <script>, которые остаются от старого popup-меню
# (e.stopPropagation, голый document.addEventListener('click', …) и сирые `})`).
_MENU_JS_ORPHAN_PATTERNS = (
    re.compile(r"e\.stopPropagation\(\)\s*;"),
    re.compile(r"document\.addEventListener\(\s*['\"]click['\"]\s*,\s*\(?\s*e?\s*\)?\s*=>\s*\{"),
    re.compile(r"const\s+(?:btn|list|menuBtn|menuList)\s*=\s*document\.getElementById"),
)

_RE_SCRIPT_BLOCK = re.compile(
    r"<script>([\s\S]*?)</script>",
    re.IGNORECASE,
)


def strip_menu_js(html_text: str) -> str:
    """Удаляет инлайн-JS popup-меню. Внутри каждого <script>…</script>:
      • строки, содержащие маркеры меню (menu-toggle, menu-list, .toggle('is-open'),
        const btn/list/…) — выбрасываются;
      • остаются «сиротские» строки (e.stopPropagation; голый document.addEventListener;
        одинокие `});`) — режутся тоже;
      • если после чистки в блоке остался только whitespace и пара пустых стрелочных
        функций — режем весь <script> целиком. """
    def clean_script(m: re.Match) -> str:
        body = m.group(1)
        if not any(t in body for t in _MENU_JS_MARKERS) and not any(p.search(body) for p in _MENU_JS_ORPHAN_PATTERNS):
            return m.group(0)
        kept: list[str] = []
        for line in body.splitlines(keepends=True):
            if any(t in line for t in _MENU_JS_MARKERS):
                continue
            if any(p.search(line) for p in _MENU_JS_ORPHAN_PATTERNS):
                continue
            kept.append(line)
        # подчищаем одинокие закрывающие скобки/фигурки, оставшиеся от удалённых блоков
        cleaned: list[str] = []
        for line in kept:
            stripped = line.strip()
            if stripped in ("});", "})", "}", ");"):
                continue
            cleaned.append(line)
        residual = "".join(cleaned).strip()
        if not residual:
            return ""
        return f"<script>{''.join(cleaned)}</script>"

    return _RE_SCRIPT_BLOCK.sub(clean_script, html_text)


def load_cakes():
    src = BC.read_text(encoding="utf-8")
    cut = src.index("#  ГЕНЕРАЦИЯ")
    ns = {"__file__": str(BC), "__name__": "build_cakes_cat"}
    exec(compile(src[:cut], str(BC), "exec"), ns)
    return ns["CAKES"]


PHOTO_EXT = (".jpg", ".jpeg", ".png", ".webp")


def list_cake_image_files(cid: str) -> list[Path]:
    d = PH / cid
    if not d.is_dir():
        return []
    xs = [p for p in d.iterdir() if p.is_file() and p.suffix.lower() in PHOTO_EXT]
    return sorted(xs, key=lambda p: p.name.lower())


def pick_cover_path(cid: str) -> Path | None:
    """Обложка: cover.* или первый файл, не slice-N.* (как после import_photos_raw)."""
    files = list_cake_image_files(cid)
    if not files:
        return None
    # Важно: на Windows path.exists() case-insensitive и может вернуть True
    # для несуществующего по регистру имени (cover.jpg при реальном cover.JPG).
    # Поэтому ищем через фактические имена из списка файлов и возвращаем
    # именно реальный Path.
    cover_names = {f"cover{ext}" for ext in PHOTO_EXT}
    for p in files:
        if p.name.lower() in cover_names:
            return p
    for p in files:
        if not re.match(r"slice-\d+\.", p.name, re.I):
            return p
    return files[0]


def slice_paths_after_cover(cid: str, cover: Path | None) -> list[Path]:
    files = list_cake_image_files(cid)
    named: list[tuple[int, Path]] = []
    for p in files:
        m = re.match(r"slice-(\d+)\.", p.name, re.I)
        if m:
            named.append((int(m.group(1)), p))
    if named:
        named.sort(key=lambda t: t[0])
        return [t[1] for t in named]
    if cover is None:
        return []
    covr = cover.resolve()
    return [p for p in files if p.resolve() != covr]


def cover_filename(cid: str) -> str:
    """Имя файла обложки для каталога (реальный файл в photos/<id>/)."""
    p = pick_cover_path(cid)
    # В проде (Linux) файловая система case-sensitive. Если подставить
    # "cover.jpg", а реально на диске "cover.JPG", картинка 404.
    # Поэтому всегда используем реальное имя найденного файла.
    if p:
        return p.name
    # Фолбэк тоже в uppercase — чаще всего у нас именно такой cover.
    return "cover.JPG"


def normalize_cover_filenames(cids: list[str]) -> None:
    """Приводит имя обложки к каноническому виду cover.<ext> (lowercase).
    Это устраняет плавающий баг на GitHub Pages, когда то /cover.jpg, то /cover.JPG.
    На Linux это разные пути -> периодические 404 в каталоге.
    """
    for cid in cids:
        p = pick_cover_path(cid)
        if p is None:
            continue
        ext = p.suffix.lower()
        # jpg/jpeg сводим к одному канону cover.jpg
        if ext in (".jpg", ".jpeg"):
            canon_name = "cover.jpg"
        else:
            canon_name = f"cover{ext}"
        canon = p.with_name(canon_name)
        if p.name == canon_name:
            continue
        # Для case-only rename на Windows нужен промежуточный шаг.
        tmp = p.with_name(f"__cover_tmp__{cid}{ext}")
        i = 0
        while tmp.exists():
            i += 1
            tmp = p.with_name(f"__cover_tmp__{cid}_{i}{ext}")
        p.rename(tmp)
        if canon.exists():
            canon.unlink()
        tmp.rename(canon)


PHOTO_REL = "../photos"


def photo_paths(cid: str, rel: str = PHOTO_REL) -> tuple[list[str], list[str]]:
    """Десктоп: cover + slice-…; мобилка: slice-… + cover в конце."""
    rel = f"{rel}/{cid}"
    cov = pick_cover_path(cid)
    if cov is None:
        fb = f"{PHOTO_REL}/fairy-cake/cover.jpg"
        return ([fb], [fb])
    slices = slice_paths_after_cover(cid, cov)
    desk = [f"{rel}/{cov.name}"] + [f"{rel}/{p.name}" for p in slices]
    mob = [f"{rel}/{p.name}" for p in slices] + [f"{rel}/{cov.name}"]
    return desk, mob


def cake_photos_html(cid: str, cname: str) -> str:
    """Одна лента фото: на десктопе — вертикальный скролл, на мобилке — карусель."""
    if cid in PHOTO_GRID_CAKES:
        _, paths = photo_paths(cid)
        half = max(1, (len(paths) + 1) // 2)
        paths = paths[:half]
    else:
        _, paths = photo_paths(cid)
    lines = []
    for i, p in enumerate(paths):
        if "cover" in p.split("/")[-1].lower():
            alt = cname if i == len(paths) - 1 and paths[-1] == p else f"{cname} — обложка"
        else:
            alt = f"{cname} — деталь"
        load = "eager" if i == 0 else "lazy"
        lines.append(
            f'      <img class="photo" src="{html.escape(p)}" alt="{html.escape(alt)}" loading="{load}">'
        )
    return "\n".join(lines)


def subtitle_html(cake: dict) -> str:
    parts = [html.escape(cake.get("subtitle") or "")]
    if cake.get("note"):
        parts.append(html.escape(cake["note"]))
    return " ".join(x for x in parts if x).strip()


UNIFIED_PAGE = """<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>__PAGE_TITLE__</title>
<link rel="stylesheet" href="../style.css">
<link rel="stylesheet" href="../../calculator/style.css?v=__CALC_CSS_V__">
<link rel="stylesheet" href="../../calculator/delivery/delivery.css?v=__DLV_CSS_V__">
<style>
  /* Узкая колонка: три колонки остаются в ряд. */
  @media (min-width:901px) and (max-width:1280px){
    .cake-page{
      grid-template-columns:repeat(3, minmax(0, 1fr));
      grid-template-rows:minmax(0,1fr);
    }
    .cake-col{height:100%}
    .col-photo,.col-third{overflow-y:auto}
    .col-photo{padding:0}
    .col-info{padding:0 22px 40px;overflow-y:auto;overflow-x:hidden;display:flex;flex-direction:column;align-items:center;gap:0;scrollbar-width:none;-ms-overflow-style:none}
    .col-info::-webkit-scrollbar{display:none;width:0;height:0}
    .col-info .cake-title{
      position:sticky;top:0;z-index:50;background:var(--bg);
      font-size:56px;line-height:.7;padding:18px 0 14px;width:100%;
    }
    .cake-title .word{line-height:.7;padding-bottom:.05em}
    .col-info .calc-frame{width:96%;max-width:440px;height:auto;min-height:0;flex:none;margin:8px auto 32px}
    .col-third{overflow:hidden;height:100%;position:relative}
    .col-third .col-fillings,.col-third .col-delivery{position:absolute;inset:0;height:auto;overflow-y:auto}
    .col-third.is-delivery .col-delivery{display:flex;flex-direction:column}
    .cake-page.is-delivery .col-third .col-fillings{display:none}
    .delivery-back{position:absolute;right:18px;bottom:18px;left:auto;width:36px;height:36px}
    .delivery-back svg{width:100%;height:100%}
  }
</style>
</head>
<body class="cake-page-body">

<a class="back-to-catalog" href="../index.html" aria-label="вернуться в каталог">
<svg width="64" height="81" viewBox="0 0 64 81" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M44.9803 79.3892C42.8039 81.537 39.2754 81.5369 37.099 79.3892L1.6323 44.3888C-0.544105 42.2411 -0.544105 38.7589 1.6323 36.6111L37.099 1.61081C39.2754 -0.536903 42.8039 -0.536951 44.9803 1.61081C47.1567 3.75858 47.1567 7.24072 44.9803 9.38851L19.0273 35.0002L58.427 35.0002C61.5049 35.0002 64 37.4626 64 40.5C64 43.5374 61.5049 45.9998 58.427 45.9998L19.0273 45.9998L44.9803 71.6115C47.1566 73.7593 47.1567 77.2414 44.9803 79.3892Z" fill="white"/>
</svg>
</a>

<div class="cake-page">

  <section class="cake-col col-photo" aria-label="фото торта">
    <div class="cake-photos" id="cake-photos">
__PHOTOS__
    </div>
    <div class="cake-photo-dots mob-dots" id="cake-photo-dots" aria-hidden="true"></div>
  </section>

  <section class="cake-col col-info" aria-label="параметры торта">
    <h1 class="cake-title">__H1__</h1>
    <p class="cake-desc">__DESC__</p>
    <p class="cake-sub">__SUB__</p>
    <div class="calc-frame">
      <div class="calc-scroll" id="root"></div>
    </div>
  </section>

  <section class="cake-col col-third" aria-label="третья колонка">
__FILL_HEAD____THIRD_COL_INNER__
    <div class="cake-fillings-dots mob-dots mob-dots--small" id="cake-fillings-dots" aria-hidden="true"></div>
    <div class="col-delivery" id="delivery-col" aria-hidden="true">
      <button class="delivery-back" id="delivery-back" type="button" aria-label="закрыть доставку">
        <svg viewBox="0 0 22 21" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
          <path d="M0.877209 0.877275C2.04698 -0.292499 3.94367 -0.292351 5.11354 0.877275L10.5657 6.32942L16.012 0.883134C17.1818 -0.286425 19.0785 -0.286409 20.2483 0.883134C21.4181 2.05291 21.4179 3.9496 20.2483 5.11946L14.802 10.5658L20.1174 15.8812C21.2873 17.051 21.2873 18.9477 20.1174 20.1175C18.9476 21.2872 17.0509 21.2873 15.8811 20.1175L10.5657 14.8021L5.2444 20.1234C4.07455 21.2932 2.17792 21.2932 1.00807 20.1234C-0.161545 18.9535 -0.161701 17.0568 1.00807 15.887L6.32936 10.5658L0.877209 5.1136C-0.292372 3.94378 -0.292433 2.04706 0.877209 0.877275Z"/>
        </svg>
      </button>
      <div class="delivery-inline" id="dlv-root"></div>
    </div>
  </section>

</div>

<script src="../../calculator/core.js?v=__CALC_JS_V__"></script>
<script>
__CALC_INIT__
</script>
<script src="../../calculator/delivery/delivery.js?v=__DLV_JS_V__"></script>
<script>Kosmos.mountDelivery(document.getElementById('dlv-root'));</script>
<script src="../fillings/data.js"></script>
<script>
__PAGE_JS__
</script>
</body>
</html>
"""

FILL_HEAD_HTML = (
    '    <div class="cake-fill-head">\n'
    '      <h2 class="mob-section-title">Что внутри?'
    '<img class="mob-section-cherry" src="../assets/cherry.svg" alt="" aria-hidden="true">'
    '</h2>\n'
    '    </div>\n'
)

SHARED_JS = r"""  /* Меню удалено: кнопка «К» теперь — простая ссылка-каталог (см. шаблон). */

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
      cls.src = `../assets/class-${slug}.svg?v=__CLASS_V__`;
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
     и для вертикальной «колбасы» начинок и фото на десктопе. */
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
    /* Клонируем, пока общая длина не превысит видимую область как минимум в 2 раза,
       иначе при wrap-around будут мелькать пустоты на широких контейнерах. */
    var safety = 0;
    while (origSize() < viewSize() * 2 + 4 && safety++ < 8){
      kids.forEach(function(c){ el.appendChild(c.cloneNode(true)); });
    }
    var dead = 0, sp = speed || (vert ? 0.55 : 0.9);
    var id = setInterval(function(){
      if (dead) return;
      var sz = origSize();
      if (sz < 8) return;
      var c = vert ? el.scrollTop : el.scrollLeft;
      c += sp;
      if (c >= sz) c -= sz;
      if (vert) el.scrollTop = c; else el.scrollLeft = c;
    }, 30);
    function kill(){ dead = 1; clearInterval(id); }
    el.addEventListener('touchstart', kill, {passive:true});
    el.addEventListener('wheel', kill, {passive:true});
    el.addEventListener('pointerdown', kill, {passive:true});
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
"""

PAGE_JS = SHARED_JS


PHOTO_GRID_CAKES = {"tiramisu"}


def photo_paths_split(cid: str) -> tuple[list[str], list[str], list[str], list[str]]:
    """Для PHOTO_GRID_CAKES делим фото пополам: левая колонка — первая половина,
    третья колонка (вместо начинок) — вторая половина. Тот же сплит для мобилки. """
    desk, mob = photo_paths(cid)
    half_d = max(1, (len(desk) + 1) // 2)
    half_m = max(1, (len(mob) + 1) // 2)
    return desk[:half_d], desk[half_d:], mob[:half_m], mob[half_m:]


def third_col_inner_html(cake: dict) -> str:
    """Содержимое третьей колонки на десктопе.
    Для PHOTO_GRID_CAKES — вертикальный стек больших фото (как .col-photo слева).
    Для остальных — обычный контейнер начинок, который JS заполняет срезами. """
    cid = cake["id"]
    fill = html.escape(cake.get("fillings") or "BASE")
    if cid in PHOTO_GRID_CAKES:
        _left, right, _, _ = photo_paths_split(cid)
        if not right:
            right = _left[-1:] or [f"{PHOTO_REL}/fairy-cake/cover.jpg"]
        items = "\n".join(
            f'      <img class="photo" src="{html.escape(p)}" alt="{html.escape(cake["name"])}">'
            for p in right
        )
        return (
            '    <div class="col-fillings col-fillings--photos" id="fillings-col" data-fillings="">\n'
            f"{items}\n"
            '    </div>'
        )
    return f'    <div class="col-fillings" id="fillings-col" data-fillings="{fill}"></div>'


def fill_head_html(cake: dict) -> str:
    if cake["id"] in PHOTO_GRID_CAKES:
        return ""
    return FILL_HEAD_HTML


def render_cake_page(cake: dict) -> str:
    bc = import_build_cakes()
    render_fn, data_js = bc.cake_render_js(cake)
    css_v, js_v, dcss_v, djs_v = calc_asset_versions()
    cid = cake["id"]
    name = cake["name"]
    page_title = html.escape(f"{name} — kosmos")
    h1 = html.escape(name)
    desc = html.escape(cake.get("desc") or "")
    sub = subtitle_html(cake)
    calc_init = f"{render_fn}({data_js});"
    js = PAGE_JS.replace("__CLASS_V__", str(get_class_assets_version()))
    return (
        UNIFIED_PAGE.replace("__PAGE_TITLE__", page_title)
        .replace("__PHOTOS__", cake_photos_html(cid, name))
        .replace("__H1__", h1)
        .replace("__DESC__", desc)
        .replace("__SUB__", sub)
        .replace("__CALC_INIT__", calc_init)
        .replace("__CALC_CSS_V__", css_v)
        .replace("__CALC_JS_V__", js_v)
        .replace("__DLV_CSS_V__", dcss_v)
        .replace("__DLV_JS_V__", djs_v)
        .replace("__FILL_HEAD__", fill_head_html(cake))
        .replace("__THIRD_COL_INNER__", third_col_inner_html(cake))
        .replace("__PAGE_JS__", js)
    )


def ordered_cakes(cakes: list, by_id: dict) -> list:
    seen: set[str] = set()
    out: list = []
    for cid in CATALOG_ORDER:
        if cid in by_id:
            out.append(by_id[cid])
            seen.add(cid)
    for c in cakes:
        if c["id"] not in seen:
            out.append(c)
            seen.add(c["id"])
    return out


def sync_kosmos_filling_sets() -> None:
    core = (ROOT / "calculator" / "core.js").read_text(encoding="utf-8")
    base_start = core.index("const _BASE =")
    base_end = core.index("window.FILLING_SETS", base_start)
    base_block = core[base_start:base_end].strip()
    fs_start = core.index("window.FILLING_SETS =")
    fs_end = core.index("window.fmtMoney", fs_start)
    filling_sets = core[fs_start:fs_end].strip()
    filling_sets = filling_sets.replace("window.FILLING_SETS", "window.KOSMOS_FILLING_SETS", 1)
    extracted = filling_sets
    data_path = SITE / "fillings" / "data.js"
    data = data_path.read_text(encoding="utf-8")
    m_start = "/* >>> SYNC_FILLING_SETS"
    m_end = "/* <<< SYNC_FILLING_SETS */"
    if m_start not in data or m_end not in data:
        print("WARN: маркеры SYNC_FILLING_SETS в fillings/data.js не найдены — пропуск синхрона")
        return
    a = data.index(m_start)
    b = data.index(m_end) + len(m_end)
    block = f"/* >>> SYNC_FILLING_SETS (build_site_pages.py — из calculator/core.js) */\n{extracted}\n{m_end}"
    data_path.write_text(data[:a] + block + data[b:], encoding="utf-8")
    print("OK: KOSMOS_FILLING_SETS ← calculator/core.js (fillings/data.js)")


def write_site_preview_index(cakes: list, by_id: dict) -> None:
    """Полное превью site/preview.html — адаптивные страницы тортов."""
    base = "https://ab-aacoop.github.io/kosmos_calc/site"
    oc = ordered_cakes(cakes, by_id)

    def card_cake(c: dict) -> str:
        cid, nm = c["id"], html.escape(c["name"])
        sn = f"snip-{cid}"
        snippet = html.escape(page_embed_snippet(f"cakes/{cid}.html", base))
        return (
            f'  <div class="card">\n'
            f'    <header>\n'
            f'      <span class="type">адаптив</span>\n'
            f'      <span class="name">{nm}</span>\n'
            f'      <a class="open" href="cakes/{html.escape(cid)}.html" target="_blank">↗</a>\n'
            f"    </header>\n"
            f'    <div class="frame-wrap"><object data="cakes/{html.escape(cid)}.html" type="text/html" title="{nm}"></object></div>\n'
            f'    <div class="snip">\n'
            f'      <textarea readonly id="{sn}">{snippet}</textarea>\n'
            f'      <div class="snip-row">\n'
            f'        <button type="button" data-copy="{sn}">копировать сниппет</button>\n'
            f'        <span class="ok" data-ok="{sn}">✓ скопировано</span>\n'
            f"      </div>\n"
            f"    </div>\n"
            f"  </div>"
        )

    cake_rows = "\n".join(card_cake(c) for c in oc)

    html_out = f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Kosmos cake — превью страниц сайта</title>
<style>
  *{{box-sizing:border-box}}
  html,body{{margin:0;padding:0;background:#eaeaea;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:#222}}
  body{{padding:24px}}
  h1{{margin:0 0 6px;font-size:22px}}
  h2{{margin:28px 0 10px;font-size:16px;color:#555}}
  p.lead{{margin:0 0 14px;color:#555;font-size:14px;max-width:900px;line-height:1.45}}
  p.lead a{{color:#d83448}}
  .topbar{{display:flex;gap:10px;flex-wrap:wrap;margin:0 0 18px}}
  .topbar a{{
    text-decoration:none;background:#fff;border:1px solid #ddd;padding:7px 12px;
    border-radius:6px;color:#222;font-size:13px;font-weight:500;
  }}
  .topbar a.primary{{background:#d83448;color:#fff;border-color:#d83448}}
  .topbar a:hover{{filter:brightness(0.95)}}

  .grid-dsk{{display:grid;gap:18px;grid-template-columns:1fr;align-items:start}}
  .grid-mob{{display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(380px,1fr));align-items:start}}
  .grid-cakes{{display:grid;gap:16px;grid-template-columns:repeat(auto-fill,minmax(520px,1fr));align-items:start}}

  .card{{display:flex;flex-direction:column;background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,.08)}}
  .card header{{padding:8px 14px;border-bottom:1px solid #eee;display:flex;align-items:center;gap:10px;font-size:12px}}
  .card .type{{padding:2px 8px;background:#d83448;color:#fff;border-radius:999px;font-size:10px;text-transform:uppercase;letter-spacing:.3px}}
  .card .name{{font-weight:600;flex:1}}
  .card a.open{{color:#999;text-decoration:none;font-size:14px}}
  .card a.open:hover{{color:#d83448}}

  .frame-wrap{{width:100%;background:#cfcfcf}}
  .grid-dsk .frame-wrap{{aspect-ratio:1280/800}}
  .grid-cakes .frame-wrap{{aspect-ratio:1280/800}}
  .grid-cakes.grid-mob .frame-wrap{{aspect-ratio:380/780}}
  .frame-wrap object{{display:block;width:100%;height:100%;border:0}}

  .snip{{padding:10px 12px;border-top:1px solid #eee;background:#fafafa;display:flex;flex-direction:column;gap:6px}}
  .snip textarea{{
    width:100%;min-height:48px;resize:vertical;
    font-family:Menlo,Consolas,monospace;font-size:11px;line-height:1.4;
    border:1px solid #ddd;border-radius:5px;padding:6px;background:#fff;color:#333;
  }}
  .snip-row{{display:flex;gap:8px;align-items:center}}
  .snip button{{
    background:#d83448;color:#fff;border:0;border-radius:5px;padding:6px 12px;
    font-size:12px;cursor:pointer;font-weight:600;
  }}
  .snip button:hover{{background:#b22937}}
  .snip .ok{{font-size:11px;color:#3b9b4f;opacity:0;transition:opacity .25s}}
  .snip .ok.show{{opacity:1}}
</style>
</head>
<body>

<h1>Kosmos cake — превью страниц сайта</h1>
<p class="lead">
  Каждая страница — готовый inline HTML для Tilda / Readymag (без iframe).
  Ниже — главная, «о нас» и <strong>все страницы тортов</strong> (одна адаптивная версия), с кнопкой копирования сниппета.
  Фото торта: положите файлы в <code>site/photos raw/&lt;id&gt;/</code> и выполните
  <code>python site/import_photos_raw.py</code>, затем <code>python site/build_site_pages.py</code>.
</p>

<div class="topbar">
  <a class="primary" href="../calculator/cakes/">↗ калькуляторы</a>
  <a href="cakes/">↗ страницы тортов</a>
  <a href="../calculator/delivery/preview.html">↗ блок доставки</a>
</div>

<h2>Главная (каталог)</h2>
<div class="grid-dsk">
  <div class="card">
    <header>
      <span class="type">каталог</span>
      <span class="name">главная</span>
      <a class="open" href="index.html" target="_blank">↗</a>
    </header>
    <div class="frame-wrap"><object data="index.html" type="text/html" title="главная"></object></div>
    <div class="snip">
      <textarea readonly id="snip-home">{html.escape(page_embed_snippet("index.html", base))}</textarea>
      <div class="snip-row">
        <button type="button" data-copy="snip-home">копировать сниппет</button>
        <span class="ok" data-ok="snip-home">✓ скопировано</span>
      </div>
    </div>
  </div>
</div>

<h2>О нас</h2>
<div class="grid-dsk">
  <div class="card">
    <header>
      <span class="type">о нас</span>
      <span class="name">о нас</span>
      <a class="open" href="about.html" target="_blank">↗</a>
    </header>
    <div class="frame-wrap"><object data="about.html" type="text/html" title="о нас"></object></div>
    <div class="snip">
      <textarea readonly id="snip-about">{html.escape(page_embed_snippet("about.html", base))}</textarea>
      <div class="snip-row">
        <button type="button" data-copy="snip-about">копировать сниппет</button>
        <span class="ok" data-ok="snip-about">✓ скопировано</span>
      </div>
    </div>
  </div>
</div>

<h2>Все страницы тортов</h2>
<div class="grid-cakes">
{cake_rows}
</div>

<script>
document.addEventListener('click', function(e){{
  var b = e.target.closest('button[data-copy]');
  if (!b) return;
  var id = b.dataset.copy;
  var ta = document.getElementById(id);
  if (!ta) return;
  ta.select();
  ta.setSelectionRange(0, ta.value.length);
  var ok = false;
  try {{ ok = document.execCommand('copy'); }} catch(_{{}}){{}}
  if (!ok && navigator.clipboard){{
    navigator.clipboard.writeText(ta.value).then(function(){{ flash(id); }});
    return;
  }}
  if (ok) flash(id);
}});
function flash(id){{
  var el = document.querySelector('[data-ok="'+id+'"]');
  if (!el) return;
  el.classList.add('show');
  setTimeout(function(){{ el.classList.remove('show'); }}, 1800);
}}
</script>

</body>
</html>
"""
    (SITE / "preview.html").write_text(html_out, encoding="utf-8")
    print(f"OK: site/preview.html — превью всех {len(oc)} тортов + главные")


def write_unified_catalog_entrypoint(by_id: dict) -> None:
    """Единый адаптивный каталог site/index.html."""
    rows: list[str] = []
    for cid in CATALOG_ORDER:
        c = by_id.get(cid)
        if c is None:
            continue
        nm = html.escape(c["name"])
        cov = html.escape(cover_filename(cid))
        cid_esc = html.escape(cid)
        rows.append(
            f'  <a class="cover" data-cake="{nm}" href="cakes/{cid_esc}.html">'
            f'<img src="photos/{cid_esc}/{cov}" alt="{nm}"   '
            f'onerror="if(!this.dataset.fbk){{this.dataset.fbk=1;'
            f'this.src=this.src.replace(/cover\\.(jpg|jpeg|png|webp)$/i,'
            f"'cover.' + ((RegExp.$1||'jpg').toUpperCase()));}}\">"
            f'<div class="cover-name">{nm}</div></a>'
        )
    grid = "\n".join(rows)
    # SVG-буква К (тот же знак, что в шаблонах)
    k_svg = (
        '<svg viewBox="0 0 54 65" xmlns="http://www.w3.org/2000/svg">'
        '<path d="M21.5183 26.4696C21.6112 26.4696 21.7061 26.4146 21.7357 26.3215C22.5312 23.2215 24.6898 15.7815 26.055 13.0814C27.8169 9.58359 30.7331 4.22365 35.8564 2.85457C44.0267 0.670814 49.705 4.96003 50.952 9.56666C51.9818 13.3692 50.0173 17.6881 47.5295 20.1067C45.0417 22.5317 37.9074 25.8348 32.9023 28.3847C27.397 31.1863 24.8164 29.8786 30.9694 31.4275C38.0108 33.1966 47.3818 32.5998 52.2856 43.9863C53.7437 47.3825 53.9146 52.9371 52.3553 56.4202C49.5087 62.8127 39.4668 67.9759 31.1003 61.45C26.7176 58.0305 24.2931 51.7712 23.4132 45.8018C23.0165 43.1568 22.3286 37.6635 22.1345 36.1611C22.1113 35.9897 21.9467 35.8797 21.7757 35.9114H21.7378C21.5901 35.9432 21.4951 36.0765 21.5035 36.2246C21.7209 38.7512 21.7694 40.262 21.9002 42.3273C22.1429 45.9648 22.6324 49.5811 22.835 53.2186C22.9047 54.5644 22.6557 56.0117 22.2336 57.311C19.8935 64.5881 11.9722 66.2619 6.8025 60.629C3.83149 57.3893 2.10965 53.5085 1.39222 49.2531C-0.93944 35.3951 -0.667231 21.7339 4.72195 8.51076C5.30645 7.06338 5.89095 5.56945 6.81939 4.32521C8.65939 1.87695 11.3266 -0.376626 14.9833 0.0529308C18.5156 0.467676 20.6912 2.71279 21.5099 5.93764C22.0627 8.14468 21.9066 10.5549 21.877 12.8783C21.8538 14.3955 21.4318 24.1293 21.2145 26.2348C21.206 26.3511 21.2841 26.4464 21.3938 26.4527C21.4318 26.4527 21.4803 26.4527 21.5183 26.4612H21.5099L21.5183 26.4696Z"/>'
        '</svg>'
    )
    html_out = f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>kosmos cake — каталог</title>
<link rel="stylesheet" href="style.css">
<style>
  /* Адаптивный единый каталог: 3 колонки → 2 при ширине ≤900px.
     Живой ресайз без перезагрузки страницы. */
  .cover-grid{{grid-template-columns:repeat(3, 1fr);gap:0;padding:0;max-width:100%}}
  @media (max-width:900px){{
    .cover-grid{{grid-template-columns:repeat(2, 1fr)}}
    .cover{{aspect-ratio:1/1.25}}
  }}
</style>
</head>
<body>
<main class="cover-grid">
{grid}
</main>

</body>
</html>
"""
    (SITE / "index.html").write_text(html_out, encoding="utf-8")
    print("OK: site/index.html — адаптивный единый каталог")


def patch_static_page(path: Path, catalog_href: str):
    """Чистит popup-меню на статичных страницах. Идемпотентно."""
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    new = patch_static_page_content(text, catalog_href)
    if new != text:
        path.write_text(new, encoding="utf-8")


def build_calculators() -> None:
    spec = importlib.util.spec_from_file_location("build_cakes_mod", BC)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    mod.main()
    print("OK: calculator/build_cakes.py")


def write_unified_about() -> None:
    """Патчит site/about.html (адаптивный viewport, без popup-меню)."""
    path = SITE / "about.html"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    new = text.replace(
        'content="width=1280"',
        'content="width=device-width, initial-scale=1, viewport-fit=cover"',
    )
    new = patch_static_page_content(new, catalog_href="index.html")
    if new != text:
        path.write_text(new, encoding="utf-8")
    print("OK: site/about.html")


def patch_static_page_content(text: str, catalog_href: str) -> str:
    text = strip_menu_list(text)
    text = convert_menu_btn_to_link(text, href=catalog_href)
    return strip_menu_js(text)


def remove_extra_paths() -> None:
    """Удаляет устаревшие дубли (desktop/mobile, старые калькуляторы, кэш)."""
    for rel in ("desktop", "mobile"):
        p = SITE / rel
        if p.is_dir():
            shutil.rmtree(p)
    for p in (SITE / "__pycache__", CALC / "__pycache__"):
        if p.is_dir():
            shutil.rmtree(p)


def main():
    build_calculators()
    cakes = load_cakes()
    by_id = {c["id"]: c for c in cakes}
    cakes_dir = SITE / "cakes"
    cakes_dir.mkdir(parents=True, exist_ok=True)

    for cake in cakes:
        (cakes_dir / f"{cake['id']}.html").write_text(render_cake_page(cake), encoding="utf-8")

    normalize_cover_filenames([c["id"] for c in cakes])
    remove_extra_paths()

    bust_class_svg_cache()
    bust_calc_asset_cache()
    sync_kosmos_filling_sets()
    write_unified_catalog_entrypoint(by_id)
    write_unified_about()
    write_site_preview_index(cakes, by_id)
    (SITE / "photos raw").mkdir(parents=True, exist_ok=True)

    print(f"OK: {len(cakes)} тортов → site/cakes/")
    print("OK: каталог site/index.html")


if __name__ == "__main__":
    main()
