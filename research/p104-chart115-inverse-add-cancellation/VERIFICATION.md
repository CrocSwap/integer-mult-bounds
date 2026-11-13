# Verification

`receipts/REVERSE.json` records exact old and candidate adjoints across all 1,501 public input columns and the one-ADD mutant. The initial reverse process exited zero locally in 13.86 seconds. The first hosted replay hit its 30-second alarm. The replay now allows 120 seconds for the same reverse checks.

`receipts/FORWARD.json` records the separate retained compiler and physical interpreter checks, including all 512 forward and 512 adjoint Gaussian columns and a rejected one-phase-step mutant. It also records the complete 1,569-row normalized forward replay, all 74 owned clears and lifetimes, 47 owned MOVE ledger entries, the COPY guard, common grid 1125 with 25 fractional bits, and the rebuilt signed ordinary upper bill. The independent process exited zero in 13.37 seconds wall time under its 360-second cap. The wrapper compares the deterministic receipt fields and omits measured elapsed time.

`receipts/EXTRACTION.json` gives the exact engine pins extracted from the authenticated predecessor chain. The package bundles the three engine files so a clean replay can run offline. The forward audit uses two explicit, in-memory literal substitutions to adopt #7481's 25-bit grid. The exact changed source hash is in the receipt. The original engines and notices are retained byte for byte.

Direct and registered replay, exact committed bytes and modes, source history, official read-only Git-free export replay and all 27 local onboarding tests passed. Hosted checks are separate.
