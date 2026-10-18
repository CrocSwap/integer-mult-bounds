import MultitapeToolkit
import Lean.Elab.BuiltinEvalCommand
import Lean.Util.CollectAxioms

/-!
Complete defining-module audit, including private and globally named helpers.
The source inventory and aggregator are independently checked by replay.py.
No declared package axiom is admitted, even when it is unused by any theorem.
-/

open Lean Elab Command in
run_cmd do
  let env ← getEnv
  let ownedModules := env.allImportedModuleNames.filter (fun m =>
    m == `MultitapeToolkit || (`MultitapeToolkit).isPrefixOf m)
  let owns := fun name =>
    match env.getModuleIdxFor? name with
    | none => false
    | some index => ownedModules.contains (env.allImportedModuleNames[index.toNat]!)
  let names := (env.constants.toList.filter (fun p => owns p.1)).map (fun p => p.1)
  let names := names.toArray.qsort (fun a b => decide (a.toString < b.toString))
  unless names.size > 0 do
    throwError "Empty toolkit declaration audit"
  let permitted : Array Name := #[`propext, `Classical.choice, `Quot.sound]
  let mut rows : Array Json := #[]
  let mut theoremCount : Nat := 0
  for name in names do
    let info ← getConstInfo name
    let kind := match info with
      | .thmInfo _ => "theorem"
      | .defnInfo _ => "definition"
      | .opaqueInfo _ => "opaque"
      | .axiomInfo _ => "axiom"
      | _ => "other"
    if kind == "axiom" then
      throwError "Toolkit declares an axiom: {name}"
    if kind == "theorem" then theoremCount := theoremCount + 1
    let axioms ← collectAxioms name
    for ax in axioms do
      unless permitted.contains ax do
        throwError "{name} depends on forbidden axiom {ax}"
    let some index := env.getModuleIdxFor? name | throwError "Missing defining module: {name}"
    let owner := env.allImportedModuleNames[index.toNat]!
    rows := rows.push (Json.mkObj [
      ("name", toJson name.toString), ("module", toJson owner.toString),
      ("kind", toJson kind), ("axioms", toJson (axioms.map Name.toString))])
  unless theoremCount > 0 do
    throwError "No theorem reports in toolkit audit"
  let report := Json.mkObj [
    ("modules", toJson (ownedModules.map Name.toString)),
    ("declaration_names", toJson (names.map Name.toString)), ("rows", Json.arr rows)]
  if let some path ← liftIO (IO.getEnv "MULTITAPE_TOOLKIT_AUDIT_PATH") then
    liftIO (IO.FS.writeFile path report.compress)
  logInfo m!"PASS_COMPLETE_MODULE_AXIOM_AUDIT: {names.size} declarations, {theoremCount} theorems, standard axioms only"

def main : IO Unit :=
  IO.println "All toolkit modules and all their declarations passed the compile-time kernel/axiom audit."

