# Compose and replay the PR670 and PR674 R420 circuits

This package combines **yongjae321's PR670 block-3 circuit** and
**x0hu's PR674 block-5 circuit** in eumemic's PR543 R420 supplier. The new
contribution is their checked composition and fresh native and whole-owner
replay. The two input circuit improvements belong to those authors.

The combined word uses **26,858 scalar ADDs instead of 26,916**, a saving of
58 per local invocation, including literal cleanup. Its 660 register frame
paths, 420 helpers, nine retained totals and paid rank mass 5,112 stay the
same. **There is no new bit exponent or integer κ.** No selected-frontier
file or predecessor source is changed.

## Reproduce

From the repository root, use Python 3.10 or later for the standard-library
check of the composition, complete local word and controls:

```sh
python3 -B research/r420-two-block-composition/verify.py
```

For the full contribution, provide NumPy, SciPy, SymPy, a C++17 compiler and
Boost headers, then run:

```sh
python3 -B research/r420-two-block-composition/verify.py --hosted
```

`--hosted` includes fresh five-, nine- and eleven-stage C++ checks on both
words, then the nine-stage physical hosting and invoice checks on both.
`--native` runs only the C++ part. Run with Python assertions enabled.
Set `CXX` and `BOOST_INCLUDE` for installations outside the default search
paths. The author used `CXX=/opt/homebrew/bin/g++-16` and
`BOOST_INCLUDE=/opt/homebrew/include` on macOS.

The command creates a temporary output directory and prints its path.
Use `--output /absolute/new/directory` to keep outputs at another location.
Expected final line:

```text
PASS_R420_TWO_BLOCK_COMPOSITION local_additions=26916->26858 saved=58 kappa=unchanged
```

The outputs include both words, exact receipts and each subprocess log.
Use the canonical decoded JSON hash in `RESULT.json` to identify a generated
word. Gzip container bytes can differ across environments.

## Pins and provenance

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
The selected conditional κ at this base is
`51110230636731/31250000000000000 = 0.001635527380375392`, from #626 with
#543. This composition does not depend on claims in newer frontier PRs.

| Source | Pinned head | Role |
|---|---|---|
| PR543, eumemic | `2065fe4f72a914d907f1046603f5a36f17018535` | Original R420 word and replay chain |
| PR670, yongjae321 | `2e31fcad7f9ecc8b97039ecb2333e581fd725fa1` | Block 3: 50 to 33 XORs |
| PR674, x0hu | `1b01fd8b135fb2c458554fbbbab4338336bf366d` | Block 5: 46 to 34 XORs |

[SOURCES.json](SOURCES.json) pins every consumed research source and input
by SHA-256 and Git blob ID. The original circuit certificates and READMEs
are retained byte for byte under `vendor/`. Neither predecessor's verifier
is imported. Each single-block reconstruction must match its author's
canonical complete-word hash before the circuits are combined.

Assignment seed 15 came from operating-system randomness. It initially
selected block 5. A 10,000-trial two-sided synthesis search found a 37-gate
word, but PR674 then supplied a stronger circuit for the same block. That
local experiment is archived and is not submitted as a competing result.
The one scope pivot was to compose and verify the two concurrent circuits.
[CLAIM.json](CLAIM.json) records the selection and pivot. No pinned sprint
issue existed at the claim or overlap checks. This composition performs no
new search and makes no optimality claim.

## Exact composition argument

The original slices are `B[263:313]` at frame 545 and `B[371:417]` at frame
547. These are zero-based, half-open intervals. The circuits use disjoint
sets of twelve source registers. No target reads occur inside either slice.
The builder applies the higher slice first, so the first replacement does
not invalidate the second slice's offsets. It then regenerates C once as
the literal reverse of all non-target gates in A and the new B.

The checker independently enumerates all 4,096 scalar inputs for each
block. Each replacement has exactly the same ordered F2 output map as its
original, with no free output permutation. Thus each block produces the
same values for all later gates, including partially formed sums. Their
composition has the same raw source and target maps. Literal reverse
cleanup restores arbitrary source and helper values. The inherited PR543
checker verifies this conclusion on all 660 symbolic columns, and checks
H1–H5 and all 672 closed rational frames.

The checker also constructs the forward and reverse nonnegative transfer
matrices for both blocks. Each replacement matrix is entrywise no larger
than the original. This establishes non-increase for arbitrary nonnegative
input bounds at each substituted slice. These matrices bound the signed
lift; F2 equality is not presented as an integer-ring endpoint identity.
Fresh C++ replay checks the actual complete lifted word at all three stage
counts and computes its prefix bounds.

Every register has exactly the same ordered frame path. D, A, scatter,
retained totals, labels, endpoints and helper stock are unchanged. Thus
source access, dirty compensation, copies, restoration and all recursive
children are included. The paid local profile remains

```text
1320 H_1 + 1440 H_2 + 60 H_4 + 120 H_5 + 9 H_8.
```

| Local quantity | Original | Composition |
|---|---:|---:|
| B gates | 837 | 808 |
| C gates | 2,661 | 2,632 |
| Scalar ADDs, including D and scatter | 26,916 | 26,858 |
| Serialized native records | 29,874 | 29,816 |
| Forward cancellation-free signed row bound | 144,651 | 144,651 |
| Reverse cancellation-free signed row bound | 2,270,064 | 2,145,492 |
| Payload prefix charge, in bits | 100 | 100 |

The nine-stage replay uses the original frozen owner selection. It does
not rerun the discovery optimizer. The unchanged emitter and independent
auditor check the actual new scalar stream, every whole helper owner,
idle window, residual coordinate and paid remainder. Both the baseline
and composition must pass the 17 parent-template and 16 hosted-template
mutation controls. The 120,960 helper invocations remain fully hosted,
with zero banks. The physical program has 288 local invocations, so the
replay must show exactly `288 * 58 = 16,704` fewer emitted instructions.

Both exact moment engines and the finite invoice are rerun. The bit
exponent must remain `0.001653826988146798944268`. The rounded invoice and
paid global profile must match the fresh baseline. The unrounded global
prefix and coefficient bounds each decrease from 189 to 188 bits; their
charged prefix stays at 192 bits. The two-level charge stays at 512 bits.
The emitted instruction count decreases from 8,603,712 to 8,587,008.
The inherited price
script also runs its historical cited-PR484 arithmetic control. That is
not a replay of PR484's complex construction or a new selected assembly.

## Controls and verification boundary

The local controls deliberately break each component's map while rebuilding
its correct inverse, omit a cleanup gate, use an unpaid low frame, and
apply both edits with stale ascending offsets. Each must fail for its
stated target, restoration or frame reason. Keeping the old cleanup still
passes scalar replay because its map is the same, but fails the required
literal-reversal hypothesis H4. It is classified as an interface failure.
The C++ replay also rejects 6, 18 and 24 omitted bridges at five, nine and
eleven stages for each word, covering 900, 1,380 and 1,620 formal columns.

See [VALIDATION.json](VALIDATION.json) for the actual runs and limits.
The repository-wide `make verify` was started once. It passed the earlier
community, producer, partial-gauge, three-stage-cover and paired-cube
groups, then was stopped during recycled-bit verification after free disk
space fell below the workspace's prior resource threshold. It is not a
full-suite pass. Extra checkout copies from that broad run were removed;
existing research and `upstream/` were preserved.

No new complex supplier, selected outer assembly, Lean theorem or practical
runtime speedup is claimed. The all-size compiler, common-label and mutable
basis realization, whole-owner hosting, precision/tape and analytic-transfer
assumptions remain. Finite replay does not prove the full multiplication
theorem. The original PR612 Lean literals do not certify these new gates.
PR661 fixes the gate stream and excludes resynthesis, so its frame result
is not contradicted.

## Credit and license

The block-3 circuit is yongjae321's PR670 contribution. The block-5 circuit
is x0hu's PR674 contribution. Both disclose substantial OpenAI Codex
assistance. Their original notices remain in the vendored READMEs.
Ali Romman prepared this composition and integration replay with
substantial OpenAI Codex assistance. No separate human review is claimed.
New files are under the repository's Apache-2.0 license.

The R420 word, scalar interface and independent local checker are eumemic's
PR543/493 work. Credit is retained for Zhihao Chen's interface and geometry;
Dylan Crow's bit format, exporter and cohort checkers; DaysSky's bridged
checker and hosting; DreamingOfClouds' nine-stage accounting and moment
engines; chafreaky's owner emitter, audit and invoice; and the cumulative
supplier lineage in the original R420 README. Their sources stay unchanged.
