# One signed-metric carrier for each reflection centre

This packet gives a complete 112-field scalar code. It stores the 16
independent readers of the new reciprocal response in 16 existing
fields. The code, its inverse, and its inverse-adjoint use only real
dyadic arithmetic. They use no extra field and no odd division.

The physical input and output metrics are diagonal signed powers of
two. Thus a diagonal correction converts the inverse-adjoint code to
the primal code. This correction does not mix fields that have
different spatial frames.

This is a code for the rank-16 difference `E-P`. It is not a
rank-16 code for `E-I`. The actual physical `P` is a paid field code,
not a free permutation.

## Source and exact blocks

The source is the actual
[reciprocal model](../../../oblique-native-20261017/signed-metric-reciprocal-20261020/model-normal-v2/RESPONSE.json.gz),
with decompressed SHA256
`df2d2028c99028db3c645b3311d7f31ff96efe72f6f9257f99157ce030ff43d0`.
It fixes every port, pair code, block, sign, and metric.
The [checker](check_signed_sixteen.py) pins that file and the exact
arithmetic helper. The source model has eight blocks of size six
and eight blocks of size eight.

For a block of size `n=m+2`, write its fields as
`(a0,...,a(m-1),b,c)`. Put

```text
K = J^-1 = diag(1,...,1,-(m-2),-(m-2)),
u = (1,...,1,m-2,0)^T,
l = (-1,...,-1,1,0),
R = I + u l.
```

Then `l u=-2`, `K l^T=-u`, and `l K l^T=2`.
It follows that `R^2=I` and `R K R^T=K`.
The mode permutation `P` exchanges `b` and `c`, and `E=P R`.

Use the following rows in the stated output order. Here
`s=a0+...+a(m-1)`.

| Output | Six-mode row | Eight-mode row |
| --- | --- | --- |
| a0 | `-s+b` | `-s+b` |
| a1 | `a2-a3` | `a4+a5-b/2` |
| a2 | `a0-a1` | `a4-a5` |
| a3 | `c` | `c` |
| a4 | — | `a0-a1` |
| a5 | — | `a2-a3` |
| b | `a0+a1-a2-a3` | `a0+a1-a2-a3` |
| c | `s-2b` | `a0+a1+a2+a3+2a4+2a5-2b` |

Let these block matrices be `C_m`. Direct row products give

```text
n=6: C_m K C_m^T = diag(2,2,2,-2,4,-4);
n=8: C_m K C_m^T = diag(2,1,2,-4,2,2,4,-4).
```

Both determinants are `-8`. The first row is `l`. Every other row
annihilates `u` and has a zero diagonal entry. Thus the first row
changes sign under `R`; every other row is fixed.

These identities also give an explicit inverse over the dyadic
ring. If the displayed Gram matrix is `G_m`, then
`C_m^-1=K C_m^T G_m^-1`. No appeal to numerical conditioning or to
an invertible rational matrix is needed.

## Actual physical pair code

Let `H` be the pinned pair code on the 48 large ports. It is the
identity on the other 64 ports. On each large pair, `H H^T=2I`.
The chosen large-block order is

```text
(centre, pair_difference_a, pair_difference_b,
 negative_difference, contrast, negative).
```

The centre, negative-difference, contrast, and negative positions
each form complete physical pair matchings. The other two
positions both have output norm two. Therefore the mode input and
output metrics are constant on every ordinary physical pair.

Let `H_R^-1` undo `H` on the ordinary pairs and act as the identity
on the selected pairs. Define

```text
C = H_R^-1 C_m H.
```

This choice keeps each selected large row equal to its individual
reader `l H`; it does not mix the two centre readers in one pair.
The selected small row is `l`.

The exact selected ports, in reader order, are

```text
0,27,36,111,20,7,57,46,1,3,6,8,17,18,24,23.
```

Let physical `K=H^-1 K_m H`. It is diagonal. The checker proves

```text
C K C^T = G,
C^-1 = K C^T G^-1,
C^-T = G^-1 C K.
```

The physical `K` has 80 entries `1`, 16 entries `-2`, and 16 entries
`-4`. The physical `G` has the following entries:

| Value | Count |
| --- | ---: |
| -4 | 24 |
| -2 | 8 |
| 1 | 8 |
| 2 | 48 |
| 4 | 24 |

The eight large centre norms are four. The eight small centre
norms are two. All 16 selected rows equal the source's actual
`reflection_L` rows, in the same order.

With `Z` equal to `-1` on the selected fields and `1` elsewhere,

```text
C R = Z C,
C R C^-1 = Z,
C P E = C R.
```

The last identity keeps the order of all factors. It does not
identify `C E` with `C`.

## Native support

The checker verifies every ordinary diagonal of both `C` and
`C R`, in the physical chart and in the actual native mode chart.
All are zero. Every ordinary mode row stays within its original
six-mode vertex or eight-port clique.

Consequently the complete dense cyclic/clique transfer grammar
has a slot for every required ordinary transfer of `C` or `C R`.
This is a support statement. It does not by itself emit a new
native word, prove a target phase, or price a changed endpoint.
In particular, a native word for `E=P R` cannot be reinterpreted
as a word for `R` without a separate operation.

The proposed clean service emits the ordinary response `C_R`
directly, removes the 16 selected target paths, advances those
targets to FULL, applies `C` to the completed source bank, and
performs the selected signed exchanges. A complete native
emission must check this sequence separately.

## Complete scalar words and price

The word applies the actual 24 pair codes, then the 16 block
codes, then undoes the pair code on the 20 ordinary pairs.
The block factorization uses only dyadic-unit pivots. Every row
exchange, ADD, sign, and scale is present in the word.

All words pass exact replay on 640 independent complex fields.
The 528 fields outside the coded bank remain unchanged.

| Word | Real scalar primitives | Instructions | Prefix row one-norm | Binary height |
| --- | ---: | ---: | ---: | ---: |
| C | 5564 | 739 | 24 | 3 |
| C inverse | 5564 | 739 | 9 | 3 |
| Literal inverse-adjoint | 5564 | 739 | 5 | 3 |
| K, then C, then G inverse | 6092 | 875 | 32 | 3 |

These are exact scalar-word bounds. They do not include the
internal arithmetic of a recursive native child or rounding.
All events are complex-linear real scalar operations. Each
event is valid at a common complex spatial frame.

## Diagonal conversion of the complete clean dual

Write the two banks as `x=(a,u)` and `y=(z,v)`, with the first
coordinate set equal to the selected 16 fields. Define

```text
w = Cx;
F_C(x,y) = ((-z,w_R),(w_P,v+w_R)).
```

This map accepts arbitrary `x` and `y`; no baseline is zero.
For `D(G)=diag(G,G)`, the exact complete identity is

```text
D(G) F_C^-T diag(J,G^-1)(x,y)
    = ((-z,w_R-v),(w_P,v)).
```

The checker proves this identity on all 640 independent fields
using the literal same-order inverse-transpose of the clean
scalar word. It does not transpose a desired endpoint and
assume that the implementation follows.

Conjugate by the selected-bank exchange at both endpoints.
The result is

```text
w = C(z,u);
Bswap_C(x,y) = ((w_P,w_R-v),(-a,v)).
```

The two metric wrappers cost 1264 real scalar primitives before
any fusion. Each wrapper scales one field at a time. Thus it
commutes with that field's spatial frame. It does not require a
common frame across distinct fields.

This scalar identity does not grant the selected-bank exchange
at arbitrary native endpoints. The intended Q-entry native
service has equal Q frames on the two selected inputs and equal
FULL frames on the two selected outputs. A complete native
packet must bind that fact and every adapter to its field.

## Reproduction, credit, and limits

Run from the workspace root, with fresh output directories:

```text
python3 -I -B work/centre-encoding-campaign-20261014/lanes/new-core-transfer-20261017/low-displacement-20261020/signed-sixteen-20261020/check_signed_sixteen.py --out <new-directory>
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/new-core-transfer-20261017/low-displacement-20261020/signed-sixteen-20261020/check_signed_sixteen.py --out <another-new-directory>
```

The expected status is `PASS_SIGNED_SIXTEEN_COMPLETION`.
Normal and optimized payloads and receipts match byte for byte.

The root lane supplied the reciprocal reflection family. The
oblique lane bound its actual physical placement and metric.
The bridge review lane supplied a distinct signed-metric basis
and a general extension. The cover lane derived the complete
clean-dual conversion. This lane supplied the stated sparse
bases, paid physical code, and exact replay. AI assistance was
used.

This packet supplies a full scalar code and exact native
support. It leaves the changed native service, routed caller,
terminal decoder, finite-precision guard, recursive helper
hosting, and complete supplier cost open. It does not allocate
the 416 auxiliary roles as a free centre cache.

No PR, commit, push, or publication is authorized. Before any
future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
