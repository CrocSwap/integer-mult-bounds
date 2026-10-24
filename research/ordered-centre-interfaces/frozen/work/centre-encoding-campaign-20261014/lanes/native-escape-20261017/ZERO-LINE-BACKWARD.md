# A raw selected backward local with no new native lines

## Result

This local uses the raw selected swap and the clean backward core from
`RAW-SELECTED-BACKWARD.md`. It omits the eight-line input correction. It has
native mass 5522 and scalar cost 206506 under the inherited core invoice.
It is a changed encoding of the two data banks. It is not the lower-unit
local from the selected-source retirement theorem.

The endpoint conventions are unchanged. At input the physical data are
`X_p = Q_p x_p` and `Y_p = y_p`. At output they are `X_p = F x'_p` and
`Y_p = F Q_p^-1 y'_p`. The common full operator F commutes with each Q_p.
No proof step moves Q through B or D.

Let A be the eight selected ports, and let U be the 104 other ports. Write
`x = (a,u)`, `y = (b,v)`, and `r = Q_A^-1 b`. The exact logical map is

```text
X_A = r + B_s v
X_U = u - v - D_s r + D_s Q_A a
Y_A = Q_A a
Y_U = v.
```

The physical selected Y bank is therefore `F a`. It holds the original
selected X in the full frame. The coefficient of r in selected X is +1.
There is no factor 12 to invert.

## Circuit

At each selected port, swap the physical X and Y arrays. Use three ADDs
and one negative SCALE. Execute the unchanged clean backward core. Then
apply the scalar lower shear `L(-D_s)` to completed full X. No new native
line is used.

A physical swap between the input arrays is not a scalar swap in their
logical coordinates. It sends `(x_A,y_A)` to
`(Q_A^-1 y_A,Q_A x_A)`. This distinction is required for the formula above.

The scalar cost is 202138 for the core, 208 for the swaps, and 4160 for
the lower shear. The native cost is the inherited 5522. All 480 arbitrary
helper arrays return to their inputs. The eight owned private arrays
return to zero.

## Inverse and use by a controller

The map has the following exact inverse:

```text
v = Y_U
r = X_A - B_s Y_U
b = Q_A r
c = Y_A
a = Q_A^-1 c
u = X_U + Y_U + D_s r - D_s c.
```

This is a unit encoding. It requires no division by 12 or 13. The formula
does not give a free physical inverse: the displayed `B_s Y_U` query is
still over different hole frames.

A later controller may know v in a completed full bank. In that case the
selected source b can be recovered from completed X as `Q_A(X_A-B_s v)`.
This needs eight positive native lines, with their copy and scatter costs.
If a subsequent corrected raw forward local changes selected X by
`-Q_A^-1 B_t k`, the formula becomes

```text
b = Q_A (X_A - B_s v) + B_t k.
```

This identity preserves operator order. A controller must prove where it
obtains v and k in the full frame, and must restore all other data and
borrowed state. The local result does not prove that controller.

## Check and scope

Run:

```text
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/check_zero_line_backward.py
```

Expected status:

```text
PASS_ZERO_LINE_BACKWARD_LOCAL_OPERATOR
```

The checker pins and replays the literal core and boundary events. It
checks all 712 formal input columns with ordered Q operator words. It
cancels only adjacent inverse pairs on the same port. It checks the
arbitrary-helper and private-zero contracts, the selected physical output,
the selected-source inverse, the exact local invoice, and three negative
controls. The full physical core proof is inherited from the pinned core.
No native line is added by this variant.

Independent review, actual inter-call views, the global controller, and
the complete recursive and owner invoice remain open. This note gives no
new complete kappa value.

This result uses the centre-free core, the raw selected exchange, and the
selected-source retirement work. The zero-line variant and its use in
selected-source recovery were identified in the coordinated controller
follow-through. The source packet and checker pins are in
`ZERO-LINE-BACKWARD.json`. This work was produced with AI assistance.
