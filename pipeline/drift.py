"""Measure camera movement in a clip, relative to its first frame: slow drift (zoom and shift) and wobble.

Drift: zoom and shift at five evenly spaced frames. Anything above about 0.5% zoom will show as a jump at
the loop point; fix it with make_loop.py --stabilize.

Wobble: every frame is tracked against frame 0 (ORB features, RANSAC similarity fit, as measured on 9 Nov
2026), the slow drift is removed with a 9-frame moving average, and what is left is the frame-to-frame
tremble and sway that a close-up magnifies. Reported as rms and max movement of the frame corners, in px at
1080p. About 0.05 px rms or less is still; Veo and Omni clips measured 0.2 to 1.4 px before make_loop.py
--lock, which brings most to about 0.03 px.

Usage: python pipeline/drift.py media/raw/clip.mp4 [more clips...]
       python pipeline/drift.py media/raw/clip.mp4 --quick     # drift only, five frames (fast)
"""
import argparse

import cv2
import numpy as np

from make_loop import track
from media import FPS, read_frames

CORNERS = np.float32([[0, 0], [1920, 0], [0, 1080], [1920, 1080]])


def drift(path, samples=5, frames=None):
    """Return [(seconds, zoom %, dx px, dy px)] at evenly spaced frames; None values if a frame can't be tracked."""
    cv2.setRNGSeed(0)
    f = read_frames(path, 960, 540, gray=True) if frames is None else frames
    rows = []
    for i in np.linspace(0, len(f) - 1, samples).astype(int):
        p = track(f[0], f[i])
        rows.append((i / FPS, *((100 * (p[0] - 1), p[2], p[3]) if p else (None, None, None))))
    return rows


def wobble(path, window=9, frames=None):
    """Frame-to-frame movement left after removing the slow drift: (rms px, max px, tracked frames, total frames)
    at 1080p, or (None, None, tracked, total) when too few frames can be tracked."""
    cv2.setRNGSeed(0)
    f = read_frames(path, 960, 540, gray=True) if frames is None else frames
    n = len(f)
    P = [track(f[0], f[i]) for i in range(n)]
    ok = np.array([p is not None for p in P])
    if ok.sum() < max(window * 2, n // 2):
        return None, None, int(ok.sum()), n
    pts = np.full((n, 4, 2), np.nan, np.float32)
    for i, p in enumerate(P):
        if p is None:
            continue
        s, th, dx, dy = p  # track() gives the shift at 1920 px; scale and angle act about the origin
        M = np.float32([[s * np.cos(th), -s * np.sin(th), dx], [s * np.sin(th), s * np.cos(th), dy]])
        pts[i] = cv2.transform(CORNERS[None], M)[0]
    t = np.arange(n)
    pts = np.stack([np.interp(t, t[ok], pts[ok, c, k]) for c in range(4) for k in range(2)], 1)  # fill untracked
    pad = window // 2
    padded = np.pad(pts, ((pad, pad), (0, 0)), mode="edge")
    slow = np.stack([np.convolve(padded[:, j], np.ones(window) / window, "valid") for j in range(pts.shape[1])], 1)
    res = (pts - slow).reshape(n, 4, 2)
    mag = np.hypot(res[..., 0], res[..., 1]).mean(1)[ok]  # mean corner movement per tracked frame
    return float(np.sqrt((mag ** 2).mean())), float(mag.max()), int(ok.sum()), n


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--quick", action="store_true", help="drift at five frames only, no wobble")
    a = ap.parse_args()
    for path in a.files:
        if len(a.files) > 1:
            print(path)
        f = read_frames(path, 960, 540, gray=True)
        for t, z, dx, dy in drift(path, frames=f):
            if z is None:
                print(f"{t:5.1f}s  not trackable (too dark or featureless)")
            else:
                print(f"{t:5.1f}s  zoom {z:+.2f}%  shift {dx:+.1f}, {dy:+.1f} px")
        if not a.quick:
            rms, mx, tracked, n = wobble(path, frames=f)
            if rms is None:
                print(f"wobble: not trackable ({tracked} of {n} frames)")
            else:
                print(f"wobble {rms:.2f} px rms, max {mx:.2f} px at 1080p ({tracked} of {n} frames tracked)")


if __name__ == "__main__":
    main()
