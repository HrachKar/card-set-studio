"""Blind recognition + geometry check (judge v3 candidate).

The judge sees ONLY the image (not the requested object), names the object and lists geometry defects.
A second text call checks whether its guess matches the requested object.
  python -m studio.blindcheck runs/ww-02 runs/ww-03 runs/final-wild-west
"""
import json, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from openai import OpenAI

from . import config, pipeline
from .judge import _img
from .util import save_json, Usage

BLIND = """You see one collectible card illustration from a casual mobile game. You are NOT told what it should be.
1. guess: name the single main object in 1-4 words, as a player would.
2. Inspect the geometry very carefully, like a 3D artist checking a model. List every defect:
   merged or fused parts, extra or missing parts (e.g. 3 wheels, a handle growing out of the wrong place), asymmetric pairs
   (two boots of different shape, wheels of different size), melted or warped forms, parts floating unconnected,
   an object that does not exist in real life, impossible construction, any text or digits.
3. distortion: "none", "minor" (visible only when you look closely) or "severe" (a player notices it at a glance).
Return JSON: {"guess": "...", "defects": ["..."], "distortion": "none|minor|severe"}"""


def check(path, card, usage):
    c = OpenAI()
    r = c.responses.create(model=config.TEXT_MODEL, reasoning={"effort": "medium"}, text={"format": {"type": "json_object"}},
                           input=[{"role": "system", "content": BLIND}, {"role": "user", "content": [_img(path, 768)]}])
    usage.add_llm(r.usage)
    out = json.loads(r.output_text)
    m = c.responses.create(model=config.TEXT_MODEL, reasoning={"effort": "low"}, text={"format": {"type": "json_object"}},
                           input=f'Requested object: "{card["object"]}" (name "{card["name"]}"). A viewer who did not know '
                                 f'the request said it is: "{out.get("guess")}". Is that the same kind of object? Return JSON {{"match": true|false}}')
    usage.add_llm(m.usage)
    out["match"] = bool(json.loads(m.output_text).get("match"))
    return out


def run(run_dirs):
    usage = Usage(); summary = {}
    for rd in map(Path, run_dirs):
        sets, _ = pipeline.load_state(rd)
        jobs = [(v, c, pipeline.card_dir(rd, v["id"], c) / "final.png") for v in sets for c in v["cards"]]
        jobs = [j for j in jobs if j[2].exists()]
        with ThreadPoolExecutor(10) as ex:
            res = list(ex.map(lambda j: dict(card=f"{j[0]['id']}{j[1]['n']}", name=j[1]["name"], **check(j[2], j[1], usage)), jobs))
        save_json(rd / "blindcheck.json", res)
        s = dict(cards=len(res), severe=sum(r["distortion"] == "severe" for r in res),
                 minor=sum(r["distortion"] == "minor" for r in res), not_recognized=sum(not r["match"] for r in res))
        summary[rd.name] = s
        print(rd.name, s)
        for r in res:
            if r["distortion"] != "none" or not r["match"]:
                print("   ", r["card"], r["name"], "| guess:", r["guess"], "|", r["distortion"], "|", "; ".join(r["defects"])[:160])
    print("usage", usage.report())
    return summary


if __name__ == "__main__":
    run(sys.argv[1:])
