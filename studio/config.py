"""All tunable settings in one place. A game designer can change models, counts and prices here."""
import os
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REF_DIR = REPO / "references"
RUNS_DIR = Path(os.environ.get("CARDSET_RUNS", REPO / "runs"))

# --- models ---
TEXT_MODEL = os.environ.get("CARDSET_TEXT_MODEL", "gpt-5.5")      # composer + judge (vision)
IMAGE_MODEL = os.environ.get("CARDSET_IMAGE_MODEL", "gpt-image-2.6-sunburst")  # won the blind A/B vs 2.5-sunburst (bench-04-blind, 19.11)
IMAGE_QUALITY = "medium"   # high was not better in bench-03 and is ~4x slower on gpt-image-2
IMAGE_SIZE = "864x960"    # 9:10, 2x the in-game 430x480; smallest size the API allows near it (576x640 is rejected), ~18% cheaper than 1152x1280
GAME_SIZE = (430, 480)

# --- pipeline ---
VARIANTS = 3          # set variants per theme
CANDIDATES = 3        # images per card per round (3 since 20.11: more choice against distortions)
MAX_ROUNDS = 2        # round 2 regenerates only cards where no candidate passed the gate
WORKERS = 4           # parallel image requests (org limit: 20 input images/min, 3 refs per call)
PASS_SCORE = 9        # judge total 0-10 (5 checklist items x 0-2, analysis/rating-checklist.md). 9 matched Hrach on 16/20 of ww-01 (8 gave 14/20)

# --- rough cost estimate, USD per 1M tokens (check current OpenAI pricing) ---
PRICE = {
    "image_out": 30.0, "image_in": 8.0, "text_in_img": 5.0,
    "llm_in": 5.0, "llm_out": 30.0,   # gpt-5.5 list price (was wrongly 1.25/10 until 20.11)
}

# Style references attached to every image request, per category (clean arts without card frames).
REFS = {
    1: ["clean/cat1_bottle.png", "clean/cat1_honey.png", "arts/window_seafaring_anchor.png"],
    2: ["clean/cat2_mojito.png", "arts/cat2_phone-booth_430x480.png", "clean/cat2_teacup.png"],
    3: ["arts/cat3_helm_430x480.png", "clean/cat3_coffeepot.png", "arts/cat3_captains-cap_430x480.png"],
    4: ["arts/cat4_lighthouse_430x480.png", "clean/cat4_fieldball.png", "clean/cat4_coaster.png"],
}
# References the judge sees to compare style (2 per category).
JUDGE_REFS = {
    1: ["clean/cat1_bottle.png", "clean/cat1_pizza.png"],
    2: ["arts/cat2_phone-booth_430x480.png", "clean/cat2_lemontree.png"],
    3: ["arts/cat3_helm_430x480.png", "clean/cat3_pie.png"],
    4: ["arts/cat4_lighthouse_430x480.png", "clean/cat4_antiquity.png"],
}
REFERENCE_WINDOW = "sets/set_amusement_window.png"
