# B-in-zicht – herhalingsoefeningen

Digitale herhalingsquizzen met voorgelezen vragen en antwoorden.

| Quiz | Map | Vragen |
|---|---|---|
| Verkeer – hoofdstuk 1 t.e.m. 8 (les 1 t.e.m. 8) | `verkeer/` | 113 |

Online: https://kurtbraeye-pixel.github.io/B-in-zicht-herhalingsoefeningen/

## Wat de quiz doet

- Vragen en antwoorden worden voorgelezen met Piper (Vlaamse stem *nl_BE Nathalie*), in een trager tempo voor anderstaligen.
- Vragen en antwoorden komen telkens in een willekeurige volgorde.
- Oefen alle vragen of één les; op het einde kun je de foute vragen opnieuw oefenen.
- Timer per vraag (standaard 30 s; kies 20, 30, 45, 60 s of uit). De tijd loopt pas als het voorlezen klaar is.
- Werkt ook offline: open `index.html` in de map van een quiz.

## Hoe het in elkaar zit

```
engine/            gedeelde motor voor alle quizzen
  template.html    de quizpagina (opmaak en werking)
  bouw.py          maakt <quiz>/index.html
  maak_audio.py    maakt de voorgelezen audio met Piper
  voices/          de Piper-stem (niet in git, 126 MB)
<quiz>/
  quiz.json        titel, ondertitel, welkomsttekst, beschrijving van de afbeeldingen
  vragen.json      de vragen: les/thema, vraag, 3 antwoorden, juiste antwoord (0 = A), afbeelding
  images/          afbeelding-1.jpg, afbeelding-2.jpg, … en logo.png
  audio/           mp3-bestanden + teksten.json (welke tekst bij welk bestand hoort)
  index.html       gemaakt door bouw.py, niet met de hand aanpassen
```

## Iets aanpassen

1. Pas `vragen.json` of `quiz.json` aan (of zet een afbeelding in `images/` en geef de vraag `"img": <nummer>`).
2. Maak de audio die ontbreekt of veranderd is:
   ```bash
   python3 engine/maak_audio.py verkeer-les-7
   ```
   Alleen gewijzigde zinnen worden opnieuw ingesproken.
3. Bouw de pagina's opnieuw:
   ```bash
   python3 engine/bouw.py
   ```

Een verbetering aan `engine/template.html` geldt na `bouw.py` voor alle quizzen.

**Nieuwe quiz:** maak een map met `quiz.json`, `vragen.json`, `images/logo.png`, voer de twee stappen hierboven uit en zet een link in `index.html` in de hoofdmap.

**Stem installeren** (nodig voor `maak_audio.py`):
```bash
pip install piper-tts
```
Download `nl_BE-nathalie-medium.onnx` en `nl_BE-nathalie-medium.onnx.json` van
https://huggingface.co/rhasspy/piper-voices/tree/main/nl/nl_BE/nathalie/medium naar `engine/voices/`.
Ook `ffmpeg` moet geïnstalleerd zijn.
