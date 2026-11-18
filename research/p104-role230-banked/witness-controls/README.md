# Exact saved-witness controls

These two optional checks distinguish equality of the exposed operator from correctness of the internal pivot witness and its scheduled reads. ChatGPT Pro proposed both mutations. Clear1nsight's role-transfer review reproduced them with substantial OpenAI Codex assistance. The public adapter preserves that exact algebra, using Ali Romman's fixed fifteen-pivot source and the released banked graph builder. [Fixed pivot witnesses](../peer/PIVOTS.json) · [Whole exact wire result](../evidence/WIRE-RESULT.json)

| Mutation | What the checker verifies |
|---|---|
| Flip the sign of internal token 97185 and invert all three readers in the first transposed pivot's entry circuit | Conjugating the scalar incidences by those signs preserves every public normalized endpoint and all 6,155 paid slots and their order. On public input column 17 the internal value goes from `2` to `−2`. The original pivot witness has residual `0` on the original circuit and residual `−8` after the mutation. The retained source verifier rejects the stale saved-signal identity. |
| Omit the coefficient `−1/3` of chart-912 token 97471 from the source form at slot 101174 | The resulting graph still schedules all 7,643 forms and retains the same 6,142 paid slots and routes. On independent helper column 39 the exact exposed value at slot 101174 changes from `0` to `1/12`. |

From the package directory, replay with Linux CPython 3.12 and the standard library.

```sh
python3.12 -I -B witness-controls/check_saved_witness_controls.py \
  --out /path/to/new-saved-witness-receipt.json
```

The adapter rebuilds the exact candidate graph in temporary storage, or consumes a retained wire output through `--candidate /path/to/CANDIDATE-GRAPH.json.gz`. It binds the fixed pivots, exact graph driver, canonical and packed candidate and actual wire receipt. The result must equal [EXPECTED.json](EXPECTED.json) and emits `PASS_SAVED_WITNESS_CONTROLS`. The inner wall limit is 75 seconds and the address-space limit is 2 GiB. The original guarded controls took 5.33 seconds wall on their already materialized inputs. This optional check has its own receipt and leaves the two registered commands and their budget intact.
