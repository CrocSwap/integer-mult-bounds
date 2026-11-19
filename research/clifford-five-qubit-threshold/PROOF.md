# The full five-qubit Clifford alphabet first becomes independent at width 15

Let $H$ be the unitary five-qubit Clifford group over $R=\mathbb Z[i,1/2]$, $Z=\langle iI\rangle$, $P$ its Pauli subgroup (including $Z$), and $V$ its natural complex module of dimension 32. Fix one lift $U_a$ per coset in $H/Z$. The matrix $A_f$ has columns $\operatorname{vec}(U_a^{\otimes f})/32^{f/2}$. Vectorizing each factor and tensoring gives the same columns up to one row permutation. Each has norm one. Choosing different lifts changes them by phases.

**Theorem.** The first width with full complex column rank is 15. At width 14 the rank deficiency is
$$
(528\cdot868)^2+(496\cdot5236)^2=6{,}954{,}742{,}423{,}552.
$$
At 15 the extremal eigenvalues of the normalized Gram matrix are exactly $394477183485/2^{43}$ and $7279231852517625/2^{45}$. The lower and upper endpoints remain valid bounds at every larger width, by the Schur product argument below.

## 1. Scalar sectors and Gram blocks

The Pauli labels form a nondegenerate symplectic space $E=\mathbb F_2^{10}$. The action on the labels identifies $H/P$ with $G=\operatorname{Sp}(10,2)$. Symplectic transvections lift to the dyadic Clifford group using $(1+i)(I+iT)/2$ for Hermitian Paulis $T$. The projective kernel consists of the Pauli labels, since their commutation characters exhaust the dual of $E$ and their matrices span all complex endomorphisms of $V$. Hence $N=|H/Z|=2^{10}|G|=25{,}410{,}822{,}678{,}459{,}187{,}200$.

For any fixed width, act on the regular space of functions on $H$ with the required central equivariance. It has dimension $N$. Each irreducible $\pi$ with the appropriate central character acts in a regular block of dimension $(\dim\pi)^2$. If $\pi$ occurs with multiplicity $m_\pi$ in $V^{\otimes f}$, central character orthogonality gives the normalized Gram eigenvalue
$$
g_\pi=\frac{N\,m_\pi}{32^f\dim\pi}.
$$
Indeed the kernel on representatives is $(\operatorname{tr}(U_a^*U_b)/32)^f$. Summing the central convolution over all lifts contributes a factor $|Z|$ relative to this representative matrix. The orthogonality scalar on the full group is $|H|m_\pi/\dim\pi$ before the $32^{-f}$ normalization, giving the displayed formula. Equivalently, polarizing the Hilbert–Schmidt products of the matrices of $V^{\otimes f}$ yields one matrix coefficient space per present irreducible. In particular an absent block contributes $(\dim\pi)^2$ to the nullity.

These reductions specialize earlier Clifford calculations at other qubit counts. The ordinary and Bell-sector decompositions used here are given below to specify the sign and dimension factors at five qubits. [#6714, scalar character sectors](https://github.com/alephnan/integer-mult-bounds/blob/f7f32a18dde54e67624a9ed9cc7e1b266d9585c0/research/clifford-three-qubit-threshold/PROOF.md) · [#7788, odd trace phase](https://github.com/aliromman/integer-mult-bounds/blob/9a8ce06644700ffa576d99316450bcb52835d6dc/research/clifford-odd-width-spectrum/PROOF.md) · [#7789, orthogonal Bell sectors](https://github.com/aliromman/integer-mult-bounds/blob/a5aa2ae21ae68338390f584b8fca58ecba0df409/research/clifford-bell-sector-spectrum/PROOF.md)

## 2. Odd widths

For $g\in G$ put $d=\dim_{\mathbb F_2}\ker(g-I)$. Choose a lift $U$ to $H$ with $a=\operatorname{tr}(U)\ne0$. To see its existence, conjugation by any lift permutes the Hermitian Pauli basis up to signs. On the fixed labels these signs are a linear character: conjugating a product multiplies the two factors' signs. Pauli translations run through every character on that fixed subspace by nondegeneracy of the symplectic pairing. For a translation canceling the signs, the conjugation trace is $2^d=|a|^2$. Every nonzero trace satisfies this equation by fixed-space character summation. A Gaussian-dyadic number of this norm is a unit phase times $(1+i)^d$: after clearing denominators, unique factorization in $\mathbb Z[i]$ leaves only the ramified prime $1+i$. Consequently $a^4=(-1)^d 2^{2d}$.

At odd $f$, the Pauli group with a given faithful scalar character has one irreducible of dimension 32. For example, fixing the scalar action identifies its twisted group algebra on $E$ with the full matrix algebra spanned by the 1,024 Weyl matrices, or their conjugates. With $V_0=V$ at $f\equiv1\bmod4$ and $V_0=\bar V$ at $f\equiv3\bmod4$, this gives
$$
V^{\otimes f}=V_0\otimes W_f,\qquad W_f=\operatorname{Hom}_P(V_0,V^{\otimes f}).
$$
The action on the Hom space descends to $G$. The same argument on any irreducible of the sector shows that the complete list is $V_0\otimes\rho$ for $\rho$ irreducible on $G$. Evaluating on the lift above and dividing the tensor character by $a$ or $\bar a$ gives
$$
\chi_{W_{13}}(g)=a^{12}=(-64)^d,\qquad
\chi_{W_{15}}(g)=a^{16}/|a|^2=128^d .
$$

The following computations use the ordinary character tables from the ATLAS of Finite Groups distributed with Thomas Breuer's GAP Character Table Library 1.3.11. These are finite external mathematical inputs. [CTblLib release](https://www.math.rwth-aachen.de/~Thomas.Breuer/ctbllib/) · [Group and table record](https://www.math.rwth-aachen.de/~Thomas.Breuer/ctbllib/ctbltoc/data/S10%282%29.html)

To bind a conjugacy class to $d$, let $G$ act on the 1,023 nonzero natural vectors. The action has rank three, since an ordered pair is either equal or independent with symplectic pairing 0 or 1, and an isometry of the two-vector span extends to $E$. Its complex permutation character therefore contains the trivial constituent and two distinct nontrivial irreducibles with multiplicity one. Let $B$ be the adjacency matrix for pairing 1. Every row sum is 512. Two distinct nonzero vectors impose independent linear equations on their common neighbors, giving 256 choices. Hence $B^2=256(J+I)$. On the complement of constants its eigenvalues are $16,-16$, with multiplicities 495 and 527 by the zero trace of $B$. These two eigenspaces are $G$-stable, so they identify the constituents. The table has exactly one character of each degree. The number of fixed natural vectors **including zero** is thus $2+\chi_{495}+\chi_{527}=2^d$ on each class.

For a group $K$ equal to $G$ or one of the subgroups below, store the eleven integers
$$
C_{\rho,d}=\sum_{g\in K:\,\dim\ker(g-I)=d}\overline{\chi_\rho(g)}.
$$
The dimension is invariant under powering a group element by an integer coprime to its order. Thus each sum is Galois invariant and hence integral. Replacing each character value with its normalized rational field trace preserves the sum, including for conjugate rows. The source extractor evaluates the normalized trace of a primitive $m$th root as $\mu(m)/\varphi(m)$ and reads the two subgroup class fusions from the same pinned release. For every row and integer $t$ at issue the multiplicity is $\sum_d C_{\rho,d}t^d/|K|$. The registered checker performs exact division and validates the tensor dimension and normalized Gram trace.

At 13 seven quotient rows have zero multiplicity. Their degrees in table order are 11,935; 81,158; 202,895; 365,211; 405,790; 1,623,160; and 1,826,055. At 15 all 198 multiplicities are positive. Each regular block has dimension $(32\deg\rho)^2$. This proves the width-15 upper bound, yields width-13 nullity 6,466,626,860,503,040, and gives the stated endpoints by taking the minimum and maximum of the 198 eigenvalues. [Projected numerical input](PROJECTION.json) · [Exact certificate](verify.py)

## 3. The decisive even width

At $f=14$, the scalar acts by its square. Write $V^{\otimes14}=(V\otimes V)\otimes W_{13}$. The 1,024 vectors obtained by vectorizing the Weyl matrices $W_u=X^x Z^z$ are the Pauli weight lines in $V\otimes V$: congruence by each real Weyl acts on each line by its commutation sign. Including the scalar and the phase convention for Hermitian Pauli lifts gives the quadratic-refinement labels. More explicitly, the Hermitian lift of a label $p=(a,b)$ has scalar $i^{a\cdot b}$ times $W_p$, up to sign. Its tensor square acts on the line indexed by $u$ with sign $(-1)^{a\cdot b+[p,u]}$. This identifies the weight with the refinement $p\mapsto a\cdot b+[p,u]$. The sign of the chosen Hermitian lift disappears upon squaring. Clifford conjugation transports these refinements by the natural symplectic action.

Nondegenerate binary quadratic forms polarizing to the fixed symplectic form have two isometry types. The action on refinements has orbits of sizes 528 (plus) and 496 (minus), corresponding to the 528 even and 496 odd values of $x\cdot z$ on $u$. For instance $\sum_{x,z}(-1)^{x\cdot z}=32$ gives the difference of the counts, and hyperbolic-plane decomposition classifies each type. Their stabilizers in $G$ are the full orthogonal groups $K_+=O_{10}^+(2).2$ and $K_-=O_{10}^-(2).2$ in ATLAS notation.

For an orbit of size $\ell$ take the preimage in $H$ of its weight stabilizer. Its actual action on the Bell line is a one-dimensional character $\eta$. Each irreducible $\rho$ of $K$ gives an irreducible of $H$ by inducing $\eta\otimes\rho$ from this preimage, of degree $\ell\deg\rho$. Indeed its Pauli weight spaces are transitive with irreducible stabilizer action, so a nonzero invariant subspace must contain them all. Conversely, restriction of any scalar-sector irreducible to $P$ splits into weight spaces because the commutator scalar $-I$ acts trivially. It has one orbit of weights, and removing $\eta$ from the action on one weight space leaves an irreducible stabilizer representation descending to $K$. Under this correspondence the multiplicity in $V^{\otimes14}$ is the multiplicity in $W_{13}|_K$, since the weight line contributes precisely $\eta$.

Apply the projected sum at $t=-64$ after fusing each orthogonal class into $G$. Of the 155 plus rows, only row 9 of degree 868 is missing. Of the 164 minus rows, only row 16 of degree 5,236 is missing. For each omission, replacing $-64$ by $64$ yields a positive numerator and therefore detects loss of the trace phase. Adding the two regular block deficiencies proves the displayed width-14 nullity. The class fusions, degree lists, full dimension sums and zero lists are checked in the replay. [Extraction and source pin](extract.py) · [Five-qubit handoff](https://github.com/apoursh/integer-mult-bounds/blob/0fefff647d869054f2e2c4eef3cdcb6e3c60c573/research/clifford-general-width/README.md)

Finally $K_{f+1}=K_f\circ K_1$ entrywise on the chosen cosets. Taking a Schur product with a positive semidefinite matrix with unit diagonal preserves positive semidefinite order and fixes $I$. Hence full rank and the width-15 eigenvalue enclosure persist at higher widths, while failure at 14 implies failure at every smaller width. This proves $T(5)=15$. It gives a lower bound of 15 on the minimum raw $R$-splitting width; the upper bound of 17 comes from #7803. The complex rank calculation alone says nothing about an $R$-left inverse at 15 or 16.
