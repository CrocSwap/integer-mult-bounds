/-
UniInhabitWs4Reg (lane UNI-INHABIT, Nov 19).  The concrete tWs4 model for UniInhabitWs4Sound:
registers R = Reg (Fin 104) (Fin 1101) (Fin 180) (owned = the 180 owned LIFETIMES of tWs4: every INIT starts a fresh
owned register, since WordModel births need `unborn`), json codes j < 1697 (0..1500 public, 1501..1680 owned
lifetimes, 1681..1696 the 16 phantom x2/y2 of the 8 non-D ports); frames = 512-bit masks (chOf); `MWs4`;
`MWs4_ok` (bijection, pub = json public, mask ⊊ ⇒ chart <), all by kernel decide / bit lemmas.
`trWs4` = the 26 checkpointed segments (UniInhabitWs4Seg); `legalWs4 : Legal (pub caller7113) trWs4` and the end
tree relation (loc of every register = checkpoint ck26).
Kernel only: no sorry, no native_decide, no new axioms.
-/
import Nov15.UniFold7113Inst
import Nov15.UniInhabitWs4Sound
import Nov15.UniInhabitWs4Seg
import Nov15.UniInhabitWs4Tabs2

set_option linter.unusedSectionVars false

namespace UniInhabitWs4
open Uni WordModel Finset UniFold7113

abbrev R7 := Reg (Fin 104) (Fin 1101) (Fin 180)

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
  else .o ⟨p % 180, Nat.mod_lt _ (by norm_num)⟩

def lkr (X i : ℕ) : ℕ := X / 2 ^ (11 * i) % 2048

def idxOf : R7 → ℕ
  | .x p => lkr Tabs.xI p
  | .y p => lkr Tabs.yI p
  | .x2 p => lkr Tabs.x2I p
  | .y2 p => lkr Tabs.y2I p
  | .h i => lkr Tabs.hI i
  | .o i => 1501 + i

theorem idx_reg : ∀ j < 1697, idxOf (regOf j) = j := by decide +kernel

theorem reg_idx (r : R7) : regOf (idxOf r) = r ∧ idxOf r < 1697 := by
  cases r with
  | x p => revert p; decide +kernel
  | y p => revert p; decide +kernel
  | x2 p => revert p; decide +kernel
  | y2 p => revert p; decide +kernel
  | h i => revert i; decide +kernel
  | o i => revert i; decide +kernel

theorem pub_reg : ∀ j < 1697, pub caller7113 (regOf j) = decide (j < 1501) := by decide +kernel

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

/-- the tWs4 model. -/
def MWs4 : Model R7 := ⟨pub caller7113, regOf, 1697, chOf, Tabs.P⟩

theorem P_NP : Tabs.P.NP = 1501 := rfl
theorem P_NR : Tabs.P.NR = 1681 := rfl
theorem P_NF : Tabs.P.NF = 1096 := rfl

theorem MWs4_ok : MWs4.OK where
  inj := fun i j hi hj h => by
    have a := idx_reg i hi; have b := idx_reg j hj
    simp only [MWs4] at h; rw [← a, ← b, h]
  surj := fun r => ⟨idxOf r, (reg_idx r).2, (reg_idx r).1⟩
  hpb := fun j hj => by
    simp only [MWs4]; rw [pub_reg j hj]; simp [P_NP]
  hNR := by simp [MWs4, P_NR]
  hN := by simp [MWs4]
  hss := fun c d h => ssub_lt c d h

/-! ## the trace -/

open Tabs in
def LWs4 : List (List (Nat × Nat) × Tr Nat) :=
  [(seg0, ck1), (seg1, ck2), (seg2, ck3), (seg3, ck4), (seg4, ck5), (seg5, ck6), (seg6, ck7), (seg7, ck8),
   (seg8, ck9), (seg9, ck10), (seg10, ck11), (seg11, ck12), (seg12, ck13), (seg13, ck14), (seg14, ck15),
   (seg15, ck16), (seg16, ck17), (seg17, ck18), (seg18, ck19), (seg19, ck20), (seg20, ck21), (seg21, ck22),
   (seg22, ck23), (seg23, ck24), (seg24, ck25), (seg25, ck26)]

open Tabs in
theorem chainWs4 : chainOK Tabs.P ck0 LWs4 = true := by
  simp only [LWs4, chainOK, seg0_ok, seg1_ok, seg2_ok, seg3_ok, seg4_ok, seg5_ok, seg6_ok, seg7_ok, seg8_ok,
    seg9_ok, seg10_ok, seg11_ok, seg12_ok, seg13_ok, seg14_ok, seg15_ok, seg16_ok, seg17_ok, seg18_ok, seg19_ok,
    seg20_ok, seg21_ok, seg22_ok, seg23_ok, seg24_ok, seg25_ok, Bool.and_self]

theorem lastWs4 : lastCk Tabs.ck0 LWs4 = Tabs.ck26 := rfl

/-- the 210240 packed events of tWs4 (1501 public births, then the json program with owned lifetimes). -/
def evsWs4 : List PE := chainEvs LWs4

/-- **tWs4 as a Uni trace**. -/
def trWs4 : Trace R7 := evsWs4.map MWs4.toEv

theorem ck0_zero : ∀ j < 2048, gt 11 Tabs.ck0 j = 0 := by decide +kernel

theorem rel_init : MWs4.Rel (init : St R7) Tabs.ck0 := by
  intro j hj
  rw [ck0_zero j (by simp [MWs4] at hj; omega)]
  simp [Model.locOf, init]

theorem inv_init : MWs4.Inv (init : St R7) := by
  refine ⟨?_, ?_, ?_⟩ <;> simp [init]

theorem soundWs4 : Legal (pub caller7113) trWs4 ∧ MWs4.Rel (exec trWs4) Tabs.ck26 ∧ MWs4.Inv (exec trWs4) := by
  have := chain_sound MWs4_ok LWs4 Tabs.ck0 init chainWs4 rel_init inv_init
  rw [lastWs4] at this
  exact this

/-- **legalWs4**: tWs4 is a legal Uni / WordModel trace under the #7113 caller's public set. -/
theorem legalWs4 : Legal (pub caller7113) trWs4 := soundWs4.1

end UniInhabitWs4

#print axioms UniInhabitWs4.legalWs4
#print axioms UniInhabitWs4.soundWs4
