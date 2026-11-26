import OAI.Computability.IntegerMultiplication.TMModel

/-! Original tape-model traces for advancing an indexed-memory cursor through occupied records. -/

namespace S008.Compiler

open OAI.Computability.IntegerMultiplication

inductive Letter where
  | blank | home | bit (b : Bool) | delimiter | count
  deriving DecidableEq, Repr, Inhabited

instance : Fintype Letter := Fintype.ofList [.blank,.home,.bit false,.bit true,.delimiter,.count] (by
  intro x
  cases x with
  | bit b => cases b <;> decide
  | _ => decide)

end S008.Compiler
