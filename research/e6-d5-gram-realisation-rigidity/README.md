# E6 is locally rigid at the Gram point; D5 is not rigid, but every rank-5 D5 realisation keeps the floor 20 (#2277 OQ4)

**Status: research note (scoped result). No κ claim, no supplier change, no
frontier unit.** This note addresses open question 4 of #2277 ("E6 / D5
realisation-free: rigidity of the Gram point and global uniqueness at rank `T`
are open"). The **D5 half is answered at rank `T`.** D5 has no rank-4
realisation. Its rank-5 realisations are *not* unique up to scaling, since they
form an irreducible 55-dimensional family, which is 16 dimensions more than the
scaled-Gram orbit. Even so, every one of them keeps #2277's dense floor 20. The
**E6 half is answered locally.** The Gram point is a smooth point whose only
local component is the scaling orbit. Global uniqueness for E6 and rank-5
realisations of E6 remain open.

## Setting (from #2277 §1, §5, §7)

A **realisation** of a unit with lines `r_1..r_v` is `M ∈ K^{v×v}` with
`M_tt ≠ 0` and `M_ts = 0` whenever `r_t ⊥ r_s`. Let `V_U` be the variety of
realisations of rank `≤ T` (`T = dim span r_t`) and `G` the Gram matrix. The
**scaling orbit** `{D₁ G D₂}` (invertible diagonal `D₁, D₂`) lies in `V_U`
and has dimension `2v − 1`. #2277 proves E6 `≥ 36` and D5 `≥ 20` (dense
pairing, factors in `col M` / `row M`, any number of terms) for the scaled-Gram
realisations `D₁ G D₂` only; E6 and D5 have no `T`-frame (`α_⊥ = 4`), so its
realisation-free Lemma 5.2 certificate gives nothing for them. #2277 §5 opens
with "Fix a unit with a T-frame", but the proofs of the Theorem 4′ inequality and
of the Lemma 5.1 rank invariance use only an F₂ rank factorisation of `B_d` and
the term count from `N = Σ x_j y_jᵀ`; only Lemma 5.2 uses the frame. Theorem C
below uses only Theorem 4′, Lemma 5.1, Lemma OC and the Theorem 7.4 count, so it
applies to D5 despite the missing frame.

"Cost" and "floor 20" throughout mean #2277's algebraic decoder cost
`Σ_j rank_F₂ B_d[R_j, A_j]` only. As in #2277's scope, this excludes copy,
hosting, restoration and every supplier or assembly cost, so the floor is not a
complete multiplication cost.

## Results

| unit | v | T | `dim T_G V_U` (exact) | scaling orbit `2v−1` | verdict at `G` |
|---|---|---|---|---|---|
| **E6** | 36 | 6 | **71** | 71 | smooth point; local component = scaling orbit (**locally rigid**) |
| **D5** | 20 | 5 | **55** | 39 | not rigid: every rank-5 realisation is edge-supported (Theorem D), i.e. a scaling of an explicit **16-parameter non-Gram family** or a boundary point of it; no rank-4 realisation (Theorem E); floor 20 everywhere |
| E7 (control) | 63 | 7 | 125 | 125 | locally rigid |
| E8 (control, `--e8`, ~140 s) | 120 | 8 | 239 | 239 | locally rigid (not new: subsumed by #1212 Theorem 1, global uniqueness up to the torus on P120 = E8) |
| D6 (control) | 30 | 6 | 84 | 59 | smooth; edge family realises all 25 extra directions |
| D4 (control) | 12 | 4 | 44 | 23 | edge family gives only 9 of the 21 extra directions (rest not integrated here) |

Every entry of the `dim T_G V_U` column is certified exactly: a prime-rank upper
bound matched by an explicit lower-bound span (E6, D5, E7, E8, D6), or an exact
`Fraction` rank (D4). The D4 family-plus-orbit span 32 is also an exact
`Fraction` rank. The new results are E6 (local rigidity), D5 (Theorems B–E) and
the D6/D4 controls; E7 is a first-order control, and E8 only re-confirms
#1212.

**Theorem A (E6 local rigidity) — PROVEN from CHECKED data.** The Zariski
tangent space of `V_E6` at `G` has dimension 71. Hence `G` is a nonsingular
point of `V_E6`, the only irreducible component through `G` is the closure of
the scaling orbit, and there is a Zariski-open neighbourhood `W ∋ G` in `V_E6`
with `W ⊆ {D₁ G D₂}`. In particular every rank-6 realisation of E6 close enough
to `G` (Zariski, or Euclidean over `R`/`C`) is scaled-Gram, so #2277 Theorem 7.3
(E6 `≥ 36`) applies to it.

*Proof.* At a rank-`T` point the determinantal variety is smooth with tangent
`{dX Yᵀ + X dYᵀ}` (`G = X Yᵀ`, `X, Y ∈ K^{v×T}` of rank `T`), so
`T_G V = {dX Yᵀ + X dYᵀ : entries on ordered orthogonal pairs vanish}`. The
map `(dX, dY) ↦ dX Yᵀ + X dYᵀ` has kernel `{(XA, −YAᵀ)}` of dimension `T²`.
`verify.py` builds the 540 × 432 integer system and finds rank 325 modulo
`p = 1000003` and `p = 998244353`; since `rank_p ≤ rank_Q`, the solution space
has dimension `≤ 432 − 325 = 107`, so `dim T_G V ≤ 107 − 36 = 71`. The `2v`
vectors `E_tt G`, `G E_ss` lie in `T_G V` and have prime rank 71, so they span
71 dimensions over `Q`. The orbit is a 71-dimensional irreducible subvariety of
`V` through `G`, so `71 ≤ dim_G V ≤ dim T_G V = 71`. A local ring whose
dimension equals its tangent dimension is regular, hence a domain, so exactly
one component passes through `G`. It contains the orbit closure and has the
same dimension, so it equals that closure. Torus orbits are open in their
closures. ∎
The count is reproduced in a second coordinate model: E6 as the E8 lines in
doubled coordinates orthogonal to two roots at 120°, using `#2277`'s
convention, with 36 vectors in `Z⁸` of rank 6. Ambient components orthogonal
to the span add a known kernel.

**Theorem B (D5 is not rigid; explicit family) — PROVEN, CHECKED.** For
parameters `a_ij, b_ij ∈ K^*` with `a_ij + b_ij ≠ 0` (one pair per edge
`{i, j}` of `K₅`), put
```
x_{ij+} = e_i + a_ij e_j,   x_{ij-} = e_i − b_ij e_j,
y_{ij+} = e_i + b_ij⁻¹ e_j, y_{ij-} = e_i − a_ij⁻¹ e_j,   M(a,b) = X Yᵀ.
```
Then `M(a,b)` is a rank-5 realisation of D5. Lines with disjoint support give
0. For the same edge, opposite signs give `1 − a·a⁻¹ = 0` and
`1 − b·b⁻¹ = 0`. The diagonal entries are `1 + a/b` and `1 + b/a`, both
nonzero. `M(1,1) = G`. At three explicit rational points (`D5_POINTS` in
`verify.py`), `M` has 240 ordered pairs that violate the scaled-Gram invariant
`M_ts M_st G_tt G_ss = G_ts² M_tt M_ss`, so `M ≠ D₁ G D₂`. The Gram parameters
give 0 violations, which is the control. The tangent space has `dim T_G V_D5 = 55`
(the upper bound comes from the prime rank). The 20 parameter derivatives
together with the 40 scaling directions span 55 dimensions, which is the lower
bound. So `G` is a smooth point with local dimension 55. Near `G`, every rank-5
realisation has the form `D₁ M(a,b) D₂`, because the inverse function theorem
applies to `(a, b, D₁, D₂) ↦ D₁ M(a,b) D₂`. The family has `16 = 20 − 4`
parameters modulo the coordinate torus `e_i ↦ d_i e_i`.

**Theorem C (the D5 floor 20 survives on the whole family) — PROVEN from
CHECKED data, using #2277's Theorem 4′ and the argument of its Theorem 7.4.**
Take any member `M(a,b)` and any decoder with `p_j = X x_j`, `q_j = Y y_j`
(`col P ⊆ col M`, `col Q ⊆ row M`, every square decoder) under the dense
pairing. Its cost is at least 20, and the coordinate decoder `p_a = X e_a`,
`q_a = Y e_a` attains 20.
*Proof.* The columns of `e_i+e_j` and `e_i−e_j` in `B_d` coincide, so every
one of the 31 classes is a union of `±` edge pairs (CHECKED). **Lemma S:**
`span{x_t : t ∈ O} = span{e_i : i covered by the edges of O}`, and the same
holds for `y`. This follows because `x_{ij±}` span `⟨e_i, e_j⟩` iff
`a + b ≠ 0`, and `y_{ij±}` span it iff `(a+b)/(ab) ≠ 0`. Only the 5 axis
classes (all 12 lines avoiding a vertex `a`) miss a vertex (CHECKED). So in
every member the π- and κ-deficient classes are exactly the 5 axis classes,
with annihilator `e_a`. Also `R(e_a) = A(e_a) = {lines through a}`. Both facts
are identical to the Gram case. By #2277 Lemma 5.1 the term ranks are therefore
the same: matched 4, unmatched 3, one deficient 4, none 5 (CHECKED). Since
`M = X I Yᵀ` with injective `X`, `Y`, we get `Σ_j x_j y_jᵀ = I_5` under the
standard pairing. The proof of #2277 Theorem 7.4 then goes through verbatim; its
core combinatorial fact, that no three pairs satisfy `b_i = a_j`, is
re-checked. ∎
Theorem D below shows that this family, together with its boundary, contains
*every* rank-5 realisation and not just those near `G`.

**Theorem E (D5 has no realisation of rank 4) — PROVEN (written proof).**
Every realisation of D5 therefore has rank `≥ 5`, which improves the frame
bound `α_⊥ = 4`.
*Proof.* Write `M = P Qᵀ` (`P, Q ∈ K^{20×ρ}` of rank `ρ`). Let `W_e` and
`U_e` be the spans of the `p`- and `q`-rows of the two lines on an edge `e`.
Each is 2-dimensional because the 2×2 block of the two orthogonal lines is
diagonal and invertible. For disjoint edges `W_e ⊥ U_f`. The four lines of two
disjoint edges form a 4-frame, so their `p`-rows are independent, and likewise
their `q`-rows. Now let `ρ = 4` and take any edge `ij` with complementary
vertices `k, l, m`. Then `W_ij` is 2-dimensional and lies in `U_kl^⊥`, which is
also 2-dimensional, so `W_ij = U_kl^⊥ = U_km^⊥ = U_lm^⊥`. Hence
`U_kl = U_km = U_lm =: U`. Since `W_ik ⊥ U_lm = U` and `W_jl ⊥ U_km = U`, the
4-dimensional space `W_ik ⊕ W_jl` (from the 4-frame `{ik±, jl±}`) lies in the
2-dimensional `U^⊥`, a contradiction. ∎

**Theorem D (every rank-5 realisation of D5 is edge-supported) — PROVEN
(written proof); construction CHECKED on 5 instances.** If `rank M = 5`, there
are dual bases `f_a`, `g_a` (`f_a·g_c = δ_ac`) with `p_t ∈ ⟨f_i, f_j⟩` and
`q_t ∈ ⟨g_i, g_j⟩` for every line `t` on edge `ij`. Equivalently,
`M = X Yᵀ` with `x_t, y_t` supported on the edge of `t`, `x_{ij±}` a basis of
`⟨e_i, e_j⟩`, `y_{ij+} ⊥ x_{ij−}` and `y_{ij−} ⊥ x_{ij+}`. This is the
closure of the family of Theorem B, with boundary points such as
`x_{01+} = e_0`. The realisation variety of D5 is therefore irreducible of
dimension `60 − 5 = 55`, consistent with the tangent count.
*Proof* (notation as in Theorem E, `ρ = 5`, complements taken in the five
vertices).
(i) Suppose `U_ij = U_ik = U_jk = U` for a triangle `ijk` with complement
`lm`. Then `W_il ⊥ U_jk` and `W_jm ⊥ U_ik`, so the 4-frame `{il±, jm±}` lies
in the 3-dimensional `U^⊥`, which is impossible. Also `W_e ⊥ U_lm` for every
edge `e ⊂ ijk`. Hence `dim U_ijk = dim W_ijk = 3`, `W_ijk = U_lm^⊥`, and
`W_ab = U_cde^⊥`; dually `U_ab = W_cde^⊥`.
(ii) At a vertex `a`, any two planes `W_ak`, `W_al` meet in exactly a line.
They meet in at least a line because both lie in the 3-dimensional `W_akl`.
They meet in at most a line because `W_ak ∩ W_al = (U_lrs + U_krs)^⊥`, and that
sum contains the 4-frame span `U_lr ⊕ U_ks`.
(iii) No three of the `W_ak` lie in one 3-space `Z`. Otherwise the three
triangle spans `U_T` (with `W_ak = U_T^⊥`) would all contain `N = Z^⊥`. Any two
of these spans are distinct, because their sum contains a 4-frame span such as
`U_24 ⊕ U_13`. Their pairwise intersections are therefore the shared edge
planes, so this gives
`U_14 = U_24 = U_34 = N` (written for `a = 0` and `k = 1, 2, 3`). Then
`W_012 = W_013 = W_023 = N^⊥` by (i), and this 3-space would contain the
4-frame span `W_01 ⊕ W_23`.
(iv) Lines in `P⁴` that pairwise meet and of which no three are coplanar all
pass through one point. So `L_a := ∩_k W_ak` is a line. If `L_a = L_b`, it would
lie in `W_ac ∩ W_bd` for a 4-frame `{ac±, bd±}`, so the `L_a` are distinct and
`W_ab = L_a ⊕ L_b`. Since `rank P = 5`, the `L_a` form a basis `f_a`. The same
argument on the `q` side gives `g_a`.
(v) For `a ≠ c`, pick `b, d` so that `ab` and `cd` are disjoint. Then
`W_ab ⊥ U_cd` gives `f_a ⊥ g_c`. Rescaling makes the bases dual. ∎
`verify.py` (`d5_normal_form`) starts from `M` alone and carries out (i)–(v)
with exact Fractions: it builds the rank factorisation, computes the `W_e`,
triangle spans, the pairwise meets, `L_a`, the dual pairing and the
edge-supported normal form. The inputs are the three family points and the Gram
matrix (each with fixed non-trivial `D₁`, `D₂`) and one boundary member. The
negative control is a rank-5 matrix that breaks 4 orthogonal zeros, and the
construction fails on it. As a consistency check, the tangent upper bound is
also 55 at the three family points and at the boundary member, so these are
smooth points of a single 55-dimensional component.

**Corollary (#2277 OQ4, D5 half).** Theorem C applies verbatim to every
edge-supported realisation, including boundary members. Lemma S needs only
that `x_{ij±}` and `y_{ij±}` each span `⟨e_i, e_j⟩`. On boundary members
`R(e_a)` can lose one line of an edge, but classes are `±`-closed, so `Def(R(e_a))`
is unchanged. The verifier recomputes the actual ranks, matched 4 and
unmatched 3. By Theorems D and E, **every realisation of D5 of rank `≤ 5`
has dense-pairing cost `≥ 20`** for decoders with `col P ⊆ col M` and
`col Q ⊆ row M`, which includes all square decoders. The bound is attained.
Realisations of rank `> 5` remain outside, as in #2277 §6.

**Robustness observation.** CHECKED: removing one orthogonal pair from the E6
pattern leaves the tangent dimension at exactly 71, and removing all 15
orthogonality constraints of line 0 gives exactly 81. NOT CERTIFIED (scratch
observation only, not replayed by verify.py): for partial removals at line 0,
the dimension stays 71 for the first 10 removals in the verifier's pair order
and then rises by 2 per removal. The threshold depends on the removal order;
an independent reviewer found 73 already at 10 removals in another ordering.

## Reproduce

```sh
python3 -I -B research/e6-d5-gram-realisation-rigidity/verify.py      # ~8 s, stdlib
# expected last line: ALL 42 CHECKS PASSED in <t>s
python3 -I -B research/e6-d5-gram-realisation-rigidity/verify.py --e8 # adds E8 239 = 2v-1: ALL 43 CHECKS PASSED (~140 s)
python3 scripts/research_package.py --package research/e6-d5-gram-realisation-rigidity --check-only
```

**Negative controls (each must fail its acceptance test; verify.py asserts that
they do):**
- E6 with the 15 orthogonality constraints of line 0 removed is not rigid:
  its tangent is exactly 81 > 71. The prime upper bound 81 is matched by the
  orbit plus the free first-order moves of `x_0` and `y_0`.
- D5 with one orthogonal pair removed has tangent exactly 57 ≠ 55 (exact
  `Fraction` rank), which shows the count depends on the pattern.
- A sign error in `y_{ij-}` breaks the pattern zeros.
- The inadmissible `a = −b` on one edge gives a zero diagonal and 6 deficient
  classes, so Lemma S fails.
- Half the family (`b` frozen) together with the orbit spans exactly 49 < 55
  (exact `Fraction` rank).
- The Theorem D construction applied to a rank-5 non-realisation (4 orthogonal
  zeros broken) fails.
- Positive control: the Gram parameters give 0 scaling violations.

## Scope, inherited assumptions, unresolved obligations

- **E6: local, not global.** Theorem A says nothing about rank-6 realisations
  outside a neighbourhood of `G`, for example on other components of `V_E6`.
  It does not exclude rank-5 realisations of E6, and no rank-5 search was run.
- **D5: rank `≤ 5` only.** Theorems D and E are written proofs. The verifier
  replays the construction of Theorem D on 5 exact instances and one negative
  control. That replay is evidence for the proof, not a machine-checked proof
  of it. Realisations of rank `> 5` are not covered.
- **Rank exactly `T`, factors in `col M` / `row M`, dense pairing.** These
  hypotheses are inherited from #2277 Theorem 4′. Arbitrary `B`, factors
  outside `col M`, and realisations of rank `> T` are not covered.
- **Inherited:** #2277 Lemma 5.1, Theorem 4′, Lemma OC and the Theorem 7.4
  argument. These are proven in the draft, unmerged PR #2277 (head
  `ca7f9992`) and are not re-proved here; only their hypotheses for the D5
  family are checked. Theorem C and the Corollary are conditional on them.
- Prime ranks are used only in the safe direction (`rank_p ≤ rank_Q`), and
  each one is matched by a bound in the other direction. All other acceptance
  checks, including the negative controls, use exact integer, `Fraction` or `F₂`
  arithmetic. Proof-relevant intermediate steps use `assert`, so verify.py
  refuses to run under `python -O`. This is a finite exact certificate combined
  with written proofs. It is not a formalisation.
- VERIFY.json declares the generic replay interpreter (3.12, required by the package tooling), but every run recorded here used CPython 3.14 (stdlib only); 3.12 itself was not tested.
- D5 is not a frontier unit. Nothing here changes a supplier, a call profile
  or κ.

## Open next questions

The structured list is in [TASK.json](TASK.json):
1. **Global uniqueness at rank 6 for E6.** This would make E6 `≥ 36`
   realisation-free at rank `T`. A first step is exact elimination on a
   normalised sub-configuration. The blocker is that there is no frame argument.
2. **Rank-5 realisations of E6** (dense cost `≤ 35` if one exists). By
   Theorems D and E, the D5 sub-configuration of such a realisation would have
   rank exactly 5 and be edge-supported. For each of the 16 extra lines `s`
   (signs `ε`), `p_s` restricted to edge `ij` must then be proportional to the
   `x` of the line on `ij` that is not orthogonal to `s`. *Unchecked sketch:*
   in the open chart, where every `x_t, y_t` has full edge support, the 16 sign
   patterns force `a_ij = b_ij` and a cocycle. That means a scaled-Gram D5
   part, which then violates the 5 extra–extra orthogonalities
   (`ε·ε' = −3 ≠ 0`). The first step is to make this exact and extend it to
   the boundary charts. The blocker is the case analysis of degenerate edges.
3. **D5 at rank `> 5`.** This is #2277's §6 cap and the last gap in a
   realisation-free D5 `≥ 20` with factors in `col M`. A first step is to count
   deficient classes in a rank-6 lift of the edge-supported family. The blocker
   is that Theorem 4′ no longer forces `ρ` terms of full deficiency control.
4. **Which other units are first-order rigid?** For D4 there are 12 tangent
   directions beyond the edge family. P112, P104 and E7-frame can be tested
   with this verifier's functions.

## Base, sources, credit

- Base commit `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`. The selected record
  `certificates/selected-result.json` (sha256 `10b9e340…fa32`) is unchanged.
  Provenance pins are in [SOURCES.json](SOURCES.json). The package has no live
  input files: every unit is rebuilt from Cartan matrices or coordinates.
- Definitions, Theorem 4′, Lemma 5.1, Lemma 7.1, Theorem 7.4 and OQ4 are from
  **#2277** (draft) and **#2228** (DreamingOfClouds), cited at #2277 head
  `ca7f99921f03398d303bba90245d3ee2e38e95c3`.
- **#2338** (Theorem R) concerns F₂ pairing-table rigidity, which is a
  different object.
- The tangent-versus-torus rigidity method on rank-8 units comes from **#1212**
  (burntout76; its Theorem 1 already proves global uniqueness up to the torus
  for rank-≤8 P120 = E8 and P112 realisations), **#1292** (navinor), and
  **#1389, #1399, #1425** (JosieElliston), with the audit in **#1367**
  (1337isnot1337). The model comes from **#2125** and **#1590**
  (DreamingOfClouds).
- The E6 screens are **#2137, #2232, #2240, #2247** (1337isnot1337) and
  **#2272** (navinor). EdDiboi contributed the local E6 seven-term audit (#1166).
  The first-order jet method follows the earlier loop PR **#2351**.

Prepared by thakrarsagar with substantial AI assistance from Claude (Anthropic, Claude Opus 5.5). Apache-2.0.
