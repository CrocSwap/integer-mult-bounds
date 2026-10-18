# Sprint claim

- Track: complex supplier. OS assignment seed **24**, drawn with Python `secrets.randbelow(100)` and persisted before selection. An earlier unpersisted draw was lost in truncated tool output and was not used for task selection.
- Exact base: `ba82555c64e1879e4b7decce28186f208fcb8262`.
- Current accepted selection: PR1042, kappa `1672188119205421/10^18`; selected manifest, assembly, actual gauge44-slots-t16 construction and batch1047 review inspected. No selected-frontier change proposed.
- Three candidates: CK coefficient-grid synthesis (overlaps PR1118); restored CK helper butterflies (overlaps PR1116); scratch-free permutation boundaries (selected).
- Object: PR971's 168 historical CK/JP8 deferred-swap boundaries, especially the 2+3-cycle boundary. Permit arbitrary mixed intermediate rows on exactly the moved coordinates, with the complete invertible PR696 real primitive alphabet and no work register or borrowed fixed coordinate.
- Hypothesis/method: reducing exact dyadic words modulo 3 permits an exhaustive meet-in-the-middle exclusion of words through length eight. Independently replay exact witnesses and classify the actual boundaries. Seed 24 fixes coordinate/generator presentation, not sampled coverage.
- Deliverable: one finite cost/scratch result with complete search domain, exact replay, meaningful adverse controls and a source-bound boundary census. No multiplication theorem or new kappa claim.
- Stopping rule: complete radius-four modular balls for dimensions 2, 3 and 5; permit one evidence-driven refinement only if needed. No unbounded circuit search.
- Expected finish: 2026-10-13 19:14 UTC; final verification/handoff starts by 19:06 UTC.
- Coordination: GitHub pinned-issue query immediately before claim returned none. Local claim used. Open queue read through PR1127; targeted scratch/permutation searches and PR1095 head `1db482a6cb63ae49cf156357ef98b8e4b676fcd9` inspected. PR1095's monomial-prefix class is distinct and credited. No workers delegated.

## Result and handoff — 2026-10-13 19:05 UTC

Submitted [PR1145](https://github.com/CrocSwap/integer-mult-bounds/pull/1145), a scoped negative result. Complete independent radius-four balls agree on 509,157 matrices/distances. The scratch-free two-/three-cycle minima are 4/6; the disjoint 2+3-cycle minimum lies in [9,10], compared with the existing 8-operation scratch witness. All 168 historical boundaries are source-bound; exactly-moved-coordinate elimination costs at least 28 additional real primitives per orientation. Nine versus ten, borrowed fixed registers and full supplier integration remain unresolved.

Research base is unchanged; submission rebased to `ce7ad1b6ab09452c3478723a2e96ed5ff212dc08`, which now selects PR1094. All seven input blobs remain identical. Tested implementation commit: `07e119dc44edf2bfa546f7212b5d60b0b9f44f12`. Full replay and ten test groups pass on CPython 3.14.6 and 3.9.6, with exact receipt regeneration, 37 gate omissions, source/receipt corruption and minimal relocation. Current selected-record integrity and five selected tests pass. Only this claim closeout changes after that tested implementation.

Final overlap refresh through PR1142 and title searches for scratch-free/permutation work found no duplicate; PR1095's exact head stayed unchanged. No pinned coordination issue exists, so this is the single local claim update. Upstream has neither `codex` nor `codex-automation` label. Hosted CI remains separate from the completed local checks. No merge, selected-frontier edit or upstream source edit.
