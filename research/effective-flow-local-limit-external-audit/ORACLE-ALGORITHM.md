# Exact rectangle/power oracle for the finite-law hypotheses

This is the independent numerical method for the declared nine-atom law and
every alpha in the fixed CASES.json bracket. It does not locate or validate
the tilt root and does not assume that the expectation equals log5. The
actual expectation is enclosed and used to center both moments and support.
The source's local-limit proof and all-n/flow/native conclusions remain outside
this numerical certificate.

The implementation uses standard-library integers and normalized Fraction
objects, explicit exceptions and no floating arithmetic or assertions. It
does not read or import the source numerical checkers or the primary checker.
The primary's raw bytes are read only to authenticate the root FILES manifest.
The fixed algorithm parameters are N=M=4096 and Q=10^12; no post-first tuning
is part of this method statement.

## Logarithms by decreasing integrals

For an integer r>1 put h=(r-1)/N. Since 1/t decreases on[1,r],

    sum(k=1..N) h/(1+k*h) <= log(r)
       <= sum(k=0..N-1) h/(1+k*h).

Each summand is exactly `(r-1)/(N+k*(r-1))`. The lower sum rounds each
summand downward to an integer multiple of1/Q; the upper sum rounds each
upward. Summing these integer numerators preserves both inequalities and
avoids products of thousands of distinct denominators. For r=1 both bounds
are exactly zero. Every required rank is treated directly rather than by
prime factorization or an atanh series.

## Exponentials by power bounds

For0<=x<M, log(1+x/M)<=x/M and -log(1-x/M)>=x/M imply

    (1+x/M)^M <= exp(x) <= (1-x/M)^(-M).

If x lies in[l,u], monotonicity permits l in the lower expression and u
in the upper. The lower initial base1+l/M is rounded downward to the Q
grid; the upper base1/(1-u/M) is rounded upward. Both are nonnegative.
Twelve repeated squarings raise them to M=2^12. After each squaring, integer
floor division gives the lower grid value and integer ceiling division gives
the upper grid value. Monotonicity of squaring on nonnegative values proves
the enclosure inductively. The engine explicitly checks0<=l<=u<4<M.
This is different from the primary positive Taylor-series method.

Because the alpha bracket and log intervals are nonnegative,
alpha*log(r) lies between alpha_lower*log_lower(r) and
alpha_upper*log_upper(r), simultaneously for every alpha in the bracket.
The resulting interval encloses r^alpha without choosing one numerical alpha.

## Normalization and actual centered moments

Multiplying each exponential interval by its nonnegative integer count gives
weight intervals[l_r,u_r]. A positive lower normalizer is required. With
A_lower=sum(l_r) and A_upper=sum(u_r), each actual probability satisfies

    l_r/A_upper <= p_r <= min(1,u_r/A_lower).

All nine rank keys remain in the certificate, including zero-count atoms in
semantic controls. Summing p_lower*log_lower and p_upper*log_upper gives an
interval[m_lower,m_upper] containing the actual mean. Correlations between
alpha, weights and logs are not assumed independent; ignoring them only widens
the enclosing box.

For each atom, the centered value lies in
`[log_lower-m_upper,log_upper-m_lower]`. Its absolute-value lower bound is
zero when this interval contains zero, otherwise the smaller absolute endpoint;
its upper bound is the larger absolute endpoint. Multiplying squared-distance
lower/upper bounds by the corresponding probability lower/upper bounds and
summing gives the variance enclosure. In particular, the code uses centered
square sums and never subtracts mean squared from a raw second moment.

The third absolute centered moment is bounded above by the sum of
`p_upper*distance_upper^3`. Maximum centered support is bounded by the largest
distance upper bound among positive-count atoms. These estimates are valid
for every actual mean and probability vector inside the enclosing intervals.
The positive fixture is accepted only if all six H inequalities are certified
by exact rational comparisons.

## Controls and retained data

The four semantic controls invoke this same numeric engine on changed laws:

- Set the rank3 count to zero; certify its probability is exactly zero and
  the atom_log3 predicate is false.
- Set alpha to[0,0]; require the computed variance upper bound to be below2,
  as well as the variance_2_3 predicate being false.
- Set the rank1 count to zero; certify its probability is exactly zero and
  atom_0 is false.
- Set all counts to zero; require the engine's specific normalization error.

Four parser controls separately require rejection of duplicate JSON keys,
numeric floats, a nonfinite JSON constant and a Boolean supplied as a fraction.
Every intended outcome is recorded; the two zero-atom witnesses and alpha-zero
variance enclosure are retained in the complete method-specific certificate.
No catch-all exception is used to count an unrelated failure as a successful
normalization control.

Before any science, FILES.json must authenticate exactly both code files,
CASES/SCHEMA/SOURCE-PINS and six inert source copies. The three immutable
metadata hashes are also pinned in the oracle. Source text is never executed.
All JSON uses duplicate-key, float and nonfinite rejection; rational fields
require their exact canonical Fraction strings, excluding Boolean fractions.

`--emit PATH` writes a complete certificate only after the positive H checks
and all controls pass. Ordinary replay instead reads the retained ORACLE.json,
or the explicit `--certificate PATH`, and compares the complete canonical
JSON representation to regeneration. Method, ranges, witnesses, provenance
and every nested field participate in that equality; accepting only the six
Boolean flags would be insufficient. The primary and oracle intentionally
produce different valid enclosures and are not expected to have equal full
certificate hashes.

This note describes the fixed algorithm before execution; actual firsts,
failures, timings, normal/optimized agreement and tampering outcomes must be
retained by the coordinator. A proposed first command is isolated Python3.12
with `-I -B oracle.py --emit <first-output>/ORACLE.json`, after FILES and both
code seals exist. Expected work is roughly8*8192 small-integer rectangle
divisions plus five nine-atom engines, and twelve squarings per exponential;
expected resources are below10 seconds and64MiB, subject to actual receipts.

The literal historical law, bracket and local-limit application remain
alephnan's and the credited predecessor packages' work. Decreasing rectangles,
elementary logarithm inequalities, outward rounding and moment enclosure are
classical. This separately implemented oracle and note use substantial
OpenAI Codex assistance. No independent human, proof-kernel, full local-limit,
flow, multiplier or selected-frontier acceptance is claimed. Apache-2.0.
