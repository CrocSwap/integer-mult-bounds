# Five rational weights for a repeated rank-one stabilizer site

Let $a,b$ be normalized four-qubit stabilizer states in absolute Gaussian-dyadic gauges, with diagonalizing Pauli Lagrangians $L_a,L_b$. Put $B=|a\rangle\langle b|$ and $y=(\mathrm{vec}B)^{\otimes13}$. For the column labelled $(S,p)$ let $V=W_pU_S$, $\tau=\langle a|V|b\rangle$, and
$$
j=d(L_a,SL_b)=4-\dim(L_a\cap SL_b).
$$
With the dictionary normalization in [the adjoint proof](PROOF.md), the full Moore–Penrose solution is
$$
(A^\dagger y)_{S,p}=h_j\,\overline\tau.
$$

| $j$ | $h_j$ |
|---:|---:|
| 0 | $279183413/16081633325721600$ |
| 1 | $52701673/32163266651443200$ |
| 2 | $36859/253254068121600$ |
| 3 | $-777583/64326533302886400$ |
| 4 | $-14688133/1029224532846182400$ |

The input to the executable specifies $a=U_{T_a}|r\rangle$ and $b=U_{T_b}|c\rangle$; changing either by a Gaussian unit gives the thirteenth power of the corresponding phase on $y$. All 36,720 stabilizer lines (2,295 Lagrangians, sixteen eigencharacters each) occur on each side. When $T_a=T_b=I$, $B$ is an ordinary computational matrix unit. For a query, evaluate one four-qubit matrix element and the rank of the displayed intersection. The class computation below is finite preprocessing shared by all inputs and queries. [Executable](canonical.py)

## From the adjoint to five distances

The two stabilizer projectors for $a$ and $Vb$ are normalized signed sums of their sixteen Pauli stabilizers. Their trace pairing vanishes when the two characters disagree on the intersection; otherwise it equals $2^{-j}$ because the intersection contains $2^{4-j}$ labels. Hence $|\tau|^2$ is zero or $2^{-j}$. In the nonzero case $\tau(1+i)^j$ is a Gaussian dyadic of norm one. Factoring its Gaussian-integer numerator over the unique prime above two leaves only a Gaussian unit, so $\overline\tau^{12}=(-1/64)^j$. This gives
$$
(A^*y)_{S,p}=(\overline\tau/4)^{13}=u_j\overline\tau,\qquad
u_j=4^{-13}(-1/64)^j
$$
also when $\tau=0$. Keeping the complex phase here is essential even for real-looking rank-one inputs.

In each fibre the 256 matrices $V_{S,p}$ are a trace-orthogonal basis of squared norm 16. Under synthesis $M_c(S)=\sum_pc_{S,p}V_{S,p}$, the adjoint data therefore become $16u_j B$. Coefficient extraction is $c_{S,p}=\operatorname{Tr}(V_{S,p}^*M_c(S))/16$. By #7816, $K=A^*A$ acts entrywise on $M$ by the real central convolution with $F(g)=16^{-12}(-64)^{\dim\operatorname{Fix}(g)}$ on $G=\mathrm{Sp}(8,2)$. This Gram is invertible. On functions $f(S)=w(d(L_a,SL_b))$, left and right transport identify its action with that at a single diagonal reference Lagrangian $Z$ on both sides. Namely, for $L_a=A_0 Z$ and $L_b=B_0 Z$ substitute $A_0^{-1}SB_0$ in the function argument; centrality makes both translations commute with the convolution. The stabilizer $P$ of $Z$ acts transitively on Lagrangians $X$ at each fixed distance from $Z$ by extending a pair of intersection-adapted symplectic bases. Thus the space of such radial functions is five-dimensional and retained by both $K$ and $K^{-1}$. [Central convolution and source conventions](https://github.com/apoursh/integer-mult-bounds/blob/7e7e62c62fcccd11f5c8e22677b4523863a48f4b/research/clifford-transported-fibre-gram/PROOF.md)

## Exact radial normal equations

Write $\Omega=G/P$ for the 2,295 Lagrangians, with shell sizes $(n_0,\ldots,n_4)=(1,30,280,960,1024)$. These also follow by selecting the intersection in $Z$ and then a symmetric graph on its quotient, $n_j={4\brack j}_2\,2^{j(j+1)/2}$. The executable generates all of $\Omega$ by closing $Z$ under specified symplectic transvections; the count, shell sizes and Lagrangian invariant certify coverage. For an ordinary conjugacy representative $g_i$ let $D_{ij}=\#\{X\in\Omega:d(X,g_iX)=j\}$. The operator $\sum_g F(g)g$ on functions on $\Omega$ has common entry $b_j$ on every ordered pair at distance $j$. Counting all such ordered pairs gives
$$
b_j=\frac{\sum_i |C_i| F(g_i)D_{ij}}{|\Omega|n_j}.
$$
The pushforward from the group has exactly this normalization: the entry from $X$ to $Y$ sums over every group element carrying $X$ to $Y$, including the entire stabilizer multiplicity. Equivalently one may use $g^{-1}$ since $F(g^{-1})=F(g)$. We compute the displacement counts on every retained ordinary representative and check equality on the fused rational pair before using its combined class size. The class sizes, fixed dimensions and all 81 representatives were computed natively in the referenced #7816 GAP source. [Frozen class data](source/CLASS-ALGEBRA.json) · [Native regeneration](https://github.com/apoursh/integer-mult-bounds/blob/7e7e62c62fcccd11f5c8e22677b4523863a48f4b/research/clifford-transported-fibre-gram/CLASS-ALGEBRA.md)

Choose one $Y_i$ at distance $i$ from $Z$ and form the $5\times5$ matrix
$$
K_{ik}^{\rm rad}=\sum_{X:d(Z,X)=k} b_{d(Y_i,X)}.
$$
Exact elimination gives the displayed solution of $K^{\rm rad}h=u$. Multiplying each $16h_jB$ by $K$ gives $16u_jB$ on *all* group arguments. Since the full Gram is invertible, synthesis and extraction prove the claimed Moore–Penrose formula. Tests check the five normal equations, $n_iK_{ik}=n_kK_{ki}$, all distance branches under independent dense lift multiplication, and a separate spherical-eigenvalue reconstruction. The displacement construction uses $81\cdot2295$ class-representative/Lagrangian pairs and five distance rows. It never forms the $12,128,668,876,800$-column dictionary. [Direct checks](verify_canonical.py) · [Independent spectral reconstruction](spherical.py)

## Error and support on the complete dictionary

Trace orthogonality gives $\sum_p|\tau|^2=16$, so each fibre has exactly $16\cdot2^j$ nonzero $\tau$. All five $h_j$ are nonzero. Each shell of distance $j$ contains $|P|n_j$ group elements, and $|P|=47,377,612,800/2295$. Thus $|P|\sum_j n_j16\cdot2^j=8,338,459,852,800$ canonical coefficients are nonzero, the same support as the adjoint on this family. The orthogonal projector satisfies
$$
\|AA^\dagger y\|^2=\langle A^*y,A^\dagger y\rangle
=16|P|\sum_j n_j u_j h_j
=\frac{478566778595}{5856573836677349376}.
$$
The input has unit norm. Subtracting this fraction from one gives the minimum squared least-squares residual in the full Clifford span. The sparse known-fibre interface of #7816 by itself would require nearly every fibre; here the rank-one stabilizer symmetry gives a compact inverse despite that density. The argument applies to a repeated separable stabilizer site. Site-varying computational points have the adjoint census in [COORDINATES.md](COORDINATES.md); their inverse-Gram reduction remains open.
