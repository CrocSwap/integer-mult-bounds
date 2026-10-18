# Verification bounds and decisions

Build the Lever changed the work from a larger deletion census to a reusable
checker for one counting lemma and its actual weight applications. Prove It
Works required complete receipt equality, losing controls, a separately coded
cover oracle and publication-byte checks. Power of Ten kept loops finite,
checks active under optimization, and generated output outside the checkout.

The code is isolated in this package. `geometry.py` is byte-identical to the
pinned PR3164 source. `beta.py` contains the new inequality, application and
overlap logic. `verify.py` reconstructs data and compares the receipt.
`test_verify.py` tests mathematical inequalities and failure conditions.
No selected result, shared verifier or frozen predecessor changes.

All control flow is structured and nonrecursive. Flat enumeration has exactly
3,309,747 and 788,035 kernels. There are 7,140 root pairs and 120 third-root
candidates per pair; 960 reflection checks; eight-dimensional elimination;
and weight multisets of lengths five through ten over six possible weights.
Quotient covers have at most C(10,5)=252 index choices and 3^5=243 bin
assignments. The independent cover oracle uses at most 2^5 * 2^5 pairs of
subsets. The endpoint-pattern control uses 7^6=117,649 patterns. Registered
commands run sequentially with 120-second bounds. There is no recursive
search, retry loop or background process.

Rule 3 deviation, managed-runtime allocation. Python creates integers, tuples
and Fraction objects during these bounded computations. Avoiding allocation
would require replacing the standard-library implementation. Live geometry is
bounded by 120 eight-dimensional roots, a 120-by-120 Gram table, 512 masks of
112 bits, at most four collections of at most 64 row masks, and 113 histogram
counters. Kernels are processed and discarded. The input has a 2 MB size cap;
the pinned input is 971,985 bytes. New live application data are at most 38
weight tuples of length ten, five result rows and 252 quotient-index choices
streamed from an iterator. Tests use scoped temporary directories. Full replay
and mutation tests exercise the bounds and cleanup. Reconsider a fixed-memory
native implementation only if the fixed problem dimensions grow.

Functions stay below 60 physical lines. Meaningful guards check dimensions,
source bytes, rank inventories, kernel counts, quotient and root thresholds,
original survivors and prior coverage. They use `require` rather than Python
assertions, so optimization does not disable them. Test assertions use unittest.
State is local except read-only module lookup tables. No dynamic evaluation or runtime
code generation is used. Every subprocess used for development is checked;
the retained verifier launches none. Output creation uses exclusive mode.

Rule 9 runtime limitation. Python exposes no C pointer-dereference discipline.
The nearest inspected mechanisms are bounded tuple/list access and direct
function calls; there is no application callback chain or dynamic dispatch.
The unittest framework has a fixed set of sixteen local test methods.

Rule 10 diagnostics limitation. Mathematical and behavioral commands run with
`-W error`; optimization controls retain their guards. Bytecode compilation
checks syntax without writing into the checkout. The registered manifest makes
the real replay recurring. No Ruff, Mypy or Pyright executable is installed;
adding a repository-wide lint policy would exceed this isolated research task.
The follow-up is to include these files in such a policy when adopted.
CHECKS.json records the exact supported diagnostics and environments.

The metric is the number of additional pinned beta shapes excluded, rather
than runtime. All acceptance values are exact integers. DECISIONS.tsv records
the rejected overlap and the original-count versus coordinate-budget attempts.
No noisy timing result or benchmark speedup is claimed. The best remaining
question requires a different quotient-independence argument for `4,5^9`.
