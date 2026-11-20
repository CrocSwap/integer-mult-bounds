/-
UniRowsMeta (lane ROWS, Nov 19).  Two small elaboration helpers for big generated data; both only BUILD terms,
every declaration they add is checked by the Lean kernel as usual (no axioms, no native code, no sorry).
* `rows_sv N "…"` / `rows_nat N "…"` : define `N : Tr SV` / `N : Tr Nat` (depth 11) from a compact string
    (the elaborator is too slow on 50k-entry literals): leaves j = 0..2^11-1 separated by '|';
    an SV leaf is a comma list "o:v" (v signed decimal), a Nat leaf a decimal.
* `kernel_rfl N : lhs = rhs` : adds theorem N with proof `Eq.refl rhs`, checked ONLY by the kernel's
    definitional-equality test (the same mechanism as `decide +kernel`, minus the Bool/Decidable wrapper).
-/
import Lean
import Nov15.UniRowsDefs

namespace UniRows
open Lean Elab Command Meta

private def natE (n : Nat) : Expr := .lit (.natVal n)

private def intE (v : Int) : Expr :=
  if v ≥ 0 then mkApp (mkConst ``Int.ofNat) (natE v.toNat)
  else mkApp (mkConst ``Int.negSucc) (natE ((-v).toNat - 1))

private def pairT : Expr := mkApp2 (mkConst ``Prod [0, 0]) (mkConst ``Nat) (mkConst ``Int)

private def svE (s : String) : Expr := Id.run do
  let items := (s.splitOn ",").filter (· ≠ "")
  let mut acc := mkApp (mkConst ``List.nil [0]) pairT
  for it in items.reverse do
    let ps := it.splitOn ":"
    let o := (ps.getD 0 "0").toNat!
    let v := (ps.getD 1 "0").toInt!
    let p := mkApp4 (mkConst ``Prod.mk [0, 0]) (mkConst ``Nat) (mkConst ``Int) (natE o) (intE v)
    acc := mkApp3 (mkConst ``List.cons [0]) pairT p acc
  return acc

private def svT : Expr := mkApp (mkConst ``List [0]) pairT

/-- depth-d tree over leaves (index j at path bits LSB-first, as UniInhabit.gt). -/
private partial def treeE (T : Expr) (dflt : Expr) (lv : Array Expr) (d j0 step : Nat) : Expr :=
  if d = 0 then mkApp2 (mkConst ``UniInhabit.Tr.lf) T (lv.getD j0 dflt)
  else mkApp3 (mkConst ``UniInhabit.Tr.nd) T (treeE T dflt lv (d - 1) j0 (step * 2)) (treeE T dflt lv (d - 1) (j0 + step) (step * 2))

private def addTree (nm : Name) (T dflt : Expr) (leaves : Array Expr) : CommandElabM Unit := do
  let full := (← getCurrNamespace) ++ nm
  let dv : DefinitionVal :=
    { name := full, levelParams := [], type := mkApp (mkConst ``UniInhabit.Tr) T,
      value := treeE T dflt leaves 11 0 1, hints := .regular 0, safety := .safe }
  liftCoreM <| addDecl (.defnDecl dv)

syntax (name := rowsSV) "rows_sv " ident str : command
syntax (name := rowsNat) "rows_nat " ident str : command

@[command_elab rowsSV] def elabRowsSV : CommandElab := fun stx => do
  let some s := stx[2].isStrLit? | throwError "rows_sv: string literal expected"
  addTree stx[1].getId svT (svE "") ((s.splitOn "|").toArray.map svE)

@[command_elab rowsNat] def elabRowsNat : CommandElab := fun stx => do
  let some s := stx[2].isStrLit? | throwError "rows_nat: string literal expected"
  addTree stx[1].getId (mkConst ``Nat) (natE 0) ((s.splitOn "|").toArray.map (fun x => natE x.toNat!))

syntax (name := kernelRfl) "kernel_rfl " ident " : " term : command

@[command_elab kernelRfl] def elabKernelRfl : CommandElab := fun stx => do
  let nm := stx[1].getId
  let ns ← getCurrNamespace
  let full := ns ++ nm
  let ty ← liftTermElabM do
    let ty ← Term.elabType stx[3]
    Term.synthesizeSyntheticMVarsNoPostponing
    instantiateMVars ty
  let some (α, _, rhs) := ty.eq? | throwError "kernel_rfl: equation expected"
  let lvl ← liftTermElabM do
    let u ← getLevel α
    instantiateLevelMVars u
  let tv : TheoremVal :=
    { name := full, levelParams := [], type := ty, value := mkApp2 (mkConst ``Eq.refl [lvl]) α rhs }
  liftCoreM <| addDecl (.thmDecl tv)

end UniRows
