"""Step 1. Composer agent: theme + wishes -> N set variants of 10 cards (JSON).

Three passes, every one logged to <run>/compose/:
  1. draft    - the composer writes the sets following studio/rules.md
  2. code     - validate(): split 3/2/3/2, required fields (violations are sent back)
  3. critic   - a second call reviews every card like a lead designer ("is the theme obvious without the caption?",
                "does the place match the set name?", "is it physically sensible?") and returns a corrected JSON
After that studio/layout.py (code, no API) shuffles the card order and picks background colours (Hrach 22.11).
The composer model is set in config.TEXT_MODEL (or passed in); OpenAI and Gemini models are supported.
"""
import json, os, re
from collections import Counter

from . import config, layout
from .util import save_json, Usage

SCHEMA_HINT = """Return JSON:
{"variants": [
  {"id": "A",
   "set_name": "1-2 English words",
   "archetypes": "the 15-20 first objects a player names for this genre, comma-separated; most cards come from this list",
   "context": "the genre in a few words, e.g. 'Wild West'",
   "place": "3-4 typical places of the genre and what is physically there, e.g. 'frontier town street with boardwalks; desert trail with cacti; campfire by a red canyon'",
   "concept": "one sentence: which place/situation of the theme this set shows",
   "palette": "one sentence on the colour mood",
   "motif": "one simple silhouette used as a background pattern on 2-3 cards, e.g. 'horseshoe'",
   "cards": [  // exactly 10; the order in the window is decided later by code (studio/layout.py)
     {"n": 1,
      "name": "1-2 English words",
      "object": "short iconic English description of ONE object, colour and theme marker included, e.g. 'a brown cowboy hat with a red band and curled brim'",
      "theme_marker": "the concrete visual detail that makes it read as the theme without caption",
      "moment": "where in the genre world it lives, e.g. 'saloon', 'campfire'",
      "class": "equipment|food|drink|clothing|accessory|transport|architecture|nature|furniture|device|other",
      "scale": "hand|furniture|big",
      "silhouette": "vertical|horizontal|round",
      "category": 1,
      "bg_options": ["2-3 clean colour words from the rules list that contrast with the object; code picks one"],
      "bg_treatment": "cat1/2: sunburst rays | vertical stripes | diagonal stripes | soft waves | concentric circles | soft gradient | faint repeating pattern of <motif> silhouettes; cat3: faint repeating pattern of <motif> silhouettes | plain wall with light glow | simple <matching> interior; cat4: leave empty",
      "surface": "cat3 only: realistic surface from one of the genre's places that fits the object; otherwise empty",
      "environment": "cat4 only: one of the genre's places as a bright environment; otherwise empty",
      "view": "camera angle, e.g. 'slightly tilted for dynamism' (cat1), 'three-quarter view slightly from above' (cat2/3), 'frontal, slightly from below' (tall cat4)"
     }
   ]}
]}"""

CRITIC = """You are a strict lead game designer reviewing card sets made by a junior designer for a casual mobile game collection.
Check EVERY card against the rules below, especially:
A. Archetype test (first and most important): would a child name this object among the first 20 things of the genre? Hybrids (a theme sign stuck on food, furniture or a random thing: cape cookie, mask locker, hero doorway) and invented gadgets fail: replace them with a real archetype. At least half of the cards show real non-plastic materials.
0. Genre: the set covers the WHOLE genre (no narrower sub-theme, place, profession or day). Class quotas: at most 2 per class, at most 2 wearables, at least 6 classes, no class is mandatory. No hybrids (theme sign on a random object); magic is at most one adjective. Invented objects (things that do not exist in films of this genre) fail: replace them with real, iconic ones.
1. Theme without caption: cover the name, look at the object alone. Would a player instantly name the theme? Generic objects (plain rope, stool, kettle, modern boots, sandwich, generic station) fail unless the theme marker clearly changes the silhouette.
2. Place: do cat3 surfaces and cat4 environments come from the genre's places and fit the object (no house interior for a desert cactus)?
3. Physical sense: does the object stand/grow where it really would?
4. Readability without caption, kid-friendly, not boring.
5. Whole variant: does it read as the whole genre, not one corner of it?
Then FIX the sets: replace failing objects (keep the category split, bg_options and diversity rules), sharpen theme markers, fix surfaces/environments. If a whole variant fails rule 5, rebuild it around a better place.
Return JSON: {"review": [{"card": "A6", "problem": "...", "fix": "..."}], "variants": [ ...full corrected variants in the same schema... ]}

RULES:
"""


def llm(model, system, messages, usage, effort="medium"):
    """One JSON-returning call to OpenAI or Gemini. messages: list of {"role": "user"|"assistant", "content": str}."""
    if model.startswith("gemini"):
        from google import genai
        from google.genai import types
        g = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        contents = [types.Content(role="model" if m["role"] == "assistant" else "user", parts=[types.Part(text=m["content"])])
                    for m in messages]
        r = g.models.generate_content(model=model, contents=contents, config=types.GenerateContentConfig(
            system_instruction=system, response_mime_type="application/json"))
        um = r.usage_metadata

        class U:  # same shape as OpenAI usage for the counter
            input_tokens = um.prompt_token_count or 0
            output_tokens = (um.candidates_token_count or 0) + (getattr(um, "thoughts_token_count", 0) or 0)
        usage.add_llm(U)
        return r.text
    from openai import OpenAI
    kw = {"reasoning": {"effort": effort}} if model.startswith(("gpt-5", "o")) else {}
    r = OpenAI().responses.create(model=model, input=[{"role": "system", "content": system}] + messages,
                                  text={"format": {"type": "json_object"}}, **kw)
    usage.add_llm(r.usage)
    return r.output_text


def validate(variants, n_expected):
    errs = []
    if len(variants) != n_expected:
        errs.append(f"expected {n_expected} variants, got {len(variants)}")
    for v in variants:
        vid = v.get("id", "?"); cards = v.get("cards", [])
        if not v.get("place"):
            errs.append(f"variant {vid}: no place")
        if not v.get("context"):
            errs.append(f"variant {vid}: no context (the genre)")
        if len(cards) != 10:
            errs.append(f"variant {vid}: {len(cards)} cards instead of 10"); continue
        cnt = Counter(int(c.get("category", 0)) for c in cards)
        for cat, t in {1: 3, 2: 2, 3: 3, 4: 2}.items():
            if cnt.get(cat, 0) < 1 or abs(cnt.get(cat, 0) - t) > 1:
                errs.append(f"variant {vid}: category {cat} has {cnt.get(cat, 0)} cards, target {t}±1 (min 1)")
        for i, c in enumerate(cards):
            if int(c.get("category", 0)) != 4 and not (c.get("bg_options") or c.get("bg_color")):
                errs.append(f"variant {vid}: card {i+1} has no bg_options (2-3 colours that contrast with the object)")
            if int(c.get("category", 0)) == 3 and not c.get("surface"):
                errs.append(f"variant {vid}: card {i+1} is cat3 but has no surface")
            if int(c.get("category", 0)) == 4 and not c.get("environment"):
                errs.append(f"variant {vid}: card {i+1} is cat4 but has no environment")
            if not c.get("moment"):
                errs.append(f"variant {vid}: card {i+1} has no moment (where in the genre world)")
            if not c.get("theme_marker"):
                errs.append(f"variant {vid}: card {i+1} has no theme_marker")
            if len(c.get("name", "").split()) > 2:
                errs.append(f"variant {vid}: card {i+1} name '{c.get('name')}' longer than 2 words")
        motif = (v.get("motif") or "").lower()
        uses = sum(1 for c in cards if motif and motif in (c.get("bg_treatment") or "").lower())
        if uses > 3:
            errs.append(f"variant {vid}: motif used on {uses} cards, max 3")
    STOP = ("blue milk", "lightsaber", "droid", "jedi", "sith", "x-wing", "tie fighter",
            "batman", "bat symbol", "superman", "snitch", "sorting hat", "dragonborn", "mjolnir")
    for v in variants:
        for c in v.get("cards", []):
            txt = f"{c.get('name','')} {c.get('object','')}".lower()
            hit = [w for w in STOP if re.search(rf"\b{w}s?\b", txt)]
            if hit:
                errs.append(f"variant {v.get('id')}: card '{c.get('name')}' uses franchise item {hit}: replace it (see the stop-list)")
    if len(variants) >= 3:  # one object type in at most 2 of 3 variants (Hrach 20.11)
        seen = Counter()
        for v in variants:
            seen.update({(c.get("name") or "x").split()[-1].lower().rstrip("s") for c in v.get("cards", [])})
        for w, k in seen.items():
            if k > 2:
                errs.append(f"object type '{w}' appears in {k} variants, max 2: replace it in one variant with another object of the genre")
    for f in ("set_name", "context", "place", "palette", "motif"):  # 3 alternatives of ONE set (Hrach 20.11)
        vals = {(v.get(f) or "").strip().lower() for v in variants}
        if len(vals) > 1:
            errs.append(f"variants differ in '{f}': all variants must share one header (copy it word for word), only the 10 objects differ")
    return errs


def _parse(raw, key="variants"):
    d = json.loads(raw)
    return d[key], d


def compose(theme, wishes, n_variants, run_dir, usage: Usage, max_attempts=3, model=None, critic=True):
    model = model or config.TEXT_MODEL
    rules = (config.REPO / "studio" / "rules.md").read_text()
    system = f"You are the lead game designer of a casual mobile game collection. Follow these rules strictly.\n\n{rules}\n\n{SCHEMA_HINT}"
    user = (f"Theme of the set: {theme}\n"
            f"Wishes from the game designer (may be empty): {wishes or '-'}\n"
            f"Make {n_variants} alternative variants of ONE set (ids A, B, C, ...): one shared header, different picks of 10 objects.")
    messages = [{"role": "user", "content": user}]
    variants = None

    def fix_loop(tag, messages, sys_prompt, key="variants"):
        nonlocal variants
        for attempt in range(1, max_attempts + 1):
            raw = llm(model, sys_prompt, messages, usage)
            try:
                variants, full = _parse(raw, key)
                errs = validate(variants, n_variants)
            except Exception as e:
                full, errs = None, [f"invalid JSON: {e}"]
            save_json(run_dir / "compose" / f"{tag}_attempt_{attempt}.json",
                      dict(model=model, system=sys_prompt, messages=messages, answer=raw, errors=errs))
            if not errs:
                return full
            print(f"[compose:{tag}] attempt {attempt}: {len(errs)} rule violations, asking to fix")
            messages = messages + [{"role": "assistant", "content": raw},
                                   {"role": "user", "content": "Fix these rule violations and return the full JSON again:\n- " + "\n- ".join(errs)}]
        print(f"[compose:{tag}] WARNING: rules still violated, continuing; see compose/ log")
        return None

    fix_loop("draft", messages, system)
    if variants is None:
        raise RuntimeError("composer failed to return valid JSON")
    save_json(run_dir / "compose" / "draft_sets.json", variants)
    if critic:
        crit_sys = CRITIC + rules + "\n\n" + SCHEMA_HINT.replace('{"variants"', '{"review": [...], "variants"')
        crit_user = (f"Theme: {theme}\nWishes: {wishes or '-'}\nSets to review:\n"
                     + json.dumps({"variants": variants}, ensure_ascii=False))
        draft = variants
        full = fix_loop("critic", [{"role": "user", "content": crit_user}], crit_sys)
        if full:
            save_json(run_dir / "compose" / "critic_review.json", full.get("review", []))
            print(f"[compose:critic] {len(full.get('review', []))} cards fixed")
        else:
            variants = draft  # critic output broke the rules: keep the validated draft
    layout.arrange(variants)  # order and background colours are chosen by code, not by the composer (Hrach 22.11)
    for v in variants:  # the context must reach the image prompt, not get lost between steps
        for card in v["cards"]:
            card["set_context"] = v.get("context", "")
    save_json(run_dir / "compose" / "sets.json", variants)
    return variants
