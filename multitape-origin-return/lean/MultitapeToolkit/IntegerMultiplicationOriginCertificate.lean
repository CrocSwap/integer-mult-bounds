import MultitapeToolkit.IntegerMultiplicationOriginRestored
set_option autoImplicit false
namespace MultitapeToolkit.IntegerMultiplicationOriginCertificate
open MultitapeToolkit.Absolute MultitapeToolkit.IntegerMultiplicationOriginRestored
open MultitapeToolkit.BinaryMultiplication Lax51Proofs.RamToTM
/-- One fixed finite table, quantified before every operand and width, performs
    actual multiplication, cleans every work tape, and physically returns all
    six heads to zero within the displayed transition bound. -/
theorem exists_fixed_origin_multiplier :
    ∃ P : Program MulStack (Option Bool) State, ∀ n a b : ℕ,
      a < 2^n → b < 2^n → ∃ t d,
        t ≤ 280*n^2+282*n+71 ∧
        MultitapeToolkit.Absolute.Runs P t (input n a b) d ∧
        MultitapeToolkit.Absolute.Halts P d ∧
        d.head = (fun _ => 0) ∧
        (∀ k, d.cell k = if k=.sumReverse then
          StackOriginSerializer.originWord (fixedBits (2*n) (a*b)).reverse
          else fun _ => none) ∧
        bitsValue ((fixedBits (2*n) (a*b)).reverse.reverse)=a*b := by
  refine ⟨machine,?_⟩
  intro n a b ha hb
  rcases product_correct n a b ha hb with ⟨t,ht,hr,hh,hv⟩
  exact ⟨t,output n (a*b),ht,hr,hh,output_heads n (a*b),output_cells n (a*b),hv⟩
end MultitapeToolkit.IntegerMultiplicationOriginCertificate
