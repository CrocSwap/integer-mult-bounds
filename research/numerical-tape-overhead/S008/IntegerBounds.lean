import S008.CallLedger
import S008.RoleMask
import S008.LabelSchedule
import S008.Frontier

namespace S008.IntegerBounds

open S008.NumericalCutoff S008.Packing S008.Piecewise S008.Piecewise.LabelSchedule
open S008.OccupiedBank
open OAI.Computability.IntegerMultiplication OAI.Computability.NearSquareRoot

private theorem rounded_at {k : ℕ} (hk : 2≤k) :
    (activeLog k:ℝ) ≤ logTwo (k:ℝ)+2 := by
  let X := activeLog k
  have hX : 0<X := Nat.clog_pos (by decide : 1<2) (by omega : 1<k+2)
  have small : 2^(X-1)<k+2 := Nat.pow_pred_clog_lt_self (x:=k+2) (by decide : 1<2) (by omega)
  have hreal : (2:ℝ)^(X-1) ≤ 2*(k:ℝ) := by exact_mod_cast (by omega : 2^(X-1) ≤ 2*k)
  have kp : (0:ℝ)<k := by exact_mod_cast (show 0<k by omega)
  have h := logTwo_mono (pow_pos (by norm_num : (0:ℝ)<2) (X-1)) hreal
  rw [←Real.rpow_natCast,logTwo_two_rpow,Nat.cast_sub (by omega : 1≤X),Nat.cast_one] at h
  have logDouble : logTwo (2*(k:ℝ)) = 1+logTwo k := by
    unfold logTwo
    rw [Real.log_mul (by norm_num) kp.ne', add_div,div_self (ne_of_gt (Real.log_pos (by norm_num)))]
  rw [logDouble] at h
  change (X:ℝ) ≤ _
  linarith only [h]

/-- The rounding hypothesis in the sharp schedule follows from the actual packed
    address width, including both ceilings. -/
theorem rounded_width {n : ℕ} (hn : 2^48<n) :
    (activeLog (addressWidth n):ℝ) ≤ logTwo (logTwo n)+2 := by
  have hk := (physical_sizes hn).1
  have rounded := rounded_at (k:=addressWidth n) (le_trans (by decide : 2≤32) hk)
  have hnpos : (0:ℝ)<addressWidth n := by exact_mod_cast (lt_of_lt_of_le (by decide : 0<32) hk)
  exact rounded.trans (add_le_add_left (logTwo_mono hnpos (S008.InputClock.input_geometry hn).1) _)

noncomputable def sharpInvoice (n : ℕ) : ℝ :=
  let t := logTwo (logTwo n)
  (n:ℝ)*Real.sqrt (logTwo n)*(2:ℝ)^(182+4*logTwo (t+2)+
    envelope (fun j => Facets.scheduled measured29 (j:ℝ)) (activeLog (addressWidth n)))

private theorem sum_priced {α : Type} (xs : List α) (ticks : α → ℕ) (price : α → ℝ)
    (bound : ∀ c ∈ xs, (ticks c:ℝ) ≤ price c) :
    ((xs.map ticks).sum : ℝ) ≤ (xs.map price).sum := by
  induction xs with
  | nil => simp
  | cons c cs ih =>
    simp only [List.map_cons,List.sum_cons,Nat.cast_add]
    exact add_le_add (bound c (by simp)) (ih (fun k hk => bound k (List.mem_cons_of_mem _ hk)))

/-- Remaining physical input is a separated accounting of the actual outer work
    and true-width child transitions. Every transfer and both returns have proved
    duration, counted with multiplicity. -/
theorem from_occupied_calls {I Q : Type} {m : Child I Q} {entry : Q}
    {n : ℕ} (cutoff : (2:ℝ)^((2:ℝ)^(7519517465920988:ℝ)) ≤ n)
    (calls : List (Call I Q m entry)) (ordinary elapsed : ℕ) (ordinaryLimit movementLimit : ℝ)
    (partition : elapsed = ordinary+(calls.map Call.steps).sum)
    (scans : (ordinary+(calls.map Call.overhead).sum : ℕ) ≤ ordinaryLimit)
    (setup rate : Call I Q m entry → ℝ)
    (native : ∀ c ∈ calls, (c.ticks:ℝ) ≤ setup c+(rank c.select c.width:ℝ)*rate c)
    (movement : (calls.map (fun c => setup c+(rank c.select c.width:ℝ)*rate c)).sum ≤ movementLimit)
    (outer : ordinaryLimit+movementLimit ≤ sharpInvoice n) :
    (elapsed:ℝ) ≤ (n:ℝ)*(Real.log n)^(501/1000:ℝ) := by
  have e : (2:ℝ)^(6:ℝ) ≤ (2:ℝ)^(7519517465920988:ℝ) :=
    Real.rpow_le_rpow_of_exponent_le (by norm_num) (by norm_num)
  have big : (2:ℝ)^(48:ℝ) < (n:ℝ) := lt_of_lt_of_le
    (Real.rpow_lt_rpow_of_exponent_lt (by norm_num) ((show (48:ℝ)<(2:ℝ)^(6:ℝ) by norm_num).trans_le e)) cutoff
  have h48 : (2:ℝ)^(48:ℕ) < (n:ℝ) := by simpa only [←Real.rpow_natCast, Nat.cast_ofNat] using big
  have hn : 2^48<n := by exact_mod_cast h48
  apply schedule_natural_clock n elapsed (addressWidth n) cutoff (rounded_width hn)
  rw [partition,Call.total_steps,←Nat.add_assoc,Nat.cast_add]
  have childTimes := sum_priced calls Call.ticks _ native
  exact (add_le_add scans (childTimes.trans movement)).trans outer

/-- A legal role in the parent word, with its original leading prefixes. -/
structure Role where
  prefixes : ℕ
  roles : ℕ
  slot : ℕ
  payload : ℕ
  valid : slot < roles

def Role.marks (r : Role) := roleMarks r.prefixes r.roles r.slot r.payload

/-- Relate independent measurements of halting wrapper traces to the numerical
    clock. The selection comes from the actual role layout. The measured wrapper
    times need not be specified by the accountant: determinism identifies them. -/
theorem from_role_runs {I Q : Type} {m : Child I Q} {entry : Q} {n : ℕ}
    (cutoff : (2:ℝ)^((2:ℝ)^(7519517465920988:ℝ)) ≤ n)
    (calls : List (Call I Q m entry)) (role : Call I Q m entry → Role)
    (layout : ∀ c ∈ calls, c.width = (role c).marks.length ∧ c.select = marked (role c).marks)
    (duration : Call I Q m entry → ℕ)
    (observed : ∀ c ∈ calls, ∃ stop,
      Trace (TM.advance (called m entry))
        (initial c.width c.select c.bank c.before Q) (duration c) stop ∧
      TM.advance (called m entry) stop = none)
    (ordinary elapsed : ℕ) (ordinaryLimit movementLimit : ℝ)
    (partition : elapsed = ordinary+(calls.map duration).sum)
    (scans : (ordinary+(calls.map Call.overhead).sum : ℕ) ≤ ordinaryLimit)
    (setup rate : Call I Q m entry → ℝ)
    (native : ∀ c ∈ calls, (c.ticks:ℝ) ≤ setup c+((role c).prefixes*(role c).payload:ℕ)*rate c)
    (movement : (calls.map (fun c => setup c+((role c).prefixes*(role c).payload:ℕ)*rate c)).sum ≤ movementLimit)
    (outer : ordinaryLimit+movementLimit ≤ sharpInvoice n) :
    (elapsed:ℝ) ≤ (n:ℝ)*(Real.log n)^(501/1000:ℝ) := by
  have timed (c) (hc : c ∈ calls) : duration c = c.steps := by
    obtain ⟨stop, run, halt⟩ := observed c hc
    exact (halting_trace_unique run halt c.halting.1 c.halting.2).1
  have counts (c) (hc : c ∈ calls) : rank c.select c.width = (role c).prefixes*(role c).payload := by
    obtain ⟨w,s⟩ := layout c hc
    rw [w,s]
    exact (occupied_role _ _ _ _ (role c).valid).2
  apply from_occupied_calls cutoff calls ordinary elapsed ordinaryLimit movementLimit
    _ scans setup rate _ _ outer
  · rw [partition, List.map_congr_left timed]
  · intro c hc
    rw [counts c hc]
    exact native c hc
  · convert movement using 2
    apply List.map_congr_left
    intro c hc
    rw [counts c hc]

/-- The exact counted fast-program arenas fit the common cap using the sharper
    natural packing lemma (N*k ≤ 8*n). -/
theorem fast_space {n cells : ℕ} (hn : 2^48<n)
    (arenas : cells ≤ 453759460*(paddedSize n*addressWidth n)) : cells ≤ 2^32*n := by
  have h := (physical_sizes hn).2.2.2
  calc
    cells ≤ 453759460*(paddedSize n*addressWidth n) := arenas
    _ ≤ 453759460*(8*n) := Nat.mul_le_mul_left _ h
    _ ≤ 2^32*n := by rw [←Nat.mul_assoc]; exact Nat.mul_le_mul_right _ (by decide)

/-- An admissible j always exists. The executable checker takes the least such j. -/
theorem search_terminates (D : ℕ) : ∃ j : ℕ, 2≤j ∧ j*D+2≤2^j := by
  let b := Nat.clog 2 (2*D+4)
  have h := Nat.le_pow_clog (by decide : 1<2) (2*D+4)
  change 2*D+4 ≤ 2^b at h
  have hb : b ≤ 2*D+4 := Nat.clog_le_of_le_pow (Nat.lt_two_pow_self.le)
  have hb1 : 0<b := Nat.clog_pos (by decide : 1<2) (by omega)
  refine ⟨b+b,by omega,?_⟩
  rw [pow_add]
  calc
    (b+b)*D+2 ≤ (2*D+4)*(2*D+4) := by nlinarith [Nat.mul_le_mul_right D hb]
    _ ≤ 2^b*2^b := Nat.mul_le_mul h h

def scale (q : ℕ) := (60*q)^3
noncomputable def index (q : ℕ) := Nat.find (search_terminates (scale q))
noncomputable def sufficient (q : ℕ) := max 1572864480 (index q * scale q)

/-- Every integer q≥2, even when the outer smooth-clock floor exceeds jD. -/
theorem every_exponent (n cost : ℝ) (q : ℕ) (hq : 2≤q)
    (hn : (2:ℝ)^((2:ℝ)^((sufficient q:ℕ):ℝ)) ≤ n)
    (bill : let z := logTwo (logTwo n)
      cost ≤ n*Real.sqrt (logTwo n)*(2:ℝ)^(182+4*logTwo (z+2)+(479/8)*phi (z+2))) :
    cost ≤ n*(Real.log n)^((1/2:ℝ)+1/(q:ℝ)) := by
  let D := scale q
  let j := index q
  have spec : 2≤j ∧ j*D+2≤2^j := Nat.find_spec (search_terminates D)
  have hD : 0<D := by dsimp [D,scale]; positivity
  have positives : 0<j*D := Nat.mul_pos (by omega) hD
  have hj : j*D ≤ sufficient q := le_max_right _ _
  have hfloor : 1572864480 ≤ sufficient q := le_max_left _ _
  have hr : (D:ℝ)=((q:ℝ)*60)^3 := by unfold D scale; push_cast; ring
  have zfloor := (show (1572864480:ℝ) ≤ (sufficient q:ℝ) by exact_mod_cast hfloor).trans
    (length_gate n _ hn)
  apply S008.Frontier.natural_reciprocal n cost q ((j*D:ℕ):ℝ) j (by exact_mod_cast hq)
    (by exact_mod_cast positives) zfloor
  · rw [←hr]; exact_mod_cast (by nlinarith [Nat.mul_le_mul_right D spec.1] : 2*D ≤ j*D+2)
  · exact_mod_cast spec.2
  · rw [←hr]; exact_mod_cast (Nat.mul_comm D j).le
  · refine le_trans (Real.rpow_le_rpow_of_exponent_le (by norm_num) ?_) hn
    exact Real.rpow_le_rpow_of_exponent_le (by norm_num) (by exact_mod_cast hj)
  · exact bill

end S008.IntegerBounds
