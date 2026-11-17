# Polynomial direct generation of two-capacity completions

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped constructive proof with exact finite corroboration.
For arbitrary subspaces A,B,C,D in n-dimensional finite-field spaces, the
package constructs every invertible map g satisfying g(A) contained in C
and g(B) contained in D exactly once from an integer index. It decodes
one index with O(1+n^5) field operations and O(1+n^4) integer arithmetic
operations. Uniform indices therefore give exactly uniform completions.
No injection is prescribed. Nonzero prescribed images remain open here.

The construction makes the quotient factors in
[Ali Romman's PR6539](https://github.com/CrocSwap/integer-mult-bounds/pull/6539)
directly executable for this subclass. Its count theorem is a cited input,
not a result re-audited by this package. The older
[PR6607](https://github.com/CrocSwap/integer-mult-bounds/pull/6607) samples
the more general prescribed-injection contract through an exponential
candidate-image scan. Its self-reduction and code are not used here.
Classical subspace, graph-map and basis-extension methods retain credit;
no general literature-priority claim is made.

[PROOF.md](PROOF.md) proves the bijection, uniformity and resource bounds.
[unrank.py](unrank.py) implements the direct decoder and a bounded entropy
interface. [linear.py](linear.py) supplies exact row reduction and canonical
complements. The executable accepts n<=12, prime q<=31, and F4 represented
by F2[t]/(t^2+t+1). The written construction applies to every finite field
with an exact arithmetic interface and a fixed element ordering.

For N>0 completions, set b=ceil(log2 N). A batch of R independent uniform
b-bit blocks has exact exhaustion probability (1-N/2^b)^R. Conditional on
success, each completion has probability 1/N. The finite API accepts R<=64,
validates the whole batch and provisions Rb bits. It reports the acceptance
position separately. There is no hidden random source. The corresponding
online method uses fewer than 2b expected fair bits when N>1. At N=1, no
random bits are needed. Empty sets are rejected for sampling.

## Evidence and reproduction

The verifier compares complete decoded endpoint sets and collision counts
with literal matrix enumeration. It covers every ordered quadruple of
subspaces over F2 at n=0,1,2, and over F3/F4 at n=1. Further selected
fixtures cover F3/F4/F5 at n=2 and F2 at n=3, including a two-branch
crossed-plane contract. Component checks enumerate all Grassmann and
ordered-injection indices through dimension three over F2/F3/F4.
Sixteen selected indices in dimensions 8,10,12 satisfy their full endpoints.
These are selected large examples, not large exhaustive censuses.

For GL2(F2), all 64 pairs of three-bit blocks produce ten occurrences of
each of six matrices and four exhausted pairs. Singleton and zero-attempt
cases are checked. Invalid field orders, dimensions, vectors, indices,
empty sampling and entropy limits are rejected. Checks use ordinary
exceptions and remain enabled under optimized Python.

From the worktree root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/two-capacity-direct-unranking
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/two-capacity-direct-unranking --check-source-history
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/two-capacity-direct-unranking/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/two-capacity-direct-unranking/verify.py
```

Another CPython 3.12 installation may replace the absolute interpreter path.
Expected marker: `PASS_TWO_CAPACITY_DIRECT_UNRANKING`. Each registered
command has a 240-second timeout. Default execution writes only stdout.
Optional `--receipt /absolute/scratch/result.json` writes a generated
receipt outside the checkout, bound to package and predecessor-input hashes.
No receipt is handwritten or committed.

For an API example, put this package on the Python import path:

```python
from unrank import Contract

contract = Contract(2, 2, (), (), (), ())
matrix = contract.decode(4)
sample, acceptance_position_bits = contract.sample((7, 4))
assert sample == matrix and acceptance_position_bits == 6
```

Maps are tuples of their standard-domain column vectors. Inputs are ordered
lists of canonical coordinate vectors; redundant rows are reduced. The API
normalizes input subspaces and fixes all later complements deterministically.

## Sources and limits

The immediate mathematical predecessor is Ali Romman's PR6539 and its
quotient/lift count. Its proof at canonical base
e54523517d0f03e58352e647c403a5af3e525a57 is a hash-bound declared input in
[SOURCES.json](SOURCES.json). It is read for attribution and hypotheses;
no predecessor scientific executable is imported or replayed. Credit ToikY
PR6535 for coupled quotient feasibility; Ali Romman PR6533 for general
capacity rank counts; Nick Petalas PR6489/4919 and PR6607 for the prior
nested/general sampling work; Brian/JoyboyBrian PR5020, Cao Yifan/intqwq
PR4610, codyw912 PR4735, and the retained Cinna Davis, Dugongue, zxv and
Jacob Alan Sussman lineage. Existing predecessor notices remain unchanged.

The code has no recursion and no function longer than 60 lines.
All production loops are bounded by the enforced dimensions or 64 entropy
blocks. Python managed allocation and bigint/field arithmetic are explicit
deviations from fixed-allocation low-level rules. Production working memory
is O(1+n^2) field elements plus O(1+n^3 log q) bits, including stored branch
weights. The verifier separately enumerates finite endpoint sets and retains
them for collision checks. Its largest component class has 181,440 members.
Ordinary Python method dispatch has the fixed visible targets in these three
files. Warning-strict ordinary and optimized execution are the diagnostics.

This is unrestricted GL generation. There is no actual native contact,
symplectic or signed-phase constraint, physical randomness source, legal
access schedule, dirty restoration, precision, stock, tape, compiler or
outer invoice. The five selected framework assumptions remain. No new
kappa, supplier admission or complete multiplication theorem follows.
Independent human and formal proof-kernel review are unclaimed.

The formal-interface-lemma card changes scope to this finite-field
construction. Selected #7000 and its kappa are unchanged. The current
selected-baseline binding check passed; no selected scientific cold replay,
Lean, Docker or predecessor verification suite ran.

## Open next questions

1. Can the direct polynomial decoder handle a nonzero prescribed injection?
   Start with the common lift subject to the quotient discrepancy in PR6539.
   Compatible affine representatives and their unique inverse decomposition
   are the missing step. The exponential general sampler remains available.
2. Can one actual shared native contact use these samples with a favorable
   complete bill? Extract its two capacities and chronological bases first.
   Signed/symplectic realization and physical costs remain blockers.
