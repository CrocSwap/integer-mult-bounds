# Sharp terminal capacity with changed unmarked arrivals

This theorem concerns a binary rank relaxation. It constructs synthetic source
libraries. It neither implements a native operation nor changes the selected frontier.

## Model

Work over F_2. An old terminal basis of W consists of n unmarked vectors
u_1,...,u_n, b base vectors a_1,...,a_b, and s singleton vectors p_1,...,p_s.
Write U=span(u), B=span(a), and m=b+s. A marked payload changes from v to v+d_v.
The fixed allowed difference libraries obey

* d_a belongs to U+B for each of the b base positions;
* d_pi belongs to U+span(p_i) for each singleton position.

These are containment hypotheses. Libraries may be proper subspaces. At most h
of the n unmarked arrivals may change arbitrarily within W. All n+m final
arrivals must form a basis of W. Let U' span the n final unmarked arrivals.
Return stock is the dimension of the span of the marked differences in W/U'.
Reconstruction from the final basis is free. The model promises no chronological
program, restored named output or paid realization.

## Upper bound, credited context

ToikY's [PR #7258 NEXT.md](https://github.com/ToikY/integer-mult-bounds/blob/90a63fbefcf79c3e0c0453ef0741dff8517b6167/research/bit-fixed-payload-quotient-bound/NEXT.md)
gives the b=12, s=10 instance of this dimension bound. Its literal library census
and prices are cited results, not verified here. The short argument below fixes
the exact abstraction for the new sharpness theorem.

Let k count singleton differences whose image in W/U is p_i. Their new marked
arrivals vanish in W/U, since p_i+p_i=0. Other marked arrivals have joint quotient
rank at most b+s-k. The h changed unmarked arrivals add at most h quotient
dimensions. Full terminal rank implies k<=h.

All differences have rank at most b+k modulo U. Both U and U' have dimension n
and share the n-h unchanged unmarked basis vectors. Thus dim(U/(U intersect U'))<=h.
For every subspace X of W,

    dim((X+U')/U') <= dim((X+U)/U) + dim(U/(U intersect U')).

Indeed, project (X+U+U')/U' onto (X+U+U')/(U+U'). Its kernel has dimension
dim(U/(U intersect U')); its image is a quotient of (X+U)/U. Apply this to the
span of the differences. Return stock is at most b+k+h, hence min(m,b+2h).

F_2 matters. Over F_3 even a lone marked position with d=p has a nonzero new
arrival 2p, without any changed unmarked arrival.

## New attaining construction

For every even b>=0, every n,s>=0 and 0<=h<=n, the upper bound

    maximum return stock = min(b+s, b+2h)

is attained with the fixed maximal libraries U+B and U+span(p_i). The same
libraries serve every budget h. Only the chosen payloads and unmarked arrivals
vary. There is no stronger universal bound from these dimension and singleton
containment hypotheses alone.

For one unmarked vector u and two singleton vectors p,q, choose

    old unmarked u -> new unmarked p+q
    marked p      -> new marked u       with d_p=p+u
    marked q      -> new marked q+u     with d_q=u.

Both differences belong to their fixed singleton libraries. The new arrivals
(p+q,u,q+u) are a basis. From their values (x,y,z), recover

    u=y, q=z+y, p=x+z+y.

Modulo U'=span(p+q), the differences p+u and u are independent. In an equality
alpha(p+u)+beta u=gamma(p+q), the q coefficient forces gamma=0, then the p
coefficient forces alpha=0, and finally beta=0. One changed unmarked arrival
therefore earns two independent difference directions.

For one remaining singleton p, use u->p and p->u, with d_p=p+u. This earns one
direction modulo the new unmarked span. Leave other singletons and unmarked
arrivals unchanged. Use min(h,floor(s/2)) disjoint three-vector gadgets, followed
by the two-vector gadget only when s is odd and budget remains. They earn exactly
min(s,2h) directions. Disjoint supports make both the endpoint bases and quotient
directions combine by direct sum.

For every pair of base vectors a,c, choose d_a=c and d_c=a+c. New arrivals are
a+c and a. Both difference and arrival pairs are bases. These disjoint blocks earn
all b base directions with no unmarked changes and no intersection with the
singleton gadgets. This proves the formula.

## The 523+22 shape and its boundary

For n=523, b=12 and s=10, the synthetic construction has terminal rank 545 and
return stocks 12,14,16,18,20,22 at budgets h=0,1,2,3,4,5. All 523 new unmarked
arrivals remain independent. No extra arrival slot is used.

It can retain the base support partition 3+3+2+4 reported by #7258. A three-vector
base block uses differences (c,d,a+c) on (a,c,d). New arrivals are
(a+c,c+d,a+c+d); both triples have determinant one. The two-vector block above
and its direct sum handle sizes two and four. The partition itself therefore
cannot exclude the synthetic attainment.

Five changed unmarked arrivals suffice for stock 21 or 22 in this abstraction,
and four cannot suffice. This proves sharpness of the source's dimension-only
necessary condition. It does not assert that five actual BIT arrivals have these
payloads, that actual singleton libraries contain the required u components, or
that free basis reconstruction has an affordable legal caller. Those are the next
discriminating constraints. This package does not enumerate the source's 523 ports
or recheck its stock values.

## Finite corroboration and implementation bounds

The verifier checks every constructed endpoint and quotient stock by binary
elimination. Small instances also use an independent span-cardinality oracle.
It enumerates every unmarked replacement and allowed difference in ten complete
small maximal-singleton models. These are complete finite certificates for their
declared domains; the written direct-sum argument supplies the all-size scoped proof.

Every loop has a finite domain. Ambient dimension is at most 545; rank calls have
at most 1,090 rows. Span sets have at most 64 elements in the construction checks
and 32 in the complete models. The largest complete model has 16,384 assignments. The construction
sweep fixes n<=4, b in {0,2,4,6,12}, s<=10, h<=n, then checks six 545-dimensional
witnesses. Functions stay below 60 lines. Explicit exceptions keep checks active
under optimized Python. Python integer, container, JSON and hashing allocation is
a managed-runtime deviation from fixed steady-state allocation; the finite
dimensions above bound live mathematical state. No recursion, dynamic code,
external process or third-party dependency is used. Warning-strict execution
supplies interpreted diagnostics.
