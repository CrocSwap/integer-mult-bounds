# Exact helper-return contract for the local F0 reference

## Statement

Fix the authenticated PR3101 finite native reference and its 26,099-event F0
word. This is its 512-complex-coordinate local reduction, not the complete
73-axis payload or owner cover. Initialize every field to zero except L224,
whose entry is an arbitrary vector z in C^512. The eight owned private fields
therefore enter zero. In exact arithmetic, the final state is zero outside
L224, and

```
L224_out = G z,
G = C_0 C_1 ... C_8 = C tensor-power 9,
C = 1/2 [[1+i, 1-i], [1-i, 1+i]].
```

The coordinate lines commute because they act on different tensor factors.
The source word records L224's ordinary endpoint frames as 0 and 1. The
statement identifies the numerical return in the reference's common array
coordinates. It does not identify distinct endpoint representations for free.

Consequently literal numerical return holds exactly on a complex
136-dimensional subspace. The mismatch G-I has complex rank 376 and Hilbert
operator norm 2. Constants return literally. The coordinate delta at zero
returns a vector supported on all 512 complex coordinates. All these statements
concern the isolated L224 input subspace. No claim is made here about other
input columns, the full helper block or full-cover native semantics.

## Source-bound all-column certificate

All operations in this exact reference are complex-linear. Its scalar
coefficients are Gaussian-dyadic, its monomials are signed coordinate
permutations with powers of i, and its native lines have denominator 2. CLEAR
sets an owned private field to zero and is also linear. Skipping a zero child
in the source interpreter does not change the mathematical linear map.

For each of the 512 unit-basis inputs in L224, track a nonnegative Hilbert-norm
bound h at every field. Start h_224=1 and all other bounds at zero. An ADD
`d += c*s` changes h_d to h_d+|c|h_s. SCALE multiplies by |c|. A monomial or
completed native recipe is unitary and leaves h unchanged. CLEAR sets it to
zero. Every matrix coefficient's real and imaginary parts are bounded by h.
The unitary premise follows directly for these local numerical recipes from
the signed permutation and the displayed two-by-two C; it is not an appeal to
an unexecuted full-cover compiler.

Separately track an exponent q such that every real and imaginary matrix
coefficient lies in 2^-q Z. An ADD takes the maximum destination/source exponent
after including the coefficient denominator. SCALE adds that denominator
exponent. A rank-r recipe adds r, monomials add zero, and CLEAR resets q to zero.
These recurrences may overestimate cancellations. The exact source traversal
returns

```
max h = 43339242709/64,
max q = 66.
```

The audit checks the same event inventory as the authenticated reference.
Let B=2^106 and simultaneously encode all basis inputs by the real entry
`z_j=B^j`. Execute the entire literal word with exact Gaussian-dyadic arithmetic.
The resulting L224 vector equals the independently computed Gz. Every other
711 field is exactly zero. No per-column result is inferred from an unbounded
or probabilistic evaluation.

To see injectivity, multiply each endpoint difference coefficient by 2^66.
The target G has denominator at most 2^9 and every coefficient has modulus at
most one. Each resulting integer real or imaginary coefficient has absolute
value at most `(43339242709/64+1)*2^66`, strictly below B/4. For a nonzero
integer polynomial `P(t)=sum a_j t^j` with |a_j|<B/4, take its highest nonzero
coefficient a_k. Its leading term at B has magnitude at least B^k. The sum of
all lower-term magnitudes is less than

```
(B/4) * (B^k-1)/(B-1) < B^k.
```

Thus P(B) cannot vanish. Apply this separately to the real and imaginary
parts of each field coordinate. The packed equalities prove all 512 complex
basis columns, and complex linearity proves the stated arbitrary-z identity.

`independent.py` executes the same source dispatcher with separately written
fixed-grid integer scalar, monomial and Gaussian-line arithmetic. Its quantum
is 2^-75. All divisions are checked for exactness. It compares every endpoint
with `W^-1 diag(i^weight) W`, computed by a separately written Walsh transform.
Both implementations share source loading, event dispatch and the conservative
packing bound. They are arithmetic corroboration, not independent audits of the
source dispatch or the original Clifford construction.

## Fixed subspace and sharp mismatch

Let w_s be the Walsh character `w_s(x)=(-1)^(s dot x)` for s in F2^9. The
constant and alternating eigenvectors of one C factor have eigenvalues 1 and
i. Therefore

```
G w_s = i^weight(s) w_s.
```

The 512 Walsh characters form an orthogonal complex basis. The multiplicities
for eigenvalues 1, i, -1 and -i are respectively

```
136 = binom(9,0)+binom(9,4)+binom(9,8),
136 = binom(9,1)+binom(9,5)+binom(9,9),
120 = binom(9,2)+binom(9,6),
120 = binom(9,3)+binom(9,7).
```

This gives fixed dimension 136 and mismatch rank 512-136=376. Unitarity gives
`||G-I|| <= 2`. A weight-two Walsh character is negated, so equality holds.
The primary audit executes this character through the actual source word,
rather than only through the closed-form target.

For the coordinate delta e_0, the coefficient at x is

```
(G e_0)_x = ((1+i)/2)^(9-weight(x)) * ((1-i)/2)^weight(x).
```

Every coefficient is nonzero and its squared modulus is 1/512. The exact
vector has a common denominator 32 and real/imaginary numerators in {-1,1}.
This is the explicit nonconstant witness in RESULT.json. The source word also
executes the constant-vector control and returns it literally.

Finally `G^-1=C_8^-1 ... C_0^-1`. Nine negative coordinate lines implement this
inverse in the local reference and restore every isolated helper input. The
packed inverse check covers all basis columns. This gives an algebraic
compensation, not a free frame adapter or a paid physical implementation.

## What the contract does and does not decide

A norm-preserving return and a constant-input restoration fixture do not prove
literal return of an arbitrary numerical helper. If a caller permits the
source's frame-relative return, this calculation is compatible with restoration
and is not a defect. If it demands the original common-coordinate array, it
must restrict the entry to the fixed subspace or provide and charge an adapter.
Increasing arithmetic precision alone cannot change this exact endpoint map.

This result does not refute the source's logical restoration contract or its
native proof. It does not contradict PR3235's completed-output error bound,
PR3226/3270's sufficient exact grids or PR3258's rounded-information bound.
It changes none of their premises. It supplies a precise calibration of one
remaining caller/restoration distinction. All other helper/data input columns,
B1, physical ownership, movement, recursive tariffs, the F17 consumer,
all-size compilation and supplier admission remain outside the certificate.
