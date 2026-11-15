import Work.GCert.Scalar.Roles
import Work.GCert.Labels.Main

/-!
# (key: gx-data) Glue between the scalar half (gx-scalar) and the label half (gx-labels)

For ANY `c : GXD.Raw` (nothing is evaluated here):

* `roles`   gx-scalar's numbering `GS.emb` / `GS.unemb` is gx-labels' `GLab.Roles`;
* `scalOf`  gx-chain's record `GX.Scal (Fin v) (Fin R) (Fin ret.length)` from the FIVE scalar
            identities of the matrices `GS.MA`, `GS.MAi`, `GS.MB`, `GS.MBi`, `GS.Jrm`, `GS.Ccm`;
* `scalOf_MA .. scalOf_MBi`  its gate matrices are the ordered products of the adds of `c`, in
            the form asked by `GLab.Valid.lab` (`GLab.mic GS.toCoef`);
* `reg`, `reg_slot`, `reg_mem`  copy `k` reads the retained register `(c.ret.getD k (0,0)).1`.

So a generated instance needs from the scalar side exactly `hAi hBi hx hy hid` (see
`wht_<Inst>_of_ids` in `Work/GCert/Data/<Inst>.lean`).  No `sorry`.
-/

namespace GXD
open SSC OAI.PowerSaving OAI.PowerSaving.CR Matrix

/-- the numbering of the roles: `x_t = t`, `y_t = v + t`, slot `q = 2 v + q` -/
theorem roles (c : Raw) (hv : 0 < c.v) : GLab.Roles c.v c.R (GS.emb c) (GS.unemb c hv) where
  hun := GS.unemb_emb hv
  hin := GS.emb_unemb hv
  hlt := fun q => by
    rcases q with (t | S) | q
    · have := t.isLt; show t.val < 2 * c.v + c.R; omega
    · have := S.isLt; show c.v + S.val < 2 * c.v + c.R; omega
    · have := q.isLt; show 2 * c.v + q.val < 2 * c.v + c.R; omega
  eX := fun _ => rfl
  eY := fun _ => rfl
  eS := fun _ => rfl

/-- **the scalar half as gx-chain's record**, from the five scalar identities -/
noncomputable def scalOf (c : Raw) (hv : 0 < c.v)
    (hAi : GS.MAi c hv * GS.MA c hv = 1) (hBi : GS.MBi c hv * GS.MB c hv = 1)
    (hx : ∀ (t : Fin c.v) (j : GS.Rl c), (GS.MB c hv * scatM (GS.Jrm c * GS.Ccm c) * GS.MA c hv)
      (lX t) j = if lX t = j then 1 else 0)
    (hy : ∀ (i : GS.Rl c) (t : Fin c.v), (GS.MB c hv * scatM (GS.Jrm c * GS.Ccm c) * GS.MA c hv)
      i (lY t) = if i = lY t then 1 else 0)
    (hid : ∀ S t : Fin c.v, (GS.MB c hv * scatM (GS.Jrm c * GS.Ccm c) * GS.MA c hv)
      (lY S) (lX t) = if S = t then 1 else 0) :
    GX.Scal (Fin c.v) (Fin c.R) (Fin c.ret.length) where
  Cc := GS.Ccm c
  Jr := GS.Jrm c
  MA := GS.MA c hv
  MAi := GS.MAi c hv
  MB := GS.MB c hv
  MBi := GS.MBi c hv
  hAi := hAi
  hBi := hBi
  hx := hx
  hy := hy
  hid := hid

section
variable (c : Raw) (hv : 0 < c.v) (hAi) (hBi) (hx) (hy) (hid)

theorem scalOf_MA : (scalOf c hv hAi hBi hx hy hid).MA
    = matP (GS.unemb c hv) (GLab.mic GS.toCoef (c.gatesA.flatMap Gate.adds)) := rfl

theorem scalOf_MAi : (scalOf c hv hAi hBi hx hy hid).MAi
    = matPinv (GS.unemb c hv) (GLab.mic GS.toCoef (c.gatesA.flatMap Gate.adds)) := rfl

theorem scalOf_MB : (scalOf c hv hAi hBi hx hy hid).MB
    = matP (GS.unemb c hv) (GLab.mic GS.toCoef (c.gatesB.flatMap Gate.adds)) := rfl

theorem scalOf_MBi : (scalOf c hv hAi hBi hx hy hid).MBi
    = matPinv (GS.unemb c hv) (GLab.mic GS.toCoef (c.gatesB.flatMap Gate.adds)) := rfl

end

/-- the register read by copy `k` (the slot of the retained total `k`) -/
def reg (c : Raw) (k : Fin c.ret.length) : Nat := (c.ret.getD k.val (0, 0)).1

theorem reg_slot (c : Raw) (hv : 0 < c.v) (hAi) (hBi) (hx) (hy) (hid) (k : Fin c.ret.length)
    (q : Fin c.R) (h : (scalOf c hv hAi hBi hx hy hid).Cc k q ≠ 0) :
    reg c k = 2 * c.v + q.val := by
  have h' : (if 2 * c.v + q.val = (c.ret.getD k.val (0, 0)).1 then (1:ℚ) else 0) ≠ 0 := h
  by_cases e : 2 * c.v + q.val = (c.ret.getD k.val (0, 0)).1
  · exact e.symm
  · rw [if_neg e] at h'; exact absurd rfl h'

theorem reg_mem (c : Raw) (k : Fin c.ret.length) : reg c k ∈ c.ret.map Prod.fst := by
  unfold reg
  rw [List.getD_eq_getElem _ _ k.isLt]
  exact List.mem_map.mpr ⟨_, List.getElem_mem k.isLt, rfl⟩

end GXD

#print axioms GXD.roles
#print axioms GXD.scalOf
#print axioms GXD.scalOf_MA
#print axioms GXD.reg_slot
#print axioms GXD.reg_mem
