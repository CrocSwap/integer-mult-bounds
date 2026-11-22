# Necessary budget for nonzero-entrance lender borrowing

This ledger prices the new nonzero-entrance lender experiment at primitive
comparison rate `b = 0.0016971949509017704265940818773`. It provides necessary
break-even requirements, not a construction or a new kappa. The reference
rate is quoted from PR2374; no frontier admission or outer conversion is
claimed here. The single- and four-alias profiles are now bound to formal
replays in `../LIFTED-CANDIDATE.json` and `../FOUR-CANDIDATE.json`. The larger
models still need complete replayed local profiles. All require native/global
admission.

The strongest result below is the **high48** four-alias construction,
retaining the 32 optional zero-entrance low helpers. In addition to the
fractional capacity screen, an explicit restriction of the inherited owner
map passes exact window, axis and rank-accounting checks with a negative
primitive-rate margin. Native/global admission and the complete outer
transfer remain separate obligations.

## Literal 428-helper owner restriction

The four-alias formal replays leave 428 helpers per call. Relative to the
437-helper PR2269 parent, original helper IDs
`606, 635, 637, 638, 639, 640, 641, 642, 644` disappear in both providers;
every retained helper keeps its original width. `verify_restricted_owners.py`
reconstructs that deletion directly, reindexes native helpers and compacts
offsets only inside each inherited pending bin. It verifies equality with
`RESTRICTED-OWNERS.json.gz` before auditing geometry.

The independent geometry checker from the preceding owner audit verifies
all 285,048 roles across 666 calls: distinct physical owner families, active
data exclusion, strict source/bridge windows, orthogonal pending axes,
prefixes and 7,138 residual spectator charts. Provider profiles and widths
are bound to the exact four-alias replay, with dispatch counts 249 gauge44
and 417 extra. The resulting global profile is

`{1:1587402, 2:337002, 3:283401, 4:84246, 5:26121, 7:2814, 8:4994, 16:167, 48:24479}`.

Its live stock is 66,304 and its exact deficit is 23,680. Two independent
rational interval engines prove excess minus deficit is approximately
**−0.21859429593742802** at the comparison primitive rate, equivalently
moment at most approximately `0.9999999548376808`. This is a strict finite
cost result for this owner map. It is not a full multiplication theorem or
a new kappa certificate.

```sh
python3 -B research/complex-structure-seed39/nonzero-lender-evidence/budget/verify_restricted_owners.py
```

Expected first line:
`PASS_428_HELPER_LITERAL_RESTRICTION_WINDOWS_AXES_PROFILE_AND_EXACT_COST`.
The receipt `RESTRICTED-VERIFICATION.json` records source pins, all profile
counts, exact interval endpoints and rejection controls for changed width,
invocation time and slice offset. `RESTRICTED-COST.json` is the earlier
arithmetic-only screen and is superseded by this scoped geometry receipt.

The high48 construction requires **76 simultaneous private zero buffers**.
This checker does not reserve those buffers, verify the new native scalar
programs or phases, or discharge the complete finite/global invoice and
outer transfer. Its inherited physical-envelope field excludes those
buffers and is explicitly marked unverified. The complete physical invoice
must charge them.

PR2374's current outer route is the capped-phase-fusion transfer, with
`kappa = C - 1/FLOOR - BACKOFF` and primitive `b = C - R0`.
Its pinned source is `5449da65da12bdfd94675dccc38731eaa91e93b6`;
the retained `../PR2374-SPEC.json`, `../PR2374-OUTER-CLAIM.json` and ledger
provide the exact parameters. `OUTER-RATE-CHECK.json` additionally prices
the alternative balanced relation `b = kappa/(1-kappa)`. The literal map's
positive margin under that alternative does **not** reject the current
outer route. The alternative computation is not an outer admission check.
Reproduce it with `python3 -B
research/complex-structure-seed39/nonzero-lender-evidence/budget/verify_balanced_alternative.py`;
the expected status is
`PASS_ALTERNATIVE_BALANCED_RATE_ARITHMETIC_NOT_CURRENT_OUTER_ROUTE`.

## Constructed single alias and fractional capacity models

`verify_capacity_witness.py` binds all four retained single-alias formal
replays (two providers, high48/full80 baselines). Their measured delta is
`4(H1 + H7 - H8) - H3 - H5`, with helper inventory change `-W8`.
The four rank-8 center copies are split into rank 7 and rank 1; existing
target rank-1 visits move earlier. The complete single-alias local rank mass
decreases by eight and `mass - helper width = 1856` is preserved.

The four-alias replay confirms exactly
`4(H1+H7-H8) - 4H3 - 4H5` and `-4W8` in each baseline/provider. Thus the
high48 four-alias/four-split capacity result is bound to a measured formal
profile, not merely extrapolated from one alias.

The checker separately evaluates the explicit larger model
`n(-H3-H5) + s(H1+H7-H8)` and inventory change `-nW8`, for `s` shared
copy splits. It does not infer an arbitrary-subset additivity theorem from
the single case. Additional target coalescences, if realized, are omitted;
any added work must still be included before admission.

The two independent engines verify exact rational bin allocations and the
following excess-minus-deficit upper bounds (displayed approximately):

| Baseline and model | gauge44 | extra |
|---|---:|---:|
| high48, actual 1 alias / 4 splits | +5.800750 | +3.409407 |
| high48, actual 4 aliases / 4 splits | −55.572055 | −57.963398 |
| high48, model 4 aliases / 8 splits | −41.875657 | −44.266999 |
| high48, model 8 aliases / 8 splits | −123.706063 | −126.097406 |
| high48, model 10 aliases / 8 splits | −164.621267 | −167.012609 |

For the actual single-alias cases, a separate feasible rational dual also
proves positive lower bounds, so the displayed positive values are not
merely costs of a poorly chosen packing. For the larger models, negative
upper bounds prove only that the explicit **fractional capacity allocation**
fits the model's moment budget. They do not provide source assignments,
chronology, integer bank/family hosting or a compiled multiplication circuit.

The retained full80/16-alias/8-split model also has a favorable fractional
allocation. The dimension-at-most-four census supplies only ten distinct
restored lenders; block648 has dimension-five first use and needs a separate
census. The later `../BLOCK-POOL.json` additionally bounds the frozen
one-use mechanism by at most fifteen aliases: twelve dimension-four slots
share only eleven eligible lenders, even if all eleven could be restored
and all four dimension-five slots had additional lenders. No sixteen-lender
assignment is supplied here. That model is a cost comparison, not a
construction option established by this experiment.

Reproduce the exact primal and dual checks with:

```sh
python3 -B research/complex-structure-seed39/nonzero-lender-evidence/budget/verify_capacity_witness.py
```

Expected first line:
`PASS_EXACT_FRACTIONAL_CAPACITY_MODELS_ACTUAL_SINGLE_REJECTED_NO_NEW_KAPPA`.
The retained receipt is `EXACT-CAPACITY-WITNESSES.json`; the exact pattern
allocations are in `HIGH48-CAPACITY-WITNESSES.json` and
`CAPACITY-WITNESSES.json`. The nomination domain was the block-sized counts
4, 8, 12, 16 for full80, followed by counts 1, 4, 8, 10 for high48 after
the dimension-at-most-four census found ten restored lenders. Only full80 count 16
and the four high48 counts are retained as verified capacity witnesses.
SciPy nominated them; verification needs only Python's standard library.

The important accounting distinction is between saving local recursive rank
and saving global recursive rank. If a new alias removes one width-8 helper,
the remaining capacity must carry eight additional padding ranks. Removing
eight local rank units alone therefore preserves the inherited deficit.
Adding a paid rank-1 descent and return increases total recursive mass by two
per call, even if the local rank total is still six lower than before.

Let `H` be the complete new local paid profile, including source access,
compensation, copies, restoration and every recursive child, and let `W` be
its helper width inventory. Define

`delta = sum_r r H(r) - sum_w w W(w) - 1856`.

In the inherited nine-stage geometry, the new available deficit is exactly

`D_new = 23680 - 666 delta`.

Consequently one extra down/up pair of rank-1 children reduces the deficit
from 23,680 to 22,348. This excludes its additional exponent cost. The exact
pair cost in the excess-plus-deficit ledger is `2 + 2 E_b(1)`, approximately
`2.014616644964054` per call, where
`E_b(r) = r ((73/r)^b - 1)`. Sixteen separately paid pairs leave deficit 2,368.

## Exact necessary lower bound

The checker verifies a fixed rational capacity dual against all 5,927
whole-helper patterns in bin capacities 8, 16, 32, 48 and arbitrary full-73
banks. Dynamic programming covers every residual padding composition with
positive child ranks at most 51. Two retained independent rational interval
engines certify the rank excesses and every dual inequality. Source hashes
and parent geometry are checked first.

For the complete inventory and profile, the bound tested is

`666 sum_r H(r) E_b(r) + certified_padding_excess_lower_bound > D_new`.

A strict result rejects that accounting case under this geometry. Failure
to reject is not admission: the dual need not be optimal, and chronology,
source ownership, physical reservations and ordinary compiler work remain
separate obligations. Additional physical banks are allowed favorably by
the capacity relaxation. No change to the outer geometry is silently made.

The pinned full-80 baselines have helper widths
`{4:4,5:4,7:36,8:84,9:272}` and no width-3 helper. Thus the initial guess
"remove width 3 plus width 8 and replace by width 8" cannot simply be
subtracted from this inventory. Source X33 and low helper 644 instead both
have entrance dimension 1 and baseline final dimension 9. If X33 still ends
at dimension 9 after a valid alias, the helper inventory loses width 8.
Legality and exact recursive savings require the new full-word replay.

## Conditional break-even requirements

The table below assumes each alias removes one width-8 helper and eight
units of local rank mass **before** paid corrections. It states how much
local excess must be saved before appending the specified rank-1 pairs.
It does not assert that any profile achieves that saving, or that a pair
can be shared between aliases. Values shown are approximate; the receipt
contains outward rational intervals.

| Baseline | Aliases | Paid down/up pairs | Required gross excess saving per call |
|---|---:|---:|---:|
| extra | 1 | 0 | 0.231748514174216 |
| extra | 1 | 1 | 2.246365159138270 |
| extra | 16 | 0 | 0.467877756674216 |
| extra | 16 | 1 | 2.482494401638270 |
| extra | 16 | 16 | 32.701744076099075 |
| base | 1 | 0 | 0.250697421365488 |
| base | 16 | 0 | 0.486826663865488 |

These requirements follow directly from the reference margin, the dual
cost of removing each width-8 demand and any paid recursive correction.
They do not use the invalidated singleton-additivity model or reopen the
previous 100-case search. A change in other helper widths or in total local
rank mass must be priced explicitly instead of using this table.

## Reproduction

From the repository root, with Python's standard library:

```sh
python3 -B research/complex-structure-seed39/nonzero-lender-evidence/budget/price.py
```

Expected first line:
`PASS_NONZERO_LENDER_NECESSARY_COST_ACCOUNTING_NO_CONSTRUCTION_CLAIM`.
The following lines report reference lower-bound margins near 156.4803443
and 143.8603721. These reference values calibrate the new mechanism's
required savings; they are not new construction claims.

To price an actual proposed full profile, pass `--case PATH`. The JSON must
contain `local_profile` and `width_inventory` objects whose keys are rank
and width strings. Include all extra positive-rank operations in the local
profile. The checker recomputes mass and deficit; it does not assume the
inherited deficit remains valid. Any supplied profile remains an assumption
until independently bound to a complete construction. `--out PATH` emits
a deterministic receipt. The retained reference receipt is `ACCOUNTING.json`.

Controls reject a nonexistent width-3 removal, an infeasible dual and a
forged source pin. They also check the exact 1,332-unit deficit charge for
two additional rank-1 children and the zero-exponent identity. Optimized
Python is rejected because one inherited arithmetic engine uses assertions.

The base commit is `7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261`; assignment
seed 39. Source and engine pins are embedded in the checker and receipt.
Credit: Cinna Davis / PR2226; Jeremy Kothe / PR2269; Sagar Thakrar / PR2339;
the retained capacity and independent interval work. Prepared for Tekalign
(@tekuuu), with substantial OpenAI Codex assistance, under Apache-2.0.
