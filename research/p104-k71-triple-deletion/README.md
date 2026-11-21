# Exhibit an above-bar k=71 placement failing a three-stage deletion

The average is the existing SUBDY_68_4 row. This particular placement already fails some nodewise CROSS/PIECE2 checks, so the separation is against aggregate capacities and the explicitly listed relaxations. Another placement of this type remains open. The above-bar type objective is not a realized caller or κ bound.

For two full hubs and 138 nonhubs of degrees 2–32, a three-deletion pointwise capacity has demand 328, including the swallowed degree-two and degree-three corrections. A labelled T=447 placement passes all 71 singleton and 2,485 pair aggregate capacities, but gives 324<328 at {0,1,2}. Its type objective lies in [128.896193445305629,128.896193445305630].

Observed validation. The producer and independent checker verify all singleton and pair aggregate scores, the triple’s raw crossing score, the exact objective interval, and the earlier T=449 pair-deletion calibration. The recorded independent node checks distinguish these from the stronger individual CROSS tests.

The source archive contains the exact pins, proof, licenses, commands and control outcomes.

Archive SHA-256 `cbf5684120cc745af8e7717ca938a0fdd0bf9801f90ae482804f86836312f3ec`.

Unpack in a clean directory, validate `sha256sum -c MANIFEST.sha256`, and run the extracted README.md commands.

## Open next questions

Find a placement that survives all pointwise node-level CROSS and PIECE2 rows, or prove every placement of this particular above-bar type violates one of them.

Clear1nsight prepared this contribution with substantial OpenAI Codex assistance. Credit DreamingOfClouds for the pinned P104 toolkit and its predecessor sources. Copied Apache-2.0 sources retain their notices.
