"""Variant A of the hand run v2 (sub-theme + class quotas). Claude, 20.11 night, no API.
Run: PYTHONPATH=. python3 night-2011/v2/make_sets_v2.py -> night-2011/v2/sets_A/<genre>.json
Then check without API: python3 -m studio new --theme X --sets night-2011/v2/sets_A/<genre>.json --stop-after dry --name <n>
"""
import json, sys
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "night-2011"))
from make_sets import card
from studio.compose import validate

OUT = Path(__file__).resolve().parent / "sets_A"
WEAR = {"costume"}

G = {
 "wild-west": dict(set_name="Frontier Town", context="Wild West: the frontier town, its main street and saloon",
  place="frontier town main street with wooden boardwalks; saloon porch and interior; sheriff office",
  palette="warm wood and leather on bright clean backgrounds", motif="horseshoe", cards=[
  ("Cowboy Hat", 1, "a brown leather cowboy hat with a curled brim and a red woven band", "pinched crown and curled brim", "sky blue", "sunburst rays", "costume", "main street"),
  ("Coffee Pot", 3, "a blue speckled enamel coffee pot with a wooden handle", "speckled enamel and curved spout", "orange", "a small black iron stove top in the sheriff office | faint repeating pattern of horseshoe silhouettes", "food/drink", "sheriff office"),
  ("Saloon", 4, "a two-storey wooden saloon with swinging half doors, a balcony and a stepped false front", "swinging half doors and false front", "", "sunny frontier main street with a dusty road and pale mesas", "building", "main street"),
  ("Saloon Piano", 2, "an old upright wooden saloon piano with brass candle holders", "upright piano with candle holders", "purple", "concentric circles", "household", "saloon"),
  ("Sheriff Star", 1, "a golden six-point sheriff star badge with ball tips", "six points with round tips", "green", "faint repeating pattern of horseshoe silhouettes", "symbol", "sheriff office"),
  ("Apple Pie", 3, "a golden lattice apple pie in a tin dish", "homemade lattice crust", "pink", "a red-and-white checkered tablecloth on a porch table", "food/drink", "saloon porch"),
  ("Lasso", 1, "a coiled golden rope lasso with a loop and a honda knot", "big open loop and coiled rope", "yellow", "diagonal stripes", "artifact", "main street"),
  ("Saddle", 2, "a brown tooled-leather western saddle with a saddle horn on a wooden saddle stand", "saddle horn and tooled leather", "turquoise", "soft waves", "artifact", "stable"),
  ("Stagecoach", 4, "a red and yellow stagecoach with four big wooden wheels and a luggage rack", "high wheels and luggage rack", "", "frontier main street with wooden storefronts and a blue sky", "vehicle", "main street"),
  ("Cactus Pot", 3, "a round prickly pear cactus with pink flowers in a terracotta pot", "paddle pads and pink flowers", "red", "a wooden saloon porch floor", "nature", "saloon porch"),
 ]),
 "heroic-fantasy": dict(set_name="Magic Kingdom", context="Heroic fantasy: the magic kingdom, its castle and the wizard's tower",
  place="stone castle with banners on a green hill; wizard's tower room with a wooden desk; castle feast hall",
  palette="jewel colours and warm gold on bright clean backgrounds", motif="small crown", cards=[
  ("Wizard Hat", 1, "a tall purple felt wizard hat with a floppy brim and golden embroidered stars", "tall pointed bent tip", "yellow", "sunburst rays", "costume", "tower"),
  ("Spellbook", 3, "a thick leather spellbook with brass corners and a round gem on the cover", "brass corners and gem", "orange", "a wooden desk in the wizard's tower", "artifact", "tower"),
  ("Castle", 4, "a fairy-tale stone castle with round towers, blue cone roofs and banners", "round towers with cone roofs", "", "green hills with a winding road and a blue sky", "building", "castle"),
  ("Treasure Chest", 2, "a wooden treasure chest with golden corners, half open with gold coins and gems", "domed lid with gold inside", "purple", "concentric circles", "household", "castle vault"),
  ("Magic Wand", 1, "a carved wooden magic wand with a golden star tip and a few sparkles", "star tip", "sky blue", "faint repeating pattern of small crown silhouettes", "artifact", "tower"),
  ("Roast Feast", 3, "a golden roast turkey with apples on a big pewter platter", "feast platter", "green", "a long wooden feast table", "food/drink", "feast hall"),
  ("Potion", 1, "a round glass potion bottle with pink liquid and a cork", "round flask with cork", "turquoise", "soft waves", "food/drink", "tower"),
  ("Cauldron", 2, "a black iron cauldron on three legs with bubbling green potion", "round belly and bubbling potion", "pink", "vertical stripes", "household", "tower"),
  ("Flying Carpet", 4, "a red and gold patterned flying carpet with tassels gliding in the air", "floating carpet with tassels", "", "sky above the castle and green hills with fluffy clouds", "vehicle", "castle sky"),
  ("Dragon Egg", 3, "a big speckled green dragon egg with a scaly shell in a straw nest", "scaly shell", "red", "a straw nest on a stone ledge", "creature", "castle tower"),
 ]),
 "space-opera": dict(set_name="Starship Life", context="Space opera: life on a starship and its spaceport",
  place="starship deck with smooth metal panels and round windows; starship galley; sunny spaceport",
  palette="white, steel and warm orange accents on bright clean backgrounds", motif="small ringed planet", cards=[
  ("Space Helmet", 1, "a round white space helmet with an orange visor", "round visor and side lights", "sky blue", "sunburst rays", "costume", "deck"),
  ("Star Map", 3, "a round brass projector showing a small holographic star map", "hologram of stars above a projector", "orange", "the metal deck of a starship | plain wall with light glow", "artifact", "bridge"),
  ("Starship", 4, "a big round-nosed white and orange passenger starship with stubby wings", "round nose and stubby wings", "", "sunny spaceport with landing pads and a light sky", "vehicle", "spaceport"),
  ("Pilot Seat", 2, "a padded orange starship pilot seat with chunky armrests", "armrests with buttons and headrest", "purple", "concentric circles", "household", "bridge"),
  ("Fleet Badge", 1, "a round brass fleet badge with a small ringed planet emblem", "ringed planet emblem", "green", "faint repeating pattern of small ringed planet silhouettes", "symbol", "deck"),
  ("Food Tray", 3, "a metal space food tray with compartments of colourful food", "compartment tray", "yellow", "a white galley table on a starship", "food/drink", "galley"),
  ("Communicator", 1, "a chunky handheld communicator with a flip antenna", "flip antenna", "pink", "diagonal stripes", "artifact", "deck"),
  ("Retro Robot", 2, "a friendly boxy retro robot made of painted metal with round eyes and an antenna", "boxy body and antenna", "turquoise", "vertical stripes", "creature", "hangar"),
  ("Space Station", 4, "a round white space station with a ring and solar panels", "ring and solar panels", "", "bright sky above a spaceport with soft clouds", "building", "spaceport sky"),
  ("Alien Plant", 3, "a strange alien plant with round purple pods in a ceramic pot", "round pods", "red", "a metal shelf on a starship deck", "nature", "greenhouse"),
 ]),
 "superheroes": dict(set_name="Hero HQ", context="Superheroes: the heroes' headquarters",
  place="hero headquarters with metal floors and big screens; training room; rooftop hangar of the hero tower",
  palette="bold comic colours on bright clean backgrounds", motif="small star burst", cards=[
  ("Hero Emblem", 1, "a big round metal hero emblem with a golden star burst", "star burst emblem", "orange", "sunburst rays", "symbol", "HQ"),
  ("Supercomputer", 3, "a big headquarters computer with three curved screens and chunky buttons", "three big screens", "sky blue", "a metal floor of hero headquarters", "household", "HQ"),
  ("Hero Tower", 4, "a tall hero headquarters tower with a round top and a big emblem", "round top with emblem", "", "downtown city with tall buildings and a blue sky", "building", "city"),
  ("Cape Stand", 2, "a flowing red fabric cape with a golden clasp on a wooden stand", "flowing cape on a stand", "purple", "concentric circles", "costume", "HQ"),
  ("Comms Badge", 1, "a round silver communicator badge with a blue light", "badge with a light", "green", "faint repeating pattern of small star burst silhouettes", "artifact", "HQ"),
  ("Hero Mug", 3, "a white ceramic mug with a star burst emblem and steam from hot cocoa", "emblem mug with steam", "yellow", "a metal table at hero headquarters", "food/drink", "HQ"),
  ("Meteor Crystal", 1, "a glowing green meteor crystal", "glowing crystal", "pink", "soft waves", "nature", "lab"),
  ("Punching Bag", 2, "a red leather punching bag with a fist-shaped dent hanging from a stand", "dent in the bag", "turquoise", "vertical stripes", "household", "training room"),
  ("Hero Jet", 4, "a sleek blue hero jet with swept wings in a hangar", "swept wings", "", "rooftop hangar of the hero tower with a bright skyline", "vehicle", "hangar"),
  ("Rescue Medal", 3, "a golden rescue medal with a red ribbon", "medal with ribbon", "red", "a velvet display stand at headquarters", "symbol", "hall"),
 ]),
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for g, d in G.items():
        head = {k: d[k] for k in ("set_name", "context", "place", "palette", "motif")}
        cards = [card(i + 1, t, d["motif"]) for i, t in enumerate(d["cards"])]
        for c in cards:
            c["wearable"] = c["class"] in WEAR
            c["set_context"] = d["context"]
        v = [dict(id="A", **head, concept="", cards=cards)]
        errs = validate(v, 1)
        cls = Counter(c["class"] for c in cards)
        if max(cls.values()) > 2: errs.append(f"class quota broken: {cls}")
        if sum(c["wearable"] for c in cards) > 1: errs.append("more than 1 wearable")
        if len(cls) < 6: errs.append(f"only {len(cls)} classes")
        (OUT / f"{g}.json").write_text(json.dumps(v, ensure_ascii=False, indent=1))
        print(g, len(cls), "classes", errs or "ok")


if __name__ == "__main__":
    main()
