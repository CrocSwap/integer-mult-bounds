# Physical monomial codes and the retained line flags

This note separates two statements. A physical monomial output code can
be carried through a complete native program by a change of coordinates.
The current independent-path transfer does not meet the required local
boundary condition. Its FULL code is monomial, but its hole code is not.

No owner schedule or complete supplier price is claimed here. The paid
terminal for a common response is in the separate
`../common-monomial-terminal-20261018/` packet.

## A whole-program coordinate change

Let G_j be one operation of an admitted physical program. Include all
productive fields, arbitrary helper fields, and owned fields in its
state. Suppose a replacement word W_j has the exact physical map

    W_j = H_j G_j,

where H_j is a known monomial operator on this complete state. It must
preserve the owned-zero subspace. Put C_0=I. Execute

    C_j W_j C_j^-1,
    C_(j+1)=C_j H_j.                              (1)

If the state before this operation is C_j z, its state afterward is
C_j H_j G_j z. This proves (1) by induction. For an unchanged operation,
use H_j=I. At the end apply C_final^-1. The result is the original raw
physical endpoint. No residual code reaches an unchanged outer twiddle
or product.

The order C_j H_j is required. Replacing it by H_j C_j is incorrect in
general. Also, every later use of a renamed live field must be changed.
This includes a productive data field that later serves as a helper.
Changing only the local data names is not sufficient.

For a structured monomial that permutes fields and cover rows and applies
one affine quadratic-phase map to each payload column, the following
conjugation rules are finite:

- An ADD uses the renamed fields and the composed monomial read map.
- A COPY or CLEAR uses the renamed field. A monomial sends zero to zero.
- A one-field Clifford child has the same Fourier rank under left and
  right monomial maps. Its address wrappers change.
- Every arbitrary helper boundary equation is conjugated with the same
  complete-state code.

These rules preserve a child profile only when the admitted array-map
grammar contains all the composed maps and when the field, cover, and
payload factorization is retained. They do not authorize an arbitrary
permutation that mixes payload columns or owned fields with live fields.
The scalar work, view descriptors, temporary stock, precision, and owner
schedule still need a finite invoice and a source certificate.

## A sufficient reciprocal-response condition

For logical reciprocal shears, put D(E)=diag(I,E). Then

    F_E D(E)=D(E) F_I,
    B_(E^-1) D(E)=D(E) B_I.                      (2)

Thus a pre-Y E code converts either call to an ideal call followed by a
Y code. In physical frames Phi_in and Phi_out, the precode and output
code are

    P=Phi_in D(E) Phi_in^-1,
    H=Phi_out D(E) Phi_out^-1.                  (3)

If both (3) are admitted physical monomials, equations (1) and (2) give
a complete program compiler. Logical monomiality of E alone does not
imply either condition in (3).

In the original local frames, X enters as Qx and Y enters as y. They
exit as F x and F q y, where q=Q^-1. The Y output code has blocks

    F q_t E_ts Q_s F^-1.                        (4)

The current transfer packet proves that E and F E F^-1 are monomial.
It does not prove that (4) is monomial.

## An exact line-flag test

Use the binary symplectic matrix of a Clifford operator. A monomial has
zero upper-right block. Its left or right multiplication preserves the
rank of that block. Let a and b be odd binary vectors, so a^T a=b^T b=1.
Set P_a=a a^T and P_b=b b^T. Let G be invertible.

Use the common phase change that converts K_G to the address permutation
P_G, F_n to the full Walsh operator H_n, and C_a to H_a at the binary
symplectic level. If b^T G a=0, the upper-right block of

    F_n C_b^-1 K_G C_a^-1

is

    (I+P_b) G^-T (I+P_a).                      (5)

Its rank is n-2. Indeed, I+P_a has an (n-1)-dimensional image a^perp.
G^-T a^perp contains b exactly because b^T G a=0. The last projection
therefore removes one further dimension.

After right multiplication by F_n^-1, the upper-right block becomes
the former upper-left block:

    P_b G(I+P_a)+(I+P_b)G^-T P_a.              (6)

It has rank two. Its two nonzero summands have independent image lines,
one in span(b) and one in b^perp. Their source rows are also independent.
The general zero-rank condition for (6) is G^T b=a.

For an empty-warp transfer, the source cut space U contains a, the target
cut space V is a subspace of b^perp, and G maps U to V. Hence b^T G a=0.
This proves the rank test for every K_G transfer with these three flag
conditions. It is not limited to one basis extension or one matching.

## Actual packet checks

The pinned independent-path packet has 112 matched transfers, for each
of two providers. The port permutation has 106 fixed points and three
two-cycles. Every matched source frame contains its intrinsic q_s. Every
matched target frame is orthogonal to its intrinsic q_t.

For all 112 blocks of each provider, the exact signed Clifford table gives

    rank(F9 q_t E_ts q_s)=7,
    rank(F9 q_t E_ts Q_s F9^-1)=2.

The original identity-response forward call has diagonal block rank
eight and cross-block rank nine. The changed forward call has diagonal
block rank eight and cross-block rank seven. The source input with two
nonzero output blocks and the target output with two nonzero input blocks
identify this cross block. Therefore independent physical monomial field
permutations and address maps at the two boundaries cannot turn this
single call into the original forward call.

The separate `screen_warped_matching.py` also permits all actual signed
prefix warp histories, using the fixed canonical intertwiner
K_V K_U^-1 at each cut. It checks 21,906 distinct cut/frame/prefix cases
per provider. The resulting 12,311 port edges contain no edge that meets
G_E^T q_t=q_s. This finite screen does not exclude other stabilizer choices
at nonempty-warp cuts.

These statements do not rule out a changed multi-transfer response, a
multi-call compiler, a paid terminal, or a common response built on the
whole 73-axis flag. They reject a free call-by-call use of (2) for the
present local matching.

## Verification

Run both scripts in this folder with one process at a time. The rank
checker reads the pinned recipes, checks their signed Clifford products,
and checks the binary formula on every invertible three-bit matrix and
all odd input/output vectors. The matching screen reads the full native
event order. It does not import the producer.

No PR, commit, push, or publication is part of this packet. Before any
future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
