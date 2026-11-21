# Certify the maximum paired-cut deficit on the P104 804-bank witness

Exact independent-set separation gives a paired-cut deficit of 50 each direction for the pinned 804-bank witness.

A 28-edge and four odd-cycle certificate proves the upper bound. Fixed append-only nested repair forces at least 100 extra banks and D+R≥128.

The source archive contains the exact pins, proof, licenses, commands and control outcomes.

Archive SHA-256 `1296d28a29c0825af438ce424c1330289783013048a4d37fa0988ccec393cbb0`.

Unpack in a clean directory, validate `sha256sum -c MANIFEST.sha256`, and run `python3 -B -S verify.py`.

## Open next questions

Separate a redesigned bank network without the fixed-witness assumption.

Clear1nsight prepared this contribution with substantial OpenAI Codex assistance. Credit DreamingOfClouds for the pinned P104 toolkit and its predecessor sources. Copied Apache-2.0 sources retain their notices.
