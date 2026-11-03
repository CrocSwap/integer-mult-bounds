# Sharp first-extension degree for an invertible pencil slice

For every prime power q and n >= 1, the exact worst-case least extension
degree admitting an invertible projective slice of a regular n-by-n pencil is

```text
E_q(n) = min { d >= 1 : n < U_q(d) },
U_q(d) = 1 + sum(k=1..d) k I_q(k),
I_q(k) = (1/k) sum(r | k) mu(r) q^(k/r).
```

Here I_q(k) counts monic irreducible degree-k polynomials over F_q.
The extension degree may depend on the pencil. This is a scoped all-prime-power
proof with exact finite corroboration. No new kappa is claimed.

The [proof](PROOF.md) shows that U_q(d) is the minimum dimension of a regular
pencil whose every projective slice is singular over **each** field F_(q^e),
1 <= e <= d. The attaining pencil has one infinity block and one companion
block for every monic irreducible of degree at most d. Extra infinity blocks
give every larger dimension. This is a new field-normalization threshold,
not a recheck of the predecessor decomposition or determinant-image results.

For q=2, the first thresholds U_2(1), U_2(2), U_2(3), U_2(4) are 3, 5, 11, 23.
In particular every regular binary pencil of dimension 9 or 10 has an
invertible slice over some extension of degree at most three. A dimension-five
extremal pencil padded by infinity blocks has first successful degree three,
so the bound is attained. A guarantee in one prescribed degree e instead
requires n < q^e+1. Searching just one larger extension is a different contract:
slice existence need not be monotone in the integer extension degree.

## Evidence and reproduction

Python 3.12 and the standard library suffice. From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/pencil-first-extension-degree/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -W error -B research/pencil-first-extension-degree/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/pencil-first-extension-degree
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/pencil-first-extension-degree --check-source-history
```

Use another CPython 3.12 path on another machine. The direct marker is
`PASS_PENCIL_FIRST_EXTENSION_DEGREE no_new_kappa`. Normal replay writes nothing.
An optional `--receipt /absolute/external/path.json` writes a new JSON receipt
with complete counts, interpreter version and hashes of every package file.
It refuses to overwrite an existing file or write inside the package.

The checker enumerates all nonzero homogeneous binary forms of degrees 1..6
over F2, 1..4 over F3, and 1..3 over F4 and F5. These are **1,707 forms**.
Literal evaluation at every projective point of each tested extension agrees
with a separate divisibility predicate. Each degree's observed maximum
first successful extension equals the formula. Irreducibles are independently
enumerated by trial division and checked against the counting formula and
the complete factorization of x^(q^e)-x.

The **18 literal pencils** cover the threshold dimensions and one padded
dimension for q=2 at d=1..3, and q=3,4,5 at d=1..2. Gaussian elimination checks
**828 literal determinants** against the companion-factor product, including
every projective point in all extension degrees through the first success.
The largest matrix is 27-by-27 and the largest field has 125 elements.
Seven named semantic controls cover infinity, extension escape, the affine
versus projective contract, the union bound, repeated roots, regularity and
nonmonotone extension degrees. Six invalid inputs reject. Explicit exceptions
retain every check under optimized Python.

Finite checks corroborate the written proof. They are not an enumeration of
all pencils, a proof-kernel certificate, or an audit of any predecessor result.
No predecessor executable or scientific suite is imported or replayed.

## Scope and obligations

The pencil is square and regular, so det(xA+yB) is a nonzero homogeneous
polynomial of degree n. Identically singular or rectangular pencils have no
such guarantee. Field existence and the usual finite-field Frobenius theorem
are classical premises; the proof supplies the exact root-union count and
the matrix-pencil attainment. The bounded checker implements q=2,3,4,5 only.

This algebraic normalization can inform exploration of larger native models.
It does not supply a native call, BIT rank saving or a free change of field.
Extension arithmetic, coefficient maps, field descent, original-field SL
transport, arbitrary dirty-state restoration, routing, precision, stock and
the complete supplier invoice remain separate obligations. In particular an
invertible extension slice does not identify the original-field stabilizer.
All five selected framework assumptions remain. No selected cold replay,
native supplier replay, Lean or Docker build was run. Independent human and
formal proof-kernel review are unclaimed.

The task card is explicitly changed from a larger-register call experiment
to this algebraic side lemma. Canonical base is
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision eight, selected
PR6030 at conditional kappa 0.003125804. The selected metadata orientation
passed. The advance [claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19362406)
and local reservation cover this field-avoidance question. Live open/account
PRs, recent claims, main README formula/object searches, merged/general-form
searches and the cached overlap report were checked. Remote pagination was
complete in the cached report; its local-note coverage was sparse. Arbitrary
historical diffs and unpublished work remain outside that coverage.

## Open next questions

- Given a raw regular pencil, can its first successful extension and a literal
  invertible slice be constructed without enumerating all irreducibles through
  the threshold? Start with its homogeneous determinant and missing irreducible
  factors. Efficient witness search and its full arithmetic cost are not
  established by the bounded checker.
- Can an extension-slice normalization help a concrete native producer and
  consumer after field descent and all coefficients are paid? Start with one
  exact pencil, representation and restored-input contract. The present theorem
  supplies no physical implementation or favorable recursive invoice.

## Credit and implementation limits

This contribution was produced by Nick Petalas. Credit Ali Romman / PR5689
for the regular-pencil interface without an invertible base-field slice and
the projective-point family; PR5692 and PR5712 for subsequent raw decomposition
and transport; apoursh / PR5672 for singular-block context; Nick Petalas / PR5250
for the earlier invertible-slice interface; David Ganz's tensor-atlas lineage;
and the retained Kronecker, companion and finite-field literature. Those results
are cited context, not audit deliverables. The new contribution is the exact
first-extension threshold and its all-dimension attainment. Frobenius,
irreducible counts, companion matrices and root counting are classical.
No global literature priority is claimed. Apache-2.0.

The verifier has no recursion and no function above 60 lines. Loops are bounded
by the displayed fixed domains. Python managed allocation is bounded by field
tables of 125 squared entries, matrices of 27 squared entries and polynomials
of at most 126 coefficients. The six invalid-input calls use a
fixed list of functions. Warning-strict normal and optimized execution provide
the available diagnostics; no external static analyzer is configured.
