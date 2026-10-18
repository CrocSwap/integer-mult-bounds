# Selected PR1094 charts: geometry and exact phase

**Adversarial supplier-boundary audit; no new κ and no selected production defect.**
An orthogonal change of the active axes can preserve their full projector,
all spectator coordinates, support and amplitude magnitudes while changing the
exact normalized complex residual. The missing condition is preservation of
coordinate weight modulo four. The selected controller binds the actual axes
and rejects the demonstrated mutation.

For an orthonormal active basis `U` and a rebase `V=US`, with `S` orthogonal over
F2, the inherited complex residuals agree exactly **if and only if every row of
S has weight 1 modulo 4**. Otherwise their convolution kernels differ by an
explicit binary character. [PROOF.md](PROOF.md) derives the criterion for every
dimension from the actual `C_q=((1+i)I+(1-i)X_q)/2` operation. This is a classical
phase-refinement argument applied to this interface, not a new algebraic
priority claim. These `C` gates are not ordinary real Hadamard gates.

The smallest bad rebase is `I+J` on four axes: its rows have weight three. It
changes the coefficient at the first original active axis from `i/4` to `-i/4`,
while the zero-displacement coefficient remains `-1/4`. Thus the discrepancy is
not a global phase. A six-axis `I+J` rebase, whose rows have weight five, is a
nonpermutation positive example that preserves the exact residual.

## Selected source-bound evidence

The audit reads the **actual selected PR1094 replay archive**, pinned at main
`49b3157d1d89adcef16df8be98445451672be5ba`, and all 69,120 literal helper owners.
It does not mistake the retained historical `evidence/` directories for a
current replay. Exact Git/SHA-256 input pins are in [SOURCES.json](SOURCES.json).
Submission is based on `dadfea6e8a78ff6ba901705f87532a71c6f5bbb8`; every experimental input remains unchanged.

| Completed check | Coverage |
|---|---:|
| Complete calls / helper roles | 144 / 69,120 |
| Emitted 73-axis charts / all Gram entries | 10,002 / 53,300,658 |
| Distinct `(chart,width)` signatures | 10,008 |
| Exact kernel coefficients, both signs | 5,348,224 |
| Embedded same-projector phase witnesses | All 10,008 signatures |
| All orthogonal matrices, dimensions 1–6 | 23,817 |
| Small-census exact coefficient comparisons | 2,996,852 |

Every original chart passes. The complete role/route/chart stream agrees with
the archived digest. Each kernel is checked by literal physical convolution,
a separate subset formula and coordinate transport through the actual chart.
Translation invariance and the written argument extend a kernel to arbitrary
complex inputs and every spectator fiber; `2^73` input columns were not enumerated.
The operator inverse is checked as well, without identifying it with the
scalar-backward supplier's helper endpoint.

The concrete selected example is **stage 0, replica 0, helper 49**, physical
family 4467, owner replica 4, port 99, child 10, offset 0, width 4. Its active
axes `[477,475,478,463]` become `[458,460,457,472]`. The full 73-dimensional Gram
matrix, active projector and every spectator column stay unchanged; the
coefficient at displacement 477 changes from `i/4` to `-i/4`.

[production_check.py](production_check.py) separately exercises the unchanged
source `orthobasis`/`audit` function ASTs and emitted-chart equality assertion,
with an explicit namespace built from the pinned archive. The original input
passes; the same-projector mutant with a correct new content hash and a wrong
spectator route reject. This is an isolated source-predicate replay, **not the
complete top-level admission driver**. The verbatim source `Op.zero_state`
method also agrees with the new kernels on 512 six-coordinate input columns
using only C gates. It does not test other source gate types.

## Reproduce

From the repository root, standard-library Python 3.10+:

```sh
python3 -I -O -B research/selected1094-chart-phase/verify.py
python3 -I -O -B research/selected1094-chart-phase/production_check.py
python3 -I -O -B research/selected1094-chart-phase/test_package.py
python3.12 scripts/research_package.py --package research/selected1094-chart-phase
```

The mathematical marker is `PASS_SELECTED1094_CHART_PHASE`, with
`roles=69120 charts=10002 no_new_kappa`. Complete deterministic receipts are
[EXPECTED.json](EXPECTED.json) and [PRODUCTION.json](PRODUCTION.json).
The verifier compares decoded complete JSON, not compression bytes of a
regenerated output. All original input containers retain strict immutable pins.
`--receipt /absolute/new/file.json` saves a new receipt; `--source-root` supports
an input-only relocation. Existing outputs are refused.

Eight package tests cover all columns and spectator fibers of a small exact
operator, inverse/square identities, an independent unpruned low-dimensional
census, positive nonpermutation rebasing, and actual optimized subprocess
failures for source/container/receipt corruption and occupied outputs. Six
mathematical controls and two source-predicate controls delimit the checks.
See [VALIDATION.md](VALIDATION.md) for exact environments and results.

## Scope, overlap and credit

Task `supplier-boundary-audit`, **refined** to the selected normalized residual
chart's ordered-axis/phase obligation. Chooser seed
`08486e2f4cb05dd9e1b849fa4eff7033`, priority revision 2.
[Discussion 1237](https://github.com/CrocSwap/integer-mult-bounds/discussions/1237)
records the scoped claim; [TASK.json](TASK.json) gives the stopping rule.

Selected PR1094 source: `0fc329d0bec93ca7cd288eaea1295172e8789810`, inheriting
PR1087 `589d1cedf5ef5f231182f4ec86408616311a8af0`. Credit Rohan Arun, Jeremy Kothe,
Hao Yan and the retained Clifford, normalization, ownership and supplier lineage.
PR1209 independently checks pending-axis independence and chronological cuts,
explicitly excluding spectator charts. PR1149 checks canonical-frame recursive
ranks. PR702/712 check historical local wrapper phases. This adds the physical
active-basis phase criterion and current emitted-chart binding; those different
checks are not replaced. See [NOTICE.md](NOTICE.md) for exact parallel heads.

The local normalized endpoint is inherited. Full scalar/native/phase-wrapper
replay, invoice and precision/tape checks, all-size compiler, physical cover
realization and analytic transfer remain outside scope. The source predicate
replay adds no new proof of its inherited premises. Neither a faster algorithm
nor an improved paid supplier profile or κ follows from this audit.

Prepared by **Gareth Davidson (@bitplane)** with substantial **OpenAI Codex
assistance**. No subagents or independent human review. Apache-2.0.

## Open next questions

1. Could a phase-preserving rebase reduce actual chart-adapter work? This matters
   only if the complete physical invoice improves. First test a six-axis
   weight-five rebase on one pinned width-seven role, preserving the full
   wrapped endpoint and accounting for every route and adapter. Current literal
   route admission would need a separately justified extension; no savings are
   established here.
2. Can the universal phase criterion be formalized alongside the existing exact
   C-gate semantics? Start with the Z/4 weight polarization identity, then prove
   convolution conjugation for an arbitrary orthogonal basis. This would certify
   the implication rather than only the finite census; the physical compiler
   and archive-to-theorem binding would still be separate obligations.
