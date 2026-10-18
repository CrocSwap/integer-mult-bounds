# Attribution and license

New refinement, implementation, verification and documentation: Dillon
Amburgey, with substantial OpenAI Codex assistance. Apache-2.0, as in the
repository and the included LICENSE. No independent human review, formal
multiplication proof, practical speedup, or literature-priority claim is made.

- androolloyd, [PR673](https://github.com/CrocSwap/integer-mult-bounds/pull/673)
  at `0e35f56cab3cae1eb0a99447135569d687c5695a`: the general multiway dirty
  echo, its nonlinear restoration proof, inherited precision accounting, and
  `O(n^log_k(4k-4))` call bound. Its exact `echo.py` and `ECHO-PROOF.md` are
  retained in `vendor/pr673`, including the source's OpenAI Codex disclosure.
  This package refines balanced size placement at fanout three and supplies an
  independent free-term/noncommutative audit of the actual pinned generator.
  The echo identity and exponent are predecessor results. This package does
  not review PR673's separate phase-alias repair or κ appendix.
- Chafik Boukhalfa / chafreaky, PR628 at
  `0768f97d06c623b8211e651543c66135796b62bf`: cyclic inverse leaves, rounded
  integer lifts, balanced binary dirty commutator, preparation/precision
  arguments, dense reference solvers, kernel fixtures and executable sources.
  The original notice is preserved at `vendor/pr628/NOTICE.md`; its credits to
  Ali Romman / PR621, the exact-DFT preprint, Alexey Kuznetsov, Pan, Mehlhorn,
  Sagraloff, Wang, Brent and Briand-Davy remain in force. This package does not
  reprove their analytic or algorithmic results.
- 0xkilgore, PR663 at `e0e546fd01b396478c68b6b6c5a16d87515983ba`:
  independent nonlinear restoration audit and the exact binary count
  `3qn-2q²`. The count provides the fair baseline here; the original `4n²`
  allowance is also retained in the precision comparisons. The symbolic
  verifier in this package is separately implemented; PR663 supplies the
  predecessor audit, not proof of the refined instruction schedule.
- Jeremy Kothe, Chafik Boukhalfa and eumemic, #622/#623/#626 and #543, and the
  preceding lineage credited in the selected review: the base repository's
  accepted conditional finite construction. Their multiplier bound is neither
  changed nor newly verified by this package.
- Borrowed-workspace cancellation and ladder methods have substantial prior
  literature. A related quantum setting is Khattar and Gidney,
  [Rise of conditionally clean ancillae for efficient quantum circuit
  constructions, §4](https://arxiv.org/html/2407.17966v2#S4), laddered toggle
  detection. That paper is cited as related work, not as the correctness proof
  or source of the exact eight-call array word retained from PR673. No quantum
  implementation is asserted.

Concurrent PR665 investigates spectral residual splitting and PR666/PR668
verify cyclic certificates/resultants. Those are distinct scopes; none is an
executable dependency of this contribution. Existing scoped negative results
for fixed incidence graphs, grouped frames, and commuting duplicate scalar
gates do not test this change to the product-of-shears composition tree.
