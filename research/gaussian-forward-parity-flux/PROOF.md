# Forward slack below one half requires unbounded parity mixing

## 1. Statement and conventions

Let
\[
H=\begin{pmatrix}
1&1&1&1\\1&-1&1&-1\\1&1&-1&-1\\1&-1&-1&1
\end{pmatrix},\qquad U=H/2.
\]
All norms are Euclidean. An admissible map is a **total injection**
\(F:\mathbb Z^4\to\mathbb Z^4\) such that
\[
\|F(x)-Ux\|\leq1,\qquad
\|F(x)\|-\|x\|\leq\delta\quad\hbox{for every }x,
\tag{1}
\]
where \(0\leq\delta<1/2\) is fixed. Neither surjectivity, an inverse
rounding rule, a period, a conserved sum nor equivariance is assumed.

Write \(Z_0=\{x:\sum_i x_i\text{ is even}\}\) and
\(Z_1=\mathbb Z^4\setminus Z_0\). Precisely the inputs in \(Z_0\) have an
integral ideal image \(Ux\). Call \(e\in Z_0\) **changed** when \(F(e)\ne Ue\).
An error-one map can change such an input only by a signed coordinate unit,
so every changed even input has an odd-sum output.

Put \(J=\operatorname{diag}(1,1,1,-1)\), \(E=JU\), \(R=UJU\). For odd
positive \(N\), define
\[
C_N=[-N/2,N/2]^4,\qquad
K_N=\#\{e\in Z_0:F(e)\ne Ue,\ E^TF(e)\in C_N\}.
\tag{2}
\]
This counts distinct changed **inputs**, classified by their transformed
output locations. It is not a count of tape operations.

**Theorem 1 (quantitative parity mixing).** For every odd \(N\geq3\) with
\[
\delta<c_N:=N-\sqrt{N^2-N+1},
\tag{3}
\]
every admissible \(F\) satisfies
\[
K_{N+2}-K_{N-2}\geq8.
\tag{4}
\]
In particular, let \(N_0\geq3\) be odd and satisfy
\[
N_0>\frac{1-\delta^2}{1-2\delta}.
\tag{5}
\]
Then, for every integer \(m\geq0\),
\[
K_{N_0-2+4m}\geq K_{N_0-2}+8m\geq8m.
\tag{6}
\]
At least \(8m\) changed even inputs consequently lie in the Euclidean ball
of radius \(N_0-1+4m\).

Thus improving global forward slack below one half requires infinitely
many changes to points whose ideal images are already integral. Their
number grows at least linearly along the explicit sequence in (6).
A finite modification on that class cannot suffice.

**Corollary 2 (the exact-on-integral subclass).** Every total injective
error-one rounder that leaves all integral ideal images unchanged has
forward radial supremum at least \(1/2\). The construction in
[CrocSwap/integer-mult-bounds#7569](https://github.com/CrocSwap/integer-mult-bounds/pull/7569),
at commit 26226aa52337e6e94bc0cdf3cf6b89d16bb42f5f, is a bijection in this
subclass with forward supremum \(1/2\). Using that explicitly cited upper
construction, the subclass optimum is exactly \(1/2\).
The lower theorem in this package is self-contained.

**Example.** If \(\delta\leq3/10\), take \(N_0=3\): at least \(8m\)
changed even inputs have norm at most \(4m+2\), for every \(m\geq0\).
This applies to any global extension at the finite threshold
\(\sqrt{78}-\sqrt{73}<3/10\) from #7571/#7651. It neither constructs
such an extension nor rules it out.

## 2. Exact lattice coordinates

Integer matrix multiplication gives \(U^T=U\), \(U^2=I\), \(R^T=R\),
\(R^2=I\) and \(ER=U\). For \(s=(1,-1,-1,1)^T\),
\(R=I-ss^T/2\).

Split the half-grid \(L_h=(\mathbb Z+1/2)^4\) into
\[
A=\{t:\sum_i t_i\text{ is odd}\},\qquad
B=\{t:\sum_i t_i\text{ is even}\}.
\]
The sum is integral. These are exact bijections:

| Map | Domain | Image |
| --- | --- | --- |
| \(U\) | \(Z_0\) | \(Z_0\) |
| \(R\) | \(Z_1\) | \(A\) |
| \(E^T\) | \(Z_1\) | \(B\) |
| \(E^T\) | \(Z_0\) | \(Z_0\) |

For the first row, the coordinates of \(Hx\) have parity \(\sum x_i\),
\(\sum(Ux)_i=2x_0\), and \(U^2=I\). The last row follows because \(J\)
preserves \(Z_0\). For \(R\), \(s^Tx\) is odd on \(Z_1\), and
\(\sum(Rx)_i=\sum x_i\). Conversely, for \(t\in A\), \(s^Tt\) is odd
and \(Rt\in Z_1\). For \(E^T=UJ\), an odd-sum integer input becomes
half-integral with even coordinate sum. Conversely, if
\(t=(1/2,\ldots,1/2)+z\in B\), then \(z\in Z_0\) and
\(Ut=e_0+Uz\in Z_1\); \(J\) preserves that parity.

For an odd input \(x\), put \(t=Rx\in A\). Equation (1) becomes
\[
\|E^TF(x)-t\|\leq1,\qquad
\|E^TF(x)\|-\|t\|\leq\delta.
\tag{7}
\]
If \(F(x)\in Z_1\), its transformed output \(v\) lies in \(B\).
The difference \(v-t\) is integral, nonzero, and has norm at most one,
so \(v=t\pm e_i\). If \(F(x)\in Z_0\), its transformed output \(z\)
is integral. All coordinates of \(z-t\) are half-integral; (7) forces
each to be \(+1/2\) or \(-1/2\).

For an even input \(e\), its integer output is either \(Ue\), or
\(Ue\pm e_i\in Z_1\). Thus, in the error-one class, preserving total
parity is equivalent to leaving all integral ideal images unchanged.

## 3. Two finite cube facts

Write \(A_N=A\cap C_N\), \(B_N=B\cap C_N\). Each coordinate has \(N+1\)
choices, and reflection of one coordinate reverses color. Therefore
\[
|A_N|=|B_N|=(N+1)^4/2.
\tag{8}
\]
Exactly eight of the sixteen corners belong to \(B\); denote them by
\(Q_N\). A corner with \(k\) negative coordinates has sum \(N(2-k)\),
which is even exactly when \(k\) is even.

**No odd-output escape.** A unit edge from \(t\in A_N\) to
\(B\setminus C_N\) changes one coordinate's magnitude from \(N/2\) to
\(N/2+1\). Its squared-radius increase is \(N+1\). As \(\|t\|\leq N\),
the radial increase is at least
\[
b_N=\sqrt{N^2+N+1}-N>1/2.
\tag{9}
\]
The final inequality follows from
\((N+1/2)^2=N^2+N+1/4<N^2+N+1\).
Thus (1) forbids every such edge. This uses only forward slack; it does
not assume an inverse bound or an invariant-cube contract.

**Missing corners.** The only \(A_N\) neighbors of any \(q\in Q_N\)
are its four inward unit neighbors. They have squared norm \(N^2-N+1\),
while \(\|q\|=N\). Each incoming edge has radial increase exactly \(c_N\).
Under (3), no odd cube input can have transformed output in \(Q_N\).
At equality \(\delta=c_N\), all four edges per corner are allowed;
strictness is essential.

These facts already give a Hall deficiency of at least eight in the
parity-preserving graph on \(A_N\), whose possible outputs lie in
\(B_N\setminus Q_N\). Letting odd \(N\) grow proves Corollary 2's
lower bound.

## 4. Charge every parity exit to a nearby changed even input

Let \(O_N\) count odd inputs represented in \(A_N\) with even output.
Let \(q_N\) count changed even inputs with transformed output in \(Q_N\).
Injectivity and the two cube facts give
\[
|A_N|-O_N\leq |B_N|-K_N-(8-q_N),
\qquad O_N-K_N+q_N\geq8.
\tag{10}
\]
The right-hand capacity removes both outputs already used by even inputs
and the corners not so used. Outputs of unchanged even inputs are even
and do not lie in \(B_N\).

An odd input counted in \(O_N\) has even output \(y=F(x)\). Set \(e=Uy\).
Then \(e\in Z_0\), \(Ue=y\), and \(e\ne x\). Totality and injectivity
force \(F(e)\ne y\); hence \(e\) is changed and \(F(e)=y\pm e_i\) for
some original coordinate unit.

Put \(z=E^Ty\), \(v=E^TF(e)\). Every coordinate of \(z-t\) is
\(\pm1/2\), and every column of \(E^T=HJ/2\) has entries \(\pm1/2\).
Consequently
\[
v-t=(z-t)+E^T(F(e)-y)\in\{-1,0,1\}^4.
\]
It follows that
\[
t\in C_N\Longrightarrow v\in C_{N+2}.
\tag{11}
\]
Different odd inputs give different \(y\), and therefore different \(e\):
\[
O_N\leq K_{N+2}.
\tag{12}
\]
This is an injective charge to actual changed even inputs, with no
surjectivity, uncharged vacancy or inverse assumption.

For \(N\geq3\), the corners \(Q_N\) are outside \(C_{N-2}\), so
\[
q_N\leq K_N-K_{N-2}.
\tag{13}
\]
Equations (10), (12) and (13) yield (4).

All counted sets are finite because the cubes contain finitely many
output lattice points and \(F\) is injective. The proof requires \(F\)
at the odd cube inputs and at the even inputs \(e=UF(x)\) they generate.
Totality supplies this closure; an arbitrary finite injection need not.

## 5. Consequences and scope

For \(0\leq\delta<1/2\), \(N-\delta>0\), and squaring shows
\[
\delta<c_N
\Longleftrightarrow
N^2-N+1<(N-\delta)^2
\Longleftrightarrow
N(1-2\delta)>1-\delta^2.
\]
Thus (3) holds for every odd \(N\geq N_0\) under (5). Apply (4) at
\(N=N_0,N_0+4,\ldots,N_0+4(m-1)\) and telescope to get (6).
For a changed input counted by \(K_M\),
\[
\|e\|=\|Ue\|\leq\|F(e)\|+1
=\|E^TF(e)\|+1\leq M+1.
\]
This proves the input-ball count.

At \(\delta=3/10\), the right side of (5) is \(91/40<3\).
Also \(\sqrt{78}-\sqrt{73}=5/(\sqrt{78}+\sqrt{73})<3/10\), since
the denominator exceeds \(17>50/3\).

The theorem is a necessary condition, not a sufficient matching.
The linear count is not claimed sharp. It does not establish the
unrestricted forward optimum, a positive limiting density of changed
points, a physical time lower bound, or failure of all-lattice
attainment at the finite threshold.

## 6. Gaussian transfer, novelty and credit

For the ideal pair \(C_+\) in #6509, in real coordinates
\((\Re x,\Im x,\Re y,\Im y)\), signed permutations
\[
S(a,b,c,d)=(a,-b,c,d),\quad L(a,b,c,d)=(a,c,-d,b)
\]
satisfy \(U=LC_+S\). Thus \(F_H(x)=L F_C(Sx)\) transfers error,
injectivity, forward slack, total parity and the class of integral ideal
images exactly. The cube count uses the stated transformed coordinates;
it is not a literal axis-aligned Gaussian input-cube assertion.

This supplies a scoped obstruction for the forward-only question left
open in #7569 and the radius-independent Hall question in #7651.
The exact-sum optimum \(1/\sqrt2\) in #7696 and finite-iterate refinements
#7714/#7743 impose additional hypotheses. They do not settle this
unrestricted matching problem.

The universal proof uses finite counting and exact orthogonal coordinates.
Executable checks corroborate local geometry, strict boundaries and a
finite unrestricted control; finite exhaustion is not the universality
argument. All five selected multiplication assumptions remain. No new
\(\kappa\), complete native caller, tape/storage tariff or multiplication
theorem is supplied.

Credit Jerry Chen / @CubeJerry's #7569 for the half-grid coordinates and
upper construction; #7571 and Nick Petalas's #7651 for the unrestricted
finite Hall problem; Ali Romman's #6509 for the Gaussian pair and #7696
for the distinct exact-sum result; Nick Petalas's #6619 and ywz65's #2589
for the preceding radial obstruction questions. The new work is the
cube-corner count, its injective two-edge charge, and the linear forced
parity-mixing conclusion. Prepared with substantial OpenAI assistance;
no human or formal-kernel acceptance is claimed.
