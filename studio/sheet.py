"""Step 5. Contact sheets: set window (5x2), all candidates with judge scores, overview vs reference."""
from PIL import Image, ImageDraw, ImageFont
from . import config

W, H = 258, 288


def font(size, bold=False):
    for f in (f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if bold else ''}.ttf",
              "/System/Library/Fonts/Supplemental/Arial.ttf", "C:/Windows/Fonts/arial.ttf"):
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            pass
    return ImageFont.load_default(size=size)


def _rounded(im, r=20):
    m = Image.new("L", im.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, *im.size), r, fill=255)
    return m


def window(variant, finals, out):
    """finals: list of 10 paths (or None) in window order."""
    pad, plate, head = 18, 34, 92
    sheet = Image.new("RGB", (5 * (W + pad) + pad, head + 2 * (H + plate + pad) + pad), (236, 226, 205))
    d = ImageDraw.Draw(sheet)
    d.text((pad, 14), f"{variant['id']}. {variant['set_name']}", fill=(70, 45, 20), font=font(30, True))
    d.text((pad, 54), (variant.get("context") or variant.get("concept", ""))[:150], fill=(90, 70, 50), font=font(15))
    for i, (card, f) in enumerate(zip(variant["cards"], finals)):
        x = pad + (i % 5) * (W + pad); y = head + (i // 5) * (H + plate + pad)
        d.rounded_rectangle((x - 5, y - 5, x + W + 5, y + H + plate + 5), 22, fill=(255, 255, 255))
        if f:
            art = Image.open(f).convert("RGB")
            if abs(art.width / art.height - 0.9) > 0.02:  # e.g. square previews: centre-crop to 9:10
                nw = int(art.height * 0.9); art = art.crop(((art.width - nw) // 2, 0, (art.width - nw) // 2 + nw, art.height))
            art = art.resize((W, H), Image.LANCZOS)
            sheet.paste(art, (x, y), _rounded(art))
        else:
            d.rounded_rectangle((x, y, x + W, y + H), 20, outline="red", width=3)
            d.text((x + 20, y + 130), "NO IMAGE", fill="red", font=font(20, True))
        d.text((x + W // 2, y + H + plate // 2), card["name"], fill=(60, 40, 20), font=font(18, True), anchor="mm")
        d.text((x + 10, y + H - 26), f"cat {card['category']}", fill="white", font=font(13, True), stroke_width=2, stroke_fill="black")
    sheet.save(out)
    return out


def candidates(variant, rows, out):
    """rows: per card list of dicts {path, label, pass, chosen}."""
    w, h, pad, lbl = 172, 192, 8, 40
    ncol = max(len(r) for r in rows)
    sheet = Image.new("RGB", (220 + ncol * (w + pad) + pad, len(rows) * (h + lbl + pad) + 50), "white")
    d = ImageDraw.Draw(sheet)
    d.text((pad, 10), f"{variant['id']}. {variant['set_name']}: all candidates (green = chosen, red label = failed gate)", fill="black", font=font(18, True))
    for ri, (card, cands) in enumerate(zip(variant["cards"], rows)):
        y = 50 + ri * (h + lbl + pad)
        d.text((pad, y + 10), f"{card['n']}. {card['name']}", fill="black", font=font(15, True))
        d.text((pad, y + 32), f"cat {card['category']}, {card.get('bg_color','')}", fill="gray", font=font(13))
        for ci, c in enumerate(cands):
            x = 220 + ci * (w + pad)
            if c.get("path"):
                sheet.paste(Image.open(c["path"]).convert("RGB").resize((w, h)), (x, y))
            if c.get("chosen"):
                d.rectangle((x - 3, y - 3, x + w + 3, y + h + 3), outline=(0, 170, 0), width=5)
            d.text((x, y + h + 3), c.get("label", ""), fill=(0, 120, 0) if c.get("pass") else (200, 0, 0), font=font(12))
    sheet.save(out)
    return out


def overview(window_paths, out, title):
    ims = [Image.open(config.REF_DIR / config.REFERENCE_WINDOW).convert("RGB")] + [Image.open(p).convert("RGB") for p in window_paths]
    width = max(i.width for i in ims[1:])
    ref = ims[0]; ref = ref.resize((int(ref.width * 700 / ref.height), 700))
    ims[0] = ref
    total_h = 60 + sum(i.height + 40 for i in ims)
    sheet = Image.new("RGB", (max(width, ref.width) + 40, total_h), "white")
    d = ImageDraw.Draw(sheet); y = 10
    d.text((20, y), title, fill="black", font=font(28, True)); y += 50
    for k, im in enumerate(ims):
        d.text((20, y), "Reference: Amusement (Summer collection)" if k == 0 else "", fill="gray", font=font(16)); y += 30 if k == 0 else 0
        sheet.paste(im, (20, y)); y += im.height + 30
    sheet.crop((0, 0, sheet.width, y)).save(out)
    return out
