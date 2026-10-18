# A rectangular batch without a dedicated connector

This is an exact recursive-interface research construction, not an admitted
integer-multiplication supplier. We extend Ross Richardson's single-source
output-borrowed fanout, PR982, to independently addressed source columns. The
commutator identity is classical; no algebraic or literature priority is claimed.

## Contract

Let m >= 1, k >= 2, and let x_0,...,x_(m-1), y_0,...,y_(k-1) be distinct,
arbitrary length-L rows. The x rows are immutable. A_i and B_j are additive
linear endomorphisms of the same module; their factors need not commute or be
invertible. The required map is

    y_i <- y_i + A_i v,       v = sum_j B_j x_j.

Every complete child `t += F(s)` preserves s and all its private scratch,
is independent of the incoming t and scratch, and uses immutable coefficient
storage. Its negative call is the literal inverse of its expanded instruction
word. The scratch pool excludes **all** external sources and outputs, apart
from their use as a child's immediate ports; immediate ports are never scratch.
Calls are sequential and return their heads to the prescribed locations. No
observer may use an output's temporary contents during a batch. These are
stronger premises than reversibility alone. Rounded nonlinear leaves do not
satisfy this exact linearity contract automatically.

## Construction

Choose different outputs q and r. Four blocks update every nonpivot output:

1. For each i != q, subtract A_i y_q from y_i.
2. For each j, add B_j x_j to y_q.
3. Undo block 1 in reverse order, with opposite signs.
4. Undo block 2 in reverse order, with opposite signs.

If Q is the incoming pivot, each nonpivot receives
`-A_i Q + A_i(Q+v) = A_i v`, while the pivot returns to Q. The sources never
change. Next complete the pivot by the four blocks

1. Subtract A_q y_r from y_q.
2. For each j, add B_j x_j to y_r.
3. Add A_q y_r to y_q.
4. Undo block 2 in reverse order.

Here y_r already contains its final increment. Calling this value R, the
pivot receives `-A_q R + A_q(R+v)=A_q v`; y_r returns exactly to R.
No A_i is commuted through B_j, and no inverse of A_i or B_j is required.
Only their invertible additive shears are reversed.

Every B_j is called four times and every A_i twice. The cost is **4m+2k
complete queries**, with no dedicated connector row and no copies or clean
row initialization. All temporary query scratch is restored at each return.

## Sharp query bound, including feedback

Work over the free associative algebra on a_0,...,a_(k-1),b_0,...,b_(m-1),
acting on independent input symbols X_j,Y_i. Permit precisely the unit queries

    Y_t += +/- b_j X_j;
    Y_i += +/- a_i Y_t,       t != i.

There are no other rows or operations in this query language. In particular,
combined-source/output queries, direct product queries, scalar copies,
coefficient arithmetic, extra connectors, writes to X_j and specialized
identities of a particular matrix or characteristic are outside the theorem.
A query may read an already modified output: feedback is included.

Fix a source j. Let h_(t,j) be the running coefficient of the degree-one term
b_j X_j in row t. Only B_j queries can change it, by +/-1. An A query increases
operator degree, and no output has a degree-zero X_j term. Every h_(t,j) begins
and ends at zero. The coefficient of a_i b_j X_j changes at an A_i query
reading row t by its sign times h_(t,j). If only one output q ever has nonzero
h_(q,j), then output q cannot acquire its required a_q b_j X_j coefficient:
self-queries are forbidden. Thus at least two rows have nonzero histories for
each j. Each zero-to-zero history requires at least two unit B_j queries.
There are therefore at least **four queries of each B_j**, not merely four
queries summed across sources.

For every i and t != i, the final coefficient of a_i Y_t is the signed count
of A_i queries reading t. Higher-degree paths cannot cancel that coefficient,
and the desired map requires it to vanish. At least one A_i query must occur
to produce the requested source increments, so there must be at least **two
queries of each A_i**. Summing proves 4m+2k. The construction attains every
per-operator bound simultaneously and hence also minimizes

    4 sum_j c_Bj + 2 sum_i c_Ai

for arbitrary positive, sign-symmetric, port-independent complete-query
prices. This is not a lower bound for all circuits or all product-factor
lowerings. Port-dependent frames, addresses or travel can change which schedule
is cheapest. The verifier records an explicit positive port-price example
where the chosen pivot loses to the separate-output schedule.

## Complete census for two sources and two outputs

At m=k=2 equality forces one positive and one negative B_j query into each
output for each j, and one positive and one negative A_i query from the other
output for each i. These are twelve distinct queries, so the complete candidate
domain is 12! = 479,001,600 permutations. No shorter word is possible by the
preceding proof.

The exact census uses a projection, not random search. Delete the four B_1
queries, retaining the A order: the source-X_0 and dirty-input coefficients
are unchanged. Delete B_0 instead to obtain the corresponding X_1 projection.
Linearity and immutable sources ensure there are no products between the two
source symbols. Therefore a twelve-query word is correct **if and only if**
both eight-query projections are single-source solutions with the same A
order. In particular, both projections check all dirty-output terms, including
higher operator degrees.

An independent free-polynomial interpreter enumerates all 8! projections and
finds 224 solutions, reproducing PR982's credited one-source count. Group each
by the order of its four A queries and the counts of B queries in the five gaps.
For a pair of projections with gap counts u and v, the exact number of lifts is

    product_(g=0..4) binomial(u_g+v_g, u_g).

Every full word has one unique pair of projections and gap shuffles, so this
counts every candidate once. Summing gives **76,032** correct twelve-query
words, 9,504 for each of eight A orders. The one-source 224 is predecessor
corroboration; the two-source 76,032 is the added finite classification.
This is an exact census for this fixed alphabet, not an optimum over other
instructions. The universal lower bound is the written degree argument, not
an inference from finite enumeration.

## Recursive lowering and all paid terms

Represent each A_i or B_j by a nonempty list of factors in application order.
For a product R followed by Q, with a private dirty row z, emit

    t -= Q z; z += R s; t += Q z; z -= R s.

Descendants use the remaining private pool and never access excluded external
rows. Induction gives an exact product shear and full scratch restoration.
All factors act on the full length L. For a complete factor price c_f(L,w),
which includes coefficient and source reads, target updates, arithmetic,
cleanup, routing, frame adapters and head return, the paid recurrence is

    C([f]) = c_f(L,w) + dispatch_leaf;
    C(R followed by Q) = 2 C(R) + 2 C(Q) + dispatch_node.

Each sign has the same upper price; no inverse is free. Let B=sum_j C(B_j)
and A=sum_i C(A_i), at a common sufficient width w. The four complete batch
recurrences, before their separately charged top-level dispatch/preparation,
are

| Schedule | Child cost | Additional dirty rows |
| --- | --- | --- |
| Rectangular borrowed batch | 4B + 2A | s |
| Single-source borrowed batches (PR982, once per source) | 4B + 2mA | s |
| Separate output echoes, each loading all m sources | 2kB + 2A | s |
| Dedicated dirty connector batch | 2B + 2A | s+1 |

Here `s=max(S(A_i),S(B_j))`, `S([f])=0`, and
`S(R followed by Q)=1+max(S(R),S(Q))`. Balanced n-factor products have
`S(n)=ceil(log2 n)` and leaf count
`N(1)=1; N(n)=2N(floor(n/2))+2N(ceil(n/2))`.
All sources, outputs, factor coefficients, descriptors, leaf-private scalar
workspace and control storage are additional to s. No row length is divided
by m or k. Frame/physical realization is not supplied by this reference.

The improvement over the two no-connector comparisons is respectively
`2(m-1)A` and `2(k-2)B`; it vanishes at m=1 or k=2. Removing the dedicated
connector **costs** 2B relative to that alternative. An application must
actually need the scratch saving before it is a useful tradeoff.

For OS seed 54, m=5-2=3, k=4, B lengths [2,3,4] and A lengths [1,2,3,4]:
B has 30 leaves, A has 31. The emitted costs are

| Schedule | Queries | Leaves | Extra dirty rows |
| --- | ---: | ---: | ---: |
| Rectangular borrowed | 20 | 182 | 2 |
| Separate sources | 36 | 306 | 2 |
| Separate outputs | 32 | 302 | 2 |
| Dedicated | 14 | 122 | 3 |

The best of these two no-connector baselines uses 302 leaves; the new word
saves 120 (39.7%). The dedicated alternative saves another 60 leaves at the
price of its extra row. No measured speedup is asserted.

## Explicit exact-integer backend

Each factor is a supplied read-only L-by-L integer matrix. A leaf performs a
dot product for every target coordinate in a zeroed scalar accumulator, using
a constant number of scalar coefficient/source/product ports, then adds or
subtracts the result into the target. For N leaves the invoice counts

- N L^2 coefficient reads and N L^2 source reads;
- N L target reads and N L target writes;
- N L^2 multiplications and N L(L+1) additions;
- L negations per negative leaf and N L accumulator zero assignments;
- N instruction records and every head return.

The zero assignments are paid; this is an ordinary exact-integer reference,
not a claim of reversible scalar hardware with free erasure. Initializing and
clearing the constant scalar work ports is an additional O(w) bit cost per
port at entry/exit. Data and coefficient rows are never cleared or initialized.

The declared data-tape layout stores data rows, then matrices in sorted name
order. Visit coefficient then source for each scalar product, then target for
its update, returning to slot zero after every leaf. The primary invoice sums
literal absolute head distances; the independent oracle derives a closed
formula. At L=3 both yield:

| Schedule | Coefficient/source reads, each | Additions | Word-slot head travel | Data words |
| --- | ---: | ---: | ---: | ---: |
| Borrowed | 1638 | 2184 | 388364 | 27 |
| Separate sources | 2754 | 3672 | 527460 | 27 |
| Separate outputs | 2718 | 3624 | 707540 | 27 |
| Dedicated | 1098 | 1464 | 229160 | 30 |

All use the same 171 coefficient words. For bit work, multiply travel by w,
charge O(w) per access/zero/negation, and multiply the arithmetic counts by
M(w) and A(w) on a constant number of separately charged scalar work tapes.
Add paid instruction fetch/dispatch, address computations and loop control;
the trace is a data-tape invoice, not a strict single-head, single-tape
compiler or a Python-runtime benchmark. For P distinct
factors and R rows, emitted program storage is O(N log(P+R)) bits, with
O(N log(P+R)) preparation work, in addition to input factor lists and recursion
metadata. Explicitly charge descriptor/shape/distinctness validation and any
coefficient preparation as `Prep(P,L,w)`; no phase or factorization oracle is
assumed free. Every change of external layout or frame needs its own price.

If initial data magnitudes are <=D and factor entries <=H, each primitive
shear has joint infinity norm <=1+LH. Every row value, scalar product and
partial dot sum at step t is bounded by `max(1,D)(1+LH)^t`. Hence

    w = 2 + ceil(log2(max(1,D))) + N ceil(log2(1+LH))

suffices for signed exact integers; use the largest N among comparators for a
common precision invoice. In inverse replay starting from the forward result,
the literal inverse visits the forward states in reverse order. Each inverse
leaf has the same source vector as its paired forward leaf, because a shear
does not change its source. Its scalar products and partial sums are therefore
identical, so the same N-factor allowance covers both directions. Storage
includes a constant number of w-bit scalar
ports plus address/control bits. This does not prove an efficient asymptotic
precision bound for the selected supplier.

## Boundary and unresolved obligations

A deterministic rounded shear remains invertible by literal reversal but can
fail dirt independence. With x=1, B=A_1=identity, A_0(t)=floor(t/2), and y_0=0,
changing initial y_1 from 0 to 1 changes the final y_0 from 0 to 1. This is an
explicit failed linearity premise, not a floating-point near miss. No rounded
recursion or coefficient preparation theorem is inferred.

The construction is useful only where its multiple-source/output contract
and scratch restriction are actually available. No placement into the U8/T37
controller is supplied, no paid term of that selected invoice is removed,
and no new moment or kappa is claimed. All-size compilation, common labels,
physical frames/owners, whole-call hosting, tape/precision/exact recovery and
outer analytic assumptions remain. Finite exact replay and this written proof
are not a proof-assistant verification of integer multiplication.
