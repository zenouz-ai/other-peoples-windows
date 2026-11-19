"""Export the zenouz.ai assets: a silent looping mosaic (no camera moves) and its poster frame.

Matches what the project page uses (public/assets/windows/ in zenouz-ai/website): 720x1280, 24 fps,
H.264, no audio, 15 s, about 3 MB (Cloudflare Pages caps files at 25 MB; keep it under 10 MB).

Usage:
  python pipeline/web_export.py layouts/poster-6.yaml                  # page 1 of any layout
  python pipeline/web_export.py layouts/facade-pages.yaml --page 2 --seconds 15
Writes web/windows-mosaic-loop.mp4 and web/windows-mosaic-poster.jpg, then copy them into the website repo.
"""
import argparse
import os

import cv2
import numpy as np

from media import FPS, frame_writer
from mosaic import SRC_H, SRC_W, Layout, Loop, Renderer


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("layout")
    ap.add_argument("--page", type=int, default=1, help="which screen of the facade to show (1 = top)")
    ap.add_argument("--seconds", type=float, default=15.0)
    ap.add_argument("--width", type=int, default=720)
    ap.add_argument("--crf", type=int, default=24)
    ap.add_argument("--out", default="web")
    a = ap.parse_args()

    L = Layout(a.layout)
    view = L.page((a.page - 1) * L.VH)
    L.segs, L.duration = [(0.0, a.seconds, view, view, None, 0.0, 0.0)], a.seconds  # hold one screen, no tour
    R = Renderer(L, a.width / L.OW)
    top, bottom = view[1] - L.VH / 2, view[1] + L.VH / 2
    ids = [k for k, v in L.win.items() if v["y"] < bottom and v["y"] + v["h"] > top]  # only decode what is visible
    loops = {k: Loop(L.win[k]["file"]) for k in ids}
    blank = np.zeros((SRC_H, SRC_W, 3), np.uint8)

    os.makedirs(a.out, exist_ok=True)
    loop, poster = os.path.join(a.out, "windows-mosaic-loop.mp4"), os.path.join(a.out, "windows-mosaic-poster.jpg")
    enc = frame_writer(loop, R.OW, R.OH, crf=a.crf, preset="slow")
    for i in range(int(round(a.seconds * FPS))):
        img = R.frame(lambda k: loops[k].get(i) if k in loops else blank, i / FPS)[0]
        if i == 0:
            cv2.imwrite(poster, cv2.cvtColor(img, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 88])
        enc.stdin.write(img.tobytes())
    enc.stdin.close(); enc.wait()
    for lp in loops.values():
        lp.close()
    mb = os.path.getsize(loop) / 1e6
    print(f"{loop}: {a.seconds:.0f} s, {R.OW}x{R.OH}, {mb:.1f} MB, silent" + ("  (over 10 MB: raise --crf)" if mb > 10 else ""))
    print(f"{poster}")


if __name__ == "__main__":
    main()
