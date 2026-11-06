# Worker C adversarial review: header/body saturation

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance, Apache-2.0. This is an independent separate-agent review in the same AI-assisted session, not human or formal-kernel certification.

**Verdict:** the three-query header obstruction, positive-body saturation implication and one-fragment/mixed-two-fragment price corollaries are valid in the intended atomic-native-stage model. The contract must explicitly require the coupled body factor and query to be adjacent components of one stage, or give an equivalent condition ensuring the same suffix conjugation. The unqualified equation PN=NP=N for gates at arbitrary separate times is insufficient for that step.

## Header factorization and the quotient

For each original query I+S N, N²=0 implies

`(I+S N)(I+N)^(-1) = I+(S−1)N`.

Removing the S=1 baseline from right to left conjugates each N by its ordinary S=1 suffix. Thus the normalized product is exactly a product of three factors I+x N_i, where x=S−1 and x²=−2x. With N_i=u_i v_i, expansion gives K=U T V, where T is triangular with unit diagonal. This remains true in characteristic two, where x²=0; it does not rely on two distinct sign evaluations.

Since rank K=3 and U,V have only three columns/rows, both have full rank. Therefore im U=im K and row V=row K. Every query image lies in X⊕E, every query row lies in Y*⊕E*, and every row annihilates X. The induced rank-at-most-one quotient map A_i on E has A_i²=0 because the X/Y components contribute nothing to v_i u_i.

If any quotient A_i vanished, two nilpotent rank-one queries would have quotient endpoint S I_E. Their normalized coefficient J would be the identity on the two-dimensional quotient. In its factorization J=U_2 T_2 V_2, full column/row ranks and J²=J imply V_2 U_2=T_2^(-1). Its diagonal is one, contradicting v_i u_i=0. Thus every query induces a nonzero rank-one nilpotent on E.

## Saturation over a ring

The logarithmic derivative in D at D=1 is a sum of body projectors conjugated by their actual suffixes. Factoring the individual terms and concatenating yields UV=P_D with total width r=rank(P_D).

The argument correctly works over R=F[S]/(S²−1), including its zero divisors. After an ordinary basis change, P_D=diag(I_r,0). The upper-left equation U_1 V_1=I_r makes both square matrices invertible over this **commutative** ring: their determinant product is one, so each determinant is a unit. Hence the other block equations force U_2=0 and V_2=0. Each individual conjugated body projector is supported on P_D on both sides. Any nilpotent supported on that projector is supported on P_D as well.

The native-query transfer then needs its actual suffix to match the body factor's suffix, up to factors commuting with the query and projector. For an atomic native stage with adjacent factors Q(S)=I+S N and B(D)=I+(D−1)P, PN=NP=N ensures this: swapping Q and B is legal, and conjugation by Q(1) fixes both P and N. At S=1 the transported N is therefore exactly the normalized header N_i used above.

Without adjacency or an equivalent common-suffix condition, raw PN=NP=N is not enough: intervening ordinary gates can conjugate the query's support without conjugating the later body factor's support. The contract should not define “coupled” solely by the raw support equation.

## Restriction of P_D to E

Commutation with K preserves im K and ker K, and their intersection X, so P_D descends to the quotient im K/X. More directly, E=ker(K−I), so it preserves E itself. The induced body projector therefore supports the nonzero nilpotent A_i. A projector of rank zero supports only zero; on a rank-one image every supported endomorphism is scalar, and a nonzero scalar over a field cannot be nilpotent. Hence rank(P_D restricted to E)=2.

This proves the stated obstruction for saturated positive body degrees, ordinary final body projectors commuting with K, the rank-three common-S header, and at least one atomic native query coupled to the selected body. It does not cover extra unsaturated body calls, inverse body factors, D-dependent ordinary controls, distinct operator-valued central alphabets or a changed endpoint/header contract.

## Price corollaries

One fragment gains strictly less than one rank-one query, so raising the required header from three queries to at least four defeats its optimistic same-body tariff.

The mixed two-fragment corollary is also valid for H(x)=x^t, 0<t<1. Let i(x)=H(x+1)−H(x), and assume a<=b. Since i decreases and a+b<=2b,

`i(a+b)>=i(2b)>=2^(t−1)i(b)`.

The latter inequality follows directly by integrating t(2b+s)^(t−1) over 0<=s<=1 and using 2b+s<=2(b+s), with negative exponent t−1. Therefore

`2i(a+b)>=2^t i(b)>i(b)`

and the mixed gain i(a)+i(b)−2i(a+b) is strictly less than i(a)<1. Thus even one necessary new thin query defeats that optimistic mixed tariff.

The equal-orientation two-fragment expression 2[i(a)−i(a+b)] is not uniformly below one as b grows. The four-query lower bound alone does not exclude that entire changed-history family. The proof correctly preserves this limitation. No physical-native, compiler, stock, precision/tape or analytic recovery admission follows.

## Final integrated contract and coupled-block addendum

The integrated `worker-d/research/binary-full-bank-retirement/HEADER-SATURATION.md`, SHA256 `717f3aa49c7124a413021f022ad7ed5b984399e5d1ef61fa1343a2ae0acbb031`, resolves the suffix issue with adjacent commuting components of one atomic native stage. It also requires ordinary split projector factorizations P_j=U_j V_j, V_j U_j=I_r_j. Thus r_j is the actual rank after S=1, not an arbitrary width that might specialize lower.

For positive unit body exponents, determinant comparison at S=1 is a formal Laurent-polynomial identity in D. Each body contributes D^r_j, the endpoint D^rank(P_D), and all other determinants are constant. Total width therefore equals final body rank. This compares integer exponents, not traces modulo the characteristic. An identity valid only modulo D^4=1 does not justify that step.

The three-block width-w extension is sound. Header rank 3w gives support confinement. On the 2w-dimensional quotient, a vector in two quotient-map kernels is fixed by their factors; endpoint S I forces the remaining nilpotent to act as identity on it, so it is zero. Centrality permits cyclic rotation. Every pair of kernels has zero intersection, forcing every quotient rank to equal w. A square-zero rank-w map supported in dimension d requires d>=2w; therefore the body projector contains all of E.

The revised wording correctly uses kernels of quotient maps, not of invertible factors. Exactly three blocks are retained; arbitrary interleavings of 3w rank-one queries are not covered by this extension. A fourth block might have smaller rank, so the scalar price statement does not become a width-w extra-query tariff. The integrated proof preserves these limitations.
