# Rounded child restoration under port borrowing

**Status: scoped obstruction and resource tradeoff. No new kappa.**

A generic same-grid rounded wrapper cannot satisfy PR1057's exact additive
child contract with arbitrarily small uniform error. On a working grid
`delta Z`, additivity forces an integer slope. For the valid PR985 leaf
`x -> 4x/3`, the error is at least `1/3` on the physical interval `[-1,1]`,
independent of the number of guard bits. A coarser source grid, a different
output grid, or a new recursive contract can escape this result.

The [proof](PROOF.md) identifies the precise borrowed boundary. It also
classifies all safe translations of componentwise nearest rounding of
`Pz/q`: they are exactly the integer vectors h with `Ph=0 mod q`.
This gives a sharp saved-residue state count when the old helper cannot
be reread. On a complete residue domain, a diagonal coprime p/q leaf
needs q^L states for length L. For a bounded physical grid, the allowed
source and displacement ranges must contain that complete domain.
The proof explicitly covers reaccess and replay as escapes from that
summary-only bound; it does not claim a general memory lower bound.

A fixed-offset averaging repair needs at least q signed variable calls
to obtain a nonzero additive result. The q-call construction attains the
bound but returns the q-scaled integer map. A separate bounded integer
lift demonstrates the clean precision extension that can make exact
arithmetic safe; its denominator, data widths, initialization, inverse
calls, and accesses are paid.

Run from the repository root with Python 3.9 or newer and the standard
library:

```sh
python3 -I -B research/rounded-borrowing-contract/verify.py
python3 -I -B research/rounded-borrowing-contract/test_package.py
```

The second command runs the first from a read-only copy under optimized
Python and checks three command failures. It prints:

```text
PASS_ROUNDED_BORROWING_CONTRACT ratios=716 responses=3495180 rounded_leaves=380 exact_lifts=22 controls=9
PASS_ROUNDED_BORROWING_PACKAGE controls=3 relocation=1
```

The receipt also covers all 700 normalized functions on the cyclic groups
of orders 2 through 5 at the actual borrowed child boundary, six matrix
quotients, three joint-denominator families, and physical input grids
through 8 fractional bits. These are finite checks of the written proof.
They are not a formal proof of the full multiplication theorem.

The actual PR985 replay uses its nearest rule with ties upward. Its
four-factor rounded witness differs from PR1057's eight-factor arbitrary
nonlinear witness. The witness is supporting evidence; the contribution
is the uniform contract, lattice, and resource results. The complete
literal inverse restores the state even when the positive call changes
a helper, which separates whole-word reversibility from helper restoration.

Experiment base: `abdc6a7002abdbcd9e21bfc5e1a795784deacfdf`.
Dependencies: PR1057 `78a062df1dcab2bffea5ff4d8243f3da6e465414`, PR985
`da1cdf8ed4ac9b1b8378dfec73f77ff4e81a4f70`, and PR1054
`6bc675be1554b3a3be771147f21f9dc2c6dae50a`. Only immutable vendored files
and context copies are hashed; a changing root selected record is not a
runtime input. During this work, main `ba82555c64e1879e4b7decce28186f208fcb8262`
selected PR1042 at conditional `kappa=1672188119205421/10^18`.

See [COVERAGE.md](COVERAGE.md) for the finite domains, check ownership,
limits, and failed approaches. [NOTICE.md](NOTICE.md) preserves predecessor
credit and discloses substantial OpenAI Codex assistance. The selected
frontier and `upstream/` are unchanged.
