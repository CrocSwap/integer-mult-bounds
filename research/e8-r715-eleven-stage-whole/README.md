# R715: an E8 bit word at the carrier lower bound, eleven stages, whole-residual hosting

**Bit supplier (exact, eleven stages, PR #442 whole-residual hosting, no cross-family split, target mixing):
c = 642564369945714399381/500000000000000000000000 ≈ 1.28513·10⁻³**, +0.74% over PR #454's bit endpoint (1.275658·10⁻³) and +1.33% over the same pipeline on
PR #443's R740 word. With the complex supplier cited here (PR #442, b = 1.267453·10⁻³) κ is complex-bound; the bit supplier alone
supports κ_bit ≈ 1.28348·10⁻³ (+1.34% over PR #456, the best whole-residual claim at submission). **Pending: a complex supplier
above ~1.2855·10⁻³ is needed for κ to reach the bit value; drop it in with `--complex-upstream=DIR` (PR #442 layout).**

## What is new
1. **A lower bound on carriers, met.** In any word of this format a source x_s whose copies first act above its own line
   frame serves only targets in a hyperplane section of s^⊥ (Thm A). The 63 lines of E7 = s^⊥ form a spherical 4-design,
   Σ_r ⟨r,u⟩²⟨r,v⟩² = 16(|u|²|v|² + 2⟨u,v⟩²) > 0, so no two hyperplanes contain them: every source needs ≥ 3 registers, i.e.
   **≥ 2 carriers per source (240)**. The same lemma gives ≥ 2 helpers reaching every target hyperplane (240, met by #370).
   PR #370's word spends 272 carriers: the eight frame lines 2e_m are added to the D4 sums of seven blocks each (7 chains).
2. **Frame-pair D4 sums** reach the bound: D4(c) = Bcw[c] + FP(a,b) + FP(c,d), FP = 2e_a + 2e_b at frame ⟨e_a,e_b⟩, with the 12
   pairs of the three parallel classes of one block (an AG(3,2) direction plane), so every block splits inside the set.
   Carriers 272 → 240, FP copies +16: R 740 → 724 after PR #443's reuse.
3. **Eleven cancelling re-expressions** (a rule w re-expressed as x ⊕ y of existing symbols, overlap cancelling inside w's
   frame, Thm A respected): R 724 → 715.
4. **Kernel rebuild** for a new word (PR #443's replica kernel, deterministic elimination search, coordinate entrances), and
   **target mixing generalised to chained receivers** (a donor that is itself a receiver): frame-0 preconditioners
   receiver-before-donor, scatter XOR with the donor's original scatter; on words without chains (PR #450) it is the
   unchanged rule, reproducing #450's mixed word byte for byte. Four mutants rejected.

## Checks (verify.py)
PR #443 parent verifier; hierarchy legality (content = kid sum, frames contain kids' frames and contents, every target's reads
sum to its 63 in-cap lines inside its hyperplane); PR #370 compile/fullword, PR #443 reuse/retime regenerate the word;
PR #370's independent all-column checker and mutants; kernel rebuild with PR #443's exact replay and interface check;
C++ cohort legality, five- and eleven-stage formal columns (R = 715), record mutants, Gram; mixing check with 4 mutants;
eleven-stage geometry, parent template and audit, whole-residual hosting (frozen selection; `--discover-check` recomputes it with
HiGHS), hosted audit, both rational moments, invoice, bootstrap and 47 strict outer inequalities.

## Scope
Conditional like its parents (inherited compiler/dirty-helper/precision/analytic assumptions, PR #450's Lemma M for the bit
target mixing). No cross-copy hosting lemma is used. No unconditional theorem or Lean proof is claimed.
