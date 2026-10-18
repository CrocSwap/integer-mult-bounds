import MultitapeToolkit.MarkedStreamModel

/-!
# Charged physical installation and removal of stream markers

Two literal transitions move selected heads left, set the boundary symbol,
and return to the original heads. Every unselected tape is preserved exactly.
This keeps marker preparation and cleanup out of uncharged endpoint notation.
-/
namespace MultitapeToolkit.Absolute.MarkerLifecycle

open MultitapeToolkit.Locality MarkedStreams

variable {ι : Type*} [Fintype ι]

/-- A fixed three-state local table. Neither coordinates nor lengths are read. -/
def markerProgram (selected : ι → Bool) (value : Symbol) : Program ι Symbol (Fin 3) where
  transition q scanned :=
    if q = 0 then
      some (1, fun i => (scanned i, if selected i then Move.left else Move.stay))
    else if q = 1 then
      some (2, fun i => (if selected i then value else scanned i,
        if selected i then Move.right else Move.stay))
    else none

def markerInput (heads : ι → ℤ) (cells : ι → ℤ → Symbol) : Config ι Symbol (Fin 3) :=
  ⟨0, heads, cells⟩

def markerMiddle (selected : ι → Bool) (heads : ι → ℤ)
    (cells : ι → ℤ → Symbol) : Config ι Symbol (Fin 3) :=
  ⟨1, fun i => heads i + if selected i then -1 else 0, cells⟩

def markerCells (selected : ι → Bool) (value : Symbol)
    (heads : ι → ℤ) (cells : ι → ℤ → Symbol) : ι → ℤ → Symbol :=
  fun i x => if selected i then (if x = heads i - 1 then value else cells i x) else cells i x

def markerOutput (selected : ι → Bool) (value : Symbol)
    (heads : ι → ℤ) (cells : ι → ℤ → Symbol) : Config ι Symbol (Fin 3) :=
  ⟨2, heads, markerCells selected value heads cells⟩

private theorem first_step (selected : ι → Bool) (value : Symbol)
    (heads : ι → ℤ) (cells : ι → ℤ → Symbol) :
    step (markerProgram selected value) (markerInput heads cells) =
      some (markerMiddle selected heads cells) := by
  simp only [step, markerProgram, markerInput, ↓reduceIte, Option.map_some]
  congr 1
  apply Config.ext
  · rfl
  · funext i
    cases hs : selected i <;> simp [markerMiddle, hs, moveOffset]
  · funext i x
    change (if x = heads i then cells i (heads i) else cells i x) = cells i x
    split_ifs with hx
    · simp [hx]
    · rfl

private theorem second_step (selected : ι → Bool) (value : Symbol)
    (heads : ι → ℤ) (cells : ι → ℤ → Symbol) :
    step (markerProgram selected value) (markerMiddle selected heads cells) =
      some (markerOutput selected value heads cells) := by
  have hn : (1 : Fin 3) ≠ 0 := by decide
  simp only [step, markerProgram, markerMiddle, hn, ↓reduceIte, Option.map_some]
  congr 1
  apply Config.ext
  · rfl
  · funext i
    cases hs : selected i <;> simp [markerOutput, hs, moveOffset]
  · funext i x
    cases hs : selected i
    · simp [markerOutput, markerCells, hs]
      intro hx; simp [hx]
    · simp [markerOutput, markerCells, hs, sub_eq_add_neg]

/-- Universal actual two-transition run, restoring every head and changing only
selected marker positions. No input length or pristine spectator premise. -/
theorem marker_run (selected : ι → Bool) (value : Symbol)
    (heads : ι → ℤ) (cells : ι → ℤ → Symbol) :
    Runs (markerProgram selected value) 2 (markerInput heads cells)
      (markerOutput selected value heads cells) :=
  .cons (first_step selected value heads cells)
    (.cons (second_step selected value heads cells) (.refl _))

/-- The returned state is genuinely halted, with no fictitious extra transition. -/
theorem marker_halts (selected : ι → Bool) (value : Symbol)
    (heads : ι → ℤ) (cells : ι → ℤ → Symbol) :
    Halts (markerProgram selected value) (markerOutput selected value heads cells) := by
  simp [Halts, step, markerProgram, markerOutput]

omit [Fintype ι] in
/-- The exact finite table preserves a whole unselected dirty spectator tape. -/
theorem marker_spectator (selected : ι → Bool) (value : Symbol)
    (heads : ι → ℤ) (cells : ι → ℤ → Symbol) (i : ι) (hi : selected i = false) :
    (markerOutput selected value heads cells).head i = heads i ∧
      (markerOutput selected value heads cells).cell i = cells i := by
  constructor
  · rfl
  · funext x; simp [markerOutput, markerCells, hi]

omit [Fintype ι] in
/-- Installing then removing a marker restores any old blank marker positions;
all other data are retained, even when dirty or arbitrarily long. -/
theorem install_remove_cells (selected : ι → Bool) (heads : ι → ℤ)
    (cells : ι → ℤ → Symbol) (hblank : ∀ i, selected i = true → cells i (heads i - 1) = .blank) :
    markerCells selected .blank heads (markerCells selected .separator heads cells) = cells := by
  funext i x
  cases hs : selected i
  · simp [markerCells, hs]
  · by_cases hx : x = heads i - 1
    · simp [markerCells, hs, hx, hblank i hs]
    · simp [markerCells, hs, hx]

end MultitapeToolkit.Absolute.MarkerLifecycle