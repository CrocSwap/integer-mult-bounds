/-
Shadow .  See Shadow.md.  internal notes (SHADOW lemma), AUDIT7.md, R8.md.

For every word, the TWIN replaces each main r (birth b, end c, route steps) by
  * a single-jump main  ⟨b, c, [(b, c)]⟩, and
  * a fresh helper g = ⟨b, c, steps⟩ (born at b, ends at c) that runs the main's old route,
the two swapped at b and swapped back at c by gates (ADD/SCALE: not invoiced).
Part A (row level): the 4-gate swap and swap-back are exact swaps; so the final rows are unchanged
        (main = old final row, g = its own unit row).
Part B (invoice, on FibreK's nativeInv): hypothesis P0-symmetry (a climb d on T and a MOVE of gap d on P carry the same
        histogram: the D0 table, and the pricekit rank of both is d).  Then the twin has the same NET count
        cnt T r - cnt P r at every rank r (so same S, F(t), D0, kappa), but the RAW T and P histograms each gain the
        common summand `mains.flatMap (tT (e-b))` (AUDIT7: that is why the interval gate, which counts invoiced T events,
        fails on the full twin).
Part C: the twin's mains make a single jump (0 interior stops); no law that depends only on net invoice + F + finals
        can force a main stop on a word of M, provided M is closed under the twin (replay/ascent legality: [C], not formalised).
Kernel only.
-/
import Nov15.FibreK

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace Shadow
open FibreK CallerCost

/-! ### Part A: the gates -/
section Gates
variable {R M : Type*} [Ring R] [AddCommGroup M] [Module R M]

/-- birth swap on (main row r, helper row g): ADD g += r ; ADD r -= g ; ADD g += r ; SCALE r by -1. -/
def swapIn (p : M × M) : M × M :=
  let g1 := p.2 + p.1
  let r1 := p.1 - g1
  let g2 := g1 + r1
  (-r1, g2)

/-- end swap-back: ADD r += g ; ADD g -= r ; ADD r += g ; SCALE g by -1. -/
def swapOut (p : M × M) : M × M :=
  let r1 := p.1 + p.2
  let g1 := p.2 - r1
  let r2 := r1 + g1
  (r2, -g1)

theorem swapIn_eq (r g : M) : swapIn (r, g) = (g, r) := by
  simp only [swapIn, Prod.mk.injEq]; constructor <;> abel

theorem swapOut_eq (r g : M) : swapOut (r, g) = (g, r) := by
  simp only [swapOut, Prod.mk.injEq]; constructor <;> abel

/-- the final rows: at birth r holds e_r, g holds e_g.  After swapIn: r holds e_g, g holds e_r.  g then runs the main's
old program and ends with ρ (the main's old final row); r (single jump, never gated) still holds e_g.
After swapOut: r holds ρ (the old final row), g holds e_g (its own unit row). -/
theorem final_rows (er eg ρ : M) :
    (swapIn (er, eg)).1 = eg ∧ (swapIn (er, eg)).2 = er ∧ swapOut ((swapIn (er, eg)).1, ρ) = (ρ, eg) := by
  refine ⟨?_, ?_, ?_⟩ <;> simp [swapIn_eq, swapOut_eq]

end Gates

/-! ### Part B: invoice -/

/-- contribution of one register to F. -/
noncomputable def hc (tb : Table) (h : Helper) (t : ℝ) : ℝ :=
  Fh (tb.tT (h.e - h.b)) t - (h.steps.map fun s => Fh (tb.tP (gap s)) t).sum

theorem sum_map_sub' {α : Type*} (l : List α) (a b : α → ℝ) :
    (l.map fun h => a h - b h).sum = (l.map a).sum - (l.map b).sum := by
  induction l with
  | nil => simp
  | cons x l ih => simp [ih]; ring

/-- F of the native, register by register. -/
theorem Fi_native (E : Inv) (tb : Table) (H : List Helper) (t : ℝ) :
    Fi (nativeInv E tb H) t = Fi E t + (H.map fun h => hc tb h t).sum := by
  have e := K_word E tb H t
  rw [e]
  simp only [FK, Ssum, PiW, Multiset.map_coe, Multiset.sum_coe, hc, sum_map_sub', sum_flatMap_map, List.map_map, Function.comp_def]
  ring

/-- A word: ends `E` (invariant), mains, helpers, and final data `fin` (final rows). -/
structure Word (Φ : Type*) where
  E : Inv
  mains : List Helper
  helpers : List Helper
  fin : Φ

def Word.regs {Φ : Type*} (w : Word Φ) : List Helper := w.mains ++ w.helpers
def Word.inv {Φ : Type*} (tb : Table) (w : Word Φ) : Inv := nativeInv w.E tb w.regs

/-- interior stops of mains = (route length - 1). -/
def Word.mainStops {Φ : Type*} (w : Word Φ) : ℕ := (w.mains.map fun m => m.steps.length - 1).sum

def shadowOf (m : Helper) : Helper := ⟨m.b, m.e, [(m.b, m.e)]⟩

/-- the TWIN. -/
def Word.shadow {Φ : Type*} (w : Word Φ) : Word Φ :=
  ⟨w.E, w.mains.map shadowOf, w.helpers ++ w.mains, w.fin⟩

/-- P0 symmetry on the mains: births before ends and a climb d on T has the same histogram as a MOVE of gap d on P. -/
def Sym {Φ : Type*} (tb : Table) (w : Word Φ) : Prop :=
  ∀ m ∈ w.mains, m.b ≤ m.e ∧ tb.tT (m.e - m.b) = tb.tP (m.e - m.b)

theorem gap_shadow (m : Helper) (hb : m.b ≤ m.e) : gap (m.b, m.e) = m.e - m.b := by
  simp only [gap]; omega

theorem shadow_stops {Φ : Type*} (w : Word Φ) : w.shadow.mainStops = 0 := by
  simp [Word.mainStops, Word.shadow, shadowOf, List.map_map, Function.comp_def]

theorem sum_congr_mem {α : Type*} (l : List α) (f g : α → ℝ) (h : ∀ x ∈ l, f x = g x) :
    (l.map f).sum = (l.map g).sum := by
  induction l with
  | nil => simp
  | cons x l ih =>
    simp only [List.map_cons, List.sum_cons]
    rw [h x (by simp), ih (fun y hy => h y (by simp [hy]))]

/-- **SHADOW (F).**  the twin has exactly the same F(t). -/
theorem shadow_F {Φ : Type*} (tb : Table) (w : Word Φ) (hs : Sym tb w) (t : ℝ) :
    Fi (w.shadow.inv tb) t = Fi (w.inv tb) t := by
  unfold Word.inv Word.regs Word.shadow
  simp only
  rw [Fi_native, Fi_native]
  simp only [List.map_append, List.sum_append, List.map_map]
  have h2 : (w.mains.map fun m => Fh (tb.tT (m.e - m.b)) t - Fh (tb.tP (m.e - m.b)) t).sum = 0 := by
    have : ∀ m ∈ w.mains, (Fh (tb.tT (m.e - m.b)) t - Fh (tb.tP (m.e - m.b)) t) = (fun _ => (0:ℝ)) m := by
      intro m hm; simp only [(hs m hm).2, sub_self]
    rw [sum_congr_mem _ _ _ this]; simp
  have h3 : (w.mains.map ((fun h => hc tb h t) ∘ shadowOf)).sum = 0 := by
    have : ∀ m ∈ w.mains, ((fun h => hc tb h t) ∘ shadowOf) m = (fun m => Fh (tb.tT (m.e - m.b)) t - Fh (tb.tP (m.e - m.b)) t) m := by
      intro m hm
      obtain ⟨hb, _⟩ := hs m hm
      simp [Function.comp, hc, shadowOf, gap_shadow m hb]
    rw [sum_congr_mem _ _ _ this]; exact h2
  rw [h3]; ring

/-- the twin's invoice in the caller form. -/
theorem shadow_invoice_F {Φ : Type*} (tb : Table) (w : Word Φ) (hs : Sym tb w) (c : Inv) (L : ℕ) (t : ℝ) :
    Fi (invoice c (w.shadow.inv tb) L) t = Fi (invoice c (w.inv tb) L) t := by
  rw [Fi_invoice, Fi_invoice, shadow_F tb w hs]

/-- kappa (a root of the invoice F) is the same. -/
theorem shadow_root {Φ : Type*} (tb : Table) (w : Word Φ) (hs : Sym tb w) (c : Inv) (L : ℕ) (κ : ℝ) :
    IsRoot (Fi (invoice c (w.shadow.inv tb) L)) κ ↔ IsRoot (Fi (invoice c (w.inv tb) L)) κ := by
  unfold IsRoot
  rw [shadow_invoice_F tb w hs]

/-- D0 for the D0 table: equal as well (the table is symmetric). -/
theorem shadow_D0 {Φ : Type*} (w : Word Φ) (hb : ∀ m ∈ w.mains, m.b ≤ m.e) :
    Dinv (w.shadow.inv d0Table) = Dinv (w.inv d0Table) := by
  unfold Word.inv Word.regs Word.shadow
  simp only
  rw [d0_native, d0_native]
  simp only [List.map_append, List.sum_append, List.map_map]
  have h0 : (w.mains.map ((fun h : Helper => (fL (h.e - h.b) - (h.steps.map fun s => fL (gap s)).sum)) ∘ shadowOf)).sum = 0 := by
    have : ∀ m ∈ w.mains, ((fun h : Helper => (fL (h.e - h.b) - (h.steps.map fun s => fL (gap s)).sum)) ∘ shadowOf) m
        = (fun _ => (0:ℝ)) m := by
      intro m hm
      simp [Function.comp, shadowOf, gap_shadow m (hb m hm)]
    rw [sum_congr_mem _ _ _ this]; simp
  rw [h0]; ring

/-- count of rank r in a histogram is additive. -/
theorem cnt_append (l m : Hist) (r : ℕ) : cnt (l ++ m) r = cnt l r + cnt m r := by
  simp [cnt, List.map_append, List.sum_append]

/-- net count at rank r. -/
def net (i : Inv) (r : ℕ) : ℤ := (cnt i.T r : ℤ) - cnt i.P r

/-- **SHADOW (net histogram).** the signed histogram cnt T r - cnt P r of the twin equals the original's at every rank:
the raw T and P histograms each gain the common summand `A` (below), which cancels. -/
theorem shadow_net {Φ : Type*} (tb : Table) (w : Word Φ) (hs : Sym tb w) (r : ℕ) :
    net (w.shadow.inv tb) r = net (w.inv tb) r := by
  unfold net Word.inv Word.regs Word.shadow nativeInv
  simp only [List.flatMap_append, List.flatMap_map, cnt_append]
  have hT : ∀ m ∈ w.mains, tb.tT (m.e - m.b) = tb.tP (m.e - m.b) := fun m hm => (hs m hm).2
  have hA : (w.mains.flatMap fun m => (shadowOf m).steps.flatMap fun s => tb.tP (gap s)) =
      w.mains.flatMap fun m => tb.tT (m.e - m.b) := by
    apply List.flatMap_congr
    intro m hm
    simp [shadowOf, gap_shadow m (hs m hm).1, hT m hm]
  have hB : (w.mains.flatMap fun m => tb.tT ((shadowOf m).e - (shadowOf m).b)) =
      w.mains.flatMap fun m => tb.tT (m.e - m.b) := by
    apply List.flatMap_congr; intro m hm; simp [shadowOf]
  rw [hA, hB]
  push_cast
  ring

/-- the RAW T histogram of the twin = the original's T plus `A` (the gate caveat: the twin pays more invoiced T events). -/
theorem shadow_T_raw {Φ : Type*} (tb : Table) (w : Word Φ) :
    (w.shadow.inv tb).T = (w.inv tb).T ++ w.mains.flatMap (fun m => tb.tT (m.e - m.b)) := by
  unfold Word.inv Word.regs Word.shadow nativeInv
  simp only [List.flatMap_append, List.flatMap_map, List.append_assoc]
  have hB : (w.mains.flatMap fun m => tb.tT ((shadowOf m).e - (shadowOf m).b)) =
      w.mains.flatMap fun m => tb.tT (m.e - m.b) := by
    apply List.flatMap_congr; intro m hm; simp [shadowOf]
  rw [hB]

/-! ### Part C: no law forces a main stop -/

/-- **COROLLARY.**  `law` sees only the net signed histogram, the function F, and the final data.  `M` is the model
(any predicate closed under the twin: the replay / ascent / ledger legality of the twin is [C] r7shadow.py, not
formalised here).  If every word of M satisfying `law` has ≥ 1 main stop, then no word of M with symmetric mains satisfies `law`. -/
theorem no_law_forces_main_stop {Φ : Type*} (tb : Table) (M : Word Φ → Prop) (hM : ∀ w, M w → M w.shadow)
    (law : (ℕ → ℤ) → (ℝ → ℝ) → Φ → Prop)
    (hforce : ∀ w, M w → law (net (w.inv tb)) (Fi (w.inv tb)) w.fin → 1 ≤ w.mainStops)
    (w : Word Φ) (hw : M w) (hs : Sym tb w) : ¬ law (net (w.inv tb)) (Fi (w.inv tb)) w.fin := by
  intro hl
  have hnet : net (w.shadow.inv tb) = net (w.inv tb) := funext (shadow_net tb w hs)
  have hF : Fi (w.shadow.inv tb) = Fi (w.inv tb) := funext (shadow_F tb w hs)
  have hl' : law (net (w.shadow.inv tb)) (Fi (w.shadow.inv tb)) w.shadow.fin := by rw [hnet, hF]; exact hl
  have := hforce w.shadow (hM w hw) hl'
  rw [shadow_stops] at this
  omega

#print axioms shadow_F
#print axioms shadow_net
#print axioms shadow_D0
#print axioms shadow_T_raw
#print axioms no_law_forces_main_stop
#print axioms final_rows

end Shadow
