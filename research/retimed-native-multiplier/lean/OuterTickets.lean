import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Tactic

namespace OuterTickets

/-- The paid volume at one active depth covers genuine ordinary shuttles. -/
theorem active {u h f v a b : ℝ} (hu : 1 ≤ u) (hh : 0 ≤ h) (hf : 0 ≤ f)
    (hshare : f ≤ h/u) (ha : a ≤ 1) (hab : a ≤ b)
    (hv : v ≤ u^(1-b)) :
    v * f^(1-a) ≤ h^(1-a) := by
  have hp : 0 < u := by linarith
  calc
    v * f^(1-a) ≤ u^(1-a) * (h/u)^(1-a) := by
      apply mul_le_mul
      · exact hv.trans (Real.rpow_le_rpow_of_exponent_le hu (by linarith))
      · exact Real.rpow_le_rpow hf hshare (by linarith)
      · exact Real.rpow_nonneg hf _
      · exact Real.rpow_nonneg hp.le _
    _ = h^(1-a) := by
      rw [← Real.mul_rpow hp.le (div_nonneg hh hp.le)]
      congr 1
      field_simp

/-- The two actual stop conditions cover the unexpanded cost at every depth. -/
theorem stop {u e h M a b g : ℝ} (hu : 0 ≤ u) (he : 0 < e) (hh : 1 ≤ h)
    (hm : 0 ≤ M) (hsize : u*e ≤ h) (hcut : e ≤ M*h^g)
    (hb : 0 ≤ b) (hb1 : b ≤ 1) (hab : a ≤ (1-g)*b) :
    u^(1-b)*e ≤ M^b*h^(1-a) := by
  have hp : 0 < h := by linarith
  calc
    u^(1-b)*e = (u*e)^(1-b)*e^b := by
      rw [Real.mul_rpow hu he.le, mul_assoc, ← Real.rpow_add he]
      ring_nf
      simp
    _ ≤ h^(1-b)*(M*h^g)^b := by
      apply mul_le_mul
      · exact Real.rpow_le_rpow (mul_nonneg hu he.le) hsize (by linarith)
      · exact Real.rpow_le_rpow he.le hcut hb
      · exact Real.rpow_nonneg he.le _
      · exact Real.rpow_nonneg hp.le _
    _ = M^b*h^(1-b+g*b) := by
      rw [Real.mul_rpow hm (Real.rpow_nonneg hp.le _),
        ← Real.rpow_mul hp.le, Real.rpow_add hp]
      ring
    _ ≤ M^b*h^(1-a) := by
      apply mul_le_mul_of_nonneg_left _ (Real.rpow_nonneg hm _)
      exact Real.rpow_le_rpow_of_exponent_le hh (by nlinarith)

/-- These are the integer offspring and data inequalities at one real depth. -/
theorem floorNext (h M j : ℕ) : (h/M^j)/M = h/M^(j+1) := by
  rw [Nat.div_div_eq_div_mul, pow_succ]

theorem floorArea (h M j : ℕ) : M^j * (h/M^j) ≤ h := by
  exact Nat.mul_div_le h _

def privateCap (s : ℕ) := s + 1024*(128*s*s+s+88)

/-- At all later sizes the entire private setup costs less than the input. -/
theorem privateCapTail (s : ℕ) (hs : 32 ≤ s) : privateCap s < 2^(s-4) := by
  obtain ⟨r, rfl⟩ := Nat.exists_eq_add_of_le hs
  induction r with
  | zero => decide
  | succ r ih =>
    have step : privateCap (32+(r+1)) ≤ 2*privateCap (32+r) := by
      unfold privateCap
      nlinarith [Nat.zero_le (r*r)]
    rw [show 32+r.succ-4 = (32+r-4)+1 by omega, pow_succ]
    omega

/-- An entire fixed native control scan, including 30 powers of J, fits the active axes. -/
theorem fixedScan (H : ℕ) (h : 32 ≤ H) : 30720*H+120 < 2^(H-1) := by
  obtain ⟨r, rfl⟩ := Nat.exists_eq_add_of_le h
  induction r with
  | zero => decide
  | succ r ih =>
    rw [show 32+r.succ-1 = (32+r-1)+1 by omega, pow_succ]
    omega

theorem prefixControl (s : ℕ) (h : 64 ≤ s) :
    2*(16*(s+1)+120) < s*s := by
  obtain ⟨r, rfl⟩ := Nat.exists_eq_add_of_le h
  nlinarith [Nat.zero_le (r*r)]

/-- Splitting the low quotient and moving the two residual factors preserves every cell. -/
theorem oneOrdinaryBank (B Q K u o A N f r G F : ℕ) :
    (u*B*Q*K)*o*A^(2*(N*f+r))*G*F =
      B*(u*Q*K*o*A^(2*(N*f))*(G*A^r)*(F*A^r)) := by
  rw [show 2*(N*f+r)=2*(N*f)+(r+r) by ring, pow_add, pow_add]
  ring

/-- A native stack records its true field sizes, including the suspended callers. -/
inductive Spine (root : ℕ) : ℕ → ℕ → List ℕ → Prop
  | initial : Spine root 0 root []
  | nested {m v z saved} : Spine root m v saved → z ≤ v →
      Spine root m z (v::saved)
  | entry {m v z saved} : Spine root m v saved → z ≤ 2*v →
      Spine root (m+1) z (v::saved)

private theorem afterEntry {m root v z : ℕ} (hv : v ≤ 2^m*root) (hz : z ≤ 2*v) :
    z ≤ 2^(m+1)*root := by
  calc
    z ≤ 2*v := hz
    _ ≤ 2*(2^m*root) := Nat.mul_le_mul_left _ hv
    _ = 2^(m+1)*root := by rw [pow_succ]; ring

/-- Only entries to a strictly earlier stage can increase an ancestor field. -/
theorem spineCap {root m v saved} (p : Spine root m v saved) :
    v ≤ 2^m*root ∧ ∀ x ∈ saved, x ≤ 2^m*root := by
  induction p with
  | initial => simp
  | nested base hz ih =>
    refine ⟨hz.trans ih.1, ?_⟩
    intro x hx
    rcases List.mem_cons.mp hx with rfl | h
    · exact ih.1
    · exact ih.2 x h
  | entry base hz ih =>
    refine ⟨afterEntry ih.1 hz, ?_⟩
    intro x hx
    rcases List.mem_cons.mp hx with rfl | h
    · exact afterEntry ih.1 (by omega)
    · exact afterEntry (ih.2 x h) (by omega)

private theorem boundedSum {ys : List ℕ} {c : ℕ} (h : ∀ x ∈ ys, x ≤ c) :
    ys.sum ≤ ys.length*c := by
  induction ys with
  | nil => simp
  | cons x ys ih =>
    have hx := h x (by simp)
    have ht := ih (fun t ht => h t (by simp [ht]))
    simp only [List.sum_cons, List.length_cons, Nat.succ_mul]
    omega

/-- All local high-water allowances add along a physical tape. -/
theorem stackHigh (localFactor : ℕ) {root m v saved} (p : Spine root m v saved) :
    (v::saved).sum*localFactor ≤ ((saved.length+1)*localFactor)*(2^m*root) := by
  have h := spineCap p
  have hs : (v::saved).sum ≤ (v::saved).length*(2^m*root) := by
    apply boundedSum
    intro x hx
    rcases List.mem_cons.mp hx with rfl | hh
    · exact h.1
    · exact h.2 x hh
  calc
    _ ≤ (v::saved).length*(2^m*root)*localFactor := Nat.mul_le_mul_right _ hs
    _ = _ := by simp only [List.length_cons]; ring

/-- The first port can vary; subsequent parent edges always take the zero port. -/
def terminalKey {α : Type*} (zero : α) : ℕ → α × List α → α × List α
  | 0, p => p
  | j+1, (i, a) => (zero, List.replicate j zero ++ i::a)

theorem readTerminal {α : Type*} (zero : α) (j : ℕ) :
    Function.Injective (terminalKey zero j) := by
  cases j with
  | zero => exact fun _ _ h => h
  | succ j =>
    rintro ⟨i,a⟩ ⟨k,b⟩ h
    simpa [terminalKey] using h

theorem recoverPort {α : Type*} (zero : α) {d j k : ℕ} {p q : α × List α}
    (hj : j ≤ d) (hk : k ≤ d) (depth : d-j=d-k)
    (label : terminalKey zero j p = terminalKey zero k q) : j=k ∧ p=q := by
  have he : j=k := by omega
  subst k
  exact ⟨rfl, readTerminal zero j label⟩

theorem sourceCard {w u s : ℕ} (f : Fin w × Fin u → Fin s)
    (hf : Function.Injective f) : w*u ≤ s := by
  simpa using Fintype.card_le_of_injective f hf

private theorem headCap (j : ℕ) (hj : 16 ≤ j) : 64*(j+1)+127 < 2^j := by
  obtain ⟨t, rfl⟩ := Nat.exists_eq_add_of_le hj
  induction t with
  | zero => decide
  | succ t ih =>
    rw [show 16+t.succ=(16+t)+1 by omega, pow_succ]
    omega

theorem headWidth (s : ℕ) (hs : 1024 ≤ s) : 4*((s+128).log2+1) ≤ s/16 := by
  have cap := headCap (s/64) (by omega)
  have loc : s+128 < 2^(s/64) := by omega
  have bits := (Nat.log2_lt (show s+128≠0 by omega)).2 loc
  omega

/-- A single integer test covers the complete stripe margin at all later lengths. -/
theorem stripeTail (s0 s localOverhead : ℕ) (h0 : 1024 ≤ s0) (hs : s0 ≤ s)
    (base : 16*(localOverhead+1028) ≤ 7*s0) :
    1024+(localOverhead+4*((s+128).log2+1)) < s/2-2 := by
  have width := headWidth s (by omega)
  omega

/-- For every cofinal stripe, a full earlier prefix has at most s/64 index bits
    after the four address and reader copies. -/
theorem sharpHeadWidth (s : ℕ) (hs : 4096 ≤ s) : 4*((s+128).log2+1) ≤ s/64 := by
  have cap : ∀ j : ℕ, 16 ≤ j → 256*(j+1)+127 < 2^j := by
    intro j h
    obtain ⟨t, rfl⟩ := Nat.exists_eq_add_of_le h
    induction t with
    | zero => decide
    | succ t ih =>
      rw [show 16+t.succ=(16+t)+1 by omega, pow_succ]
      omega
  have loc := cap (s/256) (by omega)
  have bits := (Nat.log2_lt (show s+128≠0 by omega)).2 (show s+128<2^(s/256) by omega)
  omega

theorem tightStripe (s0 s localOverhead : ℕ) (h0 : 4096 ≤ s0) (hs : s0 ≤ s)
    (base : 64*(localOverhead+1028) ≤ 31*s0) :
    1024+(localOverhead+4*((s+128).log2+1)) < s/2-2 := by
  have width := sharpHeadWidth s (by omega)
  omega

theorem precisionTail (s : ℕ) (hs : 64 ≤ s) : 12000*(34*s+9) ≤ 2^(s-2) := by
  obtain ⟨j, rfl⟩ := Nat.exists_eq_add_of_le hs
  induction j with
  | zero => decide
  | succ j ih =>
    rw [show 64+j.succ-2=(64+j-2)+1 by omega, pow_succ]
    omega

#print axioms sharpHeadWidth
#print axioms tightStripe
#print axioms precisionTail

#print axioms active
#print axioms stop
#print axioms floorNext
#print axioms floorArea
#print axioms privateCapTail
#print axioms fixedScan
#print axioms prefixControl
#print axioms oneOrdinaryBank
#print axioms spineCap
#print axioms stackHigh
#print axioms readTerminal
#print axioms recoverPort
#print axioms sourceCard
#print axioms headWidth
#print axioms stripeTail

end OuterTickets
