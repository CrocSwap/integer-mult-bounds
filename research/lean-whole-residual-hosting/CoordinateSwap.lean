import Std

/-!
Coordinate factors for whole-residual bit hosting. Apache-2.0.
Prepared with substantial OpenAI Codex assistance.

One address has two coordinates at every index. A bit residual exchanges
the two coordinates on its mask, inside ONE stream. This is the coordinate
projector form of D_P in the inherited bit geometry. Payload values and
address-coordinate values are arbitrary; in particular streams need not be
separable, initialized, or independent of other live values.

These supporting identities are standard coordinate algebra. The contribution
is their use with the complete-macro window theorem, not a novelty claim for
disjoint coordinate factorization. No priced local word is translated here.
-/

namespace WholeHosting

abbrev Mask (ι : Type u) := ι → Bool
abbrev Address (ι : Type u) (K : Type v) := ι → K × K
abbrev Stream (ι : Type u) (K : Type v) (A : Type w) := Address ι K → A

def unionMask {ι : Type u} (p q : Mask ι) : Mask ι := fun i => p i || q i

def remainderMask {ι : Type u} (pending hosted : Mask ι) : Mask ι :=
  fun i => pending i && !hosted i

def MasksDisjoint {ι : Type u} (p q : Mask ι) : Prop :=
  ∀ i, p i = true → q i = false

def MaskSubset {ι : Type u} (p q : Mask ι) : Prop :=
  ∀ i, p i = true → q i = true

def swapAddress {ι : Type u} {K : Type v} (p : Mask ι)
    (address : Address ι K) : Address ι K :=
  fun i => if p i then ((address i).2, (address i).1) else address i

def bitAction {ι : Type u} {K : Type v} {A : Type w} (p : Mask ι)
    (value : Stream ι K A) : Stream ι K A :=
  fun address => value (swapAddress p address)

theorem masksDisjoint_symm {ι : Type u} {p q : Mask ι}
    (h : MasksDisjoint p q) : MasksDisjoint q p := by
  intro i hq
  cases hp : p i with
  | false => rfl
  | true => have := h i hp; simp [hq] at this

theorem swapAddress_involution {ι : Type u} {K : Type v}
    (p : Mask ι) (address : Address ι K) :
    swapAddress p (swapAddress p address) = address := by
  funext i
  cases hp : p i <;> simp [swapAddress, hp]

/-- The coordinate exchanges commute even when the masks overlap. Overlap
must nevertheless be excluded for union-based accounting: it cancels. -/
theorem swapAddress_commute {ι : Type u} {K : Type v}
    (p q : Mask ι) (address : Address ι K) :
    swapAddress p (swapAddress q address) =
      swapAddress q (swapAddress p address) := by
  funext i
  cases hp : p i <;> cases hq : q i <;> simp [swapAddress, hp, hq]

theorem swapAddress_disjoint_union {ι : Type u} {K : Type v}
    (p q : Mask ι) (h : MasksDisjoint p q) (address : Address ι K) :
    swapAddress p (swapAddress q address) = swapAddress (unionMask p q) address := by
  funext i
  cases hp : p i with
  | false => simp [swapAddress, unionMask, hp]
  | true => simp [swapAddress, unionMask, hp, h i hp]

theorem bitAction_involution {ι : Type u} {K : Type v} {A : Type w}
    (p : Mask ι) (value : Stream ι K A) :
    bitAction p (bitAction p value) = value := by
  funext address
  exact congrArg value (swapAddress_involution p address)

theorem bitAction_commute {ι : Type u} {K : Type v} {A : Type w}
    (p q : Mask ι) (value : Stream ι K A) :
    bitAction q (bitAction p value) = bitAction p (bitAction q value) := by
  funext address
  exact congrArg value (swapAddress_commute p q address)

theorem bitAction_disjoint_comp {ι : Type u} {K : Type v} {A : Type w}
    (p q : Mask ι) (h : MasksDisjoint p q) (value : Stream ι K A) :
    bitAction q (bitAction p value) = bitAction (unionMask p q) value := by
  funext address
  exact congrArg value (swapAddress_disjoint_union p q h address)

theorem remainder_disjoint {ι : Type u} (pending hosted : Mask ι) :
    MasksDisjoint hosted (remainderMask pending hosted) := by
  intro i hi
  simp [remainderMask, hi]

theorem union_remainder {ι : Type u} (pending hosted : Mask ι)
    (h : MaskSubset hosted pending) :
    unionMask hosted (remainderMask pending hosted) = pending := by
  funext i
  cases hh : hosted i with
  | false => simp [unionMask, remainderMask, hh]
  | true => simp [unionMask, remainderMask, hh, h i hh]

/-- A whole hosted residual plus the pending child's exact remainder has
the same action as that child, for every contents of the owned stream. -/
theorem bitAction_complete {ι : Type u} {K : Type v} {A : Type w}
    (pending hosted : Mask ι) (h : MaskSubset hosted pending)
    (value : Stream ι K A) :
    bitAction (remainderMask pending hosted) (bitAction hosted value) =
      bitAction pending value := by
  rw [bitAction_disjoint_comp hosted _ (remainder_disjoint pending hosted),
    union_remainder pending hosted h]

def maskUnion {ι : Type u} : List (Mask ι) → Mask ι
  | [] => fun _ => false
  | head :: tail => unionMask head (maskUnion tail)

/-- Each mask is disjoint from all masks following it in the list. -/
def DisjointMasks {ι : Type u} : List (Mask ι) → Prop
  | [] => True
  | head :: tail => MasksDisjoint head (maskUnion tail) ∧ DisjointMasks tail

/-- Apply the masks in chronological list order to one physical stream. -/
def bitFactors {ι : Type u} {K : Type v} {A : Type w} :
    List (Mask ι) → Stream ι K A → Stream ι K A
  | [], value => value
  | head :: tail, value => bitFactors tail (bitAction head value)

theorem bitAction_empty {ι : Type u} {K : Type v} {A : Type w}
    (value : Stream ι K A) : bitAction (fun _ => false) value = value := by
  rfl

/-- An unbounded list theorem, not a finite enumeration of template slots. -/
theorem bitFactors_union {ι : Type u} {K : Type v} {A : Type w}
    (masks : List (Mask ι)) (h : DisjointMasks masks) (value : Stream ι K A) :
    bitFactors masks value = bitAction (maskUnion masks) value := by
  induction masks generalizing value with
  | nil => rfl
  | cons head tail ih =>
    change bitFactors tail (bitAction head value) = bitAction (unionMask head (maskUnion tail)) value
    rw [ih h.2, bitAction_disjoint_comp head _ h.1]

/-- Pairwise disjoint, wholly owned residuals followed by the exact
remainder complete a pending child on arbitrary correlated stream values. -/
theorem bitFactors_complete {ι : Type u} {K : Type v} {A : Type w}
    (pending : Mask ι) (masks : List (Mask ι)) (hd : DisjointMasks masks)
    (hs : MaskSubset (maskUnion masks) pending) (value : Stream ι K A) :
    bitAction (remainderMask pending (maskUnion masks)) (bitFactors masks value) =
      bitAction pending value := by
  rw [bitFactors_union masks hd, bitAction_complete pending _ hs]

end WholeHosting

#print axioms WholeHosting.swapAddress_involution
#print axioms WholeHosting.swapAddress_commute
#print axioms WholeHosting.swapAddress_disjoint_union
#print axioms WholeHosting.bitAction_involution
#print axioms WholeHosting.bitAction_commute
#print axioms WholeHosting.bitAction_disjoint_comp
#print axioms WholeHosting.bitAction_complete
#print axioms WholeHosting.bitFactors_union
#print axioms WholeHosting.bitFactors_complete
