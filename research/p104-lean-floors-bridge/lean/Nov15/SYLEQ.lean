/-
LEAN-NEXT2 (Nov 16): SPECBREAK R21 Part A, the SYLEQ closure as an operator.
A1 (each rule monotone) and A3's rule soundness are properties of the concrete rules (R20 §4) and
enter as explicit hypotheses; everything else is proved for an arbitrary finite poset of states
(⊥ = "contradiction" is just the least state, if present):
  * A2 confluence: every fair chaotic iteration of monotone deflationary rules from σ₀ stops,
    and the stopping point is the greatest common fixed point below σ₀ — so it (and the verdict
    "= ⊥") does not depend on the rule order;
  * A3 soundness: a state below σ₀ preserved by every rule lies below the closure;
  * A4 equivariance: an order isomorphism intertwining start and rules maps closures to closures.
  * A1 instance: the COVER rule (union of the A_x sets must cover a fixed register set R) is
    monotone and deflationary on the concrete state space of set families.
-/
import Mathlib.Order.WellFoundedSet
import Mathlib.Order.OrderIsoNat
import Mathlib.Data.Fintype.Lattice
import Mathlib.Order.Fin.Basic
import Mathlib.Data.Finset.Lattice.Fold

namespace SYLEQ

variable {α ι : Type*} [PartialOrder α]

/-- the iteration `σ_{k+1} = ρ_{c k}(σ_k)`. -/
def iter (ρ : ι → α → α) (σ0 : α) (c : ℕ → ι) : ℕ → α
  | 0 => σ0
  | k + 1 => ρ (c k) (iter ρ σ0 c k)

/-- common fixed points of all rules below `σ₀`. -/
def CFix (ρ : ι → α → α) (σ0 τ : α) : Prop := τ ≤ σ0 ∧ ∀ i, ρ i τ = τ

/-- every common fixed point below `σ₀` stays below every iterate (monotonicity, A1). -/
lemma cfix_le_iter (ρ : ι → α → α) (hmono : ∀ i, Monotone (ρ i)) (σ0 : α) (c : ℕ → ι)
    {τ : α} (hτ : CFix ρ σ0 τ) : ∀ k, τ ≤ iter ρ σ0 c k
  | 0 => hτ.1
  | k + 1 => by
    show τ ≤ ρ (c k) (iter ρ σ0 c k)
    calc τ = ρ (c k) τ := (hτ.2 (c k)).symm
      _ ≤ ρ (c k) (iter ρ σ0 c k) := hmono (c k) (cfix_le_iter ρ hmono σ0 c hτ k)

lemma iter_antitone (ρ : ι → α → α) (hdefl : ∀ i σ, ρ i σ ≤ σ) (σ0 : α) (c : ℕ → ι) :
    Antitone (iter ρ σ0 c) :=
  antitone_nat_of_succ_le fun k => hdefl (c k) _

lemma iter_le_start (ρ : ι → α → α) (hdefl : ∀ i σ, ρ i σ ≤ σ) (σ0 : α) (c : ℕ → ι) (k : ℕ) :
    iter ρ σ0 c k ≤ σ0 :=
  iter_antitone ρ hdefl σ0 c (Nat.zero_le k)

/-- **A2, termination.** On a finite poset, a fair iteration (every rule chosen infinitely often)
reaches a common fixed point below `σ₀`. -/
theorem fair_iter_stops [Finite α] (ρ : ι → α → α) (hdefl : ∀ i σ, ρ i σ ≤ σ) (σ0 : α) (c : ℕ → ι)
    (hfair : ∀ i N, ∃ k ≥ N, c k = i) : ∃ N, CFix ρ σ0 (iter ρ σ0 c N) ∧
      ∀ k ≥ N, iter ρ σ0 c k = iter ρ σ0 c N := by
  -- an antitone sequence in a finite poset is eventually constant
  have hwf : WellFoundedGT αᵒᵈ := inferInstance
  obtain ⟨N, hN⟩ := (wellFoundedGT_iff_monotone_chain_condition.mp hwf)
    ⟨fun k => OrderDual.toDual (iter ρ σ0 c k), fun a b hab => iter_antitone ρ hdefl σ0 c hab⟩
  refine ⟨N, ⟨iter_le_start ρ hdefl σ0 c N, fun i => ?_⟩, fun k hk => (hN k hk).symm⟩
  obtain ⟨k, hk, hck⟩ := hfair i N
  have h1 : iter ρ σ0 c (k + 1) = iter ρ σ0 c N := (hN (k + 1) (by omega)).symm
  have h2 : iter ρ σ0 c k = iter ρ σ0 c N := (hN k hk).symm
  rw [← h2]
  calc ρ i (iter ρ σ0 c k) = iter ρ σ0 c (k + 1) := by rw [iter, hck]
    _ = iter ρ σ0 c k := by rw [h1, h2]

/-- **A2, the stopping point is the greatest common fixed point below `σ₀`.** -/
theorem stop_is_greatest (ρ : ι → α → α) (hmono : ∀ i, Monotone (ρ i)) (σ0 : α) (c : ℕ → ι)
    (N : ℕ) (hN : CFix ρ σ0 (iter ρ σ0 c N)) :
    IsGreatest {τ | CFix ρ σ0 τ} (iter ρ σ0 c N) :=
  ⟨hN, fun _ hτ => cfix_le_iter ρ hmono σ0 c hτ N⟩

/-- **A2, confluence (Corollary A2).** Any two iterations (any rule orders) that stop at common
fixed points stop at the same state. -/
theorem confluence (ρ : ι → α → α) (hmono : ∀ i, Monotone (ρ i)) (σ0 : α) (c c' : ℕ → ι)
    (N N' : ℕ) (hN : CFix ρ σ0 (iter ρ σ0 c N)) (hN' : CFix ρ σ0 (iter ρ σ0 c' N')) :
    iter ρ σ0 c N = iter ρ σ0 c' N' :=
  le_antisymm (cfix_le_iter ρ hmono σ0 c' hN N') (cfix_le_iter ρ hmono σ0 c hN' N)

/-- **A2, the kill verdict is order independent**: with a least state `⊥` ("contradiction"),
one fair iteration ends at `⊥` iff every other does. -/
theorem kill_independent [Finite α] [OrderBot α] (ρ : ι → α → α) (hmono : ∀ i, Monotone (ρ i))
    (hdefl : ∀ i σ, ρ i σ ≤ σ) (σ0 : α) (c c' : ℕ → ι)
    (hfair : ∀ i N, ∃ k ≥ N, c k = i) (hfair' : ∀ i N, ∃ k ≥ N, c' k = i) :
    ∃ N N', (∀ k ≥ N, iter ρ σ0 c k = iter ρ σ0 c N) ∧ (∀ k ≥ N', iter ρ σ0 c' k = iter ρ σ0 c' N') ∧
      iter ρ σ0 c N = iter ρ σ0 c' N' ∧ (iter ρ σ0 c N = ⊥ ↔ iter ρ σ0 c' N' = ⊥) := by
  obtain ⟨N, hN, hs⟩ := fair_iter_stops ρ hdefl σ0 c hfair
  obtain ⟨N', hN', hs'⟩ := fair_iter_stops ρ hdefl σ0 c' hfair'
  have e := confluence ρ hmono σ0 c c' N N' hN hN'
  exact ⟨N, N', hs, hs', e, by rw [e]⟩

/-- **A3, soundness.** If `σ_W ≤ σ₀` and every rule maps states above `σ_W` to states above `σ_W`
(R20 §4: the support state of a realisation is never cut), then `σ_W` lies below every iterate,
in particular below the closure; so a realisable profile is never killed (`σ_W ≠ ⊥`). -/
theorem soundness (ρ : ι → α → α) (σ0 σW : α) (hW0 : σW ≤ σ0)
    (hsound : ∀ i σ, σW ≤ σ → σW ≤ ρ i σ) (c : ℕ → ι) : ∀ k, σW ≤ iter ρ σ0 c k
  | 0 => hW0
  | k + 1 => hsound (c k) _ (soundness ρ σ0 σW hW0 hsound c k)

theorem not_killed [OrderBot α] (ρ : ι → α → α) (σ0 σW : α) (hW0 : σW ≤ σ0)
    (hsound : ∀ i σ, σW ≤ σ → σW ≤ ρ i σ) (hne : σW ≠ ⊥) (c : ℕ → ι) (k : ℕ) :
    iter ρ σ0 c k ≠ ⊥ := fun h => hne (le_bot_iff.mp (h ▸ soundness ρ σ0 σW hW0 hsound c k))

/-- **A4, equivariance.** If an order isomorphism `g` maps `σ₀` to `σ₀'` and intertwines the rules
(`ρ' i ∘ g = g ∘ ρ i`, e.g. a `GL(d,2)` relabelling), then `g` maps the closure (the greatest common
fixed point) of `(ρ, σ₀)` to that of `(ρ', σ₀')`. -/
theorem equivariance {β : Type*} [PartialOrder β] (ρ : ι → α → α) (ρ' : ι → β → β) (g : α ≃o β)
    (σ0 : α) (σ0' : β) (hg0 : g σ0 = σ0') (hgρ : ∀ i σ, ρ' i (g σ) = g (ρ i σ)) (Φ : α)
    (hΦ : IsGreatest {τ | CFix ρ σ0 τ} Φ) : IsGreatest {τ | CFix ρ' σ0' τ} (g Φ) := by
  refine ⟨⟨hg0 ▸ g.monotone hΦ.1.1, fun i => by rw [hgρ, hΦ.1.2 i]⟩, fun τ hτ => ?_⟩
  have : CFix ρ σ0 (g.symm τ) := by
    refine ⟨?_, fun i => ?_⟩
    · have := g.symm.monotone hτ.1; rwa [← hg0, OrderIso.symm_apply_apply] at this
    · apply g.injective
      rw [← hgρ, OrderIso.apply_symm_apply, hτ.2 i]
  have := g.monotone (hΦ.2 this)
  rwa [OrderIso.apply_symm_apply] at this

/-! ## A1 instance: the COVER rule on the concrete state space -/

section Cover

variable {V R : Type*} [Fintype V] [DecidableEq R]

/-- concrete SYLEQ states: a family of candidate register sets per job type (`some`), or `none` = ⊥
(contradiction). Information order: smaller sets = more information. -/
abbrev St (V R : Type*) := WithBot (V → Finset R)

/-- **COVER**: the registers `Req` (e.g. the flipped registers of a tight character) must lie in the
union of the job types' candidate sets; otherwise contradiction. -/
def cover (Req : Finset R) : St V R → St V R
  | ⊥ => ⊥
  | some A => if Req ⊆ Finset.univ.biUnion A then some A else ⊥

lemma cover_coe (Req : Finset R) (A : V → Finset R) :
    cover Req (A : St V R) = if Req ⊆ Finset.univ.biUnion A then (A : St V R) else ⊥ := rfl

lemma cover_defl (Req : Finset R) (σ : St V R) : cover Req σ ≤ σ := by
  induction σ using WithBot.recBotCoe with
  | bot => exact le_rfl
  | coe A =>
    rw [cover_coe]
    split_ifs
    · exact le_rfl
    · exact bot_le

/-- **A1 for COVER** (R21: "∪ Ax_v(σ) ⊆ ∪ Ax_v(σ′), so a σ′-cover failure is a σ-cover failure"). -/
lemma cover_mono (Req : Finset R) : Monotone (cover (V := V) Req) := by
  intro σ τ h
  induction σ using WithBot.recBotCoe with
  | bot => exact bot_le
  | coe A =>
    induction τ using WithBot.recBotCoe with
    | bot => exact absurd h (WithBot.coe_ne_bot ∘ le_bot_iff.mp)
    | coe B =>
      have hAB : A ≤ B := WithBot.coe_le_coe.mp h
      rw [cover_coe, cover_coe]
      by_cases hA : Req ⊆ Finset.univ.biUnion A
      · have hB : Req ⊆ Finset.univ.biUnion B :=
          hA.trans (Finset.biUnion_mono fun v _ => hAB v)
        rw [if_pos hA, if_pos hB]; exact h
      · rw [if_neg hA]; exact bot_le

end Cover

/-! ## A1 instance: the RANK/EQ rule (LEAN-NEXT3, Nov 16)

R20 §4 / R21 A1, as implemented in R21/fpcheck.py (`kind == 'E'`). State: candidate sets `Ax_v, Ay_v`
(target registers plus the ancilla `anc`) and equality records `eX_μ, eY_μ` (`∅` = not recorded).
Order: `σ ≤ σ'` iff `Ax ⊆ Ax'`, `Ay ⊆ Ay'`, `eX ⊇ eX'`, `eY ⊇ eY'`. An EMPTY candidate set is a
contradiction, so the non-⊥ states are the valid ones (all candidate sets nonempty): R21's
"Ax_v = {j} or ⊥". On the raw space (empty sets allowed as non-⊥ states) the singleton step of A1
breaks, see `rankEq_mono` and SYLEQ.md. -/

section RankEq

variable {V M R : Type*} [DecidableEq V] [DecidableEq R] [DecidableEq M]

@[ext] structure ES (V M R : Type*) where
  Ax : V → Finset R
  Ay : V → Finset R
  eX : M → Finset R
  eY : M → Finset R

instance : PartialOrder (ES V M R) where
  le s t := s.Ax ≤ t.Ax ∧ s.Ay ≤ t.Ay ∧ t.eX ≤ s.eX ∧ t.eY ≤ s.eY
  le_refl s := ⟨le_rfl, le_rfl, le_rfl, le_rfl⟩
  le_trans a b c h1 h2 :=
    ⟨h1.1.trans h2.1, h1.2.1.trans h2.2.1, h2.2.2.1.trans h1.2.2.1, h2.2.2.2.trans h1.2.2.2⟩
  le_antisymm a b h1 h2 := ES.ext (le_antisymm h1.1 h2.1) (le_antisymm h1.2.1 h2.2.1)
    (le_antisymm h2.2.2.1 h1.2.2.1) (le_antisymm h2.2.2.2 h1.2.2.2)

lemma ES.le_def (s t : ES V M R) :
    s ≤ t ↔ s.Ax ≤ t.Ax ∧ s.Ay ≤ t.Ay ∧ t.eX ≤ s.eX ∧ t.eY ≤ s.eY := Iff.rfl

/-- valid (non-contradictory) states: every candidate set is nonempty (`x_k ≠ 0`, `y_k ≠ 0`). -/
def Valid (s : ES V M R) : Prop := ∀ v, (s.Ax v).Nonempty ∧ (s.Ay v).Nonempty

abbrev VS (V M R : Type*) [DecidableEq R] [DecidableEq M] := WithBot {s : ES V M R // Valid s}

/-- registers forced by singleton candidate sets `A_v = {j}`, `j` not the ancilla, `v ∈ S_μ`. -/
def singles (S : Finset V) (anc : R) (A : V → Finset R) : Finset R :=
  S.biUnion fun v => if (A v).card = 1 ∧ anc ∉ A v then A v else ∅

/-- `C_X = R(S) ∪ nested ∪ singletons ∪ (eq records of the nested μ', μ itself included)`;
`nestR` is the fixed part (R(S) and the `E_ν` of nested characters). -/
def CXof (S : Finset V) (anc : R) (nestR : Finset R) (Nest : Finset M) (A : V → Finset R)
    (e : M → Finset R) : Finset R :=
  nestR ∪ singles S anc A ∪ Nest.biUnion e

/-- the pinned state at equality: `A_v ← A_v ∩ C` for `v ∈ S`, record `e_μ ← C`. -/
def pin (S : Finset V) (CX CY : Finset R) (μ : M) (s : ES V M R) : ES V M R :=
  ⟨fun v => if v ∈ S then s.Ax v ∩ CX else s.Ax v, fun v => if v ∈ S then s.Ay v ∩ CY else s.Ay v,
    Function.update s.eX μ CX, Function.update s.eY μ CY⟩

lemma pin_valid (S : Finset V) (CX CY : Finset R) (μ : M) (s : ES V M R) (hs : Valid s)
    (h : ∀ v ∈ S, (s.Ax v ∩ CX).Nonempty ∧ (s.Ay v ∩ CY).Nonempty) : Valid (pin S CX CY μ s) := by
  intro v
  by_cases hv : v ∈ S
  · simpa [pin, hv] using h v hv
  · simpa [pin, hv] using hs v

/-- **RANK/EQ at μ** (`bound = J_μ + r_μ`): `|C_X| + |C_Y| > bound` kills; at equality pin (an empty
pinned set kills); below equality nothing happens. -/
def rankEq (S : Finset V) (anc : R) (nestR : Finset R) (Nest : Finset M) (μ : M) (bound : ℕ) :
    VS V M R → VS V M R
  | ⊥ => ⊥
  | some s =>
    if bound < (CXof S anc nestR Nest s.1.Ax s.1.eX).card + (CXof S anc nestR Nest s.1.Ay s.1.eY).card
    then ⊥
    else if (CXof S anc nestR Nest s.1.Ax s.1.eX).card
        + (CXof S anc nestR Nest s.1.Ay s.1.eY).card = bound then
      if h : ∀ v ∈ S, (s.1.Ax v ∩ CXof S anc nestR Nest s.1.Ax s.1.eX).Nonempty ∧
          (s.1.Ay v ∩ CXof S anc nestR Nest s.1.Ay s.1.eY).Nonempty then
        WithBot.some ⟨pin S (CXof S anc nestR Nest s.1.Ax s.1.eX) (CXof S anc nestR Nest s.1.Ay s.1.eY) μ s.1,
          pin_valid _ _ _ _ s.1 s.2 h⟩
      else ⊥
    else some s

variable (S : Finset V) (anc : R) (nestR : Finset R) (Nest : Finset M) (μ : M) (bound : ℕ)

/-- `C_X(σ) ⊇ C_X(σ')` for `σ ≤ σ'` with `σ` valid: a singleton `A'_v = {j}` forces `A_v = {j}`
(nonempty subset), and equality records only grow downwards. -/
lemma CX_anti (A A' : V → Finset R) (e e' : M → Finset R) (hA : A ≤ A') (he : e' ≤ e)
    (hne : ∀ v, (A v).Nonempty) :
    CXof S anc nestR Nest A' e' ⊆ CXof S anc nestR Nest A e := by
  intro j hj
  simp only [CXof, Finset.mem_union, Finset.mem_biUnion] at hj ⊢
  rcases hj with (hj | hj) | ⟨ν, hν, hj⟩
  · exact Or.inl (Or.inl hj)
  · left; right
    simp only [singles, Finset.mem_biUnion] at hj ⊢
    obtain ⟨v, hv, hj⟩ := hj
    split_ifs at hj with hc
    · have hsub : A v ⊆ A' v := hA v
      have heq : A v = A' v :=
        Finset.eq_of_subset_of_card_le hsub (by rw [hc.1]; exact Finset.card_pos.mpr (hne v))
      refine ⟨v, hv, ?_⟩
      rw [if_pos (heq ▸ hc)]; exact heq ▸ hj
    · simp at hj
  · exact Or.inr ⟨ν, hν, he ν hj⟩

lemma rankEq_coe (s : {s : ES V M R // Valid s}) :
    rankEq S anc nestR Nest μ bound (s : VS V M R) =
      if bound < (CXof S anc nestR Nest s.1.Ax s.1.eX).card + (CXof S anc nestR Nest s.1.Ay s.1.eY).card
      then ⊥
      else if (CXof S anc nestR Nest s.1.Ax s.1.eX).card
          + (CXof S anc nestR Nest s.1.Ay s.1.eY).card = bound then
        if h : ∀ v ∈ S, (s.1.Ax v ∩ CXof S anc nestR Nest s.1.Ax s.1.eX).Nonempty ∧
            (s.1.Ay v ∩ CXof S anc nestR Nest s.1.Ay s.1.eY).Nonempty then
          WithBot.some ⟨pin S (CXof S anc nestR Nest s.1.Ax s.1.eX) (CXof S anc nestR Nest s.1.Ay s.1.eY) μ s.1,
            pin_valid _ _ _ _ s.1 s.2 h⟩
        else ⊥
      else (s : VS V M R) := rfl

/-- `rankEq_coe` with the two sets named. -/
lemma rankEq_coe' (s : {s : ES V M R // Valid s}) (CX CY : Finset R)
    (hX : CXof S anc nestR Nest s.1.Ax s.1.eX = CX) (hY : CXof S anc nestR Nest s.1.Ay s.1.eY = CY) :
    ∃ hp : (∀ v ∈ S, (s.1.Ax v ∩ CX).Nonempty ∧ (s.1.Ay v ∩ CY).Nonempty) → Valid (pin S CX CY μ s.1),
    rankEq S anc nestR Nest μ bound (s : VS V M R) =
      if bound < CX.card + CY.card then ⊥
      else if CX.card + CY.card = bound then
        if h : ∀ v ∈ S, (s.1.Ax v ∩ CX).Nonempty ∧ (s.1.Ay v ∩ CY).Nonempty then
          WithBot.some ⟨pin S CX CY μ s.1, hp h⟩
        else ⊥
      else (s : VS V M R) := by
  subst hX hY
  exact ⟨fun h => pin_valid _ _ _ _ s.1 s.2 h, rfl⟩

/-- pinning with the same sets is monotone. -/
lemma pin_mono (CX CY : Finset R) (s t : ES V M R) (h : s ≤ t) :
    pin S CX CY μ s ≤ pin S CX CY μ t := by
  rw [ES.le_def] at h ⊢
  obtain ⟨h1, h2, h3, h4⟩ := h
  refine ⟨fun v => ?_, fun v => ?_, fun ν => ?_, fun ν => ?_⟩
  · by_cases hv : v ∈ S
    · simp only [pin, hv, if_true]; exact Finset.inter_subset_inter (h1 v) le_rfl
    · simp only [pin, hv, if_false]; exact h1 v
  · by_cases hv : v ∈ S
    · simp only [pin, hv, if_true]; exact Finset.inter_subset_inter (h2 v) le_rfl
    · simp only [pin, hv, if_false]; exact h2 v
  · by_cases hν : ν = μ
    · subst hν; simp [pin]
    · simp only [pin, Function.update_of_ne hν]; exact h3 ν
  · by_cases hν : ν = μ
    · subst hν; simp [pin]
    · simp only [pin, Function.update_of_ne hν]; exact h4 ν

/-- RANK/EQ is deflationary (needs `μ` among its own nested characters, as in fpcheck.py). -/
lemma rankEq_defl (hμ : μ ∈ Nest) (σ : VS V M R) : rankEq S anc nestR Nest μ bound σ ≤ σ := by
  induction σ using WithBot.recBotCoe with
  | bot => exact le_rfl
  | coe s =>
    rw [rankEq_coe]
    split_ifs with h1 h2 h3
    · exact bot_le
    · refine WithBot.coe_le_coe.mpr ?_
      show pin _ _ _ μ s.1 ≤ s.1
      rw [ES.le_def]
      refine ⟨fun v => ?_, fun v => ?_, fun ν => ?_, fun ν => ?_⟩
      · by_cases hv : v ∈ S <;> simp [pin, hv]
      · by_cases hv : v ∈ S <;> simp [pin, hv]
      · by_cases hν : ν = μ
        · subst hν; simp only [pin, Function.update_self]
          exact fun j hj => Finset.mem_union_right _ (Finset.mem_biUnion.mpr ⟨ν, hμ, hj⟩)
        · simp [pin, Function.update_of_ne hν]
      · by_cases hν : ν = μ
        · subst hν; simp only [pin, Function.update_self]
          exact fun j hj => Finset.mem_union_right _ (Finset.mem_biUnion.mpr ⟨ν, hμ, hj⟩)
        · simp [pin, Function.update_of_ne hν]
    · exact bot_le
    · exact le_rfl

/-- **A1 for RANK/EQ** (R21: C_X(σ) ⊇ C_X(σ′); if σ′ is at equality, σ is at ⊥ or at equality with the
same C_X, C_Y and pins by the same sets; otherwise ρ(σ′) = σ′ ≥ σ ≥ ρ(σ)). -/
lemma rankEq_mono (hμ : μ ∈ Nest) : Monotone (rankEq (V := V) S anc nestR Nest μ bound) := by
  intro σ τ h
  induction σ using WithBot.recBotCoe with
  | bot => exact bot_le
  | coe s =>
    induction τ using WithBot.recBotCoe with
    | bot => exact absurd h (WithBot.coe_ne_bot ∘ le_bot_iff.mp)
    | coe t =>
      have hst0 : s ≤ t := WithBot.coe_le_coe.mp h
      have hst : s.1 ≤ t.1 := hst0
      rw [ES.le_def] at hst
      obtain ⟨CXs, hCXs⟩ : ∃ C, CXof S anc nestR Nest s.1.Ax s.1.eX = C := ⟨_, rfl⟩
      obtain ⟨CYs, hCYs⟩ : ∃ C, CXof S anc nestR Nest s.1.Ay s.1.eY = C := ⟨_, rfl⟩
      obtain ⟨CXt, hCXt⟩ : ∃ C, CXof S anc nestR Nest t.1.Ax t.1.eX = C := ⟨_, rfl⟩
      obtain ⟨CYt, hCYt⟩ : ∃ C, CXof S anc nestR Nest t.1.Ay t.1.eY = C := ⟨_, rfl⟩
      have hX : CXt ⊆ CXs := hCXt ▸ hCXs ▸
        CX_anti S anc nestR Nest s.1.Ax t.1.Ax s.1.eX t.1.eX hst.1 hst.2.2.1 (fun v => (s.2 v).1)
      have hY : CYt ⊆ CYs := hCYt ▸ hCYs ▸
        CX_anti S anc nestR Nest s.1.Ay t.1.Ay s.1.eY t.1.eY hst.2.1 hst.2.2.2 (fun v => (s.2 v).2)
      have cX := Finset.card_le_card hX
      have cY := Finset.card_le_card hY
      obtain ⟨hps, es⟩ := rankEq_coe' S anc nestR Nest μ bound s CXs CYs hCXs hCYs
      obtain ⟨hpt, et⟩ := rankEq_coe' S anc nestR Nest μ bound t CXt CYt hCXt hCYt
      rw [es, et]
      by_cases h1 : bound < CXs.card + CYs.card
      · rw [if_pos h1]; exact bot_le
      rw [if_neg h1, if_neg (show ¬ bound < CXt.card + CYt.card by omega)]
      by_cases h2 : CXs.card + CYs.card = bound
      · rw [if_pos h2]
        by_cases h3 : CXt.card + CYt.card = bound
        · have eX : CXt = CXs := Finset.eq_of_subset_of_card_le hX (by omega)
          have eY : CYt = CYs := Finset.eq_of_subset_of_card_le hY (by omega)
          rw [if_pos h3]
          by_cases hs : ∀ v ∈ S, (s.1.Ax v ∩ CXs).Nonempty ∧ (s.1.Ay v ∩ CYs).Nonempty
          · have ht : ∀ v ∈ S, (t.1.Ax v ∩ CXt).Nonempty ∧ (t.1.Ay v ∩ CYt).Nonempty := by
              intro v hv
              rw [eX, eY]
              exact ⟨(hs v hv).1.mono (Finset.inter_subset_inter (hst.1 v) le_rfl),
                (hs v hv).2.mono (Finset.inter_subset_inter (hst.2.1 v) le_rfl)⟩
            rw [dif_pos hs, dif_pos ht]
            refine WithBot.coe_le_coe.mpr ?_
            show pin S CXs CYs μ s.1 ≤ pin S CXt CYt μ t.1
            rw [eX, eY]
            exact pin_mono S μ CXs CYs s.1 t.1 ((ES.le_def _ _).mpr hst)
          · rw [dif_neg hs]; exact bot_le
        · rw [if_neg h3]
          have := rankEq_defl S anc nestR Nest μ bound hμ (s : VS V M R)
          rw [es, if_neg h1, if_pos h2] at this
          exact this.trans h
      · rw [if_neg h2, if_neg (show ¬ CXt.card + CYt.card = bound by omega)]
        exact h

end RankEq

/-! ## R21 empty-set issue (LEAN-NEXT4, Nov 16): RANK/EQ on the RAW space

On the raw space `WithBot (ES V M R)` an empty candidate set is an ordinary (non-⊥) state. There
RANK/EQ is NOT monotone (`rankEqRaw_not_mono`): a state with `Ax_v = ∅` sits below a state with
`Ax_v = {j}`, loses the singleton `j` from `C_X`, falls below equality and is left alone, while the
larger state is pinned and records `eX_μ = {j}`, which the smaller state's empty record does not
contain. The fix: normalise first (any empty candidate set ⇒ ⊥) and then apply the valid-space rule.
The normaliser is monotone because an empty set stays empty below, so the fixed operator is monotone
and deflationary on the raw space (`rankEqFix_mono`, `rankEqFix_defl`), and it agrees with the raw
rule on valid states (`rankEqFix_valid`). -/

section RawEmpty

variable {V M R : Type*} [DecidableEq V] [DecidableEq R] [DecidableEq M]

/-- RANK/EQ exactly as written, on raw states (empty candidate sets allowed). -/
def rankEqRaw (S : Finset V) (anc : R) (nestR : Finset R) (Nest : Finset M) (μ : M) (bound : ℕ) :
    WithBot (ES V M R) → WithBot (ES V M R)
  | ⊥ => ⊥
  | some s =>
    if bound < (CXof S anc nestR Nest s.Ax s.eX).card + (CXof S anc nestR Nest s.Ay s.eY).card
    then ⊥
    else if (CXof S anc nestR Nest s.Ax s.eX).card + (CXof S anc nestR Nest s.Ay s.eY).card = bound then
      if ∀ v ∈ S, (s.Ax v ∩ CXof S anc nestR Nest s.Ax s.eX).Nonempty ∧
          (s.Ay v ∩ CXof S anc nestR Nest s.Ay s.eY).Nonempty then
        some (pin S (CXof S anc nestR Nest s.Ax s.eX) (CXof S anc nestR Nest s.Ay s.eY) μ s)
      else ⊥
    else some s

/-- **A1 fails on the raw space.** One job type, `R = {0, 1, 2}` with ancilla `2`, `bound = 2`,
`μ` its own nested character. `s`: `Ax = ∅`, `Ay = {1}`; `t`: `Ax = {0}`, `Ay = {1}`; no records.
Then `s ≤ t`, `C_X(s) = ∅` (rank sum 1 < 2: unchanged), `C_X(t) = {0}` (sum 2: pinned, `eX_μ = {0}`),
and `rankEq s = s ≰ pin(t) = rankEq t`. -/
theorem rankEqRaw_not_mono :
    let s : ES Unit Unit (Fin 3) := ⟨fun _ => ∅, fun _ => {1}, fun _ => ∅, fun _ => ∅⟩
    let t : ES Unit Unit (Fin 3) := ⟨fun _ => {0}, fun _ => {1}, fun _ => ∅, fun _ => ∅⟩
    let ρ := rankEqRaw (V := Unit) (M := Unit) (R := Fin 3) {()} 2 ∅ {()} () 2
    (s : WithBot (ES Unit Unit (Fin 3))) ≤ t ∧ ¬ ρ s ≤ ρ t := by
  intro s t ρ
  refine ⟨WithBot.coe_le_coe.mpr ((ES.le_def _ _).mpr ⟨fun _ => by simp [s, t],
    fun _ => le_rfl, fun _ => le_rfl, fun _ => le_rfl⟩), ?_⟩
  have hs : ρ s = s := by
    simp [ρ, rankEqRaw, s, CXof, singles]; rfl
  have ht : ρ t = (pin {()} {0} {1} () t : ES Unit Unit (Fin 3)) := by
    simp [ρ, rankEqRaw, t, CXof, singles]; rfl
  rw [hs, ht, WithBot.coe_le_coe, ES.le_def]
  rintro ⟨-, -, h, -⟩
  have := h () (show (0 : Fin 3) ∈ (pin {()} {0} {1} () t).eX () by simp [pin])
  simp [s] at this

section Fix

open Classical

/-- the normaliser: a raw state with an empty candidate set is a contradiction. -/
noncomputable def norm : WithBot (ES V M R) → VS V M R
  | ⊥ => ⊥
  | (s : ES V M R) => if h : Valid s then ((⟨s, h⟩ : {s : ES V M R // Valid s}) : VS V M R) else ⊥

lemma norm_coe (s : ES V M R) : norm (s : WithBot (ES V M R)) =
    if h : Valid s then ((⟨s, h⟩ : {s : ES V M R // Valid s}) : VS V M R) else ⊥ := rfl

def embed : VS V M R → WithBot (ES V M R)
  | ⊥ => ⊥
  | (s : {s : ES V M R // Valid s}) => ((s.1 : ES V M R) : WithBot (ES V M R))

lemma embed_coe (s : {s : ES V M R // Valid s}) :
    embed (s : VS V M R) = ((s.1 : ES V M R) : WithBot (ES V M R)) := rfl

lemma rankEqRaw_coe (S : Finset V) (anc : R) (nestR : Finset R) (Nest : Finset M) (μ : M)
    (bound : ℕ) (s : ES V M R) :
    rankEqRaw S anc nestR Nest μ bound (s : WithBot (ES V M R)) =
    if bound < (CXof S anc nestR Nest s.Ax s.eX).card + (CXof S anc nestR Nest s.Ay s.eY).card
    then ⊥
    else if (CXof S anc nestR Nest s.Ax s.eX).card + (CXof S anc nestR Nest s.Ay s.eY).card = bound then
      if ∀ v ∈ S, (s.Ax v ∩ CXof S anc nestR Nest s.Ax s.eX).Nonempty ∧
          (s.Ay v ∩ CXof S anc nestR Nest s.Ay s.eY).Nonempty then
        ((pin S (CXof S anc nestR Nest s.Ax s.eX) (CXof S anc nestR Nest s.Ay s.eY) μ s : ES V M R) :
          WithBot (ES V M R))
      else ⊥
    else (s : WithBot (ES V M R)) := rfl

lemma norm_mono : Monotone (norm (V := V) (M := M) (R := R)) := by
  intro σ τ h
  induction σ using WithBot.recBotCoe with
  | bot => exact bot_le
  | coe s =>
    induction τ using WithBot.recBotCoe with
    | bot => exact absurd h (WithBot.coe_ne_bot ∘ le_bot_iff.mp)
    | coe t =>
      have hst : s ≤ t := WithBot.coe_le_coe.mp h
      rw [norm_coe, norm_coe]
      by_cases hs : Valid s
      · have ht : Valid t := fun v =>
          ⟨(hs v).1.mono (((ES.le_def _ _).mp hst).1 v), (hs v).2.mono (((ES.le_def _ _).mp hst).2.1 v)⟩
        rw [dif_pos hs, dif_pos ht]
        exact WithBot.coe_le_coe.mpr (show (⟨s, hs⟩ : {s : ES V M R // Valid s}) ≤ ⟨t, ht⟩ from hst)
      · rw [dif_neg hs]; exact bot_le

lemma embed_mono : Monotone (embed (V := V) (M := M) (R := R)) := by
  intro σ τ h
  induction σ using WithBot.recBotCoe with
  | bot => exact bot_le
  | coe s =>
    induction τ using WithBot.recBotCoe with
    | bot => exact absurd h (WithBot.coe_ne_bot ∘ le_bot_iff.mp)
    | coe t =>
      have h' : s ≤ t := WithBot.coe_le_coe.mp h
      rw [embed_coe, embed_coe]
      exact WithBot.coe_le_coe.mpr h'

lemma embed_norm_le (σ : WithBot (ES V M R)) : embed (norm σ) ≤ σ := by
  induction σ using WithBot.recBotCoe with
  | bot => exact le_rfl
  | coe s =>
    rw [norm_coe]
    by_cases hs : Valid s
    · rw [dif_pos hs, embed_coe]
    · rw [dif_neg hs]; exact bot_le

variable (S : Finset V) (anc : R) (nestR : Finset R) (Nest : Finset M) (μ : M) (bound : ℕ)

/-- the fixed rule: normalise (empty set ⇒ ⊥), then RANK/EQ on valid states. -/
noncomputable def rankEqFix : WithBot (ES V M R) → WithBot (ES V M R) :=
  fun σ => embed (rankEq S anc nestR Nest μ bound (norm σ))

/-- **The fix is monotone** (A1 on the raw space). -/
lemma rankEqFix_mono (hμ : μ ∈ Nest) : Monotone (rankEqFix (V := V) S anc nestR Nest μ bound) :=
  embed_mono.comp ((rankEq_mono S anc nestR Nest μ bound hμ).comp norm_mono)

/-- **The fix is deflationary.** -/
lemma rankEqFix_defl (hμ : μ ∈ Nest) (σ : WithBot (ES V M R)) :
    rankEqFix S anc nestR Nest μ bound σ ≤ σ :=
  (embed_mono (rankEq_defl S anc nestR Nest μ bound hμ (norm σ))).trans (embed_norm_le σ)

/-- on a valid state the fix is the raw rule. -/
lemma rankEqFix_valid (s : ES V M R) (hs : Valid s) :
    rankEqFix S anc nestR Nest μ bound (s : WithBot (ES V M R)) =
      rankEqRaw S anc nestR Nest μ bound s := by
  unfold rankEqFix
  rw [norm_coe, dif_pos hs, rankEq_coe, rankEqRaw_coe]
  split_ifs <;> rfl

end Fix

end RawEmpty

end SYLEQ

#print axioms SYLEQ.fair_iter_stops
#print axioms SYLEQ.stop_is_greatest
#print axioms SYLEQ.confluence
#print axioms SYLEQ.kill_independent
#print axioms SYLEQ.soundness
#print axioms SYLEQ.not_killed
#print axioms SYLEQ.equivariance
#print axioms SYLEQ.cover_mono
#print axioms SYLEQ.cover_defl
#print axioms SYLEQ.rankEq_mono
#print axioms SYLEQ.rankEq_defl
#print axioms SYLEQ.rankEqRaw_not_mono
#print axioms SYLEQ.rankEqFix_mono
#print axioms SYLEQ.rankEqFix_defl
#print axioms SYLEQ.rankEqFix_valid
