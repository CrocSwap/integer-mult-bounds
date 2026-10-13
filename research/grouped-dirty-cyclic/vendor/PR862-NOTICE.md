# Attribution and scope

New contribution by Chafik Boukhalfa (@chafreaky), prepared with substantial
OpenAI Codex assistance, under the repository's Apache-2.0 license.

- Ali Romman (@aliromman), PR621 at
  `520774462b19b29af41554b74def31f9d01e997e`: prime-power kernel, circle
  lower bound and length-uniform inverse bound. Its notice is retained.
- Chafik Boukhalfa (@chafreaky), PR628 at
  `0768f97d06c623b8211e651543c66135796b62bf`: stable cyclic scan, rounded
  execution, preparation and phase arguments, exact kernel fixtures and
  earlier dirty-shear construction. Its notice is retained.
- The classical Mahler-measure bound, periodic filtering and approximate
  factorization methods are not claimed as new. The source-recovery and
  complementary-factor accounting are the contribution of this package.
- Pan's factorization bound is cited through Mehlhorn, Sagraloff and Wang,
  *From Approximate Factorization to Root Isolation with Application to
  Cylindrical Algebraic Decomposition*, Theorem 2 and Corollary 1,
  https://arxiv.org/pdf/1301.4870, PDF page 8. The inherited fast elementary
  function reference and original kernel attribution remain in PR628's note.

PR846 by Rohan Guliani and PR764 by Charles Bethin are discussed only as
related stride and rounding work. No source from either is consumed here;
their arbitrary-stride or sharper local bounds are not prerequisites of
this package's claims.

The dense oracle is a separate implementation in the same package. No
independent human or delegated-agent review, formal verification, practical
speedup, literature priority, complete multiplication theorem or new kappa
is claimed. The reserved low bits are part of the source contract; arbitrary
dirty storage and common-label/Clifford realization are not supplied.
