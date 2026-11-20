import Nov15.FutureAttr

/-!
CFCHAIN (lane LEANCF, Nov 20).  Kernel-only.  Formalises REUSE96's CHAIN LAW (RU.md sec 1) and the epoch facts of
CARRIER8 (C8.md sec 1) on top of FutureAttr (`life_up`, `life_intake`, `life_output`, `price`, `exact_price`).

Model.  One owned register, ambient `F2^n`.  Events: `intake` (meet `A` with the current chart `Z`; allowed only before
any output = GTD inside an epoch), `output` (join `B` with `Z`), `up D` (ascent `Z <= D`, cost `dim D - dim Z`),
`down D` (free descent).  `Pot s lc := dim (A ⊔ B ⊔ Z) <= dim A + lc` is exactly FutureAttr's invariant `Inv.i6`.
A register's life (`Life`) is a list of epochs; each epoch is a *segment* (own start state) preceded by an arbitrary
legal `gap`; the segments are disjoint pieces of one trace, costs add (`Tr` is additive).
Results:
 (1) `seg_price` / `life_costs`: per-epoch `dim(A_j ⊔ B_j) - dim A_j <= cost_j`, `Σ_j cost_j <= R`.
 (2) `price_le_charts` : `rank Q[supp w, supp c] <= dim B - dim (B ∩ A)` (labels of w in B, labels of c in A^⊥).
 (3) `chain_law`  : `R >= Σ_j [dim B_j - dim (B_j ∩ A_j)] >= Σ_j rank Q[supp w_j, supp c_j]` (and over a family of registers).
 (4) `Tr.intake_le` / `Tr.output_le`: the epoch meet `A'` lies below the chart at EVERY intake, the join `B` above the chart at
     EVERY output (needed for relay legality, see CFRelay).
 Non-vacuity: `Toy.toy_chain` (two cold epochs, R = 2 = chain price = Σ rank = 2).
-/

open Module Submodule Finset PriceLemma FutureAttr Matrix

namespace CFChain

variable {n : ℕ}

inductive Ev (n : ℕ)
  | intake : Ev n
  | output : Ev n
  | up : Chart n → Ev n
  | down : Chart n → Ev n

structure ES (n : ℕ) where
  A : Chart n
  B : Chart n
  Z : Chart n

/-- one legal step with its ascent cost. -/
inductive Step : ES n → Ev n → ES n → ℕ → Prop
  | intake (s : ES n) (h : s.B = ⊥) : Step s Ev.intake ⟨s.A ⊓ s.Z, s.B, s.Z⟩ 0
  | output (s : ES n) : Step s Ev.output ⟨s.A, s.B ⊔ s.Z, s.Z⟩ 0
  | up (s : ES n) (D : Chart n) (h : s.Z ≤ D) :
      Step s (Ev.up D) ⟨s.A, s.B, D⟩ (finrank (ZMod 2) D - finrank (ZMod 2) s.Z)
  | down (s : ES n) (D : Chart n) (h : D ≤ s.Z) : Step s (Ev.down D) ⟨s.A, s.B, D⟩ 0

/-- a trace with additive cost. -/
inductive Tr : ES n → List (Ev n) → ES n → ℕ → Prop
  | nil (s : ES n) : Tr s [] s 0
  | cons {s s1 s2 : ES n} {e : Ev n} {es : List (Ev n)} {c c' : ℕ} :
      Step s e s1 c → Tr s1 es s2 c' → Tr s (e :: es) s2 (c + c')

theorem Tr.append {s s1 s2 : ES n} {es es' : List (Ev n)} {c c' : ℕ}
    (h : Tr s es s1 c) (h' : Tr s1 es' s2 c') : Tr s (es ++ es') s2 (c + c') := by
  induction h with
  | nil s => simpa using h'
  | @cons s a b e es c1 c2 hs _ ih =>
    have := Tr.cons hs (ih h')
    rwa [Nat.add_assoc]

/-- the lifetime potential = FutureAttr's `Inv.i6`. -/
def Pot (s : ES n) (lc : ℕ) : Prop :=
  finrank (ZMod 2) (s.A ⊔ s.B ⊔ s.Z : Chart n) ≤ finrank (ZMod 2) s.A + lc

theorem Step.pot {s s' : ES n} {e : Ev n} {c lc : ℕ} (h : Step s e s' c) (hp : Pot s lc) :
    Pot s' (lc + c) := by
  cases h with
  | intake hB =>
    unfold Pot at hp ⊢
    rw [hB] at hp
    have := life_intake s.A s.Z lc hp
    simp only [Nat.add_zero]
    rw [hB]
    exact this
  | output =>
    unfold Pot at hp ⊢
    simp only [Nat.add_zero]
    rw [life_output]
    exact hp
  | up D h =>
    unfold Pot at hp ⊢
    have h1 := life_up s.A s.B s.Z D h
    have h2 : finrank (ZMod 2) s.Z ≤ finrank (ZMod 2) D := Submodule.finrank_mono h
    simp only
    omega
  | down D h =>
    unfold Pot at hp ⊢
    have h1 : finrank (ZMod 2) (s.A ⊔ s.B ⊔ D : Chart n) ≤ finrank (ZMod 2) (s.A ⊔ s.B ⊔ s.Z : Chart n) :=
      Submodule.finrank_mono (sup_le_sup_left h _)
    simp only [Nat.add_zero]
    omega

theorem Tr.pot {s s' : ES n} {es : List (Ev n)} {c lc : ℕ} (h : Tr s es s' c) (hp : Pot s lc) :
    Pot s' (lc + c) := by
  induction h generalizing lc with
  | nil s => simpa using hp
  | @cons s a b e es c1 c2 hs _ ih =>
    have := ih (hs.pot hp)
    rwa [Nat.add_assoc] at this

theorem pot_start (s : ES n) (hB : s.B = ⊥) (hZ : s.Z ≤ s.A) : Pot s 0 := by
  unfold Pot
  rw [hB, sup_bot_eq, sup_eq_left.2 hZ]
  omega

/-- THE SEGMENT LEMMA: an epoch segment from a start state with `B = ⊥`, `Z <= A` costs at least
`dim (A ⊔ B) - dim A` (`= dim B - dim (A ∩ B)`).  (= third clause of FutureAttr's `Row.ok`.) -/
theorem seg_price {s0 s1 : ES n} {es : List (Ev n)} {c : ℕ} (hB : s0.B = ⊥) (hZ : s0.Z ≤ s0.A)
    (h : Tr s0 es s1 c) : finrank (ZMod 2) (s1.A ⊔ s1.B : Chart n) ≤ finrank (ZMod 2) s1.A + c := by
  have := h.pot (pot_start s0 hB hZ)
  unfold Pot at this
  have h2 : finrank (ZMod 2) (s1.A ⊔ s1.B : Chart n) ≤ finrank (ZMod 2) (s1.A ⊔ s1.B ⊔ s1.Z : Chart n) :=
    Submodule.finrank_mono le_sup_left
  omega

/-! ### the epoch meet lies below every intake chart, the join above every output chart -/

theorem Step.A_le {s s' : ES n} {e : Ev n} {c : ℕ} (h : Step s e s' c) : s'.A ≤ s.A := by
  cases h <;> first | exact inf_le_left | exact le_rfl

theorem Step.B_ge {s s' : ES n} {e : Ev n} {c : ℕ} (h : Step s e s' c) : s.B ≤ s'.B := by
  cases h <;> first | exact le_sup_left | exact le_rfl

theorem Tr.A_le {s s' : ES n} {es : List (Ev n)} {c : ℕ} (h : Tr s es s' c) : s'.A ≤ s.A := by
  induction h with
  | nil s => exact le_rfl
  | cons hs _ ih => exact ih.trans hs.A_le

theorem Tr.B_ge {s s' : ES n} {es : List (Ev n)} {c : ℕ} (h : Tr s es s' c) : s.B ≤ s'.B := by
  induction h with
  | nil s => exact le_rfl
  | cons hs _ ih => exact hs.B_ge.trans ih

/-- at every intake the final meet `A'` is below the chart of the register at that moment. -/
theorem Tr.intake_le {s s' : ES n} {es : List (Ev n)} {c : ℕ} (h : Tr s es s' c) :
    ∀ pre post, es = pre ++ Ev.intake :: post → ∃ t c1, Tr s pre t c1 ∧ s'.A ≤ t.Z := by
  induction h with
  | nil s => intro pre post h; simp at h
  | @cons s a b e es c1 c2 hs htr ih =>
    intro pre post hes
    cases pre with
    | nil =>
      simp only [List.nil_append, List.cons.injEq] at hes
      obtain ⟨rfl, _⟩ := hes
      cases hs with
      | intake _ =>
        exact ⟨s, 0, Tr.nil s, (htr.A_le).trans inf_le_right⟩
    | cons e' pre' =>
      simp only [List.cons_append, List.cons.injEq] at hes
      obtain ⟨rfl, hrest⟩ := hes
      obtain ⟨t, c3, ht, hle⟩ := ih pre' post hrest
      exact ⟨t, _, Tr.cons hs ht, hle⟩

/-- at every output the final join `B` is above the chart of the register at that moment. -/
theorem Tr.output_le {s s' : ES n} {es : List (Ev n)} {c : ℕ} (h : Tr s es s' c) :
    ∀ pre post, es = pre ++ Ev.output :: post → ∃ t c1, Tr s pre t c1 ∧ t.Z ≤ s'.B := by
  induction h with
  | nil s => intro pre post h; simp at h
  | @cons s a b e es c1 c2 hs htr ih =>
    intro pre post hes
    cases pre with
    | nil =>
      simp only [List.nil_append, List.cons.injEq] at hes
      obtain ⟨rfl, _⟩ := hes
      cases hs with
      | output =>
        exact ⟨s, 0, Tr.nil s, le_sup_right.trans htr.B_ge⟩
    | cons e' pre' =>
      simp only [List.cons_append, List.cons.injEq] at hes
      obtain ⟨rfl, hrest⟩ := hes
      obtain ⟨t, c3, ht, hle⟩ := ih pre' post hrest
      exact ⟨t, _, Tr.cons hs ht, hle⟩

/-! ### epochs and multi-epoch lifetimes -/

structure Epoch (K : Type*) (τ : Type*) (n : ℕ) where
  A : Chart n
  B : Chart n
  cost : ℕ
  w : τ → K
  u : τ → K

variable {K : Type*} {τ : Type*}

noncomputable def Epoch.drop (e : Epoch K τ n) : ℕ :=
  finrank (ZMod 2) (e.A ⊔ e.B : Chart n) - finrank (ZMod 2) e.A

theorem Epoch.drop_eq (e : Epoch K τ n) :
    e.drop = finrank (ZMod 2) e.B - finrank (ZMod 2) (e.B ⊓ e.A : Chart n) := by
  unfold Epoch.drop
  have := Submodule.finrank_sup_add_finrank_inf_eq e.A e.B
  rw [inf_comm] at this
  omega

/-- A register life: INIT at chart `Z`, then epochs.  Epoch `j` = a legal `gap`, then a segment started with
`B = ⊥`, `A0 >= chart` (`A0 = ⊤`: first intake; `A0 = chart`: virtual first intake at the previous epoch's last output,
CARRIER8's `A' = ∩ intakes ∩ Z`), whose result `(A', B)` carries the weights `w` (labels in `B`) and the cold increment `u`
(labels in `A'^⊥`; these two facts are `Inv.i4` / `Inv.i5` of FutureAttr). -/
inductive Life [Zero K] (q : τ → Fin n → ZMod 2) : Chart n → List (Epoch K τ n) → ℕ → Prop
  | nil (Z : Chart n) : Life q Z [] 0
  | cons (Z : Chart n) (gap body : List (Ev n)) (A0 : Chart n) (sg sb : ES n) (cg cb cr : ℕ)
      (w u : τ → K) (eps : List (Epoch K τ n))
      (hgap : Tr ⟨⊤, ⊥, Z⟩ gap sg cg) (hA0 : sg.Z ≤ A0)
      (hbody : Tr ⟨A0, ⊥, sg.Z⟩ body sb cb)
      (hw : ∀ t, w t ≠ 0 → q t ∈ sb.B)
      (hu : ∀ t, u t ≠ 0 → ∀ a ∈ sb.A, a ⬝ᵥ q t = 0)
      (rest : Life q sb.Z eps cr) :
      Life q Z (⟨sb.A, sb.B, cb, w, u⟩ :: eps) (cg + cb + cr)

section price
variable [Field K] [Fintype τ]

/-- `rank Q[supp w, supp u] <= dim B - dim (B ∩ A)` when `w`-labels lie in `B` and `u`-labels in `A^⊥`
(FutureAttr's `price_le` with the effective content replaced by a plain vector `u`). -/
theorem price_le_charts (q : τ → Fin n → ZMod 2) (ρ : DRow K τ) (A B : Chart n)
    (hw : ∀ t, ρ.w t ≠ 0 → q t ∈ B) (hu : ∀ s, ρ.u s ≠ 0 → ∀ a ∈ A, a ⬝ᵥ q s = 0) :
    price q ρ ≤ finrank (ZMod 2) B - finrank (ZMod 2) (B ⊓ A : Chart n) := by
  classical
  unfold price
  set lD : {t // ρ.w t ≠ 0} → Fin n → ZMod 2 := fun t => q t.1 with hlD
  set lS : {s // ρ.u s ≠ 0} → Fin n → ZMod 2 := fun s => q s.1 with hlS
  have hM : Submodule.span (ZMod 2) (Set.range lD) ≤ B := by
    apply Submodule.span_le.2
    rintro _ ⟨t, rfl⟩; exact hw t.1 t.2
  have hL : B ⊓ A ≤ perp (Submodule.span (ZMod 2) (Set.range lS)) := by
    rw [le_perp_iff]
    apply Submodule.span_le.2
    rintro _ ⟨s, rfl⟩
    show q s.1 ∈ perp (B ⊓ A)
    rw [mem_perp]
    intro y hy
    exact hu s.1 s.2 y (Submodule.mem_inf.1 hy).2
  exact (exact_price lD lS).2
    (show finrank (ZMod 2) B - finrank (ZMod 2) (B ⊓ A : Chart n) ∈ PriceSet lD lS from
      ⟨B, B ⊓ A, hM, inf_le_left, hL, rfl⟩)

/-- the chain price of an epoch. -/
noncomputable def Epoch.price (q : τ → Fin n → ZMod 2) (e : Epoch K τ n) : ℕ :=
  FutureAttr.price q (⟨e.w, e.u⟩ : DRow K τ)

/-- **CHAIN LAW.**  For a multi-epoch owned register with cold epoch intake:
`R >= Σ_j cost_j >= Σ_j [dim B_j - dim (B_j ∩ A_j)] >= Σ_j rank Q[supp w_j, supp c_j]`,
and each epoch separately `rank <= drop_j <= cost_j`. -/
theorem life_chain {q : τ → Fin n → ZMod 2} {Z : Chart n} {eps : List (Epoch K τ n)} {c : ℕ}
    (hl : Life q Z eps c) :
    (eps.map (Epoch.price q)).sum ≤ (eps.map Epoch.drop).sum ∧
    (eps.map Epoch.drop).sum ≤ (eps.map Epoch.cost).sum ∧
    (eps.map Epoch.cost).sum ≤ c ∧
    ∀ e ∈ eps, Epoch.price q e ≤ e.drop ∧ e.drop ≤ e.cost := by
  induction hl with
  | nil Z => simp
  | cons Z gap body A0 sg sb cg cb cr w u eps hgap hA0 hbody hw hu rest ih =>
    obtain ⟨i1, i2, i3, i4⟩ := ih
    have hseg := seg_price (s0 := ⟨A0, ⊥, sg.Z⟩) rfl hA0 hbody
    have hp := price_le_charts q ⟨w, u⟩ sb.A sb.B hw hu
    have hdrop : (⟨sb.A, sb.B, cb, w, u⟩ : Epoch K τ n).drop ≤ cb := by
      unfold Epoch.drop; simp only; omega
    have hpr : Epoch.price q (⟨sb.A, sb.B, cb, w, u⟩ : Epoch K τ n) ≤
        (⟨sb.A, sb.B, cb, w, u⟩ : Epoch K τ n).drop := by
      rw [Epoch.drop_eq]; exact hp
    refine ⟨?_, ?_, ?_, ?_⟩
    · simp only [List.map_cons, List.sum_cons]; omega
    · simp only [List.map_cons, List.sum_cons]; omega
    · simp only [List.map_cons, List.sum_cons]; omega
    · intro e he
      rcases List.mem_cons.1 he with rfl | he
      · exact ⟨hpr, hdrop⟩
      · exact i4 e he

theorem chain_law {q : τ → Fin n → ZMod 2} {Z : Chart n} {eps : List (Epoch K τ n)} {c : ℕ}
    (hl : Life q Z eps c) :
    (eps.map fun e => finrank (ZMod 2) e.B - finrank (ZMod 2) (e.B ⊓ e.A : Chart n)).sum ≤ c ∧
    (eps.map (Epoch.price q)).sum ≤
      (eps.map fun e => finrank (ZMod 2) e.B - finrank (ZMod 2) (e.B ⊓ e.A : Chart n)).sum := by
  obtain ⟨i1, i2, i3, _⟩ := life_chain hl
  have e1 : (eps.map fun e => finrank (ZMod 2) e.B - finrank (ZMod 2) (e.B ⊓ e.A : Chart n)) =
      eps.map Epoch.drop := by
    apply List.map_congr_left; intro e _; exact (Epoch.drop_eq e).symm
  rw [e1]
  exact ⟨i2.trans i3, i1⟩

/-- family of registers: `R = Σ_r c_r >= Σ_r Σ_j rank`. -/
theorem chain_law_family {ρ : ℕ} {q : τ → Fin n → ZMod 2} {Z : Fin ρ → Chart n}
    {eps : Fin ρ → List (Epoch K τ n)} {c : Fin ρ → ℕ} (hl : ∀ r, Life q (Z r) (eps r) (c r)) :
    ∑ r, ((eps r).map (Epoch.price q)).sum ≤ ∑ r, c r ∧
    ∑ r, ((eps r).map Epoch.drop).sum ≤ ∑ r, c r := by
  refine ⟨Finset.sum_le_sum fun r _ => ?_, Finset.sum_le_sum fun r _ => ?_⟩
  · obtain ⟨i1, i2, i3, _⟩ := life_chain (hl r); omega
  · obtain ⟨i1, i2, i3, _⟩ := life_chain (hl r); omega

end price

/-- the epochs of a family of registers, enumerated as nodes `nodes : Fin m → Epoch` (any enumeration:
`hsum` says every additive epoch statistic agrees).  The node drops add up to at most `R`. -/
theorem total_drop_le [Field K] [Fintype τ] {ρ m : ℕ} {q : τ → Fin n → ZMod 2} {Z : Fin ρ → Chart n}
    {eps : Fin ρ → List (Epoch K τ n)} {c : Fin ρ → ℕ} (hl : ∀ r, Life q (Z r) (eps r) (c r))
    (nodes : Fin m → Epoch K τ n)
    (hsum : ∀ f : Epoch K τ n → ℕ, ∑ k, f (nodes k) = ∑ r, ((eps r).map f).sum) :
    ∑ k, (nodes k).drop ≤ ∑ r, c r := by
  rw [hsum Epoch.drop]
  exact (chain_law_family hl).2

/-! ### non-vacuity: two cold epochs on one register, `R = 2 = Σ drops = Σ rank` -/
namespace Toy

def q : Fin 2 → Fin 1 → ZMod 2 := fun _ _ => 1
def ind (j : Fin 2) : Fin 2 → ℚ := fun t => if t = j then 1 else 0

def body : List (Ev 1) := [Ev.intake, Ev.up ⊤, Ev.output]

/-- epoch body: intake at chart `⊥` (so `A' = ⊥`), ascent `⊥ → ⊤` (cost 1), output (so `B = ⊤`). -/
theorem tr_body : Tr (⟨⊤, ⊥, ⊥⟩ : ES 1) body ⟨⊤ ⊓ ⊥, ⊥ ⊔ ⊤, ⊤⟩
    (0 + ((finrank (ZMod 2) (⊤ : Chart 1) - finrank (ZMod 2) (⊥ : Chart 1)) + (0 + 0))) :=
  Tr.cons (Step.intake _ rfl) (Tr.cons (Step.up _ ⊤ le_top) (Tr.cons (Step.output _) (Tr.nil _)))

theorem hw (j : Fin 2) : ∀ t, ind j t ≠ 0 → q t ∈ (⊥ ⊔ ⊤ : Chart 1) := by
  intro t _; simp

theorem hu (j : Fin 2) :
    ∀ t, ind j t ≠ 0 → ∀ a ∈ (⊤ ⊓ ⊥ : Chart 1), a ⬝ᵥ q t = 0 := by
  intro t _ a ha
  have : a = 0 := by simpa using ha
  simp [this]

noncomputable def cb0 : ℕ := 0 + ((finrank (ZMod 2) (⊤ : Chart 1) - finrank (ZMod 2) (⊥ : Chart 1)) + (0 + 0))

theorem cb0_eq : cb0 = 1 := by simp [cb0]

noncomputable def ep (j : Fin 2) : Epoch ℚ (Fin 2) 1 := ⟨⊤ ⊓ ⊥, ⊥ ⊔ ⊤, cb0, ind j, ind j⟩

theorem life2 : Life q ⊥ [ep 0, ep 1] (0 + cb0 + (0 + cb0 + 0)) :=
  Life.cons ⊥ [] body ⊤ ⟨⊤, ⊥, ⊥⟩ ⟨⊤ ⊓ ⊥, ⊥ ⊔ ⊤, ⊤⟩ 0 cb0 (0 + cb0 + 0) (ind 0) (ind 0) _
    (Tr.nil _) le_top tr_body (hw 0) (hu 0)
    (Life.cons ⊤ [Ev.down ⊥] body ⊤ ⟨⊤, ⊥, ⊥⟩ ⟨⊤ ⊓ ⊥, ⊥ ⊔ ⊤, ⊤⟩ (0 + 0) cb0 0 (ind 1) (ind 1) _
      (Tr.cons (Step.down _ ⊥ bot_le) (Tr.nil _)) le_top tr_body (hw 1) (hu 1)
      (Life.nil _))

theorem price_toy (j : Fin 2) : FutureAttr.price q (⟨ind j, ind j⟩ : DRow ℚ (Fin 2)) = 1 := by
  haveI : Nonempty {t : Fin 2 // ind j t ≠ 0} := ⟨⟨j, by simp [ind]⟩⟩
  unfold FutureAttr.price
  letI i1 : Fintype {t : Fin 2 // ind j t ≠ 0} :=
    @Subtype.fintype _ _ (fun a => @instDecidableNot _ (Classical.propDecidable _)) _
  have key := @rank_gram_D (ZMod 2) _ 1 {t : Fin 2 // ind j t ≠ 0} {t : Fin 2 // ind j t ≠ 0} i1 i1
    (fun t : {t : Fin 2 // ind j t ≠ 0} => q t.1) (fun s : {s : Fin 2 // ind j s ≠ 0} => q s.1)
  have hr : ∀ ι : Type, Nonempty ι → Set.range (fun _ : ι => (fun _ : Fin 1 => (1 : ZMod 2))) =
      {fun _ : Fin 1 => (1 : ZMod 2)} := fun ι _ => Set.range_const
  have h1 : (fun _ : Fin 1 => (1 : ZMod 2)) ≠ 0 := by
    intro h; have := congrFun h 0; simp at this
  have e : Set.range (fun t : {t // ind j t ≠ 0} => q t.1) = {fun _ : Fin 1 => (1 : ZMod 2)} :=
    hr _ inferInstance
  have hM : finrank (ZMod 2) (Submodule.span (ZMod 2)
      (Set.range (fun t : {t // ind j t ≠ 0} => q t.1)) : Chart 1) = 1 := by
    rw [e]; exact finrank_span_singleton h1
  have hN : finrank (ZMod 2) (Submodule.span (ZMod 2)
      (Set.range (fun t : {t // ind j t ≠ 0} => q t.1)) : Chart 1) = 1 := hM
  have hp : finrank (ZMod 2) (perp (Submodule.span (ZMod 2)
      (Set.range (fun s : {s // ind j s ≠ 0} => q s.1))) : Chart 1) = 0 := by
    rw [finrank_perp]
    have e' : Set.range (fun s : {s // ind j s ≠ 0} => q s.1) = {fun _ : Fin 1 => (1 : ZMod 2)} :=
      e
    rw [e', finrank_span_singleton h1]
  have hi : finrank (ZMod 2) (Submodule.span (ZMod 2)
      (Set.range (fun t : {t // ind j t ≠ 0} => q t.1)) ⊓ perp (Submodule.span (ZMod 2)
      (Set.range (fun s : {s // ind j s ≠ 0} => q s.1))) : Chart 1) = 0 :=
    Nat.le_zero.1 (hp ▸ Submodule.finrank_mono inf_le_right)
  rw [hM, hi] at key
  exact key

/-- non-vacuity: `R = 2 = Σ_j drop_j = Σ_j rank Q[supp w_j, supp c_j]`, two multi-epoch cold epochs, all bounds tight. -/
theorem toy_chain : ∃ (eps : List (Epoch ℚ (Fin 2) 1)) (c : ℕ), Life q ⊥ eps c ∧ c = 2 ∧
    (eps.map Epoch.drop).sum = 2 ∧ (eps.map (Epoch.price q)).sum = 2 := by
  refine ⟨[ep 0, ep 1], _, life2, ?_, ?_, ?_⟩
  · simp [cb0_eq]
  · have ht : finrank (ZMod 2) (⊤ : Chart 1) = 1 := by simp
    have ha : finrank (ZMod 2) (⊤ ⊓ ⊥ ⊔ (⊥ ⊔ ⊤) : Chart 1) ≤ finrank (ZMod 2) (⊤ : Chart 1) :=
      Submodule.finrank_mono le_top
    have hb : finrank (ZMod 2) (⊤ : Chart 1) ≤ finrank (ZMod 2) (⊤ ⊓ ⊥ ⊔ (⊥ ⊔ ⊤) : Chart 1) :=
      Submodule.finrank_mono (le_sup_of_le_right le_sup_right)
    have h1 : finrank (ZMod 2) (⊤ ⊓ ⊥ ⊔ (⊥ ⊔ ⊤) : Chart 1) = 1 := by omega
    have h2 : finrank (ZMod 2) (⊤ ⊓ ⊥ : Chart 1) = 0 := by
      have := Submodule.finrank_mono (inf_le_right : (⊤ ⊓ ⊥ : Chart 1) ≤ ⊥)
      have h0 : finrank (ZMod 2) (⊥ : Chart 1) = 0 := finrank_bot _ _
      omega
    simp only [Epoch.drop, ep, List.map_cons, List.map_nil, List.sum_cons, List.sum_nil, h1, h2]
    omega
  · simp [Epoch.price, ep, price_toy]

end Toy

end CFChain

#print axioms CFChain.seg_price
#print axioms CFChain.Tr.intake_le
#print axioms CFChain.Tr.output_le
#print axioms CFChain.price_le_charts
#print axioms CFChain.life_chain
#print axioms CFChain.chain_law
#print axioms CFChain.chain_law_family
#print axioms CFChain.total_drop_le
#print axioms CFChain.Toy.life2
#print axioms CFChain.Toy.price_toy
#print axioms CFChain.Toy.toy_chain
