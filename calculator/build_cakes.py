"""
Генерирует отдельный HTML-файл под каждый торт.

Структура на выходе:
  calculator/cakes/
    tiered/<id>.html
    fixed/<id>.html
    weight/<id>.html
    index.html  ← превью всех тортов (inline HTML)

Каждый файл — простая страница, которая:
  1. Подключает ../../style.css и ../../core.js
  2. Вызывает render<Type>Cake({...данные торта...})

Никакого выбора торта внутри: одна страница = один торт.
"""

import sys, io, json, re
from pathlib import Path

ROOT = Path(__file__).parent
OUT  = ROOT / "cakes"

# ----------------------------------------------------------------
#  ВСЕ ТОРТЫ. Описания взяты из «Вся инфа по тортикам.docx».
# ----------------------------------------------------------------
CAKES = [
    # ============ ТИП 1 — ЯРУСНЫЕ ============
    {
        "id":"bell", "type":"tiered", "name":"белль",
        "title":"белль",
        "desc":"Многообразие форм, цветов, размеров и узоров. Вкупе с лентами и вишенками — полная тортовая феерия!",
        "subtitle":"Торт назван в честь принцессы из мультфильма «Красавица и чудовище» компании Дисней.",
        "decorPerTier":3000, "minWeight":6, "minTiers":6, "fillings":"BASE"
    },
    {
        "id":"lumiere", "type":"tiered", "name":"люмьер",
        "title":"люмьер",
        "desc":"Ещё более смелый и фееричный вариант торта Белль. Каждый ярус может быть с разной начинкой.",
        "subtitle":"Торт назван в честь заколдованного персонажа мультфильма «Красавица и чудовище» компании Дисней.",
        "decorPerTier":3000, "minWeight":10, "minTiers":10, "fillings":"PLUS_CHEESECAKE"
    },
    {
        "id":"fairy-cake", "type":"tiered", "name":"fairy cake",
        "title":"fairy cake",
        "desc":"По-настоящему сказочный большой торт, как из мультика. Мечта детства!",
        "subtitle":"Для сохранения сказочного объёма при небольшом весе возможно использование фальш-ярусов.",
        "decorPerTier":3000, "minWeight":4, "minTiers":2, "fillings":"BASE"
    },
    {
        "id":"big-cherry-fairy-cake", "type":"tiered", "name":"big cherry fairy cake",
        "title":"big cherry fairy cake",
        "desc":"Ещё больше усиливаем сказочность фэири кейка большой мультяшной вишней на макушке. Вот это действительно cherry on top!",
        "subtitle":"Внутри вишенки — торт, поэтому она считается отдельным ярусом.",
        "decorPerTier":3000, "minWeight":4, "minTiers":3, "fillings":"BASE"
    },
    {
        "id":"chapito", "type":"tiered", "name":"шапито",
        "title":"шапито",
        "desc":"Нет минимализму! Дофаминовый тортик в цирковом стиле.",
        "subtitle":"Цвет и другие детали могут меняться по вашему желанию.",
        "decorPerTier":3000, "minWeight":6, "minTiers":2, "fillings":"BASE"
    },
    {
        "id":"kuinji", "type":"tiered", "name":"куинджи",
        "title":"куинджи",
        "desc":"Красота живой природы, перенесённая на торт. Узоры, цветы, листья, орнаменты.",
        "subtitle":"Торт назван в честь выдающегося русского художника-пейзажиста. Стоимость декора зависит от сложности росписи.",
        "decorPerTier":3000, "minWeight":1.5, "minTiers":1, "fillings":"BASE",
        "note":"Стоимость декора зависит от сложности — может быть выше."
    },
    {
        "id":"darcy", "type":"tiered", "name":"дарси",
        "title":"дарси",
        "desc":"Монохром, крем — и всё! Базовый, но в то же время породистый торт. Классическая классика.",
        "subtitle":"Торт назван в честь одного из главных героев романа Джейн Остин «Гордость и предубеждение».",
        "decorPerTier":3000, "minWeight":1.5, "minTiers":1, "fillings":"BASE"
    },
    {
        "id":"shine-bright", "type":"tiered", "name":"shine bright",
        "title":"shine bright",
        "desc":"Торт для тех, кто хочет сиять! Покрытие может быть серебряным, золотым или перламутровым.",
        "subtitle":"Название торта вдохновлено строчкой из песни Рианны Diamonds.",
        "decorPerTier":3500, "minWeight":1.5, "minTiers":1, "fillings":"BASE"
    },
    {
        "id":"kelly", "type":"tiered", "name":"келли",
        "title":"келли",
        "desc":"Ярусный торт может быть плоским и выглядеть эстетично и аккуратно! Утончённый декор и игра с цветом.",
        "subtitle":"Торт назван в честь иконы Голливуда Грейс Келли.",
        "decorPerTier":2000, "minWeight":4, "minTiers":2, "fillings":"TYPE3_LOVE"
    },
    {
        "id":"elizabeth", "type":"tiered", "name":"элизабет",
        "title":"элизабет",
        "desc":"Классическая классика! Но в отличии от «Дарси» более нарядный: ягоды, ленты, цветочки, бусины и многое другое!",
        "subtitle":"Торт назван в честь главной героини романа Джейн Остин «Гордость и предубеждение».",
        "decorPerTier":3000, "minWeight":1.5, "minTiers":1, "fillings":"BASE"
    },
     {
        "id":"fuji", "type":"tiered", "name":"fuji",
        "title":"fuji",
        "desc":"Объёмная шапка из крема, цветные полоски, бантики, ягоды. Азиатский стиль!",
        "subtitle":"Торт назван в честь главного символа Японии.",
        "decorPerTier":3500, "minWeight":1.5, "minTiers":1, "fillings":"BASE"
    },
    # ============ ТИП 2 — ФИКС. ВЕС ============
    {
        "id":"faberge", "type":"fixed", "name":"фаберже",
        "title":"фаберже",
        "desc":"По-императорски величественный и роскошный торт с вензелями, рюшами и лепниной.",
        "subtitle":"Торт назван в честь знаменитых ювелирных изделий Российского Императорского Дома, ставших символом роскоши и богатства.",
        "decor":{"2.5":3000, "3.5":3500}, "fillings":"BASE"
    },
    {
        "id":"secret-garden", "type":"fixed", "name":"secret garden",
        "title":"secret garden",
        "desc":"Минималистично, необычно, аутентично. Цветы могут быть любые, главное — единая композиция!",
        "subtitle":"Торт назван в честь романа Фрэнсис Бёрнетт о надежде и исцелении.",
        "decor":{"2.5":3500, "3.5":4000}, "fillings":"BASE"
    },
    {
        "id":"blueberry-hill", "type":"fixed", "name":"blueberry hill",
        "title":"blueberry hill",
        "desc":"Тот случай, когда ягода — центральный (и единственный) элемент декора. Торт на 100% покрыт ягодами!",
        "subtitle":"Торт назван в честь классического хита Фэтса Домино.",
        "decor":{"2.5":5500, "3.5":6500}, "fillings":"BASE"
    },
    {
        "id":"la-la-land", "type":"fixed", "name":"la la land",
        "title":"la la land",
        "desc":"Изящные, необычные кремовые узоры, ягоды и ленты. Отличный вариант для небольшого дня рождения!",
        "subtitle":"Торт назван в честь оскароносного мюзикла о несбывшейся любви.",
        "decor":{"2.5":3000, "3.5":3500}, "fillings":"BASE"
    },

    # ============ ТИП 3 — ПЛОСКИЙ ПО ВЕСУ ============
    {
        "id":"bohemian-rhapsody", "type":"weight", "name":"богемская рапсодия",
        "title":"богемская рапсодия",
        "desc":"Кремовые рюши, роскошный декор и элегантные сахарные фрукты. Настоящее тортовое барокко!",
        "subtitle":"Торт назван в честь вечного хита группы Queen.",
        "decorTable":[(4,8.5,4500),(9,20,6500)],
        "minWeight":4, "maxWeight":20, "fillings":"BASE"
    },
    {
        "id":"babylon", "type":"weight", "name":"вавилон",
        "title":"вавилон",
        "desc":"Высокий, грациозный, впечатляющий торт. Возможен только лёгкий кремовый декор или банты.",
        "subtitle":"Название торта вдохновлено древним мифом о попытке людей построить высочайшую башню и добраться до небес.",
        "decorTable":[(10,14.5,10000),(15,18.5,15000),(19,30,18500)],
        "minWeight":10, "maxWeight":30, "fillings":"NO_SNICKERS_NO_DORBLU"
    },
    {
        "id":"swan-lake", "type":"weight", "name":"лебединое озеро",
        "title":"лебединое озеро",
        "desc":"Утончённый и глубокий, как русское искусство 19 века. Кремовые цветы, миндальные лепестки, лебеди из безе.",
        "subtitle":"Торт назван в честь покорившего весь мир балета Петра Ильича Чайковского.",
        "decorTable":[(2,20,2500)],
        "minWeight":2, "maxWeight":20, "fillings":"PLUS_CHERNIKA"
    },
    {
        "id":"green-day", "type":"weight", "name":"green day",
        "title":"green day",
        "desc":"Азиатский стиль, вписанный в современный праздничный торт. Виноград сорта шайн мускат дополняет почти любую начинку.",
        "subtitle":"Торт назван в честь культовой американской панк-рок группы.",
        "decorTable":[(3,9.5,4500),(10,20,6500)],
        "minWeight":3, "maxWeight":20, "fillings":"PLUS_CHEESECAKE"
    },
    {
        "id":"cherry-orchard", "type":"weight", "name":"вишневый сад",
        "title":"вишневый сад",
        "desc":"Эффектный торт с поляной из черешни и эстетичными кремовыми рюшами.",
        "subtitle":"Торт назван в честь пьесы Антона Павловича Чехова об уходящей эпохе и неизбежности перемен.",
        "decorTable":[(4,7.5,5500),(8,12,8000),(12.5,20,12500)],
        "minWeight":4, "maxWeight":20, "fillings":"BASE"
    },
    {
        "id":"love-in-mood", "type":"weight", "name":"любовное настроение",
        "title":"любовное настроение",
        "desc":"Любовь — лучшее, что случалось с этим миром! Поэтому и сердце должно быть большим. Классический вариант для свадьбы.",
        "subtitle":"Торт назван в честь культовой мелодрамы Вонга Карвая.",
        "decorTable":[(3,6.5,3500),(7,12,5000),(12.5,20,6500)],
        "minWeight":3, "maxWeight":20, "fillings":"TYPE3_LOVE"
    },
    {
        "id":"anna", "type":"weight", "name":"анна",
        "title":"анна",
        "desc":"Аристократичный эффектный торт с рюшами, лентами и большим количеством свежих ягод или фруктов.",
        "subtitle":"Торт назван в честь главной героини романа Льва Толстого «Анна Каренина».",
        "decorTable":[(4,7.5,6000),(8,12,10000),(12.5,20,16000)],
        "minWeight":4, "maxWeight":20, "fillings":"BASE"
    },
    {
        "id":"berry-fields", "type":"weight", "name":"ягодные поля навсегда",
        "title":"ягодные поля",
        "desc":"Свежая сочная ягода — чем не идеальное дополнение к торту? Особенно когда её ТАК много!",
        "subtitle":"Название вдохновлено знаковой песней группы the Beatles.",
        "decorTable":[
            (2,2,3000),(2.5,3,5500),(3.5,4,6000),(4.5,5,7000),
            (5.5,6,8000),(6.5,7,9000),(7.5,8,10000),(8.5,9,11000),
            (9.5,10,12000),(10.5,11,13000),(11.5,12,14000),(12.5,13,15000),
            (13.5,14,16000),(14.5,15,17000),(15.5,16,18000),(16.5,17,19000),
            (17.5,18,20000),(18.5,19,22000),(19.5,20,24000)
        ],
        "minWeight":2, "maxWeight":20, "fillings":"PLUS_CHEESECAKE"
    },
    {
        "id":"letter", "type":"weight", "name":"вам письмо",
        "title":"вам письмо",
        "desc":"Послание во вселенную прямо на торте! Лучше лаконично и ёмко.",
        "subtitle":"Торт назван в честь культового ромкома 90-х.",
        "decorTable":[(4,7.5,3000),(8,12,4500),(12.5,20,5000)],
        "minWeight":4, "maxWeight":20, "fillings":"BASE"
    },
    {
        "id":"orpheus", "type":"weight", "name":"орфей",
        "title":"орфей",
        "desc":"Классического вида, но необычный своей вытянутостью торт. Может быть только длинным, низким и/или узким.",
        "subtitle":"Торт назван в честь божественного музыканта, героя древнегреческой мифологии, сына Аполлона.",
        "decorTable":[(4,7.5,3500),(8,12.5,5000),(13,20,6500)],
        "minWeight":4, "maxWeight":20, "fillings":"PLUS_CHERNIKA"
    },
    {
        "id":"apollo", "type":"weight", "name":"аполлон",
        "title":"аполлон",
        "desc":"Величественный и изящный прямоугольный торт. В отличие от «орфея» более широкий и классический.",
        "subtitle":"Торт назван в честь древнегреческого бога света, покровителя муз и искусств, отца Орфея.",
        "decorTable":[(4,6.5,4000),(7,12,6000),(12.5,20,7500)],
        "minWeight":4, "maxWeight":20, "fillings":"PLUS_CHERNIKA"
    },
    {
        "id":"sailor-moon", "type":"weight", "name":"sailor moon",
        "title":"sailor moon",
        "desc":"Яркий и смелый, с множеством деталей и форм. Может быть в виде сердца, но не обязательно.",
        "subtitle":"Торт назван в честь культового аниме-сериала. Только 1 ярус!",
        "decorTable":[(1.5,3.5,3000),(4,5.5,3500),(6,7,5500)],
        "minWeight":1.5, "maxWeight":7, "fillings":"PLUS_CHEESECAKE"
    },
    {
        "id":"dancing-queen", "type":"weight", "name":"dancing queen",
        "title":"dancing queen",
        "desc":"Нестандартная форма и изящные кремовые изгибы. Это смотрится мило и благородно одновременно!",
        "subtitle":"Торт назван в честь великого поп-хита группы ABBA. Декор выполнен из шоколадного крема.",
        "decorTable":[(2,4.5,4000),(5,20,6500)],
        "minWeight":2, "maxWeight":20, "fillings":"BASE"
    },
    {
        "id":"totoro", "type":"weight", "name":"тоторо",
        "title":"тоторо",
        "desc":"Торт не всегда должен быть эффектным или эстетичным, иногда он может быть просто милым или забавным.",
        "subtitle":"Торт назван в честь героя анимационного фильма Хаяо Миядзаки о дружбе и доброте.",
        "decorTable":[(1.5,2.5,2500),(3,5,3500)],
        "minWeight":1.5, "maxWeight":5, "fillings":"PLUS_CHEESECAKE"
    },
   
    {
        "id":"tiramisu", "type":"weight", "name":"тирамису",
        "title":"тирамису",
        "desc":"Mama mia, dolce vita, bellissimo! Настоящий итальянский тирамису.",
        "subtitle":"Может быть круглым или длинным. Эффектно смотрится в большой ширине. Только начинка тирамису.",
        "decorTable":[(1,10,0)],
        "minWeight":1, "maxWeight":10, "fillings":"TIRAMISU"
    },
]

# ----------------------------------------------------------------
#  INLINE HTML (без iframe)
# ----------------------------------------------------------------
GITHUB_CALC = "https://ab-aacoop.github.io/kosmos_calc/calculator"


def cake_render_js(cake: dict) -> tuple[str, str]:
    """(имя render-функции, тело объекта для вызова)."""
    fillings = f"FILLING_SETS.{cake['fillings']}"
    if cake["type"] == "tiered":
        data = {
            "id": cake["id"],
            "name": cake["name"],
            "title": cake["title"],
            "desc": cake["desc"],
            "subtitle": cake.get("subtitle", ""),
            "decorPerTier": cake["decorPerTier"],
            "minWeight": cake["minWeight"],
            "minTiers": cake["minTiers"],
        }
        if "note" in cake:
            data["note"] = cake["note"]
        render = "renderTieredCake"
    elif cake["type"] == "fixed":
        data = {
            "id": cake["id"],
            "name": cake["name"],
            "title": cake["title"],
            "desc": cake["desc"],
            "subtitle": cake.get("subtitle", ""),
            "decor": {2.5: cake["decor"]["2.5"], 3.5: cake["decor"]["3.5"]},
        }
        render = "renderFixedCake"
    else:
        data = {
            "id": cake["id"],
            "name": cake["name"],
            "title": cake["title"],
            "desc": cake["desc"],
            "subtitle": cake.get("subtitle", ""),
            "decorTable": [
                {"min": r[0], "max": r[1], "price": r[2]} for r in cake["decorTable"]
            ],
            "minWeight": cake["minWeight"],
            "maxWeight": cake["maxWeight"],
        }
        render = "renderWeightCake"
    data["mobile"] = True
    data_json = json.dumps(data, ensure_ascii=False, indent=2)
    data_js = data_json.rstrip().rstrip("}").rstrip() + ',\n  "fillings": ' + fillings + "\n}"
    return render, data_js


def _v(q: str, ver: str) -> str:
    return f"{q}?v={ver}" if ver else q


def calc_inline_block(
    cake: dict,
    *,
    calc_prefix: str = "../../calculator",
    css_v: str = "",
    js_v: str = "",
    with_stylesheet: bool = False,
) -> str:
    """Готовый HTML калькулятора для вставки в Tilda / на страницу торта."""
    render, data_js = cake_render_js(cake)
    css = _v(f"{calc_prefix}/style.css", css_v)
    js = _v(f"{calc_prefix}/core.js", js_v)
    link = f'<link rel="stylesheet" href="{css}">\n' if with_stylesheet else ""
    return (
        f"{link}<div class=\"calc-frame\">\n"
        f"  <div class=\"calc-scroll\" id=\"root\"></div>\n"
        f"</div>\n"
        f'<script src="{js}"></script>\n'
        f"<script>\n{render}({data_js});\n</script>"
    )


def delivery_inline_block(
    *,
    dlv_prefix: str = "../../calculator/delivery",
    css_v: str = "",
    js_v: str = "",
    root_id: str = "dlv-root",
    with_stylesheet: bool = False,
) -> str:
    css = _v(f"{dlv_prefix}/delivery.css", css_v)
    js = _v(f"{dlv_prefix}/delivery.js", js_v)
    link = f'<link rel="stylesheet" href="{css}">\n' if with_stylesheet else ""
    return (
        f"{link}<div class=\"delivery-inline\" id=\"{root_id}\"></div>\n"
        f'<script src="{js}"></script>\n'
        f"<script>Kosmos.mountDelivery(document.getElementById('{root_id}'));</script>"
    )


def calc_embed_snippet(cake: dict, css_v: str = "", js_v: str = "") -> str:
    """Сниппет калькулятора с абсолютными URL (GitHub Pages)."""
    return calc_inline_block(
        cake,
        calc_prefix=GITHUB_CALC,
        css_v=css_v,
        js_v=js_v,
        with_stylesheet=True,
    )


def delivery_embed_snippet(css_v: str = "", js_v: str = "") -> str:
    return delivery_inline_block(
        dlv_prefix=f"{GITHUB_CALC}/delivery",
        css_v=css_v,
        js_v=js_v,
        root_id="dlv-root",
        with_stylesheet=True,
    )


# ----------------------------------------------------------------
#  ШАБЛОН СТРАНИЦЫ ТОРТА
# ----------------------------------------------------------------
def cake_template(cake):
    """Отдельная страница-калькулятор (inline HTML, без iframe)."""
    block = calc_inline_block(cake, calc_prefix="../..", with_stylesheet=False)
    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{cake['name']} — калькулятор</title>
<link rel="stylesheet" href="../../style.css">
</head>
<body class="mobile">
{block}
</body>
</html>
"""

# ----------------------------------------------------------------
#  ПРЕВЬЮ-СТРАНИЦА
# ----------------------------------------------------------------
BASE_URL = 'https://ab-aacoop.github.io/kosmos_calc/calculator/cakes'

def _asset_versions():
    css = ROOT / "style.css"
    js = ROOT / "core.js"
    return (
        str(int(css.stat().st_mtime)) if css.exists() else "",
        str(int(js.stat().st_mtime)) if js.exists() else "",
    )


def preview_page(cakes):
    aspect = '380/760'
    css_v, js_v = _asset_versions()
    h1 = 'Все торты — калькуляторы (адаптивные)'
    lead = (
        'Каждая карточка — inline HTML для вставки в Readymag/Tilda (без iframe). '
        'Страницы тортов: <a href="../../site/cakes/">site/cakes</a>. '
        'Блок доставки: <a href="../delivery/preview.html">delivery</a>.'
    )
    title = 'Kosmos — все калькуляторы'

    cards = []
    for i, c in enumerate(cakes):
        path = f"{c['type']}/{c['id']}.html"
        snippet = calc_embed_snippet(c, css_v, js_v)
        sid = f"snip{i}"
        esc_snip = snippet.replace("&", "&amp;").replace("<", "&lt;")
        cards.append(f"""
    <div class="card">
      <header>
        <span class="type">{c['type']}</span>
        <span class="name">{c['name']}</span>
        <a class="open" href="{path}" target="_blank" title="открыть в новой вкладке">↗</a>
      </header>
      <div class="frame-wrap"><object data="{path}" type="text/html" title="{c['name']}"></object></div>
      <div class="snip">
        <textarea readonly id="{sid}">{esc_snip}</textarea>
        <div class="snip-row">
          <button type="button" data-copy="{sid}">копировать сниппет</button>
          <span class="ok" data-ok="{sid}">✓ скопировано</span>
        </div>
      </div>
    </div>""")

    delivery_test_link = '../delivery/preview.html'
    other_links = '<a href="../../site/cakes/">↗ страницы тортов</a>'

    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  *{{box-sizing:border-box}}
  html,body{{margin:0;padding:0;background:#eaeaea;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:#222}}
  body{{padding:24px}}
  h1{{margin:0 0 6px;font-size:22px}}
  p.lead{{margin:0 0 14px;color:#555;font-size:14px;max-width:760px}}
  p.lead a{{color:#d83448}}
  .topbar{{display:flex;gap:10px;flex-wrap:wrap;margin:0 0 18px}}
  .topbar a{{
    text-decoration:none;background:#fff;border:1px solid #ddd;padding:7px 12px;
    border-radius:6px;color:#222;font-size:13px;font-weight:500;
  }}
  .topbar a.primary{{background:#d83448;color:#fff;border-color:#d83448}}
  .topbar a:hover{{filter:brightness(0.95)}}
  .grid{{display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));align-items:start}}
  .card{{display:flex;flex-direction:column;background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,.08)}}
  .card header{{padding:8px 14px;border-bottom:1px solid #eee;display:flex;align-items:center;gap:10px;font-size:12px}}
  .card .type{{padding:2px 8px;background:#d83448;color:#fff;border-radius:999px;font-size:10px;text-transform:uppercase;letter-spacing:.3px}}
  .card .name{{font-weight:600;flex:1}}
  .card a.open{{color:#999;text-decoration:none;font-size:14px}}
  .card a.open:hover{{color:#d83448}}
  .frame-wrap{{aspect-ratio:{aspect};width:100%;background:#cfcfcf}}
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
<h1>{h1}</h1>
<p class="lead">{lead}</p>
<div class="topbar">
  <a class="primary" href="{delivery_test_link}">↗ блок доставки (превью + сниппеты)</a>
  {other_links}
  <a href="../">↗ на главную</a>
</div>
<div class="grid">
{''.join(cards)}
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
  try {{ ok = document.execCommand('copy'); }} catch(_){{}}
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

# ----------------------------------------------------------------
#  ГЕНЕРАЦИЯ
# ----------------------------------------------------------------
import shutil

def build_into(target_dir):
    if target_dir.exists():
        shutil.rmtree(target_dir)
    target_dir.mkdir(parents=True)
    for t in ('tiered', 'fixed', 'weight'):
        (target_dir / t).mkdir()
    generated = []
    for cake in CAKES:
        path = target_dir / cake['type'] / f"{cake['id']}.html"
        path.write_text(cake_template(cake), encoding='utf-8')
        generated.append(path.relative_to(target_dir))
    (target_dir / "index.html").write_text(preview_page(CAKES), encoding='utf-8')
    return generated


def remove_legacy_calc_dirs() -> None:
    for name in ("cakes-mobile", "cakes-mobile-full"):
        d = ROOT / name
        if d.is_dir():
            shutil.rmtree(d)


def main():
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    remove_legacy_calc_dirs()
    cake_files = build_into(OUT)
    print(f"Калькуляторы ({OUT.name}/): {len(cake_files)} файлов")
    print(f"Превью: {(OUT / 'index.html').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
