# Grouped cyclic inverses with one arbitrary dirty connector

This replaces PR628/905's quadratic number of first-order dirty inverse
calls with **four higher-order calls**, using **one arbitrary dirty length-L
connector**. The source and connector restore bit for bit; the signed inverse
word cancels exactly. Incoming working-grid low bits may all be nonzero.

The data scans use O(rL) scalar arithmetic for r-1 root factors, with cubic
precision overhead. This trades the prior O(r^2 L) data term for a larger
scalar preparation and solve term. It is a local classical arithmetic
construction, **not a new kappa, common-label supplier, or bit-reversible
arithmetic compiler**.

## Construction and costs

Split the prepared roots into two stable polynomials. Each group uses a
causal integer lift of the source, a k-dimensional cyclic companion closure,
a homogeneous correction to the target, and reverse source lifts. A standard
four-call dirty commutator combines the inside/outside groups. It charges
both rounded inner calls separately; their increment may depend on the
borrowed data.

The proof bounds the summable companion powers through the adjugate
resolvent. Rounded binary powering, polynomial coefficients, phase windows,
the initial gauge, and output multipliers all have explicit error budgets.
The closure is solved by fraction-free integer elimination, with wider
intermediates and workspace paid.

For prime-power r>=3, target error 2^-p, incoming grid 2^-w, source/target/dirt
norm <=2^m, and rational unit phases of bit size at most B_phi, put

    A = max(p,w) + 2m + 48r^3.

Under the retained kernel preparation hypotheses, a conservative supplied
neighboring-cycle bill is

    soft-O(rL*(A+B_phi) + r^3 log L*(A+log L) + r^4*(A+log L)).

The data grid needs at most max(p,w)+8r^3 fractional bits. Wider coefficients
and integer guards are included in A. Scalar powering has an additional
log L precision term. Clean scalar workspace is
O(r^3(A+log L+log r)) bits, in addition to the data arrays. These scalars
can exceed a length-L array when L is small; no unconditional space or
runtime improvement is claimed. Exact product accumulators have the usual
constant-factor wider precision.

[PROOF.md](PROOF.md) gives the all-length error argument, exact restoration,
four-call composition, common-operator Wiener bound, explicit budgets, and
bit/space accounting. Finite tests exercise that argument; they do not
constitute proof-assistant verification of it.

## Replay

Python 3.11 or later, standard library only, offline:

```sh
python3 -I -O -B research/grouped-dirty-cyclic/verify.py
python3 -I -O -B research/grouped-dirty-cyclic/test_package.py
```

The main success marker is `PASS_GROUPED_DIRTY_CYCLIC`. Default verification
checks every packaged byte, retained source SHA/Git blob, and the complete
recomputed mathematical receipt. `--out /absolute/new/file.json` also writes
a fresh result outside the package after comparison; existing files are
never overwritten. `--bindings-only` checks source/package bindings only.
`--write` is an explicit authoring mode and is not an admission check.

Evidence covers 160 real cases, 40 complex weighted cases, 120 mixed-root
cases in both directions, and 48 cases from all ten pinned prime-power
fixtures through radix 16. The last group meets the original 128-bit error
target after coefficient preparation is charged. Tests include repeated and
zero inside roots, empty groups, L<k, arbitrary odd low bits, and nonzero
rounding in every newly bounded preparation component. There are 2,313
integer budget rows, three all-size polynomial identities, 16 additional
rejection controls, and 36 independent fraction-free solver comparisons.

## Scope and credit

The full multiplication reduction, common-label/Clifford realization,
arbitrary-stride fixed-tape routing, phase approximation for irrational
inputs, and hosting the clean scalar workspace remain separate obligations.
No selected certificate or `upstream/` file changes.

The kernel and bounds come from Ali Romman's PR621; the dirty lifts and
fixtures from Chafik Boukhalfa's PR628; the common-operator complement bound
from PR862; and the arbitrary-dirty cubic comparison from PR905. All consumed
sources and notices are retained byte for byte in `vendor/`, with exact
pins in [SOURCE-PINS.json](SOURCE-PINS.json). Classical state-space filtering,
Mahler bounds, factorization, and Bareiss elimination are credited in
[NOTICE.md](NOTICE.md). Prepared with substantial OpenAI Codex assistance;
no independent human or delegated-agent review is claimed.
