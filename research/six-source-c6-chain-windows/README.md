# Chain windows for the six c=6 separation-3 families

**Scoped written proof with an exact finite certificate. No new κ, supplier or
frontier change.** In the unchanged unsigned dirty connector at six sources and
characteristic 6, a floor word is weight-3 on the diagonal `s + t = 39` at `s`
when `S(s) = q_s + q_{39-s}` has every coordinate in `{0,1,6,7,12}` and exactly
three in `{1,7}`. This package answers the open question of unpaidmoon's open
[PR #7099](https://github.com/CrocSwap/integer-mult-bounds/pull/7099): which
endpoint pairs of the type-T2 multiset `(0,6,7,7,7,12)` are joined by a monotone
chain on `s = 4,...,18`.

**Answer: none.** A chain that reaches `s = 4` has `S(4)` in `{6,7}^6`, and every
step between weight-3 states keeps each coordinate in its block `{0,1}`,
`{6,7}` or `{12}`. So every chain on `[4,18]` has the multiset
`(6,6,6,7,7,7)`, and no other family of the six at `(18,21)` occurs there.
Each other family has a longest window `[s0,18]` and the start is exactly
`s0 = 3 + 5L`, where `L` is its number of entries `0` or `1`:

Here a family's window fixes the multiset at `(18,21)`. Earlier indices need
only be weight-3; their multisets may differ. The window table therefore
concerns endpoint families. It does not determine the longest windows on which
a specified multiset stays constant at every index.

| family at `(18,21)` | `L` | least `s0` | start states | end states | joined pairs |
| --- | ---: | ---: | ---: | ---: | ---: |
| `(6,6,6,7,7,7)` | 0 | 4 | 120 | 20 | 2400 |
| `(0,6,7,7,7,12)` (T2) | 1 | 8 | 180 | 120 | 720 |
| `(1,6,6,7,7,12)` | 1 | 8 | 180 | 180 | 1080 |
| `(0,1,7,7,12,12)` | 2 | 13 | 180 | 180 | 360 |
| `(1,1,6,7,12,12)` | 2 | 13 | 180 | 180 | 360 |
| `(1,1,1,12,12,12)` | 3 | 18 | 20 | 20 | 20 |

A start state is `(q_{s0}, q_{39-s0})`, an end state is `(q_18, q_21)`, and a pair
is joined when one weight-3 chain passes through both. On its longest window
`[8,18]` the T2 relation joins 720 of 21,600 pairs. The proof is two lemmas and a
counting bound: bases are frozen along a chain, a family with `L` entries at most
1 also has `L` entries equal to 12, and each low source keeps at least five of
its six copies in the last `s - 3` letters. [Proofs](PROOF.md)

## How far down the (0,9) hypothesis needs the chain

Open [PR #7029](https://github.com/CrocSwap/integer-mult-bounds/pull/7029) states
a conditional exclusion: no floor word is weight-3 at the pair `(0,9)` and at
every `s = 4,...,18`. The same two lemmas give an exact threshold. A floor word
that is weight-3 at `(0,9)` and on `[s0,18]` exists if and only if `s0 >= 8`.
Weight-3 at `(0,9)` forces `q_9` to be a permutation of `(1,1,1,6,0,0)`, whose
6-coordinate is high at `s = 9`, so a chain through `s = 9` needs `L >= 1` and
hence `s0 >= 8`. This package proves that from the definitions; #7029's own proof
is not replayed. So the chain hypothesis is needed only from `s = 7`, and
`(0,9)` together with `[8,18]` is satisfiable.

## Witness words

Each word is a floor word and weight-3 on its window; the five words with `L >= 1`
fail at `s0 - 1`. `verify.py` checks each from the string alone.

| family | window | word |
| --- | --- | --- |
| `(6,6,6,7,7,7)` | `[4,18]` | `345554433222111000345000111222334455` |
| `(0,6,7,7,7,12)` | `[8,18]` | `345555554433222111234111220334400000` |
| `(1,6,6,7,7,12)` | `[8,18]` | `345555554433222111034111222334400000` |
| `(0,1,7,7,12,12)` | `[13,18]` | `344444455555533222123220330000011111` |
| `(1,1,6,7,12,12)` | `[13,18]` | `344444455555533222013222330000011111` |
| `(1,1,1,12,12,12)` | `[18,18]` | `333333444444555555012000001111122222` |

The word `345555552443322111234111223344000000` is weight-3 at `(0,9)` and on
`[8,18]`; its family is `(0,6,7,7,7,12)`. The last window word above is the
separation-3 word printed in the merged centre-classification package.
None of these words is claimed to realize any other mask of the depth-two
interface.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -W error -B research/six-source-c6-chain-windows/verify.py
python3.12 -I -O -W error -B research/six-source-c6-chain-windows/verify.py
python3.12 -B scripts/research_package.py --package research/six-source-c6-chain-windows
```

Expected marker:

```text
PASS_SIX_SOURCE_C6_CHAIN_WINDOWS states=77220 steps=644820 first=[(0, 4), (1, 8), (2, 13), (3, 18)] joined=[360, 720, 20, 360, 1080, 2400] forward=6 starts09=[0, 0, 0, 0, 180, 480] witnesses=7 controls=7 inputs=1
```

`verify.py` enumerates all 77,220 weight-3 diagonal states with `4 <= s <= 18` and
checks the frozen-base lemma on all 644,820 legal steps between them. It counts
joined pairs by a backward search and by a second forward search that agree, and
it reproduces the least window start for each family. It then re-derives the
60 weight-3 shapes at `(0,9)`, finds the empty start sets for `s0 <= 7` and the
nonempty ones at 8 and 9, and checks the stored words literally. Seven controls
accept the cited words of #7099 and the centre package, and reject a 35-letter
word, a seventh copy of a letter, and a word without a weight-3 `(0,9)`.
`verify.py --print-witnesses` regenerates the stored words; they must match.

## Verifier limits

All search bounds are fixed in `verify.py`. Each state has six coordinates,
each layer tests at most 36 next-letter pairs per state, and each reachability
mask has at most 700 bits. Partial coordinate enumeration has at most `10^6`
entries. The graph has 15 layers, 77,220 states and 644,820 edges. Every function
is below 60 lines, and scientific checks raise even with optimized Python.
The registered commands enable warnings as errors. No solver or child process
is started.

Power-of-Ten rule 3 has a managed-runtime deviation in `verify.py`: Python
allocates tuples, dictionaries and integer masks during enumeration. The fixed
domains above bound live collections; replacing those containers with fixed
storage would require a different runtime. Normal and optimized registered
runs exercise the complete domains. A port to a runtime with controllable
allocation should preallocate these capacities before enumeration.

## Scope and limits

The model is fixed: six sources, characteristic 6, floor words of length 36, the
pairs `(s, 39-s)` for `4 <= s <= 18` and the early pair `(0,9)`. The interface is
cited from the merged `six-source-c6-centre-classification` package and pinned in
[SOURCES.json](SOURCES.json); nothing in it is re-proved. The unrestricted
depth-two exclusion at c=6 stays the solver verdict of PR6141. The joined-pair
counts other than the T1 row are census values with no closed form. Independent
human and proof-kernel review are unclaimed. Hosted CI is separate from the
local runs.

## Open next questions

1. Which further weight-3 pairs `(s,t)` with `s + t = 3 mod 6`, for example
   `(0,3)`, can hold together with `(0,9)` and a window `[8,18]`? *Why:* the pair
   `(0,9)` with `[8,18]` is satisfiable, so excluding words on that shorter
   window needs further pairs. *First step:* take the 180 start states at `s = 8` and add
   one pair that constrains only the prefix counts, with the prefix arrangement as
   extra state. *Blocked by:* the diagonal state does not record the order inside
   the first `s0` letters, which this package fixes in ascending order.
2. Does `s0 >= 3 + (c-1) L` hold at other characteristics and source counts? *Why:*
   the lemmas use only the allowed set `{0,1,c,c+1,2c}` and the suffix length.
   *First step:* rerun `verify.py` with the constants changed to the c=7 diagonal
   `s + t = 45` and compare the first-appearance table with `3 + 6L`. *Blocked by:*
   the constants are hard-coded for c=6; the c=7 existence question belongs to
   another contributor's claim and is not addressed.

The structured copies are in [TASK.json](TASK.json).

## Credit

The window theorem, the `(0,9)` threshold and the verifier were produced by Nick
Petalas. unpaidmoon's [PR #7099](https://github.com/CrocSwap/integer-mult-bounds/pull/7099)
poses the T2 question and the endpoint-pair terminology, and supplies the cited T1
control word; neighbours [#7029](https://github.com/CrocSwap/integer-mult-bounds/pull/7029)
and [#7042](https://github.com/CrocSwap/integer-mult-bounds/pull/7042) supply the
six-family census and the T1 chains. The interface is restated in unpaidmoon's
merged `six-source-c6-centre-classification` package, which credits Nick Petalas's
PR4231, PR4248 and PR6107, the Ross Richardson PR934/PR943 lineage and
JosieElliston's PR6141. No predecessor credit is changed. Apache-2.0.
