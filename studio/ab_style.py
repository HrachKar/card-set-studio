"""Blind A/B of two prompt versions on a few cards (same model, refs and size; only the prompt text differs).

  python -m studio.ab_style <old_prompts.py> <sets.json>:<card name> [...] <out_dir>

Each card gets one image per version. Versions are shown as X/Y in random order; the key is in blind_key.json.
"""
import importlib.util, json, random, sys, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw

from . import prompts as new_prompts, render
from .sheet import font
from .util import save_json, Usage


def load(path):
    spec = importlib.util.spec_from_file_location("old_prompts", path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def main(old_path, specs, out):
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    old = load(old_path)
    cards = []
    for s in specs:
        f, name = s.split(":", 1)
        vs = json.loads(Path(f).read_text())
        c = next(c for v in vs for c in v["cards"] if c["name"] == name)
        cards.append(c)
    usage = Usage(); key = {}; jobs = []
    for i, c in enumerate(cards):
        order = ["old", "new"]; random.shuffle(order)
        key[c["name"]] = {"X": order[0], "Y": order[1]}
        for lab, ver in zip("XY", order):
            p = (old if ver == "old" else new_prompts).build(c)
            jobs.append((c, lab, ver, p, out / f"{i+1}_{lab}.png"))
    save_json(out / "blind_key.json", key)
    t0 = time.time()
    with ThreadPoolExecutor(4) as ex:
        res = list(ex.map(lambda j: render.generate(j[3], j[0]["category"], j[4], usage), jobs))
    save_json(out / "log.json", dict(jobs=[dict(card=j[0]["name"], label=j[1], version=j[2], prompt=j[3], file=j[4].name, result=r)
                                           for j, r in zip(jobs, res)], usage=usage.report(), sec=round(time.time() - t0)))
    W, H = 432, 480
    sheet = Image.new("RGB", (2 * (W + 10) + 10, len(cards) * (H + 50) + 50), "white"); d = ImageDraw.Draw(sheet)
    d.text((10, 10), "Blind style A/B: pick X or Y per row (key in blind_key.json)", fill="black", font=font(22))
    for i, c in enumerate(cards):
        y = 50 + i * (H + 50)
        d.text((10, y), f"{i+1}. {c['name']} (cat {c['category']})", fill="black", font=font(20))
        for k, lab in enumerate("XY"):
            f = out / f"{i+1}_{lab}.png"
            if f.exists():
                sheet.paste(Image.open(f).convert("RGB").resize((W, H)), (10 + k * (W + 10), y + 28))
            d.text((20 + k * (W + 10), y + 34), lab, fill="white", font=font(36))
    sheet.save(out / "sheet.png")
    print(out / "sheet.png", usage.report())


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:-1], sys.argv[-1])
