# Pinned p10 weighted reuse and shared-donor evidence

This additive experiment starts from PR320, immutable head `e983fea0896b2a1d7355983674db7e9bb33a9e32`, package `research/five-stage-p10-transcript-stages/`. It has p=10, h=20, completed-bank width 100, 60 replicas and 5 stages. A main checkout is not assumed to contain these upstream inputs.

The proposed composition replaces 71 of the 890 stored reuse pairs and adds 73, giving 892 pairs. It then adds 19 rank-one prefix relations on 41 previously unused physical helpers, charging 22 distinct donor activations and 58 setup/restoration pairs. All original 775 installed kernel entries remain. The matching change and 19 rank-one relations are priced jointly; their residual width decrease of 25 is divisible by 5 and permits full width-100 packing. The 19-relation closure without the matching change is not independently bank-admissible.

Conditional numerical comparison:

- Pinned PR320: κ=0.000769198971896986.
- Fixed 15 closure on the unchanged 890 matching: κ=0.000769208711124428.
- Proposed weighted 892+19: κ=0.000769661484777339, stock 658905, banked calls 249085, rank mass 1096135.

The latter is a 0.060129% improvement over this pinned baseline. It is not an optimality or current-best claim. All displayed exponents use the retained supplier, finite-compiler, prime and all-size interfaces described below.

Publication-time note (2026-10-10, 17:38 UTC): PR320 had advanced at 17:30:25 UTC to [head `1b37957d1520c80b6ea796bf418e52be5109c2d4`](https://github.com/chafreaky/integer-mult-bounds/tree/1b37957d1520c80b6ea796bf418e52be5109c2d4/research/five-stage-p10-transcript-stages), advertising κ=0.000769553898621543. That newer result was not independently reproduced here. Every check and comparison in this addon remains bound to the earlier `e983fea…` input manifest.

## Reproduction

Use Python 3.10+ without `-O`. The checkers use only the standard library. Upstream Python is downloaded with `.py.txt` suffixes and read as inert text; none is imported or executed.

From any working directory, use absolute paths:

```
python /path/to/research/gen5b-shared-kernels/p10/acquire_inputs.py --dest /tmp/p10-inputs
P10_INPUTS=/tmp/p10-inputs P10_OUTPUT=/tmp/p10-output python /path/to/research/gen5b-shared-kernels/p10/run_checks.py --check --tests
```

The downloader pins 40 necessary input blobs by immutable URL, byte length, Git blob ID and SHA256. Existing cache entries are verified, not silently trusted. No auxiliary manifest is expected inside the downloaded directory. The two reused exact-arithmetic modules in the parent package are guarded by immutable SHA256 pins.

Large derived objects are regenerated in `P10_OUTPUT`: full alias/path receipts, exact rational factor programs, the complete role/replica bank table and scalar receipts. They are not copied into this contribution. `expected/receipts.json` compares deterministic receipt digests, excluding elapsed-time fields. The matching word is regenerated from the small remove/add/read-time witness and its exact SHA256 must match.

## Verification boundary

The independent checks reconstruct baseline arithmetic and inventory; a fresh all-column base replay and a fresh complete pre-reorder scalar/COPY replay; physical alias paths and all 775 installed response/cut relations; 120 target dependencies and their individual closing frames; new shared-donor relations; exact chart factors; complete role-bank assignments; fresh integer absolute prefix bounds; and the changed finite invoice. F2 identities and integer absolute-value majorants are distinct claims in their receipts. Transport through the 133 inherited raw reorder crossing windows is conditional; no complete final frame/raw-hash regeneration is claimed.

The admission of all 133 inherited raw reorder crossing windows, semantic transform interfaces, prime selection, decoder/compiler meaning, complex-supplier structural validity and all-size closure remain explicit inherited hypotheses where not independently reconstructed. The aggregate is not a new Lean proof and does not execute upstream producers or full upstream admission suites. No blanket claim for every characteristic greater than 5 is made: h=20 uses metric 9I−J, whose inverse exterior formula is 11a−sum(a).

Positive interior alias seams are already paid children in the rebuilt histogram. Their generic wrapper/preparation costs are charged once. Rank-zero equal-frame seams add no recursive child; existing scalar and descriptor costs remain paid. The 400-factor/599-normalizer bounds apply to endpoint banking, not as a substitute for the separate interior compiler allowance.

## Bounded discovery scope

The closure screen fixes 190 coordinate-contrast lines and two deterministic donor orders. It uses exact integer maxflow for a declared 10^9-rounded finite-exponent surrogate, with full donor activation charges, then retains residues modulo 5 and disjoint unions of the three positive lines. It excludes occupied, descended, early-restored and sink roles, as well as conservative reorder-operand exclusions. Reused physical donors are eligible; actual recipient keys are not. Discovery is bounded, and final acceptance uses exact pricing and changed-stage physical checks rather than the rounded score.

The weighted matching witness is independently checked for legality and composition. No unconstrained joint optimality is asserted. See [NOTICE.md](NOTICE.md) for source attribution and AI-assistance disclosures.
