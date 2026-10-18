/-
Hyperplane-ended helpers with a MULTI-GATE `cleanup_tail`, several helpers at once, and the cold
instance `E = ⊥`.

`Tail.lean` treats one helper with one cleanup gate `h -= p`.  Here the `cleanup_tail` is modelled
as an arbitrary list of gates `t += q • s` (or `t *= q`), each at its own frame `F`: every operand not
already at `F` climbs to `F` (one relabel), then the gate runs.  The shipped hyperplane-ended helpers
of #591/#592 are the one-gate case; multi-gate and `scale` tails are not checked here against
emitted words.  A helper `j` may be touched by any number of tail gates (as target or as partner); what
matters is the LAST tail gate touching it, whose frame must be `term j`.  The remaining cleanup `b`
never relabels a hyperplane-ended helper, and the post wrappers `relabel j (term j) (done j)` close
every such helper.

* `mtail_wellLabelled`   the tail is always well labelled: every gate runs with its operands at
                         its frame (G0 for the partners), whatever the gate list;
* `labRun_mtail`         after the tail a register sits at the frame of the last gate touching it
                         (`lastFrame`), and is untouched otherwise;
* `hpe_labels_multi`     the word `a ++ mtail ++ b ++ posts` is well labelled and every helper of
                         the list ends at `(done, j)`;
* `hpe_labels_tail`      the single-gate word of `Tail.lean` is the one-gate instance when both
                         operands start away from `U`;
* `hpe_word_multi`       Lemma A on streams for every such helper (per-helper `C j` and (N));
* `exact_cold`, `cold_hyperplane_width`   the cold specialisation: given `T_E = id` (true of the
                         canonical frame of `E = ⊥`, an input checked outside Lean), (N) reduces to
                         `T_U = L (C ⊗ id) R`; `⊥ ≤ U` with `dim U = 8` gives width 8 (rank arithmetic).
                         #593's `hpe_word` already takes an arbitrary entrance frame.
Apache-2.0.
-/
import HyperplaneEnd.Main

namespace HyperplaneEnd

open TensorProduct LemmaG LemmaG.Stream LemmaA

deriving instance DecidableEq for XLab

/-- A gate of the `cleanup_tail`: `t += q • s` or `t *= q`, run at frame `F`. -/
inductive TGate (ι Fr K : Type*) where
  | add (t s : ι) (F : Fr) (q : K)
  | scale (t : ι) (F : Fr) (q : K)

namespace TGate

variable {ι Fr K : Type*}

/-- The frame the gate runs at. -/
def frame : TGate ι Fr K → Fr
  | add _ _ F _ => F
  | scale _ F _ => F

/-- The registers the gate touches (its operands). -/
def regs : TGate ι Fr K → List ι
  | add t s _ _ => [t, s]
  | scale t _ _ => [t]

end TGate

section Labels

variable {ι Fr K : Type*} [DecidableEq ι] [DecidableEq Fr]

/-- The climb of register `r` to frame `F` in this model: nothing if `r` is already
at `F`, else one relabel from its current label. -/
def climb (r : ι) (F : Fr) (l : ι → XLab ι Fr) : List (Event ι (XLab ι Fr) K) :=
  if l r = .frame F then [] else [.relabel r (l r) (.frame F)]

/-- One tail gate as emitted: the climbs of its operands to its frame, then the scalar gate. -/
def block (g : TGate ι Fr K) (l : ι → XLab ι Fr) : List (Event ι (XLab ι Fr) K) :=
  match g with
  | .add t s F q => climb t F l ++ climb s F (labRun (climb (K := K) t F l) l) ++ [.add t s q]
  | .scale t F q => climb t F l ++ [.scale t q]

/-- The emitted `cleanup_tail` of a gate list, threading the labels. -/
def mtail : List (TGate ι Fr K) → (ι → XLab ι Fr) → List (Event ι (XLab ι Fr) K)
  | [], _ => []
  | g :: gs, l => block g l ++ mtail gs (labRun (block g l) l)

/-- The frame of the last gate of the list touching `r` (`none` if no gate touches it). -/
def lastFrame (r : ι) : List (TGate ι Fr K) → Option Fr
  | [] => none
  | g :: gs =>
    match lastFrame r gs with
    | some F => some F
    | none => if r ∈ g.regs then some g.frame else none

/-- The post wrappers `relabel j (term j) (done j)` of a list of helpers. -/
def posts (term : ι → Fr) (hs : List ι) : List (Event ι (XLab ι Fr) K) :=
  hs.map fun j => .relabel j (.frame (term j)) (.done j)

theorem labRun_climb (r : ι) (F : Fr) (l : ι → XLab ι Fr) :
    labRun (climb (K := K) r F l) l = Function.update l r (.frame F) := by
  unfold climb
  split_ifs with h
  · simp only [labRun]
    rw [← h, Function.update_eq_self]
  · simp [labRun, Event.lab]

theorem wellLabelled_climb (r : ι) (F : Fr) (l : ι → XLab ι Fr) :
    WellLabelled (climb (K := K) r F l) l := by
  unfold climb
  split_ifs
  · trivial
  · simp [WellLabelled, Event.Admissible]

theorem labRun_block (g : TGate ι Fr K) (l : ι → XLab ι Fr) (i : ι) :
    labRun (block g l) l i = if i ∈ g.regs then .frame g.frame else l i := by
  cases g with
  | add t s F q =>
    simp only [block]
    rw [labRun_append, labRun_append, labRun_climb, labRun_climb]
    by_cases hs : i = s
    · subst hs; simp [labRun, Event.lab, TGate.regs, TGate.frame]
    · by_cases ht : i = t
      · subst ht; simp [labRun, Event.lab, TGate.regs, TGate.frame, Function.update_of_ne hs]
      · simp [labRun, Event.lab, TGate.regs, Function.update_of_ne hs, Function.update_of_ne ht, hs, ht]
  | scale t F q =>
    simp only [block]
    rw [labRun_append, labRun_climb]
    by_cases ht : i = t
    · subst ht; simp [labRun, Event.lab, TGate.regs, TGate.frame]
    · simp [labRun, Event.lab, TGate.regs, Function.update_of_ne ht, ht]

/-- Every emitted tail gate is admissible: both operands are at the gate's frame (G0). -/
theorem wellLabelled_block (g : TGate ι Fr K) (l : ι → XLab ι Fr) :
    WellLabelled (block g l) l := by
  cases g with
  | add t s F q =>
    simp only [block]
    have h1 := labRun_climb (K := K) t F l
    rw [wellLabelled_append, wellLabelled_append, labRun_append, h1, labRun_climb]
    refine ⟨⟨wellLabelled_climb _ _ _, wellLabelled_climb _ _ _⟩, ?_⟩
    simp only [WellLabelled, Event.Admissible, and_true]
    by_cases hts : t = s
    · subst hts; rfl
    · rw [Function.update_of_ne hts, Function.update_self, Function.update_self]
  | scale t F q =>
    simp only [block]
    rw [wellLabelled_append]
    exact ⟨wellLabelled_climb _ _ _, by simp [WellLabelled, Event.Admissible]⟩

/-- The emitted tail is well labelled for ANY gate list and any starting labels. -/
theorem mtail_wellLabelled : ∀ (gs : List (TGate ι Fr K)) (l : ι → XLab ι Fr),
    WellLabelled (mtail gs l) l
  | [], _ => trivial
  | g :: gs, l => by
    simp only [mtail]
    rw [wellLabelled_append]
    exact ⟨wellLabelled_block g l, mtail_wellLabelled gs _⟩

/-- After the tail, a register sits at the frame of the last tail gate touching it; a register
touched by no tail gate keeps its label. -/
theorem labRun_mtail : ∀ (gs : List (TGate ι Fr K)) (l : ι → XLab ι Fr) (i : ι),
    labRun (mtail gs l) l i = ((lastFrame i gs).map XLab.frame).getD (l i)
  | [], _, _ => rfl
  | g :: gs, l, i => by
    simp only [mtail, lastFrame]
    rw [labRun_append, labRun_mtail gs _ i, labRun_block]
    cases lastFrame i gs with
    | some F => rfl
    | none => by_cases hi : i ∈ g.regs <;> simp [hi]

theorem labRun_mtail_last (gs : List (TGate ι Fr K)) (l : ι → XLab ι Fr) (i : ι) (U : Fr)
    (h : lastFrame i gs = some U) : labRun (mtail gs l) l i = .frame U := by
  rw [labRun_mtail, h]; rfl

omit [DecidableEq Fr] in
theorem posts_spec (term : ι → Fr) : ∀ (hs : List ι) (l : ι → XLab ι Fr), hs.Nodup →
    (∀ j ∈ hs, l j = .frame (term j)) →
    WellLabelled (posts (K := K) term hs) l ∧
      ∀ i, labRun (posts (K := K) term hs) l i = if i ∈ hs then .done i else l i
  | [], _, _, _ => ⟨trivial, fun _ => by simp [posts, labRun]⟩
  | j :: hs, l, hnd, hl => by
    have hj : j ∉ hs := (List.nodup_cons.1 hnd).1
    have hnd' : hs.Nodup := (List.nodup_cons.1 hnd).2
    have hl' : ∀ j' ∈ hs, Function.update l j (.done j) j' = .frame (term j') := by
      intro j' hj'
      have hne : j' ≠ j := fun h => hj (h ▸ hj')
      rw [Function.update_of_ne hne]; exact hl j' (List.mem_cons_of_mem _ hj')
    obtain ⟨ih1, ih2⟩ := posts_spec term hs (Function.update l j (.done j)) hnd' hl'
    refine ⟨⟨hl j List.mem_cons_self, ih1⟩, fun i => ?_⟩
    change labRun (posts (K := K) term hs) (Function.update l j (.done j)) i = _
    rw [ih2 i]
    by_cases hij : i = j
    · subst hij; simp [hj]
    · by_cases hi : i ∈ hs
      · simp [hi]
      · simp [hi, hij, Function.update_of_ne hij]

/-- **The terminal labels of hyperplane-ended helpers with a multi-gate tail.**  Let the word be
`a ++ mtail gs ++ b ++ posts term hs`, where `a` is well labelled, every helper `j` of the
(duplicate-free) list `hs` has its LAST tail gate at frame `term j` (any number of earlier tail
gates, as target or partner, at any frames), and the remaining cleanup `b` is well labelled and
never relabels a helper of `hs`.  Then the whole word is well labelled and every `j ∈ hs` ends at
`(done, j)`. -/
theorem hpe_labels_multi (term : ι → Fr) (hs : List ι) (hnd : hs.Nodup) (l : ι → XLab ι Fr)
    (a : List (Event ι (XLab ι Fr) K)) (gs : List (TGate ι Fr K)) (b : List (Event ι (XLab ι Fr) K))
    (ha : WellLabelled a l) (hlast : ∀ j ∈ hs, lastFrame j gs = some (term j))
    (hb : WellLabelled b (labRun (a ++ mtail gs (labRun a l)) l))
    (hmv : ∀ e ∈ b, ∀ j ∈ hs, ¬ e.moves j) :
    WellLabelled (a ++ mtail gs (labRun a l) ++ b ++ posts term hs) l ∧
      ∀ j ∈ hs, labRun (a ++ mtail gs (labRun a l) ++ b ++ posts term hs) l j = .done j := by
  set w := a ++ mtail gs (labRun a l) ++ b
  have hU : ∀ j ∈ hs, labRun w l j = .frame (term j) := by
    intro j hj
    simp only [w]
    rw [labRun_append, labRun_untouched b _ j (fun e he => hmv e he j hj), labRun_append,
      labRun_mtail_last gs _ j (term j) (hlast j hj)]
  have hwl : WellLabelled w l := by
    simp only [w]
    rw [wellLabelled_append, wellLabelled_append]
    exact ⟨⟨ha, mtail_wellLabelled gs _⟩, hb⟩
  obtain ⟨hp1, hp2⟩ := posts_spec (K := K) term hs (labRun w l) hnd hU
  refine ⟨(wellLabelled_append _ _ _).2 ⟨hwl, hp1⟩, fun j hj => ?_⟩
  rw [labRun_append, hp2 j, if_pos hj]

/-- The shipped single-gate tail (`Tail.tail`) is the one-gate `mtail` when both operands climb. -/
theorem tail_eq_mtail (h p : ι) (hp : h ≠ p) (Ah Ap U : Fr) (q : K) (l : ι → XLab ι Fr)
    (lh : l h = .frame Ah) (lp : l p = .frame Ap) (hAh : Ah ≠ U) (hAp : Ap ≠ U) :
    mtail [TGate.add h p U q] l = tail h p Ah Ap U q := by
  have c1 : climb (K := K) h U l = [.relabel h (.frame Ah) (.frame U)] := by
    simp [climb, lh, hAh]
  have c2 : climb (K := K) p U (labRun (climb (K := K) h U l) l) =
      [.relabel p (.frame Ap) (.frame U)] := by
    rw [labRun_climb]
    simp [climb, Function.update_of_ne (Ne.symm hp), lp, hAp]
  simp only [mtail, block, List.append_nil]
  rw [c2, c1]
  rfl

/-- **The single-gate word is the one-gate instance** of `hpe_labels_multi` (so the shipped
`hpe_labels` is a special case). -/
theorem hpe_labels_tail (h p : ι) (hp : h ≠ p) (Ah Ap U : Fr) (q : K) (l : ι → XLab ι Fr)
    (a b : List (Event ι (XLab ι Fr) K))
    (ha : WellLabelled a l) (lh : labRun a l h = .frame Ah) (lp : labRun a l p = .frame Ap)
    (hAh : Ah ≠ U) (hAp : Ap ≠ U)
    (hb : WellLabelled b (labRun (a ++ tail h p Ah Ap U q) l))
    (hmv : ∀ e ∈ b, ¬ e.moves h) :
    WellLabelled (a ++ tail h p Ah Ap U q ++ b ++ [.relabel h (.frame U) (.done h)]) l ∧
      labRun (a ++ tail h p Ah Ap U q ++ b ++ [.relabel h (.frame U) (.done h)]) l h = .done h := by
  have ht := tail_eq_mtail (K := K) h p hp Ah Ap U q (labRun a l) lh lp hAh hAp
  have hl : lastFrame h [TGate.add h p U q] = some U := by
    simp [lastFrame, TGate.regs, TGate.frame]
  rw [← ht] at hb ⊢
  have := hpe_labels_multi (fun _ => U) [h] (List.nodup_singleton h) l a [TGate.add h p U q] b ha
    (by simpa using hl) hb (by simpa using hmv)
  exact ⟨by simpa [posts] using this.1, by simpa [posts] using this.2 h List.mem_cons_self⟩

end Labels

/-- **Lemma A for every hyperplane-ended helper of a multi-gate word** (streams form).  Each helper
`j ∈ hs` starts at `(prew, j)`, has a unit row, and (N) for its pair `(ent j, term j)` with its own
`C j`; the word is `a ++ mtail gs ++ b ++ posts term hs` as in `hpe_labels_multi`.  Then each
helper's stream ends as `χ⁻¹ (C j ⊗ id) χ` of itself.  Nothing restricts `ent j` (cold: `ent j = ⊥`). -/
theorem hpe_word_multi {ι Fr K : Type*} [DecidableEq ι] [DecidableEq Fr] [CommSemiring K]
    {A B : Type*} [AddCommMonoid A] [Module K A] [AddCommMonoid B] [Module K B] [Fintype ι]
    {Fam G Cc W : Type*} [DecidableEq Fam] [Group G] [DecidableEq G]
    [AddCommMonoid W] [Module K W]
    (T : Fr → (A ⊗[K] B) ≃ₗ[K] (A ⊗[K] B)) (ent term : ι → Fr)
    (Lw Rw : Fr → Fr → (A ⊗[K] B) ≃ₗ[K] (A ⊗[K] B))
    (fam : ι → Fam) (σ : ι → G) (d : G)
    (fp : G → Set Cc) (hne : ∀ r, (fp (σ r)).Nonempty)
    (hdis : ∀ r r', r ≠ r' → fam r = fam r' → Disjoint (fp (σ r)) (fp (σ r')))
    (chart : ι → W ≃ₗ[K] (A ⊗[K] B)) (rec : XLab ι Fr → XLab ι Fr → A ⊗[K] B → A ⊗[K] B)
    (hs : List ι) (hnd : hs.Nodup) (l : ι → XLab ι Fr)
    (a : List (Event ι (XLab ι Fr) K)) (gs : List (TGate ι Fr K)) (b : List (Event ι (XLab ι Fr) K))
    (y : Fam × G → W)
    (ha : WellLabelled a l) (hlast : ∀ j ∈ hs, lastFrame j gs = some (term j))
    (hb : WellLabelled b (labRun (a ++ mtail gs (labRun a l)) l))
    (hmv : ∀ e ∈ b, ∀ j ∈ hs, ¬ e.moves j)
    (hrec : RecipesExact (Text T ent term Lw Rw) rec (a ++ mtail gs (labRun a l) ++ b ++ posts term hs))
    (hS : ∀ j ∈ hs, ∀ s, S (a ++ mtail gs (labRun a l) ++ b ++ posts term hs) j s =
      if s = j then 1 else 0)
    (hstart : ∀ j ∈ hs, l j = .prew j) (C : ι → A →ₗ[K] A)
    (hN : ∀ j ∈ hs, ∀ v, T (term j) ((T (ent j)).symm v) =
      Lw (ent j) (term j) ((C j).rTensor B (Rw (ent j) (term j) v))) :
    ∀ j ∈ hs, realizeRun ⟨streamOwner fam σ d, chart⟩ rec
        (a ++ mtail gs (labRun a l) ++ b ++ posts term hs) y (streamOwner fam σ d j) =
      (chart j).symm ((C j).rTensor B (chart j (y (streamOwner fam σ d j)))) := by
  intro j hj
  have hl := hpe_labels_multi term hs hnd l a gs b ha hlast hb hmv
  exact hpe_streams T ent term Lw Rw fam σ d fp hne hdis chart rec _ l y hrec hl.1 j (hS j hj)
    (hstart j hj) (hl.2 j hj) (C j) (hN j hj)


/-! ### The cold instance `E = ⊥` -/

/-- **(N) for a cold helper.**  If the entrance operator is the identity (`T_⊥ = id`, as
`clifford_exact.canonical_frame(n, ())` is) then (N) for `(⊥, U)` is just a monomial factorization
of `T_U` itself; e.g. `T_U = K⁻¹ (C ⊗ id) K`, which is how `canonical_frame` DEFINES `T_U`. -/
theorem exact_cold {K : Type*} [CommSemiring K] {A B : Type*} [AddCommMonoid A] [Module K A]
    [AddCommMonoid B] [Module K B] {Fr : Type*} (T : Fr → (A ⊗[K] B) ≃ₗ[K] (A ⊗[K] B)) (E U : Fr)
    (L R : (A ⊗[K] B) ≃ₗ[K] (A ⊗[K] B)) (C : A →ₗ[K] A)
    (hE : ∀ v, (T E).symm v = v) (hU : ∀ v, T U v = L (C.rTensor B (R v))) :
    ∀ v, T U ((T E).symm v) = L (C.rTensor B (R v)) := by
  intro v; rw [hE, hU]

/-- **Width of a cold hyperplane end** (frames of `F₂⁹`): `E = ⊥ ≤ U`, `dim U = 8` give width
`dim U - dim ⊥ = 8`, one spectator, and `U ≠ FULL`. -/
theorem cold_hyperplane_width (U : Frame) (hU : frameRank U = 8) :
    frameRank U - frameRank ⊥ = 8 ∧ 9 - (frameRank U - frameRank ⊥) = 1 ∧ U ≠ ⊤ ∧
      (⊥ : Frame) ≤ U := by
  have h0 : frameRank (⊥ : Frame) = 0 := by simp [frameRank]
  refine ⟨by omega, by omega, ?_, bot_le⟩
  rintro rfl
  have : frameRank (⊤ : Frame) = 9 := by
    simp [frameRank, finrank_top, Module.finrank_fin_fun]
  omega

end HyperplaneEnd
