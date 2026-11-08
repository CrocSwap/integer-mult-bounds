# Attribution and exact source provenance

New material is prepared for @CubeJerry with substantial OpenAI assistance
and is offered under the repository's Apache-2.0 license. Mathematical
and implementation predecessors retain their attribution and licenses.
The immutable runtime archives are imported as exact declared inputs;
their embedded source notices are unchanged.

* Nick Petalas, CrocSwap/integer-mult-bounds#4879,
  `research/cycle-schur-optimal-order`: the folded order, single-arc
  bandwidth upper bound and the physical-caller open question.
* Jose Manuel, CrocSwap/integer-mult-bounds#3851 and
  CrocSwap/integer-mult-bounds#3787: unchanged physical `BandedSolve`,
  fixed-tape ownership machinery, signed arithmetic and actual word
  multiplication. All transitive source archives are authenticated by
  the retained `gaussian_sources.py` manifest.
* CrocSwap/integer-mult-bounds#5319,
  `research/schur-boundary-residual`: actual scalar rounding and the
  effective diagonal induced by a stored reciprocal.
* JoyboyBrian, `research/old-h-rounded-schur-lu-growth`: the retained
  generic row-gap, row-mass and exact factor-growth argument. Its sharper
  M/d bound is reused, not claimed as new.
* The retained `rational-unitary-fft` Reference and
  `certified-gaussian-recovery` interval algorithms, with Jose Manuel,
  Mason Hale and their credited original Gaussian lineage. Their
  numerical function bodies are not modified by the adapter.

All live executed source files and immutable archives have base-commit,
Git-blob and SHA256 pins in `SOURCES.json`. The historical mathematical
notes and frozen task/selected record are separately marked provenance.
The exact canonical base is
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`.

`reference_source.py` is byte-identical to the source adapter previously
published by @CubeJerry in `research/shrinking-reference-halo/source.py`
at fork commit `a2f3ce7358e8103f6eccd404e594276e9ccc04d8`. Its SHA256 is
`20c0fb2e4aa95de976ef6ce74ded4bf1cb9073732eca7eda8f61e45d239afa2c`.
This is contextual reuse attribution, not an assertion that that fork
commit is an ancestor of the canonical base. The adapter's copied bytes
are part of this package, while every numerical source it executes is
separately pinned to canonical input bytes. Its constructor/entry domain
does not include the unrelated `Reference.for_cap` compiler interface.

The separately authored numerical reviewer supplied
`allocation_review.py` and its written allocation/source analysis. The
separately authored physical reviewer supplied `independent_physical.py`
and its transport/ownership analysis before assisting final integration.
Both are source-aware AI checks; neither is presented as independent
human or formal-kernel acceptance.
