import Mathlib.Data.Nat.Basic

namespace HeterogeneousRows

/-- The physical target changes direction at the peak of a Beneš word. -/
def target (width row : ℕ) : ℕ := min row (2 * width - 2 - row)

/-- An idle global row has no table query. These cases match local_switch_row. -/
def decode (maximum width g : ℕ) : Option ℕ :=
  if g < width then some g
  else if 2 * maximum - width ≤ g then some (g - 2 * (maximum - width))
  else none

/-- Place the rising rows first and the falling rows last. -/
def place (maximum width r : ℕ) : ℕ :=
  if r < width then r else r + 2 * (maximum - width)

theorem place_in_range {L h r : ℕ} (hpos : 0 < h) (hmax : h ≤ L)
    (hr : r < 2*h-1) : place L h r < 2*L-1 := by
  unfold place
  split <;> omega

theorem decode_place {L h r : ℕ} (hmax : h ≤ L) :
    decode L h (place L h r) = some r := by
  unfold place decode
  split <;> rename_i hsplit
  · simp
  · split <;> rename_i htest
    · omega
    · split
      · congr 1
        omega
      · omega

theorem exact_query {L h g r : ℕ} (hpos : 0 < h) (hmax : h ≤ L)
    (hg : g < 2*L-1) (hquery : decode L h g = some r) :
    r < 2*h-1 ∧ place L h r = g ∧ target h r = target L g := by
  unfold decode at hquery
  split at hquery <;> rename_i hfirst
  · obtain rfl : g = r := Option.some.inj hquery
    refine ⟨by omega, by simp [place, hfirst], ?_⟩
    unfold target
    rw [Nat.min_eq_left (by omega : g ≤ 2*h-2-g),
        Nat.min_eq_left (by omega : g ≤ 2*L-2-g)]
  · split at hquery <;> rename_i hsecond
    · obtain rfl : g - 2*(L-h) = r := Option.some.inj hquery
      refine ⟨by omega, ?_, ?_⟩
      · unfold place
        split <;> omega
      · unfold target
        rw [Nat.min_eq_right (by omega : 2*h-2-(g-2*(L-h)) ≤ g-2*(L-h)),
            Nat.min_eq_right (by omega : 2*L-2-g ≤ g)]
        omega
    · simp at hquery

theorem increasing {L h i j : ℕ} (hij : i < j) : place L h i < place L h j := by
  unfold place
  split <;> split <;> omega

#print axioms place_in_range
#print axioms decode_place
#print axioms exact_query
#print axioms increasing

end HeterogeneousRows
