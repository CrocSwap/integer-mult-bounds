# Caller grid and magnitude reserve for the complete QQ16 decoder

## Contract

Fix the byte-exact PR2540 word and its native representation. At their entry
times, the sixteen retained F0 fields, 224 current B1 fields and owned-buffer
dirt have Gaussian components in `2^-f Z`, of componentwise magnitude at most H.
The sixteen earlier and 224 current arrays are treated as independent for this
bound. Actual F0/B1 trajectories are a subset. Let lambda be any positive
integer number of payload tensor layers. Spectators are arbitrary.

Every declared caller-event boundary is representable exactly with **f+4lambda+3
fractional bits**, and has componentwise magnitude at most

    H * (48 + 48*2^ceil(lambda/2) + 144*2^(4lambda))
      <= 153*2^(4lambda) H < 2^(4lambda+8) H.                 (1)

Thus **4lambda+8 magnitude guard bits** suffice above a strict power-of-two
input magnitude bound. At lambda=1 the certified envelope is 2448H, the
fractional reserve is 7 and the integer guard is 12.

The theorem assumes exact outputs from atomic native children and cover maps.
It does not bound their internal recursion or rounding. The inherited B1
history boundary is a new input boundary, not a free execution of B1. Exact
caller rounding at the stated boundaries is a no-op; the retained exact
endpoint proof therefore gives exact borrowed-field restoration and scratch
cleanup there. This is not a full finite-precision supplier implementation.

## Quadratic phase kernel

For n binary address coordinates, write a native Fourier phase as

    q(x) = sum_i a_i x_i + 2 sum_(i<j) b_ij x_i x_j  (mod 4).

A sum of signed parity characters has this form because parity equals its
linear sum minus twice its pair sum modulo4. Its polarization is the symmetric
binary matrix B with diagonal `a_i mod 2` and off-diagonal b_ij:

    q(x+h)-q(x)-q(h) = 2 x^T B h  (mod 4).

Let r=rank_F2(B). For normalized Fourier coefficients

    A(t)=2^-n sum_x i^q(x) (-1)^(t.x),

autocorrelation gives

    |A(t)|^2 = 2^-n sum_(h in ker B) i^q(h) (-1)^(t.h).

On ker B, q is even and q/2 is a binary linear character: evenness follows
by setting x=h in the polarization identity. Thus exactly 2^r coefficients
are nonzero, each with squared magnitude 2^-r. Each coefficient is a Gaussian
dyadic. Repeatedly dividing an integer sum of two squares by 4 shows that its
nonzero components are `+-2^(-r/2)` on one component when r is even, or
`(+/-1 +/- i)2^(-(r+1)/2)` when r is odd. Consequently:

- the exact nonzero component denominator exponent is ceil(r/2);
- the real-component infinity norm of its convolution kernel is
  `2^ceil(r/2)`, counting both real and imaginary input components.

The latter is a box-norm statement, not the unitary Euclidean norm. For C1,
the box gain is 2. These facts are elementary Fourier/Gaussian-sum identities;
the contribution here is their exact source-bound application to all caller
prefixes, not a new general Gaussian-sum theorem.

For lambda tensor layers, q is a direct sum of lambda copies. Its polarization
rank is r*lambda, so both formulas use ceil(r*lambda/2). Scalar coefficients
stay unchanged. This is exactly the convention in the pinned BRIDGE-REVIEW
section on tensor powers; raising scalar coefficients to lambda is invalid.

## Applying it to the unchanged word

The retained symbolic replay writes each field as a sum of `(source, g)` terms
with dyadic scalar coefficients c, combining equal pairs and deleting zeros.
Here g is the actual cover-owner matrix, not a payload-only permutation. For
output frame F and source frame S, the physical term has relative phase

    F - gS,

up to the inherited owner reindexing. Transporting phase axes by g is required
because the source owner is dg. Actual payload translations remain in F and
are checked by the unchanged native replay. Left multiplication by the output
owner changes coordinates invertibly and preserves the polarization rank.

Such a term has denominator debt

    denominator_v2(c) + ceil(r*lambda/2),

where denominator_v2 includes cancellation by the numerator. Its real box
gain is `abs(c)*2^ceil(r*lambda/2)`. Summing these gains is always a valid
triangle bound, whether or not different terms can attain their signs at the
same input. We do not need any attainment or independence claim to prove (1).

The observer appends one read-only callback after each original event, keeping
all predecessor validation and endpoint checks. Every event index is observed
exactly once; every changed live field is checked. Unchanged fields retain
their earlier bounds. Newly introduced scratch dirt has the input bound until
its charged CLEAR. Native child interiors are deliberately not observer events.

Across the actual word the only relative phase ranks are 0, 1, 8. The rank-8 scalar
debt maximum is 3. The rank-0/rank-1 debt maxima and their lambda=1 bounds are
recorded in RESULT. Since ceil(lambda/2)-1 <= lambda-1, the largest denominator
debt is bounded by 4lambda+3 for every lambda>=1. The saved rank-8 term has scalar
coefficient 1/8 and a nonzero one-layer kernel coefficient 1/16. It yields 1/128;
six extra fractional bits cannot represent that isolated term. Other terms
with the same source and different owner maps may cancel it. This term
witness proves no lower bound on the complete field, even in the independent
temporal-source relaxation, or on the correlated physical F0/B1 trajectories.

For each changed field collect absolute scalar weights `(a0,a1,a8)` by phase
rank. Put `X=2^ceil(lambda/2)` and `Y=16^lambda`. Its triangle bound is
`a0+a1 X+a8 Y`. The exact finite scan verifies, for every field, with
`(b0,b1,b8)=(48-a0,48-a1,144-a8)`,

    b8 >= 0,    8b8+b1 >= 0,    b0+2b1+16b8 >= 0.

For all lambda>=1, `X>=2` and `Y-16>=8(X-2)`. Therefore

    b0+b1 X+b8 Y
      >= (b0+2b1+16b8)+(8b8+b1)(X-2) >= 0.

This proves the stated all-layer envelope from the full literal prefix census,
rather than extrapolating finite lambda samples. Finally `X<=Y/8` and `1<=Y/16`
give `48+48X+144Y <= 153Y < 256Y`. No sharp magnitude minimum is claimed.

## Evidence boundaries

The written phase and envelope arguments carry the quantifiers in lambda and
payload dimension. Direct Fourier enumeration of every quadratic phase through
three variables checks the independent elimination algorithm, both parities,
zero Fourier coefficients and the real box norm. The retained source checker
supplies the actual native word/frame semantics and both logical inverse
orders. Its exact receipt and twelve original controls are rerun unchanged.

This proof does not supply the entry bounds H,f from F0/B1, preservation through
an approximate child, physical stream/tape movement, retained-bank hosting,
an output consumer, an improved invoice, or all-size supplier admission.
