# auto-research/

The standard home for new agent-driven research packages. The proposed name is meant to be reused across auto-research repositories, so that agents find the same layout everywhere. Agent instructions: [../auto-research.md](../auto-research.md).

## Layout

One directory per submission:

```
auto-research/<YYYY-MM-DD>-<handle>-<short-slug>/
```

Required files:

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

`research/` keeps every existing package unchanged, because more than 1,600 files pin its paths. New packages should go here. A later, separately reviewed change can add a cross-index or migrate packages once their pins are updated.
