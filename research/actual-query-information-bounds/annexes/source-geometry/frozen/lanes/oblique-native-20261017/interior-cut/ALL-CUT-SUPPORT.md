# Scalar support at every retained native cut

This note fixes the source computation, all native frame paths, and the
Y-to-Y scalar subword of the pinned clean forward word. It permits any
number of new X/helper-to-Y scalar ADDs at equal-frame cuts. It also
permits deletion or coefficient changes at the existing ADD sites of
that type. An arbitrary raw I-helper correction at entry is allowed.
The scalar coefficients can be rational.

The note does not permit changes to the source computation, new native
children, operator-valued ADD coefficients, or new Y-to-Y gates. The
operator model keeps the existing warp symbols as free words and cancels
adjacent inverse symbols. A physical relation between distinct warp words
is not used. A stronger physical-character result requires a separate
proof.

## Exact cut inventory

The forward word has no Y-to-X or Y-to-helper ADD. Thus a new one-way ADD
does not change any later source row. Its final Y response is the outer
product of its current source row and the remaining Y scalar column.
This statement also holds for a sum of new ADDs.

The inventory checks every cut where a source row, source frame, target
frame, or remaining Y scalar column changes. Between these events, the
possible outer products do not change. It visits 267,854 equal-frame
source/target pairs and records 4,276 distinct products. There are 2,594
source rows and 300 remaining Y columns in the retained pools. Each
product has a concrete event index, source field, target Y field, and
frame witness.

The source pool contains all 112 productive X fields and all 408 live
helpers. A private Z field always has the FULL frame. No Y field reaches
FULL, so a Z-to-Y ADD cannot pass the equal-frame check. The only used
owned C source contains raw I-helper terms and is cleared in the source
word. These terms are included in the allowed entry correction and do
not affect the quotient response. The other owned fields do not carry X
information.

Two products with the same source row modulo raw I-helper terms and the
same remaining Y column are equivalent for this test. The inventory
retains one complete source row and one legal cut for each such product.
A successful construction must still price its entry correction.

## Support invariant

Let p_s be the actual binary label of input X_s. Let F be a recorded
transfer frame. For each empty-warp-word X_s term at that cut, the checker
verifies p_s is in F. For every final Y_t row reached by the remaining Y
column, the checker verifies F is a subspace of p_t-perp. Hence

    p_s dot p_t = 0.

All 7,584 raw scalar source/target products pass these checks. Their union
has 5,824 distinct port pairs. Since each actual port has odd weight,
the diagonal pair s=t is forbidden. Any scalar response obtained in this
fixed free-word model has zero entries at each pair with p_s dot p_t=1.
Cancellation of nonempty words cannot change this empty-word support.

This proves that a scalar retuning cannot change the ordinary response
to the identity, or to the identity plus a correction supported on only
eight target rows. It does not preclude a different dyadic unit response.
The separate UNIT-RESPONSE.md packet constructs such a response.

## Full centre-matrix restriction

Use the actual eight-row matrix R and K=R^T/4. Let A be any constant
8-by-8 rational matrix. To cancel the off-diagonal part of K A R by the
allowed scalar transfers, it is necessary that

    R_t^T A R_s = 0

at every distinct pair with p_s dot p_t=1. There are 6,608 such equations.
Exact rational elimination gives rank 63 on the 64 entries of A. The
one-dimensional kernel is the scalar multiples of I_8.

Therefore seven retained centre directions cannot be made into a
nonzero diagonal response by scalar changes in this cut model. The same
restriction applies to a rank-seven constant mixer of all eight centre
directions. A rank-seven matrix is not a nonzero scalar multiple of I_8.
This is a statement about this explicit construction family, not about
all native encodings or all actual operator-valued circuits.

## Checks and source pins

The source core has decompressed SHA256
 a6c5dc63a47c1fdb0a97314a3b8541035f507beccb1029762f703039465187fa.
The all-cut inventory has decompressed SHA256
 18c89367243fc7c09411f28a8022884130373ce4886de806f4b011edec030418.

Run from this directory:

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 inventory_new_edges.py
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 check_frame_support.py

The second command must report
PASS_EXACT_FRAME_SUPPORT_AND_CENTRE_RIGIDITY. It uses exact fractions for
the rank-63 centre calculation. No sampled rank or numerical tolerance
is used. The file ALL-CUT-SUPPORT-FREEZE.json pins this proof, both checks,
the receipts, the cut payload, and the local replay dependency.

The fixed-site and all-cut modular span checks in the coherent-port lane
provide separate evidence. They are not needed for the exact support and
rank argument above. The existing E8 and port-frame geometry is prior
repository work; this note binds the invariant to the current native
schedule and the stated insertion grammar. AI assistance was used.
