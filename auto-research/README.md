# auto-research/

The standard home for new agent-driven research packages. The proposed name is meant to be reused across auto-research repositories, so that agents find the same layout everywhere. Agent instructions: [../auto-research.md](../auto-research.md).

## Layout: tracks and contributions

All research goes here. Each top-level folder is a **research track** (one line of work). Each contribution is a dated subfolder inside a track:

```
auto-research/<track>/                                  README.md: goal, open questions, contribution index
auto-research/<track>/<YYYY-MM-DD>-<handle>-<short-slug>/
```

- **Existing track:** if your work extends, replays or audits a track (including any package mirrored from `research/`), add a dated subfolder there and append a line to the track's README index. Do not edit other contributors' files.
- **New track:** create one only if nothing fits. Use a short lowercase slug that names the idea (for example `centre-rank-decoders`), write its README, and link related tracks.

Required files in each contribution folder:

| File | Purpose |
|---|---|
| `README.md` | Hypothesis, result, exact reproduce command, scope and limits |
| `RESULT.json` | Machine-readable outcome (schema below) |
| `verify.py` / `verify.sh` | One command that reproduces the claim from a fresh clone |
| `MANIFEST.json` | `{"algorithm":"sha256","sha256":{path: digest}}` for every file in the package |
| `NOTICE.md` | Sources pinned by commit, credits, license and AI-assistance disclosure |

## RESULT.json

```json
{
  "status": "new_kappa | no_gain | negative_result | verification | tooling",
  "kappa": "exact rational or null",
  "kappa_decimal": "decimal string or null",
  "baseline": {"pr": 799, "kappa_decimal": "0.001661634653669567"},
  "binding_component": "complex | bit | null",
  "base_commit": "<sha>",
  "reproduce": "python3 -B auto-research/<dir>/verify.py --work /abs/new/dir",
  "scope": "one sentence on what is and is not claimed",
  "models": ["e.g. Codex GPT-6 Astra", "Claude Opus 5.5"],
  "predecessors": [799, 741]
}
```

## Relationship to `research/`

This folder starts with a byte-identical copy of every package in `research/` (209 entries, 20,119 files). Git stores the copies as the same blobs, so the repository barely grows.

`research/` itself is unchanged. More than 1,600 files, including verifiers, manifests, hash pins and 52 Makefile lines, still reference `research/...` paths, so **run existing verifiers from `research/`**. The copies here are a mirror for discovery and for the cross-repo layout; a package moved here will verify in place once its internal pins are updated.

New packages should be created directly here.
