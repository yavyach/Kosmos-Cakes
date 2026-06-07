# -*- coding: utf-8 -*-
"""
Кладите исходники в папку «photos raw» рядом с site (внутри репозитория):

  site/photos raw/<id торта>/*.jpg

Поддерживаемые имена внутри папки торта:
  - cover.jpg | cover.png | cover.jpeg | cover.webp  → site/photos/<id>/cover.jpg
  - slice-1.jpg, slice-2.png, …                        → site/photos/<id>/slice-N.jpg

Если нет файла cover.* — первый по алфавиту снимок станет обложкой (копируется как cover.jpg),
остальные по порядку — slice-1, slice-2, slice-3 (максимум три среза после обложки).

Запуск (из корня kosmos_calc):
  python site/import_photos_raw.py
  python site/import_photos_raw.py "D:\\полный\\путь\\к\\photos raw"

После импорта пересоберите страницы тортов:
  python site/build_site_pages.py
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
DEFAULT_RAW = SITE / "photos raw"
OUT = SITE / "photos"
EXT = {".jpg", ".jpeg", ".png", ".webp"}


def cake_ids() -> set[str]:
    bc = (ROOT / "calculator" / "build_cakes.py").read_text(encoding="utf-8")
    cut = bc.index("#  ГЕНЕРАЦИЯ")
    ns: dict = {"__file__": str(ROOT / "calculator" / "build_cakes.py"), "__name__": "x"}
    exec(compile(bc[:cut], "build_cakes.py", "exec"), ns)
    return {c["id"] for c in ns["CAKES"]}


def normalize_to_jpg(src: Path, dst: Path) -> None:
    """Копирует файл; для .jpg/.jpeg просто копия, для png/webp — копия с расширением .jpg (без перекодирования)."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.suffix.lower() in (".jpg", ".jpeg"):
        shutil.copy2(src, dst)
    else:
        # сохраняем байты под именем .jpg (браузер откроет png с неверным расширением — лучше конвертировать вручную при необходимости)
        shutil.copy2(src, dst)


def import_one_cake(raw_dir: Path, cake_id: str) -> list[str]:
    files = [p for p in raw_dir.iterdir() if p.is_file() and p.suffix.lower() in EXT]
    if not files:
        return []
    log: list[str] = []
    out_dir = OUT / cake_id
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    by_lower = {p.name.lower(): p for p in files}
    cover_src = None
    for key in ("cover.jpg", "cover.jpeg", "cover.png", "cover.webp"):
        if key in by_lower:
            cover_src = by_lower[key]
            break

    others = [p for p in files if p is not cover_src]
    others_sorted = sorted(others, key=lambda x: x.name.lower())
    if cover_src is None and others_sorted:
        cover_src = others_sorted.pop(0)

    if cover_src:
        normalize_to_jpg(cover_src, out_dir / "cover.jpg")
        log.append(f"  {cake_id}: cover ← {cover_src.name}")

    # явные slice-N.*
    slice_explicit: list[tuple[int, Path]] = []
    for p in others_sorted:
        m = re.match(r"slice-(\d+)\.", p.name, re.I)
        if m:
            slice_explicit.append((int(m.group(1)), p))

    if slice_explicit:
        slice_explicit.sort(key=lambda t: t[0])
        for n, p in slice_explicit:
            normalize_to_jpg(p, out_dir / f"slice-{n}.jpg")
            log.append(f"  {cake_id}: slice-{n} ← {p.name}")
    else:
        for i, p in enumerate(others_sorted[:3], start=1):
            normalize_to_jpg(p, out_dir / f"slice-{i}.jpg")
            log.append(f"  {cake_id}: slice-{i} ← {p.name}")
    return log


def main():
    raw_root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_RAW
    if not raw_root.is_dir():
        print(f"Нет папки: {raw_root}")
        print("Создайте её и положите подпапки по id торта (как в build_cakes.py), например:")
        print(f"  {DEFAULT_RAW / 'fairy-cake'}\\cover.jpg")
        DEFAULT_RAW.mkdir(parents=True, exist_ok=True)
        print(f"Создана пустая папка: {DEFAULT_RAW}")
        return 1

    ids = cake_ids()
    all_log: list[str] = []
    for sub in sorted(raw_root.iterdir(), key=lambda p: p.name.lower()):
        if not sub.is_dir():
            continue
        cid = sub.name.strip()
        if cid not in ids:
            print(f"Пропуск (неизвестный id торта): {cid}")
            continue
        all_log.extend(import_one_cake(sub, cid))

    if not all_log:
        print("Не найдено подпапок с id тортов или в них нет изображений.")
        return 1
    print("Импорт:\n" + "\n".join(all_log))
    print(f"\nГотово → {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
