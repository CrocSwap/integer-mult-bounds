import OAI.Computability.NearSquareRoot.KernelPass
import OAI.Computability.IntegerMultiplication.Port.Token
import Mathlib.Data.Rat.Lemmas
import Mathlib.Data.ZMod.Basic
import Mathlib.Algebra.Order.BigOperators.Ring.Finset
import Mathlib.Data.Fintype.BigOperators

/-!
# Compact composite specialization of the short rational operation

The input register is a canonical nonnegative residue. A signed numerator is
multiplied into it to obtain a canonical residue `z`. The tape computes a
short correction `r` modulo its positive denominator `b`, then divides
`z + r*M` exactly by `b`. This file proves uniqueness of the returned
register, the rational coefficient contract on every matrix entry, and the
signed lift of an integer-valued endpoint. The inverse-word lemma accepts
any verified Euclidean inverse returned by the tape.

`SourceTicket` is the published `Port.Token` specialized to ZMod. The
standalone build typechecks its complete pinned source body with small
Mathlib imports. The row result uses the original `KernelPass.RowMatrix`.
The bit-level Euclidean machine and the construction of the
individual denominator support witnesses are separate obligations.
-/

namespace Moonshot.CompactSpecialization

/-- A common modulus for every denominator dividing a power of the support. -/
def modulus (U e : ℕ) : ℕ := 2 ^ e * U + 1

theorem support_coprime {U e b t : ℕ} (h : b ∣ U ^ t) :
    b.Coprime (modulus U e) := by
  have hu : U.Coprime (modulus U e) :=
    (Nat.coprime_mul_right_add_right U 1 (2 ^ e)).2 (by simp)
  exact (hu.pow_left t).coprime_dvd_left h

/-- The shortest canonical correction register. -/
noncomputable def correction (M b z : ℕ) : ℕ :=
  (-(z : ZMod b) * (M : ZMod b)⁻¹).val

/-- Any inverse returned by the Euclidean routine gives this correction. -/
theorem correction_from_inverse {M b : ℕ} (z v : ℕ) (h : b.Coprime M)
    (hv : (v : ZMod b) * (M : ZMod b) = 1) :
    (-(z : ZMod b) * (v : ZMod b)).val = correction M b z := by
  have hu : IsUnit (M : ZMod b) := (ZMod.isUnit_iff_coprime M b).2 h.symm
  have he : (v : ZMod b) = (M : ZMod b)⁻¹ := by
    calc
      _ = (v : ZMod b) * ((M : ZMod b) * (M : ZMod b)⁻¹) := by
        rw [ZMod.mul_inv_of_unit _ hu, mul_one]
      _ = _ := by rw [← mul_assoc, hv, one_mul]
  rw [he]
  rfl

theorem correction_exact {M b : ℕ} (hb : 0 < b) (h : b.Coprime M) (z : ℕ) :
    correction M b z < b ∧ b ∣ z + correction M b z * M := by
  let _ : NeZero b := ⟨Nat.ne_of_gt hb⟩
  have hu : IsUnit (M : ZMod b) := (ZMod.isUnit_iff_coprime M b).2 h.symm
  have hr : ((correction M b z : ℕ) : ZMod b) = -(z : ZMod b) * (M : ZMod b)⁻¹ :=
    ZMod.natCast_zmod_val _
  refine ⟨ZMod.val_lt _, (ZMod.natCast_eq_zero_iff _ _).1 ?_⟩
  rw [Nat.cast_add, Nat.cast_mul, hr, mul_assoc, ZMod.inv_mul_of_unit _ hu, mul_one,
    add_neg_cancel]

noncomputable def quotientWord (M b z : ℕ) : ℕ :=
  (z + correction M b z * M) / b

theorem quotient_spec {M b z : ℕ} (hb : 0 < b) (hz : z < M) (h : b.Coprime M) :
    quotientWord M b z < M ∧
      (b : ZMod M) * (quotientWord M b z : ZMod M) = (z : ZMod M) := by
  obtain ⟨hr, hd⟩ := correction_exact hb h z
  constructor
  · apply (Nat.div_lt_iff_lt_mul hb).2
    calc
      z + correction M b z * M < M + correction M b z * M :=
        Nat.add_lt_add_right hz _
      _ = (correction M b z + 1) * M := by
        rw [Nat.add_mul, Nat.one_mul, Nat.add_comm M]
      _ ≤ b * M := Nat.mul_le_mul_right M (Nat.succ_le_of_lt hr)
      _ = M * b := Nat.mul_comm ..
  · have he : quotientWord M b z * b = z + correction M b z * M :=
      Nat.div_mul_cancel hd
    have he' := congrArg (fun k : ℕ => (k : ZMod M)) he
    simp only [Nat.cast_mul, Nat.cast_add, ZMod.natCast_self, mul_zero, add_zero] at he'
    exact (mul_comm _ _).trans he'

/-- The signed short coefficient applied to a residue word. -/
noncomputable def scalar (M b : ℕ) (a : ℤ) (x : ℕ) : ℕ :=
  quotientWord M b (((a : ZMod M) * (x : ZMod M)).val)

/-- The published rational token, specialized to the common modulus. -/
abbrev SourceTicket (M : ℕ) (t : ℚ) (v : ZMod M) : Prop :=
  OAI.Computability.IntegerMultiplication.Port.Token t v

theorem scalar_spec {U e b t : ℕ} (hb : 0 < b) (hs : b ∣ U ^ t) (a : ℤ) (x : ℕ) :
    scalar (modulus U e) b a x < modulus U e ∧
    (b : ZMod (modulus U e)) * (scalar (modulus U e) b a x : ZMod (modulus U e)) =
      (a : ZMod (modulus U e)) * (x : ZMod (modulus U e)) ∧
    SourceTicket (modulus U e) (((a : ℚ) * x) / b)
      (scalar (modulus U e) b a x : ZMod (modulus U e)) := by
  let M := modulus U e
  have hM : 0 < M := Nat.zero_lt_succ _
  let _ : NeZero M := ⟨Nat.ne_of_gt hM⟩
  have hc : b.Coprime M := support_coprime hs
  let z := ((a : ZMod M) * (x : ZMod M)).val
  have hz : z < M := ZMod.val_lt _
  obtain ⟨hq, he⟩ := quotient_spec hb hz hc
  have he' : (b : ZMod M) * (scalar M b a x : ZMod M) =
      (a : ZMod M) * (x : ZMod M) := he.trans (ZMod.natCast_zmod_val _)
  refine ⟨hq, he', (b : ℤ), a * (x : ℤ), ?_, ?_, ?_⟩
  · simpa only [Int.cast_natCast] using (ZMod.isUnit_iff_coprime b M).2 hc
  · simpa only [Int.cast_natCast, Int.cast_mul] using he'
  · have hbq : (b : ℚ) ≠ 0 := by exact_mod_cast (Nat.ne_of_gt hb)
    simpa only [Int.cast_natCast, Int.cast_mul] using
      (mul_comm (b : ℚ) (((a : ℚ) * x) / b)).trans (div_mul_cancel₀ _ hbq)

/-- Uniqueness among all valid canonical output registers. -/
theorem canonical_scalar_unique {U e b t : ℕ} (hb : 0 < b) (hs : b ∣ U ^ t)
    (a : ℤ) (x y : ℕ) (hy : y < modulus U e)
    (he : (b : ZMod (modulus U e)) * (y : ZMod (modulus U e)) =
      (a : ZMod (modulus U e)) * (x : ZMod (modulus U e))) :
    y = scalar (modulus U e) b a x := by
  obtain ⟨hq, heq, _⟩ := scalar_spec (e := e) hb hs a x
  have hu := (ZMod.isUnit_iff_coprime b (modulus U e)).2 (support_coprime hs)
  have h := congrArg ZMod.val ((IsUnit.mul_right_inj hu).mp (he.trans heq.symm))
  simpa only [ZMod.val_natCast_of_lt hy, ZMod.val_natCast_of_lt hq] using h

/-- The concrete canonical coefficients meet the OAI MatrixToken contract,
also for rectangular or empty address ranges. -/
theorem matrix_entry_tickets {I J : Type*} {U e : ℕ}
    (a : I → J → ℤ) (b t : I → J → ℕ) (hb : ∀ i j, 0 < b i j)
    (hs : ∀ i j, b i j ∣ U ^ t i j) :
    ∀ i j, SourceTicket (modulus U e) ((a i j : ℚ) / b i j)
      ((scalar (modulus U e) (b i j) (a i j) 1 : ℕ) : ZMod (modulus U e)) := by
  intro i j
  simpa using (scalar_spec (e := e) (hb i j) (hs i j) (a i j) 1).2.2

/-- A rational ticket at an integer endpoint determines its residue exactly. -/
theorem integer_ticket_cast {M : ℕ} {z : ℤ} {v : ZMod M}
    (h : SourceTicket M (z : ℚ) v) : v = (z : ZMod M) := by
  exact OAI.Computability.IntegerMultiplication.Port.Token.unique h
    (OAI.Computability.IntegerMultiplication.Port.Token.whole z)

/-- The machine's signed boundary convention. At half the modulus the
positive representative is kept. Strict uniqueness bounds exclude ties. -/
def center (M y : ℕ) : ℤ :=
  if M < 2 * y then (y : ℤ) - (M : ℤ) else (y : ℤ)

/-- A bounded integer-valued matrix endpoint is recovered with a single
centered lift, independently of the real sizes of its intermediates. -/
theorem signed_lift_of_ticket {M y : ℕ} {z : ℤ} (hy : y < M)
    (hl : -(M : ℤ) < 2 * z) (hr : 2 * z < (M : ℤ))
    (h : SourceTicket M (z : ℚ) (y : ZMod M)) : center M y = z := by
  have hM : 0 < M := Nat.zero_lt_of_lt hy
  let _ : NeZero M := ⟨Nat.ne_of_gt hM⟩
  have hc := integer_ticket_cast h
  have hmod : z % (M : ℤ) = (y : ℤ) := by
    rw [← ZMod.val_intCast, ← hc, ZMod.val_natCast_of_lt hy]
  by_cases hnonneg : 0 ≤ z
  · have hz : z < (M : ℤ) := by omega
    rw [Int.emod_eq_of_lt hnonneg hz] at hmod
    have htest : ¬ M < 2 * y := by omega
    rw [center, ite_eq_right htest]
    omega
  · have hplus : 0 ≤ z + (M : ℤ) := by omega
    have hlt : z + (M : ℤ) < (M : ℤ) := by omega
    have hmod' := Int.emod_eq_of_lt hplus hlt
    have he : (z + (M : ℤ)) % (M : ℤ) = z % (M : ℤ) := by simp
    rw [he, hmod] at hmod'
    have htest : M < 2 * y := by omega
    rw [center, ite_eq_left htest]
    omega



open scoped BigOperators
open OAI.Computability.NearSquareRoot.KernelPass

/-- The physically computed scalar can consume a register for an arbitrary
rational intermediate. Its real numerator and denominator need no size bound. -/
theorem scalar_maps_ticket {U e b t : ℕ} (hb : 0 < b) (hs : b ∣ U ^ t)
    (a : ℤ) (x : ℕ) {v : ℚ}
    (hx : SourceTicket (modulus U e) v (x : ZMod (modulus U e))) :
    SourceTicket (modulus U e) (((a : ℚ) / b) * v)
      (scalar (modulus U e) b a x : ZMod (modulus U e)) := by
  let M := modulus U e
  obtain ⟨d, u, hd, hxmod, hxrat⟩ := hx
  have hbunit : IsUnit (b : ZMod M) :=
    (ZMod.isUnit_iff_coprime b M).2 (support_coprime hs)
  have hword := (scalar_spec (e := e) hb hs a x).2.1
  have hbq : (b : ℚ) ≠ 0 := by exact_mod_cast (Nat.ne_of_gt hb)
  refine ⟨d * (b : ℤ), a * u, ?_, ?_, ?_⟩
  · simpa only [Int.cast_mul, Int.cast_natCast] using hd.mul hbunit
  · simp only [Int.cast_mul, Int.cast_natCast]
    calc
      _ = (d : ZMod M) * ((b : ZMod M) * (scalar M b a x : ZMod M)) := mul_assoc ..
      _ = (a : ZMod M) * ((d : ZMod M) * (x : ZMod M)) := by rw [hword]; ring
      _ = _ := by rw [hxmod]
  · simp only [Int.cast_mul, Int.cast_natCast]
    calc
      _ = (((a : ℚ) / b) * b) * ((d : ℚ) * v) := by ring
      _ = _ := by rw [div_mul_cancel₀ _ hbq, hxrat]

private theorem ticket_sum {M : ℕ} {I : Type*} (s : Finset I)
    (f : I → ℚ) (g : I → ZMod M)
    (h : ∀ i ∈ s, SourceTicket M (f i) (g i)) :
    SourceTicket M (∑ i ∈ s, f i) (∑ i ∈ s, g i) := by
  classical
  induction s using Finset.induction_on with
  | empty =>
    simp only [Finset.sum_empty]
    exact ⟨1, 0, by simp⟩
  | insert i s hi ih =>
    rw [Finset.sum_insert hi, Finset.sum_insert hi]
    exact OAI.Computability.IntegerMultiplication.Port.Token.add (h i (Finset.mem_insert_self ..))
      (ih (fun j hj => h j (Finset.mem_insert_of_mem hj)))

/-- The extensional output of a row of short coefficient operations and modular
adds. Its definition imposes no dense scan on the physical implementation. -/
noncomputable def rowPass {I O : Type*} [Fintype I] (M : ℕ)
    (a : O → I → ℤ) (b : O → I → ℕ) (x : I → ℕ) (o : O) : ℕ :=
  (∑ i, (scalar M (b o i) (a o i) (x i) : ZMod M)).val

/-- Consecutive stages compose by passing the returned tickets directly. -/
theorem row_pass_tickets {I O : Type*} [Fintype I] {U e : ℕ}
    (a : O → I → ℤ) (b t : O → I → ℕ) (hb : ∀ o i, 0 < b o i)
    (hs : ∀ o i, b o i ∣ U ^ t o i) (x : I → ℕ) (q : I → ℚ)
    (hx : ∀ i, SourceTicket (modulus U e) (q i) (x i : ZMod (modulus U e))) (o : O) :
    SourceTicket (modulus U e) (∑ i, ((a o i : ℚ) / b o i) * q i)
      (rowPass (modulus U e) a b x o : ZMod (modulus U e)) := by
  let _ : NeZero (modulus U e) := ⟨Nat.ne_of_gt (Nat.zero_lt_succ _)⟩
  have hr := ticket_sum (M := modulus U e) Finset.univ _ _
    (fun i _ => scalar_maps_ticket (hb o i) (hs o i) (a o i) (x i) (hx i))
  simpa only [rowPass, ZMod.natCast_zmod_val] using hr

/-- Directly typed against the published KernelPass.RowMatrix and its standard
matrix-vector semantics. With a rational row certificate, every bounded
integer output is recovered by the modular local program's one final lift. -/
theorem source_row_pass_lift {A h I O U e : ℕ} (P : RowMatrix A h I O)
    (a : Matrix (Fin O × Addr A h) (Fin I × Addr A h) ℤ)
    (b t : Matrix (Fin O × Addr A h) (Fin I × Addr A h) ℕ)
    (hb : ∀ o i, 0 < b o i) (hs : ∀ o i, b o i ∣ U ^ t o i)
    (hentry : ∀ o i, P o i = (a o i : ℚ) / b o i)
    (x : (Fin I × Addr A h) → ℕ) (q : (Fin I × Addr A h) → ℚ)
    (hx : ∀ i, SourceTicket (modulus U e) (q i) (x i : ZMod (modulus U e)))
    (y : (Fin O × Addr A h) → ℤ) (heval : ∀ o, P.mulVec q o = (y o : ℚ))
    (hl : ∀ o, -(modulus U e : ℤ) < 2 * y o)
    (hr : ∀ o, 2 * y o < (modulus U e : ℤ)) (o : Fin O × Addr A h) :
    center (modulus U e) (rowPass (modulus U e) a b x o) = y o := by
  let _ : NeZero (modulus U e) := ⟨Nat.ne_of_gt (Nat.zero_lt_succ _)⟩
  have hrow := row_pass_tickets (e := e) a b t hb hs x q hx o
  have hy : (∑ i, ((a o i : ℚ) / b o i) * q i) = (y o : ℚ) := by
    simpa only [Matrix.mulVec_apply_eq_sum, hentry] using heval o
  rw [hy] at hrow
  exact signed_lift_of_ticket (ZMod.val_lt _) (hl o) (hr o) hrow


/-- The signed integer Walsh letter underlying the source's two-bit factor. -/
def walshPairSign (x y : Fin 2 → ZMod 2) : ℤ :=
  if x 0 * y 0 + x 1 * y 1 = 0 then 1 else -1

private theorem walsh_pair_factor (x y : Fin 2 → ZMod 2) :
    pairEntry x y = (walshPairSign x y : ℚ) / 2 := by
  unfold pairEntry walshPairSign
  split <;> norm_num

private theorem walsh_pair_abs (x y : Fin 2 → ZMod 2) : |walshPairSign x y| = 1 := by
  unfold walshPairSign
  split <;> norm_num

/-- The sign of one unnormalized transform matrix entry within a bank. -/
def walshSign {A h : ℕ} (y x : Addr A h) : ℤ :=
  ∏ c, ∏ j, walshPairSign (y c j) (x c j)

private theorem walsh_sign_abs {A h : ℕ} (y x : Addr A h) : |walshSign y x| = 1 := by
  simp [walshSign, Finset.abs_prod, walsh_pair_abs]

/-- Integer numerator on the source's complete row-address space. -/
def walshCoefficient {A h W : ℕ} (r s : Fin W × Addr A h) : ℤ :=
  if s.1 = r.1 then walshSign r.2 s.2 else 0

/-- Each letter contains two address bits on each axis. -/
def walshDenominator (A h : ℕ) : ℕ := 2 ^ (A * h)

theorem target_entry_integer {A h W : ℕ} (r s : Fin W × Addr A h) :
    target A W h r s = (walshCoefficient r s : ℚ) / walshDenominator A h := by
  rcases r with ⟨o, y⟩
  rcases s with ⟨i, x⟩
  by_cases he : i = o
  · simp [target, walshCoefficient, walshSign, walshDenominator, he, walsh_pair_factor,
      Finset.prod_div_distrib, pow_mul]
  · simp [target, walshCoefficient, he]

/-- Exact unnormalized Walsh sum on the one bank selected by the output row. -/
noncomputable def walshSum {A h W : ℕ} (x : (Fin W × Addr A h) → ℤ) (r : Fin W × Addr A h) : ℤ :=
  ∑ u : Addr A h, walshSign r.2 u * x (r.1, u)

theorem target_scaled_input {A h W : ℕ} (x : (Fin W × Addr A h) → ℤ)
    (r : Fin W × Addr A h) :
    (target A W h).mulVec (fun i => (walshDenominator A h : ℚ) * x i) r =
      (walshSum x r : ℚ) := by
  have hd : (walshDenominator A h : ℚ) ≠ 0 := by
    simp [walshDenominator]
  have he : (target A W h).mulVec (fun i => (walshDenominator A h : ℚ) * x i) r =
      ((∑ i, walshCoefficient r i * x i : ℤ) : ℚ) := by
    rw [Matrix.mulVec_apply_eq_sum, Int.cast_sum]
    apply Finset.sum_congr rfl
    intro i _
    rw [target_entry_integer, Int.cast_mul, ← mul_assoc, div_mul_cancel₀ _ hd]
  rw [he]
  apply congrArg (fun z : ℤ => (z : ℚ))
  rw [Fintype.sum_prod_type]
  simp [walshCoefficient, walshSum, ite_mul, Finset.sum_ite_irrel]

/-- The sharp rowwise l1 bound does not involve independent neighbouring banks. -/
theorem walsh_sum_bound {A h W : ℕ} (x : (Fin W × Addr A h) → ℤ)
    (r : Fin W × Addr A h) :
    |walshSum x r| ≤ ∑ u : Addr A h, |x (r.1, u)| := by
  unfold walshSum
  calc
    _ ≤ ∑ u : Addr A h, |walshSign r.2 u * x (r.1, u)| :=
      Finset.abs_sum_le_sum_abs _ _
    _ = _ := by simp [abs_mul, walsh_sign_abs]

/-- For every source-correct plan and every bank size or address width,
pre-scaling by the exact binary denominator and one signed lift recover all
Walsh signed sums. The sole magnitude hypothesis is a rowwise input bound.
The output certificate is the same compositional ticket strengthened by
`row_pass_tickets`; it makes no assertion about the size of intermediate
rational values or the cost of any particular physical factorization. -/
theorem correct_plan_exact_walsh {A h W M : ℕ} (p : Plan A W W) (hp : Correct p)
    (x : (Fin W × Addr A h) → ℤ) (out : (Fin W × Addr A h) → ℕ)
    (hword : ∀ r, out r < M)
    (hticket : ∀ r, SourceTicket M
      ((p.eval h).mulVec (fun i => (walshDenominator A h : ℚ) * x i) r) (out r : ZMod M))
    (hmass : ∀ bank : Fin W, 2 * (∑ u : Addr A h, |x (bank, u)|) < (M : ℤ))
    (r : Fin W × Addr A h) : center M (out r) = walshSum x r := by
  have ht := hticket r
  rw [hp h, target_scaled_input] at ht
  have hrow := walsh_sum_bound x r
  have hi := le_abs_self (walshSum x r)
  have lo := neg_le_abs (walshSum x r)
  have hM := hmass r.1
  exact signed_lift_of_ticket (hword r) (by omega) (by omega) ht



/-- Canonical input register after the even-width scaling. -/
noncomputable def scaledWord (A h M : ℕ) (x : ℤ) : ℕ :=
  ((walshDenominator A h : ZMod M) * (x : ZMod M)).val

private theorem scaled_word_ticket (A h M : ℕ) [NeZero M] (x : ℤ) :
    SourceTicket M ((walshDenominator A h : ℚ) * x) (scaledWord A h M x : ZMod M) := by
  refine ⟨1, (walshDenominator A h : ℤ) * x, by simp, ?_, ?_⟩
  · simp [scaledWord]
  · simp

/-- The actual normalized binary target admits an unconditional composite
coefficient specialization at all widths. Its unfolded matrix evaluation is
a semantic baseline; the fast factorization is a distinct complexity claim.
Only the input mass of each individual bank bounds the final unique lift. -/
theorem compact_target_exact_walsh {A h W V e : ℕ} (x : (Fin W × Addr A h) → ℤ)
    (hmass : ∀ bank : Fin W, 2 * (∑ u : Addr A h, |x (bank, u)|) <
      (modulus (2 * V) e : ℤ)) (r : Fin W × Addr A h) :
    center (modulus (2 * V) e)
      (rowPass (modulus (2 * V) e) walshCoefficient (fun _ _ => walshDenominator A h)
        (fun i => scaledWord A h (modulus (2 * V) e) (x i)) r) = walshSum x r := by
  let M := modulus (2 * V) e
  let _ : NeZero M := ⟨Nat.ne_of_gt (Nat.zero_lt_succ _)⟩
  have hdiv : walshDenominator A h ∣ (2 * V) ^ (A * h) :=
    ⟨V ^ (A * h), by simp [walshDenominator, mul_pow]⟩
  have hrange (q : Fin W × Addr A h) :
      -(M : ℤ) < 2 * walshSum x q ∧ 2 * walshSum x q < (M : ℤ) := by
    have habs := walsh_sum_bound x q
    have hi := le_abs_self (walshSum x q)
    have lo := neg_le_abs (walshSum x q)
    have hm := hmass q.1
    change 2 * (∑ u : Addr A h, |x (q.1, u)|) < (M : ℤ) at hm
    omega
  exact source_row_pass_lift (U := 2 * V) (e := e) (target A W h) walshCoefficient
    (fun _ _ => walshDenominator A h) (fun _ _ => A * h)
    (fun _ _ => by simp [walshDenominator]) (fun _ _ => hdiv) target_entry_integer
    (fun i => scaledWord A h M (x i)) (fun i => (walshDenominator A h : ℚ) * x i)
    (fun i => scaled_word_ticket A h M (x i)) (walshSum x) (target_scaled_input x)
    (fun q => (hrange q).1) (fun q => (hrange q).2) r


end Moonshot.CompactSpecialization
