import Lean
import CyclicSchur
import Counterexamples

open Lean Elab Command

/- Check every theorem in the package namespace, including equation lemmas. -/
def CyclicSchurAudit.check : CommandElabM Unit := do
  let env ← getEnv
  let mut names : Array Name := #[]
  for (name, _) in env.constants do
    if (`CyclicSchur).isPrefixOf name then
      if getOriginalConstKind? env name == some .axiom then
        throwError "Package declares an axiom: {name}"
      if getOriginalConstKind? env name == some .thm then
        names := names.push name
  if names.isEmpty then
    throwError "No package theorems were found"
  let allowed := #[`propext, `Classical.choice, `Quot.sound]
  for name in names.qsort (fun a b => a.toString < b.toString) do
    let axioms ← collectAxioms name
    for axiomName in axioms do
      unless allowed.contains axiomName do
        throwError "Disallowed axiom in {name}: {axiomName}"
    logInfo m!"AXIOMS {name}: {axioms.toList}"
  logInfo m!"PASS_CYCLIC_SCHUR: {names.size} theorems; standard axioms only"

run_cmd CyclicSchurAudit.check
