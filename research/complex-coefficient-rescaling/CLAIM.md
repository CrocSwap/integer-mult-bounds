# Sprint claim

- Track: complex supplier; OS assignment seed **39**, drawn with `secrets.randbelow(100)` on 2026-10-13. Odd parity selects JP8.
- Exact base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Scope: selected #626 JP8 full-frame cleanup; consecutive same-source additions with **distinct coefficient magnitudes related by powers of two**. Keep target-update order and use the existing private coefficient work stream. Price source access, initialization, rescaling, accumulation and final clearing before implementing a witness.
- Method: exhaustive scan of this fixed finite word in both orientations; choose disjoint profitable blocks, exact rational arbitrary-input replay and prefix bounds. No randomized search, time-limited search, or kappa claim.
- Expected deliverable: executable finite circuit witness and scoped proof, or a complete negative census if the optimistic budget gives no gain.
- Expected finish: 2026-10-13 05:37 UTC. Reserve 05:27 onward for verification and handoff.
- Coordination: GitHub reported no pinned issues and only open issue #650 (Discussions request). Local claim recorded instead of a reservation issue. Open PR snapshot: 551 PRs through #732.

## Candidates considered

1. Joint target-basis rewrite of the selected cleanup; related bit work #710 and CK pair obstruction #719 mean a broader resynthesis obligation.
2. Source-basis rewrite of the selected factory; substantial overlap with #645/#681, so not selected.
3. Distinct-coefficient private-work rescaling in JP8 cleanup, selected. #722 shares equal coefficients and #723 changes individual numerator encodings. This instead connects differing magnitudes across macros, with a complete incremental cost comparison against equal-coefficient sharing.

## Related pending work inspected

- #696, `5a3f983715027c4fd83f50bc9001d4b18463bed1`: copy/unit scalar lowerings.
- #722, `a0766ab0fab379e1997fadc3ca157578d57986c1`: equal-coefficient JP8 cleanup sharing.
- #723, `d3bc41b87fc7d23f50d064a0f06f1a89e3ab02a7`: signed-digit numerator lowering.
- #719, `a3d9c0aa0a16b68b1f4dd064671ad018013e6dd4`: CK repeated-pair rank obstruction.
- #698, `ab78f797cffcbeddbb17a7eb069741085ffe3351`: fixed-boundary CK B-frame optimization.
- #681, `fdc2e4f3c6825530b02143b30deab5de10209479`: raw factory resynthesis.

No pending implementation is imported. The selected construction and review were followed through #626's retained supplier, local event stream, emitter and source manifest. The review ledger marks #626 and #622 incorporated, while the newer PRs above remain pending.

## Completed result — 2026-10-13

Submitted [PR #739](https://github.com/CrocSwap/integer-mult-bounds/pull/739),
**research construction / finite complex-supplier circuit improvement; no new
κ**. Initial contribution commit: `db5271d831d506ecf446609dc431e02bc3da8e0e`.

The complete fixed-word scan found 1,211 profitable distinct-magnitude edges.
Combined with the explicitly credited equal-magnitude method, 1,015 blocks
reduce forward real-component primitives from 257,232 to 227,206. The new
increment beyond #722's 237,544 is **10,338**. Backward is unchanged. Both
716-column scalar projections, all 6,279 independent block basis cases, exact
prefix envelopes, negative controls and nine focused tests pass. The selected
κ and paid recursive profiles are unchanged. Production block-interface
admission and invoice integration remain open.

The final pre-submission snapshot covered 556 open PRs through #737, including
new #734 at `21606831df4b08f79d87fd420c558a520dca571e`, whose per-macro
signed-Horner work is credited separately. #738 arrived during submission;
its Gaussian copy-floor theorem is unrelated to coefficient-work rescaling.
There was still no pinned coordination issue. The one delegated reviewer
stayed within this package, supplied the independent checker and found no
correctness blocker. One wording correction from that review distinguishes
endpoint-neutral extra instructions from equal-cost instructions.

Reproduce: `python3 -I -B research/complex-coefficient-rescaling/verify.py`.
Expected: `PASS_JP8_COEFFICIENT_RESCALING incremental_real_saved=10338 blocks=1015 columns=716 orientations=2 controls=11`.
