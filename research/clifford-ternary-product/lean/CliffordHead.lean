import TrieDelivery

/-! Run the depth-first output head with unit moves. Each child restores
its own exponent offset before the next child starts. -/
namespace CliffordHead
open BooleanGauss BellBoundary TernaryCollect SignedEvents TrieProduct TrieDelivery

inductive Command where
  | right
  | left
  | put (positive : Bool)

def execute : List Command → ℕ → ℕ × List Event
  | [],j => (j,[])
  | .right::cs,j => execute cs (j+1)
  | .left::cs,j => execute cs (j-1)
  | .put b::cs,j =>
    let r := execute cs j
    (r.1,⟨b,j⟩::r.2)

theorem execute_append (xs ys : List Command) (j : ℕ) :
    execute (xs++ys) j = (let p := execute xs j
                          let q := execute ys p.1
                          (q.1,p.2++q.2)) := by
  induction xs generalizing j with
  | nil => simp [execute]
  | cons c cs ih => cases c <;> simp [execute,ih]

def wrapped (e : ℕ) (cs : List Command) : List Command :=
  if e=0 then cs else .right::(cs++[.left])

theorem wrapper (e : ℕ) (he : e ≤ 1) (cs : List Command) (j n : ℕ) (events : List Event)
    (h : execute cs (j+e) = (j+e+n,events)) :
    execute (wrapped e cs) j = (j+n,events) := by
  rcases Nat.le_one_iff_eq_zero_or_eq_one.mp he with rfl|rfl
  · simpa [wrapped] using h
  · simp [wrapped,execute,execute_append,h]

def terminal (v : ℤ) : List Command :=
  if v=0 then [.right] else [.put (decide (0<v)),.right]

theorem terminal_execute (j : ℕ) (v : ℤ) (h : v=0 ∨ v=1 ∨ v= -1) :
    execute (terminal v) j = (j+1,encode j v) := by
  rcases h with rfl|rfl|rfl <;> simp [terminal,execute,encode,show Nat.log2 1 = 0 by rfl]

def walk : (m : ℕ) → Model (Fin (slots 0 m)) → Bool → List Command
  | 0,M,neg => terminal (flip neg (weight M Fin.elim0))
  | m+1,M,neg =>
    let child (d : Trit) :=
      let c := project d M
      wrapped c.1 (walk m c.2 neg)
    child (some false) ++ child none ++ child (some true)

theorem terminal_values {m} (M : Model (Fin m)) (x : Bits m) (neg : Bool) :
    flip neg (weight M x) = 0 ∨ flip neg (weight M x) = 1 ∨ flip neg (weight M x) = -1 := by
  rcases weight_values M x with h|h|h <;> cases neg <;> simp [SignedEvents.flip,h]

/-- The emitted signs, their addresses and the final head are all exact.
The interpreter has only left, right and deposit instructions. -/
theorem execute_walk (m : ℕ) (M : Model (Fin (slots 0 m))) (j : ℕ) (neg : Bool) :
    execute (walk m M neg) j = (j+3^m,traverse m M j neg) := by
  induction m generalizing j with
  | zero =>
    change execute (terminal (flip neg (weight M Fin.elim0))) j = (j+1,encode j (flip neg (weight M Fin.elim0)))
    exact terminal_execute _ _ (terminal_values M _ _)
  | succ m ih =>
    let H := 3^m
    have ch (d : Trit) (u : ℕ) : execute (wrapped (project d M).1 (walk m (project d M).2 neg)) u =
        (u+H,traverse m (project d M).2 (u+(project d M).1) neg) := by
      apply wrapper
      · have := project_shift d M
        cases d <;> simp_all
      · exact ih _ _
    simp only [walk,execute_append,ch,TrieDelivery.traverse]
    have z₀ : digitValue (some false) = 0 := rfl
    have z₁ : digitValue (none : Trit) = 1 := rfl
    have z₂ : digitValue (some true) = 2 := rfl
    simp only [z₀,z₁,z₂,zero_mul,one_mul,Nat.add_zero,pow_succ]
    dsimp only [H]
    have h₂ : j+3^m+3^m = j+2*3^m := by omega
    have h₃ : j+3^m+3^m+3^m = j+3^m*3 := by omega
    rw [h₃,h₂]

def travel : List Command → ℕ
  | [] => 0
  | .put _::cs => travel cs
  | .right::cs | .left::cs => travel cs + 1

theorem travel_append (xs ys : List Command) : travel (xs++ys) = travel xs + travel ys := by
  induction xs with
  | nil => simp [travel]
  | cons c cs ih => cases c <;> simp [travel,ih] <;> omega

theorem wrapped_travel (e : ℕ) (cs : List Command) :
    travel (wrapped e cs) = travel cs + (if e=0 then 0 else 2) := by
  by_cases h : e=0 <;> simp [wrapped,h,travel,travel_append]

theorem fixed_wrap {n} (M : Model (Fin (n+2))) (b : Bool) (cs : List Command) :
    wrapped (project (some b) M).1 cs = cs := rfl

theorem wrapped_le (e : ℕ) (cs : List Command) : travel (wrapped e cs) ≤ travel cs + 2 := by
  rw [wrapped_travel]
  split <;> omega

theorem travel_bound (m : ℕ) (M : Model (Fin (slots 0 m))) (neg : Bool) :
    travel (walk m M neg)+1 ≤ 2*3^m := by
  induction m with
  | zero =>
    change travel (terminal _) + 1 ≤ 2
    unfold terminal
    split <;> simp [travel]
  | succ m ih =>
    simp only [walk,travel_append,pow_succ]
    have h₀ := ih (project (some false) M).2
    have h₁ := ih (project none M).2
    have h₂ := ih (project (some true) M).2
    have hf (b : Bool) : travel (wrapped (project (some b) M).1 (walk m (project (some b) M).2 neg)) =
        travel (walk m (project (some b) M).2 neg) := congrArg travel (fixed_wrap (n := slots 0 m) M b _)
    have h := wrapped_le (project none M).1 (walk m (project none M).2 neg)
    have h₃ := hf false
    have h₄ := hf true
    omega

/-- Each of the four passes starts at bit zero. -/
def products {m} (A B : Model (Fin m)) : List Event :=
  (execute (walk m (joint A B false false) false) 0).2 ++
  (execute (walk m (joint A B true false) true) 0).2 ++
  (execute (walk m (joint A B false true) true) 0).2 ++
  (execute (walk m (joint A B true true) false) 0).2

theorem products_equal {m} (A B : Model (Fin m)) : products A B = fourTraversals A B := by
  simp [products,fourTraversals,execute_walk]

theorem physical_product {m} (a b : Fin (3^m) → Bool) (A B : Model (Fin m))
    (ha : PhysicalInput.Valid A a) (hb : PhysicalInput.Valid B b) :
    BinaryDelivery.binary (finish (products A B)) = BinaryDelivery.binary (List.ofFn a)*BinaryDelivery.binary (List.ofFn b) := by
  rw [products_equal,from_literals _ _ _ _ ha hb]

theorem physical_mixture {h n : ℕ} (A B : Bits h → Model (Fin n))
    (a b : Fin (3^h) → Fin (3^n) → Bool) (ah : PhysicalBlocks.HighHoles a) (bh : PhysicalBlocks.HighHoles b)
    (av : ∀ x, PhysicalInput.Valid (A x) (PhysicalBlocks.block a x))
    (bv : ∀ y, PhysicalInput.Valid (B y) (PhysicalBlocks.block b y)) :
    PrefixBlocks.deliver (2^(3^n)) (PrefixBlocks.binCoeffs (fun x y ↦ BinaryDelivery.binary
      (finish (products (A x) (B y))))) =
    BinaryDelivery.binary (PhysicalBlocks.strip a) * BinaryDelivery.binary (PhysicalBlocks.strip b) := by
  simp only [products_equal]
  exact complete_mixture A B a b ah bh av bv

#print axioms execute_walk
#print axioms travel_bound
#print axioms physical_product
#print axioms physical_mixture
end CliffordHead
