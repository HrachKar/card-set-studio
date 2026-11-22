"""Orchestration: compose -> prompts -> parallel generation -> quality gate -> sheets -> report.

Run folder layout (everything is kept for transparency):
  request.json                 theme, wishes, settings
  compose/attempt_N.json       composer prompt, answer, rule violations
  compose/sets.json            final set compositions
  cards/<V>/<NN>_<name>/       prompt_rK.txt, rK_i.png (every candidate), judge_rK.json, final.png, final_430x480.png
  sheets/window_<V>.png        set as it looks in the 5x2 window
  sheets/candidates_<V>.png    every candidate with scores, chosen one in green
  sheets/overview.png          all variants under the reference set
  state.json, usage.json, report.md
"""
import json, shutil, time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

from . import config, prompts, render, judge, sheet
from .compose import compose
from .util import save_json, slug, Usage

IMG_POOL = None


def img_pool():
    global IMG_POOL
    if IMG_POOL is None:
        IMG_POOL = ThreadPoolExecutor(config.WORKERS)
    return IMG_POOL


def card_dir(run_dir, vid, card):
    return run_dir / "cards" / vid / f"{int(card['n']):02d}_{slug(card['name'])}"


def process_card(run_dir, vid, card, usage, rounds=None, start_round=1, note=""):
    """Generate + judge one card until a candidate passes or rounds run out. Mutates card['history']."""
    d = card_dir(run_dir, vid, card); d.mkdir(parents=True, exist_ok=True)
    hist = card.setdefault("history", [])
    fix = note
    for rnd in range(start_round, start_round + (rounds or config.MAX_ROUNDS)):
        p = prompts.build(card, fix)
        (d / f"prompt_r{rnd}.txt").write_text(p)
        futs = [img_pool().submit(render.generate, p, card["category"], d / f"r{rnd}_{i}.png", usage)
                for i in range(config.CANDIDATES)]
        gens = [f.result() for f in futs]
        ok = [d / g["file"] for g in gens if g.get("file")]
        entry = dict(round=rnd, prompt=p, gens=gens, judge=None)
        if ok:
            try:
                entry["judge"] = judge.judge(card, ok, usage)
                entry["judged_files"] = [x.name for x in ok]
                # blind check: a second judge that is NOT told the request names the object and hunts geometry defects
                from . import blindcheck
                blinds = list(ThreadPoolExecutor(len(ok)).map(lambda p: blindcheck.check(p, card, usage), ok))
                for i, b in enumerate(blinds):
                    cj = next((c for c in entry["judge"].get("candidates", []) if c.get("id") == chr(65 + i)), None)
                    if cj is None:
                        continue
                    cj["blind"] = b
                    if not b.get("match"):
                        cj["hard"].append("not_recognized_blind")
                    if b.get("distortion") == "severe":
                        cj["hard"].append("severe_distortion")
                    cj["minor_defects"] = len(b.get("defects", [])) if b.get("distortion") == "minor" else 0
                    cj["pass"] = cj["pass"] and not cj["hard"]
            except Exception as e:
                entry["judge_error"] = str(e)[:300]
        save_json(d / f"judge_r{rnd}.json", entry)
        hist.append(entry)
        if entry["judge"] and any(c.get("pass") for c in entry["judge"].get("candidates", [])):
            break
        fix = (entry.get("judge") or {}).get("fix") or fix
        print(f"[{vid}{card['n']} {card['name']}] round {rnd}: nothing passed, fix: {fix}")
    choose(d, card)
    return card


def all_candidates(d, card):
    out = []
    for e in card.get("history", []):
        js = {c["id"]: c for c in (e.get("judge") or {}).get("candidates", [])}
        for i, f in enumerate(e.get("judged_files", [])):
            j = js.get(chr(65 + i), {})
            out.append(dict(path=d / f, round=e["round"], mean=j.get("mean", 0), pass_=j.get("pass", False),
                            hard=j.get("hard", []), comment=j.get("comment", ""), minor=j.get("minor_defects", 0)))
        for g in e["gens"]:  # generated but not judged (judge failed)
            if g.get("file") and g["file"] not in e.get("judged_files", []):
                out.append(dict(path=d / g["file"], round=e["round"], mean=0, pass_=False, hard=["not_judged"], comment=""))
    return out


def choose(d, card):
    cands = all_candidates(d, card)
    if card.get("pinned"):  # designer picked a file by hand
        best = next((c for c in cands if c["path"].name == card["pinned"]), None)
    else:
        best = max(cands, key=lambda c: (c["pass_"], c["round"], -c.get("minor", 0), c["mean"]), default=None)  # newest passing round wins (regen = designer asked for new)
    card["final"] = None
    if best:
        shutil.copy(best["path"], d / "final.png")
        render.to_game_size(d / "final.png", d / "final_430x480.png")
        card["final"] = dict(file=best["path"].name, score=best["mean"], passed=best["pass_"], hard=best["hard"])


def build_sheets(run_dir, variants):
    (run_dir / "sheets").mkdir(exist_ok=True)
    wins = []
    for v in variants:
        finals, rows = [], []
        for c in v["cards"]:
            d = card_dir(run_dir, v["id"], c)
            finals.append(d / "final.png" if (d / "final.png").exists() else None)
            chosen = (c.get("final") or {}).get("file")
            rows.append([dict(path=x["path"], chosen=x["path"].name == chosen, **{"pass": x["pass_"]},
                              label=f"r{x['round']} {x['mean']:.1f} {'PASS' if x['pass_'] else 'fail ' + ','.join(x['hard'])[:22]}")
                         for x in all_candidates(d, c)])
        wins.append(sheet.window(v, finals, run_dir / "sheets" / f"window_{v['id']}.png"))
        sheet.candidates(v, rows, run_dir / "sheets" / f"candidates_{v['id']}.png")
    req = json.loads((run_dir / "request.json").read_text())
    sheet.overview(wins, run_dir / "sheets" / "overview.png", f"Theme: {req['theme']}")
    export_zip(run_dir, variants)


def export_zip(run_dir, variants):
    """One archive for the designer: every final card as a separate PNG (full size and game size), all sheets, the report."""
    import zipfile
    out = run_dir / f"{run_dir.name}_cards.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_STORED) as z:
        for v in variants:
            for c in v["cards"]:
                d = card_dir(run_dir, v["id"], c)
                stem = f"{v['id']}{int(c['n']):02d}_{slug(c['name'])}"
                if (d / "final.png").exists():
                    z.write(d / "final.png", f"cards/{stem}.png")
                if (d / "final_430x480.png").exists():
                    z.write(d / "final_430x480.png", f"cards_game_size/{stem}_430x480.png")
        for f in sorted((run_dir / "sheets").glob("*.png")):
            z.write(f, f"sheets/{f.name}")
        for f in ("report.md", "review_sets.md", "review_prompts.md"):
            if (run_dir / f).exists():
                z.write(run_dir / f, f)
    print(f"[export] {out}")
    return out


def write_report(run_dir, variants, usage, elapsed=None):
    req = json.loads((run_dir / "request.json").read_text())
    L = [f"# {req['theme']}", "", f"Wishes: {req.get('wishes') or '-'}  ", f"Run: `{run_dir.name}`, models: {config.TEXT_MODEL} + {config.IMAGE_MODEL}  "]
    u = usage.report()
    L.append(f"Images generated: {u['images']}, LLM calls: {u['llm_calls']}, cost estimate: ~${u['usd_estimate']}"
             + (f", time: {elapsed/60:.1f} min" if elapsed else ""))
    L += ["", "![overview](sheets/overview.png)", ""]
    for v in variants:
        L += [f"## {v['id']}. {v['set_name']}", "", f"**Context:** {v.get('context', '')}", "", v.get("concept", ""), "", f"Palette: {v.get('palette','')}. Motif: {v.get('motif','')}.", "",
              f"![window](sheets/window_{v['id']}.png)", "", f"All candidates: [candidates_{v['id']}.png](sheets/candidates_{v['id']}.png)", "",
              "| # | Name | Cat | Object | Moment in the day | Background | Score | Gate | Rounds |", "|---|---|---|---|---|---|---|---|---|"]
        for c in v["cards"]:
            f = c.get("final") or {}
            bg = c.get("environment") if int(c["category"]) == 4 else f"{c.get('bg_color','')}, {c.get('bg_treatment','')}" + (f" / {c['surface']}" if c.get("surface") else "")
            L.append(f"| {c['n']} | {c['name']} | {c['category']} | {c['object']} | {c.get('moment', '')} | {bg} | {f.get('score','-')} | "
                     f"{'pass' if f.get('passed') else 'FAIL ' + ','.join(f.get('hard', []))} | {len(c.get('history', []))} |")
        L.append("")
    (run_dir / "report.md").write_text("\n".join(L))
    save_json(run_dir / "usage.json", u)


def save_state(run_dir, variants, usage):
    save_json(run_dir / "state.json", dict(variants=variants, usage=usage.d))


def load_state(run_dir):
    s = json.loads((run_dir / "state.json").read_text())
    u = Usage(); u.d.update(s.get("usage", {}))
    return s["variants"], u


def write_review(run_dir, sets):
    """Checkpoint files for a human: the object list and the exact image prompts (no API calls)."""
    from . import prompts
    lines = ["# Sets for review", ""]
    for v in sets:
        lines += [f"## {v['id']}. {v.get('set_name','')}", f"Context: {v.get('context','')}", f"Places: {v.get('place','')}", ""]
        lines += [f"{c['n']}. **{c['name']}** (cat {c['category']}, {c.get('bg_color','') or 'environment'}): {c['object']}" for c in v["cards"]]
        lines.append("")
    (run_dir / "review_sets.md").write_text("\n".join(lines))
    pl = ["# Image prompts for review", ""]
    for v in sets:
        for c in v["cards"]:
            pl += [f"## {v['id']}{c['n']} {c['name']} (cat {c['category']})", "", prompts.build(c), ""]
    (run_dir / "review_prompts.md").write_text("\n".join(pl))


def new_run(theme, wishes="", variants=None, name=None, sets_file=None, stop_after=None):
    """stop_after: None (fully automatic), "compose" (stop after the object list + prompts for review), "dry" (with sets_file: only write prompts, no API)."""
    t0 = time.time()
    n = variants or config.VARIANTS
    run_dir = config.RUNS_DIR / (name or f"{datetime.now():%Y%m%d-%H%M}_{slug(theme)}")
    run_dir.mkdir(parents=True, exist_ok=True)
    save_json(run_dir / "request.json", dict(theme=theme, wishes=wishes, variants=n, text_model=config.TEXT_MODEL,
                                             image_model=config.IMAGE_MODEL, candidates=config.CANDIDATES,
                                             max_rounds=config.MAX_ROUNDS, pass_score=config.PASS_SCORE,
                                             started=datetime.now().isoformat(timespec="seconds")))
    usage = Usage()
    print(f"[run] {run_dir}")
    if sets_file:  # object list written or edited by a human: skip the composer
        from .compose import validate
        sets = json.loads(Path(sets_file).read_text())
        errs = validate(sets, len(sets))
        save_json(run_dir / "compose" / "sets.json", sets)
        save_json(run_dir / "compose" / "validation.json", errs)
        for e in errs:
            print(f"[sets] WARNING: {e}")
        for v in sets:
            for c in v["cards"]:
                c.setdefault("set_context", v.get("context", ""))
    else:
        sets = compose(theme, wishes, n, run_dir, usage)
    write_review(run_dir, sets)
    if stop_after in ("compose", "dry"):
        save_state(run_dir, sets, usage)
        print(f"[checkpoint] review {run_dir}/review_sets.md and review_prompts.md; edit {run_dir}/compose/sets.json if needed, then run:\n"
              f"  python3 -m studio new --theme \"{theme}\" --sets {run_dir}/compose/sets.json --name <new-name>")
        return run_dir
    for v in sets:
        print(f"[compose] {v['id']}. {v['set_name']}: " + ", ".join(f"{c['name']}({c['category']})" for c in v["cards"]))
    save_state(run_dir, sets, usage)
    jobs = [(v["id"], c) for v in sets for c in v["cards"]]
    with ThreadPoolExecutor(len(jobs)) as ex:
        for f in [ex.submit(process_card, run_dir, vid, c, usage) for vid, c in jobs]:
            c = f.result()
            print(f"[card] {c['name']}: {c.get('final')}")
            save_state(run_dir, sets, usage)
    build_sheets(run_dir, sets)
    write_report(run_dir, sets, usage, time.time() - t0)
    save_state(run_dir, sets, usage)
    print(f"[done] {run_dir}/report.md  cost ~${usage.usd()}  {(time.time()-t0)/60:.1f} min")
    return run_dir


def regen(run_dir, vid, n, obj=None, name=None, note="", category=None, pick=None):
    """Re-roll one card. Optionally replace its object/name/category, add a note, or pin a file by hand."""
    run_dir = Path(run_dir)
    sets, usage = load_state(run_dir)
    v = next(v for v in sets if v["id"] == vid)
    card = next(c for c in v["cards"] if int(c["n"]) == int(n))
    if pick:
        card["pinned"] = pick
        choose(card_dir(run_dir, vid, card), card)
    else:
        card.pop("pinned", None)
        old_dir = card_dir(run_dir, vid, card)
        if obj or name or category:
            card.update({k: val for k, val in dict(object=obj, name=name, category=category).items() if val})
            card["history"] = []  # new object: old candidates no longer apply
            if old_dir.exists():
                old_dir.rename(old_dir.with_name(old_dir.name + f"_replaced_{datetime.now():%H%M%S}"))
        start = max([e["round"] for e in card.get("history", [])], default=0) + 1
        process_card(run_dir, vid, card, usage, rounds=1, start_round=start, note=note)
    save_state(run_dir, sets, usage)
    build_sheets(run_dir, sets)
    write_report(run_dir, sets, usage)
    print(f"[regen] {vid}{n} {card['name']}: {card.get('final')}")


def retest(src, card_ids, name):
    """Copy the listed cards (specs only) from an old run into a new run and generate them with current prompts."""
    import copy
    t0 = time.time()
    sets, _ = load_state(Path(src))
    run_dir = config.RUNS_DIR / name; run_dir.mkdir(parents=True, exist_ok=True)
    req = json.loads((Path(src) / "request.json").read_text())
    save_json(run_dir / "request.json", {**req, "retest_of": str(src), "cards": card_ids,
                                         "started": datetime.now().isoformat(timespec="seconds")})
    usage = Usage(); picked = {}
    for cid in card_ids:
        v = next(v for v in sets if v["id"] == cid[0].upper())
        c = copy.deepcopy(next(c for c in v["cards"] if int(c["n"]) == int(cid[1:])))
        for k in ("history", "final", "pinned"):
            c.pop(k, None)
        picked.setdefault(v["id"], {**{k: v[k] for k in v if k != "cards"}, "cards": []})["cards"].append(c)
    variants = list(picked.values())
    jobs = [(v["id"], c) for v in variants for c in v["cards"]]
    with ThreadPoolExecutor(len(jobs)) as ex:
        list(ex.map(lambda j: process_card(run_dir, j[0], j[1], usage, rounds=1), jobs))
    save_state(run_dir, variants, usage)
    build_sheets(run_dir, variants)
    write_report(run_dir, variants, usage, time.time() - t0)
    print(f"[done] {run_dir}  cost ~${usage.usd()}")
    return run_dir
