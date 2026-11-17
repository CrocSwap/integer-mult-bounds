/-
SPEC7/SPEC8 frame-separation law, lane LEAN-NEXT35, Nov 17. See FrameSep.md.
Source: cards/WILD/NEWARCH/SPEC7.md (sec 2, 4), SPEC8.md (sec 2, 4).
Abstract model: frames = submodules of V; a route is a time-indexed frame sequence whose
non-owned (public) steps ascend by inclusion; owned steps are arbitrary.
-/
import Mathlib.LinearAlgebra.Span.Basic
import Mathlib.Algebra.Field.Rat
import Mathlib.Data.Rat.Defs

namespace FrameSep

variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V]

/-- A register's frame history; `owned t` marks step t -> t+1 as an owned MOVE. -/
structure Route (K V : Type*) [Field K] [AddCommGroup V] [Module K V] where
  f : ℕ → Submodule K V
  owned : ℕ → Prop
  pub : ∀ t, ¬ owned t → f t ≤ f (t + 1)

namespace Route
variable (R : Route K V)

/-- public stretch: no owned step in [a,b) -/
def Pub (a b : ℕ) : Prop := ∀ s, a ≤ s → s < b → ¬ R.owned s

theorem pub_mono {a b : ℕ} (hab : a ≤ b) (h : R.Pub a b) : R.f a ≤ R.f b := by
  induction b, hab using Nat.le_induction with
  | base => exact le_rfl
  | succ b hb ih =>
    exact (ih fun s h1 h2 => h s h1 (by omega)).trans (R.pub b (h b hb (by omega)))

theorem persist {u : V} {a b : ℕ} (hab : a ≤ b) (h : R.Pub a b) (hu : u ∈ R.f a) :
    u ∈ R.f b := R.pub_mono hab h hu

/-- First-exit law: leaving a u-containing frame needs an OWNED step that genuinely drops u. -/
theorem exit_owned {u : V} {a b : ℕ} (hab : a ≤ b) (hu : u ∈ R.f a) (hb : u ∉ R.f b) :
    ∃ s, a ≤ s ∧ s < b ∧ R.owned s ∧ u ∈ R.f s ∧ u ∉ R.f (s + 1) := by
  induction b, hab using Nat.le_induction with
  | base => exact absurd hu hb
  | succ b hb' ih =>
    by_cases hb0 : u ∈ R.f b
    · refine ⟨b, hb', by omega, ?_, hb0, hb⟩
      by_contra hno
      exact hb (R.pub b hno hb0)
    · obtain ⟨s, h1, h2, h3, h4, h5⟩ := ih hb0
      exact ⟨s, h1, by omega, h3, h4, h5⟩

/-- A route is public if it has no owned steps. -/
def IsPublic : Prop := ∀ t, ¬ R.owned t

theorem IsPublic.mono {R : Route K V} (h : R.IsPublic) {a b : ℕ} (hab : a ≤ b) :
    R.f a ≤ R.f b := R.pub_mono hab fun s _ _ => h s

theorem IsPublic.persist {R : Route K V} (h : R.IsPublic) {u : V} {a b : ℕ} (hab : a ≤ b)
    (hu : u ∈ R.f a) : u ∈ R.f b := h.mono hab hu

end Route

/-- SPEC7 core: X contains u at the start of a public route, Y's frames lie in W with u ∉ W.
  Then X's frames never equal Y's frames. -/
theorem X_Y_never_share (X Y : Route K V) (u : V) (W : Submodule K V) (hu : u ∉ W)
    (hX : X.IsPublic) (hX0 : u ∈ X.f 0) (hY : ∀ t, Y.f t ≤ W) (s t : ℕ) :
    X.f s ≠ Y.f t := by
  intro h
  exact hu (hY t (h ▸ hX.persist (Nat.zero_le s) hX0))

/-- Any public register that has read X_a (co-present at X's frame, X's frame containing u)
  at time t0 never again shares a frame with Y at any time t ≥ t0. -/
theorem reader_never_meets_Y_after (X Y P : Route K V) (u : V) (W : Submodule K V)
    (hu : u ∉ W) (hX : X.IsPublic) (hX0 : u ∈ X.f 0) (hP : P.IsPublic)
    (hY : ∀ t, Y.f t ≤ W) {s t0 : ℕ} (hread : P.f t0 = X.f s) {t t' : ℕ} (htt : t0 ≤ t) :
    P.f t ≠ Y.f t' := by
  intro h
  have h1 : u ∈ P.f t0 := hread ▸ hX.persist (Nat.zero_le s) hX0
  exact hu (hY t' (h ▸ hP.persist htt h1))

/-- Scope: "ever reads X_a ⇒ never meets Y_a" needs "afterwards"; a public helper may meet Y
  before it reads X.  Concrete counterexample over ℚ×ℚ. -/
theorem meet_before_read_possible :
    ∃ (X Y P : Route ℚ (ℚ × ℚ)) (u : ℚ × ℚ) (W : Submodule ℚ (ℚ × ℚ)),
      u ∉ W ∧ X.IsPublic ∧ u ∈ X.f 0 ∧ P.IsPublic ∧ (∀ t, Y.f t ≤ W) ∧
      P.f 1 = X.f 1 ∧ P.f 0 = Y.f 0 := by
  let W : Submodule ℚ (ℚ × ℚ) := Submodule.span ℚ {((0 : ℚ), (1 : ℚ))}
  refine ⟨⟨fun _ => ⊤, fun _ => False, fun _ _ => le_rfl⟩,
    ⟨fun _ => W, fun _ => False, fun _ _ => le_rfl⟩,
    ⟨fun t => if t = 0 then W else ⊤, fun _ => False, ?_⟩, (1, 0), W, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩
  · intro t _
    by_cases h : t = 0
    · subst h; simp
    · simp [h]
  · intro h
    obtain ⟨a, ha⟩ := Submodule.mem_span_singleton.mp h
    have := congrArg Prod.fst ha
    simp at this
  · intro t h; exact h
  · trivial
  · intro t h; exact h
  · intro t; exact le_rfl
  · simp
  · simp

/-- Entry law: content (u) in a register's history, then a u-free frame at time t:
  an owned step dropped it.  With all owned destinations in D and F = frame(t) ∉ D,
  the register took an owned MOVE to a landing frame d ∈ D and then ASCENDED
  publicly (d < F strictly) before reaching F. -/
theorem owned_landing_then_ascent (R : Route K V) (D : Set (Submodule K V)) (u : V)
    (hD : ∀ s, R.owned s → R.f (s + 1) ∈ D) {a t : ℕ} (hat : a ≤ t) (hu : u ∈ R.f a)
    (hF : u ∉ R.f t) (hFD : R.f t ∉ D) :
    ∃ s, a ≤ s ∧ s < t ∧ R.owned s ∧ R.f (s + 1) ∈ D ∧ R.f (s + 1) < R.f t := by
  -- last owned step before t
  have key : ∀ t, a ≤ t → R.Pub a t ∨
      ∃ s, a ≤ s ∧ s < t ∧ R.owned s ∧ R.f (s + 1) ≤ R.f t := by
    intro t hat
    induction t, hat using Nat.le_induction with
    | base => exact Or.inl fun s h1 h2 => by omega
    | succ t ht ih =>
      by_cases ho : R.owned t
      · exact Or.inr ⟨t, ht, by omega, ho, le_rfl⟩
      · rcases ih with h | ⟨s, h1, h2, h3, h4⟩
        · left
          intro s h1 h2
          by_cases hs : s = t
          · subst hs; exact ho
          · exact h s h1 (by omega)
        · exact Or.inr ⟨s, h1, by omega, h3, h4.trans (R.pub t ho)⟩
  rcases key t hat with h | ⟨s, h1, h2, h3, h4⟩
  · exact absurd (R.persist hat h hu) hF
  · refine ⟨s, h1, h2, h3, hD s h3, lt_of_le_of_ne h4 ?_⟩
    intro heq
    exact hFD (heq ▸ hD s h3)

/-- SPEC8 corollary: a u-holding register sitting in Y's final frame F (u-free since F ≤ W,
  u ∉ W) with F ∉ D has landed by an owned MOVE in D and climbed publicly strictly above
  the landing frame: it is a ferrying register, not an owned register at a landing frame. -/
theorem delivery_needs_ferry (R : Route K V) (D : Set (Submodule K V)) (u : V)
    (W F : Submodule K V) (hu : u ∉ W) (hFW : F ≤ W) (hFD : F ∉ D)
    (hD : ∀ s, R.owned s → R.f (s + 1) ∈ D) {a t : ℕ} (hat : a ≤ t) (hua : u ∈ R.f a)
    (hFt : R.f t = F) :
    ∃ s, a ≤ s ∧ s < t ∧ R.owned s ∧ R.f (s + 1) ∈ D ∧ R.f (s + 1) < F := by
  have hF : u ∉ R.f t := fun h => hu (hFW (hFt ▸ h))
  obtain ⟨s, h1, h2, h3, h4, h5⟩ :=
    owned_landing_then_ascent R D u hD hat hua hF (hFt ▸ hFD)
  exact ⟨s, h1, h2, h3, h4, hFt ▸ h5⟩

/-- Consequently no owned destination (a fixed set D) equals a delivered frame:
  strict ascent means the delivering register took at least one public step after its
  owned landing (landing frame ≠ F). -/
theorem landing_ne_final (R : Route K V) (D : Set (Submodule K V)) (u : V)
    (W F : Submodule K V) (hu : u ∉ W) (hFW : F ≤ W) (hFD : F ∉ D)
    (hD : ∀ s, R.owned s → R.f (s + 1) ∈ D) {a t : ℕ} (hat : a ≤ t) (hua : u ∈ R.f a)
    (hFt : R.f t = F) :
    ∃ s, s < t ∧ R.owned s ∧ R.f (s + 1) ≠ F := by
  obtain ⟨s, -, h2, h3, -, h5⟩ := delivery_needs_ferry R D u W F hu hFW hFD hD hat hua hFt
  exact ⟨s, h2, h3, h5.ne⟩

end FrameSep

#print axioms FrameSep.X_Y_never_share
#print axioms FrameSep.reader_never_meets_Y_after
#print axioms FrameSep.meet_before_read_possible
#print axioms FrameSep.Route.exit_owned
#print axioms FrameSep.owned_landing_then_ascent
#print axioms FrameSep.delivery_needs_ferry
#print axioms FrameSep.landing_ne_final
