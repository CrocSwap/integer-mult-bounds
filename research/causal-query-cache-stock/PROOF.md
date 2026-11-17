# Minimum persistent cache at the minimum acquisition count

This scoped proof and its compiler were produced by Nick Petalas.

## Contract and statement

Let K be any field. Fix a finite list of row vectors v_1,...,v_m in K^n.
There is an immutable bank x of n arbitrary independent payload fields.
At request i the value v_i x is available, and the requested answer is
Q(v_i x), for one common K-linear query Q and one common physical ABI.
The response is delivered before request i+1. Delivered responses cannot
be read again. Any copy retained by the responder counts as cache.

Ordinary instructions take scalar K-linear combinations. An acquisition
applies Q to an ordinary combination of the original bank and returns one
payload field. Queries never take query-dependent data as their inputs.
For the lower bound, arbitrary prefetch of available ordinary combinations
is permitted. The upper construction only queries the current request.
The word and its coefficients are fixed independently of payload contents.
No external query-dependent advice or consumer feedback is available.

We require formal query correctness: ordinary and queried coefficients
are distinguished. Equivalently analyze values as a x + b Qx with the two
coefficient rows independent. This is justified by a faithful formal
operator model, or by requiring the same scalar protocol to work for all
linear Q and all payloads. It is not justified for a fixed scalar Q.
No second nonordinary operator or non-scalar ordinary address algebra is
admitted here.

Owned cache fields and one response/work field may be initialized and
erased, at positive cost. Original sources are unchanged. Dirty spectators
are untouched. This is the observational owned-erasure contract, not a
reversible dirty-workspace theorem. Ordinary arithmetic, moves, entry
scrubs, output delivery and all clears must be charged by an installation.

Set, at the cut after response i has been delivered,

    V_i = span(v_1,...,v_i),
    W_i = span(v_(i+1),...,v_m),
    r   = dim span(v_1,...,v_m),
    d_i = dim(V_i intersect W_i)
        = dim V_i + dim W_i - r.

The empty spans at i=0,m are zero. Persistent cache counts all owned
query-dependent state across these cuts. A response/work field is empty
at every cut and is counted separately during a request.

**Theorem.** The minimum number of acquisitions is r. Among protocols
using exactly r acquisitions, every cut needs at least d_i persistent
fields. One causal protocol attains all these lower bounds simultaneously.
Consequently the exact minimum persistent capacity is

    b = max_(0 <= i <= m) d_i.

The same protocol can be implemented using b cache fields and one
response/work field, with scalar ADD, nonzero SCALE, SWAP and owned CLEAR.
It uses no additional payload field for a basis conversion. This b+1
upper bound on total temporary fields is not claimed optimal.

## The new lower bound

Each acquired answer contributes one queried coefficient row. Ordinary
instructions can only combine those rows. All delivered answers together
have row span of dimension r, so at least r acquisitions are necessary.

Consider an arbitrary correct protocol using exactly r acquisitions.
Let p_i be the number acquired by cut i. Past answers span V_i, so
p_i >= dim V_i, even if the protocol prefetched future rows or discarded
old answers. Let C_i be the span of queried coefficient rows in its
persistent state at that cut. If k_i fields persist, dim C_i <= k_i.
Ordinary parts in the same fields do not increase this queried dimension.

Only the persistent state and r-p_i subsequent acquisitions can supply
queried coefficients to future answers. Past consumer outputs are
unavailable by contract. Therefore

    dim W_i <= dim C_i + (r-p_i),

and hence

    k_i >= dim W_i-r+p_i
        >= dim W_i-r+dim V_i
         = d_i.

This argument permits arbitrary linear cache encodings, discarded cache
values, prefetch, raw-source retention and scalar computation on raw
sources. None of them supplies an additional queried coefficient row.
It does not cover query feedback or free access to past consumer outputs.

## A single schedule attains every cut bound

Retain answers for a basis of U_i=V_i intersect W_i after cut i.
Initially U_0=0. At request i, write v=v_i.

If v belongs to V_(i-1), it also belongs to W_(i-1), since it is a current
or future request at the preceding cut. Thus v belongs to U_(i-1), and
its answer is reconstructed from the cache with no query. Otherwise query
the actually available v x once. The number of such rank increases is r.

For the transition to U_i, observe

    U_i is a subspace of U_(i-1) + span(v).

Indeed write u=a+c v with u in U_i and a in V_(i-1). Both u and v belong
to W_(i-1), so a belongs to V_(i-1) intersect W_(i-1). Every new basis
answer can therefore be formed from the old cache and the response.
After conversion, deliver the response and clear the response/work field.
Only dim U_i=d_i independent cache answers remain. At the final cut U_m=0,
so the cache is empty. This proves simultaneous attainment and the theorem.

The basis choice and causal reconstruction build on Dugongue's #5803,
volume-scheduling S12-S13. The contribution here is the matching per-cut
lower bound, its global minimum-capacity consequence, and the bounded
instruction-emitting compiler. The dimension identity is classical linear
algebra and is the usual connectivity function of the represented matroid;
no worldwide priority claim for that function is made. Request order is
fixed. Optimizing order is a different problem.

## Why basis conversion needs no second payload bank

Pad the old cache by zero fields to b entries and append the current
response. Express each new cache basis row in the old basis plus v.
These coefficients and a last row preserving the response give a square
(b+1)-by-(b+1) scalar matrix T. The unwanted cache rows are zero.

Two-sided Gaussian elimination constructs invertible L,R with

    L T R = diag(I_s,0).

Execute R^-1 on the existing bank, clear the last b+1-s transformed
coordinates, and execute L^-1. These operations realize T on every bank
input. Each elementary matrix is a scalar ADD, nonzero SCALE or SWAP.
No temporary payload field is used. The response may move during this
conversion but is restored before delivery. The compiler emits those
individual instructions, not a simultaneous-assignment oracle.

For a bank of h=b+1 fields, the reduction uses at most h pivot steps,
h row swaps, h column swaps, h scales, h(h-1) row ADDs and h(h-1) column
ADDs. Its emitted inverse factors and clears have at most 2h^2+2h
instructions. Preparing a dependent response uses at most b ADDs, and
its post-delivery clear uses one. Entry scrubbing uses h clears.
Thus an installation may charge at most

    h + m (2h^2+2h+b+1)

such ordinary instructions, in addition to r acquisitions, current-source
assembly, descriptor construction and access, coefficient arithmetic,
output transport, and their physical routing/precision costs. Scalars
must actually be admitted at the common chart. Elimination over a field
does not prove a dyadic-only implementation or a uniform physical tariff.

## An unbounded strict stock improvement over retaining named answers

For n>=1 request e_1,...,e_n, followed by e_1+...+e_n. The total rank is n.
For each cut 1<=i<=n, U_i is the line spanned by e_1+...+e_i. Hence b=1.
The responder accumulates the queried running sum and uses exactly n
queries. Keeping every individually acquired answer until its final use
would instead retain n fields at the cut before the last response.
That fixed-value policy is a comparator, not a lower bound for general
cache encodings. The new theorem supplies the latter lower bound of one.

## Boundaries that matter

- If previous responses remain readable, the width formula can overcharge
  the responder's private cache. Those responses are additional state.
- If reacquisitions are allowed, b need not be necessary. Requesting one
  nonzero row twice uses one query and one persistent field at the optimum;
  two queries use zero persistent fields.
- If Q is an ordinary scalar, queried and ordinary rows are not independent,
  and the acquisition lower bound can fail entirely.
- Query feedback, noncommuting ordinary operators, differing frames,
  source mutations, input-dependent control and dirty-return-only work
  fields have different contracts.

The proof is all-size within this contract. The executable compiler and
finite checks have the separate bounded domains stated in README.md.
No selected supplier installation, new kappa, full multiplication theorem,
independent human review or formal proof-kernel acceptance is claimed.
