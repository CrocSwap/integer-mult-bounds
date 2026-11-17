/-
FloorD0 (lane LEAN-NEXT18, Nov 16): closes FloorEndToEnd's hypothesis H1 (per-paid-stay cost ≥ κ).
See FloorD0.md.

Cost model (PRICEKIT pricekit.py `native_from_word` + `Dsum`, wrapped by REBUILDKIT harness `price`):
* a native word is ONE call; the invoice adds its T and P histograms once per J event (L = 17 on #7623);
* helper (public, non-main) r:  T[dim final(r) − dim initial(r)];  every MOVE a → b:  P[|dim b − dim a|];
* D0 = Σ_r (T_r − P_r)·f(r) with f(r) = r ln r (`Dsum`, ranks r > 1; f(0) = f(1) = 0 so all ranks agree).
So the invoice's D0 = caller D0 + L · (native D0) (`histD0_invoice`), and "D0/call" of the helper layer
is the word's own helper D0 = Σ_{h ∈ H} [f(dim fin − dim ini) − Σ_{moves of h} f(|Δ dim|)] (`helperD0`).

Results (f abstract: convex on [0,∞), f 0 = 0; κ_f := f 2 − 2 f 1):
* `stay_ge`: h_e(a,b) = f(e−a) − f(b−a) − f(e−b) ≥ κ_f when b − a ≥ 1, e − b ≥ 1 (GAPMAP §1 charge).
* `chD0_attr`: the GAPMAP attribution identity on any ascending move chain (D0 = Σ_moves h_e);
  `attr_final`: the final move is charged 0.
* `chain_D0_ge`: chain of k moves ⇒ D0 ≥ κ_f (k − 1).
* word level: `chain_run` (a public register's MOVE records form a chain ini → final),
  `dep_move` (a departure from c in the projection is a MOVE out of c), `fibre_le` (#stays of h ≤ #moves − 1),
  `helper_D0_ge` (per helper), `helperD0_ge` : κ_f · #stays ≤ helperD0, for EVERY accepted word.
* `kap_fL` : κ_{r ln r} = 2 ln 2.   `floor_D0_classK`: class K + H2 ⇒ helperD0 ≥ 780·2 ln 2 ≥ 1081.309.
* `chD0_id`: with rank weight f = id the same invoice is DescentPrice's (credit − paid = −2·descents).
-/
import Nov15.FloorEndToEnd
import Nov15.FloorCert
import Nov15.JunkLB2
import Nov15.DescentPrice
import Mathlib.Analysis.Complex.ExponentialBounds

open Finset

set_option linter.unusedSectionVars false

namespace FloorD0

/-! ## 1. The abstract per-stay charge -/

section Abstract
variable (f : ℝ → ℝ)

/-- κ_f = f(2) − 2 f(1): the least charge of a non-final stop. -/
def kap : ℝ := f 2 - 2 * f 1

variable {f}

/-- **per-stay charge ≥ κ_f** (convexity only). -/
theorem stay_ge (cvx : ConvexOn ℝ (Set.Ici (0 : ℝ)) f) (e a b : ℝ) (hab : 1 ≤ b - a)
    (hbe : 1 ≤ e - b) : kap f ≤ JunkLB2.h f e a b := by
  set x := b - a; set y := e - b
  have hxy : e - a = x + y := by simp only [x, y]; ring
  have s1 := JunkLB2.two_point cvx (lo := 1) (hi := x + y) (y := x) (z := 1 + y)
    (by norm_num) (by linarith) hab (by linarith) (by linarith) (by linarith) (by ring)
  have s2 := JunkLB2.two_point cvx (lo := 1) (hi := 1 + y) (y := y) (z := 2)
    (by norm_num) (by linarith) hbe (by linarith) (by norm_num) (by linarith) (by ring)
  simp only [kap, JunkLB2.h, hxy]; linarith

theorem kap_nonneg (cvx : ConvexOn ℝ (Set.Ici (0 : ℝ)) f) (hf0 : f 0 = 0) : 0 ≤ kap f := by
  have := JunkLB2.two_point cvx (lo := 0) (hi := 2) (y := 1) (z := 1)
    le_rfl (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num)
  simp only [kap]; linarith

/-- the final move (into the register's last chart) is charged 0. -/
theorem attr_final (hf0 : f 0 = 0) (a e : ℝ) : JunkLB2.h f e a e = 0 := by
  simp [JunkLB2.h, hf0]

/-- PRICEKIT instance: f(r) = r ln r gives κ = 2 ln 2. -/
theorem kap_fL : kap JunkLB2.fL = 2 * Real.log 2 := by
  simp [kap, JunkLB2.fL]

end Abstract

/-! ## 2. Per-call normalisation: the invoice is caller + L · native -/

/-- D0 of a (T, P) histogram given as rank lists: Σ_T f − Σ_P f. -/
noncomputable def histD0 (f : ℝ → ℝ) (T P : List ℕ) : ℝ :=
  (T.map fun r : ℕ => f (r : ℝ)).sum - (P.map fun r : ℕ => f (r : ℝ)).sum

/-- PRICEKIT `invoice`: native T and P are added once per call (L = #J events = 17 on #7623).
Hence D0(invoice) = D0(caller) + L · D0(native), and a native quantity quoted "per call" is the
word's own D0 (÷ L undoes the multiplicity exactly). -/
theorem histD0_invoice (f : ℝ → ℝ) (Tc Pc Tn Pn : List ℕ) (L : ℕ) :
    histD0 f (Tc ++ (List.replicate L Tn).flatten) (Pc ++ (List.replicate L Pn).flatten) =
      histD0 f Tc Pc + L * histD0 f Tn Pn := by
  induction L with
  | zero => simp [histD0]
  | succ n ih =>
    simp only [histD0, List.replicate_succ, List.flatten_cons, List.map_append, List.sum_append] at ih ⊢
    push_cast; linarith

/-! ## 3. Move chains and their D0 -/

section Chain
open FloorE2E
variable {K Reg C : Type*} [Field K] [DecidableEq K] [Fintype Reg] [DecidableEq Reg]
  [PartialOrder C] [DecidableEq C]

/-- a list of MOVE records chaining chart a to chart b. -/
def MChain : C → List (Mv K Reg C) → C → Prop
  | a, [], b => a = b
  | a, m :: ms, b => m.tail = a ∧ MChain m.head ms b

variable (f : ℝ → ℝ) (dim : C → ℕ)

/-- PRICEKIT P-charge of one MOVE: f(|dim head − dim tail|). -/
noncomputable def mvCost (m : Mv K Reg C) : ℝ := f |(dim m.head : ℝ) - dim m.tail|

/-- D0 of a register that goes a → b by the moves ms: f(dim b − dim a) − Σ f(|Δ|). -/
noncomputable def chD0 (a b : C) (ms : List (Mv K Reg C)) : ℝ :=
  f ((dim b : ℝ) - dim a) - (ms.map (mvCost f dim)).sum

def Asc (ms : List (Mv K Reg C)) : Prop := ∀ m ∈ ms, dim m.tail < dim m.head

variable {f dim}

lemma chain_le : ∀ (a : C) (ms : List (Mv K Reg C)) (b : C), MChain a ms b → Asc dim ms →
    dim a ≤ dim b
  | a, [], b, hc, _ => by simp only [MChain] at hc; rw [hc]
  | a, m :: ms, b, ⟨h1, h2⟩, hA => by
    have := chain_le m.head ms b h2 fun x hx => hA x (List.mem_cons_of_mem _ hx)
    have := hA m List.mem_cons_self
    rw [h1] at this; omega

lemma chD0_cons (a b : C) (m : Mv K Reg C) (ms : List (Mv K Reg C)) (hm : m.tail = a)
    (hlt : dim m.tail < dim m.head) :
    chD0 f dim a b (m :: ms) = JunkLB2.h f (dim b) (dim a) (dim m.head) + chD0 f dim m.head b ms := by
  have : |(dim m.head : ℝ) - dim m.tail| = (dim m.head : ℝ) - dim a := by
    rw [hm] at hlt ⊢
    have : (dim a : ℝ) < dim m.head := by exact_mod_cast hlt
    rw [abs_of_pos (by linarith)]
  simp only [chD0, List.map_cons, List.sum_cons, mvCost, this, JunkLB2.h]; ring

/-- **GAPMAP §1 attribution identity**: D0 = Σ_moves h_e(dim tail, dim head), e = dim b. -/
theorem chD0_attr (hf0 : f 0 = 0) : ∀ (a : C) (ms : List (Mv K Reg C)) (b : C), MChain a ms b →
    Asc dim ms →
    chD0 f dim a b ms = (ms.map fun m => JunkLB2.h f (dim b) (dim m.tail) (dim m.head)).sum
  | a, [], b, hc, _ => by simp only [MChain] at hc; subst hc; simp [chD0, hf0]
  | a, m :: ms, b, ⟨h1, h2⟩, hA => by
    rw [chD0_cons a b m ms h1 (hA m List.mem_cons_self),
      chD0_attr hf0 m.head ms b h2 fun x hx => hA x (List.mem_cons_of_mem _ hx)]
    simp [h1]

/-- **chain floor**: a chain of k = ms.length + 1 moves has D0 ≥ κ_f · (k − 1). Each non-final
move (= the arrival into a chart the register later leaves, i.e. a paid stay) is charged ≥ κ_f. -/
theorem chain_D0_ge (cvx : ConvexOn ℝ (Set.Ici (0 : ℝ)) f) (hf0 : f 0 = 0) :
    ∀ (ms : List (Mv K Reg C)) (a : C) (m : Mv K Reg C) (b : C), MChain a (m :: ms) b →
      Asc dim (m :: ms) → kap f * ms.length ≤ chD0 f dim a b (m :: ms)
  | [], a, m, b, ⟨h1, h2⟩, hA => by
    simp only [MChain] at h2
    rw [chD0_cons a b m [] h1 (hA m List.mem_cons_self)]
    subst h2; simp [chD0, hf0, JunkLB2.h]
  | m' :: ms, a, m, b, ⟨h1, h2⟩, hA => by
    have hA' : Asc dim (m' :: ms) := fun x hx => hA x (List.mem_cons_of_mem _ hx)
    have ih := chain_D0_ge cvx hf0 ms m.head m' b h2 hA'
    rw [chD0_cons a b m _ h1 (hA m List.mem_cons_self)]
    have hlt1 := hA m List.mem_cons_self
    rw [h1] at hlt1
    obtain ⟨h3, h4⟩ := h2
    have hlt2 := hA' m' List.mem_cons_self
    have hle := chain_le m'.head ms b h4 fun x hx => hA' x (List.mem_cons_of_mem _ hx)
    rw [h3] at hlt2
    have hs := stay_ge cvx (dim b) (dim a) (dim m.head)
      (by have : (dim a : ℝ) + 1 ≤ dim m.head := by exact_mod_cast hlt1
          linarith)
      (by have : (dim m.head : ℝ) + 1 ≤ dim b := by exact_mod_cast (show dim m.head + 1 ≤ dim b by omega)
          linarith)
    simp only [List.length_cons]; push_cast; linarith

/-! ### link to DescentPrice: rank weight f = id is DescentPrice's invoice -/

def dimList (a : C) (ms : List (Mv K Reg C)) : List ℤ := (dim a : ℤ) :: ms.map fun m => (dim m.head : ℤ)

lemma dimList_paid : ∀ (a : C) (ms : List (Mv K Reg C)) (b : C), MChain a ms b →
    DescentPrice.paid (dimList (dim := dim) a ms) =
      (ms.map fun m => |(dim m.head : ℤ) - dim m.tail|).sum
  | a, [], b, _ => rfl
  | a, m :: ms, b, ⟨h1, h2⟩ => by
    have ih := dimList_paid m.head ms b h2
    simp only [dimList, List.map_cons] at ih ⊢
    rw [DescentPrice.paid, ih, h1]; simp

lemma dimList_last : ∀ (a : C) (ms : List (Mv K Reg C)) (b : C), MChain a ms b →
    (dimList (dim := dim) a ms).getLast (by simp [dimList]) = dim b
  | a, [], b, hc => by simp only [MChain] at hc; subst hc; rfl
  | a, m :: ms, b, ⟨_, h2⟩ => by
    have ih := dimList_last m.head ms b h2
    simp only [dimList, List.map_cons] at ih ⊢
    rw [List.getLast_cons (by simp)]; exact ih

/-- with rank weight f = id (PRICEKIT's S instead of D0) the per-register invoice is DescentPrice's:
credit − paid = −2·(descent ranks). For a helper chain (strict ascent) this is 0. -/
theorem chD0_id (a b : C) (ms : List (Mv K Reg C)) (hc : MChain a ms b) :
    chD0 (fun x => x) dim a b ms = -2 * (DescentPrice.desc (dimList (dim := dim) a ms) : ℝ) := by
  have h := DescentPrice.helper_identity (dim a : ℤ) (ms.map fun m => (dim m.head : ℤ))
  have hp := dimList_paid (dim := dim) a ms b hc
  have hl := dimList_last (dim := dim) a ms b hc
  simp only [dimList] at hp hl
  rw [hp, hl] at h
  have h' : ((ms.map fun m => |(dim m.head : ℤ) - dim m.tail|).sum : ℝ) - ((dim b : ℝ) - dim a) =
      2 * (DescentPrice.desc (dimList (dim := dim) a ms) : ℝ) := by exact_mod_cast h
  have e : (ms.map (mvCost (fun x => x) dim)).sum =
      ((ms.map fun m => |(dim m.head : ℤ) - dim m.tail|).sum : ℝ) := by
    push_cast [List.map_map]
    congr 1; apply List.map_congr_left; intro m _; simp [mvCost]
  simp only [chD0, e]; linarith

end Chain

/-! ## 4. The word: helper D0 and its per-stay floor -/

section Word
open FloorE2E
variable {K Reg C : Type*} [Field K] [DecidableEq K] [Fintype Reg] [DecidableEq Reg]
  [PartialOrder C] [DecidableEq C]

/-- a public register's MOVE records form a chain from its current chart to its final chart. -/
theorem chain_run (Pub : Finset Reg) (r : Reg) (hr : r ∈ Pub) :
    ∀ (s : GSt K Reg C) (w : List (GEv K Reg C)) (a : C), LegalG Pub s w → s.loc r = some a →
      ∃ b, (grun s w).loc r = some b ∧ MChain a ((moves s w).filter fun m => m.reg = r) b
  | s, [], a, _, ha => ⟨a, ha, by simp [moves, MChain]⟩
  | s, e :: es, a, ⟨he, hL⟩, ha => by
    cases e with
    | move r' c' =>
      obtain ⟨a', ha', -, -⟩ := he
      by_cases hrr : r' = r
      · subst hrr
        rw [ha] at ha'; cases ha'
        obtain ⟨b, hb, hc⟩ := chain_run Pub r' hr _ es c' hL (by simp [gstep])
        refine ⟨b, hb, ?_⟩
        simp only [moves, mvOf, ha, List.filter_append]
        simp [MChain, hc]
      · have hloc : (gstep s (.move r' c')).loc r = some a := by
          simp [gstep, Ne.symm hrr, ha]
        obtain ⟨b, hb, hc⟩ := chain_run Pub r hr _ es a hL hloc
        refine ⟨b, hb, ?_⟩
        simp only [moves, mvOf, ha', List.filter_append]
        simpa [hrr] using hc
    | init o c' =>
      have hor : r ≠ o := fun h => he.1 (h ▸ hr)
      have hloc : (gstep s (.init o c')).loc r = some a := by
        simp [gstep, hor, ha]
      obtain ⟨b, hb, hc⟩ := chain_run Pub r hr _ es a hL hloc
      exact ⟨b, hb, by simpa [moves, mvOf] using hc⟩
    | clear o =>
      have hor : r ≠ o := fun h => he.1 (h ▸ hr)
      have hloc : (gstep s (.clear o)).loc r = some a := by
        simp [gstep, hor, ha]
      obtain ⟨b, hb, hc⟩ := chain_run Pub r hr _ es a hL hloc
      exact ⟨b, hb, by simpa [moves, mvOf] using hc⟩
    | add i j x =>
      obtain ⟨b, hb, hc⟩ := chain_run Pub r hr _ es a hL (by simpa [gstep] using ha)
      exact ⟨b, hb, by simpa [moves, mvOf] using hc⟩
    | scale i u =>
      obtain ⟨b, hb, hc⟩ := chain_run Pub r hr _ es a hL (by simpa [gstep] using ha)
      exact ⟨b, hb, by simpa [moves, mvOf] using hc⟩
    | copy i j x =>
      obtain ⟨b, hb, hc⟩ := chain_run Pub r hr _ es a hL (by simpa [gstep] using ha)
      exact ⟨b, hb, by simpa [moves, mvOf] using hc⟩

open ExportLaw in
/-- a departure of a public register r from chart c (in the projection) is a MOVE of r out of c. -/
theorem dep_move (Pub : Finset Reg) (r : Reg) (hr : r ∈ Pub) (c : C) :
    ∀ (s : GSt K Reg C) (w : List (GEv K Reg C)), LegalG Pub s w →
      0 < nDep {r} (projFrom c s w) → ∃ m ∈ moves s w, m.reg = r ∧ m.tail = c
  | s, [], _, h => by simp [projFrom, nDep] at h
  | s, e :: es, ⟨he, hL⟩, h => by
    rw [projFrom, nDep_append] at h
    by_cases h2 : 0 < nDep {r} (projFrom c (gstep s e) es)
    · obtain ⟨m, hm, h3⟩ := dep_move Pub r hr c _ es hL h2
      exact ⟨m, by simp only [moves, List.mem_append]; exact Or.inr hm, h3⟩
    · have h1 : 0 < nDep {r} (pev c s e) := by omega
      cases e with
      | move r' c' =>
        by_cases hl : s.loc r' = some c
        · by_cases hrr : r' = r
          · subst hrr
            exact ⟨⟨r', c, c', s.row r'⟩, by simp [moves, mvOf, hl], rfl, rfl⟩
          · exfalso; by_cases h' : c' = c <;> simp [pev, hl, h', nDep, hrr] at h1
        · exfalso; by_cases h' : c' = c <;> simp [pev, hl, h', nDep] at h1
      | clear o =>
        exfalso
        have : o ≠ r := fun h => he.1 (h ▸ hr)
        by_cases hl : s.loc o = some c <;> simp [pev, hl, nDep, this] at h1
      | init o c' => exfalso; by_cases h' : c' = c <;> simp [pev, h', nDep] at h1
      | add i j a => exfalso; by_cases hl : s.loc i = some c <;> simp [pev, hl, nDep] at h1
      | scale i u => exfalso; by_cases hl : s.loc i = some c <;> simp [pev, hl, nDep] at h1
      | copy i j a => exfalso; by_cases hl : s.loc i = some c <;> simp [pev, hl, nDep] at h1

end Word

/-! ## 5. Helper D0 of a word and the floor -/

section Floor
open FloorE2E
variable {K Reg C : Type*} [Field K] [DecidableEq K] [Fintype Reg] [DecidableEq Reg]
  [PartialOrder C] [DecidableEq C]

/-- dimension of an optional chart (0 for none; never used for public registers). -/
def locD (dim : C → ℕ) : Option C → ℝ
  | some c => dim c
  | none => 0

/-- **PRICEKIT D0 of one register of the word** (one call): T-term f(dim final − dim initial) minus
the P-terms f(|dim b − dim a|) of its own MOVEs. -/
noncomputable def regD0 (f : ℝ → ℝ) (dim : C → ℕ) (ini : Reg → Option C) (w : List (GEv K Reg C))
    (r : Reg) : ℝ :=
  f (locD dim ((grun (s0 ini) w).loc r) - locD dim (ini r)) -
    (((moves (s0 ini) w).filter fun m => m.reg = r).map (mvCost f dim)).sum

/-- **helper D0 per call** = Σ over helpers (public non-mains) of their PRICEKIT D0 (GAPMAP's
"helpers 9,946.29 D0/call" on #7623). -/
noncomputable def helperD0 (f : ℝ → ℝ) (dim : C → ℕ) (H : Finset Reg) (ini : Reg → Option C)
    (w : List (GEv K Reg C)) : ℝ :=
  ∑ h ∈ H, regD0 f dim ini w h

variable [Fintype C] {Pub H : Finset Reg} {ini : Reg → Option C} {w : List (GEv K Reg C)}

open ExportLaw in
/-- every paid stay of helper h is the tail of a MOVE of h other than its first: #stays(h) ≤ #moves(h) − 1. -/
theorem fibre_le (hA : Accepted Pub H ini w) (h : Reg) (hh : h ∈ H) (a : C) (ha : ini h = some a) :
    ((stays H ini w).filter fun p => p.1 = h).card ≤
      ((moves (s0 ini) w).filter fun m => m.reg = h).length - 1 := by
  have hP := hA.helpers_pub hh
  obtain ⟨b, -, hc⟩ := chain_run Pub h hP (s0 ini) w a hA.legal ha
  have key : ∀ p ∈ (stays H ini w).filter (fun p => p.1 = h),
      p.2 ≠ a ∧ ∃ m ∈ (moves (s0 ini) w).filter (fun m => m.reg = h), m.tail = p.2 := by
    intro p hp
    obtain ⟨hs, hp1⟩ := Finset.mem_filter.1 hp
    simp only [stays, Finset.mem_filter, Finset.mem_univ, true_and] at hs
    obtain ⟨-, hini, hdep⟩ := hs
    rw [hp1] at hini hdep
    rw [proj, nDep_append, births, nDep_born, zero_add] at hdep
    obtain ⟨m, hm, hmr, hmt⟩ := dep_move Pub h hP p.2 (s0 ini) w hA.legal hdep
    exact ⟨fun e => hini (by rw [ha, e]), m, List.mem_filter.2 ⟨hm, by simpa using hmr⟩, hmt⟩
  generalize (moves (s0 ini) w).filter (fun m => m.reg = h) = L at hc key
  cases L with
  | nil =>
    have : (stays H ini w).filter (fun p => p.1 = h) = ∅ := by
      ext p
      simp only [Finset.notMem_empty, iff_false]
      intro hp
      obtain ⟨-, m, hm, -⟩ := key p hp
      simp at hm
    rw [this]; simp
  | cons m0 ms =>
    have h0 : m0.tail = a := hc.1
    have hsub : (stays H ini w).filter (fun p => p.1 = h) ⊆ (ms.map fun m => (h, m.tail)).toFinset := by
      intro p hp
      obtain ⟨hne, m, hm, hmt⟩ := key p hp
      have hp1 : p.1 = h := (Finset.mem_filter.1 hp).2
      rcases List.mem_cons.1 hm with rfl | hm'
      · exact absurd (hmt.symm.trans h0) hne
      · rw [List.mem_toFinset, List.mem_map]; exact ⟨m, hm', Prod.ext hp1.symm hmt⟩
    calc _ ≤ (ms.map fun m => (h, m.tail)).toFinset.card := Finset.card_le_card hsub
      _ ≤ (ms.map fun m => (h, m.tail)).length := List.toFinset_card_le _
      _ = _ := by simp

/-- **per helper**: κ_f · #(paid stays of h) ≤ D0(h). Needs only `dim` strictly monotone on the chart
order (for the verifier: a < b iff span a ⊊ span b, so dim a < dim b). -/
theorem helper_D0_ge (f : ℝ → ℝ) (dim : C → ℕ) (hdim : ∀ a b : C, a < b → dim a < dim b)
    (cvx : ConvexOn ℝ (Set.Ici (0 : ℝ)) f) (hf0 : f 0 = 0)
    (hA : Accepted Pub H ini w) (h : Reg) (hh : h ∈ H) :
    kap f * ((stays H ini w).filter fun p => p.1 = h).card ≤ regD0 f dim ini w h := by
  have hP := hA.helpers_pub hh
  obtain ⟨a, ha⟩ := Option.ne_none_iff_exists'.1 ((hA.pub_ini h).1 hP)
  have hfib := fibre_le hA h hh a ha
  obtain ⟨b, hb, hc⟩ := chain_run Pub h hP (s0 ini) w a hA.legal ha
  have hasc : Asc dim ((moves (s0 ini) w).filter fun m => m.reg = h) := by
    intro m hm
    obtain ⟨hm, hmr⟩ := List.mem_filter.1 hm
    have hmr' : m.reg = h := by simpa using hmr
    exact hdim _ _ ((moves_facts Pub (s0 ini) w hA.legal m hm).2.1 (hmr' ▸ hP))
  have hreg : regD0 f dim ini w h =
      chD0 f dim a b ((moves (s0 ini) w).filter fun m => m.reg = h) := by
    simp only [regD0, chD0, hb, ha, locD]
  have hk := kap_nonneg cvx hf0
  rw [hreg]
  generalize (moves (s0 ini) w).filter (fun m => m.reg = h) = L at hfib hc hasc
  cases L with
  | nil =>
    simp only [MChain] at hc; subst hc
    have : ((stays H ini w).filter fun p => p.1 = h).card = 0 := by simpa using hfib
    rw [this]; simp [chD0, hf0]
  | cons m ms =>
    have := chain_D0_ge cvx hf0 ms a m b hc hasc
    simp only [List.length_cons, Nat.add_sub_cancel] at hfib
    calc kap f * (((stays H ini w).filter fun p => p.1 = h).card : ℝ)
        ≤ kap f * ms.length := mul_le_mul_of_nonneg_left (by exact_mod_cast hfib) hk
      _ ≤ _ := this

/-- **H1 closed**: on EVERY accepted word, κ_f · #(paid helper stays) ≤ helper D0. -/
theorem helperD0_ge (f : ℝ → ℝ) (dim : C → ℕ) (hdim : ∀ a b : C, a < b → dim a < dim b)
    (cvx : ConvexOn ℝ (Set.Ici (0 : ℝ)) f) (hf0 : f 0 = 0) (hA : Accepted Pub H ini w) :
    kap f * (stays H ini w).card ≤ helperD0 f dim H ini w := by
  have hmap : ∀ p ∈ stays H ini w, p.1 ∈ H := by
    intro p hp
    simp only [stays, Finset.mem_filter, Finset.mem_univ, true_and] at hp
    exact hp.1
  rw [Finset.card_eq_sum_card_fiberwise hmap]
  push_cast; rw [Finset.mul_sum]
  exact Finset.sum_le_sum fun h hh => helper_D0_ge f dim hdim cvx hf0 hA h hh

/-- the PRICEKIT instance f(r) = r ln r: helper D0 ≥ 2 ln 2 · #stays. -/
theorem helperD0_ge_fL (dim : C → ℕ) (hdim : ∀ a b : C, a < b → dim a < dim b)
    (hA : Accepted Pub H ini w) :
    2 * Real.log 2 * (stays H ini w).card ≤ helperD0 JunkLB2.fL dim H ini w := by
  have := helperD0_ge JunkLB2.fL dim hdim JunkLB2.fL_convex JunkLB2.fL0 hA
  rwa [kap_fL] at this

/-- **H2** (the remaining checked input, Python): x(w) restricted to the 18,868 support columns
satisfies the 892 exported rows (each row an instance of λ/α/β/γ/u with D = D₀) and its objective
is ≤ #paid stays (FloorEndToEnd's `objective_le` on the instances). -/
def H2 (n : ℕ) : Prop :=
  ∃ x : Fin FloorCert.nCols → ℝ, (∀ j, 0 ≤ x j) ∧
    (∀ i, FloorCert.b i ≤ ∑ j, FloorCert.A i j * x j) ∧ ∑ j, FloorCert.c j * x j ≤ n

/-- **floor_D0_classK.** Every class-K word has helper D0 ≥ 780 · 2 ln 2 ≥ 1,081.309 D0/call,
with H2 the only hypothesis beyond the model (dim strictly monotone on the chart order). -/
theorem floor_D0_classK {Kfin : Finset Reg} {D : KData C (Reg → K)} (dim : C → ℕ)
    (hdim : ∀ a b : C, a < b → dim a < dim b) (hK : ClassK Pub H Kfin ini w D)
    (hH2 : H2 (stays H ini w).card) :
    780 * (2 * Real.log 2) ≤ helperD0 JunkLB2.fL dim H ini w ∧
      (1081.309 : ℝ) ≤ helperD0 JunkLB2.fL dim H ini w := by
  obtain ⟨x, hx, hAx, hobj⟩ := hH2
  have h780 := FloorCert.stops_ge_780 (𝕜 := ℝ) x hx hAx (stays H ini w) hobj
  have hD := helperD0_ge_fL dim hdim hK.acc
  have hl := Real.log_two_gt_d9
  have h1 : 780 * (2 * Real.log 2) ≤ helperD0 JunkLB2.fL dim H ini w := by nlinarith
  exact ⟨h1, by linarith⟩

end Floor

end FloorD0

#print axioms FloorD0.stay_ge
#print axioms FloorD0.kap_fL
#print axioms FloorD0.histD0_invoice
#print axioms FloorD0.chD0_attr
#print axioms FloorD0.chain_D0_ge
#print axioms FloorD0.chD0_id
#print axioms FloorD0.chain_run
#print axioms FloorD0.dep_move
#print axioms FloorD0.fibre_le
#print axioms FloorD0.helper_D0_ge
#print axioms FloorD0.helperD0_ge
#print axioms FloorD0.helperD0_ge_fL
#print axioms FloorD0.floor_D0_classK
