import DirtyWrapper

/-!
Address-gauge refinement of literal XOR traces.

Payloads on every original role are arbitrary.  A gauge maps a logical address
to its physical location. A reframe from `old` to `new` therefore reads the
old row at `old.forward (new.inverse physicalAddress)`; its orientation is
part of the definition, not an assumed commutation rule. A typed XOR requires
equality of the two current gauges. The main theorem erases reframes and proves
that the decoded physical execution equals the literal scalar XOR word.

No finite graph is instantiated here. In particular, this file does not prove
that the repository's subspace labels give the required concrete permutations,
that its full early/middle/late phase schedule inhabits `Trace`, or that a
reframe has the claimed recursive-child list or fixed-tape cost.
-/

namespace FramedXor

open DirtyWrapper

/-- A bijection with both inverse laws, without a finiteness assumption. -/
structure Gauge (A : Type) where
  forward : A → A
  inverse : A → A
  inverse_forward : ∀ a, inverse (forward a) = a
  forward_inverse : ∀ a, forward (inverse a) = a

def Gauge.identity (A : Type) : Gauge A :=
  ⟨id, id, fun _ => rfl, fun _ => rfl⟩

abbrev Assignment (R A : Type) := R → Gauge A

def decode {R A : Type} (gauges : Assignment R A) (physical : Rows R A) : Rows R A :=
  fun r a => physical r ((gauges r).forward a)

def encode {R A : Type} (gauges : Assignment R A) (logical : Rows R A) : Rows R A :=
  fun r a => logical r ((gauges r).inverse a)

theorem decode_encode {R A : Type} (gauges : Assignment R A) (logical : Rows R A) :
    decode gauges (encode gauges logical) = logical := by
  funext r a
  exact congrArg (logical r) ((gauges r).inverse_forward a)

theorem encode_decode {R A : Type} (gauges : Assignment R A) (physical : Rows R A) :
    encode gauges (decode gauges physical) = physical := by
  funext r a
  exact congrArg (physical r) ((gauges r).forward_inverse a)

def replaceGauge {R A : Type} [DecidableEq R]
    (gauges : Assignment R A) (role : R) (new : Gauge A) : Assignment R A :=
  fun r => if r = role then new else gauges r

/-- Literal physical transport. Only the named row is permuted. -/
def reframe {R A : Type} [DecidableEq R] (gauges : Assignment R A)
    (role : R) (new : Gauge A) (physical : Rows R A) : Rows R A :=
  fun r a => if r = role then
    physical r ((gauges role).forward (new.inverse a)) else physical r a

theorem decode_reframe {R A : Type} [DecidableEq R]
    (gauges : Assignment R A) (role : R) (new : Gauge A) (physical : Rows R A) :
    decode (replaceGauge gauges role new) (reframe gauges role new physical) =
      decode gauges physical := by
  funext r a
  by_cases hr : r = role
  · subst r
    simp [decode, replaceGauge, reframe, new.inverse_forward]
  · simp [decode, replaceGauge, reframe, hr]

theorem reframe_composition {R A : Type} [DecidableEq R]
    (gauges : Assignment R A) (role : R) (middle last : Gauge A) (physical : Rows R A) :
    reframe (replaceGauge gauges role middle) role last (reframe gauges role middle physical) =
      reframe gauges role last physical := by
  funext r a
  by_cases hr : r = role
  · subst r
    simp [reframe, replaceGauge, middle.inverse_forward]
  · simp [reframe, hr]

theorem reframe_inverse {R A : Type} [DecidableEq R]
    (gauges : Assignment R A) (role : R) (new : Gauge A) (physical : Rows R A) :
    reframe (replaceGauge gauges role new) role (gauges role)
      (reframe gauges role new physical) = physical := by
  rw [reframe_composition]
  funext r a
  by_cases hr : r = role
  · subst r
    simp [reframe, (gauges role).forward_inverse]
  · simp [reframe, hr]

theorem decode_xor {R A : Type} [DecidableEq R]
    (gauges : Assignment R A) (gate : Gate R)
    (common : gauges gate.dst = gauges gate.src) (physical : Rows R A) :
    decode gauges (applyRowGate gate physical) = applyRowGate gate (decode gauges physical) := by
  funext r a
  by_cases hr : r = gate.dst
  · subst r
    simp [decode, applyRowGate, common]
  · simp [decode, applyRowGate, hr]

/-- The endpoint assignment is indexed in the type, so stale-frame XORs cannot
be inserted without a proof of equality of the current incident gauges. -/
inductive Step {R A : Type} [DecidableEq R] (gauges : Assignment R A) :
    Assignment R A → Type where
  | transport (role : R) (new : Gauge A) : Step gauges (replaceGauge gauges role new)
  | xor (gate : Gate R) (common : gauges gate.dst = gauges gate.src) : Step gauges gauges

inductive Trace {R A : Type} [DecidableEq R] : Assignment R A → Assignment R A → Type where
  | done (gauges : Assignment R A) : Trace gauges gauges
  | cons {first middle last : Assignment R A}
      (step : Step first middle) (rest : Trace middle last) : Trace first last

def executeStep {R A : Type} [DecidableEq R] {first last : Assignment R A} :
    Step first last → Rows R A → Rows R A
  | .transport role new, physical => reframe first role new physical
  | .xor gate _, physical => applyRowGate gate physical

def execute {R A : Type} [DecidableEq R] {first last : Assignment R A} :
    Trace first last → Rows R A → Rows R A
  | .done _, physical => physical
  | .cons step rest, physical => execute rest (executeStep step physical)

def scalarWord {R A : Type} [DecidableEq R] {first last : Assignment R A} :
    Trace first last → List (Gate R)
  | .done _ => []
  | .cons (.transport _ _) rest => scalarWord rest
  | .cons (.xor gate _) rest => gate :: scalarWord rest

/-- Main refinement theorem. Reframes erase to the identity; every remaining
literal XOR acts at one logical address, for arbitrary original dirty state. -/
theorem decoded_execution {R A : Type} [DecidableEq R]
    {first last : Assignment R A} (trace : Trace first last) (physical : Rows R A) :
    decode last (execute trace physical) =
      runRows (scalarWord trace) (decode first physical) := by
  induction trace generalizing physical with
  | done gauges => rfl
  | @cons first middle last step rest ih =>
    cases step with
    | transport role new =>
      simp only [execute, executeStep, scalarWord]
      rw [ih, decode_reframe]
    | xor gate common =>
      simp only [execute, executeStep, scalarWord, runRows]
      rw [ih, decode_xor first gate common]

/-- Equivalent encoded form, making both endpoint gauges explicit. -/
theorem encoded_execution {R A : Type} [DecidableEq R]
    {first last : Assignment R A} (trace : Trace first last) (logical : Rows R A) :
    execute trace (encode first logical) =
      encode last (runRows (scalarWord trace) logical) := by
  have result := decoded_execution trace (encode first logical)
  rw [decode_encode] at result
  have encoded := congrArg (encode last) result
  simpa only [encode_decode] using encoded

theorem physical_execution {R A : Type} [DecidableEq R]
    {first last : Assignment R A} (trace : Trace first last) (physical : Rows R A) :
    execute trace physical = encode last
      (runRows (scalarWord trace) (decode first physical)) := by
  simpa only [encode_decode] using encoded_execution trace (decode first physical)

/-- `destination` maps an input role to its output role. `addressMap` is a
PUSHFORWARD on physical addresses. Undoing the role permutation therefore
leaves a pullback by `addressMap.inverse` on row payloads. Bijectivity of the
role map is only needed by the outer split/merge theorem, not by this equality.
-/
theorem terminal_role_transport {R A : Type} [DecidableEq R]
    {first last : Assignment R A} (trace : Trace first last)
    (destination : R → R) (addressMap : Gauge A)
    (scalar_roles : ∀ (logical : Rows R A) (role : R) (address : A),
      runRows (scalarWord trace) logical (destination role) address = logical role address)
    (terminal_frames : ∀ role address,
      (last (destination role)).forward address = addressMap.forward ((first role).forward address))
    (physical : Rows R A) (role : R) (address : A) :
    execute trace physical (destination role) address =
      physical role (addressMap.inverse address) := by
  rw [physical_execution]
  simp only [encode, scalar_roles, decode]
  have frame := terminal_frames role ((last (destination role)).inverse address)
  rw [(last (destination role)).forward_inverse] at frame
  have pulled := congrArg addressMap.inverse frame
  rw [addressMap.inverse_forward] at pulled
  rw [← pulled]

def identityAssignment (R A : Type) : Assignment R A := fun _ => Gauge.identity A

/-- If both endpoint gauges are restored to identity, the literal physical
payload equals the scalar-word payload, without a zero-state assumption. -/
theorem restored_execution {R A : Type} [DecidableEq R]
    (trace : Trace (identityAssignment R A) (identityAssignment R A)) (physical : Rows R A) :
    execute trace physical = runRows (scalarWord trace) physical := by
  exact decoded_execution trace physical

/-- The result also agrees with the previously formalized scalar interpreter
at every address, closing the row-word/scalar-word correspondence. -/
theorem restored_addresswise {R A : Type} [DecidableEq R]
    (trace : Trace (identityAssignment R A) (identityAssignment R A))
    (physical : Rows R A) (address : A) :
    (fun role => execute trace physical role address) =
      run (scalarWord trace) (fun role => physical role address) := by
  rw [restored_execution]
  exact word_addresswise (scalarWord trace) physical address

/-! Source injection and scatter are ordinary typed XORs on disjoint banks. -/

inductive Bank (X D Z : Type) where
  | source (x : X)
  | auxiliary (d : D)
  | target (z : Z)
  deriving DecidableEq

def injectionGate {X D Z : Type} (x : X) (d : D) : Gate (Bank X D Z) :=
  ⟨.source x, .auxiliary d, by intro impossible; cases impossible⟩

def scatterGate {X D Z : Type} (d : D) (z : Z) : Gate (Bank X D Z) :=
  ⟨.auxiliary d, .target z, by intro impossible; cases impossible⟩

theorem decoded_injection {X D Z A : Type}
    [DecidableEq X] [DecidableEq D] [DecidableEq Z]
    (gauges : Assignment (Bank X D Z) A) (x : X) (d : D)
    (common : gauges (.auxiliary d) = gauges (.source x))
    (physical : Rows (Bank X D Z) A) :
    decode gauges (applyRowGate (injectionGate x d) physical) =
      applyRowGate (injectionGate x d) (decode gauges physical) :=
  decode_xor gauges (injectionGate x d) common physical

theorem decoded_scatter {X D Z A : Type}
    [DecidableEq X] [DecidableEq D] [DecidableEq Z]
    (gauges : Assignment (Bank X D Z) A) (d : D) (z : Z)
    (common : gauges (.target z) = gauges (.auxiliary d))
    (physical : Rows (Bank X D Z) A) :
    decode gauges (applyRowGate (scatterGate d z) physical) =
      applyRowGate (scatterGate d z) (decode gauges physical) :=
  decode_xor gauges (scatterGate d z) common physical

/-- Auxiliary-to-target scatter reads commute, even when targets coincide.
This permits center-first or target-grouped dispatch without dropping or
deduplicating literal incidences. Mixer XORs have no such blanket permission.
-/
theorem scatter_gates_commute {X D Z A : Type}
    [DecidableEq X] [DecidableEq D] [DecidableEq Z]
    (d₁ d₂ : D) (z₁ z₂ : Z) (physical : Rows (Bank X D Z) A) :
    applyRowGate (scatterGate d₁ z₁) (applyRowGate (scatterGate d₂ z₂) physical) =
      applyRowGate (scatterGate d₂ z₂) (applyRowGate (scatterGate d₁ z₁) physical) := by
  funext role address
  cases role with
  | source x => rfl
  | auxiliary d => rfl
  | target z =>
    by_cases first : z = z₁ <;> by_cases second : z = z₂
    · subst z₁; subst z₂
      simp [applyRowGate, scatterGate, Bool.xor_right_comm]
      cases physical (.auxiliary d₁) address <;> cases physical (.auxiliary d₂) address <;> decide
    · subst z₁
      simp [applyRowGate, scatterGate, second]
    · subst z₂
      simp [applyRowGate, scatterGate, first]
    · simp [applyRowGate, scatterGate, first, second]

theorem scatter_permutation {X D Z A : Type}
    [DecidableEq X] [DecidableEq D] [DecidableEq Z]
    (first last : List (D × Z)) (permutation : first.Perm last)
    (physical : Rows (Bank X D Z) A) :
    runRows (first.map (fun pair => scatterGate (X := X) pair.1 pair.2)) physical =
      runRows (last.map (fun pair => scatterGate (X := X) pair.1 pair.2)) physical := by
  induction permutation generalizing physical with
  | nil => rfl
  | cons pair _ ih =>
    simp only [List.map_cons, runRows]
    exact ih (applyRowGate (scatterGate pair.1 pair.2) physical)
  | swap a b rest =>
    simp only [List.map_cons, runRows]
    rw [scatter_gates_commute]
  | trans _ _ ih₁ ih₂ => exact (ih₁ physical).trans (ih₂ physical)

/-! A copied-center dispatch uses a NEW blank row. `some r` denotes an
arbitrary existing role; `none` alone is fresh and may later be discarded.
There is no overwrite, clearing or zero assumption on any existing role. -/

def allocateFresh {R A : Type} (physical : Rows R A) : Rows (Option R) A
  | none, _ => false
  | some r, a => physical r a

def restrictOriginal {R A : Type} (physical : Rows (Option R) A) : Rows R A :=
  fun r a => physical (some r) a

def extendGauge {R A : Type} (gauges : Assignment R A) (fresh : Gauge A) :
    Assignment (Option R) A
  | none => fresh
  | some r => gauges r

def cloneGate {R : Type} (source : R) : Gate (Option R) :=
  ⟨some source, none, by intro impossible; cases impossible⟩

def readFreshGate {R : Type} (target : R) : Gate (Option R) :=
  ⟨none, some target, by intro impossible; cases impossible⟩

/-- First copy at the source gauge, then transport only the fresh copy, then
read it at the target's current gauge. Existing gauges remain untouched. -/
def copiedReadTrace {R A : Type} [DecidableEq R]
    (gauges : Assignment R A) (gate : Gate R) :
    Trace (extendGauge gauges (gauges gate.src))
      (replaceGauge (extendGauge gauges (gauges gate.src)) none (gauges gate.dst)) :=
  .cons (.xor (cloneGate gate.src) rfl)
    (.cons (.transport none (gauges gate.dst))
      (.cons (.xor (readFreshGate gate.dst) (by
        simp [replaceGauge, extendGauge, readFreshGate])) (.done _)))

theorem decode_allocateFresh {R A : Type}
    (gauges : Assignment R A) (fresh : Gauge A) (physical : Rows R A) :
    decode (extendGauge gauges fresh) (allocateFresh physical) =
      allocateFresh (decode gauges physical) := by
  funext r a
  cases r <;> rfl

theorem restrict_decode_transportFresh {R A : Type} [DecidableEq R]
    (gauges : Assignment R A) (old new : Gauge A) (physical : Rows (Option R) A) :
    restrictOriginal (decode (replaceGauge (extendGauge gauges old) none new) physical) =
      decode gauges (restrictOriginal physical) := by
  funext r a
  simp [restrictOriginal, decode, replaceGauge, extendGauge]

theorem fresh_scalar_read {R A : Type} [DecidableEq R]
    (gate : Gate R) (logical : Rows R A) :
    restrictOriginal (runRows [cloneGate gate.src, readFreshGate gate.dst]
      (allocateFresh logical)) = applyRowGate gate logical := by
  funext r a
  by_cases hr : r = gate.dst
  · subst r
    simp [restrictOriginal, runRows, applyRowGate, cloneGate, readFreshGate, allocateFresh]
  · simp [restrictOriginal, runRows, applyRowGate, cloneGate, readFreshGate, allocateFresh, hr]

/-- A complete copy/transport/read/drop dispatch realizes the logical XOR even
when the original source and target gauges differ. Only the fresh copy is
transported, and every original payload may begin arbitrary and dirty. -/
theorem copied_read_correct {R A : Type} [DecidableEq R]
    (gauges : Assignment R A) (gate : Gate R) (physical : Rows R A) :
    decode gauges (restrictOriginal (execute (copiedReadTrace gauges gate)
      (allocateFresh physical))) = applyRowGate gate (decode gauges physical) := by
  have result := congrArg restrictOriginal
    (decoded_execution (copiedReadTrace gauges gate) (allocateFresh physical))
  rw [restrict_decode_transportFresh, decode_allocateFresh] at result
  simpa only [copiedReadTrace, scalarWord, fresh_scalar_read] using result

/-- The fresh temporary may be dropped after its read; the source and every
other original role keep their decoded payload. This is not a license to drop
or reset a dirty original auxiliary row. -/
theorem copied_read_preserves_other {R A : Type} [DecidableEq R]
    (gauges : Assignment R A) (gate : Gate R) (physical : Rows R A)
    (role : R) (not_target : role ≠ gate.dst) :
    (decode gauges (restrictOriginal (execute (copiedReadTrace gauges gate)
      (allocateFresh physical)))) role = decode gauges physical role := by
  rw [copied_read_correct]
  funext a
  simp [applyRowGate, not_target]

/-! The real retained-center schedule transports ONE temporary and uses it
for every scatter read. The following fanout specialization does not charge
or create a separate copy per destination. -/

def withFresh {R A : Type} (value : A → Bool) (logical : Rows R A) : Rows (Option R) A
  | none, a => value a
  | some r, a => logical r a

def addFixed {R A : Type} [DecidableEq R]
    (target : R) (value : A → Bool) (logical : Rows R A) : Rows R A :=
  fun r a => if r = target then logical r a ^^ value a else logical r a

def scatterFixed {R A : Type} [DecidableEq R] : List R → (A → Bool) → Rows R A → Rows R A
  | [], _, logical => logical
  | target :: rest, value, logical => scatterFixed rest value (addFixed target value logical)

theorem clone_blank {R A : Type} [DecidableEq R] (source : R) (logical : Rows R A) :
    applyRowGate (cloneGate source) (allocateFresh logical) = withFresh (logical source) logical := by
  funext r a
  cases r <;> simp [applyRowGate, cloneGate, allocateFresh, withFresh]

theorem fresh_fixed_read {R A : Type} [DecidableEq R]
    (target : R) (value : A → Bool) (logical : Rows R A) :
    applyRowGate (readFreshGate target) (withFresh value logical) =
      withFresh value (addFixed target value logical) := by
  funext r a
  cases r with
  | none => simp [applyRowGate, readFreshGate, withFresh]
  | some r => simp [applyRowGate, readFreshGate, withFresh, addFixed]

theorem fresh_fixed_reads {R A : Type} [DecidableEq R]
    (targets : List R) (value : A → Bool) (logical : Rows R A) :
    runRows (targets.map readFreshGate) (withFresh value logical) =
      withFresh value (scatterFixed targets value logical) := by
  induction targets generalizing logical with
  | nil => rfl
  | cons target rest ih =>
    simp only [List.map_cons, runRows, fresh_fixed_read, scatterFixed]
    exact ih (addFixed target value logical)

def freshReadsTrace {R A : Type} [DecidableEq R] (gauges : Assignment (Option R) A) :
    (targets : List R) → (∀ target ∈ targets, gauges (some target) = gauges none) → Trace gauges gauges
  | [], _ => .done gauges
  | target :: rest, common =>
      .cons (.xor (readFreshGate target) (common target (by simp)))
        (freshReadsTrace gauges rest (fun r hr => common r (by simp [hr])))

theorem freshReads_word {R A : Type} [DecidableEq R] (gauges : Assignment (Option R) A)
    (targets : List R) (common : ∀ target ∈ targets, gauges (some target) = gauges none) :
    scalarWord (freshReadsTrace gauges targets common) = targets.map readFreshGate := by
  induction targets with
  | nil => rfl
  | cons target rest ih =>
    simp only [freshReadsTrace, scalarWord, List.map_cons]
    rw [ih]

def copiedFanoutTrace {R A : Type} [DecidableEq R]
    (gauges : Assignment R A) (source : R) (new : Gauge A) (targets : List R)
    (common : ∀ target ∈ targets, gauges target = new) :
    Trace (extendGauge gauges (gauges source))
      (replaceGauge (extendGauge gauges (gauges source)) none new) :=
  .cons (.xor (cloneGate source) rfl)
    (.cons (.transport none new)
      (freshReadsTrace _ targets (by
        intro target member
        simpa only [replaceGauge, extendGauge, reduceCtorEq, ↓reduceIte] using common target member)))

/-- A single complete blank copy, one transport and ALL its target reads have
exactly the expected scalar fanout. Discarding that fresh row is safe; existing
rows remain arbitrary throughout. Duplicate targets mean repeated XORs, not
set membership, so the literal incidence multiplicity is preserved. -/
theorem copied_fanout_correct {R A : Type} [DecidableEq R]
    (gauges : Assignment R A) (source : R) (new : Gauge A) (targets : List R)
    (common : ∀ target ∈ targets, gauges target = new) (physical : Rows R A) :
    decode gauges (restrictOriginal (execute (copiedFanoutTrace gauges source new targets common)
      (allocateFresh physical))) =
      scatterFixed targets (decode gauges physical source) (decode gauges physical) := by
  have result := congrArg restrictOriginal
    (decoded_execution (copiedFanoutTrace gauges source new targets common) (allocateFresh physical))
  rw [restrict_decode_transportFresh, decode_allocateFresh] at result
  simpa only [copiedFanoutTrace, scalarWord, freshReads_word, runRows, clone_blank,
    fresh_fixed_reads, restrictOriginal, withFresh] using result

theorem scatterFixed_preserves_other {R A : Type} [DecidableEq R]
    (targets : List R) (value : A → Bool) (logical : Rows R A) (role : R)
    (not_target : role ∉ targets) : scatterFixed targets value logical role = logical role := by
  induction targets generalizing logical with
  | nil => rfl
  | cons target rest ih =>
    have different : role ≠ target := by
      intro equal
      apply not_target
      simp [equal]
    have outside : role ∉ rest := by
      intro member
      apply not_target
      simp [member]
    simp only [scatterFixed]
    rw [ih (addFixed target value logical) outside]
    funext a
    simp [addFixed, different]

theorem copied_fanout_preserves_other {R A : Type} [DecidableEq R]
    (gauges : Assignment R A) (source : R) (new : Gauge A) (targets : List R)
    (common : ∀ target ∈ targets, gauges target = new) (physical : Rows R A)
    (role : R) (not_target : role ∉ targets) :
    restrictOriginal (execute (copiedFanoutTrace gauges source new targets common)
      (allocateFresh physical)) role = physical role := by
  have decoded := congrArg (fun rows => rows role) (copied_fanout_correct gauges source new targets common physical)
  dsimp only at decoded
  rw [scatterFixed_preserves_other targets _ _ role not_target] at decoded
  funext address
  have point := congrFun decoded ((gauges role).inverse address)
  simpa only [decode, (gauges role).forward_inverse] using point

/-! Adversarial necessity of the current-gauge equality hypothesis. -/

def boolFlip : Gauge Bool :=
  ⟨Bool.not, Bool.not, by intro b; cases b <;> rfl, by intro b; cases b <;> rfl⟩

def unequalGauges : Assignment Bool Bool :=
  fun role => if role then Gauge.identity Bool else boolFlip

def counterexampleRows : Rows Bool Bool := fun role address => if role then false else address

def counterexampleGate : Gate Bool := ⟨false, true, by decide⟩

theorem mismatched_gauge_counterexample :
    decode unequalGauges (applyRowGate counterexampleGate counterexampleRows) true false = false ∧
    applyRowGate counterexampleGate (decode unequalGauges counterexampleRows) true false = true := by
  decide

/-- Copying by XOR into an arbitrary dirty temporary would be incorrect. The
fresh-row initialization used above is a necessary, explicit boundary. -/
theorem dirty_temporary_counterexample :
    restrictOriginal (runRows [cloneGate false, readFreshGate true]
      (withFresh (fun (_ : Unit) => true) (fun (_ : Bool) (_ : Unit) => false))) true () = true := by
  decide

#print axioms decode_reframe
#print axioms reframe_composition
#print axioms reframe_inverse
#print axioms decode_xor
#print axioms decoded_execution
#print axioms encoded_execution
#print axioms terminal_role_transport
#print axioms restored_execution
#print axioms restored_addresswise
#print axioms decoded_injection
#print axioms decoded_scatter
#print axioms scatter_permutation
#print axioms copied_read_correct
#print axioms copied_read_preserves_other
#print axioms copied_fanout_correct
#print axioms copied_fanout_preserves_other
#print axioms mismatched_gauge_counterexample
#print axioms dirty_temporary_counterexample

end FramedXor
