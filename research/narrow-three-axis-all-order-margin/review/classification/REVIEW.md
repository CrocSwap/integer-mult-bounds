# Independent review of the all-order Gaussian classification

## Conclusion and scope

**PASS for the assigned finite classification obligations; no blocking flaw
found.** An independent determinant reconstruction verifies all 3,360
representatives, every claimed leading polynomial, all lower powers of `w`
vanishing, the full first homogeneous Taylor polynomial, and the stated mass,
gradient and six-center bounds. Independent coordinate-word grouping verifies
coverage of all 40,320 orders in classes of size twelve.

This review concerns Sections 2 and the algebraic certificate inputs to
Section 3 of `run/gaussian-all-order-quantitative/PROOF.md`. It does not review
the separate analytic inequalities, source selectors, Gaussian aliases,
inverse identities, prime certificates, prime availability, or outer caller.
Those remain with the root review. No source or author worktree was edited.
No foundational assumption or selected conditional bound changes.

The reviewer is a separate OpenAI worker from the author. This is independent
exact-method review, not independent human review or proof-kernel acceptance.

## Sources reviewed

Canonical repository base: `e54523517d0f03e58352e647c403a5af3e525a57`.
The author's working proof and data were read from the assigned run directory;
the exact bytes are bound in `RESULT.json` and checked unchanged at the end of
the replay. In particular:

| File | SHA256 |
| --- | --- |
| `PROOF.md` | `85f820586326b51b41b73feea2edfe5426a39659440d2b04431ec9c6e24a795a` |
| `classify_leading.py` | `2422df199a4cfae4ee3caa26340d0bbe9b1bf0b82706e6990afcc4bdfac121cd` |
| `leading-classification.json` | `44480be14012ea83d7adb1287bafbf9ebb7edb49d5038a959c3429ee913cae67` |

The primary generator uses sparse multivariate arithmetic and a determinant
subset recurrence. Its second path uses column multilinearity and scalar
Bareiss determinants at six centers. The new review path imports neither
program and uses neither determinant algorithm for the classification.

## Independent exact determinant method

Set `b=2^25`. Apply Kronecker substitution

```
u = b,  x = b^9,  r = b^81,  w = b^729.
```

Construct the literal three-factor tensor by ordinary two-by-two Kronecker
products. Construct the displacement by subtracting the shifted array.
Compute its determinant using the division-free Berkowitz characteristic
polynomial recurrence in

```
Z / (b^(729*(d+1))),
```

where `d` is the certificate's claimed first lower-entry degree. The claim
selects how much to compute, but does not supply the coefficients or a
vanishing assumption. Every coefficient of `w^0,...,w^d` is decoded and
compared. A false smaller degree produces zero or a different polynomial;
a false larger degree exposes a nonzero decoded lower plane.

### Why the reconstruction is exact

Each displacement entry has at most two monomials. Each tensor monomial
uses each upper variable at most once. Every eight-entry determinant product
therefore has upper exponents at most eight, so radix nine separates them:

```
e_u + 9 e_x + 81 e_r < 729,   0 <= e_u,e_x,e_r <= 8.
```

Different `w` degrees occupy separate 729-digit planes. Terms of `w` degree
at least `d+1` are zero in the residue ring. The entire determinant has
coefficient mass at most

```
8! * 2^8 = 10,321,920 < 2^24 = b/2.
```

Balanced base-`b` decoding therefore recovers every retained signed integer
coefficient uniquely. This is an exact coefficient encoding, not a sampled
numerical evaluation or a floating-point approximation. Ordinary carries in
the integer arithmetic are allowed: balanced decoding after all cancellations
recovers the unique bounded final coefficients.

For completeness, the Berkowitz recurrence used here follows from the block
decomposition `A=[[a,R],[S,C]]`. If the characteristic coefficients of `C`
are `p_0,...,p_(n-1)`, with `p_0=1`, the new vector is the lower triangular
Toeplitz product whose first column is

```
1, -a, -RS, -RCS, ..., -RC^(n-2)S.
```

This follows by expanding
`det(tI-A)=(t-a)det(tI-C)-R adj(tI-C) S` and the polynomial adjugate.
It is a polynomial identity over every commutative ring and requires no
division or invertible pivot. At dimension eight the constant characteristic
coefficient has the positive determinant sign. The implementation is also
cross-checked against a separate scalar Bareiss routine on 80 dense,
permutation and singular matrices of sizes one through eight.

## Complete order coverage

The review groups every permutation of the eight vertices by three binary
coordinate words: each word records one coordinate along the complete order.
The orbit key is the smaller of the sorted three words and their sorted
simultaneous complements. Sorting forgets only axis permutation; complementing
all three words forgets only full vertex complementation.

For a complete cube ordering the coordinate words are distinct, and the
twelve group elements act freely. The exhaustive coordinate-word grouping
finds exactly 3,360 groups, each of size twelve. Its lexicographic minimum
orders agree exactly with the supplied representatives. This method does not
generate the author's vertex-map list or reuse its `seen` orbit traversal.

The mathematical determinant symmetries are valid: axis permutation relabels
the three upper variables, and simultaneous bit complementation transposes
the tensor. Since `E(A^T)=E(A)^T`, full complementation preserves determinant.
No partial complementation or order reversal is assumed here. Testing every
center permutation pays the upper-variable relabellings used by the orbit
reduction.

## Primary truncation and exponent audit

The primary subset recurrence correctly expands the determinant of the first
`k` rows and the selected `k` columns. Its sign is the parity of the selected
columns lying to the right, which agrees with expansion along the last row.
Every intermediate monomial is a product of at most `k<=8` entry monomials.
Thus each upper exponent is at most eight, strictly less than the primary
four-bit radix sixteen; packed upper additions cannot carry into a neighboring
upper variable or the lower-degree field. The common lower exponent is stored
in the unbounded part above bit twelve.

Because all lower degrees are nonnegative, discarding terms above `cap`
commutes with addition and multiplication in the quotient by `w^(cap+1)`.
The first nonempty truncation consequently proves lower-degree vanishing as
an identity in all three upper variables. This argument is independently
confirmed by the complete residue reconstruction, not accepted solely from
the primary code. The largest upper exponent actually observed in a leading
polynomial is seven; the rigorous no-carry bound remains eight.

## Taylor degree, mass and gradient

Starting from each independently reconstructed leading polynomial, the review
performs full substitutions `u=1-delta_0`, `x=1-delta_1`, `r=1-delta_2` by
three univariate Horner recurrences. It uses no binomial-coefficient routine,
and computes the whole translated polynomial before taking its first nonzero
total degree. Therefore all lower Taylor degrees are checked to vanish, and
the complete leading homogeneous polynomial is compared coefficient by
coefficient with the certificate.

The complete census agrees:

| First `w` degree | Taylor degree / class count |
| --- | --- |
| 0 | 0 / 1277; 1 / 575; 2 / 80; 3 / 12 |
| 1 | 0 / 775; 1 / 337; 2 / 84; 3 / 14; 4 / 1 |
| 2 | 0 / 124; 1 / 55; 2 / 3; 3 / 4 |
| 3 | 0 / 5 |
| 4 | 0 / 14 |

There are 2,677 distinct leading polynomials. Exact evaluation of every
reconstructed Taylor polynomial at all six permutations of `(33,47,62)/64`
gives minimum absolute value `7/131072`.

The independently computed maximum weighted coefficient mass is

```
max sum_e |Q_e| 2^(e_0+e_1+e_2) = 6656.
```

For a monomial `u^a x^b r^c`, the absolute coefficient mass after replacing
each variable by `1-delta` is `2^(a+b+c)`. The triangle inequality therefore
gives precisely the claimed uniform bound on the full translated polynomial.
No cancellation is assumed in obtaining this upper bound.

The independently computed maximum leading gradient bound is 156. For a
homogeneous polynomial of degree `K`, on `[0,1]^3`,

```
sum_i |partial_i T(c)| <= sum_e |T_e| sum_i e_i
                            = K sum_e |T_e|.
```

Thus the formula used by the primary code is a valid bound, including `K=0`.
This review verifies these certificate constants; the separate continuous
remainder inequalities that use them remain in the root's analytic review.

## Replay, controls and limitations

Run:

```
python3 -B -O run/gaussian-all-order-independent-review/verify_independent.py
```

The full 3,360 determinant reconstructions take approximately 31 seconds in
this environment. `RESULT.json` records all results and source hashes;
`replay.log` records the execution. Every check uses an explicit exception,
so optimized Python does not disable validation.

Three controlled false certificates are rejected: a changed leading
coefficient at degree zero, a changed leading coefficient at degree four,
and an inserted nonzero lower-`w` coefficient below a genuine degree-four
case. The separate scalar determinant comparisons validate the new recurrence
implementation on additional shapes and singular cases.

This is a complete independent finite verification of the assigned algebraic
classification, with explicit mathematical justification for the encodings
and quotient operations. It does not constitute a formal proof of the whole
Gaussian source theorem or the retained multiplication framework. Credit the
author's classification and proof and their stated #7599/source lineage;
the new contribution here is the independent exact reconstruction and review.
Apache-2.0; prepared with substantial OpenAI assistance.
