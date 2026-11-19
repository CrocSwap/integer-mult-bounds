/-
BankCallerGen.  CALLER-GENERIC banner (D ≥ 56 direction + height-stop rung, chain-tied head premises).
Caller family: caller block = K × (fixed per-call block T1/P1) + constant (Tc, Pc).
  T1 = targets 10 @ r9, 26 @ r17..65 (step 8), 13 @ r129;  P1 = paid 10 @ r1, 26 @ r8..56 (step 8).
PROVED (kernel only):
  cert_gen                       : for every K > 0 and every block with  cdat T - cdat P ≤ K (cdat T1 - cdat P1)  on s ∈ [0,1]
                                   (sign condition on the constant part), Cert of the banner ceiling at kbar = .00952721.
                                   The per-call root is .009527209881; since F_K = K Φ + c with c ≤ 0, κ_K ≤ root(Φ)
                                   for EVERY K: larger K gives LARGER (weaker) bounds when c < 0, equal ones when c = 0, and
                                   the sup over the family is root(Φ) itself, so ONE constant covers all K.
  bank_kappa_lt_banner_callergen : head theorem (as BankBannerHead) for any K-call caller satisfying the sign condition.
  bank_kappa_lt_banner_callerfam : same, family form  T = scale K T1 ++ Tc, P = scale K P1 ++ Pc, cdat Tc ≤ cdat Pc on [0,1].
  bank_kappa_lt_banner_caller48  : #7786's exact 48-call caller (BankCallerGenCert.TB/PB, consts7786) ⟹ κ < .00952721.
  hTP7761 / bank_kappa_lt_banner_caller7761_gen : #7761's 2048 caller is in the family (constant 224(9^s-1-8^s) ≤ 0,
                                   subadditivity of x^s), so the generic theorem also covers it (with the weaker .00952721).
-/
import Nov15.BankMedA
import Nov15.BankPrem
import Nov15.BankCallerGenCert

namespace BankCallerGen
open Finset Module BankNC0 BankWireC BankFit BankHelp BankBanner SafeRungsPrice BankFitHS BankTie BankPrem DecoderWall BankMed

variable {Fld Bank : Type} [Fintype Fld] [DecidableEq Fld] [Fintype Bank] [LinearOrder Bank]

/-- per-call caller block (targets / paid). -/
def T1 : List (ℕ × ℕ) := [(9, 10), (17, 26), (25, 26), (33, 26), (41, 26), (49, 26), (57, 26), (65, 26), (129, 13)]
def P1 : List (ℕ × ℕ) := [(1, 10), (8, 26), (16, 26), (24, 26), (32, 26), (40, 26), (48, 26), (56, 26)]

/-- K copies of a block. -/
def scale (K : ℕ) (l : List (ℕ × ℕ)) : List (ℕ × ℕ) := l.map fun p => (p.1, K * p.2)

def famT (K : ℕ) (Tc : List (ℕ × ℕ)) : List (ℕ × ℕ) := scale K T1 ++ Tc
def famP (K : ℕ) (Pc : List (ℕ × ℕ)) : List (ℕ × ℕ) := scale K P1 ++ Pc

theorem cdat_append (s : ℝ) (l m : List (ℕ × ℕ)) : cdat s (l ++ m) = cdat s l + cdat s m := by
  simp [cdat, List.map_append, List.sum_append]

theorem cdat_scale (s : ℝ) (K : ℕ) (l : List (ℕ × ℕ)) : cdat s (scale K l) = K * cdat s l := by
  induction l with
  | nil => simp [cdat, scale]
  | cons p l ih =>
    simp only [scale, cdat, List.map_cons, List.sum_cons] at ih ⊢
    rw [ih]; push_cast; ring

/-- #7786's caller IS 48 × the per-call block, no constant (decide-checked). -/
theorem T48_eq : BankCallerGenCert.TB = scale 48 T1 := by decide
theorem P48_eq : BankCallerGenCert.PB = scale 48 P1 := by decide

/-- **uniform certificate**: every caller of the family with a nonpositive constant part, any K > 0. -/
theorem cert_gen (K : ℕ) (hK : 0 < K) (T P : List (ℕ × ℕ))
    (hTP : ∀ s : ℝ, 0 ≤ s → s ≤ 1 → cdat s T - cdat s P ≤ K * (cdat s T1 - cdat s P1)) :
    Cert (fun s => cdat s T - cdat s P
      - K * (400 * 8 ^ s + 112 * (9 ^ s - 8 ^ s) + 104 * (1 + 7 ^ s - 8 ^ s))) (952721 / 100000000) := by
  intro t h1 h2
  have hc := BankCallerGenCert.cert t h1 h2
  unfold BankCallerGenCert.FceilBank at hc
  rw [T48_eq, P48_eq, cdat_scale, cdat_scale] at hc
  push_cast at hc
  have hb := hTP (1 - t) (by linarith) (by norm_num at h1; linarith)
  have hKr : (0 : ℝ) < K := by exact_mod_cast hK
  have hneg : cdat (1 - t) T1 - cdat (1 - t) P1 - (400 * (8:ℝ) ^ (1 - t) + 112 * ((9:ℝ) ^ (1 - t) - (8:ℝ) ^ (1 - t))
      + 104 * (1 + (7:ℝ) ^ (1 - t) - (8:ℝ) ^ (1 - t))) < 0 := by linarith
  have := mul_neg_of_pos_of_neg hKr hneg
  dsimp only
  linarith

/-- family form of the sign condition. -/
theorem hTP_fam (K : ℕ) (Tc Pc : List (ℕ × ℕ)) (hsign : ∀ s : ℝ, 0 ≤ s → s ≤ 1 → cdat s Tc ≤ cdat s Pc) :
    ∀ s : ℝ, 0 ≤ s → s ≤ 1 → cdat s (famT K Tc) - cdat s (famP K Pc) ≤ K * (cdat s T1 - cdat s P1) := by
  intro s h0 h1
  simp only [famT, famP, cdat_append, cdat_scale]
  have := hsign s h0 h1
  linarith

/-- **caller-generic banner head**: any K-call caller whose block is ≤ K × per-call block on [0,1]. -/
theorem bank_kappa_lt_banner_callergen (K : ℕ) (hK : 0 < K) (c : Caller ℚ Fld Bank K)
    (hTP : ∀ s : ℝ, 0 ≤ s → s ≤ 1 → cdat s c.T - cdat s c.P ≤ K * (cdat s T1 - cdat s P1))
    (hc : ∀ i, HSContract (c.G i).N)
    {T : Type} [Fintype T] (τ : ∀ i, ChainTie (c.G i) T) (h8 : Fintype.card T ≤ 8) (cs : Fin K → Fin 104 → ℚ)
    (hC : ∀ i, ComputesS (c.G i) (τ i).xin (τ i).yout (cs i))
    (hin : ∀ i p, DF.lq p ∈ (c.G i).N.A ((τ i).xin p))
    (hout : ∀ i s, ∀ y ∈ (c.G i).N.B ((τ i).yout s), dot (DF.lq s) y = 0)
    (hcov : ∀ i k, ¬ (c.G i).N.src k ≤ (c.G i).N.dst k → ∃ x, (τ i).e x = k)
    {O : Type} [Fintype O] (oi oc : Fin K → O → Chart)
    (hF : ∀ i, (gModel (c.G i) (oi i) (oc i)).Flow) (hW : ∀ i, 0 ≤ (gModel (c.G i) (oi i) (oc i)).W)
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : Valid c (1 - κ) (fun i k => specInvoice (c.G i) (1 - κ) k)) :
    κ < 952721 / 100000000 := by
  have hex := fun i => mediatedS_of_loc (τ i) (cs i) (fun s => ((hC i).1 s).1) (hin i) (hout i) (hcov i)
  choose τ' hx hy hM using hex
  have hD : ∀ i, 56 ≤ descMass (c.G i) := fun i =>
    tie_desc_ge_56S (τ' i) (cs i) h8 (by rw [hx i, hy i]; exact hC i) (hM i)
  have hXD : ∀ i, 2 * descMass (c.G i) ≤ excess (c.G i) := fun i => xbal_tied (c.G i) (oi i) (oc i) (hF i) (hW i)
  exact bank_kappa_lt_banner_of_cert K c.T c.P _ (by norm_num) (cert_gen K hK c.T c.P hTP) c.G hc hD hXD
    κ hκ0 hκ1 _ (fun i k => bankPrice_le_specInvoice (c.G i) (by linarith) k) (hcaller_of_valid c _ _ hV)

/-- **uniform statement, family form**: T = K·T1 ++ Tc, P = K·P1 ++ Pc with cdat Tc ≤ cdat Pc on [0,1], any K > 0. -/
theorem bank_kappa_lt_banner_callerfam (K : ℕ) (hK : 0 < K) (Tc Pc : List (ℕ × ℕ))
    (hsign : ∀ s : ℝ, 0 ≤ s → s ≤ 1 → cdat s Tc ≤ cdat s Pc) (c : Caller ℚ Fld Bank K)
    (hT : c.T = famT K Tc) (hP : c.P = famP K Pc)
    (hc : ∀ i, HSContract (c.G i).N)
    {T : Type} [Fintype T] (τ : ∀ i, ChainTie (c.G i) T) (h8 : Fintype.card T ≤ 8) (cs : Fin K → Fin 104 → ℚ)
    (hC : ∀ i, ComputesS (c.G i) (τ i).xin (τ i).yout (cs i))
    (hin : ∀ i p, DF.lq p ∈ (c.G i).N.A ((τ i).xin p))
    (hout : ∀ i s, ∀ y ∈ (c.G i).N.B ((τ i).yout s), dot (DF.lq s) y = 0)
    (hcov : ∀ i k, ¬ (c.G i).N.src k ≤ (c.G i).N.dst k → ∃ x, (τ i).e x = k)
    {O : Type} [Fintype O] (oi oc : Fin K → O → Chart)
    (hF : ∀ i, (gModel (c.G i) (oi i) (oc i)).Flow) (hW : ∀ i, 0 ≤ (gModel (c.G i) (oi i) (oc i)).W)
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : Valid c (1 - κ) (fun i k => specInvoice (c.G i) (1 - κ) k)) :
    κ < 952721 / 100000000 :=
  bank_kappa_lt_banner_callergen K hK c (by rw [hT, hP]; exact hTP_fam K Tc Pc hsign) hc τ h8 cs hC hin hout hcov
    oi oc hF hW κ hκ0 hκ1 hV

/-! ## #7786 constants (DATA: lean/tools/callergen/app7786-caller.json = caller of #7786 evidence/application.json), decide-checked -/
open BankCallerGenCert in
theorem consts7786 :
    TB = [(9, 480), (17, 1248), (25, 1248), (33, 1248), (41, 1248), (49, 1248), (57, 1248), (65, 1248), (129, 624)] ∧
    PB = [(1, 480), (8, 1248), (16, 1248), (24, 1248), (32, 1248), (40, 1248), (48, 1248), (56, 1248)] ∧
    TB = famT 48 [] ∧ PB = famP 48 [] ∧
    (480 = 48 * 10 ∧ 1248 = 48 * 26 ∧ 624 = 48 * 13) := by
  refine ⟨rfl, rfl, ?_, ?_, ?_⟩ <;> decide

/-- **#7786** (frontier, κ .00387827): its own 48-call caller, banner head ⟹ κ < .00952721 (root .009527209881). -/
theorem bank_kappa_lt_banner_caller48 (c : Caller ℚ Fld Bank 48)
    (hT : c.T = BankCallerGenCert.TB) (hP : c.P = BankCallerGenCert.PB)
    (hc : ∀ i, HSContract (c.G i).N)
    {T : Type} [Fintype T] (τ : ∀ i, ChainTie (c.G i) T) (h8 : Fintype.card T ≤ 8) (cs : Fin 48 → Fin 104 → ℚ)
    (hC : ∀ i, ComputesS (c.G i) (τ i).xin (τ i).yout (cs i))
    (hin : ∀ i p, DF.lq p ∈ (c.G i).N.A ((τ i).xin p))
    (hout : ∀ i s, ∀ y ∈ (c.G i).N.B ((τ i).yout s), dot (DF.lq s) y = 0)
    (hcov : ∀ i k, ¬ (c.G i).N.src k ≤ (c.G i).N.dst k → ∃ x, (τ i).e x = k)
    {O : Type} [Fintype O] (oi oc : Fin 48 → O → Chart)
    (hF : ∀ i, (gModel (c.G i) (oi i) (oc i)).Flow) (hW : ∀ i, 0 ≤ (gModel (c.G i) (oi i) (oc i)).W)
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : Valid c (1 - κ) (fun i k => specInvoice (c.G i) (1 - κ) k)) :
    κ < 952721 / 100000000 :=
  bank_kappa_lt_banner_callergen 48 (by norm_num) c
    (by intro s _ _; rw [hT, hP, T48_eq, P48_eq, cdat_scale, cdat_scale]; push_cast; linarith)
    hc τ h8 cs hC hin hout hcov oi oc hF hW κ hκ0 hκ1 hV

/-! ## #7761 is in the family: constant 224 (9^s - 1 - 8^s) ≤ 0 -/
theorem nine_le (s : ℝ) (h0 : 0 ≤ s) (h1 : s ≤ 1) : (9:ℝ) ^ s ≤ 1 + (8:ℝ) ^ s := by
  have h := NNReal.rpow_add_le_add_rpow (1 : NNReal) 8 h0 h1
  have h' : ((((1:NNReal) + 8) ^ s : NNReal) : ℝ) ≤ (((1:NNReal) ^ s + (8:NNReal) ^ s : NNReal) : ℝ) := by
    exact_mod_cast h
  rw [NNReal.coe_add, NNReal.coe_rpow, NNReal.coe_rpow, NNReal.coe_rpow, NNReal.coe_add] at h'
  norm_num at h'
  linarith

theorem hTP7761 : ∀ s : ℝ, 0 ≤ s → s ≤ 1 →
    cdat s BankBannerCert.TB - cdat s BankBannerCert.PB ≤ (2048 : ℕ) * (cdat s T1 - cdat s P1) := by
  intro s h0 h1
  have h9 := nine_le s h0 h1
  simp only [cdat, BankBannerCert.TB, BankBannerCert.PB, T1, P1, List.map_cons, List.map_nil, List.sum_cons,
    List.sum_nil]
  push_cast
  rw [Real.one_rpow]
  nlinarith

/-- the generic theorem also covers #7761's 2048-call caller (weaker constant than the shipped .009526828). -/
theorem bank_kappa_lt_banner_caller7761_gen (c : Caller ℚ Fld Bank 2048)
    (hT : c.T = BankBannerCert.TB) (hP : c.P = BankBannerCert.PB)
    (hc : ∀ i, HSContract (c.G i).N)
    {T : Type} [Fintype T] (τ : ∀ i, ChainTie (c.G i) T) (h8 : Fintype.card T ≤ 8) (cs : Fin 2048 → Fin 104 → ℚ)
    (hC : ∀ i, ComputesS (c.G i) (τ i).xin (τ i).yout (cs i))
    (hin : ∀ i p, DF.lq p ∈ (c.G i).N.A ((τ i).xin p))
    (hout : ∀ i s, ∀ y ∈ (c.G i).N.B ((τ i).yout s), dot (DF.lq s) y = 0)
    (hcov : ∀ i k, ¬ (c.G i).N.src k ≤ (c.G i).N.dst k → ∃ x, (τ i).e x = k)
    {O : Type} [Fintype O] (oi oc : Fin 2048 → O → Chart)
    (hF : ∀ i, (gModel (c.G i) (oi i) (oc i)).Flow) (hW : ∀ i, 0 ≤ (gModel (c.G i) (oi i) (oc i)).W)
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : Valid c (1 - κ) (fun i k => specInvoice (c.G i) (1 - κ) k)) :
    κ < 952721 / 100000000 :=
  bank_kappa_lt_banner_callergen 2048 (by norm_num) c (by rw [hT, hP]; exact hTP7761)
    hc τ h8 cs hC hin hout hcov oi oc hF hW κ hκ0 hκ1 hV

end BankCallerGen
#print axioms BankCallerGen.cert_gen
#print axioms BankCallerGen.bank_kappa_lt_banner_callergen
#print axioms BankCallerGen.bank_kappa_lt_banner_callerfam
#print axioms BankCallerGen.consts7786
#print axioms BankCallerGen.bank_kappa_lt_banner_caller48
#print axioms BankCallerGen.bank_kappa_lt_banner_caller7761_gen
