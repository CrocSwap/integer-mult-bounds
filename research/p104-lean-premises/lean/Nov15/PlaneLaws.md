# PlaneLaws : SPLIT and QUARTER lemmas in Lean

`Nov15/PlaneLaws.lean`, Lean 4.33.0-rc1 + Mathlib, kernel only: no `sorry`, no `native_decide`; axioms `[propext, Classical.choice, Quot.sound]` (the E7 `decide +kernel` checks use only `propext`/`Quot.sound`). Builds in 17 s / 2.5 GB.
Setup: `Vec n = Fin n → ZMod 2`, standard dot, `one` = all-ones, token/port = odd (`Tok s : s ⬝ᵥ one = 1`), `Junk p s := Tok s ∧ s ⬝ᵥ p = 0`.

## 1. SPLIT (GC8 section 1): TRUE as stated, any n
* `split_xor`: an odd s is orthogonal to exactly one of u' and u'+1.
* `split_lemma`, `split_partition`: tokens of u_t^perp = (u_t^perp ∩ u_t'^perp) ⊔ (u_t^perp ∩ t''^perp), disjoint, t'' = u_t+u_t'+1 (on u_t^perp, s ⊥ t'' iff s ⊥ u_t'+1). No odd-n and no port-set assumption.
* `tok_t''`: t'' is odd when `one ⬝ one = 1` (n odd). `t''_eq_one`: t'' = 1 iff u_t = u_t'. So for the full odd set minus 1 (E7), t'' is a port exactly when t ≠ t'. "t'' is a port" is NOT automatic for an arbitrary odd-port set (needs closure): only the partition is general.
* E7 (`e7_split`, kernel `decide` over all 63×62 ordered pairs, 7-bit masks): t'' port, |u_t^perp odd| = 32, |C(t,t')| = 16, hence |C(t,t'')| = 16.

## 2. QUARTER (GC9 section 2, SPEC-PLANE rule 2): TRUE, exact partition for any n and any subspace B ∋ 1
* `QHyp B H`: H ≤ B, 1 ∉ H, and every b ∈ B has b ∈ H or b+1 ∈ H (H is a hyperplane of B avoiding 1).
* `qhyp_Hs`: for odd s, H_s = B ∩ s^perp is such a hyperplane. `qtok_Hs`: s is a token of its own chart Q_H = {odd s ⊥ H}.
* `qhyp_unique`: a QHyp H with s ∈ Q_H equals H_s. `quarter_partition`: for p ∈ B and a junk token s of p there is exactly one hyperplane H of B through p avoiding 1 with s ∈ Q_H (existence and uniqueness): the quarters partition p's junk exactly, no overlap, no correction terms.
* `qtok_junk`, `readers_see_all`: every token of Q_H is a junk token of every p ∈ H, so the ports of H all read the shared chart.
* Counting (formulas, general n; NOT formalised for general n): dim B = d gives 2^(d-2) quarters through p, 2^(n-d) tokens each (so 2^(n-2) junk tokens), and 2^(d-2) readers (the odd elements of H, since p ∈ H is odd). E7 (n=7, d=4): 4 quarters × 8 tokens = 32, 4 readers.
* E7 instance, kernel-checked on a concrete block (`Bl`, last four coordinates equal; `e7_block`: |B|=16, 1 ∈ B, 7 ports; `e7_quarter`, all 7 ports p): 32 junk tokens, exactly 4 distinct H_s, each of 8 elements, containing p, avoiding 1, with 8 tokens (fibre of s ↦ H_s) and 4 ports; `e7_totals`: 9·7·4 = 252 deliverers, 9·7·8 = 504 events (the plane-spread totals are arithmetic given 9 disjoint blocks).
* The E7 section works on 7-bit masks (`par` = xor-fold parity); it is the same finite structure as `Vec 7`, but the bridge lemma between the two encodings is not proved.

## Verdict
No paper statement in GC8/GC9/SPEC-PLANE sections 1-2 is false. Only the closure of the port set under t'' (E7 only) and the counting formulas (instance-checked) go beyond what is proved in general.
