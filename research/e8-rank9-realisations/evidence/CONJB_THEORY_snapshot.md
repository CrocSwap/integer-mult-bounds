# CONJB: rank-9 realisations of the P112 / P104 / E8 orthogonality pattern

Labels: **PROVEN** (written proof here) · **CHECKED** (exact script in this folder) · **NUMERICAL** (floating point, evidence only) · **OPEN**.
python = W/venv/bin/python; run scripts from this folder. Setting: MASK-RANK9 §0/§4 (Conjecture B), UNIQ8 Theorem U (= special case of #1212).
"Pattern" = the full iff pattern: M_tt ≠ 0, and for t ≠ s, M_ts = 0 ⟺ t ⊥ s. G = Gram matrix of the chosen root representatives r_t.
O_u = lines of L orthogonal to u; Nbar[u] = lines not orthogonal to u (u included).

## §0 Status (CONJB, Oct 15)
- **Conjecture B is FALSE as stated (CHECKED, exact).** On P112, P104 and E8 there are rank-9 pattern realisations that are not
  D₁·G·D₂ + c βᵀ for any diagonal D₁, D₂ (singular allowed) and any rank-one c βᵀ with no orthogonal pair in supp c × supp β (generic parameters; for special parameters an A2-family member can be B-form, Theorem G(b)). The "no orthogonal-pair condition" variant is supported by the audit's restricted-D numerical test only, not certified.
  They form the **A2 family** (§1): Gram everywhere except the three rows of one A2 triangle {u₁,u₂,u₃}, and row u_i is the Gram row
  rescaled by one factor on Nbar(u_i) ∩ O_{u_j} and by a different factor on Nbar(u_i) ∩ O_{u_k}. Exact certificate: a2cert.py (§1.3).
  NUMERICAL (not proven): at these points the tangent space of the realisation variety has dimension 310 = 81 (GL9) + 229 (family dimension,
  a2dim.py), with singular-value gap 1e0 against 1e-14 (a2tang.py). So numerically the A2 family is locally a whole component, not a degenerate
  limit of B. The random-start searches of MASK-RANK9 did not reach it.
- **Theorem G (one-sided classification), PROVEN (§2), using CHECKED span facts (spans.py).** If the rows outside some set X are
  Gram rows (M[L∖X, :] = D₁G[L∖X, :]D₂ with D₂ invertible and r(L∖X) spanning K⁸), then M is of B-form with supp c ⊆ X and no
  orthogonal pair in supp c × supp β, **or** M is in the A2 family on an A2 triangle inside X. The transposed statement holds for columns.
  The A2 triangle is the only obstruction. It arises because the only line sets spanning a 2-plane are A1, A1×A1 and A2.
- **Lemma E (extension), PROVEN (§3).** "Rows off X are Gram rows" follows from rank M[L∖X, :] ≤ 8 when L∖X contains a sub-unit
  L′ on which rank-8 rigidity is known (#1212 / UNIQ8 Thm U and the swarm's extensions #1389 #1399 #1419 #1425 #1469 #1474 #1616 #1650),
  provided r(L′ ∩ O_s) spans r_s^⊥ for every s ∈ L. This is a finite check per (L, L′).
- **Corrected conjecture B\* (OPEN).** Every rank-9 pattern realisation on P112 / P104 / E8 has a row set or a column set of corank ≤ 8
  whose complement contains a rank-8-rigid sub-unit. Equivalently, by Theorem G + Lemma E, every such realisation is B-form or A2 family
  (rows or columns). The gap is the existence step: find X with rank M[L∖X, :] = 8. The "shared extra direction" of the tetrad spans
  (MASK-RANK9 §4) is one route to it. Evidence: §4. I do not have a proof of the existence step.
- **What this means downstream (MASK9 case (c)).** The decoder analysis of rank-9 realisations must also cover the A2 family, which has
  no rank-one biclique term. Its deviation from Gram has rank 2 (§1.2), supported on 3 rows. Case A/C of MASK-RANK9 §1–§2 do not apply
  as written. Decoder costs on this family were not computed here.
- **Prior art.** No swarm PR classifies rank ≥ 9 realisations (searched Oct 15: "rank 9", "rank nine", "rank-nine realisation",
  "masked correction rank nine", "A2 triangle", "piecewise"). #1212 states rank ≥ 9 as open. #2277 excludes "realisations of rank above T".
  #2021 is a different object (two-column rank-two corrections). #1212's frame-pivot method is rank-8 specific (K = ¼K[:,F]K[F,:]).
  At rank 9 it gives K = K[:,F]K[F,F]⁻¹K[F,:] + x yᵀ (§5), which is where any proof of B\* would have to start.

## §1 The A2 family
### §1.1 Two facts about A2 in E8 (PROVEN)
(a) The lines of E8 in a 2-dimensional plane form a simply-laced rank ≤ 2 root system: A1, A1×A1 or A2. So there are at most 3,
    and exactly 3 only for an A2 triangle (pairwise non-orthogonal).
(b) Let r₁, r₂ be roots with r₁·r₂ = 1 and r₃ = r₁ − r₂. Every root r ∉ {±r₁, ±r₂, ±r₃} is orthogonal to at least one of r₁, r₂, r₃.
    *Proof.* r·r₃ = r·r₁ − r·r₂. If r·r₁, r·r₂ ∈ {±1}, then r·r₃ ∈ {0, ±2}, and r·r₃ = ±2 forces r = ±r₃. ∎
    So L ∖ X = ∪_i (O_{u_i}), and the three sets O_{u_i} ∩ O_{u_j} all equal the E6 of lines orthogonal to the triangle.

### §1.2 Construction (PROVEN, and CHECKED on instances)
Let X = {u₁,u₂,u₃} be an A2 triangle in L. Take g₁ = 0 and g₂, g₃ ∈ span(r₁, r₂). For s ∈ O_{u_i}, set z_s = −g_i·r_s. This is
consistent on overlaps, because O_{u_i} ∩ O_{u_j} ⊥ span(r₁, r₂) ∋ g_i − g_j. Choose z on X freely. Put a_u = (r_u, 0) and
b_s = (r_s, z_s) for u ∉ X, and a_{u_i} = (r_i + g_i, 1). Then M = ABᵀ has rank ≤ 9, and M equals G off rows X. On s ∈ O_{u_i},
M_{u_i s} = r_i·r_s + g_i·r_s + z_s = 0. On s ∈ Nbar(u_i) ∩ O_{u_j}, M_{u_i s} = (r_i + g_i − g_j)·r_s.
Here g_i − g_j ∈ span(r₁, r₂), and r_s ⊥ r_j, so this is κ_{ij}·G_{u_i s} with a scalar κ_{ij}. That is the piecewise rescaling.
M − G = (rows X) has rank 2 modulo the Gram row space. Proof: with p, q, r the restrictions of Gram rows to the three parts,
G_{u₁} ≡ p+q, G_{u₂} ≡ r+q, G_{u₃} ≡ p−r, so every piecewise rescaling lies in the Gram span plus one vector. This is why
6 scale factors survive at rank 9. General D₁, D₂ are added by diagonal scaling.
a2fam.py builds exact rational instances. For P112, P104 and E8 it checks, for 3 random parameter choices per unit, that the zeros of M
are exactly the orthogonal pairs and that rank M = 9.

### §1.3 Not of B-form: exact certificate (CHECKED, a2cert.py; argument PROVEN)
Suppose rank M = 9 and M = D₁GD₂ + c βᵀ with c_uβ_s = 0 on orthogonal pairs. Write M = ABᵀ with rows a_u, b_s ∈ K⁹.
Then col M = col(D₁R) ⊕ ⟨c⟩, so c = Aπ and β = Bν for some π, ν. For u ∈ supp c, β vanishes on O_u, so ν lies in
N_u := b(O_u)^⊥. Let Σ := {u : dim N_u ≥ 2}. There are two cases.
- **Some u ∈ supp c has dim N_u = 1.** Then ν ∝ a_u, so β ∝ M[u, :], which has support Nbar[u]. supp c must avoid every line
  orthogonal to some line of Nbar[u]. CHECKED: for every line of P112, P104 and E8 that leaves only u. So c = c_u e_u, and the
  rows L∖{u} of M are rows of D₁GD₂, which has rank ≤ 8. CHECKED: every 111-row (103-, 119-row) submatrix has rank 9. Contradiction.
- **supp c ⊆ Σ.** Then the rows off Σ lie in π^⊥. CHECKED: they span exactly 8 dimensions, so π is unique up to scale, and
  supp(Aπ) = X. Then ν annihilates b(∪_{u∈X} O_u). CHECKED: rank 9, so ν = 0, so β = 0. Contradiction.
Ranks are computed mod p = 2⁶¹−1. Those are lower bounds for the rational ranks, and every inference above uses only lower bounds, or
upper bounds that hold by construction. The pattern check is exact over Q. Output: P112 Σ = X = {0,4,25}; P104 {0,3,22}; E8 {0,2,15}.

## §2 Theorem G (one-sided classification): PROVEN
**Span facts (CHECKED, spans.py, exact).** For L ∈ {P112, P104, E8}: (S1) r(O_u) spans r_u^⊥ for every u.
(S2) r(O_u ∩ O_{u′}) spans ⟨r_u, r_{u′}⟩^⊥ for every u ≠ u′.

**Theorem G.** Let L ∈ {P112, P104, E8}, and let M be a rank-9 pattern realisation on L over a field K with char K ≠ 2. Let X ⊆ L
be such that M[w, :] = d₁_w (G D₂)[w, :] for all w ∉ X, with D₂ invertible, d₁_w ≠ 0, and r(L∖X) spanning K⁸. Then one of the following holds:
(a) M = D₁′ G D₂ + x z′ᵀ with supp x ⊆ X and x_u z′_s = 0 whenever u ⊥ s (B-form, D₁′ = D₁ off X);
(b) X′ := {u ∈ X : M[u, :] ∉ rowspace(G D₂)} is an A2 triangle, and M is in the A2 family of §1.2 (with D₁, D₂ and scalars x_i on the three rows). M can also be B-form
    here, but only for special parameters.
*Proof.* rowspace(G D₂) = rowspace(Rᵀ D₂) has dimension 8 and is spanned by the rows off X. Since rank M = 9, rowspace M = rowspace(RᵀD₂) ⊕ ⟨z⟩.
Write M[u, :] = w_uᵀRᵀD₂ + x_u z for u ∈ X; this is unique, since Rᵀ has full row rank. The zeros of row u give d₂_s(w_u·r_s) + x_u z_s = 0 for s ∈ O_u.
If x_u = 0, then w_u ⊥ r(O_u), so w_u ∝ r_u by (S1), and row u is a Gram row. X′ is nonempty because rank M = 9.
For u ∈ X′ put g_u = w_u / x_u. Then z_s = −d₂_s g_u·r_s on O_u. For u, u′ ∈ X′ this gives (g_u − g_{u′})·r_s = 0 on O_u ∩ O_{u′},
so **g_u − g_{u′} ∈ ⟨r_u, r_{u′}⟩** by (S2).
*Cocycle lemma.* If |X′| ≤ 2, or r(X′) spans at least 3 dimensions, there is a g with g − g_u ∈ ⟨r_u⟩ for all u ∈ X′.
For |X′| = 1 take g = g_u. Otherwise fix u₁ ≠ u₂. Write g₁ − g₂ = μr₁ + νr₂, which is unique since r₁, r₂ are independent.
Then g := g₁ − μr₁ = g₂ + νr₂ is the unique vector that works for u₁ and u₂. Take u₃ with r₃ ∉ ⟨r₁, r₂⟩.
Then g − g₃ ∈ (g₁ − g₃ + ⟨r₁⟩) ∩ (g₂ − g₃ + ⟨r₂⟩) ⊆ ⟨r₁, r₃⟩ ∩ ⟨r₂, r₃⟩ = ⟨r₃⟩.
Now take u₃ with r₃ ∈ ⟨r₁, r₂⟩. By hypothesis some u₄ ∈ X′ has r₄ ∉ ⟨r₁, r₂⟩, and g works for u₄ by the previous step.
The pair (u₁, u₄) determines g uniquely in the same way, and r₃ ∉ ⟨r₁, r₄⟩, because ⟨r₁, r₂⟩ ∩ ⟨r₁, r₄⟩ = ⟨r₁⟩ and r₃ ∦ r₁.
Applying the previous step to the pair (u₁, u₄) gives g − g₃ ∈ ⟨r₃⟩.
Given such a g, put z′ = z + gᵀRᵀD₂. Then z′ vanishes on every O_u with u ∈ X′, and M[u, :] = x_u(g_u − g)ᵀRᵀD₂ + x_u z′.
Here x_u(g_u − g) = d₁′_u r_u, so this is (a). The condition x_u z′_s = 0 on orthogonal pairs is automatic.
Otherwise |X′| ≥ 3 and r(X′) spans a 2-plane, so X′ is an A2 triangle by §1.1(a). Rows off X′ are Gram rows, and rows u ∈ X′ have exactly
the form a_u = (d₁_u r_u + x_u g_u, x_u), b_s = (d₂_s r_s, z_s) of §1.2. Normalise g₁ = 0 by replacing z with z + g₁ᵀRᵀD₂. This is (b). ∎
**Remark (fields).** The proof uses no characteristic assumption beyond (S1)/(S2). Those are rank statements about integer matrices,
CHECKED mod 2⁶¹−1, hence true over Q and so over every field of characteristic 0. For a field of characteristic p, re-run spans.py mod p.

## §3 Lemma E (rank 8 on a row set ⇒ Gram rows): PROVEN
Let rank M[L∖X, :] ≤ 8, and let L′ ⊆ L∖X be such that M[L′, L′] = D₁GD₂ on L′ (for example, L′ a unit where rank-8 rigidity is proven)
and r(L′) spans K⁸. Assume (S1) for L, and (S1′): r(L′ ∩ O_s) spans r_s^⊥ for every s ∈ L. Then M[L∖X, :] = D₁G[L∖X, :]D₂ with D₂ invertible.
*Proof.* Factor M[L∖X, :] = A′B′ᵀ in K⁸. a(L′) spans K⁸ (M[L′, L′] has rank 8), so we may take a_u = d₁_u r_u on L′.
Each column s satisfies b_s ⊥ r(L′ ∩ O_s), so b_s = d₂_s r_s by (S1′). d₂_s ≠ 0 because some u ∈ L′ is non-orthogonal to s and M_us ≠ 0.
Each row u ∉ X satisfies a_u ⊥ b(O_u) = r(O_u) (rescaled), so a_u ∝ r_u by (S1), and the factor is nonzero since M_uu ≠ 0. ∎
Applying Theorem G then needs only the existence of X (Conjecture B\*, §0).

## §4 Evidence and checks
- **Census (NUMERICAL, census.py) on MASK-RANK9's 15 converged realisations (all B-form).**
  Σ := {u : dim span b(O_u) = 7} equals supp c exactly: the clique type has 8, and the other types have 5, 6, 13 and 1.
  The rows off Σ span 8 dimensions, and in every case with |Σ| ≥ 2 the N_u (u ∈ Σ) meet in exactly ⟨ν⟩.
  (sol_rand_7 / 24 and sol_sparse_1 / 6 are unconverged, with orthogonal residual up to 2e-3, and are excluded.)
  In the A2 family Σ = X, but the N_u meet in 0. That is the certificate of §1.3.
- **Theorem G hypotheses on the B samples.** MASK-RANK9/ana6.py found the rows off supp c in Gram form on all 15.
- **New random-start search (NUMERICAL, search.py seed 7, 40 starts, jobs/conjb_search.log).** 6 starts reached rank 9, and all 6 are
  B-form by the classifier, which finds a side with rank b(∪O_u) ≤ 8. Their (|supp c|, |supp β|) are (7,7), (1,53) ×2, (8,8) ×2, (5,10).
  The other 34 starts collapsed to rank 8. Random starts do not reach the A2 component. Saved as sol_7_*.npy.
- **Sonnet helper (HELPER.md; excess.py, pivot.py, switch.py).** On the 15 B samples, the 5-dim tetrad spans share one direction
  (NUMERICAL). It also has a frame-switch lemma (hand proof, M_ee ≠ 0). The frame-pivot Schur complement is rank one on all 1260 frames.
  These are tools for the existence step of B\*. They do not bear on the A2 counterexample, where the shared direction exists but ν does not.
- **Audit (Sonnet, independent, read-only).** PASS on §1.1, §1.2 (re-ran a2cert.py on P112 and E8, and spans.py), §1.3, §2 (cocycle
  lemma) and §3. It also ran an independent numpy check on E8: with D free on X, M − D₁GD₂ has σ₂ ≈ 40 (no rank-one fit).
  Three §0 wording fixes were applied: generic parameters only, the "without the orthogonal-pair condition" claim dropped, and the
  NUMERICAL tag kept. One Lemma E step is now spelled out: the basis change is well defined because r(L′) spans and the form is nondegenerate.

## §5 What a proof of B\* has to do (OPEN, scoped)
- Pivot on a frame F ⊆ L (#1212's method): M = M[:, F]M[F, F]⁻¹M[F, :] + x yᵀ with x_F = y_F = 0. For F-complementary blocks T, T^c,
  x|_T = 0 or y|_{T^c} = 0, from zeros alone. The two-term equations become α_u(a)β_s(a) + α_u(b)β_s(b) = −x_u y_s.
  B\* asks for a frame-independent hyperplane. In B-form it is π^⊥ = span a(L ∖ supp c), and in the A2 family it is the Gram row span.
  The frame pivot gives the hyperplane U_F, which is the right one only when F avoids supp c (and when F avoids X for A2).
- The tetrad route (MASK-RANK9 §4, "all 5-dim U_T share one extra direction") is **false for the A2 family as a route to B**, but it can
  still give the existence step. In the A2 family the extra direction is shared (the a-side hyperplane is the Gram span). What fails is
  the second half: no ν with the support condition.
- **Non-iff patterns (STRAYS case (c), zeros allowed on non-orthogonal pairs).**
  - Theorem G uses "non-orthogonal ⇒ nonzero" only through d₁_w ≠ 0, d₂ invertible, and M_uu ≠ 0. (S1)/(S2) are statements about roots,
    so with extra zeros the theorem still holds whenever its hypothesis holds.
  - Lemma E uses non-orthogonal entries only to get d₂_s ≠ 0 and a_u ≠ 0. With singular D (the K_λ case) it fails as stated.
  - The §1.3 certificate uses the exact pattern (supp β = Nbar[u] in case 1).
  - Theorem U itself needs the iff pattern. #1212 removes that need by a DRUP zero-exclusion, but only for its listed units and at rank 8.
  - With M_tt = 0 allowed, nothing here transfers.

## §6 Files
a2fam.py (exact A2 construction; UNIT=P112|P104|E8), a2cert.py (non-B certificate, exact pattern + mod-p ranks), a2tang.py and a2dim.py
(NUMERICAL tangent / family dimension 310 = 81 + 229), spans.py (S1/S2 CHECKED), census.py (NUMERICAL per-line census of the
MASK-RANK9 samples), modrank.py (GF(p) rank), search.py (NUMERICAL random-start search + classifier).
