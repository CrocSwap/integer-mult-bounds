# The exact arithmetic cost of the optimal noise norm

## 1. A split finite matrix

Let $R=\mathbb Z[i,1/2]$, and let $A\in R^{M\times N}$ have a left inverse $L\in R^{N\times M}$. Write $K=A^*A$, $J=K^{-1}A^*$ and $\lambda=\lambda_{\min}(K)>0$. All norms are Euclidean operator norms. Suppose the least eigenvalue is rational. Since $K$ has dyadic Gaussian entries, its rational eigenvalues are dyadic: multiply $K$ by a power of two to clear denominators. A rational eigenvalue of the resulting integral Gaussian matrix is an algebraic integer (use its monic characteristic polynomial and the coefficientwise conjugate), hence an integer. Write $\lambda=m/2^e$ in lowest terms when its reduced numerator $m$ is odd; below we use this notation for the Clifford widths, where $0<\lambda<1$. For a Gaussian-rational matrix $D$, its **odd denominator** is the least positive odd integer $d$ with $dD\in R^{N\times M}$.

For any exact left inverse $D$, let $C=D-J$. Then $CA=0$ and

```text
DD* = K^(-1) + CC* .
```

Indeed $CJ^*=CAK^{-1}=0$. Thus $1/\lambda$ is the minimum over complex left inverses of the squared noise norm. Equality forces $C^*x=0$ on the entire bottom eigenspace $E=\ker(K-\lambda I)$. In particular $Ax=\lambda D^*x$ there. The proof allows noncanonical minimizers.

**The sharp odd denominator is $m$.** The equations for $E$ have coefficients in $\mathbb Q(i)$, so choose a nonzero vector $x\in E\cap\mathbb Z[i]^N$, primitive by dividing out the Gaussian gcd of its coordinates. If $D$ attains the minimum and $dD$ is Gaussian dyadic, then
```text
d x = L(d Ax) = (m/2^e) L (dD*)x .
```
Every component of $dx$ belongs to $mR$. A Gaussian-integer Bézout combination of the coordinates of $x$ is 1, so $d\in mR$. Odd integer denominators satisfy $m\mid d$.

For sufficiency, begin with $L$ and make one correction
```text
T = (I - K/λ) L + A*/λ .
```
Then $TA=I$, $mT$ is Gaussian dyadic and $T-J=(I-K/\lambda)(L-J)$. Its range is orthogonal to $E$. Choose a dyadic $h>0$ with $h\|K\|<1$. From $T_0=T$ iterate $T_{j+1}=(I-hK)T_j+hA^*$. Each iterate has $T_jA=I$, $mT_j\in R^{N\times M}$, and error $C_j=(I-hK)^j(T-J)$. This error has range in $E^\perp$ and tends to zero. If $E^\perp$ is nonempty and $\lambda_2$ is the next distinct eigenvalue, choose a finite $j$ with $\|C_j\|^2\le 1/\lambda-1/\lambda_2$. In $T_jT_j^*=K^{-1}+C_jC_j^*$, the two subspaces $E,E^\perp$ reduce both summands. The former has exact eigenvalue $1/\lambda$, and the largest eigenvalue on the latter is at most $1/\lambda$. If all levels coincide, $T=J$ already. This constructs an exact norm minimizer with denominator dividing $m$, which proves sharpness. The step count uses the finite spectral gap and supplies no cost bound uniform in dimension or width.

## 2. Optimal convergence as coefficient precision increases

Write $g_s=\min_{DA=I,\,2^sD\in\mathbb Z[i]^{N\times M}}\|D\|^2-1/\lambda$ for a fixed matrix $A$ and $s\ge0$. Once the lattice contains $L$, the minimum exists: a bounded operator-norm ball contains only finitely many lattice points. Assume $m>1$.

Choose $a\ge0$ with $2^aA$ integral, and a primitive bottom vector $x$ as above. For any candidate $D$ at precision $s$, the residual $v=Ax-\lambda D^*x$ is nonzero: equality and $LA=I$ would put $x\in mR^N$. Also $2^{\max(a,e+s)}v$ is Gaussian integral. Since $v=-\lambda C^*x$, evaluation of $DD^*$ on $x$ gives the explicit lower bound
```text
g_s >= 1 / (λ² ||x||² 4^max(a,e+s)).
```
For $s\ge a-e$ this becomes $4^{-s}/(m^2\|x\|^2)$.

Conversely fix $b,t\ge0$ for which $2^b L$ and $2^t P$ are integral, where $P=I-AL$. For $s\ge\max(b,t)$, round the real and imaginary components of $J$ to their nearest multiples of $2^{t-s}$, producing $H$. Set $D=L+HP$. Because $PA=0$, $JA=I$, and $L+JP=J$, this is an exact left inverse on the required grid, with $D-J=(H-J)P$. Entrywise rounding and the Frobenius bound give
```text
||D-J|| <= sqrt(MN/2) 2^(t-s) ||P|| ,
g_s <= (MN/2) 4^t ||P||² 4^(-s).
```
The second inequality uses the orthogonal error identity of §1. Together these bounds show $g_s=\Theta_A(4^{-s})$. Thus unrestricted Gaussian-dyadic decoders approach but never attain the optimal norm when $m>1$. Precision here measures coefficient denominators in an explicit matrix, not internal word length or movement in a circuit.

## 3. Four-qubit least eigenvalues at every full-rank width

Use the Gaussian-dyadic Clifford group $G$, Pauli subgroup $P_0$, scalar subgroup $Z=\langle iI\rangle$, and defining 16-dimensional module $V$. The $N=12,128,668,876,800$ columns of $A_f$ are $\operatorname{vec}(U_a^{\otimes f})/4^f$ over scalar cosets. The normalized Gram kernel is $K_f(a,b)=(\operatorname{tr}(U_a^*U_b)/16)^f$. A different lift changes a column only by a Gaussian unit. The [splitting proof](https://github.com/apoursh/integer-mult-bounds/blob/7f08a74037788311cc6b7da27297b25f1b188e45/research/clifford-bell-fibres/PROOF.md) supplies $L_fA_f=I$ over $R$ for every integer $f\ge13$.

For odd $f\ge13$, take both endpoints from the [odd-sector proof](https://github.com/aliromman/integer-mult-bounds/blob/9a8ce06644700ffa576d99316450bcb52835d6dc/research/clifford-odd-width-spectrum/PROOF.md), with its polynomials $P,Q$. For $f\equiv 2\pmod4$, $f\ge14$, the [Bell-sector proof](https://github.com/aliromman/integer-mult-bounds/blob/a5aa2ae21ae68338390f584b8fca58ecba0df409/research/clifford-bell-sector-spectrum/PROOF.md) supplies them as $H(-2^{-(f-2)/2}),H(2^{-(f-2)/2})$. In particular these endpoints are rational.

**When $4\mid f$, both endpoints coincide with those at $f-1$.** For fixed representatives $K_f=K_{f-1}\circ K_1$ (entrywise product). The Schur product with the positive semidefinite unit-diagonal $K_1$ is positive and fixes $I$. Applying it to the Loewner bounds for $K_{f-1}$ puts every eigenvalue of $K_f$ between the previous endpoints.

For the reverse inclusion, write $S=G/P_0$. At the preceding width $f-1\equiv3\pmod4$ the [odd-sector decomposition](https://github.com/aliromman/integer-mult-bounds/blob/9a8ce06644700ffa576d99316450bcb52835d6dc/research/clifford-odd-width-spectrum/PROOF.md) gives $V^{\otimes(f-1)}=\bar V\otimes W$ with $W$ inflated from $S$. Each quotient irreducible $\rho$ of dimension $d$ and multiplicity $k$ in $W$ corresponds to the block $\bar V\otimes\rho$ of degree $16d$; these exhaust the preceding central sector. At width $f$ we have $\operatorname{End}(V)\otimes W$. The Pauli invariants in $\operatorname{End}(V)$ are exactly the scalar operators, by irreducibility of the Pauli action. Thus the Pauli-invariant subspace is precisely $W$, and the inflated $\rho$ occurs in the full module with exactly the same multiplicity $k$. The same invariant component appears in the [width-twelve analysis](https://github.com/aliromman/integer-mult-bounds/blob/ff9bdc0e82e75ab5ed39f3ff034ac8ddb3ea06d2/research/clifford-width-twelve-nullity/PROOF.md).

For completeness, a degree-$d'$ block of multiplicity $k$ in $V^{\otimes w}$ gives a projective Gram eigenvalue $Nk/(16^w d')$. Indeed the Gram matrix evaluates the central kernel $\chi_{V^{\otimes w}}(g)/16^w$. Under the finite-group matrix-coefficient orthogonality relations the convolution on that block acts by $|G|k/(16^w d')$; summing over scalar representatives instead divides by $|Z|$, since the scalar phases of the kernel and coefficient cancel. Consequently
```text
N k / (16^f d) = N k / (16^(f-1) (16d)).
```
Every preceding eigenvalue survives in the neutral sector, although regular block dimensions change. Together with the interval inclusion this proves endpoint equality without enumerating the other neutral blocks.

The least eigenvalues at widths 13, 14 and 15 are respectively
```text
470624175/2^32,   5741614935/2^35,   75707742285/2^38.
```
Width 16 repeats width 15. At width 17 the minimum is $37674563331825/2^{46}>1/2$. Monotonicity above holds for every width increment. The diagonal of each $K_f$ is 1 and $K_f\ne I$, since $I$ and the one-qubit phase gate tensored with three identities have nonzero overlap. A Hermitian matrix of average eigenvalue 1 whose minimum is at least 1 must be $I$. Hence $1/2<\lambda_{\min}(K_f)<1$ for all finite $f\ge17$. Its rational dyadic value cannot have reduced numerator 1. The four initial values also have odd numerator greater than 1. Sections 1–2 therefore apply at **every** $f\ge13$, including multiples of four.

## 4. A concrete bottom vector at width thirteen

At width 13 the minimum block is the defining $V$ times the trivial quotient row. Take $x_a=\overline{\operatorname{tr}(U_a)}$. This conjugate character lies in that block: substituting $U_b=\zeta U_aU_h$ in $K_{13}x$ cancels scalar phases because $13\equiv1\pmod4$. The sum of $\operatorname{tr}(U_h)^{13}\bar U_h$ is scalar by conjugation invariance after extending the sum to all lifts. Its scalar divided by $16^{13}$, with the coset normalization, is the defining-block eigenvalue from §3. Character orthogonality gives $\sum_a|x_a|^2=N$. The [Gaussian trace argument](https://github.com/aliromman/integer-mult-bounds/blob/9a8ce06644700ffa576d99316450bcb52835d6dc/research/clifford-odd-width-spectrum/PROOF.md) gives Gaussian-integer coordinates, and the identity coset has trace a unit times 16. Thus $x\notin mR^N$ for every odd $m>1$, which suffices in §2.

Each column of $U_a$ is a four-qubit stabilizer state with affine support $2^r$, $0\le r\le4$, of constant nonzero squared magnitude $2^{-r}$. For a Gaussian dyadic number of this magnitude the equation for the sum of two squares forces either an axial coordinate of magnitude $2^{-r/2}$ (even $r$) or two coordinates of magnitude $2^{-(r+1)/2}$ (odd $r$). This follows by removing common factors of 2 and reducing modulo 4. Thus $4U_a$ is Gaussian integral and $2^{52}A_{13}$ is integral. With $e=32$ we obtain, for $s\ge20$ at which a grid inverse exists,
```text
||D||² - 2^32/470624175 >= 4^(-s)/(12128668876800 · 470624175²).
```

Ali Romman's [canonical obstruction](https://github.com/aliromman/integer-mult-bounds/blob/9321c67e29c3c41a188154bc5c2add7d7802b694/research/clifford-odd-division-obstruction/PROOF.md) gives a necessary odd divisor for the Moore–Penrose coefficients from a selected eigenvalue. That obstruction alone cannot extend to every minimizer: a noncanonical inverse can attain the same spectral norm, as the verifier demonstrates. The dyadic splitting and the *least* eigenspace supply the missing implication here. Our sharp denominator applies to the best choice among all norm-minimizing inverses. Computing the odd denominator of the canonical matrix itself is a separate multiple-block problem. No four-qubit dense matrix or complete circuit is constructed.
