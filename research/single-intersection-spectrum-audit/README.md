# Literal audit of the single-intersection spectral rank bound

**Adversarial mathematical audit, no new kappa.** All 41 specified literal
matrices agree with the historical modular characteristic polynomial and
binary rank lower bound. The audit finds no counterexample to that bound.
It adds an independent polynomial calculation and a corruption control that
preserves both integer moments already checked by the historical routine.

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`. The selected conditional
certificate at this base is #626 with #543,
`kappa = 51110230636731/31250000000000000 = 0.001635527380375392`.
This historical-family audit does not alter that construction or certificate.

## Exact statement audited

The object is `spectral_parity_bound` in
[`scripts/experiments/single_intersection.py`](../../scripts/experiments/single_intersection.py)
and the characteristic-polynomial deduction in
[`docs/research/single-intersection.md`](../../docs/research/single-intersection.md).
For all k-subsets S,T of an h-point set, define the integer matrix

```text
C[S,T] = 1 if S=T or |S intersection T|=j, otherwise 0.
```

Let n be its order and o the total rational multiplicity of odd integer
Johnson eigenvalues. The historical claim is

```text
det(xI-C) mod 2 = x^(n-o) (x+1)^o,
rank over F2 of C >= o.
```

Reducing the integer determinant polynomial commutes with reduction of its
entries. The algebraic multiplicity of zero bounds its geometric multiplicity,
so binary nullity is at most n-o. This proves the implication from the
polynomial identity to the rank lower bound without reducing a rational
eigenbasis modulo two. The rational eigenvalue formula is inherited from
Ghareghani, Ghorbani and Mohammad-Noori,
[*Intersection matrices revisited*, Lemma 8 and Theorem 9](https://arxiv.org/html/0902.4367v4#S5.SS2).
This audit does not reprove that all-size formula by finite enumeration.

## Independent calculation and completed coverage

OS randomness produced assignment seed 65, selecting mathematical audit.
Three candidate tasks were the prime-power subset ceiling, Fano permutation
rigidity, and this spectral bound. `65 mod 3 = 2` selected the latter.
The seed sets the upper ground size to `9 + 65 mod 2 = 10` and upper subset
size to `2 + 65 mod 3 = 4`. Complete coverage is

```text
4 <= h <= 10,
2 <= k <= min(4, floor(h/2)),
0 <= j < k.
```

The stopping rule is completion of these 41 cases once, with no expansion
to the large historical orbit fixtures. The largest matrix has order 210.
This is a complete finite audit of that domain, not a search for a supplier.

`spectrum_audit.py` constructs entries from literal set intersections. It
does not call the existing incidence-factor, orbit-Gram, packed-row or rank
helpers. Its characteristic-polynomial engine applies simultaneous row/column
permutations and elementary similarities to obtain an upper Hessenberg matrix H.
Over F2, adding row r to row i and then column i to column r conjugates by
`E = I + e_(i,r)`, whose inverse is E. The implementation checks that all
entries below the first subdiagonal have vanished.

For the leading i-by-i block, let p_i be its characteristic polynomial and
p_0=1. Expansion along the last column gives, in characteristic two,

```text
p_i = (x + H[i-1,i-1]) p_(i-1)
      + sum_(a=0)^(i-2) H[a,i-1]
        product_(b=a+1)^(i-1) H[b,b-1] p_a.
```

The recurrence uses polynomial coefficient bits and no Johnson eigenvalues.
The legacy spectral routine supplies only the value o for comparison.
An independent ascending-column elimination computes the binary rank.
Each case records the full polynomial, literal-row hash, exact rank and rank
of C squared. A polynomial bit at position d is the coefficient of x^d;
`characteristic_polynomial_hex` records all coefficients, including zero ones.

All 41 polynomials match, and all 41 lower bounds hold. In 21 cases the lower
bound is strict. These are observations in the fixed domain, not a formula
for binary ranks outside it.

## Negative controls and the nonsemisimple boundary

For `(h,k,j)=(7,3,0)`, n=35 and o=15. Its literal polynomial is
`0xffff00000`, equivalently `x^20 (x+1)^15`; its binary rank is 21.
In the lexicographic subset order, remove undirected edges `(0,32)` and
`(1,28)` and add `(0,1)` and `(28,32)`.

This switch preserves symmetry, every diagonal entry and every row degree.
Both original and corrupted matrices therefore have integer trace 35 and
integer squared trace 175. The changed polynomial is `0xfccc30000`.
The new polynomial comparison rejects it even though both historical integer
moment checks would still pass. This is deliberately corrupted input, not a
counterexample within the subset family. Changing the claimed odd multiplicity
from 15 to 16 is rejected separately.

For `(4,2,0)`, the matrix is three complementary-subset pairs, each with block
`[[1,1],[1,1]]`. Over F2 its polynomial is `x^6`, its square is zero, and its
rank is 3 while o=0. Thus **rank=o is false**, although the actual historical
lower bound remains valid. More generally, at h=2k,j=0, complement pairs give
these same blocks, so rank is `binom(2k,k)/2` and the square is zero. The tests
replay k=2,3,4,5. This elementary family corroborates the existing identity-minor
bound; it is not claimed as a new rank theorem or compiler exclusion.

The engine controls compare characteristic polynomials with a separate direct
Leibniz determinant for all 512 binary 3-by-3 matrices and 48 seeded arbitrary
matrices of orders 4,5,6. Rank is checked against exhaustive kernel enumeration
on those same matrices. Further controls cover permutation similarity,
transpose, invalid matrix shapes, corrupted source pins and a corrupted
committed polynomial. These finite checks support the implementation and do
not formally verify it for every matrix order.

## Reproduction, pins and scope

From the repository root, using standard-library Python 3.11 or later:

```sh
python3 -B research/single-intersection-spectrum-audit/spectrum_audit.py
```

Expected: `PASS_LITERAL_BINARY_SPECTRAL_AUDIT` with `completed_cases: 41`.
The command verifies exact dependency hashes, recomputes every case, runs both
rejection controls, and compares the entire fresh result to `RESULT.json`.
It also passes under `-S` and `-O`. `--write` regenerates only this package's
result. Focused tests:

```sh
python3 -B -m unittest discover -s tests -p test_single_intersection_spectrum_audit.py -v
```

`SOURCE.json` pins the actual predecessor bytes, selected record and local
claim. The last predecessor change to the spectral source was
`d55bcd62ceb8f322bcf311a5a66e94c3ac7724f0`. There is no solver, compiled library
or floating-point dependency. No provider, paid cost recurrence, Gaussian
assembly parameter, tape implementation or selected-frontier replay is changed.
The compiler, side representation and all-size multiplication obligations
remain those of the inherited construction.

## Attribution and overlap

Contribution: Lucas Steinmetz (`ljste`), with substantial OpenAI Codex
assistance in task selection, mathematical analysis, implementation and writing.
No independent human review or formal verification is claimed. Apache-2.0,
following the repository license.

The historical screen and its source are Douglas R. Colkitt's work. The Johnson
spectrum is credited to the paper above and its cited predecessors. The selected
construction retains the contributors credited in the maintainer review; this
audit supplies neither that construction nor a stronger conditional exponent.

PR #778, by `merramil`, independently addresses packing and replay of the
same historical family's large orbit Gram matrices. Its inspected head is
`f015b04c74801fa330f818d178e809c760fb5469`. This audit adds a different obligation:
literal modular characteristic polynomials and a moment-preserving corruption
control. It neither depends on nor imports #778's code. No pinned sprint issue
existed, so the claim is recorded locally in `SOURCE.json`.
