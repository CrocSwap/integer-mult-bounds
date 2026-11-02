# Exact distinguished-factor invocation tariff

This scoped written proof concerns the static ordered, parent-reserved dirty
array grammar of Koroffstrogov's PR758. It does not claim optimality among
arbitrary reversible programs. The contribution was produced by Nick Petalas.

## Model and theorem

A leaf is one complete signed invocation of a fixed factor. Every internal
node has k>=2 nonempty consecutive children. Its complete echo invokes the
first and last child twice and each interior child four times, including all
inverses and restoration. Its reserved-array requirement is

    S(leaf)=0,
    S(node)=k-1+max_child S(child).

The invocation multiplicity of a leaf is the product of its child multipliers
along its path from the root. This is exactly the quantity multiplying that
factor's fixed positive invocation price. Factors retain their original order.

The complete echo identity, source preservation and arbitrary dirty-array
restoration are cited from PR758, Section 1, with androolloyd's PR673 credit
retained. For ideal linear factors, every admitted tree realizes the same
ordered product. No new assertion is made that different trees have identical
rounded nonlinear errors or dirt-dependent increments.

Let s>=0, 1<=n<=2^s, and 0<=i<n be integers. Put L=i and R=n-1-i. For d=0,...,s
set u_d=2^(s-d). Define d_* as the first depth satisfying

    ceil(L/u_d)+ceil(R/u_d) <= 2^d-1.                  (1)

There is such a depth, since d=s gives L+R=n-1<=2^s-1.

**Theorem.** Among all admitted trees on n leaves with S<=s, the least complete
invocation multiplicity of factor i is exactly 2^d_*. A binary tree attains it.
Thus higher arities cannot improve this one-factor objective, even though
PR758 shows they can improve the sum of all factor prices.

The theorem gives at most s+1 integer tests, once the powers of two are
available. This is an arithmetic operation count, not a bit-complexity or
physical tape implementation bound. The bounded reference accepts s<=10.
The proof itself has no upper bound on s.

## Capacity and replacement along one path

We use PR758, Section 2, as a cited capacity lemma: a tree of requirement at
most t has at most 2^t leaves, and every positive number at most 2^t fits in a
binary tree of requirement at most t. The latter also follows by pruning a
complete height-t binary tree and suppressing unary vertices. This citation
is a premise, not a replay of the predecessor optimizer or its numerical table.

We first prove that every marked tree of budget s has a binary replacement,
with the same ordered leaves, budget at most s, and no greater multiplicity
at its marked leaf. Induct on the number of leaves. At a k-child root let
r=s-k+1>=0. Every child has at most 2^r leaves.

If the marked child is an endpoint, combine all other children into one
ordered group. That group has at most

    (k-1)2^r <= 2^(s-1)

leaves, since k-1<=2^(k-2) for k>=2. A binary root can host this group and the
marked child, each with budget s-1. Replace the group by a fitting binary tree
and replace the marked child by induction. The marked multiplier at this root
is still two. The case k=2 is included.

If the marked child is interior then k>=3. Suppose p children precede it and
q=k-1-p follow it, with p,q>=1. Let A and B be the leaf counts in those two
ordered groups. Then

    max(A,B) <= (k-2)2^r <= 2^(s-1),
    min(A,B) <= floor((k-1)/2)2^r <= 2^(s-2).       (2)

For the second inequality use floor((k-1)/2)<=2^(k-3), valid at k=3 and for
all larger k. The first uses k-2<=2^(k-2). Both are elementary integer
inequalities and can also be proved by induction on k.

Put the larger group in one child of a binary root. Its other child is a
binary node containing the smaller group and the marked child, in the order
required by the original factors. If the left group is larger the shape is
`(left,(marked,right))`; otherwise it is `((left,marked),right)`. The side
groups fit by (2), and the marked child fits at budget s-2 because r<=s-2.
Replace the marked child by induction, using that budget. The distinguished
path now has two binary edges, with multiplier four, equal to its old
interior-child multiplier. Its ordered factors and total budget are preserved.

The induction decreases the size of the marked child. Unmarked groups use
only the cited fitting lemma. This proves binary replacement. No assertion
about the other factors' multiplicities is made or needed.

## The exact binary depth condition

In a binary tree S is its height and a leaf at depth d has multiplicity 2^d.
Consider a marked leaf at depth d<=s. At path level j=1,...,d, its sibling
has capacity at most 2^(s-j). It lies entirely before or entirely after the
marked leaf in the ordered factor list. Therefore the capacities on the two
sides have the form

    u_d m,     u_d(2^d-1-m)

for some integer m between zero and 2^d-1. Indeed the sibling capacities are
u_d times 2^(d-1),...,1, assigned to the two sides according to the path bits.
Every factor before the marked leaf belongs to a preceding sibling, and the
same holds for factors after it. Hence

    L <= u_d m,     R <= u_d(2^d-1-m),

which implies (1). Any binary marked leaf consequently has depth at least d_*.
The replacement result transfers this lower bound to every original arity:
its binary multiplicity is at least 2^d_* and at most the original multiplicity.

For attainment, choose d=d_* and m=ceil(L/u_d). By (1), there are at least L
positions in the first m dyadic blocks of size u_d and at least R positions in
the blocks strictly after block m. In a complete height-s ordered binary tree,
keep any L leaves in those preceding blocks, one leaf in block m, and any R
leaves in the following blocks. Delete all other leaves and suppress every
unary vertex. The resulting ordered tree has exactly n leaves and height at
most s. All branching inside the marked block disappears, so the marked leaf
has depth at most d. The already proved lower bound makes its depth exactly d.
This is a constructive proof for every permitted n,s,i, including n=1,s=0.
The reference chooses the leftmost available positions on each side and
constructs the compressed tree bottom up, without recursion.

## A sharp position effect and weighted consequence

For s>=2 and n=2^s-1, the theorem simplifies to

    min multiplicity at i = 2^(s-1), if i is even,
                            2^s,     if i is odd.   (3)

For d<=s-2, u_d>=4. Even ignoring the separate ceilings, (1) would require
n-1<=2^s-u_d, but n-1=2^s-2, so it fails. At d=s-1, u_d=2 and L+R=2^s-2.
When i is even, both sides are even and the ceiling sum is 2^(s-1)-1. When
i is odd, both are odd and the sum is 2^(s-1). Only the former satisfies (1).
Depth s always works. This proves (3) without extrapolating from finite checks.
For seven factors and three arrays the exact vector of individual minima is

    (4,8,4,8,4,8,4).

For any fixed positive prices c_0,...,c_(n-1), every complete schedule costs
at least sum_i c_i 2^d_*(n,s,i). This follows by applying the individual lower
bounds to the same tree and adding them. The bound need not be jointly
attainable. The theorem constructs an optimum for one designated factor at
a time; it does not solve arbitrary weighted total-cost optimization.

## Evidence boundary and credit

The universal result rests on the replacement and capacity proof above.
`verify.py` gives finite corroboration of this new quantity using a complete
all-arity marked recurrence, a separate enumeration of whole ordered trees,
and emitted binary witnesses. It does not import or replay any predecessor
executable, counts, supplier or scientific verifier.

Koroffstrogov / PR758 supplies the ordered all-arity weighted grammar and its
capacity lemma. androolloyd / PR673 supplies the multiway echo and restoration.
Dillon Amburgey / PR689, Sagar Thakrar / PR730, Ali Romman / PR744, Alexander
Schwartzman / PR784 and Gareth Davidson / PR887 retain their optimization,
budget and formalization credit, as does Chafik Boukhalfa / PR628 for the
rounded-leaf lineage. Nick Petalas / PR4862 concerns maximal equality of a
total-unit-cost bound; none of its results is used in this proof. Dyadic trees,
ordered prefix codes and unary suppression are classical. No general
literature priority is claimed for those methods.

Static parent reservation, nonempty ordered children and complete signed calls
are essential. Connector reuse, clean checkpoints, changed restoration words,
opened child bodies, reordered or commuting factors and general reversible
circuits have different contracts. Physical data movement, actual coefficient
prices, precision, stock, compiler/native admission, analytic recovery and all
five selected framework assumptions remain separate. No new kappa, completed
supplier or complete multiplication theorem follows. Independent human and
formal proof-kernel review are unclaimed.
