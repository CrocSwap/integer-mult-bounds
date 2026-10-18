# A weighted rank cover for the residual C5

## Statement and exact boundary

Use the physical cycle `E0,...,E4 = (10,12,23,35,16)` in PR2782's
56-plane geometry. Its complete two-label planes, in that order, are

```text
(508,73), (146,265), (194,134), (304,56), (50,193).
```

Labels are vectors in F2^9; the pairing is their binary dot product.
Every plane has Gram matrix I2. Two distinct planes are orthogonal exactly
when their indices are neighbors on this five-cycle. These finite premises
are reconstructed from the two authenticated canonical-main inputs.

A strict scalar fitting matrix K has ten scalar coordinates. Its diagonal
entries are one. All other entries within a plane are zero, as are all
entries between nonorthogonal planes. Entries between orthogonal planes
are free. Suppose, over Q, R or C, that

    K = sum_(t=1)^T u_t v_t^T

for any finite T. Transpose is ordinary transpose. Factors may be asymmetric;
coefficients may be negative, complex or have arbitrary denominators.
Let A_t and B_t be the subsets of planes touched by u_t and v_t. A nonzero
component in either scalar coordinate touches that complete plane.
The complete-plane tariff is

    c(A,B) = rank_F2 [x dot y : x in complete planes A,
                              y in complete planes B].

This is the inherited complete-plane tariff, not a component-specific native
cost. The claim is that the total tariff is at least 20, and 20 is attained.

## Six forced identity blocks

For a plane set H, let b_H(A,B) be one when A and B both meet H, and zero
otherwise. Use the following blocks and weights.

| H | weight | rank of K restricted to H |
|---|---:|---:|
| {1} | 2 | 2 |
| {3} | 1 | 2 |
| {4} | 1 | 2 |
| {0,2} | 1 | 4 |
| {0,3} | 1 | 4 |
| {2,4} | 1 | 4 |

Every two-plane block here consists of nonorthogonal planes, so its strict
principal block is I4. A singleton gives I2. A term restricted to such a
block has rank at most b_H(A_t,B_t). Rank subadditivity therefore gives

    sum_t b_H(A_t,B_t) >= rank K[H,H].

There is no positivity or symmetry assumption in this argument.

## The changed physical cover

On this named physical cycle, all ordered plane-support pairs satisfy

    c(A,B) >= 2 b_{1}(A,B) + b_{3}(A,B) + b_{4}(A,B)
              + b_{0,2}(A,B) + b_{0,3}(A,B) + b_{2,4}(A,B).

This is a finite premise about actual rectangular binary pairing matrices,
not an assertion about every abstract five-cycle. The verifier checks all
32 by 32 ordered pairs, including empty sides and zero-cost terms. It charges
both labels of every touched plane. The difference between the left and right
sides has the exact histogram

```text
difference       0    1    2   3
ordered pairs  496  410  110   8
```

A second implementation constructs explicit nine-coordinate labels and uses
dense binary row elimination. It agrees on every tariff, via the ordered
table digest in RESULT.json, and on every difference. Neither implementation
uses floating-point arithmetic. Floating linear programming only proposed
the integer weights during discovery; it is not a proof dependency.

Sum the physical inequality over all terms and apply the six identity-block
rank bounds. The result is

    sum_t c(A_t,B_t) >= 2*2 + 2 + 2 + 4 + 4 + 4 = 20.

Arbitrarily many zero-cost terms are harmless: their nonnegative weighted
block count is forced to zero by the same checked inequality. There is no
term-count bound, enumeration of decompositions or equality-trace assumption.

## Attainment and boundary controls

For each cyclic i, take

    u_i = e_(i,1) + 2 e_(i+1 mod 5,0),
    v_i = e_(i,1) + (1/2) e_(i+1 mod 5,0).

These five ordinary-transpose terms put one on every diagonal coordinate.
Their only other entries join neighboring, orthogonal planes and are free.
Each term touches two orthogonal I2 planes on both sides, so its binary
tariff is four. The complete fit has cost 20. Replay checks all 100 scalar
entries exactly. It also checks a signed asymmetric variant. The separate
implementation uses ten singleton terms for an independent upper bound 20.

Thus the sharp complete-plane cost on this core is 20.

## What this adds and does not establish

PR3268 at `ee5d4f466e6e44a1897896324a36aa4c64cf3912` lists this exact cycle
among five residuals of its fixed weighted-cover and equality-trace method.
The changed six-block cover resolves this one residual directly. Its other
four residuals are not settled or used here. PR3256 supplied the earlier
single-core weighted-rank and trace method; this proof needs neither its
pending executable nor its equality-case census.

This theorem is local to the named physical labels, strict scalar mask and
complete-plane tariff. Local bounds cannot be added across overlapping cores.
It supplies no global decoder floor, native implementation, dirty restoration,
physical caller, hosting or precision invoice, supplier admission or new kappa.
The selected construction is unchanged. The proof is written mathematics with
exact finite premises, not a proof-kernel or independently human-reviewed proof.
