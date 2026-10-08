# Next research steps after the bounded investigation

**Authoritative current status:** [current contracts](current-status.md).
The selected conditional witness is `κ=25508460085039/500000000000000000 > 2^-15`.
The [preserved research index](preserved-research.md) records the intervening
compression, topology, and core experiments. The roadmaps below are historical;
their bounds and proposed next steps do not describe the current release.

**Pre-compact-control roadmap:** the [preparation pass](layer-preparation.md) starts from
the published conditional 2^-59 witness and targets a sparse or fused layer
primitive. It generalizes stopping, handles unequal exponents, and audits a
stronger complex interface. The [short-guard reduction](short-guard-audit.md)
now isolates the next target: a costed gathering algorithm, or a direct
strided-window operation. Logarithmic guards suffice once gathered; the fast
movement bound is still missing. The [gather-schedule audit](gather-schedule-audit.md)
closes serial interval schedules and ordinary round reuse as ways to remove
the quadratic loss with the existing estimates. The subsequent
[bounded coded-carry attempt](coded-carry-audit.md) found no sublinear
recurrence. Its decision is to return the main effort to finite networks and
reopen the coded route only for a concrete costed construction outside the
audited class. The first [cancellation audit](cancellation-audit.md) finds two
smaller scalar circuits but rejects them through disjoint nonorthogonal-path
rank bounds under retained data frames. Future cancellation topologies should
pass that screen before frame optimization; removing self terms alone fails.
The [joint rational-frame audit](joint-frame-audit.md) then proves optimality
of internal active-factor frames under fixed invocation boundaries and the
four grouped central gates, including joint copy/injection/side changes.
The next frame experiment must cross invocation boundaries or change central
gate grouping; another internal-only matrix search cannot improve this model.
All text below is the preserved historical roadmap
from the 2^-63 stage; its status statements and target budgets are not current.

The checked result is now **conditional kappa=2^-63**, obtained by
[shared intermediate sums](shared-computation.md) with reversible role
allocation and auxiliary-role sharing. No exponent in the 50s has been established. The historical targets
below describe the investigation leading to this construction.
The priority is a stronger bit/interchange network, with every frame transition
included in its score. The existing complex network has room to accommodate
a substantial improvement of the bit primitive before it becomes limiting.

## Update to the independent agent's suggested route

The proposed O(d^2)-to-O(d) layout improvement is already in the routing patch.
Our dimension exponent epsilon is already the constant 1/21. The remaining
quadratic dependence comes from

    g2 = epsilon c (1-tau),
    tau (1+c/beta) < 1,

which forces c=O(1-tau). The packed movement audit locates this restriction in
moving full K-bit slots. It is not the former g4 layout restriction. Improving
only sigma, the complex-network exponent, cannot remove this bit bottleneck.

The agent's incidence compression and larger-primitive suggestions remain
useful. The local objective should be the actual recurrence saving
-log(s/(Wm))/log(m), with endpoint and edge ranks certified; a wire-count
reduction or a small matrix factorization by itself is insufficient.

With the present parameter recipe, a=1-tau gives G=3a^2/70, provided the
unchanged complex saving a_c satisfies 9a^2<a_c. The next targets are:

| Desired kappa | Approximate required a (strictly larger) | Relative to the new 2.7e-11 bit saving |
| --- | ---: | ---: |
| 2^-70 | 1.406e-10 | 5.21 times |
| 2^-60 | 4.499e-9 | 166.7 times |

These modest local target values are preferable to starting an unconstrained
search for a 2^-16 multiplication theorem. Reaching 2^-16 with the current
quadratic recipe would require a about 0.019, as well as a much stronger
complex primitive. The agent's a around 2^-12 target presupposes a different,
linear dependence that we have not proved.

## 1. Search for rank-two labels with the existing scalar circuit

This is a concrete alternative to redesigning the entire network. Replace each
rational triple line by a nondegenerate k-dimensional subspace U_T in a
nondegenerate rational symmetric bilinear space F of dimension r. Require

    U_S perpendicular to U_T whenever |S intersect T|=1.

The scalar XOR incidence circuit stays fixed. Its tensor labels use these
subspaces in place of lines. For a fixed stage, P has dimension k^(j-1), Q has
dimension k^(3-j), and the central decreasing residual P tensor F tensor Q
has dimension r k^2. All the original orthogonal direct-sum identities persist.
The data source projection has rank k^3 rather than one. Therefore

    m = r^3,
    L = 3v^2 h r k^2,
    total rational edge rank = Wm - N k^3 + 2L.

For even h, the same triple matching permits the side-role sharing: F tensor
U_A tensor U_B is contained in (U_S tensor U_pi(A))^perp tensor U_B.
The joining edge still saves exactly m relative to the two removed endpoint
edges. Hence W=2N+2Nz+3v^2h as in the shared-side construction. Nondegeneracy
is necessary: a collection of isotropic spaces satisfying only the zero
inner-product equations does not supply the projection interfaces.

### A specific, unrealized target

Find **2,024 nondegenerate rational two-planes in dimension 24**, indexed by
the triples of [24], with the required neighboring orthogonality. If such
planes exist, h=r=24 and k=2 give

    eta = 37/551741760,
    a = 7/10^9,
    G = 3a^2/70 = 2.1e-18 > 2^-59.

The exact log comparison and the full downstream parameter substitution pass
with the old complex network unchanged. This is a **design requirement**, not
a result: the planes have not been constructed. The arithmetic is recorded in
`scripts/block_label_targets.py` and `certificates/block-label-target.json`,
whose status explicitly records the missing hypothesis.

Here the bit label dimension would be 24^3 and the complex label dimension
would remain 46^3. A source patch would have to distinguish these fixed
constants and audit the resulting notation and interfaces. The arithmetic
target is not a substitute for that implementation audit.

This converts an open-ended gadget search into a precise rational rank problem.
The subsequent [feasibility audit](block-label-feasibility.md) excludes
intersection-only block kernels, coordinate-local planes, and positive-definite
ambient forms for this target. Its small indefinite numerical searches did
not find a candidate. The unrestricted rational target remains open.

The subsequent bounded attempt proves a stronger
[point-additive obstruction](additive-label-obstruction.md): arbitrary point
weights, offsets, indefinite forms and local frame bases still force rank at
least hk (except h=9) if even one side of the fitting factorization is additive
in the point indicators. It also supplies an
[exact h=8, r=14, k=2 control](small-block-control.md) missed by the numerical
search. That control has negative network deficit; coordinate labels and,
more generally, commuting projections cannot satisfy the positive-deficit
condition at any h. These findings justify stopping blind searches in these
models. A label-based continuation needs a specific non-additive,
noncommuting ansatz. In the absence of one, the next construction priority
is the overlapping-incidence circuit route in Section 2 below.

An equivalent sufficient object is a symmetric rational block Gram matrix,
with invertible 2x2 diagonal blocks, zero blocks at neighboring triples, and
rank at most 24. Quotient its bilinear space by its radical to recover the
nondegenerate ambient space and the required subspaces. A positive semidefinite
constraint is not part of the target; the original construction already uses
an indefinite form.

The closest literature framework is the fractional Haemers bound: it uses
block fitting matrices and their rank per block dimension. Our proposed
network needs additional symmetric, nondegenerate frame structure. The cited
paper supplies that framework, not this representation. See
[Bukh and Cox, Section 2](https://arxiv.org/pdf/1802.00476).

### Cheap rejection tests before numerical search

- A common-point sunflower gives floor((h-1)/2) mutually orthogonal labels,
  requiring r>=k floor((h-1)/2). At h=24,k=2 this requires r>=22, close to
  the proposed 24. This already rejects many overly optimistic k>=3 examples.
- Extending the old lines inside the same F cannot work. For a fixed triple T,
  its neighboring indicators span t_T^perp: their differences span the
  zero-sum directions inside and outside T, with one remaining direction.
  A new vector orthogonal to all old neighbor lines must therefore lie back
  in the old line. Both directions must be redesigned together.
- A block kernel merely proportional to (|S intersect T|-1) is a tensor
  product of the old Gram matrix and an invertible block; it has rank hk.
  It cannot reduce the dimension per label. Symmetry is useful only if the
  ansatz allows something beyond duplicating the old representation.

Start with a small symmetry-breaking ansatz and exact rank/orthogonality
checks. Finite-field solutions may guide discovery, but cannot be accepted
as rational labels without a verified lift. End a bounded attempt with an
explicit failed ansatz or obstruction; do not turn solver timeout into a
mathematical nonexistence claim.

## 2. Overlapping incidence aggregation with compatible stage frames

**Implemented:** rectangles first supplied 2^-67; sharing intermediate sums
now supplies 2^-63. A brief richer partition search saved only 1.8%, whereas
the new graph reduced side scratch by over fourfold. The new transfer uses
q+c roles for q outputs and c binary additions, with separate source-support
and reachable-target spans proving the two frame directions. Further work can
search more economical cancellation-free addition graphs. Sharing across
different common points also needs a fresh nondegeneracy proof for the reverse
spans; scalar common-subexpression elimination alone does not suffice.

The simple shared-tree bound excludes only one hierarchy, not an overlapping
linear circuit. The next worthwhile model should allow several incidence
layers and cancellation, and should optimize frame transitions jointly with
the scalar circuit. Each candidate must provide:

1. the exact GF(2) map on data and arbitrary scratch inputs;
2. a common rational frame for every gate;
3. the all-role endpoint identity and exact total edge-rank sum;
4. a strict downstream kappa certificate.

Use the current rank budget to reject designs early: at h=46 the old absolute
deficit per physical role is only about 2e-5. A reset loss of one dimension
per removed role is far too expensive. Stage sharing succeeds because its
new transitions are nested and incur no such loss.

This route is closer to the existing construction but may require more
combinatorial search than the block-label target. Do not infer a usable
implementation solely from the small Johnson association algebra.

## 3. Joint primitives and sparse packed movement

Searching a circuit for two to five logical butterfly/basis operations at once
could exploit cancellations inaccessible to a one-operation interface. Score
the complete composed operator, its all-role endpoints, and its fixed-tape
implementation. Saving a constant number of wide moves does not alter the
exponent; a successful result must change the rank ratio or the growing
dependence on K. The [packed movement audit](../packed-movement-audit.md)
states a useful sparse-movement target.

This has the greatest architectural upside, but also the highest validation
cost. It follows the two more focused finite-network attempts, rather than
being the starting point for a broad evolutionary search.

## Bounded work policy

The completed screens are in [network-screens.md](network-screens.md). Do not
repeat ground-size tuning, triple thinning, or the single-hierarchy search
unless a hypothesis changes. For a new attempt, begin with an optimistic
score and a small exact example. Spend a larger search budget only after both
survive. Keep infeasible models and conjectural targets separate from the
checked 2^-63 construction.
