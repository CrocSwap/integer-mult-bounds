/-
UniInhabitReg (lane UNI-INHABIT, Nov 19).  The concrete t7669 model for UniInhabitSound:
registers R = Reg (Fin 104) (Fin 1101) (Fin 235) (owned = the 235 owned LIFETIMES of t7669: every INIT starts a fresh
owned register, since WordModel births need `unborn`), json codes j < 1752 (0..1500 public, 1501..1735 owned
lifetimes, 1736..1751 the 16 phantom x2/y2 of the 8 non-D ports); frames = 512-bit masks (chOf); `M7669`;
`M7669_ok` (bijection, pub = json public, mask ⊊ ⇒ chart <), all by kernel decide / bit lemmas.
`tr7669` = the 26 checkpointed segments (UniInhabitSeg); `legal7669 : Legal (pub caller7113) tr7669` and the end
tree relation (loc of every register = checkpoint ck26).
Kernel only: no sorry, no native_decide, no new axioms.
-/
import Nov15.UniFold7113Inst
import Nov15.UniInhabitSound
import Nov15.UniInhabitSeg
import Nov15.UniInhabitTabs2

set_option linter.unusedSectionVars false

namespace UniInhabit
open Uni WordModel Finset UniFold7113

abbrev R7 := Reg (Fin 104) (Fin 1101) (Fin 235)

def rc (j : ℕ) : ℕ := Tabs.regCode / 2 ^ (14 * j) % 2 ^ 14

def regOf (j : ℕ) : R7 :=
  let c := rc j
  let k := c / 2048
  let p := c % 2048
  if k = 0 then .x ⟨p % 104, Nat.mod_lt _ (by norm_num)⟩
  else if k = 1 then .y ⟨p % 104, Nat.mod_lt _ (by norm_num)⟩
  else if k = 2 then .x2 ⟨p % 104, Nat.mod_lt _ (by norm_num)⟩
  else if k = 3 then .y2 ⟨p % 104, Nat.mod_lt _ (by norm_num)⟩
  else if k = 4 then .h ⟨p % 1101, Nat.mod_lt _ (by norm_num)⟩
  else .o ⟨p % 235, Nat.mod_lt _ (by norm_num)⟩

def lkr (X i : ℕ) : ℕ := X / 2 ^ (11 * i) % 2048

def idxOf : R7 → ℕ
  | .x p => lkr Tabs.xI p
  | .y p => lkr Tabs.yI p
  | .x2 p => lkr Tabs.x2I p
  | .y2 p => lkr Tabs.y2I p
  | .h i => lkr Tabs.hI i
  | .o i => 1501 + i

theorem idx_reg : ∀ j < 1752, idxOf (regOf j) = j := by decide +kernel

theorem reg_idx (r : R7) : regOf (idxOf r) = r ∧ idxOf r < 1752 := by
  cases r with
  | x p => revert p; decide +kernel
  | y p => revert p; decide +kernel
  | x2 p => revert p; decide +kernel
  | y2 p => revert p; decide +kernel
  | h i => revert i; decide +kernel
  | o i => revert i; decide +kernel

theorem pub_reg : ∀ j < 1752, pub caller7113 (regOf j) = decide (j < 1501) := by decide +kernel

/-! ## frames as masks -/

def chOf (i : ℕ) : Ch := (range 512).filter (fun v => (gt 11 Tabs.maskT i).testBit v)

theorem mask_lt (mc md : ℕ) (h : mc &&& md = mc) (hd : md < 2 ^ 512) : mc < 2 ^ 512 :=
  lt_of_le_of_lt (h ▸ Nat.and_le_right) hd

theorem filt_ssub {mc md : ℕ} (h1 : mc &&& md = mc) (h2 : mc ≠ md) (hd : md < 2 ^ 512) :
    (range 512).filter (fun v => mc.testBit v) < (range 512).filter (fun v => md.testBit v) := by
  rw [Finset.lt_iff_ssubset, Finset.ssubset_iff_subset_ne]
  have hc := mask_lt mc md h1 hd
  refine ⟨?_, ?_⟩
  · intro v hv
    simp only [mem_filter, mem_range] at hv ⊢
    refine ⟨hv.1, ?_⟩
    have := congrArg (fun m => m.testBit v) h1
    simp only [Nat.testBit_and, hv.2, Bool.true_and] at this
    exact this
  · intro he
    apply h2
    apply Nat.eq_of_testBit_eq
    intro v
    by_cases hv : v < 512
    · have := congrArg (fun S => v ∈ S) he
      simp only [mem_filter, mem_range, hv, true_and, eq_iff_iff] at this
      cases a : mc.testBit v <;> cases b : md.testBit v <;> simp_all
    · have e1 : mc.testBit v = false := Nat.testBit_lt_two_pow (lt_of_lt_of_le hc (Nat.pow_le_pow_right (by norm_num) (by omega)))
      have e2 : md.testBit v = false := Nat.testBit_lt_two_pow (lt_of_lt_of_le hd (Nat.pow_le_pow_right (by norm_num) (by omega)))
      rw [e1, e2]

theorem ssub_lt (c d : ℕ) (h : Tabs.P.ssub c d = true) : chOf c < chOf d := by
  unfold Par.ssub at h
  simp only [Bool.and_eq_true, beq_iff, blt_iff, Bool.not_eq_true'] at h
  obtain ⟨⟨h1, h2⟩, h3⟩ := h
  have h2' : gt 11 Tabs.P.mask c ≠ gt 11 Tabs.P.mask d := by
    intro e; rw [e] at h2; simp [Nat.beq_refl] at h2
  exact filt_ssub h1 h2' h3

/-- the t7669 model. -/
def M7669 : Model R7 := ⟨pub caller7113, regOf, 1752, chOf, Tabs.P⟩

theorem P_NP : Tabs.P.NP = 1501 := rfl
theorem P_NR : Tabs.P.NR = 1736 := rfl
theorem P_NF : Tabs.P.NF = 1097 := rfl

theorem M7669_ok : M7669.OK where
  inj := fun i j hi hj h => by
    have a := idx_reg i hi; have b := idx_reg j hj
    simp only [M7669] at h; rw [← a, ← b, h]
  surj := fun r => ⟨idxOf r, (reg_idx r).2, (reg_idx r).1⟩
  hpb := fun j hj => by
    simp only [M7669]; rw [pub_reg j hj]; simp [P_NP]
  hNR := by simp [M7669, P_NR]
  hN := by simp [M7669]
  hss := fun c d h => ssub_lt c d h

/-! ## the trace -/

open Tabs in
def L7669 : List (List (Nat × Nat) × Tr Nat) :=
  [(seg0, ck1), (seg1, ck2), (seg2, ck3), (seg3, ck4), (seg4, ck5), (seg5, ck6), (seg6, ck7), (seg7, ck8),
   (seg8, ck9), (seg9, ck10), (seg10, ck11), (seg11, ck12), (seg12, ck13), (seg13, ck14), (seg14, ck15),
   (seg15, ck16), (seg16, ck17), (seg17, ck18), (seg18, ck19), (seg19, ck20), (seg20, ck21), (seg21, ck22),
   (seg22, ck23), (seg23, ck24), (seg24, ck25), (seg25, ck26)]

open Tabs in
theorem chain7669 : chainOK Tabs.P ck0 L7669 = true := by
  simp only [L7669, chainOK, seg0_ok, seg1_ok, seg2_ok, seg3_ok, seg4_ok, seg5_ok, seg6_ok, seg7_ok, seg8_ok,
    seg9_ok, seg10_ok, seg11_ok, seg12_ok, seg13_ok, seg14_ok, seg15_ok, seg16_ok, seg17_ok, seg18_ok, seg19_ok,
    seg20_ok, seg21_ok, seg22_ok, seg23_ok, seg24_ok, seg25_ok, Bool.and_self]

theorem last7669 : lastCk Tabs.ck0 L7669 = Tabs.ck26 := rfl

/-- the 152023 packed events of t7669 (1501 public births, then the json program with owned lifetimes). -/
def evs7669 : List PE := chainEvs L7669

/-- **t7669 as a Uni trace**. -/
def tr7669 : Trace R7 := evs7669.map M7669.toEv

theorem ck0_zero : ∀ j < 2048, gt 11 Tabs.ck0 j = 0 := by decide +kernel

theorem rel_init : M7669.Rel (init : St R7) Tabs.ck0 := by
  intro j hj
  rw [ck0_zero j (by simp [M7669] at hj; omega)]
  simp [Model.locOf, init]

theorem inv_init : M7669.Inv (init : St R7) := by
  refine ⟨?_, ?_, ?_⟩ <;> simp [init]

theorem sound7669 : Legal (pub caller7113) tr7669 ∧ M7669.Rel (exec tr7669) Tabs.ck26 ∧ M7669.Inv (exec tr7669) := by
  have := chain_sound M7669_ok L7669 Tabs.ck0 init chain7669 rel_init inv_init
  rw [last7669] at this
  exact this

/-- **legal7669**: t7669 is a legal Uni / WordModel trace under the #7113 caller's public set. -/
theorem legal7669 : Legal (pub caller7113) tr7669 := sound7669.1

end UniInhabit

#print axioms UniInhabit.legal7669
#print axioms UniInhabit.sound7669
