# Characteristic polynomial of the 84-dimensional X_3=+1 subspace

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

For the historical 8-by-112 centre query, the trivial `(+1,+1)` joint space of
the explicit c=3 pair has dimension 216. The payload involution `X_3` cuts it
into dimensions 84 and 132. On the 84-dimensional eigenvalue-`+1` subspace,
the monic characteristic polynomial of `A_1` in characteristic zero is the
explicit degree-84 polynomial in [PROOF.md](PROOF.md). Its minimal polynomial
has degree 25 and is the product of the distinct irreducible factors.

No new kappa. The selected conditional kappa stays `781451/250000000`.

## Result

Write `B = 4 A_1` on the `c=3` block. On this subspace,
`chi_{A_1}(x) = 4^{-84} chi_B(4x)`, and both polynomials lie in `Z[x]`.
The irreducible factorisation is

```text
x^16 (x-14) (x-12) (x-4)^6 (x-2)^14 (x+2)^14 (x+4)^6 (x+12) (x+14)
  * (x^4 - 16x^2 - 8x + 16)^2
  * (x^4 - 16x^2 + 8x + 16)^2
  * (x^4 - 12x^3 + 20x^2 + 32x - 32)
  * (x^4 + 12x^3 + 20x^2 - 32x - 32)
```

Ascending coefficient SHA256 values are

```text
chi_A  c4bcbd4e52f92d13f3ad451d92c9d22256e7725e4be24ee203bea1c96c129648
chi_B  185b51cfd084f95c1dbd814b0b211ce4ab35b2d59604d7795715d65a0a4e5e65
```

The basis is the least-index signed orbit basis of the joint equations for
`H`, `u`, `v`, and `X_3 = +1`, pinned in
[evidence/basis.json](evidence/basis.json). The integer matrix of `B` in that
basis is pinned in [evidence/matrix.json](evidence/matrix.json). Its entries
lie in `-28..28`, and its trace is 0.

`Z_508` splits the same 84-space into dimensions 42 and 42. The
characteristic polynomial of the `t=0` block is

```text
x^8 (x-14) (x+12) (x-4)^6 (x+2)^6 (x-2)^8
  * (x^4 - 12x^3 + 20x^2 + 32x - 32)
  * (x^4 - 16x^2 + 8x + 16)^2
```

and the `t=1` block is

```text
x^8 (x-12) (x+14) (x-2)^6 (x+4)^6 (x+2)^8
  * (x^4 + 12x^3 + 20x^2 - 32x - 32)
  * (x^4 - 16x^2 - 8x + 16)^2.
```

Every irreducible factor of `chi_B` divides a published `c=3`, `s=+1` sector
minimal polynomial from `research/exact-one-slot-gram/CERTIFICATE.json`.
Those two degree-126 polynomials are part of the certificate whose monic LCM
is the degree-881 minimal polynomial of `B`. The comparison reads
coefficients. It does not replay the degree-881 certificate.

Each rational eigenvalue of `A_1` on this matrix has geometric multiplicity
equal to its algebraic multiplicity: 16 for 0, 14 for each of `±2`, 6 for
each of `±4`, and 1 for each of `±12` and `±14`.

## Scope

Catalogue card `formal-interface-lemma` asks for a formal interface binding.
The live question is open question 1 of
[PR #7020](https://github.com/CrocSwap/integer-mult-bounds/pull/7020),
recorded in discussion comment
[19514155](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19514155).
That pull request proves the trace split and states that the trace formula
does not list a vector. This package builds the basis and computes the
polynomial.

It does not redo the payload-involution split, the signed-permutation
classification, the 16-dimensional or 12-dimensional c=3 polynomials, or the
216-dimensional c=1 polynomial. It does not change the odd signs on the pair.

Selected-baseline orientation returned `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`
for kappa `781451/250000000`.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
python3 -B -W error research/c3-x3-plus-charpoly/verify.py
python3 -B -O research/c3-x3-plus-charpoly/verify.py
python3 -B scripts/research_package.py --package research/c3-x3-plus-charpoly --check-only
```

The marker is `PASS_C3_X3_PLUS_CHARPOLY`. Acceptance uses explicit checks, so
`-O` does not skip a theorem or a rejection control. On the measured host one
run takes about five seconds. No Lean, Docker, degree-881 replay, or selected
cold replay was run.

## Overlap

`scripts/find_overlap.py` was refreshed on 2026-11-10 against upstream
`17469fff78c22941280f04d39dc5a1faee09c840`. Coverage: local notes 10178 of
10178 HEAD paths, complete; 339 open PRs, pagination complete, fetched
2026-11-10T10:24:45Z; 7013 discussion records, pagination complete, fetched
2026-11-10T10:25:50Z. Closed PRs were searched through local READMEs, task
metadata and the ledger only.

The phrase `84-dimensional` matches open PR #7020, which records the
dimension and says the characteristic polynomial is uncomputed, and open PR
#7009, whose `84` is a c=1 character dimension. No open PR body gives this
polynomial. This search is not a novelty certificate.

## Open next questions

The structured list is in [TASK.json](TASK.json).

- The characteristic polynomial of the 132-dimensional `X_3 = -1` complement,
  inside the same trivial `(+1,+1)` joint space, is still uncomputed. The
  same basis routine applies with the opposite eigenvalue. The published
  comparison for that half is the pair of degree-88 sector polynomials.
- One 66-dimensional intersection of that complement with a single eigenvalue
  of `Z_508` is the smaller block. Its polynomial is not determined by the
  degree-84 factorisation above.

## Credit

JoyboyBrian's handoff recorded the sign-character dimensions. The explicit
pair and the signed-permutation boundary are upstream PR #6965. The trace
`-48`, the dimensions 84 and 132, and the open polynomial question are
upstream PR #7020. Ali Romman's PR4958 and PR4720 retain the query and the
Bell action. Nick Petalas's PR5120 is the degree-410 lower bound. Krzysztof
Wojt's exact one-slot package defines `X_3` and `Z_508` and is the degree-881
annihilator and the sector coefficient list used for the divisibility
comparison. The doubled representation comes from PR1719. The 216-dimensional
c=1 polynomial in `research/a1-joint-216-charpoly/` is a different block; its
Hessenberg recurrence is the model for the determinant. New work is
Apache-2.0.
