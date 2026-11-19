# Independent fixed-space census and Gram trace checks

The width-14 and width-15 rank calculations depend on character projections. As a check on their class assignments, group orders and normalization, `check_moments.py` computes the fixed-space histograms for the three groups directly from subspace orbits. It then checks the first two trace moments of each full Gram matrix, counting zero modes with their regular multiplicities. Only the block side of these comparisons reads the supplied projections.

## Counting fixed spaces from embeddings

Let $G$ be the symplectic group on a binary space of dimension $2n$, or the isometry group of a nonsingular quadratic refinement of sign $\epsilon$. Write $I(k,r)=\prod_{j=0}^{r-1}(2^k-2^j)$ for the number of ordered independent $r$-tuples in a $k$-space. If $C_k$ counts group elements fixing a space of dimension exactly $k$, Burnside's lemma gives

$$
\sum_{k=r}^{2n} C_k I(k,r)=|G|\,a_r .
$$

Here $a_r$ is the number of orbits on ordered independent $r$-tuples. The system is triangular from $r=2n$ down to zero. Witt's extension lemma identifies an orbit with its pullback form on a fixed, labelled $r$-dimensional domain. Thus $a_r$ counts the forms that embed into the specified ambient space.

For a polar form of rank $2h$, let $t=r-2h$ and $m=n-h$. There are $\binom{r}{t}_2 |\mathrm{GL}(2h,2)|/|\mathrm{Sp}(2h,2)|$ such forms: choose the radical and then a nonsingular alternating form on the quotient. In the symplectic case each embeds exactly when $t\le m$.

For the orthogonal groups, fix a vector-space complement to the radical in the domain and refine its polar form to a quadratic form. There are $2^{h-1}(2^h+\delta)$ refinements of sign $\delta$ on this complement for $h>0$; the zero-dimensional complement has positive sign. The restriction on the radical is a linear functional. When $t\le m$, count the possibilities as follows.

- A nonzero restriction contributes $(2^t-1)4^h$. After embedding the nonsingular $2h$-space, choose a nonsingular vector in its orthogonal complement, extend its line to a polar-isotropic $t$-plane, and choose an isomorphism matching the two nonzero linear restrictions. This case necessarily has $t>0$ and $m>0$.
- A zero restriction requires a totally singular $t$-plane in the complementary quadratic space of dimension $2m$ and sign $\epsilon\delta$. If $t<m$, both signs of the embedded nonsingular part are allowed. If $t=m$, only $\delta=\epsilon$ works. The case $t=m=0$ requires exactly the ambient sign.

Summing these counts and solving the triangular system gives every $C_k$. A separate calibration enumerates the binary symplectic transvections on two and four coordinates, forms the symplectic group by closure and filters it for both quadratic signs. The literal fixed-space counts agree for all six small groups. At dimension ten, all three calculated histograms agree with the trivial-character projections.

## Independent Gram moments

Let $d=2^n$ and $N=d^2|\mathrm{Sp}(2n,2)|$. The Gram entry at relative projective operator $U$ is $(\operatorname{tr}(U)/d)^f$. A symplectic element fixing a $k$-space has $2^{2n-k}$ Pauli lifts with nonzero trace, each of squared magnitude $2^k$. This is the Pauli trace support formula used in the Clifford spectrum calculation. The entries along each row have the same absolute-value distribution. As a result,

$$
\operatorname{tr}(K_f)=N,\qquad
\operatorname{tr}(K_f^2)=\frac{N}{d^{2f}}
\sum_k C_k 2^{2n-k}2^{kf},
$$

where $C_k$ is the independently counted symplectic histogram. The checker compares these numbers with $\sum_i d_i^2\lambda_i$ and $\sum_i d_i^2\lambda_i^2$ over all ordinary or Bell blocks at widths 13, 14 and 15, including the regular dimension and nullity. The comparisons test the normalization and lifting factors. The rank proof uses the individual block multiplicities in the main proof.

## The seven-pair seed from #7803

The proposed width-15 seed consists of seven Bell pairs and a singleton. At five qubits its stabilizer $C$ is the group of alternating $4\times4$ binary shears on a fixed isotropic four-space. Among its 64 elements, one is the identity, 35 have rank two, and 28 have rank four (ranks refer to $g-I$). A rank-two alternating form is specified by its two-dimensional radical, with the unique nonsingular alternating form on the quotient. There are $\binom42_2=35$ such radicals. The other 28 nonzero forms have rank four.

A shear at rank $r$ in this family is determined by its isotropic $r$-dimensional image and a nonsingular alternating form on its dual. The symplectic group is transitive on these pairs by extension of an isotropic basis and change of basis in the image. There are $\prod_{i=0}^{r-1}(2^{10-i}-2^i)/|\mathrm{GL}(r,2)|$ choices for the image and $|\mathrm{GL}(r,2)|/|\mathrm{Sp}(r,2)|$ choices for the form. This gives class sizes 86,955 and 21,912,660, respectively. Their natural fixed dimensions are 8 and 6. These two pieces of information uniquely select ordinary table columns 3 and 6 in one-based indexing.

For each irreducible character $\chi$, the fixed-space dimension is the subgroup average $(\chi(1)+35\chi(c_2)+28\chi(c_4))/64$. All 198 values are positive; the smallest is 1. Consequently this particular subgroup average has nonzero projection in every complex simple block and generates the full two-sided ideal over $\mathbb C$. The archived-source extraction checks the two columns and every multiplicity. This is evidence for pursuing the same seed at width 15 over the Gaussian dyadics. The positive-characteristic conditions at odd primes remain open. [General seed and Bell correction](https://github.com/apoursh/integer-mult-bounds/blob/0fefff647d869054f2e2c4eef3cdcb6e3c60c573/research/clifford-general-width/PROOF.md)

Prepared by apoursh with substantial OpenAI Codex assistance. The underlying orbit-counting, Witt-extension and finite classical group identities are classical.
