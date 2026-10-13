# A 34-gate replacement for R420 block 5

This finite bit-circuit improvement replaces one 46-gate phase-B block of
eumemic's PR #543 R420 word with 34 gates on the same twelve registers.
Regenerating its literal cleanup saves another twelve gates. The full native
word uses 26,892 scalar ADDs instead of 26,916. All 660 symbolic input columns,
including arbitrary helper dirt, pass the predecessor's exact replay.

The paid rank profile and every register's frame path are unchanged. This
contribution claims no new bit exponent or kappa. It does not change the
selected construction or any predecessor package.

| Quantity | Original | Replacement |
|---|---:|---:|
| Block-5 XOR gates | 46 | 34 |
| Block plus literal cleanup, unit-input norm bound | 1,075 | 485 |
| Native word scalar ADDs | 26,916 | 26,892 |
| Native forward cancellation-free bound | 144,651 | 144,651 |
| Native reverse cancellation-free bound | 2,270,064 | 2,229,592 |
| Paid rank mass | 5,112 | 5,112 |
| Nine-stage prefix bound, bit length | 189 | 189 |
| Nine-stage charged prefix bits | 192 | 192 |

## Reproduce

From the repository root, with Python 3.11 or newer and no external packages:

```sh
python3 -B research/r420-block5-resynthesis/verify.py
```

Expected final line:

```text
PASS_R420_BLOCK5_RESYNTHESIS block=46->34 native_adds=26916->26892 rank_mass=5112 kappa=unchanged
```

To retain the rebuilt word and exported records, add
`--output /tmp/r420-block5-replay`. The default uses a temporary directory.
Verification reconstructs the candidate from the pinned original, checks the
exact matrices, replays both native words and compares the complete result with
`certificate.json`. Gzip containers are not compared: the certificate pins the
canonical decompressed JSON. Runs with Python's `-O` option are refused.

## Exact change and proof

The object is zero-based D4 block 5, at the half-open slice `B[371:417]` in
`research/e8-bit-r420/data/bitE8mut-r420.json.gz`. Its frame ID is 547 and its
registers, in matrix order, are

```text
19, 24, 35, 40, 54, 56, 65, 74, 84, 95, 100, 111
```

Each operation below means `destination += source`; reduce modulo two for the
bit circuit. Five explicit rewrites advance an existing addition before readers
that need the resulting sum, then remove their redundant direct reads:

1. Advance `111 += 100` before the first read by register 54. Remove
   `54 += 100`, `65 += 100` and `56 += 100`.
2. Advance `74 += 100` to immediately before the late reads by register 40.
   Remove the additions from 100 to 40, 84, 19 and 95.
3. Advance `65 += 54` before `74 += 56`. Remove the additions from 54 to 74
   and 56.
4. Advance `56 += 65` before `74 += 56`. Remove `74 += 65`.
5. Advance `40 += 35` to the beginning of the block. Remove the additions
   from 35 to 100 and 95.

The gate counts after these steps are 43, 39, 37, 36 and 34. The certificate
includes the resulting operation list, original gate offsets, forward integer
matrix and both reverse majorant matrices. Each step preserves the full integer
forward matrix, with outputs on their original wires. Equality over the integers
implies equality over F2 and on arbitrary dirty register contents. No temporary
register, copy, source-access operation or extra frame change is introduced.

For a list of additions, replace each evolving value by a nonnegative bound on
its norm and perform the same additions. The resulting nonnegative integer matrix
maps input norm bounds to output norm bounds. Norms never decrease within this
calculation, so terminal row bounds also bound every prefix. The replacement's
forward matrix equals the original's. Its literal-reverse majorant is entrywise
no larger, with 28 strict entries. Its forward-plus-reverse majorant has 97 strict
improvements. This comparison holds for every nonnegative starting-bound vector,
not only for the unit-input numbers in the table. The verifier also compares the
signed inverse matrices, obtained by reversing and negating the additions.

All rewrites occur at one D4 frame between the same outside gates. Every affected
register still visits that frame. Exact replay checks legal nesting and equality
of the full per-register frame paths, including final climbs. Phase C is rebuilt
as the literal reverse of every source/helper write in A and B at the full frame.
The old D remains valid because the new block has the same map on all its inputs.
The predecessor's H1-H5 interface checks and U/J/K/U-inverse conclusions all pass.

## Complete cost and limits

`record_audit.py` independently interprets the predecessor exporter's MOVE, ADD,
COPY and ERASE stream in both directions. It checks all 660 columns, copied-center
lifecycle, complete frame paths, the rank histogram and cancellation-free prefix
bounds. The local histogram remains
`{1:1320, 2:1440, 4:60, 5:120, 8:9}`, including all nine rank-8 copies.
There are still 420 helpers, nine retained totals and 2,940 MOVE records.

The five-stage prefix expression is `64 * cf^3 * cb^2`. The nine-stage expression
is `2^18 * cf^5 * cb^4`, with `cf` and `cb` the native forward and reverse bounds.
Both formulas and the nine-stage invoice code are pinned in `SOURCES.json`.
The exact unrounded bounds are in the certificate. The five-stage bound still
uses 100 bits and the nine-stage bound still uses 189 bits, charged at 192.

In the inherited nine-stage, 32-replica invoice, the local-ADD term would decrease
by `9 * 32 * 24 = 6912`. The paid recursive profile is unchanged. This is a
reduction in finite circuit work and a prefix bound, not an asymptotic saving or
a measured multiplication speedup. No new owner assignment, hosted global program,
outer assembly or full frontier replay is supplied. Reusing the construction in
a selected supplier still calls for that supplier's normal complete replay.

All-size compilation, common-label and mutable-basis realization, pooled hosting,
normalized residuals, precision/tape recovery and analytic transfer remain
inherited assumptions. Exact finite replay is not a formal proof of the full
integer multiplication theorem.

## Coverage, controls and prior work

Assignment seed 5 selected the bit-supplier track and block index `5 mod 10`.
The bounded experiment applied the five recorded sum-sharing rewrites to this
one block and stopped once they produced a verified improvement. A separate
worker briefly explored bidirectional elimination and did not supply the chosen
circuit. There is no exhaustive circuit search or optimality claim. In particular,
34 is an attained gate count, not a lower bound.

Negative controls omit a block gate, alter its source, insert a doubled pair
that preserves F2 semantics but worsens the positive matrix, omit a cleanup gate,
use an illegal zero frame and reuse stale cleanup. The stale cleanup still has
the right scalar map but fails the required literal-reverse interface. Record
controls independently alter an ADD, a MOVE rank and COPY/ERASE lifecycle data.

The exact base commit is
`66849e1475c930fd7732b1a0067ffee7e1e95f60`. The source is eumemic's
[PR #543](https://github.com/CrocSwap/integer-mult-bounds/pull/543), pinned at
`2065fe4f72a914d907f1046603f5a36f17018535`. That contribution supplies the R420
construction, interleaved interface argument and bill-aware LU circuit.
Eumemic's #493 supplies its skeleton; Dylan Crow's #370 lineage supplies the word
format and exporter; DreamingOfClouds' #510 and the #463/#442 lineage supply the
retained nine-stage accounting. Original source files and notices remain intact.

[PR #661](https://github.com/CrocSwap/integer-mult-bounds/pull/661), inspected at
`9ca7aa3ab0a3260a2f36ac86b9911a31fd88bd89`, proves a fixed-order phase-B frame
bound and explicitly excludes circuit resynthesis. This contribution changes
the circuit while retaining its frame paths, consistent with that result.
DreamingOfClouds' incorporated #589 instead changes frames of the punctured bit
word and improves its paid profile. Decoder research in #620/#631 concerns a
different mechanism. Open-PR metadata and the review ledger informed the scope;
pending PR claims are not treated as accepted frontier results.

The final refresh found yongjae321's concurrent
[PR #670](https://github.com/CrocSwap/integer-mult-bounds/pull/670), at
`2e31fcad7f9ecc8b97039ecb2333e581fd725fa1`. It reports a 50-to-33-gate replacement
for block 3. The contribution here replaces the separate 46-gate block 5 and
adds exact forward equality over the integers for its five explicit rewrites.
It does not depend on #670, and this package does not certify their composition.
Both contributions improve finite work while retaining the paid frame profile.

Prepared for GitHub contributor **x0hu** with substantial OpenAI Codex assistance,
including separate Codex workers for circuit and record-level verification. No
independent human review is claimed. New files are under the repository's
Apache-2.0 license.
