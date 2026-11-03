# Nearest-grid execution of the sparse correction

This package freezes the 74-ADD correction in PR6537 at
8bc9f991afe9fde83700ff86e520230eaa4595e7. Its exact operator, low-rank
factorization and scalar saving are predecessor results. This contribution
supplies its rounded execution, sharp error contract and data inverse.

## Round the source product

For an integer numerator n and positive denominator d, let R(n/d) be the
nearest integer, with ties to even. Euclidean division gives the exact rule
in `nearest`. It has error at most 1/2 and satisfies R(-z) = -R(z).
For each literal ADD `y += c*x`, execute

```
y <- y + R(c*x).
```

The source x does not change during this gate. Subtracting the same rounded
product is its exact inverse on integer data. Reversing the gate order gives
an exact inverse for the complete correction, including all dirty public
accumulators and all 799 fields. No rounding transcript is retained.
This is the standard reversible integer-lifting principle, applied here to
the actual source program. It does not by itself supply a reversible Boolean
implementation of the temporary integer arithmetic or physical tape cleanup.

Rounding the whole sum instead is different. With ties to even,
`y <- R(y+c*x)` can lose information. The full-program control starts all
799 fields at one; this wrong rule and its apparent reverse fail to restore
thirteen fields. The placement of rounding is part of this contract.

## Exact error-transfer theorem

Let the field values lie in any real or complex normed vector space. Give each
input field norm at most M, and each permitted completed-operation defect norm
at most epsilon. Each scalar prefix is a rational linear map of those inputs
and the separate defect variables. For a row

```
z = sum_j a_j x_j + sum_t b_t delta_t,
```

its exact uniform bound is `M sum|a_j| + epsilon sum|b_t|`. The triangle
inequality proves sufficiency. Choosing all inputs or defects on one real
line with the corresponding signs proves sharpness for that row under this
independent additive-defect contract. This is not a claim that arbitrary
error signs arise from actual rounding.

The checker computes every output transfer twice: forward symbolic rows and
backward output functionals. It compares each coefficient before hashing and
retains every prefix target bound, output mass and attaining output witness.
Unchanged rows keep their previous bounds, so the update trace covers every
prefix and field. With noise only at fractional products, the new forward and
inverse both have maximum prefix and output error factor one. The ideal
prefix signal factor is 28; the final input factor is 15. An exact sign witness
attains the final factor 15. Thus, if the incoming fields have errors at most
eta, the output error from those errors and local product rounding is at most
`15 eta + epsilon` per field. This is a correction-boundary contract; it does
not estimate the preceding raw native word.

The complete comparison is:

| Program and defects | Prefix error factor | Output error factor |
| --- | ---: | ---: |
| Old 569 gates, fractional only | 36 | 21 |
| New 74 ADDs, fractional only | 1 | 1 |
| Old inverse, fractional only | 30 | 33/2 |
| New inverse, fractional only | 1 | 1 |
| Old 569 gates, every operation | 202 | 161 |
| New 74 ADDs, every operation | 61/2 | 22 |
| Old inverse, every operation | 100 | 48 |
| New inverse, every operation | 34 | 34 |

These are different defect contracts. Exact integer operations justify the
fractional-only contract for the implemented grid algorithm. A backend that
also perturbs integer ADDs must use the larger contract instead.

## Complete actual-rounding classification

The source has two disjoint integral input forms a and b. Their complete
coefficients are retained. They satisfy a[3] = b[1] = 1 and
 a[1] = b[3] = 0. The checker proves, at every fractional gate in both
directions, that its source is an integral combination of a and b with no
coefficient on any preceding defect variable. All 25 fractional divisors are
two or four. The other 49 operations are exact integer updates.

Changing either form by eight changes each fractional source product by an
even integer. Nearest-even rounding commutes with even integer translations.
Hence every fractional defect, and thus every complete prefix defect, depends
only on `(a mod 8,b mod 8)`. All 64 classes are attained by setting field3 and
field1 to the two residues and all other fields to zero. The checker exhausts
these classes separately for the forward and inverse programs. Each prefix
defect is at most 1/2 in absolute value. Both forms remain exact invariants.
The coefficient and periodicity argument extends this census to all integer
inputs; the large random tests are corroboration, not the reason for that
extension.

It follows that **every output is a nearest grid point to its exact corrected
value**, in both directions. The same statement holds at every completed
scalar prefix. At grid spacing h, the sharp per-real-coordinate bound is h/2.
With input field1 equal to h and all others zero, exact output field342 equals
h/2. Any grid output has error at least h/2 there. The implemented map attains
that lower bound uniformly, so no integer-output rule can improve its worst
coordinate error. This is a uniform grid optimum, not a runtime or circuit
minimum.

For fields with D complex coordinates, apply the same literal scalar program
componentwise. The completed field 2-norm defect is at most `h sqrt(D/2)`.
Put h+ih in field1 at every coordinate to attain this bound in field342.
Thus a consumer may use

```
output field error <= 15 eta + h sqrt(D/2).
```

No nonlinear phase or native-frame rewrite is needed inside this common-frame
correction. Its entry and exit frames are checked against the actual source.

## Range, work and optimization scope

If each integer input component has absolute value at most the integer A,
each exact prefix component has magnitude at most 28A. The rounded component
is within 1/2 and is integral, so it also has magnitude at most 28A. Numerators
of all scalar coefficients have magnitude at most three. The largest temporary
product is therefore at most 84A. A signed width W with `2^(W-1) > 84A`
suffices for the input, product, increment and output checks. This is a
sufficient bound, not a minimum-width result. Overflow is rejected.

Per real coordinate and direction there are 74 product-numerator evaluations,
74 data additions and 25 fractional roundings. Integer coefficient handling,
parity/tie tests, shifts, storage, checks and movement remain work. For D complex
coordinates multiply these counts by 2D. The original scalar allowance 696 is
retained as the source's exact-arithmetic allowance; this package does not
silently reuse it as a rounded Boolean or tape tariff.

The source's wider 78,408-program cost search remains credited prior work.
This checker enumerates every unit pivot, unit signed scale and direction
order, then selects the 44 programs with the source minimum `(696,74)`.
Every one has forward and inverse fractional factors `(prefix,output)=(1,1)`
and ideal prefix factor 28. The recorded source choice already attains the
sharp grid bound. No new gate-count optimum or improved pivot is claimed.
Changing rounding is useful here; selecting a different tied program is not.

## Remaining obligations

The exact data bijection does not prove zero auxiliary bits in a physical
implementation. The integer products and quantizer need a charged reversible
arithmetic and tape realization. The preceding native maps, entry magnitudes,
full coordinate count, owned erasure, compiler and outer/recovery assumptions
remain separate. This contribution changes neither the paid profile nor kappa,
and does not promote the selected frontier or claim independent acceptance.
