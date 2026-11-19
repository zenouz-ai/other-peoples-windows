#!/usr/bin/env python3
"""Build (and optionally publish) the curated public Other People's Windows mirror.

The canonical Other People's Windows repo is private. This script produces a sanitized,
allowlisted export suitable for the public mirror at
``zenouz-ai/other-peoples-windows`` without ever flipping the private repo public.

Pipeline
--------
1. Enumerate git-tracked files in the source repo.
2. Keep only files matching ``public-export/manifest.txt`` (allowlist).
3. Drop anything matching ``public-export/denylist.txt`` (applied on top).
4. Copy the survivors into ``--output-dir``.
5. Overlay sanitized files from ``public-export/replacements/``.
6. Apply ``public-export/content-scrub.txt`` substitutions to text files.
7. Verify every path in ``public-export/required.txt`` exists.
8. Scan the exported tree for ``forbidden-content.txt`` and
   ``secret-patterns.txt`` (BLOCKING).
9. With ``--scan-history``, scan the source repo's git history for secret
   patterns (reported as warnings; the mirror is published as a fresh tree
   with no history).

Nothing is pushed unless ``--push`` is given, and the script never force-pushes.

Usage
-----
    python3 scripts/publish_public_mirror.py --output-dir /tmp/opw-public
    python3 scripts/publish_public_mirror.py --output-dir /tmp/opw-public --scan-history

Publish (only after a clean validation) to the public mirror as fresh history:

    python3 scripts/publish_public_mirror.py --output-dir /tmp/opw-public \
        --scan-history --push

The first publish to an empty repo creates the branch; later publishes update it
with --force-with-lease (which refuses if the mirror moved since the fetch). The
published commit is authored by a neutral bot identity so the operator's git
name/email never reach the public repo.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXPORT_DIR = REPO_ROOT / "public-export"
REPLACEMENTS_DIR = EXPORT_DIR / "replacements"

DEFAULT_REMOTE_NAME = "public"
DEFAULT_REMOTE_URL = "https://github.com/zenouz-ai/other-peoples-windows.git"

# Extensions treated as binary: never scrubbed or scanned for text content.
# Lockfiles (poetry.lock / package-lock.json) are intentionally NOT here — they
# are allowlisted for export and must be scanned, since a tokenized package URL
# or private index reference in a lockfile would otherwise reach the public tree.
BINARY_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".woff", ".woff2",
    ".ttf", ".otf", ".mp4", ".webp", ".eot", ".zip", ".gz", ".tar", ".whl", ".pyc",
}

GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
BOLD = "\033[1m"
RESET = "\033[0m"


def color(text: str, code: str) -> str:
    if sys.stdout.isatty():
        return f"{code}{text}{RESET}"
    return text


# --------------------------------------------------------------------------- #
# Pattern files
# --------------------------------------------------------------------------- #

def read_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    out: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        out.append(line)
    return out


def glob_to_regex(pattern: str) -> re.Pattern[str]:
    """Translate a gitignore-style glob into an anchored regex over a path."""
    anchored_anywhere = "/" not in pattern.rstrip("/")
    out = ["^"]
    if anchored_anywhere and not pattern.startswith("**"):
        out.append("(?:.*/)?")
    i = 0
    n = len(pattern)
    while i < n:
        c = pattern[i]
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif pattern.startswith("**", i):
            out.append(".*")
            i += 2
        elif c == "*":
            out.append("[^/]*")
            i += 1
        elif c == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(c))
            i += 1
    out.append("$")
    return re.compile("".join(out), re.IGNORECASE)


@dataclass
class DenyMatcher:
    positives: list[re.Pattern[str]] = field(default_factory=list)
    negatives: list[re.Pattern[str]] = field(default_factory=list)

    @classmethod
    def load(cls, path: Path) -> DenyMatcher:
        m = cls()
        for line in read_lines(path):
            if line.startswith("!"):
                m.negatives.append(glob_to_regex(line[1:]))
            else:
                m.positives.append(glob_to_regex(line))
        return m

    def denied(self, rel: str) -> bool:
        if not any(p.match(rel) for p in self.positives):
            return False
        return not any(p.match(rel) for p in self.negatives)


def manifest_allows(rel: str, entries: list[str]) -> bool:
    return any(rel == e or rel.startswith(e + "/") for e in entries)


# --------------------------------------------------------------------------- #
# Git helpers
# --------------------------------------------------------------------------- #

def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO_ROOT, check=True,
        capture_output=True, text=True,
    ).stdout


def tracked_files() -> list[str]:
    return [p for p in git("ls-files").splitlines() if p]


# --------------------------------------------------------------------------- #
# Content helpers
# --------------------------------------------------------------------------- #

def is_text_file(path: Path) -> bool:
    if path.suffix.lower() in BINARY_SUFFIXES:
        return False
    try:
        with path.open("rb") as fh:
            chunk = fh.read(4096)
    except OSError:
        return False
    return b"\x00" not in chunk


def load_scrub(path: Path) -> list[tuple[re.Pattern[str], str, str]]:
    rules: list[tuple[re.Pattern[str], str, str]] = []
    for line in read_lines(path):
        if " => " not in line:
            continue
        pat, repl = line.split(" => ", 1)
        rules.append((re.compile(pat), repl, pat))
    return rules


# --------------------------------------------------------------------------- #
# Main steps
# --------------------------------------------------------------------------- #

def clean_output(out: Path) -> None:
    resolved = out.resolve()
    # Never wipe the filesystem root, the home dir, or anything inside the source
    # repo: clean_output() recursively deletes the target's contents, so an
    # output dir under REPO_ROOT (e.g. `--output-dir src`) would destroy tracked
    # files or the private export config. The export must go to an external dir.
    if resolved in (Path("/"), Path.home()):
        raise SystemExit(f"refusing to use unsafe output dir: {resolved}")
    if resolved == REPO_ROOT or REPO_ROOT in resolved.parents:
        raise SystemExit(
            f"refusing to use an output dir inside the source repo: {resolved}\n"
            f"choose a path outside {REPO_ROOT} (e.g. /tmp/opw-public)"
        )
    if resolved.exists():
        for child in resolved.iterdir():
            if child.is_dir() and not child.is_symlink():
                shutil.rmtree(child)
            else:
                child.unlink()
    resolved.mkdir(parents=True, exist_ok=True)


def copy_allowlisted(out: Path, manifest: list[str], deny: DenyMatcher) -> tuple[list[str], list[str]]:
    included: list[str] = []
    denied: list[str] = []
    for rel in tracked_files():
        if not manifest_allows(rel, manifest):
            continue
        if deny.denied(rel):
            denied.append(rel)
            continue
        src = REPO_ROOT / rel
        if not src.exists():
            continue
        dst = out / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        included.append(rel)
    return sorted(included), sorted(denied)


def overlay_replacements(out: Path) -> list[str]:
    applied: list[str] = []
    if not REPLACEMENTS_DIR.exists():
        return applied
    for src in sorted(REPLACEMENTS_DIR.rglob("*")):
        if not src.is_file():
            continue
        rel = src.relative_to(REPLACEMENTS_DIR).as_posix()
        dst = out / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        applied.append(rel)
    return applied


def scrub_tree(out: Path, rules: list[tuple[re.Pattern[str], str, str]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    if not rules:
        return counts
    for path in out.rglob("*"):
        if not path.is_file() or not is_text_file(path):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        new = text
        changed = False
        for pat, repl, label in rules:
            new, k = pat.subn(repl, new)
            if k:
                counts[label] = counts.get(label, 0) + k
                changed = True
        if changed:
            path.write_text(new, encoding="utf-8")
    return counts


def scan_tree(out: Path, patterns: list[str], *, ignore_case: bool) -> list[tuple[str, str, int, str]]:
    flags = re.IGNORECASE if ignore_case else 0
    compiled = [(p, re.compile(p, flags)) for p in patterns]
    hits: list[tuple[str, str, int, str]] = []
    for path in sorted(out.rglob("*")):
        if not path.is_file() or not is_text_file(path):
            continue
        rel = path.relative_to(out).as_posix()
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        for lineno, line in enumerate(lines, 1):
            for label, rx in compiled:
                if rx.search(line):
                    hits.append((rel, label, lineno, line.strip()[:120]))
    return hits


def scan_history(patterns: list[str]) -> list[tuple[str, str]]:
    compiled = [(p, re.compile(p)) for p in patterns]
    hits: list[tuple[str, str]] = []
    try:
        proc = subprocess.run(
            ["git", "log", "-p", "--all", "--no-color"],
            cwd=REPO_ROOT, check=True, capture_output=True, text=True,
            errors="ignore",
        )
    except subprocess.CalledProcessError as exc:  # pragma: no cover
        print(color(f"  history scan failed: {exc}", YELLOW))
        return hits
    for line in proc.stdout.splitlines():
        if not line.startswith("+"):
            continue
        for label, rx in compiled:
            if rx.search(line):
                hits.append((label, line.strip()[:120]))
    return hits


def check_required(out: Path, required: list[str]) -> list[str]:
    return [r for r in required if not (out / r).exists()]


# --------------------------------------------------------------------------- #

def ensure_remote(name: str, url: str) -> None:
    existing = {}
    for line in git("remote", "-v").splitlines():
        parts = line.split()
        if len(parts) >= 2:
            existing[parts[0]] = parts[1]
    if name in existing:
        if existing[name] != url:
            print(color(f"  remote '{name}' -> {existing[name]} (expected {url})", YELLOW))
        else:
            print(f"  remote '{name}' already set to {url}")
    else:
        git("remote", "add", name, url)
        print(color(f"  added remote '{name}' -> {url}", GREEN))


# Neutral author for the public mirror's single commit. Using a bot identity
# keeps the operator's real git name/email out of the public repo.
PUBLISH_AUTHOR_NAME = "Zenouz Publish"
PUBLISH_AUTHOR_EMAIL = "zenouz-ai@users.noreply.github.com"


def _git_in(out: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=out, check=check, capture_output=True, text=True
    )


def publish_export(
    out: Path, *, remote_url: str, branch: str, message: str, allow_force: bool
) -> bool:
    """Publish the validated export tree to the public mirror as FRESH history.

    Each publish reinitialises git in the output dir so none of the private
    repo's history is ever pushed. On an existing mirror we update with
    --force-with-lease (safe: it refuses if the remote moved since our fetch).
    Returns True on a successful push.
    """
    # Fresh, single-commit history.
    if (out / ".git").exists():
        shutil.rmtree(out / ".git")
    _git_in(out, "init", "-b", branch)
    _git_in(out, "add", "-A")
    commit = _git_in(
        out,
        "-c", f"user.name={PUBLISH_AUTHOR_NAME}",
        "-c", f"user.email={PUBLISH_AUTHOR_EMAIL}",
        "commit", "-m", message,
        check=False,
    )
    if commit.returncode != 0:
        print(color(f"  commit failed:\n{commit.stderr.strip()}", RED))
        return False
    _git_in(out, "remote", "add", "origin", remote_url)

    ls = _git_in(out, "ls-remote", "--heads", "origin", branch, check=False)
    remote_has_branch = ls.returncode == 0 and bool(ls.stdout.strip())

    if remote_has_branch:
        if not allow_force:
            print(color(
                f"  remote '{branch}' already exists; re-run without --no-force to "
                "update it (force-with-lease).", RED))
            return False
        # Fetch so force-with-lease has a basis: it will refuse if someone else
        # pushed to the mirror since this fetch.
        _git_in(out, "fetch", "origin", branch, check=False)
        push = _git_in(
            out, "push", f"--force-with-lease={branch}:origin/{branch}",
            "origin", f"HEAD:{branch}", check=False,
        )
    else:
        push = _git_in(out, "push", "-u", "origin", f"HEAD:{branch}", check=False)

    if push.returncode != 0:
        print(color(f"  push failed:\n{push.stderr.strip()}", RED))
        return False
    print(color(f"  pushed export to {remote_url} ({branch})", GREEN))
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", default="/tmp/opw-public",
                    help="Where to build the sanitized export.")
    ap.add_argument("--scan-history", action="store_true",
                    help="Also scan git history for secret patterns.")
    ap.add_argument("--ensure-remote", action="store_true",
                    help="Add the public remote if missing (does not push).")
    ap.add_argument("--remote-name", default=DEFAULT_REMOTE_NAME)
    ap.add_argument("--remote-url", default=DEFAULT_REMOTE_URL)
    ap.add_argument("--remote-branch", default="main",
                    help="Branch to publish on the public mirror (default: main).")
    ap.add_argument("--push", action="store_true",
                    help="After a clean validation, publish the export to the public "
                         "mirror as fresh history (force-with-lease on an existing mirror).")
    ap.add_argument("--no-force", action="store_true",
                    help="With --push, refuse to update an existing mirror branch.")
    ap.add_argument("--commit-message", default="Publish Other People's Windows public mirror",
                    help="Commit message for the published export.")
    args = ap.parse_args()

    out = Path(args.output_dir)
    manifest = read_lines(EXPORT_DIR / "manifest.txt")
    deny = DenyMatcher.load(EXPORT_DIR / "denylist.txt")
    required = read_lines(EXPORT_DIR / "required.txt")
    forbidden = read_lines(EXPORT_DIR / "forbidden-content.txt")
    secrets = read_lines(EXPORT_DIR / "secret-patterns.txt")
    scrub_rules = load_scrub(EXPORT_DIR / "content-scrub.txt")

    print(color(f"\n{BOLD}Other People's Windows public mirror export{RESET}", BOLD))
    print(f"  source : {REPO_ROOT}")
    print(f"  output : {out.resolve()}\n")

    if args.ensure_remote or args.push:
        ensure_remote(args.remote_name, args.remote_url)

    clean_output(out)
    included, denied = copy_allowlisted(out, manifest, deny)
    replaced = overlay_replacements(out)
    scrub_counts = scrub_tree(out, scrub_rules)

    missing = check_required(out, required)
    forbidden_hits = scan_tree(out, forbidden, ignore_case=True)
    secret_hits = scan_tree(out, secrets, ignore_case=False)

    # ---- report ----
    print(color(f"{BOLD}Included ({len(included)} files){RESET}", BOLD))
    for rel in included:
        print(f"  + {rel}")
    print(color(f"\n{BOLD}Denied by denylist ({len(denied)} files){RESET}", BOLD))
    for rel in denied:
        print(f"  - {rel}")
    print(color(f"\n{BOLD}Replacements overlaid ({len(replaced)}){RESET}", BOLD))
    for rel in replaced:
        print(f"  ~ {rel}")
    print(color(f"\n{BOLD}Content-scrub substitutions{RESET}", BOLD))
    if scrub_counts:
        for label, k in scrub_counts.items():
            print(f"  * {k:>3}x  {label}")
    else:
        print("  (none)")

    history_hits: list[tuple[str, str]] = []
    if args.scan_history:
        print(color(f"\n{BOLD}Scanning git history for secret patterns...{RESET}", BOLD))
        history_hits = scan_history(secrets)
        if history_hits:
            print(color(f"  {len(history_hits)} secret-pattern hit(s) in history (mirror is "
                        f"published without history; review anyway):", YELLOW))
            for label, snippet in history_hits[:40]:
                print(color(f"    ! {label}: {snippet}", YELLOW))
        else:
            print(color("  no secret patterns found in history", GREEN))

    print(color(f"\n{BOLD}Validation{RESET}", BOLD))
    ok = True
    if missing:
        ok = False
        print(color(f"  MISSING required files ({len(missing)}):", RED))
        for r in missing:
            print(color(f"    x {r}", RED))
    else:
        print(color("  required files: all present", GREEN))

    if forbidden_hits:
        ok = False
        print(color(f"  FORBIDDEN content hits ({len(forbidden_hits)}):", RED))
        for rel, label, lineno, snippet in forbidden_hits[:60]:
            print(color(f"    x {rel}:{lineno}  [{label}]  {snippet}", RED))
    else:
        print(color("  forbidden-content scan: clean", GREEN))

    if secret_hits:
        ok = False
        print(color(f"  SECRET pattern hits ({len(secret_hits)}):", RED))
        for rel, label, lineno, snippet in secret_hits[:60]:
            print(color(f"    x {rel}:{lineno}  [{label}]  {snippet}", RED))
    else:
        print(color("  secret-pattern scan (tree): clean", GREEN))

    print()
    if ok:
        print(color(f"{BOLD}RESULT: export is clean and safe to publish.{RESET}", GREEN))
    else:
        print(color(f"{BOLD}RESULT: export FAILED validation — do not publish.{RESET}", RED))

    if args.push:
        print(color(f"\n{BOLD}Publish{RESET}", BOLD))
        if not ok:
            print(color("  refusing to push: validation failed.", RED))
            return 1
        if history_hits:
            print(color("  refusing to push: secret patterns found in git history "
                        "(re-run without --push, review, and resolve first).", RED))
            return 1
        pushed = publish_export(
            out,
            remote_url=args.remote_url,
            branch=args.remote_branch,
            message=args.commit_message,
            allow_force=not args.no_force,
        )
        if not pushed:
            return 1

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
