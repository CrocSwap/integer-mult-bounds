# Which signatures can two port blocks realize?

## 1. Model and result

Split the rows of $P\in GL_n(K)$ into blocks $A,B$ of sizes $p,q>0$, with $n=p+q$. Column $j$ of $P$ determines the source blocks of message $j$. Row $j$ of $P^{-1}$ determines its reader blocks. The message labels stay fixed. Write $M$ for the two-block mask and abbreviate a pair of masks by two letters in source, reader order. This is the interface of Gonzalo Mier's #3990/#3997 and Nick Petalas's #6691. The question in #6691 asks for two blocks of three ports. [#3997](https://github.com/CrocSwap/integer-mult-bounds/pull/3997) · [#6691](https://github.com/CrocSwap/integer-mult-bounds/pull/6691)

Use the seven counts $(a,s,t,b,f,g,h)$ in order
$$
(AA,AM,MA,BB,BM,MB,MM).
$$
All other mask pairs are forbidden. Define
$$
u=p-a-s-t,\qquad v=q-b-f-g .
$$
The **ordinary conditions** are that $u,v\ge0$ and
$$
(p-a-t=0)\ \Longleftrightarrow\ (q-b-f=0),\qquad
(q-b-g=0)\ \Longleftrightarrow\ (p-a-s=0).
$$
The counts sum to $n$, so $u+v=h$.

**Theorem.** Over every field with more than two elements the ordinary conditions are necessary and sufficient. Over $\mathbb F_2$ they remain necessary. They suffice there unless $u,v$ are both odd and at least one equals one. In those cases the following additional test is exact.

| Free pivot counts | Additional condition over $\mathbb F_2$ |
| --- | --- |
| $u=1,\ v>1$ odd | $s+t>0$ |
| $v=1,\ u>1$ odd | $f+g>0$ |
| $u=v=1$ | $(s>0\ \mathrm{and}\ g>0)$ or $(t>0\ \mathrm{and}\ f>0)$ |

Every ordinary signature has an integer witness with entries $0,1,-1$ and a structural support pattern whose generic signature is exactly the requested one. Thus the generic support census equals the realizable rational census in **all two-block dimensions**. The equality concerns the union over all support patterns. A particular matrix and a generic assignment to that very same entry pattern can have different inverse supports.

For example, the six labels $AM,AM,MA,MA,MM,MM$ have only two exclusively $A$ sources and only two exclusively $A$ readers. Neither individual count reaches three, yet four labels require $A$ pivots. No $3+3$ basis can realize them. This illustrates the joint capacity test that a check of the two counts in isolation misses.

## 2. Find simultaneous pivots

Let $W_A,W_B$ be the two complementary row spaces, let $E_X$ be the coordinates $j$ for which $e_j\in W_X$, and let $F_X$ be the coordinates identically zero on $W_X$. The row-space argument in #6691 works for any block sizes. A source omits $X$ exactly on $F_X$. The expansion of $e_j$ in the rows of $P$ has coefficients in row $j$ of $P^{-1}$. Hence its reader is $A$ alone exactly on $E_A$, and $B$ alone exactly on $E_B$. An $AB$ or $BA$ message would put $e_j$ inside a space whose $j$th coordinate is always zero.

Laplace expansion of $\det P$ along its top $p$ rows supplies a set $I$ of $p$ columns such that the top minor on $I$ and the bottom minor on $J=I^c$ are both invertible. In particular $I$ contains $E_A$ because restriction of $W_A$ to $I$ is injective. It also contains $F_B$ because restriction of $W_B$ to $J$ is surjective. Similarly $J$ contains $E_B\cup F_A$. Thus every $AA,AM,MA$ must go into $I$, and every $BB,BM,MB$ into $J$. The remaining $MM$ coordinates occupy $u$ slots in $I$ and $v$ in $J$.

Order the columns as $I,J$ and independently change row bases within the two blocks. These invertible operations preserve their row spaces, hence all plane-level masks. The resulting matrix is
$$
P_0=\begin{pmatrix} I_p&X\\Y&I_q\end{pmatrix}.
$$
A pivot coordinate in $I$ is in $E_A$ exactly when its row of $X$ is zero. A coordinate of $J$ belongs to $F_A$ exactly when its column of $X$ is zero. Consequently the rows of $X$ that must be nonzero number $p-a-t$, and its required columns number $q-b-f$. For $Y$ the corresponding counts are $q-b-g$ and $p-a-s$. A matrix cannot have an empty set of nonzero rows and a nonempty set of nonzero columns or vice versa. This proves the two equivalences and all the ordinary necessity claims.

## 3. Construct an ordinary witness

Choose the required $I,J$ in label order, allocating any $u$ of the $MM$ labels to $I$. Set $X$ to one on the rectangle of its required rows and columns and zero elsewhere. Set $Y$ to a fixed nonzero scalar $c$ on its required rectangle. The ordinary conditions give exactly the prescribed zero rows and columns, including the cases where an entire rectangle is empty.

Eliminating the bottom-left block gives $\det P_0=\det(I_q-YX)$. Only $MM$ pivots belong to both active rectangles at their respective ends. In particular $YX$ has rank at most one and trace $cuv$. The rank-one determinant identity yields $\det P_0=1-cuv$, in the displayed column order. If $uv$ vanishes in $K$, any nonzero $c$ works. Otherwise exactly one nonzero scalar can fail. Every field larger than $\mathbb F_2$ supplies a choice, and over $\mathbb Q$ the choice $c=-1$ always gives determinant $1+uv>0$.

Giving every supported entry an independent indeterminate leaves the diagonal matching and a nonzero determinant. The two pivot submatrices remain diagonal, so row normalization preserves exactly the same zero rows and columns of $X,Y$. Thus every constructed ordinary pattern has the requested generic signature. Conversely the necessity proof also applies over the rational-function field of a generic matrix. This proves generic equality without enumerating $2^{n^2}$ structural supports. Structural determinant and cofactor tests by matchings are classical. [Edmonds (1967)](https://nvlpubs.nist.gov/nistpubs/jres/71B/jresv71Bn4p241_A1b.pdf)

## 4. The complete binary obstruction

In $\mathbb F_2$ take $c=1$. The construction already works if $uv$ is even. To see exactly what can happen when $uv$ is odd, let $X_0,Y_0$ be the restrictions to the $u$ and $v$ free pivots. For **any** graph matrix with the requested masks,
$$
\det P_0=\det(I_u-X_0Y_0).
$$
Indeed, in $I_p-XY$ an $I$-coordinate outside the free set has either a zero row of $X$ or a zero column of $Y$. Its determinant row or column is the corresponding identity row or column and can be deleted with its matching index. A nonfree $J$-coordinate has either a zero column of $X$ or a zero row of $Y$ and contributes nothing to the remaining product.

Start with both active rectangles filled with ones. Removing one common entry from $X_0$ or $Y_0$ leaves the other core rank one. The product then has trace $uv-1$, even, giving determinant one. The question is whether this deletion preserves the required row and column supports.

- If $u,v>1$ are odd, both are at least three. Delete any core entry of $X$ and its row and column still have other entries.
- If $u=1,v>1$ are odd and $s>0$, delete one entry of $X_0$. Its column is covered by an $AM$ row and its row still has another free column. If $t>0$, delete one entry of $Y_0$ instead. Its row can use an $MA$ column. If $s=t=0$, the only active $I$ row of $X$ and the only active $I$ column of $Y$ are the single free pivot. Every free $J$ coordinate forces a one in both cores. Their product is the scalar $v=1$ in $\mathbb F_2$. No invertible graph matrix is possible. Swapping the block names gives the $v=1,u>1$ row of the table.
- If $u=v=1$, the determinant is $1-xy$ for the two core bits. Setting $x=0$ is possible exactly when the free row can use an $MB$ column and the free column an $AM$ row, so $g,s>0$. Setting $y=0$ requires an $MA$ column and a $BM$ row, so $t,f>0$. If neither deletion is possible, both bits are forced to one. This proves necessity as well as sufficiency.

These arguments use only the counts of the signature. Every possible pivot chart has those same counts, so switching pivots cannot evade an obstruction. A field of characteristic two with at least four elements falls under Section 3.

## 5. Exact prices under monotone support tariffs

Allow a different price $c_j(S,R)$ for each message. Assume enlarging either mask cannot lower that price. The pivots from Section 2 assign every $I$-message to $A$ and every $J$-message to $B$, and the assigned block belongs to **both** masks. A row-permuted coordinate basis realizes the corresponding pure $AA$ and $BB$ messages. Its price is at most that of the original basis. Every assignment of $p$ labels to $A$ and the remainder to $B$ can itself be realized by such a permutation.

It follows that the exact minimum on every field is $\sum_j c_j(B,B)$ plus the sum of the $p$ smallest values $c_j(A,A)-c_j(B,B)$. In particular field-specific omissions cannot affect a monotone additive tariff. This statement permits message-dependent prices and concerns square bases. The matched-plane COPY mass bound for overcomplete scalar factorizations is credited separately to #4365. [#4365](https://github.com/CrocSwap/integer-mult-bounds/pull/4365)

A positive, nonmonotone tariff can distinguish fields. Take $p=q=d\ge2$ and costs $(3,3,3,1,2,2,2)$ in the seven-type order. Writing $L=a+s+t$, its total is $4d+L-b$. If $b=d$ then $E_B$ and $F_A$ both have size $d$ and all remaining messages are $AA$. Otherwise $b\le d-1$. The ordinary minimum is therefore $3d+1$, attained at $L=0,\ b=d-1$. At that equality, an additional $BM$ would saturate $F_A$ and force $E_A$ to have dimension $d$, and an additional $MB$ would saturate $E_B$ and force $F_B$ to have size $d$. Both contradict $L=0$. The sole optimal profile consists of $d-1$ copies of $BB$ and $d+1$ copies of $MM$.

Its free sizes are $(u,v)=(d,1)$. It is binary-realizable when $d$ is even and forbidden when $d$ is odd. For odd $d\ge3$, take $d-2$ copies of $BB$ and $d+2$ copies of $MM$. The free sizes $(d,2)$ have even product and this binary witness costs $3d+2$. Integrality excludes a price strictly between the two. At $d=3$ the two minima are ten and eleven. These prices exhibit a mathematical separation and are not measured decoder costs.

One zero-one witness for the six-port optimum $BB,BB,MM,MM,MM,MM$ is
$$
\begin{pmatrix}
0&0&1&0&0&1\\0&0&0&1&0&1\\0&0&0&0&1&1\\
1&0&0&0&0&0\\0&1&0&0&0&0\\0&0&1&1&1&1
\end{pmatrix}.
$$
Its determinant is $-2$, so it works over the rationals and the three-element field. In the two-element field the theorem rules out **every** witness for that signature, in addition to the singularity of this particular matrix.

## 6. Scope and reproducible counts

For $p=q=3$ the ordinary conditions give 188 count profiles and 33,727 labeled signatures. Binary feasibility leaves 167 profiles and 30,547 labeled signatures. Of the 3,180 excluded codes, 3,150 have a $1$-by-$1$ free core and 15 each have the two one-sided odd obstructions. Each profile represents $6!/\prod_i n_i!$ labelings. Exhaustive matching and finite-field incidence counts, actual matrices, exact inverse checks and prices are described in [VALIDATION.md](VALIDATION.md).

[COUNTING.md](COUNTING.md) sums the pivot categories in $O(pq)$ arithmetic operations, gives the exact size of each exception family, and derives the asymptotic binary deficit. For the six-port case, [PRICE-CERTIFICATES.json](PRICE-CERTIFICATES.json) separates 12 of the 21 missing profiles strictly below all binary profiles under a positive integral additive tariff. The other nine are exact convex combinations of binary profiles and hence cannot beat every binary choice under any linear tariff. A separating price need not make its specified profile the unique ordinary optimum.

The row-space description, four-port constraints and four-port rational census are predecessor results. This package supplies the arbitrary two-block classification, uniform larger-field construction, exact binary exceptions and tariff consequences. Three or more blocks, the full port-level joint zero pattern of $P,P^{-1}$ and physical supplier invoices fall outside the theorem.
