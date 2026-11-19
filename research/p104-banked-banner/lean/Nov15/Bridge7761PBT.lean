/- Bridge7761PBT .  Binary lookup tree for kernel O(depth) lookups (no imports). -/
namespace BridgeP

inductive BT (α : Type) where
  | lf (v : α)
  | nd (l r : BT α)

noncomputable def BT.get {α : Type} (t : BT α) : Nat → α :=
  BT.rec (motive := fun _ => Nat → α) (fun v _ => v) (fun _ _ gl gr k => if k % 2 = 0 then gl (k / 2) else gr (k / 2)) t

end BridgeP
