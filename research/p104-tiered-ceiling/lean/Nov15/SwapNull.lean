/-
SwapNull, See SwapNull.md.
Formalises LAWBUILD M3's law SWAP-NULL (internal notes).

Part A (op level, TokenCancel's model): the 4-op swap gadget
    add h1 h2 (+1); add h2 h1 (-1); add h1 h2 (+1); scale h2 (-1)      (3 ADD + SCALE -1, all at chart c)
exchanges the rows of h1 and h2.  Tail swap = gadget, then every later event renamed h1<->h2:
the final state is the unswapped final state with the rows of h1, h2 exchanged (`tail_run`).
Head swap = earlier events renamed, then gadget: every final row has its h1/h2 COORDINATES
exchanged (`head_run`).
Part B (hub model, matrix level): only a V mix L (acts on V-ender rows) or a {0}-prefix M (acts on
G0 columns) can undo that; exact statements `tail_iff`, `head_iff`, `undo_one_iff`.
Part C (ladder): per-helper cost f(e-b) - sum f(gaps) (RelaySandwich.stopCost); the swap leaves the
stay multiset unchanged and changes the span terms by a rectangle difference, which is 0 iff the
ends agree or the births agree (`delta_eq`, `delta_zero_end`, `delta_zero_birth`).
Part D: law bundle and a concrete witness.
-/
import Nov15.TokenCancel
import Nov15.RelaySandwich
import Nov15.SwapWord
import Mathlib.Data.Matrix.Mul
import Mathlib.LinearAlgebra.Matrix.ToLin

set_option linter.unusedSectionVars false

namespace SwapNull
open TokenCancel

/-! ### Part A: the gadget and the two renamings -/
section Op
variable {K Reg C : Type*} [Field K] [DecidableEq Reg] [DecidableEq C]

/-- The 4-op swap gadget at chart `c`. -/
def gadget (h1 h2 : Reg) (c : C) : List (Ev K Reg C) :=
  [.add h1 h2 1 c, .add h2 h1 (-1) c, .add h1 h2 1 c, .scale h2 (-1) c]

theorem gadget_legal (h1 h2 : Reg) (hne : h1 ≠ h2) (c : C) (z V : C) (s : St K Reg C)
    (a : s.loc h1 = some c) (b : s.loc h2 = some c) :
    Legal z V s (gadget h1 h2 c) := by
  simp [gadget, Legal, LegalEv, step, hne, hne.symm, a, b]

/-- Rows and locations read through a register permutation. -/
def permSt (σ : Equiv.Perm Reg) (s : St K Reg C) : St K Reg C :=
  ⟨fun r => s.row (σ r), fun r => s.loc (σ r)⟩

/-- Rows with their coordinates read through σ. -/
def cpermSt (σ : Equiv.Perm Reg) (s : St K Reg C) : St K Reg C :=
  ⟨fun r => fun k => s.row r (σ k), s.loc⟩

def ren (σ : Equiv.Perm Reg) : Ev K Reg C → Ev K Reg C
  | .born i c => .born (σ i) c
  | .init i c => .init (σ i) c
  | .move i c => .move (σ i) c
  | .add i j a c => .add (σ i) (σ j) a c
  | .scale i u c => .scale (σ i) u c
  | .clear i c => .clear (σ i) c
  | .copy i j c => .copy (σ i) (σ j) c

theorem gadget_run (h1 h2 : Reg) (hne : h1 ≠ h2) (c : C) (s : St K Reg C) :
    (run s (gadget h1 h2 c)).row = (fun r => s.row (Equiv.swap h1 h2 r)) ∧
    (run s (gadget h1 h2 c)).loc = s.loc := by
  refine ⟨?_, ?_⟩
  · funext r
    by_cases r1 : r = h1
    · subst r1
      simp [gadget, run, step, hne, hne.symm]
    · by_cases r2 : r = h2
      · subst r2
        simp [gadget, run, step, hne, hne.symm, Function.update_apply]
      · simp [gadget, run, step, r1, r2, Function.update_apply, Equiv.swap_apply_of_ne_of_ne]
  · simp [gadget, run, step]

lemma upd_perm {β : Type*} (σ : Equiv.Perm Reg) (hσ : ∀ r, σ (σ r) = r) (f : Reg → β)
    (i : Reg) (v : β) :
    (fun r => Function.update f i v (σ r)) = Function.update (fun r => f (σ r)) (σ i) v := by
  funext r
  simp only [Function.update_apply]
  have : σ r = i ↔ r = σ i := ⟨fun h => by rw [← h, hσ], fun h => by rw [h, hσ]⟩
  simp only [this]

theorem step_permSt (σ : Equiv.Perm Reg) (hσ : ∀ r, σ (σ r) = r) (s : St K Reg C)
    (e : Ev K Reg C) (hb : ∀ i c, e = .born i c → σ i = i) :
    step (permSt σ s) (ren σ e) = permSt σ (step s e) := by
  cases e with
  | born i c =>
    have hi := hb i c rfl
    simp only [step, ren, permSt, St.mk.injEq]
    rw [upd_perm σ hσ, upd_perm σ hσ, hi]
    simp
  | init i c =>
    simp only [step, ren, permSt, St.mk.injEq]
    rw [upd_perm σ hσ, upd_perm σ hσ]
    simp
  | move i c =>
    simp only [step, ren, permSt, St.mk.injEq]
    rw [upd_perm σ hσ]
    simp
  | add i j a c =>
    simp only [step, ren, permSt, St.mk.injEq]
    rw [upd_perm σ hσ]
    simp [hσ]
  | scale i u c =>
    simp only [step, ren, permSt, St.mk.injEq]
    rw [upd_perm σ hσ]
    simp [hσ]
  | clear i c =>
    simp only [step, ren, permSt, St.mk.injEq]
    rw [upd_perm σ hσ]
    simp
  | copy i j a =>
    simp only [step, ren, permSt, St.mk.injEq]
    rw [upd_perm σ hσ]
    simp [hσ]

theorem run_permSt (σ : Equiv.Perm Reg) (hσ : ∀ r, σ (σ r) = r) (evs : List (Ev K Reg C))
    (hb : ∀ e ∈ evs, ∀ i c, e = .born i c → σ i = i) (s : St K Reg C) :
    run (permSt σ s) (evs.map (ren σ)) = permSt σ (run s evs) := by
  induction evs generalizing s with
  | nil => rfl
  | cons e es ih =>
    simp only [List.map_cons, run]
    rw [step_permSt σ hσ s e (hb e (by simp)), ih (fun e' he' => hb e' (by simp [he']))]

/-- Tail swap: gadget at the shared chart, then every later event renamed h1 <-> h2.
Final rows = unswapped final rows with h1, h2 exchanged; locations unchanged. -/
theorem tail_run (h1 h2 : Reg) (hne : h1 ≠ h2) (c : C) (s : St K Reg C)
    (a : s.loc h1 = some c) (b : s.loc h2 = some c) (evs : List (Ev K Reg C))
    (hb : ∀ e ∈ evs, ∀ i c, e = .born i c → i ≠ h1 ∧ i ≠ h2) :
    run s (gadget h1 h2 c ++ evs.map (ren (Equiv.swap h1 h2))) =
      permSt (Equiv.swap h1 h2) (run s evs) := by
  have hσ : ∀ r, Equiv.swap h1 h2 (Equiv.swap h1 h2 r) = r := fun r => Equiv.swap_apply_self _ _ _
  have hg := gadget_run h1 h2 hne c s
  have hs : run s (gadget h1 h2 c) = permSt (Equiv.swap h1 h2) s := by
    have hloc : ∀ r, s.loc (Equiv.swap h1 h2 r) = s.loc r := by
      intro r
      by_cases r1 : r = h1
      · subst r1; simp [a, b]
      · by_cases r2 : r = h2
        · subst r2; simp [a, b]
        · rw [Equiv.swap_apply_of_ne_of_ne r1 r2]
    cases hr : run s (gadget h1 h2 c) with
    | mk row loc =>
      rw [hr] at hg
      simp only [permSt, St.mk.injEq]
      obtain ⟨hg1, hg2⟩ := hg
      simp only at hg1 hg2
      refine ⟨hg1, ?_⟩
      rw [hg2]; funext r; exact (hloc r).symm
  rw [SwapWord.run_append, hs]
  exact run_permSt _ hσ evs (fun e he i c h => by
    obtain ⟨x, y⟩ := hb e he i c h
    exact Equiv.swap_apply_of_ne_of_ne x y) s

/-- Registers and coordinates both read through σ (the state of a run whose events were renamed). -/
def bothSt (σ : Equiv.Perm Reg) (s : St K Reg C) : St K Reg C :=
  ⟨fun r k => s.row (σ r) (σ k), fun r => s.loc (σ r)⟩

lemma upd_both (σ : Equiv.Perm Reg) (hσ : ∀ r, σ (σ r) = r) (f : Reg → Reg → K)
    (i : Reg) (v : Reg → K) :
    (fun r k => Function.update f i v (σ r) (σ k)) =
      Function.update (fun r k => f (σ r) (σ k)) (σ i) (fun k => v (σ k)) := by
  funext r k
  have : σ r = i ↔ r = σ i := ⟨fun h => by rw [← h, hσ], fun h => by rw [h, hσ]⟩
  by_cases h : r = σ i
  · subst h
    simp [Function.update_apply, hσ]
  · have h' : ¬ σ r = i := fun x => h (this.1 x)
    simp [Function.update_apply, h, h']

theorem step_bothSt (σ : Equiv.Perm Reg) (hσ : ∀ r, σ (σ r) = r) (s : St K Reg C)
    (e : Ev K Reg C) :
    step (bothSt σ s) (ren σ e) = bothSt σ (step s e) := by
  cases e with
  | born i c =>
    simp only [step, ren, bothSt, St.mk.injEq]
    rw [upd_both σ hσ, upd_perm σ hσ]
    have : (fun k => (Pi.single i (1 : K) : Reg → K) (σ k)) = Pi.single (σ i) 1 := by
      funext k
      have : σ k = i ↔ k = σ i := ⟨fun h => by rw [← h, hσ], fun h => by rw [h, hσ]⟩
      by_cases h : k = σ i
      · simp [Pi.single_apply, h, this.2 h, hσ]
      · have hn : ¬ σ k = i := fun x => h (this.1 x)
        simp [Pi.single_apply, h, hn]
    rw [this]; simp
  | init i c =>
    simp only [step, ren, bothSt, St.mk.injEq]
    rw [upd_both σ hσ, upd_perm σ hσ]; simp; congr 1
  | move i c =>
    simp only [step, ren, bothSt, St.mk.injEq]
    rw [upd_perm σ hσ]; simp
  | add i j a c =>
    simp only [step, ren, bothSt, St.mk.injEq]
    rw [upd_both σ hσ]; simp [hσ]; congr 1
  | scale i u c =>
    simp only [step, ren, bothSt, St.mk.injEq]
    rw [upd_both σ hσ]; simp [hσ]; congr 1
  | clear i c =>
    simp only [step, ren, bothSt, St.mk.injEq]
    rw [upd_both σ hσ]; simp; congr 1
  | copy i j c =>
    simp only [step, ren, bothSt, St.mk.injEq]
    rw [upd_both σ hσ]; simp [hσ]

theorem run_bothSt (σ : Equiv.Perm Reg) (hσ : ∀ r, σ (σ r) = r) (evs : List (Ev K Reg C))
    (s : St K Reg C) :
    run (bothSt σ s) (evs.map (ren σ)) = bothSt σ (run s evs) := by
  induction evs generalizing s with
  | nil => rfl
  | cons e es ih =>
    simp only [List.map_cons, run]
    rw [step_bothSt σ hσ s e, ih]

theorem step_cpermSt (σ : Equiv.Perm Reg) (s : St K Reg C)
    (e : Ev K Reg C) (hσ : ∀ r, σ (σ r) = r) (hb : ∀ i c, e = .born i c → σ i = i) :
    step (cpermSt σ s) e = cpermSt σ (step s e) := by
  cases e with
  | born i c =>
    have hi := hb i c rfl
    simp only [step, cpermSt]
    congr 1
    funext r k
    by_cases h : r = i
    · subst h
      have : σ k = r ↔ k = r := ⟨fun h => by rw [← hi, ← h, hσ], fun h => by rw [h, hi]⟩
      by_cases hk : k = r
      · simp [Pi.single_apply, hk, hi]
      · have hn : ¬ σ k = r := fun x => hk (this.1 x)
        simp [Pi.single_apply, hk, hn]
    · simp [Function.update_apply, h]
  | init i c =>
    simp only [step, cpermSt]
    congr 1
    funext r k; by_cases h : r = i <;> simp [Function.update_apply, h]
  | move i c => simp [step, cpermSt]
  | add i j a c =>
    simp only [step, cpermSt]
    congr 1
    funext r k; by_cases h : r = i <;> simp [Function.update_apply, h]
  | scale i u c =>
    simp only [step, cpermSt]
    congr 1
    funext r k; by_cases h : r = i <;> simp [Function.update_apply, h]
  | clear i c =>
    simp only [step, cpermSt]
    congr 1
    funext r k; by_cases h : r = i <;> simp [Function.update_apply, h]
  | copy i j c =>
    simp only [step, cpermSt]
    congr 1
    funext r k; by_cases h : r = i <;> simp [Function.update_apply, h]

theorem run_cpermSt (σ : Equiv.Perm Reg) (hσ : ∀ r, σ (σ r) = r) (evs : List (Ev K Reg C))
    (hb : ∀ e ∈ evs, ∀ i c, e = .born i c → σ i = i) (s : St K Reg C) :
    run (cpermSt σ s) evs = cpermSt σ (run s evs) := by
  induction evs generalizing s with
  | nil => rfl
  | cons e es ih =>
    simp only [run]
    rw [step_cpermSt σ s e hσ (hb e (by simp)), ih (fun e' he' => hb e' (by simp [he']))]

/-- Head swap: earlier events (`pre`) renamed h1 <-> h2, then the gadget at the shared chart, then the
original later events (`post`, no births of h1, h2).  If the start state is σ-symmetric, every
final row has its h1/h2 coordinates exchanged; locations are unchanged. -/
theorem head_run (h1 h2 : Reg) (hne : h1 ≠ h2) (c : C) (s0 : St K Reg C)
    (hs0 : bothSt (Equiv.swap h1 h2) s0 = s0)
    (pre post : List (Ev K Reg C))
    (a : (run s0 pre).loc h1 = some c) (b : (run s0 pre).loc h2 = some c)
    (hb : ∀ e ∈ post, ∀ i c, e = .born i c → i ≠ h1 ∧ i ≠ h2) :
    run s0 (pre.map (ren (Equiv.swap h1 h2)) ++ gadget h1 h2 c ++ post) =
      cpermSt (Equiv.swap h1 h2) (run s0 (pre ++ post)) := by
  have hσ : ∀ r, Equiv.swap h1 h2 (Equiv.swap h1 h2 r) = r := fun r => Equiv.swap_apply_self _ _ _
  set σ := Equiv.swap h1 h2 with hσdef
  set t := run s0 pre with ht
  have h1' : run s0 (pre.map (ren σ)) = bothSt σ t := by
    conv_lhs => rw [← hs0]
    exact run_bothSt σ hσ pre s0
  have hg := gadget_run h1 h2 hne c (bothSt σ t)
  have hloc : ∀ r, t.loc (σ r) = t.loc r := by
    intro r
    by_cases r1 : r = h1
    · subst r1; simp [σ, a, b]
    · by_cases r2 : r = h2
      · subst r2; simp [σ, a, b]
      · rw [Equiv.swap_apply_of_ne_of_ne r1 r2]
  have hs : run (bothSt σ t) (gadget h1 h2 c) = cpermSt σ t := by
    cases hr : run (bothSt σ t) (gadget h1 h2 c) with
    | mk row loc =>
      rw [hr] at hg
      obtain ⟨hg1, hg2⟩ := hg
      simp only [bothSt] at hg1 hg2
      simp only [cpermSt, St.mk.injEq]
      refine ⟨?_, ?_⟩
      · rw [hg1]; funext r k; exact congrArg (fun x => t.row x (σ k)) (hσ r)
      · rw [hg2]; funext r; exact hloc r
  rw [SwapWord.run_append, SwapWord.run_append, h1', hs,
    run_cpermSt σ hσ post (fun e he i c h => by
      obtain ⟨x, y⟩ := hb e he i c h
      exact Equiv.swap_apply_of_ne_of_ne x y), SwapWord.run_append s0 pre post]

end Op

/-! ### Part B: what the hubs can undo (matrix level; HubSettle's V mix and {0}-prefix) -/
section Hub
variable {K Reg : Type*} [Field K] [Fintype Reg] [DecidableEq Reg]

/-- `A` is the identity outside the `S × S` block (a hub op acts only inside its own block). -/
def Blk (S : Reg → Prop) (A : Matrix Reg Reg K) : Prop :=
  ∀ i k, ¬ (S i ∧ S k) → A i k = (1 : Matrix Reg Reg K) i k

/-- F' can be restored to F by a V mix `L` (block on V-enders, acts on rows) and a {0}-prefix `M`
(block on G0 columns, right multiplication).  Invertibility is not demanded (strengthens the
only-if directions); the witnesses used for the if directions are permutation matrices. -/
def Undo (V G0 : Reg → Prop) (F F' : Matrix Reg Reg K) : Prop :=
  ∃ L M : Matrix Reg Reg K, Blk V L ∧ Blk G0 M ∧ L * F' * M = F

/-- Tail swap of the final matrix: rows h1,h2 exchanged. -/
def rowSw (σ : Equiv.Perm Reg) (F : Matrix Reg Reg K) : Matrix Reg Reg K :=
  Matrix.of fun i k => F (σ i) k
/-- Head swap of the final matrix: coordinates h1,h2 exchanged. -/
def colSw (σ : Equiv.Perm Reg) (F : Matrix Reg Reg K) : Matrix Reg Reg K :=
  Matrix.of fun i k => F i (σ k)

def swapMat (σ : Equiv.Perm Reg) : Matrix Reg Reg K :=
  Matrix.of fun i k => if k = σ i then 1 else 0

lemma blk_one (S : Reg → Prop) : Blk S (1 : Matrix Reg Reg K) := fun _ _ _ => rfl

lemma swapMat_mul (σ : Equiv.Perm Reg) (A : Matrix Reg Reg K) : swapMat σ * A = rowSw σ A := by
  ext i k
  simp [Matrix.mul_apply, swapMat, rowSw]

lemma mul_swapMat (σ : Equiv.Perm Reg) (hσ : ∀ r, σ (σ r) = r) (A : Matrix Reg Reg K) :
    A * swapMat σ = colSw σ A := by
  ext i k
  simp only [Matrix.mul_apply, swapMat, colSw, Matrix.of_apply]
  have : ∀ j, (k = σ j) ↔ (j = σ k) := fun j => ⟨fun h => by rw [h, hσ], fun h => by rw [h, hσ]⟩
  simp [this]

lemma swapMat_blk (h1 h2 : Reg) (S : Reg → Prop) (a : S h1) (b : S h2) :
    Blk S (swapMat (Equiv.swap h1 h2) : Matrix Reg Reg K) := by
  intro i k hik
  simp only [swapMat, Matrix.of_apply, Matrix.one_apply]
  have hk1 : ∀ x, S x → ¬ S k → x ≠ k := fun x hx hk h => hk (h ▸ hx)
  by_cases i1 : i = h1
  · subst i1
    have hk : ¬ S k := fun h => hik ⟨a, h⟩
    simp [hk1 _ a hk, hk1 _ b hk, (hk1 _ a hk).symm, (hk1 _ b hk).symm]
  · by_cases i2 : i = h2
    · subst i2
      have hk : ¬ S k := fun h => hik ⟨b, h⟩
      simp [hk1 _ a hk, hk1 _ b hk, (hk1 _ a hk).symm, (hk1 _ b hk).symm]
    · rw [Equiv.swap_apply_of_ne_of_ne i1 i2]
      simp [eq_comm]

lemma blk_row {V : Reg → Prop} {L : Matrix Reg Reg K} (hL : Blk V L) {x : Reg} (hx : ¬ V x)
    (Y : Matrix Reg Reg K) : (L * Y) x = Y x := by
  funext k
  have : ∀ m, L x m = if x = m then 1 else 0 := fun m => by
    simpa [Matrix.one_apply] using hL x m (fun h => hx h.1)
  simp [Matrix.mul_apply, this]

lemma mul_blk_col {G0 : Reg → Prop} {M : Matrix Reg Reg K} (hM : Blk G0 M) {a : Reg}
    (ha : ¬ G0 a) (Y : Matrix Reg Reg K) (i : Reg) : (Y * M) i a = Y i a := by
  have : ∀ j, M j a = if j = a then 1 else 0 := fun j => by
    simpa [Matrix.one_apply] using hM j a (fun h => ha h.2)
  simp [Matrix.mul_apply, this]

lemma row_eq {V : Reg → Prop} {F F' L M : Matrix Reg Reg K} (hL : Blk V L)
    (h : L * F' * M = F) {x : Reg} (hx : ¬ V x) : (F' * M) x = F x := by
  rw [Matrix.mul_assoc] at h
  have := blk_row hL hx (F' * M)
  rw [h] at this
  exact this.symm

section Swap
variable (h1 h2 : Reg)

local notation "σ" => Equiv.swap h1 h2

lemma swap_inv (r : Reg) : σ (σ r) = r := Equiv.swap_apply_self _ _ _

/-- Both helpers end in V: the V mix undoes the tail swap. -/
theorem tail_if (V G0 : Reg → Prop) (F : Matrix Reg Reg K) (a : V h1) (b : V h2) :
    Undo V G0 F (rowSw σ F) := by
  refine ⟨swapMat σ, 1, swapMat_blk h1 h2 V a b, blk_one _, ?_⟩
  rw [Matrix.mul_one, swapMat_mul]
  ext i k
  simp [rowSw, swap_inv]

/-- Both helpers born in {0}: the {0}-prefix undoes the head swap. -/
theorem head_if (V G0 : Reg → Prop) (F : Matrix Reg Reg K) (a : G0 h1) (b : G0 h2) :
    Undo V G0 F (colSw σ F) := by
  refine ⟨1, swapMat σ, blk_one _, swapMat_blk h1 h2 G0 a b, ?_⟩
  rw [Matrix.one_mul, mul_swapMat σ (swap_inv h1 h2)]
  ext i k
  simp [colSw, swap_inv]

lemma ab_cases (a : Reg) (ha : a = h1 ∨ a = h2) (hne : h1 ≠ h2) :
    (a = h1 ∧ σ a = h2) ∨ (a = h2 ∧ σ a = h1) := by
  rcases ha with rfl | rfl
  · left; simp
  · right; simp

/-- Tail swap, only-if.  `hrig`: the unchanged non-V rows pin every {0}-prefix to the identity
(`rigid_of_span` gives this from a spanning condition).  Then a tail swap is undone only if both
helpers end in V. -/
theorem tail_only_if (V G0 : Reg → Prop) (hne : h1 ≠ h2) (F : Matrix Reg Reg K)
    (hF1 : F h1 = Pi.single h1 1) (hF2 : F h2 = Pi.single h2 1)
    (hrig : ∀ M : Matrix Reg Reg K, Blk G0 M →
      (∀ x, x ≠ h1 → x ≠ h2 → ¬ V x → (F * M) x = F x) → M = 1) :
    Undo V G0 F (rowSw σ F) → V h1 ∧ V h2 := by
  rintro ⟨L, M, hL, hM, h⟩
  by_contra hn
  obtain ⟨a, ha, haV⟩ : ∃ a, (a = h1 ∨ a = h2) ∧ ¬ V a := by
    by_cases v1 : V h1
    · exact ⟨h2, Or.inr rfl, fun v2 => hn ⟨v1, v2⟩⟩
    · exact ⟨h1, Or.inl rfl, v1⟩
  have key : ∀ x, ¬ V x → (rowSw σ F * M) x = F x := fun x hx => row_eq hL h hx
  have hM1 : M = 1 := by
    refine hrig M hM (fun x hx1 hx2 hxV => ?_)
    have := key x hxV
    have hsx : σ x = x := Equiv.swap_apply_of_ne_of_ne hx1 hx2
    funext k
    have := congrFun this k
    simpa [rowSw, Matrix.mul_apply, hsx] using this
  subst hM1
  have e : F (σ a) = F a := by
    have := key a haV
    rw [Matrix.mul_one] at this
    exact this
  rcases ab_cases h1 h2 a ha hne with ⟨rfl, h'⟩ | ⟨rfl, h'⟩
  · rw [h', hF1, hF2] at e
    have := congrFun e a
    simp [Pi.single_apply, hne.symm] at this
  · rw [h', hF1, hF2] at e
    have := congrFun e a
    simp [Pi.single_apply, hne] at this

/-- Head swap, only-if: if some non-V row distinguishes the h1 and h2 coordinates, the swap is
undone only if both helpers are born in {0}. -/
theorem head_only_if (V G0 : Reg → Prop) (hne : h1 ≠ h2) (F : Matrix Reg Reg K)
    (hw : ∃ x, ¬ V x ∧ F x h1 ≠ F x h2) :
    Undo V G0 F (colSw σ F) → G0 h1 ∧ G0 h2 := by
  rintro ⟨L, M, hL, hM, h⟩
  obtain ⟨x, hxV, hxne⟩ := hw
  by_contra hn
  obtain ⟨a, ha, haG⟩ : ∃ a, (a = h1 ∨ a = h2) ∧ ¬ G0 a := by
    by_cases v1 : G0 h1
    · exact ⟨h2, Or.inr rfl, fun v2 => hn ⟨v1, v2⟩⟩
    · exact ⟨h1, Or.inl rfl, v1⟩
  have e := congrFun (row_eq hL h hxV) a
  rw [mul_blk_col hM haG] at e
  simp only [colSw, Matrix.of_apply] at e
  rcases ab_cases h1 h2 a ha hne with ⟨rfl, h'⟩ | ⟨rfl, h'⟩
  · rw [h'] at e; exact hxne e.symm
  · rw [h'] at e; exact hxne e

/-- Identity-final case: the swap matrix is the same for both kinds; it is undone iff both
helpers end in V or both are born in {0}. -/
theorem undo_one_iff (V G0 : Reg → Prop) (hne : h1 ≠ h2) :
    Undo V G0 (1 : Matrix Reg Reg K) (rowSw σ 1) ↔ (V h1 ∧ V h2) ∨ (G0 h1 ∧ G0 h2) := by
  constructor
  · rintro ⟨L, M, hL, hM, h⟩
    by_cases hv : V h1 ∧ V h2
    · exact Or.inl hv
    right
    obtain ⟨a, ha, haV⟩ : ∃ a, (a = h1 ∨ a = h2) ∧ ¬ V a := by
      by_cases v1 : V h1
      · exact ⟨h2, Or.inr rfl, fun v2 => hv ⟨v1, v2⟩⟩
      · exact ⟨h1, Or.inl rfl, v1⟩
    have e := congrFun (row_eq hL h haV) a
    have hMa : M (σ a) a = 1 := by
      have : (rowSw σ (1 : Matrix Reg Reg K) * M) a a = M (σ a) a := by
        simp [rowSw, Matrix.mul_apply, Matrix.one_apply]
      rw [this] at e
      simpa using e
    have hG : G0 (σ a) ∧ G0 a := by
      by_contra hc
      have := hM (σ a) a hc
      rw [hMa] at this
      have hn : σ a ≠ a := by
        rcases ab_cases h1 h2 a ha hne with ⟨rfl, h'⟩ | ⟨rfl, h'⟩
        · rw [h']; exact hne.symm
        · rw [h']; exact hne
      simp [Matrix.one_apply, hn] at this
    rcases ab_cases h1 h2 a ha hne with ⟨rfl, h'⟩ | ⟨rfl, h'⟩
    · rw [h'] at hG; exact ⟨hG.2, hG.1⟩
    · rw [h'] at hG; exact hG
  · rintro (⟨a, b⟩ | ⟨a, b⟩)
    · exact tail_if h1 h2 V G0 1 a b
    · have := head_if h1 h2 V G0 (1 : Matrix Reg Reg K) a b
      have e : colSw σ (1 : Matrix Reg Reg K) = rowSw σ 1 := by
        ext i k
        have : (σ i = k) ↔ (i = σ k) :=
          ⟨fun h => by rw [← h, swap_inv], fun h => by rw [h, swap_inv]⟩
        simp [colSw, rowSw, Matrix.one_apply, this]
      rwa [e] at this

end Swap

end Hub

section Rigid
variable {K Reg : Type*} [Field K] [Fintype Reg] [DecidableEq Reg]

lemma single_vecMul (M : Matrix Reg Reg K) (i : Reg) :
    Matrix.vecMul (Pi.single i (1 : K) : Reg → K) M = M i := by
  funext j
  simp [Matrix.vecMul, dotProduct, Pi.single_apply]

/-- A spanning condition forces rigidity: if the (unchanged, non-V) rows of F together with the unit
vectors of the non-G0 coordinates span everything, then a G0-block prefix that fixes those rows is 1. -/
theorem rigid_of_span (G0 : Reg → Prop) (T : Set Reg) (F : Matrix Reg Reg K)
    (hspan : Submodule.span K ((fun x => F x) '' T ∪
      Set.range (fun k : {k // ¬ G0 k} => (Pi.single k.1 (1 : K) : Reg → K))) = ⊤)
    (M : Matrix Reg Reg K) (hM : Blk G0 M) (hfix : ∀ x ∈ T, (F * M) x = F x) : M = 1 := by
  let φ : (Reg → K) →ₗ[K] (Reg → K) := Matrix.vecMulLinear M - LinearMap.id
  have hle : Submodule.span K ((fun x => F x) '' T ∪
      Set.range (fun k : {k // ¬ G0 k} => (Pi.single k.1 (1 : K) : Reg → K))) ≤
      LinearMap.ker φ := by
    rw [Submodule.span_le]
    rintro v (⟨x, hx, rfl⟩ | ⟨k, rfl⟩)
    · have := hfix x hx
      simp only [SetLike.mem_coe, LinearMap.mem_ker, φ, LinearMap.sub_apply,
        Matrix.vecMulLinear_apply, LinearMap.id_apply, sub_eq_zero]
      funext j
      have := congrFun this j
      simpa [Matrix.mul_apply, Matrix.vecMul, dotProduct] using this
    · simp only [SetLike.mem_coe, LinearMap.mem_ker, φ, LinearMap.sub_apply,
        Matrix.vecMulLinear_apply, LinearMap.id_apply, sub_eq_zero]
      rw [single_vecMul]
      funext j
      have := hM k.1 j (fun h => k.2 h.1)
      simp only [Matrix.one_apply] at this
      rw [this]
      simp [Pi.single_apply, eq_comm]
  have hall : ∀ v, φ v = 0 := fun v => hle (by rw [hspan]; trivial)
  ext i k
  have := congrFun (hall (Pi.single i 1)) k
  simp only [φ, LinearMap.sub_apply, Matrix.vecMulLinear_apply, LinearMap.id_apply,
    Pi.sub_apply, single_vecMul] at this
  simp only [Matrix.one_apply]
  simp only [Pi.zero_apply, Pi.single_apply] at this
  have h3 := sub_eq_zero.1 this
  rw [h3]; simp [eq_comm]

end Rigid

section Iff
variable {K Reg : Type*} [Field K] [Fintype Reg] [DecidableEq Reg] (h1 h2 : Reg)
local notation "σ" => Equiv.swap h1 h2

/-- (1), tail swap: undone iff both helpers end in V (under rigidity of the {0}-prefix). -/
theorem tail_iff (V G0 : Reg → Prop) (hne : h1 ≠ h2) (F : Matrix Reg Reg K)
    (hF1 : F h1 = Pi.single h1 1) (hF2 : F h2 = Pi.single h2 1)
    (hrig : ∀ M : Matrix Reg Reg K, Blk G0 M →
      (∀ x, x ≠ h1 → x ≠ h2 → ¬ V x → (F * M) x = F x) → M = 1) :
    Undo V G0 F (rowSw σ F) ↔ V h1 ∧ V h2 :=
  ⟨tail_only_if h1 h2 V G0 hne F hF1 hF2 hrig, fun ⟨a, b⟩ => tail_if h1 h2 V G0 F a b⟩

/-- (1), head swap: undone iff both helpers are born in {0} (when some non-V row separates h1, h2). -/
theorem head_iff (V G0 : Reg → Prop) (hne : h1 ≠ h2) (F : Matrix Reg Reg K)
    (hw : ∃ x, ¬ V x ∧ F x h1 ≠ F x h2) :
    Undo V G0 F (colSw σ F) ↔ G0 h1 ∧ G0 h2 :=
  ⟨head_only_if h1 h2 V G0 hne F hw, fun ⟨a, b⟩ => head_if h1 h2 V G0 F a b⟩

/-- Tail swap, spanning form of the rigidity hypothesis. -/
theorem tail_iff_span (V G0 : Reg → Prop) (hne : h1 ≠ h2) (F : Matrix Reg Reg K)
    (hF1 : F h1 = Pi.single h1 1) (hF2 : F h2 = Pi.single h2 1)
    (hspan : Submodule.span K ((fun x => F x) '' {x | x ≠ h1 ∧ x ≠ h2 ∧ ¬ V x} ∪
      Set.range (fun k : {k // ¬ G0 k} => (Pi.single k.1 (1 : K) : Reg → K))) = ⊤) :
    Undo V G0 F (rowSw σ F) ↔ V h1 ∧ V h2 :=
  tail_iff h1 h2 V G0 hne F hF1 hF2 fun M hM hfix =>
    rigid_of_span G0 _ F hspan M hM fun x hx => hfix x hx.1 hx.2.1 hx.2.2

lemma colSw_one (V : Reg → Prop) : colSw σ (1 : Matrix Reg Reg K) = rowSw σ 1 := by
  ext i k
  have : (σ i = k) ↔ (i = σ k) :=
    ⟨fun h => by rw [← h, swap_inv], fun h => by rw [h, swap_inv]⟩
  simp [colSw, rowSw, Matrix.one_apply, this]

end Iff

/-! ### Part C: ladder cost -/
section Ladder
open JunkLB2 RelaySandwich

/-- A helper's trajectory: birth dim `b`, end dim `e`, stay gaps before (`pre`) and after (`suf`) the
shared chart. -/
structure Traj where
  b : ℝ
  e : ℝ
  pre : List ℝ
  suf : List ℝ

/-- Per-helper ladder cost: span term minus the sum over stays (RelaySandwich.stopCost's accounting). -/
noncomputable def Traj.cost (f : ℝ → ℝ) (t : Traj) : ℝ :=
  f (t.e - t.b) - ((t.pre ++ t.suf).map f).sum

/-- Both helpers sit at the shared chart (dim `s`) and their gaps add up. -/
def Traj.Wf (s : ℝ) (t : Traj) : Prop := t.b + t.pre.sum = s ∧ s + t.suf.sum = t.e

/-- The swap (tail or head: same pair of trajectories, only the names differ). -/
def Traj.swap (t1 t2 : Traj) : Traj × Traj :=
  (⟨t1.b, t2.e, t1.pre, t2.suf⟩, ⟨t2.b, t1.e, t2.pre, t1.suf⟩)

theorem swap_wf (s : ℝ) (t1 t2 : Traj) (a : t1.Wf s) (b : t2.Wf s) :
    (Traj.swap t1 t2).1.Wf s ∧ (Traj.swap t1 t2).2.Wf s :=
  ⟨⟨a.1, b.2⟩, ⟨b.1, a.2⟩⟩

/-- The multiset of stays is unchanged. -/
theorem stays_multiset (t1 t2 : Traj) :
    ((↑((Traj.swap t1 t2).1.pre ++ (Traj.swap t1 t2).1.suf ++
        ((Traj.swap t1 t2).2.pre ++ (Traj.swap t1 t2).2.suf)) : Multiset ℝ)) =
      ↑(t1.pre ++ t1.suf ++ (t2.pre ++ t2.suf)) := by
  simp only [Traj.swap, ← Multiset.coe_add]
  abel

theorem cost_stopCost (f : ℝ → ℝ) (e : ℝ) (k : ℕ) :
    Traj.cost f ⟨0, e, List.replicate (k + 1) (e / (k + 1)), []⟩ = stopCost f e k := by
  simp [Traj.cost, stopCost, List.map_replicate]

/-- (2): the ladder change is exactly the rectangle difference of the span terms. -/
theorem delta_eq (f : ℝ → ℝ) (t1 t2 : Traj) :
    (Traj.swap t1 t2).1.cost f + (Traj.swap t1 t2).2.cost f - (t1.cost f + t2.cost f) =
      (f (t2.e - t1.b) + f (t1.e - t2.b)) - (f (t1.e - t1.b) + f (t2.e - t2.b)) := by
  simp only [Traj.cost, Traj.swap, List.map_append, List.sum_append]
  ring

/-- Both helpers end in V (same dim): ladder change 0. -/
theorem delta_zero_end (f : ℝ → ℝ) (t1 t2 : Traj) (h : t1.e = t2.e) :
    (Traj.swap t1 t2).1.cost f + (Traj.swap t1 t2).2.cost f - (t1.cost f + t2.cost f) = 0 := by
  rw [delta_eq, h]; ring

/-- Both helpers born in {0} (same dim 0): ladder change 0. -/
theorem delta_zero_birth (f : ℝ → ℝ) (t1 t2 : Traj) (h : t1.b = t2.b) :
    (Traj.swap t1 t2).1.cost f + (Traj.swap t1 t2).2.cost f - (t1.cost f + t2.cost f) = 0 := by
  rw [delta_eq, h]; ring

end Ladder

/-! ### Part D: the law and the converse witness -/
section Law
open JunkLB2

variable {K Reg : Type*} [Field K] [Fintype Reg] [DecidableEq Reg] (h1 h2 : Reg)
local notation "σ" => Equiv.swap h1 h2

/-- SWAP-NULL: a legal (hub-undoable) swap has ladder change 0 (ends of V-enders share the dim of V,
{0}-born helpers share dim 0). -/
theorem swap_null (f : ℝ → ℝ) (V G0 : Reg → Prop) (dV : ℝ) (t1 t2 : Traj) (hne : h1 ≠ h2)
    (hV1 : V h1 → t1.e = dV) (hV2 : V h2 → t2.e = dV)
    (hG1 : G0 h1 → t1.b = 0) (hG2 : G0 h2 → t2.b = 0)
    (hu : Undo V G0 (1 : Matrix Reg Reg K) (rowSw σ 1)) :
    (Traj.swap t1 t2).1.cost f + (Traj.swap t1 t2).2.cost f - (t1.cost f + t2.cost f) = 0 := by
  rcases (undo_one_iff h1 h2 V G0 hne).1 hu with ⟨a, b⟩ | ⟨a, b⟩
  · exact delta_zero_end f t1 t2 ((hV1 a).trans (hV2 b).symm)
  · exact delta_zero_birth f t1 t2 ((hG1 a).trans (hG2 b).symm)

/-- (3), contrapositive: a nonzero ladder change cannot be hub-undone. -/
theorem nonzero_not_undoable (f : ℝ → ℝ) (V G0 : Reg → Prop) (dV : ℝ) (t1 t2 : Traj)
    (hne : h1 ≠ h2)
    (hV1 : V h1 → t1.e = dV) (hV2 : V h2 → t2.e = dV)
    (hG1 : G0 h1 → t1.b = 0) (hG2 : G0 h2 → t2.b = 0)
    (hd : (Traj.swap t1 t2).1.cost f + (Traj.swap t1 t2).2.cost f - (t1.cost f + t2.cost f) ≠ 0) :
    ¬ Undo V G0 (1 : Matrix Reg Reg K) (rowSw σ 1) :=
  fun hu => hd (swap_null (K := K) h1 h2 f V G0 dV t1 t2 hne hV1 hV2 hG1 hG2 hu)

/-- The numerical core: 7 ln 7 + 4 ln 4 < 2 ln 2 + 9 ln 9. -/
theorem witness_num : fL (9 - 5) + fL (7 - 0) - (fL (7 - 5) + fL (9 - 0)) < 0 := by
  have h : (7 : ℝ) * Real.log 7 + 6 * Real.log 2 < 18 * Real.log 3 := by
    have := Real.log_lt_log (by positivity : (0 : ℝ) < 7 ^ 7 * 2 ^ 6) (by norm_num : (7 : ℝ) ^ 7 * 2 ^ 6 < 3 ^ 18)
    rw [Real.log_mul (by positivity) (by positivity), Real.log_pow, Real.log_pow, Real.log_pow] at this
    push_cast at this
    exact this
  have h4 : Real.log 4 = 2 * Real.log 2 := by
    rw [show (4 : ℝ) = 2 ^ 2 by norm_num, Real.log_pow]; norm_num
  have h9 : Real.log 9 = 2 * Real.log 3 := by
    rw [show (9 : ℝ) = 3 ^ 2 by norm_num, Real.log_pow]; norm_num
  unfold fL
  norm_num
  rw [h4, h9]
  linarith

end Law

/-- Concrete witness (Reg = Fin 2; helper 0 born dim 5, ends dim 7, in neither hub; helper 1 born {0},
ends in V of dim 9; shared chart dim 6). Its ladder change is strictly negative (f = r ln r, about
-1.995), and the swap, tail or head, cannot be undone by any V mix and {0}-prefix. -/
theorem converse_witness :
    let t1 : Traj := ⟨5, 7, [1], [1]⟩
    let t2 : Traj := ⟨0, 9, [6], [3]⟩
    t1.Wf 6 ∧ t2.Wf 6 ∧
    ((Traj.swap t1 t2).1.cost JunkLB2.fL + (Traj.swap t1 t2).2.cost JunkLB2.fL
        - (t1.cost JunkLB2.fL + t2.cost JunkLB2.fL) < 0) ∧
    ¬ Undo (fun r : Fin 2 => r = 1) (fun r : Fin 2 => r = 1) (1 : Matrix (Fin 2) (Fin 2) ℚ)
        (rowSw (Equiv.swap 0 1) 1) ∧
    ¬ Undo (fun r : Fin 2 => r = 1) (fun r : Fin 2 => r = 1) (1 : Matrix (Fin 2) (Fin 2) ℚ)
        (colSw (Equiv.swap 0 1) 1) := by
  intro t1 t2
  have hne : (0 : Fin 2) ≠ 1 := by decide
  have hn : ¬ Undo (fun r : Fin 2 => r = 1) (fun r : Fin 2 => r = 1) (1 : Matrix (Fin 2) (Fin 2) ℚ)
      (rowSw (Equiv.swap 0 1) 1) := by
    rw [undo_one_iff 0 1 _ _ hne]; decide
  refine ⟨by norm_num [Traj.Wf, t1], by norm_num [Traj.Wf, t2], ?_, hn, ?_⟩
  · rw [delta_eq]
    simpa [t1, t2] using witness_num
  · rw [colSw_one 0 1 (fun r : Fin 2 => r = 1)]; exact hn

/-- Scope of the per-kind iff: with identity finals and both helpers in G0 but not in V, the TAIL
swap IS undone (by the prefix), so "tail swap legal iff both end in V" needs the rigidity hypothesis. -/
theorem tail_prefix_counterexample :
    Undo (fun _ : Fin 2 => False) (fun _ : Fin 2 => True) (1 : Matrix (Fin 2) (Fin 2) ℚ)
        (rowSw (Equiv.swap 0 1) 1) ∧ ¬ (False ∧ False) := by
  refine ⟨?_, by simp⟩
  rw [undo_one_iff 0 1 _ _ (by decide)]; simp

#print axioms tail_run
#print axioms head_run
#print axioms gadget_legal
#print axioms tail_iff
#print axioms tail_iff_span
#print axioms head_iff
#print axioms undo_one_iff
#print axioms delta_eq
#print axioms swap_null
#print axioms converse_witness
#print axioms tail_prefix_counterexample
#print axioms stays_multiset
#print axioms cost_stopCost

end SwapNull
