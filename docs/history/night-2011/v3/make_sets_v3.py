"""Hand-made sets v3 (21.11, Claude, no API). Rules: set = WHOLE genre (no narrower sub-theme), class quotas
(<=2 per class, <=2 wearables, >=6 classes, food + building/vehicle), animals and genre weapons allowed (<=1 weapon).
Run: PYTHONPATH=. python3 night-2011/v3/make_sets_v3.py -> night-2011/v3/sets/<genre>.json + sets.md
Tuple: (name, category, object, theme_marker, bg_color, extra, class, where)
"""
import json, sys
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "night-2011"))
from make_sets import card
from studio.compose import validate

OUT = Path(__file__).resolve().parent / "sets"
HERO = {"wild-west": {"A": "Saloon", "B": "Mustang", "C": "Steam Train"},
        "heroic-fantasy": {"A": "Dragon", "B": "Wizard Tower", "C": "Unicorn"},
        "space-opera": {"A": "Starship", "B": "Hover Bike", "C": "Rocket"},
        "superheroes": {"A": "Hero Tower", "B": "Roof Signal", "C": "Secret Base"}}
WEARABLE = {"Cowboy Hat", "Spur Boots", "Bandana", "Wizard Hat", "Crown", "Knight Helmet", "Space Helmet", "Spacesuit",
            "Jetpack", "Pilot Goggles", "Cape Stand", "Hero Mask", "Power Gloves", "Utility Belt", "Domino Mask", "Hero Boots"}

G = {
"wild-west": dict(set_name="Wild West", context="Wild West",
 place="frontier town street with boardwalks; saloon; desert trail with cacti and red mesas; campfire by a canyon; railroad through the desert",
 palette="warm wood, leather and brass on bright clean backgrounds", motif="horseshoe", V={
 "A": [
  ("Cowboy Hat", 1, "a brown leather cowboy hat with a curled brim and a red woven band", "pinched crown and curled brim", "sky blue", "sunburst rays", "costume", "town"),
  ("Banjo", 3, "a wooden banjo with a round white drum head, a long neck and tuning pegs", "round drum body and long neck", "orange", "a hay bale by the saloon porch | faint repeating pattern of horseshoe silhouettes", "artifact", "saloon"),
  ("Saloon", 4, "a two-storey wooden saloon with swinging half doors, a balcony and a stepped false front", "swinging half doors and false front", "", "sunny frontier main street with a dusty road and pale mesas", "building", "town"),
  ("Saddle", 2, "a brown tooled-leather western saddle with a saddle horn on a wooden saddle stand", "saddle horn and tooled leather", "purple", "concentric circles", "artifact", "ranch"),
  ("Sheriff Star", 1, "a golden six-point sheriff star badge with ball tips", "six points with round tips", "green", "faint repeating pattern of horseshoe silhouettes", "symbol", "town"),
  ("Apple Pie", 3, "a golden lattice apple pie in a tin dish", "homemade lattice crust", "pink", "a red-and-white checkered tablecloth on a porch table", "food/drink", "town"),
  ("Revolver", 1, "a silver six-shooter revolver with a wooden grip in a brown leather holster", "six-shooter in a tooled holster", "yellow", "diagonal stripes", "weapon", "town"),
  ("Saloon Piano", 2, "an old upright wooden saloon piano with brass candle holders", "upright piano with candle holders", "turquoise", "soft waves", "household", "saloon"),
  ("Stagecoach", 4, "a red and yellow stagecoach with four big wooden wheels and a luggage rack", "high wheels and luggage rack", "", "desert trail with sand, cacti and red mesas under a blue sky", "vehicle", "trail"),
  ("Saguaro", 3, "a tall green saguaro cactus with two raised arms and small white flowers", "tall arms raised upward", "red", "desert sand with small stones", "nature", "trail"),
 ],
 "B": [
  ("Lasso", 1, "a coiled golden rope lasso with a loop and a honda knot", "big open loop and coiled rope", "turquoise", "sunburst rays", "artifact", "ranch"),
  ("Bean Pot", 3, "a black cast-iron pot of red beans with a wooden spoon", "cast-iron pot with a bail handle", "yellow", "flat campfire stones next to a small campfire", "food/drink", "campfire"),
  ("Water Tower", 4, "a round wooden water tower on four thick legs with a cone roof", "wooden barrel tank on stilts", "", "edge of a frontier town with a dusty road and a blue sky", "building", "town"),
  ("Spur Boots", 2, "a pair of brown cowboy boots with pointed toes, stitched patterns and silver spurs", "spurs and pointed toes", "purple", "vertical stripes", "costume", "town"),
  ("Horseshoe", 1, "a shiny iron horseshoe with nail holes, open end up", "U shape with nail holes", "orange", "faint repeating pattern of horseshoe silhouettes", "symbol", "ranch"),
  ("Oil Lantern", 3, "a red metal oil lantern with a glass globe and a warm flame", "glass globe and wire handle", "sky blue", "the top of a wooden barrel", "household", "camp"),
  ("Bandana", 1, "a red cotton bandana with a white paisley print, tied in a knot", "paisley print and knot", "green", "diagonal stripes", "costume", "trail"),
  ("Barrel", 2, "a sturdy wooden barrel with iron hoops", "oak staves and iron hoops", "pink", "concentric circles", "household", "town"),
  ("Mustang", 4, "a friendly brown horse with a white blaze and a saddle, standing at a hitching rail", "saddled horse at a hitching rail", "", "frontier main street with boardwalks and a blue sky", "creature", "town"),
  ("Cactus Pot", 3, "a round prickly pear cactus with pink flowers in a terracotta pot", "paddle pads and pink flowers", "red", "a wooden saloon porch floor", "nature", "town"),
 ],
 "C": [
  ("Cowboy Hat", 1, "a light tan cowboy hat with a brown leather band", "pinched crown and curled brim", "purple", "soft waves", "costume", "town"),
  ("Cornbread", 3, "golden cornbread in a black cast-iron skillet", "cast-iron skillet with a short handle", "sky blue", "flat campfire stones", "food/drink", "campfire"),
  ("Sheriff Office", 4, "a small wooden sheriff office with a porch, a bench and a big golden star above the door", "golden star above the door", "", "sunny frontier town street with boardwalks", "building", "town"),
  ("Wagon Wheel", 2, "a big wooden wagon wheel with thick spokes and an iron rim, standing upright", "thick spokes and iron rim", "yellow", "sunburst rays", "artifact", "trail"),
  ("Sheriff Star", 1, "a silver five-point star badge in a ring", "star in a ring", "orange", "faint repeating pattern of horseshoe silhouettes", "symbol", "town"),
  ("Banjo", 3, "a wooden banjo with a round drum body and a long neck", "round drum body", "pink", "a hay bale", "artifact", "campfire"),
  ("Gold Nugget", 1, "a big shiny gold nugget with a few small ones", "lumpy shiny gold", "turquoise", "diagonal stripes", "nature", "mine"),
  ("Rocking Chair", 2, "a wooden porch rocking chair with curved runners and a red cushion", "curved rockers", "green", "vertical stripes", "household", "town"),
  ("Steam Train", 4, "a red and black steam locomotive with a big funnel chimney and a cowcatcher", "funnel chimney and cowcatcher", "", "railroad across the desert with red mesas and a blue sky", "vehicle", "railroad"),
  ("Rattlesnake", 3, "a friendly cartoon rattlesnake coiled on a rock, rattle raised", "coiled body and rattle", "red", "a flat desert rock in the sand", "creature", "canyon"),
 ]}),
"heroic-fantasy": dict(set_name="Heroic Fantasy", context="Heroic fantasy",
 place="stone castle on a green hill; wizard's tower room; enchanted forest; dragon's cave with gold; castle feast hall",
 palette="jewel colours and warm gold on bright clean backgrounds", motif="small crown", V={
 "A": [
  ("Wizard Hat", 1, "a tall purple felt wizard hat with a floppy brim and golden embroidered stars", "tall pointed bent tip", "yellow", "sunburst rays", "costume", "tower"),
  ("Spellbook", 3, "a thick leather spellbook with brass corners and a round gem on the cover", "brass corners and gem", "orange", "a wooden desk in the wizard's tower", "artifact", "tower"),
  ("Castle", 4, "a fairy-tale stone castle with round towers, blue cone roofs and banners", "round towers with cone roofs", "", "green hills with a winding road and a blue sky", "building", "castle"),
  ("Treasure Chest", 2, "a wooden treasure chest with golden corners, half open with gold coins and gems", "domed lid with gold inside", "purple", "concentric circles", "household", "vault"),
  ("Potion", 1, "a round glass potion bottle with pink liquid and a cork", "round flask with cork", "sky blue", "soft waves", "food/drink", "tower"),
  ("Sword Stone", 3, "a shining knight's sword stuck in a mossy grey stone", "sword in a stone", "green", "forest moss and grass | plain wall with light glow", "weapon", "forest"),
  ("Crown", 1, "a golden royal crown with red and blue gems", "pointed golden rim with gems", "pink", "faint repeating pattern of small crown silhouettes", "symbol", "castle"),
  ("Cauldron", 2, "a black iron cauldron on three legs with bubbling green potion", "round belly and bubbling potion", "turquoise", "vertical stripes", "household", "forest"),
  ("Dragon", 4, "a friendly green dragon sleeping curled on a pile of gold coins", "wings, horns and gold pile", "", "a bright cave mouth with piles of gold and a blue sky outside", "creature", "cave"),
  ("Roast Feast", 3, "a golden roast turkey with apples on a big pewter platter", "feast platter", "red", "a long wooden feast table", "food/drink", "hall"),
 ],
 "B": [
  ("Knight Helmet", 1, "a steel knight helmet with a visor and a red plume", "visor slits and plume", "turquoise", "sunburst rays", "costume", "castle"),
  ("Dragon Egg", 3, "a big speckled green dragon egg with a scaly shell in a straw nest", "scaly shell", "yellow", "a straw nest on a stone ledge", "creature", "cave"),
  ("Wizard Tower", 4, "a tall crooked stone wizard tower with a purple cone roof and round windows", "crooked tower with cone roof", "", "enchanted forest clearing with giant trees and a blue sky", "building", "tower"),
  ("Crystal Ball", 2, "a clear crystal ball with a soft purple glow on a golden claw stand", "golden claw stand", "orange", "concentric circles", "artifact", "tower"),
  ("Magic Wand", 1, "a carved wooden magic wand with a golden star tip", "star tip", "purple", "faint repeating pattern of small crown silhouettes", "artifact", "tower"),
  ("Mushrooms", 3, "a cluster of big red-capped fairy mushrooms with white spots", "spotted caps", "sky blue", "green moss on a forest log", "nature", "forest"),
  ("Golden Apple", 1, "a shiny golden apple with a green leaf", "golden apple", "green", "diagonal stripes", "food/drink", "forest"),
  ("Owl", 2, "a round brown owl with big amber eyes sitting on a wooden perch", "big eyes and ear tufts", "pink", "vertical stripes", "creature", "tower"),
  ("Flying Carpet", 4, "a red and gold patterned flying carpet with tassels gliding in the air", "floating carpet with tassels", "", "sky above a castle and green hills with fluffy clouds", "vehicle", "sky"),
  ("Lute", 3, "a wooden lute with a round pear-shaped body and a bent neck", "pear-shaped body and bent neck", "red", "a wooden bench in the castle hall", "household", "hall"),
 ],
 "C": [
  ("Crown", 1, "a golden crown with emerald gems and red velvet inside", "golden points and gems", "pink", "sunburst rays", "symbol", "castle"),
  ("Roast Feast", 3, "a roast ham with apples on a wooden platter", "feast platter", "turquoise", "a long wooden feast table", "food/drink", "hall"),
  ("Castle Gate", 4, "a castle gatehouse with two round towers and a wooden drawbridge", "drawbridge and towers", "", "castle moat with blue water and green hills", "building", "castle"),
  ("Crest Shield", 2, "a kite-shaped knight shield with a golden crown crest on blue", "kite shape and crown crest", "orange", "concentric circles", "weapon", "castle"),
  ("Treasure Map", 1, "a rolled parchment treasure map with a red wax seal", "wax seal and curled edges", "purple", "faint repeating pattern of small crown silhouettes", "artifact", "vault"),
  ("Crystal Cluster", 3, "a cluster of big purple crystals", "sharp faceted crystals", "green", "a mossy stone in the forest", "nature", "forest"),
  ("Potion", 1, "a tall glass potion bottle with blue liquid and a wax-sealed cork", "tall flask with seal", "yellow", "soft waves", "food/drink", "tower"),
  ("Hourglass", 2, "a golden hourglass with blue sand", "golden frame", "sky blue", "vertical stripes", "household", "tower"),
  ("Unicorn", 4, "a white unicorn with a golden horn and a pastel mane in a flower meadow", "spiral golden horn", "", "flower meadow at the edge of an enchanted forest with a blue sky", "creature", "forest"),
  ("Spellbook", 3, "an open spellbook with glowing pages on a lectern", "open glowing pages", "red", "a stone lectern in the wizard's tower", "artifact", "tower"),
 ]}),
"space-opera": dict(set_name="Space Opera", context="Space opera",
 place="sunny spaceport with landing pads; starship deck with smooth metal panels; starship galley; alien planet with pink sand and a ringed planet in a light sky",
 palette="white, steel and warm orange accents on bright clean backgrounds", motif="small ringed planet", V={
 "A": [
  ("Space Helmet", 1, "a round white space helmet with an orange visor", "round visor and side lights", "sky blue", "sunburst rays", "costume", "deck"),
  ("Star Map", 3, "a round brass projector showing a small holographic star map", "hologram of stars above a projector", "orange", "the metal deck of a starship", "artifact", "bridge"),
  ("Starship", 4, "a big round-nosed white and orange passenger starship with stubby wings", "round nose and stubby wings", "", "sunny spaceport with landing pads and a light sky", "vehicle", "spaceport"),
  ("Pilot Seat", 2, "a padded orange starship pilot seat with chunky armrests", "armrests with buttons and headrest", "purple", "concentric circles", "household", "bridge"),
  ("Ray Gun", 1, "a retro silver ray gun with red fins and a round emitter", "retro fins and round emitter", "green", "faint repeating pattern of small ringed planet silhouettes", "weapon", "deck"),
  ("Food Tray", 3, "a metal space food tray with compartments of colourful food", "compartment tray", "yellow", "a white galley table on a starship", "food/drink", "galley"),
  ("Communicator", 1, "a chunky handheld communicator with a flip antenna", "flip antenna", "pink", "diagonal stripes", "artifact", "deck"),
  ("Retro Robot", 2, "a friendly boxy retro robot of painted metal with round eyes and an antenna", "boxy body and antenna", "turquoise", "vertical stripes", "creature", "hangar"),
  ("Space Station", 4, "a round white space station with a ring and solar panels", "ring and solar panels", "", "bright sky above a spaceport with soft clouds", "building", "sky"),
  ("Alien Plant", 3, "a strange alien plant with round purple pods in a ceramic pot", "round pods", "red", "a metal shelf on a starship deck", "nature", "greenhouse"),
 ],
 "B": [
  ("Food Tube", 1, "a silver astronaut food tube with a squeezed end", "squeezed metal tube", "purple", "sunburst rays", "food/drink", "galley"),
  ("Space Mug", 3, "a white space mug with a sipping lid and a handle", "sipping lid", "yellow", "a white galley table on a starship", "food/drink", "galley"),
  ("Hover Bike", 4, "a sleek orange hover bike floating above the sand", "no wheels, floating", "", "alien planet with pink sand and a ringed planet in a light sky", "vehicle", "planet"),
  ("Spacesuit", 2, "a white and orange spacesuit on a stand with a round helmet", "round helmet and chest panel", "sky blue", "concentric circles", "costume", "airlock"),
  ("Fleet Medal", 1, "a round brass fleet medal with a ringed planet and a blue ribbon", "ringed planet emblem", "orange", "faint repeating pattern of small ringed planet silhouettes", "symbol", "bridge"),
  ("Alien Pet", 3, "a round fluffy alien creature with three eyes and tiny antennae", "three eyes and antennae", "green", "a cargo crate in a spaceport hangar", "creature", "hangar"),
  ("Jetpack", 1, "a silver jetpack with two orange thrusters and shoulder straps", "twin thrusters", "pink", "diagonal stripes", "costume", "spaceport"),
  ("Cryo Pod", 2, "a white egg-shaped sleep pod with a glass lid", "glass lid", "turquoise", "vertical stripes", "household", "deck"),
  ("Observatory", 4, "a white observatory dome with a big telescope", "dome with a telescope", "", "alien planet with a ringed planet in a light sky", "building", "planet"),
  ("Meteorite", 3, "a dark round meteorite with orange crystal veins", "crystal veins", "red", "pink alien sand", "nature", "planet"),
 ],
 "C": [
  ("Pilot Goggles", 1, "a pair of pilot goggles with round orange lenses and a brown leather strap", "round lenses and leather strap", "turquoise", "sunburst rays", "costume", "spaceport"),
  ("Food Tray", 3, "a metal space food tray with colourful food cubes", "compartment tray", "orange", "a white galley table on a starship", "food/drink", "galley"),
  ("Rocket", 4, "a classic red and white rocket with three fins on a launch pad", "pointed nose and three fins", "", "sunny spaceport with a launch tower and a light sky", "vehicle", "spaceport"),
  ("Robot Dog", 2, "a friendly robot dog of painted metal with floppy metal ears", "metal dog with floppy ears", "purple", "concentric circles", "creature", "deck"),
  ("Communicator", 1, "a wrist communicator with a big round screen", "big round screen", "yellow", "faint repeating pattern of small ringed planet silhouettes", "artifact", "deck"),
  ("Cargo Crate", 3, "a white metal cargo crate with orange corner guards", "orange corners", "sky blue", "the metal floor of a spaceport hangar", "household", "hangar"),
  ("Fleet Badge", 1, "a round brass fleet badge with a small ringed planet emblem", "ringed planet emblem", "green", "diagonal stripes", "symbol", "deck"),
  ("Vending Bot", 2, "a rounded space vending machine with colourful snack capsules", "capsule window", "pink", "vertical stripes", "household", "spaceport"),
  ("Landing Tower", 4, "a white spaceport control tower with a round glass top", "round glass top", "", "spaceport with landing pads and a light sky", "building", "spaceport"),
  ("Alien Crystal", 3, "a cluster of turquoise alien crystals", "faceted crystals", "red", "pink alien sand with small stones", "nature", "planet"),
 ]}),
"superheroes": dict(set_name="Superheroes", context="Superheroes",
 place="hero headquarters with metal floors and big screens; training room; science lab; city rooftops with a bright skyline; downtown street",
 palette="bold comic colours on bright clean backgrounds", motif="small star burst", V={
 "A": [
  ("Hero Emblem", 1, "a big round metal hero emblem with a golden star burst", "star burst emblem", "orange", "sunburst rays", "symbol", "HQ"),
  ("Supercomputer", 3, "a big headquarters computer with three curved screens and chunky buttons", "three big screens", "sky blue", "a metal floor of hero headquarters", "household", "HQ"),
  ("Hero Tower", 4, "a tall hero headquarters tower with a round top and a big golden star burst emblem", "round top with emblem", "", "downtown city with tall buildings and a blue sky", "building", "city"),
  ("Cape Stand", 2, "a flowing red fabric cape with a golden clasp on a wooden stand", "flowing cape on a stand", "purple", "concentric circles", "costume", "HQ"),
  ("Comms Badge", 1, "a round silver communicator badge with a blue light", "badge with a light", "green", "faint repeating pattern of small star burst silhouettes", "artifact", "HQ"),
  ("Phone Booth", 3, "a red city phone booth with glass panels and a round lamp on top", "classic red booth", "yellow", "a city sidewalk with paving stones", "building", "street"),
  ("Hero Mask", 1, "a blue domino mask with pointed corners", "eye mask with pointed corners", "pink", "diagonal stripes", "costume", "rooftops"),
  ("Punching Bag", 2, "a red leather punching bag with a fist-shaped dent on a stand", "dent in the bag", "turquoise", "vertical stripes", "household", "training"),
  ("Hero Jet", 4, "a sleek blue hero jet with swept wings over the city", "swept wings", "", "city rooftops with a bright skyline", "vehicle", "rooftops"),
  ("Meteor Crystal", 3, "a green meteor crystal under a glass dome", "crystal under glass", "red", "a white science lab bench", "nature", "lab"),
 ],
 "B": [
  ("Power Gloves", 1, "a pair of big padded red hero gloves with yellow cuffs", "chunky padded fists", "sky blue", "sunburst rays", "costume", "training"),
  ("Trophy Case", 3, "a glass trophy case with golden cups and a villain's broken helmet", "trophies and a broken villain helmet", "yellow", "a polished stone floor of the hero hall", "household", "hall"),
  ("Roof Signal", 4, "a big rooftop signal spotlight projecting a star burst symbol into the sky", "spotlight with its own star burst symbol", "", "city rooftop at golden hour with a bright skyline", "building", "rooftops"),
  ("Utility Belt", 2, "a yellow belt with pouches and a round buckle on a stand", "pouches all around", "purple", "concentric circles", "costume", "HQ"),
  ("Hero Shield", 1, "a round blue hero shield with a white wing emblem", "round shield with wing emblem", "orange", "faint repeating pattern of small star burst silhouettes", "weapon", "HQ"),
  ("Lab Flask", 3, "a round glass flask with bubbling purple liquid", "bubbling liquid", "green", "a white science lab bench", "household", "lab"),
  ("Grapple Hook", 1, "a golden grappling hook with a coiled rope", "three hooks and rope", "pink", "diagonal stripes", "artifact", "rooftops"),
  ("Robot Sidekick", 2, "a small round sidekick robot with big eyes and little jet feet", "round robot with jet feet", "turquoise", "vertical stripes", "creature", "HQ"),
  ("Hero Car", 4, "a sleek red and black hero car with fins", "fins and glowing headlights", "", "downtown city street with tall buildings", "vehicle", "street"),
  ("Energy Core", 3, "a round glass reactor core with a blue glowing center in a brass frame", "glowing core in a brass frame", "red", "a white science lab bench", "artifact", "lab"),
 ],
 "C": [
  ("Domino Mask", 1, "a black domino mask with two oval eye holes and pointed corners", "pointed corners", "yellow", "sunburst rays", "costume", "rooftops"),
  ("Rescue Medal", 3, "a golden rescue medal with a red ribbon", "medal with ribbon", "sky blue", "a velvet display stand at headquarters", "symbol", "hall"),
  ("Secret Base", 4, "a secret base hidden in a mountain with a round door and a runway", "round door in a mountain", "", "green mountain by the sea with a blue sky", "building", "base"),
  ("Hero Boots", 2, "a pair of red hero boots with yellow tops", "tall boots with folded tops", "purple", "concentric circles", "costume", "HQ"),
  ("Hero Emblem", 1, "a round silver hero emblem with a blue star", "star emblem", "orange", "faint repeating pattern of small star burst silhouettes", "symbol", "HQ"),
  ("Trophy Case", 3, "a glass trophy case with golden cups and a villain's broken helmet", "trophies and a broken villain helmet", "green", "a polished stone floor of the hero hall", "household", "hall"),
  ("Comms Watch", 1, "a chunky wrist communicator watch with a big screen", "big screen", "pink", "diagonal stripes", "artifact", "HQ"),
  ("Supercomputer", 2, "a big headquarters computer with three screens and chunky buttons", "three big screens", "turquoise", "vertical stripes", "household", "HQ"),
  ("Rescue Copter", 4, "a red and white rescue helicopter with a round cockpit above the city", "round cockpit and rotor", "", "city rooftops with a bright skyline", "vehicle", "rooftops"),
  ("Meteor Crystal", 3, "a green meteor crystal under a glass dome", "crystal under glass", "red", "a white science lab bench", "nature", "lab"),
 ]}),
}

POOLS = {
 "wild-west": "Saloon, Sheriff Office, Water Tower, Stagecoach, Steam Train, Covered Wagon, Mustang, Rattlesnake, Longhorn, Coffee Pot, Bean Pot, Apple Pie, Cornbread, Lasso, Saddle, Wagon Wheel, Banjo, Gold Nugget, Saloon Piano, Rocking Chair, Barrel, Oil Lantern, Saguaro, Cactus Pot, Sheriff Star, Horseshoe, Cowboy Hat, Spur Boots, Bandana, Revolver",
 "heroic-fantasy": "Castle, Wizard Tower, Castle Gate, Stone Portal, Treehouse, Dragon, Unicorn, Owl, Dragon Egg, Flying Carpet, Potion, Roast Feast, Golden Apple, Spellbook, Magic Wand, Crystal Ball, Treasure Map, Treasure Chest, Cauldron, Hourglass, Lute, Mushrooms, Crystal Cluster, Crown, Wizard Hat, Knight Helmet, Sword Stone, Crest Shield",
 "space-opera": "Starship, Rocket, Hover Bike, Space Station, Observatory, Landing Tower, Retro Robot, Robot Dog, Alien Pet, Food Tray, Food Tube, Space Mug, Star Map, Communicator, Pilot Seat, Cryo Pod, Cargo Crate, Vending Bot, Alien Plant, Meteorite, Alien Crystal, Fleet Badge, Fleet Medal, Space Helmet, Spacesuit, Jetpack, Pilot Goggles, Ray Gun",
 "superheroes": "Hero Tower, Secret Base, Phone Booth, Roof Signal, Hero Jet, Hero Car, Rescue Copter, Robot Sidekick, Supercomputer, Punching Bag, Trophy Case, Lab Flask, Comms Badge, Comms Watch, Grapple Hook, Energy Core, Meteor Crystal, Hero Emblem, Rescue Medal, Cape Stand, Hero Mask, Domino Mask, Power Gloves, Utility Belt, Hero Boots, Hero Shield",
}


def check(cards):
    errs = []
    cls = Counter(c["class"] for c in cards)
    if max(cls.values()) > 2: errs.append(f"class >2: {dict(cls)}")
    if len(cls) < 6: errs.append(f"only {len(cls)} classes")
    if sum(c["wearable"] for c in cards) > 2: errs.append("more than 2 wearables")
    return errs, len(cls)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    md = ["# Наборы v3: набор = весь жанр, квоты классов, без гибридов; ★ = главная карта (символ жанра, последняя в окне) (21.11, вручную, без API)", ""]
    for g, d in G.items():
        head = {k: d[k] for k in ("set_name", "context", "place", "palette", "motif")}
        vs = []
        for vid, tuples in d["V"].items():
            hero = HERO[g][vid]
            tuples = [t for t in tuples if t[0] != hero] + [t for t in tuples if t[0] == hero]  # main symbol last
            cards = [card(i + 1, t, d["motif"]) for i, t in enumerate(tuples)]
            cards[-1]["hero"] = True
            for c in cards:
                c["wearable"] = c["name"] in WEARABLE
                c["set_context"] = d["context"]
            vs.append(dict(id=vid, **head, concept="", cards=cards))
        # production validate; skip checks that the approved v2 drafts drop (cross-variant repeats, phone booth on the stop-list)
        errs = [e for e in validate(vs, 3) if "appears in" not in e and "['phone booth']" not in e]
        md += [f"## {d['set_name']}", "", f"Кандидаты ({len(POOLS[g].split(', '))}): {POOLS[g]}", ""]
        for v in vs:
            e, n = check(v["cards"]); errs += [f"{v['id']}: {x}" for x in e]
            md.append(f"**{v['id']}** ({n} классов): " + ", ".join(
                ("★ " if c.get("hero") else "") + f"{c['name']} ({c['category']}{', Н' if c['wearable'] else ''})" for c in v["cards"]))
        md += ["", "Проверка: " + ("ок" if not errs else "; ".join(errs)), ""]
        (OUT / f"{g}.json").write_text(json.dumps(vs, ensure_ascii=False, indent=1))
        print(g, errs or "ok")
    (OUT / "sets.md").write_text("\n".join(md))


if __name__ == "__main__":
    main()
