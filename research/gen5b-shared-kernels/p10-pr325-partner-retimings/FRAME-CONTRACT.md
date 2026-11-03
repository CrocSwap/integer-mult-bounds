# Exact array-frame contract for the new PR325 retimings

## Pinned theorem and the two operator spaces

The source is PR325 head `0eca9340a3df6141b8e71a41638c3937b3522888`.
Its `proof/primary/03-motifs.tex`, SHA-256
`ed76761194988a01af77ead0ea6469cb5dcd29690ab985a0b5a4006b0f2b69bb`,
states the common-frame representation principle in lines 146–185.
The source `proof/PARITY-CONTRACT.md`, SHA-256
`a9246be656e31f1a21d5ec714e002f51be0aa07c36e1528066a25b2c7a02db91`,
explicitly instantiates that principle for binary payload arrays and rational
address geometry. Both files were fetched as inert text at that head and checked
against its immutable manifest. The original source's attribution is retained.

There are two distinct spaces. A rational partial-swap matrix acts on address
coordinates, including both head and tail coordinates. The induced frame is a
permutation of entries of a complete role array. The array entries are F2 payload
values. An ADD is pointwise XOR between complete role arrays at matching addresses.
It is not an arithmetic shear of one head coordinate in the rational address
matrix. No claim that a head-only arithmetic shear commutes with a partial swap
is used here; that claim would in general be false.

## Universal lifting identity

Fix any finite complete address set Omega on which the selected address maps are
invertible and preserve the required spectators. Let V be F2^Omega. For every
vertex v choose an invertible F2-linear array frame Phi_v. All operand incidences
of a pointwise gate share that same frame. An edge u→v applies Phi_v Phi_u^-1.

For a gate matrix A on k role values, its action on role arrays is A tensor I_V.
The common frame on its operands is I_k tensor Phi_v. The two operators commute:
(A tensor I_V)(I_k tensor Phi_v) = A tensor Phi_v
= (I_k tensor Phi_v)(A tensor I_V).
This is an exact identity over F2, with no restriction on the role arrays.
Induction over edges and gates therefore gives

    physical local operator = Phi_out S_Omega Phi_in^-1.

The source interpretation is Phi_in^-1 of the supplied physical input. It is a
definition, not a physical normalization or an initialization assumption.
Consequently two legal frame assignments with the same logical scalar operator
and the same source/sink frames give exactly the same physical array operator.
This includes arbitrary, independently supplied and correlated dirty helper
arrays. No finite-field sample is being used to infer this identity.

The 480 modifications change only the common frame of a partner setup gate from
its actual rank-two source frame to its actual rank-18 delivery frame. The
independent event reconstruction verifies that every opcode, operand, signed
coefficient, order and COPY episode is otherwise unchanged. The independently
replayed F2 operator is the required target shear on all 10020 formal columns.
The full local audit must bind every ADD to equal current operand frames, every
edge to its actual frame endpoints, and all input/output frames to the new word.
With those premises, the displayed identity proves equality of the old and new
complete local array operators. It does not require moving an unframed head shear
through a rational coordinate-swap matrix.

## Exact edge realization

For a fixed nondegenerate form G and nested nondegenerate subspaces U⊆W, the
orthogonal projectors obey P_U P_W = P_W P_U = P_U. Therefore P_W−P_U is an
idempotent of rank dim(W)−dim(U). For

    D_P = [[I−P, P C], [C P, I−C P C]],

direct block multiplication gives D_P²=I and
D_(P_W−P_U)=D_(P_W)D_(P_U). More generally D_A D_B=D_(A+B) when AB=BA=0.
These are rational polynomial identities and remain valid in every retained
coefficient ring where the frame data are defined and have the stated ranks.
They extend to consecutive atom blocks and common invertible weighted charts by
tensoring and conjugation. Every checked nested chain consequently has the
exact endpoint product D_final D_initial^-1, on every address coordinate and
therefore every array entry. The audit separately checks all 960 changed source
chains by explicit exact 40-column matrices.

For a reflected chain the projectors are I−P in reverse order. Its positive edge
is (I−P_U)−(I−P_W)=P_W−P_U, with the same rank. Added common stage backgrounds
cancel in this difference. The global compiler must bind its actual reverse
records to this orientation; a rank tally alone is insufficient.

## COPY is a separate, explicit interface

The pinned `proof/copied-centers-lemma.tex`, SHA-256
`d0ce6d3d504996aadb098227885224e48df46101daec8893523a0a8b7364d8fe`,
states the complete-stream copy/transform/read/discard contract. Copy the original
role array including controls and spectators, transform the copy by the exact
frame quotient, perform only read-controlled target updates, and erase the copy.
The original stays unchanged during those reads. This is a charged temporary
stream, not a presumed zero-valued independent helper.

In the forward local word, transforming the rank-18 copy to ZERO is the positive
involution D_(P_center), even though the frame difference written new-minus-old
would be negative. A reflected episode copies the original afresh at the
complementary frame, transforms that copy to the full frame, reads and discards
it. It never inverts an erasure. The local audit binds all 20 complete episodes,
144 reads each, and their barriers. The global audit must retain all 100 positive
copy transforms and use these fresh reflected episodes.

## Finite boundary

This argument closes the new arbitrary-dirty retiming implication once its
explicit finite frame/event/COPY premises are checked. All rank-18 delivery
frames already occur in the pinned PR325 word; the retiming introduces no new
frame basis. Generic primitive implementation, uniform eligible-prime coverage,
weighted compiler/routing, restored rows, ordinary leaves, complex/full-C and
analytic all-size interfaces remain separately named inherited hypotheses.
The argument neither proves an unconditional all-size theorem nor authorizes a
numerical publication before the full global packing, bill and exact price pass.
