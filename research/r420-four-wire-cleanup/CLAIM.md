# Sprint claim: four-wire cleanup synthesis

- Track: bit supplier. Fresh OS assignment seed **17**, generated with `secrets.randbelow(100)`.
- Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Object: selected #543 R420 cleanup C, expanded into its ordered binary XORs. Width selected as `2 + (17 % 3) = 4`.
- Hypothesis: an arbitrary exact CNOT circuit on a contiguous window's same at-most-four registers can shorten that window. This admits noncommuting identities outside #710's completed commuting-deletion class.
- Method: enumerate GL(k,2), k=2,3,4, with exact shortest-path distances; exhaust contiguous original cleanup windows on at most four registers. If gains exist, choose nonoverlapping windows and check all arbitrary-input maps and complete costs. No extra helpers, copies, source accesses beyond the counted XORs, frame changes or recursive children may be omitted.
- Deliverable: a verified finite circuit improvement, or a complete scoped shortest-circuit census with rejection controls. No global circuit-optimality or new kappa claim.
- Finish target: 2026-10-13 05:43 UTC; reserve the last quarter of actual work for independent verification and handoff.
- Coordination: no pinned issues exist. Open queue initially 566 PRs through #747. Local claim recorded; no reservation issue opened.

## Three candidates considered

1. Frame-zero target-donor sharing in D: already crowded by #713/#716/#733/#742.
2. Synthesis of B block 7: resembles #670/#674; #688 already supplies composition and global verification.
3. Exact four-wire cleanup window synthesis: selected because it changes the search class beyond #710's commuting cancellation and specific conjugation.

## Prior work and scope

#710 `d97c8d20a8b885271a24c5a4e8446ac7f5697d5c` closes commuting-only deletion on the fixed cleanup and gives a different two-sandwich rewrite. This experiment does not repeat that search or import its patch. #688 `bb05c40c3e6319aa8c131b06a105e3648ac6c95b` concerns B blocks 3 and 5 and their changed cleanup. The archived R715 commuting-cancellation experiment is a different word and a narrower identity class. The selected result and actual #543 construction were inspected through the current selected certificate and #626 review. Previous contribution #739 is complex-side and independent.

## Result and handoff — 2026-10-13 05:08 UTC

Completed: [PR #754](https://github.com/CrocSwap/integer-mult-bounds/pull/754),
construction commit `8ee38f714dc80526c05a6653c1ff56a678615d49`.
All 7,693 original windows were examined; 284 admit shorter circuits.
The independently certified optimum over disjoint original windows saves
137 XORs in 101 replacements, taking the complete word from 26,916 to 26,779
ADDs with unchanged paid paths and no new κ claim. Both words pass native
legality and 5/9/11-stage replay, including 96 omitted-bridge controls.
The final part of the sprint was reserved for independent review, relocated
replay, corruption controls and this handoff. Final queue refresh through
#753 found distinct concurrent decoder/compensation work, credited in the
README without an additive or composed saving claim. No pinned coordination
issue existed, so this is the single local claim update.
