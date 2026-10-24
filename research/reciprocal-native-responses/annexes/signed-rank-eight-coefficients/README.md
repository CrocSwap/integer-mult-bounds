# Reciprocal coefficients for the fixed signed 48-port family

This annex classifies the dyadic coefficients of a fixed signed response
with eight centre rows. Exactly 65,536 responses have a dyadic inverse
and dyadic inverses for both specified principal blocks. This is a
coefficient theorem and a proof of an ordinary gauge on existing data.
It does not supply a native schedule, routed controller, complete
supplier invoice, or kappa improvement.

The [producer proof](frozen/lanes/controller-followthrough-20261017/reciprocal-centres-20261018/RECIPROCAL-CENTRES.md)
and [independent review](frozen/lanes/bridge-review-20261017/reciprocal-centres-review-20261020/REVIEW.md)
use the actual matrix payload. Here a dyadic unit matrix means a matrix
and its inverse both have entries in `Z[1/2]`.

## Complete coefficient classification

On the 48-port part, the actual matrices satisfy

```text
K K^T = 12I_8,     G^T=G,     G^2=I_48,     det(G)=1,
G K^T = K^T Lambda,     Lambda=diag(1,-1,1,-1,1,-1,1,-1).
```

For dyadic parameters `beta_v`, put `D=diag(beta_v)` and
`E=G-K^T Lambda D K`. Set `s_v=1-12 beta_v`. Then

```text
det(E) = product_v s_v,
E^-1 = G+K^T Lambda diag(beta_v/s_v) K.
```

The full 48-port response is a dyadic unit exactly when

```text
beta_v = (1-(-2)^n_v)/12,     n_v in Z.
```

This is an infinite classification. Reduction modulo three and the
dyadic-unit equation prove completeness; a finite exponent check does
not. Inversion sends each exponent `n_v` to `-n_v`.

The selected physical ports are `S=[0,7,15,36,42,46,79,89]`. Let
`L=E_SS` and let `H` be the principal block on the other 40 centre ports.
The actual selected minor has `det(K_S)=-4` and `G_SS=0`, which gives

```text
det(L)=det(H)=16 product_v beta_v.
```

Thus both principal blocks are dyadic units exactly when every beta_v
is a dyadic unit. Impose the full-response condition as well. Each
exponent must then be one of `-2,-1,1,2`:

| Exponent n | beta | s | Reciprocal beta |
| ---: | ---: | ---: | ---: |
| 1 | 1/4 | -2 | 1/8 |
| -1 | 1/8 | -1/2 | 1/4 |
| 2 | -1/4 | 4 | 1/16 |
| -2 | 1/16 | 1/4 | -1/4 |

The eight choices are independent. Different coefficient vectors give
different response matrices, so `4^8=65,536` counts distinct responses.
This finite family is closed under inversion.

All three unit conditions are necessary for this count. For example,
uniform `beta=1/2` gives two principal units but a full determinant
`5^8`, which is not a dyadic unit. Uniform `beta=3/4` gives a full unit
but does not give principal units. These are retained negative controls.

## Ordinary gauge and dimension limits

Let `T=G(S)` and let `R0` contain the other 32 centre ports. Put
`B=diag(alpha_v beta_v)`. The six-step factorization acts on arbitrary
ordinary data `(t,r)`:

```text
t <- K_T t
t <- t+K_R0 r
t <- -B t
r <- G_R0 r
r <- r+K_R0^T t
t <- K_T^T t
```

It gives H. Reversing the steps and inverting each factor gives H^-1.
Each factor is a dyadic unit under the principal-unit condition. No
initial zero, clear, or additional centre field is used. This proves
the representation on existing data; it does not price an elementary
word for every coefficient choice.

The ordered borrowed interface and its inverse have determinant one on
the 48-port part. The fixed 64-port complement has square `4I` and
determinant `2^64`. Including it gives full 112-port interface determinant
`2^-64`, not one. The distinction is explicit in the independent review.

Within this fixed signed family, `E^2=I` requires each beta_v to be zero
or `1/6`. Only zero is dyadic, so G is its only dyadic orthogonal member.
This family-specific statement does not constrain the other reciprocal
families in the parent package, including the later `E=P R` construction.

## Fresh exact checks

The producer checks both full 112-port inverse orders for six cases and
counts all 65,536 coefficient tuples through the proved determinant
formulas. The independent checker uses integer Bareiss determinants,
nine matrix cases, and a separate eight-step count recurrence. It checks
the six-step gauge and its reverse on all 40 columns in eight cases,
both ordered interface inverse products, and the fixed complement.
Exponent ranges `[-64,64]` and `[-128,128]` are controls for the proof.

Use Python 3.11 or later, the standard library, at least 3 GiB free space,
and a new output directory. From the repository root:

```sh
python3 -I -B research/reciprocal-native-responses/annexes/signed-rank-eight-coefficients/replay.py --out /tmp/signed-rank-eight-coefficients
```

Expected final line:

```text
PASS_SIGNED_RANK_EIGHT_COEFFICIENT_ANNEX
```

The [runner](replay.py) executes both unchanged checkers in normal Python
and with `-O`, one process at a time. All four receipts must match their
frozen bytes. [SOURCES.json](SOURCES.json) records the 13 unchanged source
files. The [fresh replay receipt](evidence/REPLAY.json) records the
relocated run. [ANNEX-MANIFEST.json](ANNEX-MANIFEST.json) binds the final
annex files. The older bipartite native packet is retained as matrix
source and historical context; its native emitter is not rerun here.

## Open next questions

A native realization still has to form the eight queries at legal cuts,
place the chosen scatter coefficients, preserve every helper, and verify
its phases. Routed stage composition, terminal decoding, child hosting,
precision, and a complete price remain separate obligations. This annex
does not perform new work on those questions.

The publication context remains main commit
`b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`, whose selected result names
[PR #4470](https://github.com/CrocSwap/integer-mult-bounds/pull/4470).
Historical source pins stay fixed, and no transfer to that construction
is proved. [NOTICE.md](NOTICE.md) records the source credit, license,
and substantial AI assistance.
