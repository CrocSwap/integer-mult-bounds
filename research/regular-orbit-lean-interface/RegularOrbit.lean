import Std

/-! Finite Boolean coefficient extraction from a separating orbit.
    ywz65 with substantial OpenAI Codex assistance. Apache-2.0.
    The regular-orbit argument is credited to the cited written predecessors. -/
namespace RegularOrbit

def xorSum {A : Type} (xs : List A) (f : A → Bool) : Bool :=
  xs.foldr (fun a b => f a ^^ b) false

@[simp] theorem xorSum_nil {A : Type} (f : A → Bool) : xorSum [] f = false := rfl
@[simp] theorem xorSum_cons {A : Type} (a : A) (xs : List A) (f : A → Bool) :
    xorSum (a :: xs) f = (f a ^^ xorSum xs f) := rfl

theorem xorSum_congr {A : Type} (xs : List A) (f g : A → Bool)
    (h : ∀ a ∈ xs, f a = g a) : xorSum xs f = xorSum xs g := by
  induction xs with
  | nil => rfl
  | cons a xs ih =>
    simp only [xorSum_cons]
    rw [h a (by simp), ih (by intro b hb; exact h b (by simp [hb]))]

theorem xorSum_zero {A : Type} (xs : List A) (f : A → Bool)
    (h : ∀ a ∈ xs, f a = false) : xorSum xs f = false := by
  induction xs with
  | nil => rfl
  | cons a xs ih =>
    simp only [xorSum_cons]
    rw [h a (by simp), ih (by intro b hb; exact h b (by simp [hb]))]
    rfl

theorem xorSum_single {A : Type} [DecidableEq A] (xs : List A) (a : A)
    (b : Bool) (nd : xs.Nodup) (mem : a ∈ xs) :
    xorSum xs (fun x => if x = a then b else false) = b := by
  induction xs with
  | nil => simp at mem
  | cons x xs ih =>
    have hn := List.nodup_cons.mp nd
    by_cases eq : x = a
    · subst x
      have hz : xorSum xs (fun x => if x = a then b else false) = false := by
        apply xorSum_zero
        intro x hx
        have ne : x ≠ a := by intro he; subst x; exact hn.1 hx
        simp [ne]
      simp only [xorSum_cons, ite_true, hz, Bool.xor_false]
    · have hm : a ∈ xs := by
        rcases List.mem_cons.mp mem with he | hm
        · exact False.elim (eq he.symm)
        · exact hm
      simp only [xorSum_cons, ite_eq_right eq, Bool.false_xor]
      exact ih hn.2 hm

structure PermFamily (G X : Type) where
  forward : G → X → X
  inverse : G → X → X
  left_inverse : ∀ g x, inverse g (forward g x) = x
  right_inverse : ∀ g x, forward g (inverse g x) = x

def Separates {G X : Type} (p : PermFamily G X) (x : X) : Prop :=
  ∀ g h, p.forward g x = p.forward h x → g = h

theorem inverse_hit_iff {G X : Type} (p : PermFamily G X) (x : X)
    (sep : Separates p x) (g h : G) :
    p.inverse g (p.forward h x) = x ↔ g = h := by
  constructor
  · intro hit
    apply sep
    calc
      p.forward g x = p.forward g (p.inverse g (p.forward h x)) := congrArg (p.forward g) hit.symm
      _ = p.forward h x := p.right_inverse g (p.forward h x)
  · intro eq
    subst h
    exact p.left_inverse g x

def action {G X : Type} (gs : List G) (p : PermFamily G X)
    (coeff : G → Bool) (payload : X → Bool) (y : X) : Bool :=
  xorSum gs (fun g => coeff g && payload (p.inverse g y))

def delta {X : Type} [DecidableEq X] (x : X) (y : X) : Bool := decide (y = x)

theorem coefficient_extract {G X : Type} [DecidableEq G] [DecidableEq X]
    (gs : List G) (p : PermFamily G X) (x : X) (sep : Separates p x)
    (coeff : G → Bool) (h : G) (nd : gs.Nodup) (mem : h ∈ gs) :
    action gs p coeff (delta x) (p.forward h x) = coeff h := by
  unfold action
  calc
    xorSum gs (fun g => coeff g && delta x (p.inverse g (p.forward h x))) =
        xorSum gs (fun g => if g = h then coeff h else false) := by
      apply xorSum_congr
      intro g _
      by_cases eq : g = h
      · subst g
        simp [delta, p.left_inverse]
      · have ne : p.inverse g (p.forward h x) ≠ x := by
          intro hit
          exact eq ((inverse_hit_iff p x sep g h).mp hit)
        simp [delta, ne, eq]
    _ = coeff h := xorSum_single gs h (coeff h) nd mem

theorem action_faithful {G X : Type} [DecidableEq G] [DecidableEq X]
    (gs : List G) (p : PermFamily G X) (x : X) (sep : Separates p x)
    (nd : gs.Nodup) (complete : ∀ g, g ∈ gs) (a b : G → Bool)
    (same : ∀ payload y, action gs p a payload y = action gs p b payload y) :
    a = b := by
  funext h
  have eq := same (delta x) (p.forward h x)
  simpa only [coefficient_extract gs p x sep a h nd (complete h),
    coefficient_extract gs p x sep b h nd (complete h)] using eq

def matrixAction {R G X : Type} (rs : List R) (gs : List G) (p : PermFamily G X)
    (coeff : R → R → G → Bool) (payload : R → X → Bool) (i : R) (y : X) : Bool :=
  xorSum rs (fun j => action gs p (coeff i j) (payload j) y)

def roleDelta {R X : Type} [DecidableEq R] [DecidableEq X]
    (j : R) (x : X) (k : R) (y : X) : Bool := if k = j then delta x y else false

theorem action_zero {G X : Type} (gs : List G) (p : PermFamily G X)
    (coeff : G → Bool) (y : X) : action gs p coeff (fun _ => false) y = false := by
  apply xorSum_zero
  intro g _
  simp

theorem matrix_coefficient_extract {R G X : Type}
    [DecidableEq R] [DecidableEq G] [DecidableEq X]
    (rs : List R) (gs : List G) (p : PermFamily G X) (x : X) (sep : Separates p x)
    (coeff : R → R → G → Bool) (i j : R) (h : G)
    (rnd : rs.Nodup) (jmem : j ∈ rs) (gnd : gs.Nodup) (hmem : h ∈ gs) :
    matrixAction rs gs p coeff (roleDelta j x) i (p.forward h x) = coeff i j h := by
  unfold matrixAction
  calc
    xorSum rs (fun k => action gs p (coeff i k) (roleDelta j x k) (p.forward h x)) =
        xorSum rs (fun k => if k = j then coeff i j h else false) := by
      apply xorSum_congr
      intro k _
      by_cases eq : k = j
      · subst k
        have hd : roleDelta j x j = delta x := by funext y; simp [roleDelta]
        rw [hd]
        simp only [ite_true]
        exact coefficient_extract gs p x sep (coeff i j) h gnd hmem
      · have hd : roleDelta j x k = (fun _ => false) := by funext y; simp [roleDelta, eq]
        rw [hd, action_zero]
        simp [eq]
    _ = coeff i j h := xorSum_single rs j (coeff i j h) rnd jmem

theorem complete_endpoint_faithful {R G X : Type}
    [DecidableEq R] [DecidableEq G] [DecidableEq X]
    (rs : List R) (gs : List G) (p : PermFamily G X) (x : X) (sep : Separates p x)
    (rnd : rs.Nodup) (rcomplete : ∀ j, j ∈ rs)
    (gnd : gs.Nodup) (gcomplete : ∀ g, g ∈ gs)
    (a b : R → R → G → Bool)
    (same : ∀ payload i y, matrixAction rs gs p a payload i y = matrixAction rs gs p b payload i y) :
    a = b := by
  funext i j h
  have eq := same (roleDelta j x) i (p.forward h x)
  simpa only [matrix_coefficient_extract rs gs p x sep a i j h rnd (rcomplete j) gnd (gcomplete h),
    matrix_coefficient_extract rs gs p x sep b i j h rnd (rcomplete j) gnd (gcomplete h)] using eq

#print axioms coefficient_extract
#print axioms action_faithful
#print axioms matrix_coefficient_extract
#print axioms complete_endpoint_faithful

abbrev Vec3 := Fin 3 → Bool
abbrev Mat3 := Fin 3 → Fin 3 → Bool
abbrev Tuple3 := Fin 3 → Vec3

def mv3 (a : Mat3) (v : Vec3) (i : Fin 3) : Bool :=
  (a i 0 && v 0) ^^ ((a i 1 && v 1) ^^ (a i 2 && v 2))

def basis3 (j i : Fin 3) : Bool := decide (i = j)

theorem mv3_basis (a : Mat3) (i j : Fin 3) : mv3 a (basis3 j) i = a i j := by
  match j with
  | ⟨0, _⟩ => simp [mv3, basis3]
  | ⟨1, _⟩ => simp [mv3, basis3]
  | ⟨2, _⟩ => simp [mv3, basis3]
  | ⟨n+3, h⟩ => omega

def tupleAction3 (a : Mat3) (x : Tuple3) (j : Fin 3) : Vec3 := mv3 a (x j)

theorem basis_tuple_separates_matrices (a b : Mat3)
    (same : tupleAction3 a basis3 = tupleAction3 b basis3) : a = b := by
  funext i j
  have entry := congrArg (fun t : Tuple3 => t j i) same
  simpa only [tupleAction3, mv3_basis] using entry

def Invertible3 (a : Mat3) : Prop :=
  ∃ b : Mat3, (∀ v, mv3 b (mv3 a v) = v) ∧ (∀ v, mv3 a (mv3 b v) = v)

abbrev GL3 := {a : Mat3 // Invertible3 a}

def identity3 (i j : Fin 3) : Bool := decide (i = j)

theorem mv3_identity (v : Vec3) : mv3 identity3 v = v := by
  funext i
  match i with
  | ⟨0, _⟩ => simp [mv3, identity3]
  | ⟨1, _⟩ => simp [mv3, identity3]
  | ⟨2, _⟩ => simp [mv3, identity3]
  | ⟨n+3, h⟩ => omega

def identityGL3 : GL3 := ⟨identity3, identity3, by
  constructor <;> intro v <;> simp [mv3_identity]⟩

noncomputable def gl3Perm : PermFamily GL3 Tuple3 := by
  classical
  exact {
    forward := fun g => tupleAction3 g.val
    inverse := fun g => tupleAction3 (Classical.choose g.property)
    left_inverse := by
      intro g x
      funext j
      exact (Classical.choose_spec g.property).1 (x j)
    right_inverse := by
      intro g x
      funext j
      exact (Classical.choose_spec g.property).2 (x j)
  }

theorem gl3_basis_separates : Separates gl3Perm basis3 := by
  intro g h same
  apply Subtype.ext
  exact basis_tuple_separates_matrices g.val h.val same

theorem gl3_identity_basis : gl3Perm.forward identityGL3 basis3 = basis3 := by
  funext j
  exact mv3_identity (basis3 j)

theorem gl3_complete_endpoint_faithful {R : Type} [DecidableEq R]
    (rs : List R) (gs : List GL3)
    (rnd : rs.Nodup) (rcomplete : ∀ j, j ∈ rs)
    (gnd : gs.Nodup) (gcomplete : ∀ g, g ∈ gs)
    (a b : R → R → GL3 → Bool)
    (same : ∀ payload i y,
      matrixAction rs gs gl3Perm a payload i y = matrixAction rs gs gl3Perm b payload i y) :
    a = b := by
  classical
  exact complete_endpoint_faithful rs gs gl3Perm basis3 gl3_basis_separates
    rnd rcomplete gnd gcomplete a b same

#print axioms mv3_basis
#print axioms basis_tuple_separates_matrices
#print axioms mv3_identity
#print axioms gl3_identity_basis
#print axioms gl3_basis_separates
#print axioms gl3_complete_endpoint_faithful

end RegularOrbit
