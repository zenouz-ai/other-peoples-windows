# Batch 4: the model shoot-out (page 4)

> Six windows for page 4, each still made by Gemini, GPT Image and Midjourney and each picked still animated twice, by Wan 3.0 and by the current model, so the tools for the last 26 windows are chosen on a written scorecard.

## Purpose

Two empty, atmosphere-led rooms (28, 46: today Omni's ground) and four people scenes with hands and bodies (22, 27, 34, 49: today Kling's ground; 49, an evening church service, came in on 11 Nov), mixing street level and high-rise. Same prompts for every model, same checks, results in docs/batch-04-scorecard.md (written by `generate.py review`). Plan and costs: docs/plan-batches-04-05.md.

## Key Points

- **Stills:** four candidates per window from each of Gemini (`generate.py still NN`), GPT Image (`--engine openai`) and Midjourney (by hand, prompt below; two grids per window).
- **Midjourney:** paste the Midjourney prompt into midjourney.com, download the best four images of two grids into `media/inbox/`, then `generate.py import NN FILES` copies them to `media/stills/NN/m1.jpg` onwards.
- **Score before picking:** casting as described, faces away, no extra people or pedestrians, no readable text or logos, London at dusk and the 35 mm look, edits needed.
- **Video:** each picked still gets a Wan 3.0 take and a take on the current model (Kling 4.0 for 22, 27, 34, 49; Gemini Omni for 28, 46): `generate.py video NN --engine wan,kling` or `wan,omni`.
- **Midjourney video (by hand, third contender):** in midjourney.com, upload the picked still as the starting frame, paste the Midjourney video prompt, HD, low motion, then extend once to 9 s (clips start at 5 s and extend in 4 s steps). It has no sound, so the window gets a sound bed. `generate.py import NN FILE.mp4` copies the download to `media/inbox/` as an `_mj` take and checks it.
- **Checks:** `generate.py check` and `review`: first frame against the still, wobble, drift, sound flags; casting held and hands by eye.
- **Budget:** $40 for the batch on the APIs (`generate.yaml`), plus one month of Midjourney.

## Next Actions

- [ ] Make the Gemini and GPT Image stills (dry run first, then with Kayvan's go-ahead)
- [ ] Make two Midjourney grids per window and import the picks
- [ ] Score the stills in the scorecard and pick one per window
- [ ] Make the Wan 3.0 and current-model takes, score them, loop the better one and place it on page 4

## The 6 windows

_Generated from `scenes/scenes.yaml` by `pipeline/prompts.py brief`; edit the YAML, not this file._

### 22-man-ironing: Man ironing

**Kind:** Home · **Model:** Kling 4.0, 10 s, against Wan 3.0 (people)

_Batch 4 still (11 Nov): Midjourney V8, m4 upscaled (Subtle) to 2912x1632 candidate m5, no edit._

**Image prompt (Gemini, GPT Image)**

```
Generate a 16:9 image. From across the street, a second-floor mansion block window: a Middle Eastern man in his thirties with a short beard, ironing a shirt on an ironing board under a warm ceiling light, a pile of folded laundry beside him. Photorealistic, shot on 35mm film with a 35mm lens, deep focus and fine grain. London at dusk in late autumn: cool blue light outside, warm light inside, faint reflections of the street on the glass. Candid and quiet. Any people are small in the frame, absorbed in what they are doing, seen side-on or from behind with their faces turned away from the camera. Keep the people exactly as described. Every sign, screen, label and book spine is blank or too small to read, and nothing carries a brand logo.
```

**Midjourney prompt**

```
From across the street, a second-floor mansion block window: a Middle Eastern man in his thirties with a short beard, ironing a shirt on an ironing board under a warm ceiling light, a pile of folded laundry beside him. Photorealistic, shot on 35mm film with a 35mm lens, deep focus and fine grain. London at dusk in late autumn: cool blue light outside, warm light inside, faint reflections of the street on the glass. Candid and quiet. Any people are small in the frame, absorbed in what they are doing, seen side-on or from behind with their faces turned away from the camera. Keep the people exactly as described. Every sign, screen, label and book spine is blank or too small to read, and nothing carries a brand logo. --ar 16:9 --style raw
```

**Midjourney video prompt** (the picked still as starting frame)

```
Static locked-off shot from a tripod, one continuous take: the framing stays exactly as in the image, with no zoom, push-in, pan or camera drift. Animate this exact image, keeping the same place, people and lighting. He moves the iron slowly back and forth across the shirt and a soft puff of steam rises. All motion is slow, subtle and continuous for the whole clip, and everyone stays in place with their faces turned away from the camera. --motion low --raw
```

**Video prompt (Kling)**

```
Static locked-off shot from a tripod, one continuous take: the framing stays exactly as in the image, with no zoom, push-in, pan or camera drift. Animate this exact image, keeping the same place, people and lighting. He moves the iron slowly back and forth across the shirt and a soft puff of steam rises. All motion is slow, subtle and continuous for the whole clip, and everyone stays in place with their faces turned away from the camera. Ambient noise: the hiss of the iron's steam, very faint and muffled, as if heard from outside through closed glass. No music, no singing, no dialogue.
```

### 27-evening-stretch: Evening stretch

**Kind:** Home · **Model:** Kling 4.0, 10 s, against Wan 3.0 (people)

_Moved from Veo to Kling for batch 4 (10 Nov): Gemini Omni recast a person on 45, so people scenes go to Kling. Batch 4 still (11 Nov): GPT Image 2.5-flare candidate o4, no edit._

**Image prompt (Gemini, GPT Image)**

```
Generate a 16:9 image. From a tower opposite, a high-rise flat with floor-to-ceiling glass: a South Asian man in his fifties on a yoga mat in an open living room holding a gentle stretch, plants and a lamp nearby. Photorealistic, shot on 35mm film with a 35mm lens, deep focus and fine grain. London at dusk in late autumn: cool blue light outside, warm light inside, faint reflections of the street on the glass. Candid and quiet. Any people are small in the frame, absorbed in what they are doing, seen side-on or from behind with their faces turned away from the camera. Keep the people exactly as described. Every sign, screen, label and book spine is blank or too small to read, and nothing carries a brand logo.
```

**Midjourney prompt**

```
From a tower opposite, a high-rise flat with floor-to-ceiling glass: a South Asian man in his fifties on a yoga mat in an open living room holding a gentle stretch, plants and a lamp nearby. Photorealistic, shot on 35mm film with a 35mm lens, deep focus and fine grain. London at dusk in late autumn: cool blue light outside, warm light inside, faint reflections of the street on the glass. Candid and quiet. Any people are small in the frame, absorbed in what they are doing, seen side-on or from behind with their faces turned away from the camera. Keep the people exactly as described. Every sign, screen, label and book spine is blank or too small to read, and nothing carries a brand logo. --ar 16:9 --style raw
```

**Midjourney video prompt** (the picked still as starting frame)

```
Static locked-off shot from a tripod, one continuous take: the framing stays exactly as in the image, with no zoom, push-in, pan or camera drift. Animate this exact image, keeping the same place, people and lighting. He breathes slowly and shifts gently within the stretch. All motion is slow, subtle and continuous for the whole clip, and everyone stays in place with their faces turned away from the camera. --motion low --raw
```

**Video prompt (Kling)**

```
Static locked-off shot from a tripod, one continuous take: the framing stays exactly as in the image, with no zoom, push-in, pan or camera drift. Animate this exact image, keeping the same place, people and lighting. He breathes slowly and shifts gently within the stretch. All motion is slow, subtle and continuous for the whole clip, and everyone stays in place with their faces turned away from the camera. Ambient noise: slow breathing in a quiet room, very faint and muffled, as if heard from outside through closed glass. No music, no singing, no dialogue.
```

### 28-nursery-night-light: Nursery night light

**Kind:** Dark · **Model:** Gemini Omni 1.2 Flash, 10 s, against Wan 3.0 (empty rooms)

_Batch 4 still (11 Nov): GPT Image 2.5-flare candidate o2, no edit._

**Image prompt (Gemini, GPT Image)**

```
Generate a 16:9 image. From a tower opposite, a high-rise flat bedroom window: a dimly lit nursery, a star projector casting drifting stars on the ceiling, a cot mobile above an empty cot. Photorealistic, shot on 35mm film with a 35mm lens, deep focus and fine grain. London at dusk in late autumn: cool blue light outside, warm light inside, faint reflections of the street on the glass. Candid and quiet. Nobody is in the room. Every sign, screen, label and book spine is blank or too small to read, and nothing carries a brand logo.
```

**Midjourney prompt**

```
From a tower opposite, a high-rise flat bedroom window: a dimly lit nursery, a star projector casting drifting stars on the ceiling, a cot mobile above an empty cot. Photorealistic, shot on 35mm film with a 35mm lens, deep focus and fine grain. London at dusk in late autumn: cool blue light outside, warm light inside, faint reflections of the street on the glass. Candid and quiet. Nobody is in the room. Every sign, screen, label and book spine is blank or too small to read, and nothing carries a brand logo. --ar 16:9 --style raw
```

**Midjourney video prompt** (the picked still as starting frame)

```
Static locked-off shot from a tripod, one continuous take: the framing stays exactly as in the image, with no zoom, push-in, pan or camera drift. Animate this exact image, keeping the same place, people and lighting. The stars drift slowly across the ceiling and the mobile turns gently. All motion is slow, subtle and continuous for the whole clip, and the room stays empty. --motion low --raw
```

**Video prompt (Veo)**

```
Static locked-off shot from a tripod, one continuous take: the framing stays exactly as in the image, with no zoom, push-in, pan or camera drift. Animate this exact image, keeping the same place, people and lighting. The stars drift slowly across the ceiling and the mobile turns gently. All motion is slow, subtle and continuous for the whole clip, and the room stays empty. Ambient noise: the soft hush of a white-noise machine, very faint and muffled, as if heard from outside through closed glass. No music, no singing, no dialogue.
```

### 34-florist-closing: Florist closing

**Kind:** Shop · **Model:** Kling 4.0, 10 s, against Wan 3.0 (people)

_Batch 4 still (11 Nov): GPT Image 2.5-flare candidate o2, no edit._

**Image prompt (Gemini, GPT Image)**

```
Generate a 16:9 image. Seen from the pavement, a flower shop after closing: an East Asian florist in her thirties with a short bob, at the counter arranging tulips in a bucket, buckets of flowers all around. Photorealistic, shot on 35mm film with a 35mm lens, deep focus and fine grain. London at dusk in late autumn: cool blue light outside, warm light inside, faint reflections of the street on the glass. Candid and quiet. Any people are small in the frame, absorbed in what they are doing, seen side-on or from behind with their faces turned away from the camera. Keep the people exactly as described. Every sign, screen, label and book spine is blank or too small to read, and nothing carries a brand logo.
```

**Midjourney prompt**

```
Seen from the pavement, a flower shop after closing: an East Asian florist in her thirties with a short bob, at the counter arranging tulips in a bucket, buckets of flowers all around. Photorealistic, shot on 35mm film with a 35mm lens, deep focus and fine grain. London at dusk in late autumn: cool blue light outside, warm light inside, faint reflections of the street on the glass. Candid and quiet. Any people are small in the frame, absorbed in what they are doing, seen side-on or from behind with their faces turned away from the camera. Keep the people exactly as described. Every sign, screen, label and book spine is blank or too small to read, and nothing carries a brand logo. --ar 16:9 --style raw
```

**Midjourney video prompt** (the picked still as starting frame)

```
Static locked-off shot from a tripod, one continuous take: the framing stays exactly as in the image, with no zoom, push-in, pan or camera drift. Animate this exact image, keeping the same place, people and lighting. She slowly arranges the tulips. All motion is slow, subtle and continuous for the whole clip, and everyone stays in place with their faces turned away from the camera. --motion low --raw
```

**Video prompt (Kling)**

```
Static locked-off shot from a tripod, one continuous take: the framing stays exactly as in the image, with no zoom, push-in, pan or camera drift. Animate this exact image, keeping the same place, people and lighting. She slowly arranges the tulips. All motion is slow, subtle and continuous for the whole clip, and everyone stays in place with their faces turned away from the camera. Ambient noise: rustling paper in a quiet shop, very faint and muffled, as if heard from outside through closed glass. No music, no singing, no dialogue.
```

### 46-boutique-at-night: Boutique after closing

**Kind:** Quiet · **Model:** Gemini Omni 1.2 Flash, 10 s, against Wan 3.0 (empty rooms)

_Moved into batch 4 (11 Nov) in place of 49. Batch 4 still (11 Nov): GPT Image 2.5-flare candidate o2, no edit._

**Image prompt (Gemini, GPT Image)**

```
Generate a 16:9 image. Seen from the pavement, a closed clothes boutique: mannequins in the window under a single spotlight, the shop dark behind, a neon sign with no readable text. Photorealistic, shot on 35mm film with a 35mm lens, deep focus and fine grain. London at dusk in late autumn: cool blue light outside, warm light inside, faint reflections of the street on the glass. Candid and quiet. Nobody is in the room. Every sign, screen, label and book spine is blank or too small to read, and nothing carries a brand logo.
```

**Midjourney prompt**

```
Seen from the pavement, a closed clothes boutique: mannequins in the window under a single spotlight, the shop dark behind, a neon sign with no readable text. Photorealistic, shot on 35mm film with a 35mm lens, deep focus and fine grain. London at dusk in late autumn: cool blue light outside, warm light inside, faint reflections of the street on the glass. Candid and quiet. Nobody is in the room. Every sign, screen, label and book spine is blank or too small to read, and nothing carries a brand logo. --ar 16:9 --style raw
```

**Midjourney video prompt** (the picked still as starting frame)

```
Static locked-off shot from a tripod, one continuous take: the framing stays exactly as in the image, with no zoom, push-in, pan or camera drift. Animate this exact image, keeping the same place, people and lighting. The neon sign hums and flickers faintly. All motion is slow, subtle and continuous for the whole clip, and the room stays empty. --motion low --raw
```

**Video prompt (Veo)**

```
Static locked-off shot from a tripod, one continuous take: the framing stays exactly as in the image, with no zoom, push-in, pan or camera drift. Animate this exact image, keeping the same place, people and lighting. The neon sign hums and flickers faintly. All motion is slow, subtle and continuous for the whole clip, and the room stays empty. Ambient noise: the faint buzz of a neon sign, very faint and muffled, as if heard from outside through closed glass. No music, no singing, no dialogue.
```

### 49-evening-service: Evening service

**Kind:** Quiet · **Model:** Kling 4.0, 10 s, against Wan 3.0 (people)

_Rewritten 11 Nov at Kayvan's request (was Candles in an empty church, which every model drew with an impossible street-level plate-glass window): a service seen from the door of a cosy traditional church, many people. Seen through the glazed porch doors so it is still a window. The moment is silent prayer because the house rules allow no singing, organ or words in the sound. People seen from behind, so faces are turned away naturally. Kling, since it is a people scene. Replaces 18 in batch 4._

**Image prompt (Gemini, GPT Image)**

```
Generate a 16:9 image. Seen from the church porch at dusk, through the glazed inner doors of a small, cosy Victorian parish church: an evening service under way, warm lamplight on stone arches and dark wooden pews, the pews full of a congregation of all ages and backgrounds seen from behind, a woman priest in a white surplice at the altar far ahead with her back to the door, tall candles burning on the altar. Photorealistic, shot on 35mm film with a 35mm lens, deep focus and fine grain. London at dusk in late autumn: cool blue light outside, warm light inside, faint reflections of the street on the glass. Candid and quiet. Any people are small in the frame, absorbed in what they are doing, seen side-on or from behind with their faces turned away from the camera. Keep the people exactly as described. Every sign, screen, label and book spine is blank or too small to read, and nothing carries a brand logo.
```

**Midjourney prompt**

```
Seen from the church porch at dusk, through the glazed inner doors of a small, cosy Victorian parish church: an evening service under way, warm lamplight on stone arches and dark wooden pews, the pews full of a congregation of all ages and backgrounds seen from behind, a woman priest in a white surplice at the altar far ahead with her back to the door, tall candles burning on the altar. Photorealistic, shot on 35mm film with a 35mm lens, deep focus and fine grain. London at dusk in late autumn: cool blue light outside, warm light inside, faint reflections of the street on the glass. Candid and quiet. Any people are small in the frame, absorbed in what they are doing, seen side-on or from behind with their faces turned away from the camera. Keep the people exactly as described. Every sign, screen, label and book spine is blank or too small to read, and nothing carries a brand logo. --ar 16:9 --style raw
```

**Midjourney video prompt** (the picked still as starting frame)

```
Static locked-off shot from a tripod, one continuous take: the framing stays exactly as in the image, with no zoom, push-in, pan or camera drift. Animate this exact image, keeping the same place, people and lighting. The congregation sit still with heads bowed in silent prayer, breathing softly, and the altar candles flicker. All motion is slow, subtle and continuous for the whole clip, and everyone stays in place with their faces turned away from the camera. --motion low --raw
```

**Video prompt (Kling)**

```
Static locked-off shot from a tripod, one continuous take: the framing stays exactly as in the image, with no zoom, push-in, pan or camera drift. Animate this exact image, keeping the same place, people and lighting. The congregation sit still with heads bowed in silent prayer, breathing softly, and the altar candles flicker. All motion is slow, subtle and continuous for the whole clip, and everyone stays in place with their faces turned away from the camera. Ambient noise: a hushed church, the creak of a pew and a soft cough, very faint and muffled, as if heard from outside through closed glass. No music, no singing, no dialogue.
```
