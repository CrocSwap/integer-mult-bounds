/-
BankFitB .  NON-VACUITY of BankFitA.BankedGraph: an explicit inhabitant over K = ℚ.
Toy banked graph with the SAME witness-flag data (BankFlagB OUT / IN, 104 pairs each, 14+14 counted):
  fields TF = Fin 2 × Fin 104 × Bool (416; pair involution π flips the Bool);
    t = 0 (OUT pair j):  (0,j,ff) : span{v_j} → ⊤,      (0,j,tt) : ⊥ → ker φ_{a_j}
    t = 1 (IN  pair j):  (1,j,ff) : ⊥ → ker φ_{a_j},    (1,j,tt) : span{v_j} → ⊤
  outputs O = I + (partner entry 1 on the 28 COUNTED ff rows)  (BankNC0.funcMat);
  banks TBk = Fin 2 × TF:  (0,f) carries input f from A f to B f;  (1,f) carries the partner input from B(π f) to B f
    (counted ff rows only; otherwise a free dh-0 bank carrying 0);  execution order: all (0,·) before all (1,·).
  mains = the 400 fields with j < 100 (climb 8); 16 helpers (climb 8).
Every BankedGraph field (Net.read/out = P-LOC/P-ACYC, all principal minors, Contract, P-NEST, climbs, 400 mains)
is PROVED for it: `nonvacuous : Nonempty (BankedGraph ℚ TF TBk)`.  Kernel only.
-/
import Nov15.BankFitA

namespace BankFitB
open Finset Module Submodule BankNC0 BankFlagB BankWireC BankWireD BankFit

abbrev TF := Fin 2 × Fin 104 × Bool

def tπ (f : TF) : TF := (f.1, f.2.1, !f.2.2)

theorem tπ_tπ (f : TF) : tπ (tπ f) = f := by simp [tπ]
theorem tπ_ne (f : TF) : tπ f ≠ f := by
  intro h; have := congrArg (fun x : TF => x.2.2) h; simp [tπ] at this

def isP (f : TF) : Bool :=
  !f.2.2 && (if f.1 = 0 then decide (f.2.1.val ∈ cntOUT) else decide (f.2.1.val ∈ cntIN))

noncomputable def tA (f : TF) : Submodule (ZMod 2) V :=
  if f.1 = 0 then (if f.2.2 = false then span (ZMod 2) {vec (OUT.getD f.2.1 (0, 0)).1} else ⊥)
  else (if f.2.2 = false then ⊥ else span (ZMod 2) {vec (IN.getD f.2.1 (0, 0)).1})

noncomputable def tB (f : TF) : Submodule (ZMod 2) V :=
  if f.1 = 0 then (if f.2.2 = false then ⊤ else LinearMap.ker (phi (OUT.getD f.2.1 (0, 0)).2))
  else (if f.2.2 = false then LinearMap.ker (phi (IN.getD f.2.1 (0, 0)).2) else ⊤)

def TBk := Fin 2 × TF

instance : Fintype TBk := inferInstanceAs (Fintype (Fin 2 × TF))
instance : DecidableEq TBk := inferInstanceAs (DecidableEq (Fin 2 × TF))

def enc (k : TBk) : ℕ := k.1.val * 1000 + k.2.1.val * 500 + k.2.2.1.val * 2 + (if k.2.2.2 then 1 else 0)

theorem enc_inj : Function.Injective enc := by
  rintro ⟨⟨r, hr⟩, ⟨t, ht⟩, ⟨i, hi⟩, b⟩ ⟨⟨r', hr'⟩, ⟨t', ht'⟩, ⟨i', hi'⟩, b'⟩ h
  simp only [enc] at h
  have : r = r' ∧ t = t' ∧ i = i' ∧ b = b' := by
    interval_cases r <;> interval_cases r' <;> interval_cases t <;> interval_cases t' <;>
      cases b <;> cases b' <;> simp at h ⊢ <;> omega
  obtain ⟨rfl, rfl, rfl, rfl⟩ := this
  rfl

instance : LinearOrder TBk := LinearOrder.lift' enc enc_inj

def mk (r : Fin 2) (f : TF) : TBk := (r, f)

theorem bank_lt (g f : TF) : mk 0 g < mk 1 f := by
  show enc (mk 0 g) < enc (mk 1 f)
  simp only [mk]
  simp only [enc]
  have := g.1.isLt; have := g.2.1.isLt; have := f.1.isLt
  split_ifs <;> simp <;> omega

noncomputable def tsrc (k : TBk) : Submodule (ZMod 2) V :=
  if (k : Fin 2 × TF).1 = 0 then tA (k : Fin 2 × TF).2
  else if isP (k : Fin 2 × TF).2 then tB (tπ (k : Fin 2 × TF).2) else tB (k : Fin 2 × TF).2

noncomputable def tdst (k : TBk) : Submodule (ZMod 2) V := tB (k : Fin 2 × TF).2

noncomputable def td (k : TBk) : TF → ℚ :=
  if (k : Fin 2 × TF).1 = 0 then Pi.single (k : Fin 2 × TF).2 1
  else if isP (k : Fin 2 × TF).2 then Pi.single (tπ (k : Fin 2 × TF).2) 1 else 0

def tp (f : TF) : Option TF := if isP f then some (tπ f) else none

def tO : Matrix TF TF ℚ := funcMat (fun _ => 1) (fun _ => 1) tp

theorem tO_row (f : TF) : tO f = Pi.single f 1 + (if isP f then Pi.single (tπ f) 1 else 0) := by
  funext g
  simp only [tO, funcMat, tp, Pi.add_apply]
  by_cases hg : g = f
  · subst hg
    have := tπ_ne g
    split_ifs <;> simp_all [Pi.single_apply]
  · by_cases hP : isP f
    · by_cases hπ : g = tπ f
      · subst hπ; simp [hP, hg, Pi.single_apply]
      · have : (some (tπ f) = some g) = False := by simp; exact fun e => hπ e.symm
        simp [hP, hg, Pi.single_apply, hπ, this]
    · simp [hP, hg, Pi.single_apply]

noncomputable def tN : Net ℚ (Submodule (ZMod 2) V) TF TBk where
  A := tA
  B := tB
  src := tsrc
  dst := tdst
  d := td
  O := tO
  read := by
    rintro ⟨r, f⟩
    by_cases hr : r = 0
    · subst hr; apply subset_span; left; exact ⟨f, by simp [tsrc], by simp [td]⟩
    · obtain rfl : r = 1 := by fin_cases r <;> simp_all
      by_cases hP : isP f
      · apply subset_span; right
        exact ⟨mk 0 (tπ f), bank_lt _ _, by simp [mk, tdst, tsrc, hP], by simp [mk, td, hP]⟩
      · have : td ((1 : Fin 2), f) = 0 := by simp [td, hP]
        rw [this]; exact zero_mem _
  out := by
    intro f
    rw [tO_row]
    refine add_mem (subset_span (Or.inr ⟨((0 : Fin 2), f), rfl, by simp [td]⟩)) ?_
    split_ifs with hP
    · exact subset_span (Or.inr ⟨((1 : Fin 2), f), rfl, by simp [td, hP]⟩)
    · exact zero_mem _

/-! ### data facts (decide) -/
theorem outBits : ∀ j : Fin 104, (∃ i : Fin 9, (OUT.getD j (0, 0)).1.testBit i = true) ∧
    (∃ i : Fin 9, (OUT.getD j (0, 0)).2.testBit i = true) := by decide +kernel
theorem inBits : ∀ j : Fin 104, (∃ i : Fin 9, (IN.getD j (0, 0)).1.testBit i = true) ∧
    (∃ i : Fin 9, (IN.getD j (0, 0)).2.testBit i = true) := by decide +kernel
theorem cntOUT_lt : ∀ i ∈ cntOUT, i < 104 := by decide
theorem cntIN_lt : ∀ i ∈ cntIN, i < 104 := by decide

theorem vec_ne {m : ℕ} (h : ∃ i : Fin 9, m.testBit i = true) : vec m ≠ 0 := by
  obtain ⟨i, hi⟩ := h
  intro e
  have := congrFun e i
  simp [vec, hi] at this

theorem ker_rank {a : ℕ} (h : ∃ i : Fin 9, a.testBit i = true) :
    finrank (ZMod 2) (LinearMap.ker (phi a)) = 8 := by
  obtain ⟨i, hi⟩ := h
  have hs : Function.Surjective (phi a) := by
    intro y
    refine ⟨y • Pi.single i 1, ?_⟩
    have hsum : (∑ x : Fin 9, if a.testBit ↑x = true then (if x = i then (1 : ZMod 2) else 0) else 0) = 1 := by
      rw [Finset.sum_eq_single i]
      · simp [hi]
      · intro b _ hb; simp [hb]
      · simp
    rw [LinearMap.map_smul, phi_apply]
    simp [Pi.single_apply, hsum]
  have h1 := LinearMap.finrank_range_add_finrank_ker (phi a)
  rw [LinearMap.range_eq_top.mpr hs, finrank_top, Module.finrank_self, Module.finrank_fin_fun] at h1
  omega

theorem finrank_V : finrank (ZMod 2) V = 9 := Module.finrank_fin_fun _

theorem tclimb (f : TF) : tA f ≤ tB f ∧ finrank (ZMod 2) (tB f) = finrank (ZMod 2) (tA f) + 8 := by
  obtain ⟨t, j, b⟩ := f
  obtain rfl | rfl : t = 0 ∨ t = 1 := by fin_cases t <;> simp
  · cases b
    · have hA : tA (0, j, false) = span (ZMod 2) {vec (OUT.getD j (0, 0)).1} := by simp [tA]
      have hB : tB (0, j, false) = ⊤ := by simp [tB]
      rw [hA, hB]
      exact ⟨le_top, by rw [finrank_top, finrank_V, finrank_span_singleton (vec_ne (outBits j).1)]⟩
    · have hA : tA (0, j, true) = ⊥ := by simp [tA]
      have hB : tB (0, j, true) = LinearMap.ker (phi (OUT.getD j (0, 0)).2) := by simp [tB]
      rw [hA, hB]
      exact ⟨bot_le, by rw [ker_rank (outBits j).2, finrank_bot]⟩
  · cases b
    · have hA : tA (1, j, false) = ⊥ := by simp [tA]
      have hB : tB (1, j, false) = LinearMap.ker (phi (IN.getD j (0, 0)).2) := by simp [tB]
      rw [hA, hB]
      exact ⟨bot_le, by rw [ker_rank (inBits j).2, finrank_bot]⟩
    · have hA : tA (1, j, true) = span (ZMod 2) {vec (IN.getD j (0, 0)).1} := by simp [tA]
      have hB : tB (1, j, true) = ⊤ := by simp [tB]
      rw [hA, hB]
      exact ⟨le_top, by rw [finrank_top, finrank_V, finrank_span_singleton (vec_ne (inBits j).1)]⟩

theorem tminors (C : Finset TF) :
    (tO.submatrix (fun c : C => (c : TF)) (fun c : C => (c : TF))).det ≠ 0 := by
  refine minors_ne_zero (fun _ => (1 : ℚ)) (fun _ => 1) tp (fun _ => one_ne_zero) ?_
    (fun f => if isP f then 1 else 0) ?_ C
  · intro f; unfold tp; split_ifs
    · intro e; exact tπ_ne f (Option.some.inj e)
    · simp
  · intro i j h
    unfold tp at h
    split_ifs at h with hP
    obtain rfl := Option.some.inj h
    left
    have h2 : i.2.2 = false := by simp [isP] at hP; exact hP.1
    have : isP (tπ i) = false := by simp [isP, tπ, h2]
    simp [this, hP]

theorem rowO_mod {i : ℕ} (hi : i ∈ cnt OUT) : i % 104 = i := by
  rw [out_cnt] at hi; exact Nat.mod_eq_of_lt (cntOUT_lt i hi)
theorem rowI_mod {i : ℕ} (hi : i ∈ cnt IN) : i % 104 = i := by
  rw [in_cnt] at hi; exact Nat.mod_eq_of_lt (cntIN_lt i hi)

def rowO (i : ℕ) : TF := ((0 : Fin 2), ⟨i % 104, Nat.mod_lt _ (by norm_num)⟩, false)
def rowI (i : ℕ) : TF := ((1 : Fin 2), ⟨i % 104, Nat.mod_lt _ (by norm_num)⟩, false)

theorem tπ_inj {r e : TF} (h : tπ r = tπ e) : r = e := by
  have := congrArg tπ h; simpa [tπ_tπ] using this

noncomputable def tcon : Contract tN where
  π := tπ
  rowO := rowO
  rowI := rowI
  hsupp := by
    intro f g h
    change tO f g ≠ 0 at h
    rw [tO_row] at h
    by_cases h1 : g = f
    · exact Or.inl h1
    · right
      by_cases hP : isP f
      · by_contra h2
        simp [hP, Pi.single_apply, h1, Ne.symm h2] at h
      · simp [hP, Pi.single_apply, h1] at h
  injO := by
    intro i hi i' hi' h
    have := congrArg (fun x : TF => x.2.1.val) h
    simp only [rowO] at this
    rwa [rowO_mod hi, rowO_mod hi'] at this
  injI := by
    intro i hi i' hi' h
    have := congrArg (fun x : TF => x.2.1.val) h
    simp only [rowI] at this
    rwa [rowI_mod hi, rowI_mod hi'] at this
  chartO := by
    intro i hi
    have hm := rowO_mod hi
    refine ⟨?_, ?_, ?_, ?_⟩ <;> simp [tN, rowO, tA, tB, tπ, hm]
  chartI := by
    intro i hi
    have hm := rowI_mod hi
    refine ⟨?_, ?_, ?_, ?_⟩ <;> simp [tN, rowI, tA, tB, tπ, hm]
  nzO := by
    intro i hi
    have hm := rowO_mod hi
    have hc : i ∈ cntOUT := out_cnt ▸ hi
    change tO (rowO i) (tπ (rowO i)) ≠ 0
    rw [tO_row]
    have hP : isP (rowO i) = true := by simp [isP, rowO, hm, hc]
    simp [hP, Pi.single_apply, tπ_ne]
  nzI := by
    intro i hi
    have hm := rowI_mod hi
    have hc : i ∈ cntIN := in_cnt ▸ hi
    change tO (rowI i) (tπ (rowI i)) ≠ 0
    rw [tO_row]
    have hP : isP (rowI i) = true := by simp [isP, rowI, hm, hc]
    simp [hP, Pi.single_apply, tπ_ne]
  indegO := fun _ _ _ _ _ _ h => tπ_inj h
  indegI := fun _ _ _ _ _ _ h => tπ_inj h

theorem tnest (k : TBk) : tN.src k ≤ tN.dst k ∨ tN.dst k ≤ tN.src k := by
  rcases k with ⟨r, f⟩
  by_cases hr : r = 0
  · subst hr; left; simpa [tN, tsrc, tdst] using (tclimb f).1
  · by_cases hP : isP f
    · rcases f with ⟨t, j, b⟩
      have hb : b = false := by simp [isP] at hP; exact hP.1
      subst hb
      by_cases ht : t = 0
      · subst ht; left; simp [tN, tsrc, tdst, hr, hP, tB, tπ]
      · right; simp [tN, tsrc, tdst, hr, hP, tB, tπ, ht]
    · left; simp [tN, tsrc, tdst, hr, hP]

def tMn : Finset TF := Finset.univ.filter (fun f : TF => f.2.1.val < 100)

theorem tMn_card : tMn.card = 400 := by decide +kernel

/-- NON-VACUITY: the BankedGraph premises are jointly satisfiable (with the real 14+14 witness-flag data). -/
noncomputable def tG : BankedGraph ℚ TF TBk where
  N := tN
  minors := tminors
  con := tcon
  nest := tnest
  cl := fun _ => 8
  climb := tclimb
  Mn := tMn
  main8 := fun _ _ => rfl
  card := tMn_card

theorem nonvacuous : Nonempty (BankedGraph ℚ TF TBk) := ⟨tG⟩

end BankFitB
#print axioms BankFitB.nonvacuous
