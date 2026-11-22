"""Experiment: "reskin" a real game card instead of describing the whole scene.

Image 1 = a finished reference card of the same category; the model replaces ONLY the object
(and adapts the surface/environment) and keeps lighting, camera, framing and rendering.
  python -m studio.reskin runs/final-wild-west A7,B7,A9,C2 runs/exp-reskin
"""
import base64, io, json, sys, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI
from PIL import Image

from . import config, pipeline, blindcheck
from .util import save_json, Usage

BASE = {3: ["arts/cat3_helm_430x480.png", "arts/cat3_captains-cap_430x480.png"],
        4: ["arts/cat4_lighthouse_430x480.png", "clean/cat4_antiquity.png"]}


def prompt(c):
    where = c.get("surface") or c.get("environment") or ""
    return ("Image 1 is a finished card illustration from the game. Edit it: replace ONLY the main object with "
            f"{c['object']}. Change the {'surface' if c.get('surface') else 'environment'} to: {where}, in the same "
            "simplified style. Keep exactly: the rendering style, lighting, camera angle, the object's size and position in the frame, "
            "the depth of field and the amount of detail. The new object must be complete, symmetric and physically correct, "
            "no extra or fused parts. No text, no people, no animals.")


def run(src, ids, out):
    src, out = Path(src), Path(out); out.mkdir(parents=True, exist_ok=True)
    sets, _ = pipeline.load_state(src); u = Usage(); jobs = []
    for cid in ids:
        v = next(v for v in sets if v["id"] == cid[0]); c = next(c for c in v["cards"] if int(c["n"]) == int(cid[1:]))
        for k, base in enumerate(BASE[int(c["category"])]):
            jobs.append((cid, c, k, base, pipeline.card_dir(src, v["id"], c) / "final.png"))

    def job(j):
        cid, c, k, base, old = j; p = prompt(c); t = time.time()
        with open(config.REF_DIR / base, "rb") as f:
            r = OpenAI().images.edit(model=config.IMAGE_MODEL, image=[f], prompt=p, size=config.IMAGE_SIZE, quality=config.IMAGE_QUALITY)
        u.add_image(r.usage)
        dst = out / f"{cid}_reskin{k}.png"
        Image.open(io.BytesIO(base64.b64decode(r.data[0].b64_json))).convert("RGB").save(dst)
        b_new = blindcheck.check(dst, c, u); b_old = blindcheck.check(old, c, u)
        return dict(card=cid, name=c["name"], base=base, prompt=p, file=dst.name, sec=round(time.time() - t),
                    new=b_new, old=b_old)
    with ThreadPoolExecutor(4) as ex:
        res = list(ex.map(job, jobs))
    save_json(out / "log.json", dict(results=res, usage=u.report()))
    # sheet: per card -> old final | reskin 0 | reskin 1
    from .sheet import font
    from PIL import ImageDraw
    W, H = 300, 333
    sheet = Image.new("RGB", (3 * (W + 10) + 10, len(ids) * (H + 60) + 50), "white"); d = ImageDraw.Draw(sheet)
    d.text((10, 10), "old pipeline | reskin from game card (base 1) | reskin (base 2)", fill="black", font=font(18, True))
    for i, cid in enumerate(ids):
        y = 50 + i * (H + 60)
        rs = [r for r in res if r["card"] == cid]
        old = rs[0]["old"]; files = [None] + rs
        for k, r in enumerate(files):
            x = 10 + k * (W + 10)
            if k == 0:
                v = next(v for v in sets if v["id"] == cid[0]); c = next(c for c in v["cards"] if int(c["n"]) == int(cid[1:]))
                im = Image.open(pipeline.card_dir(src, v["id"], c) / "final.png"); b = old
            else:
                im = Image.open(out / r["file"]); b = r["new"]
            sheet.paste(im.convert("RGB").resize((W, H)), (x, y))
            d.text((x, y + H + 4), f"{cid} {b['distortion']}, {len(b['defects'])} defects, {'recognized' if b['match'] else 'NOT recognized'}",
                   fill=(0, 120, 0) if b["distortion"] == "none" else (200, 0, 0), font=font(13))
    sheet.save(out / "sheet.png")
    print(out / "sheet.png", u.report())


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2].split(","), sys.argv[3])
