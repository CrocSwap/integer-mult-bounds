import Nov15.NumCertK
import Nov15.CTreeCore

/-!
CONGESTION-TREE-CORE.  Abstract part of the node-partition (whole-meeting) tree bound and its port-realised refinement:
* soundness of the kernel-checked DP rows (`Row.check`, file `CTreeCore`) as lower bounds `G(x,k)` for the cost of out-trees;
* the inductive predicate `Tr` (an out-tree of charts: shapes in a given shape list, children = nested moves, readers covered);
* `tree_cost_ge` : a `Tr` tree delivering `R` readers from shape `r` costs at least `G(r, |R|) / SC` (each edge charged `w e / nm e`);
* `reduction` : double counting (every move carries at most `nm e` sources) `sum_s tree_s <= sum_e w e`;
* `tree_lower` : the Lagrange/line bound over the 104 sources with `sum |J_s| >= 4962`, `|J_s| <= 48`, transported cells pay `cap`.
No sorry, no native_decide.
-/
namespace CTree
open Finset

def SCn : ℕ := 10 ^ 14
noncomputable def SCr : ℝ := 10 ^ 14

def gv (r : Row) (k : ℕ) : ℕ := r.g.getD k 0

theorem rowLe_sound : ∀ (a b : List ℕ) (w : ℕ), rowLe a b w = true →
    ∀ j, j < b.length → j < a.length → a.getD j 0 ≤ w + b.getD j 0 := by
  intro a
  induction a with
  | nil => intro b w _ j _ hj; simp at hj
  | cons a as ih =>
    intro b w h j hjb hja
    cases b with
    | nil => simp at hjb
    | cons b bs =>
      simp only [rowLe, Bool.and_eq_true, decide_eq_true_eq] at h
      cases j with
      | zero => simpa using h.1
      | succ j =>
        have := ih bs w h.2 j (by simpa using hjb) (by simpa using hja)
        simpa using this

theorem monoB_adj : ∀ (l : List ℕ), monoB l = true → ∀ i, i + 1 < l.length → l.getD i 0 ≤ l.getD (i + 1) 0 := by
  intro l
  induction l with
  | nil => intro _ i hi; simp at hi
  | cons a t ih =>
    intro h i hi
    cases t with
    | nil => simp at hi
    | cons b t' =>
      simp only [monoB, Bool.and_eq_true, decide_eq_true_eq] at h
      cases i with
      | zero => simpa using h.1
      | succ i => simpa using ih h.2 i (by simpa using hi)

theorem monoB_mono (l : List ℕ) (h : monoB l = true) : ∀ i j, i ≤ j → j < l.length → l.getD i 0 ≤ l.getD j 0 := by
  intro i j hij hj
  induction j, hij using Nat.le_induction with
  | base => exact le_refl _
  | succ j hij ih => exact le_trans (ih (by omega)) (monoB_adj l h j hj)

theorem getD_zero_of_all (l : List ℕ) (h : ∀ v ∈ l, v = 0) (k : ℕ) : l.getD k 0 = 0 := by
  by_cases hk : k < l.length
  · rw [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem hk]; exact h _ (List.getElem_mem hk)
  · rw [List.getD_eq_getElem?_getD, List.getElem?_eq_none (by omega)]; rfl

/-- the facts packed in `Row.check` -/
structure RowOK (W : List (List ℕ)) (rs : List Row) (r : Row) : Prop where
  dim1 : 1 ≤ r.dim
  dim8 : r.dim ≤ 8
  n1 : 1 ≤ r.n
  glen : r.g.length = r.m + 1
  gelen : r.ge.length = r.m + 1
  g0 : r.g.getD 0 0 = 0
  mono : monoB r.g = true
  leaf : r.dim = 8 → r.m ≤ 1 ∧ ∀ v ∈ r.g, v = 0
  edge : r.dim ≠ 8 → ∀ r' ∈ rs, r.ok r' = true → rowLe (r.ge.drop 1) (r'.g.drop 1) (ew W r r') = true
  c4 : r.dim ≠ 8 → r.c4 = true

theorem rowOK_of_check (W : List (List ℕ)) (rs : List Row) (r : Row) (h : r.check W rs = true) : RowOK W rs r := by
  unfold Row.check at h
  simp only [Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq] at h
  obtain ⟨⟨⟨⟨⟨⟨⟨h1, h2⟩, h3⟩, h4⟩, h5⟩, h6⟩, h7⟩, h8⟩ := h
  refine ⟨h1, h2, h3, h4, h5, h6, h7, ?_, ?_, ?_⟩
  · intro h8'
    rw [if_pos h8'] at h8
    simp only [Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, beq_iff_eq] at h8
    exact ⟨h8.1, h8.2⟩
  · intro hne r' hr' hok
    rw [if_neg hne] at h8
    simp only [Bool.and_eq_true, List.all_eq_true] at h8
    have := h8.1 r' hr'
    simp only [Bool.or_eq_true, Bool.not_eq_true'] at this
    rcases this with h | h
    · rw [h] at hok; exact absurd hok (by simp)
    · exact h
  · intro hne
    rw [if_neg hne] at h8
    simp only [Bool.and_eq_true] at h8
    exact h8.2

theorem gv_zero {W rs r} (h : RowOK W rs r) : gv r 0 = 0 := h.g0

theorem gv_mono {W rs r} (h : RowOK W rs r) {i j : ℕ} (hij : i ≤ j) (hj : j ≤ r.m) : gv r i ≤ gv r j :=
  monoB_mono r.g h.mono i j hij (by rw [h.glen]; omega)

theorem edge_sem {W rs r} (hr : RowOK W rs r) (hne : r.dim ≠ 8) {r' : Row} (hr' : r' ∈ rs) (hr'ok : RowOK W rs r')
    (hok : r.ok r' = true) {j : ℕ} (hj1 : 1 ≤ j) (hj : j ≤ r'.m) :
    r.ge.getD j 0 ≤ ew W r r' + gv r' j := by
  have hm : r'.m ≤ r.m := by
    simp only [Row.ok, Bool.and_eq_true, decide_eq_true_eq] at hok; exact hok.1.2
  have := rowLe_sound _ _ _ (hr.edge hne r' hr' hok) (j - 1) (by simp [List.length_drop, hr'ok.glen]; omega)
    (by simp [List.length_drop, hr.gelen]; omega)
  have e1 : (r.ge.drop 1).getD (j - 1) 0 = r.ge.getD j 0 := by
    simp [List.getD_eq_getElem?_getD, List.getElem?_drop]; congr 2; omega
  have e2 : (r'.g.drop 1).getD (j - 1) 0 = gv r' j := by
    simp [gv, List.getD_eq_getElem?_getD, List.getElem?_drop]; congr 2; omega
  rw [e1, e2] at this; exact this

theorem c4_sem {r : Row} (h : r.c4 = true) {k : ℕ} (hk1 : 1 ≤ k) (hk : k ≤ r.m) {j : ℕ} (hj1 : 1 ≤ j) (hjk : j ≤ k) :
    gv r k ≤ r.ge.getD j 0 + gv r (k - j) := by
  unfold Row.c4 at h
  simp only [List.all_eq_true, List.mem_range, decide_eq_true_eq] at h
  have := h (k - 1) (by omega) (j - 1) (by omega)
  have e1 : k - 1 + 1 = k := by omega
  have e2 : j - 1 + 1 = j := by omega
  have e3 : k - 1 - (j - 1) = k - j := by omega
  rw [e1, e2, e3] at this; exact this

theorem list_card_foldr (l : List (Finset ρ)) [DecidableEq ρ] : (l.foldr (· ∪ ·) ∅).card ≤ (l.map Finset.card).sum := by
  induction l with
  | nil => simp
  | cons a t ih =>
    simp only [List.foldr_cons, List.map_cons, List.sum_cons]
    exact le_trans (Finset.card_union_le _ _) (by omega)

/-- the DP step: children `(row, count, cost)` deliver `k` readers at cost at least `G(r,k)` (costs in units of 1/SC). -/
theorem step {W rs r} (hr : RowOK W rs r) (hne : r.dim ≠ 8) (cs : List (Row × ℕ × ℝ))
    (hcs : ∀ c ∈ cs, c.1 ∈ rs ∧ RowOK W rs c.1 ∧ r.ok c.1 = true ∧ c.2.1 ≤ c.1.m ∧
      (((ew W r c.1 + gv c.1 c.2.1 : ℕ)) : ℝ) ≤ c.2.2) :
    ∀ k, k ≤ r.m → k ≤ (cs.map fun c => c.2.1).sum → ((gv r k : ℕ) : ℝ) ≤ (cs.map fun c => c.2.2).sum := by
  induction cs with
  | nil =>
    intro k _ hk
    simp at hk
    subst hk
    simp [gv_zero hr]
  | cons c cs ih =>
    intro k hkm hk
    simp only [List.map_cons, List.sum_cons] at hk ⊢
    have hc := hcs c (by simp)
    have hcs' : ∀ c' ∈ cs, c'.1 ∈ rs ∧ RowOK W rs c'.1 ∧ r.ok c'.1 = true ∧ c'.2.1 ≤ c'.1.m ∧
      (((ew W r c'.1 + gv c'.1 c'.2.1 : ℕ)) : ℝ) ≤ c'.2.2 := fun c' hc' => hcs c' (by simp [hc'])
    have ih' := ih hcs'
    have hnn : ∀ l : List (Row × ℕ × ℝ), (∀ c' ∈ l, (0 : ℝ) ≤ c'.2.2) → 0 ≤ (l.map fun c => c.2.2).sum := by
      intro l hl
      induction l with
      | nil => simp
      | cons a t iht =>
        simp only [List.map_cons, List.sum_cons]
        have h1 := hl a (by simp)
        have h2 := iht (fun c' hc' => hl c' (by simp [hc']))
        linarith
    have hcost0 : ∀ c' ∈ cs, (0 : ℝ) ≤ c'.2.2 := fun c' hc' => le_trans (Nat.cast_nonneg _) (hcs' c' hc').2.2.2.2
    have hS0 := hnn cs hcost0
    have hc0 : (0 : ℝ) ≤ c.2.2 := le_trans (Nat.cast_nonneg _) hc.2.2.2.2
    by_cases hk0 : k = 0
    · subst hk0; simp [gv_zero hr]; linarith
    by_cases hcnt : c.2.1 = 0
    · have := ih' k hkm (by omega)
      linarith
    · set j := min k c.2.1 with hj
      have hj1 : 1 ≤ j := by omega
      have hjk : j ≤ k := min_le_left _ _
      have hjc : j ≤ c.2.1 := min_le_right _ _
      have h4 := c4_sem (hr.c4 hne) (by omega) hkm hj1 hjk
      have he := edge_sem hr hne hc.1 hc.2.1 hc.2.2.1 hj1 (le_trans hjc hc.2.2.2.1)
      have hmo := gv_mono hc.2.1 hjc hc.2.2.2.1
      have ih2 := ih' (k - j) (by omega) (by omega)
      have hnat : gv r k ≤ ew W r c.1 + gv c.1 c.2.1 + gv r (k - j) := by omega
      have hr' : ((gv r k : ℕ) : ℝ) ≤ ((ew W r c.1 + gv c.1 c.2.1 : ℕ) : ℝ) + ((gv r (k - j) : ℕ) : ℝ) := by
        exact_mod_cast hnat
      have := hc.2.2.2.2
      linarith

variable {ρ μ : Type} [DecidableEq ρ]

/-- out-trees of charts.  A node is a chart of shape `r` (a row of the shape list `rs`), delivering readers `R`;
its children are `(row, readers, move, moves-below)`; the edge to a child is the move `e` with source capacity `nm e = n(r)`
and dimensions `dA e = dim r`, `dB e = dim child`.  `moves` lists the moves of the tree (edge, then the subtree). -/
inductive Tr (rs : List Row) (nm dA dB : μ → ℕ) : Row → Finset ρ → List μ → Prop
  | node (r : Row) (R : Finset ρ) (ch : List (Row × Finset ρ × μ × List μ))
      (hr : r ∈ rs)
      (hsub : ∀ c ∈ ch, Tr rs nm dA dB c.1 c.2.1 c.2.2.2)
      (hside : ∀ c ∈ ch, c.1 ∈ rs ∧ r.ok c.1 = true ∧ nm c.2.2.1 = r.n ∧ dA c.2.2.1 = r.dim ∧
        dB c.2.2.1 = c.1.dim ∧ c.2.1.card ≤ c.1.m)
      (hm : R.card ≤ r.m)
      (hcov : r.dim ≠ 8 → R ⊆ (ch.map fun c => c.2.1).foldr (· ∪ ·) ∅) :
      Tr rs nm dA dB r R (ch.flatMap fun c => c.2.2.1 :: c.2.2.2)

theorem sum_flatMap_eq (ch : List (Row × Finset ρ × μ × List μ)) (f : μ → ℝ) :
    (((ch.flatMap fun c => c.2.2.1 :: c.2.2.2).map f).sum) =
      (ch.map fun c => f c.2.2.1 + ((c.2.2.2.map f).sum)).sum := by
  induction ch with
  | nil => simp
  | cons c t ih => simp [List.flatMap_cons, List.map_append, List.sum_append, ih]; ring

/-- **tree DP lower bound**: a tree from shape `r` delivering `R` costs at least `G(r,|R|)/SC`, edge `e` charged `w e / nm e`. -/
theorem tree_cost_ge (W : List (List ℕ)) (rs : List Row) (hcert : ∀ r ∈ rs, r.check W rs = true)
    (nm dA dB : μ → ℕ) (w : μ → ℝ)
    (hW : ∀ e, 1 ≤ dA e → dA e < dB e → dB e ≤ 8 → (((W.getD (dA e) []).getD (dB e) 0 : ℕ) : ℝ) ≤ SCr * w e)
    {r : Row} {R : Finset ρ} {ms : List μ} (h : Tr rs nm dA dB r R ms) :
    ((gv r R.card : ℕ) : ℝ) ≤ SCr * (ms.map fun e => w e / nm e).sum := by
  induction h with
  | node r R ch hr hsub hside hm hcov ih =>
    have hro := rowOK_of_check W rs r (hcert r hr)
    by_cases h8 : r.dim = 8
    · have hch : ch = [] := by
        cases ch with
        | nil => rfl
        | cons c t =>
          exfalso
          have h1 := hside c (by simp)
          have hco := rowOK_of_check W rs c.1 (hcert c.1 h1.1)
          have h3 := h1.2.1
          simp only [Row.ok, Bool.and_eq_true, decide_eq_true_eq] at h3
          have := hco.dim8
          omega
      subst hch
      have hz := getD_zero_of_all r.g (hro.leaf h8).2 R.card
      have hz' : gv r R.card = 0 := hz
      rw [hz']; simp
    · set F : Row × Finset ρ × μ × List μ → ℝ := fun c => w c.2.2.1 / nm c.2.2.1 + (c.2.2.2.map fun e => w e / nm e).sum with hF
      set cs : List (Row × ℕ × ℝ) := ch.map fun c => (c.1, c.2.1.card, SCr * F c) with hcs
      have key := step hro h8 cs ?_ R.card hm ?_
      · rw [sum_flatMap_eq]
        have e1 : (cs.map fun c => c.2.2).sum = SCr * (ch.map F).sum := by
          rw [hcs, List.map_map]
          have : ((fun c : Row × ℕ × ℝ => c.2.2) ∘ fun c : Row × Finset ρ × μ × List μ => (c.1, c.2.1.card, SCr * F c)) =
              fun c => SCr * F c := rfl
          rw [this, List.sum_map_mul_left]
        rw [e1] at key
        exact key
      · intro c' hc'
        rw [hcs, List.mem_map] at hc'
        obtain ⟨c0, hc0, rfl⟩ := hc'
        have hs := hside c0 hc0
        have hco := rowOK_of_check W rs c0.1 (hcert c0.1 hs.1)
        have hokc := hs.2.1
        have hd : r.dim < c0.1.dim := by
          simp only [Row.ok, Bool.and_eq_true, decide_eq_true_eq] at hokc; exact hokc.1.1.1
        have hwe := hW c0.2.2.1 (by rw [hs.2.2.2.1]; exact hro.dim1) (by rw [hs.2.2.2.1, hs.2.2.2.2.1]; exact hd)
          (by rw [hs.2.2.2.2.1]; exact hco.dim8)
        rw [hs.2.2.2.1, hs.2.2.2.2.1] at hwe
        have hn : (0 : ℝ) < r.n := by exact_mod_cast hro.n1
        have hdiv : ((ew W r c0.1 : ℕ) : ℝ) ≤ SCr * (w c0.2.2.1 / nm c0.2.2.1) := by
          have h1 : ((ew W r c0.1 : ℕ) : ℝ) ≤ (((W.getD r.dim []).getD c0.1.dim 0 : ℕ) : ℝ) / r.n := Nat.cast_div_le
          have h2 : SCr * (w c0.2.2.1 / nm c0.2.2.1) = SCr * w c0.2.2.1 / r.n := by rw [hs.2.2.1]; ring
          rw [h2]
          exact le_trans h1 (div_le_div_of_nonneg_right hwe hn.le)
        have hih := ih c0 hc0
        refine ⟨hs.1, hco, hokc, hs.2.2.2.2.2, ?_⟩
        show (((ew W r c0.1 + gv c0.1 c0.2.1.card : ℕ)) : ℝ) ≤ SCr * F c0
        push_cast
        rw [hF]; simp only []
        rw [mul_add]
        linarith
      · have h1 : R ⊆ _ := hcov h8
        have h2 := le_trans (Finset.card_le_card h1) (list_card_foldr (ch.map fun c => c.2.1))
        have : (cs.map fun c => c.2.1) = ch.map fun c => c.2.1.card := by simp [hcs, List.map_map]
        have h3 : (((ch.map fun c => c.2.1)).map Finset.card).sum = (ch.map fun c => c.2.1.card).sum := by
          simp [List.map_map, Function.comp_def]
        rw [this, ← h3]
        exact h2


theorem Tr.card_le {rs : List Row} {nm dA dB : μ → ℕ} {r : Row} {R : Finset ρ} {ms : List μ}
    (h : Tr rs nm dA dB r R ms) : R.card ≤ r.m := by
  cases h with
  | node r R ch hr hsub hside hm hcov => exact hm

theorem reduction {σ : Type} [DecidableEq σ] [DecidableEq μ] (S : Finset σ) (ms : σ → List μ) (nm : μ → ℕ) (w : μ → ℝ)
    (Mv : Finset μ) (hnd : ∀ s ∈ S, (ms s).Nodup) (hsub : ∀ s ∈ S, ∀ e ∈ ms s, e ∈ Mv)
    (hcap : ∀ e ∈ Mv, (S.filter fun s => e ∈ ms s).card ≤ nm e) (hw0 : ∀ e ∈ Mv, 0 ≤ w e) :
    ∑ s ∈ S, ((ms s).map fun e => w e / nm e).sum ≤ ∑ e ∈ Mv, w e := by
  have h1 : ∑ s ∈ S, ((ms s).map fun e => w e / nm e).sum = ∑ s ∈ S, ∑ e ∈ (ms s).toFinset, w e / nm e := by
    apply Finset.sum_congr rfl
    intro s hs
    rw [List.sum_toFinset _ (hnd s hs)]
  have h2 : ∑ s ∈ S, ∑ e ∈ (ms s).toFinset, w e / nm e = ∑ e ∈ Mv, ∑ s ∈ S.filter (fun s => e ∈ ms s), w e / nm e := by
    apply Finset.sum_comm'
    intro s e
    constructor
    · rintro ⟨hs, he⟩
      have he' : e ∈ ms s := List.mem_toFinset.mp he
      exact ⟨Finset.mem_filter.2 ⟨hs, he'⟩, hsub s hs e he'⟩
    · rintro ⟨hs, he⟩
      have := Finset.mem_filter.1 hs
      exact ⟨this.1, List.mem_toFinset.2 this.2⟩
  rw [h1, h2]
  apply Finset.sum_le_sum
  intro e he
  rw [Finset.sum_const, nsmul_eq_mul]
  have hc := hcap e he
  have hw := hw0 e he
  by_cases h0 : nm e = 0
  · have : (S.filter fun s => e ∈ ms s).card = 0 := by omega
    rw [this]; simpa using hw
  · have hpos : (0 : ℝ) < nm e := by exact_mod_cast Nat.pos_of_ne_zero h0
    have hcr : (((S.filter fun s => e ∈ ms s).card : ℕ) : ℝ) ≤ nm e := by exact_mod_cast hc
    calc (((S.filter fun s => e ∈ ms s).card : ℕ) : ℝ) * (w e / nm e) ≤ (nm e : ℝ) * (w e / nm e) :=
          mul_le_mul_of_nonneg_right hcr (div_nonneg hw hpos.le)
      _ = w e := by field_simp

def lineOK (rA rB : Row) (capI lam gA gB : ℕ) : Bool :=
  (List.range 49).all (fun x => (List.range 49).all (fun r =>
    decide (lam * min 48 (x + r) ≤ gv rA r + x * capI + gA) && decide (lam * min 48 (x + r) ≤ gv rB r + x * capI + gB)))
  && decide (gB ≤ gA)

/-- the combinatorial data of the whole-meeting tree reduction (all hypotheses named; none depends on the weights).
`S` = source ports (<= 104), `Bset` = the sources whose trees use only the port-realised (restricted) shape edges (`rsB`), `J` = junk cells (source, reader),
`R s` = readers of the non-transported cells of source `s`, `x s` = transported cells, `ms s` = moves of the out-tree of `s`. -/
structure TreeData (σ ρ μ : Type) [DecidableEq σ] [DecidableEq ρ] [DecidableEq μ]
    (rsA rsB : List Row) (rootA rootB : Row) (nB : ℕ) where
  J : Finset (σ × ρ)
  S : Finset σ
  Bset : Finset σ
  Mv : Finset μ
  Mreg : Finset μ
  Mun : Finset μ
  dA : μ → ℕ
  dB : μ → ℕ
  nm : μ → ℕ
  ms : σ → List μ
  R : σ → Finset ρ
  x : σ → ℕ
  hJS : ∀ p ∈ J, p.1 ∈ S
  hScard : S.card ≤ 104
  hfib : ∀ s ∈ S, (J.filter fun p => p.1 = s).card ≤ 48
  hJcard : 4962 ≤ J.card
  hB : Bset ⊆ S
  hBcard : nB ≤ Bset.card
  hcell : ∀ s ∈ S, (J.filter fun p => p.1 = s).card ≤ x s + (R s).card
  hxk : ∀ s ∈ S, x s ≤ (J.filter fun p => p.1 = s).card
  htreeA : ∀ s ∈ S, s ∉ Bset → Tr rsA nm dA dB rootA (R s) (ms s)
  htreeB : ∀ s ∈ Bset, Tr rsB nm dA dB rootB (R s) (ms s)
  hnd : ∀ s ∈ S, (ms s).Nodup
  hMv : ∀ s ∈ S, ∀ e ∈ ms s, e ∈ Mv
  hcap : ∀ e ∈ Mv, (S.filter fun s => e ∈ ms s).card ≤ nm e
  hMsub : Mv ⊆ Mreg ∪ Mun
  hdim : ∀ e ∈ Mreg ∪ Mun, 1 ≤ dA e ∧ dA e < dB e ∧ dB e ≤ 8

theorem tree_lower {σ : Type} [DecidableEq σ] [DecidableEq μ]
    (W : List (List ℕ)) (rsA rsB : List Row) (rootA rootB : Row) (nB : ℕ) (T : TreeData σ ρ μ rsA rsB rootA rootB nB)
    (hcA : ∀ r ∈ rsA, Row.check W rsA r = true) (hcB : ∀ r ∈ rsB, Row.check W rsB r = true)
    (hrA : rootA.m ≤ 48) (hrB : rootB.m ≤ 48) (capI lam gA gB : ℕ) (hline : lineOK rootA rootB capI lam gA gB = true)
    (w : μ → ℝ)
    (hW : ∀ e, 1 ≤ T.dA e → T.dA e < T.dB e → T.dB e ≤ 8 →
      (((W.getD (T.dA e) []).getD (T.dB e) 0 : ℕ) : ℝ) ≤ SCr * w e)
    (hw0 : ∀ e ∈ T.Mv, 0 ≤ w e) (cap : ℝ) (hcap : (capI : ℝ) ≤ SCr * cap) :
    (lam : ℝ) * 4962 - ((gA : ℝ) * 104 - ((gA : ℝ) - gB) * nB) ≤
      SCr * (∑ e ∈ T.Mv, w e + cap * ∑ s ∈ T.S, (T.x s : ℝ)) := by
  have hred := reduction T.S T.ms T.nm w T.Mv T.hnd T.hMv T.hcap hw0
  have hSC : (0 : ℝ) < SCr := by unfold SCr; positivity
  unfold lineOK at hline
  simp only [Bool.and_eq_true, List.all_eq_true, List.mem_range, decide_eq_true_eq] at hline
  obtain ⟨hline, hBA⟩ := hline
  set k : σ → ℕ := fun s => (T.J.filter fun p => p.1 = s).card with hk
  set γ : σ → ℕ := fun s => if s ∈ T.Bset then gB else gA with hγ
  have per : ∀ s ∈ T.S, (lam : ℝ) * k s - γ s ≤ SCr * (((T.ms s).map fun e => w e / T.nm e).sum + cap * T.x s) := by
    intro s hs
    have hk48 : k s ≤ 48 := T.hfib s hs
    have hx := T.hxk s hs
    have hc := T.hcell s hs
    -- tree bound and line bound
    have key : ∀ (root : Row) (rs : List Row) (g : ℕ), (∀ r ∈ rs, Row.check W rs r = true) → root.m ≤ 48 →
        (∀ x < 49, ∀ r < 49, lam * min 48 (x + r) ≤ gv root r + x * capI + g) →
        Tr rs T.nm T.dA T.dB root (T.R s) (T.ms s) →
        (lam : ℝ) * k s - g ≤ SCr * (((T.ms s).map fun e => w e / T.nm e).sum + cap * T.x s) := by
      intro root rs g hcert hr48 hl htr
      have hcost := tree_cost_ge W rs hcert T.nm T.dA T.dB w hW htr
      have hrc := htr.card_le
      have hl' := hl (T.x s) (by have := T.hfib s hs; omega) (T.R s).card (by omega)
      have hn : lam * k s ≤ gv root (T.R s).card + T.x s * capI + g := by
        have : k s ≤ min 48 (T.x s + (T.R s).card) := le_min hk48 hc
        exact le_trans (Nat.mul_le_mul_left _ this) hl'
      have hr : (lam : ℝ) * k s ≤ ((gv root (T.R s).card : ℕ) : ℝ) + T.x s * capI + g := by exact_mod_cast hn
      have hcx : (T.x s : ℝ) * capI ≤ SCr * (cap * T.x s) := by
        have : (0 : ℝ) ≤ T.x s := by positivity
        nlinarith
      linarith
    by_cases hb : s ∈ T.Bset
    · have := key rootB rsB gB hcB hrB (fun x hx r hr => (hline x hx r hr).2) (T.htreeB s hb)
      simpa [hγ, hb] using this
    · have := key rootA rsA gA hcA hrA (fun x hx r hr => (hline x hx r hr).1) (T.htreeA s hs hb)
      simpa [hγ, hb] using this
  have hsum := Finset.sum_le_sum per
  have hJ : (T.J.card : ℝ) = ∑ s ∈ T.S, (k s : ℝ) := by
    have := Finset.card_eq_sum_card_fiberwise (f := Prod.fst) (s := T.J) (t := T.S) T.hJS
    exact_mod_cast this
  have hJge : (4962 : ℝ) ≤ ∑ s ∈ T.S, (k s : ℝ) := by rw [← hJ]; exact_mod_cast T.hJcard
  have hγs : ∑ s ∈ T.S, (γ s : ℝ) ≤ gA * 104 - (gA - gB) * nB := by
    have e : ∀ s, (γ s : ℝ) = gA - (if s ∈ T.Bset then ((gA : ℝ) - gB) else 0) := by
      intro s; simp only [hγ]; split_ifs <;> push_cast <;> ring
    rw [Finset.sum_congr rfl (fun s _ => e s), Finset.sum_sub_distrib, Finset.sum_const, Finset.sum_ite_mem,
      Finset.inter_eq_right.2 T.hB, Finset.sum_const, nsmul_eq_mul, nsmul_eq_mul]
    have h1 : (T.S.card : ℝ) ≤ 104 := by exact_mod_cast T.hScard
    have h2 : (nB : ℝ) ≤ T.Bset.card := by exact_mod_cast T.hBcard
    have h3 : (gB : ℝ) ≤ gA := by exact_mod_cast hBA
    have h4 : (0 : ℝ) ≤ gA := by positivity
    nlinarith [mul_nonneg h4 (sub_nonneg.2 h1), mul_nonneg (sub_nonneg.2 h3) (sub_nonneg.2 h2)]
  have hlam : (0 : ℝ) ≤ lam := by positivity
  have hgl : (lam : ℝ) * 4962 ≤ lam * ∑ s ∈ T.S, (k s : ℝ) := mul_le_mul_of_nonneg_left hJge hlam
  have e1 : ∑ s ∈ T.S, ((lam : ℝ) * k s - γ s) = lam * ∑ s ∈ T.S, (k s : ℝ) - ∑ s ∈ T.S, (γ s : ℝ) := by
    rw [Finset.sum_sub_distrib, ← Finset.mul_sum]
  have e2 : ∑ s ∈ T.S, SCr * (((T.ms s).map fun e => w e / T.nm e).sum + cap * T.x s) =
      SCr * (∑ s ∈ T.S, ((T.ms s).map fun e => w e / T.nm e).sum + cap * ∑ s ∈ T.S, (T.x s : ℝ)) := by
    rw [← Finset.mul_sum, Finset.sum_add_distrib, ← Finset.mul_sum]
  rw [e1, e2] at hsum
  have h5 : SCr * (∑ s ∈ T.S, ((T.ms s).map fun e => w e / T.nm e).sum + cap * ∑ s ∈ T.S, (T.x s : ℝ)) ≤
      SCr * (∑ e ∈ T.Mv, w e + cap * ∑ s ∈ T.S, (T.x s : ℝ)) :=
    mul_le_mul_of_nonneg_left (add_le_add_left hred _ |> fun h => by linarith) hSC.le
  linarith

end CTree
