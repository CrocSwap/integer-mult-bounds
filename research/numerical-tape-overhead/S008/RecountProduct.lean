import S008.RecountHandoff
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith

/-! Exact cyclic recovery, product assembly and the physical final output trace. -/

namespace S008.Recount.Product

open OAI.Computability.IntegerMultiplication

private theorem folded_add (xs : List Bool) (a d : ℕ) :
    xs.foldl (fun v b => 2*v+b.toNat) (a+d) =
      xs.foldl (fun v b => 2*v+b.toNat) a + 2^xs.length*d := by
  induction xs generalizing a d with
  | nil => simp
  | cons b xs ih =>
    simp only [List.foldl_cons,List.length_cons,pow_succ]
    rw [show 2*(a+d)+b.toNat=2*a+b.toNat+2*d by ring,ih]
    ring

theorem bitValue_append (p s : List Bool) :
    bitValue (p++s) = bitValue p*2^s.length+bitValue s := by
  unfold bitValue
  rw [List.foldl_append]
  have h := folded_add s 0 (p.foldl (fun v b => 2*v+b.toNat) 0)
  simpa [Nat.mul_comm,Nat.add_comm] using h

theorem bitValue_lt (s : List Bool) : bitValue s < 2^s.length := by
  induction s with
  | nil => simp [bitValue]
  | cons b s ih =>
    have h := bitValue_append [b] s
    simp only [List.singleton_append] at h
    have hb : bitValue [b]≤1 := by cases b <;> decide
    have hm := Nat.mul_le_mul_right (2^s.length) hb
    simp only [one_mul] at hm
    simp only [List.length_cons,pow_succ]
    omega

/-- Exactly w most-significant-first bits. Division by two models consuming
    the low bit on the reversed little-endian limb bank. -/
def bits : ℕ → ℕ → List Bool
  | 0, _ => []
  | w+1, a => bits w (a/2) ++ [decide (a%2=1)]

@[simp] theorem bits_length (w a : ℕ) : (bits w a).length=w := by
  induction w generalizing a with
  | zero => rfl
  | succ w ih => simp [bits,ih]

theorem bits_value (w a : ℕ) (h : a<2^w) : bitValue (bits w a)=a := by
  induction w generalizing a with
  | zero =>
    have hz : a=0 := by simpa using h
    simp [bits,bitValue,hz]
  | succ w ih =>
    have hp : a/2<2^w := by
      rw [Nat.div_lt_iff_lt_mul (by decide)]
      simpa [pow_succ] using h
    rw [bits,bitValue_append,ih _ hp]
    have hm := Nat.mod_lt a (by decide : 0<2)
    have he := Nat.mod_add_div a 2
    by_cases v : a%2=1 <;> simp [v,bitValue] <;> omega

/-- Little-endian base-B polynomial evaluation, accepting unreduced coefficients. -/
def eval (B : ℕ) : List ℕ → ℕ
  | [] => 0
  | a::as => a+B*eval B as

def pack (B : ℕ) : ℕ → ℕ → List ℕ
  | 0, _ => []
  | h+1, a => a%B :: pack B h (a/B)

@[simp] theorem pack_length (B h a : ℕ) : (pack B h a).length=h := by
  induction h generalizing a with
  | zero => rfl
  | succ h ih => simp [pack,ih]

theorem pack_value (B h a : ℕ) (hB : 0<B) (ha : a<B^h) : eval B (pack B h a)=a := by
  induction h generalizing a with
  | zero =>
    have hz : a=0 := by simpa using ha
    simp [pack,eval,hz]
  | succ h ih =>
    have hd : a/B < B^h := by
      rw [Nat.div_lt_iff_lt_mul hB]
      simpa [pow_succ] using ha
    simpa [pack,eval,ih _ hd] using Nat.mod_add_div a B

def add : List ℕ → List ℕ → List ℕ
  | [], ys => ys
  | xs, [] => xs
  | x::xs, y::ys => (x+y) :: add xs ys

private theorem eval_add (B : ℕ) (xs ys : List ℕ) :
    eval B (add xs ys) = eval B xs + eval B ys := by
  induction xs generalizing ys with
  | nil => simp [eval,add]
  | cons a xs ih => cases ys with
    | nil => simp [eval,add]
    | cons b ys => simp only [add,eval,ih]; ring

private theorem eval_scale (B a : ℕ) (ys : List ℕ) :
    eval B (ys.map (a*·)) = a*eval B ys := by
  induction ys with
  | nil => simp [eval]
  | cons y ys ih => simp only [List.map_cons,eval,ih]; ring

/-- The ordinary linear convolution. Any additionally supplied cyclic slots are zero. -/
def convolution : List ℕ → List ℕ → List ℕ
  | [], _ => []
  | a::as, ys => add (ys.map (a*·)) (0 :: convolution as ys)

theorem convolution_value (B : ℕ) (xs ys : List ℕ) :
    eval B (convolution xs ys) = eval B xs * eval B ys := by
  induction xs with
  | nil => simp [convolution,eval]
  | cons a xs ih => rw [convolution,eval_add,eval_scale]; simp only [eval,ih]; ring

/-- Return all reduced limbs and the final carry after traversing these exact coefficients. -/
def normalize (B : ℕ) : List ℕ → ℕ → List ℕ × ℕ
  | [], carry => ([],carry)
  | a::as, carry =>
    let r := normalize B as ((a+carry)/B)
    ((a+carry)%B :: r.1, r.2)

@[simp] theorem normalize_length (B : ℕ) (xs : List ℕ) (carry : ℕ) :
    (normalize B xs carry).1.length = xs.length := by
  induction xs generalizing carry with
  | nil => rfl
  | cons a xs ih => simp [normalize,ih]

theorem normalized_lt (B : ℕ) (hB : 0<B) (xs : List ℕ) (carry : ℕ) :
    ∀ d ∈ (normalize B xs carry).1, d<B := by
  induction xs generalizing carry with
  | nil => simp [normalize]
  | cons a xs ih =>
    simp only [normalize, List.mem_cons, forall_eq_or_imp]
    exact ⟨Nat.mod_lt _ hB,ih _⟩

theorem normalize_value (B : ℕ) (xs : List ℕ) (carry : ℕ) :
    eval B xs+carry = eval B (normalize B xs carry).1 + B^xs.length*(normalize B xs carry).2 := by
  induction xs generalizing carry with
  | nil => simp [normalize,eval]
  | cons a xs ih =>
    simp only [normalize,eval,List.length_cons,pow_succ]
    have h := ih ((a+carry)/B)
    have hh := congrArg (B*·) h
    have hr := Nat.mod_add_div (a+carry) B
    nlinarith only [hh,hr]

def expand (w : ℕ) : List ℕ → List Bool
  | [] => []
  | a::as => expand w as ++ bits w a

@[simp] theorem expand_length (w : ℕ) (xs : List ℕ) : (expand w xs).length = w*xs.length := by
  induction xs with
  | nil => simp [expand]
  | cons a xs ih => simp [expand,ih,Nat.mul_succ]

theorem expand_value (w : ℕ) (xs : List ℕ) (h : ∀d∈xs,d<2^w) :
    bitValue (expand w xs) = eval (2^w) xs := by
  induction xs with
  | nil => rfl
  | cons a xs ih =>
    rw [expand,bitValue_append,ih (fun d hd => h d (by simp [hd])),bits_length,bits_value _ _ (h a (by simp)),eval]
    ring

theorem trim_value (xs : List Bool) (w : ℕ) (hlen : w≤xs.length) (h : bitValue xs<2^w) :
    bitValue (xs.drop (xs.length-w)) = bitValue xs := by
  have he := bitValue_append (xs.take (xs.length-w)) (xs.drop (xs.length-w))
  rw [List.take_append_drop] at he
  have hd : (xs.drop (xs.length-w)).length = w := by simp; omega
  rw [hd] at he
  have hz : bitValue (xs.take (xs.length-w))=0 := by
    by_contra! hn
    have hp := Nat.mul_le_mul_right (2^w) (show 1≤bitValue (xs.take (xs.length-w)) by omega)
    simp only [one_mul] at hp
    omega
  simpa [hz] using he.symm

private theorem product_lt (x y : List Bool) {n : ℕ} (hx : x.length=n) (hy : y.length=n) :
    bitValue x * bitValue y < 2^(2*n) := by
  have xx := bitValue_lt x
  have yy := bitValue_lt y
  rw [hx] at xx
  rw [hy] at yy
  have ha := Nat.mul_le_mul_left (bitValue x) yy.le
  have hb := Nat.mul_lt_mul_of_pos_right xx (by positivity : 0<2^n)
  rw [← pow_add, ← two_mul] at hb
  exact lt_of_le_of_lt ha hb

private theorem add_length (xs ys : List ℕ) : (add xs ys).length = max xs.length ys.length := by
  induction xs generalizing ys with
  | nil => simp [add]
  | cons a xs ih => cases ys with
    | nil => simp [add]
    | cons b ys => simp [add,ih]

private theorem conv_length (xs ys : List ℕ) : (convolution xs ys).length ≤ xs.length+ys.length := by
  induction xs with
  | nil => simp [convolution]
  | cons a xs ih =>
    rw [convolution,add_length]
    simp only [List.length_map,List.length_cons]
    omega

private theorem eval_pad (B : ℕ) (xs : List ℕ) (p : ℕ) :
    eval B (xs ++ List.replicate p 0) = eval B xs := by
  induction xs with
  | nil =>
    induction p with
    | zero => rfl
    | succ p ih => simpa [List.replicate_succ,eval] using congrArg (B*·) ih
  | cons a xs ih => simp [eval,ih]

def coefficients (w h S : ℕ) (x y : List Bool) : List ℕ :=
  let c := convolution (pack (2^w) h (bitValue x)) (pack (2^w) h (bitValue y))
  c ++ List.replicate (S-c.length) 0

theorem coefficients_length (w h S : ℕ) (x y : List Bool) (hslots : 2*h≤S) :
    (coefficients w h S x y).length=S := by
  have hh := conv_length (pack (2^w) h (bitValue x)) (pack (2^w) h (bitValue y))
  simp only [pack_length] at hh
  unfold coefficients
  simp only [List.length_append,List.length_replicate]
  omega

theorem coefficients_value (w h S n : ℕ) (x y : List Bool)
    (hx : x.length=n) (hy : y.length=n) (hwidth : n≤w*h) :
    eval (2^w) (coefficients w h S x y) = bitValue x*bitValue y := by
  have hp := Nat.pow_le_pow_right (by decide : 0<2) hwidth
  rw [pow_mul] at hp
  have xx := bitValue_lt x
  have yy := bitValue_lt y
  rw [hx] at xx
  rw [hy] at yy
  unfold coefficients
  rw [eval_pad,convolution_value,pack_value _ _ _ (by positivity) (xx.trans_le hp),
    pack_value _ _ _ (by positivity) (yy.trans_le hp)]

def assembled (w n : ℕ) (c : List ℕ) : List Bool :=
  let s := expand w (normalize (2^w) c 0).1
  s.drop (s.length-2*n)

private theorem assembly_from_value {w n P : ℕ} (c : List ℕ)
    (hc : eval (2^w) c=P) (hcap : 2*n≤w*c.length) (hv : P<2^(2*n)) :
    (normalize (2^w) c 0).2=0 ∧ (assembled w n c).length=2*n ∧ bitValue (assembled w n c)=P := by
  have hmax := Nat.pow_le_pow_right (by decide : 0<2) hcap
  rw [pow_mul (2:ℕ) w c.length] at hmax
  have hsmall := hv.trans_le hmax
  have hn := normalize_value (2^w) c 0
  rw [hc,Nat.add_zero] at hn
  have hnull : (normalize (2^w) c 0).2=0 := by
    by_contra! hbad
    have hm := Nat.mul_le_mul_left ((2^w)^c.length) (show 1≤(normalize (2^w) c 0).2 by omega)
    simp only [mul_one] at hm
    omega
  rw [hnull,Nat.mul_zero,Nat.add_zero] at hn
  let s := expand w (normalize (2^w) c 0).1
  have hlong : 2*n≤s.length := by simpa [s] using hcap
  have hvalue : bitValue s=P := by
    rw [show s = expand w (normalize (2^w) c 0).1 by rfl,
      expand_value w _ (normalized_lt (2^w) (by positivity) c 0)]
    exact hn.symm
  refine ⟨hnull,?_,?_⟩
  · change (s.drop (s.length-2*n)).length=2*n
    rw [List.length_drop]
    omega
  · change bitValue (s.drop (s.length-2*n))=P
    rw [trim_value _ _ hlong (hvalue.trans_lt hv),hvalue]

/-- Every recovered ordinary convolution yields the full specified 2n-bit product, including leading zeros. -/
theorem complete_assembly {w h S n : ℕ} (x y : List Bool)
    (hx : x.length=n) (hy : y.length=n) (hwidth : n≤w*h) (hslots : 2*h≤S) :
    let c := coefficients w h S x y
    (normalize (2^w) c 0).2=0 ∧ (assembled w n c).length=2*n ∧
      bitValue (assembled w n c)=bitValue x*bitValue y := by
  let c := coefficients w h S x y
  change (normalize (2^w) c 0).2=0 ∧ (assembled w n c).length=2*n ∧ _
  have hc : eval (2^w) c = bitValue x*bitValue y := coefficients_value w h S n x y hx hy hwidth
  have hs : c.length=S := coefficients_length w h S x y hslots
  have hcap : 2*n≤w*c.length := by
    rw [hs]
    have hmul := Nat.mul_le_mul_left w hslots
    nlinarith only [hmul,hwidth]
  exact assembly_from_value c hc hcap (product_lt x y hx hy)

/-- Deposit a single coefficient at ordinary index k in S coefficient slots. -/
def impulse : ℕ → ℕ → ℕ → List ℕ
  | 0, _, _ => []
  | S+1, 0, a => a::List.replicate S 0
  | S+1, k+1, a => 0::impulse S k a

private theorem impulse_length (S k a : ℕ) : (impulse S k a).length=S := by
  induction S generalizing k with
  | zero => rfl
  | succ S ih => cases k <;> simp [impulse,ih]

private theorem eval_zero (B n : ℕ) : eval B (List.replicate n 0)=0 := by
  simpa [eval] using eval_pad B [] n

private theorem eval_impulse (B S k a : ℕ) (hk : k<S) : eval B (impulse S k a) = B^k*a := by
  induction S generalizing k with
  | zero => omega
  | succ S ih => cases k with
    | zero => simp [impulse,eval,eval_zero]
    | succ k =>
      simp only [impulse,eval,zero_add,ih k (by omega),pow_succ]
      ring

/-- A mathematical cyclic convolution row. The residue operation specifies
    the actual circular coefficient position returned by a transform. -/
def cyclicRow (S : ℕ) (a : ℕ) : ℕ → List ℕ → List ℕ
  | _, [] => List.replicate S 0
  | i, b::bs => add (impulse S (i%S) (a*b)) (cyclicRow S a (i+1) bs)

private theorem row_length (S a i : ℕ) (ys : List ℕ) : (cyclicRow S a i ys).length=S := by
  induction ys generalizing i with
  | nil => simp [cyclicRow]
  | cons b ys ih => simp [cyclicRow,add_length,impulse_length,ih]

private theorem row_value (B S a i : ℕ) (ys : List ℕ) (h : i+ys.length≤S) :
    eval B (cyclicRow S a i ys)=B^i*a*eval B ys := by
  induction ys generalizing i with
  | nil => simp [cyclicRow,eval,eval_zero]
  | cons b ys ih =>
    have hpos : i<S := by simp only [List.length_cons] at h; omega
    have hrem : i+1+ys.length≤S := by simp only [List.length_cons] at h; omega
    rw [cyclicRow,eval_add,Nat.mod_eq_of_lt hpos,eval_impulse _ _ _ _ hpos,ih (i+1) hrem,eval,pow_succ]
    ring

def cyclicRows (S : ℕ) (ys : List ℕ) : ℕ → List ℕ → List ℕ
  | _, [] => List.replicate S 0
  | i, a::as => add (cyclicRow S a i ys) (cyclicRows S ys (i+1) as)

private theorem rows_length (S i : ℕ) (xs ys : List ℕ) : (cyclicRows S ys i xs).length=S := by
  induction xs generalizing i with
  | nil => simp [cyclicRows]
  | cons a xs ih => simp [cyclicRows,add_length,row_length,ih]

private theorem rows_value (B S i : ℕ) (xs ys : List ℕ) (h : i+xs.length+ys.length≤S) :
    eval B (cyclicRows S ys i xs)=B^i*eval B xs*eval B ys := by
  induction xs generalizing i with
  | nil => simp [cyclicRows,eval,eval_zero]
  | cons a xs ih =>
    simp only [List.length_cons] at h
    rw [cyclicRows,eval_add,row_value _ _ _ _ _ (by omega),ih (i+1) (by omega),eval,pow_succ]
    ring

/-- The S actual cyclic slots, indexed in ordinary integer rank after inverse CRT. -/
def cyclicCoefficients (w h S : ℕ) (x y : List Bool) : List ℕ :=
  cyclicRows S (pack (2^w) h (bitValue y)) 0 (pack (2^w) h (bitValue x))

theorem cyclic_assembly {w h S n : ℕ} (x y : List Bool) (hx : x.length=n) (hy : y.length=n)
    (hwidth : n≤w*h) (hslots : 2*h≤S) :
    let c := cyclicCoefficients w h S x y
    (normalize (2^w) c 0).2=0 ∧ (assembled w n c).length=2*n ∧
      bitValue (assembled w n c)=bitValue x*bitValue y := by
  let px := pack (2^w) h (bitValue x)
  let py := pack (2^w) h (bitValue y)
  have hl : 0+px.length+py.length≤S := by simpa [px,py,two_mul] using hslots
  have he := rows_value (2^w) S 0 px py hl
  have hp := Nat.pow_le_pow_right (by decide : 0<2) hwidth
  rw [pow_mul] at hp
  have xx := bitValue_lt x
  have yy := bitValue_lt y
  rw [hx] at xx
  rw [hy] at yy
  have he' : eval (2^w) (cyclicCoefficients w h S x y)=bitValue x*bitValue y := by
    simpa [cyclicCoefficients,px,py,pack_value _ _ _ (by positivity) (xx.trans_le hp),
        pack_value _ _ _ (by positivity) (yy.trans_le hp)] using he
  have hs : (cyclicCoefficients w h S x y).length=S := rows_length ..
  apply assembly_from_value _ he' _ (product_lt x y hx hy)
  rw [hs]
  have hm := Nat.mul_le_mul_left w hslots
  nlinarith only [hm,hwidth]

end S008.Recount.Product
namespace S008.Recount.RawWrite
open OAI.Computability.IntegerMultiplication
open OAI.Computability.NearSquareRoot
open S008.Recount S008.Recount.Letter

/-- Source heads may start anywhere on a dedicated result bank. The raw
    destination starts at absolute zero and its head advances once per bit. -/
def flush : TM.Rule Letter Unit Bool := fun _ scanned =>
  match scanned false with
  | .bit b => some ((),pick (bit b,.left) (bit b,.right))
  | _ => none

def config (s : Window) (t : TM.Tape Letter) : TM.Config Letter Unit Bool :=
  ⟨(),pick s.physical t⟩

private theorem emit_one (p : ℤ) (l r : List Letter) (b : Bool) (bs : List Bool) (dst : TM.Tape Letter) :
    TM.advance flush (config (backWindow p ((b::bs).map bit) l r) dst) =
    some (config (backWindow (p-1) (bs.map bit) l (bit b::r)) (dst.apply (bit b,.right))) := by
  have ht : ((backWindow p ((b::bs).map bit) l r).apply (bit b) .left) =
      backWindow (p-1) (bs.map bit) l (bit b::r) := by cases bs <;> rfl
  simp only [TM.advance,flush,config,pick,Window.read_physical,List.map_cons,backWindow,Window.atHead,
    List.headD_cons,Option.map_some]
  congr 1
  congr 1
  funext i
  cases i with
  | false => exact (Window.physical_apply (backWindow p ((b::bs).map bit) l r) (bit b) .left).symm.trans
              (congrArg Window.physical ht)
  | true => rfl

private theorem extend_contents (ps : List Letter) (b : Letter) (t : TM.Tape Letter)
    (h : TM.whole blank ps t) (hp : t.pos=(ps.length:ℤ)) :
    TM.whole blank (ps++[b]) (t.apply (b,.right)) := by
  change t.absolute = (TM.Tape.loaded blank ps).absolute at h
  funext i
  rw [TM.Tape.absolute_apply,hp,h]
  simp only [TM.Tape.absolute,TM.Tape.loaded,Int.sub_zero]
  cases i with
  | negSucc n => rfl
  | ofNat n =>
    change (if (n:ℤ)=(ps.length:ℤ) then b else ps[n]?.getD blank) = (ps++[b])[n]?.getD blank
    by_cases hl : n<ps.length
    · rw [List.getElem?_append_left hl,ite_eq_right (by omega)]
    · have hge := Nat.le_of_not_gt hl
      rw [List.getElem?_append_right hge]
      by_cases eq : n=ps.length
      · subst n
        simp
      · have he : ps[n]? = none := List.getElem?_eq_none_iff.mpr hge
        have hmore : 1≤n-ps.length := by omega
        have hnil : [b][n-ps.length]? = none := List.getElem?_eq_none_iff.mpr hmore
        simp [he,hnil,eq]

private theorem drain (s ps : List Bool) (p : ℤ) (pre exterior : List Letter) (dst : TM.Tape Letter)
    (hw : TM.whole blank (ps.map bit) dst) (hpos : dst.pos=(ps.length:ℤ)) :
    ∃ e, Trace (TM.advance flush) (config (backWindow p (s.map bit) pre exterior) dst) s.length e ∧
      TM.advance flush e=none ∧ TM.whole blank ((ps++s).map bit) (e.tape true) ∧
      (e.tape true).pos=((ps++s).length:ℤ) := by
  induction s generalizing ps p pre exterior dst with
  | nil =>
    refine ⟨_,.nil _,?_,?_,?_⟩
    · rfl
    · simpa [config,pick] using hw
    · simpa [config,pick] using hpos
  | cons b bs ih =>
    have hs := emit_one p pre exterior b bs dst
    have he := extend_contents (ps.map bit) (bit b) dst hw (by simpa using hpos)
    have he' : TM.whole blank ((ps++[b]).map bit) (dst.apply (bit b,.right)) := by
      simpa using he
    have hp : (dst.apply (bit b,.right)).pos=((ps++[b]).length:ℤ) := by
      simp [TM.Tape.apply,TM.Move.shift,hpos]
    obtain ⟨e,ht,hh,hm,hl⟩ := ih (ps++[b]) (p-1) pre (bit b::exterior) (dst.apply (bit b,.right)) he' hp
    refine ⟨e,?_,hh,?_,?_⟩
    · simpa [Nat.add_comm] using Trace.cons hs ht
    · simpa [List.append_assoc] using hm
    · simpa [List.append_assoc] using hl

def direction : Bool → ℤ := pick (-1) 1

private theorem step_positions {x y : TM.Config Letter Unit Bool}
    (h : TM.advance flush x=some y) (i : Bool) : (y.tape i).pos=(x.tape i).pos+direction i := by
  cases hr : (x.tape false).view 0 <;> simp [TM.advance,flush,hr] at h
  subst y
  cases i <;> rfl

private theorem positions {x y : TM.Config Letter Unit Bool} {u : ℕ}
    (h : Trace (TM.advance flush) x u y) (i : Bool) : (y.tape i).pos=(x.tape i).pos+direction i*u := by
  induction h with
  | nil => simp
  | cons hs _ ih =>
    rw [ih,step_positions hs i]
    push_cast
    ring

theorem visits (init : TM.Config Letter Unit Bool) (k : ℕ) : VisitsAtMost flush init k (2*(k+1)) := by
  let lo : Bool→ℤ := pick ((init.tape false).pos-k) (init.tape true).pos
  let hi : Bool→ℤ := pick (init.tape false).pos ((init.tape true).pos+k)
  have hf : ∀ u≤k, ∀ c, Trace (TM.advance flush) init u c →
      ∀ i, lo i ≤ (c.tape i).pos ∧ (c.tape i).pos ≤ hi i := by
    intro u hu c h i
    rw [positions h i]
    cases i <;> simp [lo,hi,direction,pick] <;> omega
  have hv := visitsAtMost_of_tape_fences lo hi hf
  have he (i : Bool) : (hi i+1-lo i).toNat=k+1 := by
    cases i <;> dsimp [hi,lo,pick] <;> omega
  simpa [he,Nat.two_mul] using hv

/-- The actual finite readout trace ends with blank absolute tape contents
    everywhere outside the specified MSB-first output. -/
theorem final_raw_trace (s : List Bool) (p : ℤ) (pre exterior : List Letter) :
    let init := config (backWindow p (s.map bit) pre exterior) (TM.Tape.loaded blank [])
    ∃ e, Trace (TM.advance flush) init s.length e ∧ TM.advance flush e=none ∧
      TM.whole blank (s.map bit) (e.tape true) ∧ (e.tape true).pos=(s.length:ℤ) ∧
      VisitsAtMost flush init s.length (2*(s.length+1)) := by
  obtain ⟨e,ht,hh,hm,hl⟩ := drain s [] p pre exterior (TM.Tape.loaded blank []) rfl rfl
  exact ⟨e,ht,hh,by simpa using hm,by simpa using hl,visits _ _⟩

end S008.Recount.RawWrite
namespace S008.Recount.Product

open OAI.Computability.IntegerMultiplication OAI.Computability.NearSquareRoot
open S008.Recount S008.Recount.Letter S008.Recount.RawWrite

noncomputable def recover (r : ℝ) : ℕ := (⌊r+1/2⌋).toNat

private theorem recover_one {a : ℕ} {r : ℝ} (h : |r-a| < 1/4) : recover r=a := by
  obtain ⟨hlo,hhi⟩ := abs_lt.mp h
  have hh : ⌊r+1/2⌋ = (a:ℤ) := by
    apply Int.floor_eq_iff.mpr
    push_cast
    constructor <;> linarith
  unfold recover
  rw [hh]
  rfl

theorem recover_all {r : List ℝ} {a : List ℕ}
    (h : List.Forall₂ (fun (x:ℝ) (c:ℕ) => |x-(c:ℝ)| < 1/4) r a) : r.map recover=a := by
  induction h with
  | nil => rfl
  | cons hc _ ih => simp [recover_one hc,ih]

/-- Starting with the coefficient error promised by the Fourier supplier,
    the arithmetic normalization and the literal final tape trace deliver
    the original source product contract, including the absolute blank exterior. -/
theorem recovered_source_product {w h S n : ℕ} (x y : List Bool) (r : List ℝ)
    (hx : x.length=n) (hy : y.length=n) (hwidth : n≤w*h) (hslots : 2*h≤S)
    (herr : List.Forall₂ (fun (a:ℝ) (c:ℕ) => |a-(c:ℝ)| < 1/4) r (cyclicCoefficients w h S x y))
    (p : ℤ) (low high : List Letter) :
    let z := assembled w n (r.map recover)
    let init := config (backWindow p (z.map bit) low high) (TM.Tape.loaded blank [])
    ∃ e, Trace (TM.advance flush) init (2*n) e ∧ TM.advance flush e=none ∧
      TM.whole blank (z.map bit) (e.tape true) ∧ z.length=2*n ∧
      bitValue z=bitValue x*bitValue y ∧ (e.tape true).pos=(2*n:ℕ) ∧
      VisitsAtMost flush init (2*n) (4*n+2) := by
  rw [recover_all herr]
  let z := assembled w n (cyclicCoefficients w h S x y)
  obtain ⟨_,hl,hv⟩ := cyclic_assembly x y hx hy hwidth hslots
  have len : z.length=2*n := hl
  obtain ⟨e,ht,hh,hw,hp,hvisited⟩ := final_raw_trace z p low high
  rw [len] at ht hp hvisited
  exact ⟨e,ht,hh,hw,hl,hv,hp,by convert hvisited using 1; omega⟩

end S008.Recount.Product
