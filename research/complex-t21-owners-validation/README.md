# T21 validation receipts

Both independent cold replays passed κ = 0.001661957774647029 with assertions enabled. macOS used Python 3.11.15 and Linux aarch64 used Python 3.14.8; both rebuilt PR589, PR741, PR799 and U8 before the new T21 controller. Each ran all 20 mandatory stages and the separate 19 package-boundary rejections plus two gzip recompression positives. The companion fixed-family bound passed with three controls on both platforms.

`VALIDATION.json` records exact cross-platform comparisons and source manifest hashes. `FULL-REPLAY-SHA256.json` binds all 648 output files per run; the full outputs are recreated by the documented verifier. Selected independent control and bound receipts are retained here. These receipts record finite conditional validation, not an unconditional theorem or authenticated execution history. CI evidence is attached to the pull request.
