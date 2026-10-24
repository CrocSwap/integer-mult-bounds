# Independent review of the dyadic phase-class capture

The frozen construction passes. The actual response admits a dyadic
involution C with rank(C-I)=16 and determinant one. Both literal
capture words cost 4044 old real scalar primitives. The class-supported
response K=C E C has a 1544-primitive additive word in either direction.
All 640 arbitrary input columns and both capture inverse orders pass.

The conditional 112-H1 factorization requires the carried rank-four
frame W_R. It does not apply to the current W45 exit. A separate binary
check in this review gives rank two for all 56 proposed pair ratios in
the actual W45 frame. No native phase recipes or complete caller are
admitted by this review.

## Source binding

The producer packet is
`independent-review-20261017/phase-class-dyadic-capture-20261020`.
Its freeze SHA256 is
`3b7601e537cdd570295cde170a2491de876d7cae7814313b0c4a1f685c199ecd`.
Only its `verified-normal` and `verified-optimized` outputs are final
evidence. This review verifies every frozen file.

The actual rank16 response is read from the decompressed v2
`EXTENSION-PROGRAM.json.gz`, SHA256
`d466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4`.
The cyclic pair geometry has SHA256
`3034e1df3670f64e5b79a51a435d7903f3be7cef10d6b486a8bd4d420c989585`.
The actual W_R circuit is read from the shared-root v2 program,
decompressed SHA256
`71dec1d8e33625e301c8bfde37d8c08b0019124e1525500555fcc704530bf4a6`.
The actual W45 circuit is read from `GAUGE-PROGRAMS.json`, SHA256
`20f14f021623761160b0ef461904b38f82efdc7dd0c4008271620415bf747701`.

The checker imports no producer or compiler code. It constructs the
matrices from the source group signs and port labels. It uses a new
forward sparse-row interpreter for every scalar prefix and a binary
Pauli interpreter for the frame checks. All source paths and pins are
in `REVIEW.json`.

## Independent algebra

The source has eight signed groups of size six and eight groups of
size eight. The groups partition all 112 ports. In mode coordinates,
each response is I-dd^T. The actual pair code H gives

    E = H^-1 (direct sum of I-dd^T) H.

The checker constructs this matrix and compares it entry by entry
with the source response. It also verifies the symmetry of E.

The root space R=span(30,45,75,384) is a four-dimensional even
isotropic binary space. The actual labels give fourteen q+R classes
of size eight. H preserves each class. A six-mode group meets three
classes in two ports each; an eight-mode group meets four.

For a six-mode group, let p,t be the selected class pair. Define

    a_p=2d_p, a_t=0,
    b_p=3d_p, b_t=-d_t,
    u=a-d, v=(d-b)/4, S=I+uv^T,

with a and b zero off the pair. Direct calculation gives

    v^T d=1, v^T u=-2, S d=a, b^T S=d^T, b^T a=6.

Thus S^2=I, det S=-1, and

    S(I-dd^T)S = I-ab^T.

Only the selected class pair occurs in the changed response. The
restriction there is

    [-5, 2d_p d_t; 0, 1].

For size eight, let e equal d on the selected pair and zero elsewhere.
Set u=2e-d, v=-u/4. Then u^T u=8 and u^T d=-4. It follows that
S^2=I, S d=2e, and

    S(I-dd^T)S = I-4ee^T.

Each S-I is nonzero of rank one. The sixteen disjoint blocks therefore
give rank 16, and their determinants multiply to one. Similarity by H
gives the asserted rank and determinant of C=H^-1 S H. Exact
elimination on the independently constructed 112-by-112 matrices
confirms both statements.

## The active coordinate is a difference

The actual pair rotation is

    s=d_p x_p+d_t x_t,
    t=-d_p x_p+d_t x_t.

For size six, the transformed u is zero on the selected sum and every
other difference. On the selected negative difference and the two
other sums, the transformed rank-one update is

    u=(-2,-2,-2), v=(1/2,1/4,1/4).

For size eight, all differences are passive. A valid rescaled
rank-one representation on the four sums is

    u=(1,-1,-1,-1), v=(-1/2,1/2,1/2,1/2).

There are exactly 56 active fields, four in each global class.
The checker constructs P directly from the source signs and verifies
P S P^-1 against the literal reduced word. A control that removes
updates to a selected difference is rejected.

Every prefix of H and P preserves phase classes: each ADD has its
source and target in one class. Every prefix of the reduced word
reads and changes active fields only. These are literal gate checks,
not only matrix endpoint checks.

## Full scalar word and grid

For a reduced update I+uv^T with v^T u=-2, choose the first active
coordinate p. The shear R given by
x_i -= (u_i/u_p)x_p sends u to u_p e_p. Therefore

    R(I+uv^T)R^-1 = I+u_p e_p v^T R^-1.

Its only changed row is p. Its diagonal entry is -1; its remaining
entries in that row are u_p v_i. This proves the stated in-place
sequence R, the row update, and R^-1. It uses no extra field.

The checker verifies the complete chronological factor order

    H, P, S_reduced, P^-1, H^-1.

It also verifies the literal reverse word. The costs are:

| Component | Old real scalar primitives |
| --- | ---: |
| H or H^-1 | 470 |
| P or P^-1 | 1016 |
| Six-mode reduced block | 54 |
| Eight-mode reduced block | 80 |
| Sixteen reduced blocks | 1072 |
| Complete C or literal inverse | 4044 |

The price is derived from each emitted coefficient with the stated
binary ADD tariff. Every scale is a signed power of two. No fixed
odd multiplication, odd division, CLEAR, owned field, or native child
occurs in the scalar word.

The sparse-row replay starts with 640 independent field variables.
It verifies the complete C map on the first 112 and identity on the
other 528. Both inverse orders are identity on all 640. It computes
the exact maximum prefix row one-norm 10 and maximum binary
denominator height three in both directions.

Thus arbitrary inputs on a common dyadic grid need at most three
additional binary denominator levels for this scalar word. This is
not a bound on recursive child interiors or on the complete physical
phase implementation.

## The response is class-supported, not a diagonal unit

The checker verifies K=C E C entry by entry and checks every nonzero
entry against the global phase classes. K has nonzero off-diagonal
entries and is not symmetric. Its determinant is 35^8. The exact
inverse has denominator LCM 35, with both inverse products checked.
The factors five and seven therefore remain.

Encoding both banks by the same C changes the forward scalar shear
to Y+=KX. Since the actual source E is symmetric, the backward shear
becomes X-=KY. It is not X-=K^T Y. The checker records an explicit
entry that distinguishes K from K^T.

The two literal additive words each have 168 ADD events and cost
1544 primitives. Both act correctly on all 640 independent variables;
the 416 fields outside the two data banks remain unchanged. This
does not give an in-place dyadic implementation of K^-1. Their exact
prefix row one-norm is ten, and their binary denominator height is
zero. No odd-grid service is needed for these additive words.

## Carried-frame scope and the rank-four requirement

The actual W_R has binary Fourier rank four. For each port choose the
least actual label in its q+R class as anchor. The checker verifies
all 112 ratios

    W_R C_q C_anchor^-1 W_R^-1

have Fourier rank zero. Each conjugated anchor has rank one.
These checks bind the abstract phase-class premises to the actual
labels and W_R circuit. They do not emit full monomial records or
rank-one native wrappers.

Put Q'=W_R Q W_R^-1 and write Q'=A D, with D constant within each
class. Set T=P H. The exact ordered factorization is

    Q' C Q'^-1
      = A T^-1 (D_active S_reduced D_active^-1 direct-sum I) T A^-1.

It has 56 inverse and 56 forward anchor occurrences. Thus 112 H1 is
the conditional count in this carried frame. It retains 4044 scalar
primitives, at most 224 alignment maps, and up to 224 native side
maps. Preparing W_R, removing it, and lowering all maps are additional
obligations.

The binary checks suffice for Fourier rank and monomial support.
The ordered identity itself preserves all phases and is valid at
every tensor width. A full native implementation still needs the
actual phase records, legal access, and the inherited compiler and
recursive contracts.

The actual directional phases commute, and this remains true after
conjugation by W_R. Negative conjugation therefore uses inverse
alignments and anchors. For a transported inverse, the exact identity
is

    Q' C^-1 Q' = (Q' C^-1 Q'^-1) Q'^2.

The rightmost Q'^2 is a conjugated Pauli translation and is monomial.
It must be retained, either as a separate map or as the explicit
right factor in the first alignment. It is not a free cancellation.

The exact W45 is S_e0 C_45 S_e0. It has rank one. In this frame all
56 pair ratios have rank two. Therefore the current W45 exit does
not meet the monomial alignment premise.

There is also a lower bound on a common replacement gauge. For a
ratio C_a C_b^-1, the binary action is (x,z) -> (x+Tz,z), where
T=aa^T+bb^T. If one Clifford W makes every ratio monomial, let
L=W^-1 Z and U=L intersect X. The z-projection of L equals
U-perpendicular. Invariance implies Tz in U, so

    0=z^T Tz=(a+b) dot z.

Every edge difference a+b lies in U. The Fourier rank of W is at
least dim U, since L intersect X and L intersect Z are disjoint.
For each actual orthonormal eight-clique, the four disjoint
pair differences are independent. Across all pairs their span
has rank four. Hence any one common Clifford that makes these
pair ratios monomial needs rank at least four. The emitted W_R
attains that rank.

This bound concerns one common cover gauge. It is not a lower bound
for an arbitrary joint decoder, a circuit with cross-field mixtures,
or a changed productive construction.

## Prefix norm under the conditional phase factorization

There is a useful extension of the scalar bound. It requires the
literal prefix conditions verified above: every prefix of T and
T^-1 preserves classes, and every prefix of S_reduced reads and
changes active fields only. Endpoint support alone is insufficient.

Use the maximum of the field L2 norms. Write A_i for the input
alignment of field i and D_g for its class anchor. After T and the
inverse anchors, each active row has its scalar prefix coefficients
followed by the fixed input factor D_g(i)^-1 A_i^-1. Thus scalar
cancellations for each input field remain exact during the reduced
core. Passive rows are not read.

After the forward anchors, every row, including each passive row,
has the form

    sum_i l_(r,i) D_g(r) D_g(i)^-1 A_i^-1 x_i,

where l is the corresponding scalar-prefix matrix. A passive row
has input and output in the same class, so its two D factors cancel.
Each subsequent gate of T^-1 mixes only rows in one class. It
therefore preserves this form and its scalar cancellations. Partial
alignment and anchor passes apply a unitary to one whole field and
do not increase its L2 norm.

Consequently, the norm at completed-child boundaries is at most the
corresponding scalar row one-norm, hence at most ten times the
maximum input field norm. Recursive child interiors are excluded.
The scalar binary-height-three bound does not transfer to this
physical word without a separate phase-grid account.

The producing agent independently checked this norm argument and
specified the necessary word-prefix hypotheses. This is a peer
check of the extension, not a second native implementation review.

## Verification and limits

Run one process with
`python3 -I -B check_review.py`, then repeat with `-O`. The two
receipts must be byte-identical. Expected output starts with
`PASS_INDEPENDENT_DYADIC_PHASE_CLASS_CAPTURE`.

No material error was found in the frozen packet. The construction
provides a dyadic scalar capture and an exact conditional phase
factorization. Native phase recipes, rank-four frame preparation,
routed stage matching, helper progress, terminal output, finite map
prices, and the complete recursive invoice remain open.

The independent-review lane supplied the asymmetric six-mode
involution. The coordinator supplied the phase-class reduction.
The low-displacement, pair-code, and common-gauge packets supply
the actual response and geometry. This review used AI assistance
and is not an independent human review.

No PR, commit, push, or publication is authorized. Before any future
PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
