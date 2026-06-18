"""
Русская типографика для текстов тортов.

Кавычки: «ёлочки».
Дефис (-): сложные слова, частицы, префиксы — без пробелов вокруг.
Короткое тире (–): числовые диапазоны — без пробелов.
Длинное тире (—): прочие случаи — с пробелами.
"""

from __future__ import annotations

import re

# «…» вместо "…", "…", „…"
_QUOTE_PATTERNS = (
    re.compile(r'"([^"]+)"'),
    re.compile(r"“([^”]+)”"),
    re.compile(r'„([^"]+)"'),
    re.compile(r"«([^»]+)»"),  # idempotent
)

# 4-5, 4–5, 1.5-3.5, 90-х → короткое тире
_NUM_RANGE = re.compile(
    r"(?<!\w)(\d+(?:[.,]\d+)?)\s*[-–—]\s*(\d+(?:[.,]\d+)?)"
)

# Пунктуационное « - » / « – » → длинное тире с пробелами
_PUNCT_DASH = re.compile(r"\s+[-–—]\s+")


def quotes_to_guillemets(text: str) -> str:
    out = text
    for pat in _QUOTE_PATTERNS[:3]:
        out = pat.sub(r"«\1»", out)
    return out


def normalize_dashes(text: str) -> str:
    """Сначала диапазоны (–), затем пунктуация (—)."""
    out = _NUM_RANGE.sub(r"\1–\2", text)
    out = _PUNCT_DASH.sub(" — ", out)
    return out


def normalize_typography(text: str) -> str:
    if not text:
        return text
    text = quotes_to_guillemets(text)
    text = normalize_dashes(text)
    return text


def normalize_cake_fields(cake: dict) -> dict:
    for key in ("desc", "subtitle", "details", "note"):
        if cake.get(key):
            cake[key] = normalize_typography(cake[key])
    return cake
