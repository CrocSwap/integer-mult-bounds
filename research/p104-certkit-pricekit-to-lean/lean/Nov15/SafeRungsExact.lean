/-
SafeRungsExact (lane LEAN-R12b, Nov 18).  SafeRungs.P0_kappa / U0_kappa with the real-number certificates DISCHARGED:
CertP0 := SafeCertP0.cert, CertU0 := SafeCertU0.cert (exact, kernel-checked: convex envelope + integer-certified enclosures).
-/
import Nov15.SafeRungs
import Nov15.SafeCertP0
import Nov15.SafeCertU0

open SafeRungsPrice SafeRungsClique Finset

namespace SafeRungsExact

theorem certP0 : CertP0 := SafeCertP0.cert
theorem certU0 : CertU0 := SafeCertU0.cert

variable {α : Type*} {ι μ : Type*} {d : α → α → ℝ} (hm : PriceMetric d)
  (H : Finset ι) (hc : ι → ℝ) (hn : ι → ℕ) (hx : ι → ℕ → α)
  (M : Finset μ) (mn : μ → ℕ) (mx : μ → ℕ → α)
  (no : ℕ) (oa ob : ℕ → α) (nst : ℝ)
  (hH : ∀ i ∈ H, hc i ≤ d (hx i 0) (hx i (hn i)))
  (hM : ∀ j ∈ M, 1 ≤ mn j ∧ 8 ≤ d (mx j 0) (mx j (mn j)))
  (hM400 : M.card = 400) (hnst : 0 ≤ nst)

include hm hH hM hM400 hnst in
theorem P0_kappa_exact (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ ≤ 1)
    (hF : 0 ≤ FW d (1 - κ) H hc hn hx M mn mx no oa ob nst) : κ < 227043 / 10000000 :=
  SafeRungs.P0_kappa hm H hc hn hx M mn mx no oa ob nst hH hM hM400 hnst certP0 κ hκ0 hκ1 hF

open Classical in
include hm hH hM hM400 hnst in
theorem U0_kappa_exact (tgt : Fin no → Finset ℕ)
    (hR1 : 8 ≤ (Finset.univ.filter (fun i => InDown (tgt i))).card)
    (hR2 : 8 ≤ (Finset.univ.filter (fun i => InUp (tgt i))).card)
    (hO1 : ∀ k < no, 1 ≤ d (oa k) (ob k)) (hR3 : 104 - (no : ℝ) ≤ nst)
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ ≤ 1)
    (hF : 0 ≤ FW d (1 - κ) H hc hn hx M mn mx no oa ob nst) : κ < 204111 / 10000000 :=
  SafeRungs.U0_kappa hm H hc hn hx M mn mx no oa ob nst hH hM hM400 hnst certU0 tgt hR1 hR2 hO1 hR3 κ hκ0 hκ1 hF

end SafeRungsExact
