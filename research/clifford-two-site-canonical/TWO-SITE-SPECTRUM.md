# Two variable sites: exact rank, kernel and raw singular spectrum

Fix normalized stabilizer lines and write their rank-one matrix as $B=\lvert a\rangle\langle b\rvert$. Leave the last two matrix registers fully variable, including entangled two-site tensors. Let $R$ denote the restriction of the width-13 adjoint to $(\mathrm{vec}\,B)^{\otimes 11}\otimes T$. Independent Clifford basis changes reduce $B$ to the computational matrix unit at $(0,0)$. They permute the dictionary columns up to phase and act unitarily on the variable registers. For a projective Clifford matrix $V$, the corresponding row of $R$ thus contains the monomials
$$
 4^{-13}\overline{V_{00}^{11} V_{ik}V_{hl}} .
$$
The normalization is the dictionary's $\mathrm{vec}(V)/4$. Projective choices multiply an entire row by a common phase and disappear from the normal operator.

**Rank and kernel.** The kernel of $R$ is exactly the antisymmetric sector of the variable sites, of dimension $256\cdot255/2=32640$. Its orthogonal complement has dimension $256\cdot257/2=32896$. The restricted canonical decoder and the orthogonal projection onto the dictionary span have the same kernel, since all three vanish exactly for observations orthogonal to the dictionary. For a linear factorization through a complex feature vector recovering every queried coefficient on arbitrary two-site tensors, 32,896 coordinates are both necessary and sufficient. Sufficiency here is a dimension statement. Store the symmetric part. The sharp norm bounds below apply to the raw adjoint.

Here is a rank proof using a small subensemble. Take flat Clifford matrices with entries proportional to
$$
 i^{q(i)+q'(k)}(-1)^{i^tMk},
$$
where $M\in\mathrm{GL}(4,2)$, and $q,q'$ range independently over computational diagonal Clifford phases. These phases include the single-bit $S$ generators and pairwise $CZ$ generators. On an unordered index pair $\{i,h\}$, the four $S$ characters give the coordinate sums $i_t+h_t\in\{0,1,2\}$. At positions of sum 1 the bits of the two indices are complementary. For any two such positions, the $CZ$ character says whether their 1s belong to the same index. Thus these characters recover the unordered pair, also when there are zero or one differing positions. Orthogonality of the left and right characters separates the unordered row and column multisets. Each sector has one symmetric monomial unless both pairs are distinct, when the direct and crossed matchings give two. In the latter case the ratio of their flat phases is $(-1)^{(i+h)^t M(k+l)}$. Both signs occur for $M$ invertible, since the orbit of the nonzero $k+l$ is all nonzero vectors. Thus the two columns are independent. Antisymmetric tensors vanish by commutativity of scalar products.

## The complete normal operator

Take the orthonormal symmetric monomial basis. An unequal pair of matrix units contributes the sum of its two orderings divided by $\sqrt2$. A repeated matrix unit contributes itself. Character separation as above applies to the entire group because left and right diagonal Clifford multiplications preserve its uniform measure and fix $V_{00}$. The normal operator splits into blocks of size at most two. The four linear-change orbits of unordered row pairs and of column pairs have representatives and multiplicities

| Type | Pair | Count |
|---|---|---:|
| $00$ | $(0,0)$ | 1 |
| $xx$ | $(1,1)$ | 15 |
| $0x$ | $(0,1)$ | 15 |
| $xy$ | $(1,2)$ | 105 |

A block occurs with multiplicity equal to the product of the row and column counts. For a two-dimensional block, use the direct and crossed matchings of the displayed representatives in that order. Entries below are multiplied by $2^{70}$. Triples denote the two diagonal entries and then the off-diagonal entry. Transposing the type pair has the same block entries.

| Output pair | Input pair | Scaled block |
|---|---|---:|
| 00 | 00 | 87,222,165,730,875 |
| 00 | xx | 42,568,162,875 |
| 00 | 0x | 85,136,325,750 |
| 00 | xy | 83,059,830 |
| xx | xx | 5,854,541,334,075 |
| xx | 0x | 5,753,277,558 |
| xx | xy | 11,423,495,286 |
| 0x | 0x | (11,709,082,668,150; 5,753,277,558; −5,675,755,050) |
| 0x | xy | (11,423,495,286; 11,423,495,286; −5,537,322) |
| xy | xy | (846,565,563,510; 846,565,563,510; −815,568,426) |

There are 13 distinct positive squared singular values. The $0x,0x$ block gives two distinct irrational conjugates, each with multiplicity 225. The sharp largest and smallest positive squared singular values are $87222165730875/2^{70}$ and $83059830/2^{70}$, of multiplicity 1 and 210. Their ratio is $2100225/2$. Within the entire flat shell alone the scaled squared singular values are 315, 630, 588 and 672 with multiplicities 256, 3,840, 14,400 and 14,400, respectively.

## Counting the blocks

We give the count on $n$ qubits, $q=2^n$, at width $w>2$. Write the binary symplectic action on $X,Z$ labels as $(x,z)\mapsto (A x+B_0 z,C x+D z)$, with $j=\operatorname{rank} B_0$. Set $U=\operatorname{im}B_0$ and $W=\operatorname{im}B_0^t$. A projective Clifford with nonzero $V_{00}$ has support
$$
 T=\{(i,k): i+U=A k+U\}.
$$
To see this, the image of the diagonal input Paulis translates each column's support by $U$ while the diagonal stabilizers impose $n-j$ independent equations. Thus the support of column zero is a single $U$-coset. It is $U$ when the origin is supported. Conjugating $X_k$ translates this support by $A k$. Symplecticity says $AB_0^t=B_0 A^t$, so the quotient map kills $W$. Since the first $n$ rows of the symplectic matrix are independent, the induced map $E/W\to E/U$ is onto and is an isomorphism. Each nonzero matrix entry has magnitude $2^{-j/2}$. Among the $q^2$ Pauli translates of a fixed symplectic map, exactly $q2^j$ support the origin, by the freedom to translate the output index and choose its Pauli phase label.

For fixed $j$, all choices of $U,W$ and quotient isomorphism are equally likely. Indeed independent left and right computational changes of basis preserve the shell and origin and act transitively on those triples. The number of symplectic elements in shell $j$ is
$$
 |\mathrm{Sp}(2n,2)|\,{n\brack j}_2\,2^{j(j+1)/2}/\prod_{s=1}^n(2^s+1).
$$
For instance, choose the $(n-j)$-dimensional intersection with the fixed diagonal Lagrangian. In its symplectic quotient the transversal Lagrangians are symmetric $j\times j$ matrices. The stabilizer has order $|\mathrm{Sp}|/\prod_s(2^s+1)$, since the full group acts transitively on Lagrangians.

Suppose $i\ne h$, $k\ne l$. When both matchings survive the support test, $a=i+h\in U$ and $b=k+l\in W$ are nonzero. Choose $z$ with $B_0z=a$. The identity for $V Z_z V^*$ expresses $V_{i+a,k}/V_{ik}$ as a phase independent of $k$ times $(-1)^{z\cdot k}$. Consequently the ratio between direct and crossed products is the sign $(-1)^{z\cdot b}$. The pairing $(a,b)\mapsto z\cdot b$ is perfect on $U\times W$: the ambiguity in $z$ is $W^\perp$, and $z\cdot W=0$ implies $a=0$. Conditional on $T$, composing the output with any linear map acting arbitrarily on $U$ and identically on the quotient preserves $T$ and $V_{00}\ne0$. It transports this pairing by the corresponding inverse basis change on $U$. Therefore for fixed $a,b\ne0$ the mean sign is $-1/(2^j-1)$, by summing a nontrivial character on all nonzero vectors. At $j=0$ both matchings cannot survive.

For each graph $T$ let $s,t$ be the indicators for direct and crossed support. The diagonal contributions are proportional to $s,t$, and the off-diagonal to $-st/(2^j-1)$ when appropriate. The common multiplier for the **average** over the graphs in shell $j$ is
$$
 (1+\mathbf{1}_{(i,k)\ne(h,l)})\; q^{1-w}\, 2^{-j(w-1)}\; \#\{S:\operatorname{rank}B_0=j\}.
$$
Indeed the normalization contributes $q^{-w}$, the $q2^j$ translates support the origin, and each surviving product in a normal entry has magnitude $2^{-jw}$. The remaining factor comes from the orthonormal symmetric basis. Summing these exact integers and rationals over $j$ gives the table.

[Exact graph and spectrum calculation](two_site_spectrum.py) · [Independent two-qubit full-group verification](check_two_site_spectrum.py). The latter also checks characteristic-factor multiplicities, irreducibility of the sole quadratic, the sharp extrema and the flat-shell counts. The lower-dimensional control generates all 11,520 projective matrices with explicit Hadamard, phase and CNOT gates and measures products of their entries directly. A separate four-qubit gate check evaluates every supported rectangle in explicit phase-decorated partial-Hadamard matrices. For each nonflat or flat shell with $j>0$ it averages a transitive family of $2^j-1$ linear permutations and measures total interference $-1$ on every such rectangle.
