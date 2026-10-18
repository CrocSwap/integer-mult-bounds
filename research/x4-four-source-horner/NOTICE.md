# Attribution and license

Prepared for ToikY with substantial OpenAI Codex assistance in task selection,
construction, verification, independent integer implementation, mathematical
review and writing. The two implementations were written by separate Codex
agents; this is not independent human peer review.

The shared binary-Horner method and pair comparison follow Ross Richardson's
PR945 at `a3245bf22fa2a2eb778b11128cbc605b130d737f`, especially
`research/x4-joint-horner-seed29/joint.py`. The primary constructor adapts its
signed leading-digit convention, cost formula, eligibility and suffix-DP
method to fan-in three/four. No pending executable source is imported at
runtime. PR945's 13,072 backward saving is explicitly credited.

The copy/unit baseline is Sagar Thakrar's PR696, following icekylinx's
scalar primitive, coefficient work and Horner architecture. The literal
historical X4 word is Jeremy Kothe's PR799 on Chafik Boukhalfa's PR741/SW4
frames. Douglas R. Colkitt's retained maintainer replay supplies the source
artifacts; their existing source notices remain unchanged. The construction
lineage includes DreamingOfClouds, Dominik Scholz, Dugongue, eumemic, Rohan Arun
and the contributors credited in the inherited packages.

Related precedent includes PR751's equal-coefficient JP8 fan-in and PR830's
transposed shared work. This package neither claims joint Horner arithmetic
as new nor composes their pending circuits. PR932/961's target forests concern
the separate zero-frame panel and are not combined with this experiment.

All new files are under the repository's Apache License 2.0. No predecessor
copyright, source notice, license or file under `upstream/` is changed.
