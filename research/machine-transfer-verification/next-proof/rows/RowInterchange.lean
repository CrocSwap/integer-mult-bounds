import Mathlib.Tactic
import FramedXor

/-!
Finite semantics of cyclic row splitting and merging.

The physical row index is exactly `W * group + role`. Every role receives
`R` complete rows, including every address and arbitrary initial payload.
The framed-trace corollary exposes both required endpoint hypotheses:
the scalar word permutes roles, and the terminal gauges differ by a common
address permutation preserving the group coordinate. No machine running
time, concrete emitted trace, or recursive child accounting is assumed proved.
-/

namespace RowInterchange

def joinRow {W R : ℕ} (w : Fin W) (g : Fin R) : Fin (W * R) :=
  ⟨W * g.val + w.val, by
    calc W * g.val + w.val < W * g.val + W := Nat.add_lt_add_left w.isLt _
      _ = W * (g.val + 1) := by ring
      _ ≤ W * R := Nat.mul_le_mul_left W g.isLt⟩

def roleOf {W R : ℕ} (hW : 0 < W) (r : Fin (W * R)) : Fin W :=
  ⟨r.val % W, Nat.mod_lt _ hW⟩

def groupOf {W R : ℕ} (hW : 0 < W) (r : Fin (W * R)) : Fin R :=
  ⟨r.val / W, (Nat.div_lt_iff_lt_mul hW).2 (by simpa only [mul_comm R W] using r.isLt)⟩

theorem join_split {W R : ℕ} (hW : 0 < W) (r : Fin (W * R)) :
    joinRow (roleOf hW r) (groupOf hW r) = r := by
  apply Fin.ext
  exact Nat.div_add_mod r.val W

theorem role_join {W R : ℕ} (hW : 0 < W) (w : Fin W) (g : Fin R) :
    roleOf hW (joinRow w g) = w := by
  apply Fin.ext
  simp [roleOf, joinRow, Nat.add_mod, Nat.mod_eq_of_lt w.isLt]

theorem group_join {W R : ℕ} (hW : 0 < W) (w : Fin W) (g : Fin R) :
    groupOf hW (joinRow w g) = g := by
  apply Fin.ext
  change (W * g.val + w.val) / W = g.val
  rw [Nat.mul_add_div hW]
  simp [Nat.div_eq_of_lt w.isLt]

/-- This equivalence accounts for every finite row exactly once. -/
def rowEquiv {W R : ℕ} (hW : 0 < W) : Fin (W * R) ≃ Fin W × Fin R where
  toFun r := (roleOf hW r, groupOf hW r)
  invFun p := joinRow p.1 p.2
  left_inv := join_split hW
  right_inv p := by simp [role_join, group_join]

abbrev Payload (N : ℕ) (A B : Type) := Fin N → A → B

def splitRows {W R : ℕ} {A B : Type} (input : Payload (W * R) A B) :
    Fin W → (Fin R × A) → B := fun w p => input (joinRow w p.1) p.2

/-- `destination` maps each original role to its terminal physical role.
Reading that terminal role undoes the permutation while merging. -/
def mergeRows {W R : ℕ} {A B : Type} (hW : 0 < W)
    (destination : Fin W ≃ Fin W) (output : Fin W → (Fin R × A) → B) :
    Payload (W * R) A B :=
  fun r a => output (destination (roleOf hW r)) (groupOf hW r, a)

theorem merge_split {W R : ℕ} {A B : Type} (hW : 0 < W)
    (input : Payload (W * R) A B) :
    mergeRows hW (Equiv.refl _) (splitRows input) = input := by
  funext r a
  simp [mergeRows, splitRows, join_split]

/-- A common address pullback on complete role rows induces exactly that
pullback on original rows, with the original row coordinate unchanged. -/
theorem merge_uniform {W R : ℕ} {A B : Type} (hW : 0 < W)
    (destination : Fin W ≃ Fin W) (addressPullback : A → A)
    (input : Payload (W * R) A B) (output : Fin W → (Fin R × A) → B)
    (endpoint : ∀ w g a, output (destination w) (g, a) =
      splitRows input w (g, addressPullback a)) :
    mergeRows hW destination output = fun r a => input r (addressPullback a) := by
  funext r a
  simp only [mergeRows, endpoint, splitRows, join_split]

/-- Lift an address gauge while leaving the complete-row group unchanged. -/
def groupGauge {R : ℕ} {A : Type} (gauge : FramedXor.Gauge A) :
    FramedXor.Gauge (Fin R × A) where
  forward p := (p.1, gauge.forward p.2)
  inverse p := (p.1, gauge.inverse p.2)
  inverse_forward p := by simp [gauge.inverse_forward]
  forward_inverse p := by simp [gauge.forward_inverse]

/-- Composition with the literal framed interpreter. This is a semantic
transfer theorem with explicit scalar-word and gauge-endpoint premises. -/
theorem framed_rows {W R : ℕ} {A : Type} (hW : 0 < W)
    {first last : FramedXor.Assignment (Fin W) (Fin R × A)}
    (trace : FramedXor.Trace first last) (destination : Fin W ≃ Fin W)
    (addressMap : FramedXor.Gauge A)
    (scalar_roles : ∀ (logical : DirtyWrapper.Rows (Fin W) (Fin R × A)) role address,
      DirtyWrapper.runRows (FramedXor.scalarWord trace) logical (destination role) address =
        logical role address)
    (terminal_frames : ∀ role address,
      (last (destination role)).forward address =
        (groupGauge addressMap).forward ((first role).forward address))
    (input : Payload (W * R) A Bool) :
    mergeRows hW destination (FramedXor.execute trace (splitRows input)) =
      fun row address => input row (addressMap.inverse address) := by
  apply merge_uniform
  intro w g a
  exact FramedXor.terminal_role_transport trace destination (groupGauge addressMap)
    scalar_roles terminal_frames (splitRows input) w (g, a)

/-- Outer padding contains fresh blank rows only; every original row remains
arbitrary. Its correctness requires a row-preserving endpoint, not linearity. -/
def padRows {N M : ℕ} {A B : Type} (blank : B) (input : Payload N A B) :
    Payload M A B := fun r a => if h : r.val < N then input ⟨r.val, h⟩ a else blank

def restrictRows {N M : ℕ} {A B : Type} (hNM : N ≤ M)
    (input : Payload M A B) : Payload N A B :=
  fun r a => input ⟨r.val, Nat.lt_of_lt_of_le r.isLt hNM⟩ a

theorem restrict_pad {N M : ℕ} {A B : Type} (hNM : N ≤ M)
    (blank : B) (input : Payload N A B) :
    restrictRows hNM (padRows blank input) = input := by
  funext r a
  simp [restrictRows, padRows, r.isLt]

theorem padding_commutes {N M : ℕ} {A B : Type} (blank : B)
    (input : Payload N A B) (addressPullback : A → A) :
    (fun r a => (padRows blank input : Payload M A B) r (addressPullback a)) =
      padRows blank (fun r a => input r (addressPullback a)) := by
  funext r a
  simp [padRows]

theorem padded_endpoint_restrict {N M : ℕ} {A B : Type} (hNM : N ≤ M)
    (blank : B) (input : Payload N A B) (addressPullback : A → A)
    (output : Payload M A B)
    (endpoint : output = fun r a => (padRows blank input : Payload M A B) r (addressPullback a)) :
    restrictRows hNM output = fun r a => input r (addressPullback a) := by
  rw [endpoint, padding_commutes, restrict_pad]

theorem padded_endpoint_blank {N M : ℕ} {A B : Type}
    (blank : B) (input : Payload N A B) (addressPullback : A → A)
    (output : Payload M A B)
    (endpoint : output = fun r a => (padRows blank input : Payload M A B) r (addressPullback a))
    (r : Fin M) (h : N ≤ r.val) (a : A) : output r a = blank := by
  rw [endpoint]
  simp [padRows, Nat.not_lt_of_ge h]

end RowInterchange

#print axioms RowInterchange.join_split
#print axioms RowInterchange.role_join
#print axioms RowInterchange.group_join
#print axioms RowInterchange.merge_split
#print axioms RowInterchange.merge_uniform
#print axioms RowInterchange.framed_rows
#print axioms RowInterchange.restrict_pad
#print axioms RowInterchange.padding_commutes
#print axioms RowInterchange.padded_endpoint_restrict
#print axioms RowInterchange.padded_endpoint_blank
