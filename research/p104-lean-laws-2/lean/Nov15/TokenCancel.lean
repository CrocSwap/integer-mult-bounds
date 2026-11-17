/-
BIG-TOKENCANCEL T1 (hub blindness) and T2 (difference lemma), lane LEAN-NEXT6, Nov 16.
Source: cards/WILD/BIG/TOKENCANCEL/THEORY.md. See TokenCancel.md.

Op model: registers `Reg`, charts `C` with two hubs `z` (= {0}) and `V`; rows in initial-row
coordinates `Reg → K`. Events carry their chart. Legal = co-presence plus the two [C] facts of
T1(a)/(b): no MOVE enters z and no MOVE leaves V.
-/
import Mathlib.LinearAlgebra.Span.Basic
import Mathlib.LinearAlgebra.Pi
import Mathlib.Tactic.Abel
import Mathlib.Algebra.BigOperators.Fin

set_option linter.unusedSectionVars false

namespace TokenCancel

inductive Ev (K Reg C : Type*)
  | born (i : Reg) (c : C)
  | init (i : Reg) (c : C)
  | move (i : Reg) (c : C)
  | add (i j : Reg) (a : K) (c : C)
  | scale (i : Reg) (u : K) (c : C)
  | clear (i : Reg) (c : C)
  | copy (i j : Reg) (c : C)

structure St (K Reg C : Type*) where
  row : Reg → Reg → K
  loc : Reg → Option C

variable {K Reg C : Type*} [Field K] [DecidableEq Reg] [DecidableEq C]

def step (s : St K Reg C) : Ev K Reg C → St K Reg C
  | .born i c => ⟨Function.update s.row i (Pi.single i 1), Function.update s.loc i (some c)⟩
  | .init i c => ⟨Function.update s.row i 0, Function.update s.loc i (some c)⟩
  | .move i c => ⟨s.row, Function.update s.loc i (some c)⟩
  | .add i j a _ => ⟨Function.update s.row i (s.row i + a • s.row j), s.loc⟩
  | .scale i u _ => ⟨Function.update s.row i (u • s.row i), s.loc⟩
  | .clear i _ => ⟨Function.update s.row i 0, s.loc⟩
  | .copy i j _ => ⟨Function.update s.row i (s.row j), s.loc⟩

def run (s : St K Reg C) : List (Ev K Reg C) → St K Reg C
  | [] => s
  | e :: es => run (step s e) es

variable (z V : C)

/-- Legality: co-presence at the event's chart; births/INITs of absent registers;
MOVEs never enter `z` and never leave `V` (T1(a), T1(b), checked [C] on #7623). -/
def LegalEv (s : St K Reg C) : Ev K Reg C → Prop
  | .born i _ => s.loc i = none
  | .init i _ => s.loc i = none
  | .move i c => ∃ c0, s.loc i = some c0 ∧ c0 ≠ V ∧ c ≠ z
  | .add i j _ c => i ≠ j ∧ s.loc i = some c ∧ s.loc j = some c
  | .scale i _ c => s.loc i = some c
  | .clear i c => s.loc i = some c
  | .copy i j c => s.loc i = some c ∧ s.loc j = some c

def Legal : St K Reg C → List (Ev K Reg C) → Prop
  | _, [] => True
  | s, e :: es => LegalEv z V s e ∧ Legal (step s e) es

/-- An op (not a birth/INIT/MOVE) at a hub. -/
def hubOp : Ev K Reg C → Prop
  | .add _ _ _ c | .scale _ _ c | .clear _ c | .copy _ _ c => c = z ∨ c = V
  | _ => False

instance (e : Ev K Reg C) : Decidable (hubOp z V e) := by
  cases e <;> simp only [hubOp] <;> infer_instance

variable (h : Reg)

/-- The interior coefficient program: tracks the e_h-coefficient, ignoring every hub op. -/
def sig (σ : Reg → K) : Ev K Reg C → Reg → K
  | .born i _ => Function.update σ i (if i = h then 1 else 0)
  | .init i _ => Function.update σ i 0
  | .move _ _ => σ
  | .add i j a c => if c = z ∨ c = V then σ else Function.update σ i (σ i + a * σ j)
  | .scale i u c => if c = z ∨ c = V then σ else Function.update σ i (u * σ i)
  | .clear i c => if c = z ∨ c = V then σ else Function.update σ i 0
  | .copy i j c => if c = z ∨ c = V then σ else Function.update σ i (σ j)

def sigRun (σ : Reg → K) : List (Ev K Reg C) → Reg → K
  | [] => σ
  | e :: es => sigRun (sig z V h σ e) es

/-- The program is blind to hub ops: it equals the program run on the interior subsequence. -/
theorem sigRun_filter (σ : Reg → K) (evs : List (Ev K Reg C)) :
    sigRun z V h σ evs = sigRun z V h σ (evs.filter fun e => ¬ hubOp z V e) := by
  induction evs generalizing σ with
  | nil => rfl
  | cons e es ih =>
    by_cases he : hubOp z V e
    · have : sig z V h σ e = σ := by
        cases e <;> simp_all [hubOp, sig]
      simp [sigRun, he, this, ih]
    · simp [sigRun, he, ih]

/-- Invariant: rows not at V carry the program's e_h-coefficient; rows at z carry 0. -/
def Inv (s : St K Reg C) (σ : Reg → K) : Prop :=
  (∀ r, s.loc r ≠ some V → s.row r h = σ r) ∧ (∀ r, s.loc r = some z → s.row r h = 0)

lemma inv_update (s : St K Reg C) (σ σ' : Reg → K) (i : Reg) (nr : Reg → K)
    (hI : Inv z V h s σ) (hσ : ∀ r, r ≠ i → σ' r = σ r)
    (hnew : s.loc i ≠ some V → nr h = σ' i) (hz : s.loc i = some z → nr h = 0) :
    Inv z V h ⟨Function.update s.row i nr, s.loc⟩ σ' := by
  refine ⟨fun r hr => ?_, fun r hr => ?_⟩
  · by_cases hri : r = i
    · subst hri; simpa using hnew hr
    · simp only [Function.update_of_ne hri]; rw [hσ r hri]; exact hI.1 r hr
  · by_cases hri : r = i
    · subst hri; simpa using hz hr
    · simp only [Function.update_of_ne hri]; exact hI.2 r hr

theorem inv_step (s : St K Reg C) (σ : Reg → K) (e : Ev K Reg C)
    (hI : Inv z V h s σ) (hL : LegalEv z V s e) (hb : ∀ c, e = .born h c → c ≠ z) :
    Inv z V h (step s e) (sig z V h σ e) := by
  have hI1 := hI.1
  have hI2 := hI.2
  -- coefficient of a register present at chart c
  have atz : ∀ i c, s.loc i = some c → c = z → s.row i h = 0 := fun i c hi hc =>
    hI2 i (hc ▸ hi)
  have notV : ∀ i c, s.loc i = some c → c ≠ V → s.row i h = σ i := fun i c hi hc =>
    hI1 i (by rw [hi]; simpa using hc)
  cases e with
  | born i c =>
    refine ⟨fun r _ => ?_, fun r hr => ?_⟩
    · by_cases hri : r = i
      · subst hri; simp [step, sig, Pi.single_apply, eq_comm]
      · simp only [step, sig, Function.update_of_ne hri] at *
        exact hI1 r (by simpa [step, Function.update_of_ne hri] using ‹_›)
    · by_cases hri : r = i
      · subst hri
        simp only [step, Function.update_self, Option.some.injEq] at hr
        have : r ≠ h := fun hrh => hb c (by rw [hrh]) hr
        simp [step, this.symm]
      · simp only [step, Function.update_of_ne hri] at hr ⊢; exact hI2 r hr
  | init i c =>
    refine ⟨fun r hr => ?_, fun r hr => ?_⟩
    · by_cases hri : r = i
      · subst hri; simp [step, sig]
      · simp only [step, sig, Function.update_of_ne hri] at hr ⊢; exact hI1 r hr
    · by_cases hri : r = i
      · subst hri; simp [step]
      · simp only [step, Function.update_of_ne hri] at hr ⊢; exact hI2 r hr
  | move i c =>
    obtain ⟨c0, hc0, hc0V, hcz⟩ := hL
    refine ⟨fun r hr => ?_, fun r hr => ?_⟩
    · by_cases hri : r = i
      · subst hri; exact hI1 r (by rw [hc0]; simpa using hc0V)
      · simp only [step, sig, Function.update_of_ne hri] at hr ⊢; exact hI1 r hr
    · by_cases hri : r = i
      · subst hri; simp [step] at hr; exact absurd hr hcz
      · simp only [step, Function.update_of_ne hri] at hr ⊢; exact hI2 r hr
  | add i j a c =>
    obtain ⟨hij, hi, hj⟩ := hL
    by_cases hc : c = z ∨ c = V
    · have hs : sig z V h σ (.add i j a c) = σ := by simp [sig, hc]
      rw [hs]
      apply inv_update z V h s σ σ i _ hI (fun _ _ => rfl)
      · intro hiV
        have hcV : c ≠ V := fun h' => hiV (h' ▸ hi)
        have hcz : c = z := hc.resolve_right hcV
        simp [atz i c hi hcz, atz j c hj hcz, ← notV i c hi hcV]
      · intro hiz
        have hcz : c = z := by rw [hi] at hiz; exact Option.some.inj hiz
        simp [atz i c hi hcz, atz j c hj hcz]
    · push Not at hc
      have hs : sig z V h σ (.add i j a c) = Function.update σ i (σ i + a * σ j) := by
        simp [sig, hc]
      rw [hs]
      apply inv_update z V h s σ _ i _ hI (fun r hr => Function.update_of_ne hr _ _)
      · intro _; simp [notV i c hi hc.2, notV j c hj hc.2]
      · intro hiz; rw [hi] at hiz; exact absurd (Option.some.inj hiz) hc.1
  | scale i u c =>
    have hi : s.loc i = some c := hL
    by_cases hc : c = z ∨ c = V
    · have hs : sig z V h σ (.scale i u c) = σ := by simp [sig, hc]
      rw [hs]
      apply inv_update z V h s σ σ i _ hI (fun _ _ => rfl)
      · intro hiV
        have hcV : c ≠ V := fun h' => hiV (h' ▸ hi)
        have hcz : c = z := hc.resolve_right hcV
        simp [atz i c hi hcz, ← notV i c hi hcV]
      · intro hiz
        have hcz : c = z := by rw [hi] at hiz; exact Option.some.inj hiz
        simp [atz i c hi hcz]
    · push Not at hc
      have hs : sig z V h σ (.scale i u c) = Function.update σ i (u * σ i) := by
        simp [sig, hc]
      rw [hs]
      apply inv_update z V h s σ _ i _ hI (fun r hr => Function.update_of_ne hr _ _)
      · intro _; simp [notV i c hi hc.2]
      · intro hiz; rw [hi] at hiz; exact absurd (Option.some.inj hiz) hc.1
  | clear i c =>
    have hi : s.loc i = some c := hL
    by_cases hc : c = z ∨ c = V
    · have hs : sig z V h σ (.clear i c) = σ := by simp [sig, hc]
      rw [hs]
      apply inv_update z V h s σ σ i _ hI (fun _ _ => rfl)
      · intro hiV
        have hcV : c ≠ V := fun h' => hiV (h' ▸ hi)
        have hcz : c = z := hc.resolve_right hcV
        simp [← notV i c hi hcV, atz i c hi hcz]
      · intro _; simp
    · push Not at hc
      have hs : sig z V h σ (.clear i c) = Function.update σ i 0 := by simp [sig, hc]
      rw [hs]
      apply inv_update z V h s σ _ i _ hI (fun r hr => Function.update_of_ne hr _ _)
      · intro _; simp
      · intro _; simp
  | copy i j c =>
    obtain ⟨hi, hj⟩ := hL
    by_cases hc : c = z ∨ c = V
    · have hs : sig z V h σ (.copy i j c) = σ := by simp [sig, hc]
      rw [hs]
      apply inv_update z V h s σ σ i _ hI (fun _ _ => rfl)
      · intro hiV
        have hcV : c ≠ V := fun h' => hiV (h' ▸ hi)
        have hcz : c = z := hc.resolve_right hcV
        simp [atz j c hj hcz, ← notV i c hi hcV, atz i c hi hcz]
      · intro hiz
        have hcz : c = z := by rw [hi] at hiz; exact Option.some.inj hiz
        simp [atz j c hj hcz]
    · push Not at hc
      have hs : sig z V h σ (.copy i j c) = Function.update σ i (σ j) := by simp [sig, hc]
      rw [hs]
      apply inv_update z V h s σ _ i _ hI (fun r hr => Function.update_of_ne hr _ _)
      · intro _; simp [notV j c hj hc.2]
      · intro hiz; rw [hi] at hiz; exact absurd (Option.some.inj hiz) hc.1

def start : St K Reg C := ⟨fun _ => 0, fun _ => none⟩

theorem inv_run : ∀ (s : St K Reg C) (σ : Reg → K) (evs : List (Ev K Reg C)),
    Inv z V h s σ → Legal z V s evs → (∀ c, Ev.born h c ∈ evs → c ≠ z) →
    Inv z V h (run s evs) (sigRun z V h σ evs)
  | _, _, [], hI, _, _ => hI
  | s, σ, e :: es, hI, ⟨hL, hLs⟩, hb =>
    inv_run (step s e) (sig z V h σ e) es
      (inv_step z V h s σ e hI hL (fun c he => hb c (by simp [he])))
      hLs (fun c hc => hb c (by simp [hc]))

/-- **T1 (hub blindness).** In a legal run from the empty state in which `h` is not born at the
hub z (h off-hub born), every register r not at V at the end has e_h-coefficient equal to the
interior program's value: hub ops never enter it. -/
theorem T1_hub_blind (evs : List (Ev K Reg C)) (hL : Legal z V start evs)
    (hb : ∀ c, Ev.born h c ∈ evs → c ≠ z) (r : Reg) (hr : (run start evs).loc r ≠ some V) :
    (run start evs).row r h = sigRun z V h (fun _ => 0) (evs.filter fun e => ¬ hubOp z V e) r := by
  have hI : Inv z V h (start : St K Reg C) (fun _ => 0) :=
    ⟨fun _ _ => rfl, fun r hr => by simp [start] at hr⟩
  rw [(inv_run z V h start _ evs hI hL hb).1 r hr, sigRun_filter]

/-- **T1, two-run form.** Two legal runs with the same interior subsequence give every register
that is not at V at the end of both the same e_h-coefficient. -/
theorem T1_two_runs (evs evs' : List (Ev K Reg C))
    (hL : Legal z V start evs) (hL' : Legal z V start evs')
    (hb : ∀ c, Ev.born h c ∈ evs → c ≠ z) (hb' : ∀ c, Ev.born h c ∈ evs' → c ≠ z)
    (hfil : evs.filter (fun e => ¬ hubOp z V e) = evs'.filter (fun e => ¬ hubOp z V e))
    (r : Reg) (hr : (run start evs).loc r ≠ some V) (hr' : (run start evs').loc r ≠ some V) :
    (run start evs).row r h = (run start evs').row r h := by
  rw [T1_hub_blind z V h evs hL hb r hr, T1_hub_blind z V h evs' hL' hb' r hr', hfil]

/-! ## T2 difference lemma (direct carrier)

y's row evolves only by: `addK a r` (y += a·row_k, with row_k's e_k-coefficient 1), `addO w`
(y += w with w's e_k-coefficient 0) and `scale u` (prose leaves SCALE of y unstated; it is allowed).
`recv` tracks the net receipt from k, `A` the accumulated e_k-coefficient. -/

inductive YOp (K Reg : Type*)
  | addK (a : K) (r : Reg → K)
  | addO (w : Reg → K)
  | scale (u : K)

/-- (y, receipt from k, effective coefficient sum). -/
def yStep : (Reg → K) × (Reg → K) × K → YOp K Reg → (Reg → K) × (Reg → K) × K
  | (y, R, A), .addK a r => (y + a • r, R + a • r, A + a)
  | (y, R, A), .addO w => (y + w, R, A)
  | (y, R, A), .scale u => (u • y, u • R, u * A)

def yRun (st : (Reg → K) × (Reg → K) × K) : List (YOp K Reg) → (Reg → K) × (Reg → K) × K
  | [] => st
  | o :: os => yRun (yStep st o) os

/-- Invariant of the y-replay: y's e_k-coefficient equals the accumulated coefficient A, and
R − A·r1 stays in any submodule N containing every (row_k at a contact) − r1. -/
theorem T2_inv (k : Reg) (r1 : Reg → K) (N : Submodule K (Reg → K)) :
    ∀ (ops : List (YOp K Reg)) (y R : Reg → K) (A : K),
    (∀ a r, YOp.addK a r ∈ ops → r k = 1 ∧ r - r1 ∈ N) → (∀ w, YOp.addO w ∈ ops → w k = 0) →
    y k = A → R - A • r1 ∈ N →
    (yRun (y, R, A) ops).1 k = (yRun (y, R, A) ops).2.2 ∧
    (yRun (y, R, A) ops).2.1 - (yRun (y, R, A) ops).2.2 • r1 ∈ N
  | [], _, _, _, _, _, hy, hR => ⟨hy, hR⟩
  | o :: os, y, R, A, hK, hO, hy, hR => by
    have hK' : ∀ a r, YOp.addK a r ∈ os → r k = 1 ∧ r - r1 ∈ N :=
      fun a r h => hK a r (List.mem_cons_of_mem _ h)
    have hO' : ∀ w, YOp.addO w ∈ os → w k = 0 := fun w h => hO w (List.mem_cons_of_mem _ h)
    cases o with
    | addK a r =>
      obtain ⟨hrk, hrN⟩ := hK a r List.mem_cons_self
      apply T2_inv k r1 N os (y + a • r) (R + a • r) (A + a) hK' hO'
      · simp [hy, hrk]
      · have : R + a • r - (A + a) • r1 = (R - A • r1) + a • (r - r1) := by
          rw [add_smul, smul_sub]; abel
        rw [this]; exact N.add_mem hR (N.smul_mem a hrN)
    | addO w =>
      have hwk := hO w List.mem_cons_self
      apply T2_inv k r1 N os (y + w) R A hK' hO'
      · simp [hy, hwk]
      · exact hR
    | scale u =>
      apply T2_inv k r1 N os (u • y) (u • R) (u * A) hK' hO'
      · simp [hy]
      · have : u • R - (u * A) • r1 = u • (R - A • r1) := by rw [smul_sub, mul_smul]
        rw [this]; exact N.smul_mem u hR

/-- **T2 (difference lemma, direct carrier).** y starts with e_k-coefficient 0 and its row changes
only through `ops`: contacts y += a·row_k(t) (row_k(t) has e_k-coefficient 1), additions of rows
free of e_k, and SCALEs of y. If y's final e_k-coefficient is 0 (its SPEC final row has no helper
coordinate; T1: no hub op can fix it), then
* the effective coefficients sum to 0, and
* the net receipt from k lies in span{row_k(t_i) − row_k(t_1)}: what k carried into its first
  contact with y never reaches y net (any reference row r1, in particular row_k at the first contact). -/
theorem T2_difference (k : Reg) (r1 : Reg → K) (ops : List (YOp K Reg)) (y0 : Reg → K)
    (hy0 : y0 k = 0)
    (hK : ∀ a r, YOp.addK a r ∈ ops → r k = 1) (hO : ∀ w, YOp.addO w ∈ ops → w k = 0)
    (hfin : (yRun (y0, 0, 0) ops).1 k = 0) :
    (yRun (y0, 0, 0) ops).2.2 = 0 ∧
    (yRun (y0, 0, 0) ops).2.1 ∈
      Submodule.span K {x | ∃ a r, YOp.addK a r ∈ ops ∧ x = r - r1} := by
  set N := Submodule.span K {x | ∃ a r, YOp.addK a r ∈ ops ∧ x = r - r1}
  have := T2_inv k r1 N ops y0 0 0
    (fun a r h => ⟨hK a r h, Submodule.subset_span ⟨a, r, h, rfl⟩⟩) hO hy0 (by simp)
  have hA : (yRun (y0, 0, 0) ops).2.2 = 0 := by rw [← this.1, hfin]
  refine ⟨hA, ?_⟩
  have h2 := this.2
  rwa [hA, zero_smul, sub_zero] at h2

/-- The receipt bookkeeping is faithful: the final row is y0 scaled, plus the receipt from k, plus
the other additions (scaled by later SCALEs). Here only the e_k-coordinate part matters, so we
record the coefficient identity: final e_k-coefficient = (Π scales)·y0_k + A. With y0_k = 0 this is A. -/
theorem T2_coeff (k : Reg) : ∀ (ops : List (YOp K Reg)) (y R : Reg → K) (A : K),
    (∀ a r, YOp.addK a r ∈ ops → r k = 1) → (∀ w, YOp.addO w ∈ ops → w k = 0) →
    y k = A → (yRun (y, R, A) ops).1 k = (yRun (y, R, A) ops).2.2 := by
  intro ops y R A hK hO hy
  exact (T2_inv k 0 ⊤ ops y R A (fun a r h => ⟨hK a r h, Submodule.mem_top⟩) hO hy
    Submodule.mem_top).1

/-! ## T2, corrected Σ statement (LEAN-NEXT7)

The literal "Σ a_i = 0" is false once y is SCALEd between contacts (`T2_literal_false`). The
correct statement uses EFFECTIVE coefficients: contact i contributes a_i · Π(scales of y after it).
`scl ops` = product of all SCALE factors of y in `ops`; `contacts ops` = (effective coefficient,
row_k at the contact) for each contact, in order. -/

/-- product of the SCALE factors of y in `ops`. -/
def scl : List (YOp K Reg) → K
  | [] => 1
  | .scale u :: os => u * scl os
  | .addK _ _ :: os => scl os
  | .addO _ :: os => scl os

/-- contacts with their effective coefficients a_i · Π(later scales). -/
def contacts : List (YOp K Reg) → List (K × (Reg → K))
  | [] => []
  | .addK a r :: os => (a * scl os, r) :: contacts os
  | .addO _ :: os => contacts os
  | .scale _ :: os => contacts os

/-- Closed form of the coefficient and receipt trackers. -/
theorem yRun_closed : ∀ (ops : List (YOp K Reg)) (y R : Reg → K) (A : K),
    (yRun (y, R, A) ops).2.2 = scl ops * A + ((contacts ops).map Prod.fst).sum ∧
    (yRun (y, R, A) ops).2.1 = scl ops • R + ((contacts ops).map (fun p => p.1 • p.2)).sum
  | [], y, R, A => by simp [yRun, scl, contacts]
  | o :: os, y, R, A => by
    cases o with
    | addK a r =>
      obtain ⟨h1, h2⟩ := yRun_closed os (y + a • r) (R + a • r) (A + a)
      simp only [yRun, yStep, scl, contacts, List.map_cons, List.sum_cons]
      refine ⟨by rw [h1]; ring, ?_⟩
      rw [h2, smul_add, smul_smul, mul_comm (scl os) a]; abel
    | addO w =>
      obtain ⟨h1, h2⟩ := yRun_closed os (y + w) R A
      simpa only [yRun, yStep, scl, contacts] using ⟨h1, h2⟩
    | scale u =>
      obtain ⟨h1, h2⟩ := yRun_closed os (u • y) (u • R) (u * A)
      simp only [yRun, yStep, scl, contacts]
      refine ⟨by rw [h1]; ring, ?_⟩
      rw [h2, smul_smul, mul_comm (scl os) u]

/-- **T2, corrected.** Hypotheses as in `T2_difference`. Then
* Σ (effective coefficients a_i · Π later scales of y) = 0;
* the net receipt from k is Σ eff_i · row_k(t_i) = Σ eff_i · (row_k(t_i) − r1) for ANY r1, in
  particular r1 = row_k(t_1): content k carried into its first contact never reaches y net. -/
theorem T2_corrected (k : Reg) (ops : List (YOp K Reg)) (y0 : Reg → K)
    (hy0 : y0 k = 0)
    (hK : ∀ a r, YOp.addK a r ∈ ops → r k = 1) (hO : ∀ w, YOp.addO w ∈ ops → w k = 0)
    (hfin : (yRun (y0, 0, 0) ops).1 k = 0) (r1 : Reg → K) :
    ((contacts ops).map Prod.fst).sum = 0 ∧
    (yRun (y0, 0, 0) ops).2.1 = ((contacts ops).map (fun p => p.1 • p.2)).sum ∧
    (yRun (y0, 0, 0) ops).2.1 = ((contacts ops).map (fun p => p.1 • (p.2 - r1))).sum := by
  obtain ⟨h1, h2⟩ := yRun_closed ops y0 0 0
  have hA := (T2_difference k r1 ops y0 hy0 hK hO hfin).1
  rw [h1, mul_zero, zero_add] at hA
  have hrec : (yRun (y0, 0, 0) ops).2.1 = ((contacts ops).map (fun p => p.1 • p.2)).sum := by
    rw [h2, smul_zero, zero_add]
  refine ⟨hA, hrec, ?_⟩
  have hsplit : ∀ l : List (K × (Reg → K)),
      (l.map (fun p => p.1 • (p.2 - r1))).sum
        = (l.map (fun p => p.1 • p.2)).sum - (l.map Prod.fst).sum • r1 := by
    intro l; induction l with
    | nil => simp
    | cons p l ih =>
      simp only [List.map_cons, List.sum_cons]; rw [ih, add_smul, smul_sub]; abel
  rw [hsplit, hA, zero_smul, sub_zero, hrec]

/-- Without SCALEs of y the effective coefficients are the literal a_i, so the prose "Σ a_i = 0"
holds verbatim. -/
theorem contacts_noscale : ∀ (ops : List (YOp K Reg)), (∀ u, YOp.scale u ∉ ops) →
    (contacts ops).map Prod.fst = ops.filterMap (fun o => match o with
      | .addK a _ => some a | _ => none)
  | [], _ => rfl
  | o :: os, h => by
    have h' : ∀ u, YOp.scale u ∉ os := fun u hu => h u (List.mem_cons_of_mem _ hu)
    have hs : scl os = 1 := by
      clear h; induction os with
      | nil => rfl
      | cons o' os' ih =>
        cases o' with
        | scale u => exact absurd List.mem_cons_self (h' u)
        | addK a r => exact ih (fun u hu => h' u (List.mem_cons_of_mem _ hu))
        | addO w => exact ih (fun u hu => h' u (List.mem_cons_of_mem _ hu))
    cases o with
    | addK a r => simp [contacts, hs, contacts_noscale os h']
    | addO w => simpa [contacts] using contacts_noscale os h'
    | scale u => exact absurd List.mem_cons_self (h u)

/-- The finding, formal: y += k, y *= 2, y += (−2)·k. Final e_k-coefficient 0, literal Σ a = −1,
effective Σ = 1·2 + (−2) = 0. Over ℚ with one register. -/
theorem T2_literal_false :
    let ek : Unit → ℚ := fun _ => 1
    let ops : List (YOp ℚ Unit) := [.addK 1 ek, .scale 2, .addK (-2) ek]
    (yRun ((0 : Unit → ℚ), 0, 0) ops).1 () = 0 ∧ (1 : ℚ) + (-2) ≠ 0 ∧
    ((contacts ops).map Prod.fst).sum = 0 := by
  refine ⟨?_, by norm_num, ?_⟩ <;> simp [yRun, yStep, contacts, scl]

end TokenCancel

#print axioms TokenCancel.T1_hub_blind
#print axioms TokenCancel.T1_two_runs
#print axioms TokenCancel.T2_difference
#print axioms TokenCancel.T2_corrected
#print axioms TokenCancel.contacts_noscale
#print axioms TokenCancel.T2_literal_false
