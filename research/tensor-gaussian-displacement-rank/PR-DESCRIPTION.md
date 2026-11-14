## What changed and why it matters

This package proves an exact representation obstruction for a proposed
grouped Gaussian inverse: flattening a separable tensor does not preserve
small ordinary Toeplitz displacement rank. The retained shallow inverse uses
short lower-times-upper Toeplitz generator sums, so the required generator
count is an explicit obligation when that formula is transferred to a
grouped block.

For normalized shifted Gaussian sections of dimensions `n_i >= 2`, total
dimension `T`, and fastest axis `f`, the ordinary Sylvester and Stein
displacements of both the tensor and its inverse have exact rank `2T/n_f`.
This is also the exact minimum number of ordinary `L(u) U(v)` generator terms.
The best lexicographic axis ordering gives `2T/max_i n_i`; two-point factors
have full displacement rank in every such ordering.

The underlying proof is stronger: for any invertible `m x m` outer matrix A
and any Toeplitz fastest factor B, explicit boundary minors have determinants
`(-b_-1^2)^m det(A)^2` and `(-b_-1 b_1)^m det(A)^2`. The forward ranks follow
from these minors and the matching support upper bounds. The inverse
Sylvester identity and a Schur-complement/persymmetry argument supply the
inverse claims. A Vandermonde factorization establishes Gaussian
invertibility uniformly.

## Scope, dependencies and predecessor credit

Exact base: `e54523517d0f03e58352e647c403a5af3e525a57`. The selected record,
review, task card and source sections have Git-blob/SHA256 pins in
`SOURCES.json`. They are historical provenance; the verifier has no external
runtime inputs or dependencies.

The normalized kernel comes from `GAUGEFREE-INTERIORS.md`, while the ordinary
generator mechanism comes from `SHALLOW-TOEPLITZ.md`. Preserve Vlado
Vojdanovski's capped-phase-fusion credit and the cited source authors' work.
The one-axis application/error contracts in #5566, #5571 and #6905 remain
their own results. This package adds the exact flattened representation
calculation and its matching scope controls, without repeating the familiar
serial factor-of-axes budget as a new contribution. Bounded overlap searches
found no matching exact project theorem; no literature-wide priority claim
is made. The proof cites Olshevsky, Oseledets and Tyrtyshnikov's classical
multilevel Toeplitz/tensor work as background.

## Reproduction and executed checks

```sh
python3 -I -W error -B research/tensor-gaussian-displacement-rank/verify.py
python3 -I -O -W error -B research/tensor-gaussian-displacement-rank/verify.py
python3 scripts/research_package.py --package research/tensor-gaussian-displacement-rank --check-only
python3 scripts/research_package.py --package research/tensor-gaussian-displacement-rank
```

The two standalone commands were executed with Python 3.12.14 and returned
identical `PASS` JSON. They cover 48 generic forward cases, 47 invertible
generic inverse cases, 11 Gaussian tensors, 22 exact minimum-generator
reconstructions, all six distinct-axis orders of a `(2,3,2)` tensor, and six
negative/scope controls. Ranks use exact rational elimination; selected
minor determinants use independent denominator-cleared Bareiss elimination.
Literal shift products are compared with indexed entry formulas. Explicit
failure checks remain active under optimized Python. The package hook also
registers both commands. The universal proof is written in `PROOF.md`; these
finite fixtures are failure controls, not the proof of all sizes.

## Limitations and open obligations

- This is a lower bound on the length of one exact ordinary generator
  representation, not on runtime, the recursive Full compiler or general
  grouped circuits. A direct local-axis circuit is an explicit control.
- The minimum is over lexicographic axis orderings, not arbitrary coordinate
  permutations. A checked Gray ordering reduces the rank in dimension four.
- Exact rank alone does not establish approximate rank or a useful rounding
  threshold. A structure-preserving rounded Toeplitz table is covered only
  after its invertibility and nonzero adjacent coefficients are established.
- Paid gauges, the full periodic Reference, holes, source generation,
  restoration, movement, precision and the complete three-transform budget
  are not replaced by the normalized-core calculation.

Open next questions give concrete first steps for quantitative minor
stability and a source-faithful grouped inverse that uses multilevel
structure with its complete physical budget.

## Kappa status and assistance

**No new kappa.** The selected conditional value remains
`363005817/100000000000` (#7000), with all five inherited assumptions retained.
This is a scoped analytic-recovery representation audit, not an unconditional
integer multiplication theorem or admission of a new recovery service.

Prepared for @CubeJerry with substantial OpenAI ChatGPT assistance. The
orchestrator and research worker independently derived and checked the
boundary-minor proof; the orchestrator extended the initial two-point result
to arbitrary Toeplitz sections. Predecessor credit is retained. New files
are Apache-2.0.

## Independent review and provenance boundary

A separate worker independently derived the complete proof (REVIEW.md). Registered normal/optimized replay, metadata/pins, committed bytes/modes and direct base ancestry pass. Generic full-history preflight refuses the intentionally shallow checkout; every provenance row was instead verified at its exact canonical base. No success is claimed for the refused gate. See VALIDATION.json.
