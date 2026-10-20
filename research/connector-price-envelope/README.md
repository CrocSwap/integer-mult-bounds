# Exact positive-price envelope for the five-source binary connector

This scoped proof, supported by a complete finite census, gives the exact bill
for every positive fixed complete-call price vector in Ross Richardson's
PR943/PR934 dirty-connector model. It extends Cinna Davis's PR1770, which gives
one unequal-source-price example with unit output prices. No new kappa or
selected-frontier change is claimed.

Let `b_j` be the price of source call `B_j`, for `j=0,...,4`, and `a_S` the price
of output call `A_S`, for each nonempty subset `S` of the five sources. Then

```
base = 2 sum_j b_j + 2 sum_nonempty_S a_S
optimal bill = base + 2 min({b_j : j=0,...,4}
                           union {a_S : |S|=3 or |S|=5})
```

The minimum has 16 irredundant linear pieces. A 74-call schedule attains each
piece. Thus some minimum-query schedule is price-optimal for every such vector;
paying for a longer word never improves this complete fixed-tariff bill.
A cheap singleton, pair or four-element output cannot pay the unavoidable
surcharge. At unit prices the result is 74, and at PR1770's source prices
`[1,4,10,16,28]` with unit output prices it is 182. These overlapping values
agree exactly; their original proofs and priority remain with the predecessors.

## Contract and claim strength

The five source rows `x_j`, 31 distinct output rows `y_S` and one connector `z`
are arbitrary dirty vectors over F2. Fixed arbitrary linear maps `B_j` and `A_S`
have compatible dimensions. The only allowed calls are

```
B_j: z   += B_j x_j
A_S: y_S += A_S z
```

The required endpoint is `y_S += sum_{j in S} A_S B_j x_j`, with sources and
connector restored. Calls preserve all other rows, restore their private
scratch and return their tape heads. Schedules are fixed independently of data
and operator entries. Outputs may be observed only after completion. There are
no combined calls, mutable sources, frame changes, extra connectors or free
copies. Prices are positive and fixed per complete call, independently of its
position, the data and the current word. Equal inverse prices hold because
these F2 calls are involutions in this interface.

The formula holds for positive real prices mathematically. The implementation
accepts positive integers and exact `Fraction` values, and rejects floats.
This is a written interface proof with a finite combinatorial dependency, not
a formal-kernel proof or a complete multiplication theorem.

## Lower bound

Specialize all maps to scalar identity maps and keep all input symbols
independent. Connector restoration forces each `B_j` count even. Every source
is requested, so each appears at least twice. The coefficient of the initial
connector in `y_S` forces each `A_S` count even; its nonzero requested mask
forces at least two calls. This gives `base`.

If there are at least 12 source calls, some source is used at least four times.
Its extra pair costs at least `2 min_j b_j`. This argument covers arbitrarily
long schedules; the enumeration does not cap their lengths.

Otherwise there are exactly ten source calls, two of each label. Project onto
this source word, and let `q_t` be its source-parity prefix. At boundary `t`,

```
z = z_initial + sum_j (q_t)_j B_j x_j.
```

Two `A_S` readouts can contribute exactly `q_s XOR q_t`. The finite lemma below
says that every such word omits at least one odd mask of size three or five.
That output needs at least four readouts, hence costs at least
`2 min_{|S| in {3,5}} a_S` above `base`. The two source-count cases give the
claimed lower bound for all schedules.

## Finite lemma and coverage

Rename labels by first occurrence. Every twice-occurring five-label word is
represented by exactly one pairing of ten positions, so there are
`9*7*5*3*1 = 945` canonical words. Renaming preserves mask weight. One bounded
iterative generator builds restricted-growth words; a second independently
pairs the least unused position. They agree on the entire word set. Prefixes
are independently computed by XOR updates and by counting each label in every
prefix. For every word the verifier enumerates every pair of prefixes and
checks that at least one mask of size three or five is missing.

The complete coverage histogram agrees with PR943:

| Covered masks, including zero | 16 | 19 | 21 | 22 | 23 | 24 | 26 | 28 | 31 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Canonical words | 42 | 120 | 180 | 56 | 45 | 220 | 110 | 150 | 22 |

Among the 22 words with a sole omission, 20 omit a size-three mask and two omit
the size-five mask. The new dependency is the odd-mask obstruction and its
price consequence; the old 945-word unit-price exclusion is credited to PR943.
The generated receipt hashes the complete sorted word/missing-mask records.

## Attainment and complete bill

For each source `j`, relabel PR943's universal twelve-toggle template to repeat
`B_j`. All 31 outputs then need two readouts. This gives
`base + 2 b_j` and 74 complete calls.

For each size-three output, choose one of the sole-omission templates and
relabel its missing coordinates to that output's mask. For the size-five output,
use the other template class. The verifier finds a four-prefix XOR for the
single missing mask, places its four readouts there, and places two readouts
for each other output. These eleven schedules give `base + 2 a_S`, again with
74 complete calls. All five sources and all 31 targets still occur.

The sixteen witnesses prove the upper bound. To prove that no linear piece is
redundant, price its repeated operator at one and all other operators at 100.
That witness uniquely minimizes the sixteen bills. A separate control prices
only output mask 3 at one: the surcharge stays 200, not two.

Each tariff must include the complete child implementation, coefficient/source
access, arithmetic, target updates, private scratch restoration, head returns,
frames and any fixed per-call instruction/dispatch price. An additional common
admission or preparation bill can be added to every candidate. Word-dependent
routing, setup, hosting or instruction costs are outside this fixed-tariff
optimum and must be priced separately before applying it to a real caller.
The witnesses reserve the same 37 root rows and use one borrowed dirty connector;
child scratch remains whatever each complete child tariff requires.

## Reproduction and evidence

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/connector-price-envelope
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/connector-price-envelope --check-source-history
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B research/connector-price-envelope/verify.py --show-witness A31
```

Any CPython 3.12 interpreter can replace the absolute local path. The registered
commands run both ordinary and optimized modes. Expected final marker:

```
PASS_CONNECTOR_PRICE_ENVELOPE paths=945 witnesses=16 basis=1184 dirty=512 price_cases=20 controls=7 no_new_kappa
```

The verifier checks all sixteen generic noncommutative operator identities.
It independently replays every witness on all 74 basis bits of the 37 two-bit
rows, in both directions, using maps that include noncommuting and singular
examples. It also checks 512 mixed dirty states, sixteen uniquely active price
pieces, unit and PR1770 prices, the cheap-even-mask control and exact rational
prices. Seven controls reject deleted source/output calls, source-only
relabeling, a wrong output destination and three invalid tariff inputs.

Receipts are generated on stdout and bind the package and declared live inputs
by SHA256. No receipt is hand-written or stored as a replacement for execution.
The verifier writes no files. Source-history availability and committed-byte
checks are distinct from mathematical replay. No selected cold replay, physical
tape execution, all-size supplier admission or formal-kernel check is run.

## Scope choice and overlap

The `connector-alphabet-change` card is explicitly changed: the alphabet and
source count stay fixed, and all complete tariffs may vary. The first working
example passed with `pairings=945 max_coverage=31 queries=74 leaves=182`.
The general price formula answers a different question from PR1770's fixed
vector. Discussion1579/PR1898 concern mutable common-B sources and a different
query/readout endpoint. PR1088 concerns a signed 3x3 interface. PR1915 adds
connector frames. Active F3 and signed-characteristic work remains separate.

The initial refreshed cache covered 336 open PR bodies and 2,956 Discussion
records with complete pagination. Targeted historical PR bodies and the
Discussion1579 result were also read. This is not a novelty guarantee or a
complete code-diff search. Sources and the original card are pinned in
`SOURCES.json` and `TASK.json`; frozen predecessors are unchanged.

The verifier uses no recursion, and every function has at most 23 lines. Its
combinatorial loops are bounded by ten source positions, five labels, 32 masks,
13 prefix boundaries, 74 calls, 16 witnesses or the finite 945-word pairing
space. Python allocation is a managed-runtime deviation: collections are
bounded by these fixed domains. No dynamic code, external solver or subprocess
is used by the verifier. Explicit exceptions retain checks under `-O`.

## Open next questions

1. Does a pinned selected-supplier caller realize this all-mask interface with
   fixed complete tariffs? Extract its 36 prices, reserved rows and output
   demands, including admission and instruction costs. That physical caller
   and a recursive-moment transfer remain missing.
2. Can a short structural proof replace the 945-path odd-mask obstruction?
   Start with the parity-separated prefix sets. This package claims only the
   complete finite dependency, not such a structural argument.

## Credit

This contribution was produced by Nick Petalas. Independent human and formal
proof-kernel review are unclaimed. New work is Apache-2.0.

Ross Richardson's PR943/PR934 supplies the query contract, prefix-difference
criterion, 945-path unit-price exclusion and twelve-toggle universal template.
Cinna Davis's PR1770 supplies the earlier exact 182-price fixture. Their source
files and notices retain their credit unchanged. The inherited lineage includes
PR889's shhxera/CubeJerry common-factor batching and Chafik Boukhalfa's PR628
dirty commutator. No predecessor executable is imported.
