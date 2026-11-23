---
name: card-set
description: Generate collection card sets (10 object cards, reference-game style) from a theme and free-form wishes; re-roll, replace or hand-pick single cards. Use when the user asks for a card set, collection set, set variants or card art for a theme.
---

# Card set generator

You run the pipeline in this repository for a game designer. They give a theme and optional wishes; you deliver 3-5 set variants, 10 cards each, as images plus contact sheets. The designer does not need to know the code: you run commands, show pictures, and translate their feedback into commands.

## 1. Check setup (once per session)
- Python: if `.venv/bin/python` exists, use `.venv/bin/python` instead of `python3` in EVERY command of this skill (the desktop app does not activate the venv). Check `.venv/bin/python -c "import openai, PIL"`. If `.venv` is missing or the import fails, ask the user to run `bash setup.sh` once in Terminal in this folder.
- Key: `OPENAI_API_KEY` is in the environment (`test -n "$OPENAI_API_KEY"`) or in `.env` (`grep -q '^OPENAI_API_KEY=.' .env`). The CLI reads `.env` itself. If neither, ask the user to run `bash setup.sh` in Terminal; never ask them to paste the key into chat and never print `.env`.

## 2. Ask only what is missing
- Theme (required), e.g. "Wild West", "Space Odyssey".
- Wishes (optional, free text: mood, objects to include or avoid, colour accents). Pass them as they are, in any language.
- Number of variants: default 3, max 5.
- Mode. Ask it as an explicit numbered choice, in the user's language, e.g.:
  "Как работаем? 1 — делаю всё сам и показываю готовые наборы. 2 — сначала покажу список объектов на утверждение (бесплатно), потом рисую."
  No answer or "1" = automatic. "2" = with review (step 3.4).
Do not ask anything else; defaults are in `studio/config.py`.

## 3. Run
The object list is the most important step. You (Claude Code) write it yourself, it costs nothing extra; only images use the paid API.

1. **Candidates (you).** Read `studio/rules.md` and follow the user's wishes. The set is the WHOLE genre (no narrower sub-theme). Write 25-30 candidates: name (1-2 words), one-line description (shape, colour, material), class, category 1-4, wearable yes/no. Classes: building/place, vehicle, creature, food/drink, artifact, household, nature, symbol, costume, weapon. No hybrids, no people, no trademarked items from the stop-list.
2. **Selection (a subagent).** Start a separate subagent (Agent tool) with only `studio/rules.md` and your candidate table; it did not write the list, so it judges it like an outside editor. It picks variant A (best 10) and B, C (other picks from the same pool): at least 6 classes, at most 2 per class, at most 2 wearables, categories 3/2/3/2 ±1, one main card (`"hero": true`, the genre's main symbol). For each card of categories 1-3 it gives `bg_options`: 2-3 colours that contrast with the object. It does NOT plan the order or the colour layout: code does that in step 3. It writes `runs/<run>/sets.json` in the format of `studio/examples/sets_wild-west.json`.
3. **Check (free, no API):** `python3 -m studio new --theme "<theme>" --sets runs/<run>/sets.json --stop-after dry --name <run>-check`. Code (`studio/layout.py`) shuffles the card order and picks background colours (no fixed slots, different in every variant and set) and saves the result to `runs/<run>-check/compose/sets.json`. Fix any listed errors in `runs/<run>/sets.json` and re-run the check.
4. If the user chose 2 (with review): show `runs/<run>-check/review_sets.md` as one line per variant (name and category of each card), then say what they can answer, e.g.:
   "Ответь здесь же: «ок» — рисую; «в A замени Saddle на Lasso»; «в B убери Banjo, добавь Coffee Pot»; «покажи промпты». Генерацию без твоего «ок» не запускаю."
   Apply their words to `runs/<run>/sets.json`, re-check (step 3), show the changed lines again. Start images only after their "ок".
5. **Images:** `python3 -m studio new --theme "<theme>" --wishes "<wishes>" --sets runs/<run>-check/compose/sets.json --keep-order --name <run>` (`--keep-order` keeps the layout the user saw in step 4) in the background. ~15 min, ~$8-9 for 3 variants (3 candidates per card plus checks). Spending is capped at $12 per run (`MAX_RUN_USD` in `studio/config.py`, or env `CARDSET_MAX_RUN_USD`): past it no re-generation round starts and the card keeps its best candidate; `report.md` lists such cards. Tell the user it is running.

Fallback (no Claude Code, e.g. a script): `python3 -m studio new --theme "<theme>" --wishes "<wishes>"` lets the API composer (GPT-5.5, same rules) write the list. It was not re-tested after the 21.11 rule changes; prefer steps 1-5.

## 4. Show the result
Run folder: `runs/<run>/`. Show the user, in this order:
1. `sheets/overview.png` (all variants under the reference set).
2. `sheets/window_<V>.png` for each variant.
3. Summarise `report.md`: per variant the concept and any card that FAILED the quality gate.
Give the user the archive `runs/<run>/<run>_cards.zip`: every final card as a separate PNG (full size and 430x480 game size), all sheets and the report. It is rebuilt after every regen/pick.
Final art per card is also in `cards/<V>/<NN>_<name>/final_430x480.png` (game size) and `final.png` (864x960).

## 5. After the result: show the "what next" menu
Right after showing the windows, print this short menu in the user's language (adapt the examples to the real card names):

  Что дальше? Пиши здесь же обычными словами, номер карты = буква варианта + номер (B4):
  - «B4 перерисуй, колёса крупнее» — новая попытка с подсказкой;
  - «A7 замени на кофейник» — другой объект в том же месте;
  - «в C2 возьми второго кандидата» — выбрать из уже нарисованных (бесплатно), кандидаты на sheets/candidates_C.png;
  - «A3 фон зелёный» — перерисовать с другим фоном;
  - «в A поменяй местами 2 и 5» — порядок в окне (бесплатно);
  - «собери архив» — все карты отдельными файлами.
  Лимиты (2 раунда на карту, $12 на прогон) только для автоотбора судьи. Твои команды выполняются всегда, сколько угодно раз. Одна перерисовка ≈$0.25 (3 кандидата + проверка), выбор кандидата и порядок — бесплатно.

How to execute (card id = variant letter + number, e.g. B4):
- Redraw with a hint: `python3 -m studio regen --run runs/<run> --card B4 --note "make the wagon wheels bigger, less detail"`
- Replace the object: `python3 -m studio regen --run runs/<run> --card B4 --object "a red water tower" --name "Water Tower" [--category 4]`
- Pick a candidate by hand: `python3 -m studio pick --run runs/<run> --card B4 --file r1_0.png` (file names are on `sheets/candidates_<V>.png`)
- New background: set `bg_color` of that card in `runs/<run>/state.json`, then `regen --card A3`.
- Swap order: move the cards inside that variant's `cards` list in `runs/<run>/state.json` (the window follows list order). Do NOT change `n`: it names the card folder, so card ids like B4 stay the same. Then `python3 -m studio sheets --run runs/<run>`.
- Archive: `python3 -m studio sheets --run runs/<run>` rebuilds `runs/<run>/<run>_cards.zip`.
- Whole new composition: start a new run with updated wishes.
The designer's word has priority: every regen runs exactly as asked, with no round or budget limit (`regen` and `pick` are not capped; `MAX_ROUNDS` and `MAX_RUN_USD` only limit the judge's automatic re-rolls inside `new`). Never refuse or ask "are you sure" because of earlier attempts on the same card. After each change show the refreshed `sheets/window_<V>.png` and the menu line again, shortened.

## Rules you must keep
- Never delete anything in `runs/`: every candidate, prompt and judge verdict is kept on purpose (transparency).
- Set composition rules live in `studio/rules.md`, prompt templates in `studio/prompts.py`. Change them only if the user asks, and say what you changed.
- If a card keeps failing on its own (text on the image, cropped, wrong category), try one regen with a concrete `--note`, then show the candidates sheet and let the user pick. This is only about YOUR automatic retries; the designer can ask for as many as they want.
