# Validation receipt

Platform: Linux x86_64, CPython 3.11.13. Source base:
`66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Executed during the October 12, 2026 Pacific research sprint.

| Check | Observed result |
|---|---|
| `python3 -I -B research/jp8-compensation-batching/verify.py` | Full forward/backward primitive scalar replay; 716 native + 9 arbitrary private columns; savings 80,150/81,464; all ten controls rejected |
| Same verifier under `-O` | Identical certificate and result; checks use explicit exceptions |
| `python3 -I -B research/jp8-compensation-batching/independent.py` | Separate integer/dyadic replay on 717 panel input columns; 20,122/18,808 real primitives; all twelve controls rejected |
| Independent receipt regenerated and compared | Exact equality with committed `INDEPENDENT.json`; also passed under `-O` |
| `native_replay.py --output <new scratch directory>` | Unchanged inherited emitter/auditor pass both native orientations, 716 columns and 25 existing controls; all non-panel events unchanged |
| Native driver under `PYTHONOPTIMIZE=2 python3 -O` | Assertion-enabled children still run; byte-identical semantic `NATIVE.json` receipt |
| Native output preservation | Existing output directory rejected without modifying its receipt |
| Minimal relocated checkout, path containing spaces, invoked from `/tmp` | Main verifier and independent checker both pass under `-I -O -B` using only the new package and seven pinned inputs |
| Recompressed source inputs in relocated checkout | Both gzip inputs recompressed at level 1 with different timestamp; both checkers pass and independent receipt remains identical |
| `make selected-record-check` | Selected record, source inventory and proof-supplement checks pass |
| `ruff check research/jp8-compensation-batching/*.py` | Pass |
| Staged whitespace and scope | `git diff --cached --check` passes; only the new research package is staged |

The main controls cover missing initial/final clear, incorrect accumulation
sign, omitted target update, a write to a protected source, an invalid
dyadic step, a scalar-preserving work-prefix excursion, a nonzero-frame
compensation gate, crossing the precondition boundary, and substitution of
the forward panel for the backward one. Independent controls use separate
integer arithmetic, include arbitrary incoming private work, and distinguish
endpoint equality from a prefix-cap failure.

Two separate AI workers checked the mathematics and integer/dyadic panel
implementation; a third performed an adversarial review and optimized
replays. No independent human review is claimed. See `NOTICE.md`.

The complete repository `make verify`, selected cold supplier rebuild,
global hosting/invoice/outer admission, Lean, and remote CI were not run as
part of this isolated local-lowering contribution. No existing generator,
supplier, frontier pointer or `upstream/` file changes. Native replay is
specifically a macro-order/frame check, not an admission of the new private
work clearing boundary into production.
