/-
SharedCourier .  See SharedCourier.md.  Generator lemma behind GEN-B GB1's first win
(internal notes, section 3): a SHARED-SNAPSHOT courier picks up a row once and gives scaled copies to k
consumers along an ascending (time, frame) chain.

 (1) EXACTNESS   (TokenCancel semantics): consumers' rows = base + (total coefficient) * snapshot + courier token
                 (shared: one token e_y; separate: one token e_{y_j} per give).  Modulo tokens both plans agree;
                 TC (xclose_exact) removes a token exactly with one ADD of a token holder.
 (2) COST        (Theorem K, D0 table): D0 of a courier = f(e-b) - sum f(hop gap).  Shared (gaps a0, a_1..a_{k+1}) vs k
                 separate couriers (gaps a0, P_j, R-P_j): exact difference, shared <= separate for k >= 1 (equal at
                 k = 1), strict for k >= 2 when a0, R >= 1.
 (3) LEGALITY    `legal_tail_iff`: the shared plan is Legal iff every consumer is present at its stop chart, stops are
                 not z, and no stop except the last is V (MOVE never leaves V).  Ascent is NOT part of Legal.
Kernel only: no sorry, no native_decide.
-/
import Nov15.TokenCancel
import Nov15.FibreK
import Mathlib.Analysis.SpecialFunctions.Log.NegMulLog
import Mathlib.Analysis.Convex.SpecificFunctions.Basic

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace SharedCourier
open TokenCancel

/-! ## (1) Exactness -/
section Exact
variable {K Reg C : Type*} [Field K] [DecidableEq Reg] [DecidableEq C]

/-- a give: (consumer, coefficient, stop chart). -/
abbrev Give (K Reg C : Type*) := Reg × K × C

/-- total coefficient delivered to `r`. -/
def cf : List (Give K Reg C) → Reg → K
  | [], _ => 0
  | g :: G, r => (if g.1 = r then g.2.1 else 0) + cf G r

/-- the chain of stops: MOVE the courier to the stop, then ADD `a` copies of its row into the consumer. -/
def tailEvs (y : Reg) : List (Give K Reg C) → List (Ev K Reg C)
  | [] => []
  | g :: G => .move y g.2.2 :: .add g.1 y g.2.1 g.2.2 :: tailEvs y G

/-- SHARED courier: born at the snapshot chart, picks `p` once (coefficient 1), then walks the chain. -/
def sharedEvs (y p : Reg) (cp : C) (G : List (Give K Reg C)) : List (Ev K Reg C) :=
  .born y cp :: .add y p 1 cp :: tailEvs y G

/-- ONE courier for ONE give: pick, one stop, deliver, clear. -/
def seg (y p : Reg) (cp : C) (g : Give K Reg C) : List (Ev K Reg C) :=
  [.born y cp, .add y p 1 cp, .move y g.2.2, .add g.1 y g.2.1 g.2.2, .clear y g.2.2]

def sepEvs (p : Reg) (cp : C) : List (Reg × Give K Reg C) → List (Ev K Reg C)
  | [] => []
  | q :: L => seg q.1 p cp q.2 ++ sepEvs p cp L

lemma run_append (s : St K Reg C) (l m : List (Ev K Reg C)) : run s (l ++ m) = run (run s l) m := by
  induction l generalizing s with
  | nil => rfl
  | cons e l ih => exact ih _

lemma tail_row (y : Reg) (G : List (Give K Reg C)) (hy : ∀ g ∈ G, g.1 ≠ y) :
    ∀ (s : St K Reg C) (r : Reg), (run s (tailEvs y G)).row r =
      if r = y then s.row y else s.row r + cf G r • s.row y := by
  induction G with
  | nil => intro s r; by_cases h : r = y <;> simp [tailEvs, run, cf, h]
  | cons g G ih =>
    intro s r
    have hg : g.1 ≠ y := hy g (by simp)
    have hG : ∀ g' ∈ G, g'.1 ≠ y := fun g' h => hy g' (by simp [h])
    simp only [tailEvs, run, step]
    rw [ih hG]
    by_cases hr : r = y
    · subst hr
      simp [hg.symm, Function.update_of_ne hg.symm]
    · simp only [hr, if_false, cf, Function.update_apply, hg.symm, ite_false]
      by_cases h1 : g.1 = r
      · subst h1; simp [Function.update_self, hg]; module
      · simp [h1, Ne.symm h1]

/-- SHARED plan: every non-courier register `r` ends with `row r + cf G r • (row p + e_y)`. -/
theorem shared_row (s : St K Reg C) (y p : Reg) (cp : C) (G : List (Give K Reg C))
    (hyp : y ≠ p) (hy : ∀ g ∈ G, g.1 ≠ y) (r : Reg) (hr : r ≠ y) :
    (run s (sharedEvs y p cp G)).row r = s.row r + cf G r • (s.row p + Pi.single y (1 : K)) := by
  simp only [sharedEvs, run, step]
  rw [tail_row y G hy]
  have hrow : (Function.update (Function.update s.row y (Pi.single y 1)) y
      (Function.update s.row y (Pi.single y 1) y + (1 : K) • Function.update s.row y (Pi.single y 1) p)) y
      = Pi.single y 1 + s.row p := by simp [Function.update_of_ne hyp.symm]
  simp [hr, hrow, Function.update_of_ne hyp.symm]
  abel

/-- one separate courier. -/
theorem seg_row (s : St K Reg C) (y p : Reg) (cp : C) (g : Give K Reg C)
    (hyp : y ≠ p) (hgy : g.1 ≠ y) (hgp : g.1 ≠ p) (r : Reg) :
    (run s (seg y p cp g)).row r =
      if r = y then 0 else if r = g.1 then s.row r + g.2.1 • (Pi.single y (1 : K) + s.row p) else s.row r := by
  simp only [seg, run, step]
  by_cases hr : r = y
  · subst hr; simp
  · by_cases h1 : r = g.1
    · subst h1
      simp [hr, hyp.symm, hgy, hgp]
      try (rw [add_comm (Pi.single y (1 : K))])
    · simp [hr, h1, Function.update_of_ne hr, Function.update_of_ne h1]

/-- token part delivered by the separate couriers (one token per give). -/
def tokSep : List (Reg × Give K Reg C) → Reg → (Reg → K)
  | [], _ => 0
  | q :: L, r => (if q.2.1 = r then q.2.2.1 • Pi.single q.1 (1 : K) else 0) + tokSep L r

/-- SEPARATE plan (one courier per give, distinct couriers, none a consumer / `p`):
non-courier register `r` ends with `row r + cf G r • row p + (one token per give)`. -/
theorem sep_row (p : Reg) (cp : C) (L : List (Reg × Give K Reg C))
    (hcp : ∀ q ∈ L, q.1 ≠ p) (hcons : ∀ q ∈ L, q.2.1 ≠ p)
    (hcc : ∀ q ∈ L, ∀ q' ∈ L, q'.2.1 ≠ q.1) :
    ∀ (s : St K Reg C) (r : Reg), (∀ q ∈ L, r ≠ q.1) →
      (run s (sepEvs p cp L)).row r = s.row r + cf (L.map Prod.snd) r • s.row p + tokSep L r := by
  induction L with
  | nil => intro s r _; simp [sepEvs, run, cf, tokSep]
  | cons q L ih =>
    intro s r hr
    have hq : q.2.1 ≠ q.1 := hcc q (by simp) q (by simp)
    have hrq : r ≠ q.1 := hr q (by simp)
    have hL := ih (fun q' h => hcp q' (by simp [h])) (fun q' h => hcons q' (by simp [h]))
      (fun q' h q'' h' => hcc q' (by simp [h]) q'' (by simp [h']))
    simp only [sepEvs, run_append, List.map_cons, cf, tokSep]
    rw [hL _ r (fun q' h => hr q' (by simp [h]))]
    have hp' : (run s (seg q.1 p cp q.2)).row p = s.row p := by
      rw [seg_row s q.1 p cp q.2 (hcp q (by simp)) hq (hcons q (by simp))]
      simp [Ne.symm (hcp q (by simp)), Ne.symm (hcons q (by simp))]
    rw [hp', seg_row s q.1 p cp q.2 (hcp q (by simp)) hq (hcons q (by simp))]
    by_cases h1 : r = q.2.1
    · subst h1; simp [hrq, Ne.symm hq]; module
    · simp [hrq, h1, Ne.symm h1]

/-- **(1) EXACTNESS.**  Same plan (`G = L.map snd`).  Remove the courier tokens (shared: `cf G r • e_y`; separate: `tokSep`):
every non-courier register ends with the same row `row r + cf G r • row p`, in both builds. -/
theorem exact_mod_tokens (s : St K Reg C) (y p : Reg) (cp : C) (L : List (Reg × Give K Reg C))
    (hyp : y ≠ p) (hy : ∀ q ∈ L, q.2.1 ≠ y)
    (hcp : ∀ q ∈ L, q.1 ≠ p) (hcons : ∀ q ∈ L, q.2.1 ≠ p)
    (hcc : ∀ q ∈ L, ∀ q' ∈ L, q'.2.1 ≠ q.1)
    (r : Reg) (hr : r ≠ y) (hrs : ∀ q ∈ L, r ≠ q.1) :
    (run s (sharedEvs y p cp (L.map Prod.snd))).row r - cf (L.map Prod.snd) r • Pi.single y (1 : K)
      = (run s (sepEvs p cp L)).row r - tokSep L r := by
  rw [shared_row s y p cp _ hyp (fun g hg => by obtain ⟨q, hq, rfl⟩ := List.mem_map.mp hg; exact hy q hq) r hr, sep_row p cp L hcp hcons hcc s r hrs]
  module

/-- **TC (courier token cleanup).**  A consumer holding `τ + k • e_y` (τ free of the courier token) and a token holder
`x` with row `e_y` at the same chart: one ADD of `-k` yields exactly τ, and `-k` is the only coefficient that does.
(Instance of TokenCancel's XCLOSE exactness, `DesignLaws.xclose_exact`, re-derived by hand here.) -/
theorem tc_cleanup (z V : C) (s : St K Reg C) (r x y : Reg) (c : C) (hrx : r ≠ x)
    (hr : s.loc r = some c) (hx : s.loc x = some c) (hxrow : s.row x = Pi.single y (1 : K))
    (τ : Reg → K) (hτ : τ y = 0) (k : K) (hrow : s.row r = τ + k • Pi.single y (1 : K)) :
    LegalEv z V s (.add r x (-k) c) ∧ (step s (.add r x (-k) c)).row r = τ ∧
    ∀ a, (step s (.add r x a c)).row r = τ → a = -k := by
  refine ⟨⟨hrx, hr, hx⟩, by simp [step, hrow, hxrow], fun a ha => ?_⟩
  have h := congrFun ha y
  simp [step, hxrow, hrow, hτ] at h
  linear_combination h

end Exact

/-! ## (3) Legality -/
section Legality
variable {K Reg C : Type*} [Field K] [DecidableEq Reg] [DecidableEq C]

/-- stop conditions, relative to a location map `ℓ` of the consumers: stop not `z`, consumer present at the stop,
the courier's previous chart is not `V` (a MOVE never leaves `V`). -/
def okTail (ℓ : Reg → Option C) (z V : C) : C → List (Give K Reg C) → Prop
  | _, [] => True
  | c0, g :: G => c0 ≠ V ∧ g.2.2 ≠ z ∧ ℓ g.1 = some g.2.2 ∧ okTail ℓ z V g.2.2 G

lemma okTail_upd (z V : C) (ℓ : Reg → Option C) (y : Reg) (v : Option C) (G : List (Give K Reg C))
    (hy : ∀ g ∈ G, g.1 ≠ y) (c0 : C) :
    okTail (Function.update ℓ y v) z V c0 G ↔ okTail ℓ z V c0 G := by
  induction G generalizing c0 with
  | nil => simp [okTail]
  | cons g G ih =>
    have hg : g.1 ≠ y := hy g (by simp)
    simp only [okTail, Function.update_of_ne hg]
    rw [ih (fun g' h => hy g' (by simp [h]))]

/-- **(3) LEGALITY of the chain.**  The courier sits at `c0`.  The chain of stops is Legal (TokenCancel's co-presence,
no MOVE into `z`, no MOVE out of `V`) iff `okTail`: every consumer is at its stop chart, no stop is `z`, and every stop
but the last is not `V`.  Nothing about ORDER of the charts: ascent is an extra constraint of the frame structure. -/
theorem legal_tail_iff (z V : C) (y : Reg) (G : List (Give K Reg C)) (hy : ∀ g ∈ G, g.1 ≠ y) :
    ∀ (s : St K Reg C) (c0 : C), s.loc y = some c0 →
      (Legal z V s (tailEvs y G) ↔ okTail s.loc z V c0 G) := by
  induction G with
  | nil => intro s c0 _; simp [tailEvs, Legal, okTail]
  | cons g G ih =>
    intro s c0 hc
    have hg : g.1 ≠ y := hy g (by simp)
    have hG : ∀ g' ∈ G, g'.1 ≠ y := fun g' h => hy g' (by simp [h])
    have hloc : (step (step s (.move y g.2.2)) (.add g.1 y g.2.1 g.2.2)).loc
        = Function.update s.loc y (some g.2.2) := by simp [step]
    have hsy : (step (step s (.move y g.2.2)) (.add g.1 y g.2.1 g.2.2)).loc y = some g.2.2 := by
      rw [hloc]; simp
    have IH := ih hG _ _ hsy
    rw [hloc, okTail_upd z V s.loc y _ G hG] at IH
    simp only [tailEvs, Legal]
    rw [show (Legal z V (step (step s (.move y g.2.2)) (.add g.1 y g.2.1 g.2.2)) (tailEvs y G))
      ↔ okTail s.loc z V g.2.2 G from IH]
    simp only [LegalEv, step, okTail]
    constructor
    · rintro ⟨⟨c1, h1, h2, h3⟩, ⟨_, h4, _⟩, h5⟩
      rw [hc] at h1; cases h1
      refine ⟨h2, h3, ?_, h5⟩
      simpa [Function.update_of_ne hg] using h4
    · rintro ⟨h2, h3, h4, h5⟩
      refine ⟨⟨c0, hc, h2, h3⟩, ⟨hg, ?_, by simp⟩, h5⟩
      simpa [Function.update_of_ne hg] using h4

/-- the whole shared plan is Legal iff: `p` and the courier's first position agree (`p` at `cp`, `y` fresh, `y ≠ p`)
and the chain is `okTail`. -/
theorem legal_shared_iff (z V : C) (s : St K Reg C) (y p : Reg) (cp : C) (G : List (Give K Reg C))
    (hyp : y ≠ p) (hy : ∀ g ∈ G, g.1 ≠ y) :
    Legal z V s (sharedEvs y p cp G) ↔
      s.loc y = none ∧ s.loc p = some cp ∧ okTail (Function.update s.loc y (some cp)) z V cp G := by
  have hloc : (step (step s (.born y cp)) (.add y p 1 cp)).loc = Function.update s.loc y (some cp) := by
    simp [step]
  have hsy : (step (step s (.born y cp)) (.add y p 1 cp)).loc y = some cp := by rw [hloc]; simp
  simp only [sharedEvs, Legal]
  rw [legal_tail_iff z V y G hy _ cp hsy, hloc]
  simp only [LegalEv, step]
  constructor
  · rintro ⟨h1, ⟨_, h2, h3⟩, h4⟩
    refine ⟨h1, ?_, h4⟩
    simpa [Function.update_of_ne hyp.symm] using h3
  · rintro ⟨h1, h2, h4⟩
    refine ⟨h1, ⟨hyp, by simp, ?_⟩, h4⟩
    simpa [Function.update_of_ne hyp.symm] using h2

/-- ASCENT (frame order) as a separate hypothesis on a preorder of charts: `cp ≤ g_1 ≤ ... ≤ g_m`. -/
def Ascending [Preorder C] (cp : C) (G : List (Give K Reg C)) : Prop :=
  List.IsChain (· ≤ ·) (cp :: G.map fun g => g.2.2)

/-- Legal does not see ascent: reversing the order of the (distinct) stops of a Legal chain with the same
consumers present keeps it Legal when the `V` stop is not interior. (Two stops, neither `V`.) -/
theorem legal_blind_to_order (z V : C) (y : Reg) (g1 g2 : Give K Reg C) (hy1 : g1.1 ≠ y) (hy2 : g2.1 ≠ y)
    (s : St K Reg C) (c0 : C) (hc : s.loc y = some c0) (hV1 : g1.2.2 ≠ V) (hV2 : g2.2.2 ≠ V) (hc0 : c0 ≠ V)
    (h : Legal z V s (tailEvs y [g1, g2])) : Legal z V s (tailEvs y [g2, g1]) := by
  have hy : ∀ g ∈ [g1, g2], g.1 ≠ y := by simp [hy1, hy2]
  have hy' : ∀ g ∈ [g2, g1], g.1 ≠ y := by simp [hy1, hy2]
  rw [legal_tail_iff z V y _ hy s c0 hc] at h
  rw [legal_tail_iff z V y _ hy' s c0 hc]
  simp only [okTail] at h ⊢
  exact ⟨hc0, h.2.2.2.2.1, h.2.2.2.2.2.1, hV2, h.2.1, h.2.2.1, trivial⟩

end Legality

/-! ## (2) Cost under Theorem K -/
section Cost
open CallerCost FibreK

/-- D0 per helper (FibreK.d0_native; same definition as Delivery.courierD0, which is not built in this tree). -/
noncomputable def courierD0 (h : Helper) : ℝ := fL (h.e - h.b) - (h.steps.map fun s => fL (gap s)).sum

noncomputable def φ (x : ℝ) : ℝ := x * Real.log x

lemma fL_eq (n : ℕ) : fL n = φ n := rfl

lemma φ_zero : φ 0 = 0 := by simp [φ]

/-- two-point majorisation for the convex `x log x`: `x` between `u` and `v`. -/
lemma maj {u v x : ℝ} (hu : 0 ≤ u) (hux : u ≤ x) (hxv : x ≤ v) :
    φ x + φ (u + v - x) ≤ φ u + φ v := by
  rcases eq_or_lt_of_le (hux.trans hxv) with huv | huv
  · have : x = u := by linarith
    subst this; have : v = x := by linarith
    subst this; simp
  · have hvu : 0 < v - u := by linarith
    set a := (v - x) / (v - u) with ha
    set b := (x - u) / (v - u) with hb
    have ha0 : 0 ≤ a := div_nonneg (by linarith) hvu.le
    have hb0 : 0 ≤ b := div_nonneg (by linarith) hvu.le
    have hab : a + b = 1 := by rw [ha, hb]; field_simp; ring
    have hx : a * u + b * v = x := by rw [ha, hb]; field_simp; ring
    have hy : b * u + a * v = u + v - x := by rw [ha, hb]; field_simp; ring
    have hmem : ∀ w : ℝ, 0 ≤ w → w ∈ Set.Ici (0:ℝ) := fun w hw => hw
    have hv0 : 0 ≤ v := by linarith
    have c1 := Real.convexOn_mul_log.2 (hmem u hu) (hmem v hv0) ha0 hb0 hab
    have c2 := Real.convexOn_mul_log.2 (hmem u hu) (hmem v hv0) hb0 ha0 (by linarith)
    simp only [smul_eq_mul] at c1 c2
    rw [hx] at c1; rw [hy] at c2
    have e1 : φ x ≤ a * φ u + b * φ v := c1
    have e2 : φ (u + v - x) ≤ b * φ u + a * φ v := c2
    have hb1 : b = 1 - a := by linarith
    rw [hb1] at e1 e2
    linarith

lemma fL_incr (y z x : ℕ) (hyz : y ≤ z) : fL (y + x) + fL z ≤ fL y + fL (z + x) := by
  have := maj (u := (y : ℝ)) (v := ((z + x : ℕ) : ℝ)) (x := (z : ℝ)) (by positivity)
    (by exact_mod_cast hyz) (by push_cast; linarith [(Nat.cast_nonneg x : (0:ℝ) ≤ x)])
  have h2 : (y : ℝ) + ((z + x : ℕ) : ℝ) - z = ((y + x : ℕ) : ℝ) := by push_cast; ring
  rw [h2] at this
  simp only [fL_eq]; linarith

/-- superadditivity (weak). -/
lemma fL_super (a b : ℕ) : fL a + fL b ≤ fL (a + b) := by
  have := fL_incr 0 a b (Nat.zero_le _)
  simp [fL] at this ⊢; linarith

/-- strict superadditivity for positive arguments. -/
lemma fL_super_strict (a b : ℕ) (ha : 0 < a) (hb : 0 < b) : fL a + fL b < fL (a + b) := by
  have ha' : (0:ℝ) < a := by exact_mod_cast ha
  have hb' : (0:ℝ) < b := by exact_mod_cast hb
  have h1 : Real.log a < Real.log (a + b) := Real.log_lt_log ha' (by linarith)
  have h2 : Real.log b < Real.log (a + b) := Real.log_lt_log hb' (by linarith)
  simp only [fL]; push_cast
  nlinarith [mul_lt_mul_of_pos_left h1 ha', mul_lt_mul_of_pos_left h2 hb']

/-- prefix sums of the hop-gap sequence. -/
def pre (a : ℕ → ℕ) (j : ℕ) : ℕ := ∑ i ∈ Finset.range j, a i

lemma pre_succ (a : ℕ → ℕ) (j : ℕ) : pre a (j + 1) = pre a j + a j := by simp [pre, Finset.sum_range_succ]
lemma pre_mono (a : ℕ → ℕ) {i j : ℕ} (h : i ≤ j) : pre a i ≤ pre a j := by
  induction h with
  | refl => exact le_rfl
  | step _ ih => rw [pre_succ]; omega

/-- the convexity core: splitting a block of `n` gaps at every interior point costs at most `n·f(R)` plus the gaps. -/
theorem split_ineq (a : ℕ → ℕ) (n : ℕ) :
    ∑ j ∈ Finset.range (n + 1), (fL (pre a j) + fL (pre a n - pre a j))
      ≤ n * fL (pre a n) + ∑ i ∈ Finset.range n, fL (a i) := by
  induction n with
  | zero => simp [pre, fL]
  | succ n ih =>
    have hΔ : ∀ j ∈ Finset.range n, fL (pre a (n + 1) - pre a j) ≤ fL (pre a n - pre a j) + fL (pre a (n+1)) - fL (pre a n) := by
      intro j hj
      have hj' : pre a j ≤ pre a n := pre_mono a (by simp at hj; omega)
      have := fL_incr (pre a n - pre a j) (pre a n) (a n) (Nat.sub_le _ _)
      have e : pre a n - pre a j + a n = pre a (n + 1) - pre a j := by rw [pre_succ]; omega
      rw [e, ← pre_succ] at this
      linarith
    have h1 : ∑ j ∈ Finset.range n, (fL (pre a j) + fL (pre a (n + 1) - pre a j))
        ≤ ∑ j ∈ Finset.range n, (fL (pre a j) + fL (pre a n - pre a j) + fL (pre a (n+1)) - fL (pre a n)) :=
      Finset.sum_le_sum fun j hj => by have := hΔ j hj; linarith
    rw [Finset.sum_range_succ] at ih
    rw [Finset.sum_range_succ, Finset.sum_range_succ]
    simp only [Finset.sum_add_distrib, Finset.sum_sub_distrib, Finset.sum_const, Finset.card_range, nsmul_eq_mul] at h1
    simp only [Finset.sum_range_succ (fun i => fL (a i)) n]
    have e0 : pre a (n + 1) - pre a n = a n := by rw [pre_succ]; omega
    have e1 : pre a n - pre a n = 0 := Nat.sub_self _
    have e2 : pre a (n + 1) - pre a (n + 1) = 0 := Nat.sub_self _
    rw [e1] at ih
    rw [e0, e2]
    have hf0 : fL 0 = 0 := by simp [fL]
    simp only [hf0] at ih ⊢
    push_cast
    simp only [Finset.sum_add_distrib] at ih ⊢
    nlinarith [h1, ih]

/-- D0 of a courier whose hop gaps are the list `gs` and whose climb is their sum. -/
theorem courierD0_gaps (h : Helper) (gs : List ℕ) (hs : h.steps.map gap = gs) (hd : h.e - h.b = gs.sum) :
    courierD0 h = fL gs.sum - (gs.map fL).sum := by
  have : (h.steps.map fun s => fL (gap s)).sum = ((h.steps.map gap).map fL).sum := by rw [List.map_map]; rfl
  unfold courierD0; rw [this, hs, hd]

/-- D0 depends on the multiset of gaps only (so the beta-side order G-chain -> F -> V is priced the same). -/
theorem courierD0_perm (h h' : Helper) (hd : h.e - h.b = h'.e - h'.b)
    (hp : (h.steps.map gap).Perm (h'.steps.map gap)) : courierD0 h = courierD0 h' := by
  have e : ∀ h : Helper, (h.steps.map fun s => fL (gap s)).sum = ((h.steps.map gap).map fL).sum := by
    intro h; rw [List.map_map]; rfl
  unfold courierD0; rw [e h, e h', hd, (hp.map fL).sum_eq]

lemma sum_range_map (g : ℕ → ℕ) (n : ℕ) : ((List.range n).map g).sum = ∑ i ∈ Finset.range n, g i := by
  induction n with
  | zero => simp
  | succ n ih => simp [List.range_succ, ih, Finset.sum_range_succ]

lemma sum_range_mapR (g : ℕ → ℝ) (n : ℕ) : ((List.range n).map g).sum = ∑ i ∈ Finset.range n, g i := by
  induction n with
  | zero => simp
  | succ n ih => simp [List.range_succ, ih, Finset.sum_range_succ]

/-- K-cost of the SHARED courier: pickup hop `a0`, then the `k+1` hops `a 0 .. a k` (k gives, last hop to V). -/
noncomputable def sharedCost (a0 : ℕ) (k : ℕ) (a : ℕ → ℕ) : ℝ :=
  fL (a0 + pre a (k + 1)) - fL a0 - ∑ i ∈ Finset.range (k + 1), fL (a i)

/-- K-cost of the `k` SEPARATE couriers (courier `j+1`, `j < k`, has hops `a0`, `P_{j+1}`, `R - P_{j+1}`). -/
noncomputable def sepCost (a0 : ℕ) (k : ℕ) (a : ℕ → ℕ) : ℝ :=
  ∑ j ∈ Finset.range k, (fL (a0 + pre a (k + 1)) - fL a0 - fL (pre a (j + 1)) - fL (pre a (k + 1) - pre a (j + 1)))

/-- the shared helper's D0 is `sharedCost`. -/
theorem shared_helper_cost (h : Helper) (a0 k : ℕ) (a : ℕ → ℕ)
    (hs : h.steps.map gap = a0 :: (List.range (k + 1)).map a) (hd : h.e - h.b = a0 + pre a (k + 1)) :
    courierD0 h = sharedCost a0 k a := by
  have hsum : (a0 :: (List.range (k + 1)).map a).sum = a0 + pre a (k + 1) := by
    simp [List.sum_cons, sum_range_map, pre]
  rw [courierD0_gaps h _ hs (by rw [hd, hsum]), hsum]
  simp only [List.map_cons, List.sum_cons, List.map_map, Function.comp_def]
  rw [sum_range_mapR (fun i => fL (a i))]
  unfold sharedCost; ring

/-- the separate courier for give `j+1`. -/
theorem sep_helper_cost (h : Helper) (a0 k j : ℕ) (a : ℕ → ℕ)
    (hs : h.steps.map gap = [a0, pre a (j + 1), pre a (k + 1) - pre a (j + 1)])
    (hd : h.e - h.b = a0 + pre a (k + 1)) (hjk : j + 1 ≤ k + 1) :
    courierD0 h = fL (a0 + pre a (k + 1)) - fL a0 - fL (pre a (j + 1)) - fL (pre a (k + 1) - pre a (j + 1)) := by
  have hle := pre_mono a hjk
  have hsum : [a0, pre a (j + 1), pre a (k + 1) - pre a (j + 1)].sum = a0 + pre a (k + 1) := by
    simp; omega
  rw [courierD0_gaps h _ hs (by rw [hd, hsum]), hsum]
  simp; ring

/-- **EXACT DIFFERENCE** (separate - shared), `k` consumers. -/
theorem diff_formula (a0 k : ℕ) (a : ℕ → ℕ) :
    sepCost a0 k a - sharedCost a0 k a =
      ((k : ℝ) - 1) * (fL (a0 + pre a (k + 1)) - fL a0)
        - ∑ j ∈ Finset.range k, (fL (pre a (j + 1)) + fL (pre a (k + 1) - pre a (j + 1)))
        + ∑ i ∈ Finset.range (k + 1), fL (a i) := by
  unfold sepCost sharedCost
  have : ∀ j ∈ Finset.range k, (fL (a0 + pre a (k + 1)) - fL a0 - fL (pre a (j + 1)) - fL (pre a (k + 1) - pre a (j + 1)))
      = (fL (a0 + pre a (k + 1)) - fL a0) - (fL (pre a (j + 1)) + fL (pre a (k + 1) - pre a (j + 1))) := by
    intro j _; ring
  rw [Finset.sum_congr rfl this, Finset.sum_sub_distrib]
  simp only [Finset.sum_const, Finset.card_range, nsmul_eq_mul]
  ring

/-- the interior split terms: `Σ_{j<k} (f(P_{j+1}) + f(R - P_{j+1})) ≤ (k-1) f(R) + Σ f(a_i)`. -/
theorem interior_split (a : ℕ → ℕ) (k : ℕ) :
    ∑ j ∈ Finset.range k, (fL (pre a (j + 1)) + fL (pre a (k + 1) - pre a (j + 1)))
      ≤ ((k : ℝ) - 1) * fL (pre a (k + 1)) + ∑ i ∈ Finset.range (k + 1), fL (a i) := by
  have h := split_ineq a (k + 1)
  rw [Finset.sum_range_succ, Finset.sum_range_succ'] at h
  have e0 : pre a 0 = 0 := by simp [pre]
  have hf0 : fL 0 = 0 := by simp [fL]
  simp only [e0, Nat.sub_zero, Nat.sub_self, hf0] at h
  push_cast at h
  linarith

/-- **(2) COST THEOREM.**  For `k ≥ 1` consumers on one ascending chain with the same endpoints (pickup hop `a0`,
total chain length `R`): ONE shared courier is never dearer in D0 than `k` separate couriers (each 3 hops). -/
theorem shared_le_sep (a0 k : ℕ) (a : ℕ → ℕ) (hk : 1 ≤ k) : sharedCost a0 k a ≤ sepCost a0 k a := by
  have h1 := diff_formula a0 k a
  have h2 := interior_split a k
  have h3 := fL_super a0 (pre a (k + 1))
  have hk' : (1:ℝ) ≤ k := by exact_mod_cast hk
  have h4 : 0 ≤ ((k : ℝ) - 1) * (fL (a0 + pre a (k + 1)) - fL a0 - fL (pre a (k + 1))) :=
    mul_nonneg (by linarith) (by linarith)
  nlinarith

/-- equality exactly when one consumer: a single courier IS the shared courier. -/
theorem shared_eq_sep_one (a0 : ℕ) (a : ℕ → ℕ) : sharedCost a0 1 a = sepCost a0 1 a := by
  have e : pre a 2 - pre a 1 = a 1 := by rw [pre_succ a 1]; omega
  have e1 : pre a 1 = a 0 := by simp [pre]
  unfold sharedCost sepCost
  have e' : pre a 2 - a 0 = a 1 := by rw [← e1]; exact e
  simp [Finset.sum_range_succ, e', e1]
  ring

/-- **STRICT** for `k ≥ 2` consumers whenever the pickup hop and chain length are positive. -/
theorem shared_lt_sep (a0 k : ℕ) (a : ℕ → ℕ) (hk : 2 ≤ k) (ha0 : 0 < a0) (hR : 0 < pre a (k + 1)) :
    sharedCost a0 k a < sepCost a0 k a := by
  have h1 := diff_formula a0 k a
  have h2 := interior_split a k
  have h3 := fL_super_strict a0 (pre a (k + 1)) ha0 hR
  have hk' : (2:ℝ) ≤ k := by exact_mod_cast hk
  have h4 : 0 < ((k : ℝ) - 1) * (fL (a0 + pre a (k + 1)) - fL a0 - fL (pre a (k + 1))) :=
    mul_pos (by linarith) (by linarith)
  nlinarith

/-- the shared courier is a net K-win by at least `(k-1)·(f(a0+R) - f(a0) - f(R))`. -/
theorem saving_ge (a0 k : ℕ) (a : ℕ → ℕ) :
    ((k : ℝ) - 1) * (fL (a0 + pre a (k + 1)) - fL a0 - fL (pre a (k + 1))) ≤ sepCost a0 k a - sharedCost a0 k a := by
  have h1 := diff_formula a0 k a
  have h2 := interior_split a k
  nlinarith

/-- the unit example `a0 = 1`, gaps `1,1,1`, `k = 2`: shared D0 = 8 ln 2, two separate couriers 12 ln 2 in total. -/
theorem example_k2 : sharedCost 1 2 (fun _ => 1) = 8 * Real.log 2 ∧ sepCost 1 2 (fun _ => 1) = 12 * Real.log 2 := by
  have p1 : pre (fun _ => 1) 3 = 3 := by simp [pre]
  have p2 : pre (fun _ => 1) 1 = 1 := by simp [pre]
  have p3 : pre (fun _ => 1) 2 = 2 := by simp [pre]
  have l4 : Real.log 4 = 2 * Real.log 2 := by
    rw [show (4:ℝ) = 2 ^ 2 by norm_num, Real.log_pow]; norm_num
  have f1 : fL 1 = 0 := by simp [fL]
  have f2 : fL 2 = 2 * Real.log 2 := by simp [fL]
  have f4 : fL 4 = 8 * Real.log 2 := by simp only [fL]; push_cast; rw [l4]; ring
  constructor
  · unfold sharedCost; simp [Finset.sum_range_succ, p1, f1, f4]
  · unfold sepCost; simp [Finset.sum_range_succ, p1, p2, p3, f1, f2, f4]; ring

end Cost
end SharedCourier

#print axioms SharedCourier.exact_mod_tokens
#print axioms SharedCourier.tc_cleanup
#print axioms SharedCourier.legal_shared_iff
#print axioms SharedCourier.shared_le_sep
#print axioms SharedCourier.shared_lt_sep
#print axioms SharedCourier.example_k2
