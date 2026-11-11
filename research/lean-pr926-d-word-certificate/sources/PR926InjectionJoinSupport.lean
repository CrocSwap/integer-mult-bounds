import PR926FullInjectionRows

/-!
Concrete remaining interface suppliers for historical PR926's complete D word.
The exact original/encoded donor words are checked for target-only writes and
strictly off-target reads. Helpers fix every target-supported vector; this is
derived from accepted XOR linearity and shift transport, without assuming the
needed helper-vector identity or cleanliness of any incoming bit.

The final theorem consumes an explicit complete Fin111 row cover. It does not
assert that uncompiled or missing row certificates exist. Once that cover is
supplied, the accepted finite-basis and disjoint-preparation theorem give the
full Boolean word equality and off-target restoration on arbitrary Fin661 bits.
The literal five-part source binding, physical operators, integer/rounded
precision and current-source adoption remain separate from this scalar result.
Gareth Davidson/bitplane PR915/926, PR733's two-sided method, PR590/597 ordered
semantics and PR774 algebra are credited by the imported sources.
Apache-2.0; OpenAI assistance. Uncompiled source proposal.
-/
namespace CurrentMain.PR926InjectionJoinSupport
open BitXor BitXorConjugacy BitXorInjectionAdapter BitXorFiniteBasis
open BitXorDisjointComposition PR926PreparationSupport PR926FullInjectionRows
set_option Elab.async false

private def injectionOK (word : List (Gate Reg)) : Bool :=
  word.all (fun g => decide (target g.dst) &&
    g.sources.all (fun r => decide (¬ target r)))

private theorem injectionOK_sound (word : List (Gate Reg))
    (h : injectionOK word = true) :
    (∀ g ∈ word, target g.dst) ∧
      (∀ g ∈ word, ∀ r ∈ g.sources, ¬ target r) := by
  have hg : ∀ g ∈ word, target g.dst ∧ ∀ r ∈ g.sources, ¬ target r := by
    intro g hm
    have hh := List.all_eq_true.mp h g hm
    obtain ⟨hd, hs⟩ := Bool.and_eq_true_iff.mp hh
    exact ⟨of_decide_eq_true hd,
      fun r hr => of_decide_eq_true (List.all_eq_true.mp hs r hr)⟩
  exact ⟨fun g hm => (hg g hm).1, fun g hm => (hg g hm).2⟩

private theorem original_check : injectionOK original = true := by decide +kernel
private theorem encoded_check : injectionOK encoded = true := by decide +kernel

theorem original_injection :
    (∀ g ∈ original, target g.dst) ∧
      (∀ g ∈ original, ∀ r ∈ g.sources, ¬ target r) :=
  injectionOK_sound original original_check

theorem encoded_injection :
    (∀ g ∈ encoded, target g.dst) ∧
      (∀ g ∈ encoded, ∀ r ∈ g.sources, ¬ target r) :=
  injectionOK_sound encoded encoded_check

private theorem run_zero (word : List (Gate Reg)) :
    run word (fun _ => false) = (fun _ => false) := by
  have h := run_xor word (fun _ => false) (fun _ => false)
  have hz : xorState (fun _ : Reg => false) (fun _ => false) =
      (fun _ => false) := rfl
  rw [hz] at h
  funext r
  simpa only [xorState, Bool.xor_self] using congrFun h r

/-- Actual helper reads are disjoint from the injected vector's support. -/
theorem helpers_fix_original_vector (s : State Reg) :
    run helpers (injectionVector target original s) =
      injectionVector target original s := by
  let v := injectionVector target original s
  have hs : shift target (fun _ => false) v = v := by
    funext r
    by_cases hr : target r
    · simp only [shift, if_pos hr, Bool.false_xor]
    · simp only [shift, if_neg hr, v, injectionVector, if_neg hr]
  calc
    run helpers v = run helpers (shift target (fun _ => false) v) :=
      congrArg (run helpers) hs.symm
    _ = shift target (run helpers (fun _ => false)) v :=
      run_shift target helpers
        (fun g hg r hr => (helpers_closed g hg).2 r hr) _ v
    _ = v := by rw [run_zero]; exact hs

/-- A complete finite row cover is the only remaining matrix premise here.
Every input coordinate is enumerated; arbitrary dirty states follow from the
accepted finite-basis theorem, not from a zero-input test. -/
theorem full_D_of_rows
    (hrows : ∀ (i : Fin 111) (r : Reg),
      injectionVector target encoded (run helpers (basisState r))
          (⟨111 + i.val, by have := i.isLt; omega⟩ : Reg) =
        injectionVector target original (basisState r)
          (⟨111 + i.val, by have := i.isLt; omega⟩ : Reg))
    (s : State Reg) :
    run (helpers ++ preparation ++ encoded ++ preparation.reverse ++ helpers.reverse) s =
      run (preparation ++ original ++ preparation.reverse) s ∧
    ∀ r, ¬ target r →
      run (helpers ++ preparation ++ encoded ++ preparation.reverse ++ helpers.reverse) s r =
        s r := by
  apply full_word_of_basis target (List.finRange 661)
    (fun r => List.mem_ofFn.mpr ⟨r, rfl⟩) helpers preparation original encoded
    helpers_closed preparation_closed helpers_no_self original_injection.1
    original_injection.2 encoded_injection.1 encoded_injection.2
  intro r _
  rw [helpers_fix_original_vector]
  funext q
  by_cases hq : target q
  · have hbounds : 111 ≤ q.val ∧ q.val < 222 := hq
    let i : Fin 111 := ⟨q.val - 111, by omega⟩
    have heq : (⟨111 + i.val, by have := i.isLt; omega⟩ : Reg) = q := by
      apply Fin.ext
      change 111 + (q.val - 111) = q.val
      omega
    simpa only [heq] using hrows i r
  · simp only [injectionVector, if_neg hq]

end CurrentMain.PR926InjectionJoinSupport
#print axioms CurrentMain.PR926InjectionJoinSupport.original_injection
#print axioms CurrentMain.PR926InjectionJoinSupport.encoded_injection
#print axioms CurrentMain.PR926InjectionJoinSupport.helpers_fix_original_vector
#print axioms CurrentMain.PR926InjectionJoinSupport.full_D_of_rows
