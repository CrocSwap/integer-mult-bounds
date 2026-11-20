# When can one ordinary product return two siblings' sum?

The parent needs the low $m$ bits of $x_1y_1+x_2y_2+c$, with its incoming integer $c$ available at the parent. All congruences below are promises on admissible inputs. Left encoders see the two $x$'s and right encoders see the two $y$'s. The two individual products have no other consumer in this contract.

## A sharp congruence threshold

Let $m\ge 2$ and $1\le a,b\le m$. Write $x_1=x, x_2=x+2^a v, y_1=y, y_2=y+2^b z$. The four parameters are independent subject to their residue widths. Put

$$
A=(x_1+x_2)/2,\qquad B=(y_1+y_2)/2,\qquad d=\max(0,m+1-a-b).
$$

The half sums are integral. Taking each sum modulo $2^m$ before halving gives the same $A,B$ modulo $2^{m-1}$.

**Theorem 1.** The full residue admits a representation $F(x_1,x_2)G(y_1,y_2)+U(x_1,x_2)+V(y_1,y_2)+c\pmod {2^m}$ on every admissible input exactly when $a+b\ge m+1$. Each of the four functions may be nonlinear. The product in this representation returns its ordinary residue directly. A separate joint decoder of arbitrary complexity would change the model.

For every $a,b$ the following implementation is exact:

$$
x_1y_1+x_2y_2+c
=2AB+2^{a+b-1}vz+c\pmod {2^m}.
$$

Use the low $m-1$ bits of $AB$. When $d>0$, use only the low $d$ bits of the second product. For $d=1$, the correction is a single highest-bit toggle. Its control is the AND of the two difference parities, computed by XORing bit $a$ of the two left inputs and bit $b$ of the two right inputs. When $d=0$, the correction vanishes.

**Proof.** Expanding $2(x+2^{a-1}v)(y+2^{b-1}z)$ gives the stated identity and sufficiency. For necessity, set $c=0$ and take mixed differences at the zero input, first with a left coordinate increment and then with a right coordinate increment. The one-sided terms cancel. A product of arbitrary separate functions gives the outer product of the two vectors of differences. On the actual target, using unit increments in $(x,v)$ and $(y,z)$, its matrix is

$$
\begin{pmatrix}2&2^b\\2^a&2^{a+b}\end{pmatrix}.
$$

Subtract $2^{a-1}$ times the first row from the second, then $2^{b-1}$ times the first column from the second. The resulting diagonal entries are $2$ and $2^{a+b-1}$. These operations preserve an outer-product factorization. If the first entry of an outer product equals 2 modulo $2^m$, one of its two factors is odd and hence invertible. The vanishing off-diagonal on that factor's row or column forces the opposite second factor to vanish, so the second diagonal must be zero. This is impossible when $a+b\le m$. In that case $a,b<m$, so both unit increments used in the proof are admissible. This argument handles the zero divisors of the residue ring.

**How much information can the correction require?** Keep the half-sum product at zero by taking $x_1=-2^{a-1}v, x_2=2^{a-1}v$, and the corresponding opposite pair on the right. If $d>0$, all $v,z\pmod{2^d}$ occur. With $z=1$, the uncorrected main product is always zero and the $2^d$ different values of $v$ give different full outputs. The same holds on the right. Any extra, separately encoded inputs to a decoder that already sees this fixed main return must distinguish at least $2^d$ cases per side. A low $d$-bit multiplication attains that information bound. It is a statement about this residual interface. It does not give a minimum gate count for all algorithms.

## What changes if the parent asks for only the high bit?

Take $m\ge3$ and independently odd $x_1,x_2,y_1,y_2\pmod {2^m}$. The required result is bit $m-1$ of the sum of the products, with incoming $c$ known to the decoder. Consider separate, arbitrary encoders into a fixed list of binary polynomial products. Only the returned product coefficients and $c$ reach the decoder. Count every input coordinate across the list, including hardwired coordinates.

**Theorem 2.** The exact minimum total width is $2m-2$ per side. This is a channel-list result with unrestricted decoding. Its attainable construction sends enough information for the decoder to do the arithmetic.

**Proof.** It suffices for the lower bound to fix $c=0$. Put $Q=2^{m-1}, H=Q/2$, and $y_i=1+2t_i$. The output row indexed by $x=(x_1,x_2)$ is the indicator of the upper half of $\mathbb{Z}/Q\mathbb{Z}$ evaluated at

$$
L_x(t)+b_x,\qquad L_x(t)=x_1t_1+x_2t_2,\quad b_x=(x_1+x_2)/2.
$$

Each $L_x$ is surjective. No nonzero translation preserves a half interval. If two rows agree, translating by any member of $\ker L_x$ must leave the other row invariant. Surjectivity gives $\ker L_x\subseteq\ker L_{x'}$; both kernels have the same size. The induced automorphism of the cyclic quotient gives $L_{x'}=uL_x$ for a unit $u$.

An affine permutation preserving the lower half interval $I=[0,H-1]$ has multiplier $+1$ or $-1$. Indeed, $I$ overlaps $I+1$ in $H-1$ places, and only the two shifts $\pm1$ have that overlap. For multiplier $+1$, the translation must vanish. For multiplier $-1$, the intercept must be $H-1$, by reflection of the endpoints. If $u=-1$, both $x_i+x'_i$ are multiples of $Q$, so $b_x+b_{x'}$ is a multiple of $H$; it cannot equal $H-1\pmod Q$. If $u=1$, each coordinate can differ by $Q$, and the two intercepts agree precisely when both top bits flip or neither does.

Thus there are exactly $2^{2m-3}$ different rows, all nonconstant. The simultaneous top-bit flip preserves the full dot product for all odd right inputs, since it adds $Q(y_1+y_2)=0\pmod {2^m}$. In a product-only interface an all-zero code on one side gives a constant row at fixed $c$. Hence $2^w-1\ge2^{2m-3}$, forcing $w\ge2m-2$. Symmetry handles the right side.

For attainment, describe each row class by the $m-2$ inner bits of each odd coordinate and the XOR of the two top bits. Canonicalize by putting the first top bit at zero. Use two channels with respective left/right widths $(2m-3,1)$ and $(1,2m-3)$, hardwiring the shorter operand to one. From these codes and $c$ the decoder can compute the full residue for the two canonicalized pairs, which gives the original output. The construction proves width optimality even when all incoming carries must be served. It makes no single-channel, decoder-time or recursive-price claim.
