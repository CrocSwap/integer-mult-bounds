# When the joint probability crosses the product of the marginals

Let $R_d=J_k/p^k$, with $d=m-1$ and $2\le k\le q$. Positive and negative below mean $R_d>1$ and $R_d<1$ respectively. In particular they compare the probability of **all** guards passing with the independence prediction. They do not describe the sign of an arbitrary higher cumulant.

## Shape in the header dimension

Put $x=1/q$, $s=A/B_k$, $\theta_1=A/q^2$, $\theta_k=B_k/q^3$, and $T=\theta_k/\theta_1^k$. The pencil formula gives

~~~text
R_d = (1-x)^(1-k) T^d (1-x^(d+1))^(k-1) (1-s^d)/(1-x^d).
~~~

Here $x<s<1$, since $A<B_k<qA$ for distinct directions. The expression defines a positive smooth interpolation for real $d>0$. Its logarithm is strictly concave. To see this, write $f_a(d)=\log(1-e^{-ad})$ for $a>0$. Then
$f'_a=a/(e^{ad}-1)$ and $f''_a=-[a/(2\sinh(ad/2))]^2$. For each fixed $d>0$, both $f'_a$ and $|f''_a|$ strictly decrease in $a$. This follows from the strictly increasing functions $(e^z-1)/z$ and $\sinh(z)/z$. Thus $f_{-\log s}-f_{-\log x}$ is strictly increasing and strictly concave. The remaining correction $(k-1)f_{-\log x}(d+1)$ is also increasing and strictly concave. The affine term $d\log T$ preserves strict concavity.

In particular the consecutive ratios $R_{d+1}/R_d$ strictly decrease and tend to $T$. The positive integer dimensions form one interval, possibly empty or infinite. The correction to $T^d$ is increasing. Thus if $T\ge1$ and $R_1>1$, every dimension is positive.

## Which pencils eventually fall below the product?

We have $\theta_1=1-x+x^2$ and $\theta_k=\theta_1-(k-1)x(1-x)^2$. Factoring the difference gives

~~~text
theta_k - theta_1^k
  = x(1-x) [sum_{i=1}^{k-1} theta_1^i - (k-1)(1-x)].
~~~

The average of the powers inside the sum strictly decreases with $k$. At $k=2$ it exceeds $1-x$. At $k=3$ twice the difference of the average from $1-x$ is $x(-1+4x-2x^2+x^3)$. This is strictly negative for $0<x\le1/4$ (the first two terms sum to at most zero, the remaining two are negative) and positive at $x=1/3$. Thus over every field with $q\ge4$, every pencil of at least three directions eventually falls strictly below the product. For the only remaining triple, $q=k=3$, the initial joint probability is $1/4>(7/12)^3$ and $T>1$, so the sign is positive for all dimensions. Every pair is positive by the credited all-field pair theorem. [PR #6703](https://github.com/CrocSwap/integer-mult-bounds/pull/6703)

At $q=4,k=3$ the exact positive dimensions are $2\le m\le60$; every $m\ge61$ is negative. At $q=k=5$ the only positive dimensions are $m=3,4$. At dimension two every proper subfamily with at least two members lies above its product, yet all five together lie below theirs. For instance the joint probabilities for subsets of sizes one through five are $7/10,17/30,13/30,3/10,1/6$. The inequalities are strict. Certify the endpoints by integer division: $\lfloor 10^8 R_{m-1}\rfloor$ is 127446517, 100873870, 99909668 at $(q,k,m)=(4,3,2),(4,3,60),(4,3,61)$, and 99165030, 111744023, 102119948, 86044038 at $(5,5,m)$ for $m=2,3,4,5$. Strict concavity fills the interval between positive endpoints, and a decreasing adjacent ratio at a crossing precludes a later return.

## A complete sign classification for the full pencil

| Field order $q$, with $k=q$ | Dimensions $m\ge2$ with $J_q>p^q$ |
| --- | --- |
| 2 or 3 | All |
| 4 | 2 through 8 |
| 5 | 3 and 4 |
| Every prime power $q\ge7$ | None |

Every other dimension in this table has a strict negative sign. For the four-element case the scaled ratio floors at $m=2,8,9$ are 112040894, 109043745, 98225073. The five-element case was certified above.

For $q\ge7$, first consider $m=2$. The full pencil has $J_q=1/(q+1)$ and $p=(1-x+x^2)/(1+x)$. The bounds $1-x+x^2\ge e^{-x}$ and $1+x\le e^x$ give $p^q\ge e^{-2}>1/(q+1)$ because $e^2<8$. To rule out a later positive window it suffices by strict concavity to prove $R_2/R_1<1$. Direct cancellation gives

~~~text
R_2/R_1 = [(3q^2-3q+2)/(q(q^2+q+1))]
          [1+(q^2+q-1)/(q^3+1)]^q.
~~~

The first factor is at most $3/(q+2)$ by multiplication. The second is less than $\exp(1+1/q)$ by $\log(1+y)\le y$. For $q\ge8$ their product is at most $(3/10)\exp(9/8)<1$; one elementary bound is $e<11/4$ and $\exp(1/8)\le8/7$. At $q=7$ the floors of $10^8R_1$ and $10^8R_2$ are 79423132 and 71959023. This proves the last row for every dimension.

## Fixed family size as the field grows

Fix $k\ge3$ and let $q$ grow through prime powers. The finite upper endpoint $m_*(q,k)$ of the positive interval exists for all sufficiently large $q$, and

~~~text
m_*(q,k)/q  ->  2/(k-2).
~~~

Indeed $\theta_k=1-kx+(2k-1)x^2-(k-1)x^3$, so $\log T=-(k-1)(k-2)x^2/2+O_k(x^3)$. If $d/q\to c>0$, then $s=O_k(1/q)$ and the logarithms of all three factors involving $s^d,x^d,x^{d+1}$ are $o(1/q)$. Therefore
$q\log R_d\to(k-1)-c(k-1)(k-2)/2$. Choose $c$ just below and just above $2/(k-2)$. The two strict opposite signs, together with concavity, trap the upper crossing and prove the limit. This fixed-$k$ limit has a different regime from the full-pencil table.

SIGN-WINDOWS.json contains exact interval certificates for each pencil size at the listed prime-power orders through 31. The program first locates the peak by decreasing adjacent ratios, then bisects both boundaries. A separate bounded scan checks these intervals on $2\le m\le81$. The all-dimension conclusions above use the proof of strict concavity and the exact input ratios.

## How many guards can be bundled at a fixed dimension?

Hold $q,m$ fixed. The formula with $B_1=qA$ allows $k$ to vary continuously from $1$ to $q$. Apart from a constant and the affine term $-k\log p$, the logarithm of the ratio is $\log(B_k^d-A^d)$. Its second derivative with respect to $B=B_k$ is

~~~text
-d B^(d-2) [B^d+(d-1)A^d] / (B^d-A^d)^2 < 0.
~~~

As $B_k$ decreases linearly in $k$, the ratio is strictly log-concave in family size too. It equals one at size one and is strictly larger at size two. At each fixed dimension there is thus a unique largest size $K(q,m)$ above the independence prediction. All sizes from two to $K(q,m)$ lie above it; a possible tie can only occur at $K+1$. Equivalently, the conditional probability $J_{k+1}/J_k$ of the next specified guard passing, given that all earlier ones pass, strictly decreases for $k\ge1$ while the next direction exists. This comparison begins after conditioning on at least one pass.

For fixed $d=m-1\ge1$, as $q\to\infty$,
$K(q,m)/q\to\alpha_d$, the unique strictly positive root in $(0,1)$ of
$d\log(1-\alpha)+(d+1)\alpha=0$. Indeed for $k/q\to\alpha\in(0,1)$ the exact formulas give $J_k\to(1-\alpha)^d$ and $p^k\to\exp(-(d+1)\alpha)$, since $p=1-(d+1)/q+O_d(q^{-2})$. The limiting log ratio is strictly concave, has derivative one at zero, and tends to minus infinity at one. Two values bracketing its positive root, together with the single size cutoff, prove the stated limit.

There is a joint scaling window as well. Suppose $k\to\infty$, $k/q\to0$, and $d k/q\to c>0$. Then $d\to\infty$ and

~~~text
(q/k) log R_d -> 1-c/2.
~~~

In fact the expansion from the previous section has remainder $O(k^3/q^3)$ uniformly when $k/q$ is small: expand the two logarithms at $1$, using $|\theta_k-1|=O(k/q)$. The constant factor contributes $(k-1)/q+O(k/q^2)$ to the log ratio. Multiplying the quadratic term by $d$ supplies $-d(k-1)(k-2)/(2q^2)$; the multiplied remainder is $o(k/q)$. Also $s=O(1/q)$ along this scaling, so the three finite-power corrections are $o(k/q)$. In particular dimensions on either side of $dk/q=2$ have opposite eventual signs when bounded away from two. ASYMPTOTICS.json records finite bracketing examples for both endpoints and for $k$ near the square root of the field order.
