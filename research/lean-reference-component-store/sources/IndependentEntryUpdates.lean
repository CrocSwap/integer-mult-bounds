import Mathlib.Data.List.Nodup
import Mathlib.Logic.Function.Basic

/-!
Verbatim generic namespace slice of Current799EntryFold.lean at 9868c4be.
The historical source and terminal are pinned in SOURCE_BINDING.json.
Only imports/header are new. This slice is uncompiled under the smaller imports.
Do not import it alongside Current799EntryFold: the declarations have the same
names. No historical 728-register data or physical executor is imported.
Prepared with OpenAI assistance. Apache-2.0.
-/
namespace CurrentMain.IndependentEntryFold

variable {I M : Type*} [DecidableEq I]

/-- Chronological one-register updates; each operator reads its own current value. -/
def runUpdates (act : I → M → M) : List I → (I → M) → (I → M)
  | [], h => h
  | j :: js, h => runUpdates act js (Function.update h j (act j (h j)))

theorem runUpdates_eq_foldl (act : I → M → M) (js : List I) (h : I → M) :
    runUpdates act js h =
      js.foldl (fun s j => Function.update s j (act j (s j))) h := by
  induction js generalizing h with
  | nil => rfl
  | cons j js ih => simp only [runUpdates, List.foldl_cons, ih]

/-- Operators elsewhere cannot affect this coordinate, even if those operators
are nonlinear or the other coordinates are repeated. -/
theorem runUpdates_of_not_mem (act : I → M → M) (js : List I)
    (i : I) (hi : i ∉ js) (h : I → M) :
    runUpdates act js h i = h i := by
  induction js generalizing h with
  | nil => rfl
  | cons j js ih =>
      have hs : i ≠ j ∧ i ∉ js := by
        simpa only [List.mem_cons, not_or] using hi
      rw [runUpdates, ih hs.2, Function.update_of_ne hs.1]

/-- Membership and no duplicates suffice; operators on other coordinates are
unrestricted. There is no permutation or commutativity premise on the operators. -/
theorem runUpdates_of_mem (act : I → M → M) (js : List I)
    (hnd : js.Nodup) (i : I) (hi : i ∈ js) (h : I → M) :
    runUpdates act js h i = act i (h i) := by
  induction js generalizing h with
  | nil => simp only [List.not_mem_nil] at hi
  | cons j js ih =>
      have hn : j ∉ js ∧ js.Nodup := List.nodup_cons.mp hnd
      by_cases hij : i = j
      · subst i
        rw [runUpdates, runUpdates_of_not_mem act js j hn.1,
          Function.update_self]
      · have him : i ∈ js := (List.mem_cons.mp hi).resolve_left hij
        rw [runUpdates, ih hn.2 him, Function.update_of_ne hij]

end CurrentMain.IndependentEntryFold
