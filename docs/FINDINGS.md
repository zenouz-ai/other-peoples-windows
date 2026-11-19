# Findings

What making thirty AI windows taught us, recorded as it happened between 7 and 13 November 2026. Each finding comes from measurements in the scorecards or from notes on specific windows in `scenes/scenes.yaml`; where a judgement was made by eye, it says so. Models change fast, so read this as a dated field report.

## The brief the models were held to

Every window had to meet the same rules: one slow, continuous motion that loops; nobody entering, leaving, standing up or looking at the camera; nothing thrown, poured or passed through glass; people small and turned away; no readable text or logos; faint ambience that matches the scene and never music or words; London at dusk in late autumn; casting that reflects London. Most of the findings below are about which tools could keep to that, and how the failures were caught.

## Video models

**Kling 4.0 for people.** Used for 17 of the 30 windows. It kept the still as the exact first frame (redraw score about 1.3 to 2.2, against 2.4 to 3.5 for Omni and Wan), held the casting, and its camera barely moved: drift under 0.01% of zoom, wobble about 0.01 to 0.07 px rms at 1080p. Hands with objects (ironing, arranging tulips, turning a page) held up. Its weakness is sound: it produced music, speech, birds, and once a chicken and a rooster in a London florist, so every Kling window has a replacement sound bed.

**Veo 3.1 (in Flow) for the first windows (9 of the 30).** Good atmosphere (steam, fire, rain, television glow), but the camera crept in by 4 to 9% over eight seconds despite a locked-off prompt, and the picture trembled frame to frame. It also once added piano music to a café. Two of its takes were remade on Kling: the high-rise kitchen came out 70 times steadier and a third sharper; the café remake came out four times softer, so the original was kept.

**Wan 3.0 for empty rooms, checked frame by frame (2 of the 30).** In the six-window shoot-out it made the best empty nursery (the mobile turns, the projected stars drift), and later the empty pool, with light rippling across the ceiling. But it broke a rule on three of six takes: a neon sign switched on halfway with a glyph like a character, steam billowed and softened a man's face, and one take pushed the camera in by 2.6%. Its takes tremble (up to 0.75 px) and need locking.

**Gemini Omni (Veo's successor on the Gemini API) for quiet scenes.** It repaints the still rather than animating it, recast a person in one take, and trembles; locking took one boutique window from 0.14 to 0.04 px. Used for two windows.

## Image models

**GPT Image 2.5 follows instructions best.** People small and turned away, no pedestrians, no readable text, the family of four counted correctly in every candidate. At 2560x1440 it cost about $0.06 a still. Picked for most windows in the last two batches.

**Midjourney looks most photographic.** Moodier, more filmic grain and light, but it breaks the brief in its own ways: people large and in profile, extra figures, and it would not look down through basement railings. Its images come at 1456x816 and need upscaling (Subtle, to 2912x1632) before animation. Picked for three windows where its mood won.

**Gemini 3 Pro Image is the sharpest,** and the best for edits, but it adds pedestrians, buses and readable shop names.

**All of them drift towards default faces.** Prompts say "Keep the people exactly as described", and every still is checked for casting before it is animated.

## Things that only measurement caught

- **Shake.** A smooth stabiliser removes a slow push-in but leaves frame-to-frame tremble, which a close-up magnifies. Measuring wobble (corner movement after removing the slow drift) found it, and locking every frame to the first one brought most shaky windows down to about 0.03 to 0.08 px rms. Windows seen through glass with moving reflections got worse when locked, so each one is compared before and after.
- **Sound that sounds fine.** AudioSet tagging flagged music in takes that seemed quiet (a basement kitchen whose first two seconds tagged music 0.78), clear speech in a busy café, and a click in a rain bed (peak -8.6 dBFS) that a quieter stretch of the same clip avoided (-16.1 dBFS). The rejected takes turned out to be the best library of clean ambience.
- **Loop joins.** Choosing the end frame by the smallest picture difference at the join, then dissolving over half a second, gave joins that read as continuous; perfect loops were not needed.

## Scenes the models could not do

- A church seen from the street through a plate-glass window: every model drew an impossible window. It became a service seen from the church porch.
- Scenes whose subject makes music (a piano, a dance class) were cut, because the models add the music.
- One-off events (a light switching off, someone entering) break the loop, and several models added them unasked.

## Cost and time

Every paid API call is logged with its cost and timing. The 30 windows, the six-window shoot-out and two remakes came to **$59.19 of API calls**, on top of subscriptions and app credits used for the first windows (Veo 3.1 in Google Flow, Kling's app) and Midjourney by hand.

| Model | Kept | Cost | Unit cost | Time per call (median, range) |
|---|---|---|---|---|
| Kling 4.0 video | 14 takes | $29.67 | $2.12 per 10 s take | 6.3 min (4.1 to 18.1) |
| Wan 3.0 video | 7 takes | $14.00 | $2.00 per 10 s take | 3.2 min (2.9 to 3.8) |
| Gemini Omni 1.2 Flash video | 4 takes | $4.18 | $1.04 per 10 s take | 1.3 min (1.2 to 1.5) |
| Gemini 3 Pro Image | 55 stills | $7.37 | $0.134 a still | 25 s (22 to 35) |
| GPT Image 2.5 and 2.6 | about 56 stills | $3.51 | about $0.06 a still at 2560x1440 | 67 s per call of up to four |
| Kling Image 3.0 | 16 stills | $0.45 | $0.028 a still | 62 s per call of four |

A finished window typically cost a set of still candidates (about $0.25 to $0.55) and one or two takes (about $1 to $2 each). Failed calls (network failures, rate limits, a trial plan's parallel-task limit) cost nothing but time.

Time: seven calendar days from idea to the public films (7 to 13 November 2026). The first six windows were made by hand in chat and in Google Flow; the pipeline sessions that made the other 24, ran the shoot-out and rendered the films took about nine hours of active work across four days, with generation and rendering running in the background. The 16:9 4K film renders in about 14 minutes.

## Which provider for which job

| Job | Best in November 2026 | Main caveat |
|---|---|---|
| People in motion | Kling 4.0 | Replace its sound every time |
| Empty, atmosphere-led rooms | Wan 3.0 | Check every take frame by frame; lock it |
| Fast, cheap quiet scenes | Gemini Omni | Repaints the still; trembles |
| Stills that follow the brief | GPT Image 2.5 | Slightly soft at full size |
| Stills with mood | Midjourney | Low resolution until upscaled; people too large; no API |
| Sharpness and edits | Gemini 3 Pro Image | Adds pedestrians and readable signs |

## The hardest problems

1. **Camera creep and tremble**, invisible in a thumbnail and obvious in a close-up; solved by measuring wobble and locking frames.
2. **Sound**: models add music, speech and animals to silent rooms; solved by tagging every take and borrowing clean ambience from rejected takes.
3. **Keeping models to the rules**: readable signs, extra people, faces to camera, default casting, one-off events; solved by a shared prompt style, a lint, scorecards and checking every take.
4. **Physics and impossible spaces**: balls through glass, a church window no street could see through; solved by writing scenes around one slow cyclic motion.
5. **Providers changing under the project**: a video model left its API mid-project and another retires within weeks; solved by keeping every model and price in one config file.

## Lessons

- Choose models by job, on the same prompts, with a written scorecard.
- Measure what the eye misses at preview size.
- Keep rejected takes: they are the best sound library.
- Keep every setting in data so any window can be rebuilt.
- Budget caps, dry runs and a ledger make paid calls safe to automate.
- Fewer, better windows: cutting from 50 to 30 is what finished the work.
