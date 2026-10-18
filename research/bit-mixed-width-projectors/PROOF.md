# Prefix packing preserves the whole local block

This is a rational address-projector statement. It assumes the source level
spaces and the interpretation of an idle child by `D(P)` used in PR1307.
It does not construct or identify a physical width-seven helper.

Let `q` be a retained eight-coordinate port, with `q^T q = 4`. Write
`K_q = I - q q^T/4`. It is the orthogonal projector onto `q-perp`, of rank
seven. Use chart axis 0 for `q/2`, axes 1 through 7 for any orthonormal
completion in `q-perp`, and axes 8 through 63 for the fixed exterior basis.
An orthonormal completion exists over Q here: for `u=q/2`, the Householder
matrix `I - 2vv^T/(v^Tv)`, `v=e_0-u`, sends `e_0` to `u`; use the identity
when `v=0`. This completion is a proof device, not a charged implementation.

**Local basis criterion.** A chart-coordinate subspace avoiding axis 0 has a
projector independent of the choice of completion if and only if its chosen
local axes are either none or all of 1 through 7.

Sufficiency follows because the local projector is respectively zero or
`K_q`. For necessity, take an included local basis vector and an excluded
one, and interchange them in an orthonormal completion. The selected
projector changes by the difference of their two distinct rank-one
projectors. The fixed exterior part cannot cancel that local change.
This criterion concerns individual factors; a sum of complementary factors
can be invariant even when each factor depends on the completion.

The source levels are `L_-1=span(q)` and
`L_a=Q^8 + E_1 + ... + E_a` for `0<=a<=8`, where each `E_j` is a fixed
exterior seven-space. Thus the idle `a -> b` has ordered pending axes

```
[1, 8+7b)          if a = -1,
[8+7a, 8+7b)      if a >= 0.
```

**Prefix lemma.** Partition a prefix of this ordered interval into contiguous
slots, starting at offset zero, and retain the suffix as the idle remainder.
If there is a first slot at an entrance child (`a=-1`), require its width
to be at least seven. Then every slot and the remainder satisfies the local
basis criterion. The later slot widths need only be positive.

For `a>=0` the entire interval is exterior. For `a=-1`, an empty prefix
leaves all seven local axes in the remainder. A nonempty prefix has them
all in its first slot; its other slots and its remainder are exterior.
These cases exhaust the statement. In particular, any prefix packing with
all widths in `{7,8}` qualifies. A first width of six would split the local
block, showing why the first-slot threshold matters.

**Factorization corollary.** For a support `A` satisfying the criterion, set

`P_A = epsilon_A K_q + sum_{j in A, j>=8} e_j e_j^T`,

where `epsilon_A` is one exactly when all seven local axes are present.
Distinct supports in the partition give orthogonal projectors. Their sum
is the source pending projector `P(L_b)-P(L_a)`. For orthogonal `P,Q`,
ordinary block multiplication gives

```
D(P) = [[I-P, P], [P, I-P]],
D(P) D(Q) = D(P+Q).
```

Induction therefore identifies the product of every hosted factor and the
retained remainder with the original idle operator, on arbitrary head and
tail vectors. Factor order is immaterial. Its rank is the number of axes:
the local summand has rank seven and the exterior summands are disjoint.
Consequently this application introduces no change to the predecessor's
idle rank histogram or hypothetical moment bill.

**Application to the pinned builder.** PR1736 `verify.build` sets `off=0`
for each child/copy, emits widths 8 followed by widths 7, and increments
`off` by the emitted width. Its retained remainder is the suffix. The
order 8 then 7 is not necessary for the lemma; the prefix property is.
The audit regenerates precisely the plans used by PR1736 `main`, namely
`wopt.solve(k, Fraction(1,570), True)` for every `k=0,...,74`, and checks
each returned slot rather than relying on the builder's assertions.

The source geometry table and controller give disjoint pending intervals
for distinct idle children of the same pair. The audited `(pair,copy)`
supports are therefore disjoint across those children. The map
`(replica,pair,copy) -> 888*replica + 222*pair + copy`, with respective
ranges 32, 4 and 222, is injective and covers the 28,416 typed data families.
Taking its direct product lifts the per-replica statement. This is the
replica-local assignment of PR1736; it says nothing about an interleaved
cross-replica owner map or a physical helper-to-host conversion.

**Sharp distinction at k=1.** Child 0, copy 0 hosts widths 7 and 7 on
`{1,...,7}` and `{8,...,14}`. Swap chart axes 7 and 8 between those two
factors. Both ranks, their disjointness, total child support, helper roles
and windows are unchanged. Now their local ranks are six and one, and
each factor needs completion data. Two rational completions, differing
by an interchange of local basis vectors 6 and 7, give different first
factor projectors but the same whole-child projector. The verifier checks
this at every one of the 111 ports. This is a counterexample to a weakened
inference from ranks/windows to completion independence, not an impossible
allocation or a production-checker defect.

The algebra and source-derived slots settle only this geometric obligation.
They do not establish a native width-seven provider, its intertwiners,
chronological scalar implementation, correlated dirty-helper realization,
H4 or another replacement interface, precision, tapes, the all-size compiler,
analytic transfer, or a multiplication theorem.

Credit: PR1307 for the retained source-level/projector argument; Sagar
Thakrar's PR1736 for the placements and explicit open question; the
PR386/442/510/555/589 lineage for the geometry and source construction.
Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
Apache-2.0.
