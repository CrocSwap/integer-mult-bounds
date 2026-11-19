# Independent audit of the final bank cuts

The two final cuts in PR #7776 preserve all 1,264 rational output rows and
commute. They remove two paid positions. Each changes paid ranks `{2,3}` to
`{5}`. The complete multiplication exponent does not change in this audit.

Use Python 3.12 and its standard library:

```sh
python3.12 -B scripts/research_package.py --package research/p104-final-bank-cuts
```

Both modes print `PASS_P104_FINAL_BANK_CUTS 1264 owners 4 operators 2 cuts`
and elapsed seconds. The checks run in normal and optimized modes. Read
[the proof](PROOF.md), [certificate](RESULT.json), [source pins](SOURCE-PINS.json)
and [credits](CREDITS.md). `TASK.json` records the open next question.

No physical or full caller replay is included. All five assumptions remain.

## Open next questions

Can a changed bank interface improve the complete supplier? A new construction
must include the public operator, physical word, caller and ordinary-service bill.
