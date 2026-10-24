# Fourfold reduction of the many-axis prime-supply cutoff

This contribution was produced by Nick Petalas. Apache-2.0.

**Claim type: scoped mathematical proof with exact endpoint certificates.**
ToikY's [#4029](https://github.com/CrocSwap/integer-mult-bounds/pull/4029)
prime-supply theorem holds already for **`ell >= 2^30 = 1073741824`**, in
place of `ell >= 2^32`. The dimension range `2 <= d <= ell^334`, both target
scales, the prime band and separate halo premise stay the same. This is a new
endpoint argument using the predecessor's analytic reduction, not an audit.

## Statement and proof

Let `ell >= 2^30`, `D=d-1 >= 1` be integers and `d <= ell^334`. For either
`t=2^(ell-1)` or `t=2^ell`, the band

```text
I(t,d) = (a,b] = (t*(1-1/(3d)), t*(1-1/(4d))]
```

contains at least `D` primes. Distinct selections for any `D` axes at these
scales satisfy the same source-ratio and product conclusions as #4029.
Retain its separate premise `target_halo+2w <= 2^(ell-3)` for the period guard.
The guard and separate oddness gate retain unpaidmoon's
[#4142](https://github.com/CrocSwap/integer-mult-bounds/pull/4142) credit.

All logarithms are natural. The imported analytic theorem is Fiori, Kadiri
and Swidinsky's [Corollary 22, arXiv:2206.12557v2](https://arxiv.org/pdf/2206.12557v2):

```text
|pi(x)-Li(x)| <= 9.2211*x*sqrt(log(x))*exp(-.8476*sqrt(log(x))), x >= 2.
```

Put `y=log(t)`. We cite #4029's resulting interval estimate as the starting
point, preserving its constants and mathematical credit:

```text
pi(b)-pi(a) >= t/(12*d*y) - 20*t*sqrt(y)*exp(-sqrt(y)/2).       (1)
```

The two endpoint errors use `sqrt(t)<=a<b<=t`, `9.2211<10` and
`.8476/sqrt(2)>1/2`; the main term uses `Li(b)-Li(a)>=(b-a)/log(t)`.
We do not rerun the predecessor's source or analytic checks. To make (1)
greater than `D`, it suffices to prove

```text
480*d*y^(3/2)*exp(-sqrt(y)/2) < 1,                            (2)
t > 24*d*D*y.                                               (3)
```

Indeed, (2) bounds the subtracted term by `t/(24*d*y)`, strictly, and (3)
then supplies the quota. For `ell>=2`, both scales obey `ell/4<=y<=ell`,
using `1/2<log(2)<1`. With `z=sqrt(ell)`, the left side of (2) is at most

```text
480*ell^(335.5)*exp(-sqrt(ell)/4) = 480*z^671*exp(-z/4).       (4)
```

The new step is an elementary sharper logarithm bound. The positive
exponential series gives `log(2)<7/10`, since its degree-three partial sum
at `7/10` is `12013/6000>2`. It also gives `log(480)<7` and `log(24)<5`,
already from degrees six and three at seven and five respectively.
At `ell0=2^30`, `z0=2^15`, the logarithm of (4) is strictly less than

```text
7 + 671*15*(7/10) - 2^13 = -2279/2 < 0.                    (5)
```

The derivative of `log(480)+671*log(z)-z/4` is `671/z-1/4`.
It is negative for every `z>=z0`, because `32768>4*671=2684`.
This proves (2) throughout the new domain, without finite extrapolation.

For (3), `24*d*D*y<=24*ell^669` and `t>=exp(ell/4)`. At the new endpoint,

```text
ell0/4 - log(24) - 669*log(ell0)
  > 2^28 - 5 - 669*30*(7/10) = 268421402 > 0.               (6)
```

The derivative of `ell/4-log(24)-669*log(ell)` is `1/4-669/ell`.
It is positive for every `ell>=ell0`, since `ell0>4*669=2676`.
Thus (3) holds everywhere in the new domain. Equations (1)-(3) prove the
prime quota. QED.

The two bands are disjoint, so increasing prime lists can be interleaved in
original target order without repetition. Their lower endpoints exceed two,
so every selected prime is odd. The inherited band argument gives the strict
source guards and `S/T>(1-1/(3d))^D>2/3`, hence `T/S<3/2`.
The separate halo bound gives `s>(5/6)*2^(ell-1)>2*(target_halo+2w)`.
No new source program or setup-cost improvement is inferred.

## Exact evidence and reproduction

[verify.py](verify.py) checks (5), (6), both derivative signs and the
positive-series logarithm bounds by rational arithmetic. A second endpoint
calculation uses `e>8/3` and checks the integer inequality

```text
8^8192 > 480 * 2^10065 * 3^8192.
```

The quota endpoint also follows from `e>2` and an exponent comparison, with
no giant target integer. These are two calculations of the new endpoint,
not independent proofs of the imported analytic theorem. Twelve rejecting
controls include an unsupported cutoff `2^28`, a false logarithm bound,
altered margins, missing derivative gaps and invalid replay parameters.
A rejected certificate at `2^28` does not prove prime supply fails there.

From the repository root, using CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/many-axis-prime-cutoff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/many-axis-prime-cutoff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/many-axis-prime-cutoff
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/many-axis-prime-cutoff --check-source-history
```

Replace that interpreter path with another CPython 3.12 installation when
needed. The marker is `PASS_MANY_AXIS_PRIME_CUTOFF`. The verifier emits
computed values and hashes of all five package files, writes nothing, and
needs no Git or network. No handwritten receipt is supplied. The last command
requires a publication commit and Git history.

The verifier has bounded loops, no recursion and functions under 60 lines.
Its control helper has a fixed set of local indirect-call targets. Python's
dynamic allocation is a managed-runtime deviation, bounded by powers 2..32
and series degree at most six. Integer-power operands stay below 50,000 bits.
Explicit checks remain active under optimization; both registered commands
make warnings errors. No external analyzer is required at replay.

## Scope, provenance and credit

The scientific base is `a5df48c55ea806d7952b65acc9c76d878ff09b13`, priority
revision 7. TASK.json records the changed `uniform-transfer-audit` scope.
SOURCES.json pins the predecessor statement, reduction and guard discussion
as historical provenance. No predecessor executable or live runtime input is
imported. Selected metadata orientation passed as
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY`; it is not a supplier replay.
Live PRs/Discussions, merged searches, whole-main README searches and the
overlap helper found no matching cutoff reduction within their coverage.
Sparse local notes, arbitrary unseen diffs and unpublished work remain limits.

Credit ToikY #4029 for the source-bound theorem, band, analytic reduction,
constructive algorithm and setup bill; unpaidmoon #4142 for the guard/oddness
separation and cutoff question; Fiori, Kadiri and Swidinsky for their theorem;
Jose Manuel #3935 for the tensor interface; Tekalign #4024 for CRT conversion;
Cinna Davis, Chafik Boukhalfa #1786 and Josie Elliston for prior selector work;
and Harvey and van der Hoeven, source08 and Agarwal and Cooley for the
retained number-theoretic, trial-division and CRT lineage. The new result
is only the smaller sufficient cutoff proved above.

The cutoff remains enormous and is not claimed least. No giant prime search,
literal encoded producer, physical caller, native supplier, new kappa or
selected-frontier change is supplied. Halo/growth constants, numerical tensor
and recovery, precision/tape, stock and other supplier obligations remain.
Independent human and formal proof-kernel review are unclaimed. Selected cold
replay, predecessor scientific suites, Lean and Docker were not run.

## Open next questions

1. Can the original endpoint errors give a smaller sufficient cutoff than
   the weakened bound (4)? This would enlarge the admitted parameter domain.
   Start with rational bounds on both endpoint logarithms and a new
   monotonicity certificate. No further reduction or least cutoff is proved.
2. Can an encoded prime producer meet the actual source-tape and head-return
   contract? Start with #4142's loading/oddness boundary and #4029's written
   trial-division algorithm. Literal arithmetic, complete execution and its
   physical bill remain absent. The family decision is to stop at this
   parameter improvement.
