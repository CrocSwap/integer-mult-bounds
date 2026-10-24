# A same-cost inverse for the actual owned-center macros

Yiyang (@Lyy-iiis), with substantial OpenAI Codex assistance. Apache-2.0.

This is a positive inverse-interface construction for both actual serialized
orientations of the round-three native word in the PR4610 lineage. It removes
the owned-CLEAR obstruction to a particular coherent
inverse construction without adding paid calls. It does not prove a new
Gaussian supplier, a recursive approximation theorem, or an improved bound.

The source is Cao Yifan's round-three native word at
`research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz`. Its SHA-256 is
`7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05`, and its
Git blob is `46d929df83817b85a5387bcdb9745e0627d6366e`. Identical bytes are
present at revisions `0ce1b5c9fb7163d0b2f0ac3db95fc418dbbcec62`,
`1eb8da6cfb35512c0cc2533413e5ca42f48e13c6` and the current base below.
Our initial copy came unchanged through PR4694, head
`2add42d1edf14a263abe90a3bcde67fc1ba30768`, at
`research/retained-center-extension/inputs/round3-native.json.gz`.
No frozen source has been modified. Current research coordination is based
on refreshed main `cef4b52f2a59009865bf8eabde1be3f159063703`.

## The local identity

Let x_i be persistent capture sources, let y_j be persistent target roles
disjoint from every x_i, and let A be a deterministic function. Fix capture
coefficients b_i and fanout coefficients a_j. Consider the macro

```
c = 0
c = sum_i b_i x_i
c = A(c)
for j: y_j += a_j c
c = 0
```

Writing s for the captured linear form, the persistent endpoint is
`x_i'=x_i`, `y_j'=y_j+a_j A(s)`. On arbitrary fresh persistent inputs,
its inverse is

```
c = 0
c = sum_i b_i x_i
c = SAME_A(c)
for j: y_j -= a_j c
c = 0
```

Both directions use one invocation of the same realization A. The inverse
does not call A^-1, reconstruct discarded data from completed outputs, or
reverse a CLEAR. Every capture source remains unchanged, so both the captured
linear form and the second evaluation are identical. This identity does not need A to be linear,
invertible, unitary, or numerically exact. It needs repeatable evaluation on
the same input and exact adding/subtracting of the same increments.

Literal reversal of the extended circuit with fresh zero garbage would
attempt to recover a discarded, generally nonzero C0 value from zero. The
present construction instead computes a different straight-line program
for the inverse of the persistent map.

## Binding to both retained source orientations

Each retained program has 21,449 records, 632 persistent L roles and one
reused C0. Each contains eight consecutive 26-record center macros with
sixteen CLEARs. The forward program has eight COPYs; the backward program
gathers by ADD and has no COPYs. Every COPY/CLEAR lies inside these macros.
There is no other explicit owned or zero-buffer role in this serialized layer.

Every macro clears C0, captures a linear form, calls its paid center,
performs its fanout and clears C0 again. The two source shapes are:

| Retained orientation | Capture | Paid center frames | Fanout |
| --- | --- | --- | --- |
| Forward | Copy one persistent source | rank 8 to rank 0 | 22 ADDs, each coefficient ±1/4 |
| Backward | Sum 22 persistent sources, each coefficient ±1/4 | rank 0 to rank 8 | One ADD, coefficient -1 |

The forward sources, and corresponding backward destinations, are
`92,57,81,224,11,240,9,256`. In each backward macro the 22 capture sources
are disjoint from its single destination. In both orientations all capture
sources remain unmodified between capture and final clear. The generator
checks every record, frame, coefficient and capture/destination intersection.

Separately for each retained word, reverse the order of these macros and all other
operations. Invert persistent ADDs, invert nonzero dyadic-unit SCALEs,
invert each actual warp/adapter, and call the actual inverse of the same
persistent paid-child realization. Replace each center macro by the
same-A/negative-fanout macro above. Each inverse center macro retains its
source macro's paid orientation: rank eight to zero in the forward source,
zero to rank eight in the backward source. Neither is the literal reverse
frame itinerary. The retained backward program is not assumed to be the
actual inverse of an approximate forward program; it gets its own inverse.

The resulting persistent input frames are the source's final frames and
the resulting output frames are its start frames. Every intermediate scalar
source/destination frame and every paid/warp boundary has been checked.

## Exact paid bill

Each retained complete word and its constructed actual inverse have this
same paid profile:

```
{1:2201, 2:412, 3:510, 4:127, 5:40, 8:8}.
```

Each orientation retains all eight paid rank-eight jobs; no erased buffer
is credited as an independent output. There are no extra paid rank-one
reconstruction calls. In particular, the initially considered final-center
reconstruction is unnecessary: the forward macro's actual discarded value
is in frame zero, not frame eight.

The inverse has the same scalar gate count inside each center macro.
Negating a fanout coefficient preserves its magnitude and denominator.
Other inverse scalar/route implementation constants must still be included
in any compiler allowance; they are not paid recursive calls.

After the established disjoint-axis splitting, a two-full forward or
coherently inverted recipe therefore retains the optimistic paid invoice
`{1:4656,2:920,3:1386}`. At the declared rank-call level the macro replacement
adds no paid calls; it makes no assertion about additional precision costs.
It does not establish that the
full approximate algorithm can attain the raw `.0048568755...` crossing.

## Workspace and exact arithmetic contract

Each persistent paid child is required to be a bijection on its declared
field, with an implementation of the inverse of that SAME realization.
The unchanged invoice assumes this inverse is available at the same declared
rank charge. Both directions must restore any private workspace. A statement only about
the child's projected productive output is insufficient. Center children
need only be deterministic on their field and privately clean, since they
are recomputed in the same orientation.

Under these hypotheses the complete persistent program is a composition
of bijections. It is therefore a bijection, and the constructed inverse is
its exact two-sided inverse. This structural closure survives finite
composition, permutation routing and the finite precompiler's fixed
schedule. It does not assert that the resulting bijection equals, or is
close to, its intended Gaussian operator.

Exact dyadic arithmetic on a sufficiently fine grid makes ADD/subtract and
nonzero dyadic SCALE mutually reversible without quantization at return.
A finite dyadic word always has such an exact grid for finite dyadic input;
its necessary width and magnitude are not automatically the inherited
linear semantic guard bound. A fully charged uniform precision proof is
still required as the word and accuracy vary.

There is also a narrowly reversible rounded-shear implementation: compute
the deterministic increment `round_grid(a_j A(s))` and then add it exactly
to y_j. The inverse recomputes and subtracts that identical increment.
The capture may itself be evaluated by a fixed deterministic rule, provided
the identical rule sees the identical unchanged sources in both directions.
This does not justify rounding `y_j+a_j A(s)` as a whole, rounding a SCALE,
overflowing an accumulator, changing the child rounding policy between
directions, or dropping private garbage.

A rounded bijection can be nonlinear. Its exact reversibility alone does
not supply the linear operator-ring identities used by the Laurent border
controller. Those identities require their own proof for the chosen
actual realization.

## Executed checks

`verify.py` authenticates the actual source bytes and Git blob, extracts
all sixteen macros, and recomputes `INVERSE-RECIPE.json.gz`, an explicitly typed
inverse IR for both orientations with source event IDs. It distinguishes
`same_retained_orientation` center
children from `actual_inverse` persistent children. It is a reviewable
recipe, not an already admitted native compiler format.

The checker passes under isolated optimized Python:

```
PYTHONDONTWRITEBYTECODE=1 python3 -I -B -O verify.py
```

The frozen receipt is `RESULT.json`. Default verification is read-only and
compares both the canonical inverse recipe and the recomputed receipt. Use
`--regenerate` explicitly to update them after reviewing a construction
change. The recipe hash covers its exact decompressed canonical JSON;
gzip headers and compression streams are not mathematical evidence.

For each source orientation, the checker verifies both full 632-role round
trips on two sets of independent two-coordinate rational inputs: eight
whole-word round trips in total. Each persistent query site is assigned its own near-identity
dyadic shear, deliberately without imposing Gaussian/frame relations;
each center uses a deterministic nonlinear rounded function. Thus this is
a stress test of the inverse contract, not another ideal native endpoint
replay. Five controls in each orientation reject a changed center realization,
an unnegated fanout, a fresh nominal inverse instead of the actual inverse,
a changed captured linear form, and a source-overwriting fanout.

An independent native-integration check previously confirmed the eight
forward macros and 48 local round trips. The present checker does not import
that check; its generalized source parser and whole-word round trips cover
both source orientations separately.

## What this does not yet supply

The inverse of a complete native word reverses its productive D orientation.
It is not automatically a second fresh-D supplier with opposite central
shear. Approximate internal children may also destroy the source's
`D U(q)` factorization and other Gaussian/frame relations. Same-word
invertibility does not recover those identities.

Consequently the remaining constructive task is a caller/compiler whose
*actual* two orientations use this coherent inverse and whose complete
main/helper endpoints still match the intended jobs. Error correlation,
private-workspace cleanup, scalar range, exact or rounded execution and
the full paid invoice must be proved together at that caller. The macro
result supplies one concrete piece of this task without a paid-call
surcharge; it does not stand in for the rest.

A concrete sufficient compatibility target is a family of coherent frame
potentials A_f: an actual paid climb from a to b would equal A_b A_a^-1,
and an actual warp W would equal A_new W A_old^-1. Inverse pairs alone do
not imply these relations. The inherited physical warps would need the
corresponding intertwining without new paid calls, together with the
fresh-D caller and precision bounds above. Testing that requirement on
the actual paid-site realization is an open next step.
