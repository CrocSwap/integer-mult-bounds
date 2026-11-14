# Proofs and premises

Notation: n ports, G the root Gram matrix (rank r), K = ker G, Z = G/2 − I on partner cells (G_pt odd).
Arrivals at V are the public rows present at V plus the owned rows landing there. The deficiency is
D = rank(arrivals + targets) − rank(arrivals). Targets: X_p ↦ x_p − y_p; helpers/relays ↦ their own token.
The checked instances: A_m (roots e_i − e_j, ports e_i + e_j + e_{m+1} ∈ F₂^{m+2}; G/2 eigenvalues 0 and (m+1)/2)
and E8/P104 (G = D Tᵀ/2 from the PR968 decoder; rank 8, G² = 26G, 48 partners per port).

## Law 1. Charge law and the corrected anchored law [P]

**Premises (relay family).** (a) U-junk is cleaned by relays that lump −b·y_t, are read by X_p (coefficient
fixed by Z_pt) and re-add a copy of Y_t, ending as their own token; (b) every owned deposit is charge-neutral
(its x-part has rows in range G: true for U, which has no x, for parked copies, and for the E8-type L = G/2·x);
(c) each cell re-adds either Y_t^final (settled) or an owned copy O_t of pure y_t (early); (d) X finals at V.

**General witness.** A linear functional λ that kills every arrival but not every target certifies a missing
dimension. Take λ = (k on the x-symbols, k′ on the y-symbols, θ on tokens). Owned U rows at V are y-only and
span range G, so λ(U) = 0 forces k′ ⊥ range G, i.e. k′ ∈ K. Helper and relay
arrivals each contain their own token with coefficient 1, so θ is determined by them. Substituting into the X_p
arrival (x_p − y_p plus the relay reads) gives, row by row,
((I + Z^S)k + Z^E k′)_p = 0, where a settled cell contributes through Y_t^final = x_t (coefficient k_t) and an
early cell through O_t = y_t (coefficient k′_t). The solutions with k = k′ ∈ K are target-blind (they vanish on
x_p − y_p). Hence D = dim{(k, k′) : k′ ∈ K, (I + Z^S)k + Z^E k′ = 0} − dim K. ∎

**Corollaries.** All settled (E = ∅): the condition is (G/2)k = 0 with k′ ∈ K free, so D = dim K = n − r.
Column-pure sets give dim(K ∩ ker Z^E); per cell that form is wrong because solutions with k ∉ K exist
(8 of 90 checked sets). The σ-anchor schedule (one early cell per column on a perfect partner matching) gives
D = 0 on every E8 matching checked [C]; a general proof for all matchings is not claimed.

## Law 2. Carried-row law [P]

**Premises.** The word is linear; an owned MOVE moves one row and is billed |Δdim| ≥ 1 (SPEC P[d] per row);
owned INIT/COPY/dirty CLEAR are free and make no MOVE.

**Proof.** For each owned MOVE m of register R (F → F′), cut R at the MOVE: before it R is dirty-cleared at F;
after it a new owned register is born at F′ holding a fresh inert symbol σ_m. This σ-world has no owned MOVE;
let D₀ be its deficiency. The real word is the σ-world followed by the substitution π: σ_m ↦ c_m (the content of R
at the MOVE); this is exact because the word is linear and σ_m enters only through R. Let A be the σ-world
arrivals and W = span A ∩ (σ-free space). Then codim_{span A} W ≤ s := #σ, π is the identity on W, and so
span πA ⊆ W + (≤ s dimensions) and W ⊆ span πA. Targets T are σ-free, so T ∩ span A = T ∩ W and
D₀ = dim T − dim(T ∩ W), while D = dim T − dim(T ∩ span πA) ≥ dim T − dim(T ∩ W) − s = D₀ − s. Finally
s = #MOVEs ≤ Σ|Δdim| = owned units. ∎

## Law 3. Hub additivity [P]

**Setting.** Hubs j = 1..m in time order; S_j the X's finalised at hub j; fwd_j the ports whose finals are
present at hub j; K_j = {k ∈ K : k_{fwd_j} = 0}.

**Bound.** By the witness argument of law 1 (time-local cell charges), every register present at hub j is
killed by f_k for k ∈ K_j: forwarded finals τ_t carry f_k = −k_t = 0. Targets τ_p, p ∈ S_j, carry −k_p.
So D_j ≥ rank(K_j|S_j) = dim K_j − dim{k ∈ K_j : k_{S_j} = 0}. By law 2 each owned landing kills at most one
witness, so the owned units needed are ≥ Σ_j D_j.

**Telescoping.** Nested (fwd_j = S_{<j}): K_{j+1} = {k ∈ K_j : k_{S_j} = 0}, so Σ D_j = Σ (dim K_j − dim K_{j+1})
= dim K₁ − dim K_{m+1} = dim K − 0. Without forwarding, write ρ(A) = dim K − dim{k ∈ K : k_A = 0}, the rank of K
restricted to A (a matroid rank function, hence subadditive). Intermediate hubs give D_j = ρ(S_j) and the last
hub gives dim K − ρ(S_{<m}), so Σ D_j = Σ_{j<m} ρ(S_j) + dim K − ρ(∪_{j<m} S_j) ≥ dim K. ∎

**Scope.** The time-local arrival formula is proved for the relay family at frames where every cell is either
pre-lump or post-re-add. Hubs placed below relay re-add frames (pre-re-add relay states co-present) are covered
only through Lemma A, now the corrected PA of [ADDENDUM.md](ADDENDUM.md) (G1 + PA_gen).

## Law 4. The per-J odd unit

- [C] Arithmetic facts in odd_unit.py (o(Hⁿ), H³ = −I, o(SW) = 1, the lift, the gauge frame).
- **Automorphisms [P].** If σ(U) = U then σ(UNU⁻¹)(UNU⁻¹)⁻¹ − I = U(σ(N)N⁻¹ − I)U⁻¹, which has the same rank.
  Port relabels inside the label space are σ-fixed, so they cannot change any factor's o.
- **Gauge ledger [cond].** A gauge-shifted contract returns diag(q^{g_r})·T. Its σ-target is −1 on
  m = #{r : g_r even} roles. By Lemma E (#7555) with o(H) = 2 per J and non-involutive factors, the word needs
  ≥ m + 1 odd units, i.e. ≥ m − 16 odd ops beyond the 17 J. **Premise:** the parent applies diag(q^{−g}), of odd
  rank 36 − m, and every σ-odd unit at the boundary costs at least one odd op (each is a child-size transform,
  not a monomial). Under it the total is ≥ (m − 16) + (36 − m) = 20 for every m.
- **Finite order.** M⁶ = I is a statement about powers of one matrix. A caller exploits it only if it applies H
  to the same plane more than once. The #7113-type caller pairs fresh content at each J (an author run on the
  MONOHUB caller found 17 pairwise independent input planes spanning 34 dimensions; that caller is not packaged
  here and the statement is listed as a follow-up).

## Law 5. Y-atom conservation — original form RETRACTED (see [ADDENDUM.md](ADDENDUM.md))

**RETRACTED (Nov 13).** The original premise is kept below, struck, for the record. It is false on E8/P104 with
"neutral" read as "Y_q holds no public x-charge". A σ-anchor design whose every Y_t first takes −Z_ts·x_s from a
pure X_s and is then snapshotted and parked has N_neutral = N_owned = 0 and D = 7, against the literal bound 96
(`counterexample.py`).

> ~~**Premise PA (Lemma A).** There is a set N of columns, |N| = N_neutral + N_owned, such that every cell charge
> φ_pu lies in span({e_u} ∪ {e_q : q ∈ N}), with φ_pu = e_u unless u ∈ N. (A y-atom of column q leaves Y_q only
> during Y_q's neutral period or through an owned copy.)~~

**Corrected premise (replaces it).** A y-atom of column q is a frame-local time difference of Y_q, or an owned unit.
In the park family F1, every L-cell counted in Y_q^final is delivered after the park snapshot, at frames ⊇ the export
frame (Lemma P). For all programs D ≥ (n − r) − dim Q_V, where Q_V is the y-classes of token-free arrival
combinations at V (G1). The inequality below holds under PA_gen: Q_V ⊆ span{e_q : q ∈ N}. Statements, proof
sketches and the open cases are in ADDENDUM.md.

**Theorem [P under PA_gen; the algebra below is unchanged].** Row p of the arrival map is
(G/2)_{p,N^c} k_{N^c} + F_p·k_N with F arbitrary. For k ∈ K with k_N = 0 this is (Gk/2)_p = 0, so f_k kills every
arrival, while f_k(τ_{X_p}) = −k_p. Hence D ≥ dim{k ∈ K : k_N = 0} ≥ dim K − |N|. ∎ What fails is the identification
of N with the x-neutral columns; the 96-per-call reading for N_neutral = 0 is withdrawn.

**Cell form [P].** Z^E K = Σ_u v_u K_uᵀ over the columns u that hold early cells, a sum of rank-one terms, so
rank(Z^E K) ≤ #(such columns) and D ≥ n − r − #(columns): atoms count columns, never cells. (This concerns clean
early cells; contaminated snapshots are charged per distinct source, see ADDENDUM.md.)

**Status.** PA_gen is proved in the park family F1 (Lemma P) for the L-side bill. It is open for programs that remove
y_t from Y_t by tokened public routes, the J gauge or carrier preloads. The empirical law D ≤ ρ_K(sources) is
unproved.
