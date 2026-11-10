# Paying row additions for a common-image guard header

Permuting coordinates and scaling them by nonzero elements can change which proper leading minors pass, even for two representatives of the same complete general-linear orbit. Here a mixing operation adds a nonzero multiple of one row to another. This follows the restricted-header question in [PR #6710](https://github.com/CrocSwap/integer-mult-bounds/pull/6710).

**A five-element example.** Four nonzero coordinate charges must be made zero. With charges `1,4,2,3`, two opposite pairs cost **two** additions. With `1,1,1,2`, only the whole list sums to zero, so **three** are necessary. A separate normalized carrier ensures that both prices give genuinely passing headers. All lower-cost states fail the literal principal-minor tests. [Explicit words and depth counts](EXAMPLES.json)

| Question | Result |
| --- | --- |
| What can a uniform monomial header do? | A labeled subset recurrence counts the exact joint probability. The same complete orbit can have zero joint probability on one input and one half on another. [Counting proof](PROOF.md) |
| How much does coordinatewise slope separation cost? | For $h$ nonzero charges and at most $Z$ disjoint zero-sum blocks, the optimum is $h-Z$. The graph bound and actual row additions match. It is also the full guard cost for an anchored carrier. [Proof](PROOF.md) · [Witnesses](WITNESSES.json) |
| What if the carrier is arbitrary? | In the binary field, adjoining one dummy charge gives the exact full price for every nonempty normalized list. In the ternary field let $S$ be the separation price and $L$ the isolated scalar price. The full price always lies between $\max(S,L)$ and $2S+L$. Both endpoints are attained for **every** choice of $S,L$ across dimensions. [Sharp envelope](GAP.md) |
| Can the two requirements interact? | Even the sum $S+L$ may underestimate the optimum by an arbitrarily large amount. Five is the first ternary dimension with any strict gap above the larger single bound. [Free-orbit census](ORBITS.md) |
| How hard is the optimization? | A labeled subset algorithm produces a word and its matching partition bound. For fixed alphabet, multiplicity compression is polynomial in the number of coordinates. With variable prime field, even the anchored pencil budget decision is strongly NP-complete. [Algorithms and reduction](ALGORITHM.md) |

This is an exact arithmetic and operation-count result in a specified header model. Free scalings/permutations and a unit price for every addition are modeling choices. It supplies neither physical caller prices nor a changed bound for integer multiplication.

## Reproduce

From the repository root with Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/monomial-guard-settlement
```

For just the two displayed examples and the ternary controls, run `python3.12 -I -W error -B example_check.py` inside the package directory. The [validation notes](VALIDATION.md) distinguish literal matrices, raw tuple searches, orbit-weighted coverage and the optional larger census. [Sources](SOURCES.json) pin original bytes and [overlap notes](OVERLAP.json) compare neighboring work.

## Open next questions

1. For an unanchored ternary pencil, is the optimal price already determined by the multiset of scalar/slope charge pairs? The free-orbit graph retains additional information at zero image coordinates. Search for two such orbits with equal charges and different prices, or prove a path-lifting argument.
2. What sharp price envelope replaces $2S+L$ in the five-element field? Begin with the cost of arranging already-separated scalar charges. The ternary alternation of the two nonzero residues does not extend directly.

## Attribution

Prepared by SHIN09-git with substantial OpenAI Codex assistance. The retained field-arithmetic table and the precursor disclosures are from PR6710. ToikY and Nick Petalas retain credit for their earlier complete-header work. The abstract debt-partition principle and debt-clearing complexity have prior literature. The contribution here is the finite-field guard realization, its sharp paid distances and restricted-header certificates. [NOTICE](NOTICE)
