# Canonical readout with two arbitrary sites

Use the Gaussian-dyadic four-qubit Clifford lifts and the width-13 dictionary of #7816 and #7823. In fixed left and right stabilizer bases let the repeated site be the matrix unit $B=E_{rc}$. At the other two sites take an arbitrary joint tensor $J$ with entries $J_{ikmn}$ in the basis $E_{ik}\otimes E_{mn}$. This includes entangled two-site inputs. The observation is $(\mathrm{vec}\,B)^{\otimes 11}\otimes J$. All thirteen factors of a dictionary column are identical, so the choice of the two site positions is immaterial.

Write $V$ for the specified lifted Pauli translate expressed in those two bases, $Z$ for the computational Lagrangian and $S$ for the relative binary action. Thus $V=U_L^*W_pU_TU_R$ and $S=L^{-1}TR$. Write $j=4-\dim(Z\cap SZ)$ and $\tau=V_{rc}$. The width-13 adjoint entry for a basis pair $E_{ik}\otimes E_{mn}$ is $4^{-13}\overline\tau^{11}\overline{V_{ik}}\overline{V_{mn}}$. A nonzero $\tau$ has squared modulus $2^{-j}$ and $\overline\tau^{12}=(-1/64)^j$ by the Gaussian-dyadic phase identity of #7821. Consequently, including $\tau=0$,
$$
 4^{-13}\overline\tau^{11}=h_j\tau,
 \qquad h_j=4^{-13}(-1/32)^j.
$$

## One Pauli conjugation

Let $P_{(z,x)}=i^{|x\cap z|}X_xZ_z$ be a trace-orthogonal Hermitian Pauli basis, with $z$ stored in the low four bits. Expand $|c\rangle\langle k|=16^{-1}\sum_v\langle k|P_v|c\rangle P_v$. Then
$$
 \tau\overline{V_{ik}}=\langle r|V|c\rangle\langle k|V^*|i\rangle
 =\frac1{16}\sum_{u,v}\langle r|P_u|i\rangle\langle k|P_v|c\rangle\,
 \mathbf1_{\{u=Sv\}}\epsilon_v(V),
$$
where $VP_vV^*=\epsilon_v(V)P_{Sv}$. The signs depend on the Pauli translate. When $u=Sv$, multiplication $V\mapsto P_u VP_v$ acts on this particular basis vector by that sign.

For a fixed $S$, synthesize the adjoint coefficients by $M(S)=\sum_p d(S,p)V$. The trace basis identity is $\sum_p\overline{V_{mn}}V=16E_{mn}$. Multiplication of each coefficient by $\epsilon_v(V)$ therefore replaces $16E_{mn}$ by $16P_uE_{mn}P_v$. With $t_{uv}=\langle r|P_u|i\rangle\langle k|P_v|c\rangle$ this gives
$$
 M_{A^*y}(S)=\sum_{u,v}t_{uv}\,h_j\mathbf1_{\{u=Sv\}}P_u E_{mn}P_v.
$$
The Gram of #7816 acts on each scalar entry of $M$ by the central $F(g)=16^{-12}(-64)^{\dim\operatorname{Fix}(g)}$ on $\mathrm{Sp}(8,2)$. Constant left and right basis changes preserve this action, as does replacing $T$ by its relative coordinate $S$ since $F$ is central. Each scalar input $S\mapsto h_j\mathbf1_{\{u=Sv\}}$ is the pullback of $(X,w)\mapsto h_{d(Z,X)}\mathbf1_{\{u=w\}}$ along $S\mapsto (SZ,Sv)$. Its inverse $K(Z,u;X,w)$ is computed on that permutation module. This uses one arbitrary marked vector, including vectors outside either Lagrangian. A single incident-flag table covers the smaller one-site problem in #7823.

## Coefficient formula

Extraction of a coefficient of $M$ is $\mathrm{Tr}(V^*M)/16$. For a nonzero $t_{uv}$ we must have $u=(z,r\oplus i)$ and $v=(t,c\oplus k)$. Multiplying $t_{uv}$ with $P_uE_{mn}P_v$ cancels both Hermitian phase choices and leaves the single matrix unit $E_{r\oplus i\oplus m,c\oplus k\oplus n}$ with sign $(-1)^{z\cdot(r\oplus m)+t\cdot(c\oplus n)}$. Indeed the two factors of $i^{|x\cap z|}$ on the left multiply to $(-1)^{x\cdot z}$, and the signs from the two input indices there are $(-1)^{z\cdot(i\oplus m)}$. On the right the signs from the two input indices are $(-1)^{t\cdot(c\oplus n\oplus c\oplus k)}$, which combines with $(-1)^{t\cdot(c\oplus k)}$ to give $(-1)^{t\cdot(c\oplus n)}$. Thus the basis-pair answer is
$$
 \frac{\overline{V_{r\oplus i\oplus m,c\oplus k\oplus n}}}{16}
 \sum_{z,t\in\mathbf F_2^4}
 (-1)^{z\cdot(r\oplus m)+t\cdot(c\oplus n)}
 K\bigl(Z,(z,r\oplus i);SZ,S(t,c\oplus k)\bigr).
$$
Multiply each answer by $J_{ikmn}$ and sum. The implementation uses one length-256 Walsh transform for each occupied pair of displacements $(r\oplus i,c\oplus k)$ and combines all terms reading the same output unit. There are at most 256 such transforms and 256 output units. All requested Pauli translates of a given target reuse the same transformed weights. The implementation starts with explicit rational real and imaginary input entries and the supplied symplectic labels and bases. A physical producer and tape cost for general two-site inputs remain open.

Independent controls compare the untransformed formula with direct degree-13 entries across all five Lagrangian distances, including rotated bases. To exercise the normal equation without using the full-group inverse implementation, a second test takes the six embedded one-qubit symplectic elements and all 256 four-qubit Pauli translates. The principal scalar Gram on those six elements is inverted directly. Every one of the 1,536 resulting entries satisfies the actual Choi normal equation, whose factors are computed independently from $[\operatorname{Tr}(V^*V')/16]^{13}$. Full-group controls interchange genuinely distinct singleton matrix units and reduce either chosen singleton to the repeated site, recovering the independently computed #7823 weights.
