# A coefficient of 60 beyond an explicit input length

The complete fixed multiplier satisfies the following sharper estimate whenever $t=\log_2\log_2 n\ge1{,}572{,}864{,}480$, with $\ell=\log_2 n$:

$$
  2T(n)\le n\sqrt{\ell}\,2^{60\Phi(t)}.
$$

The earlier and revised global Walsh guards agree throughout this range. The argument also identifies the exact limiting upper coefficient of the [three-slope estimate](address-native-staircase.md). Its value in the whole-product logarithmic invoice is

$$
 C_*=\frac{33}{4}+\sqrt[3]{240}\,\frac{299}{36}
       =59.8645844044\ldots .
$$

This equality describes the stated proof estimate. It imposes no lower bound on the runtime of a multiplier.

## The change in the native coefficients

Use the same arity band, knots $S_{j,a}=240(aQ_j2^{3j}+2)$ and heights $H$ as in [the physical proof](address-native-staircase.md). Put $A=17/4,\ B=11/3,\ h=299/36,\ \alpha=240^{1/3} h,\ c=159/4$. At the initial knot with $j=6$,

$$
 S=S_{6,1}=1{,}572{,}864{,}480,\quad H(S)=200{,}560{,}880,\quad h_6=2{,}507{,}011/307{,}200<h .
$$

The recurrence $h_{j+1}=20/3+(Q_j/(4Q_{j+1}))(h_j-7/4)$ preserves $h_j\le h$ for every $j\ge6$: $Q_j\le Q_{j+1}$ and $h=20/3+(h-7/4)/4$. A negative parenthesis gives a still smaller term. At each knot $\log_2(S_{j,a}+2)\ge Q_j$, so the ratios $H/\Phi$ at the three knots of a band are at most

$$
 240^{1/3}\left(h,\ \frac{h+A}{2^{2/3}},\
                        \frac{h+A+2B}{4^{2/3}}\right).
$$

Both latter entries in parentheses are smaller than $h$ by exact cubing. On each linear piece $H-\alpha\Phi$ is convex. Therefore $H(y)\le\alpha\Phi(y)$ for every $y\ge S$.

At every previous corner $v<S$, one has $v\le S_{5,4}=692{,}060{,}640<S/2$. By the all-length bound, $H(v)-c\Phi(v)\le(115/8)\Phi(v)$. From the definition of $\Phi$,
$\Phi(v)\le2^{-2/3}\Phi(S)\le(2/3)\Phi(S)$. Thus every such corner surplus is at most $(115/12)\Phi(S)<(\alpha-c)\Phi(S)$. At $S$ itself the new bound applies. Convexity on each earlier linear piece, including the last piece ending at $S$, bounds its entire surplus by its two endpoints. For $x\ge S$ the historical maximum used in Walsh therefore satisfies

$$
 G(x)=48\Phi(x)+\max_{0\le v\le x}(H(v)-c\Phi(v))_+
       \le (\alpha+33/4)\Phi(x).
$$

This controls the true inherited bank, ordinary bills and typed column movements through the [complete Walsh transfer](routing-refined-walsh.md).

## Numerical absorption by the whole machine

The joined excess is at most $182+4\log_2(t+2)+C_*\Phi(t+2)$ for all $t\ge S$. Exact cubing gives $C_*<479/8$. The [shift inequality](../S008/WholeProfile.lean) bounds $\Phi(t+2)$ by $\Phi(t)+2$. For $t\ge2^{30}$, $512\log_2(t+2)\le t$ by the single endpoint test with $j=31$ and logarithmic density. Cubing yields $4\log_2(t+2)\le\Phi(t)/16$. Also $\Phi(t)\ge 2^{20}$. Then $182+2(479/8)+1<\Phi(t)/16$. Together these inequalities bound the joined excess plus an extra bit by $60\Phi(t)$. The original input length, actual global width and cumulated distinct-cell bound are precisely those in the [all-length statement](../CONSTRUCTION.md).
