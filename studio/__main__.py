"""CLI.

  python -m studio new --theme "Wild West" [--wishes "..."] [--variants 3] [--candidates 2] [--name my-run]
       [--stop-after compose]          # checkpoint: stop after the object list + prompts (review_sets.md, review_prompts.md)
       [--sets runs/<run>/compose/sets.json]   # continue from an approved / edited object list (skips the composer)
       [--sets file.json --stop-after dry]     # only write prompts for a ready list, no API calls
  python -m studio regen --run runs/<run> --card B4 [--object "a red barn"] [--name "Barn"] [--category 4] [--note "..."]
  python -m studio pick  --run runs/<run> --card B4 --file r2_1.png     # choose a candidate by hand
  python -m studio retest --from runs/<run> --cards A4,B4 --name <new-run>   # same cards, current prompts
  python -m studio sheets --run runs/<run>                               # rebuild sheets and report
"""
import argparse, os, sys
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(prog="studio")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("new"); a.add_argument("--theme", required=True); a.add_argument("--wishes", default="")
    a.add_argument("--variants", type=int); a.add_argument("--candidates", type=int); a.add_argument("--rounds", type=int)
    a.add_argument("--name")
    a.add_argument("--sets", help="JSON with ready sets (hand-written or edited): skip the composer")
    a.add_argument("--stop-after", choices=["compose", "dry"], help="compose: stop after the object list and prompts for review; dry: with --sets, only write prompts (no API)")
    r = sub.add_parser("regen"); r.add_argument("--run", required=True); r.add_argument("--card", required=True)
    r.add_argument("--object"); r.add_argument("--name"); r.add_argument("--category", type=int); r.add_argument("--note", default="")
    r.add_argument("--candidates", type=int)
    p = sub.add_parser("pick"); p.add_argument("--run", required=True); p.add_argument("--card", required=True); p.add_argument("--file", required=True)
    t = sub.add_parser("retest", help="re-generate chosen cards of an old run into a new run (to check prompt changes)")
    t.add_argument("--from", dest="src", required=True); t.add_argument("--cards", required=True); t.add_argument("--name", required=True)
    b = sub.add_parser("bench", help="cheap model comparison on a few cards of a run")
    b.add_argument("--from", dest="src", required=True); b.add_argument("--cards", required=True); b.add_argument("--name", required=True)
    b.add_argument("--models"); b.add_argument("--blind", action="store_true", help="also draw blind X/Y windows per set")
    k = sub.add_parser("composers", help="blind comparison of composer LLMs with cheap preview images")
    k.add_argument("--theme", required=True); k.add_argument("--wishes", default=""); k.add_argument("--models", required=True)
    k.add_argument("--variants", type=int, default=2); k.add_argument("--name", required=True)
    k.add_argument("--places", help="semicolon-separated sub-themes given to every composer, e.g. 'Frontier Town; Gold Rush Camp'")
    s = sub.add_parser("sheets"); s.add_argument("--run", required=True)
    args = ap.parse_args()

    if not os.environ.get("OPENAI_API_KEY") and getattr(args, "stop_after", None) != "dry":
        sys.exit("OPENAI_API_KEY is not set. Put it into the environment (see README).")
    from . import config, pipeline
    if getattr(args, "candidates", None):
        config.CANDIDATES = args.candidates
    if args.cmd == "new":
        if args.rounds:
            config.MAX_ROUNDS = args.rounds
        pipeline.new_run(args.theme, args.wishes, args.variants, args.name, args.sets, args.stop_after)
    elif args.cmd in ("regen", "pick"):
        vid, n = args.card[0].upper(), int(args.card[1:])
        if args.cmd == "pick":
            pipeline.regen(Path(args.run), vid, n, pick=args.file)
        else:
            pipeline.regen(Path(args.run), vid, n, obj=args.object, name=args.name, note=args.note, category=args.category)
    elif args.cmd == "bench":
        from . import bench
        bench.bench(Path(args.src), [c.strip() for c in args.cards.split(",")], args.name,
                    args.models.split(",") if args.models else None, args.blind)
    elif args.cmd == "composers":
        from . import composers
        composers.run(args.theme, args.wishes, args.models.split(","), args.variants, args.name,
                      [p.strip() for p in args.places.split(";")] if args.places else None)
    elif args.cmd == "retest":
        pipeline.retest(Path(args.src), [c.strip() for c in args.cards.split(",")], args.name)
    else:
        run = Path(args.run); sets, usage = pipeline.load_state(run)
        pipeline.build_sheets(run, sets); pipeline.write_report(run, sets, usage)


if __name__ == "__main__":
    main()
