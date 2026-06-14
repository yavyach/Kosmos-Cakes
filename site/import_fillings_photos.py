# -*- coding: utf-8 -*-
"""Импорт фото начинок: исходники → site/fillings/photos/ (имена как в data.js)."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_DEFAULT = Path.home() / "Downloads" / "Telegram Desktop" / "nachinki11"
OUT = ROOT / "site" / "fillings" / "photos"

# нормализованное имя файла (без пробелов/« 1») → целевое имя в data.js
FILE_TO_PHOTO: dict[str, str] = {
    "апельсинмангомаракуйя": "orangemangomarakua.webp",
    "ванильныйсклубникой": "vanillastrawberry.webp",
    "ванильныйсвишней": "vanillacherry.webp",
    "дорблюгруша-грецкийорех": "dorbluepearwalnut.jpg",
    "кукисэндкрим": "cookiesandcream.webp",
    "маклимон": "poppylemon.webp",
    "морковный": "carrot.webp",
    "сникерс": "sneakers.webp",
    "фисташкамалина": "phistachiorasberry.webp",
    "фисташковыйчизкейк": "phistachiocheesecakes.webp",
    "фундуккофешоколад": "fundukcoffeechocolate.webp",
    "черникашоколад": "chernikachocolate.webp",
    "чизкейкньюйорк": "newyorkcheesecake.webp",
    "чизкейкорео": "oreocheesecake.webp",
    "шоколадкокос": "coconutchoco.webp",
    "шоколадныйсшоколадом": "chocolatechoco.webp",
    "яблочныйсиннабон": "applacinnabon.webp",
}


def norm_name(name: str) -> str:
    stem = Path(name).stem.lower()
    stem = re.sub(r"\s+1$", "", stem)
    return re.sub(r"\s+", "", stem)


def import_photos(src_dir: Path) -> list[str]:
    if not src_dir.is_dir():
        raise SystemExit(f"Папка не найдена: {src_dir}")
    OUT.mkdir(parents=True, exist_ok=True)
    log: list[str] = []
    used_dest: set[str] = set()
    for f in sorted(src_dir.iterdir()):
        if not f.is_file() or f.suffix.lower() not in {".webp", ".jpg", ".jpeg"}:
            continue
        key = norm_name(f.name)
        dest_name = FILE_TO_PHOTO.get(key)
        if not dest_name:
            log.append(f"  SKIP (нет в словаре): {f.name}")
            continue
        if dest_name in used_dest:
            log.append(f"  SKIP (дубликат): {f.name} → {dest_name}")
            continue
        used_dest.add(dest_name)
        shutil.copy2(f, OUT / dest_name)
        log.append(f"  {f.name} -> {dest_name}")
    missing = set(FILE_TO_PHOTO.values()) - used_dest
    for m in sorted(missing):
        log.append(f"  WARN: нет исходника для {m}")
    # отдельный срез «Сникерс» (с заглавной) для особых тортов
    sn = OUT / "сникерс 1.webp"
    if "sneakers.webp" in used_dest and not sn.exists():
        shutil.copy2(OUT / "sneakers.webp", sn)
        log.append("  sneakers.webp -> сникерс 1.webp (копия)")
    return log


if __name__ == "__main__":
    import sys

    src = Path(sys.argv[1]) if len(sys.argv) > 1 else SRC_DEFAULT
    print(f"Импорт из {src}")
    for line in import_photos(src):
        print(line)
    print(f"Готово: {OUT}")
