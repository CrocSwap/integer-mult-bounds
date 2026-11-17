/-
CORE r13/r14 PURE-HOLDER RULE (ℓ/μ charge certificate), lane LEAN-NEXT22, Nov 16.
Source: REBUILDKIT/v11/r13/MESH13.md §3,§5 and r14/MESH14.md §1,§4. See TCCharge.md.

Model: the TokenCancel op model (rows in initial-row coordinates, columns = `Reg`).
`vec μ s r = row_r · μ` is the μ-charge of register r; `lin`/`konst` split a step on charges
into its linear part and the (birth) constant.
-/
import Nov15.TokenCancel
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Data.Rat.Defs
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith

set_option linter.unusedSectionVars false

namespace TCCharge
open TokenCancel

section General
variable {K Reg C : Type*} [Field K] [DecidableEq Reg] [DecidableEq C] [Fintype Reg]

/-- The μ-charge of every register. -/
def vec (μ : Reg → K) (s : St K Reg C) : Reg → K := fun r => ∑ c, s.row r c * μ c

def lin : Ev K Reg C → (Reg → K) → (Reg → K)
  | .born i _, w => Function.update w i 0
  | .init i _, w => Function.update w i 0
  | .move _ _, w => w
  | .add i j a _, w => Function.update w i (w i + a * w j)
  | .scale i u _, w => Function.update w i (u * w i)
  | .clear i _, w => Function.update w i 0
  | .copy i j _, w => Function.update w i (w j)

def konst (μ : Reg → K) : Ev K Reg C → (Reg → K)
  | .born i _ => Pi.single i (μ i)
  | _ => 0

def vstep (μ : Reg → K) (e : Ev K Reg C) (w : Reg → K) : Reg → K := lin e w + konst μ e

def vrun (μ : Reg → K) : List (Ev K Reg C) → (Reg → K) → (Reg → K)
  | [], w => w
  | e :: es, w => vrun μ es (vstep μ e w)

def linRun : List (Ev K Reg C) → (Reg → K) → (Reg → K)
  | [], w => w
  | e :: es, w => linRun es (lin e w)

theorem lin_add (e : Ev K Reg C) (w x : Reg → K) : lin e (w + x) = lin e w + lin e x := by
  funext r
  cases e <;> simp only [lin, Function.update_apply, Pi.add_apply] <;> (try split_ifs) <;>
    (try simp) <;> (try ring)

theorem lin_smul (e : Ev K Reg C) (a : K) (w : Reg → K) : lin e (a • w) = a • lin e w := by
  funext r
  cases e <;> simp only [lin, Function.update_apply, Pi.smul_apply, smul_eq_mul] <;>
    (try split_ifs) <;> (try simp) <;> (try ring)

theorem linRun_add : ∀ (l : List (Ev K Reg C)) (w x : Reg → K),
    linRun l (w + x) = linRun l w + linRun l x
  | [], w, x => rfl
  | e :: es, w, x => by simp [linRun, lin_add, linRun_add es]

theorem linRun_smul : ∀ (l : List (Ev K Reg C)) (a : K) (w : Reg → K),
    linRun l (a • w) = a • linRun l w
  | [], a, w => rfl
  | e :: es, a, w => by simp [linRun, lin_smul, linRun_smul es]

theorem vrun_add : ∀ (μ : Reg → K) (l : List (Ev K Reg C)) (w x : Reg → K),
    vrun μ l (w + x) = vrun μ l w + linRun l x
  | μ, [], w, x => rfl
  | μ, e :: es, w, x => by
    have : vstep μ e (w + x) = vstep μ e w + lin e x := by
      simp only [vstep, lin_add]; abel
    simp [vrun, linRun, this, vrun_add μ es]

theorem vec_step (μ : Reg → K) (s : St K Reg C) (e : Ev K Reg C) :
    vec μ (step s e) = vstep μ e (vec μ s) := by
  funext r
  cases e with
  | born i c =>
    by_cases hr : r = i
    · subst hr; simp [vec, step, vstep, lin, konst, Pi.single_apply, Finset.sum_apply]
    · simp [vec, step, vstep, lin, konst, Function.update_of_ne hr, Pi.single_apply, hr]
  | init i c =>
    by_cases hr : r = i
    · subst hr; simp [vec, step, vstep, lin, konst]
    · simp [vec, step, vstep, lin, konst, Function.update_of_ne hr]
  | move i c => simp [vec, step, vstep, lin, konst]
  | add i j a c =>
    by_cases hr : r = i
    · subst hr
      simp [vec, step, vstep, lin, konst, add_mul, mul_assoc, Finset.sum_add_distrib,
        Finset.mul_sum]
    · simp [vec, step, vstep, lin, konst, Function.update_of_ne hr]
  | scale i u c =>
    by_cases hr : r = i
    · subst hr; simp [vec, step, vstep, lin, konst, mul_assoc, Finset.mul_sum]
    · simp [vec, step, vstep, lin, konst, Function.update_of_ne hr]
  | clear i c =>
    by_cases hr : r = i
    · subst hr; simp [vec, step, vstep, lin, konst]
    · simp [vec, step, vstep, lin, konst, Function.update_of_ne hr]
  | copy i j c =>
    by_cases hr : r = i
    · subst hr; simp [vec, step, vstep, lin, konst]
    · simp [vec, step, vstep, lin, konst, Function.update_of_ne hr]

theorem vec_run (μ : Reg → K) : ∀ (l : List (Ev K Reg C)) (s : St K Reg C),
    vec μ (run s l) = vrun μ l (vec μ s)
  | [], s => rfl
  | e :: es, s => by simp [run, vrun, vec_run μ es, vec_step]

theorem run_append' (s : St K Reg C) (l1 l2 : List (Ev K Reg C)) :
    run s (l1 ++ l2) = run (run s l1) l2 := by
  induction l1 generalizing s with
  | nil => rfl
  | cons e es ih => simp [run, ih]

theorem vec_single (c : Reg) (s : St K Reg C) (r : Reg) :
    vec (Pi.single c (1 : K)) s r = s.row r c := by
  simp [vec, Pi.single_apply]

/-- **Single-insertion identity (exact).** Inserting `u += d·s'` between `l1` and `l2` changes the
μ-charges of the final registers by `d · (X_{s'}(t)·μ) · resp`, where `resp = linRun l2 e_u` is
the response of the later program to a unit at `u` and `X_{s'}(t)` is the row of `s'` at the
insertion time. -/
theorem insertion_charge (μ : Reg → K) (s0 : St K Reg C) (l1 l2 : List (Ev K Reg C))
    (u s' : Reg) (d : K) (c : C) :
    vec μ (run s0 (l1 ++ Ev.add u s' d c :: l2)) =
      vec μ (run s0 (l1 ++ l2)) +
        (d * vec μ (run s0 l1) s') • linRun l2 (Pi.single u 1) := by
  rw [run_append', run_append', vec_run μ (Ev.add u s' d c :: l2) (run s0 l1),
    vec_run μ l2 (run s0 l1)]
  have h1 : vec μ (step (run s0 l1) (Ev.add u s' d c)) =
      vec μ (run s0 l1) + (d * vec μ (run s0 l1) s') • (Pi.single u 1 : Reg → K) := by
    rw [vec_step]; funext r
    by_cases hr : r = u
    · subst hr; simp [vstep, lin, konst, Function.update_apply, Pi.single_apply]
    · simp [vstep, lin, konst, Function.update_apply, Pi.single_apply, hr]
  show vrun μ l2 (vstep μ (Ev.add u s' d c) (vec μ (run s0 l1))) = _
  rw [← vec_step μ (run s0 l1) (Ev.add u s' d c), h1, vrun_add, linRun_smul]

/-- **Row-level single-insertion identity (exact).** Column `c` of every final row moves by
`d · X_{s'}(t)[c] · resp`. -/
theorem insertion_rows (s0 : St K Reg C) (l1 l2 : List (Ev K Reg C))
    (u s' : Reg) (d : K) (c0 : C) (r col : Reg) :
    (run s0 (l1 ++ Ev.add u s' d c0 :: l2)).row r col =
      (run s0 (l1 ++ l2)).row r col +
        d * (run s0 l1).row s' col * linRun l2 (Pi.single u 1) r := by
  have := congrFun (insertion_charge (Pi.single col (1 : K)) s0 l1 l2 u s' d c0) r
  simpa [vec_single] using this

/-- **Charge theorem (ℓ/μ certificate), exact for a single insertion.** Let `Δ_h` be the change of
ℓ's reading `Σ_r ℓ_r · row_r[h]` of column `h`, assuming the insertion changes no other column
`(Δ_c = 0, c ≠ h)`. Then `Δ_h · μ_h = d · λ · (X_{s'}(t)·μ)`, `λ = ℓ · resp`. In particular if
`μ_h = 1` and either `λ = 0` (source/receiver not ℓ-live) or `μ ⊥ X_{s'}(t)`, then `Δ_h = 0`:
ℓ's reading of column `h` is unchanged. -/
theorem charge_single (ℓ μ : Reg → K) (h : Reg) (s0 : St K Reg C) (l1 l2 : List (Ev K Reg C))
    (u s' : Reg) (d : K) (c0 : C)
    (hconf : ∀ r col, col ≠ h →
      (run s0 (l1 ++ Ev.add u s' d c0 :: l2)).row r col = (run s0 (l1 ++ l2)).row r col) :
    (∑ r, ℓ r * ((run s0 (l1 ++ Ev.add u s' d c0 :: l2)).row r h -
        (run s0 (l1 ++ l2)).row r h)) * μ h =
      d * (∑ r, ℓ r * linRun l2 (Pi.single u 1) r) * (∑ c, (run s0 l1).row s' c * μ c) := by
  have key : ∀ r, (∑ c, (run s0 (l1 ++ Ev.add u s' d c0 :: l2)).row r c * μ c) -
      (∑ c, (run s0 (l1 ++ l2)).row r c * μ c) =
      ((run s0 (l1 ++ Ev.add u s' d c0 :: l2)).row r h - (run s0 (l1 ++ l2)).row r h) * μ h := by
    intro r
    rw [← Finset.sum_sub_distrib]
    rw [Finset.sum_eq_single h]
    · ring
    · intro col _ hcol
      rw [hconf r col hcol]; ring
    · simp
  have hcharge : ∀ r, ((∑ c, (run s0 (l1 ++ Ev.add u s' d c0 :: l2)).row r c * μ c) -
      (∑ c, (run s0 (l1 ++ l2)).row r c * μ c)) =
      (d * (∑ c, (run s0 l1).row s' c * μ c)) * linRun l2 (Pi.single u 1) r := by
    intro r
    have := congrFun (insertion_charge μ s0 l1 l2 u s' d c0) r
    simp only [vec, Pi.add_apply, Pi.smul_apply, smul_eq_mul] at this
    rw [this]; ring
  calc (∑ r, ℓ r * ((run s0 (l1 ++ Ev.add u s' d c0 :: l2)).row r h -
        (run s0 (l1 ++ l2)).row r h)) * μ h
      = ∑ r, ℓ r * (((run s0 (l1 ++ Ev.add u s' d c0 :: l2)).row r h -
        (run s0 (l1 ++ l2)).row r h) * μ h) := by rw [Finset.sum_mul]; congr 1; ext r; ring
    _ = ∑ r, ℓ r * ((d * (∑ c, (run s0 l1).row s' c * μ c)) * linRun l2 (Pi.single u 1) r) := by
        congr 1; ext r; rw [← key r, hcharge r]
    _ = _ := by
        generalize (∑ c, (run s0 l1).row s' c * μ c) = A
        calc ∑ r, ℓ r * ((d * A) * linRun l2 (Pi.single u 1) r)
            = (d * A) * ∑ r, ℓ r * linRun l2 (Pi.single u 1) r := by
              rw [Finset.mul_sum]; congr 1; ext r; ring
          _ = _ := by ring

/-- **Pure-holder rule.** If `μ_h = 1` and an insertion changes ℓ's reading of column `h` (only
column `h` moves), then `λ ≠ 0` (the receiver is ℓ-live) and `X_{s'}(t)·μ ≠ 0` (the source is not
μ-orthogonal). In particular when `μ` is orthogonal to every state co-present with an ℓ-live
receiver, no insertable op changes ℓ's reading of column `h`. -/
theorem pure_holder_rule (ℓ μ : Reg → K) (h : Reg) (hμ : μ h = 1) (s0 : St K Reg C)
    (l1 l2 : List (Ev K Reg C)) (u s' : Reg) (d : K) (c0 : C)
    (hconf : ∀ r col, col ≠ h →
      (run s0 (l1 ++ Ev.add u s' d c0 :: l2)).row r col = (run s0 (l1 ++ l2)).row r col)
    (hchange : (∑ r, ℓ r * (run s0 (l1 ++ Ev.add u s' d c0 :: l2)).row r h) ≠
      ∑ r, ℓ r * (run s0 (l1 ++ l2)).row r h) :
    (∑ r, ℓ r * linRun l2 (Pi.single u 1) r) ≠ 0 ∧ (∑ c, (run s0 l1).row s' c * μ c) ≠ 0 := by
  have := charge_single ℓ μ h s0 l1 l2 u s' d c0 hconf
  rw [hμ, mul_one] at this
  have hne : (∑ r, ℓ r * ((run s0 (l1 ++ Ev.add u s' d c0 :: l2)).row r h -
        (run s0 (l1 ++ l2)).row r h)) ≠ 0 := by
    intro h0
    apply hchange
    have : ∑ r, ℓ r * ((run s0 (l1 ++ Ev.add u s' d c0 :: l2)).row r h -
        (run s0 (l1 ++ l2)).row r h) =
        (∑ r, ℓ r * (run s0 (l1 ++ Ev.add u s' d c0 :: l2)).row r h) -
        ∑ r, ℓ r * (run s0 (l1 ++ l2)).row r h := by
      rw [← Finset.sum_sub_distrib]; congr 1; ext r; ring
    rw [this] at h0; exact sub_eq_zero.1 h0
  rw [this] at hne
  refine ⟨fun h0 => hne ?_, fun h0 => hne ?_⟩ <;> simp [h0]



/-- An event is μ-neutral at `s` if it leaves every register's μ-charge unchanged. -/
def Neutral (μ : Reg → K) (s : St K Reg C) (e : Ev K Reg C) : Prop :=
  vec μ (step s e) = vec μ s

theorem neutral_add (μ : Reg → K) (s : St K Reg C) (i j : Reg) (a : K) (c : C)
    (h : vec μ s j = 0) : Neutral μ s (Ev.add i j a c) := by
  unfold Neutral; rw [vec_step]; funext r
  by_cases hr : r = i
  · subst hr; simp [vstep, lin, konst, h]
  · simp [vstep, lin, konst, hr]

theorem neutral_scale (μ : Reg → K) (s : St K Reg C) (i : Reg) (u : K) (c : C)
    (h : vec μ s i = 0) : Neutral μ s (Ev.scale i u c) := by
  unfold Neutral; rw [vec_step]; funext r
  by_cases hr : r = i
  · subst hr; simp [vstep, lin, konst, h]
  · simp [vstep, lin, konst, hr]

/-- `l'` is `l` with extra events inserted, each μ-neutral at the moment (in the MODIFIED run). -/
inductive InsAt (μ : Reg → K) : St K Reg C → List (Ev K Reg C) → List (Ev K Reg C) → Prop
  | nil (s : St K Reg C) : InsAt μ s [] []
  | keep (s : St K Reg C) (e : Ev K Reg C) (l l' : List (Ev K Reg C)) :
      InsAt μ (step s e) l l' → InsAt μ s (e :: l) (e :: l')
  | ins (s : St K Reg C) (e : Ev K Reg C) (l l' : List (Ev K Reg C)) :
      Neutral μ s e → InsAt μ (step s e) l l' → InsAt μ s l (e :: l')

/-- **Charge invariance under ANY number of insertions** whose sources are μ-neutral at their
moment (strong hypothesis, checked on the modified run): the μ-charge of every register is
unchanged. -/
theorem ins_invariant (μ : Reg → K) {s' : St K Reg C} {l l' : List (Ev K Reg C)}
    (H : InsAt μ s' l l') : ∀ s : St K Reg C, vec μ s = vec μ s' →
    vec μ (run s l) = vec μ (run s' l') := by
  induction H with
  | nil s' => intro s hs; exact hs
  | keep s' e l l' _ ih =>
    intro s hs
    exact ih _ (by rw [vec_step, vec_step, hs])
  | ins s' e l l' hn _ ih =>
    intro s hs
    exact ih s (hs.trans hn.symm)

/-- **Pinned column.** With `μ_h = 1`, if the modified run differs from the base run only in
column `h` (on every register), it does not differ at all. -/
theorem column_pinned (μ : Reg → K) (h : Reg) (hμ : μ h = 1) {s' : St K Reg C}
    {l l' : List (Ev K Reg C)} (H : InsAt μ s' l l') (s : St K Reg C) (hs : vec μ s = vec μ s')
    (hconf : ∀ r col, col ≠ h → (run s' l').row r col = (run s l).row r col) (r : Reg) :
    (run s' l').row r h = (run s l).row r h := by
  have hv := congrFun (ins_invariant μ H s hs) r
  simp only [vec] at hv
  have e1 := Finset.add_sum_erase Finset.univ (fun c => (run s' l').row r c * μ c)
    (Finset.mem_univ h)
  have e2 := Finset.add_sum_erase Finset.univ (fun c => (run s l).row r c * μ c)
    (Finset.mem_univ h)
  have hs2 : ∑ c ∈ Finset.univ.erase h, (run s' l').row r c * μ c =
      ∑ c ∈ Finset.univ.erase h, (run s l).row r c * μ c :=
    Finset.sum_congr rfl (fun c hc => by rw [hconf r c (Finset.ne_of_mem_erase hc)])
  simp only [hμ, mul_one] at e1 e2
  have := hv.symm
  rw [← e1, ← e2, hs2] at this
  exact add_right_cancel this

end General

/-! ### Counterexample: the weak (ℓ-live-only) orthogonality does NOT survive two insertions.

Registers `0 = g` (INIT zero at chart A), `1 = h` (born at A, pure `e_h`), `2 = u2` (born at B);
`g` moves A → B in the base program. Base rows: `row u2 = e_2`. `μ = e_1` (μ_h = 1), `ℓ = e_2`.
* ins1 = `g += h` at A: `g` is not ℓ-live (nothing reads `g` later), so the single insertion is
  harmless (λ = 0), although `h` is a pure holder.
* ins2 = `u2 += g` at B: `u2` IS ℓ-live but `g` is μ-orthogonal in the base program (row 0).
Each alone leaves column `h` of `u2` at 0. Together `u2` gets `e_h`: column-`h`-confined change. -/
section Counter

def evsBase : List (Ev ℚ (Fin 3) Bool) :=
  [Ev.init 0 false, Ev.born 1 false, Ev.born 2 true, Ev.move 0 true]
def evsOne : List (Ev ℚ (Fin 3) Bool) :=
  [Ev.init 0 false, Ev.born 1 false, Ev.add 0 1 1 false, Ev.born 2 true, Ev.move 0 true]
def evsTwo : List (Ev ℚ (Fin 3) Bool) :=
  [Ev.init 0 false, Ev.born 1 false, Ev.born 2 true, Ev.move 0 true, Ev.add 2 0 1 true]
def evsBoth : List (Ev ℚ (Fin 3) Bool) :=
  [Ev.init 0 false, Ev.born 1 false, Ev.add 0 1 1 false, Ev.born 2 true, Ev.move 0 true,
    Ev.add 2 0 1 true]

def muH : Fin 3 → ℚ := Pi.single 1 1

theorem ce_base : (run start evsBase).row 2 1 = 0 := by
  simp [evsBase, run, step, start, Function.update_apply, Pi.single_apply]
theorem ce_one : (run start evsOne).row 2 1 = 0 := by
  simp [evsOne, run, step, start, Function.update_apply, Pi.single_apply]
theorem ce_two : (run start evsTwo).row 2 1 = 0 := by
  simp [evsTwo, run, step, start, Function.update_apply, Pi.single_apply]
theorem ce_both : (run start evsBoth).row 2 1 = 1 := by
  simp [evsBoth, run, step, start, Function.update_apply, Pi.single_apply]

/-- Every other column of every register is the same in the combined run and the base run, so the
combined change is confined to column `h = 1` (and it is nonzero: `ce_both`, `ce_base`). -/
theorem ce_confined : ∀ r col : Fin 3, col ≠ 1 →
    (run start evsBoth).row r col = (run start evsBase).row r col := by
  intro r col hc
  fin_cases r <;> fin_cases col <;>
    simp_all [evsBoth, evsBase, run, step, start, Function.update_apply, Pi.single_apply]

/-- The weak certificate holds for each single insertion (exact formula: λ = 0 for ins1,
`μ ⊥ X_g` in the base program for ins2), yet the pair changes ℓ's reading of column `h`. -/
theorem ce_weak_hyp :
    (∑ r : Fin 3, (Pi.single 2 1 : Fin 3 → ℚ) r *
        linRun [Ev.born 2 true, Ev.move 0 true] (Pi.single (0 : Fin 3) (1 : ℚ)) r) = 0 ∧
    (∑ c : Fin 3, (run start evsBase).row 0 c * muH c) = 0 := by
  constructor
  · simp [Fin.sum_univ_three, linRun, lin, Function.update_apply, Pi.single_apply]
  · simp [Fin.sum_univ_three, muH, evsBase, run, step, start, Function.update_apply, Pi.single_apply]

end Counter

end TCCharge

#print axioms TCCharge.insertion_rows
#print axioms TCCharge.charge_single
#print axioms TCCharge.pure_holder_rule
#print axioms TCCharge.ins_invariant
#print axioms TCCharge.column_pinned
#print axioms TCCharge.ce_both
#print axioms TCCharge.ce_confined
#print axioms TCCharge.ce_weak_hyp
