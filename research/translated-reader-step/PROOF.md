# The further rational reader shear

This scoped proof and construction were produced by Nick Petalas. Apache-2.0.

## Inputs and new operation

Work over the commutative ring R = Q[C2^9], with tau_g tau_h = tau_(g xor h).
Use the actual rank-30 factorization supplied by Ali Romman's PR5646, after
Nick Petalas's PR6677 translated basis. Write J for its 112 by 30 scatter and
L for its 30 by 112 gather. The cited input contract gives LJ = 0 and the
reader response JL. These premises and the native source application are not
audit claims of this package. Source manifests pin their exact input bytes.

Indices are zero based. Let

```text
A = I_30 - (1/5) E_(0,1),       A^-1 = I_30 + (1/5) E_(0,1).
```

Since E_(0,1)^2 = 0, these are inverses over R. Define L' = AL and
J' = JA^-1. This changes exactly the gather row and scatter column

```text
L'_0 = L_0 - (1/5)L_1,         J'_1 = J_1 + (1/5)J_0.
```

Every other row or column is unchanged. Thus

```text
J'L' = J A^-1 A L = JL,
L'J' = A L J A^-1 = 0.
```

This proves the exact operator identity in the group algebra. It remains true
under every representation by nine commuting involutions, in particular the
supplied positive-column tensor representations. The basis is absorbed into
the factors; no additional runtime A or A^-1 pass is presumed free.

## Complete dirty-bank endpoint

For arbitrary data x0 and arbitrary dirty bank z0, run the four shears

```text
z += L'x
x += J'z
z -= L'x
x -= J'z
```

After the first two, z1 = z0 + L'x0 and
x1 = x0 + J'z0 + J'L'x0. The third gives

```text
z2 = z0 + L'x0 - L'(x0 + J'z0 + J'L'x0) = z0,
```

because L'J' = 0. The last gives x2 = x1 - J'z0 = (I+JL)x0.
Every dirty value is restored, and the data response is identical to the cited
input word. This argument assumes no clean scratch, discarded bank, fresh
centre, or free COPY/CLEAR operation. It concerns this recoder; it does not
remove the native section's separately required bank or implementation costs.

## Exact enumerated invoice

The finite factor construction gives the following complete counts.

| Quantity | Cited translated input | New factors |
|---|---:|---:|
| Scatter coefficients | 220 | 228 |
| Gather coefficients | 9,940 | 9,928 |
| Four-shear coefficient ADDs | 20,320 | 20,312 |
| Nonidentity translation applications | 20,320 | 20,312 |
| Axis-translation units | 91,924 | 91,852 |
| Common denominator | 960 | 4,800 |
| Maximum absolute coefficient | 9/8 | 9/8 |
| Scatter absolute row-sum bound | 43/16 | 43/16 |
| Gather absolute row-sum bound | 72 | 72 |

The new gather row has twelve fewer terms. The new scatter column has eight
more. Each factor appears twice, so the net saving is 2(12-8) = 8 ADDs.
Every group element is charged for each coefficient occurrence. Pricing
its direct axis decomposition by popcount(g), the complete translation-weight
histograms for weights zero through nine are

```text
input: [0, 852, 0, 7048, 0, 8776, 0, 3374, 0, 270]
new:   [0, 844, 0, 7076, 0, 8752, 0, 3370, 0, 270].
```

Their weighted sums differ by 72 units. A backend restoring the source layout
after every coefficient ADD would use two route passes, with invoices 183,848
and 183,704. These are declared logical routing units, not physical tape time.
Coefficient multiplication and address access are not priced as free.

At denominator 4,800 the largest absolute numerator is 5,400. No new odd prime
appears, but the common denominator has one more factor of five. The same
factor-norm bounds give the conservative prefix/suffix bound

```text
B = ((1+72)(1+43/16))^2 = (4307/16)^2.
```

A gather or partial coefficient pass has stacked infinity norm at most 73;
a scatter or partial pass at most 59/16. Every prefix and suffix of the
four-shear word, or its signed inverse, contains at most two of each.
This bounds the exact logical maps uniformly in payload volume. It does not
price rational arithmetic interiors or rounded precision.

## What the certificate establishes

The verifier reconstructs the cited factors only to apply this new step.
It compares the entire two-mode product J0 L0 + J1 L1 before and after,
with all 14,320 nonzero baseline coefficients and any possible new positions,
checks the inverse operation and every untouched vector, and enumerates all
metrics above. A separate literal four-shear executor checks one dense payload
and a nonzero dirty bank on all 512 addresses. Eight rejecting controls detect
specific algebraic and input faults. No predecessor scientific suite is run.

The input identities are cited premises; the elementary basis identity and
the arbitrary-input endpoint above prove the new universal implication.
Finite execution corroborates the concrete factor expansion and instruction
ordering. The contribution is one new explicit factor pair, with no claim to
an optimum, new kappa, physical supplier, admission or complete multiplication
theorem. A complete arithmetic and physical caller remains unproved.
