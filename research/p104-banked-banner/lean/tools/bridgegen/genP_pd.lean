def sx (P w i : Nat) : Nat := (P / 2 ^ (w * i)) % 2 ^ w
def pipx (f : Nat) : Nat := sx PIK 11 f
def sF (k : Nat) : Nat := sx SFK 18 k
def sR (k : Nat) : Nat := sx SRK 14 k
def sO (p : Nat) : Nat := sx SOK 16 p
def sg (f : Nat) : Nat := sx SGK 11 f
def tu (p : Nat) : Nat := sx TUK 11 p
def dk (k : Nat) : Nat := sx DKK 32 k
def df (f : Nat) : Nat := sx DFK 40 f
def bk (k : Nat) : Nat := sx BKK 48 k
def nz (s : Nat) : Int := ((s % 65536 : Nat) : Int) - 32768
def dz (s : Nat) : Nat := s / 65536
def pw (e : Nat) : Int := ((2 ^ (72 * e) : Nat) : Int)
def fsl (k : Nat) : List Nat := List.range' (sF k) (sF (k+1) - sF k)
def rsl (k : Nat) : List Nat := List.range' (sR k) (sR (k+1) - sR k)
def osl (p : Nat) : List Nat := List.range' (sO p) (sO (p+1) - sO p)
def chkSF (n base fbw : Nat) : Bool := (List.range n).all fun u =>
  decide (sF (sx fbw 13 u) ≤ base + u) && decide (base + u < sF (sx fbw 13 u + 1))
def chkSR (n base rkw : Nat) : Bool := (List.range n).all fun u =>
  decide (sR (sx rkw 13 u) ≤ base + u) && decide (base + u < sR (sx rkw 13 u + 1))
def chkSO (n base ofw : Nat) : Bool := (List.range n).all fun u =>
  decide (sO (sg (sx ofw 11 u)) ≤ base + u) && decide (base + u < sO (sg (sx ofw 11 u) + 1))
theorem sF_mono : (List.range 5746).all (fun i => decide (sF i ≤ sF (i+1))) = true := by decide +kernel
theorem sR_mono : (List.range 5746).all (fun i => decide (sR i ≤ sR (i+1))) = true := by decide +kernel
theorem sO_mono : (List.range 1262).all (fun i => decide (sO i ≤ sO (i+1))) = true := by decide +kernel
theorem sF_end : sF 5746 ≤ 134078 := by decide +kernel
theorem sR_end : sR 5746 ≤ 11241 := by decide +kernel
theorem sO_end : sO 1262 ≤ 43106 := by decide +kernel
theorem sg_tu : (List.range 1262).all (fun x => decide (sg x < 1262) && tu (sg x) == x) = true := by decide +kernel
