# Source-side retiming and crossed-read bound

**NO VERIFIED GAIN.** Δκ = 0, exactly 0% relative to conditional κ = 0.00364665195644 on exact [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) `aaeec8c0acf01e99a5f331ef363a698d9c084ace` with signed [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) `07a76c5e2738882c0cb322278e56f6cae3c9885d`.

Two exact chronology walks cover **33,560 typed cuts** across eight frozen public MOVE windows. The mover is the sole intervening ADD's source. At 33,517 cuts its original recipient is on the wrong endpoint chart. The 43 matching cuts all belong to one paid edit on role 532 and cross the same signed read of recipient 205.

Retiming that ADD would remove a **+1/4** source-532 response from role 198. Two exact engines exclude the public correction bank immediately before the old read. Coordinate 27 is zero in every adjusted donor and nonzero in the missing response. Both engines also verify that role 198 stays on chart 207 at all 43 late cuts requiring chart 127. The [compact response witness](receipts/CROSSED-RESPONSE.json) records the exact donor bank, signed coefficient and prior protected classification. No tested key remains unresolved.

The one paid contraction would remove 17 paid positions and preserve every productive position. The eight-window compatible upper is about 1.063823269504365 raw before ancillary charges. The crossed-read pair alone has a directed upper of about 0.118078219358088 raw. Exact support leaves zero verified saving. [Proof and complete price](PROOF.md)

## Reproduce

Use CPython 3.12 with assertions and the standard library. From this package in a clean checkout or Git-free export:

```sh
python3.12 -I -B replay.py
```

Use `--output replayed` to retain the [eight pinned receipts](receipts/SHA256.json), including exact chronology, sparse rows and the cross-engine agreements. [Pinned provenance](PROVENANCE.json) · [Verification](VERIFICATION.md)

## Open next questions

Start from the [crossed-response witness](receipts/CROSSED-RESPONSE.json). A different compensation mechanism must supply coordinate 27 or change the old observation while staying inside the complete price. Preprice all compatible costs before testing another cut or adding a source. Owned donor roles, other clocks, other reads, and altered paid paths remain outside this scope.

## Credit

[#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) supplies the exact native word and #7113 the signed caller. [#7365](https://github.com/CrocSwap/integer-mult-bounds/pull/7365) at `98be9db1f28cdc5fa8962c7da065bc0174db9744` supplies the frozen changed-role census and invoice. [#7366](https://github.com/CrocSwap/integer-mult-bounds/pull/7366) at `30358d4b7467957ddc63ac1893588707c7b66c9e` tests destination-side retiming and late donors. [#7003](https://github.com/CrocSwap/integer-mult-bounds/pull/7003) and [#7312](https://github.com/CrocSwap/integer-mult-bounds/pull/7312) supply earlier ADD-slide and common-lift methods. [#7355](https://github.com/CrocSwap/integer-mult-bounds/pull/7355) supplies the exact donor-span engines.

[#7338](https://github.com/CrocSwap/integer-mult-bounds/pull/7338) at `349996445176e934ffb3c76813adcd230ca8f783` includes exact paid pair `532:44611:46018`. Its [geometry receipt manifest](https://github.com/CrocSwap/integer-mult-bounds/blob/349996445176e934ffb3c76813adcd230ca8f783/research/p104-compensated-fusion-readout-bound/receipts/SHA256.json) binds the `protected_or_owned_component` disposition before that package's maximal-component support gate. This contribution tests the same paid pair through a fixed two-contact public response. A [parallel role-1182 claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19555191) concerns deferred coframe correction at separate clocks. OpenAI Codex and subagents materially assisted proof, implementation, independent verification and packaging.
