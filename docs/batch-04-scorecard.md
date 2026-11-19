# Batch 4 scorecard

> Written by `pipeline/generate.py review` on 11 Nov 2026. Measured columns are filled in; the columns from "Casting" on are for Kayvan's judgement and are kept when the scorecard is rewritten.

How to read the measurements: **first frame** compares the take's first frame with its still (zoom, shift in px at 1080p, and *redraw*: about 1.5 when the still is kept, higher when the model has repainted it; a recast person must be judged by eye on the comparison sheet in `media/checks/`). **Wobble** is the frame-to-frame shake left after removing slow drift, rms and max in px at 1080p (under about 0.1 is still; above it, loop with `--lock`). **Sound** is loudness in LUFS (loudness units relative to full scale) with music and speech flags from `sound_check.py`.

## 22-man-ironing: Man ironing

Home, people; video model in scenes.yaml: Kling. Picked still: `media/stills/22-man-ironing.jpg`.

### Stills

| Still | Model | Size | Cost | Casting as described | Faces away | No extra people | No text or logos | London dusk, 35 mm | Edits needed | Pick |
|---|---|---|---|---|---|---|---|---|---|---|
| `media/stills/22/c1.jpg` | Gemini 3 Pro Image | 2752x1536 | $0.134 |  |  |  |  |  |  |  |
| `media/stills/22/c2.jpg` | Gemini 3 Pro Image | 2752x1536 | $0.134 |  |  |  |  |  |  |  |
| `media/stills/22/c3.jpg` | Gemini 3 Pro Image | 2752x1536 | $0.134 |  |  |  |  |  |  |  |
| `media/stills/22/c4.jpg` | Gemini 3 Pro Image | 2752x1536 | $0.134 |  |  |  |  |  |  |  |
| `media/stills/22/m1.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/22/m2.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/22/m3.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/22/m4.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/22/m5.jpg` | Midjourney | 2912x1632 |  |  |  |  |  |  |  | picked (Claude, 11 Nov) |
| `media/stills/22/o1.jpg` | GPT Image (2.5-flare) | 1536x864 | $0.033 |  |  |  |  |  |  |  |
| `media/stills/22/o2.jpg` | GPT Image (2.5-flare) | 1536x864 | $0.033 |  |  |  |  |  |  |  |
| `media/stills/22/o3.jpg` | GPT Image (2.6-flare) | 1536x864 | $0.041 |  |  |  |  |  |  |  |
| `media/stills/22/o4.jpg` | GPT Image (2.6-flare) | 1536x864 | $0.041 |  |  |  |  |  |  |  |
| `media/stills/22/o5.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |
| `media/stills/22/o6.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |
| `media/stills/22/o7.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |
| `media/stills/22/o8.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |

### Takes

| Take | Model | Length | Cost | Time | First frame vs still | Wobble rms / max px | Drift zoom | Sound | Casting held | Hands, objects, steam | Loops well | Keep |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `media/inbox/22-man-ironing_kling4-take1.mp4` | Kling 4.0 | 10.0 s | $2.119 | 6.5 min | +0.0%, 0 px, redraw 1.3 | 0.03 / 0.21 | +0.01% | -33 LUFS, MUSIC 0.40 (Music) |  |  |  | suggested by Claude |
| `media/inbox/22-man-ironing_wan3-take1.mp4` | Wan 3.0 | 10.0 s | $2.000 | 3.2 min | +0.2%, 0 px, redraw 3.0 | 0.06 / 0.42 | -0.02% | -16 LUFS, MUSIC 0.73 (Music) |  |  |  |  |

## 27-evening-stretch: Evening stretch

Home, people; video model in scenes.yaml: Kling. Picked still: `media/stills/27-evening-stretch.jpg`.

### Stills

| Still | Model | Size | Cost | Casting as described | Faces away | No extra people | No text or logos | London dusk, 35 mm | Edits needed | Pick |
|---|---|---|---|---|---|---|---|---|---|---|
| `media/stills/27/c1.jpg` | Gemini 3 Pro Image | 2752x1536 | $0.134 |  |  |  |  |  |  |  |
| `media/stills/27/c2.jpg` | Gemini 3 Pro Image | 2752x1536 | $0.134 |  |  |  |  |  |  |  |
| `media/stills/27/c3.jpg` | Gemini 3 Pro Image | 2752x1536 | $0.134 |  |  |  |  |  |  |  |
| `media/stills/27/c4.jpg` | Gemini 3 Pro Image | 2752x1536 | $0.134 |  |  |  |  |  |  |  |
| `media/stills/27/m1.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/27/m2.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/27/m3.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/27/m4.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/27/o1.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |
| `media/stills/27/o2.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |
| `media/stills/27/o3.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |
| `media/stills/27/o4.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  | picked (Claude, 11 Nov) |

### Takes

| Take | Model | Length | Cost | Time | First frame vs still | Wobble rms / max px | Drift zoom | Sound | Casting held | Hands, objects, steam | Loops well | Keep |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `media/inbox/27-evening-stretch_kling4-take1.mp4` | Kling 4.0 | 10.0 s | $2.119 | 4.9 min | -0.0%, 0 px, redraw 1.7 | 0.03 / 0.21 | -0.01% | -35 LUFS, no flags |  |  |  | suggested by Claude |
| `media/inbox/27-evening-stretch_wan3-take1.mp4` | Wan 3.0 | 10.0 s | $2.000 | 3.0 min | -0.0%, 0 px, redraw 3.2 | 0.69 / 2.46 | -2.63% | -44 LUFS, no flags |  |  |  |  |

## 28-nursery-night-light: Nursery night light

Dark, empty room; video model in scenes.yaml: Veo. Picked still: `media/stills/28-nursery-night-light.jpg`.

### Stills

| Still | Model | Size | Cost | Casting as described | Faces away | No extra people | No text or logos | London dusk, 35 mm | Edits needed | Pick |
|---|---|---|---|---|---|---|---|---|---|---|
| `media/stills/28/c1.jpg` | Gemini 3 Pro Image | 2752x1536 | $0.134 |  |  |  |  |  |  |  |
| `media/stills/28/c2.jpg` | Gemini 3 Pro Image | 2752x1536 | $0.134 |  |  |  |  |  |  |  |
| `media/stills/28/c3.jpg` | Gemini 3 Pro Image | 2752x1536 | $0.134 |  |  |  |  |  |  |  |
| `media/stills/28/c4.jpg` | Gemini 3 Pro Image | 2752x1536 | $0.134 |  |  |  |  |  |  |  |
| `media/stills/28/m1.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/28/m2.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/28/m3.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/28/m4.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/28/o1.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |
| `media/stills/28/o2.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  | picked (Claude, 11 Nov) |
| `media/stills/28/o3.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |
| `media/stills/28/o4.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |

### Takes

| Take | Model | Length | Cost | Time | First frame vs still | Wobble rms / max px | Drift zoom | Sound | Casting held | Hands, objects, steam | Loops well | Keep |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `media/inbox/28-nursery-night-light_omni-take1.mp4` | Gemini Omni | 10.0 s | $1.044 | 1.2 min | -0.0%, 0 px, redraw 3.0 | 0.23 / 2.05 | -0.01% | -37 LUFS, no flags |  |  |  |  |
| `media/inbox/28-nursery-night-light_wan3-take1.mp4` | Wan 3.0 | 10.0 s | $2.000 | 3.5 min | -0.0%, 0 px, redraw 3.4 | 0.02 / 0.12 | -0.00% | -50 LUFS, no flags |  |  |  | suggested by Claude |

## 34-florist-closing: Florist closing

Shop, people; video model in scenes.yaml: Kling. Picked still: `media/stills/34-florist-closing.jpg`.

### Stills

| Still | Model | Size | Cost | Casting as described | Faces away | No extra people | No text or logos | London dusk, 35 mm | Edits needed | Pick |
|---|---|---|---|---|---|---|---|---|---|---|
| `media/stills/34/c1.jpg` | Gemini 3 Pro Image | 2752x1536 | $0.134 |  |  |  |  |  |  |  |
| `media/stills/34/c2.jpg` | Gemini 3 Pro Image | 2752x1536 | $0.134 |  |  |  |  |  |  |  |
| `media/stills/34/c3.jpg` | Gemini 3 Pro Image | 2752x1536 | $0.134 |  |  |  |  |  |  |  |
| `media/stills/34/c4.jpg` | Gemini 3 Pro Image | 2752x1536 | $0.134 |  |  |  |  |  |  |  |
| `media/stills/34/m1.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/34/m2.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/34/m3.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/34/m4.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/34/o1.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |
| `media/stills/34/o2.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  | picked (Claude, 11 Nov) |
| `media/stills/34/o3.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |
| `media/stills/34/o4.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |

### Takes

| Take | Model | Length | Cost | Time | First frame vs still | Wobble rms / max px | Drift zoom | Sound | Casting held | Hands, objects, steam | Loops well | Keep |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `media/inbox/34-florist-closing_kling4-take1.mp4` | Kling 4.0 | 10.0 s | $2.119 | 5.6 min | -0.1%, 0 px, redraw 2.5 | 0.03 / 0.27 | -0.01% | -30 LUFS, no flags |  |  |  | suggested by Claude |
| `media/inbox/34-florist-closing_wan3-take1.mp4` | Wan 3.0 | 10.0 s | $2.000 | 3.5 min | -0.0%, 0 px, redraw 3.3 | 0.75 / 1.97 | +0.28% | -35 LUFS, no flags |  |  |  |  |

## 46-boutique-at-night: Boutique after closing

Quiet, empty room; video model in scenes.yaml: Veo. Picked still: `media/stills/46-boutique-at-night.jpg`.

### Stills

| Still | Model | Size | Cost | Casting as described | Faces away | No extra people | No text or logos | London dusk, 35 mm | Edits needed | Pick |
|---|---|---|---|---|---|---|---|---|---|---|
| `media/stills/46/c1.jpg` | Gemini 3 Pro Image | 2752x1536 | $0.134 |  |  |  |  |  |  |  |
| `media/stills/46/c2.jpg` | Gemini 3 Pro Image | 2752x1536 | $0.134 |  |  |  |  |  |  |  |
| `media/stills/46/c3.jpg` | Gemini 3 Pro Image | 2752x1536 | $0.134 |  |  |  |  |  |  |  |
| `media/stills/46/c4.jpg` | Gemini 3 Pro Image | 2752x1536 | $0.134 |  |  |  |  |  |  |  |
| `media/stills/46/m1.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/46/m2.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/46/m3.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/46/m4.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/46/o1.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |
| `media/stills/46/o2.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  | picked (Claude, 11 Nov) |
| `media/stills/46/o3.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |
| `media/stills/46/o4.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |

### Takes

| Take | Model | Length | Cost | Time | First frame vs still | Wobble rms / max px | Drift zoom | Sound | Casting held | Hands, objects, steam | Loops well | Keep |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `media/inbox/46-boutique-at-night_omni-take1.mp4` | Gemini Omni | 10.0 s | $1.044 | 1.5 min | -0.0%, 0 px, redraw 3.5 | 0.14 / 0.58 | +0.01% | -32 LUFS, MUSIC 0.16 (Music) |  |  |  | suggested by Claude |
| `media/inbox/46-boutique-at-night_wan3-take1.mp4` | Wan 3.0 | 10.0 s | $2.000 | 3.0 min | -0.0%, 0 px, redraw 2.9 | 0.01 / 0.03 | +0.01% | -38 LUFS, no flags |  |  |  |  |

## 49-evening-service: Evening service

Quiet, people; video model in scenes.yaml: Kling. Picked still: `media/stills/49-evening-service.jpg`.

### Stills

| Still | Model | Size | Cost | Casting as described | Faces away | No extra people | No text or logos | London dusk, 35 mm | Edits needed | Pick |
|---|---|---|---|---|---|---|---|---|---|---|
| `media/stills/49/c1.jpg` | Gemini 3 Pro Image | 2752x1536 | $0.134 |  |  |  |  |  |  |  |
| `media/stills/49/c2.jpg` | Gemini 3 Pro Image | 2752x1536 | $0.134 |  |  |  |  |  |  |  |
| `media/stills/49/c3.jpg` | Gemini 3 Pro Image | 2752x1536 | $0.134 |  |  |  |  |  |  |  |
| `media/stills/49/c4.jpg` | Gemini 3 Pro Image | 2752x1536 | $0.134 |  |  |  |  |  |  |  |
| `media/stills/49/m1.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/49/m2.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/49/m3.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/49/m4.jpg` | Midjourney | 1456x816 |  |  |  |  |  |  |  |  |
| `media/stills/49/o1.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |
| `media/stills/49/o2.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  | picked (Claude, 11 Nov) |
| `media/stills/49/o3.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |
| `media/stills/49/o4.jpg` | GPT Image (2.5-flare) | 2560x1440 | $0.056 |  |  |  |  |  |  |  |

### Takes

| Take | Model | Length | Cost | Time | First frame vs still | Wobble rms / max px | Drift zoom | Sound | Casting held | Hands, objects, steam | Loops well | Keep |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `media/inbox/49-evening-service_kling4-take1.mp4` | Kling 4.0 | 10.0 s | $2.119 | 6.9 min | -0.0%, 0 px, redraw 1.7 | 0.02 / 0.08 | -0.00% | -37 LUFS, no flags |  |  |  | suggested by Claude |
| `media/inbox/49-evening-service_wan3-take1.mp4` | Wan 3.0 | 10.0 s | $2.000 | 2.9 min | -0.0%, 0 px, redraw 3.0 | 0.01 / 0.09 | +0.00% | -47 LUFS, no flags |  |  |  |  |
