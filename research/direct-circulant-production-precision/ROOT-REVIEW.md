# Orchestrator review of the local precision theorem

Accept the stated source-specific numerical implication under its named
compiler, phase and exact native-service contracts. The proof does not
discharge any whole canonical assumption and does not improve kappa.

The frozen accepted proof has SHA256
`26e4e214f0a5785c1d1414561465bb49a3248f9e6f59f6b514eb95a887bdfe2f`.
Its original pre-review status is retained for byte identity. The later
separate acceptance is in `review/CROSS-REVIEW.md`.

## Critical boundaries

I checked the complete proof and separate review. The leading-section bound
comes from strict accretivity of the actual rounded stored root, not just
invertibility of its full matrix. The full compiler's fragment and inverse
estimates remain explicit premises. An interval is controlled using both
its prefix and inverse prefix; endpoint conditioning alone would not suffice.

The literal lowering has 23 diagonal factors and 16 H factors, including
38 non-pivot factors. The corrected count remains inside the conservative
`64^40` allowance. The data-error recurrence treats the diagonal and H of
an emitted entry as separate steps, so a newly rounded diagonal error is
propagated through the subsequent H. An H itself is exact only under the
stated widened-grid native-service premise.

At each odometer write, the cached suffix is an expression in the current
coordinate factors. A carry rebuilds the changed suffix and retains only
suffixes with unchanged arguments. Thus the number of rounded operations
behind one coefficient depends on the number of axes, not the number of
previously visited tensor records. The independent noncommutative oracle
tests this dependency directly rather than relying on numerical cancellation.

With `M=R=2^E` and
`epsilon=(d+1)^2 2^(-P+A)`, the proposed selector gives both the strict
bootstrap spend and
`C 2^(-P+A+2E) < 2^(-4p)`, since `C < 2^bit_length(C)`.
The computed-state bound is consequently a conclusion of the bootstrap.
The exact tensor endpoint bias is separately charged. Opposite-sign
execution uses input/output conjugation, an isometry; it does not require
the component-rounding rule to be odd.

The recovery corollary retains the true volume, CRT character, no-wrap,
digit scaling, public-grid conversions and native-service hypotheses.
The final scalar inequality `144/B^2 < 1/2` alone would not establish those
interfaces. In particular, this package is not an independent proof of the
full direct-circulant multiplier.

## Executed publication checks

The orchestrator ran the registered three-command replay with CPython 3.12.
The normal and optimized author executions passed, as did the separately
authored Gaussian-rational and noncommutative lineage checks. The complete
registered output is retained in `evidence/registered-replay.txt`.

```sh
python3 -B scripts/research_package.py --package research/direct-circulant-production-precision
```

Expected final marker:
`PASS_REGISTERED_RESEARCH_PACKAGE research/direct-circulant-production-precision outcome=completed`.

The author evidence includes 203 two-wire words, 2,448 odometer records,
60 allocator bindings and 53 selector inputs. The independent reviewer
checks 600 words across all pivots and 1,214 noncommutative records. Both
paths contain meaningful rejection controls; rerunning the author's checker
is not relabelled as independent reasoning. The universal inequalities are
the written proof, not an extrapolation from these finite examples.

The source export preserves six exact executable fixtures with Git blob and
SHA256 pins, canonical provenance, source-proof citations and review hashes.
The main proof, compiler estimates and source artifacts are unchanged by
publication integration. Strict source-history preflight is not claimed
from the shallow checkout. No complete selected replay, production-sized
transform, private-tape proof or full multiplier kernel proof was run.

## Novelty and remaining work

Ali Romman's #7849 supplies the direct construction and original generous
selector. This package gives a smaller sufficient selector for that same
chronology and the same strict raw error target, while proving the old
selector sufficient as a corollary. #7981 changes the chronology and target
and has an asymptotically smaller selector. This is explicitly not an
improvement over that successor. The source-local root and interval bounds
remain reusable evidence only after checking a successor's changed caller.

The outstanding substantive step is to connect the external error/radius
contract to all-size private-grid storage, backing and native tariffs.
The retained full compiler estimates and exact phase service also remain
named hypotheses. No selected certificate or accepted bound is changed.

Hosted CI success is not claimed: the unchanged canonical base has a
preflight documentation mismatch between #6030 in `docs/ci.md` and #7000
in the selected record, observed on #8091 before research package selection.
The local registered replay is the executed scientific evidence.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
The author, reviewer and orchestrator were separate model task roles;
this is not independent human peer review. All predecessor credit in
README.md, the proof and source notices is retained.
