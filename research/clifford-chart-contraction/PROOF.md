# A compact observation at the width-13 identity decoder

## Producer and observation

Fix four qubits per register, thirteen registers, and the identity-coefficient row of apoursh's #7800 at **fdc90699f4a64139ed6d84cdbf9a606ff0ccd32e**. The 104-bit computational address is the 52-bit row followed by the 52-bit column. Our producer is Ali Romman's #5704 signature constructor at width 104. Its chart has independent 104-bit columns of a linear map $D$, an offset $o$, a quadratic phase $q$ modulo four with even mixed terms, and an absolute scalar $c=(a+ib)/2^e$. It gives $Y[o+Dx]=c i^{q(x)}$ for each binary $x$ and zero elsewhere. A sum of producer charts costs a separate contraction per chart. The input contains no decomposition into the decoded Clifford columns. Global circuit phases are retained. Additions inside vector or mask arguments below are over the binary field.

Split a raw address linearly as $(S,V)$. The low twelve nibbles of $S$ are the XORs of adjacent nibbles for the six row pairs and then the six column pairs. The high nibble is the XOR of the singleton row and column. $V$ comprises the second nibble in each pair, then the row singleton. This is invertible because a pair can be reconstructed from its XOR and second nibble, and the column singleton equals the row singleton plus their XOR. The published row has 22 shift keys $s$ with zero high nibble. Its value at address $(s,v)$ is

$$2^{-12}\sum_{(w,n)\text{ at }s} n(-1)^{w\cdot v}.$$

The frozen compiler returns 4,265 terms with total absolute numerator 12,800. Other shifts have weight zero. This is a linear evaluation of $Y$ without conjugating $c$. [#7800 raw cost and weight formula](https://github.com/apoursh/integer-mult-bounds/blob/fdc90699f4a64139ed6d84cdbf9a606ff0ccd32e/research/clifford-sparse-row/COST.md)

## All shifts share the same phase spectrum

Eliminate $SD$ once. Write $K$ for a matrix of independent kernel columns and $d$ for its column count. For a consistent shift take any witness $t$ with $SDt=s+So$. The producer parameters over that shift are precisely $t+Ku$. Inconsistent shifts contribute zero. The map $VDK$ is injective because $(S,V)$ is invertible and $DK$ is injective. Thus $d\le52$, even for a producer of full rank 104.

Let $B$ be the binary symmetric polar matrix defined by

$$q(x+y)=q(x)+q(y)-q(0)+2x^TBy\pmod4.$$

Its diagonal gives the linear coefficients modulo two, and its off-diagonal entries are half the mixed coefficients. Set $p(u)=q(Ku)-q(0)$, $v_t=V(o+Dt)$, and $F(m)=\sum_u i^{p(u)}(-1)^{m\cdot u}$. Then term $(w,n)$ contributes exactly

$$\frac{cn}{4096}\,i^{q(t)}(-1)^{w\cdot v_t} F\big(K^TBt+(VDK)^Tw\big).$$

This identifies one quadratic polynomial $p$ shared by all 4,265 frequencies across all 22 address buckets.

Let $H$ be the polar matrix of $p$. For $z\in\ker H$, $p(z)$ is even by applying the polar identity to $x=y=z$. Moreover $p(z)/2$ is linear on the radical. Choose $m_0$ satisfying $m_0\cdot z=p(z)/2$ on a basis of the radical. The solutions form exactly $m_0+\operatorname{im}H$, since $H$ is symmetric. A shift by $z$ in the sum for $F(m)$ proves it vanishes outside this affine space. For $m=m_0+Hv$, shift the summation variable by $v$ to obtain

$$F(m)=i^{-p(v)}(-1)^{m_0\cdot v} F(m_0).$$

This is independent of the preimage $v$. In fact $|F(m_0)|^2=2^{d+\dim\ker H}$. In the square, pair indices $u$ and $u+z$. Summing over $u$ kills all $z$ outside the radical and the anchor cancels the remaining phases. Only $F(m_0)$ requires the credited #5727 Gauss-sum routine. Its input is $p(u)+2m_0\cdot u$. All other nonzero values are Gaussian-unit rotations of its output. An empty shift intersection skips the Gauss sum entirely.

A single **weighted Walsh cell** with independent mask rows $M$, signature $b$, and numerator $n$ is covered by the same algorithm. Replace its bucket terms by $(M^Tw,n(-1)^{b\cdot w})$ for all $w$ on the signature bits and multiply the denominator by $2^{\operatorname{rank} M}$. This is the binary character formula for the indicator $Mv=b$.

## General cost in the declared input model

The public command reads its JSON circuit file once and reports the exact byte count $L$. It builds the signature through the unchanged #5704 gate implementation, whose circuit-dependent work and gate restrictions carry over. The contraction begins at that returned chart. An observation already supplied as a chart needs its offset, scalar, independent columns and phase terms read once into working memory. Converting an arbitrary dense array to a chart is a separate problem. The unchanged #7800 program generates the 4,265 fixed terms once. A packed representation can store each frequency in 52 bits and each signed weight in nine (the absolute maximum is 128), plus 22 keys and bucket lengths. Python containers have additional object overhead.

Let $r\le104$ be the chart rank. Use words wide enough for a 104-bit binary mask. One pivot elimination of $SD$, one for $H$, and one linear system for $m_0$ suffice apart from the internals of the single scalar Gauss routine. A per-shift witness gives $v_t$, $q(t)$ and the twist $K^TBt$. Each term then takes at most $d$ parity products to project its frequency, $d$ pivot steps, and one phase evaluation on at most $1+d+\binom d2$ monomials, plus constant overhead. With the retained substitution-based implementation, a conservative total word-operation bound after row compilation and chart production is

$$O\big(r^2(d+1)^2+(d+1)^5+22(r+1)^2+4265(d+1)^2\big).$$

For the middle term the retained scalar routine eliminates at most $d$ variables. A generic substitution visits at most quadratically many old terms and expands each into at most quadratically many new ones. Peak dynamic working storage beyond the fixed compiled source tables is $O((r+1)^2+(d+1)^2+4265)$ mask/coefficient words, plus the Gaussian integers. The algorithm avoids enumeration of the $2^d$ coordinates. The unit-rotation accumulator has components at most 12,800 in absolute value. Each component of the Gauss result has absolute value at most $2^d$. Before reducing the final denominator $2^{e+12}$, each output numerator has absolute value at most $2^{d+1}12800(|a|+|b|)$, including multiplication by the producer scalar. The procedure reads the chart without mutation and can release the transient arrays on return.

## A priced active cell on a phase-mask tape

For each of the six adjacent register pairs, call the free second row and column nibbles $r_j,s_j$. On all $2^{104}$ raw addresses $A$ supply the normalized amplitude

$$Y_h[A]=2^{-52}(-1)^{\sum_{j=1}^6r_j\cdot s_j+h\cdot A},\qquad h\in\mathbb F_2^{104}.$$

These are actual #5704 outputs. Apply the positive translation root on each coordinate, then a diagonal phase cancelling the independent root phases and introducing the shown quadratic pairs and linear sign. The accumulated root scalar is $(1+i)^{104}/2^{104}=2^{-52}$. At $h=0$ exchanging a coupled second register with its uncoupled neighbor changes an amplitude. Every tensor power in the decoded alphabet is permutation-invariant, so this observation is outside their entire linear span.

Choose the source bucket with shifts $(0,0,0,0,0,4)$ on both sides, and signature 2 in its three masks (compiled values in *cell_tape.py*). The weight of this cell is $128/4096=1/32$. For each of the eight indicator frequencies $w$, the effective free-variable frequency is the XOR of $M^Tw$ and the restriction of $h$ to the free coordinates. Write its first 24 bits as $\alpha$, the next 24 as $\beta$, and its singleton as $\gamma$. Each pair contributes $16(-1)^{\alpha_j\cdot\beta_j}$ by Fourier orthogonality on one nibble. The singleton contributes 16 if $\gamma=0$ and zero otherwise. Including the $1/8$ from the indicator leaves the fixed denominator $2^{32}$. The numerator is a signed sum of at most eight units.

On a read-only binary tape supply the 104 bits of $h$ directly, in the order consumed. For each pair and bit, an adjacent quartet $(a,b,c,d)$ holds the two row and two column phase bits. The final eight symbols give the two phase bits of each singleton bit. On the corresponding free coordinates $h$ adds $a+b,c+d$, and on the shift it adds $a x'_j+c x_j$. Expanding $(\alpha+a+b)(\beta+c+d)$ in one coordinate changes $\alpha\beta$ by $(a+b)(c+d)+(a+b)\beta+(c+d)\alpha$. For each quartet this plus the shift phase is an eight-bit flip mask on the eight signs. The fixed table has 24 rows of 16 one-byte masks. Four singleton XORs select one of 16 one-byte eligibility masks. A one-byte initial phase mask includes the eight indicator and constant Fourier signs. The entire fixed lookup payload is **401 bytes** (384+16+1).

One evaluation reads exactly **104 binary symbols**, moves its input head **104 positions forward and 104 back**, writes zero input symbols, and emits an integer in $[-8,8]$ with implicit denominator $2^{32}$. With a fixed controller the mutable data include an eight-bit sign register, up to four quartet/singleton bits and a temporary incoming/partial bit. The final eligibility byte and five-bit signed output can reuse that space. Reserving these registers separately takes 26 bits (8+4+1+8+5). The fixed arithmetic uses 24 table lookups and byte XORs, one eligibility lookup, and a byte intersection, two population counts, a shift and a subtraction for the output. This is a read-only input track plus fixed local controller and ROM model. The loop counters in the executable simulate a fixed finite schedule. Clearing the local registers after copying the output restores the scratch. The 208 count prices input-head motion with no external scratch head. The producer supplies the phase bits in the stated order. The test encoder starts from a mask in a random-access word. A differently ordered caller tape entails an extra conversion. Reversible gate or selected-multiplier costs remain open.

At $h=0$ the cell gives $2^{-31}$. For the complete row on this input the same six-pair factorization and singleton selection, applied to all 4,265 raw frequencies, independently give $2^{-29}$. The chart algorithm handles this example with $d=52$, one Gauss evaluation and 603 supported frequencies. All 22 shifts are reached. The verifier also checks 137 phase masks against the general single-cell algorithm with exact head restoration.
