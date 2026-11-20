import HaloRadius

namespace RationalInverse

/-- A finite row sum in physical coordinate order. -/
def isum (f : Fin n → Int) : Int := (List.ofFn f).sum

@[simp] theorem sumEmpty (f : Fin 0 → Int) : isum f = 0 := by simp [isum]
theorem sumStep (f : Fin (n+1) → Int) : isum f = f 0 + isum (fun j => f j.succ) := by simp [isum, List.ofFn_succ]

theorem sumAdd (f g : Fin n → Int) : isum (fun i => f i+g i) = isum f + isum g := by
  induction n with
  | zero => simp
  | succ n ih => simpa only [sumStep, ih] using (show (f 0 + g 0) + (isum (fun i : Fin n => f i.succ) + isum (fun i : Fin n => g i.succ)) = (f 0 + isum (fun i : Fin n => f i.succ)) + (g 0 + isum (fun i : Fin n => g i.succ)) by omega)

theorem sumScale (c : Int) (f : Fin n → Int) : isum (fun i => c*f i) = c*isum f := by
  induction n with
  | zero => simp
  | succ n ih => rw [sumStep, sumStep f, Int.mul_add, ← ih]

theorem sumSub (f g : Fin n → Int) : isum (fun i => f i-g i) = isum f - isum g := by
  induction n with
  | zero => simp
  | succ n ih => rw [sumStep, sumStep f, sumStep g, ih]; omega

theorem sumLe {f g : Fin n → Int} (h : ∀ i, f i ≤ g i) : isum f ≤ isum g := by
  induction n with
  | zero => simp
  | succ n ih => rw [sumStep f, sumStep g]; exact Int.add_le_add (h _) (ih (fun i => h i.succ))

@[simp] theorem sumZero {n} : isum (fun _ : Fin n => 0) = 0 := by
  induction n with
  | zero => simp
  | succ n ih => rw [sumStep, ih]; simp

@[simp] theorem firstNeLater (i : Fin n) : (0 : Fin (n+1)) ≠ i.succ := Ne.symm (Fin.succ_ne_zero i)

@[simp] theorem sumSingle (i : Fin n) (x : Int) : isum (fun j => if j=i then x else 0) = x := by
  induction n with
  | zero => exact Fin.elim0 i
  | succ n ih =>
    cases i using Fin.cases with
    | zero => simp [sumStep, Fin.succ_ne_zero]
    | succ i => simpa [sumStep, Fin.succ_inj] using ih i

def amag (v : Int) : Int := (v.natAbs : Int)
@[simp] theorem magNonneg (v : Int) : 0 ≤ amag v := by simp [amag]
@[simp] theorem magZero : amag 0=0 := rfl
@[simp] theorem magMul (a b : Int) : amag (a*b) = amag a*amag b := by simp [amag, Int.natAbs_mul]
@[simp] theorem magNeg (a : Int) : amag (-a)=amag a := by simp [amag]
theorem magSub (a b : Int) : amag (a-b) ≤ amag a+amag b := by simpa [amag] using (Int.ofNat_le.mpr (Int.natAbs_sub_le a b))
theorem magPos (a : Int) (h : 0 ≤ a) : amag a=a := Int.natAbs_of_nonneg h
theorem leMag (a : Int) : a ≤ amag a := Int.le_natAbs

abbrev Matrix (n : Nat) := Fin n → Fin n → Int

def offDiag (row : Fin n → Int) (i : Fin n) : Int := isum (fun j => if j=i then 0 else amag (row j))
def norm1 (row : Fin n → Int) : Int := isum (fun j => amag (row j))
def Dominant (A : Matrix n) : Prop := ∀ i, offDiag (A i) i < A i i

theorem offNonneg (f : Fin n → Int) (i : Fin n) : 0 ≤ offDiag f i := by
  change 0 ≤ isum _
  rw [← @sumZero n]
  apply sumLe
  intro j
  split <;> simp

theorem offSplit (f : Fin n → Int) (i : Fin n) : offDiag f i + amag (f i) = norm1 f := by
  unfold offDiag norm1
  rw [← sumSingle i (amag (f i)), ← sumAdd]
  congr 1; funext j; split <;> simp_all

@[simp] theorem offFirst (f : Fin (n+1) → Int) : offDiag f 0 = norm1 (fun j => f j.succ) := by simp [offDiag, norm1, sumStep, Fin.succ_ne_zero]
@[simp] theorem offLater (f : Fin (n+1) → Int) (i : Fin n) : offDiag f i.succ = amag (f 0) + offDiag (fun j => f j.succ) i := by simp [offDiag, sumStep, Fin.succ_inj]

def schur (A : Matrix (n+1)) : Matrix n := fun i j => A 0 0 * A i.succ j.succ - A i.succ 0 * A 0 j.succ

theorem schurOff (A : Matrix (n+1)) (hA : Dominant A) (i : Fin n) :
    offDiag (schur A i) i ≤ A 0 0 * offDiag (fun j => A i.succ j.succ) i + amag (A i.succ 0) * offDiag (fun j => A 0 j.succ) i := by
  have hpos : 0 ≤ A 0 0 := Int.le_trans (offNonneg _ _) (Int.le_of_lt (hA 0))
  unfold offDiag
  rw [← sumScale, ← sumScale, ← sumAdd]
  apply sumLe; intro j; by_cases hj : j=i
  · simp [hj]
  · simp only [hj, ↓reduceIte, schur]
    simpa only [magMul, magPos _ hpos] using magSub (A 0 0 * A i.succ j.succ) (A i.succ 0 * A 0 j.succ)

theorem schurDominant (A : Matrix (n+1)) (ha : Dominant A) : Dominant (schur A) := by
  intro i
  have hp : 0 < A 0 0 := Int.lt_of_le_of_lt (offNonneg _ _) (ha 0)
  have h0 := ha 0
  rw [offFirst] at h0
  have hi := ha i.succ
  rw [offLater] at hi
  have hscale := Int.mul_lt_mul_of_pos_left hi hp
  have hsplit := offSplit (fun j : Fin n => A 0 j.succ) i
  have hcol := Int.mul_le_mul_of_nonneg_left (Int.le_of_lt h0) (magNonneg (A i.succ 0))
  have hcross := leMag (A i.succ 0 * A 0 i.succ)
  rw [magMul] at hcross
  have hoff := schurOff A ha i
  change offDiag (schur A i) i < A 0 0 * A i.succ i.succ - A i.succ 0 * A 0 i.succ
  rw [← hsplit, Int.mul_add] at hcol
  rw [Int.mul_add] at hscale
  grind


/-- Evaluate the dense row after collecting equal physical addresses. -/
def act (A : Matrix n) (x : Fin n → Int) (i : Fin n) : Int := isum (fun j => A i j*x j)

theorem schurAct (A : Matrix (n+1)) (y : Fin n → Int) (i : Fin n) :
    act (schur A) y i = A 0 0 * isum (fun j => A i.succ j.succ*y j) - A i.succ 0 * isum (fun j => A 0 j.succ*y j) := by
  unfold act schur
  rw [← sumScale, ← sumScale, ← sumSub]
  congr 1; funext j; grind

theorem tailScaled (p : Int) (row x : Fin n → Int) : isum (fun j => row j*(p*x j)) = p*isum (fun j => row j*x j) := by
  rw [← sumScale]; congr 1; funext j; grind

/-- Fraction-free elimination produces a positive common denominator and an exact
solution for every integer right hand side. The pivot need not be a unit. -/
theorem solve (A : Matrix n) (ha : Dominant A) (rhs : Fin n → Int) :
    ∃ S : Int, 0 < S ∧ ∃ y : Fin n → Int, ∀ i, act A y i = S * rhs i := by
  induction n with
  | zero => exact ⟨1, by decide, Fin.elim0, fun i => i.elim0⟩
  | succ n ih =>
    have hp : 0 < A 0 0 := Int.lt_of_le_of_lt (offNonneg _ _) (ha 0)
    obtain ⟨s, hs, y, hy⟩ := ih (schur A) (schurDominant A ha) (fun i => A 0 0 * rhs i.succ - A i.succ 0 * rhs 0)
    let w := s*rhs 0 - isum (fun j => A 0 j.succ*y j)
    let z : Fin (n+1) → Int := Fin.cases w (fun j => A 0 0*y j)
    refine ⟨A 0 0*s, Int.mul_pos hp hs, z, ?_⟩
    intro i; cases i using Fin.cases with
    | zero =>
      simp only [act, sumStep, z, Fin.cases_zero, Fin.cases_succ, tailScaled, w]
      grind
    | succ i =>
      have h := hy i
      rw [schurAct] at h
      simp only [act, sumStep, z, Fin.cases_zero, Fin.cases_succ, tailScaled, w]
      grind

#print axioms schurDominant
#print axioms solve


open HaloRadius

/-- Physical rows can contain repeated signed period indices. Collect their
signed coefficients, while retaining their original absolute mass bound. -/
def entry : Row (Fin n) → Fin n → Int
  | [], _ => 0
  | (c,k)::r, j => (if j=k then c else 0) + entry r j

def scalarDot (f : Fin n → Int) : Row (Fin n) → Int
  | [] => 0
  | (c,j)::r => c*f j + scalarDot f r

theorem physicalSum (row : Row (Fin n)) (f : Fin n → Int) :
    isum (fun j => entry row j * f j) = scalarDot f row := by
  induction row with
  | nil => simp [entry, scalarDot]
  | cons term row ih =>
    obtain ⟨c,k⟩ := term
    simp only [entry, scalarDot, Int.add_mul, sumAdd, ih]
    congr 1
    rw [← sumSingle k (c*f k)]
    congr 1; funext j; by_cases h : j=k <;> simp [h]

theorem eachPhysicalComponent (row : Row (Fin n)) (f : Fin n → Datum) :
    (dot f row).re = scalarDot (fun j => (f j).re) row ∧ (dot f row).im = scalarDot (fun j => (f j).im) row := by
  induction row with
  | nil => simp [dot, scalarDot]
  | cons term row ih =>
    obtain ⟨c,k⟩ := term
    simp [dot, plus, times, scalarDot, ih]

theorem entryNorm (row : Row (Fin n)) : norm1 (entry row) ≤ (mass row : Int) := by
  induction row with
  | nil => simp [entry, norm1, mass]
  | cons term row ih =>
    obtain ⟨c,k⟩ := term
    have hdis : norm1 (entry ((c,k)::row)) ≤ amag c + norm1 (entry row) := by
      unfold norm1
      rw [← sumSingle k (amag c), ← sumAdd]
      apply sumLe; intro j; by_cases hj : j=k
      · subst j
        simpa [entry, amag] using Int.ofNat_le.mpr (Int.natAbs_add_le c (entry row k))
      · simp [entry, hj]
    unfold mass at *
    simp only [List.map_cons, List.sum_cons, Int.natCast_add]
    exact Int.le_trans hdis (Int.add_le_add_left ih _)

def physicalMatrix (a : Axis (Fin n)) : Matrix n := fun i j => (if j=i then (a.D : Int) else 0) - entry (a.rows i) j

theorem perRowMass (a : Axis (Fin n)) (ha : Admitted a) (i : Fin n) : mass (a.rows i) < a.D := by
  have hp := ha.1
  have hg := ha.2 i
  have hd : 0 < a.D := Nat.pos_of_mul_pos_left hp
  by_cases h : mass (a.rows i) < a.D
  · exact h
  · have hmul := Nat.mul_le_mul_left a.a (Nat.le_of_not_gt h)
    omega

theorem physicalDominant (a : Axis (Fin n)) (ha : Admitted a) : Dominant (physicalMatrix a) := by
  intro i
  have he : offDiag (physicalMatrix a i) i = offDiag (entry (a.rows i)) i := by
    unfold offDiag; congr 1; funext j; by_cases h : j=i <;> simp [h, physicalMatrix]
  rw [he]
  have hmass := entryNorm (a.rows i)
  have hdiag := offSplit (entry (a.rows i)) i
  have hpos := Int.ofNat_lt.mpr (perRowMass a ha i)
  have he := leMag (entry (a.rows i) i)
  simp only [physicalMatrix, ↓reduceIte]
  omega

theorem physicalAction (a : Axis (Fin n)) (f : Fin n → Int) (i : Fin n) :
    act (physicalMatrix a) f i = a.D*f i - scalarDot f (a.rows i) := by
  simp only [act, physicalMatrix, Int.sub_mul, sumSub, physicalSum]
  congr 1; rw [← sumSingle i (a.D*f i)]; congr 1; funext j; by_cases h : j=i <;> simp [h]

theorem scaledPhysicalDot (f : Fin n → Int) (c : Int) (row : Row (Fin n)) :
    scalarDot (fun j => c*f j) row = c*scalarDot f row := by
  induction row with
  | nil => simp [scalarDot]
  | cons term row ih => obtain ⟨w,j⟩ := term; simp only [scalarDot, ih]; grind

/-- Every admitted, finite physical row system has an exact rational normalized
inverse on every complex integer input. No mathematical inverse is an input. -/
theorem inverseExists (a : Axis (Fin n)) (ha : Admitted a) (x : Fin n → Datum) :
    ∃ s : Nat, 0 < s ∧ ∃ y : Fin n → Datum, Fixed a x y s := by
  have hm := physicalDominant a ha
  obtain ⟨r, hr, u, hu⟩ := solve (physicalMatrix a) hm (fun i => (a.D : Int)*(x i).re)
  obtain ⟨s, hs, v, hv⟩ := solve (physicalMatrix a) hm (fun i => (a.D : Int)*(x i).im)
  let y : Fin n → Datum := fun j => ⟨s*u j, r*v j⟩
  have hnat : 0 < a.a * r.toNat*s.toNat := Nat.mul_pos (Nat.mul_pos (Nat.pos_of_mul_pos_right ha.1) (by omega)) (by omega)
  refine ⟨a.a*r.toNat*s.toNat, hnat, y, ?_⟩
  intro i
  have h1 := hu i; have h2 := hv i
  rw [physicalAction] at h1 h2
  obtain ⟨er, ei⟩ := eachPhysicalComponent (a.rows i) y
  simp only [y, scaledPhysicalDot] at er ei
  simp only [y, times, plus, Datum.mk.injEq, Int.natCast_mul, Int.toNat_of_nonneg (Int.le_of_lt hr), Int.toNat_of_nonneg (Int.le_of_lt hs)]
  change _ = _ + _*(dot y (a.rows i)).re ∧ _ = _ + _*(dot y (a.rows i)).im
  rw [er, ei]; constructor <;> grind

#print axioms inverseExists


/-- A finite nonempty field attains its largest component radius. -/
theorem attainment (f : Fin (n+1) → Nat) : ∃ k, ∀ j, f j ≤ f k := by
  induction n with
  | zero =>
    refine ⟨0, ?_⟩; intro j
    have h : j=0 := Fin.ext (by have := j.isLt; change j.val=0; omega)
    rw [h]; exact Nat.le_refl _
  | succ n ih =>
    obtain ⟨k, hk⟩ := ih (fun j => f j.succ)
    by_cases h : f 0 ≤ f k.succ
    · refine ⟨k.succ, ?_⟩; intro j; cases j using Fin.cases with
      | zero => exact h
      | succ j => exact hk j
    · refine ⟨0, ?_⟩; intro j; cases j using Fin.cases with
      | zero => exact Nat.le_refl _
      | succ j => exact Nat.le_trans (hk j) (Nat.le_of_lt (Nat.lt_of_not_ge h))

/-- Normalization makes the exact normalized inverse a contraction in the
same component-l1 radius as the actual rounded iteration. -/
theorem inverseContraction (a : Axis (Fin n)) (ha : Admitted a) (x y : Fin n → Datum) (s R : Nat)
    (hf : Fixed a x y s) (hx : ∀ i, radius (x i) ≤ R) : ∀ i, radius (y i) ≤ s*R := by
  cases n with
  | zero => exact fun i => i.elim0
  | succ n =>
    obtain ⟨k, hk⟩ := attainment (fun j => radius (y j))
    let M := radius (y k)
    have hright : (a.a*a.D)*M ≤ (a.D*s)*R + a.a*(mass (a.rows k)*M) := by
      calc
        _ = radius (times (a.a*a.D : Nat) (y k)) := by simp [M, timesRadius, Int.natAbs_mul]
        _ ≤ radius (times (a.D*s : Nat) (x k)) + radius (times a.a (dot y (a.rows k))) := by rw [hf]; exact plusBound ..
        _ ≤ _ := by simp only [timesRadius, Int.natAbs_natCast]; exact Nat.add_le_add (Nat.mul_le_mul_left _ (hx k)) (Nat.mul_le_mul_left _ (dotBound y M hk _))
    have hleft := Nat.mul_le_mul_right M (ha.2 k)
    have hboth := Nat.le_trans hleft hright
    rw [Nat.add_mul, Nat.mul_assoc a.a] at hboth
    have hbound : M ≤ s*R := Nat.le_of_mul_le_mul_left (c:=a.D) (hc:=Nat.pos_of_mul_pos_left ha.1) (by simpa [Nat.mul_assoc] using Nat.le_of_add_le_add_right hboth)
    exact fun i => Nat.le_trans (hk i) hbound

private theorem scaleInput (a : Axis (Fin n)) (x y : Fin n → Datum) (s c : Nat) (hf : Fixed a x y s) :
    Fixed a (fun i => times (c*s : Nat) (x i)) (fun i => times c (y i)) 1 := by
  intro i; rw [scaleDot]
  have h := hf i
  have xp := congrArg Datum.re h; have xq := congrArg Datum.im h
  simp only [times, plus, Int.natCast_mul] at xp xq
  simp only [times, plus, Datum.mk.injEq, Nat.mul_one, Int.natCast_mul]
  constructor <;> grind

/-- For a fixed family radius R and P-grid tail tolerance t, this condition
only asks about the generated grid, row mass and the specified iteration count. -/
def Ready (B t R : Nat) (a : Axis (Fin n)) : Prop := Admitted a ∧
    (∀ i, a.D+B*mass (a.rows i) ≤ B*a.D) ∧
    ∃ m, (∀ i, mass (a.rows i) ≤ m) ∧ R*(a.a*m)^a.J ≤ t*den a a.J

/-- Construct a common positive denominator for every exact intermediate
and final field. Its size does not enter the tape algorithm or the error. -/
theorem trajectory (axes : List (Axis (Fin n))) (B t R S : Nat) (x : Fin n → Datum)
    (ready : ∀ a ∈ axes, Ready B t R a) (bound : ∀ i, radius (x i) ≤ S*R) :
    ∃ c : Nat, 0 < c ∧ ∃ y : Fin n → Datum,
      InverseChain B (c*S) t axes (fun i => times c (x i)) y ∧ ∀ i, radius (y i) ≤ (c*S)*R := by
  induction axes generalizing S x with
  | nil =>
    refine ⟨1, by decide, (fun i => times (1 : Nat) (x i)), .nil _, ?_⟩
    intro i; simpa [timesRadius] using bound i
  | cons a tail ih =>
    obtain ⟨ha, hg, m, hm, ht⟩ := ready a (by simp)
    obtain ⟨s, hs, y, hf⟩ := inverseExists a ha x
    have hy : ∀ i, radius (y i) ≤ (s*S)*R := fun i => by simpa [Nat.mul_assoc] using inverseContraction a ha x y s (S*R) hf bound i
    obtain ⟨c, hc, z, hz, hzb⟩ := ih (s*S) y (fun b hb => ready b (by simp [hb])) hy
    refine ⟨c*s, Nat.mul_pos hc hs, z, ?_, ?_⟩
    · apply InverseChain.cons a tail _ (fun i => times c (y i)) _ (((c*s)*S)*R) m ha hg hm (scaleInput a x y s c hf)
      · intro i; rw [timesRadius, Int.natAbs_natCast]; simpa [Nat.mul_assoc] using Nat.mul_le_mul_left c (hy i)
      · have hscl := Nat.mul_le_mul_left ((c*s)*S) ht
        simpa [Nat.mul_assoc, Nat.mul_comm, Nat.mul_left_comm] using hscl
      · simpa only [Nat.mul_assoc] using hz
    · simpa only [Nat.mul_assoc] using hzb

/-- Unconditional on existence of inverse values: every admitted finite
physical band list has its unique normalized rational inverse output, and the
literal P-grid evaluation meets the accumulated radius bound on any input. -/
theorem physicalInverseError (axes : List (Axis (Fin n))) (B t R : Nat) (x : Fin n → Datum)
    (ready : ∀ a ∈ axes, Ready B t R a) (bound : ∀ i, radius (x i) ≤ R) :
    ∃ S : Nat, 0 < S ∧ ∃ y : Fin n → Datum,
      InverseChain B S t axes (fun i => times S (x i)) y ∧
      Close S ((2*B+t)*axes.length) (sweep x axes) y := by
  obtain ⟨s, hs, y, h, _⟩ := trajectory axes B t R 1 x ready (by simpa using bound)
  rw [Nat.mul_one] at h
  refine ⟨s, hs, y, h, ?_⟩
  have hc : Close s 0 x (fun i => times s (x i)) := by intro i; simp [minus, radius]
  simpa using completeInverseError axes B s t 0 x _ y h hc

#print axioms inverseContraction
#print axioms trajectory
#print axioms physicalInverseError


/-- Cross-multiply exact input and output numerators. Equal rational inputs
to a normalized row solve have equal rational outputs at any denominators. -/
theorem uniqueStep (a : Axis (Fin n)) (ha : Admitted a) (r s : Nat)
    (x u y z : Fin n → Datum) (hy : Fixed a x y 1) (hz : Fixed a u z 1)
    (he : ∀ i, times r (x i) = times s (u i)) :
    ∀ i, times r (y i) = times s (z i) := by
  let dif := fun i => minus (times r (y i)) (times s (z i))
  let zeroField : Fin n → Datum := fun _ => ⟨0,0⟩
  have hf : Fixed a zeroField dif 1 := by
    intro i; dsimp only [dif]
    rw [linearDot, scaleDot]
    have p := hy i; have q := hz i; have e := he i
    have pr := congrArg Datum.re p; have pi := congrArg Datum.im p
    have qr := congrArg Datum.re q; have qi := congrArg Datum.im q
    have er := congrArg Datum.re e; have ei := congrArg Datum.im e
    simp only [times, plus, Nat.mul_one, Int.natCast_mul] at pr pi qr qi er ei
    simp only [zeroField, times, plus, minus, Int.mul_zero, Int.zero_add, Int.natCast_mul, Datum.mk.injEq]
    constructor <;> grind
  intro i
  have h := inverseContraction a ha zeroField dif 1 0 hf (fun _ => by simp [zeroField, radius]) i
  simp [dif, radius, minus] at h
  simp only [times, Datum.mk.injEq] at h ⊢
  constructor <;> omega

/-- Every exact inverse trajectory on the same physical bands has the
same rational result, including different common denominators. -/
theorem uniqueTrajectory (axes : List (Axis (Fin n))) (B t S T r s : Nat)
    (x u y z : Fin n → Datum) (one : InverseChain B S t axes x y) (two : InverseChain B T t axes u z)
    (he : ∀ i, times r (x i) = times s (u i)) : ∀ i, times r (y i) = times s (z i) := by
  induction one generalizing u z with
  | nil x => cases two; exact he
  | cons a tail x mid y R m ha hg hm hf hr hsmall rest ih =>
    cases two with
    | cons _ _ _ next _ _ _ _ _ _ hnext _ _ rest2 =>
      exact ih next z rest2 (uniqueStep a ha r s x u mid next hf hnext he)

/-- The returned exact target exists and is unique as a rational field.
The final error includes every normalized inverse and all actual grid sweeps. -/
theorem actualGaussianInverse (axes : List (Axis (Fin n))) (B t R : Nat) (x : Fin n → Datum)
    (ready : ∀ a ∈ axes, Ready B t R a) (bound : ∀ i, radius (x i) ≤ R) :
    ∃ S : Nat, 0 < S ∧ ∃ y : Fin n → Datum,
      InverseChain B S t axes (fun i => times S (x i)) y ∧
      Close S ((2*B+t)*axes.length) (sweep x axes) y ∧
      ∀ (T : Nat) (z : Fin n → Datum), InverseChain B T t axes (fun i => times T (x i)) z →
        ∀ i, times T (y i) = times S (z i) := by
  obtain ⟨s, hs, y, h, close⟩ := physicalInverseError axes B t R x ready bound
  refine ⟨s, hs, y, h, close, ?_⟩
  intro T z h2
  apply uniqueTrajectory axes B t s T T s _ _ y z h h2
  intro i; simp only [times, Datum.mk.injEq]; constructor <;> grind

#print axioms uniqueStep
#print axioms uniqueTrajectory
#print axioms actualGaussianInverse


/-- The first two terms of the binomial expansion suffice for a discrete
geometric tail bound. This proof uses integer powers alone. -/
theorem binomialLower (m g j : Nat) : m^(j+1) + (j+1)*g*m^j ≤ (m+g)^(j+1) := by
  induction j with
  | zero => simp
  | succ j ih =>
    calc
      _ ≤ m^(j+1+1) + (j+1+1)*g*m^(j+1) + (j+1)*g*g*m^j := Nat.le_add_right _ _
      _ = (m^(j+1) + (j+1)*g*m^j)*(m+g) := by rw [Nat.pow_succ m (j+1), Nat.pow_succ m j]; grind
      _ ≤ (m+g)^(j+1)*(m+g) := Nat.mul_le_mul_right _ ih
      _ = _ := (Nat.pow_succ _ _).symm

theorem halfInOneBlock (B D m : Nat) (hB : 0<B) (hD : 0<D) (hg : D+B*m ≤ B*D) :
    2*m^B ≤ D^B := by
  have hm : m ≤ D := by
    by_cases h : m≤D
    · exact h
    · have hm := Nat.mul_le_mul_left B (Nat.le_of_not_ge h)
      omega
  let g := D-m
  have hs : m+g=D := by dsimp [g]; omega
  have hmg : m ≤ B*g := by
    rw [← hs, Nat.mul_add] at hg
    omega
  cases B with
  | zero => omega
  | succ b =>
    have hprod := Nat.mul_le_mul_right (m^b) hmg
    have first : 2*m^(b+1) ≤ m^(b+1) + (b+1)*g*m^b := by rw [Nat.pow_succ]; grind
    exact Nat.le_trans first (by simpa only [hs] using binomialLower m g b)

/-- A row contraction 1-1/B loses at least one binary bit every B
steps, uniformly for every matrix grid D and maximum physical row mass. -/
theorem poweredTail (B D m j H : Nat) (hB : 0<B) (hD : 0<D) (hg : D+B*m ≤ B*D)
    (hj : B*H ≤ j) : 2^H*m^j ≤ D^j := by
  have hm : m ≤ D := by
    by_cases h : m≤D
    · exact h
    · have hm := Nat.mul_le_mul_left B (Nat.le_of_not_ge h); omega
  let rem := j-B*H
  have hs : B*H+rem=j := by dsimp [rem]; omega
  have blk := Nat.pow_le_pow_left (halfInOneBlock B D m hB hD hg) H
  have hb : 2^H * m^(B*H) ≤ D^(B*H) := by simpa only [Nat.mul_pow, Nat.pow_mul] using blk
  have hrest := Nat.pow_le_pow_left hm rem
  have total := Nat.mul_le_mul hb hrest
  rw [← hs, Nat.pow_add, Nat.pow_add]
  simpa only [Nat.mul_assoc] using total

/-- The row hypotheses and sweep count imply the one-grid-unit tail without
a supplied analytic or floating-point tail estimate. -/
theorem readyFromGrid (a : Axis (Fin n)) (B H R : Nat) (hB : 0<B) (ha : Admitted a)
    (hg : ∀ i, a.D + B*mass (a.rows i) ≤ B*a.D) (bits : R ≤ 2^H) (length : B*H ≤ a.J) : Ready B 1 R a := by
  refine ⟨ha, hg, ?_⟩
  have hd := Nat.pos_of_mul_pos_left ha.1
  have hm : ∃ m, (∀ i, mass (a.rows i) ≤ m) ∧ a.D+B*m ≤ B*a.D := by
    cases n with
    | zero =>
      refine ⟨0, fun i => i.elim0, ?_⟩
      simpa using Nat.mul_le_mul_right a.D (show 1 ≤ B by omega)
    | succ n =>
      obtain ⟨k, hk⟩ := attainment (fun j => mass (a.rows j))
      exact ⟨mass (a.rows k), hk, hg k⟩
  obtain ⟨m, hm, gap⟩ := hm
  refine ⟨m, hm, ?_⟩
  have h1 := Nat.le_trans (Nat.mul_le_mul_right (m^a.J) bits) (poweredTail B a.D m a.J H hB hd gap length)
  have h2 := Nat.mul_le_mul_left (a.a^a.J) h1
  simpa [den, Nat.mul_pow, Nat.mul_assoc, Nat.mul_comm, Nat.mul_left_comm] using h2

/-- Fine-family specialization. The generated absolute row mass and common
dyadic normalizer imply accuracy on all inputs with numerator radius 2^(p²).
The implementation uses P=Cp bits, below p² for all sufficiently large p. -/
theorem fineGaussianInverse (axes : List (Axis (Fin n))) (p : Nat) (x : Fin n → Datum)
    (hp : 0<p) (bound : ∀ i, radius (x i) ≤ 2^(p*p))
    (admitted : ∀ a ∈ axes, Admitted a)
    (gap : ∀ a ∈ axes, ∀ i, a.D+(16*p*p)*mass (a.rows i) ≤ (16*p*p)*a.D)
    (sweeps : ∀ a ∈ axes, (16*p*p)*(p*p) ≤ a.J) :
    ∃ S : Nat, 0 < S ∧ ∃ y : Fin n → Datum,
      InverseChain (16*p*p) S 1 axes (fun i => times S (x i)) y ∧
      Close S ((2*(16*p*p)+1)*axes.length) (sweep x axes) y ∧
      ∀ (T : Nat) (z : Fin n → Datum), InverseChain (16*p*p) T 1 axes (fun i => times T (x i)) z →
        ∀ i, times T (y i) = times S (z i) := by
  apply actualGaussianInverse axes (16*p*p) 1 (2^(p*p)) x _ bound
  intro a ha
  exact readyFromGrid _ _ (p*p) _ (Nat.mul_pos (Nat.mul_pos (by decide) hp) hp) (admitted _ ha) (gap _ ha) (Nat.le_refl _) (sweeps _ ha)

#print axioms poweredTail
#print axioms readyFromGrid
#print axioms fineGaussianInverse

end RationalInverse
