# Denominators of the five-qubit canonical decoder

Let $R=\mathbb Z[i,1/2]$. Choose one five-qubit Gaussian-dyadic Clifford lift $U_a$ per projective class. Let $A_f$ have raw columns $\operatorname{vec}(U_a^{\otimes f})$, $K_f=A_f^*A_f$ and $J_f=K_f^{-1}A_f^*$. Write $D_f$ for the least positive odd integer with $D_fJ_f$ over $R$. This choice of raw columns matters at odd width because unit column normalization introduces $\sqrt{2}$. Write $G=\mathrm{Sp}(10,2)$, $g_0=|G|=24,815,256,521,932,800$, $q=32$, and $N=q^2g_0$ for the number of projective columns. We work at every odd $f\ge15$. The dyadic left inverse $L_f$ exists by #7810. [Pinned splitting theorem](https://github.com/apoursh/integer-mult-bounds/blob/9cdeb734ea8d0e6ddf3914dd92b6ced5046a6910/research/clifford-five-qubit-modular-seed/PROOF.md)

## A scalar convolution on the symplectic quotient

Put $r=(f-1)/2$ and $t=(-1)^{\lfloor(f+1)/4\rfloor}2^r$. Define the integral central group-ring element
$$
 F(X)=\sum_{s\in G} X^{k(s)}s,\qquad k(s)=\dim_{\mathbb F_2}\ker(s-1).
$$
At $X=t$, the coefficient function is the character of the quotient module $W_f$ in the odd-sector decomposition $V^{\otimes f}=V_0\otimes W_f$. Here $V_0$ is the natural Clifford module at $f=1\bmod4$ and its conjugate at $f=3\bmod4$. Indeed if a lift has nonzero trace $a$, then $|a|^2=2^{k(s)}$ and $a^4=(-1)^{k(s)}2^{2k(s)}$. Dividing $a^f$ by $a$ or by $\bar a$ gives $t^{k(s)}$. For every $s$ at least one Pauli translate has nonzero trace. Its norm being a power of two also makes its trace a unit in $R$. [Odd scalar sector, trace support and phases](https://github.com/apoursh/integer-mult-bounds/blob/b42e665721e76e69d05f24a19bdabee0e0f77c04/research/clifford-five-qubit-threshold/PROOF.md)

For an ordinary irreducible $\rho$ of $G$ of degree $d_\rho$, write
$$
 a_\rho(X)=d_\rho^{-1}\sum_{s\in G}\chi_\rho(s)X^{k(s)} .
$$
Every coefficient is rational because $k(s)$ is constant on powers coprime to the order of $s$. The corresponding integral class sum acts by this coefficient on $\rho$, so it is an algebraic integer, hence an integer. Only the identity has $k=10$, giving a monic polynomial of degree ten. At $X=t$ its value is $g_0 m_\rho/d_\rho$ for the multiplicity $m_\rho$ in $W_f$. Inversion leaves $k$ unchanged, so either character convention gives the same polynomial.

Let $H_t=F(t)^{-1}$ in $\mathbb Q[G]$. The central character formula for its coefficient at $s$ reads
$$
 H_t(s)=\frac1{g_0}\sum_{\rho}\frac{d_\rho}{a_\rho(t)}\chi_\rho(s).
$$
The usual inverse-class argument in the projector formula gives the same value here since conjugate characters have equal $a_\rho$ and degree. The raw Gram eigenvalue on $V_0\otimes\rho$ is $Nm_\rho/(q d_\rho)=q a_\rho(t)$. At two projective indices $a,b$, put $u=U_a^*U_b$, let $s$ be its symplectic image and let $\tau(u)=\operatorname{tr}_{V_0}(u)$. Matrix-coefficient orthogonality gives the projector kernel $(q d_\rho/N)\tau(u)\chi_\rho(s)$. Dividing by the raw Gram eigenvalue on each block gives
$$
 (K_f^{-1})_{ab}=\frac{\tau(u)}{q^2} H_t(s).
$$
In particular the raw reduction introduces no odd factor. The denominator of $K_f^{-1}$ equals that of $J_f$ because $J_f=K_f^{-1}A_f^*$ and $J_f L_f^*=K_f^{-1}$. Every $s$ has a lift with unit $\tau$, while a vanishing $\tau$ contributes zero. Thus $D_f$ is exactly the common odd denominator of the rational numbers $H_t(s)$. This turns the many-column Clifford operator into one coefficient per rational symplectic class. [Four-qubit projector and transfer precedent](https://github.com/apoursh/integer-mult-bounds/blob/d3df403a13bee082a8cef62f190024aaf0cd08dd/research/clifford-canonical-denominator/PROOF.md)

## Integer formula and growth at all odd widths

For a Galois orbit $B$ of ordinary characters, put $\psi_B=\sum_{\rho\in B}\chi_\rho$, an integer-valued character. Each orbit has a common degree $d_B$ and polynomial $a_B$. Its values are constant on the rational classes (unions of conjugacy classes related by powers coprime to the element order). There are 192 such classes and 192 character orbits. The full table has 198 ordinary classes and irreducibles. The packet characters are orthogonal with squared norm $|B|$ and form a basis of rational-class functions. [ATLAS table entry](https://www.math.rwth-aachen.de/~Thomas.Breuer/ctbllib/ctbltoc/data/S10%282%29.html) · [Numerical packets](PACKETS.json)

Let $P$ be the monic polynomial LCM of the $a_B$ in $\mathbb Z[X]$. For each rational class representative $s_j$, define
$$
 C_j(X)=\sum_B d_B\,\psi_B(s_j)\,P(X)/a_B(X).
$$
These integer polynomials give $H_t(s_j)=C_j(t)/(g_0 P(t))$. Consequently, with $\operatorname{odd}(z)$ the positive odd part of $|z|$,
$$
 D_f=\operatorname{odd}\!\left(\frac{|g_0P(t)|}
 {\gcd\big(g_0P(t),C_1(t),\ldots,C_{192}(t)\big)}\right).
$$
Equivalently $D_f$ is the odd part of the largest Smith invariant of multiplication by $F(t)$ on the integral rational-class sums. These sums form a ring. Over $\mathbb Q$ their character transform gives the functions constant on character orbits, where multiplication is pointwise. Integral group-ring products preserve integrality. Multiplication by $F(t)$ has nonzero determinant. In the finite additive quotient by $F(t)$ the order of the unit is the exponent, since every element is its multiple inside the quotient ring. Clearing the denominators of $H_t$ computes that order, with powers of two inverted in $D_f$.

There is no common nonconstant polynomial factor of $g_0P,C_1,\ldots,C_{192}$. Indeed, invert the rational packet-character matrix. A common factor of the $C_j$ would divide every $P/a_B$ over $\mathbb Q[X]$, contrary to the definition of the LCM. A Bézout combination over $\mathbb Q[X]$, followed by clearing scalar denominators, gives a fixed nonzero integer $b$ in the ideal generated by these polynomials over $\mathbb Z[X]$. At any integer $t$ the gcd in the formula divides $b$, so it is determined by $t\bmod |b|$. The sequence $t=\pm2^r$ is eventually periodic modulo any fixed integer, since its sign is periodic in $r$.

The 198 polynomials from the independently retained #7806 fixed-space projections yield 113 distinct polynomials. Their monic LCM has degree **272** and nonzero constant term. A Euclidean polynomial LCM computation and multiplication of the listed short factors both give the identical result. For each short factor $h(X)=\sum h_iX^i$ the checker verifies $v_2(h_i)+17 i>v_2(h_0)$ for every nonzero coefficient with $i>0$. Thus $v_2(P(\pm 2^r))=v_2(P(0))=909$ for all $r\ge17$. Combined with the bounded gcd this proves that $D_f/|P(t)|$ is eventually exactly periodic along the odd widths. Since $P$ is monic of degree 272,
$$
 \log_2 D_f=272r+O(1)=136(f-1)+O(1).
$$
The result is an asymptotic slope. Individual increments can vary. This proof does not require the period or a sharp Bézout constant. [Polynomial checker](check_growth.py) · [Short factor product](FACTORS.json) · [Original projection](https://github.com/apoursh/integer-mult-bounds/blob/b42e665721e76e69d05f24a19bdabee0e0f77c04/research/clifford-five-qubit-threshold/PROJECTION.json)

For a smaller finite comparison let $T_f=\operatorname{odd}(\operatorname{lcm}_B a_B(t))$. Each scalar $D_f/a_B(t)$ is a rational algebraic integer after inverting two, by acting with $D_f H_t$ on the irreducible block. Hence $T_f\mid D_f$. The packet formula gives $D_f\mid g_{0,\mathrm{odd}}T_f$, since each $T_f/a_B(t)$ is dyadic. The table in the README records the exact ratio for five widths.

## One explicit threshold witness

At $f=15$ take $U=S^{\otimes4}\otimes I_2$ with $S=\operatorname{diag}(1,i)$. Its trace is $2(1+i)^4=-8$, also the trace in the conjugate natural sector. Its symplectic action is the shear with symmetric matrix $\mathrm{diag}(1,1,1,1,0)$. The rank-four image is isotropic, and the associated form on its dual is nonsingular and nonalternating. The orbit of that form under $\mathrm{GL}(4,2)$ has 420 members, checked by enumerating all 20,160 ordered bases. Symplectic extension gives transitivity on the image and its bases. The number of possible images is $\prod_{j=0}^3(2^{10-j}-2^j)/|\mathrm{GL}(4,2)|$, so the conjugacy class has size 328,689,900 and natural fixed dimension six. This is ATLAS class **2F**, column seven; the other rank-four involution column is alternating. The independent replay recomputes the class size, literal gate phases, and the orthogonality norm of its ordinary character column.

For an independent threshold-only proof, reconstruct all 198 raw levels from the #7806 fixed-space projection, without the rational packet table. Multiplying the 198 scalar projector coefficients by their common denominator makes their odd parts integral. The character entries are algebraic integers and the resulting kernel is already Gaussian rational, giving an upper bound in $R$. Evaluating the ordinary character column at the four-phase gate supplies a matching lower bound on one inverse Gram entry. The diagonal misses a factor of 39. Four rational classes individually give the complete denominator at 15. At 23 none does, while the identity and class 2A together attain it. Class 2A is realized by $S\otimes I_{16}$, whose shear has rank one and whose trace is $16(1+i)$. [Single-gate check and exact entry](check_phase.py) · [All-class check](verify.py)

Finally the least raw Gram eigenvalue at width 15 is $2^{32}\cdot394477183485$. Scaling the raw matrix by the dyadic unit $2^{-38}$ gives least eigenvalue $394477183485/2^{44}$. The split-matrix theorem of #7802 therefore yields least odd denominator **394,477,183,485** among left inverses attaining the optimal Euclidean noise norm. Scaling back multiplies decoders by a dyadic unit and preserves their odd denominators. The 115-digit denominator concerns the particular Moore–Penrose inverse. Neither number by itself is an arithmetic or data-movement price. [Sharp split-matrix theorem](https://github.com/apoursh/integer-mult-bounds/blob/ebe2c019e398d73444e4f33f2d71bd5775795a01/research/clifford-dyadic-noise-floor/PROOF.md)

Prepared by apoursh with substantial OpenAI Codex assistance. New proof and code are Apache-2.0.
