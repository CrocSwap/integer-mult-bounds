import Work.GFrame.Engine.Sweep
import WHTCheck.Solution

/-!
# GFrame engine, part 4: one level of the recursion for generalised words (agent key: eng-ram)

Copy of `amplifyB` (`Work/Block/Recursion.lean`) with two changes:

* the word is a `GWord` with certificate `GLiveKernel e w` (semantics `gwalk`);
* after the XOR table the level also builds the table of `lum` over `Bits f`
  (`WHT.lum_tables`, doubling construction, `O(2^f)` work), which the free diagonal phases
  read; it is part of the environment of the sweep (`GRig`).

Cost: the same `2^k` linear term and the same recursive calls as `amplifyB`.
-/

set_option linter.unusedSectionVars false

namespace OAI
namespace PowerSaving.RAM
open Binary Matrix Ty Finset GF
noncomputable section

section
universe U
variable {α ρ σ : Type*} [Fintype α] [DecidableEq α] [Fintype ρ] [DecidableEq ρ]
  [Fintype σ] [DecidableEq σ]
variable {ι : Type U} {m : Bool}
    {k f : ι → ℕ} {cl : Paint} {b : Bank (hatch cl) ι}
    {v : ∀ i, Sim σ (k i)→ℂ}

/-- **One level of the recursion for a generalised word** (replaces `amplifyB`). -/
lemma gamplify (m : Bool) (b : Bank (hatch cl) ι) (v : ∀ i, Sim σ (k i) → ℂ)
    (X : Layout α) (R : Layout ρ) (Q : Layout σ) (e : σ → ρ) (he : Function.Injective e)
    (r : ℕ) (hr : 3 ≤ X.n) (hq : ∀ i, X.n*f i+r=k i) (hd : r < X.n) (hQ : 0<Q.n)
    (n τ : ℕ → ι → ℕ)
    (hc : ∀ rk, 1 ≤ rk → rk < X.n → ∀ i, n rk i*(sim Q (rk * f i)).n=2^k i)
    (hk : ∀ rk, 1 ≤ rk → rk < X.n → Contract cl b (fun i => rk * f i) (τ rk) Q)
    (hB : Small b.B (fun i => 2^k i))
    (w : GWord α ρ) (hw : GLiveKernel e w) (hP : w.Proper X.n) :
    Able m b (simIn cl) (bundle cl) (fun i => loaded cl Q (k i) (v i))
      (fun i => (sim Q (k i)).tape (whole (k i) (v i)))
      (fun i => 2^k i) (fun i => w.cost (fun rk => n rk i * τ rk i)) := by
  let W i := 2^k i
  let s := simIn cl
  let eQ (i : ι) := ebb X r (f i) (k i) (hq i) (v i)
  let zQ (i : ι) : Grain α σ r (f i) :=
    fun j => chords r (f i) (fun l => eQ i (j.1,l)) j.2
  let Z (i : ι) : Grain α ρ r (f i) := crossAct r (f i) (embM e) (zQ i)
  let O (i : ι) : Grain α σ r (f i) :=
    crossAct r (f i) (extM e) (gcoast r (f i) w (Z i))
  let szQ i := (fleet X Q r (f i)).n
  let szR i := (fleet X R r (f i)).n
  have hszQ : Dom W szQ := by
    refine ⟨Q.n+1, fun i => ?_⟩
    unfold W szQ fleet
    rw [Layout.pair_len, book_len,hq]
    simp only [mul_add,add_mul,mul_one,one_mul]
    gcongr <;> simp
  have hszR : Dom W szR := by
    refine ⟨R.n+1, fun i => ?_⟩
    unfold W szR fleet
    rw [Layout.pair_len, book_len,hq]
    simp only [mul_add,add_mul,mul_one,one_mul]
    gcongr <;> simp
  have hn (i : ι) : 0 < W i := pow_pos (by decide) _
  have hf (i) : f i ≤ k i := by
    have g := hq i
    have h := Nat.le_mul_of_pos_left (f i) (show 0 < X.n by omega)
    omega
  have hy (i) : k i ≤ W i := Nat.lt_two_pow_self.le
  have sd := hB.mono hy
  have sq := sd.mono hf
  let p2 i := 2^f i
  have hm : Small b.B p2 :=
    hB.mono (fun i => Nat.pow_le_pow_right (by omega) (hf i))
  have hcube (i) : p2 i ^ 3 ≤ W i := by
    unfold p2 W
    rw [← pow_mul]
    apply Nat.pow_le_pow_right (by omega)
    have hh : 3*f i ≤ X.n*f i := Nat.mul_le_mul_right _ hr
    have hg := hq i
    rw [mul_comm]
    omega
  let env (i : ι) := loaded cl Q (k i) (v i)
  -- construct fields (f,p2)
  have hmf : Can m b.B s Ty.w env f W := by
    have ht : Can m b.B s Ty.w env k W := Can.first
    refine (ht.dvdW (Can.wc X.n) sd).cong (fun _ => rfl) ?_
    intro i
    rw [← hq,mul_comm X.n]
    exact Layout.div_join hd
  have hmp : Can m b.B s (Ty.p Ty.w Ty.w) env (fun i => (f i,p2 i)) W :=
    hmf.pair (hmf.wTwo sq hm (Dom.of_le (fun i => (hf i).trans (hy i))))
  let T1 := Ty.p s (Ty.p Ty.w Ty.w)
  let Y (i : ι) : T T1 := (env i,f i,p2 i)
  have hmx : Can m b.B T1 (Ty.a Ty.w) Y (fun i => xorTab (f i)) W :=
    (Can.xor_prepare (m:=m) (f:=f) (B:=b.B) (s:=T1) (x:=Y)
      (Can.fst Can.second) (Can.snd Can.second) sq hm).mono hcube
  let T2 := Ty.p T1 (Ty.a Ty.w)
  let Y' (i : ι) : T T2 := (Y i,xorTab (f i))
  -- NEW: the table of `lum` over `Bits f`
  have hE2 : Has m b.B T2 s Y' env := Can.fst Can.first
  have hml : Can m b.B T2 (Ty.a sc) Y'
      (fun i => (bits (f i)).tape (fun y : Bits (f i) => lum y)) W :=
    (WHT.lum_tables (k:=f) (Can.fst (Can.snd Can.first)) sq hm hE2.snd.fst).1.mono
      (fun i => Nat.pow_le_pow_right (by omega) (hf i))
  let T2' := Ty.p T2 (Ty.a sc)
  let Y'' (i : ι) : T T2' := (Y' i,(bits (f i)).tape (fun y : Bits (f i) => lum y))
  -- the input, read as a table on the slots
  have hG0 : Rig m b.B f T2 Y' cl X Q r eQ := by
    refine ⟨⟨?_,?_,Can.second,hm⟩,?_,?_⟩
    · exact Can.snd (Can.snd Can.first)
    · exact Can.fst (Can.snd Can.first)
    · exact hE2.snd.fst
    · exact hE2.snd.snd.cong (fun _ => rfl) (fun i => (ebb_eq ..).symm)
  have hG : Rig m b.B f T2' Y'' cl X Q r eQ := hG0.gather id Y'' (t:=T2') Can.first
  -- leftover bits, still on the slots
  have HH : Can m b.B T2' (bundle cl) Y'' (fun i => (fleet X Q r (f i)).tape (zQ i)) W :=
    hG.dots_cost.weaken hszQ
  let T3 := Ty.p T2' (bundle cl)
  let A (i) : T T3 := (Y'' i,(fleet X Q r (f i)).tape (zQ i))
  have Hg := hG.gather id A (t:=T3) Can.first
  have G : Rig m b.B f T3 A cl X Q r zQ := ⟨Hg.gear,Hg.imag,Can.second⟩
  -- embed the slots into the table of roles; scratch roles are created as zero
  have HE : Can m b.B T3 (bundle cl) A (fun i => (fleet X R r (f i)).tape (Z i)) W :=
    (G.cross_point R (embM e)).weaken hszR
  let T4 := Ty.p T3 (bundle cl)
  let A4 (i) : T T4 := (A i,(fleet X R r (f i)).tape (Z i))
  have Hg4 := G.gather id A4 (t:=T4) Can.first
  have hL4 : Has m b.B T4 (Ty.a sc) A4
      (fun i => (bits (f i)).tape (fun y : Bits (f i) => lum y)) :=
    Can.snd (Can.fst Can.first)
  have G4 : GRig m b.B f T4 A4 cl X R r Z := ⟨⟨Hg4.gear,Hg4.imag,Can.second⟩,hL4⟩
  -- the GENERALISED word on the table of roles
  have Hy := G4.gsweep n τ Q hQ hk
    (fun rk h1 h2 i => by rw [book_len,hq]; exact hc rk h1 h2 i) w hP
  -- extract the slots; scratch roles are dropped
  let T5 := Ty.p T4 (bundle cl)
  let A5 (i) : T T5 := (A4 i,(fleet X R r (f i)).tape (gcoast r (f i) w (Z i)))
  have Hg5 := G4.rig.gather id A5 (t:=T5) Can.first
  have G5 : Rig m b.B f T5 A5 cl X R r (fun i => gcoast r (f i) w (Z i)) :=
    ⟨Hg5.gear,Hg5.imag,Can.second⟩
  have HX : Can m b.B T5 (bundle cl) A5 (fun i => (fleet X Q r (f i)).tape (O i)) W :=
    (G5.cross_point Q (extM e)).weaken hszQ
  have heq (i) : O i = ebb X r (f i) (k i) (hq i) (whole (k i) (v i)) :=
    gamplifies X r (f i) (k i) (hq i) e he w hw (v i)
  have ha (i) : (fleet X Q r (f i)).tape (O i) =
      (sim Q (k i)).tape (whole (k i) (v i)) := by
    rw [heq]; exact ebb_eq ..
  have Ho := ((Hy.weaken hszR (fun _ => le_rfl)).save_keep
    (Able.of_can (b:=b) HX)).cong (fun _ => rfl) ha
  have Hx := (Able.of_can (b:=b) hmp).save_keep
    ((Able.of_can (b:=b) hmx).save_keep ((Able.of_can (b:=b) hml).save_keep
      ((Able.of_can (b:=b) HH).save_keep ((Able.of_can (b:=b) HE).save_keep Ho))))
  simpa only [Nat.zero_add,Nat.add_zero] using Hx

end
end
end PowerSaving.RAM
end OAI

#print axioms OAI.PowerSaving.RAM.gamplify
