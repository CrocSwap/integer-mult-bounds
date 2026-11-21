# Independently certify the P104 Q=0 duals and derive a two-hub mask restriction

Independently encloses the #7869 Q=0 exact LP duals at k=71,72,73 with integer 100th-root arithmetic. The k=72 and k=73 upper endpoints are 128.850071932566733 and 128.681325145969645.

The #7856 masks first violate DYADIC_2 by 58,62,60 respectively. A direct signed-block proof requires 10,11,10 enlarged nonhubs at k=71,72,73 in the two-full-hub frame family. Fifteen legal small controls replay.

The source archive contains the exact pins, proof, licenses, commands and control outcomes.

Archive SHA-256 `50272760bdd6093cf05e552a5efb453d2c45a65a843e2109a033c69cd7392baa`.

Unpack in a clean directory, validate `sha256sum -c SHA256SUMS`, and run `python3 -B verify.py` and `python3 -B positive_controls.py`.

## Open next questions

Derive the remaining full-LP rows and frame-to-configuration bridge in Lean, and address the k=71 and smaller windows.

Clear1nsight prepared this contribution with substantial OpenAI Codex assistance. Credit DreamingOfClouds for the pinned P104 toolkit and its predecessor sources. Copied Apache-2.0 sources retain their notices.
