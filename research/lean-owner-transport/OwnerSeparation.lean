/-
Copyright (c) 2026 Rohan Arun. Apache-2.0.
Prepared with substantial OpenAI Codex assistance.
The one-owner condition must separate helpers from the two active data banks,
not only from other helpers. Declared idle windows supply that separation.
Physical realization of the windows remains a separate obligation.
-/
import OwnerTable
namespace OwnerTransport.OwnerSeparation
open OwnerTable

def encode (lanes ports replica lane port : Nat) : Nat :=
  (replica * lanes + lane) * ports + port

theorem div_tail (a b r : Nat) (hr : r < b) : (a * b + r) / b = a := by
  rw [Nat.mul_comm a b, Nat.mul_add_div (by omega : 0 < b), Nat.div_eq_of_lt hr, Nat.add_zero]

/-- Mixed-radix family identifiers retain replica, lane and port. -/
theorem encode_injective (lanes ports a l p b m q : Nat)
    (hl : l < lanes) (hm : m < lanes) (hp : p < ports) (hq : q < ports)
    (heq : encode lanes ports a l p = encode lanes ports b m q) :
    a = b ∧ l = m ∧ p = q := by
  unfold encode at heq
  have h := congrArg (fun n => n / ports) heq
  dsimp only at h
  rw [div_tail _ _ _ hp, div_tail _ _ _ hq] at h
  have hrep := congrArg (fun n => n / lanes) h
  dsimp only at hrep
  rw [div_tail _ _ _ hl, div_tail _ _ _ hm] at hrep
  subst b
  have hlm : l = m := by omega
  subst m
  exact ⟨rfl, rfl, by omega⟩

/-- Bounded coordinates encode a family in the declared live stock. -/
theorem encode_lt (lanes ports replicas r lane port : Nat)
    (hr : r < replicas) (hl : lane < lanes) (hp : port < ports) :
    encode lanes ports r lane port < replicas * lanes * ports := by
  have hm := Nat.mul_le_mul_right lanes (Nat.succ_le_of_lt hr)
  simp only [Nat.succ_mul] at hm
  have hrl : r * lanes + lane < replicas * lanes := by omega
  have hn := Nat.mul_le_mul_right ports (Nat.succ_le_of_lt hrl)
  simp only [Nat.succ_mul] at hn
  unfold encode
  omega

def mainOwner (c : Table) (pair : Nat → Nat) (t : Nat)
    (bank : Fin 2) (port : Fin c.ports) : Nat :=
  encode c.lanes c.ports (c.call t).2 (2 * pair (c.call t).1 + bank.val) port.val

/-- A declared borrowing window excludes active data on that replica and pair. -/
def WindowsAvoidData (c : Table) (pair : Nat → Nat) : Prop :=
  ∀ r child, r < c.replicas → child < c.children →
    ∀ t, t ∈ (c.window (r * c.children + child)).times →
      (c.call t).2 ≠ r ∨ c.lane child / 2 ≠ pair (c.call t).1

/-- Every active data wire has a different physical-family identifier. -/
theorem main_owners_injective (c : Table) (pair : Nat → Nat) (t : Nat)
    (hp : 2 * pair (c.call t).1 + 2 ≤ c.lanes)
    (a b : Fin 2 × Fin c.ports)
    (heq : mainOwner c pair t a.1 a.2 = mainOwner c pair t b.1 b.2) : a = b := by
  have ha := a.1.isLt
  have hb := b.1.isLt
  have hs := encode_injective c.lanes c.ports _ _ _ _ _ _
    (by omega) (by omega) a.2.isLt b.2.isLt heq
  apply Prod.ext
  · apply Fin.ext; omega
  · exact Fin.ext hs.2.2

/-- Accepted helpers in admissible windows never use an active data family. -/
theorem helper_main_distinct (c : Table) (h : Accepted c) (pair : Nat → Nat)
    (hw : WindowsAvoidData c pair) (t : Nat) (ht : t < c.calls)
    (hp : 2 * pair (c.call t).1 + 2 ≤ c.lanes)
    (helper : Fin c.helpers) (bank : Fin 2) (port : Fin c.ports) :
    helperOwner c t helper ≠ mainOwner c pair t bank port := by
  intro heq
  let i := t * c.helpers + helper.val
  have hc := accepted_at_coordinate c h t helper.val ht helper.isLt
  have hr := accepted_row c h i hc.1
  simp only [RowValid] at hr
  obtain ⟨_, _, _, _, _, hrep, hchild, hport, hlane, hfamily, _, _, _, _, _, hwindow⟩ := hr
  have hencoded :
      encode c.lanes c.ports (c.row i).ownerReplica (c.lane (c.row i).child) (c.row i).port =
      mainOwner c pair t bank port := by
    calc
      _ = (c.row i).family := by rw [hfamily]; simp [encode, Nat.add_mul, Nat.mul_assoc]
      _ = _ := heq
  have hbank := bank.isLt
  have hs := encode_injective c.lanes c.ports _ _ _ _ _ _
    hlane (by omega) hport port.isLt hencoded
  have htime : (c.row i).time = t := hc.2.1
  rw [htime] at hwindow
  rcases hw _ _ hrep hchild t hwindow with hother | hother
  · exact hother hs.1.symm
  · apply hother
    rw [hs.2.1, Nat.mul_comm 2 (pair (c.call t).1), div_tail _ _ _ bank.isLt]

/-- The complete register set includes two data banks and every helper. -/
def invocationOwner (c : Table) (pair : Nat → Nat) (t : Nat) :
    Sum (Fin 2 × Fin c.ports) (Fin c.helpers) → Nat
  | .inl wire => mainOwner c pair t wire.1 wire.2
  | .inr helper => helperOwner c t helper

/-- Accepted helper owners lie in the declared live family stock. -/
theorem helper_owner_lt (c : Table) (h : Accepted c) (t : Nat) (ht : t < c.calls)
    (helper : Fin c.helpers) : helperOwner c t helper < c.replicas * c.lanes * c.ports := by
  have hc := accepted_at_coordinate c h t helper.val ht helper.isLt
  have hr := accepted_row c h _ hc.1
  simp only [RowValid] at hr
  obtain ⟨_, _, _, _, _, hrep, _, hport, hlane, hfamily, _, _, _, _, _, _⟩ := hr
  unfold helperOwner
  rw [hfamily]
  have he := encode_lt c.lanes c.ports c.replicas _ _ _ hrep hlane hport
  simpa only [encode, Nat.add_mul, Nat.mul_assoc] using he

/-- Active data owners also lie in the declared live family stock. -/
theorem main_owner_lt (c : Table) (pair : Nat → Nat) (t : Nat)
    (hr : (c.call t).2 < c.replicas) (hp : 2 * pair (c.call t).1 + 2 ≤ c.lanes)
    (bank : Fin 2) (port : Fin c.ports) :
    mainOwner c pair t bank port < c.replicas * c.lanes * c.ports := by
  have hb := bank.isLt
  exact encode_lt _ _ _ _ _ _ hr (by omega) port.isLt

/-- The complete register map targets the same finite live stock. -/
theorem invocation_owner_lt (c : Table) (h : Accepted c) (pair : Nat → Nat) (t : Nat)
    (ht : t < c.calls) (hr : (c.call t).2 < c.replicas)
    (hp : 2 * pair (c.call t).1 + 2 ≤ c.lanes)
    (register : Sum (Fin 2 × Fin c.ports) (Fin c.helpers)) :
    invocationOwner c pair t register < c.replicas * c.lanes * c.ports := by
  cases register with
  | inl wire => exact main_owner_lt c pair t hr hp wire.1 wire.2
  | inr helper => exact helper_owner_lt c h t ht helper

/-- The full invocation has one register per family, conditional on its windows. -/
theorem invocation_owners_injective (c : Table) (h : Accepted c) (pair : Nat → Nat)
    (hw : WindowsAvoidData c pair) (t : Nat) (ht : t < c.calls)
    (hp : 2 * pair (c.call t).1 + 2 ≤ c.lanes) :
    ∀ a b, invocationOwner c pair t a = invocationOwner c pair t b → a = b := by
  intro a b heq
  cases a with
  | inl a =>
    cases b with
    | inl b => exact congrArg Sum.inl (main_owners_injective c pair t hp a b heq)
    | inr b => exact False.elim (helper_main_distinct c h pair hw t ht hp b a.1 a.2 heq.symm)
  | inr a =>
    cases b with
    | inl b => exact False.elim (helper_main_distinct c h pair hw t ht hp a b.1 b.2 heq)
    | inr b => exact congrArg Sum.inr (helper_owner_injective c h t ht a b heq)

end OwnerTransport.OwnerSeparation
