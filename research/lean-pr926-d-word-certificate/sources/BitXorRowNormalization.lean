import BitXorRowPullback
import StructuralOwnerCertificate

/-!
Parity-list normalization reuses the accepted structurally recursive Nat sort
and its unconditional permutation proof. Adjacent equal donors are canceled
with explicit fuel; exhaustion retains the remaining row, so every fuel value
preserves parity. No sortedness or complete cancellation hypothesis is needed
for soundness. Equality of two computed normal forms therefore proves equality
of their donor parity on arbitrary incoming bits, including all singleton bits.

This is intended to replace repeated661-column scans in historical PR926 full
row certificates. It does not establish any concrete row equality by itself.
Original ordered donor multiplicity is preserved through proved permutation
and XOR cancellation, rather than discarded by a set conversion.
Reuses bank's StructuralOwnerCertificate/SortedOwnerCertificate and their Lean
library credits, PR590/597 ordered semantics, PR774 algebra, and Gareth
Davidson/bitplane PR915/926 with PR733 credit. Apache-2.0; OpenAI assistance.
Uncompiled source proposal.
-/
namespace CurrentMain.BitXorRowNormalization
open BitXor BitXorRowPullback StructuralOwnerCertificate
set_option Elab.async false
variable {Reg : Type} [DecidableEq Reg]

/-- Donor parity is invariant under permutations, retaining multiplicity. -/
theorem donorXor_perm {xs ys : List Reg} (h : xs.Perm ys) (s : State Reg) :
    donorXor xs s = donorXor ys s := by
  induction h with
  | nil => rfl
  | cons x h ih => exact congrArg (fun b => s x ^^ b) ih
  | swap x y rest =>
    change (s y ^^ (s x ^^ donorXor rest s)) =
      (s x ^^ (s y ^^ donorXor rest s))
    exact Bool.xor_left_comm _ _ _
  | trans h₁ h₂ ih₁ ih₂ => exact ih₁.trans ih₂

/-- Exhaustion is safe: leave the remaining row intact. -/
def cancelFuel : Nat → List Reg → List Reg
  | 0, xs => xs
  | _ + 1, [] => []
  | _ + 1, [x] => [x]
  | fuel + 1, x :: y :: rest =>
      if x = y then cancelFuel fuel rest
      else x :: cancelFuel fuel (y :: rest)

theorem cancelFuel_sound (fuel : Nat) (xs : List Reg) (s : State Reg) :
    donorXor (cancelFuel fuel xs) s = donorXor xs s := by
  induction fuel generalizing xs with
  | zero => rfl
  | succ fuel ih =>
    cases xs with
    | nil => rfl
    | cons x xs =>
      cases xs with
      | nil => rfl
      | cons y rest =>
        by_cases hxy : x = y
        · subst y
          simp only [cancelFuel, if_pos rfl, if_true, ih, donorXor,
            ← Bool.xor_assoc, Bool.xor_self, Bool.false_xor]
        · simp only [cancelFuel, if_neg hxy, donorXor]
          exact congrArg (fun b => s x ^^ b) (ih (y :: rest))

/-- The numeric key is decoded back to exactly the original register. -/
def sortedRow (key : Reg → Nat) (decode : Nat → Reg) (xs : List Reg) : List Reg :=
  (structuralSort (xs.map key)).map decode

theorem sortedRow_perm (key : Reg → Nat) (decode : Nat → Reg)
    (hdecode : ∀ r, decode (key r) = r) (xs : List Reg) :
    (sortedRow key decode xs).Perm xs := by
  have h := (structuralSort_perm (xs.map key)).map decode
  have hb : (xs.map key).map decode = xs := by
    clear h
    induction xs with
    | nil => rfl
    | cons x xs ih => simp only [List.map_cons, hdecode, ih]
  exact h.trans (List.Perm.of_eq hb)

def normalForm (key : Reg → Nat) (decode : Nat → Reg) (xs : List Reg) : List Reg :=
  let row := sortedRow key decode xs
  cancelFuel row.length row

theorem normalForm_sound (key : Reg → Nat) (decode : Nat → Reg)
    (hdecode : ∀ r, decode (key r) = r) (xs : List Reg) (s : State Reg) :
    donorXor (normalForm key decode xs) s = donorXor xs s := by
  rw [normalForm, cancelFuel_sound]
  exact donorXor_perm (sortedRow_perm key decode hdecode xs) s

/-- An actual equality of normal forms is a finite certificate for all states.
It cannot create a false equality even if sorting/cancellation fuel runs out. -/
theorem donorXor_eq_of_normalForm (key : Reg → Nat) (decode : Nat → Reg)
    (hdecode : ∀ r, decode (key r) = r) (xs ys : List Reg)
    (h : normalForm key decode xs = normalForm key decode ys) (s : State Reg) :
    donorXor xs s = donorXor ys s := by
  rw [← normalForm_sound key decode hdecode xs s,
    ← normalForm_sound key decode hdecode ys s, h]

end CurrentMain.BitXorRowNormalization
#print axioms CurrentMain.BitXorRowNormalization.donorXor_perm
#print axioms CurrentMain.BitXorRowNormalization.cancelFuel_sound
#print axioms CurrentMain.BitXorRowNormalization.donorXor_eq_of_normalForm
