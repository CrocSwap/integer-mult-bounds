# Signed unit and oblique return on the new core

The new clean-J core admits the campaign's signed unit and oblique return
mechanisms. The two new providers have the same source and target ports
as the earlier provider. Their selected input and output frames are also
the same. The changed helper geometry does not alter these data cuts.

Let A be the port indices `[0,7,20,27,36,46,57,111]`, and let Pi be the
coordinate projection onto these fields. Define

    J = I - K R,
    S = J - Pi,
    P = K_A R,

where `K_A=Pi K`. Exact multiplication of the actual matrices gives
`RK=14I`, `RK_A=I`, `P^2=P`, and `P S^-1=-Pi`. In the selected and
ordinary coordinate blocks, the two inverse matrices have the form

    S    = [[-I, -B], [-D, I-DB]],
    S^-1 = [[12I, -B], [-D, I]],
    BD = 13I.

Thus S is a unit over the dyadic coefficient ring. No division by 13 is
needed. The checker verifies both inverse orders from the literal R.

## Literal words

For each selected input X field, copy the field into serial owned C0,
apply its inverse line transform to C0, subtract C0 from the same-port Y
field, and clear C0. The input X frame is its port line; the Y frame is
I. This is the input shear `y -= Pi x`. It costs eight rank-one children
and 112 real scalar primitives.

After a backward clean-J word, the analogous same-port output operation
copies selected Y into C0, applies its positive line transform, adds C0
to X, and clears C0. The Y output has the port hyperplane frame; X is at
FULL. This gives the output shear `x += Pi y`, at the same cost.

The resulting plain maps are

    F_S(x,y) = (x, y+Sx),
    B_S(x,y) = (x-Sy, y).

The known two scalar factors for S act on the full Y bank at frame I.
Their inverse acts on the full X bank at frame FULL. Each factor costs
7312 real scalar primitives and returns serial C0 to zero. Composition
with these factors gives

    coded F_S(x,y) = (x, S(x+y)),
    coded B_S(x,y) = (S^-1 x-y, y).

Precede coded B_S by the input shear `y -= Pi x`. This gives

    oblique B_S(x,y) = ((S^-1+Pi)x-y, y-Pi x)
                    = ((I-P)S^-1 x-y, y+P S^-1 x).

This return uses sixteen rank-one children over the clean-J core. It
does not store a persistent query record or change a borrowed helper's
contract. The selected response is a current source coordinate.

## Exact checks and cost

`emit_signed_extensions.py` checks ten complete local words: the five
maps above on each of the two new providers. It does not replace the core
by a matrix during replay. It replays every retained native, scalar,
warp, and zero-buffer event in its literal position, over exact rational
coefficients and free warp symbols.

Each check includes all 632 arbitrary live input columns and eight
arbitrary C columns. All 408 helpers have their identity logical response.
All 91 private Z buffers return to zero. C0 returns to zero. C1 through
C7 retain their arbitrary values because they are not used. The checker
also verifies every scalar access frame and all endpoint frames.

| Complete local word | Scalar bound | Rank mass | Child count | New line children |
| --- | ---: | ---: | ---: | ---: |
| Plain signed forward or backward | 164626 | 5081 | 3515 | 8 |
| Coded signed forward or backward | 171938 | 5081 | 3515 | 8 |
| Oblique backward | 172050 | 5089 | 3523 | 16 |

Each new line child has two explicit monomial wrappers. The base profile
is `{1:2433, 2:724, 3:228, 4:102, 5:20}`. Add eight or sixteen rank-one
children, as shown in the table. The scalar bound includes preparation,
copy, add, clear, and both common-bank code factors when they are used.

All sixteen signed line recipes are copied from the prior reviewed
campaign payload. The checker binds that payload by SHA256, checks each
port label against the new canonical provider, and verifies each exact
complex kernel on all 512 spatial columns. This gives 8192 checked
columns per provider. The retained core's complete physical phase review
is a separate dependency, as stated in `CLEAN-J-TRANSFER.md`.

## Scope and use

The result makes the lower-cost PR3133 core available to the campaign's
signed and oblique controllers. It establishes each local map on
arbitrary data and borrowed state. It does not establish legal global
projection bridges, query transport, endpoint decoding, recursive child
hosting, or a complete supplier invoice. In particular, a favorable
native budget is not a construction.

The old source's same-port line phase argument applies when the caller
uses the same paired exterior frames. A new caller must establish that
condition for its own routes and owner schedule. The present result does
not select a caller schedule.

Run with one process, from this directory:

    python3 -I -B emit_signed_extensions.py

The literal payload is `SIGNED-EXTENSIONS.json.gz`. The exact pins are in
`FREEZE-SIGNED.json`. The prior mechanism is in the campaign's reviewed
`current-query-encoder` and `oblique-native-20261017` packets. The new
source and its contributor credit are linked in `CLEAN-J-TRANSFER.md`.
OpenAI Codex assisted this calculation. No PR, push, or publication
commit was made.
