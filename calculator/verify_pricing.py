#!/usr/bin/env python3
"""Сверка параметров калькуляции с docx (pricing_raw) и smoke-тест формул."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from build_cakes import CAKES  # noqa: E402

DOCX = json.loads((ROOT / "_cakes_from_docx.json").read_text(encoding="utf-8"))
DOCX_BY_ID = {c["id"]: c for c in DOCX}

FILLING_PRICES = {
    "яблочный синнабон": 3000,
    "шоколадный с шоколадом": 2800,
    "ванильный с клубникой": 2800,
    "ванильный с вишней": 2800,
    "кукис энд крим": 3000,
    "мак-лимон": 3000,
    "фундук-кофе шоколад": 3600,
    "фисташка-малина": 3600,
    "шоколад-кокос": 3000,
    "морковный": 2800,
    "сникерс": 3000,
    "дорблю груша-грецкий орех": 3600,
    "апельсин-манго-маракуйя": 3000,
    "черника-шоколад": 3600,
    "фисташковый чизкейк": 3000,
    "чизкейк орео": 3000,
    "чизкейк Нью Йорк": 3000,
    "тирамису": 3000,
}
TIERED_FILLING_RATE = 3200
SAMPLE_FILLING = "яблочный синнабон"


def decor_for_weight(table: list[tuple], w: float) -> int:
    for lo, hi, price in table:
        if lo <= w <= hi:
            return price
    return table[-1][2]


def calc_total(cake: dict, *, weight: float | None = None, tiers: int | None = None, filling: str = SAMPLE_FILLING) -> int:
    t = cake["type"]
    fp = FILLING_PRICES[filling]
    if t == "tiered":
        w = weight if weight is not None else cake["minWeight"]
        tr = tiers if tiers is not None else cake["minTiers"]
        return tr * cake["decorPerTier"] + w * TIERED_FILLING_RATE
    if t == "fixed":
        w = weight if weight is not None else 2.5
        key = str(w) if str(w) in cake["decor"] else w
        return cake["decor"][key] + w * fp
    w = weight if weight is not None else cake["minWeight"]
    decor = decor_for_weight(cake["decorTable"], w)
    if cake["id"] == "tiramisu":
        return w * fp
    return decor + w * fp


def extract_fixed_decor(doc: dict) -> dict[float, int] | None:
    raw = " ".join(doc.get("pricing_raw") or [])
    m = re.search(
        r"фиксированный вес.*?2[,.]5.*?3[,.]5.*?оформлени[ея]\s*(\d+).*?(\d+)",
        raw,
        re.I,
    )
    if not m:
        return None
    return {2.5: int(m.group(1)), 3.5: int(m.group(2))}


def main() -> int:
    issues: list[str] = []
    print("=== Smoke totals (мин. параметры, синнабон) ===\n")
    for cake in CAKES:
        cid = cake["id"]
        total = calc_total(cake)
        doc = DOCX_BY_ID.get(cid, {})
        pr = " | ".join(doc.get("pricing_raw") or [])[:120]
        print(f"{cid:22} {cake['type']:7} -> {total:>7}р  |  {pr}")

        if cake["type"] == "fixed":
            doc_decor = extract_fixed_decor(doc)
            if doc_decor:
                for w, expected in doc_decor.items():
                    got = cake["decor"].get(str(w), cake["decor"].get(w))
                    if got != expected:
                        issues.append(
                            f"{cid}: decor[{w}]={got} != docx {expected}"
                        )
            # blueberry hill sample
            if cid == "blueberry-hill":
                t25 = calc_total(cake, weight=2.5)
                if t25 != 13000:
                    issues.append(f"blueberry-hill 2.5+синнабон: {t25} ≠ 13000")

    print("\n=== Fixed-weight spot checks (ves*nachinka + dekor) ===")
    for cid, w, expected in [
        ("blueberry-hill", 2.5, 13000),
        ("blueberry-hill", 3.5, 17000),
        ("faberge", 2.5, 10500),
        ("faberge", 3.5, 14000),
        ("secret-garden", 2.5, 11000),
        ("secret-garden", 3.5, 14500),
        ("la-la-land", 2.5, 10500),
        ("la-la-land", 3.5, 14000),
    ]:
        cake = next(c for c in CAKES if c["id"] == cid)
        got = calc_total(cake, weight=w)
        ok = "OK" if got == expected else "FAIL"
        print(f"  {ok} {cid} {w}kg -> {got} (expect {expected})")
        if got != expected:
            issues.append(f"{cid} {w}kg: {got} != {expected}")

    print("\n=== Weight cakes (decor + weight*filling) ===")
    for cid, w, expected_decor, expected_total in [
        ("letter", 4.0, 3000, 15000),
        ("swan-lake", 2.0, 2500, 8500),
        ("tiramisu", 2.0, 0, 6000),
    ]:
        cake = next(c for c in CAKES if c["id"] == cid)
        decor = decor_for_weight(cake["decorTable"], w)
        total = calc_total(cake, weight=w)
        print(f"  {cid} {w}кг decor={decor} total={total} (ожид.total {expected_total})")
        if decor != expected_decor:
            issues.append(f"{cid} decor@{w}={decor} != {expected_decor}")
        if total != expected_total:
            issues.append(f"{cid} total@{w}={total} != {expected_total}")

    if issues:
        print("\n=== ISSUES ===")
        for i in issues:
            print(" !", i)
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
