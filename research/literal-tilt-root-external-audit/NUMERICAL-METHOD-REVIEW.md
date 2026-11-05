# Pre-first static review of the two tilt calculators

**PASS for the reviewed arithmetic-inclusion algorithms and acceptance path;
no blocking mathematical/code discrepancy found.** This is pre-execution
static review of BUILD/primary.py, BUILD/oracle.py, their algorithm notes,
CASES/SCHEMA/SOURCE-PINS, and the coordinator's PROOF.md. I did not execute,
import, compile, parse code with AST, or run either scientific engine. Numerical
endpoint separation, actual controls, resources and whole-certificate outcomes
remain pending the coordinator's sealed first runs. This review is not a
passing execution receipt and does not claim independently checked code hashes.

## Primary: range-reduced atanh and positive Taylor series

For u in[1,2], z=(u-1)/(u+1) lies in[0,1/3]. After96 terms, the code's power
is z^193. The remaining positive log series is bounded by
2*z^193/[193*(1-z^2)]: every later denominator is at least193 and the powers
form a geometric series. The returned exact-Fraction interval therefore
contains log(u), including exact log1=0. Writing r=2^e*u with integer bit length
gives log r=e*log2+log u, using only nonnegative interval combinations.
The last floor/ceiling to denominator10^60 is outward, also for exact zero.

For exp, the argument interval is the positive rational alpha times the log
interval, rounded outward. Its checked upper bound is8. The lower Taylor
recurrence floors a lower previous term times the lower argument; the upper
recurrence ceilings an upper term times the upper argument. All factors are
nonnegative, so induction bounds each of terms0 through127 and their sums.
The next upward recurrence encloses term128. Every later ratio is at most
x_upper/129<1, so the code's geometric tail division bounds the entire omitted
positive tail. The final denominator and width guards are real acceptance
gates. Fixed grid rounding in the recurrences widens the enclosure; it is not
an uncounted remainder. No transcendental floating library call is used.

## Oracle: Simpson integral and exponential sandwiches

For u=a/b in[1,2], the node integrand is exactly
N*b/[N*b+j*(a-b)], with N=32768 even. Integer floor/ceiling at denominator
D=10^100 separately bounds every node. Simpson's weights are positive, so
weighted lower/upper sums and the final positive h/3 multiplication, rounded
outward, bound the exact Simpson approximation. On[1,2], f(t)=1/t has
|f''''(t)|=24/t^5<=24. Composite Simpson error is at most

    (u-1)^5*24/(180*N^4)=(2/15)*(u-1)^5/N^4.

The code subtracts/adds the ceiling of D times this quantity. It need not
assume a direction for the quadrature error. All node/sum rounding is already
included before that truncation bound. u=1 returns exact zero. Nonnegative
range-reduction combinations preserve enclosure.

For M=2^128 and0<=x<M, elementary log inequalities give
(1+x/M)^M<=exp(x)<=(1-x/M)^(-M). The lower code base is D times1+x_lower/M
rounded down. Its upper base is D/(1-x_upper/M) rounded up, using the exact
integer expression D^2*M/(D*M-x_upper). The checked denominator is positive.
Both bases are nonnegative. Each of128 successive squares rounds its lower
endpoint down and upper endpoint up; monotonicity of squaring proves inclusion
by induction. The resulting power is exactly M, not128. Finite grid loss and
the sandwich gap affect width only; strict final endpoint signs decide whether
the chosen precision succeeds. This is genuinely different from the primary's
log-series/exponential-series method, while sharing the literal law/spec.

## Mean, residual and finite/universal boundary

Both methods enclose every positive weight P_r*exp(alpha*log r), then sum its
normalizer and its nonnegative product with log r. After verifying a positive
normalizer lower bound, division uses N_lower/A_upper and N_upper/A_lower.
Oracle also rounds those divisions outward. Subtracting the opposite log5
endpoints encloses the actual normalized mean minus log5. Positive normalizers
make these residual signs equivalent to the unnormalized F signs in the proof.
Strict left upper<0 and right lower>0 are required; a midpoint or zero-containing
interval cannot pass. Log/weight dependence may widen bounds and causes no
false inclusion. The executed object is two rational endpoint enclosures,
not a sampled derivative or a purported exact floating root.

The conclusion Boolean strict_variance_all_real is not a numeric test over
all real parameters. It records the guarded finite premises (distinct positive
ranks with positive counts) combined with the written variance proof. The
coordinator PROOF correctly differentiates the normalized mean, proves its
variance strictly positive, and uses positive rank1/rank48 and0<log5<log48
for all-real existence/uniqueness. It correctly does not assert F'>0. Its bridge
to S5 requires S5's actual-mean centering throughout the bracket, then exact
mean=log5 at the unique root. This agrees with TILT-PROOF-REVIEW.md. No
proof-kernel/all-real computational acceptance is implied by the Boolean.

## Binding, controls and actual retained JSON

Each engine literally pins hashes of CASES, SCHEMA and SOURCE-PINS. Those
metadata bind the exact source head, literal law, alpha endpoints and target.
Both verify source bytes and require FILES to cover exactly eight unique
allowed paths: the two engines, three metadata objects and three inert inputs.
FILES itself is installed/sealed by the coordinator after code is ready;
first-run admission still needs that exact actual manifest. No source or peer
calculator import appears. The source declaration is also matched textually;
it supplements exact source authentication, rather than proving the law's
historical derivation or physical source caller.

The rank2 multiplicity+1 control changes a real law and reruns endpoint
arithmetic; it must fail the intended sign gate. Primary recomputes logs too;
oracle reuses valid same-rank log bounds, then recomputes weights/means/signs.
The swapped-endpoint primary control reaches the actual left-sign gate; oracle
rejects at its explicit endpoint-order guard before numerical evaluation.
The singleton and zero-weight controls test their named law guards. These
are accurately distinguished in the algorithm notes. Duplicate-key, floating
token and Boolean-integer controls test the actual decoder/type functions.
Nonfinite-token rejection is implemented via parse_constant, but is not an
eighth distinct built-in executed control. No actual control pass is claimed
before execution; each helper accepts only its intended ValueError diagnostic.

Both parsers reject duplicate keys, float/nonfinite tokens and Boolean proof
integers, require reduced rational pairs with positive denominators, and check
closed certificate/endpoint/control/conclusion key sets. There are no assert-
dependent acceptance gates. Oracle has lighter standalone provenance/endpoint
validation than primary; default acceptance nevertheless compares the entire
canonical actual packet with complete fresh regeneration under frozen metadata,
which binds every such value. Canonical JSON comparison also avoids Python's
Boolean/integer equality accident. A retained false field cannot pass merely
by preserving a summary flag or changing its claimed digest. Default mode
requires the actual own retained certificate; only explicit --emit writes one.
Neither code imports its peer. Matching numerical enclosures between different
methods is not assumed; each must independently bind its own complete artifact.

## Remaining evidence and scope

The coordinator must retain first code/input seals, first stdout/stderr and
full actual artifacts, and demonstrate strict signs/controls, normal/optimized
actual-certificate comparison, independent packet interval compatibility,
registered/cold transport checks and later exact-head publication evidence.
Any first failure must remain rather than being relabeled as an initial pass.
This static review supplies none of those execution outcomes.

No new paid-law derivation, full flow/local-limit theorem, selected analytic
recovery, native/physical/compiler/precision/tape admission, all-five result,
frontier/kappa change or merge follows. Credit stays with alephnan/PR6713,
the inherited direct-flow/tilt lineage, S5/PR6723 and classical calculus,
atanh/Taylor, Simpson and binomial inequalities. Source-aware, separately
assigned OpenAI Codex review; no human or proof-kernel acceptance. Apache-2.0.
