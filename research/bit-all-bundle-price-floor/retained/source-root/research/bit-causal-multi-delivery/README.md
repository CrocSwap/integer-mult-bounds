# A two-delivery price floor for the selected BIT word

Every original paid arrival of the selected PR7001 BIT word costs at least
its original rank tariff if replaced by at most two direct nested deliveries
from fixed, strictly earlier chart libraries. This holds in both orientations
for prices `s^t` with `0 < t <= 1`, even with free retention and free scalar
XOR at the destination. The original single transfer attains the floor.
The claim is a scoped proof backed by exhaustive finite replay. No new κ follows.

## Boundary and proof

Keep all 659 public inputs independent. For each original paid MOVE, write
`d` for its destination chart, `c` for its zero-based event index in the
chosen orientation, `r` for its rank, and `f` for its required normalized
binary row. For each chart `b`, let `V_b` span its public entrance rows
and its original paid arrivals at event indices strictly less than `c`.
The library permits these rows to be retained for free. Each direct delivery
to `d` contributes one row in `V_b` and pays rank
`s_b = |dim(b) - dim(d)|`. Its chart pair must be nested as rational
subspaces. The destination can add any row of `V_d` for free.

The row semantics and fixed libraries are those of Ali Romman's single-delivery
result. An entrance contributes its independent basis row. INIT provides zero,
cocharted ADD adds rows over F₂, SWAP preserves the chart attached to each row,
and CLEAR retires a row. A MOVE carries the normalized row to its destination.
The transpose reverses the event order and the MOVE direction, exchanges INIT
with CLEAR, and transposes the ADD. Thus the entrance rows and strictly earlier
arrivals suffice for the library at every tested event. [PR #7723](https://github.com/CrocSwap/integer-mult-bounds/pull/7723)

A bundle with donor set `S` can supply `f` exactly when
`f ∈ V_d + Σ_{b∈S} V_b`. The forward implication follows by adding the
received rows. For the reverse implication, take one component per chart
from a span decomposition and include its destination component. Two
contributions from one chart combine into one row. A donor with zero
library contributes zero.

For a bundle with positive ranks `s_i` and total rank `R > 0`,
`Σ s_i^t = R^t Σ (s_i/R)^t ≥ R^t` for `0 < t <= 1`.
A strictly cheaper bundle must therefore have `R < r`. In particular, it
can use only individually lower-rank donors. If the row is outside the sum
of **all** these donor libraries and the destination library, every
strictly cheaper direct bundle is excluded, regardless of its size.

For the cases where that sum contains the row, the verifier works in the
quotient by `V_d`. It tests every nonempty eligible singleton and every
distinct eligible pair with rank sum below `r`. The free destination
by itself is also checked. Empty libraries and repeated donors reduce to
these cases. In each test the projected row is outside the projected
donor span. Any bundle with rank sum at least `r` is already covered by the
price inequality. The original source row at the same deadline attains the
old price by the cited single-delivery result.

## Finite evidence

| Orientation | Arrivals | Excluded by the sum of all lower-rank donors | Exceptional singletons checked | Exceptional pairs checked |
| --- | ---: | ---: | ---: | ---: |
| Forward | 2,871 | 2,862 | 4,626 | 478,764 |
| Transpose | 2,871 | 2,871 | 0 | 0 |

The nine exceptions are forward rank-seven arrivals into chart 0 from
charts 510 through 518, at every eighth event from 26861 through 26925.
Their full lower-rank donor sums contain the required rows. Each sum grants every eligible donor
simultaneously, with no total-rank constraint. The quotient check
enforces the rank-sum constraint for one or two paid donors.

The replay authenticates the compressed native word, reconstructs the
chronological scalar rows, and computes rational nesting from the
chart bases and their orthogonal complements. For each arrival it
tests the donor span before adding that arrival to its destination
library. Its small control gives two donors that can reconstruct a
row together even though neither can do so alone. It also checks that
an equal-rank-sum pair is omitted from the strict budget test.

## Scope

The result covers fixed causal stocks and direct transfers of scalar XOR
forms into one original destination by its old deadline. The nine remaining
arrivals can still be tested with three or more positive-rank donors.
New charts, intermediate relays, changed helper relations, altered values
and deadlines, and adaptive changes to the libraries are outside the
contract. Storage and ordinary formation are granted, so the price floor
also holds for subclasses that charge nonnegative costs for them.

Productive targets and the remaining caller terms are kept fixed. Replacing
a paid term within this contract cannot improve its signed margin. The
selected frontier and its five assumptions remain as recorded. Physical
compiler delivery, storage and restoration, tape movement, analytic recovery,
the selected cold replay, Lean and Docker were outside this proof.

This changes the scope of `bit-helper-contract` to a paid-path relaxation of
the selected BIT supplier. [Task](TASK.json) · [Source pins](SOURCES.json)

## Reproduce

Use CPython 3.12.15 and its standard library from the repository root.

```sh
python3.12 -B -W error -X dev research/bit-causal-multi-delivery/verify.py
python3.12 -B -W error -X dev -O research/bit-causal-multi-delivery/verify.py
python3.12 -B scripts/research_package.py --package research/bit-causal-multi-delivery
python3.12 -B scripts/check_research_commit.py --package research/bit-causal-multi-delivery --check-source-history
```

Both direct modes produce this marker.

```text
PASS_BIT_CAUSAL_MULTI_DELIVERY arrivals=5742 union_excluded=5733 exceptional_singles=4626 exceptional_pairs=478764
```

In a sparse checkout, materialize this package and `research/paired-query-only-bit`.
The direct checker needs the one [pinned native word](SOURCES.json), with no
Git or network calls. The publication preflight requires full Git history.

## Open next questions

- For the nine exceptions, can three or more direct deliveries beat the rank-seven
  tariff? Start with the quotient at forward event 26861 and seek a donor subset
  with total rank at most six. The full donor sum gives no such subset or price.
- Could a relay create a lower-cost arrival under a changed causal library?
  Start with one exact intermediate chart and give its entry, delivery and
  restoration costs. The fixed-library proof grants no relay information.

## Credit

This contribution was produced by Nick Petalas. Ali Romman supplied the
fixed-library model, its single-delivery floor and the multi-delivery
question in [PR #7723](https://github.com/aliromman/integer-mult-bounds/blob/a4fd22c08058c0fef830306b2d46e4a51f091939/research/bit-causal-delivery-rank-obstruction/README.md).
Jerry Chen / CubeJerry supplied the selected [PR #7001](https://github.com/CrocSwap/integer-mult-bounds/pull/7001)
caller. Credit zxv and the retained native authors for the exact word,
DreamingOfClouds for the chain-root caller, and ToikY for the related
fixed-destination and retag bounds. The original source notices remain
with the pinned input. New material is Apache-2.0. Independent human
and formal proof-kernel review are unclaimed.
