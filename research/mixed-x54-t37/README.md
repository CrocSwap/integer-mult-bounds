# Mixed joint entrances, source-holder fusions and X54 on 37 replicas

This candidate applies PR1195's two source-holder fusions and PR1130/1196's X54 operation to **125 calls of the joint-entrance D3 word and 208 calls of its four-group D4 variant**. Its conditional target is **κ = 0.001675809683500501**. It composes PR1193's exact allocation with Marius-Paul Dumitrean's PR1195 local improvement. It is slightly above PR1207's concurrent 0.001675807682652000 nomination because its idle rank-one count is two rather than eighteen. These are conditional finite construction prices, not an unconditional multiplication theorem or runtime measurements.

The added contribution is the fully checked composition of the two fusions with PR1193's mixed dispatch and whole-helper realization. The predecessors remain available in `research/mixed-demotions-t37/` and `research/mixed-fusions-t37/`. Changing four more entrance frames increases local recursive cost but reduces the unused rank-one capacity. A mixture balances those costs more effectively than using either word uniformly. The 333 calls have 159,840 whole helpers; the remaining idle profile is `{1:2,48:11374}`. See [PROOF.md](PROOF.md) for the accounting and [NOTICE.md](NOTICE.md) for predecessors.

The complete local replay passed on the source commit identified in [the evidence record](evidence/REPLAY-SOURCE.json). The [result](evidence/RESULT.json), [two-engine price](evidence/PRICE.json), and [strict assembly](evidence/t37/strict/ASSEMBLY.json) retain exact inputs, charges and controls. The complete repository `make verify` suite also passed; its [receipt](evidence/MAKE-VERIFY-RESULT.json) and compressed log are retained. `CLAIM.json` preserves the original frozen target specification; admission is recorded separately in `evidence/RESULT.json`. Hosted checks and maintainer acceptance are separate.

## Reproduce

Use Python 3.11+, the repository's cold-replay dependencies (including a C++ compiler, Boost headers, NumPy/SciPy/SymPy ), and a new output directory outside the checkout:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 nice -n 15 \
  python -B research/mixed-x54-t37/verify.py --work /tmp/mixed-t37-fresh
```

If Boost is not on the compiler's normal include path, set `CPLUS_INCLUDE_PATH` to its header directory. Verification does not use OR-Tools, an allocation optimizer, a network connection, or discovery-mode admission. The frozen integer flow is expanded by deterministic perfect matchings; every integer equation is checked.

A completed cold PR799 replay can be reused with `--ancestry799 /path/to/completed/replay`. The retained maintainer checker rechecks its source, artifacts, logs and PR589/741/799 bindings; an independent fixed coverage check rejects omitted stages. This option still rebuilds both new local providers and every new global stage.

The driver checks both exact scalar maps and all 704 columns in both orientations, all native phase edges, eight X54 semantic mutations and all eight coded-cell leaver premises per provider, 20 source-holder fusion mutations across both providers, local entrance mutations, the full helper map against literal bridge-aware windows, provider substitutions, the emitted controller and its 23 mutations, the complete invoice, 114 admission mutations, 12 bit-supplier mutations, two rational moment engines, and 47 strict outer inequalities. It also checks eight parent controls, eight frozen-flow controls, and eight independent owner controls. Successful completion writes `RESULT.json` with status `PASS_MIXED_X54_FUSIONS_T37_COMPLETE_ADMISSION`.

Immutable upstream archives retain byte pins. Fresh compressed outputs are compared by their complete decompressed content or documented semantic identity; only validated phase timing and compression references are rebound. The committed `SPEC.json` remains frozen throughout verification.

The all-size compiler, common-label/mutable-source realization, whole-call hosting, precision/tape and exact recovery, analytic transfer, PR559 recurrence correction and bit H1–H5 obligations remain. This package changes the local-word family; it makes no optimality claim for mixed words or other circuits. No selected certificate is changed by this research submission.
