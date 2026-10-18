# Attribution and source pins

Contribution: Jerry Chen (@CubeJerry), with substantial OpenAI Codex assistance
in implementation, analysis, tests and documentation. Apache-2.0; the
repository LICENSE applies. No independent human review is claimed.

The original affine-vector families, Golay/Leech generator, fixed witnesses,
rank rejections and audit are by **Douglas R. Colkitt**, retained from commit
`d55bcd62ceb8f322bcf311a5a66e94c3ac7724f0`. The source note credits Brouwer and
Van Maldeghem, *Strongly Regular Graphs*, section 6.3.1 for the minimal-vector
construction. The original note, source files and all attribution remain
unchanged. `PINS.json` gives exact file hashes at base
`f567884aeb8851b6e794af1184119a3bfbe1e631`.

**Curtis Dransfield (@Curtis-D), PR752**, head
`3603d8d9184995ae1cc67c0f5e01f02f3a1d634e`, supplies the related carry-safe
integer-lane approach for quadratic-affine Hermitian minors. Its technique and
coverage discipline are credited; no code or fixture from that PR is copied.
This contribution reconstructs a distinct set of five signed real Leech
minors and decodes bytes directly.

**merramil, PR778**, head `f015b04c74801fa330f818d178e809c760fb5469`, improves
historical single-intersection Gram construction with symmetric packing.
It is related concurrent performance work, not a dependency of this package.
The original `rank_of_rows` imported here remains unchanged.

The retained upstream OpenAI manuscript and sources are pinned at
`adc7f1241b42e322a6451854ab7e4b4c146bf78a` with their original Apache-2.0
license and notices. No upstream file is modified.

Selected-result context follows Jeremy Kothe's PR799 X4 construction,
Chafik Boukhalfa's PR741 and DreamingOfClouds' PR589 on eumemic's PR555.
Those constructions and their predecessors are not changed or re-certified
by this historical-checker optimization.
