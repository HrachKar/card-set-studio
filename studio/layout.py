"""Step 1b. Layout (code, no API): card order in the 5x2 window and background colours.

Why (Hrach 22.11): the composer (LLM or a human with a template) tends to reuse one layout, so category 1 always
landed in slots 1 and 6 and the same background colours stood in the same slots in every variant and every set.
Reference sets from the game have no such grid. The composer now only says WHAT is in the set and which 2-3
background colours suit each object (bg_options); this module decides WHERE each card goes and WHICH colour it gets.

Rules:
  order   - random per variant and set; the main card (hero) is last; at most 2 cards of one category in a row;
            neighbours (left/right) are of different object classes; two variants of one set have the same category
            in at most 3 of the other 9 slots.
  colours - one of the card's bg_options (or any clean colour not named in the object); grid neighbours
            (left/right, above/below) differ; at most 3 cards of one temperature in a row; one colour at most 3 times
            per set; the set palette tilts the choice to warm or cool; two variants of one set share at most 2
            colours in the same slots. Category 4 cards have an environment instead of a colour.
Check: python -m studio.layout studio/examples/sets_*.json  (prints slot-repeat stats before/after, no API)
"""
import hashlib, itertools, random, re, sys
from collections import Counter

WARM = ["yellow", "orange", "red", "pink", "peach"]
COOL = ["sky blue", "blue", "turquoise", "green", "mint", "purple", "lilac"]
ALL = WARM + COOL
TEMP = {**{c: "warm" for c in WARM}, **{c: "cool" for c in COOL}}
MAX_CAT_RUN, MAX_TEMP_RUN, MAX_COLOUR, MAX_SLOT_SHARED, MAX_CAT_SHARED = 2, 3, 3, 2, 3


def _rng(seed, *parts):
    h = hashlib.sha256("|".join(map(str, (seed,) + parts)).encode()).hexdigest()
    return random.Random(int(h[:16], 16))


def _cat(c):
    return int(c.get("category", 0))


def _run_ok(seq, key, limit):
    """No more than `limit` equal non-empty keys in a row."""
    run, prev = 0, object()
    for x in seq:
        k = key(x)
        run = run + 1 if k and k == prev else 1
        prev = k
        if k and run > limit:
            return False
    return True


def order_ok(cards):
    if not _run_ok(cards, _cat, MAX_CAT_RUN):
        return False
    return all(not a.get("class") or a.get("class") != b.get("class") for a, b in zip(cards, cards[1:]))


def arrange_order(cards, rng, taken_orders=(), tries=4000):
    """taken_orders: category lists of already arranged variants of the same set (same-slot overlap limit)."""
    hero = [c for c in cards if c.get("hero")][-1:]
    rest = [c for c in cards if c not in hero]
    best = rest[:]
    for _ in range(tries):
        rng.shuffle(rest)
        cats = [_cat(c) for c in rest]
        if order_ok(rest + hero) and all(sum(a == b for a, b in zip(cats, o)) <= MAX_CAT_SHARED for o in taken_orders):
            return rest + hero
    return best + hero  # constraints impossible for this list: keep the composer's order


def _options(c):
    opts = [o.strip().lower() for o in (c.get("bg_options") or []) if o and o.strip().lower() in TEMP]
    if not opts:  # old lists: any clean colour whose name is not in the object description (contrast)
        obj = (c.get("object") or "").lower()
        opts = [col for col in ALL if not re.search(rf"\b{col.split()[-1]}\b", obj)]
    return opts


def _bias(v):
    txt = f"{v.get('palette', '')} {v.get('bg_temperature', '')}".lower()
    w = sum(txt.count(k) for k in ("warm", "sand", "wood", "gold", "leather", "terracotta", "sunset"))
    k = sum(txt.count(k) for k in ("cool", "blue", "steel", "ice", "night", "sea", "space"))
    return "warm" if w > k else "cool" if k > w else None


def assign_colours(v, rng, taken_slots=(), tries=400):
    """taken_slots: colour lists of already arranged variants of the same set (same-slot overlap limit)."""
    cards = v["cards"]
    bias = _bias(v)

    def weight(col):
        return 2 if bias and TEMP[col] == bias else 1

    def fits(i, col, chosen):
        if _cat(cards[i]) == 4:
            return True
        for j in (i - 1, i - 5):  # left neighbour in the row, card above
            if j >= 0 and (j != i - 1 or i % 5) and chosen[j] == col:
                return False
        if sum(1 for x in chosen if x == col) >= MAX_COLOUR:
            return False
        temps = [TEMP.get(x) for x in chosen[:i]] + [TEMP[col]]
        if not _run_ok(temps, lambda t: t, MAX_TEMP_RUN):
            return False
        for other in taken_slots:
            same = sum(1 for k in range(i) if chosen[k] and chosen[k] == other[k]) + (col == other[i])
            if same > MAX_SLOT_SHARED:
                return False
        return True

    for _ in range(tries):
        chosen = []
        for i, c in enumerate(cards):
            if _cat(c) == 4:
                chosen.append(""); continue
            opts = [o for o in _options(c) if fits(i, o, chosen)]
            if not opts:
                break
            chosen.append(rng.choices(opts, [weight(o) for o in opts])[0])
        if len(chosen) == len(cards):
            break
    else:
        chosen = [c.get("bg_color", "") for c in cards]  # no layout found: keep the composer's colours
    for c, col in zip(cards, chosen):
        if _cat(c) != 4:
            c["bg_color"] = col
    return chosen


def arrange(variants, seed=None):
    """Shuffle order and pick background colours for all variants of one set, in place. Returns variants."""
    seed = random.randrange(1 << 30) if seed is None else seed
    taken, orders = [], []
    for v in variants:
        rng = _rng(seed, v.get("set_name"), v.get("id"))
        v["cards"] = arrange_order(v["cards"], rng, orders)
        orders.append([_cat(c) for c in v["cards"]])
        for i, c in enumerate(v["cards"], 1):
            c["n"] = i
        taken.append(assign_colours(v, rng, taken))
        v["layout_seed"] = seed
    return variants


def slot_stats(all_variants):
    """Share of slots where two variants have the same category / the same background colour."""
    rows = [([_cat(c) for c in v["cards"]], [c.get("bg_color") or "" for c in v["cards"]]) for v in all_variants]
    pairs = list(itertools.combinations(rows, 2))
    cat = sum(sum(a == b for a, b in zip(x[0], y[0])) / 10 for x, y in pairs) / len(pairs)
    bg = sum(sum(a == b and a != "" for a, b in zip(x[1], y[1])) / max(1, sum(1 for a in x[1] if a)) for x, y in pairs) / len(pairs)
    orders = len({tuple(r[0]) for r in rows})
    return dict(cat_same_slot=round(100 * cat), bg_same_slot=round(100 * bg), category_orders=orders, variants=len(rows))


def check(v):
    """Layout violations of one variant (empty list = ok)."""
    cards, errs = v["cards"], []
    if not _run_ok(cards, _cat, MAX_CAT_RUN):
        errs.append(f"{v.get('id')}: more than {MAX_CAT_RUN} cards of one category in a row")
    cols = [c.get("bg_color") or "" for c in cards]
    for i, col in enumerate(cols):
        if col and ((i % 5 and cols[i - 1] == col) or (i >= 5 and cols[i - 5] == col)):
            errs.append(f"{v.get('id')}: card {i+1} shares bg colour '{col}' with a neighbour")
    if not _run_ok([TEMP.get(c) for c in cols], lambda t: t, MAX_TEMP_RUN):
        errs.append(f"{v.get('id')}: more than {MAX_TEMP_RUN} cards of one temperature in a row")
    many = [k for k, n in Counter(c for c in cols if c).items() if n > MAX_COLOUR]
    if many:
        errs.append(f"{v.get('id')}: colour used more than {MAX_COLOUR} times: {many}")
    if cards and not cards[-1].get("hero") and any(c.get("hero") for c in cards):
        errs.append(f"{v.get('id')}: main card is not last")
    return errs


if __name__ == "__main__":
    import copy, json
    from pathlib import Path
    sets = [json.loads(Path(f).read_text()) for f in sys.argv[1:]]
    before = [v for s in sets for v in s]
    print("before:", slot_stats(before))
    runs = []
    for seed in range(20):
        after = []
        for s in copy.deepcopy(sets):
            after += arrange(s, seed=seed)
        errs = [e for v in after for e in check(v)]
        runs.append((slot_stats(after), len(errs)))
    print("after (mean of 20 seeds):", {k: round(sum(r[0][k] for r in runs) / len(runs), 1) for k in runs[0][0]},
          "layout violations:", sum(r[1] for r in runs))
    print("example seed 0:")
    for s in copy.deepcopy(sets):
        for v in arrange(s, seed=0):
            print(f"  {v['set_name'][:14]:14} {v['id']}", " ".join(str(_cat(c)) for c in v["cards"]), "|",
                  ", ".join(c.get("bg_color") or "-" for c in v["cards"]))
