# Local sprint claim

- Track: bit supplier. OS randomness assignment seed: **18**.
- Base: `f567884aeb8851b6e794af1184119a3bfbe1e631`.
- Started: 2026-10-13; expected finish within 45 minutes of scope selection.
- No pinned coordination issue exists (GitHub GraphQL checked); the only open
  issue is #650 about Discussions. Claim recorded locally as instructed.
- Candidates considered: (1) whole positive-integer factorization of tuned R439
  B block 8, (2) phase-A quad 18 resynthesis, (3) cleanup frame reduction.
  Choose (1): (2) closely repeats existing quad work and (3) is excluded by
  #827's fixed-prefix result. Seed 18 selects block 18 modulo 10 = 8.
- Exact object: PR589 tuned R439 B[404:449], frame 523, twelve wires.
  Search full-block nonnegative integer row-subtraction factorizations, without
  preserving the predecessor's two-factor boundary. Require the same forward
  integer matrix and entrywise nonincreasing reverse positive matrix.
- Deliverable: one literal circuit witness, exact verifier, paid restoration
  and source/access/frame accounting, mutation controls, and a scoped note.
- Overlap checked through PR854, all open PR titles and relevant bodies.
  #844 changes R439 block 4 with fixed-factor destination-once optimization;
  #810 changes historical R420 block 8; #728/#792 change R439 A mini-nodes;
  #827 concerns cleanup frames, not scalar factorization. This investigates a
  different whole-block search class on the punctured word, imports none of
  those pending implementations, and will not add their savings to ours.
- Selected result: #799 with #589, conditional kappa 0.001661634653669567.
  This experiment claims no new kappa and will not edit the selection.

## Result update

The 5,000-trial strict search produced no shorter reverse-dominated circuit
among its 333 identity factorizations. One pivot kept exactly the same sampled
trajectories and allowed a larger reverse positive bound subject to the full
existing 104-bit native cap. The resulting 40-gate block saves ten ADDs with
cleanup; the native envelope grows from 93 to 94 bits. No moment/kappa change.
The full search coverage, witness, exact controls and replay are packaged here.

Final overlap refresh: all open PR metadata through #856 on 2026-10-13;
#843 (head c99f4478156906c323b1a041f0443f76139d6b6c) changes frame 509,
#844 (dee2c7d506312d2e555a59fb0916c161b4e64028) changes frame 520, and
#848 (510441077c17ad775003b22fca03a519f5330453) is a sharing barrier.
No block-8/frame-523 substitution found. No pinned coordination issue exists
on the final check either. Main remains the exact experimental base.

Submitted result: [PR #857](https://github.com/CrocSwap/integer-mult-bounds/pull/857).
Local and native verification passed; detailed evidence and limitations are in
`VALIDATION.md`. One focused PR submitted; no selected-frontier change or merge.
