"""Сборка блока «Доставка» для Tilda и отдельной страницы site/delivery.html."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = Path(__file__).resolve().parent

PUBLIC_CALC = "https://yavyach.github.io/Kosmos-Cakes/calculator"


def _v(path: str, ver: str) -> str:
    return f"{path}?v={ver}" if ver else path


def _mtime(rel: str) -> str:
    p = ROOT / rel
    return str(int(p.stat().st_mtime)) if p.exists() else ""


css_v = _mtime("calculator/style.css")
js_v = _mtime("calculator/delivery/delivery.js")
dlv = f"{PUBLIC_CALC}/delivery"

embed = (
    f'<link rel="stylesheet" href="{_v(f"{PUBLIC_CALC}/style.css", css_v)}">\n'
    f'<link rel="stylesheet" href="{_v(f"{dlv}/delivery.css", css_v)}">\n'
    "<style>"
    ".kosmos-delivery-embed{display:block;width:100%;max-width:100%;"
    "background:var(--bg,#cfcfcf);box-sizing:border-box;overflow-x:hidden;}"
    ".kosmos-delivery-embed .delivery-inline{width:100%;}"
    "</style>\n"
    '<div class="kosmos-delivery-embed">\n'
    '<div class="delivery-inline" id="dlv-tilda"></div>\n'
    f'<script src="{_v(f"{dlv}/zones-config.js", js_v)}"></script>\n'
    f'<script src="{_v(f"{dlv}/kosmos-dots.js", js_v)}"></script>\n'
    f'<script src="{_v(f"{dlv}/delivery.js", js_v)}"></script>\n'
    "<script>Kosmos.mountDelivery(document.getElementById('dlv-tilda'));</script>\n"
    "</div>\n"
)

page = f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Доставка — kosmos</title>
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{_v("../calculator/style.css", css_v)}">
<link rel="stylesheet" href="{_v("../calculator/delivery/delivery.css", css_v)}">
</head>
<body style="margin:0;background:var(--bg,#cfcfcf)">
<div class="delivery-inline" id="dlv-root"></div>
<script src="{_v("../calculator/delivery/zones-config.js", js_v)}"></script>
<script src="{_v("../calculator/delivery/kosmos-dots.js", js_v)}"></script>
<script src="{_v("../calculator/delivery/delivery.js", js_v)}"></script>
<script>Kosmos.mountDelivery(document.getElementById('dlv-root'));</script>
</body>
</html>
"""

(SITE / "tilda-delivery-embed.html").write_text(embed, encoding="utf-8")
(SITE / "delivery.html").write_text(page, encoding="utf-8")

iframe = (
    '<iframe src="https://yavyach.github.io/Kosmos-Cakes/site/delivery.html" '
    'title="доставка kosmos" style="display:block;width:100%;border:0;'
    'min-height:min(1200px, 95vh);background:var(--bg,#cfcfcf)"></iframe>\n'
)
(SITE / "tilda-delivery-iframe.html").write_text(iframe, encoding="utf-8")
print(f"Wrote tilda-delivery-embed.html ({len(embed)} bytes)")
print(f"Wrote delivery.html ({len(page)} bytes)")
print(f"Wrote tilda-delivery-iframe.html ({len(iframe)} bytes)")
