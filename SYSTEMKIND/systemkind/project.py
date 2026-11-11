"""Projektdateien: laden, prüfen, neues Thema anlegen."""
from __future__ import annotations

import json
import re
import unicodedata

from . import config as C
from .scenes import REGISTRY

BACKGROUNDS = {"particles", "grid", "rings", "skyline", "plain", "beams"}
TRANSITIONS = {"fade", "dip", "push", "sweep", "cut"}


def slugify(topic: str) -> str:
    s = topic.lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        s = s.replace(a, b)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:60]


def path_for(topic: str):
    return C.PROJECTS / slugify(topic) / "project.json"


def load(topic: str) -> dict | None:
    p = path_for(topic)
    if not p.exists():
        return None
    proj = json.loads(p.read_text(encoding="utf-8"))
    proj["slug"] = slugify(topic)
    proj["_path"] = str(p)
    return proj


def save(proj: dict):
    data = {k: v for k, v in proj.items() if not k.startswith("_")}
    with open(proj["_path"], "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def _strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from _strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _strings(v)


def validate(proj: dict) -> tuple[list[str], list[str]]:
    """Gibt (Fehler, Warnungen) zurück. Fehler blockieren das Rendering."""
    err, warn = [], []
    facts = {f["id"]: f for f in proj.get("research", {}).get("facts", [])}
    for f in facts.values():
        if not f.get("source") or not (f.get("url") or f.get("kind") == "calculation"):
            err.append(f"Fakt '{f['id']}': Quelle oder URL fehlt.")
        if not f.get("verified"):
            err.append(f"Fakt '{f['id']}' ist nicht als geprüft markiert (verified: false).")
    if not proj.get("scenes"):
        err.append("Keine Szenen definiert.")
    for i, sc in enumerate(proj.get("scenes", []), 1):
        tag = f"Szene {i} ({sc.get('id', '?')})"
        if sc.get("type") not in REGISTRY:
            err.append(f"{tag}: unbekannter Typ '{sc.get('type')}'. Verfügbar: {sorted(REGISTRY)}")
        if sc.get("background", "plain") not in BACKGROUNDS:
            err.append(f"{tag}: unbekannter Hintergrund '{sc.get('background')}'.")
        if sc.get("transition", "fade") not in TRANSITIONS:
            err.append(f"{tag}: unbekannter Übergang '{sc.get('transition')}'.")
        if not sc.get("vo"):
            warn.append(f"{tag}: kein Voice-over.")
        for s in sc.get("vo", []):
            if not s.get("text", "").strip():
                err.append(f"{tag}: leerer Voice-over-Satz.")
        for fid in sc.get("facts", []):
            if fid not in facts:
                err.append(f"{tag}: verweist auf unbekannten Fakt '{fid}'.")
        if sc.get("type") in ("bars", "growth", "formula") and not sc.get("facts"):
            err.append(f"{tag}: zeigt Zahlen/Thesen, nennt aber keinen Fakt (facts: [...]).")
        if any("TODO" in s for s in _strings(sc)):
            err.append(f"{tag}: enthält noch Platzhalter (TODO).")
    for u in proj.get("research", {}).get("uncertainties", []):
        warn.append(f"Unsicherheit: {u}")
    return err, warn


TEMPLATE = {
    "topic": "",
    "status": "draft",
    "voice": {"length_scale": 1.0},
    "music": {"seed": 3},
    "research": {
        "facts": [{"id": "f1", "claim": "TODO: überprüfbare Aussage", "source": "TODO: Herausgeber, Titel, Jahr",
                   "url": "", "verified": False, "confidence": "hoch | mittel | niedrig"}],
        "uncertainties": ["TODO: Was ist umstritten oder unklar?"],
    },
    "scenes": [
        {"id": "hook", "type": "title", "background": "particles", "transition": "fade",
         "vo": [{"text": "TODO: Hook – die Frage des Videos."}],
         "params": {"kicker": "SYSTEMKIND", "lines": ["TODO *Hook*"]}},
        {"id": "kern", "type": "statement", "background": "grid", "transition": "sweep",
         "vo": [{"text": "TODO: Kernaussage."}],
         "params": {"kicker": "Der Mechanismus", "lines": ["TODO *Aussage*"]}},
        {"id": "outro", "type": "outro", "background": "rings", "transition": "dip",
         "vo": [{"text": "TODO: Schlusssatz."}],
         "params": {"lines": ["TODO"], "tagline": "Verstehe das System.", "sources": []}},
    ],
}

BRIEF = """# Produktionsauftrag: {topic}

Dieses Projekt ist ein Entwurf. `project.json` enthält noch Platzhalter (TODO)
und wird deshalb nicht gerendert.

## So geht es weiter

1. Recherche: Fakten mit Quelle und URL in `research.facts` eintragen.
   Nur geprüfte Fakten bekommen `"verified": true`. Unsicheres gehört in
   `research.uncertainties` – oder wird weggelassen.
2. Skript: pro Szene Voice-over-Sätze (`vo`) und Bildinhalt (`params`) schreiben.
   Zielumfang: 100–120 Wörter (ergibt 45–55 Sekunden).
3. Prüfen: `python main.py --topic "{topic}" --review`

Tipp: In Claude Code genügt der Auftrag
„Recherchiere und fülle SYSTEMKIND/projects/{slug}/project.json nach
docs/PROJEKTFORMAT.md aus – keine erfundenen Zahlen.“

Szenentypen, Hintergründe und Felder: siehe `docs/PROJEKTFORMAT.md`.
"""


def scaffold(topic: str):
    p = path_for(topic)
    p.parent.mkdir(parents=True, exist_ok=True)
    data = json.loads(json.dumps(TEMPLATE))
    data["topic"] = topic
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (p.parent / "AUFTRAG.md").write_text(BRIEF.format(topic=topic, slug=slugify(topic)), encoding="utf-8")
    return p
