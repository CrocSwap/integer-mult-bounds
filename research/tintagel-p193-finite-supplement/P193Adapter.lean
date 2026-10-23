/- Finite P193 scalar adapter, checked with official Lean 4.34.1.
   Upstream: f010392c923279e3dd59ef3aa5fedad23affc5fd.
   Interfaces: PR397 a4e0135990efa1df734d8b9dd3af0f17cfae6f5d.
   Scope: the finite signed scalar endpoint; no geometric or cost claim. -/
import Work.GCert.Data.P193ScalOK
import Work.GCert.Chain.Phased
import SourceBound

namespace Tintagel.P193Finite
open OAI.PowerSaving OAI.PowerSaving.CB OAI.PowerSaving.CR OAI.PowerSaving.GX
open OAI.PowerSaving.SS Matrix
noncomputable section

abbrev T := Fin GXD.P193.raw.v
abbrev Sl := Fin GXD.P193.raw.R
abbrev C := Fin GXD.P193.raw.ret.length
abbrev V := T → ℂ
abbrev Helpers := Sl → ℂ
abbrev State := (V × V) × Helpers
abbrev FullState := Box T Sl C → ℂ

/-- Actual ordered matrices of the literal P193 raw data; no invocation
    specification is supplied as an argument to this definition. -/
def scalar : GX.Scal T Sl C where
  Cc := GS.Ccm GXD.P193.raw
  Jr := GS.Jrm GXD.P193.raw
  MA := GS.MA GXD.P193.raw GXD.P193.scalOK.hv
  MAi := GS.MAi GXD.P193.raw GXD.P193.scalOK.hv
  MB := GS.MB GXD.P193.raw GXD.P193.scalOK.hv
  MBi := GS.MBi GXD.P193.raw GXD.P193.scalOK.hv
  hAi := GXD.P193.scalOK.hAi
  hBi := GXD.P193.scalOK.hBi
  hx := GXD.P193.scalOK.hx
  hy := GXD.P193.scalOK.hy
  hid := GXD.P193.scalOK.hid

def vectorAbelian : Tintagel.Abelian V where
  zero := 0
  add := (· + ·)
  neg := Neg.neg
  assoc := add_assoc
  comm := add_comm
  add_zero := add_zero
  add_neg := add_neg_cancel
  neg_add := by intros a b; ext i; change -(a i + b i) = -a i + -b i; abel
  neg_neg := neg_neg

def encode (s : State) : FullState := stamp s.1.1 s.1.2 s.2 (fun _ => 0)
def decode (z : FullState) : State := ((z ∘ bX, z ∘ bY), z ∘ bS)

/-- Actual phased forward word, including response, retained-copy scatter,
    inverse helper repair and scratch erasures. This is not defined as shearF. -/
def rawForward (z : FullState) : FullState :=
  eraseC (liveAct scalar.f2
    (gateS bY bC scalar.Jr (gateS bC bS scalar.Cc (liveAct scalar.f1 (eraseC z)))))

/-- Actual inverse-transpose phased backward word, not defined as shearB. -/
def rawBackward (z : FullState) : FullState :=
  eraseC (liveAct scalar.b2
    (gateS bS bC (-scalar.Ccᵀ) (gateS bC bY scalar.Jrᵀ (liveAct scalar.b1 (eraseC z)))))

def invocation : Tintagel.Abelian.Invocation vectorAbelian Helpers where
  fwd := fun s => decode (rawForward (encode s))
  bwd := fun s => decode (rawBackward (encode s))
  fwd_spec := by
    intro p h
    change decode (rawForward (encode (p,h))) = (vectorAbelian.forward p,h)
    rw [rawForward, scalar.fwd_scalar]
    rfl
  bwd_spec := by
    intro p h
    change decode (rawBackward (encode (p,h))) = (vectorAbelian.backward p,h)
    rw [rawBackward, scalar.bwd_scalar]
    change ((p.1 - p.2,p.2),h) = ((p.1 + -p.2,p.2),h)
    rw [sub_eq_add_neg]

/-- Closed provider term, with no Invocation or scalar-identity hypothesis. -/
theorem finite_b3_signed_endpoint {Ω : Type} (p q r : Ω → V × V)
    (h : Ω → Helpers) (ω : Ω) :
    let z := Tintagel.Abelian.sourceB3With vectorAbelian (fun _ => invocation)
      (p ω) (q ω) (r ω) (h ω)
    (z.1.map vectorAbelian.signedExchange,z.2) = ([p ω,q ω,r ω],h ω) :=
  Tintagel.Abelian.sourceB3_correlated_signed_endpoint vectorAbelian
    (fun _ => invocation) p q r h ω

end
end Tintagel.P193Finite

-- Transitive axiom checks; see the independent audit receipt for source bindings.
#print axioms GXD.P193.scalOK
#print axioms Tintagel.P193Finite.scalar
#print axioms Tintagel.P193Finite.invocation
#print axioms Tintagel.P193Finite.finite_b3_signed_endpoint
