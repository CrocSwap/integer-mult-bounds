/-
UniFold7113Inst (lane UNI-L2B, Nov 19).  Non-vacuity of UniFold7113.foldBanked7113: the concrete #7113 caller of the
words t7669 (GEN/STACK/t7669.json.gz) and w_s4 (REBUILDKIT/alt/r7/w_s4.json.gz) -- both files have the SAME `ports`
(= ports7113) and the SAME `hosted.Dports` (96; non-D ports 15,17,27,34,35,42,47,55), public = 1501 = 400 mains +
1101 helpers, owned_fields = 68.  `caller7113 : Caller (Fin 104)` with all caller facts by decide; Ports7113 + DCount by
decide; hence `bankedT7669` / `bankedWs4` : every legal trace with those register types whose end state is a Word
(+ the three verifier clauses) folds to a BankedGraph.  Kernel data tie-in: UniCtl.ctl_t7669 / ctl_ws4 (bank counts
6157 / 6250, fold P = pricekit P).  CAVEAT: the 150k-event traces themselves are not replayed in the kernel.
Kernel only: no sorry, no native_decide, no new axioms.
-/
import Nov15.UniFold7113
import Nov15.UniCtl

namespace UniFold7113
open Finset WordModel Uni SafeRungsClique

/-- the 8 B (non-D) ports of the #7113 caller (indices into ports7113). -/
def nonD7113 : List ℕ := [15, 17, 27, 34, 35, 42, 47, 55]

def lab7113 (p : Fin 104) : ℕ := ports7113.getD p.1 0
def isD7113 (p : Fin 104) : Bool := !(nonD7113.contains p.1)

theorem lab7113_lt : ∀ p, lab7113 p < 512 := by decide +kernel
theorem lab7113_odd : ∀ p, wt (lab7113 p) % 2 = 1 := by decide +kernel
theorem lab7113_inj : Function.Injective lab7113 := by
  have : ∀ a b : Fin 104, lab7113 a = lab7113 b → a = b := by decide +kernel
  exact fun a b => this a b
theorem lab7113_Q : ∀ q ∈ Q, ∃ p, lab7113 p = q := by decide +kernel

/-- the #7113 caller (ports + D/B split of t7669 and w_s4). -/
def caller7113 : Caller (Fin 104) where
  lab := lab7113
  isD := isD7113
  lab_lt := lab7113_lt
  lab_odd := lab7113_odd
  lab_inj := lab7113_inj
  card104 := Fintype.card_fin 104
  Q_sub := lab7113_Q

theorem ports_caller7113 : Ports7113 caller7113 := by
  unfold Ports7113; decide +kernel

theorem dcount_caller7113 : DCount caller7113 := by
  unfold DCount; decide +kernel

/-- t7669 instance (helpers Fin 1101, owned Fin 68). -/
noncomputable def bankedT7669 {tr : Trace (Reg (Fin 104) (Fin 1101) (Fin 68))} (h : Legal (pub caller7113) tr)
    (hw : Word caller7113 (exec tr)) (hfr : FramesSubsp (exec tr)) (hcs : ChartsSubsp (exec tr))
    (hn : OwnedNested (exec tr)) :
    BankFit.BankedGraph ℚ (Fld (pub (Hl := Fin 1101) (Ow := Fin 68) caller7113)) (Fin (mlog tr).length) :=
  foldBanked7113 caller7113 ports_caller7113 dcount_caller7113 h hw hfr hcs hn

/-- w_s4 instance (same caller and register types as t7669). -/
noncomputable def bankedWs4 {tr : Trace (Reg (Fin 104) (Fin 1101) (Fin 68))} (h : Legal (pub caller7113) tr)
    (hw : Word caller7113 (exec tr)) (hfr : FramesSubsp (exec tr)) (hcs : ChartsSubsp (exec tr))
    (hn : OwnedNested (exec tr)) :
    BankFit.BankedGraph ℚ (Fld (pub (Hl := Fin 1101) (Ow := Fin 68) caller7113)) (Fin (mlog tr).length) :=
  foldBanked7113 caller7113 ports_caller7113 dcount_caller7113 h hw hfr hcs hn

/-- control tie-in: both words' caller premises hold and their folded bank lists (UniCtl data) price as pricekit. -/
theorem inst7113_ctl : Ports7113 caller7113 ∧ DCount caller7113 ∧
    (UniCtl.t7669Banks.length = 6157 ∧ UniCtl.pHist UniCtl.t7669Banks = UniCtl.t7669PK) ∧
    (UniCtl.ws4Banks.length = 6250 ∧ UniCtl.pHist UniCtl.ws4Banks = UniCtl.ws4PK) :=
  ⟨ports_caller7113, dcount_caller7113, UniCtl.ctl_t7669, UniCtl.ctl_ws4⟩

end UniFold7113

#print axioms UniFold7113.caller7113
#print axioms UniFold7113.ports_caller7113
#print axioms UniFold7113.dcount_caller7113
#print axioms UniFold7113.bankedT7669
#print axioms UniFold7113.bankedWs4
#print axioms UniFold7113.inst7113_ctl
