# Batch 5 scorecard

> Written by `pipeline/generate.py review` on 13 Nov 2026. Measured columns are filled in; the columns from "Casting" on are for Kayvan's judgement and are kept when the scorecard is rewritten.

How to read the measurements: **first frame** compares the take's first frame with its still (zoom, shift in px at 1080p, and *redraw*: about 1.5 when the still is kept, higher when the model has repainted it; a recast person must be judged by eye on the comparison sheet in `media/checks/`). **Wobble** is the frame-to-frame shake left after removing slow drift, rms and max in px at 1080p (under about 0.1 is still; above it, loop with `--lock`). **Sound** is loudness in LUFS (loudness units relative to full scale) with music and speech flags from `sound_check.py`.

## 15-basement-kitchen: Basement kitchen

Home, people; video model in scenes.yaml: Kling. Picked still: `media/stills/15-basement-kitchen.jpg`.

### Stills

| Still | Model | Size | Cost | Casting as described | Faces away | No extra people | No text or logos | London dusk, 35 mm | Edits needed | Pick |
|---|---|---|---|---|---|---|---|---|---|---|
| `media/stills/15/m1.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/15/m2.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/15/m3.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/15/m4.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/15/m5.jpg` | Midjourney | 2912x1632 |  |  |  |  |  |  |  |  |
| `media/stills/15/m6.jpg` | Midjourney | 2912x1632 |  |  |  |  |  |  |  |  |
| `media/stills/15/o1.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |
| `media/stills/15/o2.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |
| `media/stills/15/o3.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |
| `media/stills/15/o4.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |

### Takes

| Take | Model | Length | Cost | Time | First frame vs still | Wobble rms / max px | Drift zoom | Sound | Casting held | Hands, objects, steam | Loops well | Keep |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `media/raw/15-basement-kitchen_kling.mp4` | Kling | 10.0 s |  |  | -0.1%, 0 px, redraw 1.6 | 0.02 / 0.13 | +0.00% | -33 LUFS, MUSIC 0.54 (Music) |  |  |  |  |

## 16-pool-after-hours: Pool after hours

Quiet, empty room; video model in scenes.yaml: Wan. Picked still: `media/stills/16-pool-after-hours.jpg`.

### Stills

| Still | Model | Size | Cost | Casting as described | Faces away | No extra people | No text or logos | London dusk, 35 mm | Edits needed | Pick |
|---|---|---|---|---|---|---|---|---|---|---|
| `media/stills/16/m1.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/16/m2.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/16/m3.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/16/m4.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/16/o1.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |
| `media/stills/16/o2.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |
| `media/stills/16/o3.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |
| `media/stills/16/o4.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |

### Takes

| Take | Model | Length | Cost | Time | First frame vs still | Wobble rms / max px | Drift zoom | Sound | Casting held | Hands, objects, steam | Loops well | Keep |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `media/raw/16-pool-after-hours_wan.mp4` | ? | 10.0 s |  |  | -0.0%, 0 px, redraw 3.0 | 0.66 / 1.94 | +0.06% | -43 LUFS, no flags |  |  |  |  |

## 19-teenager-gaming: Teenager gaming

Home, people; video model in scenes.yaml: Kling. Picked still: `media/stills/19-teenager-gaming.jpg`.

### Stills

| Still | Model | Size | Cost | Casting as described | Faces away | No extra people | No text or logos | London dusk, 35 mm | Edits needed | Pick |
|---|---|---|---|---|---|---|---|---|---|---|
| `media/stills/19/m1.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/19/m2.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/19/m3.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/19/m4.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/19/m5.jpg` | Midjourney | 2912x1632 |  |  |  |  |  |  |  |  |
| `media/stills/19/o1.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |
| `media/stills/19/o2.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |
| `media/stills/19/o3.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |
| `media/stills/19/o4.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |

### Takes

| Take | Model | Length | Cost | Time | First frame vs still | Wobble rms / max px | Drift zoom | Sound | Casting held | Hands, objects, steam | Loops well | Keep |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `media/raw/19-teenager-gaming_kling.mp4` | Kling | 10.0 s |  |  | +0.0%, 0 px, redraw 2.0 | 0.07 / 0.71 | -0.02% | -38 LUFS, no flags |  |  |  |  |

## 20-board-game-in-the-conservatory: Board game in the conservatory

Home, people; video model in scenes.yaml: Kling. Picked still: `media/stills/20-board-game-in-the-conservatory.jpg`.

### Stills

| Still | Model | Size | Cost | Casting as described | Faces away | No extra people | No text or logos | London dusk, 35 mm | Edits needed | Pick |
|---|---|---|---|---|---|---|---|---|---|---|
| `media/stills/20/m1.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/20/m2.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/20/m3.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/20/m4.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/20/o1.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |
| `media/stills/20/o2.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |
| `media/stills/20/o3.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |
| `media/stills/20/o4.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |

### Takes

| Take | Model | Length | Cost | Time | First frame vs still | Wobble rms / max px | Drift zoom | Sound | Casting held | Hands, objects, steam | Loops well | Keep |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `media/raw/20-board-game-in-the-conservatory_kling.mp4` | Kling | 10.0 s |  |  | -0.0%, 0 px, redraw 2.2 | 0.03 / 0.41 | -0.01% | -30 LUFS, SPEECH 0.65 |  |  |  |  |

## 32-bedtime-story: Bedtime story

Home, people; video model in scenes.yaml: Kling. Picked still: `media/stills/32-bedtime-story.jpg`.

### Stills

| Still | Model | Size | Cost | Casting as described | Faces away | No extra people | No text or logos | London dusk, 35 mm | Edits needed | Pick |
|---|---|---|---|---|---|---|---|---|---|---|
| `media/stills/32/m1.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/32/m2.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/32/m3.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/32/m4.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/32/o1.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |
| `media/stills/32/o2.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |
| `media/stills/32/o3.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |
| `media/stills/32/o4.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |

### Takes

| Take | Model | Length | Cost | Time | First frame vs still | Wobble rms / max px | Drift zoom | Sound | Casting held | Hands, objects, steam | Loops well | Keep |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `media/raw/32-bedtime-story_kling.mp4` | Kling | 10.0 s |  |  | -0.0%, 0 px, redraw 1.7 | 0.02 / 0.24 | -0.00% | -25 LUFS, MUSIC 0.38 (Music) |  |  |  |  |

## 36-chip-shop: Chip shop

Shop, people; video model in scenes.yaml: Kling. Picked still: `media/stills/36-chip-shop.jpg`.

### Stills

| Still | Model | Size | Cost | Casting as described | Faces away | No extra people | No text or logos | London dusk, 35 mm | Edits needed | Pick |
|---|---|---|---|---|---|---|---|---|---|---|
| `media/stills/36/m1.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/36/m2.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/36/m3.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/36/m4.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/36/o1.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |
| `media/stills/36/o2.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |
| `media/stills/36/o3.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |
| `media/stills/36/o4.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |

### Takes

| Take | Model | Length | Cost | Time | First frame vs still | Wobble rms / max px | Drift zoom | Sound | Casting held | Hands, objects, steam | Loops well | Keep |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `media/raw/36-chip-shop_kling.mp4` | Kling | 10.0 s |  |  | -0.0%, 0 px, redraw 1.6 | 0.03 / 0.26 | +0.00% | -26 LUFS, MUSIC 0.30 (Music); SPEECH 0.54 |  |  |  |  |
