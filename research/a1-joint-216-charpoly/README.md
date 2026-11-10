# Characteristic polynomial of one A_1 joint eigenspace

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

For the historical 8-by-112 centre query, the joint `(+1,+1)` eigenspace of
the `c=1` sign stabilizer and the two involutions `g` and `t` is a
216-dimensional `A_1`-invariant subspace. Its monic characteristic polynomial
in characteristic zero is the explicit degree-216 polynomial in
[PROOF.md](PROOF.md). The same polynomial is the characteristic polynomial on
each of the four joint sign spaces.

No new kappa. The selected conditional kappa stays `781451/250000000`.

## Result

Write `B = 4 A_1` on the `c=1` block. On this subspace,
`chi_{A_1}(x) = 4^{-216} chi_B(4x)`, and both polynomials lie in `Z[x]`.
The irreducible factorization begins

```text
x^24 (x-2)^12 (x+2)^12 (x-6)^2 (x+6)^2 (x^2-2x-4) (x^2+2x-4)
```

and continues with the paired degree 11, 14, and 16 factors printed by the
verifier and copied in [PROOF.md](PROOF.md). Ascending coefficient SHA256
values are

```text
chi_A  18114a297071c454cb935ef85cab42a745954fb065be2a6d7e4ff23ef26b771b
chi_B  ec79276843b69dc6e064cdcb009a238e8231d0a8bf8f9c532c679c6a0cb6a81e
```

The basis is the least-index signed orbit basis of the joint `+1` equations,
pinned in [evidence/basis.json](evidence/basis.json). The integer matrix of
`B` in that basis is pinned in [evidence/matrix.json](evidence/matrix.json).
Every irreducible factor of `chi_B` divides a published `c=1` sector minimal
polynomial from `research/exact-one-slot-gram/CERTIFICATE.json`. That
comparison reads coefficients. It does not replay the degree-881 certificate.

Because `x` and `x-2` both divide `chi_{A_1}`, this 216-dimensional space has
a proper nonzero `A_1`-invariant subspace. The package does not construct that
subspace and does not search a centralizer.

## Scope

Catalogue card `formal-interface-lemma` asks for a formal caller binding.
The live question is the characteristic polynomial left open by the
sign-stabilizer split, discussion comment
[19144258](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19144258)
and the fork note on that split. The predecessor constructed the dimension
216 without a basis or a matrix. This package computes one polynomial.

Selected-baseline orientation returned `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`
for kappa `781451/250000000`.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
python3 -B -W error research/a1-joint-216-charpoly/verify.py
python3 -B -O research/a1-joint-216-charpoly/verify.py
python3 -B scripts/research_package.py --package research/a1-joint-216-charpoly --check-only
```

The marker is `PASS_A1_JOINT_216_CHARPOLY`. Acceptance uses explicit checks,
so `-O` does not skip a theorem or a rejection control. No Lean, Docker,
degree-881 replay, or selected cold replay was run.

## Overlap

`scripts/find_overlap.py` was run on 2026-11-10 against upstream
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Coverage: local notes 8917 of
8917 HEAD paths, complete; 885 open PRs, pagination complete, fetched
2026-11-10T02:07:47Z; 6934 discussion records, pagination complete, fetched
2026-11-10T02:08:41Z. The phrases `216-dimensional` and `216-by-216` matched
nothing. `degree-881` matched the sign-stabilizer finding, which records the
dimension and does not compute this polynomial, and
`research/equal-bell-two-slot-spectrum/`, which is a different operator.
No open PR computes this characteristic polynomial.

## Open next questions

The structured list is in [TASK.json](TASK.json).

- The unique 32-dimensional `c=1` character also splits into four spaces of
  dimension 8. Their characteristic polynomial is a different computation.
- Eigenvalue 0 has algebraic multiplicity 24. The geometric multiplicity on
  this pinned matrix is not computed here.

## Credit

JoyboyBrian's handoff recorded the open decomposition question. The
sign-stabilizer split supplied the involutions `g` and `t` and the dimension
216, without a basis. Ali Romman's PR4958 and PR4720 retain the query and the
Bell action. Nick Petalas's PR5120 is the degree-410 lower bound. Krzysztof
Wojt's exact one-slot package is the degree-881 annihilator and the sector
coefficient list used for the divisibility comparison. The doubled
representation comes from PR1719. New work is Apache-2.0.
