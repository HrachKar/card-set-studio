"""Step 2. Card spec (from the composer) -> image prompt. Templates per category follow analysis section 3."""

STYLE = ("stylized 3D casual mobile game collectible card art, warm animated-movie look, "
         "soft rounded chunky shapes, slightly exaggerated proportions, no outlines, "
         "every object keeps its real material (painted wood, brass, iron, leather, fabric, ceramic, glass, baked food) "
         "with soft hand-painted texture and medium detail, matte or satin surfaces, "
         "warm soft diffuse lighting like a sunny afternoon, gentle soft highlights, soft contact shadow, "
         "the object is the most saturated element, background slightly softer, single object centered, "
         "fills about 75% of the width, top 12% of the frame kept clear, simplified forms, "
         "thick chunky parts instead of thin lattices or wires, no fine fibers or strands, no small scattered details")
NEG = ("No text, letters, numbers, logos, frames, borders, rounded corners, card UI, stars, "
       "outlines, photorealism, dark gloomy tones, clutter, people, "
       "glossy plastic toy look, wet shine, chrome or mirror reflections, neon glow.")


def scene(c):
    obj, col, bg, view = c["object"], c.get("bg_color", ""), c.get("bg_treatment") or "soft gradient", c.get("view", "")
    cat = int(c["category"])
    if cat == 1:
        return (f"{obj}, floating in the air, {view or 'slightly tilted for dynamism'}, no surface, no ground. "
                f"Plain background: {col} with soft gradient and {bg}")
    if cat == 2:
        return (f"{obj} standing on a plain flat floor of lighter {col}, {view or 'three-quarter view slightly from above'}. "
                f"Behind it a plain vertical {col} wall with {bg}. No environment details")
    if cat == 3:
        return (f"{obj} placed on {c.get('surface') or 'a realistic wooden table'} (stylized soft painted texture, bright and warm, the surface occupies the lower quarter of the frame), "
                f"the whole object visible with space around it, {view or 'three-quarter view slightly from above'}. "
                f"Behind it a volumetric background: a saturated {col} wall with {bg} and a gentle light glow "
                f"behind the object, softly blurred, no sun rays, bright and cheerful, no dark vignette")
    return (f"{obj} in its real environment: {c.get('environment') or 'its natural surroundings with blue sky'}; {view + '; ' if view else ''}"
            f"the object is the clear central hero and fills about 70-80% of the frame, tall or wide objects may be cropped by the frame edge, "
            f"the environment is recognizable but simplified: a few large shapes of the landscape and sky with fluffy clouds, "
            f"only a little secondary detail, softly blurred, bright daylight, no characters")


def build(c, fix_note=""):
    p = (f"Using the attached images ONLY as a style reference (rendering, materials, lighting, "
         f"palette, composition, background treatment) — do not copy their objects — "
         f"create a new card illustration of {scene(c)}. Style: {STYLE}. Vertical 9:10 composition. {NEG}")
    if c.get("set_context"):
        p += (f" Context of this card set: {c['set_context']}. Let this context shape only the surface, environment and "
              f"background mood; show no people and no other objects from that day.")
    if fix_note:
        p += f" Important: {fix_note}"
    return p
