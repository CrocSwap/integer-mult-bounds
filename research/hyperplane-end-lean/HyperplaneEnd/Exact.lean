/-
Hypothesis (N) proved for the hyperplane-end pairs of the HPE words, and `hpe_word` without (N).

(N) for a pair `(E, U)` is the exact identity `T_U T_E⁻¹ = L_{E,U} (C ⊗ id) R_{E,U}` on
`ℂ^128 ⊗ ℂ^4 ≅ ℂ^512` (9 qubits; the `C` factor acts on qubits 0–6, the spectators are 7, 8):
* `T_F` is `canonical_frame(9, F)` of `hpe/vendor/clifford/clifford_exact.py` (`canon`, a port of
  `basis_extend`, `inv` and the quadratic form `Q`), for a frame given by its basis rows;
* `L_{E,U}`, `R_{E,U}` are `monomial_op` of the `"E:U"` recipe in `RESIDUAL-ADAPTERS.json`
  (`Mono.gates`: diagonal, permutation, `X`, phase);
* `C = C₇ = fourier(7)`, the product of the seven `C` gates.
Every HPE word (ck, atm3, jp8 of the v2 local runs; the same three recipes appear in every
`RESIDUAL-ADAPTERS.json` of the HPE runs) uses the same three `(E, U)` pairs, so the nine
word/pair identities are the three theorems `exact_N_pair1/2/3` (`exact_N_nine`).  Each is
checked by the kernel with `Clifford.check` (`decide +kernel`, no `native_decide`).

`hpe_word_exact` is `hpe_word` for these operators with (N) discharged: its only extra hypothesis
is that the helper's `(entrance, terminal)` pair is one of the certified pairs.
Apache-2.0.  Prepared with Claude Opus 5.5 (Anthropic) in omp; submitted by jeremykothe2.
-/
import HyperplaneEnd.Clifford
import HyperplaneEnd.Main

namespace HyperplaneEnd.Exact

open HyperplaneEnd.Clifford TensorProduct Complex

/-! ## Ports of `canonical_frame` and `monomial_op` (`clifford_exact.py`, `adapters_local.py`) -/

/-- `transpose(rows, n)`, column `i`. -/
def colBits (i : ℕ) : List ℕ → ℕ → ℕ
  | [], _ => 0
  | r :: rs, w => (if (r >>> i) % 2 = 1 then w else 0) + colBits i rs (2 * w)

def transpose (rows : List ℕ) (n : ℕ) : List ℕ := (List.range n).map fun i => colBits i rows 1

/-- `x.bit_length() - 1` for `0 < x < 2 ^ 64`. -/
def lead : ℕ → ℕ → ℕ
  | 0, _ => 0
  | f + 1, x => if x < 2 then 0 else lead f (x / 2) + 1

/-- One step of `rank`: insert `x` into the pivot table (leading bit ↦ row). -/
def insPiv : ℕ → List (ℕ × ℕ) → ℕ → List (ℕ × ℕ)
  | 0, p, _ => p
  | f + 1, p, x =>
    if x = 0 then p else
    match p.lookup (lead 64 x) with
    | none => (lead 64 x, x) :: p
    | some r => insPiv f p (x ^^^ r)

def rank (rows : List ℕ) : ℕ := (rows.foldl (insPiv 64) []).length

def basisExtend (cols : List ℕ) (n : ℕ) : List ℕ :=
  (cols ++ (List.range n).map (2 ^ ·)).foldl
    (fun out x => if rank (out ++ [x]) > out.length then out ++ [x] else out) []

/-- `inv(rows, n)`: Gauss–Jordan over `F₂` (the result is certified by `Gate.ok`). -/
def invRows (n : ℕ) (rows : List ℕ) : List ℕ :=
  let a0 := (List.range n).map fun i => rows.getD i 0 ||| (2 ^ (n + i))
  let a := (List.range n).foldl (fun a j =>
    match (List.range n).find? (fun i => decide (j ≤ i) && (a.getD i 0 >>> j) % 2 == 1) with
    | none => a
    | some k =>
      let a := (a.set j (a.getD k 0)).set k (a.getD j 0)
      let pj := a.getD j 0
      (List.range n).map fun i =>
        let ai := a.getD i 0
        if i ≠ j ∧ (ai >>> j) % 2 = 1 then ai ^^^ pj else ai) a0
  a.map (· >>> n)

/-- `fourier(n, range(r))`. -/
def fourierC (r : ℕ) : List Gate := (List.range r).map fun i => .cg (2 ^ i) true

/-- `canonical_frame(n, U)`: `K⁻¹ · fourier(r) · K` with `K = perm(G) then diag(Q)`. -/
def canon (n : ℕ) (U : List ℕ) : List Gate :=
  let r := U.length
  if r = 0 then [] else if r = n then fourierC n else
  let G := transpose (basisExtend U n) n
  let Gi := invRows n G
  let gt := transpose Gi n
  let Q := (List.range n).map fun i =>
    2 ^ i ^^^ ((List.range n).map fun j => if par9 (gt.getD i 0 &&& gt.getD j 0) then 2 ^ j else 0).sum
  let α := (List.range n).map fun i => (Q.getD i 0 >>> i) % 2
  let K := [Gate.pm G Gi, Gate.dg Q α]
  adjC K ++ fourierC r ++ K

/-- A serialized wrapper monomial: `quadratic_rows`, `linear_Z4`, `matrix_rows`, `offset`, `phase`. -/
structure Mono where
  Q : List ℕ
  α : List ℕ
  G : List ℕ
  b : ℕ
  p : ℕ
  deriving DecidableEq

/-- `monomial_op(rec)`: `diag(Q, α)`, then `perm(G)`, then `X(offset)`, then the phase. -/
def Mono.gates (r : Mono) : List Gate := [.dg r.Q r.α, .pm r.G (invRows 9 r.G), .xg r.b, .ph r.p]

/-- An `(E, U)` pair with its `"E:U"` recipe (`left` = `L`, `right` = `R`). -/
structure Pair where
  E : List ℕ
  U : List ℕ
  L : Mono
  R : Mono
  deriving DecidableEq

/-! ## The certified pairs (from `RESIDUAL-ADAPTERS.json`) -/

/-- `(E, U)` pair 1 (ck frames 437:1079). -/
def pair1 : Pair := ⟨[45], [256, 128, 64, 33, 16, 9, 5, 2],
  ⟨[5, 0, 5, 0, 0, 0, 0, 0, 0], [3, 2, 3, 2, 2, 2, 2, 0, 0], [128, 2, 261, 1, 8, 4, 16, 32, 64], 0, 0⟩,
  ⟨[12, 0, 1, 41, 0, 40, 0, 0, 0], [2, 2, 0, 3, 2, 3, 2, 2, 2], [44, 2, 4, 16, 64, 128, 256, 13, 32], 511, 1⟩⟩

/-- `(E, U)` pair 2 (ck frames 438:1080). -/
def pair2 : Pair := ⟨[51], [256, 128, 64, 33, 17, 8, 4, 3],
  ⟨[3, 3, 0, 0, 0, 0, 0, 0, 0], [3, 3, 2, 2, 2, 2, 2, 0, 0], [128, 259, 4, 8, 1, 2, 16, 32, 64], 0, 0⟩,
  ⟨[18, 1, 0, 0, 49, 48, 0, 0, 0], [2, 0, 2, 2, 3, 3, 2, 2, 2], [50, 2, 4, 8, 64, 128, 256, 19, 32], 511, 1⟩⟩

/-- `(E, U)` pair 3 (ck frames 439:1081). -/
def pair3 : Pair := ⟨[30], [256, 128, 64, 32, 18, 10, 6, 1],
  ⟨[0, 6, 6, 0, 0, 0, 0, 0, 0], [2, 3, 3, 2, 2, 2, 2, 0, 0], [1, 128, 262, 2, 4, 8, 16, 32, 64], 0, 0⟩,
  ⟨[0, 12, 2, 26, 24, 0, 0, 0, 0], [2, 2, 0, 3, 3, 2, 2, 2, 2], [1, 28, 4, 32, 64, 128, 256, 14, 16], 511, 1⟩⟩

def pairs : List Pair := [pair1, pair2, pair3]

/-- The `(E, U)` pairs of the three HPE words: `(word, E index, U index, E rows, U rows)`. -/
def nineInstances : List (String × ℕ × ℕ × List ℕ × List ℕ) :=
  [("ck", 437, 1079, pair1.E, pair1.U), ("ck", 438, 1080, pair2.E, pair2.U),
   ("ck", 439, 1081, pair3.E, pair3.U), ("atm3", 437, 1079, pair1.E, pair1.U),
   ("atm3", 438, 1080, pair2.E, pair2.U), ("atm3", 439, 1081, pair3.E, pair3.U),
   ("jp8", 421, 998, pair1.E, pair1.U), ("jp8", 422, 999, pair2.E, pair2.U),
   ("jp8", 423, 1000, pair3.E, pair3.U)]

def findPair (E U : List ℕ) : Option Pair := pairs.find? fun p => p.E == E && p.U == U

/-! ## The operators on `ℂ^512` -/

/-- `canonical_frame(9, F)` as a linear equivalence (identity if its gate data were invalid,
which `cOk` rules out for every frame used below). -/
noncomputable def frameOp (F : List ℕ) : (Fin 512 → ℂ) ≃ₗ[ℂ] (Fin 512 → ℂ) :=
  if h : cOk 512 (canon 9 F) = true then cE _ h else LinearEquiv.refl ℂ _

noncomputable def monoOp (r : Mono) : (Fin 512 → ℂ) ≃ₗ[ℂ] (Fin 512 → ℂ) :=
  if h : cOk 512 r.gates = true then cE _ h else LinearEquiv.refl ℂ _

noncomputable def lwOp (E U : List ℕ) : (Fin 512 → ℂ) ≃ₗ[ℂ] (Fin 512 → ℂ) :=
  match findPair E U with
  | some p => monoOp p.L
  | none => LinearEquiv.refl ℂ _

noncomputable def rwOp (E U : List ℕ) : (Fin 512 → ℂ) ≃ₗ[ℂ] (Fin 512 → ℂ) :=
  match findPair E U with
  | some p => monoOp p.R
  | none => LinearEquiv.refl ℂ _

/-! ## Transport to `A ⊗ B` (`A` = qubits 0–6, `B` = qubits 7–8) -/

abbrev A := Fin 128 → ℂ
abbrev B := Fin 4 → ℂ

/-- `x ↦ (x mod 128, x / 128)`. -/
def split : Fin 512 ≃ Fin 128 × Fin 4 where
  toFun x := (fx 128 x.val, fx 4 (x.val / 128))
  invFun p := ⟨p.1.val + 128 * p.2.val, by omega⟩
  left_inv x := by ext; simp [fx]; omega
  right_inv p := by
    ext <;> simp [fx]
    all_goals omega

/-- `A ⊗ B ≅ ℂ^512`, `a ⊗ b ↦ (x ↦ a(x mod 128) b(x / 128))`. -/
noncomputable def eT : (A ⊗[ℂ] B) ≃ₗ[ℂ] (Fin 512 → ℂ) :=
  ((Pi.basisFun ℂ (Fin 128)).tensorProduct (Pi.basisFun ℂ (Fin 4))).equivFun.trans
    (LinearEquiv.funCongrLeft ℂ ℂ split)

theorem eT_tmul (a : A) (b : B) (x : Fin 512) : eT (a ⊗ₜ b) x = a (split x).1 * b (split x).2 := by
  simp only [eT, LinearEquiv.trans_apply, LinearEquiv.funCongrLeft_apply, LinearMap.funLeft_apply,
    Basis.equivFun_apply]
  rw [show split x = ((split x).1, (split x).2) from rfl, Basis.tensorProduct_repr_tmul_apply,
    Pi.basisFun_repr, Pi.basisFun_repr, smul_eq_mul, mul_comm]

/-- An operator on `ℂ^512` read on `A ⊗ B`. -/
noncomputable def conj (f : (Fin 512 → ℂ) ≃ₗ[ℂ] (Fin 512 → ℂ)) : (A ⊗[ℂ] B) ≃ₗ[ℂ] (A ⊗[ℂ] B) :=
  eT.trans (f.trans eT.symm)

/-- The frame family `T_F = canonical_frame(9, F)` on `A ⊗ B`. -/
noncomputable def T (F : List ℕ) : (A ⊗[ℂ] B) ≃ₗ[ℂ] (A ⊗[ℂ] B) := conj (frameOp F)

/-- The wrapper monomials `L_{E,U}` and `R_{E,U}` on `A ⊗ B`. -/
noncomputable def Lw (E U : List ℕ) : (A ⊗[ℂ] B) ≃ₗ[ℂ] (A ⊗[ℂ] B) := conj (lwOp E U)
noncomputable def Rw (E U : List ℕ) : (A ⊗[ℂ] B) ≃ₗ[ℂ] (A ⊗[ℂ] B) := conj (rwOp E U)

/-- The residual `C₇ = fourier(7)` on the 7 coordinate qubits. -/
noncomputable def C7 : A →ₗ[ℂ] A := cL 128 (fourierC 7)

/-- Bit facts for a `C` gate on qubit `i < 7` of 9 qubits. -/
theorem split_xor : ∀ i : Fin 7, ∀ x : Fin 512,
    (x.val ^^^ 2 ^ i.val) % 512 % 128 = (x.val % 128 ^^^ 2 ^ i.val) % 128 ∧
      (x.val ^^^ 2 ^ i.val) % 512 / 128 % 4 = x.val / 128 % 4 := by
  decide +kernel

theorem rTensor_cg (i : Fin 7) (t : A ⊗[ℂ] B) :
    eT ((gL 128 (.cg (2 ^ i.val) true)).rTensor B t) = gL 512 (.cg (2 ^ i.val) true) (eT t) := by
  induction t using TensorProduct.induction_on with
  | zero => simp
  | tmul a b =>
    rw [LinearMap.rTensor_tmul]
    funext x
    obtain ⟨h1, h2⟩ := split_xor i x
    simp only [eT_tmul, gL_apply, gC, split, Equiv.coe_fn_mk]
    have e1 : fx 128 (fx 512 (x.val ^^^ 2 ^ i.val)).val = fx 128 ((fx 128 x.val).val ^^^ 2 ^ i.val) :=
      Fin.ext (by simpa [fx] using h1)
    have e2 : fx 4 ((fx 512 (x.val ^^^ 2 ^ i.val)).val / 128) = fx 4 (x.val / 128) :=
      Fin.ext (by simpa [fx] using h2)
    rw [e1, e2]
    ring
  | add s t hs ht => simp [map_add, hs, ht]

theorem rTensor_C7 (t : A ⊗[ℂ] B) : eT (C7.rTensor B t) = cL 512 (fourierC 7) (eT t) := by
  suffices ∀ c : List Gate, (∀ g ∈ c, ∃ i : Fin 7, g = .cg (2 ^ i.val) true) →
      ∀ t, eT ((cL 128 c).rTensor B t) = cL 512 c (eT t) by
    refine this _ (fun g hg => ?_) t
    simp only [fourierC, List.mem_map, List.mem_range] at hg
    obtain ⟨i, hi, rfl⟩ := hg
    exact ⟨⟨i, hi⟩, rfl⟩
  intro c hc
  induction c with
  | nil => intro t; simp [cL_nil]
  | cons g c ih =>
    intro t
    obtain ⟨i, rfl⟩ := hc g (List.mem_cons_self ..)
    rw [cL_cons, LinearMap.rTensor_comp, LinearMap.comp_apply, ih (fun g hg => hc g
      (List.mem_cons_of_mem _ hg)), rTensor_cg, cL_cons, LinearMap.comp_apply]

/-! ## (N) from the kernel checks -/

theorem frameOp_of_ok (F : List ℕ) (h : cOk 512 (canon 9 F) = true) : frameOp F = cE _ h := by
  unfold frameOp; rw [dif_pos h]

theorem monoOp_of_ok (r : Mono) (h : cOk 512 r.gates = true) : monoOp r = cE _ h := by
  unfold monoOp; rw [dif_pos h]

/-- The two sides of (N) as circuits: `T_E⁻¹` then `T_U`, versus `R`, `C₇ ⊗ id`, `L`. -/
def lhsC (p : Pair) : List Gate := adjC (canon 9 p.E) ++ canon 9 p.U
def rhsC (p : Pair) : List Gate := p.R.gates ++ fourierC 7 ++ p.L.gates

/-- (N) for a pair whose gate data are valid and whose two circuits pass `check`. -/
theorem exact_N_of_check (p : Pair) (hf : findPair p.E p.U = some p)
    (hE : cOk 512 (canon 9 p.E) = true) (hU : cOk 512 (canon 9 p.U) = true)
    (hL : cOk 512 p.L.gates = true) (hR : cOk 512 p.R.gates = true)
    (hc : check (lhsC p) (rhsC p) = true) (v : A ⊗[ℂ] B) :
    T p.U ((T p.E).symm v) = Lw p.E p.U (C7.rTensor B (Rw p.E p.U v)) := by
  have key := LinearMap.congr_fun (cL_eq_of_check _ _ hc) (eT v)
  rw [lhsC, rhsC, cL_append_apply, cL_append_apply, cL_append_apply] at key
  have hl : lwOp p.E p.U = monoOp p.L := by unfold lwOp; rw [hf]
  have hr : rwOp p.E p.U = monoOp p.R := by unfold rwOp; rw [hf]
  unfold T Lw Rw conj
  rw [hl, hr, frameOp_of_ok _ hE, frameOp_of_ok _ hU, monoOp_of_ok _ hL, monoOp_of_ok _ hR]
  simp only [LinearEquiv.trans_apply, LinearEquiv.symm_trans_apply, LinearEquiv.symm_symm,
    LinearEquiv.apply_symm_apply, cE_apply, cE_symm_apply, rTensor_C7]
  rw [key]

/-! ### The kernel checks

`canon`, `invRows` and `Mono.gates` are evaluated once into gate literals (`fE1 … rhsLit3`,
generated from `clifford_exact.py` and proved equal by the kernel); `cOk` and `check` then run on
the literals, so the kernel never re-evaluates a frame computation per basis state. -/

/-- `canon 9 pair1.E`, evaluated. -/
def fE1 : List Gate :=
  [.dg [32, 0, 32, 32, 0, 45, 0, 0, 0] [0, 0, 0, 0, 0, 3, 0, 0, 0],
   .pm [32, 33, 2, 36, 40, 16, 64, 128, 256] [3, 4, 9, 17, 32, 1, 64, 128, 256],
   .cg 1 true,
   .pm [3, 4, 9, 17, 32, 1, 64, 128, 256] [32, 33, 2, 36, 40, 16, 64, 128, 256],
   .dg [32, 0, 32, 32, 0, 45, 0, 0, 0] [0, 0, 0, 0, 0, 1, 0, 0, 0]]

/-- `canon 9 pair1.U`, evaluated. -/
def fU1 : List Gate :=
  [.dg [44, 0, 45, 45, 0, 45, 0, 0, 0] [0, 0, 3, 3, 0, 3, 0, 0, 0],
   .pm [256, 128, 64, 32, 16, 8, 4, 2, 45] [360, 128, 64, 32, 16, 8, 4, 2, 1],
   .cg 1 true,
   .cg 2 true,
   .cg 4 true,
   .cg 8 true,
   .cg 16 true,
   .cg 32 true,
   .cg 64 true,
   .cg 128 true,
   .pm [360, 128, 64, 32, 16, 8, 4, 2, 1] [256, 128, 64, 32, 16, 8, 4, 2, 45],
   .dg [44, 0, 45, 45, 0, 45, 0, 0, 0] [0, 0, 1, 1, 0, 1, 0, 0, 0]]

/-- `pair1.L.gates`, evaluated. -/
def wL1 : List Gate :=
  [.dg [5, 0, 5, 0, 0, 0, 0, 0, 0] [3, 2, 3, 2, 2, 2, 2, 0, 0],
   .pm [128, 2, 261, 1, 8, 4, 16, 32, 64] [8, 2, 32, 16, 64, 128, 256, 1, 44],
   .xg 0,
   .ph 0]

/-- `pair1.R.gates`, evaluated. -/
def wR1 : List Gate :=
  [.dg [12, 0, 1, 41, 0, 40, 0, 0, 0] [2, 2, 0, 3, 2, 3, 2, 2, 2],
   .pm [44, 2, 4, 16, 64, 128, 256, 13, 32] [385, 2, 4, 261, 8, 256, 16, 32, 64],
   .xg 511,
   .ph 1]

/-- `lhsC pair1`, evaluated. -/
def lhsLit1 : List Gate :=
  [.dg [32, 0, 32, 32, 0, 45, 0, 0, 0] [0, 0, 0, 0, 0, 3, 0, 0, 0],
   .pm [32, 33, 2, 36, 40, 16, 64, 128, 256] [3, 4, 9, 17, 32, 1, 64, 128, 256],
   .cg 1 false,
   .pm [3, 4, 9, 17, 32, 1, 64, 128, 256] [32, 33, 2, 36, 40, 16, 64, 128, 256],
   .dg [32, 0, 32, 32, 0, 45, 0, 0, 0] [0, 0, 0, 0, 0, 1, 0, 0, 0],
   .dg [44, 0, 45, 45, 0, 45, 0, 0, 0] [0, 0, 3, 3, 0, 3, 0, 0, 0],
   .pm [256, 128, 64, 32, 16, 8, 4, 2, 45] [360, 128, 64, 32, 16, 8, 4, 2, 1],
   .cg 1 true,
   .cg 2 true,
   .cg 4 true,
   .cg 8 true,
   .cg 16 true,
   .cg 32 true,
   .cg 64 true,
   .cg 128 true,
   .pm [360, 128, 64, 32, 16, 8, 4, 2, 1] [256, 128, 64, 32, 16, 8, 4, 2, 45],
   .dg [44, 0, 45, 45, 0, 45, 0, 0, 0] [0, 0, 1, 1, 0, 1, 0, 0, 0]]

/-- `rhsC pair1`, evaluated. -/
def rhsLit1 : List Gate :=
  [.dg [12, 0, 1, 41, 0, 40, 0, 0, 0] [2, 2, 0, 3, 2, 3, 2, 2, 2],
   .pm [44, 2, 4, 16, 64, 128, 256, 13, 32] [385, 2, 4, 261, 8, 256, 16, 32, 64],
   .xg 511,
   .ph 1,
   .cg 1 true,
   .cg 2 true,
   .cg 4 true,
   .cg 8 true,
   .cg 16 true,
   .cg 32 true,
   .cg 64 true,
   .dg [5, 0, 5, 0, 0, 0, 0, 0, 0] [3, 2, 3, 2, 2, 2, 2, 0, 0],
   .pm [128, 2, 261, 1, 8, 4, 16, 32, 64] [8, 2, 32, 16, 64, 128, 256, 1, 44],
   .xg 0,
   .ph 0]

/-- `canon 9 pair2.E`, evaluated. -/
def fE2 : List Gate :=
  [.dg [32, 32, 0, 0, 32, 51, 0, 0, 0] [0, 0, 0, 0, 0, 3, 0, 0, 0],
   .pm [32, 33, 34, 4, 8, 48, 64, 128, 256] [3, 5, 8, 16, 33, 1, 64, 128, 256],
   .cg 1 true,
   .pm [3, 5, 8, 16, 33, 1, 64, 128, 256] [32, 33, 34, 4, 8, 48, 64, 128, 256],
   .dg [32, 32, 0, 0, 32, 51, 0, 0, 0] [0, 0, 0, 0, 0, 1, 0, 0, 0]]

/-- `canon 9 pair2.U`, evaluated. -/
def fU2 : List Gate :=
  [.dg [50, 51, 0, 0, 51, 51, 0, 0, 0] [0, 3, 0, 0, 3, 3, 0, 0, 0],
   .pm [256, 128, 64, 32, 16, 8, 4, 2, 51] [408, 128, 64, 32, 16, 8, 4, 2, 1],
   .cg 1 true,
   .cg 2 true,
   .cg 4 true,
   .cg 8 true,
   .cg 16 true,
   .cg 32 true,
   .cg 64 true,
   .cg 128 true,
   .pm [408, 128, 64, 32, 16, 8, 4, 2, 1] [256, 128, 64, 32, 16, 8, 4, 2, 51],
   .dg [50, 51, 0, 0, 51, 51, 0, 0, 0] [0, 1, 0, 0, 1, 1, 0, 0, 0]]

/-- `pair2.L.gates`, evaluated. -/
def wL2 : List Gate :=
  [.dg [3, 3, 0, 0, 0, 0, 0, 0, 0] [3, 3, 2, 2, 2, 2, 2, 0, 0],
   .pm [128, 259, 4, 8, 1, 2, 16, 32, 64] [16, 32, 4, 8, 64, 128, 256, 1, 50],
   .xg 0,
   .ph 0]

/-- `pair2.R.gates`, evaluated. -/
def wR2 : List Gate :=
  [.dg [18, 1, 0, 0, 49, 48, 0, 0, 0] [2, 0, 2, 2, 3, 3, 2, 2, 2],
   .pm [50, 2, 4, 8, 64, 128, 256, 19, 32] [385, 2, 4, 8, 259, 256, 16, 32, 64],
   .xg 511,
   .ph 1]

/-- `lhsC pair2`, evaluated. -/
def lhsLit2 : List Gate :=
  [.dg [32, 32, 0, 0, 32, 51, 0, 0, 0] [0, 0, 0, 0, 0, 3, 0, 0, 0],
   .pm [32, 33, 34, 4, 8, 48, 64, 128, 256] [3, 5, 8, 16, 33, 1, 64, 128, 256],
   .cg 1 false,
   .pm [3, 5, 8, 16, 33, 1, 64, 128, 256] [32, 33, 34, 4, 8, 48, 64, 128, 256],
   .dg [32, 32, 0, 0, 32, 51, 0, 0, 0] [0, 0, 0, 0, 0, 1, 0, 0, 0],
   .dg [50, 51, 0, 0, 51, 51, 0, 0, 0] [0, 3, 0, 0, 3, 3, 0, 0, 0],
   .pm [256, 128, 64, 32, 16, 8, 4, 2, 51] [408, 128, 64, 32, 16, 8, 4, 2, 1],
   .cg 1 true,
   .cg 2 true,
   .cg 4 true,
   .cg 8 true,
   .cg 16 true,
   .cg 32 true,
   .cg 64 true,
   .cg 128 true,
   .pm [408, 128, 64, 32, 16, 8, 4, 2, 1] [256, 128, 64, 32, 16, 8, 4, 2, 51],
   .dg [50, 51, 0, 0, 51, 51, 0, 0, 0] [0, 1, 0, 0, 1, 1, 0, 0, 0]]

/-- `rhsC pair2`, evaluated. -/
def rhsLit2 : List Gate :=
  [.dg [18, 1, 0, 0, 49, 48, 0, 0, 0] [2, 0, 2, 2, 3, 3, 2, 2, 2],
   .pm [50, 2, 4, 8, 64, 128, 256, 19, 32] [385, 2, 4, 8, 259, 256, 16, 32, 64],
   .xg 511,
   .ph 1,
   .cg 1 true,
   .cg 2 true,
   .cg 4 true,
   .cg 8 true,
   .cg 16 true,
   .cg 32 true,
   .cg 64 true,
   .dg [3, 3, 0, 0, 0, 0, 0, 0, 0] [3, 3, 2, 2, 2, 2, 2, 0, 0],
   .pm [128, 259, 4, 8, 1, 2, 16, 32, 64] [16, 32, 4, 8, 64, 128, 256, 1, 50],
   .xg 0,
   .ph 0]

/-- `canon 9 pair3.E`, evaluated. -/
def fE3 : List Gate :=
  [.dg [0, 16, 16, 16, 30, 0, 0, 0, 0] [0, 0, 0, 0, 3, 0, 0, 0, 0],
   .pm [16, 1, 18, 20, 24, 32, 64, 128, 256] [2, 5, 9, 17, 1, 32, 64, 128, 256],
   .cg 1 true,
   .pm [2, 5, 9, 17, 1, 32, 64, 128, 256] [16, 1, 18, 20, 24, 32, 64, 128, 256],
   .dg [0, 16, 16, 16, 30, 0, 0, 0, 0] [0, 0, 0, 0, 1, 0, 0, 0, 0]]

/-- `canon 9 pair3.U`, evaluated. -/
def fU3 : List Gate :=
  [.dg [0, 28, 30, 30, 30, 0, 0, 0, 0] [0, 0, 3, 3, 3, 0, 0, 0, 0],
   .pm [256, 128, 64, 32, 16, 8, 4, 1, 30] [128, 368, 64, 32, 16, 8, 4, 2, 1],
   .cg 1 true,
   .cg 2 true,
   .cg 4 true,
   .cg 8 true,
   .cg 16 true,
   .cg 32 true,
   .cg 64 true,
   .cg 128 true,
   .pm [128, 368, 64, 32, 16, 8, 4, 2, 1] [256, 128, 64, 32, 16, 8, 4, 1, 30],
   .dg [0, 28, 30, 30, 30, 0, 0, 0, 0] [0, 0, 1, 1, 1, 0, 0, 0, 0]]

/-- `pair3.L.gates`, evaluated. -/
def wL3 : List Gate :=
  [.dg [0, 6, 6, 0, 0, 0, 0, 0, 0] [2, 3, 3, 2, 2, 2, 2, 0, 0],
   .pm [1, 128, 262, 2, 4, 8, 16, 32, 64] [1, 8, 16, 32, 64, 128, 256, 2, 28],
   .xg 0,
   .ph 0]

/-- `pair3.R.gates`, evaluated. -/
def wR3 : List Gate :=
  [.dg [0, 12, 2, 26, 24, 0, 0, 0, 0] [2, 2, 0, 3, 3, 2, 2, 2, 2],
   .pm [1, 28, 4, 32, 64, 128, 256, 14, 16] [1, 386, 4, 262, 256, 8, 16, 32, 64],
   .xg 511,
   .ph 1]

/-- `lhsC pair3`, evaluated. -/
def lhsLit3 : List Gate :=
  [.dg [0, 16, 16, 16, 30, 0, 0, 0, 0] [0, 0, 0, 0, 3, 0, 0, 0, 0],
   .pm [16, 1, 18, 20, 24, 32, 64, 128, 256] [2, 5, 9, 17, 1, 32, 64, 128, 256],
   .cg 1 false,
   .pm [2, 5, 9, 17, 1, 32, 64, 128, 256] [16, 1, 18, 20, 24, 32, 64, 128, 256],
   .dg [0, 16, 16, 16, 30, 0, 0, 0, 0] [0, 0, 0, 0, 1, 0, 0, 0, 0],
   .dg [0, 28, 30, 30, 30, 0, 0, 0, 0] [0, 0, 3, 3, 3, 0, 0, 0, 0],
   .pm [256, 128, 64, 32, 16, 8, 4, 1, 30] [128, 368, 64, 32, 16, 8, 4, 2, 1],
   .cg 1 true,
   .cg 2 true,
   .cg 4 true,
   .cg 8 true,
   .cg 16 true,
   .cg 32 true,
   .cg 64 true,
   .cg 128 true,
   .pm [128, 368, 64, 32, 16, 8, 4, 2, 1] [256, 128, 64, 32, 16, 8, 4, 1, 30],
   .dg [0, 28, 30, 30, 30, 0, 0, 0, 0] [0, 0, 1, 1, 1, 0, 0, 0, 0]]

/-- `rhsC pair3`, evaluated. -/
def rhsLit3 : List Gate :=
  [.dg [0, 12, 2, 26, 24, 0, 0, 0, 0] [2, 2, 0, 3, 3, 2, 2, 2, 2],
   .pm [1, 28, 4, 32, 64, 128, 256, 14, 16] [1, 386, 4, 262, 256, 8, 16, 32, 64],
   .xg 511,
   .ph 1,
   .cg 1 true,
   .cg 2 true,
   .cg 4 true,
   .cg 8 true,
   .cg 16 true,
   .cg 32 true,
   .cg 64 true,
   .dg [0, 6, 6, 0, 0, 0, 0, 0, 0] [2, 3, 3, 2, 2, 2, 2, 0, 0],
   .pm [1, 128, 262, 2, 4, 8, 16, 32, 64] [1, 8, 16, 32, 64, 128, 256, 2, 28],
   .xg 0,
   .ph 0]

theorem find1 : findPair pair1.E pair1.U = some pair1 := by decide +kernel
theorem find2 : findPair pair2.E pair2.U = some pair2 := by decide +kernel
theorem find3 : findPair pair3.E pair3.U = some pair3 := by decide +kernel

theorem lits1 : canon 9 pair1.E = fE1 ∧ canon 9 pair1.U = fU1 ∧ pair1.L.gates = wL1 ∧
    pair1.R.gates = wR1 ∧ lhsC pair1 = lhsLit1 ∧ rhsC pair1 = rhsLit1 := by decide +kernel
theorem lits2 : canon 9 pair2.E = fE2 ∧ canon 9 pair2.U = fU2 ∧ pair2.L.gates = wL2 ∧
    pair2.R.gates = wR2 ∧ lhsC pair2 = lhsLit2 ∧ rhsC pair2 = rhsLit2 := by decide +kernel
theorem lits3 : canon 9 pair3.E = fE3 ∧ canon 9 pair3.U = fU3 ∧ pair3.L.gates = wL3 ∧
    pair3.R.gates = wR3 ∧ lhsC pair3 = lhsLit3 ∧ rhsC pair3 = rhsLit3 := by decide +kernel

theorem ok1 : cOk 512 fE1 = true ∧ cOk 512 fU1 = true ∧ cOk 512 wL1 = true ∧ cOk 512 wR1 = true := by
  decide +kernel
theorem ok2 : cOk 512 fE2 = true ∧ cOk 512 fU2 = true ∧ cOk 512 wL2 = true ∧ cOk 512 wR2 = true := by
  decide +kernel
theorem ok3 : cOk 512 fE3 = true ∧ cOk 512 fU3 = true ∧ cOk 512 wL3 = true ∧ cOk 512 wR3 = true := by
  decide +kernel

theorem check1 : check lhsLit1 rhsLit1 = true := by decide +kernel
theorem check2 : check lhsLit2 rhsLit2 = true := by decide +kernel
theorem check3 : check lhsLit3 rhsLit3 = true := by decide +kernel

/-- (N) from the literal checks of a pair. -/
theorem exact_N_of_lits (p : Pair) (hf : findPair p.E p.U = some p) {fE fU wL wR lhs rhs : List Gate}
    (hl : canon 9 p.E = fE ∧ canon 9 p.U = fU ∧ p.L.gates = wL ∧ p.R.gates = wR ∧ lhsC p = lhs ∧
      rhsC p = rhs)
    (hok : cOk 512 fE = true ∧ cOk 512 fU = true ∧ cOk 512 wL = true ∧ cOk 512 wR = true)
    (hc : check lhs rhs = true) (v : A ⊗[ℂ] B) :
    T p.U ((T p.E).symm v) = Lw p.E p.U (C7.rTensor B (Rw p.E p.U v)) := by
  obtain ⟨h1, h2, h3, h4, h5, h6⟩ := hl
  obtain ⟨k1, k2, k3, k4⟩ := hok
  exact exact_N_of_check p hf (h1 ▸ k1) (h2 ▸ k2) (h3 ▸ k3) (h4 ▸ k4) (h5 ▸ h6 ▸ hc) v

/-- **(N) for pair 1**, exactly, global phase included. -/
theorem exact_N_pair1 (v : A ⊗[ℂ] B) :
    T pair1.U ((T pair1.E).symm v) = Lw pair1.E pair1.U (C7.rTensor B (Rw pair1.E pair1.U v)) :=
  exact_N_of_lits pair1 find1 lits1 ok1 check1 v

theorem exact_N_pair2 (v : A ⊗[ℂ] B) :
    T pair2.U ((T pair2.E).symm v) = Lw pair2.E pair2.U (C7.rTensor B (Rw pair2.E pair2.U v)) :=
  exact_N_of_lits pair2 find2 lits2 ok2 check2 v

theorem exact_N_pair3 (v : A ⊗[ℂ] B) :
    T pair3.U ((T pair3.E).symm v) = Lw pair3.E pair3.U (C7.rTensor B (Rw pair3.E pair3.U v)) :=
  exact_N_of_lits pair3 find3 lits3 ok3 check3 v

/-- (N) for every certified pair. -/
theorem exact_N {E U : List ℕ} (h : (E, U) ∈ pairs.map fun p => (p.E, p.U)) (v : A ⊗[ℂ] B) :
    T U ((T E).symm v) = Lw E U (C7.rTensor B (Rw E U v)) := by
  simp only [pairs, List.map_cons, List.map_nil, List.mem_cons, Prod.mk.injEq,
    List.not_mem_nil, or_false] at h
  rcases h with ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩
  · exact exact_N_pair1 v
  · exact exact_N_pair2 v
  · exact exact_N_pair3 v

/-- Every word/pair instance is a certified pair. -/
theorem nine_mem : ∀ q ∈ nineInstances, (q.2.2.2.1, q.2.2.2.2) ∈ pairs.map fun p => (p.E, p.U) := by
  decide +kernel

/-- **The nine word/pair identities** of the HPE words ck, atm3 and jp8. -/
theorem exact_N_nine : ∀ q ∈ nineInstances, ∀ v : A ⊗[ℂ] B,
    T q.2.2.2.2 ((T q.2.2.2.1).symm v) =
      Lw q.2.2.2.1 q.2.2.2.2 (C7.rTensor B (Rw q.2.2.2.1 q.2.2.2.2 v)) :=
  fun q hq v => exact_N (nine_mem q hq) v

/-! ## `hpe_word` without (N) -/

open LemmaG LemmaG.Stream LemmaA

/-- **The HPE word, with (N) proved.**  `hpe_word` for the tools' operators: frames are basis
lists, `T_F = canonical_frame(9, F)`, the wrappers are the `"E:U"` recipes and the residual is
`C₇ ⊗ id`.  The exact factorization is no longer a hypothesis; the helper's pair only has to be
one of the certified pairs (`exact_N`). -/
theorem hpe_word_exact {ι : Type*} [DecidableEq ι] [Fintype ι]
    {Fam G Cc W : Type*} [DecidableEq Fam] [Group G] [DecidableEq G]
    [AddCommMonoid W] [Module ℂ W] (ent term : ι → List ℕ)
    (fam : ι → Fam) (σ : ι → G) (d : G)
    (fp : G → Set Cc) (hne : ∀ r, (fp (σ r)).Nonempty)
    (hdis : ∀ r r', r ≠ r' → fam r = fam r' → Disjoint (fp (σ r)) (fp (σ r')))
    (chart : ι → W ≃ₗ[ℂ] (A ⊗[ℂ] B))
    (rec : XLab ι (List ℕ) → XLab ι (List ℕ) → A ⊗[ℂ] B → A ⊗[ℂ] B)
    (h p : ι) (hp : h ≠ p) (Ah Ap : List ℕ) (q : ℂ) (l : ι → XLab ι (List ℕ))
    (a b : List (Event ι (XLab ι (List ℕ)) ℂ)) (y : Fam × G → W)
    (ha : WellLabelled a l) (lh : labRun a l h = .frame Ah) (lp : labRun a l p = .frame Ap)
    (hb : WellLabelled b (labRun (a ++ tail h p Ah Ap (term h) q) l))
    (hmv : ∀ e ∈ b, ¬ e.moves h)
    (hrec : RecipesExact (Text T ent term Lw Rw) rec
      (a ++ tail h p Ah Ap (term h) q ++ b ++ [.relabel h (.frame (term h)) (.done h)]))
    (hS : ∀ s, S (a ++ tail h p Ah Ap (term h) q ++ b ++ [.relabel h (.frame (term h)) (.done h)])
      h s = if s = h then 1 else 0)
    (hstart : l h = .prew h)
    (hpair : (ent h, term h) ∈ pairs.map fun p => (p.E, p.U)) :
    realizeRun ⟨streamOwner fam σ d, chart⟩ rec
        (a ++ tail h p Ah Ap (term h) q ++ b ++ [.relabel h (.frame (term h)) (.done h)]) y
        (streamOwner fam σ d h) =
      (chart h).symm (C7.rTensor B (chart h (y (streamOwner fam σ d h)))) :=
  hpe_word T ent term Lw Rw fam σ d fp hne hdis chart rec h p hp Ah Ap q l a b y ha lh lp hb hmv
    hrec hS hstart C7 (exact_N hpair)

end HyperplaneEnd.Exact
