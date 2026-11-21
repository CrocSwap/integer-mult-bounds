/-
BankHelpA (lane S-BANKHELP, Nov 18).  Closes audit gap G1 (LEANSWARM/AUDIT/LA-BANK.md): helpers inside the banked Net.
MODEL.  The Net's field type `Fld` holds the 400 MAINS (`Mn`, climb 8) and the HELPERS (`Mnᶜ`, any climb `cl f`; each helper
  returns its own input, identity output row; its credit is g(climb)).  Every field f is nested (A f ≤ B f), climbs cl f.
  No premise P-HELPER: the helper credit is PROVED to be paid for.
PROVED (kernel only, axioms core):
  field_sum_gen   : Σ_j |C_j| = Σ_f cl f              (per-field climbs)
  sum_cuts_gen    : Σ_f cl f + 28 ≤ Σ_k dh(src,dst)   (flag cuts over mains AND helpers; Contract of BankWireD unchanged,
                    helpers are fixed points of π so they sit in the in-degree-1 clause)
  hE_28_gen       : window-9 extra mass over ALL fields (BankMassF.net_mass_price hypothesis hE, X = 28)
  net_price28_help: 400·8^s + 28(9^s-8^s) + helperCredit ≤ Σ paid          (paid - helper credit ≥ mains bound)
  kappa_lt_28_help: 16 such Nets, hcaller = (Σ paid - Σ helper credit ≤ cdat TB - cdat PB)  ⟹  κ < 1983/100000.
  hminor_of_outMat: the nonzero principal minors (all of Fld, helpers included) follow from BankNC0d.main_minors when the
                    output matrix is the declared caller maps ⊕ identity on helpers (K = ℚ).
STILL NAMED: P-NEST, P-CONTRACT, P-1S', P-LOC/P-HLOC (Net), P-CALLER (now exactly: paid - helper credit ≤ invoice), κ<1.
-/
import Nov15.BankWireD
import Nov15.BankFlagCert28
import Nov15.BankNC0d

namespace BankHelp
open Finset Module Submodule BankNC0 BankFlagB BankWire BankWireC BankWireD BankMassF SafeRungsPrice
open BankFlag (d)

variable {K : Type} {Fld Bank : Type} [Field K] [Fintype Fld] [DecidableEq Fld]
  [Fintype Bank] [LinearOrder Bank]

/-- fields (nested, field f climbing exactly `cl f`) cross `cl f` cuts each. -/
theorem field_sum_gen {L M : Type} [Field L] [AddCommGroup M] [Module L M] [FiniteDimensional L M]
    (F : ℕ → Submodule L M) (hmono : ∀ j, F j ≤ F (j+1)) (h0 : F 0 = ⊥) (n : ℕ)
    (hstep : ∀ j, j < n → finrank L (F (j+1)) = finrank L (F j) + 1) (hFn : F n = ⊤)
    (N : Net K (Submodule L M) Fld Bank) (cl : Fld → ℕ)
    (hclimb : ∀ f, N.A f ≤ N.B f ∧ finrank L (N.B f) = finrank L (N.A f) + cl f) :
    ∑ j ∈ range n, (Cj F N j).card = ∑ f, cl f := by
  have hle : ∀ x : Submodule L M, x ≤ F n := fun x => hFn ▸ le_top
  unfold Cj
  simp_rw [Finset.card_filter]
  rw [Finset.sum_comm]
  refine Finset.sum_congr rfl (fun f _ => ?_)
  obtain ⟨a, -⟩ := cross_nested_lt F hmono h0 n hstep _ _ (hclimb f).1 (hle _)
  rw [Finset.card_filter] at a
  rw [a]; have := (hclimb f).2; omega

variable (N : Net K (Submodule (ZMod 2) V) Fld Bank)

theorem sum_cuts_gen (hminor : ∀ C : Finset Fld,
      (N.O.submatrix (fun c : C => (c : Fld)) (fun c : C => (c : Fld))).det ≠ 0)
    (con : Contract N)
    (hnest : ∀ k, N.src k ≤ N.dst k ∨ N.dst k ≤ N.src k) (cl : Fld → ℕ)
    (hclimb : ∀ f, N.A f ≤ N.B f ∧ finrank (ZMod 2) (N.B f) = finrank (ZMod 2) (N.A f) + cl f) :
    ∑ f, cl f + 28 ≤ ∑ k, dh (finrank (ZMod 2) (N.src k)) (finrank (ZMod 2) (N.dst k)) := by
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
  have fs := field_sum_gen FF FF_mono FF_zero 9 hstep_FF FF_nine N cl hclimb
  have e1 : ∑ c ∈ range 9, (Eset OUT con.rowO c).card = 14 := by
    simp_rw [Eset_card OUT con.rowO con.injO]; exact outSum
  have e2 : ∑ c ∈ range 9, (Eset IN con.rowI c).card = 14 := by
    simp_rw [Eset_card IN con.rowI con.injI]; exact inSum
  have : ∑ c ∈ range 9, (Cset N c).card = ∑ f, cl f := fs
  rw [Finset.sum_add_distrib] at bs
  omega

theorem hE_28_gen (hminor : ∀ C : Finset Fld,
      (N.O.submatrix (fun c : C => (c : Fld)) (fun c : C => (c : Fld))).det ≠ 0)
    (con : Contract N)
    (hnest : ∀ k, N.src k ≤ N.dst k ∨ N.dst k ≤ N.src k) (cl : Fld → ℕ)
    (hclimb : ∀ f, N.A f ≤ N.B f ∧ finrank (ZMod 2) (N.B f) = finrank (ZMod 2) (N.A f) + cl f) :
    ∀ L, 8 < L → L ≤ 9 →
      ((∑ f, min L (dh (finrank (ZMod 2) (N.A f)) (finrank (ZMod 2) (N.B f))) : ℕ) : ℝ) + 28
        ≤ ((∑ k, min L (dh (finrank (ZMod 2) (N.src k)) (finrank (ZMod 2) (N.dst k))) : ℕ) : ℝ) := by
  intro L h8 h9
  have hL : L = 9 := by omega
  subst hL
  have hs := sum_cuts_gen N hminor con hnest cl hclimb
  have hle : ∀ c : Submodule (ZMod 2) V, finrank (ZMod 2) c ≤ 9 := by
    intro c
    have := Submodule.finrank_le c
    simpa using this
  have hf : ∀ f, dh (finrank (ZMod 2) (N.A f)) (finrank (ZMod 2) (N.B f)) = cl f := by
    intro f; have := (hclimb f).2; unfold dh; omega
  have hf9 : ∀ f, min 9 (cl f) = cl f := by
    intro f; have := hf f; have := hle (N.A f); have := hle (N.B f); unfold dh at *; omega
  have hk : ∀ k, min 9 (dh (finrank (ZMod 2) (N.src k)) (finrank (ZMod 2) (N.dst k)))
      = dh (finrank (ZMod 2) (N.src k)) (finrank (ZMod 2) (N.dst k)) := by
    intro k; have := hle (N.src k); have := hle (N.dst k); unfold dh; omega
  simp_rw [hf, hf9, hk]
  have : (28 : ℝ) = ((28 : ℕ) : ℝ) := by norm_num
  rw [this, ← Nat.cast_add]
  exact_mod_cast hs

/-- the credit of the helpers `Mnᶜ` at price exponent `s`: g(climb) with g d = d^s. -/
noncomputable def helperCredit (s : ℝ) (Mn : Finset Fld) : ℝ :=
  ∑ f ∈ Mnᶜ, ((dh (finrank (ZMod 2) (N.A f)) (finrank (ZMod 2) (N.B f)) : ℕ) : ℝ) ^ s

/-- P-HELPER PROVED: the banks pay for the 400 mains' climb-8 mass, the 28 extras AND every helper's own climb. -/
theorem net_price28_help {s : ℝ} (hs0 : 0 < s) (hs1 : s ≤ 1)
    (hminor : ∀ C : Finset Fld,
      (N.O.submatrix (fun c : C => (c : Fld)) (fun c : C => (c : Fld))).det ≠ 0)
    (con : Contract N) (hnest : ∀ k, N.src k ≤ N.dst k ∨ N.dst k ≤ N.src k) (cl : Fld → ℕ)
    (hclimb : ∀ f, N.A f ≤ N.B f ∧ finrank (ZMod 2) (N.B f) = finrank (ZMod 2) (N.A f) + cl f)
    (Mn : Finset Fld) (hmain : ∀ f ∈ Mn, cl f = 8) (hcard : Mn.card = 400) (paid : Bank → ℝ)
    (hpaid : ∀ k, ((dh (finrank (ZMod 2) (N.src k)) (finrank (ZMod 2) (N.dst k)) : ℕ) : ℝ) ^ s ≤ paid k) :
    400 * (8:ℝ) ^ s + 28 * ((9:ℝ) ^ s - (8:ℝ) ^ s) + helperCredit N s Mn ≤ ∑ k, paid k := by
  obtain ⟨p0, pm, pc⟩ := rpow_price hs0 hs1 9
  have hle : ∀ c : Submodule (ZMod 2) V, finrank (ZMod 2) c ≤ 9 := by
    intro c; have := Submodule.finrank_le c; simpa using this
  have := net_mass_price N hminor (fun c => finrank (ZMod 2) c) 9 8 (by norm_num) hle
    (fun d : ℕ => (d : ℝ) ^ s) p0 pm pc paid hpaid 28 (hE_28_gen N hminor con hnest cl hclimb)
  have hf : ∀ f, dh (finrank (ZMod 2) (N.A f)) (finrank (ZMod 2) (N.B f)) = cl f := by
    intro f; have := (hclimb f).2; unfold dh; omega
  have hsplit : ∑ f, ((dh (finrank (ZMod 2) (N.A f)) (finrank (ZMod 2) (N.B f)) : ℕ) : ℝ) ^ s
      = 400 * (8:ℝ) ^ s + helperCredit N s Mn := by
    rw [← Finset.sum_add_sum_compl Mn]
    congr 1
    rw [Finset.sum_congr rfl (fun f hf' => by rw [hf, hmain f hf'])]
    simp [Finset.sum_const, hcard]
  rw [hsplit] at this
  have e2 : ((8 + 1 : ℕ) : ℝ) = 9 := by norm_num
  have e3 : ((8 : ℕ) : ℝ) = 8 := by norm_num
  rw [e2, e3] at this
  linarith

theorem kappa_lt_28_help (N : Fin 16 → Net K (Submodule (ZMod 2) V) Fld Bank)
    (hminor : ∀ i, ∀ C : Finset Fld,
      ((N i).O.submatrix (fun c : C => (c : Fld)) (fun c : C => (c : Fld))).det ≠ 0)
    (con : ∀ i, Contract (N i)) (hnest : ∀ i k, (N i).src k ≤ (N i).dst k ∨ (N i).dst k ≤ (N i).src k)
    (cl : Fin 16 → Fld → ℕ)
    (hclimb : ∀ i f, (N i).A f ≤ (N i).B f ∧
      finrank (ZMod 2) ((N i).B f) = finrank (ZMod 2) ((N i).A f) + cl i f)
    (Mn : Fin 16 → Finset Fld) (hmain : ∀ i, ∀ f ∈ Mn i, cl i f = 8) (hcard : ∀ i, (Mn i).card = 400)
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (paid : Fin 16 → Bank → ℝ)
    (hpaid : ∀ i k, ((dh (finrank (ZMod 2) ((N i).src k)) (finrank (ZMod 2) ((N i).dst k)) : ℕ) : ℝ) ^ (1 - κ)
      ≤ paid i k)
    (hcaller : ∑ i, ∑ k, paid i k - ∑ i, helperCredit (N i) (1 - κ) (Mn i) ≤
      cdat (1 - κ) BankFlagCertFlagX28.TB - cdat (1 - κ) BankFlagCertFlagX28.PB) :
    κ < 1983 / 100000 := by
  by_contra hge
  push_neg at hge
  have hc := BankFlagCertFlagX28.cert κ hge hκ1.le
  unfold BankFlagCertFlagX28.FceilBank at hc
  have each : ∀ i, 400 * (8:ℝ) ^ (1 - κ) + 28 * ((9:ℝ) ^ (1 - κ) - (8:ℝ) ^ (1 - κ))
      ≤ ∑ k, paid i k - helperCredit (N i) (1 - κ) (Mn i) := fun i => by
    have := net_price28_help (N i) (s := 1 - κ) (by linarith) (by linarith) (hminor i) (con i) (hnest i)
      (cl i) (hclimb i) (Mn i) (hmain i) (hcard i) _ (hpaid i)
    linarith
  have := Finset.sum_le_sum (fun i (_ : i ∈ (Finset.univ : Finset (Fin 16))) => each i)
  simp only [Finset.sum_const, Finset.card_univ, Fintype.card_fin, nsmul_eq_mul,
    Finset.sum_sub_distrib] at this
  push_cast at this
  linarith

/-! ### minors for the helper-extended output matrix -/

/-- principal minors of any `O` that is, after reindexing the fields by `Idx h b` (helpers identity ⊕ mains in the declared
caller blocks), a copy of `BankNC0.outMat`: BankNC0d.main_minors transported along the field equivalence. -/
theorem hminor_of_outMat {Fld' : Type} [Fintype Fld'] [DecidableEq Fld'] (h b : ℕ) (t : Fin b → Fin 3)
    (e : Fld' ≃ Idx h b) (O : Matrix Fld' Fld' ℚ) (hO : ∀ f g, O f g = outMat h b t (e f) (e g))
    (C : Finset Fld') :
    (O.submatrix (fun c : C => (c : Fld')) (fun c : C => (c : Fld'))).det ≠ 0 := by
  classical
  let σ : {x // x ∈ C} ≃ {x // x ∈ C.map e.toEmbedding} :=
    Equiv.subtypeEquiv e (fun a => by simp)
  have hm := main_minors h b t (C.map e.toEmbedding)
  have : O.submatrix (fun c : C => (c : Fld')) (fun c : C => (c : Fld')) =
      ((outMat h b t).submatrix (fun c : C.map e.toEmbedding => (c : Idx h b))
        (fun c : C.map e.toEmbedding => (c : Idx h b))).submatrix σ σ := by
    funext x y
    simp [σ, hO]
  rw [this, Matrix.det_submatrix_equiv_self]
  exact hm

end BankHelp
#print axioms BankHelp.net_price28_help
#print axioms BankHelp.kappa_lt_28_help
#print axioms BankHelp.hminor_of_outMat
