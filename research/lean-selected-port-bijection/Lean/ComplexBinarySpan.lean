import Lean

/-! Fresh reconstruction after the 2026-10-10 executor loss. These are generic
Nat-mask XOR-span arguments, not recovered archival proof bytes or instances. -/
namespace CurrentMain.BinaryFrame

def Span : List Nat → Nat → Prop
  | [], n => n = 0
  | b :: bs, n => Span bs n ∨ ∃ m, Span bs m ∧ n = b ^^^ m

theorem span_nil (n : Nat) : Span [] n ↔ n = 0 := Iff.rfl

theorem span_cons (b : Nat) (bs : List Nat) (n : Nat) :
    Span (b :: bs) n ↔ Span bs n ∨ ∃ m, Span bs m ∧ n = b ^^^ m := Iff.rfl

theorem span_zero (rows : List Nat) : Span rows 0 := by
  induction rows with
  | nil => rfl
  | cons b bs ih => exact Or.inl ih

theorem span_mem (rows : List Nat) (n : Nat) (hn : n ∈ rows) : Span rows n := by
  induction rows with
  | nil => simp at hn
  | cons b bs ih =>
    rcases List.mem_cons.mp hn with rfl | hn
    · exact Or.inr ⟨0, span_zero bs, by simp⟩
    · exact Or.inl (ih hn)

theorem xor_pair_cancel (b x y : Nat) :
    (b ^^^ x) ^^^ (b ^^^ y) = x ^^^ y := by
  calc
    _ = (b ^^^ b) ^^^ (x ^^^ y) := by ac_rfl
    _ = _ := by simp

theorem span_xor (rows : List Nat) (x y : Nat)
    (hx : Span rows x) (hy : Span rows y) : Span rows (x ^^^ y) := by
  induction rows generalizing x y with
  | nil =>
    change x = 0 at hx
    change y = 0 at hy
    simp [Span, hx, hy]
  | cons b bs ih =>
    rcases hx with hx | ⟨p,hp,rfl⟩ <;> rcases hy with hy | ⟨q,hq,rfl⟩
    · exact Or.inl (ih _ _ hx hy)
    · exact Or.inr ⟨x ^^^ q, ih _ _ hx hq, by ac_rfl⟩
    · exact Or.inr ⟨p ^^^ y, ih _ _ hp hy, Nat.xor_assoc _ _ _⟩
    · exact Or.inl (by simpa only [xor_pair_cancel] using ih _ _ hp hq)

theorem span_mono (small large : List Nat)
    (generators : ∀ b ∈ small, Span large b) (n : Nat)
    (hn : Span small n) : Span large n := by
  induction small generalizing n with
  | nil =>
    change n = 0 at hn
    subst n
    exact span_zero large
  | cons b bs ih =>
    have rest : ∀ x ∈ bs, Span large x := fun x hx => generators x (List.mem_cons_of_mem b hx)
    rcases hn with hn | ⟨m,hm,rfl⟩
    · exact ih rest _ hn
    · exact span_xor large b m (generators b (by simp)) (ih rest _ hm)

theorem span_induction (rows : List Nat) (P : Nat → Prop)
    (zero : P 0) (generators : ∀ b ∈ rows, P b)
    (xor_closed : ∀ a b, P a → P b → P (a ^^^ b))
    (n : Nat) (hn : Span rows n) : P n := by
  induction rows generalizing n with
  | nil =>
    change n = 0 at hn
    simpa only [hn] using zero
  | cons b bs ih =>
    have rest : ∀ x ∈ bs, P x := fun x hx => generators x (List.mem_cons_of_mem b hx)
    rcases hn with hn | ⟨m,hm,rfl⟩
    · exact ih rest _ hn
    · exact xor_closed b m (generators b (by simp)) (ih rest _ hm)

theorem span_bit_zero (rows : List Nat) (p : Nat)
    (zero : ∀ b ∈ rows, b.testBit p = false) (n : Nat)
    (hn : Span rows n) : n.testBit p = false := by
  induction rows generalizing n with
  | nil =>
    change n = 0 at hn
    simp [hn]
  | cons b bs ih =>
    have hb := zero b (by simp)
    have rest : ∀ x ∈ bs, x.testBit p = false := fun x hx => zero x (List.mem_cons_of_mem b hx)
    rcases hn with hn | ⟨m,hm,rfl⟩
    · exact ih rest _ hn
    · simp [Nat.testBit_xor, hb, ih rest _ hm]

def masksBounded (h : Nat) (rows : List Nat) : Bool :=
  rows.all (fun n => decide (n < 2^h))

theorem masksBounded_sound (h : Nat) (rows : List Nat)
    (checked : masksBounded h rows = true) : ∀ n ∈ rows, n < 2^h := by
  intro n hn
  exact of_decide_eq_true (List.all_eq_true.mp checked n hn)

theorem span_bounded (h : Nat) (rows : List Nat)
    (bounded : ∀ b ∈ rows, b < 2^h) (n : Nat) (hn : Span rows n) : n < 2^h := by
  induction rows generalizing n with
  | nil =>
    change n = 0 at hn
    subst n
    exact Nat.two_pow_pos h
  | cons b bs ih =>
    have hb := bounded b (by simp)
    have rest : ∀ x ∈ bs, x < 2^h := fun x hx => bounded x (List.mem_cons_of_mem b hx)
    rcases hn with hn | ⟨m,hm,rfl⟩
    · exact ih rest _ hn
    · exact Nat.xor_lt_two_pow hb (ih rest _ hm)

def rowAt : List Nat → Nat → Nat
  | [], _ => 0
  | b :: _, 0 => b
  | _ :: bs, i+1 => rowAt bs i

theorem rowAt_span (rows : List Nat) (i : Nat) : Span rows (rowAt rows i) := by
  induction rows generalizing i with
  | nil => rfl
  | cons b bs ih =>
    cases i with
    | zero => exact Or.inr ⟨0, span_zero bs, by simp [rowAt]⟩
    | succ i => exact Or.inl (ih i)

def witnessSum (rows : List Nat) : List Nat → Nat
  | [] => 0
  | i :: rest => rowAt rows i ^^^ witnessSum rows rest

theorem witnessSum_span (rows : List Nat) (indices : List Nat) :
    Span rows (witnessSum rows indices) := by
  induction indices with
  | nil => exact span_zero rows
  | cons i rest ih => exact span_xor rows _ _ (rowAt_span rows i) ih

def containmentCheck (small large : List Nat) : List (List Nat) → Bool :=
  match small with
  | [] => fun witnesses => witnesses.isEmpty
  | b :: bs => fun witnesses => match witnesses with
    | [] => false
    | w :: ws => decide (witnessSum large w = b) && containmentCheck bs large ws

theorem containment_generators (small large : List Nat) (witnesses : List (List Nat))
    (checked : containmentCheck small large witnesses = true) :
    ∀ b ∈ small, Span large b := by
  induction small generalizing witnesses with
  | nil => intro b hb; simp at hb
  | cons b bs ih =>
    cases witnesses with
    | nil => simp [containmentCheck] at checked
    | cons w ws =>
      have hc := Bool.and_eq_true_iff.mp checked
      have eq : witnessSum large w = b := of_decide_eq_true hc.1
      intro x hx
      rcases List.mem_cons.mp hx with rfl | hx
      · rw [← eq]
        exact witnessSum_span large w
      · exact ih ws hc.2 x hx

theorem containment_sound (small large : List Nat) (witnesses : List (List Nat))
    (checked : containmentCheck small large witnesses = true) :
    ∀ n, Span small n → Span large n :=
  span_mono small large (containment_generators small large witnesses checked)

end CurrentMain.BinaryFrame
#print axioms CurrentMain.BinaryFrame.span_nil
#print axioms CurrentMain.BinaryFrame.span_cons
#print axioms CurrentMain.BinaryFrame.span_zero
#print axioms CurrentMain.BinaryFrame.span_mem
#print axioms CurrentMain.BinaryFrame.xor_pair_cancel
#print axioms CurrentMain.BinaryFrame.span_xor
#print axioms CurrentMain.BinaryFrame.span_mono
#print axioms CurrentMain.BinaryFrame.span_induction
#print axioms CurrentMain.BinaryFrame.span_bit_zero
#print axioms CurrentMain.BinaryFrame.masksBounded_sound
#print axioms CurrentMain.BinaryFrame.span_bounded
#print axioms CurrentMain.BinaryFrame.rowAt_span
#print axioms CurrentMain.BinaryFrame.witnessSum_span
#print axioms CurrentMain.BinaryFrame.containment_generators
#print axioms CurrentMain.BinaryFrame.containment_sound
