import MultitapeToolkit.IntegerMultiplicationPreserving
import Mathlib.Data.Nat.Size
set_option autoImplicit false
/-! Reusable actual multiplication calls retaining their two protected operand
words. Protected source heads move in the copier; the core-stage prefix theorem
starts only after the copied inputs and protected heads have reached their ABI. -/
namespace MultitapeToolkit.IntegerMultiplicationPreservingApplications
open MultitapeToolkit.BinaryMultiplication Lax51Proofs.RamToTM
open MultitapeToolkit.Absolute
open MultitapeToolkit.IntegerMultiplicationPreserving

/-- Least common operand width, including zero-width zero operands. -/
def commonWidth (a b : ℕ) : ℕ := max a.size b.size

theorem commonWidth_spec (a b n : ℕ) :
    commonWidth a b ≤ n ↔ a < 2^n ∧ b < 2^n := by
  simp [commonWidth,Nat.size_le]
theorem commonWidth_fits (a b : ℕ) :
    a < 2^(commonWidth a b) ∧ b < 2^(commonWidth a b) :=
  (commonWidth_spec a b _).mp le_rfl

theorem bitsValue_nat_bits (a : ℕ) : bitsValue a.bits = a := by
  induction a using Nat.binaryRec' with
  | zero => rfl
  | bit b a h ih =>
    rw [Nat.bits_append_bit a b h]
    simp only [bitsValue,ih]
/-- Literal zero padding, rather than only equality of decoded values. -/
theorem fixedBits_eq_bits_padding (a n : ℕ) (h : a.size ≤ n) :
    fixedBits n a = a.bits ++ List.replicate (n-a.size) false := by
  apply bitsValue_injective_of_length
  · simp [Nat.size_eq_bits_len,Nat.add_sub_of_le h]
  · rw [bitsValue_append_zeros,bitsValue_nat_bits,
      bitsValue_fixedBits_of_lt (Nat.size_le.mp h)]

/-- Arbitrary natural operands use their least common admissible padded width. -/
theorem natural_product (a b : ℕ) :
    ∃ t, t ≤ 280*(commonWidth a b)^2+284*(commonWidth a b)+74 ∧
      MultitapeToolkit.Absolute.Runs machine t
        (input (commonWidth a b) a b) (output (commonWidth a b) a b) ∧
      MultitapeToolkit.Absolute.Halts machine (output (commonWidth a b) a b) ∧
      (output (commonWidth a b) a b).head=(fun _ => 0) ∧
      (∀ i, (output (commonWidth a b) a b).cell (.inl i)=
        if i=0 then StackOriginSerializer.sourceStack 0
          (a.bits ++ List.replicate (commonWidth a b-a.size) false)
        else StackOriginSerializer.sourceStack 0
          (b.bits ++ List.replicate (commonWidth a b-b.size) false)) ∧
      bitsValue ((fixedBits (2*commonWidth a b) (a*b)).reverse.reverse)=a*b := by
  rcases product_correct _ a b (commonWidth_fits a b).1 (commonWidth_fits a b).2 with
    ⟨t,ht,hr,hh,hvalue⟩
  refine ⟨t,ht,hr,hh,output_heads _ _ _,?_,hvalue⟩
  intro i
  rw [output_protected,
    fixedBits_eq_bits_padding a (commonWidth a b) (le_max_left a.size b.size),
    fixedBits_eq_bits_padding b (commonWidth a b) (le_max_right a.size b.size)]

/-- During the actual multiplication core, both protected operands remain
stationary and unchanged at every prefix. This is not a copier-prefix claim. -/
theorem core_prefix_protected {s : ℕ}
    {c d : MultitapeToolkit.Absolute.Config Bank (Option Bool)
      MultitapeToolkit.IntegerMultiplicationOriginRestored.State}
    (hr : MultitapeToolkit.Absolute.Runs core s c d) (i : Fin 2) :
    d.head (.inl i)=c.head (.inl i) ∧ d.cell (.inl i)=c.cell (.inl i) := by
  have hi : (Sum.inl i : Bank) ∉ Set.range coreEmbedding := by
    rintro ⟨k,hk⟩
    cases hk
  have h := TapeEmbedding.preserves_extra coreEmbedding
    MultitapeToolkit.IntegerMultiplicationOriginRestored.machine (.inl i) hi hr
  exact ⟨h.1,funext h.2⟩

/-- Literal protected words and zero source heads during the actual core stage. -/
theorem core_input_prefix (n a b s : ℕ)
    (d : MultitapeToolkit.Absolute.Config Bank (Option Bool)
      MultitapeToolkit.IntegerMultiplicationOriginRestored.State)
    (hr : MultitapeToolkit.Absolute.Runs core s (coreInput n a b) d) (i : Fin 2) :
    d.head (.inl i)=0 ∧ d.cell (.inl i)=
      if i=0 then StackOriginSerializer.sourceStack 0 (fixedBits n a)
      else StackOriginSerializer.sourceStack 0 (fixedBits n b) := by
  simpa [coreInput,TapeEmbedding.liftCfg,protectedCells] using core_prefix_protected hr i

namespace Host
variable {J : Type*} [Fintype J]
noncomputable def machine (e : Bank ↪ J) :=
  TapeEmbedding.liftProgram e MultitapeToolkit.IntegerMultiplicationPreserving.machine
noncomputable def input (e : Bank ↪ J) (H : J → ℤ) (C : J → ℤ → Option Bool)
    (n a b : ℕ) := TapeEmbedding.liftCfg e
      (MultitapeToolkit.IntegerMultiplicationPreserving.input n a b) H C
noncomputable def output (e : Bank ↪ J) (H : J → ℤ) (C : J → ℤ → Option Bool)
    (n a b : ℕ) := TapeEmbedding.liftCfg e
      (MultitapeToolkit.IntegerMultiplicationPreserving.output n a b) H C

/-- A complete reusable multiplication call in any fixed finite tape bank:
protected operands, output word, all active zero heads and dirty spectators. -/
theorem embedded_product (e : Bank ↪ J) (H : J → ℤ) (C : J → ℤ → Option Bool)
    (n a b : ℕ) (ha : a<2^n) (hb : b<2^n) :
    ∃ t, t ≤ 280*n^2+284*n+74 ∧
      MultitapeToolkit.Absolute.Runs (machine e) t
        (input e H C n a b) (output e H C n a b) ∧
      MultitapeToolkit.Absolute.Halts (machine e) (output e H C n a b) ∧
      (∀ i, (output e H C n a b).head (e i)=0) ∧
      (∀ i, (output e H C n a b).cell (e (.inl i))=
        if i=0 then StackOriginSerializer.sourceStack 0 (fixedBits n a)
        else StackOriginSerializer.sourceStack 0 (fixedBits n b)) ∧
      (output e H C n a b).cell (e (.inr .sumReverse))=
        StackOriginSerializer.originWord (fixedBits (2*n) (a*b)).reverse ∧
      (∀ k, k≠MulStack.sumReverse →
        (output e H C n a b).cell (e (.inr k))=(fun _ => none)) ∧
      (∀ j, j ∉ Set.range e → (output e H C n a b).head j=H j ∧
        (output e H C n a b).cell j=C j) ∧
      bitsValue ((fixedBits (2*n) (a*b)).reverse.reverse)=a*b := by
  rcases product_correct n a b ha hb with ⟨t,ht,hr,hh,hvalue⟩
  refine ⟨t,ht,TapeEmbedding.lift_runs e _ hr H C,
    (TapeEmbedding.lift_halts e _ _ H C).2 hh,?_,?_,?_,?_,?_,hvalue⟩
  · intro i
    simp [output,MultitapeToolkit.IntegerMultiplicationPreserving.output_heads]
  · intro i
    simp [output,MultitapeToolkit.IntegerMultiplicationPreserving.output_protected]
  · simp [output,MultitapeToolkit.IntegerMultiplicationPreserving.output_work]
  · intro k hk
    simp [output,MultitapeToolkit.IntegerMultiplicationPreserving.output_work,hk]
  · intro j hj
    have hd := (TapeEmbedding.decode_none e j).2 hj
    simp [output,TapeEmbedding.liftCfg,hd]

/-- Every core prefix lifts to a genuine host run while retaining both original
words and stationary protected source heads. The copier is outside this claim. -/
theorem embedded_core_prefix (e : Bank ↪ J) (H : J → ℤ) (C : J → ℤ → Option Bool)
    (n a b s : ℕ)
    (d : MultitapeToolkit.Absolute.Config Bank (Option Bool)
      MultitapeToolkit.IntegerMultiplicationOriginRestored.State)
    (hr : MultitapeToolkit.Absolute.Runs core s (coreInput n a b) d) :
    MultitapeToolkit.Absolute.Runs (TapeEmbedding.liftProgram e core) s
      (TapeEmbedding.liftCfg e (coreInput n a b) H C) (TapeEmbedding.liftCfg e d H C) ∧
      ∀ i : Fin 2, (TapeEmbedding.liftCfg e d H C).head (e (.inl i))=0 ∧
        (TapeEmbedding.liftCfg e d H C).cell (e (.inl i))=
          if i=0 then StackOriginSerializer.sourceStack 0 (fixedBits n a)
          else StackOriginSerializer.sourceStack 0 (fixedBits n b) := by
  refine ⟨TapeEmbedding.lift_runs e core hr H C,?_⟩
  intro i
  simpa using core_input_prefix n a b s d hr i

/-- Truly extra host tapes survive every prefix of the entire preserving machine,
including its copying stage; their initial heads and cells are unrestricted. -/
theorem prefix_spectators (e : Bank ↪ J) (H : J → ℤ) (C : J → ℤ → Option Bool)
    (n a b s : ℕ) (d : MultitapeToolkit.Absolute.Config J (Option Bool) State)
    (hr : MultitapeToolkit.Absolute.Runs (machine e) s (input e H C n a b) d)
    (j : J) (hj : j ∉ Set.range e) : d.head j=H j ∧ d.cell j=C j := by
  have h := TapeEmbedding.preserves_extra e MultitapeToolkit.IntegerMultiplicationPreserving.machine j hj hr
  have hd := (TapeEmbedding.decode_none e j).2 hj
  constructor
  · simpa [input,TapeEmbedding.liftCfg,hd] using h.1
  · funext x
    simpa [input,TapeEmbedding.liftCfg,hd] using h.2 x
end Host
end MultitapeToolkit.IntegerMultiplicationPreservingApplications
