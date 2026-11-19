# A marked-Lagrangian inverse for two variable sites

Let $A$ have columns $(\operatorname{vec}(W_pU_S)/4)^{\otimes13}$ for the four-qubit Pauli translates and $S\in G=\operatorname{Sp}(8,2)$, in the fixed Gaussian-dyadic lifts of #7816 and #7821. Fix a repeated stabilizer matrix unit $B$. For an arbitrary two-site tensor $J$, the observation is $y=(\operatorname{vec} B)^{\otimes11}\otimes J$. The following construction returns every queried entry of $A^\dagger y$ exactly. The two-site amplitude calculation, including its normalization and Pauli signs, is derived in [the readout proof](DOUBLE-READOUT.md). The rank of this linear map is 32,896. The proof of that assertion and of the raw adjoint's singular spectrum uses diagonal Clifford characters and support counts. [Rank and singular spectrum](TWO-SITE-SPECTRUM.md)

## Scalar inverse

Use the left and right stabilizer bases to express the target by its relative symplectic action. Write $Z$ for the computational Lagrangian. For each $u,v\in\mathbb F_2^8$ the scalar input is
$$
 S\longmapsto h_{d(Z,SZ)}[u=Sv],\qquad
 d(L,X)=4-\dim(L\cap X),\qquad h_j=4^{-13}(-1/32)^j.
$$
It pulls back from the permutation action on $(X,w)=(SZ,Sv)$. Scalar Gram convolution by $F(g)=16^{-12}(-64)^{\dim\operatorname{Fix}(g)}$ intertwines this pullback. The inverse acts on the same permutation space because its eigenvalues on the full group are positive (#7816). This gives a single finite problem even for marks outside $Z$ or $SZ$.

There are 2,295 Lagrangians. At each there is one zero mark, 15 nonzero internal marks and 240 external marks. Each of the three sets is transitive under $G$. In coordinates $(z,x)$ with $Z=\{(z,0)\}$, the stabilizer of $Z$ consists of changes of basis and symmetric shears $(z,x)\mapsto(z+Bx,x)$. These generate arbitrary changes of nonzero internal marks. For a given nonzero $x$ the symmetric shears realize every value of $Bx$, establishing transitivity on external marks. We may thus take $u$ to be $0$, $Z_1$, or $X_1$. Starting with the transvections of $\mathrm{GL}(4,2)$ and the elementary symmetric shears, retain the generators fixing the chosen $u$. For $Z_1$ the basis changes fix the first basis column; for $X_1$ they fix the first covector and the shear's first column vanishes. The retained generators generate those subgroups by row reduction on the remaining three coordinates and the permitted additions involving the first. Traversing the resulting permutation actions gives 28, 77, and 249 orbits of $(X,w)$ respectively. Even a refinement by a subgroup fixing $u$ is valid, since the right hand side is invariant and the Gram is central. The code stores one value per orbit. The traversal labels 587,520 states for each of three roots, and never enumerates the 47,377,612,800 group elements.

## Computing the central operator from two conjugacy classes

Let $T$ be the sum of the 255 symplectic transvections $t_a(x)=x+\langle a,x\rangle a$. Let $U$ sum one involution per totally isotropic two-plane with independent generators $a,b$. Its action is
$$
 t_a t_b t_{a+b}(x)=x+\langle b,x\rangle a+\langle a,x\rangle b.
$$
The map is independent of the plane basis over $\mathbb F_2$. The image of $g-I$ recovers the plane and $\langle x,(g-I)x\rangle=0$ for all $x$. Witt extension makes this one class, of size $255\cdot126/6=5355$. The class-table representatives have the corresponding rank and pairing. Summing each action on an orbit representative gives sparse integer matrices for $T,U$ on invariant functions. Each row counts the destinations under all elements of that class.

For each class representative $g$, enumerate the invariant Lagrangians $L$. The contributions to the three permutation characters are respectively $1$, $|L\cap\operatorname{Fix}(g)|-1$ and $|\operatorname{Fix}(g)|-|L\cap\operatorname{Fix}(g)|$. Check that these counts agree within each fused packet of the pinned character table from #7816/#7823. For a row $r$ of that table (the sum of an ordinary Galois packet), take the usual character inner product with each permutation character and divide by $\langle r,r\rangle$ to get the common multiplicity. The reconstructed dimensions are 2,295, 34,425 and 550,800. Their union contains 31 character packets. Each has the central scalars
$$
 t=255r(T)/r(1),\quad u'=5355r(U)/r(1),\qquad
 f=\frac{\sum_C |C|r(C)(-64)^{\dim\operatorname{Fix}(C)}}{16^{12}r(1)}.
$$
Here $r(T),r(U)$ denote values on class representatives. Direct character arithmetic gives distinct pairs $(t,u')$ and positive $f$ for these packets. The computed $t,u'$ are integers. Since $|t|\le255$, the values $z=t+511u'$ distinguish all 31 pairs. Interpolate the 31 values $(z,1/f)$ over the rationals. Applying the resulting polynomial of degree at most 30 in $T+511U$ to the orbital input gives exactly $F^{-1}$ on it. Newton evaluation clears denominators before multiplying the sparse matrices. Mapping the left mark to its representative and reading the orbit label then gives each weight for the Walsh sum. The forward polynomial $z\mapsto f$ reproduces the right hand side in every one of the 354 orbit equations. [Implementation](flag_weights.py) · [Normal equations and diagonal probes](check_flag_weights.py)

## Finite arithmetic

The five parabolic double cosets reduce the common odd denominator to 327,680 Walsh multipliers. The resulting sharp divisor has 115 bits. Two matrix-unit queries force its lower bound, and one three-term integer input attains the full divisor in a single coefficient. [Shell sweep and witnesses](DENOMINATOR.md)

## Independent controls and scope

Direct reciprocal-class averages give the inverse values on the three aligned flags and four more values crossing the interior and exterior modules. These controls use all class representatives and bypass the interpolating polynomial. On a restricted dictionary of six symplectic actions with all 256 Pauli translates, literal degree-thirteen Choi overlaps verify all 1,536 normal equations. Full-group specializations recover both orderings of the one-site answer in #7823. The coordinate-support distribution gives a second way to check the shell sizes used in the rank analysis. [Cross-flag probes](CROSS-CHECK.md) · [Address census](ADDRESS-CENSUS.md)

The formula consumes an explicitly supplied two-site tensor and supplied bases. The singular values in the [spectrum calculation](TWO-SITE-SPECTRUM.md) belong to the restricted raw adjoint; its kernel is shared by the canonical decoder. This package establishes an algebraic readout. Physical generation, routing and finite-precision accounting at a multiplication caller remain open.
