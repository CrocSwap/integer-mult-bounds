# Recounted move prices and certified owner-fill headroom on the T74 PR2322 words

**Research note; no κ claim.** This note gives exact local-move decompositions, numerical price estimates and a certified packing cap for the
words of [PR2322](https://github.com/CrocSwap/integer-mult-bounds/pull/2322) (Vlado Vojdanovski). Those
words underlie the current open T74 line: #2349, #2363 and #2374, whose claim is
κ = 0.0016971949509. It answers one planning question: after owner fills, where can the next gain on
these words come from, and how large can it be?

| finding | value |
|---|---|
| **certified cap, any legal whole-helper owner fill of the PR2322 words** | **b < 0.001697195759** |
| headroom above PR2374's claim | ≤ 8.1e-10 |
| one more PR2322-type handoff (same reshapes) | +4.27e-8 each, linear up to 12 (+5.13e-7) |
| one PR2339-type low alias | −1.91e-7 |
| one PR2339-type high alias | approximately 0 (numerical LP check) |
| one (1,1)→(2) merge of two rank-1 climbs (no width change) | +1.13e-7 |
| the 26 such target merges that come with PR2339's low aliases, on their own | +2.94e-6 |

The discrete profile changes are exact. The displayed move prices are numerical estimates from floating-point LP solves and root bisections, not certified intervals. Moment-price comparisons use a = PR2374's κ; root differences use separately re-solved LPs. The owner-fill cap below has a separate exact rational dual certificate. The high-alias check `abs(net) < 1e-12` establishes numerical neutrality at this point, not an exact symbolic equality.

**Owner fills on these words are finished.** The width-aware bin-pattern LP of
[PR2387](https://github.com/CrocSwap/integer-mult-bounds/pull/2387) /
[PR2360](https://github.com/CrocSwap/integer-mult-bounds/pull/2360) is certified with an exact rational
dual and 800-bit enclosures. It caps every legal whole-helper fill of these words at b < 0.001697195759,
with a W·mu margin of 1.85e-7 and zero dual repair. The certificate does not reject PR2374's claimed
point. PR2374 therefore sits within 8.1e-10 of the cap, and further owner relocations on these words can
add at most that much.

## Mechanism

Under the frame-climb rule, a climb of d dimensions on a register pays one recursive child of rank d.
Local mass equals 1856 plus the sum of helper widths, and the total rank mass is fixed. So a move changes
b only through the **shape** of the children and through the helper widths, which act via the bin
patterns.

`move_prices.py` recounts which register pays each child in the pinned words. It checks every recount
against the word's own reported profile and width inventory, then decomposes the realized changes
exactly; the reshapes add up to the profile change with nothing left over.

- **PR2312 → PR2322.** The four handoffs are:
  - remove helpers 619/621/622/623, each (1,1,1,1);
  - X lenders 1/4/6/12 go (5,1,1,1)→(2,1,1,1,1,1,1);
  - partners 616/617/618/620 go (4,1,1,1,1)→(3,2,1,1,1).

  The local change is {1:−2, 2:+2, 3:+1, 4:−1, 5:−1} with one fewer width-4 helper: a net −1.23e-5 per
  call in 66304·mu, a small gain. The LP predicts a +1.96e-7 ceiling gain from PR2312 to PR2322; the
  realized claims gained +1.69e-7. The underlying prices, LP-ceiling differences, are what this note
  reports.
- **PR2269 → PR2339.**
  - A low alias's lender takes over the removed helper's climb: (3,2,1,1,1) is removed and the lender
    goes (1,1,1,1)→(2,1,1,1,1,1,1,1). The net local change is −h(3), but the width change costs
    +0.04137 per call through the bins, a loss of 5.5e-5 per call. Successive low aliases cost more,
    because the LP is convex; this is why all 32 cost −9.8e-6 (PR2387).
  - A high alias is numerically price-neutral in this calculation: its local −h(5) cancels the estimated bin cost to the checked tolerance.
  - The 26 targets whose climbs changed each gain exactly one (1,1)→(2) merge. That merge has no width
    effect and is worth +1.13e-7 by itself.

The independent recount (`independent_recount.py`) was written by a separate AI reviewer subagent
from a plain statement of the frame rules, with its own GF(2) code and no shared code. It reproduces
both providers' profiles, the exact PR2312→PR2322 change set and the site lists below.

## Untried sites (leads, not constructions)

- 33 helpers of the PR2322 words still climb (1,1,1,1). These are the 32 PR2226 low lenders 273..394
  plus 653.
- 12 X registers, 31 33 49 55 68 74 80 83 85 88 98 101, still climb (5,1,1,1) and lend no warp.
  These are the shapes of PR2322's four lenders before the handoff.
- Block 53 (registers 648–655) has exactly PR2322's pre-handoff pattern: helper 653 (1,1,1,1) next to
  four (4,1,1,1,1) partners 648/649/650/652. Its other three slots were already removed. PR2374 notes
  that alias 653 was dropped when 651 moved to lender 530.
- The other blocks pair (1,1,1,1) helpers with (4,1,1,1,1,1) mates.

If each extra handoff reproduced PR2322's reshapes, k handoffs would add k × 4.27e-8, up to 12 by the
lender count. Whether any of them admits a coherent rank-zero handoff (frame availability, lifetimes,
warp images, native lowering) is **not checked here**.

## Follow-up: where the target merges come from (`merge_mechanism.py`)

**Mechanism.** Checked on all 26 merged targets in both providers:

- In the PR2269 words each merged target climbs through exactly one intermediate frame that the PR2339
  words skip. For example, target 114 goes through dims [1,2,6,7,8] in PR2269 and [2,6,7,8] in PR2339.
- Every gate on the target at that skipped frame comes from a helper that PR2339 removes (608/609/610/612
  for target 114).
- Each merged target receives PR2339's anticipatory initial corrections, which run at frame 0 and pay
  nothing. In all, 26 of the 32 corrected targets merge.

So a merge is the removed helper's early interaction, replaced by a free frame-0 correction from a frame-0
lender.

**Lenders.** A frame-0 lender that takes over a FULL-ending role must climb to FULL (dimension 9 = H).
Its width therefore becomes 9, and widths can never exceed 9.

On the PR2322 words, the frame-0 helpers end at dimensions {4: 32, 7: 8, 8: 8, 9: 240}. The 32 that end
at dimension 4 are exactly the PR2226 lenders 273..394, which are PR2339's lenders. The 8 + 8 that end at
7 or 8 would hand off at dimension 7–8 into first frames of dimension 4–5. PR2339's handoff screen found
that this fails the rank-zero condition; that finding is inherited here, not re-proved.

Prices on the PR2322 words (LP-ceiling differences):

| lender take-over | status | db per alias | with one merge credited |
|---|---|---|---|
| width-4 → 9 (PR2339 pattern) | rank-zero, realizable | −1.91e-7 | −7.8e-8 |
| width-5 → 9 | no such frame-0 lender | −1.91e-7 | −7.8e-8 |
| width-7 (end dim 7) → 9 | outside rank-zero | +8.5e-7 | +9.6e-7 |
| width-8 (end dim 8) → 9 | outside rank-zero | **+1.43e-6** | +1.54e-6 |

**Answer to the second open question.** Under rank-zero anticipatory borrowing, the target merges come
only with the width-4 → 9 lender change, and the numerical screen prices such aliases negatively even with a full merge credited. The
merges cannot be separated from that change by choosing a different lender. The positive rows are a price
tag on a *changed handoff premise*: lenders ending at dimension 7–8, with 16 frame-0 candidates
(572–575, 580–583, 311, 327, 498, 500, 501, 510, 512, 513). Those prices are optimistic. They omit any
cost of raising the borrowed role's gate frames to contain the lender's frame, which also moves partner
climbs.

## Reproduce

From the repository root, standard library only:

```sh
python3 -I -B research/t74-2322-move-prices/move_prices.py --fetch          # ~16 s
python3 -I -B research/t74-2322-move-prices/independent_recount.py          # ~10 s
python3 -I -B research/t74-2322-move-prices/merge_mechanism.py              # ~11 s
```

`--fetch` fetches `refs/pull/{2312,2322,2269,2339}/head` from the canonical repository if the pinned
commits are absent. The pinned commits are fb76f799, 002304ef, b479fc55 and bf1742ae; each word file
is blob- and sha256-pinned.

Expected final lines:
- `PASS_T74_MOVE_PRICES cap=0.001697195759 handoff_db=+4.272e-08 low_alias_db=-1.906e-07 high_alias_net=0 sites=33/12`
- `PASS_T74_INDEPENDENT_RECOUNT`
- `PASS_T74_MERGE_MECHANISM merged=26 lenders_end4=32 pr2339_alias_db=-7.792e-08 takeover8_db=+1.427e-06`

`vendor/pr2387/` holds byte copies of this author's PR2387 `ceiling_lp.py` and `fill_check80.py` and the
iteration-3 enclosure code, all pinned. `move_prices.py` patches one line of `local_recount` at load time,
to record the register that pays each child. All results were run on CPython 3.14.4; the registered
Python 3.12 replay was not run locally.

## Scope and limits

This is a pricing screen on fixed, pinned words:

- Moves are priced only by their per-register climb reshapes and width change, through the bin-pattern
  LP. Windows, families and ports are dropped, so prices are ceiling differences, not realized gains.
- The cap is a certified relaxation ceiling for unsplit helpers on the unchanged PR2269 bin stock, not
  a κ.
- No new handoff or merge is constructed.
- Prices are first-order in the sense that they are measured at the PR2322 operating point. The low-
  alias row shows that the LP is convex, so large moves need a re-solve, which the script does for the
  ladder.

## Open next questions

- **Block 53 handoff.** Does helper 653 admit a PR2322-type coherent handoff to a free (5,1,1,1) X
  register, with partners 648/649/650/652? The first step is to rerun PR2322's handoff generator with
  653 as the target role. Its price is +4.27e-8. PR2374 dropped alias 653, so its lender conflict is the
  blocker to check.
- **Higher-rank lender take-over.** *(This replaces the earlier "target merges without low aliases"
  question; the answer above closes it for rank-zero borrowing.)* Can a lender that ends at dimension 7
  or 8 take over a removed width-8 helper's role if the role's gate frames are raised to contain the
  lender's frame? There are 16 frame-0 candidates on the PR2322 words, priced at up to +1.43e-6 each
  before frame-raising costs. The first step is to build one such word with the PR2339 builder,
  relaxing condition (d), then recount it with `move_prices.py`'s recount to get the real reshape cost.
- **More handoff patterns.** Which X shapes other than (5,1,1,1), and which partner shapes, give
  positive prices? The first step is to tabulate prices for every (lender shape, partner shape) pair
  that occurs in the words.

## Credits and licence

- PR2322 (Vlado Vojdanovski): handoffs and words.
- PR2312 and PR2269 (Jeremy Kothe): width exchange and borrow43 words.
- PR2374 and PR2349 (jeremykothe2) and PR2363 (mason-hale): owner fills on PR2322's words.
- PR2226 (Cinna Davis / 1337isnot1337): anticipatory borrowing.
- PR2339 and PR2387 (this author).
- PR2360 (Jeremy Diviney) and PR1129 (Ali Romman): pattern-dual relaxation.
- PR2394 (commdata2338): native anticipatory prefix.
- PR1995 and PR2013: fixed-word frame bounds.
- PR1319 and PR1297: T74 lineage.

Prepared with substantial AI assistance (Claude Code, Anthropic, Claude Opus 5.5). The independent
recount was written by an AI subagent; no independent human review is claimed. Apache-2.0.
