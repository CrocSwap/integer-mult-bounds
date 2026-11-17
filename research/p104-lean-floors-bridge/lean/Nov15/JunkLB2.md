# JunkLB2.lean: BIG-JUNKLB2 T1 (linked), T2, T3, T4 (Lean 4 + Mathlib), no sorry, ~9 s, 2.6 GB RSS
Source: cards/WILD/BIG/JUNKLB2/THEORY.md (T1, T3, T4), with the T4 scope fix from cards/WILD/BIG/GAPMAP/RESULT.md §2.
Self-contained, namespace JunkLB2. h / gaps / hsum / two_point / Net / chain_append are copied from JunkM.lean. Axioms (all 25 printed): [propext, Classical.choice, Quot.sound].

**T1 (g9 pricing, class M).**
- `hsum_tele`: Σ h_e over any chain = f(e−d0) − f(e−last) − Σ f(gaps). The chain need not end at e.
- `T1_Y`: for Y_p with 0 < d1 < … < 8, the real cost Σ h_8(0::d1::…) equals the g9 charge on every move but the first, plus l(d1) = f(8) − f(d1) − f(9−d1). Needs f(0) = f(1) = 0.
- `l_nonneg` (1 ≤ d ≤ 8, by convexity), `l_one`, `T1_Y_le`: charged ≤ real. Direct Y (d1 = 8) is covered and gives 0. Registers ending at V: the charge is the real cost by definition.
- `g9_nonneg`: g9 ≥ 0 for a ≤ b ≤ 9.
- `Net.T1_bound`: Σ_{junk pairs} dist_c(A_q → G_p) ≤ cost. Hypotheses:
  - a chain of moves A_q → G_p for each pair (JunkM `hpath_of_junk` now supplies it);
  - chart 0 holds no X port;
  - every move not leaving chart 0 is charged ≥ c (= g9);
  - Σ_m w_m ≤ cost.
- Σ_m w_m ≤ public cost is now a THEOREM (LEAN-NEXT4), `Net.T1_cost`; `Net.T1_full` chains it with `T1_bound`.
  - Op semantics = JunkM's (`path_to_chain`): charts never decrease; `mv t i` is register i's move chart_t(i) → chart_{t+1}(i) when its chart rises. New hypothesis: the moves are EXACTLY these (each move is `mv t i` for one rising step t < n: `hsurj`, `hinj`).
  - `movesOf i n` = register i's moves in time order; `movesOf_chain`: they form a chain birth chart → chart at time n.
  - `chain_hsum`: Σ h_e over the chain's moves = hsum_e over its dim list (dim : C → ℕ, strictly monotone).
  - Charge `wz`: 0 on moves out of chart z (dim 0), else c(s,t) = max(g9,0) (= g9 on every real move, `cg_eq`).
  - Model M as hypotheses: Y mains (Ym) are born at z and end at dim 8; every other register ends at dim 9. Public cost := Σ_i hsum_{8 or 9}(i's dim chain) (I1).
  - Per register: `reg_le_V` (charge ≤ Σ g9 = cost; 0-born non-Y first moves are charged 0 ≤ g9) and `reg_le_Y` (first move free, rest g9, then `T1_Y_le`).
  - Still hypotheses in T1_full: the pair chains (`hpath`, from JunkM `hpath_of_junk`), and chart z holds no X port.

**T3 (slot lemma), `slot_lemma`.** Conclusion: |D| ≤ rank{x_p : p ∈ D} + |(B0 ∩ Cr) \ W|. Hypotheses, all explicit:
- T2(a): the crossing rows ρ(Cr) are independent.
- T2(b): y_p = Σ A_{pμ} ρ_μ. A non-W crosser has A ≠ 0 only if it lands at G_p, and G is injective.
- W ⊆ B0 ∩ Cr. Crossing rows of W lie in S0 = span tok(B0).
- y_p = x_p + e_p with e_p ∈ S0, 0 ≠ x_p ∈ X, and X ⊓ S0 = 0.
- A linear P that fixes ρ(Cr) and kills the tokens of 0-born non-crossers. `proj_exists` builds P from IsCompl (the complementarity the T2 proof asserts).

Two findings from the formal proof:
1. The prose step "dim(S0/W) ≤ |Z| after removing stayers" needs this projection. The proof runs in P(S0), and rank{P x_p} ≤ rank{x_p}.
2. Directness of the Y_p in D is never used. D may be any set of Y mains with x_p ≠ 0. Non-direct ones are simply in Z themselves.

**T2 (crossing-basis lemma), now PROVED from op semantics (LEAN-NEXT4), `T2_run`.**
- Model at level k: ops are ADD i += c·j (i ≠ j, both on the same side of level k, i.e. co-present) and `cross i` (i's first move from dim ≤ k to > k; its row then is ρ_i). Moves that do not cross k change nothing at this level and are omitted. Time 0: every row is its own token; B = registers born at dim ≤ k.
- Hypothesis (class N): every stayer (in B, never crosses) ends as its own token.
- Conclusions, in V = B → K (rows restricted to B's coordinates, `resB`):
  - cr ⊆ B;
  - complementarity: span ρ(Cr) and span tok(B \ Cr) are complementary (`IsCompl`);
  - T2(a): the crossing rows are linearly independent;
  - T2(b), existence: every register above k at the end has its restricted final row in span ρ(Cr).
- Proof (formal): invariants (`LInv`) = above-k rows stay in the span of crossing rows so far; all rows span everything (ADD with i ≠ j is invertible). Then `compl_of_sup`: a ⊔ b = ⊤ with dim a ≤ |Cr|, dim b ≤ |St|, dim V = |Cr| + |St| forces IsCompl and dim a = |Cr|. Stayer-token independence is not needed as input.
- Discharged in T3: `slot_lemma_T2` replaces slot_lemma's independence + projection hypotheses by "ρ(Cr) ∪ tok(St) spans V, dim V = |Cr| + |St|, 0-born non-crossers are stayers". `slot_lemma_run` instantiates it on the run (V = B → K, B0 ⊆ B).
- Still hypotheses in slot_lemma_run: T2(b)'s coefficients A and their support (A_{pμ} ≠ 0 ⇒ μ lands at G_p for non-W μ; the path/landing argument), W's rows in S0, e_p ∈ S0, X ⊓ S0 = 0, x_p ≠ 0. The expansion's existence is proved (T2_run part 4), and with independence A is unique.

**T4 (departer law), CHOSEN SCOPE: owned arrivals counted.**
- Model: one chart's event list (arrive / born / ADD / depart), with ADDs only between registers present at c. Owned registers are registers too, so to be present at c they must arrive or be born there.
- `run_inv`: every present row lies in span(arrival rows) + span(c-born tokens). This is the prose's first step, and it holds only when ALL arrivals are counted.
- `strip_born`: a row with no c-born coordinates lies in the arrival span. This needs arrival rows to carry no c-born coordinates (a hypothesis).
- `T4_departer`: dim π(Arr_c^all) ≤ #public departers + #owned arrivals + #Y enders. Class-N hypothesis: public enders other than Y end as their own token, and π kills it.
- `T4_public`: the public-arrival span obeys the same bound.
- `T4_stop_cost` / `kappa_le`: a non-final move costs h_e(a,b) ≥ f(2) when b − a ≥ 1 and e − b ≥ 1.
- **Statement found false:** `T4_public_only_false`. The prose T4 (Arr_c = public arrivals, a ≤ d (+1)) fails in the same model, mirroring GAPMAP's owned-1502 → Y-213 charts. A public h arrives with e_h + e_x and owned o arrives with −e_x. Then h += o, so h ends as its own token. Yet dim π(public span) = 1 > 0. The gap is exactly step one of the prose proof. With no owned arrivals, `T4_departer` gives the prose statement back.

Still prose / hypotheses:
- "arrivals carry no c-born coordinates" (content only flows upward);
- class-N final rows;
- one arrival per register at c.
- T5 path bound: charging half formalized in Nov15/JunkT5.lean (LEAN-NEXT5). It is stated with the corrected T4 (owned arrivals) and needs root charts to be terminal. Descent is still prose.
