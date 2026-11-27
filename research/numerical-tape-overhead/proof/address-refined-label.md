# The bit length of a native label

## The actual child invoice

Use $\sigma=\log_2(\sum_iV_i/(V\sqrt m))$ for the complete native child list and $s=\log_2m$. In the notation of [the finite ternary label construction](foundations/characteristic-two-label-geometry.md) and [its audited numerical invoice](child-volume.md), $d\ge16$ is dyadic, $h_0=2d-1$, $t=\lceil (s+2d^2-2)/d^2\rceil$, $q=2^t$, and

$$
 2^\sigma\le2^{33}D_g(1+\lambda),\quad D_g=4+2h_0q^{h_0},\quad
 \lambda\le {h_0\choose d}^{d+1}(q-1)^d t^{d(d-1)} .
$$

The finite $t^{d(d-1)}$ factor here uses the true number of bits per letter. From $D_g\le8h_0q^{h_0}$ and the binomial upper bound $2^{h_0}$,

$$
 \sigma+2\le39+\log_2 h_0+(d+1)h_0+(h_0+d)t+d(d-1)\log_2t.
$$

We have $t\le s/d^2+3$, $\log_2h_0\le d$, and $(d+1)h_0\le 2d^2+2d$. Because $39+12d\le d^2$ at every $d\ge16$, the actual complete invoice satisfies

$$
 \sigma+2\le 3s/d+d^2(\log_2 t+3). \tag{1}
$$

The [kernel-checked cardinality transfer](../S008/TrueLabelCardinality.lean) derives (1) directly from the displayed total mass and binomial/letter alphabet bound for all positive integral bit widths, verifying the logarithm, dimension, degree and multiplicative inequalities. The independent coarse estimate $(\sigma+2)/s\le17/(4d)$ remains available when the actual degree is larger than the guaranteed candidate.

## A continuous concave native majorant

Write $R=240$, $y=\log_2e$, and use the previously proved [integer degree thresholds](address-native-staircase.md). At band $j\ge4$, put

$$
 D=2^j,\quad Q_j=3j+\lceil\log_2(3j+3)\rceil+2,\quad
 S_j=R(Q_jD^3+2),\quad U_j=8Q_{j+1}/Q_j .
$$

If $S_j\le y<S_{j+1}$, let $p=y/R-2$ and $\tau=p/(Q_jD^3)$. Then $1\le\tau<U_j$, $p+1\le s\le p+2$, and the actual degree is at least $D$. Also $Q_{j+1}\le Q_j+4\le2Q_j$, $U_j\le16$, $Q_j/(3j)\to1$, and $U_j\to8$.

In this band define

$$
 E_j=\frac{j+\log_2(8Q_{j+1}+1)+3}{Q_j},\qquad
 \rho(y)=\frac{3+E_j/\tau}{D}.
$$

If the actual $d=D$, then $t\le (p+2)/D^2+3\le D(8Q_{j+1}+1)$, since $p<8Q_{j+1}D^3$ and $D\ge16$. By (1) and $s\ge p$, its one-width charge $(\sigma+2)/s$ is at most $\rho(y)$. If $d>D$, the next possible degree is at least $2D$ and the coarse invoice gives $(\sigma+2)/s\le17/(8D)<3/D$. Thus $\rho$ covers every actual node. We have $0<E_j<2$ and $E_j\to1/3$. For the uniform upper bound use $Q_j\ge18$, $8Q_{j+1}+1\le16Q_j+1\le2^{Q_j-3}$, and $j<Q_j$.

Let $H_*(0)=0$ with slope $1/2$ through $y_A=R(2^{17}+2)$, the existing direct-width cutoff. From there define $H_*$ by integrating the above $\rho(y)$. The switch is inside the $j=4$ band. The new slope there is below $5/16<1/2$. Inside each band it decreases, and at an interband switch the previous left slope is at least $3/D$, while the new right slope is at most $5/(2D)$. Thus $H_*$ is increasing and concave everywhere. Boundaries may use their right slope. For every child $1\le f\le e/m$,

$$
 H_*(y)-H_*(\log_2 f)\ge s\rho(y)\ge\sigma+2 .
$$

This yields the same quarter of the native potential, native direct base, adaptive local charge and external adapter, with $H_*$ as shape. In particular the physical binary caller of positive slot width $u$ still costs at most $5120 V\sqrt u\,2^{H_*(\log_2u)}$. The unbounded function and its logarithms are never evaluated by the machine.
