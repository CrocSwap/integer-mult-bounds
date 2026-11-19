/-
ChainRowA .  CE1-ALT CHAIN-ROW LEMMA , kernel only, generic.
Setting: labels `q : ι → (κ → 𝔽₂)`; charts are `Submodule (ZMod 2) (κ → ZMod 2)` (for κ = Fin 9 this is exactly
the chart type `Submodule (ZMod 2) BankWireC.V` of `BankFit.BankedGraph`).
A PURE RELAY CHAIN of length m: charts ch 0 ⊇ ch 1 ⊇ … ⊇ ch m (descent j: a_j = ch j → b_j = ch (j+1) = a_{j+1};
any drops, dim-9 root allowed), fresh deposit f_j supported on {p : q p ∈ ch j}, direct gather g_k supported on
{s : q s ⊥ ch (k+1)}, relay coefficient β_k ≠ 0 (in-degree ≤ 1, no branching):
   carried v_0 = f_0,  v_{k+1} = β_{k+1} v_k + f_{k+1};   block[p,s] = Σ_{k<m} v_k[p] g_k[s].
PROVED:
 * `carried_eq`      : v_k = Σ_{j≤k} (P k / P j) f_j   (P = cumulative product of β)
 * `chain_row`       : on every odd pair (dot (q p) (q s) = 1): block[p,s] = φ p * c s   (rank-1)
 * `phi_supp`, `cv_supp` : supp φ ⊆ {q ∈ ch 0}, supp c ⊆ {q ⊥ ch m}
 * `pairing_rank_le_drop` : rank Q[D,S] ≤ dim A − dim B when q(D) ⊆ A, q(S) ⊥ B, B ≤ A
 * `drop_le_descentMass` : dim ch 0 − dim ch m ≤ Σ_{j<m} (dim ch j − dim ch (j+1))
 * `ChainLayout.isDecoder` : chains realising the pattern ⇒ IsDecoder with one row per chain
 * `ChainLayout.mass_le`   : mass of that decoder ≤ descent mass
-/
import Nov15.DecoderWall

open Matrix Module

namespace ChainRow
open DecoderWall

variable {κ ι : Type*} [Fintype κ] [Fintype ι]

/-- A pure relay chain of `m` descents over field `K` (indices ≥ m are ignored by every sum). -/
structure RelayChain (K : Type*) [Field K] (q : ι → κ → ZMod 2) (m : ℕ) where
  ch : ℕ → Submodule (ZMod 2) (κ → ZMod 2)
  desc : ∀ j, ch (j + 1) ≤ ch j
  fresh : ℕ → ι → K
  fresh_supp : ∀ j p, fresh j p ≠ 0 → q p ∈ ch j
  gath : ℕ → ι → K
  gath_supp : ∀ k s, gath k s ≠ 0 → ∀ y ∈ ch (k + 1), dot (q s) y = 0
  beta : ℕ → K
  beta_ne : ∀ k, beta k ≠ 0

namespace RelayChain
variable {K : Type*} [Field K] {q : ι → κ → ZMod 2} {m : ℕ} (C : RelayChain K q m)

/-- carried vector after descent k (relay: v_{k+1} = β_{k+1} v_k + f_{k+1}). -/
def carried : ℕ → ι → K
  | 0 => C.fresh 0
  | k + 1 => fun p => C.beta (k + 1) * carried k p + C.fresh (k + 1) p

/-- the chain's block on the odd-pair pattern. -/
def block (p s : ι) : K := ∑ k ∈ Finset.range m, C.carried k p * C.gath k s

/-- cumulative relay product P k = β_0 ⋯ β_k. -/
def P (k : ℕ) : K := ∏ i ∈ Finset.range (k + 1), C.beta i

theorem P_ne (k : ℕ) : C.P k ≠ 0 :=
  Finset.prod_ne_zero_iff.2 fun i _ => C.beta_ne i

/-- the row's deposit factor φ and gather factor c. -/
def phi (p : ι) : K := ∑ j ∈ Finset.range m, (C.P j)⁻¹ * C.fresh j p
def cv (s : ι) : K := ∑ k ∈ Finset.range m, C.P k * C.gath k s

theorem carried_eq (k : ℕ) (p : ι) :
    C.carried k p = ∑ j ∈ Finset.range (k + 1), C.P k * (C.P j)⁻¹ * C.fresh j p := by
  induction k with
  | zero => simp [carried, C.P_ne 0]
  | succ k ih =>
    simp only [carried]
    rw [ih, Finset.sum_range_succ _ (k + 1), Finset.mul_sum]
    have hP : C.P (k + 1) = C.P k * C.beta (k + 1) := by
      simp only [P]; rw [Finset.prod_range_succ _ (k + 1)]
    rw [mul_inv_cancel₀ (C.P_ne (k + 1)), one_mul]
    congr 1
    refine Finset.sum_congr rfl fun j _ => ?_
    rw [hP]; ring

theorem antitone_ch : Antitone C.ch := antitone_nat_of_succ_le C.desc

/-- terms with j > k vanish on odd pairs. -/
theorem cross_zero {p s : ι} (hps : dot (q p) (q s) = 1) {j k : ℕ} (hjk : k < j) :
    C.fresh j p * C.gath k s = 0 := by
  by_contra h
  have hf : C.fresh j p ≠ 0 := left_ne_zero_of_mul h
  have hg : C.gath k s ≠ 0 := right_ne_zero_of_mul h
  have hm : q p ∈ C.ch (k + 1) := C.antitone_ch hjk (C.fresh_supp j p hf)
  have h0 := C.gath_supp k s hg (q p) hm
  have : dot (q s) (q p) = dot (q p) (q s) := dotProduct_comm _ _
  rw [this, hps] at h0
  exact one_ne_zero h0

/-- **CHAIN-ROW LEMMA.** On every odd pair the chain's block is the rank-1 product φ p · c s. -/
theorem chain_row {p s : ι} (hps : dot (q p) (q s) = 1) : C.block p s = C.phi p * C.cv s := by
  unfold block phi cv
  rw [Finset.sum_mul_sum]
  rw [Finset.sum_comm]
  refine Finset.sum_congr rfl fun k hk => ?_
  rw [carried_eq, Finset.sum_mul]
  have hsub : Finset.range (k + 1) ⊆ Finset.range m := by
    intro j hj; simp only [Finset.mem_range] at *; omega
  rw [Finset.sum_subset hsub]
  · refine Finset.sum_congr rfl fun j _ => by ring
  · intro j _ hj
    simp only [Finset.mem_range, not_lt] at hj
    have := C.cross_zero hps (show k < j by omega)
    calc C.P k * (C.P j)⁻¹ * C.fresh j p * C.gath k s
        = C.P k * (C.P j)⁻¹ * (C.fresh j p * C.gath k s) := by ring
      _ = 0 := by rw [this, mul_zero]

theorem phi_supp (p : ι) (h : C.phi p ≠ 0) : q p ∈ C.ch 0 := by
  obtain ⟨j, -, hj⟩ := Finset.exists_ne_zero_of_sum_ne_zero h
  have hf : C.fresh j p ≠ 0 := right_ne_zero_of_mul hj
  exact C.antitone_ch (Nat.zero_le j) (C.fresh_supp j p hf)

theorem cv_supp (s : ι) (h : C.cv s ≠ 0) : ∀ y ∈ C.ch m, dot (q s) y = 0 := by
  obtain ⟨k, hk, hk'⟩ := Finset.exists_ne_zero_of_sum_ne_zero h
  have hg : C.gath k s ≠ 0 := right_ne_zero_of_mul hk'
  intro y hy
  simp only [Finset.mem_range] at hk
  exact C.gath_supp k s hg y (C.antitone_ch (show k + 1 ≤ m by omega) hy)

/-- the chain's paid descent mass Σ_j (dim a_j − dim b_j). -/
noncomputable def descentMass : ℕ :=
  ∑ j ∈ Finset.range m, (finrank (ZMod 2) (C.ch j) - finrank (ZMod 2) (C.ch (j + 1)))

theorem drop_le_descentMass_aux (n : ℕ) :
    finrank (ZMod 2) (C.ch 0) - finrank (ZMod 2) (C.ch n) ≤
      ∑ j ∈ Finset.range n, (finrank (ZMod 2) (C.ch j) - finrank (ZMod 2) (C.ch (j + 1))) := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [Finset.sum_range_succ]
    have h1 := Submodule.finrank_mono (C.desc n)
    have h2 := Submodule.finrank_mono (C.antitone_ch (Nat.zero_le n))
    omega

theorem drop_le_descentMass :
    finrank (ZMod 2) (C.ch 0) - finrank (ZMod 2) (C.ch m) ≤ C.descentMass :=
  C.drop_le_descentMass_aux m

end RelayChain

/-- **Pairing rank ≤ drop.**  If the deposit labels lie in chart `A` and the gather labels are ⊥ chart `B ≤ A`,
the 𝔽₂ pairing rank of `Q[D,S]` is at most `dim A − dim B`. -/
theorem pairing_rank_le_drop (q : ι → κ → ZMod 2) (D S : Finset ι)
    (A B : Submodule (ZMod 2) (κ → ZMod 2)) (hBA : B ≤ A)
    (hD : ∀ t ∈ D, q t ∈ A) (hS : ∀ s ∈ S, ∀ y ∈ B, dot (q s) y = 0) :
    ((Qm q).submatrix ((↑) : D → ι) ((↑) : S → ι)).rank ≤
      finrank (ZMod 2) A - finrank (ZMod 2) B := by
  classical
  let g : (κ → ZMod 2) →ₗ[ZMod 2] (S → ZMod 2) :=
    { toFun := fun x s => dot x (q s)
      map_add' := fun x y => by ext s; simp [dot, add_dotProduct]
      map_smul' := fun c x => by ext s; simp [dot, smul_dotProduct] }
  let h := g.comp A.subtype
  have hker : B.comap A.subtype ≤ LinearMap.ker h := by
    intro x hx
    simp only [Submodule.mem_comap, Submodule.subtype_apply] at hx
    simp only [LinearMap.mem_ker]
    ext s
    have := hS s s.2 x hx
    simp only [h, g, LinearMap.comp_apply, LinearMap.coe_mk, AddHom.coe_mk, Submodule.subtype_apply,
      Pi.zero_apply]
    rw [show dot (↑x) (q ↑s) = dot (q ↑s) ↑x from dotProduct_comm _ _, this]
  have hBc : finrank (ZMod 2) (B.comap A.subtype) = finrank (ZMod 2) B :=
    (Submodule.comapSubtypeEquivOfLe hBA).finrank_eq
  have hrn := LinearMap.finrank_range_add_finrank_ker h
  have h2 := Submodule.finrank_mono hker
  have hle : finrank (ZMod 2) (LinearMap.range h) ≤ finrank (ZMod 2) A - finrank (ZMod 2) B := by omega
  rw [Matrix.rank_eq_finrank_span_row]
  refine le_trans (Submodule.finrank_mono ?_) hle
  rw [Submodule.span_le]
  rintro _ ⟨t, rfl⟩
  refine ⟨⟨q t, hD t t.2⟩, ?_⟩
  ext s
  simp [h, g, Qm]
  try rfl

/-- A layout of pure relay chains indexed by `T` (one chain per index). -/
structure ChainLayout (K : Type*) [Field K] (q : ι → κ → ZMod 2) (T : Type*) where
  len : T → ℕ
  chain : ∀ c, RelayChain K q (len c)

namespace ChainLayout
variable {K : Type*} [Field K] {q : ι → κ → ZMod 2} {T : Type*} [Fintype T] (L : ChainLayout K q T)

/-- total block of the layout. -/
def block (p s : ι) : K := ∑ c, (L.chain c).block p s

/-- the layout realises the decoder pattern: block diagonal 1, block 0 on odd off-diagonal pairs. -/
structure Realises : Prop where
  diag : ∀ t, L.block t t = 1
  odd : ∀ t s, t ≠ s → dot (q t) (q s) = 1 → L.block t s = 0

/-- the induced decoder rows: one rank-1 row per chain. -/
def W (t : ι) (c : T) : K := (L.chain c).phi t
def U (s : ι) (c : T) : K := (L.chain c).cv s

noncomputable def descentMass : ℕ := ∑ c, (L.chain c).descentMass

theorem block_eq {p s : ι} (hps : dot (q p) (q s) = 1) : L.block p s = ∑ c, L.W p c * L.U s c :=
  Finset.sum_congr rfl fun c _ => (L.chain c).chain_row hps

/-- **Chains realising the pattern ARE a decoder with one row per chain.** -/
theorem isDecoder (hodd : ∀ t, dot (q t) (q t) = 1) (hR : L.Realises) : IsDecoder q L.W L.U where
  diag := fun t => by rw [← L.block_eq (hodd t)]; exact hR.diag t
  odd := fun t s hts h => by rw [← L.block_eq h]; exact hR.odd t s hts h

theorem rowPrice_le (c : T) :
    rowPrice q L.W L.U c ≤ (L.chain c).descentMass := by
  classical
  refine le_trans ?_ (L.chain c).drop_le_descentMass
  unfold rowPrice
  refine pairing_rank_le_drop q _ _ ((L.chain c).ch 0) ((L.chain c).ch (L.len c))
    ((L.chain c).antitone_ch (Nat.zero_le _)) ?_ ?_
  · intro t ht
    simp only [dep, Finset.mem_filter, Finset.mem_univ, true_and] at ht
    convert (L.chain c).phi_supp t ht
  · intro s hs
    simp only [gat, Finset.mem_filter, Finset.mem_univ, true_and] at hs
    convert (L.chain c).cv_supp s hs

/-- decoder mass ≤ descent mass. -/
theorem mass_le : mass q L.W L.U ≤ L.descentMass :=
  Finset.sum_le_sum fun c _ => L.rowPrice_le c

end ChainLayout
end ChainRow

#print axioms ChainRow.RelayChain.chain_row
#print axioms ChainRow.pairing_rank_le_drop
#print axioms ChainRow.ChainLayout.isDecoder
#print axioms ChainRow.ChainLayout.mass_le
