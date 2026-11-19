# Public repository scope

This repository is a curated public mirror of a private working repository. The private repository stays the source of truth; this one is rebuilt from it by `scripts/publish_public_mirror.py` and pushed as a fresh, single commit, so no private history is ever published.

## In the public mirror

| Path | Why it is public |
|---|---|
| `pipeline/` | All the code: prompt building, generation, checks, looping, the film renderer |
| `scenes/scenes.yaml` | Every window's prompt parts, model, loop settings and making-of notes: the record the findings rest on |
| `layouts/` | The page layouts and camera timing of each film |
| `docs/FINDINGS.md`, `docs/ARCHITECTURE.md`, this file | Written for the public mirror |
| `docs/batch-02.md`, `docs/batch-04.md`, `docs/batch-05.md` | Generated batch briefs with every prompt |
| `docs/batch-04-scorecard.md`, `docs/batch-05-scorecard.md` | Measured scorecards of every candidate and take |
| `docs/assets/` | A few page stills and one close-up, for the README |
| `scripts/publish_public_mirror.py`, `public-export/manifest.txt`, `denylist.txt`, `required.txt`, `secret-patterns.txt` | The publishing framework itself |
| `requirements*.txt`, `LICENSE`, `README.md`, `.gitignore` | Set-up and licence |

## Kept private

| Class | Examples | Why |
|---|---|---|
| Media | Stills, raw takes, loops, renders | Large, and the artwork is not licensed for reuse; the films are published on YouTube and zenouz.ai |
| Keys and accounts | `.env`, provider account details | Credentials |
| Spend ledger | `media/generate-ledger.jsonl` | Account-level billing detail; the findings give the totals |
| Production notes and plans | Daily log, roadmap, batch plans | Working notes with personal and account details; their findings are summarised in `docs/FINDINGS.md` |
| Assistant context | `docs/ARCHITECTURE.md` | Operating notes for the coding assistant used to build the pipeline |
| Private identifiers | Personal email addresses, home paths, the private repository name | Privacy |
| Archived planning PDFs | The first production pack | Superseded, with out-of-date numbering |

## How a publish works

1. List the files tracked in the private repository.
2. Keep only paths matched by `public-export/manifest.txt` (an allowlist).
3. Drop anything matched by `public-export/denylist.txt`, even inside an allowed folder.
4. Overlay the public versions written in `public-export/replacements/` (this README, the docs, the licence).
5. Apply export-time text substitutions (a private file, `content-scrub.txt`), for example pointing references to private docs at public ones.
6. Check that every file in `public-export/required.txt` exists.
7. Scan every exported text file for private identifiers (a private list) and for secret patterns (`secret-patterns.txt`); any hit blocks the publish. With `--scan-history`, also scan the private repository's history for secrets.
8. With `--push`, commit the tree as a single fresh commit by a neutral identity and push it; later publishes replace it with `--force-with-lease`.

The private identifier list and the substitutions are themselves private, because they would publish the very strings they exist to keep out.
