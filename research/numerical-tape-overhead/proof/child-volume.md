# Numerical charge of the adaptive interchange children

Let $V$ be the encoded bit volume of a native ternary interchange of width $e$. Set $s=\log_2m$, $l=\log_2(s+2)$ and $\Phi(s)=(s^2l)^{1/3}$. Use the odd arity and integer schedule of [adaptive interchange](foundations/adaptive-interchange.md).

**Child-volume theorem.** For every odd arity with $s\ge2^{17}$ and positive child width $f$, the actual volumes, with repetitions, satisfy

$$
 \sum_i V_i\le V\sqrt m\,2^{10\Phi(s)}. \tag{1}
$$

This counts the recursive calls. The local transitions and the outer integer caller have separate bills.

## Actual children

Put $u=\lceil s\rceil$, $v=\lceil\log_2(u+2)\rceil$, and let $d$ be the largest dyadic integer with $d^3v\le u$. Set $h_0=2d-1$, $t=\lceil(s+2d^2-2)/d^2\rceil$, $q=2^t$, $N=q^{h_0^2}$, $D_g=4+2h_0q^{h_0}$ and $a=D_g-2$. The [label proof](foundations/characteristic-two-label-geometry.md) gives $mr/N\le1$ and

$$
 \lambda\le {h_0\choose d}^{d+1}(q-1)^d t^{d(d-1)}.
$$

One [shared pencil](foundations/uniform-payload-shared-pencil.md) charges at most $R_{\rm pen}=2^{22}D_g(1+\lambda)(1+mr/N)$ calls per independent row. The constant includes repeated destination preparation. See the [geometric list audit](foundations/review-explicit-dyadic-geometry.md). Each predictor has at most $D_p\le24\sqrt m$ factors. There are two predictors per finite internal node. Four sequential phases each act on one sixteenth of the incoming volume, to depth $h=\lceil s/4\rceil$. Across the three order-three words, the internal charge is at most $3(2D_pR_{\rm pen})\sum_{j<h}4^{-j}\le8D_pR_{\rm pen}$. The $4^h$ leaves per word have relative size $16^{-h}$ and $m$ swaps apiece. Multiply the main charge by its leading padding $1\le\beta<2$. Unpad before all $2a$ reserve calls of size $V$. Thus

$$
 \sum_i V_i\le V\Lambda,\qquad \Lambda=\beta(8D_pR_{\rm pen}+3m4^{-h})+2a .
$$

This uses the [finite repair](foundations/compact-spectral-repair-executor.md), [bijective field packing](foundations/full-rate-field-packing.md) and [leading-row layout](foundations/packed-batch-with-small-radix.md). Each main child has at most $\beta V/N$ or $\beta16^{-h}V$, both at most $V/2$. The rank guard, $4^{-h}\le m^{-1/2}$ and $a\le D_g$ give

$$
 \Lambda/\sqrt m\le(768\cdot2^{22}+8)D_g(1+\lambda)\le2^{33}D_g(1+\lambda). \tag{3}
$$

## Native volume estimate

For $s\ge2^{17}$, $l\le v\le l+2\le(9/8)l$, $s\le u\le s+1\le2s$, and $16\le d\le(2s/l)^{1/3}$. Indeed $s/(\log_2(s+2)+2)$ increases on this range and starts above $16^3$. Maximality gives $d>(u/v)^{1/3}/2$, hence $s/d\le(9/4)\Phi(s)$ and $d^2l\le2\Phi(s)$. Also $t\le s/d^2+3\le s$. Consequently $\log_2N\le4s+12d^2\le5s$ and

$$
 \log_2D_g\le2+\log_2 h_0+h_0t\le2s/d+8d\le s/4.
$$

For the last step use $d\ge16$ and $64d\le s$. Bound the binomial coefficient by $2^{h_0}$. Taking logarithms in (3) gives

$$
 \log_2(\Lambda/\sqrt m)\le33+3s/d+d^2l+2d^2+13d+1
 \le33+3s/d+d^2(l+3). \tag{4}
$$

Here $13d+1\le d^2$. Since $33\le\Phi(s)/4$ and $1/4+27/4+2+6/17<10$, (4) proves (1).

## Rounded width and a quarter of the adaptive clock

For any integer $R\ge72$, let $m$ be the largest odd integer at most $e^{1/R}$. Put $E_R=2^{R(2^{17}+2)}$. For $e\ge E_R$, $e^{1/R}/2\le m\le e^{1/R}$ and $s\ge2^{17}$. The [unfolded carry bound B5](foundations/characteristic-two-count-formula.md) costs at most $512m^5$ syntax nodes per offset bit. There are at most $m$ bits since $D_p\le m$. The factored product, scalar weights, and at most two explicit pads per binary gate give at most $2^{13}m^6\le m^7$ nodes. Each sum introduces at most one grade field of at most $\log_2m$ bits. Thus $\log_2w\le m^8$ for the module width. The other factors are the field width $h_K\le m$, $16^h\le16m\le m^2$, $N\le m^5$, $32\le m$, and shift count $B<6m+3\le m^2$. Therefore

$$
 \ell=\lceil\log_3(h_K16^hN32Bw)\rceil\le1+11s+m^8\le m^9\le e^{1/8}.
$$

In the rounded width $f=\lfloor(e-\ell)/(m+2a)\rfloor$, $a\le m^{1/4}$, $e-\ell\ge e/2$, $m+2a\le3m$, and $e/m\ge24$. It follows that

$$
 e/(8m)\le f\le e/m,\qquad \log_2f\le\theta\log_2 e,\qquad \theta=1-1/(2R).
$$

For the last inequality use $\log_2m\ge(\log_2e)/R-1$ and $\log_2 e\ge2R$.

The [three-slope proof](address-native-staircase.md) uses the complete child mass in (4), including the full reserves, and this rounded width.
