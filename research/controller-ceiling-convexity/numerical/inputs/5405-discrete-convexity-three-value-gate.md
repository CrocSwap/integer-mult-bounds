# #5405: strict discrete convexity and a three-value gate for the unbounded family

**The analytic claim is valid.** For every fixed `0<t<1` and every finite real value L independent of n, the attained canonical minima C_n from the [exchange proof](5405-concavity-exchange-reduction.md) are strictly discretely convex on all integers n>=0. This includes the small-count junction. Consequently one positive candidate value and the two correct neighboring signs prove positivity of the entire unbounded invoice family at that fixed t. The n>=96 tail and the author's dynamic program are unnecessary for that implication.

This note supplies the analytic gate only. It does not evaluate the actual local profile moment, any claimed kappa, or the three numerical inequalities. A separately assigned numerical worker owns that certificate. No new paper dependency, physical caller transformation, source/native execution or coupled #5402 transfer is introduced.

## Premises and exact canonical sequence

The underlying primary source is [#5405 equation (1)](../../upstream-monitor-resume-20261024/5405-PROOF.md), pinned at head `314b56a6c0056c2358538f072c6fde9d365be44d`. The preceding frozen exchange proof establishes that each invoice with FULL count n has E>=C_n and that C_n is attained by another invoice in the same permitted family. That reduction, including its accounting and source scope, is a premise here.

Write

```
f(z)=z^t for z>0, f(0)=0,
delta(z)=f(z+1)-f(z),
A_n=f(8n+9)-f(8n+1),
D_n=C_(n+1)-C_n.
```

Since 0<t<1, A_n is positive and strictly decreases with n. Also delta(z) strictly decreases, with 0<delta(z)<1 for z>0. These follow directly by integrating the strictly decreasing positive derivative `t z^(t-1)` over intervals of fixed length eight and one respectively.

The canonical values are

```
C_n=336+(L-112)n-224f(1+8n),                        n=0,1,2,
C_n=nL+112(n-3)-224f(1+8n)
    -224[sum_(k=2)^(a+1)delta(8k)
         +sum_(k=2)^(b+1)delta(8k)],               n>=3,
a=floor((n-3)/2), b=ceil((n-3)/2).
```

Empty sums are zero. The first formula, extended to n=3, agrees with the second.

## Exact first differences and the small-count junction

The two balanced side counts increase alternately. When n increases to n+1, the shorter side gains a pair; on the next step the other side gains a pair at the same partial FULL count. Therefore, putting `k_n=floor((n+1)/2)` for n>=3,

```
D_n=L-112-224A_n,                                 n=0,1,2,
D_n=L+112-224A_n-224delta(8k_n),                    n>=3.
```

The side correction appears twice at each successive k: k_3=k_4=2, k_5=k_6=3, and so on. In particular its first argument is 16, not 8.

Explicit small values check both the branch point and that first repeated correction:

```
C_0=112,
C_1=L+224-224f(9),
C_2=2L+112-224f(17),
C_3=3L-224f(25),
C_4=4L+112-224f(33)-224delta(16),
C_5=5L+224-224f(41)-448delta(16).
```

For n=0,1,

```
D_(n+1)-D_n=224(A_n-A_(n+1))>0.
```

At the only junction, n=2,

```
D_3-D_2=224[1-delta(16)+A_2-A_3]>0.
```

For every n>=3,

```
D_(n+1)-D_n
 =224[A_n-A_(n+1)
      +delta(8k_n)-delta(8k_(n+1))]>0.
```

The first term is strictly positive. The last difference is nonnegative because k_(n+1)>=k_n; it is zero on alternate steps. Thus **D_(n+1)>D_n for every n>=0**, which is strict discrete convexity on the whole nonnegative integer domain. L cancels from each second difference, so the result is independent of its value. Dependence of L on t causes no issue because t is fixed throughout this argument.

Equivalently, define B_n=336+(L-112)n-224f(1+8n) and C_n=B_n+224T_n. Then

```
T_(n+1)-T_n=0,                                   n=0,1,2,
T_(n+1)-T_n=1-delta(8 floor((n+1)/2)),              n>=3.
```

These increments are nondecreasing, including the positive jump at n=3. B_n is already strictly discretely convex, and T_n is discretely convex. This gives the same proof without treating the balanced side contribution as strictly convex on each step: its increments deliberately repeat.

## The exact three-value gate

For any integer m>=1, suppose at one fixed t that

```
C_m>0,     D_(m-1)<=0,     D_m>=0.
```

For n<m, every D_j with n<=j<=m-1 is at most D_(m-1)<=0, so

```
C_m-C_n=sum_(j=n)^(m-1)D_j<=0.
```

For n>m, every D_j with m<=j<=n-1 is at least D_m>=0, so

```
C_n-C_m=sum_(j=m)^(n-1)D_j>=0.
```

Hence C_n>=C_m>0 for every n>=0, and every original invoice has E>=C_n>0. This is an exact unbounded conclusion from finite neighboring comparisons; no tail estimate, large-n limit or assumption of eventual growth is used. If both neighboring inequalities are strict, m is the unique minimizing FULL count. Non-strict signs still suffice for positivity, with a possible adjacent tie. Strict discrete convexity prevents a longer interval of tied minima. For m=0, the one-sided condition D_0>=0 is sufficient.

At m=18, the numerical worker can use the directly simplified expressions

```
C_18=18L+1680-224f(145)
     -224[2 sum_(k=2)^8 delta(8k)+delta(72)],
D_17=L+112-224[f(145)-f(137)+delta(72)],
D_18=L+112-224[f(153)-f(145)+delta(72)].
```

Thus the needed outward certificates are a positive lower bound for C_18, a nonpositive upper bound for D_17, and a nonnegative lower bound for D_18. Direct evaluation of these differences can avoid extra interval widening from subtracting separately enclosed C values. This is an evaluation plan, not an asserted sign or numerical result.

## Verification, provenance and limits

The [exact bounded controls](../tests/5405-DISCRETE-CONVEXITY-CONTROLS.json) use t=1/2 and only small n. They check the first-difference formula against the original canonical expression, all junction values, the convex correction decomposition, strict second differences, independence from an arbitrary affine L term, and a synthetic local-minimum example. Square-factor normalization detects exact identities; outward integer square-root bounds certify signs. The script has a ten-second alarm and imports no author/source code. Its finite examples check indexing and implementation; the all-n, all-t proof is the analytic argument above.

The source profile remains P={1:2193,2:412,3:510,4:127,5:40}, H={4:28,7:7,8:47,9:318}, with 112 ports, fresh rank-eight FULL stages, rank-one QUERY price, and the same prefix/suffix idle law. The theorem's affine-L independence does not alter the validity obligations of the source equation or grant a changed helper/coded-output contract. Coupled #5402 outputs remain outside this family.

The three-value implication is at a **fixed t=1-kappa**. Extending a certified sign to a whole interval of kappa requires a separate monotonicity argument; discrete convexity in n alone does not provide it. No actual kappa inequality, interval-tail certificate, DP replay, source/native execution, physical optimum, recursive admission or improved exponent is established by this note.

Credit Ali Romman for the primary invoice family, original unbounded ceiling and exact dynamic program; Cinna Davis for the paired controller; the retained source/helper/compiler/interval contributors; and root for proposing the discrete-convexity conjecture. This independent check and its exact controls were prepared with substantial OpenAI Codex assistance. Local only; no external publication. The preceding 66-entry checkpoint and its frozen exchange note remain unchanged.
