# Dyadic decoder kernels from complementary even subsets

**Proved algebraic family; no supplier or new kappa.** For odd n and even
2<=k<n, index ports by k-subsets, label S by the indicator of its complement,
and use K(S,T)=binomial(|S intersection T|/2,k/2). The labels have norm1;
the kernel has unit diagonal and vanishes on forbidden distinct pairings.

The explicit binomial-basis incidence factorization is dyadic. Every degree-j
feature has support spanning exactly n-j binary coordinates. For(25,6),
there are 177100 ports and 2625 features, with algebraic support-rank sum 58100.
That is an algebraic bound, not an admitted physical copy invoice.
[PROOF.md](PROOF.md) proves the whole family and its support frames.

## Reproduce

Python3.12, standard library only:

```sh
python3 scripts/research_package.py --package research/even-subset-dyadic-kernels
```

Expected: `PASS_EVEN_SUBSET_DYADIC_KERNELS` and
`PASS_REGISTERED_RESEARCH_PACKAGE`. The read-only verifier checks every
ordered pair and every actual feature support in three complete small
families;15 larger invoices; dyadic coefficients through k=24; and three
mathematical failure controls. Checks remain active under Python optimization.
No selected cold replay, physical supplier or hosted CI is claimed.

## Predecessors and scope

The repository's five-subset construction, credited to Zhihao Chen and its
compiler contributors, is prior subset-based work. Open PR172's Boolean-lattice
zeta family computes disjointness and explicitly leaves its identity fitting
condition open. This package proves the stated fitting kernel and complementary
support spans; it supplies no side DAG. Standard binomial interpolation and
incidence factorization are not claimed as new techniques. See OVERLAP.md.

## Open next questions

Construct and price I-K. Start with a complete(9,4) side word, including dirty
restoration and every endpoint transition. A decoder alone cannot establish
the promised kappa gain. Both physical orientations, hosting, precision and
the bit rail remain open.

## Credit

Prepared by Cinna Davis (@1337isnot1337), with substantial OpenAI Codex assistance.
Retain the repository's subset/compiler ancestry. Apache-2.0; no independent
human review or formalization is claimed.
