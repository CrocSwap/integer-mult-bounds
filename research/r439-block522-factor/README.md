# R439 phase-B frame 522: 43 to 33 additions

**Finite bit-circuit construction; no new kappa.** Replace B[361:404] of
PR589's tuned R439 word by the 33 additions in `CANDIDATE.json`, all at the
same frame 522. The replacement has the identical integer-linear map on the
same twelve registers. Rebuilding the literal reverse cleanup saves another
ten additions, for **20 fewer ADDs in the complete local word**.

| Exact quantity | Selected PR589 word | Replacement |
|---|---:|---:|
| Frame-522 block ADDs | 43 | 33 |
| Complete local ADDs, including cleanup and scatter | 24,305 | 24,285 |
| Exported records | 27,234 | 27,214 |
| Forward positive-prefix bound | 49,347 | 49,347 |
| Reverse positive-prefix bound | 1,113,070 | 1,045,786 |
| Native payload envelope | 93 bits | 93 bits |
| Paid rank mass | 5,129 | 5,129 |
| Registers / helpers / retained copies | 661 / 439 / 9 | 661 / 439 / 9 |

Every register's sequence of frames is identical. The local paid histogram
is unchanged:
`{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}`.
This is a circuit-size reduction, not a measured runtime improvement or an
improved recursive moment. The selected conditional exponent remains
`1661634653669567/1000000000000000000` (PR799 with PR589).

## Reproduce

From the repository root, Python 3.11+ and the standard library suffice:

```sh
python3 -I -B research/r439-block522-factor/verify.py
```

Expected final line:

```text
PASS_R439_BLOCK522_FACTOR gates=43->33 ADDs=24305->24285 columns=661 controls=11 rank_mass=5129 no_new_kappa
```

The verifier checks pinned sources, all twelve integer columns, all 4,096
Boolean block inputs, all 661 dirty-input columns of the full exported word,
identical frame paths, the inherited exact H1-H5 interface and conclusions,
the full local bill, both positive bounds and the payload cap. It imports no
search code. It compares its regenerated mathematical receipt with
`EXPECTED.json`; it does not trust the claimed savings in that file.
`--output /absolute/fresh/directory` retains both rebuilt words, exported
records, interface receipts and the result. Gzip container bytes are not used
to compare regenerated words; the immutable committed input is SHA256-pinned.

Fresh unchanged C++ legality and 5/9/11-stage replays, on **both** words:

```sh
python3 -I -B research/r439-block522-factor/native.py
```

This needs a C++17 compiler and Boost headers. `CXX` and `BOOST_INCLUDE` (or
`--cxx` / `--boost-include`) select them. Expected marker:
`PASS_R439_BLOCK522_NATIVE words=2 columns=883/1327/1549 bridge_controls=96 five_stage_regression=PASS`.
The script compiles the pinned original checkers, compares their profile,
ADD counts and exact prefix bounds with the Python result, and compares
all non-timing receipt fields with `NATIVE.json`. The specialized five-stage
checker and the general checker at KPAIRS=2 agree field for field.

Search and package controls:

```sh
python3 -I -B research/r439-block522-factor/search.py --output /tmp/block522-candidate.json
cmp /tmp/block522-candidate.json research/r439-block522-factor/CANDIDATE.json
python3 -I -B research/r439-block522-factor/test_package.py
```

The search reproduces the candidate and coverage counts byte for byte. The
package test checks a relocated minimal source closure under optimized
Python and rejects six source/candidate/receipt faults. The verifier's
`--write-expected` and native wrapper's same flag are explicit development
receipt-regeneration options, not the review commands above.

## Why the splice is valid

The twelve registers, in matrix order, are
`[1,7,24,25,28,29,98,99,100,101,106,108]`. They are existing source registers;
the replacement introduces no helper, COPY, preparation, boundary adapter or
additional source access. Every operation is the elementary addition
`destination += source` at frame 522.

Let M be the original block's integer matrix. `verify.py` obtains its columns
by executing the original block on each unit input and independently obtains
the replacement's columns the same way. Equality over the integers establishes
equality of these linear maps over every commutative coefficient ring by
reduction of the coefficients. The 4,096-input Boolean table is an additional
finite control, not the justification for the integer statement.

Before the block, the two words are identical. At its end the integer values
agree for arbitrary entering values, including any previously accumulated
dirty-register dependence; subsequent B gates therefore see the same values.
All changed gates write z registers, so C is rebuilt as the literal reverse
of all z-destination A/B gates at the full frame. Over F2 every addition is an
involution, and this C restores those registers. The pinned checker replays
all columns and re-establishes each H1-H5 hypothesis and U/J/K/C conclusion.
This is not a claim that the complete positive-integer word, including C,
equals its predecessor over Z: positive cleanup is inverse over F2, and its
signed/coefficient-growth accounting is checked separately.

The replacement and original use the same registers at the same frame, with
identical frame paths before and after the block and cleanup. Thus no MOVE,
COPY or paid rank disappears from the invoice. The only deletions from the
exported bill are ten B ADDs and ten C ADDs. Fresh chronological C++ legality
checks confirm this, including nine complete COPY/ERASE lifecycles.

The reversed positive block map is **not** entrywise dominated by the old
one. Its total entry sum falls from 319 to 141, but that alone does not prove
the whole-word bound. We explicitly recompute the full forward and reverse
cancellation-free row bounds from the exported stream, including copied
centres and resets. Both Python and C++ obtain

```text
64 * 49347^3 * 1045786^2
= 8411004922895417997685101312 < 2^104
```

Its bit length is 93. The inherited 104-bit native cap is retained.

## Search domain and coverage

The OS assignment seed is **17**. Modulo the ten contiguous B blocks it
selects index 7, frame 522. The claim and alternatives considered are in
`CLAIM.md`. The experiment is confined to this block.

Starting from M, a trajectory subtracts row s from row d only when every
coefficient remains nonnegative. It stops at the identity or when no
subtraction is available. Reversing a successful trajectory gives a positive
addition circuit with the required matrix. Each subtraction strictly reduces
the sum of all entries; rows never vanish because every row operation is
invertible and M has full rank. The sum starts at 174 and an invertible
nonnegative terminal matrix has sum at least 12, so a trajectory takes at
most 162 steps. A terminal permutation other than the identity is rejected;
permutations or free relabellings are not silently inserted.

`random.Random(17)` drives exactly **12,000 trajectories**, cycling candidate
selection among the largest one, two, four, eight, or all feasible row
subtractions. Candidate ordering is deterministic. The objective is the
lexicographic pair (ADD count, reversed positive-matrix entry sum).
**492** trajectories reached identity, including **seven** with 33 ADDs.
The selected tie-break improvement appeared at zero-based trial 8,602.
`CANDIDATE.json` records the complete successful-length histogram. The other
11,508 trajectories stalled outside the identity; they do not prove anything
impossible. **No unrestricted minimum, nor optimality within this sampled
factorization class, is claimed.**

## Relation to concurrent work

The baseline is DreamingOfClouds' PR589 tuning of eumemic's PR555 punctured
R439 supplier, with PR543/PR545/PR510 ancestry and retained notices.

- PR891 (`645fb93fcd21b86aca7e2bf81582be5c62411b27`, @navinor) reports that
  frame 522 has no circuit in its whole-block single-write class. The present
  circuit uses intermediate donors and repeatedly writes several registers,
  so it is outside that class. This does not contradict that negative result.
- PR873 covers frame 508; PR857 and PR891 cover frame 523; PR880 covers frame
  507; PR884 covers frame 521; PR843 covers frame 509; PR844 covers block 4.
  The general positive-factorization approach is shared with that work. We
  claim a distinct fixed block and exact witness, not a new synthesis method.
- PR728/PR792 alter phase-A mini-nodes. PR886 proves optimality of frame
  assignment at fixed gate order. This contribution changes a phase-B circuit,
  not either of those fixed search classes.
- [PR904](https://github.com/CrocSwap/integer-mult-bounds/pull/904), Gareth
  Davidson (@bitplane), arrived during the final overlap refresh. Its
  [pinned certificate](https://github.com/CrocSwap/integer-mult-bounds/blob/33b9175c345bcd0f21b95d29f37cb95fffd5a134/research/r439-four-wire-prefix/CERTIFICATE.json)
  selects one frame-522 interval, B[380:384], on registers `[7,28,98,108]`,
  saving one ADD (four to three). Here the entire B[361:404] block falls from
  43 to 33 using twelve registers. That is nine more B ADDs removed within
  this block, but **not** a tested nine-ADD improvement to PR904's full word.
  Its other 94 intervals and our replacement have not been combined or
  repriced. PR904's complete 254-ADD saving is a separate contribution.

No concurrent circuit or saving is imported or added to the reported totals.
The inspected relevant PRs were pending, not accepted frontiers.

## Pins, validation and remaining obligations

Base: **`f567884aeb8851b6e794af1184119a3bfbe1e631`**.
Selected bit source head: **`a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46`**
(PR589). `SOURCES.json` binds every consumed repository input, including the
selected certificate, original Python checker/exporter and C++ checker
sources. `ENVIRONMENT.json` records the local interpreter/compiler/platform
and Boost input digest. `VALIDATION.md` records executed checks.

The finite native replays do not constitute a full hosted invoice, supplier
binding update, outer assembly, all-size compilation, or a proof-assistant
proof. The mutable-source/common-label realization, whole-call hosting,
precision/tape, exact-recovery and analytic transfer assumptions remain those
of the selected construction. Integration into the hosted supplier and any
effect on execution time remain unmeasured. The selected record and
`upstream/` are unchanged.

Prepared by **Jerry Chen (@CubeJerry)** with substantial **OpenAI Codex**
assistance in discovery, implementation, verification and writing. Apache-2.0;
see `NOTICE.md`. No subagents or independent human review are claimed.
