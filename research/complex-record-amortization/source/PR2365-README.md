# Uniform parameter domain for PR2298

**Result:** the scalar parameter conditions stated below hold for every integer
`b >= 2^524288` and every integer `ceil(b/2) <= L <= b`.
This is a written arithmetic lemma with exact endpoint and induction certificates.
It adds no multiplication exponent and does not validate the full callee proofs.

Jose Manuel's [PR2298](https://github.com/CrocSwap/integer-mult-bounds/pull/2298),
at `8507498d363735ced0b0a3f02d5ecf80ed3e3805`, gives qualitative eventual
arguments for its changed dimension and tests five compressed input sizes.
This audit adds one explicit sufficient cutoff, a proof across all floor and
ceiling discontinuities, source-formula checks, and rejection controls. The
cutoff is deliberately large. No optimal or practical cutoff is claimed.

The exact audited [proof](source/PR2298-PROOF.md) and
[parameter checker](source/PR2298-checks.py) are retained as read-only inputs.
[SOURCES.json](SOURCES.json) records their commit, Git blobs and SHA-256 hashes.
The checker reads their bytes and syntax; it imports no predecessor code.

## Statement

Let `bitlen(x) = floor(log2(x)) + 1` for positive integers. Set

```text
p = 6b, d = floor(p^(1/40)), K = floor(d^(1/500)), ell = ceil(L/d),
G = 4 bitlen(p) + 6, H = dG, q0 = 5284 bitlen(d),
Q0 = q0 + ceil(2H/K) + ceil(H/K),
alpha = ceil((12 d^2 b)^(1/4)), gamma = 2d alpha^2.
```

For every `b,L` in the stated domain:

1. `0 <= d ell-L < d`, `p <= 12d ell <= 4p`, and `ell < p`.
2. `1 <= K <= ell-1`, `K > 16G`, and `K > bitlen(p)`.
3. `q0 < d/16`, `Q0 < d/4+2 < d-1`, and `2^210000 d < p/2`.
4. `ell-1 > 16d` and `ell-1 > 3+2 bitlen(d)+bitlen(ell)`.
5. `2 <= alpha`, `alpha^2 < p`, and `gamma < b/4`.
6. `448b 2^(-b+gamma) < 1/2`.

Items 2 and 3 prove the recorded chunk, reserve and guard conditions. Item 4
proves the two exact prime-room inequalities used by the predecessor. It does
not reprove the published prime-interval theorem. Item 6 bounds the numerical
expression in PR2298 section 6; it does not prove that a full implementation
has that error.

## Proof

Put `S=524288`, `s=floor(log2 p)`, `t=floor(s/40)` and
`u=floor(s/20000)`. We have `s>=S`, `t>=13107` and `u>=26`.
Integer root inequalities give

```text
2^t <= d < 2^(t+1), bitlen(d)=t+1,
2^u <= K < 2^(u+1), G=4s+10.
```

The second line follows from `floor(t/500)=floor(s/20000)`.
These inequalities include values immediately below perfect powers.

### Three exponential comparisons

For nonnegative slope `A`, the implication

```text
2^j > Aj+B  implies  2^(j+1) > A(j+1)+B
```

holds whenever `Aj+B-A >= 0`. This last expression is nondecreasing in `j`.
Thus one base comparison and one nonnegative affine difference prove the
entire integer tail. The verifier certifies these three instances:

| Variable and range | Right side strictly below its power of two |
| --- | --- |
| `u>=26` | `16(80000(u+1)+6)` |
| `t>=13107` | `16*5284(t+1)` |
| `t>=13107` | `42t+44` |

For example, the first base is `2^26 > 34560096`. Its induction difference
at 26 is `33280096`. The other base right sides are `1108202752` and
`550538`, each below `2^13107`. All comparisons use integers.

Since `s <= 20000(u+1)-1`, we have `G <= 80000(u+1)+6`.
The first comparison gives `K>16G`. The second gives
`q0=5284(t+1)<2^t/16<=d/16`. In particular `K>bitlen(p)`.
Both ceilings remain charged:

```text
Q0 < q0 + 3dG/K + 2 < d/4+2 < d-1.
```

The final strict inequality holds because `d>=2^13107>4`.

### Record lengths and precision guard

The following linear bounds hold at `s=S` and increase thereafter:

```text
s-t >= 39s/40 >= 210002,
s-2t >= 19s/20 >= 10,
s-t-u >= 19499s/20000 > 6.
```

The first also gives `s-t>=4`. Hence
`d<2^(t+1)<=2^(s-3)<=p/8<b`. The allowed interval for L then gives

```text
p/(12d) <= ell <= b/d+1 <= p/(3d).
```

The definition of the ceiling proves `0<=d ell-L<d`.
It also gives `ell<p`. Thus `r=2^ell<2^p` without constructing r.
Since `12dK<2^(t+u+6)<2^s<=p`, we have `ell>K`.
Both are integers, so `K<=ell-1`.
Finally, `t+1+210000<=s-1` gives
`2^210000 d<2^(s-1)<=p/2`.

### Prime-room inequalities

The second linear bound gives `p>256d^2`.
Since `256d^2>192d^2+12d` for `d>=1`,

```text
ell-1 >= p/(12d)-1 > 16d.
```

Also `ell<=p/(3d)<2^s`, so `bitlen(ell)<=s`. Using the third exponential
comparison and `s<=40t+39` gives

```text
3+2 bitlen(d)+bitlen(ell) <= s+2t+5 <= 42t+44 < 2^t <= d.
```

The previous bound `ell-1>16d` therefore proves the second prime-room
inequality with a strict margin.

### Gaussian parameters and the recovery expression

Write `x=(12d^2b)^(1/4)>=1`. Since `alpha=ceil(x)<=2x`,

```text
gamma <= 8 sqrt(12) d^2 sqrt(b)
      < 28 d^2 sqrt(b)
      <= 28*6^(1/20) b^(11/20)
      < 32 b^(11/20) <= b/4.
```

Here `8 sqrt(12)<28`, and `6^(1/20)<8/7` follows from
`8^20>6*7^20`. The last inequality is equivalent to `b^9>=2^140`.
It holds because `b>=2^S` and `9S>=140`. Also `x>1`, so `alpha>=2`,
and `alpha^2=gamma/(2d)<b/(8d)<p`.

For integers `b>=16`, induction proves `b^4<=2^b`: equality holds at 16,
and `(1+1/b)^4 <= (17/16)^4 < 2`. Thus `log2 b<=b/4`.
For `b>=32`,

```text
log2(896b) < 10+b/4 < 3b/4.
```

Together with `gamma<b/4`, this proves item 6.

### The actual caller and growth conditions

For the actual caller, let `b=ceil(log2 n)` and let T be the least power
of two at least `4n/b`. Then

```text
b+1-log2 b < L=log2 T < b+3-log2 b.
```

The upper bound is at most b when `b>=8`. The lower bound exceeds `b/2`
when `b>=16`, using `log2 b<=b/4`. Thus every actual large input lies
in the interval quantified above. The result includes all such integers n.
It is not restricted to the predecessor's samples `n=2^b`.

The same inequalities give the required limiting relations. In the stated
tail, `d>=p^(1/40)/2` and `K>=d^(1/500)/2`, so
`K>=p^(1/20000)/4`. Therefore `K/log p` tends to infinity.
Moreover,

```text
K/ell <= 12p^(-19499/20000) -> 0,
2^210000 d/p <= 2^210000 p^(-39/40) -> 0,
ell/log2 p >= p^(39/40)/(12 log2 p) -> infinity.
```

The last relation makes r exceed each fixed power of p eventually.
These are limits, not claims that one finite cutoff handles every possible
polynomial degree at once.

## Executable evidence and rejection controls

The universal statement uses the proof and three induction certificates.
The finite fixtures test the implementation of the exact boundary arithmetic.
They do not replace that proof. No floating-point arithmetic is used.

Three compressed fixtures use `p=2^524320+2`, `p=2^540000-4` and
`p=2^540000+2`. Each is divisible by six and lies above the cutoff.
The last pair crosses both root boundaries: d changes from `2^13500-1`
to `2^13500`, and K changes from `2^27-1` to `2^27`.
Each fixture checks five admissible L values, including both ends of the
interval and a ceiling discontinuity. The checker uses integers below 600,000
bits; it never allocates n, T, r or their arrays.

Nine controls reject a cutoff that cannot pay the guard, an enlarged guard,
ceiling-based lower bounds for d and K, an unrounded reserve, a false stronger
chunk factor and its failed certificate, a changed source exponent, and source
byte corruption. At `p=2^524320+2`, replacing the two reserve ceilings by
`floor(3H/K)` omits exactly one axis. The same fixture has
`K=77947531 < 64G=134226560`, so the stronger factor 64 is actually false.
These are false variants, not counterexamples to PR2298's original formulas.

The arithmetic uses separately implemented bisection for the 500th root and
two integer square roots for the fourth root. Exact power inequalities certify
each root. Ten syntax checks bind the formulas to the hashed source. Python
assertions are not used, so optimized execution retains every check.

## Reproduce and limits

```sh
python3.12 scripts/research_package.py --package research/outer2298-uniform-domain
python3.12 -O -B research/outer2298-uniform-domain/verify.py
```

Expected final line:

```text
PASS_OUTER2298_UNIFORM_DOMAIN cutoff_log2_b=524288 fixtures=3 controls=9 no_new_kappa
```

[RESULT.json](RESULT.json) records the exact certificate, boundary cases and
controls. [TASK.json](TASK.json) records task selection and overlap coverage.
This package uses the standard library and includes its two proof-relevant
source snapshots. Its generic replay has no inputs outside the package.

The result certifies only the stated scalar envelope. It does not prove that
Q0 counts every physical reserve, that the dimension change covers every
callee assumption, or that the claimed tape and Gaussian implementations
satisfy their contracts. The complete supplier, analytic, error-propagation
and tape proofs remain separate. No selected source or frontier is changed.
This is an author-checked proof, not a proof-assistant formalization or an
independent human review.

## Open next questions

Does PR2287 use another dimension-dependent condition outside this envelope?
That question matters because the caller must meet the full callee contract.
The first step is to trace each use of dimension in the pinned PR2287 proof
and its dependencies. This requires independent review of those constructions.
The structured question is in [TASK.json](TASK.json).

## Credit

Jose Manuel (`jmbarrancoml`) supplied PR2298's parameter family, reserve
expression, qualitative arguments and finite tests. Its proof retains credit
for the PR2234/2287 callees, OpenAI's frozen outer proof, Douglas Colkitt's
routing, Philipp's layout checker, and the Harvey–van der Hoeven algorithms.
Those underlying results are not new work in this package. The two snapshots
are retained without alteration under the repository's Apache-2.0 license.

Prepared by Jerry Lin (`jerrylin-23`) with substantial OpenAI Codex assistance
in source review, mathematics, implementation, verification and writing.
New files are Apache-2.0. Coordination is in
[Discussion2291](https://github.com/CrocSwap/integer-mult-bounds/discussions/2291#discussioncomment-18941810).
