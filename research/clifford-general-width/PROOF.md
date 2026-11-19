# A linear sufficient width for dyadic Clifford tensor interpolation

Let $R=\mathbb Z[i,1/2]$, $d=2^n$, and choose a Gaussian-dyadic unitary matrix $U_a$ in each projective class of the full $n$-qubit Clifford group modulo scalar powers of $i$. The raw observation matrix $C_f$ has columns $\operatorname{vec}(U_a^{\otimes f})$. Reordering its coordinates produces $\operatorname{vec}(U_a)^{\otimes f}$. All inputs and outputs below are complex-linear, including when the mixture coefficients are arbitrary complex numbers.

**Theorem.** There is a specified matrix $B_f$ over $R$ satisfying $B_f C_f=I$ for every $f\ge F(n)$, where

| Qubits | Sufficient width $F(n)$ |
|---|---:|
| $n=1,2$ | 5, 9 respectively |
| odd $n\ge3$ | $3n+2$ |
| even $n\ge4$ | $3n+1$ |

For the normalized columns $d^{-f/2}\operatorname{vec}(U_a^{\otimes f})$, multiply $B_f$ by $d^{f/2}$. This gives an $R$-left inverse whenever $nf$ is even. For odd $nf$ the normalization uses a square root of two, and the same formula is over $R[\sqrt2]$. In that case every entry of the normalized map lies in $\sqrt2\,\mathbb Q(i)$. Multiplying by an $R$-matrix keeps every entry in this same rational subspace, which excludes $1$ because $\sqrt2\notin\mathbb Q(i)$. Thus the raw and normalized ring conclusions genuinely differ. Every specialization of the raw identity to a residue field of odd characteristic still splits. Optimality for $n\ge5$ is open here.

The Bell-fibre decomposition and four-dimensional character corners are due to apoursh in [#7799, Sections 1–3](https://github.com/apoursh/integer-mult-bounds/blob/7f08a74037788311cc6b7da27297b25f1b188e45/research/clifford-bell-fibres/PROOF.md). The argument below includes both pair parities and constructs pure and mixed subspaces in arbitrary dimension. [#6714, three-qubit framework](https://github.com/alephnan/integer-mult-bounds/blob/f7f32a18dde54e67624a9ed9cc7e1b266d9585c0/research/clifford-three-qubit-threshold/PROOF.md) · [#7766, four-qubit spectrum](https://github.com/aliromman/integer-mult-bounds/blob/d7c2dd1868c70f0addce2c0a4d3220149452f14b/research/clifford-four-qubit-threshold/PROOF.md)

## 1. The two Bell contractions

Write $V=X\oplus L=\mathbb F_2^n\oplus\mathbb F_2^n$, $W_{x,z}=X^xZ^z$, and $q(x,z)=x\cdot z$. The symplectic pairing is the polar form of $q$, written $[u,v]$. Let $G=\mathrm{Sp}(V)$. Conjugation and congruence respectively act by

```text
U W_t U* = γ_U(t) W_(St)
U W_t Uᵀ = θ_U(t) W_(L_S t),       L_S t = St+b_S .
```

Both phases are fourth roots of unity. The first identity is the Clifford definition. Its map to $G$ is onto since symplectic transvections lift by $(1+i)(I+iP)/2$ for Hermitian Paulis $P$. For an element fixing all labels the conjugation signs form a character. Removing the corresponding Weyl leaves a scalar by Pauli irreducibility. A scalar in $R$ of complex modulus one is a power of $i$, by descent in $a^2+b^2=4^j$. The projective kernel is therefore exactly the Weyls. Since the Weyls are real, $U,\bar U$ have the same linear label action. Thus $U U^T$ is a Weyl up to phase, which gives the affine label action in the second identity. Applying transpose gives $q(L_S t)=q(t)$.

Use $k$ ordered Bell pairs and one singleton, $f_0=2k+1$. For input labels $t=(t_1,\ldots,t_k)$, an output $t'$ is hit by column $U$ exactly when $t'_j=L_S t_j$ for each $j$. The block obtained from that column is then $β U$, with $β=\prod_j\theta_U(t_j)$. Indeed input and output Bell vectors are the normalized vectorizations of the indicated Weyls. **Over $R$** each complete input/output Bell matrix element has coefficient $1/d$ times products of Weyl entries, since the two square roots cancel within a pair. This applies also to odd $n$. Write $w=\sum_j t_j$, $w'=\sum_j t'_j$ as binary sums.

| Pair count | Output sum | Fixed correction to a hit block $M$ | Result on $M=β U$ |
|---|---|---|---|
| $k$ even | $w'=Sw$ | $W_{w'} M W_w^{-1}$ | $σ U$, with $σ=β/\gamma_U(w)$ |
| $k$ odd | $w'=L_S w$ | $W_{w'}^{-1}M W_w$ | $σ\bar U$, with $σ=β\theta_U(w)$ |

For the odd row use $U W_w U^T=\theta_U(w)W_{w'}$ and $(U^T)^{-1}=\bar U$. In particular the fixed linear operation on an observation produces $σ\bar U$ on a column and $cσ\bar U$ on that column multiplied by $c$. It never conjugates $c$.

For either row of the table $σ=σ_S(t)$ is independent of the Pauli and scalar lift. Left multiplication of $U$ by a real Weyl multiplies $β$ by $(-1)^{[p,w']}$. The corresponding singleton phase in either row receives exactly that sign as well. In the even case a scalar $zU$ gives the extra factor $z^{2k}=1$. In the odd case the extra factor is $z^{2k+2}=1$. The phases of an ordinary or congruence action compose on their respective labels, so $σ_{S_1S_2}(t)=σ_{S_1}(L_{S_2}t)σ_{S_2}(t)$. This is where both parity and the direction of the right and left corrections enter.

## 2. A seed whose point stabilizer has dyadic order

Let $s=\lfloor n/2\rfloor+1$ except that $s=1$ at $n=2$. In the standard symplectic basis use the seed
```text
T = (0,Z_1,...,Z_n,X_(s+1),...,X_n),
k = 2n-s+1,       f_0 = 4n-2s+3.
```

Fixing the seed’s zero label forces $b_S=0$. Fixing $L$ pointwise forces $S$ to be the shear $(x,z)\mapsto(x,z+Bx)$, $B=B^T$. Preserving $q$ forces $B$ to have zero diagonal, and the displayed $X$ labels force its last $n-s$ columns and rows to vanish. Conversely these shears are all products of real controlled-$Z_{ab}$ with $a<b\le s$. Their lifts commute with each Weyl in the seed and $W_w$ (the latter is a signed product of seed Weyls), and have $UU^T=I$. They have zero affine offset and trivial $σ$ on the seed for either parity. This identifies the stabilizer $C$ of order $2^{\binom s2}$.

The orbit of $T$ is $G/C$. For a tuple $t_i$ in that orbit choose a transporter $g_i$ and set $j_i=σ_{g_i}(T)$. Triviality on $C$ makes $j_i$ independent of the choice. For $L_S t_i=t_j$ the phase $σ_S(t_i)=j_j/j_i$ is known. Multiplying the corrected observation block by $j_i/j_j$ yields the sum of
```text
M_S = sum_(a over S) c_a U_a          (k even),
M_S = sum_(a over S) c_a conjugate(U_a)   (k odd)
```
over $S\in g_j C g_i^{-1}$. Every left-right translate of $C$ occurs this way. Writing $e_C=\sum_{c\in C}c/|C|$ in $R[G]$, it remains to produce $1\in R[G]e_C R[G]$. Then every single-fibre indicator follows by left translation. The averaging denominator is a power of two.

## 3. Character corners in arbitrary dimension

Take $A=\operatorname{Sym}_n(\mathbb F_2)$, the elementary abelian group of all shears fixing $L$ pointwise, allowing nonzero diagonal. Its signs are indexed by binary quadratic forms $Q$ on $L$, with polar form $λ$. Specifically $χ_Q(uu^T)=(-1)^{Q(u)}$ and $χ_Q(uv^T+vu^T)=(-1)^{λ(u,v)}$. The diagonal and cross terms provide exactly $n(n+1)/2$ independent bits. The idempotents $e_Q=|A|^{-1}\sum_{a\in A}χ_Q(a)a$ are orthogonal and sum to $1$. A linear change of variables in $L$, extended contragrediently to $X$, normalizes $A$ and transports these idempotents.

For an $s$-space $W\le V$ isotropic for the symplectic pairing $[\,,\,]$, $C_W$ generated by all pair shears on basis vectors of $W$ is conjugate to $C$. The pair shear at $u,v$ sends $t\mapsto t+[t,u]v+[t,v]u$. Extend an isotropic basis to a symplectic basis to see the conjugation. Thus every $e_{C_W}$ belongs to the ideal in question.

**Pure planes.** If $λ$ has rank $2h$, it admits a totally isotropic subspace of dimension $n-h$, by adjoining the radical to one side of a symplectic basis of the quotient. Whenever $n-h\ge s$, choose an $s$-dimensional subspace $W\le L$ of this kind. Then $C_W\le A$, $χ_Q|_{C_W}=1$ and $e_Qe_{C_W}e_Q=e_Q$. This covers all odd $n$, the exception $n=2$, and every degenerate polar form at even $n$.

**Mixed planes.** The remaining case is $n=2m\ge4$, $s=m+1$, $λ$ nondegenerate. Pick $r\ne0$ with $Q(r)=0$. On any $λ$-isotropic two-plane $Q$ is linear and hence has a nonzero zero. Put $H=r^{\perp_λ}\subset L$, whose radical under $λ|_H$ is precisely $\langle r\rangle$. Extend $r$ to a maximal $λ$-isotropic $m$-space $P\le H$ using $H/\langle r\rangle$. Choose $z\in L\setminus H$ and $x\in X$ dual to $z$ and annihilating $H$ in the original pairing. Take $W=P\oplus\langle x\rangle$, which is symplectically isotropic in $V$.

The pure pairs in $P$ generate a subgroup $K\le A$ of order $2^{\binom m2}$ on which $χ_Q=1$. The remaining pair shears, involving $x$, are precisely the $2^m$ transformations $T_p$ with $p\in P$ sending $z\mapsto z+p$ and fixing $H$ pointwise on $L$. On $X$ they act contragrediently. They normalize $A$. The explicit pair formula shows these commute, and together with $K$ they give the unique products $aT_p\in C_W$. A nonzero $p\in P$ distinct from $r$ lies outside the radical of $λ|_H$, so choose $y\in H$ with $λ(p,y)=1$. Then $λ(z,y)$ changes under $T_p$, hence $Q$ changes. At $p=r$, $Q(z+r)=Q(z)+Q(r)+λ(z,r)=Q(z)+1$. Thus exactly $K$ fixes the character in $C_W$. For $p\ne0$, $e_Q aT_p e_Q=0$ by orthogonality of distinct character idempotents. For $a\in K$, $e_Q a e_Q=e_Q$. Consequently
```text
e_Q e_(C_W) e_Q = 2^(-m) e_Q .
```
Multiplying by $2^m$ recovers $e_Q$. At $n=2$ an anisotropic quadratic form can have no nonzero zero, explaining the separate choice of $s$.

Summing these explicit pure or rescaled mixed corners gives the identity in the ideal. Expanding the idempotents expresses it using the measured coset sums and coefficients in $R$. Enumeration of finite groups, subspaces and transporters suffices to specify a particular decoder.

## 4. Individual coefficients and larger widths

For the recovered matrix $M_S$, put $V_a=U_a$ for even $k$, $V_a=\bar U_a$ for odd $k$. Return $\operatorname{Tr}(V_a^*M_S)/d$. Distinct classes in the same fibre differ by a nonidentity Weyl up to scalar, hence have zero trace pairing, and the target pairs to $d$. This proves the raw left-inverse identity at $F(n)$. At larger width, tensor each target row with one copy of $\operatorname{vec}(U_a)^*/d$ per extra slot. The extra factor evaluates to one on its target. Its values on other columns are immaterial because the original row vanishes there. Each algebraic operation is over $R$.

No norm or running-time bound follows from just counting the Bell pairs. Even the character expansion has $2^{n(n+1)/2}$ terms before combining coefficients. A physical interface needs a concrete producer, precision, storage, movement and a full restoration bill.
