# Sources and attribution

- Ali Romman, with substantial OpenAI Codex assistance,
  [PR #7692](https://github.com/CrocSwap/integer-mult-bounds/pull/7692),
  head `c2870a38841f515db7203a0761cd77f014f7fb7a`:
  the [matching proof](https://github.com/aliromman/integer-mult-bounds/blob/c2870a38841f515db7203a0761cd77f014f7fb7a/research/edge-matching-image-bound/PROOF.md)
  gives the upper bound, disjoint diagonal relations, binary fibers,
  pair/triple blocks and the universal extremal family. The proof was read.
  It is a mathematical premise; the complete predecessor suite was not run.
- Ali Romman, with substantial OpenAI Codex assistance,
  [PR #7703](https://github.com/CrocSwap/integer-mult-bounds/pull/7703),
  head `2523029b27d40526b811591ce0fb85f9bc1b1df7`:
  the [proof](https://github.com/aliromman/integer-mult-bounds/blob/2523029b27d40526b811591ce0fb85f9bc1b1df7/research/edge-matching-equality-classification/PROOF.md)
  classifies first equality and gives the sharp odd-difference maxima.
  Its [checker](https://github.com/aliromman/integer-mult-bounds/blob/2523029b27d40526b811591ce0fb85f9bc1b1df7/research/edge-matching-equality-classification/verify.py)
  supplies the adapted binary matrix, basis, pattern-lift, matching, orbit
  and old-core functions. Both files were read. No prior receipt is relabelled
  as a new result. The full predecessor suite was not rerun.
- Nick Petalas,
  [PR #6785](https://github.com/CrocSwap/integer-mult-bounds/pull/6785),
  head `5dbf2c05220bea53d84b510efe5910c4cec8f182`:
  the [one-edge proof](https://github.com/petalas/integer-mult-bounds/blob/5dbf2c05220bea53d84b510efe5910c4cec8f182/research/one-edge-pattern-reducibility/PROOF.md),
  Git blob `f3e5ddb24517bebacac04442c856aec7dd2f4b40`, gives the upper bound
  four at (k,nu)=(3,1) and explicitly leaves attainment open. It was read;
  its width-five/six census was not rerun. The new two-link family attains
  that bound as one special case.
- unpaidmoon, with substantial Cursor Grok assistance,
  [PR #7094](https://github.com/CrocSwap/integer-mult-bounds/pull/7094),
  head `b5f0a0df3d22e8ad40d67d6be4d1c7ff24d180c5`:
  the [proof](https://github.com/unpaidmoon/integer-mult-bounds/blob/b5f0a0df3d22e8ad40d67d6be4d1c7ff24d180c5/research/no-edge-dim4-image-five/PROOF.md),
  Git blob `b2350589eeed011640caebd3b66f0cbb70639a83`, already attains
  (k,nu,n)=(4,0,5) with a five-member complete pool. The proof was read;
  that literal pool is checked as a source comparison. The full source
  suite was not run. The current six-member family does not claim first
  attainment of that instance. Retain the source's earlier four-cycle
  [PR #6962](https://github.com/CrocSwap/integer-mult-bounds/pull/6962)
  and normal-triple [PR #6921](https://github.com/CrocSwap/integer-mult-bounds/pull/6921)
  credit. The latter's pinned proof at
  `6020400853abc110134804fad04b695adc360bcd` was read for overlap; its full
  theorem is not used as a premise here.

The cited matching proof retains CubeJerry's
[PR #6782](https://github.com/CrocSwap/integer-mult-bounds/pull/6782), its
credit to Nick Petalas for the diagonal-deletion fiber lemma, and the
normal-triple lineage. The odd-difference proof retains unpaidmoon and
Nick Petalas's earlier fresh-link and complete-pool work. Those results
and notices remain credited; they are not new claims here.

The new contribution is the two-link attaining family for all positive even
k-nu, its complete pools including the six-member case, the exceptional
maximum at (2,0), and the zero-difference existence boundary. The odd rows
in the combined maximum table are prior results.

Source and adapted code are Apache-2.0. Prepared by Ali Romman with
substantial OpenAI Codex assistance. Independent human and formal-kernel
review are unclaimed.
