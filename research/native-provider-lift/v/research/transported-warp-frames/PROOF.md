# A sufficient construction for transported warp frames

All spaces below are over F₂. A frame is a subspace of V = F₂^h. A scalar operation touching several registers requires one common frame containing each current frame. Enlarging U to W costs one H_(dim W − dim U) when the difference is positive. Native warps have fixed invertible binary maps G and fixed free-operator identities K_G. Frame changes do not change G or K_G.

## The transported-frame lemma

Define the maximal isotropic subspace

`L_U = {(x, x + p) : x ∈ U, p ∈ U⊥}`

of the binary Pauli space V × V, with symplectic form x·z′ + z·x′. It has dimension h: the displayed parametrization is injective, its domain has dimension dim U + dim U⊥ = h, and isotropy follows because each cross term is x·p′ + p·x′ = 0.

For invertible G define the native symplectic action

`S_G(x,z) = (Gx, Gx + G^(-T)(x+z))`.

For every U, **S_G(L_U) = L_(GU)**. Indeed substituting z = x+p gives `(Gx, Gx+G^(-T)p)`, and G^(-T)(U⊥) = (GU)⊥. The latter equality follows from `(Gx)·(G^(-T)p) = x·p`; dimensions give equality rather than inclusion. This also proves the inverse statement with G^(-1).

Let T_U be any exact Clifford frame lift taking L_U to the computational Z subspace, with the same convention on both sides. If an exact Clifford K_G has action S_G, then

`T_(GU) K_G T_U^(-1)`

is monomial: its conjugation preserves the computational Z Pauli subgroup up to signs. The joint eigenspaces of the h independent Z generators are precisely the one-dimensional computational basis lines. Conjugation therefore permutes those lines. Unitarity makes the surviving coefficient on each line have modulus one. Thus its Fourier rank is zero for **every** U, not only the original U. This statement includes any global phase: multiplying K_G or either lift by a unit scalar preserves monomiality.

This proves rank-zero realizability, not a specific phase table or a particular native gate invoice. A symplectic tableau alone does not determine global phase. Those claims require the exact phase recipes and physical gate expansion. The concrete word below passes those extra gates through the unchanged attributed native replayer, including its independent Gaussian all-column checker. No generic exact-phase identity is inferred solely from this lemma.

## Word construction theorem

Fix a finite legal BORROW-WORD with invertible native maps. Keep its registers, source/target/centre/terminal interfaces, scalar opcodes and coefficients, prelude warp operators and order, B native warp order and maps, and all wrapper contracts. Choose new common frames for scalar gates and new entrance/exit frames U_k′, E_k′ for B warps. Assume:

1. Every chosen scalar frame contains the current frames of all its operands; centre descents, target cut levels and end interfaces remain legal.
2. Immediately before each B warp the lender's current frame F_k is contained in U_k′, and E_k′ = G_k U_k′.
3. The prelude's original exact frame requirements remain legal, including inverse warps. Cleanup is recomputed from the unchanged free operators.
4. The native implementation uses exact lifts and phase recipes for the new frames; any claimed physical cost beyond the rank histogram is checked separately.

Then the following algorithm yields a legal framed implementation of the same full linear operator: apply the chosen scalar frame edits, insert the scalar identity on each lender in frame U_k′ whenever F_k ≠ U_k′, apply the unchanged K_(G_k), and continue in frame E_k′. Charge the climb before the warp by H_(dim U_k′ − dim F_k); charge every other scalar climb, centre descent and terminal climb exactly as the ordinary walker does. Preserve the original operator numbers even when B positions shift.

**Proof.** Induct in execution order. A scalar step is legal by condition 1 and uses the same scalar operator. An inserted identity is exactly the identity on the register's underlying values and is legal by F_k ⊆ U_k′; the climb is explicitly charged. The transported-frame lemma makes the following native warp legal at rank zero and gives the required exit frame. Its underlying operator remains K_(G_k), not a conjugated or renamed operator. This proves the induction through B and restore. Centre and terminal interfaces are legal by condition 1. Deleting the inserted identities leaves the original opcode sequence, hence exactly the same ordered product of linear operators, including the arbitrary dirty inputs. Recomputing cleanup from that product preserves its intended correction. Each charge is literally the positive dimension change at its event, which proves the histogram invoice. Condition 4 supplies any stronger phase or physical admission claim; it is not assigned zero cost. ∎

The theorem is sufficient and constructive. It does not require a favorable histogram, a specific search method, clean helper inputs or a guessed owner schedule. Conversely it does not assert that a valid local word supplies a complete recursive owner/outer construction.

## Concrete application

The frozen recipe changes one of 72 B warp records: zero-based warp 0 on register 243, with entrance dimension 4 becoming 5 and exit its exact G image. It changes 36 scalar frames and emits one identity scale at B position 916. The compiler output equals every field of the frozen native-audited word, not merely its profile. The independent point-set walker checks containment, binary maps and lifted Lagrangian action. Independent free noncommutative forward/dual and reverse-boundary checks retain all symbolic dirty inputs. The full native driver additionally reconstructs exact warp recipes and global phases.

The resulting profile is 2468 H1 + 709 H2 + 220 H3 + 106 H4 + 20 H5 + 8 H8. Compared with the original, the rank-mass change is 28 − 32 − 12 + 16 = 0. The helper inventory remains 26 of width 4, 2 of width 5, 18 of width 6, 53 of width 7, 96 of width 8 and 213 of width 9. This is an actual nontrivial positive instance of the theorem. Its price is worse near the current endpoint; there is no new κ claim.

The reusable contribution is the explicit compatible-transport construction and its checked compiler. The shared DAG's fixed-boundary character cuts are a predecessor, not a new discovery here. Optimizing the enlarged domain and realizing a profitable complete supplier remain separate research tasks.
