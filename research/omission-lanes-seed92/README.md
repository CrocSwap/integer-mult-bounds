# Packed literal replay for the R439 omission atlas

**Production note:** `research/omission-lanes-production/` wires packed lanes into
production `research/r439-omission-atlas-seed81/verify.py`. This opt-in package
keeps a vendored literal `baseline.py` for reference-engine comparisons.

An opt-in acceleration of woklerx's retained [PR1017](https://github.com/CrocSwap/integer-mult-bounds/pull/1017)
checker. Sixteen independent single-gate omissions run in integer bit lanes.
All 5,563 mutant maps still propagate all 661 symbolic inputs through every
retained gate and observe all 661 outputs. The complete predecessor certificate
is identical. No new kappa is claimed.

Base: `cd91ac8e2652bfee6bf09da3b8724253bcf78f5f`. OS seed 92 selected verification
engineering. [CLAIM.md](CLAIM.md) records the candidates and overlap check.
[SOURCES.json](SOURCES.json) pins five live inputs with Git blobs and SHA256,
plus historical catalogue and selected-record provenance. The accepted saving
at this base is #1094's conditional `836330098538459/500000000000000000`.
This measures verifier runtime, not multiplication runtime.

## Reproduce

Python 3.10 or later, standard library only, no network:

```sh
python3 -I -B research/omission-lanes-seed92/verify.py
```

Expected JSON status: `PASS_PACKED_OMISSION_EQUIVALENCE`. This recomputes
[RESULT.json](RESULT.json): every mutant matrix against the frozen literal
implementation, every certificate field, 1,564 short/boundary words, seven
inherited controls and thirteen new controls. The matrix stream digest is
`58cf5a86dba09b165ceff9f92bda853550c83bf9be0ad72d15cf1b6cc38838f9`.

For the accelerated audit alone:

```sh
python3 -I -B research/omission-lanes-seed92/replay.py
```

Expected: `PASS_PACKED_OMISSION_REPLAY gates=5563 columns=661 lanes=16 controls=7 no_new_kappa`.
This runs the complete source audit and certificate comparison. The first
command additionally executes the slower implementation as equivalence evidence.
Add `--benchmark` to `verify.py` for five alternating-order timings per mode.
Every timed call hashes inputs and checks the entire certificate; there is no
hardware-dependent timing threshold. Raw times are in [BENCHMARK.json](BENCHMARK.json).

On macOS arm64 with CPython 3.14.8, the final median fell from 2.167 seconds to
1.490 seconds, a **1.45x speedup** for the complete audit. Full equivalence also
passes through the registered Python 3.12 hook and Python 3.11 under `-I -O -B`
from outside the checkout. Linux performance is unmeasured.

The registered Python 3.12 hook runs the full equivalence command:

```sh
python3.12 scripts/research_package.py --package research/omission-lanes-seed92
```

## Exactness and retained coverage

An output row's bit `i` is its coefficient of input `i` over F2. Pack a batch
as `sum(row[j] << (661*j))`. Each lane occupies 661 bits. XOR cannot carry
across lanes, so a packed ADD executes the same ADD independently in every
lane. At gate `k`, mask the source lane belonging to omission `k` to zero.
Every other lane executes the gate. Each lane therefore has its full literal
prefix, one omitted ADD and full literal suffix. Shifting and masking recover
the exact rows. No rank-one factor is used to derive a mutant map.

`load_checker` verifies the frozen source hash and adapts three unique fragments
in memory: create the iterator, consume each matrix with a row-count check, and
reject surplus matrices. Original per-row factor comparisons, intact boundaries,
region checks, Boolean witnesses, input-blind example, uniqueness checks and
seven controls still run. Missing matrices fail closed. The frozen source and
certificate are never edited; no persistent result cache is introduced.

The short-word domain is all 1,555 words of lengths zero through four on three
registers with distinct source/destination, plus nine seed92 words of lengths
15, 16, 17, 31, 32, 33, 63, 64 and 65. All run at batch sizes 1, 2, 3, 16 and
64. The actual circuit ends in an eleven-lane partial batch. Controls reject
invalid batch sizes, changed high input bits, duplicated/extra/missing lanes,
a missing helper output row and separate corruption of all five live inputs.
Canonical JSON comparison includes every certificate field and type distinction.

The initial 64-lane kernel trial was slower: 1.962 seconds versus 1.644 for
literal replay. A bounded follow-up tested 16 and 32 lanes, taking 0.983 and
1.245 seconds respectively, with every row checked. These exploratory kernel
times are separate from complete-audit benchmarks. Sixteen is not claimed to be
the optimal batch size on all interpreters or hardware.

The replay hook declares every external input. Catalogue and selected-record
pins are historical provenance checked through Git. Standalone commands need
only the live inputs. Finite replay is not a formal theorem proof. Scope remains
PR1017's single-ADD-omission family on PR967 D; multi-faults, whole-word/native
execution, hosting, precision, analytic transfer and the full selected cold
replay are untested here. Their inherited obligations remain. Existing packages,
`upstream/`, shared scripts, workflows and selected frontier are untouched.

## Open next questions

Run the same alternating benchmark on Linux Python 3.12 and retain all ten times
with the equivalence receipt. This tests whether the local gain carries to the
generic CI platform. [TASK.json](TASK.json) records the command and scope; the
only blocker is access to a Linux runner.

## Credit and disclosure

Sagar Thakrar, with substantial OpenAI Codex assistance in selection,
implementation, verification and writing. One agent; no independent human
review claimed. New material is Apache-2.0 under the repository license.

Credit woklerx's PR1017 atlas/interpreter, Sricharan Vagvala's PR967 word,
DreamingOfClouds' PR589 supplier and eumemic's PR555/543 lineage. The original
notices also credit Gareth Davidson's PR915/926, Scott Woolsey Biggart's PR733,
Greer Guthrie's PR694, Mikhail R. Gadelha's PR686, commdata2338's PR794 and
Sagar Thakrar's PR753/762. Those notices remain in place. This does not claim
algorithmic independence from PR1017 or novelty for integer bit packing.
