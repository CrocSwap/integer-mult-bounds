/-
Lemma A, scheduling: whole invocations, no other actor, and borrowed pending blocks.
Apache-2.0.  Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.

A global state is `y : Φ → W` (one value per physical family).  An action is a map on global
states; `Supported A S` says that `A` changes only families in `S` and reads only families in
`S`.  Words of actions are applied left to right (`evalW`).

* `commute_of_disjoint`  actions with disjoint supports commute.
* `shuffle_eval`         an interleaving of two pairwise commuting words is their concatenation.
* `whole_invocation`     the realized events of an invocation, interleaved with actions that
                         touch none of its families, act as the complete invocation followed by
                         those actions ("no other actor").
* `split_off`            an endpoint that acts on family `f` alone, and that no other family
                         reads, splits into a piece supported on `{f}` and a rest that does not
                         touch `f`.
* `defer`, `async_window` a piece on `f` moves past every action that commutes with it, in
                         particular every action not touching `f`; the pieces of one pending
                         child, gathered before its deadline, give the child (#505).
-/
import LemmaA.Realize
import Mathlib.Data.Set.Disjoint

namespace LemmaA

variable {Φ W : Type*}

/-- `A` changes only families in `S`, and its values on `S` depend only on the input on `S`. -/
def Supported (A : (Φ → W) → (Φ → W)) (S : Set Φ) : Prop :=
  (∀ y f, f ∉ S → A y f = y f) ∧ (∀ y y', (∀ f ∈ S, y f = y' f) → ∀ f ∈ S, A y f = A y' f)

theorem Supported.mono {A : (Φ → W) → (Φ → W)} {S T : Set Φ} (h : Supported A S) (hST : S ⊆ T) :
    Supported A T := by
  refine ⟨fun y f hf => h.1 y f (fun hs => hf (hST hs)), fun y y' hyy f hf => ?_⟩
  by_cases hfS : f ∈ S
  · exact h.2 y y' (fun g hg => hyy g (hST hg)) f hfS
  · rw [h.1 y f hfS, h.1 y' f hfS]; exact hyy f hf

/-- **Disjoint supports commute.** -/
theorem commute_of_disjoint {A B : (Φ → W) → (Φ → W)} {S T : Set Φ} (hA : Supported A S)
    (hB : Supported B T) (h : Disjoint S T) : A ∘ B = B ∘ A := by
  funext y f
  simp only [Function.comp]
  by_cases hfS : f ∈ S
  · have hfT : f ∉ T := Set.disjoint_left.1 h hfS
    rw [hB.1 (A y) f hfT]
    exact hA.2 (B y) y (fun g hg => hB.1 y g (Set.disjoint_left.1 h hg)) f hfS
  · rw [hA.1 (B y) f hfS]
    by_cases hfT : f ∈ T
    · exact hB.2 y (A y) (fun g hg => (hA.1 y g (Set.disjoint_right.1 h hg)).symm) f hfT
    · rw [hB.1 y f hfT, hB.1 (A y) f hfT, hA.1 y f hfS]

/-- Apply a word of actions, first element first. -/
def evalW : List ((Φ → W) → (Φ → W)) → (Φ → W) → (Φ → W)
  | [] => id
  | a :: as => evalW as ∘ a

theorem evalW_append : ∀ (as bs : List ((Φ → W) → (Φ → W))),
    evalW (as ++ bs) = evalW bs ∘ evalW as
  | [], _ => rfl
  | a :: as, bs => by simp only [List.cons_append, evalW, evalW_append as bs]; rfl

/-- An action that commutes with every element of a word commutes with the word. -/
theorem evalW_comm (U : (Φ → W) → (Φ → W)) : ∀ (as : List ((Φ → W) → (Φ → W))),
    (∀ a ∈ as, a ∘ U = U ∘ a) → evalW as ∘ U = U ∘ evalW as
  | [], _ => rfl
  | a :: as, h => by
    simp only [evalW]
    rw [Function.comp_assoc, h a List.mem_cons_self, ← Function.comp_assoc,
      evalW_comm U as (fun b hb => h b (List.mem_cons_of_mem _ hb)), Function.comp_assoc]

/-- **Deferral.**  A piece moves to the right past every action that commutes with it. -/
theorem defer (U : (Φ → W) → (Φ → W)) (xs ys zs : List ((Φ → W) → (Φ → W)))
    (h : ∀ a ∈ ys, a ∘ U = U ∘ a) :
    evalW (xs ++ U :: ys ++ zs) = evalW (xs ++ ys ++ U :: zs) := by
  simp only [evalW_append, List.append_assoc, List.cons_append, evalW]
  funext y
  exact congrArg (evalW zs) (congrFun (evalW_comm U ys h) (evalW xs y))

/-- `us` interleaves `as` and `bs`, keeping the order within each. -/
inductive Interleave {α : Type*} : List α → List α → List α → Prop
  | nil : Interleave [] [] []
  | left {a as bs us} : Interleave as bs us → Interleave (a :: as) bs (a :: us)
  | right {b as bs us} : Interleave as bs us → Interleave as (b :: bs) (b :: us)

/-- **Shuffles of commuting words.**  If every action of `as` commutes with every action of
`bs`, any interleaving evaluates to `as` followed by `bs`. -/
theorem shuffle_eval {as bs us : List ((Φ → W) → (Φ → W))}
    (hc : ∀ a ∈ as, ∀ b ∈ bs, a ∘ b = b ∘ a) (h : Interleave as bs us) :
    evalW us = evalW (as ++ bs) := by
  induction h with
  | nil => rfl
  | @left a as bs us _ ih =>
    simp only [evalW, List.cons_append]
    rw [ih (fun x hx y hy => hc x (List.mem_cons_of_mem _ hx) y hy)]
  | @right b as bs us _ ih =>
    have ih' := ih (fun x hx y hy => hc x hx y (List.mem_cons_of_mem _ hy))
    have hb := evalW_comm b as (fun x hx => hc x hx b List.mem_cons_self)
    funext y
    show evalW us (b y) = evalW (as ++ b :: bs) y
    rw [ih', evalW_append, evalW_append]
    show evalW bs (evalW as (b y)) = evalW bs (b (evalW as y))
    exact congrArg (evalW bs) (congrFun hb y)

/-! ### Whole invocation, no other actor -/

section Whole

open LemmaG

variable {ι Λ K M : Type*} [DecidableEq ι] [DecidableEq Φ] [Semiring K]
variable [AddCommMonoid W] [Module K W] [AddCommMonoid M] [Module K M]

/-- A realized event touches only families that host registers of the invocation. -/
theorem realize_supported (σ : Hosting ι Φ K W M) (rec : Λ → Λ → M → M) (e : Event ι Λ K) :
    Supported (realize σ rec e) (Set.range σ.own) := by
  refine ⟨fun y f hf => ?_, fun y y' hyy f _ => ?_⟩
  · exact Function.update_of_ne (fun h => hf ⟨_, h.symm⟩) _ _
  · have hv : view σ y = view σ y' := funext fun i => by simp [view, hyy (σ.own i) ⟨i, rfl⟩]
    by_cases hf : f = σ.own (dst e)
    · subst hf; simp [realize, hv]
    · simp [realize, Function.update_of_ne hf, hyy f ‹_›]

theorem realizeRun_eq_evalW (σ : Hosting ι Φ K W M) (rec : Λ → Λ → M → M) :
    ∀ es : List (Event ι Λ K), realizeRun σ rec es = evalW (es.map (realize σ rec))
  | [] => rfl
  | e :: es => by
    funext y
    simp only [realizeRun, List.map_cons, evalW, Function.comp, realizeRun_eq_evalW σ rec es]

/-- **Whole invocation, no other actor.**  Interleave the realized events of an invocation with
foreign actions, each supported on a set that contains no family of the invocation.  The result
is the complete invocation followed by the foreign actions; with one owner, the invocation part
is the local run read through the charts (`realize_run`). -/
theorem whole_invocation (σ : Hosting ι Φ K W M) (rec : Λ → Λ → M → M) (es : List (Event ι Λ K))
    (foreign us : List ((Φ → W) → (Φ → W)))
    (hfor : ∀ b ∈ foreign, ∃ T : Set Φ, Supported b T ∧ Disjoint (Set.range σ.own) T)
    (hint : Interleave (es.map (realize σ rec)) foreign us) :
    evalW us = evalW foreign ∘ realizeRun σ rec es := by
  rw [shuffle_eval _ hint, evalW_append, realizeRun_eq_evalW]
  intro a ha b hb
  obtain ⟨e, -, rfl⟩ := List.mem_map.1 ha
  obtain ⟨T, hbT, hdis⟩ := hfor b hb
  exact commute_of_disjoint (realize_supported σ rec e) hbT hdis

end Whole

/-! ### Borrowed pending blocks (#505) -/

section Async

variable [DecidableEq Φ]

/-- **Split off a single-family piece.**  If an endpoint `E` acts on family `f` as the piece `P`
(supported on `{f}`) and no other family's value depends on `f`, then `E` is "the rest, then
`P`", where the rest leaves `f` alone and does not read it. -/
theorem split_off (E P : (Φ → W) → (Φ → W)) (f : Φ) (hP : Supported P {f})
    (hEf : ∀ y, E y f = P y f)
    (hread : ∀ y w g, g ≠ f → E (Function.update y f w) g = E y g) :
    E = P ∘ (fun y => Function.update (E y) f (y f)) ∧
      Supported (fun y => Function.update (E y) f (y f)) {f}ᶜ := by
  refine ⟨?_, ?_, ?_⟩
  · funext y g
    simp only [Function.comp]
    by_cases hg : g = f
    · subst hg
      rw [hEf]
      exact hP.2 y _ (fun h hh => by rw [Set.mem_singleton_iff.1 hh]; simp) g rfl
    · rw [hP.1 _ g (by simpa using hg), Function.update_of_ne hg]
  · intro y g hg
    simp only [Set.mem_compl_iff, Set.mem_singleton_iff, not_not] at hg
    subst hg; simp
  · intro y y' hyy g hg
    simp only [Set.mem_compl_iff, Set.mem_singleton_iff] at hg
    have hy' : y' = Function.update y f (y' f) := by
      funext h
      by_cases hh : h = f
      · subst hh; simp
      · rw [Function.update_of_ne hh]; exact (hyy h hh).symm
    show Function.update (E y) f (y f) g = Function.update (E y') f (y' f) g
    rw [Function.update_of_ne hg, Function.update_of_ne hg, hy', hread y (y' f) g hg]

omit [DecidableEq Φ] in
/-- A piece on `{f}` commutes with every action that does not touch `f`. -/
theorem commute_of_not_mem {P A : (Φ → W) → (Φ → W)} {f : Φ} {S : Set Φ}
    (hP : Supported P {f}) (hA : Supported A S) (hf : f ∉ S) : A ∘ P = P ∘ A :=
  (commute_of_disjoint hP hA (Set.disjoint_singleton_left.2 hf)).symm

/-- **Borrowed pending block, asynchronous window (#505).**  An invocation endpoint `E` acts on
the owner family `f` as the piece `P` and nothing else reads `f`.  If every action between the
invocation and the pending child's deadline commutes with `P` (it does not touch `f`, or it is
another piece of the same child on a disjoint block), the schedule equals the one in which the
rest of the invocation runs in place and `P` runs just before the deadline. -/
theorem async_window (E P : (Φ → W) → (Φ → W)) (f : Φ) (hP : Supported P {f})
    (hEf : ∀ y, E y f = P y f)
    (hread : ∀ y w g, g ≠ f → E (Function.update y f w) g = E y g)
    (xs ys zs : List ((Φ → W) → (Φ → W))) (hys : ∀ a ∈ ys, a ∘ P = P ∘ a) :
    evalW (xs ++ E :: ys ++ zs) =
      evalW (xs ++ (fun y => Function.update (E y) f (y f)) :: ys ++ P :: zs) := by
  obtain ⟨hsplit, -⟩ := split_off E P f hP hEf hread
  have h1 : evalW (xs ++ E :: ys ++ zs) =
      evalW ((xs ++ [fun y => Function.update (E y) f (y f)]) ++ P :: ys ++ zs) := by
    simp only [evalW_append, List.append_assoc, List.cons_append, List.singleton_append, evalW]
    conv_lhs => rw [hsplit]
    rfl
  rw [h1, defer P _ ys zs hys]
  simp

omit [DecidableEq Φ] in
/-- **Gathering.**  Pieces whose product is the pending child can be replaced by the child. -/
theorem gather (ps : List ((Φ → W) → (Φ → W))) (C : (Φ → W) → (Φ → W)) (h : evalW ps = C)
    (xs zs : List ((Φ → W) → (Φ → W))) : evalW (xs ++ ps ++ zs) = evalW (xs ++ C :: zs) := by
  simp only [evalW_append, List.cons_append, evalW, h]
  rfl

end Async

end LemmaA
