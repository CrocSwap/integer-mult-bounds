# Verification

All exact runners used POSIX CPython 3.12 with assertions. The R203 forward and reverse replays exited 0 in 5.07s and 0.36s within the 35-second cap. They close all 62 small-bank keys. The R204 discovery runner used 60.06s and emitted a capped receipt with 50 exclusions and 125 unvisited keys. Its exit code was 0 because it preserved progress on timeout. Independent literal replay checked all 50 frozen separators in two batches, exiting 0 in 0.18s and 0.38s within 25 seconds each. These checks recovered exact bank charts by a full reverse pass and evaluated every bank role and old source on each rational witness.

The package authenticates the compressed word and source blobs. The compressed stage-one receipt is checked by its original decompressed bytes and the exact #7434 public expected hash. Both small-bank solvers reproduce their exact receipts, and both large-bank verification batches reproduce their exact receipts. The package checks the complete partition, reprices every key and rejects an altered R203 receipt. No elapsed-time cap is used to select the public large-bank replay keys.

The complete native, signed caller, ownership, precision, tape, compiler and recurrence checks were skipped for the hypothetical edits because no span witness survived. The 125 remaining keys are unresolved, not excluded.
