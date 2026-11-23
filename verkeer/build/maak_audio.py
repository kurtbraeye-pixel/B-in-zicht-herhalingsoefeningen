"""Genereer alle audio voor de quiz met Piper (Vlaamse stem, trager tempo)."""
import json, re, subprocess, sys, wave
from pathlib import Path
from piper import PiperVoice, SynthesisConfig

ROOT = Path(__file__).resolve().parent.parent
VOICE = ROOT / "voices" / "nl_BE-nathalie-medium.onnx"
OUT = ROOT / "audio"
LENGTH_SCALE = float(sys.argv[1]) if len(sys.argv) > 1 else 1.3  # >1 = trager

def spreek(t: str) -> str:
    t = t.replace("km/u", "kilometer per uur").replace("bv.", "bijvoorbeeld")
    t = t.replace("GPS", "gps").replace("NIET", "niet").replace("e-step", "e-step")
    t = re.sub(r"\s*\(([^)]*)\)", r", \1,", t)  # haakjes -> korte pauze
    t = re.sub(r",\s*([.?!]|$)", r"\1", t).strip()
    if t and t[-1] not in ".?!":
        t += "."
    return t

voice = PiperVoice.load(str(VOICE))
cfg = SynthesisConfig(length_scale=LENGTH_SCALE)
OUT.mkdir(exist_ok=True)

def tts(text, name):
    wav = OUT / f"{name}.wav"
    with wave.open(str(wav), "wb") as w:
        voice.synthesize_wav(text, w, syn_config=cfg)
    # 0,3 s stilte vooraan zodat het begin niet wegvalt, dan naar mp3
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav),
                    "-af", "adelay=300,apad=pad_dur=0.2", "-ac", "1",
                    "-b:a", "64k", str(OUT / f"{name}.mp3")], check=True)
    wav.unlink()

vragen = json.load(open(ROOT / "build" / "vragen.json", encoding="utf-8"))
L = "ABC"
for i, v in enumerate(vragen, 1):
    tts(spreek(v["q"]), f"v{i:02d}")  # zonder nummer: volgorde wordt geshuffeld
    # antwoorden zonder letter: de volgorde wordt in de quiz geshuffeld
    for j, a in enumerate(v["a"]):
        tts(spreek(a), f"v{i:02d}{L[j].lower()}")
    print(i, end=" ", flush=True)

for name, text in {
    "goed": "Goed zo! Dat is juist.",
    "fout": "Dat is niet juist.",
    "tijd-om": "De tijd is om.",
    "welkom": "Welkom bij de herhalingsquiz verkeer. Hoofdstuk 1 tot en met 6. Luister naar de vraag. Kies dan A, B of C.",
    "einde": "Klaar! Goed gewerkt.",
    **{f"letter-{x.lower()}": f"{x}." for x in L},
    **{f"juist-{x.lower()}": f"Het juiste antwoord is {x}." for x in L},
}.items():
    tts(text, name)
print("\nklaar")
