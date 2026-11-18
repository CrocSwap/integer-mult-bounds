# Exact basis audit of the 46 relay recodings

All 46 fixed cuts in [PR #7708](https://github.com/CrocSwap/integer-mult-bounds/pull/7708)
preserve the stated bank values and all 1501 public outputs. This closes
the requested scalar receiver review at cut 38 and cuts 40–42.
The [proof](PROOF.md) explains the division by five, the chart-778
reroute, and the complete signed paid delta. The [receipt](RESULT.json)
contains exact input coefficients for every transmitted signal.

The check covers 350961 bank/output values and 468916850 coefficient
products. It uses a separate exact basis evaluator, the pinned source
constructor, and the existing signed caller engine. The caller has
101488 paid jobs and 21152 productive jobs. Its 352-job reduction has
no target debit and no change in rank mass. No new kappa is claimed.

Use CPython 3.12 and its standard library from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/relay-recoding-basis-audit
```

Both registered commands print:

```text
PASS_ALL_RECODING_BANK_BASES 46 350961
```

Each command has a 120-second limit. Normal and optimized Python use
the same explicit checks. [Source pins](SOURCE-PINS.json) authenticate
the 23 retained files. [Credit](CREDITS.md) states which methods and
engines are reused. This is author checking after source inspection,
not blind, independent human or formal-kernel review.

The original word, CLEAR certificates and role-1256 constructor remain
inherited dependencies. This audit does not repeat the complete native
phase catalogue, physical storage, root precision or compiler proof.
The five selected-framework interfaces remain assumptions. The selected
cold replay, Lean and Docker were not run.

## Open next questions

Can an independent reviewer verify the physical and uniform implications
of the same fixed graph? Start from the source's charged schedule,
native phase catalogue and root precision proof. This scalar audit does
not supply those implications. New graph searches require a separate
overlap check. No follow-up is reserved.
