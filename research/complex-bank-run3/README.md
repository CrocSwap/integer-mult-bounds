# Rungs 3 and 4 of the bank ladder: the complex ledger's remainder, its padded width-66 bank schedule, and kappa = 7.11599961413937e-4

**A scheduled target, not a witness, and the same blocker as rung 2.** This package prices the
rest of the bank ladder above PR224's rung 2 -- two more whole-bank families of the complex
ledger -- records where the accounting criterion the built rungs use stops, and then builds the
bank schedule those rungs need: a width-66 bank tiled by the family's blocks plus a fixed
pattern of retained ones (`prototype66.py`). The padded schedule is admissible where the
unpadded bank count was not, and it prices **higher**, so the top of the ladder is the padded
rung 4.

## Result

| Rung | what leaves the ledger | kappa | Binding | Status |
|---|---|---|---|---|
| frontier, #207 | — | `1366380910073/2*10^15` = 0.0006831904550365 | bit | reproduced here **exactly** |
| rung 1, #219 | bit rank-22 bin, 6,116 width-72 banks | `700427501305159/10^18` = 0.000700427501305159 | complex | reproduced here **exactly**, by importing the vendored #219 package |
| rung 2, #224 | complex rank-11 family, 531 banks | `354145785295363/5*10^17` = 0.000708291570590726 | complex | rebuilt here **exactly** by this package's own ledger module |
| rung 3, **volume criterion** | + complex rank-16 family, 192 banks | `710572698755137/10^18` = 0.000710572698755137 | complex | accounting only: no width-66 tiling hosts 192 banks (T1) |
| rung 3, **padded schedule** | + rank-16 family, 198 banks x (4 blocks + 2 registers) | `177696102182119/25*10^16` = **0.000710784408728476** | complex | **+0.3520%** over rung 2 |
| rung 4, **volume criterion** | + complex rank-20 family, 60 banks | `355587847933979/5*10^17` = 0.000711175695867958 | complex | accounting only: no width-66 tiling hosts 60 banks (T1) |
| **rung 4, padded schedule (the top)** | + rank-20 family, 66 banks x (3 blocks + 6 registers) | `711599961413937/10^18` = **0.000711599961413937** | complex | **+0.4671%** over rung 2, **+1.5951%** over rung 1, **+4.1584%** over the frontier |

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

## Verify

```sh
cd research/complex-bank-run3
python3 -B verify.py           # check: pins, rebuild, compare with certificate.json
python3 -B verify.py --write   # authoring: regenerate certificate.json and SOURCE.json
```

`verify.py` passes with exit 0, pins 30 files by sha256, rebuilds the whole complex-side
ladder (base, rung 2, rungs 3 and 4), both paid moments per rung, the two 47-constraint
assemblies with adjacent-grid rejection, the eligibility scan, the PR208 replica, the padded
schedule (795 banks, padding 0/2/6 registers per bank, stock drops 531/198/66), the instanced
inventories (4,176 items, 795 banks, the digests), the normalizer export contract (all 6
exports, 7 acceptance tests and 11 obligations mapped, every citation resolved against the pins,
and the 0-of-6 body reading), the modulus scan (which widths the pinned
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
