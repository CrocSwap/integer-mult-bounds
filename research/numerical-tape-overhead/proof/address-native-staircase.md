# A three-slope smooth bound on the complete integer multiplier

Write $\Phi(x)=(x^2\log_2(x+2))^{1/3}$. The existing $R=240$ binary interchanger has

$$
 T_2(V,u)\le5120 V\sqrt{1+u}\,2^{(433/8)\Phi(\log_2(u+2))}.
$$

For the integer multiplier use the existing [three global branches](../CONSTRUCTION.md), with fixed global Walsh cutoff $X=2^{24}$. At and above this cutoff the existing adaptive Walsh procedure applies. Below it the direct integral Walsh procedure applies. All other width choices, the raw external interface, physical tapes, and the constituent algorithms are the same. With $L=1+\log_2n$ and $x=\log_2L$, this gives

$$
 T(n)\le n\sqrt L\;2^{63\Phi(x)}\quad(n\ge2),\qquad
 T(1)\le4096,\qquad S(n)\le2^{32}n.
$$

The width majorant below is used only in the proof. The interchanger executes precisely its previously priced parameter schedule.

## Native charges within a dyadic arity band

Let $y=\log_2e$, $s=\log_2m$ for the actual largest odd $m\le e^{1/240}$, $u_0=\lceil s\rceil$, $v=\lceil\log_2(u_0+2)\rceil$ and $d$ the largest dyadic with $d^3v\le u_0$. Adaptive nodes start at $y_A=240(2^{17}+2)$. There $y/240-1\le s\le y/240$ and $d\ge16$. With $\sigma=\log_2(\sum_iV_i/(V\sqrt m))$, the [actual all-child invoice](child-volume.md) and its [independent degree bound](compiler-full-interchange.md) give both

$$
\frac{\sigma+2}{s}\le\frac{17}{4d},\qquad
\frac{\sigma+2}{s}\le\frac3d+\frac{d^2(\log_2(s+2)+3)+35}{s}.
$$

This pays the actual output-dependent issued calls, fixed reserves, and all repeated positions. A child has $f\le e/m$.

For each integer $j\ge4$, put $D=2^j$, $Q_j=3j+\lceil\log_2(3j+3)\rceil+2$, and $S_{j,a}=240(aQ_jD^3+2)$ for $a\in\{1,2,4\}$. At $y\ge S_{j,a}$, $s\ge aQ_jD^3$ and $d\ge D$. For the latter claim write $b=\lfloor u_0/D^3\rfloor\ge Q_j$. One has $b+3\le2^{b-3j}$: it holds at $b=Q_j$ since $4(3j+3)\ge Q_j+3$, and persists by doubling. Therefore $u_0+2<D^3(b+3)\le2^b$ and $D^3v\le D^3b\le u_0$.

Let $A=17/4$, $B=11/3$, $C=10/3$. Starting at $S_{j,1}$, $S_{j,2}$, $S_{j,4}$ respectively, the slope charges $A/D,B/D,C/D$ bound $(\sigma+2)/s$ until the next listed breakpoint. For the first use the first invoice. If $d>D$, the same invoice is at most $17/(8D)$, below all three slopes. If $d=D$, use the second invoice. For $s\ge s_0=aQ_jD^3$, $(\log_2(s+2)+3+35/D^2)/s$ is decreasing, since $1/\ln2<2$. Also

$$
 \log_2(s_0+2)\le3j+\log_2 a+\log_2(Q_j+1)
                 \le Q_j-1+\log_2a.
$$

Here $Q_j+1\le 2(3j+3)$. Since $Q_j\ge18$ and $D\ge16$, the numerator at $s_0$ is at most $Q_j+5\le4Q_j/3$. This gives $(3+4/(3a))/D$, proving the second and third slope estimates. The admissible sequence of slopes decreases strictly, including from $C/D$ to $A/(2D)$.

Define $H(0)=0$ with slope $1/2$ up to $y_A$. The point $y_A$ is between $S_{4,1}$ and $S_{4,2}$. From it use the remaining pieces of this infinite staircase. The resulting $H$ is continuous, increasing and concave. On every adaptive node its right slope $\lambda$ satisfies $\sigma+2\le\lambda s$. Thus $H(y)-H(\log_2 f)\ge\lambda s$ on every true child. Its full sum uses at most one quarter of $V\sqrt e\,2^{H(y)}$. The [existing local ceiling](node-root-parameter.md) is $2V\sqrt e$. Before $y_A$ the potential is precisely $Ve$ when $e\ge1$. The same numerical induction, visited-space accounting and external range adapter therefore give $T_2(V,u)\le5120V\sqrt u\,2^{H(\log_2u)}$ for every $u\ge1$. The explicit zero-width procedure satisfies the displayed general bound as well.

## Uniform envelope at every real logarithmic width

For $j\ge5$ put $h_j=H(S_{j,1})/(240D^2Q_j)$. Direct summation over the three pieces yields

$$
 h_{j+1}=\frac{20}{3}+\frac{Q_j}{4Q_{j+1}}\left(h_j-\frac74\right),
$$

because $A+2B-4C=-7/4$. Direct summation from the first switch gives $h_5=577283/67584<43/5$. The recurrence preserves $h_j\le43/5$, since $Q_j\le Q_{j+1}$ and $20/3+(43/5-7/4)/4<43/5$. If the parenthesis is negative its entire contribution is already nonpositive.

At $S_{j,a}$ one has $\log_2(S_{j,a}+2)\ge Q_j$: use $Q_j\ge3j+3$, $\lceil \log_2(3j+3)\rceil\le\log_2Q_j+1$, and $240>8$. The normalized upper heights at $a=1,2,4$ are therefore controlled by the following three rational inequalities with $C_I=433/8$:

$$
 240c_a^3<C_I^3a^2,\qquad
 (c_1,c_2,c_4)=\left(43/5,\;43/5+A,\;43/5+A+2B\right).
$$

In fact $H(S_{j,a})\le240 D^2Q_j c_a$ and $\Phi(S_{j,a})^3\ge(240aQ_jD^3)^2Q_j$. This checks every breakpoint from $j=5$ onward.

| Earlier breakpoint $z$ | $H(z)$ | Certified lower bound for $\log_2(z+2)$ |
|---:|---:|---:|
| 31,457,760 | 15,728,880 | $124/5$ |
| 35,389,920 | 16,773,360 | 25 |
| 70,779,360 | 24,883,440 | 26 |

At each of these three points $H(z)^3<C_I^3z^2$ times the listed log lower bound. The first lower bound is the exact integer inequality $(31457760+2)^5>2^{124}$. The other two are direct powers of two. All listed rational cubings are reproduced in [the exact checker](../checks/address-native-staircase.py). The weighted geometric mean $a^{2/3}b^{1/3}$ is concave and nondecreasing in its nonnegative arguments, so its composition with $a=y$, $b=\log_2(y+2)$ is concave. Hence $H-C_I\Phi$ is convex on each linear piece. Its two endpoint checks and its value zero at the origin prove $H(y)\le C_I\Phi(y)$ on every $y\ge0$.

## The one changed integer guard

Let $k$ be the global address width, $X=\lceil\log_2(k+2)\rceil$, and $Y=\lceil(X^2\lceil\log_2(X+2)\rceil)^{1/3}\rceil$. Local arities $m=2^y-1$ satisfy $y\le Y$. In the [actual finite enumerator](walsh-node.md), a candidate has at most $m^{55}$ bits, all sixteen vector enumerations cost at most $2^{16m^3}$ tests, and all event, verification and file-traversal factors together are at most $2^{10}m^{129}$. The product including the candidate counter is

$$
2^{m^{55}+1+16m^3+10}m^{129}<2^{m^{56}}
$$

for every admitted nonbase $m\ge 2^{65536}-1$. The setup's $k^{20}$ term is paid separately. The [original common-modulus width guard](walsh-aligned-denominators.md#width-at-the-integer-caller) already holds throughout $X\ge2^{24}$ and gives $Y\le X/64+1$. Consequently $56Y\le(15/16)X\le X-7$ and $m^{56}\le2^{X-7}\le k/32$. Every arity file $m^{55}$, key/denominator file $m^{18}$, and the compact descriptions used in the existing cumulative-space proof fit this same cap.

Also $2000X\le2^{X-7}\le k/32$, by the elementary inequality at integer $X=32$ and induction. Thus $k^{1200}\le2^{k/32}$. In the explicit per-node setup invoice one may replace $2^{m^{128}}$ by $2^{m^{56}}$. Indeed

$$
 m^{60}\big(2^{m^{56}}+k^{1110}+2^{16}(m+1)(k+4)^3\big)
        \le2^{k/4}\le V
$$

for each nonempty role. For the first two terms use $m\le k$ and the preceding $k^{1200}$ bound. For the third use $2^{16}(m+1)(k+4)^3m^{60}\le2^{20}k^{64}$. The original reserve proof gives $V\ge2^{k/3}$ and the existing descriptor-stack high-water proof has the required $m^{55}$ and $2^{k/4}$ bounds. All scalar tables, basis tests and finite selections therefore use their existing physical construction in the widened range. The top-level Walsh branch now calls this constructor from $X=2^{24}$. Its internal direct-width cutoff is already $x<2^{24}$.

Let $x$ be a local Walsh log-width. The [separated movement bill](walsh-node.md#only-actual-column-maps-use-the-interchanger) at the true slot width $f$ contains $m^{17/2}(1+J(f))$, with $f/a\le1/(2m)$. Relative to its parent $\sqrt a$, the square root in $J(f)$ pays $m^{1/2}$, and $m^8\le2^{(33/4)\Phi(x)}$ by the published $y\le(33/32)\Phi(x)$. The remaining interchange exponent is at most $C_I\Phi(x)$. The [complete child quarter](walsh-child-clock.md) already holds at $48\Phi$ and persists on increasing the coefficient. All ordinary events fit $48\Phi$ by the sharpened ordinary invoice, so the complete Walsh exponent is

$$
 B_W=C_I+33/4=499/8.
$$

This also pays the direct whole layer when $X<2^{24}$, since the original direct-width comparison gives $\sqrt k\le2^{48\Phi(X)}$ there. Root placements and outer CRTs use $C_I\le B_W$. The numerical prefactor remains $A_W=2^{110}(1+5120)$; no new operation was added. Thus the [complete integer invoice](../CONSTRUCTION.md) uses $B_W\Phi(X)$ for the three transforms and output.

## All input lengths

Take the raw, dyadic and coprime-box branch thresholds of [the all-length dispatcher](../CONSTRUCTION.md). On the raw branch $n\le2^{48}$ the time is at most $4096n^2\le2^{60}n$, and $63\Phi(x)\ge63$ at $n\ge2$. The bound at $n=1$ uses its existing separate clock.

For the two transform branches put $\ell=\log_2 n$, $z=\log_2\ell$. For the middle branch $5\le z<4097$. The [literal dyadic clock](address-dyadic-words.md) and dispatcher give $T\le2^{61}nk^2$, since $Nk\le16n$ and $(k+1)^3<2k^3$ on this branch. In the logarithm after division by $n\sqrt\ell$, this costs at most $61+(3/2)z$. Up to $z=64$ this is at most 157, whereas $\Phi(z)\ge3$. From 64 through 4097, $z\le512\log_2(z+2)$ by splitting at 2048, so $\Phi(z)\ge z/8$ and $61+(3/2)z\le63\Phi(z)$.

For the coprime-box branch $z\ge4096$. After taking the logarithm in the joined invoice and dividing by $n\sqrt\ell$, the bound is $182+4\log_2(z+2)+B_W\Phi(z+2)$. From the [shifted profile proof](../S008/WholeProfile.lean) one has $\Phi(z+2)\le\Phi(z)+2$. At $z=4096$, $(4098)^8<2^{97}$ and $336(97/8)<4096$. The decreasing log-density then gives $336\log_2(z+2)\le z$ for every larger real $z$. Since $336^2>48^3$, this yields $4\log_2(z+2)\le\Phi(z)/12$. Also $\Phi(z)\ge576$ from $4096^2\cdot12\ge576^3$. Finally

$$
 (63-499/8-1/12)576\ge182+2(499/8)+1 .
$$

This even pays one extra binary exponent bit on all such inputs. Passing from $\ell,z$ to $L,x$ uses monotonicity. The unchanged bank arrangement, the strengthened finite-setup extent, and the [independent cumulative-space count](routing-outer-space.md) give the claimed common $2^{32}n$ cap on the three branches.

The [Lean certificate](../S008/ThreeSlope.lean) proves the actual integer arity eligibility, the exact full-height recurrence, the uniform bound at every member of all three infinite sequences of knot indices, the three earlier real-logarithm comparisons, the interpolation step, and the middle/coprime length inequalities. The correspondence of the native and Walsh resource invoices to the physical program is supplied by the written proofs.
