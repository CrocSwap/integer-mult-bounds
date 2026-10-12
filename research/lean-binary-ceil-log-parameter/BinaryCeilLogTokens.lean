import BinaryCounterCompactValue

/-! A five-state/two-tape lookahead tokenizer for the source parameter b.
The arbitrary-word physical theorem scans a canonical finite word into a
right-blank-ended zero-token tape, in exactly length+1 transitions. Numeric
identification is only for the already-normalized compact n record: token
length is ceil(log2 n), with zero and one mapped explicitly to zero tokens.
No binary-counter output, selected caller composition or full size setup is
claimed here. The accepted automatic-width counter is the later consumer. -/
namespace CurrentMain.BinaryCeilLogTokens
open FixedTapeMachine BinaryCounterCompactCopy
set_option Elab.async false

private theorem fin2 (i : Fin 2) : i=0 ∨ i=1 := by
  exact (show ∀ j : Fin 2, j=0 ∨ j=1 by decide) i

def fromRight (left : List Symbol) : List Bool → Tape
  | [] => ⟨left,.blank,[]⟩
  | b::rest => ⟨left,bitSymbol b,rest.map bitSymbol⟩
def endTape (left : List Symbol) : Tape := ⟨left,.blank,[]⟩
def tokenEnd (k : Nat) : Tape := endTape (List.replicate k .zero)
def buffered (seen b : Bool) : Fin 5 := if seen then 3 else if b then 2 else 1

def action (next : Fin 5) (inputMove : Move) (emit : Bool)
    (r : Fin 2 → Symbol) : Action 2 5 where
  state := next
  writes := fun i => if i=0 then r 0 else if emit then .zero else r 1
  moves := fun i => if i=0 then inputMove else if emit then .right else .stay

/-- State1 buffers zero with no earlier one;2 buffers the first one;3 has
an earlier one and no longer needs the buffer value. State4 halts. -/
def machine : Machine where
  tapes := 2
  states := 5
  initial := 0
  transition := fun s r =>
    match s.val with
    | 0 => match r (0 : Fin 2) with
      | .blank => some (action 4 .stay false r)
      | .zero => some (action 1 .right false r)
      | .one => some (action 2 .right false r)
    | 1 => match r (0 : Fin 2) with
      | .blank => some (action 4 .stay false r)
      | .zero => some (action 1 .right true r)
      | .one => some (action 2 .right true r)
    | 2 => match r (0 : Fin 2) with
      | .blank => some (action 4 .stay false r)
      | .zero | .one => some (action 3 .right true r)
    | 3 => match r (0 : Fin 2) with
      | .blank => some (action 4 .stay true r)
      | .zero | .one => some (action 3 .right true r)
    | _ => none

def configuration (s : Fin 5) (input output : Tape) : Configuration machine :=
  ⟨s,fun i => if i=(0 : Fin 2) then input else output⟩

def tokenCountAux (seen b : Bool) : List Bool → Nat
  | [] => if seen then 1 else 0
  | c::rest => 1+tokenCountAux (seen||b) c rest

def tokenCount : List Bool → Nat
  | [] => 0
  | b::rest => tokenCountAux false b rest

def tokens (word : List Bool) : List Bool := List.replicate (tokenCount word) false

def initialConfiguration (word : List Bool) : Configuration machine :=
  configuration 0 (Tape.ofWord word) Tape.blank

def finalConfiguration (word : List Bool) : Configuration machine :=
  configuration 4 (endTape (word.reverse.map bitSymbol)) (tokenEnd (tokenCount word))

/-- A natural-number version of ceiling log2, with the explicit zero extension.
Its least-power characterization is proved below from the installed core API. -/
def ceilLog2 (n : Nat) : Nat :=
  if n=0 then 0 else n.log2+(if n=2^n.log2 then 0 else 1)

private theorem step_of_transition (m : Machine) (c : Configuration m)
    (a : Action m.tapes m.states)
    (h : m.transition c.state (fun i => (c.tapes i).head) = some a) :
    step m c = some (Configuration.mk a.state
      (fun i => ((c.tapes i).write (a.writes i)).move (a.moves i))) := by
  unfold step
  rw [h]


private theorem step_action (s next : Fin 5) (input output : Tape)
    (inputMove : Move) (emit : Bool)
    (h : machine.transition s (fun i : Fin 2 => ((configuration s input output).tapes i).head)=
      some (action next inputMove emit
        (fun i : Fin 2 => ((configuration s input output).tapes i).head))) :
    step machine (configuration s input output)=some (configuration next
      (input.move inputMove)
      ((output.write (if emit then .zero else output.head)).move (if emit then .right else .stay))) := by
  refine (step_of_transition machine (configuration s input output) _ h).trans ?_
  dsimp only [action,configuration]
  apply congrArg some
  apply congrArg (@Configuration.mk machine next)
  funext i
  rcases fin2 i with rfl|rfl <;> cases emit <;> rfl

private theorem run_step (n : Nat) (c d : Configuration machine) (h : step machine c=some d) :
    run machine (n+1) c=run machine n d := by simp only [run,h]

private theorem start_bit (b : Bool) (rest : List Bool) :
    step machine (initialConfiguration (b::rest))=
      some (configuration (buffered false b) (fromRight [bitSymbol b] rest) (tokenEnd 0)) := by
  have h := step_action 0 (buffered false b) (Tape.ofWord (b::rest)) Tape.blank .right false
    (by cases b <;> rfl)
  cases rest <;> simpa only [initialConfiguration,Tape.ofWord,Tape.blank,fromRight,
    tokenEnd,endTape,List.replicate_zero,List.map_nil,List.map_cons,
    Tape.move,Tape.write,Bool.false_eq_true,if_false] using h

private theorem scan_bit (seen b c : Bool) (rest : List Bool) (left : List Symbol) (k : Nat) :
    step machine (configuration (buffered seen b) (fromRight left (c::rest)) (tokenEnd k))=
      some (configuration (buffered (seen||b) c) (fromRight (bitSymbol c::left) rest) (tokenEnd (k+1))) := by
  have h := step_action (buffered seen b) (buffered (seen||b) c)
    (fromRight left (c::rest)) (tokenEnd k) .right true
    (by cases seen <;> cases b <;> cases c <;> rfl)
  cases rest <;> simpa only [fromRight,tokenEnd,endTape,Tape.write,Tape.move,if_true,
    List.map_nil,List.map_cons,List.replicate_succ] using h

private theorem finish_step (seen b : Bool) (left : List Symbol) (k : Nat) :
    step machine (configuration (buffered seen b) (fromRight left []) (tokenEnd k))=
      some (configuration 4 (endTape left) (tokenEnd (k+(if seen then 1 else 0)))) := by
  have h := step_action (buffered seen b) 4 (fromRight left []) (tokenEnd k) .stay seen
    (by cases seen <;> cases b <;> rfl)
  cases seen <;> simpa only [fromRight,tokenEnd,endTape,Tape.write,Tape.move,
    Bool.false_eq_true,if_false,if_true,Nat.add_zero,List.replicate_succ] using h

private theorem scan_run (seen b : Bool) (rest : List Bool) (left : List Symbol) (k : Nat) :
    run machine (rest.length+1)
      (configuration (buffered seen b) (fromRight left rest) (tokenEnd k))=
      configuration 4 (endTape (rest.reverse.map bitSymbol++left))
        (tokenEnd (k+tokenCountAux seen b rest)) := by
  induction rest generalizing seen b left k with
  | nil =>
    simp only [List.length_nil,Nat.zero_add,run,finish_step,List.reverse_nil,List.map_nil,
      List.nil_append,tokenCountAux]
  | cons c rest ih =>
    rw [List.length_cons,run_step (rest.length+1) _ _ (scan_bit seen b c rest left k),ih]
    simp only [List.reverse_cons,List.map_append,List.map_cons,List.map_nil,List.append_assoc,
      List.singleton_append,tokenCountAux,Nat.add_assoc,Nat.add_left_comm,Nat.add_comm]

/-- Full physical endpoint for arbitrary words; no normalized-value premise is used. -/
theorem tokens_run_exact (word : List Bool) :
    run machine (word.length+1) (initialConfiguration word)=finalConfiguration word := by
  cases word with
  | nil =>
    have h := step_action 0 4 Tape.blank Tape.blank .stay false (by rfl)
    change run machine 1 (configuration 0 Tape.blank Tape.blank)=
      configuration 4 Tape.blank Tape.blank
    exact (run_step 0 _ _ h).trans rfl
  | cons b rest =>
    rw [List.length_cons,run_step (rest.length+1) _ _ (start_bit b rest),scan_run]
    simp only [finalConfiguration,List.reverse_cons,List.map_append,List.map_cons,List.map_nil,
      List.singleton_append,List.append_nil,Nat.zero_add,tokenCount]

private theorem aux_readback (seen b : Bool) (rest : List Bool) :
    tokenCountAux seen b rest = rest.length+
      (if seen || (b::rest).dropLast.any id then 1 else 0) := by
  induction rest generalizing seen b with
  | nil => simp only [tokenCountAux,List.length_nil,List.dropLast_singleton,List.any_nil,
      Bool.or_false,Nat.zero_add]
  | cons c rest ih =>
    simp only [tokenCountAux,ih,List.length_cons,List.dropLast_cons₂,List.any_cons,id_eq,
      Bool.or_assoc]
    omega

theorem token_count_readback (word : List Bool) :
    tokenCount word=word.dropLast.length+(if word.dropLast.any id then 1 else 0) := by
  cases word with
  | nil => rfl
  | cons b rest =>
    simpa only [tokenCount,List.length_dropLast_cons,Bool.false_or] using aux_readback false b rest

private theorem value_snoc (xs : List Bool) (b : Bool) :
    CarryTape.value (xs++[b]) =
      CarryTape.value xs + (if b then 2^xs.length else 0) := by
  induction xs with
  | nil => cases b <;> rfl
  | cons a xs ih =>
    simp only [List.cons_append,CarryTape.value,ih,List.length_cons,Nat.pow_succ]
    cases a <;> cases b <;>
      simp only [Bool.false_eq_true,if_false,if_true,Nat.add_zero,Nat.zero_add,
        Nat.mul_zero,Nat.mul_add] <;> omega

private theorem drop_head (xs : List Bool) :
    dropHighZeros xs=[] ∨ ∃ rest, dropHighZeros xs=true::rest := by
  induction xs with
  | nil => exact Or.inl rfl
  | cons b xs ih =>
    cases b with
    | false => exact ih
    | true => exact Or.inr ⟨xs,rfl⟩

private theorem compact_shape (bits : List Bool) :
    compact bits=[] ∨ ∃ q, compact bits=q++[true] := by
  rcases drop_head bits.reverse with h|⟨rest,h⟩
  · exact Or.inl (by simp only [compact,h,List.reverse_nil])
  · exact Or.inr ⟨rest.reverse,by simp only [compact,h,List.reverse_cons]⟩


private theorem any_false_iff_value_zero (q : List Bool) :
    q.any id=false ↔ CarryTape.value q=0 := by
  induction q with
  | nil => exact ⟨fun _ => rfl, fun _ => rfl⟩
  | cons b q ih =>
    cases b with
    | false =>
      simp only [List.any_cons,id_eq,Bool.false_or,CarryTape.value,Bool.false_eq_true,if_false,Nat.zero_add]
      constructor
      · intro h
        have hz := ih.1 h
        omega
      · intro h
        apply ih.2
        omega
    | true =>
      simp only [List.any_cons,id_eq,Bool.true_or,CarryTape.value,if_true]
      constructor
      · intro h
        cases h
      · intro h
        omega

/-- Only normalized input identifies the token length with the source parameter. -/
theorem token_count_ceil_log2 (bits : List Bool) :
    tokenCount (compact bits)=ceilLog2 (wordValue bits) := by
  rcases compact_shape bits with hz|⟨q,hq⟩
  · have hn := (BinaryCounterCompactValue.compact_eq_nil_iff bits).1 hz
    simp only [hz,tokenCount,hn,ceilLog2,if_pos rfl,if_true]
  · have v := BinaryCounterCompactValue.compact_value bits
    rw [hq,← BinaryCarryIncrement.value_binding,value_snoc] at v
    simp only [if_true] at v
    have pos := Nat.two_pow_pos q.length
    have hn : wordValue bits≠0 := by omega
    have hl := BinaryCounterCompactValue.compact_length_positive bits hn
    rw [hq] at hl
    simp only [List.length_append,List.length_cons,List.length_nil,Nat.zero_add] at hl
    have he : (wordValue bits).log2=q.length := by omega
    rw [token_count_readback,hq,List.dropLast_concat,ceilLog2,if_neg hn,he]
    cases ha : q.any id with
    | false =>
      have hq0 := (any_false_iff_value_zero q).1 ha
      have heq : wordValue bits=2^q.length := by omega
      simp only [Bool.false_eq_true,if_false,if_pos heq,Nat.add_zero]
    | true =>
      have hq0 : CarryTape.value q≠0 := by
        intro h
        have hx := (any_false_iff_value_zero q).2 h
        rw [ha] at hx
        cases hx
      have hne : wordValue bits≠2^q.length := by omega
      simp only [if_true,if_neg hne]

/-- Least natural exponent with value at most its power of two. For positive
values this is the source's ceiling-log2 convention, including powers of two. -/
theorem parameter_le_iff (bits : List Bool) (k : Nat) :
    tokenCount (compact bits)≤k ↔ wordValue bits≤2^k := by
  rw [token_count_ceil_log2]
  by_cases hz : wordValue bits=0
  · simp only [ceilLog2,hz,if_pos rfl]
    exact ⟨fun _ => Nat.zero_le _,fun _ => Nat.zero_le _⟩
  · rw [ceilLog2,if_neg hz]
    by_cases hp : wordValue bits=2^(wordValue bits).log2
    · rw [if_pos hp,Nat.add_zero,hp,Nat.log2_two_pow]
      exact (Nat.pow_le_pow_iff_right (by decide : 1<(2 : Nat))).symm
    · rw [if_neg hp]
      have low := Nat.log2_self_le hz
      have high := Nat.lt_log2_self (n:=wordValue bits)
      constructor
      · intro h
        have pow := Nat.pow_le_pow_right (by decide : 0<(2 : Nat)) h
        omega
      · intro h
        by_cases hk : k≤(wordValue bits).log2
        · have pow := Nat.pow_le_pow_right (by decide : 0<(2 : Nat)) hk
          omega
        · omega

/-- Physical scan plus the normalized parameter identification. -/
theorem normalized_tokens_run (bits : List Bool) :
    run machine ((compact bits).length+1) (initialConfiguration (compact bits))=
      finalConfiguration (compact bits) ∧
    (tokens (compact bits)).length=ceilLog2 (wordValue bits) := by
  refine ⟨tokens_run_exact _,?_⟩
  rw [tokens,List.length_replicate,token_count_ceil_log2]

theorem initial_word (word : List Bool) :
    (initialConfiguration word).tapes (0 : Fin 2)=Tape.ofWord word := by rfl
theorem initial_pristine (word : List Bool) :
    (initialConfiguration word).tapes (1 : Fin 2)=Tape.blank := by rfl
theorem final_halted (word : List Bool) : Halted machine (finalConfiguration word) := by rfl
theorem final_input (word : List Bool) :
    (finalConfiguration word).tapes (0 : Fin 2)=⟨word.reverse.map bitSymbol,.blank,[]⟩ := by rfl
theorem final_tokens (word : List Bool) :
    (finalConfiguration word).tapes (1 : Fin 2)=⟨List.replicate (tokenCount word) .zero,.blank,[]⟩ := by rfl
theorem empty_parameter : tokenCount (compact [])=0 := by rfl
theorem one_parameter : tokenCount (compact [true])=0 := by rfl

end CurrentMain.BinaryCeilLogTokens
#print axioms CurrentMain.BinaryCeilLogTokens.tokens_run_exact
#print axioms CurrentMain.BinaryCeilLogTokens.token_count_readback
#print axioms CurrentMain.BinaryCeilLogTokens.token_count_ceil_log2
#print axioms CurrentMain.BinaryCeilLogTokens.parameter_le_iff
#print axioms CurrentMain.BinaryCeilLogTokens.normalized_tokens_run
#print axioms CurrentMain.BinaryCeilLogTokens.initial_word
#print axioms CurrentMain.BinaryCeilLogTokens.initial_pristine
#print axioms CurrentMain.BinaryCeilLogTokens.final_halted
#print axioms CurrentMain.BinaryCeilLogTokens.final_input
#print axioms CurrentMain.BinaryCeilLogTokens.final_tokens
#print axioms CurrentMain.BinaryCeilLogTokens.empty_parameter
#print axioms CurrentMain.BinaryCeilLogTokens.one_parameter
