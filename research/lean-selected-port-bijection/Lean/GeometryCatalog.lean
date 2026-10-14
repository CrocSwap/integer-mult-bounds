import ComplexBinaryIndependence
import ComplexFastOrthogonality
namespace CurrentMain.ComplexGeometry
open CurrentMain.BinaryFrame

structure BasisRecord where
  rows : List Nat
  pivots : List Nat
  deriving DecidableEq, Repr

structure FrameRecord where
  basis : Nat
  annihilator : Nat
  deriving DecidableEq, Repr

structure EdgeRecord where
  small : Nat
  large : Nat
  witnesses : List (List Nat)
  deriving DecidableEq, Repr

def basisValid (r : BasisRecord) : Bool :=
  masksBounded 22 r.rows && pivotCheck r.rows r.pivots

def frameValid (bases : Nat → BasisRecord) (r : FrameRecord) : Bool :=
  orthogonal22 (bases r.basis).rows (bases r.annihilator).rows &&
    decide ((bases r.basis).rows.length + (bases r.annihilator).rows.length = 22)

def edgeValid (bases : Nat → BasisRecord) (e : EdgeRecord) : Bool :=
  containmentCheck (bases e.small).rows (bases e.large).rows e.witnesses &&
    decide ((bases e.small).rows.length ≤ (bases e.large).rows.length)

theorem basisValid_sound (r : BasisRecord) (checked : basisValid r = true) :
    masksBounded 22 r.rows = true ∧ Independent r.rows := by
  have h := Bool.and_eq_true_iff.mp checked
  exact ⟨h.1, pivotCheck_sound _ _ h.2⟩

theorem frameValid_sound (bases : Nat → BasisRecord) (r : FrameRecord)
    (checked : frameValid bases r = true) :
    orthogonalCheck 22 (bases r.basis).rows (bases r.annihilator).rows = true ∧
    (bases r.basis).rows.length + (bases r.annihilator).rows.length = 22 := by
  have h := Bool.and_eq_true_iff.mp checked
  exact ⟨orthogonal22_sound _ _ h.1, of_decide_eq_true h.2⟩

theorem edgeValid_sound (bases : Nat → BasisRecord) (e : EdgeRecord)
    (checked : edgeValid bases e = true) :
    (∀ n, Span (bases e.small).rows n → Span (bases e.large).rows n) ∧
    (bases e.small).rows.length ≤ (bases e.large).rows.length := by
  have h := Bool.and_eq_true_iff.mp checked
  exact ⟨containment_sound _ _ _ h.1, of_decide_eq_true h.2⟩

structure ValidCatalog (bases : Nat → BasisRecord) (frames : Nat → FrameRecord)
    (edges : Nat → EdgeRecord) : Prop where
  bases_valid : ∀ i, basisValid (bases i) = true
  frames_valid : ∀ i, frameValid bases (frames i) = true
  edges_valid : ∀ i, edgeValid bases (edges i) = true

def frameRows (bases : Nat → BasisRecord) (frames : Nat → FrameRecord) (i : Nat) : List Nat :=
  (bases (frames i).basis).rows

def edgeMatches (frames : Nat → FrameRecord) (edges : Nat → EdgeRecord)
    (small large edge : Nat) : Bool :=
  decide (small = large) || decide ((edges edge).small = (frames small).basis ∧
    (edges edge).large = (frames large).basis)

theorem checked_frame_edge (bases : Nat → BasisRecord) (frames : Nat → FrameRecord)
    (edges : Nat → EdgeRecord) (catalog : ValidCatalog bases frames edges)
    (small large edge : Nat) (checked : edgeMatches frames edges small large edge = true) :
    (∀ n, Span (frameRows bases frames small) n → Span (frameRows bases frames large) n) ∧
    (frameRows bases frames small).length ≤ (frameRows bases frames large).length := by
  rcases Bool.or_eq_true_iff.mp checked with same | checked
  · have eq : small = large := of_decide_eq_true same
    subst large
    exact ⟨fun _ h => h, Nat.le_refl _⟩
  ·
    have ids : (edges edge).small = (frames small).basis ∧
        (edges edge).large = (frames large).basis := of_decide_eq_true checked
    have h := edgeValid_sound bases (edges edge) (catalog.edges_valid edge)
    simpa only [frameRows, ids.1, ids.2] using h

end CurrentMain.ComplexGeometry
#print axioms CurrentMain.ComplexGeometry.basisValid_sound
#print axioms CurrentMain.ComplexGeometry.frameValid_sound
#print axioms CurrentMain.ComplexGeometry.edgeValid_sound
#print axioms CurrentMain.ComplexGeometry.checked_frame_edge
