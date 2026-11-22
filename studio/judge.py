"""Step 4. Quality gate: a vision LLM compares candidates of one card with reference arts of the same category.

Hard defects fail a candidate regardless of score. The best passing candidate wins.
If nothing passes, the judge's fix note is appended to the prompt for the next round.
"""
import base64, io, json
from openai import OpenAI
from PIL import Image

from . import config

HARD = ["text_or_numbers", "people", "object_cropped", "several_main_objects",
        "frame_or_border", "wrong_object", "wrong_category", "dark_or_photoreal", "broken_geometry"]

CAT_DESC = {
    1: "object floats in the air, no surface; simple background: one colour gradient with rays/stripes/waves/simple pattern",
    2: "object stands on a plain flat floor of the wall colour (lighter); plain vertical background, no environment",
    3: "object stands on a realistic textured surface (wood, cloth, tiles, stone...); volumetric soft background wall or simple interior",
    4: "object inside its real environment (landscape, sky, interior); object is the central hero, may be cropped by the frame",
}

RUBRIC = f"""You are the art lead of a casual mobile game (the reference game). Grade card illustrations against the style references,
using the same checklist the human game designer uses. Each item: 2 = yes, 1 = almost, 0 = no.
- style: could sit in the game window next to the references, same artist: chunky rounded forms, real materials (wood, metal, fabric, food) rendered softly with warm light, no outlines, NOT glossy plastic toy, chrome or neon, no fine AI-style texture (fibers, strands, gritty wood, tiny rocks/grass), not realistic.
- readability: at fingernail size, without a caption, it is instantly clear what the object is; one clear silhouette.
- category: correct depth of frame for the requested category (see below); in category 4 the object is big and dominant.
- colour: clean bright background contrasting the object; the object is the most saturated spot; nothing dark, dim or muddy.
- defects: 2 = no text/digits, no extra objects, no people, not cropped (cat 1-3), no broken geometry, top 12% free.
Be strict: AI images often look fine at first glance but fail on style (too detailed, too realistic). Give 2 for style only if you really cannot tell it apart from the references.
Hard defects (list any that apply): {", ".join(HARD)}.
Note "object_cropped" only applies to categories 1-3. Simple pictorial emblems are fine; any letters or digits are a defect.
Return JSON: {{"candidates": [{{"id": "A", "style": 0, "readability": 0, "category": 0, "colour": 0, "defects": 0, "hard_defects": [], "comment": "short"}}],
"best": "A", "fix": "if no candidate scores 9+: one short English instruction for the image prompt to fix the main problem, else empty"}}"""


def _img(path, side=512):
    im = Image.open(path).convert("RGB"); im.thumbnail((side, side))
    b = io.BytesIO(); im.save(b, "JPEG", quality=85)
    return {"type": "input_image", "image_url": "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()}


def judge(card, cand_paths, usage):
    cat = int(card["category"])
    content = [{"type": "input_text", "text": f"STYLE REFERENCES (category {cat}):"}]
    content += [_img(config.REF_DIR / r, 384) for r in config.JUDGE_REFS[cat]]
    content.append({"type": "input_text", "text":
                    f"Requested object: {card['object']} (card name '{card['name']}'). Category {cat}: {CAT_DESC[cat]}. "
                    f"Background colour asked: {card.get('bg_color')}. Candidates follow, ids in order: "
                    + ", ".join(chr(65 + i) for i in range(len(cand_paths)))})
    for i, p in enumerate(cand_paths):
        content += [{"type": "input_text", "text": f"Candidate {chr(65 + i)}:"}, _img(p)]
    r = OpenAI().responses.create(model=config.TEXT_MODEL, reasoning={"effort": "low"},
                                  text={"format": {"type": "json_object"}},
                                  input=[{"role": "system", "content": RUBRIC}, {"role": "user", "content": content}])
    usage.add_llm(r.usage)
    out = json.loads(r.output_text)
    for c in out.get("candidates", []):
        keys = ("style", "readability", "category", "colour", "defects")
        c["mean"] = sum(int(c.get(k, 0)) for k in keys)  # 0-10, same scale as the human checklist
        c["hard"] = [d for d in c.get("hard_defects", []) if d in HARD]
        # human rule: a 0 in readability or defects is a reject regardless of the total
        c["pass"] = not c["hard"] and c["mean"] >= config.PASS_SCORE and c.get("readability", 0) > 0 and c.get("defects", 0) > 0
    return out
