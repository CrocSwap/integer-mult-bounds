import SourceRaw
import SourceConnection

/-! Explicit initial payload construction. Every live role is arbitrary;
only the source's designated private row is blank. Exterior payloads are
independent arbitrary functions, and owner injectivity is used explicitly. -/
namespace InvocationPayload
open FramedReplay SourceConnection

noncomputable def extend {R S A : Type} (owner : R → S) (values : R → A)
    (outside : S → A) (s : S) : A := by
  classical
  exact if h : ∃ r, owner r = s then values (Classical.choose h) else outside s

theorem extend_owner {R S A : Type} (owner : R → S)
    (hinj : ∀ {r s}, owner r = owner s → r = s)
    (values : R → A) (outside : S → A) (r : R) :
    extend owner values outside (owner r) = values r := by
  classical
  unfold extend
  split
  · next h => rw [hinj (Classical.choose_spec h)]
  · next h => exact False.elim (h ⟨r, rfl⟩)

theorem extend_outside {R S A : Type} (owner : R → S)
    (values : R → A) (outside : S → A) (s : S)
    (hs : ∀ r, s ≠ owner r) : extend owner values outside s = outside s := by
  classical
  apply dif_neg
  rintro ⟨r, h⟩
  exact hs r h.symm

noncomputable def realize {S X : Type} (owner : SourceRaw.Role → S)
    (chart : SourceRaw.Role → Gauge X) (input : Nat → X → Bool)
    (outside : S → X → Bool) : S → X → Bool :=
  extend owner (fun r a => input r.val ((chart r).inverse a)) outside

theorem realize_owner {S X : Type} (owner : SourceRaw.Role → S)
    (chart : SourceRaw.Role → Gauge X)
    (hinj : ∀ {r s}, owner r = owner s → r = s)
    (input : Nat → X → Bool) (outside : S → X → Bool) (r : SourceRaw.Role) :
    realize owner chart input outside (owner r) =
      fun a => input r.val ((chart r).inverse a) :=
  extend_owner owner hinj _ outside r

theorem input_realize {S X : Type} (owner : SourceRaw.Role → S)
    (chart : SourceRaw.Role → Gauge X)
    (hinj : ∀ {r s}, owner r = owner s → r = s)
    (input : Nat → X → Bool) (outside : S → X → Bool)
    (blank : ∀ i, 988 ≤ i → input i = fun _ => false) :
    SourceRaw.input owner chart (realize owner chart input outside) = input := by
  funext i a
  unfold SourceRaw.input
  split
  · next hi => simp only [realize_owner owner chart hinj, (chart ⟨i, hi⟩).inverse_forward]
  · next hi => exact (congrFun (blank i (Nat.le_of_not_lt hi)) a).symm

theorem input_realize_packed {S X : Type} (owner : SourceRaw.Role → S)
    (chart : SourceRaw.Role → Gauge X)
    (hinj : ∀ {r s}, owner r = owner s → r = s)
    (data : Data → X → Bool) (helpers : Host → X → Bool)
    (outside : S → X → Bool) :
    SourceRaw.input owner chart (realize owner chart (packed data helpers) outside) =
      packed data helpers := by
  apply input_realize owner chart hinj
  intro i hi
  simp only [packed, dif_neg (show ¬ i < 240 by omega),
    dif_neg (show ¬ i < 987 by omega)]

/-- The actual complete raw fold, initialized by the displayed payload
construction, realizes the arbitrary-input framed invocation. -/
theorem realized_gather {S X : Type} (owner : SourceRaw.Role → S)
    (chart : SourceRaw.Role → Gauge X)
    (hinj : ∀ {r s}, owner r = owner s → r = s)
    (gauges : Nat → Gauge X) (data : Data → X → Bool)
    (helpers : Host → X → Bool) (outside : S → X → Bool) (r : SourceRaw.Role) :
    OwnerTransport.gather owner chart
      (SourceRaw.final owner chart gauges
        (realize owner chart (packed data helpers) outside)) r =
      (SourceFramed.final gauges (packed data helpers)).get r.val := by
  have h := SourceRaw.gather_final owner chart hinj gauges
    (realize owner chart (packed data helpers) outside) r
  rw [input_realize_packed owner chart hinj] at h
  exact h

theorem realized_payload {S X : Type} (owner : SourceRaw.Role → S)
    (chart : SourceRaw.Role → Gauge X)
    (hinj : ∀ {r s}, owner r = owner s → r = s)
    (gauges : Nat → Gauge X) (data : Data → X → Bool)
    (helpers : Host → X → Bool) (outside : S → X → Bool)
    (r : SourceRaw.Role) (a : X) :
    (SourceRaw.final owner chart gauges
      (realize owner chart (packed data helpers) outside) (owner r)).2 a =
      ((SourceFramed.final gauges (packed data helpers)).get r.val).2
        ((chart r).inverse a) := by
  have h := congrArg Prod.snd
    (realized_gather owner chart hinj gauges data helpers outside r)
  have ha := congrFun h ((chart r).inverse a)
  simpa only [OwnerTransport.gather, (chart r).forward_inverse] using ha

theorem realized_payloads {S X : Type} (owner : SourceRaw.Role → S)
    (chart : SourceRaw.Role → Gauge X)
    (hinj : ∀ {r s}, owner r = owner s → r = s)
    (gauges : Nat → Gauge X) (data : Data → X → Bool)
    (helpers : Host → X → Bool) (outside : S → X → Bool) :
    (fun r => (SourceRaw.final owner chart gauges
      (realize owner chart (packed data helpers) outside) (owner r)).2) =
      fun r a => ((SourceFramed.final gauges (packed data helpers)).get r.val).2
        ((chart r).inverse a) := by
  funext r a
  exact realized_payload owner chart hinj gauges data helpers outside r a

end InvocationPayload
