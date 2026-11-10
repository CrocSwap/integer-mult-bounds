# Sharp adaptive drift from one reused stochastic rounding seed

This contribution was produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

Claim type: scoped probability proof with exact finite corroboration.
For every positive integer denominator m, two adjacent-grid stochastic rounding
calls that reuse one uniform seed have exact worst-case absolute expected
accumulated local rounding error

```
beta(m) = floor(m^2/4) / m^2.
```

The second integer numerator may depend on the first rounded output. The caller
observes the seed only through that output. Independent private randomness is
allowed. The bound is 1/4 for every even m, and (m^2-1)/(4m^2) for odd m.
For grid spacing h, multiply the bound by h. This is an expectation bound;
it is not a pathwise bound on the sum of errors or a concentration theorem.

A two-shear word attains the positive bound and can be copied and reversed
while restoring every arbitrary dirty working value and the seed. Consequently,
pathwise restoration alone cannot justify zero-mean forward error under reuse.
Increasing a dyadic seed's bit count does not reduce this worst-case bias in
units of the output grid.

## Exact contract and proof

For n in Z, m >= 1 and U uniform on {0,...,m-1}, use Euclidean division
n = m q + r with 0 <= r < m. Define

```
S(n,m,U) = q + 1[U < r].
```

The first numerator n1 is independent of U. The second numerator n2 may be any
integer-valued function of S(n1,m,U) and private randomness independent of U.
No other seed-dependent information is available before the second call.
Let e_i = S(n_i,m,U) - n_i/m. Then

```
-beta(m) <= E[e_1 + e_2] <= beta(m),
```

and both endpoints are attainable. Integer quotients cancel from each e_i,
including negative numerators. Condition on n1 and any independent randomness;
write its remainder as r. The first output reveals only B = 1[U < r], and
E[e_1] = 0. For 0 < r < m, the two posterior seed distributions are uniform
on [0,r-1] and [r,m-1]. If s is the second numerator's remainder, its
conditional expected error is respectively

```
f_1(s) = min(s,r)/r - s/m,
f_0(s) = max(s-r,0)/(m-r) - s/m.
```

These formulas hold at all integer s in [0,m-1]. On the lower interval,
0 <= f_1(s) <= 1-r/m, with maximum at s=r and minimum at s=0.
On the upper interval, -r/m <= f_0(s) <= 0, with minimum at s=r and
maximum at s=0. Their piecewise slopes prove these extrema directly.
The branch probabilities are r/m and (m-r)/m. Thus every adaptive policy has

```
-r(m-r)/m^2 <= E[e_2] <= r(m-r)/m^2.
```

For the positive endpoint choose second remainder s=r when B=1 and s=0
when B=0. Interchanging those choices attains the negative endpoint.
For r=0 the first output reveals no seed information and both errors have
zero expectation. The same is true for m=1. Finally,
r(m-r) = m^2/4 - (r-m/2)^2 has maximum floor(m^2/4), attained at
r=floor(m/2). Averaging over independent private randomness preserves the
inequality and cannot improve the optimum. This proves the uniform theorem.

If the second call instead uses an independent uniform seed V, then
E[e_2 | first output, private randomness] = 0 for every policy. If both
numerators are fixed in advance, reusing U also preserves zero expected total
error. Adaptation and reuse together cause the quantified defect.

## Attaining word and dirty restoration

Set r=floor(m/2) and a=r/m. Begin with x=1, y=z=0 and execute

```
y += S(r*x,m,U)
z += S(r*y,m,U)
```

After the first call y=B. With the same U in the second call, z=B as well.
The exact unrounded two-shear word would give z=a^2. Therefore

```
E[z] - a^2 = a - a^2 = beta(m).
```

The bit B has a correct unbiased first marginal. Treating the second use of U
as fresh would predict E[z]=a^2 and miss the entire drift.

For arbitrary dirty x,y,z and a disjoint output accumulator w, retain the
computed z by w += z, then undo the second shear by subtracting the same
S(r*y,m,U), followed by undoing the first shear. At each inverse step its
source is still available. The endpoint restores x,y,z and U exactly and
retains the computed value in w. This uses the reversible-shear mechanism of
zxv's PR6066; it does not claim that mechanism as new. This is a logical
integer-grid protocol. No reversible bit circuit or complete physical bill
is supplied.

## New step and predecessor credit

[zxv's PR6066](https://github.com/CrocSwap/integer-mult-bounds/pull/6066),
[retained README](../reversible-stochastic-shears/README.md), already states
that restored random tape can be correlated with copied output. Its verifier
already gives the m=2 two-shear example. That example, the warning and the
inverse-shear ABI are predecessor work, not an audit deliverable here.
The new step is the sharp optimization over every two-call adaptive policy
for every denominator, with matching positive and negative policies.
Nick Petalas's PR6026 supplies the fresh-forward P104 stochastic-prefix context.
Conditional probability, threshold rounding and compute/uncompute are classical.
Global literature priority is unclaimed.

The current revision-8 priorities require precision and tape obligations to
survive the complete caller. This side result prices one proposed randomness
reuse premise. The card's supplier-admission audit is changed to an original
quantified boundary theorem. It does not audit a predecessor, install reuse
in a P104 caller, or claim that any published fresh-seed guarantee is false.
Source pins retain the exact predecessor context as provenance; the verifier
imports no predecessor code and needs no external scientific inputs.

## Reproduction and evidence

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/reused-seed-adaptive-drift/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/reused-seed-adaptive-drift/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/reused-seed-adaptive-drift
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/reused-seed-adaptive-drift --check-source-history
```

On other machines replace the interpreter path with CPython 3.12.
The direct verifier also works from a Git-free copy of this package. It writes
no files and prints `RESULT` JSON with package SHA256 hashes, followed by
`PASS_REUSED_SEED_ADAPTIVE_DRIFT`. The receipt is generated by that execution.
No result receipt was hand-authored.

The exhaustive oracle literally executes every seed for every policy
(r,s_0,s_1) in {0,...,m-1}^3, for every 1 <= m <= 24. It checks all
90,000 policies and 1,763,020 seed executions, including both attaining extrema.
This enumeration does not use the posterior formulas to evaluate a policy.
Separate controls enumerate 1,296 fresh-seed adaptive policies and 61,776 seed
pairs through m=8, and 204 fixed-input reused-seed policies. Signed translation
checks cover 21,420 tuples. The attaining word is checked at every denominator
through 64 and every seed in those domains. The 3,645 dirty copy/reverse
fixtures use x,y,z,w in {-2,0,3}, every m from 1 through 9 and every seed. Eight rejection
controls include invalid domains, the false zero-bias implication, a false
1/8 upper bound, and the false equality beta(m)=1/4 at odd m. Checks remain
active under optimized Python.

Uniformity rests on the written proof. The enumeration is bounded corroboration,
not an exhaustive check of all denominators or physical callers. Functions are
below 60 lines, all loops have fixed finite fixture bounds, and no recursion,
dynamic code or external process is used. Python's managed allocation is a
Power-of-Ten deviation; live arithmetic state is bounded by these fixture sizes.
Warnings are errors in both registered commands. No static type checker is
required or added.

## Limitations and unrun obligations

The caller sees only the first rounding result before choosing the second
numerator. Direct seed inspection, more forward calls, a changed random law,
nonadjacent rounding, data-dependent stopping and additional observations are
outside the theorem. The result is a scalar local-error expectation bound.
It supplies no full-word bias, variance, tail probability or native error budget.

The dirty inverse is logical integer arithmetic. Finite guard widths, bit-level
reversibility, random-tape preparation/access, temporary cleanup, storage, stock,
native MOVE and the complete recursive/outer bill remain unproved and unpriced.
No supplier admission, new kappa, selected-frontier change, selected cold replay,
Lean, Docker or complete multiplication theorem is claimed.

## Open next questions

- What is the sharp drift after three or more calls with one reused seed?
  It would quantify a longer reuse window. Begin with a dynamic program on
  posterior intervals and a three-call attaining policy. A uniform multistep
  optimization proof is missing; this package stops at two calls.
- Can one actual caller prove that a restored seed remains conditionally
  uniform at its next forward use? That would justify a specific reuse rather
  than a generic independence assumption. Start with its exact observation
  sigma-algebra and numerator dependency. No such source-bound caller or
  complete physical invoice is supplied here.
