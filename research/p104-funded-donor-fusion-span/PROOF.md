# Exact compensated-fusion scope

The frozen word uses the following emitted events.

| Clock | Operation |
| ---: | --- |
| 37764 | Capture x863 in owned role 1568 on chart 240 |
| 48182 | MOVE public role 1355 from 739 to 240 |
| 48183 | ADD −2 times owned role 1568 to public role 1355 |
| 48184 | MOVE public role 1355 from 240 to 127 |
| 76460 | CLEAR the chart-240 cache on role 1568 |

Replace the three middle events by one direct MOVE 739→127, and retain
every other event and both stationary cache lifetimes. Allow additive
corrections from that cache into any existing public role other than
863 or 1355 on the exact literal chart 240. The insertion cut k is
immediately before event k. Eligible cuts are 37765 through 76460,
inclusive. They are bounded by the second capture and the terminal CLEAR.

In normalized coordinates a MOVE is identity on the logical row and
changes its chart. The retained capture gives the original arbitrary
input x863. It is a source only from cut 37765 until its CLEAR. An
injection into a public role after the capture cannot change this
cache. In particular the omitted ADD has no effect on propagation of
such an injected perturbation. Every allowed correction therefore adds
its rational multiple of a suffix column `S_k e_r`, the final public
response to an impulse in recipient r at cut k. The missing response is
`−2 S_48184 e_1355`. Any permitted exact arbitrary-input replacement
requires this response to be in the span of the eligible columns.
The condition already grants arbitrary rational coefficients, with no
limit on the number of columns. The argument only needs a necessary
normalized action, so a negative result does not depend on proving
physical compatibility of a new correction.

The full reverse walk records chart-240 contact representatives,
including both operands of every scalar and both MOVE endpoints. It
visits 52 cut representatives with 1,003 cut-role pairs and finds
39 distinct nonzero columns. Exact rational echelon reduction has
rank 25 and leaves a nonzero residual. The engine checks the returned
dual directly on every retained column and the full target response.

The independent walk checks both sides of each chart-240 contact and
the endpoints, for 82 boundary cuts. Chart occupancy is constant
between these boundaries. For an eligible role r, the response
`S_k e_r` is constant between its scalar contacts. Every intervening
operation fixes an impulse in r, including normalized MOVE. Deduplication
by r and its next scalar contact leaves 59 conservative classes.
A direct forward impulse gives the full target response and the
reverse scalar adjoint checks the classes. It agrees with the full
span on `e_1109`, whose target pairing is −8 and whose column pairings
are all zero. This exact separator excludes any combination of the
eligible responses. Zero unvisited keys and no literal candidate remain.

## Directed price

The certified comparator upper crossing is
`36462214364462343366888845568981/10000000000000000000000000000000000`.
The 17-copy signed change is `ΔP={1:−17,5:−17,6:+17}`, with `ΔT={}`.
Paid count would fall from 110,536 to 110,519. Productive fields stay
22,461, rank surplus stays 1,424 and empty-root credit stays zero.
The exact optimistic gross credit upper is
`834294887484332658348023951079438343074582560347/5000000000000000000000000000000000000000000000000`.
It prices a single compensated split and grants extra costs free.
The directed complete margin at the incumbent crossing is positive
before adding any new position. The upper becomes negative with one
extra rank-one paid position.

The price-only crossing is approximately
`(0.00364665195642084, 0.00364665195644889)`. It pertains to the
hypothetical invoice. The fixed-chart support is empty and κ is unchanged.
Changed charts, owners, capture times or surrounding chronology are
outside the exclusion.
