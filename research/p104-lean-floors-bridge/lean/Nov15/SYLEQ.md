# SYLEQ.lean: R21 Part A, the SYLEQ closure as an operator (A2 confluence, A3 soundness, A4 equivariance, plus an A1 instance). No sorry, ~4 s, 1.5 GB
Self-contained, namespace SYLEQ. The setting is any partial order of states; finiteness is assumed only where termination needs it. ⊥ ("contradiction") is just the least state. R21's "finite lattice" is not needed.

**A2.** The rules are monotone (A1, a hypothesis) and deflationary.
- `fair_iter_stops`: on a finite poset, every fair iteration σ_{k+1} = ρ_{c k}(σ_k) becomes constant at a common fixed point below σ₀. "Fair" means every rule is chosen infinitely often.
- `stop_is_greatest`: the stopping point is the greatest common fixed point below σ₀.
- `confluence`: two iterations in any rule orders that stop do so at the same state.
- `kill_independent`: the verdict "= ⊥" therefore does not depend on rule order.
- The proof avoids Tarski. Every common fixed point τ ≤ σ₀ stays below every iterate (by monotonicity), so the stopping point dominates all of them.

**A3.**
- `soundness`: suppose σ_W ≤ σ₀ and every rule maps states above σ_W to states above σ_W. This is R20 §4's rule soundness, a hypothesis here. Then σ_W lies below every iterate.
- `not_killed`: if moreover σ_W ≠ ⊥, no iterate is ⊥.

**A4.** `equivariance`: suppose an order isomorphism g (e.g. a GL(d,2) relabelling) maps σ₀ to σ₀′ and intertwines the rules. Then g maps the closure to the closure.

**A1 instance.** The state space is WithBot (V → Finset R): one candidate register set per job type, with ⊥ for contradiction. The COVER rule says: if Req ⊄ ∪_v A_v, the state becomes ⊥. It is proved monotone (`cover_mono`) and deflationary (`cover_defl`).

**A1 for RANK/EQ (LEAN-NEXT3, Nov 16).** The rule follows R21/fpcheck.py `kind == 'E'`.
- State: (Ax, Ay, eX, eY), with Ax ⊆ Ax′, Ay ⊆ Ay′, eX ⊇ eX′, eY ⊇ eY′. A missing eq record is ∅.
- C_X = nestR ∪ {singletons A_v = {j}, j ≠ anc, v ∈ S} ∪ ⋃_{ν nested} eX_ν.
- The rule: a sum > J+r kills; at equality it pins A_v ∩ C (an empty pin kills) and records e_μ = C; otherwise it does nothing.
- `rankEq_mono` (A1) and `rankEq_defl` hold on WithBot of VALID states (every candidate set nonempty), with μ in its own nested set, as in the code.
- Finding: validity is needed. R21's "Ax_v = {j} or ⊥" silently identifies empty sets with ⊥. With Ax_v = ∅ allowed as a non-⊥ state, the step C_X(σ) ⊇ C_X(σ′) fails.
- **Raw-space counterexample built (LEAN-NEXT4), `rankEqRaw_not_mono`: A1 is FALSE when candidate sets can be empty.**
  - `rankEqRaw` is the rule exactly as written, on WithBot ES (empty sets are ordinary states).
  - Instance: one job type; R = {0, 1, 2}, ancilla 2; bound 2; μ ∈ Nest. s: Ax = ∅, Ay = {1}. t: Ax = {0}, Ay = {1}. No records.
  - Then s ≤ t. C_X(s) = ∅ (sum 1 < 2, so s is unchanged). C_X(t) = {0} (sum 2, so t is pinned and records eX_μ = {0}).
  - So ρ(s) = s ≰ ρ(t), because the order needs eX_μ(ρ t) ⊆ eX_μ(s) = ∅.
- **Fix proved:** `rankEqFix` = normalise (any empty candidate set ⇒ ⊥), then the valid-space rule.
  - `norm_mono`: an empty set stays empty below.
  - `rankEqFix_mono` (A1) and `rankEqFix_defl` hold on the raw space.
  - `rankEqFix_valid`: it equals the raw rule on valid states.
  - So A2–A4 apply to the fixed operator. fpcheck.py must kill empty candidate sets before (or as part of) RANK/EQ; whether it does was not checked.
- Not linked: COVER above is stated on a different (Ax-only, raw) state type. Re-stating it on the valid space is routine.

**Not formalized.**
- FRAME–HALL and its A1 monotonicity.
- A5, the singleton read-off. It rests on R17 Theorem C.

Axioms: rankEq_mono, rankEq_defl, rankEqRaw_not_mono, rankEqFix_mono/defl/valid use [propext, Classical.choice, Quot.sound]. confluence, stop_is_greatest, soundness and not_killed use no axioms. equivariance uses [propext, Quot.sound]. The rest use [propext, Classical.choice, Quot.sound]. R21 Part A's A1 for RANK/EQ is false on the raw space (empty sets as non-⊥ states) and true on the valid / normalised space.
