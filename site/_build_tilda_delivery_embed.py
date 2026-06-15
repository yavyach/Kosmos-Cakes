"""Сборка HTML-блока «Доставка» для вставки в Tilda (карта + адрес + зоны)."""
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

out = SITE / "tilda-delivery-embed.html"
out.write_text(embed, encoding="utf-8")
print(f"Wrote {out.name} ({len(embed)} bytes)")
