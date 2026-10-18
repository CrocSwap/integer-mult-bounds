# Separate proof and implementation review

**Result:** no mathematical blocker was found in the stated formal-model
theorem. Root-orbit inversion counts give simultaneous sharp lower bounds
for every finite register count, including arbitrary restored dirty roles,
for every finite-rank Coxeter system. Orbit-constant positive prices and the
rank-priced extension have the claimed exact minima. The attaining circuits
are verified in the full group algebra, separately from the lower-bound
root representation.

This review was performed by a separate OpenAI-assisted agent after reading
the completed proof and both implementations. It is not independent human
review, a proof-assistant certificate, or a supplier admission.

## Reviewed mathematical and executable bytes

The paths in this table are relative to this package. These hashes identify
the reviewed versions, rather than asserting that future edits inherit this
review automatically.

| File | SHA-256 |
| --- | --- |
| `PROOF.md` | `2e20ac459ed1524fca510b58d2792004e44024fd96b9f775501c47786c8325f8` |
| `verify.py` | `0a5a2adc28e6f2e235ae91632f8b1758f70c8f40c0d2f877e5eabf6006b892be` |
| `independent.py` | `427e6c898e92ffe02a1d81808b085b3c4a1ee7e2ababd7233a558c38046b6daa` |
| `RESULT.json` | `55f5dbdb2f9080ccb055c913bcd01f767f0bad2ecf92d313e807d4131447118f` |
| `test_package.py` | `4f36ce50aaf7179024067e9e571590d15fcad3f50c2e93fa27a1b7c563158c32` |

## Mathematical checks

The root module is the algebraic direct sum on distinct **root labels**.
Real root coordinates are not reduced modulo two: a root and its negative
remain different basis elements. Finite formal sums act by maps with
finite-support columns. Each group element has finitely many root
inversions, so the crossing block of every finite formal matrix has finite
rank even when the group and its root set are infinite. The two-block
product identity and the rank-of-images inequality therefore apply without
an analytic limit or an unjustified finite truncation.

For each invariant root orbit, a simple generator crosses exactly its own
simple root. Tensoring that single crossing with the scalar coupling gives
rank one for the original gate alphabet, and exactly `rank(N)` for the
expanded alphabet. Free scalar maps preserve the cut. The diagonal target
has the direct sum of its targets' inversion blocks, so ranks add over
heterogeneous targets and include every dirty role. Interleaved scalar
mixing and its possible final residue are handled correctly.

The right-descent recurrence is correctly oriented:
`Inv(w) = {alpha_s} disjoint union s Inv(ws)` when `s` is a right descent.
Since `s` preserves each root orbit, induction counts the letters of every
orbit in a reduced expression. Coordinate-projector products then attain
the bound coefficientwise in the full formal algebra. The proof now gives
the explicit chronological convention for the signed-permutation sorting
word; no endpoint is inferred solely from a represented operator.

The root-orbit and reflection-conjugacy formulations of the price condition
agree in the normalized geometric representation. This restricts prices:
in type A the adjacent generators are conjugate, so arbitrary unequal
adjacent-generator prices remain outside the theorem. The displayed A2
braid is a valid boundary example, not a sharing counterexample.

For type B, the chosen last-nonzero-coordinate sign convention gives
`neg(w)` short-root inversions and `inv(w)+nsp(w)` long-root inversions.
Negating a negative first entry decreases only the short count; swapping
an adjacent descent decreases only the long count. The proposed sorting
procedure terminates and attains both counts simultaneously. The `B_1`
case and central sign-reversal formula are correct.

The arbitrary-coupling extension is valid in characteristic two:
`([s]+1)^2=0` implies that every `I+([s]+1)N` is involutive, independently
of `N^2`. The crossing rank is still `rank(N)`. This is a formal rank
tariff; it is not a claim that a nilpotent coupling is one physical address
call, or that rank-two calls may be charged as unit invocations.

The standard root facts were checked against Heckman's
[Section 4.2](https://www.math.ru.nl/~heckman/CoxeterGroups.pdf#page=73),
particularly Corollaries 4.12--4.13 and Theorem 4.14. Their published
mathematical content is an explicit dependency, not newly proved here.

## Executable checks and observations

Both implementations were read. The primary checker uses exact integer
Cartan matrices, explicit root-orbit crossing blocks, and binary role-matrix
coefficients keyed by group matrices. The latter use the faithful geometric
group representation, while preserving all group-algebra coefficients;
they do not identify distinct formal sums merely because their root-module
operators agree. The independent implementation uses signed windows,
weighted Dijkstra, and a different packed-row coefficient engine. It
imports neither the producer nor its receipt.

The following commands passed under CPython 3.12.15, with assertions
disabled:

```sh
python3.12 -I -O -B research/coxeter-root-tariff/verify.py
python3.12 -I -O -B research/coxeter-root-tariff/independent.py
python3.12 -I -O -B research/coxeter-root-tariff/test_package.py
```

Normal and optimized primary/independent replays also passed under CPython
3.14.7, and its optimized six-test suite passed. Default replay does not
regenerate the receipt; the producer's `--write` explicitly regenerates it.

| Evidence | Checked domain |
| --- | --- |
| Exact root orbits and inversion recurrence | All 1,946 elements of A2, A3, A4, B2, B3, B4, D4, F4 and G2 |
| Arbitrary binary couplings | All 530 matrices through three roles, at both B2 generators: 1,060 involution/rank checks, including 24 nonzero square-zero matrices |
| Full formal endpoints | All 64 B2 target pairs with a third dirty role; all 256 single-gate omissions differ from the required endpoint |
| Infinite-group finite probe | 136 distinct affine-A2 integer matrices through radius nine, 327 transitions and alternate-word inversion-set agreement |
| Independent type-B arithmetic | All 4,282 signed permutations in B1 through B5; 12,846 tariff comparisons under three price pairs and 62,694 directed edge checks |
| Independent dirty-state circuits | Nine heterogeneous two-target cases with one through three dirty spectators; 75 omitted-call, nine dirty-column-leak and nine wrong-order controls |
| Artifact and sensitivity checks | Six optimized public-CLI test groups, including a read-only Git-free export, source-pin loss/corruption, typed and duplicate-key receipts, and a rank-undercharging code mutation |

The B2 kernel fixture is correctly discriminating. The formal norm has
eight nonzero group-algebra terms, but both four-root orbits have stabilizer
size two, so its entire root-module image is zero over F2. Adding that norm
in a dirty off-diagonal entry changes the formal endpoint while leaving the
represented endpoint unchanged. A separate signed-coordinate calculation
confirmed the two-to-one multiplicities.

One artifact weakness was corrected during review: ordinary Python
container equality accepts Boolean/integer and integer/float substitutions.
The final verifier uses canonical JSON with type-distinct encodings and
rejects duplicate keys. The public-CLI tests now exercise those failures.
The rank-two boundary check is also sensitive to a concrete mutation that
truncates every computed rank to at most one. The root-sign-mod-two check
is a boundary demonstration; it is not a separate general model validator.

## Contribution boundary and unrun obligations

The symmetric-group theorem and the finite- and infinite-dihedral tariffs
are predecessors, including the already established arbitrary-register D16
case. The infinite-dihedral arbitrary-coupling extension in
[PR2716](https://github.com/CrocSwap/integer-mult-bounds/pull/2716), inspected
at `74c96ae917fe16160db357c361058b3a6417a440`, is also prior work. The new
scope is the uniform Coxeter/root-orbit theorem and its non-dihedral
weighted consequences; it is not a new claim for those covered special
cases. No literature-priority claim is made.

The all-parameter and infinite-group conclusions rest on the written proof.
The finite checker is neither an exhaustive circuit search over arbitrary
word lengths nor a formal verification of the cited root theory. The
noncrystallographic families are covered by that proof, without numerical
root enumeration here. The affine execution stops at radius nine.

No native address implementation, physical scalar invoice, selected supplier
admission, recursive moment, selected cold replay, new exponent, hosted-CI
pass, or human/kernel proof review is established by this review. Unequal
prices within one conjugacy class, additional quotient relations, extra
unit-price address primitives, and concave rank prices remain outside the
proved model. The parent contributor owns final metadata, overlap freshness,
publication, and any checks beyond the commands recorded above.

Prepared with substantial OpenAI assistance. New review text is Apache-2.0.
