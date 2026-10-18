# Selected centre phase under the scalar cut-rank bound

This package gives an independent, finite application of the conditional
dirty-host cut-rank inequality from [PR #1664](https://github.com/CrocSwap/integer-mult-bounds/pull/1664)
to one exact stage in the accepted PR #1094 word. It fills the narrower gap
that PR #1664 explicitly left open: it did not replay the selected rank-8/64
boundary. The method is a source-to-interface audit, distinct from
[PR #1643](https://github.com/CrocSwap/integer-mult-bounds/pull/1643), which
audits the selected centre geometry over F2 in a nested-tree relaxation.

The overlap check also screened [PR #717](https://github.com/CrocSwap/integer-mult-bounds/pull/717),
whose Y1/Y2 centre/cut claims use a rebuilt #656 492-helper gauge44 word.
Its source manifest is pinned in TASK.json and SOURCES.json. That is related
frame/cut work, but it is a different source from this selected #1094
480-helper emitted phase and does not apply PR #1664's scalar boundary
inequality to it; this package does not rely on it.

After the seed-52 claim, [PR #1453](https://github.com/CrocSwap/integer-mult-bounds/pull/1453)
merged an obstruction for omitted final helper climbs through the fixed
R480 cleanup, on the same selected supplier. Its theorem fixes a later
full-frame cleanup boundary and treats private centre inputs separately.
This audit instead prices the earlier centre copy/descend/scatter/clear
phase, derives its 88-by-8 rational scatter rank, and applies PR #1664's
bound to that complete interval. It adds no helper-cleanup claim; exact
overlap pins are in TASK.json and SOURCES.json.

The exact selected provider has eight carrier registers
`[92, 57, 81, 224, 11, 240, 9, 256]`. Its 176 emitted scatter edges touch 88
distinct target registers, disjoint from the carriers. The verifier replays
the full pre-centre scalar prefix on all 704 ordinary registers and obtains
rank 704 over Q; the selected 96 carrier/target coordinates therefore have
rank 96. Each carrier is at a frame of height 8 and every served target is in
the zero frame. The exact 88-by-8 matrix has entries in `{−1/4, +1/4}` and
rank 8 over Q. The verifier computes this rank directly; it does not infer a
rational rank from the separate binary frame geometry.

The emitted centre phase includes the complete private-work interval for all
eight carriers: clear a private copy at height 8, copy the carrier, move that
copy to height 0, apply its 22 rational target updates, then clear the copy at
height 0. All eight private copies are zero at entry and exit. The original
carriers remain unchanged, all 88 targets receive exactly `Y + S X`, and no
ordinary register changes frame during the phase. There is no dirty-host
credit in this scope, so the endpoint term is zero. The PR #1664 conditional
formula gives

```text
transport mass >= H_end + q * rank_Q(S) = 0 + 8 * 8 = 64.
```

The exact emitted transport mass is also 64: eight height-eight descents.
Thus this source-bound interface is tight for the inherited inequality. The
phase contains 176 target ADDs and the private-copy setup/cleanup as well;
the reported 64 is specifically the frame-transport component, not the full
ADD/NEG invoice. The result does not identify transport slack that could be
removed from the selected word.

## Reproduce

From the repository root, with Python 3.12 and the standard library:

```sh
python3 -B research/selected-centre-cutrank-seed52/verify.py
python3 -I -O -B research/selected-centre-cutrank-seed52/verify.py
```

Expected output:

```text
PASS_SELECTED_CENTRE_CUTRANK_APPLICATION centres=8 targets=88 entry_rank_Q=96 rank_Q=8 floor=64 transport=64 controls=7
```

The registered check is:

```sh
python3.12 -B scripts/research_package.py --package research/selected-centre-cutrank-seed52
```

The optimized isolated command must emit the same marker and exact receipt.

The verifier authenticates the selected replay archive and its two compressed
provider members, interprets exact rational scalar operations, checks the
complete source/target/private boundary, and compares its output to
[EXPECTED.json](EXPECTED.json). Seven controls cover a missing edge, wrong
source frame, nonzero target level, omitted scratch cleanup, missing source
column, dependent entry data, and the difference between Q-rank and F2-rank.
The controls are finite replay checks, not a proof of the universal lemma.

## Pins, scope and limits

The exact base is main commit
`418e40eb2572d930b58c1cf9b82b41c0fc7ee08d`. The accepted selected record at
that base is `836330098538459/500000000000000000` (approximately
`0.001672660197076918`), still complex-binding. The selected PR #1094 source
head is `0fc329d0bec93ca7cd288eaea1295172e8789810`. Archive/member SHA-256
pins, the exact selected source inventory, and immutable predecessor head and
blob pins are recorded in [SOURCES.json](SOURCES.json).

This is an independent application of PR #1664's written inequality, not a
machine-checked proof of that inequality. It assumes the scalar common-frame
transport contract and its price rule from that audit. It checks only the
selected PR #1094 centre phase. It does not modify the centre schedule,
change a paid supplier profile, verify a dirty-host credit, establish
production admission, rerun the complete selected construction, alter the
accepted record, or prove a multiplication theorem. No new kappa is claimed.

The scope was narrowed after overlap review: the broad batching/restoration
route overlaps the read-free/composable-family result in
[PR #1155](https://github.com/CrocSwap/integer-mult-bounds/pull/1155), and
the remaining two-root restoring-pass question overlaps the immediately
preceding [PR #1675](https://github.com/CrocSwap/integer-mult-bounds/pull/1675)
and [PR #1651](https://github.com/CrocSwap/integer-mult-bounds/pull/1651)
work. The selected centre application instead checks the explicit unfilled
scalar-boundary interface. The
[seed-52 claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1516#discussioncomment-18917138)
was posted on the coordination discussion; it will be updated with this
result after the final overlap refresh.

## Open next questions

Applying the same inequality to a changed centre implementation would require
an exact Q scatter map and the complete typed boundary, including any
nonzero dirty-host endpoint gauges and all preparation and cleanup. That
could reveal whether a new implementation avoids compulsory transport, but
this package includes no such candidate. The first step is a source-pinned
interface replay for one changed local program; physical/production
admission, wrapper pricing, and selected supplier integration remain
separate blockers.

## Credit

Credit Rohan Arun and the selected PR #1094 construction lineage for the
provider and emitted word; DreamingOfClouds' related legacy centre/cut work
in PR #717; Ali Romman and the disclosed Codex-assisted work in PR #1453 for
the adjacent fixed-cleanup obstruction; Dennis (@antunishdPursuit) for the
complementary selected-word F2 tree audit in PR #1643; and Andrey Mas for
the conditional scalar cut-rank proof in PR #1664. Prepared by Cinna Davis
(@1337isnot1337) with substantial OpenAI Codex assistance in scope selection,
exact replay code, source handling and exposition. No independent human
review or proof-assistant verification is claimed. New work is Apache-2.0;
the pinned predecessor sources and notices are unchanged.
