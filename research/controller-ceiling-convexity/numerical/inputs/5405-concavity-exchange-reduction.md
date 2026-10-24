# #5405: concavity reduces every fixed-FULL-count invoice to one balanced mask

The proposed exchange reduction is valid for the exact invoice family in #5405 equation (1), with `0<t<1`. It yields an **attained minimum for each fixed FULL count n**. For n>=3, all three unpaired endpoint/central stages are FULL, every side pair is `10`, and the pair counts are as balanced as possible. For n=0,1,2, p=1 suffices. The proof is elementary concavity and does not need a new published theorem or a replay of the author's dynamic program.

This is an independent mathematical verification of the reduction, not a new kappa certificate. No values of the actual profile moment L, the proposed ceiling exponent, or the author's tail interval bounds were recomputed. The frozen autonomous provider profile, port count and idle law are essential. The coupled #5402 contract is outside this result.

## Exact source and reduced objective

The primary source is the sole monitor's [#5405 proof](../../upstream-monitor-resume-20261024/5405-PROOF.md), source head `314b56a6c0056c2358538f072c6fde9d365be44d`. The full equation (1), recurrence, tail and scope sections were read. Its local profiles are

```
P={1:2193,2:412,3:510,4:127,5:40},
H={4:28,7:7,8:47,9:318}.
```

Fix t in (0,1), `f(r)=r^t` for r>0, `f(0)=0`, and `L=sum P[r]f(r)-sum H[r]f(r)`. For any p>=1, split a+b=p-1 and FULL/QUERY stage mask x, the source defines

```
E = 112(2p+1)+(L-112)n-224 f(1+8n)
    +224 sum_j g(h_j,e_j),
g(h,e)=f(8h)+e f(8)-f(1+8(h+e)).
```

At fixed n, all terms except

```
J := p + sum_j g(h_j,e_j)
```

are constant: `E=224J+112+(L-112)n-224f(1+8n)`. Thus every change below compares J exactly and preserves the local FULL/helper census n. It also accounts explicitly for every added/deleted QUERY and retained idle summand. It does not preserve a given physical caller or its productive input set; the resulting mask is another member of the source's optimistic invoice family.

Read each side from its outside end toward the central stage. The left side is `x0,(x1,x2),...,(x_(2a-1),x_(2a))`; the right side is `x_(2p),(x_(2p-1),x_(2p-2)),...,(x_(2a+3),x_(2a+2))`. The central indicator is `c=x_(2a+1)`. For a pair `(o,e)` preceded by k FULL stages on that side, its summand is `g(k+o,e)`. A change preserving the total o+e leaves every later partial count unchanged.

Write `delta(z)=f(z+1)-f(z)`. Strict concavity gives `0<delta(z)<1` for z>0, `delta(0)=1`, and delta strictly decreases with z. For each fixed positive length d, `f(z+d)-f(z)` also strictly decreases with z.

## 1. Reduce side pairs to 10

**Delete 00.** This reduces p by one and removes `g(k,0)=-delta(8k)`. Therefore

```
Delta J = -1+delta(8k) <= 0.
```

Equality occurs exactly when k=0. The side may become empty; p remains at least one because a side pair existed before deletion.

**Replace 01 by 10.** This leaves p and n fixed, and leaves all later partial counts fixed. The exact change is

```
Delta J = f(8k+8)-f(8k)-f(8) <= 0.
```

This is subadditivity of the concave power. Equality holds exactly at k=0; it is strict for k>0.

**Split 11 into 10,10 on the same side.** This adds one pair, so p increases by one, while n and all later partial counts are unchanged. It adds two QUERY stages and their paid cost, which is the `+1` below in units of 224:

```
Delta J = 1+g(k+1,0)+g(k+2,0)-g(k+1,1)
        = 1+f(8k+16)-f(8k+9)-f(8).
```

For k>=0, decreasing seven-step increments imply

```
f(8k+16)-f(8k+9) <= f(16)-f(9) < f(8)-f(1).
```

The last strict inequality compares the integrals of `t z^(t-1)` over [9,16] and [1,8]. Since f(1)=1, the split strictly decreases J for every k>=0. Equivalently, the equal-sum pair (16,1) is more spread than (9,8), but no separate majorization theorem is required.

Apply these replacements independently to the finitely many original side pairs. No replacement introduces a pair type other than 10, so the process terminates. Afterwards every side consists only of 10 pairs. The three unpaired indicators are still arbitrary bits.

## 2. Move FULL stages to the unpaired positions

Let q_L,q_R count the remaining 10 pairs, and let l,r,c be the left-end, right-end and central indicators. Then

```
n = l+r+c+q_L+q_R,       p=q_L+q_R+1.
```

**A nonempty side with QUERY end.** Replace its first 10 pair and QUERY end by a FULL end, deleting the pair. The removed pair had h=1. Later partial counts are identical: both old and new prefixes contain one FULL before the next pair. Thus

```
Delta J = -1+delta(8) < 0.
```

Perform this on each side that qualifies. Every remaining QUERY end is now on an empty side.

**Fill a QUERY central stage or an empty QUERY side end.** Remove the last 10 pair from any nonempty donor side and turn that unpaired QUERY indicator into FULL. Removing the last pair affects no later donor partial count. The central indicator belongs to no side partial count; an empty recipient side has no summands. If the donor pair ends with k FULL stages on its side, k>=1, and

```
Delta J = -1+delta(8k) < 0.
```

The donor side loses one pair, p decreases by one, and the moved FULL keeps n fixed. A donor always exists while an unpaired position needs filling and the target number of FULL unpaired positions has not been reached: `q_L+q_R=n-(l+r+c)>0`.

For n>=3, repeat until l=r=c=1. The final number of pairs is n-3 and `p=n-2`. For n<=2, repeat only until all n FULL stages occupy unpaired positions; then q_L=q_R=0 and p=1. The same reasoning gives p=1 for n=3 with all three indicators FULL. The construction works also when one side initially has no pairs or both sides are empty.

This proves the small-count reduction without assuming n>=3 during a transfer. For n=0, deleting 00 pairs has equality throughout, and every all-QUERY invoice already has E=112.

## 3. Balance the two sides

For n>=3 both side ends are FULL. The j-th 10 pair on either side therefore has `h=j+1`, including h=2 for the first pair. Define

```
F(q) = -sum_(k=2)^(q+1) delta(8k),       F(0)=0.
```

The side contribution is F(q), and

```
F(q+1)-F(q)=-delta(8(q+2)).
```

These increments strictly increase with q, so F is strictly discretely convex. If a>=b+2, moving the last pair of the longer side to the end of the shorter side changes the score by

```
F(a-1)+F(b+1)-F(a)-F(b)
 = delta(8(a+1))-delta(8(b+2)) < 0.
```

Thus at fixed a+b=n-3, the minimum has

```
a=floor((n-3)/2),       b=ceil((n-3)/2),
```

up to reflection. Balanced reflected masks have the same invoice. This balancing changes the permitted split and the mask; it does not claim a free physical retiming of one caller.

## 4. Exact canonical minimum for each n

Every original invoice has been transformed to an admissible canonical invoice with no larger E. Conversely the canonical invoice is itself in the stated family. Consequently its value is the **global minimum over all p, splits and stage masks with that FULL count n**.

For n=0,1,2,

```
C_n(t) = 336+(L(t)-112)n-224(1+8n)^t.
```

For n>=3, put a=floor((n-3)/2), b=ceil((n-3)/2). Then

```
C_n(t) = n L(t)+112(n-3)-224(1+8n)^t
         -224[sum_(k=2)^(a+1) delta(8k)
              +sum_(k=2)^(b+1) delta(8k)].
```

The formulas agree at n=3 if the first expression is extended there. For n=18 they select p=16,a=7,b=8, with side FULL counts eight and nine and a FULL central stage, matching the location reported by the author's dynamic program. This is an index/formula comparison, not a replay of its numerical minimum.

The result holds separately for every 0<t<1 and is independent of the value of L(t). Strictness is as stated for each exchange; it does not assert that the original minimizing mask is unique, since zero/zero prefixes at partial FULL count zero can be deleted with equality. The endpoints t=0 and t=1 are not included in the strictness claims.

## Verification consequence and limits

If the source's n>=96 tail certificate at its specified exponent is accepted, the finite part can be independently checked using only **96 canonical invoices, n=0,...,95**, instead of 10,290,000 dynamic-program combinations. This note does not rerun that tail certificate, those 96 numerical inequalities, the author's interval engine, or the extension to all larger kappa. It establishes the analytic reduction that would permit the smaller independent verification.

The [bounded exact controls](../tests/5405-EXCHANGE-TOY-CONTROLS.json) use t=1/2, p<=4 and n<=6 so both compared invoices stay within p<=4. They compare square-root expressions using symbolic square-factor normalization and outward rational bounds on a 2^80 grid, under a ten-second alarm. They check the side-index translation against equation (1), the zero/strict cases of each exchange, balancing, and attainment of the canonical minimum in the bounded domain. No actual profile moment L is evaluated because it cancels at fixed n.

The previous #5397 primary PR body describes classical concave-order invoice preflight and explicitly separates that arithmetic from physical legality and funding. The existing literature ledger was checked first; no earlier paper dependency is needed for the elementary derivative proof above. This is not an application of Douglas's unrelated operator-majorization theorem. No new paper was added.

The local P/H profiles are autonomous jobs, each FULL has 112 ports and a fresh rank-eight stage block, and the prefix/suffix idle law is fixed. Coded or coupled helper outputs, altered target lists, changed stage ranks, different idle incidence, or another controller graph require a new comparison. In particular this does not apply to #5402. No physical optimum, native query lower bound, compiler admission or improved exponent follows.

Credit Ali Romman for #5405's source family, equation, original unbounded ceiling and exact dynamic program; Cinna Davis for the paired controller; the retained native/helper/compiler/interval contributors; and root for proposing the exchange conjecture checked here. This note independently checks the moves, indices, strictness and small counts, with substantial OpenAI Codex assistance. Local only; no external publication.
