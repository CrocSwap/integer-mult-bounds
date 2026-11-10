# A residue-field extension of the one-relation obstruction

This scoped proof is produced by Nick Petalas. The every-field theorem of
Josie Elliston's [PR6044](https://github.com/CrocSwap/integer-mult-bounds/pull/6044),
head `4ebdea4e95fa4cbf227b4be630f656105d96e5f7`, is a cited mathematical
premise. Its proof and scientific census are not replayed here. The new step
is specialization of the coefficient ring, including factors that disappear.

## Setting and cited premise

Let R be a nonzero commutative ring with identity. Let A_1,...,A_k be
nonzero rank-one rational d-by-d matrices. Write H for their additive
integer span. In the formal group algebra R[H], distinct matrices h give
independent basis symbols [h], and [h][g]=[h+g]. The integer exponent
labels are not reduced modulo the characteristic of R.

For W>=1 let N_j be idempotent W-by-W matrices over R, and suppose the
following formal identity holds:

    product_(j=1,...,k) (I + ([A_j]-1) N_j)
        = diag([C_1],...,[C_W]).                              (1)

The C_w belong to H, so are rational d-by-d matrices. Zero C_w are restored dirty registers.
The identity acts on arbitrary register contents; no zero initialization is
assumed. A global normalized outer product N_j=x_j y_j^T, y_j^T x_j=1,
is one important allowed case.

We use the following statement from PR6044. Over any field K, if all paid
projectors are rank-one idempotents and the rational span of the k paid
frames has dimension at least k-1, a formal diagonal monomial endpoint
has pairwise disjoint assignments

    C_w = sum_(j in I_w) A_j.

Consequently sum_w rank_Q(C_w)<=k. This is the exact prerequisite imported
from that work, including its arbitrary register count and restored roles.

## Theorem: one qualified residue field suffices

Choose a maximal ideal m of R and put K=R/m. Reduce N_j entrywise to
bar(N_j). Suppose every bar(N_j) has rank zero or one over K. Let

    J_m = { j : bar(N_j) != 0 },  n_m = |J_m|.

If n_m>0, assume

    dim_Q span { A_j : j in J_m } >= n_m-1.                   (2)

Then there are pairwise disjoint subsets I_w of J_m such that

    C_w = sum_(j in I_w) A_j,
    sum_w rank_Q(C_w) <= n_m.                               (3)

If J_m is empty, every C_w is zero and the same conclusion holds with
empty assignments. The hypothesis concerns this one residue field; no
constant rank or global outer-product representation of N_j is needed.

### Proof

The unital quotient map R->K induces a coefficientwise homomorphism
R[H]->K[H]. It fixes every formal label [h]. In particular its action on
(1) retains exactly the same C_w on the right. Distinct labels remain
linearly independent because 1_K is nonzero.

The reduced matrices are still idempotent. A zero reduced projector gives
an identity factor, which can be removed without changing the order of the
remaining factors. A nonzero rank-one reduced projector has a normalized
outer product: choose a nonzero vector x spanning its image. There is a
linear functional y^T with N(v)=x y^T(v). Idempotence and x!=0 give
N(x)=x, hence y^T x=1. Thus every surviving factor has precisely PR6044's
field form.

Let H_m be the additive integer span of the surviving frames. The entire
reduced left side lies in M_W(K[H_m]). Inclusion K[H_m]->K[H] is injective
on formal basis elements. Therefore each endpoint C_w belongs to H_m:
otherwise its coefficient 1 on the right could not occur on the left.
For n_m>0, apply the cited field theorem to this reduced, ordered word and
(2). It gives the disjoint subsets in (3). Rank subadditivity and the
rank-one hypothesis on each A_j give the displayed rank bound.

If n_m=0, the left side is I. Independence of formal labels gives
[C_w]=[0], hence C_w=0 for every w. This proves the empty case. QED.

## Corollary: nonfield free rank-one projectors do not escape

Suppose every N_j=x_j y_j^T over R with y_j^T x_j=1_R, and

    dim_Q span {A_1,...,A_k} >= k-1.

Then (1) implies disjoint assignment of the C_w to the original paid
frames and sum_w rank_Q(C_w)<=k, for every nonzero commutative R.

Indeed R has a maximal ideal. At every such ideal the normalized outer
product remains normalized, so each reduced projector is nonzero and has
rank one. Thus J_m is the full index set, and the theorem applies. This
covers Z/2^e for every e>=1, other Z/m with m>=2, nilpotents and zero
divisors. It uses the cited field theorem, rather than extending its
individual domain or graph arguments to rings with zero divisors.

The bound is sharp over every such R. Take k=d, A_j=E_jj, and N_j=E_11
on W>=1 scalar registers. Their product has endpoint

    diag([I_d],[0],...,[0]).

The rational target rank sum is d=k. All other registers are restored on
arbitrary inputs. There is no physical/native tariff claim in this example.

## Varying rank and the sharper active count

More generally suppose every N_j has rank at most one at every maximal
ideal, and the full frame list has at most one rational relation. Every
sublist also has at most one relation: its relation space injects into
the relation space of the full list by extending coefficients with zeros.
Thus the theorem applies at every maximal ideal, and

    sum_w rank_Q(C_w) <= min_m |J_m|.                        (4)

The minimum exists because its possible values lie in {0,...,k}. The
assigned subsets may depend on the chosen ideal. We assert neither one
assignment simultaneously describing all projectors nor a global
factorization of every idempotent. Vanishing two-by-two minors over R are
a sufficient, though unnecessary, way to ensure the required fiber rank.

For a concrete example over Z/6, take W=2 and

    N_1=3 E_11,  N_2=4 E_11,  A_1=A_2=A!=0.

Both matrices are idempotent, their product is zero, and their sum is
E_11. Multiplication gives

    (I+([A]-1)N_1)(I+([A]-1)N_2)
        = diag([A],[0]).

Exactly one factor survives modulo 2 and exactly one survives modulo 3.
Formula (4) gives the sharp bound one, although the written ring word has
two nonzero factors. Neither N_j admits a normalized global outer product:
it vanishes in one residue field, contradicting the reduction of y^T x=1.

By itself the first factor has diagonal entry 4+3[A], which is a monomial
in each residue field with different exponents there. It is not a formal
monomial over Z/6. This explains why the fixed global endpoint (1) matters;
component-dependent endpoints cannot be substituted for it.

## Scope

This extends PR6044's explicit nonfield question for commutative rings and
the stated residue-rank hypothesis. The general theorem can also apply
when the full frame list has more relations, provided one surviving
sublist satisfies (2). Noncommutative rings, rank-two residue projectors,
and surviving lists with two or more independent relations remain outside
this argument. A ring quotient alone does not supply a native operation,
legal physical endpoint, hosting, compiler, rounding or complete paid bill.
There is no new kappa or complete multiplication theorem. Independent human
and formal proof-kernel review are unclaimed.
