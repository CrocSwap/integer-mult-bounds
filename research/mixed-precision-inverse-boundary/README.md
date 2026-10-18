# Finer inverse precision can break exact dirty cancellation

The same source and coefficients do not suffice for exact inverse cancellation
when a rounded leaf's precision changes. In the actual pinned PR628 one-entry
cyclic inverse leaf, forward precision4 sends target0 to -5/16; inverse
precision5 leaves **1/32** instead of zero. Both calls pass their explicit
admission checks and restore the source. Same-grid forward/inverse calls cancel.

This is a counterexample to a proposed precision-refinement relaxation, not a
bug in the retained fixed-grid caller. A separate exact criterion below decides
when changing precision is safe for rational rounded-linear shears on an
unrestricted input grid. It does not misidentify the internally rounded PR628
leaf as one rounded linear multiplication.

## Quantified grid criterion

Let Q_w(t)=2^-w floor(2^w t+1/2), applied componentwise, matching the pinned
rounding rule. Let A be any rational r-by-s matrix and 0<=p<=w<v be integers.
For every x in (2^-p Z)^s, the two deterministic increments agree,

    Q_w(Ax) = Q_v(Ax),

**if and only if every entry of 2^(w-p) A is an integer.** Consequently the
signed shears y+=Q_w(Ax) and y-=Q_v(Ax) cancel for every such x and arbitrary
target dirt exactly under this condition. The addition/subtraction itself is
exact; the target is not rounded after the update.

Sufficiency: the integrality condition places every exact Ax on the coarse
grid, which is contained in the fine grid; both roundings are the identity.

Necessity: isolate one nonintegral scaled coefficient q=a*2^(w-p)=u/d in
lowest terms, d>=2. Choose k in {0,...,d-1} with u k congruent to floor(d/2)
mod d. This exists because gcd(u,d)=1. The fractional part of qk is between
1/3 and1/2 inclusive (1/2 for d=2). Its distance from the closest integer is
at least1/3. Fine rounding in coarse-grid units has error at most1/4 because
v-w>=1. It therefore cannot equal the coarse rounded integer. Put x_j=k/2^p
in this one column and all other inputs zero to obtain a concrete matrix
counterexample. This proves the result for arbitrary dimensions and signs.

The modular construction bounds the witness multiplier by d-1. A bounded
input box may contain no such witness, and equality at zero is uninformative.
No criterion for irrational entries, interval-only coefficients, nonlinear
increments, saturating targets or different rounding models is claimed.

## Actual source-bound leaf counterexample

Use the frozen `dirty-prefix-precision/vendor/pr628/dirty.py` `compose` with
one outside factor b=1/4, scale1; phases=[1]; beta=1/2; direction+1;
source=[1], target=[0], and no scratch. At bits4 the returned target is -5/16.
The same invocation with sign-1 and bits5 computes a different deterministic
increment and returns target1/32. Initial/coarse outputs lie on the finer
grid, the phase data are immutable and separate, and source restoration holds.
Thus neither aliasing nor off-grid input explains the residual.

The ideal scalar operator in this length-one example is -1/3. The two actual
computed increments are -5/16 and -11/32. Their approximation errors are
1/48 and1/96, respectively: the inverse approximation is closer to the ideal
operator, yet exact cancellation is lost. Better approximation error is not
an inverse certificate.

The current retained caller in `dirty-prefix-precision/numeric.py` passes the
same `bits` to both orientations and explicitly checks exact restoration.
Its proof assumes the same deterministic signed increments. Those conditions
remain valid and no frozen source is modified. A compiler seeking per-call
precision must certify paired-increment equality on the reachable source
domain, or execute both orientations at a common admitted precision. A common
finer precision pays its actual arithmetic cost on both orientations.

## Evidence and reproduction

```sh
python -O -B research/mixed-precision-inverse-boundary/verify.py
python scripts/research_package.py --package research/mixed-precision-inverse-boundary
```

Python3.12+ standard library only. The checker constructs exact modular
counterexamples for coefficients numerator-31..31/denominator1..31, input
precision0..4, five coarse precision offsets and three positive refinement
offsets. Independent complete residue-period enumeration checks the criterion
without the modular witness algorithm. It also exhausts a625-member rational
2x2 matrix alphabet on its whole common residue period.

The actual pinned leaf is tested over33 source values, four finer precisions
and both directions. Each mixed-grid case has coarse/coarse and fine/fine
positive inverse controls. All computations use Fraction, no floating point.
An explicit zero-only smoke test passes despite an unsafe coefficient, while
the nonzero witness fails. [EXPECTED.json](EXPECTED.json) records exact counts
and the counterexample; [SOURCES.json](SOURCES.json) pins every imported source
file plus the current wrapper/proof by Git blob and SHA256.

This does not replay the selected supplier, provide a native arithmetic
compiler or prove the full multiplication theorem. The grid lemma applies to
rounded-linear shears; the PR628 leaf is an independently checked actual
counterexample to the broader precision-refinement inference. Prior fixed
word-precision work chooses shared execution precision and does not supply
this grid equality criterion. The863-PR/112-discussion snapshot search found
only unrelated precision-grid matches; cached offline limitations remain.

## Open next questions

Can a compiler certify unequal-precision inverse pairs on a bounded reachable
domain without enumerating every input? Start with a proposed pair of linear
rounded increments, apply the integral-grid criterion when applicable, then
bound reachable residue classes for nonintegral coefficients. A complete
reachable-domain proof and actual precision cost are required; local error
bounds alone do not authorize the replacement.

## Credit

woklerx with substantial OpenAI Codex assistance; Apache-2.0. Chafik Boukhalfa's
PR628 supplies the signed rounded cyclic inverse prototype, Gareth Davidson's
dirty-prefix-precision supplies the retained same-grid argument/caller, and
Ali Romman's PR621/source NOTICE retains the kernel lineage. No independent
human review, source theorem flaw, new supplier or kappa is claimed.
