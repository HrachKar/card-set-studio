"""Blind windows from a multi-version test: one 5x2 window per version, 6 generated cards mixed with 4 reference
cards. All images are cropped and brought to the same low resolution, so sharpness does not give them away.
  python -m studio.blind_windows runs/ab-style-02
"""
import json, random, sys
from pathlib import Path
from PIL import Image, ImageDraw
from .sheet import font
from . import config

REF_CARDS = [  # different reference cards in every window, one per category
    ["clean/cat1_pizza.png", "clean/cat2_sunblock.png", "clean/cat3_cheeseplate.png", "clean/cat4_lifeguard.png"],
    ["clean/cat1_lollipop.png", "clean/cat2_beachbag.png", "clean/cat3_basket.png", "clean/cat4_antiquity.png"],
    ["clean/cat1_fanfold.png", "clean/cat2_lemontree.png", "clean/cat3_pie.png", "clean/cat4_fieldball.png"],
    ["clean/cat1_honey.png", "clean/cat2_teacup.png", "clean/cat3_bumpers.png", "clean/cat4_lighthouse.png"],
]
ROT = int(__import__('os').environ.get('REF_CARDS_ROT', 0))
LOW = (186, 208); CARD = (430, 480)


def norm(path):
    im = Image.open(path).convert("RGB"); w, h = im.size
    m = int(w * 0.10)
    im = im.crop((m, m, w - m, h - m)).resize(LOW, Image.LANCZOS)
    return im.resize(CARD, Image.BICUBIC)


def main(run):
    run = Path(run); key = json.loads((run / "blind_key.json").read_text())
    versions = sorted({v for row in key.values() for v in row.values()})
    random.shuffle(versions)
    out_key = {}
    for wi, ver in enumerate(versions, 1):
        items = []
        for ri, (row, m) in enumerate(key.items(), 1):
            lab = next(l for l, v in m.items() if v == ver)
            items.append((f"ours: {row}", run / f"{ri}_{lab}.png"))
        items += [(f"Ref: {t}", config.REF_DIR / t) for t in REF_CARDS[(wi - 1 + ROT) % 4]]
        random.shuffle(items)
        g = 24; W = 5 * CARD[0] + 6 * g; H = 2 * (CARD[1] + 50) + 3 * g + 60
        sheet = Image.new("RGB", (W, H), (255, 231, 196)); d = ImageDraw.Draw(sheet)
        d.text((g, 18), f"Окно {wi}: какие карточки не из игры?", fill="black", font=font(34))
        for i, (_, p) in enumerate(items):
            x = g + (i % 5) * (CARD[0] + g); y = 70 + (i // 5) * (CARD[1] + 50 + g)
            d.rounded_rectangle((x - 8, y - 8, x + CARD[0] + 8, y + CARD[1] + 50), 24, fill=(120, 160, 230))
            sheet.paste(norm(p), (x, y))
            d.text((x + CARD[0] // 2 - 12, y + CARD[1] + 6), str(i + 1), fill="white", font=font(34))
        sheet.save(run / f"window_{wi}.png")
        out_key[f"Окно {wi}"] = dict(version=ver, cards={str(i + 1): n for i, (n, _) in enumerate(items)})
    (run / "windows_key.json").write_text(json.dumps(out_key, ensure_ascii=False, indent=1))
    print("ok", versions and len(versions))


if __name__ == "__main__":
    main(sys.argv[1])
