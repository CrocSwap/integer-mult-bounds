# Exact factor-one rational Stein generators

Scoped written proof with exact finite corroboration. For every rectangular
Gaussian-rational matrix E of rank r, the new construction gives

    E = sum_(j=1)^s g_j a_j,     s <= 2r,
    ||g_j||_2 <= 1,             ||a_j||_2 <= ||E||_2.

The columns form a rational Parseval frame for col(E), and a_j=g_j*E.
This improves the coefficient norm contract of Jose Manuel's
[PR4198](https://github.com/CrocSwap/integer-mult-bounds/pull/4198)
from a factor below two to exact factor one by permitting extra terms.
Nick Petalas's [PR6228](https://github.com/CrocSwap/integer-mult-bounds/pull/6228)
already approaches one with r terms. Its fixed-term normalizer is not
used here. No new kappa is claimed. The standard coordinate factorization already
gives the unit bounds with m terms; this construction bounds the count
by 2r independently of the ambient row dimension m.

The new step represents each rational residual norm as the sum of two
Gaussian-rational squared norms, then splits its orthogonal projector.
The rational residual interface and Stein/dirty-shear identities are
credited to PR4198; Lagrange's four-square theorem is classical.
[PROOF.md](PROOF.md) gives the arbitrary-dimensional argument and limits.

## Evidence

The verifier passes 414 matrix fixtures, containing total rank 698 and
901 emitted terms. Exactly 123 fixtures use extra terms. It checks 2,048
positive integer square decompositions and seventeen rejection controls.
For E=(1,1,1)^T, it emits two terms with squared column norms 1/3 and 2/3
and squared row norms 1 and 2. The exact matrix norm squared is three.

The standalone checker independently row-reduces every input, reconstructs
every matrix entry, checks the full Parseval projector and verifies
E*E-a_j*a_j is positive semidefinite by exact Hermitian elimination.
It also checks the complete two-square preference against a separate
small enumeration. Counts and the explicit rank-one witness are emitted
by the verifier, with hashes of every package source file. No receipt is
handwritten and no predecessor scientific verifier is executed.

## Reproduce

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/exact-unit-stein-splitting/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/exact-unit-stein-splitting/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/exact-unit-stein-splitting
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/exact-unit-stein-splitting --check-source-history
```

Any CPython 3.12 path can replace the local interpreter. Expected markers
are PASS_EXACT_UNIT_STEIN_SPLITTING, PASS_REGISTERED_RESEARCH_PACKAGE and
PASS_RESEARCH_COMMIT_BYTES. The default replay is read-only. Optional
`--receipt /absolute/new/path.json` writes a source-bound receipt and
refuses to overwrite an existing file.

## Limitations

The written theorem has arbitrary finite dimensions. The executable
accepts dimensions at most eight, component height at most 256, and
primitive residual squared norm at most 65,536. It rejects exhaustion.
Its exhaustive integer-square search is not a polynomial bit-time claim.
The 2r term bound is not claimed optimal. Additional compensated macros
may outweigh the smaller coefficients. No physical precision or supplier
saving, complete multiplier, human review or formal-kernel acceptance is
claimed. All five framework assumptions remain.

## Open next questions

- Can a rational Parseval construction always use fewer than 2r terms?
  Start with the embedding of a rank-two rational Hermitian form into a
  three-coordinate standard form. This could reduce the added macros;
  arbitrary rational-form embedding and its preparation costs are open here.
- Can an actual rounded child benefit after all extra terms are charged?
  Start with one emitted tuple and its full compensated execution, including
  coefficient preparation, rounding and delivery. The physical contract
  and full caller invoice are missing. AAAmirinu's
  [PR6239](https://github.com/CrocSwap/integer-mult-bounds/pull/6239)
  already cautions that a smaller coefficient row alone need not reduce
  child precision.

This contribution was produced by Nick Petalas. Credit Jose Manuel /
jmbarrancoml and Vlado Vojdanovski for the residual and dirty-shear compiler,
Cinna Davis and the retained Gaussian/phase/caller authors, and classical
Gram-Schmidt and four-square theory. Apache-2.0.
