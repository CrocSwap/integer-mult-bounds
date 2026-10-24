# A finite terminal for the common cover response

This note gives a complete physical terminal for a common reciprocal
cover response. It does not require the response to commute with an
intrinsic port line. It contracts the two terminal line calls to one
rank-two child per X field.

The common response and its stage phase maps are supplied by
`../../bridge-access-20261017/cycle-cover-response-20261018/`.
This terminal does not certify the fresh local native words, the global
owner schedule, or the complete scalar and precision invoice. Its native
rank is explicit. The resulting rank balance does not give a positive
kappa improvement.

## 1. Coordinates and common response

Let h be an orthogonal cover matrix on D=73 binary axes. Let q_p be the
odd intrinsic vector of port p. Write

    Q_(p,h)=C_(h q_p),  q_(p,h)=Q_(p,h)^-1,
    F_h=product_j C_(h e_j).

Every C_v acts on the payload coordinates. For tensor depth lambda,
apply the same map to each payload column. The cover label h is separate
from the payload coordinates.

The raw original input is (Qx,y). This is a coordinate convention; no
initial Q call is added. The local endpoints have the original frames:

    forward:  (x,y) -> (x,y+E x),
    backward: (x,y) -> (x-E^-1 y,y).

The input and output native frames must be included in these equations.
In particular, Y has the inverse intrinsic line at its output.

For each port, the pinned cycle L_p has order ten. It sends

    q_p -> v_0 -> v_1 -> ... -> v_8 -> q_p,

where v_j for j>=1 is the first axis of fresh block j. These ten vectors
are orthonormal. The common logical response is

    (E f)_p(h)=f_p(h L_p),
    (E^-1 f)_p(h)=f_p(h L_p^-1).               (1)

It does not change the payload values. Its physical realization at an
interior cut is a separate cover map with the phase correction in the
source packet. Equation (1) is common to all nine stages; equality of
local coefficient matrices alone would not establish this fact.

## 2. The raw controller closes to an explicit code

Use the retained m-pair controller: initial F0, then B and F on each
pair, the plus and minus bridges to the next pair, the idle jobs, the
descending final bridges, and the old terminal site. Every local F uses
E; every local B uses E^-1. No additional logical code is inserted.

The exact logical output before the terminal is

    X_i=-E^-1 y_i,  Y_i=E x_i.                (2)

For a direct proof, change variables to xbar=E x and ybar=y. The F and B
calls become the ordinary unit shears on (xbar,ybar). Every retained
bridge also becomes its ordinary unit bridge because the same E acts
on every X bank. The unit controller gives (-ybar,xbar). This proves
(2) for every m. All inputs are arbitrary.

The checker also replays the exact pinned nineteen content events and
ten idle sites for m=4. It uses free integer powers of E. It does not use
the cycle relation E^10=I to obtain (2).

In physical coordinates, put U=X_preterminal and V=Y_preterminal. Then

    U=-F E^-1 y,  V=F q E x.                  (3)

With the old terminal alone, the raw physical output code would be
diag(Q E Q^-1,E^-1). The first factor is not E. We do not move E across Q.

## 3. The integrated physical terminal

Define the FULL-frame maps

    M_E=F E F^-1,  M_I=F E^-1 F^-1.

Replace the old terminal line-square map and signed exchange by:

1. V <- Q V.
2. V <- M_I V.
3. V <- Q V.
4. U <- M_E U.
5. (X,Y) <- (V,-U).

Both line calls are positive. From (3), their ordered action gives

    V: F q E x -> F E x -> F x -> F Q x,
    U: -F E^-1 y -> -F y.

The final signed exchange therefore gives F times the raw original input
(Qx,y). No encoded state passes to an unchanged outer twiddle or product.
The terminal is valid for arbitrary x and y and for each tensor depth.

## 4. Exact cover and phase recipes

Let delta_p and epsilon_p be the source packet's
`FULL_E_output_translation` and `FULL_E_inverse_output_translation`.
They satisfy

    (M_E f)_p(h)=X_(h delta_p) f_p(h L_p),
    (M_I f)_p(h)=X_(h epsilon_p) f_p(h L_p^-1).

Here X_v denotes a payload translation. The checker verifies these
translations from the full Z4 phase polynomial on all 73 basis vectors
and all 2,628 pairs. The phase polynomial has degree at most two, so this
is a complete coefficient check, not a sample. It also verifies
L_p epsilon_p=delta_p.

Since L_p^-1 q_p=v_8, the terminal has the following literal output form:

    X_new,p(h)=X_(h epsilon_p) C_(h q_p) C_(h v_8)
               V_p(h L_p^-1),
    Y_new,p(h)=-X_(h delta_p) U_p(h L_p).      (4)

Translations commute with both line transforms. The two line directions
are independent and orthogonal. Their product is one positive rank-two
native transform.

For each port, choose an orthogonal binary basis matrix G_p whose first
columns are q_p and v_8. Two orthogonal transvections send e_0 to q_p
and fix v_8. A swap of input axes 1 and 65 then gives this basis. The
emitted recipe uses:

    right view: read cover h L_p^-1 and payload h G_p z;
    child:      apply C_e0 C_e1;
    left view:  z=G_p^-1 h^-1 w+G_p^-1 epsilon_p.

These two views implement the first line of (4). The second line is one
cover/translation map followed by the retained signed exchange. No full
cover record, helper field, or new zero field is required by this
terminal. Array-map execution and recursive child hosting still use the
admitted map and child contracts.

## 5. Finite terminal inventory

For m pairs and n=112 ports per bank, the replacement terminal has:

| Item | Count |
| --- | ---: |
| Rank-two native children | mn |
| Native rank mass | 2mn |
| Child wrapper maps | 2mn |
| FULL source cover/translation maps | mn |
| Signed bank exchanges | mn |

For m=4, these are 448 rank-two children, rank mass 896, and 1,344
monomial array maps. The signed exchange is the same as in the old
terminal. It can use three unit complex ADDs, or 24 real scalar
primitives per port pair. Thus its 10,752 real primitives per replica
are retained work, not a new surcharge.

The old 448 line-square translation maps are removed. Relative to that
terminal lowering, there are 896 more monomial maps. The cover maps and
translations in (4) need no scalar multiplication. This inventory does
not include the recursive cost of the rank-two children, native map
execution, earlier local calls, idle jobs, or finite precision.

Two rank-one calls per X field are an alternative implementation with
the same rank mass. The rank-two contraction reduces the child count.
It does not reduce native rank.

## 6. Exact rank limit of this terminal

After its cover permutation is removed, each X terminal block in (4)
has Fourier rank two. Left and right monomial maps preserve this rank.
For a one-field Clifford word, the Fourier rank of a product is at most
the sum of the Fourier ranks of its factors. Thus every terminal in this
word class needs total native rank at least two per X field. The emitted
rank-two child attains that bound.

This is a bound for one-field Clifford terminal words. It does not rule
out a changed multi-field circuit or a change to an earlier local call.

The fresh independent data paths use D-1 native rank per productive
field before this terminal. There are 2mn such fields. The terminal adds
2mn rank. Under that complete path and idle accounting, total native
rank is exactly 2mnD, the productive target rank.

This equality cannot give a positive saving exponent merely by changing
the child partition. If every child width r is at most D and b>0, then

    r^(1-b) >= r D^-b.

Summing at equal total rank gives native weight at least
2mn D^(1-b). Extra scalar or map work cannot improve this inequality.
The independent owner and budget packets must verify the complete path
accounting before this conclusion is applied to a hosted supplier.

## 7. Validation and remaining work

The checker pins the common cycle payload and the retained controller.
It checks the raw controller for one through eight pairs, the actual
four-pair recipe, all 112 cycle matrices and inverses, all FULL phase
polynomials, all two-axis child bases, and the signed terminal order.
Wrong line directions, wrong cover direction, a missing FULL translation,
and an omitted terminal line are negative controls.

The proof supplies the all-m and all-tensor statements. Finite checks
support those proofs. Fresh local native emission, stage scheduling,
owner admission, the complete invoice, and precision are separate.

No PR, commit, push, or publication is part of this work. Before any
future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
