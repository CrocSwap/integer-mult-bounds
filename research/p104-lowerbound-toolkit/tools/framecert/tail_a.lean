
/-! ## bitmask machinery -/
def frameAt (i : Nat) : Nat := (framesP >>> (104 * i)) % 2 ^ 104
def labelAt (t : Nat) : Nat := (labelsP >>> (9 * t)) % 2 ^ 9
/-- the 759 frames -/
def frames : List Nat := (List.range 759).map frameAt

def combo : List Nat → Nat → Nat
  | [], _ => 0
  | f :: fs, c => (if c % 2 = 1 then f else 0) ^^^ combo fs (c / 2)

/-- accessors for a certificate [u1,u2,p0, entries...]; entry = p + 128*(cnt + 32*packed frame indices) -/
def unpack (x n k : Nat) : List Nat := (List.range n).map (fun j => (x >>> (k * j)) % 2 ^ k)
def cu1 (c : List Nat) : Nat := c.getD 0 0
def cu2 (c : List Nat) : Nat := c.getD 1 0
def cp0 (c : List Nat) : Nat := c.getD 2 0
def decEnt (v : Nat) : Nat × List Nat := (v % 128, unpack (v / 128 / 32) (v / 128 % 32) 10)
def cents (c : List Nat) : List (Nat × List Nat) := (c.drop 3).map decEnt

def xorAll : List Nat → Nat
  | [] => 0
  | f :: fs => f ^^^ xorAll fs

def colMask (j : Nat) : Nat :=
  (List.range 104).foldl (fun a t => if (labelAt t).testBit j then a ||| 2 ^ t else a) 0

/-- ports whose label has odd inner product with u -/
def parMask (u : Nat) : Nat :=
  (List.range 9).foldl (fun a j => if u.testBit j then a ^^^ colMask j else a) 0

/-- Lam = ports whose label is orthogonal to both normals u1,u2 (a 7-dim section of the label set) -/
def lamMask (u1 u2 : Nat) : Nat := (2 ^ 104 - 1) ^^^ (parMask u1 ||| parMask u2)

def covMask (ents : List (Nat × List Nat)) (p0 : Nat) : Nat := ents.foldl (fun a e => a ||| 2 ^ e.1) (2 ^ p0)

def entryOK (lam p0 : Nat) (e : Nat × List Nat) : Bool :=
  decide (e.1 < 104) && (e.1 != p0) && e.2.all (fun i => decide (i < 759)) &&
  ((xorAll (e.2.map frameAt) &&& lam) == (2 ^ e.1 ||| 2 ^ p0))

def certOK (c : List Nat) : Bool :=
  let lam := lamMask (cu1 c) (cu2 c)
  let p0 := cp0 c
  decide (p0 < 104) && lam.testBit p0 &&
  (cents c).all (entryOK lam p0) &&
  (lam == covMask (cents c) p0)

theorem all_app {a b : List (List Nat)} (ha : a.all certOK = true) (hb : b.all certOK = true) :
    (a ++ b).all certOK = true := by
  rw [List.all_append, ha, hb]; rfl

/-! ## semantics -/
lemma foldl_or_bit (l : List (Nat × List Nat)) (acc i : Nat)
    (h : (l.foldl (fun a e => a ||| 2 ^ e.1) acc).testBit i = true) :
    acc.testBit i = true ∨ ∃ e ∈ l, e.1 = i := by
  induction l generalizing acc with
  | nil => exact Or.inl h
  | cons e es ih =>
    rcases ih _ h with h1 | ⟨e', he', hi⟩
    · rw [Nat.testBit_or, Nat.testBit_two_pow, Bool.or_eq_true, decide_eq_true_eq] at h1
      rcases h1 with h2 | h2
      · exact Or.inl h2
      · exact Or.inr ⟨e, List.mem_cons_self, h2⟩
    · exact Or.inr ⟨e', List.mem_cons_of_mem _ he', hi⟩

variable {P : Type*} [DecidableEq P]

def ind (S : Finset P) : P → ZMod 2 := fun p => if p ∈ S then 1 else 0

lemma ind_inj {S T : Finset P} (h : ind S = ind T) : S = T := by
  ext p
  have := congrFun h p
  by_cases hs : p ∈ S <;> by_cases ht : p ∈ T <;> simp_all [ind]

theorem all_or_nothing (Fp : Set (P → ZMod 2)) (Lam A B : Finset P)
    (H_frame : ∀ x ∈ Fp, (∀ p, x p ≠ 0 → p ∈ Lam) → x = 0 ∨ x = ind Lam)
    (H_FS4 : ind (A ∩ B) ∈ Fp)
    (H_supp : A ⊆ Lam) :
    A ∩ B = ∅ ∨ (A = Lam ∧ Lam ⊆ B) := by
  have hsup : ∀ p, ind (A ∩ B) p ≠ 0 → p ∈ Lam := by
    intro p hp
    by_contra hn
    apply hp
    have : p ∉ A ∩ B := fun h => hn (H_supp (Finset.mem_inter.1 h).1)
    simp [ind, this]
  rcases H_frame _ H_FS4 hsup with h0 | h1
  · left
    ext p
    have := congrFun h0 p
    by_cases hp : p ∈ A ∩ B <;> simp_all [ind]
  · right
    have e : A ∩ B = Lam := ind_inj h1
    have hAL : Lam ⊆ A := by rw [← e]; exact Finset.inter_subset_left
    have hBL : Lam ⊆ B := by rw [← e]; exact Finset.inter_subset_right
    exact ⟨Finset.Subset.antisymm H_supp hAL, hBL⟩

/-- the dot product of a bitmask with a vector over the 104 ports -/
def dot (m : Nat) (x : Fin 104 → ZMod 2) : ZMod 2 :=
  ∑ i : Fin 104, if m.testBit i.val then x i else 0

/-- F^perp: vectors even on every frame -/
def Fperp : Set (Fin 104 → ZMod 2) := {x | ∀ m ∈ frames, dot m x = 0}

lemma zmod2_cancel (a : ZMod 2) : a + a = 0 := by revert a; decide

lemma dot_xor (a b : Nat) (x : Fin 104 → ZMod 2) : dot (a ^^^ b) x = dot a x + dot b x := by
  unfold dot
  rw [← Finset.sum_add_distrib]
  refine Finset.sum_congr rfl (fun i _ => ?_)
  rw [Nat.testBit_xor]
  cases a.testBit i.val <;> cases b.testBit i.val <;> simp [zmod2_cancel]

lemma dot_zero (x : Fin 104 → ZMod 2) : dot 0 x = 0 := by simp [dot]

lemma dot_and (m lam : Nat) (x : Fin 104 → ZMod 2) (hs : ∀ i : Fin 104, x i ≠ 0 → lam.testBit i.val = true) :
    dot (m &&& lam) x = dot m x := by
  unfold dot
  refine Finset.sum_congr rfl (fun i _ => ?_)
  rw [Nat.testBit_and]
  by_cases hx : x i = 0
  · simp [hx]
  · simp [hs i hx]

lemma dot_pair (p q : Nat) (hp : p < 104) (hq : q < 104) (hpq : p ≠ q) (x : Fin 104 → ZMod 2) :
    dot (2 ^ p ||| 2 ^ q) x = x ⟨p, hp⟩ + x ⟨q, hq⟩ := by
  unfold dot
  have : ∀ i : Fin 104, (if (2 ^ p ||| 2 ^ q).testBit i.val then x i else 0) =
      (if i = ⟨p, hp⟩ then x i else 0) + (if i = ⟨q, hq⟩ then x i else 0) := by
    intro i
    rw [Nat.testBit_or, Nat.testBit_two_pow, Nat.testBit_two_pow]
    have hi1 : (p = i.val) ↔ i = ⟨p, hp⟩ := by
      constructor
      · intro h; exact Fin.ext h.symm
      · intro h; rw [h]
    have hi2 : (q = i.val) ↔ i = ⟨q, hq⟩ := by
      constructor
      · intro h; exact Fin.ext h.symm
      · intro h; rw [h]
    have hb : ((decide (p = i.val) || decide (q = i.val)) = true) ↔ (i = ⟨p, hp⟩ ∨ i = ⟨q, hq⟩) := by
      rw [Bool.or_eq_true, decide_eq_true_eq, decide_eq_true_eq, hi1, hi2]
    by_cases h1 : i = ⟨p, hp⟩
    · have h2 : ¬ i = ⟨q, hq⟩ := by
        intro h; apply hpq; have := congrArg Fin.val (h1.symm.trans h); simpa using this
      rw [if_pos (hb.2 (Or.inl h1)), if_pos h1, if_neg h2, add_zero]
    · by_cases h2 : i = ⟨q, hq⟩
      · rw [if_pos (hb.2 (Or.inr h2)), if_neg h1, if_pos h2, zero_add]
      · rw [if_neg (fun h => (hb.1 h).elim h1 h2), if_neg h1, if_neg h2, add_zero]
  simp only [this, Finset.sum_add_distrib, Finset.sum_ite_eq', Finset.mem_univ, if_true]

lemma dot_xorAll (ms : List Nat) (x : Fin 104 → ZMod 2)
    (h : ∀ m ∈ ms, dot m x = 0) : dot (xorAll ms) x = 0 := by
  induction ms with
  | nil => simp [xorAll, dot_zero]
  | cons f fs ih =>
    simp only [xorAll, dot_xor]
    rw [ih (fun m hm => h m (List.mem_cons_of_mem _ hm)), h f List.mem_cons_self]; simp

lemma entry_sound (lam p0 : Nat) (e : Nat × List Nat) (x : Fin 104 → ZMod 2)
    (hF : ∀ i, i < 759 → dot (frameAt i) x = 0)
    (hs : ∀ i : Fin 104, x i ≠ 0 → lam.testBit i.val = true) (hp0 : p0 < 104)
    (h : entryOK lam p0 e = true) :
    ∃ hp : e.1 < 104, x ⟨e.1, hp⟩ = x ⟨p0, hp0⟩ := by
  simp only [entryOK, Bool.and_eq_true, decide_eq_true_eq, bne_iff_ne, ne_eq, beq_iff_eq] at h
  obtain ⟨⟨⟨hlt, hne⟩, hidx⟩, heq⟩ := h
  refine ⟨hlt, ?_⟩
  have h1 : dot (xorAll (e.2.map frameAt)) x = 0 := by
    apply dot_xorAll
    intro m hm
    obtain ⟨i, hi, rfl⟩ := List.mem_map.1 hm
    have := List.all_eq_true.1 hidx i hi
    simp only [decide_eq_true_eq] at this
    exact hF i this
  rw [← dot_and _ lam x hs, heq, dot_pair _ _ hlt hp0 hne] at h1
  have key : ∀ a b : ZMod 2, a + b = 0 → a = b := by decide
  exact key _ _ h1

/-- the Lam as a Finset of ports -/
def lamSet (lam : Nat) : Finset (Fin 104) := Finset.univ.filter (fun i => lam.testBit i.val)

def HFrame (Lam : Finset (Fin 104)) : Prop :=
  ∀ x ∈ Fperp, (∀ p, x p ≠ 0 → p ∈ Lam) → x = 0 ∨ x = ind Lam

theorem cert_sound (c : List Nat)
    (h : certOK c = true) : HFrame (lamSet (lamMask (cu1 c) (cu2 c))) := by
  intro x hx hsupp
  set lam := lamMask (cu1 c) (cu2 c) with hlam
  set p0 := cp0 c with hp0def
  simp only [certOK, Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq] at h
  obtain ⟨⟨⟨hp0, hbit⟩, hall⟩, hcov⟩ := h
  have hs : ∀ i : Fin 104, x i ≠ 0 → lam.testBit i.val = true := by
    intro i hi
    have := hsupp i hi
    simpa [lamSet] using this
  have hF : ∀ i, i < 759 → dot (frameAt i) x = 0 := fun i hi =>
    hx _ (List.mem_map.2 ⟨i, List.mem_range.2 hi, rfl⟩)
  have hconst : ∀ i : Fin 104, lam.testBit i.val = true → x i = x ⟨p0, hp0⟩ := by
    intro i hi
    have hb : (covMask (cents c) p0).testBit i.val = true := by rw [← hcov]; exact hi
    rcases foldl_or_bit _ _ _ hb with h1 | ⟨e, he, hei⟩
    · rw [Nat.testBit_two_pow, decide_eq_true_eq] at h1
      exact congrArg x (Fin.ext h1.symm)
    · obtain ⟨hlt, hxe⟩ := entry_sound lam p0 e x hF hs hp0 (List.all_eq_true.1 hall e he)
      have : (⟨e.1, hlt⟩ : Fin 104) = i := Fin.ext hei
      rw [← this]; exact hxe
  have key : ∀ a : ZMod 2, a = 0 ∨ a = 1 := by decide
  rcases key (x ⟨p0, hp0⟩) with h0 | h1
  · left
    funext i
    by_cases hi : lam.testBit i.val = true
    · simp [hconst i hi, h0]
    · by_contra hne
      exact hi (hs i hne)
  · right
    funext i
    by_cases hi : lam.testBit i.val = true
    · simp [ind, lamSet, hi, hconst i hi, h1]
    · have : x i = 0 := by by_contra hne; exact hi (hs i hne)
      simp [ind, lamSet, hi, this]

/-! ## the real instance -/
