import Mathlib.Data.ZMod.Basic
import Mathlib.Data.Fintype.Pi
import Mathlib.Algebra.BigOperators.Fin
/-!
FRAMECERT (LEANFRAME, Nov 20).  Kernel-only (no native_decide, no sorry, no new axioms).
Discharges AllOrNothing.H_frame for the REAL P104 data:
  ports = Fin 104 (labels in F2^9), frames = the 759 8-subsets (bitmasks), F^perp = vectors even on every frame.
  For each of the 1152 7-dim frame-blocking subspaces S (given by two normals u1,u2 in F2^9; Lam = ports whose
  label is orthogonal to both), every x in F^perp supported in Lam is 0 or 1_Lam.
Certificate: for each Lam, frames sel with restrictions of rank |Lam|-1, and for every p in Lam\{p0} a
  F2-combination c of sel whose restriction to Lam is exactly {p,p0}; the kernel check is a Nat-bitmask
  `decide +kernel`.  Soundness (reflection lemma) is proved once.  This file embeds AllOrNothing verbatim
  (no cross-file imports in Nov15/) and instantiates it.
Data (frames, labels, certificates) come from cards/WILD/NOVEL/leanframe/gen.py, an exact F2 elimination.
-/
set_option Elab.async false
namespace FrameCert
