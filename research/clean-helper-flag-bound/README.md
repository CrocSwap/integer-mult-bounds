# Clean helper registers preserve the common-flag span bound

A scoped written proof shows that, in the rational scalar-idempotent model of PR6338, `t` invertible data targets and any number of clean identity helpers need at least `mt` paid calls when the frame span has dimension at most `m+1` and the data-target ratios share a complete rational flag. Diagonal data targets attain the bound with `mt` calls and span `m`. The result extends PR6338's non-two-support cases to its remaining two-support case under the common-flag hypothesis. It gives no new κ.

The new step is a flag count with zero helper blocks. The upper-entry projection has identity output, while the diagonal projections have rank `t`. Their scalar rank inequalities force at least `2t` calls on the two-dimensional block. The one-dimensional blocks each need `t`. [PROOF.md](PROOF.md) gives the argument and states the exact hypotheses. The executable finite examples corroborate it; they do not formally certify the universal proof.

From the repository root, with CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/clean-helper-flag-bound/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/clean-helper-flag-bound/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/clean-helper-flag-bound
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/clean-helper-flag-bound --check-source-history
```

Use a local CPython 3.12 executable in place of the absolute path on another machine. The checks use exact finite group-algebra arithmetic, not a physical bit supplier. Common-flag hypotheses, clean helper restoration, and the span bound are essential parts of the claim. No complete multiplication theorem, physical schedule, native or compiler admission, or independent human or formal proof-kernel review is claimed.

## Open next questions

- Can the two-dimensional block bound be proved without a common rational flag? Start with two data matrices whose relative matrix has irreducible quadratic characteristic polynomial and keep helper outputs at zero. The upper-entry projection then need not have identity output.
- Can dirty monomial helper exponents be admitted when their upper-entry projections vanish? Start with the same inequalities and account for their potentially nonzero diagonal projections. Arbitrary helper blocks can make the upper projection nontrivial.

## Credit

This contribution was produced by Nick Petalas. Eumemic's PR288 supplies the model; Ali Romman's PR468 supplies the normalization, projections and original flag inequality. PR5988 supplies the all-dimensional support split. Unpaidmoon's PR6338 supplies the clean-helper question and the non-two-support cases. Ali Romman's PR4961 already proves the stronger unrestricted-span result for three lower-triangular 3-by-3 data targets and one returned register. Unpaidmoon's PR4118 proves a partial span-four result for dirty auxiliaries. These results are inputs, not audit targets. Apache-2.0.
