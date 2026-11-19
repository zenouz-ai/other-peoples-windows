# Batch 2: eight new windows on app credits

> Eight window types the facade does not have yet, made by hand with the credits already paid for. Then the API pipeline takes over.

## Purpose

Use the Google Flow and Kling app credits on scenes that add variety: a shop at work, an empty seasonal room, a dark high-rise, rain, a craft at work, a group of friends and an older neighbour with a pet. Each model gets the scenes it handles best.

## Key Points

- **Deadline:** Google says Veo 3.1 Fast and Quality retire on 5 December 2026. Make windows 07 to 10 first.
- **Veo 3.1 Quality in Flow (07 to 10, 100 credits each, 8 seconds):** atmosphere-led scenes where light, water or fire carry the motion.
- **Kling 4.0 (11 to 14, 8 to 10 seconds):** scenes with hands and people, where Kling beat Veo in the café and dog tests. Check the credit cost shown before generating; use 1080p.
- **Both:** 16:9, the still as the start frame only, one take each. Every clip must give a 6 to 10 second loop.
- **Sound:** faint ambience only. Kling's sound has added music, speech and farmyard noises in tests, so every clip goes through `pipeline/sound_check.py`; a flagged clip keeps its picture and is muted or regenerated.
- **Still images:** Gemini 3.1 Pro with the image prompts below. Check that the people match the casting before animating.
- **Name the files** with the window ID (for example `07-launderette.mp4`) and save them into `media/inbox/`.

## Next Actions

- [ ] Make the 8 stills in Gemini and save them to `media/stills/`
- [ ] Generate the 4 Veo clips in Flow (Quality, 8 s) before 5 December 2026
- [ ] Generate the 4 Kling clips (8 to 10 s)
- [ ] Save the clips to `media/inbox/` and ask Claude Code to check, loop and add them to page 2

## The 8 windows

_Generated from `scenes/scenes.yaml` by `pipeline/prompts.py brief`; edit the YAML, not this file._

### 07-launderette: Launderette

**Kind:** Shop · **Model:** Veo 3.1 Quality, 8 s (Flow)

**Image prompt (Gemini)**

```
Generate a 16:9 image. Seen from the pavement, a launderette after the evening rush: rows of washing machines with drums spinning, a young man in a wheelchair reading a book while he waits, bright strip lights. Photorealistic, shot on 35mm film with a 35mm lens, deep focus and fine grain. London at dusk in late autumn: cool blue light outside, warm light inside, faint reflections of the street on the glass. Candid and quiet. Any people are small in the frame, absorbed in what they are doing, seen side-on or from behind with their faces turned away from the camera. Keep the people exactly as described. Every sign, screen, label and book spine is blank or too small to read, and nothing carries a brand logo.
```

**Video prompt (Veo)**

```
Static locked-off shot from a tripod, one continuous take: the framing stays exactly as in the image, with no zoom, push-in, pan or camera drift. Animate this exact image, keeping the same place, people and lighting. The drums of the washing machines turn steadily. The young man sits still and reads; only his breathing moves. All motion is slow, subtle and continuous for the whole clip, and everyone stays in place with their faces turned away from the camera. Ambient noise: the low rumble of washing machines, very faint and muffled, as if heard from outside through closed glass. No music, no singing, no dialogue.
```

### 08-christmas-tree-empty-room: Christmas tree, empty room

**Kind:** Quiet · **Model:** Veo 3.1 Quality, 8 s (Flow)

**Image prompt (Gemini)**

```
Generate a 16:9 image. Seen from the pavement, a terraced front room window: an empty sitting room with a decorated Christmas tree by the window, warm fairy lights, a fire glowing in the grate. Photorealistic, shot on 35mm film with a 35mm lens, deep focus and fine grain. London at dusk in late autumn: cool blue light outside, warm light inside, faint reflections of the street on the glass. Candid and quiet. Nobody is in the room. Every sign, screen, label and book spine is blank or too small to read, and nothing carries a brand logo.
```

**Video prompt (Veo)**

```
Static locked-off shot from a tripod, one continuous take: the framing stays exactly as in the image, with no zoom, push-in, pan or camera drift. Animate this exact image, keeping the same place, people and lighting. The fairy lights twinkle softly and firelight flickers across the walls. All motion is slow, subtle and continuous for the whole clip, and the room stays empty. Ambient noise: a crackling fire, very faint and muffled, as if heard from outside through closed glass. No music, no singing, no dialogue.
```

### 09-fish-tank-in-the-dark: Fish tank in the dark

**Kind:** Dark · **Model:** Veo 3.1 Quality, 8 s (Flow)

**Image prompt (Gemini)**

```
Generate a 16:9 image. From a tower opposite, at the same height, a 20th-floor flat with floor-to-ceiling glass: a dark empty living room lit only by a large glowing fish tank, city reflections on the glass. Photorealistic, shot on 35mm film with a 35mm lens, deep focus and fine grain. London at dusk in late autumn: cool blue light outside, warm light inside, faint reflections of the street on the glass. Candid and quiet. Nobody is in the room. Every sign, screen, label and book spine is blank or too small to read, and nothing carries a brand logo.
```

**Video prompt (Veo)**

```
Static locked-off shot from a tripod, one continuous take: the framing stays exactly as in the image, with no zoom, push-in, pan or camera drift. Animate this exact image, keeping the same place, people and lighting. Fish glide slowly through the tank and bubbles rise; the city lights reflected in the glass shimmer slightly. All motion is slow, subtle and continuous for the whole clip, and the room stays empty. Ambient noise: aquarium bubbles and a distant city hum, very faint and muffled, as if heard from outside through closed glass. No music, no singing, no dialogue.
```

### 10-corner-shop: Corner shop

**Kind:** Shop · **Model:** Veo 3.1 Quality, 8 s (Flow)

**Image prompt (Gemini)**

```
Generate a 16:9 image. Seen from the pavement, a corner shop window: an older white woman with reading glasses on a chain behind the counter watching a small television, shelves of unbranded goods, a glowing open sign with no readable text, rain streaming down the shop window. Photorealistic, shot on 35mm film with a 35mm lens, deep focus and fine grain. London at dusk in late autumn: cool blue light outside, warm light inside, faint reflections of the street on the glass. Candid and quiet. Any people are small in the frame, absorbed in what they are doing, seen side-on or from behind with their faces turned away from the camera. Keep the people exactly as described. Every sign, screen, label and book spine is blank or too small to read, and nothing carries a brand logo.
```

**Video prompt (Veo)**

```
Static locked-off shot from a tripod, one continuous take: the framing stays exactly as in the image, with no zoom, push-in, pan or camera drift. Animate this exact image, keeping the same place, people and lighting. Rain streams down the shop window, the small television flickers, and the shopkeeper sits still behind the counter. All motion is slow, subtle and continuous for the whole clip, and everyone stays in place with their faces turned away from the camera. Ambient noise: rain on the glass and a fridge humming, very faint and muffled, as if heard from outside through closed glass. No music, no singing, no dialogue.
```

### 11-potter-at-the-wheel: Potter at the wheel

**Kind:** Home · **Model:** Kling 4.0, 8 to 10 s

_Replaces Piano by the window (9 Nov review): a piano scene always produces music._

**Image prompt (Gemini)**

```
Generate a 16:9 image. Seen from the pavement, the ground-floor front room of a terraced house turned into a small pottery studio: a Black man in his forties in a clay-spattered apron, seen side-on at a potter's wheel, shaping a tall clay pot with both hands, shelves of unglazed pots behind him, a single work lamp. Photorealistic, shot on 35mm film with a 35mm lens, deep focus and fine grain. London at dusk in late autumn: cool blue light outside, warm light inside, faint reflections of the street on the glass. Candid and quiet. Any people are small in the frame, absorbed in what they are doing, seen side-on or from behind with their faces turned away from the camera. Keep the people exactly as described. Every sign, screen, label and book spine is blank or too small to read, and nothing carries a brand logo.
```

**Video prompt (Kling)**

```
Static locked-off shot from a tripod, one continuous take: the framing stays exactly as in the image, with no zoom, push-in, pan or camera drift. Animate this exact image, keeping the same place, people and lighting. The wheel turns steadily and his hands rise slowly up the spinning clay in one smooth, continuous movement. All motion is slow, subtle and continuous for the whole clip, and everyone stays in place with their faces turned away from the camera. Ambient noise: the soft whirr of the wheel, very faint and muffled, as if heard from outside through closed glass. No music, no singing, no dialogue.
```

### 12-barber-sweeping-up: Barber sweeping up

**Kind:** Shop · **Model:** Kling 4.0, 8 to 10 s

**Image prompt (Gemini)**

```
Generate a 16:9 image. Seen from the pavement, a barber shop after closing: a Black British barber in his twenties sweeping hair from the floor between empty chairs, mirrors and warm lights, a striped pole outside. Photorealistic, shot on 35mm film with a 35mm lens, deep focus and fine grain. London at dusk in late autumn: cool blue light outside, warm light inside, faint reflections of the street on the glass. Candid and quiet. Any people are small in the frame, absorbed in what they are doing, seen side-on or from behind with their faces turned away from the camera. Keep the people exactly as described. Every sign, screen, label and book spine is blank or too small to read, and nothing carries a brand logo.
```

**Video prompt (Kling)**

```
Static locked-off shot from a tripod, one continuous take: the framing stays exactly as in the image, with no zoom, push-in, pan or camera drift. Animate this exact image, keeping the same place, people and lighting. He sweeps slowly and steadily between the empty chairs; the striped pole outside turns. All motion is slow, subtle and continuous for the whole clip, and everyone stays in place with their faces turned away from the camera. Ambient noise: a broom on the floor and the quiet street, very faint and muffled, as if heard from outside through closed glass. No music, no singing, no dialogue.
```

### 13-pizza-night: Pizza night

**Kind:** Home · **Model:** Kling 4.0, 8 to 10 s

**Image prompt (Gemini)**

```
Generate a 16:9 image. Looking up at a first-floor flat above a shop: four friends in their twenties from different backgrounds (a Black woman with an afro, an East Asian man, a white woman with red hair and a South Asian man) around a coffee table sharing pizza, laughing, a string of fairy lights. Photorealistic, shot on 35mm film with a 35mm lens, deep focus and fine grain. London at dusk in late autumn: cool blue light outside, warm light inside, faint reflections of the street on the glass. Candid and quiet. Any people are small in the frame, absorbed in what they are doing, seen side-on or from behind with their faces turned away from the camera. Keep the people exactly as described. Every sign, screen, label and book spine is blank or too small to read, and nothing carries a brand logo.
```

**Video prompt (Kling)**

```
Static locked-off shot from a tripod, one continuous take: the framing stays exactly as in the image, with no zoom, push-in, pan or camera drift. Animate this exact image, keeping the same place, people and lighting. They laugh and lean towards each other with small, natural movements, everyone staying seated; the fairy lights glow. All motion is slow, subtle and continuous for the whole clip, and everyone stays in place with their faces turned away from the camera. Ambient noise: an indistinct murmur of conversation and soft laughter, very faint and muffled, as if heard from outside through closed glass. No music, no singing, no dialogue.
```

### 14-knitting-with-a-cat: Knitting with a cat

**Kind:** Home · **Model:** Kling 4.0, 8 to 10 s

**Image prompt (Gemini)**

```
Generate a 16:9 image. Looking up at a first-floor flat above a shop: an elderly Chinese grandmother knitting in an armchair by the window, a cat asleep on her lap, a lamp beside her. Photorealistic, shot on 35mm film with a 35mm lens, deep focus and fine grain. London at dusk in late autumn: cool blue light outside, warm light inside, faint reflections of the street on the glass. Candid and quiet. Any people are small in the frame, absorbed in what they are doing, seen side-on or from behind with their faces turned away from the camera. Keep the people exactly as described. Every sign, screen, label and book spine is blank or too small to read, and nothing carries a brand logo.
```

**Video prompt (Kling)**

```
Static locked-off shot from a tripod, one continuous take: the framing stays exactly as in the image, with no zoom, push-in, pan or camera drift. Animate this exact image, keeping the same place, people and lighting. Her knitting needles move slowly and rhythmically, and the cat sleeps on her lap, breathing slowly. All motion is slow, subtle and continuous for the whole clip, and everyone stays in place with their faces turned away from the camera. Ambient noise: the soft click of knitting needles in a quiet room, very faint and muffled, as if heard from outside through closed glass. No music, no singing, no dialogue.
```
