"""Build, check and publish the prompts for every window from scenes/scenes.yaml.

Each window stores only its parts (scene, motion, ambience, empty); the shared wording lives once under
`prompt_style`, so a rule changed there reaches every prompt.

Usage:
  python pipeline/prompts.py show 07                 # print one window's image and video prompts
  python pipeline/prompts.py show 07 --midjourney    # the image prompt for Midjourney (pasted by hand)
  python pipeline/prompts.py show 07 --midjourney-video   # the motion prompt for animating the picked still there
  python pipeline/prompts.py lint                    # check every window against the house rules
  python pipeline/prompts.py brief batch-02          # write docs/batch-02.md and docs/batch-02.pdf
"""
import argparse
import re
import sys

import yaml

SCENES = "scenes/scenes.yaml"

# Words that invite music or speech into the generated sound. Ambience is matched whole-word.
SOUND_BANNED = ["music", "musical", "song", "singing", "sing", "radio", "television", "tv", "voice", "voices",
                "talk", "talking", "dialogue", "speech", "lullaby", "piano", "guitar", "melody", "tune", "hum along"]
# Motion the models get wrong (log.md, Findings) or that breaks a loop.
MOTION_BANNED = ["throw", "throws", "enters", "leaves the", "walks in", "walks out", "looks at the camera",
                 "drinks", "sips", "pours", "hands over", "stands up"]


def load(path=SCENES):
    with open(path) as f:
        return yaml.safe_load(f)


def build(w, style):
    """Return (image_prompt, video_prompt) for a window that has scene/motion/ambience parts."""
    people = style["empty_room"] if w.get("empty") else style["people"]
    image = style["image"].format(scene=w["scene"], people=people).strip()
    stay = style["stay_empty"] if w.get("empty") else style["stay_people"]
    video = style["video"].format(motion=w["motion"], stay=stay, ambience=w["ambience"]).strip()
    return " ".join(image.split()), " ".join(video.split())


MIDJOURNEY_PARAMS = "--ar 16:9 --style raw"


def midjourney(w, style):
    """The image prompt for Midjourney: the aspect ratio moves from the opening sentence into its parameters."""
    image = build(w, style)[0]
    return re.sub(r"^Generate a 16:9 image\.\s*", "", image) + " " + MIDJOURNEY_PARAMS


MIDJOURNEY_VIDEO_PARAMS = "--motion low --raw"


def midjourney_video(w, style):
    """The motion prompt for Midjourney video (the picked still uploaded as the starting frame). Midjourney video
    has no sound, so the ambience sentences are left out; the window gets a sound bed (make_loop.py --bed)."""
    video = build(w, style)[1]
    return video.split(" Ambient noise:")[0] + " " + MIDJOURNEY_VIDEO_PARAMS


def lint(d):
    """Return a list of problems; empty means every window follows the rules."""
    problems, titles = [], {}
    ws = d["windows"]
    active = [w for w in ws if w["status"] != "cut"]  # cut scenes keep their IDs but are not in the film
    if len(active) != d["target_windows"]:
        problems.append(f"{len(active)} windows in the film (status not cut), target is {d['target_windows']}")
    for n, w in enumerate(ws, 1):
        wid = w["id"]
        if not re.fullmatch(rf"{n:02d}-[a-z0-9-]+", wid):
            problems.append(f"{wid}: expected ID {n:02d}-short-name in order")
        if w["title"].lower() in titles:
            problems.append(f"{wid}: title duplicates {titles[w['title'].lower()]}")
        titles[w["title"].lower()] = wid
        if w["status"] == "done":
            for k in ("raw", "loop", "loop_settings"):
                if k not in w:
                    problems.append(f"{wid}: done but has no {k}")
            continue
        for k in ("scene", "motion", "ambience", "model"):
            if not w.get(k):
                problems.append(f"{wid}: missing {k}")
        amb = w.get("ambience", "").lower()
        for word in SOUND_BANNED:
            if re.search(rf"\b{re.escape(word)}\b", amb):
                problems.append(f"{wid}: ambience mentions '{word}' (invites music or speech)")
        mot = w.get("motion", "").lower()
        for word in MOTION_BANNED:
            if word in mot:
                problems.append(f"{wid}: motion includes '{word}'")
        if len(w.get("ambience", "").split(" and ")) > 2:
            problems.append(f"{wid}: more than two sounds; keep the ambience simple and faint")
    return problems


def brief_markdown(d, batch):
    meta = d["batches"][batch]
    ws = [w for w in d["windows"] if w["status"] == batch]
    lines = [f"# {meta['title']}", "", f"> {meta['summary']}", "", "## Purpose", "", meta["purpose"].strip(), "",
             "## Key Points", ""]
    lines += [f"- {p}" for p in meta["key_points"]]
    lines += ["", "## Next Actions", ""] + [f"- [ ] {a}" for a in meta["next_actions"]]
    lines += ["", f"## The {len(ws)} windows", "",
              "_Generated from `scenes/scenes.yaml` by `pipeline/prompts.py brief`; edit the YAML, not this file._", ""]
    for w in ws:
        img, vid = build(w, d["prompt_style"])
        lines += [f"### {w['id']}: {w['title']}", "", f"**Kind:** {w['kind']} · **Model:** {meta['models'][w['model']]}", ""]
        if w.get("notes"):
            lines += [f"_{w['notes']}_", ""]
        lines += ["**Image prompt (Gemini, GPT Image)**", "", "```", img, "```", ""]
        if meta.get("midjourney"):
            lines += ["**Midjourney prompt**", "", "```", midjourney(w, d["prompt_style"]), "```", "",
                      "**Midjourney video prompt** (the picked still as starting frame)", "", "```",
                      midjourney_video(w, d["prompt_style"]), "```", ""]
        lines += [f"**Video prompt ({w['model']})**", "", "```", vid, "```", ""]
    return "\n".join(lines).rstrip() + "\n"


def brief_pdf(d, batch, path):
    """A phone-friendly PDF of the same brief, for copying prompts while generating."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer

    meta = d["batches"][batch]
    ss = getSampleStyleSheet()
    body = ParagraphStyle("b", parent=ss["BodyText"], fontSize=10.5, leading=14)
    prompt = ParagraphStyle("p", parent=body, fontName="Courier", fontSize=9, leading=12, backColor="#f3f3f3",
                            borderPadding=5, spaceBefore=3, spaceAfter=8)
    label = ParagraphStyle("l", parent=body, fontSize=8, textColor="#666666", spaceBefore=4)
    esc = lambda s: s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    rich = lambda s: re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", esc(s)).replace("`", "")  # Markdown bold, no backticks
    story = [Paragraph(esc(meta["title"]), ss["Title"]), Paragraph(esc(meta["summary"]), body), Spacer(1, 6)]
    story += [Paragraph("• " + rich(p), body) for p in meta["key_points"]]
    for w in (w for w in d["windows"] if w["status"] == batch):
        img, vid = build(w, d["prompt_style"])
        story.append(KeepTogether([
            Spacer(1, 10), Paragraph(f"{esc(w['id'])}: {esc(w['title'])}", ss["Heading2"]),
            Paragraph(f"{esc(w['kind'])} · {esc(meta['models'][w['model']])}", body),
            Paragraph("IMAGE PROMPT (GEMINI, GPT IMAGE)", label), Paragraph(esc(img), prompt),
            *([Paragraph("MIDJOURNEY PROMPT", label), Paragraph(esc(midjourney(w, d["prompt_style"])), prompt),
               Paragraph("MIDJOURNEY VIDEO PROMPT (PICKED STILL AS STARTING FRAME)", label),
               Paragraph(esc(midjourney_video(w, d["prompt_style"])), prompt)]
              if meta.get("midjourney") else []),
            Paragraph(f"VIDEO PROMPT ({w['model'].upper()})", label), Paragraph(esc(vid), prompt)]))
    SimpleDocTemplate(path, pagesize=A4, title=meta["title"], leftMargin=16 * mm, rightMargin=16 * mm,
                      topMargin=14 * mm, bottomMargin=14 * mm).build(story)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("show"); s.add_argument("window", help="window ID or its number, e.g. 07")
    s.add_argument("--midjourney", action="store_true", help=f"only the Midjourney image prompt ({MIDJOURNEY_PARAMS})")
    s.add_argument("--midjourney-video", action="store_true",
                   help=f"only the Midjourney video motion prompt ({MIDJOURNEY_VIDEO_PARAMS})")
    sub.add_parser("lint")
    b = sub.add_parser("brief"); b.add_argument("batch")
    a = ap.parse_args()
    d = load()

    if a.cmd == "show":
        w = next((w for w in d["windows"] if w["id"] == a.window or w["id"].startswith(a.window.zfill(2) + "-")), None)
        if not w or "scene" not in w:
            sys.exit(f"no prompts for {a.window}")
        if a.midjourney or a.midjourney_video:
            print(midjourney_video(w, d["prompt_style"]) if a.midjourney_video else midjourney(w, d["prompt_style"]))
            return
        img, vid = build(w, d["prompt_style"])
        print(f"{w['id']} ({w['model']})\n\nIMAGE\n{img}\n\nVIDEO\n{vid}")
    elif a.cmd == "lint":
        problems = lint(d)
        n = sum(w["status"] != "cut" for w in d["windows"])
        print("\n".join(problems) or f"ok: {n} windows in the film ({len(d['windows'])} scenes) follow the rules")
        sys.exit(1 if problems else 0)
    elif a.cmd == "brief":
        md = f"docs/{a.batch}.md"
        with open(md, "w") as f:
            f.write(brief_markdown(d, a.batch))
        brief_pdf(d, a.batch, f"docs/{a.batch}.pdf")
        print(f"wrote {md} and docs/{a.batch}.pdf")


if __name__ == "__main__":
    main()
