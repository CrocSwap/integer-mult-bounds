import MultitapeToolkit.StackOriginSerializer

/-!
# Three-state simultaneous source-preserving copy of paired input words

Two source words have the same length and occupy literal compiler-stack cells
1 through n, with blank cell zero. Two destinations are globally blank. One
simultaneous pass copies both words; a second pass returns every head to zero.
The finite control contains no length, address, word or unbounded register.
-/
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
namespace MultitapeToolkit.Absolute.PairedInputCopy
open MultitapeToolkit MultitapeToolkit.Locality StackOriginSerializer Turing

inductive PairTape where
  | sourceA | sourceB | destA | destB
  deriving DecidableEq, Fintype
inductive Phase where
  | enter | scan | rewind
  deriving DecidableEq, Fintype

def program : Program PairTape (Option Bool) Phase where
  transition q r := match q with
    | .enter => some (.scan,fun k => (r k,.right))
    | .scan => match r .sourceA,r .sourceB with
      | some a,some b => some (.scan,fun k =>
        (match k with | .destA => some a | .destB => some b | _ => r k,.right))
      | none,none => some (.rewind,fun k => (r k,.left))
      | _,_ => none
    | .rewind => match r .sourceA,r .sourceB with
      | some _,some _ => some (.rewind,fun k => (r k,.left))
      | _,_ => none

/-- An explicit literal stack word, with its blank entrance at cell zero. -/
def word (bits : List Bool) (x : ℤ) : Option Bool :=
  if 1≤x then bits[(x-1).toNat]? else none

theorem word_eq_sourceStack (bits : List Bool) : word bits = sourceStack 0 bits := by
  funext x
  cases x with
  | ofNat n =>
    cases n with
    | zero => simp [word,sourceStack,absoluteCell,stackTape,Tape.nth]
    | succ n =>
      simp [word,sourceStack,absoluteCell,stackTape,Tape.nth,ListBlank.nth_mk,
        List.getI_eq_getElem?_getD,List.getElem?_map]
      change bits[n]? = (Option.map some bits[n]?).getD none
      cases bits[n]? <;> rfl
  | negSucc n =>
    simp [word,sourceStack,absoluteCell,stackTape,Tape.nth,ListBlank.nth_mk]
    rfl

/-- A proof-only wordPrefix description of the partially written destination. -/
def wordPrefix (bits : List Bool) (k : ℕ) (x : ℤ) : Option Bool :=
  if 1≤x ∧ (x-1).toNat<k then bits[(x-1).toNat]? else none

@[simp] theorem prefix_zero (bits : List Bool) : wordPrefix bits 0 = fun _ => none := by
  funext x; simp [wordPrefix]
@[simp] theorem prefix_length (bits : List Bool) : wordPrefix bits bits.length = word bits := by
  funext x
  by_cases hx : 1≤x
  · by_cases hj : (x-1).toNat<bits.length
    · simp only [wordPrefix,word,hx,hj,true_and,ite_true]
    · have hn : bits[(x-1).toNat]?=none := List.getElem?_eq_none_iff.mpr (by omega)
      simp only [wordPrefix,word,hx,hj,true_and,ite_false,ite_true,hn]
  · simp [wordPrefix,word,hx]

private theorem prefix_write (bits : List Bool) (k : ℕ) (b : Bool)
    (hb : bits[k]?=some b) :
    wordPrefix bits (k+1) = fun x => if x=(k : ℤ)+1 then some b else wordPrefix bits k x := by
  funext x
  by_cases hx : x=(k : ℤ)+1
  · subst x; simp [wordPrefix,hb]
  · by_cases hpos : 1≤x
    · have hnat : (x-1).toNat≠k := by omega
      have hiff : (x-1).toNat<k+1 ↔ (x-1).toNat<k := by omega
      simp only [wordPrefix,hx,hpos,true_and,ite_false,hiff]
    · simp [wordPrefix,hx,hpos]

def input (as bs : List Bool) : MultitapeToolkit.Absolute.Config PairTape (Option Bool) Phase :=
  ⟨.enter,fun _ => 0,fun k => match k with
    | .sourceA => sourceStack 0 as | .sourceB => sourceStack 0 bs
    | _ => fun _ => none⟩

def output (as bs : List Bool) : MultitapeToolkit.Absolute.Config PairTape (Option Bool) Phase :=
  ⟨.rewind,fun _ => 0,fun k => match k with
    | .sourceA | .destA => sourceStack 0 as
    | .sourceB | .destB => sourceStack 0 bs⟩

def scanCfg (as bs : List Bool) (k : ℕ) : MultitapeToolkit.Absolute.Config PairTape (Option Bool) Phase :=
  ⟨.scan,fun _ => (k : ℤ)+1,fun i => match i with
    | .sourceA => word as | .sourceB => word bs
    | .destA => wordPrefix as k | .destB => wordPrefix bs k⟩

def rewindCfg (as bs : List Bool) (k : ℕ) : MultitapeToolkit.Absolute.Config PairTape (Option Bool) Phase :=
  ⟨.rewind,fun _ => k,fun i => match i with
    | .sourceA | .destA => word as | .sourceB | .destB => word bs⟩

private theorem scan_step (as bs : List Bool) (k : ℕ) (a b : Bool)
    (ha : as[k]?=some a) (hb : bs[k]?=some b) :
    MultitapeToolkit.Absolute.step program (scanCfg as bs k) = some (scanCfg as bs (k+1)) := by
  have hsa : word as ((k : ℤ)+1)=some a := by simpa [word] using ha
  have hsb : word bs ((k : ℤ)+1)=some b := by simpa [word] using hb
  simp only [MultitapeToolkit.Absolute.step,scanCfg,program,hsa,hsb,Option.map_some]
  congr 1
  apply MultitapeToolkit.Absolute.Config.ext
  · rfl
  · funext i; simp [moveOffset]
  · funext i x
    cases i with
    | sourceA => by_cases hx : x=(k : ℤ)+1 <;> simp [hx,hsa]
    | sourceB => by_cases hx : x=(k : ℤ)+1 <;> simp [hx,hsb]
    | destA => exact (congrFun (prefix_write as k a ha) x).symm
    | destB => exact (congrFun (prefix_write bs k b hb) x).symm

private theorem turn_step (as bs : List Bool) (hlen : as.length=bs.length) :
    MultitapeToolkit.Absolute.step program (scanCfg as bs as.length) =
      some (rewindCfg as bs as.length) := by
  have hsa : word as ((as.length : ℤ)+1)=none := by simp [word]
  have hsb : word bs ((as.length : ℤ)+1)=none := by simp [word,hlen]
  have hprefixbs : wordPrefix bs as.length = word bs := by rw [hlen,prefix_length]
  simp only [MultitapeToolkit.Absolute.step,scanCfg,program,hsa,hsb,Option.map_some]
  congr 1
  apply MultitapeToolkit.Absolute.Config.ext
  · rfl
  · funext i; simp [rewindCfg,moveOffset]
  · funext i x
    cases i <;> simp only [rewindCfg,prefix_length,hprefixbs]
    all_goals
      by_cases hx : x=(as.length : ℤ)+1
      · simp [hx,word,hlen]
      · simp [hx]

private theorem scan_run (as bs : List Bool) (hlen : as.length=bs.length) (k r : ℕ)
    (hkr : k+r=as.length) :
    MultitapeToolkit.Absolute.Runs program (r+1) (scanCfg as bs k) (rewindCfg as bs as.length) := by
  induction r generalizing k with
  | zero =>
    have hk : k=as.length := by omega
    subst k
    exact .cons (turn_step as bs hlen) (.refl _)
  | succ r ih =>
    have hka : k<as.length := by omega
    have hkb : k<bs.length := by omega
    have hs := scan_step as bs k as[k] bs[k]
      (List.getElem?_eq_getElem hka) (List.getElem?_eq_getElem hkb)
    simpa only [Nat.add_assoc] using MultitapeToolkit.Absolute.Runs.cons hs (ih (k+1) (by omega))

private theorem enter_step (as bs : List Bool) :
    MultitapeToolkit.Absolute.step program (input as bs)=some (scanCfg as bs 0) := by
  simp only [MultitapeToolkit.Absolute.step,input,program,Option.map_some]
  congr 1
  apply MultitapeToolkit.Absolute.Config.ext
  · rfl
  · funext i; simp [scanCfg,moveOffset]
  · funext i x
    cases i <;> simp [scanCfg,prefix_zero,word_eq_sourceStack]
    all_goals
      by_cases hx : x=0
      · simp [hx]
      · simp [hx]

private theorem rewind_step (as bs : List Bool) (m : ℕ) (hm : m<as.length)
    (hlen : as.length=bs.length) :
    MultitapeToolkit.Absolute.step program (rewindCfg as bs (m+1))=some (rewindCfg as bs m) := by
  have ha : word as ((m : ℤ)+1)=some as[m] := by simp [word,List.getElem?_eq_getElem hm]
  have hmb : m<bs.length := by omega
  have hb : word bs ((m : ℤ)+1)=some bs[m] := by simp [word,List.getElem?_eq_getElem hmb]
  simp only [MultitapeToolkit.Absolute.step,rewindCfg,program,Int.natCast_add,Int.natCast_one,ha,hb,Option.map_some]
  congr 1
  apply MultitapeToolkit.Absolute.Config.ext
  · rfl
  · funext i; simp [moveOffset]
  · funext i x
    by_cases hx : x=(m : ℤ)+1 <;> simp [hx]

private theorem rewind_run (as bs : List Bool) (hlen : as.length=bs.length) (m : ℕ)
    (hm : m≤as.length) :
    MultitapeToolkit.Absolute.Runs program m (rewindCfg as bs m) (rewindCfg as bs 0) := by
  induction m with
  | zero => exact .refl _
  | succ m ih => exact .cons (rewind_step as bs m (by omega) hlen) (ih (by omega))

/-- Actual paired copy, exact cost and genuine halt, including empty words. -/
theorem exact_correct (as bs : List Bool) (hlen : as.length=bs.length) :
    MultitapeToolkit.Absolute.Runs program (2*as.length+2) (input as bs) (output as bs) ∧
      MultitapeToolkit.Absolute.Halts program (output as bs) := by
  have hr := MultitapeToolkit.Absolute.Trace.runs_trans program
    (MultitapeToolkit.Absolute.Runs.cons (enter_step as bs) (scan_run as bs hlen 0 as.length (by omega)))
    (rewind_run as bs hlen as.length (by omega))
  have he : rewindCfg as bs 0=output as bs := by
    apply MultitapeToolkit.Absolute.Config.ext
    · rfl
    · rfl
    · funext i; cases i <;> simp [rewindCfg,output,word_eq_sourceStack]
  rw [he] at hr
  constructor
  · simpa only [show 2*as.length+2 = as.length+1+1+as.length by omega] using hr
  · simp [MultitapeToolkit.Absolute.Halts,MultitapeToolkit.Absolute.step,program,output,
      sourceStack,absoluteCell,stackTape,Tape.nth]

@[simp] theorem input_heads (as bs : List Bool) : (input as bs).head=fun _ => 0 := rfl
@[simp] theorem output_heads (as bs : List Bool) : (output as bs).head=fun _ => 0 := rfl
@[simp] theorem input_sourceA (as bs : List Bool) : (input as bs).cell .sourceA=sourceStack 0 as := rfl
@[simp] theorem input_sourceB (as bs : List Bool) : (input as bs).cell .sourceB=sourceStack 0 bs := rfl
@[simp] theorem input_destA (as bs : List Bool) : (input as bs).cell .destA=fun _ => none := rfl
@[simp] theorem input_destB (as bs : List Bool) : (input as bs).cell .destB=fun _ => none := rfl
@[simp] theorem output_sourceA (as bs : List Bool) : (output as bs).cell .sourceA=sourceStack 0 as := rfl
@[simp] theorem output_sourceB (as bs : List Bool) : (output as bs).cell .sourceB=sourceStack 0 bs := rfl
@[simp] theorem output_destA (as bs : List Bool) : (output as bs).cell .destA=sourceStack 0 as := rfl
@[simp] theorem output_destB (as bs : List Bool) : (output as bs).cell .destB=sourceStack 0 bs := rfl

theorem phase_card : Fintype.card Phase=3 := by decide
end MultitapeToolkit.Absolute.PairedInputCopy
