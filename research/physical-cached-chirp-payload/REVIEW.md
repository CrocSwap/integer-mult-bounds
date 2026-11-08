# Independent chirp source and physical review

Prepared for @CubeJerry by a separate source-aware OpenAI verifier. This is
independent mathematical and code review, not human acceptance or a proof-kernel
certificate. **No new κ.**

## Frozen objects and method

Reviewed `chirp_consumer.py` SHA256
`47b91b4b9773453b24064604d174dc1fb5304b76d1477c39f414f4517ecb51a1`,
`chirp_tapes.py` SHA256
`cc257f302317fcfe332725a070fd9f90f20aa6b53bf0a70a9a3e0de20baa792b`,
and `chirp_tables.py` SHA256
`221077b7660dc991d997d62065aec336d49b108d0307c1140b3e95ab4b9b8925`.
The all-size arithmetic service is the authenticated, unchanged predecessor
cohort; this review does not implement a second integer multiplier.

`dyadic_chirp_oracle.py` encloses the actual roots through positive half-angle
square roots using integer `isqrt`, then outward complex interval powering.
It does not invoke pi, Taylor series, floating trigonometry, the producer's
root routine, or the consumer's cached expression. `ORACLE.md` proves the
enclosure invariant and distinguishes a demonstrated bad coefficient from an
inconclusive enclosure. The source adapter certifies 342 actual table rows and
342 literal conjugates in five families. All six semantic mutations reject
with the expected specific reason. Ordinary and optimized Python runs pass.

## Actual physical output against original coordinates

For the actual source `(t0,t1)=(8,4)`, `(s0,s1)=(7,3)`, radius one and target
ten, the producer selects `f=14`, `W=17`. The independent harness supplies a
signed, complex, radius-one input to the physical caller and decodes every
returned bit by direct tape reads. It does not call the author's rounded
oracle or fixture harness.

At flat position `j`, direct Euclidean division gives its original mixed-radix
coordinates. Because all radices divide `t0`, the exact phase is enclosed as
one power with exponent

\[
  \sum_i s_i x_i^2(t_0/t_i)\pmod{2t_0}.
\]

This calculation has no cached suffix or rounded intermediate phase. The
original complex input is multiplied into that interval, and its exact
distance from the physical return is bounded. Both fresh calls process all
32 outputs and perform exactly 264 scalar products. On a 74-bit oracle grid,
the maximum component-l1 errors are bounded by

| Mode | Exact error upper bound | Admitted bound |
|---|---|---|
| Forward | `1243310444594337577 / 9444732965739290427392` | `3/4096` |
| Conjugate | `2394935997974925667 / 18889465931478580854784` | `3/4096` |

The wrong original conjugation fails the stated error bound in both cases.
The forward output SHA256 is
`27331660174be5076cbf44b22bd38ffcf51a79735d53b7d44bebeb28222fcf7b`;
the conjugate output SHA256 is
`4f16140140b3b29cf19a5a10e841f7a0ee352c18c82b8f0a56fa39b31109f538`.

The same harness checks every borrowed byte and head position, consumes the
return, and independently enumerates all Tape objects reachable from the
closed owner. That object traversal exactly matches the declared inventory:
all 1322 roles, including inactive descendants and historical backing, are
blank at canonical origin. This observer runs outside the physical program.
The owner retains 3795 cells after the source call and still retains that
amount after a shorter subsequent fixture; erased historical storage is not
removed from the accounting.

## Executed arithmetic counterexample

A valid coarse prepared table at `f=2`, `W=6` has the factor `(2,-2)` and
payload `(1,1)`. Completing the real sum before division gives
`(1*2 - 1*(-2))/4 = 1`; individually truncating the two products first gives
zero. The actual caller returns `(1,0)` at that position. A disposable physical
subclass which calls the same four scalar products but truncates them before
their sums returns `(0,0)`. Both execute 28 scalar products for the complete
four-position fixture and erase their owned roles. This is an executed
rounding-semantic counterexample, independent of the much looser final norm
allowance. No production source was modified.

## Universal interface and cost review

No blocking discrepancy was found in the source or physical composition.
The following obligations were checked against the actual functions.

* `initialize` binds shape fields to exact table extents, verifies the unit
  zero entry, initializes every suffix to one and leaves the first table head
  immediately after entry zero. Nonzero phase semantics remain a prepared
  source premise; a structurally valid arbitrary page is not authenticated by
  this scan.
* `advance` increments only adjacent counter fields. At the first nonoverflowing
  field `j`, it reads the unchanged adjacent suffix `j+1`, then recomputes the
  changed suffixes in descending order. Lower reset digits are zero, matching
  `previous_page`'s return to each previous page's first entry. Final overflow
  checks both complete catalogue and input endpoints. These establish the
  fresh rounded suffix invariant for every depth and unequal radix family.
* `rounded_product` invokes the inherited four exact scalar products and exact
  component sums before the two truncations. `emit` conjugates the completed
  phase exactly when requested, reads one payload pair and writes one pair.
  Numerical values and variable counts stay in encoded tapes. Host record
  counters are diagnostic only, and fixed finite object references select
  reusable physical roles under sealed construction.
* Cache slot replacement validates and encodes the full new pair before
  creating an interior blank. With the ordinary no-concurrent-mutation
  contract, subsequent copying cannot strand the rest of the cache. Borrowed
  origins, ordinary failure cleanup and the explicit pending-return guard
  match the advertised ownership boundary; asynchronous interruption inside
  a private write is not a recovery guarantee.
* Let `L_j=product_(i<j)t_i`. There are exactly
  `U=sum_j(T/L_j-1)<2T` updates and `4(T+U)<12T` scalar products. Axis zero's
  sequential entries and returns cost `O(TW)`. For `j>=1`, each encounter with
  page `j` traverses at most `O(t_j W)` cells, at most `O(T/L_j)` times. Since
  `t_j<=t0` and `L_j>=t0*2^(j-1)`, their total is `O(TW)`. Initial catalogue
  validation and final restoration add `O(W sum_j t_j+d)=O(TW)`. Local encoded
  fields and the explicitly priced offset products do not introduce a scan
  through all `d` fields per payload. All word work remains charged as
  `T M(W)` under the inherited service's own premises.

The resulting online invoice and explicit source-preparation invoice support
this one pointwise chirp pass. They do not assemble the outer transform,
Gaussian solver, CRT supplier or integer multiplication proof. Finite physical
fixtures use the inherited word engine's base branch; they do not independently
verify its all-size FFT branch. The checks were executed under normal and
optimized Python; all logical gates use explicit exceptions, not `assert`.

Portable retained APIs are `chirp_source_review.run(producer,fresh_factory)`
and `chirp_physical_review.run(bundle)`, the latter inside the authenticated
physical runtime. The registered package verifier supplies those dependencies.
