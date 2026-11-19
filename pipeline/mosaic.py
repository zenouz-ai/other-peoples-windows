"""Render the mosaic film: a tall facade of looping windows and a virtual camera that tours it.

The layout (window positions, sizes, overlaps, tour order, timing) lives in a YAML file in layouts/.
The canvas can be taller than one 9:16 screen: the camera then scrolls down the facade, zooms into a
window, holds, zooms back out, scrolls on to the next one, and finally scrolls back to the top so the
film loops cleanly. Sound follows the camera: windows in view are audible, the focused one is lifted,
and windows scrolled out of view fade away.

Only the windows in or near the camera's view are decoded. The others are paused, not reset: frame i of
the film always shows frame (i mod clip length) of each window, so a window that scrolls back into view
is exactly where a continuous loop would be, and the frames are identical to decoding every window all
the time (checked on the three-page facade, 10 Nov 2026).

Usage:
  python pipeline/mosaic.py layouts/poster-6.yaml output/tour.mp4
  python pipeline/mosaic.py layouts/poster-6.yaml output/preview.mp4 --scale 0.25        # fast low-res preview
  python pipeline/mosaic.py layouts/poster-6.yaml output/stills --stills 5,16,25           # PNG frames to check framing
  python pipeline/mosaic.py layouts/poster-6.yaml output/youtube.mp4 --crf 14 --preset medium   # YouTube master
"""
import argparse
import json
import math
import os
import queue
import re
import subprocess
import tempfile
import threading
import time

import cv2
import numpy as np
import yaml

from media import FPS, SR, frame_writer, mux, read_audio, write_wav

SRC_W, SRC_H = 1920, 1080


def hex_rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.uint8)


def ease(u):
    return 0.5 - 0.5 * math.cos(math.pi * min(max(u, 0.0), 1.0))


class Layout:
    def __init__(self, path):
        cfg = yaml.safe_load(open(path))
        self.cfg = cfg
        c = cfg["canvas"]
        self.CW = c["width"]
        self.gap = c.get("gap", 12)
        self.bg = hex_rgb(c.get("background", "#0b0e13"))
        o = cfg.get("output", {})
        self.OW, self.OH = o.get("width", 2160), o.get("height", 3840)
        self.VH = self.CW * self.OH / self.OW  # one screen of canvas
        if "pages" in cfg:
            cfg = self.expand_pages(cfg)
        self.win = {}
        for w in cfg["windows"]:
            if w["id"] in self.win:
                raise ValueError(f"{path}: window id '{w['id']}' is placed twice; give each placement its own id")
            if not os.path.exists(w["file"]):
                raise FileNotFoundError(f"{path}: window '{w['id']}' needs {w['file']}, which does not exist")
            x, y, ww, hh = w["rect"]
            fx, fy, zw = w.get("focus", [0.5, 0.5, 0.94])
            self.win[w["id"]] = dict(file=w["file"], x=x, y=y, w=ww, h=hh, layer=w.get("layer", 0),
                                     gain=w.get("gain", 1.0), focus=(x + fx * ww, y + fy * hh, zw * ww),
                                     page_top=w.get("page_top"))
        bottom = max(v["y"] + v["h"] for v in self.win.values()) + self.gap
        self.CH = max(c.get("height") or 0, bottom, self.VH)
        self.order = sorted(self.win, key=lambda k: self.win[k]["layer"])
        self.tour = cfg.get("tour", list(self.win))
        self.build_camera(cfg.get("timing", {}))

    def expand_pages(self, cfg):
        """Page layout: every page reuses the same slot template (the published six-window poster)
        and pages stack down the facade. Each page entry maps slot -> window id; the tour visits
        each page's windows in `slot_order`, scrolling to the next page in between."""
        slots, lib = cfg["slots"], {w["id"]: w for w in cfg["windows"]}
        order = cfg.get("slot_order", list(slots))
        windows, tour = [], []
        for p, page in enumerate(cfg["pages"]):
            dy = p * self.VH
            for slot in order:
                wid = page.get(slot)
                if not wid:
                    continue
                if wid not in lib:
                    raise ValueError(f"page {p + 1}, slot {slot}: no window with id '{wid}' under `windows`")
                s, w = slots[slot], lib[wid]
                x, y, ww, hh = s["rect"]
                # page_top keeps the camera on this page's screen, exactly as on the single-screen poster
                windows.append({**w, "rect": [x, y + dy, ww, hh], "layer": s.get("layer", 0), "page_top": dy})
                tour.append(wid)
        return {**cfg, "windows": windows, "tour": cfg.get("tour", tour)}

    # ---- camera path -------------------------------------------------------
    def page(self, y):
        """Full-width view whose top edge sits at canvas y."""
        y = min(max(y, 0), self.CH - self.VH)
        return (self.CW / 2, y + self.VH / 2, self.CW)

    def build_camera(self, t):
        intro, zin, hold = t.get("intro_hold", 10), t.get("zoom_in", 1.3), t.get("hold", 5)
        zout, gap, end = t.get("zoom_out", 1.3), t.get("gap", 0.8), t.get("end_hold", 3)
        per_screen = t.get("scroll_seconds_per_screen", 3.0)
        segs, now = [], 0.0
        cur = self.page(0)

        def add(dur, v0, v1, focus=None, w0=0.0, w1=0.0):
            nonlocal now
            if dur > 0:
                segs.append((now, now + dur, v0, v1, focus, w0, w1))
                now += dur

        page_hold = t.get("page_hold", 2.0)

        def scroll_to(v, settle=True):
            nonlocal cur
            dist = abs(v[1] - cur[1]) / self.VH
            if dist > 0.01:
                add(min(max(dist * per_screen, 1.0), 8.0), cur, v)
                if settle:
                    add(page_hold, v, v)  # let the new page sit for a moment before zooming
            cur = v

        add(intro, cur, cur)
        for i, k in enumerate(self.tour):
            f, top = self.win[k]["focus"], self.win[k]["page_top"]
            scroll_to(self.page(top if top is not None else f[1] - self.VH / 2))
            add(zin, cur, f, k, 0, 1)
            add(hold, f, f, k, 1, 1)
            add(zout, f, cur, k, 1, 0)
            if i < len(self.tour) - 1:
                add(gap, cur, cur)
        scroll_to(self.page(0), settle=False)
        add(end, cur, cur)
        self.segs, self.duration = segs, now

    def view_at(self, tt):
        for a, b, v0, v1, k, w0, w1 in self.segs:
            if tt < b or b == self.segs[-1][1]:
                u = ease((tt - a) / (b - a))
                w = math.exp((1 - u) * math.log(v0[2]) + u * math.log(v1[2]))
                s = (v0[2] - w) / (v0[2] - v1[2]) if abs(v0[2] - v1[2]) > 1e-6 else u
                return v0[0] + s * (v1[0] - v0[0]), v0[1] + s * (v1[1] - v0[1]), w, k, w0 + (w1 - w0) * u
        v = self.segs[-1][3]
        return v[0], v[1], v[2], None, 0.0

    def clamp(self, cx, cy, w):
        h = w * self.OH / self.OW
        cx = min(max(cx, w / 2), self.CW - w / 2)
        cy = min(max(cy, h / 2), self.CH - h / 2)
        return cx - w / 2, cy - h / 2, w, h


class Renderer:
    def __init__(self, L, scale=1.0):
        self.L = L
        self.OW, self.OH = int(round(L.OW * scale / 2) * 2), int(round(L.OH * scale / 2) * 2)
        self.crop = {}
        for k, v in L.win.items():  # cover-crop the 16:9 source into the window's aspect
            s = max(v["w"] / SRC_W, v["h"] / SRC_H)
            sw, sh = v["w"] / s, v["h"] / s
            self.crop[k] = ((SRC_W - sw) / 2, (SRC_H - sh) / 2, sw, sh)

    def bounds(self, k, vx, vy, m):
        """Where window k lands in the output frame: (ox0, oy0, ow, oh, X0, Y0, X1, Y1); empty if X1 <= X0 or Y1 <= Y0."""
        v = self.L.win[k]
        ox0, oy0, ow, oh = (v["x"] - vx) * m, (v["y"] - vy) * m, v["w"] * m, v["h"] * m
        X0, Y0 = max(int(math.floor(ox0)), 0), max(int(math.floor(oy0)), 0)
        X1, Y1 = min(int(math.ceil(ox0 + ow)), self.OW), min(int(math.ceil(oy0 + oh)), self.OH)
        return ox0, oy0, ow, oh, X0, Y0, X1, Y1

    def view(self, tt):
        """Camera at time tt: (vx, vy, vw, vh, m, focused window, focus weight)."""
        cx, cy, w, fk, fw = self.L.view_at(tt)
        vx, vy, vw, vh = self.L.clamp(cx, cy, w)
        return vx, vy, vw, vh, self.OW / vw, fk, fw

    def near(self, view, margin=0.15):
        """Windows that are in the view or within `margin` of a view height of it: the ones to keep decoding.
        The margin lets a window's decoder start a few frames before it scrolls into sight."""
        vx, vy, vw, vh = view[:4]
        mx, my = margin * vw, margin * vh
        return [k for k, v in self.L.win.items()
                if v["x"] < vx + vw + mx and v["x"] + v["w"] > vx - mx and v["y"] < vy + vh + my and v["y"] + v["h"] > vy - my]

    def paste(self, out, src, k, vx, vy, m, alpha=1.0, raised=False):
        v = self.L.win[k]
        sx, sy, sw, sh = self.crop[k]
        ox0, oy0, ow, oh, X0, Y0, X1, Y1 = self.bounds(k, vx, vy, m)
        if X1 <= X0 or Y1 <= Y0:
            return
        src = src(k)  # decode on demand: only windows that land in the frame are asked for
        if v["layer"] > 0 and not raised:  # soft shadow + dark frame for windows laid over others
            for r, a in ((34 * m, .18), (22 * m, .22), (12 * m, .30)):
                a0x, a0y = max(int(ox0 - r + 10 * m), 0), max(int(oy0 - r + 14 * m), 0)
                a1x, a1y = min(int(ox0 + ow + r + 10 * m), self.OW), min(int(oy0 + oh + r + 14 * m), self.OH)
                if a1x > a0x and a1y > a0y:
                    out[a0y:a1y, a0x:a1x] = (out[a0y:a1y, a0x:a1x] * (1 - a)).astype(np.uint8)
            b = 10 * m
            out[max(int(oy0 - b), 0):min(int(oy0 + oh + b), self.OH),
                max(int(ox0 - b), 0):min(int(ox0 + ow + b), self.OW)] = self.L.bg
        k_s = ow / sw
        img, ss = src, 1.0
        if k_s < 0.75:
            img, ss = cv2.resize(src, (SRC_W // 2, SRC_H // 2), interpolation=cv2.INTER_AREA), 0.5
        if k_s < 0.3:
            img, ss = cv2.resize(src, (SRC_W // 4, SRC_H // 4), interpolation=cv2.INTER_AREA), 0.25
        sc = k_s / ss
        A = np.float32([[sc, 0, ox0 - sx * k_s - X0], [0, sc, oy0 - sy * k_s - Y0]])
        roi = cv2.warpAffine(img, A, (X1 - X0, Y1 - Y0),
                             flags=cv2.INTER_CUBIC if sc > 1.05 else cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        if alpha >= 0.999:
            out[Y0:Y1, X0:X1] = roi
        else:
            out[Y0:Y1, X0:X1] = (out[Y0:Y1, X0:X1] * (1 - alpha) + roi * alpha).astype(np.uint8)

    def frame(self, frames, tt, view=None):
        """frames(k) returns window k's current source frame; it is called only for windows in the frame."""
        L = self.L
        vx, vy, vw, vh, m, fk, fw = view or self.view(tt)
        out = np.empty((self.OH, self.OW, 3), np.uint8)
        out[:] = L.bg
        for k in L.order:
            self.paste(out, frames, k, vx, vy, m)
        if fk and fw > 0 and any(L.win[o]["layer"] > L.win[fk]["layer"] for o in L.win):
            self.paste(out, frames, fk, vx, vy, m, alpha=fw, raised=True)  # focused window rises above overlaps
        vis, near = {}, {}
        for k, v in L.win.items():  # for the sound mix
            ix = max(0, min(v["x"] + v["w"], vx + vw) - max(v["x"], vx))
            iy = max(0, min(v["y"] + v["h"], vy + vh) - max(v["y"], vy))
            vis[k] = ix * iy / (v["w"] * v["h"])  # fraction of the window inside the view
            # 1 within half a screen of the view, fading to 0 a full screen away (other pages go quiet)
            dist = max(v["y"] - (vy + vh), vy - (v["y"] + v["h"]), 0)
            near[k] = min(max(2 - 2 * dist / L.VH, 0.0), 1.0)
        return out, fk, fw, vis, near


def smooth(x, n):
    """Moving average over n samples, identical to np.convolve(x, ones(n)/n, "same") but O(len(x))."""
    c = np.concatenate([[0.0], np.cumsum(np.pad(x.astype(np.float64), (n // 2, (n - 1) // 2)))])
    return ((c[n:] - c[:-n]) / n).astype(np.float32)


FB = SRC_W * SRC_H * 3


def frame_count(path):
    """Frames in one pass of a clip at FPS (loops from make_loop.py are already 24 fps)."""
    j = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                   "stream=r_frame_rate,nb_frames", "-of", "json", path],
                                  capture_output=True, text=True, check=True).stdout)["streams"][0]
    if j.get("r_frame_rate") == f"{FPS}/1" and j.get("nb_frames"):
        return int(j["nb_frames"])
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={FPS}", "-f", "null", "-", "-progress", "pipe:1"],
                       capture_output=True, text=True, check=True).stdout
    return int(re.findall(r"^frame=(\d+)", r, re.M)[-1])


class Loop:
    """One window's clip, decoded only while it is near the view. get(i) returns frame (i mod n), exactly the
    frame a reader looping the clip continuously since the start of the film would give, so a window that
    comes back into view is still in step. A background thread decodes a few frames ahead."""
    AHEAD, SKIP = 3, 12  # frames decoded ahead; gap read through (rather than reopened) when a window was paused

    def __init__(self, path):
        self.path, self.n = path, frame_count(path)
        self.proc = self.q = self.stop = None
        self.pos = 0  # clip frame the queue delivers next
        self.opened = 0  # decoder starts, for the summary

    def start(self, j):
        self.close()
        seek = ["-ss", f"{(j - 0.25) / FPS:.6f}"] if j else []  # accurate seek: first frame shown is frame j
        proc = subprocess.Popen(["ffmpeg", "-v", "error", *seek, "-i", self.path,
                                 "-vf", f"scale={SRC_W}:{SRC_H}:flags=lanczos,fps={FPS}",
                                 "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE, bufsize=FB)
        q, stop = queue.Queue(self.AHEAD), threading.Event()

        def pump():
            while not stop.is_set():
                b = proc.stdout.read(FB)
                item = b if len(b) == FB else None
                while not stop.is_set():
                    try:
                        q.put(item, timeout=0.1)
                        break
                    except queue.Full:
                        pass
                if item is None:
                    return

        threading.Thread(target=pump, daemon=True).start()
        self.proc, self.q, self.stop, self.pos = proc, q, stop, j
        self.opened += 1

    def get(self, i):
        j = i % self.n
        if self.q is None or not self.pos <= j <= self.pos + self.SKIP:
            self.start(j)
        while True:
            b = self.q.get()
            if b is None:
                raise RuntimeError(f"{self.path}: decoding stopped at frame {self.pos} of {self.n}")
            self.pos += 1
            if self.pos > j:
                break
        if self.pos == self.n:  # the next frame is frame 0 again: reopen from the start then
            self.close()
        return np.frombuffer(b, np.uint8).reshape(SRC_H, SRC_W, 3)

    def close(self):
        if self.proc:
            self.stop.set()
            self.proc.kill()
            self.proc.wait()
        self.proc = self.q = self.stop = None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("layout")
    ap.add_argument("out")
    ap.add_argument("--scale", type=float, default=1.0, help="output scale (0.25 for quick previews)")
    ap.add_argument("--seconds", type=float, default=None, help="render only the first N seconds")
    ap.add_argument("--stills", default=None, help="comma-separated times; writes PNGs into OUT folder instead")
    ap.add_argument("--crf", type=int, default=19)
    ap.add_argument("--preset", default="veryfast")
    a = ap.parse_args()

    L = Layout(a.layout)
    R = Renderer(L, a.scale)
    print(f"canvas {L.CW}x{int(L.CH)} ({L.CH / L.VH:.2f} screens), {len(L.win)} windows, film {L.duration:.1f} s")
    loops = {k: Loop(v["file"]) for k, v in L.win.items()}

    if a.stills:  # every window shows its first frame, whatever the time
        os.makedirs(a.out, exist_ok=True)
        first = {}

        def frame0(k):
            if k not in first:
                first[k] = loops[k].get(0)
                loops[k].close()
            return first[k]

        for tt in map(float, a.stills.split(",")):
            img, *_ = R.frame(frame0, tt)
            cv2.imwrite(os.path.join(a.out, f"still_{tt:06.1f}.png"), cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        return

    NF = int(round((a.seconds or L.duration) * FPS))
    tmp = tempfile.mkdtemp()
    vtmp = os.path.join(tmp, "v.mp4")
    enc = frame_writer(vtmp, R.OW, R.OH, crf=a.crf, preset=a.preset)
    gains = {k: np.empty(NF, np.float32) for k in L.win}
    t0, decoded = time.time(), 0
    for i in range(NF):
        view = R.view(i / FPS)
        cache = {}
        for k in R.near(view):  # keep near windows decoding even if not yet in the frame, so they start on time
            cache[k] = loops[k].get(i)
        for k, lp in loops.items():  # windows left behind stop decoding; they resume in step when they return
            if k not in cache and lp.proc and not lp.pos <= i % lp.n <= lp.pos + lp.SKIP:
                lp.close()
        decoded += len(cache)
        img, fk, fw, vis, near = R.frame(lambda k: cache[k] if k in cache else cache.setdefault(k, loops[k].get(i)),
                                         i / FPS, view)
        enc.stdin.write(img.tobytes())
        for k in L.win:
            g = 0.1 * near[k] + 0.9 * min(1.0, vis[k] * 1.5)
            if fk:
                g *= (1 + 1.6 * fw) if k == fk else (1 - 0.8 * fw)
            gains[k][i] = g
        if i % 240 == 0:
            print(f"frame {i}/{NF}", flush=True)
    enc.stdin.close(); enc.wait()
    for lp in loops.values():
        lp.close()
    print(f"decoded {decoded / max(NF, 1):.1f} of {len(L.win)} windows per frame on average, "
          f"{sum(lp.opened for lp in loops.values())} decoder starts, {time.time() - t0:.0f} s for the picture")

    N = int(NF / FPS * SR)
    spf = SR // FPS
    mix = np.zeros((N, 2), np.float32)
    for k, v in L.win.items():
        au = read_audio(v["file"])
        if not len(au):
            continue
        au = np.tile(au, (N // len(au) + 1, 1))[:N] * v["gain"]
        gs = np.repeat(gains[k], spf)[:N]
        gs = np.pad(gs, (0, N - len(gs)), mode="edge")
        gs = smooth(gs, 2400)  # smooth gain changes (50 ms)
        mix += au * gs[:, None]
    mix *= 1.6
    pk = np.abs(mix).max() if len(mix) else 0
    if pk > 30000:
        mix *= 30000 / pk
    wtmp = os.path.join(tmp, "a.wav")
    write_wav(wtmp, mix)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    mux(vtmp, wtmp, a.out, audio_bitrate="320k" if a.crf <= 15 else "192k")
    print(f"done: {a.out} ({NF / FPS:.1f} s, {R.OW}x{R.OH})")


if __name__ == "__main__":
    main()
