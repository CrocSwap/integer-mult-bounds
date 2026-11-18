# Exact phase entry for the actual denominator-52 inverse

After at most four coins, **2,304 of the 2,704** actual residue pairs have
a unique complete-tail entry into the existing denominator-13 arithmetic
core. They are exactly the pairs with neither residue divisible by 13.
The entry changes both core parameters and phase; it preserves labels and
live-node indices. The 2,304 inputs use 1,560 distinct entry recipes.

The remaining cases split into 96 endpoint tails, 288 mixed tails and
sixteen pairs with no tail. This is a complete classification of the stated
interface, not an exclusion of other samplers. An explicit source witness
also shows why the core's cyclic inverse cannot simply replace the prefix
entry inverse. A separate boundary protocol is still required.

Read [the proof and exact limits](PROOF.md), [the entry formula](interface.py),
[all pair certificates](RESULT.json), [the checker](verify.py),
[source pins](SOURCE-PINS.json) and [source credit](CREDITS.md).

Python 3.12, standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/inverse52-phase-entry
```

Both registered commands print:

```text
PASS_INVERSE52_PHASE_ENTRY
2704 actual pairs; 2304 pairs with a unique core entry; 96 endpoint tails; 288 mixed tails; 16 dyadic pairs
22464 backend phase signatures; 43264 literal prefixes; 1437696 tail edges
4428 entry inverse checks; explicit first-entry/period-return collision
```

The independent inventory reconstructs all core phase signatures from
literal source graph outputs. The unchanged runtime circuit verifier and
its fixed-pair predecessor also run. The actual source mode columns give
all 2,704 bounded-owner witnesses. Native and selected cold replays, the
source-domain kernel fixture suite, Lean and Docker were not run.

No new kappa or physical saving follows. Prefix execution, parameter and
phase preparation, boundary control, tape movement, output retention,
conditional freshness and the complete caller invoice remain unpriced.
The selected frontier and all five framework assumptions remain unchanged.

## Open next questions

- Can a stated counter or owned-marker protocol implement the proved
  prefix/tail entry and return, with all preparation and cleanup charged?
  Use the actual nonadaptive window and retain the original parameters.
- Which exact service handles the 288 mixed tails under the same label
  and node contract? Their residues are nonzero multiples of 13, so they
  do not fit the existing unit-phase nonzero-pair core.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
