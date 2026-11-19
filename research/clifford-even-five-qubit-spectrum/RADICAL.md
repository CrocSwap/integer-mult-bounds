# A recursion for the nonzero-vector stabilizer

Write $P_m=\operatorname{Stab}_{\operatorname{Sp}(2m,2)}(e)$ and split the natural module as $\langle e,f\rangle\perp W$, where $[e,f]=1$ and $\dim W=2m-2$. Extend $s\in L=\operatorname{Sp}(W)$ by the identity on the hyperbolic plane. Every element of $P_m$ is uniquely $u(v,b)s$, with $v\in W$, $b\in\mathbb F_2$, and
$$
u(e)=e,\qquad u(x)=x+[v,x]e\quad(x\in W),\qquad u(f)=f+v+be .
$$
Indeed take the induced action on $e^\perp/\langle e\rangle$ and then the image of $f$. Preservation of the pairing determines the lift on $W$. The radical $U$ multiplies by $(v,b)(w,c)=(v+w,b+c+[v,w])$. It is elementary abelian, and $L$ acts by $(v,b)\mapsto(sv,b)$.

Let $D=\ker(s-I)$, $d=\dim D$, $I=\operatorname{im}(s-I)=D^\perp$. A vector $he+x+cf$ is fixed by $u(v,b)s$ exactly when
$$
(s-I)x=cv,\qquad [v,sx]+cb=0 .
$$
If $v\notin I$, then $c=0$ and $x$ satisfies one nonzero equation on $D$, so the fixed dimension is $d$ including the free $h$. If $v\in I$, all $x\in D$ give solutions with $c=0$. An extra dimension with $c=1$ exists precisely when $b=[v,sx_0]$ for $(s-I)x_0=v$, independent of the chosen solution. Thus for the two values of $b$ the fixed dimensions are $d+1$ and $d+2$.

There are two kinds of characters of $U$. Those trivial on $(0,1)$ are $\lambda_a(v,b)=(-1)^{[a,v]}$ for $a\in W$; they split into the zero and nonzero orbits. The others are $\lambda_Q(v,b)=(-1)^{b+Q(v)}$ for a quadratic refinement $Q$ of the pairing; they split by Arf type. Their stabilizers in $L$ are respectively $L$, $P_{m-1}$ and the two full orthogonal groups on $W$. Every weight extends to its stabilizer preimage by the formula $\lambda(us)=\lambda(u)$, since this is a split semidirect product. Inducing these extensions times each ordinary irreducible $\rho$ of the corresponding stabilizer $S$ exhausts $\mathrm{Irr}(P_m)$ by the transitive-weight argument of the main proof.

For $s\in S$, set $M=|W|=2^{2m-2}$. The Fourier sum of $X^{\dim\ker(us-1)}$ against $\lambda$ on $U$ is
$$
\begin{cases}
M\big[2\mathbf1_{a=0}X^d+(X^2+X-2)(X/2)^d\big], &\lambda=\lambda_a,\\
M(X^2-X)(X/2)^d, &\lambda=\lambda_Q.
\end{cases}
$$
For the first case subtract the baseline $2X^d$ on $I$ and add the correct two values. The total linear character sum is $M\mathbf1_{a=0}$, and on $I$ it is $|I|=M/2^d$ because $a\in D$. For the second case the two signs cancel outside $I$. Inside $I$, $Q(v)=Q(sx_0+x_0)=[sx_0,x_0]=[v,sx_0]$ by $s$-invariance of $Q$, so the positive term is exactly $X^{d+2}$. This fixes both signs of the quadratic case.

A central class sum acts on the induced representation by its scalar on one weight space. Compressing by that weight idempotent removes $s\notin S$ and replaces the coefficient of $s\in S$ by the preceding Fourier sum. Hence if $a(X)$ is the ordinary fixed-dimension scalar polynomial for $\rho$ acting on $W$, the corresponding polynomial for $P_m$ on its natural module is
$$
\begin{cases}
M\big[2a(X)+(X^2+X-2)a(X/2)\big],&a=0\text{ weight},\\
M(X^2+X-2)a(X/2),&\text{nonzero linear weight},\\
M(X^2-X)a(X/2),&\text{either quadratic orbit}.
\end{cases}
$$
Here “zero weight” means the parameter of $\lambda_a$ is zero, not that the polynomial vanishes. The base $P_1=C_2$ has polynomials $X^2\pm X$. Starting from that base, the numbers of ordinary irreducibles at ranks $2,3,4,5$ are $10,37,114,322$ and their distinct polynomial counts are $9,26,64,143$. The rank-five result agrees coefficient-by-coefficient, including repeated levels, with direct conjugacy classes and characters in the action on 1,023 nonzero vectors. A separate binary-matrix check evaluates the Fourier identities on every Levi element and invariant character through rank three. [Recursive check](check_recursion.py) · [Direct geometric check](check_radical.py) · [GAP reconstruction](export_tables.g)
