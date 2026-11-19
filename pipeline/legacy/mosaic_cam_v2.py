# Virtual-camera mosaic renderer: 9:16 canvas of looping windows, overlaps, zoom tour, focus-following audio.
import subprocess, numpy as np, cv2, wave, sys, json, math

OUT_W, OUT_H, FPS = 2160, 3840, 24
CW, CH = 2160, 3840            # canvas units (logical)
BG = np.array([0x13, 0x0e, 0x0b], np.uint8)[::-1]  # rgb of 0x0b0e13
G = 12

# name: (file, x, y, w, h, layer, audio_gain)
TILES = {
 "dinner":   ("dinner",      G,   G,             CW-2*G, 1263, 0, 1.0),
 "cat":      ("shot02_cat",  G,   1287,          1062,   627,  0, 1.0),
 "cafe":     ("cafe_v3",     G,   1926,          CW-2*G, 1263, 0, 1.0),
 "highrise": ("highrise",    G,   3201,          1062,   627,  0, 1.0),
 "terrace":  ("shot01",      848, 1914-731,      1300,   731,  1, 0.35),
 "dog":      ("dog",         CW-G-1360, CH-G-765, 1360,  765,  1, 1.0),
}
ORDER = sorted(TILES, key=lambda k: TILES[k][5])

# focus framing: (center_x, center_y, camera_width) in canvas units
def tile_focus(k, fill=0.94):
    f, x, y, w, h, *_ = TILES[k]
    return (x + w/2, y + h/2, w/fill)
# action point (fraction of tile width/height) and camera width as a fraction of tile width
ACTION = {"dinner":(0.47,0.42,0.50), "cat":(0.66,0.62,0.52), "cafe":(0.60,0.52,0.52),
          "highrise":(0.42,0.60,0.62), "dog":(0.50,0.64,0.54), "terrace":(0.62,0.55,0.72)}
FOCUS = {}
for k,(fx,fy,zw) in ACTION.items():
    f, x, y, w, h, *_ = TILES[k]; FOCUS[k] = (x+fx*w, y+fy*h, zw*w)
FULL = (CW/2, CH/2, CW)

TOUR = sys.argv[1].split(",") if len(sys.argv) > 1 else ["dinner","cat","cafe","highrise","dog","terrace"]
T_FULL0, T_IN, T_HOLD, T_OUT, T_GAP, T_END = 10.0, 1.3, 5.0, 1.3, 0.8, 3.0

# keyframe timeline: list of (t_start, t_end, from_view, to_view, focus_name_for_audio_weight_fn)
segs = []; t = 0.0
segs.append((t, t+T_FULL0, FULL, FULL, None, 0, 0)); t += T_FULL0
for i, k in enumerate(TOUR):
    segs.append((t, t+T_IN,  FULL, FOCUS[k], k, 0, 1)); t += T_IN
    segs.append((t, t+T_HOLD, FOCUS[k], FOCUS[k], k, 1, 1)); t += T_HOLD
    segs.append((t, t+T_OUT, FOCUS[k], FULL, k, 1, 0)); t += T_OUT
    if i < len(TOUR)-1:
        segs.append((t, t+T_GAP, FULL, FULL, None, 0, 0)); t += T_GAP
segs.append((t, t+T_END, FULL, FULL, None, 0, 0)); t += T_END
DUR = t; NF = int(round(DUR*FPS))
if len(sys.argv) > 2: NF = min(NF, int(sys.argv[2]))   # optional frame limit for tests

def ease(u): return 0.5 - 0.5*math.cos(math.pi*min(max(u,0),1))

def view_at(tt):
    for (a, b, v0, v1, k, w0, w1) in segs:
        if tt < b or (a, b) == segs[-1][:2]:
            u = ease((tt-a)/(b-a))
            # interpolate width geometrically, centre so the zoom feels natural
            w = math.exp((1-u)*math.log(v0[2]) + u*math.log(v1[2]))
            # centre interpolation weighted by zoom progress (keeps focal point steady)
            s = (v0[2]-w)/(v0[2]-v1[2]) if abs(v0[2]-v1[2]) > 1e-6 else u
            cx = v0[0] + s*(v1[0]-v0[0]); cy = v0[1] + s*(v1[1]-v0[1])
            return cx, cy, w, k, w0 + (w1-w0)*u
    return FULL[0], FULL[1], FULL[2], None, 0

def clamp_view(cx, cy, w):
    h = w*OUT_H/OUT_W
    cx = min(max(cx, w/2), CW-w/2); cy = min(max(cy, h/2), CH-h/2)
    return cx-w/2, cy-h/2, w, h

# source crop (cover) for each tile
SRC_W, SRC_H = 1920, 1080
def cover(w, h):
    s = max(w/SRC_W, h/SRC_H); sw, sh = w/s, h/s
    return ((SRC_W-sw)/2, (SRC_H-sh)/2, sw, sh)
CROP = {k: cover(TILES[k][3], TILES[k][4]) for k in TILES}

def reader(f):
    return subprocess.Popen(["ffmpeg","-v","error","-stream_loop","-1","-i",f"{f}_loop_16x9.mp4",
        "-f","rawvideo","-pix_fmt","rgb24","-"], stdout=subprocess.PIPE, bufsize=10**8)
R = {k: reader(TILES[k][0]) for k in TILES}
FB = SRC_W*SRC_H*3

def paste(out, src, k, vx, vy, m, alpha=1.0, raise_=False):
    f, x, y, w, h, layer, _ = TILES[k]
    sx, sy, sw, sh = CROP[k]
    # tile rect in output px
    ox0, oy0 = (x-vx)*m, (y-vy)*m; ow, oh = w*m, h*m
    X0, Y0 = max(int(math.floor(ox0)),0), max(int(math.floor(oy0)),0)
    X1, Y1 = min(int(math.ceil(ox0+ow)),OUT_W), min(int(math.ceil(oy0+oh)),OUT_H)
    if X1 <= X0 or Y1 <= Y0: return
    if layer == 1 and not raise_:   # frame + soft shadow for overlapping windows
        for r, a in ((34*m, .18), (22*m, .22), (12*m, .30)):
            a0x, a0y = max(int(ox0-r+10*m),0), max(int(oy0-r+14*m),0)
            a1x, a1y = min(int(ox0+ow+r+10*m),OUT_W), min(int(oy0+oh+r+14*m),OUT_H)
            if a1x > a0x and a1y > a0y: out[a0y:a1y, a0x:a1x] = (out[a0y:a1y, a0x:a1x]*(1-a)).astype(np.uint8)
        b = 10*m
        b0x, b0y = max(int(ox0-b),0), max(int(oy0-b),0); b1x, b1y = min(int(ox0+ow+b),OUT_W), min(int(oy0+oh+b),OUT_H)
        out[b0y:b1y, b0x:b1x] = BG
    k_s = ow/sw   # source px -> output px
    img, ss = src, 1.0
    if k_s < 0.75:
        img = cv2.resize(src, (SRC_W//2, SRC_H//2), interpolation=cv2.INTER_AREA); ss = 0.5
    sc = k_s/ss
    A = np.float32([[sc, 0, ox0 - sx*k_s - X0], [0, sc, oy0 - sy*k_s - Y0]])
    roi = cv2.warpAffine(img, A, (X1-X0, Y1-Y0), flags=cv2.INTER_CUBIC if sc > 1.05 else cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    if alpha >= 0.999: out[Y0:Y1, X0:X1] = roi
    else: out[Y0:Y1, X0:X1] = (out[Y0:Y1, X0:X1].astype(np.float32)*(1-alpha) + roi.astype(np.float32)*alpha).astype(np.uint8)

import os
if os.environ.get("STILLS"):
    frames = {k: np.frombuffer(R[k].stdout.read(FB), np.uint8).reshape(SRC_H, SRC_W, 3) for k in TILES}
    for tt in map(float, os.environ["STILLS"].split(",")):
        cx, cy, w, fk, fw = view_at(tt); vx, vy, vw, vh = clamp_view(cx, cy, w); m = OUT_W/vw
        out = np.empty((OUT_H, OUT_W, 3), np.uint8); out[:] = BG
        for k in ORDER: paste(out, frames[k], k, vx, vy, m)
        if fk and TILES[fk][5]==0 and fw>0: paste(out, frames[fk], fk, vx, vy, m, alpha=fw, raise_=True)
        cv2.imwrite(f"frames/still_{tt:05.1f}.png", cv2.cvtColor(cv2.resize(out, (540, 960), interpolation=cv2.INTER_AREA), cv2.COLOR_RGB2BGR))
    print("total duration", DUR); [r.kill() for r in R.values()]; sys.exit()

enc = subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{OUT_W}x{OUT_H}","-r",str(FPS),"-i","-",
    "-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p","-movflags","+faststart","mosaic_cam_video.mp4"], stdin=subprocess.PIPE)
weights = []
for i in range(NF):
    tt = i/FPS
    cx, cy, w, fk, fw = view_at(tt)
    vx, vy, vw, vh = clamp_view(cx, cy, w)
    m = OUT_W/vw
    frames = {k: np.frombuffer(R[k].stdout.read(FB), np.uint8).reshape(SRC_H, SRC_W, 3) for k in TILES}
    out = np.empty((OUT_H, OUT_W, 3), np.uint8); out[:] = BG
    for k in ORDER: paste(out, frames[k], k, vx, vy, m)
    if fk and TILES[fk][5]==0 and fw>0: paste(out, frames[fk], fk, vx, vy, m, alpha=fw, raise_=True)
    enc.stdin.write(out.tobytes())
    weights.append((fk, fw))
    if i % 120 == 0: print(f"frame {i}/{NF}", flush=True)
enc.stdin.close(); enc.wait()
for r in R.values(): r.kill()

# ---- audio: loop each window's sound, raise the focused one, lower the rest
SR = 48000; N = int(NF/FPS*SR)
mix = np.zeros((N, 2), np.float32)
spf = SR//FPS
for k in TILES:
    wv = wave.open(f"{TILES[k][0]}_a.wav"); a = np.frombuffer(wv.readframes(wv.getnframes()), np.int16).reshape(-1,2).astype(np.float32); wv.close()
    a = np.tile(a, (N//len(a)+1, 1))[:N] * TILES[k][6]
    g = np.empty(NF, np.float32)
    for i, (fk, fw) in enumerate(weights):
        g[i] = 1.0 if fk is None else (1.0 + 1.6*fw if fk == k else 1.0 - 0.8*fw)
    gs = np.repeat(g, spf)[:N]; gs = np.pad(gs, (0, N-len(gs)), mode="edge")
    gs = np.convolve(gs, np.ones(2400)/2400, mode="same")   # smooth gain changes
    mix += a * gs[:, None]
mix *= 1.6
pk = np.abs(mix).max()
if pk > 30000: mix *= 30000/pk
o = wave.open("mosaic_cam_audio.wav", "wb"); o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR)
o.writeframes(mix.astype(np.int16).tobytes()); o.close()
subprocess.run(["ffmpeg","-v","error","-y","-i","mosaic_cam_video.mp4","-i","mosaic_cam_audio.wav","-map","0:v","-map","1:a",
    "-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart","mosaic_tour_9x16_4k.mp4"])
print("done", round(NF/FPS,1), "seconds")
