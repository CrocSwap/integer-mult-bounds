import Std

/-!
Complement-independent dirty-scratch safety for reversible Boolean encoders.
Every legal XOR instruction is an involution, so its reversed word supplies an
actual inverse. Mandatory fresh transfer is a separate component contract.
Physical frame containment, primitive/copy charges and asymptotic compilation
are not inferred from this arithmetic theorem. Matroid/basis completion and
reversible linear circuit principles are established ingredients.
-/
namespace DirtyComplementSafety

abbrev Vec (I : Type) := I → Bool

def vxor {I : Type} (x y : Vec I) : Vec I := fun i => x i ^^ y i

def Linear {I J : Type} (f : Vec I → Vec J) : Prop :=
  ∀ x y, f (vxor x y) = vxor (f x) (f y)

theorem vxor_cancel_right {I : Type} (x y : Vec I) : vxor (vxor x y) y = x := by
  funext i
  simp only [vxor]
  cases x i <;> cases y i <;> rfl

theorem vxor_cancel_middle {I : Type} (x y z : Vec I) :
    vxor (vxor x y) (vxor y z) = vxor x z := by
  funext i
  simp only [vxor]
  cases x i <;> cases y i <;> cases z i <;> rfl

def xorUpdate {I : Type} [DecidableEq I] (a b : I) (s : Vec I) : Vec I :=
  fun i => if i=a then s a ^^ s b else s i

theorem xorUpdate_involution {I : Type} [DecidableEq I] (a b : I)
    (hab : a ≠ b) (s : Vec I) : xorUpdate a b (xorUpdate a b s) = s := by
  funext i
  by_cases h : i=a
  · subst i
    have hb : b ≠ a := Ne.symm hab
    simp only [xorUpdate,ite_true,if_neg hb]
    cases s a <;> cases s b <;> rfl
  · simp only [xorUpdate,if_neg h]

theorem xorUpdate_linear {I : Type} [DecidableEq I] (a b : I) :
    Linear (xorUpdate a b) := by
  intro s t
  funext i
  by_cases h : i=a
  · subst i
    simp only [xorUpdate,ite_true,vxor]
    cases s a <;> cases s b <;> cases t a <;> cases t b <;> rfl
  · simp only [xorUpdate,if_neg h,vxor]

def runWord {I : Type} [DecidableEq I] : List (I × I) → Vec I → Vec I
  | [],s => s
  | e::es,s => runWord es (xorUpdate e.1 e.2 s)

def Legal {I : Type} (word : List (I × I)) : Prop := ∀ e ∈ word, e.1 ≠ e.2

theorem runWord_append {I : Type} [DecidableEq I]
    (xs ys : List (I × I)) (s : Vec I) :
    runWord (xs++ys) s = runWord ys (runWord xs s) := by
  induction xs generalizing s with
  | nil => rfl
  | cons e es ih => simp only [List.cons_append,runWord,ih]

theorem runWord_inverse {I : Type} [DecidableEq I]
    (word : List (I × I)) (h : Legal word) (s : Vec I) :
    runWord word.reverse (runWord word s) = s := by
  induction word generalizing s with
  | nil => rfl
  | cons e es ih =>
    have he := h e (by simp)
    have hrest : Legal es := by intro f hf; exact h f (by simp [hf])
    simp only [List.reverse_cons,runWord,runWord_append]
    rw [ih hrest]
    exact xorUpdate_involution e.1 e.2 he s

theorem runWord_linear {I : Type} [DecidableEq I] (word : List (I × I)) :
    Linear (runWord word) := by
  induction word with
  | nil => intro s t; rfl
  | cons e es ih =>
    intro s t
    simp only [runWord]
    rw [xorUpdate_linear e.1 e.2 s t,ih]

/-- This is the actual two-pass shear schedule M,J,M^-1,V repeated twice. -/
def dirtyWord {X S : Type}
    (M N : Vec S → Vec S) (V : Vec X → Vec S) (J : Vec S → Vec X)
    (x y : Vec X) (s : Vec S) : Vec X × Vec X × Vec S :=
  let t1 := M s
  let y1 := vxor y (J t1)
  let t2 := N t1
  let t3 := vxor t2 (V x)
  let t4 := M t3
  let y2 := vxor y1 (J t4)
  let t5 := N t4
  let t6 := vxor t5 (V x)
  (x,y2,t6)

/-- Arbitrary dirty scratch cancels. No desired transfer identity is assumed:
the theorem derives the output from the separate source/encoder/scatter maps. -/
theorem dirtyWord_transfer {X S : Type}
    (M N : Vec S → Vec S) (V : Vec X → Vec S) (J : Vec S → Vec X)
    (hM : Linear M) (hJ : Linear J) (hNM : ∀ s, N (M s) = s)
    (x y : Vec X) (s : Vec S) :
    dirtyWord M N V J x y s = (x,vxor y (J (M (V x))),s) := by
  simp only [dirtyWord,hNM]
  rw [hM,hJ,vxor_cancel_middle,vxor_cancel_right]

/-- A different unit complement changes the internal encoder and retired
signals, but not the observable shear or dirty restoration when mandatory
fresh transfers agree. -/
theorem complement_independent_transfer {X S T : Type}
    (M N : Vec S → Vec S) (V : Vec X → Vec S) (J : Vec S → Vec X)
    (M' N' : Vec T → Vec T) (V' : Vec X → Vec T) (J' : Vec T → Vec X)
    (hM : Linear M) (hJ : Linear J) (hNM : ∀ s, N (M s) = s)
    (hM' : Linear M') (hJ' : Linear J') (hNM' : ∀ s, N' (M' s) = s)
    (hfresh : ∀ x, J (M (V x)) = J' (M' (V' x)))
    (x y : Vec X) (s : Vec S) (t : Vec T) :
    (dirtyWord M N V J x y s).1 = (dirtyWord M' N' V' J' x y t).1 ∧
    (dirtyWord M N V J x y s).2.1 = (dirtyWord M' N' V' J' x y t).2.1 ∧
    (dirtyWord M N V J x y s).2.2 = s ∧
    (dirtyWord M' N' V' J' x y t).2.2 = t := by
  rw [dirtyWord_transfer M N V J hM hJ hNM,
      dirtyWord_transfer M' N' V' J' hM' hJ' hNM']
  simp [hfresh]

/-- The concrete legal XOR encoder needs no assumed invertibility premise:
its literal reversed word is the proved inverse, for all dirty vectors. -/
theorem legal_word_dirty_transfer {X S : Type} [DecidableEq S]
    (word : List (S × S)) (hlegal : Legal word)
    (V : Vec X → Vec S) (J : Vec S → Vec X) (hJ : Linear J)
    (x y : Vec X) (s : Vec S) :
    dirtyWord (runWord word) (runWord word.reverse) V J x y s =
      (x,vxor y (J (runWord word (V x))),s) :=
  dirtyWord_transfer _ _ _ _ (runWord_linear word) hJ (runWord_inverse word hlegal) x y s

/-- If the unchanged mandatory producer/scatter contract is the identity,
the compiled complement produces exactly the required shear. -/
theorem legal_word_shear {X S : Type} [DecidableEq S]
    (word : List (S × S)) (hlegal : Legal word)
    (V : Vec X → Vec S) (J : Vec S → Vec X) (hJ : Linear J)
    (htransfer : ∀ x, J (runWord word (V x)) = x)
    (x y : Vec X) (s : Vec S) :
    dirtyWord (runWord word) (runWord word.reverse) V J x y s = (x,vxor y x,s) := by
  rw [legal_word_dirty_transfer word hlegal V J hJ,htransfer]

end DirtyComplementSafety

#print axioms DirtyComplementSafety.runWord_inverse
#print axioms DirtyComplementSafety.dirtyWord_transfer
#print axioms DirtyComplementSafety.complement_independent_transfer
#print axioms DirtyComplementSafety.legal_word_shear
