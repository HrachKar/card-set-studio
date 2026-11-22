---
name: card-set
description: Generate collection card sets (10 object cards, reference-game style) from a theme and free-form wishes; re-roll, replace or hand-pick single cards. Use when the user asks for a card set, collection set, set variants or card art for a theme.
---

# Card set generator

You run the pipeline in this repository for a game designer. They give a theme and optional wishes; you deliver 3-5 set variants, 10 cards each, as images plus contact sheets. The designer does not need to know the code: you run commands, show pictures, and translate their feedback into commands.

## 1. Check setup (once per session)
- `python3 -c "import openai, PIL"` works, otherwise `pip install -r requirements.txt`.
- `OPENAI_API_KEY` is set (`test -n "$OPENAI_API_KEY"`). If not, ask the user to set it; never ask them to paste the key into chat.

## 2. Ask only what is missing
- Theme (required), e.g. "Wild West", "Space Odyssey".
- Wishes (optional, free text: mood, objects to include or avoid, colour accents). Pass them as they are, in any language.
- Number of variants: default 3, max 5.
- Mode: automatic (default) or "with review". Offer review in one line: "Хотите сначала утвердить список объектов и промпты? По умолчанию делаю всё сам." If the user does not answer or says no, run automatically.
Do not ask anything else; defaults are in `studio/config.py`.

## 3. Run
The object list is the most important step. You (Claude Code) write it yourself, it costs nothing extra; only images use the paid API.

1. **Candidates (you).** Read `studio/rules.md` and follow the user's wishes. The set is the WHOLE genre (no narrower sub-theme). Write 25-30 candidates: name (1-2 words), one-line description (shape, colour, material), class, category 1-4, wearable yes/no. Classes: building/place, vehicle, creature, food/drink, artifact, household, nature, symbol, costume, weapon. No hybrids, no people, no trademarked items from the stop-list.
2. **Selection (a subagent).** Start a separate subagent (Agent tool) with only `studio/rules.md` and your candidate table; it did not write the list, so it judges it like an outside editor. It picks variant A (best 10) and B, C (other picks from the same pool): at least 6 classes, at most 2 per class, at most 2 wearables, categories 3/2/3/2 ±1, one main card (`"hero": true`, the genre's main symbol). For each card of categories 1-3 it gives `bg_options`: 2-3 colours that contrast with the object. It does NOT plan the order or the colour layout: code does that in step 3. It writes `runs/<run>/sets.json` in the format of `studio/examples/sets_wild-west.json`.
3. **Check (free, no API):** `python3 -m studio new --theme "<theme>" --sets runs/<run>/sets.json --stop-after dry --name <run>-check`. Code (`studio/layout.py`) shuffles the card order and picks background colours (no fixed slots, different in every variant and set) and saves the result to `runs/<run>-check/compose/sets.json`. Fix any listed errors in `runs/<run>/sets.json` and re-run the check.
4. If the user chose "with review": show `runs/<run>-check/review_sets.md` as one line per variant, apply their changes, re-check. Show `review_prompts.md` only if asked.
5. **Images:** `python3 -m studio new --theme "<theme>" --wishes "<wishes>" --sets runs/<run>-check/compose/sets.json --keep-order --name <run>` (`--keep-order` keeps the layout the user saw in step 4) in the background. ~15 min, ~$8-9 for 3 variants (3 candidates per card plus checks). Spending is capped at $12 per run (`MAX_RUN_USD` in `studio/config.py`, or env `CARDSET_MAX_RUN_USD`): past it no re-generation round starts and the card keeps its best candidate; `report.md` lists such cards. Tell the user it is running.

Fallback (no Claude Code, e.g. a script): `python3 -m studio new --theme "<theme>" --wishes "<wishes>"` lets the API composer (GPT-5.5, same rules) write the list. It was not re-tested after the 21.11 rule changes; prefer steps 1-5.

## 4. Show the result
Run folder: `runs/<run>/`. Show the user, in this order:
1. `sheets/overview.png` (all variants under the reference set).
2. `sheets/window_<V>.png` for each variant.
3. Summarise `report.md`: per variant the concept and any card that FAILED the quality gate.
Give the user the archive `runs/<run>/<run>_cards.zip`: every final card as a separate PNG (full size and 430x480 game size), all sheets and the report. It is rebuilt after every regen/pick.
Final art per card is also in `cards/<V>/<NN>_<name>/final_430x480.png` (game size) and `final.png` (864x960).

## 5. Apply feedback (card id = variant letter + number, e.g. B4)
- Re-roll a card, optionally with a hint: `python3 -m studio regen --run runs/<run> --card B4 --note "make the wagon wheels bigger, less detail"`
- Replace an object: `python3 -m studio regen --run runs/<run> --card B4 --object "a red water tower" --name "Water Tower" [--category 4]`
- Choose a candidate by hand (file names are on `sheets/candidates_<V>.png`): `python3 -m studio pick --run runs/<run> --card B4 --file r1_0.png`
- Want a whole new composition: start a new run with updated wishes.
After each change show the refreshed `sheets/window_<V>.png`.

## Rules you must keep
- Never delete anything in `runs/`: every candidate, prompt and judge verdict is kept on purpose (transparency).
- Set composition rules live in `studio/rules.md`, prompt templates in `studio/prompts.py`. Change them only if the user asks, and say what you changed.
- If a card keeps failing (text on the image, cropped, wrong category), try one regen with a concrete `--note`, then show the candidates sheet and let the user pick.
