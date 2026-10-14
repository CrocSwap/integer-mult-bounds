/-
Copyright (c) 2026 Rohan Arun. All rights reserved.
Apache-2.0; substantial OpenAI Codex assistance.

A sound finite owner-table checker. The witness contains rows plus untrusted
index lists. Acceptance checks their linkage; Python grouping is not a premise.
Windows here are DECLARED windows, not yet derived from physical execution.
-/
import OwnerTransport

namespace OwnerTransport.OwnerTable

structure Role where
  time : Nat
  helper : Nat
  stage : Nat
  replica : Nat
  ownerReplica : Nat
  child : Nat
  port : Nat
  family : Nat
  offset : Nat
  width : Nat
  slot : Nat
  familyRank : Nat
  deriving Repr, DecidableEq, Inhabited

structure Window where
  capacity : Nat
  times : List Nat
  deriving Repr, Inhabited

structure Table where
  ports : Nat
  children : Nat
  replicas : Nat
  helpers : Nat
  calls : Nat
  lanes : Nat
  row : Nat → Role
  group : Nat → List Nat
  byFamily : Nat → List Nat
  window : Nat → Window
  call : Nat → Nat × Nat
  width : Nat → Nat
  lane : Nat → Nat

/-- Each helper in each invocation has one canonical row address. -/
def rowCount (c : Table) : Nat := c.calls * c.helpers

def groupCount (c : Table) : Nat := c.replicas * c.children * c.ports

/-- The key retains the owner replica, child and port. -/
def groupId (c : Table) (r : Role) : Nat :=
  (r.ownerReplica * c.children + r.child) * c.ports + r.port

/-- A row's semantic and index-list contracts, without assuming the checker. -/
def RowValid (c : Table) (i : Nat) : Prop :=
  let r := c.row i
  r.time < c.calls ∧ r.helper < c.helpers ∧ r.time * c.helpers + r.helper = i ∧
  r.stage = (c.call r.time).1 ∧ r.replica = (c.call r.time).2 ∧
  r.ownerReplica < c.replicas ∧ r.child < c.children ∧ r.port < c.ports ∧
  c.lane r.child < c.lanes ∧
  r.family = r.ownerReplica * (c.lanes * c.ports) + c.lane r.child * c.ports + r.port ∧
  r.width = c.width r.helper ∧ 0 < r.width ∧
  groupId c r < groupCount c ∧
  (c.group (groupId c r))[r.slot]? = some i ∧
  (c.byFamily r.time)[r.familyRank]? = some i ∧
  r.time ∈ (c.window (r.ownerReplica * c.children + r.child)).times

instance (c : Table) (i : Nat) : Decidable (RowValid c i) := by
  unfold RowValid
  infer_instance

def checkRow (c : Table) (i : Nat) : Bool := decide (RowValid c i)

/-- Check actual row offsets, not a compressed shape supplied by the generator. -/
def checkBlocks (c : Table) (gid capacity start : Nat) : List Nat → Bool
  | [] => decide (start ≤ capacity)
  | i :: rest =>
    decide (i < rowCount c ∧ groupId c (c.row i) = gid ∧ (c.row i).offset = start) &&
    checkBlocks c gid capacity (start + (c.row i).width) rest

/-- Check strict physical-family ordering within an actual invocation. -/
def checkFamilies (c : Table) (time lower : Nat) : List Nat → Bool
  | [] => true
  | i :: rest =>
    decide (i < rowCount c ∧ (c.row i).time = time ∧ lower ≤ (c.row i).family) &&
    checkFamilies c time ((c.row i).family + 1) rest

/-- Semantic interval bounds and order exported by the block checker. -/
def BlockFacts (c : Table) (gid capacity start : Nat) (refs : List Nat) : Prop :=
  (∀ i, i ∈ refs → i < rowCount c ∧ groupId c (c.row i) = gid ∧
    start ≤ (c.row i).offset ∧ (c.row i).offset + (c.row i).width ≤ capacity) ∧
  refs.Pairwise (fun i j => (c.row i).offset + (c.row i).width ≤ (c.row j).offset)

/-- Boolean acceptance implies actual interval bounds and pairwise separation. -/
theorem blocks_sound (c : Table) (gid capacity start : Nat) (refs : List Nat)
    (h : checkBlocks c gid capacity start refs = true) :
    BlockFacts c gid capacity start refs := by
  induction refs generalizing start with
  | nil => exact ⟨by simp, List.Pairwise.nil⟩
  | cons i rest ih =>
    simp only [checkBlocks, Bool.and_eq_true, decide_eq_true_eq] at h
    obtain ⟨⟨hi, hg, ho⟩, hrest⟩ := h
    obtain ⟨hbounds, hp⟩ := ih (start + (c.row i).width) hrest
    have hend : start + (c.row i).width ≤ capacity := by
      cases rest with
      | nil => simpa only [checkBlocks, decide_eq_true_eq] using hrest
      | cons j js =>
        have hj := hbounds j (by simp)
        omega
    refine ⟨?_, List.pairwise_cons.mpr ⟨?_, hp⟩⟩
    · intro j hj
      rcases List.mem_cons.mp hj with rfl | hjrest
      · exact ⟨hi, hg, by omega, by omega⟩
      · have hr := hbounds j hjrest
        exact ⟨hr.1, hr.2.1, by omega, hr.2.2.2⟩
    · intro j hj
      have hr := hbounds j hj
      omega

/-- Family-list acceptance proves the actual row families are strictly ordered. -/
theorem families_sound (c : Table) (time lower : Nat) (refs : List Nat)
    (h : checkFamilies c time lower refs = true) :
    (∀ i, i ∈ refs → i < rowCount c ∧ (c.row i).time = time ∧ lower ≤ (c.row i).family) ∧
    refs.Pairwise (fun i j => (c.row i).family < (c.row j).family) := by
  induction refs generalizing lower with
  | nil => exact ⟨by simp, List.Pairwise.nil⟩
  | cons i rest ih =>
    simp only [checkFamilies, Bool.and_eq_true, decide_eq_true_eq] at h
    obtain ⟨⟨hi, ht, hl⟩, hrest⟩ := h
    obtain ⟨hbounds, hp⟩ := ih ((c.row i).family + 1) hrest
    refine ⟨?_, List.pairwise_cons.mpr ⟨?_, hp⟩⟩
    · intro j hj
      rcases List.mem_cons.mp hj with rfl | hjrest
      · exact ⟨hi, ht, hl⟩
      · have hr := hbounds j hjrest
        exact ⟨hr.1, hr.2.1, by omega⟩
    · intro j hj
      have hr := hbounds j hj
      omega

/-- Strictly increasing family values give injective ownership on the list. -/
theorem ordered_families_injective (c : Table) (refs : List Nat)
    (h : refs.Pairwise (fun i j => (c.row i).family < (c.row j).family)) :
    ∀ i, i ∈ refs → ∀ j, j ∈ refs → (c.row i).family = (c.row j).family → i = j := by
  induction refs with
  | nil => simp
  | cons a rest ih =>
    obtain ⟨ha, hr⟩ := List.pairwise_cons.mp h
    intro i hi j hj heq
    rcases List.mem_cons.mp hi with rfl | hirest
    · rcases List.mem_cons.mp hj with rfl | hjrest
      · rfl
      · have := ha j hjrest; omega
    · rcases List.mem_cons.mp hj with rfl | hjrest
      · have := ha i hirest; omega
      · exact ih hr i hirest j hjrest heq

/-- Ordered intervals give injective occupied coordinates, even with zero widths. -/
theorem ordered_blocks_nonalias (c : Table) (refs : List Nat)
    (h : refs.Pairwise (fun i j => (c.row i).offset + (c.row i).width ≤ (c.row j).offset)) :
    ∀ i, i ∈ refs → ∀ j, j ∈ refs → ∀ x y,
      x < (c.row i).width → y < (c.row j).width →
      (c.row i).offset + x = (c.row j).offset + y → i = j ∧ x = y := by
  induction refs with
  | nil => simp
  | cons a rest ih =>
    obtain ⟨ha, hr⟩ := List.pairwise_cons.mp h
    intro i hi j hj x y hx hy heq
    rcases List.mem_cons.mp hi with rfl | hirest
    · rcases List.mem_cons.mp hj with rfl | hjrest
      · exact ⟨rfl, by omega⟩
      · have := ha j hjrest; omega
    · rcases List.mem_cons.mp hj with rfl | hjrest
      · have := ha i hirest; omega
      · exact ih hr i hirest j hjrest x y hx hy heq

/-- Complete certificate: rows, all owner groups, and all call family lists. -/
def Accepted (c : Table) : Prop :=
  (∀ i, i < rowCount c → checkRow c i = true) ∧
  (∀ g, g < groupCount c →
    checkBlocks c g (c.window (g / c.ports)).capacity 0 (c.group g) = true) ∧
  (∀ t, t < c.calls → checkFamilies c t 0 (c.byFamily t) = true)

/-- The full finite checker does not trust either index-list construction. -/
def checkTable (c : Table) : Bool :=
  (List.range (rowCount c)).all (checkRow c) &&
  (List.range (groupCount c)).all (fun g =>
    checkBlocks c g (c.window (g / c.ports)).capacity 0 (c.group g)) &&
  (List.range c.calls).all (fun t => checkFamilies c t 0 (c.byFamily t))

/-- A successful finite computation discharges every universally quantified check. -/
theorem table_sound (c : Table) (h : checkTable c = true) : Accepted c := by
  simp only [checkTable, Bool.and_eq_true, List.all_eq_true, List.mem_range] at h
  exact ⟨h.1.1, h.1.2, h.2⟩

/-- Every source row satisfies the semantic row contract. -/
theorem accepted_row (c : Table) (h : Accepted c) (i : Nat) (hi : i < rowCount c) :
    RowValid c i := of_decide_eq_true (h.1 i hi)

/-- The row's checked inverse index gives actual membership in its owner group. -/
theorem accepted_group_mem (c : Table) (h : Accepted c) (i : Nat) (hi : i < rowCount c) :
    i ∈ c.group (groupId c (c.row i)) := by
  have hr := accepted_row c h i hi
  unfold RowValid at hr
  exact List.mem_of_getElem? hr.2.2.2.2.2.2.2.2.2.2.2.2.2.1

/-- The row's checked inverse index gives actual membership in its call family list. -/
theorem accepted_family_mem (c : Table) (h : Accepted c) (i : Nat) (hi : i < rowCount c) :
    i ∈ c.byFamily (c.row i).time := by
  have hr := accepted_row c h i hi
  unfold RowValid at hr
  exact List.mem_of_getElem? hr.2.2.2.2.2.2.2.2.2.2.2.2.2.2.1

/-- All occupied coordinates of every accepted helper fit its actual owner group. -/
theorem accepted_capacity (c : Table) (h : Accepted c) (i x : Nat)
    (hi : i < rowCount c) (hx : x < (c.row i).width) :
    (c.row i).offset + x < (c.window (groupId c (c.row i) / c.ports)).capacity := by
  have hr := accepted_row c h i hi
  have hg : groupId c (c.row i) < groupCount c := hr.2.2.2.2.2.2.2.2.2.2.2.2.1
  have hb := blocks_sound c _ _ _ _ (h.2.1 _ hg)
  have hi' := accepted_group_mem c h i hi
  have hb' := hb.1 i hi'
  omega

/-- Different helper rows in the same call cannot use the same physical family. -/
theorem accepted_owner_injective (c : Table) (h : Accepted c) (i j : Nat)
    (hi : i < rowCount c) (hj : j < rowCount c)
    (ht : (c.row i).time = (c.row j).time)
    (hf : (c.row i).family = (c.row j).family) : i = j := by
  have hr := accepted_row c h i hi
  have hi' := accepted_family_mem c h i hi
  have hj' := accepted_family_mem c h j hj
  rw [← ht] at hj'
  have hs := families_sound c _ _ _ (h.2.2 _ hr.1)
  exact ordered_families_injective c _ hs.2 i hi' j hj' hf

/-- Two actual helpers allocated to the same owner/child/port cannot alias. -/
theorem accepted_nonalias (c : Table) (h : Accepted c) (i j x y : Nat)
    (hi : i < rowCount c) (hj : j < rowCount c)
    (hg : groupId c (c.row i) = groupId c (c.row j))
    (hx : x < (c.row i).width) (hy : y < (c.row j).width)
    (heq : (c.row i).offset + x = (c.row j).offset + y) : i = j ∧ x = y := by
  have hr := accepted_row c h i hi
  have hgi : groupId c (c.row i) < groupCount c := hr.2.2.2.2.2.2.2.2.2.2.2.2.1
  have hi' := accepted_group_mem c h i hi
  have hj' := accepted_group_mem c h j hj
  rw [← hg] at hj'
  have hs := blocks_sound c _ _ _ _ (h.2.1 _ hgi)
  exact ordered_blocks_nonalias c _ hs.2 i hi' j hj' x y hx hy heq

/-- The flattened group key selects the row's declared owner window. -/
theorem group_window_index (c : Table) (r : Role) (hp : r.port < c.ports) :
    groupId c r / c.ports = r.ownerReplica * c.children + r.child := by
  unfold groupId
  rw [Nat.mul_comm (r.ownerReplica * c.children + r.child) c.ports]
  rw [Nat.mul_add_div (by omega : 0 < c.ports), Nat.div_eq_of_lt hp, Nat.add_zero]

/-- Bounds refer to the exact same declared window that admitted the invocation. -/
theorem accepted_declared_window_capacity (c : Table) (h : Accepted c) (i x : Nat)
    (hi : i < rowCount c) (hx : x < (c.row i).width) :
    (c.row i).offset + x <
      (c.window ((c.row i).ownerReplica * c.children + (c.row i).child)).capacity := by
  have hr := accepted_row c h i hi
  have hp : (c.row i).port < c.ports := hr.2.2.2.2.2.2.2.1
  have hb := accepted_capacity c h i x hi hx
  rwa [group_window_index c (c.row i) hp] at hb

/-- Every call/helper coordinate has one and only one row in an accepted table. -/
theorem accepted_census (c : Table) (h : Accepted c) (t helper : Nat)
    (ht : t < c.calls) (hh : helper < c.helpers) :
    ∃ i, i < rowCount c ∧ (c.row i).time = t ∧ (c.row i).helper = helper ∧
      ∀ j, j < rowCount c → (c.row j).time = t → (c.row j).helper = helper → j = i := by
  let i := t * c.helpers + helper
  have hp : 0 < c.helpers := by omega
  have hi : i < rowCount c := by
    have hm := Nat.mul_le_mul_right c.helpers (Nat.succ_le_of_lt ht)
    simp only [Nat.succ_mul] at hm
    unfold i rowCount
    omega
  have hr := accepted_row c h i hi
  have hrh : (c.row i).helper < c.helpers := hr.2.1
  have hre : (c.row i).time * c.helpers + (c.row i).helper = i := hr.2.2.1
  have hdiv : i / c.helpers = t := by
    unfold i
    rw [Nat.mul_comm t c.helpers, Nat.mul_add_div hp, Nat.div_eq_of_lt hh, Nat.add_zero]
  have hrt : (c.row i).time = t := by
    rw [← hre, Nat.mul_comm (c.row i).time c.helpers,
      Nat.mul_add_div hp, Nat.div_eq_of_lt hrh, Nat.add_zero] at hdiv
    exact hdiv
  have hrhelper : (c.row i).helper = helper := by
    rw [hrt] at hre
    have hre' : t * c.helpers + (c.row i).helper = t * c.helpers + helper := hre
    omega
  refine ⟨i, hi, hrt, hrhelper, ?_⟩
  intro j hj hjt hjh
  have hrj := accepted_row c h j hj
  have heq : (c.row j).time * c.helpers + (c.row j).helper = j := hrj.2.2.1
  rw [hjt, hjh] at heq
  exact heq.symm

/-- The canonical flat index itself has the advertised call/helper coordinates. -/
theorem accepted_at_coordinate (c : Table) (h : Accepted c) (t helper : Nat)
    (ht : t < c.calls) (hh : helper < c.helpers) :
    let i := t * c.helpers + helper
    i < rowCount c ∧ (c.row i).time = t ∧ (c.row i).helper = helper := by
  obtain ⟨i, hi, htime, hhelper, _⟩ := accepted_census c h t helper ht hh
  have heq := (accepted_row c h i hi).2.2.1
  rw [htime, hhelper] at heq
  subst i
  exact ⟨hi, htime, hhelper⟩

/-- Owner map for the helpers of a single invocation, suitable for hosting interfaces. -/
def helperOwner (c : Table) (t : Nat) (helper : Fin c.helpers) : Nat :=
  (c.row (t * c.helpers + helper.val)).family

/-- Acceptance supplies the helper part of the one-owner hosting hypothesis. -/
theorem helper_owner_injective (c : Table) (h : Accepted c) (t : Nat) (ht : t < c.calls) :
    ∀ a b : Fin c.helpers, helperOwner c t a = helperOwner c t b → a = b := by
  intro a b heq
  have ha := accepted_at_coordinate c h t a.val ht a.isLt
  have hb := accepted_at_coordinate c h t b.val ht b.isLt
  have hi := accepted_owner_injective c h _ _ ha.1 hb.1
    (ha.2.1.trans hb.2.1.symm) heq
  apply Fin.ext
  omega

/-- Total occupied width of the referenced rows. -/
def occupiedWidth (c : Table) : List Nat → Nat
  | [] => 0
  | i :: rest => (c.row i).width + occupiedWidth c rest

/-- The accepted offsets cover every coordinate in their occupied prefix. -/
theorem blocks_cover (c : Table) (gid capacity start : Nat) (refs : List Nat)
    (h : checkBlocks c gid capacity start refs = true) :
    ∀ x, start ≤ x → x < start + occupiedWidth c refs →
      ∃ i, i ∈ refs ∧ ∃ k, k < (c.row i).width ∧ (c.row i).offset + k = x := by
  induction refs generalizing start with
  | nil => simp [occupiedWidth]
  | cons i rest ih =>
    simp only [checkBlocks, Bool.and_eq_true, decide_eq_true_eq] at h
    obtain ⟨⟨_, _, ho⟩, hrest⟩ := h
    intro x hlo hhi
    by_cases hx : x < start + (c.row i).width
    · refine ⟨i, by simp, x - start, ?_, ?_⟩ <;> omega
    · have htail := ih (start + (c.row i).width) hrest x (by omega)
        (by simp only [occupiedWidth] at hhi; omega)
      obtain ⟨j, hj, k, hk, heq⟩ := htail
      exact ⟨j, by simp [hj], k, hk, heq⟩

/-- A bounded computation can be checked independently and then used universally. -/
def checkRange (check : Nat → Bool) (base count : Nat) : Bool :=
  (List.range count).all (fun j => check (base + j))

theorem range_sound (check : Nat → Bool) (base count i : Nat)
    (h : checkRange check base count = true) (hlo : base ≤ i) (hhi : i < base + count) :
    check i = true := by
  have hr := List.all_eq_true.mp h (i - base) (List.mem_range.mpr (by omega))
  have heq : base + (i - base) = i := by omega
  rwa [heq] at hr

/-- Independently checked chunks cover the complete finite domain. -/
theorem chunks_sound (check : Nat → Bool) (size chunks : Nat) (hs : 0 < size)
    (h : ∀ q, q < chunks → checkRange check (q * size) size = true)
    (i : Nat) (hi : i < chunks * size) : check i = true := by
  have hq : i / size < chunks := (Nat.div_lt_iff_lt_mul hs).mpr hi
  have hlo := Nat.div_mul_le_self i size
  have hmod := Nat.mod_lt i hs
  have hsplit := Nat.div_add_mod i size
  rw [Nat.mul_comm size (i / size)] at hsplit
  exact range_sound check (i / size * size) size i (h _ hq) hlo (by omega)

end OwnerTransport.OwnerTable
