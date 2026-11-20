# Exact rank of one low product bit

Let \(M_m(x,y)=\lfloor xy/2^{m-1}\rfloor\bmod 2\) for integers \(0\le x,y<2^m\), and let \(R_m=\operatorname{rank}_{\mathbb F_2}M_m\). Then

\[
R_1=1,\qquad R_m=\left\lfloor\frac{2^{m-1}}3\right\rfloor+\left\lfloor\frac{3m}2\right\rfloor-1\quad(m\ge 2).
\]

Equivalently, \(R_2=2\), \(R_3=4\), and for \(m\ge4\),

\[
R_m=R_{m-2}+2^{m-3}+3.
\]

## The monoid algebra and sign block

Work over \(\mathbb F_2\). Let \(A_m\) have basis \([x]\) for nonzero residues \(x\) modulo \(2^m\), with multiplication \([x][y]=[xy\bmod 2^m]\) and the convention \([0]=0\). Write \(1=[1]\). The linear form \(L_m\) on \(A_m\) sends a basis element to the top bit of its residue. The symmetric pairing is \(B_m(v,w)=L_m(vw)\). Its rank is \(R_m\) because the omitted zero operand contributes a zero row and column.

For \(m\ge2\) put \(t=[2]\), \(s=[-1]+1\), and \(u=[5]+1\). For a fixed valuation \(i\), write \(n=m-i\), so the elements of valuation \(i\) are represented by \(t^i\) times units modulo \(2^n\). For \(n\ge2\) these units have the unique form \((-1)^\epsilon 5^k\) with \(\epsilon\in\{0,1\}\) and \(0\le k<d_n=2^{n-2}\). Indeed, \(v_2(5^{2^j}-1)=j+2\) follows by induction since \(5^{2^j}+1\equiv2\pmod4\). Thus the powers of \(5\) are exactly the residues congruent to \(1\pmod4\), while multiplication by \(-1\) gives the other odd residues. This also holds for \(n=2\), where the power subgroup is trivial.

The elements \(t^i u^a\) and \(t^i su^a\), for \(0\le a<d_n\), form a basis in this valuation because the binomial change of basis in the powers of \(5\) and the change of basis in the sign are invertible. In this component \(t^i u^{d_n}=0\), by the characteristic-two power identity and the order of \(5\). The component with \(n=1\) has sole basis element \(t^{m-1}\), and both \(s\) and \(u\) annihilate it. Also \(s^2=0\) on \(A_m\).

Modulo \(2^n\) with \(n\ge2\), negating an odd residue complements its top bit. The paired residues lie on opposite sides of \(2^{n-1}\), since neither is zero or the midpoint. In valuation \(i\), the top bit of a unit modulo \(2^{m-i}\) is the top bit of its multiple by \(2^i\) modulo \(2^m\). It follows that \(L_m(t^i s)=1\) for \(0\le i\le m-2\) and \(L_m(t^i su^a)=0\) for every \(a>0\). In the latter identity, expanding \(u^a=([5]+1)^a\) makes the contributions from the sign pairs sum to \(2^a=0\) in the field. These identities and \(s^2=0\) imply that all \(t^i su^a\) with \(a>0\) are in the radical of \(B_m\). So is \(t^{m-1}+t^{m-2}s\). Each of its two terms pairs to one with \(1\) and to zero with all other basis elements.

Consider now the subspace spanned by \(1,t,\ldots,t^{m-2}\) and \(s,ts,\ldots,t^{m-2}s\). In this order its pairing matrix is

\[
K=\begin{pmatrix}E&T\\T^\top&0\end{pmatrix},\qquad
T_{ij}=\mathbf 1_{i+j\le m-2}\quad(0\le i,j\le m-2).
\]

The antidiagonal of \(T\) consists of ones and the entries beyond it are zero. Thus \(T\) and \(K\) are invertible. The top-left block of \(K^{-1}\) is zero, since the equation \(K(p,q)=(v,0)\) forces \(T^\top p=0\) and hence \(p=0\).

The remaining powers \(t^i u^a\) with \(a\ge1\) pair to zero with all \(t^j s\). Their cross matrix to \(K\) therefore has the form \(\binom{C}{0}\), and eliminating \(K\) makes zero Schur correction to their pairing. After replacing \(t^{m-1}\) by the radical element above, these powers, the sign block, and the radical vectors cover the entire basis. Consequently,

\[
R_m=2(m-1)+r_m,
\qquad r_m=\operatorname{rank} B_m\big|_{V_m\times V_m},
\qquad V_m=\operatorname{span}\{t^i u^a:0\le i\le m-3,\ 1\le a<d_{m-i}\}.
\]

## Degree of the cyclic block and its recurrence

For \(n\ge3\) let \(H_n=2^{n-3}\). The valuation identity gives \(5^{H_n}\equiv 1+2^{n-1}\pmod{2^n}\). Multiplying a unit by this residue flips its top bit. In a component \(n=m-i\), \(u^{H_n}=1+[5^{H_n}]\) in characteristic two. Hence \(L_m(t^i u^{H_n}[5]^k)=1\) for every \(k\). Expanding additional powers of \(u\) then gives

\[
L_m(t^i u^{H_n})=1,\qquad L_m(t^i u^a)=0\quad(a>H_n).
\]

For \(n=1,2\) all positive powers of \(u\) vanish in the component. These facts apply to any product of two monomials in \(V_m\) by adding their valuations and their powers of \(u\).

Take \(m\ge4\) and \(H=H_m\). Within \(V_m\) all powers \(u^a\) with \(a\ge H\) are radical, since every partner contains at least one power of \(u\) and the degree \(H_n\) never exceeds \(H\). On the powers \(u^1,\ldots,u^{H-1}\) the pairing matrix \(G\) is zero at \(a+b>H\) and one at \(a+b=H\). Let \(J\) reverse the order of these powers. Then \(GJ\) is upper triangular with diagonal one, so \(G^{-1}=J(GJ)^{-1}\) has zero entries whenever \(a+b<H\).

Each surviving monomial \(t^i u^b\) with \(i,b\ge1\) pairs with such a power \(u^a\) only if \(a+b\le H_{m-i}\le H/2\). All cross vectors to \(G\) are therefore supported in \(a\le H/2-1\). Any two supported indices have sum at most \(H-2\), so the corresponding submatrix of \(G^{-1}\) is zero. Eliminating \(G\) adds its rank \(H-1\) and makes zero Schur correction to the positive-valuation part of \(V_m\).

In that part, shift the valuation labels \(i\mapsto i-1\). A pair originally at valuations \(i,j\ge1\) is evaluated modulo \(2^{m-i-j}=2^{(m-2)-(i-1)-(j-1)}\) whenever the exponent is positive. If \(a\ge d_{m-i-1}\), its monomial \(t^i u^a\) pairs to zero with every positive-valuation partner, since the product is evaluated in a component of index at most \(m-i-1\). Here \(m-i-1\ge2\) for each \(i\) in \(V_m\), and annihilation of \(u\) covers component index one as well. Removing these extra coordinates leaves exactly the basis of \(V_{m-2}\) after the shift, with exactly its pairing entries. Thus

\[
r_m=H-1+r_{m-2}.
\]

The space \(V_2\) is empty. The sole basis vector of \(V_3\) is \(u\), whose square is zero there. Therefore \(r_2=r_3=0\). The displayed recurrence for \(R_m\) follows. The closed form has the same base values and recurrence, since \(2^{m-1}\) and \(2^{m-3}\) are congruent modulo three. For \(m=1\), only \(M_1(1,1)\) is nonzero.

The same proof restricted to valuation zero gives rank \(2^{m-3}+1\) for the odd-by-odd submatrix when \(m\ge3\). The sign block there is the pairing on \(1,s\) of rank two. The powers below \(H_m\) have rank \(H_m-1\), and all further powers pair to zero after the sign block is eliminated.

## Exact explicit width for this output

Consider any operand-local encodings \(f(x)\in\mathbb F_2^p\) and \(g(y)\in\mathbb F_2^q\) as inputs to any collection of carryless convolutions. A jointly linear decoder for this bit computes \(f(x)^\top Cg(y)\) for a fixed \(p\times q\) matrix \(C\), since every convolution output coordinate is bilinear in the supplied bits. If \(F\) and \(G_0\) have the vectors \(f(x)^\top\) and \(g(y)^\top\) as rows, respectively, then \(M_m=FCG_0^\top\), so \(p,q\ge R_m\). This argument allows arbitrary local encoders and any repetition of their features. If operand-local additive terms are also permitted in the decoder, replacing each entry by its sum with the entries at \((x,0)\), \((0,y)\), and \((0,0)\) cancels those terms. The target matrix is invariant under that operation and the factorization then uses centered features of the same lengths.

Conversely, a rank factorization \(M_m=XY^\top\) over \(\mathbb F_2\) gives two local encoders of length \(R_m\). Put a row of \(X\) in one polynomial and a row of \(Y\) in reverse order in the other. The coefficient of degree \(R_m-1\) in their carryless product is the desired dot product. Thus the minimum total explicit width for the single specified bit is \(2R_m\), which is \(\Theta(2^m)\). The result counts supplied coordinates for this raw unsigned product bit and allows unrestricted computation inside the local encoders.

## Direct check

Run `python3 check.py` in this directory. The script computes every matrix entry from an ordinary integer product and performs elimination over \(\mathbb F_2\). It uses neither the algebraic change of basis nor the recurrence to compute the observed ranks. The saved transcript covers the full and odd-by-odd matrices through \(m=12\).
