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

## What the top rung implies for the next step

While the complex branch caps the budget, the assembly's ceiling is `budget/(1+budget)` with
the budget capped in turn by the bit leaf of #219's rung-1 bit word (7.2825e-4). So:

* reaching `kappa = 7.2e-4` needs a complex coarse saving of `7.20518773516934e-4`, i.e.
  **+1.181%** over the top rung's own coarse saving -- more banking than this ledger contains;
* reaching `7.5e-4`, `8e-4` or `1e-3` is **impossible on this bit word**: the leaf caps kappa
  at `1819302815717/25*10^16 = 7.277251...e-4` there, so those targets need a new bit word
  before any complex-side work can matter.

## Verify

```sh
cd research/complex-bank-run3
python3 -B verify.py           # check: pins, rebuild, compare with certificate.json
python3 -B verify.py --write   # authoring: regenerate certificate.json and SOURCE.json
```

`verify.py` passes with exit 0, pins 24 files by sha256, rebuilds the whole complex-side
ladder (base, rung 2, rungs 3 and 4), both paid moments per rung, the two 47-constraint
assemblies with adjacent-grid rejection, the eligibility scan, the PR208 replica, the padded
schedule (795 banks, padding 0/2/6 registers per bank, stock drops 531/198/66), and re-runs the
T1 tiling enumeration against the pinned `schedule66.json`; it reproduces #207's, #219's and
#224's published grid points exactly. The vendored rung-1 package also self-verifies in place:

```sh
cd research/complex-bank-run3/references/pr219-run1 && python3 -B verify.py
```

## Scope and limits

* **This is a scheduled target, not a witness.** The accounting and the padded bank schedule
  are certified; C1-C7 and the inherited R1-R4 are open, so the kappa is conditional on them in
  exactly the sense #219 states for rung 1 and #224 for rung 2. It is not an unconditional
  multiplication theorem, not a practical multiplier, and not a Lean/kernel certificate.
* T1 is settled here (the enumeration above, plus the padded schedule), and what it settles is
  a *schedule*, not a construction: the bank geometry, the item-to-block map and the padding
  draw are checked, the normalizer, frames, charts and prime witnesses are C1-C7.
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
