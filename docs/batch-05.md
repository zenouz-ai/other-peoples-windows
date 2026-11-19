# Batch 5: the final six (page 5)

> The last six windows, made with the tools that won batch 4, to finish the facade at 30 windows on five pages.

## Purpose

Fill the gaps in the facade: a teenager (19), a whole family round a board game (20), a father and small child (32), the most London of shopfronts (36), a view down into a basement (15) and one empty, aqua room (16). Mostly street level and upstairs terraces, since page 4 already has two high-rise windows. Plan and costs: docs/plan-batches-04-05.md.

## Key Points

- **Stills:** four GPT Image 2.5-flare candidates at 2560x1440 (`generate.py still NN --engine openai`) and two Midjourney grids per window (`prompts.py show NN --midjourney`, then `generate.py import`). Upscale a Midjourney pick (Subtle) before using it. Gemini only for edits or a hard window.
- **Score before picking:** casting as described, faces away, no extra people or pedestrians, no readable text or logos, London at dusk and the 35 mm look, sharp at full size.
- **Video:** Kling 4.0, 10 s at 1080p, for the five people scenes (15, 19, 20, 32, 36); Wan 3.0 for the pool (16), with Gemini Omni as the fallback. Check every Wan take frame by frame.
- **Sound:** expect to replace Kling's sound with a bed from a rejected take or another raw clip; nothing with music or words.
- **Budget:** $25 on the APIs (`generate.yaml`). Kling has 151 units (10 takes of 10 s), enough for batch 5 and the page 1 retakes.

## Next Actions

- [ ] Check the OpenAI and Alibaba Cloud balances (Kling topped up 13 Nov)
- [ ] Make the GPT Image stills and the Midjourney grids; score and pick
- [ ] Make the six takes; loop the keepers with sound beds; place them on page 5
- [ ] Render the five-page film in 4K and update YouTube and zenouz.ai

## The 6 windows

_Generated from `scenes/scenes.yaml` by `pipeline/prompts.py brief`; edit the YAML, not this file._

### 15-basement-kitchen: Basement kitchen

**Kind:** Home · **Model:** Kling 4.0, 10 s at 1080p (Kling API)

_Chosen 13 Nov for batch 5, the final six._

**Image prompt (Gemini, GPT Image)**

```
Generate a 16:9 image. Seen from the pavement, looking down through black iron railings into a basement flat window: a small warm kitchen where a Black British woman in her fifties with grey locs, wearing a cardigan, stands at the sink under the window rinsing a mug, a kettle steaming on the side. Photorealistic, shot on 35mm film with a 35mm lens, deep focus and fine grain. London at dusk in late autumn: cool blue light outside, warm light inside, faint reflections of the street on the glass. Candid and quiet. Any people are small in the frame, absorbed in what they are doing, seen side-on or from behind with their faces turned away from the camera. Keep the people exactly as described. Every sign, screen, label and book spine is blank or too small to read, and nothing carries a brand logo.
```

**Midjourney prompt**

```
Seen from the pavement, looking down through black iron railings into a basement flat window: a small warm kitchen where a Black British woman in her fifties with grey locs, wearing a cardigan, stands at the sink under the window rinsing a mug, a kettle steaming on the side. Photorealistic, shot on 35mm film with a 35mm lens, deep focus and fine grain. London at dusk in late autumn: cool blue light outside, warm light inside, faint reflections of the street on the glass. Candid and quiet. Any people are small in the frame, absorbed in what they are doing, seen side-on or from behind with their faces turned away from the camera. Keep the people exactly as described. Every sign, screen, label and book spine is blank or too small to read, and nothing carries a brand logo. --ar 16:9 --style raw
```

**Midjourney video prompt** (the picked still as starting frame)

```
Static locked-off shot from a tripod, one continuous take: the framing stays exactly as in the image, with no zoom, push-in, pan or camera drift. Animate this exact image, keeping the same place, people and lighting. The woman slowly rinses the mug under running water. Steam drifts from the kettle. All motion is slow, subtle and continuous for the whole clip, and everyone stays in place with their faces turned away from the camera. --motion low --raw
```

**Video prompt (Kling)**

```
Static locked-off shot from a tripod, one continuous take: the framing stays exactly as in the image, with no zoom, push-in, pan or camera drift. Animate this exact image, keeping the same place, people and lighting. The woman slowly rinses the mug under running water. Steam drifts from the kettle. All motion is slow, subtle and continuous for the whole clip, and everyone stays in place with their faces turned away from the camera. Ambient noise: a running tap and a kettle coming to the boil, very faint and muffled, as if heard from outside through closed glass. No music, no singing, no dialogue.
```

### 16-pool-after-hours: Pool after hours

**Kind:** Quiet · **Model:** Wan 3.0, 10 s at 1080p (Alibaba Cloud Model Studio), Gemini Omni as the fallback

_New 13 Nov in place of TV glow, nobody visible (taken out of batch 4 on 11 Nov as uninteresting): the only aqua window on the facade, London civic life, empty without being dull; rippling water light loops naturally. Wan 3.0 for its first take (it made the best empty room in batch 4), Gemini Omni as the fallback._

**Image prompt (Gemini, GPT Image)**

```
Generate a 16:9 image. Seen from the pavement through the tall glass wall of a London leisure centre after closing: an empty indoor swimming pool, still turquoise water under dimmed lights, lane ropes floating on the surface, a lifeguard chair at the side, rippling light from the water playing across the ceiling and the tiled walls. Photorealistic, shot on 35mm film with a 35mm lens, deep focus and fine grain. London at dusk in late autumn: cool blue light outside, warm light inside, faint reflections of the street on the glass. Candid and quiet. Nobody is in the room. Every sign, screen, label and book spine is blank or too small to read, and nothing carries a brand logo.
```

**Midjourney prompt**

```
Seen from the pavement through the tall glass wall of a London leisure centre after closing: an empty indoor swimming pool, still turquoise water under dimmed lights, lane ropes floating on the surface, a lifeguard chair at the side, rippling light from the water playing across the ceiling and the tiled walls. Photorealistic, shot on 35mm film with a 35mm lens, deep focus and fine grain. London at dusk in late autumn: cool blue light outside, warm light inside, faint reflections of the street on the glass. Candid and quiet. Nobody is in the room. Every sign, screen, label and book spine is blank or too small to read, and nothing carries a brand logo. --ar 16:9 --style raw
```

**Midjourney video prompt** (the picked still as starting frame)

```
Static locked-off shot from a tripod, one continuous take: the framing stays exactly as in the image, with no zoom, push-in, pan or camera drift. Animate this exact image, keeping the same place, people and lighting. Soft ripples move across the water and their reflected light drifts slowly over the ceiling and walls. All motion is slow, subtle and continuous for the whole clip, and the room stays empty. --motion low --raw
```

**Video prompt (Wan)**

```
Static locked-off shot from a tripod, one continuous take: the framing stays exactly as in the image, with no zoom, push-in, pan or camera drift. Animate this exact image, keeping the same place, people and lighting. Soft ripples move across the water and their reflected light drifts slowly over the ceiling and walls. All motion is slow, subtle and continuous for the whole clip, and the room stays empty. Ambient noise: gently lapping water and the low hum of the ventilation, very faint and muffled, as if heard from outside through closed glass. No music, no singing, no dialogue.
```

### 19-teenager-gaming: Teenager gaming

**Kind:** Home · **Model:** Kling 4.0, 10 s at 1080p (Kling API)

_Chosen 13 Nov for batch 5, the final six._

**Image prompt (Gemini, GPT Image)**

```
Generate a 16:9 image. Looking up from the street at an upstairs bedroom window: a teenage girl with long box braids and headphones, seen from behind at a desk playing a computer game, her face and the room lit by the glow of a monitor and a colourful keyboard. Photorealistic, shot on 35mm film with a 35mm lens, deep focus and fine grain. London at dusk in late autumn: cool blue light outside, warm light inside, faint reflections of the street on the glass. Candid and quiet. Any people are small in the frame, absorbed in what they are doing, seen side-on or from behind with their faces turned away from the camera. Keep the people exactly as described. Every sign, screen, label and book spine is blank or too small to read, and nothing carries a brand logo.
```

**Midjourney prompt**

```
Looking up from the street at an upstairs bedroom window: a teenage girl with long box braids and headphones, seen from behind at a desk playing a computer game, her face and the room lit by the glow of a monitor and a colourful keyboard. Photorealistic, shot on 35mm film with a 35mm lens, deep focus and fine grain. London at dusk in late autumn: cool blue light outside, warm light inside, faint reflections of the street on the glass. Candid and quiet. Any people are small in the frame, absorbed in what they are doing, seen side-on or from behind with their faces turned away from the camera. Keep the people exactly as described. Every sign, screen, label and book spine is blank or too small to read, and nothing carries a brand logo. --ar 16:9 --style raw
```

**Midjourney video prompt** (the picked still as starting frame)

```
Static locked-off shot from a tripod, one continuous take: the framing stays exactly as in the image, with no zoom, push-in, pan or camera drift. Animate this exact image, keeping the same place, people and lighting. Coloured screen light shifts across the room and her hands make small movements on the keyboard and mouse. All motion is slow, subtle and continuous for the whole clip, and everyone stays in place with their faces turned away from the camera. --motion low --raw
```

**Video prompt (Kling)**

```
Static locked-off shot from a tripod, one continuous take: the framing stays exactly as in the image, with no zoom, push-in, pan or camera drift. Animate this exact image, keeping the same place, people and lighting. Coloured screen light shifts across the room and her hands make small movements on the keyboard and mouse. All motion is slow, subtle and continuous for the whole clip, and everyone stays in place with their faces turned away from the camera. Ambient noise: faint keyboard and mouse clicks, very faint and muffled, as if heard from outside through closed glass. No music, no singing, no dialogue.
```

### 20-board-game-in-the-conservatory: Board game in the conservatory

**Kind:** Home · **Model:** Kling 4.0, 10 s at 1080p (Kling API)

_Chosen 13 Nov for batch 5 in place of Bike repair shop, at Kayvan's request; rewritten as a family of four (parents, a girl and her younger brother). The only whole family on the facade. Laughter taken out of the ambience (it invites voices)._

**Image prompt (Gemini, GPT Image)**

```
Generate a 16:9 image. Seen from a neighbour's upstairs window, looking down into a back garden conservatory: a family of four (a South Asian mum and a white dad in their forties, their daughter of about ten and her younger brother of about six) around a table playing a board game under fairy lights, plants all around, the children kneeling on their chairs. Photorealistic, shot on 35mm film with a 35mm lens, deep focus and fine grain. London at dusk in late autumn: cool blue light outside, warm light inside, faint reflections of the street on the glass. Candid and quiet. Any people are small in the frame, absorbed in what they are doing, seen side-on or from behind with their faces turned away from the camera. Keep the people exactly as described. Every sign, screen, label and book spine is blank or too small to read, and nothing carries a brand logo.
```

**Midjourney prompt**

```
Seen from a neighbour's upstairs window, looking down into a back garden conservatory: a family of four (a South Asian mum and a white dad in their forties, their daughter of about ten and her younger brother of about six) around a table playing a board game under fairy lights, plants all around, the children kneeling on their chairs. Photorealistic, shot on 35mm film with a 35mm lens, deep focus and fine grain. London at dusk in late autumn: cool blue light outside, warm light inside, faint reflections of the street on the glass. Candid and quiet. Any people are small in the frame, absorbed in what they are doing, seen side-on or from behind with their faces turned away from the camera. Keep the people exactly as described. Every sign, screen, label and book spine is blank or too small to read, and nothing carries a brand logo. --ar 16:9 --style raw
```

**Midjourney video prompt** (the picked still as starting frame)

```
Static locked-off shot from a tripod, one continuous take: the framing stays exactly as in the image, with no zoom, push-in, pan or camera drift. Animate this exact image, keeping the same place, people and lighting. They lean over the board, considering the next move with small, natural movements; the boy rests his chin on his hands; the fairy lights glow. All motion is slow, subtle and continuous for the whole clip, and everyone stays in place with their faces turned away from the camera. --motion low --raw
```

**Video prompt (Kling)**

```
Static locked-off shot from a tripod, one continuous take: the framing stays exactly as in the image, with no zoom, push-in, pan or camera drift. Animate this exact image, keeping the same place, people and lighting. They lean over the board, considering the next move with small, natural movements; the boy rests his chin on his hands; the fairy lights glow. All motion is slow, subtle and continuous for the whole clip, and everyone stays in place with their faces turned away from the camera. Ambient noise: game pieces tapping softly on the board and a quiet garden at dusk, very faint and muffled, as if heard from outside through closed glass. No music, no singing, no dialogue.
```

### 32-bedtime-story: Bedtime story

**Kind:** Home · **Model:** Kling 4.0, 10 s at 1080p (Kling API)

_Chosen 13 Nov for batch 5, the final six._

**Image prompt (Gemini, GPT Image)**

```
Generate a 16:9 image. From an upstairs neighbour, looking down into a glass kitchen extension at the back of a terrace: a Black dad in his thirties reading a bedtime story to his small son on a sofa, a blanket, a reading lamp. Photorealistic, shot on 35mm film with a 35mm lens, deep focus and fine grain. London at dusk in late autumn: cool blue light outside, warm light inside, faint reflections of the street on the glass. Candid and quiet. Any people are small in the frame, absorbed in what they are doing, seen side-on or from behind with their faces turned away from the camera. Keep the people exactly as described. Every sign, screen, label and book spine is blank or too small to read, and nothing carries a brand logo.
```

**Midjourney prompt**

```
From an upstairs neighbour, looking down into a glass kitchen extension at the back of a terrace: a Black dad in his thirties reading a bedtime story to his small son on a sofa, a blanket, a reading lamp. Photorealistic, shot on 35mm film with a 35mm lens, deep focus and fine grain. London at dusk in late autumn: cool blue light outside, warm light inside, faint reflections of the street on the glass. Candid and quiet. Any people are small in the frame, absorbed in what they are doing, seen side-on or from behind with their faces turned away from the camera. Keep the people exactly as described. Every sign, screen, label and book spine is blank or too small to read, and nothing carries a brand logo. --ar 16:9 --style raw
```

**Midjourney video prompt** (the picked still as starting frame)

```
Static locked-off shot from a tripod, one continuous take: the framing stays exactly as in the image, with no zoom, push-in, pan or camera drift. Animate this exact image, keeping the same place, people and lighting. The dad reads quietly and turns a page slowly; the boy leans against him and listens. All motion is slow, subtle and continuous for the whole clip, and everyone stays in place with their faces turned away from the camera. --motion low --raw
```

**Video prompt (Kling)**

```
Static locked-off shot from a tripod, one continuous take: the framing stays exactly as in the image, with no zoom, push-in, pan or camera drift. Animate this exact image, keeping the same place, people and lighting. The dad reads quietly and turns a page slowly; the boy leans against him and listens. All motion is slow, subtle and continuous for the whole clip, and everyone stays in place with their faces turned away from the camera. Ambient noise: rain falling softly on the glass roof, very faint and muffled, as if heard from outside through closed glass. No music, no singing, no dialogue.
```

### 36-chip-shop: Chip shop

**Kind:** Shop · **Model:** Kling 4.0, 10 s at 1080p (Kling API)

_Chosen 13 Nov for batch 5, the final six. Moved from Veo to Kling for batch 5 (13 Nov): people scenes go to Kling._

**Image prompt (Gemini, GPT Image)**

```
Generate a 16:9 image. Seen from the pavement, a fish and chip shop: a server in her twenties with dyed red hair and a nose ring behind the counter, steam rising from the fryers, a builder in a hi-vis jacket waiting. Photorealistic, shot on 35mm film with a 35mm lens, deep focus and fine grain. London at dusk in late autumn: cool blue light outside, warm light inside, faint reflections of the street on the glass. Candid and quiet. Any people are small in the frame, absorbed in what they are doing, seen side-on or from behind with their faces turned away from the camera. Keep the people exactly as described. Every sign, screen, label and book spine is blank or too small to read, and nothing carries a brand logo.
```

**Midjourney prompt**

```
Seen from the pavement, a fish and chip shop: a server in her twenties with dyed red hair and a nose ring behind the counter, steam rising from the fryers, a builder in a hi-vis jacket waiting. Photorealistic, shot on 35mm film with a 35mm lens, deep focus and fine grain. London at dusk in late autumn: cool blue light outside, warm light inside, faint reflections of the street on the glass. Candid and quiet. Any people are small in the frame, absorbed in what they are doing, seen side-on or from behind with their faces turned away from the camera. Keep the people exactly as described. Every sign, screen, label and book spine is blank or too small to read, and nothing carries a brand logo. --ar 16:9 --style raw
```

**Midjourney video prompt** (the picked still as starting frame)

```
Static locked-off shot from a tripod, one continuous take: the framing stays exactly as in the image, with no zoom, push-in, pan or camera drift. Animate this exact image, keeping the same place, people and lighting. Steam rises steadily from the fryers and the server makes small movements behind the counter. All motion is slow, subtle and continuous for the whole clip, and everyone stays in place with their faces turned away from the camera. --motion low --raw
```

**Video prompt (Kling)**

```
Static locked-off shot from a tripod, one continuous take: the framing stays exactly as in the image, with no zoom, push-in, pan or camera drift. Animate this exact image, keeping the same place, people and lighting. Steam rises steadily from the fryers and the server makes small movements behind the counter. All motion is slow, subtle and continuous for the whole clip, and everyone stays in place with their faces turned away from the camera. Ambient noise: fryers sizzling and an extractor fan humming, very faint and muffled, as if heard from outside through closed glass. No music, no singing, no dialogue.
```
