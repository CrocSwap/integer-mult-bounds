# Maintainer supplement: the even-target tariff is exactly 2t at every register count

This supplement arose while reviewing Aaron Wang's PR1763 and its independently
implemented finite census. It uses the stated formal F2[GL2(F2)] model only.
It gives no multiplication supplier or kappa improvement.

Let the target be diag([c],...,[c],[e],...,[e]) on r registers, with t copies
of c=ab and r-t unchanged dirty registers, where 0<=t<=r. Paid calls are
I+N([g]+[e]), g in {a,b}, with N a binary rank-one idempotent. Arbitrary
scalar GL_r(F2) changes of register basis are free.

Move all scalar basis changes to one side by conjugation. They preserve the
allowed rank-one idempotent class, so the circuit has the form U C1...Cq.
The augmentation homomorphism F2[G] -> F2 sends every group element to 1.
It sends every paid call and the target to I_r, and sends U to itself.
Hence an exact formal implementation necessarily has U=I_r.

Now apply the two-dimensional natural representation entrywise. In this image,

    a = [[1,1],[0,1]], b = [[1,0],[1,1]], c = [[0,1],[1,1]].

Both a-I and b-I have rank one, while c-I=[[1,1],[1,0]] has rank two over F2.
Thus each paid call differs from identity by N tensor (g-I), of rank one.
For any same-size matrices A,B,

    AB-I = (A-I)B+(B-I),
    rank(AB-I) <= rank(A-I)+rank(B-I).

Induction gives rank(C1...Cq-I)<=q. The natural image of the target differs
from identity by t disjoint rank-two blocks, so its rank difference is 2t.
Therefore q>=2t, for all t and all r>=t. This is only a necessary image test,
which is sufficient for a lower bound; no faithfulness of the representation
of the group algebra is assumed.

For the matching formal upper bound, use the coordinate projector N=E_ii and
one a-call followed by one b-call for each of the t target registers. Since
N^2=N, their product is I+N([ab]+[e]). Different coordinate projectors are
disjoint. The resulting 2t-call word is the exact formal target and is identity
on every extra register. Consequently the optimum is exactly 2t, including
arbitrary restored dirty extras within this model.

This settles the general-t and extra-register questions posed in PR1763's
original finite-census README. Its finite state counts, corrected short-degree
analysis and separate formal/natural engines remain independently useful
verification contributions. This argument does not establish a three-call
SWAP lower bound: the natural SWAP-minus-identity has rank one, not three.
It also does not apply unchanged to richer paid calls, additional free
operations with nontrivial augmentation kernel, different target actions or
physical recursive prices.

Credit: Aaron Wang's PR1763 identifies and implements the even-target model;
the scalar normalization and model lineage are credited in that package to
Gareth Davidson, commdata2338 and other predecessor contributors. The short
rank argument above is a maintainer review supplement prepared with OpenAI
Codex assistance, not a novelty or priority claim. Apache-2.0.
