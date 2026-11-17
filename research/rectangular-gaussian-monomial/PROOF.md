# Monomial symmetries of a rectangular Gaussian block

Let $X=\prod_{i=1}^d\{0,\dots,m_i-1\}$ and
$Y=\prod_{i=1}^d\{0,\dots,n_i-1\}$, where $d\ge1$ and each $m_i,n_i\ge2$.
Fix real origins $\alpha_i,\beta_i$, positive spacings $s_i,t_i$ and
positive weights $\gamma_i$. The matrix $G$ has rows indexed by $X$
and columns by $Y$, with entries
$$
G_{xy}=a_x b_y\exp\!\left(-\sum_{i=1}^d
 \gamma_i(\alpha_i+s_i x_i-\beta_i-t_i y_i)^2\right),
\qquad a_x,b_y\in\mathbb C^\times.
$$
Write $\lambda_i=\gamma_i s_i t_i$, $W=\operatorname{diag}(\lambda_i)$,
$\bar x_i=x_i-(m_i-1)/2$ and $\bar y_i=y_i-(n_i-1)/2$.
The centered matrix $K_{xy}=\exp(2\bar x^{\mathsf T}W\bar y)$
satisfies $G=AKB$ for invertible diagonal matrices $A,B$.
Expanding the quadratic gives the centered mixed term
$2\bar x^{\mathsf T}W\bar y$ plus one term in $x$ and one in $y$.
These separate terms, with $a_x$ and $b_y$, give $A$ and $B$.
Alternatively one can obtain them from
$A_{xx}=G_{x0}/K_{x0}$ and $B_{yy}=G_{0y}/(A_{00}K_{0y})$.

## Classification

An invertible monomial matrix has one nonzero coefficient in each row and
column. Let $P e_x=e_{p(x)}$ and $Qe_y=e_{q(y)}$ be the permutation
parts of monomial maps $U$ and $V$ on the row and column spaces.
Then $UG=GV$ holds exactly for
$$
U=c A P A^{-1},\qquad V=c B^{-1}Q B,\qquad c\in\mathbb C^\times,
$$
where $p,q$ act by the same signed coordinate permutation on the two
index grids. In detail, there is a permutation $\sigma$ of the axes with
$$
(m_{\sigma(i)},n_{\sigma(i)},\lambda_{\sigma(i)})
 =(m_i,n_i,\lambda_i)
$$
and a sign $\epsilon_i\in\{1,-1\}$ for each axis. The maps are
$$
p(x)_{\sigma(i)}=\epsilon_i x_i+\tfrac{1-\epsilon_i}{2}(m_i-1),
\qquad
q(y)_{\sigma(i)}=\epsilon_i y_i+\tfrac{1-\epsilon_i}{2}(n_i-1).
$$
In particular, the number of possible permutation pairs is
$2^d\prod_C |C|!$, with $C$ ranging over the classes of equal
$(m_i,n_i,\lambda_i)$.

### Necessity of the coordinate maps

Write $Ue_x=u_xe_{p(x)}$ and $Ve_y=v_ye_{q(y)}$. At row $p(x)$
and column $y$, the equation $UG=GV$ says
$u_xG_{xy}=G_{p(x),q(y)}v_y$. The change of entries under $p,q$ is
therefore a product of a row factor and a column factor. Such factors
cancel from the four-entry ratio
$$
\frac{G_{xy}G_{x' y'}}{G_{xy'}G_{x' y}}
   =\exp\!\left(2 (x-x')^{\mathsf T}W(y-y')\right).
$$
The ratio is positive real even with complex gauges. Its invariance and
the injectivity of the real exponential, with $x'=y'=0$, give
$$
(p(x)-p(0))^{\mathsf T}W(q(y)-q(0))=x^{\mathsf T}Wy. \tag{1}
$$

Let $S$ have columns $p(e_i)-p(0)$, and $T$ have columns
$q(e_i)-q(0)$. Both index grids contain all unit vectors, so applying
(1) to those vectors gives $S^{\mathsf T}WT=W$. Since $W$ is
invertible, both $S$ and $T$ are invertible. Taking $y=e_j$ for every
$j$ in (1) then gives
$(p(x)-p(0)-Sx)^{\mathsf T}WT=0$, so $p(x)=p(0)+Sx$.
Taking $x=e_i$ for every $i$ gives $q(y)=q(0)+Ty$.

The affine map $p(0)+Sx$ carries the convex hull of $X$ onto itself.
At the zero corner the $d$ incident edges have the coordinate
directions. Their images are the $d$ incident edges at $p(0)$, in
some permutation of those directions. The edge in direction $i$ has
$m_i$ points of $X$, so its image has the same number of points.
Hence its image direction $\sigma(i)$ satisfies $m_{\sigma(i)}=m_i$.
The endpoints now force $Se_i=\epsilon_i e_{\sigma(i)}$, with no
change of scale between integer indices. The same argument on the column
box gives $Te_i=\eta_i e_{\tau(i)}$ and $n_{\tau(i)}=n_i$.

The $i$-th diagonal entry of $S^{\mathsf T}WT$ is zero unless
$\sigma(i)=\tau(i)$. In that case it is
$\epsilon_i\eta_i\lambda_{\sigma(i)}$. Its required value
$\lambda_i>0$ forces a common permutation, common signs and equal
effective weights on exchanged axes. The corner translations must put
each positive direction at coordinate zero and each negative direction
at the opposite end of the corresponding box.

### Attainment and uniqueness of the weights

The coordinate maps above send $\bar x,\bar y$ through the same signed
matrix $S$ with $S^{\mathsf T}WS=W$. Thus $K_{p(x),q(y)}=K_{xy}$.
Using $G=AKB$, entrywise equality for $UG=GV$ simplifies to
$$
u_x\frac{A_{xx}}{A_{p(x),p(x)}}=
v_y\frac{B_{q(y),q(y)}}{B_{yy}}
\quad\text{for every }x,y.
$$
Since every entry of $K$ is nonzero, this holds exactly when both sides
are one common nonzero scalar $c$. This gives the two stated monomial
lifts and proves their uniqueness up to that scalar. Each allowed
coordinate permutation and sign choice yields a distinct pair because
the values at the zero corner and all unit vectors determine those choices.

## Consequence and scope

If all triples $(m_i,n_i,\lambda_i)$ are distinct, the only permutation
parts are paired coordinate reflections. Every vertex cycle on either
grid has length at most two. Absolute matrix order can still depend on
the common scalar. The rectangle itself can admit axis exchanges when
some triples coincide. In the exact $8\times12$ verifier fixture, the
first two axes have different Gaussian weights and row spacings but
equal products $\gamma_i s_i t_i$. They can exchange, for 16 pairs
including all sign choices.

This theorem applies to full Cartesian grids with positive paired
weights and exact unrounded entries. The ratio proof addresses rectangular
row and column relabeling without requiring a common vertex set.
Periodization, support holes and nonseparable phase or rounding error can
alter the ratio. Charging the monomial maps and installing them in a
physical caller require separate arguments.
