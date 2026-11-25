/-
Exact Clifford circuits on `n` qubits and a kernel-checkable equality test for them.

The HPE tools (`hpe/vendor/clifford/clifford_exact.py`) represent every operator of hypothesis
(N) as a literal circuit of five gate kinds acting on state vectors indexed by `x < 2 ^ n`
(bit `i` of `x` is qubit `i`):
* `P G`      `v'(G x) = v(x)`  for an invertible `G` over `F₂` (rows as bitmasks);
* `D Q α`    `v'(x) = i ^ q(x) v(x)`, `q(x) = Σ_{i ∈ x} α_i + 2 Σ_{i ∈ x} ⟨Q_i ≫ (i+1), x ≫ (i+1)⟩ mod 4`;
* `C q s`    `v'(x) = ((1 + s i) v(x) + (1 - s i) v(x ⊕ q)) / 2`,  `s = ±1`;
* `X b`      `v'(x) = v(x ⊕ b)`;
* `phase p`  `v' = i ^ p v`.
This file gives the same gates exact semantics over `ℂ` (`gC`, `gL`, `cL`), proves that the
inverse gates invert them (`cE`), and proves `cL_eq_of_check`: if the Boolean `check c₁ c₂`
evaluates to `true` then the two circuits are equal linear maps on `ℂ^512`, global phase included.

`check` runs both circuits once, over `ℤ[i]` with the `1/2` of every `C` gate dropped, on the single
vector `u(x) = B ^ x` (`B = 4 ^ (#C(c₁) + 1)`); by linearity this computes every column of both
matrices at once, packed in base `B`, and the entry bound `|entry| ≤ 4 ^ #C` makes the packing
injective.  The packed integers are a few thousand bits, so the kernel evaluates `check` with its
GMP-backed `Nat` operations; no `native_decide` is used.
Apache-2.0.  Prepared with Claude Opus 5.5 (Anthropic) in omp; submitted by jeremykothe2.
-/
import Mathlib.LinearAlgebra.TensorProduct.Basis
import Mathlib.LinearAlgebra.StdBasis
import Mathlib.Data.Complex.Basic
import Mathlib.Algebra.Order.Group.Unbundled.Int
import Mathlib.Algebra.BigOperators.Fin
import Mathlib.Tactic.IntervalCases
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Ring

namespace HyperplaneEnd.Clifford

/-! ## Bit helpers (ports of `clifford_exact.py`; all data are 9-bit masks) -/

/-- Parity of the low `k` bits of `x`. -/
def par : ℕ → ℕ → Bool
  | 0, _ => false
  | k + 1, x => (x % 2 == 1) ^^ par k (x / 2)

/-- `parity` of `clifford_exact.py` for arguments below `2 ^ 12` (every argument here is a 9-bit
mask): `x ^ (x >> 4) ^ (x >> 8)` folds the low 12 bits into a nibble with the same parity, and
`0x6996` is the parity table of nibbles.  This uses only GMP-backed kernel operations; `par9_spec`
checks it against the bit-by-bit `par 9` on 9-bit arguments. -/
def par9 (x : ℕ) : Bool := (0x6996 >>> ((x ^^^ (x >>> 4) ^^^ (x >>> 8)) &&& 15)) % 2 == 1

theorem par9_spec : ∀ x : Fin 512, par9 x.val = par 9 x.val := by decide +kernel

def mvAux : List ℕ → ℕ → ℕ → ℕ
  | [], _, _ => 0
  | r :: rs, x, w => (if par9 (r &&& x) then w else 0) + mvAux rs x (2 * w)

/-- `mv(rows, x) = Σ_i parity(rows[i] & x) << i`: the `F₂`-linear map with the given rows. -/
def mv (rows : List ℕ) (x : ℕ) : ℕ := mvAux rows x 1

def qvAux : List ℕ → List ℕ → ℕ → ℕ → ℕ
  | q :: qs, a :: as, x, i =>
      (if (x >>> i) % 2 = 1 then
        a + 2 * (if par9 ((q >>> (i + 1)) &&& (x >>> (i + 1))) then 1 else 0) else 0) +
      qvAux qs as x (i + 1)
  | _, _, _, _ => 0

/-- `qvalue(Q, alpha, x)` of `clifford_exact.py`: the `ℤ/4` exponent of a diagonal gate. -/
def qv (Q α : List ℕ) (x : ℕ) : ℕ := qvAux Q α x 0 % 4

/-! ## Gates and circuits -/

/-- The circuit elements of `clifford_exact.Op.circuit`.  `pm G Gi` is `P G` together with the
inverse matrix `Gi`; it is read as `v'(y) = v(Gi y)`, which is `P G` whenever `Gi = G⁻¹`
(checked by `Gate.ok`).  `cg q s` is `C q (if s then 1 else -1)`. -/
inductive Gate
  | pm (G Gi : List ℕ)
  | dg (Q α : List ℕ)
  | cg (q : ℕ) (s : Bool)
  | xg (b : ℕ)
  | ph (p : ℕ)
  deriving Repr, DecidableEq

/-- The inverse gate, as `Op.adjoint` builds it. -/
def Gate.adj : Gate → Gate
  | .pm G Gi => .pm Gi G
  | .dg Q α => .dg Q (α.map fun a => (4 - a % 4) % 4)
  | .cg q s => .cg q (!s)
  | .xg b => .xg b
  | .ph p => .ph ((4 - p % 4) % 4)

/-- `Op.adjoint` on circuits (circuits run left to right). -/
def adjC (c : List Gate) : List Gate := (c.map Gate.adj).reverse

/-- Number of `C` gates. -/
def ncg : List Gate → ℕ
  | [] => 0
  | .cg _ _ :: c => ncg c + 1
  | _ :: c => ncg c

/-- Decidable side conditions under which `Gate.adj` inverts a gate on `N` basis states. -/
def Gate.ok (N : ℕ) : Gate → Bool
  | .pm G Gi => (List.range N).all fun x =>
      mv Gi (mv G x % N) % N == x && mv G (mv Gi x % N) % N == x
  | .dg Q α => (List.range N).all fun x =>
      (qv Q α x + qv Q (α.map fun a => (4 - a % 4) % 4) x) % 4 == 0
  | .cg q _ => (List.range N).all fun x => ((x ^^^ q) % N ^^^ q) % N == x
  | .xg b => (List.range N).all fun x => ((x ^^^ b) % N ^^^ b) % N == x
  | .ph _ => true

def cOk (N : ℕ) (c : List Gate) : Bool := c.all (Gate.ok N)

/-! ## Integer semantics: `ℤ[i]` as `ℤ × ℤ`, `C` gates without their `1/2` -/

/-- Multiplication by `i ^ k`. -/
def ipow (k : ℕ) (z : ℤ × ℤ) : ℤ × ℤ :=
  match k % 4 with
  | 0 => z
  | 1 => (-z.2, z.1)
  | 2 => (-z.1, -z.2)
  | _ => (z.2, -z.1)

/-- `(1 + s i) a + (1 - s i) c`. -/
def cgz (s : Bool) (a c : ℤ × ℤ) : ℤ × ℤ :=
  if s then (a.1 - a.2 + c.1 + c.2, a.2 + a.1 + c.2 - c.1)
  else (a.1 + a.2 + c.1 - c.2, a.2 - a.1 + c.2 + c.1)

/-- One gate on `ℕ`-indexed vectors (`2 ^ #C`-scaled for `C` gates). -/
def gz (N : ℕ) : Gate → (ℕ → ℤ × ℤ) → ℕ → ℤ × ℤ
  | .pm _ Gi, v, x => v (mv Gi x % N)
  | .dg Q α, v, x => ipow (qv Q α x) (v x)
  | .cg q s, v, x => cgz s (v x) (v ((x ^^^ q) % N))
  | .xg b, v, x => v ((x ^^^ b) % N)
  | .ph p, v, x => ipow p (v x)

def runZ (N : ℕ) (c : List Gate) (v : ℕ → ℤ × ℤ) : ℕ → ℤ × ℤ := c.foldl (fun v g => gz N g v) v

/-! ## Kernel evaluation: perfect binary trees -/

inductive Tr
  | lf (a : ℤ × ℤ)
  | nd (l r : Tr)

def Tr.ofFn (f : ℕ → ℤ × ℤ) : ℕ → Tr
  | 0 => .lf (f 0)
  | d + 1 => .nd (Tr.ofFn (fun i => f (2 * i)) d) (Tr.ofFn (fun i => f (2 * i + 1)) d)

def Tr.get : Tr → ℕ → ℤ × ℤ
  | .lf a, _ => a
  | .nd l r, x => if x % 2 = 0 then l.get (x / 2) else r.get (x / 2)

/-- `t₁ = k • t₂` entrywise, on trees of the same shape. -/
def Tr.beqS (k : ℤ) : Tr → Tr → Bool
  | .lf a, .lf b => a.1 == k * b.1 && a.2 == k * b.2
  | .nd l r, .nd l' r' => Tr.beqS k l l' && Tr.beqS k r r'
  | _, _ => false

/-- A circuit on `512 = 2 ^ 9` basis states, one materialized tree per gate. -/
def runT (c : List Gate) (t : Tr) : Tr := c.foldl (fun t g => Tr.ofFn (gz 512 g t.get) 9) t

/-- The packed equality test: `c₁` and `c₂` (with `#C(c₂) ≤ #C(c₁)`) agree on `ℂ^512` iff
`2^{#C(c₁)} M₁ = 2^{#C(c₁) - #C(c₂)} · 2^{#C(c₂)} M₂` over `ℤ[i]`; both sides are evaluated on
`u(x) = B ^ x`. -/
def check (c₁ c₂ : List Gate) : Bool :=
  let B : ℤ := 4 ^ (ncg c₁ + 1)
  let t := Tr.ofFn (fun k => (B ^ k, 0)) 9
  ncg c₂ ≤ ncg c₁ && Tr.beqS (2 ^ (ncg c₁ - ncg c₂)) (runT c₁ t) (runT c₂ t)

/-! ## Exact semantics over `ℂ` -/

open Complex

/-- The basis state `k mod N`. -/
def fx (N : ℕ) [NeZero N] (k : ℕ) : Fin N := ⟨k % N, Nat.mod_lt _ (NeZero.pos N)⟩

def sg (s : Bool) : ℂ := if s then 1 else -1

variable (N : ℕ) [NeZero N]

/-- One gate on `ℂ^N`. -/
noncomputable def gC : Gate → (Fin N → ℂ) → Fin N → ℂ
  | .pm _ Gi, v, x => v (fx N (mv Gi x.val))
  | .dg Q α, v, x => I ^ qv Q α x.val * v x
  | .cg q s, v, x => ((1 + sg s * I) * v x + (1 - sg s * I) * v (fx N (x.val ^^^ q))) / 2
  | .xg b, v, x => v (fx N (x.val ^^^ b))
  | .ph p, v, x => I ^ p * v x

/-- One gate as a `ℂ`-linear map. -/
noncomputable def gL (g : Gate) : (Fin N → ℂ) →ₗ[ℂ] (Fin N → ℂ) where
  toFun := gC N g
  map_add' v w := by funext x; cases g <;> simp [gC] <;> ring
  map_smul' a v := by funext x; cases g <;> simp [gC] <;> ring

/-- A circuit as a `ℂ`-linear map; the head gate is applied first. -/
noncomputable def cL : List Gate → (Fin N → ℂ) →ₗ[ℂ] (Fin N → ℂ)
  | [] => LinearMap.id
  | g :: c => cL c ∘ₗ gL N g

variable {N}

theorem gL_apply (g : Gate) (v : Fin N → ℂ) : gL N g v = gC N g v := rfl

theorem cL_nil : cL N [] = LinearMap.id := rfl

theorem cL_cons (g : Gate) (c : List Gate) : cL N (g :: c) = cL N c ∘ₗ gL N g := rfl

theorem cL_append (c d : List Gate) : cL N (c ++ d) = cL N d ∘ₗ cL N c := by
  induction c with
  | nil => simp [cL_nil]
  | cons g c ih => simp [cL_cons, ih, LinearMap.comp_assoc]

theorem cL_append_apply (c d : List Gate) (w : Fin N → ℂ) : cL N (c ++ d) w = cL N d (cL N c w) := by
  rw [cL_append, LinearMap.comp_apply]

/-! ### Inverses -/

theorem I_pow_of_mod (k : ℕ) (h : k % 4 = 0) : I ^ k = 1 := by
  obtain ⟨m, rfl⟩ : ∃ m, k = 4 * m := ⟨k / 4, by omega⟩
  rw [pow_mul, show I ^ 4 = 1 by rw [show (4 : ℕ) = 2 * 2 from rfl, pow_mul, I_sq]; norm_num, one_pow]

theorem I_pow_mod (k : ℕ) : I ^ k = I ^ (k % 4) := by
  conv_lhs => rw [← Nat.div_add_mod k 4, pow_add, pow_mul]
  rw [show I ^ 4 = 1 by rw [show (4 : ℕ) = 2 * 2 from rfl, pow_mul, I_sq]; norm_num, one_pow, one_mul]

theorem fx_val (k : ℕ) : (fx N k).val = k % N := rfl

theorem fx_of_lt {k : ℕ} (x : Fin N) (h : k % N = x.val) : fx N k = x := Fin.ext h

theorem all_range {N : ℕ} {p : ℕ → Bool} (h : (List.range N).all p = true) (x : Fin N) :
    p x.val = true := by
  rw [List.all_eq_true] at h
  exact h _ (List.mem_range.2 x.isLt)

theorem sg_not (s : Bool) : sg (!s) = - sg s := by cases s <;> simp [sg]

theorem sg_sq (s : Bool) : sg s * sg s = 1 := by cases s <;> simp [sg]

/-- `Gate.adj` is a two-sided inverse under `Gate.ok`. -/
theorem gL_adj (g : Gate) (h : g.ok N = true) :
    gL N g.adj ∘ₗ gL N g = LinearMap.id ∧ gL N g ∘ₗ gL N g.adj = LinearMap.id := by
  cases g with
  | pm G Gi =>
    constructor <;> refine LinearMap.ext fun v => funext fun x => ?_ <;>
      simp only [Gate.adj, LinearMap.comp_apply, gL_apply, gC, LinearMap.id_apply] <;>
      have hx := all_range h x <;> simp only [Bool.and_eq_true, beq_iff_eq] at hx <;>
      congr 1 <;> apply fx_of_lt <;> simp only [fx_val] <;> [exact hx.1; exact hx.2]
  | dg Q α =>
    constructor <;> refine LinearMap.ext fun v => funext fun x => ?_ <;>
      simp only [Gate.adj, LinearMap.comp_apply, gL_apply, gC, LinearMap.id_apply] <;>
      have hx := all_range h x <;> simp only [beq_iff_eq] at hx <;>
      rw [← mul_assoc, ← pow_add, I_pow_of_mod _ (by omega), one_mul]
  | cg q s =>
    have hx : ∀ x : Fin N, fx N ((fx N (x.val ^^^ q)).val ^^^ q) = x := fun x =>
      fx_of_lt x (by simpa [fx_val] using all_range h x)
    constructor <;> refine LinearMap.ext fun v => funext fun x => ?_ <;>
      simp only [Gate.adj, LinearMap.comp_apply, gL_apply, gC, LinearMap.id_apply, hx, sg_not] <;>
      ring_nf <;> simp only [I_sq, sg_sq, show sg s ^ 2 = 1 by rw [sq, sg_sq]] <;> ring
  | xg b =>
    have hx : ∀ x : Fin N, fx N ((fx N (x.val ^^^ b)).val ^^^ b) = x := fun x =>
      fx_of_lt x (by simpa [fx_val] using all_range h x)
    constructor <;> refine LinearMap.ext fun v => funext fun x => ?_ <;>
      simp [Gate.adj, gL_apply, gC, hx]
  | ph p =>
    constructor <;> refine LinearMap.ext fun v => funext fun x => ?_ <;>
      simp only [Gate.adj, LinearMap.comp_apply, gL_apply, gC, LinearMap.id_apply] <;>
      rw [← mul_assoc, ← pow_add, I_pow_of_mod _ (by omega), one_mul]

theorem adjC_cons (g : Gate) (c : List Gate) : adjC (g :: c) = adjC c ++ [g.adj] := by
  simp [adjC]

theorem cL_adjC (c : List Gate) (h : cOk N c = true) :
    cL N (adjC c) ∘ₗ cL N c = LinearMap.id ∧ cL N c ∘ₗ cL N (adjC c) = LinearMap.id := by
  induction c with
  | nil => simp [adjC, cL_nil]
  | cons g c ih =>
    simp only [cOk, List.all_cons, Bool.and_eq_true] at h
    obtain ⟨ih1, ih2⟩ := ih h.2
    obtain ⟨h1, h2⟩ := gL_adj g h.1
    rw [adjC_cons, cL_append, cL_cons, cL_cons, cL_nil, LinearMap.id_comp]
    constructor
    · refine LinearMap.ext fun v => ?_
      have e1 := LinearMap.congr_fun ih1 (gL N g v)
      have e2 := LinearMap.congr_fun h1 v
      simp only [LinearMap.comp_apply, LinearMap.id_apply] at e1 e2 ⊢
      rw [e1, e2]
    · refine LinearMap.ext fun v => ?_
      have e1 := LinearMap.congr_fun h2 (cL N (adjC c) v)
      have e2 := LinearMap.congr_fun ih2 v
      simp only [LinearMap.comp_apply, LinearMap.id_apply] at e1 e2 ⊢
      rw [e1, e2]

/-- A circuit with valid inverses as a linear equivalence; its inverse is `cL (adjC c)`. -/
noncomputable def cE (c : List Gate) (h : cOk N c = true) : (Fin N → ℂ) ≃ₗ[ℂ] (Fin N → ℂ) :=
  LinearEquiv.ofLinear (cL N c) (cL N (adjC c)) (cL_adjC c h).2 (cL_adjC c h).1

theorem cE_apply (c : List Gate) (h : cOk N c = true) (v : Fin N → ℂ) : cE c h v = cL N c v := rfl

theorem cE_symm_apply (c : List Gate) (h : cOk N c = true) (v : Fin N → ℂ) :
    (cE c h).symm v = cL N (adjC c) v := rfl

/-! ### `ℂ` semantics versus integer semantics -/

/-- `ℤ[i] → ℂ`. -/
noncomputable def φ (z : ℤ × ℤ) : ℂ := (z.1 : ℂ) + (z.2 : ℂ) * I

/-- An `ℕ`-indexed integer vector, read on `ℂ^N`. -/
noncomputable def emb (N : ℕ) (v : ℕ → ℤ × ℤ) : Fin N → ℂ := fun x => φ (v x.val)

theorem φ_ipow (k : ℕ) (z : ℤ × ℤ) : φ (ipow k z) = I ^ k * φ z := by
  rw [I_pow_mod]
  unfold ipow
  have : k % 4 < 4 := Nat.mod_lt _ (by norm_num)
  interval_cases h : k % 4 <;> simp only [h] <;> apply Complex.ext <;> simp [φ, pow_succ]

theorem φ_cgz (s : Bool) (a c : ℤ × ℤ) :
    φ (cgz s a c) = (1 + sg s * I) * φ a + (1 - sg s * I) * φ c := by
  cases s <;> apply Complex.ext <;> simp [φ, cgz, sg] <;> ring

/-- The scalar a gate loses in the integer semantics. -/
noncomputable def sc : Gate → ℂ
  | .cg _ _ => 1 / 2
  | _ => 1

theorem gC_emb (g : Gate) (v : ℕ → ℤ × ℤ) : gC N g (emb N v) = sc g • emb N (gz N g v) := by
  funext x
  cases g <;> simp only [gC, emb, gz, sc, fx_val, φ_ipow, φ_cgz, Pi.smul_apply, smul_eq_mul,
    one_mul]
  all_goals ring

omit [NeZero N] in
theorem runZ_cons (g : Gate) (c : List Gate) (v : ℕ → ℤ × ℤ) :
    runZ N (g :: c) v = runZ N c (gz N g v) := rfl

theorem cL_emb (c : List Gate) (v : ℕ → ℤ × ℤ) :
    cL N c (emb N v) = ((1 / 2 : ℂ) ^ ncg c) • emb N (runZ N c v) := by
  induction c generalizing v with
  | nil => simp [cL_nil, ncg, runZ]
  | cons g c ih =>
    rw [cL_cons, LinearMap.comp_apply, gL_apply, gC_emb, map_smul, ih, runZ_cons, smul_smul]
    congr 1
    cases g <;> simp [sc, ncg, pow_succ]
    all_goals ring

/-! ### Linearity, congruence and bounds of the integer semantics -/

theorem ipow_add (k : ℕ) (a b : ℤ × ℤ) : ipow k (a + b) = ipow k a + ipow k b := by
  unfold ipow; split <;> ext <;> simp <;> ring

theorem ipow_smul (k : ℕ) (n : ℤ) (a : ℤ × ℤ) : ipow k (n • a) = n • ipow k a := by
  unfold ipow; split <;> ext <;> simp

theorem cgz_add (s : Bool) (a b c d : ℤ × ℤ) : cgz s (a + b) (c + d) = cgz s a c + cgz s b d := by
  cases s <;> ext <;> simp [cgz] <;> ring

theorem cgz_smul (s : Bool) (n : ℤ) (a c : ℤ × ℤ) : cgz s (n • a) (n • c) = n • cgz s a c := by
  cases s <;> ext <;> simp [cgz] <;> ring

/-- One gate as a `ℤ`-linear map. -/
def gzL (N : ℕ) (g : Gate) : (ℕ → ℤ × ℤ) →ₗ[ℤ] (ℕ → ℤ × ℤ) where
  toFun := gz N g
  map_add' v w := by funext x; cases g <;> simp [gz, ipow_add, cgz_add]
  map_smul' n v := by
    funext x; cases g <;> simp only [gz, Pi.smul_apply, RingHom.id_apply, ipow_smul, cgz_smul]

def runZL (N : ℕ) : List Gate → (ℕ → ℤ × ℤ) →ₗ[ℤ] (ℕ → ℤ × ℤ)
  | [] => LinearMap.id
  | g :: c => runZL N c ∘ₗ gzL N g

omit [NeZero N] in
theorem runZL_apply (c : List Gate) (v : ℕ → ℤ × ℤ) : runZL N c v = runZ N c v := by
  induction c generalizing v with
  | nil => rfl
  | cons g c ih => simp only [runZL, LinearMap.comp_apply, ih]; rfl

theorem gz_congr (g : Gate) {v w : ℕ → ℤ × ℤ} (h : ∀ k < N, v k = w k) :
    ∀ x < N, gz N g v x = gz N g w x := by
  have hN := NeZero.pos N
  intro x hx
  cases g <;> simp only [gz, h x hx, h _ (Nat.mod_lt _ hN)]

theorem runZ_congr (c : List Gate) {v w : ℕ → ℤ × ℤ} (h : ∀ k < N, v k = w k) :
    ∀ x < N, runZ N c v x = runZ N c w x := by
  induction c generalizing v w with
  | nil => exact h
  | cons g c ih => exact ih (gz_congr g h)

/-- Entrywise bound on both coordinates. -/
def Bnd (M : ℤ) (v : ℕ → ℤ × ℤ) : Prop := ∀ k, |(v k).1| ≤ M ∧ |(v k).2| ≤ M

theorem ipow_bnd (k : ℕ) {M : ℤ} {z : ℤ × ℤ} (h : |z.1| ≤ M ∧ |z.2| ≤ M) :
    |(ipow k z).1| ≤ M ∧ |(ipow k z).2| ≤ M := by
  unfold ipow; split <;> simp [abs_neg, h.1, h.2]

/-- The growth factor of a gate in the integer semantics. -/
def gw : Gate → ℤ
  | .cg _ _ => 4
  | _ => 1

omit [NeZero N] in
theorem gz_bnd (g : Gate) {M : ℤ} {v : ℕ → ℤ × ℤ} (h : Bnd M v) : Bnd (gw g * M) (gz N g v) := by
  intro x
  cases g with
  | cg q s =>
    obtain ⟨h1, h2⟩ := h x
    obtain ⟨h3, h4⟩ := h ((x ^^^ q) % N)
    rw [abs_le] at h1 h2 h3 h4
    cases s <;> simp only [gz, cgz, gw, if_true, Bool.false_eq_true, if_false] <;>
      constructor <;> rw [abs_le] <;> constructor <;> linarith
  | pm G Gi => simpa [gz, gw] using h _
  | dg Q α => simpa [gz, gw] using ipow_bnd _ (h x)
  | xg b => simpa [gz, gw] using h _
  | ph p => simpa [gz, gw] using ipow_bnd _ (h x)

omit [NeZero N] in
theorem runZ_bnd (c : List Gate) {M : ℤ} {v : ℕ → ℤ × ℤ} (h : Bnd M v) :
    Bnd (4 ^ ncg c * M) (runZ N c v) := by
  induction c generalizing M v with
  | nil => simpa [ncg, runZ] using h
  | cons g c ih =>
    rw [runZ_cons]
    have := ih (gz_bnd (N := N) g h)
    cases g <;> simp only [ncg, gw, one_mul] at this ⊢ <;> [skip; skip; rwa [pow_succ, mul_assoc]; skip; skip] <;> exact this

/-! ### Packing -/

/-- A base-`B` expansion with digits `|d i| < B` vanishes only if every digit does. -/
theorem digits_eq_zero {B : ℤ} (hB : 0 < B) :
    ∀ (n : ℕ) (d : ℕ → ℤ), (∀ i < n, |d i| < B) →
      ∑ i ∈ Finset.range n, B ^ i * d i = 0 → ∀ i < n, d i = 0 := by
  intro n
  induction n with
  | zero => intro d _ _ i hi; omega
  | succ n ih =>
    intro d hd hs
    rw [Finset.sum_range_succ'] at hs
    simp only [pow_succ, pow_zero, one_mul] at hs
    have hs' : B * ∑ i ∈ Finset.range n, B ^ i * d (i + 1) + d 0 = 0 := by
      rw [Finset.mul_sum]; rw [← hs]; congr 1; apply Finset.sum_congr rfl; intro i _; ring
    have h0 : d 0 = 0 := by
      apply Int.eq_zero_of_abs_lt_dvd _ (hd 0 (by omega))
      exact ⟨-∑ i ∈ Finset.range n, B ^ i * d (i + 1), by linarith⟩
    rw [h0, add_zero] at hs'
    have hrest := ih (fun i => d (i + 1)) (fun i hi => hd (i + 1) (by omega))
      ((mul_eq_zero.1 hs').resolve_left hB.ne')
    intro i hi
    rcases i with _ | i
    · exact h0
    · exact hrest i (by omega)

theorem Tr.get_ofFn (f : ℕ → ℤ × ℤ) (d x : ℕ) : (Tr.ofFn f d).get x = f (x % 2 ^ d) := by
  induction d generalizing f x with
  | zero => simp [Tr.ofFn, Tr.get, Nat.mod_one]
  | succ d ih =>
    have hm : x % 2 ^ (d + 1) = x % 2 + 2 * (x / 2 % 2 ^ d) := by
      rw [pow_succ', Nat.mod_mul]
    simp only [Tr.ofFn, Tr.get, ih, hm]
    split <;> congr 1 <;> omega

theorem Tr.beqS_get {k : ℤ} : ∀ {t₁ t₂ : Tr}, Tr.beqS k t₁ t₂ = true →
    ∀ x, t₁.get x = k • t₂.get x
  | .lf a, .lf b, h, x => by
    simp only [Tr.beqS, Bool.and_eq_true, beq_iff_eq] at h
    ext <;> simp [Tr.get, h.1, h.2]
  | .nd l r, .nd l' r', h, x => by
    simp only [Tr.beqS, Bool.and_eq_true] at h
    simp only [Tr.get]
    split
    · exact Tr.beqS_get h.1 _
    · exact Tr.beqS_get h.2 _
  | .lf _, .nd _ _, h, _ => by simp [Tr.beqS] at h
  | .nd _ _, .lf _, h, _ => by simp [Tr.beqS] at h

theorem runT_get (c : List Gate) (t : Tr) : ∀ x < 512, (runT c t).get x = runZ 512 c t.get x := by
  induction c generalizing t with
  | nil => intro x _; rfl
  | cons g c ih =>
    intro x hx
    change (runT c (Tr.ofFn (gz 512 g t.get) 9)).get x = runZ 512 c (gz 512 g t.get) x
    rw [ih _ x hx]
    refine runZ_congr c (fun k hk => ?_) x hx
    rw [Tr.get_ofFn, Nat.mod_eq_of_lt (by simpa using hk)]

/-- The unit vector `e_y`. -/
def eI (y : ℕ) : ℕ → ℤ × ℤ := fun k => if k = y then (1, 0) else 0

theorem eI_bnd (y : ℕ) : Bnd 1 (eI y) := by
  intro k; unfold eI; split <;> simp

/-- Vector digits: `Σ_{y<n} B^y z_y = 0` with `|z_y| < B` coordinatewise forces `z = 0`. -/
theorem vec_digits {B : ℤ} (hB : 0 < B) (n : ℕ) (z : ℕ → ℤ × ℤ)
    (hz : ∀ y < n, |(z y).1| < B ∧ |(z y).2| < B)
    (hs : ∑ y ∈ Finset.range n, B ^ y • z y = 0) : ∀ y < n, z y = 0 := by
  have h1 := digits_eq_zero hB n (fun y => (z y).1) (fun y hy => (hz y hy).1) (by
    have := congrArg Prod.fst hs
    simpa [Prod.fst_sum, smul_eq_mul] using this)
  have h2 := digits_eq_zero hB n (fun y => (z y).2) (fun y hy => (hz y hy).2) (by
    have := congrArg Prod.snd hs
    simpa [Prod.snd_sum, smul_eq_mul] using this)
  intro y hy
  exact Prod.ext (h1 y hy) (h2 y hy)

theorem pow_two_mul_pow_four_le {n₁ n₂ : ℕ} (h : n₂ ≤ n₁) :
    (2 : ℤ) ^ (n₁ - n₂) * 4 ^ n₂ ≤ 4 ^ n₁ := by
  have : (4 : ℤ) ^ n₁ = 2 ^ (n₁ - n₂) * 4 ^ n₂ * 2 ^ (n₁ - n₂) := by
    rw [show (4 : ℤ) = 2 ^ 2 by norm_num, ← pow_mul, ← pow_mul, ← pow_add, ← pow_add]
    congr 1; omega
  rw [this]
  exact le_mul_of_one_le_right (by positivity) (one_le_pow₀ (by norm_num))

theorem single_eq_emb (y : Fin 512) (a : ℂ) : Pi.single y a = a • emb 512 (eI y.val) := by
  funext x
  by_cases hxy : x = y
  · subst hxy; simp [emb, eI, φ]
  · have : x.val ≠ y.val := fun h => hxy (Fin.ext h)
    simp [emb, eI, φ, hxy, this]

/-- **The packed check is sound.**  If `check c₁ c₂` evaluates to `true`, the circuits are the
same linear map on `ℂ^512`. -/
theorem cL_eq_of_check (c₁ c₂ : List Gate) (h : check c₁ c₂ = true) : cL 512 c₁ = cL 512 c₂ := by
  simp only [check, Bool.and_eq_true, decide_eq_true_eq] at h
  obtain ⟨hle, hT⟩ := h
  have hB : (0 : ℤ) < 4 ^ (ncg c₁ + 1) := by positivity
  -- the packed vector is `Σ_y B^y e_y` on `[0, 512)`
  have ht : ∀ k < 512, (Tr.ofFn (fun k => (((4 : ℤ) ^ (ncg c₁ + 1)) ^ k, (0 : ℤ))) 9).get k =
      (∑ y ∈ Finset.range 512, (((4 : ℤ) ^ (ncg c₁ + 1)) ^ y) • eI y) k := by
    intro k hk
    rw [Tr.get_ofFn, Nat.mod_eq_of_lt (by simpa using hk), Finset.sum_apply]
    simp only [eI, Pi.smul_apply, smul_ite, smul_zero]
    rw [Finset.sum_ite_eq (Finset.range 512) k, if_pos (Finset.mem_range.2 hk)]
    ext <;> simp
  have hpack : ∀ c : List Gate, ∀ x < 512,
      runZ 512 c (Tr.ofFn (fun k => (((4 : ℤ) ^ (ncg c₁ + 1)) ^ k, (0 : ℤ))) 9).get x =
        ∑ y ∈ Finset.range 512, (((4 : ℤ) ^ (ncg c₁ + 1)) ^ y) • runZ 512 c (eI y) x := by
    intro c x hx
    rw [runZ_congr c ht x hx, ← runZL_apply, map_sum, Finset.sum_apply]
    refine Finset.sum_congr rfl fun y _ => ?_
    rw [map_smul, Pi.smul_apply, runZL_apply]
  -- entrywise identity of the integer matrices
  have hent : ∀ x < 512, ∀ y < 512,
      runZ 512 c₁ (eI y) x = (2 : ℤ) ^ (ncg c₁ - ncg c₂) • runZ 512 c₂ (eI y) x := by
    intro x hx
    have hx' := Tr.beqS_get hT x
    rw [runT_get _ _ x hx, runT_get _ _ x hx, hpack _ x hx, hpack _ x hx, Finset.smul_sum] at hx'
    have hz := vec_digits hB 512
      (fun y => runZ 512 c₁ (eI y) x - (2 : ℤ) ^ (ncg c₁ - ncg c₂) • runZ 512 c₂ (eI y) x)
      (fun y _ => by
        obtain ⟨a1, a2⟩ := runZ_bnd (N := 512) c₁ (eI_bnd y) x
        obtain ⟨b1, b2⟩ := runZ_bnd (N := 512) c₂ (eI_bnd y) x
        have hk := pow_two_mul_pow_four_le hle
        have h4 : (0 : ℤ) < 4 ^ ncg c₁ := by positivity
        have h2 : (0 : ℤ) < 2 ^ (ncg c₁ - ncg c₂) := by positivity
        rw [mul_one] at a1 a2 b1 b2
        rw [pow_succ]
        simp only [Prod.fst_sub, Prod.snd_sub, Prod.smul_fst, Prod.smul_snd, smul_eq_mul]
        constructor
        · calc |_| ≤ |(runZ 512 c₁ (eI y) x).1| + |2 ^ (ncg c₁ - ncg c₂) * (runZ 512 c₂ (eI y) x).1| :=
                abs_sub _ _
            _ ≤ 4 ^ ncg c₁ + 2 ^ (ncg c₁ - ncg c₂) * 4 ^ ncg c₂ := by
                rw [abs_mul, abs_of_pos h2]; gcongr
            _ < 4 ^ ncg c₁ * 4 := by linarith
        · calc |_| ≤ |(runZ 512 c₁ (eI y) x).2| + |2 ^ (ncg c₁ - ncg c₂) * (runZ 512 c₂ (eI y) x).2| :=
                abs_sub _ _
            _ ≤ 4 ^ ncg c₁ + 2 ^ (ncg c₁ - ncg c₂) * 4 ^ ncg c₂ := by
                rw [abs_mul, abs_of_pos h2]; gcongr
            _ < 4 ^ ncg c₁ * 4 := by linarith)
      (by
        simp only [smul_sub, Finset.sum_sub_distrib, hx']
        rw [sub_eq_zero]
        exact Finset.sum_congr rfl fun y _ => smul_comm _ _ _)
    intro y hy
    exact sub_eq_zero.1 (hz y hy)
  -- back to `ℂ`
  apply LinearMap.pi_ext
  intro y a
  rw [single_eq_emb, map_smul, map_smul, cL_emb, cL_emb]
  congr 1
  funext x
  simp only [Pi.smul_apply, emb, smul_eq_mul]
  rw [hent x.val x.isLt y.val y.isLt]
  have h2 : ((1 / 2 : ℂ) ^ ncg c₁) * (2 : ℂ) ^ (ncg c₁ - ncg c₂) = (1 / 2 : ℂ) ^ ncg c₂ := by
    obtain ⟨k, hk⟩ : ∃ k, ncg c₁ = ncg c₂ + k := ⟨ncg c₁ - ncg c₂, by omega⟩
    rw [hk, Nat.add_sub_cancel_left, pow_add, mul_assoc, ← mul_pow]
    norm_num
  rw [← h2, mul_assoc]
  congr 1
  simp only [φ, Prod.smul_fst, Prod.smul_snd, smul_eq_mul]
  push_cast
  ring

end HyperplaneEnd.Clifford
