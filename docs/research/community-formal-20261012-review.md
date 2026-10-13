# Lemma G, Lemma A and allocation tooling integration

Douglas Colkitt with OpenAI Codex assistance, 2026-10-12 UTC.

This batch incorporates **DaysSky's #442**, **DreamingOfClouds' #484, #509 and
#516**, and **higherbeing's #520**. It strengthens the recorded verification
and preserves useful research tools. The selected conditional result remains
**κ = 0.001517760977820331**, from #531/#523 with #493.

Exact reviewed heads, source hashes and execution receipts are in the
[integration record](community-formal-20261012-integration.json). The
[central PR ledger](pr-ledger.md) separates these dispositions from unreviewed
and subsequently changed submissions.

## What was checked

| PR | Contribution | Maintainer validation |
|---|---|---|
| [#442](https://github.com/CrocSwap/integer-mult-bounds/pull/442), DaysSky | Idle-axis hosting and its stream-model construction | Full fresh parent reconstruction and hosting, independent audit and exact assembly, through #484's cold dependency run |
| [#484](https://github.com/CrocSwap/integer-mult-bounds/pull/484), DreamingOfClouds | Compatible entrance gauges, shared-donor kernels and normalized residual wrappers | Complete `--all` replay: headline, gauge-only, kernel-only and anchor; scalar identities, phases, exact labels, instance identities, end-to-end checks and mutation controls |
| [#509](https://github.com/CrocSwap/integer-mult-bounds/pull/509), DreamingOfClouds | General labeled-stream conjugation and entrance-gauge lemmas | Lean build and 16 named theorem axiom reports; extended-label and adapter hypotheses checked on all four freshly emitted words |
| [#516](https://github.com/CrocSwap/integer-mult-bounds/pull/516), DreamingOfClouds | Physical realization in the stated stream model, spectators, owners and commuting windows | Lean build and 24 named theorem axiom reports; exact-wrapper, owner and window hypotheses checked on all four words, with negative controls |
| [#520](https://github.com/CrocSwap/integer-mult-bounds/pull/520), higherbeing | Open whole-owner allocation search and delivery/frame-chain diagnostics | Source review, corrected solver failure handling, conservation/nomination regressions, and exact reproduction of the #433/#484 delivery and plane reports |

The Lean packages use Lean 4.21.0 and Mathlib commit
`308445d7985027f538e281e18df29ca16ede2ba3`. All 40 named theorem reports use
only subsets of `propext`, `Classical.choice` and `Quot.sound`. Source scans
and manifest checks pass. The two imported formal packages and the seven-package
construction/formal dependency stack are unchanged from the reviewed #516 tree.

The construction and finite hypotheses are checked by Python; the abstract
theorems are checked by Lean. This distinction matters. Exact recipes, valid
labels, scalar rows, factorization and disjoint/commuting ownership are explicit
hypotheses of the formal results. Lemma A works in #442's stream model; the
claim that this model describes the fixed-tape machine remains inherited.
Private center copies have their stated initial conditions; the formal results
do not silently supply an arbitrary-workspace theorem for every register kind.

These are **not** complete formal proofs of integer multiplication or the
selected #531 witness. The finite instance checkers here use #484's 120-port
family, whereas #531 has 112 ports. General all-size, tape, compiler and analytic
assumptions remain. We did not run #505/#512's separate asynchronous instances
or the optional hosting-discovery search. Local execution was on macOS arm64,
Python 3.14.6; no fresh Linux execution is claimed in this receipt.

## Allocator correction and limits

The original aggregate solver read solution values even when CP-SAT returned
`UNKNOWN`. A zero-second run reproduced the defect: it exited successfully and
wrote an empty allocation. The maintainer patch now permits export only after
`FEASIBLE` or `OPTIMAL`; the lazy-cut loop uses the same explicit guard. Failed
solves preserve any pre-existing output and exit unsuccessfully, including under
`python -O`. Zero-width inputs are rejected before recursive pattern generation.

Three regression methods exercise twelve subprocess cases, including both
entry points, timeout and infeasibility, absent/existing outputs, invalid width,
and a feasible fixture with independently recounted call demand, port stock,
rank mass, remainders and literal nominations.

The solver minimizes coefficients rounded after scaling by 1000. An `OPTIMAL`
status certifies that integer objective, not exact optimality of a logarithmic
cost or exponential moment. Aggregate feasibility alone does not establish a
literal, physically admissible owner map. The large historical optimizations
and #507 diagnostics remain contributor receipts; this review independently
reproduced the #433 and #484 diagnostics and the regression fixture. The tools
retain family-specific constants and are research prototypes.

The original PR commits are preserved. The maintainer patch also corrects the
credit for #425 to **Zhihao Chen / jacklightChen**, alongside **icekylinx's #433**.
Existing notices retain DreamingOfClouds' and higherbeing's Claude assistance
disclosures and all predecessor attributions. Integration does not claim their
work as a new maintainer construction.

## Reproduction

With the pinned Lean toolchain and Python dependencies available:

```sh
python3 -B research/e8-complex-gauge-kernel/verify.py /tmp/pr484-fresh --all
python3 -B research/e8-lemma-g-lean/verify.py --instances /tmp/pr484-fresh
python3 -B research/e8-lemma-a-lean/verify.py --instances /tmp/pr484-fresh
python3 -B research/complex-delivery-map-open-allocator/tools/test_allocator.py
python3 -B scripts/verify_pr_reconciliation.py
```

The first command requires a fresh output directory; NumPy is needed for the
finite instance checks and OR-Tools for the allocator regressions. Once the
pinned Mathlib cache is available, the formal runners accept `--no-cache`.
Original receipts are preserved under
[`research/community-formal-20261012-audit`](../../research/community-formal-20261012-audit).
