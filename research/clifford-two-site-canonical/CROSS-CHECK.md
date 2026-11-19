# Independent check across the two kinds of nonzero mark

At $X=L$ take a nonzero interior mark $u\in L$ and an exterior mark $w\notin L$. There are two parabolic orbits of such ordered pairs, classified by the symplectic pairing $s=\langle w,u\rangle$. In coordinates $L=Z$, the external $X$ part of $w$ is a nonzero functional on $L$. A change of basis fixing $u$ is transitive on the functionals of each specified value at $u$. Symmetric shears add an arbitrary $Z$ component to the vector with a given nonzero $X$ part (prescribe the corresponding column of a symmetric matrix). For each interior $u$ the numbers of allowed exterior $w$ are $n_0=112,n_1=128$.

Write $k_C$ for the central inverse value on conjugacy class $C$, computed directly from the full character table by the formula in #7823. Set $f_j=4^{-13}(-1/32)^j$. For each class representative $g$, sum over the 2,295 Lagrangians and form the weighted displacement count
$$
 T_s(g)=\sum_L f_{d(L,gL)}\,
 \#\{w\in (g^{-1}L)\setminus L:\langle w,gw\rangle=s\}.
$$
Indeed in the raw right hand side after shifting $(L,w)$ by $g$, the only surviving interior mark is $u=gw$. For fixed $s$ the inverse result is constant on all $2295\cdot15\cdot n_s$ triples $(L,u,w)$ by transitivity. Its value is therefore $\sum_C |C| k_C T_s(g_C)/(2295\cdot 15\cdot n_s)$. Reversing the two marks gives the same value: substitute $g^{-1}$ for $g$, using $k(g)=k(g^{-1})$ and $d(L,gL)=d(L,g^{-1}L)$. The checker compares all members of each fused rational class packet before applying its multiplicity.

This calculation makes no use of the marked orbit traversal, separating operator, or polynomial interpolation. Its exact answers are $224457234251/202337455041975052800000$ for the perpendicular pair and $-235362773012219/27517893885708607180800000$ for the paired case. Both agree with both orientations in the decoder. [Class-sum checker](check_cross.py)
