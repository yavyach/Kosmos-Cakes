"""
Парсит «Вся инфа по тортикам.docx» и сравнивает с calculator/build_cakes.py.

Выход:
  calculator/_cakes_from_docx.json
  calculator/_docx_diff.txt
"""

import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from typography import normalize_typography
DOCX = ROOT.parent / "site" / "photos" / "Вся инфа по тортикам.docx"
BUILD = ROOT / "build_cakes.py"

W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

NAME_TO_ID: dict[str, str] = {
    "богемская рапсодия": "bohemian-rhapsody",
    "fairy cake": "fairy-cake",
    "big cherry fairy cake": "big-cherry-fairy-cake",
    "вавилон": "babylon",
    "лебединое озеро": "swan-lake",
    "фаберже": "faberge",
    "белль": "bell",
    "люмьер": "lumiere",
    "ягодные поля навсегда": "berry-fields",
    "green day": "green-day",
    "вишневый сад": "cherry-orchard",
    "куинджи": "kuinji",
    "дарси": "darcy",
    "shine bright": "shine-bright",
    "любовное настроение": "love-in-mood",
    "тирамису": "tiramisu",
    "secret garden": "secret-garden",
    "анна": "anna",
    "шапито": "chapito",
    "келли": "kelly",
    "орфей": "orpheus",
    "blueberry hill": "blueberry-hill",
    "la la land": "la-la-land",
    "тоторо": "totoro",
    "fuji": "fuji",
    "вам письмо": "letter",
    "аполлон": "apollo",
    "sailor moon": "sailor-moon",
    "dancing queen": "dancing-queen",
    "элизабет": "elizabeth",
}

FILLING_ALIASES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"шоколадный с шоколад\b", re.I), "шоколадный с шоколадом"),
    (re.compile(r"долблю\b", re.I), "дорблю груша-грецкий орех"),
    (re.compile(r"дорблю-груша", re.I), "дорблю груша-грецкий орех"),
    (re.compile(r"дорблю груша-грецкий", re.I), "дорблю груша-грецкий орех"),
    (re.compile(r"дорблю груша-\s*грецкий", re.I), "дорблю груша-грецкий орех"),
    (re.compile(r"чизкейк ньюйорк", re.I), "чизкейк Нью Йорк"),
    (re.compile(r"чизкейк нью йорк", re.I), "чизкейк Нью Йорк"),
    (re.compile(r"лист чизкейк", re.I), "чизкейк Нью Йорк"),
    (re.compile(r"чизкейк орех", re.I), "чизкейк орео"),
    (re.compile(r"^чизкейк$", re.I), "чизкейк орео"),
]

CANONICAL_FILLINGS = [
    "яблочный синнабон", "шоколадный с шоколадом", "ванильный с клубникой",
    "ванильный с вишней", "кукис энд крим", "мак-лимон", "фундук-кофе шоколад",
    "фисташка-малина", "шоколад-кокос", "морковный", "сникерс",
    "дорблю груша-грецкий орех", "апельсин-манго-маракуйя", "черника-шоколад",
    "чизкейк Нью Йорк", "чизкейк орео", "фисташковый чизкейк", "тирамису",
]

DISCLAIMER_MARKERS = (
    "цвет и другие детали",
    "ягоды и другие детали",
    "цвет, рисунок и другие детали",
    "вес фиксированный",
)
HISTORY_MARKERS = (
    "торт назван",
    "название торта",
)


def extract_docx_lines(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as zf:
        xml = zf.read("word/document.xml")
    root = ET.fromstring(xml)
    lines: list[str] = []
    for p in root.iter(f"{W_NS}p"):
        parts = [t.text for t in p.iter(f"{W_NS}t") if t.text]
        if parts:
            lines.append("".join(parts).strip())
    return lines


def normalize_filling_name(raw: str) -> str | None:
    s = raw.strip().lower()
    if not s or s in ("- все", "все"):
        return None
    for pat, repl in FILLING_ALIASES:
        s = pat.sub(repl.lower(), s)
    for c in CANONICAL_FILLINGS:
        if s == c.lower():
            return c
    return None


def parse_fillings(line: str) -> list[str]:
    m = re.search(r"начинки:\s*(.+)$", line, re.I)
    if not m:
        return []
    chunk = m.group(1).replace(" - ВСЕ", "")
    out: list[str] = []
    for part in re.split(r",\s*", chunk):
        name = normalize_filling_name(part)
        if name and name not in out:
            out.append(name)
    return out


def is_cake_header(line: str) -> bool:
    key = line.strip().lower()
    return key in NAME_TO_ID


def is_disclaimer(line: str) -> bool:
    low = line.lower()
    return any(m in low for m in DISCLAIMER_MARKERS)


def is_history(line: str) -> bool:
    low = line.lower()
    return any(low.startswith(m) for m in HISTORY_MARKERS)


def is_pricing(line: str) -> bool:
    low = line.lower()
    if re.search(r"начинки:", low):
        return True
    return bool(
        re.search(
            r"(заказ от|от \d|фиксированный вес|стоимость декора|оформление|"
            r"зависит от сложности|тирамису стоит|только 1 ярус)",
            low,
        )
    )


def parse_cakes(lines: list[str]) -> list[dict]:
    cakes: list[dict] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not is_cake_header(line):
            i += 1
            continue
        name = line.strip()
        cid = NAME_TO_ID[name.lower()]
        i += 1
        body: list[str] = []
        while i < len(lines) and not is_cake_header(lines[i]):
            if lines[i] and not re.fullmatch(r"_+", lines[i]):
                body.append(lines[i])
            i += 1
        desc_parts: list[str] = []
        subtitle_parts: list[str] = []
        details = ""
        pricing_lines: list[str] = []
        fillings: list[str] = []
        note = ""
        for row in body:
            if is_pricing(row):
                pricing_lines.append(row)
                fillings.extend(parse_fillings(row))
                if "только 1 ярус" in row.lower():
                    note = "Только 1 ярус!"
                continue
            if is_history(row):
                details = row
                continue
            if is_disclaimer(row):
                subtitle_parts.append(row)
                continue
            if not subtitle_parts and not details:
                desc_parts.append(row)
            elif subtitle_parts and not details:
                subtitle_parts.append(row)
            else:
                subtitle_parts.append(row)
        cakes.append(
            {
                "id": cid,
                "name": name,
                "desc": normalize_typography("\n".join(desc_parts)),
                "subtitle": normalize_typography("\n".join(subtitle_parts)),
                "details": normalize_typography(details),
                "pricing_raw": pricing_lines,
                "fillings": fillings,
                "note": normalize_typography(note),
            }
        )
    return cakes


def load_build_cakes() -> dict[str, dict]:
    import importlib.util

    spec = importlib.util.spec_from_file_location("build_cakes", BUILD)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return {c["id"]: c for c in mod.CAKES}


def diff_report(parsed: list[dict], current: dict[str, dict]) -> str:
    lines: list[str] = []
    for p in parsed:
        cid = p["id"]
        cur = current.get(cid)
        if not cur:
            lines.append(f"=== {cid}: MISSING IN build_cakes.py ===")
            continue
        lines.append(f"=== {cid} ===")
        for field in ("desc", "subtitle", "details"):
            a, b = p.get(field, ""), cur.get(field, "")
            if a != b:
                lines.append(f"  {field}:")
                lines.append(f"    docx: {a!r}")
                lines.append(f"    code: {b!r}")
        if p.get("note") and p["note"] != cur.get("note", ""):
            lines.append(f"  note: docx={p['note']!r} code={cur.get('note', '')!r}")
    return "\n".join(lines) + "\n"


def main() -> int:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout.reconfigure(encoding="utf-8")
    if not DOCX.is_file():
        print(f"ERROR: docx not found: {DOCX}")
        return 1
    lines = extract_docx_lines(DOCX)
    parsed = parse_cakes(lines)
    out_json = ROOT / "_cakes_from_docx.json"
    out_json.write_text(json.dumps(parsed, ensure_ascii=False, indent=2), encoding="utf-8")
    current = load_build_cakes()
    report = diff_report(parsed, current)
    (ROOT / "_docx_diff.txt").write_text(report, encoding="utf-8")
    print(f"OK: {len(parsed)} cakes → {out_json.name}")
    print(f"OK: diff → _docx_diff.txt ({report.count('===')} blocks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
