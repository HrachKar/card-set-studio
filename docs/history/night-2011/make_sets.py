"""Hand-written sets (Claude, 20.11 night, no API). Archetype rule: most cards are the first things a player names for the genre.
Run: PYTHONPATH=. python3 night-2011/make_sets.py  -> night-2011/sets/<genre>.json (+ validation) and sets.md
Card tuple: (name, category, object, theme_marker, bg_color, extra, class, moment)
  extra = cat1/2: background device | cat3: "surface" or "surface | wall device" | cat4: environment
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from studio.compose import validate

OUT = Path(__file__).resolve().parent / "sets"

GENRES = {
 "wild-west": dict(
  set_name="Wild West",
  archetypes="cowboy hat, sheriff star, saloon, stagecoach, covered wagon, cactus, lasso, cowboy boots with spurs, horseshoe, saddle, water tower, coffee pot on a campfire, canteen, oil lantern, bandana, wagon wheel, banjo, bean pot, steam locomotive, mine cart",
  context="A visitor's day in the Wild West: the frontier town street, the desert trail, a campfire by the red canyon",
  place="frontier town street with wooden boardwalks and a saloon porch; desert trail with sand, cacti and red mesas; campfire with flat stones by a red canyon",
  palette="warm sandy and wooden tones on clean bright backgrounds: sky blue, turquoise, orange, purple, green, pink, yellow, red",
  motif="horseshoe",
  variants={
   "A": [
    ("Cowboy Hat", 1, "a brown leather cowboy hat with a curled brim and a red woven band", "tall pinched crown and curled brim", "sky blue", "sunburst rays", "clothing", "put on in the morning before the walk"),
    ("Coffee Pot", 3, "a blue enamel tin coffee pot with a wooden handle", "speckled enamel and a curved spout", "orange", "flat campfire stones with a few glowing embers | faint repeating pattern of horseshoe silhouettes", "drink", "campfire coffee at sunset"),
    ("Saloon", 4, "a two-storey wooden saloon with swinging half doors, a balcony and a stepped false front", "swinging half doors and false front", "", "sunny frontier town street with a dusty road and pale mesas", "architecture", "the heart of the town street"),
    ("Saddle", 2, "a brown leather western saddle with a saddle horn and stirrups on a wooden saddle stand", "saddle horn and tooled leather", "purple", "concentric circles", "equipment", "waiting at the stable before the ride"),
    ("Sheriff Star", 1, "a shiny golden six-point sheriff star badge with ball tips", "six points with round tips", "green", "faint repeating pattern of horseshoe silhouettes", "accessory", "seen on the sheriff's office door"),
    ("Cactus Pot", 3, "a round prickly pear cactus with pink flowers in a terracotta pot", "flat paddle pads with spines and pink flowers", "pink", "a wooden saloon porch floor", "nature", "decorates the porch of the town street"),
    ("Lasso", 1, "a coiled golden rope lasso with a loop and a honda knot", "big open loop and coiled rope", "yellow", "diagonal stripes", "equipment", "practice on the ranch fence"),
    ("Rocking Chair", 2, "a wooden porch rocking chair with curved runners and a red cushion", "curved rockers", "turquoise", "soft waves", "furniture", "rest on the porch at noon"),
    ("Stagecoach", 4, "a red and yellow stagecoach with four big wooden wheels, a curved roof and a luggage rack", "high wheels and luggage rack", "", "desert trail with sand, a few cacti and red mesas under a blue sky", "transport", "the ride along the desert trail"),
    ("Apple Pie", 3, "a golden lattice apple pie in a tin dish", "homemade lattice crust", "red", "a red-and-white checkered tablecloth on a porch table", "food", "lunch on the porch"),
   ],
   "B": [
    ("Horseshoe", 1, "a shiny iron horseshoe with nail holes, open end up", "U shape with nail holes", "turquoise", "sunburst rays", "equipment", "found by the stable for luck"),
    ("Campfire Beans", 3, "a black cast-iron pot full of red beans with a wooden spoon", "cast-iron pot with a bail handle", "yellow", "flat campfire stones next to a small campfire", "food", "dinner at the campfire"),
    ("Water Tower", 4, "a round wooden water tower on four thick legs with a cone roof", "wooden barrel tank on stilts", "", "edge of a frontier town with a dusty road and a blue sky", "architecture", "seen at the end of the town street"),
    ("Cowboy Boots", 2, "a pair of brown cowboy boots with pointed toes, stitched patterns and silver spurs", "spurs and pointed toes", "purple", "vertical stripes", "clothing", "pulled on before the ride"),
    ("Canteen", 1, "a round metal canteen covered in brown felt with a leather strap and a cork", "felt cover and leather strap", "orange", "soft gradient", "equipment", "water on the desert trail"),
    ("Oil Lantern", 3, "a red metal oil lantern with a glass globe and a warm flame", "glass globe and wire handle", "sky blue", "the top of a wooden barrel | faint repeating pattern of horseshoe silhouettes", "device", "lights the camp at sunset"),
    ("Bandana", 1, "a red cotton bandana with a white paisley print, tied in a knot", "paisley print and knot", "green", "faint repeating pattern of horseshoe silhouettes", "clothing", "dust protection on the trail"),
    ("Barrel", 2, "a sturdy wooden barrel with iron hoops", "oak staves and iron hoops", "pink", "concentric circles", "furniture", "stands outside the general store"),
    ("Covered Wagon", 4, "a covered wagon with a white canvas top and big wooden wheels", "arched white canvas top", "", "desert trail with sand, sagebrush and red mesas", "transport", "passes the visitor on the trail"),
    ("Banjo", 3, "a wooden banjo with a round drum body and a long neck", "round drum body", "red", "a hay bale | plain wall with light glow", "device", "music at the campfire"),
   ],
   "C": [
    ("Cowboy Hat", 1, "a light tan cowboy hat with a brown leather band and a curled brim", "pinched crown and curled brim", "purple", "soft waves", "clothing", "the visitor's new hat from the store"),
    ("Skillet Bread", 3, "golden cornbread in a black cast-iron skillet", "cast-iron skillet with a short handle", "sky blue", "flat campfire stones", "food", "breakfast before leaving camp"),
    ("Sheriff Office", 4, "a small wooden sheriff office with a porch, a bench and a big golden star above the door", "golden star above the door", "", "sunny frontier town street with boardwalks", "architecture", "the visitor greets the sheriff's town"),
    ("Wagon Wheel", 2, "a big wooden wagon wheel with thick spokes and an iron rim, standing upright", "thick wooden spokes and iron rim", "yellow", "sunburst rays", "equipment", "leaning by the blacksmith"),
    ("Sheriff Star", 1, "a shiny silver five-point star badge in a ring", "star in a ring", "orange", "faint repeating pattern of horseshoe silhouettes", "accessory", "a souvenir from the sheriff"),
    ("Saguaro", 3, "a tall green saguaro cactus with two raised arms and small white flowers", "tall arms raised upward", "pink", "desert sand with small stones", "nature", "the trail landmark at noon"),
    ("Spurs", 1, "a pair of shiny silver cowboy spurs with star-shaped rowels and leather straps", "star rowels", "turquoise", "diagonal stripes", "accessory", "jingling on the boardwalk"),
    ("Mine Cart", 2, "a small iron mine cart full of gold nuggets on a short piece of rail", "gold nuggets heaped above the rim", "green", "concentric circles", "transport", "the gold mine at the canyon"),
    ("Steam Train", 4, "a red and black steam locomotive with a big funnel chimney and a cowcatcher", "funnel chimney and cowcatcher", "", "railway across the desert with red mesas and a blue sky", "transport", "arrives at the town in the afternoon"),
    ("Coffee Pot", 3, "a speckled green enamel coffee pot", "enamel speckles and curved spout", "red", "a wooden crate by the campfire", "drink", "the last coffee of the day"),
   ],
  }),
 "heroic-fantasy": dict(
  set_name="Hero Realm",
  archetypes="castle, wizard hat, spellbook, potion bottle, crystal ball, treasure chest, crown, dragon egg, knight helmet, crest shield, magic staff, map scroll, cauldron, glowing mushrooms, stone portal, wizard tower, armour on a stand, lute, hourglass, gem cave",
  context="A visitor's day in a heroic fantasy kingdom: the castle courtyard, the enchanted forest, the wizard's tower",
  place="stone castle courtyard with banners; enchanted forest with moss, giant mushrooms and old trees; wizard's tower room with a wooden desk and stone walls; mountain path with ancient ruins",
  palette="jewel colours on clean bright backgrounds: royal blue, purple, emerald green, gold yellow, turquoise, pink, orange, red",
  motif="small crown",
  variants={
   "A": [
    ("Wizard Hat", 1, "a tall purple wizard hat with a wide floppy brim and golden moons and stars", "tall pointed bent tip", "yellow", "sunburst rays", "clothing", "a gift from the wizard"),
    ("Potion", 3, "a round glass potion bottle with glowing blue liquid and a cork", "round flask and glowing liquid", "orange", "a wooden alchemist desk | plain wall with light glow", "drink", "bought at the castle market"),
    ("Castle", 4, "a fairy-tale stone castle with round towers, blue cone roofs and banners", "round towers with cone roofs", "", "green hills with a winding road and a blue sky", "architecture", "the morning arrival"),
    ("Treasure Chest", 2, "a wooden treasure chest with golden corners, half open with gold coins and gems", "domed lid with gold inside", "purple", "concentric circles", "furniture", "found in the castle vault"),
    ("Crown", 1, "a golden royal crown with red and blue gems", "pointed golden rim with gems", "sky blue", "faint repeating pattern of small crown silhouettes", "accessory", "seen in the throne room"),
    ("Spellbook", 3, "a thick leather spellbook with brass corners and a glowing gem on the cover", "brass corners and glowing gem", "green", "a stone lectern in the wizard's tower", "device", "read in the wizard's tower"),
    ("Magic Staff", 1, "a wooden wizard staff with a twisted top holding a glowing blue crystal", "twisted top and glowing crystal", "pink", "soft waves", "equipment", "leaning in the wizard's tower"),
    ("Armour Stand", 2, "a shiny knight's armour on a wooden stand, helmet with a red plume", "full plate armour and plume", "turquoise", "vertical stripes", "clothing", "on display in the castle hall"),
    ("Wizard Tower", 4, "a tall crooked stone wizard tower with a purple cone roof and round windows", "crooked tower with cone roof", "", "enchanted forest clearing with giant trees and a blue sky", "architecture", "the visitor's afternoon visit"),
    ("Dragon Egg", 3, "a big speckled green dragon egg with golden scales pattern in a nest of straw", "scaly shell", "red", "a straw nest on a stone ledge", "nature", "the secret of the mountain path"),
   ],
   "B": [
    ("Knight Helmet", 1, "a shiny steel knight helmet with a visor and a red plume", "visor slits and plume", "turquoise", "sunburst rays", "clothing", "tried on in the armoury"),
    ("Cauldron", 3, "a black iron cauldron with bubbling green potion", "round belly and bubbling potion", "yellow", "a stone hearth with a small fire", "device", "the witch's kitchen in the forest"),
    ("Stone Portal", 4, "an ancient round stone portal arch with glowing blue runes inside", "round stone arch with glow", "", "mountain path with ancient ruins and a blue sky", "architecture", "the afternoon wonder"),
    ("Crystal Ball", 2, "a clear crystal ball with a soft purple glow on a golden claw stand", "golden claw stand", "orange", "concentric circles", "device", "the fortune teller's tent"),
    ("Old Key", 1, "a big ornate golden key with a crown-shaped bow", "ornate bow", "purple", "faint repeating pattern of small crown silhouettes", "accessory", "opens the castle gate"),
    ("Mushrooms", 3, "a cluster of glowing blue fantasy mushrooms", "glowing caps", "pink", "green moss on a forest log", "nature", "the enchanted forest at noon"),
    ("Map Scroll", 1, "a rolled parchment map with a red wax seal and a ribbon", "wax seal and curled edges", "green", "diagonal stripes", "equipment", "the visitor's route"),
    ("Crest Shield", 2, "a kite-shaped knight shield with a golden crown crest on blue", "kite shape and crown crest", "red", "vertical stripes", "equipment", "on the armoury wall"),
    ("Castle Gate", 4, "a castle gatehouse with two round towers and a wooden drawbridge", "drawbridge and towers", "", "castle moat with blue water and green hills", "architecture", "entering the castle in the morning"),
    ("Lute", 3, "a wooden lute with a round pear-shaped body and a bent neck", "pear-shaped body and bent neck", "sky blue", "a wooden bench in the castle courtyard", "device", "the minstrel's song at dinner"),
   ],
   "C": [
    ("Crown", 1, "a golden crown with emerald gems and velvet inside", "golden points and gems", "pink", "sunburst rays", "accessory", "the king's crown in the throne room"),
    ("Quill Pen", 3, "a white feather quill in a glass inkpot", "feather quill", "turquoise", "a wooden desk in the wizard's tower", "device", "signing the guest book"),
    ("Treehouse", 4, "a fairy-tale wooden treehouse with round windows built in a giant oak", "house in a giant tree", "", "enchanted forest with sunbeams and moss", "architecture", "the forest at noon"),
    ("Hourglass", 2, "a golden hourglass with blue sand", "golden frame", "purple", "concentric circles", "device", "the wizard's desk"),
    ("Wizard Hat", 1, "a blue wizard hat with silver stars and a bent tip", "pointed bent tip", "orange", "faint repeating pattern of small crown silhouettes", "clothing", "a souvenir from the tower"),
    ("Crystal Cluster", 3, "a cluster of big glowing purple crystals", "sharp glowing crystals", "green", "a mossy stone in the forest", "nature", "found on the mountain path"),
    ("Brass Horn", 1, "a curved brass hunting horn with a leather strap", "curved horn shape", "yellow", "soft waves", "device", "announces the castle tournament"),
    ("Treasure Chest", 2, "a red wooden treasure chest with golden bands and a big lock", "domed lid and lock", "sky blue", "vertical stripes", "furniture", "the treasure of the cave"),
    ("Gem Cave", 4, "a cave entrance in a mountain with piles of gold and glowing gems inside", "gold and gems in a cave mouth", "", "mountain path with green grass and a blue sky", "architecture", "the end of the mountain path"),
    ("Dragon Egg", 3, "a big red dragon egg with golden spots in a straw nest", "scaly shell", "red", "a straw nest on a stone ledge", "nature", "the treasure of the mountain"),
   ],
  }),
 "space-opera": dict(
  set_name="Star Voyage",
  archetypes="starfighter, space helmet, rocket ship, jetpack, space station, hover bike, moon rover, holographic star map, boxy retro robot, pilot goggles, communicator, glowing crystal, meteorite, satellite dish, alien plant, planet globe, spacesuit, astronaut food tube, observatory dome, landing pad",
  context="A visitor's day in a space opera: the spaceport hangar, the starship deck, the alien planet outpost",
  place="sunny spaceport with landing pads and white hangars; starship deck with smooth metal panels; alien planet outpost with pink sand, strange plants and a ringed planet in a bright sky",
  palette="clean white and steel with neon accents on bright backgrounds: sky blue, turquoise, purple, pink, orange, yellow, green, red",
  motif="small ringed planet",
  variants={
   "A": [
    ("Space Helmet", 1, "a round white space helmet with an orange glass visor", "round visor and side lights", "sky blue", "sunburst rays", "clothing", "put on before boarding"),
    ("Star Map", 3, "a holographic star map floating above a round metal projector", "glowing blue hologram of stars", "orange", "the metal deck of a starship | plain wall with light glow", "device", "plans the route on the starship deck"),
    ("Starfighter", 4, "a white and orange starfighter with swept wings and a bubble cockpit", "swept wings and bubble cockpit", "", "sunny spaceport landing pad with white hangars and a light sky", "transport", "the visitor's flight"),
    ("Jetpack", 2, "a silver jetpack with two orange thrusters and shoulder straps", "twin thrusters", "purple", "concentric circles", "equipment", "flying tour of the outpost"),
    ("Pilot Goggles", 1, "a pair of pilot goggles with round orange lenses and a brown leather strap", "round lenses and leather strap", "green", "faint repeating pattern of small ringed planet silhouettes", "accessory", "the pilot's gift"),
    ("Food Tube", 3, "a silver astronaut food tube with a squeezed end", "squeezed metal tube", "yellow", "a white galley table on a starship", "food", "lunch on the starship"),
    ("Communicator", 1, "a chunky handheld communicator with a flip antenna and glowing buttons", "flip antenna", "pink", "diagonal stripes", "device", "talking to the crew"),
    ("Retro Robot", 2, "a friendly boxy retro robot with round eyes, antenna and claw hands", "boxy body and antenna", "turquoise", "vertical stripes", "device", "the hangar helper"),
    ("Moon Rover", 4, "a six-wheeled white moon rover with a dish antenna", "six wheels and dish antenna", "", "alien planet with pink sand and a ringed planet in a light sky", "transport", "the afternoon drive"),
    ("Alien Crystal", 3, "a cluster of glowing turquoise alien crystals", "glowing faceted crystals", "red", "pink alien sand with small stones", "nature", "found at the outpost"),
   ],
   "B": [
    ("Astro Glove", 1, "a white padded spacesuit glove with an orange cuff", "padded fingers and cuff ring", "purple", "sunburst rays", "clothing", "part of the visitor's suit"),
    ("Meteorite", 3, "a dark meteorite with glowing blue cracks", "glowing cracks", "yellow", "pink alien sand", "nature", "a souvenir from the outpost"),
    ("Space Station", 4, "a round white space station with a ring and solar panels docked above a spaceport", "ring and solar panels", "", "bright sky above a spaceport with soft clouds", "architecture", "seen in the morning sky"),
    ("Spacesuit", 2, "a white and orange spacesuit on a stand with a round helmet", "round helmet and chest panel", "sky blue", "concentric circles", "clothing", "the suit-up room"),
    ("Pilot Goggles", 1, "a pair of pilot goggles with green lenses and a strap", "round lenses", "orange", "faint repeating pattern of small ringed planet silhouettes", "accessory", "flight briefing"),
    ("Satellite Dish", 3, "a white satellite dish with a red antenna tip", "round dish", "green", "a metal roof of a spaceport hangar", "device", "calls home from the hangar"),
    ("Planet Globe", 1, "a small globe of a ringed purple planet on a brass stand", "rings around the planet", "turquoise", "soft waves", "device", "the travel guide"),
    ("Retro Robot", 2, "a round-headed red retro robot with a dome head and tracks", "dome head and tracks", "pink", "vertical stripes", "device", "carries the luggage"),
    ("Rocket Ship", 4, "a classic red and white rocket ship with three fins standing on a launch pad", "pointed nose and three fins", "", "sunny spaceport with a launch tower and a light sky", "transport", "the launch in the afternoon"),
    ("Food Tube", 3, "a blue astronaut food tube with a squeezed end next to a small cup", "squeezed metal tube", "red", "a white galley table on a starship", "food", "dinner on board"),
   ],
   "C": [
    ("Space Helmet", 1, "a silver space helmet with a blue visor and an antenna", "visor and antenna", "pink", "sunburst rays", "clothing", "ready for the flight"),
    ("Cargo Crate", 3, "a white metal cargo crate with glowing blue edges", "glowing seams", "sky blue", "the metal floor of a spaceport hangar", "other", "unloading at the hangar"),
    ("Hover Bike", 4, "a sleek orange hover bike floating above the sand", "no wheels, glowing underside", "", "alien planet outpost with pink sand and strange plants", "transport", "a ride across the outpost"),
    ("Jetpack", 2, "a red jetpack with two blue thrusters", "twin thrusters", "yellow", "concentric circles", "equipment", "training flight"),
    ("Communicator", 1, "a wrist communicator with a big round screen", "big round screen", "purple", "faint repeating pattern of small ringed planet silhouettes", "device", "messages from the crew"),
    ("Alien Plant", 3, "a strange alien plant with round glowing pods in a metal pot", "glowing pods", "green", "a metal shelf on a starship deck", "nature", "the greenhouse on board"),
    ("Star Compass", 1, "a brass star compass with a glowing needle", "glowing needle", "orange", "diagonal stripes", "device", "navigation on the trail"),
    ("Pilot Seat", 2, "a padded starship pilot seat with armrest buttons", "armrest buttons and headrest", "turquoise", "vertical stripes", "furniture", "the starship cockpit"),
    ("Observatory", 4, "a white observatory dome with a big telescope opening", "dome with a slit", "", "alien planet with a ringed planet in a light sky", "architecture", "watching the evening sky"),
    ("Meteorite", 3, "a round meteorite with glowing orange cracks", "glowing cracks", "red", "pink alien sand", "nature", "found near the outpost"),
   ],
  }),
 "superheroes": dict(
  set_name="Hero City",
  archetypes="cape, domino mask, power gloves, hero shield, armoured robot suit, hero tower, hero jet, hero car, emblem badge, hero boots, utility belt with pouches, wrist communicator, glowing meteor crystal, science lab flask, grappling hook, hero helmet, HQ console, rescue medal, secret base, rooftop helipad",
  context="A visitor's day in a superhero city: the downtown street, the hero headquarters, the city rooftops",
  place="downtown street with tall buildings; hero headquarters with metal floors and big screens; science lab with white benches; city rooftops with helipads and a bright skyline",
  palette="bold comic colours on clean bright backgrounds: blue, red, yellow, purple, green, orange, pink, turquoise",
  motif="small star burst",
  variants={
   "A": [
    ("Domino Mask", 1, "a black domino mask with two oval eye holes and pointed corners", "eye mask with pointed corners", "yellow", "sunburst rays", "accessory", "the visitor's hero costume"),
    ("Power Gloves", 3, "a pair of big padded red hero gloves with yellow cuffs", "chunky padded fists", "sky blue", "a metal table at hero headquarters", "clothing", "tried on at headquarters"),
    ("Hero Tower", 4, "a tall glass and steel hero headquarters tower with a big round emblem on top", "emblem on top of the tower", "", "downtown city with tall buildings and a blue sky", "architecture", "the morning view downtown"),
    ("Robot Suit", 2, "a big blue and silver armoured robot suit standing on a platform", "chunky armour plates and glowing chest core", "orange", "concentric circles", "equipment", "the HQ exhibit"),
    ("Hero Cape", 1, "a flowing red cape with a golden clasp", "flowing cape with clasp", "purple", "soft waves", "clothing", "fluttering on the rooftop"),
    ("Meteor Crystal", 3, "a glowing green meteor crystal under a glass dome", "glowing crystal under glass", "pink", "a white science lab bench", "nature", "the lab's secret"),
    ("Hero Badge", 1, "a round golden hero badge with a blue star", "star on a round badge", "green", "faint repeating pattern of small star burst silhouettes", "accessory", "the visitor's souvenir"),
    ("Hero Boots", 2, "a pair of red hero boots with yellow tops", "tall boots with folded tops", "turquoise", "vertical stripes", "clothing", "ready for flight"),
    ("Hero Jet", 4, "a sleek blue hero jet with swept wings parked on a rooftop helipad", "swept wings and cockpit", "", "city rooftop helipad with a bright skyline", "transport", "the afternoon flight"),
    ("Lab Flask", 3, "a round glass flask with bubbling purple liquid", "bubbling liquid", "red", "a white science lab bench", "device", "the science lab tour"),
   ],
   "B": [
    ("Hero Shield", 1, "a round blue hero shield with a white wing emblem", "round shield with wing emblem", "orange", "sunburst rays", "equipment", "the hero's gear"),
    ("Comms Watch", 3, "a chunky wrist communicator watch with a big glowing screen", "big glowing screen", "purple", "a metal table at hero headquarters", "device", "hearing a call for help"),
    ("Hero Car", 4, "a sleek red and black hero car with fins", "fins and glowing headlights", "", "downtown city street with tall buildings", "transport", "the downtown ride"),
    ("HQ Console", 2, "a big hero headquarters computer console with three screens and buttons", "three big screens", "sky blue", "concentric circles", "device", "headquarters tour"),
    ("Utility Belt", 1, "a yellow belt with pouches and a round buckle", "pouches all around", "pink", "faint repeating pattern of small star burst silhouettes", "accessory", "gear for the rooftops"),
    ("Meteor Crystal", 3, "a glowing blue meteor crystal on a stand", "glowing crystal", "yellow", "a white science lab bench", "nature", "the lab exhibit"),
    ("Grapple Hook", 1, "a golden grappling hook with a coiled rope", "three hooks and rope", "green", "diagonal stripes", "equipment", "climbing to the rooftops"),
    ("Jet Boots", 2, "a pair of silver boots with small jet thrusters on the heels", "heel thrusters", "red", "vertical stripes", "clothing", "flying test"),
    ("Secret Base", 4, "a secret base hidden in a mountain with a round door and a runway", "round door in a mountain", "", "green mountain by the sea with a blue sky", "architecture", "the hero's secret"),
    ("Rescue Medal", 3, "a golden rescue medal with a red ribbon", "medal with ribbon", "turquoise", "a velvet display stand at headquarters", "accessory", "the hero hall of fame"),
   ],
   "C": [
    ("Hero Cape", 1, "a flowing blue cape with a silver clasp", "flowing cape", "red", "sunburst rays", "clothing", "fluttering in the wind"),
    ("Power Gloves", 3, "a pair of big green hero gloves with silver cuffs", "chunky padded fists", "yellow", "a metal table at hero headquarters", "clothing", "training at headquarters"),
    ("Hero Tower", 4, "a tall hero tower with a round top and an emblem", "round top with emblem", "", "city skyline with a blue sky", "architecture", "the downtown view"),
    ("Robot Suit", 2, "a big green and silver robot suit on a platform", "chunky armour and glowing chest core", "purple", "concentric circles", "equipment", "the exhibit at HQ"),
    ("Hero Helmet", 1, "a silver hero helmet with small fins and a blue visor", "fins and visor", "orange", "faint repeating pattern of small star burst silhouettes", "clothing", "the hero's gear"),
    ("Lab Flask", 3, "a tall glass flask with glowing green liquid", "glowing liquid", "pink", "a white science lab bench", "device", "the lab tour"),
    ("Domino Mask", 1, "a blue domino mask with pointed corners", "pointed corners", "green", "diagonal stripes", "accessory", "the visitor's costume"),
    ("Hero Shield", 2, "a round red hero shield with a golden star burst on a stand", "round shield with emblem", "sky blue", "vertical stripes", "equipment", "shown at headquarters"),
    ("Hero Jet", 4, "a red hero jet with swept wings over the city", "swept wings", "", "city rooftops with a bright skyline", "transport", "the afternoon flight"),
    ("Comms Watch", 3, "a wrist communicator watch with a round glowing screen", "round glowing screen", "turquoise", "a metal table at hero headquarters", "device", "the call for help"),
   ],
  }),
}


def card(n, t, motif):
    name, cat, obj, marker, col, extra, cls, moment = t
    c = dict(n=n, name=name, object=obj, theme_marker=marker, moment=moment, **{"class": cls}, scale="hand",
             silhouette="", category=cat, bg_color=col, bg_treatment="", surface="", environment="", view="")
    if cat in (1, 2):
        c["bg_treatment"] = extra
    elif cat == 3:
        surf, _, treat = extra.partition(" | ")
        c["surface"], c["bg_treatment"] = surf, treat or "plain wall with light glow"
    else:
        c["environment"] = extra
    return c


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    md = ["# Наборы, составленные вручную (Claude, ночь 20.11, без API)", "",
          "Правило: большинство карточек из списка архетипов жанра. Шапка общая на 3 варианта.", ""]
    total_err = 0
    for g, d in GENRES.items():
        head = {k: d[k] for k in ("set_name", "archetypes", "context", "place", "palette", "motif")}
        vs = [dict(id=vid, **head, concept="", cards=[card(i + 1, t, d["motif"]) for i, t in enumerate(cards)])
              for vid, cards in d["variants"].items()]
        for v in vs:
            for c in v["cards"]:
                c["set_context"] = v["context"]
        errs = validate(vs, 3)
        total_err += len(errs)
        (OUT / f"{g}.json").write_text(json.dumps(vs, ensure_ascii=False, indent=1))
        md += [f"## {d['set_name']} ({g})", f"Архетипы: {d['archetypes']}", f"Места: {d['place']}", ""]
        for v in vs:
            md.append(f"**{v['id']}:** " + ", ".join(f"{c['name']} ({c['category']})" for c in v["cards"]))
        md += ["", "Проверка кода: " + ("ок" if not errs else "; ".join(errs)), ""]
        print(g, "errors:", errs)
    (OUT / "sets.md").write_text("\n".join(md))
    return total_err


if __name__ == "__main__":
    main()
