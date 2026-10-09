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

### 2b. The criterion is not sufficient: T1, enumerated

A bank is a partition of 66 coordinates into blocks.  Absorbing a family *uniformly* -- the
same block pattern in every bank, as the certified bit-side construction uses (eighteen
4-coordinate cores, or three 24-coordinate cores, per width-72 bank) -- means `k_f` blocks of
family `f` per bank and `n_f = k_f * B` items for one **common** `B`.  Hence `B` divides
every `n_f` in the absorbed set and the pattern must fit: `sum_f k_f * f <= 66`.  So the scan
(`schedule66.py`) is over the **common divisors** of the item counts, not over partitions of
66; it is exhaustive and therefore a decision, not a search.

| family | `n_f` (three copies) | capacity `66 // f` | banks by volume criterion | banks its capacity needs | uniform patterns |
| ---: | ---: | ---: | ---: | ---: | --- |
| 11 | 3,186 | 6 | 531 | 531 | 4, `B` in {3186, 1593, 1062, **531**} |
| 16 | 792 | 4 | 192 | **198** | 4, `B` in {**198**, 264, 396, 792} |
| 20 | 198 | 3 | 60 | **66** | 3, `B` in {**66**, 99, 198} |

Three consequences, all asserted in `verify.py` and recorded in `certificate.json` ->
`tiling`:

1. **Rank 11 is exactly consistent**, and rung 2's 531 is the tightest of its four patterns
   (six blocks per bank, no padding).  `66 = 6 * 11` is what makes the volume criterion and
   the capacity criterion agree.
2. **Ranks 16 and 20 are not.**  `66 = 4 * 16 + 2` and `66 = 3 * 20 + 6`: a bank holds four
   or three whole blocks, so 792 items need 198 banks and 198 items need 66 -- six three-copy
   banks (two per copy) more than the volume criterion prices, the padding being 2 and 6
   registers per bank (396 three-copy registers in both cases).  At the priced counts the
   required items per bank are `33/8 = 4.125` and `33/10 = 3.3`, above the capacities 4
   and 3; a bank cannot hold a fraction of a block.
3. **No mixture is admissible.**  For a set of families absorbed together, `B` divides the
   `gcd` of their counts: {11,16} -> 18 (531 and 132 blocks per bank), {16,20} -> 198 (four
   and one, 84 registers into a 66-wide bank), {11,20} -> 18 (177 and 11), {11,16,20} -> 18
   (177, 44, 11).  Every one overflows the bank, so no uniform tiling of width 66 absorbs two
   whole bins at once -- which is also why the padding cannot be paid from a *retained*
   family, since that would remove part of a bin, while the priced ledger removes bins whole.

The obligation T1 therefore has a determined answer, and it is negative: rungs 3 and 4 are
priced on bank counts that no admissible tiling of a width-66 bank realises.  Making them
physical needs either partial-bin removals (a ledger change, which would move the retained
histogram and so the price) or a different bank width (which moves the whole ladder).  That
is a sharper statement of the blocker than "a construction is owed", and it is the reason the
upper two rows of the price table carry a caveat rather than a status.

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
  rejections), the branch ceilings, the eligibility exhaustion, the PR208 replica and the T1
  enumeration of the width-66 tilings (both the pinned scan and its findings).
* **Not** checked here: any physical realization. C1-C7 and T1 are open, and #219's R1-R4 are
  inherited open; the complex supplier has no bank construction in the pins
  (machine-checked), and neither new family has an occurrence inventory. T1's *enumeration*
  is done here and comes out negative (~2b), so the rungs above rung 2 are priced targets
  whose bank counts are not realisable by any uniform tiling -- not merely unconstructed. The
  kappa is conditional on all of them, exactly as #219's rung 1 and #224's rung 2 are.
* Not run: upstream CI, and any contributor verifier other than the vendored #219 package
  invoked in place.
* The `10^-10` supplier field is priced as a conservative variant; on it the ladder's top sits
  lower, because PR193's published `complex_saving` is its coarser-grid value.
