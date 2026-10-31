# Independent current native-catalogue admission review

Reviewer: @CubeJerry with substantial OpenAI Codex assistance (worker B).
Reviewed source base: `2485805a6d47f36ea83ddde6327d453ac82d44dc`.
This is a source and exact finite-geometry review for the extension of
CrocSwap/integer-mult-bounds#5708 routing to the native catalogue used by
CrocSwap/integer-mult-bounds#5616. It does not independently discharge any
all-size or ordinary-cost premise. **No new κ.**

## Source equivalence and actual predicate

The current source chain is `g20-conjugation-admission/integration.py` →
`prior/integration.py` → `prior/prior/integration.py` →
`prior/prior/prior/source/local_relations.py` →
`source/vendor/g20/provider/local_ir.py`. The last relative path is resolved
from `prior/prior/prior`; it supplies the actual `Geometry` class. The
`source()` function reads that vendor's `inputs/FRAMES.json`.

Those current frame bytes are **identical**, not merely equivalent after
renumbering, to decompressed `bit-g20-contact-expansion-bound/FRAMES.json.gz`.
Both have SHA256
`0d99fc6b8f45c03dfba5252a03dd9e7fe23be3a7593dfe15368e34da6629a654`;
the current uncompressed Git blob is
`9edf8d95b45a9c9c766a956bfcd3c19cf07bc13c`. The older gzip blob is
`39146e47daba85b6154544caa03003a60edca1d8` both at the canonical base and at
CrocSwap/integer-mult-bounds#5616 head
`bf17817bcaae61379dcadd50ee6bde9a6c7f5018`. `NATIVE-SOURCE-TRACE.json` pins the
nine relevant files. The 29 MB flow certificate was neither retrieved nor
used. No older scalar word or old caller invoice is being transferred.

The **current** `Geometry.nested(s,t,k)` sorts the two endpoints by dimension
and requires all three conditions:

1. `0 < k < 8`;
2. dimension difference exactly `k`;
3. every low-dimensional B row orthogonal over the rationals to every
   high-dimensional A row.

Consequently it admits both directions of a proper nested pair, rejects
rank-eight children, and rejects zero-rank QUERYs. Identical-frame moves are
identity skips in current `construct.emit.route`, before any path lookup.
Since all 645 physical frame spaces are distinct, there are no distinct
frame IDs denoting another uncharged equality case. Native replay also
checks the actual current source frame before each QUERY. `ZERO_Q` requires
the whole normalized row (and, when replayed, its native field) to vanish.
The geometry review grants no additional free retag of a nonzero field.

## Independent finite check

`review_geometry.py` imports neither predecessor nor candidate executable
code. It derives exact rational RREFs of B, derives annihilators from those
RREFs, and tests inclusion against these newly computed annihilators. The
supplied A rows are checked separately for complementary dimension and
orthogonality; they are not the inclusion-test oracle. This checks all
unordered pairs of catalogue frames.

Results: 645 distinct spaces; dimensions 0,1,2,4,6,7,8 have respective
populations 1,120,153,70,180,120,1; 26,312 unordered proper nested pairs,
52,624 directed native edges. Directed edge ranks 1,...,7 have respective
counts 1,812; 2,664; 3,360; 8,542; 19,980; 15,786; 480. All 2,369 retained
current one-edge routes pass the independently derived admission rule.

Executed normally and with `python -O`, producing byte-identical receipts.
Five negative controls reject rank eight, rank zero, incorrect rank,
incorrect declared dimension, and incorrect complement. From a checkout,
pass the current vendor `FRAMES.json`, older package `FRAMES.json.gz`, and
current `PATHS.json` to:

```sh
python review_geometry.py --current CURRENT_FRAMES --older OLDER_FRAMES_GZ --paths CURRENT_PATHS
```

These argument names denote the exact paths above; the script binds the
catalogue hash and checks the retained path count. `RESULT.json` is the
actual execution receipt. This is finite exact rational verification, not
a proof of a uniform native implementation at every recursive height.

## Why arbitrary admitted paths telescope

For a rational orthogonal projector P on the eight antisymmetric address
coordinates, write R(x) = (x_i − x_(15−i)) for i=0,...,7. Let L embed z as
the 16-vector with entries z_i and −z_i in the corresponding paired
positions. Thus RL=2I. The current `Geometry.move(P,x)` is the linear map

    M_P = I − L P R.

Since P²=P, `M_P²=I`. If U⊂V with orthogonal projectors P and Q, then
PQ=QP=P, and direct multiplication gives

    M_Q M_P = M_P M_Q = I − L(Q−P)R = M_(Q−P).

The actual residual uses Q−P irrespective of edge direction, exactly as
`Geometry.residual_mod` does. Thus the QUERY from any admitted frame s to
t implements `M_t M_s` in this rational model. Along an arbitrary finite
path, consecutive equal frame involutions cancel, leaving `M_final
M_initial`. This requires neither dimension monotonicity nor pairwise
commutation among unrelated frame projectors. Repeated vertices and
backtracking do not invalidate the identity. Rational equality transports
to a modular realization only where the inherited denominator and native
admission conditions hold.

The scalar emitter's invariant is a sum of input terms each in the current
frame; two rows can ADD at a shared actual frame because that same factor
is linear. Therefore changing a route while preserving its endpoints and
all actual coframe obligations does not change the symbolic endpoint under
this inherited native interpretation. This argument alone does not price
new matcher/normalizer work, prove whole dirty restoration for an arbitrary
new scalar word, or discharge the five selected-frontier assumptions.

## Scope of approval

The native graph used for a favorable **lower-bound relaxation** may safely
contain all 52,624 directed edges above. A shortest-path rank floor over
this enlarged graph is stronger in coverage than the old directed-table
restriction. A future positive construction using new edges must still
give complete ordinary and recursive costs, native admission and all
endpoint/owned-return checks. This review does not transfer the old
CrocSwap/integer-mult-bounds#5616 scalar contact theorem to the different
685-column current word.

## Independent rank-distance and signed-invoice review

Let `d(a,b)` be minimum **total rank** over paths in the admitted graph.
This is not the minimum of the concave paid tariff. If the edge ranks of
any physical path are positive integers r₁,...,rₘ, then for every real
`0<t<1`,

    Σ rᵢ^t ≥ (Σ rᵢ)^t ≥ d(a,b)^t.

The first inequality is strict for at least two positive edges, by strict
subadditivity of `x^t`; the second uses monotonicity. For an identical
endpoint the identity route has floor zero. Therefore charging the single
optimistic term `d(a,b)^t` for each paid route is a valid relaxation of
every finite admitted path, including backtracking and paths that decrease
and later increase dimension. It need not be attainable by a physical
single QUERY. In particular d=8 does **not** grant a rank-eight child.

`review_distances.py` independently reconstructs the graph and uses integer
bucket relaxation, rather than the author's heap implementation. It then
checks all edge-potential inequalities and a tight descending predecessor
for every non-origin vertex in every distance row. The former prove the
lower bound for arbitrary paths; the latter prove attainability of the
integer rank sum and exactness of the distance. All 416,025 ordered pairs
(including the 645 identities) agree entry by entry with the author's
`METRIC.json.gz`. The author's metric encoding has SHA256
`ef39ef8c66b715f36e81894797ec627f9f75b6db762497be084f42897733f2aa`;
the independently produced `codes`/`matrix` encoding has SHA256
`4e0b9aad61d7d3c9bc249c76dce0729a65216ae7bb2613c060ab2e6cd31f4a3f`.
Distances 0,...,8 have counts 645; 1,812; 32,502; 81,948; 69,148;
50,220; 77,328; 60,420; 42,002. Normal and optimized Python executions
produce identical receipts; inflated and deflated distances, nonzero
diagonal and Boolean-as-integer mutations are rejected.

For a signed invoice, a partition certificate assigns a disjoint nonempty
group of positive rank occurrences to **each** negative rank occurrence q,
requiring that group's integer sum to be at least q. Subadditivity and
monotonicity give `Σ_group r^t ≥ q^t`. Every positive occurrence must be
used exactly once, either in a group or as a leftover. A group of at least
two positive ranks gives strictness, as does a group sum exceeding q or
any leftover. These are sufficient simultaneous sign certificates for the
whole open exponent interval, not numerical samples.

`review_partitions.py` independently checks these occurrence counts,
disjointness, integer ranks, coverage and strictness. Applied to frozen
`NATIVE-ONE-STEP.json.gz`, it validates all 211 distinct exact shapes and
their listed multiplicities: 2,248 strictly positive changes and 22 zero
changes over 2,270 outcomes. Normal and optimized runs agree. Seven
negative controls reject double use, empty groups, insufficient rank,
uncovered negative occurrences, missing leftovers, invented positive
occurrences and Boolean coefficients. The exact frozen receipt is
`NATIVE-PARTITIONS-RESULT.json`; exploratory floating-point fields are not
used by this check.

Reproduction commands for the independent graph and sign obligations:

```sh
python review_distances.py --frames CURRENT_FRAMES
python review_partitions.py --certificate NATIVE-ONE-STEP.json.gz
```

This review independently establishes geometry, distance values, the
all-path concave-power lower bound, and signs of the supplied exact invoice
shapes. The 2,270-case candidate census and its complete per-candidate
invoice reconstruction remain author-checked; this review does not claim
to have independently re-enumerated them. The earlier separate emitter
review checked selected route-sensitive cases from the narrower retained
graph, and must not be represented as a replay of every new native case.

## Final combined two-step certificate

The independent checker was also run on the final joint certificate with
decompressed SHA256
`33c7d4f11e530a7cf64d3ca38f8740913767ec055af8ad6e7669126f0c09d121`.
All 211 global partition proofs validate, and every proof occurs among the
supplied joint rows. Across its 22 listed first-word branches, all 49,865
listed second outcomes have a valid exact sign certificate: 49,392 strictly
positive changes and 473 zero changes. The checker independently verifies
each branch's declared shape multiplicities, strict/zero classifications,
candidate count and zero-contact count, then checks the aggregate counts.
The certificate's metric digest is exactly the independently reconstructed
keyed distance digest above. `NATIVE-JOINT-PARTITIONS-RESULT.json` records
the actual check; its normal isolated-Python and optimized isolated-Python
runs are byte-identical.

```sh
python -I review_distances.py --frames CURRENT_FRAMES
python -I review_partitions.py --certificate NATIVE-CERTIFICATE.json.gz
python -I -O review_partitions.py --certificate NATIVE-CERTIFICATE.json.gz
```

The `review_distances.py` sibling load is explicit and works under `-I`.
The certificate adapter checks all supplied joint rows; it does not
independently generate the 22 first words or the 49,865 second candidates,
nor recompute their scalar invoices. Those completeness and accounting
claims belong to the contribution's primary and complementary census
implementations. The combination of this source/geometry review,
independent metric, analytic all-path bound, and independent sign checking
supports the exact stated two-step family; it supplies no statement about
arbitrary rewrite depth or projectors outside the fixed catalogue.
