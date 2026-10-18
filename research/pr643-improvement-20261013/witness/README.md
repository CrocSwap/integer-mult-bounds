# PR643 twin-supplier owner packing improvement

This witness retains Jeremy Kothe's PR643 suppliers and changes the literal owner map: idle ranks 12+32 become 44. The exact admitted bound is κ = 1636569158555067/1000000000000000000 = **0.001636569158555067**, above pinned PR643's 0.001636542223442109. Dispatch remains 71 PR637 JP8 calls and one PR635 JP8 call (named jp8b); all 35,424 literal roles retain their window, family, width and disjoint-interval constraints. This does not claim an unrestricted optimum.

Pinned predecessor: `jeremykothe2/integer-mult-bounds` commit `bbfa9fe1d84d5572f4d144c2ee56a3eddc7a83f5`, package `research/complex-571-cold14-twin`. Every Python file in `code/` and `verify.py` is byte-identical to that source. Six pinned dependencies are vendored unchanged. Source preservation is recorded in SOURCE-COMPARISON.json.

## Reproduce

Use Python >=3.10 with assertions enabled, a C++ compiler and Boost headers for the frozen baseline. Python admission uses the standard library. Choose a new output directory:

```sh
PYTHON=python3 sh verify.sh /tmp/pr643-owner-replay
```

The wrapper rebuilds both suppliers and the baseline without reuse, then runs independent native-width/owner/rational checks and five mutations, declaration reconstruction, a portable owner exporter with four mutations, and six independent U4 mutations. Owner reproduction compares decompressed payloads. The full fresh candidate replay passed all 58 core stages without reuse in 327.44 seconds, followed by every supplemental wrapper check. All 46 receipt artifacts and 58 stage logs were independently hash-checked. The enclosing validation directory retains full replay archives, receipts and executed input snapshots. Execution was on macOS; no Linux replay or GitHub CI success is claimed. Prepublication exact assembly and 114 admission controls passed using actual supplier outputs from an independently completed fresh PR643 replay. That baseline source replay passed all 58 stages without reuse; it is distinct from the candidate's fresh replay.

`owner-search/README.md` documents the recorded export from pinned PR643 data. Solver output is nomination only. Inherited proof notes describe the unchanged supplier construction. Both orientations, arbitrary-dirt native scalar/frame behavior, exact phase edges and whole-provider identity bindings remain checked by the complete core replay.

## Attribution and scope

Chi Zhao prepared the owner repair, independent audit and portable package with substantial OpenAI Codex assistance. Jeremy Kothe (CarrierBypass) supplied PR643's twin dispatch and the PR635/637 suppliers, building on Jeremy Diviney's factored ends and earlier contributors retained in NOTICE.md. The separate interval checker retains Chafik Boukhalfa's PR626 exact interval engine.

This is a conditional native exact-complex witness, not formal verification of the multiplication theorem or a measured implementation speedup. All-size compiler, common-label/mutable-source realization, whole-call hosting, precision/tape recovery, analytic transfer and bit H1–H5 premises remain. The inherited PR543 bit supplier is repriced rather than rebuilt. Publication does not assert that this is the latest unreviewed frontier.
