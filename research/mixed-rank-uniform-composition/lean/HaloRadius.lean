import Std

namespace HaloRadius

structure Datum where
  re : Int
  im : Int
  deriving DecidableEq, Repr

def radius (v : Datum) : Nat := v.re.natAbs + v.im.natAbs

def plus (x y : Datum) : Datum := ⟨x.re + y.re, x.im + y.im⟩

def times (n : Int) (x : Datum) : Datum := ⟨n * x.re, n * x.im⟩

def truncate (d : Nat) (x : Datum) : Datum := ⟨x.re.tdiv d, x.im.tdiv d⟩

theorem plusBound (x y : Datum) : radius (plus x y) ≤ radius x + radius y := by
  have hr := Int.natAbs_add_le x.re y.re
  have hi := Int.natAbs_add_le x.im y.im
  simp only [radius, plus]
  omega

theorem timesRadius (c : Int) (x : Datum) : radius (times c x) = c.natAbs * radius x := by
  simp [radius, times, Int.natAbs_mul, Nat.mul_add]

theorem truncateRadius (d : Nat) (x : Datum) : radius (truncate d x) ≤ radius x / d := by
  simp only [radius, truncate, Int.natAbs_tdiv, Int.natAbs_natCast]
  change x.re.natAbs / d + x.im.natAbs / d ≤ (x.re.natAbs + x.im.natAbs) / d
  exact Nat.div_add_div_le_add_div

variable {ι : Type}

abbrev Row (ι : Type) := List (Int × ι)

def mass (row : Row ι) : Nat := (row.map fun term => term.1.natAbs).sum

def dot (z : ι → Datum) : Row ι → Datum
  | [] => ⟨0, 0⟩
  | (w, j) :: rest => plus (times w (z j)) (dot z rest)

theorem dotBound (z : ι → Datum) (R : Nat) (hz : ∀ i, radius (z i) ≤ R) (row : Row ι) :
    radius (dot z row) ≤ mass row * R := by
  induction row with
  | nil => simp [radius, dot, mass]
  | cons item tail ih =>
    obtain ⟨w, j⟩ := item
    exact calc
      radius (dot z ((w,j)::tail))
          ≤ radius (times w (z j)) + radius (dot z tail) := plusBound ..
      _ ≤ w.natAbs * R + mass tail * R :=
          Nat.add_le_add (by rw [timesRadius]; exact Nat.mul_le_mul_left _ (hz j)) ih
      _ = mass ((w,j)::tail) * R := by simp [mass, Nat.add_mul]

/-- Base grid has unit 1/D. Input, state and reference coefficients use that grid.
The row computes x/a + sum cⱼ zⱼ/D and truncates only the full sum. -/
def update (D a : Nat) (x : Datum) (z : ι → Datum) (row : Row ι) : Datum :=
  truncate (a * D) (plus (times D x) (times a (dot z row)))

theorem updateBound (D a R : Nat) (hd : 0 < a * D) (row : Row ι)
    (hg : D + a * mass row ≤ a * D) (x : Datum) (z : ι → Datum)
    (hx : radius x ≤ R) (hz : ∀ i, radius (z i) ≤ R) :
    radius (update D a x z row) ≤ R := by
  let v := plus (times D x) (times a (dot z row))
  have hv : radius v ≤ a * D * R := by
    calc
      radius v ≤ radius (times D x) + radius (times a (dot z row)) := plusBound ..
      _ ≤ D * R + a * (mass row * R) := by
        simp only [timesRadius, Int.natAbs_natCast]
        exact Nat.add_le_add (Nat.mul_le_mul_left D hx)
          (Nat.mul_le_mul_left a (dotBound z R hz row))
      _ = (D + a * mass row) * R := by simp [Nat.add_mul, Nat.mul_assoc]
      _ ≤ a * D * R := Nat.mul_le_mul_right _ hg
  have hquot : radius v / (a * D) ≤ (a * D * R) / (a * D) := Nat.div_le_div_right hv
  calc
    radius (update D a x z row) ≤ radius v / (a * D) := truncateRadius ..
    _ ≤ (a * D * R) / (a * D) := hquot
    _ = R := Nat.mul_div_cancel_left R hd

structure Axis (ι : Type) where
  D : Nat
  a : Nat
  J : Nat
  rows : ι → Row ι

def Admitted (axis : Axis ι) : Prop :=
  0 < axis.a * axis.D ∧ ∀ i, axis.D + axis.a * mass (axis.rows i) ≤ axis.a * axis.D

def iterate (axis : Axis ι) (x : ι → Datum) : Nat → ι → Datum
  | 0, _ => ⟨0, 0⟩
  | k+1, i => update axis.D axis.a (x i) (iterate axis x k) (axis.rows i)

theorem eachIteration (axis : Axis ι) (ha : Admitted axis) (x : ι → Datum) (R : Nat)
    (hx : ∀ i, radius (x i) ≤ R) (k : Nat) : ∀ i, radius (iterate axis x k i) ≤ R := by
  induction k with
  | zero => simp [iterate, radius]
  | succ k ih => exact fun i => updateBound _ _ _ ha.1 _ (ha.2 i) _ _ (hx i) ih

def sweep (x : ι → Datum) : List (Axis ι) → ι → Datum
  | [] => x
  | a :: rest => sweep (iterate a x a.J) rest

theorem everyAxis (axes : List (Axis ι)) (x : ι → Datum) (R : Nat)
    (ha : ∀ a ∈ axes, Admitted a) (hx : ∀ i, radius (x i) ≤ R) :
    ∀ i, radius (sweep x axes i) ≤ R := by
  induction axes generalizing x with
  | nil => exact hx
  | cons a rest ih =>
    apply ih (iterate a x a.J)
    · exact fun b hb => ha b (List.mem_cons_of_mem _ hb)
    · exact eachIteration a (ha a (by simp)) x R hx a.J

def minus (x y : Datum) : Datum := ⟨x.re - y.re, x.im - y.im⟩

theorem truncateResidual (d : Nat) (hd : 0 < d) (v : Datum) :
    radius (minus (times d (truncate d v)) v) ≤ 2*d := by
  have single (x : Int) : ((d : Int) * x.tdiv d - x).natAbs < d := by
    have eq : (d : Int) * x.tdiv d - x = -x.tmod d := by
      have := Int.mul_tdiv_add_tmod x d
      omega
    rw [eq, Int.natAbs_neg, Int.natAbs_tmod, Int.natAbs_natCast]
    exact Nat.mod_lt _ hd
  have hr := single v.re
  have hi := single v.im
  simp only [radius, minus, times, truncate]
  omega

theorem linearDot (row : Row ι) (z w : ι → Datum) (n : Int) :
    dot (fun j => minus (times n (z j)) (w j)) row =
      minus (times n (dot z row)) (dot w row) := by
  induction row with
  | nil => simp [dot, minus, times]
  | cons el rest ih =>
    obtain ⟨coef,j⟩ := el
    simp only [dot]
    rw [ih]
    simp only [minus, times, plus, Datum.mk.injEq]
    constructor <;> grind

def den (axis : Axis ι) (k : Nat) : Nat := (axis.a * axis.D)^k

/-- The unrounded Horner numerator at common denominator (aD)^k, measured
in input grid units. This is precisely the k-term finite Neumann polynomial. -/
def exactIter (axis : Axis ι) (x : ι → Datum) : Nat → ι → Datum
  | 0, _ => ⟨0,0⟩
  | k+1, i => plus (times (axis.D * den axis k : Nat) (x i))
                  (times axis.a (dot (exactIter axis x k) (axis.rows i)))

def defect (axis : Axis ι) (x : ι → Datum) (k : Nat) (i : ι) : Datum :=
  minus (times (den axis k) (iterate axis x k i)) (exactIter axis x k i)

private theorem errorAlgebra (a D n : Int) (x y z v : Datum) :
    minus (times (n * (a * D)) v) (plus (times (D * n) x) (times a z)) =
    plus (times n (minus (times (a * D) v) (plus (times D x) (times a y))))
         (times a (minus (times n y) z)) := by
  simp only [minus, plus, times, Datum.mk.injEq]
  constructor <;> grind

theorem defectStep (axis : Axis ι) (x : ι → Datum) (k : Nat) (i : ι) :
    defect axis x (k+1) i =
      let raw := plus (times axis.D (x i))
            (times axis.a (dot (iterate axis x k) (axis.rows i)))
      plus (times (den axis k)
             (minus (times (axis.a * axis.D : Nat) (truncate (axis.a * axis.D) raw)) raw))
           (times axis.a (dot (defect axis x k) (axis.rows i))) := by
  have row := linearDot (axis.rows i) (iterate axis x k) (exactIter axis x k) (den axis k)
  change dot (defect axis x k) (axis.rows i) = _ at row
  rw [row]
  simp only [defect, iterate, update, exactIter, den, Nat.pow_succ, Int.natCast_mul]
  apply errorAlgebra

/-- With B an integer bound for the inverse row gap, numerical Horner error
stays at most 2B input-grid units, after clearing the exact denominator. -/
theorem finiteNeumannError (axis : Axis ι) (x : ι → Datum) (B : Nat)
    (hd : 0 < axis.a * axis.D)
    (hg : ∀ i, axis.D + B * mass (axis.rows i) ≤ B * axis.D)
    (k : Nat) : ∀ i, radius (defect axis x k i) ≤ 2 * B * den axis k := by
  induction k with
  | zero => simp [defect, den, iterate, exactIter, radius, times, minus]
  | succ k ih =>
    intro i
    let row := axis.rows i
    let raw := plus (times axis.D (x i)) (times axis.a (dot (iterate axis x k) row))
    rw [defectStep]
    exact calc
      _ ≤ _ := plusBound _ _
      _ ≤ den axis k * (2 * (axis.a * axis.D)) +
             axis.a * (mass row * (2 * B * den axis k)) := by
              simp only [timesRadius, Int.natAbs_natCast]
              exact Nat.add_le_add
                (Nat.mul_le_mul_left _ (truncateResidual _ hd raw))
                (Nat.mul_le_mul_left _ (dotBound _ _ ih row))
      _ = (2 * den axis k * axis.a) * (axis.D + B * mass row) := by grind
      _ ≤ (2 * den axis k * axis.a) * (B * axis.D) := Nat.mul_le_mul_left _ (hg i)
      _ = 2 * B * den axis (k+1) := by simp only [den, Nat.pow_succ]; grind

theorem finiteContraction (axis : Axis ι) (ha : Admitted axis) (x : ι → Datum)
    (R : Nat) (hx : ∀ i, radius (x i) ≤ R) (k : Nat) :
    ∀ i, radius (exactIter axis x k i) ≤ R * den axis k := by
  induction k with
  | zero => simp [exactIter, den, radius]
  | succ k ih =>
    intro i
    calc
      _ ≤ _ := plusBound _ _
      _ ≤ (axis.D * den axis k) * R +
           axis.a * (mass (axis.rows i) * (R * den axis k)) := by
        simp only [timesRadius, Int.natAbs_natCast]
        exact Nat.add_le_add (Nat.mul_le_mul_left _ (hx i))
          (Nat.mul_le_mul_left _ (dotBound _ _ ih (axis.rows i)))
      _ = (R * den axis k) * (axis.D + axis.a * mass (axis.rows i)) := by grind
      _ ≤ (R * den axis k) * (axis.a * axis.D) := Nat.mul_le_mul_left _ (ha.2 i)
      _ = R * den axis (k+1) := by simp [den, Nat.pow_succ, Nat.mul_assoc]

theorem scaleDot (row : Row ι) (z : ι → Datum) (n : Int) :
    dot (fun j => times n (z j)) row = times n (dot z row) := by
  induction row with
  | nil => simp [dot, times]
  | cons term tail ih =>
    obtain ⟨c,j⟩ := term
    simp only [dot]
    rw [ih]
    simp only [times, plus, Datum.mk.injEq]
    constructor <;> grind

def tailNumerator (axis : Axis ι) (x y : ι → Datum) (S k : Nat) (i : ι) : Datum :=
  minus (times (den axis k) (y i)) (times S (exactIter axis x k i))

private theorem fixedAlgebra (a d n s : Int) (x y row prev : Datum)
    (hf : times (a*d) y = plus (times (d*s) x) (times a row)) :
    minus (times (n*(a*d)) y) (times s (plus (times (d*n) x) (times a prev))) =
      times a (minus (times n row) (times s prev)) := by
  have hm : times (n*(a*d)) y = times n (times (a*d) y) := by simp [times, Int.mul_assoc]
  rw [hm, hf]
  simp only [times, plus, minus, Datum.mk.injEq]
  constructor <;> grind

def Fixed (axis : Axis ι) (x y : ι → Datum) (s : Nat) : Prop :=
  ∀ i, times (axis.a * axis.D : Nat) (y i) =
    plus (times (axis.D*s : Nat) (x i)) (times axis.a (dot y (axis.rows i)))

theorem tailStep (axis : Axis ι) (x y : ι → Datum) (s k : Nat) (hf : Fixed axis x y s) (i : ι) :
    tailNumerator axis x y s (k+1) i = times axis.a (dot (tailNumerator axis x y s k) (axis.rows i)) := by
  have hd := linearDot (axis.rows i) y (fun j => times s (exactIter axis x k j)) (den axis k)
  change dot (tailNumerator axis x y s k) (axis.rows i) = _ at hd
  rw [hd, scaleDot]
  simp only [tailNumerator, exactIter, den, Nat.pow_succ, Int.natCast_mul]
  apply fixedAlgebra
  simpa only [Int.natCast_mul] using hf i

/-- For a rational fixed point y/s, the finite Neumann numerator differs from
it by at most R (a m)^k at denominator s(aD)^k. The physical contraction
ratio is m/D, where m bounds the absolute row sum of encoded coefficients. -/
theorem geometricTail (axis : Axis ι) (x y : ι → Datum) (s m R : Nat)
    (hf : Fixed axis x y s) (hm : ∀ i, mass (axis.rows i) ≤ m)
    (hr : ∀ i, radius (y i) ≤ R) (k : Nat) :
    ∀ i, radius (tailNumerator axis x y s k i) ≤ R * (axis.a*m)^k := by
  induction k with
  | zero =>
    intro i
    simpa [tailNumerator, exactIter, den, minus, times, radius] using hr i
  | succ k ih =>
    intro i
    rw [tailStep _ _ _ _ _ hf, timesRadius, Int.natAbs_natCast]
    exact calc
      _ ≤ axis.a * (mass (axis.rows i) * (R * (axis.a*m)^k)) :=
          Nat.mul_le_mul_left _ (dotBound _ _ ih _)
      _ ≤ axis.a * (m * (R * (axis.a*m)^k)) :=
          Nat.mul_le_mul_left _ (Nat.mul_le_mul_right _ (hm i))
      _ = _ := by simp only [Nat.pow_succ]; grind

theorem dotSame (row : Row ι) (x y : ι → Datum) (h : ∀ term ∈ row, x term.2 = y term.2) :
    dot x row = dot y row := by
  induction row with
  | nil => rfl
  | cons item tail ih =>
    obtain ⟨w,j⟩ := item
    simp only [dot]
    rw [h (w,j) (by simp), ih (fun t ht => h t (List.mem_cons_of_mem _ ht))]

/-- Rows of the full and the principal polynomial agree whenever the entire
backward dependency cone stays inside the retained physical section. -/
theorem locality (a b : Axis ι) (x : ι → Datum) (zone : Nat → ι → Prop)
    (hd : a.D=b.D) (hs : a.a=b.a)
    (rows : ∀ k i, zone (k+1) i → a.rows i = b.rows i)
    (cone : ∀ k i, zone (k+1) i → ∀ term ∈ a.rows i, zone k term.2)
    (k : Nat) : ∀ i, zone k i → exactIter a x k i = exactIter b x k i := by
  induction k with
  | zero => intros; rfl
  | succ k ih =>
    intro i hi
    have eq := dotSame (a.rows i) _ _ (fun t ht => ih t.2 (cone k i hi t ht))
    rw [rows k i hi] at eq
    simp only [exactIter, den, hd, hs, rows k i hi, eq]

theorem roundedLocality (a b : Axis ι) (x : ι → Datum) (zone : Nat → ι → Prop)
    (hd : a.D=b.D) (hs : a.a=b.a)
    (rows : ∀ k i, zone (k+1) i → a.rows i = b.rows i)
    (cone : ∀ k i, zone (k+1) i → ∀ term ∈ a.rows i, zone k term.2)
    (k : Nat) : ∀ i, zone k i → iterate a x k i = iterate b x k i := by
  induction k with
  | zero => intros; rfl
  | succ k ih =>
    intro i hi
    have eq := dotSame (a.rows i) _ _ (fun t ht => ih t.2 (cone k i hi t ht))
    rw [rows k i hi] at eq
    simp only [iterate, update, hd, hs, rows k i hi, eq]

theorem dotZero (row : Row ι) : dot (fun _ => ⟨0,0⟩) row = ⟨0,0⟩ := by
  induction row with
  | nil => rfl
  | cons term tail ih =>
    obtain ⟨c,j⟩ := term
    simp only [dot, ih, times, plus, Int.mul_zero, Int.add_zero]

/-- In step one the incoming iterate is zero, so no input-band neighbor is
needed. This is the J-1 transition count of the physical shrinking rectangle. -/
theorem savedRectangle (a b : Axis ι) (x y : ι → Datum) (inside : Nat → ι → Prop)
    (hd : a.D=b.D) (hs : a.a=b.a)
    (source : ∀ k i, inside k i → x i=y i)
    (rows : ∀ k i, inside (k+1) i → a.rows i=b.rows i)
    (cone : ∀ k i, inside (k+1) i → ∀ term ∈ a.rows i, inside k term.2)
    (k : Nat) : ∀ i, inside k i →
      iterate a x (k+1) i = iterate b y (k+1) i ∧
      exactIter a x (k+1) i = exactIter b y (k+1) i := by
  induction k with
  | zero =>
    intro i hi
    simp [iterate, exactIter, update, den, dotZero, hd, hs, source _ i hi]
  | succ k ih =>
    intro i hi
    have hn := dotSame (a.rows i) _ _ (fun t ht => (ih t.2 (cone k i hi t ht)).1)
    have he := dotSame (a.rows i) _ _ (fun t ht => (ih t.2 (cone k i hi t ht)).2)
    rw [rows k i hi] at hn he
    constructor
    · change update a.D a.a (x i) (iterate a x (k+1)) (a.rows i) =
             update b.D b.a (y i) (iterate b y (k+1)) (b.rows i)
      simp only [update, hd, hs, source _ i hi, rows k i hi, hn]
    · change plus (times (a.D * den a (k+1) : Nat) (x i))
               (times a.a (dot (exactIter a x (k+1)) (a.rows i))) =
             plus (times (b.D * den b (k+1) : Nat) (y i))
               (times b.a (dot (exactIter b y (k+1)) (b.rows i)))
      simp only [den, hd, hs, source _ i hi, rows k i hi, he]

def inset (lo hi w : Int) (k : Nat) (i : Int) : Prop :=
  lo + k*w ≤ i ∧ i < hi - k*w

/-- Every physical neighbor at signed offset in [-w,w] stays inside the
previous lifted (possibly period-crossing) rectangle. -/
theorem physicalCone (lo hi w i j : Int) (k : Nat) (h : inset lo hi w (k+1) i)
    (left : i-w ≤ j) (right : j ≤ i+w) : inset lo hi w k j := by
  simp only [inset, Int.natCast_succ, Int.add_mul, Int.one_mul] at h ⊢
  omega

theorem linearExact (axis : Axis ι) (x y : ι → Datum) (n : Int) (k : Nat) :
    ∀ i, exactIter axis (fun i => minus (times n (x i)) (y i)) k i =
       minus (times n (exactIter axis x k i)) (exactIter axis y k i) := by
  induction k with
  | zero => simp [exactIter, times, minus]
  | succ k ih =>
    intro i
    simp only [exactIter]
    rw [funext ih, linearDot]
    simp only [minus, times, plus, Datum.mk.injEq]
    constructor <;> grind

/-- An exact input uses one integer denominator d for the entire field. -/
def Close (d e : Nat) (x y : ι → Datum) : Prop :=
  ∀ i, radius (minus (times d (x i)) (y i)) ≤ e * d

private theorem splitStep (s t : Int) (a b c : Datum) :
    minus (times (s*t) a) c = plus (times s (minus (times t a) b)) (minus (times s b) c) := by
  simp only [minus, times, plus, Datum.mk.injEq]
  constructor <;> grind

theorem nextExactComparison (axis : Axis ι) (ha : Admitted axis) (B : Nat)
    (hg : ∀ i, axis.D + B * mass (axis.rows i) ≤ B * axis.D)
    (s e : Nat) (x y : ι → Datum) (hc : Close s e x y) :
    Close (s * den axis axis.J) (e + 2*B) (iterate axis x axis.J) (exactIter axis y axis.J) := by
  intro i
  have hlin := linearExact axis x y s axis.J i
  have hcon := finiteContraction axis ha (fun j => minus (times s (x j)) (y j)) (e*s) hc axis.J i
  have hnum := finiteNeumannError axis x B ha.1 hg axis.J i
  simp only [Int.natCast_mul]
  rw [splitStep (s : Int) (den axis axis.J) _ (exactIter axis x axis.J i) _, ← hlin]
  calc
    _ ≤ _ := plusBound _ _
    _ ≤ s * (2*B*den axis axis.J) + e*s*den axis axis.J := by
      rw [timesRadius, Int.natAbs_natCast]
      exact Nat.add_le_add (Nat.mul_le_mul_left s hnum) hcon
    _ = _ := by grind

def exactSweep (x : ι → Datum) : List (Axis ι) → ι → Datum
  | [] => x
  | a :: rest => exactSweep (exactIter a x a.J) rest

def sweepDen (axes : List (Axis ι)) : Nat := (axes.map fun a => den a a.J).prod

/-- Rounded successive axis evaluations are compared at their actual inputs.
No linearity or one-Lipschitz assertion about the rounded operation is needed. -/
theorem spectralNumeratorError (axes : List (Axis ι)) (B s e : Nat) (x y : ι → Datum)
    (ha : ∀ a ∈ axes, Admitted a ∧ ∀ i, a.D+B*mass (a.rows i) ≤ B*a.D)
    (hc : Close s e x y) :
    Close (s * sweepDen axes) (e + 2*B*axes.length) (sweep x axes) (exactSweep y axes) := by
  induction axes generalizing s e x y with
  | nil => simpa [sweepDen, sweep, exactSweep] using hc
  | cons a rest ih =>
    have h := ha a (by simp)
    have step := nextExactComparison a h.1 B h.2 s e x y hc
    have tail := ih (s*den a a.J) (e+2*B) _ _
      (fun t ht => ha t (List.mem_cons_of_mem _ ht)) step
    simpa [sweep, exactSweep, sweepDen, Nat.mul_assoc, Nat.mul_add,
      Nat.add_assoc, Nat.add_comm, Nat.add_left_comm] using tail

def splice (keep : ι → Bool) (core face : ι → Datum) (i : ι) : Datum :=
  if keep i then core i else face i

/-- At fixed denominator all first-face and kept-row returns have disjoint ownership. -/
theorem disjointSplice (keep : ι → Bool) (core face ideal : ι → Datum)
    (d ec ef : Nat)
    (hc : ∀ i, keep i = true → radius (minus (times d (core i)) (ideal i)) ≤ ec*d)
    (hf : ∀ i, keep i = false → radius (minus (times d (face i)) (ideal i)) ≤ ef*d) :
    Close d (max ec ef) (splice keep core face) ideal := by
  intro i
  cases h : keep i with
  | false =>
    simpa [splice, h] using Nat.le_trans (hf i h) (Nat.mul_le_mul_right d (Nat.le_max_right ec ef))
  | true =>
    simpa [splice, h] using Nat.le_trans (hc i h) (Nat.mul_le_mul_right d (Nat.le_max_left ec ef))

private theorem differenceTriangle (x y z : Datum) :
    radius (minus x z) ≤ radius (minus x y) + radius (minus z y) := by
  have re : x.re-z.re = (x.re-y.re) + -(z.re-y.re) := by omega
  have im : x.im-z.im = (x.im-y.im) + -(z.im-y.im) := by omega
  have hr := Int.natAbs_add_le (x.re-y.re) (-(z.re-y.re))
  have hi := Int.natAbs_add_le (x.im-y.im) (-(z.im-y.im))
  rw [← re, Int.natAbs_neg] at hr
  rw [← im, Int.natAbs_neg] at hi
  simp only [radius, minus]
  omega

private theorem commonDenominator (s d : Nat) (x y : Datum) :
    minus (times (s*d : Nat) x) (times d y) = times d (minus (times s x) y) := by
  simp only [times, minus, Int.natCast_mul, Datum.mk.injEq]
  constructor <;> grind

/-- Both ideal fields have denominator S. The tail bound is rounded upward
to t grid units, so the final integer bound adds t to the numerical bill. -/
theorem compareToInverse (axis : Axis ι) (B S e R m t : Nat)
    (actual before after : ι → Datum) (ha : Admitted axis)
    (hg : ∀ i, axis.D + B * mass (axis.rows i) ≤ B * axis.D)
    (hm : ∀ i, mass (axis.rows i) ≤ m) (hf : Fixed axis before after 1)
    (hr : ∀ i, radius (after i) ≤ R) (small : R*(axis.a*m)^axis.J ≤ t*S*den axis axis.J)
    (hc : Close S e actual before) :
    Close S (e + 2*B + t) (iterate axis actual axis.J) after := by
  intro i
  have hn := nextExactComparison axis ha B hg S e actual before hc i
  have ht := geometricTail axis before after 1 m R hf hm hr axis.J i
  have hone (v : Datum) : times 1 v = v := by cases v; simp [times]
  have oneCast : ((1 : Nat) : Int) = 1 := rfl
  simp only [tailNumerator, oneCast, hone] at ht
  have both := differenceTriangle
    (times (S*den axis axis.J : Nat) (iterate axis actual axis.J i))
    (exactIter axis before axis.J i) (times (den axis axis.J) (after i))
  rw [commonDenominator, timesRadius, Int.natAbs_natCast] at both
  have sum := Nat.add_le_add hn (Nat.le_trans ht small)
  have hc' := Nat.le_trans both sum
  have hd : 0 < den axis axis.J := Nat.pow_pos ha.1
  apply Nat.le_of_mul_le_mul_left (c := den axis axis.J) (hc := hd)
  calc
    _ ≤ _ := hc'
    _ = _ := by grind

/-- The mathematical inverse trajectory is expressed by its exact rational
linear equations. The algorithm consumes none of these fields at runtime. -/
inductive InverseChain (B S t : Nat) : List (Axis ι) → (ι → Datum) → (ι → Datum) → Prop
  | nil (v : ι → Datum) : InverseChain B S t [] v v
  | cons (a : Axis ι) (tail : List (Axis ι)) (x y z : ι → Datum) (R m : Nat)
      (ha : Admitted a) (hg : ∀ i, a.D + B * mass (a.rows i) ≤ B * a.D)
      (hm : ∀ i, mass (a.rows i) ≤ m) (hf : Fixed a x y 1) (hr : ∀ i, radius (y i) ≤ R)
      (small : R*(a.a*m)^a.J ≤ t*S*den a a.J) (rest : InverseChain B S t tail y z) :
      InverseChain B S t (a::tail) x z

/-- Rounded physical iteration over all axes versus the full normalized
inverse, including the geometric tails and actual-input error at every stage. -/
theorem completeInverseError (axes : List (Axis ι)) (B S t e : Nat)
    (actual before after : ι → Datum) (chain : InverseChain B S t axes before after)
    (hc : Close S e actual before) :
    Close S (e + (2*B+t)*axes.length) (sweep actual axes) after := by
  induction chain generalizing actual e with
  | nil => simpa [sweep] using hc
  | cons a tail x y z R m ha hg hm hf hr small rest ih =>
    have hs := compareToInverse a B S e R m t actual x y ha hg hm hf hr small hc
    have combined := ih (e := e + 2*B + t) (actual := iterate a actual a.J) hs
    simpa [sweep, Nat.mul_add, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm] using combined

#print axioms updateBound
#print axioms eachIteration
#print axioms everyAxis
#print axioms finiteNeumannError
#print axioms geometricTail
#print axioms locality
#print axioms roundedLocality
#print axioms savedRectangle
#print axioms physicalCone
#print axioms spectralNumeratorError
#print axioms disjointSplice
#print axioms completeInverseError

end HaloRadius
