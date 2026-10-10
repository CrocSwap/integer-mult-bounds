# Four signed target transformations

The new groups cover0–3,40–43,72–75 and864–871. `echelon/selection.json` records an elementary integer row-operation word, the transformed responses to every prefix source, and the common inverse frame for each group. Each operation is Y_t←Y_t+cY_p with distinct t,p and integer c. The inverse reverses the operation order and negates c.

Let T denote the coordinate transformation and R the original prefix-response matrix. Starting with arbitrary dirty target vector y, the literal word computes Ty, adds the signed responses TRz, and applies T⁻¹. Its result is y+Rz. The independent checker reconstructs T, proves det(T)=1, verifies an explicit integer inverse, and tests this transfer on independent target and response variables for both defining-integer signs.

The first three quartets replace six equal-response pairs. For group0–3 the setup subtracts Y0 from Y1,Y2,Y3, then subtracts the updated Y2 from Y3. Their common inverse frames have rank21. Each quartet changes its target histogram by C1−1,C2−1,C3+1. The fourth group replaces the former rank-response octet864–871, uses12 elementary setup operations and closes at rank20; relative to that old octet it changes the histogram by C2−3,C6−3,C8+4,C12+1,C20−1.

The four groups execute24 setup operations and24 inverse operations. Their48 nonzero signed response additions expand to56 unit additions because some coefficients have absolute value two. All these units are added to the conservative fixed-call bill, with no credits for the replaced target operations. The transformed responses are executed at their original source-gauge frames, and all groups are inverted before subsequent incompatible reads.

A sign-flip corruption is checked over the integers: F₂ alone would not detect it. Seventeen whole-word controls and separate local matrix controls reject omitted setup, omitted inverse and altered signed responses. The full source and dirty registers restore, every target remains within its exact frame cap, both reflected ledgers agree, and the new frame prime witnesses have stripped residual one.

Prepared by eumemic with substantial OpenAI Codex assistance; inherited attribution, licenses and assistance notices remain.
