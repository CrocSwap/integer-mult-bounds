# What is proved here, and what is only priced

## Setting

PR208 prices a ladder of bank absorptions on PR200's bit word. #219 built rung 1 of that
ladder as a certified accounting construction: the rank-22 bin leaves the ledger, its
440,352 three-copy registers of dirt become 6,116 width-72 banks, and the composition
`T(n) = O(n (log n)^(1-kappa))` follows with

    kappa = 700427501305159/10^18 = 0.000700427501305159,

conditional on that submission's R1-R4. This package asks what rung 2 is, prices it
exactly, and reports why it cannot be built yet.

## Fact 1: rung 1 sits on the complex branch's ceiling

The composition's budget is `a = min(bit_leaf, (1-beta) C_complex - weak)` and its kappa
is `(1-eta) q/(1+q)` with `q = a(1-2 eta)`, floored to the grid. Holding the complex coarse
saving `C_complex = 700918443859411/10^18` fixed, the largest kappa any bit ledger can
reach is that expression at `a = C_complex`,

    C/(1+C) = 700918443859411/1000700918443859411 = 7.0042750130515981e-4.

Rung 1's kappa is `7.00427501305159e-4`: `8.52e-19` below that ceiling, i.e. inside one
`10^-18` grid step. Both numbers are produced here by the vendored #219 code and by this
package's replica of the assembly rule, which also reproduces #207's published
`1366380910073/2*10^15` exactly from #207's own `a_bit`/`a_complex`.

Consequently a rung above rung 1 cannot be taken on the bit word. The bit side's headroom
at that point is 1.95e-5 of coarse saving and is unspendable while the complex branch
binds.

## Fact 2: the rung-2 ledger, and its invariants

Let the complex supplier's row be the pinned profile: width `m = 66`, one copy
`W = 12,052`, deficit `D = 1,320`, and ledger `hist` with `hist[11] = 1,062`. Over the
supplier's three copies let `H = 3 * hist`, `W3 = 3W`, `D3 = 3D`, so that the row identity
`66 * 36,156 - 2,382,336 = 3,960` holds with integral stock.

Absorb the rank-11 family:

1. **volume**: `11 * H[11] = 11 * 3,186 = 35,046 = 66 * 531`, so the absorbed dirt fills
   exactly 531 banks (177 one copy);
2. **retained ledger**: `H' = H \ {11}` has rank mass `2,347,290 = 2,382,336 - 35,046`;
3. **row identity and stock**: `W3' = (2,347,290 + 3,960)/66 = 35,625`, integral, and
   `W3 - W3' = 531` equals the bank count -- the absorption removes exactly the banks it
   creates;
4. **largest child** is unchanged at 20, and the children count falls from 639,441 to
   636,255.

These four are asserted in `ledger.py` and re-derived in `verify.py`; the whole-bank
condition, the row identity and the stock-drop identity are the whole of what the
supplier's own allocation rule requires of a schedule.

## Fact 3: the prices

Two paid moments on the pinned engine (PR200's exact rational interval moment, used on the
complex side without the bit branch's rare-class fallback, as #219 uses it):

    coarse(before) = 700918443859411/10^18  = 7.00918443859411e-4
    coarse(after)  = 708793603125109/10^18  = 7.08793603125109e-4

each the largest `10^-18` grid point whose paid moment is below 1, with the adjacent grid
point excluded. The frontier certificate's `a_complex` equals the first, and
`verify.py` asserts that equality -- the row priced here is the one the composition already
uses.

Assembling with the bit leaf of rung 1 and the absorbed complex saving gives the rung-2
budget `a2 = (1-beta) * coarse(after) - weak` (the complex branch binds), hence

    kappa_2 = 354145785295363/5*10^17 = 0.000708291570590726 (binding complex),

with the next `10^-18` grid point rejected by the unchanged 47-constraint assembly, and
`kappa_2 = 8.56e-19` below the new ceiling `coarse(after)/(1+coarse(after))`.

Independently, in the `10^-10` convention of PR208's pricing model, the same ledger prices
`3541457/5*10^9 = 7.082914e-4` -- PR208's own published value for this rung, reproduced
here; the two conventions differ by `1.7e-11`, four orders below their agreement.

## Fact 4: the blocker

`obligations.json` lists five new obligations and inherits #219's four. The first is not
dischargeable from the pins:

* the complex supplier's certificate has **no key containing `bank`**, and neither does
  #207's frontier certificate (asserted in `verify.py` through `blocked_on`);
* the only bank construction in the pins is #205's `physical.banks` -- 45,842 banks with
  gauge roles, distinct gauges, copies and `bank_controls` -- which banks the **bit**
  word's selected entrance-gauge exteriors at width 72; its mechanism does not exist on the
  complex word;
* no pin enumerates the complex rank-11 family: #219's `inputs/absorbed-occurrences.json`
  covers rank 22 of the bit word only, and it is precisely that enumeration that makes
  #219's R1 a closed checklist.

So C1 (the complex bank construction, its blocks and normalizers) and C5 (the family's
inventory and provenance) are both open with no starting material in the queue.

## What would discharge C1-C5

1. **C5** first: an enumeration of the complex word's rank-11 occurrences by frame and
   chain, with a bijection onto the 3,186 three-copy children and a check that no other bin
   is touched.
2. **C1**: the complex-side bank construction -- banks of width 66, the normalizer sending
   each item's true residual projector to its block, the six-block pattern per bank, and
   the hashed item-to-bank/offset map for all 531 banks.
3. **C2-C4**: the formal-column replay of the modified complex word (F2 and the defining
   integers, with the lift checked through `exact_scalar_program_sha256` rather than a
   container digest), exact charts, incidence colouring and prime witnesses for the new
   blocks, and the moment-envelope parity of the retained row priced here (stock 35,625,
   deficit 3,960, no rare-class fallback on the complex side); any completion child
   C1 introduces re-enters the ledger and the kappa is recomputed.
4. Inherited: #219's R1-R4 for the bit-side rank-22 absorption, unchanged.

Until then the kappa above is a priced, exactly certified **target** -- the same status
#219 gives its rung-1 number, with one rung's worth of extra mechanism to build.
