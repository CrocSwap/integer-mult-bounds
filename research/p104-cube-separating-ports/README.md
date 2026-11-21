# Raise two 28-port tight-cube projection lower bounds to 44

28-port projections of the two 00 children with the specified cover and normal constraints. The upper constructions exceed 55. Neither full cube nor budget-55 SAT/UNSAT is resolved; the inherited 665/1,001 full-cube count is unchanged.

Retesting all 80 omitted ports invalidates the saved i3/00 and i5/00 24-port witnesses at 42 and 22 ports respectively. Four additional distinct ports per child give exact simultaneous projection bounds 44≤Q≤63, improving the prior integer lower 43.

Observed validation. Original clause generation finds the same first violated port-0 cover clause in both old witnesses. New exact rational lower certificates, 63-cost upper subspaces, sources and damaged controls verify independently of solver output.

The source archive contains the exact pins, proof, licenses, commands and control outcomes.

Archive SHA-256 `457a68b2d03e949e7f58324e0ad2dbf975b12f25a4d2d816f9044ebb60f0e804`.

Unpack in a clean directory, validate `sha256sum -c SHA256SUMS`, and run the extracted README.md commands.

## Open next questions

Add original omitted constraints that separate the new 63-cost upper witnesses, or obtain a verified all-port ≤55 word or >55 projection certificate.

Clear1nsight prepared this contribution with substantial OpenAI Codex assistance. Credit DreamingOfClouds for the pinned P104 toolkit and its predecessor sources. Copied Apache-2.0 sources retain their notices.
