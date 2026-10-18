# R420 block 9: a 24-gate integer factorization

**Finite bit-circuit improvement; no new kappa.** Eumemic's
[PR543](https://github.com/CrocSwap/integer-mult-bounds/pull/543) R420 word has
a 38-XOR phase-B block on twelve source registers. This package replaces it
with **24 XORs**, with exactly the same ordered output matrix over the
integers. Replacing the corresponding literal reverse cleanup saves another
14 XORs. All 660 native input columns, including arbitrary helper dirt, pass;
the complete five-, nine-, and eleven-stage column checks also pass.

The replacement adds no helper, source-access operation, copy, frame change,
or recursive child. Every register's physical frame path is identical. The
full local word uses **26,888 scalar ADDs instead of 26,916**, and the
reverse cancellation-free prefix bound decreases from 2,270,064 to 2,234,964.
The paid profile and rounded prefix budgets stay the same.

## Reproduce

From the repository root, with Python 3.11+ and a C++17 compiler with Boost
headers:

```sh
python3 -B research/r420-block9-factorization/verify.py
```

No Python packages, solver, network access, or discovery search are required.
The four C++ checker builds run sequentially. The final line is:

```text
PASS_R420_BLOCK9_FACTORIZATION gates=38->24 native_adds=26916->26888 columns=660/900/1380/1620 rank_mass=5112
```

The driver creates a unique directory under `build/`, containing the rebuilt
word, exported records, complete checker receipts, logs, environment details
and `verification.json`. Use `--output PATH` to choose a fresh directory.
It verifies every proof-relevant field against [CERTIFICATE.json](CERTIFICATE.json).
Gzip output is compared by canonical decompressed JSON, not container bytes.
`--write-certificate` is an explicit development operation to regenerate the
expected certificate; it is unnecessary for verification. Input packages and
the selected frontier are never rewritten.

## Exact object and algebra

The original half-open slice is **B[559:597]**, zero-based block 9, frame 551
of rational rank four. Matrix row and column order is:

```text
8, 13, 33, 39, 42, 47, 80, 85, 88, 94, 114, 119
```

There is no outside read interleaved within this block. Operations in
[CANDIDATE.json](CANDIDATE.json) are pairs `(a,b)` of indices into this list,
meaning `register[a] += register[b]`. They retain the original physical output
assignment. All other B gates, D, A, the retained totals and scatter stay
unchanged. C is regenerated as the literal reversed list of all source/helper
destination gates in A followed by B, at the full frame, exactly as required
by PR543's H4 interface.

Let `T_ab = I + e_a e_b^T`, with `a != b`. For a chronological gate list
`g_1,...,g_l`, its positive integer transfer is
`M = T_{g_l} ... T_{g_1}`. Direct exact multiplication gives the same M for
the original and replacement lists. Hence the block has the same linear map
over every commutative coefficient ring, including F2, on arbitrary input
registers. The signed inverse, using the reversed list with negative
coefficients, is also identical. This is a block identity; the complete
dirty-restored word is certified over F2, not claimed to have its defining
endpoint over the integers.

For norm accounting, let R be the transfer of the **positive** reversed gate
list. This is different from the signed inverse. The certificate checks
`R_new <= R_old` entrywise, with **22 strict entries**. Thus
`R_new M <= R_old M`, with **102 strict entries**. The unit-input maximum for
block followed by positive reverse falls from **973 to 137**. Every matrix
entry is stored and recomputed with unbounded Python integers.

For any nonnegative vector of entry bounds, endpoint domination follows by
matrix multiplication. Within an addition-only block, every bound coordinate
is nondecreasing, so the endpoint also bounds every intermediate prefix.
This compares maximum prefix bounds, not intermediate steps with the same
gate index. The unchanged exterior ADD, COPY and ERASE operations are monotone
on nonnegative bounds. Domination therefore propagates through the whole
native word. Reversing the whole word exchanges the two changed segments;
the same forward equality and reverse domination apply. The independent
record interpreter and inherited C++ implementations confirm both complete
prefix calculations.

## Cost accounting and limits

| Quantity | Original | Replacement |
|---|---:|---:|
| Selected block ADDs | 38 | 24 |
| Phase-B gate records | 837 | 823 |
| Literal cleanup gate records | 2661 | 2647 |
| Complete native scalar ADDs | 26916 | 26888 |
| MOVE records | 2940 | 2940 |
| Full-frame COPY / ERASE episodes | 9 / 9 | 9 / 9 |
| Helpers / retained totals | 420 / 9 | 420 / 9 |
| Local forward norm bound F | 144651 | 144651 |
| Local reverse norm bound B | 2270064 | 2234964 |
| Five-stage prefix bound bits | 100 | 100 |
| Nine-stage prefix bound bits / charged bits | 189 / 192 | 189 / 192 |

The complete paid histogram, including all nine rank-eight COPY charges, is

```text
H = {1:1320, 2:1440, 4:60, 5:120, 8:9}; rank mass = 5112.
```

It accounts for every source, target and helper climb, the final climbs,
and the copies. Consequently the recursive moment remains exactly

```text
1320 + 1440 * 2^p + 60 * 4^p + 120 * 5^p + 9 * 8^p.
```

The 28 saved ADDs are fourteen at the original rank-four block frame and
fourteen in its rank-eight cleanup. No computation or restoration is moved
to an unpriced private row. The unchanged compensation, scatter, other local
gates, source reads, copy/erase lifecycle, routing and recursive children are
all retained in the rebuilt word and checked record stream. This is a complete
local event/profile comparison; it does not infer costs from gate count alone.

The pinned five-stage bound is `64 F^3 B^2`. The inherited nine-stage template
uses `2^18 F^5 B^4` (18 bridging shears); its invoice rounds the bit count up
to a multiple of 64. Both exact integers are in the certificate. In the
nine-stage, 32-replica invoice's scalar term
`unit = 9 * 32 * local_additions + bridge_additions`, the reduction would be
**8064 ADDs**. The 2160 bridge additions per unreplicated nine-stage word,
all 81 copied-center episodes, and their reverse semantics are checked by
the cohort replay. Those bridges and copies are retained, not eliminated.

The prefix formulas and invoice are source-pinned, but a new globally hosted
owner program, physical invoice and outer assembly are **not** supplied here.
No new bit saving or multiplication kappa follows from this finite operation
reduction. Installing it into a supplier requires the normal full hosting,
invoice and assembly replay and updated bindings. In particular, the selected
base certificate is PR626 with PR543 at
`kappa = 51110230636731/31250000000000000`, and its actual assembly is
complex-bound. This package does not change that selection.

The inherited all-size compiler, common-label/mutable-basis realization,
pooled hosting, normalized residual, precision/tape/exact-recovery and analytic
transfer assumptions remain. The checks here are finite certificates, not
a formal proof of the full multiplication theorem or a runtime benchmark.

## Search and verification coverage

Assignment seed **19** came from operating-system randomness. It selects the
bit-supplier track, the second of the three candidates below via `19 mod 3`,
and block 9 via `19 mod 10`.

The nomination starts from the original positive 12-by-12 matrix. A terminal
gate can be removed by subtracting one componentwise dominated row. An initial
gate can be removed by subtracting column a from column b. For the latter,
`M (I - e_a e_b^T)` removes the chronological first gate `a += b`. Each
subtraction keeps entries nonnegative and all diagonal entries positive.
The search records initial gates in removal order and terminal gates in
reverse removal order. If the residual reaches I, this reconstructs M exactly.
These restrictions define a search class; they are not claimed necessary for
all XOR circuits or even sufficient for every remaining matrix to factor.

The deterministic seeded walk selects among legal subtractions using five
greedy/randomized weighting modes. It completed **2000 trials**: 372 reached
I, 18 stopped with no legal subtraction, and 1610 reached the current-best
gate budget without reaching I. Of the 372 exact integer factorizations, 236
passed reverse domination. Improvements occurred at zero-based trials 6
(25 gates) and 20 (24 gates). The fixed trial count is the stopping rule.
No exhaustive circuit search or minimality of 24 is claimed.

```sh
python3 -B research/r420-block9-factorization/search.py --seed 19 --trials 2000 --output NEW-candidate.json
```

This reproduces the frozen candidate on the recorded Python environment.
Floating-point randomized scores nominate circuits only; verification neither
imports the search nor trusts its discovery trace.

The verification layers are:

1. Integer block transfer, signed inverse and entrywise positive-bound checks.
2. PR543's exact E8 label, rational-frame, all-column and H1-H5 interface checks
   on both complete native words.
3. A separate standard-library interpreter using fraction-free ranks and
   **one input column at a time** in active-row sets, on all 660 columns in
   both orientations. It reconstructs every exported MOVE/ADD/COPY/ERASE
   record, the frame paths, paid profile and positive prefixes. It imports
   no predecessor checker or search code.
4. The unchanged official C++ legality checker and complete five-, nine-, and
   eleven-stage column checkers on both words: respectively 900, 1380 and
   1620 physical input columns, with 6, 18 and 24 omitted-bridge controls per
   word. The C++ and separate Python prefix/profile results must agree.

Fifteen new negative controls cover bad source/dependency pins, a new register,
self XOR, an omitted gate, permuted output assignment, an F2-neutral positive
inflation, an integer-correct 25-gate factorization with a worse positive reverse,
a corrupted block with matching cleanup, omitted cleanup, stale literal
cleanup, an illegal zero frame, missing dirty compensation, a missing ERASE,
and a false paid MOVE rank. The stale-cleanup control deliberately passes
F2 endpoint replay but fails H4; it is not described as a scalar counterexample.
The reverse-inflation control passes the gate-count improvement and forward
integer equality checks, then fails the verifier's reverse-cost condition.

## Scope selection, pins and attribution

Base commit: **66849e1475c930fd7732b1a0067ffee7e1e95f60**.
[SOURCES.json](SOURCES.json) records SHA-256 and Git blob IDs for consumed
predecessor sources and context certificates. PR543's reviewed source head is
`2065fe4f72a914d907f1046603f5a36f17018535`.

Three narrow candidates were considered: fixed-order R420 phase-B frame
reassignment; integer resynthesis of block 9; and resynthesis of a block in
PR589's punctured R439 word. The first is closed by
[PR661](https://github.com/CrocSwap/integer-mult-bounds/pull/661), inspected at
`9ca7aa3ab0a3260a2f36ac86b9911a31fd88bd89`; its theorem explicitly excludes
resynthesis. The third has a different supplier/dependency chain. The chosen
experiment changes the scalar factorization rather than reopening the closed
frame-reassignment class.

The 497-open-PR snapshot and base review ledger were checked. Related pending
[PR670](https://github.com/CrocSwap/integer-mult-bounds/pull/670), at
`2e31fcad7f9ecc8b97039ecb2333e581fd725fa1`, reduces **block 3** through local F2
rewrites; [PR674](https://github.com/CrocSwap/integer-mult-bounds/pull/674), at
`1b01fd8b135fb2c458554fbbbab4338336bf366d`, reduces **block 5** through five
explicit sum-sharing rewrites. This contribution treats **block 9**, uses
matrix-level bidirectional factorization, and supplies complete cohort replays.
Neither pending PR is an execution dependency; their composition is not
certified here. Final overlap metadata is recorded in [VALIDATION.json](VALIDATION.json).

The final anonymous refresh at 2026-10-13 04:07 UTC found
[PR686](https://github.com/CrocSwap/integer-mult-bounds/pull/686), inspected at
`23dcb610c2b156b76b9d599ea296c3cbde224b2d`. Mikhail R. Gadelha's contribution
shares one dirty-helper pair in phase D and restores it before A. It changes
a separate phase and interface; it neither replaces nor certifies block 9.
No composition with it is claimed. The refresh covered the 100 most recently
updated open PRs in addition to the initial 497-PR snapshot.

Sibling lane intmult-b studies the asymmetric Hurwitz ten-line pairing-rank
question; lane intmult-c factors R420's frame-zero dirty compensation D.
Neither concerns this block. The earlier
[PR677](https://github.com/CrocSwap/integer-mult-bounds/pull/677) studies restored
native-query DATA shears and recursive workspace/query costs, a different
object and algebra. All claims present at selection were read; both siblings'
later claims were also read and checked before handoff.
The claim is local because this environment has no GitHub write access.

Credit to **eumemic** for PR543's circuit, source plan, integer norm objective,
interleaved interface and exact checker, building on PR493; **Dylan Crow** for
the PR370 word/exporter lineage; **DaysSky** for the bridged cohort checker;
**DreamingOfClouds** for the PR503/510 and PR463 nine-stage pricing;
**Zhihao Chen** for PR425's interface; **Chafik Boukhalfa** for common-label
and hosting/emitter work; and the cumulative authors in the
[selected maintainer review](../../docs/research/community-k492-review.md).
Related block-reduction contributions retain their separate credit above.

Submitted by **@commdata2338** with substantial AI assistance: **OpenAI Codex**
(GPT-6-Astra) did the nomination, proof, implementation and verification, and
Claude Code packaged the submission. No independent human review is claimed; algorithmic
cross-checks were written in the same AI-assisted session. New files use the
repository's Apache-2.0 license. Predecessor files and notices are unchanged.
