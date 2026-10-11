# Heterogeneous helper endpoints by dirty preconditioning

This is a constructive finite compiler route. The two sink rows and the complete 1,023-column rational scalar program have been checked on the frozen 18-prefix certificate. Physical Clifford endpoints, both chronological orientations, heterogeneous banks and the changed global invoice require their separate checks; scalar evidence alone does not certify the multiplication theorem.

Frozen main source: structural-local-prefix18.json, SHA256 ba159f566568627d8459960500b9c285e9c9d69368f1b60fa27ae83f0a84c39a. Main selections: structural-sink-prefix18-audit.json. Literal pre/post witness: structural-prewhite-prefix18.json, SHA256 be5fa48b48491d7b3587e3df22f7d7f8f767dcb48817c4f49f4be87c7cc87519.

## Sufficient block compiler

Let a fixed finite scalar main word over Q act on sources x, helpers h and targets y by

    x' = x,
    h' = N x + A h,
    y' = y + M x + B h.

The hypotheses are checked properties of the fixed word: no helper/target feeds a source, no target feeds a helper, the final source block and target-to-target block are identities, and A is the product of the literal helper-to-helper elementary shears. The eight retained-centre contributions are included in M and B. Intermediate target-to-target shears are allowed: only their complete final target block must equal the identity.

For selected sinks require the corresponding complete clean-source row N_r to be exactly zero after the inserted uncompute. This is an exact equality of all 120 rational source columns. No assumed recovery matrix is used.

Execute these gates in this order:

1. At the common initial ZERO frame, y -= (B A^-1) h, using the explicit nonzero rational entries of the computed matrix.
2. At the same ZERO frame, h <- A^-1 h. The witness is the literal reverse helper-to-helper subword of the modified main, negating each coefficient. Source-to-helper gates are omitted from this inverse because they do not belong to A.
3. Execute the modified main, including the two same-frame uncomputes and every paid donor advancement. Its values become x, N x+h, y+M x.
4. At FULL, for every nonsunk helper, subtract the explicit row N_r x using source registers that are already at FULL. Each sink has N_r=0, so it needs no FULL repair or final lift.

The final scalar operator is (x,h,y)->(x,h,y+Mx). Initial helpers may be arbitrary and correlated. The preconditioner changes initial dirt before the address walk; it does not assume helpers start clean. The target correction must precede helper preconditioning, because its stored matrix multiplies the original input helper vector.

The exact fixed program has 1,550 pre-helper shears, 1,660 pre-target shears and 7,800 post-helper shears. No source inverse is required. Coefficients use numerators with at most two bits and denominators with at most three bits; the serialized denominator set must be read from the witness (it includes 4). Repeated halving and division by three, with a cleared coefficient scratch stream, realize every coefficient. The structural pre/post estimate was 61,161; it is not the admitted invoice. The final literal coefficient compiler charges 165,748 real-component primitives for the complete local orientation, as detailed in complex-hetero-note.md. These operations are finite work and are charged; no recursive address child is hidden in the scalar matrix calculation.

## Two exact local sink equations and address bill

Sink 355 ends at frame 206, rank eight, the cap perpendicular to port q=508. At its actual final main-use cut, perform

    h355 -= h356; h355 += h556/2; h355 += h619.

Sink 403 ends at frame 221, rank eight, the cap perpendicular to port q=499. At its actual final main-use cut, perform

    h403 -= h409; h403 += h577/2; h403 += h628.

The actual cut indices are remapped from the frozen certificate's last-use groups, rather than reused from the older source. Before either uncompute every donor is genuinely advanced to the sink frame when needed; all later paths remain nested. The complete changed walk has local histogram delta H1:+2,H3:+4,H4:-4 and rank-mass delta -2. This invoice includes donor advances and removal of the two terminal rank-one lifts. The two equations together pass rational replay, rather than adding independent gains.

## Literal heterogeneous banks and recurrence

Use T=32 replicas. At each of nine stages there are 64 rank-eight residuals and 24,992 rank-nine residuals. Eight banks contain one rank-nine and eight rank-eight blocks, filling width 73. The remaining 24,984 rank-nine residuals occupy 3,123 banks containing eight rank-nine blocks and one paid rank-one padding child. Thus each stage uses 3,131 banks, compared with 3,132 in the uniformly full-endpoint source. All residual blocks have disjoint coordinate images; there is no shared-axis overlap or assumed free padding.

Compared with the same source replicated four times (T=32), live stock changes by -9 and the complete nine-stage profile changes by

    H1:+495, H3:+1152, H4:-1152.

Its rank-mass change is -657=73*(-9), so the deficit is preserved. Per-cover live stock is 58,899. This profile has been priced as a nomination; final admission also needs the exact rank-eight endpoint adapters, cover-owner injections, padding, all-live cover correction, changed private work, scalar primitives and row/precision/router bounds.

## Dual orientation

For an invertible fully lowered forward operator F, define the backward operator by F^(-*), then exchange source and target roles. A rational elementary ADD t += a*s becomes s -= a*t; its program position is preserved, because inversion and adjunction each reverse product order. A unitary Clifford/address factor has U^(-*)=U, so its recursive rank is unchanged. The forward scalar block is a target shear M with independent helper endpoints; its inverse adjoint is a source shear -M^T and has the same independent helper endpoint operators. Thus the same heterogeneous residual ranks are mathematically sufficient for both orientations.

This construction supplies a literal dual of every pre/main/post scalar ADD. An implementation must re-lower the dual coefficient macros with fresh cleared scratch and check the changed source/target endpoint adapters and actual chronological labels. COPY/clear macros should not be mechanically transposed as unrelated noninvertible maps: first use their proven complete ADD/centre macro, then lower its inverse adjoint. The physical dual check is a separate required receipt, not inferred from the forward scalar check.

## Controls and provenance

structural-prewhite.cpp computes and exports the explicit matrices, checks all helper dirty columns, verifies the complete source identity and original clean target matrix, and checks zero sink clean rows. Its matrix calculations use exact rational arithmetic with overflow checks. The separate sink audit computes every actual changed frame transition and rejects false rational uncomputes. The underlying local E8 certificate, compressed-window construction and Clifford framework remain Sussman/PR352/PR377 contributions. This new route is dirty preconditioning plus heterogeneous residual banks; ordinary retiming and the eighteen-prefix word retain their existing attribution.

Independent scalar dual replay: structural-dual.cpp/.exe executes the inverse-adjoint literal scalar word with source/target role exchange and verifies all 1,046,529 entries against source/helper identity and target -M^T. Its separate witness structural-dual-prefix18.json has SHA256 f718717b56108910c22fdc4c0ac8f11ef8b88174a8d7cadcb893ad49a89896bb. This does not replace the chronological Clifford/private-centre audit. Three fixed-target controls in structural-controls.json reject one omitted helper preconditioner shear, one omitted target dirty cancellation and one omitted FULL helper repair. All failed earlier bank-overlap, lifetime-reuse and lexical-basis sink invoices are retained; none is included as a positive result.

Structural retrieval scope: four exact operator-cooccurrence predicates were queried read-only in the canonical DAG, with no declaration-name filter and no refresh of unrelated sources: TensorProduct.map+LinearMap.comp, Matrix.fromBlocks+Matrix.mul, LinearMap.rankOne+LinearMap.comp, and LinearEquiv.trans+LinearEquiv.symm. They returned 163 records, 140 typed and 23 source-only; the two 80-record queries were truncated. structural-operator-hits.json preserves IDs and snapshots. Current source statements inspected include SymplecticTI.contract_eq_comp, SymplecticTI.standardCoordEquiv_conjugates and GLOfPaddedGeneral20260902.padG_cancel_substituted. These contracts support explicit composition, conjugation and cancellation as structural background; they are not imported as a certificate of this new finite compiler, and no current Lean replay or complete-DAG search is claimed.
