# Minimum rank of an invertible correction with paired support constraints

Let $V$ be a finite-dimensional vector space over a field $K$, let
$S\le V$, and let $f:S\to V$ be linear and injective. Let
$\pi,g:V\to Q$ be surjective linear maps to the same vector space, with
$\pi f=g|_S$. We seek $P\in\mathrm{GL}(V)$ with $P|_S=f$ and
$\pi P=g$.

For the inverse-transpose interpretation, suppose covectors $a_i$ must
be sent to $b_i$ by $P^{-\mathsf T}$, where both lists are independent.
Use $g(v)=(a_i(v))_i$ and $\pi(v)=(b_i(v))_i$. Then
$P^{-\mathsf T}a_i=b_i$ exactly when $b_i(Pv)=a_i(v)$ for all $v$.
The compatibility hypothesis is equality of the prescribed pairings on
$S$. If the source and target covector lists have dependencies, a common
independent sublist suffices when all corresponding relations agree.

Put

~~~text
H  = ker(g - pi)
A  = S ∩ H
B  = f(S) ∩ H
S0 = {s in S : f(s) = s}.
~~~

Then the minimum of $\operatorname{rank}(P-I)$ is

$$
\operatorname{rank}(g-\pi)+\max(\dim A,\dim B)-\dim S_0.
$$

Equivalently, writing $d(s)=f(s)-s$, the minimum is

$$
\operatorname{rank}(g-\pi)+\operatorname{rank}d
-\min(\operatorname{rank}(\pi d),\operatorname{rank}(g d)).
$$

Indeed $(g-\pi)s=\pi d(s)$ and $(g-\pi)f(s)=g d(s)$ for every
$s\in S$, by compatibility. Thus the ranks of $\pi d$ and $g d$
give the codimensions of $A$ in $S$ and $B$ in $f(S)$,
respectively. Also $S_0=\ker d$ lies in both $A$ and $B$.

## Lower bound

For any admissible $P$, set $F=\ker(P-I)$. Then $F\le H$, since
$gv=\pi Pv=\pi v$ on $F$, and $F\cap A=S_0$.
If $f(s)\in F$, then $P^2s=Ps$. Injectivity of $P$ gives
$Ps=s$ and $f(s)=s\in S_0$. Hence $F\cap B=S_0$ as well.
Applying the dimension formula to $F+A$ and $F+B$ inside $H$ gives

$$
\dim F\le\dim H-\max(\dim A,\dim B)+\dim S_0.
$$

Taking codimensions in $V$ gives the bound.

## Attainment

Choose complements $A'$ and $B'$ of $A\cap B$ in $A$ and $B$.
Take bases $a_1,\ldots,a_u$ of $A'$ and $b_1,\ldots,b_v$ of
$B'$. Let $C$ be a complement of $A+B$ in $H$.
With $p=\min(u,v)$, take

$$
F=S_0\oplus\operatorname{span}(a_i+b_i:1\le i\le p)\oplus C.
$$

This sum is direct. Inside $A+B=(A\cap B)\oplus A'\oplus B'$,
the $A'$ and $B'$ projections of the middle summand are both
injective. Therefore $F\cap A=F\cap B=S_0$, and
$\dim F=\dim S_0+p+\dim H-\dim(A+B)$ reaches the bound.

On $W=S+F$, define $L(s+x)=f(s)+x$ for $s\in S,x\in F$.
The equality $S\cap F=S_0$ makes this well defined. The equality
$f(S)\cap F=S_0$ makes it injective: if $f(s)=-x\in S_0$,
then $f$ fixes $-x$ and injectivity of $f$ gives $s=-x$.
The map $L$ is onto $W'=f(S)+F$ and satisfies $\pi L=g$ on $W$.

To extend $L$, map a basis of $W\cap\ker g$ to its image, a
basis of $W'\cap\ker\pi$. Extend both to bases of the full kernels
and pair the added vectors arbitrarily. Next choose a basis of
$g(W)$ and take lifts in $W$. Pair them with their $L$-images in
$W'$. Complete that quotient basis to a basis of $Q$ and pair any
remaining $g$-lifts with $\pi$-lifts of the same basis vectors.
These pairs specify $P$ between two bases of $V$. They preserve $L$
on $W$ and satisfy $\pi P=g$. In particular $P$ fixes $F$,
so the lower bound is attained. The construction uses basis extensions
and linear solves over $K$, including $K=\mathbb F_2$.

## What invertibility costs

For arbitrary endomorphisms $T$ with the same equations $T|_S=f$
and $\pi T=g$, the minimum rank of $T-I$ is

$$
\operatorname{rank}(g-\pi)+\operatorname{rank}d-\operatorname{rank}(\pi d).
$$

In this case every fixed space lies in $H$ and meets $A$ in $S_0$.
For attainment take $S_0$ plus a complement of $A$ in $H$ as
the fixed subspace and define $L$ as before. On a complement of
$S+F$ extend $L$ by choosing any $\pi$-lift of $g$ on each
basis vector. This proves the relaxed formula. The increase imposed
by invertibility is exactly
$\max(0,\operatorname{rank}(\pi d)-\operatorname{rank}(g d))$.

For a smallest-dimensional example with a strict increase, take
$V=K^2$, $S=Ke_1$, $f(e_1)=e_2$, $\pi=(0,1)$ and
$g=(1,1)$. The two constraint equations force the shape

$$
P=\begin{pmatrix}0&a\\1&1\end{pmatrix}.
$$

At $a=0$ the matrix is singular with correction rank one.
If $a\ne0$, both $\det P$ and $\det(P-I)$ equal $-a$.
The invertible minimum is two over every field. In dimensions at most
one, no strict increase is possible. A nonzero $d$ in dimension one
requires $S=V$, where the injective $f$ already fixes the whole
completion. If $d=0$, the two formulas coincide.
