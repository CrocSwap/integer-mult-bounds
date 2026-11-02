# Composition of the lifted source and the binary tree

This package composes two published constructions. PR6349 supplies the four
native input lifts. PR6348 supplies the binary query tree. Neither construction
is new here. The new result is their complete composition and its conditional
bound. The selected frontier is not changed.

## 1. Source and caller interface

The source is PR6349 at `af7cb6c67f8fc7d82a2e4aee2dd2f07481bf6690`.
Its constructor starts from PR6314's compressed word. The verifier reconstructs
all 17,452 events and compares every payload byte with the published word.
The exact source checks cover all 770 public inputs, the owned fields, the four
input directions and their output corrections. A separate dense transpose
checks all 799 input columns and 638,401 coefficients.

The lifted helper entrances are 496, 649, 663 and 508. They have dimensions
1, 1, 1 and 3. Their independent productive targets have ranks 8, 8, 8 and 6.
The main port interface is unchanged. In the notation of PR6348, each port
supplies `D_s U(q)` after the same signed swaps and central translations.
The exact native checker reconstructs the lifted helper maps, main adapters
and all paid maps with their absolute phases.

The caller is PR6348 at `9894015d6f380206f990ad5fd14bc49bbd26b0d0`.
Its 19 native calls, 16 thin queries and 16 paired whole idles are unchanged.
The complete Laurent replay checks every input and output coefficient with
independent stage variables. The physical replay checks all 7,904 contacts,
all main output phases, all whole idle jobs and the factorwise native routes.

Each native occurrence receives its own 562 helper inputs. These inputs are
independent of the 34 main fields per port and of every other occurrence.
Thus there are `19*562 + 34*104 = 14214` productive fields. No helper input is
reused as a free query or idle field. The owned fields have no productive
credit. The local word has 29 owned labels, 32 lifetimes and peak 13.

## 2. Complete recursive invoice

Write `H_r = r^(1-kappa)`. The exact local changes from PR6167 are

```text
paid:       H1 + H2 + H3 + 2H4 - 4H5
productive: H6 + 3H8 - 4H9
```

Each change occurs 19 times in the retained tree. The complete changes from
PR6348 are therefore

```text
paid:       19H1 + 19H2 + 19H3 + 38H4 - 76H5
productive: 19H6 + 57H8 - 76H9.
```

The helper count stays 562 per native call. Paid local calls increase from
3449 to 3450. The full caller has 70,542 paid jobs and 14,214 productive jobs.
The paid and productive rank masses each decrease by 114. Their surplus stays
808. The main ranks, whole idle ranks and maximum target rank 153 are unchanged.

The verifier counts the emitted caller events and compares that count with
PR6348's separate tree formula. It also compares the complete signed changes
with the two displayed formulas. All extra native input transports are paid,
and all four helper target reductions are debited.

## 3. Strict price and outer transfer

The raw moment crossing is strictly inside
`(0.00314981300605, 0.00314981300606)`. These are adjacent points on the
grid `10^-14`. The complete receipt records the exact rational enclosure. A derivative bound makes
the crossing unique below the admitted BIT cap. A second rational moment
engine checks the strict inequality at the tested saving.

The claim is `kappa = 0.00314980`. The tested saving is `0.003149805`.
The retained completion uses power 1024, cutoff 12, floor 13, tail offset 1/7,
reserve `10^-12`, decay 31/32 and logarithm power 1100. The verifier checks all
completion and rounding inequalities, the uniform threshold and the adjacent
rejected threshold point. It checks the local native/scalar route allowance
and the complete ordinary-work allowance. It then checks all 54 strict outer
inequalities and four functional predicates with the retained admitted BIT
saving .0034.

The prior PR6348 complete bill fails at the new claim. Failure controls also
reject an unpaid carrier move, a missing productive target debit, missing
caller work, a wrong central orientation and invalid lifted input preparation.
`PRICING-EDITS.json` lists every change to the retained price verifier. The
code checks that this list produces the new price file exactly.

## 4. Scope and limits

The five inherited framework assumptions remain: `native_all_columns`,
`owned_erasure`, `compiler`, `precision_tape` and `analytic_recovery`. Finite
native and compiler checks do not discharge their full quantified statements.
The large uniform word and rounded multiplier are not materialized. Author
replay is not independent scientific acceptance or proof-kernel acceptance.

The gain over PR6348 is 0.00000047, approximately 0.0149 percent. It is a small
composition gain. It does not meet the donor's one-percent breakthrough target.
This package makes no global caller optimum or novelty claim for either source
construction. Other active native input-direction research is outside its scope.

## Open next questions

An independent reviewer can first check the unchanged main interface, helper
input separation and the complete signed deltas. A new source can use this
composition only after its complete arbitrary-input and native phase checks.
A larger caller gain needs a different exact interface and a complete price;
none follows from this composition.
