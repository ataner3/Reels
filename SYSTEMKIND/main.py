#!/usr/bin/env python3
"""SYSTEMKIND Video Factory – ein Thema rein, ein fertiges Short raus.

    python main.py --topic "Warum werden die Reichen immer reicher?"
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time

from systemkind import config as C


def check_environment(verbose=True) -> bool:
    """Phase 0: Hardware und Software prüfen."""
    import os
    import platform
    rows, ok = [], True

    def row(name, good, detail, required=True):
        nonlocal ok
        ok &= good or not required
        rows.append((name, "ok" if good else ("FEHLT" if required else "optional"), detail))

    row("Python ≥ 3.10", sys.version_info >= (3, 10), platform.python_version())
    for tool in ("ffmpeg", "ffprobe"):
        path = shutil.which(tool)
        ver = subprocess.run([tool, "-version"], capture_output=True, text=True).stdout.split("\n")[0] if path else "nicht gefunden"
        row(tool, bool(path), ver[:60])
    if shutil.which("ffmpeg"):
        enc = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True).stdout
        row("FFmpeg: libx264 + aac", "libx264" in enc and " aac " in enc, "H.264- und AAC-Encoder")
    for mod in ("PIL", "numpy", "piper"):
        try:
            m = __import__(mod)
            row(f"Python-Paket {mod}", True, getattr(m, "__version__", "installiert"))
        except ImportError:
            row(f"Python-Paket {mod}", False, "pip install -r requirements.txt")
    from systemkind import tts
    row("Piper-Stimme", tts.voice_available(), C.VOICE["name"] + ("" if tts.voice_available() else " – python main.py --setup"))
    row("Schriften", C.SERIF.exists() and (C.SANS_DIR / C.SANS[400]).exists(), "Playfair Display, Inter")
    try:
        from PIL import features
        row("Pillow mit libraqm", features.check("raqm"), "für Versalziffern (sonst Mediävalziffern)", required=False)
    except ImportError:
        pass
    row("CPU-Kerne", True, str(os.cpu_count()))
    free = shutil.disk_usage(C.ROOT).free / 1e9
    row("Freier Speicher", free > 2, f"{free:.0f} GB")
    if verbose:
        for name, state, detail in rows:
            print(f"  [{state:^8}] {name:<24} {detail}")
    return ok


def produce(topic: str, review: bool, approve: bool) -> int:
    from systemkind import assets, audio, project, qc, render, report, timeline, tts
    from systemkind import review as review_mod

    t0 = time.time()
    proj = project.load(topic)
    if proj is None:
        p = project.scaffold(topic)
        print(f"Neues Projekt angelegt: {p.parent}\n"
              "Es gibt noch kein recherchiertes Skript zu diesem Thema. Ohne geprüfte Fakten wird\n"
              f"nichts gerendert. Nächster Schritt: {p.parent / 'AUFTRAG.md'}")
        return 2

    while True:
        print("\n[A] RESEARCH – Fakten und Quellen prüfen")
        errors, warnings = project.validate(proj)
        facts = proj.get("research", {}).get("facts", [])
        print(f"  {len(facts)} Fakten, {sum(1 for f in facts if f.get('verified'))} geprüft")
        for w in warnings:
            print(f"  Hinweis: {w}")
        if errors:
            print("\nDas Projekt kann nicht gerendert werden:")
            for e in errors:
                print(f"  ✗ {e}")
            return 2

        vname = tts.settings(proj)["name"]
        if not tts.voice_available(vname):
            print(f"  Lade Stimme {vname} …")
            tts.download_voice(vname)
        work = C.BUILD / proj["slug"]
        work.mkdir(parents=True, exist_ok=True)

        print("\n[B] SCRIPT + [D] AUDIO – Voice-over erzeugen, Szenen timen")
        tl, vo = timeline.build(proj)
        print(f"  Gesamtlänge: {tl['duration']:.1f} s")
        audio.write_wav(work / "vo.wav", vo)
        if not C.MIN_DURATION <= tl["duration"] <= C.MAX_DURATION:
            print(f"  ✗ Länge außerhalb von {C.MIN_DURATION:.0f}–{C.MAX_DURATION:.0f} s. Skript kürzen oder "
                  "erweitern (oder voice.length_scale anpassen).")
            return 2

        print("\n[C] ASSETS – B-Roll zuordnen")
        used, missing = assets.assign(tl)
        print(f"  {len(used)} Clips zugeordnet, {len(missing)} fehlend")
        for m in missing:
            print(f"  FEHLT: {m}")

        if review or proj.get("status") != "approved":
            if approve:
                proj["status"] = "approved"
                project.save(proj)
            else:
                ans = review_mod.run(proj, tl, used, missing, work)
                if ans == "reload":
                    proj = project.load(topic)
                    continue
                if ans == "abort":
                    print("Abgebrochen – es wurde nichts gerendert.")
                    return 1
                proj["status"] = "approved"
                project.save(proj)
        break

    print("\n[D] AUDIO – Musik, Soundeffekte, Mischung")
    audio.write_wav(work / "music.wav", audio.music(tl["duration"], proj.get("music", {}).get("seed", 3)))
    audio.write_wav(work / "sfx.wav", audio.sfx_track(tl["sfx"], tl["duration"]))
    audio.mix(work / "vo.wav", work / "music.wav", work / "sfx.wav", work / "mix.wav", tl["duration"])
    print(f"  {len(tl['sfx'])} Soundeffekte, Ziel-Lautheit {C.TARGET_LUFS:.0f} LUFS")

    print("\n[E] VIDEO – Szenen rendern")
    C.EXPORTS.mkdir(exist_ok=True)
    out = C.EXPORTS / f"{proj['slug']}.mp4"
    srt = C.EXPORTS / f"{proj['slug']}.srt"
    tmp = work / "render.mp4"
    render.render_video(tl, work / "mix.wav", tmp, work)
    timeline.write_srt(tl["cues"], srt)

    print("\n[F] QUALITY CONTROL")
    checks = qc.check(tmp, tl, srt)
    for c in checks:
        print(f"  {'✓' if c['ok'] else '✗'} {c['name']}: {c['detail']}")
    shots = [qc.frame_grab(tmp, sc["start"] + sc["duration"] * u) for sc in tl["scenes"] for u in (0.5, 0.95)]
    labels = [f"{sc['id']} {u:.0%}" for sc in tl["scenes"] for u in (0.5, 0.95)]
    render.contact_sheet(shots, labels, work / "qc_frames.png")
    shutil.move(tmp, out)
    rep = C.EXPORTS / f"{proj['slug']}_bericht.md"
    ok = report.write(rep, proj, tl, checks, used, missing, warnings,
                      {"video": out.name, "srt": srt.name})
    assets.mark_used(used, proj["slug"])
    print(f"\n{'FERTIG' if ok else 'FERTIG MIT FEHLERN'} in {time.time() - t0:.0f} s")
    print(f"  Video:      {out}  ({out.stat().st_size / 1e6:.1f} MB)")
    print(f"  Untertitel: {srt}")
    print(f"  Bericht:    {rep}")
    print(f"  Kontrollbilder: {work / 'qc_frames.png'}")
    print("  Nicht veröffentlicht – ein Upload erfolgt nur manuell durch dich.")
    return 0 if ok else 3


def main():
    ap = argparse.ArgumentParser(description="SYSTEMKIND Video Factory")
    ap.add_argument("--topic", help="Thema des Videos")
    ap.add_argument("--review", action="store_true", help="Skript, Szenen und Material vor dem Rendern prüfen")
    ap.add_argument("--approve", action="store_true", help="Entwurf ohne Rückfrage freigeben")
    ap.add_argument("--check", action="store_true", help="Hardware und Software prüfen")
    ap.add_argument("--setup", action="store_true", help="Piper-Stimme herunterladen und Umgebung prüfen")
    ap.add_argument("--list", action="store_true", help="Projekte anzeigen")
    ap.add_argument("--voice-samples", action="store_true", help="Hörproben der Stimm-Presets erzeugen")
    ap.add_argument("--assets", action="store_true", help="B-Roll-Bibliothek anzeigen")
    ap.add_argument("--add-asset", metavar="DATEI", help="Clip in die B-Roll-Bibliothek aufnehmen")
    ap.add_argument("--tags", default="", help="Schlagworte, kommagetrennt")
    ap.add_argument("--source", default="", help="Quelle, z. B. Pexels")
    ap.add_argument("--url", default="", help="Link zur Originalseite des Clips")
    ap.add_argument("--license", default="", help="Lizenzhinweis, z. B. 'Pexels License'")
    ap.add_argument("--author", default="", help="Urheber")
    a = ap.parse_args()

    if a.setup:
        from systemkind import tts
        print("Stimme:")
        tts.download_voice()
        print("Umgebung:")
        return 0 if check_environment() else 1
    if a.voice_samples:
        from systemkind import tts
        for label, vs, path in tts.samples(C.EXPORTS / "stimmproben"):
            print(f"  {label}: {path}")
        print("Stimme festlegen: VOICE in systemkind/config.py (oder \"voice\" im Projekt).")
        return 0
    if a.check:
        return 0 if check_environment() else 1
    if a.add_asset:
        from systemkind import assets
        c = assets.add(a.add_asset, a.tags.split(","), a.source, a.url, a.license, a.author)
        print(f"Aufgenommen: {c['file']} · {c['width']}×{c['height']} · {c['duration']:.1f} s · Tags: {', '.join(c['tags'])}")
        return 0
    if a.assets:
        from systemkind import assets
        cl = assets.clips()
        print(f"{len(cl)} Clips in {C.BROLL}")
        for c in cl:
            print(f"  {c['file']} · {', '.join(c['tags'])} · {c['source']} · {c['license']} · genutzt in {len(c.get('used_in', []))} Videos")
        return 0
    if a.list:
        import json
        for p in sorted(C.PROJECTS.glob("*/project.json")):
            j = json.loads(p.read_text(encoding="utf-8"))
            print(f"  [{j.get('status', '?'):^8}] {j.get('topic')}")
        return 0
    if a.topic:
        if not check_environment(verbose=False):
            print("Die Umgebung ist unvollständig:")
            check_environment()
            return 1
        return produce(a.topic, a.review, a.approve)
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
