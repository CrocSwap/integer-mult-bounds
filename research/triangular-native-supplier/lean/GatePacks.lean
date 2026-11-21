import CompletePacks

namespace GatePacks

open CompletePacks CirculantTraceProduct TriangularSupplier MixedRankRecovery MixedRankPublicGrid
open scoped BigOperators

variable {d D : ℕ} (t : Fin d → ℕ)

/-- This witness records the rational gates and the measured physical states in one pack. -/
structure GateData (entry exit : Field t) (ideal : Field t → Field t) where
  steps : ℕ
  exactGate : ℕ → Field t → Field t
  actual : ℕ → Field t
  M : ℝ
  ε : ℝ
  β : ℝ
  positiveM : 0 ≤ M
  positiveε : 0 ≤ ε
  first : actual 0 = entry
  last : actual steps = exit
  homogeneous : ∀ j, j < steps → exactGate j 0 = 0
  interval : ∀ i k, i+k ≤ steps → ∀ x y,
    dist (DirectTensorStability.run exactGate i k x) (DirectTensorStability.run exactGate i k y) ≤ M*dist x y
  rounded : ∀ j, j < steps → dist (actual (j+1)) (exactGate j (actual j)) ≤ ε*(1+‖actual j‖)
  synthesis : ‖entry‖ ≤ 2 → dist (DirectTensorStability.run exactGate 0 steps entry) (ideal entry) ≤ β

structure GateWitness (entry exit : Field t) (ideal : Field t → Field t) (δ : ℝ)
    extends GateData t entry exit ideal where
  bootstrap : (steps : ℝ)*M*ε ≤ 1/2
  spend : (steps : ℝ)*M*ε*(2+4*M)+β ≤ δ

theorem gate_defects (x y : Field t) (ideal : Field t → Field t) (δ : ℝ)
    (g : GateWitness t x y ideal δ) (hx : ∀ i, ‖x i‖ ≤ 2) : Close δ y (ideal x) := by
  have rad : ‖x‖ ≤ 2 := (pi_norm_le_iff_of_nonneg (by norm_num)).mpr hx
  have zero (i k : ℕ) (h : i+k ≤ g.steps) : DirectTensorStability.run g.exactGate i k 0 = 0 := by
    induction k generalizing i with
    | zero => rfl
    | succ k ih =>
      rw [DirectTensorStability.run, g.homogeneous i (by omega)]
      exact ih (i+1) (by omega)
  have hr (k : ℕ) (hk : k ≤ g.steps) :
      ‖DirectTensorStability.run g.exactGate 0 k (g.actual 0)‖ ≤ 2*g.M := by
    have h := g.interval 0 k (by omega) x 0
    rw [zero 0 k (by omega), dist_zero_right, dist_zero_right] at h
    rw [g.first]
    exact h.trans (by simpa [mul_comm] using mul_le_mul_of_nonneg_left rad g.positiveM)
  have out := (DirectTensorStability.bounded_computation g.exactGate g.actual g.steps
    g.M g.ε (2*g.M) g.positiveM g.positiveε (by linarith [g.positiveM]) g.bootstrap
    g.interval hr g.rounded g.steps le_rfl).2
  rw [g.first, g.last] at out
  have whole := dist_triangle y (DirectTensorStability.run g.exactGate 0 g.steps x) (ideal x)
  have err : dist y (ideal x) ≤ δ := by linarith [g.synthesis rad, g.spend]
  intro k
  exact (show ‖y k - ideal x k‖ ≤ dist y (ideal x) by
    simpa only [dist_eq_norm] using dist_le_pi_dist y (ideal x) k).trans err

/-- The binary selector dominates a closed integer bound for each local gate bill. -/
theorem selector_budget (p E J K P : ℕ) (hJ : 0 < J) (hK : 0 < K)
    (selector : p+3+8*E+4*((J*K).log2+1)+(K.log2+1)+64 ≤ P) :
    64*(2^p)*J*K^3*(2^E)^4 ≤ 2^P := by
  let bits := (J*K).log2+1
  have jk : J*K ≤ 2^bits :=
    Nat.le_of_lt ((Nat.log2_lt (Nat.mul_ne_zero hJ.ne' hK.ne')).mp (Nat.lt_succ_self _))
  have powJ : J ≤ J^3 := by simpa using Nat.pow_le_pow_right hJ (show 1 ≤ 3 by decide)
  calc
    _ ≤ 64*2^p*(J*K)^3*(2^E)^4 := by
      rw [mul_pow, ← Nat.mul_assoc (64*2^p)]
      gcongr
    _ ≤ 64*2^p*(2^bits)^3*(2^E)^4 := by gcongr
    _ = 2^(6+p+bits*3+E*4) := by simp only [pow_add,pow_mul]; norm_num
    _ ≤ _ := Nat.pow_le_pow_right (by decide) (by dsimp [bits]; omega)

theorem selector_spend (A J K U V : ℝ) (hA : 1 ≤ A) (hJ : 1 ≤ J) (hK : 1 ≤ K)
    (hU : 1 ≤ U) (guard : 64*U*J*K^3*A^4 ≤ V) :
    J*A*(K^2*A^2/V) ≤ 1/2 ∧
      J*A*(K^2*A^2/V)*(2+4*A)+2*K*A/V ≤ (1/8 : ℝ)/U/K := by
  have a0 : 0 < A := by linarith
  have j0 : 0 < J := by linarith
  have k0 : 0 < K := by linarith
  have u0 : 0 < U := by linarith
  have v0 : 0 < V := lt_of_lt_of_le (by positivity) guard
  have k1 : K ≤ K^2 := by nlinarith
  have a1 : A ≤ A^4 := by calc
    A = A^1 := by ring
    _ ≤ _ := pow_le_pow_right₀ hA (by decide)
  have jk : K*A ≤ J*K^2*A^4 := by
    calc
      _ = 1*K*A := by ring
      _ ≤ _ := by gcongr
  have lhs : J*A*(K^2*A^2)*(2+4*A)+2*K*A ≤ 8*J*K^2*A^4 := by
    have fac : 2+4*A ≤ 6*A := by linarith
    calc
      _ ≤ J*A*(K^2*A^2)*(6*A)+2*(J*K^2*A^4) :=
        add_le_add (mul_le_mul_of_nonneg_left fac (by positivity)) (by linarith only [jk])
      _ = _ := by ring
  have one : 2*J*A*(K^2*A^2) ≤ 64*U*J*K^3*A^4 := by
    calc
      _ ≤ 64*1*J*K^3*A^4 := by
        have h : 2*J*K^2*A^3 ≤ 64*J*K^3*A^4 := by
          gcongr <;> norm_num
        linarith only [h]
      _ ≤ _ := by gcongr
  constructor
  · rw [show J*A*(K^2*A^2/V) = (J*A*(K^2*A^2))/V by ring]
    rw [div_le_iff₀ v0]
    linarith only [one,guard]
  · rw [show J*A*(K^2*A^2/V)*(2+4*A)+2*K*A/V =
        (J*A*(K^2*A^2)*(2+4*A)+2*K*A)/V by ring]
    rw [div_le_iff₀ v0]
    have h : 8*J*K^2*A^4 ≤ (1/8:ℝ)/U/K*V := by
      calc
        _ = (1/8:ℝ)/U/K*(64*U*J*K^3*A^4) := by field_simp; ring
        _ ≤ _ := mul_le_mul_of_nonneg_left guard (by positivity)
    exact lhs.trans h

variable (s : Fin d → ℕ) (hs : Pairwise fun i j ↦ Nat.Coprime (s i) (s j))
  [∀ i, NeZero (s i)] (ht : ∀ i, s i ≤ t i) [NeZero (∏ i, s i)]

/-- A measured gate trace in each actual pack suffices for the two-source exact integer product. -/
theorem from_gates_to_bits (B : ℕ) (hB : 32 ≤ B) (hEven : Even B) (hsize : ∏ i, s i ≤ B)
    (w : TapePacks s t (B^6)) (δ : Bool → ℝ) (mask : Bool → ℕ → Finset (Fin d))
    (budget : ∀ p, (w.count p : ℝ)*δ p ≤ (1/8 : ℝ)/(B^6:ℕ))
    (hd : ∀ p, 0 ≤ δ p) (schedule : MaskSchedule s t w mask)
    (entry : ∀ p x, disk x.val (1/2) → w.state p x 0 = zeroFill s t hs ht x.val)
    (inspect : ∀ p (x : GridSignal (∏ i,s i) (B^6)), disk x.val (1/2) → ∀ j, j < w.count p →
      GateWitness t (w.state p x j) (w.state p x (j+1)) (w.action p j) (δ p))
    (a b : ZMod (∏ i,s i) → ℕ) (ha : ∀ j, a j ≤ B) (hb : ∀ j, b j ≤ B)
    (hspan : ∀ i j, a i ≠ 0 → b j ≠ 0 → i.val+j.val < ∏ i, s i) :
    pack B (carry B 0 (ordered (wordDecode (by omega : 0 < B) hEven
      (read s t hs ht w false) (read s t hs ht w true) a b))) =
      radixValue B a * radixValue B b := by
  apply recovered_from_partition s t hs ht B hB hEven hsize w δ mask _ schedule a b ha hb hspan
  exact ⟨hd, budget, entry, fun p x hx j hj ↦ gate_defects t _ _ _ _ (inspect p x hx j hj)⟩

#print axioms gate_defects
#print axioms selector_budget
#print axioms selector_spend
#print axioms from_gates_to_bits

/-- Substitute the integer precision selector in the complete theorem. The remaining
numeric bounds apply to individual stored gate words and their local arithmetic. -/
theorem at_selected_precision (B p E J K P : ℕ) (hB : 32 ≤ B) (hEven : Even B)
    (hsize : ∏ i, s i ≤ B) (hD : B^6 = 2^p) (hJ : 0 < J) (hK : 0 < K)
    (sel : p+3+8*E+4*((J*K).log2+1)+(K.log2+1)+64 ≤ P)
    (w : TapePacks s t (B^6)) (mask : Bool → ℕ → Finset (Fin d))
    (schedule : MaskSchedule s t w mask) (count : ∀ sign, w.count sign ≤ K)
    (entry : ∀ sign x, disk x.val (1/2) → w.state sign x 0 = zeroFill s t hs ht x.val)
    (inspect : ∀ sign (x : GridSignal (∏ i,s i) (B^6)), disk x.val (1/2) →
      ∀ j, j < w.count sign →
      {g : GateData t (w.state sign x j) (w.state sign x (j+1)) (w.action sign j) //
        g.steps ≤ J ∧ g.M ≤ (2:ℝ)^E ∧
        g.ε ≤ (K:ℝ)^2*((2:ℝ)^E)^2/((2:ℝ)^P) ∧ g.β ≤ 2*K*(2:ℝ)^E/((2:ℝ)^P)})
    (a b : ZMod (∏ i,s i) → ℕ) (ha : ∀ j, a j ≤ B) (hb : ∀ j, b j ≤ B)
    (hspan : ∀ i j, a i ≠ 0 → b j ≠ 0 → i.val+j.val < ∏ i, s i) :
    pack B (carry B 0 (ordered (wordDecode (by omega : 0 < B) hEven
      (read s t hs ht w false) (read s t hs ht w true) a b))) =
      radixValue B a * radixValue B b := by
  let A : ℝ := 2^E
  let U : ℝ := 2^p
  let V : ℝ := 2^P
  have real_pub : ((B^6 : ℕ) : ℝ) = U := by rw [hD]; dsimp [U]; norm_cast
  have big : 64*U*J*(K:ℝ)^3*A^4 ≤ V := by
    dsimp [U,A,V]; exact_mod_cast selector_budget p E J K P hJ hK sel
  have A1 : 1 ≤ A := one_le_pow₀ (by norm_num)
  have U1 : 1 ≤ U := one_le_pow₀ (by norm_num)
  have K1 : 1 ≤ (K:ℝ) := by exact_mod_cast hK
  have J1 : 1 ≤ (J:ℝ) := by exact_mod_cast hJ
  obtain ⟨fund, spend⟩ := selector_spend A J K U V A1 J1 K1 U1 big
  let δ : ℝ := (1/8 : ℝ)/U/K
  have dn : 0 ≤ δ := by dsimp [δ,U]; positivity
  apply from_gates_to_bits t s hs ht B hB hEven hsize w (fun _ ↦ δ) mask _
    (fun _ ↦ dn) schedule entry _ a b ha hb hspan
  · intro sign
    rw [real_pub]
    calc
      _ ≤ (K : ℝ)*δ := mul_le_mul_of_nonneg_right (by exact_mod_cast count sign) dn
      _ = _ := by dsimp [δ]; field_simp
  · intro sign x hx j hj
    obtain ⟨g,hN,hM,he,hβ⟩ := inspect sign x hx j hj
    have nj : (g.steps:ℝ) ≤ J := by exact_mod_cast hN
    change g.M ≤ A at hM
    change g.ε ≤ (K:ℝ)^2*A^2/V at he
    change g.β ≤ 2*K*A/V at hβ
    have part : (g.steps:ℝ)*g.M*g.ε ≤ J*A*((K:ℝ)^2*A^2/V) :=
      mul_le_mul (mul_le_mul nj hM g.positiveM (by positivity)) he g.positiveε
        (show 0 ≤ (J:ℝ)*A by dsimp [A]; positivity)
    refine ⟨g, part.trans fund, ?_⟩
    apply le_trans _ spend
    exact add_le_add (mul_le_mul part (by linarith) (by linarith [g.positiveM])
      (show 0 ≤ (J:ℝ)*A*((K:ℝ)^2*A^2/V) by dsimp [A,V]; positivity)) hβ

#print axioms at_selected_precision

end GatePacks
