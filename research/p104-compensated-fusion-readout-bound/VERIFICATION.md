# Verification receipts

The 17 deterministic receipt hashes in `receipts/SHA256.json` were reproduced from the declared closure using CPython 3.12.14. Direct replay exited 0 in 3.32 seconds. A Git-free staged tar export with an empty environment replayed in 2.89 seconds. The registered repository runner validated the pinned base catalogue and selected-record metadata and passed in 3.34 seconds. Each replay rejects a changed compressed word before decoding. The known-good and synthetic controls run within the same command.

The initial staging replay used an independent Round 68 case cap of 4 and therefore disagreed with the original receipt's cap field. The original runner cap is 128 and its actual coverage is 4. Using the original cap reproduced the exact sealed bytes. No input or prior receipt was changed.

The package's scoped negative outcome is local verification. Committed-byte, mode and source-history checks require the final contribution commit. Hosted checks for this contribution are pending its submission. Separately, comparator [#7334's exact-head run](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/43114736518) passed all three jobs at the 23:08 UTC refresh on November 11, 2026. Its four-stage independent local scientific replay is recorded in the bundled admission receipt.
