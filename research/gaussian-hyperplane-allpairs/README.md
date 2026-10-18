# Gaussian whole-hyperplane decoders: an exact reciprocity boundary

**Scoped negative result and exact boundary certificate. No new supplier or κ.**

Allow **all 3,600 ordered pairs** of the 60 whole Gaussian E8 root hyperplanes,
not just the 960 equal/orthogonal-normal pairs of Charles Bethin's
[PR767](https://github.com/CrocSwap/integer-mult-bounds/pull/767).
If the **fitted decoder matrix** is symmetric, every such binary decoder must
pay at least **180 Gaussian rank units / 360 rational rank units**. Individual
totals need not be symmetric, and arbitrary finite repetitions are allowed.
Even a fitted matrix with just **one asymmetric unordered pair** costs at least
**66 Gaussian units**, already too much for a positive inherited Dfc deficit.

The symmetry hypothesis is material. We characterize the coefficient diagonal
for *every* fitting matrix: its possible values are exactly the even-weight
vectors in `F2^60`. The package supplies a genuine nonsymmetric fitting example
with **no diagonal-hyperplane terms**, so the symmetric forced-diagonal proof
cannot be generalized to all completions. That example costs 4,736 Gaussian
units and is only a scope-boundary control, not an improved decoder.

## Exact model and difference from predecessors

Use PR767's lexicographically ordered 60 Gaussian lines in `Q(i)^4`, obtained
from the doubled E8 roots by pairing successive real coordinates. The form is
positive-definite Hermitian. For normal line `u`, put

```
H_u = {i : <v_u,v_i> = 0},       O[i,u] = 1_{i in H_u}.
```

Each `H_u` has 15 lines and spans a Gaussian hyperplane. A total with readers
`H_u` and sources `H_v` contributes the binary rectangle
`O[:,u] O[:,v]^T` and pays

```
beta(u,v) = rank_Q(i) G[H_u,H_v] = 2 if u is orthogonal to v, else 3.
```

In particular `beta(u,u)=3`. This is **not** the binary rank one of the
rectangle. Aggregate multiplicities modulo two into a 60-by-60 matrix `X`.
The decoded relation is `B = O X O^T` over `F2`. Fitting means
`B[i,i]=1` and `B[i,j]=0` for distinct nonorthogonal lines; orthogonal
entries are free **independently in the two directions**.

PR767's hyperplane theorem restricts `X` to 960 equal/orthogonal-normal types
and assumes no symmetry of `B`. It forces all diagonal types and gives a
floor of 180; its reported cost-820 feasible witness is not an optimality
claim. Our theorem instead allows all 2,640 excluded normal pairs but
restricts **global reciprocity of B**. Neither hypothesis set contains the
other. The new general defect identity specifies exactly how the forced
coefficients cease to follow when reciprocity is removed. We do not reprove
PR767's planar or six-plane results, or Sagar Thakrar's PR738 unrestricted
Gaussian floor of 40.

## Proof: reciprocity forces the expensive diagonal

The source-bound geometry check gives a symmetric binary matrix `O` of rank
60, every row of weight 15. Let `Q=O^-1`. Then `Q` is symmetric and
`O 1 = 1`, hence `Q 1 = 1`. Every fitted matrix has the **unique**
whole-hyperplane coefficient matrix

```
X = Q B Q^T.
```

For a symmetric matrix `B` over `F2`, the cross terms cancel in each quadratic
form, giving the general identity

```
diag(Q B Q^T) = Q diag(B).
```

Thus `diag(X)=Q 1=1`: each of the 60 diagonal rectangle types has odd
multiplicity. Each costs three, so `C >= 3*60 = 180`. Reducing coefficients
modulo two cannot undercharge this lower bound: odd multiplicity requires at
least one paid occurrence, and cancelling pairs still cost twice their
physical pairing rank. This proves the statement for every finite number of
totals, not a bounded search. No attainment at 180 is claimed.

Conversely, symmetry of `B` and symmetry of aggregated `X` are equivalent by
invertible congruence. This is not a requirement that every original total
be self-adjoint. The exact positive control `B=I` uses 1,920 nonorthogonal-normal
types absent from PR767's dictionary; it is reciprocal, costs 5,940, and has
all 60 compulsory diagonal types. It establishes that the enlarged theorem
is nonvacuous outside the predecessor class, not that the floor is sharp.

## Complete asymmetry formula and its exact image

For each of the 450 unordered orthogonal pairs `e={i,j}`, set

```
a_e = B[i,j] XOR B[j,i],
c_e = Q[:,i] AND Q[:,j].
```

Expanding the quadratic forms without assuming symmetry gives

```
diag(X) = 1 XOR (XOR over e with a_e=1 of c_e).                 (1)
C >= 3 * popcount(diag(X)).                                  (2)
```

The diagonal part of `B` gives `Q 1=1`; forbidden nonorthogonal entries are
zero; pairing the remaining two directions gives (1). Equation (2) charges
only compulsory diagonal types and deliberately grants every other expense
for free.

The exact certificate establishes:

- 360 columns `c_e` have weight 34, and 90 have weight 38.
- Their binary span has rank **59**. All columns have even weight, so this
  span is exactly the codimension-one even-weight subspace.
- Every defect vector `a` is allowed: choose `B=I` plus one directed entry
  on each selected orthogonal edge. Therefore the possible coefficient
  diagonals are **exactly all even-weight vectors**, not just a superset.
- With one asymmetric pair, `popcount(diag(X))` is 26 or 22. Hence `C>=66`.
  This is a necessary floor; it is not an optimum or a supplier construction.
- A deterministic elimination witness uses 34 directed orthogonal entries
  and gives `diag(X)=0`. Its 1,726 active types have ranks `2*442+3*1284=4736`.
  The full `B` and `X` are retained and all 3,600 entries are replayed directly
  as support rectangles. Transposing this witness gives a different `B`.

The verifier checks both directions of all 450 fitting generators, and the
reciprocal generators, rather than sampling the `2^900` fitting matrices.
The written linearity argument extends those exact checks to the whole space.
The reciprocal affine space has dimension 450. The diagonal image census is
not an optimization of the unrestricted bill; indeed a zero diagonal makes
this particular lower-bound certificate vacuous, not the actual bill zero.

## Full optimistic budget and stopping decision

Under the inherited [format accounting](../format-limits-corrected/README.md#a1-scope-s2-accounting-axioms)
(Dfc and nonnegative pressure/fallback), a Gaussian line has rational rank
`k=2`, there are `v=60` ports, and the copied-information bill is `cst=2C`.
For every positive stage count `s`, before other necessary expenses,

```
D/T = (s-1) v k - s cst <= 120(s-1) - 2sC.
reciprocal B:                 D/T <= -120 - 240s < 0.
at most one asymmetric pair: D/T <= -120 -  12s < 0.
```

This is the complete favorable **negative screen**: additional helpers,
source access, frames, restoration, hosting, precision, and recursive work
are granted zero extra expense, never a credit. Nonnegative required
expenses cannot turn this nonpositive-deficit model into positive saving.
Equivalently, with nonnegative paid children of ranks below the parent width,
the normalized moment already exceeds one at saving zero and only increases
at positive saving. The original card's complete physical **5% ceiling gain**
gate is not weakened or passed. The selected 73-wide calculator is not applied
to this changed Gaussian interface. Supplier synthesis stops for the two
proved classes; unrestricted nonsymmetric whole-hyperplane decoding remains
open, as do partial supports, other geometries, and changed accounting.

The original card working example and ideal lever table were run at the task
base: selected-word `a_ceiling=0.001690054109089`,
`kappa_cap=0.0016872026453254019`; ideal rank-16 delivery has about 2.31 times
that saving ceiling. Those are planning controls, not evidence of a Gaussian
construction. The selected κ `0.001672660197076918` is unchanged.

## Reproduce and evidence

Python 3.12, standard library only, from the repository root:

```sh
uv run --python 3.12 --no-project python -I -O -B research/gaussian-hyperplane-allpairs/verify.py
uv run --python 3.12 --no-project python scripts/research_package.py --package research/gaussian-hyperplane-allpairs
```

Expected final scientific receipt:

```
PASS_GAUSSIAN_HYPERPLANE_RECIPROCITY pairs=3600 symmetric_floor=180 single_asymmetry_floor=66 diagonal_image_rank=59 zero_diagonal_bill=4736 controls=11 no_new_kappa
```

`verify.py --write` regenerates [RESULT.json](RESULT.json); ordinary replay
compares the complete parsed result, not a compressed container hash. The
receipt retains the two-sided binary inverse, 59 independent defect columns,
zero-diagonal witness, invoices, and coverage. All 3,600 Gaussian pairing ranks
are checked, with 62 independently realified rational-rank checks. The 11
controls cover source drift, singular incidence, physical/binary-rank
confusion, omitted compulsory types, direction, forbidden mask entries,
unjustified reciprocity, false unrestricted diagonal forcing, an impossible
odd diagonal, an incomplete image basis, and duplicate physical charges.
All acceptance checks remain active under `-O`. No Lean/kernel run or full
multiplication theorem verification is claimed.

Observed on macOS arm64 / CPython **3.12.12**: the optimized `--write` smoke
and the complete registered replay both passed with the receipt above; the
wrapper reported `PASS_REGISTERED_RESEARCH_PACKAGE` with outcome
`negative-result`. No full repository suite, selected cold replay, or GitHub CI
result is claimed.

[SOURCES.json](SOURCES.json) pins live predecessor bytes and historical Git
provenance; [VERIFY.json](VERIFY.json) registers every live input. Direct replay
works without Git or network in a source tree containing those paths; the
registered provenance check additionally needs the pinned Git history.
[SELECTION.json](SELECTION.json) preserves the one independent chooser draw.
[TASK.json](TASK.json) records the explicit bounded pivot: unrestricted
all-pairs optimization was not resolved, and the final deliverable is the
reciprocity theorem and exact unrestricted **diagonal-image** classification,
not a claim about the unrestricted optimum.

## Open next questions

1. **Can a nonsymmetric whole-hyperplane decoder attain C<60?** Equation (1)
   eliminates reciprocity and single-defect candidates but not the remaining
   class. First optimize the full weighted bill with at least two asymmetric
   orthogonal pairs, retaining exact certificates. The blocker is a certified
   optimizer or a stronger lower bound; vanishing diagonal alone does not help.
2. **Can a partial-support inventory evade the invertible incidence argument
   while paying its entire physical bill?** First specify actual reader/source
   supports and recompute pairing ranks before applying any bound. The blockers
   are support-specific exact fitting and a legal complete paid realization.

Structured relevance, first steps, and blockers are in TASK.json. These are
research questions, not promised future implementation in this PR.

## Attribution, overlap, and license

Base `e112d71c8d7bb32435debcc54df932593dd8223a`; independent seed
`ab997fb2d6ec74f382d67332d715ef38`, complex-mechanisms. The scoped claim and
explicit pivot are in [discussion2049](https://github.com/CrocSwap/integer-mult-bounds/discussions/2049#discussioncomment-18931187).
Cached overlap coverage included 329 open PRs (drafts included) and 692
fully paginated discussions on 2026-10-14 at 18:11/18:12 UTC; targeted local,
merged, and live predecessor checks are recorded in SOURCES.json. No-match
searches are not a novelty certificate.

Charles Bethin / `cbethin` supplies PR767's geometry implementation and the
restricted whole-hyperplane theorem, published head
`96b4b74677d1bef99e8346bfb6a4ed0531e58a62`; all imported bytes are pinned from
the current base. Joel Pulikkan / `GamingPuzzled` (PR620) supplies the Gaussian
line model and open copy-cost problem. Sagar Thakrar / `thakrarsagar` (PR738)
supplies the distinct unrestricted floor40. Douglas R. Colkitt /
`Mister-Meeseeks` supplies related Hurwitz and planning precedents;
`DreamingOfClouds` supplies inherited format accounting. Their source-specific
notices and the original project attribution are retained unchanged.

Prepared for Adam Gall with substantial OpenAI Codex (GPT-6 Astra) assistance
in research, proof, implementation, and packaging. No independent human review
or formal proof-assistant acceptance is claimed. Apache-2.0.
