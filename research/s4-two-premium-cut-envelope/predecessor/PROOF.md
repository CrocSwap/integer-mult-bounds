# Two order cuts and weighted adjacent transpositions

Ross Richardson, with substantial OpenAI Codex assistance. New work is
Apache-2.0. This is a written proof with exact finite checks, not a formal-kernel
proof. See README.md for predecessor attribution and the precise scope change.

## 1. Model and the inherited cut-rank lemma

Let G be a finite group and A = F2[G]. There are r finite, arbitrary dirty
scalar roles. Free operations are GL_r(F2) acting on roles. A paid gate with
involutive label s is

    D_N(s) = I + ([s] + 1) N,

where N is a binary rank-one idempotent. Products and restoration are literal
over A. The required endpoint is diag([w_1], ..., [w_d], 1, ..., 1). In
particular, every extra dirty role is restored for every input. The cost of a
gate depends only on its label. This theorem does not cover a larger free
alphabet, nonuniform coefficient-dependent free maps, clean initialization,
unpriced sources, resets, or identities valid only in a specialized quotient.

Represent A by left multiplication on the basis G, and repeat a subset H of
that basis uniformly in every role. Write K = G minus H, and define

    Phi_H(M) = rank_F2 M_(K,H).

Here rows and columns include all r roles. Since

    (UV)_(K,H) = U_(K,H) V_(H,H) + U_(K,K) V_(K,H),

rank subadditivity gives Phi_H(UV) <= Phi_H(U) + Phi_H(V).
Free role operations preserve the H/K splitting and have Phi_H = 0. Set

    c_g(H) = |{h in H : gh not in H}|.

The crossing block of a paid gate is the tensor product of N and the crossing
block of the permutation g=s. The latter is a partial permutation matrix of
rank c_s(H). Thus Phi_H(D_N(s)) = c_s(H). At a diagonal endpoint the blocks
are disjoint, so Phi_H(endpoint) = sum_j c_(w_j)(H).

Consequently, any nonnegative combination P = sum_H a_H Phi_H satisfying
sum_H a_H c_s(H) <= price(s) is a lower bound on total paid cost. This is the
cut-rank argument inherited from Gall PR1941 and Richardson PR1966/1989;
the contribution here is the order-cut combination below and its exact scope.

## 2. Two cuts in S_n

Use one-line permutations h=(h(1),...,h(n)) and multiplication (gh)(i)=g(h(i)).
For n >= 3 define

    H_A = {h : h(1) < h(n)},
    H_B = {h : h^(-1)(1) < h^(-1)(n)}.

For any g, a crossing of H_A chooses a pair a<b with g(a)>g(b) for
h(1)=a, h(n)=b. Each pair has (n-2)! completions. Therefore

    c_g(H_A) = (n-2)! inv(g).                         (1)

Write s_i=(i,i+1). An interior generator fixes the labels 1 and n, hence
c_(s_i)(H_B)=0 for 2 <= i <= n-2. For s_1, a crossing occurs precisely
when the positions of labels 1,n,2 occur in that order. For s_(n-1), it
occurs when the positions of n-1,1,n occur in that order. Each is one of
the six orders of three distinct labels. Thus

    c_(s_1)(H_B) = c_(s_(n-1))(H_B) = n!/6.           (2)

For t=(1,n), left multiplication exchanges labels 1 and n, taking H_B to
its complement. It follows that

    c_t(H_B) = n!/2,      inv(t) = 2n-3.             (3)

These counts prove (1)-(3) for every n>=3; the independent verifier's
enumeration for n=3,...,7 is a finite cross-check of the written argument.

## 3. Exact outer-transposition tariff for every n >= 3

Give s_1 and s_(n-1) price beta and every interior s_i price alpha, where
beta >= alpha > 0 are arbitrary real numbers. Define

    P = alpha/(n-2)! Phi_(H_A)
        + 6(beta-alpha)/n! Phi_(H_B).

Both coefficients are nonnegative. Equations (1)-(2) give charge alpha
for interior labels and beta for exterior labels. Equations (1) and (3)
give endpoint value

    alpha(2n-3) + 3(beta-alpha)
      = 3 beta + (2n-6) alpha

for t. Hence every literal implementation of diag([t] repeated k times,
1 repeated r-k times), for any finite r>=k>=0, costs at least

    k [3 beta + (2n-6) alpha].                       (4)

The chronological word

    s_1, s_2, ..., s_(n-1), s_(n-2), ..., s_1

implements t. It contains three exterior generators and 2n-6 interior
generators, including the n=3 boundary case. Applying this word separately
to each target role attains (4). Therefore (4) is the exact tariff with
any number of restored dirty roles. The construction uses coordinate
rank-one idempotents, which are allowed in the model.

## 4. A common exact tariff for twenty S4 targets

For S4, P = (alpha/2) Phi_(H_A) + ((beta-alpha)/4) Phi_(H_B).
On a diagonal target g its value is

    alpha inv(g) + (beta-alpha)c_g(H_B)/4.           (5)

RESULT.json lists all 24 permutations, both cut counts, and chronological
direct words. For each of the 20 entries marked saturated, the displayed
word has exactly inv(g) letters and c_g(H_B)/4 exterior letters. The
verifiers independently check those integer facts and the word endpoint.
Thus the same word attains (5) for every beta>=alpha>0, not just the
sample prices (2,1,2). The common potential is additive on diagonal
endpoints: for any tuple whose entries belong to this 20-element set,
sum of (5) is the exact cost, with arbitrary finite restored dirty roles.

The four exclusions, written in one-line notation, are 2143, 2413, 3142,
3412. At (beta,alpha)=(2,1), their potentials are 7/2,9/2,9/2,11/2,
whereas direct distances are 4,5,5,6. Exclusion means this common
certificate does not prove their exact arbitrary-tuple tariff; it is not
a counterexample and does not negate predecessor results.

In particular, t=4231 has cuts (10,12) and reversal v=4321 has cuts
(12,12). Arbitrary tuples containing k copies of t and l copies of v
have exact cost

    k(3 beta + 2 alpha) + l(3 beta + 3 alpha).

At prices (2,1,2), diag([t],[t],1) costs exactly 16 for any further
restored spectators, and two reversals cost exactly 18.

## 5. Finite census and its exact coverage

Lexicographically index permutations of 0,1,2,3. Then H_A and H_B have
bitmasks 22015 and 29183. CUTS.tsv enumerates the distinct vectors

    (c_s1, c_s2, c_s3, c_t, c_v),

their multiplicities among complementary pairs, and the smallest
representative mask of each vector. Since c_g(H)=c_g(G minus H), it
suffices to enumerate 2^23 masks. The primary implementation fixes bit23
absent and uses Gray-code updates. The independent implementation fixes
bit0 absent and uses binary traversal, then canonicalizes by the smaller
of a mask and its complement. They agree on all 8,388,608 pairs, all
4,255 vectors, their multiplicities and their least witnesses.

Every vector satisfies

    2c_t <= 3(c_s1+c_s3) + 4c_s2,
    2c_v <= 3(c_s1+c_s3) + 6c_s2.

These are dual bounds of 8 and 9 at prices (2,1,2). The two-cut
certificate attains both simultaneously. Full enumeration is a discovery
and independent finite-coverage result; sections 1-4 do not require
assuming an exhaustive search proves an all-parameter statement.

The same coordinate-cut lower-bound cone is obtained from all finite
permutation G-sets. Indeed, a transitive orbit is G/K. For H subset G/K,
its preimage H~ in G has c_g(H~)=|K|c_g(H) for every g. General G-sets
are disjoint unions of such orbits, and their crossing profiles add.
Conversely, the regular G-set is itself allowed. This proves equality
of generator/diagonal-endpoint profile cones; it does NOT identify
crossing ranks at arbitrary prefixes in regular and coset modules.
Arbitrary subspace cuts and nonpermutation representations are outside
this census.

## 6. What remains unproved

This is an algebraic tariff obstruction under the stated free alphabet.
It constructs no BIT supplier, does not establish a recursive child or
workspace recurrence, and makes no new kappa or selected-frontier claim.
The all-n statement concerns repeated outer transpositions. The S4
statement concerns the explicitly identified 20-target family and all
tuples drawn from it, not arbitrary tuples from all 24 permutations.
No human review, hosted CI run, or formal-kernel proof is asserted.
