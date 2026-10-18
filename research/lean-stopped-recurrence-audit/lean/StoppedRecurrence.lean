import Mathlib

/-!
Independent formal audit of PR2234's stopped-recurrence implication.
The recurrence and uniform local charge are hypotheses, not a formal proof of
the complete recursive machine. The numerical margins are the predecessor's.
Gareth Davidson with substantial OpenAI Codex assistance. Apache-2.0.
-/

open scoped BigOperators

namespace StoppedRecurrence

noncomputable def potential (C w τ x : ℝ) : ℝ :=
  200 * C * x + 10000 * C * x ^ τ * w

/-- Including width zero makes the maximum total. For nonnegative costs with
zero cost at width zero, it equals the source's maximum on `1..f`. -/
noncomputable def worst (T : ℕ → ℝ) (f : ℕ) : ℝ :=
  (Finset.range (f + 1)).sup' (by simp) T

theorem potential_mono {C w τ x y : ℝ}
    (hC : 0 ≤ C) (hw : 0 ≤ w) (hτ : 0 ≤ τ) (hx : 0 ≤ x) (hxy : x ≤ y) :
    potential C w τ x ≤ potential C w τ y := by
  unfold potential
  apply add_le_add
  · exact mul_le_mul_of_nonneg_left hxy (by positivity)
  · exact mul_le_mul_of_nonneg_right
      (mul_le_mul_of_nonneg_left (Real.rpow_le_rpow hx hxy hτ) (by positivity)) hw

theorem potential_scale {C w τ x y : ℝ} (hx : 0 ≤ x) (hy : 0 ≤ y) :
    potential C w τ (x * y) =
      (200 * C * y) * x + (10000 * C * y ^ τ * w) * x ^ τ := by
  unfold potential
  rw [Real.mul_rpow hx hy]
  ring

/-- The source's literal positive-width fallback maximum agrees with `worst`.
The separate condition on width zero cannot silently be dropped. -/
theorem worst_eq_positive (T : ℕ → ℝ) (f : ℕ) (hf : 1 ≤ f)
    (hzero : T 0 ≤ T 1) :
    worst T f = (Finset.Icc 1 f).sup' (by exact ⟨1, by simp [hf]⟩) T := by
  apply le_antisymm
  · apply Finset.sup'_le
    intro j hj
    have hjf : j ≤ f := by simpa only [Finset.mem_range, Nat.lt_succ_iff] using hj
    by_cases hj0 : j = 0
    · subst j
      exact hzero.trans (Finset.le_sup' T (by simp [hf]))
    · exact Finset.le_sup' T (by simp; omega)
  · apply Finset.sup'_le
    intro j hj
    exact Finset.le_sup' T (by simpa only [Finset.mem_range, Nat.lt_succ_iff] using
      (Finset.mem_Icc.mp hj).2)

/-- Quantified recurrence implication. All recursive calls have proper width;
the two moment margins pay separately for `C*n` and `C*w`. -/
theorem stopped_bound {R : Type*} [Fintype R]
    (limit m : ℕ) (hm : 1 < m) (rank : R → ℕ)
    (hrank : ∀ r, 0 < rank r ∧ rank r < m)
    (a : R → ℝ) (ha : ∀ r, 0 ≤ a r) (b C w τ : ℝ)
    (hb : 0 ≤ b) (hC : 0 ≤ C) (hw : 0 ≤ w) (hτ : 0 ≤ τ)
    (linear : (∑ r, a r * ((rank r : ℝ) / m)) + b * (1 / m) ≤ 199 / 200)
    (power : (∑ r, a r * ((rank r : ℝ) / m) ^ τ) + b * (1 / m) ^ τ ≤ 9999 / 10000)
    (T : ℕ → ℝ) (zero : T 0 ≤ 0)
    (leaf : ∀ n, n ≤ limit → 0 < n → n < m → T n ≤ C * w)
    (step : ∀ n, n ≤ limit → m ≤ n → T n ≤
      (∑ r, a r * T (rank r * (n / m))) + b * worst T (n / m) + C * (n + w)) :
    ∀ n, n ≤ limit → T n ≤ potential C w τ n := by
  intro n
  induction n using Nat.strong_induction_on with
  | h n ih =>
    intro hnlimit
    by_cases hn0 : n = 0
    · subst n
      exact zero.trans (by unfold potential; positivity)
    have hn : 0 < n := by omega
    have hnreal : (1 : ℝ) ≤ n := by exact_mod_cast hn
    have hone : 1 ≤ (n : ℝ) ^ τ := Real.one_le_rpow hnreal hτ
    by_cases hsmall : n < m
    · apply (leaf n hnlimit hn hsmall).trans
      unfold potential
      have hcw : C * w ≤ C * (n : ℝ) ^ τ * w :=
        mul_le_mul_of_nonneg_right (by nlinarith) hw
      have hlin : 0 ≤ 200 * C * (n : ℝ) := by positivity
      have hpow : 0 ≤ C * (n : ℝ) ^ τ * w := by positivity
      nlinarith
    have hmn : m ≤ n := by omega
    have hmpos : 0 < (m : ℝ) := by exact_mod_cast (show 0 < m by omega)
    have hf : 0 < n / m := Nat.div_pos hmn (by omega)
    have hfn : n / m < n := Nat.div_lt_self hn hm
    have hfloor : (m : ℝ) * (n / m : ℕ) ≤ n := by
      exact_mod_cast Nat.mul_div_le n m
    have hdiv : (n / m : ℕ) ≤ (n : ℝ) / m := (le_div_iff₀ hmpos).mpr (by nlinarith)
    let A : ℝ := 200 * C * n
    let B : ℝ := 10000 * C * (n : ℝ) ^ τ * w
    have hA : 0 ≤ A := by dsimp [A]; positivity
    have hB : 0 ≤ B := by dsimp [B]; positivity
    have scaled (k : ℕ) (hk : k < n) (x : ℝ) (hx : 0 ≤ x)
        (hkn : (k : ℝ) ≤ x * n) : T k ≤ A * x + B * x ^ τ := by
      calc
        T k ≤ potential C w τ k := ih k hk (le_trans hk.le hnlimit)
        _ ≤ potential C w τ (x * n) := potential_mono hC hw hτ (by positivity) hkn
        _ = A * x + B * x ^ τ := potential_scale hx (by positivity)
    have children (r : R) : T (rank r * (n / m)) ≤
        A * ((rank r : ℝ) / m) + B * ((rank r : ℝ) / m) ^ τ := by
      apply scaled
      · have hi := (hrank r).2
        have hi' := Nat.mul_div_le n m
        nlinarith
      · positivity
      · push_cast
        calc
          (rank r : ℝ) * (n / m : ℕ) ≤ (rank r : ℝ) * ((n : ℝ) / m) :=
            mul_le_mul_of_nonneg_left hdiv (by positivity)
          _ = (rank r : ℝ) / m * n := by ring
    have fallback : worst T (n / m) ≤ A * (1 / m) + B * (1 / m) ^ τ := by
      apply Finset.sup'_le
      intro j hj
      have hjf : j ≤ n / m := by simpa only [Finset.mem_range, Nat.lt_succ_iff] using hj
      apply scaled j (lt_of_le_of_lt hjf hfn) (1 / m) (by positivity)
      calc
        (j : ℝ) ≤ (n / m : ℕ) := by exact_mod_cast hjf
        _ ≤ (n : ℝ) / m := hdiv
        _ = (1 / m) * n := by ring
    have aggregate : T n ≤
        A * ((∑ r, a r * ((rank r : ℝ) / m)) + b * (1 / m)) +
        B * ((∑ r, a r * ((rank r : ℝ) / m) ^ τ) + b * (1 / m) ^ τ) + C * (n + w) := by
      calc
        T n ≤ (∑ r, a r * T (rank r * (n / m))) + b * worst T (n / m) + C * (n + w) := step n hnlimit hmn
        _ ≤ (∑ r, a r * (A * ((rank r : ℝ) / m) + B * ((rank r : ℝ) / m) ^ τ)) +
            b * (A * (1 / m) + B * (1 / m) ^ τ) + C * (n + w) := by
          exact add_le_add (add_le_add
            (Finset.sum_le_sum fun r _ => mul_le_mul_of_nonneg_left (children r) (ha r))
            (mul_le_mul_of_nonneg_left fallback hb)) le_rfl
        _ = _ := by
          have expand : (∑ r, a r * (A * ((rank r : ℝ) / m) + B * ((rank r : ℝ) / m) ^ τ)) =
              A * (∑ r, a r * ((rank r : ℝ) / m)) +
              B * (∑ r, a r * ((rank r : ℝ) / m) ^ τ) := by
            rw [Finset.mul_sum, Finset.mul_sum, ← Finset.sum_add_distrib]
            apply Finset.sum_congr rfl
            intro r _
            ring
          rw [expand]
          ring
    have margins : T n ≤ A * (199 / 200) + B * (9999 / 10000) + C * (n + w) :=
      aggregate.trans (by gcongr)
    have saved : C * w ≤ C * (n : ℝ) ^ τ * w :=
      mul_le_mul_of_nonneg_right (by nlinarith) hw
    dsimp [A, B] at margins
    unfold potential
    nlinarith

end StoppedRecurrence

#print axioms StoppedRecurrence.worst_eq_positive
#print axioms StoppedRecurrence.stopped_bound
