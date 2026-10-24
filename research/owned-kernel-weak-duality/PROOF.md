# Exact weak duality for the retained functional-1 invoice

Let C=302177585/100000000000, p=1-C and P_r=r^p for 0<=r<=9
(with P_0=0). For every binary contact assignment in the exact
`owned-kernel-shared-map` functional-1 model, the complete paid-minus-helper
moment is at least its value at the unchanged source. Equality is attained
by the unchanged source. This is a fixed finite model theorem, not a bound
on changed contact spaces, other functionals, or all multiplication mechanisms.

## Full source objective

The pinned source builder supplies all nodes, frozen contacts, old/new spaces,
paid edges and productive helpers. A contact is variable precisely when it is
not frozen and its two spaces differ. There are 9,188 variables. A two-contact
rank table (r00,r10,r01,r11), with sign +1 for a paid edge and -1 for a helper,
contributes the following difference from its unchanged value:

    a*x + b*y + v*x*y,
    a = sign*(P_r10-P_r00), b = sign*(P_r01-P_r00),
    v = sign*(P_r11-P_r10-P_r01+P_r00).

A fixed endpoint is zero; a self-edge contributes
sign*(P_r11-P_r00)*x. Summing yields E(x)=sum a_i*x_i + sum v_ij*x_i*x_j.
All coefficient vectors are exact integers in (P_0,...,P_9). No floating
threshold removes a term. There are 14,480 nonzero pairs, of which 20 have
positive v. The 408 helpers remain productive, with histogram
{4:28,7:7,8:47,9:326}; paid histogram is
{1:2201,2:412,3:510,4:127,5:40,8:8}. Every former zero persistent edge is
included. All eight owned COPY centers pay their full changed r^p. The
72 shared late native maps and twelve frozen prelude line constraints are
inherited unchanged. No rank-subtracted center discount or unpriced helper
has been introduced. The retained source proves its native rank minima;
this certificate consumes that exact rank model rather than synthesizing G.

## Doubled signed-cut lower bound

Write w_ij=-v_ij/2 and d_i=a_i+sum_j v_ij/2. On binary contacts,
E(x)=sum d_i*x_i + sum w_ij*|x_i-x_j|. Introduce independent binary literals
z_i,z'_i. Replace the unary by d_i*(z_i+1-z'_i)/2. For w>=0 replace its
term by w*(|z_i-z_j|+|z'_i-z'_j|)/2. For w<0 replace it by
w + (-w)*(|z_i-z'_j|+|z'_i-z_j|)/2. Call the sum F(z,z'). At the
consistent lift (x,1-x), F=E, term by term. Allowing independent literals
is a relaxation and therefore a lower bound on the original binary problem.

Four times F is a graph cut plus a constant independent of the literals.
Each undirected edge is represented by two directed arcs. For negative v,
same-copy edges have capacity -v; for positive v, cross-copy edges have
capacity v. Terminal coefficient at i is 2*a_i+sum_j v_ij, with its negative
at i'. A positive coefficient c gives an arc i->sink of capacity c; a
negative coefficient gives source->i of capacity -c, with a constant offset.
The source side represents literal1. All capacities are nonnegative.
Thus Cut(x,1-x)-Cut(0,1)=4*E(x). This algebra includes the constants from
negative terminal coefficients and negative signed-cut terms; subtraction
at the explicit baseline eliminates them, not any assignment-dependent cost.

The stored witness has one flow vector for each of the 61,138 directed arcs.
The verifier independently reconstructs the graph and checks 0<=flow<=capacity,
exact conservation at all 18,376 internal vertices, and terminal balance.
It then sums capacities across the explicit baseline cut (original literals0,
complement literals1) and checks equality with the flow value as an integer
coefficient-vector identity, ignoring only P_0=0. Both equal

    -892 P_0 +556 P_1 -232 P_2 +504 P_3 -24 P_4
    +96 P_5 -8 P_6 -24 P_7 -36 P_8 +60 P_9.

For any cut, flow conservation expresses its value as outgoing flow minus
incoming flow; this is at most the outgoing capacity. Therefore every cut
has value at least this witnessed baseline cut. Consequently E(x)>=0 for
all 2^9188 binary assignments. The baseline attains E=0. The optimizing
Dinic implementation is not trusted by this argument and is not run during
normal verification. Only its saved feasible witness is checked.

## Rigorous real-number inequalities

For r=2,...,9 set z=(r-1)/(r+1). The rational sum
L=2*sum(j=0..399) z^(2j+1)/(2j+1) satisfies

    L < log(r) < L + 2*z^801/(801*(1-z^2)) = U.

This follows by integrating the geometric series; the positive tail has all
denominators at least801. For 0<a<1, the alternating exponential series
through degree31 is a lower bound on exp(-a), and through degree30 is an
upper bound. Here 0<C*L<=C*U<1. Applying the lower polynomial at C*U and
upper polynomial at C*L, then multiplying by r, bounds P_r. All arithmetic
is Python Fraction arithmetic. Flooring the lower endpoint and ceiling the
upper at denominator10^60 gives the recorded outward enclosures. P_0 and
P_1 are exact. No floating calculation participates in acceptance.

A coefficient vector's sign is checked by integer interval arithmetic using
these enclosures. Exact zero is accepted only when every coefficient of
P_1,...,P_9 is zero. An interval containing zero for a nonzero vector is an
error, never assumed nonnegative. Flow conservation and cut equality are
symbolic identities and do not accumulate interval errors. The certificate
passes every sign query without an ambiguous interval. This is elementary
rational verification, not proof-kernel checking.

## Scope and full invoice boundary

The theorem closes the exact weak-duality question left by PR5144 at this
one price and functional. It includes all paid rank jobs, all helper credits,
all eight owned center changes and the frozen/native constraints in that
model. It proves a lower bound even after independent-literal relaxation;
no search of the other510 nonzero functionals occurred. It neither asserts
uniqueness of the unchanged minimizer nor a neighborhood in C.

No physical supplier is built. The source's unresolved actual shared-G
synthesis, signed native endpoints, compiler, precision and recursive outer
admission remain unresolved; their costs are not assigned zero. These
additional obligations cannot turn this relaxation's nonnegative modeled
delta into a negative modeled delta, but this statement grants no complete
runtime or multiplication theorem. Certificate memory, graph allocation,
rational arithmetic and file decoding are host verification work, not free
payload operations in a physical multiplication algorithm. Source contracts
and invoices are preserved, not replaced by the host graph's operation count.
