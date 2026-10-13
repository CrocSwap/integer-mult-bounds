# Restored target pairs in the selected X4 compensation

**Finite complex-supplier circuit construction; no new κ.** On the selected
PR799 X4 word, 56 disjoint signed-unit target pairs reduce the fully paid
zero-frame compensation from **6,320 to 3,276 additions**, including preparation
and restoration. The full emitted programs save **33,800 real-component
primitives per orientation** under the unchanged binary-Horner lowering.

| Full emitted scalar program | Original | Candidate |
| --- | ---: | ---: |
| Scalar macros, either orientation | 19,197 | 16,153 |
| Forward real-component primitives | 193,162 | 159,362 |
| Inverse-transpose real-component primitives | 193,210 | 159,410 |
| Forward positive-prefix bound | 6,812,058,044,968,180,837 / 256 | unchanged |
| Reverse positive-prefix bound | 48,299,247,699,832,632,898,063 / 16 | 48,299,247,845,619,250,997,475 / 16 |
| Forward / reverse prefix bits | 55 / 72 | 55 / 72 |

The paid child profile remains
`{1:2548, 2:338, 3:430, 4:194, 5:56, 8:8}`. Every non-scalar event is preserved
in order, including phases, climbs, centre boundaries and residual wrappers.
The accepted conditional κ remains **0.001661634653669567**. This scalar saving
alone changes no recurrence exponent and is not a measured runtime improvement.

## Reproduce

Python 3.10 or newer, standard library only, no network or optimizer:

```sh
python3 -I -B research/complex-x4-compensation-pairs/verify.py
python3 -I -B research/complex-x4-compensation-pairs/test_package.py
```

Expected main marker:

```text
PASS_X4_COMPENSATION_PAIRS pairs=56 compensation=6320->3276 saved_real=33800 columns=728+9 orientations=2 no_new_kappa
```

The second command passes nine focused tests. Both also work under `-O`.
To export both literal candidate event programs, add `--out /fresh/directory`
to the first command. Verification regenerates and compares every result field;
the output directory must not exist. Normal replay takes approximately six
seconds on the author's environment; this is reproduction guidance only.

## Circuit and complete local cost

At the compensation boundary the old operation is `y += C h`, where all 112
targets are arbitrary and all 504 helpers may contain dirt. `experiment.py`
re-derives C from the actual `A + cut + B` map followed by the actual target
precondition; it compares every coefficient with the selected canonical input.
There are 6,320 nonzero coefficients.

For a selected pair `(t,u,s)`, `s` is ±1. Let T be the target shear
`y_t += s y_u`. Replace the compensation by the literal schedule

1. prepare every disjoint T;
2. accumulate `(T C) h` into the prepared targets;
3. restore every target with T⁻¹ in reverse order.

Only row t changes: `C_t` becomes `C_t + s C_u`. Thus the endpoint is exactly
`T⁻¹(T y + T C h) = y + C h` over the rationals and complexes, with arbitrary
initial y and h. The 56 pairs are disjoint, so these transforms commute; no
helper is written, no private array is added, and every target is restored to
its original basis before the next retained event. The reverse program uses
the inverse transpose of every scalar macro in chronological order. Its
composition is the inverse transpose of the same complete endpoint.

All replacement gates are at frame zero. Every touched target has bottom start
frame. Every touched helper has bottom start and FULL end; no entering or
cold-ended helper is touched before its wrapper. Both basis changes occur
before `entry_adapters`. Consequently the complete state and existing frame
schedule at that boundary are identical to the original. The subsequent
scalar, frame, cone, phase, centre and wrapper interfaces are inherited from
the exact source-pinned selected construction.

For a reduced nonzero dyadic coefficient `q = ±a / 2^d`, the retained lowering
charges

`2 (3 + floor(log2(a)) + popcount(a) + d)`

real-component primitives. These are the initial coefficient-stream CLEAR,
every source access, Horner doubling, halving, signed target accumulation and
final CLEAR, on both real and imaginary components. A signed-unit target shear
costs eight, so preparation and restoration cost **16 per pair**, all included.
No coefficient sharing or copy/unit discounts from other pending PRs are added.
All old centre copies/clears and every retained scalar macro remain paid.

The primitive replay gives exact endpoints on all **728 logical input columns
plus nine arbitrary private-input columns** in both orientations. The inherited
eight centre registers and coefficient stream are erased with charged CLEARs;
they are not claimed to restore arbitrary private dirt. All 504 public dirty
helpers are restored. Positive envelopes include every coefficient-work
intermediate. The reverse envelope grows slightly, while the 55/72-bit budgets
remain below the inherited local 192-bit allowance. A global precision or
invoice replay is not claimed.

## Search domain and independent evidence

OS assignment seed **39** chooses the complex-supplier track. Exhaustive scoring
covers all **24,864** ordered distinct target pairs with signs ±1; **2,978** have
positive fully paid saving. A single seeded shuffle followed by descending
gain and greedy disjoint selection yields the 56-pair recipe. The stopping
rule is completion of this census and one greedy pass. This proves neither
optimal pair matching nor optimal general compensation. Larger coefficients,
overlapping bases, helper bases and broader circuit classes were not searched.

`RECIPE.json` records every selected pair and score, and binds the complete
score census. `RESULT.json` records full programs' semantic hashes, exact
prices, prefixes, profiles and endpoint digests. `independent.py` imports no
constructor, retained auditor or experiment code: it replays sparse integer
numerator rows with common dyadic denominators. It checks the original and
candidate logical words on all 728 columns in both orientations, as well as
the complete compensation boundary with arbitrary target inputs.

Negative controls reject missing preparation/restoration, sign and coefficient
errors, dirty-helper writes, dropped private-stream clears, overlapping pairs,
unpaid basis costs, corrupted sources (even after repairing the outer manifest)
and corrupted results. The missing-preparation control **passes a helper-only
column check but fails the arbitrary-target check**. Recompression, JSON
reformatting and standalone optimized relocation are positive controls.

## Provenance, limits and credit

Exact base: `f567884aeb8851b6e794af1184119a3bfbe1e631`. `SOURCES.json` pins the
immutable accepted replay archive and all proof-relevant input JSON fields.
The three inputs are unchanged `native/local/` members of
`research/community-frontier799-audit/integrated799-replay.tar.gz`; their
canonical word and ordered program hashes match PR799's published local pins.
Gzip packaging is not a mathematical equality criterion.

The source is Jeremy Kothe's **PR799** (`80e6463157cfc80b85af09e7e2f14748fe2dac60`)
on Chafik Boukhalfa's **PR741** (`e516b1463606840a15f80aac1995d64ce0092e89`),
icekylinx's gauge44 and the retained cold/entrance/owner/compiler ancestry.
**Sricharan Vagvala's PR749** (`d76c276a9f77df270982a61be7e53219316faf55`)
supplied the restored rational target-pair mechanism on the earlier JP8 word;
its implementation is not imported. That PR credits the binary target-basis
work in **PR713/PR716**. This contribution applies the credited mechanism to
the actual selected X4 matrix and emitted programs, supplies a new complete
pair census, and adds an integer-based full logical replay. No priority for
the mechanism is claimed. PR787 coefficient composition and PR807 CK helper
pairs concern different inputs/circuit blocks. PR864 frame-only optimality
does not exclude changes to this scalar block.

Concurrent **Philipp (@mightyOil), PR883**
(`b31a870a3842b37f6ab97767c506ce91783632a2`) fuses X4's original 168
precondition macros. Here those macros are retained byte-for-byte; the changed
block is the subsequent 6,320-addition helper compensation. Its code and
784-primitive saving are not consumed, and no combined saving is asserted.

Only this research directory is added. Production integration still requires
a typed alternative-compensation step and refreshed source/program bindings,
global hosting, invoice and assembly admission. All-size/compiler,
common-label/mutable-source realization, whole-call hosting, precision/tape,
analytic transfer and bit H1–H5 remain inherited hypotheses. No full supplier
cold replay, whole-repository suite, hosted CI, Lean multiplication theorem,
or independent human review is claimed. See `VALIDATION.md` for checks and
development corrections. The selected frontier and `upstream/` are unchanged.

Prepared for **ToikY** with substantial **OpenAI Codex assistance**, including
one bounded delegated implementation and review of the integer checker.
Apache-2.0; predecessor notices and license are retained alongside this note.
