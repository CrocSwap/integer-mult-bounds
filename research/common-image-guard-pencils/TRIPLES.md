# Three independent covectors are above the product in every dimension

Let $q$ be any finite field order, $m\ge3$, $d=m-1$, and let the three normalized rows be independent. Then their joint guard probability is **strictly greater than** $p^3$. This statement includes the finite dimensions not controlled by comparison of the dominant exponential bases in the lattice formula.

## Use a larger sampling space

Sample $u'$ uniformly among nonzero vectors. Given $u'$, sample three rows independently and uniformly with pairing one against $u'$. Put $Q=q^d$. The rows lie in an affine hyperplane with $Q$ points. Their linear independence is equivalent to affine independence there: any linear relation has coefficient sum zero because all three pair to one. Given the first point, the second must avoid one point and the third must avoid the affine line through the first two. Thus the event $I$ of independence has probability
$P_I=(1-1/Q)(1-q/Q)>0$ and $1-P_I\le(q+1)/Q$. Conditioning on $I$ gives exactly the uniform rank-three tuple orbit in PROOF.md.

Let $z(u')$ be the single-row pass probability at fixed $u'$. Its mean is $p$. It vanishes unless $u'_m\ne0$, an event with probability $c=(1-1/q)/(1-q^{-m})$. In the enlarged space the joint probability is $T=\mathbb E[z^3]\ge p^3/c^2$ by conditional Jensen. In the independent-row orbit,
$P_I J_{\mathrm{ind},3}\ge T-(1-P_I)$. Consequently $T-p^3>1-P_I$ suffices. Here $c^{-1}=1+q^{-1}+\cdots+q^{-d}$, giving $c^{-2}-1\ge2/q$. Writing $t_1=1-1/q+1/q^2$ gives $p=c\,t_1^d>(1-1/q)t_1^d$. A sufficient **integer-checkable** inequality is therefore

~~~text
L(q,d) = (2/q)(1-1/q)^3 (q t_1^3)^d > q+1.
~~~

For $q\ge3$ the base $q t_1^3>1$: at $q=3$ it equals $343/243$; at $q\ge4$ it exceeds $q(3/4)^3>1$. Thus once this condition holds it continues to hold as the dimension grows.

## A uniform tail and finite certificates

For every $q\ge19$ already at $d=2$,
$L(q,2)>2q(1-1/q)^9\ge2q-18\ge q+1$, using Bernoulli's inequality. For $q=2$ the last-coordinate bound in PROOF.md already gives strict positivity at family size three.

For the remaining prime powers, the table gives the first $d_0\ge2$ certified by $L(q,d)>q+1$. Below it the four-term independent-triple formula gives the listed **minimum** floor of $10^6J_{\mathrm{ind},3}/p^3$ over $2\le d<d_0$. All 17 exceptional rows, with exact numerator and denominator of the ratio, are retained in TRIPLE-CERTIFICATES.json.

| $q$ | $d_0$ | Number of exceptional dimensions | Minimum scaled floor |
| ---: | ---: | ---: | ---: |
| 3 | 9 | 7 | 2327091 |
| 4 | 5 | 3 | 1798642 |
| 5 | 4 | 2 | 1570085 |
| 7 | 3 | 1 | 1362826 |
| 8 | 3 | 1 | 1307085 |
| 9 | 3 | 1 | 1266206 |
| 11 | 3 | 1 | 1210248 |
| 13 | 3 | 1 | 1173734 |
| 16 or 17 | 2 | 0 | — |

The exceptional values also have a direct affine-point count. Given $u'_m\ne0$, suppose $j$ of the first $d$ coordinates of $u'$ are zero. A normalized row has $d$ free coordinates before testing. At each zero position retain its free row coordinate; at each nonzero position use the new prefix sum as the coordinate. This triangular coordinate change is invertible and preserves affine independence. The allowed rows form a box with $j$ unrestricted coordinates and $d-j$ coordinates avoiding one, of size $N=q^j(q-1)^{d-j}$. There are $N(N-1)(N-2)$ ordered triples of distinct points. For each scalar $\lambda\ne0,1$, count $z=(1-\lambda)x+\lambda y$ in the same box. An unrestricted coordinate allows $q^2$ pairs, a restricted coordinate allows $(q-1)(q-2)$ after translating the forbidden value to zero. The count $H=q^{2j}[(q-1)(q-2)]^{d-j}$ includes $N$ choices with $x=y$. Thus subtract $(q-2)(H-N)$ to remove exactly the distinct collinear triples. Weight by the $(q-1)\binom dj(q-1)^{d-j}$ corresponding image vectors and divide by $(q^m-1)Q(Q-1)(Q-q)$. This different computation reproduces every exceptional ratio without using the subspace weights.
Thus the independent triple is strictly above the product over every field and dimension in its domain.

## Exhausting the triple types

A triple with a repeated row also lies strictly above $p^3$: it reduces to a marginal or a distinct pair, and the latter exceeds $p^2$. Three distinct rows of rank two lie on an affine line of normalized covectors, so they form exactly a three-direction pencil. The pencil classification in SIGN.md and the independent result above exhaust the possibilities. In particular a below-product triple requires three distinct collinear covectors; it cannot be explained by any negative pair sign.
