# Sharp dimension scale of the heavy tensor-error envelope

This scoped proof replaces a linear sufficient dimension gate by the sharp
quadratic scale of the stated scalar error envelope. For fixed nonnegative
constants K,C, the largest admissible integer dimension satisfies

```text
g_max(p) ln(p) / p^2 -> 1/10.
```

At p=64 and K=C=0, the exact largest dimension is 98. Dimension 99 fails
the scalar inequality. A simpler integer-only gate already certifies g=68.
James Reed's #4695 sufficient gate certifies through g=10 there. The latter
is a consequence of its stated hypothesis, not a replay of its verifier.

This contribution is produced by Nick Petalas. Independent human and formal
proof-kernel review are unclaimed. New work is Apache-2.0.

## Scope and predecessor credit

The inherited envelope is

```text
M(p,g,K) = g (p^10)^(g-1) p^6 (1+p^4) exp(Kp-p^2)
         = g p^(10g) (1+p^-4) exp(Kp-p^2).
```

The question is exactly when M < 2^(-Cp), for integers p>=2, g>=1 and
nonnegative K,C. The proof allows real K,C; the finite verifier uses integers.
Credit James Reed's merged #4695 for g copies and the factor-1 sufficient
gate, #4693 for the single slice, #4526 for the heavy trailing slice and
#4524 for the unequal-tail factor. Jose Manuel's #4100 supplies the retained
Gaussian/HALO setting. Source READMEs are pinned in SOURCES.json. Their
results are premises and context; no predecessor computation is replayed.

The `uniform-transfer-audit` card changes to a new scalar dimension theorem.
This is a side result about a quantified error budget. It does not settle
an existing proof's correctness. It exposes slack in this one restriction
without removing other restrictions on g. In particular, the original
header, storage, geometry and physical-cost conditions may still require
`g log p=o(p)`. No caller at the larger dimension is constructed here.

## Proof

All logarithms in this section are natural. Put

```text
a = 10 ln p,
B = p^2 - (K+C ln 2)p - ln(1+p^-4),
f(x) = a x + ln x.
```

Taking the logarithm of M 2^(Cp) gives exactly f(g)-B. Since
f'(x)=a+1/x>0 for x>0, and f ranges from minus infinity to plus infinity,
there is a unique positive real x_* with f(x_*)=B. Consequently

```text
g_max = max(0, ceil(x_*)-1).
```

The strict ceiling accounts for the strict error inequality, including a
hypothetical integer root. If B<=a, no positive integer is admissible.
If B>a, let t=B/a>1. The following explicit bracket avoids special functions:

```text
t - (ln t)/a < x_* < t.
```

Indeed u=t-(ln t)/a is positive. For p>=2, a>1, and ln t<t for t>1.
Now f(t)=B+ln t>B, whereas
f(u)=B-ln t+ln u<B because 0<u<t. Monotonicity proves both inequalities.
These bounds also localize the integer maximum without an asymptotic claim.

For fixed K,C and p tending to infinity through integers,

```text
t = p^2/(10 ln p) - (K+C ln 2)p/(10 ln p)
    - ln(1+p^-4)/(10 ln p).
```

Thus t ln p/p^2 tends to 1/10 and ln t/a tends to 1/5. The bracket
shows x_*=t+O(1), and rounding changes the answer by at most one.
Therefore g_max ln p/p^2 tends to 1/10. More explicitly, for each
fixed alpha with 0<alpha<1/10, floor(alpha p^2/ln p) is admissible for
all sufficiently large p. For alpha>1/10, ceil(alpha p^2/ln p) fails
for all sufficiently large p. This proves sharpness for the envelope.
Failure of an upper envelope does not prove failure of an actual operator.

## A fully integer sufficient gate

Let L=ceil(log2 p). For nonnegative integer K,C, the condition

```text
10gL + 2L + 1 + (2K+C)p <= p^2
```

suffices for M<2^(-Cp). It implies g<p^2<=2^(2L). Also
1+p^-4<2, p^(10g)<=2^(10gL), exp(Kp)<=2^(2Kp), and
exp(-p^2)<2^(-p^2). The elementary bounds 2<e<4 imply the
last two comparisons. Their proofs follow from the positive series for e
and n!>=2^(n-1) for n>=1, with strictness for n>=3. Multiplying gives

```text
M 2^(Cp) < 2^[10gL+2L+1+(2K+C)p-p^2] <= 1.
```

This gate permits order p^2/log p and requires neither p>=64 nor a
separate linear parameter bound. At p=64, L=6, K=C=0, g=68 gives
4093<=4096. At g=69 this particular sufficient gate fails, without
implying failure of M. The exact boundary remains 98.

## Exact finite evidence

The standalone verifier uses only integer and Fraction arithmetic. For
1<=x<=2 and z=(x-1)/(x+1), it encloses ln x by

```text
S_N = 2 sum_(j=0)^(N-1) z^(2j+1)/(2j+1),
S_N <= ln x <= S_N + 2 z^(2N+1)/[(2N+1)(1-z^2)].
```

The positive logarithm series follows by integrating the geometric series
for 2/(1-z^2). Bounding every remaining denominator below by 2N+1 gives
the stated tail. Range reduction x=n/2^k puts integer logarithms in this
interval. All loops have explicit bounds; N=32 in boundary decisions.
A sign overlapping zero fails closed instead of guessing.

RESULT.json is a generated receipt with source hashes and rational sign
bounds. Its 207 boundary cases include 175 positive integer-gate checks.
Eleven neighboring signs also pass independent rational e-power comparisons.
Seventeen semantic controls cover invalid arguments, series contracts, log
identities, the integer gate and the p=64 sign margins. The verifier finds the last admissible integer by monotonic
binary search, certifies both neighboring signs, checks the integer gate,
and compares a bounded subset against literal rational powers enclosing e.
The independent power comparison does not use the logarithm implementation.
The p=64 signs are additionally separated by the rational margins
`log(M(64,98,0)) < -15` and `log(M(64,99,0)) > 25`.
No floats, predecessor scripts or scientific dependencies are imported.
The recorded finite counts are corroboration; the all-p conclusion rests
on the written proof above.

## Reproduce

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/heavy-tensor-dimension/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/heavy-tensor-dimension
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/heavy-tensor-dimension --check-source-history
```

The registered replay includes warning-strict ordinary and optimized runs.
A normal replay reads the receipt and writes nothing. Explicit
`--write-receipt PATH` generates a receipt and refuses an existing path.
CPython 3.12 is sufficient; there are no third-party requirements.

## Limitations

The tail formula, norm ceilings and any correspondence to the physical
Gaussian caller remain hypotheses. This proof does not cover operator
conditioning, headers, storage, movement, restoration, recursive admission
or the full multiplication theorem. It yields no new kappa and changes no
selected record. No Lean, Docker, selected-supplier cold replay or independent
human proof review was run.

Python's managed integer/Fraction allocation is a Power of Ten deviation.
The verifier limits p to 2^20, g to p^2+1, K,C to 2^20, series lengths to
64, and file sizes to 2 MiB. Loops and binary search depth are bounded.
These are verifier resource bounds, not restrictions on the written proof.

## Open next questions

1. Which actual caller restriction first blocks dimensions at the quadratic
   error scale? This matters because numerical error is only one obligation.
   Start by stating one caller's header-size and storage inequalities with
   its fixed parameters. The missing physical contract blocks a claimed
   algorithmic improvement; no larger implementation campaign is implied.
2. Can a concrete tensor caller use unequal per-axis norm ceilings to obtain
   a larger certified dimension than this worst-slice envelope permits?
   Start with its explicit ordered list of norm and error bounds. Those
   caller data are absent here; a formal change to the scalar envelope is
   insufficient by itself.
