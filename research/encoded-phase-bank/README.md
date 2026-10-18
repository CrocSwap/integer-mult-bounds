# Encoded bank dimension for open phase schedules

**Scoped mathematical audit and extension; no new kappa.** For the separated-label,
repeated-word contract in [PROOF.md](PROOF.md), changing from assigned Pauli bits
to arbitrary invertible complex matrices cannot compress a producer-prefix bank
below its weighted longest-increasing-subsequence bound. The minimum bank
dimension is exactly `2^W`; every valid dimension is divisible by `2^W`.

This extends Dennis / antunishdPursuit's [PR2859](https://github.com/CrocSwap/integer-mult-bounds/pull/2859)
from one assigned tensor bit per scalar column to arbitrary finite complex
representations and vector-label blocks. It also gives a necessary and sufficient
commutation criterion for **any paired schedule**, including interleaved producers
and consumers. An explicit five-cycle schedule needs dimension eight despite
having no three mutually crossing columns. The proof excludes dimension four
even for non-Pauli, nonunitary matrices. It does not claim that coloring is always
optimal on arbitrary crossing graphs.

The result closes a specific representation loophole in an open-state boundary.
It does not find a flaw in PR2859, improve the recursive invoice, or exclude a
different caller contract. Standard representation theory and permutation-order
arguments are credited, not claimed as new mathematics in themselves.

## Result and essential hypotheses

Each column j has independent labels `u_j,v_j in F2^r_j` and executes
`P_j(u,v)=B_j(v)A_j(u)` on the same arbitrary bank `C^d`. A and B are group
homomorphisms. Each column appears twice with identical operators and unchanged
labels. The desired endpoint on every bank state is
`(-1)^(sum u_j dot v_j) I_d`. No common Pauli basis, tensor factorization,
unitarity or irreducibility of the bank is assumed.

Two columns cross when their occurrences alternate. The full endpoint holds
exactly when the within-column generators have the prescribed anticommutation
and all four pairs of generator families commute across each crossing edge.
Nested columns need not commute. See the sparse-label necessity and pair-removal
sufficiency proofs in PROOF.md.

For producer order `0,...,f-1` followed by a consumer permutation pi, W is the
maximum sum of r_j along an increasing subsequence of pi. A weighted crossing
clique forces `2^W | d`; explicit coordinate intervals attain dimension `2^W`.
For unit weights this is PR2859's LIS optimum, now over arbitrary representations.
For `pi=(2,0,1)`, weights `(1,2,1)`, W=3: dimension eight works and dimension four
is impossible. Reversal has W=max r_j; identical orders have W=sum r_j.

The general paired word `0 1 4 0 3 4 2 3 1 2` has a five-cycle crossing graph.
With scalar labels it needs minimum dimension eight: a commutant argument
excludes four, and a three-bit construction attains eight. Thus the clique
lower bound need not be attained outside the producer-prefix class. We do not
classify all larger valid dimensions for C5.

Separated-label dependence is essential. If it is removed, the scalar choice
`P_j(u,v)=i^(u dot v)` solves every paired schedule at dimension one. It already
performs the desired quadratic phase, so is not a free implementation or a
favorable supplier bill. The theorem also excludes prepared-state-only equality,
discarded lanes, changing operators between occurrences, and extra operations
not included in the paired word.

## Reproduce and evidence

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/encoded-phase-bank
```

Expected markers: `PASS_ENCODED_PHASE_BANK`,
`PASS_INDEPENDENT_ENCODED_BANK_MATRICES`, `PASS_ENCODED_BANK_PACKAGE_CONTROLS`,
and `PASS_REGISTERED_RESEARCH_PACKAGE`. Direct scripts work from a Git-free
copy. Ordinary replay is read-only. `--emit` prints a receipt for deliberate
comparison, without overwriting committed evidence.

- `verify.py`: all **139,434** combinations of canonical paired schedules
  with f<=4 and all six ordered one-bit anticommuting Pauli frames per column;
  **124** schedules. A literal Z/4 polynomial interpreter tracks prefix
  translations and every incoming-bank label independently of the crossing
  formula. All terms, not just acceptance booleans, agree.
- Two-bit coverage: one seeded general symplectic encoding for each of all
  **11,464** canonical schedules with 1<=f<=6, using seed 70. Encodings are
  sampled, not exhausted; the stopping rule is completion of these schedules.
- Weighted prefix coverage: **31,287** permutation/weight cases for 1<=f<=5,
  weights in {0,1,2}. Independent subset enumeration checks the maximum chain;
  every constructed coordinate and crossing disjointness condition is checked.
  This tests the combinatorial premises, not all complex representations.
- The complete two-bit symplectic census has 20 nondegenerate planes, whose
  orthogonality graph is ten disjoint edges. This corroborates the C5 exclusion
  within that finite subclass; PROOF.md establishes the general GL exclusion.
- `independent.py` imports neither verifier nor predecessor. Exact Fraction
  matrix actions check all **10,784 joint label/bank columns**, comprising
  **84,032 endpoint coefficients**, in five fixtures. They include non-Pauli
  noncommuting nested matrices, dense nonunitary conjugations, vector-label
  blocks, an interleaved path and the complete C5 construction. These are bank
  matrices at fixed Fourier labels, not a native physical C/Q compiler replay.
- Nine symbolic and five matrix controls cover invalid order, diagonal pairing,
  missing consumers, dropped cross terms and malformed schedules. The d=1
  joint-label escape checks all 1,024 label assignments of a five-column case.
  Package tests reject source/receipt changes and check optimized, relocated,
  Git-free, read-only execution. Finite checks support the written all-size
  proof; they are not a proof-assistant formalization.

Exact scientific base: `066766afb181a421eb851b8d73bb0ba71a78a170`.
[SOURCES.json](SOURCES.json) pins base provenance; [REFERENCES.json](REFERENCES.json)
pins the two verbatim predecessor READMEs by original commit, Git blob and SHA256.
Their bytes were retrieved and authenticated at entry and are checked locally
on replay. No predecessor mathematical code is imported or executed. Reference
checking does not certify their other scientific claims. [TASK.json](TASK.json)
records the three candidates, selection, overlap scope and stopping decision.

## Cost boundary and family decision

**Narrow / stop.** This is a bank-dimension audit, not another construction round
in an unchanged native alphabet. A d-dimensional bank has d arbitrary lanes,
all of which remain part of the operand. The bound is on d, not coefficient
precision or a supplier's recursive rank. Even its attained coordinate
construction requires pricing all A/B implementations, encoding, access,
scheduling, movement, restoration and precision at an actual caller. General
conjugating matrices can be expensive and are only correctness fixtures here.
Unknown implementation costs are not zero.

We neither reprice PR2850's complete C/Q recurrence nor remove its support gate.
PR2859's 4f C-call count for its literal unfused word is not promoted into a
lower bound for all implementations. No native or full supplier admission,
selected cold replay, new multiplication exponent, or unconditional theorem
about integer multiplication is claimed. The selected record is unchanged.

## Open next questions

An actual caller seeking fewer bank lanes must change a proved hypothesis:
permit a paid joint-label operation, change the repeated-word contract, or
admit a different endpoint. First write the smallest f=2 caller and full paid
encoding/consumer recurrence, then check arbitrary inputs at two parent levels.
The blocker is a favorable native implementation, not another choice of bank
basis under the contract proved here. The general crossing-graph representation
problem remains mathematically open here, but is not proposed as a supplier
optimization without such a caller. Structured details are in TASK.json.

## Credit and disclosure

Gareth Davidson / bitplane's PR2850 supplies the phase accumulator, reverse-order
positive control, closed-commutator dimension proof, native recurrence and
failed-budget handoff. Dennis / antunishdPursuit's PR2859 supplies the
producer-prefix crossing-phase formula and assigned-bit LIS theorem.
Both remain credited through their unmodified reference READMEs. The
eigenspace, commutant and weighted-poset arguments use standard linear algebra;
the contribution is the precise extension to arbitrary bank representations,
the general paired-schedule criterion, its sharp weighted consequence and
C5 scope witness, with separate executable checks.

Pre-submission overlap found Dugongue's concurrent
[PR2871](https://github.com/CrocSwap/integer-mult-bounds/pull/2871), head
`894a3edbcd90fc379a277eb07a5ae2b706c7a8e1`. Its P006 gives a vector-control
crossing formula with an added correction, and P056 gives a sufficient
odd-incidence encoded-bank construction. Those formulations retain their
credit. The present result adds necessity and sharp weighted dimension over
arbitrary GL(V) representations under the unchanged paired-word contract,
including all four cross-family relations and the C5 commutant obstruction.
The inspected overlap statements are recorded in TASK.json; they are context,
not executable or mathematical dependencies of this proof.

Prepared by **Tekalign (@tekuuu), with substantial OpenAI Codex assistance** in
derivation, implementation, source inspection, verification and writing. Both
implementations have the same AI-assisted author; no subagents, independent
human review, or formal-kernel proof is claimed. New work and retained source
references are Apache-2.0, with predecessor notices preserved. The repository
root LICENSE applies.
