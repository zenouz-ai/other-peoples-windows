"""Small FFmpeg helpers shared by the pipeline scripts."""
import json
import shutil
import subprocess

import numpy as np


def ensure_ffmpeg():
    """Use ffmpeg/ffprobe from PATH if present, otherwise the static build from the static-ffmpeg package."""
    if shutil.which("ffmpeg") and shutil.which("ffprobe"):
        return
    try:
        import static_ffmpeg
        static_ffmpeg.add_paths()  # downloads once into the virtualenv, then prepends it to PATH
    except ImportError:
        raise SystemExit("ffmpeg not found: pip install -r requirements.txt (includes static-ffmpeg) or install ffmpeg")


ensure_ffmpeg()

FPS = 24
SR = 48000  # audio sample rate


def probe(path):
    """Return (width, height, frame_count, duration_seconds) of the first video stream."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height,nb_frames:format=duration", "-of", "json", path],
        capture_output=True, text=True, check=True).stdout
    j = json.loads(out)
    s = j["streams"][0]
    return int(s["width"]), int(s["height"]), int(s.get("nb_frames") or 0), float(j["format"]["duration"])


def read_frames(path, width=None, height=None, gray=False):
    """Decode a whole clip at FPS into a numpy array (frames, H, W[, 3]). Optionally rescale.

    Clips at other frame rates (some models deliver 25 or 30 fps) are resampled to FPS, so frame
    numbers in scenes.yaml always mean 1/24 s and the sound stays in sync."""
    w, h, _, _ = probe(path)
    filters = [f"fps={FPS}"]
    if width and height:
        filters.append(f"scale={width}:{height}:flags=lanczos")
        w, h = width, height
    vf = ["-vf", ",".join(filters)]
    pix = "gray" if gray else "rgb24"
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, *vf, "-f", "rawvideo", "-pix_fmt", pix, "-"],
                         capture_output=True, check=True).stdout
    shape = (-1, h, w) if gray else (-1, h, w, 3)
    return np.frombuffer(raw, np.uint8).reshape(shape)


def frame_writer(path, width, height, crf=16, preset="veryfast", fps=FPS):
    """Open an FFmpeg process that encodes raw RGB frames written to its stdin."""
    return subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{width}x{height}",
         "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
         "-pix_fmt", "yuv420p", "-movflags", "+faststart", path],
        stdin=subprocess.PIPE)


def read_audio(path):
    """Decode a clip's audio as float32 stereo at 48 kHz. Returns an empty array if there is no audio."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vn", "-ac", "2", "-ar", str(SR),
                          "-f", "s16le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.int16).reshape(-1, 2).astype(np.float32)


def write_wav(path, samples):
    import wave
    with wave.open(path, "wb") as o:
        o.setnchannels(2)
        o.setsampwidth(2)
        o.setframerate(SR)
        o.writeframes(np.clip(samples, -32768, 32767).astype(np.int16).tobytes())


def mux(video, wav, out, audio_bitrate="192k"):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-i", wav, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", audio_bitrate, "-shortest", "-movflags", "+faststart", out],
                   check=True)
