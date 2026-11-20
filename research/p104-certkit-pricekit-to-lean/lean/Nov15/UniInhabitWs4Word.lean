/-
UniInhabitWs4Word (lane UNI-INHABIT, Nov 19).  The end state of the concrete tWs4 trace is a `Word caller7113` up to
the row clause, and satisfies the three verifier clauses:
* frames: every frame mask is a subspace (frameOK certificate ⇒ IsSubsp), dim (chOf i) = dimT (cntM = 2^dim);
* endpoint charts of the 400 mains (line / Vc / {0} / q^⊥) by mask bit checks;
* `wordWs4 (hrow : RowsWs4) : Word caller7113 (exec trWs4)`, where `RowsWs4` = final rows of the public
  registers = caller targets (WordModelDefs.Word.final_row) is the ONE clause not replayed in the kernel;
* `framesWs4 : FramesSubsp`, `chartsWs4 : ChartsSubsp`, `nestedWs4 : OwnedNested` (all from the replay).
Kernel only: no sorry, no native_decide, no new axioms.
-/
import Nov15.UniInhabitWs4Reg
import Nov15.UniInhabitWs4Ports

set_option linter.unusedSectionVars false

namespace UniInhabitWs4
open Uni WordModel Finset UniFold7113 SafeRungsClique

attribute [local irreducible] trWs4 evsWs4 Tabs.maskT Tabs.ck26 Tabs.xI Tabs.yI Tabs.x2I Tabs.y2I Tabs.finP Tabs.initP

/-! ## frames are subspaces -/

theorem red_mem (m : ℕ) : ∀ (G : List ℕ), (∀ v, m.testBit v = true → ∀ g ∈ G, m.testBit (v ^^^ g) = true) →
    ∀ b a, m.testBit a = true → m.testBit (a ^^^ b ^^^ red G b) = true := by
  intro G
  induction G with
  | nil => intro _ b a ha; simp [red, ha]
  | cons g G ih =>
    intro hcl b a ha
    have hcl' : ∀ v, m.testBit v = true → ∀ g' ∈ G, m.testBit (v ^^^ g') = true :=
      fun v hv g' hg' => hcl v hv g' (List.mem_cons_of_mem _ hg')
    simp only [red]
    cases hb : Nat.blt (b ^^^ g) b
    · simp only [cond_false]; exact ih hcl' b a ha
    · simp only [cond_true]
      have h1 : m.testBit (a ^^^ g) = true := hcl a ha g (List.mem_cons_self ..)
      have := ih hcl' (b ^^^ g) (a ^^^ g) h1
      have e : a ^^^ g ^^^ (b ^^^ g) = a ^^^ b := by
        rw [Nat.xor_assoc, ← Nat.xor_assoc g b g, Nat.xor_comm g b, Nat.xor_assoc b g g, Nat.xor_self, Nat.xor_zero]
      rw [e] at this; exact this

theorem testBit_big {m v : ℕ} (hm : m < 2 ^ 512) (hv : 512 ≤ v) : m.testBit v = false :=
  Nat.testBit_lt_two_pow (lt_of_lt_of_le hm (Nat.pow_le_pow_right (by norm_num) hv))

theorem subsp_of_frameOK {m : ℕ} {G : List ℕ} (h : frameOK m G = true) :
    IsSubsp ((range 512).filter (fun v => m.testBit v)) := by
  unfold frameOK at h
  simp only [Bool.and_eq_true, blt_iff, List.all_eq_true, List.mem_range, Bool.or_eq_true, Bool.not_eq_true',
    beq_iff] at h
  obtain ⟨⟨h0, hm⟩, hall⟩ := h
  have hcl : ∀ v, m.testBit v = true → ∀ g ∈ G, m.testBit (v ^^^ g) = true := by
    intro v hv g hg
    by_cases hv5 : v < 512
    · rcases hall v hv5 with h' | h'
      · rw [hv] at h'; cases h'
      · exact h'.1 g hg
    · rw [testBit_big hm (by omega)] at hv; cases hv
  refine ⟨?_, ?_, ?_⟩
  · simp [h0]
  · intro a ha; simp only [mem_filter, mem_range] at ha; exact ha.1
  · intro a ha b hb
    simp only [mem_filter, mem_range] at ha hb ⊢
    have hred : red G b = 0 := by
      rcases hall b hb.1 with h' | h'
      · rw [hb.2] at h'; cases h'
      · exact h'.2
    have := red_mem m G hcl b a ha.2
    rw [hred, Nat.xor_zero] at this
    refine ⟨?_, this⟩
    by_contra hc
    rw [testBit_big hm (by omega)] at this; cases this

theorem frame_subsp (i : ℕ) (hi : i < 1096) : IsSubsp (chOf i) :=
  subsp_of_frameOK (frames_all i hi)

theorem card_filt_gen (p : ℕ → Bool) (n : ℕ) : ((range n).filter (fun v => p v = true)).card =
    ((List.range n).filter p).length := by
  rw [Finset.card_def, Finset.filter_val, Finset.range_val, Multiset.range, Multiset.filter_coe, Multiset.coe_card]
  congr 1; apply List.filter_congr; intro x _; simp

theorem card_filt (m : ℕ) : ((range 512).filter (fun v => m.testBit v)).card = cntM m :=
  card_filt_gen (fun v => m.testBit v) 512

theorem card_chOf (i : ℕ) : (chOf i).card = cntM (gt 11 Tabs.maskT i) := card_filt _

theorem dim_chOf (i : ℕ) (hi : i < 1096) : dim (chOf i) = gt 11 Tabs.dimT i := by
  have h : cntM (gt 11 Tabs.maskT i) = 2 ^ gt 11 Tabs.dimT i := by
    by_cases a : i < 100
    · exact dims_0 i a (by omega)
    by_cases b : i < 200
    · exact dims_1 i b (by omega)
    by_cases c : i < 300
    · exact dims_2 i c (by omega)
    by_cases d : i < 400
    · exact dims_3 i d (by omega)
    by_cases e : i < 500
    · exact dims_4 i e (by omega)
    by_cases f : i < 600
    · exact dims_5 i f (by omega)
    by_cases g : i < 700
    · exact dims_6 i g (by omega)
    by_cases k : i < 800
    · exact dims_7 i k (by omega)
    by_cases l : i < 900
    · exact dims_8 i l (by omega)
    by_cases n : i < 1000
    · exact dims_9 i n (by omega)
    · exact dims_10 i hi (by omega)
  unfold dim; rw [card_chOf, h, Nat.log_pow (by norm_num)]

/-! ## end state -/

theorem reg_eq : MWs4.reg = regOf := rfl
theorem ch_eq : MWs4.ch = chOf := rfl

theorem rel_end : MWs4.Rel (exec trWs4) Tabs.ck26 := soundWs4.2.1
theorem inv_end : MWs4.Inv (exec trWs4) := soundWs4.2.2

theorem loc_pub (j : ℕ) (hj : j < 1501) : (exec trWs4).loc (regOf j) = .sit (chOf (fin7 j)) := by
  have : (exec trWs4).loc (MWs4.reg j) = MWs4.locOf (gt 11 Tabs.ck26 j) := rel_end j (by show j < 1697; omega)
  rw [reg_eq] at this
  rw [this, (fin_codes j hj).1]
  have e1 : lk Tabs.finP j + 2 ≠ 0 := by omega
  have e2 : lk Tabs.finP j + 2 ≠ 1 := by omega
  unfold Model.locOf
  rw [if_neg e1, if_neg e2, Nat.add_sub_cancel, ch_eq]
  rfl

theorem loc_own (j : ℕ) (hj : j < 1697) (h1 : 1501 ≤ j) : ∀ c, (exec trWs4).loc (regOf j) ≠ .sit c := by
  intro c
  have : (exec trWs4).loc (MWs4.reg j) = MWs4.locOf (gt 11 Tabs.ck26 j) := rel_end j (by show j < 1697; omega)
  rw [reg_eq] at this
  have hc := own_codes j hj h1
  rw [this]
  unfold Model.locOf
  rcases (by omega : gt 11 Tabs.ck26 j = 0 ∨ gt 11 Tabs.ck26 j = 1) with e | e
  · rw [if_pos e]; exact fun h => by cases h
  · rw [if_neg (by omega), if_pos e]; exact fun h => by cases h

/-- births: every public j is born at its json initial frame. -/
theorem mem_B_run {R : Type} [Fintype R] [DecidableEq R] (r : R) (c : Ch) :
    ∀ (tr : Trace R) (s : St R), Ev.birthPub r c ∈ tr → r ∈ (run s tr).B c := by
  intro tr
  induction tr with
  | nil => intro s h; cases h
  | cons e tr ih =>
    intro s h
    rcases List.mem_cons.1 h with h | h
    · subst h
      simp only [run, List.foldl_cons]
      apply B_sub_run tr _ c
      simp [Ev.apply]
    · simp only [run, List.foldl_cons]; exact ih _ h

theorem chkB_mem : ∀ (L : List PE) (j n : ℕ), chkB L j n = true → ∀ i, j ≤ i → i < j + n →
    ∃ e ∈ L, e.op = 0 ∧ e.r = i ∧ e.c = lk Tabs.initP i := by
  intro L
  induction L with
  | nil => intro j n h i h1 h2; cases n with
    | zero => omega
    | succ n => simp [chkB] at h
  | cons e L ih =>
    intro j n h i h1 h2
    cases n with
    | zero => omega
    | succ n =>
      simp only [chkB, Bool.and_eq_true, beq_iff] at h
      obtain ⟨⟨⟨ho, hr⟩, hc⟩, hL⟩ := h
      by_cases e1 : i = j
      · subst e1; exact ⟨e, List.mem_cons_self .., ho, hr, hc⟩
      · obtain ⟨e', he', h'⟩ := ih (j + 1) n hL i (by omega) (by omega)
        exact ⟨e', List.mem_cons_of_mem _ he', h'⟩

theorem exec_eq : exec trWs4 = run init trWs4 := rfl

theorem born (j : ℕ) (hj : j < 1501) : regOf j ∈ (exec trWs4).B (chOf (ini7 j)) := by
  obtain ⟨e, he, ho, hr, hc⟩ := chkB_mem (decodeAll Tabs.seg0) 0 1501 births_ok j (by omega) (by omega)
  rw [exec_eq]
  refine mem_B_run (regOf j) (chOf (ini7 j)) trWs4 init ?_
  have hev : MWs4.toEv e = Ev.birthPub (regOf j) (chOf (ini7 j)) := by
    unfold Model.toEv
    rw [if_pos ho, hr, hc, reg_eq, ch_eq]; rfl
  rw [← hev]
  unfold trWs4 evsWs4
  apply List.mem_map_of_mem
  simp only [chainEvs, LWs4, List.map_cons, List.flatten_cons]
  exact List.mem_append_left _ he

/-! ## endpoint charts of the mains -/

theorem lab_eq (p : Fin 104) : lab7113 p = labN p.1 := rfl
theorem isD_eq (p : Fin 104) : isD7113 p = isDN p.1 := rfl
theorem dot_eq (v q : ℕ) : dot v q = dotN v q := rfl

theorem chart_ext {m : ℕ} {c : Ch} (h : ∀ v, v ∈ c ↔ v < 512 ∧ m.testBit v = true) :
    (range 512).filter (fun v => m.testBit v) = c := by
  ext v; simp [h v]

theorem pD (p : Fin 104) (hD : isD7113 p = true) (v : ℕ) (hv : v < 512) :
    Nat.testBit (mk (ini7 (lk Tabs.x2I p))) v = decide (v = 0 ∨ v = labN p) ∧ Nat.testBit (mk (fin7 (lk Tabs.x2I p))) v = true ∧
    Nat.testBit (mk (ini7 (lk Tabs.y2I p))) v = decide (v = 0) ∧
    Nat.testBit (mk (fin7 (lk Tabs.y2I p))) v = decide (dotN v (labN p) = 0) := by
  rcases lineD p.1 p.2 v hv with h | h
  · rw [isD_eq] at hD; rw [hD] at h; cases h
  · exact h

theorem ch_line {j : ℕ} {q : ℕ} (hq : q < 512) (h : ∀ v < 512, ((mk j).testBit v = true ↔ (v = 0 ∨ v = q))) :
    chOf j = line q := by
  unfold chOf; apply chart_ext; intro v
  simp only [line, mem_insert, mem_singleton]
  constructor
  · intro hv; have hv5 : v < 512 := by rcases hv with rfl | rfl <;> omega
    exact ⟨hv5, (h v hv5).2 hv⟩
  · rintro ⟨hv5, hb⟩; exact (h v hv5).1 hb

theorem line_iff (p : Fin 104) (j : ℕ) (h : ∀ v < 512, (mk j).testBit v = decide (v = 0 ∨ v = labN p)) :
    ∀ v < 512, ((mk j).testBit v = true ↔ (v = 0 ∨ v = lab7113 p)) := by
  intro v hv; rw [h v hv, lab_eq]; exact decide_eq_true_iff

theorem ch_V {j : ℕ} (h : ∀ v < 512, (mk j).testBit v = true) : chOf j = Vc := by
  unfold chOf; apply chart_ext; intro v
  simp only [Vc, mem_range]
  constructor
  · intro hv; exact ⟨hv, h v hv⟩
  · exact fun h' => h'.1

theorem ch_zero {j : ℕ} (h : ∀ v < 512, (mk j).testBit v = decide (v = 0)) : chOf j = zeroCh := by
  unfold chOf; apply chart_ext; intro v
  simp only [zeroCh, mem_singleton]
  constructor
  · rintro rfl; refine ⟨by norm_num, ?_⟩; have := h 0 (by norm_num); simp only [mk] at this; rw [this]; rfl
  · rintro ⟨hv5, hb⟩; have := h v hv5; simp only [mk] at this; rw [this] at hb; simpa using hb

theorem ch_Hq {j q : ℕ} (h : ∀ v < 512, (mk j).testBit v = decide (dot v q = 0)) : chOf j = Hq q := by
  unfold chOf; apply chart_ext; intro v
  simp only [Hq, mem_filter, mem_range]
  constructor
  · rintro ⟨hv5, hd⟩; refine ⟨hv5, ?_⟩; have := h v hv5; simp only [mk] at this; rw [this]; simpa using hd
  · rintro ⟨hv5, hb⟩; have := h v hv5; simp only [mk] at this; rw [this] at hb; exact ⟨hv5, by simpa using hb⟩

theorem hq_y (p : Fin 104) : chOf (fin7 (lk Tabs.yI p)) = Hq (lab7113 p) :=
  ch_Hq (fun v hv => by rw [lab_eq, dot_eq]; exact (lineM p.1 p.2 v hv).2.2.2)

theorem hq_y2 (p : Fin 104) (hD : isD7113 p = true) : chOf (fin7 (lk Tabs.y2I p)) = Hq (lab7113 p) :=
  ch_Hq (fun v hv => by rw [lab_eq, dot_eq]; exact (pD p hD v hv).2.2.2)

/-! ## the word -/

/-- the ONE clause of `Word` not replayed in the kernel: final rows of the public registers = caller targets. -/
def RowsWs4 : Prop := ∀ r, pub caller7113 r = true → (exec trWs4).row r = tgt caller7113 r

theorem idx_x (p : Fin 104) : idxOf (.x p : R7) = lk Tabs.xI p := rfl

theorem regOf_idx (r : R7) : regOf (idxOf r) = r := (reg_idx r).1

theorem wordWs4 (hrow : RowsWs4) : Word caller7113 (exec trWs4) where
  reach := reach_exec legalWs4
  pub_sit := by
    intro r hp
    rw [← regOf_idx r] at hp ⊢
    have hj := (reg_idx r).2
    have := (MWs4_ok.hpb _ hj).1 hp
    change idxOf r < 1501 at this
    exact ⟨_, loc_pub _ this⟩
  own_off := by
    intro r c hp
    rw [← regOf_idx r] at hp ⊢
    have hj := (reg_idx r).2
    have : ¬ idxOf r < 1501 := by
      intro h
      have := (MWs4_ok.hpb _ hj).2 (by change idxOf r < 1501; exact h)
      have e : MWs4.pb (MWs4.reg (idxOf r)) = pub caller7113 (regOf (idxOf r)) := rfl
      rw [e] at this; rw [this] at hp; cases hp
    exact loc_own _ hj (by omega) c
  x_birth := by
    intro p
    rw [show caller7113.lab p = lab7113 p from rfl]
    have := born _ (xI_lt p.1 p.2).1
    rwa [show regOf (lk Tabs.xI p) = .x p from regOf_idx (.x p),
      ch_line (lab7113_lt p) (line_iff p _ (fun v hv => (lineM p.1 p.2 v hv).1))] at this
  x_final := by
    intro p
    have := loc_pub _ (xI_lt p.1 p.2).1
    rwa [show regOf (lk Tabs.xI p) = .x p from regOf_idx (.x p), ch_V (fun v hv => (lineM p.1 p.2 v hv).2.1)] at this
  y_birth := by
    intro p
    have := born _ (xI_lt p.1 p.2).2
    rwa [show regOf (lk Tabs.yI p) = .y p from regOf_idx (.y p), ch_zero (fun v hv => (lineM p.1 p.2 v hv).2.2.1)] at this
  y_final := by
    intro p
    have := loc_pub _ (xI_lt p.1 p.2).2
    rwa [show regOf (lk Tabs.yI p) = .y p from regOf_idx (.y p), hq_y p] at this
  x2_birth := by
    intro p hD
    rw [show caller7113.lab p = lab7113 p from rfl]
    have := born _ (x2I_lt p.1 p.2 (by rw [← isD_eq]; exact hD)).1
    rwa [show regOf (lk Tabs.x2I p) = .x2 p from regOf_idx (.x2 p),
      ch_line (lab7113_lt p) (line_iff p _ (fun v hv => (pD p hD v hv).1))] at this
  x2_final := by
    intro p hD
    have := loc_pub _ (x2I_lt p.1 p.2 (by rw [← isD_eq]; exact hD)).1
    rwa [show regOf (lk Tabs.x2I p) = .x2 p from regOf_idx (.x2 p),
      ch_V (fun v hv => (pD p hD v hv).2.1)] at this
  y2_birth := by
    intro p hD
    have := born _ (x2I_lt p.1 p.2 (by rw [← isD_eq]; exact hD)).2
    rwa [show regOf (lk Tabs.y2I p) = .y2 p from regOf_idx (.y2 p),
      ch_zero (fun v hv => (pD p hD v hv).2.2.1)] at this
  y2_final := by
    intro p hD
    have := loc_pub _ (x2I_lt p.1 p.2 (by rw [← isD_eq]; exact hD)).2
    rwa [show regOf (lk Tabs.y2I p) = .y2 p from regOf_idx (.y2 p), hq_y2 p hD] at this
  final_row := hrow

/-! ## verifier clauses -/

theorem framesWs4 : FramesSubsp (exec trWs4) := by
  obtain ⟨hB, hO, _⟩ := inv_end
  refine ⟨?_, ?_, ?_⟩
  · intro r c h
    obtain ⟨i, hi, rfl⟩ := hB r c h
    exact frame_subsp i hi
  · intro r c h
    rw [← regOf_idx r] at h
    have hj := (reg_idx r).2
    by_cases hp : idxOf r < 1501
    · rw [loc_pub _ hp] at h
      cases h
      exact frame_subsp _ (fin_codes _ hp).2
    · exact absurd h (loc_own _ hj (by omega) c)
  · intro m hm
    obtain ⟨i, i', hi, hi', h1, h2, _⟩ := hO m hm
    rw [h1, h2]; exact ⟨frame_subsp i hi, frame_subsp i' hi'⟩

theorem chartsWs4 : ChartsSubsp (exec trWs4) := by
  obtain ⟨_, hO, hP⟩ := inv_end
  refine ⟨?_, ?_⟩
  · intro m hm
    obtain ⟨i, i', hi, hi', h1, h2, _⟩ := hO m hm
    rw [h1, h2]; exact ⟨frame_subsp i hi, frame_subsp i' hi'⟩
  · intro m hm
    obtain ⟨i, i', hi, hi', h1, h2⟩ := hP m hm
    rw [h1, h2]; exact ⟨frame_subsp i hi, frame_subsp i' hi'⟩

theorem nestedWs4 : OwnedNested (exec trWs4) := by
  obtain ⟨_, hO, _⟩ := inv_end
  intro m hm
  obtain ⟨_, _, _, _, _, _, h⟩ := hO m hm
  exact h

end UniInhabitWs4

#print axioms UniInhabitWs4.wordWs4
#print axioms UniInhabitWs4.framesWs4
#print axioms UniInhabitWs4.chartsWs4
#print axioms UniInhabitWs4.nestedWs4
