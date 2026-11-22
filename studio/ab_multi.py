"""Blind test of 4 style versions on the same cards (21.11 evening: gloss / 3D-render look).

  python -m studio.ab_multi <out_dir>

ctrl = current prompts and refs; V1 = no "3D / animated-movie" wording; V2 = no glossy plastic
(no satin/highlights/glass wording, matte refs); V3 = V1 + V2. Same model, size, quality.
Each row shows the 4 versions as W/X/Y/Z in random order; the key is in blind_key.json.
"""
import json, random, sys, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw

from . import prompts, render, config
from .sheet import font
from .util import save_json, Usage

ROOT = Path(__file__).resolve().parent.parent
CARDS = [("space-opera", "Space Helmet"), ("heroic-fantasy", "Potion"), ("space-opera", "Pilot Seat"),
         ("wild-west", "Saddle"), ("space-opera", "Food Tray"), ("superheroes", "Hero Jet")]

NO_3D = [
    ("stylized 3D casual mobile game collectible card art, warm animated-movie look, ",
     "hand-painted casual mobile game collectible card illustration, digital painting with volume, "
     "looks painted by an artist, not a 3D render, "),
    ("style reference (rendering, materials,", "style reference (painting manner, materials,"),
    ("people, glossy plastic toy look,", "people, 3D render look, CGI, glossy plastic toy look,"),
]
NO_PLASTIC = [
    ("ceramic, glass, baked food)", "ceramic, baked food)"),
    ("matte or satin surfaces", "matte surfaces with painted brush shading"),
    ("gentle soft highlights,", "highlights only as a few soft pale painted strokes on rounded edges, no specular hotspots,"),
    ("glossy plastic toy look, wet shine, chrome or mirror reflections, neon glow.",
     "glossy plastic toy look, specular hotspots, reflections, wet shine, chrome, neon glow."),
    (" and a gentle light glow behind the object", ""),
]
MATTE_REFS = {
    1: ["clean/cat1_fanfold.png", "clean/cat1_honey.png", "arts/window_seafaring_anchor.png"],
    2: ["clean/cat2_lemontree.png", "arts/cat2_phone-booth_430x480.png", "clean/cat2_teacup.png"],
    3: ["arts/cat3_helm_430x480.png", "clean/cat3_pie.png", "arts/cat3_captains-cap_430x480.png"],
    4: ["arts/cat4_lighthouse_430x480.png", "clean/cat4_fieldball.png", "clean/cat4_antiquity.png"],
}
VERSIONS = {"ctrl": ([], False), "V1_no3d": (NO_3D, False), "V2_noplastic": (NO_PLASTIC, True),
            "V3_both": (NO_3D + NO_PLASTIC, True)}


def apply(p, reps, cat):
    for a, b in reps:
        if a in p:
            p = p.replace(a, b)
        elif not (a.startswith(" and a gentle") and cat != 3):
            raise ValueError(f"not found: {a!r}")
    return p


def main(out):
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    cards = []
    for g, n in CARDS:
        vs = json.loads((ROOT / f"night-2011/v3/sets/{g}.json").read_text())
        cards.append(next(c for c in vs[0]["cards"] if c["name"] == n))
    usage = Usage(); key = {}; jobs = []
    for i, c in enumerate(cards):
        order = list(VERSIONS); random.shuffle(order)
        key[f"{i+1}. {c['name']}"] = dict(zip("WXYZ", order))
        cat = int(c["category"])
        for lab, ver in zip("WXYZ", order):
            reps, matte = VERSIONS[ver]
            p = apply(prompts.build(c), reps, cat)
            refs = MATTE_REFS[cat] if matte else config.REFS[cat]
            jobs.append((c, lab, ver, p, refs, out / f"{i+1}_{lab}.png"))
    save_json(out / "blind_key.json", key)
    if "--dry" in sys.argv:
        save_json(out / "prompts.json", [dict(card=j[0]["name"], version=j[2], refs=j[4], prompt=j[3]) for j in jobs])
        print("dry ok", len(jobs), "jobs"); return
    t0 = time.time()
    with ThreadPoolExecutor(config.WORKERS) as ex:
        res = list(ex.map(lambda j: render.generate(j[3], j[0]["category"], j[5], usage, refs=j[4]), jobs))
    save_json(out / "log.json", dict(jobs=[dict(card=j[0]["name"], label=j[1], version=j[2], refs=j[4], prompt=j[3],
                                                file=j[5].name, result=r) for j, r in zip(jobs, res)],
                                     usage=usage.report(), sec=round(time.time() - t0)))
    W, H = 360, 400
    sheet = Image.new("RGB", (4 * (W + 10) + 10, len(cards) * (H + 50) + 50), "white"); d = ImageDraw.Draw(sheet)
    d.text((10, 10), "Blind style test: per row, which is closest to the reference cards? (W/X/Y/Z)", fill="black", font=font(22))
    for i, c in enumerate(cards):
        y = 50 + i * (H + 50)
        d.text((10, y), f"{i+1}. {c['name']} (cat {c['category']})", fill="black", font=font(20))
        for k, lab in enumerate("WXYZ"):
            f = out / f"{i+1}_{lab}.png"
            if f.exists():
                sheet.paste(Image.open(f).convert("RGB").resize((W, H)), (10 + k * (W + 10), y + 28))
            d.text((20 + k * (W + 10), y + 34), lab, fill="white", font=font(36))
    sheet.save(out / "sheet.png")
    print(out / "sheet.png", usage.report())


if __name__ == "__main__":
    main(sys.argv[1])
