import re
from pathlib import Path

SITE = Path(__file__).resolve().parent
PUBLIC = "https://yavyach.github.io/Kosmos-Cakes/site/"

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
    "html,body{overflow:hidden!important;height:100%!important}"
    "#allrecords{overflow:visible!important;height:auto!important;min-height:100%!important}"
    ".catalog-scroll-viewport{position:relative;height:100vh;max-height:100dvh;"
    "overflow-x:hidden!important;overflow-y:auto!important;-webkit-overflow-scrolling:touch;"
    "overscroll-behavior-y:contain;touch-action:pan-y}"
    "#kosmos-cake-viewer{position:fixed;inset:0;z-index:99999;display:none;"
    "background:#cfcfcf}"
    "#kosmos-cake-viewer.is-open{display:block}"
    "#kosmos-cake-viewer iframe{width:100%;height:100%;border:0;display:block}"
    "body.kosmos-cake-open{overflow:hidden!important}"
    "</style>\n"
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
    "  function openCake(path){\n"
    "    if(!path)return;\n"
    "    var slug=path.replace(/^cakes\\//,'').replace(/\\.html$/i,'');\n"
    "    frame.src=SITE+path+(path.indexOf('?')>=0?'&':'?')+'embed=kosmos';\n"
    "    viewer.classList.add('is-open');\n"
    "    viewer.setAttribute('aria-hidden','false');\n"
    "    document.body.classList.add('kosmos-cake-open');\n"
    "    if(location.hash!=='#/cake/'+slug)location.hash='#/cake/'+slug;\n"
    "  }\n"
    "  function closeCake(){\n"
    "    viewer.classList.remove('is-open');\n"
    "    viewer.setAttribute('aria-hidden','true');\n"
    "    document.body.classList.remove('kosmos-cake-open');\n"
    "    frame.src='about:blank';\n"
    "    if(location.hash.indexOf('#/cake/')===0)history.replaceState(null,'',location.pathname+location.search);\n"
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
    "  window.addEventListener('hashchange',function(){\n"
    "    var path=cakePathFromHash();\n"
    "    if(path)openCake(path); else if(viewer.classList.contains('is-open'))closeCake();\n"
    "  });\n"
    "  var initial=cakePathFromHash();\n"
    "  if(initial)openCake(initial);\n"
    "})();\n"
    "</script>\n"
)

embed = (
    f'<link rel="icon" href="{PUBLIC}assets/favicon.svg" type="image/svg+xml">\n'
    f'<link rel="stylesheet" href="{PUBLIC}style.css">\n'
    + scroll_fix
    + '<div class="kosmos-catalog-embed">\n'
    + main
    + "\n</div>\n"
    + f'<script src="{PUBLIC}catalog-init.js"></script>\n'
    + viewer
)
(SITE / "tilda-catalog-embed.html").write_text(embed, encoding="utf-8")
print(len(embed))
