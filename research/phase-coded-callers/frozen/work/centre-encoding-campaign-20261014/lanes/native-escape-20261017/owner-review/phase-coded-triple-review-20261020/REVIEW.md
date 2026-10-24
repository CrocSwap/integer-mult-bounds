# Independent review of the actual phase-coded triple

The stated physical endpoint is correct. The three FULL shears give

```text
X = -F25 q Y0,       Y = F25 q X0
```

for Q entry on the selected borrowed fields. For initial I entry, only
the sixteen selected X outputs omit q. There is no material local
finding. The residual q is an actual operator. This review does not
admit it as a free terminal or a recursive input type.

The review binds the producer proof with SHA256
`5eb5eba5d3bed38faf9e411ca4a9a6f8e67765966011e93dec96f2300613756f`,
the producer freeze with SHA256
`0ee32fe22f42cffce2a9673f0dc95496a4b4bb8b11a534f77a11f5fe9c7aeb4b`,
and the completed producer receipt with SHA256
`44a1c03836ba47af92965dc7d2bb716d0f94d03dd54cb3122eeaa9f1d08a3cc3`.
The local controller freeze has SHA256
`284e6239ae3287bb139497fe610e67def239ad50697f230b61ac7c7280fb4b75`.
`SOURCE-MANIFEST.json` gives all exact paths and source hashes.

The checker imports only the frozen independent phase engine from
the preceding owner review. It imports no producer checker. It does
not repeat the native 640-column transcript or the producer's expanded
global matrix. Instead, it checks the local data matrices, proves the
ordered block composition, and checks the actual D25 frame identities.

## Binding to the stored local maps

The ordered selected set P has sixteen ports:

```text
[0,27,36,111,20,7,57,46,1,3,6,8,17,18,24,23].
```

R is the sorted complement of 96 ports. The local source and the actual
row-code source have the same selected set, ordinary set, and code.
The line labels agree with the D25 view source. From those matrices,
the checker obtains

```text
C = [[I,H],[0,I]],       D = -H^T.
```

It reconstructs all 224 independent data columns of the zero-transfer
forward body:

```text
F_zero(a,u,z,v) = (-z,u,a+H u,v).
```

It derives the inverse, checks both inverse product orders, and takes
its transpose with the actual selected-wire conjugation. This gives
all stored columns of

```text
B_zero(a,u,z,v) = (z,u+D z,-a,v).
```

The physical forward prefix is `Y_R += X_R`, before every input
adapter. Since physical X has type Q and ordinary Y has type I,
this adds `Q_R u` to v. The backward prefix is `X_R -= Y_R`;
it changes u to `u-q_R v`. Composition with the two zero bodies gives
the stored operator rows

```text
F_Q(a,u,z,v) = (-z,u,a+H u,v+Q_R u),
B_Q(a,u,z,v) = (z,u+D z-q_R v,-a,v).
```

All 224 rows and columns agree exactly with the serialized maps. Each
of the 96 nonconstant line terms remains attached to its original
input port. The checker does not replace Q or q by a scalar.

The native source receipt checks both providers, all 640 independent
local inputs, and all 416 arbitrary helper returns. This review binds
that receipt and all files in its freeze. Native helper restoration is
an inherited premise, not a second native replay.

## Literal route and phase proof

Let `G_s=diag(rho_s,p)` contain only the orthogonal routes. Every actual
route is an involution and fixes its own q_p. All local line labels
lie in the root nine axes. The literal physical views are

```text
Ventry_s,p = T_(rho_s,p(entry_X)) rho_s,p,
Vexit_s,p  = T_(exit_X) rho_s,p.
```

The X and Y translations agree. At each port of stages 1 and 2, the
checker verifies these six identities:

```text
Ventry_s Fprev_s     = Fext_s Q G_s,
Ventry_s Fprev_s q   = Fext_s G_s,
Vexit_s Fnext_s      = Fnext_s G_s,
Vexit_s Fnext_s q    = Fnext_s q G_s,
Vexit_s F25         = F25 G_s,
Vexit_s Vexit_s     = I.
```

There are 1,344 identities. The checker applies each word from right
to left and records phases in the input-character coordinates. For
binary x, a parity has the exact expansion

```text
parity(v dot x) =
sum_i v_i x_i - 2 sum_(i<j) v_i v_j x_i x_j       (mod 4).
```

Thus the linear coefficients and the 300 quadratic coefficients
determine the phase on all 25-bit characters. This is an exact identity
check, not a character sample. The route matrices are also checked.
The identities tensor over every spatial column, at every width.

The ordinary Y input at each natural boundary has type `Fprev q_R`.
Its entry view therefore gives `Fext G_R`, which is the required
ordinary local input type. X and selected Y give `Fext Q G`.
The common exterior acts on the other axes and can be removed for
the local root-axis calculation. At exit, the content operators are

```text
H_s = G_(s,P) H G_(s,R),
D_s = G_(s,R) D G_(s,P).
```

Only each route's own Q line is commuted with that route. No Q is
commuted through H or D. Omission of the entry translation fails all
224 controls. Treating the ordinary input as FULL fails all 192
ordinary-port controls.

## Ordered block proof and the middle boundary

Define arbitrary initial contents by

```text
X0 = Q(a,u),       Y0 = (Q_P z,v).
alpha = a+H0 u.
```

These definitions do not add gates. Invertibility of Q makes them
valid for every physical input. Initial I entry instead has `Y0_P=z`.

The first two decoded states are

```text
after F_Q0:  (-z,u,alpha,v+Q_R u),
after B_Q1: (alpha,R,z,v+Q_R u),
R = u+D1 alpha-q_R(v+Q_R u) = D1 alpha-q_R v.
```

Without a middle correction, the third call has selected Y content
`alpha+H2 R` and ordinary Y content

```text
v+Q_R u+Q_R R = Q_R(u+D1 alpha).
```

Its ordinary output frame is `F25 q_R`. The adjacent `q_R Q_R`
therefore cancels on the left of the entire expression. Ordinary Y
is FULL because of this identity, not because of which input data
occurs in that field.

For the shorter placement, complete the entire stage-1 cover sweep.
All local calls must have returned their helpers. At this boundary,
X_P and X_R both have frame F17. Apply the physical FULL shear

```text
X_R -= D1 X_P.
```

The literal stage-1 exit views implement this operation on F17.
The shear uses no ordinary Y field and does not enter an open helper
call. It changes R to `-q_R v`. The last local call then gives

```text
X = F25(-z,-q_R v),
Y = F25(alpha-H2 q_R v,u).
```

At the final boundary, apply

```text
Y_P -= H2 X_R,
Y_P -= H0 Y_R.
```

The first uses the actual stage-2 FULL views. The second is a scalar
port map in the global FULL frame. The endpoint is

```text
X = F25(-z,-q_R v),       Y = F25(a,u).
```

Substitution of the original physical inputs gives the stated
common-q signed exchange. With initial I entry, only selected X
has no q.

`BLOCK-PROOF.json` records this calculation with H0, H2, and D1 as
free operators. It reduces only adjacent powers of the same Q.
It rejects the wrong middle sign and does not impose Q-reader
commutation. `FULL-SHEARS.json` gives the literal map and ADD
instructions. Each shear is checked on all 224 arbitrary columns,
including unchanged source fields and all fields outside the shear.

## Exact invoice and the remaining obligations

For each provider, the checker counts the stored body events and
the 96 physical prefix ADDs. Each local word has 1,520 native calls,
3,864 body scalar units, and 768 prefix units, for 4,632 scalar units.
The Q-entry profile is

```text
1392 H1 + 64 H2 + 48 H3 + 16 H8.
```

Initial I entry replaces the last sixteen H8 calls by H9. Each
direct H or D shear has 216 coefficient ADDs and 2,048 scalar units.
The two routed shears each have 224 affine map calls. H0 needs no
additional view. Thus the three shears add 648 coefficient ADDs,
6,144 scalar units, and 448 affine maps.

| Initial entry | Native mass before terminal | Positive terminal lines | Native mass after terminal |
| --- | ---: | ---: | ---: |
| I | 5,392 | 208 | 5,600 |
| Q | 5,376 | 224 | 5,600 |

The scalar subtotal is `3*4632+6144=20040`. It excludes terminal
wrappers and any added sign conversion. An unsigned X output needs
112 signs, which add 224 scalar units. The local words also contain
656 explicit endpoint views in the I case or 672 in the Q case.
These counts are distinct from the 448 added shear maps and from
the inherited native side maps. No stream or address cost is waived.

The direct terminal applies positive Q to all 112 Y outputs and
all 96 ordinary X outputs. In Q entry it also applies Q to selected
X. The checker verifies the resulting phase on every output row:

```text
X = -F25 Y0,       Y = F25 X0.
```

Every remaining q fails the identity test when its positive terminal
line is omitted. The complete native profiles are

```text
I: 4384 H1 + 192 H2 + 144 H3 + 32 H8 + 16 H9,
Q: 4400 H1 + 192 H2 + 144 H3 + 48 H8.
```

Both have mass `5600=224*25`. These operator terminals do not supply
their global helper host or line wrappers. Global owner hosting,
map-stream and address cost, bank routing, numerical precision, and
recursive acceptance of the literal common-q type remain open.
There is no new owned field, odd division, strict supplier result,
or kappa claim in this review.

## Verification record

The normal and optimized review runs use separate fresh directories:

```text
python3 -B check_review.py --out final-normal
python3 -O -B check_review.py --out final-optimized
```

Both return `PASS_INDEPENDENT_PHASE_CODED_TRIPLE_REVIEW`. All six
JSON output files are byte-identical. Every bound source is hashed
again at the end of each run. No producer file is changed.

No PR, commit, push, or publication is authorized. Before any future
PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
