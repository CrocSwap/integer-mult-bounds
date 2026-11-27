# From field width to the full Walsh history

## Pricing the actual Walsh path

Use the [spatial child quarter](walsh-child-clock.md) at $48\Phi$ and the [separated column-map bill](walsh-node.md#only-actual-column-maps-use-the-interchanger) at the true slot width $f$. Here $x=\lceil\log_2(a+2)\rceil$ for current active width $a$, $y=\log_2(m+1)\le(33/32)\Phi(x)$, and $f/a\le 1/(2m)$. Define $\gamma=33/4$ and

$$
G(x)=48\Phi(x)+\max\left\{0,\max_{0\le v\le x}
       [H(v)-(48-\gamma)\Phi(v)]\right\}. \tag{2}
$$

The excess $G-48\Phi$ is nondecreasing, so the spatial quarter inequality remains true for $G$ at each rounded child width. Also $G(x)\ge H(v)+\gamma\Phi(x)$ for every $v\le x$. In particular the local nonrecursive movement costs at most a fixed $2^{54}(1+5120)$ times its parent volume, $b\sqrt a$ and $2^{G(x)}$: the [native bound](address-native-staircase.md) and $\sqrt{f/a}\le1/\sqrt{2m}$ reduce $m^{17/2}$ to $m^8$, and $m^8\le2^{\gamma\Phi(x)}$. The ordinary $2^{105}m^{45}V$ term fits $2^{105}V\sqrt a\,2^{48\Phi(x)}$, since $45(33/32)<47$. The direct remainder and fixed-additive amortization use the original volume proof. The smaller prefactor $A_W=2^{110}(1+5120)$ pays the direct base, ordinary events and typed local calls under the fixed guard in [the all-width proof](address-native-staircase.md). Induction gives the full layer with prefactor $2^{18}A_W$ and exponent $G(X)$. At the initial and final root positions $G(X)\ge H(\log_2 k)$ pays their actual interchanges. The full CRTs and block layers use the same comparison. Thus the complete joined time is

$$
T\le 2^{55}A_W b^4 Nk\sqrt{k}\,2^{G(X)}
$$

at the actual global address width $k$, $b=\lceil\log_2(2k)\rceil$ and $X=\lceil\log_2(k+2)\rceil$. Formula (2) is a proof majorant only. Constructing a table of its history is unnecessary during execution.

## A decreasing density for the full history

Write $P=\Phi$, $L=48$, $\gamma=33/4$, $c=L-\gamma=159/4$. The historic Walsh potential is

$$
 G(x)=L P(x)+\max\{0,\max_{0\le v\le x}(H(v)-cP(v))\}.
$$

The [typed-width proof](routing-refined-walsh.md) uses this $H$ without changing any location, coefficient, arity or adaptive local call. In particular a true local direct width $x<2^{24}$ costs at most $2^{19}V\sqrt a\,2^{48\Phi(x)}$ by the [base invoice](walsh-node.md). Every nonbase ordinary and data bill has room under $A_W=2^{110}(1+5120)$. The parent pays its real inherited reserve exactly once and the historical surplus preserves the paid spatial quarter.

For $t\ge z>0$, both $H(t)/t$ and $P(t)/t$ are nonincreasing because the functions are concave and vanish at zero. The same holds for $G(t)/t$. To prove this, for $v\le z$ a nonpositive surplus is already covered by $LP(t)$; a positive fixed surplus divided by $t$ decreases. For $z\le v\le t$ put $r=v/t$. Then $H(v)\le vH(z)/z$ and $P(v)\ge rP(t)$. Consequently

$$
 \frac{LP(t)+H(v)-cP(v)}{t}
 \le (L-cr)\frac{P(t)}t+r\frac{H(z)}z
 \le\frac{(1-r)LP(z)+r[H(z)+\gamma P(z)]}{z}
 \le G(z)/z .
$$

The [kernel-checked density theorem](../S008/PiecewiseDensity.lean) proves this inequality for an arbitrary earlier charge and real outer scale. The zero-surplus contribution satisfies the same inequality. In particular $G(t+2)/t$ decreases, as the product of $G(t+2)/(t+2)$ and $(t+2)/t$. The other normalized charges $1/t$ and $\log_2(t+2)/t$ also decrease. A successful endpoint therefore controls every later real width, including across all future native switches.
