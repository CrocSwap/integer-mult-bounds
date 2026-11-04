# Which source and reader masks can two port blocks realize?

This answers open question 1 of Nick Petalas's #6691. For two blocks of three ports, an invertible basis realizes **33,727 labeled source/reader signatures over the rationals**, exactly the generic support census. Over the two-element field it realizes **30,547**. The classification holds for arbitrary positive block sizes and every field. [Four-port handoff](https://github.com/CrocSwap/integer-mult-bounds/pull/6691)

A signature records which blocks a message uses on input and which blocks read it on output. The input masks come from the corresponding column of the basis matrix and the output masks from the corresponding row of its inverse. A generic support pattern gives each allowed matrix entry its own independent coefficient. The original six-port search would have had 2^36 port-level supports.

| Two blocks of three ports | Up to relabeling messages | Labeled signatures |
| --- | ---: | ---: |
| Rational, generic or any field with more than two elements | 188 | 33,727 |
| Zero-one entries with rational inversion | 179 | 32,287 |
| Two-element field | 167 | 30,547 |
| Ordinary minus two-element field | 21 | 3,180 |

In the middle row the basis entries are restricted. The rational inverse can use other coefficients. An exact weighted census accounts for 28,836,612,000 invertible zero-one matrices. [Restricted coefficient census](ZERO-ONE.md)

Although these three sets have different sizes, one additive tariff shared across the six messages gives at most two distinct minimum prices. Either adjacent pair can tie. [Why the three minima cannot all be distinct](ZERO-ONE.md#why-the-three-minima-cannot-all-be-distinct)

## What determines a signature

A nonzero determinant supplies simultaneous pivots for both blocks. After row-basis changes inside each block, the matrix consists of two identity diagonal blocks and two rectangular off-diagonal blocks. Six exclusive message types force the side on which they pivot. Messages using both blocks on input and output fill the leftover positions. The row and column support requirements then give an exact test and a direct witness with entries 0, 1 and −1 over the rationals. A small parity obstruction accounts for the entire binary deficit. Fields of characteristic two with more than two elements realize the full ordinary set. [Classification and proof](PROOF.md)

The labeled counts take quadratic arithmetic time in the balanced dimension. In balanced size d+d, the proportion of ordinary signatures missing over the two-element field is asymptotic to d^(3/2) (16/49)^d / (4√π). [Counting formula](COUNTING.md)

## Why the tariff matters

If a message's price cannot decrease when either mask grows, its exact minimum over all invertible bases is attained by assigning messages to individual blocks with a coordinate permutation. This even permits different prices for different messages. The result concerns square bases. The earlier sharp matched-plane COPY bound also allows overcomplete scalar factorizations. [Tariff proof](PROOF.md#5-exact-prices-under-monotone-support-tariffs) · [#4365](https://github.com/CrocSwap/integer-mult-bounds/pull/4365)

Under a positive **nonmonotone** tariff, fields can differ. The same seven prices give minima 10 and 11 in the six-port rational and binary cases, respectively. Among the 21 missing profiles, 12 can be priced strictly below every binary choice. The other nine are convex combinations of binary profiles. These are exact example tariffs. A physical decoder would need its own measured or proved prices. [Price certificates](PRICE-CERTIFICATES.json)

## Reproduce

Run the registered replay from the repository root with CPython 3.12 and its standard library.

```sh
python3.12 -B scripts/research_package.py --package research/two-block-signatures
```

[SIX-PORTS.json](SIX-PORTS.json) contains a rational matrix for each of the 188 profiles, a binary matrix where one exists, and the exact number of ordered complementary pairs over the two- and three-element fields for each **single labeling**. The matrix strings use `+` for one, `-` for minus one and `.` for zero. The symbol order is AA, AM, MA, BB, BM, MB, MM. Permuting the columns relabels a witness. [RESULT.json](RESULT.json) and [VALIDATION.md](VALIDATION.md) give the counts and the independent replay commands.

## Source, scope and credit

Gonzalo Mier supplied the original binary-coefficient and generic four-port screens in #3990/#3997. Nick Petalas supplied the complementary-space interpretation, four-port classification and six-port handoff in #6691. #4365 supplies the earlier overcomplete matched-plane result. Classical determinant/cofactor matchings and coordinate incidence retain their usual credit. Source blobs from the pending handoff are retained with their original author, path and Git identity. [Source identities](SOURCES.json) · [Scope and overlap](OVERLAP.json)

The revision-8 `coverage-law-change` card changes scope to the exact attainable signatures of this decoder interface. The selected source-binding orientation passed. Native delivery, completeness of a physical caller and a new multiplication exponent are outside this result. New work prepared for SHIN09-git with substantial OpenAI Codex assistance in derivation, implementation, verification and writing. Apache-2.0.

## Open next questions

1. For three blocks of two ports, can a special cancellation produce a signature absent from the generic census? A reader coordinate can lie in the sum of the other two row spaces, so the present opposite-space test does not decide it.
2. Is there an exact field-order formula for the number of bases with an individual signature? Begin with the stored two- and three-element multiplicities. Feasibility alone does not determine those numbers.
