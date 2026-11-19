import Nov15.DecoderWall6Fac
import Nov15.DecoderWall4Data

/-!
# DecoderWall6Gen : the P104 decoder hypotheses and the frame identities.
`oddb p q` = the 9-bit labels of ports `p q` (REBASET1 order, `DW4.labs`) have odd dot product.
`Hyp W U`: `card T = 8`, `M_pp = 1`, `M_pq = 0` for `p ≠ q` with odd labels (`M = W Uᵀ`).
-/
namespace DW6

def lab (i : ℕ) : ℕ := DW4.labs.getD i 0
def dotb (a b : ℕ) : Bool := ((List.range 9).filter fun k => a.testBit k && b.testBit k).length % 2 == 1
def oddb (p q : Fin 104) : Bool := dotb (lab p.val) (lab q.val)

variable {T K : Type*} [Fintype T] [DecidableEq T] [Field K]

structure Hyp (W U : Fin 104 → T → K) : Prop where
  card : Fintype.card T = 8
  diag : ∀ p, Mx W U p p = 1
  odd : ∀ p q, p ≠ q → oddb p q = true → Mx W U p q = 0

/-- 8 ports, pairwise distinct with pairwise odd labels. -/
def FrameOK (c : Fin 8 → Fin 104) : Prop := ∀ i j : Fin 8, i ≠ j → c i ≠ c j ∧ oddb (c i) (c j) = true

instance (c : Fin 8 → Fin 104) : Decidable (FrameOK c) := by unfold FrameOK; infer_instance

theorem frame_fac {W U : Fin 104 → T → K} (h : Hyp W U) (c : Fin 8 → Fin 104) (hc : FrameOK c)
    (p r : Fin 104) : Mx W U p r = ∑ i, Mx W U p (c i) * Mx W U (c i) r := by
  refine factor W U c h.card (fun i j => ?_) p r
  by_cases hij : i = j
  · subst hij; simp [h.diag]
  · rw [if_neg hij]; exact h.odd _ _ (hc i j hij).1 (hc i j hij).2

theorem frame8 {W U : Fin 104 → T → K} (h : Hyp W U) (f0 f1 f2 f3 f4 f5 f6 f7 : Fin 104)
    (hc : FrameOK ![f0, f1, f2, f3, f4, f5, f6, f7]) (p r : Fin 104) :
    Mx W U p r = Mx W U p f0 * Mx W U f0 r + Mx W U p f1 * Mx W U f1 r + Mx W U p f2 * Mx W U f2 r
      + Mx W U p f3 * Mx W U f3 r + Mx W U p f4 * Mx W U f4 r + Mx W U p f5 * Mx W U f5 r
      + Mx W U p f6 * Mx W U f6 r + Mx W U p f7 * Mx W U f7 r := by
  rw [frame_fac h _ hc p r, Fin.sum_univ_eight]
  rfl

end DW6

