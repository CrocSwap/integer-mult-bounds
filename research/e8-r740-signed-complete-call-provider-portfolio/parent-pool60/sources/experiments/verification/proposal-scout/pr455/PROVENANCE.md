# Frozen provenance and attribution

Upstream copyright/license notices and attribution are retained in source files and `notices/`,
with one contributor's own handle omitted from an aggregate historical acknowledgement at their privacy request.
New construction, independent audits and packaging were developed with OpenAI assistance.
No contributor identity is inferred from the machine or supplied as submission metadata.

| PR | Frozen head | Contribution |
|---|---|---|
| [451](https://github.com/CrocSwap/integer-mult-bounds/pull/451) | f3a38153678b55063fc005901cc968266166507d | rank149 whole-residual baseline, complex fractional-depth rows, trace objection |
| [450](https://github.com/CrocSwap/integer-mult-bounds/pull/450) | 6faca41020a620689de013cdab9f61a22deca314 | target-label mixing and executable stage interfaces; split hosting excluded |
| [453](https://github.com/CrocSwap/integer-mult-bounds/pull/453) | cff79050526545e7b66d24a7f4c65f22c1da8618 | vendored source collection and local-word comparison; higher split-based claim excluded |
| [447](https://github.com/CrocSwap/integer-mult-bounds/pull/447) | d3cf3079091bb7e93a23e9cd98e82ccb89697328 | eleven-stage kernel/schedule lineage |
| [445](https://github.com/CrocSwap/integer-mult-bounds/pull/445) | 40ab91daf2b5e87fc4071dedae1699d5d7e7cecc | eleven-stage interfaces |
| [433](https://github.com/CrocSwap/integer-mult-bounds/pull/433) | 6d9244518175caf9e0089f92486959bc2c317273 | split-centre complex program and source-basis reuse |
| [425](https://github.com/CrocSwap/integer-mult-bounds/pull/425) | e11ccea1d092beb1b01b4ee4ce49da478234254c | mutable-basis lineage |
| [448](https://github.com/CrocSwap/integer-mult-bounds/pull/448) | 9b966d8188e1cadd00aa834078ee6a8742a9d9b4 | compared and rejected cross-family splitting |
| [449](https://github.com/CrocSwap/integer-mult-bounds/pull/449) | 7fac5292693bf738ff5eed6ec754f8ec22ebcf8e | reviewed source snapshot |
| [452](https://github.com/CrocSwap/integer-mult-bounds/pull/452) | 8a8079ec31abac7ccc4a0eae89df83b309fafbe1 | reviewed prototype, not used |

Additional direct lineage retained in the vendored sources: PR442 whole idle-data hosting;
PR443/439/417 response kernels and residual isometries; PR386/370 Hamming/E8 geometry and
producer/controller; PR401/404 shared-donor and partial-prefix recovery. The rational moment
and 47-constraint engines retain the PR315 assembly lineage and their embedded notices.
These credits identify actual construction inputs or direct inspirations, not endorsements
of every claim in those PRs.

`SOURCE-FILES.json` records initial copied-source hashes, before local adaptation; it is
historical provenance, not a final integrity manifest. `MANIFEST.json` is authoritative for
final bytes. `REPLAY-MANIFEST.json` freezes the actually executed source/input set.
Changes after initial staging include final whole-owner registry/controller checks,
conservative prefix accounting, provider CLI argument order, relative engine lookup in
`vendor/runtime/e8core.py`, and inclusion of `pricing/prime_witnesses.py`, `tile_m.py`, and
`bank_routes.py`. All mathematical changes precede the successful portable replay.

Paths in agent notes are translated as follows: construct149.py -> code/providers.py;
audit149.py -> code/provider_audit.py; selection149-portfolio.json -> inputs/providers.json;
complex-pooled-selection.json -> inputs/complex-selection.json. The archived rank137
PROOF.md mentioned by PROOF149 is withdrawn history; the final sufficient theorem is
PROOF.md in this directory. Use `verify.py`, not the historical standalone prefix CLI,
which remains pinned to its earlier comparison input. Its reusable construct function is
called with the current pinned input by the wrapper. Historical metadata and JSON field
`gain_over_pr442_percent` remain for compatibility; `reference_label=PR451` and
`gain_over_reference_percent` identify the actual comparison.

The final portable witness is inputs/bit-selection.json, including its five explicit variant_calls; the earlier solver nomination lacked that dispatch metadata and is not shipped.
