# Audit eight cross-port branches on residual P104 cubes i3 and i5

The coupled exact row spans apply to the selected 24 ports. Upper witnesses of cost 60 or 61 do not prove price ≤55, infeasibility at 55, or full-cube satisfiability. The earlier ≤55 assertion was withdrawn.

Each cube has a complete four-way flag branch cover. After restoring every active-row condition, an unbudgeted 24-port span witness costs 60 in child 00 and 61 in each other child. All eight lower bounds remain below 55 and all eight budget-55 questions remain unresolved. The sound inherited exclusion count remains 665/1,001.

Observed validation. The corrected public-replay log verifies the eight child CNF hashes, all active rows, explicit spans and selected clauses, exact lower bounds and damaged controls. Old 665 exclusions were replayed separately. The packet's README explicitly labels each corrected bound.

The source archive contains the exact pins, proof, licenses, commands and control outcomes.

Archive SHA-256 `d907219aba65368aa9eb7c67d71c72600d31fded0058f90c497c8e87a49800ac`.

Unpack in a clean directory, validate `sha256sum -c SHA256SUMS`, and run the extracted README.md commands.

## Open next questions

Add genuinely valid coupled constraints or port coverage, and seek a verified lower bound >55 in every child or a fully legal budget-55 construction.

Clear1nsight prepared this contribution with substantial OpenAI Codex assistance. Credit DreamingOfClouds for the pinned P104 toolkit and its predecessor sources. Copied Apache-2.0 sources retain their notices.
