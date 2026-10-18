# Attribution

Prepared for Ali Romman (@aliromman) with substantial OpenAI Codex assistance.
New code, tests and documentation use the repository's Apache-2.0 license.
No independent human review is claimed.

- Charles Bethin (@cbethin), PR662, supplied the exact permutation and phase
  tables. This package imports those tables unchanged and compares against
  his complete dense evaluator. PR662 head:
  `458744109003e0958798f27c1f04be78f03663ce`.
- The Gaussian-dyadic algebra and lowering come from the retained
  `clifford_exact.py`. `lowering.py` adapts its `monomial` and `lower_child`
  routines to take an evaluator argument. `run.py` adapts `phases_full.py`.
  The latter credits icekylinx and the PR425 ancestry, with Codex assistance.
  The PR531 license and notice remain at
  `research/complex-k492-owner-repair/vendor/multicold/vendor/pr558/vendor/pr552/complex-global/vendor531/`.
  Those files retain the upstream contributor and AI-assistance notices.
- Jonathan Capalbo's PR942 supplies the retained U8 replay archive used by
  the benchmark. Its head is
  `1960cfa919a0945d0ca4cb14ea96237000037903`.
  The U8 word comes from the PR869/870 lineage, which credits NewBArch's
  triangle-hybrid construction and ColdWitness/icekylinx's driver, on Jeremy
  Kothe's PR799 X4 work. Chafik Boukhalfa's PR741/890 work and Hao Yan's
  PR858 work remain credited in the retained package notices.

The new contribution is the sparse state update, its explicit compiler
entry point, and the complete U8 comparison with corruption controls and
time/memory measurements. Sparse state propagation is an established general
technique; this package makes no priority claim for that technique.

The package does not change frozen source files, accepted certificates,
`upstream/`, or the default selected replay. All inherited compiler,
realization, hosting, precision, tape and analytic obligations remain.
