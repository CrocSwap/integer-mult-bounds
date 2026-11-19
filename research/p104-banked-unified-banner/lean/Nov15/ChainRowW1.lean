/-
ChainRowW1 .  THEOREM W case (a): beta = 0 SPLITS .  Kernel only.
`ZData K q`: chain data with ARBITRARY relay coefficients (zero allowed).  carried v_{k+1} = β_{k+1} v_k + f_{k+1}
(a zero relay RESTARTS the carried vector).  A chain with z zero relays (inner indices) is a concatenation of ≤ z+1 pure chains.
 * `ZData.exists_split`   : block m D = block of a ChainLayout over T, card T ≤ zc + 1, descent mass equal.
 * `zlayout_mass_ge_56`   : layout of zero-relay chains, total (zeros + 1) ≤ 8, realising the live pattern ⇒ descent mass ≥ 56.
 * `zlayout_mass_ge_56_rank8` : any number of pieces, stacked ranks of the induced rows ≤ 8.
-/
import Nov15.ChainRowB

open Matrix Module

namespace ChainRow
open DecoderWall

variable {κ ι : Type*} [Fintype κ] [Fintype ι]

/-- chain data with arbitrary relay coefficients. -/
structure ZData (K : Type*) [Field K] (q : ι → κ → ZMod 2) where
  ch : ℕ → Submodule (ZMod 2) (κ → ZMod 2)
  desc : ∀ j, ch (j + 1) ≤ ch j
  fresh : ℕ → ι → K
  fresh_supp : ∀ j p, fresh j p ≠ 0 → q p ∈ ch j
  gath : ℕ → ι → K
  gath_supp : ∀ k s, gath k s ≠ 0 → ∀ y ∈ ch (k + 1), dot (q s) y = 0
  beta : ℕ → K

namespace ZData
variable {K : Type*} [Field K] {q : ι → κ → ZMod 2} (D : ZData K q)

def carried : ℕ → ι → K
  | 0 => D.fresh 0
  | k + 1 => fun p => D.beta (k + 1) * carried k p + D.fresh (k + 1) p

def block (m : ℕ) (p s : ι) : K := ∑ k ∈ Finset.range m, D.carried k p * D.gath k s

noncomputable def descentMass (m : ℕ) : ℕ :=
  ∑ j ∈ Finset.range m, (finrank (ZMod 2) (D.ch j) - finrank (ZMod 2) (D.ch (j + 1)))

open scoped Classical in
/-- number of zero relays at inner positions 1..m-1. -/
noncomputable def zc (m : ℕ) : ℕ := ∑ i ∈ Finset.range m, if i ≠ 0 ∧ D.beta i = 0 then 1 else 0

/-- shift the chain by r descents. -/
def shift (r : ℕ) : ZData K q where
  ch := fun j => D.ch (r + j)
  desc := fun j => D.desc (r + j)
  fresh := fun j => D.fresh (r + j)
  fresh_supp := fun j => D.fresh_supp (r + j)
  gath := fun j => D.gath (r + j)
  gath_supp := fun k => D.gath_supp (r + k)
  beta := fun j => D.beta (r + j)

/-- with no inner zero relay, the data is a pure relay chain. -/
noncomputable def toRelay (m : ℕ) (_hz : ∀ i, 0 < i → i < m → D.beta i ≠ 0) : RelayChain K q m :=
  open scoped Classical in
  { ch := D.ch, desc := D.desc, fresh := D.fresh, fresh_supp := D.fresh_supp,
    gath := D.gath, gath_supp := D.gath_supp,
    beta := fun i => if D.beta i = 0 then 1 else D.beta i
    beta_ne := fun i => by
      by_cases h : D.beta i = 0
      · simp [h]
      · simp [h] }

theorem toRelay_carried (m : ℕ) (hz : ∀ i, 0 < i → i < m → D.beta i ≠ 0) :
    ∀ k, k < m → ∀ p, (D.toRelay m hz).carried k p = D.carried k p := by
  intro k
  induction k with
  | zero => intro _ p; rfl
  | succ k ih =>
    intro hk p
    have hb := hz (k + 1) (by omega) hk
    have e : (D.toRelay m hz).carried (k + 1) p =
        (open scoped Classical in if D.beta (k + 1) = 0 then 1 else D.beta (k + 1)) *
          (D.toRelay m hz).carried k p + D.fresh (k + 1) p := rfl
    have e2 : D.carried (k + 1) p = D.beta (k + 1) * D.carried k p + D.fresh (k + 1) p := rfl
    rw [e, e2, ih (by omega) p]
    simp [hb]

theorem toRelay_block (m : ℕ) (hz : ∀ i, 0 < i → i < m → D.beta i ≠ 0) (p s : ι) :
    (D.toRelay m hz).block p s = D.block m p s := by
  unfold RelayChain.block block
  refine Finset.sum_congr rfl fun k hk => ?_
  rw [D.toRelay_carried m hz k (Finset.mem_range.1 hk) p]; rfl

theorem toRelay_mass (m : ℕ) (hz : ∀ i, 0 < i → i < m → D.beta i ≠ 0) :
    (D.toRelay m hz).descentMass = D.descentMass m := rfl

/-- a zero relay at r ≥ 1 restarts the carried vector. -/
theorem shift_carried {r : ℕ} (hr : 0 < r) (h0 : D.beta r = 0) :
    ∀ k p, (D.shift r).carried k p = D.carried (r + k) p := by
  intro k
  induction k with
  | zero =>
    intro p
    obtain ⟨r', rfl⟩ : ∃ r', r = r' + 1 := ⟨r - 1, by omega⟩
    show D.fresh (r' + 1 + 0) p = D.carried (r' + 1 + 0) p
    show D.fresh (r' + 1) p = D.carried (r' + 1) p
    simp only [carried, h0, zero_mul, zero_add]
  | succ k ih =>
    intro p
    show D.beta (r + (k + 1)) * (D.shift r).carried k p + D.fresh (r + (k + 1)) p =
      D.beta (r + k + 1) * D.carried (r + k) p + D.fresh (r + k + 1) p
    rw [ih p]; rfl

theorem block_split {r : ℕ} (hr : 0 < r) (h0 : D.beta r = 0) (n : ℕ) (p s : ι) :
    D.block (r + n) p s = D.block r p s + (D.shift r).block n p s := by
  unfold block
  rw [Finset.sum_range_add]
  congr 1
  refine Finset.sum_congr rfl fun k _ => ?_
  rw [D.shift_carried hr h0 k p]; rfl

theorem mass_split (r n : ℕ) : D.descentMass (r + n) = D.descentMass r + (D.shift r).descentMass n := by
  unfold descentMass
  rw [Finset.sum_range_add]
  rfl

theorem zc_split {r : ℕ} (hr : 0 < r) (h0 : D.beta r = 0) (n : ℕ) (hn : 0 < n) :
    D.zc (r + n) = D.zc r + (D.shift r).zc n + 1 := by
  classical
  unfold zc
  rw [Finset.sum_range_add]
  obtain ⟨n', rfl⟩ : ∃ n', n = n' + 1 := ⟨n - 1, by omega⟩
  rw [Finset.sum_range_succ', Finset.sum_range_succ' _ n']
  have h1 : (if r + 0 ≠ 0 ∧ D.beta (r + 0) = 0 then 1 else 0) = 1 := by
    rw [if_pos]; exact ⟨by omega, by simpa using h0⟩
  have h2 : (if (0:ℕ) ≠ 0 ∧ (D.shift r).beta 0 = 0 then 1 else 0) = 0 := by simp
  rw [h1, h2]
  have h3 : ∑ x ∈ Finset.range n', (if r + (x + 1) ≠ 0 ∧ D.beta (r + (x + 1)) = 0 then 1 else 0)
      = ∑ x ∈ Finset.range n', (if x + 1 ≠ 0 ∧ (D.shift r).beta (x + 1) = 0 then 1 else 0) := by
    refine Finset.sum_congr rfl fun x _ => ?_
    have : r + (x + 1) ≠ 0 := by omega
    simp [shift, this]
  rw [h3]; ring

/-- **SPLIT.** A chain with z zero relays is a layout of ≤ z+1 pure relay chains with the same block
and the same descent mass. -/
theorem exists_split : ∀ (m : ℕ) (D : ZData K q),
    ∃ (T : Type) (_ : Fintype T) (L : ChainLayout K q T),
      Fintype.card T ≤ D.zc m + 1 ∧ (∀ p s, L.block p s = D.block m p s) ∧
        L.descentMass = D.descentMass m := by
  intro m
  induction m using Nat.strong_induction_on with
  | _ m ih =>
    intro D
    by_cases h : ∃ r, 0 < r ∧ r < m ∧ D.beta r = 0
    · obtain ⟨r, hr0, hrm, hb⟩ := h
      obtain ⟨n, rfl⟩ : ∃ n, m = r + n := ⟨m - r, by omega⟩
      obtain ⟨T1, i1, L1, c1, b1, m1⟩ := ih r (by omega) D
      obtain ⟨T2, i2, L2, c2, b2, m2⟩ := ih n (by omega) (D.shift r)
      refine ⟨T1 ⊕ T2, inferInstance,
        { len := Sum.elim L1.len L2.len
          chain := fun c => Sum.rec (motive := fun c => RelayChain K q (Sum.elim L1.len L2.len c))
            (fun c => L1.chain c) (fun c => L2.chain c) c }, ?_, ?_, ?_⟩
      · rw [Fintype.card_sum, D.zc_split hr0 hb n (by omega)]; omega
      · intro p s
        rw [D.block_split hr0 hb n p s, ← b1 p s, ← b2 p s]
        simp only [ChainLayout.block, Fintype.sum_sum_type]
        rfl
      · rw [D.mass_split r n, ← m1, ← m2]
        simp only [ChainLayout.descentMass, Fintype.sum_sum_type]
        rfl
    · have hz : ∀ i, 0 < i → i < m → D.beta i ≠ 0 := fun i h1 h2 h3 => h ⟨i, h1, h2, h3⟩
      refine ⟨Unit, inferInstance, { len := fun _ => m, chain := fun _ => D.toRelay m hz }, ?_, ?_, ?_⟩
      · simp
      · intro p s
        simp only [ChainLayout.block, Finset.univ_unique, Finset.sum_singleton]
        exact D.toRelay_block m hz p s
      · simp only [ChainLayout.descentMass, Finset.univ_unique, Finset.sum_singleton]
        exact D.toRelay_mass m hz

end ZData

/-- A layout of zero-relay chains indexed by `T` (one chain data and length per index). -/
structure ZLayout (K : Type*) [Field K] (q : ι → κ → ZMod 2) (T : Type*) where
  len : T → ℕ
  dat : T → ZData K q

namespace ZLayout
variable {K : Type*} [Field K] {q : ι → κ → ZMod 2} {T : Type} [Fintype T] (Z : ZLayout K q T)

def block (p s : ι) : K := ∑ c, (Z.dat c).block (Z.len c) p s
noncomputable def descentMass : ℕ := ∑ c, (Z.dat c).descentMass (Z.len c)
noncomputable def pieces : ℕ := ∑ c, ((Z.dat c).zc (Z.len c) + 1)

structure Realises : Prop where
  diag : ∀ t, Z.block t t = 1
  odd : ∀ t s, t ≠ s → dot (q t) (q s) = 1 → Z.block t s = 0

/-- **Flattening.**  The zero-relay layout is, block for block, a pure `ChainLayout` with `pieces` chains
and the same descent mass. -/
theorem exists_flat : ∃ (T' : Type) (_ : Fintype T') (L : ChainLayout K q T'),
    Fintype.card T' ≤ Z.pieces ∧ (∀ p s, L.block p s = Z.block p s) ∧ L.descentMass = Z.descentMass := by
  classical
  choose T' hT' L' hc hb hm using fun c => ZData.exists_split (K := K) (q := q) (Z.len c) (Z.dat c)
  letI : ∀ c, Fintype (T' c) := hT'
  refine ⟨(c : T) × T' c, inferInstance,
    { len := fun x : (c : T) × T' c => (L' x.1).len x.2
      chain := fun x : (c : T) × T' c => (L' x.1).chain x.2 }, ?_, ?_, ?_⟩
  · rw [Fintype.card_sigma]
    exact Finset.sum_le_sum fun c _ => hc c
  · intro p s
    simp only [ChainLayout.block, Fintype.sum_sigma]
    refine Finset.sum_congr rfl fun c _ => ?_
    have := hb c p s
    simpa [ChainLayout.block] using this
  · simp only [ChainLayout.descentMass, Fintype.sum_sigma]
    refine Finset.sum_congr rfl fun c _ => ?_
    have := hm c
    simpa [ChainLayout.descentMass] using this

end ZLayout

variable {T : Type} [Fintype T]

/-- **THEOREM W (a): β = 0 splits.**  Zero-relay chains realising the live pattern with at most 8 pure pieces
(chains + zero relays) have descent mass ≥ 56. -/
theorem zlayout_mass_ge_56 (Z : ZLayout ℚ DF.lq T) (hR : Z.Realises) (h8 : Z.pieces ≤ 8) :
    56 ≤ Z.descentMass := by
  obtain ⟨T', i, L, hc, hb, hm⟩ := Z.exists_flat
  have hR' : L.Realises :=
    { diag := fun t => by rw [hb]; exact hR.diag t
      odd := fun t s h1 h2 => by rw [hb]; exact hR.odd t s h1 h2 }
  rw [← hm]
  exact chain_mass_ge_56 L hR' (hc.trans h8)

/-- same, any number of pieces whose stacked deposit/gather factor ranks are ≤ 8. -/
theorem zlayout_mass_ge_56_rank8 (Z : ZLayout ℚ DF.lq T) (hR : Z.Realises) :
    ∃ (T' : Type) (_ : Fintype T') (L : ChainLayout ℚ DF.lq T'), L.Realises ∧
      L.descentMass = Z.descentMass ∧ Fintype.card T' ≤ Z.pieces ∧
      ((DW7.Wm L.W).rank ≤ 8 → (DW7.Wm L.U).rank ≤ 8 → 56 ≤ Z.descentMass) := by
  obtain ⟨T', i, L, hc, hb, hm⟩ := Z.exists_flat
  have hR' : L.Realises :=
    { diag := fun t => by rw [hb]; exact hR.diag t
      odd := fun t s h1 h2 => by rw [hb]; exact hR.odd t s h1 h2 }
  exact ⟨T', i, L, hR', hm, hc, fun hW hU => hm ▸ chain_mass_ge_56_rank8 L hR' hW hU⟩

end ChainRow

#print axioms ChainRow.ZData.exists_split
#print axioms ChainRow.zlayout_mass_ge_56
#print axioms ChainRow.zlayout_mass_ge_56_rank8
