# Whole-payload dimension of owner-local repairs

This is a conditional linear-information theorem for the exact selected
replica-0 calls 0 (forward, stage 0) and 4 (backward, stage 1). It extends the
constant-payload scalar theorem in retained PR2461. All initial target/helper
differences are zero; their common baseline contents can be arbitrary dirt.
The demanded output is the entire later eight-query field, immediately before
its eight transports. Preserving only a final completed endpoint is a different
contract.

## 1. Payload and observation contract

Let G be the selected finite orthogonal cover group, with owners labelled by
group elements, not by payload addresses. Let M be the same finite-dimensional
complex payload space at every port and owner, with dimension d > 0. Physical
payload fields on all 73 axes (and any finite spectator factor) are an intended
application. A local nine-axis factor has dimension 512; 512 is not the
dimension of the entire 73-axis physical payload.

For each g in G, the 112 arbitrary source differences form x(g) in M^112.
Different g and different ports are independent. The admitted local-view
contract supplies invertible row-wise coordinate identifications on M,
including entry translations, common exterior factors and spectator
identifications. In those coordinates, the local native word is the checked
nine-axis word tensored with identity on spectators. Multi-register operations
use the same common coordinate space. These are full-space identifications,
not merely embeddings of constant exterior factors. The finite local checks
below establish the local word part. The global view/compiler contract is an
explicit inherited hypothesis, not independently rebuilt here.

At old owner g, retain the first eight centre arrays z(g), with their known
invertible output carrier conventions removed. A permitted additional
observation e(g) = E_g x(g) is linear and depends only on this old owner's
112 original source arrays. It can mix ports and payload coordinates; its
complex codomain dimension is m_g. Encoders can vary with g. The decoder may
use all z and e fields across all owners, and may even be nonlinear. It has no
other source-dependent input. The original calls and their chronology remain
fixed for the purpose of defining the required query field.

**Theorem.** Every such repair requires m_g >= 104d at every owner g.
Equality is attainable as an abstract linear-information interface. If each
additional record can hold at most d complex coordinates, at least 104 such
records per owner are necessary. No number of recursive children, transport
rank mass or primitive physical reads follows from this dimension statement.

## 2. Exact native factorization, in both orientations

Write T_f for the canonical invertible operator of frame f. The pinned
Clifford evaluator checks, including phase and on every one of 512 columns,
that every used child from a to b applies T_b T_a^-1. Both orientations together
use 2,896 distinct (a,b,rank) recipes. The extended-label audit tracks all 704
ordinary formal inputs through all 24,767 events in each orientation. Every
ADD combines equal canonical labels. It also checks the role, direction,
phase, frame and multiplicity of all conversions and the private COPY/CLEAR
boundaries. No ordinary field is cleared.

At a source entry with actual monomial A_p, use initial label
L_Dp = A_p^-1 T_start(p). At a target exit with monomial N_p, use final label
L_Tp = N_p^-1 T_final(p). For a helper wrapper with factors R,L and start/end
(a,b), use initial R T_a and final L^-1 T_b. The audit permits ADD only after
these conversion labels become canonical. All monomials are invertible; all
224 source/target adapter identities are checked, and all 36 distinct helper
wrapper records are checked for invertibility. Their residual coordinate
tariff identities are not needed or claimed.

The standard common-frame induction, credited to Stream.conj_matrix and
PR2048, therefore gives the complete local operator

    diag(L_final) (S tensor I_M) diag(L_initial^-1).

The fresh scalar audit finds the exact complete endpoints

    S_forward:  (D,T,h) -> (D,T+D,h),
    S_backward: (D,T,h) -> (D-T,T,h).

Consequently the first complete call's source-to-helper block is zero, and
its source-to-target block is diagonal by port with invertible blocks. A
helper's own dirt can undergo a nonidentity change: zero source response does
not assume that physical helper bits are restored.

For each actual port normal q, the local source label equals

    C_q = ((1+i) I + (1-i) X_q)/2.

Its inverse normalizes the old source. The target final label is F9 C_q^-1,
and the complete first D-to-T block is F9 C_q^-2 = F9 X_q. The checker verifies
these identities and both inverse orders for every one of the 112 ports,
including phase. Circuit arrays in the receipt are listed in execution order,
so [C_q^-1,C_q^-1,F9] denotes this last product. Tensoring and applying the
admitted row-wise identifications preserve invertibility.

The backward query must be audited separately: applying the forward proof
to a scalar D-only specialization would not exclude operator cancellation.
Immediately before the actual backward centre transports, the eight formal
rows have **only T coefficients**, with D and helper coefficients identically
zero on all 704 formal inputs. Their matrix is H = R/4, where R is the forward
eight-by-112 source block. Thus the earlier D endpoint cannot cancel the T
response in this later query. Each H column is nonzero.

## 3. Chronology and the full payload field

The retained exact route/schedule checker verifies that the first five
global events are the local call sweeps 0 through 4, and that calls 1-3 touch
none of call 0's 224 D/T families. Call 0 has zero source-to-helper response
at its complete endpoint. Linearity therefore leaves no source variation in
the intervening calls, even if they share helper families. Stage 0 has
identity data routes. In particular source differences at g cannot affect
the first transcript at another old owner.

Let A_gp: M -> M be the old physical-to-normalized source map. Let B_gp be
the first call's completed physical D-to-T block. Let V_dp identify that
physical target payload, at owner d rho_p, with the later normalized input
coordinates. Each is invertible on the same M by section 2 and the declared
full-space view contract. They need not agree with one another or commute.
After normalizing the output carriers, the two exact field equations are

    z_k(g) = sum_p R_kp A_gp x_p(g),
    y_k(d) = sum_p H_kp V_dp B_(d rho_p,p) x_p(d rho_p).

Thus W_dp = V_dp B_(d rho_p,p) is invertible. For a fixed input port p it is
the same operator in all eight output rows k: common-frame conjugation makes
the scalar coefficient H_kp multiply the entire normalized array. This is
the required block-operator factorization, stronger than equality on constant
payloads. The first formula has rank 8d because rank R = 8 and diag(A_gp) is
invertible. The receipt contains an eight-column minor with determinant 32.

The route checker constructs the actual 73-column rho_p matrices and verifies
their orthogonality, involutions, fixed port normals, chart swaps and both
stage-translation formulas. All 112 are distinct group elements. For fixed g,
right cancellation in G proves d_p = g rho_p^-1 are 112 distinct owners; this
is not an assumption that their action on a particular payload address is free.

## 4. Lower bound and sharp abstract repair

Fix g and vary only x(g). In the complete later field, input port p occurs
only at owner d_p. Its block map is

    u in M -> (H_0p W_(d_p,p) u, ..., H_7p W_(d_p,p) u) in M^8.

This map is injective because some H_kp is nonzero and W_(d_p,p) is invertible.
The 112 output-owner supports are disjoint, so their direct sum has rank 112d.
There is no possible cancellation between ports on this one-owner input
slice, even when their payload operators differ.

All old observations except z(g) vanish on the slice. If the stacked linear
map x(g) -> (z(g),e(g)) had a nonzero kernel vector, that vector and zero would
give the same entire available transcript but different required later
outputs. Even a nonlinear decoder could not distinguish them. Hence it must
be injective, and

    112d <= rank[z(g); E_g] <= 8d + m_g,

which proves m_g >= 104d.

For equality let J = (0,1,2,3,4,5,6,12), the checked pivot columns of R.
At every g observe the 104 complete normalized arrays A_gp x_p(g) for p not
in J. Subtract their contributions from z(g) and use (R[:,J]^-1 tensor I_M)
to recover the remaining eight arrays. Undo all A_gp and apply the displayed
later field formula. This observes exactly 104d coordinates. It grants the
abstract routing, inversion and aggregation free of charge and supplies no
physical implementation or invoice.

For d=512 the dimension numbers are 4,096 old, 57,344 required on the slice,
and 53,248 additional. This is an illustrative common-payload instance of the
theorem; interpreting one 512-vector as the whole 73-axis physical field would
be incorrect. For the full finite physical payload, use its full dimension d.

## 5. Checks that distinguish the missing implication

The local all-column identities plus both complete extended-label audits
justify arbitrary payloads in the local word. A separate exact two-coordinate
instance uses distinct port-dependent rotations/sign maps: old rank 16,
required rank 224, repaired rank 224, and rank 223 after omitting one additional
coordinate. This finite instance tests the proof bookkeeping; it does not
substitute for the all-d argument.

The averaging map [[1/2,1/2],[1/2,1/2]] fixes constants but kills (1,-1).
The inverse check rejects it. Thus the constant endpoint facts in PR2461
alone cannot justify this lift. Other controls corrupt the backward common
frame, reverse its centre direction, remove a forward transport, change a
native global phase, omit one repair coordinate, and collapse owner routes.
For the last, when all routes and port maps coincide the positive boundary
case y=z/4 needs zero repair; distinct-owner support is essential.

No full physical compiler, global supplier cold replay, all-size recursion,
native repair implementation, restoration/tape bill, precision proof or new
exponent is established. Nonlinear encoders, mixed-owner observations,
additional source-dependent state, sequential rereads and final-output-only
contracts are outside this theorem. Lean source is pinned and read, not run.
