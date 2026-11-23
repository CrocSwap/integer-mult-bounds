import Init

/-! Raw Boolean XOR semantics for an ordered multi-source gate. Frame metadata
is retained but has no scalar action here; physical frame transport is separate.
This small structural adapter reuses core Bool XOR laws. It does not interpret
COPY/ERASE or assert any source-specific operator or geometry. -/
namespace CurrentMain.BitXor
set_option Elab.async false

structure Gate (Reg : Type) where
  frame : Nat
  dst : Reg
  sources : List Reg

abbrev State (Reg : Type) := Reg → Bool
variable {Reg : Type} [DecidableEq Reg]

/-- One actual XOR ADD, preserving every other register. -/
def single (dst src : Reg) (s : State Reg) : State Reg :=
  fun r => if r = dst then s r ^^ s src else s r

/-- Operand order matches the source checker's `for src in srcs` loop. -/
def sourcesRun (dst : Reg) : List Reg → State Reg → State Reg
  | [], s => s
  | src :: rest, s => sourcesRun dst rest (single dst src s)

def step (g : Gate Reg) (s : State Reg) : State Reg :=
  sourcesRun g.dst g.sources s

theorem sourcesRun_untouched (dst : Reg) (rs : List Reg) :
    ∀ s r, r ≠ dst → sourcesRun dst rs s r = s r := by
  induction rs with
  | nil => intro s r hr; rfl
  | cons src rs ih =>
    intro s r hr
    change sourcesRun dst rs (single dst src s) r = s r
    rw [ih (single dst src s) r hr]
    simp [single, hr]

def run : List (Gate Reg) → State Reg → State Reg
  | [], s => s
  | g :: gs, s => run gs (step g s)

variable (target : Reg → Prop) [DecidablePred target]

def shift (s delta : State Reg) : State Reg :=
  fun r => if target r then s r ^^ delta r else s r

def eraseTargets (s : State Reg) : State Reg :=
  fun r => if target r then false else s r

theorem single_shift (dst src : Reg) (hsrc : ¬ target src)
    (s delta : State Reg) :
    single dst src (shift target s delta) =
      shift target (single dst src s) delta := by
  funext r
  by_cases hd : r = dst
  · subst r
    by_cases ht : target dst <;>
      simp [single, shift, ht, hsrc, Bool.xor_right_comm]
    exact Bool.xor_comm (delta dst) (s src)
  · by_cases ht : target r <;>
      simp [single, shift, hd, ht, hsrc, Bool.xor_right_comm]

theorem sourcesRun_shift (dst : Reg) (rs : List Reg) :
    (∀ r ∈ rs, ¬ target r) → ∀ s delta,
    sourcesRun dst rs (shift target s delta) =
      shift target (sourcesRun dst rs s) delta := by
  induction rs with
  | nil => intro h s delta; rfl
  | cons src rs ih =>
    intro h s delta
    have hs : ¬ target src := h src List.mem_cons_self
    have ht : ∀ r ∈ rs, ¬ target r := fun r hr => h r (List.mem_cons_of_mem src hr)
    change sourcesRun dst rs (single dst src (shift target s delta)) = _
    rw [single_shift target dst src hs s delta]
    exact ih ht (single dst src s) delta

theorem step_shift (g : Gate Reg) (h : ∀ r ∈ g.sources, ¬ target r)
    (s delta : State Reg) :
    step g (shift target s delta) = shift target (step g s) delta :=
  sourcesRun_shift target g.dst g.sources h s delta

theorem run_shift (gs : List (Gate Reg)) :
    (∀ g ∈ gs, ∀ r ∈ g.sources, ¬ target r) → ∀ s delta,
    run gs (shift target s delta) = shift target (run gs s) delta := by
  induction gs with
  | nil => intro h s delta; rfl
  | cons g gs ih =>
    intro h s delta
    change run gs (step g (shift target s delta)) =
      shift target (run gs (step g s)) delta
    rw [step_shift target g (h g List.mem_cons_self) s delta]
    exact ih (fun q hq => h q (List.mem_cons_of_mem g hq)) (step g s) delta

theorem run_off_target (gs : List (Gate Reg)) :
    (∀ g ∈ gs, target g.dst) → ∀ s r, ¬ target r → run gs s r = s r := by
  induction gs with
  | nil => intro h s r hr; rfl
  | cons g gs ih =>
    intro h s r hr
    have hne : r ≠ g.dst := by
      intro he
      apply hr
      simpa [he] using h g List.mem_cons_self
    change run gs (step g s) r = s r
    rw [ih (fun q hq => h q (List.mem_cons_of_mem g hq)) (step g s) r hr]
    exact sourcesRun_untouched g.dst g.sources s r hne

theorem erase_shift_self (s : State Reg) :
    shift target (eraseTargets target s) s = s := by
  funext r
  by_cases hr : target r <;> simp [shift, eraseTargets, hr]

theorem target_identity (gs : List (Gate Reg))
    (h : ∀ g ∈ gs, ∀ r ∈ g.sources, ¬ target r)
    (s : State Reg) (r : Reg) (hr : target r) :
    run gs s r = (s r ^^ run gs (eraseTargets target s) r) := by
  calc
    run gs s r = run gs (shift target (eraseTargets target s) s) r := by
      rw [erase_shift_self]
    _ = shift target (run gs (eraseTargets target s)) s r :=
      congrFun (run_shift target gs h (eraseTargets target s) s) r
    _ = (s r ^^ run gs (eraseTargets target s) r) := by
      simp [shift, hr, Bool.xor_comm]

theorem erased_eq_of_agree_off_target (s t : State Reg)
    (h : ∀ r, ¬ target r → s r = t r) :
    eraseTargets target s = eraseTargets target t := by
  funext r
  by_cases hr : target r
  · simp [eraseTargets, hr]
  · simp [eraseTargets, hr, h r hr]

end CurrentMain.BitXor
#print axioms CurrentMain.BitXor.run_shift
#print axioms CurrentMain.BitXor.run_off_target
#print axioms CurrentMain.BitXor.target_identity
#print axioms CurrentMain.BitXor.erased_eq_of_agree_off_target
