# A forest caller with interval-coalesced idle transforms

This is a new complete caller architecture, using the existing exact local
native suppliers as leaves. It changes the scalar controller and the placement
of idle work; it does not claim a cheaper local native. The F19 instance gives
strict raw savings 0.0035448718 on the BIT branch and 0.0031454352 on the complex
branch. Effective finite compilation is recorded in `FOREST-F19-ADMISSION.json`.
The inherited physical-native, fixed-precision, tape and analytic-recovery
premises remain. Neither number reaches 0.004.

## 1. The physical leaf contract

The BIT leaf is the prior exact temporal-cut native, SHA256
`bd39feba78d80df93cbc7240daabe06609107af725d4ab6ba47d4b02ac22184d`.
It has 111 main ports, body rank 7, paid profile

    1411 H1 + 1250 H2 + 89 H3 + 50 H4 + 10 H5 + 102 H6 + 7 H7,

and independent productive helpers `30 H4 + 419 H8`. Its 347 owned labels
remain owned and receive no productive credit. The local word, endpoint receipt
and route receipt are copied byte-for-byte to `inputs/`.

The complex leaf is Ali Romman's PR5827 native, SHA256
`5d50e5654910c9535e9025de0f644bb2dece2396e799b4a766110363448fd0b0`.
It has 104 main ports, body rank 8, paid profile

    2225 H1 + 456 H2 + 498 H3 + 98 H4 + 163 H5 + 9 H6 + 6 H7,

and independent helper profile

    18 H1 + 7 H2 + 4 H3 + 107 H4 + 14 H5 + 9 H7 + 18 H8 + 385 H9.

All 770 public inputs are arbitrary; its 29 owned labels are charged. The local
word, result and proof are pinned in `INPUTS.json`. The existing exact quartet
normalizers are used jointly on the two main fields, including their absolute
phases. Independently normalizing three matrix entries would not suffice.

After the quartet normalizers, the complex main block is

    D L(Q^{-1}),  L(A) = [[I,0],[A,I]],

where Q acts on one common head axis and D acts on a fresh block of eight body
axes. This follows directly from C_F=C_head C_body, C_P=C_head and C_Q=C_body.
All spectators are carried unchanged. Different leaves have disjoint body
blocks. All main ports use the same head and body operators after their own
ordinary monomial adapters.

For the complex Gaussian convention Q²=M is an exact ordinary whole-job Pauli
translation, and M²=I. Set

    a=(1+i)/2, b=(1-i)/2, R=a I+b M.

Then R²=M, R^{-1}=conj(a)I+conj(b)M, and

    q=Q R^{-1}=R Q^{-1},  q²=I.

Conjugating D L(Q^{-1}) by diag(I,R) gives D L(q). Composing with the ordinary
L(-1) gives D[I+(q-1)E21]. R commutes with D because the two act on disjoint
axes. At the final endpoint multiply by R to turn each q back into Q. The same
construction works for every column width f: Q and M here mean their whole-job
f-fold operators, and the scalar coefficients a,b do not depend on f.

R is an ordinary Gaussian-dyadic operation, not a paid linear combination of
two native jobs. One explicit zero-clean realization is

    t←x; t←M t; x←a x+b t;
    u←x; u←M u;
    t←t−conj(b)x−conj(a)u=0;
    u←M u; u←u−x=0.

The t,u arrays are owned; their zero states may be cleared. This uses two
copies, three ordinary M routes and a fixed number of dyadic scalar operations.
Conjugating a,b implements the inverse. The prior independent exact coefficient
check is retained in the source provenance; the identities above also prove it
directly. No small parameter or approximation is introduced.

On the BIT branch Q is already involutive and the analogous normalized leaf
is D[I+(q-1)E21]. All signs below reduce modulo two. Thus one integral
controller handles both branches.

## 2. Integral head geometry

For F full leaves use p=F−2 scalar coordinate pairs. Write the symplectic form
as ω(v,w)=vᵀJw with J a direct sum of [[0,1],[-1,0]]. For a vector u let

    N(u)=−u uᵀJ.

It is square zero. A carry (a,b) satisfies ω(a,b)=1. If x,z is a fresh
coordinate pair, define

    A=a+x, B=a+z, C=a−x+z.

The active A/B plane and its idle complement are

    R=span(A,B),  K=span(a,b+x−z).

These are orthogonal symplectic planes whose direct sum is
span(a,b,x,z). The three carries are ordered so that every head leaf u_i
has ω(u_i,u_j)=1 for i<j. At the root the three carries are

    (x,z), (z,−x), (−x+z,−x).

A nonroot binary node recurses into (A,B) and (B,−A), then emits a thin head
query at C. This gives F full calls, F−3 thin calls and 2F−3 head vectors.

For the emitted integral vectors, the exact product at q=−1 is −I:

    ∏_i [I−2N(u_i)] = −I.

At q=1 every factor is I. Therefore, over Q[q]/(q²−1), their product is qI.
The emitter verifies the two identities directly. It also verifies the
separate characteristic-two identity Σ_i N(u_i)=I. Since (q−1)²=0 in
F2[q]/(q²−1), the latter gives the same qI endpoint over F2. The independent
root checker instead expands the entire chronological polynomial word over
Z[q,d_0,...,d_(F−1)]/(q²−1); it found the exact diagonal endpoint. This integer
polynomial identity itself reduces modulo two.

## 3. Why the idle grouping is legal

A full leaf applies its body D_s on its two-dimensional active plane. The
coordinate projection onto its root-to-leaf path decomposes as that plane
plus one K plane from each ancestor. These summands are pairwise orthogonal.
One may first imagine paying a separate D_s on every such ancestor K plane.
The resulting augmented body projection is a coordinate projection. All these
coordinate projections commute, and each commutes with the preceding head
prefix; the emitter checks these identities exactly.

At an internal node K annihilates every head in the complete A+B interval,
including every descendant thin head. It also annihilates every descendant
full active plane and commutes with each descendant idle projection. Thus all
the D_s on this K plane can move through that interval and combine into one
product over all its full leaves. This product is paid as two whole native
jobs of rank s F_v, where F_v is the number of full leaves below the node and
s is 7 or 8. They are placed immediately after A+B and before the node's thin
C query. They are never moved through C or across an unrelated sibling.

The root has no external carry complement, so it needs no idle work. Each
internal coordinate pair ends with q times all body factors under its node.
It therefore gives two independent targets of rank 1+s F_v. Every native
helper retains its complete independent endpoint. There is no shared-input
or zero-at-entrance assumption on any public field.

The F19 instance has root subtree sizes (4,7,8). Its sixteen nonroot internal
sizes are nine 2s, one 3, four 4s, one 7 and one 8. The controller file includes
every FULL, THIN and grouped IDLE in chronological order, and every literal
integer basis and inverse basis needed to place a native plane. Every basis
entry and inverse entry is 0,1 or −1.

For a carry (a,b), the first two columns (b,−a) put N(a) into the standard
lower shear E21. Remaining columns are projected coordinate units. The
emitter checks each basis inverse, native shear and two-field body projection
exactly. No paid transform is hidden inside a scalar basis change.

## 4. Complete inventories

Let H_r(t)=r^t. For subtree multiset S, the complete profile is

    T = F T_local + 2n H_(1+sF) + 2n Σ_(k in S) H_(1+sk),
    P = F P_local + n(F−3) H1 + 2n Σ_(k in S) H_(sk).

Multiplicity in S is retained. The ordinary/source script reconstructs these
profiles from the literal event list, not just this formula. At F19 the rank
surplus is 801 on BIT and 808 on complex. The complete raw crossings are
enclosed, by rational interval arithmetic, in

    BIT:     (0.0035448718284785, 0.0035448718284791),
    complex: (0.0031454352668594, 0.0031454352668600).

Both complete invoices remain negative at 0.004. The crossing statements
describe these fixed profiles; they are not upper bounds for other callers.

## 5. Ordinary work, ownership and precision

A scalar basis can always be executed by copying all m inputs to owned
arrays, subtracting those copies from the public arrays, adding the prescribed
linear combinations back, and clearing the owned arrays. Public arrays are
zeroed by legal subtraction, never by public CLEAR. Since the matrices have
entries 0,±1, this costs at most 8(nnz(B)+4m) real scalar primitives and m
owned arrays. Both directions of every FULL and IDLE basis are charged.

A thin rank-one head query computes its fixed linear functional in owned
storage, applies one rank-one native query and its ordinary q adapter, then
adds the specified multiple of the query difference to the main fields.
All temporary arrays are owned and explicitly reset; the bound reserves fresh
banks for all of them. No productive credit is assigned to scratch.

Local native ordinary work is bounded by 10^7 per invocation, as in the
pinned exact source. For complete embeddings and normalizers at ambient height
h≤153, 8(10h²+10h) elementary real operations per whole-job route is a loose
explicit bound: binary Gaussian elimination, address swaps, linear phases,
and the quadratic phase polynomial all have O(h²) fixed terms. Spectator
coordinates are included. The certificate charges four routes for every paid
and productive call, plus eight per full main interface and per grouped idle
plane. It also separately charges all basis programs and all R adapters.
The resulting visible plus routing bound is below 10^12 per raw invocation.

The owned reserve is recomputed from every native invocation, both directions
of every basis, and sixteen fresh arrays per thin/full/final head adapter.
Its exact bound is in the receipt and is below 10^7 per raw invocation.
The finite compiler therefore uses O=O_raw U_raw, Z=W+O and
G=10^12 U_raw+8R, followed by E=64(Z+N+P+G+1)^3 and C0=32N(P+E)^2.
These replace the old controller's numerical constants. Fixed scalar growth
and all native row-norm growth are absorbed by these recomputed constants;
there is no variable conditioning parameter.

## 6. Effective finite compilation

`forest_admission.py` uses unchanged, authenticated rational Taylor interval
arithmetic and the retained finite target-restriction theorem. For both
branches it takes product power768, paid cutoff15^768, productive floor16^768,
and both tail offsets1/5. The exact strict inequality

    alpha^768 + 2 gamma^768 + lambda^768 < 1

is certified with an outward rational upper bound. Every discarded complete
target is owned zero with its original paid work retained. Paid jobs above
the cutoff split on disjoint axes. The separated finite uniform compiler is
then explicit, including its integer threshold H and uniform native rank2^H.
The astronomical finite product is specified algorithmically, not materialized.

The strict uniform savings are 0.00354487179 and 0.00314543519. On BIT the
covered saving is 0.00354487178. Three exact ordinary-wrapper bootstrap steps
from the previously admitted0.00351656399 yield the strictly admitted ordinary
saving0.00354487177. The ordinary wrapper uses its full retained envelope;
only the limiting term is displayed in the receipt after all other terms are
checked by the inherited inequalities. The outer ledger must use the new
complex and BIT numbers and the new fixed source constants.

## Reproduction and scope

Run `python -B emit_forest_controller.py 19` and
`python -B forest_admission.py`. The independent full polynomial checker is
`../root/audit_forest_controller.py`. It imports no proposer implementation,
adds body exponents as ordinary nonnegative integers, and checks all34×34
entries of the complete endpoint. Its receipt is
`../root/FOREST-F19-INDEPENDENT.json`.

The construction is exact at the native-interface level. It strengthens the
conditional construction under the existing realization and recovery premises;
it is not an unconditional integer-multiplication theorem, and no uniform
word or hardware implementation is claimed to have been materialized.
