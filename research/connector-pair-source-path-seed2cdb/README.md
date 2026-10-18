# Pair-source connector calls: five-source universal path of exactly ten, and the 72-query support bound attained

**Recursive-interface construction plus exact finite exclusion; no new kappa.**
Aaron Wang, with help from opencode.

Add exactly one operation family to the connector alphabet of
[research/universal-connector-boundary](../universal-connector-boundary/README.md):
the **pair-source connector call** `B_jk: z += B_j x_j + B_k x_k`, one complete
query depositing two sources at once, charged two coefficient/source accesses
and one query record. Everything else of that Exact interface is unchanged:
dirty rows, paired readouts, restoration of `z`, no free copies.

Result on the five-source, all-31-nonzero-row matrix:

| Quantity | Fixed alphabet (predecessor) | With pair-source calls |
|---|---:|---:|
| Minimum universal source path | 12 | 10 |
| Complete queries, all-31 matrix | 74 | 72 |
| Support bound `2*(5+31)` | 72, unattainable | 72, attained |
| Source-side leaf cost, best labeling | 120 | 120 |

The query optimum in the extended alphabet is **exactly 72**: 62 paired
readouts (each nonzero row needs two `A_i` calls) plus a source path of at
least 10, and the word below attains 10. In the fixed alphabet the same
support bound of 72 was proved unattainable by the 945-pairing census, and
parity ruled out 73.

## The word

Closed walk on `F_2^5`, one step per source query, step vectors of Hamming
weight 1 (single `B_j`) or 2 (pair `B_jk`):

```text
prefixes: 0  2  3  5  13  15  30  26  10  8  0
steps:    2  1  6  8   2  17   4  16   2  8
calls:   B_1 B_0 B_12 B_3 B_1 B_04 B_2 B_4 B_1 B_3
```

The prefix set `P = {0,2,3,5,8,10,13,15,26,30}` has `P XOR P = F_2^5`
(verified two ways in `verify.py`). Place each output's two `A_i` readouts at
the two boundaries whose prefix XOR is its row mask; characteristic two makes
the dirty connector contributions cancel. Source multiplicities are
`(2,4,2,2,2)`, all even, so `z` is restored.

## Why ten is optimal

1. Each of the 31 nonzero masks needs its own unordered pair of prefixes, and
   `C(8,2) = 28 < 31`, so `|P| >= 9`.
2. A complete census of all `C(31,8) = 7,888,725` nine-point sets of `F_2^5`
   finds **zero** with `P XOR P = F_2^5`; maximum coverage is **29**. Two
   independent implementations agree (recursive DFS in the discovery script;
   `itertools.combinations` in `verify.py --full`). So `|P| >= 10`.
3. The walk is closed (`z` restoration), so `|P| <= L`; hence `L >= 10`, and
   the word attains 10.

This is a finite computational exclusion for the stated interface, not an
impossibility theorem for other circuit models.

## Pricing (predecessor fixture)

Fixture: B factor leaf prices `1, 4, 10, 16, 28`; each `A` leaf price 1; every
call doubled for the inverse in the complete cost; dispatch `D` paid per root
query. Renaming sources preserves coverage, so free relabeling is granted on
both sides.

| Schedule | Queries | B leaves (min relabeling) | Total leaves |
|---|---:|---:|---:|
| This word, best labeling | 72 | 120 | 182 |
| This word, fixture labeling | 72 | 126 | 188 |
| Predecessor ten-call path | 74 | 118 | 182 |
| Predecessor twelve-call path | 74 | 120 | 182 |

At the best labeling this schedule ties the predecessor's leaf cost exactly
and saves 2 dispatch records, so the completed cost is strictly lower for any
positive per-query dispatch. At the fixed fixture labeling it pays
`+12` leaf charges (doubled) against `-2 D`, favorable iff one query's
dispatch/dispatch-record cost exceeds 6 leaf-price units. The tie at the best
labeling is optimal among 72-query schedules: a length-10 source path needs at
least one pair call (pure-single ten-call paths are excluded by the
predecessor's 945-pairing census), so its weight sum is at least 12, and
weight sum 12 with even multiplicities gives exactly this multiset.

## Verification

```sh
python3 -I -O -B research/connector-pair-source-path-seed2cdb/verify.py
```

Expected: `PASS_CONNECTOR_PAIR_SOURCE_PATH`. Checks the word (two coverage
recomputations), the dirty replay at `L = 1,2,3` with seeded dense
nonsymmetric noncommuting `F_2` maps and arbitrary dirty `x`, `z`, `y`
(exact boundary on all 31 outputs), three mutation controls (dropped call,
mutated step, misplaced readouts) that must all be rejected, and the pricing
numbers.

```sh
python3 -I -O -B research/connector-pair-source-path-seed2cdb/verify.py --full
```

Expected: `CENSUS {"sets": 7888725, "covering": 0, "max_coverage": 29}` then
`PASS_CONNECTOR_PAIR_SOURCE_PATH_CENSUS`. This is the exact nine-point census
behind `L >= 10`; it takes a few minutes.

## Scope and limits

- Exactly one added family (`B_jk`); a different extension is a different
  question. Pair calls are charged, never free.
- No instance of this interface is claimed inside the selected supplier; this
  is not a kappa claim and the selected record is unchanged. The `a < D/E`
  diagnostic is not applicable: no supplier moment or recursive profile
  changes here.
- The necessity side (62 readouts, two per nonzero row) inherits the
  predecessor's specialization argument unchanged; only the source-path side
  changes.
- The census covers nine-point sets exhaustively and finds the length-10 word
  by seeded random search over covering sets (seed 4242, trial 911); minimality
  rests on the census plus the counting bound, not on search exhaustion at 10.

## Open next questions

1. **Do triple-source calls `B_jkℓ` reach the readout-dominated floor?** The
   source path could drop toward 8 or 9, but each call's leaf charge grows;
   the same prefix-set method answers it. Blocker: none; a bounded census of
   weight-3 steps is the first step.
2. **Six sources with pair calls.** The predecessor stops at the five-source
   boundary. For six sources the counting bound gives `|P| >= 12`
   (`C(11,2) = 55 < 63 <= C(12,2)`); does a pair-call universal path of length
   12 exist? Blocker: the set census grows to `C(63,11)`; it needs a walkwise
   search rather than a setwise one.
3. **Common-label realization of pair calls.** The predecessor leaves
   realization open for single calls; a pair call needs two coefficient
   accesses in one query record, which a real compiler must price.

Predecessor credit: `research/universal-connector-boundary` (fixed-alphabet
four/five-source boundary, 945-pairing census, 74-query optimum) and PR934's
three-by-three result. Claim thread:
https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18930631
