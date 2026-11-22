# Why the full raw invoice has exactly one crossing

For the complete 36-call binary circuit, write its raw difference as
$D(t)=\sum_r a_r r^t$, where $a_r$ is the productive count minus the paid
count at rank $r$. The price $c$ uses $t=1-c$. Normalizing at the rank
where the sign pattern changes gives a global monotonicity proof.

**Lemma.** Let $p>0$. Suppose $a_r\le0$ for $r<p$ with at least one strict
inequality, and every upper tail $S_j=\sum_{r\ge r_j}a_r$ at the
distinct ranks $p<r_1<\cdots<r_m$ is nonnegative. Then
$D(t)/p^t$ is strictly increasing for $t\ge0$.

**Proof.** Below $p$, each term has derivative
$a_r(r/p)^t\log(r/p)\ge0$, with at least one positive derivative.
At $p$ the normalized contribution is constant. Put
$q_j=(r_j/p)^t\log(r_j/p)$ and $q_0=0$. For every $t\ge0$, the function
$x\mapsto x^t\log x$ is increasing on $x>1$, because its derivative is
$x^{t-1}(1+t\log x)>0$. By summation by parts the derivative of the upper
contribution is $\sum_{j=1}^m S_j(q_j-q_{j-1})\ge0$. This proves strict
increase on the whole half-line.

For the source word take $p=8$. The seven lower coefficients at ranks 1
through 7 are $-48972,-44892,-1980,-900,-1044,-2916,-480$.
Above rank 8 the nonzero coefficients pair 444 labels at each of
$14,21,28,35,42,49,56$ with the same number one rank higher.
The two additional productive counts are 444 at rank 64 and 222 at rank
127. Every upper tail is at least 222. Since $D(0)=-85998$ and
$D(1)=1506$, there is exactly one crossing on $0\le t\le1$.
In particular, the raw funding condition $D(1-c)>0$ cannot resume above
a failed trial anywhere in $0\le c\le1$. For $t\le0$ all positive
coefficients occur at ranks at least eight and their sum is 18,294. Keeping
just the negative rank-one term bounds $D(t)\le-48,972+18,294=-30,678$.
The same sign dichotomy therefore holds for all real prices.

Integer square-root enclosures at two internal dyadics independently put the
crossing $c_*$ strictly between 0.003890115286594461129996942 and
0.003890115286594461129996943. The outward integer sign intervals have
common denominator $2^{112}$. Their numerators are
$[1457154697782,1457195972250]$ and $[-534622260294,-534579885888]$.
Thus 0.003890115286594461 is the largest multiple of $10^{-18}$
that can satisfy this raw test for these exact labelled words.
Whether a particular finite priced machine reaches that grid point is a
separate construction. Other productive or paid inventories change the
polynomial and its crossing.
