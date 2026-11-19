/-
DecoderWall7 .  
`D56_rank8_anyk` : a decoder of the live P104 pattern with ANY number of rows k whose factors W, U (104 x k)
have rank <= 8 has mass >= 56.  (WALL9 step 2; replaces Wall56 for every decoder with rank M <= 8.)
Route: rank M = 8 (clique8 gives I_8) => M = M[:,F] M[F,:] (column spaces agree) => an 8-row decoder with the
same M => DW6.rigid_gram (M = L G L^-1 / 2) => every live column of W (resp. U) lies in col M (resp. col M^T),
so a column vanishing on S gives rank G_SS <= rank M[S,S] <= 7 => RigidCols (on the live rows) => DF.D56_decoder.
Kernel only, no hypotheses.
-/
import Nov15.DecoderFactsRigid
import Mathlib.LinearAlgebra.Matrix.Rank

open Matrix
set_option maxHeartbeats 0
namespace DW7

abbrev Wm {T : Type} (W : Fin 104 → T → ℚ) : Matrix (Fin 104) T ℚ := Matrix.of fun p k => W p k

theorem range_mul_le {m n o : Type*} [Fintype n] [Fintype o] (A : Matrix m n ℚ) (B : Matrix n o ℚ) :
    LinearMap.range (A * B).mulVecLin ≤ LinearMap.range A.mulVecLin := by
  rw [Matrix.mulVecLin_mul]; exact LinearMap.range_comp_le_range _ _

/-- A column of `A` lies in `col (A Bᵀ)` when `rank A <= 8 <= rank (A Bᵀ)`. -/
theorem col_mem {T : Type} [Fintype T] (A B : Matrix (Fin 104) T ℚ) (hA : A.rank ≤ 8)
    (h8 : 8 ≤ (A * Bᵀ).rank) (t : T) :
    (fun p => A p t) ∈ LinearMap.range (A * Bᵀ).mulVecLin := by
  classical
  have hle := range_mul_le A Bᵀ
  have heq : LinearMap.range (A * Bᵀ).mulVecLin = LinearMap.range A.mulVecLin :=
    Submodule.eq_of_le_of_finrank_le hle (by
      have h1 : Module.finrank ℚ (LinearMap.range A.mulVecLin) = A.rank := rfl
      have h2 : Module.finrank ℚ (LinearMap.range (A * Bᵀ).mulVecLin) = (A * Bᵀ).rank := rfl
      omega)
  rw [heq]
  refine ⟨Pi.single t 1, ?_⟩
  ext p
  simp [Matrix.mulVecLin_apply, Matrix.mulVec, dotProduct, Pi.single_apply]

/-- If `M` has rank <= 8 and a nonzero vector of `col M` vanishes on `S`, then `M[S,S]` has rank <= 7. -/
theorem rank_sub_le_seven (M : Matrix (Fin 104) (Fin 104) ℚ) (h8 : M.rank ≤ 8) (S : Finset (Fin 104))
    (v : Fin 104 → ℚ) (hv : v ∈ LinearMap.range M.mulVecLin) (hv0 : v ≠ 0) (hS : ∀ p ∈ S, v p = 0) :
    (M.submatrix ((↑) : S → Fin 104) ((↑) : S → Fin 104)).rank ≤ 7 := by
  classical
  have h1 : (M.submatrix ((↑) : S → Fin 104) ((↑) : S → Fin 104)).rank
      ≤ (M.submatrix ((↑) : S → Fin 104) id).rank :=
    Matrix.rank_submatrix_le (M.submatrix ((↑) : S → Fin 104) id) id ((↑) : S → Fin 104)
  refine h1.trans ?_
  let V := LinearMap.range M.mulVecLin
  let Rs : (Fin 104 → ℚ) →ₗ[ℚ] (S → ℚ) := LinearMap.funLeft ℚ ℚ ((↑) : S → Fin 104)
  let Ψ : V →ₗ[ℚ] (S → ℚ) := Rs ∘ₗ V.subtype
  have e1 : (M.submatrix ((↑) : S → Fin 104) id).mulVecLin = Rs ∘ₗ M.mulVecLin := by
    ext x s; rfl
  have e2 : LinearMap.range (M.submatrix ((↑) : S → Fin 104) id).mulVecLin = LinearMap.range Ψ := by
    rw [e1, LinearMap.range_comp]
    simp only [Ψ, LinearMap.range_comp, Submodule.range_subtype, V]
  have hnull := LinearMap.finrank_range_add_finrank_ker Ψ
  have hV : Module.finrank ℚ V ≤ 8 := h8
  have hker : 0 < Module.finrank ℚ (LinearMap.ker Ψ) := by
    refine (Module.finrank_pos_iff_exists_ne_zero (R := ℚ) (M := LinearMap.ker Ψ)).2 ?_
    refine ⟨⟨⟨v, hv⟩, ?_⟩, ?_⟩
    · rw [LinearMap.mem_ker]
      ext s
      exact hS s.1 s.2
    · intro h
      apply hv0
      have := congrArg (fun z => (z : V).1) (congrArg Subtype.val h)
      simpa using this
  have : (M.submatrix ((↑) : S → Fin 104) id).rank = Module.finrank ℚ (LinearMap.range Ψ) := by
    rw [← e2]; rfl
  omega

/-- rank of the blk from a rank of the `M[S,S]` where `M = L G L^-1 / 2`. -/
theorem blk_rank_le (M : Matrix (Fin 104) (Fin 104) ℚ) (lam : Fin 104 → ℚ) (hl : ∀ p, lam p ≠ 0)
    (hM : ∀ p q, M p q = lam p / lam q * (DW4.g p.val q.val : ℚ) / 2) (S : Finset (Fin 104))
    (h7 : (M.submatrix ((↑) : S → Fin 104) ((↑) : S → Fin 104)).rank ≤ 7) : (DW4.blk S).rank ≤ 7 := by
  classical
  have e : DW4.blk S = Matrix.diagonal (fun p : S => 2 / lam p.1) *
      (M.submatrix ((↑) : S → Fin 104) ((↑) : S → Fin 104)) * Matrix.diagonal (fun r : S => lam r.1) := by
    ext p r
    have hm := hM p.1 r.1
    simp only [DW4.blk, DW4.Gq, Matrix.submatrix_apply, Matrix.of_apply, Matrix.mul_apply,
      Matrix.diagonal_apply, mul_ite, ite_mul, mul_zero, zero_mul, Finset.sum_ite_eq, Finset.mem_univ, if_true,
      Finset.sum_ite_eq']
    have h1 := hl p.1
    have h2 := hl r.1
    rw [hm]
    field_simp
  rw [e]
  exact ((Matrix.rank_mul_le_left _ _).trans (Matrix.rank_mul_le_right _ _)).trans h7

/-- Frame factorisation of a rank <= 8 matrix with `M[F,F] = I`. -/
theorem frame_factor (M : Matrix (Fin 104) (Fin 104) ℚ) (h8 : M.rank ≤ 8) (F : Fin 8 → Fin 104)
    (hF : ∀ i j, M (F i) (F j) = if i = j then 1 else 0) (p r : Fin 104) :
    M p r = ∑ i, M p (F i) * M (F i) r := by
  classical
  let E : Matrix (Fin 104) (Fin 8) ℚ := Matrix.of fun r i => if r = F i then 1 else 0
  let P : Matrix (Fin 104) (Fin 8) ℚ := M * E
  have hP : ∀ p i, P p i = M p (F i) := by
    intro p i
    simp [P, E, Matrix.mul_apply]
  have hle : LinearMap.range P.mulVecLin ≤ LinearMap.range M.mulVecLin := range_mul_le M E
  have hPr : 8 ≤ P.rank := by
    have h1 : (P.submatrix F id).rank ≤ P.rank := Matrix.rank_submatrix_le P F id
    have h2 : P.submatrix F id = 1 := by
      ext i j
      simp [Matrix.submatrix_apply, hP, hF, Matrix.one_apply]
    rw [h2, Matrix.rank_one] at h1
    simpa using h1
  have heq : LinearMap.range P.mulVecLin = LinearMap.range M.mulVecLin :=
    Submodule.eq_of_le_of_finrank_le hle (by
      have h1 : Module.finrank ℚ (LinearMap.range P.mulVecLin) = P.rank := rfl
      have h2 : Module.finrank ℚ (LinearMap.range M.mulVecLin) = M.rank := rfl
      omega)
  have hmem : (fun p => M p r) ∈ LinearMap.range P.mulVecLin := by
    rw [heq]
    refine ⟨Pi.single r 1, ?_⟩
    ext p
    simp [Matrix.mulVecLin_apply, Matrix.mulVec, dotProduct, Pi.single_apply]
  obtain ⟨x, hx⟩ := hmem
  have hxp : ∀ p, M p r = ∑ i, M p (F i) * x i := by
    intro p
    have := congrFun hx p
    simp only [Matrix.mulVecLin_apply, Matrix.mulVec, dotProduct, hP] at this
    exact this.symm
  have hxj : ∀ j, x j = M (F j) r := by
    intro j
    rw [hxp (F j)]
    simp [hF]
  rw [hxp p]
  exact Finset.sum_congr rfl fun i _ => by rw [hxj i]

open DecoderWall in
theorem D56_rank8_anyk {T : Type} [Fintype T] (W U : Fin 104 → T → ℚ) (hd : IsDecoder DF.lq W U)
    (hW : (Wm W).rank ≤ 8) (hU : (Wm U).rank ≤ 8) : 56 ≤ mass DF.lq W U := by
  classical
  set M : Matrix (Fin 104) (Fin 104) ℚ := Wm W * (Wm U)ᵀ with hMdef
  have hMe : ∀ p r, M p r = ∑ k, W p k * U r k := by
    intro p r; simp [hMdef, Matrix.mul_apply]
  have hMd : ∀ p, M p p = 1 := fun p => by rw [hMe]; exact hd.diag p
  have hMo : ∀ p q, p ≠ q → DW6.oddb p q = true → M p q = 0 := fun p q hpq ho => by
    rw [hMe]; exact hd.odd p q hpq ((DFR.oddb_iff p q).1 ho)
  have hF : ∀ i j, M (DF.clique8 i) (DF.clique8 j) = if i = j then 1 else 0 := by
    intro i j
    by_cases hij : i = j
    · subst hij; simp [hMd]
    · rw [if_neg hij, hMe]
      exact hd.odd _ _ (fun e => hij (DF.clique8_inj e)) (DF.clique8_odd i j hij)
  have hM8 : 8 ≤ M.rank := by
    have h1 := Matrix.rank_submatrix_le M DF.clique8 DF.clique8
    have h2 : M.submatrix DF.clique8 DF.clique8 = 1 := by
      ext i j; simp [Matrix.submatrix_apply, hF, Matrix.one_apply]
    rw [h2, Matrix.rank_one] at h1
    simpa using h1
  have hMle : M.rank ≤ 8 := (Matrix.rank_mul_le_left _ _).trans hW
  have hfac := frame_factor M hMle DF.clique8 hF
  -- the 8-row decoder with the same M
  let W8 : Fin 104 → Fin 8 → ℚ := fun p i => M p (DF.clique8 i)
  let U8 : Fin 104 → Fin 8 → ℚ := fun r i => M (DF.clique8 i) r
  have hMx : ∀ p r, DW6.Mx W8 U8 p r = M p r := fun p r => (hfac p r).symm
  have hyp : DW6.Hyp W8 U8 :=
    { card := by simp
      diag := fun p => by rw [hMx]; exact hMd p
      odd := fun p q hpq ho => by rw [hMx]; exact hMo p q hpq ho }
  obtain ⟨lam, hl, hg⟩ := DW6.rigid_gram hyp
  have hg' : ∀ p q, M p q = lam p / lam q * (DW4.g p.val q.val : ℚ) / 2 := fun p q => by
    rw [← hMx]; exact hg p q
  -- transposed side
  set M' : Matrix (Fin 104) (Fin 104) ℚ := Wm U * (Wm W)ᵀ with hM'def
  have hM'T : M' = Mᵀ := by
    rw [hM'def, hMdef, Matrix.transpose_mul, Matrix.transpose_transpose]
  have hM'8 : 8 ≤ M'.rank := by rw [hM'T, Matrix.rank_transpose]; exact hM8
  have hM'le : M'.rank ≤ 8 := by rw [hM'T, Matrix.rank_transpose]; exact hMle
  -- live rows
  let live : T → Prop := fun t => (∃ p, W p t ≠ 0) ∧ (∃ p, U p t ≠ 0)
  let T' := {t : T // live t}
  let W' : Fin 104 → T' → ℚ := fun p t => W p t.1
  let U' : Fin 104 → T' → ℚ := fun p t => U p t.1
  have hdead : ∀ t, ¬ live t → ∀ p r, W p t * U r t = 0 := by
    intro t ht p r
    by_contra hne
    apply ht
    exact ⟨⟨p, left_ne_zero_of_mul hne⟩, ⟨r, right_ne_zero_of_mul hne⟩⟩
  have hsum : ∀ f : T → ℚ, (∀ t, ¬ live t → f t = 0) → ∑ t : T', f t.1 = ∑ t, f t := by
    intro f hf
    rw [← Finset.sum_subtype (Finset.univ.filter live) (by simp) f]
    exact Finset.sum_filter_of_ne (fun t _ hne => by by_contra h; exact hne (hf t h))
  have hsumM : ∀ p r, ∑ t : T', W' p t * U' r t = ∑ t, W p t * U r t := fun p r =>
    hsum (fun t => W p t * U r t) (fun t ht => hdead t ht p r)
  have hd' : IsDecoder DF.lq W' U' :=
    { diag := fun p => by rw [hsumM]; exact hd.diag p
      odd := fun p q hpq ho => by rw [hsumM]; exact hd.odd p q hpq ho }
  have hr' : DF.RigidCols W' U' := by
    intro t
    constructor
    · intro S hS
      refine blk_rank_le M lam hl hg' S (rank_sub_le_seven M hMle S (fun p => W p t.1) ?_ ?_ ?_)
      · have := col_mem (Wm W) (Wm U) hW (by simpa [hMdef] using hM8) t.1
        simpa [hMdef] using this
      · intro h
        obtain ⟨p, hp⟩ := t.2.1
        exact hp (congrFun h p)
      · intro p hp
        by_contra hne
        exact hS p hp (by simp [DecoderWall.dep, W', hne])
    · intro S hS
      have key := rank_sub_le_seven M' hM'le S (fun p => U p t.1) (by
          have := col_mem (Wm U) (Wm W) hU (by simpa [hM'def] using hM'8) t.1
          simpa [hM'def] using this) (by
          intro h
          obtain ⟨p, hp⟩ := t.2.2
          exact hp (congrFun h p)) (by
          intro p hp
          by_contra hne
          exact hS p hp (by simp [DecoderWall.gat, U', hne]))
      refine blk_rank_le M lam hl hg' S ?_
      have e : M.submatrix ((↑) : S → Fin 104) ((↑) : S → Fin 104) =
          (M'.submatrix ((↑) : S → Fin 104) ((↑) : S → Fin 104))ᵀ := by
        rw [hM'T]; ext p r; simp
      rw [e, Matrix.rank_transpose]
      exact key
  have h56 := DF.D56_decoder W' U' hd' hr'
  refine h56.trans ?_
  unfold DecoderWall.mass
  have hrp : ∀ t : T', DecoderWall.rowPrice DF.lq W' U' t = DecoderWall.rowPrice DF.lq W U t.1 := fun t => rfl
  simp only [hrp]
  rw [← Finset.sum_subtype (Finset.univ.filter live) (by simp)
    (fun t => DecoderWall.rowPrice DF.lq W U t)]
  exact Finset.sum_le_sum_of_subset (Finset.filter_subset _ _)

end DW7

#print axioms DW7.D56_rank8_anyk
