/-
V2Bridge: JB edge cost vs FloorD0's helper D0 (lane LEAN-BRIDGE, Nov 16). See V2Bridge.md.

FloorD0.helperD0 = Σ_h [f(dim fin − dim ini) − Σ_moves f(Δ)], f = r ln r (PRICEKIT).
V2FloorBound.wcut θ = JB's edge price: θ(S2β + B1·[a=1]) + (1−θ)(S2α + B1·[b=8]) on 1 ≤ a < b ≤ 8, else 0.

* `chD0_bound`: per ascending chain d0 → … → e, Σ wcut ≤ D0 + corr θ d0 e (exact endpoint credit; corr θ 0 9 = 0).
* `bridge`: on EVERY accepted word, JB(E_W) ≤ helperD0 + Σ_h corr θ (dim ini h) (dim fin h), where
  E_W = distinct (ι tail, ι head) over all helper MOVEs (deduplicated; wcut ≥ 0).
* `bridge_0V`: if every helper is born at dim 0 and ends at dim 9, JB(E_W) ≤ helperD0.
* `bridge_beta_V`: θ = 1, every helper ends at V: JB_β(E_W) ≤ helperD0 + B1·#(line-born helpers).
The uncorrected bridge is false (V2Bridge.md: a one-move helper dim 1 → dim 2 has D0 = 0, JB > 0).
-/
import Nov15.FloorD0
import Nov15.V2FloorBound

open Finset

namespace V2Bridge
open V2Floor (flog B1 wt wcut fdim Sub)

noncomputable def cB (a b : ℕ) : ℝ := flog (9 - a) - flog (9 - b) - flog (b - a)
noncomputable def cA (a b : ℕ) : ℝ := flog b - flog a - flog (b - a)
/-- the B1-free θ-mix: exact per-move D0 for {0}→V helpers. -/
noncomputable def w0 (θ : ℝ) (a b : ℕ) : ℝ := θ * cB a b + (1 - θ) * cA a b
noncomputable def rho (θ : ℝ) (d : ℕ) : ℝ :=
  θ * (if d = 1 then B1 else 0) - (1 - θ) * (if d = 8 then B1 else 0)
/-- endpoint credit of a helper born at dim d0 and ending at dim e. -/
noncomputable def corr (θ : ℝ) (d0 e : ℕ) : ℝ := w0 θ d0 e + rho θ d0 - rho θ e

lemma flog_zero : flog 0 = 0 := by simp [flog]
lemma flog_one : flog 1 = 0 := by simp [flog]

lemma flog_super (x y : ℕ) : flog x + flog y ≤ flog (x + y) := by
  unfold flog
  push_cast
  rcases Nat.eq_zero_or_pos x with rfl | hx
  · simp
  rcases Nat.eq_zero_or_pos y with rfl | hy
  · simp
  have hx' : (0 : ℝ) < x := by exact_mod_cast hx
  have hy' : (0 : ℝ) < y := by exact_mod_cast hy
  have h1 : Real.log x ≤ Real.log (x + y) := Real.log_le_log hx' (by linarith)
  have h2 : Real.log y ≤ Real.log (x + y) := Real.log_le_log hy' (by linarith)
  nlinarith [mul_le_mul_of_nonneg_left h1 hx'.le, mul_le_mul_of_nonneg_left h2 hy'.le]

lemma flog_super' {a b : ℕ} (h : a ≤ b) : flog a + flog (b - a) ≤ flog b := by
  have := flog_super a (b - a); rwa [Nat.add_sub_cancel' h] at this

lemma cB_nonneg {a b : ℕ} (hab : a ≤ b) (hb : b ≤ 9) : 0 ≤ cB a b := by
  unfold cB
  have := flog_super' (a := b - a) (b := 9 - a) (by omega)
  rw [show 9 - a - (b - a) = 9 - b by omega] at this
  linarith

lemma cA_nonneg {a b : ℕ} (hab : a ≤ b) : 0 ≤ cA a b := by
  unfold cA; have := flog_super' hab; linarith

lemma B1_eq : B1 = flog 9 - flog 8 := rfl

lemma B1_nonneg : 0 ≤ B1 := by
  have := flog_super' (a := 8) (b := 9) (by norm_num)
  rw [show 9 - 8 = 1 by norm_num, flog_one] at this
  rw [B1_eq]; linarith

lemma cB01 : cB 0 1 = B1 := by simp [cB, B1_eq, flog_one]
lemma cA89 : cA 8 9 = B1 := by simp [cA, B1_eq, flog_one]
lemma cA0 (b : ℕ) : cA 0 b = 0 := by simp [cA, flog_zero]
lemma cB9 (a : ℕ) : cB a 9 = 0 := by simp [cB, flog_zero]

/-- JB's edge price is ≥ 0 on a strict ascent with b ≤ 9. -/
lemma wcut_nonneg (θ : ℝ) (h0 : 0 ≤ θ) (h1 : θ ≤ 1) {a b : ℕ} (hab : a < b) (hb : b ≤ 9) :
    0 ≤ wcut θ a b := by
  unfold wcut
  split_ifs with h
  · unfold wt
    have hb' : 0 ≤ V2Floor.Wb a b := by
      have := cB_nonneg hab.le hb
      have := B1_nonneg
      show 0 ≤ cB a b + _
      split_ifs <;> linarith
    have ha' : 0 ≤ V2Floor.Wa a b := by
      have := cA_nonneg hab.le
      have := B1_nonneg
      show 0 ≤ cA a b + _
      split_ifs <;> linarith
    have : 0 ≤ 1 - θ := by linarith
    positivity
  · exact le_rfl

/-- **per-move domination**: JB's price of a move a → b is at most its B1-free θ-mix plus a potential
difference (the line debt θB1 is prepaid by 0 → 1, the hyperplane debt (1−θ)B1 by 8 → 9). -/
theorem move_dom (θ : ℝ) (h0 : 0 ≤ θ) (h1 : θ ≤ 1) {a b : ℕ} (hab : a < b) (hb : b ≤ 9) :
    wcut θ a b ≤ w0 θ a b + rho θ a - rho θ b := by
  have hB := B1_nonneg
  have h1' : 0 ≤ 1 - θ := by linarith
  unfold wcut
  split_ifs with h
  · have ha8 : a ≠ 8 := by omega
    have hb1 : b ≠ 1 := by omega
    apply le_of_eq
    simp only [wt, V2Floor.Wb, V2Floor.Wa, w0, cB, cA, rho, ha8, hb1, if_false]
    split_ifs <;> ring
  · rcases (show a = 0 ∨ b = 9 by omega) with rfl | rfl
    · have hc := cB_nonneg (a := 0) (b := b) (by omega) hb
      simp only [w0, cA0, rho, show (0 : ℕ) ≠ 1 by norm_num, show (0 : ℕ) ≠ 8 by norm_num, if_false]
      by_cases hb1 : b = 1
      · subst hb1; rw [cB01]; simp
      · by_cases hb8 : b = 8
        · subst hb8; simp; nlinarith [mul_nonneg h0 hc, mul_nonneg h1' hB]
        · simp [hb1, hb8]; nlinarith [mul_nonneg h0 hc]
    · have hc := cA_nonneg (a := a) (b := 9) (by omega)
      simp only [w0, cB9, rho, show (9 : ℕ) ≠ 1 by norm_num, show (9 : ℕ) ≠ 8 by norm_num, if_false]
      by_cases ha8 : a = 8
      · subst ha8; rw [cA89]; simp
      · by_cases ha1 : a = 1
        · subst ha1; simp; nlinarith [mul_nonneg h1' hc, mul_nonneg h0 hB]
        · simp [ha1, ha8]; nlinarith [mul_nonneg h1' hc]

lemma fL_sub {x y : ℕ} (h : y ≤ x) : JunkLB2.fL ((x : ℝ) - y) = flog (x - y) := by
  rw [← Nat.cast_sub h]; rfl

/-- three-point identity: w0(a,b) − w0(c,b) − w0(a,c) = −h_b(a,c). -/
lemma w0_step (θ : ℝ) {a c b : ℕ} (hac : a ≤ c) (hcb : c ≤ b) :
    w0 θ a b = w0 θ c b + w0 θ a c - JunkLB2.h JunkLB2.fL (b : ℝ) (a : ℝ) (c : ℝ) := by
  simp only [JunkLB2.h, fL_sub (le_trans hac hcb), fL_sub hac, fL_sub hcb, w0, cB, cA]
  ring

lemma corr_self (θ : ℝ) (d : ℕ) : corr θ d d = 0 := by
  simp [corr, w0, cB, cA, flog_zero]

lemma corr_0V (θ : ℝ) : corr θ 0 9 = 0 := by
  simp [corr, w0, cB, cA, rho, flog_zero]

lemma corr_beta_V (d : ℕ) : corr 1 d 9 = if d = 1 then B1 else 0 := by
  simp only [corr, w0, cB9, rho]
  by_cases h : d = 1 <;> simp [h]

section Chain
open FloorE2E FloorD0
variable {K Reg C : Type*} [Field K] [DecidableEq K] [Fintype Reg] [DecidableEq Reg]
  [PartialOrder C] [DecidableEq C]

/-- **chain bound**: an ascending MOVE chain a → … → b (dims ≤ 9) has
Σ wcut θ ≤ D0 (FloorD0.chD0, f = r ln r) + corr θ (dim a) (dim b). -/
theorem chD0_bound (θ : ℝ) (h0 : 0 ≤ θ) (h1 : θ ≤ 1) (dim : C → ℕ) (hd9 : ∀ c, dim c ≤ 9) :
    ∀ (a : C) (ms : List (Mv K Reg C)) (b : C), MChain a ms b → Asc dim ms →
      (ms.map fun m => wcut θ (dim m.tail) (dim m.head)).sum ≤
        chD0 JunkLB2.fL dim a b ms + corr θ (dim a) (dim b)
  | a, [], b, hc, _ => by
    simp only [MChain] at hc; subst hc
    simp [chD0, corr_self, JunkLB2.fL0]
  | a, m :: ms, b, ⟨hm, hc⟩, hA => by
    have hlt := hA m List.mem_cons_self
    have hA' : Asc dim ms := fun x hx => hA x (List.mem_cons_of_mem _ hx)
    have ih := chD0_bound θ h0 h1 dim hd9 m.head ms b hc hA'
    have hle := chain_le m.head ms b hc hA'
    rw [chD0_cons a b m ms hm hlt]
    rw [hm] at hlt
    have hdom := move_dom θ h0 h1 hlt (hd9 _)
    have hst := w0_step θ hlt.le hle (a := dim a)
    simp only [List.map_cons, List.sum_cons, hm]
    simp only [corr] at ih ⊢
    linarith

end Chain

section Word
open FloorE2E FloorD0
variable {K Reg C : Type*} [Field K] [DecidableEq K] [Fintype Reg] [DecidableEq Reg]
  [PartialOrder C] [DecidableEq C]

/-- dimension of an optional chart as ℕ (0 for none; never used for public registers). -/
def natLoc (dim : C → ℕ) : Option C → ℕ
  | some c => dim c
  | none => 0

/-- the endpoint credit of register h in word w. -/
noncomputable def hcorr (θ : ℝ) (dim : C → ℕ) (ini : Reg → Option C) (w : List (GEv K Reg C))
    (h : Reg) : ℝ :=
  corr θ (natLoc dim (ini h)) (natLoc dim ((grun (s0 ini) w).loc h))

variable {Pub H : Finset Reg} {ini : Reg → Option C} {w : List (GEv K Reg C)}

theorem helper_bound (θ : ℝ) (h0 : 0 ≤ θ) (h1 : θ ≤ 1) (dim : C → ℕ)
    (hdim : ∀ a b : C, a < b → dim a < dim b) (hd9 : ∀ c, dim c ≤ 9)
    (hA : Accepted Pub H ini w) (h : Reg) (hh : h ∈ H) :
    (((moves (s0 ini) w).filter fun m => m.reg = h).map fun m => wcut θ (dim m.tail) (dim m.head)).sum ≤
      regD0 JunkLB2.fL dim ini w h + hcorr θ dim ini w h := by
  have hP := hA.helpers_pub hh
  obtain ⟨a, ha⟩ := Option.ne_none_iff_exists'.1 ((hA.pub_ini h).1 hP)
  obtain ⟨b, hb, hc⟩ := chain_run Pub h hP (s0 ini) w a hA.legal ha
  have hasc : Asc dim ((moves (s0 ini) w).filter fun m => m.reg = h) := by
    intro m hm
    obtain ⟨hm, hmr⟩ := List.mem_filter.1 hm
    have hmr' : m.reg = h := by simpa using hmr
    exact hdim _ _ ((moves_facts Pub (s0 ini) w hA.legal m hm).2.1 (hmr' ▸ hP))
  have hreg : regD0 JunkLB2.fL dim ini w h =
      chD0 JunkLB2.fL dim a b ((moves (s0 ini) w).filter fun m => m.reg = h) := by
    simp only [regD0, chD0, hb, ha, locD]
  have hcr : hcorr θ dim ini w h = corr θ (dim a) (dim b) := by
    simp only [hcorr, ha, hb, natLoc]
  rw [hreg, hcr]
  exact chD0_bound θ h0 h1 dim hd9 a _ b hc hasc

/-- generic dedup: summing a function ≥ 0 over the distinct images is at most the list sum. -/
lemma sum_toFinset_le {α β : Type*} [DecidableEq β] (φ : α → β) (g : β → ℝ) :
    ∀ l : List α, (∀ x ∈ l, 0 ≤ g (φ x)) → ∑ e ∈ (l.map φ).toFinset, g e ≤ (l.map fun x => g (φ x)).sum
  | [], _ => by simp
  | x :: l, hl => by
    have ih := sum_toFinset_le φ g l fun y hy => hl y (List.mem_cons_of_mem _ hy)
    have hx := hl x List.mem_cons_self
    simp only [List.map_cons, List.toFinset_cons, List.sum_cons]
    by_cases hm : φ x ∈ (l.map φ).toFinset
    · rw [Finset.insert_eq_of_mem hm]; linarith
    · rw [Finset.sum_insert hm]; linarith

lemma sum_biUnion_le' {α β : Type*} [DecidableEq β] (g : β → ℝ) (t : α → Finset β) :
    ∀ s : Finset α, (∀ a ∈ s, ∀ e ∈ t a, 0 ≤ g e) →
      ∑ e ∈ s.biUnion t, g e ≤ ∑ a ∈ s, ∑ e ∈ t a, g e := by
  classical
  intro s
  induction s using Finset.induction_on with
  | empty => intro _; simp
  | insert a s has ih =>
    intro hg
    rw [Finset.biUnion_insert, Finset.sum_insert has]
    have ih' := ih fun b hb => hg b (Finset.mem_insert_of_mem hb)
    have hu := Finset.sum_union_inter (s₁ := t a) (s₂ := s.biUnion t) (f := g)
    have hi : 0 ≤ ∑ e ∈ t a ∩ s.biUnion t, g e :=
      Finset.sum_nonneg fun e he => hg a (Finset.mem_insert_self a s) e (Finset.mem_inter.1 he).1
    linarith

open scoped Classical in
/-- **the helper relay of w**, as a plan for V2-FLOOR: the distinct images (ι tail, ι head) of all
helper MOVEs (chains deduplicated, sharing free). ι = chart ↦ its span in F₂⁹. -/
noncomputable def relayE (ι : C → Sub) (H : Finset Reg) (ini : Reg → Option C) (w : List (GEv K Reg C)) :
    Finset (Sub × Sub) :=
  H.biUnion fun h =>
    (((moves (s0 ini) w).filter fun m => m.reg = h).map fun m => (ι m.tail, ι m.head)).toFinset

lemma fdim_le9 (X : Sub) : fdim X ≤ 9 := by
  have := Submodule.finrank_le X
  simpa [fdim, Module.finrank_fin_fun] using this

/-- relay edges strictly ascend. -/
theorem relayE_lt (ι : C → Sub) (hι : ∀ a b : C, a < b → ι a < ι b) (hA : Accepted Pub H ini w) :
    ∀ e ∈ relayE ι H ini w, e.1 < e.2 := by
  classical
  intro e he
  simp only [relayE, Finset.mem_biUnion, List.mem_toFinset, List.mem_map, List.mem_filter] at he
  obtain ⟨h, hh, m, ⟨hm, hmr⟩, rfl⟩ := he
  have hmr' : m.reg = h := by simpa using hmr
  exact hι _ _ ((moves_facts Pub (s0 ini) w hA.legal m hm).2.1 (hmr' ▸ hA.helpers_pub hh))

open scoped Classical in
/-- **BRIDGE** (every accepted word, any θ ∈ [0,1]): JB_θ of the helper relay ≤ helper D0 + Σ_h corr. -/
theorem bridge (θ : ℝ) (h0 : 0 ≤ θ) (h1 : θ ≤ 1) (dim : C → ℕ) (ι : C → Sub)
    (hι : ∀ a b : C, a < b → ι a < ι b) (hιd : ∀ c, fdim (ι c) = dim c) (hA : Accepted Pub H ini w) :
    ∑ e ∈ relayE ι H ini w, wcut θ (fdim e.1) (fdim e.2) ≤
      helperD0 JunkLB2.fL dim H ini w + ∑ h ∈ H, hcorr θ dim ini w h := by
  have hdim : ∀ a b : C, a < b → dim a < dim b := fun a b hab => by
    rw [← hιd a, ← hιd b]; exact Submodule.finrank_lt_finrank_of_lt (hι a b hab)
  have hd9 : ∀ c, dim c ≤ 9 := fun c => hιd c ▸ fdim_le9 (ι c)
  -- nonnegativity of every helper move's price
  have hnn : ∀ h ∈ H, ∀ m ∈ (moves (s0 ini) w).filter (fun m => m.reg = h),
      0 ≤ wcut θ (fdim (ι m.tail, ι m.head).1) (fdim (ι m.tail, ι m.head).2) := by
    intro h hh m hm
    obtain ⟨hm, hmr⟩ := List.mem_filter.1 hm
    have hmr' : m.reg = h := by simpa using hmr
    have hlt := hdim _ _ ((moves_facts Pub (s0 ini) w hA.legal m hm).2.1 (hmr' ▸ hA.helpers_pub hh))
    simp only [hιd]
    exact wcut_nonneg θ h0 h1 hlt (hd9 _)
  have step1 := sum_biUnion_le' (fun e : Sub × Sub => wcut θ (fdim e.1) (fdim e.2))
    (fun h => (((moves (s0 ini) w).filter fun m => m.reg = h).map fun m => (ι m.tail, ι m.head)).toFinset) H
    (by
      intro h hh e he
      simp only [List.mem_toFinset, List.mem_map] at he
      obtain ⟨m, hm, rfl⟩ := he
      exact hnn h hh m hm)
  have step2 : ∀ h ∈ H,
      ∑ e ∈ (((moves (s0 ini) w).filter fun m => m.reg = h).map fun m => (ι m.tail, ι m.head)).toFinset,
        wcut θ (fdim e.1) (fdim e.2) ≤ regD0 JunkLB2.fL dim ini w h + hcorr θ dim ini w h := by
    intro h hh
    refine le_trans (sum_toFinset_le (fun m : Mv K Reg C => (ι m.tail, ι m.head))
      (fun e : Sub × Sub => wcut θ (fdim e.1) (fdim e.2)) _ (hnn h hh)) ?_
    have := helper_bound θ h0 h1 dim hdim hd9 hA h hh
    simpa only [hιd] using this
  calc ∑ e ∈ relayE ι H ini w, wcut θ (fdim e.1) (fdim e.2)
      ≤ ∑ h ∈ H, ∑ e ∈ (((moves (s0 ini) w).filter fun m => m.reg = h).map
          fun m => (ι m.tail, ι m.head)).toFinset, wcut θ (fdim e.1) (fdim e.2) := step1
    _ ≤ ∑ h ∈ H, (regD0 JunkLB2.fL dim ini w h + hcorr θ dim ini w h) := Finset.sum_le_sum step2
    _ = _ := by rw [Finset.sum_add_distrib]; rfl

/-- **BRIDGE, {0}→V helpers**: if every helper is born at dim 0 and ends at dim 9 (the JB model's chains),
JB_θ(relay) ≤ helper D0, for every θ ∈ [0,1]. -/
theorem bridge_0V (θ : ℝ) (h0 : 0 ≤ θ) (h1 : θ ≤ 1) (dim : C → ℕ) (ι : C → Sub)
    (hι : ∀ a b : C, a < b → ι a < ι b) (hιd : ∀ c, fdim (ι c) = dim c) (hA : Accepted Pub H ini w)
    (h0V : ∀ h ∈ H, natLoc dim (ini h) = 0 ∧ natLoc dim ((grun (s0 ini) w).loc h) = 9) :
    ∑ e ∈ relayE ι H ini w, wcut θ (fdim e.1) (fdim e.2) ≤ helperD0 JunkLB2.fL dim H ini w := by
  have hb := bridge θ h0 h1 dim ι hι hιd hA
  have hz : ∑ h ∈ H, hcorr θ dim ini w h = 0 :=
    Finset.sum_eq_zero fun h hh => by
      simp only [hcorr, (h0V h hh).1, (h0V h hh).2, corr_0V]
  linarith

/-- **BRIDGE, β (θ = 1), helpers ending at V**: JB_β(relay) ≤ helper D0 + B1 · #(helpers born at a line).
(No condition on where helpers are born; the only debt is JB's line term B1 for line-born helpers.) -/
theorem bridge_beta_V (dim : C → ℕ) (ι : C → Sub)
    (hι : ∀ a b : C, a < b → ι a < ι b) (hιd : ∀ c, fdim (ι c) = dim c) (hA : Accepted Pub H ini w)
    (hV : ∀ h ∈ H, natLoc dim ((grun (s0 ini) w).loc h) = 9) :
    ∑ e ∈ relayE ι H ini w, wcut 1 (fdim e.1) (fdim e.2) ≤
      helperD0 JunkLB2.fL dim H ini w + B1 * (H.filter fun h => natLoc dim (ini h) = 1).card := by
  have hb := bridge 1 zero_le_one le_rfl dim ι hι hιd hA
  have hz : ∑ h ∈ H, hcorr 1 dim ini w h = B1 * (H.filter fun h => natLoc dim (ini h) = 1).card := by
    rw [Finset.card_eq_sum_ones, Nat.cast_sum, Finset.mul_sum, Finset.sum_filter]
    refine Finset.sum_congr rfl fun h hh => ?_
    simp only [hcorr, hV h hh, corr_beta_V]
    split_ifs <;> simp
  linarith

end Word

end V2Bridge

#print axioms V2Bridge.move_dom
#print axioms V2Bridge.chD0_bound
#print axioms V2Bridge.helper_bound
#print axioms V2Bridge.bridge
#print axioms V2Bridge.bridge_0V
#print axioms V2Bridge.bridge_beta_V
