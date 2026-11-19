noncomputable def cgT (tw : BT Nat) (w t : Nat) : Nat := sx (tw.get (t / 1500)) w (t % 1500)
noncomputable def fF (t : Nat) : Nat := cgT FFT 11 t
noncomputable def fC (t : Nat) : Nat := cgT FCT 32 t
noncomputable def rJ (t : Nat) : Nat := cgT RJT 13 t
noncomputable def rC (t : Nat) : Nat := cgT RCT 32 t
noncomputable def oJ (t : Nat) : Nat := cgT OJT 13 t
noncomputable def oC (t : Nat) : Nat := cgT OCT 32 t
noncomputable def mfz (k t : Nat) : Int := ((dk k : Int) * nz (fC t)) / ((dz (fC t) : Nat) : Int)
noncomputable def mrz (k t : Nat) : Int := ((dk k : Int) * nz (rC t)) / ((dz (rC t) * dk (rJ t) : Nat) : Int)
noncomputable def moz (f t : Nat) : Int := ((df f : Int) * nz (oC t)) / ((dz (oC t) * dk (oJ t) : Nat) : Int)
def mdd (f : Nat) : Int := ((df f : Int) * nz (sx ODK 32 f)) / ((dz (sx ODK 32 f) : Nat) : Int)
def mop (f : Nat) : Int := ((df f : Int) * nz (sx OPK 32 f)) / ((dz (sx OPK 32 f) : Nat) : Int)
noncomputable def fterm (b0 k t : Nat) : Int := if b0 ≤ fF t ∧ fF t < b0 + 256 then mfz k t * pw (fF t - b0) else 0
noncomputable def rterm (qt : BT Int) (k t : Nat) : Int := mrz k t * qt.get (rJ t)
noncomputable def chkBank (b0 : Nat) (qt : BT Int) (k : Nat) : Bool :=
  qt.get k == ((fsl k).map (fterm b0 k)).sum + ((rsl k).map (rterm qt k)).sum
noncomputable def oterm (qt : BT Int) (f t : Nat) : Int := moz f t * qt.get (oJ t)
def tgt (b0 f : Nat) : Int := (if b0 ≤ f ∧ f < b0 + 256 then mdd f * pw (f - b0) else 0) +
  (if nz (sx OPK 32 f) ≠ 0 ∧ b0 ≤ pipx f ∧ pipx f < b0 + 256 then mop f * pw (pipx f - b0) else 0)
noncomputable def chkOut (b0 : Nat) (qt : BT Int) (p : Nat) : Bool :=
  ((osl p).map (oterm qt (tu p))).sum == tgt b0 (tu p)
noncomputable def chkB (k : Nat) : Bool :=
  decide (0 < dk k) &&
  (fsl k).all (fun t => decide (0 < dz (fC t)) && ((dk k : Int) * nz (fC t)) % ((dz (fC t) : Nat) : Int) == 0) &&
  (rsl k).all (fun t => decide (0 < dz (rC t) * dk (rJ t)) &&
     ((dk k : Int) * nz (rC t)) % ((dz (rC t) * dk (rJ t) : Nat) : Int) == 0) &&
  decide (((fsl k).map (fun t => (mfz k t).natAbs)).sum + ((rsl k).map (fun t => (mrz k t).natAbs * bk (rJ t))).sum ≤ bk k)
noncomputable def chkOB (p : Nat) : Bool :=
  decide (0 < df (tu p)) && decide (0 < dz (sx ODK 32 (tu p))) && decide (0 < dz (sx OPK 32 (tu p))) &&
  ((df (tu p) : Int) * nz (sx ODK 32 (tu p))) % ((dz (sx ODK 32 (tu p)) : Nat) : Int) == 0 &&
  ((df (tu p) : Int) * nz (sx OPK 32 (tu p))) % ((dz (sx OPK 32 (tu p)) : Nat) : Int) == 0 &&
  (osl p).all (fun t => decide (0 < dz (oC t) * dk (oJ t)) &&
     ((df (tu p) : Int) * nz (oC t)) % ((dz (oC t) * dk (oJ t) : Nat) : Int) == 0) &&
  decide (((osl p).map (fun t => (moz (tu p) t).natAbs * bk (oJ t))).sum + (mdd (tu p)).natAbs + (mop (tu p)).natAbs < 2 ^ 72)
