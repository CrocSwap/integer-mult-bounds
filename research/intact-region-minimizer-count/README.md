# Exactly 2^43 intact-region minimizers in each orientation

This contribution was produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

The fixed-boundary intact-region model has exactly
**8,796,093,022,208 = 2^43 minimizing chart assignments in each orientation**.
The minimizing set is a complete Boolean cube. Of the predecessor's 203
residual binary region choices, 160 are fixed and 43 vary independently.
The free region IDs and all fixed bits are identical forward and backward.
Every minimum has the same rank histogram throughout `0<t<1`.

This is a scoped equality-class proof with an exact finite certificate. It
answers the uniqueness gap in Krzysztof Wojt's
[PR #5024](https://github.com/CrocSwap/integer-mult-bounds/pull/5024), whose
README explicitly makes no uniqueness claim. His optimum, graph reduction,
source correctness and elimination certificate are **cited premises**. This
package neither reruns his native word nor re-establishes that optimum.
The new result identifies every equality case and shows that their set does
not depend on the exponent inside the open interval.

Chris R / Clear1nsight's open
[PR #5161](https://github.com/CrocSwap/integer-mult-bounds/pull/5161) already
proves that all `2^43` subsets of its 43 declared zero moves preserve the
paid and helper invoices, following Cinna Davis's #5124 census. That
construction retains credit. The new step here is the **converse completeness
statement** for #5024's entire intact-region domain, including every one of
its 203 residual binary choices. The numerical count agrees; this package
does not compute a mapping between the two packages' region/group IDs or
assert equivalence of their different declared domains.

## Why the equality class matters

An unchanged minimum recursive moment leaves a substantial choice of charts.
A later contributor can restrict a finite routing, storage or precision
objective to these 43 independent bits, instead of searching all 203 bits
again. This result supplies that exact domain. It does not claim any reduction
in those additional costs, legal absolute-phase lowering, physical execution,
supplier admission, improved kappa or selected-frontier change.

The fixed scalar word, native maps, start/final charts, owned-center interfaces
and intact source zero-edge regions are the hypotheses of #5024. Changing a
region boundary or splitting a region remains outside this theorem. The
43 choices count assignments of contracted-region subspaces, not physical
circuits, bases for a subspace, labelled owners or independent forward/backward
circuits that may be combined without another compatibility proof.

## Equality extraction theorem

Let a certified binary bucket-elimination trace have the meaning established
in #5024. At each step its two candidate histograms are the exact conditional
minima for the eliminated bit. Keep the recorded choice when the comparison
is strict, both choices when the histograms coincide, and no choice when
both candidates are infeasible. This gives one Boolean relation on the
eliminated bit and its later separator bits.

**The complete global minimizing set is exactly the conjunction of these
relations.** To prove this, reverse the elimination order. Given a minimizing
assignment of later variables, a strict loser cannot extend it to a minimum;
each equal candidate can. Each retained candidate has a minimizing extension
by the predecessor's elimination invariant. Repeating this step includes
every minimum and excludes every nonminimum. Disconnected terminal buckets
combine independently because their eliminated variables are disjoint.

In this source, every unequal certified comparison is strict for all
`0<t<1`. For majorization, strict concavity of `r^t` on the nonnegative reals
makes equality possible only for identical sorted rank lists. The histograms
already distinguish these lists, with equal edge counts including rank zero.
The five exceptional power inequalities are strictly positive in #5024's
written proof. Forced choices have no feasible alternative. Thus no isolated
exponent inside the interval adds an equality branch. This is a consequence
of the cited inequalities, not a new audit of them.

[verify.py](verify.py) performs exact sum-product elimination on the new
Boolean relations. It counts the assignments and each bit's two marginals.
Each orientation has 43 varying bits, each with `2^42` solutions per value;
the other 160 bits are forced. The total is `2^43`. Since the solution set
is a subset of the cube on those 43 bits and has that cube's full cardinality,
it equals the whole cube. The receipt contains all 203 marginals and the
complete fixed/free classification.

[independent.py](independent.py) proves the same cube by a different method,
with no primary-counter or predecessor-code import. It removes unsupported
bit values until the domains stabilize. Every removal is necessary for any
solution. It then explicitly enumerates each local Cartesian product and
checks that **every** tuple in it is allowed. This second step proves
sufficiency; arc consistency alone would not. Four passes leave 160 singleton
domains and 43 two-point domains, and 270 local Cartesian tuples per
orientation certify the full product. The source relations have 552 allowed
rows before propagation in each orientation.

## Explicit enumeration and reproduction

[RESULT.json](RESULT.json) is generated by the primary verifier and binds the
source witness and package verifier/document bytes. Its `free_regions` list
is sorted. For each integer `0 <= j < 2^43`, assign free region number `k`
the bit `(j >> k) & 1`, and use `fixed_bits` at every other binary region.
Choose the lower or upper basis in the predecessor witness's `bounds` row
according to that bit; all nonbinary regions keep their unique bound.
This is a bijection and an explicit enumeration without storing trillions
of assignments. Region IDs refer to #4997's contracted graph, not word offsets.

Use CPython 3.12 and the standard library, from the worktree root:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/intact-region-minimizer-count
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/intact-region-minimizer-count --check-source-history
~/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/intact-region-minimizer-count/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/intact-region-minimizer-count/independent.py
```

The manifest registers both direct commands in normal and optimized modes.
The main success marker is `PASS_INTACT_REGION_MINIMIZER_COUNT`.
`verify.py --write` explicitly regenerates only RESULT.json. Ordinary replay
compares its freshly computed receipt and writes no package files.
Controls include a coupled equality pair whose two varying marginals do not
form a cube, independent factors, contradictory relations, an unreachable
conditional tie, duplicate variables and propagated implications.

## Scope, provenance and implementation limits

Canonical base is `a5df48c55ea806d7952b65acc9c76d878ff09b13`, priority revision
7. TASK.json preserves the original `complex-rank-shape-decoder` card and
records its changed scope to this equality question. The card's decoder
synthesis experiment is replaced by equality extraction from #5024's first
working certificate, because this contribution does not propose a new paid
profile. The selected baseline metadata orientation passed separately.

SOURCES.json pins the live compressed witness and preserves the predecessor
proof/README as Git provenance. No predecessor executable is an input.
The universal equality-extraction argument and strictness above use #5024's
proved trace semantics. The finite verifier establishes this pinned trace's
new equality class. It is not independent validation of the native graph,
absolute phases, arbitrary dirty endpoints or the predecessor optimum.
No native/all-column, compiler, stock, precision/tape, complete selected cold
replay, Lean or outer multiplication proof is run or claimed.

All new loops have finite input or explicit iteration bounds; the source is
capped at 203 variables, separators at three bits and the decompressed witness
at one million bytes. Both algorithms are iterative. Python's managed
allocation is a Power of Ten deviation: tables have at most 16 entries,
integer counts at most 204 bits, and at most 406 elimination factors. Package
metadata checks and warning-strict normal/optimized replays supply the
available diagnostics. Assertions are not verification gates.

## Open next questions

Can one of the 43 independent minimum-moment chart choices reduce a concrete
routing, storage or precision cost? First attach that actual cost to the free
region IDs, retain all incident operations and absolute phases, and compare
fully charged alternatives. A physical implementation and a complete consumer
bill are the blockers. This package assigns no such improvement.

Can splitting one source region exploit a minimum-moment choice to remove an
actual paid transition? Coordinate with the broader
[PR #4993](https://github.com/CrocSwap/integer-mult-bounds/pull/4993) before
selecting one literal split. The first test needs its exact operator, dirty
restoration, all new edges and full cost. The intact-region theorem does not
answer that changed-boundary question.

## Credit and overlap

Chris R / Clear1nsight #5161 and Cinna Davis #5124 retain the existing
43-zero-move family and its `2^43` invoice-preserving subsets. This submission
adds exhaustive equality classification in the intact-region model.
Krzysztof Wojt #5024 supplies the global optimum, complete elimination witness
and five strict all-exponent comparison arguments, with the first three
inequalities credited there to Cinna Davis #4997. Cinna Davis supplies the
intact-region graph/model. Dugongue #4971 supplies carried-frame swaps and the
retained native source. Cao Yifan, zxv, Jacob Alan Sussman, James Reed and all
contributors named in those predecessor packages retain their attribution.
No predecessor file or credit line is changed.

The broader numerical domain of #5016, Clear1nsight's small-component
fixed-price result #5068 and Cinna Davis's continuing #4993 search have
different restrictions. Their minima and search results are cited, not
recomputed here. Live PR bodies, this account's recent work, handoffs, active
Discussions, merged/main-tree terms and question reservations were checked.
The overlap cache covered 331 open PRs and 4,359 Discussion records; sparse
local notes were supplemented with all-main README searches. This is bounded
overlap evidence, not a novelty certificate. Unpublished work and arbitrary
code diffs remain outside coverage.
