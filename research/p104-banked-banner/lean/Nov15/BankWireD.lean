/-
BankWireD .  
Assembly for the 400-main hosted Net with the witness flag of BankFlagB (V = F_2^9, FF = flag of BankWireC):
  Contract       : the caller-fixed main contract + chart model (NAMED PREMISE P-CONTRACT): row support {self, partner pi},
                   counted OUT row i: chart [v_i] -> top, partner [] -> ker phi_{a_i}; counted IN row i: [] -> ker phi_{a_i},
                   partner [v_i] -> top; partner coefficient nonzero; in-degree 1 (hinj per cut).
  extras_sum     : sum_c (|Eo c| + |Ei c|) = 28 (BankFlagB atLevel, rows distinct)
  hE_28          : hE of BankMassF.net_mass_price at L = 9 (H = 9, m = 8, X = 28), from out_cut / in_cut / bank_sum / field_sum.
  net_price28    : 400 * 8^s + 28 (9^s - 8^s) <= total paid of the (mains-only) Net, any s in (0,1].
Premises NOT discharged: P-NEST (banks nested: needed by bank_sum under dh pricing), minors, P-CONTRACT, P-LOC/P-HLOC (Net),
P-1S' (hpaid), and the helper decomposition P-HELPER (see BankWireE).  Kernel only, no sorry/native_decide/axioms.
-/
import Nov15.BankWireB
import Nov15.BankWireC

namespace BankWireD
open Finset Module Submodule BankNC0 BankFlagB BankWire BankWireC
open BankFlag (d)

variable {K : Type} {Fld Bank : Type} [Field K] [Fintype Fld] [DecidableEq Fld]
  [Fintype Bank] [LinearOrder Bank]

noncomputable def Cset (N : Net K (Submodule (ZMod 2) V) Fld Bank) (c : ℕ) : Finset Fld := Cj FF N c

def Eset (P : List (ℕ × ℕ)) (row : ℕ → Fld) (c : ℕ) : Finset Fld :=
  (((cnt P).filter (fun i => level (P.getD i (0, 0)).1 == c + 1)).toFinset).image row

structure Contract (N : Net K (Submodule (ZMod 2) V) Fld Bank) where
  π : Fld → Fld
  rowO : ℕ → Fld
  rowI : ℕ → Fld
  hsupp : ∀ f g, N.O f g ≠ 0 → g = f ∨ g = π f
  injO : ∀ i ∈ cnt OUT, ∀ i' ∈ cnt OUT, rowO i = rowO i' → i = i'
  injI : ∀ i ∈ cnt IN, ∀ i' ∈ cnt IN, rowI i = rowI i' → i = i'
  chartO : ∀ i ∈ cnt OUT, N.A (rowO i) = span (ZMod 2) {vec (OUT.getD i (0, 0)).1} ∧ N.B (rowO i) = ⊤ ∧
    N.A (π (rowO i)) = ⊥ ∧ N.B (π (rowO i)) = LinearMap.ker (phi (OUT.getD i (0, 0)).2)
  chartI : ∀ i ∈ cnt IN, N.A (rowI i) = ⊥ ∧ N.B (rowI i) = LinearMap.ker (phi (IN.getD i (0, 0)).2) ∧
    N.A (π (rowI i)) = span (ZMod 2) {vec (IN.getD i (0, 0)).1} ∧ N.B (π (rowI i)) = ⊤
  nzO : ∀ i ∈ cnt OUT, N.O (rowO i) (π (rowO i)) ≠ 0
  nzI : ∀ i ∈ cnt IN, N.O (rowI i) (π (rowI i)) ≠ 0
  indegO : ∀ c, c < 9 → ∀ e ∈ Eset OUT rowO c, ∀ r ∈ Cset N c ∪ Eset OUT rowO c, π r = π e → r = e
  indegI : ∀ c, c < 9 → ∀ e ∈ Eset IN rowI c, ∀ r ∈ Eset IN rowI c, π r = π e → r = e

theorem Eset_card (P : List (ℕ × ℕ)) (row : ℕ → Fld) (hinj : ∀ i ∈ cnt P, ∀ i' ∈ cnt P, row i = row i' → i = i')
    (c : ℕ) : (Eset P row c).card = atLevel P (c + 1) := by
  unfold Eset atLevel
  have hnd : ((cnt P).filter (fun i => level (P.getD i (0, 0)).1 == c + 1)).Nodup :=
    List.Nodup.filter _ (by unfold cnt; exact List.Nodup.filter _ List.nodup_range)
  have hi : Set.InjOn row (((cnt P).filter (fun i => level (P.getD i (0, 0)).1 == c + 1)).toFinset : Set ℕ) := by
    intro i hi i' hi' h
    simp only [Finset.mem_coe, List.mem_toFinset, List.mem_filter] at hi hi'
    exact hinj i hi.1 i' hi'.1 h
  rw [Finset.card_image_of_injOn hi, List.toFinset_card_of_nodup hnd]

theorem outSum : ∑ c ∈ Finset.range 9, atLevel OUT (c + 1) = 14 := by decide +kernel
theorem inSum : ∑ c ∈ Finset.range 9, atLevel IN (c + 1) = 14 := by decide +kernel

theorem hstep_FF : ∀ j, j < 9 → finrank (ZMod 2) (FF (j+1)) = finrank (ZMod 2) (FF j) + 1 :=
  fun j hj => flag_step j hj

variable (N : Net K (Submodule (ZMod 2) V) Fld Bank)

theorem sum_cuts (hminor : ∀ C : Finset Fld,
      (N.O.submatrix (fun c : C => (c : Fld)) (fun c : C => (c : Fld))).det ≠ 0)
    (con : Contract N)
    (hnest : ∀ k, N.src k ≤ N.dst k ∨ N.dst k ≤ N.src k)
    (hclimb : ∀ f, N.A f ≤ N.B f ∧ finrank (ZMod 2) (N.B f) = finrank (ZMod 2) (N.A f) + 8) :
    8 * Fintype.card Fld + 28 ≤ ∑ k, dh (finrank (ZMod 2) (N.src k)) (finrank (ZMod 2) (N.dst k)) := by
  classical
  have hout : ∀ c ∈ range 9, (Cset N c).card + (Eset OUT con.rowO c).card ≤
      (Finset.univ.filter (fun k => d FF (N.src k) c < d FF (N.dst k) c)).card := by
    intro c hc
    have hc9 := Finset.mem_range.mp hc
    refine out_cut FF FF_mono 9 hstep_FF N hminor c hc9 (Eset OUT con.rowO c) con.π ?_ ?_ con.hsupp
      (con.indegO c hc9)
    · intro e he
      unfold Eset at he
      obtain ⟨i, hi, rfl⟩ := Finset.mem_image.mp he
      simp only [List.mem_toFinset, List.mem_filter, beq_iff_eq] at hi
      obtain ⟨hcnt, hl⟩ := hi
      obtain ⟨-, h1, h2, h3, h4⟩ := counted_chart OUT out_ok i hcnt
      rw [hl] at h1 h2 h3 h4
      simp only [Nat.add_sub_cancel] at h1 h2 h3 h4
      obtain ⟨cA, cB, cA', cB'⟩ := con.chartO i hcnt
      exact ⟨_, _, h1, h2, h3, h4, cA, cB, cA', cB'⟩
    · intro e he
      unfold Eset at he
      obtain ⟨i, hi, rfl⟩ := Finset.mem_image.mp he
      simp only [List.mem_toFinset, List.mem_filter] at hi
      exact con.nzO i hi.1
  have hin : ∀ c ∈ range 9, (Eset IN con.rowI c).card ≤
      (Finset.univ.filter (fun k => d FF (N.dst k) c < d FF (N.src k) c)).card := by
    intro c hc
    have hc9 := Finset.mem_range.mp hc
    refine in_cut FF FF_mono 9 hstep_FF N c hc9 (Eset IN con.rowI c) con.π ?_ ?_ con.hsupp
      (con.indegI c hc9)
    · intro e he
      unfold Eset at he
      obtain ⟨i, hi, rfl⟩ := Finset.mem_image.mp he
      simp only [List.mem_toFinset, List.mem_filter, beq_iff_eq] at hi
      obtain ⟨hcnt, hl⟩ := hi
      obtain ⟨-, h1, h2, h3, h4⟩ := counted_chart IN in_ok i hcnt
      rw [hl] at h1 h2 h3 h4
      simp only [Nat.add_sub_cancel] at h1 h2 h3 h4
      obtain ⟨cA, cB, cA', cB'⟩ := con.chartI i hcnt
      exact ⟨_, _, h1, h2, h3, h4, cA, cB, cA', cB'⟩
    · intro e he
      unfold Eset at he
      obtain ⟨i, hi, rfl⟩ := Finset.mem_image.mp he
      simp only [List.mem_toFinset, List.mem_filter] at hi
      exact con.nzI i hi.1
  have s1 := Finset.sum_le_sum hout
  have s2 := Finset.sum_le_sum hin
  rw [Finset.sum_add_distrib] at s1
  have bs := bank_sum FF FF_mono FF_zero 9 hstep_FF FF_nine N hnest
  have fs := field_sum FF FF_mono FF_zero 9 hstep_FF FF_nine N 8 hclimb
  have e1 : ∑ c ∈ range 9, (Eset OUT con.rowO c).card = 14 := by
    simp_rw [Eset_card OUT con.rowO con.injO]; exact outSum
  have e2 : ∑ c ∈ range 9, (Eset IN con.rowI c).card = 14 := by
    simp_rw [Eset_card IN con.rowI con.injI]; exact inSum
  have : ∑ c ∈ range 9, (Cset N c).card = 8 * Fintype.card Fld := fs
  rw [Finset.sum_add_distrib] at bs
  omega

theorem hE_28 (hminor : ∀ C : Finset Fld,
      (N.O.submatrix (fun c : C => (c : Fld)) (fun c : C => (c : Fld))).det ≠ 0)
    (con : Contract N)
    (hnest : ∀ k, N.src k ≤ N.dst k ∨ N.dst k ≤ N.src k)
    (hclimb : ∀ f, N.A f ≤ N.B f ∧ finrank (ZMod 2) (N.B f) = finrank (ZMod 2) (N.A f) + 8) :
    ∀ L, 8 < L → L ≤ 9 →
      ((∑ f, min L (dh (finrank (ZMod 2) (N.A f)) (finrank (ZMod 2) (N.B f))) : ℕ) : ℝ) + 28
        ≤ ((∑ k, min L (dh (finrank (ZMod 2) (N.src k)) (finrank (ZMod 2) (N.dst k))) : ℕ) : ℝ) := by
  intro L h8 h9
  have hL : L = 9 := by omega
  subst hL
  have hs := sum_cuts N hminor con hnest hclimb
  have hle : ∀ c : Submodule (ZMod 2) V, finrank (ZMod 2) c ≤ 9 := by
    intro c
    have := Submodule.finrank_le c
    simpa using this
  have hf : ∀ f, dh (finrank (ZMod 2) (N.A f)) (finrank (ZMod 2) (N.B f)) = 8 := by
    intro f; have := (hclimb f).2; unfold dh; omega
  have hk : ∀ k, min 9 (dh (finrank (ZMod 2) (N.src k)) (finrank (ZMod 2) (N.dst k)))
      = dh (finrank (ZMod 2) (N.src k)) (finrank (ZMod 2) (N.dst k)) := by
    intro k; have := hle (N.src k); have := hle (N.dst k); unfold dh; omega
  simp_rw [hf, hk]
  simp only [min_eq_right (show 8 ≤ 9 by norm_num), Finset.sum_const, Finset.card_univ, smul_eq_mul]
  have : (28 : ℝ) = ((28 : ℕ) : ℝ) := by norm_num
  rw [this, ← Nat.cast_add]
  exact_mod_cast (by omega : Fintype.card Fld * 8 + 28 ≤ _)

end BankWireD
