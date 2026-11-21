# Combine P104 decoder gauges using paid row budgets

Gives a weighted certificate combining individually gaugeable subsets under explicitly checked per-row rank budgets.

An exact P104 construction gives a weighted bound of 104 with single-subset maximum 52. The pinned E8 example gives 17 versus 6 with unit weights. Negative controls reject mere disjointness and submodularity.

The source archive contains the exact pins, proof, licenses, commands and control outcomes.

Archive SHA-256 `c2753b47cbc6ef01290245b483f4b55f2829fa722aaf251b96e17aa71708db3a`.

Unpack in a clean directory, validate `sha256sum -c SHA256SUMS`, and run `python3 -I -B verify.py`.

## Open next questions

Evaluate row-budget certificates on the loose-row classes still open in #7869.

Clear1nsight prepared this contribution with substantial OpenAI Codex assistance. Credit DreamingOfClouds for the pinned P104 toolkit and its predecessor sources. Copied Apache-2.0 sources retain their notices.
