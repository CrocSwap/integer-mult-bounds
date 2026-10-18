# Executed validation

Base: `407d52ff15b2217b6e22bce44728b4c3907b6515`.
Assignment: fresh OS seed 2, bit-supplier track. Executed 2026-10-13.
Python environment: CPython 3.12.14, macOS 26.5.2 arm64. The package itself
requires only the Python standard library; native replay additionally uses
C++17 and Boost. These are finite mathematical and failure-mode checks,
not performance benchmarks or formal verification of the full theorem.

## Python and independent checks — PASS

- `python3 -I -B research/r480-qnode-seed02/verify.py --replay-search`:
  all 1,000 frozen Q-node2 trajectories replayed; exact recipe and receipt
  matched. The complete command also passed in an isolated minimal source
  closure under `-I -O -B`, in a directory containing spaces.
- `python3 -I -B research/r480-qnode-seed02/test_package.py`:
  **4 regression groups passed**, 7.536 seconds in this environment. Tests
  cover fixed output labels, frame/register scope, non-integer/Boolean
  metadata, source-byte corruption, removal of a pinned input from both
  manifest lists, receipt type corruption and safe refusal to overwrite
  existing output directories. The minimal-copy test confirms inherited
  inputs are byte-identical after replay and compares decompressed exports.
- `independent.py`: all 4,096 local Boolean assignments and their inverse,
  every one of 720 arbitrary persistent input columns, both chronological
  positive-prefix directions and all 720 register frame paths. This separate
  support-set implementation does not import the search or primary verifier.
- Independent reconstruction of every native record tuple matched the actual
  unchanged exporter output for both words: 36,916 original records and
  36,898 replacement records. This comparison passed under `-I -O -B`.
- All 21 retained inputs matched both the SHA256 and Git blob at the exact
  base commit. No inherited input, `upstream/`, selected record, generator
  or global artifact was changed.
- `scripts/verify_selected_result.py`: PASS at the selected PR942 value.
  The selected-result regression module's **25 tests passed** (0.687 seconds).
  These protect selection bookkeeping; they do not prove this candidate's
  mathematical admission.

The two interpreters agree on complete ADD counts 33,958/33,940, F = 176,135
for both, B = 3,751,204/3,682,548, and the exact payloads in `EXPECTED.json`.
Each payload has bit length 102 and is strictly below 2^104. Local positive
forward growth rises 25 -> 99; no entrywise positive-domination claim is made.

## Negative controls — PASS

There are **53 distinct adverse cases** across the Python checks: all 43
single-gate deletions; eight additional independent controls (output swap,
source/helper/target incorrectly treated as zero, omitted compensation,
omitted cleanup, wrong frame, omitted ERASE); and two primary controls.
The overlapping gate-deletion coverage is not double-counted.

The two primary controls deliberately preserve the F2 endpoint:

1. Keeping the old cleanup after replacing A has 33,949 ADDs and fails the
   literal-inverse contract. It is not an endpoint counterexample.
2. Repeated six-XOR identity cycles with matching reverse cleanup pass the
   endpoint check but fail the complete 104-bit precision allowance.

These controls distinguish endpoint validity, claimed cost and precision.

## Native replay — PASS

`native.py` ran both complete words through the unchanged retained checks.
`NATIVE.json` contains their complete receipts, removing only elapsed time
and a temporary scalar-stream path.

- Legality, source ownership and copied-center lifecycle: PASS.
- 5/9/11 stages: **960/1,440/1,680 formal columns per word**, respectively;
  **96 rejected bridge controls** across both words.
- **2,940 nested MOVEs, 9 COPYs, 9 ERASEs, rank mass 5,592** and histogram
  `[[1,1200],[2,1440],[4,180],[6,120],[8,9]]` remain identical.
- Relaxed mutable-source 720-column checker and PR425 interface: PASS.
  The stock immutable-source checker rejects both words as expected.
- Positive E8 Gram checks: all **672 frames per word** pass.
- The word hashes and complete positive bounds exactly match both Python
  implementations. ADD saving is 18 at each checked stage count.

Executed with Apple clang 21.0.0 (`clang-2100.1.1.101`), C++17 and Boost 1.87.0.
The Boost `version.hpp` SHA256 is
`de3c73716db521194a767801a45f78f466e83e06cbae476fa2492be39d820252`.
The first C++ `-O2` / normal Python receipt exactly matches the final C++
`-O0` / `python3 -I -O -B` wrapper receipt. The wrapper defaults to `-O0`
and runs inherited assertion-based Python checkers without `-O`, using `-I`
to ignore `PYTHONOPTIMIZE`. Constants are `HDIM=8, NCOPY=9, VPORTS=120,
RHELP=480`, with `KPAIRS=4/5` for the 9/11-stage builds. A modified source
pin is rejected. Compiler warnings were limited to inherited Boost syntax.

The README native command reproduces the final receipt; `--out` preserves
all compiler/checker logs and `ENVIRONMENT.json`. Initial compilation was
slow under the local restricted environment; it completed without changing
any retained checker or weakening its coverage.

## Search coverage

The final experiment is precisely 1,000 trajectories of the Q-node2 matrix,
`random.Random(2)`, with the first shortest word retained. Trial 860 uniquely
reached 43 XORs. The exact histogram and improvement sequence are frozen in
`RECIPE.json`; no optimality or exhaustive circuit-search claim is made.

During orientation, three separate 1,000-trial probes were run, in order
Q-node2, Q-node1, Q-node8. Each reset `random.Random(2)` and used the same
elimination domain. Their preliminary lengths were 52 -> 43, 71 -> 41, 62 -> 46.
Only Q-node2 received full precision/native verification and is submitted.
The Q-node1/8 observations are disclosed exploratory work, not admitted
constructions or independently packaged results. The final command replays
Q-node2, not those two discarded probes.

No repository-wide suite, selected cold replay, full hosting reconstruction,
outer assembly or formal theorem proof was run or claimed for this change.
No selected-construction file or inherited generator was edited.

## Submission refresh

Refreshed main `f4a7051883bc76dad7861b3f0caf7361ce86fe90` retains all 21
source Git blobs and the selected record unchanged. Recent open PRs were
reviewed through #999, with all-state R480 and Q-node searches. #823 remains
the related six-wire R480 result; #980, #986 and #989 change R439 words.
None of those bodies describes this twelve-source R480 Q-node2 replacement.
No composition with their savings is claimed. The two open issues remain
unrelated to sprint coordination, so the local claim is used.
