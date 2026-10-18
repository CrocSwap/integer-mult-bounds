# Executed validation

This folder retains one complete fresh strict replay of witness635 at immutable commit `4988e425009a1a94ebd5f4281a251fa5cc9cb162`, including the baseline, both native providers, physical owner controller and exact moment assembly. `VERIFIED.json` identifies the command, environment, input manifest, scope and checks.

`FRESH-REPLAY.tar.gz` contains the entire generated `replay/` directory, including all stage logs and local/global artifacts. `RECEIPT.json` binds the 64 main stages and selected generated artifacts; `WRAPPER.log` additionally records the independent basis proof, twelve composition mutations, native-owner/rational checker, five owner mutations, declaration reconstruction and both nomination exporters. `EXECUTED-MANIFEST.json` and `EXECUTED-README.md` preserve the exact input manifest and README used by the replay. Any later prose-only README/manifest refresh is separately documented by the parent README. `SHA256SUMS` covers every retained validation file except itself.

The wrapper was run with no baseline or local reuse. Earlier discovery used reused baseline/local artifacts only to nominate inputs; those runs are not represented as fresh evidence here. The exact finite conditional saving is κ = 0.001636269762440408. All inherited premise limits in the witness README remain. Execution was on macOS; no Linux run is claimed.

Prepared by Chi Zhao with substantial OpenAI Codex assistance.
