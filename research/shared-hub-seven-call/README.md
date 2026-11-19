# Seven-call shared-hub obstruction

Seven nonzero calls, with one shared-hub type repeated, still require two triple blocks to give a
diagonal endpoint. The repeated calls cannot straddle a call from the
other triple. Exact totals give the same five target labels, and their
total rational rank cannot exceed the paid rank.

Read [PROOF.md](PROOF.md), [RESULT.json](RESULT.json),
[verify.py](verify.py), [SOURCE-PINS.json](SOURCE-PINS.json) and
[CREDITS.md](CREDITS.md). The proof handles both exceptional cases that
the degree-two check misses. The finite checker covers all four leading-form cases and all six choices
of repeated type. The theorem has no relation-rank limit.

Run from the repository root with Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/shared-hub-seven-call
```

Both registered modes print `PASS_SHARED_HUB_SEVEN_CALL`. The retained
six-call verifier runs unchanged. The general theorem is a written proof;
finite replay is not formal proof-kernel acceptance.

No new kappa, physical supplier or selected-frontier change follows.
All five framework assumptions remain. The selected cold replay, Lean
and Docker were not run.

## Open next questions

- Resolve two repeated types at eight calls without a relation limit. The
  visible-core and exact-cut arguments must then handle two extra calls.
  A complete caller cost remains necessary for any physical proposal.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
