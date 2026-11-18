import Nov15.JunkLawA
import Nov15.CongestionNativeN

/-!
CEILING WITHOUT hJ: `ceiling_noHJ` = `ceiling_native_N96` with `hJ : 96 <= |J|` DERIVED from Law A.
The junk set `J` is tied to the abstract model: `hJdef : J = junkSet m.M` (the off-diagonal nonzeros of the arrival rows), `m : LawAModel K 104 D` carries the Law A
premises (spans of D arrival vectors, nonzero diagonal, odd off-diagonals zero, 48-partner universe) and `hD : D <= 56` is the own56 premise. Lean's `D` is the size of ANY spanning set of arrival vectors, so `hD` in effect says rank M <= 56 (the natives have rank 11, D = 24); it is implied by <= 56 owned descending moves, hence by descending mass <= 56.
The same `J` carries the junk count, `hcong` and `hdist`; `hJdef` is a naming link and Lean does not tie `J` to any word.
Conclusion: `F(1 - t, invoice (caller 6 7) n 17) < 0` for t in [tN0, 1], tN0 = .0151027, i.e. kappa <= .0151027.  See JunkLawA.md.
-/
namespace CongestionNative
open NumCertK JointCeiling CallerCost CongestionI3 CongestionI3Dual Finset

/-- **the no-hJ ceiling.** -/
theorem ceiling_noHJ {ι : Type*} [DecidableEq ι] {K : Type*} [Field K] {D : ℕ}
    (m : JunkLawA.LawAModel K 104 D) (hD : D ≤ 56)
    (R : Finset ι) (nR : ι → ℕ) (dR : ι → ℕ → ℕ)
    (hmono : ∀ r ∈ R, ∀ i < nR r, dR r i ≤ dR r (i + 1)) (hd9 : ∀ r ∈ R, dR r (nR r) ≤ 9)
    (hmix : (R.filter fun r => Mixed dR nR r).card ≤ 5)
    (n : Inv) (ks : List ℕ) (mr st : ℕ) (E : ℝ → ℝ) (J : Finset (ℕ × ℕ)) (distF : ℝ → ℕ × ℕ → ℝ) (spF cstF : ℝ → ℝ)
    (hk : ∀ k ∈ ks, 1 ≤ k ∧ k ≤ 9) (hmass : 56 ≤ ks.sum) (hmd : 8 ≤ ks.length) (hmr : 8 ≤ mr)
    (hF : ∀ s, 0 ≤ s → s ≤ 1 → Finv s n ≤ -400 * (8 : ℝ) ^ s - dprice ks s - mr - E s)
    (hY : 104 ≤ st + (ks.length + mr))
    (hst : ∀ s, 0 ≤ s → s ≤ 1 → (2 - (2 : ℝ) ^ s) * st ≤ E s)
    (hEex : ∀ s, 0 ≤ s → s ≤ 1 → ∑ r ∈ R, ex (gs s) (lev dR r) (nR r) ≤ E s)
    (hcong : ∀ s, 9 / 10 ≤ s → s ≤ 1 - ((tN0 : ℚ) : ℝ) →
      ∑ p ∈ J, min (distF s p) (capC s) - corrC cstF s ≤
        ∑ r ∈ R, ∑ i ∈ range (nR r), c2 (gs s) (lev dR r i) (lev dR r (i + 1)) + Omega ks mr s)
    (hdist : ∀ s, 9 / 10 ≤ s → s ≤ 1 - ((tN0 : ℚ) : ℝ) → ∀ p ∈ J, spF (1 - s) ≤ distF s p)
    (hJdef : J = JunkLawA.junkSet m.M)
    (hspMono : MonotoneOn spF (Set.Icc ((tN0 : ℚ) : ℝ) (1 / 10)))
    (hcstMono : MonotoneOn cstF (Set.Icc ((tN0 : ℚ) : ℝ) (1 / 10)))
    (hspTabN : ((spFloN0 : ℚ) : ℝ) ≤ spF ((tN0 : ℚ) : ℝ) ∧ ((spFloN1 : ℚ) : ℝ) ≤ spF ((tN1 : ℚ) : ℝ) ∧
      ((spFloN2 : ℚ) : ℝ) ≤ spF ((tN2 : ℚ) : ℝ) ∧ ((spFloN3 : ℚ) : ℝ) ≤ spF ((tN3 : ℚ) : ℝ) ∧
      ((spFloN4 : ℚ) : ℝ) ≤ spF ((tN4 : ℚ) : ℝ))
    (hcstTabN : cstF ((tN1 : ℚ) : ℝ) ≤ ((cHN0 : ℚ) : ℝ) ∧ cstF ((tN2 : ℚ) : ℝ) ≤ ((cHN1 : ℚ) : ℝ) ∧
      cstF ((tN3 : ℚ) : ℝ) ≤ ((cHN2 : ℚ) : ℝ) ∧ cstF ((tN4 : ℚ) : ℝ) ≤ ((cHN3 : ℚ) : ℝ) ∧
      cstF ((tN5 : ℚ) : ℝ) ≤ ((cHN4 : ℚ) : ℝ)) :
    ∀ t : ℝ, ((tN0 : ℚ) : ℝ) ≤ t → t ≤ 1 → Finv (1 - t) (invoice (caller 6 7) n 17) < 0 := by
  have hJ : 96 ≤ J.card := by rw [hJdef]; exact JunkLawA.junkSet_card_ge_96 m hD
  exact ceiling_native_N96 R nR dR hmono hd9 hmix n ks mr st E J distF spF cstF hk hmass hmd hmr hF hY hst hEex hcong hdist hJ
    hspMono hcstMono hspTabN hcstTabN

end CongestionNative

#print axioms CongestionNative.ceiling_noHJ
