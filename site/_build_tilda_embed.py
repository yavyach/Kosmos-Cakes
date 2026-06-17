"""Сборка HTML-блока каталога для вставки в Tilda (inline JS — без внешнего catalog-init.js)."""
import re
from pathlib import Path

SITE = Path(__file__).resolve().parent
PUBLIC = "https://yavyach.github.io/Kosmos-Cakes/site/"


def _mtime(name: str) -> str:
    p = SITE / name
    return str(int(p.stat().st_mtime)) if p.exists() else ""


css_v = _mtime("style.css")
js_v = _mtime("catalog-init.js")

text = (SITE / "index.html").read_text(encoding="utf-8")
m = re.search(r'<main class="cover-grid">[\s\S]*?</main>', text)
main = m.group(0) if m else ""
main = main.replace('src="photos/', f'src="{PUBLIC}photos/')
main = re.sub(
    r'href="cakes/([^"]+\.html)"',
    r'href="#/cake/\1" data-kosmos-cake="cakes/\1"',
    main,
)

scroll_fix = (
    "<style>"
    "html,body{margin:0;padding:0;width:100%;}"
    "html.catalog-page,body.catalog-page{height:auto;min-height:100%;}"
    "body.catalog-page{overflow-y:auto!important;overflow-x:hidden!important;}"
    "#allrecords{overflow:visible!important;height:auto!important;min-height:100%!important}"
    ".kosmos-catalog-embed{"
    "display:block;width:100%;min-height:100vh;min-height:100dvh;"
    "overflow:visible;position:relative;"
    "}"
    "#kosmos-cake-viewer{position:fixed;inset:0;z-index:99999;display:none;background:#cfcfcf}"
    "#kosmos-cake-viewer.is-open{display:block}"
    "#kosmos-cake-viewer iframe{width:100%;height:100%;border:0;display:block}"
    "body.kosmos-cake-open{overflow:hidden!important}"
    ".kosmos-catalog-embed .cover img{height:100%;animation:none!important;transform:none!important;will-change:auto}"
    "</style>\n"
)

boot_class = (
    "<script>"
    "document.documentElement.classList.add('catalog-page');"
    "document.body.classList.add('catalog-page');"
    "</script>\n"
)

viewer = (
    '<div id="kosmos-cake-viewer" aria-hidden="true">'
    '<iframe title="карточка торта"></iframe></div>\n'
    "<script>\n"
    "(function(){\n"
    f"  var SITE='{PUBLIC}';\n"
    "  var viewer=document.getElementById('kosmos-cake-viewer');\n"
    "  var frame=viewer&&viewer.querySelector('iframe');\n"
    "  var grid=document.querySelector('.cover-grid');\n"
    "  if(!viewer||!frame||!grid)return;\n"
    "  function cakePathFromHash(){\n"
    "    var m=location.hash.match(/^#\\/cake\\/(.+)$/);\n"
    "    if(!m)return'';\n"
    "    var slug=m[1].replace(/\\.html$/i,'');\n"
    "    return 'cakes/'+slug+'.html';\n"
    "  }\n"
    "  function openCake(path, skipHistory){\n"
    "    if(!path)return;\n"
    "    var slug=path.replace(/^cakes\\//,'').replace(/\\.html$/i,'');\n"
    "    frame.src=SITE+path+(path.indexOf('?')>=0?'&':'?')+'embed=kosmos';\n"
    "    viewer.classList.add('is-open');\n"
    "    viewer.setAttribute('aria-hidden','false');\n"
    "    document.body.classList.add('kosmos-cake-open');\n"
    "    var hash='#/cake/'+slug;\n"
    "    if(!skipHistory&&location.hash!==hash){\n"
    "      history.pushState({kosmosCake:slug},'',hash);\n"
    "    }\n"
    "  }\n"
    "  function closeCake(){\n"
    "    if(!viewer.classList.contains('is-open'))return;\n"
    "    viewer.classList.remove('is-open');\n"
    "    viewer.setAttribute('aria-hidden','true');\n"
    "    document.body.classList.remove('kosmos-cake-open');\n"
    "    frame.src='about:blank';\n"
    "    if(location.hash.indexOf('#/cake/')===0){\n"
    "      history.replaceState(null,'',location.pathname+location.search);\n"
    "    }\n"
    "  }\n"
    "  grid.addEventListener('click',function(e){\n"
    "    var a=e.target.closest('a.cover');\n"
    "    if(!a)return;\n"
    "    var path=a.getAttribute('data-kosmos-cake')||'';\n"
    "    if(!path)return;\n"
    "    e.preventDefault();\n"
    "    openCake(path);\n"
    "  });\n"
    "  window.addEventListener('message',function(e){\n"
    "    if(e&&e.data==='kosmos-close-cake')closeCake();\n"
    "  });\n"
    "  window.addEventListener('popstate',function(){\n"
    "    var path=cakePathFromHash();\n"
    "    if(path){\n"
    "      if(!viewer.classList.contains('is-open'))openCake(path,true);\n"
    "    }else{\n"
    "      closeCake();\n"
    "    }\n"
    "  });\n"
    "  window.addEventListener('hashchange',function(){\n"
    "    var path=cakePathFromHash();\n"
    "    if(path){\n"
    "      if(!viewer.classList.contains('is-open'))openCake(path,true);\n"
    "    }else{\n"
    "      closeCake();\n"
    "    }\n"
    "  });\n"
    "  var initial=cakePathFromHash();\n"
    "  if(initial)openCake(initial,true);\n"
    "})();\n"
    "</script>\n"
)

catalog_js = (SITE / "catalog-init.js").read_text(encoding="utf-8")
catalog_script = f"<script>\n/* catalog-init.js v={js_v} */\n{catalog_js}\n</script>\n"

embed = (
    f'<link rel="icon" href="{PUBLIC}assets/favicon.svg" type="image/svg+xml">\n'
    f'<link rel="stylesheet" href="{PUBLIC}style.css?v={css_v}">\n'
    + scroll_fix
    + boot_class
    + '<div class="kosmos-catalog-embed">\n'
    + main
    + "\n</div>\n"
    + catalog_script
    + viewer
)
(SITE / "tilda-catalog-embed.html").write_text(embed, encoding="utf-8")
(SITE / "tilda-embed.html").write_text(embed, encoding="utf-8")
print(len(embed))
