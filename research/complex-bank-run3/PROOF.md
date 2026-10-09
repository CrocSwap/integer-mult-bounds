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

T1's enumeration therefore has a determined answer, and for *uniform* tilings it is negative:
rungs 3 and 4 cannot be priced on the bank counts the volume criterion gives.  What the
criterion leaves is the padding -- and the padding is constructible, in exactly the way this
section's third bullet forbids for a *retained* bin but allows for the banks themselves: the
2 or 6 registers are filled by blocks of a retained family, drawn as a partial removal from
that bin.  The retained histogram then carries the reduced count, the mass that leaves is
`banks * 66` by construction, and the row identity and the stock-drop-equals-bank-count rule
both survive.  Section 3b builds that schedule and prices it; it is what the certificate's top
rung now is, and it prices *above* the unpadded rows because it removes more.

## 3. The ledgers, step by step (three-copy rows)

| after | W | rank mass | children | largest child | rule applied |
| --- | ---: | ---: | ---: | ---: | --- |
| base | 36,156 | 2,382,336 | 639,441 | 20 | row identity `66 * 12,052 - 794,112 = 1,320` |
| rung 2 (+11) | 35,625 | 2,347,290 | 636,255 | 20 | removed 35,046 = 66 x 531; stock drop 531 |
| rung 3 (+16), volume criterion | 35,433 | 2,334,618 | 635,463 | 19 | removed 12,672 = 66 x 192; stock drop 192 (not a width-66 tiling, 2b) |
| rung 4 (+20), volume criterion | 35,373 | 2,330,658 | 635,265 | 19 | removed 3,960 = 66 x 60; stock drop 60 (not a width-66 tiling, 2b) |

Every row re-satisfies `66 * W - rank_mass = 3,960` (= three copies of the deficit `1,320`,
unchanged by banking). The deficit is untouched, which is the point: banking moves dirt from
paid children into bank structure, it does not create or destroy rank mass.

### 3b. The padded schedule (`prototype66.py`)

The rows above are the volume criterion's; the schedule a width-66 bank admits is the padded
one, and this is where it is built. A bank carries the family's whole blocks plus a fixed
pattern of retained ones, with item `i` of the family going to bank `i // k_f`, block
`i % k_f`:

| rung | banks | per bank | padding per bank | draw (best option) |
| ---: | ---: | --- | ---: | --- |
| 11 | 531 | 6 x rank 11 | 0 | none |
| 16 | 198 | 4 x rank 16 | 2 | 2 rank-1 blocks, i.e. 396 rank-1 children of 262,602 (0.15%) |
| 20 | 66 | 3 x rank 20 | 6 | 6 rank-1 blocks, i.e. 396 rank-1 children |

Every bank is exactly full (`4 * 16 + 2 = 3 * 20 + 6 = 66`), every item of the family lands in
some block with no slot unused (`4 * 198 = 792`, `3 * 66 = 198`, `6 * 531 = 3,186`), and the
padding is a partial removal from a bin the ledger keeps, so the retained histogram carries the
reduced count. The ledger follows mechanically, because the mass that leaves is `banks * 66`:

| after | W | rank mass | children | rule applied |
| --- | ---: | ---: | ---: | --- |
| rung 2 (unpadded, as PR224) | 35,625 | 2,347,290 | 636,255 | removed 35,046 = 66 x 531 |
| **rung 3 (padded)** | **35,427** | **2,334,222** | **635,067** | removed 198 x 66 = 12,672 + 396; stock drop **198** |
| **rung 4 (padded)** | **35,361** | **2,329,866** | **634,473** | removed 66 x 66 = 3,960 + 396; stock drop **66** |

Each padded step re-satisfies the row identity, the stock falls by exactly the bank count, and
the eligibility scan is still empty afterwards, so the padded top is still the top of the
criterion. The padding pattern is a free parameter and every option is enumerated and compared
on the coarse saving it induces (rank 16: two options, `177822495639541/25*10^16` or
`88906856814031/125*10^15`; rank 20: eleven, from `356053348255849/5*10^17` down to
`712015725758741/10^18`); the best is the one claimed, and rank-1 padding wins in both rungs.
What this does *not* do is construct anything physically: the padding blocks are ordinary
retained children, and the normalizer, frames, charts and prime witnesses remain C1-C7.

### 3c. The instanced schedule, and the width question

`instantiate66.py` instances the schedule: item `i` of a family goes to bank `i // k_f`, block
`i % k_f`, offset `(i % k_f) * rank`, which addresses 3,186 + 792 + 198 = **4,176 items** over
531 + 198 + 66 = **795 banks** with 792 registers of padding, each family's table digested
(`fb9bd2d1...`, `f96efd45...`, `f9d9567b...`) and the ledger re-derived with the stock falling
by exactly the bank count.  That is C1's combinatorial half plus the C5-C7 inventories; the
physical half (the normalizer) and C2-C4 are still owed, because the supplier's own status line
says its operation program is not exported.

`widths66.py` then settles whether the bank width is a dial.  It is not: the pinned precedent
makes it the word's modulus (`M = 72` for the bit word, 66 here).  The engine's contraction is
`rank mass < W * modulus`, the pinned row has `rank mass / W = 65.8905...`, so every `w <= 65`
leaves the row unposeable -- 66 is the smallest modulus this ledger admits -- and every wider
modulus leaves a row whose density has moved (99.834% at 66, 95.5% at 69, 91.5% at 72), i.e. a
different word, which the scan records rather than prices.  At `w = 54` nine families would tile
whole banks and 1,549,098 registers (65% of the rank mass) could leave, against 52,470 (2.2%)
here: the criterion is not the cap, the density is, so the dial to turn is the supplier.

## 4. The prices

For each rung the complex paid moment is recomputed by the pinned engine on the retained row
(`bit=False`, i.e. without the bit branch's rare-class fallback, exactly as PR219 prices the
complex side), on the `10^-18` grid with the adjacent grid point rejected in both directions:

| rung | complex coarse saving | grid gap above |
| --- | ---: | ---: |
| base | 7.00918443859411e-4 | — |
| rung 2 | 7.08793603125109e-4 | (PR224, reproduced to the digit) |
| rung 3, volume criterion | 7.11077971348264e-4 | adjacent point rejected; not a width-66 tiling (2b) |
| rung 4, volume criterion | 7.11681826686289e-4 | adjacent point rejected; not a width-66 tiling (2b) |
| **rung 3, padded schedule** | **7.11289982558164e-4** | adjacent point rejected; 198 banks of (4 rank-16 + 2 registers) |
| **rung 4, padded schedule (the top)** | **7.12106696511698e-4** | adjacent point rejected; 66 banks of (3 rank-20 + 6 registers) |

The assembly rule is the queue's own: `a = min(bit_leaf, (1-beta) * C - weak)`,
`q = a(1-2 eta)`, `kappa = floor((1-eta) q/(1+q) * 10^18)/10^18`, with
`eta = beta = 10^-24`, `weak = 10^-30`. It prints the same numbers #207, #219 and #224 print
on their own inputs (asserted equal, not within a tolerance), so the convention is calibrated
rather than chosen here.

| rung | kappa | binding | assembly bound | ceiling gap |
| --- | ---: | --- | ---: | ---: |
| rung 2 | 7.08291570590726e-4 | complex | 7.082915705907269e-4 | 8.6e-19 |
| rung 3, volume criterion | 7.10572698755137e-4 | complex | 7.105726987551371e-4 | < 1e-18 |
| rung 4, volume criterion | 7.11175695867958e-4 | complex | 7.111756958679581e-4 | < 1e-18 |
| **rung 3, padded schedule** | **7.10784408728476e-4** | complex | 7.107844087284761e-4 | < 1e-18 |
| **rung 4, padded schedule (the top)** | **7.11599961413937e-4** | complex | 7.115999614139371e-4 | < 1e-18 |

Each rung lands on its own branch ceiling: the complex budget `(1-beta) C - weak` is what the
minimum selects (asserted), the adjacent `10^-18` point is rejected by the unchanged
47-constraint assembly (asserted), and the bit leaf is not the binding branch (recorded).

## 5. Where the ladder stops, and what the next step costs

Rung 4 is the top of the accounting ladder: no family of the remaining 17 has a whole-bank
volume (asserted). Two consequences follow, and they are the useful part of the result:

* **Above the top, the bank mechanism has nothing left to take.** Reaching `kappa = 7.2e-4`
  needs a complex coarse saving of `7.20518773516934e-4`, i.e. +1.181% over the top rung's
  coarse saving -- more banking than this ledger's remaining mass can supply at this width.
* **Above `kappa = 7.277211e-4` the bit word is the wall.** While the complex branch caps the
  budget, the ceiling is `budget/(1+budget)`, and the budget is in turn capped by #219's
  rung-1 bit leaf (7.2825e-4). Targets `7.5e-4`, `8e-4` and `1e-3` are therefore unreachable
  on this bit word, whatever the complex ledger does; they need a new bit supplier first.

### 5b. The wall quantified (`suppliers.py` and `bit_requirement`)

Two measurements bound the next step rather than describing it.  First, the density question the
width scan raises is answered over the tree: every ledger-bearing certificate in the repository
is scored on modulus, density `mass/(m*W)`, the smallest modulus the row admits and the mass
share tiling there, keeping only rows that satisfy `m*W - mass = D` with every child inside the
width.  20 distinct poseable ledgers are found and **none is less dense than the complex word**
(`3008/3013 = 0.9983405`), which is itself the least dense one in the repository -- so a narrower
modulus must be built, not found.  Second, holding the pinned shape and occupancy fixed and
varying only the modulus, the cheapest stock that poses the row is priced: at the pinned width
the required row is *exactly* the pinned ledger (stock 12,052) and it reproduces the top kappa,
which calibrates the curve; at widths 48 and 60 the complex branch stops binding and the kappa
rises to the budget the bit leaf allows, `7.277211...e-4` (+2.2655% over the top); at 72 nothing
tiles and every wider word is strictly worse (-0.74% at 84, -13.2% at 96).  The curve is
synthetic, so it specifies a word instead of reporting one.

With the ceiling of the complex side established by measurement, the targets invert onto both
branches.  Since `kappa` is read off `budget = min(bit leaf, (1-beta) C - weak)`, a target needs
*both* branches above its budget, and because the cap must clear the budget after the `beta` and
`weak` haircuts the complex saving must sit one `10^-18` step above it:

| target | required budget | required bit leaf | required complex coarse saving |
| ---: | ---: | ---: | ---: |
| 7.2e-4 | 7.20518773516933e-4 | 7.2825e-4 (already enough) | 7.20518773516934e-4 (+1.181%) |
| 7.5e-4 | 7.50562922191644e-4 | 7.50562922191644e-4 (+3.064%) | 7.50562922191645e-4 (+5.400%) |
| 8e-4 | 8.00640512409928e-4 | 8.00640512409928e-4 (+9.940%) | 8.00640512409929e-4 (+12.433%) |
| 1e-3 | 1.001001001001002e-3 | 1.001001001001002e-3 (+37.453%) | 1.001001001001003e-3 (+40.569%) |

Each line is checked twice -- the pair reaches its target, and one grid step below the budget it
misses -- so the requirement is sufficient and tight on the grid.  Only 7.2e-4 is short on the
complex branch alone; the three higher targets are short on both, and the complex ceiling that
the density curve finds above is still below all of them.

## 6. Verification boundary

* Machine-checked here: the pinned bytes (31 files, sha256), the frontier reproduction, rung 1
  rebuilt by the vendored #219 package, rung 2 rebuilt by this package's own ledger module,
  rungs 3 and 4 (volumes, row identities, stock drops, both paid moments, adjacency
  rejections), the branch ceilings, the eligibility exhaustion, the PR208 replica, the T1
  enumeration of the width-66 tilings (both the pinned scan and its findings) and the padded
  schedule of 3b (795 banks, every bank exactly filled, stock drops 531/198/66, the residual
  eligibility empty, the padded top above the volume-criterion rows it replaces), the instanced
  inventories of 3c (4,176 items, 795 banks, 792 registers of padding, the digests, the ledger
  cross-check) and the modulus scan of 3c (which widths are poseable, and that only the pinned
  one is priced).
* **Not** checked here: any physical realization. C1's physical half, C2-C4 and #219's R1-R4
  are open (C5-C7 have their inventories instanced, each child's frame/chain identity still
  owed); the complex supplier has no bank construction in the pins (machine-checked), and
  neither new family has an occurrence inventory. T1 is settled here at the *schedule* level
  (~2b and ~3b): no uniform width-66 tiling hosts the rungs, the padded schedule does, and the
  padded top is what this package claims. The kappa is conditional on C1-C7 and R1-R4, exactly
  as #219's rung 1 and #224's rung 2 are.
* Also machine-checked: the supplier scan and the density curve, including their two
  calibrations (the least dense poseable ledger in the repository is the word priced here, and
the curve's width-66 row is exactly the pinned stock reproducing the top kappa), and the
  per-target requirement table, each line re-derived from the assembly rule and tested one grid
  step below its budget.  The curve itself is a *specification*: the engine prices a row no
  supplier in the pins owns, and the scan reports other packages' certificates at their own
  conventions rather than re-deriving them.
* Also machine-checked: the *unconditionality* record.  The four pinned readings it quotes --
  the supplier's `PASS conditional finite witness` status, its `not exported` operation-program
  line, its `downstream integration task` receipt, and the vendored package's `not an
  unconditional multiplication theorem in any case` -- are matched back against the pinned files
  by `verify.py` (`check_unconditionality`), together with the per-item table for all eleven
  obligations.  The verdict is therefore evidence rather than commentary: discharging C1-C7 and
  R1-R4 buys a conditional finite witness -- the house-standard status -- and the label
  'unconditional' is closed by the pins.
* Also machine-checked: the normalizer export contract (`EXPORT-CONTRACT.md`,
  `export-contract.json`).  Six required exports, seven acceptance tests and the mapping of all
  eleven obligations are checked, and every citation the contract makes -- the digests
  `3b4e671d…`, `1d81a79b…`, `51da02c6…`, the three cache digests, the column and read counts, the
  status strings, and the banked word's and inventory's precedent values -- is resolved back
  against the pinned bytes, with the declared state (0 of 6 bodies exported) asserted rather
  than described.  The contract's one design reading is also pinned: it addresses the
  `lift`/witness pair, not the flow block, whose own status says *"Not an exact supplier
  certificate"*.
* Also machine-checked: the contract's executable form, `importer66.py`.  Its self-test is run
  as part of the verification and must pass all twelve of its cases -- seven acceptance checks
  broken in turn (a tampered body, a wrong cardinality, a denominator above the published bound,
  counts that do not come out of the exported tables, a foreign family and bin, an accepted
  colouring conflict, a repeated prime witness), an absent body, a checker the contract does not
  pin, the pinned checker passing, and the gate green without any checker -- and the real drop,
  which does not exist yet, must still be refused with the refusal code.  The harness never
  claims the physics: the replay needs the checker whose digest E3 pins, and until it is supplied
  the import stops at *gate green, replay not run*.
* Not run: upstream CI, and any contributor verifier other than the vendored #219 package
  invoked in place.
* The `10^-10` supplier field is priced as a conservative variant; on it the ladder's top sits
  lower, because PR193's published `complex_saving` is its coarser-grid value.
