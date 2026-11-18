# Row-atomic arithmetic for the fixed chart-595 graph

Accumulate an integer common numerator, then divide once per completed row.
This evaluates the same normalized graph at stored scale 161280, instead
of the 45158400 needed for separately divided literal products. The full
basis trace agrees at all 7644 rows. The new arithmetic representation
needs W+20-bit temporaries for W-bit donors; a W+19 control fails on an
actual source row with exact division.

Read [the proof](PROOF.md), [receipt](RESULT.json), [kernel](kernel.py),
[checker](verify.py) and [credit](CREDITS.md).

With CPython 3.12 and its standard library, from the repository root:

```sh
python3.12 -I -W error -B research/chart595-row-atomic-arithmetic/verify.py
python3.12 -B scripts/research_package.py --package research/chart595-row-atomic-arithmetic
```

Expected: `PASS_CHART595_ROW_ATOMIC_ARITHMETIC`, then
`PASS_REGISTERED_RESEARCH_PACKAGE` for the registered command.

The kernel uses shifts, additions and binary exact division. Two full scalar
runs agree with a separate Fraction oracle. All rows have boundary checks;
large words and five rejection controls also pass. The construction is
normalized scalar arithmetic. It does not install a physical provider or
change kappa. Full candidate/selected replays, physical root/tape checks,
Lean and Docker were not run. All five selected assumptions remain.

## Open next questions

Supply the complete guarded-stream, root, movement and cleanup substitution
before claiming a lower physical allocation or ordinary bill.
