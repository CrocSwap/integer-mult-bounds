# Bounded-residue Gaussian Newton validator

**Exact verifier improvement; no new kappa.** Membership in the P104 Gaussian
Newton lattice B_r depends only on each component modulo `2^ceil(r/2)`. The
validator uses a modular Boolean difference transform and returns a failing
mask with checked residues. This modulus is sharp among common power-of-two
component moduli. At the actual nine-axis boundary, only **five residue bits
per component** are needed, even for thousands-bit coefficients.

The [proof](PROOF.md) retains the existing lattice and states the all-rank
criterion, sharpness, input cost and limits. [membership.py](membership.py)
provides `member(values)` and `obstruction(values)`. Inputs are nonempty
power-of-two lists of Gaussian integer pairs. No source file is changed.
[RESULT.json](RESULT.json) records exact decisions and literal prefix evidence.
[BENCHMARK.json](BENCHMARK.json) gives matched local timings; run
[benchmark.py](benchmark.py) explicitly to repeat them. Timing is not acceptance. On CPython 3.12.13, five alternating samples of
100 calls gave median membership speedups of 4.37x, 3.70x, 6.44x and 23.71x
for coefficient widths 14, 129, 1025 and 8065 bits. Both paths receive the
same accepted array. These measurements include their respective input
validation and exclude input encoding; they are not whole-collector timings.

## Replay

Use standard-library CPython 3.12 from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/newton-bounded-residue-validator
python3.12 -I -O -B research/newton-bounded-residue-validator/benchmark.py
```

Expected scientific status: `PASS_NEWTON_BOUNDED_RESIDUE_VALIDATOR_NO_NEW_KAPPA`.
Normal and optimized checks compare the unchanged Gaussian decoder, a separate
subset-sum oracle and the new modular method. They include all binary Gaussian
arrays through rank two, all 65536 real residue arrays at rank three, large
signed coefficients through 8065 bits, and 96 actual collector prefix checks.
Fifteen controls cover sharpness, odd pi parity and malformed inputs. Source
hashes and typed receipt equality are mandatory. The official export permits
replay without Git or network.

This does not reconstruct coefficient words or prepare an admitted entrance.
Input reading, physical access/movement, a complete validation scan and actual
caller admission are separate. The full P104 word, selected cold replay, Lean,
Docker and a physical supplier were not run. No human or kernel review is
claimed. Source finite-reference limits apply only to differential fixtures.

## Scope and credit

Base `7c472563474e60185e6ca101a17622133d047e56`, priority revision 7.
[SOURCES.json](SOURCES.json) pins all consumed bytes. The card is changed from
P104 side correction to exact entrance validation, as [TASK.json](TASK.json)
records. The obsolete card baseline failed at missing `bit_lower`; the
current `research_selected_baseline.py` passed. No selected file was changed.

Clear1nsight's [PR #3382](https://github.com/CrocSwap/integer-mult-bounds/pull/3382)
supplies B_r, its exact decoder, literal collector reference and source lineage.
Credit ywz65's [PR #2586](https://github.com/CrocSwap/integer-mult-bounds/pull/2586)
word, Arham Tahir's retained collector, Tekalign's
[PR #3025](https://github.com/CrocSwap/integer-mult-bounds/pull/3025) pair and
Ross Richardson's phase-domain work. The full source notes retain their credit.
The older Newton entrance and period residue-reducer results remain separate;
this changes the membership algorithm, not their scientific contracts.

Ali Romman with substantial OpenAI Codex assistance; new work Apache-2.0.

## Open next questions

Use the validator in a reviewed consumer that needs only membership, retaining
its original input limits and diagnostics where those are public contracts.
A physical validation scan still needs its complete input, memory, movement
and cleanup bill. Neither faster local checks nor fewer residue bits makes
that paid caller or the producer entrance free.
