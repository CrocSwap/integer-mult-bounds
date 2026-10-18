# Format obstructions: statements, proofs and the checks behind them

Labels: **[P]** proved here by hand; **[C]** checked by computer, exactly (F₂, integer or `Fraction` arithmetic, or
SAT); **[M]** a pricer or model output, not a theorem; **[U]** a hypothesis read from upstream and not re-derived
here. `verify.py` runs every [C] and [M] item; §11 maps each statement to its check.

## 0. Conventions

- A label space L of dimension m carries a symmetric bilinear form ⟨·,·⟩ over a field F (F₂ with the dot product for
  the complex words; ℚ with the E8 form or x ↦ xᵀ(I − J/9)y for the bit words). For a subspace V, V^⊥ is its
  orthogonal, rk V = dim V − dim(V ∩ V^⊥) is the rank of the form restricted to V, and V is *nondegenerate* if
  V ∩ V^⊥ = 0. If V is nondegenerate then L = V ⊕ V^⊥ and V^⊥ is nondegenerate (L is nondegenerate).
- A pair (port) a has a *label* U_a ⊆ L, nondegenerate of dimension k_a. In every program checked here U_a = ⟨q_a⟩
  with ⟨q_a, q_a⟩ ≠ 0 (k = 1).
- `h` is the window dimension of one invocation, `v` the number of ports, `R` the number of helper registers,
  `cst` the copy cost, `m` the dimension of the whole label space of a multi-stage word.

## 1. The model

**Frames and steps.** Every register stands at a *frame*, a subspace of L, and changes frame by *steps*. A step
f → g is *nested* if f ⊆ g and a *drop* otherwise. It costs d(f, g) = dim f + dim g − 2 dim(f ∩ g), the rank of the
block (upstream's general frame lemma, Jacob Sussman's `frame_lemma` in the Lean repository; used as a black box and
only for prices, never in Theorems A and B).

**Gates.** A gate is a free linear addition between registers that all stand at one common frame; each register
first reaches that frame by a step.

**Data wires.** The source wire x_a starts at U_a. The target wire y_a starts at 0 and every frame it ever occupies
lies inside U_a^⊥. Helper registers ("slots") start at 0. These are the rules E0–E3 of `gx.check1` (see `gx/gx.py`):
`E1` labels (nested steps, equal frame at a gate, x: ⟨q⟩ → full, y: 0 → q^⊥, slots 0 → full), `E2` the scatter cut
(every y at frame 0 when the retained totals are copied), `E3` gate kinds, `E6` the block ledger.

**Drop-free paths.** A contribution of x_T reaches a register w *drop-free* if there are registers
x_T = r₀, r₁, …, r_k = w and times 0 = t₀ < t₁ < … < t_k such that a gate at time t_i adds r_{i−1} into r_i, and
r_{i−1} takes only nested steps between t_{i−1} and t_i. (A drop of the *receiving* register before the gate does
not matter.)

**Two semantics in which the statements are checked.**
1. `gx.check1` (gcert/1): the rules above, with the star scatter, plus the exact scalar identity E5. Checked on
   three programs: the p = 3 toy (v = 8), the p = 10 complex program of PR #327 (v = 960) and Sussman's p = 11
   program of #193 (v = 1,320). All three are complex-side programs.
2. PR #425's mutable-basis semantics (jacklightChen): gates (adds and dyadic scalings) between registers at the
   same current label, nested climbs except the eight centre copies (full → 0), source registers and target
   registers may be modified and read, no target feeds a source or helper register, a frame-0 preconditioner
   y ← V⁻¹(y − K s) and a cleanup of all source and helper registers at the full frame. The model above contains
   this semantics (it never assumed immutable sources); §9 checks it on #425's own word.

Not covered by any check here: the bit words (their checker is the community's paired-cube checker, not gcert/1), and
the Lean layer.

## 2. Theorem A (content-frame invariant) [P][C]

**Statement.** If a register w receives at time t a contribution of x_T along a drop-free path, then
frame(w, t′) ⊇ U_T for every t′ ≥ t until w's next drop.

**Proof.** Induction along the path x_T = r₀, …, r_k = w of the definition. x_T starts at U_T and takes only nested
steps until t₁, so frame(x_T, t₁) ⊇ U_T. The gate at t₁ puts both registers at one frame F₁ = frame(x_T, t₁) ⊇ U_T, so
r₁ stands at F₁ ⊇ U_T after it. Between t_i and t_{i+1} the register r_i takes only nested steps, so its frame at
t_{i+1} still contains U_T, and the gate at t_{i+1} puts r_{i+1} at that frame. ∎

**Corollary A1.** If a drop-free path leads from x_T to y_S, then U_T ⊆ frame(y_S) ⊆ U_S^⊥, so U_T ⊥ U_S. This holds
for any number of hops, any gate kinds (x→x, y→y, s→s, x→y, s→y), any write order, any layout, and for recursive
invocations (a nested invocation is a sub-network; flatten it).

**Corollary A2.** U_S is nondegenerate and nonzero, so U_S ⊄ U_S^⊥: no drop-free path leads from x_S to y_S. Every
route that delivers x_S to y_S passes a drop.

**Check [C]** (`checks/certs.py`). Replay the gates of each program and carry, for every register, the set of
sources that reached it drop-free (the scatter, a drop, passes none). At every gate every newly received source port
must lie in the gate's frame (exact F₂ reduction). Result: 110 / 1,081,204 / 2,063,837 gate checks (p = 3 / 10 / 11),
0 violations. The final set of y_S is orthogonal to q_S, never contains S, and has size 4 / 620 / 884. Controls:
cyclically shifting the labels makes 12 of the lossless pairs of the p = 3 program non-orthogonal; corrupting one port
(odd weight kept) is rejected by `gx.check1` at E1 and gives 14 violations in the replay.

## 3. Theorem B (stage additivity) [P] under hypotheses [U]

**Rank lemma.** If V₀, …, V_s ⊆ L are pairwise orthogonal then Σ rk V_i ≤ m.
*Proof.* Let B be the list of the union of bases of the V_i (the V_i may overlap in isotropic vectors, so the list may
be dependent). Its Gram matrix is block diagonal with blocks Gram(basis of V_i), so its rank is Σ rk V_i. The Gram
matrix of a list is BᵀQB with B the m × |B| coordinate matrix, so its rank is at most m. ∎

**Setting.** Fix a pair a and the stages j = 1, …, s that run an invocation containing it, in time order. Let 𝒯_j be
the targets of stage j (all ports) and M_j = span{U_b : b ∈ 𝒯_j}. Let C_j be the span of the labels U_b of the
ports b that reach Y_a drop-free during stage j (the *correctors* of a; by Cor. A1 C_j ⊆ U_a^⊥).

- (B1) *Target family.* There is a nondecreasing family of subspaces Ψ(t) with frame(Y_a, t) ⊆ Ψ(t) ⊆ U_a^⊥. (In a
  layout with twin gates, Ψ is the frame of the wires tied to Y_a.)
- (B2) *Common cut.* There are times τ₁ < … < τ_s ≤ τ_{s+1} (the end) such that at τ_j every target b ∈ 𝒯_j stands at
  the frame Ψ(τ_j), and all gates of stage j precede τ_{j+1}.
  In `gx.check1` programs this is E2 (all y at frame 0 at the scatter).

**Statement.** Put N_j = Ψ(τ_{j+1}) ∩ M_j. Then U_a, N₁, …, N_s are pairwise orthogonal, and C_j ⊆ N_j. Hence
k_a + Σ_j rk C_j ≤ m.

**Proof.** (i) N_j ⊆ Ψ(τ_{j+1}) ⊆ U_a^⊥. (ii) For j < j′: N_j ⊆ Ψ(τ_{j+1}) ⊆ Ψ(τ_{j′}) by monotonicity, and by (B2) Ψ(τ_{j′})
is the frame of every target b of stage j′, hence ⊆ U_b^⊥; so N_j ⊥ M_{j′} ⊇ N_{j′}. (iii) C_j ⊆ N_j: a corrector b of a in
stage j has U_b ⊆ frame(Y_a at its arrival) by Theorem A, which lies in Ψ(τ_{j+1}); and U_b ⊆ M_j. The rank of a
subspace is monotone (a principal submatrix has rank at most that of the matrix), so rk C_j ≤ rk N_j. The rank lemma
gives k_a + Σ rk N_j ≤ m. ∎

**Corollary B1.** Suppose in every stage the correctors of a span all of U_a^⊥ ∩ (window), of dimension h − 1; this
subspace is nondegenerate (complement of a nondegenerate line), so rk C_j = h − 1. Then
m ≥ 1 + s(h − 1). For the five-stage layout s = 5, for K-stage layouts with twin gates s = 2K + 1:
m ≥ 1 + (2K + 1)(h − 1). If the saving of a data wire is at most k, i.e. D ≤ N_data·k (the ledger of the five-stage
layout, D = 4kv − 5·cst [U]; read from upstream and not derived here), the saving fraction obeys
δ = D/(mW) ≤ (N_data/W)·k/(k + Σ_j rk C_j).

**Measured neighbourhood ranks [C]** (`checks/certs.py`, `checks/families.py`, `checks/sat_e8.py`,
`checks/mutable425.py`): the span of the drop-free correctors of every target is exactly q^⊥, of dimension h − 1:

| family | h | ports | correctors per target | rank |
|---|---|---|---|---|
| complex p = 10 (#327) | 20 | 960 | 620 | 19 |
| complex p = 11 (#193) | 22 | 1,320 | 884 | 21 |
| bit, paired cube p = 4, 5, 10, 11 (ℚ, x ↦ xᵀ(I − J/9)y) | 8, 10, 20, 22 | 32 … 1,320 | 15, 39, 339, 435 | 7, 9, 19, 21 |
| E8 bit dual (ℚ⁸, E8 form) | 8 | 120 | 63 | 7 |
| E8 complex (unique h = 9 labelling, §6) | 9 | 120 | 56 | 8 |
| #425's word, final lossless set of each target | 9 | 120 | | 8 |

The complex p = 10, 11 rows and the #425 row are replayed drop-free correctors (final taint of every target). The bit
and E8 rows are the in-cap neighbourhoods of the family, not replayed correctors: for the paired cube `paired_bit`
computes port 0 only (the automorphism group of the paired cube is transitive on ports, not checked here), for E8 every
line is computed.

The p = 3 program is degenerate (its ports span a 4-dimensional subspace of F₂⁶; rank 3 ≠ h − 1 = 5) and is not used
for Theorem B.

Bounds from Cor. B1, against the widths in use: m ≥ 96 / 134 / 172 (p = 10, s = 5 / 7 / 9) against 100 / 140 / 180;
106 (p = 11, s = 5) against 110; 36 (E8 bit dual, s = 5) against 40. For E8 complex at s = 9 the bound is
1 + 9·8 = 73, and **#425's word has m = 73** (the `m` of its report): Theorem B is attained. For the E8 bit dual at
s = 9 the bound is 64; the width of #386 is 64 (reported in #386, not checked here).

**What (B1)–(B2) are in a layout [U].** In the five-stage layout of Sussman's repository at f010392c
(`Work/Bridge/Net.lean`, `Work/BridgeGeom/Stage.lean`, `Work/BridgeGeom/Net.lean`) the target family of a pair is tied
across the 2K + 1 stages by twin gates, and every stage has a common cut. These facts were read from those files; their
consistency with (B1)–(B2) is not formally verified (see §12). #425's nine-stage word satisfies (B2) at its
scatter (all 120 targets stand at frame 0 at the cut, checked in §9).

**What Theorem B does not bound.** It bounds m below by a function of the neighbourhood rank. It says nothing about the
helper count R, and nothing about a port family whose correctors span less than q^⊥.

## 4. Theorem C (drop pricing) [P][C]

**Statement.** Let a retained total be gathered drop-free from sources P, with root frame f ⊇ V := Σ_{T∈P} U_T
(Theorem A). Its content is delivered to readers Q through a rooted tree of arrays: each non-root array is a copy
taken by a gate at its parent's current frame, and every array may take any steps (drops and climbs, degenerate
frames included). Every reader b reads at a frame ⊆ U_b^⊥. Then the total cost of the drops in the tree is at least
rk(V × U(Q)) = dim V − dim(V ∩ U(Q)^⊥), the rank of the pairing V × U(Q) → F, with U(Q) = Σ_{b∈Q} U_b.

**Proof.** Attach to every array e a *survivor* S_e ⊆ V, defined along time: at the root S = V; a nested step leaves
S unchanged; a drop f_e → g_e replaces S by S ∩ g_e; a copy starts with the survivor of its parent at the copy time.
By induction S ⊆ frame(e) at all times (at the root V ⊆ f; a nested step enlarges the frame; after a drop S ⊆ g_e;
a copy stands at the parent's frame). A drop costs d(f_e, g_e) ≥ dim f_e − dim(f_e ∩ g_e) ≥ dim S − dim(S ∩ g_e),
because S ⊆ f_e and the map S → f_e/(f_e ∩ g_e) has kernel S ∩ g_e.

Let a reader b read array e at time t. Its common frame F_b with e lies in U_b^⊥ and contains S_e(t); write S_b = S_e(t),
so S_b ⊥ U_b. For an array e define σ(e) as its survivor at creation and ρ(e) as the intersection of the S_b over
all readers in the subtree of e (ρ(e) = σ(e) if there are none). Claim: cost(subtree of e) ≥ dim σ(e) − dim ρ(e).
Induct over the tree. Along e the survivors form a decreasing chain S₀ = σ(e) ⊇ S₁ ⊇ … ⊇ S_last; e's own drops cost at
least dim S₀ − dim S_last. A child c_i created when the survivor is S(i) ⊇ S_last has cost ≥ dim S(i) − dim ρ(c_i), with
ρ(c_i) ⊆ S(i). Direct readers see survivors ⊇ S_last. Then ρ(e) ⊇ S_last ∩ ⋂ρ(c_i), and the codimension of S_last ∩ ρ(c_i) in
S_last is at most that of ρ(c_i) in S(i); so dim ρ(e) ≥ dim S_last − Σ(dim S(i) − dim ρ(c_i)). Adding up gives the claim.
At the root, ρ ⊆ V ∩ ⋂_b U_b^⊥ = V ∩ U(Q)^⊥. ∎

**Corollary C1 (read discipline is worthless when the readers span the window).** If U(Q) is the whole nondegenerate
window then V ∩ U(Q)^⊥ = 0 and the bound is dim V: splitting the readers into classes, reading at nonzero frames,
climbing copies, or any tree is never cheaper than one copy dropped from f to 0 when f = V. The bound is subadditive over
column blocks: rk(V × ΣU(Q_i)) ≤ Σ rk(V × U(Q_i)).

**Equality [C].** In all three gcert/1 programs every retained total has frame f = V, and the readers (all ports)
span the window, so the star copy meets the bound: p = 10: 20 totals × 18 = 360 = cst; p = 11: 440 = cst. On #425's word
each of the eight centres gathers 57 sources (the drop-free taint before the cut, equal to the support of its root-line
coordinate), which span F₂⁹; the pairing ranks are 9 each, 72 in total, equal to the frames paid (8 × 9). For the E8 bit-dual
decoder M = UUᵀ (9 totals, each read by the 56 ports of its bit, rank_ℚ of the Gram block = 8) the package computes only the
bound, 72; it equals the copy loss #370 reports (nine retained totals at the full frame), which is not replayed here.
For the p = 3 program the port span is degenerate: the bound is 12 and the paid cost 18.

**The one gain (p = 3 toy) [C]** (`checks/toy.py`). The ports of the p = 3 program span W of dimension 4 with W^⊥ ⊆ W
(radical of dimension 2, nonzero vectors 001111, 110011, 111100). Allow the scatter in cuts; at a cut all y stand at
one common frame g ⊆ ⋂ q^⊥ = W^⊥, copy k costs d(f_k, g), and the cut frames form a chain. Cut 1 at g = 0 for the totals
2–5, the y climb to l = 111100, cut 2 at g = ⟨l⟩ for the totals 0, 1. Result: cst 18 → 16, moves 194 → 192, every
register chain nested, equal frames at every gate, every y inside q^⊥ and avoiding q, block mass R·h + 2v(h − 1),
and `gx.scal` passes (gates and coefficients unchanged). An exhaustive search over all chains of cut frames in W^⊥
gives optimum 16 (the old format: 18). Control: a common frame outside the radical puts some target outside its q^⊥.
The gain needs W^⊥ ≠ 0, a degenerate port span. In the p = 10 and p = 11 programs (and every family above) the ports
span the nondegenerate window (`window_rank = h`), so g = 0 is forced and the gain is 0.

## 5. The clique bound [P][C]

**Statement.** Let K be a set of ports such that for all T ≠ S in K there is a drop-free path from x_T to y_S. Then the
U_T (T ∈ K) are pairwise orthogonal and nondegenerate, so they form an orthogonal direct sum and
Σ_{T∈K} k_T ≤ r, where r is the dimension of the window that contains the labels. If H is the graph of ports joined
by a drop-free route, k_T = k for all T, then k·ω(H) ≤ r.

**Proof.** Corollary A1 gives pairwise orthogonality; each U_T is nondegenerate, so U_T ∩ Σ_{S≠T} U_S ⊆ U_T ∩ U_T^⊥ = 0. ∎
The statement is independent of the field, the form and any symmetry of the labels.

**In the five-stage ledger** (D = 4kv − 5·cst, W = 4v + R, m = 5h): δ = D/(mW) < k/(5h) ≤ 1/(5ω(H)).

**Instances [C]** (`checks/families.py`, `checks/sat_e8.py`; ω of the in-cap graph of the paired cube, exact maximum
clique): bit side (|S ∩ T| = 1) ω = p for p = 4, 5, 6, 7; complex side (|S ∩ T| ∈ {0, 2}) ω = 8, 8, 12, 12 for p = 4, 5, 6, 7.
For p = 10 complex, 20 ports (five pairwise disjoint transversal 4-sets from the K₅ stars, all four triples each) are
pairwise orthogonal with q·q = 1 and every pair of them is a drop-free pair inside the #327 program itself, so
Σ k_T ≤ 20 = h and k = 1. The E8 in-cap graph (3,360 edges, degree 56) has ω = 8 (8,640 maximal 8-cliques, each an
orthonormal basis): k = 1 needs r ≥ 8, k = 2 needs r ≥ 16 by the bound alone and r ≥ 18 by §6.

On the bit side ω = p = h/2, so the bound allows k = 2 at r = h; it says nothing against k = 2 there.

## 6. Labels on the E8 in-cap graph: exact SAT results [C]

Setting (`checks/sat_e8.py`; CaDiCaL 1.5.3 (`Cadical153`, uniqueness) and 1.9.5 (`cadical195`, planes) through python-sat 1.9.dev15). H is the graph on the 120 E8 root lines
(Hamming coordinates of #370) joining lines with ⟨a, b⟩ = ±1. A *k-dimensional labelling in dimension r* assigns
to every line a nondegenerate k-dimensional subspace A_T of (F₂^r, dot product), with A_S ⊥ A_T on every edge.
By Cor. A1 these are the labels of any word in which H is realised by drop-free correctors.

**Reduction.** Fix an 8-clique C of H (§5). Its labels are pairwise orthogonal and nondegenerate, hence an
orthogonal direct sum. The window dimension is r ≤ 17, so the complement of the span of C has dimension at most 1
(k = 2: r − 16) or r − 8 ≤ 1 (k = 1, r ∈ {8, 9}), and is absent or I₁.
- k = 1: the labels are orthonormal; as F₂^r = ⟨C⟩ ⊕ ⟨C⟩^⊥ with ⟨C⟩ of dimension 8 and ⟨C⟩^⊥ absent (r = 8) or a nondegenerate
  line ⟨w⟩ with w·w = 1 (r = 9), an isometry of (F₂^r, ·) maps them to e₁, …, e₈. Every other line T has A_T orthogonal to the blocks of the clique members adjacent
  to T, i.e. supported on the blocks of the non-adjacent members and on the complement coordinates.
- k = 2: each plane of C is either I₂ (p·p = q·q = 1, p·q = 0) or the hyperbolic plane (every nondegenerate symmetric
  plane over F₂ is one of the two); for r = 16 the 8 planes are the whole space, so not all can be hyperbolic (that form
  is alternating, the dot product is not); for r = 17 the complement is I₁. Non-clique planes are free of type.
  The SAT instance enumerates all 2⁸ type patterns of the clique (255 for r = 16).

**6.1 Uniqueness at h = 9.** The CNF has the 9 coordinates of every line, u·u = 1, orthogonality on H, and injectivity
of the labels (E0 of `gx.check1`). Enumerated to exhaustion: **exactly one solution** (blocking clause after the first
solution is UNSAT). It is checked independently of the CNF: u·u = 1, orthogonal on all 3,360 edges, injective, and
u_a·u_b = 1 on all 3,780 E8-orthogonal pairs, which is the Gram matrix of Sussman's E8 complex unit (decoder
M = J + (G mod 2)). So every h = 9 labelling of H is, up to an isometry of F₂⁹, Sussman's. Its correctors span rank 8
for every line. #425's ports satisfy exactly this Gram relation with the word's own root lines (all 120 × 120 entries),
so #425 uses that labelling. Control: the same CNF with h = 8 is UNSAT.

**6.2 Planes (k = 2).** **UNSAT for r = 16 (255 patterns) and r = 17 (256 patterns).** A labelling in dimension r ≤ 17
would embed in dimension 17 by padding with zero coordinates (the dot product of F₂^{r+1} restricts to that of F₂^r), so
there is no k = 2 labelling of H in any dimension r ≤ 17: k = 2 needs r ≥ 18. Dimension 18 is attained by the direct sum
of two copies of the 9-dimensional labelling (A_T = ⟨(u_T, 0), (0, u_T)⟩), a split labelling. Controls: the k = 1
encoder at r = 8 is UNSAT and at r = 9 SAT (rank 9); the k = 2 encoder at r = 18 accepts the direct sum (SAT under the
assumptions that fix it), so the UNSAT results are not an artefact of the encoding.

This closes the labelling lever only for the **full E8 in-cap graph**: it says nothing about subgraphs, other
decoders or other port sets.

## 7. Fixed-role B₂ windows: Theorem P [P][C], with its exact scope

**Scope.** Theorem P concerns layouts in which one helper set runs the same program on the same slots in every stage
and the stage windows are transports of one window (the fixed-role windows of the five-stage layout B₂ of Sussman's
repository, as read). It is stated for F₂ dot-product windows and checked on the complex gcert/1 programs of #327
(p = 10) and #193 (p = 11) only, and it is **not a general obstruction**. **Compressed windows circumvent it**: #425's
nine-stage complex word has m = 73 = 1 + 9·8 (checked in §9), which attains the width bound of Theorem B and lies below
the s·h = 81 that Theorem P forces for a fixed-role complex layout whose program's slot-carried pairs span, so its
windows do not satisfy (P1)–(P2) together with a spanning program. PR #386's nine-stage bit word (reported m = 64 =
1 + 9·7, h = 8) has a ℚ form; Theorem P is not stated or checked for ℚ forms and nothing is claimed about whether
the analogue would force 72 there.

**Hypotheses [U].** (P1) Stage j runs the program c on the window W_j = ι_j(F₂^h), where ι_j : (F₂^h, ·) → L is an
isometric embedding (so W_j is nondegenerate of dimension h); in stage j the source T starts at ι_j(⟨q_T⟩) and every
frame of y_S during stage j lies in ι_j(q_S)^⊥. (P2) One helper set runs the *same* program on the *same* slots in
every stage, and slots never drop (nested steps only). Both are read from the layout, not re-derived here.

**Statement.** For stages j < j′ let K = ι_jᵀι_j′ (h × h over F₂). Let the *slot-carried pairs* be the pairs (T, S) such
that T is in the final set of sources that reached some slot z drop-free in the program and z writes the target y_S.
If the tensors q_T ⊗ q_S over the slot-carried pairs span F₂^{h×h}, then K = 0. Consequently W₁, …, W_s are pairwise
orthogonal, nondegenerate, and m ≥ s·h.

**Proof.** After stage j the slot z stands at a frame containing ι_j(q_T) for every such T (Theorem A in stage j) and it
never drops. In stage j′ it writes y_S at a frame inside ι_j′(q_S)^⊥ (P1). So ⟨ι_j q_T, ι_j′ q_S⟩ = q_Tᵀ K q_S = 0 for
every slot-carried pair. This is linear in K; if the q_T ⊗ q_S span, K = 0. Pairwise orthogonal nondegenerate
subspaces form a direct sum. ∎

**Check [C]** (`checks/pivots.py`). The pairs with q_T·q_S = 0 alone span a space of dimension h² − 1 (their tensors lie
in the hyperplane tr M = Σ M_ii = q_T·q_S = 0; this leaves K = λI), and the full set of slot-carried pairs spans h²:
399 / 400 on the #327 program (3,708 writer slots) and 483 / 484 on #193 (4,125 writer slots). So K = 0; a
slot-carried pair with q_T·q_S = 1 is what excludes K = λI, i.e. two stages with identified windows. By Cor. A1 such a
pair cannot be drop-free within one stage, so T necessarily reached the slot only after the slot wrote y_S.

A shorter route to K = 0 exists under (P1)–(P2) and rule E1 of `gx.check1` (every slot ends a stage at the full window):
the frame of a slot in stage j′ contains ι_j(F₂^h), so ι_j(F₂^h) ⊥ ι_j′(q_S) for every slot-written S, and the ports of the
slot-written targets span F₂^h (rank 20 and 22, checked). The taint computation above proves the stronger version that
needs only the frames actually reached by taint, so the rank 399/400 should not be overweighted.

**What the exact part gives, and what is priced [M]** (`checks/pricing.py`, pricer `inputs/pricing/cost.py`, histogram of
#325's p = 10 bit word, pinned root reproduced). If the 2K block pivots were free (m = 1 + 5(h − 1) = 96 instead of
100: each helper wire loses 4 levels, the pair-1 end idle block 2h + 2 → 2h − 2, the pair-2 end idle block of rank 4
disappears), the saving of the p = 10 bit word would be larger by +3.56 % to +8.11 %, depending on which helper blocks
shrink (largest blocks / mid blocks / 2 → 1 / rank-1 blocks removed: +3.56, +5.75, +6.39, +8.11), and by +1.53, +3.68,
+4.30, +5.99 with 40 extra copy ranks per unit (below). The saving would be unavailable to fixed-role B₂ windows if the
analogue of Theorem P holds for the bit word's programs; that is **not claimed**, since Theorem P is stated and was
computed on complex F₂ programs only and no bit certificate was replayed. Nothing here concerns compressed windows.

**Measurements for one overlap [C][model]** (`checks/pivots.py`). Suppose two stage windows of a *shared-helper* layout
overlap in one direction w = ι_{j−1}(e) = ι_j(e′) with e·e = e′·e′ = 1. A retained total whose frame is not inside e^⊥
carries w into stage j and, in the model, pays one extra copy rank there unless e′ lies in its frame. Over all
odd a, b ∈ F₂²⁰ and the 20 retained totals of the #327 program (frames of dimension 18): at most 1 total has a frame
inside a^⊥ and at most 9 frames contain b, so ≥ 20 − 1 − 9 = **10 forced extra copy ranks per overlap**. On the helper
side, for each of the 1,160 candidate directions tried (the 20 unit vectors and the 1,140 weight-3 vectors) at least
5,984 of the 6,515 slots end at a frame not inside e^⊥, and the forward closure of those slots through the gates
contains all 8,435 registers and all 960 targets (their ports have rank 20, so no e′ ⊥ all of them exists). These are
counts in a stated model for one program with shared slots; they say nothing about layouts whose helpers are organised
differently.

## 8. Non-nested steps on registers [P][M]

**Proposition N [P].** A register whose chain runs from f₀ to f_end with nested steps except one non-nested step f → g
has total mass (dim f_end − dim f₀) + 2r with r = dim f − dim(f ∩ g). *Proof.* The step costs d(f, g) = r + r′ with
r′ = dim g − dim(f ∩ g); the nested steps cost (dim f − dim f₀) + (dim f_end − dim g); and dim f − dim g = r − r′. ∎
So a descent of rank r on a register that must still reach its sink costs 2r more than a nested chain with the same
endpoints. A copy of rank r is charged r by the ledger (`gx.check1`: N + tails = R·h + 2v(h − 1) + cst, with the copy
blocks H["c"][dim f] in `cst`).

By Theorem C the drops that carry a total to its readers cost at least rk(V × U(Q)) however they are arranged, and the
star copy attains it on every family checked; a register descent pays that and then the re-climb.

**Pricing [M]** (same pricer and histogram as §7). One rank-1 copy in each of the five stages, per 12-normalised unit,
is 60 extra blocks of rank 1 (5 × 12): **−0.2457 %**. One rank-1 register descent in each of the five stages is one
non-nested step of rank d = 2 per stage, 60 extra blocks of rank 2: **−0.4911 %**. Quote ≈ −0.49 %: other blockings of
the same mass give −0.4906 % to −0.4914 % (two rank-1 blocks: −0.4914 %), so the fourth digit is a modelling choice.

**Two-level words.** A word whose gates are small verified words flattens to a nested-frame network; Theorems A–C apply
to the flattened network unchanged.

## 9. PR #425's mutable-basis word: Theorems A–C and Theorem S [C][P]

Input: `inputs/pr425/FULL-WORD.json.gz`, #425's `FULL-WORD.json.gz` (920 registers: 120 sources, 120 targets,
680 helpers; m = 73, h = 9), regenerated with #425's own `hamming_packets.py` and `hamming_full.py` under Python 3.12;
its sha256 equals the one in #425's `EXPECTED.json`.

**Replay [C]** (`checks/mutable425.py`, the same frame and taint detector as §2). 0 violations of: nested climbs,
common frame at every gate, taint of both gate registers inside the gate frame (Theorem A), target frames inside
q^⊥, target taint orthogonal to its port (Cor. A1), no target feeding a source or helper register. All 120 targets stand at
frame 0 at the scatter ((B2)), and the final lossless set of every target has rank 8 = h − 1 (Theorem B: m ≥ 1 + 9·8 = 73
= m of the word). On the eight centre copies the pairing-rank bound (Theorem C) is 72 and the frames paid are 72. The
same detector in *immutable-source / no-target-read* mode flags 1,640 modifications of sources and 112 reads of
targets in the word as written. Exact scalar replay over ℚ: the helpers and sources are restored, J = I, and with the
frame-0 preconditioner y ← V⁻¹(y − K s) the word is exactly (x, s, y) ↦ (x, s, y + x); omitting the K part is rejected.

**Theorem S (simulation) [P].** *Hypotheses.* Let 𝒲 be a word with (H1) nested climbs and common-frame gates and
invertible scalings; (H2) no gate has a target as source and a source or helper as destination; (H3) after a frame-0
preconditioner y ← V⁻¹(y − K s) it acts as (x, s, y) ↦ (x, s, y + x). Let b_x be the number of source registers that are
destinations of some gate and b_y the number of targets that are sources of some gate.
*Statement.* There is a word 𝒲′ with R + b_x + b_y helper registers in which no source is modified and no target is read,
with the same frames at the corresponding gates, that acts as (x, s, g, y) ↦ (x, s, g, y + x) after a frame-0 preconditioner.
*Proof.* For each modified source r add a helper g_r and a gate g_r += x_r at frame ⟨q_r⟩ (g_r climbs from 0, x_r
is already there). For each read target t add a helper g_t, starting at frame 0. Rename every occurrence of x_r and y_t
in every event of 𝒲 to g_r and g_t. Then g_r and g_t follow the frame sequences of x_r and y_t, so every gate has the
frames it had; the real x_r are never modified and the real y_t (t read) never read. After the last event add y_t += g_t
at the frame q_t^⊥ (g_t is inside it, as y_t was). Finally undo, at the full frame and in reverse order, every renamed event
whose destination is not a real target, and add g_r −= x_r. By (H2) these events read, in 𝒲′, only source registers and
helpers (the g's are helpers), so the reverse sequence restores every source and helper register exactly, whatever the
targets hold. Every real target then ends at y_t + (J x)_t + ℓ_t(s, γ), where γ is the initial dirt of the g's and ℓ_t is
linear (it collects the V and K responses, including those that unread targets receive from renamed g_u); the
coefficients of x are those of 𝒲, so J = I. The dirty registers (s and g) stand at frame 0 at the start, so the
preconditioner y ← y − ℓ(s, γ) removes all such terms. ∎

*Consequence.* Relative to its own simulation in the immutable-source / no-target-read format, the mutable-basis format
saves at most b_x + b_y ≤ 2v helper registers (at most one per source and one per target). It bounds the helper
count of the simulation, not its price.

**Check [C].** On #425's word b_x = b_y = 112; the simulation has 904 = 680 + 112 + 112 helpers. The same detector finds 0
violations in it (immutable mode), z is restored exactly, and after the frame-0 compensation the map is exactly
(x, s, y) ↦ (x, s, y + x); without the compensation it is not. Under the coarse formula of #425's `hamming_full.py`
(reproduced: b = 1.049105 × 10⁻³ for #425's word) the simulation has b = 9.102 × 10⁻⁴ (−13.24 %), below the pre-#425
word (9.994 × 10⁻⁴). The simulation was not run through `gx.check1`; it was replayed by the detector above.

## 10. What the theorems bound, and what they do not

Theorems A–C and the clique bound bound three things: the label dimension k (for a given in-cap graph), the width m
(Theorem B, for a given corrector rank) and the copy rank (Theorem C, for given source and reader spans). **They do not
bound the helper count R, nor the idle and stock costs (the block profile of the helpers),** which is where PR #425
(mutable-basis packets), #433 (split centres) and #442 gained. #425 keeps m at the Theorem B width and the copy rank at
the Theorem C bound (checked in §9); #433 and #442 are not replayed here. The only family-dependent term in Theorem B is the rank of the
corrector span; it equals h − 1 in every family above, and a family with a smaller rank and a cheap decoder would
change the width bound.

## 11. Statement → check

| statement | check (module, function) | pinned facts in `expected.json` |
|---|---|---|
| gx.check1, Thm A, Cor A1/A2, Thm B data, Thm C on three programs | `certs.stage` | `certificates` |
| negative controls (shifted labels, corrupted port) | `certs.controls` | `certificates.p3.controls` |
| toy: 18 → 16, exhaustive optimum, control | `toy.run` | `toy_p3` |
| Theorem P | `pivots.thm_P` | `pivots.thm_P` |
| overlap measurements | `pivots.copy_count`, `pivots.overlap_scan` | `pivots` |
| #425: replay, scalar, Theorem S, controls | `mutable425.run` | `mutable_425` |
| pricing, pivot-free variants, copy/descent units | `pricing.run` | `pricing` |
| neighbourhood ranks, E8 bit dual, ω, 20-clique | `families.*` | `families`, `thmB_table` |
| h = 9 uniqueness, k = 2 planes, calibrations | `sat_e8.*` | `e8_labels` |

## 12. Scope and open points

- The correspondence between the model of §1 and each checker is by reading `gx.py` (E0–E7) and #425's `PROOF.txt` §3;
  there is no mechanical proof of it and no Lean check.
- (B1)–(B2) and (P1)–(P2) are hypotheses about the layout [U].
- Theorem P holds for fixed-role B₂ windows only (§7) and is computed on complex programs; the bit words are not replayed.
- The simulation of Theorem S is checked on #425's word only.
- `inputs/pricing/hist_p10b.json` is a copy of the five-stage histogram that #325's verification writes to `math.json` (a
  run output at head 0eca9340, not a committed file; its `bit_root` is the pinned root the pricer reproduces). It was not
  re-derived from #325's records here.
- Lean: (P1)–(P2) and (B1)–(B2) were read against `Work/Bridge/Net.lean`, `Work/BridgeGeom/Stage.lean` and
  `Work/BridgeGeom/Net.lean` (f010392c); the docstrings and lemma statements are consistent with them, but this is not
  formally verified. Two points are open: whether the backward stages 1 and 3 count as "the same program", and whether the
  stage-j target frames lie in ι_j(q_S)^⊥.
- `inputs/gcert1-p3-cone-R16.json` is a local research program (not published upstream).
