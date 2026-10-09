# Balanced columns with envelope ordering and carried-signal exchanges

The selected conditional witness has κ = **51915547765237/10^18**
(**5.1915547765237e-5**) and bit saving **3244890195589/62500000000000000**.
It combines balanced coarse columns with anchored split frames, envelope
ordering and carried-signal exchanges. Physical width is **133,585,058**,
with auxiliary role counts **27,128 / 35,598**.

Compared with PR #74 at `5830ccfca8466aff613767222558e29b57fa8225`, the
conditional κ improves by approximately **0.163125609609%**. Compared with
PR #76 it improves by **0.3418559067%**. These are comparisons of pinned
conditional claims; no global optimality or unconditional theorem is claimed.

[Proof and attribution](selected-both/PROOF.md) ·
[Exact certificate](selected-both/arithmetic.json) ·
[Source and word manifest](selected-both/MANIFEST.json) ·
[Completed finite validation](package-validation-receipt.json) ·
[Exact comparison](selected-both/comparison.json)

Passed checks include dense scalar/data-output identities, full compiler
input/dirty bases, independent serialized-word replay in both orientations,
exact frame/event reconstruction, regenerated fixed-basis profiles with zero
CRT disagreements, independent rational moments, all 47 strict assembly
constraints and seven margins, and adjacent-grid rejection. Fresh portable
deterministic compilation and broad repository checks remain pending.

The package validation receipt independently reproduces all saved-word, profile
and arithmetic checks against the current manifest. Its mathematical results
match the original receipt exactly. The original validation receipt binds
the original freeze manifest archived
in `provenance/frozen-manifest.json`. Runtime sources, words, profiles and
arithmetic are byte-identical to that freeze; only proof/comparison metadata
has been updated for this publication. The current manifest records those
two documentation changes. No CI configuration or dependencies are changed.

From the repository root, restore the exact inherited source archive:

```sh
git fetch https://github.com/CrocSwap/integer-mult-bounds.git 1bef94fd40a746452548c84a4a8f8834670a3113
mkdir -p research/round6-pr71/baseline
git archive 1bef94fd40a746452548c84a4a8f8834670a3113 | tar -x -C research/round6-pr71/baseline
python3 research/round9-balanced-columns/dense_audit.py
python3 research/round9-balanced-columns/validate_selected.py --bundle research/round9-balanced-columns/selected-both --output /tmp/balanced-columns-validation.json
```

The proof gives sequential compiler regeneration commands. Use assert-enabled
Python and C++17; `CXX` can select a compiler and SDK. All inherited all-size
compiler, fixed-tape, analytic, routing, prime-selection, precision and recovery
hypotheses remain conditional. Finite checks do not establish practical speedup.

Credit eumemic's PR #69 balanced coarse columns; huxint's PR #77 anchored
adapter; Thomas DiFiore's PR #74 envelope ordering; Chafik Boukhalfa's PR #71
anchored splits and next-use scoring; Alejandro Zarzuelo Urdiales's PR #70
exchanges; Rohan Arun's PR #65/#67 schedules, costs and arithmetic; Dominik
Scholz's PR #68/#76 controls and composition; Avi Eisenberg's PR #62,
eumemic's PR #57 and the complete inherited contributor chain. This composition
was prepared by Dominik Scholz with substantial OpenAI GPT-6 Astra assistance.
All original notices and Apache-2.0 terms remain preserved.
