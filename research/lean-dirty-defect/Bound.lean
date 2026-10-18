import NonlinearEcho
/- Prepared for ywz65 with OpenAI Codex assistance. Apache-2.0.
   See README for the formal/external boundary and predecessor credit. -/
set_option autoImplicit false
namespace DirtyBound
abbrev V (ι : Type) := ι → Rat
def add {ι : Type} (x y : V ι) : V ι := fun i => x i + y i
def sub {ι : Type} (x y : V ι) : V ι := fun i => x i - y i
structure Shadow (ι : Type) where
  map : V ι → V ι
  add_map : ∀ x y, map (add x y) = add (map x) (map y)
  sub_map : ∀ x y, map (sub x y) = sub (map x) (map y)
def compose {ι : Type} (a b : Shadow ι) : Shadow ι where
  map := fun x => a.map (b.map x)
  add_map := by intro x y; rw [b.add_map, a.add_map]
  sub_map := by intro x y; rw [b.sub_map, a.sub_map]
structure Gauge (ι : Type) where
  norm : V ι → Rat
  nonneg : ∀ x, 0 ≤ norm x
  add_bound : ∀ x y, norm (add x y) ≤ norm x + norm y
  sub_bound : ∀ x y, norm (sub x y) ≤ norm x + norm y
def Lipschitz {ι : Type} (N : Gauge ι) (S : Shadow ι) (K : Rat) : Prop :=
  ∀ x, N.norm (S.map x) ≤ K * N.norm x
structure Domain (ι : Type) where
  mem : V ι → Prop
  add_mem : ∀ x y, mem x → mem y → mem (add x y)
  sub_mem : ∀ x y, mem x → mem y → mem (sub x y)
def Preserves {ι : Type} (D : Domain ι) (f : V ι → V ι) : Prop :=
  ∀ x, D.mem x → D.mem (f x)
def Defect {ι : Type} (D : Domain ι) (N : Gauge ι) (f : V ι → V ι)
    (S : Shadow ι) (E : Rat) : Prop :=
  ∀ x, D.mem x → N.norm (sub (f x) (S.map x)) ≤ E
def commutator {ι : Type} (a b : V ι → V ι) (z x : V ι) : V ι :=
  sub (a (add z (b x))) (a z)
theorem defect_decomposition {ι : Type} (a b : V ι → V ι) (A B : Shadow ι)
    (z x : V ι) :
    sub (commutator a b z x) ((compose A B).map x) =
      add (A.map (sub (b x) (B.map x)))
        (sub (sub (a (add z (b x))) (A.map (add z (b x))))
          (sub (a z) (A.map z))) := by
  simp only [A.sub_map, A.add_map, compose, commutator]
  funext i
  simp only [add, sub]
  grind
theorem commutator_bound {ι : Type} (D : Domain ι) (N : Gauge ι)
    (a b : V ι → V ι) (A B : Shadow ι) (K EA EB : Rat)
    (hK : 0 ≤ K) (hA : Lipschitz N A K)
    (ha : Defect D N a A EA) (hb : Defect D N b B EB)
    (pb : Preserves D b) (z : V ι) (hz : D.mem z) :
    Defect D N (commutator a b z) (compose A B) (K * EB + 2 * EA) := by
  intro x hx
  rw [defect_decomposition]
  have h1 := N.add_bound (A.map (sub (b x) (B.map x)))
    (sub (sub (a (add z (b x))) (A.map (add z (b x)))) (sub (a z) (A.map z)))
  have h2 := N.sub_bound (sub (a (add z (b x))) (A.map (add z (b x))))
    (sub (a z) (A.map z))
  have h3 := hA (sub (b x) (B.map x))
  have h4 := Rat.mul_le_mul_of_nonneg_left (hb x hx) hK
  have h5 := ha (add z (b x)) (D.add_mem z (b x) hz (pb x hx))
  have h6 := ha z hz
  grind
inductive Tree where
  | leaf (label : Nat)
  | node (earlier later : Tree)
def leaves : Tree → Nat
  | .leaf _ => 1
  | .node b a => leaves a + leaves b
theorem leaves_pos (t : Tree) : 1 ≤ leaves t := by
  induction t with
  | leaf _ => simp [leaves]
  | node b a hb ha => simp only [leaves]; omega
def product {ι : Type} (s : Nat → Shadow ι) : Tree → Shadow ι
  | .leaf j => s j
  | .node b a => compose (product s a) (product s b)
def delta {ι : Type} (f : Nat → V ι → V ι) : Tree → (Nat → V ι) → V ι → V ι
  | .leaf j, _ => f j
  | .node b a, d => commutator (delta f a (fun n => d (n+1)))
      (delta f b (fun n => d (n+1))) (d 0)
def budget (L E : Rat) : Tree → Rat
  | .leaf _ => E
  | .node b a => L ^ leaves a * budget L E b + 2 * budget L E a
theorem delta_preserves {ι : Type} (D : Domain ι) (f : Nat → V ι → V ι)
    (hf : ∀ j, Preserves D (f j)) (t : Tree) (d : Nat → V ι)
    (hd : ∀ n, D.mem (d n)) : Preserves D (delta f t d) := by
  induction t generalizing d with
  | leaf j => exact hf j
  | node b a hb ha =>
    intro x hx
    have hd' : ∀ n, D.mem ((fun n => d (n+1)) n) := fun n => hd (n+1)
    exact D.sub_mem _ _
      (ha _ hd' _ (D.add_mem _ _ (hd 0) (hb _ hd' x hx)))
      (ha _ hd' _ (hd 0))
theorem power_add (L : Rat) (a b : Nat) : L ^ (a+b) = L^a * L^b := by
  induction b with
  | zero => simp
  | succ b ih => simp only [Nat.add_succ, Rat.pow_succ, ih]; grind
theorem power_one_le (L : Rat) (hL : 1 ≤ L) (n : Nat) : 1 ≤ L^n := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [Rat.pow_succ]
    have h0 : 0 ≤ L := by grind
    have h := Rat.mul_le_mul_of_nonneg_right ih h0
    grind
theorem power_two_le (L : Rat) (hL : 2 ≤ L) (n : Nat) (hn : 1 ≤ n) : 2 ≤ L^n := by
  cases n with
  | zero => omega
  | succ n =>
    rw [Rat.pow_succ]
    have h1 : 1 ≤ L := by grind
    have h0 : 0 ≤ L := by grind
    have h := Rat.mul_le_mul_of_nonneg_right (power_one_le L h1 n) h0
    grind
theorem product_lipschitz {ι : Type} (N : Gauge ι) (s : Nat → Shadow ι)
    (L : Rat) (hL : 0 ≤ L) (hs : ∀ j, Lipschitz N (s j) L) (t : Tree) :
    Lipschitz N (product s t) (L ^ leaves t) := by
  induction t with
  | leaf j => simpa [product, leaves] using hs j
  | node b a hb ha =>
    intro x
    have h1 := ha ((product s b).map x)
    have h2 := Rat.mul_le_mul_of_nonneg_left (hb x) (Rat.pow_nonneg (n := leaves a) hL)
    simp only [product, compose, leaves, power_add]
    grind
theorem tree_recurrence {ι : Type} (D : Domain ι) (N : Gauge ι)
    (f : Nat → V ι → V ι) (s : Nat → Shadow ι) (L E : Rat)
    (hL : 0 ≤ L) (hs : ∀ j, Lipschitz N (s j) L)
    (hf : ∀ j, Defect D N (f j) (s j) E) (pf : ∀ j, Preserves D (f j))
    (t : Tree) (d : Nat → V ι) (hd : ∀ n, D.mem (d n)) :
    Defect D N (delta f t d) (product s t) (budget L E t) := by
  induction t generalizing d with
  | leaf j => exact hf j
  | node b a hb ha =>
    have hd' : ∀ n, D.mem ((fun n => d (n+1)) n) := fun n => hd (n+1)
    exact commutator_bound D N _ _ _ _ _ _ _ (Rat.pow_nonneg hL)
      (product_lipschitz N s L hL hs a) (ha _ hd') (hb _ hd')
      (delta_preserves D f pf b _ hd') (d 0) (hd 0)
theorem mul_shuffle (p q r s : Rat) : p * (q*r*s) = q*(p*r)*s := by grind
theorem distrib (a b c e : Rat) : (a+b)*c*e = a*c*e+b*c*e := by grind
theorem merge_budget (L E : Rat) (hL : 2 ≤ L) (hE : 0 ≤ E)
    (a b : Nat) (ha : 1 ≤ a) (hb : 1 ≤ b) :
    L^a * ((b : Rat) * L^(b-1) * E) + 2 * ((a : Rat) * L^(a-1) * E)
      ≤ ((a+b : Nat) : Rat) * L^(a+b-1) * E := by
  have hL0 : 0 ≤ L := by grind
  have hpow := power_two_le L hL b hb
  have ha0 : 0 ≤ (a : Rat) := Rat.natCast_nonneg
  have hbase := Rat.mul_nonneg (Rat.mul_nonneg ha0 (Rat.pow_nonneg (n := a-1) hL0)) hE
  have hmul := Rat.mul_le_mul_of_nonneg_right hpow hbase
  have hexp1 : a + (b-1) = a+b-1 := by omega
  have hexp2 : b + (a-1) = a+b-1 := by omega
  have hp1 := power_add L a (b-1)
  have hp2 := power_add L b (a-1)
  rw [hexp1] at hp1
  rw [hexp2] at hp2
  rw [mul_shuffle (L^b), ← hp2] at hmul
  rw [mul_shuffle (L^a), ← hp1, Rat.natCast_add, distrib]
  grind only
theorem budget_closed (L E : Rat) (hL : 2 ≤ L) (hE : 0 ≤ E) (t : Tree) :
    budget L E t ≤ (leaves t : Rat) * L^(leaves t-1) * E := by
  induction t with
  | leaf j => simp [leaves, budget]
  | node b a hb ha =>
    have hL0 : 0 ≤ L := by grind
    have h1 := Rat.mul_le_mul_of_nonneg_left hb (Rat.pow_nonneg (n := leaves a) hL0)
    have h2 := Rat.mul_le_mul_of_nonneg_left ha (show (0 : Rat) ≤ 2 by decide)
    have h3 := merge_budget L E hL hE (leaves a) (leaves b) (leaves_pos a) (leaves_pos b)
    simp only [budget, leaves]
    grind
theorem all_tree_error {ι : Type} (D : Domain ι) (N : Gauge ι)
    (f : Nat → V ι → V ι) (s : Nat → Shadow ι) (L E : Rat)
    (hL : 2 ≤ L) (hE : 0 ≤ E) (hs : ∀ j, Lipschitz N (s j) L)
    (hf : ∀ j, Defect D N (f j) (s j) E) (pf : ∀ j, Preserves D (f j))
    (t : Tree) (d : Nat → V ι) (hd : ∀ n, D.mem (d n))
    (x : V ι) (hx : D.mem x) :
    N.norm (sub (delta f t d x) ((product s t).map x))
      ≤ (leaves t : Rat) * L^(leaves t-1) * E := by
  have hL0 : 0 ≤ L := by grind
  have h1 := tree_recurrence D N f s L E hL0 hs hf pf t d hd x hx
  have h2 := budget_closed L E hL hE t
  exact Rat.le_trans h1 h2
/- A sharp majorant for the scalar recurrence, without a sharpness claim
   for the actual nonlinear endpoint error. -/
def envelope (L : Rat) : Nat → Rat
  | 0 => 0
  | n+1 => L^n + 2 * envelope L n
theorem envelope_nonneg (L : Rat) (hL : 0 ≤ L) (n : Nat) : 0 ≤ envelope L n := by
  induction n with
  | zero => simp [envelope]
  | succ n ih =>
    have hp := Rat.pow_nonneg (n := n) hL
    simp only [envelope]
    grind
theorem envelope_add (L : Rat) (a b : Nat) :
    envelope L (a+b) = L^a * envelope L b + (2 : Rat)^b * envelope L a := by
  induction b with
  | zero => simp [envelope]; grind
  | succ b ih =>
    have hp := power_add L a b
    simp only [Nat.add_succ, envelope, Rat.pow_succ]
    grind
theorem envelope_closed_identity (L : Rat) (n : Nat) :
    (L-2) * envelope L n = L^n - (2 : Rat)^n := by
  induction n with
  | zero => simp [envelope]; grind
  | succ n ih => simp only [envelope, Rat.pow_succ]; grind
theorem envelope_division (L : Rat) (n : Nat) (hL : L ≠ 2) :
    envelope L n = (L^n - (2 : Rat)^n) / (L-2) := by
  have h0 : L-2 ≠ 0 := by grind
  calc
    envelope L n = envelope L n * (L-2) / (L-2) := (Rat.mul_div_cancel h0).symm
    _ = (L^n - (2 : Rat)^n) / (L-2) := by
      rw [Rat.mul_comm (envelope L n), envelope_closed_identity]
theorem envelope_at_least_four (L : Rat) (hL : 4 ≤ L) (n : Nat) (hn : 1 ≤ n) :
    envelope L n ≤ 2 * L^(n-1) := by
  cases n with
  | zero => omega
  | succ n =>
    have hL0 : 0 ≤ L := by grind
    have hp0 := Rat.pow_nonneg (n := n) hL0
    have htwo := Rat.pow_nonneg (n := n+1) (show (0 : Rat) ≤ 2 by decide)
    have hfour := Rat.mul_le_mul_of_nonneg_right hL hp0
    have hid := envelope_closed_identity L (n+1)
    rw [Rat.pow_succ] at hid
    have hm : envelope L (n+1) * (L-2) ≤ (2 * L^n) * (L-2) := by grind
    exact Rat.le_of_mul_le_mul_right hm (by grind)
theorem budget_envelope (L E : Rat) (hL : 0 ≤ L) (hE : 0 ≤ E) (t : Tree) :
    budget L E t ≤ envelope L (leaves t) * E := by
  induction t with
  | leaf j => simp [leaves, budget, envelope]; grind
  | node b a hb ha =>
    have h1 := Rat.mul_le_mul_of_nonneg_left hb (Rat.pow_nonneg (n := leaves a) hL)
    have h2 := Rat.mul_le_mul_of_nonneg_left ha (show (0 : Rat) ≤ 2 by decide)
    have h3 := power_two_le 2 (by decide) (leaves b) (leaves_pos b)
    have h4 := Rat.mul_le_mul_of_nonneg_right h3
      (Rat.mul_nonneg (envelope_nonneg L hL (leaves a)) hE)
    simp only [budget, leaves, envelope_add]
    grind
def comb : Nat → Tree
  | 0 => .leaf 0
  | n+1 => .node (.leaf 0) (comb n)
theorem comb_leaves (n : Nat) : leaves (comb n) = n+1 := by
  induction n with
  | zero => rfl
  | succ n ih => simp only [comb, leaves, ih]
theorem comb_budget (L E : Rat) (n : Nat) :
    budget L E (comb n) = envelope L (n+1) * E := by
  induction n with
  | zero => simp [comb, budget, envelope]; grind
  | succ n ih => simp only [comb, budget, comb_leaves, ih, envelope]; grind
theorem all_tree_envelope {ι : Type} (D : Domain ι) (N : Gauge ι)
    (f : Nat → V ι → V ι) (s : Nat → Shadow ι) (L E : Rat)
    (hL : 0 ≤ L) (hE : 0 ≤ E) (hs : ∀ j, Lipschitz N (s j) L)
    (hf : ∀ j, Defect D N (f j) (s j) E) (pf : ∀ j, Preserves D (f j))
    (t : Tree) (d : Nat → V ι) (hd : ∀ n, D.mem (d n))
    (x : V ι) (hx : D.mem x) :
    N.norm (sub (delta f t d x) ((product s t).map x))
      ≤ envelope L (leaves t) * E := by
  exact Rat.le_trans (tree_recurrence D N f s L E hL hs hf pf t d hd x hx)
    (budget_envelope L E hL hE t)
end DirtyBound
namespace DirtyBound
def liftI {w : Nat} (x : NonlinearEcho.Value w) : V (Fin w) := fun i => (x i : Rat)
def erase {d : Nat} : NonlinearEcho.Tree d → Tree
  | .leaf _ j => .leaf j
  | .node b a => .node (erase b) (erase a)
theorem lift_add {w : Nat} (x y : NonlinearEcho.Value w) :
    liftI (NonlinearEcho.add x y) = add (liftI x) (liftI y) := by
  funext i
  simp [liftI, NonlinearEcho.add, add]
theorem lift_sub {w : Nat} (x y : NonlinearEcho.Value w) :
    liftI (NonlinearEcho.sub x y) = sub (liftI x) (liftI y) := by
  funext i
  simp [liftI, NonlinearEcho.sub, sub]
theorem delta_lift {w d : Nat} (f : Nat → NonlinearEcho.Value w → NonlinearEcho.Value w)
    (g : Nat → V (Fin w) → V (Fin w))
    (fg : ∀ j x, g j (liftI x) = liftI (f j x)) (t : NonlinearEcho.Tree d)
    (s : NonlinearEcho.Dirt w d) (r : Nat → V (Fin w))
    (sr : ∀ i : Fin d, r i.val = liftI (s i)) (x : NonlinearEcho.Value w) :
    delta g (erase t) r (liftI x) = liftI (NonlinearEcho.delta f t x s) := by
  induction t generalizing x r with
  | leaf depth j => exact fg j x
  | @node depth b a hb ha =>
    have hs : ∀ i : Fin depth, (fun n => r (n+1)) i.val =
        liftI ((NonlinearEcho.tail s) i) := fun i => sr i.succ
    have h0 : r 0 = liftI (NonlinearEcho.head s) := sr 0
    simp only [erase, delta, commutator, NonlinearEcho.delta]
    rw [hb _ _ hs x, h0, ← lift_add, ha _ _ hs _, ha _ _ hs _, ← lift_sub]
theorem execution_error {w d : Nat} (D : Domain (Fin w)) (N : Gauge (Fin w))
    (f : Nat → NonlinearEcho.Value w → NonlinearEcho.Value w)
    (g : Nat → V (Fin w) → V (Fin w)) (S : Nat → Shadow (Fin w)) (L E : Rat)
    (fg : ∀ j x, g j (liftI x) = liftI (f j x))
    (hL : 2 ≤ L) (hE : 0 ≤ E) (hS : ∀ j, Lipschitz N (S j) L)
    (hg : ∀ j, Defect D N (g j) (S j) E) (pg : ∀ j, Preserves D (g j))
    (t : NonlinearEcho.Tree d) (s : NonlinearEcho.Dirt w d)
    (r : Nat → V (Fin w)) (sr : ∀ i : Fin d, r i.val = liftI (s i))
    (hr : ∀ n, D.mem (r n)) (x y : NonlinearEcho.Value w) (hx : D.mem (liftI x)) :
    N.norm (sub (liftI (NonlinearEcho.sub (NonlinearEcho.run f t true x y s).1 y))
      ((product S (erase t)).map (liftI x)))
      ≤ (leaves (erase t) : Rat) * L^(leaves (erase t)-1) * E := by
  rw [NonlinearEcho.positive_increment, ← delta_lift f g fg t s r sr x]
  exact all_tree_error D N g S L E hL hE hS hg pg (erase t) r hr (liftI x) hx
theorem execution_envelope {w d : Nat} (D : Domain (Fin w)) (N : Gauge (Fin w))
    (f : Nat → NonlinearEcho.Value w → NonlinearEcho.Value w)
    (g : Nat → V (Fin w) → V (Fin w)) (S : Nat → Shadow (Fin w)) (L E : Rat)
    (fg : ∀ j x, g j (liftI x) = liftI (f j x))
    (hL : 0 ≤ L) (hE : 0 ≤ E) (hS : ∀ j, Lipschitz N (S j) L)
    (hg : ∀ j, Defect D N (g j) (S j) E) (pg : ∀ j, Preserves D (g j))
    (t : NonlinearEcho.Tree d) (s : NonlinearEcho.Dirt w d)
    (r : Nat → V (Fin w)) (sr : ∀ i : Fin d, r i.val = liftI (s i))
    (hr : ∀ n, D.mem (r n)) (x y : NonlinearEcho.Value w) (hx : D.mem (liftI x)) :
    N.norm (sub (liftI (NonlinearEcho.sub (NonlinearEcho.run f t true x y s).1 y))
      ((product S (erase t)).map (liftI x)))
      ≤ envelope L (leaves (erase t)) * E := by
  rw [NonlinearEcho.positive_increment, ← delta_lift f g fg t s r sr x]
  exact all_tree_envelope D N g S L E hL hE hS hg pg (erase t) r hr (liftI x) hx
end DirtyBound
