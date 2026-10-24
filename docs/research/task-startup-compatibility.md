# Task startup and frozen-input compatibility

At canonical main `624de9dc66858af0945e5f8a0942488d62280d43` (priority revision 7),
16 of 22 task cards emit `python3 -B scripts/research_baseline.py` as their first
step. The catalogue's `selection_context.orientation_command` and current
priorities already name `research_selected_baseline.py`; the picker does not
include `selection_context` in its output. Following a card alone therefore
reaches the historical certificate schema.

Use the [standing procedure's generic-command substitution](agent-procedure.md#1-orient-briefly-then-choose-a-distinct-task).
It routes current contributors to the existing source-bound successor while
leaving frozen cards, helpers and scientific commands unchanged. This is a
navigation repair and scoped dependency audit, not a new certificate adapter,
research priority, supplier or kappa claim.

## Exact dependency boundary

The inventory below covers every tracked top-level `research/*/SOURCES.json`
and `research/*/VERIFY.json` at that base: **5,854 files**, each checked against
its Git blob. Counts refer to exact repository paths in standard manifest fields.
Nested vendor manifests, code imports, archives and undeclared reads are outside
this audit. A provenance pin reads historical Git bytes; a live input pin checks
working bytes. A declared replay input selects a package when the path changes,
even if its source pin is only provenance.

| Path | Live `input` rows | `provenance` rows | Declaring `VERIFY.json` files |
| --- | ---: | ---: | ---: |
| `docs/research/agent-task-catalog.json` | 16 | 2,676 | 57 |
| `scripts/choose_research_task.py` | 1 | 8 | 1 |
| `scripts/research_baseline.py` | 6 | 4 | 7 |
| `docs/research/agent-procedure.md` | 0 | 3 | 0 |

The catalogue's 16 live pins already differ from the catalogue bytes at this
base. Their existence is **not** evidence that this proposed change newly breaks
16 passing packages. Editing the catalogue would nevertheless select 57 declared
dependents, requiring a separate compatibility decision. The procedure has only
historical provenance pins in this inventory, so this repair changes that active
guide and adds this note. No source receipt is rewritten or silently repinned.

For example, the catalogue is a live input in
[`clean-selector-embedding/SOURCES.json`](../../research/clean-selector-embedding/SOURCES.json),
whereas the procedure is provenance in
[`p104-newton-interfaces/SOURCES.json`](../../research/p104-newton-interfaces/SOURCES.json).
The substring reference in `kappa-rebuild/SOURCES.json` names its separate
`provenance/public-final/docs/research/agent-procedure.md` copy, not the live guide.

## Reproduce the inventory

From a checkout containing the pinned base, run this Python snippet. It reads
committed objects, so sparse files need not be materialized; a partial clone may
fetch the required blobs. It does not execute research packages. Git replacement
objects are disabled for these reads.

```python
import io, json, subprocess

BASE = "624de9dc66858af0945e5f8a0942488d62280d43"
TARGETS = ["docs/research/agent-task-catalog.json",
           "scripts/choose_research_task.py", "scripts/research_baseline.py",
           "docs/research/agent-procedure.md"]
def git(*args, **kwargs):
    return subprocess.check_output(["git", "--no-replace-objects", *args], **kwargs)

entries = []
for entry in git("ls-tree", "-r", "-z", BASE).split(b"\0"):
    if not entry:
        continue
    metadata, name = entry.split(b"\t", 1)
    parts = name.decode("utf-8").split("/")
    if (len(parts) == 3 and parts[0] == "research"
            and parts[2] in {"SOURCES.json", "VERIFY.json"}):
        entries.append((name.decode("utf-8"), metadata.split()[2]))
stream = io.BytesIO(git("cat-file", "--batch",
                       input=b"".join(oid + b"\n" for _, oid in entries)))
counts = {p: {"input": 0, "provenance": 0, "declared": 0} for p in TARGETS}
for name, oid in entries:
    actual, kind, size = stream.readline().split()
    if actual != oid or kind != b"blob":
        raise ValueError("Unexpected Git object: " + name)
    data = json.loads(stream.read(int(size)))
    if stream.read(1) != b"\n":
        raise ValueError("Invalid Git batch framing")
    if not isinstance(data, dict):
        continue
    for target, result in counts.items():
        if name.endswith("/VERIFY.json"):
            result["declared"] += target in data.get("inputs", [])
        elif isinstance(data.get("files"), list):
            for row in data["files"]:
                if isinstance(row, dict) and row.get("path") == target:
                    usage = row.get("usage")
                    if usage in {"input", "provenance"}:
                        result[usage] += 1
print(json.dumps({"base": BASE, "manifests": len(entries), "paths": counts}, indent=2))
```

## Evidence and remaining work

The selected #4470 closure passes the existing source checker. On those same
authenticated inputs, the historical command fails with `KeyError: 'bit_lower'`;
the successor passes in ordinary and optimized Python with identical reports.
The result remains `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`. Existing selected
baseline controls pass 13 tests, and assignment controls pass 16 tests on native
Windows / CPython 3.12.0. All eight coordination tests pass with `-X utf8`; the
default cp1252 run has one existing `read_text()` decoding error on
`autoresearch.md`. The exact inventory snippet reproduces the table from Git
objects, independently of the working-file/blob comparison. The registered
package planner selects zero packages for the two changed documentation paths
and 57 for a hypothetical catalogue edit. No mathematical cold replay, broad
historical replay or Lean build was run.

**Open next question:** migrate the 16 emitted generic commands after an explicit
decision on the 57 declared dependents. Start with the exact-path inventory above,
distinguish existing drift from a new incompatibility, and preserve each package's
original task and source history. This matters because callers of the picker that
skip the standing procedure will still see the historical command. Hidden runtime
dependencies remain a blocker to claiming a complete compatibility migration.

This refines `scope-navigation`, selected with nonce
`cc0ba7957f5aa29a9b8e5a07a7a6ec93`, and continues the migration handoff in
[Discussion #4458](https://github.com/CrocSwap/integer-mult-bounds/discussions/4458#discussioncomment-19134442).
Credit Douglas Colkitt and retained onboarding/source-checker contributors;
Mihir Srivastava / [#4463](https://github.com/CrocSwap/integer-mult-bounds/pull/4463)
for the productive-helper adapter; lee-phys /
[#4631](https://github.com/CrocSwap/integer-mult-bounds/pull/4631) for schema-aware
sparse diagnosis; and Mister-Meeseeks / the credited Claude agent in
[#3725](https://github.com/CrocSwap/integer-mult-bounds/pull/3725) for the
immutable-helper precedent. Scientific sources retain the selected contributor
map's attribution. Prepared by Mihir Srivastava with substantial OpenAI Codex
assistance; no subagents. Apache-2.0.
