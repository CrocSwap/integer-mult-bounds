import DirtyComplementSafety

/-!
Consistent coordinate renaming conjugates the complete Boolean XOR program.
This proves data/dirty symmetry and equality-based I+J geometry. It does not
claim an uncharged runtime permutation or certify ordered corner profiles.
A new frame/profile replay must pay and verify its physical implementation.
-/
namespace CoordinateConjugacy
open DirtyComplementSafety

variable {I : Type} [DecidableEq I]

def rename (q : I → I) (s : Vec I) : Vec I := fun i => s (q i)

def renamedWord (p : I → I) (word : List (I × I)) : List (I × I) :=
  word.map (fun e => (p e.1,p e.2))

omit [DecidableEq I] in
theorem rename_inverse (p q : I → I) (hpq : ∀ i, p (q i)=i) (s : Vec I) :
    rename q (rename p s) = s := by
  funext i
  exact congrArg s (hpq i)

omit [DecidableEq I] in
theorem rename_xor (q : I → I) (s t : Vec I) :
    rename q (vxor s t) = vxor (rename q s) (rename q t) := rfl

/- Rewrite gate endpoints consistently: auxiliary endpoints may be fixed
while both data banks are renamed by the same induced triple permutation. -/
theorem xor_gate_conjugacy (p q : I → I)
    (hqp : ∀ i, q (p i)=i) (hpq : ∀ i, p (q i)=i)
    (a b : I) (s : Vec I) :
    xorUpdate (p a) (p b) (rename q s) = rename q (xorUpdate a b s) := by
  funext i
  by_cases hi : i=p a
  · subst i
    simp only [xorUpdate,rename,ite_true,hqp]
  · have hqa : q i ≠ a := by
      intro h
      have hh := congrArg p h
      rw [hpq] at hh
      exact hi hh
    simp only [xorUpdate,rename,if_neg hi,if_neg hqa]

/- The actual full word, not only its fresh output, is conjugated. Arbitrary
initial dirty coordinates are covered by the same identity. -/
theorem complete_word_conjugacy (p q : I → I)
    (hqp : ∀ i, q (p i)=i) (hpq : ∀ i, p (q i)=i)
    (word : List (I × I)) (s : Vec I) :
    runWord (renamedWord p word) (rename q s) = rename q (runWord word s) := by
  induction word generalizing s with
  | nil => rfl
  | cons e es ih =>
    simp only [renamedWord,List.map_cons,runWord]
    rw [xor_gate_conjugacy p q hqp hpq]
    exact ih _

omit [DecidableEq I] in
theorem renamed_word_legal (p q : I → I) (hqp : ∀ i, q (p i)=i)
    (word : List (I × I)) (hlegal : Legal word) : Legal (renamedWord p word) := by
  intro e he
  rcases List.mem_map.mp he with ⟨old,ho,rfl⟩
  intro h
  have hi := congrArg q h
  rw [hqp,hqp] at hi
  exact hlegal old ho hi

def subset (a b : I → Bool) : Prop := ∀ i, a i=true → b i=true

omit [DecidableEq I] in
theorem subset_renaming_iff (p q : I → I) (hqp : ∀ i, q (p i)=i)
    (a b : I → Bool) : subset (rename q a) (rename q b) ↔ subset a b := by
  constructor
  · intro h i hi
    have hh := h (p i)
    simp only [rename,hqp] at hh
    exact hh hi
  · intro h i hi
    exact h (q i) hi

/- The actual frame containment predicate is invariant under the explicit
point permutation, so the new frames have genuine containing masks. -/
omit [DecidableEq I] in
theorem frame_containment_renaming (p q : I → I) (hqp : ∀ i, q (p i)=i)
    (core cover nextCore nextCover : I → Bool) :
    (subset (rename q nextCore) (rename q core) ∧
     subset (rename q cover) (rename q nextCover)) ↔
    (subset nextCore core ∧ subset cover nextCover) := by
  rw [subset_renaming_iff p q hqp,subset_renaming_iff p q hqp]

/- Permutation invariance of equality is the entire I+J entry argument. -/
omit [DecidableEq I] in
theorem equality_preserved (p q : I → I) (hqp : ∀ i, q (p i)=i) (i j : I) :
    p i=p j ↔ i=j := by
  constructor
  · intro h
    have hh := congrArg q h
    simpa only [hqp] using hh
  · intro h
    exact congrArg p h

def ijEntry (i j : I) : Int := if i=j then 2 else 1

theorem ij_entry_invariant (p q : I → I) (hqp : ∀ i, q (p i)=i) (i j : I) :
    ijEntry (p i) (p j) = ijEntry i j := by
  unfold ijEntry
  simp only [equality_preserved p q hqp]

/- Applying a point bijection and its inverse restores every triple list.
Canonical sorting is a representation step; unordered families descend
through the separate map-preserves-permutation identity. -/
omit [DecidableEq I] in
theorem list_points_inverse (p q : I → I) (hqp : ∀ i, q (p i)=i) (xs : List I) :
    (xs.map p).map q = xs := by
  induction xs with
  | nil => rfl
  | cons x xs ih => simp only [List.map_cons,hqp,ih]

omit [DecidableEq I] in
theorem mapped_triple_length (p : I → I) (xs : List I) (h : xs.length=3) :
    (xs.map p).length=3 := by simpa only [List.length_map] using h

omit [DecidableEq I] in
theorem point_map_preserves_unordered_equivalence (p : I → I)
    {xs ys : List I} (h : List.Perm xs ys) : List.Perm (xs.map p) (ys.map p) :=
  h.map p

end CoordinateConjugacy

#print axioms CoordinateConjugacy.complete_word_conjugacy
#print axioms CoordinateConjugacy.frame_containment_renaming
#print axioms CoordinateConjugacy.ij_entry_invariant
#print axioms CoordinateConjugacy.list_points_inverse
