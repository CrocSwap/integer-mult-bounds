# Counting common-image full guards with row dependencies

Fix a finite field of order $q$, an integer $m\ge2$, a nonzero column $u$, and a nonempty list of rows $v_i$ with $v_i u=1$. Let $V$ be the matrix of these rows, $S=\operatorname{im}V\subseteq\mathbb F_q^k$, $r=\dim S$, and $t=(1,\ldots,1)\in S$. The rows can repeat, and $k$ can exceed $m$. Write $E_i$ for the event that every leading principal minor of orders 1 through $m-1$ of $G(I-u v_i)G^{-1}$ is nonzero. The header $G$ is uniform on the complete $GL_m(\mathbb F_q)$. The order-$m$ determinant vanishes identically.

## The orbit and the denominator

Under a header the pair becomes $(G u,V G^{-1})$. Its image is still $S$, and $V u=t$ still holds. Conversely, for any pair with these properties, fix the same basis of $S$ beginning with $t$, lift its first element by $u$, lift the remaining $r-1$ elements arbitrarily, and append a basis of the kernel. In these domain coordinates all such pairs are identical. Thus the action is transitive. The stabilizer in adapted coordinates has blocks $[I_r,0;T,H]$, with $H\in GL_{m-r}$ and the first column of $T$ zero. Each pair is reached by $q^{(r-1)(m-r)}|GL_{m-r}|$ headers, using $|GL_0|=1$.

Put $d=m-1$. For each of the $q^m-1$ choices of $u'$, choose coordinates with $u'$ last. Its image fixes the final column of $V'$ to $t$. In coordinates on $S$ beginning with $t$, the first row of the other $d$ columns is arbitrary and the remaining $r-1$ rows must be independent. Hence the orbit size is

```text
D_r = (q^m-1) q^d product_{i=0}^{r-2}(q^d-q^i).
```

This counts tuples with a fixed initial representative of the common image vector. Over larger fields there are several representatives of an image line. The constant-fiber argument applies before any quotient by rescaling that vector.

## Which tuples pass?

For the transformed pair write $c_a$ for column $a$ of $V'$, and $y_j=\sum_{a\le j}u'_a c_a$. The rank-one determinant identity gives the $i$-th minor at order $j$ as $1-(y_j)_i$. Indeed the leading block is the identity minus one column times one row, whose determinant is one minus their pairing. All proper prefixes must avoid value one in **every** coordinate. The final prefix equals $t$. Thus $u'_m\ne0$ on the joint event.

For any subspace $\langle t\rangle\le L\le S$, first count tuples with columns contained in $L$, allowing their span to be smaller. Define

```text
h(L) = number of vectors in L having every coordinate nonzero,
lambda(L) = q^dim(L) + (q-1) h(L).
```

At each proper position, a zero $u'_a$ keeps the prefix and allows any of the $q^{\dim L}$ columns. For a fixed nonzero $u'_a$, prescribing the next prefix prescribes exactly one column in $L$. The allowed prefixes in $L$ are counted by $h(L)$, since $y\mapsto t-y$ takes the forbidden-value-one condition to the full-support condition. This count is independent of the preceding allowed prefix. At the last position there are $q-1$ nonzero choices for $u'_m$ and the unique column $(t-y_d)/u'_m$. The number with span contained in $L$ is therefore $(q-1)\lambda(L)^d$. The actual span always contains $t$.

Invert these counts on the interval of subspaces between $\langle t\rangle$ and $S$. The exact probability is

```text
J_S = (q-1) sum_{<t> <= L <= S} mu(L,S) lambda(L)^d / D_r,
mu(L,S) = (-1)^c q^[c(c-1)/2],   c = r-dim(L).
```

For completeness, the displayed Möbius coefficient has value one at $c=0$. In a quotient of dimension $n>0$, its required zero sum is the specialization at $z=1$ of
$\prod_{i=0}^{n-1}(1-q^i z)=\sum_{c=0}^n {n\brack c}_q (-1)^c q^{\binom c2}z^c$.
The polynomial identity follows inductively from multiplying by the next factor using the Gaussian binomial recurrence. The Gaussian coefficient counts the subspaces of each codimension by counting independent ordered bases. This is the classical subspace-lattice inversion. [G.-C. Rota, 1964](https://doi.org/10.1007/BF00531932)

At $q=2$ every $L$ in the interval contains exactly one full-support vector, $t$. For independent rows, expand $(2^{\dim L}+1)^d$. The coefficient of $\binom dj$ after inversion counts $j$ arbitrary columns spanning $S$ together with $t$. The same row count as in the denominator is $2^j\prod_{i=0}^{k-2}(2^j-2^i)$ when $j\ge k-1$, and zero otherwise. This recovers ToikY's binary independent-family formula. [PR #6701](https://github.com/CrocSwap/integer-mult-bounds/pull/6701)

## A pencil and its named pass patterns

Let $v_a=b+a w$, where $bu=1$, $wu=0$, $w\ne0$. Choose $k$ distinct $a$ in the field, $2\le k\le q$. Here $S$ consists of evaluation vectors of the affine polynomials $z_0+az_1$. The constant nonzero evaluations give $q-1$ full-support vectors. For each of $q-1$ nonzero slopes, exactly $q-k$ intercepts avoid a zero at a selected direction. The only proper space containing $t$ is its line. Consequently,

```text
A = q+(q-1)^2,                 B_k = q^2+(q-1)^2(q+1-k),
p = (q-1) A^d / D_1,          J_k = (q-1)(B_k^d-A^d) / D_2 .
```

The marginal is the rank-one-image formula. The formula for $J_k$ also extends algebraically to $k=1$ since $B_1=qA$; set $J_0=1$. At $k=2$ transpose the matrices and replace $G$ by $G^{-T}$, a bijection of complete headers. The marginal and pair formula recover Nick Petalas's prior results. The strict pair sign for every finite field is credited to ToikY. [PR #4227](https://github.com/CrocSwap/integer-mult-bounds/pull/4227) · [PR #4807](https://github.com/CrocSwap/integer-mult-bounds/pull/4807) · [PR #6703](https://github.com/CrocSwap/integer-mult-bounds/pull/6703)

The probability of any specified exact pass mask with $j$ ones is
$\sum_{i=0}^{k-j}(-1)^i\binom{k-j}{i}J_{j+i}$ by inclusion-exclusion. For $1\le j<k$, put $f=k-j$. The constant $A^d$ cancels. Apart from the positive factor $(q-1)/D_2$, the remaining sum counts words of length $d$ over a background alphabet of size $B_k$ with $f$ additional disjoint classes of size $(q-1)^2$, requiring every additional class to appear. Indeed $B_{j+i}=B_k+(f-i)(q-1)^2$. The count is positive exactly when $f\le d$. For $j=k$, the joint probability is positive directly. For $j=0$ the full inclusion-exclusion expression applies, including $J_0=1$. The empty pass mask is attainable by placing $u=e_1$ with the normalized rows and using the identity header.

## A comparison with independent covectors

For three independent rows, $S=\mathbb F_q^3$. There are $q+1$ planes through $t$. Every such plane is spanned by $t$ and a nonconstant vector. Its number of full-support vectors is $(q-1)(q+1-j)$, where $j$ is the number of distinct coordinates of that vector, by the same affine count. Exactly three planes impose equality on a specified pair of coordinates and have $j=2$; the other $q-2$ have $j=3$. In particular,

```text
C = q^3+(q-1)^4
J_ind,3 = (q-1)[C^d-3B_2^d-(q-2)B_3^d+q A^d]/D_3,   m >= 3.
```

At $q=4,m=61$, exact integer comparison gives $J_{\rm ind,3}>p^3>J_3$. All three marginal and pair laws agree across these two families. Their common complete-header distribution does not determine a triple from its pair marginals. The precise integer ratio bounds are in RESULT.json.

More generally $\lambda(S)>\lambda(L)$ for every proper $L$ in the interval. For fixed $S,q$, as $m\to\infty$,
$J_S\sim (q-1)q^{-1}[\lambda(S)/q^{r+1}]^d$.
For $S=\mathbb F_q^k$, the base equals $q^{-1}+(1-q^{-1})^{k+1}$. This is $\mathbb E[X^k]$ when $X=1$ with probability $1/q$, $X=1-1/q$ otherwise. For $k\ge2$ strict convexity gives $\mathbb E[X^k]>(\mathbb E[X])^k$. Thus independent rows eventually give a joint probability above $p^k$ for each fixed field and $k$.

## A dimension-uniform lower bound and complete affine flats

There is a simple event that passes **every** member of any normalized common-image family. If $G u$ is a nonzero multiple of the last coordinate vector, all proper leading blocks are identity. Uniform $G u$ therefore gives
$J_S\ge b_m=(q-1)/(q^m-1)$. Set $t_1=1-1/q+1/q^2$ and $c_m=(1-1/q)/(1-q^{-m})<1$. The marginal and this lower bound can be written as $p=c_m t_1^d$ and $b_m=c_m q^{-d}$. Consequently

~~~text
if k >= 2 and t_1^k <= 1/q, then J_S >= b_m > p^k, for every m.
~~~

This sufficient size condition applies to arbitrary row dependencies. For $q=2$ it holds already at $k=3$, since $(3/4)^3<1/2$. With the prior distinct-pair result (or $p>p^2$ for identical events), this proves strict positivity for every binary normalized family of at least two guards. The same last-coordinate event holds under each uniform determinant stratum.

In particular, consider **all** $q^{r-1}$ affine directions $(1,a_1,\ldots,a_{r-1})$ in rank $r$. For $r\ge3$, the inequality $t_1^{q^2}\le \exp(-(q-1))<1/q$ proves strict positivity for every field and every $m\ge r$. This contrasts with the rank-two full pencil, which is strictly below its product everywhere for $q\ge7$.

The full flat also has a closed count. For any $L$ in the subspace interval, the only coefficient vectors with nonzero evaluations at every point are the $q-1$ nonzero constants: every nonconstant affine linear function on the complete space attains zero. Hence $h(L)=q-1$ throughout. Expand $(q^{\dim L}+(q-1)^2)^d$ by the binomial theorem and invert termwise as in the binary specialization. For $A_{r,j}=q^j\prod_{i=0}^{r-2}(q^j-q^i)$ at $j\ge r-1$ and $A_{r,j}=0$ otherwise,

~~~text
J_flat = (q-1) sum_{j=r-1}^d binom(d,j) (q-1)^[2(d-j)] A_{r,j} / D_r .
~~~

At $m=r$ only $j=d$ remains, so $J_{\rm flat}=b_m$ exactly. For $r\ge3$, the mass of headers that send $u$ to the last axis alone strictly exceeds the independence prediction. AFFINE-PLANES.json checks all subfamilies at rank three, including this equality for the full flat.

## A restricted distribution covered by the count

For any nonzero determinant $z$, left multiplication of a header by $H=\mathrm{diag}(z,1,\ldots,1)$ moves it bijectively to the corresponding determinant stratum. Each conjugated leading block is then diagonally similar to its original, so its determinant is identical. Hence **every named mask**, including for other projector families, has the same distribution in each uniform determinant stratum as under complete uniform $GL_m$. This covers uniform $SL_m$ and arbitrary mixtures of the uniform strata. Arbitrary restricted headers can behave differently. In the pencil with $u=e_1$, the identity fails every first minor, while a coordinate permutation sending $e_1$ last passes every proper minor.
