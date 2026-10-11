# Conditional R715 composition

## Local word and exact reconstruction

The starting artifact is the byte-pinned R715 word published in PR463.
Its discovery history is not used as a correctness oracle. A separate exact
replay verifies the 955 formal columns, restored helpers, source/target
boundaries, nested frames and integer source support. The final word is
also exported into the inherited records and checked by independently
compiled C++ legality and defining-decoder column programs.

For each selected entrance E, the dirty target response of a pivot p is
the F2 sum of its selected donor responses. The entrance is nonzero,
root-spanned, and contained in the first frame of every participant.
Pivots and donors are disjoint; a donor serves one entrance; retained
centres are excluded. The unchanged shared-donor construction starts p at
E, removes its frame-zero completion reads, adds p into its donors at E,
and undoes those additions after cleanup at the full frame. The exact
response equalities and frame conditions are checked for all 109 pivots,
103 donor slots and total entrance rank 120. This is the inherited kernel
construction, with a new frozen selection rather than a new compiler rule.

Next apply 56 receiver/donor target mixes. Receivers and donors are distinct
and disjoint. At the selected frame G, the two targets' helper-delivery
prefixes agree as F2 multisets. Add the donor target to the receiver at
frame zero, XOR their centre-scatter rows, omit the receiver's shared
prefix, and add the donor target at G. The two copies of the donor's
initial value, compensation and scatter cancel; precisely its shared
prefix remains. All dirty helper and target columns therefore retain their
required final values. The reconstruction checks these exact set identities,
frame inclusions and the complete intermediate word.

Expand grouped additions into their primitive sequence without changing
order. Apply 60 frozen single-gate changes in A and 14 connected pairs
(28 gates) in B. The latter are bound to PR467's actual operands and old/new
root frames. Each moved gate remains between its participants' preceding
and following frames and contains its integer source-support lower bound.
Gate operands, coefficients and order do not change. Thus scalar semantics
are unchanged, and the exact nested frame realization remains legal.
The final word must equal the supplied frozen word in every field.

The local paid histogram is

```
rank       1     2    3    4   5   6  8
count   2396  1076  232  311  72  72  9
```

All 955 local columns pass exact F2 replay, including arbitrary helper dirt.
The stronger integer source-support check also passes. Independent records
check 1,195 five-stage and 1,915 eleven-stage columns; omitted deliveries,
wrong frames, mispriced moves/copies, missing compensation and an eight-copy
build are rejected. Gram matrices are positive and nondegenerate on all
958 frames. The separate four mixing controls reject missing zero-frame,
scatter or mixed additions and an incorrect mixing frame.

## Shared physical labels and residual routes

For a frame F with orthogonal projector P, the inherited bit address map is

```
D_F = [[I-P, P], [P, I-P]].
```

It is an involution over every admitted odd address field. Its pullback Λ_F
on F2-valued streams is independent of whether a register is called a source,
helper or target. For a common address bijection D,
Λ(f XOR g) = Λf XOR Λg. Consequently an addition commutes with a common
block-diagonal label. Induction through additions and frame changes gives
the common-frame realization, with the inherited COPY/ERASE semantics.
This is the same realization required by PR454; finite checks do not prove
the all-size compiler contract.

The new label audit reads every record, verifies both operands' actual
current frames on all 112 target additions and reconstructs the 57 exact
16-by-16 address involutions involved. Its F3-address/F2-value controls
check 648 shared-label commutations and reject unequal labels on 54 columns.
The two fields have different roles and are not identified.

All 11 helper entrance frames are coordinate subspaces. Stored root rows
divided by two form an exact orthonormal completion: the first rows span
the entrance, and the remaining rows its residual. A checked sequence of
at most seven swaps reduces each matrix to the identity. Extend by identity
in dimension 78 and move the residual coordinates to their assigned idle
slot. The full inherited 144-factor route overcharge is retained. Exact
projectors verify all 3,396 nested and reflected frame pairs.

## Eleven stages and eight pooled replicas

The unchanged geometry has K=5, L=11, m=78 and 120 ports. Each of eight
replicas has five source/target pairs. The integer ten-wire bridge/exchange
schedule is the identity; every local endpoint and bridge sees the same
complete level. Every one of the 24 omitted bridge shears is rejected.
The emitted unbanked scalar program separately checks all 9,065 columns,
including a distinct set of helpers for each of the eleven stages.
All 1,320 data routes are inherited from a freshly verified parent and
bound to the new word's identical ordered source labels.

Pool the eight replicas when choosing idle host families. Every helper
occurrence has one physical family, one contiguous residual slot and its
original full residual width. A host can lie in a different replica, but
its pair is untouched by every local call or bridge throughout the required
window. All 62,920 occurrences are expanded and independently checked for
coverage, capacity, owner identity, slot disjointness and idle timing.
The four-replica whole-hosting construction of PR462 extends by changing
the finite replica index range; no new residual decomposition is used.

The retained whole-call correlated-helper interface treats a complete local
call with its arbitrary dirty input and its full residual operator on each
owner. Idle coordinate factors have disjoint pending subspaces and commute;
the remaining idle child uses exactly the unused coordinates. Each residual
stays entirely on its owner. There is no conjugacy between one residual
and a direct sum on different physical families. The all-size hosting and
compiler realization remain explicit conditional interfaces.

The resulting paid histogram is

```
rank       1      2     3     4    5    6    7   8  34  56
count 211200  98367 20416 30728 6336 8256 4192 792   1 652
```

Its rank mass is 745,536 and
78*9,600 - 745,536 = 3,264 = 8*(1,200 - 11*72).
There are 9,600 live and 9,609 physical families, no banks and no omitted
remainder children. The independent audit reconstructs the local streams,
owner map, schedule and all 1,726,296 renamed instructions. Twenty-two
mutations reject changes to ownership, windows, widths, replicas, stages,
operators, routes, counts and residual coverage.

## Physical growth and finite accounting

As in PR462, maintain a nonnegative cancellation-free row-L1 bound for every
physical family in chronological order. Initialize live bounds to one and
private work to zero. ADD updates B_dst by |c| B_src, including when the
logical owners alias. COPY copies the bound; erase resets private work.
Every bridge is included. Bit climbs and residual routes are address
permutations and do not increase this envelope. Updating a whole-family
bound overcharges a restricted-coordinate operation. This gives an
inductive bound within the retained cover/compiler interpretation, without
assuming independent borrowed contents. A separate traversal recomputes it.

The maximum needs 804 bits, charged at 832. The complete finite coefficient
needs 804 bits and includes all 15,440 local additions per call, all 23,040
bridge additions, 792 copy/erase episodes, 62,920 helper selectors, private
work, local compilers and paid children. Every helper route retains its
residual isometry charge plus the two hosting factors. The three-level
coefficient (C+1)^3(E+1)^3 needs 2,468 bits, charged at 2,496 in every bootstrap
cutoff. The old 192/1,024-bit allowances are not reused.

Halving holds because 78^3 > 2*56^3. The uniform orthogonal-cover count from
PR445 gives stock exponent 3,090 and complete row coefficient 19,431, below
20,161. The complex supplier retains PR458's paid two-sided wrappers,
one-helper-per-family-per-invocation condition and 788,480 charged wrapper
groups. Its full phases, operator audit, moments and finite invoice are
freshly rebuilt in default mode. The complex row contract remains 20,161.
The common outer degree gap is therefore unchanged.

## Rational assembly and scope

Two independent rational moment engines certify the bit interval
[0.001293771240692396056124, 0.001293771240692396056125]
with the inherited bad-branch allowance and opposite strict endpoint signs.
The recomputed paid complex lower endpoint is
0.001297203880559577927527. The bit side binds.

Using η=β=10^-18, six strict bootstrap steps with the enlarged finite cutoff,
and all 47 outer inequalities gives

```
κ = 646049779721139 / 500000000000000000
  = 0.001292099559442278.
```

The next 10^-18 grid point and zero-eta, zero-beta and unit-beta controls
are rejected. This is a conditional finite composition. No finite test here
discharges the inherited all-size realization, hosting, compiler, analytic,
common-grid/tape, restored-work, precision or row-divisor assumptions.
The kernel, retiming and packing are not claimed globally optimal. The
scoped architecture ceiling from PR458 still applies; κ=1 is not established.
