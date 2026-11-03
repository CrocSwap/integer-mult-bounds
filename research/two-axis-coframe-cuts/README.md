# Sharp cut threshold for the full two-axis Gaussian chart menu

This contribution was produced by Nick Petalas. Claim type: scoped written
mathematical proof with exact finite corroboration. No new kappa is claimed.

For all fifteen binary Lagrangian planes in F2^4, set
`d(L,M)=2-dim(L intersect M)`. For every real `0<t<=1`, the complete chart
metric `d^t` has a nonnegative cut representation exactly when

```text
2^t <= 3/2.
```

The least real L1 distortion is exactly `max(1,2^(t+1)/3)`. In particular,
it is `4/3` at the linear rank tariff. An explicit five-chart witness
proves the lower bound; fifteen line-pencil cuts attain it. Below the
threshold, an explicit mixture of pencil and singleton cuts is exact.
[PROOF.md](PROOF.md) gives every coefficient and the full argument.

The same witness excludes exact cut representation for the full binary
Lagrangian menu in every dimension with at least two axes when
`2^t>3/2`, including all `t=1-C` with `0<=C<=1/100`. The matching upper
bound is proved only for two axes. This is a restriction on representing
the full chart metric by fixed nonnegative cut coordinates. It is not a
complexity theorem, an exclusion of auxiliary-variable cut reductions,
or an obstruction to all coframe algorithms.

## Why this is a new step in the repository

David Ganz / Dugongue's [PR5693](https://github.com/CrocSwap/integer-mult-bounds/pull/5693)
supplies the inverse-Lagrangian transition-rank interface and a common-anchor
binary cut method. Its source head is `9911c12ab1d1888113c566fe0dbf8a5ce1dbc1bd`.
The new step determines the exact tariff range in which a full small chart
menu itself has cut coordinates, and the sharp unavoidable distortion
outside that range. The source theorem and source word are not replayed or
audited here. This result does not contradict the binary method.

zxv's [PR5283](https://github.com/CrocSwap/integer-mult-bounds/pull/5283)
already has the same numerical threshold for choosing between two specific
three-terminal cache trees. Its topology comparison does not classify cut
representations of the full chart metric; no priority for the numerical
constant itself is claimed here.

Jerry Chen / CubeJerry's [PR907](https://github.com/CrocSwap/integer-mult-bounds/pull/907)
already supplies the repository's pentagonal-inequality precedent for
different shear and Cayley metrics. Finite cut-cone and polar-geometry
methods are classical. The unpowered generalized-quadrangle nonembedding
is also known; see Deza and Laurent, [L1-rigid graphs, Fact 5.10(ii)](https://www.maths.tcd.ie/EMIS/journals/JACO/Volume3_2/x8470250l6u31743.fulltext.pdf).
The powered classification and attaining formulas are derived here for
this coframe interface. No worldwide literature-priority claim is made.

## Reproduce

From the repository root, CPython 3.12 and its standard library suffice:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/two-axis-coframe-cuts/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/two-axis-coframe-cuts/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/two-axis-coframe-cuts
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/two-axis-coframe-cuts --check-source-history
```

Another CPython 3.12 path can replace the displayed interpreter. Direct
replay prints `PASS_TWO_AXIS_COFRAME_CUTS` in a generated JSON receipt with
SHA256 hashes of all six package files. Registered replay also requires
`PASS_REGISTERED_RESEARCH_PACKAGE`. No receipt is hand-written or trusted
as an input. Direct replay works without Git, network or predecessor code
and writes nothing.

The checker enumerates all 35 binary planes, selects the fifteen isotropic
ones, and checks every ordered chart pair by both literal vector-set
intersection and separate binary elimination. It checks all 16,384 cuts
up to complementation, including the empty cut, against the five-chart
separator. All fifteen pencils, every coefficient of the affine cut
identity and 33 exact rational tariffs spanning `1<=a<=2` are checked.
Twelve rejecting controls cover invalid planes, negative cut weights and
an omitted pencil. The continuum statement rests on the written symbolic
proof, not on sampling the 33 tariffs.

## Scope, sources and limitations

Base canonical main is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority
revision 8, selected PR6030. The selected binding example passed; it is
orientation only. The complex-rank-shape-decoder card has changed scope
from a completed supplier to this rank-only algorithmic obstruction.
[TASK.json](TASK.json) records the change. [SOURCES.json](SOURCES.json)
pins the source interface and cut-metric precedent as historical provenance;
no external mathematical input is imported during verification.

[Advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19375394).
Overlap checks covered live PRs and Discussion claims, the account's recent
work, local reservations, targeted main README and merged-PR searches. The
cached search paginated 572 open PRs and 6,639 Discussion records; it searched
only 131 local notes, leaving 8,786 HEAD note paths unsearched. Targeted Git
searches supplemented that sparse coverage. Neither search proves novelty.

No physical chart realization, phase-aware Clifford lowering, independent
productive target, native word, complete paid invoice, dirty restoration,
precision, tape, stock, compiler closure or outer admission is supplied.
All five selected framework assumptions remain. No selected cold replay,
Lean or Docker was run. Independent human and formal proof-kernel review
are unclaimed. The selected frontier is unchanged.

Credit Dugongue and the native, Clifford, helper, matcher, compiler and
analytic lineage retained in PR5693; Jerry Chen and eumemic for PR907's
metric context. Original source notices and source files are unchanged.
New material is Apache-2.0.

## Verifier bounds and diagnostics

There is no recursion, dynamic evaluation, subprocess or input callback.
All domains are fixed: at most 35 planes, 225 ordered pairs, 15 pencils,
16,384 cut masks, 33 tariffs and six package files of at most 1 MiB each.
Each function is below 60 physical lines. Errors use explicit exceptions
and remain enabled under optimization. Registered commands enable warnings
as errors. No separate static analyzer is supplied.

Power of Ten deviation, rules 3 and 9: Python's managed runtime, exact
Fractions, sets, tuples, iteration and standard-library method dispatch
allocate during verification. Fixed finite domains bound live tables to
15 by 15 entries and the plane collection to 35 entries; the cut masks
stream without retention. Receipt hashing reads one bounded file at a time.
No interpreter allocation instrumentation or fixed-allocation native port
is supplied. Expanding these fixed domains requires revisiting those
bounds and the replay timeout rather than silently lifting them.

## Open next questions

Can a named source caller restrict its allowed inverse-Lagrangian charts to
a cut-representable subset while retaining its useful paid transitions and
independent targets? First extract its actual allowed charts and complete
pair-rank table, then test the explicit five-chart obstruction before
optimization. A source-owned legal chart menu, all target debits, phases,
restoration and the full caller price are prerequisites. This theorem does
not justify a larger construction search by itself.
