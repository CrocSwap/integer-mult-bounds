# Primary rational numerical method — unexecuted implementation

This method independently bounds only the six finite hypotheses H for the
frozen nine-rank law, for every alpha in the declared bracket. It does not
prove the existence or location of the tilt root, assume that the actual
mean equals log5, evaluate a convolution or validate the all-n local-limit
or flow theorem. The source LOCAL_LIMIT text is an inert mathematical
specification; no predecessor checker or peer implementation is read,
imported or executed by this engine.

## Logarithm enclosures

For p in{2,3,5}, put z=(p-1)/(p+1). Then

`log(p)=2*sum(k>=0,z^(2k+1)/(2k+1))`.

The first80 positive terms give a lower bound. The remaining tail is at
most `2*z^161/(161*(1-z^2))`, because each omitted denominator is at
least161 and the powers form a geometric series. All operations are
Fraction arithmetic. The lower endpoint is rounded down and the upper
endpoint up to the rational grid Q=10^18. Floor/ceiling are implemented
by exact integer division, not a binary floating conversion.

Each rank is factored into2,3,5. Summing the corresponding log intervals
gives its natural-log enclosure, including log1=[0,0]. The runtime rejects
a rank with any other prime factor. Only the frozen rank support is used.

## Exponential enclosures

The nonnegative argument interval is the alpha interval times the rank-log
interval. Its upper endpoint must be less than4; violation is a failure,
not a silent extension of the declared numerical domain.

For an endpoint x, sum terms0..79 of the positive Taylor series. This is
a lower bound for exp(x). The first omitted term is x^80/80!. Every
subsequent ratio is at most x/81<1, so the full remainder is bounded by
`(x^80/80!)/(1-x/81)`. Apply this upper bound at the upper endpoint and
the positive partial sum at the lower endpoint, then round outwards to Q.
No approximate exp implementation is called.

## Probabilities and actual-mean centering

For each rank r, multiply the exponential enclosure by its nonnegative
literal count. If the resulting normalizer interval is [L,U], with L>0,
then a weight [l_r,u_r] has probability enclosed by [l_r/U,u_r/L].
All nine rank keys remain present, including zero-count control atoms.
An all-zero law fails the positive-normalizer guard.

All log values are nonnegative. Summing products of probability and log
endpoints therefore bounds the actual mean mu and raw second moment m2.
If mu is in[m,M] and m2 in[s,S], the variance belongs to
`[s-M^2,S-m^2]`, since the mean is nonnegative. Dependence between
probabilities and their normalizer can widen these interval bounds but
cannot invalidate them.

For a rank-log interval[l,h], its absolute distance from the actual mean
is at most `max(abs(l-M),abs(h-m))`. Cubing this value and summing against
upper probability endpoints bounds the third absolute centered moment.
The largest such distance over positive-count ranks bounds the centered
support. Both use the actual expectation interval throughout, rather
than substituting the inherited special value log5.

The three atom lower bounds, variance interval inclusion[2,3], third
absolute-moment upper bound5 and centered support upper bound3 must all
pass before any certificate is emitted.

## Actual-engine controls

The same numerical engine evaluates laws with rank3 count zero, alpha
interval[0,0], and rank1 count zero. These must respectively fail the
atom_log3, variance_2_3 and atom_0 predicates. Setting every count to zero
must fail the positive normalizer. These are changed input distributions,
not changes to a claimed answer. The log bounds are safely reused because
the ranks themselves do not change.

Four parser controls reject duplicate JSON keys, numeric floats,
nonfinite numeric tokens and a Boolean supplied as a rational value.
Rational proof values must be strings exactly equal to str(Fraction(value));
unreduced fractions, negative denominators, decimal spellings and Boolean
values are rejected. JSON Booleans are allowed only where the complete
certificate requires actual Boolean hypothesis/control outcomes; complete
canonical regeneration distinguishes them from integers everywhere else.

## File and full-certificate protocol

Before numerical work the engine checks all11 exact FILES manifest paths:
both engine source files; CASES/SCHEMA/SOURCE-PINS; and all six inert inputs.
Every listed SHA256 must match, no required path may be omitted, and no
duplicate or unexpected path is allowed. CASES, SCHEMA and SOURCE-PINS
also have independently frozen hashes in the primary source. The original
acquisition manifest spells its local paths INPUTS/...; the runtime has
inputs/... and uses the fixed validated basenames to authenticate those
same six byte objects. No source file is edited to accommodate that spelling.
Peer code is read only as raw bytes for manifest hashing, never imported.

`--emit PATH` explicitly writes the complete own certificate. Default
replay requires HERE/CERTIFICATE.json; `--certificate PATH` selects an actual
retained packet for mutation controls. Both modes regenerate the complete
certificate, including all method-specific rational endpoints and eight
control results. The parser validates canonical rational fields and exact
key/type shapes, then compares complete canonical JSON byte strings.
Summary flags alone cannot make a changed method, enclosure or extra field
pass. The primary and independent oracle methods intentionally need not
produce equal enclosures.

## Freeze and resource expectation

Implementation is standard-library Python3.12/Fraction, without assertions,
float arithmetic or numerical packages. No import, execution, py_compile,
test or scientific trial has been performed at this code-readiness point.
The frozen first will be run only by root after its source/manifest seal.

Expected work is three80-term log series and at most five nine-rank
interval-law evaluations, each with two80-term exponential endpoint sums.
Final enclosures are rounded before downstream moments, keeping retained
rationals modest. Expected runtime is comfortably below the180-second
first-run cap and expected memory below128MiB; these are forecasts, not
measurements. Any failure or exceeded bound must remain in the first-run
record rather than being relabeled a clean first.
