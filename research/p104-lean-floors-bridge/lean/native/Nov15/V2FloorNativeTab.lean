/-
V2FloorNativeTab (lane LEAN-NEXT21, Nov 16): membership tables for subspaces of F₂⁹ and a complete DFS over all of them.
Part of the SEPARATE native_decide route (V2FloorNative*). This file itself uses no native_decide.

`Rep t S`: the 512-bit number t is the membership table of S (bit v ⇔ vec v ∈ S).
`go` walks every subspace exactly once through the tree  Node j S ℓ n  (S ≤ F₂ʲ, ℓ = set of lead positions, n = dim S);
`go_sound` : if `go` returns true then every subspace S of F₂⁹ satisfies Q S, for any predicate Q implied by the
node check.  Completeness (`node_complete`) is proved by the lead-position reduction argument.
-/
import Nov15.V2FloorBound
import Mathlib.Data.Nat.Bitwise

namespace V2Floor
open Finset Module
attribute [local instance] Classical.propDecidable
set_option maxHeartbeats 2000000

theorem vec_zero : vec 0 = 0 := by funext i; simp [vec]

theorem vec_xor (a b : ℕ) : vec (a ^^^ b) = vec a + vec b := by
  funext i
  simp only [vec, Nat.testBit_xor, Pi.add_apply]
  cases a.testBit i <;> cases b.testBit i <;> decide

theorem vec_inj {a b : ℕ} (ha : a < 512) (hb : b < 512) (h : vec a = vec b) : a = b := by
  apply Nat.eq_of_testBit_eq
  intro i
  by_cases hi : i < 9
  · have := congrFun h ⟨i, hi⟩
    simp only [vec] at this
    cases h1 : a.testBit i <;> cases h2 : b.testBit i <;> simp_all
  · have h9 : 9 ≤ i := by omega
    have e1 : a.testBit i = false := Nat.testBit_eq_false_of_lt (lt_of_lt_of_le ha (by
      calc 512 = 2 ^ 9 := by norm_num
        _ ≤ 2 ^ i := Nat.pow_le_pow_right (by norm_num) h9))
    have e2 : b.testBit i = false := Nat.testBit_eq_false_of_lt (lt_of_lt_of_le hb (by
      calc 512 = 2 ^ 9 := by norm_num
        _ ≤ 2 ^ i := Nat.pow_le_pow_right (by norm_num) h9))
    rw [e1, e2]

theorem vec_surj (x : Vec) : ∃ v < 512, vec v = x := by
  let f : Fin 512 → Vec := fun v => vec v.val
  have hinj : Function.Injective f := fun a b h => Fin.ext (vec_inj a.2 b.2 h)
  have hcard : Fintype.card (Fin 512) = Fintype.card Vec := by
    simp [Vec, Fintype.card_fun, ZMod.card]
  obtain ⟨v, hv⟩ := ((Fintype.bijective_iff_injective_and_card f).2 ⟨hinj, hcard⟩).2 x
  exact ⟨v.val, v.2, hv⟩

/-- translation of a membership table by w (v ↦ v ⊕ w). -/
def tr (t w : ℕ) : ℕ :=
  (List.range 512).foldl (fun acc v => if t.testBit v then acc ||| (1 <<< (v ^^^ w)) else acc) 0

def addv (t w : ℕ) : ℕ := t ||| tr t w

theorem testBit_one_shl (j k : ℕ) : (1 <<< j).testBit k = decide (j = k) := by
  rw [Nat.one_shiftLeft, Nat.testBit_two_pow]

theorem foldl_tr (t w : ℕ) (l : List ℕ) (acc k : ℕ) :
    (l.foldl (fun acc v => if t.testBit v then acc ||| (1 <<< (v ^^^ w)) else acc) acc).testBit k =
      (acc.testBit k || decide (∃ v ∈ l, t.testBit v = true ∧ (v ^^^ w) = k)) := by
  induction l generalizing acc with
  | nil => simp
  | cons v l ih =>
    simp only [List.foldl_cons, ih]
    by_cases hv : t.testBit v = true
    · simp only [hv, if_true, Nat.testBit_or, testBit_one_shl, List.mem_cons]
      by_cases hk : (v ^^^ w) = k
      · simp [hk, hv]
      · simp [hk, hv]
    · simp [hv]

theorem tr_testBit (t w k : ℕ) (hw : w < 512) (hk : k < 512) : (tr t w).testBit k = t.testBit (k ^^^ w) := by
  unfold tr
  rw [foldl_tr]
  simp only [Nat.zero_testBit, Bool.false_or]
  have hx : (k ^^^ w) < 512 := by
    have := Nat.xor_lt_two_pow (n := 9) (x := k) (y := w) (by norm_num; omega) (by norm_num; omega)
    norm_num at this; exact this
  rw [Bool.eq_iff_iff, decide_eq_true_iff]
  constructor
  · rintro ⟨v, _, hv, hvk⟩
    have : v = k ^^^ w := by rw [← hvk]; simp [Nat.xor_assoc]
    rw [← this]; exact hv
  · intro h
    exact ⟨k ^^^ w, List.mem_range.2 hx, h, by simp [Nat.xor_assoc]⟩

/-- t is the membership table of S. -/
def Rep (t : ℕ) (S : Sub) : Prop := ∀ v < 512, t.testBit v = decide (vec v ∈ S)

theorem vec_add_self (a : ℕ) : vec a + vec a = 0 := by
  funext i; simp only [vec, Pi.add_apply, Pi.zero_apply]; split_ifs <;> decide

theorem Rep_bot : Rep 1 ⊥ := by
  intro v hv
  rw [Bool.eq_iff_iff, decide_eq_true_iff, Nat.testBit_one_eq_true_iff_self_eq_zero, Submodule.mem_bot]
  constructor
  · rintro rfl; exact vec_zero
  · intro h; exact vec_inj hv (by norm_num) (h.trans vec_zero.symm)

theorem mem_sup_vec (S : Sub) (v w : ℕ) :
    vec v ∈ S ⊔ Submodule.span (ZMod 2) {vec w} ↔ vec v ∈ S ∨ vec (v ^^^ w) ∈ S := by
  rw [Submodule.mem_sup]
  constructor
  · rintro ⟨y, hy, z, hz, hyz⟩
    obtain ⟨a, rfl⟩ := Submodule.mem_span_singleton.1 hz
    rcases (by decide : ∀ a : ZMod 2, a = 0 ∨ a = 1) a with rfl | rfl
    · left; simp only [zero_smul, add_zero] at hyz; rw [← hyz]; exact hy
    · right
      simp only [one_smul] at hyz
      have : vec (v ^^^ w) = y := by
        rw [vec_xor, ← hyz, add_assoc, vec_add_self, add_zero]
      rw [this]; exact hy
  · rintro (h | h)
    · exact ⟨_, h, 0, Submodule.zero_mem _, by simp⟩
    · refine ⟨_, h, vec w, Submodule.subset_span rfl, ?_⟩
      rw [vec_xor, add_assoc, vec_add_self]; simp

theorem Rep_add {t w : ℕ} {S : Sub} (h : Rep t S) (hw : w < 512) :
    Rep (addv t w) (S ⊔ Submodule.span (ZMod 2) {vec w}) := by
  intro v hv
  have hx : (v ^^^ w) < 512 := by
    have := Nat.xor_lt_two_pow (n := 9) (x := v) (y := w) (by norm_num; omega) (by norm_num; omega)
    norm_num at this; exact this
  unfold addv
  rw [Nat.testBit_or, tr_testBit t w v hw hv, h v hv, h _ hx]
  have := mem_sup_vec S v w
  by_cases h1 : vec v ∈ S <;> by_cases h2 : vec (v ^^^ w) ∈ S <;> simp_all

def memM (S : Sub) (v : ℕ) : Prop := vec v ∈ S

structure St where
  j : ℕ
  S : Sub
  l : ℕ
  n : ℕ

inductive Step : St → St → Prop
  | skip (j S l n) : j < 9 → Step ⟨j, S, l, n⟩ ⟨j + 1, S, l, n⟩
  | add (j S l n r) : j < 9 → r < 2 ^ j → r &&& l = 0 →
      Step ⟨j, S, l, n⟩ ⟨j + 1, S ⊔ Submodule.span (ZMod 2) {vec (2 ^ j ||| r)}, l ||| 2 ^ j, n + 1⟩

def Inv (st : St) : Prop :=
  st.j ≤ 9 ∧ (∀ v < 512, memM st.S v → v < 2 ^ st.j) ∧ fdim st.S = st.n ∧ st.l < 2 ^ st.j ∧
    ∀ x < 2 ^ st.j, ∃ s < 512, memM st.S s ∧ (x ^^^ s) &&& st.l = 0

def init : St := ⟨0, ⊥, 0, 0⟩

theorem lt_two_pow_of_bits {x j : ℕ} (h : ∀ i, j ≤ i → x.testBit i = false) : x < 2 ^ j :=
  Nat.lt_pow_two_of_testBit x h

theorem bits_of_lt {x j : ℕ} (h : x < 2 ^ j) (i : ℕ) (hi : j ≤ i) : x.testBit i = false :=
  Nat.testBit_eq_false_of_lt (lt_of_lt_of_le h (Nat.pow_le_pow_right (by norm_num) hi))

theorem inv_init : Inv init := by
  refine ⟨by norm_num [init], ?_, ?_, by simp [init], ?_⟩
  · intro v hv hm
    simp only [init, memM, Submodule.mem_bot] at hm
    have := vec_inj hv (by norm_num) (hm.trans vec_zero.symm)
    simp [init, this]
  · show fdim ⊥ = 0
    unfold fdim; exact Submodule.finrank_eq_zero.2 rfl
  · intro x hx
    have : x = 0 := by simpa [init] using hx
    exact ⟨0, by norm_num, by simp [init, memM, vec_zero], by simp [this, init]⟩

/-- clearing bit j of x < 2^(j+1) with bit j set. -/
theorem clear_bit {x j : ℕ} (hx : x < 2 ^ (j + 1)) (hb : ¬ x < 2 ^ j) : (x ^^^ 2 ^ j) < 2 ^ j := by
  apply lt_two_pow_of_bits
  intro i hi
  rw [Nat.testBit_xor, Nat.testBit_two_pow]
  rcases Nat.eq_or_lt_of_le hi with h | h
  · subst h
    have : x.testBit j = true := by
      by_contra hc
      apply hb
      apply lt_two_pow_of_bits
      intro i hi
      rcases Nat.eq_or_lt_of_le hi with h | h
      · subst h; simpa using hc
      · exact bits_of_lt hx i h
    simp [this]
  · have := bits_of_lt hx i h
    simp [this]
    omega

theorem and_pow_lt {z j : ℕ} (hz : z < 2 ^ j) : z &&& 2 ^ j = 0 := by
  apply Nat.eq_of_testBit_eq
  intro i
  simp only [Nat.testBit_and, Nat.testBit_two_pow, Nat.zero_testBit]
  by_cases h : j = i
  · subst h; simp [bits_of_lt hz j le_rfl]
  · simp [h]

theorem and_xor_pow {x s l j : ℕ} (hl : l < 2 ^ j) : ((x ^^^ 2 ^ j) ^^^ s) &&& l = (x ^^^ s) &&& l := by
  apply Nat.eq_of_testBit_eq
  intro i
  simp only [Nat.testBit_and, Nat.testBit_xor, Nat.testBit_two_pow]
  by_cases h : j = i
  · subst h; simp [bits_of_lt hl j le_rfl]
  · simp [h]

theorem or_eq_xor {r j : ℕ} (hr : r < 2 ^ j) : 2 ^ j ||| r = 2 ^ j ^^^ r := by
  apply Nat.eq_of_testBit_eq
  intro i
  simp only [Nat.testBit_or, Nat.testBit_xor, Nat.testBit_two_pow]
  by_cases h : j = i
  · subst h; simp [bits_of_lt hr j le_rfl]
  · simp [h]

theorem xor_lt' {a b n : ℕ} (ha : a < 2 ^ n) (hb : b < 2 ^ n) : a ^^^ b < 2 ^ n := Nat.xor_lt_two_pow ha hb

theorem pow_succ_le {j : ℕ} (h : j < 9) : 2 ^ (j + 1) ≤ 512 := by
  calc 2 ^ (j + 1) ≤ 2 ^ 9 := Nat.pow_le_pow_right (by norm_num) (by omega)
    _ = 512 := by norm_num

theorem inv_skip {j : ℕ} {S : Sub} {l n : ℕ} (hj : j < 9) (h : Inv ⟨j, S, l, n⟩) : Inv ⟨j + 1, S, l, n⟩ := by
  obtain ⟨h1, h2, h3, h4, h5⟩ := h
  simp only at h1 h2 h3 h4 h5
  have hp : 2 ^ j ≤ 2 ^ (j + 1) := Nat.pow_le_pow_right (by norm_num) (by omega)
  refine ⟨by simp only; omega, ?_, h3, ?_, ?_⟩
  · intro v hv hm; exact lt_of_lt_of_le (h2 v hv hm) hp
  · exact lt_of_lt_of_le h4 hp
  · intro x hx
    simp only at hx
    by_cases hxj : x < 2 ^ j
    · exact h5 x hxj
    · obtain ⟨s, hs, hms, hz⟩ := h5 (x ^^^ 2 ^ j) (clear_bit hx hxj)
      exact ⟨s, hs, hms, by simpa [and_xor_pow h4] using hz⟩

theorem inv_add {j : ℕ} {S : Sub} {l n r : ℕ} (hj : j < 9) (hr : r < 2 ^ j) (h : Inv ⟨j, S, l, n⟩) :
    Inv ⟨j + 1, S ⊔ Submodule.span (ZMod 2) {vec (2 ^ j ||| r)}, l ||| 2 ^ j, n + 1⟩ := by
  obtain ⟨h1, h2, h3, h4, h5⟩ := h
  simp only at h1 h2 h3 h4 h5
  have hp : 2 ^ (j + 1) = 2 * 2 ^ j := by rw [pow_succ]; ring
  have hle : 2 ^ (j + 1) ≤ 512 := pow_succ_le hj
  set w := 2 ^ j ||| r with hw
  have hwx : w = 2 ^ j ^^^ r := or_eq_xor hr
  have hw1 : w < 2 ^ (j + 1) := by rw [hwx]; apply xor_lt' <;> omega
  have hw2 : 2 ^ j ≤ w := by rw [hw]; exact Nat.left_le_or
  have hw512 : w < 512 := by omega
  have hwS : ¬ memM S w := fun hm => by have := h2 w hw512 hm; omega
  have hmemS' : ∀ v, memM (S ⊔ Submodule.span (ZMod 2) {vec w}) v ↔ memM S v ∨ memM S (v ^^^ w) :=
    fun v => mem_sup_vec S v w
  have hwS' : memM (S ⊔ Submodule.span (ZMod 2) {vec w}) w := by
    rw [hmemS']; right; simp only [Nat.xor_self, memM, vec_zero]; exact Submodule.zero_mem _
  refine ⟨by simp only; omega, ?_, ?_, ?_, ?_⟩
  · intro v hv hm
    simp only
    rw [hmemS'] at hm
    rcases hm with hm | hm
    · have := h2 v hv hm; omega
    · have hu : (v ^^^ w) < 512 := by
        have := Nat.xor_lt_two_pow (n := 9) (x := v) (y := w) (by norm_num; omega) (by norm_num; omega)
        norm_num at this; exact this
      have := h2 _ hu hm
      have : v = (v ^^^ w) ^^^ w := by simp [Nat.xor_assoc]
      rw [this]; exact xor_lt' (by omega) hw1
  · show fdim (S ⊔ Submodule.span (ZMod 2) {vec w}) = n + 1
    unfold fdim
    rw [Submodule.finrank_sup_span_singleton (v := vec w) (fun hv => hwS hv)]
    rw [← h3]; rfl
  · show l ||| 2 ^ j < 2 ^ (j + 1)
    exact Nat.or_lt_two_pow (by omega) (by omega)
  · intro x hx
    simp only at hx
    by_cases hxj : x < 2 ^ j
    · obtain ⟨s, hs, hms, hz⟩ := h5 x hxj
      refine ⟨s, hs, ?_, ?_⟩
      · exact Submodule.mem_sup_left hms
      · have hsj := h2 s hs hms
        rw [Nat.and_or_distrib_left, hz, and_pow_lt (xor_lt' hxj hsj)]; simp
    · have hx' : (x ^^^ w) < 2 ^ j := by
        rw [hwx, ← Nat.xor_assoc]; exact xor_lt' (clear_bit hx hxj) hr
      obtain ⟨s, hs, hms, hz⟩ := h5 _ hx'
      have hsj := h2 s hs hms
      refine ⟨s ^^^ w, ?_, ?_, ?_⟩
      · have := Nat.xor_lt_two_pow (n := 9) (x := s) (y := w) (by norm_num; omega) (by norm_num; omega)
        norm_num at this; exact this
      · rw [hmemS']
        right
        have : (s ^^^ w) ^^^ w = s := by simp [Nat.xor_assoc]
        rw [this]; exact hms
      · have e : x ^^^ (s ^^^ w) = (x ^^^ w) ^^^ s := by
          simp [Nat.xor_assoc, Nat.xor_comm, Nat.xor_left_comm]
        rw [e, Nat.and_or_distrib_left, hz, and_pow_lt (xor_lt' hx' hsj)]; simp

theorem inv_step {a b : St} (h : Step a b) (ha : Inv a) : Inv b := by
  cases h with
  | skip j S l n hj => exact inv_skip hj ha
  | add j S l n r hj hr _ => exact inv_add hj hr ha

theorem inv_rtg {a b : St} (h : Relation.ReflTransGen Step a b) (ha : Inv a) : Inv b := by
  induction h with
  | refl => exact ha
  | tail _ hs ih => exact inv_step hs ih

/-- vectors supported on the first j coordinates. -/
def Flt (j : ℕ) : Sub where
  carrier := {x | ∀ i : Fin 9, j ≤ i.val → x i = 0}
  add_mem' := by intro a b ha hb i hi; simp [ha i hi, hb i hi]
  zero_mem' := by intro i _; rfl
  smul_mem' := by intro c x hx i hi; simp [hx i hi]

theorem vec_mem_Flt {j v : ℕ} (hv : v < 512) : vec v ∈ Flt j ↔ v < 2 ^ j := by
  constructor
  · intro h
    apply lt_two_pow_of_bits
    intro i hi
    by_cases h9 : i < 9
    · have := h ⟨i, h9⟩ hi
      simp only [vec] at this
      by_contra hc; simp [Bool.not_eq_false] at hc; simp [hc] at this
    · exact bits_of_lt (j := 9) (by norm_num; omega) i (by omega)
  · intro h i hi
    simp [vec, bits_of_lt h i hi]

theorem memM_xor {S : Sub} {a b : ℕ} (ha : memM S a) (hb : memM S b) : memM S (a ^^^ b) := by
  unfold memM at *; rw [vec_xor]; exact S.add_mem ha hb

theorem complete : ∀ j, j ≤ 9 → ∀ X : Sub, (∀ v < 512, memM X v → v < 2 ^ j) →
    ∃ l n, Relation.ReflTransGen Step init ⟨j, X, l, n⟩ := by
  intro j
  induction j with
  | zero =>
    intro _ X hX
    have : X = ⊥ := by
      rw [eq_bot_iff]
      intro x hx
      obtain ⟨v, hv, rfl⟩ := vec_surj x
      have := hX v hv hx
      have : v = 0 := by simpa using this
      subst this; rw [vec_zero]; exact Submodule.zero_mem _
    subst this
    exact ⟨0, 0, Relation.ReflTransGen.refl⟩
  | succ j ih =>
    intro hj X hX
    have hj9 : j < 9 := by omega
    set X' : Sub := X ⊓ Flt j with hX'
    have hX'm : ∀ v < 512, memM X' v → v < 2 ^ j := by
      intro v hv hm
      exact (vec_mem_Flt hv).1 hm.2
    obtain ⟨l, n, hr⟩ := ih (by omega) X' hX'm
    have hinv : Inv ⟨j, X', l, n⟩ := inv_rtg hr inv_init
    by_cases hall : ∀ v < 512, memM X v → v < 2 ^ j
    · have : X' = X := by
        apply le_antisymm inf_le_left
        intro x hx
        refine ⟨hx, ?_⟩
        obtain ⟨v, hv, rfl⟩ := vec_surj x
        exact (vec_mem_Flt hv).2 (hall v hv hx)
      rw [this] at hr
      exact ⟨l, n, hr.tail (by rw [this] at *; exact Step.skip j X l n hj9)⟩
    · push Not at hall
      obtain ⟨x, hx512, hxX, hxj⟩ := hall
      have hx2 := hX x hx512 hxX
      have hy : x - 2 ^ j < 2 ^ j := by
        have : 2 ^ (j + 1) = 2 * 2 ^ j := by rw [pow_succ]; ring
        omega
      obtain ⟨s, hs512, hsX', hz⟩ := hinv.2.2.2.2 (x - 2 ^ j) hy
      obtain ⟨r, hrdef⟩ : ∃ r, r = (x - 2 ^ j) ^^^ s := ⟨_, rfl⟩
      have hsj : s < 2 ^ j := hinv.2.1 s hs512 hsX'
      have hrj : r < 2 ^ j := by rw [hrdef]; exact xor_lt' hy hsj
      have hrl : r &&& l = 0 := by rw [hrdef]; exact hz
      have hxor : x = 2 ^ j ^^^ (x - 2 ^ j) := by
        have h1 := Nat.two_pow_add_eq_or_of_lt hy 1
        simp only [Nat.mul_one] at h1
        rw [or_eq_xor hy] at h1
        omega
      have hvx : (2 ^ j ||| r) = x ^^^ s := by
        rw [or_eq_xor hrj, hrdef]
        conv_rhs => rw [hxor]
        simp [Nat.xor_assoc]
      have hv512 : (2 ^ j ||| r) < 512 := by
        have := pow_succ_le hj9
        have hp : 2 ^ (j + 1) = 2 * 2 ^ j := by rw [pow_succ]; ring
        have hv1 : (2 ^ j ||| r) < 2 ^ (j + 1) := by
          rw [or_eq_xor hrj]; apply xor_lt' <;> omega
        omega
      have hstep := Step.add j X' l n r hj9 hrj hrl
      have hvX : memM X (2 ^ j ||| r) := by rw [hvx]; exact memM_xor hxX hsX'.1
      have hvlo : 2 ^ j ≤ (2 ^ j ||| r) := Nat.left_le_or
      have heq : X = X' ⊔ Submodule.span (ZMod 2) {vec (2 ^ j ||| r)} := by
        apply le_antisymm
        · intro y hy'
          obtain ⟨u, hu, rfl⟩ := vec_surj y
          have hu2 := hX u hu hy'
          rw [mem_sup_vec]
          by_cases huj : u < 2 ^ j
          · left; exact ⟨hy', (vec_mem_Flt hu).2 huj⟩
          · right
            have hu3 : (u ^^^ (2 ^ j ||| r)) < 2 ^ j := by
              rw [or_eq_xor hrj, ← Nat.xor_assoc]; exact xor_lt' (clear_bit hu2 huj) hrj
            have hu512 : (u ^^^ (2 ^ j ||| r)) < 512 := by
              have := pow_succ_le hj9
              have : 2 ^ j ≤ 2 ^ (j + 1) := Nat.pow_le_pow_right (by norm_num) (by omega)
              omega
            exact ⟨memM_xor hy' hvX, (vec_mem_Flt hu512).2 hu3⟩
        · apply sup_le inf_le_left
          rw [Submodule.span_le]
          intro z hz; rw [Set.mem_singleton_iff.1 hz]; exact hvX
      have := hr.tail hstep
      rw [← heq] at this
      exact ⟨l ||| 2 ^ j, n + 1, this⟩

/-- the DFS over every subspace; `chk t n` is run on each (table, dim). -/
def go (chk : ℕ → ℕ → Bool) : ℕ → ℕ → ℕ → ℕ → ℕ → Bool
  | 0, _, t, _, n => chk t n
  | k + 1, j, t, l, n =>
    go chk k (j + 1) t l n &&
    (List.range (2 ^ j)).all (fun r =>
      decide (r &&& l ≠ 0) || go chk k (j + 1) (addv t (2 ^ j ||| r)) (l ||| 2 ^ j) (n + 1))

theorem rtg_j {a b : St} (h : Relation.ReflTransGen Step a b) : a.j ≤ b.j := by
  induction h with
  | refl => exact le_rfl
  | tail _ hs ih => cases hs <;> simp only at ih ⊢ <;> omega

theorem go_sound (chk : ℕ → ℕ → Bool) : ∀ k j t l n (S : Sub), Rep t S → j + k = 9 →
    go chk k j t l n = true → ∀ S2 l2 n2,
      Relation.ReflTransGen Step ⟨j, S, l, n⟩ ⟨9, S2, l2, n2⟩ → ∃ t2, Rep t2 S2 ∧ chk t2 n2 = true := by
  intro k
  induction k with
  | zero =>
    intro j t l n S hrep hj hgo S2 l2 n2 hr
    simp only [go] at hgo
    rcases Relation.ReflTransGen.cases_head hr with h | ⟨c, hs, _⟩
    · simp only [St.mk.injEq] at h
      obtain ⟨_, rfl, _, rfl⟩ := h
      exact ⟨t, hrep, hgo⟩
    · cases hs <;> omega
  | succ k ih =>
    intro j t l n S hrep hj hgo S2 l2 n2 hr
    have hj9 : j < 9 := by omega
    simp only [go, Bool.and_eq_true, List.all_eq_true] at hgo
    rcases Relation.ReflTransGen.cases_head hr with h | ⟨c, hs, hrest⟩
    · simp only [St.mk.injEq] at h; omega
    · cases hs with
      | skip _ _ _ _ _ => exact ih (j + 1) t l n S hrep (by omega) hgo.1 S2 l2 n2 hrest
      | add _ _ _ _ r _ hr2 hrl =>
        have hmem := hgo.2 r (List.mem_range.2 hr2)
        simp only [Bool.or_eq_true, decide_eq_true_eq] at hmem
        rcases hmem with h | h
        · exact absurd hrl h
        · have hw : (2 ^ j ||| r) < 512 := by
            have := pow_succ_le hj9
            have hp : 2 ^ (j + 1) = 2 * 2 ^ j := by rw [pow_succ]; ring
            have : (2 ^ j ||| r) < 2 ^ (j + 1) := by
              rw [or_eq_xor hr2]; apply xor_lt' <;> omega
            omega
          exact ih (j + 1) _ _ _ _ (Rep_add hrep hw) (by omega) h S2 l2 n2 hrest

theorem enum_all (chk : ℕ → ℕ → Bool) (h : go chk 9 0 1 0 0 = true) :
    ∀ S : Sub, ∃ t n, Rep t S ∧ fdim S = n ∧ chk t n = true := by
  intro S
  obtain ⟨l, n, hr⟩ := complete 9 le_rfl S (fun v hv _ => by simpa using hv)
  have hinv := inv_rtg hr inv_init
  obtain ⟨t2, ht2, hc⟩ := go_sound chk 9 0 1 0 0 ⊥ Rep_bot rfl h S l n hr
  exact ⟨t2, n, ht2, hinv.2.2.1, hc⟩

end V2Floor
