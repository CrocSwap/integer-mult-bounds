# The argument for rungs 3 and 4, and for the top of the complex ladder

Everything below is exact rational arithmetic on the pinned complex profile
(`references/pr193-source-assisted-v4.certificate.json`, the word #207's frontier certificate
prices) through the pinned interval-moment engine and the unchanged 47-constraint assembly.
The machine-checked form is `certificate.json`; `verify.py` rebuilds it from pinned bytes.

## 1. The criterion

A family of rank `r` with `n` children per vertex occupies `r * n` registers per copy. It can
leave the ledger into whole banks of width `m` only when

    m | r * n        (whole-bank volume)

and the absorption is free rather than a relabelling when the retained ledger still satisfies
the row identity `m * W - rank_mass = deficit` and the stock falls by exactly the bank count.
Those are the conditions PR219's rank-22 bit absorption and PR224's rank-11 complex
absorption satisfy, and the conditions the certified entrance-bank proof satisfies on the bit
word (2,200 rank-60 exteriors: `60 * 6,600 = 396,000 = 72 * 5,500`).

The criterion is necessary, and it is what the built rungs use. It is not sufficient: a bank
must be tiled by blocks, which for a rank that does not divide the width means a mixture
(obligation T1). Both facts are stated, not blurred: rungs 3 and 4 are priced on the volume
condition and they owe the tiling.

## 2. Which families qualify, and that is all of them

On the complex ledger (`m = 66`, one copy `W = 12,052`, deficit `1,320`, 20 families,
213,147 children, rank mass 794,112, largest child 20) the whole-bank volume condition
`66 | r * n_r` selects exactly three families:

| rank | n_r | r * n_r | = 66 x |
| ---: | ---: | ---: | ---: |
| 11 | 1,062 | 11,682 | 177 |
| **16** | 264 | 4,224 | 64 |
| **20** | 66 | 1,320 | 20 |

`verify.py` asserts this list, so the claim "exactly three" is machine-checked rather than
eyeballed. After rungs 2-4 all three are out of the ledger, and the eligibility scan on the
retained row is empty -- the criterion cannot be applied again at this width, on this ledger.

## 3. The ledgers, step by step (three-copy rows)

| after | W | rank mass | children | largest child | rule applied |
| --- | ---: | ---: | ---: | ---: | --- |
| base | 36,156 | 2,382,336 | 639,441 | 20 | row identity `66 * 12,052 - 794,112 = 1,320` |
| rung 2 (+11) | 35,625 | 2,347,290 | 636,255 | 20 | removed 35,046 = 66 x 531; stock drop 531 |
| **rung 3 (+16)** | **35,433** | **2,334,618** | **635,463** | 19 | removed 12,672 = 66 x 192; stock drop 192 |
| **rung 4 (+20)** | **35,373** | **2,330,658** | **635,265** | 19 | removed 3,960 = 66 x 60; stock drop 60 |

Every row re-satisfies `66 * W - rank_mass = 3,960` (= three copies of the deficit `1,320`,
unchanged by banking). The deficit is untouched, which is the point: banking moves dirt from
paid children into bank structure, it does not create or destroy rank mass.

## 4. The prices

For each rung the complex paid moment is recomputed by the pinned engine on the retained row
(`bit=False`, i.e. without the bit branch's rare-class fallback, exactly as PR219 prices the
complex side), on the `10^-18` grid with the adjacent grid point rejected in both directions:

| rung | complex coarse saving | grid gap above |
| --- | ---: | ---: |
| base | 7.00918443859411e-4 | — |
| rung 2 | 7.08793603125109e-4 | (PR224, reproduced to the digit) |
| **rung 3** | **7.11077971348264e-4** | adjacent point rejected |
| **rung 4** | **7.11681826686289e-4** | adjacent point rejected |

The assembly rule is the queue's own: `a = min(bit_leaf, (1-beta) * C - weak)`,
`q = a(1-2 eta)`, `kappa = floor((1-eta) q/(1+q) * 10^18)/10^18`, with
`eta = beta = 10^-24`, `weak = 10^-30`. It prints the same numbers #207, #219 and #224 print
on their own inputs (asserted equal, not within a tolerance), so the convention is calibrated
rather than chosen here.

| rung | kappa | binding | assembly bound | ceiling gap |
| --- | ---: | --- | ---: | ---: |
| rung 2 | 7.08291570590726e-4 | complex | 7.082915705907269e-4 | 8.6e-19 |
| **rung 3** | **7.10572698755137e-4** | complex | 7.105726987551371e-4 | < 1e-18 |
| **rung 4** | **7.11175695867958e-4** | complex | 7.111756958679581e-4 | < 1e-18 |

Each rung lands on its own branch ceiling: the complex budget `(1-beta) C - weak` is what the
minimum selects (asserted), the adjacent `10^-18` point is rejected by the unchanged
47-constraint assembly (asserted), and the bit leaf is not the binding branch (recorded).

## 5. Where the ladder stops, and what the next step costs

Rung 4 is the top of the accounting ladder: no family of the remaining 17 has a whole-bank
volume (asserted). Two consequences follow, and they are the useful part of the result:

* **Above the top, the bank mechanism has nothing left to take.** Reaching `kappa = 7.2e-4`
  needs a complex coarse saving of `7.2051877e-4`, i.e. +1.242% over the top rung's coarse
  saving -- more banking than this ledger's remaining mass can supply at this width.
* **Above `kappa = 7.277251e-4` the bit word is the wall.** While the complex branch caps the
  budget, the ceiling is `budget/(1+budget)`, and the budget is in turn capped by #219's
  rung-1 bit leaf (7.2825e-4). Targets `7.5e-4`, `8e-4` and `1e-3` are therefore unreachable
  on this bit word, whatever the complex ledger does; they need a new bit supplier first.

## 6. Verification boundary

* Machine-checked here: the pinned bytes (21 files, sha256), the frontier reproduction, rung 1
  rebuilt by the vendored #219 package, rung 2 rebuilt by this package's own ledger module,
  rungs 3 and 4 (volumes, row identities, stock drops, both paid moments, adjacency
  rejections), the branch ceilings, the eligibility exhaustion and the PR208 replica.
* **Not** checked here: any physical realization. C1-C7 and T1 are open, and #219's R1-R4 are
  inherited open; the complex supplier has no bank construction in the pins
  (machine-checked), and neither new family has an occurrence inventory. The kappa is
  conditional on all of them, exactly as #219's rung 1 and #224's rung 2 are.
* Not run: upstream CI, and any contributor verifier other than the vendored #219 package
  invoked in place.
* The `10^-10` supplier field is priced as a conservative variant; on it the ladder's top sits
  lower, because PR193's published `complex_saving` is its coarser-grid value.
