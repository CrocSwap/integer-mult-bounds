# Sharp error for one rounded half-shear

This contribution was produced by Nick Petalas. Apache-2.0.

## Statement

Let R be componentwise nearest-integer rounding with ties to even. Coordinates
are numbered 0,1,2,3. Define

```text
2A = [[1, 1, 0, 0],       2B = [[1, 0, 1, 0],
      [1,-1, 0, 0],             [0, 1, 0, 1],
      [0, 0, 1, 1],             [1, 0,-1, 0],
      [0, 0, 1,-1]]             [0, 1, 0,-1]].
```

For any distinct t,s in {0,1,2,3}, put S=I+E_ts/2 and

```text
y=R(Ax), z=R(Sy), F(x)=R(Bz), T=BSA, x in Z^4.
```

Then

```text
max_(x in Z^4) ||F(x)-Tx||_infinity = 9/8.
```

The middle rounding is part of the program. The comparator contains the same
half-shear without rounding. On grid h Z^4, using R_h(v)=h R(v/h) at each
rounding, the sharp error is 9h/8 for every h>0.

## Universal upper bound

Write delta=y-Ax, epsilon=z-Sy and eta=F(x)-Bz. Each coordinate of delta and
eta is in {0,+1/2,-1/2}. Only epsilon_t can be nonzero, and it is in the
same three-element set. The endpoint error is exactly

```text
F(x)-Tx = BS delta + B epsilon + eta.
```

Nearest-even rounding of a half-integer has the implication

```text
delta_i != 0 implies y_i is even.
```

For any output whose B-pair does not contain t, the middle update is absent.
If eta_j=0, the error is at most 1/2. Otherwise that pair of stored integer
inputs has odd sum or difference. At least one input is odd, so its delta
is zero. The error is at most 1/4+1/2=3/4.

For an affected output, put p=t xor 2. With the actual B-row signs
alpha,beta in {+1,-1}, the error is

```text
(alpha delta_t + beta delta_p + alpha delta_s/2
 + alpha epsilon_t)/2 + eta_j.
```

This identity also covers s=p. Its repeated occurrence does not create an
independent error variable.

If epsilon_t=0, the triangle bound is

```text
(1/2 + 1/2 + 1/4)/2 + 1/2 = 9/8.
```

Suppose epsilon_t is nonzero. Since y_t,y_s are integers, y_s must be odd.
Consequently delta_s=0. The middle operation rounded a half-integer to even,
so z_t is even. If eta_j=0, the remaining error is at most
(1/2+1/2+1/2)/2=3/4. If eta_j is nonzero, z_t and z_p have opposite parity.
Thus z_p=y_p is odd, and delta_p=0. The error is at most
(1/2+1/2)/2+1/2=1. This proves the upper bound for every integer input,
without a search assumption.

## Attainment

The following explicit inputs attain the bound. The final column is one
coordinate of 8(F(x)-Tx). Every row is evaluated by both integer and dense
interpreters during the full residue checks.

| t | s | x | output coordinate j | error times eight |
|---:|---:|---|---:|---:|
| 0 | 1 | (1,4,0,1) | 0 | -9 |
| 0 | 2 | (0,1,0,13) | 0 | -9 |
| 0 | 3 | (0,1,0,3) | 2 | -9 |
| 1 | 0 | (1,2,0,3) | 3 | 9 |
| 1 | 2 | (0,1,0,3) | 3 | 9 |
| 1 | 3 | (0,1,0,13) | 1 | 9 |
| 2 | 0 | (0,3,0,7) | 0 | 9 |
| 2 | 1 | (0,3,0,1) | 2 | 9 |
| 2 | 3 | (0,1,1,4) | 0 | -9 |
| 3 | 0 | (0,3,0,1) | 3 | -9 |
| 3 | 1 | (0,3,0,7) | 1 | -9 |
| 3 | 2 | (0,1,1,10) | 1 | 9 |

For example, t=0,s=1,x=(1,4,0,1) gives
y=(2,-2,0,0), z=(1,-2,0,0), F(x)=(0,-1,0,-1), and
8Tx=(9,-8,5,-4). Hence the complete error times eight is (-9,0,-5,-4).
The middle rounding is exact in this extremizer. Its possible nonzero
error elsewhere still needs the preceding case analysis.

## Complete finite reduction

Nearest-even rounding commutes with every even integer translation. Replace
x by x+16v, for arbitrary v in Z^4. At the first stage the displacement
16Av is coordinatewise divisible by eight, so y shifts by exactly 16Av.
After S, the displacement is divisible by four, so z shifts by exactly
16SAv. After B, the displacement is even, so F shifts by exactly 16BSAv.
The linear comparator has that same displacement. Thus the entire error
vector is periodic modulo 16 in each input coordinate.

Both verifiers enumerate all 12*16^4=786,432 pair/input cases. The primary
uses explicit butterflies and a closed signed half-rounding formula. The
separate interpreter multiplies three dense integer matrices and chooses
the nearer integer by two distances. It also compares 3,072 complete output
error vectors with Python Fraction rounding. The canonical stream of all
3,145,728 signed eighth-unit error coordinates is hashed in both checks.
This is a finite certificate, and the parity argument supplies an independent
all-input upper bound. Neither is a formal-kernel proof.

Period eight is insufficient. For t=0,s=1, the inputs (0,0,0,2) and
(8,0,0,2) give error vectors times eight (-4,4,4,-4) and (4,4,-4,-4).
The integer-shear period must therefore not be reused silently here.

## Scope and predecessors

Josie Elliston's #6140 poses the interleaved-grid-shear question. Jerry Chen /
CubeJerry's #6146 proves the different exact-integer-shear law and supplies
the two-axis model and parity context. Nick Petalas's #6129 pure-stage law
is background. No predecessor theorem, scientific code or census is replayed
as this contribution. The upper bound and half-shear witnesses above are new
work for the stated program; nearest-even parity and translation facts are
elementary and carry no literature-priority claim.

The theorem covers one positive half-shear, two distinct real Walsh axes,
exact arithmetic before each specified rounding and sufficient range.
Negative/other rational coefficients, complex gates, additional stages,
cross-fiber operations and a production compiler binding remain outside it.
There is no physical cost, reversible-history implementation, native supplier,
precision saving, kappa improvement or complete multiplication theorem.
