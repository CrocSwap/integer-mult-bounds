# Exhibit exact BIT readout obstructions for a diamond and three helper splits

Checks the ingress swap on the literal 0→2/5→125 diamond and three remaining fixed-source middle-window helper splits after 200 bounded pair representatives.

All six swapped bases fail the early clock-11 reader. The three helper readouts fail even with the specified free stock. A causal two-world witness matches all seven available stocks.

The source archive contains the exact pins, proof, licenses, commands and control outcomes.

Archive SHA-256 `a1df9182c5e6055ff1a4033eed7e061ef54b505c457e74ff0f929e771656f742`.

Unpack in a clean directory, validate `sha256sum -c SHA256SUMS`, and run `(cd diamond && python3 -IB replay.py)` and `(cd helper && python3 -IB verify.py)`.

## Open next questions

Test changed old packet histories, additional paid observations or larger and non-fixed helper interfaces.

Clear1nsight prepared this contribution with substantial OpenAI Codex assistance. Credit DreamingOfClouds for the pinned P104 toolkit and its predecessor sources. Copied Apache-2.0 sources retain their notices.
