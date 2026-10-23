import BitXorFiniteBasis

/-!
Structural composition for two-sided XOR compensation around a separate
preparation word. Disjoint read/write regions imply exact commutation on every
incoming state, using the already checked interpreter locality laws. The final
D-word equality is then derived from the accepted finite-basis injection
adapter, without assuming the desired full-word conclusion.

Motivation: Gareth Davidson/bitplane PR926 at
0f216a345c37bc71cc0e22030ef11ec31b26a69e and its PR915 target preparation.
PR926's192 helper pairs are disjoint, but this generic theorem needs only the
weaker helper-versus-target read/write separation. Actual498-gate support and
all111 target-row basis certificates remain source-specific suppliers.
Reuses PR590/597 ordered semantics and reversal, PR774's earlier unary
compensation algebra, and the PR733 two-sided method credited by PR926.
Apache-2.0; prepared with OpenAI assistance. Uncompiled source proposal.
-/
namespace CurrentMain.BitXorDisjointComposition
open BitXor BitXorReversal BitXorInjectionAdapter BitXorFiniteBasis
set_option Elab.async false
variable {Reg : Type} [DecidableEq Reg]

/-- Every read and write belongs to the stated region. -/
def ClosedOn (region : Reg → Prop) (word : List (Gate Reg)) : Prop :=
  ∀ g ∈ word, region g.dst ∧ ∀ r ∈ g.sources, region r

private theorem closed_reverse (region : Reg → Prop) (word : List (Gate Reg))
    (h : ClosedOn region word) : ClosedOn region word.reverse := by
  intro g hg
  exact h g (List.mem_reverse.mp hg)

/-- Separate read/write regions commute, with arbitrary dirty incoming bits.
No involution, ordering or within-region disjointness premise is needed. -/
theorem run_closed_commute
    (region : Reg → Prop) [DecidablePred region]
    (inside outside : List (Gate Reg))
    (hin : ClosedOn region inside)
    (hout : ClosedOn (fun r => ¬ region r) outside)
    (s : State Reg) :
    run inside (run outside s) = run outside (run inside s) := by
  funext r
  by_cases hr : region r
  · have ho : run outside (run inside s) r = run inside s r :=
      run_off_target (fun q => ¬ region q) outside
        (fun g hg => (hout g hg).1) _ r (fun hn => hn hr)
    rw [ho]
    exact run_agree_off_target (fun q => ¬ region q) inside
      (fun g hg q hq hn => hn ((hin g hg).2 q hq))
      (run outside s) s
      (fun q hq => run_off_target (fun v => ¬ region v) outside
        (fun g hg => (hout g hg).1) s q hq)
      r (fun hn => hn hr)
  · have hi : run inside (run outside s) r = run outside s r :=
      run_off_target region inside (fun g hg => (hin g hg).1) _ r hr
    rw [hi]
    exact (run_agree_off_target region outside
      (fun g hg q hq => (hout g hg).2 q hq)
      (run inside s) s
      (fun q hq => run_off_target region inside
        (fun g hg => (hin g hg).1) s q hq) r hr).symm

/-- Lift the finite helper-basis certificate through the actual separate
preparation and its reverse. This establishes the full five-part structural
join once every listed finite supplier is supplied. No clean register premise,
helper pairwise commutation or target-preparation inverse premise is assumed.
The latter is unnecessary for equality to the same prepared parent word. -/
theorem full_word_of_basis
    (target : Reg → Prop) [DecidablePred target]
    (registers : List Reg) (hcover : ∀ r, r ∈ registers)
    (helpers preparation original encoded : List (Gate Reg))
    (hhelpers : ClosedOn (fun r => ¬ target r) helpers)
    (hpreparation : ClosedOn target preparation)
    (hself : ∀ g ∈ helpers, g.dst ∉ g.sources)
    (horiginal_writes : ∀ g ∈ original, target g.dst)
    (horiginal_reads : ∀ g ∈ original, ∀ r ∈ g.sources, ¬ target r)
    (hencoded_writes : ∀ g ∈ encoded, target g.dst)
    (hencoded_reads : ∀ g ∈ encoded, ∀ r ∈ g.sources, ¬ target r)
    (hbasis : ∀ r ∈ registers,
      injectionVector target encoded (run helpers (basisState r)) =
        run helpers (injectionVector target original (basisState r)))
    (s : State Reg) :
    run (helpers ++ preparation ++ encoded ++ preparation.reverse ++ helpers.reverse) s =
      run (preparation ++ original ++ preparation.reverse) s ∧
    ∀ r, ¬ target r →
      run (helpers ++ preparation ++ encoded ++ preparation.reverse ++ helpers.reverse) s r =
        s r := by
  have hblock := (BitXorFiniteBasis.conjugated_word_injection_of_basis target
    registers hcover helpers original encoded hself horiginal_writes
    horiginal_reads hencoded_writes hencoded_reads hbasis (run preparation s)).1
  simp only [run_append] at hblock
  have heq :
      run (helpers ++ preparation ++ encoded ++ preparation.reverse ++ helpers.reverse) s =
        run (preparation ++ original ++ preparation.reverse) s := by
    simp only [run_append]
    rw [run_closed_commute target preparation helpers hpreparation hhelpers s]
    rw [← run_closed_commute target preparation.reverse helpers.reverse
      (closed_reverse target preparation hpreparation)
      (closed_reverse (fun r => ¬ target r) helpers hhelpers)]
    rw [hblock]
  constructor
  · exact heq
  · intro r hr
    rw [heq]
    apply run_off_target target (preparation ++ original ++ preparation.reverse)
    · intro g hg
      simp only [List.mem_append, List.mem_reverse, or_assoc] at hg
      rcases hg with hg | hg | hg
      · exact (hpreparation g hg).1
      · exact horiginal_writes g hg
      · exact (hpreparation g hg).1
    · exact hr

end CurrentMain.BitXorDisjointComposition
#print axioms CurrentMain.BitXorDisjointComposition.run_closed_commute
#print axioms CurrentMain.BitXorDisjointComposition.full_word_of_basis
