# QQ16 without early retention: an explicit expensive comparison

This gives one finite zero-early-retention decoder for the explicit comparison
requested in [PR2540](https://github.com/CrocSwap/integer-mult-bounds/pull/2540).
It reads all 224 current X/Y fields after B1, leaves those borrowed fields
untouched and returns all 224 original logical arrays in **the same F_U1
output frame** as that predecessor. It retains no owned records across B1.

The word uses a common 25-axis frame to realize both chart queries with local
native operations. The exact trade is **16 fewer early banks, 3,344 more native
rank units, 256 more cover maps and 8,368 more real scalar primitives** than
the pinned PR2540 word. The changed observation interface, native realization,
same-contract comparison and explicit stopping decision are the contribution.
Full-current invertibility itself was already known and is credited.

| Added local quantity | PR2540 | This word |
|---|---:|---:|
| Rank-one / rank-eight children | 224 / 16 | 112 / 448 |
| Native rank mass | 352 | 3696 |
| Monomial wrappers | 480 | 1120 |
| Complete cover maps | 208 | 464 |
| Real scalar primitive allowance | 17472 | 25840 |
| Owned final output banks | 224 | 224 |
| Additional owned early banks / retained values across B1 | 16 / 16 | 0 / 0 |
| Peak local owned scratch arrays | 16 | 16 |

At the same parent width, this candidate's child-moment difference has numerator
`432*8^(1-a)-112 >= 320` for `0<=a<=1`. Stop this common-frame recipe after the
comparison. Physical storage, maps, precision, hosting and the output consumer
remain open costs; no complete-cost saving, optimality, supplier admission or
new kappa is claimed. A different direct-current realization is not excluded.

[PROOF.md](PROOF.md) gives the ordered inverse, all-owner phase identity, signed
child lowering, complete local bill and remaining obligations. [WORD.json](WORD.json)
is the 4047-record literal word; [RESULT.json](RESULT.json) is its exact receipt.
All output and scratch dirt is accounted for; owned CLEARs are charged. Neither
the source F0/B1 calls nor complete cover maps are assigned zero physical cost.

## Evidence and reproduction

From the repository root, Python 3.12 and the standard library:

```sh
python3.12 scripts/research_package.py --package research/qq16-zero-retention-comparison
```

The primary checker independently implements the published forward formulas,
the emitted scalar/native word and a separate inverse formula. It checks both
inverse orders on 224 free symbols over the actual routed operator algebra,
all 224 output frames and untouched borrowed inputs, all private lifetimes,
224 exact frame-polynomial identities and 605248 independent character sums,
57344 rank-one basis columns, 256 rank-eight difference coefficients and twelve
semantic failure controls. R is reconstructed from the immutable selected scalar
prefix, and actual route bases come from the pinned selected archive.

The boundary script checks a real Git-free export, read-only default replay,
source-byte corruption before parsing, a bool/int receipt mutation and overwrite
refusal. Validation stays active under Python `-O`. Direct replay:

```sh
python3 -I -O -B research/qq16-zero-retention-comparison/verify.py
python3 -I -B research/qq16-zero-retention-comparison/test_integrity.py
```

Expected markers are `PASS_QQ16_ZERO_RETENTION_COMPARISON` and
`PASS_QQ16_ZERO_RETENTION_INTEGRITY`. Default replay regenerates in memory and
compares complete committed JSON; `--write` only creates absent receipts.
No predecessor Python is imported or executed. Complete source native F0/B1
core replay, child hosting and a supplier cold replay are outside this result.

Base: canonical main `b4560d9e7216f72b73c5aa940ac099c05e33ccf9`, priority revision 5.
PR2540 is pinned at `630d557af5088f66b45c447969cee9576600e50b`; exact copied notes
and their Git/SHA256 pins are in [SOURCES.json](SOURCES.json). The task picker,
live-overlap coverage, family decision and structured next steps are recorded in
[TASK.json](TASK.json). [Discussion2650](https://github.com/CrocSwap/integer-mult-bounds/discussions/2650)
is the canonical claim/result thread. Discussion2617's pending early-output-bank
coalescing still retains sixteen values across B1 and is a distinct question.

The registered optimized primary and all four integrity groups passed on
Windows with CPython 3.12.14. Submission was checked against canonical main
`1884c509efc004524786e9b7cfcc4aca572316d5`; the new review, guidance, selected
record and scientific input paths were checked. The guidance, selected record
and inputs are unchanged. Hosted CI and a full supplier replay are not claimed.

## Open next questions

Can a different direct-current implementation avoid most of the 448 wide-frame
conversions? First specify its same-endpoint native word and optimistic complete
bill; no such implementation is supplied here. Can a concrete caller justify a
direct decoder through priced retention or lifetime savings? First pin that
caller and the current coalescing proposal, assign physical owners and consumers
and price both alternatives. Physical hosting and complete consumer costs block
that comparison. These are scoped reopening conditions, not a new search campaign.

## Credit

Ali Romman and the credited joint-query team supplied the ordered maps and inverse.
ywz65/PR2540 and PR2511 supplied the equal-contract comparison request, retaining
starship-s/PR2443, thakrarsagar/PR2470, Ross Richardson/PR2480 and the credited
PR2456/2468/2492/2512 native geometry and source-binding methods. All original
sources and licenses are preserved. New work by Arham Tahir with substantial
OpenAI Codex assistance in derivation, implementation, verification and writing;
Apache-2.0. No independent human or subagent review is claimed.
