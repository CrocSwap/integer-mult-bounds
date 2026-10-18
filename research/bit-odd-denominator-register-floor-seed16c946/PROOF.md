# Square-zero augmentation for odd-denominator address frames

## Model

Fix a positive odd integer $q$ and let $L=q^{-1}M_m(\mathbb Z)$ be the full additive address lattice. Work in the formal group algebra $\mathbb F_2[L]$, with $[A][B]=[A+B]$. A paid call on $n$ scalar registers is

$$
D_N([A])=I_n+([A]-1)N,
$$

where $A\in L$ has rational rank one and $N\in M_n(\mathbb F_2)$ is a rank-one idempotent. Arbitrary address-independent $GL_n(\mathbb F_2)$ maps may be interleaved for free. There are $W$ data registers with exact diagonal endpoints $([C_1],\ldots,[C_W])$, where $C_i\in L$ and $qC_i\bmod 2$ is invertible. Auxiliary registers may have arbitrary diagonal monomial endpoints in $L$. The lower bound also applies when auxiliary outputs are discarded, provided the data-to-data block is exactly the stated diagonal target.

The base statement uses equality of the full register matrix. The auxiliary-discarded variant constrains only its data-to-data block; the other blocks may be arbitrary.

## Square-zero map

Let $V=M_m(\mathbb F_2)$ as a vector space, and define

$$
S=\mathbb F_2\oplus V,\qquad (a,X)(b,Y)=(ab,aY+bX).
$$

The ideal $0\oplus V$ has square zero. Since $q$ is odd, the assignment

$$
\phi([A])=(1,qA\bmod 2)
$$

extends to a group-algebra homomorphism: $(1,qA)(1,qB)=(1,q(A+B))$. Thus $([A]-1)$ maps to $(0,qA\bmod 2)$.

After applying $\phi$, a paid factor is the identity plus the square-zero matrix term represented, as a vector in $M_n(V)$, by $N\otimes(qA\bmod 2)$. Products of two first-order terms vanish. The degree-one coefficient of a $k$-call word, including free interleaved scalar changes of basis, is therefore

$$
T=\sum_{j=1}^{k} B_j\otimes \bar A_j,
$$

where $\bar A_j=qA_j\bmod 2$ and $B_j$ is obtained from $N_j$ by invertible prefix and suffix factors. In particular, $\operatorname{rank}(B_j)=1$, while $\operatorname{rank}(\bar A_j)\le 1$. Under the usual Kronecker identification with an ordinary matrix on $\mathbb F_2^n\otimes\mathbb F_2^m$, each summand has rank

$$
\operatorname{rank}(B_j\otimes\bar A_j)=\operatorname{rank}(B_j)\operatorname{rank}(\bar A_j)\le 1.
$$

For the full diagonal endpoint, the zero-degree part forces the product of all free scalar changes to be the identity. Under the auxiliary-discarded variant this need not hold, but it is not needed: the degree-one contribution of each call is still multiplied on the left and right by invertible prefix and suffix matrices, so its register factor has rank one in either model. The data-to-data degree-one block is

$$
\operatorname{diag}(qC_1\bmod 2,\ldots,qC_W\bmod 2),
$$

which has rank $mW$. Any unspecified auxiliary rows or columns can only increase the rank of the full coefficient matrix. Rank subadditivity gives

$$
k\ge mW.
$$

This proof allows any number of dirty auxiliaries, any rational relations among the paid address frames, and arbitrary free interleaved scalar $GL_n(\mathbb F_2)$ maps. It requires one common odd-denominator lattice and targets whose cleared matrices $qC_i$ are invertible modulo two.

## Tightness

For each data target $C_i$, write its columns as $c_{i1},\ldots,c_{im}$, so

$$
C_i=\sum_{r=1}^{m}c_{ir}e_r^T.
$$

Use one paid call with frame $c_{ir}e_r^T$ and register idempotent $E_{ii}$ for each pair $(i,r)$. Since $C_i\in L$, each column frame $c_{ir}e_r^T$ also belongs to the full lattice $L$. The $m$ calls on role $i$ multiply to $[C_i]$ on that diagonal role; calls on distinct coordinate projectors do not interact. Auxiliary registers remain unchanged. This gives an exact $mW$-call construction for every such collection of targets, so the lower bound is sharp in the stated model.

For the concrete instance in this package, $m=W=3$ and

$$
C_1=I_3,\qquad C_2=I_3+E_{21},\qquad C_3=I_3+E_{32}.
$$

All three have determinant one. Their column decompositions give a nine-call word, replayed over the complete formal group algebra in `verify.py`.

## Boundary

If $qC_i$ is singular modulo two for some target, this argument gives only $k\ge\sum_i\operatorname{rank}(qC_i\bmod2)$. If a paid frame has an even denominator, no odd $q$ clears all frames and this map does not apply. These are scope boundaries, not conclusions about those cases.
