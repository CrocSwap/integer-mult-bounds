import Mathproof.Meta.RamStd20261007
import Mathproof.Meta.Problem18RAMLax13ProofsSimulation20261001
import Mathlib.Tactic
set_option autoImplicit false
namespace Mathproof.WordRAMLogWidthTransfer20261022
open Lax51.BinaryWordEncoding

def ComputesInOn (D : List ℕ → Prop) (f : List ℕ → List ℕ)
    (p : RamStd.Program) (W T : ℕ → ℕ) : Prop :=
  ∀ x, D x →
    (∀ a ∈ (x.length :: x) ++ f x, a < 2 ^ W (bitSize x)) ∧
    ∀ w, W (bitSize x) ≤ w → ∃ t ≤ T (bitSize x),
      RamStd.RunsTo w p (x.length :: x) (f x) t

def BinaryWords (x : List ℕ) : Prop := ∀ a ∈ x, a ≤ 1

def LogWordTimeOn (D : List ℕ → Prop) (f : List ℕ → List ℕ) (T : ℕ → ℕ) : Prop :=
  ∃ (p : RamStd.Program) (c : ℕ),
    ComputesInOn D f p (fun n => c * (Nat.log2 (n + 2) + 1)) T

theorem computesIn_on {D f p W T} (h : RamStd.ComputesIn f p W T) :
    ComputesInOn D f p W T := fun x _ => h x

theorem computesInOn_mono {D E f p W T}
    (hDE : ∀ x, D x → E x) (h : ComputesInOn E f p W T) :
    ComputesInOn D f p W T := fun x hx => h x (hDE x hx)

theorem computesInOn_ofLax13 {D : List ℕ → Prop} {f : List ℕ → List ℕ}
    {p : Lax13.Ram.Program} {W T : ℕ → ℕ}
    (h : ∀ x, D x →
      (∀ a ∈ (x.length :: x) ++ f x, a < 2 ^ W (bitSize x)) ∧
      ∀ w, W (bitSize x) ≤ w → ∃ t ≤ T (bitSize x),
        Lax13.Ram.RunsTo w p (x.length :: x) (f x) t) :
    ComputesInOn D f (p.map RamStd.ofLax13) W T := by
  intro x hx
  refine ⟨(h x hx).1, ?_⟩
  intro w hw
  obtain ⟨t, ht, hr⟩ := (h x hx).2 w hw
  exact ⟨t, ht, RamStd.runsTo_ofLax13.mpr hr⟩

open Lax13Proofs.Compile Lax13Proofs.Imp Lax13Proofs.Simulation

theorem polynomial_fitsWords (L : Layout) {n B d a w : ℕ}
    (hB : 1 < B) (hpoly : B ≤ (n + 2) ^ d)
    (hconst : L.temps + 2 + L.scalars.length + L.arrays.length ≤ 2 ^ a)
    (hw : (d + a) * (Nat.log2 (n + 2) + 1) ≤ w) : L.FitsWords B w := by
  let ell := Nat.log2 (n + 2) + 1
  have hell : 1 ≤ ell := by dsimp [ell]; omega
  have hn : n + 2 ≤ 2 ^ ell := (Nat.lt_log2_self (n := n + 2)).le
  have hbp : B ≤ 2 ^ (d * ell) := by
    calc B ≤ (n + 2) ^ d := hpoly
      _ ≤ (2 ^ ell) ^ d := Nat.pow_le_pow_left hn d
      _ = 2 ^ (d * ell) := by rw [← pow_mul, Nat.mul_comm ell d]
  have hspan : L.span B ≤ 2 ^ a * B := by
    unfold Layout.span
    have h1 : L.temps + 2 + L.scalars.length ≤
        (L.temps + 2 + L.scalars.length) * B := Nat.le_mul_of_pos_right _ (by omega)
    calc L.temps + 2 + L.scalars.length + L.arrays.length * B
        ≤ (L.temps + 2 + L.scalars.length + L.arrays.length) * B := by nlinarith
      _ ≤ 2 ^ a * B := Nat.mul_le_mul_right B hconst
  have h_exp : a + d * ell ≤ w := by
    have ha : a ≤ a * ell := Nat.le_mul_of_pos_right _ (by omega)
    dsimp [ell] at *
    nlinarith
  have hbig : 2 ^ (a + d * ell) ≤ 2 ^ w := Nat.pow_le_pow_right (by omega) h_exp
  refine ⟨hB, ?_, ?_⟩
  · exact hbp.trans (Nat.pow_le_pow_right (by omega) (by omega))
  · calc L.span B ≤ 2 ^ a * B := hspan
      _ ≤ 2 ^ a * 2 ^ (d * ell) := Nat.mul_le_mul_left _ hbp
      _ = 2 ^ (a + d * ell) := (pow_add 2 a (d * ell)).symm
      _ ≤ 2 ^ w := hbig

theorem compiled_polynomial_run {L : Layout} {c : Com} {ext : String → ℕ}
    {x : List ℕ} {s : Env} {k n B d a w : ℕ}
    (hok : Com.Ok L c) (hB : 1 < B) (hpoly : B ≤ (n + 2) ^ d)
    (hconst : L.temps + 2 + L.scalars.length + L.arrays.length ≤ 2 ^ a)
    (hw : (d + a) * (Nat.log2 (n + 2) + 1) ≤ w)
    (hx : ∀ v ∈ x, v < B) (hr : BigStepB B c (initEnv ext x) s k) :
    ∃ t ≤ 10 * k, RamStd.RunsTo w ((compileProgram L c).map RamStd.ofLax13) x s.out t := by
  obtain ⟨t, ht, hrun⟩ := compileProgram_runsTo
    (polynomial_fitsWords L hB hpoly hconst hw) hok hx hr
  exact ⟨t, by simpa [Layout.const] using ht, RamStd.runsTo_ofLax13.mpr hrun⟩

end Mathproof.WordRAMLogWidthTransfer20261022
