# The pair (0, 3) coexists with (0, 9) on the sharp T2 window

**Exhaustive finite census with explicit words. No new κ and no selected-frontier
change.** In the six-source characteristic-6 floor-word model, the named pair
`(0, 3)` coexists with weight-3 at `(0, 9)` and with every T2 pair joined on
the sharp window `[8, 18]`.

A floor word calls each source exactly six times. `S(s) = q_s + q_{39-s}` is
weight-3 when every coordinate lies in `{0,1,6,7,12}` and exactly three lie in
`{1,7}`. The same predicate on `q_3` and on `q_9` is weight-3 at `(0,3)` and
at `(0,9)`. The T2 family is the endpoint multiset `(0,6,7,7,7,12)`. The
interface is the merged centre-classification package pinned in
[SOURCES.json](SOURCES.json). The question is open-next item 1 of
[PR #7176](https://github.com/CrocSwap/integer-mult-bounds/pull/7176), restricted
to the single pair `(0,3)`.

The selected conditional κ remains `363005817/100000000000` in
`certificates/selected-result.json`.

## Census

There are exactly **180** weight-3 diagonal states at `s = 8` with one
coordinate at most 1. They are given by a heavy source `H`, a low source `L`,
and which two of the other four sources have prefix count 1:

- `q_8` is the matching permutation of `(6,1,1,0,0,0)`;
- `S(8)` is the matching permutation of `(1,6,6,7,7,12)`.

The T2 tuple itself does not occur at `s = 8`: a coordinate equal to 0 would
need six copies in the five-letter suffix. These 180 states are exactly the
states that reach the T2 family on `[8,18]`. They meet the 120 T2 endpoints in
**720** joined pairs, the count proved for this window by #7176. Deleting every
`s = 9` state whose `q_9` is not weight-3 leaves each of those 720 endpoint
sets unchanged. The same holds for the other one-low endpoint family
`(1,6,6,7,7,12)` and its 1,080 pairs; that count is a by-product of the same
masks.

For each of the 180 states the prefix of length 8 has **56** orders and exactly
**6** of them make `(0,3)` weight-3: the two singleton letters both sit in the
first three positions. Prefix order does not change `q_8`, so it preserves the
diagonal chain and the truth value of `(0,9)`. Every previously joined T2 pair
therefore has a floor word that is weight-3 at `(0,3)`, at `(0,9)`, and at
every `s` in `[8,18]`.

The proof, including the uniform word that realises all `180 * 6 = 1080`
favorable prefixes, is in [PROOF.md](PROOF.md).

## Witnesses

`verify.py` rebuilds all 1,080 words and lifts one filtered path for each of
the 720 joined pairs. Three words are also written here and checked from the
string alone.

| role | word |
| --- | --- |
| canonical construction `(H,L,A,B,C,D) = (0,1,2,3,4,5)` | `230000004223344555234555443322111111` |
| #7176 word, weight-3 at `(0,9)` and at `(0,3)` | `345555552443322111234111223344000000` |
| #7176 T2 word whose `q_9` has shape `(0,0,0,1,2,6)` | `345555554433222111234111220334400000` |

The third word is a chain on `[8,18]` with T2 endpoint and with weight-3
`(0,3)`. Its `q_9` is not weight-3, so a T2 chain need not pass through
`(0,9)`. The filtered graph still reaches the same endpoints by another path.
Replacing the canonical prefix by six heavies followed by the two singletons
keeps the window and `(0,9)` and makes `(0,3)` fail, so the prefix order is
the exact extra datum.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -W error -B research/six-source-c6-prefix-pair-03/verify.py
python3.12 -I -O -W error -B research/six-source-c6-prefix-pair-03/verify.py
python3.12 -B scripts/research_package.py --package research/six-source-c6-prefix-pair-03
```

Expected marker:

```text
PASS_SIX_SOURCE_C6_PREFIX_PAIR_03 l1=180 prefixes=56 favorable=6 constructed=1080 lifts=720 joined_t2=720 joined_other=1080 forward=720 layer8=3600 l0=3420 controls=7 inputs=1
```

The verifier enumerates every weight-3 diagonal state for `8 <= s <= 18`,
checks base preservation on every legal edge, compares backward and forward
T2 endpoint sets with and without the `(0,9)` filter, checks all 56 prefixes
of each of the 180 states, and checks every constructed and lifted word from
its letters. Seven controls accept the two cited words, reject a bad prefix
order, a 35-letter string, and a seventh copy of one letter, and reject a
nearby count vector that is outside the census. Failures raise `SystemExit`.

Layer sizes are fixed at `3600` through `700` as listed in the proof. Each
state has six coordinates and at most 36 successor candidates. Partial column
enumeration uses the ten legal pairs and at most `10^6` partial tuples. No
solver or child process is started.

Python dicts and arbitrary-precision endpoint masks are a managed-runtime
deviation while the domains above stay fixed. Normal and optimized runs both
exercise the full domains.

## Scope and limits

The result fixes six sources, characteristic 6, length 36, the diagonal pairs
`(s, 39-s)` for `8 <= s <= 18`, and the two early pairs `(0,9)` and `(0,3)`.
It is an exhaustive census of that finite set, not a sample and not a proof
of the unrestricted depth-two exclusion. Intermediate multisets may differ
from the endpoint: every word above has `S(8)` of type `(1,6,6,7,7,12)` and
`S(s)` of T2 type for `s >= 9`. Pairs such as `(4,5)`, `(2,7)`, `(3,6)` and
`(1,8)` are untouched. Independent human and formal proof-kernel review are
unclaimed. No supplier, consumer, or selected frontier changes.

## Open next questions

1. On these same 180 states, which of the six `(0,3)`-favorable prefixes make
   `(4,5)` weight-3? *Why:* `(0,3)` sees only the first three letters and
   never obstructs a joined T2 pair, while `(4,5)` still lies inside the free
   prefix and reads five letters, so it can reject some of those six orders.
   *First step:* evaluate `q_4 + q_5 = 2 q_4 + e_{w_4}` on the six prefixes of
   the canonical word, then repeat for every state only if that word is empty.
   *Blocked by:* nothing in the present certificate; the checker is hard-coded
   for `(0,3)`.

The structured copy is in [TASK.json](TASK.json).

## Credit

The classification, the prefix count, the 1,080-word construction and the
endpoint-set comparison were prepared by unpaidmoon with substantial Cursor
Grok assistance. Nick Petalas's open
[PR #7176](https://github.com/CrocSwap/integer-mult-bounds/pull/7176) supplies
the sharp-window theorem, the figures 180 and 720, the question, and the two
cited words; those words are rechecked here and that package is not replayed.
unpaidmoon's [PR #7099](https://github.com/CrocSwap/integer-mult-bounds/pull/7099),
[PR #7029](https://github.com/CrocSwap/integer-mult-bounds/pull/7029) and
[PR #7042](https://github.com/CrocSwap/integer-mult-bounds/pull/7042) supply
the T2 question, the six families and the `(0,9)` pricing. The mask definition
is the merged `six-source-c6-centre-classification` package. No predecessor
credit is changed. Apache-2.0.
