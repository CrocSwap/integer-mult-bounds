# Exact canonical support of every varying-row coordinate

Fix the input column at all 13 sites and let $r_i\in V=\mathbb F_2^4$ be arbitrary computational output rows. Write $t=\bigoplus_i r_i$, $u_i=r_i+t$, and $D=\operatorname{span}(u_i)$. The $u_i$ sum to zero. For covectors $\xi\in V^*$ define
$$
 Q(\xi)=\frac{\#\{i:\xi(u_i)=1\}}{2}\pmod2 .
$$
The count is even. Evaluating the parity of $\xi+\eta$ shows that the polar form of $Q$ is $\sum_i\xi(u_i)\eta(u_i)$. Let $E$ be the annihilator in $V$ of all covectors with both $Q(\xi)=0$ and zero polar pairing against every covector. This is the least subspace such that $Q$ factors through $E^*$: translating a covector leaves every value unchanged exactly when both conditions hold. Since $Q$ is defined by vectors in $D$, $E\subseteq D$.

The adjoint requires the projection $H=\pi_X(SL_b)$ to contain $D$. The canonical entry at $(S,p)$ is nonzero exactly when $H\supseteq E$ **and** $\langle t|W_pU_S|b\rangle\ne0$. The assertion also holds in rotated common stabilizer bases by transporting the coordinates. For each admissible $H$ of dimension $h$ there are $2^{h(h+1)/2}$ graphs of symmetric forms, $20,643,840$ group elements per Lagrangian and $16\cdot 2^h$ compatible Pauli labels per group element. The number of such $H$ containing a given $e$-plane is the binary Gaussian binomial coefficient of $4-e$ and $h-e$. Summation gives the five exact possibilities.

| $e=\dim E$ | Occupied symplectic fibres | Nonzero canonical coefficients |
|---:|---:|---:|
| 0 | 47,377,612,800 | 8,338,459,852,800 |
| 1 | 31,585,075,200 | 6,670,767,882,240 |
| 2 | 25,268,060,160 | 5,929,571,450,880 |
| 3 | 22,460,497,920 | 5,580,773,130,240 |
| 4 | 21,139,292,160 | 5,411,658,792,960 |

All are attained. Take row lists $(0)$, $(1,1)$, $(1,2,3)$, $(1,2,3,4,4)$, or $(1,2,3,4,8,12)$, padding each with zeros to length 13. Nibbles are written in decimal. [Support calculator](support.py)

## Shear character and noncancellation

A symmetric shear adds an arbitrary symmetric form $T$ on $V$ to the graph above $H$, through its restriction $T|_H$. Define a functional $[Q,T]$ on symmetric forms by $[Q,\xi\otimes\xi]=Q(\xi)$. Rank-one squares span all symmetric forms. Equivalently, if $Q(\xi)=\sum_i a_i\xi_i+\sum_{i<j}a_{ij}\xi_i\xi_j$, then $[Q,T]=\sum_i a_i T_{ii}+\sum_{i<j}a_{ij}T_{ij}$. This establishes existence and equivariance under basis changes.

On $H\supseteq D$, the sign in the feature at $t$ is $(-1)^{[Q,\ell]}$ for any ambient extension of the graph form $\ell$. Indeed translating each row by $t$ gives the $u_i$ whose sum vanishes; the phase difference in the [feature formula](PROOF.md) is unaffected because $13\equiv1\bmod4$ and the polar cross terms from the sum vanish. Each diagonal form entry contributes half the number of shifted rows carrying its bit modulo two. Each off-diagonal entry contributes the parity of the number carrying both bits. These are exactly the diagonal and polarized coefficients of $Q$. The adjoint scalar is consequently $(-1/64)^h(-1)^{[Q,\ell]}$ on compatible Lagrangians and zero elsewhere. The Gram inverse commutes with the symmetric shears, so its output transforms by the same character $(-1)^{[Q,T]}$. The shears act transitively above each $H$. Nonzero output is possible only if the character is trivial on the stabilizer there, so the character must factor through restriction to $H$. This requires $E\subseteq H$.

Sufficiency also requires excluding cancellations in the inverse. The finite certificate checks them all over the integers. Move $D$ to a coordinate $d$-plane by a general linear basis change, and start with all $2^{d(d+1)/2}$ possible quadratic defects on $D^*$. The elementary coordinate additions generate the general linear group. Closing their action leaves $1,2,4,5,7$ representative forms for $d=0,1,2,3,4$, respectively, including any formal types not needed for particular row lists. For each of the 19 representatives, construct the 2,295 exact signed features from $(D,Q)$ and evaluate the inverse at the 67 zero graphs, clearing common denominators. In **all 1,273 cases** the output is nonzero precisely when $E\subseteq H$. Equivariance under basis changes and shears proves the statement for all lifts and all inputs. The checker also verifies the reduction to these signed features against the coordinate program on actual observations. [Integer certificate](check_support.py)

For rows $(1,0,\ldots,0)$, $d=1$ and $e=0$. There are 6,670,767,882,240 adjoint and 8,338,459,852,800 canonical nonzeros. The adjoint is zero throughout the identity symplectic fibre, but the canonical coefficient there for $p=16$ (one $X$ shift) is $-1965636949/32404491151329024000$ when the input column is zero. The squared norm of the projection of this unit observation is $34240796149757/767064758258815834521600$. Before the common factor $16|P|/4^{26}$, the norm is the inner product of the 2,295 scalar features with their inverse images, by trace orthogonality. The subgroup preserving the marked vector acts transitively on projected subspaces of each dimension and incidence, and the shear character is trivial, so the sum uses eight shells. The independent pointed-flag construction gives the same result. [Singleton calculation](POINTED.md)
