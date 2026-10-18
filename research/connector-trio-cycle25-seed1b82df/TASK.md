Task ID / scope key: `connector-alphabet-change` / `F2^6-full-mask-cycle-k12-W14-single-TRIO`
Track and accepted seed: `recursive-interfaces` / `1b82dfd0673536e282d9d9e7adcb1a04`
Priority revision / catalogue SHA-256: 4 / `d46eb6d5b3e279428753d770653663fbdf1063e55c255ea073d768f344927ef7`
Exact base / selected-record SHA-256: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2` / `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`
Scope status: **changed** from the pair-source DUO handoff. Fix the source group to `F2^6`, use exactly twelve complete source calls with eleven singleton steps and one charged weight-three step, and require all 63 nonzero prefix differences. The new operation is `B_jkl: z += B_j x_j + B_k x_k + B_l x_l` with source rows read-only.

Question: can a closed 12-step source path with exactly one weight-three step and eleven weight-one steps cover every nonzero mask of `F2^6` as a pairwise difference of its twelve distinct boundary prefixes?

Predecessors / nearest work: `research/universal-connector-boundary/` proves the exact five-source boundary and provides the paired-readout interface. `research/duo-toggle-connector/` adds a fully charged weight-two DUO operation; its n=6 successor is PR #2128, head `697369a971eed02c0fbcd75ebefec9f59945f08e`, with a 14-call, 16-add universal path. Its five-source weight-three question is answered in the PR body. This cycle changes both the operation arity and the n=6 parameter domain; it seeks a 12-call path, which is the counting lower bound because 11 prefixes yield at most 55 differences.

Optimistic complete budget: the 63 outputs require two readouts each, for 126 A calls in either schedule. PR #2128 uses 14 source calls and 16 source additions (140 total root calls). A positive path here uses 12 source calls and 14 source additions (138 root calls). With complete source-call overhead `o` and per-add cost `p`, the modeled saving is `2o + 2p`; the TRIO itself is charged `o + 3p`, never as one free addition. Any extra implementation surcharge for a three-source call must be below `2o + 2p` to retain the modeled advantage. No native supplier/controller/hosting instance currently exists, so no supplier or kappa claim is possible.

Method / bounded domain: translate each path to a simple 12-vertex cycle in the 6-cube with eleven Hamming-distance-one edges and one closing distance-three edge. Translation and coordinate-permutation symmetries set the start and first two singleton edges to `0, 1, 3`. Enumerate every self-avoiding unit walk under that normalization (at most `5^9 = 1,953,125` paths), retain endpoints of weight three, and test the exact full difference set. A complete negative covers only this call/weight profile; a positive witness is checked against the universal connector endpoint for arbitrary dirty inputs through the paired-prefix-difference identity.

Success evidence: exact twelve-call path and full 63-mask difference certificate, or complete census of the stated profile. Include the 12-call counting floor, direct source/add/query bill, PR #2128 benchmark, source restoration and one omitted/altered-step negative control. Stop after the complete normalized domain; do not widen to other weight profiles in this cycle.

Claim venue: new canonical Discussion thread in the Ideas category; short pointer to #1167. Fresh overlap snapshot: 396 open PRs and 807 Discussion records, complete pagination with no warnings; exact all-term query for six-source / TRIO / 12-call / weight-three returned zero matches.

Reproduction target: `python3 -I -B research/connector-trio-cycle25-seed1b82df/verify.py`. Substantial OpenAI Codex assistance; no independent human review claimed.
