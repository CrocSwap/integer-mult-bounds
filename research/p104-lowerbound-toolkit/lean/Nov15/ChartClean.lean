import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.LinearAlgebra.Dimension.Finite
import Mathlib.LinearAlgebra.Dimension.StrongRankCondition
import Mathlib.Algebra.Field.ZMod

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

/-!
# ChartClean (LANDSPANC1, Nov 20): Lemma CC (chart-clean) and corollary C1, kernel-only.

Trace model (charts = any preorder, registers `ι`, rows in `ι → K`): public registers start with their own token
and only ASCEND strictly; ADD/SCALE need co-location; owned registers (`O`) move/reset freely.  Fix a chart `F`.
Step restriction (O'): no ADD involving an owned register happens at a chart `⊇ F` (owned registers may VISIT).
Arrivals into `F` are recorded (`A`, `arrow` = the row at the moment of the MOVE into `F`).
Lemma CC: if the final rows of the arrived registers are independent, vanish on the tokens of the registers
initial at `F` (B), and all arrived registers still sit at `F` (S), then
  span(final rows of arrivals) = span(arrival rows).
Corollary C1: every arrival row lies in `W_F = span(finals)`; a copy `e_K + g` forces `g ∈ W_F + span e_K`.
-/
namespace ChartClean
open Module

variable {ι K C : Type*} [Fintype ι] [DecidableEq ι] [Field K] [Preorder C]

structure St (ι K C : Type*) where
  row : ι → ι → K
  cur : ι → C
  A : Finset ι
  arrow : ι → ι → K

inductive Step (F : C) (O : ι → Prop) : St ι K C → St ι K C → Prop
  | add (s : St ι K C) (d e : ι) (q : K) (hco : s.cur d = s.cur e)
      (hO : (O d ∨ O e) → ¬ F ≤ s.cur d) :
      Step F O s { s with row := Function.update s.row d (s.row d + q • s.row e) }
  | scale (s : St ι K C) (d : ι) (q : K) :
      Step F O s { s with row := Function.update s.row d (q • s.row d) }
  | arrive (s : St ι K C) (r : ι) (hr : ¬ O r) (hlt : s.cur r < F) :
      Step F O s { s with cur := Function.update s.cur r F, A := insert r s.A,
                          arrow := Function.update s.arrow r (s.row r) }
  | movePub (s : St ι K C) (r : ι) (c : C) (hr : ¬ O r) (hlt : s.cur r < c) (hne : c ≠ F) :
      Step F O s { s with cur := Function.update s.cur r c }
  | moveOwn (s : St ι K C) (r : ι) (c : C) (hr : O r) :
      Step F O s { s with cur := Function.update s.cur r c }
  | resetOwn (s : St ι K C) (r : ι) (hr : O r) :
      Step F O s { s with row := Function.update s.row r 0 }

def tok (B : ι) : ι → K := Pi.single B 1
def Arr (s : St ι K C) : Submodule K (ι → K) := Submodule.span K (s.arrow '' (s.A : Set ι))
def Tsp (BS : Set ι) : Submodule K (ι → K) := Submodule.span K ((tok : ι → ι → K) '' BS)

def Inv (F : C) (O : ι → Prop) (BS : Set ι) (s : St ι K C) : Prop :=
  (∀ x B, B ∈ BS → s.row x B ≠ 0 → ¬ O x ∧ F ≤ s.cur x) ∧
  (∀ r ∈ s.A, ¬ O r ∧ F ≤ s.cur r) ∧
  (∀ r ∈ s.A, ∀ B ∈ BS, s.arrow r B = 0) ∧
  (∀ x, ¬ O x → s.cur x = F → s.row x ∈ Arr s ⊔ Tsp BS)

variable (F : C) (O : ι → Prop) (BS : Set ι)

lemma Arr_mono {s s' : St ι K C} (h : (s.arrow '' (s.A : Set ι)) ⊆ s'.arrow '' (s'.A : Set ι)) :
    Arr s ≤ Arr s' := Submodule.span_mono h

lemma inv_step {s s' : St ι K C} (hi : Inv F O BS s) (hs : Step F O s s') : Inv F O BS s' := by
  obtain ⟨I1, I2, I3, I4⟩ := hi
  cases hs with
  | add d e q hco hO =>
    refine ⟨?_, I2, I3, ?_⟩
    · intro x B hB hx
      by_cases hxd : x = d
      · subst hxd
        simp only [Function.update_self, Pi.add_apply, Pi.smul_apply, smul_eq_mul] at hx
        by_cases h1 : s.row x B = 0
        · rw [h1, zero_add] at hx
          have h2 : s.row e B ≠ 0 := fun h => hx (by rw [h, mul_zero])
          obtain ⟨he, hle⟩ := I1 e B hB h2
          refine ⟨fun hOx => hO (Or.inl hOx) (hco ▸ hle), hco ▸ hle⟩
        · exact I1 x B hB h1
      · simpa [Function.update_of_ne hxd] using I1 x B hB (by simpa [Function.update_of_ne hxd] using hx)
    · intro x hx hcx
      by_cases hxd : x = d
      · subst hxd
        have hce : s.cur e = F := hco ▸ hcx
        have hOe : ¬ O e := fun h => hO (Or.inr h) (le_of_eq hcx.symm)
        have := I4 e hOe hce
        have h3 := I4 x hx hcx
        simp only [Function.update_self]
        exact add_mem h3 (Submodule.smul_mem _ _ this)
      · simp only []
        rw [Function.update_of_ne hxd]; exact I4 x hx hcx
  | scale d q =>
    refine ⟨?_, I2, I3, ?_⟩
    · intro x B hB hx
      by_cases hxd : x = d
      · subst hxd
        simp only [Function.update_self, Pi.smul_apply, smul_eq_mul] at hx
        exact I1 x B hB (fun h => hx (by rw [h, mul_zero]))
      · simpa [Function.update_of_ne hxd] using I1 x B hB (by simpa [Function.update_of_ne hxd] using hx)
    · intro x hx hcx
      by_cases hxd : x = d
      · subst hxd
        simp only [Function.update_self]
        exact Submodule.smul_mem _ _ (I4 x hx hcx)
      · simp only []
        rw [Function.update_of_ne hxd]; exact I4 x hx hcx
  | arrive r hr hlt =>
    have hnot : ¬ F ≤ s.cur r := not_le_of_gt hlt
    have hrA : r ∉ s.A := fun h => hnot (I2 r h).2
    refine ⟨?_, ?_, ?_, ?_⟩
    · intro x B hB hx
      by_cases hxr : x = r
      · subst hxr; simp [hr]
      · simpa [Function.update_of_ne hxr] using I1 x B hB hx
    · intro y hy
      by_cases hyr : y = r
      · subst hyr; simp [hr]
      · have hy' : y ∈ s.A := by simpa [hyr] using hy
        simpa [Function.update_of_ne hyr] using I2 y hy'
    · intro y hy B hB
      by_cases hyr : y = r
      · subst hyr
        simp only [Function.update_self]
        by_contra hne
        exact hnot (I1 y B hB hne).2
      · have hy' : y ∈ s.A := by simpa [hyr] using hy
        simpa [Function.update_of_ne hyr] using I3 y hy' B hB
    · intro x hx hcx
      by_cases hxr : x = r
      · subst hxr
        refine Submodule.mem_sup_left (Submodule.subset_span ⟨x, ?_, ?_⟩)
        · simp
        · simp
      · have hcx' : s.cur x = F := by simpa [Function.update_of_ne hxr] using hcx
        have h := I4 x hx hcx'
        have hle : Arr s ≤ Arr (St.mk s.row (Function.update s.cur r F) (insert r s.A) (Function.update s.arrow r (s.row r))) := by
          apply Arr_mono
          rintro _ ⟨y, hy, rfl⟩
          have hyr : y ≠ r := fun h => hrA (h ▸ hy)
          exact ⟨y, by simp [hy], by simp [Function.update_of_ne hyr]⟩
        exact sup_le_sup_right hle _ h
  | movePub r c hr hlt hne =>
    refine ⟨?_, ?_, I3, ?_⟩
    · intro x B hB hx
      by_cases hxr : x = r
      · subst hxr
        obtain ⟨h1, h2⟩ := I1 x B hB hx
        exact ⟨h1, by simpa using le_trans h2 hlt.le⟩
      · simpa [Function.update_of_ne hxr] using I1 x B hB hx
    · intro y hy
      by_cases hyr : y = r
      · subst hyr
        obtain ⟨h1, h2⟩ := I2 y hy
        exact ⟨h1, by simpa using le_trans h2 hlt.le⟩
      · simpa [Function.update_of_ne hyr] using I2 y hy
    · intro x hx hcx
      by_cases hxr : x = r
      · subst hxr; simp at hcx; exact absurd hcx hne
      · have hcx' : s.cur x = F := by simpa [Function.update_of_ne hxr] using hcx
        exact I4 x hx hcx'
  | moveOwn r c hr =>
    refine ⟨?_, ?_, I3, ?_⟩
    · intro x B hB hx
      by_cases hxr : x = r
      · subst hxr; exact absurd hr (I1 x B hB hx).1
      · simpa [Function.update_of_ne hxr] using I1 x B hB hx
    · intro y hy
      by_cases hyr : y = r
      · subst hyr; exact absurd hr (I2 y hy).1
      · simpa [Function.update_of_ne hyr] using I2 y hy
    · intro x hx hcx
      have hxr : x ≠ r := fun h => hx (h ▸ hr)
      exact I4 x hx (by simpa [Function.update_of_ne hxr] using hcx)
  | resetOwn r hr =>
    refine ⟨?_, I2, I3, ?_⟩
    · intro x B hB hx
      by_cases hxr : x = r
      · subst hxr; simp at hx
      · simpa [Function.update_of_ne hxr] using I1 x B hB (by simpa [Function.update_of_ne hxr] using hx)
    · intro x hx hcx
      have hxr : x ≠ r := fun h => hx (h ▸ hr)
      simp only []
      rw [Function.update_of_ne hxr]; exact I4 x hx hcx

lemma inv_init {s0 : St ι K C} (hBS : ∀ x, x ∈ BS ↔ (¬ O x ∧ s0.cur x = F))
    (h0row : ∀ r, ¬ O r → s0.row r = tok r) (h0own : ∀ r, O r → s0.row r = 0)
    (hA : s0.A = ∅) : Inv F O BS s0 := by
  refine ⟨?_, ?_, ?_, ?_⟩
  · intro x B hB hx
    by_cases hOx : O x
    · simp [h0own x hOx] at hx
    · rw [h0row x hOx] at hx
      have : B = x := by
        by_contra h; apply hx; simp [tok, Pi.single_apply, h]
      subst this
      exact ⟨hOx, le_of_eq ((hBS B).1 hB).2.symm⟩
  · intro r hr; simp [hA] at hr
  · intro r hr; simp [hA] at hr
  · intro x hx hcx
    have hxB : x ∈ BS := (hBS x).2 ⟨hx, hcx⟩
    rw [h0row x hx]
    exact Submodule.mem_sup_right (Submodule.subset_span ⟨x, hxB, rfl⟩)

theorem inv_reach {s0 s : St ι K C} (hBS : ∀ x, x ∈ BS ↔ (¬ O x ∧ s0.cur x = F))
    (h0row : ∀ r, ¬ O r → s0.row r = tok r) (h0own : ∀ r, O r → s0.row r = 0)
    (hA : s0.A = ∅) (hr : Relation.ReflTransGen (Step F O) s0 s) : Inv F O BS s := by
  induction hr with
  | refl => exact inv_init F O BS hBS h0row h0own hA
  | tail _ hs ih => exact inv_step F O BS ih hs

/-- **Lemma CC (chart-clean).** -/
theorem chart_clean {s0 s : St ι K C} (hBS : ∀ x, x ∈ BS ↔ (¬ O x ∧ s0.cur x = F))
    (h0row : ∀ r, ¬ O r → s0.row r = tok r) (h0own : ∀ r, O r → s0.row r = 0)
    (hA : s0.A = ∅) (hr : Relation.ReflTransGen (Step F O) s0 s)
    (hS : ∀ r ∈ s.A, s.cur r = F)
    (hB : ∀ r ∈ s.A, ∀ B ∈ BS, s.row r B = 0)
    (hI : LinearIndependent K (fun r : s.A => s.row r)) :
    Submodule.span K (s.row '' (s.A : Set ι)) = Arr s := by
  obtain ⟨I1, I2, I3, I4⟩ := inv_reach F O BS hBS h0row h0own hA hr
  have hle : Submodule.span K (s.row '' (s.A : Set ι)) ≤ Arr s := by
    rw [Submodule.span_le]
    rintro _ ⟨r, hrA, rfl⟩
    have h := I4 r (I2 r hrA).1 (hS r hrA)
    obtain ⟨a, ha, t, ht, hsum⟩ := Submodule.mem_sup.mp h
    -- a vanishes on BS, t vanishes off BS
    let Z : Submodule K (ι → K) :=
      { carrier := {v | ∀ B ∈ BS, v B = 0}
        add_mem' := fun ha hb B hB => by simp [ha B hB, hb B hB]
        zero_mem' := fun B hB => rfl
        smul_mem' := fun c v hv B hB => by simp [hv B hB] }
    let W : Submodule K (ι → K) :=
      { carrier := {v | ∀ i, i ∉ BS → v i = 0}
        add_mem' := fun ha hb i hi => by simp [ha i hi, hb i hi]
        zero_mem' := fun i hi => rfl
        smul_mem' := fun c v hv i hi => by simp [hv i hi] }
    have haZ : a ∈ Z := by
      have : Arr s ≤ Z := by
        rw [Arr, Submodule.span_le]
        rintro _ ⟨y, hy, rfl⟩
        exact fun B hB => I3 y hy B hB
      exact this ha
    have htW : t ∈ W := by
      have : Tsp (K := K) BS ≤ W := by
        rw [Tsp, Submodule.span_le]
        rintro _ ⟨B, hB, rfl⟩ i hi
        have : i ≠ B := fun h => hi (h ▸ hB)
        simp [tok, Pi.single_apply, this]
      exact this ht
    have ht0 : t = 0 := by
      funext i
      by_cases hi : i ∈ BS
      · have h1 : (a + t) i = s.row r i := by rw [hsum]
        have h2 := hB r hrA i hi
        have h3 := haZ i hi
        simp only [Pi.add_apply] at h1
        rw [h2, h3, zero_add] at h1
        exact h1
      · exact htW i hi
    rw [ht0, add_zero] at hsum
    rw [← hsum]; exact ha
  refine Submodule.eq_of_le_of_finrank_le hle ?_
  have h1 : finrank K (Submodule.span K (s.row '' (s.A : Set ι))) = s.A.card := by
    have := finrank_span_eq_card hI
    rw [Set.image_eq_range]
    simpa using this
  have h2 : finrank K (Arr s) ≤ s.A.card := by
    classical
    have := finrank_span_finset_le_card (R := K) (s.A.image s.arrow)
    rw [Finset.coe_image] at this
    exact this.trans Finset.card_image_le
  omega

/-- **C1 (arrival rows lie in W_F)**. -/
theorem c1_arrival_in_finals {s0 s : St ι K C} (hBS : ∀ x, x ∈ BS ↔ (¬ O x ∧ s0.cur x = F))
    (h0row : ∀ r, ¬ O r → s0.row r = tok r) (h0own : ∀ r, O r → s0.row r = 0)
    (hA : s0.A = ∅) (hr : Relation.ReflTransGen (Step F O) s0 s)
    (hS : ∀ r ∈ s.A, s.cur r = F)
    (hB : ∀ r ∈ s.A, ∀ B ∈ BS, s.row r B = 0)
    (hI : LinearIndependent K (fun r : s.A => s.row r)) (K' : ι) (hK : K' ∈ s.A) :
    s.arrow K' ∈ Submodule.span K (s.row '' (s.A : Set ι)) := by
  rw [chart_clean F O BS hBS h0row h0own hA hr hS hB hI]
  exact Submodule.subset_span ⟨K', hK, rfl⟩

/-- **C1 (copy-courier)**: an arrival `e_K + g` forces `g ∈ W_F + span e_K`. -/
theorem c1_copy {s0 s : St ι K C} (hBS : ∀ x, x ∈ BS ↔ (¬ O x ∧ s0.cur x = F))
    (h0row : ∀ r, ¬ O r → s0.row r = tok r) (h0own : ∀ r, O r → s0.row r = 0)
    (hA : s0.A = ∅) (hr : Relation.ReflTransGen (Step F O) s0 s)
    (hS : ∀ r ∈ s.A, s.cur r = F)
    (hB : ∀ r ∈ s.A, ∀ B ∈ BS, s.row r B = 0)
    (hI : LinearIndependent K (fun r : s.A => s.row r)) (K' : ι) (hK : K' ∈ s.A)
    (g : ι → K) (hg : s.arrow K' = tok K' + g) :
    g ∈ Submodule.span K (s.row '' (s.A : Set ι)) ⊔ Submodule.span K {tok (K := K) K'} := by
  have h := c1_arrival_in_finals F O BS hBS h0row h0own hA hr hS hB hI K' hK
  rw [hg] at h
  have : g = (tok K' + g) + (-1 : K) • tok K' := by simp
  rw [this]
  exact Submodule.add_mem _ (Submodule.mem_sup_left h)
    (Submodule.mem_sup_right (Submodule.smul_mem _ _ (Submodule.subset_span rfl)))

/-- arrivals are independent and `|A|` many. -/
theorem arrivals_finrank {s0 s : St ι K C} (hBS : ∀ x, x ∈ BS ↔ (¬ O x ∧ s0.cur x = F))
    (h0row : ∀ r, ¬ O r → s0.row r = tok r) (h0own : ∀ r, O r → s0.row r = 0)
    (hA : s0.A = ∅) (hr : Relation.ReflTransGen (Step F O) s0 s)
    (hS : ∀ r ∈ s.A, s.cur r = F)
    (hB : ∀ r ∈ s.A, ∀ B ∈ BS, s.row r B = 0)
    (hI : LinearIndependent K (fun r : s.A => s.row r)) :
    finrank K (Arr s) = s.A.card := by
  rw [← chart_clean F O BS hBS h0row h0own hA hr hS hB hI]
  have := finrank_span_eq_card hI
  rw [Set.image_eq_range]
  simpa using this


/-! ## Non-vacuity: ι = Fin 4 over 𝔽₂, charts ℕ, F = 2, owned = {3}.
Public 0,1 start at chart 0 with their tokens, public 2 starts AT F with its token, owned 3 starts at 0.
Run: ADD 0 += 1·1 (chart 0); public 0 arrives at F; owned 3 VISITS F (no ADD). -/
section inst
abbrev IK := ZMod 2
def Oi : Fin 4 → Prop := fun i => i = 3
def t0 : St (Fin 4) IK ℕ :=
  { row := fun i => if i = 3 then 0 else tok i, cur := fun i => if i = 2 then 2 else 0,
    A := ∅, arrow := fun _ => 0 }
def t1 : St (Fin 4) IK ℕ := { t0 with row := Function.update t0.row 0 (t0.row 0 + (1 : IK) • t0.row 1) }
def t2 : St (Fin 4) IK ℕ :=
  St.mk t1.row (Function.update t1.cur 0 2) (insert 0 t1.A) (Function.update t1.arrow 0 (t1.row 0))
def t3 : St (Fin 4) IK ℕ := { t2 with cur := Function.update t2.cur 3 2 }

lemma s01 : Step 2 Oi t0 t1 := Step.add (F := 2) (O := Oi) t0 0 1 1 (by simp [t0]) (by simp [Oi])
lemma s12 : Step 2 Oi t1 t2 := Step.arrive (F := 2) (O := Oi) t1 0 (by simp [Oi]) (by simp [t1, t0])
lemma s23 : Step 2 Oi t2 t3 := Step.moveOwn (F := 2) (O := Oi) t2 3 2 (by simp [Oi])
lemma reach3 : Relation.ReflTransGen (Step 2 Oi) t0 t3 :=
  ((Relation.ReflTransGen.single s01).tail s12).tail s23

def BSi : Set (Fin 4) := {x | ¬ Oi x ∧ t0.cur x = 2}

lemma nonvac :
    Submodule.span IK (t3.row '' (t3.A : Set (Fin 4))) = Arr t3 ∧ t3.A.card = 1 ∧ finrank IK (Arr t3) = 1 := by
  have hBS : ∀ x, x ∈ BSi ↔ (¬ Oi x ∧ t0.cur x = 2) := fun x => Iff.rfl
  have h0row : ∀ r, ¬ Oi r → t0.row r = tok r := by
    intro r hr; simp [t0, Oi] at hr ⊢; simp [hr]
  have h0own : ∀ r, Oi r → t0.row r = 0 := by
    intro r hr; simp [Oi] at hr; subst hr; simp [t0]
  have hS : ∀ r ∈ t3.A, t3.cur r = 2 := by
    intro r hr; simp [t3, t2, t1, t0] at hr; subst hr; simp [t3, t2]
  have hB : ∀ r ∈ t3.A, ∀ B ∈ BSi, t3.row r B = 0 := by
    intro r hr B hB
    simp [t3, t2, t1, t0] at hr; subst hr
    simp [BSi, Oi, t0] at hB
    obtain ⟨h1, h2⟩ := hB
    subst h2
    simp [t3, t2, t1, t0, tok]
  haveI : Unique ↥t3.A :=
    ⟨⟨⟨0, by simp [t3, t2, t1, t0]⟩⟩, fun a => Subtype.ext (by simpa [t3, t2, t1, t0] using a.2)⟩
  have hI : LinearIndependent IK (fun r : ↥t3.A => t3.row r) := by
    rw [linearIndependent_unique_iff]
    intro h
    have hd : ((default : ↥t3.A) : Fin 4) = 0 := by
      have h' : ((default : ↥t3.A) : Fin 4) ∈ (insert 0 (∅ : Finset (Fin 4))) := (default : ↥t3.A).2
      simpa using h'
    rw [hd] at h
    have := congrFun h 0
    simp [t3, t2, t1, t0, tok] at this
  refine ⟨chart_clean 2 Oi BSi hBS h0row h0own rfl reach3 hS hB hI, ?_, ?_⟩
  · simp [t3, t2, t1, t0]
  · rw [arrivals_finrank 2 Oi BSi hBS h0row h0own rfl reach3 hS hB hI]; simp [t3, t2, t1, t0]

end inst

#print axioms chart_clean
#print axioms c1_arrival_in_finals
#print axioms c1_copy
#print axioms arrivals_finrank
#print axioms nonvac
end ChartClean
