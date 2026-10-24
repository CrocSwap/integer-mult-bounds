# Bounded-word recovery for actual cyclic Pauli ports

Given cyclic observations `v = (I + U/2)y`, with fixed role count W and phase-retaining Pauli routing U, this package constructs and executes an explicit inverse. It replaces a dense inverse oracle with a finite monomial/ADD program and implements every prescribed fixed-rational rounding using ordinary bounded-word operations, without a multiplication or division primitive.

The two constructive mechanisms are:

1. Compile the return monomial V = U^W and factor the finite inverse. At most W + q - 2 monomial/ADD passes suffice, where q = 2 for pure XOR routing and q = 4 for general quarter-phase Pauli routing. The inspected three-role and thirteen-role XOR ports use 3 and 13 passes, respectively. Absolute phases are retained.
2. Pack all binary-prefix remainders of one scalar into a constant number of ordinary bit-plane words. A doubling scan emits all quotient bits in O(log(2 + h)) Boolean/shift/add instructions at h-bit precision, for each fixed divisor. Signed floor, truncation and nearest ties to even are explicit. No MUL, DIV, remainder or table oracle is used.

For N TOTAL complex entries across the W roles, the combined fixed-W consumer costs O(W N log(2 + h)) instructions, with explicit fixed-denominator constants, O(W N) literal return-table preprocessing, and two owned full buffers for XOR or three for general phases. The observation arrays remain intact. The Python implementation additionally stores an O(N) routing table. [INTEGRATED-CASCADE-THEOREM.md](INTEGRATED-CASCADE-THEOREM.md) gives the quantifiers, address headroom and precision: error is at most 5 grid units against exact recovery of stored observations, or 6 including half-unit observation quantization, per real/imaginary component.

This also improves PR #4885's conservative fixed-rational recovery fallback from O(N h) to O(N log(2 + h)), under the declared both-logical-shifts Word RAM. [APPLICATIONS-NOTE.md](APPLICATIONS-NOTE.md) instantiates the exact-image odd divisions already priced by Ali Romman's PR #4733; those source constructions are credited premises, not newly replayed here.

**No new κ was obtained.** The actual paid producer of the favorable cyclic observations remains unproved. This is a sufficient consumer theorem and executable arithmetic implementation, not a complete supplier or multiplication theorem. The literal source couplers from #4818, #4819 and #4826 are authenticated and checked; their retained headers make large κ claims that this package does not endorse. No new κ follows from coupling matrices, their inverse or a favorable hypothetical producer bill. The selected main certificate remains unchanged.

## Reproduce

Python 3.10 or later, standard library only; no solver, Git, GPU, network or platform-specific executable is needed for direct replay. From this directory:

```sh
python3 -I -B verify_division.py
python3 -I -O -B verify_division.py
python3 -I -B cascade_free.py
python3 -I -O -B cascade_free.py
python3 -I -B verify.py
python3 -I -O -B verify.py
python3 -I -B preflight.py
```

From a repository checkout, `python3 -B scripts/research_package.py --package research/native-cyclic-recovery` runs the registered checks. Direct checks only read their files. Python Fraction arithmetic is used by the independent references and exact cascade certificate; the bounded-word scalar datapath itself is the explicitly instrumented Boolean/shift/add implementation in fixed_divisor.py. Operation counts are conservative emulation bounds, not cycle-accurate processor timings or a demonstrated practical speedup. Normal and optimized checks use explicit rejection, not assertions.

The division proof applies to every positive width with fixed guard widening and sufficient address space; finite tests cover widths through 4,096, 6,912 unsigned cases, 24,978 signed-rounding cases and 840 fixed-rational cases. Separate review adds 5,117 boundary cases. The cascade checker covers all 376 literal basis columns and 7,168 pinned coupler entries; independent review includes 144 additional fixtures and tensor-width phase controls. End-to-end checks compare rounded recovery with a distinct exact rational reference and reject a wrong recurrence sign. Separate optimized subprocess mutations also reject an incorrect prefix remainder offset, discarded return phases and a wrong final normalization denominator. These finite checks corroborate the written universal proofs, rather than replacing them.

## Scope and precedent

[CASCADE-INVERSE.md](CASCADE-INVERSE.md) proves the phase-preserving decoder. [DIVISION-PROOF.md](DIVISION-PROOF.md) proves the bounded-word scalar implementation. The exact Problem 1.8 Lean RAM derives right shift using DIV; both shifts are primitives in this contribution's explicitly different ABI. There is no claimed division-free compilation into that literal Lean instruction set. Inspected MathProof shift/division sources and DAG entries are source-only precedent, without a fresh kernel audit.

Credit hexapode's #4818/#4819/#4826 for the particular cyclic couplers, Clear1nsight's #4842 for full-cascade conditioning and the producer/admission distinction, Dugongue's #4743/#4885 for native-port and resonant recovery context, JoyboyBrian #4797 for the resonant channel and Nick Petalas #4825 for its width-four rank question, Ali Romman #4733 for concrete odd-division services, and the retained Yiyang / Lyy-iiis #4710, lee-phys #4688 and Jacob Alan Sussman #4628 lineage. Classical finite geometric series, Clifford/Pauli conjugation, Blelloch associative scan and invariant division are credited standard ingredients; no broad literature-priority claim is made. Prepared by Dugongue with substantial OpenAI Codex assistance from one lead and three workers. Root Apache-2.0 and every redistributed predecessor LICENSE/NOTICE are retained.

Canonical main was refreshed through a dedicated immutable checkpoint ref at 624de9dc66858af0945e5f8a0942488d62280d43, priority revision 7. Public PR bodies and relevant exact sources were inspected, including #4885 and successors; remote Discussion loading and sparse local notes provide incomplete overlap coverage. No worldwide novelty or exhaustive repository audit is claimed. Full source-history audit, hosted Linux CI, a Lean kernel audit, supplier admission and a practical full multiplier were not run. The authoritative MathProof DAG, frozen predecessor packages and selected frontier are unchanged.

## Open next questions

- Emit one named cyclic observation from independent original inputs with a chronological producer, paid Gaussian profile, retained owners and restoration. The inverse here supplies its consumer; it supplies no missing producer.
- Bind the entire producer/consumer word to an admitted native compiler and all nine outer rows. Count every call, monomial pass, buffer, phase, initialization, clearing and source error.
- Integrate the fixed-divisor routine into an executable native backend with the declared both-shifts ABI; compare actual instruction counts and crossover widths without substituting RAM instructions for tape head steps.
