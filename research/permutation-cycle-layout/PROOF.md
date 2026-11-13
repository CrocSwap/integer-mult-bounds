# Optimal simultaneous column order for a wire permutation

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written proof. The finite replay corroborates bounded
instances; it is not the universal proof or a proof-kernel certificate.

## 1. Contract and result

Let n >= 1, d >= 2 and let pi be a permutation of {0,...,n-1}.
Each site is C^d. The full operator U_pi routes an input site to its
specified destination:

    U_pi[y,x] = product_i [y_(pi(i)) = x_i].

Every input and output coordinate is retained. There is no side information,
restriction to a subspace, dirty workspace, scalar phase or discarded output.
Choose one order o of the sites and use it for both input and output columns.
At a cut let A be the sites preceding it, B its complement, and put

    c(A) = |{i in A : pi(i) in B}|.

There are also c(A) wires from B to A, since pi is a bijection. A fixed-width
matrix-product representation may use different local tensors at different
positions, with scalar boundary bonds. Its peak bond is the largest internal
virtual dimension; define it as one when n=1.

**Theorem.** The coefficient unfolding across A|B has exactly

    r(A) = d^(2 c(A))

nonzero singular values, all with square d^(n-2 c(A)). In the prescribed
order the minimum possible peak bond is max_A r(A), over its prefix cuts.
When the simultaneous order may be chosen arbitrarily,

    min_order min_exact_train peak_bond = 1       if pi is identity,
                                       = d^2    otherwise.

Consecutive directed cycles attain the optimum. These are algebraic layout
statements. They do not assert that a caller permits that layout, that a
permutation description is available cheaply, or that physical reordering
has zero cost. The fixed-width representation does not invoke the all-width
fixed-table equivalence theorem of zxv's PR #5441.

## 2. Complete cut spectrum

Unfold U_pi with rows (y_A,x_A) and columns (y_B,x_B).
There are 2c crossing wires. Index their independent d-valued wire labels
by z. For fixed z, let u_z be the left 0/1 vector imposing the crossing
labels and every equality on an internal A-to-A wire. Define v_z on B
similarly. Orient each label by its original source wire, so that

    H = sum_z u_z v_z^T.

Different z have disjoint left supports and disjoint right supports: each
crossing label appears in a distinct left physical coordinate and a distinct
right physical coordinate. They therefore give orthogonal nonzero vectors.
There are |A|-c internal A-to-A wires. Each contributes one freely chosen
label after its equality constraint, independently of every other wire.
Consequently

    ||u_z||^2 = d^(|A|-c),
    ||v_z||^2 = d^(|B|-c).

Normalizing these orthogonal vectors gives a singular value decomposition
with d^(2c) equal singular values. Their squares are d^(n-2c).
In particular their sum is d^n, the squared Frobenius norm of U_pi.
This includes empty cuts and c=0. The same disjoint-support factorization
also proves the rank formula over any coefficient field.

## 3. Exact attaining tensor train

At each cut carry one d-valued state label for each directed wire whose
endpoints lie on opposite sides of that cut. Thus the virtual space has
dimension d^(2c). For a local tensor at site v, impose these equalities:

- Every wire present on both adjacent cut frontiers keeps its label.
- The wire with source v has label x_v at its source endpoint.
- The wire with destination v has label y_v at its destination endpoint.
- A self-wire imposes x_v=y_v locally.

All other tensor entries are zero. Both endpoint frontiers are empty.
Contracting the local tensors sums over every wire label. A full physical
input/output pair has exactly one satisfying assignment if it obeys every
routing equality, and has none otherwise. The contracted coefficient is
therefore precisely U_pi[y,x], with no multiplicative d factor or phase.
This constructs all cut dimensions simultaneously.

Conversely, at a bond of dimension D the unfolding factors through that
D-dimensional virtual space, so its rank is at most D. Section 2 forces
D >= d^(2c) at every cut. The explicit construction attains every such
lower bound in the prescribed order. It uses standard tensor-network
factorization; no new general factorization principle is claimed.

## 4. Optimal simultaneous order

Decompose pi into disjoint directed cycles. Place each cycle consecutively,
in its directed order, and concatenate the cycles. At any prefix, completed
cycles contribute no crossing wires. A cut strictly inside one nontrivial
cycle has exactly one wire from A to B and one from B to A. A cut between
cycles has no crossing wires. Hence the peak is at most d^2, or one when
all cycles are fixed points. The algorithm visits each site once after
validating the permutation.

For the lower bound, fix any order of a nonidentity permutation and consider
its first moved site v. Every preceding site is a fixed point. The site
pi(v) is another moved site, so it is still on the right. At the cut just
after v, exactly one A-to-B wire leaves, namely the wire from v. There is
at least one further moved site, so this is an internal cut. Section 2
forces bond at least d^2. Identity routing is a product of local identities
and has peak one. This proves the optimum for all n and d in the contract.

For the half-swap pi(i)=i+k modulo 2k, natural order has c=k at its middle
cut, giving peak d^(2k). The cycle order

    0,k,1,k+1,...,k-1,2k-1

alternates c=1 and c=0 and has peak exactly d^2. Thus the fixed-order
exponential obstruction from #5441 disappears under this simultaneous
layout change. Its physical legality and cost are a separate question.

## 5. Approximation consequence and its limit

Write N=d^n. At a cut of rank r, an arbitrary rank-D approximation to H
has optimal squared relative Frobenius error

    max(0,1-D/r).

Indeed its squared singular values are N/r, and projection can retain at
most D of them; truncating the displayed decomposition attains the bound.
Unfolding preserves the Frobenius norm. For a physical approximation V,
||V-U_pi||_F^2 <= N ||V-U_pi||_op^2, so cut bond D and operator error
at most epsilon imply D >= (1-epsilon^2)r. This is a necessary condition,
not an attaining operator-norm construction or a joint approximation at
all cuts. The projection argument is inherited classical reasoning, also
used for #5441's two original fixed-order examples.

## 6. Attribution and scope

[zxv #5441](https://github.com/CrocSwap/integer-mult-bounds/pull/5441)
provides the repository's physical-column transfer contract, the cut-rank
argument, the half-swap example and the explicit warning that reordering
changes the obstruction. Its native fixture, equivalence algorithm and
scientific verification are cited, not replayed. Its predecessor attribution,
including Krzysztof Wójt #5262, Ali Romman #5352 and Jose Manuel #2250,
remains in that unchanged package.

Cycle decomposition, operator-Schmidt rank, projection bounds and
matrix-product factorizations are classical. The new repository result is
the complete arbitrary-permutation cut spectrum, its explicit wire-label
train, and the sharp optimum over simultaneous orders, resolving the
algebraic layout subproblem. No global literature priority is claimed.
Nick Petalas #6184 concerns arithmetic chirp phases, a different endpoint;
its formulas and construction are not used here.

No fixed finite table uniform across all widths, legal physical reordered
caller, native/tape tariff, supplier admission, new kappa or complete
multiplication theorem follows. The selected frontier is unchanged.
Independent human and formal proof-kernel review are unclaimed.
