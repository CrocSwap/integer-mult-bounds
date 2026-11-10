# Frozen-serial-schedule temporal pairing obstruction

## Fixed source and permitted model

Source: PR #6824 head `2a7ca44fbda3abaa4df355b183ed7d7478eef7c1`.
Canonical reconstructed payload SHA256:
`d3ccfce7bdbca3b79771844e6c9fee48f1a8066444a19218995648df96982821`.
This matches that head's `EXPECTED.json`; `SOURCES.json` pins reconstruction
provenance separately. Cold verification imports no predecessor executable.

The decoded scalar endpoint is
`T = I + Σ e_(r+112) e_rᵀ` over the actual 104 live ports, with all owned
outputs zero and no dirty-input dependence. The checker verifies all 801
formal axes. A helper is a public coordinate outside the actual live-port
and offset-port sets, including helper holes below label 224. Partition
helpers by identical entrance and exit frame IDs `(U,V)`. Each group G is an
identity block of T.

Choose one group G and any frame F with `U < F < V` as binary subspaces.
Keep every old scalar instruction and the serial event order. A source MOVE
A→B can be replaced by A→F→B if F is strictly between its actual endpoints,
ascending for public or descending for owned. Grant every such subdivision
without a price limit. Its midpoint permits collection, injection and use of
the moving helper as a pivot. Original MOVE times otherwise remain fixed;
no role is retimed across another source event. No additional old-role
relocation, including a free zero-header retag, is allowed. At the common cut require at
least two distinct old G labels at F, including at most the one current
subdivided MOVE's role.

Allow arbitrary rational collection coefficients on any F contact no later
than the cut, and injection coefficients on any F contact no earlier than
it. Buffers stay at F. Grant all boundary bases and unlimited storage. Each
complete collection row and injection column must be supported in G. This
includes zero dirty-input dependence and zero correction on owned outputs.
The broader rational alphabet and free resources are necessary relaxations,
not claims of physical admission.

**Residency lemma.** A common frame occupied by at least two old pivots in
this model is a stored source frame.

**Proof.** At an original event boundary every old public role has its stored
source chart. Inside an old MOVE, only that MOVE's role can occupy a newly
inserted frame; all other old roles retain their stored source charts. Two
distinct old pivots at a common F therefore include a stationary old role,
which forces F to be its stored chart. Inserting further serial subdivisions
of the same MOVE does not change the count of moving old roles. A different
name or basis for the same physical subspace is not a new subspace; an actual
extra chart relocation or retag lies outside the model. Owned or fresh
buffer labels cannot replace the required old G pivots. ∎

Consequently the stored-frame census below is exhaustive for arbitrary
intermediate-frame subdivisions under this serial schedule. New frames need
a changed pivot meeting to evade the obstruction. This reduction does not
apply to retimed/overlapping MOVEs or additional old-role transports.

## Complete temporal histories

Let `p_(r,t)` be the complete prefix row of role r and `s_(r,t)` its complete
suffix column into all old outputs. Both have 801 coordinates. The prefix
starts with identity on all public and dirty-owned axes. ADD updates its
destination, SCALE scales it, COPY replaces its owned destination, and
INIT/CLEAR zero it. MOVE preserves decoded coefficients. The actual frame,
ownership, COPY-zero and terminal contracts are checked.

The suffix starts with identity on all outputs including owned outputs.
Reverse ADD updates its source column by its destination column. Reverse
COPY does this then zeroes the old destination column. SCALE scales its
column, INIT/CLEAR zero it and MOVE preserves it. These are transposes of
the actual primitives; no inverse of a singular prefix is used.

At each physical frame interval record a prefix row at its earliest
availability and a suffix column at its latest availability. Record both
at every granted MOVE midpoint too. Zero vectors need not be retained.
For a cut τ define

`Cτ = span_Q {p_(r,t): F contact, t ≤ τ} ∩ Q^G`,

`Dτ = span_Q {s_(r,t): F contact, t ≥ τ} ∩ Q^G`.

Every admissible S09 collection row belongs to Cτ and every injection column
belongs to Dτ. These spaces permit arbitrary combinations of all contacts;
they are not a test of only selected elimination-basis pairs.

The records cover every observation because a prefix row stays constant
between destination changes, and a suffix column stays constant between
reverse changes. Thus an equal prefix observation exists no later and an
equal suffix observation exists no earlier. Frame changes produce records
even when coefficients do not change.

## Exhaustive finite cuts

Time `2i` is the boundary before event i; `2i+1` is the midpoint of MOVE i.
Each helper residence at F is a closed interval from the boundary after its
arrival to the boundary before departure. A midpoint pivot contributes a
singleton interval. Repeated visits stay separate and simultaneous labels
are deduplicated.

For each group/frame take all residence endpoints and all prefix/suffix
contact times. Test these critical times whenever at least two eligible
pivots are present. Between consecutive critical times there is no contact
or residence endpoint. Its prefix space is the same as at the left endpoint;
its suffix space and pivot set are contained in those at that endpoint.
Therefore a rank-two pairing inside the gap would also exist at a tested
left endpoint with at least two pivots. Endpoint coincidences are granted
simultaneous access, only enlarging the model. Boundary times are included
by the contacts and residence intervals. The census consequently covers
every eligible cut in the stated model.

## Exact intersection and rank argument

Gaussian elimination orders coordinates outside G before those inside G.
The non-pure basis rows have distinct leading outside coordinates. No
nonzero combination of them can be supported in G: inspect its earliest
nonzero outside pivot. The pure basis rows therefore span exactly the
intersection with Q^G. All arithmetic is rational, without tolerances or a
modular upper bound.

Let `c₁,…,c_a` and `d₁,…,d_b` be the two pure bases. Set `M_ij=c_i d_j`.
For every r-channel proposal, `C=X(c_i)` and `D=(d_j)Y`, hence
`C D = X M Y` and `rank(C D) ≤ rank(M)`.

The Gram test uses exact cross-minors, separately from the intersection
elimination. The zero matrix has rank zero. Otherwise choose `M_ab != 0`.
Rank is at most one exactly when every entry satisfies
`M_ij M_ab = M_ib M_aj`; these identities give an outer-product factorization.
A failed identity gives a nonzero two-by-two minor.

All 77 boundary groups are enumerated. Groups with fewer than two helpers
cannot supply two pivots; target-grade-one groups have no strictly
intermediate dimension. The remaining 30 groups give 4,296 tested cuts:
4,292 zero Grams and four rank-one Grams. `RESULT.json` retains every cut.
All four nonzero cases belong to group `(3,127)`.

**Theorem.** The pinned source admits no rank-r S09 hub, r≥2, in the
frozen-serial-schedule model above, including arbitrary nested intermediate
frames.

**Proof.** S09 requires `C D = I_r`, of rank r. The complete temporal spaces
place its pairing inside a tested Gram of rank at most one. Contradiction.
Unit-pivot normalization, dyadic legality and physical charges impose only
further requirements. ∎

Rank-one Grams are only necessary possibilities. They still require a legal
pivot, boundary word, independent targets, owned restoration and full bill.

## Accounting boundary and limits

For two old helper grades w split at relative dimension a, the prospective
target change is `ΔT=2(H_a+H_(w-a)−H_w)`, where `H_j=j^t`. Both old targets
must be debited. A query split u+v→u,v costs `H_u+H_v−H_(u+v)`, counted once
if really shared. Both difference buffers retain fresh-minus-retired inputs
and need charged CLEARs after their last injections. They earn no target
credit. Boundary bases, additions, swaps, INIT/CLEAR, matching routes,
completion fields and peak owned stock remain due for an actual program.

The theorem grants these costs zero before rejecting rank two. It yields no
new paid/target histogram or κ claim. No omitted cost funds an improvement.
Retiming, changed source contacts or boundaries, extra old-role relocations,
transported/substituted buffer pivots and other mechanisms change the spaces
and are outside this proof. New frames alone do not evade the residency lemma.
The separate retiming screen is a search failure only.

The elementary intersection/rank argument is standard. PR #5786/#5800
supply the temporal and dirty-owned contract; PR #5803 supplies S09. Earlier
common-cut censuses are credited in README. Prepared for @CubeJerry with
substantial OpenAI Codex assistance. Apache-2.0.
