import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.NumberTheory.Padics.RingHoms

/-!
# DecoderWall (lane LEAN-DEC, Nov 18): the decoder wall, kernel-checked part

Setting (cards/WILD/FABLEWORK/HANDOFF.md, DECMINRANK/RESULT.md, ADICWALL/RESULT.md).
Labels `q : ι → (κ → 𝔽₂)` (odd weight: `q_t·q_t = 1`).  A decoder is a pair `W, U : ι → T → K`
with `M = W Uᵀ`, `M_tt = 1`, `M_ts = 0` on every odd pair (`q_t·q_s = 1`, `t ≠ s`); even cells free.
Row `k` deposits into `D_k = supp W[:,k]` and gathers from `S_k = supp U[:,k]`;
its price is the pairing rank `rank_𝔽₂ Q[D_k,S_k]` (DECMINRANK Lemma 1); mass `C = Σ_k price_k`.

Proved here (kernel only, no sorry, no native_decide, no axioms beyond the Mathlib three):
* `mass_ge_card_of_reduction` : any decoder over a ring `R` with a ring hom `R → 𝔽₂`
  (e.g. 𝔽₂-valued, ℤ, ℤ₍₂₎, ℤ_[2]: every odd-denominator decoder) has `C ≥ n`.  (ADICWALL §0.2, e=0)
* `pairing_rank_add_le` : row-price law, lower half. A chain `f0 ≤ f1` of frames with the deposit labels in
  `f1` and `f0 ⊥ gathered labels` climbs at least the pairing rank.  (DECMINRANK Lemma 1)
* `frame_climb_ge_card` : combining the two: total climb `≥ n` for odd-denominator decoders.
* `orthonormal_card_le` / `gram_one_rank` : pairwise-even odd-weight set is independent, `|P| ≤ h`,
  pairing rank `|P|`.  (HANDOFF "line of attack" step 3)
* `tensor_isDecoder` : decoders tensor (ADICWALL §1, the break of "any label set").
-/

open Matrix

namespace DecoderWall

/-! ## Copied from `DecoderDuality.lean` (verbatim): `import DecoderDuality` pulls all of Mathlib and
exceeds the 3.5 GB runlean guard, so the generic lemmas are repeated here. -/
section Copied
variable {F : Type*} [Field F]

/-- Rank is subadditive. -/
theorem rank_add_le {m n : Type*} [Fintype m] [Fintype n] (A B : Matrix m n F) :
    (A + B).rank ≤ A.rank + B.rank := by
  unfold Matrix.rank
  rw [Matrix.mulVecLin_add]
  calc Module.finrank F (LinearMap.range (A.mulVecLin + B.mulVecLin))
      ≤ Module.finrank F ↥(LinearMap.range A.mulVecLin ⊔ LinearMap.range B.mulVecLin) :=
        Submodule.finrank_mono (LinearMap.range_add_le _ _)
    _ ≤ _ := Submodule.finrank_add_le_finrank_add_finrank _ _

/-- Rank of a finite sum is at most the sum of the ranks. -/
theorem rank_sum_le {m n ι : Type*} [Fintype m] [Fintype n] (s : Finset ι)
    (f : ι → Matrix m n F) : (∑ i ∈ s, f i).rank ≤ ∑ i ∈ s, (f i).rank := by
  classical
  induction s using Finset.induction_on with
  | empty => simp
  | insert a s ha ih =>
    rw [Finset.sum_insert ha, Finset.sum_insert ha]
    exact (rank_add_le _ _).trans (Nat.add_le_add_left ih _)

/-- **Support restriction.** If `p` vanishes off `S` and `q` vanishes off `U`, then
`rank (diag p * B * diag q) ≤ rank (B restricted to S × U)`. -/
theorem rank_diag_mul_mul_diag_le {m n : Type*} [Fintype m] [Fintype n]
    [DecidableEq m] [DecidableEq n] (B : Matrix m n F) (p : m → F) (q : n → F)
    (S : Finset m) (U : Finset n) (hp : ∀ t, p t ≠ 0 → t ∈ S) (hq : ∀ s, q s ≠ 0 → s ∈ U) :
    (diagonal p * B * diagonal q).rank ≤
      (B.submatrix ((↑) : S → m) ((↑) : U → n)).rank := by
  let X : Matrix m S F := fun t i => if (i : m) = t then p t else 0
  let Y : Matrix U n F := fun k s => if (k : n) = s then q s else 0
  have key : diagonal p * B * diagonal q = X * B.submatrix ((↑) : S → m) ((↑) : U → n) * Y := by
    ext t s
    rw [mul_diagonal, diagonal_mul, mul_apply]
    by_cases hs : s ∈ U
    · rw [Fintype.sum_eq_single ⟨s, hs⟩]
      · simp only [Y, if_pos rfl, mul_apply, submatrix_apply]
        by_cases ht : t ∈ S
        · rw [Fintype.sum_eq_single ⟨t, ht⟩]
          · simp only [X, if_pos rfl]
          · intro i hi
            have : (i : m) ≠ t := fun h => hi (Subtype.ext h)
            simp only [X, if_neg this, zero_mul]
        · have hpt : p t = 0 := by
            by_contra h; exact ht (hp t h)
          rw [hpt]
          simp only [zero_mul]
          symm
          rw [Finset.sum_mul]
          apply Finset.sum_eq_zero
          intro i _
          have : (i : m) ≠ t := fun h => ht (h ▸ i.2)
          simp only [X, if_neg this, zero_mul]
      · intro k hk
        have : (k : n) ≠ s := fun h => hk (Subtype.ext h)
        simp only [Y, if_neg this, mul_zero]
    · have hqs : q s = 0 := by
        by_contra h; exact hs (hq s h)
      rw [hqs, mul_zero]
      symm
      apply Finset.sum_eq_zero
      intro k _
      have : (k : n) ≠ s := fun h => hs (h ▸ k.2)
      simp only [Y, if_neg this, mul_zero]
  rw [key]
  exact (rank_mul_le_left _ _).trans (rank_mul_le_right _ _)

end Copied

/-- **Core lemma.** Let `B : ι × ι` over a field `F`, and vectors `p j, q j : ι → F`
(`j : T`). If the Hadamard product `N t s = B t s * ∑ⱼ p j t * q j s` is diagonal with
nonzero diagonal, then for any sets `S j ⊇ supp (p j)`, `U j ⊇ supp (q j)`,
`|ι| ≤ ∑ⱼ rank (B restricted to S j × U j)`. -/
theorem hadamard_diag_rank_sum {F : Type*} [Field F] {ι T : Type*} [Fintype ι]
    [DecidableEq ι] [Fintype T] (B : Matrix ι ι F) (p q : T → ι → F)
    (S U : T → Finset ι)
    (hpS : ∀ j t, p j t ≠ 0 → t ∈ S j) (hqU : ∀ j s, q j s ≠ 0 → s ∈ U j)
    (hoff : ∀ t s, t ≠ s → B t s * ∑ j, p j t * q j s = 0)
    (hdiag : ∀ t, B t t * ∑ j, p j t * q j t ≠ 0) :
    Fintype.card ι ≤ ∑ j, (B.submatrix ((↑) : S j → ι) ((↑) : U j → ι)).rank := by
  classical
  let w : ι → F := fun t => B t t * ∑ j, p j t * q j t
  have hN : ∑ j, diagonal (p j) * B * diagonal (q j) = diagonal w := by
    ext t s
    rw [Matrix.sum_apply]
    simp only [mul_diagonal, diagonal_mul]
    have : ∑ j, p j t * B t s * q j s = B t s * ∑ j, p j t * q j s := by
      rw [Finset.mul_sum]; exact Finset.sum_congr rfl fun j _ => by ring
    rw [this]
    by_cases hts : t = s
    · subst hts; simp [w]
    · rw [diagonal_apply_ne _ hts]; exact hoff t s hts
  have hrank : (diagonal w).rank = Fintype.card ι := by
    rw [rank_diagonal]
    exact Fintype.card_congr (Equiv.subtypeUnivEquiv fun t => hdiag t)
  calc Fintype.card ι = (∑ j, diagonal (p j) * B * diagonal (q j)).rank := by rw [hN, hrank]
    _ ≤ ∑ j, (diagonal (p j) * B * diagonal (q j)).rank := rank_sum_le _ _
    _ ≤ _ := Finset.sum_le_sum fun j _ =>
        rank_diag_mul_mul_diag_le B (p j) (q j) (S j) (U j) (hpS j) (hqU j)


section Defs
variable {κ ι T : Type*} [Fintype κ] [Fintype ι] [Fintype T]

/-- Binary dot product. -/
def dot (x y : κ → ZMod 2) : ZMod 2 := x ⬝ᵥ y

/-- The 0/1 matrix of odd cells (diagonal included when labels have odd weight). -/
def Qm (q : ι → κ → ZMod 2) : Matrix ι ι (ZMod 2) := Matrix.of fun t s => dot (q t) (q s)

/-- Decoder over a ring `R`: diagonal of `W Uᵀ` is 1, zero on odd off-diagonal pairs. -/
structure IsDecoder {R : Type*} [CommRing R] (q : ι → κ → ZMod 2) (W U : ι → T → R) : Prop where
  diag : ∀ t, ∑ k, W t k * U t k = 1
  odd : ∀ t s, t ≠ s → dot (q t) (q s) = 1 → ∑ k, W t k * U s k = 0

open Classical in
/-- Deposit support of row `k`. -/
noncomputable def dep {R : Type*} [Zero R] (W : ι → T → R) (k : T) : Finset ι :=
  Finset.univ.filter fun t => W t k ≠ 0

open Classical in
/-- Gather support of row `k`. -/
noncomputable def gat {R : Type*} [Zero R] (U : ι → T → R) (k : T) : Finset ι :=
  Finset.univ.filter fun s => U s k ≠ 0

/-- Row price: pairing rank of `Q[D_k, S_k]` over `𝔽₂`. -/
noncomputable def rowPrice {R : Type*} [Zero R] (q : ι → κ → ZMod 2) (W U : ι → T → R) (k : T) : ℕ :=
  ((Qm q).submatrix ((↑) : dep W k → ι) ((↑) : gat U k → ι)).rank

/-- Decoder mass `C = Σ_k price_k`. -/
noncomputable def mass {R : Type*} [Zero R] (q : ι → κ → ZMod 2) (W U : ι → T → R) : ℕ :=
  ∑ k, rowPrice q W U k

end Defs

section Floor
variable {κ ι T : Type*} [Fintype κ] [Fintype ι] [DecidableEq ι] [Fintype T]

/-- **C ≥ n for reducible decoders.**  If `red : R →+* 𝔽₂` and `(W,U)` is a decoder over `R`
(labels of odd weight), then `n ≤ C`.  Covers every odd-denominator rational decoder
(`R = ℤ_[2]`, `red = PadicInt.toZMod`), ℤ-decoders, and 𝔽₂-decoders. -/
theorem mass_ge_card_of_reduction {R : Type*} [CommRing R] (red : R →+* ZMod 2)
    (q : ι → κ → ZMod 2) (hodd : ∀ t, dot (q t) (q t) = 1)
    (W U : ι → T → R) (hd : IsDecoder q W U) :
    Fintype.card ι ≤ mass q W U := by
  classical
  have h01 : ∀ x : ZMod 2, x = 0 ∨ x = 1 := by decide
  have h := hadamard_diag_rank_sum (Qm q) (fun k t => red (W t k))
    (fun k s => red (U s k)) (dep W) (gat U)
    (fun k t ht => by
      simp only [dep, Finset.mem_filter, Finset.mem_univ, true_and]
      intro h0; apply ht; rw [h0, map_zero])
    (fun k s hs => by
      simp only [gat, Finset.mem_filter, Finset.mem_univ, true_and]
      intro h0; apply hs; rw [h0, map_zero])
    (fun t s hts => by
      rcases h01 (Qm q t s) with hB | hB
      · rw [hB, zero_mul]
      · have h1 : dot (q t) (q s) = 1 := by simpa [Qm] using hB
        have := hd.odd t s hts h1
        have h2 : ∑ k, red (W t k) * red (U s k) = 0 := by
          rw [← map_zero red, ← this, map_sum]
          exact Finset.sum_congr rfl fun k _ => (map_mul red _ _).symm
        rw [h2, mul_zero])
    (fun t => by
      have h2 : ∑ k, red (W t k) * red (U t k) = 1 := by
        rw [← map_one red, ← hd.diag t, map_sum]
        exact Finset.sum_congr rfl fun k _ => (map_mul red _ _).symm
      rw [h2]
      have : Qm q t t = 1 := by simpa [Qm] using hodd t
      rw [this]; simp)
  exact h

/-- Odd-denominator decoders: entries in `ℤ_[2]` (every rational with odd denominator embeds). -/
theorem mass_ge_card_padic (q : ι → κ → ZMod 2) (hodd : ∀ t, dot (q t) (q t) = 1)
    (W U : ι → T → ℤ_[2]) (hd : IsDecoder q W U) :
    Fintype.card ι ≤ mass q W U :=
  mass_ge_card_of_reduction PadicInt.toZMod q hodd W U hd

end Floor

section PairingRank
variable {κ D S : Type*} [Fintype κ] [Fintype D] [Fintype S]

/-- **Row-price law, lower half (DECMINRANK Lemma 1).**  Frames `f0 ≤ f1` (a climb), deposit labels
`qD t ∈ f1`, and `f0` orthogonal to every gathered label `qS s`.  Then the pairing rank of
`[qD t · qS s]` plus `dim f0` is at most `dim f1`, i.e. `climb ≥ pairing rank`. -/
theorem pairing_rank_add_le (qD : D → κ → ZMod 2) (qS : S → κ → ZMod 2)
    (f0 f1 : Submodule (ZMod 2) (κ → ZMod 2)) (h01 : f0 ≤ f1)
    (hD : ∀ t, qD t ∈ f1) (hS : ∀ v ∈ f0, ∀ s, dot v (qS s) = 0) :
    (Matrix.of fun (t : D) (s : S) => dot (qD t) (qS s)).rank + Module.finrank (ZMod 2) f0
      ≤ Module.finrank (ZMod 2) f1 := by
  classical
  set G : Matrix D S (ZMod 2) := Matrix.of fun t s => dot (qD t) (qS s) with hG
  let Φ : (κ → ZMod 2) →ₗ[ZMod 2] (S → ZMod 2) := (Matrix.of fun (s : S) (i : κ) => qS s i).mulVecLin
  have hΦ : ∀ v s, Φ v s = dot v (qS s) := by
    intro v s
    simp only [Φ, Matrix.mulVecLin_apply, Matrix.mulVec, dot, dotProduct, Matrix.of_apply]
    exact Finset.sum_congr rfl fun i _ => mul_comm _ _
  let Ψ := Φ ∘ₗ f1.subtype
  have hrange : LinearMap.range Gᵀ.mulVecLin ≤ LinearMap.range Ψ := by
    rintro _ ⟨c, rfl⟩
    have hv : (∑ t, c t • qD t) ∈ f1 :=
      Submodule.sum_mem _ fun t _ => Submodule.smul_mem _ _ (hD t)
    refine ⟨⟨_, hv⟩, ?_⟩
    ext s
    simp only [Ψ, LinearMap.comp_apply, Submodule.subtype_apply, hΦ, Matrix.mulVecLin_apply,
      Matrix.mulVec, dotProduct, Matrix.transpose_apply, hG, Matrix.of_apply, dot,
      Finset.sum_apply, Pi.smul_apply, smul_eq_mul, Finset.sum_mul]
    rw [Finset.sum_comm]
    refine Finset.sum_congr rfl fun t _ => ?_
    refine Finset.sum_congr rfl fun i _ => ?_
    ring
  have hker : f0.comap f1.subtype ≤ LinearMap.ker Ψ := by
    intro x hx
    rw [LinearMap.mem_ker]
    ext s
    simp only [Ψ, LinearMap.comp_apply, Submodule.subtype_apply, hΦ, Pi.zero_apply]
    exact hS _ hx s
  have h1 := LinearMap.finrank_range_add_finrank_ker Ψ
  have h2 : Module.finrank (ZMod 2) (f0.comap f1.subtype) = Module.finrank (ZMod 2) f0 :=
    LinearEquiv.finrank_eq (Submodule.comapSubtypeEquivOfLe h01)
  have h3 : Module.finrank (ZMod 2) (f0.comap f1.subtype) ≤ Module.finrank (ZMod 2) (LinearMap.ker Ψ) :=
    Submodule.finrank_mono hker
  have h4 : G.rank = Gᵀ.rank := (Matrix.rank_transpose G).symm
  have h5 : Gᵀ.rank ≤ Module.finrank (ZMod 2) (LinearMap.range Ψ) :=
    Submodule.finrank_mono hrange
  omega

end PairingRank


section Combined
variable {κ ι T : Type*} [Fintype κ] [Fintype ι] [DecidableEq ι] [Fintype T]

/-- **Total climb ≥ n for odd-denominator decoders (frame model).**  Row `k` is a climb `f0 k ≤ f1 k`
of owned frames; deposits `q t ∈ f1 k` for `t ∈ D_k`, gathers `s ∈ S_k` have `f0 k ⊥ q s`.
Then `n + Σ dim f0 ≤ Σ dim f1`, i.e. total climb `≥ n`.  (e = 0 case of the wall; ADICWALL §0.2.) -/
theorem frame_climb_ge_card (q : ι → κ → ZMod 2) (hodd : ∀ t, dot (q t) (q t) = 1)
    (W U : ι → T → ℤ_[2]) (hd : IsDecoder q W U)
    (f0 f1 : T → Submodule (ZMod 2) (κ → ZMod 2)) (h01 : ∀ k, f0 k ≤ f1 k)
    (hD : ∀ k, ∀ t ∈ dep W k, q t ∈ f1 k)
    (hS : ∀ k, ∀ v ∈ f0 k, ∀ s ∈ gat U k, dot v (q s) = 0) :
    Fintype.card ι + ∑ k, Module.finrank (ZMod 2) (f0 k) ≤ ∑ k, Module.finrank (ZMod 2) (f1 k) := by
  have h1 := mass_ge_card_padic q hodd W U hd
  have h2 : ∀ k, rowPrice q W U k + Module.finrank (ZMod 2) (f0 k) ≤ Module.finrank (ZMod 2) (f1 k) := by
    intro k
    exact pairing_rank_add_le (fun t : dep W k => q t) (fun s : gat U k => q s) (f0 k) (f1 k) (h01 k)
      (fun t => hD k t t.2) (fun v hv s => hS k v hv s s.2)
  have h3 : mass q W U + ∑ k, Module.finrank (ZMod 2) (f0 k) ≤ ∑ k, Module.finrank (ZMod 2) (f1 k) := by
    unfold mass
    rw [← Finset.sum_add_distrib]
    exact Finset.sum_le_sum fun k _ => h2 k
  omega

end Combined

section Orthonormal
variable {κ ι : Type*} [Fintype κ] [Fintype ι] [DecidableEq ι]

/-- A pairwise-even family of odd-weight vectors is `𝔽₂`-orthonormal, hence independent. -/
theorem orthonormal_linearIndependent (q : ι → κ → ZMod 2)
    (hg : ∀ t s, dot (q t) (q s) = if t = s then 1 else 0) :
    LinearIndependent (ZMod 2) q := by
  rw [Fintype.linearIndependent_iff]
  intro c hc s
  have h := congrArg (fun v => dot v (q s)) hc
  simp only [dot, sum_dotProduct, smul_dotProduct, zero_dotProduct] at h
  have h2 : ∀ t, c t • (q t ⬝ᵥ q s) = if t = s then c t else 0 := by
    intro t
    have := hg t s
    simp only [dot] at this
    rw [this]; split_ifs <;> simp
  simp only [h2, Finset.sum_ite_eq', Finset.mem_univ, if_true] at h
  exact h

/-- `|P| ≤ h` for pairwise-even odd-weight label sets (HANDOFF step 3). -/
theorem orthonormal_card_le (q : ι → κ → ZMod 2)
    (hg : ∀ t s, dot (q t) (q s) = if t = s then 1 else 0) :
    Fintype.card ι ≤ Fintype.card κ := by
  have := (orthonormal_linearIndependent q hg).fintype_card_le_finrank
  simpa using this

/-- Its pairing matrix is the identity: pairing rank (one unit of climb) per port. -/
theorem gram_one_rank (q : ι → κ → ZMod 2)
    (hg : ∀ t s, dot (q t) (q s) = if t = s then 1 else 0) :
    (Qm q).rank = Fintype.card ι := by
  have : Qm q = 1 := by
    ext t s
    simp [Qm, hg, Matrix.one_apply]
  rw [this, Matrix.rank_one]

end Orthonormal

section Tensor
variable {κ₁ κ₂ ι₁ ι₂ T₁ T₂ : Type*} [Fintype κ₁] [Fintype κ₂] [Fintype ι₁] [Fintype ι₂]
  [Fintype T₁] [Fintype T₂]

/-- Tensor product of label sets `q ⊗ q'`. -/
def tens (q₁ : ι₁ → κ₁ → ZMod 2) (q₂ : ι₂ → κ₂ → ZMod 2) : ι₁ × ι₂ → κ₁ × κ₂ → ZMod 2 :=
  fun p a => q₁ p.1 a.1 * q₂ p.2 a.2

theorem dot_tens (q₁ : ι₁ → κ₁ → ZMod 2) (q₂ : ι₂ → κ₂ → ZMod 2) (p p' : ι₁ × ι₂) :
    dot (tens q₁ q₂ p) (tens q₁ q₂ p') = dot (q₁ p.1) (q₁ p'.1) * dot (q₂ p.2) (q₂ p'.2) := by
  simp only [dot, tens, dotProduct, Fintype.sum_prod_type, Finset.sum_mul_sum]
  refine Finset.sum_congr rfl fun a _ => Finset.sum_congr rfl fun b _ => by ring

/-- **Decoders tensor** (ADICWALL §1): labels `q⊗q'` on `ι₁×ι₂` have the decoder `W⊗W', U⊗U'`
(rows `T₁×T₂`), so the cost ratio multiplies and "C ≥ n/2 on every label set" fails
(P104⊗P104: 0.290 per port, h = 81; the numerical instance is `ADICWALL/tensor.out`). -/
theorem tensor_isDecoder {R : Type*} [CommRing R] [DecidableEq ι₁] [DecidableEq ι₂]
    (q₁ : ι₁ → κ₁ → ZMod 2) (q₂ : ι₂ → κ₂ → ZMod 2)
    (W₁ U₁ : ι₁ → T₁ → R) (W₂ U₂ : ι₂ → T₂ → R)
    (h₁ : IsDecoder q₁ W₁ U₁) (h₂ : IsDecoder q₂ W₂ U₂) :
    IsDecoder (tens q₁ q₂) (fun (p : ι₁ × ι₂) (k : T₁ × T₂) => W₁ p.1 k.1 * W₂ p.2 k.2)
      (fun (p : ι₁ × ι₂) (k : T₁ × T₂) => U₁ p.1 k.1 * U₂ p.2 k.2) := by
  have hsum : ∀ (p p' : ι₁ × ι₂), ∑ k : T₁ × T₂, (W₁ p.1 k.1 * W₂ p.2 k.2) * (U₁ p'.1 k.1 * U₂ p'.2 k.2)
      = (∑ j, W₁ p.1 j * U₁ p'.1 j) * (∑ l, W₂ p.2 l * U₂ p'.2 l) := by
    intro p p'
    rw [Fintype.sum_prod_type, Finset.sum_mul_sum]
    refine Finset.sum_congr rfl fun a _ => Finset.sum_congr rfl fun b _ => by ring
  constructor
  · intro t
    simp only [hsum, h₁.diag, h₂.diag, mul_one]
  · intro t s hts hodd
    simp only [hsum]
    rw [dot_tens] at hodd
    have hodd' : ∀ x y : ZMod 2, x * y = 1 → x = 1 ∧ y = 1 := by decide
    obtain ⟨ha, hb⟩ := hodd' _ _ hodd
    by_cases h1 : t.1 = s.1
    · have h2 : t.2 ≠ s.2 := fun h => hts (Prod.ext h1 h)
      rw [h₂.odd _ _ h2 hb, mul_zero]
    · rw [h₁.odd _ _ h1 ha, zero_mul]

theorem tens_odd (q₁ : ι₁ → κ₁ → ZMod 2) (q₂ : ι₂ → κ₂ → ZMod 2)
    (h₁ : ∀ t, dot (q₁ t) (q₁ t) = 1) (h₂ : ∀ t, dot (q₂ t) (q₂ t) = 1) (p : ι₁ × ι₂) :
    dot (tens q₁ q₂ p) (tens q₁ q₂ p) = 1 := by
  rw [dot_tens, h₁, h₂]; simp

/-- Supports of tensor rows are products. -/
theorem dep_tens {R : Type*} [CommRing R] [NoZeroDivisors R] [DecidableEq ι₁] [DecidableEq ι₂]
    (W₁ : ι₁ → T₁ → R) (W₂ : ι₂ → T₂ → R) (k : T₁ × T₂) :
    dep (fun (p : ι₁ × ι₂) (k : T₁ × T₂) => W₁ p.1 k.1 * W₂ p.2 k.2) k
      = dep W₁ k.1 ×ˢ dep W₂ k.2 := by
  ext p
  simp [dep, mul_ne_zero_iff]

end Tensor

section Hypotheses
variable {ι : Type*} [Fintype ι] [DecidableEq ι]

/-- NAMED HYPOTHESIS (never an axiom): the diagonal stabiliser of `col(G)` is scalars only.
Data: `cards/WILD/BIGBUILD3/aprime/ap3.py` (nullity 1 on G104, computed), `DYADICPORTS rigid.py`.
It is what AP1 §4 uses (with "every rank-8 fit is D₁GD₂") for "no rank-8 doubled decoder". -/
def ColStabScalar (G : Matrix ι ι ℚ) : Prop :=
  ∀ d : ι → ℚ, (∀ j, Matrix.diagonal d *ᵥ (fun t => G t j) ∈
      Submodule.span ℚ (Set.range fun j => fun t => G t j)) → ∀ t s, d t = d s

end Hypotheses

end DecoderWall

#print axioms DecoderWall.mass_ge_card_of_reduction
#print axioms DecoderWall.mass_ge_card_padic
#print axioms DecoderWall.pairing_rank_add_le
#print axioms DecoderWall.frame_climb_ge_card
#print axioms DecoderWall.orthonormal_card_le
#print axioms DecoderWall.gram_one_rank
#print axioms DecoderWall.tensor_isDecoder
#print axioms DecoderWall.dep_tens
