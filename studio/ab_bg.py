"""ab-style-03: softer backgrounds + tighter framing, and micro-contrast post-processing.
Reuses the ctrl images of ab-style-02 (no new cost for them); generates only the 'new' prompt version.
  python -m studio.ab_bg runs/ab-style-02 runs/ab-style-03 [--dry]
"""
import json, random, re, shutil, sys, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from . import prompts, render, config
from .ab_multi import CARDS, ROOT
from .post import microcontrast
from .util import save_json, Usage


def soften(p):
    reps = [("fills about 75% of the width", "fills about 85% of the width, almost touching the side edges"),
            ("background slightly softer", "background clearly softer and less saturated than the object")]
    for a, b in reps:
        assert a in p, a; p = p.replace(a, b)
    p = re.sub(r"a saturated (.+?) wall", r"a soft, slightly muted \1 wall, lighter than the object", p)
    p = p.replace("bright and cheerful", "cheerful")
    p = re.sub(r"Plain background: (.+?) with soft gradient", r"Plain background: soft, slightly muted \1 with soft gradient", p)
    p = re.sub(r"plain vertical (.+?) wall", r"plain vertical soft, slightly muted \1 wall", p)
    return p


def main(src, out):
    src, out = Path(src), Path(out); out.mkdir(parents=True, exist_ok=True)
    k2 = json.loads((src / "blind_key.json").read_text())
    cards = []
    for g, n in CARDS:
        vs = json.loads((ROOT / f"night-2011/v3/sets/{g}.json").read_text())
        cards.append(next(c for c in vs[0]["cards"] if c["name"] == n))
    usage = Usage(); key = {}; jobs = []; log = []
    for i, c in enumerate(cards):
        row = f"{i+1}. {c['name']}"
        ctrl_lab = next(l for l, v in k2[row].items() if v == "ctrl")
        order = ["ctrl", "ctrl_post", "new", "new_post"]; random.shuffle(order)
        key[row] = dict(zip("WXYZ", order)); lab = {v: l for l, v in key[row].items()}
        shutil.copy(src / f"{i+1}_{ctrl_lab}.png", out / f"{i+1}_{lab['ctrl']}.png")
        microcontrast(Image.open(src / f"{i+1}_{ctrl_lab}.png")).save(out / f"{i+1}_{lab['ctrl_post']}.png")
        p = soften(prompts.build(c)); log.append(dict(card=c["name"], prompt=p))
        jobs.append((c, p, out / f"{i+1}_{lab['new']}.png", out / f"{i+1}_{lab['new_post']}.png"))
    save_json(out / "blind_key.json", key)
    if "--dry" in sys.argv:
        save_json(out / "prompts.json", log); print("dry ok"); return
    t0 = time.time()
    with ThreadPoolExecutor(config.WORKERS) as ex:
        res = list(ex.map(lambda j: render.generate(j[1], j[0]["category"], j[2], usage), jobs))
    for j, r in zip(jobs, res):
        if j[2].exists():
            microcontrast(Image.open(j[2])).save(j[3])
    save_json(out / "log.json", dict(jobs=log, results=res, usage=usage.report(), sec=round(time.time() - t0)))
    print(usage.report())


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
