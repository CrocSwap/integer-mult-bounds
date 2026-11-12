# Independent review of the contiguous compiler source-row index

Reviewer: separate analytic-recovery research agent, prepared for CubeJerry
with substantial OpenAI assistance. This is independent AI reasoning and
bounded execution, not independent human review or formal-kernel acceptance.
No author source file was edited by this reviewer.

**Final disposition: PASS after deterministic-table repair.** The initial findings below are historical; accepted final hashes and model-specific bounds appear in the repaired-version section.

## Initial reviewed version and disposition

Initial `source_index.py` SHA256:
`589876e684b98bc8441e88079263b64724d64e17f734955362e54d55bfba6e64`.
The exact proof, verifier and executable hashes inspected by each replay
are recorded in INITIAL-REVIEW-RESULT.json and INDEPENDENT-RESULT.json. The initial logical indexing theorem passes
this review. Its advertised universal implementation bit-work bound has
a material hash-map qualification requiring repair before publication.
The root and author were notified and a deterministic-table repair is in
progress. A later addendum must record the repaired hashes and disposition.

## Mathematical checks

The local count depends exactly on depth h, paid-rank product rho, and last
paid rank r. At child multiindex alpha, a productive type k_i is fresh iff
the issuing parent point alpha+e_i at dilation rho/r is absent. The parent's
fit is `A*(rho/r)*c(alpha)*k_i <= N`. The strict separated-rank hypothesis
r<k_min ensures a fitting parent supplies a fully fitting Pascal bucket;
there is no partial bucket hidden in this test. Summing native roles with
the same rank by W_i is appropriate for counts, while row enumeration keeps
their distinct native-list identities.

The last rank cannot be dropped. At A=5, targets 3 and 5, N=45, G=2,
the state (h,rho)=(2,2) has one fresh role when r=1 (the rank-five parent
would need capacity 50), and zero when r=2 (parent requirements 15 and 25).
The dependence on owner labels disappears only in the count; it does not
merge physical owner identities.

The subtree recurrence multiplies each equal-rank child count by its number
of actual paid positions. Its state cap
`1+q*binom(G+q-1,q)` follows by fixing the last rank and counting multisets
of h-1 earlier ranks. Multiplicative coincidences only decrease this cap.
Every chronological class exists because a repeated minimum-target word
fits at every h<=G under r_max<k_min. The total target-profile count
`binom(G+d,d)` includes degree zero. These formulas handle G=0 and q=1.

The declared order is depth-first class preorder followed by lexicographic
multiindex, ordinal and actual native role order. Lexicographic finite
path tuples have exactly this preorder, including empty paths and prefixes.
The rank algorithm skips disjoint half-open child/source intervals; unrank
chooses the unique containing interval. Local zero blocks and zero subtrees
are safely skipped. Equal paid ranks still have separate consecutive child
intervals. Replica offsets b*S_N and Euclidean division give the claimed
contiguous product interval, and `kind == source` excludes all owned banks.

Source-count bits fit the stated bound since there are at most
P^h W^(G-h) units at depth h and at most W fresh roles per unit. Products
and binomial intermediates have O(B) bits with the supplied B. The missing
cost item in the initial version is data-structure access, not the counts
or the size of those integer operands.

## Exact collision family against the original setup tariff

On the tested CPython 3.12 interpreter let

    H = sys.hash_info.modulus = 2305843009213693951.

Use one productive target rank 8H, ambient A=8H, and five paid positions
of ranks H*(1,2,3,5,7), all owned by that productive role. Set
N=A*(8H)^G. This is a fixed separated finite rule with d=1,q=P=5,W=1.

At every positive depth, rho and the last paid rank are multiples of H,
so their integer hashes are zero. Consequently every tuple (rho,last)
in that level has the same hash. The four independent prime exponents
2,3,5,7 show that the exact number of distinct states at depth h is
`5*binom(h+3,4)`. The bounded check confirms 5,25,75,175 distinct states
at h=1,2,3,4 respectively, each level with exactly one hash. The correct
source count is one; the indexing semantics are unaffected.

Python's hash-based deduplication and state dictionaries cannot be priced
as uniformly bounded or logarithmic lookup operations on this family.
Identical-hash open-address insertion has quadratic collision work in the
number of distinct level keys. Summing the level lower bounds gives
Omega(sum h^8)=Omega(G^9) equality/probe work. For this fixed rule the
initial displayed setup expression is O(G^8 log^2 G). Thus its use as a
universal tariff for the supplied hash-map implementation is unsound.
The finite witness establishes the actual collision pattern; the polynomial
exponents follow from the all-size family, not timing extrapolation.

A deterministic repair is to sort candidate level pairs and deduplicate
adjacent equal entries, then use sorted state keys with binary-search values
and list-indexed degree profiles. `log R=O(B)` follows from the class-tree
count, so comparison-based metadata lookup can be charged explicitly.
An actual sequential tape/bit-machine statement additionally needs to pay
metadata movement; a conservative serialized-table full scan is sufficient
to retain polynomial work for fixed alphabets, even if it is much looser.
No constant-time payload access follows from any metadata representation.

## Independent executable evidence

From the workspace root:

```sh
python3 -I -W error -B independent_check.py .
```

Expected initial result:

```text
PASS_SOURCE_INDEX_PEER_FUNCTIONAL_CHECKS cases=16 sources=314 hash_collision_cases=4
```

The oracle enumerates ordered native-role words, actual paid-position paths
and physical role identities before sorting the resulting fresh sources.
It does not use the author's multiplicity, parent, local-count, block or
subtree implementations to build expected intervals. The 16 cases include
four distinct paid ranks, multiplicative coincidences such as 2*3=6,
duplicate paid positions and target ranks, one-target families, empty child
source blocks, G=0..3 and all five replicas. Every one of 314 independent
source rows is ranked and unranked, and all 1,570 replicated rows checked.
Out-of-range rows and owned-bank source credit reject.

These checks and the written argument support the logical theorem at its
stated inherited-flow boundary. The real selected product manifest, full
compiler emission, physical source access, owned allocation, compiler
assumption and multiplication bound remain unproved by this package.


# Repaired-version disposition: pass at the declared scope

The deterministic-table repair resolves the setup-tariff objection in
REVIEW.md. Reviewed SHA256 values:

- source_index.py: `e978025591b06770026b9879f1e5b10827424f410794fb2b1e1f10a720f49176`
- PROOF.md: `1631e28072e1ad39c3833ec83ff7d59e35c4d8fd1ad45ebce6b777aed4125bdb`
- verify.py: `fb89cad83c3ed69bffaf2a95347b21d26dde4da1dc9c52b4304e7d94d836f623`

The author now generates states in sorted lists, deduplicates prior dilations
before multiplying by each next distinct paid rank, and stores both count
tables under one immutable sorted key vector with binary-search values.
Degree profiles are list-indexed. Growing state-table access no longer relies
on hash dispersion. Remaining hash collections are over the fixed input rule;
their worst-case quadratic work fits the specification-size factor.

The dilation deduplication preserves the storage bound. Prior `(rho,last)`
pairs are sorted, so equal rho values are adjacent. At fixed next rank r,
multiplication is injective in positive rho. Different next ranks give
different last-rank fields. Thus the generated candidate count is exactly
the next level's state count, with no q-times duplicated buffer hidden
under the O(R) state envelope.

The revised proof separates two access models. In the indexed metadata model,
a key comparison costs O(B), binary search uses O(log(R+1)) comparisons, and
log(R+1)=O(B) follows from the chronological class-tree bound. Comparison
sorting and lookup fit the displayed arithmetic bound. Travel to a metadata
record is explicitly excluded from that bound.

The separate sequential simulation serializes metadata of length
L=(S+R+dM+1)B and charges O(L^2) per logical operation, including candidate
insertion, metadata scans, copying, shifting, arithmetic and head returns.
O(L) stored representation plus a spare copy and O(B)-bit scalar registers
supports this conservative simulation. This is a described offline
simulation construction, not a claim that Python is that tape machine or
that selected multiplier code was emitted. Both costs remain polynomial
for fixed target and paid-rank alphabets. No free payload access follows.

The independent ordered-word oracle was rerun and again passed 16 cases,
314 source rows and all 1,570 replicated rows. The same four adversarial
families retain their proven hash collisions and correct source count;
the repaired implementation does not use those hashes for state access.
Exact final results and tested hashes are in INDEPENDENT-RESULT.json. The original defect and witness remain documented above and in PROOF.md.

Reproduction from this package directory:

```sh
python3 -I -W error -B independent_check.py .
```

Expected output:

```text
PASS_SOURCE_INDEX_PEER_FUNCTIONAL_CHECKS cases=16 sources=314 hash_collision_cases=4
```

Disposition: no remaining objection to the stated logical bijection,
state-count/storage bounds or revised model-separated costs. The inherited
flow, selected-manifest, actual row-access and full compiler limitations
remain. This is independent AI review and bounded execution, not human
or formal-kernel acceptance.

## Root integration review

The orchestrator read the complete proof, repaired implementation, hash-collision witness and both independent reviews. The mathematical state recurrence, last-rank distinction, complete source interval bijection and conservative serialized-table model passed review. Only packaging and the independent checker's paths were adapted. Reviewed scientific bytes remain frozen. The final self-contained author and independent checks are recorded below through their executable receipts; no complete selected-certificate replay or assumption discharge is claimed.

The root also inspected the primary CPython v3.12.14 sources: [tupleobject.c](https://github.com/python/cpython/blob/v3.12.14/Objects/tupleobject.c), function `tuplehash`, combines only the fixed tuple length and element hashes; [setobject.c](https://github.com/python/cpython/blob/v3.12.14/Objects/setobject.c), functions `set_add_entry` and `set_insert_clean`, use the same deterministic probe sequence for equal hashes. Distinct equal-hash tuples consequently occupy successive positions of that shared probe sequence; insertion of n such keys incurs quadratic probing work. This supports the explicitly CPython-scoped collision witness independently of timing measurements.
