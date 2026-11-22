# Finite price of the physical Gaussian calendar

Use the installed two Gaussian job types, their weights 1 and 90, and their 51 grade shares. Set the lower band edge to $L=2048$ in the active calendar. The raw trial is $c=17145637167/2^{42}$ and $t=1-c$. For every $M=2^H$ with $H\ge 1024$, let $F$ be the actual number of recursive singleton calls divided by the number $M^{92}$ of productive rows. The bound is

$$
F < M^{1-c}2^{65081/524288}.
$$

Thus the positive supplier buys any booked rate $b<c-(65081/524288)/H$. The complete positive coefficient is still $Z=M^{220}(1+B_{\rm ord})$. This section prices the numerical invocation. The ordinary supplier has its own physical transfer and two-moment reserve. [Integer calendar and typed receiver](typed_transport.py) · [Exact price](positive_debit.py)

## Boundary mass and paid suffixes

Write $N_k=\sum_b w_b n_{bk}$ for the weighted count of targets of grade $k$. Use $D_r$ for the corresponding weighted paid count. Let $p_{rk}$ be the installed grade fraction. After summing the probabilities of individual target owners, the directed measure for grade pair $(r,k)$ has weight $D_r p_{rk}$. Its common boundary mass is

$$
\Psi=\sum_{r,k}D_r p_{rk}\,r\,\frac{(k/r)^c-1}{c}.
$$

With $V=M^6$ and $U=2\lfloor M/(2048\cdot306)\rfloor$, the ideal terminal and exterior **linear axis counts** per time are $VL^c\Psi$ and $VU^c\Psi$. These follow by integration on $[L,Lk/r]$ and $[U,Uk/r]$, since $U/L>516\ge k/r$. They count the actual singleton axes from a job and the width of the corresponding exterior job. [Linear boundary proof](https://github.com/aliromman/integer-mult-bounds/blob/dfd25d553a843a946ca0b94130a5ff8943e98fdd/research/retimed-native-multiplier/TRANSFER.md#price-of-the-complete-integer-plan)

For $z=k/r$ set $u=(z-1)/(z+1)$. All occupied cells have $z\ge5/4$. The bound $(z^c-1)/c\ge\log z$ follows from $\exp v\ge1+v$. Integrating $2/(1-v^2)$ on $[0,u]$ gives $\log z\ge2(u+u^3/3+u^5/5)$. The sum of these rational lower bounds on all 51 actual cells is greater than $179021766.8064$. The weighted sum of productive axes is $\sum_k N_k k=135150528$. Therefore

$$
d_{\rm fringe}=\frac{10\sum_k N_k k}{t\Psi}<7.579 .
$$

On an interior edge the parent issues a prefix of its paid job to a real target. Its remaining suffix has fewer than $10k$ axes. At each bin $e$, type $b$ and actual target port, at most $m[e,b]$ real intervals can arrive. This follows from the per-owner capacity and disjoint receiver ranges. Thus the whole interior suffix count is bounded by $10\sum_{e,b}m[e,b]\sum_i k_{bi}$. The ideal part is at most $10V\sum_k N_k k/(tL^t)$. Dividing by $V L^c\Psi$ gives $d_{\rm fringe}/L$. The excess from the upward-rounded counts is below $20M\cdot105216\cdot258<2^{30}M$ axes. The receipt uses the exact rational upper value of $d_{\rm fringe}$ from the preceding three log terms. [Typed capacity calculation](receipt.py) · [Kernel-checked finite weighted lifting](WeightedNumerical.lean)

## The lower edge and the integer periods

Each lower band edge satisfies $e\ge2048>48$. Thus $4(e+2)/5<5e/6$, as required for separate return deadlines. The column count remains $e-8>0$ and is even. At most $4H+1$ simultaneous contexts occur on a causal dependence. With delay radix $2^{19}$, the lifetime of one raw unit is at most $1+2^{19}(U/L)^{77}<M^{77}$. The last inequality follows from $U\le M/(1024\cdot306)$, $L=2048$ and $M\ge2^{1024}$. The new lower edge increases the range of true jobs. All real executions across these extra bins occur in the charged loop. Its total number of real openings per time satisfies

$$
\sum_{b,e}m[e,b]\le\frac{91V}{tL^t}+2U<2V.
$$

Here $11t>10$, so $L^t>1024$. The lower edge has no effect on the upper fraction or the physical rank-258 root used for the mandatory ordinary exchange. Its exterior band is above $L$ at all admitted ranks. The integral endpoints remain positive and less than $M$. The original $2^{-64(H+1)}$ grid still gives less than $1/4$ error after the factor $90V/t$. The lower edge also preserves the prior precision, owner, control and high-water estimates. [Physical schedule and resource proof](PROOF.md) · [Original positive data and precision](https://github.com/aliromman/integer-mult-bounds/blob/dfd25d553a843a946ca0b94130a5ff8943e98fdd/research/retimed-native-multiplier/NUMERICAL.md#precision-along-a-real-dependency)

Set $\delta=2^{-128}$. Every exterior donor starts at a continuous coordinate $x\ge U$. Consequently its receiver coordinate $y=xr/k$ is at least $U/516$. The real per-grade columns $2\lfloor y/2\rfloor-8$ exceed $y-10$. They therefore exceed $(1-\delta)y$, since $U\ge5160/\delta$ even at $H=1024$. Also $U\ge(1-\delta)M/(1024\cdot306)$ since defining the even upper edge loses less than two units. Both inequalities hold at all larger $H$.

The number of real labels and the unchanged width-two bins give a total floor, ceiling and quadrature loss below $2^{46}M^2$ per time by the source counting proof. The separately bounded suffix count error is below $2^{30}M$. The end-of-calendar loss per birth is at most $(M^{77}/M^{82})\,2V\,2^{19}M=2^{20}V/M^4$. Each is below $2^{-132}V$ for every $H\ge1024$. Thus even their sum fits the $\delta$ allowances in the normalized terminal and exterior bills, since $\Psi>1$ and $L,U>1$. These bounds charge the factor 90 before rounding each individual grant.

Let $s'$ be an exterior field's actual number of axes and $q=4\lceil M/(4s')\rceil$ its installed period. Then $s'\le258U$, so $q s'/M\le 1+4\cdot258/(1024\cdot306)$. Also $q\le M$ because $s'\ge1$ and $M$ is divisible by four. The $R=M^2$ rounds lose at most the fraction $q/R\le\delta$ to an incomplete period. For $h$ full exterior slots, the real upper count $h\le2M^{82}V\cdot52608\cdot R<M^{91}$ holds at the entry and all later ranks. Hence the complete copy groups have overhead $\lceil M^{92}/h\rceil h/M^{92}<1+1/M\le1+\delta$. Their number retains the bound $3M^3$ because the lower exterior supply still exceeds $V$ per time. Every last partial group contributes its true data movement and singleton costs. [Source widths, active stock and complete groups](https://github.com/aliromman/integer-mult-bounds/blob/dfd25d553a843a946ca0b94130a5ff8943e98fdd/research/retimed-native-multiplier/NUMERICAL.md#true-copying-and-stack-high-water)

Combining these inequalities gives the following finite factor on $F/M^t$.

$$
(1+\delta)
\left(1+\frac{4\cdot258}{1024\cdot306}\right)
(1024\cdot306\cdot L)^c
\frac{1+d_{\rm fringe}/L+\delta}{(1-\delta)^4}.
$$

The four denominator factors cover the even upper edge to the power $c\le1$, exterior column discretization, lost integer source grants and the periodic round floor. Directed 112-bit roots prove that this factor is strictly below $2^{65081/524288}$. The numerical rate needs only the resulting bound on the volume of singleton calls. [Exact finite factor and directed root test](positive_debit.py)

## Sum by the actual number of recursive depths

Write $a=\kappa+4g$ and $b=\kappa+5g$ as in the signed caller. For a rank with $b<c-(65081/524288)/H$, the result above gives $F<M^{1-b}$. A nonnegative physical volume $v$ at the top of a positive call therefore contributes at most $v M^{(1-b)j}$ in total true fields at depth $j$. For an initial $D$ selected windows, child widths satisfy $f\le D/M^{j+1}$. At an active depth, multiplication by the local factor $(1+f)^{1-a}$ and $a<b$ give the bound $2M^{193}v(1+B_{\rm ord})(1+k)(1+D)^{1-a}$ for that entire depth. Here $k$ is the outer window width from the original controller. The stopped bound is $2^{45}M^{92}(1+e)v$ per incoming volume. The stopping condition $e\le\max(M,D^g)$ and $(1-g)b>a$ give the same per-depth coefficient as in the source.

There are at most $s+2$ physical depths, with $k\le1030(s+1)$ for the multiplier's admitted packs. The explicit coefficient $M^{220}(1+B_{\rm ord})$ pays the entire sum, including the factor $(s+1)^2$ in the outer rate. This is the predecessor's per-depth proof with the present bound $F<M^{1-b}$. The factor $256/255$ used by its stronger geometric-sum certificate is redundant in this calculation. The ordinary stage prices its separate same-rank child volumes under its original rule. [Complete positive clock, including stopped calls and every depth](https://github.com/aliromman/integer-mult-bounds/blob/dfd25d553a843a946ca0b94130a5ff8943e98fdd/research/retimed-native-multiplier/NUMERICAL.md#complete-conditional-positive-clock)
