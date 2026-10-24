# The common-q type persists through the nine DATA stages

The phase-coded triple can be repeated at the actual DATA stage
views. After nine local calls and nine FULL scalar shears, it gives

```text
X =  F73 q Y0,
Y = -F73 q X0.
```

Both original input banks are arbitrary. The same q factor remains
on both banks. It does not accumulate with the number of triples.
This is a closure result for the data type at the actual stage
boundaries. It does not prove a recursive gathered-axis interface,
a complete helper host, or a multiplication bound.

## Fixed source and views

Use the reviewed phase-coded triple from
`../phase-coded-triple-20261020/PHYSICAL-ENDPOINT.md`.
Its freeze SHA256 is
`0ee32fe22f42cffce2a9673f0dc95496a4b4bb8b11a534f77a11f5fe9c7aeb4b`.
The independent review is
`../owner-review/phase-coded-triple-review-20261020/REVIEW.md`,
SHA256
`8342f508f9c2432a01ef196820d5c94b98df012c63f21d560940c8799e337c0c`.

The full stage view source is
`bridge-access-20261017/check_bridge_access.py`,
SHA256
`9510c5624dfb51d98767728084851e4ee75a135e6d7b546569a47fe458485111`.
It binds the actual 73-axis DATA phase ledger in the selected source
archive. The checker verifies the archive and member hashes before
using any recipe. It checks all 112 ports at stages 1 through 8.

As before, G_s means the portwise orthogonal route rho_s. Define
`H_s=G_(s,P) H G_(s,R)` and `D_s=G_(s,R) D G_(s,P)`.
The literal entry and exit identities are

```text
Ventry_s Fprev_s = Fext_s Q G_s,
Vexit_s Fnext_s = Fnext_s G_s.
```

The checker verifies the FULL and hole forms of both identities:
3,584 phase identities in total. Every route fixes its own q line.
Omitting the actual entry or exit translation fails at all 896
respective port-stage pairs.

There are nine added shears, at these route and execution levels:

```text
(route 1, level 1), (route 2, level 2), (route 0, level 2),
(route 4, level 4), (route 5, level 5), (route 3, level 5),
(route 7, level 7), (route 8, level 8), (route 6, level 8).
```

Level s has common FULL frame `F_(9+8s)`. For each listed shear,
the checker verifies the exact FULL affine-view identity and its
involution at all 112 ports. This gives 1,008 further phase checks.
The stage-0 view is the identity.

## The type lemma

At a natural boundary, write the physical state as

```text
X = Fprev(a,u),
Y_P = Fprev z,
Y_R = Fprev q_R v.
```

The literal entry views give the declared Q-entry local type.
The three routed local content maps are the F_Q, B_Q, and F_Q
maps of the reviewed triple. At the end of the middle call, apply
`X_R-=D_(s+1) X_P`. At the end of the last call, apply
`Y_P-=H_(s+2) X_R` and `Y_P-=H_s Y_R`.

The same ordered calculation as in the reviewed triple gives

```text
X = Fnext(-z,-q_R v),
Y = Fnext(a,u).
```

The middle shear occurs after the complete middle cover sweep.
The last two occur after the complete last sweep. Every local
helper return must finish before these scalar maps start.

Now assume the input has one common-q code:

```text
X = Fprev q A,
Y = Fprev q B.
```

Its natural contents are

```text
(a,u)=q A,  z=q_P B_P,  v=B_R.
```

Substitution gives

```text
X = -Fnext q B,
Y =  Fnext q A.
```

Thus each corrected triple preserves the same code and applies
the signed bank exchange `J(A,B)=(-B,A)`. There is no extra q
factor. In particular, treating ordinary Y as FULL at the next
entry would give the wrong contents: its natural ordinary
coordinate is Q times its stored FULL coordinate.

This argument uses the order of Q and q. It never moves a line
operator through H or D. The checker uses free noncommuting
operators with only adjacent inverse cancellations.

The lemma applies to any further stage block with the stated
entry, exit, and FULL-view identities. The literal application
proved here stops at the actual nine source stages. No arbitrary
dimension compiler is supplied.

## Actual nine-stage word

The first three calls are F_Q0, B_Q1, F_Q2 with the three
corrections of the reviewed packet. They give the common-q type
under F25 from arbitrary original physical inputs.

Use the type lemma for calls F_Q3, B_Q4, F_Q5, then for
F_Q6, B_Q7, F_Q8. The three block signs are J, J^2, and J^3.
Since `J^3(A,B)=(B,-A)`, the final result is the endpoint
stated at the start. The checker verifies each intermediate
operator row and the final sign.

The local word order is an explicit choice for this new data
caller. The old global helper allocation is not thereby proved
to host the changed words. Local arbitrary-helper restoration
and global chronological hosting are separate obligations.

## Invoice and limits

All nine local words use Q entry. Their total native profile is

```text
12528 H1 + 576 H2 + 432 H3 + 144 H8.
```

The native mass is `16128=224*72`. The nine local scalar
invoices sum to 41,688 primitives. The nine direct coefficient
shears add at most 18,432 primitives and 1,792 affine field-map
calls. They add no native child or owned field.

The eight transitions retain 3,584 global entry and exit field-map
calls. Those maps are separate from the local invoices and the
added shear views. Every map retains its stream and address cost.
Native side maps retain their inherited cost as well.

Applying one positive Q line operation to each of the 224 final
data fields gives

```text
X =  F73 Y0,
Y = -F73 X0.
```

The total native mass is then `16352=224*73`. There is no strict
native-mass gain. The common-q code must be matched to an actual
consumer to avoid that terminal cost. This packet proves
within-chain stage matching only. It does not prove matching
across recursive gathered-axis views.

The source local numerical bounds do not supply a complete
recursive precision proof. The global owner host, terminal native
recipes, final bank convention, and complete kappa calculation
remain open.

## Verification

Run with fresh output directories:

```text
python3 -B check_chain.py --out <new-directory>
python3 -O -B check_chain.py --out <another-new-directory>
```

The normal and optimized receipts are byte-identical. The checks
use the literal DATA ledger and all listed phase identities,
then a separate free-operator induction for the three corrected
blocks. The 224-column local operator checks are inherited from
the reviewed D25 packet. This checker does not repeat a dense
73-axis input matrix expansion.

No PR, commit, push, or publication is authorized. Read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`
before any future PR description.
