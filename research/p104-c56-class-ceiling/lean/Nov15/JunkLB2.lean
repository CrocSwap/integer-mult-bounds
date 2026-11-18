/-
BIG-JUNKLB2 (internal notes), T1  g9 pricing (class M): charging every move at g9 = h_9, except a Y main's first move
    (out of chart 0, never on a pair chain), never exceeds the real I1 cost; the gap for Y_p is
    l(d_1) = f(8) - f(d_1) - f(9-d_1) ≥ 0. Hence Σ_{junk pairs} dist_{g9}(A_q → G_p) ≤ public cost.
T3  slot lemma (level 7): |D| ≤ rank{x_p : p ∈ D} + |Z|, with the T2 facts as explicit hypotheses.
T4  departer law, CORRECTED SCOPE (GAPMAP): arrivals = ALL arrivals at c, owned included;
    dim π(Arr_c) ≤ #public departers + #owned arrivals + #Y enders. Each departer stop costs ≥ f(2).
    The public-only version is false in the same model (`T4_public_only_false`).
(Nov 16): T1 linked to registers (`Net.T1_cost`, `Net.T1_full`: Σ move charges ≤ public
cost under JunkM op semantics); T2 proved from level-k op semantics (`T2_run`: complementarity,
independence, expansion existence) and discharged in T3 (`slot_lemma_T2`, `slot_lemma_run`).
Self-contained: h / gaps / hsum / two_point / Net are copied from Nov15/JunkM.lean.
-/
import Mathlib.Analysis.SpecialFunctions.Log.NegMulLog
import Mathlib.Analysis.Convex.Slope
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.LinearAlgebra.StdBasis
import Mathlib.LinearAlgebra.Dimension.OrzechProperty

open Finset

set_option linter.unusedSectionVars false
set_option linter.unusedSimpArgs false

namespace JunkLB2

/-! ## Costs (copied from JunkM, I1) -/

section Cost

variable (f : ℝ → ℝ)

/-- `h_e(a,b) = f(e-a) - f(b-a) - f(e-b)`. -/
def h (e a b : ℝ) : ℝ := f (e - a) - f (b - a) - f (e - b)

def gaps : List ℝ → ℝ
  | a :: b :: t => f (b - a) + gaps (b :: t)
  | _ => 0

/-- `Σ h_e(d_i, d_{i+1})` along a dim chain. -/
def hsum (e : ℝ) : List ℝ → ℝ
  | a :: b :: t => h f e a b + hsum e (b :: t)
  | _ => 0

/-- telescoping with an arbitrary pricing level `e` (the chain need not end at `e`):
`Σ h_e(d_i,d_{i+1}) = f(e - d_0) - f(e - last) - Σ f(gaps)`. -/
theorem hsum_tele (e : ℝ) : ∀ (d0 : ℝ) (ds : List ℝ),
    hsum f e (d0 :: ds) =
      f (e - d0) - f (e - (d0 :: ds).getLast (List.cons_ne_nil _ _)) - gaps f (d0 :: ds)
  | d0, [] => by simp [hsum, gaps]
  | d0, b :: t => by
    have ih := hsum_tele e b t
    rw [List.getLast_cons (List.cons_ne_nil _ _)]
    simp only [hsum, gaps, h] at ih ⊢
    rw [ih]; ring

end Cost

/-- `f(r) = r log r`. -/
noncomputable def fL (r : ℝ) : ℝ := r * Real.log r

lemma fL_convex : ConvexOn ℝ (Set.Ici (0 : ℝ)) fL := Real.convexOn_mul_log

/-- two-point majorisation for a convex function on `[0,∞)` (copied from JunkM). -/
lemma two_point {f : ℝ → ℝ} (cvx : ConvexOn ℝ (Set.Ici (0 : ℝ)) f) {lo hi y z : ℝ} (h0 : 0 ≤ lo)
    (hlt : lo < hi) (hy1 : lo ≤ y) (hy2 : y ≤ hi) (hz1 : lo ≤ z) (hz2 : z ≤ hi)
    (hs : y + z = lo + hi) : f y + f z ≤ f lo + f hi := by
  have hD : 0 < hi - lo := by linarith
  have hlo : lo ∈ Set.Ici (0:ℝ) := h0
  have hhi : hi ∈ Set.Ici (0:ℝ) := by simp; linarith
  have hy := cvx.2 hlo hhi
    (div_nonneg (by linarith) hD.le : (0:ℝ) ≤ (hi - y) / (hi - lo))
    (div_nonneg (by linarith) hD.le : (0:ℝ) ≤ (y - lo) / (hi - lo)) (by field_simp; ring)
  have hz := cvx.2 hlo hhi
    (div_nonneg (by linarith) hD.le : (0:ℝ) ≤ (hi - z) / (hi - lo))
    (div_nonneg (by linarith) hD.le : (0:ℝ) ≤ (z - lo) / (hi - lo)) (by field_simp; ring)
  simp only [smul_eq_mul] at hy hz
  have ey : (hi - y) / (hi - lo) * lo + (y - lo) / (hi - lo) * hi = y := by field_simp; ring
  have ez : (hi - z) / (hi - lo) * lo + (z - lo) / (hi - lo) * hi = z := by field_simp; ring
  rw [ey] at hy; rw [ez] at hz
  have e1 : (hi - y) / (hi - lo) + (hi - z) / (hi - lo) = 1 := by field_simp; linarith
  have e2 : (y - lo) / (hi - lo) + (z - lo) / (hi - lo) = 1 := by field_simp; linarith
  have : f y + f z ≤ ((hi - y) / (hi - lo) + (hi - z) / (hi - lo)) * f lo
      + ((y - lo) / (hi - lo) + (z - lo) / (hi - lo)) * f hi := by linarith
  rw [e1, e2] at this; linarith

lemma fL0 : fL 0 = 0 := by simp [fL]
lemma fL1 : fL 1 = 0 := by simp [fL]

/-- every ascending move strictly below the final dim costs at least `κ = f(2) = 2 log 2`:
`h_e(a,b) ≥ f(2)` when `b - a ≥ 1` and `e - b ≥ 1` (T4's "each departer stop costs ≥ f(2)"). -/
theorem kappa_le (e a b : ℝ) (hab : 1 ≤ b - a) (hbe : 1 ≤ e - b) : fL 2 ≤ h fL e a b := by
  have cvx := fL_convex
  set x := b - a; set y := e - b
  have hxy : e - a = x + y := by simp only [x, y]; ring
  -- f(x) + f(1+y) ≤ f(1) + f(x+y)
  have s1 := two_point cvx (lo := 1) (hi := x + y) (y := x) (z := 1 + y)
    (by norm_num) (by linarith) hab (by linarith) (by linarith) (by linarith) (by ring)
  -- f(y) + f(2) ≤ f(1) + f(1+y)
  have s2 := two_point cvx (lo := 1) (hi := 1 + y) (y := y) (z := 2)
    (by norm_num) (by linarith) hbe (by linarith) (by norm_num) (by linarith) (by ring)
  simp only [h, hxy]; rw [fL1] at s1 s2; linarith

/-- `g9(a,b) ≥ 0` for `a ≤ b ≤ 9`. -/
lemma g9_nonneg (a b : ℝ) (hab : a ≤ b) (hb : b ≤ 9) : 0 ≤ h fL 9 a b := by
  have := two_point fL_convex (lo := 0) (hi := 9 - a) (y := b - a) (z := 9 - b)
  rcases (show a = 9 ∨ a < 9 by
      rcases lt_or_eq_of_le (hab.trans hb) with h' | h' <;> [exact Or.inr h'; exact Or.inl h']) with
    rfl | ha
  · have : b = 9 := le_antisymm hb hab
    subst this; simp [h, fL0]
  · have := this le_rfl (by linarith) (by linarith) (by linarith) (by linarith) (by linarith)
      (by ring)
    simp only [h]; rw [fL0] at this; linarith

/-! ## T1. g9 pricing (class M) -/

section T1

/-- **T1, Y main.** For `Y_p` with dim chain `0 < d_1 < … < d_k = 8`, the real I1 cost
`Σ h_8` equals the g9 charge on every move but the first, plus `l(d_1) = f(8) - f(d_1) - f(9 - d_1)`. -/
theorem T1_Y (f : ℝ → ℝ) (hf0 : f 0 = 0) (hf1 : f 1 = 0) (d1 : ℝ) (rest : List ℝ)
    (hlast : (d1 :: rest).getLast (List.cons_ne_nil _ _) = 8) :
    hsum f 8 (0 :: d1 :: rest) = hsum f 9 (d1 :: rest) + (f 8 - f d1 - f (9 - d1)) := by
  have e1 : hsum f 8 (0 :: d1 :: rest) = h f 8 0 d1 + hsum f 8 (d1 :: rest) := rfl
  rw [e1, hsum_tele f 8 d1 rest, hsum_tele f 9 d1 rest, hlast]
  have a1 : (8:ℝ) - 8 = 0 := by norm_num
  have a2 : (9:ℝ) - 8 = 1 := by norm_num
  simp only [h, a1, a2, hf0, hf1, sub_zero]; ring

/-- the T1 slack `l(d) = f(8) - f(d) - f(9-d) ≥ 0` for `1 ≤ d ≤ 8` (and `l(1) = l(8) = 0`). -/
theorem l_nonneg (d : ℝ) (h1 : 1 ≤ d) (h8 : d ≤ 8) : 0 ≤ fL 8 - fL d - fL (9 - d) := by
  have := two_point fL_convex (lo := 1) (hi := 8) (y := d) (z := 9 - d)
    (by norm_num) (by norm_num) h1 h8 (by linarith) (by linarith) (by ring)
  rw [fL1] at this; linarith

lemma l_one : fL 8 - fL 1 - fL (9 - 1) = 0 := by norm_num [fL1]

/-- **T1, per register.** Charged ≤ real for a Y main (`0 :: d_1 :: … :: 8`, first move uncharged);
for a register ending at V (dim 9) the charge is its real cost by definition (`hsum fL 9`). -/
theorem T1_Y_le (d1 : ℝ) (rest : List ℝ) (h1 : 1 ≤ d1) (h8 : d1 ≤ 8)
    (hlast : (d1 :: rest).getLast (List.cons_ne_nil _ _) = 8) :
    hsum fL 9 (d1 :: rest) ≤ hsum fL 8 (0 :: d1 :: rest) := by
  rw [T1_Y fL fL0 fL1 d1 rest hlast]; linarith [l_nonneg d1 h1 h8]

/-! ### The path bound with g9 everywhere (copy of JunkM's `Net`, no free moves) -/

attribute [local instance] Classical.propDecidable

variable {C XP YP Mv : Type*} [PartialOrder C] [Fintype XP] [Fintype YP] [Fintype Mv]

structure Net (C XP YP Mv : Type*) [PartialOrder C] where
  inS : XP → C → Prop
  inP : YP → C → Prop
  monoS : ∀ q s s', s ≤ s' → inS q s → inS q s'
  antiP : ∀ p t t', t ≤ t' → inP p t' → inP p t
  A : XP → C
  G : YP → C
  hA : ∀ q, inS q (A q)
  hG : ∀ p, inP p (G p)
  src : Mv → C
  tgt : Mv → C
  hlt : ∀ m, src m < tgt m

namespace Net

variable (N : Net C XP YP Mv)

noncomputable def nS (s : C) : ℕ := (univ.filter fun q => N.inS q s).card
noncomputable def mP (t : C) : ℕ := (univ.filter fun p => N.inP p t).card

def Chain : C → List Mv → C → Prop
  | a, [], b => a = b
  | a, m :: ms, b => N.src m = a ∧ Chain (N.tgt m) ms b

lemma chain_bounds : ∀ (a : C) (ℓ : List Mv) (b : C), N.Chain a ℓ b →
    ∀ m ∈ ℓ, a ≤ N.src m ∧ N.tgt m ≤ b
  | a, [], b, _, m, hm => absurd hm (List.not_mem_nil)
  | a, m' :: ms, b, ⟨hs, hc⟩, m, hm => by
    have hab : ∀ x ∈ ms, N.tgt m' ≤ N.src x ∧ N.tgt x ≤ b := chain_bounds _ ms b hc
    have hend : N.tgt m' ≤ b := by
      cases ms with
      | nil => exact le_of_eq hc
      | cons x xs => exact (le_of_lt (N.hlt x)).trans' ((hab x (by simp)).1) |>.trans (hab x (by simp)).2
    rcases List.mem_cons.mp hm with rfl | hm
    · exact ⟨le_of_eq hs.symm, hend⟩
    · have := hab m hm
      exact ⟨(le_of_eq hs.symm).trans ((le_of_lt (N.hlt m')).trans this.1), this.2⟩

lemma chain_nodup : ∀ (a : C) (ℓ : List Mv) (b : C), N.Chain a ℓ b → ℓ.Nodup
  | a, [], b, _ => List.nodup_nil
  | a, m :: ms, b, ⟨_, hc⟩ => by
    refine List.nodup_cons.mpr ⟨fun hm => ?_, chain_nodup _ ms b hc⟩
    have := (N.chain_bounds _ ms b hc m hm).1
    exact absurd (lt_of_lt_of_le (N.hlt m) this) (lt_irrefl _)

noncomputable def wt (c : C → C → ℝ) (m : Mv) : ℝ :=
  c (N.src m) (N.tgt m) / ((N.nS (N.src m) : ℝ) * N.mP (N.tgt m))

lemma users_card (P : Finset (YP × XP)) (path : YP × XP → List Mv)
    (hpath : ∀ π ∈ P, N.Chain (N.A π.2) (path π) (N.G π.1)) (m : Mv) :
    (P.filter fun π => m ∈ path π).card ≤ N.mP (N.tgt m) * N.nS (N.src m) := by
  rw [mP, nS, ← card_product]
  apply card_le_card
  intro π hπ
  rw [mem_filter] at hπ
  have hb := N.chain_bounds _ _ _ (hpath π hπ.1) m hπ.2
  simp only [mem_product, mem_filter, mem_univ, true_and]
  exact ⟨N.antiP π.1 _ _ hb.2 (N.hG π.1), N.monoS π.2 _ _ hb.1 (N.hA π.2)⟩

def ChartChain : C → List C → C → Prop
  | a, [], b => a = b
  | a, t :: ts, b => a < t ∧ ChartChain t ts b

noncomputable def cw (c : C → C → ℝ) : C → List C → ℝ
  | _, [] => 0
  | a, t :: ts => c a t / ((N.nS a : ℝ) * N.mP t) + cw c t ts

/-- the shortest-path value `dist(a → b)` in the chart graph. -/
noncomputable def dist (c : C → C → ℝ) (a b : C) : ℝ :=
  sInf {x | ∃ l, ChartChain a l b ∧ N.cw c a l = x}

lemma cw_nonneg (c : C → C → ℝ) (hc0 : ∀ s t, 0 ≤ c s t) : ∀ a l, 0 ≤ N.cw c a l
  | _, [] => le_rfl
  | a, t :: ts => add_nonneg (div_nonneg (hc0 _ _) (by positivity)) (cw_nonneg c hc0 t ts)

lemma chain_to_chart (c : C → C → ℝ) : ∀ (a : C) (ℓ : List Mv) (b : C), N.Chain a ℓ b →
    ChartChain a (ℓ.map N.tgt) b ∧ N.cw c a (ℓ.map N.tgt) = (ℓ.map (N.wt c)).sum
  | a, [], b, h => ⟨h, rfl⟩
  | a, m :: ms, b, ⟨hs, hc⟩ => by
    obtain ⟨h1, h2⟩ := chain_to_chart c _ ms b hc
    refine ⟨⟨hs ▸ N.hlt m, h1⟩, ?_⟩
    simp only [List.map_cons, cw, List.sum_cons, h2, wt, hs]

lemma dist_le (c : C → C → ℝ) (hc0 : ∀ s t, 0 ≤ c s t) {a b : C} {ℓ : List Mv}
    (h : N.Chain a ℓ b) : N.dist c a b ≤ (ℓ.map (N.wt c)).sum := by
  obtain ⟨h1, h2⟩ := N.chain_to_chart c a ℓ b h
  exact csInf_le ⟨0, fun x ⟨l, _, hx⟩ => hx ▸ N.cw_nonneg c hc0 a l⟩ ⟨_, h1, h2⟩

/-- the path bound without free moves: if every USED move is charged `w m ≥ c(src,tgt)`, then
`Σ_pairs dist ≤ Σ_m w m`. -/
theorem bound0 (c : C → C → ℝ) (w : Mv → ℝ) (P : Finset (YP × XP)) (path : YP × XP → List Mv)
    (hpath : ∀ π ∈ P, N.Chain (N.A π.2) (path π) (N.G π.1))
    (hc0 : ∀ s t, 0 ≤ c s t) (hw0 : ∀ m, 0 ≤ w m)
    (hpay : ∀ m, (∃ π ∈ P, m ∈ path π) → c (N.src m) (N.tgt m) ≤ w m) :
    ∑ π ∈ P, N.dist c (N.A π.2) (N.G π.1) ≤ ∑ m, w m := by
  have s1 : ∑ π ∈ P, N.dist c (N.A π.2) (N.G π.1) ≤ ∑ π ∈ P, ((path π).map (N.wt c)).sum :=
    sum_le_sum fun π hπ => N.dist_le c hc0 (hpath π hπ)
  have s2 : ∑ π ∈ P, ((path π).map (N.wt c)).sum
      = ∑ m, ((P.filter fun π => m ∈ path π).card : ℝ) * N.wt c m := by
    have e1 : ∀ π ∈ P, ((path π).map (N.wt c)).sum
        = ∑ m, if m ∈ path π then N.wt c m else 0 := by
      intro π hπ
      rw [← List.sum_toFinset _ (N.chain_nodup _ _ _ (hpath π hπ)), ← sum_filter]
      congr 1; ext m; simp
    rw [sum_congr rfl e1, sum_comm]
    refine sum_congr rfl fun m _ => ?_
    rw [← sum_filter, sum_const, nsmul_eq_mul]
  have s3 : ∀ m, ((P.filter fun π => m ∈ path π).card : ℝ) * N.wt c m ≤ w m := by
    intro m
    by_cases hu : ∃ π ∈ P, m ∈ path π
    · have hcard := N.users_card P path hpath m
      obtain ⟨π, hπ, hm⟩ := hu
      have hpos : 0 < (P.filter fun π => m ∈ path π).card :=
        card_pos.mpr ⟨π, mem_filter.mpr ⟨hπ, hm⟩⟩
      have hD : (0 : ℝ) < (N.nS (N.src m) : ℝ) * N.mP (N.tgt m) := by
        have : 0 < N.mP (N.tgt m) * N.nS (N.src m) := lt_of_lt_of_le hpos hcard
        rw [mul_comm]; exact_mod_cast this
      have hle : ((P.filter fun π => m ∈ path π).card : ℝ) ≤ (N.nS (N.src m) : ℝ) * N.mP (N.tgt m) := by
        rw [mul_comm]; exact_mod_cast hcard
      have : ((P.filter fun π => m ∈ path π).card : ℝ) * N.wt c m ≤ c (N.src m) (N.tgt m) := by
        rw [wt, mul_div_assoc', div_le_iff₀ hD]
        exact mul_le_mul_of_nonneg_left hle (hc0 _ _) |>.trans_eq' (by ring)
      exact this.trans (hpay m ⟨π, hπ, hm⟩)
    · have : (P.filter fun π => m ∈ path π) = ∅ := by
        ext π; simp only [mem_filter, Finset.notMem_empty, iff_false, not_and]
        exact fun hπ hm => hu ⟨π, hπ, hm⟩
      simp [this, hw0 m]
  calc _ ≤ _ := s1
    _ = _ := s2
    _ ≤ _ := sum_le_sum fun m _ => s3 m

/-- **T1 (class M), path form.** Chart `z` (= chart 0) holds no X port (`n(0) = 0`). Every move
not leaving `z` is charged at least `c` (with `c = g9` on dims: `g9_nonneg`, `T1_Y_le`); moves out of
`z` (Y mains' first moves, the uncharged ones) may be charged anything `≥ 0`. Then
`Σ_{junk pairs} dist_c(A_q → G_p) ≤ Σ_m w m`; combined with `Σ_m w m ≤ public cost` (per register:
`T1_Y_le` for Y mains, equality for registers ending at V) this is T1's bound. -/
theorem T1_bound (c : C → C → ℝ) (w : Mv → ℝ) (P : Finset (YP × XP)) (path : YP × XP → List Mv)
    (hpath : ∀ π ∈ P, N.Chain (N.A π.2) (path π) (N.G π.1))
    (hc0 : ∀ s t, 0 ≤ c s t) (hw0 : ∀ m, 0 ≤ w m) (z : C) (hz : ∀ q, ¬ N.inS q z)
    (hcharge : ∀ m, N.src m ≠ z → c (N.src m) (N.tgt m) ≤ w m)
    (cost : ℝ) (hcost : ∑ m, w m ≤ cost) :
    ∑ π ∈ P, N.dist c (N.A π.2) (N.G π.1) ≤ cost := by
  refine (N.bound0 c w P path hpath hc0 hw0 fun m ⟨π, hπ, hm⟩ => hcharge m ?_).trans hcost
  intro hzm
  have := (N.chain_bounds _ _ _ (hpath π hπ) m hm).1
  rw [hzm] at this
  exact hz π.2 (N.monoS π.2 _ _ this (N.hA π.2))

end Net

end T1

/-! ## T1, linked to registers: total move charges ≤ public cost (JunkM op semantics) -/

section T1link

attribute [local instance] Classical.propDecidable

variable {C XP YP Mv R : Type*} [PartialOrder C] [Fintype XP] [Fintype YP] [Fintype Mv] [Fintype R]

namespace Net

variable (N : Net C XP YP Mv)

lemma chain_append : ∀ (a : C) (ℓ : List Mv) (b : C) (m : Mv), N.Chain a ℓ b → N.src m = b →
    N.Chain a (ℓ ++ [m]) (N.tgt m)
  | a, [], b, m, h, hm => by simp only [Chain] at h; subst h; exact ⟨hm, rfl⟩
  | a, m' :: ms, b, m, ⟨hs, hc⟩, hm => ⟨hs, chain_append _ ms b m hc hm⟩

/-- register `i`'s moves up to time `n`, in time order: `mv t i` at each `t < n` where its chart
rises (JunkM's `mv t i`). -/
noncomputable def movesOf (chart : ℕ → R → C) (mv : ℕ → R → Mv) (i : R) (n : ℕ) : List Mv :=
  ((List.range n).filter (fun t => decide (chart t i < chart (t + 1) i))).map (fun t => mv t i)

/-- JunkM op semantics (b) charts never decrease, (c) `mv t i` goes `chart t i → chart (t+1) i` when
`i`'s chart rises: then `i`'s moves form a chain from its birth chart to its chart at time `n`. -/
lemma movesOf_chain (chart : ℕ → R → C) (mv : ℕ → R → Mv)
    (hmv : ∀ t i, chart t i < chart (t + 1) i →
      N.src (mv t i) = chart t i ∧ N.tgt (mv t i) = chart (t + 1) i)
    (hmono : ∀ t i, chart t i ≤ chart (t + 1) i) (i : R) :
    ∀ n, N.Chain (chart 0 i) (movesOf chart mv i n) (chart n i) := by
  intro n
  induction n with
  | zero => simp [movesOf, Chain]
  | succ n ih =>
    by_cases hlt : chart n i < chart (n + 1) i
    · have e : movesOf chart mv i (n + 1) = movesOf chart mv i n ++ [mv n i] := by
        simp [movesOf, List.range_succ, List.filter_append, hlt]
      obtain ⟨hs, ht⟩ := hmv n i hlt
      rw [e, ← ht]; exact N.chain_append _ _ _ _ ih hs
    · have e : movesOf chart mv i (n + 1) = movesOf chart mv i n := by
        simp [movesOf, List.range_succ, List.filter_append, hlt]
      have heq : chart (n + 1) i = chart n i :=
        ((hmono n i).lt_or_eq.resolve_left hlt).symm
      rw [e, heq]; exact ih

/-- the move costs along a chain telescope into `hsum` over the chain's dims. -/
lemma chain_hsum (f : ℝ → ℝ) (e : ℝ) (dim : C → ℝ) : ∀ (a : C) (ℓ : List Mv) (b : C), N.Chain a ℓ b →
    (ℓ.map fun m => h f e (dim (N.src m)) (dim (N.tgt m))).sum =
      hsum f e (dim a :: ℓ.map fun m => dim (N.tgt m))
  | a, [], b, _ => by simp [hsum]
  | a, m :: ms, b, ⟨hs, hc⟩ => by
    simp only [List.map_cons, List.sum_cons, hsum]
    rw [chain_hsum f e dim _ ms b hc, hs]

lemma chain_last (dim : C → ℝ) : ∀ (a : C) (ℓ : List Mv) (b : C), N.Chain a ℓ b →
    (dim a :: ℓ.map fun m => dim (N.tgt m)).getLast (List.cons_ne_nil _ _) = dim b
  | a, [], b, hc => by simp only [Chain] at hc; subst hc; rfl
  | a, m :: ms, b, ⟨_, hc⟩ => by
    rw [List.map_cons, List.getLast_cons (List.cons_ne_nil _ _)]
    exact chain_last dim _ ms b hc

/-- the T1 edge price `c(s,t) = g9(dim s, dim t)` (clipped at 0, which changes nothing on real moves). -/
noncomputable def cg (dim : C → ℕ) (s t : C) : ℝ := max (h fL 9 (dim s) (dim t)) 0

/-- the T1 move charge: moves out of chart `z` (= chart 0; Y mains' first moves) are uncharged, every
other move is charged `c(src, tgt)`. -/
noncomputable def wz (dim : C → ℕ) (z : C) (m : Mv) : ℝ :=
  if N.src m = z then 0 else cg dim (N.src m) (N.tgt m)

lemma cg_eq (dim : C → ℕ) (hdim : StrictMono dim) (s t : C) (hst : s < t) (ht : dim t ≤ 9) :
    cg dim s t = h fL 9 (dim s) (dim t) := by
  have h1 : (dim s : ℝ) ≤ dim t := by exact_mod_cast (hdim hst).le
  have h2 : (dim t : ℝ) ≤ 9 := by exact_mod_cast ht
  exact max_eq_left (g9_nonneg _ _ h1 h2)

/-- a register ending at V (dim 9): its charges are at most its real cost `Σ h_9`. -/
lemma reg_le_V (dim : C → ℕ) (hdim : StrictMono dim) (z : C) (a : C) (ℓ : List Mv) (b : C)
    (hc : N.Chain a ℓ b) (hb : dim b ≤ 9) :
    (ℓ.map (N.wz dim z)).sum ≤ hsum fL 9 ((dim a : ℝ) :: ℓ.map fun m => (dim (N.tgt m) : ℝ)) := by
  rw [← N.chain_hsum fL 9 (fun c => (dim c : ℝ)) a ℓ b hc]
  apply List.sum_le_sum
  intro m hm
  have hbd := N.chain_bounds a ℓ b hc m hm
  have ht9 : dim (N.tgt m) ≤ 9 := (hdim.monotone hbd.2).trans hb
  have hceq := cg_eq dim hdim _ _ (N.hlt m) ht9
  have h1 : (dim (N.src m) : ℝ) ≤ dim (N.tgt m) := by exact_mod_cast (hdim (N.hlt m)).le
  have h2 : (dim (N.tgt m) : ℝ) ≤ 9 := by exact_mod_cast ht9
  unfold wz; split_ifs
  · exact g9_nonneg _ _ h1 h2
  · exact hceq.le

/-- a Y main (born at chart `z`, dim 0; ends at `G_p`, dim 8): charges ≤ real cost `Σ h_8`
(the first move is uncharged; `T1_Y_le`). -/
lemma reg_le_Y (dim : C → ℕ) (hdim : StrictMono dim) (z : C) (hz0 : dim z = 0) (ℓ : List Mv) (b : C)
    (hc : N.Chain z ℓ b) (hb : dim b = 8) :
    (ℓ.map (N.wz dim z)).sum ≤ hsum fL 8 ((dim z : ℝ) :: ℓ.map fun m => (dim (N.tgt m) : ℝ)) := by
  cases ℓ with
  | nil => simp only [Chain] at hc; subst hc; omega
  | cons m1 rest =>
    obtain ⟨hs1, hc'⟩ := hc
    have hw1 : N.wz dim z m1 = 0 := by simp [wz, hs1]
    have hrest : (rest.map (N.wz dim z)) = rest.map fun m => h fL 9 (dim (N.src m)) (dim (N.tgt m)) := by
      apply List.map_congr_left
      intro m hm
      have hbd := N.chain_bounds _ rest b hc' m hm
      have hpos : 0 < dim (N.src m) := by
        have := hdim (lt_of_lt_of_le (hs1 ▸ N.hlt m1) hbd.1); omega
      have hne : N.src m ≠ z := fun e => by rw [e] at hpos; omega
      have ht9 : dim (N.tgt m) ≤ 9 := by have := hdim.monotone hbd.2; omega
      simp only [wz, hne, if_false]
      exact cg_eq dim hdim _ _ (N.hlt m) ht9
    rw [List.map_cons, List.sum_cons, hw1, zero_add, hrest,
      N.chain_hsum fL 9 (fun c => (dim c : ℝ)) _ rest b hc', List.map_cons, hz0, Nat.cast_zero]
    have hd1 : 0 < dim (N.tgt m1) := by have := hdim (hs1 ▸ N.hlt m1); omega
    have hd8 : dim (N.tgt m1) ≤ 8 := by
      have := hdim.monotone (show N.tgt m1 ≤ b from by
        cases rest with
        | nil => exact le_of_eq hc'
        | cons x xs =>
          have hx := N.chain_bounds _ (x :: xs) b hc' x (by simp)
          exact (le_of_lt (N.hlt x)).trans' hx.1 |>.trans hx.2)
      omega
    apply T1_Y_le
    · exact_mod_cast hd1
    · exact_mod_cast hd8
    · rw [N.chain_last (fun c => (dim c : ℝ)) _ rest b hc', hb]; norm_num

lemma list_range_filter_sum (n : ℕ) (p : ℕ → Prop) (g : ℕ → ℝ) :
    (((List.range n).filter (fun t => decide (p t))).map g).sum =
      ∑ t ∈ Finset.range n, if p t then g t else 0 := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [List.range_succ, List.filter_append, List.map_append, List.sum_append, ih,
      Finset.sum_range_succ]
    by_cases hp : p n <;> simp [hp]

/-- **T1, Σ_m w_m ≤ public cost, as a theorem.** JunkM op semantics: charts never decrease,
`mv t i` is register `i`'s move `chart t i → chart (t+1) i` when its chart rises, and the moves are
exactly these (each move is `mv t i` for exactly one rising step `t < n`). Charts carry a strictly
monotone dim (`z` = chart 0, dim 0). Model M: a Y main (`Ym`) is born at `z` and ends at dim 8, every
other register ends at V (dim 9). The public cost is `Σ_i h-sum` over each register's dim chain
(I1), with `e = 8` for Y mains and `9` otherwise. -/
theorem T1_cost (chart : ℕ → R → C) (mv : ℕ → R → Mv) (n : ℕ)
    (hmv : ∀ t i, chart t i < chart (t + 1) i →
      N.src (mv t i) = chart t i ∧ N.tgt (mv t i) = chart (t + 1) i)
    (hmono : ∀ t i, chart t i ≤ chart (t + 1) i)
    (hsurj : ∀ m, ∃ t < n, ∃ i, chart t i < chart (t + 1) i ∧ mv t i = m)
    (hinj : ∀ t t' i i', chart t i < chart (t + 1) i → chart t' i' < chart (t' + 1) i' →
      mv t i = mv t' i' → t = t' ∧ i = i')
    (dim : C → ℕ) (hdim : StrictMono dim) (z : C) (hz0 : dim z = 0) (Ym : Finset R)
    (hY : ∀ i ∈ Ym, chart 0 i = z ∧ dim (chart n i) = 8) (hV : ∀ i ∉ Ym, dim (chart n i) = 9) :
    ∑ m, N.wz dim z m ≤ ∑ i, hsum fL (if i ∈ Ym then 8 else 9)
      ((dim (chart 0 i) : ℝ) :: (movesOf chart mv i n).map fun m => (dim (N.tgt m) : ℝ)) := by
  have hsplit : ∑ m, N.wz dim z m = ∑ i, ((movesOf chart mv i n).map (N.wz dim z)).sum := by
    have e1 : ∀ i, ((movesOf chart mv i n).map (N.wz dim z)).sum =
        ∑ t ∈ Finset.range n, if chart t i < chart (t + 1) i then N.wz dim z (mv t i) else 0 := by
      intro i; rw [movesOf, List.map_map]; exact list_range_filter_sum n _ _
    simp_rw [e1]
    rw [Finset.sum_comm, ← Finset.sum_product (s := Finset.range n) (t := Finset.univ)
      (f := fun x : ℕ × R => if chart x.1 x.2 < chart (x.1 + 1) x.2 then N.wz dim z (mv x.1 x.2) else 0),
      ← Finset.sum_filter]
    symm
    refine Finset.sum_bij (fun x _ => mv x.1 x.2) (fun _ _ => Finset.mem_univ _) ?_ ?_ (fun _ _ => rfl)
    · rintro ⟨t, i⟩ h1 ⟨t', i'⟩ h2 he
      simp only [Finset.mem_filter] at h1 h2
      obtain ⟨rfl, rfl⟩ := hinj t t' i i' h1.2 h2.2 he; rfl
    · intro m _
      obtain ⟨t, ht, i, hr, rfl⟩ := hsurj m
      exact ⟨(t, i), by simp [ht, hr], rfl⟩
  rw [hsplit]
  refine Finset.sum_le_sum fun i _ => ?_
  have hc := N.movesOf_chain chart mv hmv hmono i n
  by_cases hi : i ∈ Ym
  · obtain ⟨h0, h8⟩ := hY i hi
    rw [if_pos hi, h0]; rw [h0] at hc
    exact N.reg_le_Y dim hdim z hz0 _ _ hc h8
  · rw [if_neg hi]
    exact N.reg_le_V dim hdim z _ _ _ hc (by rw [hV i hi])

/-- **T1 (class M), full form.** Under the hypotheses of `T1_cost`, with chart `z` holding no X port
and a move chain `A_q → G_p` for every junk pair (JunkM `hpath_of_junk`):
`Σ_{junk pairs} dist_{g9}(A_q → G_p) ≤ public cost`. -/
theorem T1_full (chart : ℕ → R → C) (mv : ℕ → R → Mv) (n : ℕ)
    (hmv : ∀ t i, chart t i < chart (t + 1) i →
      N.src (mv t i) = chart t i ∧ N.tgt (mv t i) = chart (t + 1) i)
    (hmono : ∀ t i, chart t i ≤ chart (t + 1) i)
    (hsurj : ∀ m, ∃ t < n, ∃ i, chart t i < chart (t + 1) i ∧ mv t i = m)
    (hinj : ∀ t t' i i', chart t i < chart (t + 1) i → chart t' i' < chart (t' + 1) i' →
      mv t i = mv t' i' → t = t' ∧ i = i')
    (dim : C → ℕ) (hdim : StrictMono dim) (z : C) (hz0 : dim z = 0) (Ym : Finset R)
    (hY : ∀ i ∈ Ym, chart 0 i = z ∧ dim (chart n i) = 8) (hV : ∀ i ∉ Ym, dim (chart n i) = 9)
    (hz : ∀ q, ¬ N.inS q z)
    (P : Finset (YP × XP)) (path : YP × XP → List Mv)
    (hpath : ∀ π ∈ P, N.Chain (N.A π.2) (path π) (N.G π.1)) :
    ∑ π ∈ P, N.dist (cg dim) (N.A π.2) (N.G π.1) ≤ ∑ i, hsum fL (if i ∈ Ym then 8 else 9)
      ((dim (chart 0 i) : ℝ) :: (movesOf chart mv i n).map fun m => (dim (N.tgt m) : ℝ)) :=
  N.T1_bound (cg dim) (N.wz dim z) P path hpath (fun _ _ => le_max_right _ _)
    (fun m => by unfold wz; split_ifs; exact le_rfl; exact le_max_right _ _) z hz
    (fun m hm => by simp [wz, hm]) _
    (N.T1_cost chart mv n hmv hmono hsurj hinj dim hdim z hz0 Ym hY hV)

end Net

end T1link



/-! ## T3. Slot lemma (level 7) -/

section T3

open Module Submodule

variable {K V Reg D C : Type*} [Field K] [AddCommGroup V] [Module K V] [FiniteDimensional K V]
  [DecidableEq Reg] [Fintype D]

/-- **T3 slot lemma.** Data at level 7 (all T2 outputs are hypotheses):
* `Cr` = crossers of level 7 with crossing rows `ρ μ`, linearly independent (T2(a));
* `B0` = registers born at chart 0 with tokens `tok b`; `S0 = span tok(B0)`;
* `W ⊆ Cr ∩ B0` = 0-born registers jumping from chart 0 straight to dim 8/9; their crossing rows lie
  in `S0` (chart 0 holds only 0-born tokens); `Z = (B0 ∩ Cr) \ W` (0-born, cross after a paid stop);
* `P` fixes every crossing row and kills the tokens of 0-born registers that never cross
  (a projection onto span ρ(Cr) along the stayer tokens; it exists because these are complementary,
  T2 proof — see `proj_exists`);
* for `p ∈ D`: `y p = Σ_μ A p μ • ρ μ` (T2(b)), where a non-`W` crosser has `A p μ ≠ 0` only if it
  lands at `G p` (a level-7 crosser landing `≤ G_p`, dim 8, lands AT `G_p`), and `G` is injective;
* `y p = x p + e p` with `e p ∈ S0` (Y_p's token) and `0 ≠ x p ∈ X`, `X ⊓ S0 = ⊥` (X content and
  0-born tokens are different coordinates).
Then `|D| ≤ rank{x_p} + |Z|`. No directness of the `Y_p`, `p ∈ D`, is needed. -/
theorem slot_lemma (Cr B0 W : Finset Reg) (hW : W ⊆ B0 ∩ Cr)
    (ρ tok : Reg → V) (P : V →ₗ[K] V)
    (hind : ∀ g : Reg → K, ∑ μ ∈ Cr, g μ • ρ μ = 0 → ∀ μ ∈ Cr, g μ = 0)
    (hPρ : ∀ μ ∈ Cr, P (ρ μ) = ρ μ)
    (hPst : ∀ b ∈ B0, b ∉ Cr → P (tok b) = 0)
    (hWS0 : ∀ μ ∈ W, ρ μ ∈ span K (tok '' (B0 : Set Reg)))
    (land : Reg → C) (G : D → C) (hG : Function.Injective G)
    (y x e : D → V) (A : D → Reg → K)
    (hT2b : ∀ p, y p = ∑ μ ∈ Cr, A p μ • ρ μ)
    (hsupp : ∀ p, ∀ μ ∈ Cr, μ ∉ W → A p μ ≠ 0 → land μ = G p)
    (hy : ∀ p, y p = x p + e p) (he : ∀ p, e p ∈ span K (tok '' (B0 : Set Reg)))
    (X : Submodule K V) (hx : ∀ p, x p ∈ X) (hXS : X ⊓ span K (tok '' (B0 : Set Reg)) = ⊥)
    (hx0 : ∀ p, x p ≠ 0) :
    Fintype.card D ≤ finrank K (span K (Set.range x)) + ((B0 ∩ Cr) \ W).card := by
  classical
  set S0 := span K (tok '' (B0 : Set Reg)) with hS0
  -- step 1: every y p has a non-W crosser in its expansion
  have hyW : ∀ p, ∃ μ ∈ Cr, μ ∉ W ∧ A p μ ≠ 0 := by
    intro p; by_contra hcon; push Not at hcon
    have hyS : y p ∈ S0 := by
      rw [hT2b p]
      refine Submodule.sum_mem _ fun μ hμ => ?_
      by_cases hμW : μ ∈ W
      · exact Submodule.smul_mem _ _ (hWS0 μ hμW)
      · rw [hcon μ hμ hμW, zero_smul]; exact Submodule.zero_mem _
    have hxS : x p ∈ S0 := by
      have : x p = y p - e p := by rw [hy p]; abel
      rw [this]; exact Submodule.sub_mem _ hyS (he p)
    have : x p ∈ X ⊓ S0 := ⟨hx p, hxS⟩
    rw [hXS] at this
    exact hx0 p ((Submodule.mem_bot K).mp this)
  -- step 2: the family (y_p)_{p ∈ D} ⊔ (ρ_h)_{h ∈ W} is linearly independent
  let F : D ⊕ W → V := Sum.elim y (fun h => ρ h)
  have hF : LinearIndependent K F := by
    rw [Fintype.linearIndependent_iff]
    intro g hg
    let gW : Reg → K := fun μ => if hμ : μ ∈ W then g (Sum.inr ⟨μ, hμ⟩) else 0
    let coef : Reg → K := fun μ => (∑ p, g (Sum.inl p) * A p μ) + gW μ
    have hW' : ∑ h : W, g (Sum.inr h) • ρ h = ∑ μ ∈ Cr, gW μ • ρ μ := by
      rw [← Finset.sum_subset (fun μ hμ => (mem_inter.mp (hW hμ)).2)
        (fun μ _ hμ => by simp [gW, hμ])]
      rw [← Finset.sum_attach W]
      refine Finset.sum_congr rfl fun h _ => ?_
      simp [gW, h.2]
    have hsum : ∑ μ ∈ Cr, coef μ • ρ μ = 0 := by
      rw [← hg, Fintype.sum_sum_type]
      simp only [F, Sum.elim_inl, Sum.elim_inr, hT2b, Finset.smul_sum, smul_smul, coef, add_smul,
        Finset.sum_add_distrib, Finset.sum_smul]
      rw [hW', Finset.sum_comm]
    have hc := hind coef hsum
    -- non-W crossers: only one p contributes
    have hone : ∀ μ ∈ Cr, μ ∉ W → ∀ p, g (Sum.inl p) * A p μ = 0 := by
      intro μ hμ hμW p
      have h0 : coef μ = 0 := hc μ hμ
      simp only [coef, gW, hμW, dite_false, add_zero] at h0
      by_cases hA2 : A p μ = 0
      · simp [hA2]
      rw [Finset.sum_eq_single p] at h0
      · exact h0
      · intro p' _ hp'
        by_cases hA : A p' μ = 0
        · simp [hA]
        exact absurd (hG ((hsupp p' μ hμ hμW hA).symm.trans (hsupp p μ hμ hμW hA2))) hp'
      · simp
    have hD0 : ∀ p, g (Sum.inl p) = 0 := by
      intro p
      obtain ⟨μ, hμ, hμW, hA⟩ := hyW p
      exact (mul_eq_zero.mp (hone μ hμ hμW p)).resolve_right hA
    rintro (p | ⟨μ, hμW⟩)
    · exact hD0 p
    · have h0 : coef μ = 0 := hc μ (mem_inter.mp (hW hμW)).2
      simp only [coef, gW, hμW, dite_true, hD0, zero_mul, Finset.sum_const_zero, zero_add] at h0
      exact h0
  -- step 3: the family lies in span(P x) ⊔ E
  let E : Submodule K V := span K (((B0 ∩ Cr).image fun b => P (tok b) : Finset V) : Set V)
  have hPS0 : ∀ v ∈ S0, P v ∈ E := by
    have : S0.map P ≤ E := by
      rw [hS0, Submodule.map_span, Submodule.span_le]
      rintro _ ⟨_, ⟨b, hb, rfl⟩, rfl⟩
      by_cases hbC : b ∈ Cr
      · exact Submodule.subset_span (by simp only [coe_image, coe_inter]; exact ⟨b, ⟨hb, hbC⟩, rfl⟩)
      · simp only [SetLike.mem_coe]; rw [hPst b hb hbC]; exact Submodule.zero_mem _
    exact fun v hv => this (Submodule.mem_map_of_mem hv)
  set Sx := span K (Set.range fun p => P (x p))
  have hrange : Set.range F ⊆ (Sx ⊔ E : Submodule K V) := by
    rintro _ ⟨i, rfl⟩
    rcases i with p | ⟨μ, hμW⟩
    · have hPy : P (y p) = y p := by
        rw [hT2b p, map_sum]
        exact Finset.sum_congr rfl fun μ hμ => by rw [map_smul, hPρ μ hμ]
      show y p ∈ Sx ⊔ E
      rw [← hPy, hy p, map_add]
      exact Submodule.add_mem _ (Submodule.mem_sup_left (Submodule.subset_span ⟨p, rfl⟩))
        (Submodule.mem_sup_right (hPS0 _ (he p)))
    · show ρ μ ∈ Sx ⊔ E
      rw [← hPρ μ (mem_inter.mp (hW hμW)).2]
      exact Submodule.mem_sup_right (hPS0 _ (hWS0 μ hμW))
  -- step 4: count
  have h1 : Fintype.card (D ⊕ W) ≤ finrank K (Sx ⊔ E : Submodule K V) := by
    rw [← finrank_span_eq_card hF]
    exact Submodule.finrank_mono (Submodule.span_le.mpr hrange)
  have h2 := Submodule.finrank_add_le_finrank_add_finrank Sx E
  have h3 : finrank K Sx ≤ finrank K (span K (Set.range x)) := by
    have : Sx = (span K (Set.range x)).map P := by
      rw [Submodule.map_span, ← Set.range_comp]; rfl
    rw [this]; exact Submodule.finrank_map_le _ _
  have h4 : finrank K E ≤ (B0 ∩ Cr).card :=
    (finrank_span_finset_le_card _).trans Finset.card_image_le
  have h5 : (B0 ∩ Cr).card = W.card + ((B0 ∩ Cr) \ W).card := by
    rw [add_comm, Finset.card_sdiff_add_card_eq_card hW]
  rw [Fintype.card_sum, Fintype.card_coe] at h1
  omega

/-- the projection `P` of T3 exists whenever the crossing span and the stayer-token span are
complementary (T2's proof gives exactly this). -/
theorem proj_exists (R Q : Submodule K V) (hRQ : IsCompl R Q) :
    ∃ P : V →ₗ[K] V, (∀ v ∈ R, P v = v) ∧ (∀ v ∈ Q, P v = 0) := by
  refine ⟨R.subtype ∘ₗ Submodule.projectionOnto R Q hRQ, fun v hv => ?_, fun v hv => ?_⟩
  · simp [Submodule.projectionOnto_apply_of_mem_left hRQ hv]
  · simp [Submodule.projectionOnto_apply_of_mem_right hRQ hv]

end T3

/-! ## T2. Crossing-basis lemma (complementarity), from the level-k op semantics -/

section T2

open Module Submodule

/-- dimension count: if `a ⊔ b = ⊤`, `dim a ≤ m`, `dim b ≤ n` and `dim V = m + n`, then `a`, `b`
are complementary and both bounds are equalities. -/
lemma compl_of_sup {K V : Type*} [Field K] [AddCommGroup V] [Module K V] [FiniteDimensional K V]
    (a b : Submodule K V) (m n : ℕ) (hsup : a ⊔ b = ⊤) (ha : finrank K a ≤ m) (hb : finrank K b ≤ n)
    (hV : finrank K V = m + n) : IsCompl a b ∧ finrank K a = m ∧ finrank K b = n := by
  have h := Submodule.finrank_sup_add_finrank_inf_eq a b
  rw [hsup, finrank_top, hV] at h
  have h0 : finrank K (a ⊓ b : Submodule K V) = 0 := by omega
  refine ⟨⟨disjoint_iff.mpr (Submodule.finrank_eq_zero.mp h0), codisjoint_iff.mpr hsup⟩, by omega,
    by omega⟩

lemma finrank_span_image_le {K V ι : Type*} [Field K] [AddCommGroup V] [Module K V]
    (s : Finset ι) (f : ι → V) : finrank K (span K (f '' (s : Set ι))) ≤ s.card := by
  classical
  rw [← Finset.coe_image]; exact (finrank_span_finset_le_card _).trans Finset.card_image_le

variable {K Reg : Type*} [Field K] [Fintype Reg] [DecidableEq Reg]

/-- ops seen at level `k`: an ADD `row_i += c·row_j` (co-present, so on the same side of level `k`),
or register `i` crossing level `k` (its first move from dim `≤ k` to dim `> k`). Moves that do not
cross level `k` change neither rows nor sides, so they are omitted. -/
inductive LOp (K Reg : Type*)
  | add (i j : Reg) (c : K)
  | cross (i : Reg)

/-- rows (initial-row coordinates), registers above level `k`, crossers so far, crossing rows. -/
structure LSt (K Reg : Type*) where
  row : Reg → Reg → K
  ab : Finset Reg
  cr : Finset Reg
  rho : Reg → Reg → K

def lstep : LSt K Reg → LOp K Reg → LSt K Reg
  | s, .add i j c => ⟨Function.update s.row i (s.row i + c • s.row j), s.ab, s.cr, s.rho⟩
  | s, .cross i => ⟨s.row, insert i s.ab, insert i s.cr, Function.update s.rho i (s.row i)⟩

def lrun : LSt K Reg → List (LOp K Reg) → LSt K Reg
  | s, [] => s
  | s, op :: ops => lrun (lstep s op) ops

/-- legality: an ADD has `i ≠ j` (an invertible public op) and both registers on the same side of
level `k` (co-presence at one chart); a crossing register is still at dim `≤ k`. -/
def LLegal : LSt K Reg → List (LOp K Reg) → Prop
  | _, [] => True
  | s, .add i j c :: ops => (i ≠ j ∧ (i ∈ s.ab ↔ j ∈ s.ab)) ∧ LLegal (lstep s (.add i j c)) ops
  | s, .cross i :: ops => i ∉ s.ab ∧ LLegal (lstep s (.cross i)) ops

/-- time 0: every register holds its own token; `B` = registers born at dim `≤ k`, the rest are
above level `k` already. -/
def lstart (B : Finset Reg) : LSt K Reg := ⟨fun r => Pi.single r 1, univ \ B, ∅, fun _ => 0⟩

/-- the run invariant (for any linear `L` that kills the tokens of registers born above `k`). -/
structure LInv {W : Type*} [AddCommGroup W] [Module K W] (B : Finset Reg) (L : (Reg → K) →ₗ[K] W)
    (s : LSt K Reg) : Prop where
  crB : s.cr ⊆ B
  ab_iff : ∀ r, r ∈ s.ab ↔ (r ∉ B ∨ r ∈ s.cr)
  up : ∀ r ∈ s.ab, L (s.row r) ∈ span K ((fun μ => L (s.rho μ)) '' (s.cr : Set Reg))
  top : span K (Set.range s.row) = ⊤

lemma linv_start {W : Type*} [AddCommGroup W] [Module K W] (B : Finset Reg)
    (L : (Reg → K) →ₗ[K] W) (hL : ∀ r, r ∉ B → L (Pi.single r 1) = 0) :
    LInv B L (lstart (K := K) B) where
  crB := by simp [lstart]
  ab_iff := by intro r; simp [lstart]
  up := by
    intro r hr
    simp only [lstart, mem_sdiff, mem_univ, true_and] at hr
    simp only [lstart]; rw [hL r hr]; exact Submodule.zero_mem _
  top := by
    have : Set.range (fun r : Reg => (Pi.single r (1 : K) : Reg → K)) =
        Set.range (Pi.basisFun K Reg) := by
      congr 1; funext r; simp
    simp only [lstart]; rw [this]; exact (Pi.basisFun K Reg).span_eq

lemma linv_step {W : Type*} [AddCommGroup W] [Module K W] (B : Finset Reg)
    (L : (Reg → K) →ₗ[K] W) (s : LSt K Reg) (op : LOp K Reg) (hI : LInv B L s)
    (hop : match op with
      | .add i j _ => i ≠ j ∧ (i ∈ s.ab ↔ j ∈ s.ab)
      | .cross i => i ∉ s.ab) :
    LInv B L (lstep s op) := by
  cases op with
  | add i j c =>
    obtain ⟨hij, hside⟩ := hop
    refine ⟨hI.crB, hI.ab_iff, ?_, ?_⟩
    · intro r hr
      simp only [lstep] at hr ⊢
      by_cases hri : r = i
      · subst hri
        rw [Function.update_self, map_add, map_smul]
        exact Submodule.add_mem _ (hI.up r hr) (Submodule.smul_mem _ _ (hI.up j (hside.mp hr)))
      · rw [Function.update_of_ne hri]; exact hI.up r hr
    · rw [eq_top_iff, ← hI.top, Submodule.span_le]
      rintro _ ⟨r, rfl⟩
      simp only [lstep]
      set u := Function.update s.row i (s.row i + c • s.row j) with hu
      by_cases hri : r = i
      · subst hri
        have e1 : s.row r = u r - c • u j := by
          rw [hu, Function.update_self, Function.update_of_ne (Ne.symm hij)]; abel
        rw [e1]
        exact Submodule.sub_mem _ (Submodule.subset_span ⟨r, rfl⟩)
          (Submodule.smul_mem _ _ (Submodule.subset_span ⟨j, rfl⟩))
      · have : s.row r = u r := by
          rw [hu, Function.update_of_ne hri]
        rw [this]; exact Submodule.subset_span ⟨r, rfl⟩
  | cross i =>
    have hiB : i ∈ B := by
      by_contra h; exact hop ((hI.ab_iff i).mpr (Or.inl h))
    have hicr : i ∉ s.cr := fun h => hop ((hI.ab_iff i).mpr (Or.inr h))
    have hmono : span K ((fun μ => L (s.rho μ)) '' (s.cr : Set Reg)) ≤
        span K ((fun μ => L (Function.update s.rho i (s.row i) μ)) '' ((insert i s.cr : Finset Reg) : Set Reg)) := by
      apply Submodule.span_mono
      rintro _ ⟨μ, hμ, rfl⟩
      have hμi : μ ≠ i := fun e => hicr (e ▸ hμ)
      refine ⟨μ, by simp [hμ], ?_⟩
      simp [Function.update_of_ne hμi]
    refine ⟨?_, ?_, ?_, hI.top⟩
    · simp only [lstep]; exact Finset.insert_subset hiB hI.crB
    · intro r; simp only [lstep, mem_insert]
      rw [hI.ab_iff r]; tauto
    · intro r hr
      simp only [lstep, mem_insert] at hr ⊢
      rcases hr with rfl | hr
      · apply Submodule.subset_span
        exact ⟨r, by simp, by simp⟩
      · exact hmono (hI.up r hr)

lemma linv_run {W : Type*} [AddCommGroup W] [Module K W] (B : Finset Reg)
    (L : (Reg → K) →ₗ[K] W) : ∀ (s : LSt K Reg) (ops : List (LOp K Reg)),
    LInv B L s → LLegal s ops → LInv B L (lrun s ops)
  | s, [], hI, _ => hI
  | s, .add i j c :: ops, hI, ⟨h, hL⟩ => linv_run B L _ ops (linv_step B L s _ hI h) hL
  | s, .cross i :: ops, hI, ⟨h, hL⟩ => linv_run B L _ ops (linv_step B L s _ hI h) hL

/-- restriction to the coordinates of registers born at dim `≤ k`. -/
def resB (B : Finset Reg) : (Reg → K) →ₗ[K] (B → K) := LinearMap.funLeft K K (Subtype.val)

lemma resB_single (B : Finset Reg) (r : Reg) (hr : r ∉ B) : resB B (Pi.single r (1 : K)) = 0 := by
  funext b
  have : (b : Reg) ≠ r := fun e => hr (e ▸ b.2)
  simp [resB, LinearMap.funLeft_apply, Pi.single_apply, this]

/-- **T2 (crossing-basis lemma), from the op semantics.** Run legal level-`k` ops from time 0
(`B` = registers born at dim `≤ k`). Class-N hypothesis: every stayer (born `≤ k`, never crosses)
ends as its own token. Restrict rows to the coordinates of `B` (`resB`). Then
* `cr ⊆ B`;
* (complementarity) the crossing rows and the stayer tokens span complementary subspaces of `B → K`;
* (T2(a)) the crossing rows are linearly independent;
* (T2(b), existence) every register above level `k` at the end (born above, or crossed) has its
  restricted final row in the span of the crossing rows. -/
theorem T2_run (B : Finset Reg) (ops : List (LOp K Reg)) (hL : LLegal (lstart B) ops)
    (hst : ∀ r ∈ B, r ∉ (lrun (lstart B) ops).cr → (lrun (lstart B) ops).row r = Pi.single r 1) :
    (lrun (lstart (K := K) B) ops).cr ⊆ B ∧
    IsCompl (span K ((fun μ => resB B ((lrun (lstart B) ops).rho μ)) '' ((lrun (lstart B) ops).cr : Set Reg)))
      (span K ((fun b => resB B (Pi.single b (1 : K))) '' ((B \ (lrun (lstart B) ops).cr : Finset Reg) : Set Reg))) ∧
    LinearIndependent K (fun μ : (lrun (lstart (K := K) B) ops).cr => resB B ((lrun (lstart B) ops).rho μ)) ∧
    (∀ r, r ∉ B ∨ r ∈ (lrun (lstart (K := K) B) ops).cr →
      resB B ((lrun (lstart B) ops).row r) ∈
        span K ((fun μ => resB B ((lrun (lstart B) ops).rho μ)) '' ((lrun (lstart B) ops).cr : Set Reg))) := by
  classical
  set s := lrun (lstart (K := K) B) ops
  have hI : LInv B (resB B) s := linv_run B (resB B) _ ops (linv_start B _ (resB_single B)) hL
  set a := span K ((fun μ => resB B (s.rho μ)) '' (s.cr : Set Reg))
  set b := span K ((fun b => resB B (Pi.single b (1 : K))) '' ((B \ s.cr : Finset Reg) : Set Reg))
  have hsup : a ⊔ b = ⊤ := by
    have hsurj : Function.Surjective (resB (K := K) B) :=
      LinearMap.funLeft_surjective_of_injective _ _ _ Subtype.val_injective
    rw [eq_top_iff, ← LinearMap.range_eq_top.mpr hsurj, LinearMap.range_eq_map, ← hI.top,
      Submodule.map_span, Submodule.span_le]
    rintro _ ⟨_, ⟨r, rfl⟩, rfl⟩
    by_cases hr : r ∈ s.ab
    · exact Submodule.mem_sup_left (hI.up r hr)
    · have hrB : r ∈ B := by by_contra h; exact hr ((hI.ab_iff r).mpr (Or.inl h))
      have hrc : r ∉ s.cr := fun h => hr ((hI.ab_iff r).mpr (Or.inr h))
      apply Submodule.mem_sup_right
      rw [hst r hrB hrc]
      exact Submodule.subset_span ⟨r, by simp [hrB, hrc], rfl⟩
  have ha : finrank K a ≤ s.cr.card := finrank_span_image_le _ _
  have hb : finrank K b ≤ (B \ s.cr).card := finrank_span_image_le _ _
  have hV : finrank K (B → K) = s.cr.card + (B \ s.cr).card := by
    rw [Module.finrank_fintype_fun_eq_card, Fintype.card_coe, add_comm,
      Finset.card_sdiff_add_card_eq_card hI.crB]
  obtain ⟨hc, hfa, -⟩ := compl_of_sup a b _ _ hsup ha hb hV
  refine ⟨hI.crB, hc, ?_, fun r hr => hI.up r ((hI.ab_iff r).mpr hr)⟩
  rw [linearIndependent_iff_card_eq_finrank_span, Set.finrank]
  have : Set.range (fun μ : s.cr => resB B (s.rho μ)) = (fun μ => resB B (s.rho μ)) '' (s.cr : Set Reg) := by
    ext v; simp
  rw [this, Fintype.card_coe]; exact hfa.symm

end T2

/-! ### T3 with T2 discharged -/

section T3T2

open Module Submodule

/-- **T3 with the complementarity discharged.** `slot_lemma` with its T2 hypotheses (independence of
the crossing rows, and the projection `P`) replaced by the T2 data: the crossing rows `ρ(Cr)` and the
stayer tokens `tok(St)` span `V`, `dim V = |Cr| + |St|`, and every 0-born non-crosser is a stayer.
(`T2_run` derives exactly this from the op semantics, with `V = B → K`.) -/
theorem slot_lemma_T2 {K V Reg D C : Type*} [Field K] [AddCommGroup V] [Module K V]
    [FiniteDimensional K V] [DecidableEq Reg] [Fintype D]
    (Cr B0 W St : Finset Reg) (hW : W ⊆ B0 ∩ Cr) (ρ tok : Reg → V)
    (hsup : span K (ρ '' (Cr : Set Reg)) ⊔ span K (tok '' (St : Set Reg)) = ⊤)
    (hdim : finrank K V = Cr.card + St.card)
    (hSt : ∀ b ∈ B0, b ∉ Cr → b ∈ St)
    (hWS0 : ∀ μ ∈ W, ρ μ ∈ span K (tok '' (B0 : Set Reg)))
    (land : Reg → C) (G : D → C) (hG : Function.Injective G)
    (y x e : D → V) (A : D → Reg → K)
    (hT2b : ∀ p, y p = ∑ μ ∈ Cr, A p μ • ρ μ)
    (hsupp : ∀ p, ∀ μ ∈ Cr, μ ∉ W → A p μ ≠ 0 → land μ = G p)
    (hy : ∀ p, y p = x p + e p) (he : ∀ p, e p ∈ span K (tok '' (B0 : Set Reg)))
    (X : Submodule K V) (hx : ∀ p, x p ∈ X) (hXS : X ⊓ span K (tok '' (B0 : Set Reg)) = ⊥)
    (hx0 : ∀ p, x p ≠ 0) :
    Fintype.card D ≤ finrank K (span K (Set.range x)) + ((B0 ∩ Cr) \ W).card := by
  obtain ⟨hc, hfa, -⟩ := compl_of_sup _ _ _ _ hsup (finrank_span_image_le _ _)
    (finrank_span_image_le _ _) hdim
  obtain ⟨P, hP1, hP2⟩ := proj_exists _ _ hc
  have hli : LinearIndependent K (fun μ : Cr => ρ μ) := by
    rw [linearIndependent_iff_card_eq_finrank_span, Set.finrank]
    have : Set.range (fun μ : Cr => ρ μ) = ρ '' (Cr : Set Reg) := by ext v; simp
    rw [this, Fintype.card_coe]; exact hfa.symm
  refine slot_lemma Cr B0 W hW ρ tok P ?_ (fun μ hμ => hP1 _ (subset_span ⟨μ, hμ, rfl⟩))
    (fun b hb hbC => hP2 _ (subset_span ⟨b, hSt b hb hbC, rfl⟩)) hWS0 land G hG y x e A hT2b hsupp
    hy he X hx hXS hx0
  intro g hg μ hμ
  have := Fintype.linearIndependent_iff.mp hli (fun μ => g μ)
    (by rw [Finset.sum_coe_sort Cr (fun μ => g μ • ρ μ)]; exact hg)
  exact this ⟨μ, hμ⟩

/-- **T3 from the op semantics.** Level-7 run (`T2_run`): `B` = registers born at dim `≤ 7`, `B0 ⊆ B`
the 0-born ones, stayers end as their own tokens (class N). In `V = B → K` with crossing rows
`resB(ρ_μ)` and tokens `resB(e_b)`, the slot bound holds with only T2(b)'s coefficient/support data,
the W/S0 facts and the X/S0 split left as hypotheses. -/
theorem slot_lemma_run {K Reg D C : Type*} [Field K] [Fintype Reg] [DecidableEq Reg] [Fintype D]
    (B B0 W : Finset Reg) (hB0 : B0 ⊆ B) (ops : List (LOp K Reg)) (hL : LLegal (lstart B) ops)
    (hst : ∀ r ∈ B, r ∉ (lrun (lstart B) ops).cr → (lrun (lstart B) ops).row r = Pi.single r 1)
    (hW : W ⊆ B0 ∩ (lrun (lstart (K := K) B) ops).cr)
    (hWS0 : ∀ μ ∈ W, resB B ((lrun (lstart B) ops).rho μ) ∈
      span K ((fun b => resB B (Pi.single b (1 : K))) '' (B0 : Set Reg)))
    (land : Reg → C) (G : D → C) (hG : Function.Injective G)
    (y x e : D → (B → K)) (A : D → Reg → K)
    (hT2b : ∀ p, y p = ∑ μ ∈ (lrun (lstart (K := K) B) ops).cr,
      A p μ • resB B ((lrun (lstart B) ops).rho μ))
    (hsupp : ∀ p, ∀ μ ∈ (lrun (lstart (K := K) B) ops).cr, μ ∉ W → A p μ ≠ 0 → land μ = G p)
    (hy : ∀ p, y p = x p + e p)
    (he : ∀ p, e p ∈ span K ((fun b => resB B (Pi.single b (1 : K))) '' (B0 : Set Reg)))
    (X : Submodule K (B → K)) (hx : ∀ p, x p ∈ X)
    (hXS : X ⊓ span K ((fun b => resB B (Pi.single b (1 : K))) '' (B0 : Set Reg)) = ⊥)
    (hx0 : ∀ p, x p ≠ 0) :
    Fintype.card D ≤ finrank K (span K (Set.range x)) +
      ((B0 ∩ (lrun (lstart (K := K) B) ops).cr) \ W).card := by
  obtain ⟨hcrB, hc, -, -⟩ := T2_run B ops hL hst
  set s := lrun (lstart (K := K) B) ops
  refine slot_lemma_T2 s.cr B0 W (B \ s.cr) hW (fun μ => resB B (s.rho μ))
    (fun b => resB B (Pi.single b (1 : K))) hc.sup_eq_top ?_ ?_ hWS0 land G hG y x e A hT2b hsupp
    hy he X hx hXS hx0
  · rw [Module.finrank_fintype_fun_eq_card, Fintype.card_coe, add_comm,
      Finset.card_sdiff_add_card_eq_card hcrB]
  · intro b hb hbC; exact Finset.mem_sdiff.mpr ⟨hB0 hb, hbC⟩

end T3T2


/-! ## T4. Departer law, corrected scope (all arrivals, owned included) -/

section T4

open Module Submodule

variable {K Reg : Type*} [Field K] [Fintype Reg] [DecidableEq Reg]

/-- events at ONE chart `c`, in time order: a register arrives with a row, a register is born at
`c` (row = its own token), an ADD `row_i += k·row_j`, or a register departs (moves up). -/
inductive Ev (K Reg : Type*)
  | arrive (i : Reg) (v : Reg → K)
  | born (b : Reg)
  | add (i j : Reg) (k : K)
  | depart (i : Reg)

/-- rows (initial-row coordinates `Reg → K`) and the set of registers present at `c`. -/
structure St (K Reg : Type*) where
  row : Reg → Reg → K
  pres : Finset Reg

def step : St K Reg → Ev K Reg → St K Reg
  | s, .arrive i v => ⟨Function.update s.row i v, insert i s.pres⟩
  | s, .born b => ⟨Function.update s.row b (Pi.single b 1), insert b s.pres⟩
  | s, .add i j k => ⟨Function.update s.row i (s.row i + k • s.row j), s.pres⟩
  | s, .depart i => ⟨s.row, s.pres.erase i⟩

def run : St K Reg → List (Ev K Reg) → St K Reg
  | s, [] => s
  | s, ev :: evs => run (step s ev) evs

/-- an ADD at `c` only reads and writes registers present at `c` (owned ones included: they are
registers like any other and must ARRIVE or be BORN at `c` to be present). -/
def Legal : St K Reg → List (Ev K Reg) → Prop
  | _, [] => True
  | s, .add i j k :: evs => (i ∈ s.pres ∧ j ∈ s.pres) ∧ Legal (step s (.add i j k)) evs
  | s, ev :: evs => Legal (step s ev) evs

/-- invariant: every present row lies in `N` as long as all arrival rows and born tokens do. -/
lemma run_inv (N : Submodule K (Reg → K)) :
    ∀ (s : St K Reg) (evs : List (Ev K Reg)), Legal s evs →
      (∀ i ∈ s.pres, s.row i ∈ N) →
      (∀ i v, Ev.arrive i v ∈ evs → v ∈ N) → (∀ b, Ev.born b ∈ evs → Pi.single b 1 ∈ N) →
      ∀ i ∈ (run s evs).pres, (run s evs).row i ∈ N
  | s, [], _, hs, _, _ => hs
  | s, ev :: evs, hL, hs, harr, hborn => by
    have harr' : ∀ i v, Ev.arrive i v ∈ evs → v ∈ N := fun i v h => harr i v (by simp [h])
    have hborn' : ∀ b, Ev.born b ∈ evs → Pi.single b 1 ∈ N := fun b h => hborn b (by simp [h])
    cases ev with
    | arrive i v =>
      refine run_inv N _ evs hL ?_ harr' hborn'
      intro r hr
      simp only [step, mem_insert] at hr ⊢
      by_cases hri : r = i
      · subst hri; simp only [Function.update_self]; exact harr r v (by simp)
      · rw [Function.update_of_ne hri]; exact hs r (hr.resolve_left hri)
    | born b =>
      refine run_inv N _ evs hL ?_ harr' hborn'
      intro r hr
      simp only [step, mem_insert] at hr ⊢
      by_cases hrb : r = b
      · subst hrb; simp only [Function.update_self]; exact hborn r (by simp)
      · rw [Function.update_of_ne hrb]; exact hs r (hr.resolve_left hrb)
    | add i j k =>
      obtain ⟨⟨hi, hj⟩, hL⟩ := hL
      refine run_inv N _ evs hL ?_ harr' hborn'
      intro r hr
      simp only [step] at hr ⊢
      by_cases hri : r = i
      · subst hri; simp only [Function.update_self]
        exact N.add_mem (hs r hi) (N.smul_mem k (hs j hj))
      · rw [Function.update_of_ne hri]; exact hs r hr
    | depart i =>
      refine run_inv N _ evs hL ?_ harr' hborn'
      intro r hr
      simp only [step, mem_erase] at hr ⊢
      exact hs r hr.2

/-- the c-born coordinates can be stripped: if `v ∈ span S ⊔ span tok(Born)`, every generator in
`S` vanishes on `Born`, and `v` vanishes on `Born`, then `v ∈ span S`. -/
lemma strip_born (S : Set (Reg → K)) (Born : Finset Reg) (hS : ∀ u ∈ S, ∀ b ∈ Born, u b = 0)
    (v : Reg → K) (hv : v ∈ span K S ⊔ span K ((fun b => Pi.single b (1 : K)) '' (Born : Set Reg)))
    (hvB : ∀ b ∈ Born, v b = 0) : v ∈ span K S := by
  let L : (Reg → K) →ₗ[K] (Reg → K) :=
    LinearMap.pi fun r => if r ∈ Born then LinearMap.proj r else 0
  have hL : ∀ u r, L u r = if r ∈ Born then u r else 0 := by
    intro u r; by_cases hr : r ∈ Born <;> simp [L, hr]
  have hA : span K S ≤ LinearMap.ker L := by
    rw [Submodule.span_le]; intro u hu
    simp only [SetLike.mem_coe, LinearMap.mem_ker]; funext r
    rw [hL]; split_ifs with hr
    · exact hS u hu r hr
    · rfl
  have hT : span K ((fun b => Pi.single b (1 : K)) '' (Born : Set Reg)) ≤ LinearMap.eqLocus L LinearMap.id := by
    rw [Submodule.span_le]; rintro _ ⟨b, hb, rfl⟩
    simp only [SetLike.mem_coe, LinearMap.mem_eqLocus, LinearMap.id_coe, id_eq]; funext r
    rw [hL]; split_ifs with hr
    · rfl
    · have : r ≠ b := fun h => hr (h ▸ hb)
      simp [Pi.single_apply, this]
  obtain ⟨a, ha, t, ht, rfl⟩ := Submodule.mem_sup.mp hv
  have hLv : L (a + t) = 0 := by
    funext r; rw [hL]; split_ifs with hr
    · exact hvB r hr
    · rfl
  have hLa : L a = 0 := hA ha
  have hLt : L t = t := LinearMap.mem_eqLocus.mp (hT ht)
  rw [map_add, hLa, zero_add, hLt] at hLv
  rw [hLv, add_zero]; exact ha

/-- **T4 (departer law), corrected scope.** One chart `c ≠ V` with its event list `evs` (legal, from
the empty state). Arrivals `Arr = Pub ∪ Own` (public and OWNED registers arriving at `c`, disjoint),
arrival rows `arrRow`, which carry no `c`-born coordinates; `Born` = registers born at `c`, disjoint
from `Arr`. Class N: a public register still at `c` at the end (an ender), other than a Y main in
`Ey`, has final row = its own token, and `π` kills that token. Then
`dim π(Arr_c) ≤ #public departers + #owned arrivals + #Y enders`. -/
theorem T4_departer (π : (Reg → K) →ₗ[K] (Reg → K)) (evs : List (Ev K Reg))
    (Pub Own Born Ey : Finset Reg) (arrRow : Reg → Reg → K)
    (hL : Legal ⟨fun _ => 0, ∅⟩ evs)
    (harr : ∀ i v, Ev.arrive i v ∈ evs → (i ∈ Pub ∪ Own) ∧ v = arrRow i)
    (hborn : ∀ b, Ev.born b ∈ evs → b ∈ Born)
    (hPO : Disjoint Pub Own) (hAB : Disjoint (Pub ∪ Own) Born)
    (hrowB : ∀ i ∈ Pub ∪ Own, ∀ b ∈ Born, arrRow i b = 0)
    (hfinal : ∀ h ∈ Pub, h ∈ (run ⟨fun _ => 0, ∅⟩ evs).pres → h ∉ Ey →
      (run ⟨fun _ => 0, ∅⟩ evs).row h = Pi.single h 1)
    (hπ : ∀ h ∈ Pub, h ∉ Ey → π (Pi.single h 1) = 0) :
    finrank K ((span K (arrRow '' ((Pub ∪ Own : Finset Reg) : Set Reg))).map π) ≤
      (Pub.filter fun h => h ∉ (run ⟨fun _ => 0, ∅⟩ evs).pres).card + Own.card + Ey.card := by
  classical
  set sf := run ⟨fun _ => 0, ∅⟩ evs
  set Arr := Pub ∪ Own
  set A := span K (arrRow '' (Arr : Set Reg))
  set Etok := (Pub.filter fun h => h ∈ sf.pres) \ Ey
  -- enders' tokens lie in A
  have hEA : ∀ h ∈ Etok, (Pi.single h (1 : K) : Reg → K) ∈ A := by
    intro h hh
    simp only [Etok, mem_sdiff, mem_filter] at hh
    have hM := run_inv (A ⊔ span K ((fun b => Pi.single b (1 : K)) '' (Born : Set Reg)))
      ⟨fun _ => 0, ∅⟩ evs hL (by simp)
      (fun i v hv => by
        obtain ⟨hi, rfl⟩ := harr i v hv
        exact Submodule.mem_sup_left (Submodule.subset_span ⟨i, hi, rfl⟩))
      (fun b hb => Submodule.mem_sup_right (Submodule.subset_span ⟨b, hborn b hb, rfl⟩))
      h hh.1.2
    rw [hfinal h hh.1.1 hh.1.2 hh.2] at hM
    refine strip_born _ Born ?_ _ hM ?_
    · rintro _ ⟨i, hi, rfl⟩ b hb; exact hrowB i hi b hb
    · intro b hb
      have : h ≠ b := fun e => Finset.disjoint_left.mp hAB (mem_union_left _ hh.1.1) (e ▸ hb)
      simp [Pi.single_apply, Ne.symm this]
  -- rank–nullity on π restricted to A
  let f := π.domRestrict A
  have hrn := LinearMap.finrank_range_add_finrank_ker f
  have hrange : LinearMap.range f = A.map π := LinearMap.range_domRestrict A π
  -- Etok tokens are independent inside ker f
  have hker : Etok.card ≤ finrank K (LinearMap.ker f) := by
    let g : Etok → LinearMap.ker f := fun h =>
      ⟨⟨Pi.single h.1 1, hEA h.1 h.2⟩, by
        have hh := h.2
        simp only [Etok, mem_sdiff, mem_filter] at hh
        simp [f, hπ h.1 hh.1.1 hh.2]⟩
    have hli : LinearIndependent K g := by
      apply LinearIndependent.of_comp ((LinearMap.ker f).subtype)
      apply LinearIndependent.of_comp A.subtype
      have e : (⇑A.subtype ∘ ⇑(LinearMap.ker f).subtype ∘ g) = fun h : Etok => Pi.single h.1 (1 : K) := by
        funext h; rfl
      rw [e]
      have hb := (Pi.basisFun K Reg).linearIndependent
      have : (fun h : Etok => Pi.single h.1 (1 : K)) = (Pi.basisFun K Reg) ∘ Subtype.val := by
        funext h; simp
      rw [this]; exact hb.comp _ Subtype.val_injective
    simpa using hli.fintype_card_le_finrank
  have hAc : finrank K A ≤ Arr.card := by
    have : (arrRow '' (Arr : Set Reg)) = ((Arr.image arrRow : Finset (Reg → K)) : Set (Reg → K)) := by
      simp
    rw [show A = span K (arrRow '' (Arr : Set Reg)) from rfl, this]
    exact (finrank_span_finset_le_card _).trans Finset.card_image_le
  have hArr : Arr.card = Pub.card + Own.card := Finset.card_union_of_disjoint hPO
  have hPub : Pub.card = (Pub.filter fun h => h ∉ sf.pres).card + (Pub.filter fun h => h ∈ sf.pres).card := by
    rw [add_comm]; exact (Finset.card_filter_add_card_filter_not _).symm
  have hEt : (Pub.filter fun h => h ∈ sf.pres).card ≤ Etok.card + Ey.card := by
    calc _ ≤ (Etok ∪ Ey).card := by
          apply card_le_card; intro h hh
          by_cases hy : h ∈ Ey
          · exact mem_union_right _ hy
          · exact mem_union_left _ (mem_sdiff.mpr ⟨hh, hy⟩)
      _ ≤ _ := card_union_le _ _
  rw [← hrange]
  have : finrank K A = finrank K (LinearMap.range f) + finrank K (LinearMap.ker f) := hrn.symm
  omega

/-- T4 for the public arrival span: it sits inside the all-arrivals span, so the same right-hand
side (with the owned-arrival term) bounds it. Without `Own.card` it is false (`T4_public_only_false`). -/
theorem T4_public (π : (Reg → K) →ₗ[K] (Reg → K)) (Pub Own : Finset Reg) (arrRow : Reg → Reg → K) :
    finrank K ((span K (arrRow '' (Pub : Set Reg))).map π) ≤
      finrank K ((span K (arrRow '' ((Pub ∪ Own : Finset Reg) : Set Reg))).map π) :=
  Submodule.finrank_mono (Submodule.map_mono (Submodule.span_mono
    (Set.image_mono (by simp))))

/-- each departer's move into `c` is not its final move, so it costs `h_e(a, dim c)` with
`dim c + 1 ≤ e`, which is `≥ κ = f(2)` (`kappa_le`). Re-export for T4. -/
theorem T4_stop_cost (e a b : ℝ) (hab : 1 ≤ b - a) (hbe : 1 ≤ e - b) : fL 2 ≤ h fL e a b :=
  kappa_le e a b hab hbe

/-- the public-arrivals-only version of T4 is FALSE in this model (GAPMAP scope finding: owned
register 1502 ADDs X content into Y main 213 at charts 593–595, 597). Registers `0` = public `h`,
`1` = owned `o`, `2` = X coordinate. `h` arrives with `e_h + e_x`, `o` arrives with `-e_x`, then
`h += o`: `h` ends at `c` as its own token (class N) and π kills it, yet the public arrival span has
`dim π = 1 > 0 = #public departers + #Y enders`. Counting the owned arrival (`T4_departer`) fixes it. -/
theorem T4_public_only_false :
    let π : (Fin 3 → ℚ) →ₗ[ℚ] (Fin 3 → ℚ) := (LinearMap.single ℚ (fun _ => ℚ) 2) ∘ₗ LinearMap.proj 2
    let evs : List (Ev ℚ (Fin 3)) :=
      [.arrive 0 (Pi.single 0 1 + Pi.single 2 1), .arrive 1 (-Pi.single 2 1), .add 0 1 1]
    let sf := run (⟨fun _ => 0, ∅⟩ : St ℚ (Fin 3)) evs
    Legal (⟨fun _ => 0, ∅⟩ : St ℚ (Fin 3)) evs ∧ (0 : Fin 3) ∈ sf.pres ∧
      sf.row 0 = Pi.single 0 1 ∧ π (Pi.single 0 1) = 0 ∧
      ¬ finrank ℚ ((span ℚ {(Pi.single 0 1 + Pi.single 2 1 : Fin 3 → ℚ)}).map π) ≤ 0 := by
  intro π evs sf
  refine ⟨?_, ?_, ?_, ?_, ?_⟩
  · simp [evs, Legal, step]
  · simp [sf, evs, run, step]
  · simp only [sf, evs, run, step]
    funext r; fin_cases r <;> simp [Function.update, Pi.single_apply]
  · simp [π]
  · intro h0
    have hbot := Submodule.finrank_eq_zero.mp (Nat.le_zero.mp h0)
    have hmem : π (Pi.single 0 1 + Pi.single 2 1) ∈
        (span ℚ {(Pi.single 0 1 + Pi.single 2 1 : Fin 3 → ℚ)}).map π :=
      Submodule.mem_map_of_mem (Submodule.mem_span_singleton_self _)
    rw [hbot, Submodule.mem_bot] at hmem
    have := congrFun hmem 2
    simp [π] at this

end T4

end JunkLB2

#print axioms JunkLB2.hsum_tele
#print axioms JunkLB2.kappa_le
#print axioms JunkLB2.g9_nonneg
#print axioms JunkLB2.T1_Y
#print axioms JunkLB2.l_nonneg
#print axioms JunkLB2.T1_Y_le
#print axioms JunkLB2.Net.T1_bound
#print axioms JunkLB2.slot_lemma
#print axioms JunkLB2.proj_exists
#print axioms JunkLB2.run_inv
#print axioms JunkLB2.strip_born
#print axioms JunkLB2.Net.movesOf_chain
#print axioms JunkLB2.Net.chain_hsum
#print axioms JunkLB2.Net.reg_le_V
#print axioms JunkLB2.Net.reg_le_Y
#print axioms JunkLB2.Net.T1_cost
#print axioms JunkLB2.Net.T1_full
#print axioms JunkLB2.compl_of_sup
#print axioms JunkLB2.T2_run
#print axioms JunkLB2.slot_lemma_T2
#print axioms JunkLB2.slot_lemma_run
#print axioms JunkLB2.T4_departer
#print axioms JunkLB2.T4_public
#print axioms JunkLB2.T4_stop_cost
#print axioms JunkLB2.T4_public_only_false
