# BSTAR: towards Conjecture B* (rank-9 realisations of the P112 / P104 / E8 iff pattern)

Labels: **PROVEN** (written proof here) · **CHECKED** (exact script in this folder) · **NUMERICAL** (floating point, evidence only) · **OPEN**.
python = W/venv/bin/python; run scripts from this folder. Inputs used: CONJB Theorem G, Lemma E, (S1)/(S2); UNIQ8 Theorem U and §1 coordinates.
Setting: M is a rank-9 pattern realisation on L ∈ {E8, P112, P104} over a field K of char ≠ 2 (iff pattern: M_tt ≠ 0, M_ts = 0 ⟺ t ⊥ s).
Factor M = ABᵀ with rows a_t, b_t ∈ K⁹. ρ_a(S) := dim span a(S), ρ_b(S) likewise. O_u = lines ⊥ u, Nbar(u) = lines not ⊥ u, u excluded.

## §0 Status (BSTAR, Oct 15, final)
**E8 is the primary target** (P120: W(E8)-transitive; per coordinator, all floors are now equivalent to C(P120) ≥ 72). Every result below holds verbatim for E8.
- **Theorem P (pinning), PROVEN (§3).** Fix a P-compatible frame F ⊆ L and put D_F := {u : a_u ∉ span a(F)}. Call a pair {a,b} *unpinned* if, for some sign ε,
  at most one of the three ε-classes at {a,b} (one per F-tetrad through {a,b}) meets L ∖ D_F. If the unpinned pairs form a matching, then
  M[L∖D_F, :] consists of Gram rows, and by CONJB Theorem G **M is B-form (supp c ⊆ D_F) or A2 family (triangle ⊆ D_F)**. The transposed statement uses D′_F and columns.
  P-compatible frames: E8 2025/2025, P112 1260/1260, P104 135/759 (CHECKED, pcompat.py).
- **Theorem A, PROVEN (§4).** Let Σ_a = {u : ρ_a(O_u) = 7} and Σ_b = {u : ρ_b(O_u) = 7}. **If Σ_a or Σ_b contains an orthogonal pair, M is B-form or A2.**
  This covers all of E8 and all of P112: every orthogonal pair lies in a P-compatible frame (CHECKED: 3780/3780 and 3304/3304). For P104 it covers 1404 of 2860 pairs.
- **Lemma 0, PROVEN (§1).** B\* ⟺ some rigid sub-unit L′ (with S1′) has rank M[L′,L′] ≤ 8 (Sylvester).
- **OPEN, the sticking point: Case B.** Here Σ_a and Σ_b are both pairwise non-orthogonal, i.e. cliques of size ≤ 8 (CHECKED: clique number 8). The A2 family and the clique-type B-form (8,8) live here.
  With the transposed Theorem P available, the residue is exactly
  **(K′): if F is a P-compatible frame avoiding Σ_b and D′_F fails Theorem P's condition, then D_F satisfies it.**
  Frames avoiding a clique exist: at least 945 in E8 and at least 384 of the 896 H-compatible frames of P112 (CHECKED). So (K′) ⇒ B\* for E8 and P112.
  NUMERICAL: on all 21 converged samples, every frame avoiding Σ_b has D_F ⊆ Σ_b (hence good in Case B), and D_F is bad iff F meets Σ_b.
  **Why it is still open:** the tetrad-level constraints are Schur (x|_T ≠ 0 ⇒ y|_{T^c} = 0), ∩𝒯y = ∅ (F avoids Σ_b), and both sides bad.
  These admit 3 227 764 (𝒯x, 𝒯y) configurations (kprime.py), so the Schur rule alone is far too weak.
  A proof needs the ε-class-level propagation of the local K³ lemma (§5) from the bad pair {1,2} to the pairs {3,4}, {5,6}, and from there to the tetrads through one endpoint. Not done.
- **P104:** Theorem P and Theorem A apply only through its 135 P-compatible frames (1404 of 2860 orthogonal pairs). Lemma E's H-set route fails for most small deviation sets (§6, §7).
- **No new family found.** All converged samples are B-form with the predicted frame-class structure. A targeted construction against a surviving (K′) configuration is the way to look for a third family (not started).

## §1 Lemma 0 (Sylvester reformulation): PROVEN
For S ⊆ L: rank M[S,S] = rank(A_S B_Sᵀ) ≥ ρ_a(S) + ρ_b(S) − 9. So rank M[S,S] ≤ 8 ⇒ ρ_a(S) ≤ 8 or ρ_b(S) ≤ 8.
Hence, if a rigid sub-unit L′ (Theorem U applies, and r(L′ ∩ O_s) spans r_s^⊥ for all s ∈ L) has rank M[L′,L′] ≤ 8, then rows L′ or
columns L′ span ≤ 8 dimensions. Lemma E (rows or columns) and Theorem G then give B-form or A2. The converse is trivial.
So **B\* fails only if every rigid sub-unit L′ ⊆ L has rank M[L′,L′] = 9.**

## §2 Frame calculus: PROVEN
**Pivot coordinates.** A frame F ⊆ L gives a basis: a_f = e_f, b_f = e_f (after rescaling column f), plus e₉. Then a_u = (α_u, x_u) and
b_s = (β_s, y_s), where supp α_u = T(u) is exactly the F-tetrad of u (α_u(f) = M_uf). Likewise supp β_s = T(s).
For u ⊥ s: α_u·β_s + x_u y_s = 0. M − M[:,F]M[F,F]⁻¹M[F,:] = x yᵀ, with x = x_F, y = y_F (HELPER §1).
D_F = supp x, D′_F = supp y, Z_F = L ∖ D_F ⊇ F. D_F depends only on the hyperplane H_F = span a(F). Frames F′ ⊆ Z_F have H_{F′} = H_F.
**Schur rule.** For complementary F-tetrads T, T^c: x|_T ≠ 0 ⇒ y|_{T^c} = 0. Equivalently, Lemma 1₉: ρ_a(Δ_T) + ρ_b(Δ_{T^c}) ≤ 9.
**(Σ0)** ρ_a(O_u), ρ_b(O_u) ∈ {7, 8}. The upper bound is ρ_a(O_u) + ρ_b({u}) ≤ 9. The lower bound holds because O_u contains 7 orthogonal lines.
**(Σ1)** For f ∈ F: **f ∈ Σ_a ⟺ D_F ⊆ Nbar(f)**. This holds because a(O_f) ⊆ {v_f = 0}, and it spans that hyperplane iff x ≢ 0 on O_f.
  If u ∈ Σ_a, every frame through u has the same hyperplane H_u = span a(O_u) ⊕ ⟨a_u⟩: span a(F∖u) is 7-dimensional and lies in the 7-dimensional span a(O_u).
  Its deviation set lies in Nbar(u).
**(Σ2)** If u, w ∈ Σ_a with u ⊥ w lie in a common frame F, then H_u = H_w = H_F and D_F ⊆ Nbar(u) ∩ Nbar(w).
  That is the set of lines of the three F-tetrads through the pair {u,w}. Three orthogonal lines of Σ_a in F confine D_F to one tetrad, since each triple lies in exactly one tetrad.
  Five orthogonal lines are impossible, since they would give D_F = ∅ and rank 8.
**(Σ3)** For v ∈ D_F: on O_v, y_s = −α_v·β_s / x_v, so b(O_v) is the injective linear image of β(O_v) and ρ_b(O_v) = rank β(O_v).
  So v ∈ Σ_b iff β(O_v) lies in a hyperplane of K⁸.
**(Σ4)** For any frame hyperplane H, every line s with O_s ∩ D_H = ∅ is in Σ_a. Proof: a(O_s) ⊆ H ∩ b_s^⊥, which is 7-dimensional, because H = b_s^⊥ would put a frame inside O_s.

## §3 Theorem P (pinning): PROVEN
**P-compatible frames.** Call F ⊆ L *P-compatible* if every ε-class (4 lines) at every pair of every F-tetrad has ≥ 1 line in L, and every pattern (ε_ab, ε_bc) (2 lines) of every triple of every F-tetrad has ≥ 1 line in L.
H-compatible ⇒ P-compatible. CHECKED (pcompat.py): E8 2025/2025 frames, P112 1260/1260, P104 135/759. These are the only uses of L's missing lines in the proof.
**Statement.** Let F ⊆ L be a P-compatible frame, with Z = Z_F and D = D_F. For a pair {a,b} and sign ε, call {a,b} *ε-pinned* if at least two of the
three tetrads through {a,b} have an ε-class meeting Z. Let 𝒰 be the set of pairs that are not both +pinned and −pinned. If 𝒰 is a matching
(possibly empty), then M[Z, :] = D₁G[Z,:]D₂ with D₂ invertible. By CONJB Theorem G with X = D, M is then **B-form (supp c ⊆ D) or A2 family (triangle ⊆ D)**.
The transposed statement holds with D′_F and columns.
**Proof.** Use pivot coordinates. For u with {a,b} ⊆ T(u) put φ(u) = [α_u(a) : α_u(b)], and for columns ψ(s) = [β_s(a) : β_s(b)]. Both are points of P¹ ∖ {0, ∞}, because the supports are exact.
(i) *Pair pinning.* Let u ∈ Z lie in the ε-class of T_i, and let s be a column of T_j, j ≠ i, with T_i ∩ T_j = {a,b}. Then M_us = α_u(a)β_s(a) + α_u(b)β_s(b), since x_u = 0.
  Also u ⊥ s ⟺ ε_ab(s) ≠ ε (UNIQ8 §1). So ψ(s) = φ(u)^⊥ for every (−ε)-column s outside T_i.
  Let u_i, u_k be such rows in two different tetrads. A (−ε)-column of the third tetrad exists: the class has 4 lines in E8, and P-compatibility (below) leaves at least 1 in L.
  That column forces φ(u_i) = φ(u_k) =: Π_ab(ε), and every (−ε)-column s at {a,b} has ψ(s) = Π_ab(ε)^⊥.
  Π_ab(+) ≠ Π_ab(−): otherwise a +column s of T_j would satisfy M_{u s} = 0 for a +row u ∈ Z of some T_i (i ≠ j), but u, s are not orthogonal.
  So for a pinned pair, ρ_ab(ε) := β_s(b)/β_s(a) depends only on ε = ε_ab(s), and ρ_ab(+) ≠ ρ_ab(−).
(ii) *Triangles.* Take {a,b,c} ⊆ T with all three pairs pinned. The columns of T realise all four patterns (ε_ab, ε_bc), each by 2 lines, and at least one survives H-compatibility.
  ε_ac = ε_abε_bc, and β(c)/β(a) = (β(b)/β(a))(β(c)/β(b)). Write A = ρ_ab(+), A′ = ρ_ab(−), and so on. This gives C = AB = A′B′ and C′ = AB′ = A′B.
  So B² = B′², and since char ≠ 2 and B ≠ B′, B′ = −B. Likewise A′ = −A and C′ = −C. Also ρ_ac(+) = ρ_ab(+)ρ_bc(+).
(iii) *Gauge.* 𝒰 is a matching. So every pinned pair {a,b} lies in a triple whose three pairs are pinned: choose c avoiding the at most two partners of a and b in 𝒰.
  Fix a vertex a₀ and define μ_{a₀} = 1. For b with {a₀,b} pinned put μ_b = ρ_{a₀b}(+). Because 𝒰 is a matching, b₀ is the only vertex with {a₀,b₀} ∈ 𝒰 (if any). Put μ_{b₀} = ρ_{a₀c}(+)ρ_{cb₀}(+), where c is not a₀, b₀ or a partner in 𝒰. Then {a₀,c}, {c,b₀} and every triangle {a₀,c,b}, {c,b₀,b} used below are all-pinned.
  The triangle relation (ii) makes ρ_ab(+) = μ_b/μ_a on every pinned pair. Two applications of (ii) through a third index show this for pairs not containing a₀. The definition of μ_{b₀} is independent of c by the same relation.
  Every tetrad T meets 𝒰 in at most 2 disjoint pairs, so its pinned graph is connected. Hence for every column s: β_s(i) = κ_s σ^s_i μ_i (i ∈ T(s)), κ_s ≠ 0, i.e. **β_s ∝ D_μ r_s**.
  This includes the pairs in 𝒰, via a path of pinned pairs inside T(s). Frame columns are e_f = Gram.
(iv) *Rows.* For u ∈ Z, α_u·β_s = M_us = 0 on O_u ∩ L. Here β(O_u ∩ L) = D_μ r(O_u ∩ L) spans D_μ(r_u^⊥), by (S1) for L (CONJB spans.py).
  So α_u ∝ D_μ⁻¹ r_u, and M_us = λ_u κ_s G_us on Z × L. The vectors r(Z) ⊇ r(F) span K⁸. Theorem G applies with X = D. ∎
**Remarks.** (1) Only the rows in Z and the column vectors β are used. y and D′ never enter. (2) In the A2 family with F avoiding X, and in B-form with F avoiding supp c, we get D = X or supp c, |D| ≤ 13, and the condition holds.
(3) The failure mode is the **star**: F ∋ t, where t carries the deviation. Then D_F ⊇ every line of the seven tetrads through t's coordinate, every pair {i, t} is unpinned, and the coordinate β(t) is twisted.
  NUMERICAL: these are exactly the |D_F| = 52 frames in all samples.

## §4 Theorem A (an orthogonal pair in Σ): PROVEN
Let f₁ ⊥ f₂ in Σ_a, lying in a P-compatible frame F ⊆ L. By (Σ2), D_F ⊆ the lines of T₁ ∪ T₂ ∪ T₃, the three F-tetrads through {1,2}.
An unpinned pair {a,b} needs two tetrads through {a,b} whose ε-class (nonempty in L, by P-compatibility) lies inside D. Only T₁, T₂, T₃ qualify,
and two of them meet exactly in {1,2}. So 𝒰 ⊆ {{1,2}}, which is a matching, and Theorem P gives B-form or A2. Transpose for Σ_b. ∎
CHECKED (hset3.py, hcompat.py): in E8 all 3780 orthogonal pairs lie in frames, and all 2025 frames are H-compatible. In P112, 896 of the 1260 frames are H-compatible,
and they cover 3136 of the 3304 orthogonal pairs. Superseded by pcompat.py: every P112 frame is P-compatible, and all 3304 orthogonal pairs are covered. P104: 1404 of 2860 pairs are covered.
NUMERICAL: the (1,52), (52,1), (13,4), (5,11) and (6,9) samples have orthogonal pairs in Σ_a or Σ_b, so they fall under Theorem A.
The clique type (8,8), the (7,7) sample and the A2 family have both Σ's pairwise non-orthogonal (Case B).

## §5 Case B: what is missing (OPEN), and the evidence
Case B: Σ_a and Σ_b each have no orthogonal pair. Then |Σ_a|, |Σ_b| ≤ 8 (CHECKED: the clique number of the non-orthogonality graph is 8 for E8, P112 and P104).
Some H-compatible frame avoids Σ_b. Each frame meets a clique in ≤ 1 line, so in E8 at most 8·135 = 1080 of the 2025 frames meet it, and in P112 at most 512 of the 896 (CHECKED, cliqueavoid.py).
**Lemma (K), OPEN:** if F avoids Σ_b, then 𝒰_F is a matching. NUMERICAL, stronger: D_F ⊆ Σ_b.
In Case B that rules out any ε-class in D, because an ε-class contains orthogonal pairs, so it gives 𝒰_F = ∅.
(K) ⇒ B\* for E8 and P112. The weaker (K′) of §0 suffices.
Evidence (lemK.py, bad.py, bad2.py; NUMERICAL on the 21 converged samples, all B-form; and orientA2.py, exact A2 instance converted to float):
- Every frame avoiding Σ_b has D_F ⊆ Σ_b, and all such frames lie in one hyperplane class. The dual statement for Σ_a holds too (21/21).
- D_F fails Theorem P's condition iff F ∩ Σ_b ≠ ∅, on every sample tested (5 types).
- B-form: Σ_b = supp c and Σ_a = supp β exactly. A2: Σ_a = Σ_b = X. Frames through X give |D_F| = 52 (stars), and the other frames give D_F = X.
**Where the proof attempt stops.** Schur's rule only controls y on complementary tetrads. A bad pair {1,2} puts x ≠ 0 on two ε-classes (in T₁ = 1234 and T₂ = 1256).
That forces y = 0 on the lines of 5678 and 3478, but y = 0 is needed on all of O_{f₁} (or all of O_{f₂}), which also contains 3456 and four tetrads through 2.
In the pair configuration {1,2}, the vectors (φ, x) and (ψ, y) live in K³, and the local lemma below gives only "row excess at (i, ε) ⇒ column ψ̂ constant on the (−ε)-classes j ≠ i".
The missing ingredient is propagation of that constancy to the pairs {3,4} and {5,6}, and from there to the tetrads through one endpoint.
**Local lemma (pair configuration), PROVEN.** Let U_i = span{(φ_u, x_u) : u in the ε-class of T_i} ⊆ K³ and V_j = span{(ψ_s, y_s) : s in the (−ε)-class of T_j}.
Then U_i ⊥ V_j for i ≠ j. dim U_i = 2 ⇒ V_j = V_k is a single line ⟨v⟩ with U_i = v^⊥. x ≡ 0 on the class ⇒ dim U_i = 1, since otherwise V_j = ⟨e₃⟩ contradicts ψ ≠ 0.

## §6 P104 (OPEN)
No frame of P104 is H-compatible. Every frame F ⊆ P104 has some F-tetrad missing ≥ 2 lines of E8 ∖ L.
Theorem P's steps need: (i) a (−ε)-column in the third tetrad, (ii) all four sign patterns per triple among columns, and (iii) S1 for L (true).
Steps (i)/(ii) can fail where 2 lines of the same pattern are missing. A P104 version must either choose F so that the missing pairs never hit a needed pattern, or use #1399's P104 rigidity. Not attempted.

## §7 CHECKED finite facts (exact integer arithmetic on E8 roots; scripts here)
- hset.py / hset2.py: E8 and P112 minus any single line or any A2 triangle contain an H-set. P104: 32 of 104 lines and 480 of 704 triangles fail.
- hset3.py: E8 minus the 8 lines of any frame-tetrad contains an H-set (9450/9450). P112: 6300 of 7308 do. P104: 28 of 5550 do.
- hset4.py: L minus Nbar(u) ∩ Nbar(w) for u ⊥ w (the (Σ2) set): never contains an H-set. That is why Theorem A goes through Theorem P rather than Lemma E.
- s1p.py: S1′ holds for L′ = L ∖ D for every D tested: single lines, A2 triangles, tetrad line-sets (E8 10690 sets, P112 8316, P104 6358; min rank 7).
- hcompat.py, cliqueavoid.py: H-compatible frame counts, orthogonal-pair coverage, clique number 8, frames avoiding a clique.
NUMERICAL only: orient.py, orient2.py, orientA2.py, lemK.py, bad.py, bad2.py.

## §8 Files
blib.py (E8 lines, units, frames, tetrads w.r.t. any frame), hset*.py, s1p.py, hcompat.py, cliqueavoid.py (CHECKED);
orient*.py, lemK.py, bad*.py (NUMERICAL orientation on MASK-RANK9 / CONJB samples and the exact A2 instance).

## §9 Follow-up on (K′) (coordinator round 2; E8 focus)
- **Sharpened residue, PROVEN reduction.** Theorem P already handles the case where the unpinned-pair set 𝒰_F is a matching. So (K′) is equivalent to
  **(K″): in Case B, if a P-compatible frame F avoids Σ_b, then 𝒰_F has maximum degree ≤ 1.**
  The obstruction is a vertex a with two unpinned pairs {a,b}, {a,c}. This is the "star" mechanism of §3 Remark (3): column coordinate a can twist freely.
- **The Case B hypothesis is essential (infinitesimal, NUMERICAL, inf.py).** Take c generic on E₁ ∪ E₂ (two full +classes at {1,2}). Then F avoids Σ_b, D_F is bad,
  and the first-order solution space has exactly the B-form dimension 14. So these deformations are B-form with f₁, f₂ ∈ Σ_a (Case A). A proof of (K″) must use "Σ_a has no orthogonal pair".
- **Targeted construction: no third family at first order with small row support (NUMERICAL, inf3.py).**
  Setup: first-order rank-9 deformations of the E8 Gram matrix, a_u = (r_u + εV_u, √ε c_u), b_s = (r_s + εU_s, √ε β_s).
  The condition c_uβ_s + r_u·U_s + V_u·r_s = 0 on orthogonal pairs is linear in (β, U, V) for fixed c.
  For every W(E8) orbit type of support S with |S| ≤ 4 (21 types) and both random and all-ones c on S, dim{β} equals the B-form prediction
  dim(col R + ⟨e_t : t ∈ comNbar(S)⟩). The only exception is the A2 triangle, which has 1 extra dimension (12 vs 11): the A2 family, as expected.
  Larger supports tested (8-line tetrad, E₁+E₂, E₁+E₂+E₃, two tetrads): B-form dimension exactly.
  Caveat: c is only defined modulo col R. A third family whose row deviation has no small-support representative is not excluded by this scan.
- **Proof attempt, where it stops.** Bad at {1,2} gives y = 0 on 5678 and 3478 (Schur). The Z′-columns there pin all rows at pairs {3,4}, {5,6} and {7,8} (transposed pinning, PROVEN).
  The step still missing is to show that a second bad pair through 1 (or 2) forces y ≡ 0 on O_{f₁} (or O_{f₂}), i.e. f₁ ∈ Σ_b, using the clique property of Σ_a.
