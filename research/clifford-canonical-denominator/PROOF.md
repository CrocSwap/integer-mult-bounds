# Canonical odd denominator at the first four-qubit width

Let $R=\mathbb Z[i,1/2]$. The odd denominator of a Gaussian-rational matrix $B$ is the least positive odd integer $d$ such that $dB$ has entries in $R$. Choose one Gaussian-dyadic unitary $U_a$ per scalar coset of the full four-qubit Clifford group, and put $N=12,128,668,876,800$. Let $A$ have the $N$ columns $\operatorname{vec}(U_a^{\otimes13})/4^{13}$. Write $K=A^*A$ and $J=K^{-1}A^*$.

**Theorem.** The odd denominator of $J$ is
$$
D=22{,}742{,}436{,}009{,}630{,}709{,}072{,}767{,}882{,}717{,}680{,}300{,}149{,}753{,}125.
$$
The least odd denominator among *all* norm-optimal left inverses is $470,624,175$ by [PR #7802](https://github.com/apoursh/integer-mult-bounds/blob/ebe2c019e398d73444e4f33f2d71bd5775795a01/research/clifford-dyadic-noise-floor/PROOF.md). The much larger $D$ measures the cost in odd factors of choosing the canonical operator.

## 1. Transfer to a central kernel

The [width-13 splitting](https://github.com/apoursh/integer-mult-bounds/blob/7f08a74037788311cc6b7da27297b25f1b188e45/research/clifford-bell-fibres/PROOF.md) supplies a matrix $L$ over $R$ with $LA=I$. For every positive odd integer $d$,
$$
dK^{-1}\in R^{N\times N}\quad\Longleftrightarrow\quad dJ\in R^{N\times 256^{13}} .
$$
The forward implication multiplies on the right by $A^*$ and the reverse implication multiplies on the right by $L^*$. This permits a calculation on the inverse Gram kernel. Changing the scalar lift of a column conjugates $K$ by a diagonal Gaussian unitary and multiplies the corresponding rows of $J$ by units, so the denominator is intrinsic to the projective alphabet.

Let $S=\mathrm{Sp}(8,2)$, the quotient by the Pauli subgroup, and let $V$ be the defining 16-dimensional Clifford module. In the scalar sector of $V^{\otimes13}$ the irreducibles are $V\otimes\rho$, one for every quotient irreducible $\rho$. Write $d_\rho=\dim\rho$ and $\lambda_\rho$ for the corresponding positive eigenvalue of $K$. The 81 rows, their multiplicities and their normalizations come from Ali Romman's threshold computation and Nick Petalas's projected character data. At width 13, $V^{\otimes13}=V\otimes W$ for an inflated $W$ with integer character $(-64)^k$ on symplectic elements having fixed-space dimension $k$. Hence the character of $W$ is rational, and Galois-conjugate quotient characters occur in $W$ with equal multiplicities. [Width-13 decomposition and spectrum](https://github.com/aliromman/integer-mult-bounds/blob/1398fbdca3536389d8ac3c8b3aaa408f03e8f6c2/research/clifford-threshold-conditioning/PROOF.md) · [Odd-sector character and phases](https://github.com/aliromman/integer-mult-bounds/blob/9a8ce06644700ffa576d99316450bcb52835d6dc/research/clifford-odd-width-spectrum/PROOF.md)

For $g=U_a^*U_b$ let $s$ be its symplectic image. Matrix-coefficient orthogonality gives the entries
$$
K^{-1}(a,b)=\frac{16\,\operatorname{tr}(g)}{N}
              \sum_\rho \frac{d_\rho}{\lambda_\rho}\,\chi_\rho(s).
\tag{1}
$$
Indeed the projector for $V\otimes\rho$ has kernel $(16d_\rho/N)\operatorname{tr}(g)\chi_\rho(s)$. To multiply two such kernels one may average over all lifts in the finite Clifford group because the central phases contributed by the two factors at the intermediate index cancel. Schur orthogonality then gives idempotence within each block and zero products between distinct blocks. Their ranks $(16d_\rho)^2$ sum to $N$. In the Gram kernel $\operatorname{tr}(g)^{13}/16^{13}$ a multiplicity $m_\rho$ therefore gives $\lambda_\rho=N m_\rho/(16^{13}\cdot 16d_\rho)$. Replacing each block scalar by its reciprocal yields (1). The identity entry uses $\operatorname{tr}(I)=16$. All traces in (1) are evaluated with the displayed lift of $g$.

## 2. A common upper bound and the diagonal divisor

Let $T$ be the least common multiple of the reduced numerators of the 52 distinct $\lambda_\rho$, and set $b_\rho=T d_\rho/\lambda_\rho\in\mathbb Z$. Write $\operatorname{odd}(x)$ for the positive odd part of a positive integer. The odd part of $N$ is $722,925$. Exact arithmetic on the 81 source rows gives

| Quantity | Value |
|---|---:|
| $T$ | 2674007761273451977985641706958295138125 |
| $\gcd_\rho b_\rho$ | 91268055040 |
| $\operatorname{odd}(\gcd_\rho b_\rho)$ | 85 |
| Common odd denominator of $16b_\rho/(NT)$ | $8505T=D$ |

This last denominator is an upper bound for all entries in (1). Characters of finite groups are algebraic integers, including the trace of $g$. Multiplying by $D$ clears the odd denominators of the scalar coefficients. Multiplying further by a suitable power of two gives a sum of algebraic integers. Each entry already belongs to $\mathbb Q(i)$ by inversion of $K$, so after this multiplication it is in $\mathbb Z[i]$, the ring of integers of $\mathbb Q(i)$. This argument allows quotient characters with nonrational values.

The diagonal entry is independent of $a$ and equals
$$
K^{-1}(a,a)
=\frac{1}{N}\sum_\rho\frac{(16d_\rho)^2}{\lambda_\rho}
=\frac{8084515602799097617265541791880056776818688}{7580812003210236357589294239226766716584375}.
$$
Its reduced odd denominator is $D/3$. The eigenvalue numerators alone account for $T=D/8505$.

## 3. The order-17 entry

Use the literal operator $U$ of [PR #6208](https://github.com/apoursh/integer-mult-bounds/blob/4e3f55105e436dfa364029f9032c90f6a239fbe0/research/order-seventeen-clifford/PROOF.md). It has trace $-1$, order 17, and a nonidentity symplectic image $s$ of order 17. The binary space $E$ of dimension eight is irreducible for $s$: the order of 2 modulo 17 is eight, so every nontrivial 17th root already needs degree eight. Consequently the linear centralizer of $s$ consists of multiplications by nonzero elements of $\mathbb F_{256}=\mathbb F_2[s]$. Adjoint for the symplectic form acts on that field as the sixteenth-power map, since it sends $s$ to $s^{-1}=s^{16}$. Multiplication by $u$ preserves the form exactly when $u^{17}=1$. Thus $|C_S(s)|=17$. The independent checker also enumerates all 256 linear maps commuting with the explicit binary action and finds exactly 17 symplectic ones.

Group the 81 quotient characters by their pair $(d_\rho,\lambda_\rho)$. Equal degree and multiplicity give equal eigenvalue, and conversely equal degree and eigenvalue give equal multiplicity. Section 1 shows that each such packet $B$ is Galois-stable; it may contain several orbits. There are 79 singletons and one packet of size two. The packet character $\psi_B=\sum_{\rho\in B}\chi_\rho$ takes integer values because it is both rational and algebraic integral.

Put $m=|B|$ and let $d$ be its common degree. On the cyclic subgroup generated by $s$, the rational character has equal multiplicities for all 16 nontrivial 17th roots. Indeed Galois automorphisms permute these root characters transitively and fix the restricted character. If the common multiplicity is $h$ and the trivial multiplicity is $h_0$, then $md=h_0+16h$ and $\psi_B(s)=h_0-h$. Combining this congruence with column orthogonality gives
$$
\psi_B(s)\equiv md\pmod {17},\qquad
|\psi_B(s)|^2\le m\sum_{\rho\in B}|\chi_\rho(s)|^2
               \le 17m .
$$
Here $m\le2$, so the interval has length at most $2\sqrt{34}<17$. Each packet value is the unique integer in this interval with the required residue. Among the 80 packet values, five are $+1$, four are $-1$ and 71 are zero. Substitution in (1) with $U_a=I$, $U_b=U$ gives
$$
K^{-1}(I,U)=\frac{-309891064832}{22949540428586199553125}.
$$
This fraction is reduced. Its denominator has 3-adic valuation 12, one greater than that of the diagonal denominator. Their least common multiple is $D$. Together with Section 2 this proves the theorem. Rephasing either representative multiplies the off-diagonal entry by a fourth root of unity and preserves this divisor.

## 4. Independent local check

The second checker reconstructs all $\lambda_\rho$ using the fixed-space projection in [PR #7747](https://github.com/petalas/integer-mult-bounds/blob/ff12ca358d601a21cd4b1f016b8a3a969ac44016/research/clifford-four-qubit-width-nine/PROJECTION.json) and the integer character of $W$. It obtains $b_\rho\equiv0\bmod 3$ except in the two rows of degrees 35 and 238, where both residues equal one. Both degrees occur once, so their characters are rational. Their values at $s$ are $1$ and $0$, respectively, by the congruence and bound above. In the algebraic-integer ring containing all character values, the numerator of $NTK^{-1}(I,U)$ is therefore congruent to $-16\equiv2\bmod 3$. Thus it is prime to 3 at the rational level, while $NT$ contains $3^{12}$. This verifies the missing prime power without using the reported spectrum or the other 78 packet values at $s$.

The construction classifies common odd denominators of entries. An implementation may factor or share divisions differently. The result gives no operation count, fixed-tape algorithm, or improvement of the selected multiplication exponent.
