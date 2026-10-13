import BlockComposition

/-! Register-preserving synthesis for verified block-stable straight-line DAGs.
The outer may use actual matrix transpose. Every multiplication instruction is
replaced by a scalar leaf, while additions, fixed scalings and register sharing
retain their actual order. The unrefined outer's correctness is a normal input. -/
namespace PersonalMatrix.DAG
open PersonalMatrix.Hybrid
variable {K : Type*} [CommRing K] {a b ell : ℕ}

inductive Op (K : Type*) where
  | copy (x : ℕ)
  | add (x y : ℕ)
  | sub (x y : ℕ)
  | scale (c : K) (x : ℕ)
  | transpose (x : ℕ)
  | mul (x y : ℕ)
structure Instruction (K : Type*) where
  destination : ℕ
  operation : Op K
abbrev State (K : Type*) (b : ℕ) := ℕ → Square (K := K) b

def Op.isMul : Op K → Bool
  | .mul _ _ => true
  | _ => false

def evalOp : Op K → State K b → Square (K := K) b
  | .copy x, s => s x
  | .add x y, s => s x + s y
  | .sub x y, s => s x - s y
  | .scale c x, s => c • s x
  | .transpose x, s => (s x).transpose
  | .mul x y, s => s x * s y

def step (i : Instruction K) (s : State K b) : State K b :=
  Function.update s i.destination (evalOp i.operation s)

def translatedStep (l : Leaf K b ell) (i : Instruction K) (s : State K b) :
    State K b × List (Fin ell → K) :=
  match i.operation with
  | .mul x y =>
    let products := leafProducts l (s x) (s y)
    (Function.update s i.destination (leafReconstruct l products), [products])
  | _ => (step i s, [])

theorem translatedStep_state (l : Leaf K b ell) (hl : LeafValid l)
    (i : Instruction K) (s : State K b) : (translatedStep l i s).1 = step i s := by
  rcases i with ⟨dest,op⟩
  cases op <;> try rfl
  rename_i x y
  change Function.update s dest (leafEval l (s x) (s y)) =
    Function.update s dest (s x * s y)
  rw [hl]

theorem translatedStep_trace (l : Leaf K b ell) (i : Instruction K) (s : State K b) :
    (translatedStep l i s).2.length = if i.operation.isMul then 1 else 0 := by
  rcases i with ⟨dest,op⟩
  cases op <;> rfl

def run : List (Instruction K) → State K b → State K b
  | [],s => s
  | i::rest,s => run rest (step i s)

def translatedRun (l : Leaf K b ell) : List (Instruction K) → State K b →
    State K b × List (Fin ell → K)
  | [],s => (s,[])
  | i::rest,s =>
    let first := translatedStep l i s
    let remaining := translatedRun l rest first.1
    (remaining.1, first.2 ++ remaining.2)

theorem translatedRun_state (l : Leaf K b ell) (hl : LeafValid l)
    (p : List (Instruction K)) (s : State K b) : (translatedRun l p s).1 = run p s := by
  induction p generalizing s with
  | nil => rfl
  | cons i rest ih =>
    change (translatedRun l rest (translatedStep l i s).1).1 = run rest (step i s)
    rw [ih, translatedStep_state l hl]

theorem translatedRun_trace (l : Leaf K b ell) (p : List (Instruction K)) (s : State K b) :
    (translatedRun l p s).2.length = p.countP (fun i => i.operation.isMul) := by
  induction p generalizing s with
  | nil => rfl
  | cons i rest ih =>
    simp only [translatedRun, List.length_append, translatedStep_trace, ih, List.countP_cons]
    split <;> omega

/-- Initialise only the actual A/B input blocks. No desired product is placed in
an initial register; all other registers are zero. -/
noncomputable def inputState (A B : Full (K := K) a b) : State K b :=
  fun n => if hn : n < Fintype.card (Input a) then
    match (Fintype.equivFin (Input a)).symm ⟨n,hn⟩ with
    | .inl p => blocks A p.1 p.2
    | .inr p => blocks B p.1 p.2
  else 0

def readOutput (outputs : Fin a → Fin a → ℕ) (s : State K b) : Blocked (K := K) a b :=
  fun i j => s (outputs i j)

noncomputable def OuterDAGValid (p : List (Instruction K)) (outputs : Fin a → Fin a → ℕ) : Prop :=
  ∀ A B : Full (K := K) a b, flatten (readOutput outputs (run p (inputState A B))) = A*B

noncomputable def translatedEval (l : Leaf K b ell) (p : List (Instruction K))
    (outputs : Fin a → Fin a → ℕ) (A B : Full (K := K) a b) : Full (K := K) a b :=
  flatten (readOutput outputs (translatedRun l p (inputState A B)).1)

def scalarGateCount (trace : List (Fin ell → K)) : ℕ := trace.length * ell

theorem translated_cost (l : Leaf K b ell) (p : List (Instruction K)) (s : State K b) :
    scalarGateCount (translatedRun l p s).2 = p.countP (fun i => i.operation.isMul) * ell := by
  rw [scalarGateCount, translatedRun_trace]

/-- Certified synthesis: original outer validity is required only before the
leaf refinement. The new hybrid identity and cost are proved conclusions. -/
theorem synthesized_correct_and_cost (l : Leaf K b ell) (hl : LeafValid l)
    (p : List (Instruction K)) (outputs : Fin a → Fin a → ℕ)
    (hp : OuterDAGValid (b := b) p outputs) (A B : Full (K := K) a b) :
    translatedEval l p outputs A B = A*B ∧
      scalarGateCount (translatedRun l p (inputState A B)).2 =
        p.countP (fun i => i.operation.isMul) * ell := by
  constructor
  · unfold translatedEval
    rw [translatedRun_state l hl]
    exact hp A B
  · exact translated_cost l p (inputState A B)

#print axioms translatedStep_state
#print axioms translatedRun_state
#print axioms translatedRun_trace
#print axioms translated_cost
#print axioms synthesized_correct_and_cost
#check @synthesized_correct_and_cost
end PersonalMatrix.DAG
