# Architecture

How Other People's Windows turns a few lines of text into a 4K film. Every stage is a small Python script run from the project root; the stages share one data file (`scenes/scenes.yaml`) and one folder of media (`media/`, not in this repository).

## Data

| Path | What it holds |
|---|---|
| `scenes/scenes.yaml` | One entry per window: `id` (`NN-short-name`), title, kind, model, status (`done`, `cut`), the prompt parts (`scene`, `motion`, `ambience`, `empty`), and for made windows the still, raw clip, loop, exact `loop_settings` and notes. A shared `prompt_style` block holds the house wording. |
| `pipeline/generate.yaml` | Models, sizes, clip lengths and prices for every provider, budget caps, and the ledger path, kept in one place because providers rename and retire models. |
| `layouts/*.yaml` | Canvas and output size, the slot geometry of one page, the windows (loop file and close-up focus), the pages, and the camera timing. |
| `media/stills/NN/` | Candidate stills (`c1` Gemini, `o1` GPT Image, `k1` Kling Image, `m1` Midjourney); the pick is copied to `media/stills/NN-name.jpg`. |
| `media/raw/`, `media/loops/` | Takes exactly as generated (rejected ones keep a `_rejected` suffix and serve as a sound library) and finished loops. |
| `media/generate-ledger.jsonl` | Every paid call, its estimate and its actual cost (private). |

A loop can always be rebuilt from its raw clip, because `loop_settings` records the exact `make_loop.py` arguments.

## Stages

### 1. Prompts (`pipeline/prompts.py`)

The image prompt is the scene plus the house style: 35 mm photograph, London at dusk in late autumn, cool light outside and warm inside, people small and turned away, every sign and screen blank. The video prompt is a locked-off tripod shot that animates the exact image, the window's one slow motion, the ambience labelled as faint and heard through glass, and "No music, no singing, no dialogue". `lint` rejects ambience that mentions music, radio, television, voices or talking, because models answer those with music or speech. `brief` writes a Markdown and PDF brief for a batch; `show NN --midjourney` prints the hand-made Midjourney prompt.

### 2. Stills and takes (`pipeline/generate.py`)

- `still NN --engine gemini|openai|kling` asks for candidates through each provider's API; `edit` revises one; `import` brings in hand-made Midjourney images or videos with a checksum check against every window.
- `video NN --engine kling|wan|omni` sends the picked still as the first frame of a 10 second, 1080p take. `--engine kling,wan` sends one still to two models for comparison.
- Every command prints its plan and cost first. `--dry-run` stops there; otherwise it asks before spending (or takes `--yes`). A per-command and per-batch budget cap refuses anything over the limit, and each call is written to the ledger with its actual cost (from the token or duration usage the provider returns).
- Long video tasks are polled and downloaded at once (Wan results expire after 24 hours).

### 3. Checks (`generate.py check` and `review`)

For every take:

- **First frame against the still:** an affine fit gives zoom, stretch and shift, and a redraw score says how much the model repainted. A recast person cannot be measured reliably, so a side-by-side sheet is written for a human to judge.
- **Drift and wobble** (`pipeline/drift.py`): ORB features and a RANSAC similarity fit track every frame against the first; slow drift is the fitted zoom and shift, wobble is what is left after a 9-frame moving average, in px rms at 1080p.
- **Sound** (`pipeline/sound_check.py`): loudness in LUFS, peak, and the top AudioSet tags from PANNs CNN14, with flags for music (0.15) and clear speech (0.30).

`review` writes a scorecard (`docs/batch-NN-scorecard.md`) with the measurements filled in and blank columns for human judgement, which it keeps when it rewrites the file.

### 4. Loops (`pipeline/make_loop.py`)

1. Optional `--stabilize` removes a slow push-in with a smooth fit; `--lock` cancels every frame's measured movement against the first (sub-pixel corner tracking), which also removes tremble.
2. Trim to `[start, end)` and dissolve the last `blend` frames into the frames just before `start`, so the restart is a soft half-second blend rather than a jump. End frames are chosen by the smallest picture difference at the join.
3. Sound: the clip's own, or `--bed FILE:START-END`, a clean stretch from any clip, repeated with crossfades; scaled by `--volume`.

### 5. The film (`pipeline/mosaic.py`)

- A page is one screen with a fixed slot template; pages stack down a tall canvas. The camera holds on the page, zooms into each window to its `focus` (centre and close-up width), holds for one loop, zooms out, then scrolls to the next page, and finally back to the top so the film loops.
- Frame `i` of the film always shows frame `i mod n` of each window, so only the windows near the camera are decoded (about 6 of 30 at a time), and the result is identical to decoding all of them.
- Sound follows the camera: windows in view are audible, the focused one is lifted and the others lowered, and windows out of view fade away. The final mix is limited to a fixed peak.

The layouts share one running order, from dusk to bedtime: `facade-landscape-3x10.yaml` (16:9, 3840x2160, the published film: three walls of ten, two large windows and eight small on a 4x4 grid of 16:9 cells, so no clip is cropped; windows seen high up or across gardens get a per-window `gain` so they are heard faintly, if at all), `facade-landscape.yaml` (the first 16:9 cut, one large window and five smaller per page), `facade-pages.yaml` (9:16, 2160x3840, the geometry of the first published poster) and `short-2pages.yaml` (the twelve strongest windows on two 9:16 pages for YouTube Shorts).

## Keys and costs

Keys are read from the environment or a git-ignored `.env` file: `GEMINI_API_KEY` (or `GOOGLE_API_KEY`), `KLING_API_KEY` (or `KLING_AI_API_KEY`), `OPENAI_API_KEY` and `DASHSCOPE_API_KEY`. Prices used for estimates live in `pipeline/generate.yaml`; in November 2026 a 10 second 1080p take cost about $2.12 on Kling 4.0, $2.00 on Wan 3.0 and $1.04 on Gemini Omni, and a 2560x1440 GPT Image still about $0.06.

## Dependencies

Python 3.11, NumPy, OpenCV, PyYAML, ReportLab (brief PDFs) and FFmpeg (from PATH or the `static-ffmpeg` package), all in `requirements.txt`. The sound checker also needs PyTorch, librosa and `panns_inference` (`requirements-audio.txt`, about 1 GB) and the PANNs model files, downloaded once:

```bash
mkdir -p ~/panns_data && cd ~/panns_data \
  && curl -LO http://storage.googleapis.com/us_audioset/youtube_corpus/v1/csv/class_labels_indices.csv \
  && curl -L -o "Cnn14_mAP=0.431.pth" "https://zenodo.org/record/3987831/files/Cnn14_mAP%3D0.431.pth?download=1"
```
