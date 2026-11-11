"""Produktionsbericht (Markdown)."""
from __future__ import annotations

import datetime

from . import config as C
from . import tts


def write(path, proj, tl, checks, used_broll, missing, warnings, files, loud=None):
    ok = all(c["ok"] for c in checks)
    vs = tts.settings(proj)
    words = sum(len(s["text"].split()) for sc in tl["scenes"] for s in sc["sentences"])
    L = [f"# Produktionsbericht – {proj['topic']}", "",
         f"- Erstellt: {datetime.datetime.now():%d.%m.%Y %H:%M}",
         f"- Video: `{files['video']}`",
         f"- Untertitel: `{files['srt']}`",
         f"- Länge: {tl['duration']:.1f} s · {len(tl['scenes'])} Szenen · {words} Wörter Voice-over",
         f"- Qualitätskontrolle: **{'bestanden' if ok else 'FEHLER – siehe unten'}**", "",
         "## Qualitätskontrolle", "", "| Prüfung | Ergebnis | Detail |", "|---|---|---|"]
    L += [f"| {c['name']} | {'✅' if c['ok'] else '❌'} | {c['detail']} |" for c in checks]
    L += ["", "## Szenen", "", "| # | Start | Dauer | Typ | Hintergrund | Voice-over |", "|---|---|---|---|---|---|"]
    for sc in tl["scenes"]:
        vo = " ".join(s["text"] for s in sc["sentences"])
        bg = "B-Roll" if sc.get("broll_file") else sc["background"]
        L.append(f"| {sc['index'] + 1} | {sc['start']:.1f} s | {sc['duration']:.1f} s | {sc['type']} | {bg} | {vo} |")
    L += ["", "## Fakten und Quellen", ""]
    for f in proj.get("research", {}).get("facts", []):
        L += [f"- **{f['id']}** – {f['claim']}",
              f"  - Quelle: {f['source']}" + (f" – {f['url']}" if f.get("url") else ""),
              f"  - Geprüft: {'ja' if f.get('verified') else 'NEIN'} · Sicherheit: {f.get('confidence', '-')}"
              + (f" · Hinweis: {f['note']}" if f.get("note") else "")]
    unc = proj.get("research", {}).get("uncertainties", [])
    if unc:
        L += ["", "## Unsicherheiten", ""] + [f"- {u}" for u in unc]
    L += ["", "## Verwendete Assets und Lizenzen", "",
          f"- Stimme: {tts.describe(vs)}",
          "- Musik und Soundeffekte: von der Pipeline selbst erzeugt (prozedural), keine Fremdrechte",
          "- Grafiken und Animationen: von der Pipeline selbst erzeugt",
          "- Schriften: Playfair Display und Inter – SIL Open Font License 1.1"]
    for u in used_broll:
        L.append(f"- B-Roll `{u['file']}` (Szene {u['scene']}): {u['source']} – {u['url']} – Lizenz: {u['license']}"
                 + (f" – Urheber: {u['author']}" if u.get("author") else ""))
    if not used_broll:
        L.append("- B-Roll: keine Fremdaufnahmen verwendet")
    L += ["", "## Fehlende Assets", ""] + ([f"- {m}" for m in missing] or ["- keine"])
    if warnings:
        L += ["", "## Hinweise", ""] + [f"- {w}" for w in warnings]
    L += ["", "## Veröffentlichung", "",
          "Das Video wurde **nicht** veröffentlicht. Ein Upload erfolgt nur manuell nach deiner Freigabe.", ""]
    open(path, "w", encoding="utf-8").write("\n".join(L))
    return ok
