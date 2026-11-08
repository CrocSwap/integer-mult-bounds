# Independent review of costly-first G20 A2 compensation

Prepared by @CubeJerry with substantial OpenAI GPT-6 assistance, as the
caller-accounting reviewer in the same authorized research team, 2026-11-08.
This is a bounded independent review of the incremental invoice and the
exceptional paths; it does not independently re-enumerate 5,114,417 paths.

## Mathematical findings

No issue was found in the incremental-state or route-floor argument.

For E=(a+=b), deleting the left gate makes the transformed state equal to
E times the original state. At each later original event followed by its
forced correction, only row a differs, by old_a XOR old_b. For b+=s, b updates
normally and the correction a+=s restores this invariant with the new b.
For d+=a, the transformed source old_a XOR old_b and correction d+=b cancel
the extra old_b. The reversed gate is excluded, so these cases do not overlap.
All remaining ADDs and resets away from a,b commute with E. Deleting the
right gate restores every formal input column.

The request accounting follows the pre-event rows, including the important
zero cases:

- If old_a=0 and old_b is nonzero at d+=a, the original event made no requests.
  Its transformed pair requires d at the contact frame; exactly one additional
  third-role request is necessary, charged iff old_d was nonzero. The second
  request is at the same frame. After correction, d's row is restored, but its
  frame change persists and must be included in the suffix bill.
- If old_a=old_b is nonzero, the transformed original event is skipped, while
  the correction retains the old third-destination request. No extra third
  request is needed and the a request disappears.
- If neither source vanishes, the old third-role request remains valid; only
  the two distinguished role histories change. A b+=s correction reuses the
  already requested source frame on s.

Starting from the previous request's frame, replacing the interval requests
and including the first unchanged subsequent request/reset is exact: that
request restores a common frame, and all formal rows already agree after the
right gate. Later costs coincide. A final public return can be that first
suffix request. This justifies the code's local splice without omitting
restoration or zero-row header effects.

The non-edge strengthening is universal in the declared routing model.
A distinct non-edge request requires at least two positive-integer-rank
native edges. If their total is S>=d, concavity and subadditivity give
sum(r_i^t)>=1+(S-1)^t>=1+(d-1)^t for every 0<t<1. A non-edge cannot have d=1.
The correction must be applied per occurrence; collapsing duplicate endpoint
pairs would undercharge the lower bound. Different demands remain separately
charged, as required by the source emitter contract. Shared or cancelled
routes are outside this result.

The two raw exceptional shapes have total coefficient -1 and are negative
near t=0, so the unstrengthened rank-distance relaxation does not prove a
universal loss. The mandatory non-edge refinement produces the displayed
nonnegative, nonzero hinge vectors. The discrete expansion in min(r,k) has
strictly positive coefficients for r^t, proving strict loss on all of (0,1).
The five zero differences can be attained at the paid-query level because
every nonzero demand is an actual native edge; this says nothing about a
new complete supplier or its ordinary costs.

The prior [#6324](https://github.com/CrocSwap/integer-mult-bounds/pull/6324) README was also checked: its final all-native theorem covers
all 22 neutral first moves and 49,865 second intervals, distinct from its older
14-first-move fixed-table calibration. Thus combining this costly-first
result with that neutral-first theorem closes the specified two-rewrite domain,
while leaving deeper rewrites and changed contacts/interfaces outside scope.

## Independent executable review

Portable replay from the repository root:

```sh
python3 -I -B research/g20-costly-first-compensation/independent/check_review.py
```

`check_review.py` separately reconstructs the two rewritten scalar words from
each descriptor, fully interprets every resulting event and all 685 columns,
prices every actual nonzero role demand including final returns, counts each
non-edge occurrence, and compares the result with both incremental stages.
It authenticates the source files, reconstructs the edge catalogue from the
pinned geometry implementation, and checks the reconstructed metric against the
previously authenticated metric digest. It does not rerun the domain search.

Executed on Python 3.12.14: PASS_INDEPENDENT_COSTLY_FIRST_REVIEW. All 35
paths passed; the results are 30 strict losses and five zero paid differences.
Reviewed trace SHA256:
`41617a06d3abb4b3627c354199e8a8a20f4e0955f8d08b7f79835429e6cd08b6`.
The complete source receipt SHA256 is
`afa1e5a39379bc054a28f96d934c4d771c5710990c553cec4bf857923f8df3ce`.
Exact per-path results are in REVIEW-RESULT.json. The local review used an
existing metric cache only after source equality, edge reconstruction and
pinned metric-digest checks. The portable version reconstructs the metric
from authenticated source files and removes the cache/pickle dependency; it
also authenticates the reviewed trace before importing it and compares the
review receipt read-only by default (`--emit` explicitly regenerates it).
The native geometry/metric source remains inherited rather than newly proved
by this review. No native-size, compiler, precision, outer theorem or selected
frontier replay is claimed.

The portable checker was additionally executed from this package in normal
and optimized Python 3.12.14 modes; both matched REVIEW-RESULT.json exactly.
