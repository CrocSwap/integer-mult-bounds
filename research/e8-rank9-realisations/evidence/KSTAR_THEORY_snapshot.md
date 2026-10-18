# KSTAR: closing Case B of Conjecture B* (lemma (K″)) — E8 first, then P112
Labels: **PROVEN** · **CHECKED** (exact script here) · **NUMERICAL** · **OPEN**. Setting and notation: BSTAR/THEORY.md (§2 pivot coordinates, §3 Theorem P, §5 local lemma).

## STATE
- 16:45 KSTAR: started; read BSTAR/CONJB/UNIQ8/ZEROS. Plan: class-level propagation rules from the local K³ lemma + Schur + Σ facts, then a tiny certified kissat step for (K″) on E8.
- 17:20 KSTAR: class-level SAT abstraction (Schur + mixed-class homogeneity + Σ facts) is SAT even for the joint residue (full tetrads in D and D′) → value-level coupling needed. Pivoting to Σ_a ∩ Σ_b ≠ ∅ ⇒ reduces to a 56-line point/line incidence problem; certifying that by kissat.
- 17:50 KSTAR: Theorem S (Σ_a ∩ Σ_b ≠ ∅ ⇒ B/A2) CHECKED for E8 (56-line incidence problem, kissat UNSAT + independent RUP checker). Theorem Σ (Σ_a ≠ ∅ or Σ_b ≠ ∅ ⇒ B/A2) PROVEN from it + Theorem A + span facts (S2), (S3′) CHECKED. (K″) is no longer needed: B* on E8 reduces to excluding Σ_a = Σ_b = ∅.

- 18:45 KSTAR: P112 checks done (112/112 UNSAT+RUP, spans 0 bad); Theorem Σ holds on P112. Advisor fixes applied (antipodes in cocycle, g_u projection). Residue Σ_a=Σ_b=∅ OPEN. Handing back.

- 19:00 KSTAR: round 2 started (residue Σ_a = Σ_b = ∅). E7 recursion scoped and set aside (§4.1). Working on the extremal-frame + twist route; numerical residue probe running (job kstar_probe).
- 19:35 KSTAR: P¹-valued pinning SAT model (pin.py: equalities of pair ratios, ORTH/NON/TRI/K³/ZZ/Schur + residue + both sides non-Gram) is SAT (pin1.out: x on the 11 tetrads not through {1,2}, y on the 3 tetrads avoiding {1,2}). Corrected the round-1 joint-pinning 'only if'. Generic residue probe killed (too slow on efficiency cores); running a targeted numerical realisability test of pin1's support pattern (job kstar_cfg).
- 20:05 KSTAR: **residue killed (pending certificate).** P¹-valued pinning model + ratio rules (pin.py, §7) is UNSAT on E8 with residue + both sides non-Gram (kissat < 100 s); SAT without either hypothesis (sanity); 0 clause violations on true data of A2 and B-form instances over many frames incl. stars (soundtest.py). DRAT + rup.py certificate running (job kstar_cert). P112 frame 0 also UNSAT.
- 20:55 KSTAR: **Theorem R CERTIFIED on E8.** kissat 4.0.4 (--factor=false --preprocessfactor=false, so no extension variables) DRAT proof pin3.drat (163 MB) checked by rupc.c, an independent forward RUP checker that honours deletions and rejects RAT: "VERIFIED: top-level conflict after 2 382 724 lemmas (2 761 873 deletions)", 890 s. (The first proof used kissat's default factor/BVA with new variables, and rupc rejected it as "var out of range". Hence the flags.) rupc also re-verifies s56 and rejects a bogus empty-clause proof. **So B* holds on E8, PROVEN modulo two CHECKED finite steps (s56 incidence, pin3 UNSAT), each with an independent certificate.** P112: frames 0, 2, 26 (one per orbit of 2⁸:AGL(3,2)) are running in job kstar_cert2 (log jobs/kstar_cert2.log; frame 0 had already been UNSAT by plain kissat); soundtest rerun is queued in the same job.

## §0 Status
- **Round 2: Theorem R (§7), the residue Σ_a = Σ_b = ∅ is empty on E8. Together with S and Σ this gives Conjecture B\* on E8: every rank-9 iff-realisation is B-form or A2.**
  Reduction PROVEN; finite step = one kissat UNSAT on a sound Boolean model (pin.py), CERTIFIED by rupc (STATE 20:55). P112: Theorem R running on the 3 frame orbits (job kstar_cert2; frame 0 UNSAT, uncertified).
- **Theorem Σ (E8), PROVEN (§2), using Theorem S (CHECKED, §1), BSTAR Theorem A, CONJB Theorem G, spans (S2) and (S3′) (CHECKED).**
  If Σ_a ≠ ∅ or Σ_b ≠ ∅, then M is B-form or in the A2 family. This covers Case B whenever either Σ is nonempty, with no use of (K″).
- **P112: Theorem Σ also holds (CHECKED, §3).**
- **Residue for B\* on E8 and P112: Σ_a = Σ_b = ∅** (every b(O_u) and every a(O_u) spans 8 dims). OPEN, see §4.
- Every known rank-9 realisation has Σ ≠ ∅ (B-form: Σ_a ⊇ supp β, Σ_b ⊇ supp c; A2: Σ_a = Σ_b = X).

## §1 Theorem S: Σ_a ∩ Σ_b ≠ ∅ ⇒ B-form or A2 (E8). Reduction PROVEN, finite step CHECKED
Let f₁ ∈ Σ_a ∩ Σ_b and take any frame F ∋ f₁ (pivot coordinates, BSTAR §2). By (Σ1) on both sides, x ≡ 0 and y ≡ 0 on O_{f₁}.
(i) *Everything off index 1 is Gram-shaped.* For a pair p = {j,k} ⊆ {2..8} the three tetrads through p are T_a, T_b (avoiding 1) and T_c ∋ 1.
Rows of T_a, T_b are in Z and their columns in Z′, so every orthogonal pair (u,s) at p with u or s in T_a ∪ T_b has M̃_us = M_us = 0.
The row-column graph of BSTAR §3 (i) is connected, so all rows and all columns at p are pinned, Π_p(+) ≠ Π_p(−) (witness: a +row of T_a against a +column of T_b).
Triangles ⊆ {2..8} lie in one tetrad whose columns realise all 4 patterns, so BSTAR §3 (ii)–(iii) give a gauge μ on {2..8}.
Hence α_u|_{T(u)∖1} ∝ D_μ⁻¹σ^u and β_s|_{T(s)∖1} ∝ D_μσ^s for all u, s; lines avoiding 1 are Gram rows and columns.
(ii) *The 56-problem.* Choose representatives with σ₁ = +1 on the 56 lines of Nbar(f₁). Rescale e₁ freely. Write α_u(1) = κ_u p_u, x_u = κ_u x̂_u, P_u = (p_u, x̂_u),
and Q_s = (q_s, ŷ_s) for columns. For u, s ∈ Nbar(f₁): M_us = κ_uκ′_s (g_us − 1 + P_u·Q_s), g_us = Σ_{T(u)∩T(s)} σσ′ = 2 r_u·r_s.
All other entries are Gram (×κκ′) except row f₁ (M_{f₁s} = κ′_s q_s) and column f₁ (M_{uf₁} = κ_u p_u). So the only constraint left is
**P_u·Q_s = 1 whenever u ⊥ s (u, s ∈ Nbar(f₁))**. Projectively P̂_u = (P_u, 1) is a point and Q̂_s = (Q_s, −1) a line of P²(K), incident whenever u ⊥ s.
(iii) *Finite step (CHECKED, s56.py + rup.py; W(E8) is transitive on lines so one f₁ suffices; run for f₁ = lines 0–15, identical 4863-lemma proofs: jobs/kstar_s56_E8.log).* Encode equality of points (resp. lines) by Boolean variables with transitivity,
plus the incidence axiom "two distinct points have at most one common line" (and dually), applied to every pair of rows u, u′ and every pair of common Γ-neighbours.
Negate the conclusion: "no point class A₀ meets Γ(s) for every column s, and no line class B₀ meets Γ(u) for every row u" (Γ = orthogonality inside Nbar(f₁);
|Γ(u)| = 27, common neighbours 10 (u ⊥ u′), 16 (r_u·r_{u′} = 1), 0 (antipodes)). kissat: UNSAT; the DRAT proof (4863 lemmas) is re-verified by rup.py,
an independent 90-line RUP checker (tested to reject a bogus empty-clause proof and a satisfiable formula). The abstraction only keeps necessary conditions, so UNSAT is sound.
(iv) *Conclusion.* Say A₀ = {u : P_u = P₀} meets Γ(s) for every s ∈ Nbar(f₁). Then P₀·Q_s = 1 for all such s, so every row of A₀ is a Gram row
(M_us = κκ′g_us for all s, M_{uf₁} = κ_u p₀). Rows of O_{f₁} are Gram rows. With X := {f₁} ∪ (Nbar(f₁) ∖ A₀) the rows off X are Gram rows (D₂ = diag(κ′) with entry p₀ at f₁),
and r(L ∖ X) ⊇ r(O_{f₁}) ∪ {r_u} (u ∈ A₀) spans K⁸. CONJB Theorem G gives B-form or A2. The case B₀ is the transpose. ∎

## §2 Theorem Σ: Σ_a ≠ ∅ ⇒ B-form or A2 (E8). PROVEN
Let f₁ ∈ Σ_a and F ∋ f₁ any frame. By (Σ1), x ≡ 0 on O_{f₁}, i.e. D := D_F ⊆ Nbar(f₁). D ≠ ∅, otherwise rank ≤ 8.
(i) *Columns are Gram-shaped off index 1.* As in §1 (i), but using rows only (BSTAR Theorem P (i)): at p = {j,k} ⊆ {2..8} the rows of T_a, T_b are in Z, so every column at p is pinned
(old Theorem P sense), with a nonzero witness from a Z-row; triangles and gauge as before. So β_s|_{T(s)∖1} ∝ D_μσ^s. Rescale columns: b_s = (D_μ r_s, y_s) for s ∈ O_{f₁}.
(ii) *Remark (not used below).* Rows of O_{f₁} are Gram: α_u(1) = 0 and x_u = 0, so (D_μα_u, 0)·r_s = 0 for s ∈ O_u; since r_u has no f₁-component, (S1) gives α_u ∝ D_μ⁻¹r_u.
(iii) *Rows through 1.* Let u ∈ Nbar(f₁) and E6_u := O_u ∩ O_{f₁}. For s ∈ E6_u: α_u·D_μ r_s + x_u y_s = 0 (coordinate 1 does not meet s).
If u ∈ D this says y_s = g_u·r_s on E6_u, with g_u := proj_{f₁^⊥}(−D_μα_u/x_u) (only the projection matters, since r_s ⊥ f₁ on E6_u).
(iv) *Cocycle.* For u, u′ ∈ D: (g_u − g_{u′})·r_s = 0 on E6_u ∩ E6_{u′}. Let w_u := proj_{f₁^⊥} r_u. Antipodes (r_ū = f₁ − r_u) have E6_u = E6_ū and w_ū = −w_u.
**(S3′) CHECKED (spans3.py):** for u, u′ ∈ Nbar(f₁) not equal or antipodal, r(O_{f₁} ∩ O_u ∩ O_{u′}) spans ⟨r_{f₁}, r_u, r_{u′}⟩^⊥ (all 1512 pairs). With (S2) for antipodes,
g_u − g_{u′} ∈ ⟨w_u, w_{u′}⟩ for all u, u′ ∈ D. **(W2) CHECKED (spans3.py):** the 56 vectors w_u give 28 directions and no 3 of them lie in a 2-plane.
Apply the cocycle lemma of CONJB Theorem G to one representative per direction: with ≤ 2 directions its first case applies; with ≥ 3 directions, (W2) says no direction lies in the plane of two others, so its exceptional branch never occurs. This gives g ∈ f₁^⊥ with g − g_u ∈ ⟨w_u⟩ for each representative; for an antipode ū ∈ D, g_u − g_ū ∈ ⟨w_u⟩ by (S2) (E6_u = E6_ū spans ⟨f₁,u⟩^⊥), so g − g_ū ∈ ⟨w_ū⟩ too.
Since w_u ⊥ r_s on E6_u, **y_s = g·r_s on ∪_{u∈D} E6_u.**
(v) *Dichotomy.* Case 1: every s ∈ O_{f₁} is orthogonal to some u ∈ D. Then y = g·r on O_{f₁}, so b(O_{f₁}) ⊆ {(D_μρ, g·ρ) : ρ ∈ f₁^⊥} has dimension ≤ 7, i.e. f₁ ∈ Σ_b.
  Theorem S applies. Case 2: some s ∈ O_{f₁} has O_s ∩ D = ∅. By (Σ4), s ∈ Σ_a. Then f₁ ⊥ s are both in Σ_a, and BSTAR Theorem A applies. ∎
The transposed statement (Σ_b ≠ ∅) follows by symmetry (Theorem S and Theorem A are symmetric).
**Remark.** This is the mechanism BSTAR's (K″) was after: a star at f₁ makes f₁ a deviation line. (K″) itself is not needed.

## §3 P112: Theorems S and Σ hold verbatim (CHECKED)
The proofs of §1–§2 use only: frames through every line inside L, P-compatibility (pinning at pairs avoiding index 1, the P ≠ Q witness, all 4 patterns per triple),
(S1), (S2_L) r(O_{f₁} ∩ O_u ∩ L) spans ⟨f₁,u⟩^⊥, (S3′_L) the triple version inside L, (W2) (a property of directions, inherited by subsets), Theorem A and Theorem G for L,
and the finite step §1 (iii) on the 52 lines Nbar(f₁) ∩ L. All P112 frames are P-compatible (BSTAR pcompat.py), Theorem A covers all P112 orthogonal pairs, Theorem G holds for P112.
CHECKED (job kstar_p112, jobs/kstar_p112.log): spansL.py P112, (S2_L) and (S3′_L) for every f₁ ∈ P112: 151648 span checks, 0 bad; runall.sh P112: §1 (iii) UNSAT + RUP-VERIFIED for all 112 choices of f₁.
So **Theorem Σ holds on P112**: Σ_a ∪ Σ_b ≠ ∅ ⇒ B-form or A2. The same residue Σ_a = Σ_b = ∅ remains (OPEN).

## §4 The residue Σ_a = Σ_b = ∅ (OPEN)
Then every a(O_u) and b(O_u) spans 8 dims: a(O_u) spans b_u^⊥ and b(O_u) spans a_u^⊥, and this pairing is nondegenerate (its kernel would be ⟨a_u⟩, but a_u·b_u ≠ 0), so M[O_u, O_u] is a rank-8 realisation of the E7 pattern (Gram rank 7, plus one) for every u.
**This residue is where a third family would have to live. It is far from Gram (Gram has Σ_a = L), so BSTAR's first-order scan (inf3.py) says nothing about it.**
Consequences (PROVEN): for every frame F, D_F and D′_F meet O_s for every line s (Σ4), and Theorem P fails on both sides (otherwise Theorem G gives B-form or A2, and both have Σ ≠ ∅;
in B-form supp β ⊆ Σ_a). So every frame has a star in 𝒰_F and in 𝒰′_F.
**Class-level combinatorics cannot close it (CHECKED, kenc3.py):** Schur + mixed-class homogeneity (§5) + (Σ4) domination + stars on both sides is satisfiable,
e.g. x full on 11 tetrads and y full on 5 (k3.out). Value-level coupling is needed. Suggested route: the E7 recursion (B\* for rank-8 E7 realisations would give
M[O_u,O_u] B-form/A2 for every u, and the E7 Σ-lines then lift to E8 Σ-lines), or an anchor argument like §2 with D ∩ O_{f₁} small instead of empty.

### §4.1 Why the E7 recursion is not a short route (scoping, round 2)
- In E7 = O_{f₁} each pair {j,k} ⊆ {2..8} lies in only two tetrads (the third tetrad through {j,k} contains 1). Theorem P (i) needs three:
  two rows in different tetrads are equated through a column of the third. So neither rank-7 E7 rigidity nor an E7 Theorem P comes from the existing cards.
- Even a full E7 classification does not lift: an E7-Σ line v of the slice O_u means a(O_u ∩ O_v) spans 6 inside b_u^⊥ ∩ b_v^⊥ (7-dim).
  That says nothing about ρ_a(O_v) in K⁹, so a gluing argument across all 120 slices would still be needed.
- The E7 residue (all E7-Σ empty) recurs one level down. The recursion only pays if it bottoms out in something computable, and that chain is unscoped.

## §5 Side results (PROVEN)
- **Mixed-class homogeneity.** At a pair p, sign ε, if the row class R^ε_{T_i}(p) contains a Z-row and a D-row, then dim U_i = 2, so V_j = V_k = ⟨v⟩ (BSTAR §5 local lemma):
  the columns of C^{−ε}_{T_j} ∪ C^{−ε}_{T_k} are all multiples of one vector v, hence all in Z′ (e₃ ∈ U_i) or all in D′. Transposed likewise.
  An all-Z row class has dim U_i = 1 (constant φ).
- **Joint pinning (sharper Theorem P), corrected in round 2.** M̃ = M − xyᵀ has the correct zero pattern off D × D′. At (p, ε) the rows of R_1 ∪ R_2 ∪ R_3 are pinned
  to one value iff the bipartite graph (edges R_i–C_j, i ≠ j, orthogonal, not both in D × D′) joins them. Sufficient: every C_j^{−ε} has a Z′ column
  (each such column is adjacent to all rows of the other two tetrads). So if D′ contains no full ε-class, all rows are pinned, the gauge argument of Theorem P (ii)–(iii)
  applies to rows, columns in Z′ are Gram, and transposed Theorem G gives B-form or A2. (The round-1 "only if R_i ⊆ D and C_j ∪ C_k ⊆ D′" was wrong:
  pin1.out has rows of T₁ in Z, rows of T₂, T₃ in D, columns of T₁ in Z′, columns of T₂, T₃ in D′, and the graph splits into two components.)
- **The SAT abstraction of (K″)** (kenc.py/kenc2.py: Schur + homogeneity + Σ facts + Case B + F avoiding Σ_b + star) is satisfiable (k1.out, k2.out), so (K″)
  cannot be proved at the class level either. Theorem Σ bypasses it.

## §6 Files
Round 2: pin.py / pinL.py (P¹-valued pinning model; UNIT, FRAME env), soundtest.py (rule soundness on true data), p112orb.py (P112 frame orbits: 28 + 336 + 896, reps 0, 2, 26),
rupc.c (independent forward RUP checker in C, deletions honoured, RAT rejected; also re-verifies s56), certjob2.sh, num/probe.py and num/cfg.py (NUMERICAL, inconclusive: did not converge).

s56.py (56-problem CNF; UNIT=E8|P112), rup.py (independent RUP checker), runall.sh (kissat + RUP for every f₁), spans3.py (S3′, W2 on E8, sympy exact),
spansL.py (S2_L, S3′_L mod 2³¹−1, ranks are at their maxima so exact), kenc.py, kenc2.py, kenc3.py, dec.py (class-level SAT abstractions; negative results).

## §7 Round 2: the residue Σ_a = Σ_b = ∅ is empty (E8). Rules PROVEN, finite step CHECKED (certificate: see STATE)
**Theorem R.** On E8 there is no rank-9 iff-realisation with Σ_a = Σ_b = ∅. With Theorems S, Σ: **every rank-9 iff-realisation on E8 is B-form or in the A2 family (Conjecture B\* for E8).**
*Reduction (PROVEN).* Fix any frame F (W(E8) is transitive on frames, so frames()[0] suffices) and pivot coordinates. Call the rows *Gram-shaped* if for every pair p = {a,b} ⊆ F
the ratio ρ_p(u) = α_u(b)/α_u(a) takes one value on rows with ε_p = + and a different value on rows with ε_p = −. Then BSTAR §3 (ii)–(iii) (all triples, rows of a tetrad realise
all four patterns) give a gauge with α_u ∝ D_μ⁻¹σ^u; for s ∈ Z′ (y_s = 0), β_s ⊥ α(O_s), and (S1) gives β_s ∝ D_μ r_s, so the columns Z′ ⊇ F are Gram columns and
transposed Theorem G gives B-form or A2. Columns likewise (columns Gram-shaped ⇒ rows Z Gram ⇒ Theorem G). B-form and A2 both have Σ ≠ ∅
(B: a line of supp β has c ≡ 0 on its O, so it is in Σ_a; A2: z is linear on O_{u_i}, so u_i ∈ Σ_b). So the residue forces: **neither rows nor columns are Gram-shaped**, and by (Σ4)
(H_F ≠ b_s^⊥ since no line is orthogonal to all of F) **D and D′ meet O_s for every line s.**
*Boolean model (pin.py).* Variables: x[u] (x_u ≠ 0), y[s]; for each pair p, equality of the values ρ_p(u) (rows) and τ_p(s) := −β_s(a)/β_s(b) (columns), all in K*; for each index i,
equality of rat_i(u) := x_u/α_u(i) (rows with x ≠ 0) and of y_s/β_s(i) (columns). Transitivity throughout. Since α_u|_p·β_s|_p = α_u(a)β_s(b)(ρ_p(u) − τ_p(s)), each rule below is a one-line proof:
- ORTH: u ∈ T_i, s ∈ T_j (T_i ∩ T_j = p), u ⊥ s: x_u y_s = 0 ⇒ ρ = τ; x_u y_s ≠ 0 ⇒ ρ ≠ τ (M_us = 0). NON: same sign at p (not orthogonal): x_u y_s = 0 ⇒ ρ ≠ τ.
- TRI: in a tetrad ⊇ {a,b,c}: ρ_abρ_bc = ρ_ac and τ_abτ_bc = −τ_ac. So row-row (col-col): two equalities ⇒ the third; row-col: two equalities ⇒ the third is unequal (char ≠ 2).
- K³ (BSTAR §5 local lemma): two rows of R^ε_{T_i}(p) with (φ, x) independent (ρ differs, or one has x = 0 and the other not) ⇒ dim U_i = 2 ⇒ V_j = V_k = ⟨v⟩: all columns of
  C^{−ε}_{T_j} ∪ C^{−ε}_{T_k} have equal τ and equal y-status. ZZ: two x = 0 rows of one class have equal ρ (else V ⊆ ⟨e₃⟩, ψ = 0). Transposed versions.
- D1: if C^{−ε}_{T_j} ∪ C^{−ε}_{T_k} contains two independent (ψ, y) (τ differs, or a y = 0 and a y ≠ 0 column), then dim U_i = 1: the class rows are multiples of one (P, ξ), so
  equal ρ_p, equal x-status, and equal rat_a, rat_b (a, b ∈ p).
- TW: rows u, w of T in a common 1-dim class at p = {a,b} and at the complementary pair {c,d}, x ≠ 0: equal rat_a and rat_c, hence ρ_ac(u) = ρ_ac(w). (Subsumed by the next two once encoded.)
- RATIO: rat_a/rat_b = ρ_ab, so two of {rat_a eq, rat_b eq, ρ_ab eq} ⇒ the third. Common partner: u ∈ R^ε_{T_i}, w ∈ R^ε_{T_k}, s ∈ C^{−ε}_{T_j} ({i,j,k} = {1,2,3}), x_u x_w y_s ≠ 0 and ρ_p(u) = ρ_p(w):
  φ_u = λφ_w gives x_u = λx_w, so rat_a, rat_b equal. Transposed versions for columns.
- Schur; rank 9 (x, y ≢ 0); residue (D, D′ meet every O_s); "rows not Gram-shaped" and "columns not Gram-shaped" (a pair p and two rows with equal sign and different ρ, or opposite sign and equal ρ).
*Result (CHECKED).* kissat 4.0.4 with `--factor=false --preprocessfactor=false --no-binary`: UNSAT on pin3.cnf (56 784 vars, 3 513 012 clauses, frames()[0]).
pin3.drat (163 MB) is kept; it can be regenerated deterministically with exactly these flags (the default flags add bounded-variable-addition variables, which rupc rejects).
rupc pin3.cnf pin3.drat → "VERIFIED: top-level conflict after 2 382 724 lemmas". Every lemma up to that point was RUP-checked; after it, F ∧ lemmas already derives ⊥ by unit propagation.
So the proof is complete, not truncated.
**Audit targets:** (a) the reduction "Gram-shaped ⇒ B/A2 ⇒ Σ ≠ ∅"; (b) the rule proofs above (TRI row-column sign, D1, common partner); (c) rupc.c. Suggested: rerun soundtest.py with fresh seeds and rupc on pin3. Sanity: SAT with residue dropped, SAT with "not Gram-shaped" dropped.
*Soundness test (soundtest.py, NUMERICAL check of the rules, not part of the proof):* every clause (residue and non-Gram clauses off) is satisfied by the true Boolean data of
an exact E8 A2 instance and two B-forms (single-row; 8-clique), on random frames including star frames (|D| = |D′| = 56): 0 violations.
*How the earlier models failed and what kills them.* pin1.out (x on the 11 tetrads not through {1,2}, y on 3456, 3478, 5678) dies by TW: at {3,4} and {5,6} the 3456 rows are
twisted (x = t α(3) on each ε₃₄-class, x = t′α(5) on each ε₅₆-class), forcing equal ρ₃₅ on two rows of opposite ε₃₅, which the Z′ columns of 1357 and 2358 separate.
pin2.out (x, y on 1357, 2358, 2367, 2457) dies by RATIO: x/α(5) is constant on 1357, so ρ₃₅ cannot depend on ε₃₅.
