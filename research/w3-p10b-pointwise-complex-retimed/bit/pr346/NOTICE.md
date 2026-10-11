# Attribution and provenance

Prepared with substantial Anthropic Claude assistance. Apache-2.0 (see `LICENSE`) applies to the new code and to the
inherited Apache-2.0 code below; third-party notices are preserved where files are vendored.

- **Base bit word, re-annealed pair module, p = 10 five-stage pipeline and its moment/outer/prime engines**
  (`data/bit/BASE-*`, `data/complex/pm_p10b.json`, `code/pricing/{moment,base_two_moment,outer,prime_witnesses}.py`):
  DreamingOfClouds, PR #325 at `0eca9340a3df6141b8e71a41638c3937b3522888` on PR #315 at
  `64bccfb67494f7c4549bfb2f186b400a3cfefb42` (#285/#276 gen5/gen4 lineage on eumemic's PR168 generator and source527
  package, PR #200's physical rules, hcg890 and Jacob Sussman's five-stage architecture, Evan McKinney's completed
  banks). The engines are copied unchanged from PR #315's package.
- **Design T, twin condensation, the Design T verifier and the cost model** (`code/builders/{interface,gather,build_v5,twin,addcomp}.py`,
  `code/checkers/{verifyT.cpp,sub.hpp,exactnd_h.py}`, `code/pricing/cost.py`): utcorvusvolat-dotcom's w3 supplier work
  (Agents A/B) packaged in PR #310 at `484b85f1d1fada27fda2ddab3ec952c1314d84c7`, ported here to h = 20 (literals 24/23
  replaced by h and h − 1, a `drop` case for gauge-bound partial carriers, configurable paths).
- **Official checkers** (`code/checkers/{legality_h,columns_h}.cpp`): PR #266's `cohort-legality-independent` and
  `cohort-five-stage-columns` as retained in PR #310, with only h, v, R and the copy count generalized.
  `json.hpp`: Niels Lohmann, MIT license in its header.
- **Triple module** (`data/complex/tmod_t2_p10.json`): PR #327 (complex-p10) at `40ed0456ab1990beb3440e61bb883ccf95fdcea4`.
- **Complex chain and checks** (`producer/`, `code/complex/`): PR #304's recipe and PR #315's portable complex checks
  (#256/#233/#202/#200/#194/#184 lineage: icekylinx, Chafik Boukhalfa, Avi Eisenberg, eumemic and others), ported to
  p = 10. Jacob Sussman's `gx.check1`, `gxcore` and pinned Lean sources are vendored unchanged under
  `code/complex/inputs/complex/sources` with their own notices.
- **New here** (Claude-assisted): the exporter, the h = 20 ports, the selection of the complex modules with a
  one-instance compile proxy, the p = 10 complex program and its pins, the tiling/prime/certification helpers and
  `verify.sh`.

Credits do not imply endorsement or review by the credited authors.
