import NormalizedCostEnvelope

/-!
Source-only propagation of normalized-cost boundedness by child descent.
UNCOMPILED. This imports the independently source-reviewed envelope lemma;
that predecessor is itself uncompiled.

A finite list of base widths does not mean a finite collection of physical
states. At every base width, a uniform bound over the entire admissible
normalized-cost family is explicitly required. Individual terminating runs
or individually finite costs do not provide that bound.

Above the threshold, actual child widths are strictly smaller and positive.
Nat.strong_induction_on propagates BddAbove, using the genuine envelope_step
derived from the full physical decomposition. This induction proves only
boundedness; it does not duplicate the preserved RoundedRecurrence power
bound or assume its scalar-recurrence premise.

Scientific context remains PR1094 at
ce7ad1b6ab09452c3478723a2e96ed5ff212dc08, author-checked selected outer
kappa = 836330098538459/500000000000000000. No selected physical caller,
base-family supplier, precision, full overhead constant, runtime object or
final multiplication theorem is instantiated here. The native exponent
1-bCurrent remains distinct from outer kappa.

Attribution: NormalizedCostEnvelope and the reviewed PR1379 normalization
map; preserved ranked-pair RoundedRecurrence work; Mathlib completeness and
Lean's natural-number strong induction. Apache-2.0. OpenAI assistance.
-/

set_option Elab.async false

namespace NormalizedCostEnvelopeDescent
open scoped BigOperators
open NormalizedCostEnvelope

variable {State ι : Type*}

/-- One width/state-uniform complete physical cost contract. The child
selection may depend on all parent-state data. Every actual selected copy
must be admissible and have the exact positive parent/W volume ratio.
No normalized recurrence or rate bound occurs in this definition. -/
def PhysicalCostDecomposition (s : Finset ι) (multiplicity : ι → ℕ)
    (admissible : ℕ → State → Prop) (cost volume : State → ℝ)
    (childWidth : ℕ → ι → ℕ) (W C : ℝ) (N : ℕ) : Prop :=
  ∀ n, N < n → ∀ x, admissible n x →
    ∃ child : ι → ℕ → State,
      (∀ r ∈ s, ∀ j ∈ Finset.range (multiplicity r),
        admissible (childWidth n r) (child r j) ∧
        volume (child r j) = volume x / W) ∧
      cost x ≤ C * volume x +
        ∑ r ∈ s, ∑ j ∈ Finset.range (multiplicity r), cost (child r j)

/-- Uniformly bounded positive base-width families and genuine child descent
suffice to establish boundedness at EVERY positive width. No global family
majorant, attained maximum, scalar recurrence or exponent bound is assumed.
The complete physical cost contract and the finite base-family bounds are
independent supplied obligations, not established implementation facts. -/
theorem bounded_rates_of_base_and_descent
    (s : Finset ι) (multiplicity : ι → ℕ)
    (admissible : ℕ → State → Prop) (cost volume : State → ℝ)
    (childWidth : ℕ → ι → ℕ) (W C : ℝ) (N : ℕ)
    (hW : 0 < W)
    (hne : ∀ n, 0 < n → ∃ x, admissible n x)
    (hvolume : ∀ n, 0 < n → ∀ x, admissible n x → 0 < volume x)
    (hbase : ∀ n, 0 < n → n ≤ N →
      BddAbove (rates admissible cost volume n))
    (hdescent : ∀ n, N < n → ∀ r ∈ s,
      0 < childWidth n r ∧ childWidth n r < n)
    (hphysical : PhysicalCostDecomposition s multiplicity admissible cost volume
      childWidth W C N) :
    ∀ n, 0 < n → BddAbove (rates admissible cost volume n) := by
  intro n
  induction n using Nat.strong_induction_on with
  | h n ih =>
    intro hn
    by_cases hsmall : n ≤ N
    · exact hbase n hn hsmall
    · have hlarge : N < n := Nat.lt_of_not_ge hsmall
      have hchild_bdd : ∀ r ∈ s,
          BddAbove (rates admissible cost volume (childWidth n r)) := by
        intro r hr
        obtain ⟨hpos, hlt⟩ := hdescent n hlarge r hr
        exact ih (childWidth n r) hlt hpos
      exact (envelope_step s multiplicity admissible cost volume n
        (childWidth n) W C hW (hne n hn) (hvolume n hn)
        hchild_bdd (hphysical n hlarge)).1

/-- The actual least-upper-bound sequence now exists at every positive
width and satisfies the desired scalar recurrence. This is obtained from
the finite base-family/decomposition/descent inputs, rather than added as
a premise. The existing all-width power theorem can subsequently consume
this recurrence only with its separate base, threshold, strict-moment and
rounding/additive-cost budget hypotheses. -/
theorem envelope_family_of_base_and_descent
    (s : Finset ι) (multiplicity : ι → ℕ)
    (admissible : ℕ → State → Prop) (cost volume : State → ℝ)
    (childWidth : ℕ → ι → ℕ) (W C : ℝ) (N : ℕ)
    (hW : 0 < W)
    (hne : ∀ n, 0 < n → ∃ x, admissible n x)
    (hvolume : ∀ n, 0 < n → ∀ x, admissible n x → 0 < volume x)
    (hbase : ∀ n, 0 < n → n ≤ N →
      BddAbove (rates admissible cost volume n))
    (hdescent : ∀ n, N < n → ∀ r ∈ s,
      0 < childWidth n r ∧ childWidth n r < n)
    (hphysical : PhysicalCostDecomposition s multiplicity admissible cost volume
      childWidth W C N) :
    (∀ n, 0 < n → BddAbove (rates admissible cost volume n)) ∧
    (∀ n, 0 < n →
      IsLUB (rates admissible cost volume n) (envelope admissible cost volume n)) ∧
    (∀ n, N < n → envelope admissible cost volume n ≤ C +
      ∑ r ∈ s, ((multiplicity r : ℝ) / W) *
        envelope admissible cost volume (childWidth n r)) := by
  have hbdd := bounded_rates_of_base_and_descent s multiplicity admissible
    cost volume childWidth W C N hW hne hvolume hbase hdescent hphysical
  refine ⟨hbdd, ?_, ?_⟩
  · intro n hn
    exact envelope_isLUB admissible cost volume n (hne n hn) (hbdd n hn)
  · intro n hn
    have hnpos : 0 < n := Nat.zero_lt_of_lt hn
    have hchild_bdd : ∀ r ∈ s,
        BddAbove (rates admissible cost volume (childWidth n r)) := by
      intro r hr
      exact hbdd (childWidth n r) (hdescent n hn r hr).1
    exact (envelope_step s multiplicity admissible cost volume n
      (childWidth n) W C hW (hne n hnpos) (hvolume n hnpos)
      hchild_bdd (hphysical n hn)).2.2

end NormalizedCostEnvelopeDescent

#print axioms NormalizedCostEnvelopeDescent.bounded_rates_of_base_and_descent
#print axioms NormalizedCostEnvelopeDescent.envelope_family_of_base_and_descent
