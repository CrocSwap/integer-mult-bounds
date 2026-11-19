# The raw width-15 Gaussian-dyadic splitting

Let $R=\mathbb Z[i,1/2]$, $G=\mathrm{Sp}_{10}(2)$, and $C$ be the elementary abelian group of 64 alternating shears supported on the first four of the five binary coordinates. For the full five-qubit Clifford alphabet, choose one Gaussian-dyadic unitary lift $U_a$ of each projective class. Let $A_f$ have columns $\operatorname{vec}(U_a^{\otimes f})$, without normalization. The minimum integer width with an $R$-linear left inverse of $A_f$ is **15**.

## From one Bell seed to an integral splitting

Use the seven Bell labels $(0,Z_1,Z_2,Z_3,Z_4,Z_5,X_5)$ and one unpaired tensor factor. Their simultaneous stabilizer in the symplectic label group is $C$. The real controlled-$Z$ lifts of its six generators act trivially on the corrected seed phase. Every left-right translate of the subgroup sum then occurs as a Bell observation after an $R$-linear correction. The explicit correction for seven pairs uses the conjugate singleton $\bar U_a$ and acts linearly on mixture coefficients. All Bell contractions and the final Pauli trace division by 32 use only Gaussian dyadics. These are the seven-pair seed and interpolation implication proved in Sections 1, 2 and 4 of #7803. [Pinned Bell correction and recovery](https://github.com/apoursh/integer-mult-bounds/blob/0fefff647d869054f2e2c4eef3cdcb6e3c60c573/research/clifford-general-width/PROOF.md)

Put $e=64^{-1}\sum_{c\in C}c$ and $I=R[G]eR[G]$. If $1\in I$, expand it in translated subgroup averages, recovering a single symplectic fibre from the seed observations. Translation gives the remaining fibres and trace pairing within a fibre recovers every coefficient. It suffices to show $R[G]/I=0$.

For any field $k$ of odd characteristic, the ideal $k[G]e k[G]$ equals $k[G]$ if and only if every simple $k[G]$-module has a nonzero $C$-fixed vector. Indeed, $eM=M^C$. Every nonzero quotient of the group algebra by a two-sided ideal has a simple module, obtained by taking a maximal left ideal of the quotient. An obstruction therefore supplies a simple module killed by $e$, and conversely any such module witnesses a proper ideal. This argument also applies in the nonsemisimple characteristics.

The module $R[G]/I$ is finite over $R$. Every maximal ideal of $R$ has a finite residue field of odd characteristic. The two-sided ideal commutes with base change at the level of the quotient, by right exactness and by using the finite set of generators $g e h$. An algebraic closure of a residue field is a faithfully flat extension of that field. Thus the vanishing of the quotient over the algebraic closure implies that its residue fibre vanishes. Nakayama's lemma then gives vanishing at each maximal ideal. A nonzero finite module has a maximal ideal in its support, proving the required global implication. This establishes existence of Gaussian-dyadic coefficients for the seed expansion.

## The ordinary and modular tests

The three relevant classes are the identity, a rank-two alternating shear $c_2$, and a rank-four alternating shear $c_4$. Their multiplicities in $C$ are $1,35,28$. For any Brauer character $\varphi$ in odd characteristic define
$$
 b(\varphi)=\frac{\varphi(1)+35\varphi(c_2)+28\varphi(c_4)}{64}.
$$
The restriction to the elementary abelian 2-group is a sum of sign characters. Its eigenvalues lift uniquely to $\pm1$ in characteristic zero, so this exact integer is the dimension of the fixed subspace, including in characteristics that divide the dimension. It is additive on short exact sequences.

The group order is $2^{25}3^6 5^2\cdot7\cdot11\cdot17\cdot31$. For a prime away from this order the ordinary character table gives the Brauer table over an algebraically closed residue field. In modular character theory these are all defect-zero blocks and their ordinary characters reduce irreducibly with unchanged lifted values. All 198 ordinary irreducibles have $b>0$, as found in #7806 and checked again from the three ordinary class columns here. For each of the five available odd-characteristic symplectic tables in CTblLib, the full modular computation gives the following results. [Ordinary predecessor census](https://github.com/apoursh/integer-mult-bounds/blob/b42e665721e76e69d05f24a19bdabee0e0f77c04/research/clifford-five-qubit-threshold/MOMENTS.md) · [CTblLib symplectic table record](https://www.math.rwth-aachen.de/~Thomas.Breuer/ctbllib/ctbltoc/data/S10%282%29.html)

| Characteristic | Irreducible Brauer rows | Least $b$ | Least $b$ on a nontrivial row |
|---:|---:|---:|---:|
| 5 | 162 | 1 | 15 |
| 7 | 187 | 1 | 15 |
| 11 | 195 | 1 | 15 |
| 17 | 192 | 1 | 15 |
| 31 | 195 | 1 | 15 |

At 3, compare the restrictions to the simple plus and minus orthogonal subgroups containing the same $C$. If a nonzero $G$-module had zero $C$-fixed dimension, the additivity and nonnegativity of $b$ would restrict every composition factor in each subgroup to one of its zero rows. At $c_2$ the normalized Brauer trace of such a module would have to be both $-1/31$ and $-67/1309$. The two rational numbers differ, and lifting the involution eigenvalues makes this an equality test in characteristic zero. This proves positivity in the last exceptional characteristic. [Subgroup embeddings, class fusions and all zero rows](THREE.md)

The global argument now gives the raw $R$-left inverse. Given a target row at width 15, tensor it with the linear functional $\operatorname{vec}(U_a)^*/32$ for each extra slot. This preserves its value one on the target and zero on the others, and it also shows that a left inverse at any width below 14 would give one at 14. Width 14 already has a nonzero complex kernel of dimension 6,954,742,423,552 by #7806. Since base change to $\mathbb C$ preserves a left inverse, this proves the lower bound as well. [Pinned width-14 kernel](https://github.com/apoursh/integer-mult-bounds/blob/b42e665721e76e69d05f24a19bdabee0e0f77c04/research/clifford-five-qubit-threshold/PROOF.md)

## Reconstructing the finite table calculation

Write $O$ for the three selected columns of the ordinary character table, $D$ for the ordinary-to-modular decomposition matrix and $B$ for the same three columns of the table of irreducible Brauer characters. The three classes are regular for every odd prime, so $D B=O$. The numerical evidence stores $O$ and the positive entries of $D$, indexed from one. For each of the seven tables a sequence of integer pivots recovers all unknown rows of $B$. Substitution into every ordinary row checks the complete overdetermined system. Ordinary column orthogonality separately checks each group's order, the two centralizers and the vanishing cross products.

The Fourier coefficients of the restricted class function on $C$ provide a second set of integer constraints. The 64 signs have three orbits under change of basis on the four-space, indexed by ranks 0, 2 and 4. The sums of each representative sign over the three original rank classes are respectively $(1,35,28),(1,3,-4),(1,-5,4)$. For example, enumerate the 64 symmetric zero-diagonal bit matrices in off-diagonal order $(12,13,14,23,24,34)$. A representative sign is the parity on none, on coordinate 12, or on 12 plus 34. The replay checks divisibility by 64, nonnegativity and recovery of the full degree from these three multiplicities. GAP's native irreducible Brauer tables independently reproduce all 1,005 modular triples in their published ordering.

The theorem applies to raw observations. At odd width the Hilbert–Schmidt unit normalization contains $\sqrt 2$ when there are five qubits. A normalized inverse follows over the extended ring $R[\sqrt 2]$ by rescaling. None of these existence statements prices the extraction of all fibres, a coefficient-growth bound or a multiplication interface.
