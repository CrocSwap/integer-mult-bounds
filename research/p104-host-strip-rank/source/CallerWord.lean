/-
CallerWord (lane CALLERWORD, Nov 20).  The SPEC-level multi-call CALLER word in Lean, and its bridge to the
CallerSGram stage model.

Source (data, not run): the caller replay `caller(C)` of research/shared-wire-split-composition/independent.py
(+ the #7113 signed edit `IDLE_ODD` = `pscale(row, q = e[4], m = D^S)`, 7113_signed_model.py), and the
`validate` clauses of the mixed-root-caller/1 operator_ring.py (distinct HOST fields).  A caller acts on ROWS
R[r] (one per role r), entries in Q(i)[q, D_1..D_k]/(q^4 - 1); it starts at R[r] = e_r and must end at the
DIAGONAL target R[r] = q^(ex r) * prod_{t in mask r} D_t * e_r  (`expected`: key (r, dg[0] % 4, mask)).
Ops (one register type; a J record is macro-expanded, see `jA` / `jB`):
  ADD r s c    R[r] += c R[s]               SCALE r c   R[r] *= c          SWAP r s
  QUERY r s σ  R[r] += q^σ R[s]             LAMBDA r σ  R[r] = (1+σi)/2 R[r] + (1-σi)/2 q^2 R[r]
  IDLE r S σ   R[r] *= q^σ prod_{t∈S} D_t   (IDLE_ONE: σ = 0, IDLE_ODD: σ = e[4])
  HOST s t a b (s ≠ t, simultaneous)  R[s] = R[s] + a q R[t],  R[t] = b q^-1 R[s] + (1+ab) R[t]
A J event at stage t is  HOST blocks of the record, then IDLE x {t} 0 on every touched register (code order).
The verifier's check is an exact polynomial identity; `Legal` below quantifies it over EVERY commutative
ℚ-algebra S with q^4 = 1 and i^2 = -1 (equivalent: the formal ring is one such S; every such S receives an
evaluation homomorphism from it).

Bridge (all kernel-checked):
* `stage_product` : Legal  ==>  over ℂ, with V_j := P(j+1)^-1 X_j P(j)  (P = replay prefix at q = 1, D = 1;
   X_j = event j at q = -1)  each V_j = I + A Pi_j B^T  with explicit columns, and
   V_{N-1} ... V_0 = diag((-1)^(ex r))   (= -I when every target exponent is odd: the #7113 family).
   Columns = the NONZERO "q-odd terms": a HOST with a ≠ 0 / b ≠ 0 gives one column each, a QUERY / IDLE with
   odd σ gives one (thin) column; ADD/SCALE/SWAP/LAMBDA/IDLE_ONE give none.
* `role_count`    : all ex odd ==>  n ≤ #columns  (= 2k + Q for 2 nonzero HOST coefficients per stage and Q thin
   odd events), and rank K + n ≤ #columns (sgForward) with rank G = n.
* `role_count_lam`: if some 2x2 principal minor of K is nonzero (λ ≠ -1 at one stage) then n + 2 ≤ #columns.
* `toy_*`         : non-vacuity, a 2-role 1-stage legal caller (HOST + QUERY + 2 IDLE_ODD).
Kernel only: no sorry, no native_decide, no new axioms.
-/
import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.LinearAlgebra.Matrix.NonsingularInverse
import Mathlib.Algebra.Algebra.Rat
import Mathlib.Data.Complex.Basic
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Ring
import Nov15.CallerSGram

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace CallerWord
open Matrix Finset CallerSign

/-! ## The caller word -/

/-- primitive caller events on one register type (roles `Fin n`, stages `Fin k`). -/
inductive Ev (n k : ℕ) where
  | add (r s : Fin n) (c : ℚ)
  | scale (r : Fin n) (c : ℚ)
  | swap (r s : Fin n)
  | query (r s : Fin n) (σ : ℤ)
  | lam (r : Fin n) (σ : ℤ)
  | idle (r : Fin n) (S : Finset (Fin k)) (σ : ℤ)
  | host (s t : Fin n) (a b : ℚ)

/-- a caller word: event list + diagonal target (q-exponent `ex r` = dg[0], D-mask `mask r` = dg[2:]). -/
structure CWord (n k : ℕ) where
  evs : List (Ev n k)
  ex : Fin n → ℤ
  mask : Fin n → Finset (Fin k)

/-- J record of type A (`[x, y, u, v]`, HOST2 coefficient α2) at stage t, macro-expanded in code order. -/
def jA {n k : ℕ} (t : Fin k) (x y u v : Fin n) (α2 : ℚ) : List (Ev n k) :=
  [.host x y 0 1, .host u v α2 0, .idle x {t} 0, .idle y {t} 0, .idle u {t} 0, .idle v {t} 0]
/-- J record of type B (`[s, t', a, b]`) at stage t. -/
def jB {n k : ℕ} (t : Fin k) (s t' : Fin n) (a b : ℚ) : List (Ev n k) :=
  [.host s t' a b, .idle s {t} 0, .idle t' {t} 0]

/-- verifier well-formedness used here: HOST fields distinct (operator_ring `joint distinct fields`). -/
def WF {n k : ℕ} (w : CWord n k) : Prop := ∀ e ∈ w.evs, ∀ s t a b, e = Ev.host s t a b → s ≠ t

section sem
variable {S : Type*} [CommRing S] [Algebra ℚ S] {n k : ℕ}

/-- single-entry matrix. -/
def E1 (r s : Fin n) (c : S) : Matrix (Fin n) (Fin n) S := Matrix.of fun x y => if x = r ∧ y = s then c else 0

/-- q^σ in Q[q]/(q^4-1) (exponent key `% 4`). -/
def qp (q : S) (σ : ℤ) : S := q ^ (σ % 4).toNat

/-- the event as a row operation: new rows = evMat * old rows. -/
def evMat (q i : S) (D : Fin k → S) : Ev n k → Matrix (Fin n) (Fin n) S
  | .add r s c => 1 + E1 r s (algebraMap ℚ S c)
  | .scale r c => 1 + E1 r r (algebraMap ℚ S c - 1)
  | .swap r s => Matrix.of fun x y => if y = Equiv.swap r s x then 1 else 0
  | .query r s σ => 1 + E1 r s (qp q σ)
  | .lam r σ => 1 + E1 r r (algebraMap ℚ S (1/2) * (1 + (σ : S) * i)
      + algebraMap ℚ S (1/2) * (1 - (σ : S) * i) * q ^ 2 - 1)
  | .idle r T σ => 1 + E1 r r (qp q σ * ∏ t ∈ T, D t - 1)
  | .host s t a b => 1 + E1 s t (algebraMap ℚ S a * q) + E1 t s (algebraMap ℚ S b * q ^ 3)
      + E1 t t (algebraMap ℚ S (a * b))

/-- prefix product: the first m events, latest on the left. -/
def pre (q i : S) (D : Fin k → S) (l : List (Ev n k)) (m : ℕ) : Matrix (Fin n) (Fin n) S :=
  ((l.take m).map (evMat q i D)).reverse.prod

/-- the replay (all events). -/
def replay (q i : S) (D : Fin k → S) (l : List (Ev n k)) : Matrix (Fin n) (Fin n) S := pre q i D l l.length

/-- the diagonal target. -/
def target (q : S) (D : Fin k → S) (w : CWord n k) : Matrix (Fin n) (Fin n) S :=
  Matrix.diagonal fun r => qp q (w.ex r) * ∏ t ∈ w.mask r, D t

def LegalAt (q i : S) (D : Fin k → S) (w : CWord n k) : Prop := replay q i D w.evs = target q D w

theorem pre_succ (q i : S) (D : Fin k → S) (l : List (Ev n k)) (m : ℕ) :
    pre q i D l (m + 1) = ((l[m]?).map (evMat q i D)).getD 1 * pre q i D l m := by
  unfold pre
  rw [List.take_add_one]
  cases h : l[m]? with
  | none => simp
  | some e => simp

end sem

/-- SPEC legality: well-formed, and the exact endpoint identity under every evaluation. -/
def Legal {n k : ℕ} (w : CWord n k) : Prop :=
  WF w ∧ ∀ (S : Type) [CommRing S] [Algebra ℚ S] (q i : S) (D : Fin k → S),
    q ^ 4 = 1 → i ^ 2 = -1 → LegalAt q i D w

/-! ## q-odd terms of an event (the columns) -/

/-- slot c of event e: (row index, column index, coefficient); `evMat(-1) - evMat(1) = Σ_c E1 x y coef`. -/
def terms {n k : ℕ} : Ev n k → Fin 2 → Fin n × Fin n × ℚ
  | .add r _ _ => fun _ => (r, r, 0)
  | .scale r _ => fun _ => (r, r, 0)
  | .swap r _ => fun _ => (r, r, 0)
  | .query r s σ => ![(r, s, if σ % 2 = 1 then -2 else 0), (r, s, 0)]
  | .lam r _ => fun _ => (r, r, 0)
  | .idle r _ σ => ![(r, r, if σ % 2 = 1 then -2 else 0), (r, r, 0)]
  | .host s t a b => ![(s, t, -2 * a), (t, s, -2 * b)]

section delta
variable {K : Type*} [Field K] [CharZero K] {n k : ℕ}

theorem E1_sub (x y : Fin n) (c d : K) : E1 x y c - E1 x y d = E1 x y (c - d) := by
  ext a b; simp only [E1, Matrix.sub_apply, Matrix.of_apply]; split_ifs <;> simp

theorem E1_zero (x y : Fin n) : E1 x y (0 : K) = 0 := by
  ext a b; simp [E1]

theorem neg_one_qp (σ : ℤ) : qp (-1 : K) σ = if σ % 2 = 1 then -1 else 1 := by
  unfold qp
  have key : (σ % 4).toNat % 2 = if σ % 2 = 1 then 1 else 0 := by split_ifs <;> omega
  rcases Nat.even_or_odd (σ % 4).toNat with h | h
  · have h2 : (σ % 4).toNat % 2 = 0 := Nat.even_iff.mp h
    rw [h.neg_one_pow]; split_ifs with h3 <;> simp_all
  · have h2 : (σ % 4).toNat % 2 = 1 := Nat.odd_iff.mp h
    rw [h.neg_one_pow]; split_ifs with h3 <;> simp_all

theorem one_qp (σ : ℤ) : qp (1 : K) σ = 1 := by simp [qp]

theorem sum_terms (x : Fin 2 → Fin n × Fin n × ℚ) :
    ∑ c : Fin 2, E1 (x c).1 (x c).2.1 (algebraMap ℚ K (x c).2.2)
      = E1 (x 0).1 (x 0).2.1 (algebraMap ℚ K (x 0).2.2) + E1 (x 1).1 (x 1).2.1 (algebraMap ℚ K (x 1).2.2) :=
  Fin.sum_univ_two _

/-- the per-event q-jump at D = 1:  evMat(-1) - evMat(1) = Σ_c E1 x_c y_c coef_c. -/
theorem delta_eq (i : K) (e : Ev n k) :
    evMat (-1 : K) i 1 e - evMat (1 : K) i 1 e
      = ∑ c : Fin 2, E1 (terms e c).1 (terms e c).2.1 (algebraMap ℚ K (terms e c).2.2) := by
  rw [sum_terms]
  cases e with
  | add r s c => simp [evMat, terms, E1_zero]
  | scale r c => simp [evMat, terms, E1_zero]
  | swap r s => simp [evMat, terms, E1_zero]
  | query r s σ =>
    simp only [evMat, terms, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons,
      add_sub_add_left_eq_sub, E1_sub, neg_one_qp, one_qp, map_zero, E1_zero, add_zero]
    congr 1; split_ifs <;> simp; norm_num
  | lam r σ =>
    simp [evMat, terms, E1_zero]
  | idle r T σ =>
    simp only [evMat, terms, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons,
      add_sub_add_left_eq_sub, E1_sub, neg_one_qp, one_qp, map_zero, E1_zero, add_zero,
      Pi.one_apply, Finset.prod_const_one, mul_one]
    congr 1; split_ifs <;> simp; norm_num
  | host s t a b =>
    simp only [evMat, terms, Matrix.cons_val_zero, Matrix.cons_val_one]
    have e1 : ∀ X Y Z W Z' : Matrix (Fin n) (Fin n) K,
        (1 + X + Y + Z) - (1 + W + Z' + Z) = (X - W) + (Y - Z') := by intros; abel
    rw [e1, E1_sub, E1_sub,
      show algebraMap ℚ K a * -1 - algebraMap ℚ K a * 1 = algebraMap ℚ K (-2 * a) by simp; ring,
      show algebraMap ℚ K b * (-1) ^ 3 - algebraMap ℚ K b * 1 ^ 3 = algebraMap ℚ K (-2 * b) by simp; ring]

end delta

/-! ## the stage product -/

section stage
variable {K : Type*} [Field K] [CharZero K] {n k : ℕ} (w : CWord n k) (i : K)

/-- prefix at q = 1, D = 1 (the base point) and at q = -1, D = 1. -/
noncomputable def P1 (m : ℕ) : Matrix (Fin n) (Fin n) K := pre (1 : K) i 1 w.evs m
noncomputable def Pm (m : ℕ) : Matrix (Fin n) (Fin n) K := pre (-1 : K) i 1 w.evs m

/-- slot data of column p = (event index, slot). -/
def tm (p : Fin w.evs.length × Fin 2) : Fin n × Fin n × ℚ := terms (w.evs.get p.1) p.2

/-- the columns: nonzero q-odd slots. -/
abbrev Iota := {p : Fin w.evs.length × Fin 2 // (tm w p).2.2 ≠ 0}

/-- column (j,c) of A: coef_c * P1(j+1)^-1 e_{x_c}. -/
noncomputable def Aw : Matrix (Fin n) (Iota w) K :=
  Matrix.of fun r p => (P1 w i (p.1.1.val + 1))⁻¹ r (tm w p.1).1 * algebraMap ℚ K (tm w p.1).2.2
/-- column (j,c) of B: P1(j)^T e_{y_c}. -/
noncomputable def Bw : Matrix (Fin n) (Iota w) K :=
  Matrix.of fun r p => P1 w i p.1.1.val (tm w p.1).2.1 r
/-- block = event index. -/
def βw : Iota w → ℕ := fun p => p.1.1.val

theorem evAt_get (q : K) (D : Fin k → K) (m : ℕ) (h : m < w.evs.length) :
    ((w.evs[m]?).map (evMat q i D)).getD 1 = evMat q i D (w.evs.get ⟨m, h⟩) := by
  rw [List.getElem?_eq_getElem h]; rfl

/-- entry of a sandwiched single-entry matrix. -/
theorem sandwich (X Y : Matrix (Fin n) (Fin n) K) (x y : Fin n) (c : K) (r r' : Fin n) :
    (X * E1 x y c * Y) r r' = X r x * c * Y y r' := by
  simp only [Matrix.mul_apply, E1, Matrix.of_apply]
  rw [Finset.sum_eq_single y]
  · rw [Finset.sum_eq_single x]
    · simp
    · intro b _ hb; simp [hb]
    · simp
  · intro b _ hb; simp [hb]
  · simp

theorem diag_sandwich {ι : Type*} [Fintype ι] [DecidableEq ι] (A B : Matrix (Fin n) ι K) (d : ι → K)
    (r r' : Fin n) : (A * Matrix.diagonal d * Bᵀ) r r' = ∑ p, A r p * d p * B r' p := by
  simp only [Matrix.mul_apply, Matrix.transpose_apply, Matrix.diagonal_apply, mul_ite, mul_zero,
    Finset.sum_ite_eq', Finset.mem_univ, if_true]

theorem stage_term (m : ℕ) (hm : m < w.evs.length) :
    Aw w i * blkPi (βw w) m * (Bw w i)ᵀ
      = (P1 w i (m + 1))⁻¹ * (evMat (-1 : K) i 1 (w.evs.get ⟨m, hm⟩) - evMat (1 : K) i 1 (w.evs.get ⟨m, hm⟩))
          * P1 w i m := by
  classical
  rw [delta_eq, Matrix.mul_sum, Matrix.sum_mul]
  ext r r'
  rw [Matrix.sum_apply]
  simp only [sandwich]
  unfold blkPi
  rw [diag_sandwich]
  set g : Fin w.evs.length × Fin 2 → K := fun p =>
    (P1 w i (p.1.val + 1))⁻¹ r (tm w p).1 * algebraMap ℚ K (tm w p).2.2 *
      (if p.1.val = m then 1 else 0) * P1 w i p.1.val (tm w p).2.1 r' with hg
  have hsub : ∑ p : Iota w, g p.1 = ∑ p, g p := by
    rw [← Finset.sum_subtype (univ.filter fun p => (tm w p).2.2 ≠ 0) (by simp) g]
    rw [Finset.sum_filter_of_ne]
    intro p _ hp h0
    apply hp; simp [hg, h0]
  calc _ = ∑ p : Iota w, g p.1 := rfl
    _ = ∑ p, g p := hsub
    _ = _ := by
      rw [Fintype.sum_prod_type]
      rw [Finset.sum_eq_single (⟨m, hm⟩ : Fin w.evs.length)]
      · refine Finset.sum_congr rfl ?_
        intro c _
        simp [hg, tm]
      · intro j _ hj
        have : j.val ≠ m := fun h => hj (Fin.ext h)
        simp [hg, this]
      · simp

/-- the base prefix is invertible at every m ≤ N when the base replay is the identity. -/
theorem det_P1_ne (h1 : replay (1 : K) i 1 w.evs = 1) (m : ℕ) (hm : m ≤ w.evs.length) :
    (P1 w i m).det ≠ 0 := by
  suffices H : ∀ j m, w.evs.length - m = j → m ≤ w.evs.length → (P1 w i m).det ≠ 0 from H _ m rfl hm
  intro j
  induction j with
  | zero =>
    intro m hj hm
    have : m = w.evs.length := by omega
    subst this
    have : P1 w i w.evs.length = 1 := h1
    rw [this, det_one]; exact one_ne_zero
  | succ j ih =>
    intro m hj hm
    have hlt : m < w.evs.length := by omega
    have := ih (m + 1) (by omega) (by omega)
    unfold P1 at this ⊢
    rw [pre_succ, evAt_get w i 1 1 m hlt, det_mul] at this
    exact right_ne_zero_of_mul this

/-- telescoping: sgProd at m = P1(m)^-1 Pm(m). -/
theorem sg_tele (h1 : replay (1 : K) i 1 w.evs = 1) (m : ℕ) (hm : m ≤ w.evs.length) :
    sgProd (Aw w i) (Bw w i) (βw w) m = (P1 w i m)⁻¹ * Pm w i m := by
  induction m with
  | zero =>
    simp [sgProd, P1, Pm, pre]
  | succ m ih =>
    have hlt : m < w.evs.length := by omega
    rw [sgProd, ih (by omega), sgStage, stage_term w i m hlt]
    have hu0 : IsUnit (P1 w i m).det := isUnit_iff_ne_zero.mpr (det_P1_ne w i h1 m (by omega))
    have hu1 : IsUnit (P1 w i (m + 1)).det := isUnit_iff_ne_zero.mpr (det_P1_ne w i h1 (m + 1) (by omega))
    set Y := evMat (1 : K) i 1 (w.evs.get ⟨m, hlt⟩)
    set X := evMat (-1 : K) i 1 (w.evs.get ⟨m, hlt⟩)
    have hP1 : P1 w i (m + 1) = Y * P1 w i m := by
      unfold P1; rw [pre_succ, evAt_get w i 1 1 m hlt]
    have hPm : Pm w i (m + 1) = X * Pm w i m := by
      unfold Pm; rw [pre_succ, evAt_get w i (-1) 1 m hlt]
    have hY : (P1 w i (m + 1))⁻¹ * Y = (P1 w i m)⁻¹ := by
      have e : (P1 w i (m + 1))⁻¹ * Y * P1 w i m = 1 := by
        rw [Matrix.mul_assoc, ← hP1, nonsing_inv_mul _ hu1]
      calc (P1 w i (m + 1))⁻¹ * Y = (P1 w i (m + 1))⁻¹ * Y * P1 w i m * (P1 w i m)⁻¹ := by
            rw [Matrix.mul_assoc _ (P1 w i m), mul_nonsing_inv _ hu0, Matrix.mul_one]
        _ = (P1 w i m)⁻¹ := by rw [e, Matrix.one_mul]
    rw [hPm, Matrix.add_mul, Matrix.one_mul, Matrix.mul_sub, Matrix.sub_mul, Matrix.sub_mul,
      hY, Matrix.mul_assoc _ (P1 w i m), ← Matrix.mul_assoc (P1 w i m), mul_nonsing_inv _ hu0,
      Matrix.one_mul, Matrix.mul_assoc _ (P1 w i m), ← Matrix.mul_assoc (P1 w i m),
      mul_nonsing_inv _ hu0, Matrix.one_mul, Matrix.mul_assoc]
    abel

/-- the per-type sign matrix diag((-1)^(ex r)). -/
noncomputable def sgn : Matrix (Fin n) (Fin n) K := Matrix.diagonal fun r => qp (-1 : K) (w.ex r)

/-- STAGE PRODUCT.  Legal at q = ±1, D = 1  ==>  the q-odd stage updates multiply to diag((-1)^(ex r)). -/
theorem stage_product (h1 : LegalAt (1 : K) i 1 w) (hm1 : LegalAt (-1 : K) i 1 w) :
    sgProd (Aw w i) (Bw w i) (βw w) w.evs.length = sgn w := by
  have hb : replay (1 : K) i 1 w.evs = 1 := by
    rw [h1]; unfold target; simp [one_qp]
  rw [sg_tele w i hb _ le_rfl]
  have : P1 w i w.evs.length = 1 := hb
  rw [this, inv_one, Matrix.one_mul]
  show replay (-1 : K) i 1 w.evs = _
  rw [hm1]; unfold target sgn; simp

theorem sgn_odd (hodd : ∀ r, w.ex r % 2 = 1) : sgn w = (-1 : Matrix (Fin n) (Fin n) K) := by
  ext r r'
  by_cases h : r = r'
  · subst h; simp [sgn, neg_one_qp, hodd r]
  · simp [sgn, h]

theorem beta_lt : ∀ p, βw w p < w.evs.length := fun p => p.1.1.isLt

/-- ROLE COUNT.  odd targets  ==>  rank K + n ≤ #columns and rank G = n (sgForward). -/
theorem role_count (h1 : LegalAt (1 : K) i 1 w) (hm1 : LegalAt (-1 : K) i 1 w) (hodd : ∀ r, w.ex r % 2 = 1) :
    (sgK (βw w) (sgG (Aw w i) (Bw w i))).rank + n ≤ Fintype.card (Iota w) ∧
      (sgG (Aw w i) (Bw w i)).rank = n := by
  have hP := stage_product w i h1 hm1
  rw [sgn_odd w hodd] at hP
  exact sgForward _ _ _ _ two_ne_zero (beta_lt w) hP

/-- λ ≠ -1 at one stage (some 2x2 principal minor of K nonzero)  ==>  n + 2 ≤ #columns. -/
theorem role_count_lam (h1 : LegalAt (1 : K) i 1 w) (hm1 : LegalAt (-1 : K) i 1 w)
    (hodd : ∀ r, w.ex r % 2 = 1) (f : Fin 2 → Iota w)
    (hK : ((sgK (βw w) (sgG (Aw w i) (Bw w i))).submatrix f f).det ≠ 0) :
    n + 2 ≤ Fintype.card (Iota w) := by
  have h := (role_count w i h1 hm1 hodd).1
  have h2 : ((sgK (βw w) (sgG (Aw w i) (Bw w i))).submatrix f f).rank = 2 := by
    rw [Matrix.rank_of_isUnit _ ((Matrix.isUnit_iff_isUnit_det _).mpr (isUnit_iff_ne_zero.mpr hK))]
    simp
  have h3 := Matrix.rank_submatrix_le (sgK (βw w) (sgG (Aw w i) (Bw w i))) f f
  omega

end stage

/-! ## from SPEC legality (over ℂ) -/

theorem legal_pm {n k : ℕ} (w : CWord n k) (hL : Legal w) :
    LegalAt (1 : ℂ) Complex.I 1 w ∧ LegalAt (-1 : ℂ) Complex.I 1 w :=
  ⟨hL.2 ℂ 1 Complex.I 1 (by norm_num) Complex.I_sq,
   hL.2 ℂ (-1) Complex.I 1 (by norm_num) Complex.I_sq⟩

/-- headline: every legal caller word with odd targets is a CallerSGram P = -1 frame (over ℂ),
    with rank K + n ≤ #q-odd columns and rank G = n. -/
theorem legal_frame {n k : ℕ} (w : CWord n k) (hL : Legal w) (hodd : ∀ r, w.ex r % 2 = 1) :
    sgProd (Aw w Complex.I) (Bw w Complex.I) (βw w) w.evs.length = -1 ∧
    (sgK (βw w) (sgG (Aw w Complex.I) (Bw w Complex.I))).rank + n ≤ Fintype.card (Iota w) ∧
    (sgG (Aw w Complex.I) (Bw w Complex.I)).rank = n := by
  obtain ⟨h1, hm1⟩ := legal_pm w hL
  refine ⟨?_, role_count w _ h1 hm1 hodd⟩
  rw [stage_product w _ h1 hm1, sgn_odd w hodd]

/-! ## non-vacuity: a 2-role, 1-stage legal caller -/

/-- HOST(0,1,0,1) at stage 0 (J record of type A with only the live block), undo the q-part of role 1 with
    SCALE / QUERY / SCALE, then IDLE_ODD(-1) on both roles. Target q^-1 D_0 on both roles. -/
def toy : CWord 2 1 where
  evs := [.host 0 1 0 1, .idle 0 {0} 0, .idle 1 {0} 0, .scale 1 (-1), .query 1 0 (-1), .scale 1 (-1),
          .idle 0 ∅ (-1), .idle 1 ∅ (-1)]
  ex := fun _ => -1
  mask := fun _ => {0}

theorem toy_legal : Legal toy := by
  refine ⟨?_, ?_⟩
  · intro e he s t a b h
    subst h
    simp [toy] at he
    rcases he with ⟨rfl, rfl, -, -⟩
    decide
  · intro S _ _ q i D hq hi
    unfold LegalAt replay pre target toy
    ext r r'
    fin_cases r <;> fin_cases r' <;>
      simp [evMat, E1, qp, Matrix.mul_apply, Fin.sum_univ_two, Matrix.diagonal] <;> ring

theorem toy_card : Fintype.card (Iota toy) = 4 := by
  rw [Fintype.card_subtype]
  decide +kernel

theorem toy_nonvac :
    sgProd (Aw toy Complex.I) (Bw toy Complex.I) (βw toy) toy.evs.length = -1 ∧
    (sgK (βw toy) (sgG (Aw toy Complex.I) (Bw toy Complex.I))).rank + 2 ≤ 4 ∧
    (sgG (Aw toy Complex.I) (Bw toy Complex.I)).rank = 2 := by
  have h := legal_frame toy toy_legal (fun r => by show (-1 : ℤ) % 2 = 1; decide)
  rw [toy_card] at h
  exact h

end CallerWord

#print axioms CallerWord.stage_product
#print axioms CallerWord.role_count
#print axioms CallerWord.role_count_lam
#print axioms CallerWord.legal_frame
#print axioms CallerWord.toy_nonvac
