# When positive guard pairs give a below-product joint probability

On one uniform invertible header, consider the full proper-minor tests for corank-one complements sharing an image direction in their rank-one kernels. Nick Petalas derived the marginal and pair laws. ToikY proved the binary independent-family law and the strict positive sign for every pair over any finite field. This package answers the nonbinary question left by PR #6701, including families of linearly dependent covectors. [PR #4227](https://github.com/CrocSwap/integer-mult-bounds/pull/4227) · [PR #4807](https://github.com/CrocSwap/integer-mult-bounds/pull/4807) · [PR #6701](https://github.com/CrocSwap/integer-mult-bounds/pull/6701) · [PR #6703](https://github.com/CrocSwap/integer-mult-bounds/pull/6703)

In the smallest example here with five guards, take the rows `(1,a)` for all five field elements, common column `(1,0)^T`, and headers in `GL_2(F_5)`. Of the 480 headers, **336 pass each named guard, 272 pass each named pair, but only 80 pass all five**. Thus every pair beats independence, while all five pass with probability `1/6 < (7/10)^5`. Every proper subfamily of size two through four beats its product. The outcome depends on the header dimension too. For these five directions the joint probability beats the product exactly in dimensions three and four.

| Result | Evidence |
| --- | --- |
| Exact joint law for any fixed space of row dependencies over a finite field, and its specialization to an affine pencil | [Counting proof](PROOF.md) |
| Four is the smallest field order allowing any below-product common-image family; every larger field has an eventual triple counterexample | [Sharp field-size boundary](SMALL-FIELDS.md) · [Ternary certificates](TERNARY-FOUR.json) |
| Full pencil over every field, all dimension windows, and size and dimension scaling | [Sign proof](SIGN.md) · [232 exact windows](SIGN-WINDOWS.json) · [Scaling examples](ASYMPTOTICS.json) |
| Same marginals and all pairs, opposite triple signs at field order four and dimension 61 | [Exact results](RESULT.json) |
| Independent triples beat the product over every field and dimension; a negative triple must be three distinct collinear directions | [Triple proof](TRIPLES.md) · [17 exceptions to the sufficient bound, checked exactly](TRIPLE-CERTIFICATES.json) |
| Every binary common-image family of at least two guards beats its product; complete affine flats of rank at least three do so over all fields | [Last-coordinate bound](PROOF.md) · [Full-flat checks](FULL-FLATS.json) |
| Every named mask has the same law in each uniform determinant class, including uniform special-linear headers | [Counting proof](PROOF.md) · [Literal checks](LITERAL-GL.json) |
| Complete matches for every subset of all normalized covectors in dimension three over the fields of orders two, three and four | [Affine-plane census](AFFINE-PLANES.json) |

One practical consequence concerns estimates for a caller that batches several tests on the same header. Even knowing every pair exactly leaves room for the all-pass probability to fall on the opposite side of the independence prediction. A physical caller, its price, an improved multiplication bound and a formal proof-kernel check are outside this result.

## Reproduce

With Python 3.12 from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/common-image-guard-pencils
```

For the literal five-direction counterexample alone, run from the package directory:

```sh
python3.12 -I -W error -B verify.py --controls
```

[Validation](VALIDATION.md) describes the finite domains and rejection controls. [Source provenance](SOURCES.json) pins the original and retained predecessor objects. [Overlap search](OVERLAP.json) identifies related work and the limits of the search.

## Open next questions

1. Do four or more independent normalized covectors beat independence in **every** dimension? The last-coordinate bound covers large families and the sampling argument resolves triples. Between these regimes the cost of conditioning on a full affine frame still needs control.
2. Under uniform monomial headers, how does the size cutoff depend on the initial tuple? Start with several nonzero coordinates in the common image vector and enumerate permutations. The determinant-stratum symmetry alone does not identify that distribution.

## Credit

Prepared by SHIN09-git with substantial OpenAI Codex assistance, including the different counting implementations. The retained source notices credit ToikY and Nick Petalas. New material is Apache-2.0. [Attribution](NOTICE)
