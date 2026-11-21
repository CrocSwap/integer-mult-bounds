/-
CallerTightDeg (lane TIGHTPAD, Nov 20).  Item (2): the hypothesis "every role has degree >= 2" of the Q = 0 caller laws
(CallerAsm.word_hp_B, CallerAsm.word_hp_A) is DERIVED, not assumed.

Frame level (`Host.deg_ge_two`): in a CallerBridge.Host frame with no thin column (|iota| = 2k, i.e. Q = 0 and T = 0),
char /= 2, every role has |mask| >= 2.
  Proof.  If |mask r| <= 1 pick a stage s0 with mask r ⊆ {s0} (any stage when the mask is empty).  Every column is a host
  column col s a (no thins); off the slot pos s0 it belongs to a stage s /= s0, so s ∉ mask r and B r (col s a) = 0 (hB).
  LEAF-RANK (CallerThin.leaf_rank, F = {r}, Th = ∅, lambda_{s0} /= -1 via Host.knondeg) gives |{r}| <= 0.  Contradiction.
  (Degree 0 is the same argument with an arbitrary slot: the B-row of r vanishes everywhere, so V fixes e_r and P e_r = -e_r
  forces e_r = 0.)
Word level: the Host of a legal type-B word (CallerBridge.hostOf) and of a legal type-A word (CallerJA.hostA, merged slots)
exist under exactly the hypotheses of word_hp_B / word_hp_A minus hdeg, so
  `word_hp_B_nodeg` / `word_hp_A_nodeg` : the Q = 0 headline without the degree hypothesis.
Necessity of Q = 0 for this step: CallerThin's one-host + one-thin frame (A1, B1) is a Host with a degree-1 role
(`thin_leaf_exists`), so with a thin column a leaf IS possible.
Non-vacuity of the frame lemma: `hostK2` = an explicit k = 2, n = 2 Q = 0 Host over Q (V_0 = 2, V_1 = -1/2), `hostK2_deg`.
Kernel only.
-/
import Nov15.CallerJASchema

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace CallerTight
open Finset Matrix CallerSign CallerWord CallerAsm CallerEv CallerHP CallerBridge

section frame
variable {K : Type*} [Field K] {ι : Type*} [Fintype ι] [DecidableEq ι] {n k m : ℕ}
variable {A B : Matrix (Fin n) ι K} {β : ι → ℕ} {mask : Fin n → Finset (Fin k)}

/-- no thin column: Th = ∅. -/
theorem th_empty (H : Host A B β k m mask) (hQ0 : Fintype.card ι = 2 * k) : H.Th = ∅ := by
  rw [← Finset.card_eq_zero, H.th_card, hQ0, Nat.sub_self]

/-- Q = 0 frames have no role of degree <= 1. -/
theorem deg_ge_two (H : Host A B β k m mask) (h2 : (2 : K) ≠ 0) (hQ0 : Fintype.card ι = 2 * k) (hk : 0 < k)
    (r : Fin n) : 2 ≤ (mask r).card := by
  by_contra hlt
  push_neg at hlt
  obtain ⟨s0, hs0⟩ : ∃ s0 : Fin k, ∀ s ∈ mask r, s = s0 := by
    rcases (mask r).eq_empty_or_nonempty with he | ⟨s1, hs1⟩
    · exact ⟨⟨0, hk⟩, fun s hs => by simp [he] at hs⟩
    · refine ⟨s1, fun s hs => ?_⟩
      exact Finset.card_le_one.mp (by omega) s hs s1 hs1
  have hTh := th_empty H hQ0
  have h := CallerThin.leaf_rank A B β m (H.pos s0) (H.hposlt s0) h2 H.hP (H.knondeg s0) {r} ∅
    (by
      intro r' hr' i hb _
      rw [Finset.mem_singleton] at hr'
      subst hr'
      have hT : i ∉ H.Th := by rw [hTh]; simp
      obtain ⟨s, a, rfl⟩ := (H.notTh_iff i).1 hT
      have hs : s ≠ s0 := by
        intro e; apply hb; rw [H.hcolβ, e]
      exact H.hB r' s (fun hm => hs (hs0 s hm)) a)
  simp at h

end frame

/-! ## word level: the Q = 0 headlines without the degree hypothesis -/
section word
variable {n k : ℕ} {w : CWord n k}

/-- HEADLINE (type B), degree hypothesis removed. -/
theorem word_hp_B_nodeg (hL : Legal w) (J : JB w) (hodd : ∀ r, w.ex r % 2 = 1) (hk : 3 ≤ k)
    (hQ0 : Fintype.card (Iota w) = 2 * k) (hn : n + 2 = Fintype.card (Iota w))
    (hlam : ∀ s, IsUnit ((sgK (βw w) (sgG (Aw w Complex.I) (Bw w Complex.I))).submatrix (J.col s) (J.col s)).det) :
    cHat w ≤ HPr k :=
  word_hp_B hL J hodd hk hQ0 hn hlam
    (fun r => deg_ge_two (hostOf hL J hodd hlam) (by norm_num) hQ0 (by omega) r)

/-- HEADLINE (type A), degree hypothesis removed. -/
theorem word_hp_A_nodeg (hL : Legal w) (J : JA w) (hodd : ∀ r, w.ex r % 2 = 1) (hk : 3 ≤ k)
    (hQ0 : Fintype.card (Iota w) = 2 * k) (hn : n + 2 = Fintype.card (Iota w))
    (hlam : ∀ s, IsUnit ((sgK (βw w) (sgG (Aw w Complex.I) (Bw w Complex.I))).submatrix (J.col s) (J.col s)).det) :
    cHat w ≤ HPr k :=
  word_hp_A hL J hodd hk hQ0 hn hlam
    (fun r => deg_ge_two (CallerJA.hostA hL J hodd hlam) (by norm_num) hQ0 (by omega) r)

/-- the derived degree law itself, type B (any k >= 1). -/
theorem word_deg_B (hL : Legal w) (J : JB w) (hodd : ∀ r, w.ex r % 2 = 1) (hk : 1 ≤ k)
    (hQ0 : Fintype.card (Iota w) = 2 * k)
    (hlam : ∀ s, IsUnit ((sgK (βw w) (sgG (Aw w Complex.I) (Bw w Complex.I))).submatrix (J.col s) (J.col s)).det)
    (r : Fin n) : 2 ≤ (w.mask r).card :=
  deg_ge_two (hostOf hL J hodd hlam) (by norm_num) hQ0 (by omega) r

/-- the derived degree law itself, type A. -/
theorem word_deg_A (hL : Legal w) (J : JA w) (hodd : ∀ r, w.ex r % 2 = 1) (hk : 1 ≤ k)
    (hQ0 : Fintype.card (Iota w) = 2 * k)
    (hlam : ∀ s, IsUnit ((sgK (βw w) (sgG (Aw w Complex.I) (Bw w Complex.I))).submatrix (J.col s) (J.col s)).det)
    (r : Fin n) : 2 ≤ (w.mask r).card :=
  deg_ge_two (CallerJA.hostA hL J hodd hlam) (by norm_num) hQ0 (by omega) r

end word

/-! ## non-vacuity and necessity -/
section inst

/-- k = 2, n = 2, Q = 0: stage t has columns (t, 0), (t, 1); A_0 = I, A_1 = -3/2 I, B_t = I.
    V_0 = 2, V_1 = -1/2, product -1; K_00 = 3 I, K_11 = 1/2 I. -/
def a2 : Fin 2 → ℚ := ![1, -3/2]
def AK2 : Matrix (Fin 2) (Fin 2 × Fin 2) ℚ := Matrix.of fun r c => a2 c.1 * (if r = c.2 then 1 else 0)
def BK2 : Matrix (Fin 2) (Fin 2 × Fin 2) ℚ := Matrix.of fun r c => if r = c.2 then 1 else 0
def βK2 : Fin 2 × Fin 2 → ℕ := fun c => c.1.val
def maskK2 : Fin 2 → Finset (Fin 2) := fun _ => univ

theorem prodK2 : sgProd AK2 BK2 βK2 2 = -1 := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [sgProd, sgStage, blkPi, AK2, BK2, βK2, a2, Matrix.mul_apply, Matrix.one_apply,
      Matrix.diagonal_apply, Fintype.sum_prod_type, Fin.sum_univ_succ] <;> norm_num

theorem lamK2 (s : Fin 2) :
    ((sgK βK2 (sgG AK2 BK2)).submatrix (fun a : Fin 2 => (s, a)) (fun a : Fin 2 => (s, a))).det ≠ 0 := by
  fin_cases s <;>
    simp [Matrix.det_fin_two, sgK, sgDiag, sgUp, sgLow, sgG, AK2, BK2, βK2, a2, Matrix.mul_apply,
      Matrix.one_apply, Fin.sum_univ_succ, Matrix.transpose_apply] <;> norm_num

def hostK2 : Host AK2 BK2 βK2 2 2 maskK2 where
  col := fun s a => (s, a)
  pos := fun s => s.val
  hβ := fun i => i.1.isLt
  hP := prodK2
  hpos := fun s t h => Fin.ext h
  hposlt := fun s => s.isLt
  hcolβ := fun s a => rfl
  hcolinj := fun p q h => h
  hslot := fun s i hi => ⟨i.2, Prod.ext (Fin.ext hi) rfl⟩
  hw := by
    intro t ht
    have : Fintype.card {i : Fin 2 × Fin 2 // βK2 i = t} ≤ Fintype.card (Fin 2) := by
      apply Fintype.card_le_of_injective (fun i => i.1.2)
      intro i j h
      apply Subtype.ext
      exact Prod.ext (Fin.ext (i.2.trans j.2.symm)) h
    simpa using this
  hlam := lamK2
  hA := fun r s hs => by simp [maskK2] at hs
  hB := fun r s hs => by simp [maskK2] at hs

/-- the frame lemma applies (hypotheses satisfiable, Q = 0). -/
theorem hostK2_deg : ∀ r, 2 ≤ (maskK2 r).card :=
  fun r => deg_ge_two hostK2 (by norm_num) (by simp) (by norm_num) r

/-- necessity of Q = 0: with one thin column (CallerThin's A1/B1, n = 1, k = 1) the Host has a degree-1 role. -/
theorem thin_leaf_exists : (inst_mask 0).card = 1 ∧ Fintype.card (Fin 3) ≠ 2 * 1 := by
  simp [inst_mask]

/-- and `instHost` is a genuine Host (so `deg_ge_two` cannot hold without hQ0). -/
theorem thin_needed : ¬ (2 ≤ (inst_mask 0).card) := by simp [inst_mask]

end inst
end CallerTight

#print axioms CallerTight.deg_ge_two
#print axioms CallerTight.word_hp_B_nodeg
#print axioms CallerTight.word_hp_A_nodeg
#print axioms CallerTight.word_deg_B
#print axioms CallerTight.word_deg_A
#print axioms CallerTight.hostK2_deg
#print axioms CallerTight.thin_leaf_exists
