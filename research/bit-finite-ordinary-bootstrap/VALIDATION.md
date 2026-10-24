# Author-side verification

Scientific commit: `db3856719bdf2b913f9662ec348e39c2c7c65242`.
Base: `624de9dc66858af0945e5f8a0942488d62280d43`.
Environment: Windows, CPython 3.12.14, standard library only.

- Registered package metadata/source pins: PASS.
- Both registered commands, normal mode: PASS. This includes the source-identical
  PR4760 native/caller/all-RAW replay, the tighter rank compiler and all three
  ordinary stages, and the separate census/positive-series arithmetic engine.
- Committed-byte/source-history preflight: PASS, 43 source inputs and 53 total
  exported scientific files. No predecessor file was changed.
- Export creation and archive integrity: PASS.
- Fresh Git-free extraction, empty PATH, both direct commands under
  `python -I -O -B`: PASS. Source/native, deterministic primary/independent
  certificates and negative controls pass from that extraction.

Reproduce the registered checks with the README command. Direct export commands
are `verify.py` and `independent.py`. The portable replay uses no network calls;
the environment did not impose a network-denial policy. Later documentation
and publication-identity commits do not change the verified scientific code,
parameters or input bytes; their committed bytes are checked separately.

Separate internal AI checks independently derived the exact tails, H0/H1,
prime allowance and three stages, and read the completed arbitrary-width,
spectator and nested ROW contracts. These are author-side assisted checks,
not external human review or formal-kernel verification. The completed backend
and underlying implementation premises remain those identified in PROOF.md.
The enormous uniform program and fixed machine/precision constants are
algorithm-defined, not materialized or empirically timed here.

## Hosted portability correction

The first Linux CI on head `709fcb31cc66bd8ce2165d60f495259502325536`
passed the complete primary/source replay, then rejected the independent
receipt comparison. Its four source-pin keys had Windows path separators.
The generator now uses repository-relative POSIX keys on every OS. Exact
comparison proves these key separators are the only changed certificate
fields; all mathematics, input hashes, bounds and controls are identical.
Normal and isolated optimized checks of the correction pass, including a
fresh Git-free export of the corrected independent check. The Linux hosted
primary and independent replay both passed on head
`4a4418d1f274da5dbac8778f0fdf6907a9828594`:
[exact run](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/39853042928).
This records that head's result and does not claim external mathematical approval.
