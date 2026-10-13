import DyadicCertificates
import GaussianLattice
import GaussianScalarCircuits

/-!
Finite recursive execution of the exact Gaussian C tensor.
This proves arithmetic composition, not physical tape layout or runtime.
-/

namespace GaussianTensorExecution
open GaussianParity GaussianSynthesis

/-- A uniform complete binary coefficient cube. -/
def Cube : Nat → Type
  | 0 => GInt
  | n+1 => Cube n × Cube n

def cubeMap (f : GInt → GInt) : (n : Nat) → Cube n → Cube n
  | 0, z => f z
  | n+1, z => (cubeMap f n z.1,cubeMap f n z.2)

def cubeZip (f : GInt → GInt → GInt) : (n : Nat) → Cube n → Cube n → Cube n
  | 0, u, v => f u v
  | n+1, u, v => (cubeZip f n u.1 v.1,cubeZip f n u.2 v.2)

def cubeAdd (n : Nat) : Cube n → Cube n → Cube n := cubeZip add n
def cubeI (n : Nat) : Cube n → Cube n := cubeMap mulI n
def cubePi (n : Nat) : Cube n → Cube n := cubeMap mulPi n
def cubePiIter (k n : Nat) : Cube n → Cube n := cubeMap (piIter k) n

/-- Pointwise raw C numerators for one complete coordinate axis. -/
def axisForward (n : Nat) (z : Cube n × Cube n) : Cube n × Cube n :=
  (cubeAdd n (cubeI n z.1) z.2,cubeAdd n z.1 (cubeI n z.2))

/-- Pointwise inverse-axis numerators: X C. -/
def axisInverse (n : Nat) (z : Cube n × Cube n) : Cube n × Cube n :=
  (cubeAdd n z.1 (cubeI n z.2),cubeAdd n (cubeI n z.1) z.2)

/-- Children are transformed first, then the new coordinate axis. Every
level contributes one pi denominator unit. -/
def forward : (n : Nat) → Cube n → Cube n
  | 0, z => z
  | n+1, z => axisForward n (forward n z.1,forward n z.2)

/-- Reverse the new axis first, then recursively reverse both children. -/
def inverse : (n : Nat) → Cube n → Cube n
  | 0, z => z
  | n+1, z =>
    let q := axisInverse n z
    (inverse n q.1,inverse n q.2)

/-- Lifting a pointwise scalar identity to every cube coordinate. -/
theorem cubeMap_congr (n : Nat) (f g : GInt → GInt) (h : ∀ z, f z = g z)
    (z : Cube n) : cubeMap f n z = cubeMap g n z := by
  induction n with
  | zero => exact h z
  | succ n ih =>
    apply Prod.ext
    · exact ih z.1
    · exact ih z.2

theorem cubeMap_comp (n : Nat) (f g : GInt → GInt) (z : Cube n) :
    cubeMap f n (cubeMap g n z) = cubeMap (fun u => f (g u)) n z := by
  induction n with
  | zero => rfl
  | succ n ih =>
    apply Prod.ext
    · exact ih z.1
    · exact ih z.2

theorem cubeMap_zip (n : Nat) (f : GInt → GInt)
    (g : GInt → GInt → GInt) (h : ∀ u v, f (g u v) = g (f u) (f v))
    (u v : Cube n) :
    cubeMap f n (cubeZip g n u v) =
      cubeZip g n (cubeMap f n u) (cubeMap f n v) := by
  induction n with
  | zero => exact h u v
  | succ n ih =>
    apply Prod.ext
    · exact ih u.1 v.1
    · exact ih u.2 v.2

theorem mulPi_add (u v : GInt) : mulPi (add u v) = add (mulPi u) (mulPi v) := by
  apply GInt.ext <;> simp only [mulPi,add] <;> omega

theorem mulPi_mulI (z : GInt) : mulPi (mulI z) = mulI (mulPi z) := by
  apply GInt.ext <;> simp only [mulPi,mulI] <;> omega

theorem cubePi_add (n : Nat) (u v : Cube n) :
    cubePi n (cubeAdd n u v) = cubeAdd n (cubePi n u) (cubePi n v) := by
  exact cubeMap_zip n mulPi add mulPi_add u v

theorem cubePi_I (n : Nat) (z : Cube n) : cubePi n (cubeI n z) = cubeI n (cubePi n z) := by
  unfold cubePi cubeI
  rw [cubeMap_comp,cubeMap_comp]
  exact cubeMap_congr n _ _ mulPi_mulI z

theorem axisForward_pi (n : Nat) (z : Cube n × Cube n) :
    axisForward n (cubePi n z.1,cubePi n z.2) =
      (cubePi n (axisForward n z).1,cubePi n (axisForward n z).2) := by
  apply Prod.ext <;> simp only [axisForward,cubePi_add,cubePi_I]

theorem axisInverse_pi (n : Nat) (z : Cube n × Cube n) :
    axisInverse n (cubePi n z.1,cubePi n z.2) =
      (cubePi n (axisInverse n z).1,cubePi n (axisInverse n z).2) := by
  apply Prod.ext <;> simp only [axisInverse,cubePi_add,cubePi_I]

theorem inverse_pi (n : Nat) (z : Cube n) :
    inverse n (cubePi n z) = cubePi n (inverse n z) := by
  induction n with
  | zero => rfl
  | succ n ih =>
    change
      (inverse n (axisInverse n (cubePi n z.1,cubePi n z.2)).1,
       inverse n (axisInverse n (cubePi n z.1,cubePi n z.2)).2) =
      (cubePi n (inverse n (axisInverse n z).1),
       cubePi n (inverse n (axisInverse n z).2))
    rw [axisInverse_pi]
    apply Prod.ext
    · exact ih _
    · exact ih _

theorem cubePiIter_succ (k n : Nat) (z : Cube n) :
    cubePiIter (k+1) n z = cubePi n (cubePiIter k n z) := by
  unfold cubePiIter cubePi
  rw [cubeMap_comp]
  rfl

theorem cubePiIter_add (k l n : Nat) (z : Cube n) :
    cubePiIter (k+l) n z = cubePiIter k n (cubePiIter l n z) := by
  unfold cubePiIter
  rw [cubeMap_comp]
  exact cubeMap_congr n _ _ (piIter_add k l) z

end GaussianTensorExecution

namespace GaussianTensorExecution
open GaussianParity GaussianSynthesis

def Path : Nat → Type
  | 0 => Unit
  | n+1 => Bool × Path n

def get : (n : Nat) → Cube n → Path n → GInt
  | 0, z, _ => z
  | n+1, z, p => if p.1 then get n z.2 p.2 else get n z.1 p.2

theorem cube_ext (n : Nat) {u v : Cube n}
    (h : ∀ p : Path n, get n u p = get n v p) : u = v := by
  induction n with
  | zero => exact h ()
  | succ n ih =>
    apply Prod.ext
    · apply ih
      intro p
      exact h (false,p)
    · apply ih
      intro p
      exact h (true,p)

theorem get_map (n : Nat) (f : GInt → GInt) (z : Cube n) (p : Path n) :
    get n (cubeMap f n z) p = f (get n z p) := by
  induction n with
  | zero => rfl
  | succ n ih =>
    rcases p with ⟨b,p⟩
    cases b <;> simp only [get,cubeMap,Bool.false_eq_true,↓reduceIte]
    · exact ih _ p
    · exact ih _ p

theorem get_zip (n : Nat) (f : GInt → GInt → GInt)
    (u v : Cube n) (p : Path n) :
    get n (cubeZip f n u v) p = f (get n u p) (get n v p) := by
  induction n with
  | zero => rfl
  | succ n ih =>
    rcases p with ⟨b,p⟩
    cases b <;> simp only [get,cubeZip,Bool.false_eq_true,↓reduceIte]
    · exact ih _ _ p
    · exact ih _ _ p

theorem cubeMap_id (n : Nat) (z : Cube n) : cubeMap (fun u => u) n z = z := by
  apply cube_ext n
  intro p
  rw [get_map]

theorem inverse_piIter (k n : Nat) (z : Cube n) :
    inverse n (cubePiIter k n z) = cubePiIter k n (inverse n z) := by
  induction k with
  | zero => simp [cubePiIter,piIter,cubeMap_id]
  | succ k ih => rw [cubePiIter_succ,inverse_pi,ih,← cubePiIter_succ]

/-- One raw forward axis followed by its raw inverse multiplies every
numerator by pi squared. This is unconditional scalar arithmetic. -/
theorem axis_inverse_forward (n : Nat) (z : Cube n × Cube n) :
    axisInverse n (axisForward n z) =
      (cubePiIter 2 n z.1,cubePiIter 2 n z.2) := by
  apply Prod.ext <;> apply cube_ext n <;> intro p
  · simp only [axisInverse,axisForward,cubeAdd,cubeI,cubePiIter,get_map,get_zip]
    apply GInt.ext <;> simp only [add,mulI,piIter,mulPi] <;> omega
  · simp only [axisInverse,axisForward,cubeAdd,cubeI,cubePiIter,get_map,get_zip]
    apply GInt.ext <;> simp only [add,mulI,piIter,mulPi] <;> omega

/-- Full finite C tensor restoration, proved for every dimension and every
coefficient cube. No parity promises are imposed on any input or scratch. -/
theorem inverse_forward (n : Nat) (z : Cube n) :
    inverse n (forward n z) = cubePiIter (2*n) n z := by
  induction n with
  | zero => simp [inverse,forward,cubePiIter,piIter,cubeMap_id]
  | succ n ih =>
    change
      (inverse n (axisInverse n (axisForward n (forward n z.1,forward n z.2))).1,
       inverse n (axisInverse n (axisForward n (forward n z.1,forward n z.2))).2) =
      (cubePiIter (2*(n+1)) n z.1,cubePiIter (2*(n+1)) n z.2)
    rw [axis_inverse_forward]
    apply Prod.ext
    · change inverse n (cubePiIter 2 n (forward n z.1)) = cubePiIter (2*(n+1)) n z.1
      rw [inverse_piIter,ih,← cubePiIter_add]
      have h : 2+2*n = 2*(n+1) := by omega
      rw [h]
    · change inverse n (cubePiIter 2 n (forward n z.2)) = cubePiIter (2*(n+1)) n z.2
      rw [inverse_piIter,ih,← cubePiIter_add]
      have h : 2+2*n = 2*(n+1) := by omega
      rw [h]

end GaussianTensorExecution

#print axioms GaussianTensorExecution.axis_inverse_forward
#print axioms GaussianTensorExecution.inverse_forward

namespace GaussianTensorExecution
open GaussianParity GaussianSynthesis

theorem shifted_tag_sameValue (k e : Nat) (z : GInt) :
    SameValue ⟨piIter k z,e+k⟩ ⟨z,e⟩ := by
  simp only [SameValue]
  rw [← piIter_add]

/-- Every returned coordinate restores its exact input value when the two
raw tensor calls charge their actual 2D denominator units. -/
theorem inverse_forward_leaf_sameValue (n e : Nat) (z : Cube n) (p : Path n) :
    SameValue ⟨get n (inverse n (forward n z)) p,e+2*n⟩ ⟨get n z p,e⟩ := by
  rw [inverse_forward]
  simp only [cubePiIter,get_map]
  exact shifted_tag_sameValue (2*n) e _

/-- Canonicalization restores each literal exact representation too. -/
theorem inverse_forward_leaf_canonical (n e : Nat) (z : Cube n) (p : Path n) :
    normalize ⟨get n (inverse n (forward n z)) p,e+2*n⟩ = normalize ⟨get n z p,e⟩ :=
  normalize_congr (inverse_forward_leaf_sameValue n e z p)

theorem repeatPi_eq_piIter (k : Nat) (z : GInt) : repeatPi k z = piIter k z := by
  induction k with
  | zero => rfl
  | succ k ih => simp only [repeatPi,piIter,ih]

/-- A terminal forward-coordinate numerator has the proved binary grid
conversion, now connected directly to the actual recursive execution. -/
theorem forward_leaf_binary_grid (n e : Nat) (z : Cube n) (p : Path n) :
    ∃ w : GInt, piIter (e+n) w = scale ((2 : Int)^((e+n+1)/2)) (get n (forward n z) p) := by
  rcases binary_grid_conversion (e+n) (get n (forward n z) p) with ⟨w,hw⟩
  exact ⟨w,by simpa only [repeatPi_eq_piIter] using hw⟩

def zeroCube : (n : Nat) → Cube n
  | 0 => ⟨0,0⟩
  | n+1 => (zeroCube n,zeroCube n)

theorem cubeI_zero (n : Nat) : cubeI n (zeroCube n) = zeroCube n := by
  induction n with
  | zero => rfl
  | succ n ih =>
    change (cubeI n (zeroCube n),cubeI n (zeroCube n)) = (zeroCube n,zeroCube n)
    rw [ih]

theorem cubeAdd_zero_left (n : Nat) (z : Cube n) : cubeAdd n (zeroCube n) z = z := by
  induction n with
  | zero => apply GInt.ext <;> simp [cubeAdd,cubeZip,zeroCube,add]
  | succ n ih =>
    change (cubeAdd n (zeroCube n) z.1,cubeAdd n (zeroCube n) z.2) = z
    rw [ih,ih]
    cases z
    rfl

theorem forward_zero (n : Nat) : forward n (zeroCube n) = zeroCube n := by
  induction n with
  | zero => rfl
  | succ n ih =>
    simp only [forward,zeroCube]
    rw [ih]
    simp only [axisForward]
    rw [cubeI_zero,cubeAdd_zero_left]

def firstPath : (n : Nat) → Path n
  | 0 => ()
  | n+1 => (false,firstPath n)

/-- Input impulse at the all-one coordinate. -/
def lastImpulse : (n : Nat) → Cube n
  | 0 => ⟨1,0⟩
  | n+1 => (zeroCube n,lastImpulse n)

/-- The actual recursively evaluated all-zero output has numerator 1 for
the all-one input impulse, giving the entry 1/pi^D without a matrix axiom. -/
theorem forward_impulse_first (n : Nat) :
    get n (forward n (lastImpulse n)) (firstPath n) = ⟨1,0⟩ := by
  induction n with
  | zero => rfl
  | succ n ih =>
    simp only [forward,lastImpulse,firstPath,get,Bool.false_eq_true,↓reduceIte]
    simp only [axisForward]
    rw [forward_zero,cubeI_zero,cubeAdd_zero_left]
    exact ih

/-- The tensor's actual impulse coordinate cannot fit a one-bit coarser
binary grid at positive even dimension. -/
theorem forward_even_grid_sharp (q : Nat) :
    ¬ ∃ w : GInt, piIter (2*(q+1)) w =
      scale ((2 : Int)^q)
        (get (2*(q+1)) (forward (2*(q+1)) (lastImpulse (2*(q+1)))) (firstPath (2*(q+1)))) := by
  rw [forward_impulse_first]
  simpa only [repeatPi_eq_piIter] using even_grid_sharp q

/-- Sharpness at every odd dimension, linked to the actual executed impulse. -/
theorem forward_odd_grid_sharp (q : Nat) :
    ¬ ∃ w : GInt, piIter (2*q+1) w =
      scale ((2 : Int)^q)
        (get (2*q+1) (forward (2*q+1) (lastImpulse (2*q+1))) (firstPath (2*q+1))) := by
  rw [forward_impulse_first]
  simpa only [repeatPi_eq_piIter] using odd_grid_sharp q

end GaussianTensorExecution

#print axioms GaussianTensorExecution.inverse_forward_leaf_sameValue
#print axioms GaussianTensorExecution.inverse_forward_leaf_canonical
#print axioms GaussianTensorExecution.forward_leaf_binary_grid
#print axioms GaussianTensorExecution.forward_impulse_first
#print axioms GaussianTensorExecution.forward_even_grid_sharp
#print axioms GaussianTensorExecution.forward_odd_grid_sharp

namespace GaussianTensorExecution
open GaussianParity GaussianSynthesis

/-- A complete cube with one common exact pi-denominator tag. -/
structure TaggedCube (n : Nat) where
  numerators : Cube n
  exponent : Nat

def executeForward (n : Nat) (x : TaggedCube n) : TaggedCube n :=
  ⟨forward n x.numerators,x.exponent+n⟩

def executeInverse (n : Nat) (x : TaggedCube n) : TaggedCube n :=
  ⟨inverse n x.numerators,x.exponent+n⟩

def coordinate (n : Nat) (x : TaggedCube n) (p : Path n) : Fraction :=
  ⟨get n x.numerators p,x.exponent⟩

/-- The explicit tagged execution interface restores arbitrary original
coordinates exactly after a complete forward/inverse pair. -/
theorem execute_inverse_forward_exact (n : Nat) (x : TaggedCube n) (p : Path n) :
    SameValue (coordinate n (executeInverse n (executeForward n x)) p)
      (coordinate n x p) := by
  unfold coordinate executeInverse executeForward
  simp only
  have he : x.exponent+n+n = x.exponent+2*n := by omega
  rw [he]
  exact inverse_forward_leaf_sameValue n x.exponent x.numerators p

theorem execute_inverse_forward_canonical (n : Nat) (x : TaggedCube n) (p : Path n) :
    normalize (coordinate n (executeInverse n (executeForward n x)) p) =
      normalize (coordinate n x p) :=
  normalize_congr (execute_inverse_forward_exact n x p)

/-- The registered forward execution charges exactly one pi unit per axis. -/
theorem execute_forward_tag (n : Nat) (x : TaggedCube n) :
    (executeForward n x).exponent = x.exponent+n := rfl

/-- For incoming binary-grid precision p, the terminal recursive C tensor
needs p+ceil(D/2) binary fractional bits. The Pi tag 2p represents the same
binary grid, up to a unit phase. -/
theorem forward_binary_input_grid (n p : Nat) (z : Cube n) (path : Path n) :
    ∃ w : GInt, piIter (2*p+n) w =
      scale ((2 : Int)^(p+(n+1)/2)) (get n (forward n z) path) := by
  have h := forward_leaf_binary_grid n (2*p) z path
  have he : (2*p+n+1)/2 = p+(n+1)/2 := by omega
  simpa only [he] using h

/-- At odd tensor depth the converted binary numerator carries the exact
index-two Gaussian parity constraint, linked to the executed forward cube. -/
theorem forward_odd_binary_sublattice (p q : Nat) (z : Cube (2*q+1))
    (path : Path (2*q+1)) :
    ∃ w : GInt, piIter (2*p+(2*q+1)) w =
      scale ((2 : Int)^(p+q+1)) (get (2*q+1) (forward (2*q+1) z) path) ∧ PiDvd w := by
  let a := get (2*q+1) (forward (2*q+1) z) path
  refine ⟨repeatNegI (p+q+1) (mulPi a),?_,odd_binary_numerator_parity (p+q) a⟩
  have hc := odd_binary_conversion (p+q) a
  have he : 2*p+(2*q+1) = 2*(p+q)+1 := by omega
  rw [he]
  simpa only [repeatPi_eq_piIter] using hc

end GaussianTensorExecution

#print axioms GaussianTensorExecution.execute_inverse_forward_exact
#print axioms GaussianTensorExecution.execute_inverse_forward_canonical
#print axioms GaussianTensorExecution.forward_binary_input_grid
#print axioms GaussianTensorExecution.forward_odd_binary_sublattice
