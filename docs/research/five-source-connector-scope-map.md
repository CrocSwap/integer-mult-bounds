# Five-source connector: call counts, tariffs and changed contracts

The generic five-source, one-dirty-connector problem with all 31 nonzero output
masks already has an exact optimum for **every 36 independently positive
source/readout prices**. Start with Adam Gall's
[all-tariff theorem](../../research/connector-all-tariff-optimum/README.md),
retained in the [review through #2135](community-efficient1100-review.md).
Repricing the original alphabet or extending its word-length search does not
reopen that problem. This map connects that result to the older unit-call and
fixed-price results and identifies contracts to which it does not apply.

This is navigation at main `b5ea56e0a5ac4552166253b1fa4be0753bb38c30`, priority
revision 5. [Source bindings](five-source-connector-scope-map.json) record the
reviewed heads, retained locations and exact README bytes. The listed results
are scoped interface results; none supplies a new selected multiplication
exponent. Resolve that separate status through
[selected-result.json](../../certificates/selected-result.json).

## First identify the contract

The common starting contract has five immutable source rows, one arbitrarily
dirty connector `z`, and 31 distinct arbitrarily dirty output rows. Its only
operations are complete `B_j: z += B_j x_j` and `A_m: y_m += A_m z` calls over
F2. Each call restores private scratch and heads; `z` is restored at completion.
The word must work for arbitrary admissible linear maps, including singular
and noncommuting maps, and cannot exploit special relations among them.
Outputs are unobserved until completion. Source mutation, combined source
calls, extra connectors, frame operations and intermediate delivery cuts are
outside this starting alphabet or boundary.

| Question and exact boundary | Retained result | What to use it for |
|---|---|---|
| Original alphabet, unit complete-call prices, all 31 masks | Ross Richardson, [#943](../../research/universal-connector-boundary/README.md): minimum **74 complete queries**; no ten-source-event path covers all masks with two readouts each | The generic unit-call baseline and paired-prefix criterion |
| Same alphabet, source prices `(1,4,10,16,28)`, every readout price 1 | Cinna Davis, [#1770](../../research/weighted-connector-readouts-seed1275309492/README.md): exact **182** leaf bill; the displayed predecessor word costs 200 before relabeling | A particular complete-price fixture, not 182 for arbitrary prices |
| Same alphabet, all 36 fixed prices independently positive | Adam Gall, [#2063](../../research/connector-all-tariff-optimum/README.md): exact formula below over **all finite legal words**, with 16 minimal count profiles | The completed general tariff question; do not repeat a longer-word census |
| Each output has its own sequential delivery interval, with no writes before or after that interval | woklerx, [#1442](../../research/connector-delivery-cut-optimum/README.md): exact demand-count formula; **142** unit queries for all 31 masks | A stricter observation boundary; the offline 74-call optimum is inapplicable |
| Add arbitrary map-independent invertible connector frames, all implemented frames charged | Arham Garg, [#1945](../../research/connector-frame-73-exclusion/README.md), following Adam Gall's #1915: minimum **74 A/B map calls**, even if frame prices are zero | A map-call floor in the expanded alphabet; it is not the 36-price theorem with frame costs omitted |
| Add pair-source calls, one query depositing two sources, with both accesses charged | Aaron Wang, [#2056](../../research/connector-pair-source-path-seed2cdb/README.md): a **72-query construction**, ten-event minimum for the universal paired-readout path, and best-labeling leaf bill **182** | Separate query records from leaves; the maintainer review does not claim a general optimum over every extended-alphabet program |

All six entries have `incorporated` dispositions in the pinned
[PR ledger](pr-ledger.json). That status is a record of their scoped review,
not an independent replay of every theorem in this map. Predecessor notices
and credit remain in their original packages.

## The tariff result includes the older price examples

For source prices `b_j > 0` and readout prices `a_m > 0`, put
`H = {m : popcount(m) is 3 or 5}`. The #2063 formula is

```text
OPT = 2 sum_j b_j + 2 sum_(m=1..31) a_m
      + 2 min({b_0,...,b_4} union {a_m : m in H}).
```

Each of the 16 minimal count profiles has a 74-call witness: two uses of every
map, plus two uses of one source or one of the eleven heavy odd-mask readouts.
The unrestricted-word reduction and exact 945-pairing exclusion belong to
#2063, building on Richardson's prefix-path construction and Cinna Davis's
[#1770](../../research/weighted-connector-readouts-seed1275309492/README.md)
and [#1811](../../research/five-source-parity-hyperplanes-seed595e/README.md).
This map introduces no new lower bound or construction.

With all prices 1 the formula gives `72 + 2 = 74`. With #1770's prices it gives
`180 + 2 = 182`. It does **not** permit an arbitrary cheap readout to absorb the
surcharge: prices 10 except `a_3=1` give **722**, while prices 10 except
`a_31=1` give **704**. Weight-two mask 3 is not in H; weight-five mask 31 is.
These are the retained theorem's examples, not new experiments.

For #1442's distinct delivery contract, let `n_j` count requests containing
source j. Its optimum is

```text
2 sum_(active outputs i) c_Ai + sum_j c_Bj (n_j + n_j mod 2).
```

For all nonzero five-bit masks, every source occurs in 16 requests, so unit
prices give `62 + 5*16 = 142`. Different observation boundaries explain the
difference from 74; the two formulas do not contradict one another.

## What a new caller still has to establish

Choose the matching row before optimizing. For the #2063 row, exhibit an
actual caller with the immutable-source, unobserved-output boundary and known
complete positive prices. Add admission/layout, coefficient preparation and
root program construction, storage, reads and dispatch. Word-dependent costs
can change the best total physical schedule even when its map bill is optimal.
Do not substitute query counts for leaf bills or assume unknown costs vanish.

For pair-source operations, charge both source/coefficient accesses and prove
their implementation at the caller's ports. For frames, a 74-map-call floor
does not itself price frames or prove the all-tariff frontier survives. For
delivery cuts, retain their exact write/observation policy. Mutable sources,
additional roots, specialized maps and different target-mask families need
their own applicable results; this six-entry map is not a survey of those
families or a claim that they are unexplored.

Apply the [family expansion gate](research-family-status.md) before a dependent
implementation campaign: identify the consumer, distinguish proved costs,
constructive upper bounds and unknowns, and name the obligation the next result
can change. A local tariff optimum alone is not supplier admission.

## Validation and limits of this navigation repair

The source receipt binds the six README files and their ledger dispositions at
the stated base; frozen packages and dispositions are unchanged. The retained
#2063 verifier was replayed with CPython 3.12.7 using
`python -I -O -B research/connector-all-tariff-optimum/verify.py`: 945 pairings,
16 profiles, 3,552 dirty-basis case pairs and nine controls passed. The other
five mathematical suites, selected cold replay and formal-kernel proof were
not rerun for this documentation change. Local links and source hashes were
checked separately.

Prepared by ywz65 with substantial OpenAI Codex assistance. Apache-2.0.
