# Two finite schedules at tensor width 13

Let $R=\mathbb Z[i,1/2]$. For one Gaussian-dyadic unitary $U_a$ in each projective four-qubit Clifford class, let $A$ have columns $(\operatorname{vec}(U_a)/4)^{\otimes13}$. There are $N=12,128,668,876,800$ columns. Write $K=A^*A$, $J=K^{-1}A^*$, and use the Euclidean operator norm. The width-13 spectrum gives **52 distinct positive rational levels** $x_0<\cdots<x_{51}$. In particular,
$$
x_0=470624175/2^{32},\qquad x_1=359889075/2^{31},\qquad x_{51}=7841980575/2^{30}.
$$
The starting matrix $B$ is any left inverse with $\|B-J\|<2^{56}$. The dyadic Bell-fibre construction satisfies this hypothesis. We count one application of $K$ to the current output vector per step, with $B y$ and the reusable $A^*y$ supplied. [Exact spectrum, PR 7772](https://github.com/aliromman/integer-mult-bounds/blob/1398fbdca3536389d8ac3c8b3aaa408f03e8f6c2/research/clifford-threshold-conditioning/PROOF.md) · [Bell inverse and starting error, PR 7799 §5](https://github.com/apoursh/integer-mult-bounds/blob/7f08a74037788311cc6b7da27297b25f1b188e45/research/clifford-bell-fibres/PROOF.md)

For a real step $h$, update $D\gets D+h(A^*-KD)$, starting at $D=B$. For an observation $y$ this means $d\gets d+h(A^*y-Kd)$. Each update preserves $DA=I$. The error after any prefix is $D-J=p(K)(B-J)$, where $p(X)=\prod_j(1-h_jX)$. As $K$ is Hermitian, $\|p(K)\|=\max_i|p(x_i)|$. Every exact left inverse also satisfies
$$
DD^*=K^{-1}+(D-J)(D-J)^*.
$$
Indeed $(D-J)A=0$ kills both cross terms. The least attainable squared norm is therefore $1/x_0$.

## 1. A dyadic schedule with relative residual below $2^{-129}$

For each level $x$ define
$$
S_x=x\prod_{y\ne x}|1-x/y|,\qquad
T_x=\max_{y\ne x}64y/|1-y/x|,\qquad
b_x=\max(0,\lceil\log_2(2^{128}S_x)\rceil,\lceil\log_2 T_x\rceil).
$$
Use $h_x=2^{-b_x}\operatorname{round}(2^{b_x}/x)$, nearest with ties to even, in **decreasing order of $x$**. These 52 real-dyadic steps are specified without large matrix operations.

For the residual at $x$, its own multiplier has absolute value at most $x2^{-b_x-1}$. The other multipliers obey
$$
|1-h_y x|\le (1+1/128)|1-x/y|
$$
by the choice of $T_y$. Thus the 52-factor product is bounded by $2^{-b_x-1}S_x(1+1/128)^{51}<2^{-128}$. The last inequality follows from $(1+1/128)^{51}\le1/(1-51/128)<2$. Exact evaluation at the 52 rational nodes gives the stronger certificate
$$
2^{-130}<\max_i|p(x_i)|<2^{-129}.
$$
Consequently $\|D-J\|<2^{-73}$ and $\|D\|^2-1/x_0<2^{-146}$. All operations stay in $R$ for $B\in R^{N\times 256^{13}}$.

Both schedules in this note have ordered positive steps $h_1\le\cdots\le h_m$. For a fixed $x>0$, the factors $|1-h_jx|$ are at most one until $h_jx>2$, and at least one thereafter. Prefix products have their maximum at an endpoint. The final product at each node is at most one, so **every prefix has norm at most one** as an operator on the initial error. The order matters numerically even in this finite example. Applying the same 52 factors in reverse gives a prefix norm strictly between $2^{138}$ and $2^{139}$ at step 48.

### A coefficient bound for writing out the decoder

The nominal $b_x$ range from 69 to 266 with sum 5,676. Reducing each $h_x$ gives a total denominator exponent of 5,627. This counts dyadic scalar coefficients. To bound coefficients in the full decoder, the stabilizer-state result $4U_a\in\mathbb Z[i]^{16\times16}$ gives $2^{52}A$ integral. Also $K(a,b)=(\operatorname{tr}(U_a^*U_b)/16)^{13}$. The relative Clifford has finite order, and its Gaussian-rational trace, a sum of roots of unity, is a Gaussian integer. Thus $2^{52}K$ is integral. [Stabilizer entry bound, PR 7802 §4](https://github.com/apoursh/integer-mult-bounds/blob/ebe2c019e398d73444e4f33f2d71bd5775795a01/research/clifford-dyadic-noise-floor/PROOF.md)

For the explicit initial Bell inverse of PR 7799, $2^{27}B$ is integral. Indeed its normalization multiplier $4^{13}$ and the six Bell bras and six Bell kets with entries of denominator four leave the factor $4^{13}/4^{12}=4$. The Weyl permutations and phase corrections are integral. Isolating a fibre costs at most $2^{23}$ in the denominator, through two shear-character averages of order $2^{10}$ and a coset average of order eight. The terminal coefficient comes from $U_a^*/16$, with denominator dividing $2^6$. The scalar ledger gives the exponent $23+6-2=27$. Adding the exponents under the 52 updates therefore places every coefficient of every prefix on the $2^{-8358}\mathbb Z[i]$ grid, since $27+52\cdot52+5627=8358$. This is a sufficient common grid. Movement, accumulator headroom, and a gate count for $A^*$ and $K$ require a concrete implementation. [Bell maps and averages, PR 7799 §§1–4](https://github.com/apoursh/integer-mult-bounds/blob/7f08a74037788311cc6b7da27297b25f1b188e45/research/clifford-bell-fibres/PROOF.md)

## 2. Exact optimum with 50 dyadic steps and one odd reciprocal

Construct a real polynomial $r$ of degree at most 50 by prescribing at the 51 nonbottom nodes
$$
r(x_j)=(-1)^{j-1}/(1-x_j/x_0),\qquad 1\le j\le51.
$$
Its values alternate strictly, so it has one simple real root in each open interval $(x_j,x_{j+1})$, $1\le j\le50$, and degree exactly 50. For each root $z$ use the scalar $2^{-192}\lfloor 2^{192}/z\rfloor$, in order of decreasing root. Complete the sequence by the exact factor $h=1/x_0=2^{32}/470624175$. These steps approximate the normalized polynomial $(1-X/x_0)r(X)/r(0)$, chosen to vanish on the bottom level and equioscillate on the rest. The package rounds reciprocals using only rational interpolation and integer sign comparisons. In particular, its generator never approximates a root in floating point. All 51 factors are listed in SCHEDULE.json.

Exact substitution of the stored shifts gives $p(x_0)=0$ and $2^{-59}<\max_i|p(x_i)|<2^{-58}$. Set $C=D-J$. The range of $C$ is orthogonal to the bottom eigenspace and $\|C\|<1/4$. On that eigenspace $DD^*=K^{-1}+CC^*$ is exactly $1/x_0$. On its orthogonal complement the largest eigenvalue is at most $1/x_1+1/16<1/x_0$, since the spectral gap $1/x_0-1/x_1$ exceeds three. Hence the exact corrected decoder **attains** $\|D\|^2=1/x_0$. If $B$ is dyadic, all odd denominators enter through the single last scalar. The sharp necessity in PR 7802 then gives the least odd denominator exactly $470,624,175$. This realizes the optimum among left inverses, including noncanonical ones. [Sharp denominator theorem, PR 7802](https://github.com/apoursh/integer-mult-bounds/blob/ebe2c019e398d73444e4f33f2d71bd5775795a01/research/clifford-dyadic-noise-floor/PROOF.md) · [Separate canonical-denominator result, PR 7805](https://github.com/apoursh/integer-mult-bounds/blob/d3df403a13bee082a8cef62f190024aaf0cd08dd/research/clifford-canonical-denominator/PROOF.md)

## 3. Why the pass counts are sharp in the stated model

A normalized residual polynomial has $p(0)=1$ and may have complex coefficients. For any $d+1$ distinct positive nodes $X$ and any $p$ of degree at most $d$, Lagrange interpolation at zero gives
$$
1\le\max_{x\in X}|p(x)|W(X),\qquad W(X)=\sum_{x\in X}\prod_{y\in X,\, y\ne x}|y/(y-x)|.
$$
The verifier computes the following strict integer bounds. The independent replay uses Newton divided differences on the alternating data $(-1)^i$ in increasing node order, since these are the signs of the Lagrange basis values at zero.

| Nodes, indexed from zero in increasing order | Certified weight sum | Consequence for the full spectrum |
|---|---:|---|
| All 52 levels | $2^{60}<W<2^{61}$ | Every degree at most 51 has residual norm $>2^{-61}$. |
| All levels except $x_{21}$ | $2^{52}<W<2^{53}$ | Every degree at most 50 has residual norm $>2^{-53}$. |

Thus 52 is the least degree for contraction by $2^{-128}$. On the full set, the exact degree-51 minimax residual equals $1/W$, attained by interpolation of the alternating signs divided by $W$. This also explains the abrupt gain in the last degree.

For the second claim, fix a polynomial of degree at most 50 in advance. There is a level $x$ with $|p(x)|>2^{-53}$. Let $u$ be a unit $K$-eigenvector at that level and $v$ a unit ambient vector perpendicular to the columns of $A$. Give the method the initial inverse $B'=J+2^{55}uv^*$. It has $B'A=I$ and admissible error $2^{55}<2^{56}$. Its final error norm exceeds four, so the identity for $DD^*$ forces $\|D\|>4>1/\sqrt{x_0}$. The same strict obstruction holds for some dyadic starting inverse. Indeed choose a dyadic split $L$, put $P=I-AL$, and observe that $B'=L+(B'-L)P$. Approximating $B'-L$ entrywise by a dyadic $H$ gives the exactly feasible $L+HP$ arbitrarily close to $B'$. Continuity preserves both strict bounds. Therefore 51 is the smallest degree of a **fixed normalized residual polynomial guaranteeing the optimal norm for every such initial dyadic left inverse**, when the final odd reciprocal is allowed.

These are uniform polynomial lower bounds given only a spectral residual or initial norm requirement. The Bell inverse may have additional structure in its error, and more general algorithms may use projections or side information. Neither lower bound prices a physical multiplier. Larger tensor widths require a new spectral check for these node-specific schedules.
