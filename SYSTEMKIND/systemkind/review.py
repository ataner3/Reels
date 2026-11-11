"""Interaktiver Review-Modus vor dem finalen Rendering."""
from __future__ import annotations

from . import config as C
from . import render


def storyboard(tl, path):
    imgs, labs = [], []
    for sc in tl["scenes"]:
        for u in (0.55, 0.96):
            T = sc["start"] + sc["duration"] * u
            imgs.append(render.frame_at(tl, T))
            labs.append(f"{sc['index'] + 1} {sc['id']}  {T:.1f}s")
    render.contact_sheet(imgs, labs, path, cols=4)
    return path


def show_script(tl):
    for sc in tl["scenes"]:
        bg = "B-Roll: " + sc["broll_file"] if sc.get("broll_file") else "Hintergrund: " + sc["background"]
        print(f"\n  Szene {sc['index'] + 1} · {sc['id']} · {sc['type']} · {sc['start']:.1f}–"
              f"{sc['start'] + sc['duration']:.1f} s · {bg} · Übergang: {sc['transition']}")
        for s in sc["sentences"]:
            print(f"    {s['start']:5.1f} s  {s['text']}")


def show_sources(proj):
    for f in proj.get("research", {}).get("facts", []):
        mark = "geprüft" if f.get("verified") else "UNGEPRÜFT"
        print(f"\n  [{f['id']}] ({mark}, Sicherheit: {f.get('confidence', '-')})\n    {f['claim']}"
              f"\n    Quelle: {f['source']} {f.get('url', '')}")
        if f.get("note"):
            print(f"    Hinweis: {f['note']}")
    for u in proj.get("research", {}).get("uncertainties", []):
        print(f"  ! {u}")


def run(proj, tl, used, missing, work_dir) -> str:
    """Gibt 'approve', 'reload' oder 'abort' zurück."""
    sb = storyboard(tl, work_dir / "storyboard.png")
    print(f"\n=== REVIEW: {proj['topic']} ===")
    print(f"  Länge: {tl['duration']:.1f} s · Szenen: {len(tl['scenes'])} · Untertitel: {len(tl['cues'])}")
    print(f"  Storyboard: {sb}")
    print(f"  Voice-over zum Anhören: {work_dir / 'vo.wav'}")
    print(f"  Projektdatei: {proj['_path']}")
    for m in missing:
        print(f"  FEHLT: {m}")
    for u in used:
        print(f"  B-Roll: Szene {u['scene']} ← {u['file']} ({u['source']}, {u['license']})")
    show_script(tl)
    while True:
        try:
            ans = input("\n[f] freigeben und rendern · [s] Skript · [q] Quellen · "
                        "[n] Projektdatei neu laden · [a] abbrechen > ").strip().lower()
        except EOFError:
            print("\nKeine Eingabe möglich – Rendering nicht freigegeben.")
            return "abort"
        if ans == "f":
            return "approve"
        if ans == "s":
            show_script(tl)
        elif ans == "q":
            show_sources(proj)
        elif ans == "n":
            return "reload"
        elif ans == "a":
            return "abort"
