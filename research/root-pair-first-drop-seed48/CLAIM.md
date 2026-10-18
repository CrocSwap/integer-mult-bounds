# Round 4 structural decoder claim, seed 48

Base `2921874911956718fcaaaf9396fe8267b3cfa9f0`. Scope: the first puncture
threshold beyond PR968's p<=24 closure at which an odd pair of E8 root normals
has term pairing cost at most six. Seed48 chooses the starting root line48
in a fixed independent lexicographic model, with its first odd partner.

Method: enumerate all codimension-two functional violator masks for the two
root supports; use exact F2 pairing ranks and the rank-dimension inequality
to make the 25-puncture coverage complete; test a 26-puncture witness and
transport the result over the finite simple-reflection orbit. If found,
complete the normal pair to an exact eight-term decoder and report its full
cost. No claim of a global decoder optimum or implemented supplier.

Three candidates: (1) this first-drop threshold (chosen); (2) changed-reader
decoders with at least nine terms (too broad for one round, adjacent to
PR998's multi-lift exclusion); (3) masked identities on the E-graph (distinct
functional model requiring another proof boundary). PR968 closes <=24, not
this first open boundary. No geometry from round1 or shared/multistage-copy
scope from round6 is used.

Expected outcome: exact small threshold or a sharply scoped completed
negative result, with source pins, independent replay and mutation controls.
No GitHub writes, selected-pointer changes or edits outside this package.
Prepared for @woklerx with substantial OpenAI Codex assistance. Apache-2.0.

Completed result: threshold exactly 26. Exhaustive 25-puncture coverage gives
126 masks, all rank seven. The explicit 26-puncture witness has rank six,
and verified reflection transport covers all 6,720 ordered odd root pairs.
Its rational eight-term completion costs 69 copies on 94 ports and makes
no supplier improvement claim. See PROOF.md and CERTIFICATE.json.
