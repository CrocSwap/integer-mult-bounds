# Odd-sign factors of the weight-4 degree-16 polynomial

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

On the weight-4 character of sector `c=3`, the cross-coset pair whose odd
signs are minus on coordinate 1 only does not split the common degree-16
polynomial of upstream PR #7021 into two different degree-8 factors. Both
joint factors are

```text
x^4 (x - 2)^2 (x + 2)^2.
```

The same equality holds for every cross-coset pair from the described list of
96 splitting involutions. [PROOF.md](PROOF.md) separates the direct
factorisation of the named pair from that finite census.

No new kappa. The selected conditional kappa stays `781451/250000000`.

## Result

The live input is the query pinned in [SOURCES.json](SOURCES.json), SHA256
`5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3`.
The named pair is

| name | permutation | minus signs |
|---|---|---|
| `u` | `(0 2)(4 6)` | coordinates 0, 1 and 2 |
| `v` | `(0 4)(2 6)` | coordinates 0, 1 and 4 |

Its product is the explicit no-odd-minus involution `(0 6)(2 4)` with minus
signs on coordinates 0 and 6. Each of the four joint spaces has dimension 8
and characteristic polynomial `x^4 (x - 2)^2 (x + 2)^2` for `A_3`. Each
eigenspace of `u` has dimension 16, and its characteristic polynomial is the
square

```text
x^8 (x - 2)^4 (x + 2)^4.
```

The two degree-8 factors of that square are equal. Ascending-coefficient
SHA256 values agree with the polynomials recorded by #7021:

```text
degree 8   4078d16db1834dcd427c4f1094b96838a2c425c116c7cd1b60d46aa1f472f632
degree 16  4207a8e80e73e3fcd16abc6cba001f8e9881023742eeb587cbd8fbadd9f24350
```

`B = 4 A_3` is killed by `x(x - 8)(x + 8)` on each of these spaces, so `A_3`
is diagonalizable over `Q`. On each joint space the multiplicities are 4, 2
and 2 for eigenvalues `0`, `2` and `-2`.

Every one of the 96 described involutions acts on the weight-4 space as `±`
the no-odd-minus representative of its permutation. Both signs occur 16 times
in each of the three cosets. Every one of the `3072` unordered cross-coset
pairs therefore has the same four joint spaces, up to eigenvalue labels, and
the same equal degree-8 factors.

## Scope

Catalogue card `formal-interface-lemma` asks for a formal interface binding.
The question answered here is open-next item 1 of upstream PR
[#7021](https://github.com/CrocSwap/integer-mult-bounds/pull/7021):
whether one cross-coset pair with a nontrivial odd-sign pattern splits the
common degree-16 polynomial into two different degree-8 factors. The first
step named there is the three even double transpositions with a minus on
coordinate 1 only. This package factors that pair and then checks the rest of
the described list.

It does not recompute the degree-16 theorem as a new result for the
no-odd-minus pair, and it does not repeat the signed-permutation
classification of #6965. The 12-dimensional weight-3 polynomial and the
payload-involution questions are not taken.

Selected-baseline orientation returned `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`
for kappa `781451/250000000`.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
python3 -B -W error research/c3-weight4-odd-sign-factors/verify.py
python3 -B -O research/c3-weight4-odd-sign-factors/verify.py
python3 -B scripts/research_package.py --package research/c3-weight4-odd-sign-factors --check-only
```

The marker is `PASS_C3_WEIGHT4_ODD_SIGN_FACTORS`. Acceptance uses explicit
checks, so `-O` does not skip a theorem, the census, or a rejection control.
On the measured host one run takes about one second. No Lean, Docker,
degree-881 replay, or selected cold replay was run.

## Overlap

Canonical main was fetched at session start and was still
`17469fff78c22941280f04d39dc5a1faee09c840`. Local
`scripts/find_overlap.py --offline` searched 10178 of 10178 note paths. The
weight-4 polynomial is not in this tree; it is the open package of #7021.
A GitHub search of open pull requests for `odd-sign degree-8 factors` returned
only #7021, which asks this question. A search for `cross-coset` also returned
#7020, the payload-involution split, which is a different operator. Fork
branches named `cursor/*` did not already contain an odd-sign factorisation
of this polynomial. This search is not a novelty certificate.

## Open next questions

The structured list is in [TASK.json](TASK.json).

- The odd-sign reduction uses the weight-4 character. It does not determine
  the characteristic polynomial of one 12-dimensional joint space of a
  weight-3 `c=3` character. That question remains the second open item of
  #7021.

## Credit

The explicit pair, the list of 96 involutions, and the count of 3072
cross-coset pairs come from upstream PR #6965. The degree-16 polynomial, the
degree-8 polynomial of the no-odd-minus pair, and the question answered here
come from upstream PR #7021. The query and the Bell action are Ali Romman's
PR4958 and PR4720. The doubled representation comes from PR1719. New work is
Apache-2.0.
