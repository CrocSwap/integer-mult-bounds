# Sharp integer inertia certificates for two-facet downsets

This contribution was produced by Nick Petalas. Apache-2.0.

**Claim type: scoped mathematical proof with exact finite corroboration.**
Every finite downset with at most two maximal members and at least one
nonempty member admits a nonsingular, symmetric, nonnegative integer matrix
supported on disjoint pairs, with exactly as many positive eigenvalues as
its largest star. Thus its optimal number of nonnegative eigenvalues is
exactly that star size.

This proves the two-facet case of Ellis, Filmus and Friedgut's
[Conjecture I, section 4](https://arxiv.org/html/2609.28404v1#S4), recorded as
C070 in David Ganz's [atlas, PR2849](https://github.com/CrocSwap/integer-mult-bounds/pull/2849).
The contribution is the explicit construction and all-size congruence below.
No global literature priority is claimed. The general downset conjecture,
physical suppliers and a new kappa remain outside scope.

## Statement and explicit entries

Write the downset as

```text
D = 2^(C union A) union 2^(C union B),
C, A, B pairwise disjoint; |A|=a >= b=|B|; |C|=c.
```

For two distinct maximal members, take their intersection as C and their
differences as A,B, so a,b >= 1. A single maximal member is included by
taking B empty. Unused ground elements do not affect the construction.
Fix an injection iota:B -> A.

First set c=0 and list all subsets S of A, followed by all **nonempty**
subsets T of B. Define the base matrix K as follows:

- Within either of these two lists, K(U,V)=1 if U and V are disjoint,
  and zero otherwise.
- Between S subset A and nonempty T subset B, put
  K(S,T)=K(T,S)=h(|S intersect iota(T)|), where
  h(0)=1 and h(k)=2^k-1 for k>=1.

These cross pairs are always disjoint in the actual ground set. The
injection only defines weights; it does not identify ground elements.
For general c, put

```text
M((R,U),(R',V)) = 1[R intersect R' is empty] K(U,V).
```

Here R,R' subset C and U,V are base labels. In particular M is symmetric,
integral and nonnegative, and M(X,Y)=0 whenever X intersect Y is nonempty.
The empty-set diagonal is 1, as permitted by the conjecture.

Let N=2^c(2^a+2^b-1), and let s be the largest star size. Then

```text
s = 2^(a-1)           if c=0,
s = N/2               if c>=1.
inertia(M) = (s, N-s, 0).
det(M) = (-1)^(N-s) 3^e,
e = 2^c(2^(b-1)-1)   if b>=1, and e=0 if b=0.
```

The c=0 case has a>=1 by the nonempty-member hypothesis. The case
a=b=0,c>=1 is the ordinary full cube and is included separately below.

## All-size proof

For the Boolean cube on r elements, let Z_r(S,T)=1[T subset S],
J_r(T,T)=(-1)^|T|, and D_r(S,T)=1[S intersect T is empty].
Order subsets by any linear extension of inclusion. Then Z_r is unit
lower triangular, and

```text
D_r = Z_r J_r Z_r^T,
```

since its (S,T) entry is the sum of (-1)^|U| over U subset S intersect T.
For r>=1 exactly half the diagonal entries of J_r have each sign.

Assume b>=1, so a>=1. Let Z' and J' be the restrictions of Z_b and J_b
to nonempty subsets. Set u(T)=(-1)^(|T|+1). Summing over nonempty
subsets proves Z'u=1. Deleting the empty row and column from D_b gives

```text
D_b[nonempty,nonempty] = Z'(J' + uu^T)Z'^T.
```

Let e0 denote the empty-subset coordinate in the A cube. Define a
2^a by (2^b-1) matrix E whose column T is the coordinate vector at
iota(T) if T has positive even cardinality, and zero if T has odd
cardinality. Distinct nonzero columns are distinct coordinate vectors,
all at positive diagonal entries of J_a, and none at e0. Therefore

```text
J_a E = E,    e0^T E = 0,
E^T E = diag(1[|T| is positive and even]).
```

Put H=e0 u^T + 2E. The cross block of K is Z_a H Z'^T: its entry
is 1 plus twice the number of nonempty even subsets of
iota^(-1)(S) intersect T. For intersection size k, that number is
zero if k=0 and 2^(k-1)-1 otherwise. This is exactly the prescribed h(k).
Consequently congruence by diag(Z_a,Z') reduces K to

```text
             [ J_a       H         ]
             [ H^T       J' + uu^T ].
```

Eliminate the invertible upper-left block J_a. Its Schur complement is

```text
J' + uu^T - H^T J_a H = J' - 4E^T E.
```

This is diagonal: -3 on nonempty even subsets of B, and -1 on odd
subsets. It is negative definite. Sylvester's law of inertia gives
exactly 2^(a-1) positive eigenvalues of K, with every other eigenvalue
negative. All congruence factors used have determinant one. There are
2^(b-1)-1 entries -3, so |det K|=3^(2^(b-1)-1).

If b=0, K=D_a; its zeta congruence gives the same inertia conclusion
when a>=1 and determinant of absolute value one. If a=b=0, K=[1].

For c>=1 the full matrix is D_c tensor K. The symmetric invertible
matrix D_c has equally many positive and negative eigenvalues, so
tensoring with any invertible symmetric K gives N/2 eigenvalues of
each sign. Also |det D_c|=1, so |det M|=|det K|^(2^c).
This proves all stated determinant and inertia formulas, including
the a=b=0 case.

For c=0, a coordinate in A lies in 2^(a-1) members; one in B lies
in 2^(b-1) members. For c>=1, a coordinate in C lies in N/2 members.
The other star sizes are 2^c 2^(a-1) and 2^c 2^(b-1) when those
coordinates exist, each at most N/2. Thus the positive count equals s.

Finally, any symmetric disjointness-supported matrix has a zero
principal block on a star of size s. Its quadratic form vanishes on
that s-dimensional coordinate subspace. If it had fewer than s
nonnegative eigenvalues, its negative eigenspace would intersect that
subspace nontrivially, contradicting negative definiteness there.
This proves optimality among all real supported symmetric matrices.

## First fixture and verification

For a=b=2,c=0 there are seven sets and s=2. The ordinary disjointness
matrix has inertia (3,4,0). The construction changes just the weight
between the two full exclusive facets from 1 to 3, producing inertia
(2,5,0) and determinant -3. Weight 2 instead gives inertia (2,4,1),
so its zero eigenvalue still leaves three nonnegative eigenvalues.

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/two-facet-downset-inertia/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/two-facet-downset-inertia/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/two-facet-downset-inertia
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/two-facet-downset-inertia --check-source-history
```

Any CPython 3.12 can replace the local interpreter path. The standalone
standard-library verifier needs only its package; it does not load atlas
code or fetch the paper. The source pin identifies the originating
question, not a mathematical dependency needed by the proof.

The verifier enumerates all **49 triples** a>=b>=0,c>=0 with
1<=a+b+c<=6, including degenerate single-cube presentations. It constructs
each matrix literally, checks every support entry, counts each star,
checks the integer zeta congruence, and computes inertia and determinant
by independent exact rational symmetric elimination, with 1-by-1 and
2-by-2 pivots. This covers matrices through order 64. These finite checks
corroborate the all-size proof; they do not replace it.

Eight control checks include the unweighted failure, the first positive
fixture, the singular weight-two modification, zero-diagonal pivots,
zero eigenvalue counting and invalid inputs. Explicit exceptions keep
checks active under optimization. JSON output records each case and
SHA-256 of the package files; no receipt is hand-written or stored.

The bounded loops use at most six ground coordinates and matrix order
64. Each function fits within 60 lines. Python allocates rational
numbers and lists dynamically; this managed-runtime deviation is bounded
by these fixed domains and the fixed five-file package inventory.
Warnings are errors in both registered modes. No additional static
analyzer is assumed. No recursive calls or background processes occur.

## Scope, overlap and credit

David Ganz's PR2849 supplies atlas C070 and its research direction.
Ellis, Filmus and Friedgut formulate the spectral conjecture; their
general intersecting-family and projection-packing theorems are not
reproved or needed here. The Boolean zeta identity and Sylvester
congruence are classical tools. This package adds a constructive
two-facet specialization, including the weights, inertia and determinant.
The atlas's credit lines and all predecessor files remain unchanged.

Canonical base is ff3cc58e370d0f678e529246f8c73e8094e18fcf, priority
revision 7. TASK.json marks the formal-interface-lemma card as changed:
this is an algebraic side result on an explicit open certificate
question, with no claimed implication for the selected supplier.
Live open/account PRs, active Discussions, recent account handoffs,
local reservations, merged searches and main README searches showed
no matching two-facet inertia contribution. The cached overlap search
covered 311 open PRs and 4,483 Discussion records; only 187 of 7,091
HEAD notes were materialized. Targeted main-tree searches supplement
that sparse coverage. Unpublished work and global literature priority
remain outside the novelty claim.

Independent human and formal proof-kernel review are unclaimed.
No Lean, Docker, selected cold replay, physical caller, compiler,
precision, storage or complete multiplication theorem is certified.

## Open next questions

Can a disjointness-supported integer matrix achieve the largest-star
inertia for downsets with three maximal sets? Start with three pairwise
disjoint two-element facets and write the zeta-basis cross blocks.
This tests whether positive directions can be coupled without increasing
the final positive count. The blocker is simultaneous control of the
three Schur interactions; the two-facet negative complement alone does
not settle it. The full spectral conjecture remains separate.
