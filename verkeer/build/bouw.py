import json
from pathlib import Path
R = Path(__file__).resolve().parent.parent
v = json.loads((R/"build/vragen.json").read_text(encoding="utf-8"))
html = (R/"template.html").read_text(encoding="utf-8").replace("__VRAGEN__", json.dumps(v, ensure_ascii=False))
(R/"quiz.html").write_text(html, encoding="utf-8")                      # voor publicatie als artifact
(R/"index.html").write_text("<!doctype html>\n<html lang=\"nl\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n" + html + "\n</html>", encoding="utf-8")  # lokaal openen
