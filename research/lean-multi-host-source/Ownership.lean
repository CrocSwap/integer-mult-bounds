import OwnershipData

/-!
Constructive ownership for the literal PR442 stage-2, replica-0 invocation.
`owner` is the actual formula `(family, d ∘ sigma⁻¹)` with arbitrary source
charts for the 240 data roles and our explicit slot-permutation charts for
all 747 helpers. The family outer chart is instantiated by the actual source
port basis in OwnershipGeometry; the inverse law here is an explicit premise.

Injection holds at a fixed cover invocation. No assertion of disjoint owners
across different cover elements is made. Apache-2.0. Prepared with substantial
OpenAI Codex assistance.
-/
namespace SourceOwnership

abbrev Vec (K : Type) := Axis → K

def reindex {K : Type} (t : Tag) (v : Vec K) : Vec K := fun i => v (invPerm t i)
def unindex {K : Type} (t : Tag) (v : Vec K) : Vec K := fun i => v (perm t i)

theorem unindex_reindex {K : Type} (t : Tag) (v : Vec K) :
    unindex t (reindex t v) = v := by
  funext i
  simp only [unindex, reindex, perm_inverse]

theorem reindex_unindex {K : Type} (t : Tag) (v : Vec K) :
    reindex t (unindex t v) = v := by
  funext i
  simp only [unindex, reindex, inverse_perm]

/-- Transport of the full residual coordinate projector, for every vector. -/
theorem residual_projector_transport {K : Type} (zero : K) (t : Tag) (v : Vec K) :
    reindex t (fun i => if sourceMask t i then v i else zero) =
      fun i => if targetMask t i then reindex t v i else zero := by
  funext i
  have hm := perm_support t (invPerm t i)
  rw [inverse_perm] at hm
  simp only [reindex, ← hm]

theorem perm_tag_injective {a b : Tag} (h : perm a = perm b) : a = b := by
  apply fingerprint_injective a b
  unfold fingerprint
  rw [h]

/-- Distinct literal permutations give distinct actions over any set with
 two distinct values. Descriptor inequality alone is not used. -/
theorem unindex_tag_injective {K : Type} (lo hi : K) (hne : lo ≠ hi)
    {a b : Tag} (h : @unindex K a = @unindex K b) : a = b := by
  apply perm_tag_injective
  funext i
  apply Classical.byContradiction
  intro hn
  let v : Vec K := fun j => if j = perm a i then lo else hi
  have he := congrFun (congrFun h v) i
  have hn' : perm b i ≠ perm a i := fun hh => hn hh.symm
  simp only [unindex, v, if_pos rfl, if_neg hn'] at he
  exact hne he

theorem family_data_general (r : Role) (hr : r.val < 240) : family r = r.val := by
  exact family_data ⟨r.val, hr⟩

theorem same_family_data {r s : Role} (hf : family r = family s) (hr : r.val < 240) : r = s := by
  have hfr := family_data_general r hr
  by_cases hs : s.val < 240
  · apply Fin.ext
    rw [← hfr, hf, family_data_general s hs]
  · have hfs := (helper_range s (Nat.le_of_not_lt hs)).1
    omega

/-- Helpers first undo the common family chart, then undo their explicit
slot permutation. Data inverse charts are exactly the supplied source maps. -/
def sigmaInverse {K : Type}
    (dataInverse : Role → Vec K → Vec K)
    (familyInverse : Nat → Vec K → Vec K) (r : Role) : Vec K → Vec K :=
  if r.val < 240 then dataInverse r
  else fun v => unindex (tag r) (familyInverse (family r) v)

/-- Physical class as an actual function on address vectors. A proof that
these functions lie in the orthogonal cover is provided separately. -/
def owner {K : Type}
    (dataInverse : Role → Vec K → Vec K)
    (familyInverse : Nat → Vec K → Vec K)
    (d : Vec K → Vec K) (r : Role) : Nat × (Vec K → Vec K) :=
  (family r, fun v => d (sigmaInverse dataInverse familyInverse r v))

/-- All 987 roles have distinct physical owners at every fixed injective
cover map d. The common outer family chart has the displayed actual inverse;
there is no physical-aliasing premise. -/
theorem owners_injective {K : Type} (lo hi : K) (hne : lo ≠ hi)
    (dataInverse : Role → Vec K → Vec K)
    (familyForward familyInverse : Nat → Vec K → Vec K)
    (hinv : ∀ f v, familyInverse f (familyForward f v) = v)
    (d : Vec K → Vec K) (hd : ∀ {x y}, d x = d y → x = y)
    {r s : Role}
    (h : owner dataInverse familyInverse d r = owner dataInverse familyInverse d s) : r = s := by
  have hf : family r = family s := congrArg Prod.fst h
  by_cases hr : r.val < 240
  · exact same_family_data hf hr
  by_cases hs : s.val < 240
  · exact (same_family_data hf.symm hs).symm
  apply family_tag_injective hf
  apply unindex_tag_injective lo hi hne
  funext v
  have ho := congrFun (congrArg Prod.snd h) (familyForward (family r) v)
  have he := hd ho
  simp only [sigmaInverse, if_neg hr, if_neg hs, ← hf, hinv] at he
  exact he

end SourceOwnership
#print axioms SourceOwnership.residual_projector_transport
#print axioms SourceOwnership.unindex_tag_injective
#print axioms SourceOwnership.owners_injective
