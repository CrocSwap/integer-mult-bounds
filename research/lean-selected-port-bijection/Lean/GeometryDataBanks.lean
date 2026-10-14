import SignedTraceCore

/-! Prop-valued leaf certificates keep literal lookup data independent of the
modules that establish validity of their entries. -/
namespace CurrentMain.GeometryDataBanks
open CurrentMain.SignedTrace
universe u
variable {α : Type u}

inductive AllLeaves (P : α → Prop) : Table α → Prop where
  | leaf {a : α} : P a → AllLeaves P (.leaf a)
  | fork {l r : Table α} : AllLeaves P l → AllLeaves P r → AllLeaves P (.fork l r)

theorem allLeaves_get {P : α → Prop} {t : Table α}
    (certificate : AllLeaves P t) (i : Nat) : P (get t i) := by
  induction certificate generalizing i with
  | leaf h => exact h
  | fork _ _ left right =>
    simp only [CurrentMain.SignedTrace.get]
    split
    · exact left (i/2)
    · exact right (i/2)

def bankLookup (bits : Nat) (bank : Table (Table α)) (i : Nat) : α :=
  get (get bank (i/2^bits)) (i%2^bits)

theorem bankLookup_valid {P : α → Prop} (bits : Nat) {bank : Table (Table α)}
    (certificate : AllLeaves (fun t => ∀ j, P (get t j)) bank) (i : Nat) :
    P (bankLookup bits bank i) :=
  allLeaves_get certificate (i/2^bits) (i%2^bits)

theorem bankLookup_allLeaves {P : α → Prop} (bits : Nat) {bank : Table (Table α)}
    (certificate : AllLeaves (AllLeaves P) bank) (i : Nat) :
    P (bankLookup bits bank i) :=
  allLeaves_get (allLeaves_get certificate (i/2^bits)) (i%2^bits)

end CurrentMain.GeometryDataBanks
#print axioms CurrentMain.GeometryDataBanks.allLeaves_get
#print axioms CurrentMain.GeometryDataBanks.bankLookup_valid
#print axioms CurrentMain.GeometryDataBanks.bankLookup_allLeaves
