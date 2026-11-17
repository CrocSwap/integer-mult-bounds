/-
Spread (lane LEAN-NEXT24, Nov 17): the subscription / spread identity. See Spread.md.
Source: cards/WILD/JUNKHYGIENE/R1.md §2.

Model: a holder z = z̃ + λ·r with r = h's row (all in a K-module M). Events on (z̃, λ, r):
* `other c`: an op among non-h registers: z̃ += c (λ, r unchanged);
* `read c` : z += c·r (a read of h): z̃ unchanged, λ += c;
* `hrow y` : h's row changes r += y; the register z itself is NOT touched, so z̃ -= λ·y.
`inv_run`: z = z̃ + λ r is preserved. `spread_identity`: over a window with NO h-reads (λ constant),
the e_h channel content z̃ − (z̃_0 + Σ c) equals −λ·(r_end − r_0): z's net change through e_h is
−λ·Δ(h's row). `spread_neutral`: if h's row is the same at both ends, the spread is content-neutral.
Scoping note (`varying_lambda_counterexample`): if an h-read inside the window changes λ, the
formula with a single λ is FALSE; "z̃ untouched by h-reads" must mean λ constant over the window.
-/
import Mathlib.Algebra.Module.Basic
import Mathlib.Tactic.Module
import Mathlib.Tactic.Abel
import Mathlib.Tactic.LinearCombination

namespace Spread
variable {K M : Type*} [Field K] [AddCommGroup M] [Module K M]

inductive Ev (K M : Type*)
  | other (c : M)
  | read (c : K)
  | hrow (y : M)

structure St (K M : Type*) where
  zt : M
  lam : K
  r : M

def step : St K M → Ev K M → St K M
  | s, .other c => { s with zt := s.zt + c }
  | s, .read c => { s with lam := s.lam + c }
  | s, .hrow y => { s with zt := s.zt - s.lam • y, r := s.r + y }

def run : St K M → List (Ev K M) → St K M
  | s, [] => s
  | s, e :: es => run (step s e) es

/-- the actual register content. -/
def val (s : St K M) : M := s.zt + s.lam • s.r

/-- the actual register changes only by `other c` (+c), `read c` (+c·r); an h-row change leaves it fixed. -/
theorem val_step (s : St K M) (e : Ev K M) :
    val (step s e) = val s + (match e with
      | .other c => c
      | .read c => c • s.r
      | .hrow _ => 0) := by
  cases e <;> simp [step, val, add_smul, smul_sub] <;> abel

def Reads : Ev K M → Prop
  | .read _ => True
  | _ => False

def sumOther : List (Ev K M) → M
  | [] => 0
  | .other c :: es => c + sumOther es
  | _ :: es => sumOther es

theorem lam_run (s : St K M) (es : List (Ev K M)) (h : ∀ e ∈ es, ¬ Reads e) :
    (run s es).lam = s.lam := by
  induction es generalizing s with
  | nil => rfl
  | cons e es ih =>
    have he : ¬ Reads e := h e List.mem_cons_self
    have : (step s e).lam = s.lam := by cases e <;> simp_all [step, Reads]
    simp only [run]; rw [ih _ (fun x hx => h x (List.mem_cons_of_mem _ hx)), this]

/-- **spread identity**: with no h-reads in the window, the e_h channel
`z̃_end − z̃_0 − Σ other` equals −λ·(r_end − r_0). -/
theorem spread_identity (s : St K M) (es : List (Ev K M)) (h : ∀ e ∈ es, ¬ Reads e) :
    (run s es).zt - s.zt - sumOther es = -(s.lam • ((run s es).r - s.r)) := by
  induction es generalizing s with
  | nil => simp [run, sumOther]
  | cons e es ih =>
    have h' : ∀ x ∈ es, ¬ Reads x := fun x hx => h x (List.mem_cons_of_mem _ hx)
    have he : ¬ Reads e := h e List.mem_cons_self
    have ih' := ih (step s e) h'
    have hl : (step s e).lam = s.lam := by cases e <;> simp_all [step, Reads]
    rw [hl] at ih'
    simp only [run]
    cases e with
    | other c =>
      simp only [step, sumOther] at ih' ⊢
      linear_combination (norm := module) ih'
    | read c => exact absurd trivial he
    | hrow y =>
      simp only [step, sumOther] at ih' ⊢
      linear_combination (norm := module) ih'

/-- a spread over a window where h's row is the same at both ends is content-neutral. -/
theorem spread_neutral (s : St K M) (es : List (Ev K M)) (h : ∀ e ∈ es, ¬ Reads e)
    (hr : (run s es).r = s.r) :
    (run s es).zt = s.zt + sumOther es := by
  have := spread_identity s es h
  rw [hr] at this; simp at this
  have h2 : (run s es).zt - s.zt - sumOther es = 0 := this
  rw [sub_sub, sub_eq_zero] at h2; rw [h2, add_comm]

/-- with no h-row change events at all, the holder only gets its `other` content. -/
theorem no_hrow_neutral (s : St K M) (es : List (Ev K M)) (h : ∀ e ∈ es, ¬ Reads e)
    (hn : ∀ e ∈ es, ∀ y, e ≠ Ev.hrow y) : (run s es).zt = s.zt + sumOther es := by
  apply spread_neutral s es h
  induction es generalizing s with
  | nil => rfl
  | cons e es ih =>
    have he := h e List.mem_cons_self
    have hne := hn e List.mem_cons_self
    have : (step s e).r = s.r := by
      cases e with
      | other c => rfl
      | read c => exact absurd trivial he
      | hrow y => exact absurd rfl (hne y)
    simp only [run]
    rw [ih _ (fun x hx => h x (List.mem_cons_of_mem _ hx)) (fun x hx => hn x (List.mem_cons_of_mem _ hx)), this]

/-- scoping counterexample: if an h-read changes λ inside the window, the single-λ formula fails
(neither λ_0 = 0 nor λ_end = 1 gives the true channel −1). -/
theorem varying_lambda_counterexample :
    let s : St ℚ ℚ := ⟨0, 0, 0⟩
    let es : List (Ev ℚ ℚ) := [.hrow 1, .read 1, .hrow 1]
    (run s es).zt - s.zt - sumOther es = -1 ∧
    -(s.lam • ((run s es).r - s.r)) = 0 ∧
    -((run s es).lam • ((run s es).r - s.r)) = -2 := by
  norm_num [run, step, sumOther]

end Spread
