"""Check a clip's sound against the house rules: no music, and only faint sound that fits the scene.

For each file it prints the loudness (integrated LUFS, from FFmpeg's EBU R128 meter), the peak level,
and the top AudioSet tags from a pretrained PANNs model, then flags music and clear speech.

Usage:
  python pipeline/sound_check.py media/raw/07-launderette.mp4 [more files...]
  python pipeline/sound_check.py media/loops/*.mp4 --top 3

Needs the optional audio extras (pip install -r requirements-audio.txt) and, once, the model files
in ~/panns_data (see docs/ARCHITECTURE.md). Flags are hints for a human listen, not a verdict.
"""
import argparse
import re
import subprocess
import sys

import numpy as np

import media  # noqa: F401  (makes sure ffmpeg is on PATH)

MUSIC =range(137, 283)  # AudioSet "Music" through the instrument, genre and mood classes
SPEECH = range(0, 8)     # Speech, male/female/child speech, conversation, narration, babbling
MUSIC_FLAG, SPEECH_FLAG = 0.15, 0.30
FAINT_LUFS = -30.0       # finished loops should sit at or below this; the renderer lifts the focused window


def loudness(path):
    """Integrated loudness (LUFS) and true peak (dBFS) via FFmpeg, or (None, None) with no audio."""
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-vn", "-af", "ebur128=peak=true",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    i = re.findall(r"I:\s+(-?[\d.]+|-inf) LUFS", err)
    p = re.findall(r"Peak:\s+(-?[\d.]+|-inf) dBFS", err)
    f = lambda v: None if not v or v[-1] == "-inf" else float(v[-1])
    return f(i), f(p)


def audio32k(path):
    """Mono float audio at 32 kHz (the rate PANNs was trained on); empty if the clip is silent."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", "32000", "-f", "f32le", "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.float32)


def tagger():
    from panns_inference import AudioTagging  # imported late: slow, and optional
    return AudioTagging(checkpoint_path=None, device="cpu")


def measure(path, model, top=5):
    """Loudness, peak, the top AudioSet tags and the music and speech scores of one clip, with its flags.
    Returns a dict; `silent` is True (and the rest None) when the clip has no audible sound."""
    from panns_inference import labels
    lufs, peak = loudness(path)
    au = audio32k(path)
    if not len(au) or lufs is None or peak is None:  # muted loops have silence, not a level
        return {"silent": True, "lufs": None, "peak": None, "music": None, "speech": None, "tags": "", "flags": []}
    p, _ = model.inference(au[None, :])
    p = p[0]
    music, speech = float(p[list(MUSIC)].max()), float(p[list(SPEECH)].max())
    tags = ", ".join(f"{labels[i]} {p[i]:.2f}" for i in np.argsort(p)[::-1][:top])
    flags = []
    if music >= MUSIC_FLAG:
        flags.append(f"MUSIC {music:.2f} ({labels[int(np.argmax(np.where(np.isin(np.arange(len(p)), MUSIC), p, 0)))]})")
    if speech >= SPEECH_FLAG:
        flags.append(f"SPEECH {speech:.2f}")
    if "/loops/" in path and lufs > FAINT_LUFS:
        flags.append(f"LOUD (loop above {FAINT_LUFS:.0f} LUFS)")
    return {"silent": False, "lufs": lufs, "peak": peak, "music": music, "speech": speech, "tags": tags, "flags": flags}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--top", type=int, default=5, help="how many tags to show")
    a = ap.parse_args()

    model = tagger()
    flagged = 0
    for path in a.files:
        m = measure(path, model, a.top)
        if m["silent"]:
            print(f"{path}\n   silent or no audio track")
            continue
        flagged += bool(m["flags"])
        print(f"{path}\n   {m['lufs']:6.1f} LUFS, peak {m['peak']:+.1f} dBFS | {m['tags']}"
              + (f"\n   FLAG: {'; '.join(m['flags'])}" if m["flags"] else ""))
    sys.exit(1 if flagged else 0)


if __name__ == "__main__":
    main()
