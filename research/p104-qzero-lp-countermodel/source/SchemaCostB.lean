/-
SchemaCostB (lane SCHEMACOST, Nov 20).  Part B: INVOICE = COST.  The event-form invoice `CallerEv.invoice` behind `cHat` / `cHatQ`
versus the repo's actual Theorem-K caller invoice (CertCallerCore header; pricing.py `caller_invoice` + #7113 IDLE_ODD; CALLERINV §1).

Repo pricing, per port of the type (CertCaller.evItem / tRaw / pRaw):
  QUERY -> P[1];  IDLE_ONE S -> P[8|S|];  IDLE_ODD S -> P[8|S|+1];  ADD/SCALE/SWAP/LAMBDA -> 0;  J -> one call, ZERO caller price
  diagonal row (ex, mask) -> T[(ex mod 2) + 8|mask|].
The J contacts are billed natively (`kappa_of_cert_dep`: L * 400 * 8^s, 400 = 96*4 + 8*2 = ports_A * 4 + ports_B * 2 on #7113).
So the caller-side per-port quantity (what `cHat`/`cHatQ` estimates) is
  repo := sum_r rank_r^s - sum_{plain events} price(e)^s - k * C * 8^s       (C = contacts per J: 2 for B, 4 for A),
and the event form is  invoice = sum_r (8 D_r + 1)^s - sum_{ALL events} (8|S_e|)^s [S_e /= {}].
Results (all kernel-only):
 * `repo_eq` : for a tight word (n + 2 = |Iota|), grammar-legal plain events:  repo = (k/104) * cHatQ + sum_plain dlt,
   dlt(IDLE_ODD S) = (8|S|)^s [S /= {}] + 1 - (8|S|+1)^s >= 0, and 0 on everything else (QUERY, IDLE_ONE, ADD, ...).
 * `repo_eq_q0` : Q = 0 (no thin plain event): repo = (k/104) * cHat EXACTLY (invoice = cost).
 * `repo_ge`, `repo_le` : cHatQ is a LOWER bound of the repo invoice, off by exactly sum dlt in [0, Q]; equality iff no IDLE_ODD has a
   nonempty stage set.  (#7113 type B has 4 IDLE_ODD with |S| = 1: a genuine, small, one-sided gap.)
 * `price_eq_item` / `rowRank_neg1` : the model prices equal CertCaller's items (evItem, rowRank) op by op.
Not derived (unchanged, outside Lean): that the repo's `cdat T - cdat P - L*(400*8^s + ...)` IS the quantity `Cert` is applied to is
UniUniversal.kappa_of_cert_dep's statement (we read it, we do not re-derive it); the Python JSON -> Nat packing is CERTKIT's.
-/
import Nov15.SchemaCostA
import Nov15.CertCallerCore

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace SchemaCost
open Finset Matrix CallerSign CallerWord CallerAsm CallerHP CallerEv

section defs
variable {n k : ℕ}

/-- the repo's plain-event grammar (no HOST outside a J record; QUERY orientation is odd). -/
def PlainOK : Ev n k → Prop
  | .host .. => False
  | .query _ _ σ => σ % 2 = 1
  | _ => True

/-- per-port repo price of a plain event (exponent applied). -/
noncomputable def price (σ : ℝ) : Ev n k → ℝ
  | .query .. => 1
  | .idle _ S q => if q % 2 = 0 then (8 * (S.card : ℝ)) ^ σ else (8 * (S.card : ℝ) + 1) ^ σ
  | _ => 0

/-- the event-form charge of an event (the summand of `CallerEv.invoice`). -/
noncomputable def mdl (σ : ℝ) : Ev n k → ℝ
  | .idle _ S _ => if S = ∅ then 0 else (8 * (S.card : ℝ)) ^ σ
  | _ => 0

/-- thin (q-odd) column of a plain event. -/
def thin : Ev n k → ℕ
  | .query _ _ q => if q % 2 = 1 then 1 else 0
  | .idle _ _ q => if q % 2 = 1 then 1 else 0
  | _ => 0

/-- the discrepancy: only an IDLE_ODD can have one. -/
noncomputable def dlt (σ : ℝ) : Ev n k → ℝ
  | .idle _ S q => if q % 2 = 0 then 0 else
      ((if S = ∅ then 0 else (8 * (S.card : ℝ)) ^ σ) + 1 - (8 * (S.card : ℝ) + 1) ^ σ)
  | _ => 0

def colCnt : Ev n k → ℕ := fun e => (univ.filter fun c : Fin 2 => (terms e c).2.2 ≠ 0).card

theorem mdl_thin_price (σ : ℝ) (hσ : σ ≠ 0) (e : Ev n k) (hp : PlainOK e) :
    mdl σ e + thin e - price σ e = dlt σ e := by
  cases e with
  | query r s q =>
    have : q % 2 = 1 := hp
    simp [mdl, thin, price, dlt, this]
  | idle r S q =>
    by_cases h : q % 2 = 0
    · by_cases hS : S = ∅
      · simp [mdl, thin, price, dlt, h, hS, Real.zero_rpow hσ]
      · simp [mdl, thin, price, dlt, h, hS]
    · simp [mdl, thin, price, dlt, h]
  | add a1 a2 a3 => simp [mdl, thin, price, dlt]
  | scale a1 a2 => simp [mdl, thin, price, dlt]
  | swap a1 a2 => simp [mdl, thin, price, dlt]
  | lam a1 a2 => simp [mdl, thin, price, dlt]
  | host a1 a2 a3 a4 => exact absurd hp (by simp [PlainOK])

theorem colCnt_eq_sum (e : Ev n k) : colCnt e = ∑ c : Fin 2, if (terms e c).2.2 ≠ 0 then 1 else 0 := by
  unfold colCnt; rw [Finset.card_filter]

theorem colCnt_eq_thin (e : Ev n k) (hp : PlainOK e) : colCnt e = thin e := by
  rw [colCnt_eq_sum]
  cases e with
  | query r s q =>
    have : q % 2 = 1 := hp
    simp [thin, terms, this, Fin.sum_univ_two]
  | idle r S q =>
    by_cases h : q % 2 = 1
    · simp [thin, terms, h, Fin.sum_univ_two]
    · simp [thin, terms, h, Fin.sum_univ_two]
  | add a1 a2 a3 => simp [thin, terms, Fin.sum_univ_two]
  | scale a1 a2 => simp [thin, terms, Fin.sum_univ_two]
  | swap a1 a2 => simp [thin, terms, Fin.sum_univ_two]
  | lam a1 a2 => simp [thin, terms, Fin.sum_univ_two]
  | host a1 a2 a3 a4 => exact absurd hp (by simp [PlainOK])

/-- subadditivity of the power: (x+1)^s <= x^s + 1 for 0 <= s <= 1. -/
theorem rpow_succ_le (x σ : ℝ) (hx : 0 ≤ x) (h0 : 0 ≤ σ) (h1 : σ ≤ 1) : (x + 1) ^ σ ≤ x ^ σ + 1 := by
  have := NNReal.rpow_add_le_add_rpow x.toNNReal 1 h0 h1
  have h2 := NNReal.coe_le_coe.mpr this
  simpa [NNReal.coe_rpow, Real.coe_toNNReal _ hx] using h2

theorem dlt_nonneg (σ : ℝ) (h0 : 0 < σ) (h1 : σ ≤ 1) (e : Ev n k) : 0 ≤ dlt σ e := by
  cases e with
  | idle r S q =>
    simp only [dlt]
    split_ifs with h hS
    · exact le_rfl
    · have := rpow_succ_le 0 σ le_rfl h0.le h1
      simp only [Real.zero_rpow h0.ne', zero_add] at this
      simp only [hS, Finset.card_empty, Nat.cast_zero, mul_zero, Real.zero_rpow h0.ne', zero_add]
      linarith
    · have := rpow_succ_le (8 * (S.card : ℝ)) σ (by positivity) h0.le h1
      linarith
  | query a1 a2 a3 => simp [dlt]
  | add a1 a2 a3 => simp [dlt]
  | scale a1 a2 => simp [dlt]
  | swap a1 a2 => simp [dlt]
  | lam a1 a2 => simp [dlt]
  | host a1 a2 a3 a4 => simp [dlt]

theorem dlt_le_thin (σ : ℝ) (h0 : 0 < σ) (h1 : σ ≤ 1) (e : Ev n k) (hp : PlainOK e) : dlt σ e ≤ (thin e : ℝ) := by
  cases e with
  | idle r S q =>
    by_cases h : q % 2 = 0
    · simp [dlt, thin, h]
    · have h' : q % 2 = 1 := by omega
      simp only [dlt, thin, h, h', if_false, if_true]
      push_cast
      split_ifs with hS
      · have : (0:ℝ) ≤ (8 * (S.card : ℝ) + 1) ^ σ := by positivity
        linarith
      · have : (8 * (S.card : ℝ)) ^ σ ≤ (8 * (S.card : ℝ) + 1) ^ σ :=
          Real.rpow_le_rpow (by positivity) (by linarith) h0.le
        linarith
  | query a1 a2 a3 => simp only [dlt]; positivity
  | add a1 a2 a3 => simp [dlt, thin]
  | scale a1 a2 => simp [dlt, thin]
  | swap a1 a2 => simp [dlt, thin]
  | lam a1 a2 => simp [dlt, thin]
  | host a1 a2 a3 a4 => exact absurd hp (by simp [PlainOK])

end defs

/-! ## sums over the block normal form -/
section sums
variable {n k : ℕ} {M : Type*} [AddCommMonoid M]

theorem blocks_sum (B : Blk n k) (φ : Ev n k → M) (m : ℕ) :
    ((blocks B.f m).map φ).sum = ∑ c ∈ range m, ((B.f c).map φ).sum := by
  induction m with
  | zero => simp [blocks]
  | succ m ih => rw [blocks_succ, List.map_append, List.sum_append, ih, Finset.sum_range_succ]

theorem evs_sum (B : Blk n k) (φ : Ev n k → M) :
    (B.evs.map φ).sum = ∑ c : Fin k, ((B.pre c).map φ).sum + ∑ c : Fin k, ((B.jx c).map φ).sum
      + (B.post.map φ).sum := by
  unfold Blk.evs
  rw [List.map_append, List.sum_append, blocks_sum, Finset.sum_range (fun c => ((B.f c).map φ).sum)]
  simp only [Blk.f_fin, List.map_append, List.sum_append, Finset.sum_add_distrib]

/-- the plain events' share of a sum. -/
def plainSum (B : Blk n k) (φ : Ev n k → M) : M := ∑ c : Fin k, ((B.pre c).map φ).sum + (B.post.map φ).sum

theorem evs_sum' (B : Blk n k) (φ : Ev n k → M) :
    (B.evs.map φ).sum = plainSum B φ + ∑ c : Fin k, ((B.jx c).map φ).sum := by
  rw [evs_sum]; unfold plainSum; abel

theorem plainSum_mono (B : Blk n k) {φ ψ : Ev n k → ℝ} (h : ∀ c, ∀ e ∈ B.pre c, φ e ≤ ψ e)
    (h' : ∀ e ∈ B.post, φ e ≤ ψ e) : plainSum B φ ≤ plainSum B ψ := by
  unfold plainSum
  have h1 : ∀ l : List (Ev n k), (∀ e ∈ l, φ e ≤ ψ e) → (l.map φ).sum ≤ (l.map ψ).sum := by
    intro l hl
    induction l with
    | nil => simp
    | cons a l ih =>
      simp only [List.map_cons, List.sum_cons]
      exact add_le_add (hl a (by simp)) (ih fun e he => hl e (by simp [he]))
  exact add_le_add (Finset.sum_le_sum fun c _ => h1 _ (h c)) (h1 _ h')

theorem plainSum_congr (B : Blk n k) {φ ψ : Ev n k → ℝ} (h : ∀ c, ∀ e ∈ B.pre c, φ e = ψ e)
    (h' : ∀ e ∈ B.post, φ e = ψ e) : plainSum B φ = plainSum B ψ := by
  apply le_antisymm
  · exact plainSum_mono B (fun c e he => (h c e he).le) (fun e he => (h' e he).le)
  · exact plainSum_mono B (fun c e he => (h c e he).ge) (fun e he => (h' e he).ge)

end sums


/-! ## invoice and column count as list sums -/
section lists
variable {n k : ℕ}

theorem invoice_list (w : CWord n k) (σ : ℝ) :
    invoice σ w.mask (evS w) = ∑ r, (8 * ((w.mask r).card : ℝ) + 1) ^ σ - (w.evs.map (mdl σ)).sum := by
  unfold invoice
  congr 1
  have h : ∀ j : Fin w.evs.length,
      (if evS w j = ∅ then (0:ℝ) else (8 * ((evS w j).card : ℝ)) ^ σ) = mdl σ (w.evs.get j) := by
    intro j
    unfold evS
    generalize w.evs.get j = e
    cases e <;> simp [mdl]
  simp_rw [h]
  rw [← Fin.sum_univ_fun_getElem]
  simp [List.get_eq_getElem]

theorem card_iota_real (w : CWord n k) :
    (Fintype.card (Iota w) : ℝ) = (w.evs.map fun e => (colCnt e : ℝ)).sum := by
  have h : Fintype.card (Iota w) = (w.evs.map colCnt).sum := by
    rw [Fintype.card_subtype, Finset.card_filter, Fintype.sum_prod_type]
    rw [← Fin.sum_univ_fun_getElem]
    refine Finset.sum_congr rfl fun j _ => ?_
    rw [colCnt_eq_sum]
    refine Finset.sum_congr rfl fun c _ => ?_
    simp only [tm, List.get_eq_getElem]
    by_cases h0 : (terms w.evs[j.1] c).2.2 = 0 <;> simp [h0]
  rw [h]
  push_cast [Nat.cast_list_sum, List.map_map]
  rfl

theorem lsum_lin (l : List (Ev n k)) (φ ψ χ : Ev n k → ℝ) :
    (l.map fun e => φ e + ψ e - χ e).sum = (l.map φ).sum + (l.map ψ).sum - (l.map χ).sum := by
  induction l with
  | nil => simp
  | cons a l ih => simp only [List.map_cons, List.sum_cons]; rw [ih]; ring

theorem plainSum_lin (B : Blk n k) (φ ψ χ : Ev n k → ℝ) :
    plainSum B (fun e => φ e + ψ e - χ e) = plainSum B φ + plainSum B ψ - plainSum B χ := by
  unfold plainSum
  simp only [lsum_lin, Finset.sum_sub_distrib, Finset.sum_add_distrib]
  ring

end lists

/-! ## the repo caller quantity and its relation to cHatQ -/
section main
open CallerBridge
variable {n k : ℕ} (B : Blk n k)

/-- the caller-side per-port quantity of the repo invoice: targets - plain-event prices - native contact charge (`Cn` per call). -/
noncomputable def repo (Cn : ℕ) : ℝ :=
  ∑ r, (((B.ex r % 2).toNat + 8 * (B.mask r).card : ℕ) : ℝ) ^ σ0 - plainSum B (price σ0) - (k : ℝ) * ((Cn : ℝ) * 8 ^ σ0)

theorem sigma_pos : (0:ℝ) < σ0 := by norm_num [σ0]
theorem sigma_le : σ0 ≤ 1 := by norm_num [σ0]

variable {B}
variable (Cn : ℕ) (hjm : ∀ c, ((B.jx c).map (mdl σ0)).sum = (Cn : ℝ) * 8 ^ σ0)
  (hjc : ∀ c, ((B.jx c).map fun e => (colCnt e : ℝ)).sum = 2)
  (hpre : ∀ c, ∀ e ∈ B.pre c, PlainOK e) (hpost : ∀ e ∈ B.post, PlainOK e)
  (hex : ∀ r, B.ex r = -1) (hk : 0 < k)
include hjm hjc hpre hpost hex hk

/-- n - (2k - 2) = number of plain thin columns, for a tight frame. -/
theorem excess_eq (hn : n + 2 = Fintype.card (Iota B.word)) :
    (n : ℝ) - (2 * k - 2) = plainSum B (fun e => (thin e : ℝ)) := by
  have h1 : (Fintype.card (Iota B.word) : ℝ) = n + 2 := by rw [← hn]; push_cast; ring
  have h2 := card_iota_real B.word
  have h3 : (B.word.evs.map fun e => (colCnt e : ℝ)).sum
      = plainSum B (fun e => (colCnt e : ℝ)) + 2 * k := by
    show (B.evs.map fun e => (colCnt e : ℝ)).sum = _
    rw [evs_sum']
    simp [hjc]
    ring
  have h4 : plainSum B (fun e => (colCnt e : ℝ)) = plainSum B (fun e => (thin e : ℝ)) :=
    plainSum_congr B (fun c e he => by rw [colCnt_eq_thin e (hpre c e he)])
      (fun e he => by rw [colCnt_eq_thin e (hpost e he)])
  linarith

theorem repo_eq (hn : n + 2 = Fintype.card (Iota B.word)) :
    repo B Cn = (k : ℝ) / 104 * cHatQ B.word + plainSum B (dlt σ0) := by
  have hinv := invoice_list B.word σ0
  have hs : (B.word.evs.map (mdl σ0)).sum = plainSum B (mdl σ0) + k * ((Cn : ℝ) * 8 ^ σ0) := by
    show (B.evs.map (mdl σ0)).sum = _
    rw [evs_sum']
    simp [hjm]
  have hex' := excess_eq Cn hjm hjc hpre hpost hex hk hn
  have hk' : (k : ℝ) ≠ 0 := by positivity
  have hc : (k : ℝ) / 104 * cHatQ B.word = invoice σ0 B.word.mask (evS B.word) - ((n : ℝ) - (2 * k - 2)) := by
    unfold cHatQ; field_simp
  have hrank : ∀ r, (((B.ex r % 2).toNat + 8 * (B.mask r).card : ℕ) : ℝ) = 8 * ((B.mask r).card : ℝ) + 1 := by
    intro r; rw [hex r]; push_cast; norm_num [Int.toNat]; ring
  have hd : plainSum B (dlt σ0) = plainSum B (fun e => mdl σ0 e + (thin e : ℝ) - price σ0 e) :=
    (plainSum_congr B (fun c e he => (mdl_thin_price σ0 sigma_pos.ne' e (hpre c e he)).symm)
      (fun e he => (mdl_thin_price σ0 sigma_pos.ne' e (hpost e he)).symm))
  rw [hd, plainSum_lin, hc, hex', hinv]
  unfold repo
  simp only [hrank]
  have : B.word.mask = B.mask := rfl
  rw [this, hs]
  ring

theorem repo_ge (hn : n + 2 = Fintype.card (Iota B.word)) :
    (k : ℝ) / 104 * cHatQ B.word ≤ repo B Cn := by
  rw [repo_eq Cn hjm hjc hpre hpost hex hk hn]
  have : 0 ≤ plainSum B (dlt σ0) := by
    have := plainSum_mono B (φ := fun _ => (0:ℝ)) (ψ := dlt σ0)
      (fun c e _ => dlt_nonneg σ0 sigma_pos sigma_le e) (fun e _ => dlt_nonneg σ0 sigma_pos sigma_le e)
    simpa [plainSum] using this
  linarith

theorem repo_le (hn : n + 2 = Fintype.card (Iota B.word)) :
    repo B Cn ≤ (k : ℝ) / 104 * cHatQ B.word + ((n : ℝ) - (2 * k - 2)) := by
  rw [repo_eq Cn hjm hjc hpre hpost hex hk hn, excess_eq Cn hjm hjc hpre hpost hex hk hn]
  have := plainSum_mono B (φ := dlt σ0) (ψ := fun e => (thin e : ℝ))
    (fun c e he => dlt_le_thin σ0 sigma_pos sigma_le e (hpre c e he))
    (fun e he => dlt_le_thin σ0 sigma_pos sigma_le e (hpost e he))
  linarith

/-- equality when no IDLE_ODD has a nonempty stage set (in particular for Q = 0 and for QUERY-only thin columns). -/
theorem repo_eq_of_empty (hn : n + 2 = Fintype.card (Iota B.word))
    (hemp : ∀ c, ∀ e ∈ B.pre c, ∀ r S q, e = Ev.idle r S q → q % 2 = 1 → S = ∅)
    (hemp' : ∀ e ∈ B.post, ∀ r S q, e = Ev.idle r S q → q % 2 = 1 → S = ∅) :
    repo B Cn = (k : ℝ) / 104 * cHatQ B.word := by
  have hz : ∀ e : Ev n k, (∀ r S q, e = Ev.idle r S q → q % 2 = 1 → S = ∅) → dlt σ0 e = 0 := by
    intro e he
    cases e with
    | idle r S q =>
      by_cases h : q % 2 = 0
      · simp [dlt, h]
      · have hS := he r S q rfl (by omega)
        simp [dlt, h, hS]
    | query a1 a2 a3 => simp [dlt]
    | add a1 a2 a3 => simp [dlt]
    | scale a1 a2 => simp [dlt]
    | swap a1 a2 => simp [dlt]
    | lam a1 a2 => simp [dlt]
    | host a1 a2 a3 a4 => simp [dlt]
  have h0 : plainSum B (dlt σ0) = 0 := by
    have := plainSum_congr B (φ := dlt σ0) (ψ := fun _ => (0:ℝ))
      (fun c e he => hz e (hemp c e he)) (fun e he => hz e (hemp' e he))
    simpa [plainSum] using this
  rw [repo_eq Cn hjm hjc hpre hpost hex hk hn, h0]; ring

/-- Q = 0: the repo invoice IS the event-form `cHat`, exactly. -/
theorem repo_eq_q0 (hn : n + 2 = Fintype.card (Iota B.word)) (hQ0 : Fintype.card (Iota B.word) = 2 * k) :
    repo B Cn = (k : ℝ) / 104 * cHat B.word := by
  have hn2 : n + 2 = 2 * k := by omega
  have hq : cHatQ B.word = cHat B.word := cHatQ_q0 hn2
  have hex' := excess_eq Cn hjm hjc hpre hpost hex hk hn
  have hz : (n : ℝ) - (2 * k - 2) = 0 := by
    have : ((n + 2 : ℕ) : ℝ) = ((2 * k : ℕ) : ℝ) := by rw [hn2]
    push_cast at this; linarith
  have h1 := repo_le Cn hjm hjc hpre hpost hex hk hn
  have h2 := repo_ge Cn hjm hjc hpre hpost hex hk hn
  rw [hq] at h1 h2
  rw [hz] at h1
  linarith

end main

end SchemaCost
