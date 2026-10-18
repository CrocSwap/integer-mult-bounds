# Decoder floors, case (c): the A2 family of non-B-form rank-9 realisations (P112 ≥ 64, #968 P104 ≥ 56, E8 ≥ 72; no κ claim)

**Status: research note. Exact finite computations plus written proofs; not a SAT/DRAT result. No κ claim, no supplier word.**
Only `research/a2-family-decoder-floors/` is added; nothing existing is changed. It works on the `m = 9`, rank-9 case "(c)" of #2338's trichotomy,
but only for **one explicit family of rank-9 realisations**, not for all of case (c) (see "Not covered").

## Claims box (scope is part of the claim)

Setting (the model of #2338 / #2277 / #2724): a unit of lines `V` (`E8`, `P112` = E8 minus an orthogonal frame `F0`, `P104` = E8 minus `F0 ∪ F1`, #968's unit, `F1 = H4`), a **pattern realisation**
`M` (`M_tt ≠ 0`; for `t ≠ s`: `M_ts = 0 ⇔ r_t ⊥ r_s`; "iff pattern") over a field of characteristic 0, the **dense** pairing table `B[t,s] = 1 ⇔ (t = s or r_t ⊥ r_s)` (F2-rank 9, 511 label classes),
and the cost `Σ_j rank_F2 B[R_j, A_j]` of a decoder `M = Σ_j p_j q_jᵀ` with row/column supports `R_j`, `A_j`.

| # | Statement | Scope | Status |
|---|---|---|---|
| **A1** | **The A2 family**: rank-9 iff-pattern realisations of P112, P104, E8 equal to the Gram matrix `G` except on the three rows of one A2 triangle, where row `u_i` is `G` rescaled by one factor on `N̄(u_i) ∩ O_{u_j}` and by another on `N̄(u_i) ∩ O_{u_k}`; 7 parameters plus diagonal scalings (§2) | the three units | PROVEN (construction) + CHECKED (exact members, `a2fam.py`) |
| **A2** | **They are not of B-form** `D₁GD₂ + cβᵀ` (`c_uβ_s = 0` on every orthogonal pair): a counterexample to the B-form conjecture (our working "Conjecture B", never posted) for rank-9 square decoders | generic members (3 random exact members per unit) and the two tie members of S1 | PROVEN (argument, §2.3) from CHECKED (exact / mod-p ranks, `a2cert.py`) |
| **G** | **Theorem G**: if the rows outside a set `X` are Gram rows, a rank-9 pattern realisation is B-form with `supp c ⊆ X`, **or** in the A2 family on an A2 triangle inside `X` (transposed statement for columns) | P112, P104, E8; char K ≠ 2 | PROVEN (§3) from CHECKED span facts S1, S2 (`spans.py`) |
| **E** | **Lemma E**: if `rank M[V∖X, :] ≤ 8` and `V∖X` contains a sub-unit with rank-8 rigidity (#1212 and extensions) and a span condition, the rows off `X` are Gram rows | conditional on the cited rigidity | PROVEN (§3) |
| **F** | **Floors**: every `9`-term (square) decoder of **every** A2-family member, all parameters, all triangles, costs **P112 ≥ 64, P104 (#968's unit) ≥ 56, E8 ≥ 72** (§5) | `m = 9`, rank-9 A2 members, dense `B` | PROVEN from CHECKED (row census parameter-free; column census treats `γ` symbolically; merged-kill fact `mergedkill.py`; exact class-level relaxation `iib_check.py`); corroborated by RECORDED robust CP-SAT runs |
| **S** | **Sharpness**: exact tie decoders of cost **64 (P112)** and **72 (E8)** at the stated special parameter points; generic members reach only 65 / 73 (§6) | the two points | CHECKED (exact over Q) |
| **M** | **`m ≥ 10`, both factors in the realisation's two 9-dimensional spaces** (`P = AX`, `Q = BY`): cost ≥ **68 (P112), 64 (P104), 77 (E8)** (§7) | A2 members **off the B-locus `γ₂ ≠ γ₃`**, any `m ≥ 10`; the B-locus case is **OPEN** (the relaxation drops there to 62 / 58 / 70) | PROVEN from CHECKED (class-level relaxation `iib_check.py` + merged-kill fact); pair tables at members are corroboration only |

The result relies on #2338 (our own PR, open): the model, Theorem P (`P_0`), the exact rank formula; the 8-term floors `P_0 = 64 / 56 / 72` are re-confirmed here by exact branch-and-bound.

### Not covered (stated up front)

* **`m ≥ 10` on the B-locus `γ₂ = γ₃`** (the cocycle locus, B-form members): not claimed. The class-level relaxation drops there to 62 / 58 / 70 (P112 / P104 / E8), below the floors of Theorem F, and the recorded logs exclude the locus. Open.
* **Decoders whose factors leave `col M` / `row M` on an A2 member with `m ≥ 10` are NOT covered** (the catalogue method needs the factors inside the realisation's 9-dimensional spaces). For `m = 10` such decoders are exactly the
  one-sided frame-expansion decoders (§7.3, PROVEN reduction); a heuristic search (§7.3) found only ties, nothing proven. `m ≥ 11` outside the spaces was not analysed.
* **Other rank-9 realisations.** The existence step is open: we do **not** prove that every rank-9 pattern realisation is B-form or A2 ("Conjecture B\*"). Theorem G only says that a rank-9 realisation with Gram rows off a set `X` is one of the two. So the floors above are
  floors for the A2 family and (by the earlier B-form analysis, not part of this package) are *not* a statement about all of case (c). The co-star decoders (Discussion 1267, #1320) are case (c) of #2338; nothing here proves anything about them unless their realisation lies in the family.
* **Non-iff patterns** (zeros allowed on non-orthogonal pairs), `B` of rank ≥ 10, other P104 units, other punctured units.
* The A2 family is shown not to be of B-form; we do **not** claim that it is an irreducible component of the realisation variety (a floating-point tangent-space count, 310 = 81 + 229, points that way; it is not shipped and not claimed).
* Not DRAT-logged. Two things are RECORDED, not re-run (§9): the robust CP-SAT / CEGAR logs and the all-parameter rigidity of the pair tables (special-locus census).

## 1. Setting and notation

`L` = the lines of the unit, root representatives `r_t ∈ Z⁸` (E8 roots, norm 2), `G_ts = r_t · r_s`, `R` the `v × 8` matrix of the `r_t` (rank 8). `O_u = {s : s ⊥ u}`, `N̄[u] = {s : s ⊥̸ u} ∪ {u}`.
A **pattern realisation** `M` is a `v × v` matrix with the iff pattern; `M = ABᵀ` with `A, B ∈ K^{v×ρ}` (rows `a_u`, `b_s`), `ρ = rank M`. The **Gram realisation** is `G` (`ρ = 8`). **B-form** (our working conjecture "B"): `M = D₁GD₂ + cβᵀ`,
`D₁, D₂` diagonal (singular allowed), `c βᵀ` rank one with `c_uβ_s = 0` on every orthogonal pair `(u, s)`.
`E8` is the full 120-line unit; `P112`, `P104` as above (`checks/units_check.py` recomputes sizes and the label dimension 9).

**Square decoders.** Every 9-term decoder `M = PQᵀ`, `P, Q ∈ K^{v×9}`, of a rank-9 `M` is *square*: `P = AX̂`, `Q = BŶ` with `X̂, Ŷ ∈ GL₉`, `X̂Ŷᵀ = I`.
*Proof.* `rank M = 9` forces `rank P = rank Q = 9`, `col P = col M = col A` and `col Q = col B`, so `P = AX̂`, `Q = BŶ`; then `AX̂ŶᵀBᵀ = ABᵀ` and `A, B` injective give `X̂Ŷᵀ = I`. ∎
Write `x_j, y_j` for the columns of `X̂, Ŷ` (dual bases of `K⁹`). A row normal `x` has support `R(x) = {u : a_u · x ≠ 0}`, a column normal `y` has `A(y) = {s : b_s · y ≠ 0}`.

**Exact rank formula (PROVEN; proof inlined).** Dense `B[t,s] = Ω(u(t), u(s))` with `u(t) ∈ F₂⁹` the label of line `t` and `Ω` nondegenerate (`h = 9`, 511 classes, `units_check.py`). For supports `R, A` with label spans `U_R, U_A`,
`B[R,A]` has the rank of `Ω` restricted to `U_R × U_A`, i.e. `rank B[R,A] = dim U_R − dim(U_R ∩ U_A^{⊥Ω})`. The class `O_z = {t : Ω(z,u(t)) = 1}` is *avoided* by `R` iff `z ∈ U_R^⊥`; put `δ(R) = dim U_R^⊥`.
Hence **`rank B[R,A] ≥ 9 − δ(R) − δ(A)`** (Lemma 3.1 of the working notes behind #2338) and the cost of a term depends only on the label classes its supports avoid.
A row normal `x` avoids the class `O` iff `a(O) ⊆ x^⊥`; a normal killing no class behaves as "full support".

## 2. The A2 family

### 2.1 Two facts about A2 in E8 (PROVEN)
(a) The lines of E8 in a 2-plane form a simply-laced rank-≤2 root system (A1, A1×A1 or A2), so at most 3 lines, exactly 3 only for an **A2 triangle** (pairwise non-orthogonal, `r_3 = ±r_1 ± r_2`).
(b) Let `r_1·r_2 = ±1`, `r_3 = ±(r_1 ∓ r_2)`. Every root `r ∉ {±r_1, ±r_2, ±r_3}` is orthogonal to at least one of `r_1, r_2, r_3`. *Proof.* `r·r_3 = r·r_1 ∓ r·r_2`; if `r·r_1, r·r_2 ∈ {±1}` then `r·r_3 ∈ {0, ±2}`, and `±2` forces `r = ±r_3`. ∎
So `V ∖ X = O_{u_1} ∪ O_{u_2} ∪ O_{u_3}` and `O_{u_i} ∩ O_{u_j}` is the same set `E6` of lines orthogonal to the plane `Π = ⟨r_1, r_2⟩` (`a2fam.py` asserts this: 34 / 32 / 36 lines on P112 / P104 / E8).

### 2.2 Construction (PROVEN; CHECKED on instances)
Let `X = {u_1, u_2, u_3}` be an A2 triangle in `L`. Take `g_1 = 0`, `g_2, g_3 ∈ Π` (four parameters `θ = (α₂, β₂, α₃, β₃)`: `g_2 = α₂r_1 + β₂r_2`, `g_3 = α₃r_1 + β₃r_2`), and three numbers `ζ_i`. For `s ∈ O_{u_i}` put `z_s = −g_i · r_s`
(consistent on overlaps because `O_{u_i} ∩ O_{u_j} ⊥ Π ∋ g_i − g_j`), `z_{u_i} = ζ_i`. Rows and columns in `K⁹`:
`a_u = (r_u, 0)` for `u ∉ X`, `a_{u_i} = (r_i + g_i, 1)`, `b_s = (r_s, z_s)`, and `M = ABᵀ` (then `D₁MD₂` for diagonal scalings).
* `M` equals `G` off the three rows `X`.
* For `s ∈ O_{u_i}`: `M_{u_i s} = (r_i + g_i)·r_s + z_s = 0`, an orthogonal pair, as required.
* For `s ∈ N̄(u_i) ∩ O_{u_j}`: `M_{u_i s} = (r_i + g_i − g_j)·r_s`; with `g_i − g_j = a r_i + b r_j` and `r_s ⊥ r_j` this is `(1 + a) G_{u_i s}`: row `u_i` is the Gram row **rescaled by `κ_ij = 1 + a`** on `N̄(u_i) ∩ O_{u_j}` and by `κ_ik` on `N̄(u_i) ∩ O_{u_k}`.
* Pattern (iff): the nonzero conditions are `κ_ij ≠ 0` (i.e. `r_i + g_i − g_j ∉ ⟨r_j⟩`, six open conditions) and `M_{u_iu_i}, M_{u_iu_j} ≠ 0` (open conditions on `ζ`); nothing else changes.
* `M − G` has rank 2 modulo the Gram row space (with `p, q, r` the restrictions of Gram rows to the three parts, `G_{u_1} ≡ p+q`, `G_{u_2} ≡ r+q`, `G_{u_3} ≡ p−r`, so every piecewise rescaling lies in the Gram span plus one vector). That is why six scale factors survive at rank 9.
* `rank M = 9` iff `A` and `B` have rank 9; `A` always does, `B` does unless `z` is a linear function of `r` (an open condition).

`checks/a2fam.py` (exact rationals) builds random members on each unit and asserts: every line off `X` is orthogonal to a line of `X`; the zeros of `M` are exactly the orthogonal pairs and the diagonal is nonzero; `rank A = rank B = 9`; `M = G` off `X`.
Parameter draws that create an extra zero are skipped (they leave the open set).

### 2.3 Not of B-form: exact certificate (argument PROVEN; ranks CHECKED)
**Claim.** For a member with the iff pattern and `rank M = 9`, there is no `M = D₁GD₂ + cβᵀ` with `c_uβ_s = 0` on all orthogonal pairs, if the following CHECKED facts hold (they do for the members tested): (i) the lines non-orthogonal to all of `N̄[u]` are just `{u}`, for every `u`;
(ii) `Σ := {u : rank b(O_u) ≤ 7}` equals `X`, the rows `a_w`, `w ∉ Σ`, span 8 dimensions, and `rank b(⋃_{u∈X} O_u) = 9`; (iii) every `(v−1)`-row submatrix of `M` has rank 9.
*Proof.* Suppose `M = D₁GD₂ + cβᵀ` with these properties. `rank M = 9` forces `rank D₁GD₂ = 8` and `c ∉ col(D₁R)`, so `col M = col(D₁R) ⊕ ⟨c⟩` and likewise `row M = row(D₂R) ⊕ ⟨β⟩`: `c = Aπ`, `β = Bν`.
For `u ∈ supp c` the condition `c_uβ_s = 0` on `O_u` says `ν ∈ N_u := b(O_u)^⊥`. Note `a_u ∈ N_u`.
*Case 1: some `u ∈ supp c` has `dim N_u = 1`.* Then `ν ∝ a_u`, so `β ∝ M[u,:]` with support `N̄[u]`. Every `w ∈ supp c` is non-orthogonal to every `s ∈ supp β = N̄[u]`, so `supp c = {u}` by (i). Then all rows `w ≠ u` of `M` are rows of `D₁GD₂`, rank ≤ 8, contradicting (iii).
*Case 2: all `u ∈ supp c` have `dim N_u ≥ 2`.* Then `supp c ⊆ Σ = X`. The rows off `X` satisfy `a_w·π = 0` (since `c_w = 0`), and they span 8 dimensions, so `π` is unique up to scale and `supp c = supp(Aπ)`; by the computation `supp(Aπ) = X`. Then `ν` annihilates `b(O_u)` for all `u ∈ X`, i.e. `b(⋃_{u∈X}O_u)`, which has rank 9: `ν = 0`, `β = 0`, and `M = D₁GD₂` has rank ≤ 8. Contradiction. ∎
`checks/a2cert.py` verifies (i), (ii), (iii) on three random exact members of each unit (and on the two tie members of §6). Ranks are computed **mod p = 2⁶¹ − 1**, which are lower bounds for the ranks over Q; every inference above uses only lower bounds, or upper bounds that hold by construction
(`dim N_u` computed mod p can only be too large, which enlarges `Σ`, the safe direction). **Not claimed:** the variant without the orthogonal-pair condition on `supp c × supp β`; for special parameters (e.g. the cocycle locus `γ₂ = γ₃` of §5.1, where `M = D₁G + 1_X ζᵀ`) an A2-family member *is* B-form.

## 3. Theorem G and Lemma E

**Span facts (CHECKED, `spans.py`, exact up to the safe mod-p direction).** For `L ∈ {P112, P104, E8}`: **(S1)** `r(O_u)` spans `r_u^⊥` (rank 7) for every `u`; **(S2)** `r(O_u ∩ O_{u′})` spans `⟨r_u, r_{u′}⟩^⊥` (rank 6) for every `u ≠ u′`.

**Theorem G (PROVEN from S1, S2).** Let `L ∈ {P112, P104, E8}`, `M` a rank-9 pattern realisation over `K`, `char K ≠ 2`, `X ⊆ L` with `M[w,:] = d_w (GD₂)[w,:]` for all `w ∉ X` (`D₂` invertible, `d_w ≠ 0`) and `r(L∖X)` spanning `K⁸`. Then
(a) `M = D₁′GD₂ + x z′ᵀ` with `supp x ⊆ X` and `x_u z′_s = 0` whenever `u ⊥ s` (B-form), **or** (b) `X′ := {u ∈ X : M[u,:] ∉ rowspace(GD₂)}` is an A2 triangle and `M` is in the A2 family of §2.2 (with `D₁, D₂` and scalars `x_i` on the three rows; for special parameters it can also be B-form).
*Proof.* `rowspace(GD₂) = rowspace(RᵀD₂)` has dimension 8 and is spanned by the rows off `X`; as `rank M = 9`, `rowspace M = rowspace(RᵀD₂) ⊕ ⟨z⟩`. For `u ∈ X` write `M[u,:] = w_uᵀRᵀD₂ + x_u z` (unique). Zeros of row `u` give `d₂_s(w_u·r_s) + x_u z_s = 0` on `O_u`.
If `x_u = 0` then `w_u ⊥ r(O_u)`, so `w_u ∝ r_u` by (S1) and row `u` is a Gram row; `X′ ≠ ∅` because `rank M = 9`. For `u ∈ X′` put `g_u = w_u/x_u`: `z_s = −d₂_s g_u·r_s` on `O_u`, and for `u, u′ ∈ X′`, `(g_u − g_{u′})·r_s = 0` on `O_u ∩ O_{u′}`, hence by (S2) **`g_u − g_{u′} ∈ ⟨r_u, r_{u′}⟩`**.
*Cocycle lemma.* If `|X′| ≤ 2` or `r(X′)` spans ≥ 3 dimensions, there is `g` with `g − g_u ∈ ⟨r_u⟩` for all `u ∈ X′`. (`|X′| = 1`: `g = g_u`. Otherwise fix `u_1 ≠ u_2`, write `g_1 − g_2 = μr_1 + νr_2` (unique, `r_1, r_2` independent) and put `g := g_1 − μr_1 = g_2 + νr_2`, the unique vector that works for `u_1, u_2`.
For `u_3` with `r_3 ∉ ⟨r_1, r_2⟩`: `g − g_3 ∈ (g_1 − g_3 + ⟨r_1⟩) ∩ (g_2 − g_3 + ⟨r_2⟩) ⊆ ⟨r_1, r_3⟩ ∩ ⟨r_2, r_3⟩ = ⟨r_3⟩`. For `u_3` with `r_3 ∈ ⟨r_1, r_2⟩` use some `u_4 ∈ X′` with `r_4 ∉ ⟨r_1, r_2⟩` and the pair `(u_1, u_4)`, which determines the same `g`, and `r_3 ∉ ⟨r_1, r_4⟩`.)
Given such `g`, put `z′ = z + gᵀRᵀD₂`: it vanishes on every `O_u`, `u ∈ X′`, and `M[u,:] = x_u(g_u − g)ᵀRᵀD₂ + x_u z′` with `x_u(g_u − g) = d₁′_u r_u`: this is (a). Otherwise `|X′| ≥ 3` and `r(X′)` spans a 2-plane, so `X′` is an A2 triangle (§2.1(a)); the rows off `X′` are Gram rows and the rows of `X′` have exactly the form of §2.2. This is (b). ∎
The proof uses no characteristic assumption beyond S1/S2 (rank statements about integer matrices; true over Q, hence over every field of characteristic 0; for characteristic `p` re-run `spans.py` mod `p`). The transposed statement holds for columns.

**Lemma E (PROVEN).** Let `rank M[V∖X, :] ≤ 8` and `L′ ⊆ V∖X` with `M[L′,L′] = D₁GD₂` on `L′` (e.g. a sub-unit where rank-8 rigidity is known: #1212 and its extensions #1389, #1399, #1419, #1425, #1616) and `r(L′)` spanning `K⁸`; assume (S1) for `L` and (S1′) `r(L′ ∩ O_s)` spans `r_s^⊥` for every `s` (a finite check per `(L, L′)`). Then `M[V∖X,:] = D₁G[V∖X,:]D₂` with `D₂` invertible.
*Proof.* Factor `M[V∖X,:] = A′B′ᵀ` in `K⁸`; `a(L′)` spans `K⁸` (as `M[L′,L′]` has rank 8), so take `a_u = d₁_u r_u` on `L′` (the basis change is well defined because `r(L′)` spans and the form is nondegenerate). Each column has `b_s ⊥ r(L′ ∩ O_s)`, so `b_s = d₂_s r_s` by (S1′); `d₂_s ≠ 0` because some `u ∈ L′` is non-orthogonal to `s` and `M_us ≠ 0`. Each row `u ∉ X` has `a_u ⊥ b(O_u) ∝ r(O_u)`, so `a_u ∝ r_u` by (S1), with nonzero factor since `M_uu ≠ 0`. ∎
Theorem G + Lemma E reduce the classification of rank-9 realisations to the *existence* of such a set `X` ("Conjecture B\*"), which is **OPEN** here.

## 4. Catalogue facts for the cost count (CHECKED)

Normal form of a member (GL₉-normalised): `a_u = (r_u, 0)`, `a_{u_i} = (c_i, 1)`, `b_s = (r_s, z_s)` with `c_1 = r_1`, `c_i ∈ Π`, and off `X`: `z_s = −γ_i (r_1·r_s)` on `O_{u_i}` (`γ_1 = 0`); the parameters are `(c_2, c_3 ∈ Π; ζ_1, ζ_2, ζ_3)`. The pattern is equivalent to `c_i − c_j ∉ ⟨r_i⟩ ∪ ⟨r_j⟩` (`i ≠ j`) plus open conditions on `ζ`.
The **cocycle locus** `γ₂ = γ₃` is B-form (`M = D₁G + 1_X ζ′ᵀ`).
`checks/unitcensus.py` (UNIT = P112 | P104 | E8, a triangle chosen by `A2TRI`) recomputes, and `checks/census_facts.py` asserts, for each unit and triangle:
* **(R) rows.** The 63 X-avoiding classes have `rank r(O) = 8`, so their only killer is `e_9` (`R(e_9) = X`). The other row-deficient classes are those with `|O ∩ X| = 1`, or `O ∩ X = X`, and `rank r(O∖X) = 7`: **11 (P112: 8 "survivors" + 3 "triangle classes" `T_i = O_{u_i} ∪ {u_i}`, of 60 lines), 19 (P104: 16 + 3, the triangle classes having 56 lines), 3 (E8: only the triangle classes, 64 lines)**.
  Each has a **1-dimensional nullspace** and the normals are pairwise distinct, so every `x ≠ e_9` kills at most one class (`δ_R ≤ 1`).
* **(S) spans.** For each `u_i`, `r(O_{u_i} ∖ (E6 ∪ X))` spans `r_i^⊥` (rank 7); no line off `X` is non-orthogonal to all of `X`.
* **(C) columns.** For generic `γ` exactly six column classes are killable by a vector `(f, 1)`: the three triangle classes `T_i` and three "merged" classes `M_ij` (`|M ∩ X| = 2`; 52 lines on P112, 48 on P104, 56 on E8); they are co-killable only as the three triples `{M_ij, T_i, T_j}` (a vector killing a triple has a 26-line support on P112), and no other triple is. Each `T_i` has a unique column killer, so a merged `y` is the killer of both of its triangle classes, and at most one merged `y` exists.
  Consequently, off the B-locus, **`δ_A ≤ 1` for every column normal, except for at most one term with `δ_A = 2`** (§5.3(b): two merged classes are co-killable only on `γ₂ = γ₃`, `mergedkill.py`). On the cocycle locus a column normal `y ≠ e_9` kills at most one class, from the same list 11 / 19 / 3.
* **B[X, s] = e_i** for every `s ∈ O_{u_i} ∖ (E6 ∪ X)` (asserted in `floors.py`; convention `B = 1` on orthogonal-or-equal pairs).
* **Triangles.** E8: `W(E8)` is transitive on A2 subsystems. P112: the 204 automorphism generators found (reflections and products of two reflections preserving `L`) merge all **896** triangles into **one orbit** (`orbits.py`); E8: all 1120 in one orbit. P104: the 64 signed permutations found merge the **704** triangles into **≤ 28 orbits**, and `unitcensus.py` + `census_facts.py` are run on **all 28 representatives** (identical structure; logs recorded and compared line for line). Every fact above is invariant under automorphisms of `L`.

## 5. The floors (F)

### 5.1 Row-puncture floors `P_k` (CHECKED)
`P_k` := the minimum cost of an 8-term (square, dimension 8) decoder of the Gram matrix `G` with the rows of `Z ⊆ X`, `|Z| = k`, deleted; a row that is not honest (a non-Gram row, or zero) costs at least as much (supports only grow), so `P_k` bounds every such decoder from below.
`floors.py`: **P112: `P_k = 64, 63, 62, 62` (`k = 0..3`); P104: `56` for all `k`** by exact duality branch-and-bound over the catalogue of deficiency directions (`opt3u.py`; complete because every candidate space is 1-dimensional); **E8: `72, 71, 70, 70`**, by the structural count
(no column-deficient classes; the row-deficient classes of the punctured Gram are exactly `|Z|` classes with 1-dim nullspace and normal `r_i`, `i ∈ Z`; every term costs ≥ 9 except at most `rank{r_i : i ∈ Z}` terms, which cost ≥ 8, so **`P_k ≥ 72 − rank{r_i : i ∈ Z}`**, and `r_1, r_2, r_3` span only 2 dimensions).
`P_0 = 64 / 56 / 72` is #2338's Theorem P for these units.

**Remark (the E8 near-miss).** On E8 the three punctured row classes have normals `r_1, r_2, r_3`, which are dependent (`r_3 = ±r_1 ± r_2`, `floors.py` asserts `rank{r_1, r_2, r_3} = 2`), so at most **two** cost-8 terms fit in one basis: `P_3 = 70`, not `69`.
The count below uses `cost_0 ≥ |T|`, which holds because `B[X, s] = e_i` for the columns used (convention `B = 1` on orthogonal-or-equal pairs; `floors.py` verifies it for the `B` of this package), so `|T| = 3` gives `70 + 3 = 73` and the dependency enters only through `P_k`.

### 5.2 Case I: some `x_{j0} ∝ e_9` (PROVEN from §4)
Duality gives `y_j = (y′_j, 0)` for `j ≠ j0`, and `(x′_j, y′_j)_{j≠j0}` are dual bases of `K⁸`. Normalise `y_{j0} = (y′_0, 1)` and put **`w_i := c_i − y′_0`**. For `j ≠ j0`: the columns are honest Gram columns, rows off `X` are Gram rows and `p_j(u_i) = w_i · x′_j`. Term `j0` has `R_0 = X` and `q_0(s) = −w_i · r_s` on `O_{u_i}∖X`.
Let `T = {i : w_i ∉ ⟨r_i⟩}`. For `i ∈ T` (S) gives `s ∈ O_{u_i}∖(E6 ∪ X)` with `q_0(s) ≠ 0`, i.e. `s ∈ A_0`, and `B[X,s] = e_i`, so **`cost_0 ≥ rank{e_i : i ∈ T} = |T|`**.
For `i, j ∉ T` write `w_i = λ_i r_i`, `w_j = λ_j r_j`: the pattern (`c_i − c_j ∉ ⟨r_i⟩ ∪ ⟨r_j⟩`) forces `λ_i, λ_j ≠ 0`, so those rows are honest scaled Gram rows. The other eight terms form a Gram decoder with `|Z|` rows non-honest, `|Z| = |T|` for `|T| ≤ 1`, `|Z| ∈ {2,3}` for `|T| = 2`, `|Z| = 3` for `|T| = 3`:
`|T| = 0`: ≥ `P_0`; `|T| = 1`: ≥ `1 + P_1`; `|T| = 2`: ≥ `2 + min(P_2, P_3)`; `|T| = 3`: ≥ `3 + P_3`. Totals: **P112 64, 64, 64, 65; P104 56, 57, 58, 59; E8 72, 72, 72, 73** (`floors.py`). So Case I costs **≥ 64 / 56 / 72**, tight for P112 and E8 as a bound.

### 5.3 Case II: no `x_j ∝ e_9`
The split is frame-invariant: (a) some `y_j` has `A_j ⊆ X` (it kills every X-avoiding column class), or (b) no `y_j` does. By (C), (a) can occur only on the cocycle locus (B-form members).
**(a)** (PROVEN). In the cocycle frame `y_{j0} = e_9`, `x_{j0} = (x′_0, 1)`; the other terms have honest Gram rows, and column `u_i` is `(r_i − ζ′_i x′_0)·y′_j`. `A_0 = {u_i : ζ′_i ≠ 0} ≠ ∅` (else `rank M = 8`). Let `Z ⊆ A_0` be the non-honest columns: the `i ∈ A_0` with `x′_0 ∉ ⟨r_i⟩`, plus at most one `i ∈ A_0` with `r_i = ζ′_i x′_0`.
If `x′_0 = 0`: `R_0 = X`, `cost_0 = |A_0| ≥ 1`, total ≥ `1 + P_0`. Otherwise `x′_0` lies on at most one `⟨r_k⟩`; for each `i ∈ A_0` with `x′_0 ∉ ⟨r_i⟩` (S) gives a row `s ∈ O_{u_i}∖(E6∪X)` in `R_0` with `B[s, A_0] = e_i|_{A_0}`, and if `r_k − ζ′_k x′_0 = 0` for `k ∈ A_0`, the diagonal condition `M_{u_ku_k} ≠ 0` says exactly `u_k ∈ R_0`, with `B[u_k, A_0] = e_k|_{A_0}`.
Hence **`cost_0 ≥ |Z|`** and the other eight terms cost ≥ `P_{|Z|}` (column version of §5.1, equal by the symmetry of `G` and `B`): total ≥ `min_k (k + P_k)` = **64 / 56 / 72**.
**(b)** (PROVEN from CHECKED: row census parameter-free; column census treats `γ` symbolically). By (R) and (C) a term's row normal kills at most one deficient class (`δ_R ≤ 1`), and its column normal kills one class, except for merged columns.
The cost of a term depends only on the label classes its two supports avoid (exact rank formula), so it is read from a **class-level table** `f[i][j] = rank_F2 B[R_i, A_j]` for the row direction `i` (one of the 11 / 19 / 3 row-deficient classes, or "full support") and the column direction `j`.
*Column directions.* The eta = 0 killers `S` (8 on P112, 16 on P104, none on E8), the three triangle classes `T_i`, and merged classes `M_ij`. **Merged-kill fact (CHECKED, `mergedkill.py`; P112, E8 and all 28 P104 representatives):** the joint kill system of any two merged classes
(unknowns: one column normal `(f,1)` per class, shared `γ₂, γ₃, ζ₁..ζ₃`, X-column `ζ` conditions included) has solutions only on `γ₂ = γ₃`. Hence **off the B-locus at most one column direction kills any `M_ij`** (a direction killing `M_ij` also kills `T_i, T_j` (the co-killable triples of (C)); `T_i` has a unique killer, so two different `M`'s would share a killer and be killed jointly).
So off the locus the available column directions are `S ∪ T` plus at most one merged class (alone, or merged with the `T_i, T_j` it co-kills); on the locus a column normal kills at most one class and the merged ones are absent.
*Relaxation.* The terms of a square decoder have pairwise non-parallel row normals and column normals (they are dual bases), so each direction is used at most once; the relaxation chooses 9 terms, each direction at most once per side, "full support" unlimited, and minimises the sum of table entries (exact min-cost flow, `iib.py`; it ignores duality and independence, so it only lowers the bound).
Its exact optimum is **off the B-locus 65 (P112) / 62 (P104) / 74 (E8); on the B-locus 66 / 63 / 75** (`iib_check.py`; P112, E8 and all 28 P104 representatives; the case with the single merged class is the minimum).
(The relaxation is not a count of the form `9 − δ_R − δ_A` per term: a survivor row against a single `M` column costs 7, and there are 12 such pairs on P112; allowing them, and ignoring the fact above, the relaxation would reach 63.)

**Theorem F (floors).** *Every 9-term decoder of every A2-family member, at every parameter point and on every A2 triangle, costs at least 64 on P112, 56 on P104 and 72 on E8.* Cases I, II(a), II(b) give `≥ 64, 64, 65` (P112), `≥ 56, 56, 62` (P104), `≥ 72, 72, 74` (E8). ∎ (PROVEN from CHECKED: the census, the merged-kill fact and the class-level relaxation).
`floors.py` re-computes `P_k` and all arithmetic (including the II(b) relaxation); `unitcensus.py`/`census_facts.py` the inputs; `mergedkill.py`/`iib_check.py` the merged-kill fact and the relaxation; `orbits*.py` the triangle coverage. Independent corroboration (RECORDED): a robust CP-SAT / CEGAR search over all parameters in each stratum reports **no square decoder of cost ≤ 63 on P112 and ≤ 71 on E8** (`evidence/logs/hunt-a2/`); at the checked members, exact duality branch-and-bound (`exact_opt.py`, below) gives the same.

## 6. Sharpness (S)

`checks/tie_check.py` re-verifies, with its own inverse, products, pattern (from raw root coordinates), dense `B` and F2 ranks (independent of `a2lib.evaluate`): at the special points below there is a **square decoder of cost exactly 64 (P112) and 72 (E8)**, with `PQᵀ = M` exactly over Q, `M` of rank 9 with the iff pattern.
Parameters are in the convention of §2.2 with `r_1, r_2` the first two lines of the triangle: **P112** `X = (r_1, r_2, r_3) = ((1,0,1,0,0,0,0,0), (1,0,0,0,1,0,0,0), (0,0,1,0,−1,0,0,0))` (lines 0, 4, 25 of `setup9.load('P112')`); **E8** `X = ((1,1,0,0,0,0,0,0), (1,0,1,0,0,0,0,0), (0,1,−1,0,0,0,0,0))` (lines 0, 2, 15 of the E8 list); the decoder (row normals `x_j`; `y_j` the dual basis) is in `data/tie_P112.json`, `data/tie_E8.json`:

| unit | `θ = (α₂, β₂, α₃, β₃)` | `ζ = (ζ_1, ζ_2, ζ_3)` | term costs | total |
|---|---|---|---|---|
| P112 | `(37/6, 0, −11/2, 4/3)` | `(0, 29/2, −33/2)` | `1, 8, 8, 8, 8, 7, 8, 8, 8` | **64** |
| E8 | `(4/3, 0, −11/2, −11/2)` | `(4/3, 0, 3/2)` | `2, 8, 8, 9, 9, 9, 9, 9, 9` | **72** |

The cost-1 (P112) / cost-2 (E8) term is the `e_9` row against a "2-kill" column direction. `a2cert.py tie` certifies both tie members as **not of B-form**, so these are decoders on genuine A2 (non-B) members, not on the cocycle locus. Hence the floors of Theorem F are **attained**.
Generic members: `exact_opt.py` (exact square optimum at one fixed member by duality branch-and-bound over the catalogue, §4) gives **65 (P112, generic member), 64 (P112, tie member), 73 (E8, generic), 72 (E8, tie)**. We claim only that 64 / 72 occur at special parameter points
(a zX-special locus together with conditions on `θ`; the special-locus census is RECORDED) and that the generic members checked reach 65 / 73; we do not claim a full characterisation of where the optimum is 64 / 72, and we do not claim sharpness of the P104 floor 56.

## 7. `m ≥ 10`, factors inside the realisation's spaces (M)

**7.1 Reduction (PROVEN).** Let `P = AX`, `Q = BY` with `X, Y ∈ K^{9×m}`, `XYᵀ = I₉`, `m ≥ 10` (both factors in `col A`, `col B`; any realisation of the family). *Merge lemma:* terms with parallel row normals `x` merge, `p q₁ᵀ + p q₂ᵀ = p(q₁ + q₂)ᵀ`, and `rank B[R, A₁ ∪ A₂] ≤ rank B[R, A₁] + rank B[R, A₂]`, likewise for columns; the cost does not rise.
Repeating, WLOG all row normals are pairwise non-parallel and so are all column normals, `m′ ≥ 9` terms (`m′ = 9` is square: Theorem F). So each catalogue direction is used at most once per side.
**7.2 Pair tables and arithmetic.** The cost of a term is `f[i][j] = rank B[R(d_i), A(e_j)]` for a catalogue row direction `d_i` and column direction `e_j` (or "full support" for a direction killing no class). `pairtable.py` computes the table exactly at a member and solves the relaxation "choose `m′` terms, each real direction at most once" by exact min-cost flow.
**Class-level relaxation (CHECKED, `iib_check.py`; PROVEN from CHECKED).** Same table as §5.3(b) with the `e_9` row (support `X`) added, and the same column directions: off the B-locus `γ₂ ≠ γ₃` at most one merged class (`mergedkill.py`). The exact min-cost relaxation with `m′` terms is monotone in `m′` (dropping a term never raises the cost); at `m′ = 10` it is exactly **68 (P112), 64 (P104), 77 (E8)** (and `+8 / +7 / +9` per further term), attained by the "survivor/`T` columns plus one single `M`" configuration. Hence for `m′ ≥ 10` and **off the B-locus: P112 ≥ 68, P104 ≥ 64, E8 ≥ 77** (P112, E8 and all 28 P104 representatives).
**On the B-locus the relaxation is lower** (cocycle column `A ⊆ X` allowed: 62 / 58 / 70 at `m′ = 10`), the recorded logs exclude the locus, and the `m ≥ 10` case there is **OPEN** (Scope).
Corroboration at members (`pairtable.py`, CHECKED at the members tested, generic and tie members, all off the locus): bounds of at least 64 / 64 / 77 from the member's own catalogue (relaxation values 69 on P112, 65 on P104, 78 on E8 there).
**All parameters** (RECORDED, not re-run): the catalogue is parameter-rigid on the row side (the special-locus census `specall.log`: row-special sets 2 / 4 / 0 on P112 / P104 / E8, columns change only through `ζ`, three mutually exclusive zX-special options, each adding one column direction that kills a 2-dim subspace).
**7.3 What is not covered.** Factors outside `col A` / `col B`. For `m = 10` with `rank P = 10` these are exactly the one-sided frame-expansion decoders (`q_j = B y_j`, each row `u` expands `a_u = Σ_j p_j(u) y_j` in one of several square decoders sharing the other terms): PROVEN reduction (working notes), not shipped.
A heuristic search over such expansions (single-row annealing and whole-class block moves from 60 best square decoders and the E8 tie) found only ties, nothing below, **nothing proven**. `m ≥ 11` outside the spaces and two-sided decoders with `rank > 9` were not analysed.

## 8. Relation to other work, and caveats

* **#2338** (ours, open): the model; Theorem P/R; the `m = 9` trichotomy `(a)/(b)/(c)`. This package treats part of (c): the A2 family, not all of (c). **#2724** (ours, open): case (b); its "Not covered" names this family. **#2639, #2277** (ours): closures and dense-pairing floors for rank-T realisations.
* **#1212** (burntout76, merged) and its extensions #1389, #1399, #1419, #1425, #1616: rank-8 gauge rigidity; #1212 lists rank ≥ 9 as open. Used only to state Lemma E. **#968** (merged): the P104 unit and the 8-term floor.
* **#2321, #2385, #2398, #2515** (open, other authors): one *fixed* rank-9 P112 completion (a column modification of the Gram matrix) under a COPY-power cost; not the A2 family, not the dense-`B` pairing rank. **#1180, #1224, #1320** (merged): the nine-term example, the one-sided normal form, one co-star assignment.
* Not independently re-implemented: the census (`unitcensus.py`) and the branch-and-bound (`opt3u.py`) were written once; `tie_check.py` is an independent evaluator for the tie decoders only. The column census (C) treats `γ` symbolically at generic `γ`; `γ`-special points are covered by the recorded special-locus census (RECORDED, not re-run).

## 9. Labels (every step)

| Step | Label |
|---|---|
| square-decoder normal form; merge lemma; exact rank formula; E6/A2 facts §2.1; construction §2.2 (algebra) | PROVEN (in text) |
| exact members with iff pattern and rank 9 on P112, P104, E8 | CHECKED (exact over Q, `a2fam.py`) |
| non-B-form certificate (i)–(iii) | CHECKED (exact pattern; ranks mod p, safe direction); argument PROVEN |
| S1, S2 | CHECKED (`spans.py`) |
| Theorem G, Lemma E | PROVEN (given S1, S2; Lemma E given cited rigidity) |
| survivors (8 / 16 classes) and survivor-pair ranks (P112 all 8) | CHECKED (`inputs_check.py`) |
| census (R), (S), (C), `B[X,s] = e_i`, triangle orbits (896 / 1120 / ≤ 28 reps, all 28 run) | CHECKED (`unitcensus.py`, `census_facts.py`, `orbits*.py`; recorded logs compared line for line) |
| `P_k` | CHECKED (exact B&B on P112, P104; structural + arithmetic on E8) |
| Case I, II(a) | PROVEN from CHECKED (`floors.py` re-computes the arithmetic) |
| merged-kill fact (two merged classes co-killable only on `γ₂ = γ₃`; P112, E8, 28 P104 reps) | CHECKED (`mergedkill.py`) |
| Case II(b): class-level relaxation 65 / 62 / 74 off the B-locus (66 / 63 / 75 on it) | PROVEN from CHECKED (row census parameter-free; column census treats `γ` symbolically; `iib_check.py`) |
| tie decoders 64 / 72; tie members not B-form; exact optima at fixed members 65 / 64 / 73 / 72 | CHECKED (exact) |
| `m ≥ 10` off the B-locus: class-level relaxation 68 / 64 / 77 | PROVEN from CHECKED (`iib_check.py`, all 28 P104 reps); pair tables at the checked members: CHECKED (corroboration) |
| `m ≥ 10` on the B-locus `γ₂ = γ₃` | OPEN, not claimed |
| all-parameter rigidity of the tables; robust CP-SAT / CEGAR logs; special-locus census | RECORDED (logs shipped, hash-pinned, headline lines asserted, **not re-run**) |
| out-of-space `m ≥ 10`, B\*, the full classification of rank-9 realisations | NOT CLAIMED |

## 10. Verification

`bash research/a2-family-decoder-floors/verify.sh /fresh/dir` (Python ≥ 3.11, `numpy`, `networkx`; one process at a time; no SAT solver, no CP-SAT, no kissat). Steps: 0 manifest (pins every shipped file including the recorded logs); 1 units, S1/S2, survivor classes and survivor-pair ranks; 2 A2 members and the non-B certificate on all three units;
3 census on the first triangle of each unit (identical to the recorded logs), on all 28 P104 orbit representatives, and the triangle-orbit counts; 4 `P_k` and the case arithmetic, the merged-kill fact (`mergedkill.py`) and the class-level relaxation (`iib_check.py`) on P112, P104, E8 and all 28 P104 representatives; 5 the tie decoders (exact), the tie members' certificates and the exact optima at fixed members; 6 pair tables (member-level corroboration of `m ≥ 10`); 7 headline lines of the recorded logs.
The measured transcript is stated in the PR body.

## 11. Files

* `checks/` — `lib.py, lib2.py, common2.py, frames.py, frames_data.py, cert2.py, setup9.py` (the author's library files, as in #2724); `a2lib.py` (unit-generic exact helpers, A2 realisations, evaluator; merged from two working files); `a2fam.py, a2cert.py, spans.py, modrank.py` (A2 construction and certificate, S1/S2); `unitcensus.py, census_facts.py, orbits.py, orbits104.py` (census, triangle orbits); `inputs_check.py` (survivor classes and survivor-pair ranks, as in #2724);
  `floors.py, opt3u.py` (`P_k`, cases); `a2cls.py, mergedkill.py, iib.py, iib_check.py` (class-level catalogue, merged-kill fact, II(b) and `m ≥ 10` relaxation); `tie_check.py, exact_opt.py` (sharpness); `pairtable.py` (`m ≥ 10`, member-level corroboration); `log_counts.py` (recorded logs); `units_check.py, manifest_check.py`.
* `data/` — `p104_frames.json` (the frames `F0`, `F1`), `tie_P112.json`, `tie_E8.json` (the tie decoders, exact rationals).
* `evidence/logs/census/` — recorded unit-census logs (3 units + 28 P104 triangles); `evidence/logs/hunt-a2/` — recorded robust CP-SAT / CEGAR / special-locus logs; `evidence/hunt-a2-scripts/` — the scripts that produced the latter (provenance only: they need `ortools` and the working-card library and are **not** run by `verify.sh`).
* `SOURCES.json` — hashes of each shipped copy and of its working-card source; `MANIFEST.sha256`; `NOTICE.md`; `LICENSE` (Apache-2.0, copied from the repository root).

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0.
