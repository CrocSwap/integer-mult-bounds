# The even-width five-qubit canonical decoder

Let $R=\mathbb Z[i,1/2]$. Let $H$ be the five-qubit Gaussian-dyadic unitary Clifford group, $Z=\langle iI\rangle$ its scalar center, $P$ the Pauli group, $E=P/Z=\mathbb F_2^{10}$ the symplectic label space, $V$ the natural module of dimension $q=32$, and $G=H/P=\operatorname{Sp}(10,2)$. Fix a lift $U_a$ of each of the $N=q^2|G|$ scalar cosets. Take raw columns $A_f(:,a)=\operatorname{vec}(U_a^{\otimes f})$, Gram $K_f=A_f^*A_f$ and Moore–Penrose left inverse $J_f=K_f^{-1}A_f^*$. For even $f\ge16$, put
$$
r=(f-2)/2,\qquad t=(-1)^{\lfloor f/4\rfloor}2^r,\qquad k(s)=\dim\ker_E(s-1).
$$
Write $D_f$ for the least positive odd integer with $D_fJ_f$ over $R$. These widths admit an $R$-left inverse $L_f$ by the five-qubit splitting theorem. Hence $D_f$ is also the odd denominator of $K_f^{-1}$, by $J_f=K_f^{-1}A_f^*$ and $J_f L_f^*=K_f^{-1}$. Dividing $A_f$ by $q^{f/2}$ changes matrices by units of $R$ here. [Five-qubit splitting](https://github.com/apoursh/integer-mult-bounds/blob/9cdeb734ea8d0e6ddf3914dd92b6ced5046a6910/research/clifford-five-qubit-modular-seed/PROOF.md)

## 1. Two integral corners in each even sector

The odd-width Pauli decomposition applied at $f-1$ gives $V^{\otimes f}=B\otimes W$, with $B=V\otimes\bar V$ for $4\mid f$ and $B=V\otimes V$ for $f\equiv2\pmod4$. Here $W$ is inflated from $G$ and $\chi_W(s)=t^{k(s)}$. Indeed a lift of $s$ with nonzero trace $a$ exists, and $|a|^2=2^{k(s)}$, $a^4=(-1)^{k(s)}2^{2k(s)}$. Dividing $a^{f-1}$ by $\bar a$ or $a$, respectively, gives the stated sign. Losing this sign swaps the ordering in two of the four even residues modulo eight. [Odd-sector decomposition](https://github.com/aliromman/integer-mult-bounds/blob/9a8ce06644700ffa576d99316450bcb52835d6dc/research/clifford-odd-width-spectrum/PROOF.md) · [Five-qubit trace and orbit proof](https://github.com/apoursh/integer-mult-bounds/blob/b42e665721e76e69d05f24a19bdabee0e0f77c04/research/clifford-five-qubit-threshold/PROOF.md)

The unnormalized vectorized real Weyl matrices form $q^2$ one-dimensional $P$-weight spaces in $B$. In $\operatorname{End}(V)$ they have commutation weights $p\mapsto(-1)^{[p,u]}$. They split into orbits of sizes $1,1023$, with stabilizers $G,P_5$, where $P_5$ fixes a nonzero vector in $E$. In $V\otimes V$ the Hermitian lift of $p=(a,b)$ instead has weight $(-1)^{a\cdot b+[p,u]}$. The symplectic group transports the resulting quadratic refinements. Their Arf types give orbit sizes $528,496$ and stabilizers $K_+,K_-$, the full orthogonal groups (ATLAS names O10+(2).2 and O10-(2).2). [Bell-sector construction](https://github.com/aliromman/integer-mult-bounds/blob/a5aa2ae21ae68338390f584b8fca58ecba0df409/research/clifford-bell-sector-spectrum/PROOF.md)

We need an integral decomposition because a change of basis having an odd denominator could change the answer. In the central-character summand of $R[H]$ with $iI$ acting by $i^f$, let $e_\lambda=|P|^{-1}\sum_{p\in P}\lambda(p)^{-1}p$ be the Pauli weight idempotents. These are in $R[H]$, since $|P|$ is a power of two and all weights are fourth roots of unity. They are orthogonal and sum to the unit of this summand. This follows from the ordinary abelian Fourier sum on $P/[P,P]$ because $-I$ acts trivially. Fix one weight $\lambda$ in an orbit of size $\ell$, stabilizer $S\le G$ and preimage $\widetilde S\le H$. The actual action of $\widetilde S$ on the corresponding Weyl line in $B$ gives a character $\eta$ extending $\lambda$. Its scalars and their inverses lie in $R$: the chosen vector has a coordinate equal to a unit and the action and inverse preserve $R$-coordinates.

Choose coset representatives $x_i$ carrying $\lambda$ to the orbit's weights. Multiplication of the matrix units $x_i e_\lambda x_j^{-1}$ identifies the orbit ideal with $\operatorname{Mat}_\ell(e_\lambda R[H]e_\lambda)$. The corner has $R$-basis $e_\lambda\tilde s$ for any lifts $\tilde s\in\widetilde S$ of $s\in S$, by disjoint coset supports; elements outside the stabilizer compress to zero. Replacing each basis vector by $\eta(\tilde s)^{-1}e_\lambda\tilde s$ makes the products the ordinary products in $S$, independently of lifts. Thus these are isomorphisms of $R$-algebras, including their integral lattices. On each matrix factor the irreducibles over $\mathbb C$ are indexed by $\rho\in\mathrm{Irr}(S)$, have degree $\ell d_\rho$, and appear in $B\otimes W$ with multiplicity $m_\rho=\langle W|_S,\rho\rangle$. This follows by restricting to one weight and canceling the character $\eta$.

Put $F_S(X)=\sum_{s\in S} X^{k(s)}s$ and
$$
a_\rho(X)=d_\rho^{-1}\sum_{s\in S}\chi_\rho(s) X^{k(s)} .
$$
Each coefficient is rational since coprime powers preserve the fixed space, and is an algebraic integer since the corresponding integral central class sum acts by that coefficient. These polynomials are therefore in $\mathbb Z[X]$ and are monic of degree ten. Inversion also preserves the fixed space. The raw regular Gram scalar is
$$
\frac{N m_\rho}{\ell d_\rho}=q^2 a_\rho(t);
\qquad \text{the normalized scalar is }a_\rho(t)/t^{10}.
$$
Indeed the raw kernel on representatives is $\operatorname{tr}(U_a^*U_b)^f$. Character orthogonality on $H$ gives the scalar $|H|m_\rho/(\ell d_\rho)$ and passing to scalar cosets removes $|Z|$. The normalization uses $q^f=q^2 t^{10}$. By equality on every complex irreducible, the corresponding central convolution is $q^2 F_S(t)I_\ell$ in the above coordinates. One may use the opposite convolution or central character when identifying representative columns with functions; inversion and conjugation preserve the polynomials, and permutation or unit phases preserve the lattice. In the coset basis of the regular algebra multiplication is integral exactly when the multiplying element is integral (evaluate at the unit for necessity). Thus
$$
D_f=\operatorname{lcm}_{S}\ \operatorname{odd-den}\big(F_S(t)^{-1}\big)
$$
where the two stabilizers are chosen from the preceding orbit description. No odd orbit size multiplies or divides the answer.

## 2. Class formula and logarithmic growth

For each distinct polynomial $a$ in a fixed $S$, set $h_a(s)=\sum_{\rho:a_\rho=a} d_\rho\chi_\rho(s)$. Galois action preserves the polynomial and degrees, so $h_a$ is integer-valued and invariant under inversion. The central idempotent formula gives
$$
F_S(t)^{-1}(s)=\frac1{|S|}\sum_a\frac{h_a(s)}{a(t)} .
$$
This yields an exact algorithm at any supported width. The retained columns group together classes with equal $k$ and the entire vector $(h_a)$, recording their total mass. The checker verifies $\sum_s h_a(s)h_b(s)=|S|\delta_{ab}h_a(1)$ and $\sum_s h_a(s)X^{k(s)}=h_a(1)a(X)$, plus the regular character sum. Three groups' polynomials are separately reproduced from the earlier table projection. For $P_5$, an independent recursion on the radical reproduces all 322 irreducibles and their levels. [Parabolic recursion](RADICAL.md) · [Class data](CORNERS.json) · [Ordinary GAP/ATLAS source record](https://www.math.rwth-aachen.de/~Thomas.Breuer/ctbllib/ctbltoc/data/S10%282%29.html)

Let $P(X)$ now denote the monic LCM of the spectral polynomials across both stabilizers of the chosen sector. Put $g=|G|$ and $C_{S,s}=(g/|S|)\sum_a h_a(s)P/a\in\mathbb Z[X]$. Then $D_f$ is the positive odd part of
$$
\frac{|g P(t)|}{\gcd\big(gP(t),\,C_{S,s}(t)\text{ for all }S,s\big)}.
$$
By row orthogonality each $P/a$ is a rational linear combination of the $C_{S,s}$ for its group. The LCM property makes the $P/a$ coprime as a family over $\mathbb Q[X]$. Hence a Bézout combination of the integer polynomials $gP,C_{S,s}$ gives a fixed nonzero integer $b$ after clearing scalar denominators. The evaluated gcd divides $b$ and depends only on $t\bmod |b|$. These residues are eventually periodic on each subsequence of widths.

Write $P=X^e Q$ with $Q(0)\ne0$. Factoring the polynomials into short, pairwise coprime monic factors and taking maximum exponents gives the following values. The checker proves coprimality, exact division of every polynomial and attainment of each exponent. For each factor of $Q$ it also verifies that the constant term has strictly lower 2-adic valuation than every other term at the indicated widths.

| $f\bmod4$ | Distinct polynomials | $\deg P$ | $e$ | $v_2(Q(\pm2^r))$ | Sufficient $r$ |
|---:|---:|---:|---:|---:|---:|
| 0 | 256 | 592 | 2 | 1918 | 17 |
| 2 | 156 | 381 | 1 | 1041 | 7 |

The factor $t^e$ contributes no odd part. Thus $D_f/|Q(t)|$ is eventually periodic and bounded above and below by positive constants on each subsequence. Monicity yields
$$
\log_2D_f=295(f-2)+O(1)\quad(4\mid f),\qquad
\log_2D_f=190(f-2)+O(1)\quad(f\equiv2\bmod4).
$$
These slopes describe the common denominator of the canonical decoder. The preceding odd-width computation used the single symplectic quotient with slope 136. [Odd-width predecessor](https://github.com/apoursh/integer-mult-bounds/blob/46a25a0e602ae6e2917ae2f2de3828f04bfcba4f/research/clifford-canonical-class-denominators/PROOF.md) · [Polynomial certificate](check_growth.py)

## 3. Sharp endpoints and optimal noise denominators

In the $4\mid f$ sector denote the trivial polynomial of $G$ by $T$ and its table row 2 (degree 155) polynomial by $B$. In the $f\equiv2\pmod4$ sector take $T,B$ from the trivial and nontrivial linear characters of $K_-$, the first two rows of its table. Their eleven coefficients are the specified rows of the pinned projection divided by the row degree. For $t>0$ the smallest and largest normalized Gram eigenvalues are $B(t)/t^{10},T(t)/t^{10}$. For $t<0$ the two polynomials exchange places.

For a finite exact certificate, compare every polynomial $p$ in both groups with the proposed endpoints. For each sign $\sigma$, form $(p-B)(\sigma z),(T-p)(\sigma z)$ in the positive case, and exchange $T,B$ in the negative case. The checker evaluates every admissible $z=2^r<2^{18}$ of that phase and expands each difference at $z=2^{18}+Y$. All expansion coefficients are nonnegative, giving the inequalities on the whole remaining ray. Both claimed polynomials occur. At $4\mid f$ this also agrees with the neutral Pauli-invariant component and the Schur-product endpoint inheritance from $f-1$. [Shifted-polynomial check](verify.py) · [Four-qubit endpoint inheritance and noise theorem](https://github.com/apoursh/integer-mult-bounds/blob/ebe2c019e398d73444e4f33f2d71bd5775795a01/research/clifford-dyadic-noise-floor/PROOF.md)

For the normalized Gram the minimum is positive, rational and below 1. Its mean eigenvalue is 1 and the matrix has a nonzero off-diagonal entry (take the identity and a single phase gate). The normalized analysis matrix is split over $R$ because $f$ is even. The split-matrix noise theorem therefore gives the sharp odd denominator among *all* left inverses attaining the optimal Euclidean norm as the odd part of the smaller of $B(t),T(t)$. Scaling by $q^{f/2}$ preserves it. For completeness the same two $G$ polynomials give the sharp endpoints at every odd $f\ge15$ with $r=(f-1)/2$ and $t=(-1)^{\lfloor(f+1)/4\rfloor}2^r$. The odd-sector formula gives normalized eigenvalues $a_\rho(t)/t^{10}$, with raw eigenvalues $q a_\rho(t)$. Both signs on the large ray were checked above, and the checker verifies the eleven remaining odd widths below that ray. Choose a power of two $2^{-h}$ small enough that the smallest raw Gram eigenvalue of $2^{-h}A_f$ is below 1. Its reduced numerator is the odd part of $\min(B(t),T(t))$, and the dyadic split and denominator are invariant under this scaling. This supplies the optimal noise denominator for every full-rank width without introducing a square root of two into the raw odd-width lattice. The resulting arithmetic invariant gives no circuit cost.
