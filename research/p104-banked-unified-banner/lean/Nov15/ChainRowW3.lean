/-
ChainRowW3 .  THEOREM W cases (b) and (c).  Kernel only.
 (b) `BranchNet`: a trunk of `tlen` descents with NO fresh content (f_j = 0, gathers arbitrary) feeding n branch chains
     (branch i starts with relay inflow β_0 · tip, tip = trunk carried vector at its last descent).
     `BranchNet.block_eq`: net block = block of the branches as stand-alone zero-relay chains (trunk adds 0).
     `branch_mass_ge_56`: realising the live pattern with ≤ 8 pure pieces (branches + zero relays) ⇒ descent mass ≥ 56.
 (c) `MergeNet`: n chains merging into a tail with NO gathers (g_k = 0), tail inflow = Σ_i tip_i (tails fresh arbitrary).
     `MergeNet.block_eq`, `merge_mass_ge_56`.
The trunk (resp. tail) drop is simply not charged (descent mass ≥ branches' mass), so there is no double charge.
-/
import Nov15.ChainRowW1

open Matrix Module

namespace ChainRow
open DecoderWall

variable {κ ι : Type*} [Fintype κ] [Fintype ι]

namespace ZData
variable {K : Type*} [Field K] {q : ι → κ → ZMod 2} (D : ZData K q)

/-- carried vector of a chain whose first descent receives a relay inflow `w`. -/
def carriedIn (w : ι → K) : ℕ → ι → K
  | 0 => fun p => D.beta 0 * w p + D.fresh 0 p
  | k + 1 => fun p => D.beta (k + 1) * carriedIn w k p + D.fresh (k + 1) p

def blockIn (m : ℕ) (w : ι → K) (p s : ι) : K :=
  ∑ k ∈ Finset.range m, D.carriedIn w k p * D.gath k s

theorem carriedIn_zero : ∀ k p, D.carriedIn (fun _ => 0) k p = D.carried k p := by
  intro k
  induction k with
  | zero => intro p; simp [carriedIn, carried]
  | succ k ih => intro p; simp only [carriedIn, carried, ih]

theorem blockIn_zero (m : ℕ) (p s : ι) : D.blockIn m (fun _ => 0) p s = D.block m p s := by
  unfold blockIn block
  exact Finset.sum_congr rfl fun k _ => by rw [D.carriedIn_zero]

/-- the carried vector at the last of `t` descents (0 when there is none). -/
def tip : ℕ → ι → K
  | 0 => fun _ => 0
  | t + 1 => D.carried t

/-- fresh-free ⇒ nothing is carried. -/
theorem carried_eq_zero {t : ℕ} (h : ∀ j, j < t → ∀ p, D.fresh j p = 0) :
    ∀ k, k < t → ∀ p, D.carried k p = 0 := by
  intro k
  induction k with
  | zero => intro hk p; simp [carried, h 0 hk p]
  | succ k ih => intro hk p; simp [carried, ih (by omega) p, h (k + 1) hk p]

theorem tip_zero {t : ℕ} (h : ∀ j, j < t → ∀ p, D.fresh j p = 0) : D.tip t = fun _ => 0 := by
  cases t with
  | zero => rfl
  | succ t => funext p; exact D.carried_eq_zero h t (by omega) p

theorem block_zero {t : ℕ} (h : ∀ j, j < t → ∀ p, D.fresh j p = 0) (p s : ι) : D.block t p s = 0 := by
  unfold block
  exact Finset.sum_eq_zero fun k hk => by
    rw [D.carried_eq_zero h k (Finset.mem_range.1 hk) p, zero_mul]

theorem block_gath_zero {t : ℕ} (h : ∀ k, k < t → ∀ s, D.gath k s = 0) (w : ι → K) (p s : ι) :
    D.blockIn t w p s = 0 := by
  unfold blockIn
  exact Finset.sum_eq_zero fun k hk => by
    rw [h k (Finset.mem_range.1 hk) s, mul_zero]

end ZData

/-- (b) a fresh-free trunk branching into chains. -/
structure BranchNet (K : Type*) [Field K] (q : ι → κ → ZMod 2) (T : Type*) where
  trunk : ZData K q
  tlen : ℕ
  free : ∀ j, j < tlen → ∀ p, trunk.fresh j p = 0
  blen : T → ℕ
  br : T → ZData K q

namespace BranchNet
variable {K : Type*} [Field K] {q : ι → κ → ZMod 2} {T : Type} [Fintype T] (N : BranchNet K q T)

def block (p s : ι) : K :=
  N.trunk.block N.tlen p s + ∑ i, (N.br i).blockIn (N.blen i) (N.trunk.tip N.tlen) p s

noncomputable def descentMass : ℕ :=
  N.trunk.descentMass N.tlen + ∑ i, (N.br i).descentMass (N.blen i)

def toZ : ZLayout K q T := ⟨N.blen, N.br⟩

theorem block_eq (p s : ι) : N.block p s = N.toZ.block p s := by
  unfold block ZLayout.block toZ
  rw [N.trunk.block_zero N.free p s, zero_add, N.trunk.tip_zero N.free]
  exact Finset.sum_congr rfl fun i _ => (N.br i).blockIn_zero _ p s

theorem toZ_mass_le : N.toZ.descentMass ≤ N.descentMass := by
  unfold descentMass ZLayout.descentMass toZ
  dsimp only
  omega

end BranchNet

/-- (c) chains merging into a gather-free tail. -/
structure MergeNet (K : Type*) [Field K] (q : ι → κ → ZMod 2) (T : Type*) where
  blen : T → ℕ
  br : T → ZData K q
  tail : ZData K q
  tlen : ℕ
  nogath : ∀ k, k < tlen → ∀ s, tail.gath k s = 0

namespace MergeNet
variable {K : Type*} [Field K] {q : ι → κ → ZMod 2} {T : Type} [Fintype T] (N : MergeNet K q T)

def block (p s : ι) : K :=
  ∑ i, (N.br i).block (N.blen i) p s +
    N.tail.blockIn N.tlen (fun p => ∑ i, (N.br i).tip (N.blen i) p) p s

noncomputable def descentMass : ℕ :=
  (∑ i, (N.br i).descentMass (N.blen i)) + N.tail.descentMass N.tlen

def toZ : ZLayout K q T := ⟨N.blen, N.br⟩

theorem block_eq (p s : ι) : N.block p s = N.toZ.block p s := by
  unfold block ZLayout.block toZ
  rw [N.tail.block_gath_zero N.nogath _ p s, add_zero]

theorem toZ_mass_le : N.toZ.descentMass ≤ N.descentMass := by
  unfold descentMass ZLayout.descentMass toZ
  dsimp only
  omega

end MergeNet

/-- **THEOREM W (b).**  Branching off a fresh-free trunk: ≤ 8 pure pieces ⇒ descent mass ≥ 56. -/
theorem branch_mass_ge_56 {T : Type} [Fintype T] (N : BranchNet ℚ DF.lq T)
    (hdiag : ∀ t, N.block t t = 1)
    (hodd : ∀ t s, t ≠ s → dot (DF.lq t) (DF.lq s) = 1 → N.block t s = 0)
    (h8 : N.toZ.pieces ≤ 8) : 56 ≤ N.descentMass := by
  have hR : N.toZ.Realises :=
    { diag := fun t => by rw [← N.block_eq]; exact hdiag t
      odd := fun t s h1 h2 => by rw [← N.block_eq]; exact hodd t s h1 h2 }
  exact (zlayout_mass_ge_56 N.toZ hR h8).trans N.toZ_mass_le

/-- **THEOREM W (c).**  Merging into a gather-free tail: ≤ 8 pure pieces ⇒ descent mass ≥ 56. -/
theorem merge_mass_ge_56 {T : Type} [Fintype T] (N : MergeNet ℚ DF.lq T)
    (hdiag : ∀ t, N.block t t = 1)
    (hodd : ∀ t s, t ≠ s → dot (DF.lq t) (DF.lq s) = 1 → N.block t s = 0)
    (h8 : N.toZ.pieces ≤ 8) : 56 ≤ N.descentMass := by
  have hR : N.toZ.Realises :=
    { diag := fun t => by rw [← N.block_eq]; exact hdiag t
      odd := fun t s h1 h2 => by rw [← N.block_eq]; exact hodd t s h1 h2 }
  exact (zlayout_mass_ge_56 N.toZ hR h8).trans N.toZ_mass_le

end ChainRow

#print axioms ChainRow.BranchNet.block_eq
#print axioms ChainRow.MergeNet.block_eq
#print axioms ChainRow.branch_mass_ge_56
#print axioms ChainRow.merge_mass_ge_56
