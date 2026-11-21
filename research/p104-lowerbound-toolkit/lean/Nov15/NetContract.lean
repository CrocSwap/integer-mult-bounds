import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.Algebra.Field.ZMod
import Mathlib.Tactic.FieldSimp
import Mathlib.LinearAlgebra.Matrix.NonsingularInverse
import Mathlib.Tactic.LinearCombination
import Nov15.NetBowtie

/-!
NETCONTRACT (lane LEANCONTRACT).  Kernel-only: no sorry / native_decide / new axioms.

TIGHT-CHAIN CONTRACTION (NA.md sec 2c), one tight series edge at a time, on a general (non-bowtie) network `GNet`
(conventions of NetBowtie, minus the bowtie data).  `Contractible Nt j k`: relay `j → k` (`H k j ≠ 0`),
tight (`a_k ≤ b_j`, hence `a_k = b_j`), `k` is the only successor of `j` and `j` the only predecessor of `k`.
`contract Nt j k` merges `j` into `k` (same index type: `j` becomes an inert node, all rows/columns 0, charts ⊥):
  a'_k = a_j, b'_k = b_k, F'_k = F_k + η F_j, G'_k = G_k + G_j / η, H'_{k y} = η H_{j y}, N' = N off {j}.
Proved: legal GNet (`contract`), total drop EXACTLY preserved (`contract_D`), `G N F` preserved on ODD cells
(`contract_M_odd`; not on even cells: the lost cross term is G_j F_k / η, even because a_k = b_j),
edge count drops by one (`contract_edges_lt`), a contraction-closed network is reached (`exists_closed`).
Headline: `contract_D_ge_mass` / `contract_D_ge_of_wall`: if some iterated contraction of `Nt` carries bowtie data,
then mass ≤ D(Nt) (and N ≤ D(Nt) under a Wall hypothesis).
-/

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace NetContract
open FutureAttr Module Submodule Finset Function PriceLemma Matrix NetBowtie

/-- general network over a field `K` (BNet minus the bowtie data, with `hN2` derived). -/
structure GNet (K : Type*) [Field K] (ι κ : Type*) [Fintype ι] [Fintype κ]
    [DecidableEq ι] [DecidableEq κ] (h : ℕ) where
  q : ι → Fin h → ZMod 2
  lt : κ → κ → Prop
  ltrans : ∀ a b c, lt a b → lt b c → lt a c
  lirr : ∀ a, ¬ lt a a
  a : κ → Chart h
  b : κ → Chart h
  hba : ∀ k, b k ≤ a k
  F : Matrix κ ι K
  G : Matrix ι κ K
  H : Matrix κ κ K
  N : Matrix κ κ K
  hF : ∀ k p, F k p ≠ 0 → q p ∈ a k
  hG : ∀ s k, G s k ≠ 0 → ∀ y ∈ b k, y ⬝ᵥ q s = 0
  hHlt : ∀ k j, H k j ≠ 0 → lt j k
  hH : ∀ k j, H k j ≠ 0 → b j ≤ a k
  hN1 : N = 1 + H * N

/-- bowtie data on a general network (the extra fields of `BNet`). -/
structure BData {K : Type*} [Field K] {ι κ : Type*} [Fintype ι] [Fintype κ]
    [DecidableEq ι] [DecidableEq κ] {h : ℕ} (Nt : GNet K ι κ h) (γ : Type*) where
  comp : κ → γ
  role : κ → Role
  hub : γ → κ
  hhub : ∀ c, comp (hub c) = c ∧ role (hub c) = Role.hub
  hhub' : ∀ k, role k = Role.hub → k = hub (comp k)
  hcomp : ∀ k j, Nt.H k j ≠ 0 → comp k = comp j
  hshape : ∀ k j, Nt.H k j ≠ 0 →
    (role j = Role.inn ∧ (role k = Role.inn ∨ role k = Role.hub)) ∨
      (role k = Role.out ∧ (role j = Role.hub ∨ role j = Role.out))
  hgath : ∀ k p, Nt.F k p ≠ 0 → role k ≠ Role.out
  hdep : ∀ s k, Nt.G s k ≠ 0 → role k ≠ Role.inn
  hinpar : ∀ j, role j = Role.inn → ∃ k, Nt.H k j ≠ 0
  houtpar : ∀ k, role k = Role.out → ∃ j, Nt.H k j ≠ 0

namespace GNet
variable {K : Type*} [Field K] {ι κ : Type*} [Fintype ι] [Fintype κ]
  [DecidableEq ι] [DecidableEq κ] {h : ℕ}

theorem hN2 (Nt : GNet K ι κ h) : Nt.N = 1 + Nt.N * Nt.H := by
  have e1 : Nt.N - Nt.H * Nt.N = 1 := sub_eq_of_eq_add Nt.hN1
  have e2 : (1 - Nt.H) * Nt.N = 1 := by rw [sub_mul, one_mul]; exact e1
  have e3 : Nt.N * (1 - Nt.H) = 1 := mul_eq_one_comm.1 e2
  have e4 : Nt.N - Nt.N * Nt.H = 1 := by rw [mul_sub, mul_one] at e3; exact e3
  exact eq_add_of_sub_eq e4

noncomputable def drop (Nt : GNet K ι κ h) (k : κ) : ℕ :=
  finrank (ZMod 2) (Nt.a k) - finrank (ZMod 2) (Nt.b k)
noncomputable def D (Nt : GNet K ι κ h) : ℕ := ∑ k, Nt.drop k

/-- a bowtie datum turns a `GNet` into a `BNet` (same data). -/
noncomputable def toBNet {γ : Type*} [Fintype γ] [DecidableEq γ] (Nt : GNet K ι κ h)
    (B : BData Nt γ) : BNet K ι κ γ h where
  q := Nt.q
  lt := Nt.lt
  ltrans := Nt.ltrans
  lirr := Nt.lirr
  a := Nt.a
  b := Nt.b
  hba := Nt.hba
  F := Nt.F
  G := Nt.G
  H := Nt.H
  N := Nt.N
  hF := Nt.hF
  hG := Nt.hG
  hHlt := Nt.hHlt
  hH := Nt.hH
  hN1 := Nt.hN1
  hN2 := Nt.hN2
  comp := B.comp
  role := B.role
  hub := B.hub
  hhub := B.hhub
  hhub' := B.hhub'
  hcomp := B.hcomp
  hshape := B.hshape
  hgath := B.hgath
  hdep := B.hdep
  hinpar := B.hinpar
  houtpar := B.houtpar

theorem toBNet_D {γ : Type*} [Fintype γ] [DecidableEq γ] (Nt : GNet K ι κ h) (B : BData Nt γ) :
    (Nt.toBNet B).D = Nt.D := rfl


theorem Nrec (Nt : GNet K ι κ h) (k j : κ) :
    Nt.N k j = (if k = j then 1 else 0) + ∑ m, Nt.H k m * Nt.N m j := by
  have := congrFun (congrFun Nt.hN1 k) j
  simpa [Matrix.add_apply, Matrix.one_apply, Matrix.mul_apply] using this

theorem Nrec2 (Nt : GNet K ι κ h) (x j : κ) :
    Nt.N x j = (if x = j then 1 else 0) + ∑ m, Nt.N x m * Nt.H m j := by
  have := congrFun (congrFun Nt.hN2 x) j
  simpa [Matrix.add_apply, Matrix.one_apply, Matrix.mul_apply] using this

/-- a tight series edge `j → k`: `k` is the only successor of `j`, `j` the only predecessor of `k`. -/
structure Contractible (Nt : GNet K ι κ h) (j k : κ) : Prop where
  edge : Nt.H k j ≠ 0
  tight : Nt.a k ≤ Nt.b j
  inj : ∀ x, Nt.H x j ≠ 0 → x = k
  outk : ∀ y, Nt.H k y ≠ 0 → y = j

namespace Contractible
variable {Nt : GNet K ι κ h} {j k : κ} (hc : Contractible Nt j k)
include hc

theorem ltjk : Nt.lt j k := Nt.hHlt k j hc.edge
theorem jk : j ≠ k := fun e => Nt.lirr j (by have := hc.ltjk; rwa [← e] at this)
theorem Hjk : Nt.H j k = 0 := by
  by_contra hne
  exact Nt.lirr j (Nt.ltrans _ _ _ hc.ltjk (Nt.hHlt j k hne))
theorem Hjj : Nt.H j j = 0 := by
  by_contra hne
  exact Nt.lirr j (Nt.hHlt j j hne)
theorem Hxj {x : κ} (hx : x ≠ k) : Nt.H x j = 0 := by
  by_contra hne; exact hx (hc.inj x hne)
theorem Hky {y : κ} (hy : y ≠ j) : Nt.H k y = 0 := by
  by_contra hne; exact hy (hc.outk y hne)
theorem abk : Nt.a k = Nt.b j := le_antisymm hc.tight (Nt.hH k j hc.edge)

theorem N_k_row (y : κ) : Nt.N k y = (if k = y then 1 else 0) + Nt.H k j * Nt.N j y := by
  have hs : ∑ z, Nt.H k z * Nt.N z y = Nt.H k j * Nt.N j y :=
    Finset.sum_eq_single j (fun z _ hz => by rw [hc.Hky hz, zero_mul])
      (fun hh => absurd (Finset.mem_univ _) hh)
  rw [Nt.Nrec k y, hs]

theorem N_col {x : κ} (hx : x ≠ j) : Nt.N x j = Nt.H k j * Nt.N x k := by
  have hs : ∑ z, Nt.N x z * Nt.H z j = Nt.N x k * Nt.H k j :=
    Finset.sum_eq_single k (fun z _ hz => by rw [hc.Hxj hz, mul_zero])
      (fun hh => absurd (Finset.mem_univ _) hh)
  rw [Nt.Nrec2 x j, hs, if_neg hx, zero_add, mul_comm]

end Contractible

/-! ## the contracted data -/
variable (Nt : GNet K ι κ h) (j k : κ)

def ca : κ → Chart h := fun x => if x = j then ⊥ else if x = k then Nt.a j else Nt.a x
def cb (Nt : GNet K ι κ h) (j k : κ) : κ → Chart h := fun x => if x = j then ⊥ else Nt.b x
def cF : Matrix κ ι K := Matrix.of fun y p =>
  if y = j then 0 else if y = k then Nt.F k p + Nt.H k j * Nt.F j p else Nt.F y p
def cG : Matrix ι κ K := Matrix.of fun s y =>
  if y = j then 0 else if y = k then Nt.G s k + Nt.G s j / Nt.H k j else Nt.G s y
def cH : Matrix κ κ K := Matrix.of fun x y =>
  if x = j ∨ y = j then 0 else if x = k then Nt.H k j * Nt.H j y else Nt.H x y
def cN (Nt : GNet K ι κ h) (j k : κ) : Matrix κ κ K := Matrix.of fun x y =>
  if x = j ∨ y = j then (if x = y then 1 else 0) else Nt.N x y

variable {Nt j k}

theorem cH_row_j (y : κ) : cH Nt j k j y = 0 := by simp [cH]
theorem cH_col_j (x : κ) : cH Nt j k x j = 0 := by simp [cH]
theorem cH_k {y : κ} (hy : y ≠ j) (hkj : k ≠ j) : cH Nt j k k y = Nt.H k j * Nt.H j y := by
  simp [cH, hy, hkj]
theorem cH_o {x y : κ} (hx : x ≠ j) (hx' : x ≠ k) (hy : y ≠ j) : cH Nt j k x y = Nt.H x y := by
  simp [cH, hx, hx', hy]

theorem cN_row_j (y : κ) : cN Nt j k j y = if j = y then 1 else 0 := by simp [cN]
theorem cN_col_j (x : κ) : cN Nt j k x j = if x = j then 1 else 0 := by simp [cN]
theorem cN_o {x y : κ} (hx : x ≠ j) (hy : y ≠ j) : cN Nt j k x y = Nt.N x y := by
  simp [cN, hx, hy]

theorem cF_j (p : ι) : cF Nt j k j p = 0 := by simp [cF]
theorem cF_k (p : ι) (hkj : k ≠ j) : cF Nt j k k p = Nt.F k p + Nt.H k j * Nt.F j p := by
  simp [cF, hkj]
theorem cF_o {y : κ} (p : ι) (hy : y ≠ j) (hy' : y ≠ k) : cF Nt j k y p = Nt.F y p := by
  simp [cF, hy, hy']
theorem cG_j (s : ι) : cG Nt j k s j = 0 := by simp [cG]
theorem cG_k (s : ι) (hkj : k ≠ j) : cG Nt j k s k = Nt.G s k + Nt.G s j / Nt.H k j := by
  simp [cG, hkj]
theorem cG_o {y : κ} (s : ι) (hy : y ≠ j) (hy' : y ≠ k) : cG Nt j k s y = Nt.G s y := by
  simp [cG, hy, hy']

theorem ca_j : ca Nt j k j = ⊥ := by simp [ca]
theorem ca_k (hkj : k ≠ j) : ca Nt j k k = Nt.a j := by simp [ca, hkj]
theorem ca_o {x : κ} (hx : x ≠ j) (hx' : x ≠ k) : ca Nt j k x = Nt.a x := by simp [ca, hx, hx']
theorem cb_j : cb Nt j k j = ⊥ := by simp [cb]
theorem cb_o {x : κ} (hx : x ≠ j) : cb Nt j k x = Nt.b x := by simp [cb, hx]

theorem cN_hN1 (hc : Contractible Nt j k) : cN Nt j k = 1 + cH Nt j k * cN Nt j k := by
  ext x y
  rw [Matrix.add_apply, Matrix.one_apply, Matrix.mul_apply]
  by_cases hxj : x = j
  · rw [hxj, cN_row_j]
    have : ∑ z, cH Nt j k j z * cN Nt j k z y = 0 :=
      Finset.sum_eq_zero (fun z _ => by rw [cH_row_j, zero_mul])
    rw [this, add_zero]
  · by_cases hyj : y = j
    · rw [hyj, cN_col_j, if_neg hxj]
      have : ∑ z, cH Nt j k x z * cN Nt j k z j = 0 := by
        apply Finset.sum_eq_zero; intro z _
        by_cases hz : z = j
        · rw [hz, cH_col_j, zero_mul]
        · rw [cN_col_j, if_neg hz, mul_zero]
      rw [this, add_zero]
    · rw [cN_o hxj hyj]
      by_cases hxk : x = k
      · have e1 : ∀ z, cH Nt j k x z * cN Nt j k z y = Nt.H k j * (Nt.H j z * Nt.N z y) := by
          intro z
          by_cases hz : z = j
          · rw [hz, cH_col_j, hc.Hjj]; simp
          · rw [hxk, cH_k hz hc.jk.symm, cN_o hz hyj]; ring
        have hj := Nt.Nrec j y
        rw [if_neg (Ne.symm hyj), zero_add] at hj
        rw [Finset.sum_congr rfl (fun z _ => e1 z), ← Finset.mul_sum, ← hj, hxk]
        exact hc.N_k_row y
      · have e1 : ∀ z, cH Nt j k x z * cN Nt j k z y = Nt.H x z * Nt.N z y := by
          intro z
          by_cases hz : z = j
          · rw [hz, cH_col_j, hc.Hxj hxk]; simp
          · rw [cH_o hxj hxk hz, cN_o hz hyj]
        rw [Finset.sum_congr rfl (fun z _ => e1 z)]
        exact Nt.Nrec x y

/-- CONTRACTION of one tight series edge: `j` is merged into `k`, `j` becomes inert. -/
noncomputable def contract (Nt : GNet K ι κ h) (j k : κ) (hc : Contractible Nt j k) : GNet K ι κ h where
  q := Nt.q
  lt := Nt.lt
  ltrans := Nt.ltrans
  lirr := Nt.lirr
  a := ca Nt j k
  b := cb Nt j k
  hba := by
    intro x
    by_cases hxj : x = j
    · rw [hxj, ca_j, cb_j]
    · by_cases hxk : x = k
      · rw [hxk, ca_k hc.jk.symm, cb_o hc.jk.symm]
        calc Nt.b k ≤ Nt.a k := Nt.hba k
          _ ≤ Nt.b j := hc.tight
          _ ≤ Nt.a j := Nt.hba j
      · rw [ca_o hxj hxk, cb_o hxj]; exact Nt.hba x
  F := cF Nt j k
  G := cG Nt j k
  H := cH Nt j k
  N := cN Nt j k
  hF := by
    intro y p hy
    by_cases hyj : y = j
    · rw [hyj, cF_j] at hy; exact absurd rfl hy
    · by_cases hyk : y = k
      · rw [hyk, cF_k p hc.jk.symm] at hy
        rw [hyk, ca_k hc.jk.symm]
        by_cases h1 : Nt.F k p = 0
        · by_cases h2 : Nt.F j p = 0
          · rw [h1, h2] at hy; simp at hy
          · exact Nt.hF j p h2
        · have := Nt.hF k p h1
          exact Nt.hba j (hc.tight this)
      · rw [cF_o p hyj hyk] at hy; rw [ca_o hyj hyk]; exact Nt.hF y p hy
  hG := by
    intro s y hy w hw
    by_cases hyj : y = j
    · rw [hyj, cG_j] at hy; exact absurd rfl hy
    · rw [cb_o hyj] at hw
      by_cases hyk : y = k
      · rw [hyk, cG_k s hc.jk.symm] at hy
        rw [hyk] at hw
        by_cases h1 : Nt.G s k = 0
        · by_cases h2 : Nt.G s j = 0
          · rw [h1, h2] at hy; simp at hy
          · exact Nt.hG s j h2 w (hc.tight (Nt.hba k hw))
        · exact Nt.hG s k h1 w hw
      · rw [cG_o s hyj hyk] at hy; exact Nt.hG s y hy w hw
  hHlt := by
    intro x y hxy
    by_cases hxj : x = j
    · rw [hxj, cH_row_j] at hxy; exact absurd rfl hxy
    · by_cases hyj : y = j
      · rw [hyj, cH_col_j] at hxy; exact absurd rfl hxy
      · by_cases hxk : x = k
        · rw [hxk, cH_k hyj hc.jk.symm] at hxy
          have h1 : Nt.H j y ≠ 0 := fun e => hxy (by rw [e, mul_zero])
          rw [hxk]
          exact Nt.ltrans _ _ _ (Nt.hHlt j y h1) hc.ltjk
        · rw [cH_o hxj hxk hyj] at hxy; exact Nt.hHlt x y hxy
  hH := by
    intro x y hxy
    by_cases hxj : x = j
    · rw [hxj, cH_row_j] at hxy; exact absurd rfl hxy
    · by_cases hyj : y = j
      · rw [hyj, cH_col_j] at hxy; exact absurd rfl hxy
      · by_cases hxk : x = k
        · rw [hxk, cH_k hyj hc.jk.symm] at hxy
          have h1 : Nt.H j y ≠ 0 := fun e => hxy (by rw [e, mul_zero])
          have hyk : y ≠ k := fun e => h1 (by rw [e]; exact hc.Hjk)
          rw [hxk, ca_k hc.jk.symm, cb_o hyj]
          exact Nt.hH j y h1
        · rw [cH_o hxj hxk hyj] at hxy
          rw [ca_o hxj hxk, cb_o hyj]; exact Nt.hH x y hxy
  hN1 := cN_hN1 hc

theorem sum_split {M : Type*} [AddCommMonoid M] (f : κ → M) {j k : κ} (hjk : j ≠ k) :
    ∑ x, f x = f j + (f k + ∑ x ∈ (univ.erase j).erase k, f x) := by
  rw [← Finset.add_sum_erase univ f (Finset.mem_univ j),
    ← Finset.add_sum_erase (univ.erase j) f (Finset.mem_erase.2 ⟨hjk.symm, Finset.mem_univ k⟩)]

theorem mem_rest {j k x : κ} (hx : x ∈ (univ.erase j).erase k) : x ≠ j ∧ x ≠ k := by
  obtain ⟨h1, h2⟩ := Finset.mem_erase.1 hx
  exact ⟨(Finset.mem_erase.1 h2).1, h1⟩

/-- (iii) TOTAL DROP IS EXACTLY PRESERVED. -/
theorem contract_D (hc : Contractible Nt j k) : (contract Nt j k hc).D = Nt.D := by
  unfold D
  rw [sum_split (fun x => (contract Nt j k hc).drop x) hc.jk, sum_split (fun x => Nt.drop x) hc.jk]
  have hrest : ∑ x ∈ (univ.erase j).erase k, (contract Nt j k hc).drop x =
      ∑ x ∈ (univ.erase j).erase k, Nt.drop x := by
    apply Finset.sum_congr rfl
    intro x hx
    obtain ⟨h1, h2⟩ := mem_rest hx
    show finrank (ZMod 2) (ca Nt j k x) - finrank (ZMod 2) (cb Nt j k x) = _
    rw [ca_o h1 h2, cb_o h1]; rfl
  have dj : (contract Nt j k hc).drop j = 0 := by
    show finrank (ZMod 2) (ca Nt j k j) - finrank (ZMod 2) (cb Nt j k j) = 0
    rw [ca_j, cb_j]; simp
  have dk : (contract Nt j k hc).drop k =
      finrank (ZMod 2) (Nt.a j) - finrank (ZMod 2) (Nt.b k) := by
    show finrank (ZMod 2) (ca Nt j k k) - finrank (ZMod 2) (cb Nt j k k) = _
    rw [ca_k hc.jk.symm, cb_o hc.jk.symm]
  have e1 : finrank (ZMod 2) (Nt.a k) = finrank (ZMod 2) (Nt.b j) := by rw [hc.abk]
  have e2 : finrank (ZMod 2) (Nt.b k) ≤ finrank (ZMod 2) (Nt.a k) := Submodule.finrank_mono (Nt.hba k)
  have e3 : finrank (ZMod 2) (Nt.b j) ≤ finrank (ZMod 2) (Nt.a j) := Submodule.finrank_mono (Nt.hba j)
  have hdj : Nt.drop j = finrank (ZMod 2) (Nt.a j) - finrank (ZMod 2) (Nt.b j) := rfl
  have hdk : Nt.drop k = finrank (ZMod 2) (Nt.a k) - finrank (ZMod 2) (Nt.b k) := rfl
  rw [hrest, dj, dk, hdj, hdk]
  omega

/-- (ii) `G N F` is preserved on ODD cells (`q_s · q_p = 1`). -/
theorem contract_M_odd (hc : Contractible Nt j k) (s p : ι) (hodd : Nt.q s ⬝ᵥ Nt.q p = 1) :
    ((contract Nt j k hc).G * (contract Nt j k hc).N * (contract Nt j k hc).F) s p =
      (Nt.G * Nt.N * Nt.F) s p := by
  have hη : Nt.H k j ≠ 0 := hc.edge
  have hkj : k ≠ j := hc.jk.symm
  have hV' : ∀ x, x ≠ j → ((contract Nt j k hc).N * (contract Nt j k hc).F) x p =
      (Nt.N * Nt.F) x p := by
    intro x hx
    simp only [Matrix.mul_apply]
    rw [sum_split (fun y => (contract Nt j k hc).N x y * (contract Nt j k hc).F y p) hc.jk,
      sum_split (fun y => Nt.N x y * Nt.F y p) hc.jk]
    have hrest : ∑ y ∈ (univ.erase j).erase k, (contract Nt j k hc).N x y * (contract Nt j k hc).F y p =
        ∑ y ∈ (univ.erase j).erase k, Nt.N x y * Nt.F y p := by
      apply Finset.sum_congr rfl
      intro y hy
      obtain ⟨h1, h2⟩ := mem_rest hy
      show cN Nt j k x y * cF Nt j k y p = _
      rw [cN_o hx h1, cF_o p h1 h2]
    rw [hrest]
    have a1 : cN Nt j k x j * cF Nt j k j p = 0 := by rw [cF_j, mul_zero]
    have a2 : cN Nt j k x k * cF Nt j k k p = Nt.N x k * (Nt.F k p + Nt.H k j * Nt.F j p) := by
      rw [cN_o hx hkj, cF_k p hkj]
    show cN Nt j k x j * cF Nt j k j p + (cN Nt j k x k * cF Nt j k k p + _) = _
    rw [a1, a2, hc.N_col hx]; ring
  have hVj : ((contract Nt j k hc).N * (contract Nt j k hc).F) j p = 0 := by
    simp only [Matrix.mul_apply]
    apply Finset.sum_eq_zero
    intro y _
    show cN Nt j k j y * cF Nt j k y p = 0
    rw [cN_row_j]
    by_cases hy : j = y
    · rw [if_pos hy, ← hy, cF_j, mul_zero]
    · rw [if_neg hy, zero_mul]
  have hVk : (Nt.N * Nt.F) k p = Nt.F k p + Nt.H k j * (Nt.N * Nt.F) j p := by
    simp only [Matrix.mul_apply]
    calc ∑ y, Nt.N k y * Nt.F y p
        = ∑ y, ((if k = y then 1 else 0) * Nt.F y p + Nt.H k j * (Nt.N j y * Nt.F y p)) :=
          Finset.sum_congr rfl (fun y _ => by rw [hc.N_k_row y]; ring)
      _ = Nt.F k p + Nt.H k j * ∑ y, Nt.N j y * Nt.F y p := by
          rw [Finset.sum_add_distrib, ← Finset.mul_sum]; simp
  have hz : Nt.G s j * Nt.F k p = 0 := by
    by_contra hne
    have h1 : Nt.G s j ≠ 0 := left_ne_zero_of_mul hne
    have h2 : Nt.F k p ≠ 0 := right_ne_zero_of_mul hne
    have := Nt.hG s j h1 (Nt.q p) (hc.tight (Nt.hF k p h2))
    rw [dotProduct_comm] at this
    rw [this] at hodd
    exact zero_ne_one hodd
  have e : ∀ (G : Matrix ι κ K) (N : Matrix κ κ K) (F : Matrix κ ι K),
      (G * N * F) s p = ∑ x, G s x * (N * F) x p := by
    intro G N F; rw [Matrix.mul_assoc, Matrix.mul_apply]
  rw [e, e]
  rw [sum_split (fun x => (contract Nt j k hc).G s x * ((contract Nt j k hc).N * (contract Nt j k hc).F) x p) hc.jk,
    sum_split (fun x => Nt.G s x * (Nt.N * Nt.F) x p) hc.jk]
  have hrest : ∑ x ∈ (univ.erase j).erase k, (contract Nt j k hc).G s x *
        ((contract Nt j k hc).N * (contract Nt j k hc).F) x p =
      ∑ x ∈ (univ.erase j).erase k, Nt.G s x * (Nt.N * Nt.F) x p := by
    apply Finset.sum_congr rfl
    intro x hx
    obtain ⟨h1, h2⟩ := mem_rest hx
    show cG Nt j k s x * _ = _
    rw [cG_o s h1 h2, hV' x h1]
  rw [hrest]
  show cG Nt j k s j * ((contract Nt j k hc).N * (contract Nt j k hc).F) j p +
      (cG Nt j k s k * ((contract Nt j k hc).N * (contract Nt j k hc).F) k p + _) = _
  rw [hV' k hkj, hVk, cG_j, cG_k s hkj, hVj]
  have hV2 := hVk
  field_simp
  linear_combination (1 : K) * hz

end GNet

open GNet

variable {K : Type*} [Field K] {ι κ : Type*} [Fintype ι] [Fintype κ]
  [DecidableEq ι] [DecidableEq κ] {h : ℕ}

/-- iterated contraction -/
inductive Reach : GNet K ι κ h → GNet K ι κ h → Prop
  | refl (Nt : GNet K ι κ h) : Reach Nt Nt
  | step {Nt Nt' : GNet K ι κ h} (j k : κ) (hc : Contractible Nt j k) :
      Reach (contract Nt j k hc) Nt' → Reach Nt Nt'

theorem Reach.q_eq {Nt Nt' : GNet K ι κ h} (hR : Reach Nt Nt') : Nt'.q = Nt.q := by
  induction hR with
  | refl => rfl
  | step j k hc _ ih => exact ih

theorem Reach.D_eq {Nt Nt' : GNet K ι κ h} (hR : Reach Nt Nt') : Nt'.D = Nt.D := by
  induction hR with
  | refl => rfl
  | step j k hc _ ih => rw [ih, contract_D]

theorem Reach.M_odd {Nt Nt' : GNet K ι κ h} (hR : Reach Nt Nt') (s p : ι)
    (hodd : Nt.q s ⬝ᵥ Nt.q p = 1) : (Nt'.G * Nt'.N * Nt'.F) s p = (Nt.G * Nt.N * Nt.F) s p := by
  induction hR with
  | refl => rfl
  | step j k hc _ ih => rw [ih hodd]; exact contract_M_odd hc s p hodd

/-! ## HEADLINE: contraction to a bowtie -/

/-- If some iterated tight-series contraction of `Nt` carries bowtie data, the decoder mass of any pattern
realised on odd cells by `Nt` is at most `D(Nt)`. -/
theorem contract_D_ge_mass {γ : Type*} [Fintype γ] [DecidableEq γ] {Nt Nt' : GNet K ι κ h}
    (hR : Reach Nt Nt') (B : BData Nt' γ) (Rec : ι → ι → K)
    (hM : ∀ s p, Nt.q s ⬝ᵥ Nt.q p = 1 → (Nt.G * Nt.N * Nt.F) s p = Rec s p) :
    mass Nt.q Rec ≤ Nt.D := by
  have hq := hR.q_eq
  have key : mass Nt'.q Rec ≤ Nt'.D :=
    (Nt'.toBNet B).bowtie_D_ge_mass Rec (fun s p hsp => by
      have hsp' : Nt.q s ⬝ᵥ Nt.q p = 1 := by rw [← hq]; exact hsp
      exact (hR.M_odd s p hsp').trans (hM s p hsp'))
  rw [hR.D_eq, hq] at key
  exact key

/-- ... and `N ≤ D(Nt)` given the decoder wall `N` (e.g. 56 at Q96) as hypothesis. -/
theorem contract_D_ge_of_wall {γ : Type*} [Fintype γ] [DecidableEq γ] {Nt Nt' : GNet K ι κ h}
    (hR : Reach Nt Nt') (B : BData Nt' γ) (N : ℕ) (Rec : ι → ι → K)
    (hM : ∀ s p, Nt.q s ⬝ᵥ Nt.q p = 1 → (Nt.G * Nt.N * Nt.F) s p = Rec s p)
    (hwall : Wall Nt.q Rec N) : N ≤ Nt.D := by
  have hq := hR.q_eq
  have hw : Wall Nt'.q Rec N := by rw [hq]; exact hwall
  have key : N ≤ Nt'.D :=
    (Nt'.toBNet B).bowtie_D_ge_of_wall N Rec (fun s p hsp => by
      have hsp' : Nt.q s ⬝ᵥ Nt.q p = 1 := by rw [← hq]; exact hsp
      exact (hR.M_odd s p hsp').trans (hM s p hsp')) hw
  rw [hR.D_eq] at key
  exact key

/-! ## termination: a contraction-closed network is reached -/

open Classical in
/-- number of relay edges -/
noncomputable def edges (Nt : GNet K ι κ h) : ℕ :=
  (Finset.univ.filter (fun p : κ × κ => Nt.H p.1 p.2 ≠ 0)).card

theorem contract_edges_lt {Nt : GNet K ι κ h} {j k : κ} (hc : Contractible Nt j k) :
    edges (contract Nt j k hc) < edges Nt := by
  classical
  have hkj : k ≠ j := hc.jk.symm
  let φ : κ × κ → κ × κ := fun p => if p.1 = k then (j, p.2) else p
  have mem1 : ∀ p : κ × κ, p ∈ (Finset.univ.filter
      (fun p : κ × κ => (contract Nt j k hc).H p.1 p.2 ≠ 0)) →
      p.1 ≠ j ∧ p.2 ≠ j ∧ cH Nt j k p.1 p.2 ≠ 0 := by
    intro p hp
    have hp' : cH Nt j k p.1 p.2 ≠ 0 := (Finset.mem_filter.1 hp).2
    exact ⟨fun e => hp' (by rw [e, cH_row_j]), fun e => hp' (by rw [e, cH_col_j]), hp'⟩
  have hle : (Finset.univ.filter (fun p : κ × κ => (contract Nt j k hc).H p.1 p.2 ≠ 0)).card ≤
      ((Finset.univ.filter (fun p : κ × κ => Nt.H p.1 p.2 ≠ 0)).erase (k, j)).card := by
    apply Finset.card_le_card_of_injOn φ
    · intro p hp
      obtain ⟨hp1, hp2, hp'⟩ := mem1 p (Finset.mem_coe.1 hp)
      rw [Finset.mem_coe, Finset.mem_erase, Finset.mem_filter]
      by_cases hk : p.1 = k
      · have hφ : φ p = (j, p.2) := if_pos hk
        rw [hk, cH_k hp2 hkj] at hp'
        rw [hφ]
        exact ⟨fun e => hkj (Prod.mk.inj e).1.symm, Finset.mem_univ _,
          fun e => hp' (by rw [e, mul_zero])⟩
      · have hφ : φ p = p := if_neg hk
        rw [cH_o hp1 hk hp2] at hp'
        rw [hφ]
        exact ⟨fun e => hk (congrArg Prod.fst e), Finset.mem_univ _, hp'⟩
    · intro p hp p' hp' e
      obtain ⟨hp1, hp2, _⟩ := mem1 p (Finset.mem_coe.1 hp)
      obtain ⟨hq1, hq2, _⟩ := mem1 p' (Finset.mem_coe.1 hp')
      by_cases hk : p.1 = k
      · by_cases hk' : p'.1 = k
        · have e1 : φ p = (j, p.2) := if_pos hk
          have e2 : φ p' = (j, p'.2) := if_pos hk'
          rw [e1, e2] at e
          exact Prod.ext (hk.trans hk'.symm) (Prod.mk.inj e).2
        · have e1 : φ p = (j, p.2) := if_pos hk
          have e2 : φ p' = p' := if_neg hk'
          rw [e1, e2] at e
          exact absurd (congrArg Prod.fst e).symm hq1
      · by_cases hk' : p'.1 = k
        · have e1 : φ p = p := if_neg hk
          have e2 : φ p' = (j, p'.2) := if_pos hk'
          rw [e1, e2] at e
          exact absurd (congrArg Prod.fst e) hp1
        · have e1 : φ p = p := if_neg hk
          have e2 : φ p' = p' := if_neg hk'
          rw [e1, e2] at e
          exact e
  have hmem : (k, j) ∈ Finset.univ.filter (fun p : κ × κ => Nt.H p.1 p.2 ≠ 0) := by
    simpa using hc.edge
  have := Finset.card_erase_lt_of_mem hmem
  unfold edges
  exact lt_of_le_of_lt hle this

/-- iterating contraction reaches a contraction-closed network (no `Contractible` edge left). -/
theorem exists_closed : ∀ (n : ℕ) (Nt : GNet K ι κ h), edges Nt ≤ n →
    ∃ Nt', Reach Nt Nt' ∧ ∀ j k, ¬ Contractible Nt' j k := by
  intro n
  induction n with
  | zero =>
    intro Nt hn
    by_cases hex : ∃ j k, Contractible Nt j k
    · obtain ⟨j, k, hc⟩ := hex
      have := contract_edges_lt hc
      omega
    · push Not at hex
      exact ⟨Nt, Reach.refl Nt, hex⟩
  | succ n ih =>
    intro Nt hn
    by_cases hex : ∃ j k, Contractible Nt j k
    · obtain ⟨j, k, hc⟩ := hex
      have := contract_edges_lt hc
      obtain ⟨Nt', hR, hcl⟩ := ih (contract Nt j k hc) (by omega)
      exact ⟨Nt', Reach.step j k hc hR, hcl⟩
    · push Not at hex
      exact ⟨Nt, Reach.refl Nt, hex⟩

theorem exists_closed' (Nt : GNet K ι κ h) :
    ∃ Nt', Reach Nt Nt' ∧ ∀ j k, ¬ Contractible Nt' j k := exists_closed _ Nt le_rfl

/-! ## Non-vacuity: a tight chain that is NOT a bowtie, and becomes one after contraction.
`h = 2`, ports `P0 (q = e1)`, `P1 (q = e2)`, nodes `0 = j`, `1 = k`.
 node j: a = ⊤, b = ⟨e2⟩ (drop 1), gathers P0, deposits at P0 (q = e1 ⊥ e2);
 node k: a = ⟨e2⟩ = b_j (TIGHT), b = ⊥ (drop 1), gathers P1, deposits at P1;  relay j → k with scalar 1.
j gathers and deposits and has an out-relay, k gathers and deposits and has an in-relay: no role assignment
exists (`toy_not_bowtie`).  The contraction merges them into one hub (`toy_bowtie_after`). `D = 2`, `G N F` has odd
part `I`, and `contract_D_ge_mass` gives mass ≤ 2. -/
namespace Toy

def E2 : Chart 2 := Submodule.span (ZMod 2) {(![0, 1] : Fin 2 → ZMod 2)}

theorem e2_ne : (![0, 1] : Fin 2 → ZMod 2) ≠ 0 := fun e => by
  have := congrFun e 1; simp at this

theorem mem_E2 (y : Fin 2 → ZMod 2) (hy : y ∈ E2) : y 0 = 0 := by
  obtain ⟨c, rfl⟩ := Submodule.mem_span_singleton.1 hy
  simp

def Hm : Matrix (Fin 2) (Fin 2) ℚ := !![0, 0; 1, 0]
def Nm : Matrix (Fin 2) (Fin 2) ℚ := !![1, 0; 1, 1]
def Fm : Matrix (Fin 2) (Fin 2) ℚ := !![1, 0; 0, 1]
def Gm : Matrix (Fin 2) (Fin 2) ℚ := !![1, 0; 0, 1]
def qm : Fin 2 → Fin 2 → ZMod 2 := ![![1, 0], ![0, 1]]

def ach : Fin 2 → Chart 2 := ![⊤, E2]
def bch : Fin 2 → Chart 2 := ![E2, ⊥]

noncomputable def toy : GNet ℚ (Fin 2) (Fin 2) 2 where
  q := qm
  lt := fun a b => a < b
  ltrans := fun a b c h1 h2 => lt_trans h1 h2
  lirr := fun a => lt_irrefl a
  a := ach
  b := bch
  hba := by
    intro k; fin_cases k
    · simp [ach, bch]
    · simp [ach, bch]
  F := Fm
  G := Gm
  H := Hm
  N := Nm
  hF := by
    intro k p hk
    fin_cases k <;> fin_cases p
    · simp [ach]
    · simp [Fm] at hk
    · simp [Fm] at hk
    · simp only [ach, qm]
      exact Submodule.subset_span rfl
  hG := by
    intro s k hk y hy
    fin_cases s <;> fin_cases k
    · have := mem_E2 y hy
      simp [qm, dotProduct, Fin.sum_univ_two, this]
    · simp [Gm] at hk
    · simp [Gm] at hk
    · have : y = 0 := by simpa [bch] using hy
      simp [this]
  hHlt := by
    intro k j hk
    fin_cases k <;> fin_cases j <;> simp [Hm] at hk ⊢
  hH := by
    intro k j hk
    fin_cases k <;> fin_cases j <;> simp [Hm] at hk ⊢
    simp [ach, bch, E2]
  hN1 := by
    ext i j
    fin_cases i <;> fin_cases j <;> simp [Hm, Nm, Matrix.mul_apply, Fin.sum_univ_two, Matrix.one_apply]

theorem toy_contractible : GNet.Contractible toy 0 1 where
  edge := by simp [toy, Hm]
  tight := by simp [toy, ach, bch]
  inj := by
    intro x hx; fin_cases x
    · simp [toy, Hm] at hx
    · rfl
  outk := by
    intro y hy; fin_cases y
    · rfl
    · simp [toy, Hm] at hy

/-- the chain is not a bowtie, whatever the component type. -/
theorem toy_not_bowtie {γ : Type*} [Fintype γ] [DecidableEq γ] (B : BData toy γ) : False := by
  have hs := B.hshape 1 0 (by simp [toy, Hm])
  have hd := B.hdep 0 0 (by simp [toy, Gm])
  have hg := B.hgath 1 1 (by simp [toy, Fm])
  rcases hs with ⟨h1, _⟩ | ⟨h1, _⟩
  · exact hd h1
  · exact hg h1

theorem hcH (x y : Fin 2) : (GNet.contract toy 0 1 toy_contractible).H x y = 0 := by
  fin_cases x <;> fin_cases y <;> simp [GNet.contract, cH, toy, Hm]

/-- after contraction: a single hub (all roles `hub`, every node its own component, no relays). -/
def toyB : BData (GNet.contract toy 0 1 toy_contractible) (Fin 2) where
  comp := id
  role := fun _ => Role.hub
  hub := id
  hhub := fun c => ⟨rfl, rfl⟩
  hhub' := fun k _ => rfl
  hcomp := fun k j hk => absurd (hcH k j) hk
  hshape := fun k j hk => absurd (hcH k j) hk
  hgath := fun k p _ => by simp
  hdep := fun s k _ => by simp
  hinpar := fun j hj => by simp at hj
  houtpar := fun k hk => by simp at hk

theorem toy_reach : Reach toy (GNet.contract toy 0 1 toy_contractible) :=
  Reach.step 0 1 toy_contractible (Reach.refl _)

theorem toy_D : toy.D = 2 := by
  have h2 : finrank (ZMod 2) (⊤ : Chart 2) = 2 := by simp
  have h1 : finrank (ZMod 2) E2 = 1 := finrank_span_singleton e2_ne
  have d0 : toy.drop 0 = 1 := by
    show finrank (ZMod 2) (ach 0) - finrank (ZMod 2) (bch 0) = 1
    have a0 : ach 0 = ⊤ := rfl
    have b0 : bch 0 = E2 := rfl
    rw [a0, b0, h2, h1]
  have d1 : toy.drop 1 = 1 := by
    show finrank (ZMod 2) (ach 1) - finrank (ZMod 2) (bch 1) = 1
    have a1 : ach 1 = E2 := rfl
    have b1 : bch 1 = ⊥ := rfl
    rw [a1, b1, h1, finrank_bot]
  simp only [GNet.D, Fin.sum_univ_two, d0, d1]

theorem toy_M_odd (s p : Fin 2) (hodd : toy.q s ⬝ᵥ toy.q p = 1) :
    (toy.G * toy.N * toy.F) s p = if s = p then 1 else 0 := by
  fin_cases s <;> fin_cases p <;>
    simp [toy, Gm, Nm, Fm, qm, Matrix.mul_apply, Fin.sum_univ_two, dotProduct] at hodd ⊢

theorem toy_headline :
    toy.D = 2 ∧ mass toy.q (fun s p => if s = p then (1 : ℚ) else 0) ≤ 2 := by
  refine ⟨toy_D, ?_⟩
  have := contract_D_ge_mass toy_reach toyB (fun s p => if s = p then (1 : ℚ) else 0)
    (fun s p hsp => toy_M_odd s p hsp)
  rwa [toy_D] at this

end Toy

#print axioms GNet.contract_D
#print axioms GNet.contract_M_odd
#print axioms contract_edges_lt
#print axioms exists_closed'
#print axioms contract_D_ge_mass
#print axioms contract_D_ge_of_wall
#print axioms Toy.toy_not_bowtie
#print axioms Toy.toy_headline

end NetContract
