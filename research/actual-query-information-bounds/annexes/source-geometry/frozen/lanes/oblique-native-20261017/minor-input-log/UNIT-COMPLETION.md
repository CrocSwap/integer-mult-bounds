# A unit criterion for the mixed source partition

This theorem gives the exact condition under which an input log repairs
the mixed source partition of the raw selected backward word. It also
gives an inverse for the complementary data code. The theorem applies
to ordered operators. It needs no commutation relation and no identity
for BD. It is a content theorem. Native placement and cost are separate
obligations.

## Modules and the local map

Let E and U be finite free right modules over a ring with identity. Let
Q be an invertible map on E, and put q=Q^-1. Let

    B:U->E,   D:E->U,   M:U->E,   K=MD:E->E.

Products denote composition, with the rightmost map applied first.
The original data are (a,u) in E+U. The original source is (b,v) in
E+U. Put beta=qb. Consider the local map

    d=Qa+Mv,
    h=beta+Bv,
    w=u-v+D(d-beta),
    r=v.                                                   (1)

The actual A8 input-minor word has this map. It has dim(E)=8,
dim(U)=104, BD=13I, and a current ordinary minor with MD=I. The
native packet MINOR-INPUT-LOG.md proves that particular instance.
Equation (1) defines the algebraic family in this note. It does not
assert a native implementation for every B, D, and M.

The complete map (1) is a unit for every M. Its direct inverse is

    b=Q(h-Br),
    a=q(d-Mr),
    u=w+r-D(d-h+Br),
    v=r.

The question is stronger: does the mixed partition (w,d), by itself,
give a unit map on the source when the original data are fixed?

## The exact criterion

The source map to (w,d) is a unit if and only if K=MD is a unit on E.
To prove this, remove the fixed data terms from (w,d). Its linear
source part is

    w=-D beta-v+DMv,   d=Mv.

Make the reversible output change

    f0=-w+Dd,   g=d-Mf0.

This gives

    f0=v+D beta,   g=-K beta.

The reversible input change (beta,v)->(beta,v+D beta), followed by
a change of component order, leaves diag(I,-K). Therefore the source
map is a unit exactly when K is a unit. This factorization proves
necessity over the ring; a test for a nonzero kernel alone would not
prove that statement over a general ring.

Over a field, a source code for this partition therefore needs a log
of rank at least dim(E). This lower bound applies to the partition
(w,d) in (1). It is not a lower bound for every native controller or
every possible output partition.

## Source and data codes when K is a unit

Assume that K has a two-sided inverse H. Define

    e=(I-H)d-HMw,
    f=-w+DH(d+Mw),
    z=h-e-Bf,
    t=r-f.                                                 (2)

Put C=H(Qa+Mu). Direct substitution gives

    e=beta-C,
    f=v-u+DC,
    z=Bu+(I-BD)C,
    t=u-DC.                                                (3)

Thus, for fixed data, (e,f) has source coefficients q and I, with
no source cross term. The complementary coordinates (z,t) contain
no source value. Their exact inverse is

    Qa=-Mt,
    C=z-Bt,
    u=t+DC.                                                (4)

Equation (4) follows from MD=K and HK=KH=I: more directly,
-Mt=-Mu+KC=Qa, and z-Bt=C. Equation (4) needs no further inverse.
If B, D, M, and H are dyadic, all of these coefficients are dyadic.
After (4), recover a=q(Qa), b=Q(e+C), and v=f+u-DC.

The full change of output coordinates in (2) is also a unit. An
inverse that uses no H is

    d=Mf,
    w=-f+D(Mf-e),
    h=z+e+Bf,
    r=t+f.                                                 (5)

To prove the first two identities, use Mf=d and H(d+Mw)=d-e.
These follow directly from (2). The other two identities are the
definitions of z and t. The order of the factors in (2)--(5) is part
of each formula.

For the actual current minor, K=I. Then (2) reduces to

    e=-Mw,   f=-w+D(d+Mw).

The source code resides in this mixed (w,d) partition. The selected
output d=Qa+Mv contains the input ordinary-source minor; it is not
the complete selected source code. In particular, e reads ordinary
X. This specifies the meaning of the source-channel sentence in
the frozen MINOR-INPUT-LOG.md proof.

## Composition through every pair count

The same result extends the controller in MIXED-CONTROLLER.md.
Each backward stage s has maps B_s,D_s,M_s and a unit K_s=M_sD_s.
Put H_s=K_s^-1. Each forward stage t has the stated content map

    (h,k;d,v)->(h-qB_t k,k;d,v+L_t k),
    L_t=I-D_tB_t.

Keep the ordinary suffix, bridge, and final triangle order from the
companion proof. There is no selected bridge. Recover each w_i
from the final ordinary X triangle. Let

    P_i=L_t(i-1)w_(i-1),   P_0=0,
    e_i=(I-H_s)d_i-H_sM_s w_i,
    F_i=-w_i+D_sH_s(d_i+M_s w_i)-P_i,
    C_i=H_s(Qa_i+M_s z_i).

The same substitutions as in (3) give

    e_i=qb_i-C_i,
    F_0=y_0+D_s0 C_0,
    F_i=y_i+D_si C_i-D_t(i-1)B_t(i-1)z_i,  i>0.

Define

    Z_i=f_i-e_i-B_s F_i-B_s P_i+qB_t w_i,
    T_i=r_i-F_i-P_i-L_t w_i.

Then

    Z_i=B_s z_i+(I-B_sD_s)C_i-qB_t z_(i+1),
    T_i=z_i-D_sC_i+L_t z_(i+1).

Start with z_m=0 and work backwards. Remove the known next suffix
from these two equations. Apply (4) to the remaining local pair.
This recovers Qa_i and z_i. Then x_i=z_i+z_(i+1). Recover the
source from the displayed e_i and F_i equations. At the first pair,
subtract a_0 from the recovered b_0 to undo the initial full forward
call. This proves an inverse for every positive pair count.

This general proof does not use B_sD_s=13I. The actual emitted
native words still have their own fixed graph hypotheses. The
extension permits other input logs with unit M_sD_s at the content
level. A proposed log must still have legal access in its current
chart, and its decoder must still pass native placement and cost
checks.

## Verification and scope

The companion check_unit_completion.py checks the local map and
its two inverses with ordered formal operators. It uses only
Qq=qQ=I, MD=K, and HK=KH=I. It also checks the exact necessity
factorization. The earlier check_mixed_controller.py checks the
actual K=I controller for one through eight pairs. Its proof supplies
the controller order used above.

The current native instance has a 32-term signed-half input log and
adds no native child to the raw B word. The complete decoder still
needs access to d in its hole frame, cross-frame output operations,
terminal types, helper ownership, and a full recursive cost. This
note does not resolve those obligations or claim a kappa change.

The coordinating lane supplied the general K=MD criterion and its
source and data formulas. The oblique-native lane supplied the
explicit unit factorization and the all-pair extension. The
independent-review lane supplied the short output-code inverse for
K=I; equation (5) gives the same inverse for every unit K. The work
used OpenAI Codex under the user's direction. Independent review
is required. No PR, push, or publication commit was made.
