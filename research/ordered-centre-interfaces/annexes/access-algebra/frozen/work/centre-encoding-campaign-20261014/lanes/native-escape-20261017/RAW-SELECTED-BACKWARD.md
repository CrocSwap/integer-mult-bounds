# A physical selected exchange in the backward word

This local construction carries each original selected X input into its
productive Y output. It uses eight new rank-one children. It does not keep
the old logical contents of the selected X or ordinary Y outputs. An
explicit unit code retains that information. A global controller must
use or remove this code before the construction can replace a supplier.

The literal word has 210,714 real scalar primitives and native mass 5,530.
It restores all 480 arbitrary helper arrays. It clears the eight owned
private outputs. One existing owned array, C0, serves all new copies in
sequence. No additional array is used. An optional block adds eight more
rank-one children and changes the ordinary X output to `x_U-y_U`. The
optional total is 214,922 real scalar primitives and native mass 5,538.
These are local invoices. No complete supplier or kappa claim is made.

## Operators and local contract

Use the selected set

```text
A = [0, 7, 20, 27, 36, 46, 57, 111].
```

Its complement U has 104 ports. The source matrix R and `K=R^T/4` give

```text
J = [[0, -B], [-D, I-DB]],       BD=13I.
```

At the local input, physical X_p is `Q_p x_p`, and physical Y_p is `y_p`.
Here Q_p is the exact positive line operator C_qp. At the local output,
physical X_p is `F x'_p`, and physical Y_p is `F Q_p^-1 y'_p`. The full
operator F commutes with each Q_p. These are the existing local endpoints.
Write `x=(a,u)` and `y=(b,v)`, with selected components first. Put

```text
r = Q_A^-1 b.
```

The operator order is part of this definition. In particular, the proof
does not commute Q_A through B or D.

## Literal construction

First form `r_a` in C0 from each unchanged selected Y input. Apply the exact
inverse line to the copy. Subtract `D[:,a] r_a` from ordinary Y, then clear
C0. This gives the physical common-address update

```text
Y_U <- v-D Q_A^-1 b.
```

The source C0 after the child and the target Y field have different logical
frame labels. Their ADD is a physical ADD at the same local addresses. Its
operator Q_A^-1 remains in the data code. It is not removed by a frame label
change or an uncharged inverse. A verifier that permits only equal logical
frame labels cannot validate this block without an explicit operator code.

Next exchange physical X_a and Y_a for each selected port. Each exchange is
three unit ADDs followed by one negative SCALE. This is an exact exchange
of arbitrary physical arrays. In logical input coordinates it gives

```text
X_A <- Q_A^-1 b,        Y_A <- Q_A a.
```

All ordinary X fields are unchanged. Then execute the byte-exact clean-J
backward core. Finally, at the complete FULL X boundary, apply `L(-D)`:
subtract D times selected X from ordinary X.

The full logical result is

```text
X_A = Bv-12r,
X_U = u-v+D Q_A a,
Y_A = Q_A a,
Y_U = v-Dr.
```

Indeed, the clean backward core has map `(X,Y)->(X-JY,Y)`. Its selected X
row is `r+B(v-Dr)=Bv-12r`. Its ordinary X row before the final lower shear
is `u-v+D Q_A a+DBv-12Dr`. The lower shear removes its final two terms.
These identities use `BD=13I` and do not require any other relation.

The physical selected Y output is exactly

```text
F Q_A^-1 Q_A a = F a.
```

Thus the original selected input is present in productive FULL Y. No
original-input record cohort is required for this local statement.

## The remaining unit code

The other selected X and ordinary Y values form the unit

```text
(X_A,Y_U) = U(B) L(-D) (r,v).
```

Its direct inverse is

```text
r = X_A-B Y_U,
v = Y_U+D r,
b = Q_A r.
```

No division by 12 or 13 is used. The first inverse operation reads the
ordinary Y fields, whose physical operators are different holes. Its
algebraic formula is not a free native decoder. A useful controller must
route this code, cancel it, or provide and price its native inverse.

For the optional ordinary correction, copy each physical selected Y output
`F a_a` into C0. Apply the positive Q_a line and subtract D times that copy
from completed ordinary X. This removes `D Q_A a`. The output is then
`X_U=u-v`. It costs eight rank-one children. C0 is cleared after every copy.

## Checks and source pins

Run

```text
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/emit_raw_selected_backward.py
```

The first line is

```text
PASS_RAW_SELECTED_BACKWARD_LOCAL_OPERATOR
```

The checker replays every retained scalar event on all 712 formal input
columns. Its operator words cancel only adjacent Q and Q^-1 pairs. It does
not use commutation between different Q operators or between Q, B, and D.
It checks every retained scalar frame and native frame transition. It
checks arbitrary helper restoration, all owned-private outputs, both
local formulas, and the displayed source-code inverse. The boundary
interpreter uses physical common-address ADDs, not equal-logical-frame
ADDs. Five mutation controls reject omitted or wrongly signed blocks.

The sixteen signed line recipes are checked on every one of the 512
spatial basis columns: 8,192 exact Gaussian columns. Both wrappers, their
addresses, their translations, and all scalar phase fields are included.
The complete unchanged core native proof is inherited. It is not replayed
as a new 712-array physical Gaussian operator in this packet.

The payload pins are:

```text
clean-J core, decompressed:
fa60b4af013dd8b8db289845e3ed597720ff955751ad270c3d58236b64080877
canonical word, compressed:
16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219
source matrix receipt:
5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3
signed line recipe packet, decompressed:
17122a343fb8a3dd804b2d7042d523aa209d0684447cdba63d84cc5561b6144f
```

`RAW-SELECTED-BACKWARD.json` pins the emitted word and this checker. The
old core cost is recalculated from its literal scalar events. The new
scalar parts are 4,208 for the input code, 208 for the physical exchanges,
and 4,160 for the final lower shear. The optional correction costs 4,208.
Each new line has two monomial wrappers. The uncorrected native profile
adds eight rank-one children to the old profile.

The remaining obligations are an independent review, the actual inter-call
views and controller, new child hosting, and the complete recursive scalar,
storage, and precision invoice. The old canonical-frame obstruction does
not apply because the new physical ADDs cross its declared logical frame
classes. This escape does not establish that the desired final supplier
can decode the resulting unit code within its budget.

The coordinating lane proposed the input code and the final lower shear.
This lane supplied the physical selected exchange and the independent local
operator replay. The clean-J and exact native recipes are prior campaign
results. Research and verification used OpenAI Codex under the user's
direction. No independent human review is claimed. No publication is
authorized.
