# Exact circuit for the mixed and endpoint denominator-52 tails

One reversible circuit now covers the 288 mixed and 96 endpoint source
tails that cannot enter the nonzero-pair core. It uses 1,277 gates and
382 clean work bits per draw. The ordered output labels, continuing-node
indices, stopping depths, parameters and coin are preserved.

Read the [proof and complete contract](PROOF.md), [circuit](tail.py),
[exact bill and all source recipes](RESULT.json), [checker](verify.py)
and [credits](CREDITS.md). This is a tail circuit, not a complete physical
sampler or a new kappa result.

Use Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/nonunit52-tail-circuit
```

Both registered commands print `PASS_NONUNIT52_TAIL_CIRCUIT`. All 20,736
runtime transitions and 16,128 actual source-tail edges pass. The complete
fixed-pair primitive source verifier also runs unchanged. Exported replay
needs no Git or repository imports.

## Open next questions

- Can the four-coin prefix and its return boundary be implemented with
  a complete physical bill for an actual inverse call? The tail inverse
  does not implement the first-entry return.
- Can parameter preparation, conditional freshness, output retention and
  unbounded stopping storage fit that caller's paid allowance? An expected
  coin count or a local gate count does not establish that allowance.
