# Sixteen-replica packing of the eight-endpoint k8 word

The frozen conditional value is **κ = 0.001674622497877364**, a **0.072195%** increase over 0.001673414377866467. The local circuit is unchanged from `../k8-eight-ends`; the change is a sixteen-replica owner map obtained by optimizing larger groups of complete calls.

The new search combines knapsack pricing of capacity patterns with an integer assignment of those patterns to actual owners. It releases all 480 helpers in each selected call, including the previously fixed width-five and width-seven helpers. Coordinating 48 calls at a time reached a substantially better packing than the tested smaller neighborhoods. Optimizer output is used only to nominate frozen data. The byte-identical upstream admission engines check every actual time window, whole-helper interval, chart, occupancy, prefix invoice, and exact arithmetic condition.

The final idle profile is `{1:2088, 24:1, 48:4918}`. There are 144 complete calls, 69,120 hosted helpers, and 14,336 live wires. The rank mass is 1,041,408 and the deficit is 5,120.

An independent exact signed-dual certificate bounds the same fixed word and packing inventory at every positive integer replica count. Its 18-decimal-grid upper bound is **0.001674630216885732**. Less than **0.000461%** further improvement remains in that family. A materially larger gain requires changing the circuit, helper model, or recursion geometry. The bound does not rule out those changes.

This remains a conditional finite witness, with the inherited compiler, analytic-transfer, common-label, mutable-source, whole-call hosting, precision/tape, and bit-supplier assumptions. It is not an unconditional integer-multiplication theorem. See `CLAIM.json`, `PROOF.md`, and `NOTICE.md`.

## Reproduce

Use Python 3.11+ and the native backend's C++ compiler and Boost dependencies. No optimization solver is used during verification. `BASE` is the raw R480 k8 + seven-slot word identified in `../k8-eight-ends/RECIPE.json`.

```sh
python -B research/k8-eight-ends-t16/verify.py \
  --base "$BASE" \
  --work /tmp/k8-eight-ends-t16-fresh
```

The output directory must be new and outside the repository. Set `CPLUS_INCLUDE_PATH` to the Boost include directory if necessary. The default run rebuilds the endpoint word and reruns all five native stages, the exact local audit, 32 endpoint controls, the unchanged T16 strict verifier, and the independent all-replica bound. To reuse a completed native replay of the same word, add `--native-from /path/to/completed/native`; its receipts, word content, and all proof-relevant semantic artifact identities are checked.

The package pins the consumed PR1074 controller sources by SHA-256 and Git blob identity. `SOURCE-PINS.json` pins repository dependencies; `MANIFEST.json` pins this package. The frozen plan is decompressed verbatim, and the T16 verifier independently reconstructs it from actual source-event windows. No discovery mode or solver runs in admission.

## Research record

`SEARCH.json` and compressed traces document the successful search chain, the smaller-neighborhood runs, and interrupted exploratory runs. `discovery/make_start.py` reconstructs the doubled T8 starting assignment. The search scripts require NumPy/SciPy; solver choices can vary across versions. The frozen witness does not depend on reproducing those choices.

The same run screened 76 scalar aliases with fixed ordering, 430 adjacent commuting windows, 20 entrance-promotion groups, and several stage-private bank relaxations. Those tests did not produce a structural improvement. Their scope and numerical limitations are recorded in `SEARCH.json`; they are not general impossibility results. The separate all-replica certificate uses two exact rational arithmetic engines and checks all 1,163 capacity patterns.
