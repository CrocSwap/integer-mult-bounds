import Init.Data.List.Sort.Lemmas

/-!
Source-only generic certificate: a strict adjacent scan after merge sort
implies no duplicates in the original list. No sortedness or permutation is
assumed. The scan truth is a premise to this generic lemma; the concrete
client proposes its own unrun finite check. Original owner order is untouched.

Reuses Lean's mergeSort_perm and Perm.nodup, pinned at Lean4 commit
6741444a63eec253a7eae7a83f1beb3de015023d. Preserve Lean FRO and Kim Morrison,
Eric Wieser and Francois G. Dorais credits and Apache-2.0 notices in the
retained primary sources. New proof prepared with OpenAI assistance.
This source is uncompiled; no compiler-time improvement is claimed.
-/
set_option Elab.async false

namespace CurrentMain.SortedOwnerCertificate

def strictFrom (a : Nat) : List Nat → Bool
  | [] => true
  | b :: xs => decide (a < b) && strictFrom b xs

def strictAdjacent : List Nat → Bool
  | [] => true
  | a :: xs => strictFrom a xs

private theorem strictFrom_spec (xs : List Nat) :
    ∀ a, strictFrom a xs = true →
      (∀ b ∈ xs, a < b) ∧ xs.Pairwise (fun b c => b < c) := by
  induction xs with
  | nil =>
    intro a h
    refine ⟨?_, List.Pairwise.nil⟩
    intro b hb
    cases hb
  | cons b xs ih =>
    intro a h
    change (decide (a < b) && strictFrom b xs) = true at h
    obtain ⟨habBool, hrest⟩ := Bool.and_eq_true_iff.mp h
    have hab : a < b := of_decide_eq_true habBool
    obtain ⟨hhead, htail⟩ := ih b hrest
    constructor
    · intro c hc
      rcases List.mem_cons.mp hc with hc | hc
      · subst c
        exact hab
      · exact Nat.lt_trans hab (hhead c hc)
    · exact List.Pairwise.cons hhead htail

theorem strictAdjacent_nodup (xs : List Nat) (h : strictAdjacent xs = true) :
    xs.Nodup := by
  cases xs with
  | nil => exact List.Pairwise.nil
  | cons a xs =>
    obtain ⟨hhead, htail⟩ := strictFrom_spec xs a h
    exact (List.Pairwise.cons hhead htail).imp (fun hlt => Nat.ne_of_lt hlt)

/-- The permutation theorem is constructive and independent of scan success.
Only the certificate computation uses sorted order; the conclusion is about xs. -/
theorem nodup_of_sorted_adjacent (xs : List Nat)
    (h : strictAdjacent (xs.mergeSort (fun a b => decide (a ≤ b))) = true) :
    xs.Nodup :=
  (List.mergeSort_perm xs (fun a b => decide (a ≤ b))).nodup
    (strictAdjacent_nodup _ h)

end CurrentMain.SortedOwnerCertificate

#print axioms CurrentMain.SortedOwnerCertificate.strictAdjacent_nodup
#print axioms CurrentMain.SortedOwnerCertificate.nodup_of_sorted_adjacent
