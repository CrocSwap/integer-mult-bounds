# Attribution and license

Prepared for Gareth Davidson (@bitplane), with substantial OpenAI Codex
assistance in research, proof, implementation, checking and writing. One AI
agent performed this pass. The two implementations provide algorithmic
crosschecks, not independent human review. New work is Apache-2.0; see LICENSE.

**@dd-hemant (Hemant), PR816**, head
`133735a2cc2319c12ba5d786214b2217e083e7da`, supplies the CK signed-unit forest,
its exact 16,364 floor, the retained recipe and 66,520-real-primitive saving.
Its forest construction/MST method and exact source layout inform this package.
The recipe is read unchanged from the maintainer-integrated package. Its
original proof and attribution remain intact. Credit **Oscar Fennell, PR759**
for the binary forest/superroot mechanism and **Sricharan Vagvala, PR749**
for restored rational target pairs.

**ToikY, PR909**, head `5896f6fce48ee1d507722cc91eb1dcccc878670d`, supplies the
quarter-grid affine-tail argument and cost-domain model for nonunit powers of
two on X4 disjoint pairs. PROOF.md explicitly follows that argument. The CK
census, quantitative edge-deletion extension to overlapping forests, and
the independently regenerated forest evidence are the new scope here.
No priority is claimed for the original tail identity or forest minimum.

Concurrent **woklerx PR961**, head
`4257ddf4b755cd0ac3bd3b0f6281cc5b2b1f72ad`, arrived during final verification.
It extends the X4 signed-unit floor to every nonzero dyadic parent coefficient
using root or same-parent unit-edge domination. The related forest-exchange
reasoning is acknowledged; no implementation or claimed X4 census is imported.
This contribution retains its independently checked CK power-of-two scope.

**Ross Richardson, PR932**, demonstrates signed-unit forests on X4 and
records the nonunit/overlap boundary motivating this pass. **Ross Richardson,
PR917**, combines a CK target forest with helper transformations, outside the
present fixed-helper class. Their new circuits are not imported or priced as
additive savings here.

Historical PR626 is Chafik Boukhalfa's owner repair on Jeremy Kothe's PR622
chain. The retained CK construction, emitter, Horner invoice and checks credit
icekylinx, DreamingOfClouds, eumemic, Dylan Crow, Zhihao Chen, DaysSky,
Dominik Scholz, jon314159, Dugongue, Rohan Arun and the source notices. Original
licenses and AI-assistance disclosures remain in their packages. SOURCES.json
pins the exact consumed source, recipe and proof objects. The current PR890
frontier and the historical word are unchanged.
