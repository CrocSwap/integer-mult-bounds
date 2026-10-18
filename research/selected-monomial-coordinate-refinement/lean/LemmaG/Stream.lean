/-
Lemma G, semantic part: the common-frame conjugation lemma for labelled event streams.
Apache-2.0.  Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.

A register file is a function `ι → M`.  Every register also carries a label in `Λ`
(a frame, possibly tagged by its conversion phase; see PROOF.md §1).  A family
`T : Λ → M ≃ₗ[K] M` of linear automorphisms gives each label its operator.  The
physical program executes the events below; the label program tracks the labels; the
scalar shadow is the same program with every relabel deleted.

Main results:
* `Stream.conj`        physical run = D(λ¹) ∘ scalar shadow ∘ D(λ⁰)⁻¹ (operator form);
* `Stream.conj_matrix` the same with the scalar shadow written as its matrix `S`;
* `Stream.row_unit`, `Stream.row_pair`  the two row shapes used by the word.
Nothing about the field, the frames or the operators is used beyond: `K` is a semiring,
`M` a `K`-module, every `T F` is a `K`-linear bijection.
-/
import Mathlib.Algebra.Module.Equiv.Defs
import Mathlib.Algebra.Module.Pi
import Mathlib.Algebra.BigOperators.Pi
import Mathlib.Algebra.Module.LinearMap.Basic
import Mathlib.LinearAlgebra.Span.Basic

namespace LemmaG

/-- The events of an emitted local program (PROOF.md §1.1).  `relabel r A B` covers climbs,
centre steps, data adapters and residual wrappers: the register `r` moves from label `A`
to label `B` and the hardware executes a fixed recipe. -/
inductive Event (ι Λ K : Type*) where
  | relabel (r : ι) (A B : Λ)
  | add (t s : ι) (q : K)
  | scale (t : ι) (q : K)
  | copy (c r : ι) (F : Λ)
  | clear (c : ι) (F : Λ)

namespace Event

variable {ι Λ K : Type*} [DecidableEq ι]

section Semantics

variable [Semiring K] {M : Type*} [AddCommMonoid M] [Module K M]

/-- Physical effect.  `rec A B` is the operator the hardware executes for `relabel _ A B`
(the serialized recipe). -/
def phys (rec : Λ → Λ → M → M) : Event ι Λ K → (ι → M) → (ι → M)
  | relabel r A B, h => Function.update h r (rec A B (h r))
  | add t s q, h => Function.update h t (h t + q • h s)
  | scale t q, h => Function.update h t (q • h t)
  | copy c r _, h => Function.update h c (h r)
  | clear c _, h => Function.update h c 0

/-- Scalar shadow: the same event with the frames stripped (a relabel does nothing). -/
def scal (e : Event ι Λ K) : (ι → M) → (ι → M) := e.phys (fun _ _ v => v)

end Semantics

/-- Label effect. -/
def lab : Event ι Λ K → (ι → Λ) → (ι → Λ)
  | relabel r _ B, l => Function.update l r B
  | copy c _ F, l => Function.update l c F
  | clear c F, l => Function.update l c F
  | add .., l => l
  | scale .., l => l

/-- The label condition of one event (clause G0 together with the source label of a
relabel).  This is the whole hypothesis on the labels. -/
def Admissible : Event ι Λ K → (ι → Λ) → Prop
  | relabel r A _, l => l r = A
  | add t s _, l => l t = l s
  | copy _ r F, l => l r = F
  | scale .., _ => True
  | clear .., _ => True

/-- The registers an event can relabel. -/
def moves : Event ι Λ K → ι → Prop
  | relabel r _ _, i => i = r
  | copy c _ _, i => i = c
  | clear c _, i => i = c
  | add .., _ => False
  | scale .., _ => False

end Event

namespace Stream

open Event

variable {ι Λ K : Type*} [DecidableEq ι] [Semiring K]
variable {M : Type*} [AddCommMonoid M] [Module K M]

/-- Run a list of events physically (left to right). -/
def physRun (rec : Λ → Λ → M → M) : List (Event ι Λ K) → (ι → M) → (ι → M)
  | [], h => h
  | e :: es, h => physRun rec es (e.phys rec h)

/-- The scalar shadow of a stream. -/
def scalRun (es : List (Event ι Λ K)) : (ι → M) → (ι → M) := physRun (fun _ _ v => v) es

/-- The labels after a stream. -/
def labRun : List (Event ι Λ K) → (ι → Λ) → (ι → Λ)
  | [], l => l
  | e :: es, l => labRun es (e.lab l)

/-- Every event is admissible at the labels current when it runs. -/
def WellLabelled : List (Event ι Λ K) → (ι → Λ) → Prop
  | [], _ => True
  | e :: es, l => e.Admissible l ∧ WellLabelled es (e.lab l)

/-- Every relabel of the stream executes exactly `T B ∘ (T A)⁻¹`. -/
def RecipesExact (T : Λ → M ≃ₗ[K] M) (rec : Λ → Λ → M → M) (es : List (Event ι Λ K)) : Prop :=
  ∀ r A B, Event.relabel r A B ∈ es → ∀ v, rec A B v = T B ((T A).symm v)

/-- Register-wise label operator `D(λ)`. -/
def D (T : Λ → M ≃ₗ[K] M) (l : ι → Λ) (x : ι → M) : ι → M := fun r => T (l r) (x r)

/-- Its inverse `D(λ)⁻¹`. -/
def Dinv (T : Λ → M ≃ₗ[K] M) (l : ι → Λ) (h : ι → M) : ι → M := fun r => (T (l r)).symm (h r)

omit [DecidableEq ι] in
theorem D_Dinv (T : Λ → M ≃ₗ[K] M) (l : ι → Λ) (h : ι → M) : D T l (Dinv T l h) = h := by
  funext r; simp [D, Dinv]

/-- One step of the invariant `h = D(λ) ℓ`. -/
theorem step (T : Λ → M ≃ₗ[K] M) (rec : Λ → Λ → M → M) (e : Event ι Λ K) (l : ι → Λ)
    (x : ι → M) (hrec : ∀ r A B, e = Event.relabel r A B → ∀ v, rec A B v = T B ((T A).symm v))
    (ha : e.Admissible l) :
    e.phys rec (D T l x) = D T (e.lab l) (e.scal x) := by
  cases e with
  | relabel r A B =>
    have hr := hrec r A B rfl
    simp only [Admissible] at ha
    funext i
    by_cases hi : i = r
    · subst hi; simp [phys, scal, lab, D, hr, ha]
    · simp [phys, scal, lab, D, Function.update_of_ne hi]
  | add t s q =>
    simp only [Admissible] at ha
    funext i
    by_cases hi : i = t
    · subst hi; simp [phys, scal, lab, D, ha]
    · simp [phys, scal, lab, D, Function.update_of_ne hi]
  | scale t q =>
    funext i
    by_cases hi : i = t
    · subst hi; simp [phys, scal, lab, D]
    · simp [phys, scal, lab, D, Function.update_of_ne hi]
  | copy c r F =>
    simp only [Admissible] at ha
    funext i
    by_cases hi : i = c
    · subst hi; simp [phys, scal, lab, D, ha]
    · simp [phys, scal, lab, D, Function.update_of_ne hi]
  | clear c F =>
    funext i
    by_cases hi : i = c
    · subst hi; simp [phys, scal, lab, D]
    · simp [phys, scal, lab, D, Function.update_of_ne hi]

/-- **Conjugation lemma (operator form).**  For a well-labelled stream whose relabels execute
`T B ∘ (T A)⁻¹`, the physical program equals `D(λ¹) ∘ (scalar shadow) ∘ D(λ⁰)⁻¹`. -/
theorem conj (T : Λ → M ≃ₗ[K] M) (rec : Λ → Λ → M → M) :
    ∀ (es : List (Event ι Λ K)) (l : ι → Λ) (x : ι → M),
      RecipesExact T rec es → WellLabelled es l →
        physRun rec es (D T l x) = D T (labRun es l) (scalRun es x)
  | [], _, _, _, _ => rfl
  | e :: es, l, x, hrec, hw => by
    have h1 := step T rec e l x
      (fun r A B he v => hrec r A B (he ▸ List.mem_cons_self ..) v) hw.1
    have h2 := conj T rec es (e.lab l) (e.scal x)
      (fun r A B hm v => hrec r A B (List.mem_cons_of_mem _ hm) v) hw.2
    simp only [physRun, scalRun, labRun] at h2 ⊢
    rw [h1, h2]
    rfl

theorem conj' (T : Λ → M ≃ₗ[K] M) (rec : Λ → Λ → M → M) (es : List (Event ι Λ K))
    (l : ι → Λ) (h : ι → M) (hrec : RecipesExact T rec es) (hw : WellLabelled es l) :
    physRun rec es h = D T (labRun es l) (scalRun es (Dinv T l h)) := by
  rw [← conj T rec es l _ hrec hw, D_Dinv]

/-! ### The scalar shadow is a matrix -/

section Matrix

variable {N : Type*} [AddCommMonoid N] [Module K N]

theorem scal_map (φ : M →ₗ[K] N) (e : Event ι Λ K) (x : ι → M) :
    e.scal (fun i => φ (x i)) = fun i => φ (e.scal x i) := by
  funext i
  cases e with
  | relabel r A B => by_cases hi : i = r <;> simp [scal, phys, Function.update_apply, hi]
  | add t s q => by_cases hi : i = t <;> simp [scal, phys, Function.update_apply, hi]
  | scale t q => by_cases hi : i = t <;> simp [scal, phys, Function.update_apply, hi]
  | copy c r F => by_cases hi : i = c <;> simp [scal, phys, Function.update_apply, hi]
  | clear c F => by_cases hi : i = c <;> simp [scal, phys, Function.update_apply, hi]

theorem scalRun_map (φ : M →ₗ[K] N) :
    ∀ (es : List (Event ι Λ K)) (x : ι → M),
      scalRun es (fun i => φ (x i)) = fun i => φ (scalRun es x i)
  | [], _ => rfl
  | e :: es, x => by
    show scalRun es (e.scal (fun i => φ (x i))) = fun i => φ (scalRun es (e.scal x) i)
    rw [scal_map φ e x]
    exact scalRun_map φ es (e.scal x)

theorem scal_add (e : Event ι Λ K) (x y : ι → M) : e.scal (x + y) = e.scal x + e.scal y := by
  funext i
  cases e with
  | relabel r A B => by_cases hi : i = r <;> simp [scal, phys, Function.update_apply, hi]
  | add t s q =>
    by_cases hi : i = t <;> simp [scal, phys, Function.update_apply, hi, smul_add, add_add_add_comm]
  | scale t q => by_cases hi : i = t <;> simp [scal, phys, Function.update_apply, hi, smul_add]
  | copy c r F => by_cases hi : i = c <;> simp [scal, phys, Function.update_apply, hi]
  | clear c F => by_cases hi : i = c <;> simp [scal, phys, Function.update_apply, hi]

theorem scal_zero (e : Event ι Λ K) : e.scal (0 : ι → M) = 0 := by
  funext i
  cases e with
  | relabel r A B => by_cases hi : i = r <;> simp [scal, phys, Function.update_apply, hi]
  | add t s q => by_cases hi : i = t <;> simp [scal, phys, Function.update_apply, hi]
  | scale t q => by_cases hi : i = t <;> simp [scal, phys, Function.update_apply, hi]
  | copy c r F => by_cases hi : i = c <;> simp [scal, phys, Function.update_apply, hi]
  | clear c F => by_cases hi : i = c <;> simp [scal, phys, Function.update_apply, hi]

theorem scalRun_add : ∀ (es : List (Event ι Λ K)) (x y : ι → M),
    scalRun es (x + y) = scalRun es x + scalRun es y
  | [], _, _ => rfl
  | e :: es, x, y => by
    show scalRun es (e.scal (x + y)) = scalRun es (e.scal x) + scalRun es (e.scal y)
    rw [scal_add e x y]
    exact scalRun_add es _ _

theorem scalRun_zero : ∀ (es : List (Event ι Λ K)), scalRun es (0 : ι → M) = 0
  | [] => rfl
  | e :: es => by
    show scalRun es (e.scal (0 : ι → M)) = 0
    rw [scal_zero e]
    exact scalRun_zero es

/-- The scalar shadow as an additive map. -/
def scalHom (es : List (Event ι Λ K)) : (ι → M) →+ (ι → M) where
  toFun := scalRun es
  map_zero' := scalRun_zero es
  map_add' := scalRun_add es

/-- The matrix of the scalar shadow: `S r s` is the coefficient of the input of register `s`
in the output of register `r` (replay over `K` on the basis column `s`). -/
def S (es : List (Event ι Λ K)) (r s : ι) : K := scalRun es (Pi.single s (1 : K)) r

/-- The same matrix, read row-wise from one symbolic replay in which register `i` holds the
basis vector `eᵢ` (this is how the checker `lg_lib.scalar_replay` computes it). -/
theorem S_rowform (es : List (Event ι Λ K)) (r s : ι) :
    scalRun es (fun i => (Pi.single i (1 : K) : ι → K)) r s = S es r s := by
  let ev : (ι → K) →ₗ[K] K :=
    { toFun := fun v => v s
      map_add' := fun _ _ => rfl
      map_smul' := fun _ _ => rfl }
  have h := congrFun (scalRun_map (M := ι → K) (N := K) ev es
    (fun i => (Pi.single i (1 : K) : ι → K))) r
  simp only [ev, LinearMap.coe_mk, AddHom.coe_mk] at h
  rw [← h, S]
  congr 1
  funext i
  by_cases hi : i = s
  · subst hi; simp
  · simp [Pi.single_apply, hi, Ne.symm hi]

variable [Fintype ι]

/-- **The scalar shadow acts on any module through its matrix.** -/
theorem scalRun_eq_sum (es : List (Event ι Λ K)) (x : ι → M) (r : ι) :
    scalRun es x r = ∑ s, S es r s • x s := by
  have hx : x = ∑ s, Pi.single s (x s) := (Finset.univ_sum_single x).symm
  have hcol : ∀ s, scalRun es (Pi.single s (x s)) r = S es r s • x s := by
    intro s
    let φ : K →ₗ[K] M :=
      { toFun := fun k => k • x s
        map_add' := fun a b => add_smul a b (x s)
        map_smul' := fun a b => by simp [mul_smul] }
    have e1 : (Pi.single s (x s) : ι → M) = fun i => φ ((Pi.single s (1 : K) : ι → K) i) := by
      funext i
      by_cases hi : i = s
      · subst hi; simp [φ]
      · simp [φ, Pi.single_apply, hi]
    rw [e1, scalRun_map φ es]
    simp [S, φ]
  calc scalRun es x r = scalHom es x r := rfl
    _ = scalHom es (∑ s, Pi.single s (x s)) r := by rw [← hx]
    _ = ∑ s, scalHom es (Pi.single s (x s)) r := by rw [map_sum, Finset.sum_apply]
    _ = ∑ s, S es r s • x s := Finset.sum_congr rfl (fun s _ => hcol s)

/-- **Conjugation lemma, matrix form (Lemma G (G-ii)).**  For every input `h`,
`h_r(final) = T_{λ¹ r} (∑ₛ S r s • T_{λ⁰ s}⁻¹ hₛ)`. -/
theorem conj_matrix (T : Λ → M ≃ₗ[K] M) (rec : Λ → Λ → M → M) (es : List (Event ι Λ K))
    (l : ι → Λ) (h : ι → M) (hrec : RecipesExact T rec es) (hw : WellLabelled es l) (r : ι) :
    physRun rec es h r = T (labRun es l r) (∑ s, S es r s • (T (l s)).symm (h s)) := by
  rw [conj' T rec es l h hrec hw]
  simp only [D]
  rw [scalRun_eq_sum]
  rfl

/-- A unit row (`S r = eᵣ`): register `r` ends as `T_{λ¹ r} T_{λ⁰ r}⁻¹ hᵣ` and no other input
reaches it.  Sources (forward), targets (backward) and all helpers; for an entering helper
`λ⁰ = E_j`, which is the virtual entrance. -/
theorem row_unit (T : Λ → M ≃ₗ[K] M) (rec : Λ → Λ → M → M) (es : List (Event ι Λ K))
    (l : ι → Λ) (h : ι → M) (hrec : RecipesExact T rec es) (hw : WellLabelled es l) (r : ι)
    (hS : ∀ s, S es r s = if s = r then 1 else 0) :
    physRun rec es h r = T (labRun es l r) ((T (l r)).symm (h r)) := by
  rw [conj_matrix T rec es l h hrec hw r]
  congr 1
  simp [hS, ite_smul]

/-- A paired row (`S r = eᵣ + a·e_{s₀}`): targets (forward, `a = 1`) and sources
(backward, `a = -1`). -/
theorem row_pair (T : Λ → M ≃ₗ[K] M) (rec : Λ → Λ → M → M) (es : List (Event ι Λ K))
    (l : ι → Λ) (h : ι → M) (hrec : RecipesExact T rec es) (hw : WellLabelled es l) (r s₀ : ι)
    (a : K) (hS : ∀ s, S es r s = (if s = r then 1 else 0) + (if s = s₀ then a else 0)) :
    physRun rec es h r =
      T (labRun es l r) ((T (l r)).symm (h r) + a • (T (l s₀)).symm (h s₀)) := by
  rw [conj_matrix T rec es l h hrec hw r]
  congr 1
  simp [hS, add_smul, ite_smul, Finset.sum_add_distrib]

end Matrix

/-! ### Composition facts used by the schedule lemma -/

omit [Semiring K] in
theorem labRun_append : ∀ (a b : List (Event ι Λ K)) (l : ι → Λ),
    labRun (a ++ b) l = labRun b (labRun a l)
  | [], _, _ => rfl
  | _ :: a, b, _ => labRun_append a b _

omit [Semiring K] in
theorem wellLabelled_append : ∀ (a b : List (Event ι Λ K)) (l : ι → Λ),
    WellLabelled (a ++ b) l ↔ WellLabelled a l ∧ WellLabelled b (labRun a l)
  | [], _, _ => by simp [WellLabelled, labRun]
  | e :: a, b, l => by
    simp only [List.cons_append, WellLabelled, labRun]
    rw [wellLabelled_append a b]
    tauto

omit [Semiring K] in
/-- A stream that never relabels register `i` leaves its label unchanged (Claim 3). -/
theorem labRun_untouched : ∀ (es : List (Event ι Λ K)) (l : ι → Λ) (i : ι),
    (∀ e ∈ es, ¬ e.moves i) → labRun es l i = l i
  | [], _, _, _ => rfl
  | e :: es, l, i, h => by
    simp only [labRun]
    rw [labRun_untouched es _ i (fun e' he' => h e' (List.mem_cons_of_mem _ he'))]
    have hi := h e List.mem_cons_self
    cases e <;> simp_all [Event.lab, Event.moves, Function.update_of_ne]

end Stream

end LemmaG
