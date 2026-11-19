# Characteristic three via the two orthogonal subgroups

Let $G=\mathrm{Sp}_{10}(2)$ and let $C$ be the width-15 subgroup of 64 alternating shears. Every nonzero finite-dimensional $\overline{\mathbb F}_3G$-module has a $C$-fixed vector. We prove this by comparing the Brauer trace of the same involution after restriction to two subgroups. The traces are ordinary integers, including when the module dimension is divisible by 3.

## Realizing the same subgroup twice

Write a vector as $(x,z)$ with five binary coordinates in each half. Use the two quadratic refinements $q_+(x,z)=x\cdot z$ and $q_-(x,z)=x\cdot z+x_5+z_5$. They have respectively 528 and 496 zeros. The group $C$ acts by $z\mapsto z+Mx$, where $M$ is zero off its first four coordinates and is alternating. This preserves each form. In fact $C$ lies in both derived orthogonal groups $H_+=\Omega_{10}^{+}(2)$ and $H_-=\Omega_{10}^{-}(2)$, the simple groups called `O10+(2)` and `O10-(2)` in the ATLAS.

For distinct indices $i,j,k$ among the first four, let $s_{ij}$ be the pair shear for $e_i e_j^t+e_j e_i^t$. Let $T$ send $e_k$ to $e_k+e_i$ on the $z$-space and act contragrediently on the $x$-space. Both $T$ and $s_{kj}$ are involutions in both orthogonal groups. Conjugating the shear by $T$ gives $s_{kj}s_{ij}$. Thus $[T,s_{kj}]=s_{ij}$, which puts every generator in both derived groups.

The 35 nonidentity rank-two shears and 28 rank-four shears each occupy a single class in each $H_\epsilon$. For rank $r$ choose a totally singular image of dimension $r$ and a nonsingular alternating form on its dual. Witt extension and change of basis on the image give a single full orthogonal orbit. Its stabilizer contains an element outside the derived group. Indeed, split off $r$ hyperbolic planes around the image and choose a nonsingular vector in the residual quadratic space of dimension $10-2r\ge2$. Its orthogonal symmetry fixes those planes pointwise and has Dickson invariant one. The orbit therefore stays transitive in the derived group.

After a singular frame of length $j$, its perpendicular modulo the frame has dimension $10-2j$ and the original sign. Each nonzero singular vector in that quotient has $2^j$ lifts. Dividing the resulting ordered frame count by $|\mathrm{GL}_r(2)|$ and multiplying by the number $|\mathrm{GL}_r(2)|/|\mathrm{Sp}_r(2)|$ of alternating forms gives the following class sizes. In each simple orthogonal group the sizes identify unique columns. Both published class fusions agree with the symplectic columns below. In particular two symplectic columns have size 21,912,660, so that size alone cannot distinguish them.

| Group | Rank two, class size (one-based column) | Rank four, class size (one-based column) |
|---|---:|---:|
| $H_+$ | 23,715 (2) | 1,992,060 (4) |
| $H_-$ | 19,635 (2) | 706,860 (4) |
| $G$ | 86,955 (3) | 21,912,660 (6) |

## Excluding a fixed-point-free restriction

On each simple orthogonal module with Brauer character $\varphi$, the dimension of the fixed space is $(\varphi(1)+35\varphi(c_2)+28\varphi(c_4))/64$. Here $c_r$ denotes a fixed member of $C$ of rank $r$. The published decomposition matrices and the ordinary character values at these three columns determine all modular triples. The only rows with zero fixed-space dimension are as follows. The underlying matrices have 97 ordinary rows and 39 modular columns for the plus group and 115 rows and 35 columns for the minus group. [Plus decomposition matrix](https://www.math.rwth-aachen.de/~moc/decomposition/tex/O10%2B%282%29/O10%2B%282%29mod3.pdf) · [Minus decomposition matrix](https://www.math.rwth-aachen.de/~moc/decomposition/tex/O10-%282%29/O10-%282%29mod3.pdf)

| Group | Modular row | Dimension | Trace at $c_2$ | Trace at $c_4$ |
|---|---:|---:|---:|---:|
| $H_+$ | 4 | 868 | −28 | 4 |
| $H_+$ | 10 | 13,888 | −448 | 64 |
| $H_-$ | 7 | 5,236 | −268 | 148 |

Suppose a nonzero $G$-module $V$ has zero $C$-fixed space. Averaging over the 2-group $C$ is exact in characteristic three. Consequently every composition factor in either subgroup restriction has zero fixed space and must appear in this table. Brauer characters are additive along composition series, even if the restricted module is indecomposable. The two plus rows force the Brauer trace of $c_2$ on $V$, divided by $\dim V$, to be $-1/31$. The minus row forces the very same quotient to be $-67/1309$. The unequal rational numbers contradict the existence of $V$.

The geometric checker enumerates all 64 shears, verifies six commutator identities on all 1,024 points, and counts each class in the table. With the original CTblLib 1.3.11 archive as its sole argument it also checks both two-stage class fusions and centralizer orders. The modular calculation and the ideal-to-decoder argument are in the main proof. [Geometric checker](check_orthogonal.py) · [Main proof](PROOF.md)

Prepared by apoursh with substantial OpenAI Codex assistance. New work is Apache-2.0. ATLAS and Modular Atlas character data retain their source attribution.
