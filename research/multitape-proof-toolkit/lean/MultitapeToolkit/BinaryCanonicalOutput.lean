import Mathlib.Data.Nat.Bits
import Mathlib.Data.Nat.Basic
import Mathlib.Algebra.Group.Nat.Defs
import Mathlib.Data.List.TakeDrop
import Lean.Elab.Tactic.Omega

/-!
# Canonical binary output from fixed-width words

Narrow reuse of the project Problem1.8 output adapter, source SHA256
F7DC666A9FDC13A28324A56106D6C626C13A7B7754515765C6530253BD5F7456,
lemmas `fixedBits_eq_bits_append_replicate`, `dropWhile_false_reverse_bits`,
and `trimHighZeros_fixedBits_reverse`. No unbounded machine register is used here:
these are mathematical specifications for the finite converter in the next module.
-/

set_option autoImplicit false
namespace MultitapeToolkit.OutputNormalization

def fixedBits : Nat → Nat → List Bool
  | 0, _ => []
  | w + 1, n => n.bodd :: fixedBits w n.div2

@[simp] theorem fixedBits_length (w n : Nat) : (fixedBits w n).length = w := by
  induction w generalizing n <;> simp [fixedBits, *]

@[simp] theorem fixedBits_zero (w : Nat) : fixedBits w 0 = List.replicate w false := by
  induction w <;> simp [fixedBits, List.replicate_succ, *]

theorem fixedBits_eq_bits_append_replicate {w n : Nat} (h : n < 2 ^ w) :
    fixedBits w n = n.bits ++ List.replicate (w - n.bits.length) false := by
  induction w generalizing n with
  | zero =>
      have hn : n = 0 := by simpa using h
      subst n
      rfl
  | succ w ih =>
      by_cases hn : n = 0
      · subst n
        simp [fixedBits, List.replicate_succ]
      · have hd : n.div2 < 2 ^ w := by
          rw [← Nat.bit_bodd_div2 n] at h
          simp only [pow_succ] at h
          cases n.bodd <;> simp [Nat.bit_val] at h ⊢ <;> omega
        have htail := ih hd
        have hbits : n.bits = n.bodd :: n.div2.bits := by
          rw [← Nat.bit_bodd_div2 n]
          simpa [Nat.bodd_bit, Nat.div2_bit] using
            (Nat.bits_append_bit n.div2 n.bodd (by
          intro hz
          have : n.bodd = true := by
            have hbit : Nat.bit n.bodd 0 = n := by
              simpa [hz] using Nat.bit_bodd_div2 n
            cases hb : n.bodd
            · simp [Nat.bit, hb] at hbit
              exact False.elim (hn hbit.symm)
            · rfl
          exact this))
        have hlen : n.div2.bits.length <= w := by
          have := congrArg List.length htail
          simp only [fixedBits_length, List.length_append,
            List.length_replicate] at this
          omega
        rw [fixedBits, htail, hbits]
        simp only [List.cons_append, List.length_cons]
        congr 2
        simpa [Nat.add_comm] using congrArg
          (fun k => List.replicate k false)
          (Nat.succ_sub_succ_eq_sub w n.div2.bits.length).symm

def trimHighZeros (bitsMSB : List Bool) : List Bool :=
  (bitsMSB.dropWhile (· = false)).reverse

theorem dropWhile_false_reverse_bits (n : Nat) :
    (n.bits.reverse.dropWhile (· = false)).reverse = n.bits := by
  induction n using Nat.strong_induction_on with
  | h n ih =>
      by_cases hn : n = 0
      · subst n
        simp
      · have hdiv : n.div2 < n := by
          rw [Nat.div2_val]
          exact Nat.div_lt_self (Nat.zero_lt_of_ne_zero hn) (by omega)
        have htail := ih n.div2 hdiv
        have hbit : n.bits = n.bodd :: n.div2.bits := by
          calc
            n.bits = (Nat.bit n.bodd n.div2).bits :=
              congrArg Nat.bits (Nat.bit_bodd_div2 n).symm
            _ = n.bodd :: n.div2.bits := Nat.bits_append_bit _ _ (by
              intro hz
              have heq : Nat.bit n.bodd 0 = n := by
                simpa [hz] using Nat.bit_bodd_div2 n
              cases hb : n.bodd
              · simp [Nat.bit, hb] at heq
                exact False.elim (hn heq.symm)
              · rfl)
        by_cases hz : n.div2 = 0
        · have hb : n.bodd = true := by
            have heq : Nat.bit n.bodd 0 = n := by
              simpa [hz] using Nat.bit_bodd_div2 n
            cases hb : n.bodd
            · simp [Nat.bit, hb] at heq
              exact False.elim (hn heq.symm)
            · rfl
          simp [hbit, hz, hb]
        · rw [hbit, List.reverse_cons, List.dropWhile_append]
          have hnonempty : n.div2.bits.reverse.isEmpty = false := by
            have hne : n.div2.bits ≠ [] := by
              have hmBits : n.div2.bits =
                  n.div2.bodd :: n.div2.div2.bits := by
                calc
                  n.div2.bits = (Nat.bit n.div2.bodd n.div2.div2).bits :=
                    congrArg Nat.bits (Nat.bit_bodd_div2 n.div2).symm
                  _ = _ := Nat.bits_append_bit _ _ (by
                    intro hzero
                    have heq : Nat.bit n.div2.bodd 0 = n.div2 := by
                      simpa [hzero] using Nat.bit_bodd_div2 n.div2
                    cases hb : n.div2.bodd
                    · simp [Nat.bit, hb] at heq
                      exact False.elim (hz heq.symm)
                    · rfl)
              rw [hmBits]
              simp
            simp [hne]
          rw [show n.div2.bits.reverse.dropWhile (· = false) =
              n.div2.bits.reverse by
            have := congrArg List.reverse htail
            simpa using this]
          simp [hnonempty]

theorem trimHighZeros_fixedBits_reverse {w n : Nat} (h : n < 2 ^ w) :
    trimHighZeros (fixedBits w n).reverse = n.bits := by
  rw [fixedBits_eq_bits_append_replicate h]
  unfold trimHighZeros
  rw [List.reverse_append, List.reverse_replicate]
  rw [List.dropWhile_append_of_pos (by intro a ha; simp at ha ⊢; exact ha.2)]
  exact dropWhile_false_reverse_bits n


end MultitapeToolkit.OutputNormalization



