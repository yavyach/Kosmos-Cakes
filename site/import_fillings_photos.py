# -*- coding: utf-8 -*-
"""Импорт фото начинок: исходники → site/fillings/photos/ (имена латиницей)."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_DEFAULT = Path.home() / "Downloads" / "Telegram Desktop" / "nachinki11"
OUT = ROOT / "site" / "fillings" / "photos"

# нормализованное имя файла (без пробелов/« 1») → целевое имя webp
FILE_TO_PHOTO: dict[str, str] = {
    "апельсинмангомаракуйя": "apelsin-mango-marakuyya.webp",
    "ванильныйсклубникой": "vanilnyy-s-klubnikoy.webp",
    "ванильныйсвишней": "vanilnyy-s-vishney.webp",
    "дорблюгруша-грецкийорех": "dorblu-grusha-gretskiy-orex.webp",
    "кукисэндкрим": "kukis-end-krim.webp",
    "маклимон": "mak-limon.webp",
    "морковный": "morkovnyy.webp",
    "сникерс": "snikers.webp",
    "фисташкамалина": "fistashka-malina.webp",
    "фисташковыйчизкейк": "fistashkovyy-chizkeyk.webp",
    "фундуккофешоколад": "funduk-kofe-shokolad.webp",
    "черникашоколад": "chernika-shokolad.webp",
    "чизкейкньюйорк": "chizkeyk-nyu-york.webp",
    "чизкейкорео": "chizkeyk-oreo.webp",
    "шоколадкокос": "shokolad-kokos.webp",
    "шоколадныйсшоколадом": "shokoladnyy-s-shokoladom.webp",
    "яблочныйсиннабон": "yablochnyy-sinnabon.webp",
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
        if not f.is_file() or f.suffix.lower() != ".webp":
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
    return log


if __name__ == "__main__":
    import sys

    src = Path(sys.argv[1]) if len(sys.argv) > 1 else SRC_DEFAULT
    print(f"Импорт из {src}")
    for line in import_photos(src):
        print(line)
    print(f"Готово: {OUT}")
