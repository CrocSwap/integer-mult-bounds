# Coherent line powers in the actual centre Schur operator

The actual graph has a sharp distinction between odd and even coherent
line powers. Put

```text
S_k = B Q_U^k D,       D=B^T,       BD=13I.
```

The same integer k acts at all 104 ordinary ports. The native line has
fourth power I. At every positive tensor width, `S_0=13I`, and `S_2`
has the reviewed finite translation inverse. Each odd-power operator
is singular at every width at least five. Thus replacing an odd-power
Schur inverse by the squared-line Schur inverse changes an impossible
uniform inverse into an available one. The replacement has explicit
odd arithmetic and implementation costs.

| k modulo four | Uniform conclusion |
| --- | --- |
| 0 | `S_k=13I` at every width |
| 1 | Singular at every width at least five |
| 2 | Invertible at every width; inverse has a fixed finite translation kernel |
| 3 | Singular at every width at least five |

This table concerns invertibility over the rational or complex field.
It does not say that the even cases have dyadic inverses. The inverse
of `13I` needs division by 13. The squared-line inverse has odd
denominator 2,145 in its character matrices.

## A direct actual-source obstruction

Use selected ports `A=[0,7,20,27,36,46,57,111]` and their ordinary
complement U. In this order, `B=R_A^T R_U/4`. For the five tensor-copy
characters

```text
(1,2,3,6,6),
```

the native phase at label q is

```text
i^(parity(q.1)+parity(q.2)+parity(q.3)+2 parity(q.6))
    = (-1)^(q0*q1+q0+q2).
```

The checker verifies all 512 label values directly. The phase is real,
so it is the same for Q and Q^-1. The actual 104 columns give the
following matrix, with no model replacement:

```text
          [ 1 -1 -4  7 -4  0 -5  0 ]
          [-1  5  0 -5 -4 -4  3  0 ]
          [-4  0 -3  4 -1  3  0 -1 ]
2 S_1 =   [ 7 -5  4  1  0 -4 -5  0 ]
          [-4 -4 -1  0  1  3  0 -1 ]
          [ 0 -4  3 -4  3  1  0 -1 ]
          [-5  3  0 -5  0  0  1  0 ]
          [ 0  0 -1  0 -1 -1  0  1 ].
```

Its null vector is `v=(0,0,1,0,-1,1,0,1)`. Its leading seven-by-seven
minor is exactly `-73`. Hence its rank is exactly seven. Also,
`||Dv||^2=52`, and `Q Dv` lies in the kernel of B. A nonzero centre
direction has moved into the unobserved ordinary subspace.

Append zero characters to obtain the same matrix at each larger width.
The real phase also gives the same matrix for `S_3`. Finally, `Q^4=I`
reduces every integer k to one of the four cases in the table. No
minimum singular width is claimed.

The independent checker imports no producer code. It pins the frozen
singular witness and reconstructs the graph, phases, null vector,
rank certificate, and ordinary image from the primary R and q files.
It also binds the positive result to the independent all-width
translation review.

## The squared-line inverse and its physical scope

For `T=S_2`, the exact spectra at all widths are contained in
`{+-1,+-3,+-5,+-11,+-13}`. All values occur. The character of Q squared
depends only on the XOR of the tensor-copy characters, so 512 exact
eight-by-eight checks cover every width. The finite inverse has 256
simultaneous translation shifts, 4,544 nonzero coefficients, and common
denominator `8580=4*2145`.

The independently reviewed local service applies `y += T^-1 x` to
two distinct existing FULL centre banks, with one owned field C0. It
uses zero native children. One schedule costs 114,528 scalar primitives,
8,944 body translations, sixteen real division-by-2,145 scans, and
32 completed-view maps. The alternative trades more scalar operations
for fewer maps. The source bank is unchanged; all target baselines are
arbitrary; C0 has zero output. A three-shear coded exchange is also
available. These are complete local words, not full supplier decoders.

The stage content routes give

```text
B_s = rho_A^-1 B rho_U,
D_s = rho_U^-1 D rho_A.
```

Each port route fixes its own native direction, so it commutes with
that port's Q. Thus `S_(k,s)=rho_A^-1 S_k rho_A`. The classification
and the nonzero null modes transfer to every actual stage. The physical
view translations remain part of the implementation; they are already
included in the reviewed service. This algebra does not remove those
translations from an emitted word.

## A precise positive-line section

Let the required query be `A_query=BQ_U`. A completion confined to the
unchanged image of D would have form `D H`. Its query response is
`S_1 H`. At the displayed mode S_1 is not surjective, so no H can make
that response the identity on arbitrary centre values. This also
excludes a nonlinear choice of H with values in that fixed image: a
centre value outside the range of S_1 has no preimage there.

The positive-line image instead gives the exact section

```text
K_plus = Q_U D T^-1,
A_query K_plus = I.
```

The known inverse-line section is `K_minus=q_U D/13`. Their relation is

```text
K_plus = Q_U^2 K_minus (13 T^-1).
```

The ordinary factor Q squared is a translation, and the centre factor
has the finite service above. This proves a uniform change of section
with an explicit centre code. It does not make a dense scatter free.
An additive scatter must apply the ordinary translation to the update,
or conjugate its target bank before and after that scatter. A complete
construction must also provide the centre owners needed to form the
encoded source. The two-bank additive inverse service does not by itself
give an in-place inverse on a single centre bank.

This distinction identifies the next useful construction problem:
implement the squared-line code at a cut with available centre owners,
then carry it through the physical data endpoint. A larger joint unit,
an additive shear, a restricted-input inverse, or a code that retains
the lost direction elsewhere remains outside the odd-power obstruction.

## Reproduction and scope

Run with one process from the workspace root:

```text
python3 -I -B work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/schur-power-classification/check_classification.py
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/schur-power-classification/check_classification.py
```

Both runs print `PASS_COHERENT_POWER_SCHUR_CLASSIFICATION` and produce
the same receipt bytes. The separate spectral and literal-service
reviews supply their own reproduction commands and source pins.
The complete supplier's root grid, ownership, recursive accounting,
and final physical decoder remain separate obligations. No native lower
bound, complete supplier admission, or kappa improvement is claimed.
The work builds on the campaign's native graph, phase-access proof,
singular-mode search, and translation service. OpenAI Codex assisted
the calculation and proof. No PR, push, or commit was made. Before any
future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
