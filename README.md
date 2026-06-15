# Kosmos Cakes — калькулятор и сайт

Репозиторий содержит **калькуляторы тортов** (для встраивания) и **адаптивный сайт-каталог** с карточками тортов, начинками и блоком доставки.

Локально проект обычно открывается через OSPanel: `http://kosmoscakes.local/site/`

На GitHub Pages: `https://yavyach.github.io/Kosmos-Cakes/site/`

---

## Структура проекта

```
kosmoscakes.local/
├── build.py                    # главная команда сборки (запускать отсюда)
├── push.bat                    # быстрый git commit + push (Windows)
├── index.html                  # редирект в calculator/
│
├── calculator/                 # логика калькуляторов
│   ├── build_cakes.py          # ★ данные всех тортов + генерация calculator/cakes/
│   ├── core.js                 # ★ движок калькулятора (вес, ярусы, цена, начинки)
│   ├── style.css               # стили калькулятора
│   ├── cakes/                  # отдельные HTML только с калькулятором (для встраивания)
│   │   ├── tiered/             # ярусные торты
│   │   ├── fixed/              # фиксированный вес (2,5 / 3,5 кг)
│   │   ├── weight/             # торты с выбором веса
│   │   └── index.html          # превью всех калькуляторов
│   ├── delivery/               # блок «Доставка» (карта, зоны, адрес)
│   │   ├── delivery.js
│   │   ├── delivery.css
│   │   └── preview.html        # превью и сниппеты для вёрстки
│   └── build_iframe_table.py   # утилита: xlsx → inline HTML для Redimag
│
└── site/                       # публичный сайт
    ├── build_site_pages.py     # ★ сборка site/cakes/, каталога, preview
    ├── index.html              # каталог (сетка обложек)
    ├── about.html              # страница «о нас»
    ├── preview.html            # превью всех страниц + сниппеты для Tilda
    ├── style.css               # стили сайта
    ├── cake-page.js            # общая логика карточки (карусели, начинки, доставка)
    ├── cake-page-layout.css    # вёрстка узкой колонки (901–1280 px)
    ├── templates/              # ★ шаблоны карточки торта (редактировать здесь)
    │   ├── cake-page-prefix.html   # <head>, стили, кнопка «назад»
    │   ├── cake-card-body.html     # три колонки (фото, инфо, начинки)
    │   ├── cake-page-mid.html      # панель доставки
    │   ├── cake-page-suffix.html   # скрипты
    │   └── cake-fill-head.html     # заголовок «Что внутри?»
    ├── cakes/                  # ★ готовые страницы тортов (генерируются, не править вручную)
    ├── fillings/
    │   └── data.js             # описания начинок (синхрон с core.js при сборке)
    ├── photos/                 # фото тортов (по папке на торт)
    ├── photos raw/             # исходники для импорта
    ├── assets/                 # SVG сайта (логотипы, вишенка, классы начинок)
    └── import_photos_raw.py    # импорт фото из photos raw/
```

---

## Быстрый старт

### Требования

- Python 3.10+
- Локальный веб-сервер (OSPanel, `python -m http.server`, GitHub Pages)

> Страницы нужно открывать по **http://**, не как `file://` — иначе не подгрузятся скрипты и карта.

### Сборка всего проекта

Из корня репозитория:

```bash
python build.py
```

То же самое, если запускать напрямую:

```bash
python site/build_site_pages.py
```

Сборка делает:

1. `calculator/build_cakes.py` → 30 HTML в `calculator/cakes/`
2. `site/build_site_pages.py` → 30 страниц в `site/cakes/`, каталог `site/index.html`, `site/preview.html`
3. синхронизацию наборов начинок в `site/fillings/data.js`
4. обновление cache-bust (`?v=...`) у CSS/JS

---

## Что править и куда

| Задача | Где менять | После правки |
|--------|-----------|--------------|
| Тексты, цены, вес, тип торта | `calculator/build_cakes.py` → массив `CAKES` | `python build.py` |
| Логика калькулятора (шаги, формулы) | `calculator/core.js` | `python build.py` |
| Внешний вид калькулятора | `calculator/style.css` | `python build.py` |
| Доставка (карта, зоны, адрес) | `calculator/delivery/delivery.js`, `delivery.css` | `python build.py` |
| Шапка / футер / скрипты карточки | `site/templates/cake-page-*.html` | `python build.py` |
| Карусели, пузыри начинок | `site/cake-page.js` | `python build.py` |
| Стили сайта и каталога | `site/style.css` | `python build.py` |
| Описания начинок | `calculator/core.js` (`_BASE`, …) | `python build.py` (синхрон в `fillings/data.js`) |
| Фото торта | `site/photos/<id>/` или импорт из `photos raw/` | см. ниже |
| Порядок в каталоге | `site/build_site_pages.py` → `CATALOG_ORDER` | `python build.py` |

### ⚠️ Не редактировать вручную (генерируется, в git не хранится)

- `site/cakes/*.html` — из шаблонов и данных
- `site/index.html`, `site/preview.html`, `site/catalog-init.js`
- `site/tilda-embed.html` — для Tilda (`python build.py`)
- `calculator/cakes/**/*.html` — из `build_cakes.py`

После `git clone` запусти `python build.py` для локальной работы.

### Деплой на GitHub

1. Один раз в **Settings → Pages → Build and deployment → Source: GitHub Actions**.
2. `push.bat` (сборка локально только для проверки; на Pages собирает CI) или `git push`.
3. Workflow `.github/workflows/pages.yml` запускает `python build.py` и выкладывает сайт.

---

## Типичные сценарии

### Изменить описание или цену торта

1. Открыть `calculator/build_cakes.py`, найти торт по `"id"`.
2. Поменять `desc`, `subtitle`, `decorTable`, `decorPerTier` и т.д.
3. Запустить `python build.py`.
4. Обновить страницу в браузере (Ctrl+Shift+R).

### Добавить / заменить фото

**Вариант А — вручную:** положить файлы в `site/photos/<id>/` (`cover.webp`, `1.webp`, …).

**Вариант Б — импорт:**

```bash
# положить исходники в site/photos raw/<id>/
python site/import_photos_raw.py
python build.py
```

### Поменять общую вёрстку всех карточек

Редактировать файлы в `site/templates/`, затем `python build.py`.

Сборщик склеивает:

```
prefix + card-body (с данными торта) + mid + suffix  →  site/cakes/<id>.html
```

### Только калькулятор без сайта

```bash
python calculator/build_cakes.py
```

Открыть: `calculator/cakes/index.html`

---

## Вспомогательные скрипты

| Скрипт | Назначение |
|--------|------------|
| `build.py` | полная сборка |
| `site/build_site_pages.py` | только сайт + калькуляторы |
| `calculator/build_cakes.py` | только HTML калькуляторов |
| `site/import_photos_raw.py` | импорт фото из `photos raw/` |
| `calculator/build_iframe_table.py` | Excel с inline-HTML (нужен `openpyxl`, файл `tortonachinki.xlsx` рядом с репо) |

---

## Два «мира» калькулятора

1. **`calculator/cakes/`** — голый калькулятор на одной странице. Удобно встраивать в Tilda / Redimag.
2. **`site/cakes/`** — полная карточка: фото, текст, калькулятор, начинки, доставка. Десктоп + мобилка в одном HTML.

Данные для обоих берутся из одного источника: **`calculator/build_cakes.py`**.

---

## Превью и сниппеты

- `site/preview.html` — все торты в iframe + textarea с HTML для вставки
- `calculator/delivery/preview.html` — блок доставки отдельно
- `calculator/cakes/index.html` — список калькуляторов

---

## Локальная разработка (OSPanel)

Корень домена должен указывать на папку проекта. Сайт: `/site/index.html`, карточка: `/site/cakes/letter.html`.

---

## Заметки

- `calculator/delivery/zones-data.js` — координаты зон доставки; на страницах сайта не подключается (зоны уже встроены в `delivery.js`). Файл оставлен для `delivery/preview.html` и ручного редактирования.
- `site/assets/class-*.svg` — иконки классов начинок в пузырьках на карточке торта (отдельно от одноимённых файлов в `calculator/assets/`).
