# P104: 233-CLEAR conditional composition

This research combines the frame-restored H5B construction with the E1/E4 changes from the cited follow-up work. Under the conditions in CONDITIONS.md, the directed interval result supports **κ ≥ 0.0037**. This is not a selected-frontier update or unconditional multiplier theorem.

The final word contains 78,596 events, 233 nonzero CLEARs, peak live stock 50 and 52 used labels. All 68 reserved labels and 1,156 signed banks remain charged. The canonical JSON SHA-256 is `8ab3d9dbe2e2e24202ac96c6122b010b3e7980912f935cc0cc2db2e9d85f83aa`. The changed entrance `initial[457]: 3 -> 281` is explicit.

## Layout and reproduction

Scientific Python sources remain visible under src/. Large immutable inputs and retained evidence are deduplicated by hash inside data/inputs.tar.gz; DATA-MANIFEST.json maps each original path to its exact bytes and SHA-256. It is a data pack, not a new scientific verifier. Operational sample logs and duplicate copies are not included. LICENSE and NOTICE retain attribution.

The pre-existing #7334 closure archive is deliberately not vendored again. Download the exact public file from:
https://raw.githubusercontent.com/rohanarun/integer-mult-bounds/58a9d052143f5d85295ed2d0163591c47f89a331/research/p104-helper-449-fused-return/inputs/pr7334.tar.gz

Expected SHA-256: `721f839cc48605cccd3629d11456e1fcbb3810a624803ad27e99a1bfd6246211`; Git blob `e69e784c1edeeffe330a78c579aed210cd8815ff`. This introduces a network/source-availability dependency, or use an existing local copy with the same hash.

With Python 3.12, from the repository root:

```sh
python3.12 -I -B research/final233-portable-conditional/replay.py integrity
python3.12 -I -B research/final233-portable-conditional/replay.py materialize --upstream-archive /path/to/pr7334.tar.gz --work /path/to/new-work
python3.12 -I -B research/final233-portable-conditional/replay.py reconstruct --upstream-archive /path/to/pr7334.tar.gz --work /path/to/another-new-work
```

Integrity without the external archive explicitly reports EXTERNAL_NOT_CHECKED. The work directory must be new. The original native, signed and optional scalar execution routes are exposed as `native`, `signed`, and `optional-scalar` modes with the same arguments. A timeout does not prove a mathematical failure. Use an appropriate process-tree resource supervisor. Do not use Python -O/-OO.

## Evidence and limits

See VALIDATION.md. Earlier candidate-adapted native and signed results are author evidence, not new executions of this repackaging. Signed coverage comprised 3,060 maps, with 2,000 guarded cached results and 1,060 newly executed. The independently authored finite audit checked 233 recoverability identities and 932 targeted mutation predicates. It is not a physical reset proof.

The inherited five framework assumptions remain, together with the stated common-U supplier and its entrance, extent, reset, residual and cost obligations. An implementation satisfying those obligations has not been established. Different researchers may use their own verifiers; the candidate hash binds this candidate, not a project-wide acceptance gate.

## Credit and next work

Credit Ali Romman/#7605, SYLforge/H5B, DreamingOfClouds/#7630, Clear1nsight/#7631/#7633 and #7626, Rohan Arun and all retained upstream contributors. Substantial OpenAI assistance was used. Further review should first test the changed entrance and a concrete supplier's whole-extent/reset/tariff contract as described in CONDITIONS.md; the blocker is the absence of an admitted supplier.

## Open next questions

1. Can a concrete common-U supplier satisfy the changed entrance and all 233 lifetime histories? First inspect the whole-private-extent, nonaliasing return and reset obligations in CONDITIONS.md. Blocker: no admitted supplier has been established.
2. Can the scalar service handle the reachable residual domain at the retained tariff? First audit events 45330/45331 and the ADD return-domain comparison. Blocker: actual implementation error, cost and space bounds are missing.
3. Can an independent reviewer replay the combined word and signed application? First materialize the pinned inputs and run the reconstruction route, then review the candidate-specific adapters. Blocker: independent scientific replay has not been completed.
