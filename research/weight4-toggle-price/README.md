# A weight-4 connector step costs `72o + 76p`

**Scoped proof, three exhaustive finite censuses, and an attaining schedule.
No new κ.** Selected κ stays `363005817/100000000000`.

On the five-source, 31-row dirty connector, every nonempty source subset is
allowed as one toggle. Dispatch price is `o >= 0` and each source or readout
addition costs `p > 0`. The DUO schedule costs `72o + 74p`. This package
answers the weight-4 half of the open price question in
[PR #6695](https://github.com/CrocSwap/integer-mult-bounds/pull/6695): every
correct schedule that uses at least one weight-4 toggle costs at least
`72o + 76p`, and a schedule attains that price. The weight-4 extension is
therefore exactly `2p` more expensive than the DUO point for every `o >= 0`
and `p > 0`. It is not a favorable alphabet extension.

The same counting split as the weight-3 price applies. A weight-4 step
changes the parity, so the addition floor is already `76` before any census.
The equality rows are a different finite domain. Two of them are nonempty
and one of them attains both floors at once.

## Interface

The batch is the one in `research/universal-connector-boundary`: five
read-only sources, one arbitrarily dirty connector `z`, and all 31 nonzero
output rows. A call `T_S` adds `sum_{j in S} B_j x_j` into `z` and costs one
dispatch plus `|S|` additions. A readout `A_m` costs one dispatch and one
addition. Maps are arbitrary `F_2`-linear maps. They need not commute or be
invertible. Private scratch and tape heads are restored by each call. Outputs
are unobserved until the batch completes. There is no joint readout, second
connector, frame change, or source mutation.

The lower bound uses the identity-map, one-bit specialization, which is
necessary for a schedule that is correct for every admissible map and every
dirty input. The attaining schedule is replayed on formal symbols, so it is
correct for every map, and on explicit dirty vectors.

## Result

Let `T` be the number of toggles and `W` their total source additions. Prefix
differences are translation invariant, so the initial prefix may be taken to
be `0`. Let `u` be the number of nonzero rows that are not a difference of
two prefixes. Each of the 31 rows needs an even positive number of readouts,
because the initial dirt in `z` is arbitrary, and a row that is not a prefix
difference needs at least four. Thus the readout count is at least `62 + 2u`,
the query count is `Q >= T + 62 + 2u`, and the addition count is
`A >= W + 62 + 2u`.

**Theorem.** Every correct schedule with at least one weight-4 toggle has
`Q >= 72` and `A >= 76`. Both bounds are attained by the same schedule, so
the minimum price is `72o + 76p`. The recomputed DUO schedule, which uses no
weight-4 step, costs `72o + 74p`.

A positive per-call surcharge on weight-4 toggles, beyond the four source
additions already counted, would make this schedule strictly worse. The
operation is not treated as free.

## Proof

Closed walks in `F_2^5` have even `W`, because every source incidence is
even. One weight-4 step and `T - 1` singletons sum to `T + 3`, so
`W >= T + 3`. When `T` is even, `T + 3` is odd and is not a legal addition
count, so `W >= T + 4`. Equivalently, `W_min(T) = T + 3` for odd `T` and
`W_min(T) = T + 4` for even `T`. Extra heavy steps only increase `W`.

Let `s` be the number of distinct prefixes. Then `T >= s`, and `u` is at
least `max(0, 31 - C(s, 2))`. For `s <= 8` this counting bound is already at
least 3. For `s = 9` counting allows a cover, but none exists:

Differences are translation invariant, so one prefix may be moved to `0`.
A covering set spans `F_2^5` and therefore contains a basis. Every linear
automorphism preserves the property of being a difference basis, and
`GL(5, 2)` can send any ordered basis to the standard basis. The other
three points then lie among the remaining 26 vectors. All `C(26, 3) = 2,600`
such sets were checked. None covers. The same enumerator finds 80 covers
with four extra points, the ten-point normal-form count recomputed by
PR #6695, so the empty nine-point result is not an empty search.
Consequently `u >= 1` whenever `s <= 9`.

Under those floors, every pair `(T, s)` with `1 <= T <= 40` and `1 <= s <= T`
has `T + 2u >= 10` and `W_min(T) + 2u >= 14`. The only pair with query excess
10 is `T = 10`, `s = 10`, `u = 0`. The only pairs with addition excess 14 are:

| `T` | `s` | `u` floor | `W_min` | forced composition |
| ---: | ---: | ---: | ---: | --- |
| 9 | 9 | 1 | 12 | one weight-4 and eight singletons |
| 10 | 10 | 0 | 14 | one weight-4, one weight-2, eight singletons |
| 11 | 10 | 0 | 14 | one weight-4 and ten singletons |
| 11 | 11 | 0 | 14 | one weight-4 and ten singletons |

The compositions are the only solutions in weights `{1,2,3,4,5}` of those
length and weight totals with at least one 4. For `T >= 40`, the same closed
form gives `W_min(T) >= 44`. The counting floors are therefore already
`Q >= 72` and `A >= 76` on every finite schedule. A schedule can meet
addition excess 14 only on the four rows in the table. The censuses below
show that the nine-step row and the eleven-step `s = 10` row do not meet it,
the eleven-step `s = 11` row meets it at query excess 11, and the ten-step
row meets both excesses.

### Equality census

Rotation that puts the unique weight-4 step last translates the prefix set
and preserves differences. Every word of one of the compositions above has
exactly one such rotation. The censuses enumerate those rotations. Each
count below is cross-checked by an independent dynamic program on the XOR
condition, and every reported full cover is accepted by a second difference
accumulator.

**Nine steps, `W = 12`.** All `5^8 = 390,625` singleton words were scanned.
Exactly 115,920 have XOR weight 4. Among the words with nine distinct
prefixes, the best difference count is 25 nonzero rows, so `u >= 6` and
`W + 2u >= 24`. No word has 30 nonzero rows. A repeated prefix has `s <= 8`,
hence `u >= 3` and `W + 2u >= 18`. This row does not meet addition excess 14.
The same 115,920, divided evenly across the five weight-4 masks, is the
23,184-word domain whose maximum `26/32` (zero included) is recorded by open
PR #3909. That agreement is a control. It is not that paper's unit-sum theorem.

**Ten steps, `W = 14`.** Duo position, duo mask, and eight singleton labels:
`9 * 10 * 5^8 = 35,156,250` words. Exactly 10,875,600 have closing weight 4,
2,175,120 on each of the five weight-4 masks. Among the ten-distinct-prefix
words, 576 per mask cover every nonzero row, 2,880 in total. The row is
nonempty. One such word is the schedule below, so query excess 10 and
addition excess 14 occur together.

**Eleven steps, `W = 14`.** All `5^10 = 9,765,625` singleton words were
scanned. Exactly 2,996,400 have XOR weight 4. Exactly 5,760 have eleven
distinct prefixes and all 31 nonzero differences. None of the words with
only ten distinct prefixes cover. So the `s = 10` row is empty and the
`s = 11` row is nonempty. Those 5,760 words give `(Q, A) = (73, 76)`. They
meet the addition floor and miss the query floor by one, so they do not
undercut `72o + 76p`.

## Attaining schedule

Step masks, with `17 = {0,4}` and `15 = {0,1,2,3}`:

```text
17, 2, 1, 4, 2, 1, 2, 8, 16, 15
```

The walk is closed, the ten prefixes are distinct, and their differences are
all of `F_2^5`. It uses one weight-4 step, one DUO and eight singletons, so
`T = 10` and `W = 14`. Placing two readouts on the first boundary pair of
each nonzero row produces 72 calls and 76 additions. The formal-symbol replay
accepts that schedule for every linear map and every dirty input. A fixed
width-3 trial uses identity maps, source vectors `(1, 2, 3, 4, 5)`, connector
dirt `7` and row dirt `(3m + 1) mod 8`. Forty further trials use independent
pseudorandom maps and dirt. Dropping the readout of row 1 is rejected. The
word is one of the 576 covers with closing mask 15; the verifier checks this
word and recomputes the census. It does not replace the census by a search.

The published DUO word `1, 2, 8, 18, 12, 16, 1, 2, 4, 2` is rebuilt by the
same scheduler. It costs `(72, 74)`, passes the formal replay, and contains
no weight-4 step.

The eleven-step word `1, 2, 1, 4, 2, 1, 2, 8, 16, 8, 23` is one of the 5,760
full covers above. It uses ten singletons and one weight-4 step, costs
`(73, 76)`, and passes the same replays. In the summed unit ledger its cost
is `73 + 76 = 149`.

## What this does not show

The theorem is only for schedules that contain a weight-4 toggle, on this
five-source batch, in the dispatch-plus-addition ledger above. It is not a
bound for six or more sources, for joint readouts, or for a physical frame,
routing, or tape surcharge. No supplier, native word, or selected-frontier
change follows.

Open PR #3909 prices the singleton-plus-arity-four alphabet in one summed
unit ledger and states a 149-unit floor. This package does not use that
ledger and does not audit that proof. The eleven-step word above lies in
that narrower alphabet and sums to 149. The ten-step word uses one DUO, so
it is outside that alphabet; its unit sum is 148 and is not a counterexample
to a singleton-plus-arity-four claim. The nine-step maximum 25 is the shared
control named above.

The nine-point exclusion and the three equality censuses are exhaustive
finite checks, not a proof-assistant derivation. The weight-3 price on fork
commit `3e704efb3ffb49c431ab1d0075e41e66a7971d44` is a predecessor question,
not an input: every count used here is recomputed.

## Reproduce

From the repository root, CPython 3.12, standard library only. The censuses
finish in about half a minute.

```sh
python3 -B research/weight4-toggle-price/verify.py
python3 -I -O -W error -B research/weight4-toggle-price/verify.py
python3 -B scripts/research_package.py --package research/weight4-toggle-price
```

Expected marker:

```text
PASS_WEIGHT4_TOGGLE_PRICE queries=72 additions=76 duo=(72,74) nine_point_covers=0 ten_point_normal=80 t9_best=25 t9_weight4=115920 t10_full=2880 t11_full=5760 t11_s10=0 t11_s11=5760 t11_schedule=(73,76) no_new_kappa
```

The orientation command `python3 -B research/universal-connector-boundary/verify.py`
was run once and printed
`PASS_UNIVERSAL_CONNECTOR_BOUNDARY pairings=945 max_coverage=31 queries=74 leaves=182`.
That is the card's positive control, not evidence for this theorem. Selected
cold replay, Lean, Docker and a proof-kernel check were not run.

## Open next questions

1. Does the same one-point collapse give `Q` and `A` floors at six sources
   for every toggle alphabet? PR #6695 already asks this. A six-source
   difference-basis count is larger than the five-source normal form used
   here, and the five-source floors do not transfer.
2. In the singleton-plus-weight-4 alphabet, with DUO and weight-3 steps
   forbidden, is the exact price `73o + 76p`, or does a length-10 word with
   two weight-4 steps cover and leave a Pareto split with `72o + 78p`?
   The summed unit ledger of PR #3909 ranks `149` ahead of `150` and does
   not decide that split. The first step is the two-weight-4 length-10
   census on the same prefix test.

## Credit

Ross Richardson, PR #943, supplied the dirty-connector interface and the
prefix-difference readout criterion. The DUO word and the `72o + 74p` point
are from `research/duo-toggle-connector`. Nick Petalas, PR #6695
(`research/five-source-toggle-frontier`), proved the all-alphabet floor
`72o + 74p`, the weight-5 floor `72o + 78p`, and left the weight-3 and
weight-4 prices open; the ten-point normal-form count 80 is the control
recomputed there. The full-coverage form of the length-10 query floor is
from PR #4137 (`research/connector-triple-query-floor`); the partial-coverage
form used here is the one in PR #6695, recomputed as the corner table.
Open PR #3909 recorded the normalized nine-step maximum used as a control.
The weight-3 price and its case split were computed on
`cursor/weight3-toggle-price-6a62` at `3e704efb3ffb49c431ab1d0075e41e66a7971d44`;
this package recomputes the shared nine-point exclusion and does not import
that branch's witness. Those results are cited and, where a number is reused
as a control, recomputed. They were not audited.

Prepared by unpaidmoon with substantial Cursor Grok assistance. New work is
Apache-2.0. No independent human or formal-kernel review is claimed.
