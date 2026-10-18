# Faster historical joint-frame rank verification

**Tooling improvement; no new kappa.** This opt-in adapter accelerates the
complete historical `audit_joint_frames.certificate()` by certifying full
rational rank with exact elimination modulo 101. Every deficient modular
result, and every denominator divisible by 101, goes to the original
rational elimination routine. There is no approximate rank decision.

Seven alternating fresh-process A/B pairs on the recorded Linux/Python
environment gave the following medians. These measurements include source
admission, imports, the complete certificate, its exact comparison and
per-run count recording; they do not time a selected-frontier reconstruction.

| Complete historical certificate | Reference | Screened |
| --- | ---: | ---: |
| Wall seconds | 1.952577 | 1.701918 |
| Child CPU seconds | 1.949693 | 1.701471 |

This is **12.8% less median wall time**, or 1.147x speedup, for this workload
and environment. One of the seven individual pairs was slower. All samples
are retained in `RESULT.json`; timing is not a correctness gate and there
is no claim of a universal speedup, new search throughput or practical
integer-multiplication speedup. The initial exploratory pair, before input
validation and the complete harness, was 1.7548 -> 1.5152 seconds and is
not the benchmark used in the table.

## Reproduce

From a full checkout, using Python 3.11+ and the standard library on Linux
or macOS:

```sh
python3 -I -B research/joint-frame-modular-screen/verify.py --pairs 7 --output /tmp/joint-frame-rank-result.json
```

Choose a fresh output filename. Expected final marker:
`PASS_JOINT_FRAME_MODULAR_SCREEN`. The command runs 12 focused test groups,
the unchanged eight-test historical suite in both engines, every actual
rank comparison, an optimized-interpreter rejection control, and all
fourteen timed full-certificate replays. The final JSON includes every
sample, environment, source-manifest hash and implementation hashes.
Use an interpreter with assertions enabled; the adapter rejects `-O`
because assertions in inherited source code must stay active.

To run only the faster complete certificate:

```sh
python3 -I -B research/joint-frame-modular-screen/replay.py
```

The printed certificate must have SHA-256
`b7686b518e4e677ca5e6f92066a41255bd696abae6c7b0c4f09d11eb6e8bdffd`.
It is byte-identical to the committed `certificates/joint-frame-audit.json`
at the base commit; the adapter never writes that original file.

## Coverage and interpretation

* All **2,644** uncached rank calls in the complete certificate agree
  individually with the original rational routine. **752** are certified
  by the fast path and **1,892** use the original fallback. The existing
  outer rank cache is retained for both engines.
* A separate determinant/minor implementation checks all **530** binary
  square matrices of dimensions 1, 2 and 3. Seed 85 generates **240**
  additional exact rational matrices of dimensions 1 through 12, with
  rectangular, duplicate-row and zero-column controls. This campaign is
  bounded testing, not an exhaustive claim about larger matrices.
* Four deliberately incorrect kernels are detected by numeric
  counterexamples. Additional controls cover exceptional denominators,
  full rank lost on reduction, row swaps, empty shapes, large integers,
  unsupported input types, unchanged inputs and source/certificate drift.
* The complete historical certificate retains all 2,042 physical edges,
  the h=6 rank total 1,292, the twelve h=10 rational controls, and the
  published h=50 accounting total 27,388,000. The original scalar and
  dirty-scratch tests run unchanged in both engines.

`PROOF.md` gives the exact algebraic implication that makes the fast path
safe. `SOURCE.json` pins all 36 original source/data/test files admitted
by the harness with both SHA-256 and Git blob IDs. It also records the
base and upstream commits; attribution files have separate informational
pins and do not block replay on unrelated notice edits.

## Scope, source and coordination

Exact base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
OS-random assignment seed: **85**, verification engineering. `CLAIM.json`
records three candidates, the selected narrow scope, overlap inspection
and the local claim/result. No pinned sprint coordination issue was found;
the session had public GitHub reads but no authorized write connection.

The selected certificate was traced to the #626 construction and review,
with #543, at kappa `51110230636731/31250000000000000`. This package instead
improves the older fixed-boundary audit. It does not reopen the already
closed internal-frame optimization class or claim a stronger bound.

Only this research package is added. Original scripts, frozen artifacts,
default verification commands, the selected frontier and `upstream/`
remain unchanged. The focused historical replay/tests and the selected
record binding check are the applicable checks. The repository-wide
`make verify`, selected cold supplier replay and Lean builds were not
rerun; no result from those suites or from hosted CI is claimed.

All-size/compiler, common-label/mutable-basis realization, pooled hosting,
normalized residual, precision/tape and analytic-transfer assumptions of
the selected theorem remain inherited and unresolved here. Finite replay
and this written rank argument are not a formal proof of multiplication.
See `NOTICE.md` for predecessor credit and substantial AI-assistance disclosure.
