# A complete optimistic invoice for the minimal uncovered-pivot family

All field spaces below are over a field of characteristic different from two.
The moment parameter is `t=1-kappa`, with `0<t<1`. The algebraic companion
construction establishes the root endpoint; the bound here is an independent
necessary accounting condition and does not depend on treating that endpoint
as a complete multiplication theorem.

## 1. Physical contract and the extra idle in the proxy

There are `L=a+b+1` productive sites, numbered `0,...,L-1`, a pivot `p=a`, and
`n=L` independent arbitrary-input fields `A,F_i (i != p)`. Field A is present
at every site; field F_i has mask `[min(i,p),max(i,p)]`. Each field is one
independent whole compiler target. There is one thin rank-one query. Each full
site invokes the same rank-two native main interface as #6833 and contributes
rank eight on fresh axes. Ordinary changes of basis do not create or identify
independent inputs.

A main target therefore has rank `1+8*(number of sites in its mask)`. The
multiset of main targets per port is

```
{8L+1} union {8s+1: 2<=s<=a+1} union {8s+1: 2<=s<=b+1}.
```

At site k, its coordinate mask projector P_k has rank |M_k|. Decomposing its
full stage into a rank-two native projector and independent rank-one idle
projectors requires exactly `d_k=|M_k|-2` idle incidences. Thus

```
d = (0,1,...,a-1, a+b-1, b-1,b-2,...,0).
```

At the pivot, every field is present. A rank-two native main plane leaves
`L-2` idle dimensions. The fieldwise `mask minus y-host` expression in #6868
counts every one of the `L-1` non-A fields as idle there, because the pivot has
no non-A y-host. These cannot all be independent idle projectors annihilating
the pivot's x and y: the intersection of their required kernel/image conditions
has at most `L-2` independent projector directions. Thus the D_root proxy is
not a physical invoice at the uncovered pivot.

This discrepancy is an **overcount of paid idle rank**, not free surplus.
The complete shortest-root mass is fixed. With n independent fields, t_q thin
queries, and L full rank-two stages,

```
main target mass = n + 8 sum_k |M_k|,
root paid mass   = t_q + 8 sum_k (|M_k|-2),
root surplus     = n-t_q+16L = 17L-1,  since L+t_q=n+1.
```

For L=18, both #6833 and the corrected pivot invoice have root surplus 305 per
port. The uncorrected fieldwise invoice has 297. Adding the unchanged 18 native
helper/paid invoices over 104 ports gives complete surplus 760, not a larger
surplus from the removed phantom incidence.

## 2. Which whole idle jobs are bounded

The source frames are ordinary and data-independent, as in #6833. More
generally, the transport argument requires a nondegenerate source frame at
D=1,S=-1. A frame that becomes singular or vanishes there is outside this
contract; specialization alone would not exclude it.

A whole idle job transforms one independent scalar field, has one rank-one
projector at each covered site in the common physical field chart, and covers m distinct fresh
rank-eight stages. It is paid at rank `8m`, hence costs `(8m)^t`. It can cover
nonconsecutive stages; the lower bound deliberately does not require intervals.
At every covered full site, its projector lies inside P_k, annihilates the
native rank-one query on both sides, and belongs to an independent orthogonal
idle decomposition of P_k minus the rank-two native projector. We also allow
its line and dual to be transported between sites by conjugating through the
literal intervening query factors; this stronger possibility is excluded
between the two arms below. The demand d_k
above is exact. Jobs of zero length are irrelevant.

The fixed-projector subcase is the whole-idle contract used to obtain #6833's
invoice, expressed independently of changing ordinary bases in its literal word.
It does not identify multiple independent fields as one paid job of their total
rank. Arbitrary rank packing is a different compiler contract.

A fixed-projector job cannot cover both a strict left site i<p and a strict
right site j>p. Their mask spaces intersect only on span(A). The left query
covector has nonzero A coefficient, so its annihilation condition kills every
nonzero line in this intersection.

The following stronger argument also excludes transport by all intervening
literal queries. Set all stage variables D=1 and specialize S=-1, so
`T_k=I-2x_k y_k^T`. Let U_i be the query prefix strictly before left site i,
V_j the query suffix strictly after right site j, and H the product strictly
between i and j. An admissible root has the scalar endpoint

```
V_j T_j H T_i U_i = -I.
```

Suppose a candidate source-idle vector v lies in M_i, has y_i v=0, and its
transport H v lies in M_j. Then T_i v=v, and applying the endpoint to
U_i^{-1}v gives

```
-U_i^{-1}v = V_j T_j H v.
```

All earlier left masks lie inside M_i, so U_i^{-1} preserves M_i. All later
right masks lie inside M_j, so V_j T_j preserves M_j. Hence U_i^{-1}v belongs
to M_i intersect M_j = span(A), and v=c U_i A.

In this minimal pivot family, `y_i=A*+F_i*`; each preceding left query has
A component 1 in x, and no earlier query introduces F_i. Acting on A, the
A coordinate therefore flips sign at each preceding query, giving
`y_i U_i A=(-1)^i`. Source neutrality forces c=0. There is no nonzero transported
primal line, regardless of the choice of dual. This necessary condition at
D=1,S=-1 rules out an arbitrary-data whole idle job linking the two arms.
A valid independent whole field cannot be replaced by an input restricted to
one spectral eigenspace; that would change the target/compiler contract.

This transport proof was derived by the companion root-construction worker and
independently checked here. The replay separately builds the vectors and tests
the source-neutral/destination-support linear system over Q, with no companion
module import, for every cross-arm site pair at every pivot for L=4,6,18.

## 3. Universal majorization, with no search over jobs

Let m_1>=m_2>=... be the positive lengths of any admissible idle jobs, with zeros
appended as needed. The total is fixed by the site demands:

```
S = sum m_i = a(a+1)/2 + b(b+1)/2 - 1.
```

For any chosen k jobs, split them into k_L jobs touching the left arm, k_R
jobs touching the right arm, and the remaining pivot-only jobs. At a left site
whose demand is j, these jobs contribute at most min(k_L,j); the right arm
similarly contributes min(k_R,j). At the pivot their contribution is at most
min(k,a+b-1). Hence the sum of the k longest job lengths is at most

```
max_{k_L,k_R>=0, k_L+k_R<=k}
 [sum_{j=0}^{a-1} min(k_L,j)
  + sum_{j=0}^{b-1} min(k_R,j) + min(k,a+b-1)].
```

For k<=a+b-2, replacing the last summand by k associates one pivot incidence
with each selected job. The marginal values on the left are `a,a-1,...,2`,
followed by 1s; on the right they are `b,b-1,...,2`, followed by 1s. Taking the
largest k marginal values gives exactly the first k entries of

```
v = sorted({1,...,a} union {1,...,b} with one 1 removed).
```

For k>=a+b-1, use the total mass S. These are precisely all partial sums of v,
so v majorizes m after appending zeros to both lists. The same proof handles
an empty arm; there is still at least one nonempty arm for L>=2. Nothing here
asserts that v can be realized by the actual query geometry.

Because x^t is concave, increasing, and zero at zero, Karamata's inequality
now gives

```
sum_jobs (8 m_job)^t >= sum_{s=1}^a (8s)^t + sum_{s=1}^b (8s)^t - 8^t.
```

Together with the mandatory one thin query, this is a rigorous paid lower
relaxation. It removes one length-one idle from the proxy and optimistically
allows every other proxy merge. The correction was derived from physical
rank accounting and majorization, not assumed to be a legal construction.

## 4. Balance is optimal for the full power moment

Write the resulting optimistic root saving as

```
R_t(a,b) = (8L+1)^t - 1 + 8^t + H_t(a) + H_t(b),
H_t(q) = sum_{s=1}^q [(8s+9)^t - (8s)^t].
```

For every `0<t<1`, the increments `(8s+9)^t-(8s)^t` strictly decrease in s,
because the derivative of x^t strictly decreases. Therefore H_t is strictly
discretely concave. For fixed a+b=L-1, the whole optimistic saving is maximized
when |a-b|<=1. At L=18, the only maximizing shapes are (8,9) and (9,8).
This is a full rank-power moment comparison, not an entropy approximation.
The unchanged native invoice is independent of a,b, so the conclusion applies
to the complete optimistic margin as well.

## 5. Complete source-bound bill at L=18

Per native invocation, the retained source `pricing-6833.py` declares

```
helpers = {1:14,2:8,3:4,4:109,5:17,6:3,7:10,8:40,9:359},
paid    = {1:2234,2:454,3:489,4:110,5:152,6:7,7:9,8:1}.
```

The exact source commit, source Git blob and SHA256 are in SOURCE-PINS.json;
the replay parses the literal dictionaries without importing or executing the
retained source. It multiplies these dictionaries by 18 and adds 104 copies of
both outer histograms. Thus all native helpers, all native requests, all main
targets, the thin query and every required idle incidence are counted.

At the best shape, the outer target histogram is `{17:2,25:2,...,73:2,81:1,145:1}`;
the optimistic paid histogram is `{1:1,8:1,16:2,...,64:2,72:1}`. The complete
optimistic crossing lies strictly in

```
(0.0033334095468, 0.0033334095470).
```

The complete upper margin at kappa=.00337180 is strictly negative. An exact
upper bound on its derivative is negative throughout `0<=kappa<=.0034`, so it
cannot reenter the favorable region before the currently admitted BIT cap.
The other shapes have no larger margin for any exponent in this range.
Consequently this minimal-mask pivot family, under the stated one-field
whole-idle contract and unchanged native source, cannot improve #6833 through the retained mixed-target rank-power moment
criterion. A different compiler or recurrence criterion is outside this claim.

The interval engine uses only rational arithmetic: a positive atanh series for
logarithms, with its geometric remainder, and alternating degree-19/20 Taylor
bounds for exp(-z), where 0<=z<1. The complete signed histogram and all resulting
bounds are recorded in RESULT.json. As a positive source control, the same
engine independently reconstructs #6833's published raw crossing interval.

No ordinary adapters, precision, compiler or outer loss can improve a negative
raw margin; treating all additional ordinary work as free is conservative for
this exclusion. This is neither a new kappa nor a completed multiplication
algorithm. The five framework assumptions remain unchanged.

## 6. Scope and finite checks

The universal statements are the physical rank identity, literal-query-transport
cross-arm obstruction, all-cover majorization, and balanced-shape comparison.
Their proofs above do not rely on finite enumeration. The replay separately
checks the exact top-k identity at all shapes L=2,...,22 and each relevant k;
all 18 source-shape margins at the benchmark; every cross-arm transport
linear system at every pivot for L=4,6,18; all source hashes; and complete
rational crossing/derivative signs.

Negative controls corrupt retained source bytes; omit source neutrality and
admit a false transported carrier; preserve total mass while dropping arm
separation, producing
longer cross-arm jobs and violating the majorization bound; add back the phantom
pivot idle and obtain the wrong root surplus; and omit the native bill and
obtain a false favorable margin. These controls explain why each accounting
premise matters.

Enlarged masks, noncoordinate target representations, doubleton hosts, different
native active ranks, changed native profiles, and different compiler contracts
are not excluded. A changed query word requires its own transport argument; the literal-query
proof does not transfer to an arbitrary new representation.
