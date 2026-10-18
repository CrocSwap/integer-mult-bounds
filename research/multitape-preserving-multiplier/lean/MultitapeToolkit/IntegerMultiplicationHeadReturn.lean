import MultitapeToolkit.IntegerMultiplicationEngine

/-!
# Charged restoration of every multiplication head to physical origin

Four finite states scan the padded output forward, moving the accumulator once
per bit and the two operand heads once per pair. A reverse scan restores the
output head. Every transition rewrites its scanned symbols unchanged. Lists,
positions and widths below are proof descriptions, never machine registers.
-/
set_option autoImplicit false
namespace MultitapeToolkit.IntegerMultiplicationHeadReturn
open MultitapeToolkit MultitapeToolkit.Absolute
open MultitapeToolkit.IntegerMultiplicationEngine MultitapeToolkit.BinaryMultiplication Lax51Proofs.RamToTM

inductive Phase where
  | forward (parity : Bool)
  | backward
  | done
  deriving DecidableEq, Fintype

def forwardMoves (parity : Bool) : MulStack → Move
  | .sumReverse | .accumulator => .right
  | .multiplier | .multiplicand => if parity then .left else .stay
  | _ => .stay

def outputMove (m : Move) : MulStack → Move :=
  fun k => if k = .sumReverse then m else .stay

def program : Program MulStack (Option Bool) Phase where
  transition q r := match q with
    | .forward parity => match r .sumReverse with
      | some _ => some (.forward (!parity),fun k => (r k,forwardMoves parity k))
      | none => some (.backward,fun k => (r k,outputMove .left k))
    | .backward => match r .sumReverse with
      | some _ => some (.backward,fun k => (r k,outputMove .left k))
      | none => some (.done,fun k => (r k,outputMove .right k))
    | .done => none

noncomputable def input (n product : ℕ) : MultitapeToolkit.Absolute.Config MulStack (Option Bool) Phase :=
  ⟨.forward false,(cleanOutput n product).head,(cleanOutput n product).cell⟩

noncomputable def output (n product : ℕ) : MultitapeToolkit.Absolute.Config MulStack (Option Bool) Phase :=
  ⟨.done,fun _ => 0,(cleanOutput n product).cell⟩

/-- Every actual step of this table preserves the entire tape bank. -/
theorem step_preserves_cells {c d : MultitapeToolkit.Absolute.Config MulStack (Option Bool) Phase}
    (h : MultitapeToolkit.Absolute.step program c = some d) : d.cell = c.cell := by
  cases hq : c.state with
  | forward parity =>
    cases hs : c.cell .sumReverse (c.head .sumReverse) <;>
      simp only [MultitapeToolkit.Absolute.step,program,hq,hs,Option.map_some,Option.some.injEq] at h
    all_goals
      rw [← h]
      funext k x
      dsimp
      split <;> rename_i hx
      · simp [hx]
      · rfl
  | backward =>
    cases hs : c.cell .sumReverse (c.head .sumReverse) <;>
      simp only [MultitapeToolkit.Absolute.step,program,hq,hs,Option.map_some,Option.some.injEq] at h
    all_goals
      rw [← h]
      funext k x
      dsimp
      split <;> rename_i hx
      · simp [hx]
      · rfl
  | done => simp [MultitapeToolkit.Absolute.step,program,hq] at h

private theorem scanned_step (q q' : Phase) (H H' : MulStack → ℤ)
    (C : MulStack → ℤ → Option Bool) (moves : MulStack → Move)
    (ht : program.transition q (fun k => C k (H k)) =
      some (q',fun k => (C k (H k),moves k)))
    (hh : ∀ k, H' k = H k + MultitapeToolkit.Locality.moveOffset (moves k)) :
    MultitapeToolkit.Absolute.step program ⟨q,H,C⟩ = some ⟨q',H',C⟩ := by
  simp only [MultitapeToolkit.Absolute.step,ht,Option.map_some]
  congr 1
  apply MultitapeToolkit.Absolute.Config.ext
  · rfl
  · funext k
    exact (hh k).symm
  · funext k x
    by_cases hx : x = H k <;> simp [hx]

/-- Proof-only bank after k complete pairs of output symbols. -/
def forwardCfg (n k : ℕ) (C : MulStack → ℤ → Option Bool) :
    MultitapeToolkit.Absolute.Config MulStack (Option Bool) Phase :=
  ⟨.forward false,fun i => match i with
    | .sumReverse => 2*(k : ℤ)
    | .accumulator => -2*(n : ℤ)+2*(k : ℤ)
    | .multiplier | .multiplicand => (n : ℤ)-(k : ℤ)
    | _ => 0,C⟩

/-- Proof-only bank between the two symbols of a pair. -/
def halfCfg (n k : ℕ) (C : MulStack → ℤ → Option Bool) :
    MultitapeToolkit.Absolute.Config MulStack (Option Bool) Phase :=
  ⟨.forward true,fun i => match i with
    | .sumReverse => 2*(k : ℤ)+1
    | .accumulator => -2*(n : ℤ)+2*(k : ℤ)+1
    | .multiplier | .multiplicand => (n : ℤ)-(k : ℤ)
    | _ => 0,C⟩

def backwardCfg (x : ℤ) (C : MulStack → ℤ → Option Bool) :
    MultitapeToolkit.Absolute.Config MulStack (Option Bool) Phase :=
  ⟨.backward,fun k => if k=.sumReverse then x else 0,C⟩

private theorem pair_step (n k : ℕ) (C : MulStack → ℤ → Option Bool)
    (b c : Bool) (hb : C .sumReverse (2*(k : ℤ)) = some b)
    (hc : C .sumReverse (2*(k : ℤ)+1) = some c) :
    MultitapeToolkit.Absolute.Runs program 2 (forwardCfg n k C) (forwardCfg n (k+1) C) := by
  have h1 : MultitapeToolkit.Absolute.step program (forwardCfg n k C) = some (halfCfg n k C) := by
    apply scanned_step (.forward false) (.forward true) _ _ C (forwardMoves false)
    · simp [program,hb]
    · intro i; cases i <;> simp [forwardMoves,MultitapeToolkit.Locality.moveOffset]
  have h2 : MultitapeToolkit.Absolute.step program (halfCfg n k C) = some (forwardCfg n (k+1) C) := by
    apply scanned_step (.forward true) (.forward false) _ _ C (forwardMoves true)
    · simp [program,hc]
    · intro i; cases i <;> simp [forwardMoves,MultitapeToolkit.Locality.moveOffset] <;> omega
  exact .cons h1 (.cons h2 (.refl _))

private theorem forward_run (n k r : ℕ) (C : MulStack → ℤ → Option Bool)
    (hkr : k+r=n) (hword : ∀ j : ℕ, j<2*n → ∃ b, C .sumReverse (j : ℤ) = some b) :
    MultitapeToolkit.Absolute.Runs program (2*r) (forwardCfg n k C) (forwardCfg n n C) := by
  induction r generalizing k with
  | zero =>
    have hk : k=n := by omega
    subst k
    exact .refl _
  | succ r ih =>
    obtain ⟨b,hb⟩ := hword (2*k) (by omega)
    obtain ⟨c,hc⟩ := hword (2*k+1) (by omega)
    have hp := pair_step n k C b c (by simpa using hb) (by simpa using hc)
    have ht := MultitapeToolkit.Absolute.Trace.runs_trans program hp (ih (k+1) (by omega))
    simpa [Nat.mul_succ,Nat.add_assoc,Nat.add_comm,Nat.add_left_comm] using ht

private theorem turn_step (n : ℕ) (C : MulStack → ℤ → Option Bool)
    (hend : C .sumReverse (2*(n : ℤ)) = none) :
    MultitapeToolkit.Absolute.step program (forwardCfg n n C) =
      some (backwardCfg (2*(n : ℤ)-1) C) := by
  apply scanned_step (.forward false) .backward _ _ C (outputMove .left)
  · simp [program,hend]
  · intro i; cases i <;> simp [outputMove,MultitapeToolkit.Locality.moveOffset]
    all_goals omega

private theorem backward_run (n m : ℕ) (C : MulStack → ℤ → Option Bool)
    (hm : m≤2*n) (hword : ∀ j : ℕ, j<2*n → ∃ b, C .sumReverse (j : ℤ)=some b) :
    MultitapeToolkit.Absolute.Runs program m (backwardCfg ((m : ℤ)-1) C) (backwardCfg (-1) C) := by
  induction m with
  | zero => exact .refl _
  | succ m ih =>
    obtain ⟨b,hb⟩ := hword m (by omega)
    have hs : MultitapeToolkit.Absolute.step program (backwardCfg (m : ℤ) C) =
        some (backwardCfg ((m : ℤ)-1) C) := by
      apply scanned_step .backward .backward _ _ C (outputMove .left)
      · simp [program,hb]
      · intro i; cases i <;> simp [outputMove,MultitapeToolkit.Locality.moveOffset]
        all_goals omega
    simpa using MultitapeToolkit.Absolute.Runs.cons hs (ih (by omega))

private theorem finish_step (C : MulStack → ℤ → Option Bool)
    (hstart : C .sumReverse (-1) = none) :
    MultitapeToolkit.Absolute.step program (backwardCfg (-1) C) =
      some ⟨.done,fun _ => 0,C⟩ := by
  apply scanned_step .backward .done _ _ C (outputMove .right)
  · simp [program,hstart]
  · intro i; cases i <;> simp [outputMove,MultitapeToolkit.Locality.moveOffset]

/-- Full endpoint bank equality and genuine halt after exactly four n plus two
physical transitions, including the empty output case. -/
theorem exact_correct (n product : ℕ) :
    MultitapeToolkit.Absolute.Runs program (4*n+2) (input n product) (output n product) ∧
      MultitapeToolkit.Absolute.Halts program (output n product) := by
  let C := (cleanOutput n product).cell
  have hword : ∀ j : ℕ, j<2*n → ∃ b, C .sumReverse (j : ℤ)=some b := by
    intro j hj
    have hlen : ((fixedBits (2*n) product).reverse).length = 2*n := by simp
    have hj' : j < ((fixedBits (2*n) product).reverse).length := by omega
    refine ⟨((fixedBits (2*n) product).reverse)[j],?_⟩
    change StackOriginSerializer.originWord _ (j : ℤ) = _
    simpa only [StackOriginSerializer.originWord,Int.natCast_nonneg,ite_true,Int.toNat_natCast]
      using (List.getElem?_eq_getElem hj')
  have hend : C .sumReverse (2*(n : ℤ))=none := by
    simp [C,cleanOutput,StackOriginSerializer.originWord]
  have hstart : C .sumReverse (-1)=none := by
    simp [C,cleanOutput,StackOriginSerializer.originWord]
  have hi : input n product = forwardCfg n 0 C := by
    apply MultitapeToolkit.Absolute.Config.ext
    · rfl
    · funext i; cases i <;> simp [input,cleanOutput,forwardCfg]
    · rfl
  have hf := forward_run n 0 n C (by omega) hword
  have ht := MultitapeToolkit.Absolute.Runs.cons (turn_step n C hend)
    (backward_run n (2*n) C (by omega) hword)
  have hall := MultitapeToolkit.Absolute.Trace.runs_trans program
    (MultitapeToolkit.Absolute.Trace.runs_trans program hf ht)
    (MultitapeToolkit.Absolute.Runs.cons (finish_step C hstart) (.refl _))
  constructor
  · rw [hi]
    convert hall using 1 <;> simp [output,C]
    omega
  · simp [MultitapeToolkit.Absolute.Halts,MultitapeToolkit.Absolute.step,program,output]

@[simp] theorem input_heads (n product : ℕ) : (input n product).head = (cleanOutput n product).head := rfl
@[simp] theorem input_cells (n product : ℕ) : (input n product).cell = (cleanOutput n product).cell := rfl
@[simp] theorem output_heads (n product : ℕ) : (output n product).head = fun _ => 0 := rfl
@[simp] theorem output_cells (n product : ℕ) : (output n product).cell = (cleanOutput n product).cell := rfl

theorem phase_card : Fintype.card Phase = 4 := by decide
end MultitapeToolkit.IntegerMultiplicationHeadReturn
