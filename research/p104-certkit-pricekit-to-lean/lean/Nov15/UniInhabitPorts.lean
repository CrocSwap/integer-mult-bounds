/-
UniInhabitPorts (lane UNI-INHABIT, Nov 19).  Endpoint-chart mask checks for the 400 mains of t7669 (decide +kernel,
26-port chunks): x/x2 born at the port line {0,q}, ending at V; y/y2 born at {0}, ending at q^perp.
Port labels / non-D ports / dot are verbatim copies of UniFold7113.ports7113, nonD7113, SafeRungsClique.dot
(bridged by rfl in UniInhabitWord).  Core Lean only.
-/
import Nov15.UniInhabitFacts

namespace UniInhabit

def portsL : List Nat := [11, 19, 35, 131, 259, 13, 21, 37, 69, 133, 261, 41, 73, 265, 49, 81, 145, 273, 161, 193, 321, 385, 14, 22, 38, 70, 134, 262, 26, 74, 138, 50, 146, 274, 98, 290, 194, 322, 386, 28, 44, 140, 268, 84, 148, 276, 100, 164, 292, 196, 324, 388, 56, 88, 152, 280, 168, 296, 200, 328, 392, 112, 176, 304, 208, 336, 400, 224, 352, 416, 508, 506, 502, 494, 478, 446, 382, 254, 505, 501, 493, 477, 445, 381, 253, 499, 475, 443, 379, 251, 487, 471, 439, 375, 247, 463, 431, 367, 239, 415, 351, 223, 319, 191]
def nonDL : List Nat := [15, 17, 27, 34, 35, 42, 47, 55]
def labN (p : Nat) : Nat := portsL.getD p 0
def isDN (p : Nat) : Bool := !(nonDL.contains p)
def wtN (n : Nat) : Nat :=
  n % 2 + (n / 2) % 2 + (n / 4) % 2 + (n / 8) % 2 + (n / 16) % 2 + (n / 32) % 2 +
  (n / 64) % 2 + (n / 128) % 2 + (n / 256) % 2
def dotN (p q : Nat) : Nat := wtN (p &&& q) % 2
def mk (j : Nat) : Nat := gt 11 Tabs.maskT j
def fin7 (j : Nat) : Nat := lk Tabs.finP j
def ini7 (j : Nat) : Nat := lk Tabs.initP j

theorem xI_lt : ∀ p < 104, lk Tabs.xI p < 1501 ∧ lk Tabs.yI p < 1501 := by decide +kernel
theorem x2I_lt : ∀ p < 104, isDN p = true → lk Tabs.x2I p < 1501 ∧ lk Tabs.y2I p < 1501 := by decide +kernel

theorem lineM_0 : ∀ p < 13, 0 ≤ p → ∀ v < 512,
    Nat.testBit (mk (ini7 (lk Tabs.xI p))) v = decide (v = 0 ∨ v = labN p) ∧ Nat.testBit (mk (fin7 (lk Tabs.xI p))) v = true ∧
    Nat.testBit (mk (ini7 (lk Tabs.yI p))) v = decide (v = 0) ∧ Nat.testBit (mk (fin7 (lk Tabs.yI p))) v = decide (dotN v (labN p) = 0) := by decide +kernel
theorem lineD_0 : ∀ p < 13, 0 ≤ p → ∀ v < 512, isDN p = false ∨ (
    Nat.testBit (mk (ini7 (lk Tabs.x2I p))) v = decide (v = 0 ∨ v = labN p) ∧ Nat.testBit (mk (fin7 (lk Tabs.x2I p))) v = true ∧
    Nat.testBit (mk (ini7 (lk Tabs.y2I p))) v = decide (v = 0) ∧ Nat.testBit (mk (fin7 (lk Tabs.y2I p))) v = decide (dotN v (labN p) = 0)) := by decide +kernel
theorem lineM_1 : ∀ p < 26, 13 ≤ p → ∀ v < 512,
    Nat.testBit (mk (ini7 (lk Tabs.xI p))) v = decide (v = 0 ∨ v = labN p) ∧ Nat.testBit (mk (fin7 (lk Tabs.xI p))) v = true ∧
    Nat.testBit (mk (ini7 (lk Tabs.yI p))) v = decide (v = 0) ∧ Nat.testBit (mk (fin7 (lk Tabs.yI p))) v = decide (dotN v (labN p) = 0) := by decide +kernel
theorem lineD_1 : ∀ p < 26, 13 ≤ p → ∀ v < 512, isDN p = false ∨ (
    Nat.testBit (mk (ini7 (lk Tabs.x2I p))) v = decide (v = 0 ∨ v = labN p) ∧ Nat.testBit (mk (fin7 (lk Tabs.x2I p))) v = true ∧
    Nat.testBit (mk (ini7 (lk Tabs.y2I p))) v = decide (v = 0) ∧ Nat.testBit (mk (fin7 (lk Tabs.y2I p))) v = decide (dotN v (labN p) = 0)) := by decide +kernel
theorem lineM_2 : ∀ p < 39, 26 ≤ p → ∀ v < 512,
    Nat.testBit (mk (ini7 (lk Tabs.xI p))) v = decide (v = 0 ∨ v = labN p) ∧ Nat.testBit (mk (fin7 (lk Tabs.xI p))) v = true ∧
    Nat.testBit (mk (ini7 (lk Tabs.yI p))) v = decide (v = 0) ∧ Nat.testBit (mk (fin7 (lk Tabs.yI p))) v = decide (dotN v (labN p) = 0) := by decide +kernel
theorem lineD_2 : ∀ p < 39, 26 ≤ p → ∀ v < 512, isDN p = false ∨ (
    Nat.testBit (mk (ini7 (lk Tabs.x2I p))) v = decide (v = 0 ∨ v = labN p) ∧ Nat.testBit (mk (fin7 (lk Tabs.x2I p))) v = true ∧
    Nat.testBit (mk (ini7 (lk Tabs.y2I p))) v = decide (v = 0) ∧ Nat.testBit (mk (fin7 (lk Tabs.y2I p))) v = decide (dotN v (labN p) = 0)) := by decide +kernel
theorem lineM_3 : ∀ p < 52, 39 ≤ p → ∀ v < 512,
    Nat.testBit (mk (ini7 (lk Tabs.xI p))) v = decide (v = 0 ∨ v = labN p) ∧ Nat.testBit (mk (fin7 (lk Tabs.xI p))) v = true ∧
    Nat.testBit (mk (ini7 (lk Tabs.yI p))) v = decide (v = 0) ∧ Nat.testBit (mk (fin7 (lk Tabs.yI p))) v = decide (dotN v (labN p) = 0) := by decide +kernel
theorem lineD_3 : ∀ p < 52, 39 ≤ p → ∀ v < 512, isDN p = false ∨ (
    Nat.testBit (mk (ini7 (lk Tabs.x2I p))) v = decide (v = 0 ∨ v = labN p) ∧ Nat.testBit (mk (fin7 (lk Tabs.x2I p))) v = true ∧
    Nat.testBit (mk (ini7 (lk Tabs.y2I p))) v = decide (v = 0) ∧ Nat.testBit (mk (fin7 (lk Tabs.y2I p))) v = decide (dotN v (labN p) = 0)) := by decide +kernel
theorem lineM_4 : ∀ p < 65, 52 ≤ p → ∀ v < 512,
    Nat.testBit (mk (ini7 (lk Tabs.xI p))) v = decide (v = 0 ∨ v = labN p) ∧ Nat.testBit (mk (fin7 (lk Tabs.xI p))) v = true ∧
    Nat.testBit (mk (ini7 (lk Tabs.yI p))) v = decide (v = 0) ∧ Nat.testBit (mk (fin7 (lk Tabs.yI p))) v = decide (dotN v (labN p) = 0) := by decide +kernel
theorem lineD_4 : ∀ p < 65, 52 ≤ p → ∀ v < 512, isDN p = false ∨ (
    Nat.testBit (mk (ini7 (lk Tabs.x2I p))) v = decide (v = 0 ∨ v = labN p) ∧ Nat.testBit (mk (fin7 (lk Tabs.x2I p))) v = true ∧
    Nat.testBit (mk (ini7 (lk Tabs.y2I p))) v = decide (v = 0) ∧ Nat.testBit (mk (fin7 (lk Tabs.y2I p))) v = decide (dotN v (labN p) = 0)) := by decide +kernel
theorem lineM_5 : ∀ p < 78, 65 ≤ p → ∀ v < 512,
    Nat.testBit (mk (ini7 (lk Tabs.xI p))) v = decide (v = 0 ∨ v = labN p) ∧ Nat.testBit (mk (fin7 (lk Tabs.xI p))) v = true ∧
    Nat.testBit (mk (ini7 (lk Tabs.yI p))) v = decide (v = 0) ∧ Nat.testBit (mk (fin7 (lk Tabs.yI p))) v = decide (dotN v (labN p) = 0) := by decide +kernel
theorem lineD_5 : ∀ p < 78, 65 ≤ p → ∀ v < 512, isDN p = false ∨ (
    Nat.testBit (mk (ini7 (lk Tabs.x2I p))) v = decide (v = 0 ∨ v = labN p) ∧ Nat.testBit (mk (fin7 (lk Tabs.x2I p))) v = true ∧
    Nat.testBit (mk (ini7 (lk Tabs.y2I p))) v = decide (v = 0) ∧ Nat.testBit (mk (fin7 (lk Tabs.y2I p))) v = decide (dotN v (labN p) = 0)) := by decide +kernel
theorem lineM_6 : ∀ p < 91, 78 ≤ p → ∀ v < 512,
    Nat.testBit (mk (ini7 (lk Tabs.xI p))) v = decide (v = 0 ∨ v = labN p) ∧ Nat.testBit (mk (fin7 (lk Tabs.xI p))) v = true ∧
    Nat.testBit (mk (ini7 (lk Tabs.yI p))) v = decide (v = 0) ∧ Nat.testBit (mk (fin7 (lk Tabs.yI p))) v = decide (dotN v (labN p) = 0) := by decide +kernel
theorem lineD_6 : ∀ p < 91, 78 ≤ p → ∀ v < 512, isDN p = false ∨ (
    Nat.testBit (mk (ini7 (lk Tabs.x2I p))) v = decide (v = 0 ∨ v = labN p) ∧ Nat.testBit (mk (fin7 (lk Tabs.x2I p))) v = true ∧
    Nat.testBit (mk (ini7 (lk Tabs.y2I p))) v = decide (v = 0) ∧ Nat.testBit (mk (fin7 (lk Tabs.y2I p))) v = decide (dotN v (labN p) = 0)) := by decide +kernel
theorem lineM_7 : ∀ p < 104, 91 ≤ p → ∀ v < 512,
    Nat.testBit (mk (ini7 (lk Tabs.xI p))) v = decide (v = 0 ∨ v = labN p) ∧ Nat.testBit (mk (fin7 (lk Tabs.xI p))) v = true ∧
    Nat.testBit (mk (ini7 (lk Tabs.yI p))) v = decide (v = 0) ∧ Nat.testBit (mk (fin7 (lk Tabs.yI p))) v = decide (dotN v (labN p) = 0) := by decide +kernel
theorem lineD_7 : ∀ p < 104, 91 ≤ p → ∀ v < 512, isDN p = false ∨ (
    Nat.testBit (mk (ini7 (lk Tabs.x2I p))) v = decide (v = 0 ∨ v = labN p) ∧ Nat.testBit (mk (fin7 (lk Tabs.x2I p))) v = true ∧
    Nat.testBit (mk (ini7 (lk Tabs.y2I p))) v = decide (v = 0) ∧ Nat.testBit (mk (fin7 (lk Tabs.y2I p))) v = decide (dotN v (labN p) = 0)) := by decide +kernel

theorem lineM : ∀ p < 104, ∀ v < 512,
    Nat.testBit (mk (ini7 (lk Tabs.xI p))) v = decide (v = 0 ∨ v = labN p) ∧ Nat.testBit (mk (fin7 (lk Tabs.xI p))) v = true ∧
    Nat.testBit (mk (ini7 (lk Tabs.yI p))) v = decide (v = 0) ∧ Nat.testBit (mk (fin7 (lk Tabs.yI p))) v = decide (dotN v (labN p) = 0) := by
  intro p hp

  by_cases h0 : p < 13
  · exact lineM_0 p h0 (by omega)

  by_cases h1 : p < 26
  · exact lineM_1 p h1 (by omega)

  by_cases h2 : p < 39
  · exact lineM_2 p h2 (by omega)

  by_cases h3 : p < 52
  · exact lineM_3 p h3 (by omega)

  by_cases h4 : p < 65
  · exact lineM_4 p h4 (by omega)

  by_cases h5 : p < 78
  · exact lineM_5 p h5 (by omega)

  by_cases h6 : p < 91
  · exact lineM_6 p h6 (by omega)

  by_cases h7 : p < 104
  · exact lineM_7 p h7 (by omega)

  omega


theorem lineD : ∀ p < 104, ∀ v < 512, isDN p = false ∨ (
    Nat.testBit (mk (ini7 (lk Tabs.x2I p))) v = decide (v = 0 ∨ v = labN p) ∧ Nat.testBit (mk (fin7 (lk Tabs.x2I p))) v = true ∧
    Nat.testBit (mk (ini7 (lk Tabs.y2I p))) v = decide (v = 0) ∧ Nat.testBit (mk (fin7 (lk Tabs.y2I p))) v = decide (dotN v (labN p) = 0)) := by
  intro p hp

  by_cases h0 : p < 13
  · exact lineD_0 p h0 (by omega)

  by_cases h1 : p < 26
  · exact lineD_1 p h1 (by omega)

  by_cases h2 : p < 39
  · exact lineD_2 p h2 (by omega)

  by_cases h3 : p < 52
  · exact lineD_3 p h3 (by omega)

  by_cases h4 : p < 65
  · exact lineD_4 p h4 (by omega)

  by_cases h5 : p < 78
  · exact lineD_5 p h5 (by omega)

  by_cases h6 : p < 91
  · exact lineD_6 p h6 (by omega)

  by_cases h7 : p < 104
  · exact lineD_7 p h7 (by omega)

  omega

end UniInhabit
