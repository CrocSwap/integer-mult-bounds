# A direct Pascal codec for complete lockstep occurrences

## 1. Contract and distinction from the inherited flow

Fix an ordered finite list of productive roles `t=0,...,W-1`, each with
integer target rank `k(t)>=2`, and an ordered finite list of paid occurrences
`j=0,...,P-1`. Occurrence j has positive rank r(j) and acts on exactly one
productive role or one separately named owned bank. All names are distinct,
and owned banks are disjoint from productive roles. Require

`r_max < k_min <= k_max <= A`,

where A is the actual ambient cap. It need not occur as a target rank.
For a positive integer N>=A, set `G=max{g:A*k_min^g<=N}`.

The native endpoint, arbitrary-input contract, spectator correctness,
whole-job adapters, allowed initialization/erasure and costs are retained
premises. This result only constructs the logical field-address and matching
layer of the finite compiler. It supplies neither those primitives nor a
fixed-tape execution bound.

The inherited `finite_dag_audit.py` materializes each class, gathers matching
target slots in a dictionary indexed by their augmented multiindex, and pairs
incoming jobs to that list in order. Its class-unit order is lexicographic
multiindex, then increasing unit ordinal; role order is the supplied native
role list. We give exactly that bijection as arithmetic on one occurrence
descriptor, and then resolve its physical owner without a stored class or
owner table. The original Pascal and live-role arguments retain their credit.

## 2. The interval bijection

Let the distinct target ranks be `k_0<...<k_(d-1)` and let `W_i` be the
number of roles of rank k_i. For a nonnegative multiindex alpha put

`c(alpha)=product_i k_i^alpha_i`,

`u(alpha)=|alpha|! / product_i alpha_i! * product_i W_i^alpha_i`.

For `|alpha|>0`, the weighted Pascal identity is

`u(alpha)=sum_(i:alpha_i>0) W_i u(alpha-e_i)`.

For each present i define

`b_i=sum_(h<i, alpha_h>0) W_h u(alpha-e_h)`.

The half-open intervals

`[b_i,b_i+W_i u(alpha-e_i))`

partition `[0,u(alpha))`. Therefore every ordinal a in this interval has the
unique representation

`a=b_i+W_i*v+l`,  with `0<=v<u(alpha-e_i)` and `0<=l<W_i`.

The decoded child is its unit at point `alpha-e_i`, ordinal v, and the l-th
native role of rank k_i. Conversely those data recover a by the displayed
formula. All operations are on integers; no rounded population or fractional
array occurs.

**Order correspondence.** At fixed alpha, the child points `alpha-e_i`
appear in increasing i order in the predecessor's lexicographic lattice.
Within one child point its unit ordinal increases first and the matching
roles retain native order. Hence its target-slot list consists precisely of
the blocks above. The parent supply bucket uses increasing ordinal a at
point alpha. Encode/decode consequently reproduce its exact ordered pairing,
not just a rank histogram or an arbitrary equinumerous matching. This holds
even when the native role list is not grouped by target rank.

## 3. Capacity, sources and exact matched ranks

A class has a paid-occurrence path `p=(j_1,...,j_h)` and dilation
`rho(p)=product r(j_l)`. Its unit descriptors are

`(p,alpha,a)`, where `|alpha|=G-h`, `0<=a<u(alpha)`,
and `A rho(p)c(alpha)<=N`.

A child slot `(p,beta,v,t)` with nonempty path has potential parent

`p'=p without its last occurrence`,
`alpha=beta+e_i`, where `k(t)=k_i`,
`a=b_i+W_i*v+l(t)`.

If `A rho(p')c(alpha)<=N`, that parent exists and issues the slot's job at
the last paid occurrence j of p. The requested and delivered ranks agree:

`r(j)rho(p')c(alpha)=k_i rho(p)c(beta)`.

If the potential parent is absent, this is a fresh source. Root-class slots
are fresh sources by definition. This criterion is exact: for a present parent
of point alpha, every Pascal child group is present because

`A rho(p') r(j)c(alpha-e_i)
 = A rho(p')c(alpha) r(j)/k_i <=N`.

The strict separation assumption makes the ratio less than one. Thus the
entire interval bijection is available whenever its parent bucket exists;
otherwise its incoming bucket is empty. There is no partially funded prefix
to hide. Extending this codec unchanged to overlapping paid/target ranks is
not justified and its public constructor rejects that input.

Every fresh source rank s is in `(N/A,N]`. Its upper bound follows from
`k_i<=A` and the child's fit inequality. At a nonroot source, parent absence
gives `A rho(p')c(alpha)>N`, and thus
`s=r(j)rho(p')c(alpha)>r(j)N/A>=N/A`.
At a root source, `A c(alpha)k_i>N` follows from the definition of G:
otherwise the degree-G+1 multiindex `alpha+e_i` would fit.

Every terminal paid exit has `e=r(j)rho(p)c(0)<N`, since its unit fits and
`r(j)<A`. A source complement N-s is either zero or smaller than N. These
facts recover the inherited strict-descent domain with the actual ambient
cap A, including the selected construction's case with no rank-A target.
They are compatibility checks, not new asymptotic leaf estimates.

## 4. Direct physical-owner identifiers

Supply an external namespace identifying this particular flow invocation
and a nonnegative replica number. They remain part of every identifier.
Define

`Source(namespace,replica,p,alpha,a,t)` and
`Owned(namespace,replica,p,alpha,a,b)`

for a source slot t and an owned bank b of one unit. Tags are different even
if their payload values happen to agree. The identifier is a mathematical
field name, not permission to read that field in constant machine time.

To resolve the physical field of a productive slot, compute its potential
parent by Section 3. If absent, return its Source identifier. If present,
inspect the last paid occurrence's actual owner. When that owner is an owned
bank, return its Owned identifier on the parent unit. Otherwise replace the
current slot by that productive parent slot and repeat. Each iteration removes
one paid occurrence, so at most `|p|+1<=G+1` such decisions terminate the lookup.
The algorithm never enumerates the other unit occurrences.

**Owner equivalence.** Induct on |p|. A root slot is exactly the predecessor's
fresh input. A later unmatched slot is exactly its fresh input by the capacity
criterion. A matched slot receives exactly the field on which the issuing
parent's paid occurrence acts, by the ordered bijection. That field is either
the explicitly named parent owned bank or the parent's productive field,
already identified by induction. Thus the returned name equals the literal
compiler's physical field after replacing its sequential numeric source/owned
labels by these canonical occurrence labels. It need not equal the literal
compiler's arbitrary numeric uid.

**Distinct live fields.** Within one class, the parent supplies one job per
unit at the same paid position. The interval bijection uses each such job
exactly once. Assuming the parent class's fields are distinct, these matched
fields are distinct. New source tags are distinct and cannot coincide with
an ancestor's tag; owned tags are separate per unit. Induction therefore gives
injective productive/owned field identities within each class. Reuse along
a chain of suspended ancestors is intended and is not a new productive input.
The inherited lockstep schedule completes a child class before resuming its
parent. This codec specifies the identical owner on that schedule; it does
not replace the separate lifetime proof.

Paid paths record occurrence numbers, not just their ranks or product.
Two paid positions of equal rank can act on different owners and require
different source fields. Replica and invocation namespaces similarly cannot
be discarded. Source, owned and replica labels receive no productive credit
beyond the source count already present in the original flow.

## 5. Representation and separately paid arithmetic

Let S be the bit size of the read-only finite role/paid-owner specification,
using integer role indices, and write `ell(x)=ceil(log2(x+1))`. The live
query descriptor and answer require

`O(S + log N + d ell(G) + G ell(W+P))` bits.

The point has d entries at most G. The path has at most G paid indices.
An occurrence ordinal has at most `G log2 W+1` bits because the total number
of weighted words of length G is `W^G`, and u(alpha) is one of its groups.
Valid capacities/columns and the one-step absent-parent comparison have
`O(log N+log A)` bits. Intermediate weighted multinomial computations can be
done by exact small-factor binomial recurrences; they need no factorial-sized
table. A returned symbolic identifier and its constituent fields are counted
in the bound. No occurrence dictionary, GL cover or generated instruction
list is counted as implicit free storage.

This is **offline arithmetic**, not unit-cost execution on a Turing machine.
For a conservative implementation let

`B=S+ell(N)+(G+1)ell(W+P+A+G+2)`.

One u(alpha) uses O(G+d) exact integer multiply/divide operations, with
O(Sd) additional scans if target weights are recomputed from the fixed input.
Encode tests at most d blocks and the owner query has at most G+1 levels.
Including validation, path products and linear role lookup gives the loose
bound

`O((S+1)(d+1)^2(G+1)^2 B^2)` bit operations

using schoolbook multiplication and division. This upper bound is deliberately
conservative; no practical speedup or constant-time random access is asserted.
The code's Python tuples/dictionaries are verification conveniences, not a
fixed-tape lowering. The all-size claim is the algorithm and the foregoing
integer argument, not extrapolation from measured Python timings.

`iter_units` streams the predecessor's ordered class descriptors with ordinary
lexicographic counters. Its total time must include every emitted item;
the per-query bound does not turn a huge complete output into a short output.
Ranking all fresh Source names into a contiguous physical row interval,
integrating source complements and smaller-rank invocations, and generating
all actual native segments remain subsequent tasks.

## 6. What this contributes to the selected compiler assumption

The selected #7000 proof uses a separated completed unit, actual ambient
`A=153^1920` and finite compiler rank `N=2^H_C`. The codec theorem permits
that domain abstractly whenever the full finite role/paid-owner specification
is supplied. It does not materialize A, N, the product's role list, all source
arrays or its emitted word. Merely supplying the number A or an invoice does
not supply the role/owner specification.

The reduction is precise: the compiler's previously implicit per-bucket
Pascal matching and physical-owner lookup can be replaced by the explicit,
terminating local algorithm above. The remaining emitter must supply the
finite product/completion/splitting role manifest, contiguous source indexing,
owned initialization/erasure, complete coordinate routes and physical tariff.
The selected five assumptions and the accepted kappa remain unchanged.
