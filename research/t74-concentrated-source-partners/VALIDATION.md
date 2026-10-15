# Validation of the PR2673 composition

All results below concern the exact submitted late8 words, the authenticated
PR2673 hosting files and the code bound in `evidence/FULL-RESULT.json`.
The complete fresh public replay passed on 2026-10-15. Its three wrapper
stages took 1110.96 seconds (18.52 minutes), including a complete
fresh predecessor release. No externally supplied baseline or native receipts
were accepted. The final multiplication exponent remains conditional.

## Environment and commands

Python 3.12.14 on macOS 26.5.1 arm64; Apple clang 21.0.0; Boost 1.87.0 headers;
NumPy 2.3.5, SymPy 1.14.0 and mpmath 1.3.0. `gmpy2` was absent.
`ENVIRONMENT.json` records the literal environment and invocation.
The local checkout was `1884c509efc004524786e9b7cfcc4aca572316d5` plus this
new package. Source archives were exported from exact PR2462 and PR2588 Git
commits by `fetch_sources.py`; their complete inventories and every source
byte were authenticated before and after replay. The seven retained PR2673
files are separately authenticated against their exact head and Git blobs.

The actual full command, from the repository root, was:

```sh
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPYCACHEPREFIX=/tmp/kappa-round2/final2673-cold-cache \
PYTHONINTMAXSTRDIGITS=0 \
CPLUS_INCLUDE_PATH=/tmp/kappa-search/boost_1_87_0 \
/tmp/kappa-venv/bin/python -B \
  research/t74-concentrated-source-partners/full_replay.py \
  --sources /tmp/kappa-round2/publication-sources \
  --main . --work /tmp/kappa-round2/final2673-cold
```

The full wrapper sets fresh bytecode namespaces for subprocesses and disables
inherited discovery/optimization flags. It reproduces the complete PR2530 and
PR2588 word payloads before generating both new words. The final generated
payloads equal the submitted candidates in every JSON field.

## Full finite replay

The fresh PR2588 release completes all 14 named stages in its result,
including its retained-provider/parent admission and both fresh predecessor
native pipelines. The changed candidate then completes these 13 stages:

| Stage | Seconds | Exit code |
| --- | ---: | ---: |
| reconstruct | 3.79 | 0 |
| lift | 4.69 | 0 |
| native-base | 138.76 | 0 |
| native-extra | 137.00 | 0 |
| rebuild-borrow | 39.79 | 0 |
| rebind | 0.54 | 0 |
| lemma-g | 19.51 | 0 |
| discover | 67.23 | 0 |
| strict | 66.28 | 0 |
| geometry | 0.39 | 0 |
| outer-ledger | 0.08 | 0 |
| outer-independent | 0.07 | 0 |
| outer-replay | 23.78 | 0 |

Both changed natives complete native lowering, ledgers, local replay,
wrappers and phases. Strict assembly reconstructs ownership and global
geometry, checks adapters and the complete physical invoice, and consumes
the changed provider profiles. The final inventory is 66,814 physical
registers, including 78 dedicated zero buffers, and rank mass 4,816,512.
The outer ledger has 63 strictly positive exact rational checks. The separate
balance derivation agrees on the rational κ; all 19 outer replays pass.
`OUTER-REPLAY.log` retains the successful outer and 19-replay summaries. The
inherited replayer compares every regenerated proof-relevant JSON artifact with
its pinned source, then removes its temporary outputs. `FINE-PADDING.json`
retains the separately regenerated finite arithmetic controls.

Primary results are retained as raw output bytes. `RECEIPT-FILES.json` lists
their SHA-256 hashes; `FULL-RESULT.json` additionally binds required receipts,
all local execution code and inputs, source manifests, stages and logs.
The evidence checker requires the complete execution-input inventory and
exactly 13 candidate, 3 wrapper, 5+5 changed-native and 14 predecessor stages.
It does not substitute those stored statuses for a fresh native replay.

## Bounded publication replay and controls

The registered command was run after attaching the final raw receipts:

```sh
/tmp/kappa-venv/bin/python -B scripts/research_package.py \
  --package research/t74-concentrated-source-partners
```

`verify.py` independently represents binary subspaces as full finite sets and
uses free noncommuting chart operators. It checks all 646 independent input
columns in both orientations for each provider, every frame and source handoff,
the twelve targets, all 4,529 cleanup events, the actual width-class helper
permutation and matched endpoint dimensions. It recomputes both old and new
281,052-role allocations against strict windows, capacities, distinct physical
families and contiguous prefixes. It reconstructs the complete old profile,
proves the exact new histogram delta, and brackets the moment with rational
intervals. The published bracket and both profiles must match these results.

The six mathematical controls reject a wrong prelude sign, missing cleanup,
uncharged centre, missing owner role, outside-window role and duplicate physical
family. `check_evidence.py` rejects ten empty/truncated/reordered-stage,
noninteger-exit and changed-receipt mutants. The final bounded receipt is
`evidence/BOUNDED.json`; registered output is `evidence/REGISTERED-REPLAY.log`.
An independent directed fixed-point engine also confirms the bracket; its
record is `evidence/INDEPENDENT-FINE-MOMENT.json`.

The complete publication verifier also passed from a Git-free, read-only copy
with empty PATH and a fresh bytecode namespace. The copy remained byte-identical.
Optimized Python and occupied output paths reject; the occupied file remains
unchanged. Corrupt source code, a changed candidate word and changed hosting
bytes reject. `evidence/EXPORT-CONTROLS.json` records these seven checks, including both read-only verifier commands.

During development, the inherited target-swap mutant turned out to commute two
identical additions. Its replacement chooses distinct sources at the same
frame; the nonzero residual is explicitly derived and both providers reject.
Both providers' complete 24-control results are retained. A separate inherited
target-frame mutant rejected correctly but had a stale expected diagnostic;
that string was updated. The original failures and regression explanations are
preserved under `evidence/mutation-regression/` and `evidence/diagnostic-regression/`.
These changes do not relax a mathematical acceptance predicate.

## Boundaries of this evidence

The mathematical gain is an exact symbolic finite construction and strict
moment inequality, not a test of a range of integer sizes. Complete finite
native/global/outer execution is author-checked evidence, not maintainer
acceptance or proof-assistant verification. The main selected record is not
changed. The main-selected historical cold suite was not rerun; this is the
applicable pinned pending PR2588 chain and the new construction.

All-size compiler and common-label/mutable-source realization, whole-call
physical hosting, precision/tape, exact recovery, analytic transfer, recurrence
and bit H1–H5 premises remain inherited. No unconditional multiplication theorem,
measured practical speedup, global optimum or exhaustive search is claimed.
