# Bit supplier claim — seed 2

- Started 2026-10-13 08:55 PDT; planned finish by 09:55, final fifteen minutes reserved for verification and handoff. Finish sooner if complete.
- Fresh OS randomness: `secrets.randbelow(100)` returned **2**, assigning the bit-supplier track.
- Exact fetched base: `407d52ff15b2217b6e22bce44728b4c3907b6515`.
- Selected record and actual construction/review read: PR942 U8/T37, conditional kappa `0.001661960547713947`, unchanged PR589/555 bit supplier. This investigation uses a historical R480 word deliberately.
- Three candidates: (0) another R439 six-wire prefix pass (overlaps PR980); (1) an R480 six-wire quad (PR823 already supplies quad1 and the class has substantial precedent); (2) R480 twelve-source Q-node2. Seed `2 % 3` chooses the third; `2 % 10` chooses Q-node2.
- Exact scope: historical PR503/510 word, phase A events `[2250:2302]`, frame484, twelve arbitrary source registers. Replace this one 52-XOR common-frame block, then regenerate and charge its literal reverse cleanup. No extra wire, source copy, frame transition or recursive child is proposed.
- Method: bounded 1,000 seeded column-order Gauss-Jordan trajectories for the exact twelve-output F2 map; complete whole-word positive-prefix and native checks decide admission. This is a different twelve-source matrix from PR823's six-wire dirty-helper quad1, not a repeat with a different random seed. No unrestricted optimum claim.
- Optimistic budget before packaging: a preliminary exact 43-XOR word would save nine in A and nine in C, or eighteen per complete local word; all other operations and paid recursive profile retained. Precision could invalidate it. No exponent improvement follows from this finite arithmetic saving.
- Deliverable: one frozen exact recipe, executable bounded reproduction, independent full-column evidence, complete local/native bills and controls, proof/interface limits, source pins and attribution. If the candidate fails complete precision, record that failure distinctly and allow one bounded revision within this block.
- Coordination: open issues650 and913 are unrelated; no pinned sprint issue found. Local claim used. Refreshed recent PRs through985 and all-state R480/Q-node queries immediately before claiming. PR823 is the relevant historical comparator, PR980 concerns R439, PR978 R420 compensation; none changes this Q-node. Review ledger records PR503/510 and PR691 as incorporated. No separate reservation issue.
- Scope ownership: delegated work stays within this block; no edits to upstream, selected frontier, inherited generators or unrelated packages.
- Prepared for ToikY with substantial OpenAI Codex assistance, Apache-2.0; full predecessor credit and exact pins will be included.

## Completed result and claim update

The candidate and search were frozen by approximately 09:03 PDT, followed by
verification and packaging. Three preliminary orientation probes ran in order
Q2, Q1, Q8, each with a fresh `random.Random(2)` and 1,000 trajectories. Their
best lengths were 52 -> 43, 71 -> 41 and 62 -> 46. Only the seed-selected Q2
was packaged and admitted; the other probes received no whole-word precision
or native validation. Final Q2 coverage is exactly 1,000 trajectories; no
further search or pivot was made. This disclosure avoids presenting the
orientation probes as admitted additional results.

Completed: Q2 uses 43 XORs and literal cleanup saves 18 complete local ADDs.
Both independent Python implementations and retained native 5/9/11-stage
checks pass; the paid histogram and frame paths are unchanged, and both
complete payloads remain 102 bits within the 104-bit allowance. No new kappa,
optimum or hosted-parent invoice is claimed. See VALIDATION.md for executed
coverage and controls.

Final overlap refresh through PR999 and all-state R480/Q-node searches found
no duplicate of this matrix. Related PR823 is credited. New PR986 and PR989
concern R439; main `f4a7051883bc76dad7861b3f0caf7361ce86fe90` preserves all
21 consumed source blobs and the selected record. There is still no open
sprint coordination issue. This is the one local claim update with the result:
[reviewable contribution branch](https://github.com/ToikY/integer-mult-bounds/tree/codex/bit-supplier-seed02/research/r480-qnode-seed02).
