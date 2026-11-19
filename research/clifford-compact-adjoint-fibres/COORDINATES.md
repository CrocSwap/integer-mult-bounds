# Exactly how dense is the adjoint of one computational coordinate?

Even a width-13 chart supported at one raw address produces trillions of nonzero adjoint coefficients. Their exact count depends on the correlations between the row and column nibbles of its 13 sites. The counts below concern the standard point observation with amplitude one. They do not assume a Clifford decomposition of that observation.

| Attained extremum over all raw addresses | Occupied symplectic fibres | Nonzero Pauli-labelled coefficients |
|---|---:|---:|
| Minimum | 21,139,292,160 | 5,411,658,792,960 |
| Maximum | 47,377,612,800 | 8,338,459,852,800 |

## Count for any coordinate

Write $V=\mathbb F_2^n$, $q=2^n$, and denote the raw site row and column nibbles by $(r_i,c_i)\in V^2$. Use $n=4,f=13$ for the counts above. Let $Z$ denote the diagonal Pauli Lagrangian. For a fixed symplectic element $S$, write $H$ for the projection of $SZ$ onto the output $X$ bits and put $h=\dim H$. Let $J$ be the $X$-to-$X$ block of $S$. The support of the zero column of its unitary lift $U_S$ is an affine translate of $H$. Indeed it is stabilized by $SZ$ with specified signs. Diagonal stabilizers give $n-h$ independent support equations; the remaining stabilizer translations generate $H$ and preserve absolute value. Column $c$ is obtained by applying the conjugated input $X^c$, so its support is shifted by $Jc$. Each nonzero matrix entry has absolute value $2^{-h/2}$ by normalization.

For the label $X^xZ^z U_S$ the adjoint entry on this coordinate is a product of $f$ conjugated unitary matrix entries divided by $q^{f/2}$. It is nonzero exactly when the constraints on $x$ at the individual sites agree. With differences from site one, this requires
$$
  \Delta r_i+J\Delta c_i\in H \quad\text{for every }i .
$$
When compatible, $x$ runs through one coset of $H$ and $z$ is arbitrary. Exactly $2^{n+h}$ coefficients survive in the fibre, each of absolute value $2^{-(n+h)f/2}$.

For each candidate subspace $H\le V$, quotient the output by $H$ and write $m=n-h$. The map $\bar J:V\to V/H$ is surjective since the full symplectic map has surjective output $X$ block and the images of the input $Z$ directions generate $H$. The site differences prescribe $\bar J(\Delta c_i)=\overline{\Delta r_i}$ on a subspace of dimension $s=\operatorname{rank}(\Delta c_i)$. If the prescribed pairs do not form the graph of a linear map on that subspace, this $H$ contributes zero. Otherwise let $b=\operatorname{rank}(\overline{\Delta r_i})$ and set $E(a,d)=\prod_{j=0}^{d-1}(2^a-2^j)$ for $d\le a$, zero for $d>a$. The number of surjective extensions is
$$
  2^{b(n-s)}E(n-s,m-b).
$$
To see this, choose a complement to the prescribed domain. Its map to the codomain modulo the prescribed image must be onto, and each such map has $2^{b(n-s)}$ lifts.

The multiplicity of each surjective $\bar J$ at fixed $H$ is
$$
  2^{h(h+1)/2}\,\frac{|P_Z|}{E(n,m)},\qquad
  |P_Z|=2^{n(n+1)/2}|\operatorname{GL}(n,2)|.
$$
Indeed any Lagrangian $L$ projecting onto $H$ satisfies $L\cap Z=H^\perp$. Modulo $H^\perp$, its lifts of $H$ are the graphs of maps $H\to H^*$, with isotropy equivalent to symmetry. This gives $2^{h(h+1)/2}$ choices. The symplectic group acts transitively on Lagrangians by extending a basis to a symplectic basis. For each $L$ there are $|P_Z|$ maps with $SZ=L$. The stabilizer $P_Z$ of $Z$ consists of a general linear basis change and a symmetric shear, giving its displayed order. Right composition with general linear basis changes preserving $Z$ permutes the surjections $V\to V/H$ transitively, so every surjection has the same multiplicity. Summing the product of the extension count and this multiplicity over $H$ counts exactly the occupied fibres.

## Sharp extrema

For $h=n$ the compatibility conditions disappear at every address. This yields the lower bound; take $c_i=0$ and use rows $0,e_1,\ldots,e_n$ among the $f$ sites to force $H=V$. Taking every site equal makes all fibres compatible, attaining the upper bound. These two witnesses exist for $f\ge n+1$. Each occupied rank-$h$ fibre always contributes the same number of entries and the same positive squared norm, so the witnesses also minimize and maximize the squared norm. At width 13 the extrema of $\|A^*\delta\|_2^2$ are $315/2^{70}$ and $87222165730875/2^{70}$, respectively.

For the all-equal address the numbers of compatible fibres by $h=0,1,2,3,4$ are 20,643,840, 619,315,200, 5,780,275,200, 19,818,086,400 and 21,139,292,160. These follow from the same multiplicity or by counting the $h$-dimensional $H$. The computation enumerates only the 67 binary subspaces in dimension four. The independent small-qubit checker generates the 6 and 720 symplectic classes of lifts modulo Paulis in dimensions two and four via actual Hadamard, phase and controlled-NOT matrices. It tests all pairs of site addresses at each size and 240 further multisite lists, for 512 literal comparisons. [Census implementation](coordinate_support.py) · [Small-qubit verification](check_coordinates.py)

## Independent check of the five canonical weights

For a repeated site the canonical calculation in [the main proof](PROOF.md) reduces to a radial Gram on the graph of the 2,295 Lagrangians. The following check uses the earlier quotient character spectrum and the nearest-neighbour graph alone to compute this action, independently of the conjugacy-class displacement computation. Write $i=4-\dim(L\cap L_0)$ and connect vertices sharing a hyperplane. The number of neighbours at distances $i-1$ and $i+1$ is
$$
 c_i=2^i-1,\qquad b_i=2(16-2^i).
$$
Indeed each hyperplane of $L$ extends to two other Lagrangians, since its perpendicular quotient has dimension two. Exactly $2^i-1$ hyperplanes contain $L\cap L_0$. For each of these, one of the other two extensions adds the line cut out by $L_0$ in that quotient, reducing the distance; the other keeps it fixed. If the hyperplane misses part of $L\cap L_0$, the original $L$ already uses the unique line from $L_0$, so both alternatives increase the distance. This gives shell sizes $k=(1,30,280,960,1024)$.

The stabilizer of $L_0$ acts transitively on each shell by extending bases adapted to two Lagrangians to symplectic bases. Consequently the permutation representation has a five-dimensional commutant, one dimension per orbit on ordered pairs. The adjacency matrix has five distinct eigenvalues: with $u(0)=1$, the tridiagonal radial eigenvalue equation
$$
 \theta u(i)=c_i u(i-1)+(30-c_i-b_i)u(i)+b_i u(i+1)
$$
gives and checks $\theta=30,13,3,-5,-15$ at both boundaries. The adjacency algebra thus exhausts the commutant and every eigenspace is an irreducible constituent of multiplicity one. Its projection kernel based at a vertex is a multiple of $u$. Transitivity, the trace and idempotence give its multiplicity $2295/\sum_i k_i u(i)^2$. The respective dimensions are 1, 135, 1190, 918 and 51, each unique among the 81 quotient characters in the frozen #7772 table. Their normalized Gram eigenvalues are, in this order,
$$
 \frac{470624175}{2^{32}},\quad \frac{1132984125}{2^{32}},\quad
 \frac{5790052125}{2^{33}},\quad \frac{15074084025}{2^{33}},\quad
 \frac{22846598775}{2^{32}} .
$$
Project the radial adjoint values onto each $u$, divide by the corresponding Gram eigenvalue, and sum. All five canonical weights and the squared projection norm $478566778595/5856573836677349376$ agree exactly with the displacement-based solve. The norm is strictly between zero and one and all weights are nonzero. [Independent computation](spherical.py) · [Source spectrum](source/width13-spectrum.json)
