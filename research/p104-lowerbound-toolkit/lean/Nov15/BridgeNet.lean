/-
BridgeNet (lane BRIDGE, Nov 20).  THE WORD -> NETWORK BRIDGE (YCARRIER YC.md sec 1, formalised), kernel only.
Model hypotheses used: NONE beyond the word model itself (WordModelDefs.Word / Reach / Step) and the two verifier
clauses ChartsSubsp (independent.py l.26-31 frames are spans) and OwnedNested (l.51).  No Wall56, no rank-8 facts.

Part 1 (this section, generic in the register type R, the publicity flag pb and the port map ix : Pt -> R):
every reachable state carries a NETWORK  (nodes ℕ-indexed, n of them)
  * node k : charts a_k, b_k (Finset ℕ), direct gather row F_k (port coordinates), relay row H_k, content val_k;
  * DAG:  H k j != 0 -> j < k;  relay rule  H k j != 0 -> b_j ⊆ a_k;
  * gather rule: F k p != 0 -> the port register ix p was BORN at a chart c' ⊆ a_k;
  * val_k = F_k + Σ_{j<k} H k j val_j;
  * owned register r sitting at c: its row restricted to the ports = val of its current node, whose b-chart is c;
  * public register r sitting at c: row restricted to ports = pi_r + Σ_j g r j val_j with pi_r supported on ports
    born inside c, and g r j != 0 -> b_j ⊆ c ("deposit rule");
  * each node is either flat (a = b) or the chart pair (src, dst) of an owned MOVE with src ⊄ dst;
  * Σ_k (dim a_k - dim b_k) = ownDrop s = Σ over owned MOVEs of (dim src - dim dst)  (truncated; = owned descent).
Nodes: one per owned birth (flat), per owned gate (flat), per owned MOVE c -> d (a = d, b = d if c ⊆ d, else a = c,
b = d).  Public registers are wires, not nodes (YC sec 1).
-/
import Nov15.LevelCutDX
import Nov15.WordModelR3
import Mathlib.FieldTheory.Finiteness

set_option linter.unusedSectionVars false
set_option maxHeartbeats 0

namespace BridgeNet
open Finset Module WordModel SafeRungsClique

section Generic
variable {R Pt : Type} [Fintype R] [DecidableEq R] [Fintype Pt] [DecidableEq Pt]

/-- network data carried along a run. -/
structure ND (R Pt : Type) where
  n : ℕ
  a : ℕ → Ch
  b : ℕ → Ch
  F : ℕ → Pt → ℚ
  H : ℕ → ℕ → ℚ
  val : ℕ → Pt → ℚ
  cur : R → ℕ
  pi : R → Pt → ℚ
  g : R → ℕ → ℚ

/-- restriction of a row to the port coordinates. -/
def xp (ix : Pt → R) (v : R → ℚ) : Pt → ℚ := fun p => v (ix p)

/-- owned descent: Σ over owned MOVEs (src, dst) of (dim src - dim dst), truncated (ascents count 0). -/
def ownDrop (s : St R) : ℕ := (s.olog.map fun m => dim m.1 - dim m.2.1).sum

/-- network fields. -/
structure InvN (ix : Pt → R) (s : St R) (N : ND R Pt) : Prop where
  hHlt : ∀ k j, N.H k j ≠ 0 → j < k
  hHn : ∀ k j, N.H k j ≠ 0 → k < N.n
  hrel : ∀ k j, N.H k j ≠ 0 → N.b j ⊆ N.a k
  hF : ∀ k p, N.F k p ≠ 0 → ∃ c', c' ⊆ N.a k ∧ ix p ∈ s.B c'
  hval : ∀ k < N.n, N.val k = N.F k + ∑ j ∈ range k, N.H k j • N.val j
  hkind : ∀ k < N.n, N.a k = N.b k ∨ ∃ m ∈ s.olog, N.a k = m.1 ∧ N.b k = m.2.1 ∧ ¬ m.1 ⊆ m.2.1
  hdrop : ∑ k ∈ range N.n, (dim (N.a k) - dim (N.b k)) = ownDrop s

/-- register fields. -/
structure InvR (pb : R → Bool) (ix : Pt → R) (s : St R) (N : ND R Pt) : Prop where
  hown : ∀ r c, pb r = false → s.loc r = .sit c →
    N.cur r < N.n ∧ N.b (N.cur r) = c ∧ xp ix (s.row r) = N.val (N.cur r)
  hpi : ∀ r c, pb r = true → s.loc r = .sit c → ∀ p, N.pi r p ≠ 0 → ∃ c', c' ⊆ c ∧ ix p ∈ s.B c'
  hg : ∀ r c, pb r = true → s.loc r = .sit c → ∀ j, N.g r j ≠ 0 → j < N.n ∧ N.b j ⊆ c
  hrow : ∀ r c, pb r = true → s.loc r = .sit c →
    xp ix (s.row r) = N.pi r + ∑ j ∈ range N.n, N.g r j • N.val j

structure Inv (pb : R → Bool) (ix : Pt → R) (s : St R) (N : ND R Pt) : Prop where
  net : InvN ix s N
  reg : InvR pb ix s N

/-! ### pushing one node -/

def ND.push (N : ND R Pt) (a b : Ch) (F : Pt → ℚ) (H : ℕ → ℚ) (v : Pt → ℚ) (cur : R → ℕ) : ND R Pt :=
  { n := N.n + 1, a := Function.update N.a N.n a, b := Function.update N.b N.n b,
    F := Function.update N.F N.n F, H := Function.update N.H N.n H, val := Function.update N.val N.n v,
    cur := cur, pi := N.pi, g := N.g }

theorem dim_mono {c d : Ch} (h : c ⊆ d) : dim c ≤ dim d :=
  Nat.log_mono_right (Finset.card_le_card h)

theorem push_net {ix : Pt → R} {s s' : St R} {N : ND R Pt} (hN : InvN ix s N)
    (hB : ∀ c, s.B c ⊆ s'.B c) (hol : ∀ m ∈ s.olog, m ∈ s'.olog)
    (a b : Ch) (F : Pt → ℚ) (H : ℕ → ℚ) (v : Pt → ℚ) (cur : R → ℕ)
    (hH : ∀ j, H j ≠ 0 → j < N.n ∧ N.b j ⊆ a)
    (hFc : ∀ p, F p ≠ 0 → ∃ c', c' ⊆ a ∧ ix p ∈ s'.B c')
    (hv : v = F + ∑ j ∈ range N.n, H j • N.val j)
    (hk : a = b ∨ ∃ m ∈ s'.olog, a = m.1 ∧ b = m.2.1 ∧ ¬ m.1 ⊆ m.2.1)
    (hd : ownDrop s' = ownDrop s + (dim a - dim b)) :
    InvN ix s' (N.push a b F H v cur) where
  hHlt := by
    intro k j h
    simp only [ND.push] at h
    by_cases hk : k = N.n
    · subst hk; rw [Function.update_self] at h; exact (hH j h).1
    · rw [Function.update_of_ne hk] at h; exact hN.hHlt k j h
  hHn := by
    intro k j h
    simp only [ND.push] at h ⊢
    by_cases hk : k = N.n
    · omega
    · rw [Function.update_of_ne hk] at h; have := hN.hHn k j h; omega
  hrel := by
    intro k j h
    simp only [ND.push] at h ⊢
    by_cases hk : k = N.n
    · subst hk; rw [Function.update_self] at h
      obtain ⟨hj, hb⟩ := hH j h
      rw [Function.update_self, Function.update_of_ne (Nat.ne_of_lt hj)]; exact hb
    · rw [Function.update_of_ne hk] at h
      have hkn := hN.hHn k j h
      have hjk := hN.hHlt k j h
      rw [Function.update_of_ne hk, Function.update_of_ne (by omega)]; exact hN.hrel k j h
  hF := by
    intro k p h
    simp only [ND.push] at h ⊢
    by_cases hk : k = N.n
    · subst hk; rw [Function.update_self] at h; rw [Function.update_self]; exact hFc p h
    · rw [Function.update_of_ne hk] at h; rw [Function.update_of_ne hk]
      obtain ⟨c', h1, h2⟩ := hN.hF k p h
      exact ⟨c', h1, hB c' h2⟩
  hval := by
    intro k hk
    simp only [ND.push] at hk ⊢
    by_cases hkn : k = N.n
    · subst hkn
      rw [Function.update_self, Function.update_self, Function.update_self, hv]
      congr 1
      refine Finset.sum_congr rfl fun j hj => ?_
      rw [Function.update_of_ne (Nat.ne_of_lt (Finset.mem_range.1 hj))]
    · have hk' : k < N.n := by omega
      rw [Function.update_of_ne hkn, Function.update_of_ne hkn, hN.hval k hk']
      congr 1
      refine Finset.sum_congr rfl fun j hj => ?_
      have hjk := Finset.mem_range.1 hj
      rw [Function.update_of_ne hkn, Function.update_of_ne (by omega)]
  hkind := by
    intro k hk2
    simp only [ND.push] at hk2 ⊢
    by_cases hkn : k = N.n
    · subst hkn; rw [Function.update_self, Function.update_self]; exact hk
    · rw [Function.update_of_ne hkn, Function.update_of_ne hkn]
      rcases hN.hkind k (by omega) with h | ⟨m, hm, h1, h2, h3⟩
      · exact Or.inl h
      · exact Or.inr ⟨m, hol m hm, h1, h2, h3⟩
  hdrop := by
    simp only [ND.push]
    rw [Finset.sum_range_succ, Function.update_self, Function.update_self, hd, ← hN.hdrop]
    congr 1
    refine Finset.sum_congr rfl fun k hk => ?_
    have := Finset.mem_range.1 hk
    rw [Function.update_of_ne (Nat.ne_of_lt this), Function.update_of_ne (Nat.ne_of_lt this)]

theorem same_net {ix : Pt → R} {s s' : St R} {N : ND R Pt} (hN : InvN ix s N)
    (hB : ∀ c, s.B c ⊆ s'.B c) (hol : s'.olog = s.olog) (cur : R → ℕ) (pi : R → Pt → ℚ) (g : R → ℕ → ℚ) :
    InvN ix s' { N with cur := cur, pi := pi, g := g } where
  hHlt := hN.hHlt
  hHn := hN.hHn
  hrel := hN.hrel
  hF := fun k p h => by
    obtain ⟨c', h1, h2⟩ := hN.hF k p h
    exact ⟨c', h1, hB c' h2⟩
  hval := hN.hval
  hkind := by
    intro k hk; rw [hol]; exact hN.hkind k hk
  hdrop := by
    have : ownDrop s' = ownDrop s := by unfold ownDrop; rw [hol]
    rw [this]; exact hN.hdrop

/-- old public sums survive a push. -/
theorem sum_push (N : ND R Pt) (gr : ℕ → ℚ) (hg : ∀ j, gr j ≠ 0 → j < N.n) (v : Pt → ℚ) :
    ∑ j ∈ range (N.n + 1), gr j • Function.update N.val N.n v j = ∑ j ∈ range N.n, gr j • N.val j := by
  rw [Finset.sum_range_succ]
  have h0 : gr N.n = 0 := by
    by_contra h; exact absurd (hg _ h) (lt_irrefl _)
  rw [h0, zero_smul, add_zero]
  refine Finset.sum_congr rfl fun j hj => ?_
  rw [Function.update_of_ne (Nat.ne_of_lt (Finset.mem_range.1 hj))]

/-! ### the gate combination -/

/-- direct part of a gate combination over the registers S. -/
def gF (pb : R → Bool) (N : ND R Pt) (S : Finset R) (coef : R → ℚ) : Pt → ℚ :=
  ∑ t ∈ S.filter (fun t => pb t = true), coef t • N.pi t

/-- relay part of a gate combination over the registers S. -/
def gH (pb : R → Bool) (N : ND R Pt) (S : Finset R) (coef : R → ℚ) : ℕ → ℚ := fun j =>
  ∑ t ∈ S.filter (fun t => pb t = false), coef t * (if j = N.cur t then 1 else 0) +
  ∑ t ∈ S.filter (fun t => pb t = true), coef t * N.g t j

theorem filter_not_true (pb : R → Bool) (S : Finset R) :
    S.filter (fun t => ¬ pb t = true) = S.filter (fun t => pb t = false) :=
  Finset.filter_congr fun t _ => by simp

theorem gate_row {pb : R → Bool} {ix : Pt → R} {s : St R} {N : ND R Pt} (hI : InvR pb ix s N)
    (c : Ch) (coef : R → ℚ) :
    xp ix (∑ t ∈ univ.filter (fun t => s.loc t = .sit c), coef t • s.row t)
      = gF pb N (univ.filter (fun t => s.loc t = .sit c)) coef
        + ∑ j ∈ range N.n, gH pb N (univ.filter (fun t => s.loc t = .sit c)) coef j • N.val j := by
  set S := univ.filter (fun t => s.loc t = .sit c) with hSdef
  have hS : ∀ t ∈ S, s.loc t = .sit c := fun t ht => (Finset.mem_filter.1 ht).2
  funext p
  simp only [xp, Finset.sum_apply, Pi.smul_apply, smul_eq_mul, Pi.add_apply, gF, gH]
  rw [← Finset.sum_filter_add_sum_filter_not S (fun t => pb t = true), filter_not_true]
  have hown : ∀ t ∈ S.filter (fun t => pb t = false),
      coef t * s.row t (ix p) = ∑ j ∈ range N.n, coef t * (if j = N.cur t then 1 else 0) * N.val j p := by
    intro t ht
    obtain ⟨htS, hpb⟩ := Finset.mem_filter.1 ht
    obtain ⟨hlt, _, hrow⟩ := hI.hown t c hpb (hS t htS)
    have := congrFun hrow p
    simp only [xp] at this
    rw [this]
    simp only [mul_ite, mul_one, mul_zero, ite_mul, zero_mul, Finset.sum_ite_eq', Finset.mem_range, hlt, if_true]
  have hpub : ∀ t ∈ S.filter (fun t => pb t = true),
      coef t * s.row t (ix p) = coef t * N.pi t p + ∑ j ∈ range N.n, coef t * N.g t j * N.val j p := by
    intro t ht
    obtain ⟨htS, hpb⟩ := Finset.mem_filter.1 ht
    have := congrFun (hI.hrow t c hpb (hS t htS)) p
    simp only [xp, Pi.add_apply, Finset.sum_apply, Pi.smul_apply, smul_eq_mul] at this
    rw [this, mul_add, Finset.mul_sum]
    refine congrArg _ (Finset.sum_congr rfl fun j _ => by ring)
  rw [Finset.sum_congr rfl hown, Finset.sum_congr rfl hpub, Finset.sum_add_distrib]
  simp only [add_mul, Finset.sum_add_distrib, Finset.sum_mul]
  rw [Finset.sum_comm (s := range N.n) (t := S.filter (fun t => pb t = false)),
    Finset.sum_comm (s := range N.n) (t := S.filter (fun t => pb t = true))]
  ring

theorem gH_cond {pb : R → Bool} {ix : Pt → R} {s : St R} {N : ND R Pt} (hI : InvR pb ix s N)
    (c : Ch) (coef : R → ℚ) :
    ∀ j, gH pb N (univ.filter (fun t => s.loc t = .sit c)) coef j ≠ 0 → j < N.n ∧ N.b j ⊆ c := by
  intro j h
  simp only [gH] at h
  rcases (by
      by_contra hc; push Not at hc; rw [hc.1, hc.2, add_zero] at h; exact h rfl :
      (∑ t ∈ (univ.filter (fun t => s.loc t = .sit c)).filter (fun t => pb t = false),
          coef t * (if j = N.cur t then 1 else 0)) ≠ 0 ∨
      (∑ t ∈ (univ.filter (fun t => s.loc t = .sit c)).filter (fun t => pb t = true), coef t * N.g t j) ≠ 0)
    with h1 | h2
  · obtain ⟨t, ht, hne⟩ := Finset.exists_ne_zero_of_sum_ne_zero h1
    simp only [Finset.mem_filter, Finset.mem_univ, true_and] at ht
    have hj : j = N.cur t := by by_contra hj; simp [hj] at hne
    obtain ⟨hlt, hb, _⟩ := hI.hown t c ht.2 ht.1
    subst hj; exact ⟨hlt, hb.le⟩
  · obtain ⟨t, ht, hne⟩ := Finset.exists_ne_zero_of_sum_ne_zero h2
    simp only [Finset.mem_filter, Finset.mem_univ, true_and] at ht
    exact hI.hg t c ht.2 ht.1 j (right_ne_zero_of_mul hne)

theorem gF_cond {pb : R → Bool} {ix : Pt → R} {s : St R} {N : ND R Pt} (hI : InvR pb ix s N)
    (c : Ch) (coef : R → ℚ) :
    ∀ p, gF pb N (univ.filter (fun t => s.loc t = .sit c)) coef p ≠ 0 → ∃ c', c' ⊆ c ∧ ix p ∈ s.B c' := by
  intro p h
  simp only [gF, Finset.sum_apply, Pi.smul_apply, smul_eq_mul] at h
  obtain ⟨t, ht, hne⟩ := Finset.exists_ne_zero_of_sum_ne_zero h
  simp only [Finset.mem_filter, Finset.mem_univ, true_and] at ht
  exact hI.hpi t c ht.2 ht.1 p (right_ne_zero_of_mul hne)

/-! ### register helpers -/

theorem pub_push_pi {pb : R → Bool} {ix : Pt → R} {s s' : St R} {N : ND R Pt} (hI : InvR pb ix s N)
    (a b : Ch) (F : Pt → ℚ) (H : ℕ → ℚ) (v : Pt → ℚ) (cur : R → ℕ)
    (r : R) (c : Ch) (hpb : pb r = true) (hloc : s.loc r = .sit c) (hB : ∀ c, s.B c ⊆ s'.B c) :
    ∀ p, (N.push a b F H v cur).pi r p ≠ 0 → ∃ c', c' ⊆ c ∧ ix p ∈ s'.B c' := fun p hp => by
  obtain ⟨c', h1, h2⟩ := hI.hpi r c hpb hloc p hp
  exact ⟨c', h1, hB c' h2⟩

theorem pub_push_g {pb : R → Bool} {ix : Pt → R} {s : St R} {N : ND R Pt} (hI : InvR pb ix s N)
    (a b : Ch) (F : Pt → ℚ) (H : ℕ → ℚ) (v : Pt → ℚ) (cur : R → ℕ)
    (r : R) (c : Ch) (hpb : pb r = true) (hloc : s.loc r = .sit c) :
    ∀ j, (N.push a b F H v cur).g r j ≠ 0 → j < (N.push a b F H v cur).n ∧ (N.push a b F H v cur).b j ⊆ c :=
  fun j hj => by
  obtain ⟨h1, h2⟩ := hI.hg r c hpb hloc j hj
  simp only [ND.push]
  exact ⟨by omega, by rw [Function.update_of_ne (Nat.ne_of_lt h1)]; exact h2⟩

theorem pub_push_row {pb : R → Bool} {ix : Pt → R} {s s' : St R} {N : ND R Pt} (hI : InvR pb ix s N)
    (a b : Ch) (F : Pt → ℚ) (H : ℕ → ℚ) (v : Pt → ℚ) (cur : R → ℕ)
    (r : R) (c : Ch) (hpb : pb r = true) (hloc : s.loc r = .sit c) (hrow : s'.row r = s.row r) :
    xp ix (s'.row r) = (N.push a b F H v cur).pi r +
      ∑ j ∈ range (N.push a b F H v cur).n, (N.push a b F H v cur).g r j • (N.push a b F H v cur).val j := by
  simp only [ND.push]
  rw [hrow, sum_push N (N.g r) (fun j hj => (hI.hg r c hpb hloc j hj).1) v]
  exact hI.hrow r c hpb hloc

theorem own_push {pb : R → Bool} {ix : Pt → R} {s s' : St R} {N : ND R Pt} (hI : InvR pb ix s N)
    (a b : Ch) (F : Pt → ℚ) (H : ℕ → ℚ) (v : Pt → ℚ) (cur : R → ℕ)
    (r : R) (c : Ch) (hpb : pb r = false) (hloc : s.loc r = .sit c)
    (hcur : cur r = N.cur r) (hrow : s'.row r = s.row r) :
    (N.push a b F H v cur).cur r < (N.push a b F H v cur).n ∧
    (N.push a b F H v cur).b ((N.push a b F H v cur).cur r) = c ∧
    xp ix (s'.row r) = (N.push a b F H v cur).val ((N.push a b F H v cur).cur r) := by
  obtain ⟨h1, h2, h3⟩ := hI.hown r c hpb hloc
  simp only [ND.push]
  rw [hcur, hrow, Function.update_of_ne (Nat.ne_of_lt h1), Function.update_of_ne (Nat.ne_of_lt h1)]
  exact ⟨by omega, h2, h3⟩

theorem B_ins (B : Ch → Finset R) (c : Ch) (r : R) : ∀ c', B c' ⊆ Function.update B c (insert r (B c)) c' := by
  intro c'
  by_cases h : c' = c
  · subst h; rw [Function.update_self]; exact Finset.subset_insert _ _
  · rw [Function.update_of_ne h]

theorem ne_of_pb {pb : R → Bool} {r r' : R} (h1 : pb r = true) (h2 : pb r' = false) : r' ≠ r := by
  rintro rfl; rw [h1] at h2; exact Bool.noConfusion h2

theorem ne_of_pb' {pb : R → Bool} {r r' : R} (h1 : pb r = false) (h2 : pb r' = true) : r' ≠ r := by
  rintro rfl; rw [h1] at h2; exact Bool.noConfusion h2

/-! ### one step -/

theorem step_inv {pb : R → Bool} {ix : Pt → R} {s s' : St R} {N : ND R Pt} (hst : Step pb s s')
    (hI : Inv pb ix s N) : ∃ N' : ND R Pt, Inv pb ix s' N' := by
  cases hst with
  | birthPub r c h1 h2 =>
    refine ⟨{ N with
        cur := N.cur
        pi := Function.update N.pi r (fun p => if ix p = r then 1 else 0)
        g := Function.update N.g r 0 }, ⟨same_net hI.net ?_ ?_ _ _ _, ?_⟩⟩
    · exact B_ins s.B c r
    · rfl
    constructor
    · intro r' c' hpb hloc
      have hne := ne_of_pb h2 hpb
      simp only [Function.update_of_ne hne] at hloc ⊢
      exact hI.reg.hown r' c' hpb hloc
    · intro r' c' hpb hloc p hp
      by_cases hr : r' = r
      · subst hr
        simp only [Function.update_self, Loc.sit.injEq] at hloc hp
        subst hloc
        have : ix p = r' := by by_contra h; simp [h] at hp
        exact ⟨c, subset_refl _, by
          show ix p ∈ Function.update s.B c (insert r' (s.B c)) c
          rw [Function.update_self, this]; exact Finset.mem_insert_self _ _⟩
      · simp only [Function.update_of_ne hr] at hloc hp
        obtain ⟨c'', h1', h2'⟩ := hI.reg.hpi r' c' hpb hloc p hp
        exact ⟨c'', h1', B_ins s.B c r c'' h2'⟩
    · intro r' c' hpb hloc j hj
      by_cases hr : r' = r
      · subst hr; simp at hj
      · simp only [Function.update_of_ne hr] at hloc hj
        exact hI.reg.hg r' c' hpb hloc j hj
    · intro r' c' hpb hloc
      by_cases hr : r' = r
      · subst hr
        simp only [Function.update_self]
        funext p
        simp [xp, Pi.single_apply]
      · simp only [Function.update_of_ne hr] at hloc ⊢
        exact hI.reg.hrow r' c' hpb hloc
  | birthOwn r c h1 h2 =>
    refine ⟨N.push c c 0 0 0 (Function.update N.cur r N.n),
      ⟨push_net hI.net ?_ ?_ c c 0 0 0 _ (fun j h => absurd rfl h) ?_ (by simp) ?_ ?_, ?_⟩⟩
    · exact fun _ => subset_refl _
    · exact fun _ hm => hm
    · exact fun p h => absurd rfl h
    · exact Or.inl rfl
    · simp [ownDrop]
    constructor
    · intro r' c' hpb hloc
      by_cases hr : r' = r
      · subst hr
        simp only [Function.update_self, Loc.sit.injEq] at hloc
        subst hloc
        simp only [ND.push, Function.update_self]
        refine ⟨by omega, by simp, ?_⟩
        funext p; simp [xp]
      · simp only [Function.update_of_ne hr] at hloc
        refine own_push hI.reg c c 0 0 0 _ r' c' hpb hloc (Function.update_of_ne hr _ _) ?_
        exact Function.update_of_ne hr _ _
    · intro r' c' hpb hloc
      have hne := ne_of_pb' h2 hpb
      simp only [Function.update_of_ne hne] at hloc
      exact pub_push_pi hI.reg c c 0 0 0 _ r' c' hpb hloc (fun _ => subset_refl _)
    · intro r' c' hpb hloc
      have hne := ne_of_pb' h2 hpb
      simp only [Function.update_of_ne hne] at hloc
      exact pub_push_g hI.reg c c 0 0 0 _ r' c' hpb hloc
    · intro r' c' hpb hloc
      have hne := ne_of_pb' h2 hpb
      simp only [Function.update_of_ne hne] at hloc
      refine pub_push_row hI.reg c c 0 0 0 _ r' c' hpb hloc ?_
      exact Function.update_of_ne hne _ _
  | gate r c coef h1 =>
    by_cases hpbr : pb r = true
    · refine ⟨{ N with
            cur := N.cur
            pi := Function.update N.pi r (gF pb N (univ.filter (fun t => s.loc t = .sit c)) coef)
            g := Function.update N.g r (gH pb N (univ.filter (fun t => s.loc t = .sit c)) coef) },
        ⟨same_net hI.net ?_ ?_ _ _ _, ?_⟩⟩
      · exact fun _ => subset_refl _
      · rfl
      constructor
      · intro r' c' hpb hloc
        have hne := ne_of_pb hpbr hpb
        simp only [Function.update_of_ne hne]
        exact hI.reg.hown r' c' hpb hloc
      · intro r' c' hpb hloc p hp
        by_cases hr : r' = r
        · subst hr
          have hcc : c' = c := by rw [h1] at hloc; exact (Loc.sit.inj hloc).symm
          subst hcc
          simp only [Function.update_self] at hp
          exact gF_cond hI.reg c' coef p hp
        · simp only [Function.update_of_ne hr] at hp
          exact hI.reg.hpi r' c' hpb hloc p hp
      · intro r' c' hpb hloc j hj
        by_cases hr : r' = r
        · subst hr
          have hcc : c' = c := by rw [h1] at hloc; exact (Loc.sit.inj hloc).symm
          subst hcc
          simp only [Function.update_self] at hj
          exact gH_cond hI.reg c' coef j hj
        · simp only [Function.update_of_ne hr] at hj
          exact hI.reg.hg r' c' hpb hloc j hj
      · intro r' c' hpb hloc
        by_cases hr : r' = r
        · subst hr
          have hcc : c' = c := by rw [h1] at hloc; exact (Loc.sit.inj hloc).symm
          subst hcc
          simp only [Function.update_self]
          exact gate_row hI.reg c' coef
        · simp only [Function.update_of_ne hr]
          exact hI.reg.hrow r' c' hpb hloc
    · have hpbf : pb r = false := by simpa using hpbr
      refine ⟨N.push c c (gF pb N (univ.filter (fun t => s.loc t = .sit c)) coef)
          (gH pb N (univ.filter (fun t => s.loc t = .sit c)) coef)
          (xp ix (∑ t ∈ univ.filter (fun t => s.loc t = .sit c), coef t • s.row t))
          (Function.update N.cur r N.n),
        ⟨push_net hI.net ?_ ?_ c c _ _ _ _ (gH_cond hI.reg c coef) ?_ (gate_row hI.reg c coef) ?_ ?_, ?_⟩⟩
      · exact fun _ => subset_refl _
      · exact fun _ hm => hm
      · exact gF_cond hI.reg c coef
      · exact Or.inl rfl
      · simp [ownDrop]
      constructor
      · intro r' c' hpb hloc
        by_cases hr : r' = r
        · subst hr
          have hcc : c' = c := by rw [h1] at hloc; exact (Loc.sit.inj hloc).symm
          subst hcc
          simp only [ND.push, Function.update_self]
          exact ⟨by omega, by simp, by simp⟩
        · refine own_push hI.reg c c _ _ _ _ r' c' hpb hloc (Function.update_of_ne hr _ _) ?_
          exact Function.update_of_ne hr _ _
      · intro r' c' hpb hloc
        exact pub_push_pi hI.reg c c _ _ _ _ r' c' hpb hloc (fun _ => subset_refl _)
      · intro r' c' hpb hloc
        exact pub_push_g hI.reg c c _ _ _ _ r' c' hpb hloc
      · intro r' c' hpb hloc
        have hne := ne_of_pb' hpbf hpb
        refine pub_push_row hI.reg c c _ _ _ _ r' c' hpb hloc ?_
        exact Function.update_of_ne hne _ _
  | movePub r c d h1 h2 h3 =>
    refine ⟨{ N with cur := N.cur }, ⟨same_net hI.net ?_ ?_ N.cur N.pi N.g, ?_⟩⟩
    · exact fun _ => subset_refl _
    · rfl
    constructor
    · intro r' c' hpb hloc
      have hne := ne_of_pb h2 hpb
      simp only [Function.update_of_ne hne] at hloc
      exact hI.reg.hown r' c' hpb hloc
    · intro r' c' hpb hloc p hp
      by_cases hr : r' = r
      · subst hr
        simp only [Function.update_self, Loc.sit.injEq] at hloc
        subst hloc
        obtain ⟨c'', ha, hb⟩ := hI.reg.hpi r' c hpb h1 p hp
        exact ⟨c'', subset_trans ha (le_of_lt h3), hb⟩
      · simp only [Function.update_of_ne hr] at hloc
        exact hI.reg.hpi r' c' hpb hloc p hp
    · intro r' c' hpb hloc j hj
      by_cases hr : r' = r
      · subst hr
        simp only [Function.update_self, Loc.sit.injEq] at hloc
        subst hloc
        obtain ⟨ha, hb⟩ := hI.reg.hg r' c hpb h1 j hj
        exact ⟨ha, subset_trans hb (le_of_lt h3)⟩
      · simp only [Function.update_of_ne hr] at hloc
        exact hI.reg.hg r' c' hpb hloc j hj
    · intro r' c' hpb hloc
      by_cases hr : r' = r
      · subst hr
        exact hI.reg.hrow r' c hpb h1
      · simp only [Function.update_of_ne hr] at hloc
        exact hI.reg.hrow r' c' hpb hloc
  | moveOwn r c d h1 h2 =>
    obtain ⟨hlt, hbc, hrw⟩ := hI.reg.hown r c h2 h1
    have hca : c ⊆ (if c ⊆ d then d else c) := by split_ifs with h <;> [exact h; exact subset_refl _]
    refine ⟨N.push (if c ⊆ d then d else c) d 0 (fun j => if j = N.cur r then 1 else 0) (N.val (N.cur r))
        (Function.update N.cur r N.n),
      ⟨push_net hI.net ?_ ?_ _ d 0 _ _ _ ?_ ?_ ?_ ?_ ?_, ?_⟩⟩
    · exact fun _ => subset_refl _
    · exact fun _ hm => List.mem_cons_of_mem _ hm
    · intro j hj
      have : j = N.cur r := by by_contra h; simp [h] at hj
      subst this; exact ⟨hlt, hbc ▸ hca⟩
    · exact fun p h => absurd rfl h
    · funext p
      simp [Finset.sum_apply, ite_smul, Finset.sum_ite_eq', hlt]
    · by_cases hcd : c ⊆ d
      · exact Or.inl (by simp [hcd])
      · exact Or.inr ⟨(c, d, s.row r), List.mem_cons_self, by simp [hcd], rfl, hcd⟩
    · show ownDrop ⟨_, _, _, _, _, (c, d, s.row r) :: s.olog, _, _⟩ = _
      simp only [ownDrop, List.map_cons, List.sum_cons]
      by_cases hcd : c ⊆ d
      · simp only [hcd, if_true, Nat.sub_self, Nat.sub_eq_zero_of_le (dim_mono hcd)]; ring
      · simp only [hcd, if_false]; ring
    constructor
    · intro r' c' hpb hloc
      by_cases hr : r' = r
      · subst hr
        simp only [Function.update_self, Loc.sit.injEq] at hloc
        subst hloc
        simp only [ND.push, Function.update_self]
        exact ⟨by omega, by simp, hrw⟩
      · simp only [Function.update_of_ne hr] at hloc
        exact own_push hI.reg _ d 0 _ _ _ r' c' hpb hloc (Function.update_of_ne hr _ _) rfl
    · intro r' c' hpb hloc
      have hne := ne_of_pb' h2 hpb
      simp only [Function.update_of_ne hne] at hloc
      exact pub_push_pi hI.reg _ d 0 _ _ _ r' c' hpb hloc (fun _ => subset_refl _)
    · intro r' c' hpb hloc
      have hne := ne_of_pb' h2 hpb
      simp only [Function.update_of_ne hne] at hloc
      exact pub_push_g hI.reg _ d 0 _ _ _ r' c' hpb hloc
    · intro r' c' hpb hloc
      have hne := ne_of_pb' h2 hpb
      simp only [Function.update_of_ne hne] at hloc
      exact pub_push_row hI.reg _ d 0 _ _ _ r' c' hpb hloc rfl
  | clearOwn r c h1 h2 =>
    refine ⟨{ N with cur := N.cur }, ⟨same_net hI.net ?_ ?_ N.cur N.pi N.g, ?_⟩⟩
    · exact fun _ => subset_refl _
    · rfl
    constructor
    · intro r' c' hpb hloc
      by_cases hr : r' = r
      · subst hr; simp at hloc
      · simp only [Function.update_of_ne hr] at hloc ⊢
        exact hI.reg.hown r' c' hpb hloc
    · intro r' c' hpb hloc
      have hne := ne_of_pb' h2 hpb
      simp only [Function.update_of_ne hne] at hloc
      exact hI.reg.hpi r' c' hpb hloc
    · intro r' c' hpb hloc
      have hne := ne_of_pb' h2 hpb
      simp only [Function.update_of_ne hne] at hloc
      exact hI.reg.hg r' c' hpb hloc
    · intro r' c' hpb hloc
      have hne := ne_of_pb' h2 hpb
      simp only [Function.update_of_ne hne] at hloc ⊢
      exact hI.reg.hrow r' c' hpb hloc

/-- the empty network. -/
def N0 : ND R Pt := ⟨0, fun _ => ∅, fun _ => ∅, fun _ => 0, fun _ => 0, fun _ => 0, fun _ => 0, fun _ => 0,
  fun _ => 0⟩

theorem inv_init (pb : R → Bool) (ix : Pt → R) : Inv pb ix (init : St R) (N0 : ND R Pt) where
  net :=
    { hHlt := fun _ _ h => absurd rfl h
      hHn := fun _ _ h => absurd rfl h
      hrel := fun _ _ h => absurd rfl h
      hF := fun _ _ h => absurd rfl h
      hval := fun _ h => absurd h (Nat.not_lt_zero _)
      hkind := fun _ h => absurd h (Nat.not_lt_zero _)
      hdrop := by simp [N0, ownDrop, init] }
  reg :=
    { hown := fun _ _ _ h => by simp [init] at h
      hpi := fun _ _ _ h => by simp [init] at h
      hg := fun _ _ _ h => by simp [init] at h
      hrow := fun _ _ _ h => by simp [init] at h }

/-- **BRIDGE (generic)**: every reachable state carries a network satisfying Inv. -/
theorem inv_of_reach (pb : R → Bool) (ix : Pt → R) {s : St R} (h : Reach pb s) :
    ∃ N : ND R Pt, Inv pb ix s N := by
  induction h with
  | refl => exact ⟨N0, inv_init pb ix⟩
  | tail _ hst ih =>
    obtain ⟨N, hN⟩ := ih
    exact step_inv hst hN

end Generic

/-! ## Part 2: charts as F2-subspaces, labels as vectors -/

section Bits
open DF

theorem vecOf_xor (a b : ℕ) : vecOf (a ^^^ b) = vecOf a + vecOf b := by
  funext i
  simp only [vecOf, Pi.add_apply, Nat.testBit_xor]
  cases a.testBit i <;> cases b.testBit i <;> decide

theorem vecOf_zero : vecOf 0 = 0 := by funext i; simp [vecOf]

theorem vecOf_inj {a b : ℕ} (ha : a < 512) (hb : b < 512) (h : vecOf a = vecOf b) : a = b := by
  apply Nat.eq_of_testBit_eq
  intro i
  by_cases hi : i < 9
  · have := congrFun h ⟨i, hi⟩
    simp only [vecOf] at this
    cases h1 : a.testBit i <;> cases h2 : b.testBit i <;> simp_all
  · have h9 : 512 ≤ 2 ^ i := by
      calc 512 = 2 ^ 9 := by norm_num
        _ ≤ 2 ^ i := Nat.pow_le_pow_right (by norm_num) (by omega)
    rw [Nat.testBit_lt_two_pow (by omega), Nat.testBit_lt_two_pow (by omega)]

theorem zmod2_cases : ∀ r : ZMod 2, r = 0 ∨ r = 1 := by decide

/-- a subspace chart as a submodule of F2^9. -/
def subOf (c : Ch) (hc : IsSubsp c) : Submodule (ZMod 2) N8.W9 where
  carrier := vecOf '' (c : Set ℕ)
  add_mem' := by
    rintro _ _ ⟨a, ha, rfl⟩ ⟨b, hb, rfl⟩
    exact ⟨a ^^^ b, hc.2.2 a ha b hb, vecOf_xor a b⟩
  zero_mem' := ⟨0, hc.1, vecOf_zero⟩
  smul_mem' := by
    rintro r _ ⟨a, ha, rfl⟩
    rcases zmod2_cases r with rfl | rfl
    · rw [zero_smul]; exact ⟨0, hc.1, vecOf_zero⟩
    · rw [one_smul]; exact ⟨a, ha, rfl⟩

theorem span_eq_subOf (c : Ch) (hc : IsSubsp c) :
    Submodule.span (ZMod 2) (vecOf '' (c : Set ℕ)) = subOf c hc := by
  have : (vecOf '' (c : Set ℕ)) = ((subOf c hc : Submodule (ZMod 2) N8.W9) : Set N8.W9) := rfl
  rw [this, Submodule.span_eq]

/-- the dimension of a subspace chart (log2 of its size, WordModel.dim) is the F2-rank of its span. -/
theorem finrank_chart (c : Ch) (hc : IsSubsp c) :
    finrank (ZMod 2) (Submodule.span (ZMod 2) (vecOf '' (c : Set ℕ))) = dim c := by
  rw [span_eq_subOf c hc]
  have h1 : Nat.card (subOf c hc) = 2 ^ finrank (ZMod 2) (subOf c hc) := by
    rw [Module.natCard_eq_pow_finrank (K := ZMod 2), Nat.card_zmod]
  have h2 : Nat.card (subOf c hc) = c.card := by
    have e1 : Nat.card (subOf c hc) = Nat.card (vecOf '' (c : Set ℕ)) := rfl
    rw [e1, Nat.card_image_of_injOn (fun a ha b hb h => vecOf_inj (hc.2.1 a ha) (hc.2.1 b hb) h)]
    simp
  unfold dim; rw [← h2, h1, Nat.log_pow (by norm_num)]

theorem wt_eq_sum (n : ℕ) : wt n = ∑ k ∈ range 9, n / 2 ^ k % 2 := by
  simp [wt, Finset.sum_range_succ]

theorem bit_eq (n k : ℕ) : (if n.testBit k then 1 else 0) = n / 2 ^ k % 2 := by
  rw [Nat.testBit_eq_decide_div_mod_eq]
  rcases Nat.mod_two_eq_zero_or_one (n / 2 ^ k) with h | h <;> simp [h]

/-- the word model's label dot product IS the F2 dot product of the label vectors. -/
theorem dot_bridge (a b : ℕ) : ((SafeRungsClique.dot a b : ℕ) : ZMod 2) = DecoderWall.dot (vecOf a) (vecOf b) := by
  rw [DF.dot_vecOf]
  unfold SafeRungsClique.dot
  rw [ZMod.natCast_mod]
  congr 1
  rw [wt_eq_sum, Finset.card_filter]
  refine Finset.sum_congr rfl fun k _ => ?_
  rw [← bit_eq, Nat.testBit_and]

theorem dot_zero_of_Hq {v q : ℕ} (h : v ∈ Hq q) : DecoderWall.dot (vecOf v) (vecOf q) = 0 := by
  have h' := (Finset.mem_filter.1 h).2
  rw [← dot_bridge, h']; rfl

theorem sdot_comm (a b : ℕ) : SafeRungsClique.dot a b = SafeRungsClique.dot b a := by
  unfold SafeRungsClique.dot; rw [Nat.and_comm]

/-- the orthogonal complement of one vector. -/
def orthW (w : N8.W9) : Submodule (ZMod 2) N8.W9 where
  carrier := {y | DecoderWall.dot y w = 0}
  add_mem' := by
    intro a b ha hb
    simp only [Set.mem_ofPred_eq, DecoderWall.dot] at *
    rw [add_dotProduct, ha, hb, add_zero]
  zero_mem' := by simp [DecoderWall.dot]
  smul_mem' := by
    intro r y hy
    simp only [Set.mem_ofPred_eq, DecoderWall.dot] at *
    rw [smul_dotProduct, hy, smul_zero]

end Bits

/-! ## Part 3: every legal word is a P104 NetW -/

section WordNet
variable {Pt Hl Ow : Type} [Fintype Pt] [Fintype Hl] [Fintype Ow]
  [DecidableEq Pt] [DecidableEq Hl] [DecidableEq Ow]

theorem nmat_val {n : ℕ} {κ : Type} [Fintype κ] (H : Matrix (Fin n) (Fin n) ℚ) (hH : ∀ k j, H k j ≠ 0 → j < k)
    (F V : Matrix (Fin n) κ ℚ) (h : V = F + H * V) : N8.Nmat H * F = V := by
  have hF : F = (1 - H) * V := by
    rw [Matrix.sub_mul, Matrix.one_mul]; exact eq_sub_of_add_eq h.symm
  rw [hF, ← Matrix.mul_assoc, N8.Nmat_mul H hH, Matrix.one_mul]

/-- the chart of a node as a submodule (span of its label vectors). -/
noncomputable def spanCh (c : Ch) : Submodule (ZMod 2) N8.W9 := Submodule.span (ZMod 2) (DF.vecOf '' (c : Set ℕ))

/-- **WORD -> NETWORK BRIDGE.**  Every legal word (WordModelDefs.Word: reachable end state meeting the #7113 caller
contract) whose MOVE charts are subspaces (ChartsSubsp) and whose owned MOVEs are nested (OwnedNested) -- both
verifier clauses -- and whose caller's 104 port labels are the P104 labels (σ : Fin 104 ≃ Pt) yields a P104 NetW
(Net8.NetW: gather/deposit/relay rules, strict DAG, M = G(1-H)^{-1}F = c_s δ on every odd pair) with
  * total drop Σ_k drop_k = ownDrop s  (the word's owned descent, EXACTLY),
  * b_k ≤ a_k for every node,
  * c_s = 1 on D ports, 1/2 on B ports. -/
theorem word_netW (cl : Caller Pt) {s : St (Reg Pt Hl Ow)} (hw : Word cl s) (hcs : ChartsSubsp s)
    (hn : OwnedNested s) (σ : Fin 104 ≃ Pt) (hlab : ∀ i, cl.lab (σ i) = DW4.lab i) :
    ∃ (n : ℕ) (N : N8.NetW n), (∑ k, N.drop k = ownDrop s) ∧ (∀ k, N.b k ≤ N.a k) ∧
      (∀ i, N.c i = if cl.isD (σ i) then 1 else 1 / 2) := by
  obtain ⟨N, hI⟩ := inv_of_reach (pub cl) (fun p : Pt => (Reg.x p : Reg Pt Hl Ow)) hw.reach
  have hbu := born_unique hw
  have hxb : ∀ p c', (Reg.x p : Reg Pt Hl Ow) ∈ s.B c' → cl.lab p ∈ c' := by
    intro p c' h
    rw [hbu _ _ _ h (hw.x_birth p)]
    exact Finset.mem_insert_of_mem (Finset.mem_singleton_self _)
  have hlq : ∀ i, DF.lq i = DF.vecOf (cl.lab (σ i)) := fun i => by rw [hlab]; rfl
  -- the matrices
  let H' : Matrix (Fin N.n) (Fin N.n) ℚ := Matrix.of fun k j => N.H k j
  let F' : Matrix (Fin N.n) (Fin 104) ℚ := Matrix.of fun k i => N.F k (σ i)
  let G' : Matrix (Fin 104) (Fin N.n) ℚ := Matrix.of fun i k => N.g (Reg.y (σ i)) k
  let V : Matrix (Fin N.n) (Fin 104) ℚ := Matrix.of fun k i => N.val k (σ i)
  have hHlt : ∀ k j, H' k j ≠ 0 → j < k := fun k j h => hI.net.hHlt k j h
  have hV : V = F' + H' * V := by
    ext k i
    simp only [V, F', H', Matrix.add_apply, Matrix.mul_apply, Matrix.of_apply]
    rw [hI.net.hval k k.2]
    simp only [Pi.add_apply, Finset.sum_apply, Pi.smul_apply, smul_eq_mul]
    congr 1
    rw [Fin.sum_univ_eq_sum_range (fun j => N.H k j * N.val j (σ i)) N.n]
    refine Finset.sum_subset (Finset.range_subset_range.2 (le_of_lt k.2)) fun j _ hj => ?_
    have : N.H k j = 0 := by
      by_contra h; exact hj (Finset.mem_range.2 (hI.net.hHlt k j h))
    rw [this, zero_mul]
  have hNF : N8.Nmat H' * F' = V := nmat_val H' hHlt F' V hV
  have hpi0 : ∀ i p, DecoderWall.dot (DF.lq i) (DF.lq p) = 1 → N.pi (Reg.y (σ i)) (σ p) = 0 := by
    intro i p hip
    by_contra hne
    obtain ⟨c', hc', hB⟩ := hI.reg.hpi (Reg.y (σ i)) _ rfl (hw.y_final (σ i)) (σ p) hne
    have hmem : cl.lab (σ p) ∈ Hq (cl.lab (σ i)) := hc' (hxb _ _ hB)
    have h0 := dot_zero_of_Hq hmem
    rw [← hlq p, ← hlq i, DF.dot_comm'] at h0
    rw [h0] at hip; exact zero_ne_one hip
  have htgt : ∀ q q' : Pt, tgt cl (Reg.y q : Reg Pt Hl Ow) (Reg.x q') =
      if q' = q then (if cl.isD q then 1 else 1 / 2) else 0 := by
    intro q q'
    unfold tgt WordModel.e
    by_cases hD : cl.isD q = true <;> by_cases hq : q' = q <;> simp [hD, hq]
  refine ⟨N.n,
    { a := fun k => spanCh (N.a k)
      b := fun k => spanCh (N.b k)
      F := F'
      G := G'
      H := H'
      c := fun i => if cl.isD (σ i) then 1 else 1 / 2
      hF := ?_
      hG := ?_
      hHlt := hHlt
      hH := ?_
      hc := ?_
      hM := ?_ }, ?_, ?_, fun i => rfl⟩
  · intro k i hki
    obtain ⟨c', hc', hB⟩ := hI.net.hF k (σ i) hki
    rw [hlq]
    exact Submodule.subset_span ⟨_, hc' (hxb _ _ hB), rfl⟩
  · intro i k hik y hy
    obtain ⟨_, hsub⟩ := hI.reg.hg (Reg.y (σ i)) _ rfl (hw.y_final (σ i)) k hik
    have hle : spanCh (N.b k) ≤ orthW (DF.lq i) := by
      rw [spanCh, Submodule.span_le]
      rintro _ ⟨v, hv, rfl⟩
      show DecoderWall.dot (DF.vecOf v) (DF.lq i) = 0
      rw [hlq]; exact dot_zero_of_Hq (hsub hv)
    exact hle hy
  · intro k j h
    exact Submodule.span_mono (Set.image_mono (Finset.coe_subset.2 (hI.net.hrel k j h)))
  · intro i
    split_ifs <;> norm_num
  · intro i p hip
    rw [Matrix.mul_assoc, hNF]
    have hrow := congrFun (hI.reg.hrow (Reg.y (σ i)) _ rfl (hw.y_final (σ i))) (σ p)
    simp only [xp, Pi.add_apply, Finset.sum_apply, Pi.smul_apply, smul_eq_mul] at hrow
    rw [hw.final_row _ rfl, htgt, hpi0 i p hip, zero_add] at hrow
    simp only [G', V, Matrix.mul_apply, Matrix.of_apply]
    rw [Fin.sum_univ_eq_sum_range (fun k => N.g (Reg.y (σ i)) k * N.val k (σ p)) N.n, ← hrow]
    by_cases h : i = p
    · subst h; simp
    · have h' : σ p ≠ σ i := fun e => h (σ.injective e).symm
      simp [h, h']
  · show ∑ k : Fin N.n, (finrank (ZMod 2) (spanCh (N.a k)) - finrank (ZMod 2) (spanCh (N.b k))) = ownDrop s
    rw [← hI.net.hdrop, ← Fin.sum_univ_eq_sum_range (fun k => dim (N.a k) - dim (N.b k)) N.n]
    refine Finset.sum_congr rfl fun k _ => ?_
    rcases hI.net.hkind k k.2 with h | ⟨m, hm, h1, h2, _⟩
    · rw [h]; simp
    · rw [spanCh, spanCh, h1, h2, finrank_chart _ (hcs.1 m hm).1, finrank_chart _ (hcs.1 m hm).2]
  · intro k
    show spanCh (N.b k) ≤ spanCh (N.a k)
    rcases hI.net.hkind k k.2 with h | ⟨m, hm, h1, h2, h3⟩
    · rw [h]
    · rcases hn m hm with h4 | h4
      · exact absurd (le_of_lt h4) h3
      · rw [h1, h2]; exact Submodule.span_mono (Set.image_mono (Finset.coe_subset.2 (le_of_lt h4)))

/-- **D-side laws for every legal word** (through the bridge): the word's owned descent `ownDrop s` is the total drop
of a P104 NetW that has >= 8 gathering and >= 8 depositing nodes, obeys the DX downward-crossing level cut for every
level set L, and (NET8 node corollary) has ownDrop s >= 56 whenever it has at most 8 gathering and 8 depositing nodes. -/
theorem word_net_laws (cl : Caller Pt) {s : St (Reg Pt Hl Ow)} (hw : Word cl s) (hcs : ChartsSubsp s)
    (hn : OwnedNested s) (σ : Fin 104 ≃ Pt) (hlab : ∀ i, cl.lab (σ i) = DW4.lab i) :
    ∃ (n : ℕ) (N : N8.NetW n), (∑ k, N.drop k = ownDrop s) ∧ (∀ k, N.b k ≤ N.a k) ∧
      8 ≤ (N8.gatS N).card ∧ 8 ≤ (N8.depS N).card ∧
      (∀ L : Finset ℕ, ∑ l ∈ L, (N8.Mstar N.G N.H N.F N.da N.db l).rank ≤ ownDrop s) ∧
      ((N8.gatS N).card ≤ 8 → (N8.depS N).card ≤ 8 → 56 ≤ ownDrop s) := by
  obtain ⟨n, N, hd, hba, _⟩ := word_netW cl hw hcs hn σ hlab
  have hd' : ∑ k, (N.da k - N.db k) = ownDrop s := hd
  refine ⟨n, N, hd, hba, (N8.netw_gat_dep_ge8 N).1, (N8.netw_gat_dep_ge8 N).2, fun L => ?_, fun hg hdp => ?_⟩
  · rw [← hd']; exact N8.netw_dx_D_ge N L
  · rw [← hd']; exact N8.net8_node_corollary N hg hdp

end WordNet

/-! ## non-vacuity of the generic bridge: one owned register, born at a 4-chart, descends to a 2-chart (drop 1) -/
section Toy

def cT : Ch := {0, 1, 2, 3}
def dT : Ch := {0, 1}

def s1 : St (Fin 1) := ⟨fun _ => .sit cT, fun _ => 0, fun _ => ∅, fun _ => ∅, fun _ _ => 0, [], [], []⟩
/-- the toy run: birthOwn at cT, then moveOwn cT -> dT. -/
def sT : St (Fin 1) :=
  ⟨fun _ => .sit dT, fun _ => 0, fun _ => ∅, fun _ => ∅, fun _ _ => 0, [(cT, dT, fun _ => 0)], [], []⟩

theorem step1 : Step (fun _ : Fin 1 => false) init s1 := by
  have h := Step.birthOwn (pb := fun _ : Fin 1 => false) (init : St (Fin 1)) 0 cT rfl rfl
  convert h using 2 <;> first | rfl | (funext r; fin_cases r; rfl)

theorem step2 : Step (fun _ : Fin 1 => false) s1 sT := by
  have h := Step.moveOwn (pb := fun _ : Fin 1 => false) s1 0 cT dT rfl rfl
  convert h using 2 <;> first | rfl | (funext r; fin_cases r; rfl)

theorem sT_reach : Reach (fun _ : Fin 1 => false) sT :=
  Relation.ReflTransGen.tail (Relation.ReflTransGen.single step1) step2

theorem toy_ownDrop : ownDrop sT = 1 := by
  have h4 : dim cT = 2 := by
    unfold dim; rw [show cT.card = 2 ^ 2 by rfl]; exact Nat.log_pow (by norm_num) 2
  have h2 : dim dT = 1 := by
    unfold dim; rw [show dT.card = 2 ^ 1 by rfl]; exact Nat.log_pow (by norm_num) 1
  simp [ownDrop, sT, h4, h2]

/-- the generic bridge yields a network with total drop exactly 1 on the toy run. -/
theorem toy_bridge : ∃ N : ND (Fin 1) (Fin 1), Inv (fun _ => false) (fun _ => 0) sT N ∧
    ∑ k ∈ range N.n, (dim (N.a k) - dim (N.b k)) = 1 := by
  obtain ⟨N, hN⟩ := inv_of_reach (fun _ : Fin 1 => false) (fun _ : Fin 1 => (0 : Fin 1)) sT_reach
  exact ⟨N, hN, by rw [hN.net.hdrop, toy_ownDrop]⟩

end Toy

end BridgeNet

#print axioms BridgeNet.inv_of_reach
#print axioms BridgeNet.word_netW
#print axioms BridgeNet.word_net_laws
#print axioms BridgeNet.toy_bridge
