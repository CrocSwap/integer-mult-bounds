# Certify P104 B-linear cube coverage and exclude 612 cube IDs

Verify encoding and lex coverage for 1,001 generated cubes. Exclude 612 by an explicit inactive-mask contradiction.

A fresh RUP replay independently refutes f3591, one of those 612. The other 389 lack a certificate in this package.

The source archive contains the exact pins, proof, licenses, commands and control outcomes.

Archive SHA-256 `5f26a5032de29a21b9c7767fc0f1ae905fd98590cc65a66f4b4d62f875bb6bd8`.

Unpack in a clean directory, validate `sha256sum -c SHA256SUMS`, and run `python3 -B verify_all.py`.

## Open next questions

Reduce the 389 residual cubes with independent proof-producing checks.

Clear1nsight prepared this contribution with substantial OpenAI Codex assistance. Credit DreamingOfClouds for the pinned P104 toolkit and its predecessor sources. Copied Apache-2.0 sources retain their notices.
