# Six-source universal connector path with pair-source DUO calls

**Recursive-interface construction and exact finite exclusion; no new kappa.**
Add exactly one operation family to the frozen connector alphabet of
[`research/universal-connector-boundary`](../universal-connector-boundary/README.md)
(Ross Richardson), the pair-source DUO call `B_jk: z += B_j x_j + B_k x_k`
already defined and charged in
[`research/duo-toggle-connector`](../duo-toggle-connector/README.md), and ask
its own open question 2 at the next source count: what is the Pareto profile
`(k calls, W source adds)` of a **six-source** universal source path?

This package supplies an explicit universal word of **(k, W) = (14, 16)**,
beating the singleton-alphabet value `f(6) = 16`
([`research/universal-connector-six-source`](../universal-connector-six-source/README.md),
PR1185 lineage) in calls at equal adds. For the frozen all-63-row six-source
batch this gives **140 root queries at 142 source adds**, against the
singleton optimum 142 at 142. In the predecessor price model
`c_B = o + p`, `c_DUO = o + 2p`, `c_A = o + p` the batch totals
`140 o + 142 p` against `142 o + 142 p`: exactly two per-call overheads `o`
saved, adds unchanged. The 138-query support bound `2 (6 + 63)` is **not**
excluded: the exact six-source DUO optimum remains between 12 and 14 calls.

```sh
python3 -B research/connector-six-source-duo/verify.py
```

Expected (Python 3.10+, standard library only, a few seconds):

```text
PASS_CONNECTOR_SIX_DUO witness=(14,16) n5max=31 k12max=49 mutations=4
```

`CERTIFICATE.json` records the controls, both complete censuses, and the
seeded search cells with their best coverages. `search.py` re-runs the
heuristic search deterministically (seed 20261014); the verifier does not
re-run it and does not trust it: every recorded fact it certifies is
recomputed by a code-disjoint method.

## Model and reduction

Unchanged from the predecessors: dirty `F2` arrays `x_j`, `y_i`, `z`; complete
calls `B_j: z += B_j x_j`, `B_jk: z += B_j x_j + B_k x_k` and paired `A_i`
readouts; sources read-only; restoration of `z` and all scratch; no copies,
extra connectors or frame changes. A source word is a closed walk on `F2^6`
from 0; a weight-1 step is a singleton call, a weight-2 step a DUO call.
`k` counts calls, `W = sum of step weights` counts source adds. The available
row masks are `D(w) = {q_s xor q_t}` over prefixes, and the word is universal
when `D(w) = F2^6` (PR943's prefix reduction, which needs no change for DUO
steps).

## Result

| Sources / alphabet | Best Pareto (k, W) | Status here |
|---|---|---|
| 6, singleton (`research/universal-connector-six-source`) | (16, 16) | cited predecessor value `f(6) = 16` |
| 6, singleton + DUO | **(14, 16)** | explicit witness, replayed exactly |
| 6, singleton + DUO, lower bounds | (12, 12) impossible | exact exclusions below |

Witness (steps as bitmasks of source labels, seed 20261014):

    steps     2 16 8 16 1 4 48 4 3 4 32 8 4 16
    prefixes  0 2 18 26 10 11 15 63 59 56 60 28 20 16

Fourteen calls: twelve singletons and the two DUO calls `48 = 32 + 16` and
`3 = 1 + 2`, so `W = 16`. All fourteen prefixes are distinct, the walk closes,
and all 64 masks appear as prefix XORs. The verifier rebuilds the prefixes and
recomputes coverage with the dual test (mask `m` covered iff some prefix `p`
has `p xor m` among the prefixes).

## Bounds and exact exclusions

* `k >= 12`. Full coverage needs `s` distinct prefixes with
  `C(s, 2) + 1 >= 64`, so `s >= 12`, and `k >= s`.
* `W >= k`, `W` is even, and `W - k` is the number of DUO calls (each source
  flips an even number of times). So `W >= 12`, and `W = 12` is possible only
  at `k = 12` with all-unit steps.
* `(12, 12)`: all-unit words of length 12 are complete here (10,395 canonical
  words, maximum coverage **49/64**), independently reproducing
  `research/universal-connector-six-source`'s census A count and maximum.
* `(14, 14)`: all-unit words of length 14 have maximum coverage 59/64 in that
  package's complete census (cited, not re-derived here).
* Therefore any six-source improvement over `(16, 16)` needs at least one DUO
  call; `(14, 16)` attains one.

Open cells, from the bounded seeded search (search failures, **not**
exclusions): `(12, 14)` best 53/64, `(12, 16)` best 58/64, `(13, 14)` best
56/64, `(13, 16)` best **63/64**. The search is seeded hill-climbing over
closed walks (seed 20261014, about two minutes total); `search.py` records
the cells and best coverages.

## Side result: no weight-3 family helps at five sources

`research/duo-toggle-connector`'s open question 3 asks whether a charged
three-source call can lower `W` below 12 at `k = 10` on five sources. It
cannot: `W = 10` forces `W = k`, hence all steps have weight 1, and those
words are exactly the frozen 945 pairings, whose maximum coverage is 31/32
(re-derived here by a complete matching enumeration). Together with the
predecessor's own `k >= 10` census, the five-source Pareto `(10, 12)` is
optimal for the whole alphabet of steps of weight at most 3. The question's
second half (a deferred-readout variant) is not addressed; see TASK.json.

## Priced whole construction

The batch object is the frozen six-source instance: one output for each of the
63 nonzero masks. Both schedules use 126 paired readouts (`63 x 2`), so the
comparison is exactly the source word.

| Schedule | Root queries | Source adds | Source calls | Readouts |
|---|---:|---:|---:|---:|
| Singleton 16-call word (`research/universal-connector-six-source`) | 142 | 142 | 16 | 126 |
| DUO witness here | **140** | **142** | 14 | 126 |

With per-call overhead `o` and per-add marginal `p` (the predecessor's price
model), the totals are `142 o + 142 p` and `140 o + 142 p`; the saving is
exactly `2 o`, the two singleton calls folded into DUO calls. The DUO call
pays its full price `o + 2p`; nothing is declared free. Weighted global
optima outside this price model are not claimed.

## Verification, controls and not-checked obligations

`verify.py` recomputes everything it certifies by methods disjoint from
`search.py`: dual coverage test, perfect-matching enumeration (pair the least
unmatched position first) instead of restricted-growth words, exact integers.
Positive fixtures: the predecessor's n = 3, 4, 5 DUO witness words (coverages
8, 16, 32 at Pareto (5,6), (6,8), (10,12)) and the singleton Gray-16 word
(64). Failure controls, each of which must be detected: deleted final call,
weight-2 step substitution (breaks restoration), half-word coverage, tampered
certificate claim.

**Not checked:** no physical supplier instance of this connector interface
exists (the predecessors' own limitation); no compiler/tape integration,
frames, owner admission, precision or outer analytic obligations; no proof
assistant; the open cells above are search failures, not impossibility
results; the `(14, 14)` all-unit cap of 59/64 is cited from
`research/universal-connector-six-source`, not re-derived; no batch optimum
below 140 is claimed.

## Open next questions

- **Does a six-source DUO word of (k, W) = (12, 14), (12, 16), (13, 14) or
  (13, 16) exist?** It matters because any of them drops the all-63-row batch
  below 140 queries toward the 138 support bound. First step: enumerate the
  s = 12 and s = 13 difference covers of `F2^6` with the collision prune and
  test weight-1/2 walkability; the (13, 16) cell reached 63/64 here. Blocked
  by: `C(63, 11)` enumeration needs the prune to bite before it is cheap.
- **Does a deferred-readout variant lower the five-source add count below
  W = 12 at k = 10?** It is the remaining half of the predecessor's open
  question 3. First step: state the deferred-readout contract precisely.
  Blocked by: the term is not defined in the predecessor package.
- **Does a real supplier boundary admit the DUO call at `o > 0`?** The whole
  saving is `2 o`. First step: instantiate the predecessor dense-bit-matrix
  leaf for one DUO call and price its entry/exit frame. Blocked by: no
  physical instance of the connector interface exists in the selected
  supplier.

## Scope status and credit

**Changed**, recorded in [TASK.json](TASK.json): the card
`connector-alphabet-change` asked for one additional operation and a small
source count for its first counterexample, and that domain is saturated by
merged `research/duo-toggle-connector` (n = 3, 5 with n = 4 as a side row) and
the concurrent five-source restatement
https://github.com/CrocSwap/integer-mult-bounds/pull/2056. Its own
scope-change trigger records raising the source count as a changed assignment;
the six-source count is `research/duo-toggle-connector`'s open question 2.

Predecessor credit: Ross Richardson
(https://github.com/CrocSwap/integer-mult-bounds/pull/943 /
https://github.com/CrocSwap/integer-mult-bounds/pull/934 and
`research/universal-connector-boundary`) for the interface and prefix
reduction; Douglas Colkitt
(https://github.com/CrocSwap/integer-mult-bounds/pull/1185) and Hanson Sun
(https://github.com/CrocSwap/integer-mult-bounds/pull/1215) for
`research/universal-connector-six-source` (`f(6) = 16`, the 12/14 censuses
reproduced and cited here); `research/duo-toggle-connector` (prepared by
Navinor with help from opencode) for the DUO family, its pricing model and
the open questions this package continues; Arham Tahir
(https://github.com/CrocSwap/integer-mult-bounds/pull/1340 /
https://github.com/CrocSwap/integer-mult-bounds/pull/1370, discussion 1352)
for the mutable-source comparison mechanism, which this package does not use.

Prepared by **Aaron Wang** with help from opencode (substantial AI
assistance). Apache-2.0. No frozen source, upstream file, selected record or
supplier claim is changed by this package.
