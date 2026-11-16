# Characteristic polynomial of one weight-3 c=3 joint space

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

For the historical 8-by-112 centre query, the joint eigenspace
`(u, v) = (+1, -1)` inside weight-3 character 7 of sector `c=3` is a
12-dimensional `A_3`-invariant subspace. Its monic characteristic polynomial
is

```text
x^4 (x - 2)^4 (x + 2)^4.
```

The same polynomial is the characteristic polynomial on all twelve
12-dimensional joint spaces of the explicit pair `(u, v)`, and on the three
12-dimensional joint spaces of one odd-sign witness pair inside the same
character. [PROOF.md](PROOF.md) separates the explicit-basis proof, the
twelve-space census, and the single witness.

No new kappa. The selected conditional kappa stays `781451/250000000`.

## Result

The live input is the query pinned in [SOURCES.json](SOURCES.json), SHA256
`5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3`.
`B = 4 A_3` is the integer operator on sector 3. On the pinned space,
`chi_{A_3}(x) = 4^{-12} chi_B(4x)`, and both polynomials lie in `Z[x]`.
Ascending-coefficient SHA256 values are

```text
chi_A  589ce5d010f0e4c5cf6d78719150e69afee3650ddf71dd273b58de10a5082e45
chi_B  bf3564eac70bdbb2ff2e0041ca84c8f69f1f215e9ba5678f5a10d8b90804106a
```

Character 7 is the product of the signs on coordinates 1, 3 and 5. The pair
is the explicit pair from the c=3 sign-split: `u = (0 2)(4 6)` with minus
signs on coordinates 0 and 2, and `v = (0 4)(2 6)` with minus signs on
coordinates 0 and 4. On a weight-3 character that pair splits the
80-dimensional space as `44 + 12 + 12 + 12`. The source first step names the
`(+1, +1)` space. That space is the 44-dimensional summand, so the pinned
space is the `(+1, -1)` summand instead.

The basis is the least-index signed orbit basis, pinned in
[evidence/basis.json](evidence/basis.json). Every vector has support 8. The
integer matrix of `B` in that basis is pinned in
[evidence/matrix.json](evidence/matrix.json). It is two 4-by-4 blocks of
type `x^2 (x - 8)(x + 8)` and four scalar blocks `8, -8, -8, 8`. The block
eigenvectors diagonalize `A_3` over `Q`. Eigenvalues `0`, `2` and `-2` each
have geometric multiplicity 4.

The four weight-3 characters are exactly the indices `7, 11, 13, 14`. For
this explicit pair, each contributes three 12-dimensional joint spaces, and
all twelve have this polynomial. Each matrix of `B` is killed by
`x(x - 8)(x + 8)`, so each space is diagonalizable over `Q` with the same
multiplicities. One further pair, with an extra minus on coordinate 1, moves
the 44-dimensional slot and still has this polynomial on its three
12-dimensional spaces. That pair is one witness, not a census of the
cross-coset pairs.

The factors `x`, `x - 8` and `x + 8` of `chi_B` each divide all four
published `c=3` sector polynomials in
`research/exact-one-slot-gram/CERTIFICATE.json`. That comparison reads
coefficients. It does not replay the degree-881 certificate.

The weight-4 polynomials `x^8 (x - 2)^4 (x + 2)^4` and
`x^4 (x - 2)^2 (x + 2)^2` are different. They were not recomputed here.

## Scope

Catalogue card `formal-interface-lemma` asks for a formal interface binding.
The live question is open-next item 2 of
[#7021](https://github.com/CrocSwap/integer-mult-bounds/pull/7021),
recorded again in discussion comment
[19514159](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19514159).
The weight-4 polynomial does not determine this one. This package computes
it. It does not repeat the sign-split classification, and it does not take
the odd-sign factorisation of the weight-4 degree-16 polynomial, the
payload-involution question, or the 216-dimensional, 48-dimensional and
8-dimensional `c=1` polynomials.

Selected-baseline orientation returned `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`
for kappa `781451/250000000`.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
python3 -B -W error research/c3-weight3-joint-charpoly/verify.py
python3 -B -O research/c3-weight3-joint-charpoly/verify.py
python3 -B scripts/research_package.py --package research/c3-weight3-joint-charpoly --check-only
```

The marker is `PASS_C3_WEIGHT3_JOINT_CHARPOLY`. Acceptance uses explicit
checks, so `-O` does not skip a theorem or a rejection control. On the
measured host one run takes about two seconds. No Lean, Docker, degree-881
replay, or selected cold replay was run.

## Overlap

Local `scripts/find_overlap.py --offline` on 2026-11-10, against HEAD
`17469fff78c22941280f04d39dc5a1faee09c840`, searched 10178 of 10178 note
paths. There was no match for a 12-dimensional joint characteristic
polynomial. A targeted GitHub search of open pull requests found the
question only as an open next step of #7021. Searches for `weight-3 c=3`
and `12-dimensional` did not find another open PR that computes this
polynomial. The nearby open polynomials are the weight-4 `c=3` polynomial
(#7021), the 8-dimensional and 48-dimensional `c=1` polynomials (#7019,
#7036), and the `c=1` blocks in #7008, #7009 and #7023. Fork branches named
`cursor/*` contain `c3-weight4-joint-charpoly` and not this computation.
This search is not a novelty certificate. Closed PRs were not paginated
beyond those searches and the local notes.

## Open next questions

The structured list is in [TASK.json](TASK.json).

- The twelve-space census uses the explicit pair, whose odd signs are all
  positive, plus one witness with a minus on coordinate 1. Whether every
  cross-coset pair has this same degree-12 polynomial is open. That question
  is not the weight-4 degree-16 splitting question of #7021.
- The 44-dimensional `(+1, +1)` joint space of character 7 is still
  uncomputed. The 12-dimensional calculation does not determine it.

## Credit

JoyboyBrian's handoff recorded the sign-character dimensions. The c=3
classification, the explicit pair `(u, v)`, and the joint dimensions
`44 + 12 + 12 + 12` are the certificate in upstream PR #6965. The question,
and the fact that the weight-4 calculation does not determine this
polynomial, are open-next item 2 of #7021. Ali Romman's PR4958 and PR4720
retain the query and the Bell action. Nick Petalas's PR5120 is the
degree-410 lower bound. Krzysztof Wojt's exact one-slot package is the
degree-881 annihilator and the sector coefficient list used for the
divisibility comparison. The doubled representation comes from PR1719. New
work is Apache-2.0.

## Workflow feedback (optional)

The source first step names the `(+1, +1)` space of character 7. For a
weight-3 character that space has dimension 44, while the question asks for
a 12-dimensional space. Naming the joint eigenvalues next to the dimension
removes the ambiguity.
https://github.com/CrocSwap/integer-mult-bounds/discussions/1200
