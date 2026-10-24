# Address twists: one-sided floor and a two-sided relaxation witness

## 1. Model with free address twists

Fix an address dimension $m$ and $R$ binary roles. Each role holds an element
of $\mathbb F_2[M_m(\mathbb Q)]$, with $[A][B]=[A+B]$. A **paid call** is

$$
D_N([A])=I_R+([A]-1)N,\qquad \operatorname{rank}_{\mathbb Q}A=1,\qquad
N=xy^T,\ x,y\in\mathbb F_2^R,\ y^Tx=1 .
$$

Free operations are binary $GL_R(\mathbb F_2)$ mixing and, new here, a
**twist** of one role $r$ by an additive automorphism

$$
\varphi_{P,Q}(B)=PBQ,\qquad P,Q\in GL_m(\mathbb Z_{(2)}),
$$

acting on that role's content by $[B]\mapsto[\varphi(B)]$ and leaving the other
roles unchanged. Twists may be applied to any role, at any time, any number
of times. Conjugating an XOR by a twist gives a twisted XOR
$f_r\mathrel{+}=\varphi(f_s)$, so the operators form matrices over the skew
group ring $\mathbb F_2[M_m(\mathbb Q)]\rtimes G$. This ring is not
commutative. The predecessors listed in the README exclude exactly these free
address maps.

Roles $0,\ldots,W-1$ are data roles; any further roles are dirty helpers. The
endpoint is

$$
\operatorname{diag}([C_0],\ldots,[C_{W-1}],1,\ldots,1)
$$

as an operator, with every helper restored. The **odd-denominator
hypothesis** is $A_j\in\Gamma:=M_m(\mathbb Z_{(2)})$ for every paid frame.
Because twists preserve $\Gamma$, the submodule $\mathbb F_2[\Gamma]^R$ is
invariant under every operation. The endpoint restricted to it sends
$[0]e_s$ to $[C_s]e_s$, so each $C_s\in\Gamma$. Write $\bar X$ for reduction
modulo two and $\bar\varphi(X)=\bar P X\bar Q$.

## 2. Square-zero image

Let $\Lambda=\mathbb F_2\oplus M_m(\mathbb F_2)$ with $(a,X)(b,Y)=(ab,aY+bX)$.
The map $\pi([A])=(1,\bar A)$ is a ring homomorphism
$\mathbb F_2[\Gamma]\to\Lambda$, because $\overline{A+B}=\bar A+\bar B$. Let
$K=\ker\pi$.

Each operation preserves $K^R$. Paid calls are $\mathbb F_2[\Gamma]$-linear
and mixing is scalar. For a twist, $\pi\circ\varphi=\bar\varphi_\Lambda\circ\pi$,
where $\bar\varphi_\Lambda(c,X)=(c,\bar P X\bar Q)$ is a ring automorphism of
$\Lambda$. Hence $\varphi(K)=K$. Every operation therefore descends to
$\Lambda^R$, and the descended word equals the descended endpoint.

Write a state as $(c,w)$ with $c\in\mathbb F_2^R$ and
$w\in M_m(\mathbb F_2)^R$. The descended operations are:

- mixing $E$: $(c,w)\mapsto(Ec,(E\otimes 1)w)$;
- twist of role $r$: $c$ is unchanged and $w_r\mapsto\bar P w_r\bar Q$;
- paid call: $(c,w)\mapsto(c,\ w+(y^Tc)\,x\otimes\bar A)$, since
  $([A]-1)\mapsto(0,\bar A)$ and $(0,\bar A)(0,X)=0$.

Twists never change $c$, and paid calls do not change how $w$ is transported.
Let $E_{<j}$ be the product of mixings before call $j$, and $\Psi_j$ the
composite of free operations after it, acting on $M_m(\mathbb F_2)^R$. For
$w=0$, the final $w$-part is

$$
w_{\rm fin}=\sum_{j=1}^k(\hat y_j^Tc)\,\Psi_j(x_j\otimes\bar A_j),
\qquad \hat y_j=E_{<j}^Ty_j. \tag{1}
$$

The endpoint requires $w_{{\rm fin},r}=\delta_{rs}\bar C_s$ when $c=e_s$ for
a data role $s$. Let $L$ be the linear map $c\mapsto w_{\rm fin}$, with
coefficients $L[(r,i),(s,l)]$ giving entry $(i,l)$ of block $r$ from $c_s$.

## 3. Theorem A: one-sided twists keep the floor

**Theorem A.** Assume the odd-denominator hypothesis. Suppose also that every
twist used reduces modulo two to a left multiplication
$X\mapsto\bar PX$ (condition L), or every twist reduces to a right
multiplication $X\mapsto X\bar Q$ (condition R). Then every exact word has

$$
k\ \ge\ \sum_{s<W}\operatorname{rank}_{\mathbb F_2}\bar C_s .
$$

This holds for any finite number of dirty helpers and any binary mixing.

*Proof.* Write $A_j=a_jb_j^T$ with $a_j$ primitive in $\mathbb Z_{(2)}^m$.
Some coordinate of $a_j$ is a unit, so $b_j\in\mathbb Z_{(2)}^m$ and
$\bar A_j=\bar a_j\bar b_j^T$.

Under condition L, every map making up $\Psi_j$ commutes with blockwise right
multiplication by a fixed matrix. Mixing acts across roles, and twists act by
left multiplication. Put $B_j=e_1\bar b_j^T$. Then
$x_j\otimes\bar A_j=(x_j\otimes\bar a_je_1^T)B_j$, so

$$
\Psi_j(x_j\otimes\bar A_j)=\Psi_j(x_j\otimes\bar a_je_1^T)\,B_j .
$$

Let $u_j\in(\mathbb F_2^m)^R$ be the first column of
$\Psi_j(x_j\otimes\bar a_je_1^T)$. By (1),

$$
L[(r,i),(s,l)]=\sum_{j=1}^k u_j(r,i)\,\bar b_j(l)\,\hat y_j(s).
$$

This matrix, with rows $(r,i)$ and columns $(s,l)$, is a sum of $k$ matrices
of rank at most one. Its data-to-data block must equal
$\operatorname{diag}(\bar C_0,\ldots,\bar C_{W-1})$, whose rank is
$\sum_s\operatorname{rank}\bar C_s$. A submatrix has rank at most that of the
whole matrix.

Under condition R, every map commutes with blockwise left multiplication.
Write $x_j\otimes\bar A_j=(\bar a_je_1^T)(x_j\otimes e_1\bar b_j^T)$. Let
$v_j(r,l)$ be the first row of the transported block. Then
$L[(r,l),(s,i)]=\sum_j v_j(r,l)\,\bar a_j(i)\,\hat y_j(s)$. With rows $(r,l)$
and columns $(s,i)$, the target block is
$\operatorname{diag}(\bar C_s^T)$, with the same rank. $\square$

The proof uses only the data-to-data block, so the bound also holds when
helper outputs are discarded. With no twists, this is the square-zero bound
of #2110, extended from one lattice $q^{-1}M_m(\mathbb Z)$ to
$M_m(\mathbb Z_{(2)})$. Because $q$ is odd, $\overline{qC}$ and $\bar C$
have the same rank.

**Corollary.** Let the three targets of the three-register model have odd
denominators, with each $\bar C_s$ invertible. Then one-sided twists and any
number of dirty helpers still need nine calls. The untwisted direct column
word uses nine, so nine is the exact minimum in this scoped model.

*Why one-sidedness is needed.* For a two-sided twist,
$\Psi_j(x_j\otimes\bar a\bar b^T)$ can place $\bar P_r\bar a(\bar Q_r\bar b)^T$
in role $r$ with $\bar Q_r$ depending on $r$. Then neither flattening
factors. The witness below shows this matters.

## 4. Proposition B: two-sided twists defeat the square-zero relaxation

Let $m=3$, $W=R=3$, and $C_0=C_1=C_2=I$. Let $\sigma(B)=SBS^T$, where $S$
swaps address axes 0 and 1. This is a simultaneous relabelling: $P=S$ and
$Q=S^T$, so condition L and condition R both fail. Use seven calls:

- **J:** $x=y=(1,1,1)$ with frame $E_{00}$ and no twist.
- **P$_s$** for $s=0,1,2$: twist every role $r\ne s$ by $\sigma$. Then call
  with $x=(1,1,1)$, $y=e_s$ and frame $E_{11}$, and undo the twist.
- **D$_s$** for $s=0,1,2$: call with $x=y=e_s$ and frame $E_{22}$.

**Proposition B.** In every one of the $7!=5040$ call orders, the
square-zero image of the word in $M_3(\Lambda\rtimes G)$ equals that of
$\operatorname{diag}([I],[I],[I])$. No order realizes the endpoint exactly.

For the $L$ part, column $s$ receives three kinds of contribution:

- **J** adds $E_{00}$ to every block.
- **P$_s$** adds $E_{11}$ to block $s$. It adds $\sigma(E_{11})=E_{00}$ to
  every other block.
- **D$_s$** adds $E_{22}$ to block $s$.

Block $s$ therefore receives $E_{00}+E_{11}+E_{22}=I$, and each other block
receives $E_{00}+E_{00}=0$. The constant and twist components agree as well.
`verify.py` checks the full image entry by entry for all 5040 orders. It also
computes each exact skew-ring product and finds no exact order.

Hence no argument that factors through $\pi$ can prove nine calls once
two-sided twists are free; this includes Theorem A and the argument of #2110.
Seven calls pass that relaxation. This is a barrier to the
**method**. It is neither a seven-call word nor a lower bound below nine:
whether two-sided twists can beat nine remains open.

## 5. Checked finite evidence and limits

`verify.py` checks the following with exact finite sets in the skew group
ring:

1. The direct nine-call word is exact, with zero and one dirty helpers.
2. A deleted call and a mutated frame are rejected.
3. In 120 seeded random words per side, with 1–4 calls, 3–4 roles, random
   twists, mixing and odd-denominator integer frames, the correct flattening
   has rank at most $k$. The opposite flattening exceeds $k$ in many of
   these words.
4. Proposition B holds for all 5040 orders, with no exact order.
5. Controls reject the witness against altered targets, untwisted private
   calls and left-only private twists.

The random words corroborate Theorem A; the written proof establishes it.
Proposition B is a finite exact statement about one explicit word family.
Neither result covers clean ancillas, twists not of the form $PBQ$,
even-denominator frames, or any native implementation or price of a twist.
