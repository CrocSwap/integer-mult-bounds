# Characteristic polynomial of one 48-dimensional eigenspace of s

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

For the historical 8-by-112 centre query, the order-4 signed permutation
`s = (0 4 3 7)(5 6)`, all signs `+1`, preserves two moved 192-dimensional
sign characters of the `c=1` block. On the character `eps[1] * eps[2]`, the
eigenvalue-`+1` eigenspace of `s` is 48-dimensional and `A_1`-invariant. Its
monic characteristic polynomial in characteristic zero is the explicit
degree-48 polynomial in [PROOF.md](PROOF.md). The eigenvalue-`-1` space of
the same character has the same polynomial. The other preserved character,
`eps[5] * eps[6]`, has a different degree-48 polynomial, also recorded there.

No new kappa. The selected conditional kappa stays `781451/250000000`.

## Result

Write `B = 4 A_1` on the `c=1` block. On the canonical subspace,
`chi_{A_1}(x) = 4^{-48} chi_B(4x)`, and both polynomials lie in `Z[x]`.
The irreducible factorization is

```text
x^10 (x-2)^6 (x+2)^6
  (x^5 - 4x^4 - 24x^3 + 80x^2 + 80x - 160)
  (x^5 + 4x^4 - 24x^3 - 80x^2 + 80x + 160)
  (x^8 - 4x^7 - 72x^6 + 240x^5 + 784x^4 - 2208x^3 + 1920x - 768)
  (x^8 + 4x^7 - 72x^6 - 240x^5 + 784x^4 + 2208x^3 - 1920x - 768)
```

Ascending coefficient SHA256 values are

```text
chi_A  1230f7227b6cbd0ad1383273a601bb4f517462ca663235c673e6b6bb13f1b3af
chi_B  7505211cf6196c312dd5afce7307eb5ec8f63b89cfe0bd73463f9d5352535d7e
```

The basis is the least-index signed orbit basis of the character equations
and of `s v = v`, pinned in [evidence/basis.json](evidence/basis.json). The
integer matrix of `B` in that basis is pinned in
[evidence/matrix.json](evidence/matrix.json). Every entry lies in `-16..16`.
Every irreducible factor of `chi_B` divides a published `c=1` sector minimal
polynomial from `research/exact-one-slot-gram/CERTIFICATE.json`. That
comparison reads coefficients. It does not replay the degree-881 certificate.

Because `x` and `x-2` both divide `chi_{A_1}`, this 48-dimensional space has
a proper nonzero `A_1`-invariant subspace. The polynomial is not square-free,
so it is not the minimal polynomial of the restriction. The package does not
construct the subspace and does not search for a signed permutation outside
the centralizer of `s`.

## Scope

Catalogue card `formal-interface-lemma` asks for a formal caller binding.
The live question is open question 2 of the moved-character split, PR #7009:
the characteristic polynomial of one 48-dimensional eigenspace of `s` on a
moved 192-character. This package computes that polynomial for the real
eigenvalue `+1` on the character `eps[1] * eps[2]`, and compares the other
three real eigenspaces. It does not compute an eigenvalue-`i` polynomial.

Selected-baseline orientation returned `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`
for kappa `781451/250000000`.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
python3 -B -W error research/c1-moved-48-charpoly/verify.py
python3 -B -O research/c1-moved-48-charpoly/verify.py
python3 -B scripts/research_package.py --package research/c1-moved-48-charpoly --check-only
```

The marker is `PASS_C1_MOVED_48_CHARPOLY`. Acceptance uses explicit checks,
so `-O` does not skip a theorem or a rejection control. No Lean, Docker,
degree-881 replay, or selected cold replay was run.

## Overlap

`scripts/find_overlap.py "48-dimensional eigenspace" "moved 192" --offline`
was run on 2026-11-10 against upstream
`17469fff78c22941280f04d39dc5a1faee09c840`. Local notes: 10178 of 10178 HEAD
paths, complete, no matches. The remote PR and discussion snapshots were not
available offline. A GitHub search of open pull requests and discussions for
`48-dimensional eigenspace` returned only PR #7009, which asks for this
polynomial and does not compute it. Merged PR #6964 is the 216-dimensional
joint eigenspace of `g` and `t`, a different subspace. This package does not
recompute that polynomial.

## Open next questions

The structured list is in [TASK.json](TASK.json).

- The eigenvalue-`i` and eigenvalue-`-i` spaces are 48-dimensional over `C`.
  Their characteristic polynomials are not computed here.
- Eigenvalue 0 has algebraic multiplicity 10 on the canonical matrix. The
  geometric multiplicity is not computed here. This is not the 216-by-216
  matrix of PR #6964.

## Credit

JoyboyBrian's handoff recorded the open decomposition question. PR #7009
recorded the order-4 splitter `s`, the multiplicity pattern `48^4`, and the
open polynomial question, without a basis. The sign-stabilizer split supplied
`g` and `t`. The characteristic-polynomial method follows the 216-dimensional
computation in `research/a1-joint-216-charpoly/`, on a different space. Ali
Romman's PR4958 and PR4720 retain the query and the Bell action. Nick
Petalas's PR5120 is the degree-410 lower bound. Krzysztof Wojt's exact
one-slot package is the degree-881 annihilator and the sector coefficient
list used for the divisibility comparison. The doubled representation comes
from PR1719. New work is Apache-2.0.
