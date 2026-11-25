import Std

/-!
Literal PR442 inherited frame rows, with independently checked integer
witnesses. Apache-2.0. Prepared with substantial OpenAI Codex assistance.
The balanced lookup stores proofs alongside each frame; no native_decide,
external solver axiom, or sampled field arithmetic is used.

frames.json SHA-256: 884480e45865a9d9d57f5f7198844a64271b046bc95e9820efbefb9e10878330
GLOBAL-TEMPLATE.json.gz SHA-256: 6e18a9ce240229c34556ba43fd6ec28f83200dfcf85e5584d4a670aeb605aeb0
-/
namespace FrameGeometry
set_option maxRecDepth 100000
set_option maxHeartbeats 0

abbrev IntMatrix8 := Fin 8 → Fin 8 → Int
def entry (a : Array (Array Int)) : IntMatrix8 :=
  fun i j => (a.getD i.val #[]).getD j.val 0

def dot8 (a b : IntMatrix8) (i j : Fin 8) : Int :=
  a i 0 * b 0 j + (a i 1 * b 1 j + (a i 2 * b 2 j +
  (a i 3 * b 3 j + (a i 4 * b 4 j + (a i 5 * b 5 j +
  (a i 6 * b 6 j + (a i 7 * b 7 j + 0)))))))

structure FrameDatum where
  dimension : Nat
  scaled : Array (Array Int)
  /-- Exactly the source's B rows followed by its A rows. -/
  stack : Array (Array Int)
  /-- Untrusted witness for 256 times the inverse of stack. -/
  inverse256 : Array (Array Int)

def ValidFrame (d : FrameDatum) : Prop :=
  d.dimension ≤ 8 ∧
  (∀ i j : Fin 8, dot8 (entry d.scaled) (entry d.scaled) i j = 4 * entry d.scaled i j) ∧
  (∀ i j : Fin 8, entry d.scaled i j = entry d.scaled j i) ∧
  (∀ i j : Fin 8, dot8 (entry d.scaled) (fun a b => entry d.stack b a) i j =
    if j.val < d.dimension then 4 * entry d.stack j i else 0) ∧
  (∀ i j : Fin 8, dot8 (entry d.stack) (entry d.inverse256) i j =
    if i = j then 256 else 0) ∧
  (∀ i j : Fin 8, dot8 (entry d.inverse256) (entry d.stack) i j =
    if i = j then 256 else 0)

instance (d : FrameDatum) : Decidable (ValidFrame d) := by
  unfold ValidFrame
  infer_instance

abbrev CertifiedFrame := { d : FrameDatum // ValidFrame d }

end FrameGeometry
