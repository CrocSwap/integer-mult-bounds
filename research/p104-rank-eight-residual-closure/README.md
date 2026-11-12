# Exact closure of the fixed-paid P104 rank-eight split

**No verified κ gain.** This package closes the 29 cases left open by
[#7363](https://github.com/CrocSwap/integer-mult-bounds/pull/7363). The full
frozen census now excludes **326 of 326** public banks for one productive
rank-eight split into 4+4. Four new exact checks suffice; the other 25 cuts
are linked to exact checks by certified reversible changes of coordinates.

The literal paid itinerary is held fixed to
[#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334), with
[#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)'s signed
caller and the same 15 productive roles from chart 3 to chart 245. The
intermediate bank is public on chart 242, 772 or 1091; public axes outside
the productive cohort may take part in the bank, but prefix and suffix
endpoint images must be supported on the cohort. Original owned fields keep
their operations and stay outside the chosen public bank. The [signed price
replay](https://github.com/CrocSwap/integer-mult-bounds/pull/7363) has
110,519 paid positions and 22,461 targets before editing. In its directed
units the optimistic gross credit for one split is about 0.342 at the
comparator; one extra rank-one paid position would erase it. No edited
word or caller was constructed. The conditional comparator κ stays
0.00364665195644, the repository's selected κ stays 0.00363005817, and the
contribution's Δκ is zero.

## Exact result

Each key is (event index, chart), with the cut **before** the indexed event.

| New exact key | Prefix / suffix exterior rank | Productive prefix / suffix image dimensions | Obstruction | Residual cuts covered |
| --- | ---: | ---: | --- | ---: |
| (45270, 242) | 17 / 17 | 1 / 1 | Both pairing matrices are zero | 2 |
| (45277, 242) | 18 / 18 | 1 / 1 | Both pairing matrices are zero | 1 |
| (45435, 242) | 19 / 19 | 1 / 1 | Both pairing matrices are zero | 7 |
| (45676, 1091) | 25 / 24 | 0 / 2 | Every pure prefix has zero productive image | 11 |

The eight other residual cuts transfer to three exact zero-pairing seeds
already checked by #7363: (40243, 242), (41740, 242) and (45266, 242).
Thus the partition is 8 inherited by transfer plus 21 covered by the four
new checks; 25 of these 29 keys use a transfer. Together with the 297
predecessor exclusions, this covers the whole census.

For a verified interval on a fixed public bank, let `P_i` map initial
coordinates to bank coordinates at cut `i`; let `S_i` map a perturbation
supported on that bank to the final coordinates. Every operation in the
interval is either disjoint from the bank or an invertible public ADD or
SCALE within it. If their bank matrix is `M`, then `P_2 = M P_1` and
`S_1 = S_2 M`. With cut row `a` and cut column `b`, the bijections
`a_1 = a_2 M` and `b_2 = M b_1` preserve both endpoint images
(`a_i P_i`, `S_i b_i`) and the cut pairing `a_i b_i`. Thus they
preserve both the support test and every pairing test, including the
absence of a nonzero productive prefix. The verifier checks every event
in each interval, reconstructs the chart and owned lifecycle, builds
`M` and its inverse over the rationals, and checks both products. It
rejects mixed contacts, bank COPY and zero SCALE. In particular event
45675 reads owned role 1564 into the public bank; the cut at 45676 is
checked directly rather than transferred across that event.

At each new representative, the pinned backward covector / forward
impulse trace and the pinned full forward / reverse trace reconstruct
the exact coefficient and endpoint-image spaces separately. The verifier
compares canonical row spaces of the stacked coefficients and images,
checks both pairing matrices, and runs the inherited positive and
negative pairing controls. These are two trace paths on the same
source and arithmetic model, not two independently sourced words.
A synthetic nonidentity bank transform also tests the transfer check.

## Reproduce

Run with CPython 3.12 and the standard library. The same command works
from a Git-free export:

```sh
python3.12 -I -B replay.py --output RESULT.json
```

The output file must be new; omit `--output` for the registered replay.
The wrapper validates the retained source before extraction, reproduces
#7363's 17 original receipts and then regenerates the complete residual
receipt (all four exact forms and all 25 transfer matrices and inverses).
Its SHA256 is
`bd130ab860c7c605c47059d4a3e43852608acc2d31ffa7c9f80799b88600bc6e`.
A changed source bundle is a failure control. No network, Lean, or
unbounded search is needed.

The retained source is the unchanged `research/p104-rank-eight-fixed-paid-bank-bound`
subtree (Git tree `ff3642284311ba255be219e5828defd044d215f6`) of
[#7363 at a0502b0](https://github.com/CrocSwap/integer-mult-bounds/tree/a0502b0b30a4a4a0e9a37c08e83febbd515c5955/research/p104-rank-eight-fixed-paid-bank-bound).
The tar is retained because the exact prior replay produces the original
297 exclusions used by this package; it avoids reliance on a live PR ref
or a second package installation. Its SHA256 is
`a7b02b2dab1f5de4b81566b3d04627f543c7cf1264491013aa887675a914f37d`.
To authenticate separately, fetch `refs/pull/7363/head` from the canonical
repo, confirm the stated commit, and compare the extracted subtree to
`git archive --format=tar a0502b0b30a4a4a0e9a37c08e83febbd515c5955 research/p104-rank-eight-fixed-paid-bank-bound`.
The unchanged caller and paid word are pinned at
`07a76c5e2738882c0cb322278e56f6cae3c9885d` and
`aaeec8c0acf01e99a5f331ef363a698d9c084ace`, respectively.
[SOURCES.json](SOURCES.json) records the canonical task and selected-record
provenance at base `e54523517d0f03e58352e647c403a5af3e525a57`.

## Open next questions

This exact scope is exhausted. Different paid itineraries, a bank using
owned fields, other helper cohorts, and multiple interacting edits remain
outside the result. The smallest follow-up is to price one separately
claimed and source-pinned route change with a neutral or compensating
paid delta before attempting an exact construction. There is no such
route or complete supplier in this package. See [TASK.json](TASK.json).

## Credit

ToikY's [#7363](https://github.com/CrocSwap/integer-mult-bounds/pull/7363)
supplies the frozen census and both trace implementations.
[#7367](https://github.com/CrocSwap/integer-mult-bounds/pull/7367) supplies
the reversible bank approach in the rank-seven cohort.
[#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) and
[#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) supply the
word and signed caller. [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298)
and [#7338](https://github.com/CrocSwap/integer-mult-bounds/pull/7338) supply
the directed price and admitted invoice, and
[#7314](https://github.com/CrocSwap/integer-mult-bounds/pull/7314) and
[#7319](https://github.com/CrocSwap/integer-mult-bounds/pull/7319) the
inherited helper census. See the retained predecessor's NOTICE for
additional credit. OpenAI Codex materially assisted this proof,
implementation, verification and packaging.
