# Exclude the fixed-clock two-relay repair for the BIT rank-21 triple

Extends #7921 to a second relay for the exact peer triple, retains original source/delivery clocks and exterior rows. The separate same-relay price-only bound does not cover cross-relay returns.

All 334 charts and 14,283 covering pairs fail the fixed-clock no-exchange screen. All 357 proper nested pairs fail every original deadline even with free historical stock and unlimited exchange.

Observed validation. A fresh extraction passed `python3 -I -B verify_all.py` in 9.99 seconds, including 2,073 separating assignments and a corrupted-witness rejection.

The source archive contains the exact pins, proof, licenses, commands and control outcomes.

Archive SHA-256 `1222e5bbd3c9aa2ba88d6f0adafcf579661951fc16d6535f3b1b4077535d384d`.

Unpack in a clean directory, validate `sha256sum -c SHA256SUMS`, and run the extracted README.md commands.

## Open next questions

Change a deadline or exterior row with a realizable funded stock path and full protected output replay.

Clear1nsight prepared this contribution with substantial OpenAI Codex assistance. Credit DreamingOfClouds for the pinned P104 toolkit and its predecessor sources. Copied Apache-2.0 sources retain their notices.
