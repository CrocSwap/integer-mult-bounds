# The full controller residual does not compress into fewer whole arrays

This note uses the selected nine-stage controller at commit
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. It uses the centre-free local
interface in `../circuit-interface/INTERFACE.json`. That interface has
`J = I - R*R/4` and `R R* = 56 I_8`. A star denotes the adjoint.

The source controller is the member
`t16/global/base/split-centres/GLOBAL-TEMPLATE.json.gz` of
`research/community-frontier1042-audit/selected-replay.tar.gz`.
`RESIDUAL.json` gives the byte pins and the exact checks.

The algebra below assumes that the native words have the stated abstract
routed interface. Three separate sources supply the required application
facts. The local native lift is checked in
`../interface-proof/NATIVE-LIFT-REVIEW.json`. The actual global endpoint
normal form is stated in `../encoded-controller/CONTROLLER.md`. The bound
on the common routed centre image is proved in `../cover-algebra/PROOF.md`.
This note does not re-prove those results. The scalar interface receipt
alone does not prove the native global normal form.

## Result

Let `G` be the finite orthogonal cover group. Use its full regular action.
Each port has a function on `G`. Put

\[
H=\mathbb C^{112}\otimes\mathbb C^G,
\qquad R_s=(R\otimes I_G)D_s,
\qquad R_s R_s^*=56 I_{8|G|},
\]

where `D_s` is the actual port-dependent route at stage `s`. In particular,
`D_0=I`. Let `C_0` be the old controller before its final signed swap. Let
`C` be the same controller with all nine centre blocks omitted by the new
local interface. Define

\[
d=\dim\bigcap_{s=0}^8\operatorname{im}R_s^*.
\]

Then

\[
\operatorname{rank}(C-C_0)=72|G|-d.
\tag{1}
\]

If only a proper set `S` of the nine stages uses the new interface, then

\[
\operatorname{rank}(C-C_0)=8|S||G|.
\tag{2}
\]

The separate routed-projection theorem in `../cover-algebra/PROOF.md` gives
`d <= (8/183)|G|`. Therefore the full nine-stage residual has rank greater
than `71|G|`. Across all 16 independent replicas, its rank is at least

\[
\left(1152-\frac{128}{183}\right)|G|>1151|G|.
\tag{3}
\]

Thus a final linear correction that passes all residual information through
complete cover arrays still needs 72 arrays per replica, or 1,152 arrays
for the selected 16 replicas. A joint linear encoder across replicas does
not reduce either whole-array count.

These counts concern the dimension of one complete residual encoding.
They are not a lower bound on the number of work arrays that must be live
at one time. A circuit can reuse a smaller workspace if it reads the data
again. The counts do not bound native child rank, phase changes, storage
through time, or a circuit that uses the data arrays directly. In particular,
they are not a proof that the old 64 centre rank units per call are optimal.

## The actual bank controller

Order the eight bank roles as

\[
(X_0,Y_0,X_1,Y_1,X_2,Y_2,X_3,Y_3).
\]

The old local steps have the form `Y_i += X_i` or `X_i -= Y_i`.
The bridge from pair `j` to pair `i`, with coefficient `a`, is

\[
X_i\gets X_i+aX_j,\qquad Y_j\gets Y_j-aY_i.
\]

The two updates commute. Every local step and every bridge preserves

\[
\Omega=\operatorname{diag}_{i=0}^3
\begin{pmatrix}0&I_H\\-I_H&0\end{pmatrix}.
\]

The source row for local stage `s`, pulled back through the old prefix,
is the following row `v_s` on the eight bank roles:

| Stage | Source row |
| --- | --- |
| 0 | `(1, 0, 0, 0, 0, 0, 0, 0)` |
| 1 | `(1, 1, 0, 0, 0, 0, 0, 0)` |
| 2 | `(0, -1, 1, 0, 0, 0, 0, 0)` |
| 3 | `(0, -1, 1, 1, 0, 0, 0, 0)` |
| 4 | `(0, 1, 0, -1, 1, 0, 0, 0)` |
| 5 | `(0, 1, 0, -1, 1, 1, 0, 0)` |
| 6 | `(0, -1, 0, 1, 0, -1, 1, 0)` |
| 7 | `(0, -1, 0, 1, 0, -1, 1, 1)` |
| 8 | `(0, 1, 0, -1, 0, 1, 0, -1)` |

These rows have rank eight. Their only relation, up to a scalar, has
coefficient vector

\[
c=(1,-1,-1,1,1,-1,-1,1,1).
\tag{4}
\]

Every coefficient is nonzero. Every proper subset of the rows is
independent. The executable check derives the rows from the pinned recipe
and checks all nine subsets of eight rows.

## An exact factorization of the residual

Put

\[
V_s=R_s(v_s\otimes I_H),\qquad
V=\begin{pmatrix}V_0\\\vdots\\V_8\end{pmatrix}.
\]

At an old forward step, the omitted centre term is
`-R_s*R_s/4` in the update to `Y`. At an old backward step it is
`+R_s*R_s/4` in the update to `X`. Both signs give the same interaction
factor after the old prefix is removed:

\[
B_s=I+\frac14\Omega V_s^*V_s.
\]

Thus

\[
C_0^{-1}C=B_8B_7\cdots B_0.
\tag{5}
\]

This identity includes the actual bridge positions. No routed operators
are commuted. In particular, it does not assume that two `J_s` commute.

Define the strict lower block matrix `L` by

\[
L_{ij}=\begin{cases}
V_i\Omega V_j^*,&i>j,\\
0,&i\le j.
\end{cases}
\]

Then

\[
C_0^{-1}C-I=\Omega V^*(4I-L)^{-1}V.
\tag{6}
\]

To prove (6), let `x_i=B_i x_{i-1}` and `z_i=V_i x_{i-1}`. Directly,

\[
z_i=V_i x_{-1}+\frac14\sum_{j<i}V_i\Omega V_j^*z_j.
\]

The stacked relation is `(I-L/4)z=V x_{-1}`. Also
`x_8-x_{-1}=Omega V*z/4`. These two equations give (6).
The inverse exists because `L` is strictly lower block triangular.

This also shows that the actual online centre demands and the ideal-prefix
demands have the same joint information rank. The two demand lists differ
by an invertible lower triangular map.

## The only syndrome relations

Let `N=ker(V*)`. Write a vector in its domain as `(z_0,...,z_8)` and put
`w_s=R_s*z_s`. The equation `V*z=0` is

\[
\sum_s v_s^*\otimes w_s=0.
\]

By (4), there is a single `w` such that `w_s=c_s w` for every stage.
This `w` lies in every image `im(R_s*)`. Conversely, every such `w`
gives one relation, because

\[
z_s=\frac{c_s}{56}R_s w
\tag{7}
\]

is the unique solution of `R_s*z_s=c_s w`. Therefore `dim N=d` and

\[
\operatorname{rank}V=72|G|-d.
\tag{8}
\]

For a proper stage subset, the independent rows `v_s` force each `w_s=0`.
Each `R_s*` is injective. Therefore the corresponding stack has full row
rank `8|S||G|`.

## No additional cancellation in the final decoder

Equation (6) alone does not prove that the residual has rank `rank V`.
Its middle factor could send part of `im V` into `ker V*`. The following
calculation excludes that event for this controller.

Use (7) to identify `N` with the common image. Direct calculation of the
bank rows gives

\[
\sum_{i>j}c_i c_j(v_i\Omega v_j^*)=4.
\tag{9}
\]

Here `Omega` in (9) is the eight by eight bank matrix. Since
`R_s*R_s w=56w` on the common image, (7) gives

\[
\langle z(w),4z(w')\rangle=\frac9{14}\langle w,w'\rangle,
\]

and (9) gives

\[
\langle z(w),Lz(w')\rangle=4\langle w,w'\rangle.
\]

Consequently

\[
\langle z(w),(4I-L)z(w')\rangle
=-\frac{47}{14}\langle w,w'\rangle.
\tag{10}
\]

This form on `N` is nonsingular. Suppose `u` lies in `im V` and
`(4I-L)^-1 u` lies in `N`. Put `n=(4I-L)^-1 u`. The relation
`im V=N-perp` implies that `(4I-L)n` is orthogonal to `N`.
Equation (10) then forces `n=0`, and hence `u=0`.
Thus `V*(4I-L)^-1` is injective on `im V`. This proves (1) from
(6) and (8).

For a proper stage subset, `V*` is injective on its whole domain. The
middle factor remains invertible. This proves (2).

## Final correction and borrowed state

Both old and new controllers are invertible. The required final corrector
is `C_0 C^-1`. Its difference from the identity has the same rank as
`C-C_0`. The boundary native frame maps and the final signed permutation
are also invertible, so they preserve this rank. Tensoring with the signal
space multiplies both the rank and one full array's capacity by the same
factor.

A linear correction that has the form `x -> x+A(Bx)` through `k` complete
cover arrays has residual rank at most `k|G|`. This remains true if those
arrays start with arbitrary borrowed values and the circuit restores them:
linearity forces the borrowed-input contribution to cancel, and the data
contribution still factors through the declared residual channel.

This statement does not apply to a procedure that reads the data again
after the encoded residual is formed, or that corrects parts of the data
during the original computation. Such a procedure has additional channels
that must be included in its rank factorization.

## Cost consequence and remaining escape

The old schedule makes nine separate centre cohorts of eight full
arrays per replica. A plan that runs all centre-free local words and then
stores a smaller complete-array residual does not save centre information.
The same conclusion holds across all 16 selected replicas.

The result leaves a different route open: carry all required residual
information in a representation with cheaper native phase changes. It
also leaves source-dependent state during the original calls, new bank
controllers, partial-cover processing, and changed recursive children
open. The rank of a map does not price those mechanisms.

For comparison, putting both final bank types in the common full frame,
undoing the abstract controller by scalar cover operations, and correcting
the remaining boundary frames is algebraically possible. It needs one
rank-one native correction for each of the 896 data families per replica.
The complete centre-free non-centre invoice, divided by 16 replicas, has
rank mass `72*896`. Adding 896 per replica gives `73*896`, which consumes
the entire rank deficit at exponent zero. This is not a supplier
improvement. A useful boundary method must avoid part of that 896-unit
charge and must price all access and restoration steps. This normalization
does not assign cross-replica hosting costs to individual replicas.

## Reproduction and validation limits

Run from the workspace root:

```sh
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/residual-syndrome/verify_residual.py --repo worktrees/k5-centre-sharing --interface work/centre-encoding-campaign-20261014/lanes/circuit-interface/INTERFACE.json --out work/centre-encoding-campaign-20261014/lanes/residual-syndrome/RESIDUAL.json
```

Expected first line:

```text
PASS_SELECTED_CONTROLLER_RESIDUAL_FACTORIZATION
```

The checker binds the literal controller and interface bytes. It derives
the bank rows, verifies their unique relation, checks all maximal proper
subsets, and checks the coefficient in (10). A separate direct matrix
product checks (6) on two exact rational examples. One example has a common
centre image and one does not. A missing bridge and an incorrect triangular
sign are rejected. The examples test the general algebra; they are not
substitutes for the proof over the full cover group.

The normalized numerical rank bound uses the separate routed-projection
theorem. This file does not re-prove that theorem. No new native corrector,
recursive cost certificate, whole-invocation owner assignment, cold supplier
admission, or multiplication exponent is claimed. The finite algebra passed
the separate review in `review/REVIEW.md`. That review also reproduced the
source-bound receipt and ran independent exact matrix examples. It did not
re-prove the three application dependencies listed at the start of this
note. `review/REVIEW-EDITS.json` records the scope and wording edits made
after that review.

This work used substantial AI assistance. It builds on the selected native
supplier, the campaign's independently checked centre-free local interface,
and the campaign's routed-projection theorem. Apache-2.0.
