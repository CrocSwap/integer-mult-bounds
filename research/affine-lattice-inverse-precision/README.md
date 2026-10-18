# Exact inverse precision on an affine reachable lattice

For rational matrices A and B, a rational vector x0, and integers0<=w<v, let
`Q_b(t)=2^-b floor(2^b t+1/2)` componentwise. On the entire affine lattice
`L={x0+Bz : z in Z^k}`, the identity

`Q_w(Ax)=Q_v(Ax) for every x in L`

holds **if and only if** both conditions hold:

1. Every entry of `2^w A B` is an integer.
2. `Q_w(Ax0)=Q_v(Ax0)`.

Thus `y += Q_w(Ax); y -= Q_v(Ax)` restores every arbitrary dirty target exactly
under precisely these hypotheses, provided x is unchanged and both updates use
exact addition/subtraction. This is a theorem for rational rounded-linear
increments, not a claim that an internally rounded leaf has this form.

The integrated [mixed-precision inverse boundary](../mixed-precision-inverse-boundary/README.md)
gives the unrestricted product-grid criterion and a real PR628 leaf counterexample.
This extends its reachable-domain question to correlated affine lattices. It
adds both a safe nonintegral-coefficient example and the necessary offset test.
No frozen caller is modified or alleged faulty.

## Proof for all integer parameters

Use coarse-grid units: put `c=2^w Ax0`, `D=2^w AB` and `h=2^(w-v)<=1/2`.
Equality of coarse and fine rounding for a scalar t holds exactly when t lies
in one of the half-open intervals `[n-h/2,n+h/2)` around integers n. Indeed the
fine rounded value must equal the coarse integer n, and that fine rounding cell
is contained in the coarse cell. Modulo one this is a single half-open arc of
length h.

If D is integral, every `c+Dz` differs from c by an integer vector. Both rounding
maps commute with these translations, proving sufficiency and the offset test.

Conversely, suppose one entry of D is u/d in lowest terms with d>=2. Hold all
other integer parameters at zero and vary this parameter through0,...,d-1.
In that output coordinate, the fractional parts form d equally spaced points
on the unit circle, translated by c. A connected arc containing them has length
at least `1-1/d`. For d>2 this exceeds1/2; for d=2 it equals1/2, but a half-open
arc of that length cannot contain both antipodal endpoints. Therefore those
points cannot all lie in the safe half-open arc of length h<=1/2. At least one
integer parameter produces unequal increments. This proves necessity for every
entry, all dimensions, signs and rational affine offsets.

## Why correlations and offsets matter

Take `A=(1/2,1/2)` and let B have columns `(1,1)` and `(1,-1)`. Then `AB=(1,0)`.
For x0=0, coarse precision0 and any finer precision are safe on the index-two
lattice `x1+x2 even`, although A itself is nonintegral and is unsafe on Z^2.
For the larger product grid, x=(1,0) already witnesses failure.

An integral D does not suffice: c=1/2 has coarse rounding1 and fine rounding1/2.
Conversely, exact coarse-grid membership of the offset is unnecessarily strong:
c=1/16 is safe at coarse precision0 and fine precision2, although nonintegral.
Testing only z=0 also does not certify the unrestricted lattice.

## Reproduce and evidence

```sh
python3 -I -O -B research/affine-lattice-inverse-precision/verify.py
python3.12 scripts/research_package.py --package research/affine-lattice-inverse-precision
```

The standard-library verifier checks34,821 scalar parameter combinations against
complete residue periods, and52,488 affine matrix cases. The latter uses every
2x2 A with entries in{0,1/2,1}, every2x2 B with entries in{-1,0,1}, four offsets
and two coarse precisions. The period oracle directly rounds every residue;
it does not implement the circle proof. There are867 arbitrary-dirty exact
inverse fixtures and five controls for correlations, offset omission, an
unnecessarily strong offset condition and bounded-domain confusion.

These finite checks corroborate the written quantified proof. They are not a
formalization of the multiplication theorem or evidence that a selected runtime
maintains the required lattice. Source Git blobs and byte hashes are pinned.

## Open next questions

Can a selected caller certify closure of a useful affine source lattice under
all intervening updates? Extract its exact update maps, prove closure, then
apply this criterion to each inverse pair and price the resulting precision
policy. Internally rounded source updates and bounded nonlattice reachable sets
remain blockers; this theorem does not infer their safety from local error bounds.

## Credit and limitations

The integrated mixed-precision-inverse-boundary package supplies the product-grid
criterion; Gareth Davidson's dirty-prefix-precision and Chafik Boukhalfa's PR628
supply the same-deterministic-increment discipline. Prepared for woklerx with
substantial OpenAI Codex assistance. Apache-2.0. No independent human review,
native compiler, selected cold replay, new supplier or kappa is claimed.
