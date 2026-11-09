#!/usr/bin/env python3
"""Baut aus web/src die Seiten:
- web/app.html   : Inhalt für das claude.ai-Artifact (ohne <html>/<head>, wird beim Veröffentlichen ergänzt)
- web/index.html : eigenständige Web-App (PWA) für eigenes Hosting, z. B. GitHub Pages
"""
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"
FONTS = ("https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600..800"
         "&family=Figtree:wght@400..800&display=swap")

css = (SRC / "style.css").read_text()
js = (SRC / "content.js").read_text() + "\n" + (SRC / "app.js").read_text()

body = f"""<title>Fabulous</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<style>
{css}
</style>
<div id="app"></div>
<div id="sheet-root"></div>
<div id="player-root"></div>
<div id="toast" class="toast" role="status" aria-live="polite"></div>
<script>
{js}
</script>
"""

(ROOT / "app.html").write_text(body)

standalone = f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#EE5A36">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Fabulous">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" type="image/png" sizes="192x192" href="icons/icon-192.png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<style>:root{{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}body{{margin:0}}[hidden]{{display:none!important}}</style>
</head>
<body>
{body}<script>
if ('serviceWorker' in navigator && location.protocol === 'https:') {{
  window.addEventListener('load', () => navigator.serviceWorker.register('sw.js').catch(() => {{}}));
}}
</script>
</body>
</html>
"""
(ROOT / "index.html").write_text(standalone)
print("app.html", len(body), "bytes; index.html", len(standalone), "bytes")
