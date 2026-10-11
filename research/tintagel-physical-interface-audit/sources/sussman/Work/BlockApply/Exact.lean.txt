import Work.Block.Majorant
import Work.BlockAccounting.Steps

/-!
# Block paths with an EXACT block count (agent key: block-apply)

`Work.Block.Paths` (agent block-engine) carries an upper bound `c` of the cost
`w.costR φ` of a block word for ONE price list `φ`.  That is all the engine needs, but it
does not say which blocks the word contains.  Here the same calculus is redone with the cost
known EXACTLY and for EVERY price list at once:

* `XStep l M N c`      a block word on the single role `l`, `M ↦ N`, with
                       `∀ φ, w.costR φ = c φ`   (`c : (ℕ → ℝ) → ℝ`);
* `XRoute S T g c`     the same for a network of roles (`refl`, `cast`, `trans`, `gate`,
                       `on_role`, `of_route`, `shifts`, `lift`, `parallel`, `liveKernel`);
* `XPath A s t g c`    routes between frames of fixed orthonormal bases (`gate`, `reframe`,
                       `inc`, and `refl`/`trans`/`lift`/`parallel` with upstream's argument lists);
* `listCost φ L`       the price of a list `L` of `(rank, count)` pairs;
* `BWord.cost_cast`     natural-number cost = real cost (so `tally w.flat` is a price);
* `BWord.hist_of_listCost`
                       if `∀ φ, w.costR φ = listCost φ L` then the block histogram of `w` IS
                       the histogram of `L`:  `∀ r, w.hist r = histFn L r`;
* `engine_program_xcert`
                       the block engine (`engine_program_block`) fed with such a word and the
                       moment inequality of the list `L`.

All proofs follow `Work/Block/Frames.lean` and `Work/Block/Paths.lean` line by line; only the
cost field changes (`=` for all `φ` instead of `≤` for one `φ`).  No `sorry`.
-/

set_option linter.unusedSectionVars false

namespace OAI
namespace PowerSaving.Binary
open Matrix Finset
noncomputable section
section
variable {α ρ σ : Type*} [Fintype α] [DecidableEq α] [Fintype ρ] [DecidableEq ρ]
  [Fintype σ] [DecidableEq σ]

/-- Price of a list of `(rank, count)` pairs when a block of rank `r` costs `φ r`. -/
def listCost (φ : ℕ → ℝ) (l : List (ℕ × ℕ)) : ℝ := (l.map fun b => (b.2:ℝ) * φ b.1).sum

lemma listCost_nil (φ : ℕ → ℝ) : listCost φ [] = 0 := rfl
lemma listCost_cons (φ : ℕ → ℝ) (b : ℕ × ℕ) (l : List (ℕ × ℕ)) :
    listCost φ (b :: l) = (b.2:ℝ) * φ b.1 + listCost φ l := by
  simp [listCost]
lemma listCost_append (φ : ℕ → ℝ) (l l' : List (ℕ × ℕ)) :
    listCost φ (l ++ l') = listCost φ l + listCost φ l' := by
  simp [listCost]

/-- With the price list `(r/m)^z` the price of a list is its moment. -/
lemma listCost_moment (m : ℕ) (z : ℝ) (l : List (ℕ × ℕ)) :
    listCost (fun r => ((r:ℝ)/(m:ℝ))^z) l = BlockAccounting.moment m z l := rfl

/-- The price list "1 at rank `r`, 0 elsewhere" counts the blocks of rank `r`. -/
lemma BWord.costR_ind (w : BWord α ρ) (r : ℕ) :
    w.costR (fun q => if q = r then 1 else 0) = (w.hist r : ℝ) := by
  induction w with
  | nil => simp
  | cons mv w ih =>
    rw [BWord.costR_cons, ih, BWord.hist_cons]
    push_cast
    rw [add_comm]
    congr 1
    cases mv with
    | localM g => simp [BMove.costR, BMove.rk?]
    | shift l z => simp [BMove.costR, BMove.rk?]
    | block l rk z ind => simp [BMove.costR, BMove.rk?]

/-- The natural-number cost of a block word, as a real cost. -/
lemma BWord.cost_cast (g : ℕ → ℕ) (w : BWord α ρ) :
    ((w.cost g : ℕ) : ℝ) = w.costR (fun r => (g r : ℝ)) := by
  induction w with
  | nil => simp
  | cons mv w ih =>
    rw [BWord.cost_cons, BWord.costR_cons, ← ih]
    push_cast
    congr 1
    cases mv with
    | localM g' => simp [BMove.cost, BMove.costR, BMove.rk?]
    | shift l z => simp [BMove.cost, BMove.costR, BMove.rk?]
    | block l rk z ind => simp [BMove.cost, BMove.costR, BMove.rk?]

lemma listCost_ind (l : List (ℕ × ℕ)) (r : ℕ) :
    listCost (fun q => if q = r then 1 else 0) l = (BlockAccounting.histFn l r : ℝ) := by
  induction l with
  | nil => simp [listCost, BlockAccounting.histFn_nil]
  | cons b l ih =>
    rw [BlockAccounting.histFn_cons, listCost_cons, ih]
    push_cast
    congr 1
    by_cases h : b.1 = r <;> simp [h]

/-- **A word whose price is the price of a list, for every price list, has the histogram of
that list.** -/
theorem BWord.hist_of_listCost (w : BWord α ρ) (L : List (ℕ × ℕ))
    (h : ∀ φ : ℕ → ℝ, w.costR φ = listCost φ L) :
    ∀ r, w.hist r = BlockAccounting.histFn L r := by
  intro r
  have h1 := h (fun q => if q = r then 1 else 0)
  rw [BWord.costR_ind, listCost_ind] at h1
  exact_mod_cast h1

/-! ### one role -/

/-- A block word acting on the single role `l`, carrying the matrix `M` of that role to `N`,
whose cost is `c φ` for every price list `φ`. -/
def XStep (l : ρ) (M N : CMat α) (c : (ℕ → ℝ) → ℝ) : Prop :=
  ∃ (w : BWord α ρ) (U : CMat α), w.Proper (Fintype.card α) ∧ (∀ φ, w.costR φ = c φ) ∧
    U * M = N ∧ ∀ (f : ℕ) (x : Data α ρ f), walk f w.flat x = roleAct f l U x

namespace XStep
variable {l : ρ} {M N K : CMat α} {c c' : (ℕ → ℝ) → ℝ}

theorem refl (l : ρ) (M : CMat α) : XStep l M M (fun _ => 0) := by
  refine ⟨[], 1, fun mv h => by simp at h, fun _ => rfl, one_mul _, fun f x => ?_⟩
  funext j
  simp [walk, roleAct]

theorem cast (a : XStep l M N c) (h : ∀ φ, c φ = c' φ) : XStep l M N c' := by
  obtain ⟨w, U, hw, hc, hU, hwalk⟩ := a
  exact ⟨w, U, hw, fun φ => (hc φ).trans (h φ), hU, hwalk⟩

theorem trans (a : XStep l M N c) (b : XStep l N K c') :
    XStep l M K (fun φ => c φ + c' φ) := by
  obtain ⟨w, U, hw, hc, hU, hwalk⟩ := a
  obtain ⟨w', V, hw', hc', hV, hwalk'⟩ := b
  refine ⟨w ++ w', V * U, hw.append hw', fun φ => by rw [BWord.costR_append, hc, hc'],
    by rw [mul_assoc, hU, hV], fun f x => ?_⟩
  rw [BWord.flat_append, walk_append, hwalk, hwalk', roleAct_mul]

end XStep

namespace OBase
variable (A : OBase α)

lemma xup_small (l : ρ) (c d : Finset α) (h : Disjoint c d)
    (h1 : 1 ≤ d.card) (h2 : d.card < Fintype.card α) :
    XStep l (frame A c) (frame A (c ∪ d)) (fun φ => φ d.card) := by
  refine ⟨[BMove.block l d.card (A.fam d) (A.fam_indep d), BMove.shift l (A.corr d)],
    shift (A.corr d) * blockMat (A.fam d), ?_, ?_, ?_, ?_⟩
  · intro mv hmv
    simp only [List.mem_cons, List.not_mem_nil, or_false] at hmv
    rcases hmv with rfl|rfl
    · exact ⟨h1, h2⟩
    · trivial
  · intro φ
    simp [BWord.costR, BMove.costR, BMove.rk?]
  · rw [← A.deltas_eq, ← A.frame_union c d h]
  · intro f x
    rw [walk_flat_cons, walk_flat_cons]
    change roleAct f l (shift (A.corr d)) (roleAct f l (blockMat (A.fam d)) x) = _
    rw [roleAct_mul]

lemma xdown_small (l : ρ) (c d : Finset α) (h : Disjoint c d)
    (h1 : 1 ≤ d.card) (h2 : d.card < Fintype.card α) :
    XStep l (frame A (c ∪ d)) (frame A c) (fun φ => φ d.card) := by
  refine ⟨[BMove.block l d.card (A.fam d) (A.fam_indep d), BMove.shift l (A.corr d),
      BMove.shift l (A.tot d)],
    shift (A.tot d) * (shift (A.corr d) * blockMat (A.fam d)), ?_, ?_, ?_, ?_⟩
  · intro mv hmv
    simp only [List.mem_cons, List.not_mem_nil, or_false] at hmv
    rcases hmv with rfl|rfl|rfl
    · exact ⟨h1, h2⟩
    · trivial
    · trivial
  · intro φ
    simp [BWord.costR, BMove.costR, BMove.rk?]
  · rw [A.frame_union c d h, ← A.deltas_eq, ← mul_assoc, A.deltas_inv, one_mul]
  · intro f x
    rw [walk_flat_cons, walk_flat_cons, walk_flat_cons]
    change roleAct f l (shift (A.tot d)) (roleAct f l (shift (A.corr d))
      (roleAct f l (blockMat (A.fam d)) x)) = _
    rw [roleAct_mul, roleAct_mul, mul_assoc]

lemma erase_union' (c d : Finset α) (i : α) (hi : i ∈ d) :
    c ∪ d.erase i ∪ {i} = c ∪ d := by
  ext j
  simp only [Finset.mem_union, Finset.mem_erase, Finset.mem_singleton]
  constructor
  · rintro ((hj|⟨_, hj⟩)|rfl)
    · exact Or.inl hj
    · exact Or.inr hj
    · exact Or.inr hi
  · rintro (hj|hj)
    · exact Or.inl (Or.inl hj)
    · by_cases hji : j = i
      · exact Or.inr hji
      · exact Or.inl (Or.inr ⟨hji, hj⟩)

/-- One role moves UP by the lines `d`: exactly one block of rank `|d|` (two blocks, of ranks
`m-1` and `1`, if `|d| = m`; none if `d` is empty). -/
lemma xup_step (hm : 2 ≤ Fintype.card α) (l : ρ) (c d : Finset α) (h : Disjoint c d) :
    XStep l (frame A c) (frame A (c ∪ d))
      (fun φ => splitCost φ (Fintype.card α) d.card) := by
  by_cases h0 : d.card = 0
  · have hd : d = ∅ := Finset.card_eq_zero.mp h0
    subst hd
    rw [Finset.union_empty]
    exact (XStep.refl l _).cast (fun φ => by simp [splitCost])
  · by_cases h2 : d.card < Fintype.card α
    · exact (A.xup_small l c d h (Nat.pos_of_ne_zero h0) h2).cast
        (fun φ => by simp [splitCost, h0, h2])
    · have hfull : d.card = Fintype.card α :=
        le_antisymm (Finset.card_le_univ d) (Nat.le_of_not_lt h2)
      obtain ⟨i, hi⟩ : d.Nonempty := Finset.card_pos.mp (Nat.pos_of_ne_zero h0)
      have hcard : (d.erase i).card = Fintype.card α - 1 := by
        rw [Finset.card_erase_of_mem hi, hfull]
      have hd1 : Disjoint c (d.erase i) := h.mono_right (Finset.erase_subset i d)
      have hd2 : Disjoint (c ∪ d.erase i) {i} := by
        rw [Finset.disjoint_singleton_right, Finset.mem_union, not_or]
        exact ⟨fun hc => Finset.disjoint_left.mp h hc hi, fun he => (Finset.mem_erase.mp he).1 rfl⟩
      have e1 := A.xup_small l c (d.erase i) hd1 (by rw [hcard]; omega) (by rw [hcard]; omega)
      have e2 := A.xup_small l (c ∪ d.erase i) {i} hd2 (by simp)
        (by rw [Finset.card_singleton]; omega)
      have e := e1.trans e2
      rw [erase_union' c d i hi] at e
      refine e.cast (fun φ => ?_)
      simp only [splitCost, if_neg h0, if_neg h2, hcard, Finset.card_singleton]

/-- One role moves DOWN by the lines `d`: exactly one block of rank `|d|` (two if `|d| = m`). -/
lemma xdown_step (hm : 2 ≤ Fintype.card α) (l : ρ) (c d : Finset α) (h : Disjoint c d) :
    XStep l (frame A (c ∪ d)) (frame A c)
      (fun φ => splitCost φ (Fintype.card α) d.card) := by
  by_cases h0 : d.card = 0
  · have hd : d = ∅ := Finset.card_eq_zero.mp h0
    subst hd
    rw [Finset.union_empty]
    exact (XStep.refl l _).cast (fun φ => by simp [splitCost])
  · by_cases h2 : d.card < Fintype.card α
    · exact (A.xdown_small l c d h (Nat.pos_of_ne_zero h0) h2).cast
        (fun φ => by simp [splitCost, h0, h2])
    · have hfull : d.card = Fintype.card α :=
        le_antisymm (Finset.card_le_univ d) (Nat.le_of_not_lt h2)
      obtain ⟨i, hi⟩ : d.Nonempty := Finset.card_pos.mp (Nat.pos_of_ne_zero h0)
      have hcard : (d.erase i).card = Fintype.card α - 1 := by
        rw [Finset.card_erase_of_mem hi, hfull]
      have hd1 : Disjoint c (d.erase i) := h.mono_right (Finset.erase_subset i d)
      have hd2 : Disjoint (c ∪ d.erase i) {i} := by
        rw [Finset.disjoint_singleton_right, Finset.mem_union, not_or]
        exact ⟨fun hc => Finset.disjoint_left.mp h hc hi, fun he => (Finset.mem_erase.mp he).1 rfl⟩
      have e1 := A.xdown_small l c (d.erase i) hd1 (by rw [hcard]; omega) (by rw [hcard]; omega)
      have e2 := A.xdown_small l (c ∪ d.erase i) {i} hd2 (by simp)
        (by rw [Finset.card_singleton]; omega)
      have e := e2.trans e1
      rw [erase_union' c d i hi] at e
      refine e.cast (fun φ => ?_)
      simp only [splitCost, if_neg h0, if_neg h2, hcard, Finset.card_singleton]
      ring

/-- **One role from frame `s` to frame `t`**: exactly a down-block of rank `|s \ t|` and an
up-block of rank `|t \ s|`. -/
lemma xreframe_step (hm : 2 ≤ Fintype.card α) (l : ρ) (s t : Finset α) :
    XStep l (frame A s) (frame A t)
      (fun φ => splitCost φ (Fintype.card α) (s \ t).card +
        splitCost φ (Fintype.card α) (t \ s).card) := by
  have hs : (s ∩ t) ∪ (s \ t) = s := by
    ext j; simp only [Finset.mem_union, Finset.mem_inter, Finset.mem_sdiff]; tauto
  have ht : (s ∩ t) ∪ (t \ s) = t := by
    ext j; simp only [Finset.mem_union, Finset.mem_inter, Finset.mem_sdiff]; tauto
  have hd1 : Disjoint (s ∩ t) (s \ t) :=
    Finset.disjoint_left.mpr (fun j hj hj' => (Finset.mem_sdiff.mp hj').2 (Finset.mem_inter.mp hj).2)
  have hd2 : Disjoint (s ∩ t) (t \ s) :=
    Finset.disjoint_left.mpr (fun j hj hj' => (Finset.mem_sdiff.mp hj').2 (Finset.mem_inter.mp hj).1)
  have e1 := A.xdown_step (ρ:=ρ) hm l (s ∩ t) (s \ t) hd1
  have e2 := A.xup_step (ρ:=ρ) hm l (s ∩ t) (t \ s) hd2
  rw [hs] at e1
  rw [ht] at e2
  exact e1.trans e2

end OBase
end
end
end PowerSaving.Binary

namespace PowerSaving.RAM
open Binary Matrix Finset
noncomputable section
section
variable {α ρ σ : Type*} [Fintype α] [DecidableEq α] [Fintype ρ] [DecidableEq ρ]
  [Fintype σ] [DecidableEq σ]

/-- **Exact block route.**  A proper block word that carries role `r` from the matrix `S r`
to the matrix `T r` while the scalar network does `g`, and whose cost is `c φ` for EVERY price
list `φ` (so `c` determines the block histogram of the word). -/
def XRoute (S T : ρ → CMat α) (g : (ρ→ℂ) → (ρ→ℂ)) (c : (ℕ → ℝ) → ℝ) : Prop :=
  ∃ w : BWord α ρ, w.Proper (Fintype.card α) ∧ (∀ φ, w.costR φ = c φ) ∧
    ∀ (f : ℕ) (x : Data α ρ f), walk f w.flat (multiAct f S x) = multiAct f T (point f g x)

/-- **Exact block path**: an exact block route between frames of fixed orthonormal bases. -/
abbrev XPath (A : ρ → OBase α) (s t : ρ → Finset α)
    (g : (ρ→ℂ) → (ρ→ℂ)) (c : (ℕ → ℝ) → ℝ) : Prop :=
  XRoute (fun r => frame (A r) (s r)) (fun r => frame (A r) (t r)) g c

namespace XRoute
variable {S T U : ρ → CMat α}

theorem refl : XRoute S S id (fun _ => 0) :=
  ⟨[], fun mv h => by simp at h, fun _ => rfl, fun f x => rfl⟩

theorem cast {g : (ρ→ℂ) → (ρ→ℂ)} {c c' : (ℕ → ℝ) → ℝ} (h : XRoute S T g c)
    (hc : ∀ φ, c φ = c' φ) : XRoute S T g c' := by
  obtain ⟨w, hw, hcost, hwalk⟩ := h
  exact ⟨w, hw, fun φ => (hcost φ).trans (hc φ), hwalk⟩

/-- An exact route is a block route (`Work.Block.Paths`) for every price list. -/
theorem toBRoute {g : (ρ→ℂ) → (ρ→ℂ)} {c : (ℕ → ℝ) → ℝ} (h : XRoute S T g c) (φ : ℕ → ℝ) :
    BRoute φ S T g (c φ) := by
  obtain ⟨w, hw, hcost, hwalk⟩ := h
  exact ⟨w, hw, (hcost φ).le, hwalk⟩

theorem trans {g h : (ρ→ℂ) → (ρ→ℂ)} {c c' : (ℕ → ℝ) → ℝ} (a : XRoute S T g c)
    (b : XRoute T U h c') : XRoute S U (h ∘ g) (fun φ => c φ + c' φ) := by
  obtain ⟨p,hp,cp,ap⟩ := a
  obtain ⟨q,hq,cq,aq⟩ := b
  refine ⟨p++q, hp.append hq, fun φ => by rw [BWord.costR_append, cp, cq], ?_⟩
  intro f x
  rw [BWord.flat_append, walk_append, ap, aq]; rfl

/-- **Copy / overwrite / erase gate** (no block). -/
theorem gate (g : Matrix ρ ρ ℚ) (S T : ρ → CMat α)
    (cond : ∀ i j, g i j ≠ 0 → T i = S j) :
    XRoute S T (actPoint g) (fun _ => 0) := by
  refine ⟨[.localM g], ?_, ?_, ?_⟩
  · intro mv hmv
    simp only [List.mem_cons, List.not_mem_nil, or_false] at hmv
    subst hmv; trivial
  · intro φ
    simp [BWord.costR, BMove.costR, BMove.rk?]
  intro f x
  rw [show BWord.flat [BMove.localM g] = [Move.localM g] from rfl]
  let M (r : ρ) := digitProd (fun _ : Fin f => S r)
  let N (r : ρ) := digitProd (fun _ : Fin f => T r)
  funext r i
  change ∑ j, (g r j:ℂ)* (∑ a, M j i a * x j a)
    = ∑ a, N r i a * (∑ j, (g r j:ℂ)*x j a)
  simp only [mul_sum]
  rw [sum_comm]
  apply sum_congr rfl
  intro a ha
  apply sum_congr rfl
  intro j hj
  by_cases gh : g r j = 0
  · simp [gh]
  · dsimp only [M, N]
    rw [cond r j gh]
    ac_rfl

/-- A block word on one role moves the matrix of that role only. -/
theorem on_role (S : ρ → CMat α) (l : ρ) (N : CMat α) {c : (ℕ → ℝ) → ℝ}
    (h : XStep l (S l) N c) :
    XRoute S (Function.update S l N) id c := by
  obtain ⟨w, V, hw, hc, hV, hwalk⟩ := h
  refine ⟨w, hw, hc, fun f x => ?_⟩
  rw [hwalk, show point f id x = x from rfl]
  funext j
  by_cases hj : j = l
  · subst hj
    simp [roleAct, multiAct, hV]
  · simp [roleAct, multiAct, hj]

/-- Every unit-move `Route` is an exact block route: each directional move a block of rank
one. -/
theorem of_route (hm : 2 ≤ Fintype.card α) {g : (ρ→ℂ) → (ρ→ℂ)} {c : ℕ}
    (h : Route S T g c) : XRoute S T g (fun φ => (c:ℝ) * φ 1) := by
  obtain ⟨p, hp, hw⟩ := h
  refine ⟨BWord.ofPWord p, BWord.proper_ofPWord _ hm p, ?_, ?_⟩
  · intro φ
    rw [BWord.costR_ofPWord, hp]
  · intro f x
    rw [BWord.flat_ofPWord]
    exact hw f x

/-- Free translations of all roles (upstream `translateAll`): no block. -/
theorem shifts (hm : 2 ≤ Fintype.card α) (S : ρ → CMat α) (z : ρ → Space α) :
    XRoute S (fun r => shift (z r) * S r) id (fun _ => 0) := by
  obtain ⟨p, hp, hw⟩ := translateAll (ρ := ρ) z
  refine ⟨BWord.ofPWord p, BWord.proper_ofPWord _ hm p, ?_, ?_⟩
  · intro φ
    rw [BWord.costR_ofPWord, hp]; simp
  · intro f x
    rw [BWord.flat_ofPWord, hw, show point f id x = x from rfl]
    funext r
    simp [multiAct]

/-- Re-index a route on a sub-network of roles (as upstream `Path.lift`). -/
theorem lift (e : ρ ↪ σ) {S T : σ → CMat α}
    {g : (σ→ℂ) → (σ→ℂ)} {h : (ρ→ℂ) → (ρ→ℂ)} {c : (ℕ → ℝ) → ℝ}
    (q : XRoute (S ∘ e) (T ∘ e) h c)
    (hin : ∀ x, (g x) ∘ e = h (x ∘ e)) (hout : ∀ x i, i∉covered e → g x i=x i)
    (he : ∀ i, i∉covered e → S i = T i) :
    XRoute S T g c := by
  obtain ⟨w,hw,hc,ha⟩ := q
  refine ⟨w.map (BMove.over e), BWord.proper_over _ e w hw,
    fun φ => by rw [BWord.costR_over]; exact hc φ, ?_⟩
  intro f x
  rw [BWord.flat_over]
  have frame_cont (S : σ → CMat α) (x : Data α σ f) :
      multiAct f S x ∘ e = multiAct f (S∘e) (x∘e) := rfl
  have point_cont :
      point f g x ∘ e = point f h (x ∘ e) := by
    funext i j
    exact congr_fun (hin _) i
  funext i
  by_cases hm : i∈covered e
  · obtain ⟨j,rfl⟩ := (cover_iff ..).mp hm
    exact congr_fun (show walk f _ _ ∘ e = multiAct f T _ ∘ e by
      rw [walk_over,frame_cont, ha,frame_cont,point_cont]) j
  · rw [walk_out e w.flat _ _ hm]
    unfold multiAct
    simp only [he i hm]
    apply congrArg
    funext j
    exact (hout (fun r => x r j) i hm).symm

section Parallel
variable {J : Type*} [Fintype J] [DecidableEq J]

/-- Compose routes on disjoint sets of roles (as upstream `Path.parallel`); costs add. -/
theorem parallel (e : J → ρ ↪ σ)
    (dis : ∀ i j, i ≠ j → ∀ r ∈ covered (e i), r ∉ covered (e j))
    {S T : σ → CMat α} {d : J → (ℕ → ℝ) → ℝ}
    {g : (σ→ℂ)→(σ→ℂ)} {h : J → (ρ→ℂ) → (ρ→ℂ)}
    (q : ∀ i, XRoute (S ∘ e i) (T ∘ e i) (h i) (d i))
    (hin : ∀ i x, (g x) ∘ e i = h i (x ∘ e i))
    (hout : ∀ x r, (∀ i, r∉covered (e i)) → g x r=x r)
    (he : ∀ r, (∀ i, r∉covered (e i)) → S r=T r) :
    XRoute S T g (fun φ => ∑ i, d i φ) := by
  let u (j : Finset J) := j.biUnion fun i => covered (e i)
  let l (j : Finset J) (r : σ) := if r∈u j then T r else S r
  let k (j : Finset J) (x : σ→ℂ) (r : σ) := if r∈u j then g x r else x r
  have hh (j : Finset J) : XRoute S (l j) (k j) (fun φ => ∑ i ∈ j, d i φ) := by
    induction j using Finset.induction with
    | empty =>
      simp only [k,l,u,biUnion_empty,notMem_empty,ite_false,sum_empty]
      exact XRoute.refl
    | insert i j hi ih =>
      have hiu (r) (hr : r∈covered (e i)) : r ∉ u j := by
        intro hg
        obtain ⟨w,hw,he'⟩ := mem_biUnion.mp hg
        have hw' : i ≠ w := fun hh => hi (hh ▸ hw)
        exact dis _ _ hw' r hr he'
      have hui (r) : r∈u (insert i j) ↔ r∈covered (e i) ∨ r∈u j := by
        simp [u]
      let fn (x : σ→ℂ) (r : σ) := if r∈covered (e i) then g x r else x r
      have compi (x) : fn x ∘ e i = h i (x∘e i) := by
        rw [← hin]
        funext j; simp [fn,covered]
      have gg : XRoute (l j) (l (insert i j)) fn (d i) := by
        apply XRoute.lift (e i) (h:=h i) _ compi
        · intro x l hl; simp [fn,hl]
        · intro r hr; simp [l,hui,hr]
        · have eq1 : l j ∘ e i = S ∘ e i := by
            funext r
            have h : e i r ∈ covered (e i) := by simp [covered]
            simp [l, hiu _ h]
          have eq2 : l (insert i j) ∘ e i = T ∘ e i := by
            funext r
            have h : e i r ∈ covered (e i) := by simp [covered]
            simp [l,hui,h]
          rw [eq1,eq2]; apply q
      have cmp : fn ∘ k j = k (insert i j) := by
        funext x r
        by_cases hqr : r ∈ covered (e i)
        · obtain ⟨r,rfl⟩ := (cover_iff ..).mp hqr
          change fn (k j x) _ = _
          have eq : k j x ∘ e i = x ∘ e i := by
            funext r
            have h : e i r ∈ covered (e i) := by simp [covered]
            simp [k,hiu _ h]
          have H := congr_fun (show fn (k j x) ∘ e i = g x ∘ e i by rw [compi,eq,hin]) r
          exact H.trans (by simp [k,hui,hqr])
        · simp [Function.comp,k,fn,hui,hqr]
      rw [← cmp]
      exact (ih.trans gg).cast (fun φ => by rw [sum_insert hi, add_comm])
  have ha (r) : r∉u univ ↔ ∀ i, r∉covered (e i) := by simp [u]
  have eq1 : l univ = T := by
    funext r; by_cases h : r∈u univ
    · simp [l,h]
    · simp [l,h,he r ((ha r).1 h)]
  have eq2 : k univ = g := by
    funext x r; by_cases h : r∈u univ
    · simp [k,h]
    · simp [k,h,hout x r ((ha r).1 h)]
  have H := hh univ
  rwa [eq1,eq2] at H

end Parallel

/-- **Assembling a scratch certificate in block form from an exact route** (as
`BRoute.liveKernel`), keeping the exact cost. -/
theorem liveKernel (e : σ → ρ) (S S' T : ρ → CMat α) (hS : ∀ r, S r * S' r = 1)
    (g : (ρ→ℂ) → (ρ→ℂ)) (c : (ℕ → ℝ) → ℝ) (h : XRoute S T g c)
    (hg : ∀ x : ρ → ℂ, (∀ s, (∀ l, e l ≠ s) → x s = 0) → ∀ l, g x (e l) = x (e l))
    (hT : ∀ l, T (e l) = kernel α * S (e l)) :
    ∃ w : BWord α ρ, w.Proper (Fintype.card α) ∧ (∀ φ, w.costR φ = c φ) ∧
      LiveKernel e w.flat := by
  obtain ⟨w,hp,hc,hw⟩ := h
  refine ⟨w, hp, hc, ?_⟩
  intro f v hv l
  let y : Data α ρ f := multiAct f S' v
  have hy : multiAct f S y = v := by
    funext r; simp [y, multiAct, hS]
  have hy0 (s : ρ) (hs : ∀ l, e l ≠ s) : y s = 0 := by
    change matAct f (S' s) (v s) = 0
    rw [hv s hs]; exact matAct_zero f _
  have hpt : point f g y (e l) = y (e l) := by
    funext i
    exact hg (fun r => y r i) (fun s hs => by rw [hy0 s hs]; rfl) l
  have h1 := congrFun (hw f y) (e l)
  rw [hy] at h1
  rw [h1]
  change matAct f (T (e l)) (point f g y (e l)) = _
  rw [hpt, hT, ← matAct_mul]
  exact congrArg _ (congrFun hy (e l))

end XRoute

namespace XPath
variable {A : ρ → OBase α} {s t u : ρ → Finset α}

theorem refl : XPath A s s id (fun _ => 0) := XRoute.refl

theorem cast {g : (ρ→ℂ) → (ρ→ℂ)} {c c' : (ℕ → ℝ) → ℝ} (h : XPath A s t g c)
    (hc : ∀ φ, c φ = c' φ) : XPath A s t g c' := XRoute.cast h hc

theorem trans {g h : (ρ→ℂ) → (ρ→ℂ)} {c c' : (ℕ → ℝ) → ℝ} (a : XPath A s t g c)
    (b : XPath A t u h c') : XPath A s u (h ∘ g) (fun φ => c φ + c' φ) := XRoute.trans a b

/-- Move through a gate whose nonzero entries stay within a common frame (as upstream
`Path.gate`); no block. -/
theorem gate (g : Matrix ρ ρ ℚ)
    (cond : ∀ i j, g i j ≠ 0 → frame (A i) (s i) = frame (A j) (s j)) :
    XPath A s s (actPoint g) (fun _ => 0) :=
  XRoute.gate g _ _ cond

/-- **Reframe with blocks, exact count**: every role pays exactly one down-block of rank
`|s r \ t r|` and one up-block of rank `|t r \ s r|` (a residual of full rank `m` is split
`(m-1)+1`, a residual of rank `0` is no block). -/
theorem reframe (hm : 2 ≤ Fintype.card α) (A : ρ → OBase α) (s t : ρ → Finset α) :
    XPath A s t id (fun φ => ∑ r, (splitCost φ (Fintype.card α) (s r \ t r).card +
      splitCost φ (Fintype.card α) (t r \ s r).card)) := by
  have hh (J : Finset ρ) :
      XPath A s (fun r => if r ∈ J then t r else s r) id
        (fun φ => ∑ r ∈ J, (splitCost φ (Fintype.card α) (s r \ t r).card +
          splitCost φ (Fintype.card α) (t r \ s r).card)) := by
    induction J using Finset.induction_on with
    | empty =>
      have e0 : (fun r => if r ∈ (∅ : Finset ρ) then t r else s r) = s := by
        funext r; simp
      rw [e0]
      exact XRoute.refl.cast (fun φ => by simp)
    | insert l J hl ih =>
      have hsl : (if l ∈ J then t l else s l) = s l := if_neg hl
      have step : XStep l (frame (A l) (if l ∈ J then t l else s l)) (frame (A l) (t l))
          (fun φ => splitCost φ (Fintype.card α) (s l \ t l).card +
            splitCost φ (Fintype.card α) (t l \ s l).card) := by
        rw [hsl]; exact (A l).xreframe_step hm l (s l) (t l)
      have b := XRoute.on_role
        (fun r => frame (A r) (if r ∈ J then t r else s r)) l (frame (A l) (t l)) step
      have hupd : Function.update (fun r => frame (A r) (if r ∈ J then t r else s r)) l
          (frame (A l) (t l)) =
          fun r => frame (A r) (if r ∈ insert l J then t r else s r) := by
        funext r
        by_cases hr : r = l
        · subst hr; simp
        · simp [Function.update_of_ne hr, Finset.mem_insert, hr]
      rw [hupd] at b
      exact (ih.trans b).cast (fun φ => by rw [Finset.sum_insert hl, add_comm])
  have H := hh Finset.univ
  have e1 : (fun r => if r ∈ (Finset.univ : Finset ρ) then t r else s r) = t := by
    funext r; simp
  rw [e1] at H
  exact H

/-- Growing frames: exactly one up-block per role whose frame grows. -/
theorem inc (hm : 2 ≤ Fintype.card α) (A : ρ → OBase α) {s t : ρ → Finset α}
    (h : ∀ r, s r ⊆ t r) :
    XPath A s t id (fun φ => ∑ r, splitCost φ (Fintype.card α) (t r \ s r).card) := by
  refine (reframe hm A s t).cast (fun φ => ?_)
  apply Finset.sum_congr rfl
  intro r _
  have h0 : s r \ t r = ∅ := Finset.sdiff_eq_empty_iff_subset.mpr (h r)
  rw [h0]
  simp [splitCost]

/-- Same argument list as upstream `Path.lift` (FrameLifting.lean:102). -/
theorem lift (e : ρ ↪ σ) (A : σ → OBase α) {s t : σ → Finset α}
    {g : (σ→ℂ) → (σ→ℂ)} {h : (ρ→ℂ) → (ρ→ℂ)} {c : (ℕ → ℝ) → ℝ}
    (q : XPath (A ∘ e) (s ∘ e) (t ∘ e) h c)
    (hin : ∀ x, (g x) ∘ e = h (x ∘ e)) (hout : ∀ x i, i∉covered e → g x i=x i)
    (he : ∀ i, i∉covered e → s i = t i) :
    XPath A s t g c :=
  XRoute.lift e (S:=fun r => frame (A r) (s r)) (T:=fun r => frame (A r) (t r)) q hin hout
    (fun i hi => by
      change frame (A i) (s i) = frame (A i) (t i)
      rw [he i hi])

/-- Same argument list as upstream `Path.parallel` (FrameLifting.lean:146); costs add. -/
theorem parallel {J : Type*} [Fintype J] [DecidableEq J] (e : J → ρ ↪ σ)
    (dis : ∀ i j, i ≠ j → ∀ r ∈ covered (e i), r ∉ covered (e j))
    (A : σ → OBase α) {s t : σ → Finset α} {d : J → (ℕ → ℝ) → ℝ}
    {g : (σ→ℂ)→(σ→ℂ)} {h : J → (ρ→ℂ) → (ρ→ℂ)}
    (q : ∀ i, XPath (A ∘ e i) (s ∘ e i) (t ∘ e i) (h i) (d i))
    (hin : ∀ i x, (g x) ∘ e i = h i (x ∘ e i))
    (hout : ∀ x r, (∀ i, r∉covered (e i)) → g x r=x r)
    (he : ∀ r, (∀ i, r∉covered (e i)) → s r=t r) :
    XPath A s t g (fun φ => ∑ i, d i φ) :=
  XRoute.parallel e dis (S:=fun r => frame (A r) (s r)) (T:=fun r => frame (A r) (t r)) q hin
    hout (fun r hr => by
      change frame (A r) (s r) = frame (A r) (t r)
      rw [he r hr])

end XPath
end

universe U

/-- **The block engine fed with a word whose blocks are those of a list `L`.**  `w` is a
scratch certificate in block form (`LiveKernel e w.flat`), its cost is the price of the list
`L` for every price list (hence `w.hist = histFn L`, `BWord.hist_of_listCost`), and `L`
satisfies the strict moment inequality.  Conclusion: upstream's `hills_program` statement with
envelope `⌈(k+1)^z⌉`. -/
theorem engine_program_xcert {α ρ σ : Type} [Fintype α] [DecidableEq α] [Fintype ρ]
    [DecidableEq ρ] [Fintype σ] [DecidableEq σ]
    (u a : ℕ) (hα : Fintype.card α = u) (hσ : Fintype.card σ = 2^a) (hu : 3 ≤ u)
    (e : σ → ρ) (he : Function.Injective e)
    (w : BWord α ρ) (hw : LiveKernel e w.flat) (hP : w.Proper u)
    (L : List (ℕ × ℕ)) (hL : ∀ φ : ℕ → ℝ, w.costR φ = listCost φ L)
    (z : ℝ) (hz : 0 ≤ z)
    (hmom : BlockAccounting.moment u z L < (2:ℝ)^a)
    (cl : Paint) (m : Bool) {ι : Type U} (k : ι→ℕ) (v : ∀ i, Bits (k i) → ℂ) :
    Can m (fun i => 2^k i) (simIn cl) (bundle cl)
      (fun i => givenBits cl (k i) (v i)) (fun i => (bits (k i)).tape (ripple (k i) (v i)))
      (fun i => 2^k i*envelope z (k i)) := by
  refine engine_program_block u a hα hσ hu e he w hw hP (BlockAccounting.histFn L)
    (fun r => (BWord.hist_of_listCost w L hL r).le) (BlockAccounting.keys L)
    (BlockAccounting.mem_keys_of_histFn_ne_zero L) z hz ?_ cl m k v
  rw [BlockAccounting.moment_finset]
  exact hmom

end
end PowerSaving.RAM
end OAI

#print axioms OAI.PowerSaving.Binary.BWord.hist_of_listCost
#print axioms OAI.PowerSaving.Binary.OBase.xreframe_step
#print axioms OAI.PowerSaving.RAM.XRoute.parallel
#print axioms OAI.PowerSaving.RAM.XRoute.liveKernel
#print axioms OAI.PowerSaving.RAM.XPath.reframe
#print axioms OAI.PowerSaving.RAM.engine_program_xcert
