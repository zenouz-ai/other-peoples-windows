"""Generate stills and video takes for windows in scenes/scenes.yaml through the Gemini, Kling, OpenAI and
Alibaba Cloud (Wan) APIs, and measure them for the scorecard.

Every paid command prints the exact plan and its estimated cost first, refuses to go over the run and batch
budgets in pipeline/generate.yaml, and then asks before spending (or needs --yes when not run from a terminal).
--dry-run stops after the estimate. Every paid call is logged, with its actual cost, in the spend ledger.

Usage (from the project root):
  python pipeline/generate.py still 45 23 --dry-run      # plan: 4 candidate stills each, prompts from scenes.yaml
  python pipeline/generate.py still 45 -n 2              # make 2 candidates into media/stills/45/
  python pipeline/generate.py still 45 --engine kling    # Kling Image 3.0 candidates (k1.jpg, ...) instead of Gemini (c1.jpg, ...)
  python pipeline/generate.py still 45 --engine openai   # GPT Image candidates (o1.jpg, ...)
  python pipeline/generate.py import 45 media/inbox/*.png  # hand-made Midjourney stills -> media/stills/45/m1.jpg, ...
  python pipeline/generate.py import 45 ~/Downloads/x.mp4  # Midjourney video -> media/inbox/45-..._mj-take1.mp4, then check
  python pipeline/generate.py edit media/stills/45/c2.jpg "Turn the woman's face away from the window."
                                                         # o*.jpg are edited with GPT Image, everything else with Gemini
  python pipeline/generate.py review 45 23               # contact sheet (media/review.html) and docs/<batch>-scorecard.md
  python pipeline/generate.py pick 45 media/stills/45/c2-e1.jpg     # becomes media/stills/45-village-pub-by-the-fire.jpg
  python pipeline/generate.py video 45 44 --dry-run      # one take each from the picked stills, model from scenes.yaml
  python pipeline/generate.py video 22 --engine kling,wan   # one take on each of two models (also: omni)
  python pipeline/generate.py check media/inbox/45-*.mp4 # checksum, size, first frame against the still, sound, drift, wobble
  python pipeline/generate.py fetch kling TASK_ID media/inbox/x.mp4   # recover a finished take whose download failed
  python pipeline/generate.py spend                       # what the ledger says has been spent

Keys come from .env (git-ignored): GEMINI_API_KEY, KLING_API_KEY, OPENAI_API_KEY, DASHSCOPE_API_KEY and
DASHSCOPE_WORKSPACE (other accepted names in generate.yaml).
"""
import argparse
import base64
import concurrent.futures as cf
import glob
import hashlib
import html
import json
import os
import re
import shutil
import ssl
import threading
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone

import numpy as np
import yaml

try:  # python.org builds of Python on macOS ship without root certificates
    import certifi
    TLS = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    TLS = ssl.create_default_context()

sys.path.insert(0, os.path.dirname(__file__))
from prompts import build, load  # noqa: E402

CONFIG = "pipeline/generate.yaml"
STILLS, INBOX, RAW = "media/stills", "media/inbox", "media/raw"
MEASURED = "media/measurements.json"  # check results per clip checksum, so review does not measure twice
VIDEO_ENGINES = {"omni": "Veo", "kling": "Kling", "wan": "Wan"}  # --engine name -> video section of generate.yaml
TAKE_TAGS = {"gemini": "omni", "kling": "kling4", "wan": "wan3"}  # engine -> take file tag
STILL_MODELS = {"c": "Gemini 3 Pro Image", "k": "Kling Image 3.0", "o": "GPT Image", "m": "Midjourney"}


# ---------------------------------------------------------------- plumbing

def load_env(path=".env"):
    """Read KEY=VALUE lines from .env into os.environ (values never printed)."""
    if not os.path.exists(path):
        return
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.removeprefix("export ").split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip("'\""))


def key(names):
    """The first of `names` (a name or a list of accepted names) that is set in the environment or .env."""
    names = [names] if isinstance(names, str) else names
    v = next((os.environ[n] for n in names if os.environ.get(n)), None)
    if not v:
        sys.exit(f"{' or '.join(names)} is not set: add it to .env (never paste keys into chat)")
    return v


def http(method, url, headers=None, body=None, timeout=120, retries=0, raw=False, retry_network=True):
    """JSON (or raw bytes) over HTTPS. Retries only 429/5xx and (unless retry_network is False, for paid calls that
    may have gone through) network errors, with back-off. GETs carry no Content-Type, which signed download URLs
    (Alibaba Cloud OSS) include in their signature."""
    data = json.dumps(body).encode() if body is not None else None
    hdrs = {**({"Content-Type": "application/json"} if data is not None else {}), **(headers or {})}
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, data, hdrs, method=method), timeout=timeout, context=TLS) as r:
                out = r.read()
                return out if raw else json.loads(out or b"{}")
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")[:800]
            if e.code in (429, 500, 502, 503, 504) and attempt < retries:
                time.sleep(10 * 2 ** attempt)
                continue
            raise RuntimeError(f"HTTP {e.code} from {url.split('?')[0]}: {msg}") from None
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < retries and retry_network:
                time.sleep(10 * 2 ** attempt)
                continue
            raise RuntimeError(f"network error for {url.split('?')[0]}: {e}") from None


def b64(path):
    return base64.b64encode(open(path, "rb").read()).decode()


def mime(path):
    return "image/png" if path.lower().endswith(".png") else "image/jpeg"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def window(d, ref):
    ref = os.path.basename(ref.rstrip("/"))
    w = next((w for w in d["windows"] if w["id"] == ref or w["id"].startswith(ref.zfill(2) + "-")), None)
    if not w or "scene" not in w:
        sys.exit(f"no prompts for window {ref}")
    return w


def num(w):
    return w["id"][:2]


def engine_for(cfg, w, engine="auto"):
    """Video section for a window: from its `model` in scenes.yaml (auto), or the --engine named."""
    m = w["model"].lower()
    auto = "Kling" if "kling" in m else "Wan" if "wan" in m else "Veo"
    family = auto if engine == "auto" else VIDEO_ENGINES[engine]
    return family, cfg["video"][family]


# ---------------------------------------------------------------- ledger and guard rails

def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def log(cfg, **rec):
    os.makedirs(os.path.dirname(cfg["ledger"]), exist_ok=True)
    with open(cfg["ledger"], "a") as f:
        f.write(json.dumps({"time": now(), "batch": cfg["batch"], **rec}) + "\n")


def ledger(cfg):
    """Latest record per call. A call costs its actual figure once known, otherwise its estimate."""
    calls = {}
    if os.path.exists(cfg["ledger"]):
        for line in open(cfg["ledger"]):
            r = json.loads(line)
            calls.setdefault(r["call"], {}).update(r)
    return calls


def spent(cfg, batch=None):
    return sum(c.get("usd_actual", c["usd_est"]) for c in ledger(cfg).values() if batch in (None, c.get("batch")))


def approve(cfg, plan, a):
    """plan: [(description, usd)]. Print it, enforce both budgets, then ask (or require --yes)."""
    total = sum(u for _, u in plan)
    batch_spent = spent(cfg, cfg["batch"])
    print("\nPlanned paid calls:")
    for desc, usd in plan:
        print(f"  ${usd:6.3f}  {desc}")
    print(f"  -------\n  ${total:6.3f}  total (run budget ${a.budget:.2f}; {cfg['batch']} so far ${batch_spent:.2f} "
          f"of ${cfg['batch_budget_usd']:.2f})")
    if a.dry_run:
        print("dry run: nothing spent")
        sys.exit(0)
    if total > a.budget:
        sys.exit(f"over the run budget (${total:.2f} > ${a.budget:.2f}): plan less or pass --budget")
    if batch_spent + total > cfg["batch_budget_usd"]:
        sys.exit(f"over the batch budget: raise batch_budget_usd in {CONFIG} only with Kayvan's agreement")
    if not a.yes:
        if not sys.stdin.isatty():
            sys.exit("not a terminal: rerun with --yes once Kayvan has approved this spend")
        if input(f"Spend about ${total:.2f}? [y/N] ").strip().lower() != "y":
            sys.exit("cancelled")


# ---------------------------------------------------------------- Gemini (Interactions API)

def gemini_headers(cfg):
    g = cfg["gemini"]
    return {"x-goog-api-key": key(g["key_env"]), "Api-Revision": g["api_revision"]}


def output_of(resp, kind):
    """The image or video block of an interaction (convenience field, else the last model_output step)."""
    if resp.get(f"output_{kind}"):
        return resp[f"output_{kind}"]
    found = None
    for step in resp.get("steps", []):
        if step.get("type") == "model_output":
            for c in step.get("content", []):
                if c.get("type") == kind:
                    found = c
    if not found:
        text = " ".join(c.get("text", "") for s in resp.get("steps", []) for c in s.get("content", []) if isinstance(c, dict))
        raise RuntimeError(f"no {kind} in the response (status {resp.get('status')}): {text[:400]}")
    return found


def gemini_image(cfg, inputs, out, label):
    """One paid image call. inputs: Interactions API input blocks. Saves a JPEG to `out`."""
    im = cfg["image"]
    call = uuid.uuid4().hex[:12]
    log(cfg, call=call, kind="image", model=im["model"], window=label, usd_est=im["usd_per_image"], status="submitted")
    body = {"model": im["model"], "input": inputs,
            "response_format": {"type": "image", "mime_type": "image/jpeg", "aspect_ratio": im["aspect_ratio"],
                                "image_size": im["size"]}}
    try:
        r = http("POST", f"{cfg['gemini']['base']}/interactions", gemini_headers(cfg), body, timeout=300, retries=2)
        img = output_of(r, "image")
        with open(out, "wb") as f:
            f.write(base64.b64decode(img["data"]))
    except Exception as e:  # no image came back, so nothing to pay for
        log(cfg, call=call, status="failed", error=str(e)[:300], usd_actual=0)
        raise
    log(cfg, call=call, status="done", file=out, usd_actual=im["usd_per_image"], interaction=r.get("id"),
        usage=r.get("usage"))
    return out


def gemini_video(cfg, v, w, still, prompt, seconds, end_on_still, out):
    call = uuid.uuid4().hex[:12]
    est = seconds * v["usd_per_second"]
    log(cfg, call=call, kind="video", model=v["model"], window=w["id"], usd_est=est, status="submitted", out=out)
    img = {"type": "image", "data": b64(still), "mime_type": mime(still)}
    inputs = [img, img, {"type": "text", "text": prompt}] if end_on_still else [img, {"type": "text", "text": prompt}]
    body = {"model": v["model"], "input": inputs,
            "response_format": {"type": "video", "resolution": v["resolution"], "aspect_ratio": v["aspect_ratio"],
                                "duration": f"{seconds}s", "delivery": "uri"}}
    hdr = gemini_headers(cfg)
    base = cfg["gemini"]["base"]
    r = None
    try:
        r = http("POST", f"{base}/interactions", hdr, body, timeout=1800)
        log(cfg, call=call, status="generated", interaction=r.get("id"), usage=r.get("usage"))
        vid = output_of(r, "video")
        if vid.get("data"):
            data = base64.b64decode(vid["data"])
        else:
            fid = re.search(r"files/([^/:?]+)", vid["uri"]).group(1)
            for _ in range(120):
                state = http("GET", f"{base}/files/{fid}", hdr, retries=3).get("state")
                if state == "ACTIVE":
                    break
                if state == "FAILED":
                    raise RuntimeError("Gemini file processing failed")
                time.sleep(5)
            data = http("GET", f"{base}/files/{fid}:download?alt=media", hdr, timeout=600, retries=3, raw=True)
        with open(out, "wb") as f:
            f.write(data)
    except Exception as e:  # billed only if the video was generated (then recover it with `fetch gemini`)
        log(cfg, call=call, status="failed", error=str(e)[:300], **({} if r else {"usd_actual": 0}))
        raise
    u = r.get("usage") or {}
    actual = (u.get("total_output_tokens", 0) * v["usd_per_million_output"]
              + u.get("total_input_tokens", 0) * v["usd_per_million_input"]) / 1e6
    log(cfg, call=call, status="done", file=out, **({"usd_actual": round(actual, 4)} if u else {}))
    return out


# ---------------------------------------------------------------- Kling

def kling_headers(cfg):
    return {"Authorization": f"Bearer {key(cfg['kling']['key_env'])}"}


def kling_wait(cfg, task, out, timeout=1800):
    """Poll a Kling task until it finishes, then download its video. Returns the task record."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        r = http("GET", f"{cfg['kling']['base']}/tasks?task_ids={task}", kling_headers(cfg), retries=3)
        rec = (r.get("data") or [{}])[0]
        if rec.get("status") == "succeeded":
            url = next(o["url"] for o in rec.get("outputs", []) if o.get("type") == "video")
            with open(out, "wb") as f:
                f.write(http("GET", url, timeout=600, retries=3, raw=True))
            return rec
        if rec.get("status") == "failed":
            raise RuntimeError(f"Kling task {task} failed: {rec.get('message')}")
        time.sleep(15)
    raise RuntimeError(f"Kling task {task} still running after {timeout} s; recover it later with: fetch kling {task} {out}")


def kling_video(cfg, v, w, still, prompt, seconds, end_on_still, out):
    call = uuid.uuid4().hex[:12]
    est = seconds * v["units_per_second"] * v["usd_per_unit"]
    log(cfg, call=call, kind="video", model=v["endpoint"], window=w["id"], usd_est=est, status="submitted", out=out)
    frame = b64(still)
    contents = [{"type": "prompt", "text": prompt}, {"type": "first_frame", "url": frame, "id": "image_1"}]
    if end_on_still:
        contents.append({"type": "last_frame", "url": frame, "id": "image_2"})
    body = {"contents": contents,
            "settings": {"resolution": v["resolution"], "aspect_ratio": v["aspect_ratio"], "duration": seconds,
                         "audio": v["audio"]},
            "options": {"external_task_id": f"{w['id']}-{call}", "watermark_info": {"enabled": False}}}
    try:
        r = http("POST", cfg["kling"]["base"] + v["endpoint"], kling_headers(cfg), body, timeout=120)
        if r.get("code") != 0:
            raise RuntimeError(f"Kling refused the task: {r.get('code')} {r.get('message')}")
        task = r["data"]["id"]
        log(cfg, call=call, status="generating", task=task)
        rec = kling_wait(cfg, task, out)
    except Exception as e:  # refused or failed tasks are not billed; a timeout or failed download is
        unbilled = "refused" in str(e) or "HTTP" in str(e)[:9] or re.search(r"task \S+ failed", str(e))
        log(cfg, call=call, status="failed", error=str(e)[:300], **({"usd_actual": 0} if unbilled else {}))
        raise
    dur = (rec.get("usage") or {}).get("output_duration")
    actual = float(dur) * v["units_per_second"] * v["usd_per_unit"] if dur else None
    log(cfg, call=call, status="done", file=out, **({"usd_actual": round(actual, 4)} if actual else {}))
    return out


# ---------------------------------------------------------------- OpenAI (GPT Image)

def openai_headers(cfg):
    return {"Authorization": f"Bearer {key(cfg['openai']['key_env'])}"}


def openai_size(o):
    """The configured 16:9 size for models documented to take custom sizes, otherwise the standard fallback."""
    native = any(o["model"] == m or o["model"].startswith(m + "-20") for m in o["custom_sizes"])
    return o["size"] if native else o["fallback_size"]


def openai_cost(o, usage):
    """Actual cost from the token usage an Image API response returns, or None without usage."""
    if not usage:
        return None
    p, det = o["usd_per_million"], usage.get("input_tokens_details") or {}
    image_in = det.get("image_tokens", 0)
    text_in = det.get("text_tokens", usage.get("input_tokens", 0) - image_in)
    return (text_in * p["text_input"] + image_in * p["image_input"] + usage.get("output_tokens", 0) * p["image_output"]) / 1e6


def save_169(data, out, quality=95):
    """Save image bytes as a 16:9 JPEG: written as they are when already a 16:9 JPEG, else centre-cropped and encoded.
    Returns (width, height) of the saved image."""
    import cv2
    import numpy as np
    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise RuntimeError("the image could not be decoded")
    h, w = img.shape[:2]
    if abs(w / h - 16 / 9) < 0.01 and data[:2] == b"\xff\xd8":
        with open(out, "wb") as f:
            f.write(data)
        return w, h
    if w / h > 16 / 9:
        cw, ch = int(round(h * 16 / 9)), h
    else:
        cw, ch = w, int(round(w * 9 / 16))
    x0, y0 = (w - cw) // 2, (h - ch) // 2
    cv2.imwrite(out, img[y0:y0 + ch, x0:x0 + cw], [cv2.IMWRITE_JPEG_QUALITY, quality])
    return cw, ch


def openai_image(cfg, prompt, outs, label, gate, image=None):
    """One paid GPT Image call returning len(outs) images: generate, or edit `image` when given. Saves 16:9 JPEGs.
    `gate` keeps one call in flight at a time (new OpenAI organisations have low image rate limits)."""
    o = cfg["openai_image"]
    call = uuid.uuid4().hex[:12]
    log(cfg, call=call, kind="image", model=o["model"], window=label, usd_est=len(outs) * o["usd_per_image"],
        status="submitted")
    body = {"model": o["model"], "prompt": prompt, "n": len(outs), "size": openai_size(o), "quality": o["quality"],
            "output_format": o["output_format"], "output_compression": o["output_compression"]}
    endpoint = "/images/generations"
    if image:
        body["images"] = [{"image_url": f"data:{mime(image)};base64,{b64(image)}"}]
        endpoint = "/images/edits"
    try:
        with gate:
            r = http("POST", cfg["openai"]["base"] + endpoint, openai_headers(cfg), body, timeout=900, retries=2,
                     retry_network=False)
        imgs = [x["b64_json"] for x in r.get("data") or [] if x.get("b64_json")]
        if not imgs:
            raise RuntimeError(f"no image in the response: {json.dumps(r)[:300]}")
        saved = []
        for data, out in zip(imgs, outs):
            save_169(base64.b64decode(data), out)
            saved.append(out)
    except Exception as e:  # nothing came back, so nothing to pay for
        log(cfg, call=call, status="failed", error=str(e)[:300], usd_actual=0)
        raise
    actual = openai_cost(o, r.get("usage"))
    log(cfg, call=call, status="done", file=",".join(saved), usage=r.get("usage"), size=r.get("size"),
        quality=r.get("quality"), **({"usd_actual": round(actual, 4)} if actual is not None else {}))
    return ", ".join(saved)


# ---------------------------------------------------------------- Alibaba Cloud Model Studio (Wan 3.0)

def wan_base(cfg):
    ds = cfg["dashscope"]
    return ds["base"].format(workspace=key(ds["workspace_env"])) if "{workspace}" in ds["base"] else ds["base"]


def wan_headers(cfg):
    return {"Authorization": f"Bearer {key(cfg['dashscope']['key_env'])}"}


def wan_wait(cfg, task, out, timeout=1800):
    """Poll a Model Studio task about every 15 s until it finishes, then download its video at once (the URL
    expires after 24 hours). Returns the task record."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        r = http("GET", f"{wan_base(cfg)}/tasks/{task}", wan_headers(cfg), retries=3)
        o = r.get("output") or {}
        status = o.get("task_status")
        if status == "SUCCEEDED":
            with open(out, "wb") as f:
                f.write(http("GET", o["video_url"], timeout=600, retries=3, raw=True))
            return r
        if status in ("FAILED", "CANCELED", "UNKNOWN"):
            raise RuntimeError(f"Wan task {task} {status.lower()}: {o.get('code') or r.get('code')} "
                               f"{o.get('message') or r.get('message')}")
        time.sleep(15)
    raise RuntimeError(f"Wan task {task} still running after {timeout} s; recover it within 24 hours with: "
                       f"fetch wan {task} {out}")


def wan_video(cfg, v, w, still, prompt, seconds, end_on_still, out):
    call = uuid.uuid4().hex[:12]
    log(cfg, call=call, kind="video", model=v["model"], window=w["id"], usd_est=seconds * v["usd_per_second"],
        status="submitted", out=out)
    body = {"model": v["model"],
            "input": {"prompt": prompt, "media": [{"type": "first_frame", "url": f"data:{mime(still)};base64,{b64(still)}"}]},
            "parameters": {"resolution": v["resolution"], "ratio": v["ratio"], "duration": seconds, "audio": v["audio"],
                           "watermark": v["watermark"], "prompt_extend": v["prompt_extend"]}}
    try:
        r = http("POST", f"{wan_base(cfg)}/services/aigc/video-generation/video-synthesis",
                 {**wan_headers(cfg), "X-DashScope-Async": "enable"}, body, timeout=120)
        task = (r.get("output") or {}).get("task_id")
        if not task:
            raise RuntimeError(f"Wan refused the task: {r.get('code')} {r.get('message')}")
        log(cfg, call=call, status="generating", task=task)
        rec = wan_wait(cfg, task, out)
    except Exception as e:  # refused or failed tasks are not billed; a timeout or failed download is
        unbilled = "refused" in str(e) or str(e).startswith("HTTP") or re.search(r"task \S+ (failed|canceled|unknown)", str(e))
        log(cfg, call=call, status="failed", error=str(e)[:300], **({"usd_actual": 0} if unbilled else {}))
        raise
    u = rec.get("usage") or {}
    dur = u.get("output_video_duration") or u.get("duration")
    log(cfg, call=call, status="done", file=out, usage=u,
        **({"usd_actual": round(float(dur) * v["usd_per_second"], 4)} if dur else {}))
    return out


# ---------------------------------------------------------------- checks

def frame_at(path, t=0.0, size=(960, 540)):
    """One frame of a clip as BGR at `size`; t < 0 counts from the end."""
    import numpy as np
    seek = ["-sseof", str(t)] if t < 0 else ["-ss", str(t)]
    raw = subprocess.run(["ffmpeg", "-v", "error", *seek, "-i", path, "-frames:v", "1", "-vf",
                          f"scale={size[0]}:{size[1]}", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw[:size[0] * size[1] * 3], np.uint8).reshape(size[1], size[0], 3)


def still_vs_take(path, still, sheet=None):
    """Compare a take's first frame with the still it was made from.
    zoom/stretch/shift: the affine fit from the still to the first frame (ORB features, RANSAC), at 1080p; Kling
    squeezes a 2K Gemini still to 16:9 (stretch under 1%), Omni has reframed and recast. redraw: median colour change of
    20 px patches (at 960x540) after alignment (Lab units); about 1.5 when the still is kept as the first frame, higher when the
    model has repainted it. A recast face is too small to measure reliably (the Omni take of 45 scored like the
    faithful Kling take), so `sheet` writes still, first frame, change map and last frame side by side for a look."""
    import cv2
    import numpy as np
    s = cv2.resize(cv2.imread(still), (960, 540), interpolation=cv2.INTER_AREA)
    f = frame_at(path)
    gs, gf = (cv2.cvtColor(x, cv2.COLOR_BGR2GRAY) for x in (s, f))
    cv2.setRNGSeed(0)
    orb = cv2.ORB_create(4000)
    k0, d0 = orb.detectAndCompute(gs, None)
    k1, d1 = orb.detectAndCompute(gf, None)
    M = None
    if d0 is not None and d1 is not None:
        m = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(d0, d1)
        if len(m) >= 12:
            M, _ = cv2.estimateAffine2D(np.float32([k0[x.queryIdx].pt for x in m]), np.float32([k1[x.trainIdx].pt for x in m]),
                                        method=cv2.RANSAC, ransacReprojThreshold=1.5)
    if M is None:
        return {"matched": False}
    sx, sy = np.hypot(M[0, 0], M[1, 0]), np.hypot(M[0, 1], M[1, 1])
    centre = M @ np.float32([480, 270, 1]) - np.float32([480, 270])
    fw = cv2.warpAffine(f, cv2.invertAffineTransform(M), (960, 540), borderMode=cv2.BORDER_REPLICATE)
    P = 20
    a, b = (cv2.cvtColor(x, cv2.COLOR_BGR2LAB).astype(np.float32).reshape(540 // P, P, 960 // P, P, 3).mean((1, 3))
            for x in (s, fw))
    change = np.sqrt(((a - b) ** 2).sum(-1))
    out = {"matched": True, "zoom": float(100 * ((sx + sy) / 2 - 1)), "stretch": float(100 * (sx / sy - 1)),
           "shift": float(2 * np.hypot(*centre)), "redraw": float(np.median(change))}
    out["reframed"] = abs(out["zoom"]) > 1.5 or out["shift"] > 20 or abs(out["stretch"]) > 2
    if sheet:
        heat = cv2.applyColorMap(cv2.resize((np.clip(change / 20, 0, 1) * 255).astype(np.uint8), (960, 540),
                                            interpolation=cv2.INTER_NEAREST), cv2.COLORMAP_INFERNO)
        heat = cv2.addWeighted(s, 0.5, heat, 0.5, 0)
        grid = np.vstack([np.hstack([s, f]), np.hstack([heat, frame_at(path, -0.1)])])
        for (x, y), label in zip([(12, 30), (972, 30), (12, 570), (972, 570)],
                                 ["still", "take: first frame", "change after alignment", "take: last frame"]):
            cv2.putText(grid, label, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
        os.makedirs(os.path.dirname(sheet), exist_ok=True)
        cv2.imwrite(sheet, grid, [cv2.IMWRITE_JPEG_QUALITY, 88])
        out["sheet"] = sheet
    return out


def still_for(path):
    """The picked still a take was made from: media/stills/<window id>.jpg, from the file name's window number."""
    m = re.match(r"(\d\d)-", os.path.basename(path))
    hits = glob.glob(f"{STILLS}/{m.group(1)}-*.jpg") if m else []
    hits = [h for h in hits if re.fullmatch(r"\d\d-[a-z0-9-]+\.jpg", os.path.basename(h))]
    return hits[0] if len(hits) == 1 else None


_sound_model = None


def measure(path):
    """Everything check and review report about one clip, cached by checksum in media/measurements.json."""
    global _sound_model
    digest = sha256(path)
    cache = json.load(open(MEASURED)) if os.path.exists(MEASURED) else {}
    if digest in cache:
        return cache[digest]
    import drift as drift_tool
    from media import read_frames
    j = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                   "stream=codec_type,width,height,r_frame_rate:format=duration", "-of", "json", path],
                                  capture_output=True, text=True).stdout or "{}")
    vs = [x for x in j.get("streams", []) if x["codec_type"] == "video"]
    r = {"file": path, "audio": any(x["codec_type"] == "audio" for x in j.get("streams", []))}
    if vs:
        r.update(width=vs[0]["width"], height=vs[0]["height"], fps=vs[0]["r_frame_rate"],
                 seconds=round(float(j["format"]["duration"]), 2))
    frames = read_frames(path, 960, 540, gray=True)
    rows = drift_tool.drift(path, frames=frames)
    zooms = [z for _, z, _, _ in rows if z is not None]
    r["drift_zoom"] = max(zooms, key=abs) if zooms else None
    r["drift_shift"] = max((float(np.hypot(dx, dy)) for _, z, dx, dy in rows if z is not None), default=None)
    r["wobble_rms"], r["wobble_max"], r["tracked"], r["frames"] = drift_tool.wobble(path, frames=frames)
    try:
        import sound_check
        if _sound_model is None:
            import contextlib
            import io
            import warnings
            warnings.filterwarnings("ignore", message="The given NumPy array is not writable")
            with contextlib.redirect_stdout(io.StringIO()):  # PANNs prints its checkpoint path
                _sound_model = sound_check.tagger()
        r["sound"] = sound_check.measure(path, _sound_model)
    except ImportError:
        r["sound"] = None  # optional audio extras not installed
    still = still_for(path)
    if still:
        r["still"] = still
        r["vs_still"] = still_vs_take(path, still, sheet=os.path.join("media/checks",
                                                                         os.path.splitext(os.path.basename(path))[0] + ".jpg"))
    cache = json.load(open(MEASURED)) if os.path.exists(MEASURED) else {}
    cache[digest] = r
    with open(MEASURED, "w") as f:
        json.dump(cache, f, indent=1)
    return r


def check(path):
    """Duplicate check against media/raw and media/inbox, then size, first frame against the still, sound, drift
    and wobble."""
    print(f"\n== {path}")
    digest = sha256(path)
    dupes = [p for p in glob.glob(f"{RAW}/*.mp4") + glob.glob(f"{INBOX}/*.mp4")
             if os.path.abspath(p) != os.path.abspath(path) and sha256(p) == digest]
    print("   duplicate of " + ", ".join(dupes) if dupes else "   new clip (no checksum match in media/raw or media/inbox)")
    for line in describe(measure(path)):
        print("   " + line)


def describe(r):
    out = []
    if "width" in r:
        out.append(f"{r['width']}x{r['height']} at {r['fps']} fps, {r['seconds']:.2f} s, {'with' if r['audio'] else 'NO'} audio")
    v = r.get("vs_still")
    if v is None:
        out.append("first frame: no picked still to compare with")
    elif not v["matched"]:
        out.append(f"first frame: DOES NOT MATCH {r['still']} (no common features)")
    else:
        out.append(f"first frame vs still: zoom {v['zoom']:+.2f}%, stretch {v['stretch']:+.2f}%, shift {v['shift']:.0f} px, "
                   f"redraw {v['redraw']:.1f}" + ("  REFRAMED" if v["reframed"] else "")
                   + f"; check the casting by eye in {v['sheet']}")
    if r.get("drift_zoom") is None:
        out.append("drift: not trackable (too dark or featureless)")
    else:
        out.append(f"drift: zoom up to {r['drift_zoom']:+.2f}%, shift up to {r['drift_shift']:.1f} px"
                   + ("  USE --stabilize" if abs(r["drift_zoom"]) > 0.5 else ""))
    if r.get("wobble_rms") is None:
        out.append(f"wobble: not trackable ({r.get('tracked')} of {r.get('frames')} frames)")
    else:
        out.append(f"wobble: {r['wobble_rms']:.2f} px rms, max {r['wobble_max']:.2f} px at 1080p"
                   + ("  USE --lock" if r["wobble_rms"] > 0.1 else ""))
    snd = r.get("sound")
    if snd is None:
        out.append("sound: not measured (install requirements-audio.txt)")
    elif snd["silent"]:
        out.append("sound: silent or no audio track")
    else:
        out.append(f"sound: {snd['lufs']:.1f} LUFS, peak {snd['peak']:+.1f} dBFS | {snd['tags']}"
                   + (f"  FLAG: {'; '.join(snd['flags'])}" if snd["flags"] else ""))
    return out


# ---------------------------------------------------------------- commands

def next_name(folder, stem, ext=".jpg"):
    k = 1
    while os.path.exists(os.path.join(folder, f"{stem}{k}{ext}")):
        k += 1
    return os.path.join(folder, f"{stem}{k}{ext}")


def kling_image(cfg, prompt, outs, label, gate):
    """One paid Kling image task returning len(outs) images (Kling Image 3.0). Saves each as JPEG.
    `gate` keeps the images in flight within the image pack's concurrency limit."""
    with gate:
        return _kling_image(cfg, prompt, outs, label)


def _kling_image(cfg, prompt, outs, label):
    import cv2
    import numpy as np
    k = cfg["kling_image"]
    call = uuid.uuid4().hex[:12]
    est = len(outs) * k["units_per_image"] * k["usd_per_unit"]
    log(cfg, call=call, kind="image", model=k["model"], window=label, usd_est=est, status="submitted")
    body = {"model_name": k["model"], "prompt": prompt, "n": len(outs), "resolution": k["resolution"],
            "aspect_ratio": k["aspect_ratio"], "watermark_info": {"enabled": False}}
    base, hdr = cfg["kling"]["base"], kling_headers(cfg)
    try:
        r = http("POST", base + k["endpoint"], hdr, body, timeout=120)
        if r.get("code") != 0:
            raise RuntimeError(f"Kling refused the task: {r.get('code')} {r.get('message')}")
        task = r["data"]["task_id"]
        for _ in range(120):
            rec = http("GET", f"{base}{k['endpoint']}/{task}", hdr, retries=3)["data"]
            if rec["task_status"] == "succeed":
                break
            if rec["task_status"] == "failed":
                raise RuntimeError(f"Kling task {task} failed: {rec.get('task_status_msg')}")
            time.sleep(5)
        else:
            raise RuntimeError(f"Kling image task {task} still running after 10 minutes")
        for img, out in zip(sorted(rec["task_result"]["images"], key=lambda i: i["index"]), outs):
            raw = np.frombuffer(http("GET", img["url"], timeout=300, retries=3, raw=True), np.uint8)
            cv2.imwrite(out, cv2.imdecode(raw, cv2.IMREAD_COLOR), [cv2.IMWRITE_JPEG_QUALITY, 95])
    except Exception as e:  # refused or failed tasks are not billed
        log(cfg, call=call, status="failed", error=str(e)[:300], usd_actual=0)
        raise
    units = float(rec.get("final_unit_deduction") or 0)
    log(cfg, call=call, status="done", file=",".join(outs), task=task,
        **({"usd_actual": round(units * k["usd_per_unit"], 4)} if units else {}))
    return ", ".join(outs)


def cmd_still(cfg, d, a):
    if a.model:  # e.g. compare gpt-image-2.5-flare with gpt-image-2.6-flare without editing generate.yaml
        if a.engine != "openai":
            sys.exit("--model is for --engine openai")
        cfg["openai_image"]["model"] = a.model
    ws = [window(d, r) for r in a.windows]
    n = a.n or cfg["image"]["candidates"]
    if a.engine == "kling":
        k = cfg["kling_image"]
        plan = [(f"{w['id']}: {n} stills, Kling {k['model']} {k['resolution']}", n * k["units_per_image"] * k["usd_per_unit"])
                for w in ws]
    elif a.engine == "openai":
        o = cfg["openai_image"]
        size = openai_size(o)
        crop = "" if size == o["size"] else f", cropped to {o['size']}"
        plan = [(f"{w['id']}: {n} stills, {o['model']} {size} {o['quality']}{crop} (estimate; billed by tokens)",
                 n * o["usd_per_image"]) for w in ws]
    else:
        plan = [(f"{w['id']}: {n} stills, {cfg['image']['model']} {cfg['image']['size']}", n * cfg["image"]["usd_per_image"])
                for w in ws]
    for w in ws:
        print(f"\n{w['id']} image prompt:\n{build(w, d['prompt_style'])[0]}")
    approve(cfg, plan, a)
    jobs = []
    gate = threading.BoundedSemaphore(max(1, cfg["kling_image"]["concurrency"] // n))
    openai_gate = threading.BoundedSemaphore(1)
    with cf.ThreadPoolExecutor(8) as ex:
        for w in ws:
            folder = os.path.join(STILLS, num(w))
            os.makedirs(folder, exist_ok=True)
            prompt = build(w, d["prompt_style"])[0] + (f" {a.note}" if a.note else "")
            if a.engine == "kling":  # one task returns all n images; files k1.jpg, k2.jpg, ...
                outs = []
                for _ in range(n):
                    outs.append(next_name(folder, "k"))
                    open(outs[-1], "wb").close()
                jobs.append(ex.submit(kling_image, cfg, prompt, outs, w["id"], gate))
                continue
            if a.engine == "openai":  # one call returns all n images; files o1.jpg, o2.jpg, ...
                outs = []
                for _ in range(n):
                    outs.append(next_name(folder, "o"))
                    open(outs[-1], "wb").close()
                jobs.append(ex.submit(openai_image, cfg, prompt, outs, w["id"], openai_gate))
                continue
            for _ in range(n):
                out = next_name(folder, "c")
                open(out, "wb").close()  # reserve the name so parallel jobs do not collide
                jobs.append(ex.submit(gemini_image, cfg, [{"type": "text", "text": prompt}], out, w["id"]))
        report(jobs)


def cmd_edit(cfg, d, a):
    """Edit with the model that made the still where it has an edit call (GPT Image for o*.jpg), otherwise Gemini."""
    w = window(d, os.path.dirname(a.image))
    engine = a.engine if a.engine != "auto" else ("openai" if os.path.basename(a.image).startswith("o") else "gemini")
    text = (f"Edit this image. {a.instruction} Keep everything else exactly as it is: "
            "the framing, light, people, colours and film grain.")
    if engine == "openai":
        o = cfg["openai_image"]
        plan = [(f"{w['id']}: edit {a.image}, {o['model']} {openai_size(o)} (estimate; billed by tokens)", o["usd_per_image"])]
    else:
        plan = [(f"{w['id']}: edit {a.image}, {cfg['image']['model']}", cfg["image"]["usd_per_image"])]
    print(f"\nEdit instruction: {a.instruction}")
    approve(cfg, plan, a)
    out = next_name(os.path.dirname(a.image), os.path.splitext(os.path.basename(a.image))[0] + "-e")
    if engine == "openai":
        print(openai_image(cfg, text, [out], w["id"], threading.BoundedSemaphore(1), image=a.image))
        return
    inputs = [{"type": "image", "data": b64(a.image), "mime_type": mime(a.image)}, {"type": "text", "text": text}]
    print(gemini_image(cfg, inputs, out, w["id"]))


def import_videos(w, files, tag):
    """Copy hand-made video takes into media/inbox/<id>_<tag>-take1.mp4, ... (skipping checksum duplicates of
    anything in media/inbox or media/raw), then check them."""
    known = {sha256(p): p for p in glob.glob(f"{INBOX}/*.mp4") + glob.glob(f"{RAW}/*.mp4")}
    done = []
    for src in files:
        h = sha256(src)
        if h in known:
            print(f"skip {src}: already in as {known[h]}")
            continue
        out = next_name(INBOX, f"{w['id']}_{tag}-take", ".mp4")
        if src.lower().endswith(".mp4"):
            shutil.copyfile(src, out)
        else:  # .mov or .webm: rewrap or re-encode to H.264 MP4, keeping any sound
            subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-c:v", "libx264", "-crf", "14", "-preset", "slow",
                            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", out], check=True)
        print(f"{src} -> {out}")
        known[sha256(out)] = out
        done.append(out)
    for path in done:
        check(path)


def cmd_import(cfg, d, a):
    """Copy hand-made stills (Midjourney downloads) into media/stills/NN/ as m1.jpg, m2.jpg, ..., converting PNG or
    WebP to JPEG. A file whose checksum matches an earlier import or an existing still is skipped. Video files
    (.mp4, .mov, .webm) go to media/inbox/ as takes instead (see import_videos)."""
    import cv2
    w = window(d, a.window)
    videos = [f for f in a.files if f.lower().endswith((".mp4", ".mov", ".webm"))]
    a.files = [f for f in a.files if f not in videos]
    if videos:
        import_videos(w, videos, a.video_tag)
    folder = os.path.join(STILLS, num(w))
    os.makedirs(folder, exist_ok=True)
    record = os.path.join(folder, "imported.json")  # source checksum -> still, since converted files change checksum
    seen = json.load(open(record)) if os.path.exists(record) else {}
    known = {sha256(p): p for p in glob.glob(f"{STILLS}/*.jpg") + glob.glob(f"{STILLS}/*/*.jpg")}
    for other in glob.glob(f"{STILLS}/*/imported.json"):  # sources imported into any window
        if os.path.abspath(other) != os.path.abspath(record):
            known.update(json.load(open(other)))
    for src in a.files:
        h = sha256(src)
        if h in seen or h in known:
            print(f"skip {src}: already in as {seen.get(h) or known[h]}")
            continue
        img = cv2.imread(src, cv2.IMREAD_COLOR)
        if img is None:
            print(f"skip {src}: not an image OpenCV can read")
            continue
        out = next_name(folder, a.prefix)
        if open(src, "rb").read(2) == b"\xff\xd8":  # already a JPEG: copy untouched
            shutil.copyfile(src, out)
        else:
            cv2.imwrite(out, img, [cv2.IMWRITE_JPEG_QUALITY, 95])
        ih, iw = img.shape[:2]
        note = "" if abs(iw / ih - 16 / 9) < 0.02 else f"; NOT 16:9 ({iw / ih:.2f}:1), a grid or the wrong --ar?"
        print(f"{src} -> {out} ({iw}x{ih}{note})")
        seen[h] = out
        known[sha256(out)] = out
    with open(record, "w") as f:
        json.dump(seen, f, indent=1)


def cmd_pick(cfg, d, a):
    w = window(d, a.window)
    dest = os.path.join(STILLS, w["id"] + ".jpg")
    if os.path.exists(dest) and not a.force:
        sys.exit(f"{dest} exists; pass --force to replace it")
    shutil.copyfile(a.image, dest)
    print(f"{a.image} -> {dest} (set `still: {dest}` in scenes.yaml)")


def cmd_video(cfg, d, a):
    jobs, plan = [], []
    engines = list(dict.fromkeys(e.strip() for e in a.engine.split(",")))
    for e in engines:
        if e != "auto" and e not in VIDEO_ENGINES:
            sys.exit(f"--engine {e}: choose from auto, {', '.join(VIDEO_ENGINES)} (comma-separated for several)")
    for ref in a.windows:
        w = window(d, ref)
        still = os.path.join(STILLS, w["id"] + ".jpg")
        if not os.path.exists(still) and not a.dry_run:
            sys.exit(f"no picked still for {w['id']}: run `pick` first")
        families = list(dict.fromkeys(engine_for(cfg, w, e)[0] for e in engines))
        for family in families:
            v = cfg["video"][family]
            secs = a.seconds or v["seconds"]
            end_on = a.end_on_still or v.get("end_on_still", False)
            if end_on and v["engine"] == "wan":
                sys.exit("--end-on-still is not wired up for Wan")
            prompt = " ".join(filter(None, [v.get("prompt_prefix"), build(w, d["prompt_style"])[1]]))
            if v["engine"] == "gemini":
                usd, name, fn = secs * v["usd_per_second"], v["model"], gemini_video
            elif v["engine"] == "kling":
                usd, name, fn = secs * v["units_per_second"] * v["usd_per_unit"], "kling-4.0", kling_video
            else:
                usd, name, fn = secs * v["usd_per_second"], v["model"], wan_video
            for _ in range(a.takes):
                plan.append((f"{w['id']}: {name}, {secs} s, {v['resolution']}{', ends on the still' if end_on else ''}", usd))
                jobs.append((fn, w, v, still, prompt, secs, end_on, TAKE_TAGS[v["engine"]]))
            print(f"\n{w['id']} ({family} -> {name}) video prompt:\n{prompt}")
    approve(cfg, plan, a)
    os.makedirs(INBOX, exist_ok=True)
    futures = []
    with cf.ThreadPoolExecutor(5) as ex:  # Kling trial packs allow 5 concurrent tasks
        for fn, w, v, still, prompt, secs, end_on, tag in jobs:
            out = next_name(INBOX, f"{w['id']}_{tag}-take", ".mp4")
            open(out, "wb").close()
            futures.append(ex.submit(fn, cfg, v, w, still, prompt, secs, end_on, out))
        done = report(futures)
    for path in done:
        check(path)


def report(futures):
    done = []
    for f in cf.as_completed(futures):
        try:
            done.append(f.result())
            print(f"saved {done[-1]}")
        except Exception as e:
            print(f"FAILED: {e}")
    for p in glob.glob(f"{STILLS}/*/*.jpg") + glob.glob(f"{INBOX}/*.mp4"):
        if os.path.getsize(p) == 0:  # names reserved by failed jobs
            os.remove(p)
    return sorted(done)


STILL_JUDGE = ["Casting as described", "Faces away", "No extra people", "No text or logos", "London dusk, 35 mm",
               "Edits needed", "Pick"]
TAKE_JUDGE = ["Casting held", "Hands, objects, steam", "Loops well", "Keep"]


def ledger_by_file(cfg):
    """file -> (cost, seconds from submission to done, model) from the spend ledger."""
    first, calls = {}, ledger(cfg)
    if os.path.exists(cfg["ledger"]):
        for line in open(cfg["ledger"]):
            rec = json.loads(line)
            first.setdefault(rec["call"], rec["time"])
    out = {}
    for c in calls.values():
        files = [f for f in (c.get("file") or "").split(",") if f]
        if not files or c.get("status") != "done":
            continue
        took = (datetime.fromisoformat(c["time"]) - datetime.fromisoformat(first[c["call"]])).total_seconds()
        for f in files:
            out[os.path.normpath(f)] = (c.get("usd_actual", c["usd_est"]) / len(files), took, c.get("model"))
    return out


def still_model(path):
    stem = os.path.splitext(os.path.basename(path))[0]
    edits = stem.count("-e")
    return STILL_MODELS.get(stem[:1], "?") + (f", {edits} edit{'s' * (edits > 1)}" if edits else "")


def take_model(path):
    tag = re.search(r"_(omni|kling4|wan3|kling|veo|mj)", os.path.basename(path))
    return {"omni": "Gemini Omni", "kling4": "Kling 4.0", "kling": "Kling", "wan3": "Wan 3.0", "veo": "Veo",
            "mj": "Midjourney video"}.get(
        tag.group(1) if tag else "", "?")


def old_judgements(path):
    """Kayvan's entries in an existing scorecard, by row key and column, so rewriting it keeps them."""
    kept, header = {}, None
    if not os.path.exists(path):
        return kept
    for line in open(path):
        if not line.startswith("|"):
            header = None
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if header is None:
            header = cells
        elif not set("".join(cells)) <= set("-: "):
            for h, c in zip(header, cells):
                if c and h in STILL_JUDGE + TAKE_JUDGE:
                    kept[(cells[0], h)] = c
    return kept


def table(header, rows):
    return ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"] + \
           ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]


def cmd_review(cfg, d, a):
    """Contact sheet (media/review.html) and the scorecard docs/<batch>-scorecard.md for the windows given, or for
    every window whose status is the current batch. Measurements are filled in; the judgement columns are blank for
    Kayvan, and anything already written in them is kept when the scorecard is rewritten."""
    import cv2
    ws = [window(d, r) for r in a.windows] if a.windows else [w for w in d["windows"] if w["status"] == cfg["batch"]]
    if not ws:
        sys.exit(f"no windows given and none with status {cfg['batch']}")
    parts = ["<!doctype html><meta charset=utf-8><title>Window review</title><style>body{background:#111;color:#ddd;"
             "font:14px system-ui;margin:16px}figure{display:inline-block;margin:6px;width:min(48%,720px)}img,video"
             "{width:100%}figcaption{padding:4px 0}</style>"]
    card_path = a.out or f"docs/{cfg['batch']}-scorecard.md"
    kept, costs = old_judgements(card_path), ledger_by_file(cfg)
    usd = lambda p: f"${costs[os.path.normpath(p)][0]:.3f}" if os.path.normpath(p) in costs else ""
    title = re.sub(r"^batch-0*(\d+)$", r"Batch \1", cfg["batch"])
    card = [f"# {title} scorecard", "",
            f"> Written by `pipeline/generate.py review` on {datetime.now():%d %b %Y}. Measured columns are filled in; "
            "the columns from \"Casting\" on are for Kayvan's judgement and are kept when the scorecard is rewritten.", "",
            "How to read the measurements: **first frame** compares the take's first frame with its still (zoom, shift in "
            "px at 1080p, and *redraw*: about 1.5 when the still is kept, higher when the model has repainted it; a recast "
            "person must be judged by eye on the comparison sheet in `media/checks/`). **Wobble** is the frame-to-frame "
            "shake left after removing slow drift, rms and max in px at 1080p (under about 0.1 is still; above it, loop "
            "with `--lock`). **Sound** is loudness in LUFS (loudness units relative to full scale) with music and speech "
            "flags from `sound_check.py`.", ""]
    for w in ws:
        parts.append(f"<h2>{html.escape(w['id'])}: {html.escape(w['title'])}</h2><p>{html.escape(w['scene'])}</p>")
        stills = sorted(glob.glob(f"{STILLS}/{num(w)}/*.jpg"))
        seen, takes = set(), []
        for p in sorted(glob.glob(f"{INBOX}/{w['id']}*.mp4")) + sorted(glob.glob(f"{RAW}/{w['id']}*.mp4")):
            h = sha256(p)
            if h not in seen:
                seen.add(h)
                takes.append(p)
        for p in stills + takes:
            rel = os.path.relpath(p, "media")
            tag = f"<video src='{rel}' controls loop></video>" if p.endswith(".mp4") else f"<img src='{rel}'>"
            parts.append(f"<figure>{tag}<figcaption>{html.escape(p)}</figcaption></figure>")
        picked = os.path.join(STILLS, w["id"] + ".jpg")
        card += [f"## {w['id']}: {w['title']}", "",
                 f"{w['kind']}, {'empty room' if w.get('empty') else 'people'}; video model in scenes.yaml: {w['model']}."
                 + (f" Picked still: `{picked}`." if os.path.exists(picked) else ""), "", "### Stills", ""]
        rows = []
        for p in stills:
            img = cv2.imread(p)
            size = f"{img.shape[1]}x{img.shape[0]}" if img is not None else "?"
            key = f"`{p}`"
            c = costs.get(os.path.normpath(p))
            model = still_model(p) + (f" ({c[2].removeprefix('gpt-image-')})" if c and str(c[2]).startswith("gpt-image") else "")
            rows.append([key, model, size, usd(p)] + [kept.get((key, h), "") for h in STILL_JUDGE])
        card += table(["Still", "Model", "Size", "Cost"] + STILL_JUDGE, rows) if rows else ["No stills yet."]
        card += ["", "### Takes", ""]
        rows = []
        for p in takes:
            print(f"measuring {p}", flush=True)
            r = measure(p)
            v, snd = r.get("vs_still"), r.get("sound")
            first = ("no still" if v is None else "NO MATCH" if not v["matched"] else
                     f"{v['zoom']:+.1f}%, {v['shift']:.0f} px, redraw {v['redraw']:.1f}" + (" REFRAMED" if v["reframed"] else ""))
            wob = "not trackable" if r.get("wobble_rms") is None else f"{r['wobble_rms']:.2f} / {r['wobble_max']:.2f}"
            dz = "not trackable" if r.get("drift_zoom") is None else f"{r['drift_zoom']:+.2f}%"
            sound = ("not measured" if snd is None else "silent" if snd["silent"] else
                     f"{snd['lufs']:.0f} LUFS" + (f", {'; '.join(snd['flags'])}" if snd["flags"] else ", no flags"))
            c = costs.get(os.path.normpath(p))
            key = f"`{p}`"
            rows.append([key, take_model(p), f"{r.get('seconds', 0):.1f} s", usd(p), f"{c[1] / 60:.1f} min" if c else "",
                         first, wob, dz, sound] + [kept.get((key, h), "") for h in TAKE_JUDGE])
        card += table(["Take", "Model", "Length", "Cost", "Time", "First frame vs still", "Wobble rms / max px",
                       "Drift zoom", "Sound"] + TAKE_JUDGE, rows) if rows else ["No takes yet."]
        card.append("")
    with open("media/review.html", "w") as f:
        f.write("\n".join(parts))
    with open(card_path, "w") as f:
        f.write("\n".join(card).rstrip() + "\n")
    print(f"wrote media/review.html and {card_path}")


def cmd_fetch(cfg, d, a):
    if a.service == "kling":
        kling_wait(cfg, a.id, a.out)
    elif a.service == "wan":
        wan_wait(cfg, a.id, a.out)
    else:
        r = http("GET", f"{cfg['gemini']['base']}/interactions/{a.id}", gemini_headers(cfg), timeout=600, retries=3)
        with open(a.out, "wb") as f:
            f.write(base64.b64decode(output_of(r, "video")["data"]))
    print(f"saved {a.out}")
    check(a.out)


def cmd_spend(cfg, d, a):
    calls = ledger(cfg)
    for c in calls.values():
        usd = c.get("usd_actual", c["usd_est"])
        print(f"{c['time']}  {c.get('batch')}  {c['kind']:5}  {c['window']:32} {c['status']:10} ${usd:.3f}"
              + ("" if "usd_actual" in c else " (estimate)"))
    print(f"total ${spent(cfg):.2f}; {cfg['batch']} ${spent(cfg, cfg['batch']):.2f} of ${cfg['batch_budget_usd']:.2f}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def paid(p):
        p.add_argument("--dry-run", action="store_true", help="print the plan and cost, spend nothing")
        p.add_argument("--yes", action="store_true", help="skip the prompt (only after Kayvan has approved)")
        p.add_argument("--budget", type=float, default=None, help="override run_budget_usd for this run")

    s = sub.add_parser("still"); s.add_argument("windows", nargs="+"); s.add_argument("-n", type=int)
    s.add_argument("--engine", choices=["gemini", "kling", "openai"], default="gemini",
                   help="Gemini 3 Pro Image, Kling Image 3.0 or GPT Image (model in generate.yaml)")
    s.add_argument("--note", help="extra sentence appended to the image prompt for this run")
    s.add_argument("--model", help="GPT Image model for this run (default: openai_image.model in generate.yaml)"); paid(s)
    e = sub.add_parser("edit"); e.add_argument("image"); e.add_argument("instruction")
    e.add_argument("--engine", choices=["auto", "gemini", "openai"], default="auto",
                   help="auto: GPT Image for o*.jpg, Gemini for everything else"); paid(e)
    i = sub.add_parser("import"); i.add_argument("window"); i.add_argument("files", nargs="+")
    i.add_argument("--prefix", default="m", help="file prefix in media/stills/NN/ (m = Midjourney)")
    i.add_argument("--video-tag", default="mj", help="take tag for video files (mj = Midjourney video)")
    p = sub.add_parser("pick"); p.add_argument("window"); p.add_argument("image"); p.add_argument("--force", action="store_true")
    v = sub.add_parser("video"); v.add_argument("windows", nargs="+"); v.add_argument("--takes", type=int, default=1)
    v.add_argument("--seconds", type=int); v.add_argument("--end-on-still", action="store_true")
    v.add_argument("--engine", default="auto", help="auto (from scenes.yaml), omni, kling or wan; comma-separated "
                   "for one take on each, e.g. kling,wan"); paid(v)
    r = sub.add_parser("review"); r.add_argument("windows", nargs="*", help="default: the windows of the current batch")
    r.add_argument("--out", help="scorecard path (default docs/<batch>-scorecard.md)")
    c = sub.add_parser("check"); c.add_argument("files", nargs="+")
    f = sub.add_parser("fetch"); f.add_argument("service", choices=["kling", "gemini", "wan"]); f.add_argument("id"); f.add_argument("out")
    sub.add_parser("spend")
    a = ap.parse_args()

    cfg = yaml.safe_load(open(CONFIG))
    if getattr(a, "budget", 0) is None:
        a.budget = cfg["run_budget_usd"]
    load_env()
    d = load()
    if a.cmd == "check":
        for path in a.files:
            check(path)
    else:
        globals()[f"cmd_{a.cmd}"](cfg, d, a)


if __name__ == "__main__":
    main()
