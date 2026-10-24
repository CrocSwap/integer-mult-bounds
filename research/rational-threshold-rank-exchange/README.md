# Rank exchanges with an exact rational saving threshold

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped algebraic proof with exact finite corroboration. For every
rational threshold t in (0,1), there are two nonnegative integer child profiles
with equal child count and rank mass whose paid power moment improves exactly
for savings 0<a<t. The exchange reverses direction for t<a<1.

The first example is

```text
4 rank-1 + 3 rank-8  ->  6 rank-2 + 1 rank-16.
```

Both sides have seven children and rank mass 28. This exchange improves the
moment exactly when 0<a<1/2. Throughout 0.003<=a<=0.0031, 127 copies also
pay for one additional rank-one child. Thus the fully charged comparison is

```text
{1:508, 8:381}  ->  {1:1, 2:762, 16:127}.
```

Its new rank mass is one larger, while its raw power bill is strictly smaller
by at least 1646873/2000000000. This is a sufficient arithmetic allowance,
not an implemented exchange, a minimum batch size or a new kappa.

This answers Open next question 2 of Dugongue's
[#3868](https://github.com/CrocSwap/integer-mult-bounds/pull/3868), which asks
for a different stencil that helps on the intended saving interval without
improving every exponent. That predecessor supplies all-exponent binomial
stencils and a paid-overhead framework. Its computations are cited, not
replayed or re-verified here.

## Exact threshold theorem

For a finite integer profile H, write its raw power bill as

```text
B_H(a) = sum_r H_r r^(1-a).
```

Fix integers q>=2 and 1<=s<q. Expand the integer polynomial

```text
P_qs(x) = (x-1)(x-2)(x^q-2^s) = sum_j c_j x^j.
```

At rank 2^j, put max(-c_j,0) children in H_old and max(c_j,0)
children in H_new. Common zero coefficients are omitted. These are finite
nonnegative integer profiles, with maximum rank 2^(q+2).

Their counts agree because sum c_j=P_qs(1)=0. Their rank masses agree
because sum 2^j c_j=P_qs(2)=0. For every real 0<a<1, put x=2^(1-a).
Then 1<x<2 and, exactly,

```text
B_new(a)-B_old(a) = (x-1)(x-2)(x^q-2^s).
```

The first two factors have negative product. The last factor is positive
exactly when q(1-a)>s. Therefore

```text
B_new(a) < B_old(a)  iff  a < 1-s/q;
B_new(a) = B_old(a)  iff  a = 1-s/q;
B_new(a) > B_old(a)  iff  a > 1-s/q.
```

Every rational t in (0,1) is 1-s/q for such integers. This proves the
quantified threshold statement. It does not assert a smallest profile for
that threshold. The algebraic substitution and polynomial factorization are
elementary background; no literature-wide priority claim is made.

For q=2,s=1, expansion gives P(x)=x^4-3x^3+6x-4, hence the displayed
seven-child exchange. Its failure at larger a follows from the exact sign
law, rather than from numerical samples.

## Uniform credit and the fully paid example

Let a range over [3/1000,31/10000], and put x=2^(1-a). The integer
inequalities

```text
399^10000 < 2^9969 * 200^10000,
2^997 * 250^1000 < 499^1000
```

give 399/200 < x < 499/250 throughout this interval. They follow by raising
the two positive endpoint comparisons to their denominators; the verifier
checks both displayed inequalities with integer arithmetic. Monotonicity of
2^p covers every intermediate real exponent.

The per-copy raw saving is (x-1)(2-x)(x^2-2). Each factor is positive on
this bracket, so it is at least

```text
L = (399/200-1)(2-499/250)((399/200)^2-2)
  = 15760999/2000000000.
```

Since 127L-1=1646873/2000000000>0, 127 copies fund an additional rank-one
child, whose raw power bill is exactly one at every a. Expanding those
copies gives precisely the fully charged profiles above. The old count is
889 and the new count is 890; their rank masses are 3556 and 3557.

This credit also obeys 126L<1. That only says this particular lower bound
does not certify 126 copies. It is not a lower bound on the actual optimum.
More generally, any complete added positive-rank bill with rank mass below
NL is funded by N copies, since r^(1-a)<=r for every integer r>=1.
This paid-cost implication is the framework credited to #3868 and #3863.

At unchanged positive ambient rank m and normalizer W, multiplying the
comparison by m^(a-1)/W preserves its sign. Unchanged other charges cancel.
Consequently an already admissible complete moment remains below one if
this replacement is legally implemented with exactly the charged cost.
Strict child contraction requires m>16 in the first example, and m>2^(q+2)
for the general family. Other compiler restrictions remain separate.

## Evidence and reproduction

The written factorization proves the universal statement. The standalone
standard-library verifier constructs all 66 pairs q,s with 2<=q<=12.
For each it checks count and mass conservation, four rational polynomial
points, exact reduction modulo x^q-2^s at the threshold, and the raw profile
signs at every distinct rational power with denominator at most ten.
Integer bisection encloses each power at 80 binary places. The raw cost
comparison adds the actual positive and negative profile terms separately,
without using the factored sign formula to evaluate their costs. There are
264 polynomial evaluations, 1,994 strict power comparisons and 52 crossing
cases in that finite domain.

It also checks the two large integer endpoint inequalities, the complete
overhead accounting and three rational points of the fully charged bill.
Twelve controls cover six malformed parameter pairs, an omitted rank-sixteen
term, reversed profiles, the false all-exponent extension, reversed sign,
the uncertified 126-copy allowance and a false upper power bracket. Every
check uses an explicit exception and remains active under optimized Python.
The stdout receipt is generated from actual checks and hashes every package
file. No receipt is handwritten, and ordinary execution writes no files.

From the repository root, use CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/rational-threshold-rank-exchange/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/rational-threshold-rank-exchange/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/rational-threshold-rank-exchange
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/rational-threshold-rank-exchange --check-source-history
```

Any CPython 3.12 installation may replace the displayed interpreter. Direct
execution works in a Git-free export of these five files and prints
`PASS_RATIONAL_THRESHOLD_RANK_EXCHANGE` inside its JSON receipt.

## Scope, sources and credit

Base: canonical main a5df48c55ea806d7952b65acc9c76d878ff09b13, priority
revision 7. The independent-moment card is explicitly changed to this
original arithmetic side question. The selected source-binding baseline
passed as orientation only. It is not a selected operator replay.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19144860)
names this scope. SOURCES.json pins predecessor prose as provenance only;
no predecessor executable or scientific receipt is imported or rerun.

Credit Dugongue #3868 for the interval-specific question, all-exponent
comparison and paid allowance; Dugongue #3863 for the preceding concave
pricing framework; and their retained ranked-pair and moment-transfer
lineage, including Avi Eisenberg, eumemic, Chafik Boukhalfa, Dominik Scholz
and MathProof. Their source notices and credit lines remain unchanged.

No current source inventory, compatible operands, native implementation,
dirty restoration, frame changes, hosting, stock, precision, tape cost or
complete compiler/consumer has been supplied. All missing costs are unknown.
The result supplies neither a physical supplier nor a complete multiplication
theorem, and changes no selected-frontier file. Independent human and formal
proof-kernel review are unclaimed. Lean, Docker and predecessor scientific
replays were outside scope and were not run.

The finite checker uses no recursion, subprocesses, network calls or dynamic
code generation. Its functions stay below 60 physical lines. The largest
profile has 15 coefficient slots; its family loop has 66 iterations and each
root bisection has at most 81. The endpoint checks use fixed exponents at most
10000. Five package reads are capped at 1 MiB each. Python's dynamic integer
and Fraction allocation and the bounded rejection dispatcher are documented
managed-runtime deviations from Power of Ten rules 3 and 9. Warning-strict
normal/optimized execution and the registered replay are the available
diagnostics. No real-time or performance claim is made.

## Open next questions

Can an actual producer and consumer implement this seven-child exchange with
a favorable complete bill? Start with four rank-one and three rank-eight
operations in one named word. Prove the replacement operator identity and
its endpoint compatibility before counting copies. No such grouping,
rank-sixteen recursion, physical circuit or complete paid implementation is
known from this package. Optimizing the arithmetic batch size cannot supply
those missing obligations.
