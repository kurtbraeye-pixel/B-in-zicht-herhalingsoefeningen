"""Bouw de quizpagina('s): engine/template.html + <map>/quiz.json + <map>/vragen.json -> <map>/index.html

Gebruik:  python3 engine/bouw.py            (alle quizmappen)
          python3 engine/bouw.py verkeer-les-7
"""
import html, json, sys
from pathlib import Path

ENGINE = Path(__file__).resolve().parent
ROOT = ENGINE.parent

def quizmappen():
    return sorted(p.parent for p in ROOT.glob("*/quiz.json"))

def bouw(map_: Path):
    quiz = json.loads((map_ / "quiz.json").read_text(encoding="utf-8"))
    vragen = json.loads((map_ / "vragen.json").read_text(encoding="utf-8"))
    t = (ENGINE / "template.html").read_text(encoding="utf-8")
    t = t.replace("__TITEL__", html.escape(quiz["titel"]))
    # </ in JSON onschadelijk maken binnen <script>
    js = lambda o: json.dumps(o, ensure_ascii=False).replace("</", "<\\/")
    t = t.replace("__QUIZ__", js(quiz)).replace("__VRAGEN__", js(vragen))
    (map_ / "index.html").write_text(
        '<!doctype html>\n<html lang="nl"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n' + t + "\n</html>",
        encoding="utf-8")
    print(f"{map_.name}: {len(vragen)} vragen")

if __name__ == "__main__":
    mappen = [ROOT / a for a in sys.argv[1:]] or quizmappen()
    for m in mappen:
        bouw(m)
