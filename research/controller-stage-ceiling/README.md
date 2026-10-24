# Exact ceiling for native/thin path-controller changes

**No higher K or new supplier is claimed.** For the source-pinned PR4470,
PR4610 and PR4626 invoices, every minimal-cut path controller with 1..64
pairs, every split, and every native/thin stage subset fails at
C=0.003022. A normalized-moment monotonicity proof excludes all larger
C<1 in this family. This turns the earlier floating stage search into an
exact certificate and identifies a model change required for a substantial
increase. The selected conditional K remains 0.00302015 at the base commit.

[PROOF.md](PROOF.md) derives the complete invoice, the exhaustive max-plus
recurrence, outward integer bounds and the monotone rank-eight separator.
[RESULT.json](RESULT.json) contains the exact receipt. This does not exclude
new words, native interfaces, idle masks, coded corrections, or p>64.

The changed-model calculation also prices an optimistic combination of
PR4610 with H112's 56-rank-unit local saving. Its repair budgets at .004,
.006 and .01 are included, with the unproved native/caller compatibility
explicitly retained. A budget or positive invoice is not an implementation.

| Candidate C | Maximum optimistic rank-one repair budget |
| --- | ---: |
| .004 | 2641.1932795534 (p=64) |
| .006 | 342.1085144324 (p=37) |
| .01 | Already negative: -93.1789150428 |

These are bounded-family upper limits; source compatibility is unproved.

Reproduce from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/controller-stage-ceiling
```

The verifier uses the standard library and the pinned rational interval
engine. It does not require a solver. Controls compare small complete
censuses and literal p16 event bills, and show why dropping middle idles
or duplicating independent helper credit would give false apparent gains.
The external PR inputs are exact unmodified Git blobs, not newly admitted
native words; their provenance and heads are in SOURCES.json.

## Open next questions

1. Construct a physical H caller with a complete correction invoice below
   the recorded repair budget. Start with one actual head/hole boundary and
   check all columns, source/complement ownership and absolute phases. The
   old local H invoice and its scalar involution do not close that caller.
2. Change the native word, interface or controller topology. A further
   native/thin subset scan inside the certified family cannot reach .004.
   A new candidate must provide an exact endpoint and a complete paid bill.

## Attribution and status

Prepared by Cinna Davis with substantial OpenAI Codex assistance, Apache-2.0.
The branch recurrence is credited to the pre-existing
`research/kappa-hybrid-controller/search/direct_stage_dp.py` authors and
Cinna Davis's PR4440/PR4470 controller lineage. Cao Yifan's PR4610 supplies
the changed warp invoice; hexapode's PR4626 supplies the helper621 invoice.
Retain zxv's exact interval/native/strictification contributions and Jacob
Alan Sussman's mixed-job/compiler work. The new contribution is the exact
integer bound, the monotonicity proof and the current source-bound repair
budget. It does not assert independent human review, a formal proof-kernel
check, or a new multiplication theorem.
