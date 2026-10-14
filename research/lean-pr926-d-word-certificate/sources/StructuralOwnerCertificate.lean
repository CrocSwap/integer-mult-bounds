import SortedOwnerCertificate

/-!
A structurally recursive certificate path after the pinned library mergeSort
failed kernel reduction even on [2,1], while executable evaluation succeeded.
Both recursions decrease an explicit Nat fuel argument. Exhaustion returns an
unsorted permutation rather than assuming any equation or dropping an owner.
The permutation theorem therefore holds for every fuel, including the chosen
list-length fuel. A true strict-adjacency scan is still a separate obligation.

Original owner lookup order, range, length and interval-exclusion obligations
are unchanged. This generic source does not check any selected row. The old
library certificate, its actual failures and the accepted adjacency theorem
remain preserved. No native_decide, external oracle or sorting hypothesis.

Reuses the accepted SortedOwnerCertificate adjacency theorem and Lean List.Perm,
append and take/drop APIs. Preserve Lean FRO, Kim Morrison, Eric Wieser and
Francois G. Dorais source credits and Apache-2.0 notices. Prepared with OpenAI
assistance. New source; kernel acceptance is pending.
-/
set_option Elab.async false

namespace CurrentMain.StructuralOwnerCertificate

/-- Structural fuel makes every reduction independent of well-founded proof
elimination. The exhaustion branch preserves every input occurrence. -/
def mergeFuel : Nat → List Nat → List Nat → List Nat
  | 0, xs, ys => xs ++ ys
  | _ + 1, [], ys => ys
  | _ + 1, xs, [] => xs
  | fuel + 1, a :: xs, b :: ys =>
      if a ≤ b then a :: mergeFuel fuel xs (b :: ys)
      else b :: mergeFuel fuel (a :: xs) ys

theorem mergeFuel_perm (fuel : Nat) (xs ys : List Nat) :
    (mergeFuel fuel xs ys).Perm (xs ++ ys) := by
  induction fuel generalizing xs ys with
  | zero => exact List.Perm.refl _
  | succ fuel ih =>
    cases xs with
    | nil => cases ys <;> exact List.Perm.refl _
    | cons a xs =>
      cases ys with
      | nil => simpa only [mergeFuel, List.append_nil] using (List.Perm.refl (a :: xs))
      | cons b ys =>
        simp only [mergeFuel]
        split
        · exact (ih xs (b :: ys)).cons a
        · exact ((ih (a :: xs) ys).cons b).trans List.perm_middle.symm

/-- Each recursive sort call decreases only fuel. Length fuel bounds recursion;
short lists stop immediately. The midpoint is the same ceiling half as the
pinned library algorithm, and merge receives the whole input length. -/
def sortFuel : Nat → List Nat → List Nat
  | 0, xs => xs
  | _ + 1, [] => []
  | _ + 1, [a] => [a]
  | fuel + 1, a :: b :: xs =>
      let whole := a :: b :: xs
      let half := (whole.length + 1) / 2
      mergeFuel whole.length
        (sortFuel fuel (whole.take half))
        (sortFuel fuel (whole.drop half))

theorem sortFuel_perm (fuel : Nat) (xs : List Nat) :
    (sortFuel fuel xs).Perm xs := by
  induction fuel generalizing xs with
  | zero => exact List.Perm.refl _
  | succ fuel ih =>
    cases xs with
    | nil => exact List.Perm.refl _
    | cons a xs =>
      cases xs with
      | nil => exact List.Perm.refl _
      | cons b xs =>
        change (mergeFuel (a :: b :: xs).length
          (sortFuel fuel ((a :: b :: xs).take (((a :: b :: xs).length + 1) / 2)))
          (sortFuel fuel ((a :: b :: xs).drop (((a :: b :: xs).length + 1) / 2)))).Perm _
        have h := (mergeFuel_perm (a :: b :: xs).length _ _).trans
          ((ih ((a :: b :: xs).take (((a :: b :: xs).length + 1) / 2))).append
            (ih ((a :: b :: xs).drop (((a :: b :: xs).length + 1) / 2))))
        simpa only [List.take_append_drop] using h

def structuralSort (xs : List Nat) : List Nat := sortFuel xs.length xs

theorem structuralSort_perm (xs : List Nat) :
    (structuralSort xs).Perm xs := sortFuel_perm xs.length xs

/-- A verified scan implies original-order Nodup. Insufficient fuel cannot
manufacture this conclusion: the output is always proved to be a permutation. -/
theorem nodup_of_structural_scan (xs : List Nat)
    (h : SortedOwnerCertificate.strictAdjacent (structuralSort xs) = true) :
    xs.Nodup :=
  (structuralSort_perm xs).nodup
    (SortedOwnerCertificate.strictAdjacent_nodup _ h)

theorem tiny_sort : structuralSort [2, 1] = [1, 2] := by decide +kernel

theorem tiny_scan :
    SortedOwnerCertificate.strictAdjacent (structuralSort [2, 1]) = true := by
  decide +kernel

end CurrentMain.StructuralOwnerCertificate

#print axioms CurrentMain.StructuralOwnerCertificate.mergeFuel_perm
#print axioms CurrentMain.StructuralOwnerCertificate.sortFuel_perm
#print axioms CurrentMain.StructuralOwnerCertificate.structuralSort_perm
#print axioms CurrentMain.StructuralOwnerCertificate.nodup_of_structural_scan
#print axioms CurrentMain.StructuralOwnerCertificate.tiny_sort
#print axioms CurrentMain.StructuralOwnerCertificate.tiny_scan
