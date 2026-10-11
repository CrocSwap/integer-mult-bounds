# Whole-residual replica pooling, complex supplier

## Sufficient construction

Use the inherited PR442 whole dirty-helper hosting theorem, with its universal
arbitrary-correlated-helper scope. For each invocation and helper, choose ONE
physical idle family and ONE rank-nine interval of its pending orthogonal axes.
The complete helper array is routed into that family by a coordinate permutation;
its entire rank-nine residual is conjugated onto that interval. No helper array
is partitioned between families. If every interval is after the family's last touch,
before its pending idle child, off the active data pair, and disjoint from every
other allocated physical interval, the residuals multiply within that family to
its assigned coordinate factor. The remaining factor of the original idle child
completes the unchanged full idle operator. Every route is charged.

For a cover class g the actual owner is the scalar stream (F,g sigma^-1),
not just the family name F: sigma maps the whole local residual onto the selected
nine-axis block. Distinct blocks give distinct routing maps and hence distinct
cover classes within one invocation, even when they share F. The canonical
whole-block coordinate permutation and inherited idle-basis U_q supply sigma.
This preserves PR442's within-invocation owner distinctness; arbitrary aliasing
of two helper variables in the same scalar stream is never assumed.

A replica label is just part of the physical family's index. The local universal
helper theorem does not require matching invocation/host replica labels, so these
same sufficient conditions admit cross-replica whole-family hosting. All replicas
execute a stage before advancing to the next one; eligibility uses strictly interior
stages, so no source/target family is accidentally touched by another replica's
invocation while being borrowed. Host pair is different from active pair.

This is a valid direct-sum reindexing of COMPLETE array families. It is not a
claim that the address coordinates of one array can be split into different arrays.
The latter is false: PR451's trace obstruction is decisive. Our first coordinate
splitting nomination from the parallel lane was discarded. The MUB commuting
projector identities (MUBProjectionInduction20260923.lean, atoms_mul/weighted_mul)
apply within one family; they do not justify crossing array-family boundaries.

## New finite pooling

PR451 selected whole-rank-nine slots independently in each of eight replicas.
We jointly nominate 1920 family copies of each eligible idle child, assigning
4480 entire rank-nine residuals at each of eleven stages. One exact frozen integer
flow is in complex-pooled-selection.json. It has no optimizer dependency at replay.
The source-controlled native HiGHS solve took less than one second; its floating
objective was only a nomination. All integer flow equalities, actual owners,
physical axes and paid counts were then independently rechecked.

Old idle profile:
{1:2104,3:3840,5:3840,7:3832,8:7680,16:8,64:1736}.
New idle profile:
{1:2102,3:3840,5:3840,7:3840,8:7680,55:6,64:1732}.
Delta {1:-2,7:+8,16:-8,55:+6,64:-4}; rank mass unchanged.
This removes per-replica integer packing restrictions while retaining whole
helpers. It is a genuinely different feasible region from PR448's false split
extension, and extends ordinary integer load balancing to physical family routing.
No global packing optimality or literature-wide novelty is claimed.

## Explicit changed global program

complex_whole_emit.py reads regenerated PR433 local programs and fresh PR451
89-dimensional phase recipes. It emits88 invocations and their exact owners,
all idle remainders and phases, bridge/terminal order, cover correction, and the
unchanged private namespaces. Full literal expansion includes2,187,416 instructions.
Its actual transcript SHA256 is a006debfbf3bbb1ff1ee932922f7fe92a5e9ab6bb04a2c1b67e9567413be9bc1.
It does not rerun an unchanged public supplier pipeline or assume a fabricated
parent output directory. It source-binds the unchanged local800-column theorems.

The changed primitive profile is
{1:170358,2:68992,3:18624,4:19712,5:38336,7:3840,8:9792,55:6,64:1732}.
Live9600; physical10178; rank mass851136; deficit3264; largest child64.
Every one of49280 residuals belongs to exactly ONE owner interval.41360 use a
foreign replica. All443520 occupied physical family/axis cells are distinct.
The number of residual-routing operations and their sizes are unchanged: a
host family selector now uses the existing full physical-family index, not a
larger stock or extra split route. The exact finite invoice must nevertheless
be rebound to the emitted program before reporting a new kappa.

## Independent audit and sources

complex_whole_audit.py independently derives chronological windows from actual
execution events; derives each local profile from literal climb/center events;
checks every data and helper owner, physical coordinate and idle complement;
and rejects ten adverse mutations. Complex-whole/AUDIT.json records the fresh pass.
The global phase generator checks exact Z4 polynomials, including translations,
terminal controls and all-live cover correction. Its49,280 whole helper residuals
retain PR451's phase convention and the same local primitive IDs.

Sources retained/credited: PR433 split centres and local scalar architecture;
PR442 whole idle-axis hosting; PR445/451 eleven-stage route and exact phase/invoice
proofs; PR451's correction to invalid cross-family splitting. The library relation
Matrix.fromBlocks_multiply and Matrix.reindex motivate the whole-array reindexing.
The selected integer flow is new to this package; standard scheduling and linear
algebra identities are not claimed novel. No Lean certification was attempted.

Scope remains the inherited all-size compiler, dirty-helper, compressed-window,
phase/precision, row-divisor and analytic contracts. Finite replay and exact outer
pricing support a conditional construction, not an unconditional multiplication theorem.
