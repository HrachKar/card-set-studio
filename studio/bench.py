"""Cheap model bake-off on a few cards of an existing run, with the CURRENT prompts.

  python -m studio bench --from runs/ww-01 --cards A4,A6,B3,B5 --name bench-02 [--models gpt2-high,nb2]

Real cost per image is computed from the usage the API returns (prices below, USD per 1M tokens).
Output: runs/<name>/  images, log.json, sheet.png (rows = models with $/image and seconds).
"""
import base64, io, json, os, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from PIL import Image, ImageDraw

from . import config, prompts, pipeline
from .sheet import font

# provider, model id, quality, price per 1M tokens: (image out, image in, text in)
MODELS = {
    "gpt2-high":      ("openai", "gpt-image-2", "high", (30, 8, 5)),
    "gpt2-med":       ("openai", "gpt-image-2", "medium", (30, 8, 5)),
    "gpt25f-med":     ("openai", "gpt-image-2.5-flare", "medium", (30, 8, 5)),
    "gpt25s-med":     ("openai", "gpt-image-2.5-sunburst", "medium", (30, 8, 5)),
    "gpt26f-med":     ("openai", "gpt-image-2.6-flare", "medium", (30, 8, 5)),
    "gpt26s-med":     ("openai", "gpt-image-2.6-sunburst", "medium", (30, 8, 5)),
    "gpt26f-high":    ("openai", "gpt-image-2.6-flare", "high", (30, 8, 5)),
    "gpt1mini-med":   ("openai", "gpt-image-1-mini", "medium", (8, 2.5, 2)),
    "nbpro":          ("gemini", "gemini-3-pro-image", None, (120, 2, 2)),
    "nb2":            ("gemini", "gemini-3.1-flash-image", None, (60, 0.5, 0.5)),
}


def run_openai(model, quality, prompt, cat):
    from openai import OpenAI
    files = [open(config.REF_DIR / r, "rb") for r in config.REFS[cat]]
    try:
        try:
            r = OpenAI().images.edit(model=model, image=files, prompt=prompt, size=config.IMAGE_SIZE, quality=quality)
        except Exception as e:
            if "size" not in str(e).lower():
                raise
            for f in files: f.seek(0)
            r = OpenAI().images.edit(model=model, image=files, prompt=prompt, size="1024x1024", quality=quality)
    finally:
        for f in files: f.close()
    u = r.usage; det = getattr(u, "input_tokens_details", None)
    toks = (u.output_tokens or 0, getattr(det, "image_tokens", 0) or 0, getattr(det, "text_tokens", 0) or 0)
    return base64.b64decode(r.data[0].b64_json), toks


def run_gemini(model, prompt, cat):
    from google import genai
    from google.genai import types
    c = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    parts = [Image.open(config.REF_DIR / r) for r in config.REFS[cat]] + [prompt]
    r = c.models.generate_content(model=model, contents=parts, config=types.GenerateContentConfig(
        response_modalities=["IMAGE"], image_config=types.ImageConfig(aspect_ratio="4:5")))
    um = r.usage_metadata
    for p in r.candidates[0].content.parts:
        if p.inline_data:
            return p.inline_data.data, (um.candidates_token_count or 0, um.prompt_token_count or 0, 0)
    raise RuntimeError("no image returned")


def fit_9x10(raw):
    im = Image.open(io.BytesIO(raw)).convert("RGB"); w, h = im.size
    if w / h > 0.9:
        nw = int(h * 0.9); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = int(w / 0.9); im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    return im


def bench(src, card_ids, name, models=None, blind=False):
    models = models or list(MODELS)
    sets, _ = pipeline.load_state(Path(src))
    cards = []
    for cid in card_ids:
        v = next(v for v in sets if v["id"] == cid[0].upper())
        c = next(c for c in v["cards"] if int(c["n"]) == int(cid[1:]))
        cards.append((cid, c, pipeline.card_dir(Path(src), v["id"], c) / "final.png"))
    out = config.RUNS_DIR / name; out.mkdir(parents=True, exist_ok=True)

    prev = {}
    if (out / "log.json").exists():  # reuse images already made in this bench (add cards/models cheaply)
        prev = {(r["model"], r["card"]): r for r in json.load(open(out / "log.json"))["results"] if r.get("file")}

    def job(t):
        m, (cid, c, _) = t
        if (m, cid) in prev and (out / prev[(m, cid)]["file"]).exists():
            return prev[(m, cid)]
        prov, mid, q, price = MODELS[m]
        p = prompts.build(c); t0 = time.time()
        try:
            for attempt in range(6):  # org limit: 20 input images/min for gpt-image (3 refs per call)
                try:
                    raw, toks = run_openai(mid, q, p, int(c["category"])) if prov == "openai" else run_gemini(mid, p, int(c["category"]))
                    break
                except Exception as e:
                    if "429" not in str(e) or attempt == 5:
                        raise
                    time.sleep(20 + 10 * attempt)
            f = out / f"{m}_{cid}.png"; fit_9x10(raw).save(f)
            usd = sum(a * b for a, b in zip(toks, price)) / 1e6
            return dict(model=m, card=cid, file=f.name, sec=round(time.time() - t0, 1), tokens=toks, usd=round(usd, 4), prompt=p)
        except Exception as e:
            return dict(model=m, card=cid, error=str(e)[:300], sec=round(time.time() - t0, 1), prompt=p)

    with ThreadPoolExecutor(12) as ex:
        res = list(ex.map(job, [(m, c) for m in models for c in cards]))
    for r in res:
        print({k: v for k, v in r.items() if k != "prompt"})
    json.dump(dict(source=str(src), cards=card_ids, models={m: MODELS[m][:3] for m in models}, results=res),
              open(out / "log.json", "w"), indent=1, ensure_ascii=False)
    make_sheet(out, cards, models, res)
    if blind:
        blind_windows(out, sets, card_ids, models, res)
    print(out / "sheet.png")


def blind_windows(out, sets, card_ids, models, res):
    """Blind A/B: every set variant is drawn once per model as a game window, labelled X, Y, ... in random order.
    The key (which letter is which model) goes to blind_key.json; look at it only after choosing."""
    import random
    from .sheet import window
    letters = [chr(88 + i) if i < 3 else chr(65 + i) for i in range(len(models))]  # X, Y, Z, D...
    order = models[:]; random.shuffle(order)
    key = dict(zip(letters, order))
    json.dump(key, open(out / "blind_key.json", "w"), indent=1)
    for v in sets:
        ids = [f"{v['id']}{c['n']}" for c in v["cards"]]
        if not all(i in card_ids for i in ids):
            continue
        for L, m in key.items():
            files = []
            for i in ids:
                r = next((r for r in res if r["model"] == m and r["card"] == i and r.get("file")), None)
                files.append(out / r["file"] if r else None)
            vv = {**v, "id": f"{v['id']}-{L}", "concept": f"Blind version {L}"}
            window(vv, files, out / f"blind_{v['id']}_{L}.png")


def make_sheet(out, cards, models, res):
    W, H, pad, lab = 240, 267, 8, 250
    seen = {}
    def ref(cat):
        k = seen[cat] = seen.get(cat, -1) + 1
        return config.REF_DIR / config.JUDGE_REFS[cat][k % len(config.JUDGE_REFS[cat])]
    rows = [("Reference (game),\nsame category", [ref(int(c['category'])) for _, c, _ in cards], ""),
            ("Previous run (ww-01, old prompt)", [p for _, _, p in cards], "")]
    for m in models:
        rs = [next((r for r in res if r["model"] == m and r["card"] == cid), {}) for cid, _, _ in cards]
        ok = [r for r in rs if r.get("usd") is not None]
        info = (f"${sum(r['usd'] for r in ok)/len(ok):.3f}/img, {sum(r['sec'] for r in ok)/len(ok):.0f} s" if ok else "failed")
        rows.append((f"{m}\n{MODELS[m][1]} {MODELS[m][2] or ''}".strip(), [out / r["file"] if r.get("file") else None for r in rs], info))
    sheet = Image.new("RGB", (lab + len(cards) * (W + pad) + pad, 50 + len(rows) * (H + pad) + pad), "white")
    d = ImageDraw.Draw(sheet)
    for ci, (cid, c, _) in enumerate(cards):
        d.text((lab + ci * (W + pad), 14), f"{cid} {c['name']} (cat {c['category']})", fill="black", font=font(16, True))
    for ri, (title, files, info) in enumerate(rows):
        y = 50 + ri * (H + pad)
        d.text((10, y + 10), f"{ri - 1}. " + title if ri >= 2 else title, fill="black", font=font(15, True))
        d.text((10, y + 80), info, fill=(0, 100, 0), font=font(18, True))
        for ci, f in enumerate(files):
            x = lab + ci * (W + pad)
            if f and Path(f).exists():
                sheet.paste(Image.open(f).convert("RGB").resize((W, H)), (x, y))
            else:
                d.rectangle((x, y, x + W, y + H), outline="red", width=2); d.text((x + 10, y + 120), "FAILED", fill="red", font=font(18))
    sheet.save(out / "sheet.png")
