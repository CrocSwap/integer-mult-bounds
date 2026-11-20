/-
CertCaller7113Link (lane CK-CALLER, Nov 19).  CERTKIT brackets with the caller block DERIVED from the #7113 caller file
(cards/WILD/MONOCALLER/7113_CALLER.json, via CertCaller7113Facts), not the DATA constant SafeRungsPrice.Tcal/Pcal:
  ValidAtD κ :=  cdat (1-κ) (pRaw C) + Σ_{calls C} wordPaid ≤ cdat (1-κ) (tRaw C) + Σ_{calls C} helper credits,
where tRaw/pRaw are the caller's own raw items (one per diagonal row / invoiced event, per port) and calls C = #J events.
kwordD (sSup over ValidAtD) = CertT7669.kword / CertWs4.kword, hence the same [lo, hi] brackets.  Kernel only.
-/
import Nov15.CertT7669
import Nov15.CertWs4
import Nov15.CertCaller7113Facts

namespace CertCaller7113Link
open Uni WordModel Finset UniFold7113 UniUniversal SafeRungsPrice CertKit CertCaller CertCaller7113

theorem sum_calls (x : ℝ) : ∑ _i : Fin (calls Data.C), x = ∑ _i : Fin 17, x := by
  simp only [Finset.sum_const, Finset.card_univ, Fintype.card_fin, L_eq]

/-- t7669: the Valid inequality with the caller block derived from the caller file. -/
def ValidAtT (κ : ℝ) : Prop :=
  cdat (1 - κ) (pRaw Data.C) + ∑ _i : Fin (calls Data.C), wordPaid caller7113 (exec UniInhabit.tr7669) specPrice (1 - κ) ≤
    cdat (1 - κ) (tRaw Data.C) + ∑ _i : Fin (calls Data.C), ∑ r ∈ (helpers : Finset UniInhabit.R7), gc (1 - κ) (hcred (exec UniInhabit.tr7669) r)

theorem validT_iff (κ : ℝ) : ValidAtT κ ↔ CertT7669.ValidAt κ := by
  unfold ValidAtT CertT7669.ValidAt
  rw [sum_calls, sum_calls, ← cdat_hist _ (pRaw _), ← cdat_hist _ (tRaw _), ← Tcal_eq, ← Pcal_eq]

noncomputable def kwordT : ℝ := sSup {κ : ℝ | 0 ≤ κ ∧ κ < 1 ∧ ValidAtT κ}

theorem kwordT_eq : kwordT = CertT7669.kword := by
  unfold kwordT CertT7669.kword; simp only [validT_iff]

/-- **t7669 bracket, caller derived**: lo ≤ κ ≤ hi with no caller constant trusted. -/
theorem kwordT_bracket : CertT7669.lo ≤ kwordT ∧ kwordT ≤ CertT7669.hi := by
  rw [kwordT_eq]; exact CertT7669.kword_bracket

/-- w_s4: the Valid inequality with the caller block derived from the caller file. -/
def ValidAtW (κ : ℝ) : Prop :=
  cdat (1 - κ) (pRaw Data.C) + ∑ _i : Fin (calls Data.C), wordPaid caller7113 (exec UniInhabitWs4.trWs4) specPrice (1 - κ) ≤
    cdat (1 - κ) (tRaw Data.C) + ∑ _i : Fin (calls Data.C), ∑ r ∈ (helpers : Finset UniInhabitWs4.R7), gc (1 - κ) (hcred (exec UniInhabitWs4.trWs4) r)

theorem validW_iff (κ : ℝ) : ValidAtW κ ↔ CertWs4.ValidAt κ := by
  unfold ValidAtW CertWs4.ValidAt
  rw [sum_calls, sum_calls, ← cdat_hist _ (pRaw _), ← cdat_hist _ (tRaw _), ← Tcal_eq, ← Pcal_eq]

noncomputable def kwordW : ℝ := sSup {κ : ℝ | 0 ≤ κ ∧ κ < 1 ∧ ValidAtW κ}

theorem kwordW_eq : kwordW = CertWs4.kword := by
  unfold kwordW CertWs4.kword; simp only [validW_iff]

/-- **w_s4 bracket, caller derived**. -/
theorem kwordW_bracket : CertWs4.lo ≤ kwordW ∧ kwordW ≤ CertWs4.hi := by
  rw [kwordW_eq]; exact CertWs4.kword_bracket

end CertCaller7113Link

#print axioms CertCaller7113Link.kwordT_bracket
#print axioms CertCaller7113Link.kwordW_bracket
