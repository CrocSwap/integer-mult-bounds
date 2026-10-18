# Independent review of the conserved QQ16 native words

The frozen payload passes this component review. No material defect was
found. The payload SHA256, after decompression, is

    2efe83c59978aa9c0db2c3e4eccc14cbfdcd3c9ce499432601b5dd34083472ef.

This review accepts the two complete local operators under the stated
full-cover view and sweep contract. It does not admit their new children
or sweeps to the global supplier. In particular, it does not prove a
complete controller, helper-owner assignment, recursive hosting, address
implementation, precision bound, or kappa improvement.

## Independent finite checks

Run from the workspace root, without `-O`:

```sh
python3 -I -B work/centre-encoding-campaign-20261014/lanes/residual-syndrome/physical-algebra/review-gauss/conserved-qq16/native/verify_native_review.py
```

The first output is

    PASS_INDEPENDENT_CONSERVED_QQ16_FULL_COVER_NATIVE_COMPONENTS

The checker imports no producer or phase helper. It reconstructs each
73-axis chart from the pinned doubled data. It then derives every route
as eight disjoint swaps of orthogonal basis vectors. This checks all
1008 actual port and stage routes. It checks both inverse orders of all
3650 affine cover maps, including each translation.

The checker expands each parity polynomial directly modulo four. It
checks all 1054 registered phase polynomials, and then follows the phase
through every wrapper event in all 28 backward and nine forward cases.
It checks the complete event sequence against the ordered construction.
This includes the exact relative owner path of every selected source,
not only equality of the source and target frames.

All 32 positive and inverse line recipes are compared with the pinned
component bytes. Their 16384 Gaussian integer columns are evaluated
independently, including the constant scalar phase. A scalar phase
mutation fails for each recipe. Separate controls reject the positive
line in place of an inverse line and an omitted payload translation.

Both retained core words equal the pinned complete words. Their local
frame ledger, endpoint frames, scalar accesses, and child profiles are
rechecked. The old child kernels and global core embedding are inherited
from the pinned native and bridge reviews; they are not re-proved here.

Every native case has exactly the scalar projection checked by the
independent scalar review in the parent directory. That review checked
the complete B and F words on all 712 formal inputs, all 480 helper
outputs, the eight owned zero outputs, both data inverse orders, and
all sixteen selected sums. It also rebuilt the coefficient matrices and
each scalar block from the actual R. This review pins that receipt and
checker. It does not treat the producer's common-chart output as an
independent oracle.

## Owner action, phases, and order

For a cover map use the right action

    M(g,a) f(d,z) = f(dg,z XOR d a).

Direct substitution gives

    M(g,a) M(h,b) = M(gh,a XOR g b),
    M(g,a)^-1 = M(g^-1,g^-1 a).

The owner action and the payload translation have distinct roles. To
test the distinction, give owner I constant input zero and owner g
constant input one, with g nonidentity. The correct map reads one at I.
A payload-only permutation at owner I still reads zero. The actual
chart routes in this packet include such a nonidentity g.

If the frame phase at the identity owner is phi(w), the map changes it
to phi(g^T w)+2 a dot w modulo four. A line with axis q therefore changes
to a line with axis g q. This follows from the changed owner in the
input frame. It does not follow from applying g to the payload address.
The checker uses this exact identity and checks all constant phases
through the line kernels.

Write the native boundary operator at port p as T_p. The accepted bridge
identity is A_p T_p=T_common D_p, where D_p is the right-owner route.
Thus a scalar source block between aligned ports acts logically by
D^-1 M D. For a source q read at target p without moving the target,

    A_p^-1 A_q T_q = T_p D_p^-1 D_q.

This proves the required order of the relative path. The checker
compares each literal path with this group product, including its
translation, and checks its undo. The paths may not be reversed merely
because the before and after native phases are equal.

In B, inverse C_q first gives each selected X_T field the current Y
type. The A copies read the original Y before E_t changes it. Each
positive line on C0 changes that copy to the X target type. The future
logger precedes the current U update, selected swaps, and final T query.
The final T query reads the changed U fields. All source paths are
undone, and positive C_q restores the eight X_T types before the core.

In F, the retained forward core reads the original source first. The
five source blocks then run in their fixed order. The A target copies
read the changed source. Their inverse C_q gives the Y target type.
Stage zero has a separate completed-X base case with no owner maps.
This review uses the pinned core lift for the incoming F frame; the
wrapper phase replay starts from the completed frame after that core.

These statements hold for every tensor length. Each physical address
layer has the same owner route and translation, and its exact line
identity is already fixed, including scalar phase. The phase equality
is summed over the layers. The scalar coefficient acts once on the
port index. It is not replaced by a tensor power of R. Spectator axes
are unchanged.

## Ordered maps and inverses

The full-cover conclusion uses the ordered pair proof, not the
common-chart coefficient replay alone. In chart s let

    R_s=R D_s,    K_s=D_s^-1 K,    P_s=K_(s,T),
    ell_s=R_T pi_T D_s,    Pi_T=P_s ell_s.

Portwise routes preserve coordinate supports. Therefore
R_s P_s=ell_s P_s=I, R_s K_(s,A)=I, and R_s K_(s,U)=12I.
No relation between D_s and a future D_t is needed.

For the future logger E_t, its added term has only A rows and no A
columns. Hence E_t^-1=2I-E_t. Put

    u=E_t y,    a=ell_s x,    b=R_s u.

The backward word gives

    Y'_A=u_A,
    Y'_U=y_U+K_(s,U)a,
    Y'_T=u_T-P_s(b+11a),
    X'_U=x_U-y_U,
    X'_A=x_A+y_A-u_A,
    X'_T=P_s(b+12a).

To invert it, first read a=R_s Y' and b=ell_s X'-12a. Recover
u_U=Y'_U-K_(s,U)a, u_A=Y'_A, and u_T=Y'_T+P_s(b+11a).
Then y=E_t^-1u, x_U=X'_U+y_U, x_T=P_s a, and
x_A=X'_A+Y'_A-y_A. All products retain their order.

For F, put f=R_s x. The source becomes

    X'_U=x_U-K_(s,U)f,
    X'_A=P_(s,A)ell_s x,
    X'_T=P_s f.

Its target has Y'_U=y_U+X'_U and Y'_S=y_S+x_S-X'_S for
S=A union T. Read f=ell_s X' and c=ell_(s,A)X'. Recover
x_U=X'_U+K_(s,U)f, x_T=P_s c, and
x_A=P_(s,A)(f-c-R_(s,U)x_U). The target equations then recover y.
These are two invertible data maps. B and F are not mutual inverses.
Their inverse formulas do not provide free inverse native access at
the output frames. Neither complete map is invertible on the discarded
owned private input values.

## Sweeps, scratch, and invoices

Every common-frame scalar block is a full-cover sweep with a completion
barrier. A subsequent block can therefore read its completed output.
Each port route is a bijection on its data family. At a fixed common
owner, the different port fields occupy distinct addresses. Within one
sweep the frozen scalar order gives the exact dependency order.

Each private body starts with CLEAR C0 and ends with CLEAR C0 in frame I.
It forms one target correction, applies its native line, and adds the
result before the next owner starts. The temporary source fields are
unchanged during this body. This needs one serial owned C0 array, not
one C0 for each cover owner. The checker verifies all eight row bodies,
their source paths, their reversals, and their complete boundaries in
each case. C1 through C7 are untouched by the wrappers; the retained
core clears them. The 480 ordinary helpers are untouched by the new
wrappers and restored by the inherited complete core.

The complete invoices agree exactly with the producer:

| Word | Added scalar | Complete scalar | Added rank-one children | Native mass | Added map bound |
|---|---:|---:|---:|---:|---:|
| B |12848|214986|24|5546|576|
| F, positive stage |9072|211210|8|5530|304|
| F, stage zero |9072|211210|8|5530|16|

B has profile {1:2436,2:418,3:432,4:142,5:82}. F has profile
{1:2420,2:418,3:432,4:142,5:82}. The map bound includes two wrappers
per new line child. The independently recomputed formal scalar prefix
bounds are 573411134169296526275133/64 for B and
5413950274051752469/256 for F, with ceiling logarithms 73 and 55.
These are finite scalar bounds, not recursive precision certificates.

The sweep and scratch argument specifies the abstract component access
contract. It does not allocate helpers for the new recursive children,
show that their live intervals fit the selected supplier, or price a
physical implementation of the cover views. Those remain material
obligations for any supplier claim.

This review used separate OpenAI Codex agent work. It is not independent
human review. No frozen producer artifact was edited, and no PR or
commit was made.
