# One accumulation per Bell read for the entire identity fibre

Use the compiled, normalized four-qubit decoder of #7800, at width 13, with identity symplectic target and real unphased lifts $W_{x,z}=X^xZ^z$. Its 256 outputs are indexed by $16x+z$. All statements concern its specified linear extension on arbitrary observations, including inputs outside the Clifford column span. The compiler supplies 4,265 signed numerators $n$ of total absolute mass 12,800. Output and input tuples each have six Weyl labels. Write $w_o=(t_o,z_o)$ and $w_i=(t_i,z_i)$ for their binary sums. The compiler verifies $t_o=t_i=t$ and unit transport phase on these reads. [Pinned block and phase conventions](https://github.com/apoursh/integer-mult-bounds/blob/fdc90699f4a64139ed6d84cdbf9a606ff0ccd32e/research/clifford-sparse-row/PROOF.md)

## Partial Bell transform

At a 104-bit raw address let $s$ be the twelve 4-bit XORs of adjacent row/column pairs, $v$ the twelve second nibbles and $y=(a,b)$ the two singleton nibbles. These are independent linear coordinates of lengths 48, 48 and 8. For each read take its shift $s$ from the X bits and its frequency $w$ from the Z bits of the twelve ordered labels. Define the partial Walsh transform
$$
T(s,w,y)=\sum_v(-1)^{w\cdot v}Y(s,v,y).
$$
The actual Bell block is $4T$ after undoing column normalization. Applying its singleton corrections translates $y$ by $d=(t_o,t_i)$ and multiplies the entry at the raw location by $(-1)^{\sigma\cdot y}$, where $\sigma=(z_o,z_i)$. Indeed $(W_o T W_i^{-1})_{a+t_o,b+t_i}=(-1)^{z_o\cdot a+z_i\cdot b}T_{a,b}$. Accumulate each corrected block with integer weight $n$. For each $x$ extract the shifted diagonal indexed by corrected column $c$ and apply its four-bit Walsh transform in $c$. Dividing the final array by 4,096 accounts for the Bell factor $4$, compiler denominator $1,024$ and trace factor $1/16$.

Suppose the chart gives $Y[o+Dh]=c_0 i^{q(h)}$ for independent columns of $D$ and zero elsewhere. The scalar is complex and the contraction is linear in it. Let $Lh$ be the $(s,y)$ projection of $Dh$ and $Vh$ its $v$ projection. Write $K$ for a kernel basis of $L$, $k=\dim\ker L$. Because $D$ is injective, $VK$ is injective and $k\le48$. Choose a binary echelon section of $L$. On *all* right sides it returns a linear pair (remainder, preimage); the remainder vanishes exactly on the image. The section tested on $(s,y)+o_{sy}$ returns its remainder and $h$. On the consistent slices the chart parameters are exactly $h+Ku$.

Let $B$ be the polar matrix of $q$, including the parity of its linear coefficients on the diagonal. Set $p(u)=q(Ku)-q(0)$ and $H=K^TBK$. Use the common anchor $m_0$ of #7801, satisfying $m_0\cdot z=p(z)/2$ on $\ker H$. Translation in the finite sum proves
$$
\sum_u i^{p(u)}(-1)^{m\cdot u}
= i^{-p(l)}(-1)^{m_0\cdot l}G,\qquad
G=\sum_u i^{p(u)}(-1)^{m_0\cdot u},
$$
when $Hl=m+m_0$; otherwise the sum is zero by pairing with a radical vector. The anchor exists since $p/2$ is linear on the radical, and $|G|^2=2^{k+\dim\ker H}$ by orthogonality. [Pinned scalar spectrum and retained Gauss routine](https://github.com/apoursh/integer-mult-bounds/blob/9d15f66abc9ccf760ca5f7ea442adeb87b8f7115/research/clifford-chart-contraction/PROOF.md)

Here $m=K^TBh+(VK)^T w$. Apply a fixed echelon section of $H$ to $m+m_0$, giving a second remainder and preimage $l$. Combining the two remainders gives an affine binary syndrome $E(s,w,y)$. The following expression is a quadratic polynomial on *all* addresses, including the inconsistent ones:
$$
P(s,w,y)=q(h)+2w\cdot(o_v+Vh)-p(l)+2m_0\cdot l\pmod4.
$$
Both sections are linear, so all mixed terms remain even after affine substitution. The exact transformed entry is $c_0G\,i^{P(s,w,y)}$ when $E=0$, and zero otherwise. This requires one Gauss sum per chart and avoids storing the full transformed observation.

## A shared basis on the eight singleton bits

Holding $(s,w)$ fixed leaves the same linear part of $E$ on $y$ for every read. Let $U$ be its kernel, with independent columns $u_1,\ldots,u_e$, $0\le e\le8$. A consistent read occupies a single affine coset of $U$, even after the read-dependent singleton translation. Choose the canonical representative $a_0$ of that corrected coset. Its raw representative is $y_0=a_0+d$. Put $v_0=(s,w,y_0)$ and define the common chirp
$$
p_U(h)=P(0,0,Uh)-P(0,0,0).
$$
Writing $B_P$ for the polar form of $P$, the corrected slice at $a_0+Uh$ has scalar phase
$$
i^{P(v_0)+2\sigma\cdot y_0}\,i^{p_U(h)}(-1)^{f\cdot h},\qquad
f_j=B_P(v_0,(0,0,u_j))+\sigma\cdot u_j.
$$
This follows by polarization. In implementing the formula the coset representative and the internal basis indices are separate. The $e$ binary functionals $B_P(-,(0,0,u_j))$ are tabulated once from the differences at zero and the 104 unit vectors.

There are $2^{8-e}$ cosets and $2^e$ modulations per coset. Consequently **one signed Gaussian-unit accumulation in exactly one of 256 bins suffices for a supported read**. Inconsistent reads have no bin. On each coset do a length-$2^e$ Walsh transform on its bins and multiply by the shared pointwise chirp. This reconstructs the full weighted singleton matrix. The sixteen length-16 trace transforms then give all outputs using the absolute scalar $c_0G/4096$. The disjoint coset supports and Walsh orthogonality show that these chirped modulations constitute an orthogonal basis. Its shape depends on the chart but is shared across all reads.

After the chart and fixed list are available, this takes at most 4,265 Gaussian accumulator updates and exactly $256(e+4)\le3,072$ complex additions/subtractions in the two transform stages. Further operations include the binary sections, coefficient projections and phase evaluations, chirp rotations, and the shared final scalar multiplication. The algorithm uses one elimination for each of the two large maps, a radical-anchor solve, and maps on at most eight coordinates. The implementation also reconstructs a section of the polar map after the retained anchor routine. Forming the $e$ polar functionals needs at most $e\cdot104$ extra phase evaluations on sums of basis vectors plus the unit-vector and origin evaluations. Each read computes the syndrome, finds its coset, evaluates its phase, and takes at most eight polar dot products. All of these steps have polynomial cost in the chart parameters; the actual 4,265-term list remains independent of those parameters. Each internal Walsh component has magnitude at most 12,800. Before applying the common scalar, a final trace component has magnitude at most $16\cdot12,800$. The Gaussian anchor has components bounded by $2^k$. Materializing arbitrary dense observations or applying the full normal matrix from #7809 is outside this interface.

## Exact dense and mask-input costs

For a raw address with $x=a+b$, only the outputs with Pauli X label $x$ are affected. All sixteen Pauli Z labels in that sector differ by the fixed sign $(-1)^{z\cdot(b+t)}$, since $t$ depends only on that bucket's X shifts. For $z=0$, translate **every column nibble** by $x$. This keeps all pair shifts fixed, translates each free column nibble by $x$, and sets its singleton to $a$. It therefore adds $z_i\cdot x$ to the pair signs of the old identity row, exactly replacing its singleton sign $(z_o+z_i)\cdot a$ by $z_o\cdot a+z_i\cdot b$. Thus each X sector's nonzero weight set is a bijective translate of the #7800 identity support. The sectors are pairwise disjoint. Together their support size is $16\cdot151\cdot2^{47}=340,021,771,866,472,448$. Reading those addresses suffices. On the all-zero dense observation any unread supported address can be perturbed to change an answer, proving a matching lower bound for deterministic exact adaptive coordinate probes. [Scalar support census and enumerator](https://github.com/apoursh/integer-mult-bounds/blob/fdc90699f4a64139ed6d84cdbf9a606ff0ccd32e/research/clifford-sparse-row/COST.md)

The #7801 coupled full-support producer instead supplies $Y_h(A)=2^{-52}(-1)^{h\cdot A+\sum r_j\cdot s_j}$, where $r_j,s_j$ are the free second row and column nibbles. Write $A,B$ for the singleton row and column nibbles of the mask $h$, and $\alpha,\beta$ for its two sides' adjacent-XOR masks. Let $\theta$ be the dot product of the twelve first mask nibbles with the twelve Bell shifts. Summing each free row/column pair yields $16(-1)^{(w'_j+\alpha_j)\cdot(w_j+\beta_j)}$. Summing over the remaining singleton nibble forces $z=z_o+z_i+A+B$. For $k=z_o+A$ put the signed weight
$$
n(-1)^{\theta+z\cdot t+\sum_j(w'_j+\alpha_j)\cdot(w_j+\beta_j)}
$$
into bin $(z,k)$. Sixteen final length-16 Walsh transforms in $k$ give the output numerators, with denominator $2^{36}$ from $16^7\cdot2^{-52}/4096$. This specialization uses 4,265 signed integer accumulator updates and 1,024 binary Walsh additions/subtractions. A signed 15-bit register per bin suffices as every transform intermediate is bounded by 12,800. Each fixed record can be encoded with 48 shift bits, 48 Z bits and nine signed weight bits; remaining XOR summaries derive from those fields. The implementation stores additional precomputed summaries.

On a read-only track provide $h$ in ascending bit order, start and finish at bit zero, and charge movement in adjacent-symbol steps. Read all 104 bits into working memory and return across the 103 links. This uses 104 probes and 206 head moves. On the **same** mask `e90447f9b4d1553cfdce84821d` in hexadecimal, flipping any one of the 104 input bits changes the output vector. The executable checks the 104 inequalities using exact integers. An adaptive deterministic decoder must probe every symbol on that mask because the unchanged answers to all earlier reads cannot distinguish the corresponding neighbor. In particular it must visit bit 103 and return, proving the 206-move lower bound. These are sharp costs for this producer encoding and head contract. Constructing the mask from another producer and moving local arithmetic or output tapes carry separate costs. [Specialized consumer](phase_mask.py) · [Literal singleton matrix check](check_phase_masks.py)
