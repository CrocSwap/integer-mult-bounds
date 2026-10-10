# What instantiating the bit rank-6 bank rung would take

The cheapest way to beat the frontier is [beats.py](beats.py)'s first strict rung:
absorb the bit word's rank-6 child family into width-72 banks, worth **+2.1672%**
(`kappa` 6.831904550366e-4 → 6.979968750671e-4). This note asks what would have to
exist for it to be a construction.

```
python3 -B instantiate.py           # ~2 s, writes instantiate.json
python3 -B instantiate.py --check   # byte-for-byte comparison with it
```

Everything below is derived from the frontier certificate's own three-copy row; the
supplier's published bank proof is vendored beside it
([coordinated-bank-proof.md](references/queue/coordinated-bank-proof.md), hashed in
[SOURCE.json](SOURCE.json)) and read item by item.

## The schedule, and the condition that decides it

A bank is a width-`m` coordinate-block partition, so a family absorbs into banks only
when its own volume fills whole banks. For rank `r` on width `m` that has a one-line
form: `m/r` blocks fill a bank, so the family's child count must be **divisible by
`m/r`**. On the frontier's two words that leaves exactly four families:

| word | rank | blocks per bank | banks (three copies) | children divisible by `m/r` |
| --- | ---: | ---: | ---: | --- |
| bit (m=72) | **6** | 12 | 1008 | yes |
| bit (m=72) | 8 | 9 | 816 | yes |
| bit (m=72) | 18 | 4 | 999 | yes |
| complex (m=66) | 11 | 6 | 177 | yes |
| bit | 1, 2, 3, 4, 9, 12 | 72, 36, 24, 18, 8, 6 | — | no |
| complex | 1, 2, 3, 6 | 66, 33, 22, 11 | — | no |

Rank 4 is the certified block size and rank 1 is the biggest mass in the word, but
neither has a volume that fills whole banks, so neither is available without a mixed
tiling. The stride-6, 9 and stride-4 partitions are the ones the arithmetic admits.

## The rung's arithmetic, re-derived

| quantity | value |
| --- | --- |
| family | bit rank 6 |
| children | 12,096 over three copies = **4,032 per physical copy** |
| blocks per bank | 12 (stride 6 on width 72, `12 × 6 = 72`) |
| blocks needed | 4,032 per copy — **exactly one block per absorbed child**, count for count |
| banks | 1,008 over three copies = **336 per copy**, integral |
| removed rank volume | 72,576 |
| stock `W` | 56,402 → 55,394 (the fall is the bank count, by the row identity) |
| rank mass | 4,055,136 → 3,982,560 |
| deficit | 5,808, **unchanged** |
| retained ledger | 21 families, max child 22 |
| certified saving | 6.83657523331095e-4 → **6.98484415006068e-4** |
| kappa | 6.831904550366e-4 → **6.979968750671e-4** (+2.1672%) |

The one-block-per-child identity is the useful structural fact: the normalizer's
targets and the absorbed children are equinumerous, so no child needs two blocks and
no block is left half-used at this rank. The certified proof's own absorption is not
like that — it removes 2,200 rank-60 gauge exteriors whose volume (396,000 over three
copies) fills 5,500 banks, and it needed nine physical replicas to make its
stage-private allocation integral. Here the per-copy count is 336, so if the rank-6
dirt is stage-private in the same three-family way the allocation is 112 banks per
stage and needs no replicas. **That is an inference**: no pin says the rank-6 dirt is
stage-private.

## What the published bank proof already covers

The proof is a finite verification of a *different* absorption — the rank-60 entrance
exteriors, one per selected gauge — but several of its items are stated for any
partition, so the rung inherits them:

* **The projector algebra.** `S_P S_Q = S_(P+Q)` and `S_P² = I` are proved by direct
  expansion for *any* finite disjoint projector partition summing to `I`, and chart
  conjugation telescopes for any common invertible weighted chart. A stride-6
  partition needs no new algebra; it is a new instance of the same construction.
* **The column check.** 144 columns of the two-bank address map over `F2` and over
  `Z`, for the endpoint and its inverse, rejecting a missing or repeated last block in
  both rings. `144 = 2 × 72` independently of which blocks fill the bank.
* **The moment-envelope parity.** The rare-class fraction `10^-16`, the fallback
  `32 × 72²` children per edge and the positive atom/row-adapter toll on its own
  `10^-24` grid are all unchanged by this rung, and two rational log/exp enclosures
  certify the accepted moment and reject the adjacent `10^-18` point — which is
  exactly what `beats.json` and `instantiate.json` already do with the supplier's own
  enclosure implementation.
* **The assembly.** 47 strict constraints and 7 margins at PR207's parameters. The
  rung is bit-binding, so the complex budget is untouched.

## What it does not cover, and what is missing

* **The normalizer.** The certified proof's banked items are the 2,200 rank-60 gauge
  exteriors, and each one's *gauge itinerary* supplies its address. The rank-6 family
  is interior dirt with no registered gauge address, so the child-to-block map has to
  be built rather than inherited.
* **The inventory — the real gap.** No pinned package enumerates the word's rank-6
  children: not their frame or chain occurrences, not a bijection onto the 4,032
  blocks per copy, and not a proof that nothing else in their ledger row moves. This
  is the same blank shape as the complex rung's inventory obligation, and it is
  smaller: one family of one word, whose counts, bank schedule and divisibility
  condition are pinned by this file.
* **Charts and witnesses.** Integer kernel bases with fraction-free inverses and
  replayed elementary factors for the stride-6 frames, and distinct integer Gram/prime
  witnesses for each of the 1,008 three-copy blocks (the certified supply is per block
  *frame*, not per bank).
* **The conditional interfaces.** The inherited all-input weighted compiler, the
  completed-core routing, the stage cover, local-ring precision/recovery, prime
  supply, uniform setup and the all-size analytic/tape contracts stay conditional; the
  bank proof discharges none of them, and neither does this package.

## Verdict

The rung is the closest of the pinned targets to being buildable: its algebra is
inherited from a published proof rather than invented, its allocation is integral
per copy (so it does not need the replicas the certified bank used), the block
arithmetic is exact and pinned here, and the saving and kappa are certified with
tooling that already exists. What stops it is not mathematics but an inventory: the
dirt it removes has never been enumerated anywhere in the queue, exactly as the
complex word's rank-11 family has never been. Whoever writes that enumeration — one
family, one word, 4,032 items per copy — hands this rung to the certified harness with
the stride changed from 4 to 6.
