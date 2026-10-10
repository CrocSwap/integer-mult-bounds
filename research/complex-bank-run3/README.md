# The bank ladder and its new row: rungs 3 and 4 on the published profiles, the rank-3 rung on PR233's row, and the bit word's own retained ledger banked a second time, which lands the package on that row's complex branch at κ = 8.339545889388e-4

**A scheduled target, not a witness, and the same blocker as rung 2.** This package prices the
rest of the bank ladder above PR224's rung 2 -- two more whole-bank families of the complex
ledger -- records where the accounting criterion the built rungs use stops, and then builds the
bank schedule those rungs need: a width-66 bank tiled by the family's blocks plus a fixed
pattern of retained ones (`prototype66.py`). The padded schedule is admissible where the
unpadded bank count was not, and it prices **higher**, so the top of the complex ladder is the padded
rung 4 at `711599961413937/10^18` = 7.11599961413937e-4 -- until PR233's source-assisted v4 layer
is read as a *row*, where the same ledger's first whole-bank family is rank 3, needs no padding
at all, and prices **7.277211262868e-4** -- and then, one lever further, because the rank-3 rung is *bit-bound*, the bit word's own retained ledger is banked a second time ([bitrung.py](research/complex-bank-run3/bitrung.py)), which lifts the leaf the whole ladder had been sitting under and prices **`416977294469409/500000000000000000` = 8.339545889388e-4**. That last point is the top of this package: it is PR233's row's complex branch, reached from the bit side, and it is still conditional on C1-C7 and on the inherited R1-R4.

## Result

| Rung | what leaves the ledger | kappa | Binding | Status |
|---|---|---|---|---|
| frontier, #207 | — | `1366380910073/2*10^15` = 0.0006831904550365 | bit | reproduced here **exactly** |
| rung 1, #219 | bit rank-22 bin, 6,116 width-72 banks | `700427501305159/10^18` = 0.000700427501305159 | complex | reproduced here **exactly**, by importing the vendored #219 package |
| rung 2, #224 | complex rank-11 family, 531 banks | `354145785295363/5*10^17` = 0.000708291570590726 | complex | rebuilt here **exactly** by this package's own ledger module |
| rung 3, **volume criterion** | + complex rank-16 family, 192 banks | `710572698755137/10^18` = 0.000710572698755137 | complex | accounting only: no width-66 tiling hosts 192 banks (T1) |
| rung 3, **padded schedule** | + rank-16 family, 198 banks x (4 blocks + 2 registers) | `177696102182119/25*10^16` = **0.000710784408728476** | complex | **+0.3520%** over rung 2 |
| rung 4, **volume criterion** | + complex rank-20 family, 60 banks | `355587847933979/5*10^17` = 0.000711175695867958 | complex | accounting only: no width-66 tiling hosts 60 banks (T1) |
| rung 4, padded schedule (the top of the complex ladder) | + rank-20 family, 66 banks x (3 blocks + 6 registers) | `711599961413937/10^18` = **0.000711599961413937** | complex | **+0.4671%** over rung 2, **+1.5951%** over rung 1, **+4.1584%** over the frontier |
| **the bit-side rung (the top of this package, above rung 4)** | + the bit word's ranks 7, 8 and 20, 7,342 width-72 banks (rank 7 padded 10+2, rank 8 exact, rank 20 padded 3+12) | `416977294469409/500000000000000000` = **0.000833954588938818** | complex | **+17.1943%** over the rung-4 top here, **+14.5981%** over the rank-3 rung, **+22.07%** over the frontier |

The 192- and 60-bank rows are what the whole-bank volume criterion gives, and they are kept
because they are the accounting the criterion produces -- but a width-66 bank cannot host
them: the rank-16 and rank-20 absorptions need 198 and 66 banks by their own capacity, and no
uniform tiling absorbs either family together with another (T1, below). The padded rows are
the schedule a bank actually admits: every bank exactly filled, every item in a block, the
remainder padded from a retained bin, and the retained ledger re-derived. The padded schedule
is the one this package claims.

The price is the same ledger in two independent conventions: the `10^-18` grid of the queue's
latest rungs (`eta = beta = 10^-24`, `weak = 10^-30`), and PR208's pricing model
(`stop = 10^-9`, `eta = 10^-8`, `10^-10` grid) as an independent replica -- where rung 2
reproduces PR208's own published ladder value `3541457/5*10^9`, and rungs 3 and 4 price at
`284229/4*10^8` and `1422351/2*10^9`.

## The new row: the rank-3 rung prices `κ = 7.277211262868e-4`

PR233's source-assisted v4 layer is a *new row* for this ledger, and on it the complex word's
first whole-bank family is **rank 3**, not rank 16: 29,964 rank-3 children per vertex, three
registers each, so `3 * 89,892 = 269,676 = 66 * 4,086` three-copy banks -- and `66 = 22 * 3`, so
the bank is exactly filled by 22 rank-3 blocks and **this rung needs no padding at all** (the T1
obligation the padded schedule exists to satisfy does not arise here).

| the rung on #233's row (head `109a857`, pinned by digest) | value |
| --- | --- |
| banks | 4,086 (1,362 per copy), 22 blocks of 3 registers, **zero padding** |
| retained ledger | stock 36,156 -> 32,070, mass 2,382,336 -> 2,112,660, children 635,067 -> 545,175 |
| retained coarse saving | `417325324839139/5*10^17` = 8.346506496783e-4 (next grid point up excluded) |
| budget | the bit leaf `7.282510899902e-4` -- **bit-bound**, so the supplier no longer binds |
| **κ** | **`1819302815717/25*10^14 = 7.277211262868e-4`**, `binding = bit` |
| against this package's top | `711599961413937/10^18` = 7.11599961413937e-4, **+2.2655%**, `beats_published_top = True` |
| against the pinned frontier (PR207) | `1366380910073/2*10^15` = 6.831904550365e-4, **+6.5180%**, `beats_frontier = True` |
| assembly | the unchanged 47-constraint assembly green at that budget, its own adjacent `10^-18` point rejected |

The rung's contract, its instanced assignment and its stability measurement are
[EXPORT-CONTRACT-RANK3.md](research/complex-bank-run3/EXPORT-CONTRACT-RANK3.md),
[occurrences-rank3.json](research/complex-bank-run3/occurrences-rank3.json) and
[rank3-stability.json](research/complex-bank-run3/rank3-stability.json); `verify.py`
re-derives the retained ledger, re-instantiates the assignment, re-derives the bit leaf through
#219's vendored arithmetic and re-prices the point through the assembly rule, and asserts both
comparisons above against numbers this package carries.

**What this is not.** C1-C7 stay `OPEN` (the normalizer, the columns, the charts and witnesses,
the envelope parity and each child's provenance), the row's PR is **unmerged** and pinned by
digest, and the rung's own export contract is **importable** -- the ten bodies of G1-G6 declared
in the importer's dialect, with its own thirteen-case self-test -- while the row publishes none
of them, so this is a **priced, conditional
target on a scheduled row**, never a witness, exactly as the ladder's other rungs are. It is
also **row-dependent**: on the four earlier heads of #233 the rank-3 family is not a whole-bank
family at all (one child per copy short), which the stability section below measures.

## Why the ladder is on the complex word, and how far it goes

Rung 1 already sits on the complex branch's ceiling, so every later rung must raise the
**complex** coarse saving; rung 2 does it once, and lands on the new ceiling in turn. The
criterion that makes such an absorption free is that the family's own volume is a whole
number of banks (`66 | rank * children`), and on this ledger exactly three families satisfy
it: rank 11 (already rung 2), **rank 16** and **rank 20**. Rungs 3 and 4 take the other two.
After them **no family of the remaining 17 has a whole-bank volume**, so the criterion is
exhausted and the complex-side accounting ladder terminates.

| rank | children per vertex | volume (three copies) | banks (three copies) | share of the ledger's rank mass |
| --- | ---: | ---: | ---: | ---: |
| 11 (rung 2) | 1,062 | 35,046 = 66 x 531 | 531 | 1.471% |
| **16 (rung 3)** | 264 | 12,672 = 66 x 192 | 192 | 0.540% |
| **20 (rung 4)** | 66 | 3,960 = 66 x 60 | 60 | 0.169% |

Each step is checked rather than relabelled: the volume fills whole banks, the retained
ledger satisfies the row identity `66 * W - rank_mass = 3,960`, and the stock falls by
exactly the bank count. The padded schedule occupies **795 width-66 banks** in total
(531 + 198 + 66), and the top row is `W = 35,361`, rank mass `2,329,866`, 634,473 children in
17 families, largest child 19.

## What the pins do not provide (the blocker, unchanged from rung 2)

`obligations.json` states C1-C7 and inherits #219's R1-R4; **T1**, which this package carried as
an obligation, is settled just below -- enumerated, then built at the schedule level. The two
facts that decide the status are read from the pins, not asserted:

* **The complex supplier still has no bank construction.** Its certificate carries no key
  containing `bank` at all (`certificate.json` -> `blocked_on`, machine-checked), and neither
  does #207's frontier certificate. The only banked word in the pins is the **bit** word's
  entrance-gauge pack (#205: 45,842 banks, width 72, rank-60 exteriors), a mechanism specific
  to that word's entrance structure.
* **The new families have no inventory.** Nothing enumerates the complex word's rank-16 or
  rank-20 children, exactly as nothing enumerates its rank-11 family or #219's rank-22 bin
  before its own inventory was written. A rung that cannot name its items cannot be built.

One further obligation is specific to rungs 3 and 4, and this package no longer merely owes it:
it **enumerates** it (`schedule66.py`, `schedule66.json`, checked by `verify.py`) and the
answer is negative. A bank is a width-66 block partition, and a *uniform* pattern -- the same
pattern in every bank, which is what the certified bit-side construction uses (eighteen
4-coordinate cores, or three 24-coordinate cores, per width-72 bank) -- absorbing a family
forces one common bank count `B` with `k_f = n_f / B`. So `B` divides `gcd(n_f)`, and
`sum_f k_f * f <= 66`. That is finite and exhaustive:

| family | blocks per bank (capacity) | banks by volume criterion | banks its capacity needs | admissible uniform patterns |
| --- | ---: | ---: | ---: | --- |
| 11 (rung 2) | 6 (`66 = 6 * 11`) | 531 | 531 | 4, `B` in {3186, 1593, 1062, **531**} |
| **16 (rung 3)** | 4 (`66 = 4 * 16 + 2`) | 192 | **198** | 4, `B` in {**198**, 264, 396, 792} |
| **20 (rung 4)** | 3 (`66 = 3 * 20 + 6`) | 60 | **66** | 3, `B` in {**66**, 99, 198} |

Three findings, each machine-checked:

* **rank 11 tiles alone**, four ways, and rung 2's 531 (six blocks per bank, no padding) is the
  tightest of them -- which is why rung 2 is consistent and rungs 3 and 4 are not;
* **ranks 16 and 20 tile alone only above the bank counts their own volume criterion prices**:
  792 rank-16 items need 198 banks, not the 192 that `12,672 / 66` gives (192 banks hold
  4.125 items each where 4 is the capacity), and 198 rank-20 items need 66, not 60. The
  unused registers are the padding: 2 per rank-16 bank, 6 per rank-20 bank, 396 three-copy
  registers in both cases;
* **no subset admits a uniform tiling.** The common divisor for {11,16} is 18 (531 and 132
  blocks per bank), for {16,20} it is 198 (four and one, 84 registers into a 66-wide bank),
  for all three it is 18 (177, 44 and 11). Every one overflows the bank.

So T1 has **no uniform solution**, and the unpadded bank counts the volume criterion prices
are not admissible tilings. The volume criterion and the capacity criterion coincide exactly
when the rank divides the width, which is true of rank 22 at width 72, rank 11 at width 66
and the certified bit-side rank-60 exteriors (`396,000 / 72 = 5,500` banks, cores of 4 and
24), and false of ranks 16 and 20. What the criterion leaves is the padding, and the padding
is constructible: see the prototype below.

## The prototype: the padded schedule (`prototype66.py`)

A bank that the family cannot fill alone can still be filled -- by the family plus a fixed
pattern of **retained** blocks. Then every register is accounted for, and the item-to-block
assignment is as explicit as it is for rank 11: item `i` of the family goes to bank
`i // k_f`, block `i % k_f`.

| rung | banks | blocks per bank | padding per bank | padding registers | padding draw (chosen) |
| --- | ---: | ---: | ---: | ---: | --- |
| 2 (rank 11) | 531 | 6 x rank 11 | 0 | 0 | none: `66 = 6 * 11` |
| 3 (rank 16) | 198 | 4 x rank 16 | 2 | 396 | 2 rank-1 blocks per bank (396 rank-1 children) |
| 4 (rank 20) | 66 | 3 x rank 20 | 6 | 396 | 6 rank-1 blocks per bank (396 rank-1 children) |

Every bank is exactly full (`4 * 16 + 2 = 66`, `3 * 20 + 6 = 66`), every family item lands in
a block with no slot unused (`4 * 198 = 792`, `3 * 66 = 198`, `6 * 531 = 3,186`), and the
retained ledger is re-derived rather than assumed: the mass that leaves is exactly
`banks * 66`, so the row identity still holds and **the stock falls by exactly the bank count**
(531, 198, 66 on top of rung 2's row). The padding is a *partial* draw from a bin the ledger
keeps -- 396 of the 262,602 rank-1 children, 0.15% -- which is the one step the priced ledger
never took and does not need to: the retained histogram carries the reduced count.

The padding pattern is a free parameter of the construction, so all of them are enumerated and
compared on the complex coarse saving each induces (the assembly rule of section 4 then maps
the winner to κ, which is the κ in the table above and in `padded_rungs`):

* rank 16: two options -- 2 rank-1 blocks per bank, coarse `177822495639541/25*10^16`, or 1
  rank-2 block, coarse `88906856814031/125*10^15`;
* rank 20: eleven options, from 6 rank-1 blocks per bank, coarse `356053348255849/5*10^17`, down
  to one rank-6 block, coarse `712015725758741/10^18`; the padding rank matters only in the
  fifth digit of the saving, and rank-1 padding wins in both rungs.

The prototype is a **schedule-level** construction and says so: banks, blocks per bank, the
item-to-block map, the padding draw and the ledger it induces are all machine-checked, but the
normalizer that sends each item's residual projector to its block, the frames, charts and prime
witnesses are C1-C7 and remain open. No new frame family is introduced -- the padding blocks
are ordinary retained children.

## Is the bank width a lever? (`widths66.py`)

The bank width is not a schedule parameter: the pinned precedent makes it **the word's own
modulus**. In `references/pr219-run1/schedule.py` the bit word has `M = 72`, its rank-22 bin's
20,016 occurrences carry `22 * 20,016 = 440,352` registers into `440,352 / 72 = 6,116` banks,
the row identity is `M * W - mass = D`, and the stock drops by exactly the bank count. The
complex word's modulus is 66, which is why its banks are width 66. So "use another width" is a
question about the word, and the scan answers it in three machine-checked parts:

* **No narrower modulus exists for this ledger.**  The engine's contraction is
  `rank mass < W * modulus`, and the pinned row has `rank mass / W = 65.8905...`, so every
  `w <= 65` leaves the row unposeable (`mass >= w * W`) -- checked at 48, 54, 58, 60, 63, 64
  and 65 in the certificate.  66 is the *smallest* modulus this ledger admits, by exact
  arithmetic rather than by sampling.
* **At the pinned width the scan reproduces this package.**  Running the whole criterion at
  `w = 66` returns the same schedule and the same κ, which is the scan's calibration
  (asserted in `verify.py`).
* **Wider moduli are different words, and the scan shows why instead of quoting a number.**
  Holding the pinned ledger fixed while raising `w` leaves a row whose rank mass fills only
  `mass / (W * w)` of its capacity: 99.834% at 66, **95.5% at 69, 91.5% at 72, 68.6% at 96**.
  That is no longer the dense ledger the moment is calibrated on -- and the vendored
  certifier's own bracket stops holding there, which is why the scan prices `66` and records
  the rest as arithmetic.

The useful part is what the scan exposes about the *criterion*: at `w = 54`, nine of the 20
families would tile whole banks and **1,549,098 registers (65% of the rank mass)** could leave
-- for comparison, the pinned ladder leaves 52,470 (2.2%).  The criterion is not what caps
the ladder; the ledger's density is.  A **less** dense complex word -- more stock per unit of
rank mass -- would admit a narrower modulus where far more of its ledger tiles at once.  That
is the concrete thing to look for in a new supplier, and it is a measurement, not a guess.

## Which suppliers exist, and the word a narrower modulus would take (`suppliers.py`)

The width scan ends on a measurement -- what caps the ladder is the ledger's *density*, not the
criterion -- and `suppliers.py` turns that into two measurements over the tree itself.

* **No less dense supplier exists to be reused.**  Every ledger-bearing certificate in the
  repository is read and scored on the same four numbers: modulus, density `mass / (m * W)`, the
  smallest modulus the row admits (`floor(mass / W) + 1`), and the mass share that tiles whole
  banks there -- keeping only rows that satisfy the row identity `m * W - mass = D` with every
  child inside the width.  **20** distinct poseable ledgers are found (the densest are the two
  `certificates/endpoint-gauge*` rows at modulus 38,400, density 0.9999996), and **none is less
  dense than the word priced here**: the complex word, at density `3008/3013 = 0.9983405`, is
  itself the least dense poseable ledger in the repository.  So the narrower modulus the width
  scan wants cannot be reached by reusing anything already pinned; it has to be built.
* **What a word of a given width would have to look like.**  Holding the pinned *shape* (the same
  bins and counts) and its occupancy fixed and varying only the modulus, the cheapest stock that
  poses the row is `ceil(mass / (density * m))`, and the module prices it wherever the vendored
  certifier's bracket still holds:

| modulus | stock it needs | density | what tiles there | coarse saving | kappa |
| ---: | ---: | ---: | --- | ---: | ---: |
| 48 | 16,572 | 0.99831 | the same families | 8.2678e-4 | `1819302815717/25*10^16` **+2.2655%** |
| 54 | 14,731 | 0.99829 | padding exceeds the kept rank-1 bin | -- | not priced |
| 60 | 13,258 | 0.99828 | the same families | 7.7898e-4 | `1819302815717/25*10^16` **+2.2655%** |
| **66** | **12,052** | **0.99834** | the pinned ladder | 7.1211e-4 | `711599961413937/10^18` (the calibration) |
| 72 | 11,048 | 0.99831 | nothing | -- | not priceable |
| 84 | 9,470 | 0.99828 | a smaller set | 7.0686e-4 | -0.7364% |
| 96 | 8,286 | 0.99831 | a smaller set | 6.1836e-4 | -13.1559% |

At the pinned width the row the curve requires is *exactly* the pinned ledger -- the same stock,
12,052 -- and it reproduces this package's top kappa: that is the curve's calibration, asserted
in `verify.py`.  At widths 48 and 60 the complex branch stops binding altogether and the kappa
rises to the budget the pinned **bit** leaf allows, `7.277211...e-4` -- **+2.2655%** over the top
rung, and the whole of the complex headroom that is left.  The curve is **synthetic** (the pinned
engine pricing a row that no supplier in the pins owns), so it specifies a word rather than
reporting a result about one; the width-72 entry is what the pinned word itself does, and every
wider word is strictly worse.

## What is instanced, and what is still owed (`instantiate66.py`)

The padded schedule is now instanced, which is C1's combinatorial half and C5-C7's
inventories: every item of every absorbed family has a bank, a block and an offset, under the
rule *item `i` -> bank `i // k_f`, block `i % k_f`, offset `(i % k_f) * rank`*.

| family | per vertex | items (3 copies) | banks | blocks per bank | padding registers | table digest |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 11 | 1,062 | 3,186 | 531 | 6 | 0 | `fb9bd2d17f69...` |
| 16 | 264 | 792 | 198 | 4 | 396 | `f96efd45d9d9...` |
| 20 | 66 | 198 | 66 | 3 | 396 | `f9d9567b4b41...` |

**795 banks, 4,176 items addressed**, 792 registers of padding (0.30% of the kept rank-1 bin),
every bank exactly filled, every block holding exactly one item, the map a bijection onto the
bank/block/offset grid, a digest per family over the whole table, and the ledger re-derived
with the stock falling by exactly the bank count.  The artifact is pinned in
[occurrences66.json](research/complex-bank-run3/occurrences66.json).

What is still owed is stated as facts read from the pins, not as prose: the complex supplier's
certificate carries **no key containing `bank`** and its own status line declares that a literal
globally renumbered operation program **is not exported** -- so the residual projectors the
normalizer must move (C1's physical half) are not in the pins, only the item counts are.  C2,
C3 and C4 (formal columns, charts and prime witnesses, moment-envelope parity) follow the same
gap, and C5-C7 still owe each child's frame/chain identity.  The *shape* of the inventory the
complex side owes is pinned -- for the bit word, at
`references/pr219-run1/inputs/absorbed-occurrences.json`, whose per-vertex keys
(`H`, `H_center`, `Y`, `src`) are recorded in the certificate.

## What the top rung implies for the next step

While the complex branch caps the budget, the assembly's ceiling is `budget/(1+budget)` with
the budget capped in turn by the bit leaf of #219's rung-1 bit word (7.2825e-4). So:

* reaching `kappa = 7.2e-4` needs a complex coarse saving of `7.20518773516934e-4`, i.e.
  **+1.181%** over the top rung's own coarse saving -- more banking than this ledger contains;
* reaching `7.5e-4`, `8e-4` or `1e-3` is **impossible on this bit word**: the leaf caps kappa
  at `1819302815717/25*10^16 = 7.277211...e-4` there, so those targets need a new bit word
  before any complex-side work can matter.

### The same three targets, inverted onto both branches (`bit_requirement`)

`kappa` is read off `budget = min(bit leaf, (1-beta) * C - weak)`, so a target is met only when
**both** branches clear the budget it needs.  The certificate inverts the rule per target and
checks each line twice: the pair (budget, required complex coarse saving) reaches the target, and
one `10^-18` step below the budget misses it.  Because the cap must *clear* the budget after the
`beta` and `weak` haircuts, a complex saving on the grid must sit one grid step **above** the
budget it has to supply.

| target | required budget | required bit leaf (gain over the pinned leaf) | required complex coarse (gain over the top rung) |
| ---: | ---: | ---: | ---: |
| 7.2e-4 | 7.20518773516933e-4 | 7.2825e-4 -- already enough | 7.20518773516934e-4 (+1.181%, as above) |
| 7.5e-4 | 7.50562922191644e-4 | 7.50562922191644e-4 (**+3.064%**) | 7.50562922191645e-4 (**+5.400%**, +7.083% over rung 1) |
| 8e-4 | 8.00640512409928e-4 | 8.00640512409928e-4 (**+9.940%**) | 8.00640512409929e-4 (**+12.433%**, +14.227% over rung 1) |
| 1e-3 | 1.001001001001002e-3 | 1.001001001001002e-3 (**+37.453%**) | 1.001001001001003e-3 (**+40.569%**, +42.813% over rung 1) |

Only `7.2e-4` is short on the complex branch alone; the three higher targets are short on **both**
-- and the complex ceiling the density curve finds above (`7.27721126e-4`) is still below every
one of them.  That is the package's answer to "what would a new bit word have to bring": a leaf of
at least the budget column, and a complex supplier that can clear the same budget by the same
margin -- the bit word because the leaf caps the budget, the complex supplier because the bank
mechanism has nothing left to take at width 66.

## Can the obligations be discharged, and can this be made unconditional?

The first answer is yes and the second is no, and both are readings of the pinned bytes rather
than positions -- `verify.py -> check_unconditionality` matches the four quotes back against the
files, so the record cannot drift from what the pins say.

**C1-C7 and R1-R4 are one missing artifact, not eleven gaps.** Every one of them needs the same
thing: the literal operation program, then the columns, charts, witnesses and envelope re-run on
the word it is banked by. The supplier this whole ladder is priced on certifies its flow and its
all-column fresh identity, and states in the same breath that *"a literal globally renumbered
operation program is not exported"*; its construction receipts call the literal
program/replay *"a downstream integration task"*. So the work is reserved upstream, not
invented here, and it is the work of a construction rather than of arithmetic: C1's normalizer
has to move projectors that exist only in that program, C2 has to re-run the columns of a word
that program defines, C3 has to chart frames those columns create, and C5-C7 need each child's
frame/chain identity, which the pins export as a *count* per bin (`1,062`, `264`, `66` per
vertex) and not as an identity. The one item that could be closed from the pins alone -- once
C1's completion children are named -- is the moment-envelope parity (C4), because the envelope
this package prices is already the certified arithmetic. R1 is the exception on the other side:
the bit word's banked precedent *is* pinned (the entrance-gauge pack, 45,842 physical banks with
gauge roles), so that obligation has a shape to extend instead of a mechanism to invent.

**Unconditional is not a reachable label.** Three independent pinned facts close it: the
supplier's own certificate is published as `PASS conditional finite witness`; the vendored #219
package states that discharging R1-R4 buys a completed finite witness and that the result is
`not an unconditional multiplication theorem in any case`; and this package's own scope says the
same for the finite bridge and the all-size interfaces it inherits (general Clifford/tensor,
uniform weighted compilation, restored rows, routing, paid layout, prime supply,
precision/recovery, fixed tape). Discharging the eleven obligations would raise this ladder's
kappa from a *scheduled target* to the **house-standard conditional finite witness** -- the same
status the queue's published rungs carry, and the strongest status anything in the repository
claims. That is the whole of what the work buys, and the package now says so with the quotes
attached rather than in general terms.

**The contract that would turn it into an increment.** [EXPORT-CONTRACT.md](research/complex-bank-run3/EXPORT-CONTRACT.md)
and its machine-readable twin [export-contract.json](research/complex-bank-run3/export-contract.json)
put the missing artifact in the form an interface can carry: six required exports -- the
operation program, the frame bodies behind the three published cache digests, the lift and
witness pair, the chronology tables, the per-child occurrence inventory, and the envelope plus
integrity manifest -- each with the digest it must *reproduce* (so the contract asks for bodies
behind hashes the supplier already publishes, never for new trust), seven acceptance tests with
their bounds and reject controls, and the mapping from every export to the obligations it
unblocks. Two readings shape it: the exports are addressed to the `lift`/witness pair and not to
the flow block, because the supplier's own `flow.status` says "Not an exact supplier
certificate"; and the per-child export is asked in the exact shape of the bit word's
`inputs/absorbed-occurrences.json`, because our side of that bijection already exists
(`occurrences66.json`, 4,176 items over 795 banks). Today it fails closed -- **0 of 6 bodies** --
and `verify.py` asserts that reading against the pins rather than asserting it in prose.

**The contract in executable form** is [importer66.py](research/complex-bank-run3/importer66.py).
It consumes the exports, runs the seven acceptance tests with their bounds and refuses cleanly
while a body is absent -- which is the state today: `python3 -B importer66.py` exits **2** after
naming all ten bodies that are missing, and no obligation moves. The module separates the two
things that are easy to confuse. The **gate** is decidable from what the bodies declare: hashes
anchored to the digests the supplier already published, cardinalities, the published bounds
(denominators, colouring, prime threshold), the two bijections (the frame id map, and A5's
families against this package's own `occurrences66.json`) and the counts that must come out of
the exported tables rather than out of the certificate. The **replay** -- formal columns over F2
and the defining integers, fraction-free charts, the moment envelope -- is the supplier's own
checker: the contract pins its digest (`lift.checker_sha256`), so the harness requires that exact
file and reports the replay `NOT RUN` until it arrives, and exit code 3 says so rather than
certifying anything. `--self-test` builds synthetic bodies, patches the anchored digests to their
synthetic hashes, and then breaks each check in turn: thirteen cases, including a tampered body, a broken equality bound, a
bound above `at_most`, a false flag, a broken bijection, a denominator above the bound, counts
that do not come out of the tables, a foreign table, a repeated prime witness, an absent body, a
checker the contract does not pin, and the pinned checker passing --with the complex side's real drop, still absent, refused at the end. All thirteen pass in `verify.py`, so the refusals the harness will
perform on the real drop are demonstrated now rather than promised. Both contracts get the same
thirteen cases, because the proof is derived from the contract rather than written beside it:
`importer66.py --self-test` builds the synthetic bodies, the anchored digests and the mutation
that must be rejected out of whichever contract it is handed.

**Its twin for the bit side.** [EXPORT-CONTRACT-BIT.md](research/complex-bank-run3/EXPORT-CONTRACT-BIT.md)
and [export-contract-bit.json](research/complex-bank-run3/export-contract-bit.json) are this same
contract turned on the *other* half of the ledger pair: what the bit supplier must publish for
#219's rank-22 realization obligations R1-R4 to close. The schema, the seven acceptance tests
`A1-A7`, the gate/replay split and the fail-closed reading are this side's, unchanged; only the
content differs. The bit twin is **half-met** where this side is empty: the pins already carry
that word's built physical layer (PR200's formal columns and prime witnesses, PR205's charts,
incidence and colouring), the rank-22 family enumerated occurrence by occurrence in the exact
shape of `inputs/absorbed-occurrences.json`, the whole-bank schedule and the retained ledger.
What is missing is those bodies *re-published and re-run on the banked word*, plus the one
genuinely new artifact R1 asks for -- the per-occurrence assignment (item -> bank, offset) and
its normalizer, whose admissible tilings `schedule.py` already enumerates. The cross-reading that
makes it a closed checklist rather than an open question: the inventory's
`source_pins.word_p12_sha256` **is** PR205's `physical.word_sha256`, so the twin asks for bodies
behind digests of a word this repository already half-holds, and it pins that supplier's own
checker (`source_pins.checker_sha256 = 4d7c86cd...`) rather than this side's
`lift.checker_sha256 = 9d841bcf...` -- `verify.py` asserts the two digests differ, so neither
contract can be discharged with the other side's checker.

**The same contract on a new row, at one rung.** [EXPORT-CONTRACT-RANK3.md](research/complex-bank-run3/EXPORT-CONTRACT-RANK3.md)
and [export-contract-rank3.json](research/complex-bank-run3/export-contract-rank3.json) are the
complex contract instantiated at the **rank-3 rung** of PR233's source-assisted v4 layer -- the
row on which the first family whose own volume fills whole width-66 banks is rank **3**, not
rank 16. It is the one rung of this ladder that needs no padding at all: `66 = 22 * 3`, so its
89,892 three-copy items fill 4,086 banks exactly, and the acceptance test that checks the
assignment therefore **rejects** a padding register instead of asking for one. The assignment is
already instanced on this side of the interface
([occurrences-rank3.json](research/complex-bank-run3/occurrences-rank3.json), table digest
`71cb207f...`), which is what makes the export a bijection in both directions rather than a count.
C1-C7 are restated at the rung's own numbers and quoted verbatim from
[obligations.json](research/complex-bank-run3/obligations.json); C6 and C7 (the families beyond)
are explicitly outside its scope. The row is pinned by digest --
[references/pr233-source-assisted-v4-layer.certificate.json](research/complex-bank-run3/references/pr233-source-assisted-v4-layer.certificate.json),
head `109a857`, 3,988 bytes, sha256 `691cb0aa...` -- because its branch is **unmerged**: if it
moves, `check_manifest` fails closed and the contract must be re-taken rather than reused. The
point the retained row carries is therefore derived and **not published**: coarse
`8.346506496783e-4`, budget = the bit leaf `7.282510899902e-4` (**bit-bound**, so after this rung
the supplier is no longer the lever), kappa `1819302815717/25*10^14 = 7.277211262868e-4`
(+2.2655% over the top this package publishes), with the complex ceiling `1.06e-4` above it -- so
the rung is not ceiling-tight the way the published rungs are.

The same executable form consumes it, unchanged:
`python3 -B importer66.py --contract export-contract-bit.json` runs the twin's gate on its own
drop (`exports-bit`) and still refuses it (exit **2**), while the same command with `--partial`
reports what the bodies present decide (exit **4**, never admissible) and `--self-test` gives the
twin the identical thirteen-case proof.

**The bit drop: two of the seven acceptance tests now decide on published bytes.**
`exports-bit/` holds **10 of the 15 required bodies, 8 of them anchored**, and the export groups
they complete are `B1` and `B3`; `B2` (`assignment.json`), `B4` (`columns.json`), `B5`
(`controls.json`) and `B6` (`envelope.json`, `integrity.json`) are absent. The five word bodies
(`word.json.gz` `1cb7e8ed…`, `frames.json.gz` `ad8e2705…`, `graph.json` `31a09a55…`,
`kchron.json` `0fab548e…`, `profile.json` `c44ef864…`) and the witness body
(`prime-witnesses.json.gz` `612f0b91…`) are the supplier's own bytes, each hashing to the digest
its certificate already published. The chart and incidence streams do not exist upstream as
files, so they are **re-derived** by running PR205's packer unmodified on those word bodies:
`22662b85…` and `76bff256…`, byte for byte, with `exports-bit/physical.rebuilt.json` differing
from PR205's published `physical` block in **0 of its 26 fields**. What the bodies do not declare
is declared by two **index** bodies, derived by `bitindex.py` from the bodies and the pinned
certificates rather than typed in (`index.json.gz` for `B1`, `charts.index.json.gz` for `B3`);
neither is anchored, because an index is a declaration and the bodies it describes are what carry
the digests. On that drop the gate **decides `A2` (9 checks) and `A3` (17 checks)** -- `A2` on the
index's six counts, its frame-record bijection and its foreign-replay bound, `A3` on the chart and
witness bounds -- and reports the rest instead of guessing: `A1` passes all eight digest anchors
and nine index checks with no failure but stays not runnable while `integrity.json` is absent,
`A6` and `A7` pass seventeen chart/index checks each and stay not runnable while `B5`'s
`controls.json` is absent, and `A4` and `A5` have no checks at all. The run is recorded as
[bit-drop-report.json](research/complex-bank-run3/bit-drop-report.json); the default import still
refuses the five absent bodies, the replay is **NOT RUN** because the pinned checker `4d7c86cd…`
is not supplied, and R1-R4 therefore stay OPEN with nothing discharged.

## Is the rank-3 rung stable? (`rank3stability.py`)

The rung is priced on one row, and that row is on an unmerged branch.  So the question worth
measuring is not whether the number is right but whether the rung survives the branch moving,
and whether it is a property of the *family* or of that one *row*.  `rank3stability.py` measures
both: every commit of #233 that touches its layer certificate (**six**, all vendored under
[references/pr233-heads/](research/complex-bank-run3/references/pr233-heads) so the measurement
re-runs in a clone rather than needing the branch), and every other width-66 ledger row the
repository's certificates carry (nine distinct rows).

The reason the answer is delicate is arithmetic.  A family of rank `r` with `n` children in the
ledger row fills whole width-66 banks exactly when `66 | r * n`, which is a condition on the
count alone -- `n` a multiple of `66 / gcd(r, 66)`:

| rank | needs | on the pinned row |
| ---: | --- | --- |
| 3 | `22 \| n` | 89,892 = 22 x 4,086 -- the rung |
| 4 | `33 \| n` | 34,551 = 33 x 1,047 |
| 11 | `6 \| n` | 3,177: 33 registers short, *not* eligible on this row |
| 16 | `33 \| n` | 729: 18 registers short, *not* eligible on this row |
| 18 | `11 \| n` | 23,760 = 11 x 2,160 |
| 20 | `33 \| n` | 198 = 33 x 6 |

So eligibility is a modular accident of each family's child count, and it moves when the
supplier's pairing moves a handful of children between ranks.  It did move:

| head | row | rank 3 eligible | whole-bank eligibility | registers short of it |
| --- | --- | --- | --- | ---: |
| `52c6fba`, `7f909fb`, `cf08677`, `c3f9ba1` | 29,061 per vertex | **no** | `[12, 17, 18, 20]` | 9 |
| `246f6f9` | 29,964 (rank 4: 11,502) | yes | `[3, 18, 20]` | 0 |
| `109a857` (pinned) | 29,964 (rank 4: 11,517) | yes | `[3, 4, 18, 20]` | 0 |

**The rung exists on two of the six heads and not on the first four** -- and the four miss it by
*one rank-3 child per copy*, i.e. nine registers over the ledger's three copies, not by a
different family.  Where it exists its **price is identical** (`1819302815717/25*10^14`, bit-bound)
even though the coarse saving differs, because the bit leaf binds both and the assembly's floor is
a function of the budget.  What is *not* stable is the rung after it: the retained eligibility is
`[18, 20]` on `246f6f9` and `[4, 18, 20]` on the pinned head, so rank 4 is bankable only on the
head the contract is priced on.  And **no other width-66 row carries the rung at all**: the
pinned ladder row (PR193/PR207/PR205) is eligible at `[11, 16, 20]` and misses rank 3 by 39
registers; PR200's complex physical rows, coordinated-frames' two rows and the older heads'
audit row are eligible at `[16, 17, 18, 20]`, `[4, 17, 18, 20]`, `[17, 20]` and
`[12, 17, 18, 20]`.  The rung is a property of *this row*, not of the family.

What the measurement does not cover: any head that does not exist yet (a new head is a new
measurement, not a silent pass), and any row outside this repository.  The artifact is
[rank3-stability.json](research/complex-bank-run3/rank3-stability.json), and
`verify.py -> check_rank3_stability` re-derives all of it, checks the modular criterion against
the ledger's own divisibility test on every row, and asserts the four findings above.

## The rung above: rank 4, and why κ does not move (`rank4rung.py`)

The rank-3 rung's own contract names the next whole-bank family of the retained row (rank 4,
`2,094` banks by the volume criterion) and says it still owes T1's padded tiling.  That is the
question [rank4rung.py](research/complex-bank-run3/rank4rung.py) measures, and the answer is a
negative result in three parts -- recorded as data rather than asserted, in
[rank4-rung.json](research/complex-bank-run3/rank4-rung.json):

* **The volume criterion holds on one head only.** The retained row's rank-4 bin is `n4 = 34,551`
  three-copy children on the pinned head, and `66 | 4 * 34551 = 138,204 = 66 * 2,094`.  On
  `246f6f9` -- the other head that carries the rank-3 rung -- `n4 = 34,506` and `138,024 / 66` is
  not an integer, so the rung does not exist there.  The four earlier heads carry neither rung.
* **T1's padding cannot be reinstated here.** The padded schedule needs saturation
  (`16 | n4`) and `34,551 = 16 * 2,159 + 7`: nine slots, thirty-six registers short, so its
  padding is not uniform.  And the bank count the rung *prices* cannot host its own items:
  `2,094 * 16 = 33,504 < 34,551`.  T1's mixed-tiling enumeration, run at every bank count that
  divides `n4`, does have solutions -- `B in {3,141, 3,839, 11,517}`, 1,168 patterns -- but every
  one of them draws **at least 22 of the bank's 66 registers** from other bins, and every tiled
  ledger is a different ledger from the priced one.
* **κ does not move.** All of it is priced by the same rule as the rest of the package, and every
  ledger the rung can induce is bit-bound: the budget is the leaf `7.282510899902e-4`, so κ is
  `1819302815717/25*10^14 = 7.277211262868e-4` -- the value the rank-3 rung already holds, to the
  last `10^-18` step -- while the coarse saving rises by `+8.8925%` (priced ledger, to
  `9.088721229013e-4`) and by `+114.805%` (best tiled ledger, to `1.792871277258e-3`).

So the ladder's complex side stops binding by a wide margin and the assembly rule cannot spend
any of it.  The lever is the bit word's leaf, and the module inverts the rule to say how much
leaf each further target needs -- cross-checked against the certificate's own `bit_requirement`
table: κ's next `10^-18` step needs the leaf's next grid point (`728251089990229/10^18`),
`7.5e-4` needs `7.5056292219e-4` (`+3.06%`), `8e-4` needs `8.0064051241e-4` (`+9.94%`) and
`1e-3` needs `1.0010010010e-3` (`+37.45%`).

`verify.py -> check_rank4_rung` re-derives the criterion, every head, the padded schedule's
shortfall, the whole enumeration and every price, and asserts the three findings above.

## The bit side: a second absorption on #219's word, and the new top (`bitrung.py`)

The ladder has been **bit-bound since rung 2**, and the leaf that bounded it was treated as a
constant.  #219's rung 1 absorbs the rank-22 family of the PR200/PR205 packed bit word into
6,116 whole width-72 banks and leaves a retained row of `W = 50,286` roles, rank mass 3,614,784,
deficit 5,808 and 857,622 children over 21 ranks, whose certified paid saving -- bootstrapped
through #185's three-level chain -- is the leaf `7.282510899902e-4`.  Every later reading of this
package priced *that* row as it stands, which is why the rank-4 section above concluded that the
bit word's ceiling was the leaf and that `7.5e-4`, `8e-4` and `1e-3` were out of reach on it.
[bitrung.py](research/complex-bank-run3/bitrung.py) prices the row one rung further: a second
family can leave the **same** retained ledger into whole banks, the way the rank-22 bin did, and
every absorption lowers the retained mass -- so the leaf itself is a lever, not a constant.

The criterion is rung 1's, restated on the retained row and read two ways, because the two
readings are not the same rung:

* the **volume** reading: the family's own volume is a whole number of width-72 banks,
  `72 | rank * n_rank`;
* the **padded** reading: what a bank can actually host when the rank does not divide the width --
  `capacity = 72 // rank` blocks of the family plus `72 mod rank` registers of padding in every
  bank, so it needs saturation (`capacity | n_rank`) and a retained bin that can supply the
  padding.  This is T1's padded schedule, one word over.

Thirteen of the retained row's 21 families satisfy one reading or the other -- ranks 4, 6, 7, 8,
9, 11, 12, 15, 16, 17, 19, 20 and 21 -- so the module prices every rung of up to three of them
(13 + 78 + 286 = 377 rungs) with the vendored interval-moment engine, and reads the block
schedule each family needs.  The climb, in three rows of that screen (the gains are the recorded
kappas divided by the rank-3 rung's `1819302815717/25*10^14`):

| absorb | banks | retained W | bit leaf | kappa | binding | gain |
| --- | ---: | ---: | ---: | ---: | --- | ---: |
| rank 20 | 5,280 of 3 blocks + 12 registers | 45,006 | 7.957727174054441e-4 | `397569983356707/500000000000000000` = 7.95139966713414e-4 | bit | +9.2644% |
| ranks 4, 20 | 6,878 (rank 4 exactly filled, rank 20 as above) | 43,408 | 8.337650404202950e-4 | `104133806924797/125000000000000000` = 8.33070455398376e-4 | bit | +14.4766% |
| **ranks 7, 8, 20** | **7,342** (1,224 of 10 blocks + 2 registers; 838 of 9, exact; 5,280 of 3 + 12) | **42,944** | **8.349765438523530e-4** | **`416977294469409/500000000000000000` = 8.339545889388e-4** | **complex** | **+14.5981%** |

The last row is the rung this module claims, and it is the *cheapest* rung that reaches its own
kappa, not the only one: **108 of the 377 rungs** price `416977294469409/500000000000000000`,
because once a rung's bit leaf clears the complex branch the budget is the branch and every such
rung lands on the same point -- the screen is not choosing among them, the cap is.  The leader
rule is the package's own (highest kappa, ties broken by the fewest banks, then by the sorted
ranks), which is why the claimed rung is ranks 7, 8 and 20 at 7,342 banks rather than rank 21
alone (15,018 banks) or ranks 4 and 21 (16,616).  Its schedule keeps the retained row identical
-- `W = 42,944`, rank mass 3,086,160, deficit 5,808, 756,192 children over 18 families -- the
stock drops by exactly the 7,342 banks, and the padding is drawn from the retained singleton bin:
rank 7 needs 1,224 banks of 10 blocks plus 2 registers, rank 8 divides the width and needs 838
exactly filled banks of 9 blocks, rank 20 needs 5,280 banks of 3 blocks plus 12 registers, so
**65,808 registers of padding in all**, a partial removal from one bin exactly as T1 does on the
complex side.  The module checks rather than asserts that each padded step needs its own bank
count: `volume_reading_hosts_the_items` is `false` for both of them, rank 7's volume reading
prices 1,190 banks where its schedule needs 1,224, and the reading the module writes for rank 20
is `4,400 * 3 = 13,200 < 15,840 items`.  The rung prices the schedule, not the accounting.

The binding side changes here, and that is the result.  The leader's leaf, 8.349765438523530e-4,
sits **above** the complex branch it has to clear -- the leader reaches `1.000390455784346` of it
-- so the budget is the branch `417325324839138999999999582174675160861/5*10^41` and the kappa is
`416977294469409/500000000000000000`, the last `10^-18` grid point at or below PR233's row's
complex ceiling `417325324839139/500417325324839139`, which the unchanged 47-constraint assembly
accepts with its adjacent grid point rejected.  So the wall moves rather than disappears: every
further bit rung is capped by the complex side, and the next increment is the complex supplier
again (or a new bit word that lifts the leaf without spending the branch).  That **revises the
reading two sections up**: the bit *word* was never the wall, the retained *ledger's* leaf was,
and it moves by two absorptions.

Nothing here is built, and the boundary is the package's: the absorbed families need the new
residual types the suppliers' proofs reserve, the rows are pinned by digest to unmerged branches,
and C1-C7 and the inherited R1-R4 stand exactly as the rest of the package states them.  This is
a **priced target**, one rung deeper into the side that had been binding, and it is the top of
this package.

`verify.py -> check_bit_rung` re-derives the retained row, re-checks every absorption's volume,
bank count, stock drop and padding draw, re-runs the whole 377-rung screen and compares it with
[bitrung.json](research/complex-bank-run3/bitrung.json), and re-prices the point through the
assembly rule -- asserting the leader's minimality, the plateau of 108 rungs, the switch of the
binding side and the gain over the rank-3 rung rather than restating them.

## Verify

```sh
cd research/complex-bank-run3
python3 -B verify.py           # check: pins, rebuild, compare with certificate.json
python3 -B verify.py --write   # authoring: regenerate certificate.json and SOURCE.json
python3 -B rank4rung.py        # the rank-4 measurement: writes rank4-rung.json
python3 -B bitrung.py          # the bit-side rung: writes bitrung.json
python3 -B importer66.py                 # the export import: refuses, codes 0/1/2/3
python3 -B importer66.py --self-test     # the harness's own thirteen cases
python3 -B importer66.py --contract export-contract-bit.json              # the bit twin: same codes
python3 -B importer66.py --contract export-contract-bit.json --exports exports-bit --partial
                                                                          # the real bit drop: reports, code 4
python3 -B importer66.py --contract export-contract-bit.json --self-test  # and its own proof
python3 -B importer66.py --contract export-contract-rank3.json            # the rank-3 rung's gate: refuses, code 2
python3 -B importer66.py --contract export-contract-rank3.json --partial  # ... reports, code 4
python3 -B importer66.py --contract export-contract-rank3.json --self-test # ... and proves itself, thirteen cases
```

`verify.py` passes with exit 0, pins 64 files by sha256 -- the 35 this package owns (bitrung.py and
its artifact bitrung.json, and the five ranked heads of #233 among them), the two upstream
certificates it is priced against (#207's frontier and #233's source-assisted v4 layer), the 16 the
vendored rung-1 package carries and the 11 in the bit drop, its reproduction evidence included --
and rebuilds the whole complex-side
ladder (base, rung 2, rungs 3 and 4), both paid moments per rung, the two 47-constraint
assemblies with adjacent-grid rejection, the eligibility scan, the PR208 replica, the padded
schedule (795 banks, padding 0/2/6 registers per bank, stock drops 531/198/66), the instanced
inventories (4,176 items, 795 banks, the digests), the normalizer export contract (all 6
exports, 7 acceptance tests and 11 obligations mapped, every citation resolved against the pins,
and the 0-of-6 body reading), the bit-side twin contract (its 6 exports, the four obligations
quoted word for word and mapped, the 0-of-6 reading, the checker it pins -- asserted to be
the bit word's own and not this side's -- and the drop it now ships: 10 of the 15 bodies, 8
anchored, the gate deciding A2 and A3 on them and reporting the other five, exit 4), the rank-3
rung's contract on the newly pinned row (its 6 exports, 7 acceptance tests and C1-C7 restated and
quoted verbatim, every citation resolved, the assignment re-instantiated from its addressing rule
with zero padding, the retained ledger re-derived, the bit leaf re-derived through #219's vendored
arithmetic and the point re-priced through the assembly rule and the 47-constraint assembly --
asserted bit-bound and above the published top -- and the 0-of-6 body reading machine-read from
the row's own key set), the rank-3 rung's stability across the six ranked heads of #233 and the
nine width-66 rows of the repository (the criterion checked against the ledger's own test on every
row, and the four findings asserted), the rank-4 rung on the pinned row (the volume criterion on
every head, the padded schedule's nine-slot shortfall, the whole T1 tiling enumeration, every
price, the unmoved κ and the required bit leaves, all re-derived), the bit-side rung on #219's rung-1
word (the retained row re-derived, every absorption's volume, bank count, stock drop and padding
draw re-checked, the whole 377-rung screen re-run and compared with bitrung.json, the leader's
minimality, the 108-rung plateau and the switch of the binding side asserted, and the point
re-priced through the assembly rule and its unchanged 47 constraints), the rank-3 rung's gate as
code runs it (the contract in the importer's dialect, the ten bodies, the thirteen-case
self-test, the refusal and the partial report), the modulus
scan (which widths the pinned
row admits, and that only the pinned width is priced), the supplier scan and the density curve
with both of their calibrations, the per-target requirement table (each line re-derived from the
assembly rule and tested one `10^-18` step below its budget), and re-runs the T1 tiling
enumeration against the pinned `schedule66.json`; it reproduces #207's, #219's and #224's
published grid points exactly. The vendored rung-1 package also self-verifies in place:

```sh
cd research/complex-bank-run3/references/pr219-run1 && python3 -B verify.py
```

## Scope and limits

* **This is a scheduled target, not a witness.** The accounting and the padded bank schedule
  are certified; C1-C7 and the inherited R1-R4 are open, so the kappa is conditional on them in
  exactly the sense #219 states for rung 1 and #224 for rung 2. It is not an unconditional
  multiplication theorem, not a practical multiplier, and not a Lean/kernel certificate.
* T1 is settled here (the enumeration above, plus the padded schedule), and C1's combinatorial
  half with C5-C7's inventories are instanced on top of it; what all of that settles is a
  *schedule*: the bank geometry, the item addresses and the padding draw are checked, the
  normalizer, frames, charts and prime witnesses are C1 (physical half), C2, C3 and C4.
* The whole-bank volume condition is necessary and is the criterion the built rungs use; it is
  not sufficient -- for the two new families it is not even compatible with a width-66 tiling
  at the bank count it prices, which is why the padded schedule exists.
* Nothing here bounds any *other* complex-side lever: the ladder is over this supplier's
  child ledger at this bank width. A different word, width or frame layout is not priced.
* The ladder inherits every interface #207/#219/#224 inherit (all-size compiler, weighted and
  restored selector, routing/layout, fixed-tape leaf, prime supply, precision/recovery,
  analytic transfer).
* The `10^-10` supplier field (PR193's published `complex_saving = 219037/312500000`) is
  priced too, in `certificate.json` -> `conservative_variant`, rather than ignored.

## Credits

Rung 1, its retained-ledger schedule, the interval-moment engine and the 47-constraint
assembly are **PR219** (`research/residual-bank-run1`, head `237067f`) -- vendored
byte-identically under `references/pr219-run1/` and imported, not re-implemented; the frontier
floor and the complex ledger's own shape are **PR207** (`research/coordinated-crossover-pr200`,
head `cd14825`), whose certificate is vendored verbatim; rung 2 and the ceiling argument it
rests on are **PR224** (`research/complex-bank-run2`); the bank-absorption ladder and the
`10^-10` replica price are **PR208** (`research/composed-diagonal-bit-bootstrap`); the
underlying bank proof and engine chain is PR200/PR205 (Chafik Boukhalfa and the PR197/PR205
line) and PR184/PR168-v4 (icekylinx/eumemic) as inherited through them. This package adds
rungs 3 and 4, their prices, the exhaustion of the ledger's whole-bank criterion, the T1
enumeration of the width-66 tilings (with its negative result), the padded bank schedule
(`prototype66.py`) and the next-step arithmetic. Apache-2.0; no existing file is changed.
