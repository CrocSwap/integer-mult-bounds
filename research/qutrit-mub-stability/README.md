# Square-root stability for complete qutrit MUBs

**Scoped written proof with an exact finite linear-algebra certificate.**
For four unitary 3-by-3 matrices, let Delta be the sum of the 54 squared
unbiasedness residuals. For all sufficiently small Delta,

$$
\operatorname{dist}(U,O)\le (2/\sqrt3)\sqrt{\Delta},
$$

where O is the standard complete family's equivalence orbit, and distance is
the product Frobenius distance. This strengthens the unproved one-quarter
exponent in David Ganz's [atlas B096](../pure-math-atlas-400/volumes/02-geometry.md#b096).
The positive residual threshold is existential and is not computed.

[PROOF.md](PROOF.md) gives the argument. The exact Jacobian has rank 16 on
the 36-dimensional real tangent space. Its 20-dimensional kernel is exactly
the common-unitary and column-phase tangent space. In the Frobenius metric,
all sixteen normal squared singular values are exactly 3. A uniform Taylor
bound in a tubular neighborhood gives the estimate. Brierley, Weigert and
Bengtsson's [complete-family classification](https://arxiv.org/html/0907.4097v2#S2.SS2)
and compactness place every sufficiently small-residual family in that neighborhood.
That classification is cited, not audited as this contribution's deliverable.

The checker uses rational arithmetic in Q(omega), a nonzero determinant
-64/2187, all 1296 entries of K W^{-1} K=3K, the rank-20 equivalence space,
and 972 derivative comparisons in a second tangent coordinate system.
[RESULT.json](RESULT.json) is generated from the checker and binds the proof
and verifier hashes. Optimized relocated CLI controls reject seven source,
receipt, missing-file and mathematical corruptions. They check that successful
replay leaves the exported bytes unchanged.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -Werror -B research/qutrit-mub-stability/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -Werror -B research/qutrit-mub-stability/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -Werror -B research/qutrit-mub-stability/test_package.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/qutrit-mub-stability
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/qutrit-mub-stability --check-source-history
```

On another host, replace the interpreter path with its Python 3.12 executable.
Set TMPDIR to owned external scratch storage for the corruption controls.
Direct verification supports a Git-free export with the declared atlas input
at its repository-relative path. Explicit `verify.py --emit` prints a fresh
receipt; ordinary verification never regenerates it.

## Limits

This is a side result on the atlas's exact numerical repair question. It
assumes already unitary bases and the cited complete-family classification.
It gives no computed epsilon, nearest-family algorithm, nonunitary-input
repair, other-dimensional theorem, physical supplier, new kappa or complete
multiplication theorem. No Lean, Docker or selected-construction cold replay
is needed or claimed. Independent human and formal proof-kernel review are
unclaimed; global literature priority is unclaimed.

Python's managed runtime allocates dynamically. The fixed 3-by-3 field matrices, 54-by-36
Jacobian and at-most-60-by-60 elimination inputs bound live data. The tests
execute only this package's fixed source in a private namespace to construct
corruptions; this is a deliberate metaprogramming deviation. No external code
or variable-size search is accepted. Every function stays below 60 lines.
Warning-strict execution and source compilation are the available diagnostics;
a separate static linter is not installed. No repository-wide configuration
changes are made for this isolated package.

## Open next questions

1. Compute an explicit admissible epsilon. Start with a uniform second-derivative
   bound and a quantitative separation from the complement of the local orbit
   tube. The exact normal singular value is supplied; global separation remains
   the blocker to an effective threshold.
2. Construct a certified nearest-family repair algorithm for unitary inputs.
   Start with a symmetry-fixed local Newton step and prove its convergence
   inside an explicit neighborhood. The present theorem supplies existence,
   not a procedure or an initialization radius.

## Credit

This contribution was produced by Nick Petalas. Credit David Ganz's PR2849
for B096 and its qualitative compactness argument, and Stephen Brierley,
Stefan Weigert and Ingemar Bengtsson for complete-family uniqueness and the
standard dimension-three family. The original atlas and its credits are
unchanged. Infinitesimal rigidity and tubular-neighborhood arguments are
established methods; the contribution resolves this project's stated
quantitative question with the specified exact certificate. Apache-2.0.
