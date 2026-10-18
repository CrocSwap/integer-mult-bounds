# Five-helper cyclic basis change on the R439 D map

**Finite local circuit construction; no new κ.** A five-edge directed cycle on
five helpers reduces the pinned R439 D-stage cost by 12 ADDs after paying for
both preparation and restoration. The selected result, accepted bit supplier,
paid rank profile and `upstream/` are unchanged. The selected complex side still
binds.

## Exact construction

The source is the source-pinned 11,500-ADD word in
[`research/r439-bsection-stars-seed01/`](../r439-bsection-stars-seed01/README.md),
which combines the R439 helper-star D word with its ten phase-B block programs.
The cycle is applied **after** the old helper preparation. Using local helper
indices, its chronological word is:

```text
helper[59]  ^= helper[148]
helper[148] ^= helper[21]
helper[21]  ^= helper[129]
helper[129] ^= helper[25]
helper[25]  ^= helper[59]
```

The corresponding absolute wire IDs are 281, 370, 243, 351 and 247. Write
`H0` for the original helper basis change, `H1` for this five-operation cycle,
and `J0` for the original 111-by-439 injection. The old helper state at
injection is `H0 s`. The new state is `H1 H0 s`; use the injection
`J0 H1^-1`, then restore `H1^-1` in reverse operation order before the old
`H0^-1`. Thus

```text
J0 H1^-1 H1 H0 s = J0 H0 s
```

for every helper vector `s`, including arbitrary dirty values. The target and
helper D boundary is identical. The existing target preparation/restoration,
other stages, COPY/ERASE records and frame schedule remain in place.

The five selected injection columns have total weight 92 before the cycle and
70 after it. Their 111-row injection therefore drops from 4,464 to 4,442 ADDs.
The cycle adds five preparation and five restoration ADDs, giving:

| Quantity | Pinned word | Cyclic word |
|---|---:|---:|
| Injection ADDs | 4,464 | 4,442 |
| Helper cycle preparation and restoration | 0 | 10 |
| Complete D-stage ADDs | 5,548 | 5,536 |
| Complete R439 word ADDs | 11,500 | **11,488** |
| Paid rank mass | 5,129 | 5,129 |

The complete-word bounds are `F=27,061` and `B=5,921,344`. Exact integer
arithmetic gives

```text
64 F^3 B^2 = 44468459235010318794652647424
             < 20282409603651670423947251286016 = 2^104

2^18 F^5 B^4 = 4676708453903757010070537011688772133559165966010548224
               < 6277101735386680763835789423207666416102355444464034512896 = 2^192
```

## Bounded search and optimistic price

Rank all 439 injection columns by their total pairwise support overlap, breaking
ties by column weight (larger first) and local helper index (smaller first).
Take the top 20 helpers. For every one of the 15,504 five-element supports,
test all 120 permutations, where each permutation gives the five chronological
cyclic edges `p[i] ^= p[i+1]` with indices modulo five. The search tests exactly
**1,860,480** words and stops there. It finds 56 words with positive complete
ADD savings; four tie at the maximum of 12. The candidate above is the
lexicographically first maximum.

Before enumeration, a favorable basis bound gave at most 109 net ADDs of
savings in this domain: the highest-ranked five columns have weight 124 and
rank five, while preparation and restoration cost ten. For any invertible
change on five columns, the new injection has at least that rank in nonzero
columns. The cycle search attains 12 of the 109-ADD ceiling.

The paid profile is unchanged, so the recursive moment and κ gain are exactly
zero. This construction does not enter the selected assembly or establish a
smaller integer-multiplication exponent. It is scoped to the frozen R439 word
and the stated top-20 cyclic-sweep domain; it is not a minimum over other helper
supports, longer cycles, target bases or complete circuits.

## Verification

The source-pinned replay uses the standard library and the retained R439
boundary, owner and exporter checks:

```sh
python3 -B research/r439-five-cycle-seed9f01/verify.py
python3 scripts/research_package.py --package research/r439-five-cycle-seed9f01 --check-only
python3.12 scripts/research_package.py --package research/r439-five-cycle-seed9f01
```

The first command repeats the full finite search, checks all 661 formal columns
in both directions, verifies the dirty D boundary, replays H1–H5 and the paid
profile, and checks the complete exporter invoice and precision expressions.
It also rejects five controls: a missing preparation edge, a missing inverse
edge, the stale injection, a wrong inverse order, and a changed injection
coefficient. The expected final line is:

```text
PASS_R439_FIVE_CYCLE candidates=1860480 best_saving=12 ADDs=11500->11488 columns=661 controls=5 no_new_kappa
```

The exact candidate, search receipt and replay receipt are
[`CANDIDATE.json.gz`](CANDIDATE.json.gz),
[`SEARCH-RESULT.json`](SEARCH-RESULT.json) and
[`CERTIFICATE.json`](CERTIFICATE.json). `SOURCES.json` pins the task catalogue,
selected result, review, source manifest, assembly certificate and every live
input used by the predecessor replay. The conditional result remains subject
to the inherited all-size/compiler, common-label/mutable-source realization,
whole-call hosting, precision/tape and analytic-transfer assumptions. Native
C++ replay, supplier adoption and outer assembly replay were not run here.

## Open next questions

- **Can a six-helper cyclic change save more on the same D map?** A longer cycle
  could realize multi-column cancellations unavailable to a five-cycle. First
  compute its exact rank-based optimistic ceiling and full six-edge
  preparation/restoration bill on a bounded overlap-ranked support family.
  Continue only if that ceiling is positive and the precision budget is
  favorable.

## Credit

The R439 word, helper-star basis, phase-B programs and retained checkers come
from the predecessor packages and PR lineage named in `SOURCES.json` and the
linked README. Those inputs are reused unchanged. Prepared by Cinna Davis
(@1337isnot1337) with substantial OpenAI Codex assistance in the derivation,
search, implementation, checking and writing. No independent human review is
claimed. This package is Apache-2.0.
