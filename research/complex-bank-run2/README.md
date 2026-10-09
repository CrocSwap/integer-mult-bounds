# Rung 2 of the bank ladder is capped on the complex side: kappa = 7.08291570590726e-4 priced exactly, blocked on a complex-side bank construction (no new kappa)

**No new kappa, and no completed construction.** This package prices the next rung of
PR208's bank-absorption ladder above #219 and records the two facts that decide when it
can be built: **rung 1 already sits on the complex branch's ceiling**, and the rung above
it needs a **bank construction on the complex supplier that no package in the queue has**.

## Result

| Rung | kappa | Binding | Status |
|---|---|---|---|
| frontier, #207 | `1366380910073/2*10^15` = 0.0006831904550365 | bit | reproduced here **exactly** from #207's own `a_bit`/`a_complex` |
| rung 1, #219 | `700427501305159/10^18` = 0.000700427501305159 | complex | reproduced here **exactly**, by importing the vendored #219 package |
| rung 2, this package | `354145785295363/5*10^17` = 0.000708291570590726 | complex | **+1.122753%** over rung 1, **+3.674102%** over the frontier; blocked (below) |

The price is the same ledger in two independent conventions: **0.00070829157059072603** on
the `10^-18` grid in the convention of the queue's latest rungs (`eta = beta = 10^-24`,
`weak = 10^-30`), and **`3541457/5*10^9`** on the `10^-10` grid of PR208's pricing model
(`stop = 10^-9`, `eta = 10^-8`), which is PR208's own published value for this rung --
reproduced here, not restated.

## Why rung 2 has to be taken on the complex word

#219's rung 1 absorbs the bit word's rank-22 bin and then binds on the complex supplier.
This package shows that it does not merely bind there: it lands **on the complex branch's
ceiling**. With the complex coarse saving `C = 7.00918443859411e-4`, the assembly's bound
is `C/(1+C) = 7.0042750130515981e-4`, and rung 1's kappa is `7.00427501305159e-4` --
**8.5e-19 below it, inside one grid step**. The bit side's own headroom at that point is
1.95e-5 of coarse saving, and it is unspendable: whatever the bit ledger does, the
composition is capped by the complex branch.

So every further rung starts by raising the complex supplier's coarse saving. Rung 2 does
that by absorbing the complex word's rank-11 family, and it likewise lands on the *new*
ceiling (`708793603125109/1000708793603125109` = 7.082915705907269e-4, gap 8.6e-19).

## The rung-2 ledger

On the pinned complex profile (`m = 66`, one copy `W = 12,052`, deficit `1,320`, ledger
bin 11 = **1,062** children per vertex):

| | before | after |
|---|---|---|
| absorbed family | bin 11: 1,062 per vertex (3,186 over the three copies) | out of the ledger |
| dirt volume | — | `11 * 3,186 = 35,046` registers = `66 * 531` **banks**, exactly (177 one copy) |
| stock (three copies) | 36,156 | 35,625 (drop **531** = the bank count) |
| rank mass | 2,382,336 | 2,347,290 |
| children | 639,441 | 636,255 |
| largest child | 20 | 20 |
| complex coarse saving | 7.00918443859411e-4 | **7.08793603125109e-4** |

Three invariant checks make the absorption free rather than a re-labelling: the volume
fills whole banks (`35,046 = 66 * 531`), the retained ledger satisfies the row identity
`66 * 35,625 - 2,347,290 = 3,960`, and the stock falls by exactly the bank count. The
absorbed share of the ledger's rank mass is 1.471%.

One further property is worth stating precisely because it is **not** a construction: the
family's rank divides the bank width (`66 = 6 * 11`), so a bank admits a uniform six-block
tiling of the new family alone and no mixture with older families is needed. That is a
necessary condition satisfied, not a built bank.

## What blocks the rung

`obligations.json` states C1-C5 and inherits R1-R4 from #219. C1 is the blocker, and it is
a fact about the queue rather than a gap in this package:

* **The complex supplier has no bank construction.** Its certificate
  (`references/pr219-run1/references/pr193-source-assisted-v4.certificate.json`) carries
  no key containing `bank` at all (`certificate.json` -> `blocked_on`, machine-checked),
  and neither does #207's frontier certificate.
* **The only banked word in the pins is the bit word's.** #205's `physical.banks` (45,842
  banks) with its gauge roles, distinct gauges, copies and `bank_controls` is the
  entrance-gauge pack of the width-72 bit word -- a mechanism specific to that word's
  entrance structure, not something the complex word inherits.
* **The family has no inventory.** The only occurrence inventory in the pins is #219's
  bit-side `inputs/absorbed-occurrences.json` for rank 22, which is exactly what makes
  #219's R1 a closed checklist. Nothing enumerates the complex word's 1,062 rank-11
  children, so C5 has no starting point and C1's item-to-block map cannot even be stated.

A rung that cannot name its items cannot be built. That is the report.

## A grid-precision note for reviewers

PR193 publishes `complex_saving = 219037/312500000 = 7.009184e-4`, which is its value on
the `10^-10` grid and sits `4.3859411e-11` below the `10^-18` certified paid moment of the
same profile. #207's `a_complex` and #219's rung 1 both price the certified moment, and
this package reproduces both numbers exactly, so rung 2 is priced on the certified moment.
The coarser field is priced too, as `supplier_field.conservative_variant`: there the
complex branch's ceiling already sits at rung 1, which is why the rung is only visible on
the refined grid.

## Verify

```sh
cd research/complex-bank-run2
python3 -B verify.py           # check: pins, rebuild, compare with certificate.json
python3 -B verify.py --write   # authoring: regenerate certificate.json and SOURCE.json
```

`verify.py` passes with exit 0 and prints the conditional kappa. It pins 21 files by
sha256, rebuilds the rung-2 ledger, both paid moments, the 47-constraint assembly and the
PR208 replica, and reproduces #207's and #219's published grid points exactly. The vendored
rung-1 package also self-verifies in place:

```sh
cd research/complex-bank-run2/references/pr219-run1 && python3 -B verify.py
```

## Scope and limits

* **This is a priced target, not a witness.** The accounting is certified; C1-C5 and the
  inherited R1-R4 are open, so the kappa is conditional on them in exactly the sense #219
  states for rung 1. It is not an unconditional multiplication theorem, not a practical
  multiplier, and not a Lean/kernel certificate.
* Nothing here bounds any *other* complex-side lever: only the rank-11 family of the
  current complex ledger is priced, and only at the ledger's own bank width.
* The rung inherits every interface #207/#219 inherit (all-size compiler, weighted and
  restored selector, routing/layout, fixed-tape leaf, prime supply, precision/recovery,
  analytic transfer).

## Credits

Rung 1, its retained-ledger schedule, the interval-moment engine and the 47-constraint
assembly are **PR219** (`research/residual-bank-run1`, head `237067f`) -- vendored
byte-identically under `references/pr219-run1/` and imported, not re-implemented; the
frontier floor is **PR207** (`research/coordinated-crossover-pr200`, head `cd14825`), whose
certificate is vendored verbatim; the bank-absorption ladder and the `10^-10` replica price
are **PR208** (`research/composed-diagonal-bit-bootstrap`); the underlying bank proof and
engine chain is PR200/PR205 (Chafik Boukhalfa and the PR197/PR205 line) and PR184/PR168-v4
(icekylinx/eumemic) as inherited through them. This package adds the complex-side ledger,
its price, the ceiling argument and the blocker. Apache-2.0; prepared with Anthropic
Claude assistance. No existing file is changed.
