# Characteristic polynomial over Q(i) of one eigenvalue-i eigenspace

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

For the historical 8-by-112 centre query, the order-4 signed permutation
`s = (0 4 3 7)(5 6)`, all signs `+1`, preserves the moved 192-dimensional
sign character `eps[1] * eps[2]` of the `c=1` block. The eigenvalue-`i`
eigenspace of `s` on that character is 48-dimensional over `Q(i)` and
`A_1`-invariant. Its monic characteristic polynomial lies in `Z[x]` and is
the explicit degree-48 polynomial in [PROOF.md](PROOF.md). The eigenvalue-`-i`
space of the same character has the same polynomial.

No new kappa. The selected conditional kappa stays `781451/250000000`.

## Result

Write `B = 4 A_1` on the `c=1` block. On this subspace,
`chi_{A_1}(x) = 4^{-48} chi_B(4x)`, and both polynomials lie in `Z[x]`.
The irreducible factorization over `Q(i)` is

```text
x^10 (x-2)^5 (x+2)^5
  (x^3 - 8x^2 + 4x + 32)
  (x^3 - 12x - 8)
  (x^3 - 12x + 8)
  (x^3 + 8x^2 + 4x - 32)
  (x^8 - 6x^7 - 56x^6 + 296x^5 + 704x^4 - 3264x^3 - 1728x^2 + 7296x - 3072)
  (x^8 + 6x^7 - 56x^6 - 296x^5 + 704x^4 + 3264x^3 - 1728x^2 - 7296x - 3072)
```

Ascending coefficient SHA256 values are

```text
chi_A  248dde5357601a63a3e5b548e370f6025e6cc457204723a43413d2eaa79833e3
chi_B  d2d03090e33a628beb31eb51a8f332ec5ccbb18800a56f25186815bde4d81ffd
```

The basis is the least-index unit orbit basis of the character equations and
of `s v = i v`, pinned in [evidence/basis.json](evidence/basis.json).
Coefficients lie in `{±1, ±i}`. The matrix of `B` in that basis is pinned in
[evidence/matrix.json](evidence/matrix.json). Real parts lie in `-16..16`
and imaginary parts lie in `-4..4`. Every irreducible factor of `chi_B`
divides a published `c=1` sector minimal polynomial from
`research/exact-one-slot-gram/CERTIFICATE.json`. That comparison reads
coefficients. It does not replay the degree-881 certificate.

The polynomial is not square-free. Algebraic multiplicity of eigenvalue 0 is
10, and algebraic multiplicity of each of `±2` is 5. The package does not
compute the geometric multiplicity.

The same explicit polynomial is the one open PR #7036 records for the
eigenvalue-`±1` spaces of `eps[5] * eps[6]`. This package recomputes it on
the eigenvalue-`i` space of `eps[1] * eps[2]` and does not rebuild that
matrix.

## Scope

Catalogue card `formal-interface-lemma` asks for a formal caller binding.
The live question is open question 1 of PR #7036: the characteristic
polynomial, over `Q(i)`, of one eigenvalue-`i` eigenspace of `s` on
`eps[1] * eps[2]`. The integer basis in that PR solves only the eigenvalues
`±1`. This package builds a `Q(i)` basis and computes the monic polynomial.

Selected-baseline orientation returned `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`
for kappa `781451/250000000`.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
python3 -B -W error research/c1-moved-48-i-charpoly/verify.py
python3 -B -O research/c1-moved-48-i-charpoly/verify.py
python3 -B scripts/research_package.py --package research/c1-moved-48-i-charpoly --check-only
```

The marker is `PASS_C1_MOVED_48_I_CHARPOLY`. Acceptance uses explicit checks,
so `-O` does not skip a theorem or a rejection control. No Lean, Docker,
degree-881 replay, or selected cold replay was run.

## Overlap

Upstream main was fetched at session start and is
`17469fff78c22941280f04d39dc5a1faee09c840`.
`scripts/find_overlap.py "eigenvalue-i eigenspace" "Q(i) characteristic" "48-dimensional" --offline`
was run on 2026-11-10. Local notes: 10178 of 10178 HEAD paths, complete.
The only local hits are unrelated 48-dimensional lattice notes. The remote
PR and discussion snapshots were not available offline. A GitHub search of
open pull requests and discussions for `eigenvalue-i` returned PR #7036,
which asks this question and computes the eigenvalue-`±1` polynomial, and
PR #7009, which records the multiplicity pattern `48^4` without an
eigenvalue-`i` basis. No fork branch already contained this computation.

## Open next questions

The structured list is in [TASK.json](TASK.json).

- Eigenvalue 0 has algebraic multiplicity 10 on this matrix. The geometric
  multiplicity over `Q(i)` is not computed. This is not the pinned
  eigenvalue-`±1` matrix of PR #7036.
- The eigenvalue-`i` polynomial on the other preserved character,
  `eps[5] * eps[6]`, is not computed.

## Credit

JoyboyBrian's handoff recorded the open decomposition question. PR #7009
recorded `s` and the multiplicity pattern `48^4` without a basis. PR #7036
computed the eigenvalue-`±1` polynomial on this character and left the
eigenvalue-`i` polynomial open. The sign-stabilizer split supplied `g` and
`t`. Ali Romman's PR4958 and PR4720 retain the query and the Bell action.
Nick Petalas's PR5120 is the degree-410 lower bound. Krzysztof Wojt's exact
one-slot package is the degree-881 annihilator and the sector coefficient
list used for the divisibility comparison. The doubled representation comes
from PR1719. New work is Apache-2.0.
