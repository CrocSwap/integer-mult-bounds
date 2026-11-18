# Independent exact reviewer

This optional standalone comparator reads two frozen literal words and their full 17-call invoices; no constructor, builder origin map, or sibling checkout is imported. It uses the previously independently authored rational interpreter `exact.py` from the #7645 independent reviewer and a new comparison driver. `PLAN.md` is the prospective plan written before inspecting construction logic; `RESULT.json` is the original successful run. The prior work includes DreamingOfClouds #7617 and SYLforge #7616, and the credited predecessor chain remains applicable.

Supply the exact frozen inputs as explicit paths. Both word raw SHA-256 hashes and invoice file hashes are pinned in the checker. The compressed bytes may be repacked; their hashes are included as receipt metadata. Use Python 3 with Linux affinity/resource support and a new output path:

```sh
python3 -I -B independent/check.py \
  --base PATH/TO/7645-WORD.json.gz \
  --candidate PATH/TO/COURIER-WORD.json.gz \
  --base-invoice PATH/TO/7645-INVOICE.json \
  --candidate-invoice PATH/TO/COURIER-INVOICE.json \
  --output PATH/TO/NEW-RESULT.json
```

The checker selects one allowed CPU, sets 2 GiB address-space, 570 seconds CPU and 600 seconds wall alarm, and fails if the output already exists. It checks literal ordered protected events, their roles and live chart, and every before/after rational row, including all 1,501 arbitrary public input columns; all 74 ordered erasures and all 1,501 final public rows are compared. The actual sign of a candidate-specific public ADD is flipped and the same replay must reject it. The output records the changed event and first error.

The fixed full 17-call baseline invoice is decomposed into its 17 native word charges plus a residual. Candidate word charges are added back and the resulting paid and target histograms must equal the pinned candidate invoice. This does not independently establish that inherited residual, the price crossing, physical provider availability or native/signed execution. Owned INIT is ideal zero and depends on the inherited reset contract. The logical replay does not discharge common-U, physical covariance, precision, allocation, or goal admission. This reviewer shares the published word format and prior #7645 independent interpreter; it is independent of the new builder and origin alignment, not of those shared assumptions.

The predecessor and candidate inputs used for the original comparison have raw hashes `6c52b2fba7c20343a50cb92ed4b997aa9921c78f212ac6428d13fff2bcd014cf` and `450c7e544efb5258c4b8b4858b49cbd7482d14f206cdda1a71833fc73343ac66`. Invoice hashes are `7d54c1ec036d4c096526dd95e06892ca99210812d51a503b22f6d78243330ca9` and `fa0c37a9e67d0a82850c4fcfd5cbdb3bd88e1f8db329176e5669da6c7788f6a2`. The original run started 2026-11-17T23:48:51Z and took 63.92 seconds. An initial invocation failed before scientific execution because Python isolated mode omitted the module path; the portable driver inserts its own directory explicitly.

To compare a new result with the original receipt while allowing different timestamps, elapsed time, and gzip repacking, run `python3 independent/compare_results.py independent/RESULT.json PATH/TO/NEW-RESULT.json`. The checked stable fields include both raw word hashes, the complete test counts and invoice deltas, the mutation witness, and the scope statement. When using the package's generated fresh workspace, its input names are `baseline.json.gz`, `candidate.json.gz`, `baseline-invoice.json`, and `candidate-invoice.json`.

A separate-directory replay completed on 2026-11-18 at 00:07:36 UTC in 66.31 seconds. `RELOCATED-RESULT.json` preserves that receipt, and `STABLE-COMPARISON.txt` records equality of all 20 stable fields against the original. The relocated receipt SHA-256 is `1d6a1c86cacf43c382450139e522ad65d9d4723c25e25e268d9239dabf2c8dfc`. Recompression metadata and timing are intentionally excluded from stable comparison; raw word hashes remain included.
