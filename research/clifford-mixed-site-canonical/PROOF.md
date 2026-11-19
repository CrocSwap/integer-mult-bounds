# A one-sided canonical decoder at width 13

Use the four-qubit dictionary with columns $(\mathrm{vec}(V)/4)^{\otimes13}$, $V=W_pU_S$, and the Gaussian-dyadic lifts in #7821. The observation has an arbitrary 52-qubit vector $\psi$ on the row registers and $\bar b^{\otimes13}$ on the column registers. Here $b$ is any normalized four-qubit stabilizer vector in the indicated gauges, with Pauli Lagrangian $L_b$. The linear statements apply to all complex $\psi$ given the stated overlaps. The compact producer takes a supplied affine-quadratic row chart. [Lift and address conventions](https://github.com/apoursh/integer-mult-bounds/blob/eead545a4ba6c50010fcac0919a9fdc6b14bd673/research/clifford-compact-adjoint-fibres/PROOF.md)

## Reduction to 36,720 features

For each Lagrangian $L$ take an orthonormal stabilizer eigenbasis $\mathcal B_L$ in Gaussian-dyadic gauges and set
$$
 d_\psi(L)=\sum_{w\in\mathcal B_L} w\langle w^{\otimes13},\psi\rangle .
$$
Changing the allowed lift of a line multiplies its vector by a Gaussian unit $\eta$. Indeed a Gaussian dyadic of modulus one has only units at odd primes, and clearing its denominator leaves only the ramified prime above two. The phase change in the feature is $\eta\bar\eta^{13}=1$. Each $Vb$ is a line of $SL_b$ with such a phase. Thus $(A^*y)_{S,p}=4^{-13}\langle Vb,d_\psi(SL_b)\rangle$. In the trace-orthogonal synthesis $M_c(S)=\sum_p c_{S,p}V$ this reads $M_{A^*y}(S)=16\cdot4^{-13}d_\psi(SL_b)b^*$. By #7816, $K=A^*A$ applies the same real central convolution on each matrix entry, with kernel $16^{-12}(-64)^{\dim\mathrm{Fix}(g)}$. It is positive definite and preserves functions of $SL_b$. This permutation module has 2,295 vertices. [Normal operator](https://github.com/apoursh/integer-mult-bounds/blob/7e7e62c62fcccd11f5c8e22677b4523863a48f4b/research/clifford-transported-fibre-gram/PROOF.md)

The normalized zonal functions $u_\theta(i)$ and Gram scalars $\lambda_\theta$ on this module are computed in #7821 from the dual polar graph on the Lagrangians. At adjacency levels $30,13,3,-5,-15$ their multiplicities are $m_\theta=1,135,1190,918,51$. The spectral projector entry on a vertex pair at distance $i$ is $m_\theta u_\theta(i)/2295$. The full inverse has entry $H_i=\sum_\theta m_\theta u_\theta(i)/(2295\lambda_\theta)$. This works on arbitrary vertex data, even when $d_\psi$ itself is nonradial. The canonical label query is
$$
 (A^\dagger y)_{S,p}=4^{-13}\left\langle Vb,\sum_X H_{d(SL_b,X)} d_\psi(X)\right\rangle .
$$
These five inverse kernel entries give the normal solution before returning to Weyl coordinates. The repeated-site coefficients from #7821 already applied the inverse to a particular radial right-hand side. [Pinned spherical decomposition](https://github.com/apoursh/integer-mult-bounds/blob/eead545a4ba6c50010fcac0919a9fdc6b14bd673/research/clifford-compact-adjoint-fibres/COORDINATES.md) · [Program](mixed.py)

## One elimination per vertex on an entangled row chart

Project $L$ onto its $X$ coordinates to obtain $H\subseteq\mathbb F_2^4$ of dimension $h$. Choose a pivot-reduced basis $x_i$ of $H$, with lifts $(x_i,z_i)\in L$. Decompose a nibble $r=s+\sum_i t_i x_i$ using the pivot bits for $t(r)$, so both $s$ and $t(r)$ are linear functions of $r$. The form $\ell_{ij}=z_i\cdot x_j$ is symmetric by isotropy, and well-defined because changes of lift lie in $H^\perp$. Put
$$
 q(t)=\sum_i\ell_{ii}t_i+2\sum_{i<j}\ell_{ij}t_it_j\pmod4 .
$$
A stabilizer basis over $L$ on each $H$-coset has vectors with amplitudes $(1+i)^h2^{-h}i^{q(t)+2v\cdot t}$, for $v\in\mathbb F_2^h$. The translation part of generator $X^{x_i}Z^{z_i}$ changes $q$ by a phase whose variable part cancels the Pauli sign. Diagonal stabilizers are constant on each coset. Distinct $v$ are orthogonal by the binary Fourier sum.

Expand $d_\psi(L)$ in that basis. A tuple $(r_1,\ldots,r_{13})$ contributes exactly when its nibbles are in the same coset of $H$. Summing over $v$ places the whole contribution at $r_*=\bigoplus_i r_i$, with multiplier on the input amplitude
$$
 (-1/64)^h i^{q(t(r_*))-\sum_iq(t(r_i))}.
$$
Indeed the aligned Walsh sum gives $2^h$ times one basis scalar and thirteen conjugate scalars. For a single computational point the canonical convolution therefore keeps just one vector component. Its support over vertices may expand. [Exact support classification](SUPPORT.md)

For the 52-bit affine-quadratic input with support rank $a\le52$, introduce four output bits and impose $r_*=\bigoplus_i r_i$ and $r_i+r_*\in H$ on the $4+a$ variables. Add the displayed quadratic phase to the observation phase, restrict to the affine solution space, and eliminate the observation variables while retaining the output variables. Substitution preserves fourth-root quadratic phases with even mixed terms. The pinned parameterized Gauss elimination yields a four-bit affine-quadratic chart or zero. There are at most 2,295 eliminations with at most 56 variables. The previous conservative small-coefficient operation bound per elimination is $O((4+a)^5)$; a point needs just the explicit formula. For $r$ distinct requested target Lagrangians the implementation scans 2,295 vertices per target and uses at most $16\cdot2295r$ real-weight/complex-entry multiply-adds. Each requested label then needs a single four-qubit transition vector and inner product. These are arithmetic and representation costs on supplied charts. Precision, preparation and tape movement require additional accounting. [Gaussian controls](check_mixed.py)

## The sharp dimension on unrestricted row vectors

Let $\psi$ vary among superpositions of the 36,720 tensors $v^{\otimes13}$, all rows of the stabilizer bases. If $w,v$ belong to Lagrangians at distance $j$, the stabilizer-projector trace gives $|\langle w,v\rangle|^2=0$ or $2^{-j}$. For nonzero overlap, $\langle w,v\rangle(1+i)^j$ is a Gaussian unit, so $\langle w,v\rangle^{13}=(-1/64)^j\langle w,v\rangle$, also valid at zero. Represent the 16 mixture coefficients for each input basis as the ordinary coordinates of a single vector in $\mathbb C^{16}$. The map to $d_\psi$ becomes $C\otimes I_{16}$ where $C_{LM}=(-1/64)^{d(L,M)}$. Its diagonal is one and its off-diagonal absolute row sum is $30/64+280/64^2+960/64^3+1024/64^4<1$. Strict diagonal dominance gives invertibility. All 36,720 complex features can therefore vary independently. The Gram inverse on the quotient is invertible, and all 16 line amplitudes may be recovered from label queries in each $SL_b$ fibre. The restricted canonical map has rank **36,720**, a matching dimension lower bound for any exact linear encoding of unrestricted row observations. The affine-quadratic subclass has additional structure.
