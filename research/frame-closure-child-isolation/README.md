# Fresh imports throughout the frame-closure caller

This opt-in adapter authenticates the existing frame-closure caller and gives
its parent and all eight nested Python interpreters distinct fresh default
import-cache namespaces. All six complete engine receipts, all 6,477 closure
entries, 1,156 enumerated assignments and nine inherited test groups remain
checked. The optimized-rejection grandchild remains an expected failure.
No frozen source, selected result or mathematical assertion is changed.

## Why this is a separate boundary

[PR2553](https://github.com/CrocSwap/integer-mult-bounds/pull/2553), pinned at
`a82fea84445e54042fa56b39ff1509fa329fad93`, gives each registered interpreter a
fresh `-X pycache_prefix` and explicitly excludes separately launched children.
Its source-boundary argument and eight regression groups are credited, not
recounted here as new work. The retained note is in `source/`.

The actual caller is `research/bit-frame-closure-basis/verify.py`. It authenticates
`closure.py` through its benchmark receipt, imports that helper through `run.py`,
then launches six `-I -B run.py` processes and one `-I -B test_closure.py`
process. That test process launches an eighth `-I -O -B run.py` process to check
assertion-policy rejection. Neither interpreter command inherits the parent's
`-X` option. `-B` suppresses cache writes but does not disable cache reads;
`-I` also ignores `PYTHONPYCACHEPREFIX`.

The regression is deliberately benign. In a disposable copy only, compile
`closure.py` with its numeric `PRIME` value changed from 2,147,483,647 to
2,147,483,629, then restore the exact original source bytes and timestamp.
A numeric observer reports the prior value from matching timestamp or
unchecked-hash bytecode. A fresh explicit namespace reports the current value.
Checked-hash bytecode already invalidates correctly. No fixture bypasses a
verification check or terminates a verifier. This demonstrates a source/execution
consistency gap, **not acceptance of an invalid mathematical certificate**.

## Exact adapter contract

`SOURCES.json` binds 15 original runtime files at canonical main
`1884c509efc004524786e9b7cfcc4aca572316d5`. Every original runtime source is
authenticated before any transformed source executes. The selected record and
catalogue are historical provenance, not runtime dependencies.

`replay.py` parses authenticated originals in memory and changes only:

1. The two `subprocess.run` callsites in `verify.py` and the single callsite in
   `test_closure.py`, routing those calls through `isolated_child`.
2. The single `str(ROOT / path)` input-argument expression in `run.py`, replacing
   it with `(ROOT / path).as_posix()`.

The second change is a native Windows compatibility prerequisite for this exact
consumer. The frozen checker derives a display basename with `rsplit('/')`.
Without it, the actual Windows receipt differs only at `receipt.word` and the
corresponding `stdout_sha256`. The adapter passes the same existing file with
forward-slash spelling, so the **entire original expected JSON and stdout hash**
are checked without exclusions or replacement receipts. It does not rewrite
any input bytes or post-process a report.

Only the source's `-I -B` and `-I -O -B` forms and its exact `run.py` or
`test_closure.py` targets are accepted. Script arguments and all original
subprocess keyword arguments pass through unchanged. Each call owns a fresh
temporary cache until that synchronous call returns or raises; context cleanup
then removes it. The parent also owns a fresh namespace before importing any
original helper. The grandchild keeps `-O`, so the source's explicit rejection
still runs. Source compilation uses `optimize=0`, preserving inherited assertions.

The full replay records the numeric value imported by all nine interpreters,
requires the pinned current value, checks eight distinct child namespaces plus
the parent namespace, and checks successful cleanup. It requires seven normal
child returns and the one expected optimized rejection. These observations are
additional evidence; the unchanged mathematical caller still decides its own
complete receipts, closure inventories and rational/control assertions.

## Reproduce

Use CPython 3.12 and a writable temporary directory:

```text
python -B scripts/research_package.py --package research/frame-closure-child-isolation
```

The registered primary replays the full consumer. Four additional test groups
cover benign timestamp/unchecked/checked-hash numeric observations, the exact
child command grammar and optimization flags, rejection of changed current
source, and a complete Git-free export under an optimized parent with prior
numeric bytecode present. The export retains all nine original test groups and
requires exact equality with `RESULT.json`; original source bytes remain intact.
`PATH` is empty for that export. No measured speedup is claimed.

The first clean native CPython 3.12.7 full replay passed. Final registered replay
and independent review details are recorded in `TASK.json` and the PR.

## Scope and decision

Revision5 decision: narrow the assigned source-bound cache/replay audit to this
already registered consumer. The acceptance gap is authenticated-source versus
executed-module consistency, not a new kappa. Source authentication, the nine
import namespaces, original comparison coverage and synchronous cleanup are
constructively checked here. Cache-directory overhead is unpriced; no performance
claim or supplier invoice follows.

The guarantee covers this normal adapter entrypoint and this fixed caller tree.
It is not a general security boundary. Explicit external `--child` invocations,
preloaded modules from non-isolated startup, custom import loaders, standalone
bytecode, concurrent file mutations and arbitrary additional descendants are
outside scope. The original loader's source-read/execute race is not repaired.
No repository-wide test run, selected cold replay, native supplier, all-size
multiplication theorem or new kappa is claimed.

## Attribution

Ross Richardson's frame-closure adapter and Seth Burkart's PR886 closure contract
and Hadamard guard supply the mathematical checks. The retained PR589/PR555
fixtures and their source lineage remain unchanged. PR2553 supplies the prior
registered-interpreter cache-isolation result and explicit child-process handoff.
This contribution was prepared for ywz65 with substantial OpenAI Codex assistance,
including separate agent review; it is not an independent human or formal-kernel
review. Apache-2.0.

## Open next questions

Which other actual registered callers launch Python descendants without an
explicit cache boundary? Audit one concrete command chain and reproduce a benign
source/executed-value difference before changing it. This package does not
inventory arbitrary descendants or justify a generic runtime expansion.
