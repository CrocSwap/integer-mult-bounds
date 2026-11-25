import Init

/-!
Total list-level valuation of the exact character sequence produced by the
installed logical Nat.repr. The induction follows Nat.toDigitsCore with its
actual base-10 quotient/remainder recurrence and sufficient original fuel.
A left inverse then proves injectivity of that decimal representation.

The valuation is an arithmetic fold, not a rejecting lexical parser. Its
correctness theorem is for canonical Nat.repr characters. No equation for the
opaque partial Json.Parser.natCore/anyCore, JSON parse success, general grammar,
runtime extern refinement, artifact authentication or physical cost follows.
No selected numeral list is introduced. Author-checked context
kappa=836330098538459/500000000000000000=0.001672660197076918;
the generic statements do not use or change kappa.
Credits: Lean core Nat.repr/toDigitsCore and arithmetic authors; bank/frame
canonical compact-column work; Rohan Arun PR1094; Jeremy Kothe T16/PR514.
James Chang with OpenAI assistance. Apache-2.0. Native acceptance is separate.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.DecimalReprValuation

/-- The same base-10 accumulator arithmetic, evaluated structurally on characters. -/
def decimalValue (digits : List Char) (acc : Nat) : Nat :=
  digits.foldl (fun n c => 10 * n + (c.toNat - 48)) acc

private theorem digit_value : ∀ d : Fin 10,
    (Nat.digitChar d.val).toNat - 48 = d.val := by
  decide

private theorem core_value (fuel n : Nat) (tail : List Char) (h : n < fuel) :
    decimalValue (Nat.toDigitsCore 10 fuel n tail) 0 = decimalValue tail n := by
  induction fuel generalizing n tail with
  | zero => exact False.elim (Nat.not_lt_zero n h)
  | succ fuel ih =>
      have hd : (Nat.digitChar (n % 10)).toNat - 48 = n % 10 :=
        digit_value ⟨n % 10, Nat.mod_lt n (by decide)⟩
      by_cases hz : n / 10 = 0
      · have hn : n % 10 = n := by
          simpa only [hz, Nat.mul_zero, Nat.zero_add] using Nat.div_add_mod n 10
        simp only [Nat.toDigitsCore, if_pos hz, decimalValue, List.foldl_cons,
          Nat.mul_zero, Nat.zero_add, hd]
        rw [hn]
      · have hn : 0 < n := by
          cases n with
          | zero => simp only [Nat.zero_div] at hz; contradiction
          | succ n => exact Nat.zero_lt_succ n
        have hq : n / 10 < fuel :=
          Nat.lt_of_lt_of_le (Nat.div_lt_self hn (by decide)) (Nat.le_of_lt_succ h)
        rw [Nat.toDigitsCore, if_neg hz, ih (n / 10) _ hq]
        change decimalValue tail (10 * (n / 10) + ((Nat.digitChar (n % 10)).toNat - 48)) =
          decimalValue tail n
        rw [hd, Nat.div_add_mod]

/-- All magnitudes, including zero, have their original numeric value. -/
theorem decimalValue_repr (n : Nat) : decimalValue (Nat.repr n).data 0 = n := by
  change decimalValue (Nat.toDigitsCore 10 (n + 1) n []) 0 = n
  exact core_value (n + 1) n [] (Nat.lt_succ_self n)

/-- Equal canonical decimal representations determine equal natural numbers. -/
theorem repr_injective {m n : Nat} (h : Nat.repr m = Nat.repr n) : m = n := by
  have he := congrArg (fun s : String => decimalValue s.data 0) h
  simpa only [decimalValue_repr] using he

end CurrentMain.DecimalReprValuation
#print axioms CurrentMain.DecimalReprValuation.decimalValue_repr
#print axioms CurrentMain.DecimalReprValuation.repr_injective
#check CurrentMain.DecimalReprValuation.decimalValue_repr
#check @CurrentMain.DecimalReprValuation.repr_injective
