import Std

/-!
An address uses occurrence labels. Two equal ranks can name different ports.
The paid history is in reverse time order. The first remaining target label
determines the port at which the next paid request enters the child.
-/
namespace MixedCompiler

variable {K J : Type}

structure Node (K J : Type) where
  history : List J
  future : List K
  deriving DecidableEq

structure Demand (K J : Type) where
  node : Node K J
  paid : J
  deriving DecidableEq

structure Port (K J : Type) where
  node : Node K J
  target : K
  deriving DecidableEq

def child : Demand K J → Option (Port K J)
  | ⟨⟨_, []⟩, _⟩ => none
  | ⟨⟨p, k :: a⟩, j⟩ => some ⟨⟨j :: p, a⟩, k⟩

def parent : Port K J → Option (Demand K J)
  | ⟨⟨[], _⟩, _⟩ => none
  | ⟨⟨j :: p, a⟩, k⟩ => some ⟨⟨p, k :: a⟩, j⟩

theorem matched_iff (d : Demand K J) (s : Port K J) :
    child d = some s ↔ parent s = some d := by
  obtain ⟨⟨p, a⟩, j⟩ := d
  obtain ⟨⟨q, b⟩, k⟩ := s
  cases a <;> cases q <;> simp [child, parent, and_comm, and_left_comm, and_assoc, eq_comm]

def mass {A : Type} (rank : A → Nat) : List A → Nat
  | [] => 1
  | x :: xs => rank x * mass rank xs

def scale (rank : K → Nat) (paid : J → Nat) (u : Node K J) : Nat :=
  mass paid u.history * mass rank u.future

def live (rank : K → Nat) (paid : J → Nat) (A n : Nat) (u : Node K J) : Prop :=
  A * scale rank paid u ≤ n

def demandRank (rank : K → Nat) (paid : J → Nat) (d : Demand K J) : Nat :=
  paid d.paid * scale rank paid d.node

def portRank (rank : K → Nat) (paid : J → Nat) (s : Port K J) : Nat :=
  rank s.target * scale rank paid s.node

def depth (u : Node K J) : Nat := u.history.length + u.future.length

variable (rank : K → Nat) (paid : J → Nat)

theorem edge (d : Demand K J) (s : Port K J) (h : child d = some s) :
    demandRank rank paid d = portRank rank paid s ∧
    depth d.node = depth s.node ∧
    d.node.future.length = s.node.future.length + 1 := by
  obtain ⟨⟨p, a⟩, j⟩ := d
  cases a with
  | nil => simp [child] at h
  | cons k a =>
    cases h
    simp [demandRank, portRank, scale, depth, mass,
      Nat.mul_assoc, Nat.mul_comm, Nat.mul_left_comm, Nat.add_comm, Nat.add_left_comm]

theorem fits_child (A n : Nat) (separated : ∀ j k, paid j ≤ rank k)
    (d : Demand K J) (s : Port K J) (h : child d = some s)
    (hl : live rank paid A n d.node) : live rank paid A n s.node := by
  obtain ⟨⟨p, a⟩, j⟩ := d
  cases a with
  | nil => simp [child] at h
  | cons k a =>
    cases h
    have hmul := Nat.mul_le_mul_left (A * mass paid p * mass rank a) (separated j k)
    simp only [live, scale, mass] at hl ⊢
    apply Nat.le_trans _ hl
    simpa only [Nat.mul_assoc, Nat.mul_comm, Nat.mul_left_comm] using hmul

/-- A port is external if its unique parent is missing or is above the ambient cap. -/
def external (A n : Nat) (s : Port K J) : Prop :=
  match parent s with
  | none => True
  | some d => ¬live rank paid A n d.node

theorem external_or_unique (A n : Nat) (s : Port K J) :
    (external rank paid A n s ∧
        ¬∃ d, live rank paid A n d.node ∧ child d = some s) ∨
    (¬external rank paid A n s ∧
        ∃ d, (live rank paid A n d.node ∧ child d = some s) ∧
          (∀ e, live rank paid A n e.node → child e = some s → e = d)) := by
  cases h : parent s with
  | none =>
    left
    refine ⟨by simp [external, h], ?_⟩
    rintro ⟨d, _, hd⟩
    rw [matched_iff, h] at hd
    cases hd
  | some d =>
    by_cases hd : A * scale rank paid d.node ≤ n
    · right
      refine ⟨?_, d, ⟨hd, (matched_iff d s).mpr h⟩, ?_⟩
      · unfold external
        rw [h]
        exact fun nope => nope hd
      · intro e _ he
        exact Option.some.inj ((matched_iff e s).mp he |>.symm.trans h)
    · left
      refine ⟨by simpa [external, h, live] using hd, ?_⟩
      rintro ⟨e, he, hed⟩
      have hs : e = d := Option.some.inj (((matched_iff e s).mp hed).symm.trans h)
      exact hd (hs ▸ he)

theorem external_interval (A n G : Nat)
    (positive : ∀ j, 0 < paid j) (bounded : ∀ k, rank k ≤ A)
    (top : ∀ a : List K, a.length = G + 1 → n < A * mass rank a)
    (s : Port K J) (hl : live rank paid A n s.node)
    (hg : depth s.node = G) (hx : external rank paid A n s) :
    n < A * portRank rank paid s ∧ portRank rank paid s ≤ n := by
  constructor
  · obtain ⟨⟨p,a⟩,k⟩ := s
    cases p with
    | nil =>
      have ha : a.length = G := by simpa [depth] using hg
      simpa [portRank, scale, mass] using
        top (k :: a) (by simp [ha])
    | cons j p =>
      have hv : n < A * scale rank paid ⟨p, k :: a⟩ := by
        simpa [external, parent, live] using hx
      have hmul := Nat.le_mul_of_pos_left
        (A * scale rank paid ⟨p, k :: a⟩) (positive j)
      apply Nat.lt_of_lt_of_le hv
      simpa only [portRank, scale, mass, Nat.mul_assoc, Nat.mul_comm, Nat.mul_left_comm] using hmul
  · exact Nat.le_trans (Nat.mul_le_mul_right _ (bounded s.target)) hl

theorem product_bounds {A : Type} (w : A → Nat) (xs : List A) (lo hi : Nat)
    (lower : ∀ x, lo ≤ w x) (upper : ∀ x, w x ≤ hi) :
    lo ^ xs.length ≤ mass w xs ∧ mass w xs ≤ hi ^ xs.length := by
  induction xs with
  | nil => simp [mass]
  | cons x xs ih =>
    simp only [List.length_cons, Nat.pow_succ, mass]
    constructor
    · rw [Nat.mul_comm]
      exact Nat.mul_le_mul (lower x) ih.1
    · rw [Nat.mul_comm (hi ^ xs.length)]
      exact Nat.mul_le_mul (upper x) ih.2

/-- Advance the floor by one target, with an explicit bound on the number of steps. -/
def horizon (n k a : Nat) : Nat → Nat
  | 0 => 0
  | fuel+1 => if a*k ≤ n then horizon n k (a*k) fuel + 1 else 0

theorem horizon_spec (n k a fuel : Nat) (hk : 1 < k) (ha : 0 < a)
    (start : a ≤ n) (enough : n - a < fuel) :
    a * k ^ horizon n k a fuel ≤ n ∧ n < a * k ^ (horizon n k a fuel + 1) := by
  induction fuel generalizing a with
  | zero => omega
  | succ fuel ih =>
    by_cases step : a*k ≤ n
    · have growth : a < a*k := by
        simpa only [Nat.mul_one] using Nat.mul_lt_mul_of_pos_left hk ha
      have later := ih (a*k) (Nat.mul_pos ha (by omega)) step (by omega)
      simp only [horizon, step, ite_true]
      constructor
      · rw [Nat.pow_succ]
        simpa only [Nat.mul_assoc, Nat.mul_comm, Nat.mul_left_comm] using later.1
      · rw [Nat.pow_succ]
        simpa only [Nat.mul_assoc, Nat.mul_comm, Nat.mul_left_comm] using later.2
    · simpa [horizon, step] using And.intro start (Nat.lt_of_not_ge step)

theorem root_cut (A n lo : Nat) (ha : 0 < A) (han : A ≤ n) (hm : 1 < lo)
    (lower : ∀ k, lo ≤ rank k) (upper : ∀ k, rank k ≤ A) (a : List K)
    (h : a.length = horizon n lo A (n+1) + 1) : n < A * mass rank a := by
  have ht := (horizon_spec n lo A (n+1) hm ha han (by omega)).2
  have hw := (product_bounds rank a lo A lower upper).1
  rw [h] at hw
  exact Nat.lt_of_lt_of_le ht (Nat.mul_le_mul_left A hw)

theorem exit_bound (G hi : Nat) (upper : ∀ j, paid j ≤ hi)
    (d : Demand K J) (hg : depth d.node = G) (he : child d = none) :
    demandRank rank paid d ≤ hi ^ (G + 1) := by
  obtain ⟨⟨p, a⟩, j⟩ := d
  cases a with
  | cons k a => simp [child] at he
  | nil =>
    have hp : p.length = G := by simpa [depth] using hg
    have h := (product_bounds paid p 0 hi (fun _ => Nat.zero_le _) upper).2
    rw [← hp, Nat.pow_succ, Nat.mul_comm]
    simpa [demandRank, scale, mass] using Nat.mul_le_mul (upper j) h

section Census

/-- Enumerate ordered occurrence labels. A sum with the indicator of a rank counts
that rank over the integers. Thus the same census applies to real moment prices. -/
def total {X : Type} (xs : List X) (f : X → Int) : Int :=
  (xs.map f).sum

theorem total_nil {X : Type} (f : X → Int) : total [] f = 0 := rfl

theorem total_cons {X : Type} (x : X) (xs : List X) (f : X → Int) :
    total (x::xs) f = f x + total xs f := by simp [total]

theorem total_congr {X : Type} (xs : List X) (f g : X → Int) (eq : ∀ x, f x = g x) :
    total xs f = total xs g := by
  induction xs with
  | nil => rfl
  | cons x xs h => simp only [total_cons, eq, h]

theorem total_zero {X : Type} (xs : List X) : total xs (fun _ => 0) = 0 := by
  induction xs <;> simp [total_nil, total_cons, *]

theorem total_add {X : Type} (xs : List X) (f g : X → Int) :
    total xs (fun x => f x + g x) = total xs f + total xs g := by
  induction xs with
  | nil => rfl
  | cons x xs h => simp only [total_cons, h]; omega

theorem total_sub {X : Type} (xs : List X) (f g : X → Int) :
    total xs (fun x => f x - g x) = total xs f - total xs g := by
  induction xs with
  | nil => rfl
  | cons x xs h => simp only [total_cons, h]; omega

theorem total_append {X : Type} (xs ys : List X) (f : X → Int) :
    total (xs ++ ys) f = total xs f + total ys f := by
  induction xs with
  | nil => simp [total_nil]
  | cons x xs h => simp only [List.cons_append, total_cons, h, Int.add_assoc]

theorem total_map {X Y : Type} (xs : List X) (f : X → Y) (g : Y → Int) :
    total (xs.map f) g = total xs (fun x => g (f x)) := by simp [total, List.map_map, Function.comp_def]

theorem total_flatMap {X Y : Type} (xs : List X) (f : X → List Y) (g : Y → Int) :
    total (xs.flatMap f) g = total xs (fun x => total (f x) g) := by
  induction xs with
  | nil => rfl
  | cons x xs h => simp only [List.flatMap_cons, total_append, h, total_cons]

def words (xs : List K) : Nat → List (List K)
  | 0 => [[]]
  | m+1 => (words xs m).flatMap (fun a => xs.map (fun k => k::a))

theorem mem_words (ks : List K) (m : Nat) (a : List K) :
    a ∈ words ks m ↔ a.length = m ∧ ∀ k ∈ a, k ∈ ks := by
  induction m generalizing a with
  | zero =>
    cases a with
    | nil =>
      constructor
      · intro _
        exact ⟨rfl, fun _ h => nomatch h⟩
      · intro _
        exact List.Mem.head _
    | cons k a =>
      constructor
      · intro h
        have hnil : k::a = [] := List.mem_singleton.mp h
        cases hnil
      · intro h
        cases h.1
  | succ m ih =>
    cases a with
    | nil =>
      constructor
      · intro h
        obtain ⟨a, _, ha⟩ := List.mem_flatMap.mp h
        obtain ⟨i, _, impossible⟩ := List.mem_map.mp ha
        cases impossible
      · intro h
        cases h.1
    | cons k a =>
      simp only [words, List.mem_flatMap, List.mem_map, List.cons.injEq,
        List.length_cons, Nat.succ.injEq, List.forall_mem_cons]
      constructor
      · rintro ⟨b, hb, i, hi, rfl, rfl⟩
        exact ⟨((ih b).mp hb).1, hi, ((ih b).mp hb).2⟩
      · rintro ⟨ha, hk, hs⟩
        exact ⟨a, (ih a).mpr ⟨ha, hs⟩, k, hk, rfl, rfl⟩

theorem words_nodup (ks : List K) (unique : ks.Nodup) (m : Nat) :
    (words ks m).Nodup := by
  induction m with
  | zero => simp [words]
  | succ m ih =>
    simp only [words, List.Nodup, List.pairwise_flatMap, List.pairwise_map]
    constructor
    · intro a _
      exact unique.imp (fun h eq => h (List.cons.inj eq).1)
    · apply ih.imp
      intro a b hab x hx y hy
      obtain ⟨i, _, rfl⟩ := List.mem_map.mp hx
      obtain ⟨k, _, rfl⟩ := List.mem_map.mp hy
      exact fun eq => hab (List.cons.inj eq).2

def legal (ks : List K) (js : List J) (G : Nat) (u : Node K J) : Prop :=
  depth u = G ∧ (∀ j ∈ u.history, j ∈ js) ∧ (∀ k ∈ u.future, k ∈ ks)

theorem legal_edge (ks : List K) (js : List J) (G : Nat)
    (d : Demand K J) (s : Port K J) (h : child d = some s) :
    (legal ks js G d.node ∧ d.paid ∈ js) ↔ (legal ks js G s.node ∧ s.target ∈ ks) := by
  obtain ⟨⟨p, a⟩, j⟩ := d
  cases a with
  | nil => simp [child] at h
  | cons k a =>
    cases h
    simp [legal, depth, Nat.add_comm, Nat.add_left_comm,
      and_comm, and_left_comm, and_assoc]

/-- A genuine portal has exactly its live enumerated parent, or is charged as a source. -/
theorem enumerated_sources (ks : List K) (js : List J) (G A n : Nat) (s : Port K J)
    (hs : legal ks js G s.node ∧ s.target ∈ ks) :
    external rank paid A n s ↔
      ¬∃ d, (legal ks js G d.node ∧ d.paid ∈ js) ∧
             live rank paid A n d.node ∧ child d = some s := by
  rcases external_or_unique rank paid A n s with ⟨he,hn⟩ | ⟨hn,d,hd,_⟩
  · exact ⟨fun _ ⟨d,_,h⟩ => hn ⟨d,h⟩, fun _ => he⟩
  · have hl := (legal_edge ks js G d s hd.2).mpr hs
    exact ⟨fun he => (hn he).elim, fun h => (h ⟨d,hl,hd⟩).elim⟩

theorem admitted_source (ks : List K) (js : List J) (A n lo : Nat)
    (base : A ≤ n) (ambient : 0 < A) (floorGt : 1 < lo)
    (paidPos : ∀ j, 0 < paid j) (atLeast : ∀ k, lo ≤ rank k) (atMost : ∀ k, rank k ≤ A)
    (s : Port K J) (hlive : live rank paid A n s.node)
    (hin : legal ks js (horizon n lo A (n+1)) s.node ∧ s.target ∈ ks)
    (outside : external rank paid A n s) :
    (n < A * portRank rank paid s ∧ portRank rank paid s ≤ n) ∧
    ¬∃ d, (legal ks js (horizon n lo A (n+1)) d.node ∧ d.paid ∈ js) ∧
             live rank paid A n d.node ∧ child d = some s := by
  constructor
  · apply external_interval rank paid A n _ paidPos atMost _ s hlive hin.1.1 outside
    exact root_cut rank A n lo ambient base floorGt atLeast atMost
  · exact (enumerated_sources rank paid ks js _ A n s hin).mp outside

theorem mass_replicate (k : K) (m : Nat) :
    mass rank (List.replicate m k) = rank k ^ m := by
  induction m with
  | zero => rfl
  | succ m ih => simp [List.replicate_succ, mass, ih, Nat.pow_succ, Nat.mul_comm]

theorem has_root (ks : List K) (k : K) (hk : k ∈ ks) (A n : Nat)
    (ha : 0 < A) (han : A ≤ n) (hm : 1 < rank k) :
    let G := horizon n (rank k) A (n+1)
    ∃ a ∈ words ks G, live rank paid A n ⟨[],a⟩ ∧
        ∀ i ∈ ks, external rank paid A n ⟨⟨[],a⟩,i⟩ := by
  intro G
  refine ⟨List.replicate G k, (mem_words ks G _).mpr ⟨by simp, ?_⟩, ?_, ?_⟩
  · intro i hi
    exact (List.eq_of_mem_replicate hi).symm ▸ hk
  · have hh := (horizon_spec n (rank k) A (n+1) hm ha han (by omega)).1
    simpa only [live, scale, mass, Nat.one_mul, mass_replicate, G] using hh
  · intro i _
    trivial

variable (ks : List K) (js : List J) (A n : Nat) (price : Nat → Int)

def charge (u : Node K J) (v : Int) : Int :=
  if A * scale rank paid u ≤ n then v else 0

def inputs (p : List J) (m : Nat) : Int :=
  total (words ks m) (fun a => total ks (fun k =>
    charge rank paid A n ⟨p,a⟩ (price (portRank rank paid ⟨⟨p,a⟩, k⟩))))

def paidAt (p : List J) (j : J) (m : Nat) : Int :=
  total (words ks m) (fun a =>
    charge rank paid A n ⟨p,a⟩ (price (demandRank rank paid ⟨⟨p,a⟩, j⟩)))

def newSources (p : List J) (j : J) (m : Nat) : Int :=
  total (words ks m) (fun a => total ks (fun k =>
    if A * scale rank paid ⟨p, k :: a⟩ ≤ n then 0 else
      charge rank paid A n ⟨j :: p, a⟩ (price (portRank rank paid ⟨⟨j :: p,a⟩,k⟩))))

theorem count_edge (sep : ∀ j k, paid j ≤ rank k) (p : List J) (j : J) (m : Nat) :
    newSources rank paid ks A n price p j m + paidAt rank paid ks A n price p j (m+1) =
    inputs rank paid ks A n price (j::p) m := by
  simp only [newSources, paidAt, inputs, words, total_flatMap, total_map]
  rw [← total_add]
  apply total_congr
  intro a
  rw [← total_add]
  apply total_congr
  intro k
  by_cases h : A * scale rank paid ⟨p, k::a⟩ ≤ n
  · have hl := fits_child rank paid A n sep ⟨⟨p,k::a⟩,j⟩ ⟨⟨j::p,a⟩,k⟩ rfl h
    have he := (edge rank paid ⟨⟨p,k::a⟩,j⟩ ⟨⟨j::p,a⟩,k⟩ rfl).1
    simp only [live] at hl
    simp only [charge, h, hl, ite_true, Int.zero_add, he]
  · simp only [charge, h, ite_false, Int.add_zero]

/-- Pay the local cost at each retained unit before visiting its child classes. -/
def sumLocal (p : List J) : Nat → Int
  | 0 => inputs rank paid ks A n price p 0 - total js (fun j => paidAt rank paid ks A n price p j 0)
  | m+1 => inputs rank paid ks A n price p (m+1) -
      total js (fun j => paidAt rank paid ks A n price p j (m+1)) +
      total js (fun j => sumLocal (j::p) m)

/-- Count external ports below the current class. -/
def deeperSources (p : List J) : Nat → Int
  | 0 => 0
  | m+1 => total js (fun j =>
      newSources rank paid ks A n price p j m + deeperSources (j::p) m)

/-- Keep the exact order of paid labels at a leaf class. -/
def exits (p : List J) : Nat → Int
  | 0 => total js (fun j => paidAt rank paid ks A n price p j 0)
  | m+1 => total js (fun j => exits (j::p) m)

theorem cancellation (sep : ∀ j k, paid j ≤ rank k) (p : List J) (m : Nat) :
    sumLocal rank paid ks js A n price p m =
    inputs rank paid ks A n price p m + deeperSources rank paid ks js A n price p m -
    exits rank paid ks js A n price p m := by
  induction m generalizing p with
  | zero => simp only [sumLocal, deeperSources, exits, Int.add_zero]
  | succ m ih =>
    simp only [sumLocal, deeperSources, exits]
    have tt := total_congr js _ _ (fun j => ih (j::p))
    rw [tt, total_sub, total_add, total_add]
    have hs := total_congr js _ _ (fun j => count_edge rank paid ks A n price sep p j m)
    rw [total_add] at hs
    omega

end Census

section Batching

def replication (width : Nat → Nat) (ranks : List Nat) : Nat :=
  mass width ranks

theorem replication_positive (width : Nat → Nat) (positive : ∀ r, 0 < width r)
    (ranks : List Nat) : 0 < replication width ranks := by
  induction ranks with
  | nil => exact Nat.zero_lt_one
  | cons e es ih => exact Nat.mul_pos (positive e) ih

theorem width_divides (width : Nat → Nat) (ranks : List Nat) (r : Nat) (h : r ∈ ranks) :
    width r ∣ replication width ranks := by
  induction ranks with
  | nil => simp at h
  | cons e es ih =>
    rcases List.mem_cons.mp h with he | he
    · subst r
      exact Nat.dvd_mul_right _ _
    · exact Nat.dvd_trans (ih he) (Nat.dvd_mul_left _ _)

/-- At a fixed slot, assign one contiguous block of arrays to each smaller program.
Ranks can repeat at different slots. -/
theorem cleared_batch (width : Nat → Nat) (ranks : List Nat)
    (r multiplicity work : Nat) (hr : r ∈ ranks) :
    let copies := replication width ranks * multiplicity
    let groups := copies / width r
    groups * width r = copies ∧ (groups * work) * width r = copies * work := by
  intro copies groups
  have h : width r ∣ copies :=
    Nat.dvd_trans (width_divides width ranks r hr) (Nat.dvd_mul_right _ _)
  have eqn : groups * width r = copies := Nat.div_mul_cancel h
  exact ⟨eqn, by rw [← eqn]; ac_rfl⟩

/-- A chronological word has ordinary records and complete, synchronous calls. -/
inductive Record (I P : Type) where
  | ordinary : I → Record I P
  | call : P → Record I P

def inline {I P Q : Type} (body : P → List (Record I Q)) :
    List (Record I P) → List (Record I Q)
  | [] => []
  | .ordinary i :: tail => .ordinary i :: inline body tail
  | .call p :: tail => body p ++ inline body tail

def execute {I P S : Type} (op : I → S → S) (call : P → S → S) :
    List (Record I P) → S → S
  | [], s => s
  | .ordinary i :: tail, s => execute op call tail (op i s)
  | .call p :: tail, s => execute op call tail (call p s)

theorem execute_append {I P S : Type} (op : I → S → S) (childOp : P → S → S)
    (left right : List (Record I P)) (s : S) :
    execute op childOp (left ++ right) s = execute op childOp right (execute op childOp left s) := by
  induction left generalizing s with
  | nil => rfl
  | cons r tail ih => cases r <;> exact ih _

/-- Inlining preserves the complete state at every returned job. The state can
contain payloads, parked banks, private work and tapes. -/
theorem execute_inline {I P Q S : Type} (op : I → S → S) (req : P → S → S)
    (leaves : Q → S → S) (body : P → List (Record I Q))
    (correct : ∀ p s, execute op leaves (body p) s = req p s)
    (word : List (Record I P)) (s : S) :
    execute op leaves (inline body word) s = execute op req word s := by
  induction word generalizing s with
  | nil => rfl
  | cons r tail ih =>
    cases r with
    | ordinary i => exact ih (op i s)
    | call p =>
      simp only [inline, execute_append, correct, execute]
      exact ih _

end Batching

end MixedCompiler

#print axioms MixedCompiler.edge
#print axioms MixedCompiler.matched_iff
#print axioms MixedCompiler.fits_child
#print axioms MixedCompiler.external_or_unique
#print axioms MixedCompiler.external_interval
#print axioms MixedCompiler.exit_bound
#print axioms MixedCompiler.horizon_spec
#print axioms MixedCompiler.root_cut
#print axioms MixedCompiler.count_edge
#print axioms MixedCompiler.mem_words
#print axioms MixedCompiler.words_nodup
#print axioms MixedCompiler.enumerated_sources
#print axioms MixedCompiler.admitted_source
#print axioms MixedCompiler.has_root
#print axioms MixedCompiler.cancellation
#print axioms MixedCompiler.cleared_batch
#print axioms MixedCompiler.execute_inline
