# Attribution and scope

The averaged-height estimate and its integration with the explicit
precision budget were prepared by Chafik Boukhalfa (@chafreaky), with
substantial OpenAI Codex assistance. Apache-2.0, as in the repository.
No literature-priority, independent human review, delegated-agent review
or full formal-verification claim is made.

- Ali Romman (@aliromman), PR621, head
  `520774462b19b29af41554b74def31f9d01e997e`: the prime-power ideal
  argument, nonzero resultant, cofactor/circle estimate, Fourier inverse
  bound and rational field checker. Its proof, notice and two checkers
  are retained byte for byte. The new `resultants.py` adapts the independent
  SymPy checker's field and Sylvester constructions, and compares a
  polynomial resultant with the retained rational-field computation.
- Chafik Boukhalfa, PR628, head
  `0768f97d06c623b8211e651543c66135796b62bf`: coefficient preparation,
  root-margin framework and rational interval kernel. Its proof, notice
  and interval implementation are retained. The new interval checker sets
  its documented module precision to 192 bits, and adds outward rational
  logarithm and square-root bounds.
- Chafik Boukhalfa, PR862, head
  `57e0659150d323b784580110b36aa64a2dca2a33`: the common-operator
  complementary-factor bound and explicit cubic precision budgets.
  Its proof and notice are retained.
- Chafik Boukhalfa, PR977, head
  `2846af720af190cb75b45ebddbb0357dec1121ec`: effective nonzero depth
  for the original PR846 stride solver and its cubic-budget integration.
  Its proof, notice and budget code are retained. `budgets.py` adapts those
  formulas to the new circle exponent. `verify.py` and `test_package.py`
  adapt that package's source binding, receipt comparison and relocation
  harness. Rohan Guliani's PR846 arbitrary-stride Euclidean solver and
  Charles Bethin's PR764 shared-suffix estimate remain credited through
  the retained notice; no new solver execution is claimed here.

The kernel comes from the pinned OpenAI exact-DFT manuscript, with its
classical Newton/q-Pochhammer factorization provenance retained in PR621's
notice. The logarithm Fourier series, geometric sums, Hadamard inequality,
algebraic norm, Mahler-measure argument, approximate factorization and fast
arithmetic remain classical ingredients. The new proof is self-contained
for its averaged-height estimate and does not infer a finite rational-unit
bound from an irrational Sudler-product theorem.

All retained files have immutable Git-blob and SHA256 pins in
`SOURCE-PINS.json`. Existing notices and licenses are unchanged. This
contribution improves a sufficient precision theorem; it does not resolve
the full-transform, common-label, Clifford, physical hosting or complete
multiplication obligations, and it makes no new kappa claim.
