/-
LEAN-PREM6, Nov 17. E3-tree: the PARENT/CHILD half of owned_erasure's E3 as a kernel fact for #7630's
owned skeleton.  See OwnedTree.md.  Data: OwnedTreeData.lean (generated, ownedtree_gen/gen.py).

Model (FINITE-PRECOMPILATION.md section 3 and 6): a unit is the finite word; at each paid round (a
MOVE) the unit is suspended, the ENTIRE child unit (the same finite word, own unit tag) is run to
completion, then the parent advances.  Owned banks are tagged by the unit path.  A CLEAR in unit p
requires the bank (p,f) live and NO live bank of any strict descendant of p.
-/
import Nov15.OwnedSkeleton

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace OwnedTree
open OwnedSkeleton

abbrev Path := List ℕ
abbrev St := List (Path × ℕ)

/-- `q` strictly extends `p`. -/
def desc (p q : Path) : Bool := q.take p.length == p && p.length < q.length

/-- One owned event in unit `p`; the CLEAR clause is E3's "never acts on a descendant's live storage". -/
def applyEv (p : Path) (L : St) : E → Option St
  | .init f _ => if (p, f) ∈ L then none else some ((p, f) :: L)
  | .move f _ => if (p, f) ∈ L then some L else none
  | .clear f _ => if (p, f) ∈ L ∧ ∀ q ∈ L, desc p q.1 = false then some (L.erase (p, f)) else none
  | _ => none

/-- Walk the events of unit `p` from index `i`; `ch gap L` runs all children called at that gap
(before event `gap`). -/
def go (ch : ℕ → St → Option St) (p : Path) : ℕ → St → List E → Option St
  | i, L, [] => ch i L
  | i, L, e :: es => (ch i L).bind fun L' => (applyEv p L' e).bind fun L'' => go ch p (i + 1) L'' es

def sitesAt (sites : List ℕ) (g : ℕ) : List ℕ := (List.range sites.length).filter fun j => sites[j]! == g

/-- Run unit `p` to depth `d` (depth 0 = no child calls) with child call sites `sites`
(site j is child unit `p ++ [j]`). -/
def execU (sites : List ℕ) : ℕ → Path → St → Option St
  | 0, p, L => go (fun _ L => some L) p 0 L skel
  | d + 1, p, L =>
      go (fun g L => (sitesAt sites g).foldlM (fun L j => execU sites d (p ++ [j]) L) L) p 0 L skel

/-! ## The frame lemma: E1 of one unit, run inside any context, restores the context -/

def Fresh (p : Path) (L : St) : Prop := ∀ q ∈ L, ¬ p <+: q.1
def NoDesc (p : Path) (L : St) : Prop := ∀ q ∈ L, desc p q.1 = false

def own (p : Path) (l : List ℕ) : St := l.map fun f => (p, f)

theorem desc_false_of_not_prefix {p q : Path} (h : ¬ p <+: q) : desc p q = false := by
  unfold desc
  by_cases h1 : q.take p.length = p
  · exfalso; apply h; rw [← h1]; exact List.take_prefix _ _
  · simp [h1]

theorem desc_self (p : Path) : desc p p = false := by simp [desc]

theorem nodesc_own_append {p : Path} {l : List ℕ} {M : St} (hM : Fresh p M) : NoDesc p (own p l ++ M) := by
  intro q hq
  rcases List.mem_append.1 hq with h | h
  · obtain ⟨f, _, rfl⟩ := List.mem_map.1 h
    exact desc_self p
  · exact desc_false_of_not_prefix (hM q h)

theorem mem_own_append {p : Path} {l : List ℕ} {M : St} (hM : Fresh p M) (f : ℕ) :
    ((p, f) ∈ own p l ++ M) ↔ f ∈ l := by
  constructor
  · intro h
    rcases List.mem_append.1 h with h | h
    · obtain ⟨g, hg, hq⟩ := List.mem_map.1 h
      have : g = f := (Prod.mk.inj hq).2
      exact this ▸ hg
    · exact absurd (List.prefix_refl p) (hM _ h)
  · intro h; exact List.mem_append.2 (Or.inl (List.mem_map.2 ⟨f, h, rfl⟩))

theorem erase_own_append {p : Path} {l : List ℕ} {M : St} (f : ℕ) (hf : f ∈ l) :
    (own p l ++ M).erase (p, f) = own p (l.erase f) ++ M := by
  have hinj : Function.Injective (fun f : ℕ => ((p, f) : Path × ℕ)) := fun a b h => (Prod.mk.inj h).2
  unfold own
  rw [List.erase_append_left _ (List.mem_map.2 ⟨f, hf, rfl⟩), List.map_erase hinj]

/-- E1 of the unit (e1run) transports to the tagged run, in any context with no live bank at or below `p`. -/
theorem go_frame (p : Path) (ch : ℕ → St → Option St)
    (hch : ∀ i L, NoDesc p L → ch i L = some L) :
    ∀ (es : List E) (i : ℕ) (l l' : List ℕ) (M : St), Fresh p M → e1run l es = some l' →
      go ch p i (own p l ++ M) es = some (own p l' ++ M) := by
  intro es
  induction es with
  | nil =>
    intro i l l' M hM h
    simp only [e1run, Option.some.injEq] at h
    subst h
    simp [go, hch i _ (nodesc_own_append hM)]
  | cons e es ih =>
    intro i l l' M hM h
    have hc := hch i _ (nodesc_own_append (l := l) hM)
    cases e with
    | init f c =>
      simp only [e1run] at h
      by_cases hf : f ∈ l
      · simp [hf] at h
      · have h' : e1run (f :: l) es = some l' := by simpa [hf] using h
        have h1 : (p, f) ∉ own p l ++ M := fun hm => hf ((mem_own_append hM f).1 hm)
        have := ih (i + 1) (f :: l) l' M hM h'
        simp only [go, hc, Option.bind_some, applyEv, h1, if_false]
        simpa [own] using this
    | move f b =>
      simp only [e1run] at h
      by_cases hf : f ∈ l
      · have h' : e1run l es = some l' := by simpa [hf] using h
        have := ih (i + 1) l l' M hM h'
        have h1 : (p, f) ∈ own p l ++ M := (mem_own_append hM f).2 hf
        simp only [go, hc, Option.bind_some, applyEv, h1, if_true]
        exact this
      · simp [hf] at h
    | clear f c =>
      simp only [e1run] at h
      by_cases hf : f ∈ l
      · have h' : e1run (l.erase f) es = some l' := by simpa [hf] using h
        have := ih (i + 1) (l.erase f) l' M hM h'
        have h1 : (p, f) ∈ own p l ++ M := (mem_own_append hM f).2 hf
        have h2 : ∀ q ∈ own p l ++ M, desc p q.1 = false := nodesc_own_append (l := l) hM
        simp only [go, hc, Option.bind_some, applyEv]
        rw [if_pos ⟨h1, h2⟩, erase_own_append f hf]
        simpa using this
      · simp [hf] at h
    | _ => simp [e1run] at h

/-! ## Main theorem: the whole call tree, any depth, any call sites -/

theorem fresh_child {p : Path} {L : St} (h : NoDesc p L) (j : ℕ) : Fresh (p ++ [j]) L := by
  intro q hq hpre
  have h1 := h q hq
  have : desc p q.1 = true := by
    unfold desc
    have hp : p.length < (p ++ [j]).length := by simp
    have hl := hpre.length_le
    simp only [Bool.and_eq_true, beq_iff_eq, decide_eq_true_eq]
    refine ⟨?_, by omega⟩
    have := (List.prefix_append p [j]).trans hpre
    exact (List.prefix_iff_eq_take.1 this).symm
  rw [h1] at this; exact absurd this (by simp)

theorem fresh_of_nodesc_ext {p : Path} {L : St} (h : NoDesc p L) (j : ℕ) : NoDesc (p ++ [j]) L := by
  intro q hq
  have := fresh_child h j q hq
  exact desc_false_of_not_prefix this

/-- A child run starting in a state with no live bank at or below the child returns the state unchanged. -/
theorem execU_id (sites : List ℕ) (sk_ok : e1run [] skel = some []) :
    ∀ (d : ℕ) (p : Path) (L : St), Fresh p L → execU sites d p L = some L := by
  intro d
  induction d with
  | zero =>
    intro p L hL
    have := go_frame p (fun _ L => some L) (fun _ _ _ => rfl) skel 0 [] [] L hL sk_ok
    simpa [own, execU] using this
  | succ d ih =>
    intro p L hL
    have key := go_frame p (fun g L => (sitesAt sites g).foldlM (fun L j => execU sites d (p ++ [j]) L) L)
      (by
        intro i L' hL'
        have : ∀ (js : List ℕ) (L'' : St), NoDesc p L'' →
            js.foldlM (fun L j => execU sites d (p ++ [j]) L) L'' = some L'' := by
          intro js
          induction js with
          | nil => intro L'' _; rfl
          | cons j js ihj =>
            intro L'' hL''
            simp only [List.foldlM, ih (p ++ [j]) L'' (fresh_child hL'' j)]
            exact ihj L'' hL''
        exact this _ _ hL') skel 0 [] [] L hL sk_ok
    simpa [own, execU] using key

/-- E3-tree for the recursion tree of the word: running the root unit (path []) to any depth, with
child calls at ANY set of call sites, succeeds and leaves no bank live. -/
theorem e3_tree (sites : List ℕ) (d : ℕ) : execU sites d [] [] = some [] :=
  execU_id sites (by decide +kernel) d [] [] (by intro q hq; simp at hq)

/-! ## The caller layer (#7113: 17 sequential native calls, the caller owns no storage) -/

/-- The caller as the root: 17 sequential native calls (children `[k]`), each a full call tree. -/
def callerRun (sites : List ℕ) (d : ℕ) : Option St :=
  (List.range 17).foldlM (fun L k => execU sites d [k] L) []

theorem caller_tree (sites : List ℕ) (d : ℕ) : callerRun sites d = some [] := by
  have : ∀ (ks : List ℕ) (L : St), (∀ q ∈ L, q.1 = [] ∨ ∀ k ∈ ks, ¬ [k] <+: q.1) → False ∨ True := by
    intro _ _ _; exact Or.inr trivial
  unfold callerRun
  have h : ∀ (ks : List ℕ), ks.Nodup → ∀ (L : St), (∀ q ∈ L, ∀ k ∈ ks, ¬ [k] <+: q.1) →
      ks.foldlM (fun L k => execU sites d [k] L) L = some L := by
    intro ks
    induction ks with
    | nil => intro _ L _; rfl
    | cons k ks ih =>
      intro hnd L hL
      simp only [List.foldlM, execU_id sites (by decide +kernel) d [k] L (fun q hq => hL q hq k (by simp)),
        Option.bind_some]
      exact ih (List.nodup_cons.1 hnd).2 L (fun q hq k' hk' => hL q hq k' (by simp [hk']))
  exact h _ (List.nodup_range) [] (by intro q hq; simp at hq)

/-! ## Concrete runs (kernel) and negative controls -/

/-- Run a unit made from `skel'` instead of `skel` (to test rejection). -/
def execBad (skel' : List E) (sites : List ℕ) (p : Path) : Option St :=
  go (fun g L => (sitesAt sites g).foldlM
    (fun L j => go (fun _ L => some L) (p ++ [j]) 0 L skel') L) p 0 [] skel

/-- Control 1: a child that leaks one bank (its last CLEAR missing) leaves a live descendant bank;
the parent's next CLEAR (of its own field) is then rejected. Site at gap 1: parent has live field. -/
def parentSk : List E := [.init 1501 3, .clear 1501 3]
def childLeak : List E := [.init 1502 3]
theorem c_child_leak : go (fun g L => if g = 1 then
    go (fun _ L => some L) [0] 0 L childLeak else some L) [] 0 [] parentSk = none := by decide +kernel
/-- Control 1b (accepting twin): the same call with a well-formed child succeeds. -/
def childOk : List E := [.init 1502 3, .clear 1502 3]
theorem c_child_ok : go (fun g L => if g = 1 then
    go (fun _ L => some L) [0] 0 L childOk else some L) [] 0 [] parentSk = some [] := by decide +kernel
/-- Control 3: a child that CLEARs a bank it never owns (the parent's field, same label, other tag). -/
theorem c_child_steals : go (fun g L => if g = 1 then
    go (fun _ L => some L) [0] 0 L [.clear 1501 3] else some L) [] 0 [] parentSk = none := by decide +kernel
/-- Control 4: a parent CLEAR with a descendant bank live (applyEv directly). -/
theorem c_clear_with_desc :
    applyEv [] [([], 1501), ([0], 1502)] (.clear 1501 3) = none := by decide +kernel
theorem c_clear_no_desc :
    applyEv [] [([], 1501)] (.clear 1501 3) = some [] := by decide +kernel
/-- Control 5: a sibling-boundary leak at caller level: a leaking native call is rejected by `go` at the root. -/
theorem c_caller_leak : (go (fun _ L => some L) [3] 0 [] childLeak).bind (fun L =>
    if L = [] then some L else none) = none := by decide +kernel

#print axioms go_frame
#print axioms execU_id
#print axioms e3_tree
#print axioms caller_tree

end OwnedTree
