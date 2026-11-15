import Work.BridgeGeom.Net
import Work.Bridge.Cert
import Work.Reframe.F3
import Work.Combine.XCirc

/-!
# (key: bridge-geom) The bridged word B_2: block certificate for ANY checked helper circuit

`BR.bridge2_certificate` (agent bridge-net, `Work.Bridge.Cert`) applied to the geometric term
`BG.geomBridge2` (`Work.BridgeGeom.Net`).  Counterpart of `Work.Reframe.F3` for five stages.

* `bridge2_bcert_geom I base l hbase hH`   for an invocation package whose lines are the vectors
                              of index `l` of orthonormal bases;
* `bridge2_bcert N`           for every `CB.XNetData` (block circuit, bases through its input
                              vectors; `pad` is ignored): a finite type `Γ` (the orthogonal
                              matrices of the label space `L5 H = H ⊕ (Fin 4 × H)`, `m = 5h`) and a
                              block certificate with
                                live roles  `card Γ * (4 card T + card Sl)`     (`BR.card_BLive`)
                                price  `card Γ * (5 * X.cost φ + 2 card T * (φ(h-1) + φ(2h-2) + φ(2h+2) + φ 4))`;
* `SSC.PCert.Valid.bridge2_bcert V hid h2`   the same for a certificate `c : SSC.PCert` accepted
                              by the kernel checks: the MERGED unit price of PLAN2.md B1,
                              `5 * (rcost φ c.invRanks + 2 v bcost φ (h-1))
                                 + 2 v (bcost φ (h-1) + bcost φ (2h-2) + bcost φ (2h+2) + bcost φ 4)`
                              (`= BridgeRate.B2L16.unitPrice φ` for `c = LinkedCert16.cert`).

No `sorry` in this file; the proof of `bridge2_certificate` is bridge-net's.
-/

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace OAI
namespace PowerSaving
namespace BG
open Binary Matrix Finset RAM SS CB RF BR
noncomputable section

section
variable {H T Sl C : Type} [Fintype H] [DecidableEq H] [Fintype T] [DecidableEq T]
  [Fintype Sl] [DecidableEq Sl] [Fintype C] [DecidableEq C]

/-- the bank blocks of one class outside the invocations (merged idle climbs). -/
def bankPrice (h : ℕ) (φ : ℕ → ℝ) : ℝ :=
  (bcost φ (2 * h - 2) + bcost φ (2 * h - 2)) + 2 * bcost φ (h - 1)
    + (bcost φ (2 * h + 2) + bcost φ (2 * h + 2)) + (bcost φ 4 + bcost φ 4)

/-- **Block certificate of the bridged word B_2** for an invocation package whose lines are the
vectors of index `l` of orthonormal bases. -/
theorem bridge2_bcert_geom (I : Inv H T Sl C) (base : T → OBase H) (l : H)
    (hbase : ∀ t, I.tv t = (base t).v l) (hH : 1 ≤ Fintype.card H) :
    BCert (L5 H) (Sum.inl : BLive (Orth (L5 H)) T Sl → BRole (Orth (L5 H)) T Sl C)
      (fun φ => (Fintype.card (Orth (L5 H)) : ℝ)
        * (5 * I.cost φ + (Fintype.card T : ℝ) * bankPrice (Fintype.card H) φ)) :=
  bridge2_certificate (geomBridge2 I base l hbase hH)

/-- **Block certificate of the bridged word B_2**, for any block circuit with bases through its
input vectors. -/
theorem bridge2_bcert (N : CB.XNetData H T Sl C) :
    ∃ (Γ : Type) (_ : Fintype Γ) (_ : DecidableEq Γ), 1 ≤ Fintype.card Γ ∧
      BCert (L5 H) (Sum.inl : BLive Γ T Sl → BRole Γ T Sl C)
        (fun φ => (Fintype.card Γ : ℝ)
          * (5 * N.X.cost φ + (Fintype.card T : ℝ) * bankPrice (Fintype.card H) φ)) := by
  have hH2 := N.hH
  have hH1 : 1 ≤ Fintype.card H := by omega
  have hpos : 0 < Fintype.card H := by omega
  obtain ⟨l⟩ : Nonempty H := Fintype.card_pos_iff.mp hpos
  have hb : ∀ t, N.X.inv.tv t = (reindex (N.base t) (Equiv.swap (N.piv t) l)).v l := by
    intro t
    show N.X.K.tv t = _
    rw [N.hbase t]
    show (N.base t).v (N.piv t) = (N.base t).v (Equiv.swap (N.piv t) l l)
    rw [Equiv.swap_apply_right]
  refine ⟨Orth (L5 H), inferInstance, inferInstance, Orth.card_pos, ?_⟩
  exact bridge2_bcert_geom N.X.inv (fun t => reindex (N.base t) (Equiv.swap (N.piv t) l)) l hb hH1

end
end
end BG
end PowerSaving
end OAI

namespace SSC
namespace PCert
open OAI OAI.PowerSaving OAI.PowerSaving.Binary OAI.PowerSaving.RAM OAI.PowerSaving.CB
  OAI.PowerSaving.RF OAI.PowerSaving.BR OAI.PowerSaving.BG

variable {c : PCert}

/-- **Block certificate of the bridged word B_2 with a kernel-checked helper circuit.**
`v = c.v` triples, `R = c.R` helper slots, `h = c.p.h`; label dimension `5h`; live roles
`card Γ * (4 v + R)`; merged idle climbs. -/
theorem Valid.bridge2_bcert (V : c.Valid) (hid : c.ScalarId V.hR) (h2 : 2 ≤ c.p.h) :
    ∃ (Γ : Type) (_ : Fintype Γ) (_ : DecidableEq Γ), 1 ≤ Fintype.card Γ ∧
      BCert (L5 (Fin c.p.h))
        (Sum.inl : BLive Γ (Fin c.v) (Fin c.R) → BRole Γ (Fin c.v) (Fin c.R) (Fin c.p.h))
        (fun φ => (Fintype.card Γ : ℝ)
          * (5 * (rcost φ c.invRanks + 2 * ((c.v : ℝ) * bcost φ (c.p.h - 1)))
              + 2 * ((c.v : ℝ) * (bcost φ (c.p.h - 1) + bcost φ (2 * c.p.h - 2)
                  + bcost φ (2 * c.p.h + 2) + bcost φ 4)))) := by
  obtain ⟨Γ, i1, i2, hG, h⟩ := BG.bridge2_bcert (V.xnetdata hid 0 h2)
  refine ⟨Γ, i1, i2, hG, h.cast (fun φ => ?_)⟩
  show (Fintype.card Γ : ℝ) * (5 * (V.xcircuit hid).cost φ
      + (Fintype.card (Fin c.v) : ℝ) * BG.bankPrice (Fintype.card (Fin c.p.h)) φ) = _
  rw [V.xcost hid φ, Fintype.card_fin, Fintype.card_fin]
  unfold BG.bankPrice
  ring

end PCert
end SSC

#print axioms OAI.PowerSaving.BG.bridge2_bcert_geom
#print axioms OAI.PowerSaving.BG.bridge2_bcert
#print axioms SSC.PCert.Valid.bridge2_bcert
