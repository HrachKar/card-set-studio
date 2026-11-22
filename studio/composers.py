"""Blind comparison of composer models (the LLM that picks objects and places).

  python -m studio composers --theme "Wild West" --models gpt-5.5,gpt-5.4-mini,gemini-3.5-flash --variants 2 --name comp-01

Each model composes the sets (draft + code check + critic). Then every card gets ONE cheap preview image
(gpt-image-1-mini, ~$0.01) with the same prompts, so the human judges objects and places, not rendering.
Windows are labelled with random letters; the key is in blind_key.json.
"""
import json, random, time
from concurrent.futures import ThreadPoolExecutor

from . import config, prompts, render, sheet
from .compose import compose
from .util import save_json, Usage

PREVIEW = ("gpt-image-1-mini", "medium", "1024x1024")


def run(theme, wishes, models, n_variants, name, places=None):
    out = config.RUNS_DIR / name; out.mkdir(parents=True, exist_ok=True)
    letters = [chr(80 + i) for i in range(len(models))]  # P, Q, R...
    order = models[:]; random.shuffle(order)
    key = dict(zip(letters, order))
    save_json(out / "blind_key.json", key)
    if places:  # same sub-themes for every composer, otherwise the models are not comparable
        n_variants = len(places)
        wishes = (wishes + "\n" if wishes else "") + "Make exactly these variants, in this order, one place each: " + \
            "; ".join(f"{chr(65+i)} = {p}" for i, p in enumerate(places)) + ". Keep these places, do not swap them for others."
    save_json(out / "request.json", dict(theme=theme, wishes=wishes, places=places, models=models, variants=n_variants, preview=PREVIEW))
    usage = {m: Usage() for m in models}
    t0 = time.time()

    def comp(m):
        L = next(l for l, mm in key.items() if mm == m)
        if m.startswith("file:"):  # sets composed by Claude Code itself inside the skill (no API call)
            from .compose import validate
            vs = json.loads(open(m[5:]).read())
            save_json(out / L / "compose" / "sets.json", vs)
            save_json(out / L / "compose" / "validation.json", validate(vs, n_variants))
            return L, vs
        try:
            return L, compose(theme, wishes, n_variants, out / L, usage[m], model=m)
        except Exception as e:
            print(f"[{m}] compose failed: {e}"); return L, None
    with ThreadPoolExecutor(len(models)) as ex:
        sets = dict(ex.map(comp, models))
    print(f"[composers] composed in {time.time()-t0:.0f}s")

    config.IMAGE_MODEL, config.IMAGE_QUALITY, config.IMAGE_SIZE = PREVIEW
    img_usage = Usage()
    jobs = []
    for L, vs in sets.items():
        for v in vs or []:
            for c in v["cards"]:
                d = out / L / "cards" / v["id"]; d.mkdir(parents=True, exist_ok=True)
                jobs.append((c, d / f"{int(c['n']):02d}.png"))
    with ThreadPoolExecutor(config.WORKERS) as ex:
        list(ex.map(lambda j: render.generate(prompts.build(j[0]), j[0]["category"], j[1], img_usage), jobs))
    for L, vs in sets.items():
        for v in vs or []:
            files = [out / L / "cards" / v["id"] / f"{int(c['n']):02d}.png" for c in v["cards"]]
            vv = {**v, "id": f"{L}{v['id']}", "concept": f"[{v.get('place','')}] {v.get('concept','')}"}
            sheet.window(vv, [f if f.exists() else None for f in files], out / f"window_{L}{v['id']}.png")
    cost = {key_l: usage[m].report() for key_l, m in key.items()}
    save_json(out / "usage.json", dict(composers=cost, preview_images=img_usage.report()))
    # one readable text file per letter, for the report and for reading without images
    for L, vs in sets.items():
        lines = [f"# Composer {L}", ""]
        for v in vs or []:
            lines += [f"## {L}{v['id']}. {v['set_name']}", f"Place: {v.get('place','')}", ""]
            lines += [f"{c['n']}. **{c['name']}** (cat {c['category']}): {c['object']} — marker: {c.get('theme_marker','')}"
                      + (f" — on {c['surface']}" if c.get('surface') else "") + (f" — in {c['environment']}" if c.get('environment') else "")
                      for c in v["cards"]]
            lines.append("")
        (out / f"sets_{L}.md").write_text("\n".join(lines))
    print(f"[done] {out}  composers: " + ", ".join(f"{l}=${c['usd_estimate']}" for l, c in cost.items())
          + f"  previews: ${img_usage.usd()}  {time.time()-t0:.0f}s")
