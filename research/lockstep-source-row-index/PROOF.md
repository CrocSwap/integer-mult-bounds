# Contiguous source indices from aggregated chronological subtrees

## 1. Domain and declared order

Use the separated finite rule and the exact occurrence/owner codec at
CubeJerry commit `91246e5131152ccb1f64a969c36706360861f821`,
`research/pascal-occurrence-codec/`. Its fixed role list has W productive
roles of ranks `k_i>=2`, with d distinct target ranks and multiplicities W_i.
There are P ordered paid occurrences with positive ranks strictly below
`k_min`; their q distinct ranks have multiplicities P_r. The actual ambient
cap A satisfies `A>=k_max`. For integer N>=A set

`G=max{g:A*k_min^g<=N}`.

A unit `(p,alpha,v)` has `|p|+|alpha|=G`, column
`rho(p)c(alpha)`, fit `A rho(p)c(alpha)<=N`, and
`0<=v<u(alpha)`, with c and u as in the predecessor. Each paid position,
productive role and owned bank retains its separate identity.

Number fresh sources in this fixed order:

1. Visit classes in depth-first preorder, with children in actual paid-position
   order. The class's own fresh inputs precede its child classes.
2. Within one class, visit unit multiindices lexicographically, unit ordinals
   increasingly, then roles in the native role-list order; keep only fresh slots.

This is a declared canonical row numbering, compatible with the direct
per-unit source order in the #4691 executor. It need not equal the incidental
numeric source IDs allocated by `finite_dag_audit.py`'s dictionary of augmented
points. No job, native instruction or paid occurrence is reordered. The new
numbers specify which independent input array occupies each existing source
slot; changing an already stored external layout still requires the caller's
charged row permutation.

## 2. Exact source counts at one class

For a class at depth h let rho be its paid-rank product. If h>0, let r be
the rank of its last paid occurrence. At the root use state `(0,1,0)`.
The state for counting is therefore `(h,rho,r)`; it is not a physical owner ID.

For any fitting multiindex alpha of degree G-h define the number of fresh
roles per unit by

`F(h,rho,r;alpha)
 = sum_i W_i * 1[h=0 or A*(rho/r)*c(alpha)*k_i>N]`.

At h=0 the predicate is defined to be true without dividing by zero. The
local source count is

`C(h,rho,r)
 = sum_(|alpha|=G-h, A*rho*c(alpha)<=N) u(alpha)*F(h,rho,r;alpha)`.

This is the predecessor's exact absence-of-parent test. For a present
parent the complete Pascal interval is available, because `r<k_min`.
Consequently there is no partially supplied bucket and the formula counts
all and only fresh inputs. The count depends on h, rho and r, rather than
the whole paid path or its owner values.

The last rank is necessary. For targets `{3:1,5:1}`, ambient A=5,
paid ranks 1 and 2, and N=45, G=2. At depth 2 and rho=2,

`C(2,2,1)=1`, while `C(2,2,2)=0`.

The two paths have identical dilation but different parent capacities. A
cache keyed only by depth and dilation would be incorrect.

As a separate count identity, let U(h,rho) be the number of units in that
class. Then

`C(0,1,0)=W*U(0,1)`,
`C(h,rho,r)=W*U(h,rho)-U(h-1,rho/r)` for h>0.

Every parent unit supplies exactly one target slot at that paid position;
the inherited bijection supplies all of them. This identity provides an
alternative way to verify the local source counts. It does not merge the
physical fields of distinct classes.

## 3. Subtree aggregation and polynomial state count

Let T(h,rho,r) be the total fresh sources in the complete subtree beginning
at that class. At h=G, put T=C. For h<G use

`T(h,rho,r)=C(h,rho,r)+sum_s P_s*T(h+1,rho*s,s)`.

All states refer to positive finite integers. Induction on G-h proves the
recurrence: first count this class, then each actual paid occurrence's child
subtree. Equal paid ranks have identical *counts*, so their multiplicity
P_s may multiply one cached value. They still occupy separate consecutive
intervals in actual paid-position order. In particular, they must not be
collapsed into one physical source interval.

There is a fitting unit at every class path of depth h<=G: its minimum
possible column is at most `r_max^h*k_min^(G-h)<=k_min^G<=N/A`.
The recurrence therefore describes the same full depth-G class tree as the
separated predecessor. Empty source blocks and subtrees are permitted;
they have count zero and are skipped in indexing.

At a positive depth h, fix the last rank s. The preceding h-1 paid ranks
are described, for their product, by a multiplicity vector on q values.
There are `binom(h+q-2,q-1)` such vectors. Multiplicative coincidences can
only reduce the number of distinct products. Summing over last ranks and
depths bounds the total number of cached states by

`R = 1 + q*binom(G+q-1,q)`.

Use `binom(q-1,q)=0` when G=0; the bound is then one. At q=1 the formula
is G+1. No factorization of paid ranks or enumeration of paid paths is needed.
Keep each level sorted by `(rho,r)`. First remove adjacent repeated rho
values, then form `(rho*s,s)` for each remaining rho and distinct paid rank s.
These candidates are already distinct: equality forces the same s and then
the same rho. Comparison sorting and adjacent deduplication produce the next
sorted level. Thus the temporary candidate list has exactly the next level's
state count; it is not q times a list containing duplicate dilations.

All target multiindices needed at degrees 0 through G number exactly

`M = sum_(g=0..G) binom(g+d-1,d-1) = binom(G+d,d)`.

They may be enumerated once with c(alpha) and u(alpha), then scanned by the
capacity predicate. This enumerates neither the u(alpha) individual unit
occurrences nor the P^G paid paths. R and M are polynomial in G for fixed
finite rank alphabets q,d. No polynomial bound with a degree independent
of varying q,d is asserted.

## 4. Rank and unrank are inverse

Set `S_N=T(0,1,0)>0`. To rank a fresh source with path p, start at the root
with offset zero. For every selected paid position j on its path, add the
current class's C and the T values of all preceding paid positions; then
descend to j. This gives the number of sources before the destination class.

Within that class, for every fitting multiindex beta preceding alpha add
`u(beta)*F(beta)`. For alpha add

`v*F(alpha) + #{fresh native roles preceding the given role}`.

Reject a role whose parent is present. This yields an integer in `[0,S_N)`.

To unrank `x in [0,S_N)`, compare x to the current class's local C. If x<C,
scan its nonzero multiindex blocks in order. In the unique block containing
x, division by F gives its unit ordinal v and remainder indexing the fresh
native roles. If x>=C, subtract C and skip complete child intervals in actual
paid-position order until reaching the one containing x; descend and repeat.
At each descent h increases, so there are at most G descents. Zero-size
intervals are simply skipped. The half-open intervals partition the current
state's total, so a valid x cannot fall outside them.

Induction over this finite interval decomposition proves both inverse
identities. Consequently fresh source occurrences are in bijection with
every integer in `[0,S_N)`, not merely with a sparse set of large labels.
The distinction between source roles at the same target rank and between
equal-rank paid occurrences is preserved.

For a positive integer replica count a, the full finite compiler has the
source width `B_N=a*S_N`. Encode a source in replica b as

`row = b*S_N + rank(source)`,  for `0<=b<a`.

Euclidean division by S_N recovers b and the local source index. The namespace
identifies the particular invocation's row arena. Owned-bank identifiers are
rejected: they are not independent productive sources and receive no row credit
from this bijection. A productive role first resolved by the predecessor codec
can now be assigned its concrete row integer when its ultimate owner is a source.
Owned ultimate owners retain their separately reserved bank identity.

## 5. Bit sizes, setup, and query work

Counting a subtree does not require storing a source for every occurrence.
At depth h there are at most `P^h*W^(G-h)` units. Therefore

`S_N <= W*sum_(h=0..G) P^h W^(G-h)
     <= (G+1)*W*max(W,P)^G`.

Every source or subtree count thus has
`O(log(G+1)+log W+G log(max(W,P)))` bits. Point products have at most
`O(G log A)` bits even when a point is later discarded by the capacity test.
The number of classes can be exponential while their exact counts have only
linear-in-G bit length.

Let S be the bit size of the finite input specification, including its role
and paid-position lists, namespace and replica count a. Put

`B=S+ell(N)+(G+1)*ell(A+W+P+G+2)+1`,

where `ell(x)=ceil(log2(x+1))`. All relevant arithmetic fits O(B) bits.
Use the following logical operation envelopes:

`K_setup=(S+1)^2 * [M(G+d+1)+R(M(d+1)+q+1)]`,

`K_query=(S+1)^2 * [M(d+1)+G*P+G+d+1]`.

There are two distinct access models below. Neither grants free physical
payload access.

### Deterministic indexed metadata algorithm

The supplied implementation uses a list of point profiles, sorted level
lists, and two value arrays sharing one immutable sorted vector of all
state keys. `SortedStateTable` locates a key by binary search and verifies
exact equality. No expanding state set or dictionary occurs. The only
remaining hash collections are over the fixed input specification (the
paid-rank Counter and predecessor rule validation/type lists). Even total
collision there costs at most a quadratic factor in S, already included.

For the arithmetic/comparison count, an indexed metadata record can be
retrieved/copied into arithmetic workspace with its bit length charged;
physical travel to that record is a separate model below. A state key
comparison costs O(B), and a lookup makes O(log(R+1)) comparisons. Since
`R<=sum_(h=0..G) P^h`, `log(R+1)=O(B)`. Hence each lookup costs O(B^2)
in this indexed model, including index arithmetic and record bits.
Sorting all state levels costs O(R log(R+1)) key comparisons; forming
their candidates and all child count queries fits O(qR) operations.
These costs are included in `K_setup*B^2`.

Exact small-factor binomial arithmetic and schoolbook multiplication/
division therefore give these intentionally loose bounds:

* Setup indexed arithmetic/comparison work: `O(K_setup*B^2)`.
* Stored input, state counts and target profiles: `O((S+R+dM)*B)` bits.
* A valid rank or unrank query after setup: `O(K_query*B^2)` indexed
  arithmetic/comparison work.

The bounds include capacity tests, repeated role lookup, all count
comparisons and lookups, multiplication/division, interval subtraction and
replica encoding. A malformed query's reading/rejection cost also depends
on its supplied length; no bounded-length claim is made for arbitrary
oversized invalid input. These are deterministic bounds, with no average
hash dispersion premise and no unit-cost big-integer arithmetic premise.
They are not by themselves fixed-tape time bounds.

### Conservative serialized-table simulation

A separate implementation removes indexed metadata access. Set

`L=(S+R+dM+1)*B`.

Serialize the input, profiles, state keys and counts on a fixed number of
binary work tapes using delimiters, with total length O(L). Keep only
O(B)-bit scalar arithmetic registers and one current d-component point;
enumerate the lexicographic profiles with counters rather than retaining a
recursive stack of tuple copies. Their storage is included in O(L).

Generate each state candidate and insert it into a sorted serialized level
by one scan and copy to a spare tape, discarding equality matches. There
are at most qR candidates; the unique stored keys remain bounded by R.
For each logical count lookup or update, scan the serialized key table,
compare with the current key, and copy/update its value. This linear scan
replaces the implementation's binary search; it does not simulate a random
access instruction for free. An O(L)-bit scan with binary position/extent
counters, key comparisons, copying and head return takes at most O(LB)
local operations. Shifting an encoded record, retiring the spare copy,
and restoring cursors fit the same conservative O(L^2) allowance.
Schoolbook O(B^2) arithmetic also fits because B<=L.

Charge O(L^2) to each logical operation counted in K_setup or K_query,
including each candidate insertion. This gives the standalone offline
metadata bounds

* Setup: `O(K_setup*L^2)` fixed-tape time and O(L) workspace.
* A valid query after setup: `O(K_query*L^2)` fixed-tape time and O(L)
  workspace, including retained metadata.

An optional final erasure of this bounded private workspace costs O(L)
and fits these bounds. This is a conservative simulation construction,
not a claim that the Python interpreter is that tape machine or a binary
lowering of the selected multiplier. Both models remain polynomial in G
and log N for a fixed native rule.

### Collision audit and correction

An independent peer review rejected the earlier unqualified hash-table
work claim. Let H be Python's positive integer hash modulus; the
[Python 3.12 numeric-hash specification](https://docs.python.org/3.12/library/stdtypes.html#hashing-of-numeric-types)
gives hash(x)=x mod H for nonnegative integers. Fix one role
of rank 8H, ambient A=8H, and five paid ranks H,2H,3H,5H,7H. Take
`N=A*(8H)^G`. At positive depth h there are exactly
`5*binom(h+3,4)` distinct states, but hash(rho)=hash(last)=0 for every one;
all same-depth CPython tuple hashes therefore coincide. Building the old hash
sets incurs quadratic probing work per level, totaling Omega(G^9), while
the former displayed fixed-rule estimate was only O(G^8 log^2 G).
The indexing bijection was unaffected; its data structure did not satisfy
that claimed worst-case tariff. Sorted comparison tables remove this
premise. The verifier includes the same fixed-rule collision family at
G=8, checks all 3,961 state counts and the one source row, and rejects
absent, unordered, duplicate or uninitialized table entries. These checks
are structural controls, not timing evidence for the universal bound.

The emitted row identifier needs O(log a + log S_N) bits. Issuing its actual
array access still requires the caller's movement, restoration and routing
bill. This theorem does not make a lookup, gather, COPY, erase or whole-row
permutation free.

## 6. Relation to the unfinished selected compiler

The predecessor codec left contiguous fresh-source rank/unrank open. This
theorem closes that logical indexing obligation and supplies exact integer
row names compatible with replication `B_N=a*S_N`. Together the two codecs
specify a productive occurrence's ultimate source row without materializing
the class tree or source array list.

The selected finite product's actual role/paid-owner manifest is still a
required input. Neither its 1920-fold expansion nor its winning N is emitted.
Integer batching factors, source complements, nested smaller-rank programs,
owned-bank allocation and the native/tape endpoints remain separate contracts.
The selected five assumptions and kappa are unchanged. No complete multiplier,
physical source access tariff or unconditional theorem follows.
