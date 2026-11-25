"""Maak de voorgelezen audio voor een quiz met Piper (Vlaamse stem, trager tempo).

Alleen fragmenten die ontbreken of waarvan de tekst veranderde, worden (opnieuw) gemaakt.
Welke tekst bij welk bestand hoort, staat in <map>/audio/teksten.json.

Gebruik:
  python3 engine/maak_audio.py verkeer-les-7            # ontbrekende/gewijzigde fragmenten
  python3 engine/maak_audio.py verkeer-les-7 --alles    # alles opnieuw
  python3 engine/maak_audio.py verkeer --vertrouw-bestaande
        # bestaande mp3's als juist beschouwen en alleen teksten.json aanmaken

Stem: engine/voices/nl_BE-nathalie-medium.onnx (+ .onnx.json), niet in git (126 MB). Downloaden:
  https://huggingface.co/rhasspy/piper-voices/tree/main/nl/nl_BE/nathalie/medium
Tempo: LENGTH_SCALE (1.3 = trager dan normaal, geschikt voor anderstaligen).
"""
import json, re, subprocess, sys, wave
from pathlib import Path

ENGINE = Path(__file__).resolve().parent
ROOT = ENGINE.parent
VOICE = ENGINE / "voices" / "nl_BE-nathalie-medium.onnx"
LENGTH_SCALE = 1.3
L = "ABC"


def spreek(t: str) -> str:
    """Schrijfwijze omzetten naar iets wat de stem goed uitspreekt."""
    t = t.replace("km/u", "kilometer per uur").replace("bv.", "bijvoorbeeld")
    t = t.replace("GPS", "gps").replace("NIET", "niet")
    t = t.replace("M.T.M.", "M T M").replace("M.B.T.", "M B T").replace("MTM", "M T M").replace("MBT", "M B T")
    t = re.sub(r"\b((?:[A-Z]\.){2,})", lambda m: " ".join(m.group(1).replace(".", "")), t)  # P.I.C.S. -> P I C S
    t = re.sub(r"(\d) (\d{3})\b", r"\1\2", t)              # 35 000 -> 35000
    t = re.sub(r"\+(\d)", r"plus \1", t)                   # +3,5 t -> plus 3,5 t
    t = re.sub(r"(\d),(\d)", r"\1 komma \2", t)          # 3,5 -> 3 komma 5
    t = re.sub(r"(\d)\s?t\b", r"\1 ton", t)               # 3,5 t -> ton
    t = re.sub(r"(\d)\s?kg\b", r"\1 kilogram", t)
    t = re.sub(r"(\d)\s?m\b", r"\1 meter", t)
    t = re.sub(r"\s*\(([^)]*)\)", r", \1,", t)           # haakjes -> korte pauze
    t = re.sub(r",\s*([.?!]|$)", r"\1", t).strip()
    if t and t[-1] not in ".?!":
        t += "."
    return t


def teksten(map_: Path) -> dict:
    """Alle fragmenten van een quiz: bestandsnaam -> uit te spreken tekst."""
    quiz = json.loads((map_ / "quiz.json").read_text(encoding="utf-8"))
    vragen = json.loads((map_ / "vragen.json").read_text(encoding="utf-8"))
    t = {}
    for i, v in enumerate(vragen, 1):
        t[f"v{i:02d}"] = spreek(v["q"])                       # zonder nummer: volgorde wordt geshuffeld
        for j, a in enumerate(v["a"]):                         # zonder letter: antwoorden worden geshuffeld
            t[f"v{i:02d}{L[j].lower()}"] = spreek(a)
    t.update({
        "welkom": quiz["welkom"],
        "goed": "Goed zo! Dat is juist.",
        "fout": "Dat is niet juist.",
        "tijd-om": "De tijd is om.",
        "einde": "Klaar! Goed gewerkt.",
        **{f"letter-{x.lower()}": f"{x}." for x in L},
        **{f"juist-{x.lower()}": f"Het juiste antwoord is {x}." for x in L},
    })
    return t


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        sys.exit(__doc__)
    map_ = ROOT / args[0]
    out = map_ / "audio"
    out.mkdir(exist_ok=True)
    manifest_pad = out / "teksten.json"
    oud = json.loads(manifest_pad.read_text(encoding="utf-8")) if manifest_pad.exists() else {}
    nieuw = teksten(map_)

    if "--vertrouw-bestaande" in sys.argv:
        oud = {k: v for k, v in nieuw.items() if (out / f"{k}.mp3").exists()}
    te_doen = [k for k, v in nieuw.items()
               if "--alles" in sys.argv or oud.get(k) != v or not (out / f"{k}.mp3").exists()]

    if te_doen:
        from piper import PiperVoice, SynthesisConfig
        voice = PiperVoice.load(str(VOICE))
        cfg = SynthesisConfig(length_scale=LENGTH_SCALE)
        for k in te_doen:
            wav = out / f"{k}.wav"
            with wave.open(str(wav), "wb") as w:
                voice.synthesize_wav(nieuw[k], w, syn_config=cfg)
            # 0,3 s stilte vooraan zodat het begin niet wegvalt, dan naar mp3
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav),
                            "-af", "adelay=300,apad=pad_dur=0.2", "-ac", "1", "-b:a", "64k",
                            str(out / f"{k}.mp3")], check=True)
            wav.unlink()
            print(k, "-", nieuw[k])

    # fragmenten die niet meer nodig zijn opruimen
    weg = [p for p in out.glob("*.mp3") if p.stem not in nieuw]
    for p in weg:
        p.unlink()
    manifest_pad.write_text(json.dumps(nieuw, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{map_.name}: {len(te_doen)} gemaakt, {len(weg)} verwijderd, {len(nieuw)} in totaal")


if __name__ == "__main__":
    main()
