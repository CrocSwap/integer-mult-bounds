import SelectedSourceSyntax
import Current1094CallSequenceHelpersStructuralComplete

/-!
UNCOMPILED. Strict already-parsed owner and ordered-centre declarations for
selected PR1094, using the independently accepted all144 owner certificate.
This reuses the shared parsed Value/register vocabulary. It does not implement
JSON byte parsing, interpret a route as a chart, or run a physical allocator.

Each L row retains its complete route. Its family must match the certified
original-order owner at the same position. C indices are ordered local tags:
the source enumerates centres [92,57,81,224,11,240,9,256] and declares the private
family interval [14336,14344). Numeric family projection below models this
declaration; no mutable component-store allocation is present in emit_allcold.py.
A physical implementation must separately realize that declared projection.

Source context: kappa=836330098538459/500000000000000000.
Credits: Rohan Arun PR1094, Jeremy Kothe T16/hyperplane-ended emitter, Hao Yan
PR514/484/507, columbia-git PR1553 owner binding, DreamingOfClouds realization,
and the accepted bank/machine/frame/signed proof interfaces. Apache-2.0;
prepared with OpenAI assistance. No supplier or compiler replay in preparation.
-/
set_option Elab.async false
namespace CurrentMain.Current1094OwnerDeclarationDecoder
open SelectedSourceSyntax (Value natValue bounded Register)
open Current1094CallSequenceHelpersStructural

/-- Source route syntax only. No basis, recipe or physical meaning is assigned. -/
inductive Route where
  | data (stage : Fin 9) (port : Fin 112)
  | whole (child : Fin 18) (offset : Fin 73)
  | narrow (child : Fin 18) (offset : Fin 73) (width : Nat)
      (spectators : List (Fin 73))

def route : Value → Option Route
  | .array [.integer tag, sv, pv] =>
      if tag = 1 then do
        let s ← bounded 9 sv
        let p ← bounded 112 pv
        return .data s p
      else if tag = 3 then do
        let child ← bounded 18 sv
        let offset ← bounded 73 pv
        if offset.val + 9 ≤ 73 then return .whole child offset else none
      else none
  | .array [.integer tag, cv, ov, wv, .array spectators] => do
      if tag ≠ 4 then none else do
        let child ← bounded 18 cv
        let offset ← bounded 73 ov
        let width ← natValue wv
        let slots ← spectators.mapM (bounded 73)
        if 0 < width ∧ width < 9 ∧ offset.val + width ≤ 73 ∧
            slots.length = 9 - width ∧ slots.Nodup then
          return .narrow child offset width slots
        else none
  | _ => none

structure OwnerRow where
  family : Fin 14336
  route : Route

/-- Exact two-field owner row; no default owner and no Fin modulo coercion. -/
def ownerRow : Value → Option OwnerRow
  | .array [fv, rv] => do
      let f ← bounded 14336 fv
      let r ← route rv
      return ⟨f, r⟩
  | _ => none

/-- A successful table retains its decoded rows and the checked ordered match. -/
def MatchedOwners (c : Fin 144) :=
  { rows : List OwnerRow //
      rows.map OwnerRow.family = List.ofFn (selectedOrdinaryOwner c) }

def owners (c : Fin 144) : Value → Option (MatchedOwners c)
  | .array xs => do
      let rows ← xs.mapM ownerRow
      if h : rows.map OwnerRow.family = List.ofFn (selectedOrdinaryOwner c) then
        return ⟨rows, h⟩
      else none
  | _ => none

/-- Every lookup is in the actual decoded family list; the length comes from
its checked equality to the704-entry certified list. -/
def ownerAt {c : Fin 144} (m : MatchedOwners c) (i : Fin 704) : Fin 14336 :=
  (m.val.map OwnerRow.family)[i.val]'(by
    rw [m.property, List.length_ofFn]
    exact i.isLt)

theorem ownerAt_eq {c : Fin 144} (m : MatchedOwners c) (i : Fin 704) :
    ownerAt m i = selectedOrdinaryOwner c i := by
  simp only [ownerAt, m.property, List.getElem_ofFn]

theorem decoded_owner_injective {c : Fin 144} (m : MatchedOwners c) :
    Function.Injective (ownerAt m) := by
  intro i j h
  apply selectedOrdinaryOwner_injective c
  simpa only [ownerAt_eq] using h

/-- This order is the actual provider's canonical.centers declaration.
These are carrier L registers, not the eight private physical-family numbers. -/
def centreCarriers : List (Fin 704) := [92, 57, 81, 224, 11, 240, 9, 256]

def MatchedCentres := { carriers : List (Fin 704) // carriers = centreCarriers }

/-- Both the ordered carrier array and the exact declared half-open private
interval are checked. This is not a mutable C allocation implementation. -/
def centres : Value → Value → Option MatchedCentres
  | .array xs, .array [.integer lo, .integer hi] => do
      if lo = 14336 ∧ hi = 14344 then do
        let carriers ← xs.mapM (bounded 704)
        if h : carriers = centreCarriers then return ⟨carriers, h⟩ else none
      else none
  | _, _ => none

theorem centres_ordered (m : MatchedCentres) : m.val = centreCarriers := m.property

abbrev Family := Current1094PrivateCentreHosting.Family

/-- Numeric family indices only. No scalar address/base or byte allocation. -/
def familyNumber : Family → Fin 14826
  | .inl f => ⟨f.val, by have h := f.isLt; omega⟩
  | .inr i => ⟨14336 + i.val, by have h := i.isLt; omega⟩

theorem familyNumber_injective : Function.Injective familyNumber := by
  intro x y h
  have hv := congrArg Fin.val h
  cases x with
  | inl a =>
      cases y with
      | inl b =>
          exact congrArg Sum.inl (Fin.ext (by simpa only [familyNumber] using hv))
      | inr b =>
          have ha := a.isLt
          change a.val = 14336 + b.val at hv
          omega
  | inr a =>
      cases y with
      | inl b =>
          have hb := b.isLt
          change 14336 + a.val = b.val at hv
          omega
      | inr b =>
          apply congrArg Sum.inr
          apply Fin.ext
          change 14336 + a.val = 14336 + b.val at hv
          omega

def declaredAt {c : Fin 144} (m : MatchedOwners c) : Register → Family
  | .inl i => .inl (ownerAt m i)
  | .inr k => .inr k

theorem declaredAt_eq {c : Fin 144} (m : MatchedOwners c) (r : Register) :
    declaredAt m r =
      Current1094PrivateCentreHosting.declaredFamily (selectedOrdinaryOwner c) r := by
  cases r <;> simp only [declaredAt, ownerAt_eq,
    Current1094PrivateCentreHosting.declaredFamily]

/-- The centre witness ensures the exact ordered source declaration was
validated; its private family index is determined by the C tag, not its carrier. -/
def declaredProjection {c : Fin 144} (m : MatchedOwners c) (_centres : MatchedCentres)
    (r : Register) : Fin 14826 := familyNumber (declaredAt m r)

theorem declaredProjection_injective {c : Fin 144}
    (m : MatchedOwners c) (cs : MatchedCentres) :
    Function.Injective (declaredProjection m cs) := by
  intro r s h
  apply selectedDeclaredFamily_injective c
  have he := familyNumber_injective h
  simpa only [declaredAt_eq] using he

theorem centre_projection {c : Fin 144} (m : MatchedOwners c)
    (cs : MatchedCentres) (k : Fin 8) :
    (declaredProjection m cs (.inr k)).val = 14336 + k.val := rfl

end CurrentMain.Current1094OwnerDeclarationDecoder
#print axioms CurrentMain.Current1094OwnerDeclarationDecoder.ownerAt_eq
#print axioms CurrentMain.Current1094OwnerDeclarationDecoder.decoded_owner_injective
#print axioms CurrentMain.Current1094OwnerDeclarationDecoder.centres_ordered
#print axioms CurrentMain.Current1094OwnerDeclarationDecoder.familyNumber_injective
#print axioms CurrentMain.Current1094OwnerDeclarationDecoder.declaredAt_eq
#print axioms CurrentMain.Current1094OwnerDeclarationDecoder.declaredProjection_injective
#print axioms CurrentMain.Current1094OwnerDeclarationDecoder.centre_projection
