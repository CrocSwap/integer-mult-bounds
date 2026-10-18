# R420 cleanup: 137 fewer XORs from exact four-wire synthesis

**Status: finite bit-supplier construction and independently checked search.**
The selected #543 word's cleanup drops from **2,973 to 2,836 binary XORs**.
The complete native word drops from **26,916 to 26,779 ADDs**, with the same
2,940 frame MOVEs, nine paid copies, nine erasures, 420 dirty helpers and every
register's frame path. The paid recursive histogram is unchanged. This is not
a new supplier exponent or a new κ claim.

Base commit: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
The [selected certificate](../../certificates/selected-result.json) at that base
selects #626/#622/#623 with #543, conditional
κ = `51110230636731/31250000000000000` = `0.001635527380375392`.
The [current review](../../docs/research/community-k492-review.md), rather than
historical frontier labels, determines that context.

## Reproduce

Python 3.11 or newer, standard library only, from the repository root:

```sh
python3 -I -B research/r420-four-wire-cleanup/verify.py
```

Expected final line:

```text
PASS_R420_FOUR_WIRE_CLEANUP: 101 windows, 137 XORs saved; 26916 -> 26779 native ADDs; 8 negative controls rejected
```

The default command uses a temporary directory and leaves the checkout alone.
To retain both complete words, their actual native exports and the receipt:

```sh
python3 -I -B research/r420-four-wire-cleanup/verify.py --out /tmp/r420-four-wire-check
```

The output directory must not exist. The changed word is
`rewritten/word.json`; the record stream is
`rewritten/records/249-records.bin`. The canonical JSON hash of the changed word
is `5af46aa89fc362cc3fe9541ab833d4bbb26645ca6d767bce7197e995535afa5d`.
No compressed-output hash is used as a mathematical equality test.

[SOURCE.json](SOURCE.json) pins every imported implementation and the source
word by SHA-256, plus its complete canonical payload. [CERTIFICATE.json](CERTIFICATE.json)
contains all 101 exact original slices and replacement circuits.
[EXPECTED.json](EXPECTED.json) is the deterministic verification receipt.

For the supplementary unchanged C++ legality and five/nine/eleven-stage
checkers, use a C++17 compiler and Boost headers:

```sh
python3 -I -B research/r420-four-wire-cleanup/native.py /tmp/r420-four-wire-native --boost-include /path/to/boost/include
```

This first runs the Python check, then compiles and runs the retained checkers
on both words. It compares all deterministic receipt fields against
[NATIVE-EXPECTED.json](NATIVE-EXPECTED.json). The final line begins
`PASS_NATIVE_R420_FOUR_WIRE`. [VALIDATION.md](VALIDATION.md) records the tested
environment and its compatibility flag.

## Search class and completed coverage

The fresh OS assignment seed was **17**, selecting the bit-supplier track and
width `2 + (17 % 3) = 4`. The [claim](CLAIM.md) records three candidate tasks,
the coordination check and the choice of a less explored search class.
The search has no random trials, heuristic timeout or incomplete tail.

Expand each cleanup gate `[frame, target, sources]` into its listed-source
sequence of binary XORs. Enumerate every nonempty contiguous interval of this
**original** sequence whose union of registers has size at most four. For each
interval, permit any circuit of `target ^= source` with distinct operands from
that same register set. Registers remain labeled: no free permutations,
ancillas, reads of global y/output registers, frame changes or extra wires are
allowed. Stop extending
an interval immediately when its register union exceeds four; the union cannot
shrink. No second synthesis pass is included.

| Original register count | Windows examined | Shortenable windows | Longest interval |
| --- | ---: | ---: | ---: |
| 2 | 2,973 | 0 | 1 |
| 3 | 1,927 | 45 | 3 |
| 4 | 2,793 | 239 | 7 |
| Total | **7,693** | **284** | 7 |

Of the 284 shortenable intervals, 239 save one XOR, 39 save two, and six save
three. Weighted interval scheduling selects 101 disjoint intervals, replacing
414 gates by 277. **137 is the maximum saving in this one-layer,
disjoint-original-interval model.** This is not a lower bound on the size of an
arbitrary cleanup circuit: wider windows, different orderings, iterative
rewrites and circuits using other registers remain outside the search.

For example, interval `[158,163)` acts on registers 16, 22, 103 and 118:

```text
old: 22^=118; 103^=22; 103^=118; 16^=22; 16^=118
new: 16^=22; 103^=22; 22^=118
```

Both send `(a,b,c,d)=(x16,x22,x103,x118)` to
`(a+b,b+d,c+b,d)` over F2. This illustrates the search class; the committed
packing may choose a different overlapping interval when maximizing total gain.

## Independent finite distance and circuit evidence

The producer in [verify.py](verify.py) performs breadth-first search on packed
**rows** of GL(k,2), for k = 2, 3, 4, using all k(k−1) XOR generators. It then
does interval scheduling by decreasing start position. Equal scores skip the
current start, or retain the first improving stop; this fixes all tie breaking.

[independent.py](independent.py) imports no producer code. It:

1. Enumerates all binary matrices and recognizes invertible **columns** by their
   generated F2 span. It checks 6, 168 and 20,160 states respectively.
2. Converts the proposed distance labels to columns and checks zero only at the
   identity, nonnegative labels, every directed edge's one-Lipschitz inequality,
   and a descending neighbor from each nonidentity state. There are 242,940
   directed edges in total. Along any path from the identity the label rises by
   at most one; descending neighbors supply a path of the claimed length.
   These finite checks certify the exact distances in this gate model.
3. Recomputes its own column BFS and incrementally scans all original intervals.
   A separate end-time interval-scheduling implementation confirms the optimum.
4. Replays every selected replacement on **all 1,408 Boolean inputs** across
   the individual windows, checks the actual labeled register sets and original
   slices, and verifies that every replacement attains its exact distance.

The whole original and changed words are also replayed on all **660 independent
input columns**, including arbitrary helper dirt, by the unchanged #543
`xcheck.py`. Its geometric checks certify the original 120 labels and all 672
unchanged closed frames. The newly exported record bytes receive an additional
chronological frame, copy-lifecycle, rank-charge and full-input replay.

## Cleanup interface, frames and precision

The #543 interface's literal-reversal hypothesis H4 intentionally fails on this
word: the cleanup is resynthesized. The verifier preserves that guard and
requires its failure, while checking all other hypotheses and all conclusions.
The applicable replacement, **H4′**, is semantic:

> C acts on source/helper registers only, at the full frame, and implements
> the inverse of the raw A/B source/helper map U over F2.

This suffices for the same finite interface conclusion. The unchanged raw word
has the block form `z' = U z`, `y' = y + J x + K s`, with `J = I` and D adding
the same `K s`. Every chosen window is the same labeled linear map, so the new
C is the old C as a matrix and hence is `U^-1`. Applying it restores every
source/helper, independently of the initial target or helper values. Nothing
here asserts that the new positive-integer cleanup is an integer inverse of U.
The inherited **whole-word** signed inverse still reverses the event order and
negates ADD coefficients, interchanging copy and erase.

All C gates have full frame 1, but an operand can still need a paid climb before
its first cleanup use. The verifier therefore compares the complete per-register
MOVE paths emitted for both words, not just final frame IDs or rank totals.
Every such path and every COPY/ERASE record is identical. Some first-use times
move; their actual common-frame legality is freshly checked. Splitting a
multi-source gate does not introduce an unpaid climb.

There is also a prefix certificate stronger than fewer gates. For each window,
replace XOR by nonnegative integer addition and compute its transfer matrix.
The new matrix is entrywise at most the old matrix, **both in forward order and
in reversed order**, verified with 756 separate basis-column propagations.
For nonnegative inputs, coordinates during an add-only interval increase
monotonically. Thus every new intermediate coordinate is bounded by its new
endpoint, which is bounded by the old endpoint. Unchanged intervening positive
operations preserve this domination. This proves preservation of these
cancellation-free envelopes for the fixed circuit and its signed reverse.

The actual native prefix replay gives:

| Quantity | Original | Rewritten |
| --- | ---: | ---: |
| Forward positive prefix | 144,651 | 109,173 |
| Reverse positive prefix | 2,270,064 | 2,270,064 |
| `64 F^3 B^2` | 998206739997057013039187410944 | 429142879200064664450983477248 |
| Payload upper-bound bit length | 100 | 99 |

The rewritten value remains below the inherited `2^104` local payload ceiling.
This is a local signed-prefix check, not a fresh global hosted invoice.

## Complete local cost and limits

| Count | Original | Rewritten |
| --- | ---: | ---: |
| D / A / scatter / B ADDs | 19,922 / 2,376 / 568 / 1,077 | identical |
| C ADDs, including restoration | 2,973 | 2,836 |
| Total ADDs | 26,916 | 26,779 |
| Paid MOVEs / COPYs / ERASEs | 2,940 / 9 / 9 | identical |
| Total native records | 29,874 | 29,737 |
| Live registers / copied temporary | 660 / 1 | identical |
| Dirty helpers / retained totals | 420 / 9 | identical |
| Rank mass | 5,112 | 5,112 |

The complete rank histogram remains
`{1:1320, 2:1440, 4:60, 5:120, 8:9}`. All new XORs are actual priced native
ADDs in frame 1; no auxiliary preparation, source access, frame conversion,
restoration, copied information or recursive child is hidden. The scalar
saving does not improve this recursive histogram, and the selected assembly
remains complex-bound. This package does not regenerate a global hosted
program, reprice an outer assembly or alter a selected certificate.

Eight negative controls reject a dropped XOR, reversed operand orientation,
overlapping windows, a forged distance label, a missing GL state, an undeclared
extra register, an undercharged frame MOVE and omitted cleanup. The unchanged
literal-H4 guard also reports failure as expected. The finite search and replay
do not prove the all-size multiplication theorem; common-label/mutable-basis
realization, compiler, hosting, residual, precision/tape and analytic assumptions
remain those of the selected review.

## Attribution and relation to concurrent work

Prepared by **Jeffrey Cox (@namredips)** with substantial **OpenAI Codex**
assistance, including an independently implemented column-based checker and
scoped review. New files use the repository's Apache-2.0 license.

The source word and `xcheck.py` are **eumemic's #543**, head
`2065fe4f72a914d907f1046603f5a36f17018535`; their
[notice](../e8-bit-r420/NOTICE.md) preserves the earlier contributors and AI
disclosures. The native exporter is retained from **#493**; its author header
credits **Dylan Crow** with Anthropic Claude assistance. No imported source is
edited or reattributed.

**Sagar Thakrar's [#710](https://github.com/CrocSwap/integer-mult-bounds/pull/710)**,
head `d97c8d20a8b885271a24c5a4e8446ac7f5697d5c`, is the methodological and
semantic-interface predecessor: it closes commuting-only deletion on this word
and saves two XORs by noncontiguous conjugation. This search instead permits
arbitrary circuits inside contiguous four-wire intervals. Its two distant
sandwiches are not among these intervals. Our `[1318,1322)` overlaps two of its
deleted gates, so **no composition or additive 139-XOR saving is claimed**.

**Ali Romman's [#688](https://github.com/CrocSwap/integer-mult-bounds/pull/688)**,
head `bb05c40c3e6319aa8c131b06a105e3648ac6c95b`, composes B-block changes and
their cleanup with global replay. **@ellipsi2's
[#742](https://github.com/CrocSwap/integer-mult-bounds/pull/742)**,
head `6e7a5d271a123886dc7b54ca3180d0b9f9beda5a`, changes D using target donors.
This package does not import or claim compatibility with either patch. The
archived [R715 commuting experiment](../experiment-log/negative-searches/commuting-cancellations/README.md)
has a different word and narrower gate identities; this is not a repeated
search with a different seed.

The final queue refresh also inspected **Chinmay Khaladkar's
[#748](https://github.com/CrocSwap/integer-mult-bounds/pull/748)** at
`0ccc0b425d2b9667108d3a0918a5cfa0aa7a5861` (a changed decoder-total source
coset and compensated dirty operator), and **Alluri's
[#681](https://github.com/CrocSwap/integer-mult-bounds/pull/681)** at
`e536f6fc8aad65adef8ac4682d13625598a5c3f9` (a six-package circuit consolidation).
Neither supplies this finite shortest-CNOT window census. Both change the word
to which these original interval indices refer; integrating this mechanism
would require new synthesis and verification rather than adding headline
savings. No priority is claimed over their underlying circuit mechanisms.

Immediately before submission, **Sagar Thakrar's
[#753](https://github.com/CrocSwap/integer-mult-bounds/pull/753)** appeared at
`2b30b63789f6d9948233fc67d9d79bca6b185c5b`: restored helper stars in decoder
totals, with literal reverse cleanup and a larger positive prefix. That is
another A/C mechanism; this contribution holds A fixed and independently
resynthesizes C with a nonincreasing positive envelope. Its 128-XOR saving is
not combined with the 137 certified here.
