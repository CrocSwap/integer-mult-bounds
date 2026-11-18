# Independent chart-595 factor-seven audit

The fixed PR #7697 graph needs scale 45158400 for its literal products and
161280 for its complete stored rows. This audit confirms those reported
values without importing the source verifier. All 630 products that need a
factor of 49 occur in only two independent input columns, the split owners
281 and 1501. The first old-owner witness is `(-2/7)*(-40/21) = 80/147`.

Read [the proof](PROOF.md), [the receipt](RESULT.json),
[the checker](verify.py) and [source credit](CREDITS.md).

With CPython 3.12 and its standard library, from the repository root:

```sh
python3.12 -I -W error -B research/chart595-factor-seven-audit/verify.py
python3.12 -B scripts/research_package.py --package research/chart595-factor-seven-audit
```

Expected: `PASS_CHART595_FACTOR_SEVEN_AUDIT`, then
`PASS_REGISTERED_RESEARCH_PACKAGE` for the registered command.

The complete 8738317-product replay, separate rational basis witnesses and
six under-grid controls check the normalized scalar contract. This is an
independent numerical audit, not complete supplier admission. No new kappa
or selected-assumption discharge is claimed. Full candidate and selected
replays, physical Clifford/root checks, Lean and Docker were not run.

## Open next questions

Check a row-atomic integer accumulator at the stored-row scale, with all
numerator widths and physical costs included. This changes the operation
contract and is not established by the present audit.
