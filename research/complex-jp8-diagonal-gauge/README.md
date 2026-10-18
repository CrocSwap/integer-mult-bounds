# Optimal restored diagonal gauge for the historical PR626 JP8 cleanup

**Research construction / finite complex-supplier circuit improvement; no new κ.**

The #622 JP8 provider consumed by historical #626 has a full-frame cleanup of
8,894 additions and 112 scales. A simultaneous, restored power-of-two change
of 203 live register coordinates saves **6,154 real-component scalar
primitives in each orientation**, after charging all boundary scaling.
An exact integer primal/dual certificate proves optimality within the specific
constant-diagonal class below. It does not prove circuit optimality.

| Complete JP8 scalar program | Original | Candidate |
| --- | ---: | ---: |
| Forward real primitives | 257,232 | 251,078 |
| Inverse-transpose real primitives | 257,280 | 251,126 |
| Scalar macros, either orientation | 22,693 | 23,099 |
| Forward positive prefix bound, bits | 64 | 70 |
| Inverse-transpose positive prefix bound, bits | 101 | 101 |

The 406 added scale macros are explicitly charged: 916 real primitives.
Adjusted addition coefficients save 7,070 real primitives, for a net 6,154.
The forward positive prefix envelope increases by exactly 64; both orientations
remain below the inherited 192-bit local allowance. There is no claim of a
practical runtime improvement or complete supplier-cost improvement. The larger
macro count can increase the generic adapter allowance; that allowance is not
included in the scalar-primitive saving. Global invoicing is not performed.

## Reproduce

From the repository root, with Python 3.11 or later and its standard library:

```sh
python3 -B research/complex-jp8-diagonal-gauge/check.py
```

The final line is:

```text
PASS_JP8_GAUGE_COMPLETE saved=6154/6154 optimal_cost=10326 tests=10 inherited_controls=25 kappa=unchanged
```

The command checks the exact certificate and all native input columns, runs a
separate integer-arithmetic cleanup replay, then feeds the candidate to the
unchanged pinned native emitter and local frame/wrapper auditor. The inherited
25 controls must reject. Generated files live only in a temporary directory.
`verify.py` alone is the read-only, solver-free arithmetic checker.

No SciPy, SymPy, compiler, network access, or new source download is needed for
verification. Optional `discover.py` requires NumPy and SciPy and prints a new
nomination; it does not overwrite the checked certificate. It was run using
NumPy 2.3.5, SciPy 1.17.0 and `linprog(method="highs")`. Different solver versions
can nominate different equal-cost optima. Solver status is never a certificate.

## Exact construction and restoration

Let the original cleanup map be `A` and let
`D = diag(2**g[r])`, with integer exponents. Execute:

1. Scale each nonzero-gauge register by `2**g[r]`.
2. Keep every cleanup gate in order. Replace each addition
   `x[t] += q*x[s]` by `x[t] += q*2**(g[t]-g[s])*x[s]`.
   Keep the original scale gates unchanged.
3. Scale each affected register by `2**(-g[r])`.

The middle word is `D A D^-1`, so the complete map is exactly
`D^-1 (D A D^-1) D = A`, for arbitrary register inputs. This is not an argument
restricted to clean helpers or a reachable subspace. Applying inverse transpose
to each chronological gate gives the original inverse-transpose cleanup as well;
the corresponding diagonal basis is `D^-1`.

All 203 affected registers already have terminal frame FULL (frame ID 1).
Neither an early-ended helper nor a target register is rescaled. The new scales
occur wholly inside the original full-frame cleanup, before its post-wrappers.
There are no new helpers, source copies, frames, recursive children or centre
operations. The 492 helpers, 716 native columns, all non-scalar events and the
paid rank histogram are unchanged. The checker verifies these facts against the
selected SPEC and the inherited auditor independently checks frame incidence,
wrapper ordering, arbitrary dirty-helper restoration and the paid profile.

## Exact optimality certificate and its scope

Write each nonzero addition coefficient uniquely as `q = ±o*2**e`, with positive
odd integer `o`. Under the retained original binary-Horner lowering, its complex
component cost is

`2 + bit_length(o) + popcount(o) + abs(e)`.

The numerator's sign is handled by signed accumulation. Every source addition,
doubling, halving, accumulation and private-work clear is included. A scale by
`2**g` costs `abs(g)` per complex component. Thus the only varying part of the
complete component cost is

`P(g) = 2*sum_r abs(g[r]) + sum_additions abs(e + g[t] - g[s])`.

The first term pays BOTH boundary changes. Original internal scales are
unchanged, so their costs cancel. Each real-component program costs twice this
component convention. The zero gauge has objective **13,403**; the candidate
has objective **10,326**, saving `2*(13403-10326) = 6154` in each orientation.

For each addition the certificate supplies an integer `f` in `[-1,1]`. Define
`div[r] = sum_(t=r) f - sum_(s=r) f`. The checker verifies `abs(div[r]) <= 2`
for every register. For ANY real vector g:

`P(g) >= sum_e f[e]*e + sum_r (2*abs(g[r]) + div[r]*g[r]) >= sum_e f[e]*e`.

The certificate's last sum is **10,326**, exactly the candidate's cost. This
proves a global minimum for the relaxed expression and therefore for every
integer gauge, without a bounded enumeration or trust in floating arithmetic.
It remains a finite-word theorem, not a formalization of integer multiplication.

**The class is precisely:** one constant positive power-of-two diagonal basis
throughout the entire fixed JP8 cleanup, paid separate boundary scales,
unchanged chronological additions and internal scales, and the original
Horner lowering. It excludes changing gauge mid-word, signed diagonal choices,
boundary-scale fusion, scale relocation, addition resynthesis, coefficient-work
sharing, different lowering, and altered frames or ownership. No claim of
uniqueness, optimality in those larger classes, or improved κ follows.

## Evidence and search coverage

`CERTIFICATE.json` gives all 716 exponents and 8,894 edge dual variables.
`EXPECTED.json` pins exact generated cleanup/program digests, both full costs,
and rational prefix envelopes. `SOURCES.json` binds every consumed source;
compressed inputs are accepted by decompressed payload, not gzip container.
`verify.py` also checks both word/program bindings against #626's SPEC.

The exact rational interpreter checks all 716 native columns simultaneously,
plus eight arbitrary private-centre columns, in both orientations. Separately,
846 distinct original/candidate coefficients are lowered into explicit original
Horner primitives on formal target/source/arbitrary-work inputs. This proves
the macro substitution and its full clearing cost. Whole-program matrix replay
uses these verified macro semantics; it is not claimed to execute every primitive
on every full matrix row.

`test_verify.py` implements cleanup matrix arithmetic using integer rows and
binary exponents instead of Fraction, checking all 716 arbitrary input columns
in both orientations. Its ten tests include missing entry/exit scales, a wrong
conjugation coefficient, box/divergence/gap failures in the dual, dirty work,
aliasing, illegal frames, changed source blocks, and an exact-identity excursion
that violates the prefix allowance. Fifty small integer/rational matrix replays
cross-check the second arithmetic engine.

OS assignment seed **35** chose the complex track; odd parity selected JP8.
The first bounded screen used seed-35 shuffled coordinate descent over
`[-2,2]`, at most ten sweeps, stopping on a sweep with no strict improvement.
It completed seven sweeps and nominated a 4,840-real-primitive saving. This
positive complete budget justified replacing the bounded screen by the exact
convex-dual nomination on the SAME word/mechanism. The final exponents range
from -2 to 7. The final coverage is all integer constant gauges via the above
dual proof, not an assertion that coordinate descent exhausted its search cube.
No retired supplier search was reopened.

## Provenance, overlap and remaining obligations

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Reviewed #622: `f69477f4f6d3c7eb1f740b166881bffed4ffa9f6`.
Selected #626: `660de893d27bb7abd1d5b01b1640207528a5c851`.
Retained #543: `2065fe4f72a914d907f1046603f5a36f17018535`.
At the research base, accepted κ was `51110230636731/31250000000000000`.
At publication refresh `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`, the selected
record is #1094, κ = `836330098538459/500000000000000000`. This package
studies the frozen #626 circuit, not the newer frontier. `SELECTED-AT-BASE.json`
is a byte-identical copy of the original selected record; its original path and
hash are retained in SOURCES.json so future frontier updates do not break replay.

Credit to Jeremy Kothe and the #622/#623 contributors for JP8/K-triangle
construction, Chafik Boukhalfa for #626, icekylinx for the original emitter and
direct-delivery lineage, DreamingOfClouds for cold-helper/native checks,
Dominik Scholz and Dugongue for prefix work, Rohan Arun for recurrence work,
eumemic for #543, and all predecessors retained in the maintainer review.

Concurrent #750 (`b6d6934092c063ab2575ebee00f48bbc7b1c9d82`) optimizes one
existing CK scale's position. This adds a simultaneous JP8 diagonal sandwich
and an exact global certificate for its distinct class. #739
(`abb9825202dba6f9bc95c7df8d12d86088fdff1a`) rescales private coefficient work;
this changes live register coordinates and preserves per-macro work clearing.
#696/#723/#734 lower individual coefficients, #722/#751 share preparation,
#769 (`e891b2b19e3185ec91bcf001e255af87f42389ce`) shares CK coefficient work
across varying-magnitude ladders, #755
(`a1dd9f819102c40e0b5e4a75215cf69ee864f480`) extends JP8 coefficient reuse
across scalar phases, and #749 uses a restored target basis in compensation.
Those pending
implementations are not imported. Savings are measured against the accepted
base and are not asserted additive to concurrent results without a composed
recount. The local claim records the three candidates and refreshed overlap.

Only this research package is added. The selected frontier, native production
emitter, global owners, source archives and `upstream/` are unchanged. Production
integration would need a typed diagonal-cleanup construction step, refreshed
bindings and prefix receipts, plus global invoice and outer-admission replay.
The inherited all-size compiler, common-label/mutable-basis realization,
pooled hosting, residual, precision/tape/exact recovery, bit-supplier and
analytic-transfer assumptions remain. No full repository/cold replay, remote
CI, Lean multiplication proof or new asymptotic exponent is claimed.

Prepared for **Luis Leon (@mythrilium)** with substantial **OpenAI Codex**
assistance in research, implementation, checks and writing. No independent
human peer review is claimed. New files are under the repository's Apache-2.0
license. No copied predecessor source or notice is replaced.

## Publication overlap and open next questions

The publication-time search also found #786 (quarter factoring and adapter-cost
warning), #793 (larger JP8 compensation savings through coefficient routes),
#984 (single-block scale deferral), and #949 (a different fixed 26-ADD factory
gauge census). Those results are not imported or claimed additive. This package
adds a simultaneous 716-coordinate cleanup gauge and an exact unbounded-domain
primal/dual optimum, not a best-scalar-saving headline. Search results are bounded
overlap evidence, not a novelty proof.

- Can the same gauge fit a fixed-macro lowering? First derive the complete adapter
  invoice with the 406 extra macros; it may erase the scalar saving. This blocks
  any complete supplier improvement claim.
- Can one compose the gauge with #793's coefficient reuse? First reprice one
  shared-source run with both boundary scales. The present dual only certifies
  the original per-add lowering and does not establish an optimum for that class.
