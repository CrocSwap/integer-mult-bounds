# Exact factor schedules for R420 block 7

**Finite bit-circuit construction and finite-class optimality certificate; no
new κ.** The phase-B block at `B[471:512]` (frame 549) in eumemic's selected
PR543 R420 word falls from **41 to 28 binary XOR additions**. Its literal
reverse cleanup saves thirteen more, so the complete native word falls from
**26,916 to 26,890 ADDs**. No temporary register is introduced.

The exact forward **integer** transfer matrix is unchanged, not merely its
reduction modulo two. The reverse cancellation-free transfer matrix is
entrywise no larger (25 entries strictly decrease). The replacement retains
all 660 dirty-input columns, the original per-register frame paths, all
420 helpers, nine retained copies and paid rank mass 5,112. This is a scalar
instruction reduction, not a recursive-profile or practical runtime result.

| Local native bill | Original | Replacement |
|---|---:|---:|
| First factor | 17 | **14** |
| Second factor | 24 | **14** |
| Block plus its reverse cleanup | 82 | **56** |
| All ADDs, including D and scatter | 26,916 | **26,890** |
| All native records | 29,874 | **29,848** |
| Forward positive prefix | 144,651 | 144,651 |
| Reverse positive prefix | 2,270,064 | **2,205,308** |
| Local payload allowance | 100 bits | 100 bits |

## Reproduce

From the repository root, Python 3.9+ and the standard library suffice:

```sh
python3 -I -B research/r420-block7-exact-schedule/verify.py
```

Expected final line:

```text
PASS_R420_BLOCK7_EXACT_SCHEDULE factors=17+24->14+14 ADDs=26916->26890 states=8192 columns=660 controls=8 kappa=unchanged
```

The default command writes only into an automatically removed temporary
directory. `--out /path/to/new-directory` retains both complete words, the
original exporter's binary records, frame files, and exact receipt. An
existing output path is rejected. Nothing under `upstream/`, the original
supplier, or the selected frontier is edited.

For unchanged C++17/Boost native legality and five-, nine-, eleven-stage
column checkers:

```sh
python3 -I -B research/r420-block7-exact-schedule/native.py --out /tmp/block7-native-new
```

Expected: `PASS_R420_BLOCK7_NATIVE words=2 stages=5,9,11 bridge_controls=96`.
Set `CXX` to the compiler executable and `BOOST_INCLUDE` to the Boost include
directory if needed. Defaults are `c++` and `/opt/homebrew/include` on macOS,
`/usr/include` elsewhere. The C++ inputs and portable headers are source-pinned;
the external compiler and Boost version are environment dependencies.

Reproduce the complete nomination, without a stochastic search or a solver:

```sh
python3 -I -B research/r420-block7-exact-schedule/nominate.py > /tmp/block7-certificate.json
cmp /tmp/block7-certificate.json research/r420-block7-exact-schedule/CERTIFICATE.json
```

Expected: `cmp` exits zero. Both factor searches complete all 4,096 states;
there is no timeout, sample, truncated search, or claim of unrestricted
circuit optimality. The OS assignment seed is **17**; `17 mod 10` selects
block 7. No other object was optimized.

## Exact object and schedule class

Base commit: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Selected bit source #543: `2065fe4f72a914d907f1046603f5a36f17018535`.
Selected #626 source: `660de893d27bb7abd1d5b01b1640207528a5c851`.
`SOURCES.json` pins every consumed repository source, including the unchanged
checker/exporter and optional native dependencies. `CERTIFICATE.json` contains
the complete integer distance potentials and explicit replacement batches;
`EXPECTED.json` contains the exact regenerated evidence.

Use local wire order

```
[1, 7, 26, 27, 30, 31, 106, 107, 108, 109, 115, 117].
```

The original 41-gate block has a fixed cut after gate 17: its first and second
factors are the original upper/lower elimination factors. We retain these two
**integer** matrices separately. Each is a binary matrix with diagonal one.

Within each factor a schedule finishes every destination exactly once, in
any order. Finishing row `d` means one contiguous batch of operations
`wire[d] += wire[s]`, using distinct other wires; no extra scratch, scaling,
subtraction, or later revisit of the destination is allowed. Empty batches
are allowed for unchanged rows. Sources may be read before or after they
are finished. The output is on the same named wires, with no free permutation.
All additions have coefficient +1. The same circuit is then interpreted
as XORs over F2 in the bit word.

The original two factors belong to this class. The certified minima are
14 and 14, respectively. The combined 28 is optimal only among independent
schedules of these **fixed two factors**. A circuit that crosses the cut,
changes the intermediate matrix, revisits a destination, uses cancellation,
borrows wires, changes frames or chooses another block is outside this claim.

## Proof of the finite-class minimum

Let `M` be one factor and `e_s` the original unit row on wire `s`. At the
boundary after finishing precisely the set `S`, the row on wire `s` is
`M_s` for `s in S` and `e_s` otherwise. This follows directly by induction on
the batches and does not depend on their earlier order.

To finish an unfinished destination `d`, choose a subset `Q` of the other
wires such that, over the nonnegative integers,

```
M_d = e_d + sum(current_row(s, S) for s in Q).
```

This is necessary and sufficient; its exact cost is `|Q|`. Since the target
row is binary, selected donor supports must partition `M_d - e_d`. A donor
with a coordinate outside that support cannot occur, and a donor cannot
occur twice. The empty set is handled explicitly. This proves that the
state graph enumerates the entire stated class, with transitions
`S -> S union {d}`. Marking an unchanged row as finished is a harmless
zero-cost transition: its row stays the same.

`nominate.py` minimizes over this acyclic graph using a recursive exact-cover
oracle. Its path is a construction, not the sole evidence for the minimum.
`verify.py` does **not import the nominator**. It reconstructs each matrix
with twelve separately replayed integer input columns and independently
enumerates all eligible donor subsets using ordinary integer addition in
base 16. Each sum contains at most eleven binary vectors, so no carry can
hide an overlap or a missing coordinate.

For every valid donor subset the verifier checks the certificate potential
inequality

```
p(S union {d}) <= p(S) + |Q|,       p(empty) = 0.
```

Telescoping along any schedule gives `p(full) <= cost(schedule)`. Separately,
the explicit batch witness realizes `M` at cost `p(full) = 14`. Thus the
lower and upper bounds coincide. This is checked for **49,152** possible
state/destination pairs across the factors; **43,520** are feasible. Every
potential and witness is in the committed certificate. This is a finite
mathematical certificate with a written completeness argument, not a
proof-assistant formalization.

## Full word, growth and accounting

The changed block occurs at one closed D4 frame, after the initial target
single reads and before all later needer writes and target reads. Its same
named-wire integer map therefore preserves all source and helper components
of every later read, including arbitrary initial dirt. Nothing in D, A,
scatter, or the remaining B gates changes. C is regenerated as the literal
reverse of **all** z-destination gates in A and B, at the full frame. This
retains the original H1–H5 interface; no checker guard is patched or relaxed.

All twelve changed wires already have the same legal climb to frame 549.
Every wire's ordered frame path is checked equal to the original. Reordering
first accesses inside the block can reorder MOVE events globally, but cannot
remove or discount any individual climb. Native legality checks common-frame
access and the actual emitted chronological stream. The complete rank
histogram remains `{1:1320, 2:1440, 4:60, 5:120, 8:9}`.

The first factor saves 3 ADDs, the second saves 10, and their full reverse
saves another 13. There are no new helper, source-copy, preparation,
restoration, frame-change, or recursive-child charges. The recursive paid
profile and retained-copy cost are unchanged. The selected assembly remains
complex-bound and unchanged; **no larger bit exponent or κ is inferred**.

The verifier compares exact integer matrices for the complete block and
compares the reversed positive matrices entry by entry. Because positive
updates only increase each row, every intermediate norm within a block is
bounded by its final row norm. Equality of forward matrices and domination
of reverse matrices therefore preserve the relevant prefix envelope for any
nonnegative starting-bound vector. The native exporter and independent C++
checker also recompute the actual prefix numbers shown above. The inherited
payload formula `64 * forward^3 * reverse^2` stays below `2^104`.

The primary checker replays all 4,096 Boolean block inputs and all 660 full
word columns with a separate set-valued interpreter. The unchanged PR543
checker verifies exact rational E8 geometry, all 672 closed frames, the
complete word, and each H1–H5 hypothesis and conclusion. Geometry is computed
once and reused only because the entire frame/label data is unchanged.

Eight negative controls reject omitted local work, F2-neutral positive-cost
inflation, missing cleanup, scalar-valid but nonliteral stale cleanup,
missing dirt compensation, illegal frame descent, an inflated lower-bound
potential, and an unpaid witness gate. The stale-cleanup control explicitly
passes the endpoint map before failing literal H4; endpoint equality alone
is not passed off as interface compliance.

## Scope, related work and credit

The selected conditional result remains
`51110230636731/31250000000000000 = 0.001635527380375392`.
All-size compilation, common-label/mutable-basis realization, physical
hosting, normalized residuals, precision/tape/exact recovery and analytic
transfer remain inherited obligations. The hosted-parent/invoice/outer
assembly was not regenerated for this local circuit. Finite stage checks
are not a full multiplication theorem, a speed benchmark or independent
human peer review.

Credit eumemic's #543/#493 construction and interface; Dylan Crow's #370
format, exporter and checker lineage; DreamingOfClouds' retained-total and
pricing work; Zhihao Chen's scalar interface; chafreaky/DaysSky and the
cumulative stage, realization and hosting lineage in the original
[NOTICE](../e8-bit-r420/NOTICE.md). Those source notices remain unchanged.

Concurrent #670 (yongjae321) and #674 (x0hu) shorten **blocks 3 and 5**;
#691 (mtpsl) changes phase-A quad 13. #681 (Alluri) integrates those and other
circuits; #754 (Jeffrey Cox / namredips) gives exact synthesis of cleanup
windows on at most four wires. They are credited as related predecessors,
not imported or asserted composable. This contribution supplies an unchanged
literal-H4 circuit at **block 7**, and a complete twelve-wire factor-schedule
lower-bound certificate. The elementary dynamic-programming technique itself
is not claimed as new. See `CLAIM.md` and `VALIDATION.md` for overlap checks
and exact execution limits.

Prepared by **Yuzhou Wang (@yzhouwang)** with substantial **OpenAI Codex
assistance** in task selection, mathematical derivation, implementation,
verification and writing. Apache-2.0. No delegated workers were used.
