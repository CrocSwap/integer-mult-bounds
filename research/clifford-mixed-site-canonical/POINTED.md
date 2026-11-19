# Twelve repeated sites and an arbitrary singleton

Fix two normalized four-qubit stabilizer vectors $a,b$ in the Gaussian-dyadic lifts of #7821. Put $B=|a\rangle\langle b|$ and take any complex $16$-by-$16$ matrix $C$. This construction returns the canonical Moore–Penrose coefficient of $y=(\mathrm{vec}\,B)^{\otimes 12}\otimes\mathrm{vec}\,C$ at any requested width-13 label. All site orderings have the same coefficients because each dictionary column is a tensor power. The program accepts Gaussian-rational entries for $C$ in the respective stabilizer bases. It includes coherences and arbitrary superpositions. [Pointed-flag implementation](pointed.py) · [Independent verification](check_pointed.py)

## The compatibility projector

In the convention of #7821, column $(S,p)$ has the factor $\mathrm{vec}(V)/4$ with $V=W_pU_S$. Let $L_a,L_b$ be the Pauli-label Lagrangians fixing the lines of $a,b$. For each $u\in L_a$, let $D_a(u)$ be the *signed* Hermitian Pauli fixing $a$ pointwise. Define $D_b(v)$ similarly. Within each Lagrangian the signed Paulis form an ordinary elementary abelian group. For $X=S L_b$, put $I=X\cap L_a$ and $j=4-\dim I$.

The overlap $\tau=\langle a|V|b\rangle$ is nonzero exactly when the two stabilizer signs agree on $I$. Indeed the trace of the two stabilizer projectors is either $|I|/16$ or zero by character orthogonality. Compatibility at $u=S v\in I$ is the equality $D_a(u)=V D_b(v) V^*$. In the nonzero case $\overline{\tau}^{12}=(-1/64)^j$, including the phase in the Gaussian-dyadic lift. This follows as in #7821 from $|\tau|^2=2^{-j}$ and unique factorization in the Gaussian integers. Consequently the raw adjoint coefficient is $4^{-13}(-1/64)^j\,\mathbf1_{\rm compatible}\,\mathrm{Tr}(V^*C)$.

Under the matrix synthesis of #7816, $M_d(S)=\sum_p d_{S,p}W_pU_S$. The operator $C\mapsto D_a(Sv) C D_b(v)$ is diagonal on the trace-orthogonal basis $\{W_pU_S\}_p$ with signs equal to the compatibility characters. Averaging over $Sv\in I$ projects onto precisely the compatible basis matrices. Thus
$$
 M_{A^*y}(S)/16
  = b_j\!\!\sum_{v\in L_b:\,Sv\in L_a} D_a(Sv) C D_b(v),\qquad
 b_j=\frac{(-1/64)^j}{4^{13}2^{4-j}} .
$$
Here $D_a(0)=D_b(0)=1$. The central Gram applies separately to each scalar matrix-entry function on $G=\mathrm{Sp}(8,2)$. The scalar convolution with $F(g)=16^{-12}(-64)^{\dim\mathrm{Fix}(g)}$ is invertible. For the $v=0$ term invert the five-shell function $b_j$ on the unmarked Lagrangians. Each remaining term is a scalar function associated to two **pointed** Lagrangians. Fix $u\in L_a\setminus0$ and $v\in L_b\setminus0$, set $\alpha=(L_a,u)$ and $\beta=(L_b,v)$. Its input function at $S$ is
$$
 f_\alpha(S\beta)=b_{d(L_a,SL_b)}\mathbf1_{\{u=Sv\}} .
$$
Both the unmarked and the pointed inputs are pullbacks along a transitive group action. Convolution pushes forward to the permutation action; inversion commutes with this identification because the convolution is central. Inverting these scalar functions once therefore gives the desired $M_{A^\dagger y}(S)/16$ with the same matrix factors.

## The twenty orbital weights

The set $\mathcal F$ of pointed Lagrangians has $N=2295\cdot15=34425$ members. For $\alpha=(L,u)$, $\beta=(X,w)$ use the tuple
$$
 R(\alpha,\beta)=\bigl(4-\dim(L\cap X),\ [u=w],\ [u\in X],\ [w\in L],\ \langle u,w\rangle\bigr)
$$
with the final entry the binary symplectic pairing. All entries are invariant under simultaneous symplectic action. Fix $(L,u)=(Z,e_1)$; any flag can be carried here via a symplectic basis. The finite orbit certificate enumerates every flag and finds twenty tuples, with 2, 5, 6, 5 and 2 at respective distances 0 through 4. For each tuple it starts at one representative and closes under ten symmetric shears fixing $Z$ pointwise and nine elementary basis changes within the stabilizer of $e_1$. Every generated orbit has exactly the size of its tuple's fibre. This proves that the tuple separates all ordered-pair orbits without assuming the pointed permutation representation is multiplicity-free.

For a central per-element convolution kernel $T$, write $t_k$ for a single entry of its induced matrix between flags of relation $k$, and $n_k$ for the number of flags at this relation from one base flag. For each group conjugacy representative $g_c$ let $D_{ck}$ count the flags $z$ with $R(z,g_c z)=k$. Double-counting ordered flags and transports gives
$$
  t_k=\frac{\sum_c |c|T(g_c)D_{ck}}{Nn_k}.
$$
Compute this for $F$ and its inverse. For the inverse, in the ordinary character formula take the sum of $d_\chi\chi(g_c^{-1})/\lambda_\chi$ over irreducible characters and divide by $|G|$. Here $\lambda_\chi=|\,\chi(1)\,|^{-1}\sum_g \chi(g) F(g)$. The retained rational Galois packet sums are real. Each constituent degree is the identity value of its packet divided by its character norm squared. The two representatives in the sole fused rational class yield the same displacement counts, verified before fusion. These computations use the native class data from #7816 and the standard library.

The checker composes the two induced kernels on all twenty relations, summing over every intermediate flag and obtaining the identity exactly. Summing the inverse's marked targets with a fixed underlying Lagrangian gives the corresponding unmarked matrix entry, since the fifteen marked target fibres partition the transports into that Lagrangian. For a *pointed* input $f_\alpha$ supported only on flags with mark $u$, each output weight requires only the 135 Lagrangians containing $u$. Exactly five unmarked weights $z_j$ and twenty pointed weights $w_k$ remain. All depend only on the alphabet. The optional independent permutation-character check gives the same forward and inverse traces. [Spectral check](flag_spectrum.py)

## Query and support

Use the supplied left and right stabilizer bases so that $a,b$ have coordinate labels $r,c$ and $C$ has coordinates $C_{ik}$. Conjugating all labels by the two given basis changes gives a relative symplectic matrix $S'$ and absolute matrix entries $V'_{ik}$. Write $j=d(Z,S'Z)$. On rows and columns $D_a(u),D_b(v)$ act by the signs $(-1)^{u\cdot(i+r)},(-1)^{v\cdot(k+c)}$. Therefore
$$
 \gamma_{ik}
   =z_j+\sum_{u,v\in Z\setminus0}(-1)^{u\cdot(i+r)+v\cdot(k+c)}
       w_{R((Z,u),(S'Z,S'v))},\qquad
 (A^\dagger y)_{S,p}=\sum_{i,k}\gamma_{ik}\,\overline{V'_{ik}} C_{ik}.
$$
One length-256 Walsh transform (2,048 rational additions/subtractions) supplies all the $\gamma_{ik}$ after 225 relation lookups; only nonzero supplied $C_{ik}$ then contribute to the sum. For each requested Pauli translate the inherited transition routine contracts the three $16$-dimensional basis matrices with absolute phases. Computing the shared table and the basis transitions is included in the program. It uses rational arithmetic without enumerating $|G|$ symplectic maps or the dictionary columns. The interface takes explicit singleton matrix entries; an arbitrary observation producer would incur its own cost. A minimal request, with the singleton different from the repeated matrix unit, is

~~~json
{"row":0,"column":0,"singleton":[[3,2,["2/3","1/5"]]],"queries":[[[1,2,4,8,16,32,64,128],16]]}
~~~

Both real and imaginary answers are nonzero, $-515081410492739/6019539287498757820800000$ and $-515081410492739/20065130958329192736000000$ respectively. Optional `left_basis` and `right_basis` select the bases used both for the repeated site and for the entries of $C$. Example reproduction: pass the object in a file to `python3.12 -B pointed.py input.json`.

For each distance it suffices to enumerate all $16^2$ Walsh frequencies on one representative Lagrangian. Basis changes preserving $Z$ carry any other pair of Lagrangians at that distance to the representative pair; this permutes their linear forms. The numbers of distinct $\gamma$ are respectively 4, 7, 8, 7 and 4, giving thirty distinct nonzero rationals in total. Their least common denominator is $2^{17}\cdot 5878456335448005684375$. Each frequency is realizable by choosing the singleton matrix unit and the labels of the repeated matrix unit. For every such choice some Pauli translate makes $V'_{ik}$ nonzero; in the Gaussian dyadics that entry is a unit since its norm squared is a power of two. The displayed odd part is consequently *sharp* for the family of 12+1 matrix units, and clears the decoder coefficients for Gaussian-dyadic singleton entries. For every same-basis singleton matrix unit the nonzero canonical support consists of precisely the columns where $V'_{ik}\ne0$, hence 8,338,459,852,800 columns by the shell census of #7821.

## Principal angles for the entire variable-singleton subspace

For $C=|i\rangle\langle k|$ in the given bases, let $\alpha=i+r$ and $\beta=k+c$. To compute $\|AA^\dagger y\|^2=\langle A^* y,A^\dagger y\rangle$, use compatibility of the repeated and singleton coordinates. Their nonzero Pauli sets agree or are disjoint according as
$$
 \alpha\cdot Sv=\beta\cdot v\quad\text{for all }v\in Z\text{ with }Sv\in Z
$$
in relative coordinates. If compatible, the sum of $|V'_{ik}|^2$ over that common Pauli set is $16$. At each distance, average $16\,4^{-13}(-1/64)^j\gamma_{ik}$ times the compatibility indicator over all row and column differences of the prescribed zero/nonzero types, then multiply by the number of group elements at the distance. This average gives the exact sum for any fixed differences: independent linear changes of the left and right computational bases act transitively on each nonzero character set and preserve the distance and the uniform sum over $S$. At fixed distance representative the uniform average covers the transported characters on the two representative Lagrangians. The group-element count in shell $j$ is $(|G|/2295)(1,30,280,960,1024)_j$.

| Difference from the repeated matrix unit | Multiplicity | Squared projection norm |
|---|---:|---:|
| Neither coordinate differs | 1 | $478566778595/5856573836677349376$ |
| Exactly one differs | 30 | $34240796149757/767064758258815834521600$ |
| Both differ | 225 | $319403078159153570779/55516311878981796023500800000$ |

The three values are positive, distinct and strictly below one. They are the squared cosines of the three principal angles between the 256-dimensional variable-singleton subspace and the Clifford column span. Indeed, left and right diagonal Paulis in the chosen bases permute the dictionary columns up to phases, so commute with the orthogonal projection. The twelve repeated sites contribute a trivial sign to this action. Distinct singleton matrix units belong to distinct simultaneous characters. Their projections are therefore mutually orthogonal. For a general $C$, multiplying each table value by the appropriate $|C_{ik}|^2$ and summing gives the exact squared projection norm. The intersection of this entire subspace with the Clifford column span is zero. The computational checks also compare literal raw thirteenth-degree products at rotated bases and the $C=B$ specialization against the five-weight solution of #7821. [Exact checks](check_pointed.py)
