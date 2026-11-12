# Proof for the pinned block

This contribution was produced by Nick Petalas. Apache-2.0.

## The finite object

Let `M` be unpaidmoon's pinned 216-by-216 integer matrix for `B=4 A_1` in
`research/a1-joint-216-charpoly/evidence/matrix.json`. Let `v_i` be the pinned
signed-orbit basis vectors from that package. Their supports are disjoint and
their nonzero entries are signs. Consequently the Gram matrix is the positive
diagonal matrix `D`, with `D_ii = |support(v_i)|`.

The predecessor supplies this historical block and its interpretation. The
following argument uses the literal pinned matrix; it does not rederive the
block, the characteristic polynomial or any predecessor kernel certificate.

## A completeness certificate

Put `d=12480`, and take the integer matrix `Q` in PROJECTOR.json. Exact integer
multiplication verifies `Q^2=dQ` and `MQ=QM=0`. Entrywise comparison verifies
`DM=M^T D` and `DQ=Q^T D`. Gaussian elimination modulo the prime 1000003 gives

```text
det(M+Q) = 905182 (mod 1000003).
```

A zero integer determinant has zero residue in every modulus. Thus `M+Q` is
invertible over the rationals. These finite identities are the certificate;
the verifier checks every matrix entry and the modular elimination directly.

Let `P=Q/d`. Idempotence gives `P^2=P`, and `MQ=0` gives
`image(P) subset kernel(M)`. If `x` lies in `kernel(M)`, then

```text
(M+Q)(d x-Qx) = d Mx - MQx + d Qx - Q^2 x = 0.
```

Invertibility implies `Qx=dx`, so `Px=x`. Hence `image(P)=kernel(M)`.
The weighted self-adjointness of `Q` gives `DP=P^T D`, so this is the unique
orthogonal projector onto that kernel in the positive inner product defined
by `D`. Also `PM=0`; since `M` is self-adjoint, its image is the orthogonal
complement of its kernel. Thus `P` is precisely the zero spectral projector,
and it commutes with `M` and `A_1`.

The exact trace is 24, hence this idempotent has rank 24. This is a consequence
of the new projector certificate, not a substituted modular-rank argument.
The proof does not require the predecessor characteristic polynomial or its
algebraic-multiplicity count.

One way to discover the matrix is to choose a rational kernel basis `K` and
form `K (K^T D K)^(-1) K^T D`. The committed certificate is independent of
that construction procedure: its identities alone prove the result.

## The denominator is sharp

Since `Q` is integral, `dP` is integral. Exact reduction of four specified
entries gives

```text
P[10,60] = 9/4160,   P[4,4] = 47/156,
P[6,6] = 71/260,    P[0,0] = 5/416.
```

Each fraction is reduced. Any positive integer `e` for which `eP` is integral
must be divisible by all four denominators. Their least common multiple is
12480. Therefore the least such `e` is exactly
`12480 = 2^6 * 3 * 5 * 13`. Independently, the verifier checks that the gcd of
`d` and all entries of `Q` is one, which proves the same minimality by Bezout.
No single entry is asserted to have denominator 12480.

## Consequence for exact dyadic operations

A finite linear straight-line program with dyadic rational scalar coefficients
and dyadic constants has a dyadic rational linear part. This follows by
induction on additions, subtractions and scalar multiplications. Adding clean
zero coordinates, or arbitrary dirty coordinates that must be restored, does
not change this fact about the induced input-output block.

The displayed entries of `P` have unavoidable odd denominator factors 3, 5
and 13. Therefore such a program cannot implement `P` on the pinned input and
output coordinates. The same conclusion holds for a polynomial in `A_1` with
dyadic coefficients, since `A_1=M/4` is a dyadic matrix.

This is a fixed-basis exact obstruction. It is invariant under input and
output changes of basis whose matrices and inverses are dyadic: if an adapted
matrix were dyadic, converting back would make `P` dyadic. The statement does
not grant a free rational basis conversion. It makes no claim about other
invariant projections, nonlinear operations, approximation, paid odd division,
physical routing, recursive costs or a multiplication theorem.
