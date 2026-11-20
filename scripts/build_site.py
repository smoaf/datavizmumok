"""Build index.html from the template, the located artists and the land mask.

Usage (from the repo root):
    python3 scripts/build_site.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

artists = [a for a in json.loads((DATA / "artists_mumok_places_v2.json").read_text(encoding="utf-8"))
           if a.get("type", "person") == "person"]
known = sum(1 for a in artists if a["born_place"] and a["died_place"])
rows = [
    [a["who"], a["born"], a["died"], a["born_place"], a["died_place"], a["born_country"], a["died_country"],
     a["born_lat"], a["born_lon"], a["died_lat"], a["died_lon"], a["born_near"], a["died_near"]]
    for a in artists
    if a["born_lat"] is not None and a["died_lat"] is not None
]
map_data = json.dumps({"known": known, "rows": rows}, ensure_ascii=False, separators=(",", ":"))
(DATA / "map_data.json").write_text(map_data, encoding="utf-8")

mask = json.loads((DATA / "land_world1.json").read_text())["hex"]
template = (ROOT / "scripts" / "template.html").read_text(encoding="utf-8")
html = template.replace("__DATA__", map_data.replace("</", "<\\/")).replace("__MASK__", mask)
(ROOT / "index.html").write_text(html, encoding="utf-8")
print(f"index.html written: {len(rows)} artists on the map, {known} with both places on record")
