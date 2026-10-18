# Three queries for a centered odd-kernel native BIT shear

This is a local recursive-interface construction and a scoped query lower
bound. Ordinary ADDRESS interchange and ordered affine tape streams remain
premises. There is no new supplier, kappa, or formal multiplication proof.

It answers the explicit non-dyadic limitation left open by
[PR840](https://github.com/CrocSwap/integer-mult-bounds/pull/840)
(`research/dyadic-query-pair`): the PR840 lowering specializes to every odd
modulus for dyadic powers, and states that a non-dyadic power introduces prime
exclusions into that particular word. Here the odd kernel is fixed to **3**,
the completed endpoint uses `a = ±3·2^j`, and every excluded modulus is named.

## Object

Use the same six ADDRESS fields and unipotent push `h` as PR521/PR840, with

```text
s=(1,0,1,-1,0,-1)^T, r=(1,0,-1,-1,0,1)^T,
M(k)=I6+(k/4)s r^T,   h = array permutation of M(1).
```

For each integer `j >= 0` and sign `σ ∈ {±1}`, set `a = σ·3·2^j`. The completed
DATA endpoint is

```text
F_a(x,y,z)=(x+(h^a+h^-a)y, y, z).                 (1)
```

VALUE addition is over F2. Source `y` and every spectator remain arbitrarily
dirty. The target requires exclusive access until the completed boundary.

## Lowering of every signed odd-kernel power

Put `c = k/4` for `k = ±3·2^j`. The same seven-event word as PR840 applies:

```text
z2 <- z2-z0
z3 <- z3+z0
z5 <- c*z5+(1+c)*z0-c*z2-c*z3
CHILD_C(0,5)
z2 <- z2+z0
z3 <- z3-z0
z5 <- -(1/c)*z5+(1/c-1)*z0+z2+z3.                  (2)
```

The algebraic identity `M(k)` is unchanged for any nonzero integer `k`. The
diagonal units are `1`, `c`, and `-1/c`. For `k = ±3·2^j`, the numerators and
denominators of these diagonal units have only the prime factors two and three.
All control-coefficient denominators also have only these factors; their
numerators need not be units (for example `1+c=7/4` at `k=3`).
Therefore (2) specializes to **every odd modulus not divisible by 3**. Moduli
divisible by 3, and every even modulus, are excluded from this particular
lowering. No all-odd-radix claim is made.

## Completed pair fusion

The chronological fused program is identical in form to PR840:

```text
x <- h^-a x
x ^= y
x <- h^(2a) x
x ^= y
x <- h^-a x.                                      (3)
```

The three target permutations multiply to the identity, and the VALUE endpoint
is (1). Relative to two separate completed PR677-style shears for `h^a` and
`h^-a` (four queries, four XOR scans), the fused word uses **three ordinary
children, eighteen affine events and two XOR scans**.

## Three queries are necessary

The PR840 determinant argument applies verbatim with any nonzero integer unit
power `a` on an odd full-order orbit: zero or one query cannot match (1); two
queries force opposite exponents and then collapse to the identity after
comparing Laurent coefficients. The finite two-query census in the verifier
corroborates the `a = ±3` case on dimensions 2–4; the written argument is the
universal exclusion inside the stated query/XOR alphabet.

## Complete typed costs

With the same notation as PR840 for child cost `C`, lowering `L_k`, XOR `X`
and routing `R`,

```text
B_a <= 4 C + 2 L_a + 2 L_-a + 4 X + R_b,
F_a <= 3 C + 2 L_-a + L_2a + 2 X + R_f.
```

The middle lowering uses `k = 2a = ±3·2^{j+1}` and therefore a different
coefficient table. No physical runtime saving is asserted for every finite
implementation. No supplier admission, precision/tape transfer or new kappa
follows.

## Evidence boundary

The checker compares (2) to the independent closed form `M(k)`, specializes to
named admitted and excluded moduli, checks Laurent endpoints and a two-query
census, and replays dirty BIT columns on `(Z/5)^6` and `(Z/7)^6`. An independent
module rebuilds the matrix identity `M(-a)M(2a)M(-a)=I` without importing the
primary verifier. Negative controls omit fused events, break the doubled middle
power, and reject modulus 3 and even rings.
