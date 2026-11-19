import Nov15.DecoderWall4Defs
import Nov15.DecoderWall4C0
import Nov15.DecoderWall4C1
import Nov15.DecoderWall4C2
import Nov15.DecoderWall4C3
import Nov15.DecoderWall4C4
import Nov15.DecoderWall4C5
import Nov15.DecoderWall4C6
import Nov15.DecoderWall4Cert
import Nov15.DecoderWall4Cover

open Matrix
set_option maxHeartbeats 0
namespace DW4

theorem cats_ok (k : ℕ) (hk : k < catD.length) : catOK k := by
  rw [catD_length] at hk
  by_cases h6 : 180 ≤ k
  · exact cats_ok_6 k (by rw [List.mem_range'_1]; omega)
  · have h : ∀ i, i < 6 → k ∈ List.range' (30 * i) 30 → catOK k := by
      intro i hi hmem
      interval_cases i
      · exact cats_ok_0 k hmem
      · exact cats_ok_1 k hmem
      · exact cats_ok_2 k hmem
      · exact cats_ok_3 k hmem
      · exact cats_ok_4 k hmem
      · exact cats_ok_5 k hmem
    exact h (k / 30) (by omega) (by rw [List.mem_range'_1]; omega)

/-! ### From certificates to ranks -/

noncomputable def Gq : Matrix (Fin 104) (Fin 104) ℚ := Matrix.of fun i j => (g i j : ℚ)

noncomputable def blk (S : Finset (Fin 104)) : Matrix S S ℚ :=
  Gq.submatrix ((↑) : S → Fin 104) ((↑) : S → Fin 104)

theorem rank_blk_mono {S S' : Finset (Fin 104)} (h : S ⊆ S') : (blk S).rank ≤ (blk S').rank := by
  have := Matrix.rank_submatrix_le (blk S') (fun x : S => (⟨x.1, h x.2⟩ : S')) (fun x : S => (⟨x.1, h x.2⟩ : S'))
  exact this

theorem rank_of_cert (S : Finset (Fin 104)) (k : ℕ) (hk : catOK k)
    (hP : ∀ i : Fin 8, ∃ h : portOf k i < 104, (⟨portOf k i, h⟩ : Fin 104) ∈ S) :
    8 ≤ (blk S).rank := by
  classical
  choose hlt hmem using hP
  let pf : Fin 8 → S := fun i => ⟨⟨portOf k i, hlt i⟩, hmem i⟩
  let A : Matrix (Fin 8) (Fin 8) ℚ := (blk S).submatrix pf pf
  let X : Matrix (Fin 8) (Fin 8) ℚ := Matrix.of fun l j => (xOf k l j : ℚ)
  have hAX : A * X = Matrix.diagonal (fun _ => (dOf k : ℚ)) := by
    ext i j
    have := hk.2.2 i j
    have h2 : ((∑ l : Fin 8, g (portOf k i) (portOf k l) * xOf k l j : ℤ) : ℚ)
        = ((if (i : ℕ) = j then dOf k else 0 : ℤ) : ℚ) := by rw [this]
    simp only [Matrix.mul_apply, A, X, blk, Gq, pf, Matrix.submatrix_apply, Matrix.of_apply]
    push_cast at h2
    rw [h2]
    by_cases hij : i = j
    · subst hij; simp
    · have : (i : ℕ) ≠ j := fun e => hij (Fin.ext e)
      simp [hij, this, Matrix.diagonal_apply_ne _ hij]
  have h1 : (A * X).rank ≤ A.rank := Matrix.rank_mul_le_left _ _
  have h2 : A.rank ≤ (blk S).rank := Matrix.rank_submatrix_le (blk S) pf pf
  have hd : (dOf k : ℚ) ≠ 0 := by exact_mod_cast hk.1
  have h3 : (Matrix.diagonal (fun _ : Fin 8 => (dOf k : ℚ))).rank = 8 := by
    rw [Matrix.rank_diagonal]; simp [hd]
  rw [hAX, h3] at h1
  omega

def outS (y : ℕ) : Finset (Fin 104) := Finset.univ.filter fun p => dotb (lab p) y = true
def out2 (a b : ℕ) : Finset (Fin 104) := Finset.univ.filter fun p => (dotb (lab p) a || dotb (lab p) b) = true

/-- Every non-bad hyperplane `y^⊥` (y ∈ 1..511): the outside ports have Gram rank 8. -/
theorem hyperplane_good (y : ℕ) (hy : y < 512) (hy0 : y ≠ 0) (hb : y ∉ bad) : 8 ≤ (blk (outS y)).rank := by
  have hc := cover_y y hy
  rcases hc with h | h | ⟨p, hp, hpy⟩
  · exact absurd h hy0
  · exact absurd h hb
  · obtain ⟨hlt, hdot⟩ := certY_ok p hp
    have hk := cats_ok p.2 hlt
    apply rank_of_cert (outS y) p.2 hk
    intro i
    have h1 : portOf p.2 i < 104 := (hk.2.1 i)
    refine ⟨h1, ?_⟩
    simp only [outS, Finset.mem_filter, Finset.mem_univ, true_and]
    have := hdot i
    rw [hpy] at this
    exact this

/-- **No 2-dimensional `Y = ⟨a, b⟩` has outside-ports of Gram rank ≤ 7.** -/
theorem codim2_rank (a b : ℕ) (ha : a < 512) (hb : b < 512) (ha0 : a ≠ 0) (hb0 : b ≠ 0) (hab : a ≠ b) :
    8 ≤ (blk (out2 a b)).rank := by
  by_cases hA : a ∈ bad
  · by_cases hB : b ∈ bad
    · -- both bad: explicit pair certificate
      have key : ∀ a b, a ∈ bad → b ∈ bad → a < b → 8 ≤ (blk (out2 a b)).rank := by
        intro a b hA hB hlt
        obtain ⟨t, ht, h1, h2⟩ := cover_P a b hA hB hlt
        obtain ⟨hl, hdot⟩ := certP_ok t ht
        have hk := cats_ok t.2.2 hl
        apply rank_of_cert (out2 a b) t.2.2 hk
        intro i
        refine ⟨hk.2.1 i, ?_⟩
        simp only [out2, Finset.mem_filter, Finset.mem_univ, true_and]
        have := hdot i
        rw [h1, h2] at this
        exact this
      rcases lt_or_gt_of_ne hab with h | h
      · exact key a b hA hB h
      · have e : out2 a b = out2 b a := by
          ext p; simp [out2, Bool.or_comm]
        rw [e]; exact key b a hB hA h
    · refine le_trans (hyperplane_good b hb hb0 hB) (rank_blk_mono ?_)
      intro p hp
      simp only [outS, out2, Finset.mem_filter, Finset.mem_univ, true_and] at hp ⊢
      simp [hp]
  · refine le_trans (hyperplane_good a ha ha0 hA) (rank_blk_mono ?_)
    intro p hp
    simp only [outS, out2, Finset.mem_filter, Finset.mem_univ, true_and] at hp ⊢
    simp [hp]

end DW4

#print axioms DW4.cats_ok
#print axioms DW4.hyperplane_good
#print axioms DW4.codim2_rank
