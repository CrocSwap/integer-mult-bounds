# Fixed-clock simultaneous Type B signed idle unions

**NO VERIFIED GAIN.** Exact Δκ = 0 on independently reproduced conditional κ = `0.00364665195644`, #7334 at `aaeec8c0acf01e99a5f331ef363a698d9c084ace`, with signed #7113 at `07a76c5e2738882c0cb322278e56f6cae3c9885d`. [Comparator #7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) · [Signed caller #7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)

Each proposed edit adds one disjoint even body mask to a signed odd idle at the original odd clock and role, and removes that even idle. We exclude every nonempty choice of at most four edits with distinct odd and even clocks and the rest of the caller fixed. Both engines exhaust 17 body stages and 18,443 stagewise subset comparisons. Of those, 4,527 admit a mask-compatible bijection. No exact projector sum agrees, and all 60 even sites have a missing-stage certificate. [Stagewise proof](PROOF.md) · [Agreement](receipts/STAGE-AGREEMENT.json)

The nested two-edit test independently excludes all 11,728 unequal-mask and 210 equal-mask placements. The two largest size-eight cases also fail direct 36-column endpoint tangents, with witness +16 at global coordinate (36,36). [Two-edit proof](r123/PROOF.md) · [Two-edit agreement](r123/receipts/AGREEMENT.json)

The optimistic four-edit matching would lower the paid position count from 110,519 to 110,487 and leave 22,461 productive positions fixed. The whole-stock upper is 3.076075380146476 raw at the incumbent. The complete fixed-target margin is at most −136.39071166273732. The tested family has no supported construction and zero verified savings.

## Replay

Use CPython 3.12 and assertions from a clean checkout.

```sh
python3.12 -I -B research/p104-type-b-simultaneous-idle-bound/replay.py
```

The standard-library replay authenticates exact #7357 receipts and the signed #7113 caller, regenerates both complete prices and replays both engines at each scope. Add `--out fresh-directory` for all eight receipts. Altered predecessor, price and caller bytes reject. [Verification](VERIFICATION.md) · [Path-keyed pins](LOCAL-PINS.json) · [Source provenance](r123/PROVENANCE.json)

## Open next questions

Could a distinct paid mechanism preserve these body-stage responses with different clocks, roles or supplier action? Start from one concrete changed operator and price every changed child and ancillary operation on the complete invoice. The result exhausts the fixed original-odd-clock union family and does not address those different mechanisms.

## Credit

#7357 at `b4902a36a1506ab87cbdee03c51345b179fb00a6` supplies the 180 one-edit obstructions and exact input manifests. #7315 supplies the even-idle census and projector method. #7323 supplies the odd-idle census and earlier joint sign-cancellation method. #7356 extends that separate sign-transfer model, #7144 supplies a different fixed-skeleton diagonal-gauge obstruction, and #7296 treats the exact site (1339,2324) under a canonical erased-child volume bound. #7298 supplies the directed tariff. [#7357](https://github.com/CrocSwap/integer-mult-bounds/pull/7357) · [#7315](https://github.com/CrocSwap/integer-mult-bounds/pull/7315) · [#7323](https://github.com/CrocSwap/integer-mult-bounds/pull/7323) · [#7356](https://github.com/CrocSwap/integer-mult-bounds/pull/7356) · [#7144](https://github.com/CrocSwap/integer-mult-bounds/pull/7144) · [#7296](https://github.com/CrocSwap/integer-mult-bounds/pull/7296) · [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298)

OpenAI Codex and subagents materially assisted proof, implementation, independent verification and packaging.
