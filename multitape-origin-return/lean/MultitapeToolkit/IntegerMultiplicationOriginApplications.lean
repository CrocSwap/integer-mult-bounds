import MultitapeToolkit.IntegerMultiplicationOriginRestored
import MultitapeToolkit.IntegerMultiplicationProductApplications
set_option autoImplicit false
/-! Applications of the concrete origin-restored multiplication program. The
selected six heads physically return to zero; spectator tapes retain arbitrary
heads and arbitrary cells. Input width and residue labels are supplied ABI data. -/
namespace MultitapeToolkit.IntegerMultiplicationOriginApplications
open MultitapeToolkit.BinaryMultiplication Lax51Proofs.RamToTM
open MultitapeToolkit.Absolute
open MultitapeToolkit.IntegerMultiplicationOriginRestored
open MultitapeToolkit.IntegerMultiplicationProductApplications

noncomputable def minimalInput (a b : ℕ) := input (commonWidth a b) a b

/-- The original literal padded operand ABI survives the physical return extension. -/
theorem minimalInput_operands (a b : ℕ) :
    (minimalInput a b).cell .multiplier = StackOriginSerializer.sourceStack 0
      (b.bits ++ List.replicate (commonWidth a b-b.size) false) ∧
    (minimalInput a b).cell .multiplicand = StackOriginSerializer.sourceStack 0
      (a.bits ++ List.replicate (commonWidth a b-a.size) false) := by
  have h := input_operands (commonWidth a b) a b
  rw [fixedBits_eq_bits_padding b (commonWidth a b) (le_max_right a.size b.size),
    fixedBits_eq_bits_padding a (commonWidth a b) (le_max_left a.size b.size)] at h
  exact h

/-- Every natural pair has an actual clean multiplication run at its least common
width, with literal all-origin terminal heads and its exact padded product. -/
theorem natural_product (a b : ℕ) :
    ∃ t, t ≤ 280*(commonWidth a b)^2+282*(commonWidth a b)+71 ∧
      MultitapeToolkit.Absolute.Runs machine t (minimalInput a b)
        (output (commonWidth a b) (a*b)) ∧
      MultitapeToolkit.Absolute.Halts machine (output (commonWidth a b) (a*b)) ∧
      (output (commonWidth a b) (a*b)).head=(fun _ => 0) ∧
      bitsValue ((fixedBits (2*commonWidth a b) (a*b)).reverse.reverse)=a*b := by
  rcases product_correct _ a b (commonWidth_fits a b).1 (commonWidth_fits a b).2 with
    ⟨t,ht,hr,hh,hvalue⟩
  exact ⟨t,ht,hr,hh,output_heads _ _,hvalue⟩

/-- Full double-width physical output carries the ring product residue. No
physical truncation or signed parsing operation is hidden in the interpretation. -/
theorem zmod_product (n : ℕ) (x y : ZMod (2^n)) :
    ∃ t, t ≤ 280*n^2+282*n+71 ∧
      MultitapeToolkit.Absolute.Runs machine t (input n x.val y.val)
        (output n (x.val*y.val)) ∧
      MultitapeToolkit.Absolute.Halts machine (output n (x.val*y.val)) ∧
      (output n (x.val*y.val)).head=(fun _ => 0) ∧
      (bitsValue ((fixedBits (2*n) (x.val*y.val)).reverse.reverse) : ZMod (2^n))=x*y ∧
      bitsValue (fixedBits n (x.val*y.val))=(x*y).val := by
  let : NeZero (2^n) := ⟨pow_ne_zero _ (by decide)⟩
  rcases product_correct n x.val y.val x.val_lt y.val_lt with ⟨t,ht,hr,hh,hvalue⟩
  refine ⟨t,ht,hr,hh,output_heads _ _,?_,?_⟩
  · rw [hvalue,Nat.cast_mul,ZMod.natCast_zmod_val,ZMod.natCast_zmod_val]
  · rw [bitsValue_fixedBits,ZMod.val_mul]

/-- Signed labels are canonical nonnegative residue input words. The actual
terminal configuration has all six heads at origin. -/
theorem signed_residue_product (n : ℕ) (a b : ℤ) :
    ∃ t, t ≤ 280*n^2+282*n+71 ∧
      MultitapeToolkit.Absolute.Runs machine t
        (input n (a : ZMod (2^n)).val (b : ZMod (2^n)).val)
        (output n ((a : ZMod (2^n)).val*(b : ZMod (2^n)).val)) ∧
      MultitapeToolkit.Absolute.Halts machine
        (output n ((a : ZMod (2^n)).val*(b : ZMod (2^n)).val)) ∧
      (output n ((a : ZMod (2^n)).val*(b : ZMod (2^n)).val)).head=(fun _ => 0) ∧
      (bitsValue ((fixedBits (2*n)
        ((a : ZMod (2^n)).val*(b : ZMod (2^n)).val)).reverse.reverse) : ZMod (2^n))=
        ((a*b : ℤ) : ZMod (2^n)) := by
  rcases zmod_product n (a : ZMod (2^n)) (b : ZMod (2^n)) with
    ⟨t,ht,hr,hh,hhead,hvalue,_⟩
  exact ⟨t,ht,hr,hh,hhead,by simpa only [Int.cast_mul] using hvalue⟩

namespace Host
open MultitapeToolkit.Absolute
variable {J : Type*} [Fintype J]
noncomputable def machine (e : MulStack ↪ J) :=
  TapeEmbedding.liftProgram e MultitapeToolkit.IntegerMultiplicationOriginRestored.machine
noncomputable def input (e : MulStack ↪ J) (H : J → ℤ) (C : J → ℤ → Option Bool)
    (n a b : ℕ) := TapeEmbedding.liftCfg e
      (MultitapeToolkit.IntegerMultiplicationOriginRestored.input n a b) H C
noncomputable def output (e : MulStack ↪ J) (H : J → ℤ) (C : J → ℤ → Option Bool)
    (n product : ℕ) := TapeEmbedding.liftCfg e
      (MultitapeToolkit.IntegerMultiplicationOriginRestored.output n product) H C

/-- Inject this actual multiplication into any finite tape bank. The six selected
heads return to zero; every unselected tape retains its entire dirty exterior. -/
theorem embedded_product (e : MulStack ↪ J) (H : J → ℤ) (C : J → ℤ → Option Bool)
    (n a b : ℕ) (ha : a<2^n) (hb : b<2^n) :
    ∃ t, t ≤ 280*n^2+282*n+71 ∧
      MultitapeToolkit.Absolute.Runs (machine e) t
        (input e H C n a b) (output e H C n (a*b)) ∧
      MultitapeToolkit.Absolute.Halts (machine e) (output e H C n (a*b)) ∧
      (∀ i, (output e H C n (a*b)).head (e i)=0) ∧
      (output e H C n (a*b)).cell (e .sumReverse)=
        StackOriginSerializer.originWord (fixedBits (2*n) (a*b)).reverse ∧
      (∀ j, j ∉ Set.range e → (output e H C n (a*b)).head j=H j ∧
        (output e H C n (a*b)).cell j=C j) ∧
      bitsValue ((fixedBits (2*n) (a*b)).reverse.reverse)=a*b := by
  rcases product_correct n a b ha hb with ⟨t,ht,hr,hh,hvalue⟩
  refine ⟨t,ht,TapeEmbedding.lift_runs e _ hr H C,
    (TapeEmbedding.lift_halts e _ _ H C).2 hh,?_,?_,?_,hvalue⟩
  · intro i
    simp [output,MultitapeToolkit.IntegerMultiplicationOriginRestored.output_heads]
  · simp [output,MultitapeToolkit.IntegerMultiplicationOriginRestored.output_cells]
  · intro j hj
    have hd := (TapeEmbedding.decode_none e j).2 hj
    simp [output,TapeEmbedding.liftCfg,hd]

/-- Dirty spectators survive every prefix, including before multiplication halts. -/
theorem prefix_spectators (e : MulStack ↪ J) (H : J → ℤ) (C : J → ℤ → Option Bool)
    (n a b s : ℕ) (d : MultitapeToolkit.Absolute.Config J (Option Bool)
      MultitapeToolkit.IntegerMultiplicationOriginRestored.State)
    (hr : MultitapeToolkit.Absolute.Runs (machine e) s (input e H C n a b) d)
    (j : J) (hj : j ∉ Set.range e) : d.head j=H j ∧ d.cell j=C j := by
  have h := TapeEmbedding.preserves_extra e MultitapeToolkit.IntegerMultiplicationOriginRestored.machine j hj hr
  have hd := (TapeEmbedding.decode_none e j).2 hj
  constructor
  · simpa [input,TapeEmbedding.liftCfg,hd] using h.1
  · funext x
    simpa [input,TapeEmbedding.liftCfg,hd] using h.2 x
end Host
end MultitapeToolkit.IntegerMultiplicationOriginApplications
