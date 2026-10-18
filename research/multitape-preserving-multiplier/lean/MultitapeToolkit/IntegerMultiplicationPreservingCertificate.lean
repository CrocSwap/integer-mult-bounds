import MultitapeToolkit.IntegerMultiplicationPreserving
set_option autoImplicit false
namespace MultitapeToolkit.IntegerMultiplicationPreservingCertificate
open MultitapeToolkit.Absolute MultitapeToolkit.IntegerMultiplicationPreserving
open MultitapeToolkit.BinaryMultiplication Lax51Proofs.RamToTM
/-- One fixed eight-tape program preserves both supplied operand words, produces
    the exact double-width product, erases other work, and returns every head. -/
theorem exists_fixed_preserving_multiplier :
    ∃ P : Program Bank (Option Bool) State, ∀ n a b : ℕ,
      a < 2^n → b < 2^n → ∃ t d,
        t ≤ 280*n^2+284*n+74 ∧
        MultitapeToolkit.Absolute.Runs P t (input n a b) d ∧
        MultitapeToolkit.Absolute.Halts P d ∧
        d.head = (fun _ => 0) ∧
        (∀ i : Fin 2, d.cell (.inl i) = (input n a b).cell (.inl i)) ∧
        (∀ k : MulStack, d.cell (.inr k) = if k=.sumReverse then
          StackOriginSerializer.originWord (fixedBits (2*n) (a*b)).reverse
          else fun _ => none) ∧
        bitsValue ((fixedBits (2*n) (a*b)).reverse.reverse)=a*b := by
  refine ⟨machine,?_⟩
  intro n a b ha hb
  rcases product_correct n a b ha hb with ⟨t,ht,hr,hh,hv⟩
  exact ⟨t,output n a b,ht,hr,hh,output_heads n a b,preserves_inputs n a b,output_work n a b,hv⟩
end MultitapeToolkit.IntegerMultiplicationPreservingCertificate
