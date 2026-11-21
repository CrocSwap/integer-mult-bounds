/-
CallerWordD (lane CALLERWORD, Nov 20).  The D-structure of a legal caller word (CallerWord): masks, stage incidence,
support and biorthogonality, derived from `Legal` alone (evaluated over the dual numbers ℂ[ε], q = 1, D_t0 = 1 + ε,
D_t = 1 otherwise).

Notation: P1 m = base prefix (q = 1, D = 1) of the first m events; an INCIDENCE of stage t0 is an IDLE event
`idle r T σ` with t0 ∈ T (this includes the J contacts, which are `idle x {t} 0`); E_t0 = {r : t0 ∈ mask r}.
* `linear_E1`      : diag(1[t0 ∈ mask r]) = Σ_j P1(j+1)^-1 Z_j P1(j),  Z_j = E_{rr} for an incidence on register r.
* `stage_incidence`: |E_t0| = #incidences of t0 (D-degree count; MAINS + idle incidences = mask incidences).
* `incV`/`incW`    : v_j = P1(j)^-1 e_r, w_j = P1(j)^T e_r for each incidence j;  Π_t0 = V W^T,
  `biorth`         : W^T V = 1  (w_j · v_j' = δ for incidences sharing stage t0),
  `support_V/W`    : v_j, w_j vanish outside E_t0.
Kernel only: no sorry, no native_decide, no new axioms.
-/
import Mathlib.Algebra.DualNumber
import Nov15.CallerWord

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace CallerWord
open Matrix Finset CallerSign TrivSqZeroExt DualNumber

abbrev DN := DualNumber ℂ

section dn
variable {n k : ℕ}

/-- D_t0 = 1 + ε, other D_t = 1. -/
noncomputable def Dt (t0 : Fin k) : Fin k → DN := fun t => if t = t0 then 1 + ε else 1

noncomputable def fstM (M : Matrix (Fin n) (Fin n) DN) : Matrix (Fin n) (Fin n) ℂ := M.map fst
noncomputable def sndM (M : Matrix (Fin n) (Fin n) DN) : Matrix (Fin n) (Fin n) ℂ := M.map snd

theorem fstM_mul (M N : Matrix (Fin n) (Fin n) DN) : fstM (M * N) = fstM M * fstM N := by
  ext a b; simp [fstM, Matrix.mul_apply, fst_sum]

theorem sndM_mul (M N : Matrix (Fin n) (Fin n) DN) :
    sndM (M * N) = fstM M * sndM N + sndM M * fstM N := by
  ext a b
  simp only [sndM, fstM, Matrix.map_apply, Matrix.mul_apply, Matrix.add_apply, snd_sum, DualNumber.snd_mul,
    ← Finset.sum_add_distrib]

theorem fstM_one : fstM (1 : Matrix (Fin n) (Fin n) DN) = 1 := by
  ext a b; by_cases h : a = b <;> simp [fstM, Matrix.one_apply, h]

theorem sndM_one : sndM (1 : Matrix (Fin n) (Fin n) DN) = 0 := by
  ext a b; by_cases h : a = b <;> simp [sndM, Matrix.one_apply, h]

theorem fstM_E1 (x y : Fin n) (c : DN) : fstM (E1 x y c) = E1 x y c.fst := by
  ext a b; simp only [fstM, E1, Matrix.map_apply, Matrix.of_apply]; split_ifs <;> simp

theorem sndM_E1 (x y : Fin n) (c : DN) : sndM (E1 x y c) = E1 x y c.snd := by
  ext a b; simp only [sndM, E1, Matrix.map_apply, Matrix.of_apply]; split_ifs <;> simp

theorem fstM_add (M N : Matrix (Fin n) (Fin n) DN) : fstM (M + N) = fstM M + fstM N := by
  ext a b; simp [fstM]
theorem sndM_add (M N : Matrix (Fin n) (Fin n) DN) : sndM (M + N) = sndM M + sndM N := by
  ext a b; simp [sndM]

theorem prod_Dt (t0 : Fin k) (T : Finset (Fin k)) : ∏ t ∈ T, Dt t0 t = if t0 ∈ T then 1 + ε else 1 := by
  unfold Dt; rw [Finset.prod_ite_eq']

/-- the ε-part of an event. -/
noncomputable def Zm (t0 : Fin k) : Ev n k → Matrix (Fin n) (Fin n) ℂ
  | .idle r T _ => if t0 ∈ T then E1 r r 1 else 0
  | _ => 0

/-- incidence predicate. -/
def inc (t0 : Fin k) : Ev n k → Bool
  | .idle _ T _ => decide (t0 ∈ T)
  | _ => false

/-- register of an event (row slot 0). -/
def reg : Ev n k → Fin n
  | .add r _ _ => r | .scale r _ => r | .swap r _ => r | .query r _ _ => r | .lam r _ => r
  | .idle r _ _ => r | .host s _ _ _ => s

noncomputable def iD : DN := inl Complex.I

theorem ev_fst (t0 : Fin k) (e : Ev n k) :
    fstM (evMat (1 : DN) iD (Dt t0) e) = evMat (1 : ℂ) Complex.I 1 e := by
  cases e with
  | add r s c => simp [evMat, fstM_add, fstM_one, fstM_E1, algebraMap_eq_inl']
  | scale r c => simp [evMat, fstM_add, fstM_one, fstM_E1, algebraMap_eq_inl']
  | swap r s =>
    ext a b; simp only [fstM, evMat, Matrix.map_apply, Matrix.of_apply]; split_ifs <;> simp
  | query r s σ => simp [evMat, fstM_add, fstM_one, fstM_E1, qp]
  | lam r σ => simp [evMat, fstM_add, fstM_one, fstM_E1, algebraMap_eq_inl', iD]
  | idle r T σ =>
    simp only [evMat, fstM_add, fstM_one, fstM_E1, prod_Dt, qp, one_pow, one_mul, Pi.one_apply,
      Finset.prod_const_one]
    split_ifs <;> simp
  | host s t a b => simp [evMat, fstM_add, fstM_one, fstM_E1, algebraMap_eq_inl']

theorem ev_snd (t0 : Fin k) (e : Ev n k) :
    sndM (evMat (1 : DN) iD (Dt t0) e) = Zm t0 e := by
  cases e with
  | add r s c => simp [evMat, Zm, sndM_add, sndM_one, sndM_E1, algebraMap_eq_inl', E1_zero]
  | scale r c => simp [evMat, Zm, sndM_add, sndM_one, sndM_E1, algebraMap_eq_inl', E1_zero]
  | swap r s =>
    ext a b; simp only [sndM, evMat, Zm, Matrix.map_apply, Matrix.of_apply]; split_ifs <;> simp
  | query r s σ => simp [evMat, Zm, sndM_add, sndM_one, sndM_E1, qp, E1_zero]
  | lam r σ => simp [evMat, Zm, sndM_add, sndM_one, sndM_E1, algebraMap_eq_inl', iD, E1_zero]
  | idle r T σ =>
    simp only [evMat, Zm, sndM_add, sndM_one, sndM_E1, prod_Dt, qp, one_pow, one_mul, zero_add]
    split_ifs <;> simp [E1_zero]
  | host s t a b => simp [evMat, Zm, sndM_add, sndM_one, sndM_E1, algebraMap_eq_inl', E1_zero]

end dn

section lin
variable {n k : ℕ} (w : CWord n k) (t0 : Fin k)

noncomputable def PD (m : ℕ) : Matrix (Fin n) (Fin n) DN := pre (1 : DN) iD (Dt t0) w.evs m

noncomputable def Zat (j : ℕ) : Matrix (Fin n) (Fin n) ℂ := ((w.evs[j]?).map (Zm t0)).getD 0

theorem fst_PD (m : ℕ) : fstM (PD w t0 m) = P1 w Complex.I m := by
  induction m with
  | zero => simp [PD, P1, pre, fstM_one]
  | succ m ih =>
    unfold PD P1 at *
    rw [pre_succ, pre_succ, fstM_mul, ih]
    congr 1
    cases h : w.evs[m]? with
    | none => simp [fstM_one]
    | some e => simp [ev_fst]

theorem snd_step (m : ℕ) :
    sndM (PD w t0 (m + 1)) = ((w.evs[m]?).map (evMat (1 : ℂ) Complex.I 1)).getD 1 * sndM (PD w t0 m)
      + Zat w t0 m * P1 w Complex.I m := by
  unfold PD Zat
  rw [pre_succ, sndM_mul, ← fst_PD w t0 m]
  unfold PD
  congr 2
  · cases h : w.evs[m]? with
    | none => simp [fstM_one]
    | some e => simp [ev_fst]
  · cases h : w.evs[m]? with
    | none => simp [sndM_one]
    | some e => simp [ev_snd]

variable (hb : replay (1 : ℂ) Complex.I 1 w.evs = 1)
include hb

theorem snd_tele (m : ℕ) (hm : m ≤ w.evs.length) :
    (P1 w Complex.I m)⁻¹ * sndM (PD w t0 m)
      = ∑ j ∈ range m, (P1 w Complex.I (j + 1))⁻¹ * Zat w t0 j * P1 w Complex.I j := by
  induction m with
  | zero => simp [PD, pre, sndM_one]
  | succ m ih =>
    have hlt : m < w.evs.length := by omega
    have hu0 : IsUnit (P1 w Complex.I m).det := isUnit_iff_ne_zero.mpr (det_P1_ne w _ hb m (by omega))
    have hu1 : IsUnit (P1 w Complex.I (m + 1)).det :=
      isUnit_iff_ne_zero.mpr (det_P1_ne w _ hb (m + 1) (by omega))
    rw [Finset.sum_range_succ, ← ih (by omega), snd_step, evAt_get w _ 1 1 m hlt]
    set Y := evMat (1 : ℂ) Complex.I 1 (w.evs.get ⟨m, hlt⟩)
    have hP1 : P1 w Complex.I (m + 1) = Y * P1 w Complex.I m := by
      unfold P1; rw [pre_succ, evAt_get w _ 1 1 m hlt]
    have hY : (P1 w Complex.I (m + 1))⁻¹ * Y = (P1 w Complex.I m)⁻¹ := by
      have e : (P1 w Complex.I (m + 1))⁻¹ * Y * P1 w Complex.I m = 1 := by
        rw [Matrix.mul_assoc, ← hP1, nonsing_inv_mul _ hu1]
      calc (P1 w Complex.I (m + 1))⁻¹ * Y
          = (P1 w Complex.I (m + 1))⁻¹ * Y * P1 w Complex.I m * (P1 w Complex.I m)⁻¹ := by
            rw [Matrix.mul_assoc _ (P1 w Complex.I m), mul_nonsing_inv _ hu0, Matrix.mul_one]
        _ = (P1 w Complex.I m)⁻¹ := by rw [e, Matrix.one_mul]
    rw [Matrix.mul_add, ← Matrix.mul_assoc, hY, Matrix.mul_assoc]

/-- the mask projector of stage t0. -/
noncomputable def Pi0 : Matrix (Fin n) (Fin n) ℂ := Matrix.diagonal fun r => if t0 ∈ w.mask r then 1 else 0

/-- LINEAR E1: the stage-t0 mask projector is the sum of the conjugated incidence idempotents. -/
theorem linear_E1 (hL : LegalAt (1 : DN) iD (Dt t0) w) :
    Pi0 w t0 = ∑ j ∈ range w.evs.length, (P1 w Complex.I (j + 1))⁻¹ * Zat w t0 j * P1 w Complex.I j := by
  rw [← snd_tele w t0 hb _ le_rfl]
  have h1 : P1 w Complex.I w.evs.length = 1 := hb
  rw [h1, inv_one, Matrix.one_mul]
  have : PD w t0 w.evs.length = target (1 : DN) (Dt t0) w := hL
  rw [this]
  ext a b
  by_cases h : a = b
  · subst h; simp [Pi0, sndM, target, prod_Dt, qp]; split_ifs <;> simp
  · simp [Pi0, sndM, target, h]

end lin

/-- a matrix whose rank equals its width is left-cancellable. -/
theorem cancel_left {n : ℕ} {J : Type*} [Fintype J] [DecidableEq J] {m : Type*} (M : Matrix (Fin n) J ℂ)
    (hr : M.rank = Fintype.card J) (X Y : Matrix J m ℂ) (h : M * X = M * Y) : X = Y := by
  have hk : LinearMap.ker M.mulVecLin = ⊥ := by
    have h1 := LinearMap.finrank_range_add_finrank_ker M.mulVecLin
    rw [Module.finrank_fintype_fun_eq_card] at h1
    have h2 : Module.finrank ℂ (LinearMap.range M.mulVecLin) = M.rank := rfl
    rw [h2, hr] at h1
    exact Submodule.finrank_eq_zero.mp (by omega)
  ext a c
  have hinj := LinearMap.ker_eq_bot.mp hk
  have : M.mulVecLin (fun x => X x c) = M.mulVecLin (fun x => Y x c) := by
    ext r
    have := congrFun (congrFun h r) c
    simpa [Matrix.mulVecLin_apply, Matrix.mulVec, dotProduct, Matrix.mul_apply] using this
  exact congrFun (hinj this) a

/-- idempotent factorisation: Π = V W^T idempotent of rank |J|  ==>  W^T V = 1, Π V = V, W^T Π = W^T. -/
theorem idem_factor {n : ℕ} {J : Type*} [Fintype J] [DecidableEq J] (Pm : Matrix (Fin n) (Fin n) ℂ)
    (V W : Matrix (Fin n) J ℂ) (hPi : Pm = V * Wᵀ) (hidem : Pm * Pm = Pm) (hr : Pm.rank = Fintype.card J) :
    Wᵀ * V = 1 ∧ Pm * V = V ∧ Wᵀ * Pm = Wᵀ := by
  have hrV : V.rank = Fintype.card J := by
    apply le_antisymm (Matrix.rank_le_card_width V)
    rw [← hr, hPi]; exact Matrix.rank_mul_le_left _ _
  have hrW : W.rank = Fintype.card J := by
    apply le_antisymm (Matrix.rank_le_card_width W)
    rw [← hr, hPi, ← Matrix.rank_transpose W]; exact Matrix.rank_mul_le_right _ _
  have e1 : V * (Wᵀ * (V * Wᵀ)) = V * Wᵀ := by
    have := hidem; rw [hPi] at this
    simpa [Matrix.mul_assoc] using this
  have e2 : Wᵀ * (V * Wᵀ) = Wᵀ := cancel_left V hrV _ _ e1
  have e3 : W * (Vᵀ * W) = W * (1 : Matrix J J ℂ) := by
    have := congrArg Matrix.transpose e2
    simpa [Matrix.transpose_mul, Matrix.mul_assoc] using this
  have e4 : Vᵀ * W = 1 := cancel_left W hrW _ _ e3
  have hbi : Wᵀ * V = 1 := by
    have := congrArg Matrix.transpose e4; simpa [Matrix.transpose_mul] using this
  refine ⟨hbi, ?_, ?_⟩
  · rw [hPi, Matrix.mul_assoc, hbi, Matrix.mul_one]
  · rw [hPi, ← Matrix.mul_assoc, hbi, Matrix.one_mul]

/-! ## incidences: trace count, V W^T factorisation, biorthogonality, support -/

section incid
variable {n k : ℕ} (w : CWord n k) (t0 : Fin k)

/-- the incidences of t0 (event indices). -/
abbrev Inc := {j : Fin w.evs.length // inc t0 (w.evs.get j) = true}

noncomputable def incV : Matrix (Fin n) (Inc w t0) ℂ :=
  Matrix.of fun r j => (P1 w Complex.I j.1.val)⁻¹ r (reg (w.evs.get j.1))
noncomputable def incW : Matrix (Fin n) (Inc w t0) ℂ :=
  Matrix.of fun r j => P1 w Complex.I j.1.val (reg (w.evs.get j.1)) r

theorem idle_base (r : Fin n) (T : Finset (Fin k)) (σ : ℤ) :
    evMat (1 : ℂ) Complex.I 1 (Ev.idle r T σ) = 1 := by
  simp [evMat, qp, E1_zero]

theorem zat_term (j : Fin w.evs.length) :
    (P1 w Complex.I (j.val + 1))⁻¹ * Zat w t0 j.val * P1 w Complex.I j.val
      = if inc t0 (w.evs.get j) then
          Matrix.of (fun r r' => (P1 w Complex.I j.val)⁻¹ r (reg (w.evs.get j)) *
            P1 w Complex.I j.val (reg (w.evs.get j)) r')
        else 0 := by
  have hP : P1 w Complex.I (j.val + 1) = evMat (1 : ℂ) Complex.I 1 (w.evs.get j) * P1 w Complex.I j.val := by
    unfold P1; rw [pre_succ, evAt_get w _ 1 1 j.val j.isLt]
  have hZ : Zat w t0 j.val = Zm t0 (w.evs.get j) := by
    unfold Zat; rw [List.getElem?_eq_getElem j.isLt]; rfl
  rw [hZ, hP]
  generalize w.evs.get j = e
  cases e with
  | idle r T σ =>
    rw [idle_base, Matrix.one_mul]
    simp only [Zm, inc]
    by_cases h : t0 ∈ T
    · simp only [h, if_true, decide_true]
      ext a b; rw [sandwich]; simp [reg]
    · simp [h]
  | _ => simp [Zm, inc]

variable (hb : replay (1 : ℂ) Complex.I 1 w.evs = 1)
include hb

theorem Pi0_VW (hL : LegalAt (1 : DN) iD (Dt t0) w) : Pi0 w t0 = incV w t0 * (incW w t0)ᵀ := by
  rw [linear_E1 w t0 hb hL]
  rw [Finset.sum_range (fun j => (P1 w Complex.I (j + 1))⁻¹ * Zat w t0 j * P1 w Complex.I j)]
  simp only [zat_term]
  ext a b
  rw [Matrix.sum_apply]
  simp only [Matrix.mul_apply, Matrix.transpose_apply, incV, incW, Matrix.of_apply]
  rw [← Finset.sum_subtype (univ.filter fun j : Fin w.evs.length => inc t0 (w.evs.get j) = true) (by simp)
    (fun j : Fin w.evs.length => (P1 w Complex.I j.val)⁻¹ a (reg (w.evs.get j)) *
      P1 w Complex.I j.val (reg (w.evs.get j)) b)]
  rw [Finset.sum_filter]
  refine Finset.sum_congr rfl fun j _ => ?_
  split_ifs <;> simp

/-- trace of an incidence term is 1. -/
theorem trace_inc :
    (incV w t0 * (incW w t0)ᵀ).trace = (Fintype.card (Inc w t0) : ℂ) := by
  rw [Matrix.trace_mul_comm]
  have : ∀ j : Inc w t0, ((incW w t0)ᵀ * incV w t0) j j = 1 := by
    intro j
    have hu : IsUnit (P1 w Complex.I j.1.val).det :=
      isUnit_iff_ne_zero.mpr (det_P1_ne w _ hb _ j.1.isLt.le)
    have := congrFun (congrFun (mul_nonsing_inv (P1 w Complex.I j.1.val) hu) (reg (w.evs.get j.1)))
      (reg (w.evs.get j.1))
    simp only [Matrix.mul_apply, Matrix.one_apply_eq] at this
    simp only [Matrix.mul_apply, Matrix.transpose_apply, incV, incW, Matrix.of_apply]
    rw [← this]
  simp [Matrix.trace, this]

theorem trace_Pi0 : (Pi0 w t0).trace = ((univ.filter fun r => t0 ∈ w.mask r).card : ℂ) := by
  simp [Pi0, Matrix.trace, Finset.sum_boole]

/-- STAGE INCIDENCE: |E_t0| = #incidences of t0. -/
theorem stage_incidence (hL : LegalAt (1 : DN) iD (Dt t0) w) :
    (univ.filter fun r => t0 ∈ w.mask r).card = Fintype.card (Inc w t0) := by
  have h := trace_Pi0 w t0 hb
  rw [Pi0_VW w t0 hb hL, trace_inc w t0 hb] at h
  exact_mod_cast h.symm

/-- BIORTHOGONALITY: W^T V = 1, and SUPPORT: Π V = V, W^T Π = W^T. -/
theorem biorth (hL : LegalAt (1 : DN) iD (Dt t0) w) :
    (incW w t0)ᵀ * incV w t0 = 1 ∧ Pi0 w t0 * incV w t0 = incV w t0 ∧
      (incW w t0)ᵀ * Pi0 w t0 = (incW w t0)ᵀ := by
  classical
  have hPi := Pi0_VW w t0 hb hL
  have hcard := stage_incidence w t0 hb hL
  have hrPi : (Pi0 w t0).rank = Fintype.card (Inc w t0) := by
    rw [Pi0, Matrix.rank_diagonal, ← hcard, Fintype.card_subtype]
    congr 1; ext r; simp
  have hidem : Pi0 w t0 * Pi0 w t0 = Pi0 w t0 := by
    unfold Pi0; rw [Matrix.diagonal_mul_diagonal]; congr 1; funext r; split_ifs <;> simp
  exact idem_factor (Pi0 w t0) (incV w t0) (incW w t0) hPi hidem hrPi

/-- SUPPORT: the incidence vectors of stage t0 vanish on roles whose mask misses t0. -/
theorem support_VW (hL : LegalAt (1 : DN) iD (Dt t0) w) (r : Fin n) (hr : t0 ∉ w.mask r)
    (j : Inc w t0) : incV w t0 r j = 0 ∧ incW w t0 r j = 0 := by
  obtain ⟨-, h2, h3⟩ := biorth w t0 hb hL
  constructor
  · have := congrFun (congrFun h2 r) j
    simp [Pi0, Matrix.diagonal_mul, hr] at this
    exact this.symm
  · have := congrFun (congrFun h3 j) r
    simp [Pi0, Matrix.mul_diagonal, hr] at this
    exact this.symm

end incid

/-! ## from SPEC legality -/

theorem legal_dn {n k : ℕ} (w : CWord n k) (hL : Legal w) (t0 : Fin k) :
    LegalAt (1 : DN) iD (Dt t0) w ∧ replay (1 : ℂ) Complex.I 1 w.evs = 1 := by
  refine ⟨hL.2 DN 1 iD (Dt t0) (by norm_num) ?_, ?_⟩
  · unfold iD
    rw [sq, ← inl_mul, ← sq, Complex.I_sq]; simp
  · have h := (legal_pm w hL).1
    unfold LegalAt at h; rw [h]; unfold target; simp [one_qp]

/-- headline (D side): for every legal caller word and every stage t0, |E_t0| = #incidences, W^T V = 1, and every
    incidence vector is supported on E_t0. -/
theorem legal_masks {n k : ℕ} (w : CWord n k) (hL : Legal w) (t0 : Fin k) :
    (univ.filter fun r => t0 ∈ w.mask r).card = Fintype.card (Inc w t0) ∧
    (incW w t0)ᵀ * incV w t0 = 1 ∧
    ∀ r, t0 ∉ w.mask r → ∀ j, incV w t0 r j = 0 ∧ incW w t0 r j = 0 := by
  obtain ⟨hL', hb⟩ := legal_dn w hL t0
  exact ⟨stage_incidence w t0 hb hL', (biorth w t0 hb hL').1, fun r hr j => support_VW w t0 hb hL' r hr j⟩

/-- non-vacuity on the toy caller: stage 0 has |E_0| = 2 = #incidences (the two J contacts). -/
theorem toy_masks : (univ.filter fun r => (0 : Fin 1) ∈ toy.mask r).card = Fintype.card (Inc toy 0) ∧
    (incW toy 0)ᵀ * incV toy 0 = 1 := by
  obtain ⟨h1, h2, -⟩ := legal_masks toy toy_legal 0
  exact ⟨h1, h2⟩

theorem toy_inc_card : Fintype.card (Inc toy 0) = 2 := by
  rw [Fintype.card_subtype]; decide +kernel

end CallerWord

#print axioms CallerWord.linear_E1
#print axioms CallerWord.stage_incidence
#print axioms CallerWord.biorth
#print axioms CallerWord.legal_masks
#print axioms CallerWord.toy_masks
#print axioms CallerWord.toy_inc_card
