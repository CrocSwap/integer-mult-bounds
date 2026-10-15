import BitXorRowPullback

/-!
A destination-filtered donor collector for actual injection words. Target-only
writes and strictly off-target reads imply that a pulled target singleton is
exactly the target followed by the ordered concatenation of donors from gates
writing that target. Gates writing other target coordinates are skipped by a
proved structural identity, rather than repeatedly reducing every scalar donor.
Donor order and multiplicity are preserved, including repeated target writes.

This is a source-only contingency for the measured PR926 full-row certificates.
It changes no existing accepted row, assumes no concrete donor equation, and
supplies no physical, precision or selected-construction claim. Reuses the
accepted PR590/597 interpreter and row-pullback laws, PR774 algebra, and Gareth
Davidson/bitplane PR915/926 with PR733 attribution. Apache-2.0; OpenAI assistance.
-/
namespace CurrentMain.BitXorTargetDonorCollector
open BitXor BitXorInjectionAdapter BitXorRowPullback
set_option Elab.async false
variable {Reg : Type} [DecidableEq Reg]

/-- Retain every matching gate's sources in chronological operand order. -/
def collectDonors (q : Reg) : List (Gate Reg) → List Reg
  | [] => []
  | g :: rest =>
      if g.dst = q then g.sources ++ collectDonors q rest
      else collectDonors q rest

private theorem pullSingle_avoids (dst src : Reg) (row : List Reg)
    (h : ∀ r ∈ row, r ≠ dst) : pullSingle dst src row = row := by
  induction row with
  | nil => rfl
  | cons r rs ih =>
    simp only [pullSingle, if_neg (h r List.mem_cons_self)]
    exact congrArg (List.cons r)
      (ih (fun q hq => h q (List.mem_cons_of_mem r hq)))

private theorem pullSources_avoids (dst : Reg) (sources row : List Reg)
    (h : ∀ r ∈ row, r ≠ dst) : pullSources dst sources row = row := by
  induction sources with
  | nil => rfl
  | cons src rest ih =>
    rw [pullSources, ih]
    exact pullSingle_avoids dst src row h

variable (target : Reg → Prop) [DecidablePred target]

private theorem collectDonors_outside (word : List (Gate Reg)) (q : Reg)
    (hreads : ∀ g ∈ word, ∀ r ∈ g.sources, ¬ target r) :
    ∀ r ∈ collectDonors q word, ¬ target r := by
  induction word with
  | nil => intro r hr; cases hr
  | cons g rest ih =>
    intro r hr
    have ht : ∀ a ∈ rest, ∀ v ∈ a.sources, ¬ target v :=
      fun a ha => hreads a (List.mem_cons_of_mem g ha)
    by_cases hd : g.dst = q
    · simp only [collectDonors, if_pos hd] at hr
      rcases List.mem_append.mp hr with hg | hg
      · exact hreads g List.mem_cons_self r hg
      · exact ih ht r hg
    · simp only [collectDonors, if_neg hd] at hr
      exact ih ht r hr

private theorem pullSources_head (dst : Reg) (sources row : List Reg)
    (hd : target dst) (hs : ∀ r ∈ sources, ¬ target r)
    (hr : ∀ r ∈ row, ¬ target r) :
    pullSources dst sources (dst :: row) = dst :: (sources ++ row) := by
  induction sources with
  | nil => rfl
  | cons src rest ih =>
    have ht : ∀ r ∈ rest, ¬ target r :=
      fun r hm => hs r (List.mem_cons_of_mem src hm)
    rw [pullSources, ih ht]
    have ha : ∀ r ∈ rest ++ row, r ≠ dst := by
      intro r hm he
      have hn : ¬ target r := by
        rcases List.mem_append.mp hm with hm | hm
        · exact ht r hm
        · exact hr r hm
      apply hn
      simpa only [he] using hd
    simp only [pullSingle, if_pos rfl, if_true]
    rw [pullSingle_avoids dst src (rest ++ row) ha]
    rfl

/-- Exact list identity, without a distinct-destination or clean-state premise. -/
theorem pullWord_target (word : List (Gate Reg)) (q : Reg)
    (hq : target q)
    (hwrites : ∀ g ∈ word, target g.dst)
    (hreads : ∀ g ∈ word, ∀ r ∈ g.sources, ¬ target r) :
    pullWord word [q] = q :: collectDonors q word := by
  induction word with
  | nil => rfl
  | cons g rest ih =>
    have hw : ∀ a ∈ rest, target a.dst :=
      fun a ha => hwrites a (List.mem_cons_of_mem g ha)
    have hr : ∀ a ∈ rest, ∀ r ∈ a.sources, ¬ target r :=
      fun a ha => hreads a (List.mem_cons_of_mem g ha)
    rw [pullWord, ih hw hr]
    by_cases hd : g.dst = q
    · simp only [collectDonors, if_pos hd]
      simpa only [hd] using pullSources_head target q g.sources
        (collectDonors q rest) hq (hreads g List.mem_cons_self)
        (collectDonors_outside target rest q hr)
    · have ha : ∀ r ∈ q :: collectDonors q rest, r ≠ g.dst := by
        intro r hm he
        rcases List.mem_cons.mp hm with hqeq | hm
        · exact hd (he.symm.trans hqeq)
        · have hn := collectDonors_outside target rest q hr r hm
          apply hn
          rw [he]
          exact hwrites g List.mem_cons_self
      rw [pullSources_avoids g.dst g.sources _ ha]
      simp only [collectDonors, if_neg hd]

private theorem offTarget_outside (row : List Reg)
    (h : ∀ r ∈ row, ¬ target r) : offTarget target row = row := by
  induction row with
  | nil => rfl
  | cons r rs ih =>
    simp only [offTarget, if_neg (h r List.mem_cons_self)]
    exact congrArg (List.cons r)
      (ih (fun q hq => h q (List.mem_cons_of_mem r hq)))

/-- The inexpensive collector denotes the actual arbitrary-state injection. -/
theorem injection_coordinate_collected (word : List (Gate Reg))
    (hwrites : ∀ g ∈ word, target g.dst)
    (hreads : ∀ g ∈ word, ∀ r ∈ g.sources, ¬ target r)
    (s : State Reg) (q : Reg) (hq : target q) :
    injectionVector target word s q = donorXor (collectDonors q word) s := by
  rw [injection_coordinate target word s q hq,
    pullWord_target target word q hq hwrites hreads]
  simp only [offTarget, if_pos hq]
  rw [offTarget_outside target (collectDonors q word)
    (collectDonors_outside target word q hreads)]

theorem prepared_injection_coordinate_collected
    (word entrance : List (Gate Reg))
    (hwrites : ∀ g ∈ word, target g.dst)
    (hreads : ∀ g ∈ word, ∀ r ∈ g.sources, ¬ target r)
    (s : State Reg) (q : Reg) (hq : target q) :
    injectionVector target word (run entrance s) q =
      donorXor (pullWord entrance (collectDonors q word)) s := by
  rw [pullWord_sound]
  exact injection_coordinate_collected target word hwrites hreads
    (run entrance s) q hq

end CurrentMain.BitXorTargetDonorCollector
#print axioms CurrentMain.BitXorTargetDonorCollector.pullWord_target
#print axioms CurrentMain.BitXorTargetDonorCollector.injection_coordinate_collected
#print axioms CurrentMain.BitXorTargetDonorCollector.prepared_injection_coordinate_collected
