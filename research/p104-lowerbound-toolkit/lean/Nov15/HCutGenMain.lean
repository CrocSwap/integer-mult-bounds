/-
HCutGenMain (lane HCUT, Nov 20).  Instances of HCutGen.rung_port_net_h at the danger label ranks h = 8 (half-spin 64, E7+A1 bound)
and h = 7 (E7), with the HCall cut contract DISCHARGED from a Net + the port-row contract; plus a NON-VACUITY net at h = 8, n = 1:
a concrete Net over submodules of F_2^8 with one port, whose contract is built by `contract_of_ports`, whose principal minors are
nonzero, and whose HCall (via HCall.ofNet) satisfies price_h.
Kernel only.
-/
import Nov15.HCutGen

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace HCutGen
open Finset Module BankNC0 PriceH SafeRungsPrice

theorem rung_port_net_h8 (n QR : ℕ) (ρD ρR kbar : ℝ) (L : ℕ) (T P : List (ℕ × ℕ))
    (hcert : Cert (fun s => cdat s T - cdat s P - (L : ℝ) * UniPort.PortInv n QR 8 ρD ρR 0 s) kbar)
    {K Chart : Type} [Field K] {Fld Bank : Fin L → Type} [∀ i, Fintype (Fld i)] [∀ i, DecidableEq (Fld i)]
    [∀ i, Fintype (Bank i)] [∀ i, LinearOrder (Bank i)] (ht : Chart → ℕ) (hle : ∀ c, ht c ≤ 8)
    (N : ∀ i, Net K Chart (Fld i) (Bank i))
    (hminor : ∀ i (C : Finset (Fld i)), ((N i).O.submatrix (fun c : C => (c : Fld i)) (fun c : C => (c : Fld i))).det ≠ 0)
    (hc : ∀ i, HSContractH (N i) ht 8 n)
    (Mn : ∀ i, Finset (Fld i)) (hmain : ∀ i, ∀ f ∈ Mn i, dh (ht ((N i).A f)) (ht ((N i).B f)) = 8 - 1)
    (hcard : ∀ i, (Mn i).card = 2 * n + 2 * QR)
    (Dm Rm : Fin L → ℝ)
    (hD : ∀ i, ρD * n ≤ Dm i) (hR : ∀ i, ρR * n ≤ Rm i)
    (hX : ∀ i, Dm i + Rm i ≤ (HCall.ofNet (N i) ht 8 n QR (hminor i) (hc i) hle (Mn i) (hmain i) (hcard i)).excess)
    (κ : ℝ) (hκ0 : 0 ≤ κ) (hκ1 : κ < 1)
    (hbud : kbar ≤ κ → 0 ≤ bud 8 md8 (fun d : ℕ => (d : ℝ) ^ (1 - κ)))
    (hV : cdat (1 - κ) P + ∑ i, (HCall.ofNet (N i) ht 8 n QR (hminor i) (hc i) hle (Mn i) (hmain i) (hcard i)).spec (1 - κ) ≤
      cdat (1 - κ) T + ∑ i, (HCall.ofNet (N i) ht 8 n QR (hminor i) (hc i) hle (Mn i) (hmain i) (hcard i)).cred (1 - κ)) :
    κ < kbar :=
  rung_port_net_h 8 n QR (by norm_num) md8 ρD ρR kbar L T P hcert ht hle N hminor hc Mn hmain hcard Dm Rm hD hR hX κ hκ0 hκ1 hbud hV

theorem rung_port_net_h7 (n QR : ℕ) (ρD ρR kbar : ℝ) (L : ℕ) (T P : List (ℕ × ℕ))
    (hcert : Cert (fun s => cdat s T - cdat s P - (L : ℝ) * UniPort.PortInv n QR 7 ρD ρR 0 s) kbar)
    {K Chart : Type} [Field K] {Fld Bank : Fin L → Type} [∀ i, Fintype (Fld i)] [∀ i, DecidableEq (Fld i)]
    [∀ i, Fintype (Bank i)] [∀ i, LinearOrder (Bank i)] (ht : Chart → ℕ) (hle : ∀ c, ht c ≤ 7)
    (N : ∀ i, Net K Chart (Fld i) (Bank i))
    (hminor : ∀ i (C : Finset (Fld i)), ((N i).O.submatrix (fun c : C => (c : Fld i)) (fun c : C => (c : Fld i))).det ≠ 0)
    (hc : ∀ i, HSContractH (N i) ht 7 n)
    (Mn : ∀ i, Finset (Fld i)) (hmain : ∀ i, ∀ f ∈ Mn i, dh (ht ((N i).A f)) (ht ((N i).B f)) = 7 - 1)
    (hcard : ∀ i, (Mn i).card = 2 * n + 2 * QR)
    (Dm Rm : Fin L → ℝ)
    (hD : ∀ i, ρD * n ≤ Dm i) (hR : ∀ i, ρR * n ≤ Rm i)
    (hX : ∀ i, Dm i + Rm i ≤ (HCall.ofNet (N i) ht 7 n QR (hminor i) (hc i) hle (Mn i) (hmain i) (hcard i)).excess)
    (κ : ℝ) (hκ0 : 0 ≤ κ) (hκ1 : κ < 1)
    (hbud : kbar ≤ κ → 0 ≤ bud 7 md7 (fun d : ℕ => (d : ℝ) ^ (1 - κ)))
    (hV : cdat (1 - κ) P + ∑ i, (HCall.ofNet (N i) ht 7 n QR (hminor i) (hc i) hle (Mn i) (hmain i) (hcard i)).spec (1 - κ) ≤
      cdat (1 - κ) T + ∑ i, (HCall.ofNet (N i) ht 7 n QR (hminor i) (hc i) hle (Mn i) (hmain i) (hcard i)).cred (1 - κ)) :
    κ < kbar :=
  rung_port_net_h 7 n QR (by norm_num) md7 ρD ρR kbar L T P hcert ht hle N hminor hc Mn hmain hcard Dm Rm hD hR hX κ hκ0 hκ1 hbud hV

/-! ### Non-vacuity: a concrete one-port net at h = 8 -/
section Toy
abbrev W8 := Fin 8 → ZMod 2

def v8 : W8 := Pi.single 0 1
def φ8 : W8 →ₗ[ZMod 2] ZMod 2 := LinearMap.proj 0

theorem v8_ne : v8 ≠ 0 := by
  intro h; have := congrFun h 0; simp [v8] at this

theorem φ8_ne : φ8 ≠ 0 := by
  intro h; have := LinearMap.congr_fun h v8; simp [φ8, v8] at this

theorem finrank_W8 : finrank (ZMod 2) W8 = 8 := by simp

abbrev Ch := Submodule (ZMod 2) W8

def tA : Fin 2 → Ch := ![Submodule.span (ZMod 2) {v8}, ⊥]
def tB : Fin 2 → Ch := ![⊤, LinearMap.ker φ8]
def tsrc : Fin 4 → Ch := ![Submodule.span (ZMod 2) {v8}, ⊥, ⊥, Submodule.span (ZMod 2) {v8}]
def tdst : Fin 4 → Ch := ![⊤, LinearMap.ker φ8, ⊤, LinearMap.ker φ8]
def td : Fin 4 → Fin 2 → ℚ := ![Pi.single 0 1, Pi.single 1 1, Pi.single 1 1, Pi.single 0 1]
def tO : Matrix (Fin 2) (Fin 2) ℚ := !![1, 1; 1, 2]

theorem tO0 : tO 0 = Pi.single 0 1 + Pi.single 1 1 := by
  ext i; fin_cases i <;> simp [tO]
theorem tO1 : tO 1 = Pi.single 0 1 + 2 • (Pi.single 1 1 : Fin 2 → ℚ) := by
  ext i; fin_cases i <;> simp [tO]

def tN : Net ℚ Ch (Fin 2) (Fin 4) where
  A := tA
  B := tB
  src := tsrc
  dst := tdst
  d := td
  O := tO
  read k := by
    classical
    fin_cases k
    · exact Submodule.subset_span (Or.inl ⟨0, by simp [tA, tsrc], by simp [td]⟩)
    · exact Submodule.subset_span (Or.inl ⟨1, by simp [tA, tsrc], by simp [td]⟩)
    · exact Submodule.subset_span (Or.inl ⟨1, by simp [tA, tsrc], by simp [td]⟩)
    · exact Submodule.subset_span (Or.inl ⟨0, by simp [tA, tsrc], by simp [td]⟩)
  out f := by
    classical
    fin_cases f
    · show tO 0 ∈ _
      rw [tO0]
      refine Submodule.add_mem _ (Submodule.subset_span (Or.inr ⟨0, by simp [tB, tdst], by simp [td]⟩))
        (Submodule.subset_span (Or.inr ⟨2, by simp [tB, tdst], by simp [td]⟩))
    · show tO 1 ∈ _
      rw [tO1]
      refine Submodule.add_mem _ (Submodule.subset_span (Or.inr ⟨3, by simp [tB, tdst], by simp [td]⟩))
        (Submodule.smul_mem _ _ (Submodule.subset_span (Or.inr ⟨1, by simp [tB, tdst], by simp [td]⟩)))

def tπ : Fin 2 → Fin 2 := fun f => 1 - f

noncomputable def tHC : HSContractH tN (fun c => finrank (ZMod 2) c) 8 1 :=
  contract_of_ports tN finrank_W8 (fun _ => 0) (fun _ => 1) (fun a b _ => Subsingleton.elim a b)
    (fun a b _ => Subsingleton.elim a b) (fun _ => v8) (fun _ => φ8) (fun _ => v8_ne) (fun _ => φ8_ne)
    (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl)
    tπ (by intro a b h; fin_cases a <;> fin_cases b <;> simp_all [tπ])
    (fun _ => by simp [tπ]) (fun _ => by simp [tπ])
    (by intro f g h; fin_cases f <;> fin_cases g <;> simp [tN, tO, tπ] at h ⊢)
    (fun _ => by simp [tN, tO]) (fun _ => by simp [tN, tO])

theorem tminor : ∀ C : Finset (Fin 2), (tN.O.submatrix (fun c : C => (c : Fin 2)) (fun c : C => (c : Fin 2))).det ≠ 0 := by
  intro C
  have : C = ∅ ∨ C = {0} ∨ C = {1} ∨ C = univ := by
    revert C; decide
  rcases this with rfl | rfl | rfl | rfl
  · simp
  · simp [Matrix.det_unique, tN, tO]
  · simp [Matrix.det_unique, tN, tO]
  · have e := Matrix.det_submatrix_equiv_self (Equiv.subtypeUnivEquiv (fun x : Fin 2 => mem_univ x)) tN.O
    have h2 : tN.O.det = 1 := by simp [Matrix.det_fin_two, tN, tO]; norm_num
    have : (tN.O.submatrix (fun c : (univ : Finset (Fin 2)) => (c : Fin 2)) (fun c : (univ : Finset (Fin 2)) => (c : Fin 2))) =
        tN.O.submatrix (Equiv.subtypeUnivEquiv (fun x : Fin 2 => mem_univ x)) (Equiv.subtypeUnivEquiv (fun x : Fin 2 => mem_univ x)) := rfl
    rw [this, e, h2]; exact one_ne_zero

end Toy

/-- the toy call as an HCall: n = 1, QR = 0, mains = the x row (climb 8 - 0... see below) -/
theorem toy_ht_le : ∀ c : Ch, finrank (ZMod 2) c ≤ 8 := ht_le_h finrank_W8

/-- the toy net satisfies the cut inequality of PriceH.HCall.hcut at h = 8, n = 1 for every mask. -/
theorem toy_cut (m : ℕ) :
    ∑ f, xcut m (finrank (ZMod 2) (tN.A f)) (finrank (ZMod 2) (tN.B f)) + (if isSepH 8 m then 2 * 1 else 0) ≤
      ∑ k, xcut m (finrank (ZMod 2) (tN.src k)) (finrank (ZMod 2) (tN.dst k)) :=
  cut_hsH tN tminor tHC m

end HCutGen
#print axioms HCutGen.rung_port_net_h7
#print axioms HCutGen.rung_port_net_h8
#print axioms HCutGen.tHC
