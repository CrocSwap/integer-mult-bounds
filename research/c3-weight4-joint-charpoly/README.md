# Characteristic polynomial of one weight-4 c=3 summand

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

For the historical 8-by-112 centre query, the `+1` eigenspace of the explicit
involution `u` inside the weight-4 character of sector `c=3` is a
16-dimensional `A_3`-invariant subspace. Its monic characteristic polynomial
is

```text
x^8 (x - 2)^4 (x + 2)^4.
```

The trace formula's dimension 8 is the finer joint eigenspace of the explicit
commuting pair `(u, v)`. That space has characteristic polynomial

```text
x^4 (x - 2)^2 (x + 2)^2,
```

and the degree-16 polynomial is its square. [PROOF.md](PROOF.md) separates
the explicit-basis proof from the evaluation on the described list of 96
involutions.

No new kappa. The selected conditional kappa stays `781451/250000000`.

## Result

The live input is the query pinned in [SOURCES.json](SOURCES.json), SHA256
`5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3`.
`B = 4 A_3` is the integer operator on sector 3. On the pinned
16-dimensional space, `chi_{A_3}(x) = 4^{-16} chi_B(4x)`, and both
polynomials lie in `Z[x]`. Ascending-coefficient SHA256 values are

```text
chi_A  4207a8e80e73e3fcd16abc6cba001f8e9881023742eeb587cbd8fbadd9f24350
chi_B  5030313ecab6822bd390a9e6847a3b6a9c9d701d2e7e247d7892ce5f55bfe717
```

The basis is the least-index signed orbit basis of the weight-4 character
and of `u = +1`, pinned in [evidence/basis.json](evidence/basis.json). The
integer matrix of `B` in that basis is pinned in
[evidence/matrix.json](evidence/matrix.json). It is the orthogonal sum of
eight 2-by-2 blocks, four of type `[[-4,4],[4,-4]]` and four of type
`[[4,4],[4,4]]`. The block eigenvectors diagonalize `A_3` over `Q`.
Eigenvalue 0 has geometric multiplicity 8, and eigenvalues `2` and `-2` each
have geometric multiplicity 4.

The same degree-16 polynomial is the characteristic polynomial of `A_3` on
both eigenspaces of every one of the 96 involutions described by the c=3
sign-split certificate. Each of those 192 matrices of `B` is killed by
`x(x-8)(x+8)`, so each space is diagonalizable over `Q` with the same
multiplicities. Completeness of that list of 96 is the predecessor census.
This package evaluates the list; it does not reclassify the stabilizer.

The factors `x`, `x-8` and `x+8` of `chi_B` each divide all four published
`c=3` sector polynomials in `research/exact-one-slot-gram/CERTIFICATE.json`.
That comparison reads coefficients. It does not replay the degree-881
certificate.

## Scope

Catalogue card `formal-interface-lemma` asks for a formal interface binding.
The live question is the characteristic polynomial left open by the c=3
sign-split, upstream PR
[#6965](https://github.com/CrocSwap/integer-mult-bounds/pull/6965).
The predecessor gave the dimensions 16 and 8 without a basis or a matrix.
This package computes the polynomials. It does not repeat the sign-split
classification, and it does not take the payload-involution question, the
216-dimensional `A_1` polynomial, or the 48-dimensional `c=1` polynomial.

Selected-baseline orientation returned `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`
for kappa `781451/250000000`.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
python3 -B -W error research/c3-weight4-joint-charpoly/verify.py
python3 -B -O research/c3-weight4-joint-charpoly/verify.py
python3 -B scripts/research_package.py --package research/c3-weight4-joint-charpoly --check-only
```

The marker is `PASS_C3_WEIGHT4_JOINT_CHARPOLY`. Acceptance uses explicit
checks, so `-O` does not skip a theorem or a rejection control. On the
measured host one run takes about nine seconds. No Lean, Docker, degree-881
replay, or selected cold replay was run.

## Overlap

Local `scripts/find_overlap.py --offline` on 2026-11-10, against HEAD
`17469fff78c22941280f04d39dc5a1faee09c840`, searched 10178 of 10178 note
paths. The only match is `research/c3-centre-sign-split/`, which states this
polynomial as still uncomputed. A targeted GitHub search of open pull
requests for `characteristic polynomial` returned #7008 and #7009, both
about the `c=1` block. The phrase `16-dimensional joint` matched closed
#6965, the source of the question, and an unrelated closed Niemeier note.
No open PR computes this `c=3` polynomial. Fork branches named `cursor/*`
contain the predecessor `c3-centre-sign-split` package and the 216-dimensional
polynomial, not this computation. This search is not a novelty certificate.
Closed PRs were not paginated beyond those searches and the local notes.

## Open next questions

The structured list is in [TASK.json](TASK.json).

- The degree-8 polynomial is known for the explicit pair `(u, v)` only.
  A cross-coset pair whose odd signs are not all positive may split the
  common degree-16 polynomial into two different degree-8 factors.
- One 12-dimensional joint space of a weight-3 `c=3` character is the next
  block in the same sector. The weight-4 calculation does not determine it.

## Credit

JoyboyBrian's handoff recorded the sign-character dimensions. The c=3
classification, the explicit pair `(u, v)`, and the dimensions 16 and 8 are
the certificate in upstream PR #6965. Ali Romman's PR4958 and PR4720 retain
the query and the Bell action. Nick Petalas's PR5120 is the degree-410 lower
bound. Krzysztof Wojt's exact one-slot package is the degree-881 annihilator
and the sector coefficient list used for the divisibility comparison. The
doubled representation comes from PR1719. New work is Apache-2.0.
