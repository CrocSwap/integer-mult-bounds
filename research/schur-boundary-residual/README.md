# Actual scalar boundary solve against the original Schur matrix

This closes one conditional implication in the unchanged PR3851 Gaussian
boundary solver: the stored reciprocal pivots and the initial Schur rounding
both enter the error against the **original** old-H Schur system. It supplies
the product-inverse bridge explicitly excluded by `factor-perturbation-margin`
and a narrow part of PR5081's local Core defect handoff. No new κ is claimed.

For integer `p>=101`, `P=32768p`, `eta=2^-P`, the [proof](PROOF.md) derives

```text
T = Lhat Ueff,    Ueff_ii = 1/round_P(1/U_ii),
T x-r = e_f + Lhat e_b,
||T^-1||_infinity <= 32p,
||x-S^-1 r||_infinity < 2^17 p^5 eta max(1,||r||_infinity).
```

The constants do not grow with the boundary dimension. `S` is the original
Schur matrix; exact `L U` factors `round_P(S)`. The upper pass multiplies its
complete unrounded dot-product residual by the stored reciprocal and rounds
once. Substituting a rounded upper diagonal or rounding that residual early
analyzes a different program.

The theorem retains the original old-H row gap, matching source/page,
bandwidth, positive pivots, exact factor caps for `LU(round_P(S))`, primitive
arithmetic and adequate record widths. It derives both inverse bounds rather
than assuming the published product-inverse cap. These premises are not
certified by a successful finite replay.

## Evidence and reproduction

[fixture.py](fixture.py) executes the authenticated source producer and scalar
solver, with independent rational reconstruction and observation of computed
states. [RESULT.json](RESULT.json) records the complete deterministic result.
The page crosses a physical period and has eight source rows, three eliminated
interior rows and five boundary rows. Two scalar calls execute 20 boundary truncations
and 50 exact multiplication calls in total. Both components distinguish all
three semantic controls, and borrowed ports and scratch are restored. The
finite parameters `s=13,t=14,u=w=1,p=16,P=24` are reduced calibration
parameters, outside the production theorem. [verify.py](verify.py) also isolates the missing initial
Schur perturbation: a scalar solve has zero online residual but nonzero error
against the original matrix. A two-row control distinguishes premature upper
residual truncation. These controls test the claimed mathematical distinctions.

Local environment: CPython 3.12.13, Linux x86_64, standard library only.
Run from the repository root with Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/schur-boundary-residual --check-only
python3.12 -B scripts/research_package.py --package research/schur-boundary-residual
python3.12 -I -O -B research/schur-boundary-residual/verify.py
```

The direct verifier authenticates every declared live input before importing
source code, uses a fresh bytecode cache, and authenticates the retained nested
word/branch-free archives. The registered command has a 300-second limit.
`--write` regenerates the complete receipt; ordinary replay compares every
field, not only an output digest. Explicit exceptions remain enabled under
optimized Python. A committed package export supports the same direct command
outside Git; the generic metadata runner requires Git history.

## Scope, overlap and stopping decision

Base main `ff3cc58e370d0f678e529246f8c73e8094e18fcf`, priority revision7.
[TASK.json](TASK.json) preserves the original `uniform-transfer-audit` card,
refinement, overlap coverage and [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/3664#discussioncomment-19150318).
[SOURCES.json](SOURCES.json) binds exact live source bytes and historical
catalogue/selected-record provenance. Full refresh covered 353 open PR bodies,
4,564 Discussion records and all 7,091 local notes; targeted live checks
separated this question from the expansion/chirp/compression join, which was
reported complete conditionally in [Discussion3664](https://github.com/CrocSwap/integer-mult-bounds/discussions/3664#discussioncomment-19150284).
This is coverage evidence, not proof of novelty or an atomic board snapshot.

The boundary owner borrows factor bands and a dyadic RHS, returns a protected
solution and restores borrowed ports and scratch. No production algorithm or
paid cost changes. Its complete physical cost remains inherited; global
coefficient/interval acceptance, full Core headroom, two interior applications,
coupling errors, locality, normalization, tensor/chirp and CRT admission remain
open here. We compared the PR5292 three-register eleven-call question and
stopped before an unpriced large search. The decision is to narrow this round
to an existing numerical acceptance gap, then stop at that implication.

## Open next questions

1. Compose the complete old-H local Core defect on its actual computed input.
   Begin with both interior passes and the rounded coupling RHSs, then apply
   this boundary estimate and final normalization. This matters because this
   lemma alone does not close PR5081 OQ1. Interior approximation, coefficient
   intervals, locality and primitive acceptance remain blockers.
2. Independently audit the inherited global row gap and exact factor-growth
   caps for `LU(round_P(S))`. Start at the corresponding source proof and its
   diagonal-dominant elimination argument, retaining the initial Schur
   perturbation. The current result is conditional on those analytic premises.

## Credit

Prepared by Hiroki KUMAZAKI (@kumagi), with substantial OpenAI Codex assistance
in proof, source audit, checker, coordination and writing. Apache-2.0. This is
an author-checked conditional argument and finite source replay, with additional
AI review; it is not independent human or formal-kernel acceptance.

Jose Manuel / `jmbarrancoml` supplied the unchanged physical Gaussian Core,
[PR3851](https://github.com/CrocSwap/integer-mult-bounds/pull/3851), head
`7ab67b4a84d28cd562b9711aa315ca5b47822b37`, including its finite old-H setup
checks and claimed scalar allowance. We retain Chafik Boukhalfa's PR489
branch-free source at `8922e3b3f0fd7772b0fb42028eb2532984c3ab42`, PR3787's
physical word source at `9b5474f47b0ea9a3c76bb5b1b577fb36704815e0`, and their
nested notices and full Gaussian/RaD/manuscript lineage. The displayed
`2^17 p^5 eta` allowance already appears in the retained
[RaD phase-cell report](../../references/semantic-bulk/rad20/reports/downstream-phase-cell-inverse.md);
our contribution is the explicit actual-caller bridge and residual evidence,
not a new constant. Its LICENSE and NOTICE are declared export inputs. James Reed's
[factor margin audit](../factor-perturbation-margin/README.md), commit
`b1d6a2447f8d05d3f859dd278d333e247ee9a8e0`, already covers scalar perturbation
and growth margins; we do not claim those as new. JoyboyBrian's
[PR5081](https://github.com/CrocSwap/integer-mult-bounds/pull/5081), head
`4c49fff7fdfa4ddda6ef615575b6762b3f46f9cd`, requests the local-defect audit.
PR5059 explicitly separates original `S` from `LU(round(S))`, but uses a
different block ABI. PR5255 concerns a graph-support resolvent bound and
excludes Gaussian rounding. Cinna Davis's PR4100 supplies the wider uniform
transfer context, rather than this scalar solver's definition.
