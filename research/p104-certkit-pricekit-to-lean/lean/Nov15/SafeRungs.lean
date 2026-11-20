/-
SafeRungs (lane LEAN-R12, Nov 18).  The two SAFE universal word rungs of cards/WILD/UCEIL/MINPREM.md (+ERRATUM).
 P0_kappa : kappa < .0227043   from SPEC rank pricing (metric), Theorem-K invoice, the #7113 contract's 400 rank-8 mains.
 U0_kappa : kappa < .0204111   adding V-asc (public strict ascent, l.51) [enters ONLY through R1/R2/R3 counts below]
            and 'every owned move between distinct charts costs >= 1' [hO1, ERRATUM premise].
            n >= 16 owned moves comes from R1 (>= 8 entering a down-set q^perp), R2 (>= 8 entering U_Q) and the
            decide-checked clique Q (SafeRungsClique.owned_ge_16: target-disjoint).  R3 (stops >= 104 - n) is hypothesis hR3.
 Named hypotheses left: CertP0 / CertU0 (real crossing certificates), hR1 hR2 hR3 (paper proofs, WHOLEFLOOR R1-R3 / AUDIT1 c),
 the 400 mains (hM, hM400), owned price >= 1 (hO1), caller data Tcal/Pcal (ladder.log).
Kernel only: no sorry, no native_decide, no axioms.
-/
import Nov15.SafeRungsClique
import Nov15.SafeRungsPrice

open SafeRungsPrice SafeRungsClique Finset

namespace SafeRungs

variable {α : Type*} {ι μ : Type*} {d : α → α → ℝ} (hm : PriceMetric d)
  (H : Finset ι) (hc : ι → ℝ) (hn : ι → ℕ) (hx : ι → ℕ → α)
  (M : Finset μ) (mn : μ → ℕ) (mx : μ → ℕ → α)
  (no : ℕ) (oa ob : ℕ → α) (nst : ℝ)
  (hH : ∀ i ∈ H, hc i ≤ d (hx i 0) (hx i (hn i)))
  (hM : ∀ j ∈ M, 1 ≤ mn j ∧ 8 ≤ d (mx j 0) (mx j (mn j)))
  (hM400 : M.card = 400) (hnst : 0 ≤ nst)

include hm hH hM hM400 hnst in
/-- RUNG P0: every crossing kappa in (0,1] of the word invoice is < .0227043. -/
theorem P0_kappa (cert : CertP0) (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ ≤ 1)
    (hF : 0 ≤ FW d (1 - κ) H hc hn hx M mn mx no oa ob nst) : κ < 227043 / 10000000 := by
  refine kappa_lt (fun t => FW d (1 - t) H hc hn hx M mn mx no oa ob nst) FceilP0 _ ?_ cert κ hκ0 hκ1 hF
  intro t ht0 ht1
  exact P0_ceiling hm (1 - t) (by linarith) (by linarith) H hc hn hx M mn mx no oa ob nst hH hM hM400 hnst

open Classical in
include hm hH hM hM400 hnst in
/-- RUNG U0.  tgt k = target chart (set of labels) of owned move k. -/
theorem U0_kappa (cert : CertU0) (tgt : Fin no → Finset ℕ)
    (hR1 : 8 ≤ (Finset.univ.filter (fun i => InDown (tgt i))).card)
    (hR2 : 8 ≤ (Finset.univ.filter (fun i => InUp (tgt i))).card)
    (hO1 : ∀ k < no, 1 ≤ d (oa k) (ob k))
    (hR3 : 104 - (no : ℝ) ≤ nst)
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ ≤ 1)
    (hF : 0 ≤ FW d (1 - κ) H hc hn hx M mn mx no oa ob nst) : κ < 204111 / 10000000 := by
  classical
  have h16 : 16 ≤ no := owned_ge_16 tgt hR1 hR2
  refine kappa_lt (fun t => FW d (1 - t) H hc hn hx M mn mx no oa ob nst) FceilU0 _ ?_ cert κ hκ0 hκ1 hF
  intro t ht0 ht1
  exact U0_ceiling hm (1 - t) (by linarith) (by linarith) H hc hn hx M mn mx no oa ob nst hH hM hM400 hnst
    hO1 h16 hR3

end SafeRungs
