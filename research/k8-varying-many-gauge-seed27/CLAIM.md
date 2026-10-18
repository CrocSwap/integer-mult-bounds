# Sprint claim — seed 27

- **Track and seed:** complex supplier; OS-random integer seed 27.
- **Exact base:** `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
- **Coordination:** the repository has no open sprint coordination issue (the two open issues are #913 and #650). The claim is recorded here; no separate reservation issue was opened.
- **Object:** one temporal dyadic gauge on L253 in the selected PR1094 k8 complex word, with the other 217 simultaneous constant gauges frozen to the open PR1263 certificate.
- **Seed diversification:** select the zero-based helper index `seed mod 218` from the sorted PR1263 forward gauge support. Index 27 is L253. This avoids PR1259's L276 and PR1214's L251/L427 pair.
- **Method:** exact integer sequence dynamic programming over all 96 L253-incident ADDs in each orientation; price every inserted transition scale and changed coefficient with the retained copy-init lowerer; replay the complete word on all 712 formal input columns.
- **Deliverable and finish:** source-pinned certificate, reproducible verifier, independent DP check and rejection controls; completed 2026-10-13 23:16 UTC, ahead of the 23:35 UTC estimate.

## Three narrow candidates inspected

1. **Chosen:** L253 temporal rescaling on top of PR1263's 218-helper constant-gauge word. The method changes the temporal class and tests one seed-selected coordinate; the best complete optimistic price is obtained by the exact all-integer DP before full packaging.
2. L276 temporal rescaling on that same word. This is close to Sagar Thakrar's open PR1259, whose target is L276, so it was not selected.
3. A two-coordinate temporal schedule on L253 and L254. It changes shared-ADD interactions, but needs a larger state space and a separate full invoice; it is deferred until the one-coordinate result is complete.

## Recent overlap check

Read the current status, selected certificate and review, central PR ledger, the two open repository issues, and recent relevant PRs/discussions. PR1263 covers simultaneous constant gauges, PR1259 covers one temporal helper on the original word, PR1214 covers at most two constant gauges, and PR1161 covers one constant helper. Discussion #1258 is the constant many-helper claim; current discussion #1328 concerns packing thresholds. PR1310 (head `b9ca10f02fca37c8214d880c244ac14ead6bae7a`) completes a distinct exact two-coordinate constant-gauge study and explicitly does not compose phase-varying gauges. No reviewed or recent claim matches the L253 temporal schedule over PR1263's frozen multi-gauge word.

## Result and handoff

The complete DP found an exact minimum of −91 real primitives in both orientations, or 182 complex primitives saved per orientation beyond PR1263's frozen 218-helper word. Full costs are 135,820 forward and 135,836 backward, with all 712 formal columns, the paid profile, source/frame events and local 192-bit charge checked. Selected κ is unchanged.

Submitted as [PR #1350](https://github.com/CrocSwap/integer-mult-bounds/pull/1350). The registered package replay passed on CPython 3.12.15; optimized direct replay and seven controls also passed on CPython 3.14.7. Native/hosting admission, global multi-coordinate search and a new κ remain open.
