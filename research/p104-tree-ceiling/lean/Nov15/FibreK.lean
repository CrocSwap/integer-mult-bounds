/-
FibreK .  See FibreK.md.  Formalises the AUDITED parts of internal notes,2}.md, AUDIT2.md.

Part 1  THEOREM K.  Price premise P0 as an explicit hypothesis (a `Table`: the ranks charged for a helper climb d = e - b on T,
        and for a helper MOVE of |dim step| = d on P).  The invoice F(t) = sum_r (T_r - P_r) r^(1-t) of the word is
        `FK E tb S Pi t`: a function of the ends E, the step multiset S and the climb multiset Pi only (`K_word`, `K_invoice`).
Part 2  G2 for PURE relabels.  Helpers end identity; hub gauge L in Blk(V'), M in Blk(G0) (SwapNull.Blk / Undo).
        * tail: row relabel (SwapNull.rowSw), V' = sigma^-1 V (the corrected hypothesis),  `tail_pairs`;
        * head: column relabel (SwapNull.colSw), prefix block G1 = the NEW births-at-0 set, proved DIRECTLY `head_pairs`;
        the (birth,end) multiset, hence Pi, hence F(t) by K, is unchanged.
Kernel only: no sorry, no native_decide.
-/
import Nov15.SwapNull
import Nov15.CallerCost

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace FibreK
open CallerCost

/-! ### Part 1: THEOREM K -/

/-- P0: rank tables.  `tT d` = ranks charged to T for a helper with climb d = e - b;
`tP d` = ranks charged to P for a helper MOVE with |Δdim| = d.  (Hist = (rank, count) lists.) -/
structure Table where
  tT : ℕ → Hist
  tP : ℕ → Hist

/-- A helper: birth dim, end dim, and its MOVE steps as (source dim, target dim). -/
structure Helper where
  b : ℕ
  e : ℕ
  steps : List (ℕ × ℕ)

def gap (s : ℕ × ℕ) : ℕ := Int.natAbs ((s.2 : ℤ) - s.1)

/-- F-contribution of a histogram: sum count * rank^(1-t). -/
noncomputable def Fh (l : Hist) (t : ℝ) : ℝ := (l.map fun p => (p.2 : ℝ) * (p.1 : ℝ) ^ (1 - t)).sum
noncomputable def Fi (i : Inv) (t : ℝ) : ℝ := Fh i.T t - Fh i.P t

theorem Fh_append (l m : Hist) (t : ℝ) : Fh (l ++ m) t = Fh l t + Fh m t := by simp [Fh]

theorem Fh_scale (L : ℕ) (l : Hist) (t : ℝ) : Fh (scale L l) t = L * Fh l t := by
  induction l with
  | nil => simp [Fh, scale]
  | cons p l ih =>
    simp only [Fh, scale, List.map_cons, List.sum_cons] at ih ⊢
    rw [ih]; push_cast; ring

theorem Fh_flatMap {α : Type*} (l : List α) (g : α → Hist) (t : ℝ) :
    Fh (l.flatMap g) t = (l.map fun x => Fh (g x) t).sum := by
  induction l with
  | nil => simp [Fh]
  | cons x l ih => simp [List.flatMap_cons, Fh_append, ih]

/-- invoice = caller + L * native, at the level of F. -/
theorem Fi_invoice (c n : Inv) (L : ℕ) (t : ℝ) :
    Fi (invoice c n L) t = Fi c t + L * Fi n t := by
  simp only [Fi, invoice, Fh_append, Fh_scale]; ring

/-- the native's invoice histograms from the helper list (P0). -/
def nativeInv (E : Inv) (tb : Table) (H : List Helper) : Inv :=
  ⟨E.T ++ H.flatMap fun h => tb.tT (h.e - h.b),
   E.P ++ H.flatMap fun h => h.steps.flatMap fun s => tb.tP (gap s)⟩

/-- the timed-step data: S = multiset of all helper MOVEs, Pi = multiset of climbs e - b. -/
def Ssum (H : List Helper) : Multiset (ℕ × ℕ) := ↑(H.flatMap Helper.steps)
def PiW (H : List Helper) : Multiset ℕ := ↑(H.map fun h => h.e - h.b)

/-- F as a function of the DATA (E, S, Pi). -/
noncomputable def FK (E : Inv) (tb : Table) (S : Multiset (ℕ × ℕ)) (Pi : Multiset ℕ) (t : ℝ) : ℝ :=
  Fi E t + (Pi.map fun d => Fh (tb.tT d) t).sum - (S.map fun s => Fh (tb.tP (gap s)) t).sum

theorem sum_flatMap_map {α β : Type*} (H : List α) (g : α → List β) (φ : β → ℝ) :
    ((H.flatMap g).map φ).sum = (H.map fun h => ((g h).map φ).sum).sum := by
  induction H with
  | nil => simp
  | cons h H ih => simp [List.flatMap_cons, List.map_append, List.sum_append, ih]

/-- **THEOREM K** (P0 as hypothesis `tb`): the word's F is `FK` of its (E, S, Pi). -/
theorem K_word (E : Inv) (tb : Table) (H : List Helper) (t : ℝ) :
    Fi (nativeInv E tb H) t = FK E tb (Ssum H) (PiW H) t := by
  simp only [Fi, nativeInv, FK, Ssum, PiW, Fh_append, Fh_flatMap, Multiset.map_coe, Multiset.sum_coe]
  rw [sum_flatMap_map]
  have : ∀ h : Helper, (h.steps.map fun s => Fh (tb.tP (gap s)) t).sum
      = Fh (h.steps.flatMap fun s => tb.tP (gap s)) t := fun h => (Fh_flatMap _ _ _).symm
  simp only [List.map_map, Function.comp_def, this]
  ring

/-- κ depends only on (E, S, Pi): two words with the same data have the same F, so the same roots. -/
theorem K_congr (E : Inv) (tb : Table) (H H' : List Helper)
    (hS : Ssum H' = Ssum H) (hP : PiW H' = PiW H) (t : ℝ) :
    Fi (nativeInv E tb H') t = Fi (nativeInv E tb H) t := by
  rw [K_word, K_word, hS, hP]

/-- the caller invoice of the native (calls = L) is a function of (E, S, Pi) (and the fixed caller). -/
theorem K_invoice (c E : Inv) (tb : Table) (H : List Helper) (L : ℕ) (t : ℝ) :
    Fi (invoice c (nativeInv E tb H) L) t = Fi c t + L * FK E tb (Ssum H) (PiW H) t := by
  rw [Fi_invoice, K_word]

/-- κ = a root of F: invariant when F is. -/
def IsRoot (F : ℝ → ℝ) (κ : ℝ) : Prop := F κ = 0

theorem kappa_depends_only (c E : Inv) (tb : Table) (H H' : List Helper) (L : ℕ)
    (hS : Ssum H' = Ssum H) (hP : PiW H' = PiW H) (κ : ℝ) :
    IsRoot (Fi (invoice c (nativeInv E tb H') L)) κ ↔ IsRoot (Fi (invoice c (nativeInv E tb H) L)) κ := by
  unfold IsRoot
  rw [K_invoice, K_invoice, hS, hP]

/-- the instance used by FloorD0 / V2Bridge: D0 table `tT d = tP d = [(d, 1)]`; then the helper part is
Σ_h [f(e-b) - Σ_steps f(gap)] (the per-helper D0 identity). -/
def d0Table : Table := ⟨fun d => [(d, 1)], fun d => [(d, 1)]⟩

theorem Dh_flatMap {α : Type*} (l : List α) (g : α → Hist) :
    Dh (l.flatMap g) = (l.map fun x => Dh (g x)).sum := by
  induction l with
  | nil => simp [Dh]
  | cons x l ih => simp [List.flatMap_cons, Dh_append, ih]

theorem d0_native (E : Inv) (H : List Helper) :
    Dinv (nativeInv E d0Table H) = Dinv E + (H.map fun h =>
      (fL (h.e - h.b) - (h.steps.map fun s => fL (gap s)).sum)).sum := by
  simp only [Dinv, nativeInv, Dh_append, Dh_flatMap, d0Table]
  have h1 : ∀ h : Helper, Dh [(h.e - h.b, 1)] = fL (h.e - h.b) := by intro h; simp [Dh]
  have h2 : ∀ h : Helper, (h.steps.map fun s => Dh [(gap s, 1)]).sum = (h.steps.map fun s => fL (gap s)).sum := by
    intro h; simp [Dh]
  have hs : ∀ (l : List Helper) (a b : Helper → ℝ),
      (l.map fun h => a h - b h).sum = (l.map a).sum - (l.map b).sum := by
    intro l a b
    induction l with
    | nil => simp
    | cons x l ih => simp [ih]; ring
  simp only [h1, h2]
  rw [hs]
  ring

/-! ### Part 2: G2 for pure relabels -/
section G2
open SwapNull
variable {K Reg : Type*} [Field K] [Fintype Reg] [DecidableEq Reg]

/-- helpers end identity: the final row of a helper is its own unit vector. -/
def HelpersId (H : Reg → Prop) (F : Matrix Reg Reg K) : Prop :=
  ∀ x, H x → ∀ k, F x k = (1 : Matrix Reg Reg K) x k

/-- Row x ∉ V' of L * A * M is the row of A * M. -/
theorem lrow {V' : Reg → Prop} {L : Matrix Reg Reg K} (hL : Blk V' L) (A : Matrix Reg Reg K)
    {x : Reg} (hx : ¬ V' x) (j : Reg) : (L * A) x j = A x j := by
  rw [Matrix.mul_apply, Finset.sum_eq_single x]
  · rw [hL x x (fun h => hx h.1)]; simp
  · intro i _ hi; rw [hL x i (fun h => hx h.1), Matrix.one_apply_ne (Ne.symm hi)]; simp
  · simp

/-- TAIL force: if L ∈ Blk(V'), M ∈ Blk(G0) undo a row relabel of an identity-final matrix, every moved
helper x ∉ V' has x and σ x in G0. -/
theorem tail_force {H V' G0 : Reg → Prop} {F : Matrix Reg Reg K} (hF : HelpersId H F)
    (σ : Equiv.Perm Reg) (hσH : ∀ x, H x → H (σ x))
    (hu : Undo V' G0 F (rowSw σ F)) {x : Reg} (hx : H x) (hV : ¬ V' x) (hm : σ x ≠ x) :
    G0 x ∧ G0 (σ x) := by
  obtain ⟨L, M, hL, hM, h⟩ := hu
  have key : ∀ k, M (σ x) k = (1 : Matrix Reg Reg K) x k := by
    intro k
    have h1 : (L * rowSw σ F * M) x k = M (σ x) k := by
      rw [Matrix.mul_apply, Finset.sum_eq_single (σ x)]
      · rw [lrow hL _ hV]; simp [rowSw, hF (σ x) (hσH x hx)]
      · intro j _ hj
        rw [lrow hL _ hV]; simp [rowSw, hF (σ x) (hσH x hx), Matrix.one_apply_ne (Ne.symm hj)]
      · simp
    rw [← h1, h]; exact hF x hx k
  constructor
  · by_contra hg
    have := hM (σ x) x (fun h => hg h.2)
    rw [key x, Matrix.one_apply_ne hm] at this
    simp at this
  · by_contra hg
    have := hM (σ x) (σ x) (fun h => hg h.1)
    rw [key (σ x), Matrix.one_apply_ne (Ne.symm hm)] at this
    simp at this

/-- HEAD force (direct, not by time reversal): a column relabel undone by L ∈ Blk(V), M ∈ Blk(G1):
every moved helper x ∉ V has σ⁻¹ x and x in G1. -/
theorem head_force {H V G1 : Reg → Prop} {F : Matrix Reg Reg K} (hF : HelpersId H F)
    (σ : Equiv.Perm Reg)
    (hu : Undo V G1 F (colSw σ F)) {x : Reg} (hx : H x) (hV : ¬ V x) (hm : σ x ≠ x) :
    G1 (σ.symm x) ∧ G1 x := by
  obtain ⟨L, M, hL, hM, h⟩ := hu
  have key : ∀ k, M (σ.symm x) k = (1 : Matrix Reg Reg K) x k := by
    intro k
    have h1 : (L * colSw σ F * M) x k = M (σ.symm x) k := by
      rw [Matrix.mul_apply, Finset.sum_eq_single (σ.symm x)]
      · rw [lrow hL _ hV]; simp [colSw, hF x hx]
      · intro j _ hj
        rw [lrow hL _ hV]
        have : x ≠ σ j := fun e => hj (by rw [e]; simp)
        simp [colSw, hF x hx, Matrix.one_apply_ne this]
      · simp
    rw [← h1, h]; exact hF x hx k
  have hy : σ.symm x ≠ x := fun e => hm (by
    have := congrArg σ e; simpa using this.symm)
  constructor
  · by_contra hg
    have := hM (σ.symm x) (σ.symm x) (fun h => hg h.1)
    rw [key (σ.symm x), Matrix.one_apply_ne (Ne.symm hy)] at this
    simp at this
  · by_contra hg
    have := hM (σ.symm x) x (fun h => hg h.2)
    rw [key x, Matrix.one_apply_ne hy] at this
    simp at this

/-! counting lemma: equal cardinality, differing only on birth-0 elements, so equal birth multisets -/
theorem map_birth_eq (β : Reg → ℕ) (A B : Finset Reg) (hc : A.card = B.card)
    (hA : ∀ x ∈ A, x ∉ B → β x = 0) (hB : ∀ x ∈ B, x ∉ A → β x = 0) :
    A.val.map β = B.val.map β := by
  classical
  have hne : ∀ b : ℕ, b ≠ 0 → A.filter (fun x => b = β x) = B.filter (fun x => b = β x) := by
    intro b hb
    ext x
    simp only [Finset.mem_filter]
    constructor
    · rintro ⟨ha, e⟩
      refine ⟨?_, e⟩
      by_contra hn
      exact hb (e.trans (hA x ha hn))
    · rintro ⟨ha, e⟩
      refine ⟨?_, e⟩
      by_contra hn
      exact hb (e.trans (hB x ha hn))
  apply Multiset.ext.2
  intro b
  rw [Multiset.count_map, Multiset.count_map]
  simp only [← Finset.filter_val, Finset.card_val]
  by_cases hb : b = 0
  · subst hb
    have h1 := Finset.card_filter_add_card_filter_not (s := A) (fun x => 0 = β x)
    have h2 := Finset.card_filter_add_card_filter_not (s := B) (fun x => 0 = β x)
    have h3 : A.filter (fun x => ¬ (0 = β x)) = B.filter (fun x => ¬ (0 = β x)) := by
      ext x
      simp only [Finset.mem_filter]
      constructor
      · rintro ⟨ha, e⟩
        refine ⟨?_, e⟩
        by_contra hn
        exact e (hA x ha hn).symm
      · rintro ⟨ha, e⟩
        refine ⟨?_, e⟩
        by_contra hn
        exact e (hB x ha hn).symm
    rw [h3] at h1
    omega
  · rw [hne b hb]

variable (β ε : Reg → ℕ) (d : ℕ)

/-- birth/end pairs of the helpers `Hs`. -/
def pairs (Hs : Finset Reg) : Multiset (ℕ × ℕ) := Hs.val.map fun x => (β x, ε x)
/-- after a tail relabel x keeps its birth but takes σ x's end. -/
def pairsTail (σ : Equiv.Perm Reg) (Hs : Finset Reg) : Multiset (ℕ × ℕ) :=
  Hs.val.map fun x => (β x, ε (σ x))
/-- after a head relabel x takes σ x's birth but keeps its end. -/
def pairsHead (σ : Equiv.Perm Reg) (Hs : Finset Reg) : Multiset (ℕ × ℕ) :=
  Hs.val.map fun x => (β (σ x), ε x)

theorem sigma_H {H : Reg → Prop} (σ : Equiv.Perm Reg) (hσ : ∀ x, ¬ H x → σ x = x) :
    ∀ x, H x → H (σ x) := by
  intro x hx
  by_contra h
  have h1 := hσ _ h
  have : σ x = x := σ.injective h1
  exact h (by rw [this]; exact hx)

theorem split_map {α γ : Type*} (s : Multiset α) (p : α → Prop) [DecidablePred p] (f : α → γ) :
    s.map f = (s.filter p).map f + (s.filter (fun x => ¬ p x)).map f := by
  rw [← Multiset.map_add, Multiset.filter_add_not]

/-- the (birth, end) pair multiset determines the climb multiset Pi -/
def PiOf (ps : Multiset (ℕ × ℕ)) : Multiset ℕ := ps.map fun p => p.2 - p.1

theorem PiW_eq (H : List Helper) : PiW H = PiOf (↑(H.map fun h => (h.b, h.e)) : Multiset (ℕ × ℕ)) := by
  simp [PiW, PiOf, Multiset.map_coe, List.map_map, Function.comp_def]

section Pairs

theorem symm_fix (σ : Equiv.Perm Reg) (x : Reg) (h : σ.symm x = x) : σ x = x := by
  have h2 := congrArg σ h
  rw [Equiv.apply_symm_apply] at h2
  exact h2.symm

/-- **G2, TAIL case.**  Hypotheses (AUDIT2): helpers end identity; G0-members are born at 0; the V-enders
(= the helpers ending at the single chart `d`) are exactly V ⊆ H; σ permutes helpers only; hub gauge
L ∈ Blk(V'), M ∈ Blk(G0) with V' = σ⁻¹ V.  Then the (birth,end) multiset is unchanged. -/
theorem tail_pairs {H V G0 : Reg → Prop} [DecidablePred H] [DecidablePred V]
    {F : Matrix Reg Reg K} (hF : HelpersId H F) (σ : Equiv.Perm Reg) (hσ : ∀ x, ¬ H x → σ x = x)
    (hVH : ∀ x, V x → H x) (hE : ∀ x, H x → (ε x = d ↔ V x)) (hG : ∀ x, G0 x → β x = 0)
    (hu : Undo (fun x => V (σ x)) G0 F (rowSw σ F)) :
    pairsTail β ε σ (Finset.univ.filter H) = pairs β ε (Finset.univ.filter H) := by
  classical
  have hσH := sigma_H σ hσ
  have hσs : ∀ x, ¬ H x → σ.symm x = x := fun x hx => (Equiv.symm_apply_eq σ).2 (hσ x hx).symm
  have hσsH := sigma_H σ.symm hσs
  set Hs : Finset Reg := Finset.univ.filter H with hHs
  have memH : ∀ x, x ∈ Hs ↔ H x := by intro x; simp [hHs]
  have F1 : ∀ x, H x → ¬ V (σ x) → σ x ≠ x → β x = 0 ∧ β (σ x) = 0 := by
    intro x hx hv hm
    obtain ⟨a, b⟩ := tail_force hF σ hσH hu hx hv hm
    exact ⟨hG _ a, hG _ b⟩
  have F2 : ∀ x, H x → ¬ V (σ x) → β (σ x) = β x := by
    intro x hx hv
    by_cases hm : σ x = x
    · rw [hm]
    · obtain ⟨a, b⟩ := F1 x hx hv hm; rw [a, b]
  set V' : Finset Reg := Hs.filter (fun x => V (σ x)) with hV'
  set Vf : Finset Reg := Hs.filter V with hVf
  have hcard : V'.card = Vf.card := by
    apply Finset.card_bij (fun x _ => σ x)
    · intro x hx
      simp only [hV', hVf, Finset.mem_filter, memH] at hx ⊢
      exact ⟨hσH x hx.1, hx.2⟩
    · intro x _ y _ e; exact σ.injective e
    · intro y hy
      simp only [hV', hVf, Finset.mem_filter, memH] at hy ⊢
      refine ⟨σ.symm y, ⟨hσsH y hy.1, by simpa using hy.2⟩, by simp⟩
  have F4 : ∀ x ∈ V', x ∉ Vf → β x = 0 := by
    intro x hx hxn
    simp only [hV', hVf, Finset.mem_filter, memH] at hx hxn
    have hnV : ¬ V x := fun h => hxn ⟨hx.1, h⟩
    have hmu : σ (σ.symm x) ≠ σ.symm x := by
      intro e
      rw [Equiv.apply_symm_apply] at e
      exact hnV (by have := symm_fix σ x e.symm; rw [← this]; exact hx.2)
    have := (F1 _ (hσsH x hx.1) (by rw [Equiv.apply_symm_apply]; exact hnV) hmu).2
    rwa [Equiv.apply_symm_apply] at this
  have F5 : ∀ y ∈ Vf, y ∉ V' → β y = 0 := by
    intro y hy hyn
    simp only [hV', hVf, Finset.mem_filter, memH] at hy hyn
    have hnV : ¬ V (σ y) := fun h => hyn ⟨hy.1, h⟩
    have hm : σ y ≠ y := fun e => hnV (by rw [e]; exact hy.2)
    exact (F1 y hy.1 hnV hm).1
  have hV'map : V'.val.map β = Vf.val.map β :=
    map_birth_eq β V' Vf hcard F4 F5
  -- the non-V' part is carried to the non-V part by σ
  set N1 : Finset Reg := Hs.filter (fun x => ¬ V (σ x)) with hN1
  set N2 : Finset Reg := Hs.filter (fun x => ¬ V x) with hN2
  have hN : N2 = N1.map σ.toEmbedding := by
    ext y
    simp only [hN1, hN2, Finset.mem_filter, Finset.mem_map, memH, Equiv.coe_toEmbedding]
    constructor
    · rintro ⟨hy, hv⟩
      exact ⟨σ.symm y, ⟨hσsH y hy, by simpa using hv⟩, by simp⟩
    · rintro ⟨x, ⟨hx, hv⟩, rfl⟩
      exact ⟨hσH x hx, hv⟩
  unfold pairsTail pairs
  rw [split_map Hs.val (fun x => V (σ x)), split_map Hs.val V]
  congr 1
  · have e1 : (Hs.val.filter (fun x => V (σ x))).map (fun x => (β x, ε (σ x))) =
        V'.val.map (fun x => (β x, d)) := by
      apply Multiset.map_congr rfl
      intro x hx
      have hx' : x ∈ V' := hx
      simp only [hV', Finset.mem_filter, memH] at hx'
      rw [(hE (σ x) (hσH x hx'.1)).2 hx'.2]
    have e2 : (Hs.val.filter V).map (fun x => (β x, ε x)) = Vf.val.map (fun x => (β x, d)) := by
      apply Multiset.map_congr rfl
      intro x hx
      have hx' : x ∈ Vf := hx
      simp only [hVf, Finset.mem_filter, memH] at hx'
      rw [(hE x hx'.1).2 hx'.2]
    rw [e1, e2]
    have h3 : ∀ A : Finset Reg, A.val.map (fun x => (β x, d)) = (A.val.map β).map (fun b => (b, d)) := by
      intro A; rw [Multiset.map_map]; rfl
    rw [h3, h3, hV'map]
  · have e : (Hs.val.filter (fun x => ¬ V (σ x))) = N1.val := rfl
    have e' : (Hs.val.filter (fun x => ¬ V x)) = N2.val := rfl
    rw [e, e', hN, Finset.map_val, Multiset.map_map]
    apply Multiset.map_congr rfl
    intro x hx
    have hx' : x ∈ N1 := hx
    simp only [hN1, Finset.mem_filter, memH] at hx'
    simp [F2 x hx'.1 hx'.2]

/-- **G2, HEAD case, proved directly** (no time reversal).  A head relabel x ↦ birth of σ x, same end;
the hub undoing it is L ∈ Blk(V) (the V-enders are unchanged) and the prefix M ∈ Blk(G1), where G1 is the set
of helpers born at 0 in the NEW word (`G1 x → β (σ x) = 0`; the head-side analogue of V' = σ⁻¹ V). -/
theorem head_pairs {H V G1 : Reg → Prop} [DecidablePred H] [DecidablePred V]
    {F : Matrix Reg Reg K} (hF : HelpersId H F) (σ : Equiv.Perm Reg) (hσ : ∀ x, ¬ H x → σ x = x)
    (hVH : ∀ x, V x → H x) (hE : ∀ x, H x → (ε x = d ↔ V x)) (hG : ∀ x, G1 x → β (σ x) = 0)
    (hu : Undo V G1 F (colSw σ F)) :
    pairsHead β ε σ (Finset.univ.filter H) = pairs β ε (Finset.univ.filter H) := by
  classical
  have hσH := sigma_H σ hσ
  have hσs : ∀ x, ¬ H x → σ.symm x = x := fun x hx => (Equiv.symm_apply_eq σ).2 (hσ x hx).symm
  have hσsH := sigma_H σ.symm hσs
  set Hs : Finset Reg := Finset.univ.filter H with hHs
  have memH : ∀ x, x ∈ Hs ↔ H x := by intro x; simp [hHs]
  have F1 : ∀ x, H x → ¬ V x → σ x ≠ x → β x = 0 ∧ β (σ x) = 0 := by
    intro x hx hv hm
    obtain ⟨a, b⟩ := head_force hF σ hu hx hv hm
    refine ⟨?_, hG _ b⟩
    have := hG _ a
    rwa [Equiv.apply_symm_apply] at this
  have F2 : ∀ x, H x → ¬ V x → β (σ x) = β x := by
    intro x hx hv
    by_cases hm : σ x = x
    · rw [hm]
    · obtain ⟨a, b⟩ := F1 x hx hv hm; rw [a, b]
  set Vf : Finset Reg := Hs.filter V with hVf
  set Vs : Finset Reg := Vf.map σ.toEmbedding with hVs
  have hcard : Vs.card = Vf.card := Finset.card_map _
  have F4 : ∀ x ∈ Vs, x ∉ Vf → β x = 0 := by
    intro x hx hxn
    simp only [hVs, hVf, Finset.mem_map, Finset.mem_filter, memH, Equiv.coe_toEmbedding] at hx hxn
    obtain ⟨w, ⟨hw, hv⟩, rfl⟩ := hx
    have hnV : ¬ V (σ w) := fun h => hxn ⟨hσH w hw, h⟩
    have hm : σ (σ w) ≠ σ w := fun e => hnV (by have := σ.injective e; rw [this]; exact hv)
    exact (F1 (σ w) (hσH w hw) hnV hm).1
  have F5 : ∀ x ∈ Vf, x ∉ Vs → β x = 0 := by
    intro x hx hxn
    simp only [hVs, hVf, Finset.mem_map, Finset.mem_filter, memH, Equiv.coe_toEmbedding] at hx hxn
    have hnV : ¬ V (σ.symm x) := fun h => hxn ⟨σ.symm x, ⟨hσsH x hx.1, h⟩, by simp⟩
    have hm : σ (σ.symm x) ≠ σ.symm x := by
      intro e
      rw [Equiv.apply_symm_apply] at e
      exact hnV (by rw [← e]; exact hx.2)
    have := (F1 (σ.symm x) (hσsH x hx.1) hnV hm).2
    rwa [Equiv.apply_symm_apply] at this
  have hmap : Vs.val.map β = Vf.val.map β := map_birth_eq β Vs Vf hcard F4 F5
  unfold pairsHead pairs
  rw [split_map Hs.val V]
  conv_rhs => rw [split_map Hs.val V]
  congr 1
  · have e1 : (Hs.val.filter V).map (fun x => (β (σ x), ε x)) = Vf.val.map (fun x => (β (σ x), d)) := by
      apply Multiset.map_congr rfl
      intro x hx
      have hx' : x ∈ Vf := hx
      simp only [hVf, Finset.mem_filter, memH] at hx'
      rw [(hE x hx'.1).2 hx'.2]
    have e2 : (Hs.val.filter V).map (fun x => (β x, ε x)) = Vf.val.map (fun x => (β x, d)) := by
      apply Multiset.map_congr rfl
      intro x hx
      have hx' : x ∈ Vf := hx
      simp only [hVf, Finset.mem_filter, memH] at hx'
      rw [(hE x hx'.1).2 hx'.2]
    rw [e1, e2]
    have h3 : Vf.val.map (fun x => (β (σ x), d)) = (Vs.val.map β).map (fun b => (b, d)) := by
      rw [hVs, Finset.map_val, Multiset.map_map, Multiset.map_map]; rfl
    have h4 : Vf.val.map (fun x => (β x, d)) = (Vf.val.map β).map (fun b => (b, d)) := by
      rw [Multiset.map_map]; rfl
    rw [h3, h4, hmap]
  · have e' : (Hs.val.filter (fun x => ¬ V x)) = (Hs.filter (fun x => ¬ V x)).val := rfl
    rw [e']
    apply Multiset.map_congr rfl
    intro x hx
    have hx' : x ∈ Hs.filter (fun x => ¬ V x) := hx
    simp only [Finset.mem_filter, memH] at hx'
    simp [F2 x hx'.1 hx'.2]

/-! ### G2 ⇒ Π ⇒ F: the combined statement -/

theorem tail_Pi {H V G0 : Reg → Prop} [DecidablePred H] [DecidablePred V]
    {F : Matrix Reg Reg K} (hF : HelpersId H F) (σ : Equiv.Perm Reg) (hσ : ∀ x, ¬ H x → σ x = x)
    (hVH : ∀ x, V x → H x) (hE : ∀ x, H x → (ε x = d ↔ V x)) (hG : ∀ x, G0 x → β x = 0)
    (hu : Undo (fun x => V (σ x)) G0 F (rowSw σ F)) :
    PiOf (pairsTail β ε σ (Finset.univ.filter H)) = PiOf (pairs β ε (Finset.univ.filter H)) := by
  rw [tail_pairs β ε d hF σ hσ hVH hE hG hu]

theorem head_Pi {H V G1 : Reg → Prop} [DecidablePred H] [DecidablePred V]
    {F : Matrix Reg Reg K} (hF : HelpersId H F) (σ : Equiv.Perm Reg) (hσ : ∀ x, ¬ H x → σ x = x)
    (hVH : ∀ x, V x → H x) (hE : ∀ x, H x → (ε x = d ↔ V x)) (hG : ∀ x, G1 x → β (σ x) = 0)
    (hu : Undo V G1 F (colSw σ F)) :
    PiOf (pairsHead β ε σ (Finset.univ.filter H)) = PiOf (pairs β ε (Finset.univ.filter H)) := by
  rw [head_pairs β ε d hF σ hσ hVH hE hG hu]

/-- G2 + K: a hub-undoable pure tail relabel that keeps the step multiset S (SwapNull.stays_multiset) leaves
F(t), hence κ, unchanged. -/
theorem tail_F_null {H V G0 : Reg → Prop} [DecidablePred H] [DecidablePred V]
    {F : Matrix Reg Reg K} (hF : HelpersId H F) (σ : Equiv.Perm Reg) (hσ : ∀ x, ¬ H x → σ x = x)
    (hVH : ∀ x, V x → H x) (hE : ∀ x, H x → (ε x = d ↔ V x)) (hG : ∀ x, G0 x → β x = 0)
    (hu : Undo (fun x => V (σ x)) G0 F (rowSw σ F))
    (E : Inv) (tb : Table) (S : Multiset (ℕ × ℕ)) (t : ℝ) :
    FK E tb S (PiOf (pairsTail β ε σ (Finset.univ.filter H))) t =
      FK E tb S (PiOf (pairs β ε (Finset.univ.filter H))) t := by
  rw [tail_Pi β ε d hF σ hσ hVH hE hG hu]

theorem head_F_null {H V G1 : Reg → Prop} [DecidablePred H] [DecidablePred V]
    {F : Matrix Reg Reg K} (hF : HelpersId H F) (σ : Equiv.Perm Reg) (hσ : ∀ x, ¬ H x → σ x = x)
    (hVH : ∀ x, V x → H x) (hE : ∀ x, H x → (ε x = d ↔ V x)) (hG : ∀ x, G1 x → β (σ x) = 0)
    (hu : Undo V G1 F (colSw σ F))
    (E : Inv) (tb : Table) (S : Multiset (ℕ × ℕ)) (t : ℝ) :
    FK E tb S (PiOf (pairsHead β ε σ (Finset.univ.filter H))) t =
      FK E tb S (PiOf (pairs β ε (Finset.univ.filter H))) t := by
  rw [head_Pi β ε d hF σ hσ hVH hE hG hu]

end Pairs

/-! ### C3 (R1's 3-cycle) is NOT undoable once V' = σ⁻¹ V is used (Lean check of AUDIT2's observation) -/
section C3
open SwapNull

/-- a = (5→9), b = (0→7), c = (0→9) on Fin 3; σ: a ↦ b, b ↦ c, c ↦ a. -/
def c3β : Fin 3 → ℕ := ![5, 0, 0]
def c3ε : Fin 3 → ℕ := ![9, 7, 9]
def c3σ : Equiv.Perm (Fin 3) := Equiv.swap 0 1 * Equiv.swap 1 2

theorem c3σ_apply : c3σ 0 = 1 ∧ c3σ 1 = 2 ∧ c3σ 2 = 0 := by decide

/-- the pair multiset changes (Π {4,7,9} → {2,9,9} in R1's words) -/
theorem c3_pairs_change :
    pairsTail c3β c3ε c3σ Finset.univ ≠ pairs c3β c3ε Finset.univ := by decide

theorem c3_not_undoable (G0 : Fin 3 → Prop) (hG : ∀ x, G0 x → c3β x = 0) :
    ¬ Undo (fun x => (c3ε (c3σ x) = 9 : Prop)) G0 (1 : Matrix (Fin 3) (Fin 3) ℚ)
        (rowSw c3σ 1) := by
  intro hu
  have := tail_pairs (K := ℚ) (H := fun _ => True) (V := fun x => c3ε x = 9) c3β c3ε 9
    (F := 1) (fun _ _ _ => rfl) c3σ (fun x hx => absurd trivial hx) (fun _ _ => trivial)
    (fun x _ => Iff.rfl) hG hu
  have h2 : (Finset.univ.filter (fun _ : Fin 3 => True)) = (Finset.univ : Finset (Fin 3)) := by simp
  rw [h2] at this
  exact c3_pairs_change this
end C3

#print axioms K_word
#print axioms K_congr
#print axioms K_invoice
#print axioms kappa_depends_only
#print axioms d0_native
#print axioms tail_force
#print axioms head_force
#print axioms tail_pairs
#print axioms head_pairs
#print axioms tail_F_null
#print axioms head_F_null
#print axioms c3_not_undoable

end G2

end FibreK
