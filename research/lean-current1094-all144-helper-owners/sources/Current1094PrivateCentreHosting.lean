import FreshScalarSupportRealize

/-!
A source-only hosting interface for one selected current1094 invocation.
The selected receipt has 704 ordinary registers (224 data/target and 480 helpers),
and the source emitter reserves eight centre families outside the 14336 live
families. The tagged domains below keep those namespaces disjoint.

This does not parse an owner table or identify physical numeric addresses.
The live-owner injection, the actual hosting projection, and actual executor
equality are supplied explicitly. Charts remain arbitrary linear equivalences.
The conclusion reuses LemmaA.realize_run; it does not re-prove realization or
LemmaA.lemmaA_async, nor discharge recipes, labels, scalar rows/columns,
endpoint factorization, or schedule commutation.

Prepared with OpenAI assistance. Apache-2.0. Inherited PR516 realization:
DreamingOfClouds, with Claude Opus 5.5 (Anthropic), via Claude Code.
FreshScalarSupportRealize is bank's explicit uncompiled import-only alias;
do not combine it with the historical/raw LemmaA modules in one closure.
-/
set_option Elab.async false

namespace CurrentMain.Current1094PrivateCentreHosting

abbrev Register := Fin 704 ⊕ Fin 8
abbrev Family := Fin 14336 ⊕ Fin 8

/-- The ordinary owner map and the private centre namespace of one invocation. -/
def declaredFamily (liveOwner : Fin 704 → Fin 14336) : Register → Family
  | .inl i => .inl (liveOwner i)
  | .inr c => .inr c

/-- Distinct live owners plus the disjoint centre namespace cover all registers. -/
theorem declaredFamily_injective (liveOwner : Fin 704 → Fin 14336)
    (hlive : Function.Injective liveOwner) :
    Function.Injective (declaredFamily liveOwner) := by
  intro i j hij
  cases i with
  | inl i =>
    cases j with
    | inl j =>
      change (Sum.inl (liveOwner i) : Family) = Sum.inl (liveOwner j) at hij
      exact congrArg Sum.inl (hlive (Sum.inl.inj hij))
    | inr c =>
      change (Sum.inl (liveOwner i) : Family) = Sum.inr c at hij
      cases hij
  | inr c =>
    cases j with
    | inl j =>
      change (Sum.inr c : Family) = Sum.inl (liveOwner j) at hij
      cases hij
    | inr d =>
      change (Sum.inr c : Family) = Sum.inr d at hij
      exact congrArg Sum.inr (Sum.inr.inj hij)

section Hosting

variable {Φ Λ K W M : Type*} [Semiring K]
  [AddCommMonoid W] [Module K W] [AddCommMonoid M] [Module K M]

/-- An exact family projection is sufficient even when owners carry route data. -/
theorem hosting_injective (liveOwner : Fin 704 → Fin 14336)
    (hlive : Function.Injective liveOwner)
    (σ : LemmaA.Hosting Register Φ K W M) (familyOf : Φ → Family)
    (hproject : ∀ r, familyOf (σ.own r) = declaredFamily liveOwner r) :
    Function.Injective σ.own := by
  intro i j hij
  apply declaredFamily_injective liveOwner hlive
  rw [← hproject i, ← hproject j, hij]

/-- The actual complete invocation is local execution through its supplied charts.
The executor equality includes the numeric-address/tagged-index correspondence. -/
theorem actual_invocation_view [DecidableEq Φ]
    (liveOwner : Fin 704 → Fin 14336) (hlive : Function.Injective liveOwner)
    (σ : LemmaA.Hosting Register Φ K W M) (familyOf : Φ → Family)
    (hproject : ∀ r, familyOf (σ.own r) = declaredFamily liveOwner r)
    (rec : Λ → Λ → M → M) (es : List (LemmaG.Event Register Λ K))
    (actual : (Φ → W) → (Φ → W))
    (hexec : actual = LemmaA.realizeRun σ rec es) (y : Φ → W) :
    LemmaA.view σ (actual y) = LemmaG.Stream.physRun rec es (LemmaA.view σ y) := by
  rw [hexec]
  exact LemmaA.realize_run σ (hosting_injective liveOwner hlive σ familyOf hproject)
    rec es y

end Hosting
end CurrentMain.Current1094PrivateCentreHosting

#print axioms CurrentMain.Current1094PrivateCentreHosting.declaredFamily_injective
#print axioms CurrentMain.Current1094PrivateCentreHosting.hosting_injective
#print axioms CurrentMain.Current1094PrivateCentreHosting.actual_invocation_view
#check @CurrentMain.Current1094PrivateCentreHosting.hosting_injective
#check @CurrentMain.Current1094PrivateCentreHosting.actual_invocation_view
