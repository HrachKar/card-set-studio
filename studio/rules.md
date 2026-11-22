# Rules for composing a collection card set (reference-game style)

These rules come from the analysis of the reference collection (Summer).
The game designer may edit this file; the composer agent reads it on every run.

## The set is the WHOLE GENRE; fill CLASS QUOTAS (most important)
- Hierarchy: the collection theme is "Movies"; the sub-theme of a set is the GENRE (Wild West, Heroic Fantasy, Space Opera, Superheroes...). There is NO narrower sub-theme inside the set: no single place, profession, route or "day of a visitor".
- Every card is a DIFFERENT representative of the genre, taken from anywhere in its world, like Seafaring: spyglass, buoy, map, ship, anchor, helm, captain's cap, lighthouse, cargo barrel. Not a wardrobe, not a catalogue of one kind of thing.
- Class quotas for the 10 cards. Classes: building/place, vehicle, creature (animals, fantastic creatures, robots), food or drink, artifact (a magic or genre item you hold), household item (furniture, device, container, tool), nature, symbol (badge, medal, emblem object, crown), costume, weapon (a genre archetype shown as an item, never in use).
  - at most 2 cards per class;
  - at most 2 wearable items per set (hat, mask, cape, boots, gloves, helmet, crown all count);
  - at least 6 different classes per set;
  - no class is mandatory: only the diversity counts.
- Each card must be one of the first things a player names for the genre (recognizable at a glance). NO hybrids at all: never stick a theme sign on a random thing (cape cookie, mask locker, hero smoothie, emblem mug, hero cereal). Real collection sets have none. Magic or genre flavour is at most ONE adjective on a real object (Frozen Rose, Ice Castle, Magic Portal, Golden Apple).
- Real materials: at least half of the cards show wood, metal, fabric, ceramic, stone or real food. No neon, no chrome; at most 2 glowing elements per set.
- No people (gold cards are out of scope). No film-set props (cameras, clapperboards).

## Two steps: candidates, then selection
- Step 1 (composer) writes 25-30 candidates for the genre, each with class, category guess, wearable yes/no, and a one-line reason why a player knows it.
- Step 2 (selector, a separate pass that did not write the list) picks 10 by: recognizability at fingernail size, class quotas, all 4 categories (3/2/3/2 ±1), different silhouettes and scales. It writes why each rejected strong candidate was dropped.
- Variants: variant A is the selector's best 10; B and C are alternative picks from the same candidate pool (same header), overlapping by up to 4 cards, each still obeying the quotas.

## What a set is
- A set = 10 different representatives of ONE genre.
- Each card = ONE recognizable everyday object, the first association with the theme. Silhouette must read instantly at thumbnail size (fingernail-sized on a phone). No abstract, rare or "clever" items. No people or characters (they belong to gold cards, which the task excludes). Animals and creatures ARE allowed as objects (horse, dragon, owl, robot), drawn in the same chunky style.
- One idea per card. A pair of linked items is allowed only if they read as one whole (sunscreen + sunglasses).
- No text, letters, numbers or logos on objects. Simple pictorial emblems are fine (a star on a badge).

## Theme must be obvious on EVERY card (most important rule)
- Cover the caption and look at one card alone: a player must say the theme ("Wild West!") at once. If the object exists the same way outside the theme (a plain rope, a stool, a kettle, modern boots, a sandwich), it is FORBIDDEN unless its description carries a strong visual theme marker that changes the silhouette: a lasso with a honda loop, pointed cowboy boots with spurs and stitched patterns, a saddle-shaped stool made of a barrel, a tin coffee pot on campfire stones.
- The marker must come from the object's own shape (spurs, fringe, pointed toe, saddle horn), not from stamping a theme emblem on a generic object. Printed or embossed emblems (a horseshoe on a pot, a trunk, a barrel) are allowed on at most 2 cards per set.
- Every card has a field theme_marker: the concrete visual detail that makes it read as the theme. "Western style" is not a marker; "spurs and a pointed toe" is.
- Prefer the genre's archetypes (sheriff star, saddle, cowboy hat, saloon, covered wagon, horseshoe) over everyday objects with a marker. Never create a new object by attaching a theme sign to an everyday one.

## Places come from the genre
- Field "place" lists 3-4 typical places of the genre (e.g. Wild West: frontier town street, saloon, desert trail, campfire by a canyon). They are only a source for category 3 surfaces and category 4 environments, not a story. Each surface/environment must be one of them and match the object.
- Physical sense: things stand where they really stand (a cactus grows in sand or a clay pot, never from a wooden floor; a kettle sits on campfire stones or a crate, not on "something").

## Common sense (a real person must believe the picture)
- Category 1 and 2 show an object ALONE, so it must be a complete freestanding thing that makes sense on its own: a hat, boots, a lantern, a saddle on its stand. Never a part of a building or a fixed installation pulled out of its place (a door, a window, a wall, a gate, a pump, a counter) on an abstract floor or in the air. Such objects go to category 3-4 inside their place, or are not used.
- In categories 3-4 the object stands where it really is in life: a kettle on campfire stones, a cactus in sand or a pot, a saddle on a fence or a horse rail, a wagon on a dusty road.
- The object is shown whole, in its normal shape and proportions: no melted, bent or invented versions.

## Diversity inside a set (this is what makes a set feel rich)
- Mix object classes: tool/equipment, food or drink, clothing/accessory, transport or architecture, nature element, furniture/device. The order in the window is set later by code (studio/layout.py): it never puts two items of the same class side by side.
- Mix real-world scales: hand-sized (whistle, ticket), furniture/device size (chair, machine), big (lighthouse, ferris wheel, bus). In the frame everything is drawn at the same visual size.
- Mix silhouettes: vertical, horizontal, round.
- Background colour: give each card of categories 1-3 a field "bg_options" with 2-3 colours that contrast with the object (blue bottle on yellow, red booth on green, orange honey on turquoise). Use clean colours: sky blue, blue, yellow, orange, green, purple, pink, red, turquoise, lilac, peach, mint. Do NOT plan the colour layout: code picks one option per card (neighbours differ, at most 3 cards of one temperature in a row, the set palette tilts warm or cool, no colour pattern repeated between variants). Not a rainbow: reference sets often keep one dominant colour family.

## Categories (depth-of-frame scale). All 4 must be present.
Target split for 10 cards: cat1 = 3, cat2 = 2, cat3 = 3, cat4 = 2 (each may deviate by ±1, minimum 1 each).
1. Floating object, no surface. Small hand-held "icon" items (bottle, lollipop, anchor, spyglass). Background: one colour with soft gradient + ONE device: sunburst rays, vertical or diagonal stripes, soft waves, or a simple repeating thematic pattern. Usually tilted for dynamism.
2. Object stands on a plain flat floor of the same colour as the wall but lighter; plain vertical background (gradient, concentric circles, waves, rays, stripes or a faint thematic pattern). Medium standing items, furniture, machines (tea cup, phone booth, claw machine).
3. Object stands on a REALISTIC surface (wooden table, checkered tablecloth, tiled floor, ship deck, sand, wooden porch, stone floor). Background is volumetric: a coloured wall with a faint thematic pattern or a light glow, or a simple matching interior, softly blurred. Items that "need" their surface: food on a table, a thing on a deck.
4. Object inside its real environment (sky with clouds, sea, field, desert, interior hall), environment simplified and blurred, object stays the central hero; large objects may be cropped by the frame edge. Big things that live in a place (lighthouse, ferris wheel, roller coaster, buoy in the sea).

## Mood
- Always bright, friendly, daytime (or warm golden hour). Never night, darkness, gloom, blood or violence in action (a sword on a stand is fine, a fight is not). Category 4 environments are bright with a light sky.
- The object never has the same hue as its background colour.

- Genre weapons are allowed as objects when they are archetypes of the genre (revolver in a holster, sword, shield, war hammer, bow, tournament lance), shown as an item, never in use. Alcohol, tobacco and gambling: not banned by the task; avoid by default, the designer may allow.
- Every object must be understood WITHOUT its caption at thumbnail size: avoid objects that need a name to be recognized (a hand pump, a gold pan with nuggets, a sluice box) and boring utility items (a dinner triangle). Prefer objects with a bold, iconic silhouette.

## Thematic background motif
- Pick 1 simple motif silhouette from the theme (horseshoe for western, star for space). Use it as a background pattern on 2-3 cards of the set, not more. Other cards use rays/stripes/waves/circles/gradient.

## Names
- 1-2 English words, nouns, short, sometimes playful (Bounce, Chains, Gallery, Cargo Barrel, Captain's Cap).

## Main card
- One card per variant is the main symbol of the genre (field "hero": true): the thing a player would draw to say the genre (saloon, dragon, starship, hero tower). It is the last card in the window (highest rarity); its category can be any.

## Order
- Do not plan the order. Code (studio/layout.py) shuffles cards per variant and set: main card last, at most 2 cards of one category in a row, no fixed slots (category 1 is not always card 1 and 6), different layouts in every variant and set. Reason (Hrach 22.11): a hand-planned order turned into one template repeated in every set.

## No protected IP (stop-list)
- Generic archetypes are ALLOWED and wanted (cape, domino mask, gloves, round shield, hammer, robot suit, jetpack, starfighter, wizard hat, sword in stone). Forbidden are only SPECIFIC designs and names of known franchises, even renamed: trademarked names and symbols (lightsaber, droid, Jedi/Sith, blue milk, the bat symbol, the S-shield, Mjolnir, the One Ring, sorting hat, golden snitch) and exact signature designs (X-wing/TIE silhouettes, the red-and-gold Iron Man helmet, the red-white-blue star shield, the horned dragonborn helmet). A rooftop signal spotlight, a phone booth, a utility belt or a round shield with the set's OWN symbol is an archetype and is allowed.
- Test: would a lawyer say "that is THE <franchise> item"? Then change the shape and colours until it is just the archetype.

## Note for the report
- Weapons and animals were banned in earlier versions by our own inference (family audience). The task does not require it and collection cards are not 16+ scenes, so the ban was lifted on 20.11 (Hrach).
