import re
from pathlib import Path

SITE = Path(__file__).resolve().parent
text = (SITE / "index.html").read_text(encoding="utf-8")
m = re.search(r"<main class=\"cover-grid\">[\s\S]*?</main>", text)
main = m.group(0) if m else ""
scroll_fix = (
    "<style>"
    "html,body{overflow-x:hidden!important;overflow-y:auto!important;"
    "height:auto!important;min-height:100%}"
    "</style>\n"
)
embed = (
    '<base href="https://yavyach.github.io/Kosmos-Cakes/site/">\n'
    '<link rel="stylesheet" href="style.css">\n'
    + scroll_fix
    + main
)
(SITE / "tilda-catalog-embed.html").write_text(embed, encoding="utf-8")
print(len(embed))
