# Review of the eight promoted native modes

The two local words in `../history-encoding/MODE-PORT-PROGRAMS.json.gz`
have the stated native maps on arbitrary inputs. The variant in
`../history-encoding/TARGET-MODE-PORT-PROGRAMS.json.gz` also passes. The second
variant keeps the eight new roles in one target type in both orientations.
The repeated-label variant also passes. These results do not supply a global
controller or a complete supplier.

The program payload hashes are, respectively,
`4cf7846365aa8238d23f8a663b3e9b59612555c1524ef40f9ca69f5b800f530a` and
`00cd70ec2614ea3fc02e33ab1c8b7335a63a9fc4e502997155ee848542d7f8c2`.
The source is the selected word at commit
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
`MODE-PORT-REVIEW.json` and `TARGET-MODE-PORT-REVIEW.json` record the independent
checks. `HISTORY-BASIS-REVIEW.json` records the earlier independent basis and
complete Fourier phase check.

## The scalar mechanism

Let R be the clean centre map and H its helper map. Let V be the helper
response to an independent perturbation of the eight centre carriers. The
independent cut calculation gives

    R R^T=56I,   H V=I,   K=R^T/4,   P=KR.

Omit the centre cut and the dirty preload, and multiply the eight retained
centre carriers by -1. The raw word has scalar map

    x'=x,
    y'=y+x-K(Rx+Hh),
    h'=h-2V(Rx+Hh).

The basis matrix S is invertible and uses only the 122 helpers that have
native entrance I and exit F. Its eight selected rows equal H, and SV is
the coordinate inclusion of those eight rows. Put encoded helper coordinates
equal to (u,w), with u in the selected positions. Apply S^-1 before the raw
word and S after it. The result is

    x'=x,   y'=y+(I-P)x-Ku,   u'=-u-2Rx,   w'=w.             (1)

Every coordinate of w is an arbitrary input. This is exact restoration in
the supplied logical coordinates, not a zero-input calculation. The basis
does not touch either old data bank. Outside the 122 common-frame helpers,
the old helper words are unchanged.

The backward word uses S^T at entry and S^-T at exit. Its raw word is the
logical inverse transpose of the raw forward word. Consequently its full
scalar map is the inverse transpose of (1):

    x'=x-(I+P)y-2R^T u,   y'=y,   u'=-u-Ry/4,   w'=w.       (2)

For example, the inverse of (1) has
u=-u'-2Rx' and y=y'-(I+P)x'-Ku'. Transposition gives (2).
The independent replay checks both maps on all 704 persistent input columns
by propagating transpose columns through the literal instructions. It also
checks the full matrix identity A_forward^T A_backward=I. This inverse-
transpose assertion concerns the logical scalar maps. The physical maps
have the separate native entry and exit frames below.

## Native placement and arbitrary helper inputs

Write F for the full nine-axis native operator and T_q=F C_q^-1. All native
operators in this section can be replaced by their lambda-th tensor powers.
The old source entrance is C_q, and its exit is F. The old target entrance
is I, and its exit is T_q.

The full original native event list is retained. The added basis operations
are before all of that list or after all of it. Thus their 122 helper
operands have the exact common native frame I at entry and F at exit.
Scalar basis operations commute with the common F. The scalar proof of
w'=w therefore restores every ordinary helper to its old physical endpoint.
It does not attempt to undo a basis after its operands have different frames.

The dual variant has these additional endpoints:

| Orientation | Promoted mode entrance | Promoted mode exit | Position of C_n^-1 |
|---|---|---|---|
| Forward | I | T_n | After the entire output basis |
| Backward | C_n | F | Before the entire input basis |

For the forward word, let physical inputs be X,Y,U. Put x_p=C_p^-1 X_p.
Its physical outputs are

    X'_p=T_p X_p,
    Y'_p=T_p[Y_p+sum_j (I-P)[p,j] x_j-sum_k K[p,k] U_k],
    U'_k=T_(n_k)[-U_k-2 sum_p R[k,p] x_p].

For the dual backward word, put u_k=C_(n_k)^-1 U_k. The outputs are

    X'_p=F[x_p-sum_j (I+P)[p,j] Y_j-2 sum_k R[k,p] u_k],
    Y'_p=T_p Y_p,
    U'_k=F[-u_k-sum_p R[k,p] Y_p/4].

Every other helper keeps its old native operator on its arbitrary input.
The normal labels are 42, 7, 25, 52, 82, 127, 97, and 76, in that order.

The both-target variant moves the backward C_n^-1 operations to the end,
after S^-T. Both orientations then have mode entrance I and exit T_n.
The scalar formulas (1) and (2) are unchanged. In the backward physical
formula, use u=U and replace its mode output F by T_n. This supplies one
consistent local native role type for a controller that carries the modes
between calls. It does not itself establish the required routed global
content or final cleanup.

One can also put the descents at entry in both orientations, giving mode
entrance C_n and exit F. This follows from the same common-frame proof.
At the time of this review, an emitted both-source program has not been
independently checked. It is not part of either PASS receipt above.

The labels of the eight descents need not be the eight centre normals.
Each descent acts after all scalar output operations, or before all scalar
input operations. Thus it only sets that mode's native type. The repeated
variant uses label 11 on all eight modes. Its payload hash is
`e8afc81d1509247cb0dcc188d3e47cc3ba6c1bcf18fdfb7fa1c6c6c4a3260d4b`.
`REPEATED-MODE-PORT-REVIEW.json` gives the same full independent check.
This choice can use the existing route for label 11. It does not require
an extra cover generator. Exact global content and closure remain open.

The forward scalar map also has a useful change of coordinates. Put
v=y-(R^T/8)u. Then (1) gives

    v'=v+x,   u'=-u-2Rx.

Thus a target-to-mode basis change separates an ordinary data shear from
the mode reflection. A controller must prove access to that basis at its
actual native boundaries. The forward and backward words do not use the
same conjugated basis automatically: the backward word requires the dual
basis for an inverse-transpose statement.

## Complete phases and tensor lift

The added event is the exact operator

    C_n^-1=((1-i)I+(1+i)T_n^address)/2,

where T_n^address means address translation by n. This notation is distinct
from the full output operator T_q above. Its phase is specified, not inferred
from a binary subspace label.

The normal recipes in `../coherent-port/EXTENDED.json` provide a rank-one
child and two monomial maps for each C_n^-1. The independent native interpreter
checks each recipe's complete Pauli action and its exact Gaussian-dyadic
image of the zero basis vector. It also checks C_n^-1 C_n=I and
C_n^-1 F=F C_n^-1. These give 24 complete operator equalities. Each of eight
deliberate global phase changes is rejected. This check imports neither the
original Clifford compiler nor the history emitter.

For the repeated label, `normal_rank_one_recipe.py` gives a direct recipe.
Choose an invertible binary matrix A with A e_1=q. Then

    C_q^-1 = P_A (-i Z_1 C_1 Z_1) P_A^-1.

The first and last factors combine into two monomial maps around C_1.
This follows from C_1^-1=-i Z_1 C_1 Z_1 and the conjugation of address
translation by P_A. It applies to every nonzero binary label q. The full
endpoint F C_q^-1 has Fourier rank nine minus the parity of q. The recipe
for q=11 has one rank-one child and an endpoint of rank eight, as checked
in `REPEATED-LABEL-RECIPES.json` with exact phases.

Exact operator identities remain exact under every tensor power. Scalar
coefficients act on role coordinates and remain unchanged under that lift.
All common-frame scalar accesses therefore retain the same maps for every
lambda and all spectator inputs. The prior basis review also checked all
1,048,576 Fourier characters across the eight 17-dimensional normal bridges.

## Local bill and its scope

Both reviewed variants have the same local invoice per orientation:

| Item | Value |
|---|---:|
| Data coordinates | 232 |
| Ordinary helper coordinates | 472 |
| Persistent scalar input columns checked | 704 |
| Private centre registers used | 0 |
| Scalar macros | 20,389 |
| Real-component dyadic primitive bound | 204,418 |
| Retained native events | 5,056 |
| Added rank-one children | 8 |
| Added monomial maps in their lowering | 16 |
| Paid profile | 1:2420, 2:418, 3:432, 4:142, 5:82 |
| Paid rank mass | 5,530 |

The scalar bound excludes the 16 added monomial maps and address work.
The eight unused private centre arrays may retain arbitrary contents because
the new word never accesses them. The original native coefficient workspace
is a separate retained obligation.

The eight promoted helpers previously had full rank-nine productive endpoints.
Each new mode has rank-eight productive growth. Relative to the old word,
the paid rank falls by 56 but productive growth falls by eight. Thus the
local rank balance improves by 48, provided a full controller can use the
new modes as productive independent state and close their output contract.
This is a local comparison. It is not a recursive saving or an exponent.

A full construction must now route the eight normal roles, account for
their changed contents at each stage, complete the mode outputs, replace
the eight old helper owner assignments, and lower all new operations.
The logical echo identity alone is insufficient: its two inputs must use
the same source and mode coordinates, which successive native charts do
not provide without proof.

## Reproduction

Run `review_mode_ports.py` with the pinned original source directory, either
mode program and receipt, `../bounds-review/review_centre_free.py` as the
transpose checker, `verify_native_lift.py` as the native checker, and
`../coherent-port/EXTENDED.json` as `--normal-recipes`. The two output files
listed at the start identify the exact program hashes. All checks ran with
`python3 -I -O -B` and remain active with optimization enabled.

The history-encoding lane supplied the basis, raw echo, and promoted words.
The coherent-port lane supplied the normal-child recipes. This lane supplied
the independent scalar and native review. The selected supplier and native
compiler retain their source lineage. This work used substantial OpenAI
Codex assistance and independent agent review, not independent human review.
