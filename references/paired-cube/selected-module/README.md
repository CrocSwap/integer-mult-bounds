# Frozen selected complex carrier matching

`matching-arcs.json` contains the selected 6,074 carrier donor/use pairs from
the round-nine p=12 coordinate-frame witness. Node identifiers are one-based.
An ordinary use code is `2*node + operand`; a root use is `(1<<31) | root_index`.
`SOURCE.json` binds this exact list, the deterministically regenerated scalar
graph, and the unchanged PR117 witness in `references/three-stage-cover/pr117`.
The verifier reconstructs all frames and checks every arc, rather than trusting
the omitted large annihilator witness. Different maximum matching algorithms
need not reproduce this selected matching.

Round-nine channel/matching work: icekylinx with OpenAI assistance, Apache-2.0.
Inherited PR117: eumemic with Claude assistance, existing LICENSE/NOTICE apply.
