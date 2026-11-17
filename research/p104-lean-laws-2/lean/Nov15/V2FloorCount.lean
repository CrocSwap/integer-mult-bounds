/-
V2FloorCount (Nov 16; started by LEAN-NEXT21, finished by lane LEAN-KERNEL): the Gaussian count lemma for subspaces
of F₂⁹, kernel-only, sorry-free.

  #{U : Y ≤ U, dim U = d} ≤ [9 − b choose d − b]₂      (dim Y = b)

The proof (double counting pairs (U, v), v ∈ U \ Y, induction on d − b) is `count_le'` in V2FloorKernelLemmas;
`Mt b d` is the table of Gaussian binomials [9−b choose d−b]₂ (check.c / flagcheck.c's M(b,d)).
-/
import Nov15.V2FloorKernelLemmas

namespace V2Floor
open Finset

attribute [local instance 10] Classical.propDecidable

theorem gaussian_count (Y : Sub) (d : ℕ) :
    (univ.filter (fun U : Sub => Y ≤ U ∧ fdim U = d)).card ≤ Mt (fdim Y) d := count_le' Y d

end V2Floor
