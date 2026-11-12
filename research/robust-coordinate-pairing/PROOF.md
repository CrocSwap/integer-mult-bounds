# Exact common pairings under coordinate uncertainty

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written algebraic proof with exact finite corroboration.
The argument uses classical matrix rank, rank factorization and outer products.
No claim of general literature priority is made for those tools.

## 1. Contract and theorem

Let F be any field, B an m by n matrix over F, and E a subset of
{1,...,m} times {1,...,n}. The uncertainty family is

    B(t) = B + sum_{(i,j) in E} t_ij e_i e_j^T,  t_ij in F.

For r >= 0, a common identity pairing consists of fixed matrices X of size
r by m and Y of size n by r such that

    X B(t) Y = I_r                                               (1)

for every parameter choice. X and Y cannot depend on t. Empty matrices give
the r=0 convention. Write B[A,C] for the submatrix with row set A and column
set C. A rectangle A times C is clean when it is disjoint from E.

**Theorem.** The largest r satisfying (1) is exactly

    c(B,E) = max_{A,C: (A times C) intersect E = empty} rank B[A,C]. (2)

Empty rectangles have rank zero. The same answer holds if (1) is requested
only for the nominal B and the single-entry alternatives B+e_i e_j^T, one
for each (i,j) in E. No large or infinite field hypothesis is needed.

**Upper bound.** Subtract the nominal equation from each single-entry
alternative. For every (i,j) in E this gives

    (X e_i)(e_j^T Y) = 0.                                       (3)

An outer product over a field is zero only if one factor is zero. Let A be
the indices of nonzero columns of X and C the indices of nonzero rows of Y.
Equation (3) says that A times C is clean. Consequently

    r = rank(X B Y) = rank(X[:,A] B[A,C] Y[C,:])
      <= rank B[A,C] <= c(B,E).

**Attainment.** A rank-d clean submatrix has a nonsingular d by d minor
B[A',C']=M. Let S select rows A' and let T embed into coordinates C', in the
corresponding orders. Then X=M^{-1}S and Y=T satisfy XBY=I_d. For every
(i,j) in E, either i is outside A' or j is outside C'. Thus Xe_i e_j^T Y=0,
so the same X,Y satisfy (1). Restricting this identity pairing attains every
r<=d. For d=0 use empty matrices. This proves (2).

Necessity used only the nominal and single-entry alternatives. Sufficiency
uses linearity. This proves the assertion for the smaller finite family too.
The finite oracle directly enumerates the single-entry alternatives; it does
not assume the outer-product factorization when computing its answer.

## 2. Identity nominal pairing and its error graph

For B=I_n, construct a graph on n coordinates. An error (i,j) forbids an
independent set from containing both i and j. A loop (i,i) forbids i itself.
Direction has no effect on independence; one directed edge suffices.

**Corollary.** c(I_n,E) equals the independence number alpha(E), with this
loop convention. Arbitrary dense X,Y cannot improve on coordinate selection.

Indeed rank I_n[A,C]=|A intersect C|. If A times C is clean, A intersect C is
independent, so (2) is at most alpha(E). Conversely an independent set S gives
the clean rectangle S times S, with submatrix I_|S|. Coordinate selection
therefore attains alpha(E) over every field.

For the directed cycle E={(1,2),(2,3),...,(n-1,n),(n,1)}, n>=3, the sharp
value is floor(n/2). Summing the n inequalities
1_S(i)+1_S(i+1)<=1 gives 2|S|<=n, and alternating vertices attain the bound.
In particular the five-cycle admits exactly two common channels. Yet each
individual alternative I_n+e_i e_j^T in this cycle is invertible, with inverse
I_n-e_i e_j^T since i!=j. Thus the loss already occurs for a finite family of
n+1 entirely invertible maps. It is not caused by including a singular
simultaneous perturbation.

Replacing each single-entry alternative by B+a_ij e_i e_j^T, for any nonzero
fixed a_ij, leaves the answer unchanged. Divide (3) by a_ij for necessity.
Arbitrarily small nonzero errors over R or C therefore have the same exact
obstruction. Approximate output contracts require a different theorem.

## 3. Boundary witnesses

Independent coordinate uncertainty cannot be replaced by support alone when
coefficients are correlated. Over Q, put

    B = I_3,
    D = [[0,1,1],[-1,0,1],[-1,-1,0]],
    Y = [[1,1],[-1,0],[1,0]],
    X = [[0,-1/2,1/2],[1,1/2,-1/2]].

Direct multiplication gives XY=I_2 and XDY=0, hence X(I_3+tD)Y=I_2 for
every t. The nonzero-entry support of D is the complete loopless graph,
whose independent-coordinate capacity is only one. Correlation changes the
uncertainty space and escapes the theorem. This is a boundary witness.

The identity-graph corollary also cannot replace (2) for arbitrary B. For
B=[[0,1],[1,0]] with uncertain diagonal entries, the graph has a loop on
every vertex. Nevertheless X=[1,0] and Y=[0,1]^T give one common channel.
Formula (2) finds the clean off-diagonal minor and gives exactly one.

## 4. Helper relevance and limitations

The new premise requires a proposed helper interface to use the same two
linear maps for the nominal pairing and specified coordinate alternatives.
Equation (1) is necessary for every stronger interface requiring that
identity block. Formula (2) exactly solves this optimistic algebraic
relaxation. A failed capacity test excludes that common-pairing contract.
No selected supplier is asserted to have this uncertainty family.

For square B, every solution of positive size has full row rank X and full
column rank Y, since XBY=I_r. They extend to separate invertible output and
input bases over F. This does not force either off-diagonal block of the
transformed B(t) to vanish. Arbitrary dirty spectator independence,
restoration, chronological delivery and invertible dyadic completion require
additional conditions. Extra workspace, adaptive bases, correlated errors,
nonlinear decoders, approximate recovery and coefficients in rings with zero
divisors are outside this statement. Over rings, (3) need not kill a factor.

No producer, native word, scalar schedule, paid/target histogram, precision
policy, physical hosting, storage or tape implementation is supplied. Their
costs are unknown and are not zero. This side result changes no selected
frontier and proves no complete multiplication theorem. All five selected
framework assumptions remain. The universal statement rests on the written
proof. Independent human and formal proof-kernel review are unclaimed.
