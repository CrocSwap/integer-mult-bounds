/-
CONTENT-PIN (CONTENT2OPT R1), lane LEAN-NEXT39, Nov 17. See ContentPin.md.
Reader op `r += c·h1` reads h1's whole row.  Re-reading h2 instead changes every downstream
final q by  coef_q · c · (row h2 − row h1)  (exact), where coef_q is the downstream
difference tracker of r.
-/
import Nov15.TokenCancel

set_option linter.unusedSectionVars false

namespace ContentPin
open TokenCancel

variable {K Reg C : Type*} [Field K] [DecidableEq Reg] [DecidableEq C]

/-- Difference tracker: how a row-difference sitting on registers (α q • v) propagates. -/
def dstep (α : Reg → K) : Ev K Reg C → Reg → K
  | .born i _ => Function.update α i 0
  | .init i _ => Function.update α i 0
  | .move _ _ => α
  | .add i j a _ => Function.update α i (α i + a * α j)
  | .scale i u _ => Function.update α i (u * α i)
  | .clear i _ => Function.update α i 0
  | .copy i j _ => Function.update α i (α j)

def drun : List (Ev K Reg C) → (Reg → K) → Reg → K
  | [], α => α
  | e :: es, α => drun es (dstep α e)

lemma diff_step (s1 s2 : St K Reg C) (α : Reg → K) (v : Reg → K) (e : Ev K Reg C)
    (h : ∀ q, s2.row q - s1.row q = α q • v) :
    ∀ q, (step s2 e).row q - (step s1 e).row q = dstep α e q • v := by
  intro q
  cases e with
  | born i c => by_cases hq : q = i <;> simp_all [step, dstep, Function.update_apply]
  | init i c => by_cases hq : q = i <;> simp_all [step, dstep, Function.update_apply]
  | move i c => simpa [step, dstep] using h q
  | clear i c => by_cases hq : q = i <;> simp_all [step, dstep, Function.update_apply]
  | scale i u c =>
    by_cases hq : q = i
    · subst hq; have := h q
      simp only [step, dstep, Function.update_self]
      rw [← smul_sub, this, smul_smul]
    · simpa [step, dstep, Function.update_apply, hq] using h q
  | copy i j c =>
    by_cases hq : q = i
    · subst hq; simpa [step, dstep] using h j
    · simpa [step, dstep, Function.update_apply, hq] using h q
  | add i j a c =>
    by_cases hq : q = i
    · subst hq
      simp only [step, dstep, Function.update_self]
      have h1 := h q; have h2 := h j
      calc _ = (s2.row q - s1.row q) + a • (s2.row j - s1.row j) := by
              simp only [smul_sub]; abel
        _ = _ := by rw [h1, h2, smul_smul, add_smul]
    · simpa [step, dstep, Function.update_apply, hq] using h q

theorem diff_run (tail : List (Ev K Reg C)) :
    ∀ (s1 s2 : St K Reg C) (α : Reg → K) (v : Reg → K),
    (∀ q, s2.row q - s1.row q = α q • v) →
    ∀ q, (run s2 tail).row q - (run s1 tail).row q = drun tail α q • v := by
  induction tail with
  | nil => intro s1 s2 α v h q; exact h q
  | cons e es ih => intro s1 s2 α v h q; exact ih _ _ _ _ (diff_step s1 s2 α v e h) q

/-- coefficient with which a difference sitting on register `r` reaches register `q`. -/
def coef (tail : List (Ev K Reg C)) (r q : Reg) : K := drun tail (Pi.single r 1) q

/-- Exact substitution law: reader `r += c·h1` replaced by `r += c·h2`. -/
theorem sub_delta (s : St K Reg C) (r h1 h2 : Reg) (c : K) (ch : C)
    (tail : List (Ev K Reg C)) (q : Reg) :
    (run (step s (.add r h2 c ch)) tail).row q - (run (step s (.add r h1 c ch)) tail).row q
      = coef tail r q • c • (s.row h2 - s.row h1) := by
  have := diff_run tail (step s (.add r h1 c ch)) (step s (.add r h2 c ch)) (Pi.single r 1)
    (c • (s.row h2 - s.row h1)) (by
      intro q
      by_cases hq : q = r
      · subst hq; simp [step, smul_sub]
      · simp [step, hq, Function.update_apply, Pi.single_apply]) q
  simpa [coef] using this

/-- CONTENT-PIN (iff form, mod a linear map `π`: the coordinates the downstream finals see).
Finals in `F` are unchanged under the swap iff for each q ∈ F, coef_q · c · π(row h2 − row h1)=0. -/
theorem content_pin {W : Type*} [AddCommGroup W] [Module K W] (π : (Reg → K) →ₗ[K] W)
    (s : St K Reg C) (r h1 h2 : Reg) (c : K) (ch : C) (tail : List (Ev K Reg C))
    (F : Set Reg) :
    (∀ q ∈ F, π ((run (step s (.add r h2 c ch)) tail).row q)
              = π ((run (step s (.add r h1 c ch)) tail).row q)) ↔
    ∀ q ∈ F, (coef tail r q * c) • π (s.row h2 - s.row h1) = 0 := by
  refine forall₂_congr fun q _ => ?_
  rw [← sub_eq_zero, ← map_sub, sub_delta, map_smul, map_smul, smul_smul]

/-- Whole-row version (π = id). -/
theorem content_pin_row (s : St K Reg C) (r h1 h2 : Reg) (c : K) (ch : C)
    (tail : List (Ev K Reg C)) (F : Set Reg) (hreach : ∃ q ∈ F, coef tail r q * c ≠ 0) :
    (∀ q ∈ F, (run (step s (.add r h2 c ch)) tail).row q
              = (run (step s (.add r h1 c ch)) tail).row q) ↔ s.row h2 = s.row h1 := by
  have := content_pin (LinearMap.id) s r h1 h2 c ch tail F
  simp only [LinearMap.id_apply] at this
  rw [this]
  constructor
  · obtain ⟨q, hq, hne⟩ := hreach
    intro h; have := h q hq
    rcases smul_eq_zero.mp this with h0 | h0
    · exact absurd h0 hne
    · exact (sub_eq_zero.mp h0)
  · intro h q _; simp [h]

/-- Reach hypothesis + δ ∉ ker π ⇒ some final in F changes (as seen through π). -/
theorem content_pin_changes {W : Type*} [AddCommGroup W] [Module K W] (π : (Reg → K) →ₗ[K] W)
    (s : St K Reg C) (r h1 h2 : Reg) (c : K) (ch : C) (tail : List (Ev K Reg C))
    (F : Set Reg) (hreach : ∃ q ∈ F, coef tail r q * c ≠ 0)
    (hδ : π (s.row h2 - s.row h1) ≠ 0) :
    ∃ q ∈ F, π ((run (step s (.add r h2 c ch)) tail).row q)
              ≠ π ((run (step s (.add r h1 c ch)) tail).row q) := by
  by_contra hcon
  push_neg at hcon
  have := (content_pin π s r h1 h2 c ch tail F).mp hcon
  obtain ⟨q, hq, hne⟩ := hreach
  exact hδ ((smul_eq_zero.mp (this q hq)).resolve_left hne)

/-- Token coordinate, exact: final difference at coordinate h1 is −coef·c when
row h1 h1 = 1 and row h2 h1 = 0. -/
theorem token_coord (s : St K Reg C) (r h1 h2 : Reg) (c : K) (ch : C)
    (tail : List (Ev K Reg C)) (q : Reg)
    (h1tok : s.row h1 h1 = 1) (h2tok : s.row h2 h1 = 0) :
    (run (step s (.add r h2 c ch)) tail).row q h1 - (run (step s (.add r h1 c ch)) tail).row q h1
      = -(coef tail r q * c) := by
  have := congrArg (fun f => f h1) (sub_delta s r h1 h2 c ch tail q)
  simp only [Pi.sub_apply, Pi.smul_apply, smul_eq_mul, h1tok, h2tok] at this
  rw [this]; ring

/-- COROLLARY (fresh tokens): if h1 carries its own token (row h1 h1 = 1), h2 has not read
it (row h2 h1 = 0), and the reader's row reaches a final q ∈ F non-trivially
(coef·c ≠ 0), then the swap changes that final, already in the coordinate h1. -/
theorem no_reassign (s : St K Reg C) (r h1 h2 : Reg) (c : K) (ch : C)
    (tail : List (Ev K Reg C)) (F : Set Reg) (hreach : ∃ q ∈ F, coef tail r q * c ≠ 0)
    (h1tok : s.row h1 h1 = 1) (h2tok : s.row h2 h1 = 0) :
    ∃ q ∈ F, (run (step s (.add r h2 c ch)) tail).row q
              ≠ (run (step s (.add r h1 c ch)) tail).row q := by
  obtain ⟨q, hq, hne⟩ := hreach
  refine ⟨q, hq, fun h => hne ?_⟩
  have := token_coord s r h1 h2 c ch tail q h1tok h2tok
  rw [h, sub_self] at this
  exact neg_eq_zero.mp this.symm

/-- Born helpers are fresh: after born h1; born h2 (h1 ≠ h2), tokens are as required. -/
theorem fresh_born (s : St K Reg C) (h1 h2 : Reg) (hne : h1 ≠ h2) (c1 c2 : C) :
    (run s [.born h1 c1, .born h2 c2]).row h1 h1 = 1 ∧
    (run s [.born h1 c1, .born h2 c2]).row h2 h1 = 0 := by
  simp [run, step, hne, hne.symm, Pi.single_apply]

/-! Scope checks (ℚ, Reg = Fin 3, h1 = 0, h2 = 1, r = 2). -/

/-- Without the reach hypothesis the conclusion fails: reader cleared right after. -/
theorem dead_reader_preserves :
    let s : St ℚ (Fin 3) Unit := ⟨fun i => Pi.single i 1, fun _ => some ()⟩
    s.row 1 ≠ s.row 0 ∧
    ∀ q ∈ ({2} : Set (Fin 3)),
      (run (step s (.add 2 1 1 ())) [.clear 2 ()]).row q
        = (run (step s (.add 2 0 1 ())) [.clear 2 ()]).row q := by
  intro s
  refine ⟨?_, ?_⟩
  · intro h; have := congrFun h 0; simp [s] at this
  · intro q hq; simp at hq; subst hq; simp [run, step, s]

/-- Distinct birth tokens do not suffice: a COPY makes the rows equal, so the swap is harmless.
The extra hypothesis row h2 h1 = 0 (h2 never read h1's token) is needed. -/
theorem copy_equalises :
    let s : St ℚ (Fin 3) Unit := ⟨fun _ => 0, fun _ => none⟩
    let t := run s [.born 0 (), .born 1 (), .copy 1 0 ()]
    t.row 1 = t.row 0 := by
  intro s t
  simp [t, run, step, s]

end ContentPin

#print axioms ContentPin.diff_run
#print axioms ContentPin.sub_delta
#print axioms ContentPin.content_pin
#print axioms ContentPin.content_pin_row
#print axioms ContentPin.content_pin_changes
#print axioms ContentPin.token_coord
#print axioms ContentPin.no_reassign
#print axioms ContentPin.fresh_born
#print axioms ContentPin.dead_reader_preserves
#print axioms ContentPin.copy_equalises
