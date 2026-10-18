# Coupled residues for the P104 integer lifting word

This package reduces the certified nonlinear residue domain of PR3033's
rank-seven lifting word from **1,024 to 343 bits per 128 Gaussian components**.
For four blocks at N=512, the corresponding counts are 4,096 and 1,372 bits.
Every real residue coordinate remains between 0 and 15. The result is an exact
local domain reduction, with an executable signed-input identity. It establishes
no runtime gain, complete supplier or new multiplication exponent.

Base main `d8e0f83f00191df62174b641e9fff055c357f641`, priority revision 6.
Dependency [PR3033](https://github.com/CrocSwap/integer-mult-bounds/pull/3033)
at `b12bbaeb5ca2e83f15433fc2dd0ba3b766595281`. Its open question 2 asks how to
reduce the narrow correction cost. This changes the independent scalar residue
contract to a coupled lattice contract. It is a side result relative to the
catalogue's chronological endpoint-correction task. The concrete relevance is
that a future narrow circuit can operate on 343 residue bits, rather than
1,024 independently chosen bits, while preserving the identical floor word.
No claim is made that this alone overcomes the O(N r²) correction overhead.

## Lattice and exact identity

Let N=2^r. Identify Z[i]^N with Z^(2N), using interleaved real/imaginary
coordinates. Let P be the exact pair from Tekalign's PR3025/3033 reference:

```
d=a-b; s=b+floor(d/2); d=i*d;
b'=s-floor(d/2); a'=b'+d.
```

Floors act on both real components. Its ideal linear map is
C(a,b)=((a+b+i(a-b))/2, (a+b-i(a-b))/2).
Let L_r apply P on address bits 0,...,r-1 and let U_j be the first j ideal
stages, with U_0=I. Define Γ_r to be precisely the set of integer shifts z
satisfying, for every j=0,...,r-1 and every pair (a,b) in stage j,

```
Re((U_j z)[a]-(U_j z)[b]) ∈ 2Z,
Im((U_j z)[a]-(U_j z)[b]) ∈ 2Z.                 (1)
```

The conditions also ensure that every ideal prefix on z is integral.
For all signed Gaussian integer x and z∈Γ_r,

```
L_r(x+z) = L_r(x) + U_r(z).                    (2)
```

This is a sufficient translation lattice, not a claimed characterization of
all periods of the nonlinear error. We compute the entire lattice defined by
(1); a larger equivariance lattice could give an even smaller domain.

To prove (2), write d=p+iq. The difference between P and C at either output
is `(q mod 2 - p mod 2)*(1-i)/2`. Translating a pair by a shift whose difference
has even real and imaginary components preserves this correction. Induct on
stages. If the computations have differed by U_j(z) so far, condition (1)
preserves the next pair's correction, so their next difference is U_(j+1)(z).
This proof includes negative inputs because the parities are Euclidean residues.

P is bijective, with the literal inverse obtained by using -i. Consequently,
L_r is bijective. Setting y=L_r(x) in (2) proves the inverse identity

```
L_r⁻¹(y+U_r(z)) = L_r⁻¹(y)+z.                 (3)
```

The inverse translation lattice here is **U_r Γ_r**. It need not equal Γ_r.
For example, at r=2, interleaved z=(0,0,0,0,1,1,1,3) satisfies (1), but
U_2(z)=(2,0,1,1,0,2,-1,1) does not. The replay checks (3) on every rank-seven
basis column; it does not silently use the forward residue box for the inverse.

## Exact index certificate

Start with an integer basis B=I. Before a stage, intersect its column lattice
with each even-difference condition. If every entry of the constraint row wB is
even, the condition costs no index. Otherwise choose one odd pivot column p,
subtract p from every other odd column, then double p. Column subtraction is
unimodular, and the doubled pivot parameterizes exactly the parity kernel.
Thus this restriction multiplies the index by exactly two.

Apply the ideal stage to that restricted basis. Its entries are integral by
the constraints. Each complex C has determinant i, so its real determinant is
one. It therefore preserves covolume. Induction proves that the following
integer counts are the exact index exponents of (1), without a floating-point
rank or a bounded search over candidate shifts:

```
r   nontrivial parity conditions per stage       log2 index
1   2                                            2
2   4,2                                          6
3   8,4,3                                       15
4   16,8,6,4                                    34
5   32,16,12,8,7                                75
6   64,32,24,16,14,11                           161
7   128,64,48,32,28,22,21                       343
```

`lattice.index_counts` performs this exact basis-intersection calculation.
`independent.py` imports neither it nor the predecessor. It instead builds all
rational-prefix congruences at once, scales them to modulus 2^(floor(r/2)+1),
and computes their image by minimum-valuation elimination over Z/2^g. It
independently obtains the same seven indices. At r=7 it also obtains quotient
factors `(Z/16)^3 × (Z/8)^22 × (Z/4)^70 × (Z/2)^125`.
The two methods share the stated ideal pair formula and coordinate convention.
They are separate internal implementations, not independent human review.

## Canonical residues with bounded coordinates

`HNF7.json` contains a sparse upper triangular integer matrix H. Its 4,192
nonzero entries have absolute value at most 16. Verification checks all of
its columns against (1), verifies its triangular/Hermite bounds, and computes
its determinant from its diagonal. The determinant is 2^343, so inclusion
H Z^256⊆Γ_7 and equality of indices prove H Z^256=Γ_7. The replay does not
trust Sympy, the optional generator, or a stored hash as a mathematical proof
of this equality.

The diagonal has 36 ones, 125 twos, 70 fours, 22 eights and three sixteens.
Descending triangular division gives one unique representative s per coset,
with `0 <= s[j] < H[j,j]`. Existence follows by division; uniqueness follows
by taking the largest coordinate where two such representatives differ.
There are exactly `2^343` such representatives, each with every coordinate
below 16. This is 681 fewer residue bits per block, about 66.5 percent.

PR3033's lattice `16 Z^256` lies in Γ_7. Indeed an ideal prefix of length j
has real denominators dividing 2^ceil(j/2), and for j≤6 multiplication by 16
makes every component even. The replay also verifies all 256 scalar generators
by triangular reduction. Therefore the canonical representative depends only
on the four low bits of each input component.

For `t = x mod 16` and `s = canonical(t)`, formula (2) gives the exact split

```
L_7(x) = U_7(x-t) + U_7(t-s) + L_7(s).         (4)
```

Both ideal images in (4) are integral, and every real coordinate of t-s lies
in [-15,15]. `lattice.split` executes this identity and compares it against the
byte-identical predecessor word, including negative and 4,090-bit inputs.
Its wide backend is a direct exact numerator transform. No approximate backend
or integer recovery step is assumed.

For N=512, the seven active bits form four independent blocks before the left
wrapper. The product lattice has index 2^1372. With exact monomial wrappers
A on output and R on input, the input lattice is R⁻¹(Γ_7^4), the output/inverse
lattice is A U_7(Γ_7^4), and (2)-(3) hold after wrapping. Permutations and Gaussian
units preserve integrality and covolume. Two fixtures check arbitrary synthetic
512-address monomial wrappers and paired return. This is not a replay or
admission of the actual PR2586 native recipe; the wrapper assertion follows
from the general algebraic argument.

## Cost boundary and stopping decision

This improves the residue **domain**, not its evaluated circuit cost. Relative
to the scalar split, the executable reference adds triangular reduction and
one narrow ideal transform per block. Dense triangular division performs 256
quotient steps and at most 32,896 column updates. The narrow ideal transform
uses 448 pair butterflies. The narrow nonlinear pass still uses 448 pair
lifts. Basis access, allocation, all intermediate buffers, exact division,
reads/writes and disposal are additional costs; Python local-array disposal
is not a dirty-memory restoration or reversible-erasure proof.

The final t,s coordinates are four bits and t-s has magnitude at most 15, but
triangular division intermediates can be larger. A conservative bound starts
with magnitude below 16 and grows it by a factor of at most 17 per pivot:
`M_next <= 17 M + 16`. With 256 fixed pivots this is a finite bound below
2^1053 for the low-bit reduction. It is not evidence for a cheap variable-rank
reducer. The optional generator and exact index verifiers are offline tools;
their cost must not be charged as zero setup in a future supplier.

The implementation owns its Python arrays, retains no source/query aliases,
and has no concurrent writers. It leaves the wide backend contract, physical
routing, collector error bounds, storage/restoration and complete caller
invoice unresolved. PR3033 already states why an approximate child cannot be
substituted for exact output for free. No new favorable complete-supplier budget
is proved here. The family decision is **stop after this local domain reduction**.
Do not launch a lookup-table or dependent circuit campaign merely from the
state-count reduction; 2^343 entries are still unaffordable.

## Reproduction and controls

From repository root, Python 3.12, standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/p104-coupled-lifting-residues
```

The registered replay checks the exact basis/index, all seven ranks with the
separate modular checker, both translation directions for all 256 basis
columns, 18 signed fixtures at six widths, two wrapped four-block fixtures and
162 exhaustive signed pair cases. Eight behavioral groups include complete
unpruned quotient enumeration at ranks one and two, a same-index invalid basis,
wrong inverse-lattice reuse, input limits, typed-receipt and source corruption,
and read-only Git-free ordinary/optimized CLI exports. Checks use explicit
exceptions and remain active under `-O`. The normal replay never rewrites evidence.

Optional certificate regeneration uses Sympy 1.14.0 and writes a new external
file, refusing overwrite:

```sh
uv run --python 3.12 --with sympy==1.14.0 --no-project python -B \
  research/p104-coupled-lifting-residues/generate_basis.py \
  --output "$HOME/.cache/integer-mult-bounds-runs/SESSION/HNF7.json"
cmp research/p104-coupled-lifting-residues/HNF7.json \
  "$HOME/.cache/integer-mult-bounds-runs/SESSION/HNF7.json"
```

Use an existing session-owned external directory for SESSION. Sympy is needed
only for regeneration; membership plus determinant verify the witness independently.
The observed environment and completed commands are recorded in TASK.json.
No full selected cold replay, native admission, outer release, formal-kernel
verification or independent human review is claimed.

Engineering-mode's **Build the Lever** led to the exact index, residue and
independent modular scripts instead of a hand-calculated count. **Prove It Works**
led to literal predecessor comparisons, signed inputs, invalid certificates and
Git-free CLI checks. Power-of-ten limits/deviations for these finite research
scripts are recorded in ENGINEERING.md.

## Open next questions

1. Can the 343-bit residue domain support a circuit cheaper than the scalar
   split after paying reduction and the extra narrow linear pass? First inspect
   the triangular basis for a sparse or staged reducer and price the whole
   path. The blocker is a complete operation/width/buffer bill, not state count.
2. Is Γ_r the full equivariance lattice of the nonlinear error? Start by
   enumerating all rank-two periods and comparing them with (1). Cancellation
   between stages could enlarge the period group. A proof must distinguish
   sufficient prefix conditions from necessary conditions on the final map.
3. Can an inverse residue box for U_7 Γ_7 give a complete paired implementation
   with the same physical storage contract? First derive and certify its own
   triangular basis, then include both reduction passes and reset. Reusing H
   directly is unjustified; the rank-two counterexample is a regression control.

## Attribution and scope

Nick Petalas. Substantial automated assistance in the proof, code, separate
internal modular implementation, tests and writing; no independent human review
claimed. Apache-2.0. Tekalign's PR3025 supplies the reversible floor word and
collector, and PR3033 supplies the scalar translation split and its exact/precision
cost boundary. `vendor/lifting.py` is byte-identical to its PR3033 source, originally
PR3025 `a544ef068a46f4de3bc47d1d02149cbdc3ba547f`; PREDECESSOR.json records the
exact source blob and SHA256. Its original notice is retained. Gaussian monomial
recipe context is from ywz65/PR2586, with Arham Tahir/PR2999's occurrence/collision
lineage and the broader retained P104 geometry/native contributors. Generic
lattice parity kernels, Hermite normal form and Walsh factorization are not
claimed as new. SOURCES.json preserves the selected-record/catalogue provenance.
No shared checker, frozen predecessor, priority, frontier or other PR disposition
is changed. [Canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2750#discussioncomment-18981569).
