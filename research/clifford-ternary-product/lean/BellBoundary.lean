import BooleanGauss

/-! One ternary projection keeps a common affine support and a quadratic
phase at all unobserved sites. Each path accumulates its own scalar. -/
namespace BellBoundary
open BooleanGauss TernaryCollect

theorem compact_weight {n} (M : Model (Fin n)) (x : Bits n) : weight M.compact x = weight M x := by
  simp [weight, Model.compact,support,List.all_map,Function.comp_def, Aff.compact_eval, Quad.compact_eval]

def collapse {n} (M : Model (Fin (n+1))) : ℕ × Model (Fin n) :=
  match M.rows.find? Aff.head with
  | some a => (0,(M.sub (insertHead (a.sub off))).compact)
  | none => (1,(eliminateLoose M).compact)

theorem collapse_exact {n} (M : Model (Fin (n+1))) (x : Bits n) :
    weight M (Fin.cons true x) + weight M (Fin.cons false x) =
      (2:ℤ)^(collapse M).1 * weight (collapse M).2 x := by
  unfold collapse
  split
  next a hv =>
    simpa [compact_weight] using pivot_weight M a (List.mem_of_find?_eq_some hv) (List.find?_some hv) x
  next hv =>
    have hn : ∀ a ∈ M.rows, a.head = false := by simpa using List.find?_eq_none.mp hv
    simpa [compact_weight] using loose_weight M hn x

def fixedMap {n} (b : Bool) : Fin (n+2) → Aff (Fin n) :=
  Fin.cases (.const b) (insertHead (.const b))

def mixedMap {n} : Fin (n+2) → Aff (Fin (n+1)) :=
  Fin.cases (.var 0) (Fin.cases (.plus (.const true) (.var 0)) (fun j ↦ .var j.succ))

def pairBits {n} (b c : Bool) (x : Bits n) : Bits (n+2) := Fin.cons b (Fin.cons c x)

theorem fixed_eval {n} (b : Bool) (x : Bits n) :
    (fun i ↦ (fixedMap b i).eval x) = pairBits b b x := by
  funext i
  refine Fin.cases ?_ (fun j ↦ ?_) i
  · rfl
  · refine Fin.cases ?_ (fun k ↦ ?_) j <;> rfl

theorem mixed_eval {n} (b : Bool) (x : Bits n) :
    (fun i ↦ (mixedMap i).eval (Fin.cons b x)) = pairBits b (!b) x := by
  funext i
  refine Fin.cases ?_ (fun j ↦ ?_) i
  · rfl
  · refine Fin.cases ?_ (fun k ↦ ?_) j
    · cases b <;> rfl
    · rfl

def bell {n} : Trit → (Bits (n+2) → ℤ) → Bits n → ℤ
  | some b,f,x => f (pairBits b b x)
  | none,f,x => f (pairBits true false x) + f (pairBits false true x)

def project {n} : Trit → Model (Fin (n+2)) → ℕ × Model (Fin n)
  | some b,M => (0,(M.sub (fixedMap b)).compact)
  | none,M => collapse (M.sub mixedMap)

theorem project_exact {n} (d : Trit) (M : Model (Fin (n+2))) (x : Bits n) :
    bell d (weight M) x = (2:ℤ)^(project d M).1 * weight (project d M).2 x := by
  cases d with
  | some b => simp [bell,project,compact_weight,weight_sub,fixed_eval]
  | none =>
    have h := collapse_exact (M.sub mixedMap) x
    simpa only [bell,project,weight_sub,mixed_eval,Bool.not_true,Bool.not_false] using h

theorem project_shift {n} (d : Trit) (M : Model (Fin (n+2))) :
    (project d M).1 ≤ (if d.isNone then 1 else 0) := by
  cases d with
  | some b => rfl
  | none => simp only [project,collapse]; split <;> norm_num

/-- The first pair is the highest unobserved pair. The tail has fixed type. -/
def slots (n : ℕ) : ℕ → ℕ | 0 => n | i+1 => slots n i + 2

def run (n : ℕ) : (ds : List Trit) → Model (Fin (slots n ds.length)) → ℕ × Model (Fin n)
  | [], M => (0,M)
  | d::ds, M =>
    let step := project d M
    let tail := run n ds step.2
    (step.1+tail.1,tail.2)

def contract (n : ℕ) : (ds : List Trit) → (Bits (slots n ds.length) → ℤ) → Bits n → ℤ
  | [], f => f
  | d::ds, f => contract n ds (bell d f)

theorem contract_scale (n : ℕ) (ds : List Trit) (c : ℤ) (f : Bits (slots n ds.length) → ℤ) (x : Bits n) :
    contract n ds (fun z ↦ c*f z) x = c*contract n ds f x := by
  induction ds with
  | nil => rfl
  | cons d ds ih =>
    have h : (bell d (fun z ↦ c*f z)) = fun z ↦ c*bell d f z := by
      funext z
      cases d with
      | some b => rfl
      | none => simp [bell,mul_add]
    change contract n ds (bell d (fun z ↦ c*f z)) x = _
    rw [h,ih]
    rfl

/-- At every cut this gives all remaining amplitudes, including zero
entries, with one chart and one scalar. No boundary table is assumed. -/
theorem boundary_exact (n : ℕ) (ds : List Trit) (M : Model (Fin (slots n ds.length))) (x : Bits n) :
    contract n ds (weight M) x = (2:ℤ)^(run n ds M).1 * weight (run n ds M).2 x := by
  induction ds with
  | nil => simp only [contract,run,pow_zero,one_mul]; rfl
  | cons d ds ih =>
    change contract n ds (bell d (weight M)) x = _
    rw [funext (project_exact d M),contract_scale,ih]
    simp only [run,pow_add,mul_assoc]

theorem boundary_shift (n : ℕ) (ds : List Trit) (M : Model (Fin (slots n ds.length))) :
    (run n ds M).1 ≤ ds.countP (·.isNone) := by
  induction ds with
  | nil => rfl
  | cons d ds ih =>
    have h := project_shift d M
    have ht := ih (project d M).2
    simp only [run,List.countP_cons]
    cases hd : d.isNone
    · simp only [hd,Bool.false_eq_true,↓reduceIte] at h ⊢
      omega
    · simp only [hd,↓reduceIte] at h ⊢
      omega

#print axioms project_exact
#print axioms boundary_exact
#print axioms boundary_shift
end BellBoundary
