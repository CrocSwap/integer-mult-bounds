/-
V2FloorKernelSound (lane LEAN-KERNEL, Nov 16): soundness of the FLAG-cover checker (V2FloorKernelCheck).

`kernel_intFeasible`: if the data checks return `true`, then `IntFeasible` holds for the listed pairs, with the
thresholds T. Generic over the data; kernel-only (no native_decide).
-/
import Nov15.V2FloorKernelCheck

namespace V2Floor
open Finset

attribute [local instance 10] Classical.propDecidable

/-! ### small list facts -/

theorem getD_mem' {α : Type*} {l : List α} {i : ℕ} (d : α) (h : i < l.length) : l.getD i d ∈ l := by
  rw [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem h, Option.getD_some]; exact List.getElem_mem h

theorem headD_mem {l : List ℕ} (h : l ≠ []) : l.headD 0 ∈ l := by
  cases l with
  | nil => exact absurd rfl h
  | cons a l => simp

theorem sortedLt_pairwise : ∀ l : List ℕ, sortedLt l = true → l.Pairwise (· < ·)
  | [], _ => List.Pairwise.nil
  | [a], _ => List.pairwise_singleton _ _
  | a :: b :: l, h => by
    simp only [sortedLt, Bool.and_eq_true, decide_eq_true_eq] at h
    have ih := sortedLt_pairwise (b :: l) h.2
    refine List.Pairwise.cons ?_ ih
    intro c hc
    rcases List.mem_cons.mp hc with rfl | hc
    · exact h.1
    · exact lt_trans h.1 (List.rel_of_pairwise_cons ih hc)

theorem list_sum_filter {α : Type*} (l : List α) (p : α → Bool) (f : α → ℕ) :
    ((l.filter p).map f).sum = (l.map (fun x => if p x then f x else 0)).sum := by
  induction l with
  | nil => simp
  | cons a l ih => by_cases h : p a <;> simp [List.filter_cons, h, ih]

theorem biorth_ne_zero {A C : List ℕ} (h : biorth A C = true) {v : ℕ} (hv : v ∈ A) : v ≠ 0 := by
  obtain ⟨_, hb⟩ := biorth_spec h
  obtain ⟨j, hj, rfl⟩ := List.getElem_of_mem hv
  have := hb j j hj hj
  have e : A.getD j 0 = A[j] := by rw [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem hj, Option.getD_some]
  rw [e, if_pos rfl] at this
  intro h0; rw [h0, Nat.and_zero] at this; exact absurd this (by decide)

theorem allLt_mem {A : List ℕ} (h : allLt A = true) {v : ℕ} (hv : v ∈ A) : v < 512 := by
  unfold allLt at h; rw [List.all_eq_true] at h; exact of_decide_eq_true (h v hv)

theorem vec_mem_Lsub {B : List ℕ} {v : ℕ} (hv : v ∈ B) : vec v ∈ Lsub B :=
  Submodule.subset_span (by simp only [Set.mem_setOf_eq, List.mem_map]; exact ⟨v, hv, rfl⟩)

theorem maskOf_congr {P H H' : List ℕ} (hP : allLt P = true) (h : ∀ v < 512, chk H v = chk H' v) :
    maskOf P H = maskOf P H' := by
  unfold maskOf
  have : ∀ (l : List ℕ) (acc : ℕ), (∀ v ∈ l, v < 512) →
      l.foldl (fun acc v => if chk H v then 2 * acc + 1 else 2 * acc) acc =
      l.foldl (fun acc v => if chk H' v then 2 * acc + 1 else 2 * acc) acc := by
    intro l; induction l with
    | nil => intros; rfl
    | cons a l ih =>
      intro acc hl
      simp only [List.foldl_cons]
      rw [h a (hl a (List.mem_cons_self ..))]
      exact ih _ (fun v hv => hl v (List.mem_cons_of_mem _ hv))
  exact this _ _ (fun v hv => allLt_mem hP hv)

/-! ### facts extracted from the validity checks -/

section facts
variable {NS : List KGrp} {PR : List ℕ}

theorem grpOK_of (hNS : nsOK NS PR = true) {g : ℕ} (hg : g < NS.length) : grpOK (grp NS g) = true := by
  unfold nsOK at hNS; simp only [Bool.and_eq_true, List.all_eq_true] at hNS
  exact hNS.1.1 _ (getD_mem' _ hg)

theorem grp_facts (hNS : nsOK NS PR = true) {g : ℕ} (hg : g < NS.length) :
    fdim (Usub (grp NS g).uh) = 9 - (grp NS g).uh.length ∧ 9 - (grp NS g).uh.length ≤ 8 := by
  have h := grpOK_of hNS hg
  unfold grpOK at h; simp only [Bool.and_eq_true, Bool.not_eq_true', List.isEmpty_eq_false_iff] at h
  refine ⟨fdim_Usub h.1.1.2 h.1.2, ?_⟩
  have := List.length_pos_iff.mpr h.1.1.1; omega

theorem rec_ok (hNS : nsOK NS PR = true) {q : ℕ × ℕ} (hq : q ∈ POS NS) :
    recOK (grp NS q.1).uh.length (rcd NS q) = true := by
  rw [mem_POS] at hq
  have h := grpOK_of hNS hq.1
  unfold grpOK at h; simp only [Bool.and_eq_true, List.all_eq_true] at h
  exact h.2 _ (getD_mem' _ hq.2)

theorem rec_facts (hNS : nsOK NS PR = true) {q : ℕ × ℕ} (hq : q ∈ POS NS) :
    fdim (Lsub (rcd NS q).lb) = (rcd NS q).lb.length ∧ (rcd NS q).lb ≠ [] ∧
    (∀ v ∈ (rcd NS q).lb, v < 512 ∧ v ≠ 0) ∧
    fld (rcd NS q).c 0 = 0 ∧ (∀ k < 9, fld (rcd NS q).c k ≤ fld (rcd NS q).c (k + 1) ∧
      (fld (rcd NS q).c k = fld (rcd NS q).c (k + 1) ∨
        ((rcd NS q).lb.length ≤ k ∧ k < 9 - (grp NS q.1).uh.length))) := by
  have h := rec_ok hNS hq
  unfold recOK cumOK at h
  simp only [Bool.and_eq_true, Bool.not_eq_true', List.isEmpty_eq_false_iff, beq_iff_eq, List.all_eq_true,
    List.mem_range, decide_eq_true_eq, Bool.or_eq_true] at h
  obtain ⟨⟨⟨⟨hne, hlb⟩, hlw⟩, hbi⟩, h0, hk⟩ := h
  exact ⟨fdim_Lsub hlb hbi, hne, fun v hv => ⟨allLt_mem hlb hv, biorth_ne_zero hbi hv⟩, h0, hk⟩

theorem grp_inj (hNS : nsOK NS PR = true) {g g' : ℕ} (hg : g < NS.length) (hg' : g' < NS.length)
    (h : Usub (grp NS g).uh = Usub (grp NS g').uh) : g = g' := by
  have hPR : allLt PR = true := by
    unfold nsOK at hNS; simp only [Bool.and_eq_true] at hNS; exact hNS.1.2
  have hm : maskOf PR (grp NS g).uh = maskOf PR (grp NS g').uh := by
    apply maskOf_congr hPR; intro v hv
    have e1 := mem_Usub_iff (grp NS g).uh hv
    have e2 := mem_Usub_iff (grp NS g').uh hv
    rw [h] at e1
    exact Bool.eq_iff_iff.mpr (e1.symm.trans e2)
  unfold nsOK at hNS; simp only [Bool.and_eq_true] at hNS
  have hnd := (sortedLt_pairwise _ hNS.2).imp (fun h => ne_of_lt h)
  have hl1 : g < (NS.map (fun G => maskOf PR G.uh)).length := by simpa using hg
  have hl2 : g' < (NS.map (fun G => maskOf PR G.uh)).length := by simpa using hg'
  apply (List.Nodup.getElem_inj_iff hnd (i := g) (j := g') (hi := hl1) (hj := hl2)).mp
  simp only [List.getElem_map]
  have e1 : grp NS g = NS[g] := by unfold grp; rw [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem hg]; rfl
  have e2 : grp NS g' = NS[g'] := by unfold grp; rw [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem hg']; rfl
  rw [← e1, ← e2]; exact hm

theorem ent_of {LT : BT} (hLT : ltOK NS LT = true) {v : ℕ} (hv : v < 512) {e : KEnt} (he : e ∈ LT.get 9 v) :
    (e.g, e.j) ∈ POS NS ∧ e.uh = (grp NS e.g).uh ∧ e.lb = (rcd NS (e.g, e.j)).lb ∧ e.c = (rcd NS (e.g, e.j)).c ∧
      e.lb.headD 0 = v := by
  unfold ltOK at hLT; rw [List.all_eq_true] at hLT
  have h := hLT v (List.mem_range.mpr hv); rw [List.all_eq_true] at h
  have h2 := h e he
  unfold entOK at h2; simp only [Bool.and_eq_true, decide_eq_true_eq] at h2
  obtain ⟨⟨⟨⟨⟨h1, h2'⟩, h3⟩, h4⟩, h5⟩, h6⟩ := h2
  exact ⟨(mem_POS NS).mpr ⟨h1, h2'⟩, h3, h4, h5, h6⟩

theorem compl_of {LT : BT} (hC : complOK NS LT = true) {q : ℕ × ℕ} (hq : q ∈ POS NS)
    (h2 : (rcd NS q).lb.length ≤ 2) :
    ∃ e ∈ LT.get 9 ((rcd NS q).lb.headD 0), e.g = q.1 ∧ e.j = q.2 := by
  rw [mem_POS] at hq
  unfold complOK at hC; rw [List.all_eq_true] at hC
  have h := hC q.1 (List.mem_range.mpr hq.1); rw [List.all_eq_true] at h
  have h' := h q.2 (List.mem_range.mpr hq.2)
  simp only [Bool.or_eq_true, Bool.not_eq_true', decide_eq_false_iff_not, List.any_eq_true, Bool.and_eq_true,
    decide_eq_true_eq] at h'
  rcases h' with h' | ⟨e, he, h1, h2⟩
  · exact absurd h2 h'
  · exact ⟨e, he, h1, h2⟩

end facts

/-! ### the τ bound on the listed pairs -/

section bound
variable {NS : List KGrp} {PR : List ℕ}

theorem bound_of_cover (hNS : nsOK NS PR = true) (X Y : Sub) (a : ℕ) (Q : Finset (ℕ × ℕ)) (hQ : Q ⊆ POS NS)
    (hS : ∀ q ∈ POS NS, Lsub (rcd NS q).lb ≤ X → Y ≤ Usub (grp NS q.1).uh → q ∈ Q) (τ : ℕ → ℕ) :
    ∑ q ∈ (POS NS).filter (fun q => Lsub (rcd NS q).lb ≤ X ∧ Y ≤ Usub (grp NS q.1).uh), seg (rcd NS q).c a (fdim Y) ≤
      ∑ g ∈ (Q.image Prod.fst).filter (fun g => fdim Y ≤ 9 - (grp NS g).uh.length),
        (∑ q ∈ Q.filter (fun q => q.1 = g), seg (rcd NS q).c a (fdim Y) - τ (9 - (grp NS g).uh.length)) +
      ∑ d ∈ Icc (fdim Y) 8, Mt (fdim Y) d * τ d := by
  refine le_trans (Finset.sum_le_sum_of_subset_of_nonneg (t := Q.filter (fun q => Y ≤ Usub (grp NS q.1).uh)) ?_
    (fun _ _ _ => Nat.zero_le _)) ?_
  · intro q hq; simp only [mem_filter] at hq ⊢; exact ⟨hS q hq.1 hq.2.1 hq.2.2, hq.2.2⟩
  · have hpos : ∀ q ∈ Q, q.1 < NS.length := fun q hq => ((mem_POS NS).mp (hQ hq)).1
    exact tau_bound Q Prod.fst (fun g => Usub (grp NS g).uh) (fun g => 9 - (grp NS g).uh.length)
      (fun q hq => (grp_facts hNS (hpos q hq)).1) (fun q hq => (grp_facts hNS (hpos q hq)).2)
      (by
        intro g hg g' hg' h
        obtain ⟨q, hq, rfl⟩ := mem_image.mp (Finset.mem_coe.mp hg)
        obtain ⟨q', hq', rfl⟩ := mem_image.mp (Finset.mem_coe.mp hg')
        exact grp_inj hNS (hpos q hq) (hpos q' hq') h)
      (fun q => seg (rcd NS q).c a (fdim Y)) Y τ

/-- E rows: the τ bound over the members of a computed entry list is at most `rowE`. -/
theorem rhs_le_rowE (ms : List KEnt) (a b : ℕ) (hb : b ≤ 9)
    (hcons : ∀ e ∈ ms, e.uh = (grp NS e.g).uh ∧ e.c = (rcd NS (e.g, e.j)).c) :
    ∑ g ∈ (((ms.map (fun e => (e.g, e.j))).toFinset).image Prod.fst).filter (fun g => b ≤ 9 - (grp NS g).uh.length),
        (∑ q ∈ ((ms.map (fun e => (e.g, e.j))).toFinset).filter (fun q => q.1 = g), seg (rcd NS q).c a b -
          tauE ms a b (9 - (grp NS g).uh.length)) +
      ∑ d ∈ Icc b 8, Mt b d * tauE ms a b d ≤ rowE ms a b := by
  unfold rowE
  rw [mtau, ← sum_Icc_list b _ hb]
  apply Nat.add_le_add_right
  set du := fun g => 9 - (grp NS g).uh.length
  set τ := tauE ms a b
  have himg : ((ms.map (fun e => (e.g, e.j))).toFinset).image Prod.fst = (ms.map (fun e => e.g)).toFinset := by
    ext g; simp
  have hkeys : keysE ms = ((ms.map (fun e => e.g)).map (fun g => (g, du g))).dedup := by
    unfold keysE; congr 1; rw [List.map_map]; apply List.map_congr_left
    intro e he; simp only [Function.comp, du, (hcons e he).1]
  rw [himg, hkeys, ← sum_toFinset_nodup _ (List.nodup_dedup _)]
  refine le_trans ?_ (le_of_eq (Finset.sum_congr (s₂ := ((ms.map (fun e => e.g)).toFinset).image (fun g => (g, du g)))
    ?_ (fun _ _ => rfl)).symm)
  swap
  · ext k; simp [List.mem_dedup]
  rw [Finset.sum_image (fun x _ y _ h => (Prod.mk.inj h).1), Finset.sum_filter]
  refine Finset.sum_le_sum fun g _ => ?_
  split_ifs with h
  · apply Nat.sub_le_sub_right
    have hf : ((ms.map (fun e => (e.g, e.j))).toFinset).filter (fun q => q.1 = g) =
        (((ms.filter (fun e => decide (e.g = g))).map (fun e => (e.g, e.j)))).toFinset := by
      ext q; simp only [mem_filter, List.mem_toFinset, List.mem_map, List.mem_filter, decide_eq_true_eq]
      constructor
      · rintro ⟨⟨e, he, rfl⟩, h⟩; exact ⟨e, ⟨he, h⟩, rfl⟩
      · rintro ⟨e, ⟨he, h⟩, rfl⟩; exact ⟨⟨e, he, rfl⟩, h⟩
    rw [hf]
    refine le_trans (sum_toFinset_le_list _ _) (le_of_eq ?_)
    unfold wE; rw [List.map_map]; congr 1; apply List.map_congr_left
    intro e he; simp only [Function.comp]; rw [(hcons e (List.mem_of_mem_filter he)).2]
  · exact le_rfl

/-- F rows: the τ bound over the hyperplane class is at most `rowF`. -/
theorem rhs_le_rowF (h a b : ℕ) (hb : b ≤ 9) (τ : ℕ → ℕ) :
    ∑ g ∈ (((POS NS).filter (fun q => memF h a (rcd NS q) = true)).image Prod.fst).filter
        (fun g => b ≤ 9 - (grp NS g).uh.length),
        (∑ q ∈ ((POS NS).filter (fun q => memF h a (rcd NS q) = true)).filter (fun q => q.1 = g),
          seg (rcd NS q).c a b - τ (9 - (grp NS g).uh.length)) +
      ∑ d ∈ Icc b 8, Mt b d * τ d ≤ rowF NS h a b τ := by
  unfold rowF
  rw [mtau, ← sum_Icc_list b _ hb]
  apply Nat.add_le_add_right
  rw [← sum_range_getD NS default, Finset.sum_filter]
  refine le_trans (Finset.sum_le_sum_of_subset_of_nonneg (t := range NS.length) ?_ (fun _ _ _ => Nat.zero_le _)) ?_
  · intro g hg; obtain ⟨q, hq, rfl⟩ := mem_image.mp hg
    exact mem_range.mpr ((mem_POS NS).mp (mem_filter.mp hq).1).1
  refine Finset.sum_le_sum fun g hg => ?_
  change _ ≤ (if b ≤ 9 - (grp NS g).uh.length then wF h a b (grp NS g) - τ (9 - (grp NS g).uh.length) else 0)
  split_ifs with hh
  · apply Nat.sub_le_sub_right; apply le_of_eq
    have hf : ((POS NS).filter (fun q => memF h a (rcd NS q) = true)).filter (fun q => q.1 = g) =
        ((range (grp NS g).recs.length).filter (fun j => memF h a ((grp NS g).recs.getD j default) = true)).image
          (fun j => (g, j)) := by
      ext q; simp only [mem_filter, mem_image, mem_range, mem_POS]
      constructor
      · rintro ⟨⟨⟨_, h2⟩, h3⟩, h4⟩; subst h4; exact ⟨q.2, ⟨h2, h3⟩, rfl⟩
      · rintro ⟨j, ⟨h2, h3⟩, rfl⟩; exact ⟨⟨⟨mem_range.mp hg, h2⟩, h3⟩, rfl⟩
    rw [hf, Finset.sum_image (fun x _ y _ h => (Prod.mk.inj h).2), Finset.sum_filter]
    unfold wF; rw [list_sum_filter, ← sum_range_getD _ default]; rfl
  · exact le_rfl

end bound

/-! ### geometry of the E classes -/

theorem span_single_eq {X : Sub} {l : ℕ} (hl : l < 512) (hl0 : l ≠ 0) (hX : fdim X = 1) (hmem : vec l ∈ X) :
    X = Submodule.span (ZMod 2) {vec l} := by
  have hv : vec l ≠ 0 := fun h => hl0 ((vec_eq_zero hl).mp h)
  symm; apply Submodule.eq_of_le_of_finrank_eq
  · exact (Submodule.span_singleton_le_iff_mem _ _).mpr hmem
  · rw [finrank_span_singleton hv]; exact hX.symm

theorem mem_span_single_iff {l m : ℕ} (hl : l < 512) (hm : m < 512) :
    vec m ∈ Submodule.span (ZMod 2) {vec l} ↔ (m = 0 ∨ m = l) := by
  have h := mem_span_pair_iff hl hl hm
  rw [Set.pair_eq_singleton, Nat.xor_self] at h
  rw [h]; tauto

theorem plane_decomp {X : Sub} {l : ℕ} (hl : l < 512) (hl0 : l ≠ 0) (hX : fdim X = 2) (hmem : vec l ∈ X) :
    ∃ w < 512, w ≠ 0 ∧ w ≠ l ∧ w < w ^^^ l ∧ X = Submodule.span (ZMod 2) {vec l, vec w} := by
  have hv : vec l ≠ 0 := fun h => hl0 ((vec_eq_zero hl).mp h)
  have hS1 : fdim (Submodule.span (ZMod 2) {vec l}) = 1 := finrank_span_singleton hv
  have hle : Submodule.span (ZMod 2) {vec l} ≤ X := (Submodule.span_singleton_le_iff_mem _ _).mpr hmem
  have hlt : Submodule.span (ZMod 2) {vec l} < X := lt_of_le_of_ne hle (fun h => by rw [← h] at hX; omega)
  obtain ⟨x, hxX, hxS⟩ := SetLike.exists_of_lt hlt
  obtain ⟨w0, hw0, rfl⟩ := vec_surj x
  have hx1 : w0 ^^^ l < 512 := Nat.xor_lt_two_pow (n := 9) hw0 hl
  have key : ∀ w < 512, vec w ∈ X → vec w ∉ Submodule.span (ZMod 2) {vec l} → w < w ^^^ l →
      ∃ w < 512, w ≠ 0 ∧ w ≠ l ∧ w < w ^^^ l ∧ X = Submodule.span (ZMod 2) {vec l, vec w} := by
    intro w hw hwX hwS hwl
    refine ⟨w, hw, ?_, ?_, hwl, ?_⟩
    · rintro rfl; exact hwS (by rw [vec_zero]; exact Submodule.zero_mem _)
    · rintro rfl; exact hwS (Submodule.mem_span_singleton_self _)
    · symm; apply Submodule.eq_of_le_of_finrank_eq
      · rw [Submodule.span_le]; intro y hy
        rcases hy with rfl | hy
        · exact hmem
        · rw [Set.mem_singleton_iff.mp hy]; exact hwX
      · have h1 : Submodule.span (ZMod 2) {vec l} < Submodule.span (ZMod 2) {vec l, vec w} := by
          refine lt_of_le_of_ne (Submodule.span_mono (by simp)) (fun h => hwS ?_)
          rw [h]; exact Submodule.subset_span (by simp)
        have h2 := Submodule.finrank_lt_finrank_of_lt h1
        have h3 := Submodule.finrank_mono (show Submodule.span (ZMod 2) {vec l, vec w} ≤ X by
          rw [Submodule.span_le]; intro y hy
          rcases hy with rfl | hy
          · exact hmem
          · rw [Set.mem_singleton_iff.mp hy]; exact hwX)
        unfold fdim at hS1 hX; omega
  by_cases hc : w0 < w0 ^^^ l
  · exact key w0 hw0 hxX hxS hc
  · apply key (w0 ^^^ l) hx1
    · rw [vec_xor]; exact X.add_mem hxX hmem
    · intro h; apply hxS
      have z2 : ∀ y : ZMod 2, y + y = 0 := by decide
      have : vec w0 = vec (w0 ^^^ l) + vec l := by
        rw [vec_xor]; funext j; simp only [Pi.add_apply]; rw [add_assoc, z2, add_zero]
      rw [this]; exact Submodule.add_mem _ h (Submodule.mem_span_singleton_self _)
    · have hne : w0 ≠ w0 ^^^ l := by
        intro h; apply hl0
        have := congrArg (· ^^^ w0) h; simp only [Nat.xor_self] at this
        rw [Nat.xor_comm w0 l, Nat.xor_assoc, Nat.xor_self, Nat.xor_zero] at this; exact this.symm
      rw [Nat.xor_assoc, Nat.xor_self, Nat.xor_zero]; omega

/-! ### the main theorem -/

theorem rowsF_mem (a b : ℕ) (h3 : 3 ≤ a) (hab : a < b) (h8 : b ≤ 8) : (a, b) ∈ rowsF := by
  have : a ≤ 7 := by omega
  interval_cases a <;> interval_cases b <;> decide

theorem lhs_eq {NS : List KGrp} {PR : List ℕ} (hNS : nsOK NS PR = true) (X Y : Sub) (a b : ℕ) (hab : a ≤ b) (hb : b ≤ 9) :
    ∑ p ∈ univ.filter (fun p : PS NS => Lsub (LBK NS p) ≤ X ∧ Y ≤ Usub (UHK NS p)), ∑ k ∈ Ico a b, numK NS p k =
    ∑ q ∈ (POS NS).filter (fun q => Lsub (rcd NS q).lb ≤ X ∧ Y ≤ Usub (grp NS q.1).uh), seg (rcd NS q).c a b := by
  rw [Finset.sum_filter, Finset.sum_filter, ← Finset.sum_coe_sort (POS NS)]
  refine Finset.sum_congr rfl fun p _ => ?_
  unfold LBK UHK
  split_ifs
  · unfold numK seg
    obtain ⟨-, -, -, -, hk⟩ := rec_facts hNS p.2
    exact sum_Ico_tele (fld (rcd NS p.1).c) (fun k hk' => (hk k hk').1) a b hab hb
  · rfl

set_option maxHeartbeats 4000000 in
theorem kernel_intFeasible {NS : List KGrp} {PR : List ℕ} {LT : BT} {T : ℕ → ℕ → ℕ} {TD : List ℕ}
    (hNS : nsOK NS PR = true) (hLT : ltOK NS LT = true) (hC : complOK NS LT = true)
    (hE1 : ∀ l < 512, (LT.get 9 l).isEmpty = true ∨ lineOK LT T l = true)
    (hE2 : ∀ l < 512, planeAll LT T l = true)
    (hF : ∀ h < 512, 0 < h → hypOK NS T (TD.getD (h - 1) 0) h = true) :
    IntFeasible (fun p : PS NS => Lsub (LBK NS p)) (fun p => Usub (UHK NS p)) (numK NS) T := by
  intro X Y hXY h1 h8
  have hab : fdim X < fdim Y := Submodule.finrank_lt_finrank_of_lt hXY
  rw [lhs_eq hNS X Y _ _ (le_of_lt hab) (by omega)]
  set a := fdim X with ha_def
  set b := fdim Y with hb_def
  set S := (POS NS).filter (fun q => Lsub (rcd NS q).lb ≤ X ∧ Y ≤ Usub (grp NS q.1).uh) with hS_def
  by_cases ha3 : 3 ≤ a
  · -- hyperplane rows
    have hXT : X ≠ ⊤ := by
      intro hX; have : fdim X = 9 := by rw [hX]; simp [fdim]
      omega
    obtain ⟨h, h0, h512, hXH⟩ := exists_hyperplane X hXT
    have hrow := hF h h512 h0
    unfold hypOK at hrow; rw [List.all_eq_true] at hrow
    have hr := hrow (a, b) (rowsF_mem a b ha3 hab h8)
    simp only [decide_eq_true_eq] at hr
    have hcov : ∀ q ∈ POS NS, Lsub (rcd NS q).lb ≤ X → Y ≤ Usub (grp NS q.1).uh →
        q ∈ (POS NS).filter (fun q => memF h a (rcd NS q) = true) := by
      intro q hq hL _
      rw [mem_filter]; refine ⟨hq, ?_⟩
      obtain ⟨hd, -, hvs, -, -⟩ := rec_facts hNS hq
      unfold memF; simp only [Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, beq_iff_eq]
      refine ⟨?_, fun v hv => ?_⟩
      · rw [← hd]; exact Submodule.finrank_mono hL
      · have hm := (mem_Usub_iff [h] (hvs v hv).1).mp (hXH (hL (vec_mem_Lsub hv)))
        unfold chk at hm; simpa using hm
    have e1 := bound_of_cover hNS X Y a ((POS NS).filter (fun q => memF h a (rcd NS q) = true))
      (Finset.filter_subset _ _) hcov (fun d => fld (TD.getD (h - 1) 0) (slotF a b d))
    rw [← hb_def] at e1
    have e2 := rhs_le_rowF (NS := NS) h a b (by omega) (fun d => fld (TD.getD (h - 1) 0) (slotF a b d))
    exact le_trans e1 (le_trans e2 hr)
  · -- exact-X rows, dim X ≤ 2
    by_cases hSe : S = ∅
    · rw [hSe, sum_empty]; exact Nat.zero_le _
    obtain ⟨p0, hp0⟩ := Finset.nonempty_iff_ne_empty.mpr hSe
    rw [hS_def, mem_filter] at hp0
    obtain ⟨hd0, hne0, hvs0, -, -⟩ := rec_facts hNS hp0.1
    set l := (rcd NS p0).lb.headD 0 with hl_def
    have hlmem := headD_mem hne0
    obtain ⟨hl512, hl0⟩ := hvs0 l hlmem
    have hlX : vec l ∈ X := hp0.2.1 (vec_mem_Lsub hlmem)
    have hlen0 : (rcd NS p0).lb.length ≤ 2 := by
      rw [← hd0]; have := Submodule.finrank_mono hp0.2.1; unfold fdim at *; omega
    obtain ⟨e0, he0, -, -⟩ := compl_of hC hp0.1 hlen0
    have hnemp : (LT.get 9 l).isEmpty = false := by
      cases hh : LT.get 9 l with
      | nil => rw [hh] at he0; exact absurd he0 (List.not_mem_nil)
      | cons _ _ => rfl
    have hXU : ∀ q ∈ S, ∀ m < 512, vec m ∈ X → chk (grp NS q.1).uh m = true := by
      intro q hq m hm hmX
      rw [hS_def, mem_filter] at hq
      exact (mem_Usub_iff _ hm).mp (hq.2.2 ((le_of_lt hXY) hmX))
    -- generic finish
    have fin : ∀ ms : List KEnt, (∀ e ∈ ms, ∃ v < 512, e ∈ LT.get 9 v) →
        (∀ q ∈ S, ∃ e ∈ ms, e.g = q.1 ∧ e.j = q.2) →
        ∑ q ∈ S, seg (rcd NS q).c a b ≤ rowE ms a b := by
      intro ms hms hcov
      have hent : ∀ e ∈ ms, (e.g, e.j) ∈ POS NS ∧ e.uh = (grp NS e.g).uh ∧ e.c = (rcd NS (e.g, e.j)).c := by
        intro e he; obtain ⟨v, hv, hev⟩ := hms e he
        obtain ⟨h1, h2, -, h4, -⟩ := ent_of hLT hv hev; exact ⟨h1, h2, h4⟩
      have hsub : (ms.map (fun e => (e.g, e.j))).toFinset ⊆ POS NS := by
        intro q hq; simp only [List.mem_toFinset, List.mem_map] at hq
        obtain ⟨e, he, rfl⟩ := hq; exact (hent e he).1
      have hcv : ∀ q ∈ POS NS, Lsub (rcd NS q).lb ≤ X → Y ≤ Usub (grp NS q.1).uh →
          q ∈ (ms.map (fun e => (e.g, e.j))).toFinset := by
        intro q hq hL hU
        obtain ⟨e, he, h1, h2⟩ := hcov q (by rw [hS_def, mem_filter]; exact ⟨hq, hL, hU⟩)
        simp only [List.mem_toFinset, List.mem_map]
        exact ⟨e, he, Prod.ext h1 h2⟩
      have e1 := bound_of_cover hNS X Y a (ms.map (fun e => (e.g, e.j))).toFinset hsub hcv (tauE ms a b)
      rw [← hb_def, ← hS_def] at e1
      exact le_trans e1 (rhs_le_rowE ms a b (by omega) (fun e he => ⟨(hent e he).2.1, (hent e he).2.2⟩))
    -- entries of members
    have hmemb : ∀ q ∈ S, (rcd NS q).lb.length ≤ 2 ∧ ∃ e ∈ LT.get 9 ((rcd NS q).lb.headD 0),
        e.g = q.1 ∧ e.j = q.2 ∧ e.lb = (rcd NS q).lb ∧ e.uh = (grp NS q.1).uh := by
      intro q hq
      have hq' := hq; rw [hS_def, mem_filter] at hq'
      obtain ⟨hd, hne, hvs, -, -⟩ := rec_facts hNS hq'.1
      have hlen : (rcd NS q).lb.length ≤ 2 := by
        rw [← hd]; have := Submodule.finrank_mono hq'.2.1; unfold fdim at *; omega
      obtain ⟨e, he, h1, h2⟩ := compl_of hC hq'.1 hlen
      have hh := (hvs _ (headD_mem hne)).1
      obtain ⟨-, h3, h4, -, -⟩ := ent_of hLT hh he
      refine ⟨hlen, e, he, h1, h2, ?_, ?_⟩
      · rw [h4, h1, h2]
      · rw [h3, h1]
    have ha12 : a = 1 ∨ a = 2 := by omega
    rcases ha12 with ha1 | ha2
    · -- lines
      have hX1 := span_single_eq hl512 hl0 ha1 hlX
      have hrow : lineOK LT T l = true := by
        rcases hE1 l hl512 with h | h
        · rw [hnemp] at h; exact absurd h (by decide)
        · exact h
      unfold lineOK at hrow; rw [List.all_eq_true] at hrow
      have hr := hrow b (List.mem_range'_1.mpr ⟨by omega, by omega⟩)
      simp only [decide_eq_true_eq] at hr
      rw [← ha1] at hr
      refine le_trans (fin _ ?_ ?_) hr
      · intro e he; exact ⟨l, hl512, List.mem_of_mem_filter he⟩
      · intro q hq
        have hq' := hq; rw [hS_def, mem_filter] at hq'
        obtain ⟨-, hne, hvs, -, -⟩ := rec_facts hNS hq'.1
        have hall : ∀ v ∈ (rcd NS q).lb, v = l := by
          intro v hv
          have := hq'.2.1 (vec_mem_Lsub hv); rw [hX1, mem_span_single_iff hl512 (hvs v hv).1] at this
          rcases this with h | h
          · exact absurd h (hvs v hv).2
          · exact h
        obtain ⟨-, e, he, h1, h2, h3, h4⟩ := hmemb q hq
        rw [hall _ (headD_mem hne)] at he
        refine ⟨e, List.mem_filter.mpr ⟨he, ?_⟩, h1, h2⟩
        unfold memE1; simp only [Bool.and_eq_true, List.all_eq_true, beq_iff_eq]
        refine ⟨fun v hv => hall v (h3 ▸ hv), ?_⟩
        rw [h4]; exact hXU q hq l hl512 hlX
    · -- planes
      obtain ⟨w, hw512, hw0, hwl, hwlt, hXe⟩ := plane_decomp hl512 hl0 ha2 hlX
      have hx512 : l ^^^ w < 512 := Nat.xor_lt_two_pow (n := 9) hl512 hw512
      have hwX : vec w ∈ X := by rw [hXe]; exact Submodule.subset_span (by simp)
      have hpa := hE2 l hl512
      unfold planeAll at hpa; rw [hnemp, Bool.false_or, List.all_eq_true] at hpa
      have hpr := hpa (w / 32) (List.mem_range.mpr (by omega))
      unfold planeR at hpr; rw [List.all_eq_true] at hpr
      have hpo := hpr w (List.mem_range'_1.mpr ⟨by omega, by omega⟩)
      simp only [Bool.or_eq_true, beq_iff_eq, Bool.not_eq_true', decide_eq_false_iff_not] at hpo
      have hok : planeOK LT T l w = true := by
        rcases hpo with ((h | h) | h) | h
        · exact absurd h hw0
        · exact absurd h hwl
        · exact absurd hwlt h
        · exact h
      unfold planeOK at hok; rw [List.all_eq_true] at hok
      have hr := hok b (List.mem_range'_1.mpr ⟨by omega, by omega⟩)
      simp only [decide_eq_true_eq] at hr
      rw [← ha2] at hr
      refine le_trans (fin _ ?_ ?_) hr
      · intro e he
        have he' := List.mem_of_mem_filter he
        simp only [List.mem_append] at he'
        rcases he' with (h | h) | h
        · exact ⟨l, hl512, h⟩
        · exact ⟨w, hw512, h⟩
        · exact ⟨l ^^^ w, hx512, h⟩
      · intro q hq
        have hq' := hq; rw [hS_def, mem_filter] at hq'
        obtain ⟨-, hne, hvs, -, -⟩ := rec_facts hNS hq'.1
        have hall : ∀ v ∈ (rcd NS q).lb, v = l ∨ v = w ∨ v = l ^^^ w := by
          intro v hv
          have := hq'.2.1 (vec_mem_Lsub hv); rw [hXe, mem_span_pair_iff hl512 hw512 (hvs v hv).1] at this
          rcases this with h | h
          · exact absurd h (hvs v hv).2
          · exact h
        obtain ⟨-, e, he, h1, h2, h3, h4⟩ := hmemb q hq
        refine ⟨e, List.mem_filter.mpr ⟨?_, ?_⟩, h1, h2⟩
        · simp only [List.mem_append]
          rcases hall _ (headD_mem hne) with h | h | h <;> rw [h] at he
          · exact Or.inl (Or.inl he)
          · exact Or.inl (Or.inr he)
          · exact Or.inr he
        · unfold memE; simp only [Bool.and_eq_true, List.all_eq_true]
          refine ⟨⟨fun v hv => ?_, ?_⟩, ?_⟩
          · rcases hall v (h3 ▸ hv) with h | h | h <;> simp [inPlane, h]
          · rw [h4]; exact hXU q hq l hl512 hlX
          · rw [h4]; exact hXU q hq w hw512 hwX


/-! ### chunk assembly, totals, linking, and the floor -/

theorem planeAll_of {LT : BT} {T : ℕ → ℕ → ℕ} {l : ℕ} (h : ∀ i < 16, planeR LT T l (32 * i) 32 = true) :
    planeAll LT T l = true := by
  unfold planeAll; rw [Bool.or_eq_true, List.all_eq_true]; right
  intro i hi; exact h i (List.mem_range.mp hi)

theorem planeAll_of_empty {LT : BT} {T : ℕ → ℕ → ℕ} {l : ℕ} (h : (LT.get 9 l).isEmpty = true) :
    planeAll LT T l = true := by unfold planeAll; rw [h]; rfl

/-- Σ of the certificate. -/
def totK (NS : List KGrp) : ℕ := (NS.map (fun G => (G.recs.map (fun r => fld r.c 9)).sum)).sum

/-- every listed pair is a pair of the reference list D (index `orig`, same L basis and U checks). -/
def linkOK (NS : List KGrp) (D : ℕ → List ℕ × List ℕ × List ℕ) (N : ℕ) : Bool :=
  NS.all (fun G => G.recs.all (fun r => decide (r.orig < N) && decide (r.lb = (D r.orig).1) &&
    decide (G.uh = (D r.orig).2.1)))

theorem link_of {NS : List KGrp} {D : ℕ → List ℕ × List ℕ × List ℕ} {N : ℕ} (hl : linkOK NS D N = true)
    (p : PS NS) : ∃ i < N, LBK NS p = (D i).1 ∧ UHK NS p = (D i).2.1 := by
  have hp := (mem_POS NS).mp p.2
  unfold linkOK at hl; rw [List.all_eq_true] at hl
  have h1 := hl _ (getD_mem' default hp.1); rw [List.all_eq_true] at h1
  have h2 := h1 _ (getD_mem' default hp.2)
  simp only [Bool.and_eq_true, decide_eq_true_eq] at h2
  exact ⟨_, h2.1.1, h2.1.2, h2.2⟩

theorem sum_POS {NS : List KGrp} (f : ℕ × ℕ → ℕ) :
    ∑ q ∈ POS NS, f q = ∑ g ∈ range NS.length, ∑ j ∈ range (grp NS g).recs.length, f (g, j) := by
  unfold POS
  rw [Finset.sum_biUnion]
  · refine Finset.sum_congr rfl fun g _ => ?_
    rw [Finset.sum_image (fun x _ y _ h => (Prod.mk.inj h).2)]
  · intro g _ g' _ hne
    simp only [Function.onFun]
    rw [Finset.disjoint_left]
    intro q hq hq'
    obtain ⟨j, _, rfl⟩ := mem_image.mp hq
    obtain ⟨j', _, h⟩ := mem_image.mp hq'
    exact hne (Prod.mk.inj h).1.symm

theorem tot_eq {NS : List KGrp} {PR : List ℕ} (hNS : nsOK NS PR = true) :
    (∑ p : PS NS, ∑ k ∈ range 9, numK NS p k) = totK NS := by
  unfold numK
  rw [Finset.sum_coe_sort (POS NS) (fun q => ∑ k ∈ range 9, (if k < 9 then fld (rcd NS q).c (k + 1) - fld (rcd NS q).c k else 0))]
  have e : ∀ q ∈ POS NS, (∑ k ∈ range 9, (if k < 9 then fld (rcd NS q).c (k + 1) - fld (rcd NS q).c k else 0)) =
      fld (rcd NS q).c 9 := by
    intro q hq
    obtain ⟨-, -, -, h0, hk⟩ := rec_facts hNS hq
    rw [Finset.range_eq_Ico, sum_Ico_tele _ (fun k hk' => (hk k hk').1) 0 9 (by omega) le_rfl, h0, Nat.sub_zero]
  rw [Finset.sum_congr rfl e, sum_POS, totK, ← sum_range_getD NS default]
  refine Finset.sum_congr rfl fun g _ => ?_
  exact sum_range_getD (grp NS g).recs default (fun r => fld r.c 9)

/-- **The kernel FLAG floor, generic**: data checks + threshold bound ⇒ every plan realising the listed pairs
costs at least Σ/2^30. -/
theorem kernel_floor {NS : List KGrp} {PR : List ℕ} {LT : BT} {T : ℕ → ℕ → ℕ} {TD : List ℕ} (θ : ℝ)
    (hNS : nsOK NS PR = true) (hLT : ltOK NS LT = true) (hC : complOK NS LT = true)
    (hE1 : ∀ l < 512, (LT.get 9 l).isEmpty = true ∨ lineOK LT T l = true)
    (hE2 : ∀ l < 512, planeAll LT T l = true)
    (hF : ∀ h < 512, 0 < h → hypOK NS T (TD.getD (h - 1) 0) h = true)
    (hT : ∀ a b, 1 ≤ a → a < b → b ≤ 8 → (T a b : ℝ) ≤ 2 ^ 30 * wt θ a b)
    (E : Finset (Sub × Sub)) (hE : ∀ e ∈ E, e.1 < e.2)
    (hreal : ∀ p : PS NS, Reach E (Lsub (LBK NS p)) (Usub (UHK NS p))) :
    (totK NS : ℝ) / 2 ^ 30 ≤ ∑ e ∈ E, wcut θ (fdim e.1) (fdim e.2) := by
  have hfeas := kernel_intFeasible (TD := TD) hNS hLT hC hE1 hE2 hF
  have h := floor_F2 (LBK NS) (UHK NS) (numK NS) θ T hT
    (fun p hb => by
      obtain ⟨hd, hne, -, -, -⟩ := rec_facts hNS p.2
      have : fdim (Lsub (LBK NS p)) = 0 := by rw [hb]; simp [fdim]
      unfold LBK at this; rw [hd] at this
      exact hne (List.length_eq_zero_iff.mp this))
    (fun p ht => by
      obtain ⟨hd, h8⟩ := grp_facts hNS ((mem_POS NS).mp p.2).1
      have : fdim (Usub (UHK NS p)) = 9 := by rw [ht]; simp [fdim]
      unfold UHK at this; omega)
    (fun p k hk => by
      unfold numK at hk
      split_ifs at hk with h9
      · obtain ⟨-, -, -, -, hkk⟩ := rec_facts hNS p.2
        rcases (hkk k h9).2 with h | h
        · exact absurd (by rw [h]; simp) hk
        · exact h
      · exact absurd rfl hk)
    (fun p k hk => by unfold numK; rw [if_neg (by omega)])
    hfeas E hE hreal
  have ht : (∑ p : PS NS, ∑ k ∈ range 9, (numK NS p k : ℝ)) = totK NS := by
    rw [← tot_eq hNS]; push_cast; rfl
  rwa [ht] at h


/-! ### chunk assembly helpers -/

theorem all_of_getD {α : Type*} [Inhabited α] (l : List α) (P : α → Bool)
    (h : ∀ g < l.length, P (l.getD g default) = true) : l.all P = true := by
  rw [List.all_eq_true]; intro x hx
  obtain ⟨g, hg, rfl⟩ := List.getElem_of_mem hx
  have := h g hg; rwa [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem hg, Option.getD_some] at this

theorem all_range_of {F : ℕ → Bool} {N : ℕ} (h : ∀ i < N, F i = true) : (List.range N).all F = true := by
  rw [List.all_eq_true]; intro x hx; exact h x (List.mem_range.mp hx)

theorem forall_of_chunks {P : ℕ → Prop} (N c n : ℕ) (hc : 0 < c) (hN : N ≤ c * n)
    (h : ∀ k < n, ∀ i < c, c * k + i < N → P (c * k + i)) : ∀ i < N, P i := by
  intro i hi
  have e : c * (i / c) + i % c = i := Nat.div_add_mod i c
  have h1 : i / c < n := by
    rcases Nat.lt_or_ge (i / c) n with h' | h'
    · exact h'
    · exfalso; have := Nat.mul_le_mul_left c h'; have := Nat.mod_lt i hc; omega
  have := h (i / c) h1 (i % c) (Nat.mod_lt i hc) (by omega)
  rwa [e] at this

theorem map_eq_of_getD {α : Type*} [Inhabited α] (l : List α) (f : α → ℕ) (ML : List ℕ) (hlen : l.length = ML.length)
    (h : ∀ g < l.length, f (l.getD g default) = ML.getD g 0) : l.map f = ML := by
  apply List.ext_getElem (by simp [hlen])
  intro i h1 h2
  have hi : i < l.length := by simpa using h1
  have := h i hi
  rw [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem hi, Option.getD_some,
    List.getD_eq_getElem?_getD, List.getElem?_eq_getElem h2, Option.getD_some] at this
  simpa using this

theorem nsOK_of {NS : List KGrp} {PR ML : List ℕ} (hG : NS.all grpOK = true) (hP : allLt PR = true)
    (hlen : NS.length = ML.length)
    (hM : ∀ g < NS.length, maskOf PR (NS.getD g default).uh = ML.getD g 0) (hS : sortedLt ML = true) :
    nsOK NS PR = true := by
  unfold nsOK; rw [hG, hP, map_eq_of_getD NS (fun G => maskOf PR G.uh) ML hlen hM, hS]; rfl

end V2Floor
