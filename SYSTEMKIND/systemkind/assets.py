"""Asset-Manager: verwaltet B-Roll mit Quelle und Lizenz und verwendet
vorhandene Aufnahmen wieder. Es wird nichts automatisch heruntergeladen –
Clips werden bewusst importiert (main.py --add-asset …)."""
from __future__ import annotations

import datetime
import json
import shutil
import subprocess
from pathlib import Path

from . import config as C

MANIFEST = C.BROLL / "manifest.json"


def _load() -> dict:
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    return {"clips": []}


def _save(data: dict):
    C.BROLL.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def probe(path) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height:format=duration", "-of", "json", str(path)],
        capture_output=True, text=True, check=True).stdout
    j = json.loads(out)
    s = j["streams"][0]
    return {"width": s["width"], "height": s["height"], "duration": float(j["format"]["duration"])}


def add(file: str, tags: list[str], source: str, url: str, license: str, author: str = "") -> dict:
    """Clip in die Bibliothek aufnehmen. Quelle und Lizenz sind Pflicht."""
    src = Path(file)
    if not src.exists():
        raise SystemExit(f"Datei nicht gefunden: {file}")
    if not (source and url and license):
        raise SystemExit("Quelle (--source), URL (--url) und Lizenz (--license) sind Pflichtangaben.")
    info = probe(src)
    C.BROLL.mkdir(parents=True, exist_ok=True)
    dst = C.BROLL / src.name
    if src.resolve() != dst.resolve():
        shutil.copy2(src, dst)
    data = _load()
    data["clips"] = [c for c in data["clips"] if c["file"] != dst.name]
    clip = {"file": dst.name, "tags": sorted({t.strip().lower() for t in tags if t.strip()}),
            "source": source, "url": url, "license": license, "author": author,
            "added": datetime.date.today().isoformat(), "used_in": [], **info}
    data["clips"].append(clip)
    _save(data)
    return clip


def clips() -> list[dict]:
    return [c for c in _load()["clips"] if (C.BROLL / c["file"]).exists()]


def find(tags, exclude=()) -> dict | None:
    """Besten Clip für die Schlagworte finden; selten genutzte zuerst."""
    if isinstance(tags, str):
        tags = [tags]
    want = {t.lower() for t in tags}
    best, score = None, 0
    for c in clips():
        if c["file"] in exclude:
            continue
        s = len(want & set(c["tags"])) * 10 - len(c.get("used_in", []))
        if want & set(c["tags"]) and (best is None or s > score):
            best, score = c, s
    return best


def assign(timeline: dict) -> tuple[list[dict], list[str]]:
    """Ordnet Szenen mit 'broll'-Wunsch einen Clip zu. Gibt (genutzt, fehlend) zurück."""
    used, missing, taken = [], [], set()
    for sc in timeline["scenes"]:
        if not sc.get("broll"):
            continue
        clip = find(sc["broll"], exclude=taken)
        if clip:
            sc["broll_file"] = str(C.BROLL / clip["file"])
            taken.add(clip["file"])
            used.append({"scene": sc["id"], **clip})
        else:
            sc["broll_file"] = None
            missing.append(f"Szene '{sc['id']}': keine B-Roll für {sc['broll']} in der Bibliothek – "
                           f"animierter Hintergrund '{sc['background']}' als Ersatz verwendet.")
    return used, missing


def mark_used(used: list[dict], slug: str):
    data = _load()
    names = {u["file"] for u in used}
    for c in data["clips"]:
        if c["file"] in names and slug not in c.setdefault("used_in", []):
            c["used_in"].append(slug)
    if names:
        _save(data)
