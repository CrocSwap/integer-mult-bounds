import PairedBitXorScan
import Init.Data.List.Zip

/-!
Injectivity of the accepted little-endian Boolean decoder at fixed length.
Leading false bits make the unrestricted decoder noninjective, so equal length
is an explicit premise. The paired consequence uses both decoded tracks and
recovers actual ordered symbols. There is no runtime or physical encoding claim.
James Chang with OpenAI assistance; Apache-2.0. Reuses Lean core and the
accepted PairedBitXorScan value definition unchanged. Author-checked context:
kappa=836330098538459/500000000000000000.
-/
set_option Elab.async false
set_option autoImplicit false
namespace CurrentMain.FixedWidthBitValue
open PairedBitXorScan (Pair value)

theorem value_injective_of_length (xs ys : List Bool)
    (hl : xs.length = ys.length) (hv : value xs = value ys) : xs = ys := by
  induction xs generalizing ys with
  | nil =>
      cases ys with
      | nil => rfl
      | cons b ys => simp only [List.length_nil, List.length_cons] at hl; omega
  | cons a xs ih =>
      cases ys with
      | nil => simp only [List.length_nil, List.length_cons] at hl; omega
      | cons b ys =>
          have htail : xs.length = ys.length := Nat.succ.inj hl
          cases a <;> cases b
            <;> simp only [value, Bool.toNat_false, Bool.toNat_true, Nat.add_zero] at hv
          · exact congrArg (false :: ·) (ih ys htail (by omega))
          · omega
          · omega
          · exact congrArg (true :: ·) (ih ys htail (by omega))

theorem paired_injective_of_length (xs ys : List Pair)
    (hl : xs.length = ys.length)
    (ha : value (xs.map Prod.fst) = value (ys.map Prod.fst))
    (hb : value (xs.map Prod.snd) = value (ys.map Prod.snd)) : xs = ys := by
  have hf := value_injective_of_length (xs.map Prod.fst) (ys.map Prod.fst)
    (by simpa only [List.length_map] using hl) ha
  have hs := value_injective_of_length (xs.map Prod.snd) (ys.map Prod.snd)
    (by simpa only [List.length_map] using hl) hb
  calc
    xs = (ys.map Prod.fst).zip (ys.map Prod.snd) := List.zip_of_prod hf hs
    _ = ys := by simpa only [List.unzip_fst, List.unzip_snd] using List.zip_unzip ys

end CurrentMain.FixedWidthBitValue
#print axioms CurrentMain.FixedWidthBitValue.value_injective_of_length
#print axioms CurrentMain.FixedWidthBitValue.paired_injective_of_length
#check @CurrentMain.FixedWidthBitValue.paired_injective_of_length
