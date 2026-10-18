# Independent checks

Prepared for icekylinx with OpenAI GPT-6 Astra assistance. Apache-2.0, under the
package license. The scalar/frame audit imports no generator or supplier
checker. Pricing uses the pinned inherited rational engines and the retained
PR635 outer formula, with their original notices preserved in the main
dependency tree.

From the delta package directory, using the pinned checkouts and a rebuilt
word:

```sh
python independent/audit_local.py \
  --word /path/to/rebuild/cold44/FULL-WORD.json.gz \
  --main /path/to/main \
  --output /path/to/output/LOCAL-AUDIT.json

python independent/price_profile.py \
  --main /path/to/main \
  --output /path/to/output/PRICE.json

python independent/review_guards.py \
  --pr635 /path/to/pr635 \
  --output /path/to/output/GUARD-REVIEW.json
```

`audit_local.py` can run without `--main`; including it also verifies the
transported centre-frame and port boundary against the pinned parent. Its
receipt authenticates the supplied word by its content SHA256, independent
of its location. `price_profile.py` defaults to the package's `data/PLAN.json`;
`--profile` accepts another explicit profile for arithmetic only. The bit side is the cited merged PR589 supplier
(`inputs/PR589-EXPECTED.json`, git blob `e293ddc5…`); its rank-mass deficit
`T(2Kv - L*cst) = 32*(8*111 - 9*63) = 10272` is re-derived independently of
`code/assemble.py`, and the outer receipt key is `outer_with_bit`. The retained
`GAUGE44-INDEPENDENT-PRICE.json` is #645/PR543 historical evidence unless regenerated. The optional
`--headroom-c 0.001733052823330162099157` reproduces the unchanged-kappa
comparison with the reviewed PR555 rate without importing a second supplier.

The retained receipts are `GAUGE-COLD44-INDEPENDENT-AUDIT.json`,
`GAUGE44-INDEPENDENT-PRICE.json`, and `GAUGE44-GLOBAL-GUARD-REVIEW.json`.
[CENTRE-GUARD-REVIEW.md](CENTRE-GUARD-REVIEW.md) gives the semantic argument
behind the changed centre boundary and the single-provider control branch.
The main package driver performs the separate complete global admission.
