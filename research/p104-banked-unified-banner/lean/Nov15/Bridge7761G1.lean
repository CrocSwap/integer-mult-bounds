/-
Bridge7761G1 .  O-matrix of #7761's final graph as a Lean `Matrix (Fin 1262) (Fin 1262) ℚ` from PACKED data
(Bridge7761G1D: pi / chart ids base 2^11, O diag and partner entries base 2^32), O(1) lookups `sl`, and its PRINCIPAL MINORS:
  pack_pi / pack_fA / pack_fB : the packed numerals ARE the lists piL / fA / fB of Bridge7761D2 (one Nat equality each);
  pack_od / pack_op          : likewise for the rational lists odL / opL, with `qdec_encQ`;
  minors7761                 : every principal minor of O7761 is nonzero (BankNC0d.minors_ne_zero from two decide-checked data conditions).
Kernel only (decide +kernel on data; no sorry / native_decide / new axioms).
-/
import Nov15.Bridge7761G1D
import Nov15.Bridge7761F2
import Nov15.BankNC0d

namespace Bridge7761
open Finset Matrix BankNC0

def pkw (w : ℕ) : List ℕ → ℕ
  | [] => 0
  | x :: l => x + 2 ^ w * pkw w l

def sl (P w i : ℕ) : ℕ := (P / 2 ^ (w * i)) % 2 ^ w

theorem pkw_get (w : ℕ) (l : List ℕ) (hl : ∀ x ∈ l, x < 2 ^ w) (i : ℕ) : sl (pkw w l) w i = l.getD i 0 := by
  induction l generalizing i with
  | nil => simp [pkw, sl]
  | cons x l ih =>
    have hx := hl x List.mem_cons_self
    have ih' := fun i => ih (fun y hy => hl y (List.mem_cons_of_mem _ hy)) i
    have hw : 0 < 2 ^ w := by positivity
    cases i with
    | zero =>
      simp only [sl, pkw, Nat.mul_zero, pow_zero, Nat.div_one, List.getD_cons_zero]
      rw [Nat.add_mul_mod_self_left]; exact Nat.mod_eq_of_lt hx
    | succ i =>
      have e : 2 ^ (w * (i + 1)) = 2 ^ w * 2 ^ (w * i) := by rw [mul_add, mul_one, pow_add, mul_comm]
      have e2 : (x + 2 ^ w * pkw w l) / 2 ^ w = pkw w l := by
        rw [Nat.add_mul_div_left _ _ hw, Nat.div_eq_of_lt hx, zero_add]
      have := ih' i
      simp only [sl] at this ⊢
      rw [e, ← Nat.div_div_eq_div_mul]; simp only [pkw]; rw [e2, this, List.getD_cons_succ]

/-- rational entries: (num + 2^15) | (den << 16) -/
def encQ (c : ℚ) : ℕ := (c.num + 32768).toNat + 65536 * c.den
def qdec (s : ℕ) : ℚ := ((((s % 65536 : ℕ) : ℤ) - 32768 : ℤ) : ℚ) / ((s / 65536 : ℕ) : ℚ)

theorem qdec_encQ (c : ℚ) (h1 : -32768 < c.num) (h2 : c.num < 32768) : qdec (encQ c) = c := by
  have hn : (((c.num + 32768).toNat : ℕ) : ℤ) = c.num + 32768 := Int.toNat_of_nonneg (by omega)
  have hlt : (c.num + 32768).toNat < 65536 := by omega
  have e1 : encQ c % 65536 = (c.num + 32768).toNat := by
    unfold encQ; rw [Nat.add_mul_mod_self_left]; exact Nat.mod_eq_of_lt hlt
  have e2 : encQ c / 65536 = c.den := by
    unfold encQ; rw [Nat.add_mul_div_left _ _ (by norm_num), Nat.div_eq_of_lt hlt, zero_add]
  unfold qdec; rw [e1, e2, hn]
  have : (c.num + 32768 - 32768 : ℤ) = c.num := by ring
  rw [this]; exact Rat.num_div_den c

def fin1262 (x : ℕ) : Fin 1262 := ⟨x % 1262, Nat.mod_lt _ (by norm_num)⟩

def pip (i : ℕ) : ℕ := sl PIK 11 i
def ddv (i : ℕ) : ℚ := qdec (sl ODK 32 i)
def oov (i : ℕ) : ℚ := qdec (sl OPK 32 i)

theorem lt_piL : ∀ x ∈ piL, x < 2 ^ 11 := by decide +kernel
theorem lt_fA' : ∀ x ∈ fA, x < 2 ^ 11 := by decide +kernel
theorem lt_fB' : ∀ x ∈ fB, x < 2 ^ 11 := by decide +kernel
theorem pack_pi : pkw 11 piL = PIK := by decide +kernel
theorem pack_fA : pkw 11 fA = FAK := by decide +kernel
theorem pack_fB : pkw 11 fB = FBK := by decide +kernel

theorem pip_eq (i : ℕ) : pip i = piL.getD i 0 := by
  unfold pip; rw [← pack_pi]; exact pkw_get 11 piL lt_piL i


def pkQ : List ℚ → ℕ
  | [] => 0
  | c :: l => encQ c + 2 ^ 32 * pkQ l

theorem pkQ_get (l : List ℚ) (hl : ∀ c ∈ l, -32768 < c.num ∧ c.num < 32768 ∧ encQ c < 2 ^ 32) (i : ℕ) :
    qdec (sl (pkQ l) 32 i) = l.getD i 0 := by
  induction l generalizing i with
  | nil => simp [pkQ, sl, qdec]
  | cons x l ih =>
    have hx := hl x List.mem_cons_self
    have ih' := fun i => ih (fun y hy => hl y (List.mem_cons_of_mem _ hy)) i
    have hw : 0 < 2 ^ 32 := by positivity
    cases i with
    | zero =>
      simp only [sl, pkQ, Nat.mul_zero, pow_zero, Nat.div_one, List.getD_cons_zero]
      rw [Nat.add_mul_mod_self_left, Nat.mod_eq_of_lt hx.2.2]; exact qdec_encQ x hx.1 hx.2.1
    | succ i =>
      have e : 2 ^ (32 * (i + 1)) = 2 ^ 32 * 2 ^ (32 * i) := by rw [mul_add, mul_one, pow_add, mul_comm]
      have e2 : (encQ x + 2 ^ 32 * pkQ l) / 2 ^ 32 = pkQ l := by
        rw [Nat.add_mul_div_left _ _ hw, Nat.div_eq_of_lt hx.2.2, zero_add]
      have := ih' i
      simp only [sl] at this ⊢
      rw [e, ← Nat.div_div_eq_div_mul]; simp only [pkQ]; rw [e2, this, List.getD_cons_succ]

theorem odL_ok : ∀ c ∈ odL, -32768 < c.num ∧ c.num < 32768 ∧ encQ c < 2 ^ 32 := by decide +kernel
theorem opL_ok : ∀ c ∈ opL, -32768 < c.num ∧ c.num < 32768 ∧ encQ c < 2 ^ 32 := by decide +kernel
theorem pack_od : pkQ odL = ODK := by decide +kernel
theorem pack_op : pkQ opL = OPK := by decide +kernel

theorem ddv_eq (i : ℕ) : ddv i = odL.getD i 0 := by
  unfold ddv; rw [← pack_od]; exact pkQ_get odL odL_ok i
theorem oov_eq (i : ℕ) : oov i = opL.getD i 0 := by
  unfold oov; rw [← pack_op]; exact pkQ_get opL opL_ok i

def pOpt (i : Fin 1262) : Option (Fin 1262) := if oov i ≠ 0 then some (fin1262 (pip i)) else none
noncomputable def O7761 : Matrix (Fin 1262) (Fin 1262) ℚ := funcMat (fun i => ddv i) (fun i => oov i) pOpt

theorem chkD : ∀ i < 1262, ddv i ≠ 0 := by decide +kernel
theorem chkP : ∀ i < 1262, oov i ≠ 0 → (pip i < 1262 ∧ pip i ≠ i ∧
    (oov (pip i) = 0 ∨ (pip (pip i) = i ∧ ddv i * ddv (pip i) ≠ oov i * oov (pip i)))) := by decide +kernel

theorem minors7761 (C : Finset (Fin 1262)) :
    ((O7761).submatrix (fun c : C => (c : Fin 1262)) (fun c : C => (c : Fin 1262))).det ≠ 0 := by
  refine minors_ne_zero (fun i : Fin 1262 => ddv i) (fun i : Fin 1262 => oov i) pOpt (fun i => chkD i i.2) ?_
    (fun i : Fin 1262 => if oov i ≠ 0 then 1 else 0) ?_ C
  · intro i h
    unfold pOpt at h
    by_cases ho : oov i ≠ 0
    · rw [if_pos ho] at h
      have hc := chkP i i.2 ho
      have h' : (fin1262 (pip i)) = i := Option.some.inj h
      have : (pip i) % 1262 = i := congrArg Fin.val h'
      rw [Nat.mod_eq_of_lt hc.1] at this
      exact hc.2.1 this
    · rw [if_neg ho] at h; exact absurd h (by simp)
  · intro i j h
    unfold pOpt at h
    by_cases ho : oov i ≠ 0
    · rw [if_pos ho] at h
      have hc := chkP i i.2 ho
      have h' : (fin1262 (pip i)) = j := Option.some.inj h
      have hj : (j : ℕ) = pip i := by rw [← h']; exact Nat.mod_eq_of_lt hc.1
      by_cases hz : oov j = 0
      · left; simp [hz, ho]
      · right
        have hc2 := hc.2.2
        rcases hc2 with h0 | ⟨h1, h2⟩
        · exfalso; rw [← hj] at h0; exact hz h0
        · constructor
          · unfold pOpt; rw [if_pos hz]
            apply congrArg some; apply Fin.ext
            show (pip j) % 1262 = i
            rw [hj, h1]; exact Nat.mod_eq_of_lt i.2
          · rw [hj]; exact h2
    · rw [if_neg ho] at h; exact absurd h (by simp)

end Bridge7761
#print axioms Bridge7761.minors7761
#print axioms Bridge7761.pip_eq
#print axioms Bridge7761.ddv_eq
