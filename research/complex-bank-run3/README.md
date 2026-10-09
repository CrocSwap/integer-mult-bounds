# Rungs 3 and 4 of the bank ladder: the complex ledger's remainder priced to kappa = 7.11175695867958e-4, and the ladder's top

**A priced target, not a witness, and the same blocker as rung 2.** This package prices the
rest of the bank ladder above PR224's rung 2 -- two more whole-bank families of the complex
ledger -- and records where the accounting criterion the built rungs use stops.

## Result

| Rung | what leaves the ledger | kappa | Binding | Status |
|---|---|---|---|---|
| frontier, #207 | — | `1366380910073/2*10^15` = 0.0006831904550365 | bit | reproduced here **exactly** |
| rung 1, #219 | bit rank-22 bin, 6,116 width-72 banks | `700427501305159/10^18` = 0.000700427501305159 | complex | reproduced here **exactly**, by importing the vendored #219 package |
| rung 2, #224 | complex rank-11 family, 531 banks | `354145785295363/5*10^17` = 0.000708291570590726 | complex | rebuilt here **exactly** by this package's own ledger module |
| **rung 3, this package** | + complex rank-16 family, 192 banks | `710572698755137/10^18` = **0.000710572698755137** | complex | **+0.3221%** over rung 2; blocked (below) |
| **rung 4, this package** | + complex rank-20 family, 60 banks | `355587847933979/5*10^17` = **0.000711175695867958** | complex | **+0.4072%** over rung 2, **+4.0963%** over the frontier; blocked (below) |

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
exactly the bank count. The ladder's three absorptions occupy **783 width-66 banks** in total
(531 + 192 + 60), and the top row is `W = 35,373`, rank mass `2,330,658`, 635,265 children in
17 families, largest child 19.

## What the pins do not provide (the blocker, unchanged from rung 2)

`obligations.json` states C1-C7 and T1 and inherits #219's R1-R4. The two facts that decide
the status are read from the pins, not asserted:

* **The complex supplier still has no bank construction.** Its certificate carries no key
  containing `bank` at all (`certificate.json` -> `blocked_on`, machine-checked), and neither
  does #207's frontier certificate. The only banked word in the pins is the **bit** word's
  entrance-gauge pack (#205: 45,842 banks, width 72, rank-60 exteriors), a mechanism specific
  to that word's entrance structure.
* **The new families have no inventory.** Nothing enumerates the complex word's rank-16 or
  rank-20 children, exactly as nothing enumerates its rank-11 family or #219's rank-22 bin
  before its own inventory was written. A rung that cannot name its items cannot be built.

One further obligation is specific to rungs 3 and 4 and worth stating precisely because it is
**not** a construction: rank 11 divides the bank width (`66 = 6 * 11`) and needed no mixture,
but `66 = 4 * 16 + 2` and `66 = 3 * 20 + 6`, so the rank-16 and rank-20 blocks cannot tile a
66-wide bank alone. Their banks must mix block sizes (T1), which is the same obligation #219
carries for the bit word as R1 -- admissible tilings of width 72 over families {4, 24, 22} --
with no analogous enumeration to inherit.

## What the top rung implies for the next step

While the complex branch caps the budget, the assembly's ceiling is `budget/(1+budget)` with
the budget capped in turn by the bit leaf of #219's rung-1 bit word (7.2825e-4). So:

* reaching `kappa = 7.2e-4` needs a complex coarse saving of `7.2051877e-4`, i.e. **+1.242%**
  over the top rung's own coarse saving -- more banking than this ledger contains;
* reaching `7.5e-4`, `8e-4` or `1e-3` is **impossible on this bit word**: the leaf caps kappa
  at `1819302815717/25*10^16 = 7.277251...e-4` there, so those targets need a new bit word
  before any complex-side work can matter.

## Verify

```sh
cd research/complex-bank-run3
python3 -B verify.py           # check: pins, rebuild, compare with certificate.json
python3 -B verify.py --write   # authoring: regenerate certificate.json and SOURCE.json
```

`verify.py` passes with exit 0, pins 21 files by sha256, rebuilds the whole complex-side
ladder (base, rung 2, rungs 3 and 4), both paid moments per rung, the two 47-constraint
assemblies with adjacent-grid rejection, the eligibility scan and the PR208 replica, and
reproduces #207's, #219's and #224's published grid points exactly. The vendored rung-1
package also self-verifies in place:

```sh
cd research/complex-bank-run3/references/pr219-run1 && python3 -B verify.py
```

## Scope and limits

* **This is a priced target, not a witness.** The accounting is certified; C1-C7, T1 and the
  inherited R1-R4 are open, so the kappa is conditional on them in exactly the sense #219
  states for rung 1 and #224 for rung 2. It is not an unconditional multiplication theorem,
  not a practical multiplier, and not a Lean/kernel certificate.
* The whole-bank volume condition is necessary and is the criterion the built rungs use; it
  is not sufficient on its own for the two new families, which owe T1's tiling.
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
rungs 3 and 4, their prices, the exhaustion of the ledger's whole-bank criterion and the
next-step arithmetic. Apache-2.0; no existing file is changed.
