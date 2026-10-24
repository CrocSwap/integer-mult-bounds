# The natural clean forward-backward-forward word

Use the clean exchange at stage 0, its selected-swap inverse adjoint
at stage 1, and the clean exchange at stage 2. Do not put a physical
bank reset between these calls. The actual D25 views preserve the
declared mixed types. The endpoint has a dyadic content inverse and
a remaining sixteen-row phase query.

This packet gives the routed physical endpoint and a complete operator
terminal with 208 positive line operations. It does not emit native
recipes or a host for those line operations. It does not treat the
96 ordinary Y fields as FULL before their stated normalization.

## Sources and types

The checker binds the same literal D25 views and clean native payloads
as `../coupled-data-split-20261020/TYPED-SPLIT.md`. It imports only
the exact phase-ring and sparse-row functions from that checker.
It reads the stored forward and backward content matrices from their
pinned payloads. It does not derive those matrices from the endpoint
claimed here.

Use the same selected set P, ordinary set R, and matrices H and D.
Thus `D=-H*`. Define

```text
G_s = diag(R_(rho_(s,p))),
H_s = G_(s,P) H G_(s,R),
D_s = G_(s,R) D G_(s,P),
G_0 = I.
```

Every G is only a portwise orthogonal route. It is not a Fourier
prefix. Let `Fprev_s=F_(9+8(s-1))` and let Fext_s act on axes
9 through `9+8s-1`. The literal entry and exit views obey

```text
Ventry_s Fprev_s = Fext_s Q G_s,
Vexit_s F_(9+8s) = F_(9+8s) G_s.
```

At a natural boundary, the global types are

```text
X = Fprev x,
Y_P = Fprev z,
Y_R = Fprev q_R v.
```

The next physical input, after the literal views, is therefore

```text
X = Fext Q G_s x,
Y_P = Fext Q_P G_(s,P) z,
Y_R = Fext G_(s,R) v.
```

This is exactly the Q-entry clean type with common exterior Fext.
No Q passes through H or D. The decoded contents change only by G_s.

At stage 0, use the already emitted I-entry formation variant.
Let the original physical inputs be

```text
X0 = Q(a,u),
Y0 = (z,v).
```

All 224 data fields can be arbitrary. These equations define the
initial local contents; they are not extra gates. The I-entry variant
costs sixteen more units of native mass than the Q-entry variant.
It avoids an initial selected q on z.

## Actual routed endpoint

Put

```text
alpha = a+H_0 u,
K = v+u+D_0 alpha.
```

After the first clean call the content is

```text
X = (-z,u),
Y = (alpha,K).
```

X and selected Y are FULL at F9. Ordinary Y has frame `F9 q_R`.
The actual stage-1 call has decoded local input
`G_1(-z,u,alpha,K)`. After Bswapclean and its literal exits, the
global content is

```text
X = (alpha+H_1 K, W),
Y = (z,K),
W = -v+(D_1-D_0)alpha.
```

The same natural boundary rule applies at stage 2. The final physical
endpoint is

```text
X_P = -F25 z,
X_R = F25 W,
Y_P = F25 beta,
Y_R = F25 q_R r,

beta = alpha+H_1 K+H_2 W,
r = u+D_1 alpha+D_2 beta.
```

This formula includes every original borrowed input. The selected
borrowed fields are restored by a sign. The ordinary borrowed fields
still contain the centre correction `(D_1-D_0)alpha`.

## Exact content inverse and the physical obligation

Since `K=r-D_2 beta-W`, the old centre can be written as

```text
alpha = beta-H_1(r-D_2 beta-W)-H_2 W
      = (I+H_1 D_2)beta-H_1 r+(H_1-H_2)W.
```

Then

```text
u = r-D_1 alpha-D_2 beta,
a = alpha-H_0 u,
v = -W+(D_1-D_0)alpha.
```

All these content maps are dyadic. No inverse of E, odd division,
or additional independent centre bank occurs in these equations.
The checker verifies the inverse as a content identity. This does
not make the physical access free.

The final W and beta are in FULL fields. Therefore the terms
`(I+H_1 D_2)beta` and `(H_1-H_2)W` use legal past FULL views.
The term `H_1 r` reads the ordinary Y holes, whose physical content
is `q_R r`. A phase-aware query service is still required for this
term. It cannot be replaced by a scalar read of those fields.

For the desired original data, the ordinary output is `Q_R u`.
The free translation L_R changes the final `q_R r` baseline to
`Q_R r`. The required correction is then

```text
Q_R D_1 alpha + Q_R D_2 beta.
```

The selected original data are `Q_P a`. A complete terminal must
produce this selected output, make the ordinary correction, restore
v, and preserve all borrowed fields. A low-rank factorization is
not a native implementation of those tasks.

The reader and scatter occur as a joint problem. The content inverse
above can be used to test a phase code without assuming a free query
or a free final normalization.

## A complete operator terminal with 208 positive line operations

There is a direct baseline that uses no extra field. It first puts
ordinary Y in FULL. It then uses a sequence of dyadic shears. This
sequence does not require `I+H_1 D_2` to be a unit.

Starting from the displayed physical endpoint, use these operations:

```text
1. Apply Q_R to the 96 ordinary Y fields.
2. Y_R <- Y_R-D_2 Y_P.
3. Y_P <- Y_P-H_1 Y_R.
4. Y_P <- Y_P+(H_1-H_2)X_R.
5. X_R <- -X_R+(D_1-D_0)Y_P.
6. Y_R <- Y_R-D_1 Y_P.
7. Y_P <- Y_P-H_0 Y_R.
8. X_P <- -X_P.
9. Apply Q to all 112 Y fields.
```

In steps 2 through 8, all fields are in the common F25 FULL frame.
The H and D expressions denote their legal FULL affine views, with
the literal translations. They are not bare current-chart shears.
After step 2, ordinary Y is `t=r-D_2 beta`. After step 4, selected Y
is alpha. Step 5 restores v. Steps 6 and 7 give u and a. Therefore
the exact physical result is

```text
X = F25 Y0,
Y = F25 X0.
```

The bank exchange is stated explicitly. A final exchange can put the
data in the designated bank if the complete caller requires it.
This result uses the initial I-entry variant. With initial selected
Q entry, restoration of `Y0_P=Q_P z` has a further sixteen-line cost.

The checker composes this terminal on all 224 input columns. It checks
that each routed H or D shear is an affine FULL view. This gives a
complete operator terminal with 208 positive line operations. It does
not include a serialized native recipe or a global host for those
line operations.

The direct coefficient implementation has eight H or D shears, each
with the same 216 coefficients and a cost of 2,048 old real primitives.
The 112 signs add 224 primitives. Thus a direct scalar upper bound
is 16,608 primitives. Six routed shears use at most 1,344 per-field
affine map calls in total. These counts do not include the side maps
of the 208 line recipes or the final bank permutation. No map is
priced as a constant-time operation on a complete stream.

This is a baseline for a joint improvement. No claim is made that
208 line operations fit the complete supplier budget.

## Local bill and remaining assembly

The initial I-entry clean call has native profile

```text
1392 H1 + 64 H2 + 48 H3 + 16 H9.
```

Each later Q-entry call has

```text
1392 H1 + 64 H2 + 48 H3 + 16 H8.
```

The sum is native mass 5,392. The three local scalar invoices sum to
25,800 real primitives. These prices include the native local words
and their local adapters. Adding the direct terminal gives 208 more
positive line operations and at most 16,608 more real primitives.
The literal global stage views, terminal views, line side maps, and
bank permutation have their own stream and address costs. No reset
or extra field is added.

The route proof is exact in dimension 25 and tensors over all spatial
columns. The complete cover sweep must finish before the next stage.
The inherited helper restoration is supplied by the local native
packets. This checker does not replay the global helper host, the
recursive bill, or the full precision proof.

## Verification

Run each command with a new output directory:

```text
python3 -B check_no_reset.py --out <new-directory>
python3 -O -B check_no_reset.py --out <another-new-directory>
```

The normal and optimized receipts are byte-identical. Both initial
entry variants pass all 224 arbitrary input columns and all 224
physical output rows. The final operator matrix has 176,144 nonzero
input-operator terms. The direct terminal passes on the I-entry
variant. The checker also verifies all 896 natural-boundary phase
identities, all 224 terminal FULL-view identities, and the dyadic
content inverse.

The first two exploratory runs were interrupted before they produced
a receipt. They used a slower phase substitution. The final checker
uses the same exact polynomial rule with sparse bit iteration.
It compares that rule with the original dense rule on all 224
actual terminal view/line combinations.

No PR, commit, or publication is authorized. Read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`
before any future PR description.
