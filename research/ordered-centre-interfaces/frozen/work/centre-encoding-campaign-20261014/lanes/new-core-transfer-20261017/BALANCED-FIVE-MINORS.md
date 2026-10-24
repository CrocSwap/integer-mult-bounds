# Five-minor encoding on the new native core

The actual PR3133 core has a forty-field selected set for which the
ordinary borrowed-state block is a dyadic unit. That block and its inverse
can be applied in place. They need no new private field or recursive
child. The resulting backward word carries all forty selected X inputs
into productive selected Y. An optional upper shear makes the borrowed-Y
response diagonal. The corresponding original-X response is also a
dyadic unit.

These are complete local words. A controller must still bind their
operator codes and views. No complete supplier or kappa gain is claimed.

## The actual matrices

Use the source matrix R, K=R^T/4, and J=I-KR. The pinned core has
RK=14I. Select the union S of these five eight-port minors:

    [0,7,20,27,36,46,57,111]
    [21,37,47,76,81,87,92,110]
    [1,6,22,28,33,49,58,109]
    [2,9,14,19,88,95,101,106]
    [3,8,15,18,89,94,102,105]

Let U be the remaining 72 ports. Each listed minor has R_A K_A=I.
The exact ordinary Gram matrix is R_U K_U=9I. Thus

    H = J_UU = I-K_U R_U,
    H^-1 = I-K_U R_U/8.

This H is the ordinary data block. It is not the helper-debt matrix
called H in the earlier clean-J proof.

## An in-place unit factorization

Use the retained minor A=`[4,11,12,17,90,97,99,104]` inside U. Write
U=A union W. Set L=K_A R_W and M=K_W R_A. Both matrices have 256 nonzero
entries, each equal to 1/2 or -1/2. Define

    T(a,w)=(a+Lw,w).

Then

    H = T^-1 [[-8I,0],[-M,I]] T.

To apply H, perform these steps in order:

    a += Lw;  w -= Ma;  a *= -8;  a -= Lw.

To apply H^-1, reverse the steps and invert each step:

    a += Lw;  a *= -1/8;  w += Ma;  a -= Lw.

Every shear has disjoint source and target sets. Each SCALE is a dyadic
unit. These operations preserve all information and use no scratch.
Each complete factor has 768 ADDs and eight SCALEs. Its cost is 7744 real
scalar primitives under the source price rule.

For the optional upper shear, insert

    x_S += K_S R_A a

after the -1/8 SCALE in H^-1, before either restore shear. At this point
the pivot a equals K_A R_U times the final ordinary output. The inserted
step therefore implements x_S += K_S R_U x_U after H^-1. It has 160
nonzero half-unit ADDs and costs 1600 scalar primitives. The pivot is a
live temporary query, not a saved query from a previous invocation. The
checker rejects the same short scatter after the pivot has been restored.

## Local endpoint maps

Write input x=(a,u), y=(b,v), in S,U order. Let Q be the diagonal positive
line operator on S and q=Q^-1. Physical input X is Q_p x_p on each port;
input Y is y. At output, physical X is F x' and physical Y is
F Q_p^-1 y', with common full operator F. No Q is commuted through a
dense matrix.

The balanced backward word first exchanges selected physical X and Y,
runs the complete clean-J backward core, and applies H^-1 to full-frame
ordinary X. Its map is

    X_S' = q b - J_SS Q a - J_SU v,
    X_U' = H^-1 u - v - H^-1 J_US Q a,
    Y_S' = Q a,
    Y_U' = v.

Add the fused upper shear to obtain the diagonal-borrowed variant. With
c=R_S Q a+R_U u, its map is

    X_S' = q b - Q a - K_S c/8,
    X_U' = u - v - K_U c/8,
    Y_S' = Q a,
    Y_U' = v.

The borrowed-Y block in X is diag(q,-I). Physical selected Y is exactly
F a in both backward variants. It contains the original selected X input.

The balanced forward word first applies H to ordinary input Y. It then
exchanges selected X and Y, runs the complete clean-J forward core, and
exchanges selected physical X and Y again. Its map is

    X_S' = a + q J_SS q b + q J_SU u,
    X_U' = u,
    Y_S' = b,
    Y_U' = H(u+v) + J_US q b.

The H input step acts on fields at I. The inverse and fused upper steps
act on full-frame X. They do not need line transforms, wrappers, helper
access, or private storage. Each physical exchange uses three unit ADDs
and one negative SCALE. It operates on the same physical addresses and
does not identify different logical frames.

## The stronger content unit

For the diagonal-borrowed backward word, put E=diag(-I_S,I_U). Apart
from the explicit input Q on S, its original-X response is

    A = E - KR/8,
    A^-1 = E + E K R E/4.

Both matrices are dyadic. The determinant is 1/256. The checker verifies
both inverse orders on all 112 columns of the actual source matrix using
integer numerator matrices. This is a content inverse; its placement in
a native controller is a separate obligation.

More generally, select k complete orthogonal minors. Then the ordinary
block is H_k=I-K_U R_U, with R_U K_U=(14-k)I. For k different from 13,

    H_k^-1 = I + K_U R_U/(k-13).

The same pivot factor uses the SCALE 1/(k-13). For k=5,9,11,12 this is a
dyadic unit. Five is the first positive number of complete selected
minors with this property. This statement concerns that minor family;
it does not rule out other selections or exact rational arithmetic.

The diagonal-borrowed original-X response is

    A_k = E + KR/(k-13),
    det(A_k) = det(E) ((1-k)/(k-13))^8.

For k=5 the inverse above is a dyadic unit. For k=1, the X response has
an eight-dimensional kernel even over the rationals: the columns of EK
span it. The complete two-register backward map is still a unit because
selected Y retains selected X. Thus rational division removes the
ordinary-block restriction at k=1, but it does not give an invertible
X response there. This distinction may affect the controller design.

For k different from 1 and 13, the general content inverse is
`A_k^-1=E+E K R E/(k-1)`. Within this complete-minor family, k=5 and k=9
give both a dyadic ordinary-block unit and a dyadic X-response unit.
The cases k=11 and k=12 give an ordinary-block unit, but their X-response
determinants are 5^8 and 11^8. They are not dyadic units.

## Complete local invoice and checks

| Word | Scalar primitives | Native rank mass | Native children |
| --- | ---: | ---: | ---: |
| Balanced backward | 173312 | 5073 | 3507 |
| Diagonal-borrowed backward | 174912 | 5073 | 3507 |
| Balanced forward | 174352 | 5073 | 3507 |

Each row includes the full 164514-scalar clean-J core, all physical
exchanges, all unit factors, and the 14-scalar final cleanup of C1 through
C7. The native profile is `{1:2433,2:724,3:228,4:102,5:20}` in every row.
No new native child, wrapper, or private field is added.

The emitter checks all six words, on both source providers. It replays
all 632 arbitrary live inputs, eight arbitrary owned inputs, and 91
private zero buffers. All 408 helpers restore; all owned fields and
zero buffers return to zero. The literal native core, scalar frames,
warp order, and zero-buffer lifetimes are checked. Q, K, and dual-K
remain separate ordered symbols. Only adjacent exact inverses cancel.
The source phase dependency uses the independently reviewed fresh native
recipes and the separate literal dual-warp tables.

Run with one process:

    python3 -I -B emit_balanced_five_minors.py
    python3 -I -B check_five_minor_unit.py

The two receipts record exact input and output hashes. Independent review
of this extension is still required. The decoder H_t H_s^-1 between
successive views, exterior phase, owner hosting, full recursive precision,
and the complete supplier bill remain open.

## Sources and credit

The source words, contributor credit, and commit-pinned links are in
`CLEAN-J-TRANSFER.md`. The selected minor partition and balanced endpoint
mechanism were developed in `lanes/native-escape-20261017` with the
coordinating and controller lanes. This lane independently derived the
pivot factor, fused the upper shear, and transferred the mechanism onto
the changed source geometry. The native-escape source packet is
`RAW-MINOR-SUBSETS.md`, with proof SHA256
`65c63ed233fd34dbc163b1c98f7c0c80533760656fac7d21acc1d47c995e3e08`.
Its program payload has decompressed SHA256
`10ec46ba44ed7bf7deeec98333c03e358b777898cb6642091e758afabd6e8a3d`.
OpenAI Codex assisted this work. No human
review or maintainer selection is claimed. No PR, push, or publication
commit was made.
