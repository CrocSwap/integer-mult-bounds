import Mathlib.Tactic

namespace SevenStage

/-- No stage can earn more than a 249/250 share of the raw saving and a
    1/250 share of its predecessor. This grants free transport and exact rounding. -/
def ideal (c : ℚ) (i : ℕ) : ℚ := c*(1-(1/250:ℚ)^i)

theorem idealStep (c : ℚ) (i : ℕ) :
    ideal c (i+1) = (249*c+ideal c i)/250 := by
  unfold ideal
  rw [pow_succ]
  ring

theorem allStageUpper (c : ℚ) (b : ℕ → ℚ) (m : ℕ) (start : b 0 ≤ 0)
    (step : ∀ i<m, b (i+1) ≤ (249*c+b i)/250) :
    ∀ i≤m, b i ≤ ideal c i := by
  intro i hi
  induction i with
  | zero => simpa [ideal] using start
  | succ i ih =>
    rw [idealStep]
    have prior := ih (by omega)
    have next := step i (by omega)
    linarith

def c : ℚ := 4484997569314581 / 2^60
def k : ℚ := 3890115286594445 / 10^18
def g : ℚ := 1 / 10^21

/-- Six is impossible for the actual unpowered dyadic price even if all local
    calls, physical transport, strict slack, and intermediate grid errors are free. -/
theorem sixCannotReach (b : ℕ → ℚ) (start : b 0 ≤ 0)
    (step : ∀ i<6, b (i+1) ≤ (249*c+b i)/250) : b 6 < k := by
  have upper := allStageUpper c b 6 start step 6 (by omega)
  exact upper.trans_lt (by norm_num [ideal,c,k])

theorem finalSeparation : k+5*g-ideal c 6 =
    3916755027601357/7036874417766400000000000000000000 := by
  norm_num [ideal,c,k,g]

def ranks : List ℕ :=
  [5698204041,91171264649,1458740234375,23339843750000,373437500000000,
   5975000000000000,95600000000000000]

def ticks : List ℕ :=
  [3874554585109198542,3890053028767339082,3890115036624328130,
   3890115285535903366,3890115286586558872,3890115286594199570,3890115286594445005]

def price (previous : ℚ) (h : ℕ) : ℚ :=
  min (39/10000) ((249*(c-11/(8*(h:ℚ)))+previous)/250)

/-- Follow the written booking grid for every intermediate stage and the actual
    complete caller's exact chosen ordinary rate on the final stage. -/
def paidList : ℚ → List (ℕ × ℕ) → Bool
  | _, [] => true
  | previous, (h,b)::rest =>
    let boundary := price previous h
    let rate : ℚ := (b:ℚ) / 10^21
    decide (h>0 ∧ previous<rate ∧ rate<boundary) &&
    (if rest.isEmpty then decide (rate=k+5*g)
     else decide ((b:ℚ)+1 ≤ boundary*10^21 ∧ boundary*10^21 < (b:ℚ)+2)) &&
    paidList rate rest

theorem actualSeven : ranks.length=7 ∧ ticks.length=7 ∧ paidList 0 (ranks.zip ticks) = true := by
  norm_num [ranks,ticks,paidList,price,c,k,g,List.zip,List.zipWith]

/-- Exact serial-clock normalization with the charged stage factor present at
    every depth. The stage list can have any finite length. -/
theorem serialClock (J B : ℕ → ℚ) (A K : ℚ) (hA : 1 ≤ A) (hK : 1 ≤ K)
    (hJ : ∀ i, 2 ≤ J i) (initial : B 0 ≤ A)
    (step : ∀ i, B (i+1) ≤ K*(J i)^14*(1+B i)) (n : ℕ) :
    B n ≤ A*K^n*∏ i ∈ Finset.range n, (J i)^15 := by
  have invariant : ∀ i, 1 ≤ A*K^i*∏ j ∈ Finset.range i, (J j)^15 := by
    intro i
    apply one_le_mul_of_one_le_of_one_le
    · exact one_le_mul_of_one_le_of_one_le hA (one_le_pow₀ hK)
    · induction i with
      | zero => simp
      | succ i ih =>
        rw [Finset.prod_range_succ]
        exact one_le_mul_of_one_le_of_one_le ih (one_le_pow₀ (le_trans (by norm_num : (1:ℚ)≤2) (hJ i)))
  induction n with
  | zero => simpa using initial
  | succ n ih =>
    have hp := invariant n
    have hn := hJ n
    have factor : 0 ≤ K*(J n)^14 := by positivity
    have move : 1+B n ≤
        J n*(A*K^n*∏ i ∈ Finset.range n, (J i)^15) := by
      have double := mul_le_mul_of_nonneg_right hn (le_trans zero_le_one hp)
      linarith
    rw [Finset.prod_range_succ, pow_succ K]
    calc
      _ ≤ K*(J n)^14*(1+B n) := step n
      _ ≤ K*(J n)^14*(J n*(A*K^n*∏ i ∈ Finset.range n, (J i)^15)) :=
        mul_le_mul_of_nonneg_left move factor
      _ = _ := by ring

#print axioms serialClock
#print axioms allStageUpper
#print axioms sixCannotReach
#print axioms finalSeparation
#print axioms actualSeven

end SevenStage
