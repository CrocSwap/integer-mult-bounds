# Polylogarithmic spectators for the retained coordinate router

## Result and scope

The retained coordinate router can use a spectator with `s = h^2` address
bits, where `h = ceil(log2 p)`. It does not need a spectator of width
`Theta(p^(1-epsilon))`. This change removes the router condition
`epsilon > a`, where its admitted bit-interchange exponent is `tau = 1-a`.

The result is conditional on the same equal-width arbitrary-gap
interchange and fixed-tape scan interfaces as the original router. It
changes neither the arithmetic precision nor a local supplier. It does
not increase the currently certified multiplication kappa. It does not
remove the complex guard `b < 1/32`, the Gaussian guard `r < 1/4`, the
small-field exposure charge, or a phase normalization condition.

## Source and credit

The source checkout is pinned at
`a900f98be8ff2c09d3292b5112d4731dbd0c8438`. A separate GitHub blob
query confirms that the seven used files are identical at refreshed
main `681e8923a0f23a19f93c7105c3a9c96149aa8362`. The receipt is
`frontier/refresh-2/OUTER-BLOB-PINS-CHECKED.json`. These retained sources
are unchanged dependencies:

- `references/semantic-bulk/rad20/reports/compact-arbitrary-source-routing.md`:
  masked shears, local repair, three scratch reservoirs, matching routing,
  the two-involution decomposition, and spectator placements.
- `references/semantic-bulk/rad20/reports/review-arbitrary-routing.md`:
  source/target masks, current-address repair, complete record charges,
  the suffix convention, and original width-one fallback operations.
- `references/semantic-bulk/rad20/reports/bulk-resampling-tape-transfer.md`:
  full-volume layouts, small-field transposes, fixed tapes, and restoration.
- `references/semantic-bulk/rad20/reports/downstream-semantic-bulk-assembly.md`:
  the seven outer margins and the retained analytic conditions.

The RaD source is `hipotures/rad` at
`45d9b60355872041f9275f77c057514def0d45bc`, carried by PR20 at
`4f8d6c8272b5ff307a0da51df545ec3cd96a8b6e`. The router also retains
Douglas Colkitt's complete chunk-interchange interface and the inherited
finite-alphabet, fixed-tape model. The bulk composition retains the
credited PR23 work of Zhihao Chen and icekylinx. This result only changes
the choice of borrowed spectator width. It does not claim these earlier
constructions as new. The source notices and Apache-2.0 license remain.

## Conditional cost proof

Let the stream have shape `[P] x [2^n] x [R0]`, bit volume `V`,
`n = O(p)`, and total address width `O(p)`. Let a supplied coordinate
permutation have polynomial setup and descriptor costs in `p`. Assume
`0 <= tau < 1`. Each original complete interchange of two disjoint
width-`u` fields costs `O(V*(u^tau+1))`. The original fixed-block
implementation of one elementary XOR costs `O(V)`.

Put `h = ceil(log2 p)` and `s = h^2`, for `p >= 2`.

If `n <= 3s`, decompose the permutation into two involutions and perform
their matching swaps with three elementary XORs per edge. There are
`O(n)` such XORs. The complete charge is
`O(V*n) = O(V*(log p)^2)`. Every width-one placement and its return
are included in this charge. The global supplied-map/setup term remains
polynomial in `p`.

If `n > 3s`, take the first `s` slots, the next `s` slots, and the
last `s` slots as three disjoint spectator fields. Partition each
matching into three edge classes. Each edge avoids at least one field:
an edge has two endpoints and the fields are disjoint. Assign the edge
to the first field it avoids.

For one class, move its untouched spectator to the actual suffix with
one original width-`s` interchange. The first and second fields have
disjoint suffix destinations because `n > 3s`. The third field is
already the suffix. This convention also works in the strict boundary
range `3s < n < 4s`; a consecutive third front field would overlap
its destination in that range.

The complete payload record now has length `R = R0*2^s`. No address
coordinate or payload is added. For every fixed descriptor degree `A`,
the inequality `p <= 2^h` gives

    2^s = 2^(h^2) >= p^h >= p^A, when h >= A.

Thus a fixed polynomial amount of arithmetic per record or controlling
fiber is absorbed by its complete record volume. The old local repair
bound, counters, descriptor scans, and stable reinsertion charges still
apply. This uses the same complete records as the original argument.
It does not add an address oracle or omit a per-record cost.

Run the original scratch-reservoir router on the remaining `n-s` prefix.
Every edge in this class lies in that prefix. If the prefix has fewer
than `64G` bits, its elementary cost is `O(V*G)` with
`G = 4h+6`; this is another polylogarithmic term. Otherwise the original
three scratch reservoirs, residue classes, masked rotations, and exact
bad-address repair apply without a change. They cost
`O(V*(n-s)^tau*polylog(p))`, plus polynomial global setup. They leave
the suffix spectator unchanged.

Return the spectator placement after the complete class. This restores
every original coordinate name. Repeat for the other two classes and
the second involution. There are at most six classes, so the charged
spectator moves cost `O(V*(s^tau+1))`. All inverse, rewind, and return
scans remain in the retained complete-interchange and router costs.

Combining both cases gives

    M(V,p,n) = O(V*p^tau*polylog(p) + poly(p)).

This bound holds for every `n = O(p)`, including short coefficient
records. It has no condition on `epsilon`. The statement uses eventual
fixed constants, as does the original asymptotic router theorem. A finite
initial range can use the same elementary fallback.

For each fixed positive exponent gap `t`, `h^2 = o(p^t)`. The full
tensor has `n = Theta(p)`, so its spectator fields exist eventually.
The same proof covers the smaller dimensions that occur in CRT and
resampling: their complete supplied permutations are either in the
spectator case or in the paid polylogarithmic fallback case. Polynomial
global setup is retained and is absorbed by the intended full tensor
volume, as in the original theorem. The code does not change a supplier
cutoff or assert a bound on an inherited ordinary constant.

This is a layout of address fields. Enlarging a payload record does not
combine its coefficients into one arithmetic coefficient. Each scalar
word, coefficient precision, Gaussian operation, control, and restored
row has its original value and charge. The same fixed set of tapes is
used. Spectators are borrowed from existing coordinates and returned;
there is no new live field, allocation, or recursion dependency.

## Exact checks

The harness uses the unchanged independently written RaD routing
operator. It checks its pinned hash and executes actual packed rotations,
current-address inverses, bad-address repair, dirty temporaries, all
spectator placements, scratch placements, and both matching involutions.
A separate named-slot calculation checks the borrowed fields and returns.

The deterministic run with seed `110509` passes 4,280 complete tiny
payload addresses, 192 larger forward/inverse route probes, and 96
independent named-slot classes. The cases include `n = 3s-1, 3s, 3s+1`,
the range below `4s`, and `n = floor(p/6)`. The actual guard parameter is
`G = 4h+6`. The largest tested width is 5,461 address bits. Tests include
good compact calls and bad-address corrections; they do not reduce the
guard to make a case pass.

Three negative controls reject an overlapping consecutive third field,
an omitted return placement, and a merely logarithmic spectator that
does not absorb a quadratic descriptor bound. Exact descriptor controls
also check fixed degrees 1, 8, 64, and 256.

Run:

    python3 -B verify_polylog_spectators.py --source-root /absolute/pinned/checkout --output /absolute/new/receipt.json

The test supports the finite identities and layouts. The written cost
proof supplies the all-size transfer. Neither proves the full conditional
asymptotic integer-multiplication theorem independently.

## Remaining limits and the next required change

With the current numeric guards retained, the original bound
`kappa < 1/33` still applies. If only the complex guard is replaced with
a new valid supplier proof, the retained Gaussian guard still gives
`kappa < 1/4`. This spectator change removes neither guard.

If both guards later receive valid replacement proofs, the old
golden-ratio obstruction from `epsilon > a` no longer applies. The
retained model nevertheless has

    kappa < epsilon*q <= epsilon,
    kappa < 1-epsilon,

because an ordinary local saving cannot exceed one and `q < a <= 1`.
Therefore `kappa < 1/2`. This is a limit of these declared cost terms,
not a lower bound on all multiplication algorithms. The retained
small-field exposure and Gaussian normalization conditions also remain.

The harness gives an exact rational relaxed row with `a=4/5`, `b=9/10`
and margin about 0.4444435. Its old short-record slack is negative,
and its remaining non-numeric margins have positive exact slacks.
This is a parameter comparison, not an admitted supplier or exponent
record. It violates the still-retained complex and Gaussian numeric
guards. No constructed circuit with these hypothetical savings is
asserted.

For a path to `kappa = 1`, the compact-layer depth and Gaussian
normalization charges must also change. Even an ideal linear-volume
layer has `q <= 1`, while there are `Theta(p/d)` layers. The compact
layer margin is at most `epsilon`. The retained Gaussian normalization
requires `epsilon+r < 1`, while the Gaussian boundary margin is below
`r`. These charges cannot both give a saving near one.

The scalar-pass and conventional short-axis product charges also
contribute `d` and `p/d` work per complete stream volume. Their
exponents are `epsilon` and `1-epsilon`. A recursive fast multiplier
could reduce the short-axis product term, but it would not remove the
compact-depth and Gaussian-normalization obstruction above. A valid
next construction needs a new paid compact/analytic reduction, rather
than a parameter change alone. A local circuit improvement cannot
reach the target through the present seven-margin model.

Prepared with OpenAI Codex assistance. Apache-2.0.
