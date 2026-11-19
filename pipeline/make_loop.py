"""Turn a raw generated clip into a finished window loop with sound.

Steps (each optional):
  1. --stabilize  remove the slow push-in / drift video models add despite a locked-off prompt
                  (feature tracking + smooth fit, then a small crop to hide the edges)
     --lock       hold the picture still: cancel every frame's measured movement against the first frame
                  (sub-pixel corner tracking), which also removes the frame-to-frame tremble and sway that the
                  smooth fit lets through. With a large push-in, use both: --stabilize runs first, then --lock
  2. trim to frames [start, end) and blend the last --blend frames into the frames just
     before `start`, so the restart is a soft dissolve rather than a jump
  3. take the matching slice of the clip's own sound, crossfade its seam, scale by --volume
     --bed        use another stretch of sound instead (FILE or FILE:START-END in seconds), repeated with soft
                  crossfades so it loops seamlessly; for windows whose own sound has music or speech
  4. output 1920x1080 MP4 with AAC audio

Examples:
  python pipeline/make_loop.py media/raw/05-dinner.mp4 media/loops/05-dinner.mp4 --start 12 --blend 12 --volume 0.3
  python pipeline/make_loop.py media/raw/04-dog.mp4 media/loops/04-dog.mp4 --stabilize --start 12 --end 172 --volume 0.3
"""
import argparse
import os
import tempfile

import cv2
import numpy as np

from media import FPS, SR, frame_writer, mux, read_audio, read_frames, write_wav

W, H = 1920, 1080


def track(g0, g1, min_matches=12):
    """Similarity transform (scale, angle, dx, dy at 1920 px) taking 960x540 frame g0 to g1, or None."""
    orb = cv2.ORB_create(4000)
    k0, d0 = orb.detectAndCompute(g0, None)
    k1, d1 = orb.detectAndCompute(g1, None)
    if d0 is None or d1 is None:
        return None
    m = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(d0, d1)
    if len(m) < min_matches:
        return None
    a = np.float32([k0[x.queryIdx].pt for x in m])
    b = np.float32([k1[x.trainIdx].pt for x in m])
    M, _ = cv2.estimateAffinePartial2D(a, b, method=cv2.RANSAC, ransacReprojThreshold=1.5)
    if M is None:
        return None
    return [np.hypot(M[0, 0], M[1, 0]), np.arctan2(M[1, 0], M[0, 0]), M[0, 2] * 2, M[1, 2] * 2]


def lock_track(fr):
    """Similarity (scale, angle, dx, dy at 1920 px) from frame 0 to every frame, from sub-pixel corner tracking.
    Corners on moving subjects are rejected by RANSAC; returns None for frames that cannot be measured."""
    g = [cv2.cvtColor(x, cv2.COLOR_RGB2GRAY) for x in fr]
    g = [cv2.createCLAHE(2.0, (8, 8)).apply(x) for x in g]  # lifts dark scenes so their edges can be tracked
    p0 = cv2.goodFeaturesToTrack(g[0], 3000, 0.005, 8, blockSize=7)
    if p0 is None:
        return [None] * len(fr)
    out = []
    for x in g:
        p1, st, err = cv2.calcOpticalFlowPyrLK(g[0], x, p0, None, winSize=(31, 31), maxLevel=3,
                                               criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 40, 0.003))
        ok = st[:, 0] == 1
        if ok.sum() < 20:
            out.append(None); continue
        M, inl = cv2.estimateAffinePartial2D(p0[ok], p1[ok], method=cv2.RANSAC, ransacReprojThreshold=0.7)
        if M is None or inl.sum() < 20:
            out.append(None); continue
        out.append([np.hypot(M[0, 0], M[1, 0]), np.arctan2(M[1, 0], M[0, 0]), M[0, 2], M[1, 2]])
    return out


def stabilize(fr, lock=False):
    """Remove camera movement relative to frame 0: smooth drift only, or with lock=True every frame's movement.
    Returns new frames (same size, slightly cropped in)."""
    n = len(fr)
    cv2.setRNGSeed(0)  # RANSAC is random; a fixed seed makes rebuilds from scenes.yaml repeatable
    if lock:
        P = lock_track(fr)
    else:
        g = [cv2.cvtColor(cv2.resize(x, (960, 540)), cv2.COLOR_RGB2GRAY) for x in fr]
        P = [track(g[0], g[i]) for i in range(n)]
    ok = np.array([p is not None for p in P])
    if ok.sum() < max(8, n // 4):
        raise SystemExit(f"stabilize: only {ok.sum()} of {n} frames could be tracked (too dark or featureless); "
                         "run without --stabilize")
    if not ok.all():
        print(f"stabilize: {n - ok.sum()} frames untracked, fitted from the others")
    P = np.array([p for p in P if p is not None])
    t = np.arange(n)
    if lock:  # follow the measured movement exactly; untracked frames are interpolated
        Ps = np.stack([np.interp(t, t[ok], P[:, j]) for j in range(4)], 1)
    else:  # drift is smooth: fit a cubic to the tracked frames and evaluate it on every frame
        Ps = np.stack([np.polyval(np.polyfit(t[ok], P[:, j], 3), t) for j in range(4)], 1)
    Ps[0] = [1, 0, 0, 0]
    mats = [np.array([[s * np.cos(th), -s * np.sin(th), dx], [s * np.sin(th), s * np.cos(th), dy]], np.float32)
            for s, th, dx, dy in Ps]
    x0, y0, x1, y1 = 0, 0, W, H
    for M in mats:  # largest box that stays valid in every frame
        c = cv2.transform(np.float32([[[0, 0], [W, 0], [0, H], [W, H]]]), cv2.invertAffineTransform(M))[0]
        x0 = max(x0, c[[0, 2], 0].max()); x1 = min(x1, c[[1, 3], 0].min())
        y0 = max(y0, c[[0, 1], 1].max()); y1 = min(y1, c[[2, 3], 1].min())
    cw = min(x1 - x0, (y1 - y0) * 16 / 9); ch = cw * 9 / 16
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    C = np.array([[W / cw, 0, -(cx - cw / 2) * W / cw], [0, W / cw, -(cy - ch / 2) * W / cw], [0, 0, 1]], np.float32)
    print(f"stabilize: crop zoom {W / cw:.3f}x")
    out = np.empty_like(fr)
    for i in range(n):
        A = (C @ np.vstack([cv2.invertAffineTransform(mats[i]), [0, 0, 1]]))[:2]
        out[i] = cv2.warpAffine(fr[i], A, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
    return out


def loop_sound(b, n, x):
    """Repeat sound b to n samples with equal-power crossfades of x samples; seamless when the result repeats."""
    x = max(1, min(x, len(b) // 3))
    t = np.linspace(0, 1, x)[:, None]
    fi, fo = np.sin(t * np.pi / 2), np.cos(t * np.pi / 2)
    out = b.copy()
    while len(out) < n + x:
        out = np.concatenate([out[:-x], out[-x:] * fo + b[:x] * fi, b[x:]])
    out = out[:n + x].copy()
    out[:x] = out[:x] * fi + out[n:n + x] * fo  # fold the tail into the head, so the end flows into the start
    return out[:n]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--start", type=int, default=12, help="first frame of the loop (must be >= blend)")
    ap.add_argument("--end", type=int, default=None, help="frame after the last one kept (default: clip end)")
    ap.add_argument("--blend", type=int, default=12, help="frames of soft blend at the restart (12 = half a second)")
    ap.add_argument("--volume", type=float, default=0.3, help="audio gain; windows sit quietly in the mix")
    ap.add_argument("--stabilize", action="store_true", help="remove camera drift first")
    ap.add_argument("--lock", action="store_true", help="hold the picture still: remove drift, sway and tremble")
    ap.add_argument("--bed", help="sound from FILE or FILE:START-END (seconds) instead of the clip's own, looped")
    a = ap.parse_args()

    fr = read_frames(a.src, W, H)
    if a.stabilize:  # remove the smooth push-in first, so --lock only has small movements left to follow
        fr = stabilize(fr)
    if a.lock:
        fr = stabilize(fr, lock=True)
    S, E, K = a.start, a.end or len(fr), a.blend
    assert K <= S < E <= len(fr), "need blend <= start < end <= frames"
    L = E - S

    tmp = tempfile.mkdtemp()
    vtmp = os.path.join(tmp, "v.mp4")
    p = frame_writer(vtmp, W, H, crf=16)
    for t in range(L):
        img = fr[S + t].astype(np.float32)
        k = t - (L - K)
        if k >= 0:  # dissolve the tail into the frames just before the loop start
            w = (k + 1) / (K + 1)
            img = img * (1 - w) + fr[S - K + k].astype(np.float32) * w
        p.stdin.write(np.clip(img, 0, 255).astype(np.uint8).tobytes())
    p.stdin.close(); p.wait()

    N = int(round(L / FPS * SR))  # audio must cover every video frame, or -shortest drops the last ones
    au = read_audio(a.src)
    if a.bed:
        path, _, rng = a.bed.partition(":")
        bed = read_audio(path)
        if rng:
            b0, b1 = (float(v) for v in rng.split("-"))
            bed = bed[int(b0 * SR):int(b1 * SR)]
        if not len(bed):
            raise SystemExit(f"--bed {a.bed}: no sound there")
        seg = loop_sound(bed, N, int(0.5 * SR))
    elif len(au):
        aS = int(round(S / FPS * SR))
        seg = au[aS:aS + N].copy()
        if len(seg) < N:  # generated audio often ends a few milliseconds before the video
            seg = np.concatenate([seg, np.zeros((N - len(seg), 2), np.float32)])
        X = min(max(int(K / FPS * SR), int(0.4 * SR)), aS, N)
        if X > 0:  # equal-power crossfade of the tail into the sound just before the loop start
            tt = np.linspace(0, 1, X)[:, None]
            seg[-X:] = seg[-X:] * np.cos(tt * np.pi / 2) + au[aS - X:aS] * np.sin(tt * np.pi / 2)
    else:
        seg = np.zeros((N, 2), np.float32)
    wtmp = os.path.join(tmp, "a.wav")
    write_wav(wtmp, seg * a.volume)
    mux(vtmp, wtmp, a.out)
    print(f"{a.out}: {L / FPS:.2f} s loop")


if __name__ == "__main__":
    main()
