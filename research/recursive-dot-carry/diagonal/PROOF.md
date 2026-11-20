# Exact fusion of two scalar returns with a one-sided offset

Suppose a parent needs bit $m-1$ of $xy+uv+C$, where $x,u,y,v,C$ are signed integers, $m\ge 1$, and $u=x+2^d q$ for $d\ge 0$. The offset $q$ may vary with the operands and may be hidden from the parent. The published carryless observation in #7838 concerned raw product bits without operand-dependent side information. This construction changes the boundary to two ordinary integer products with a relation on one side only.

## One wide return and the exact correction

Use the low $m$ bits of the single return $P=x(y+v)$. The ordinary dot product is $P+2^d qv$. If $v\ne 0$, put $s=v_2(v)$ and $\ell=\max(0,m-d-s)$. If $v=0$, take $\ell=0$. For positive $\ell$, let $a=q\bmod 2^\ell$ and $b=(v/2^s)\bmod 2^\ell$. Return

$$
  \operatorname{bit}_{m-1}\bigl(P+C+2^{d+s}(ab\bmod 2^\ell)\bigr).
$$

For $\ell=0$, return the bit of $P+C$. These expressions give the same entire residue modulo $2^m$ as the unfused dot product with the same carry. The decoder needs no division on an unknown integer. It obtains $a$ by subtracting the $\ell$-bit slices of $u$ and $x$ that start at bit $d$. Their lower $d$ bits agree, so this difference gives the low $\ell$ bits of $q$ even when the offset is negative. The division of $v$ by $2^s$ is a shift. The scan that finds the first set bit of $v\bmod 2^m$ also detects the case where the correction vanishes.

For $\ell=1$, the bit of $P+C$ flips exactly when $q$ is odd. In particular, at $d=m-1$ and for unrestricted $v$, XOR the top bits of $u,x$, AND with the low bit of $v$, then XOR with the selected bit of $P+C$. The final XOR is valid after arbitrary incoming carry because the correction is a multiple of $2^{m-1}$.

### Sharpness with arbitrary incoming carry

Fix $x,y,v$ and the wide return $P$. Assume the left input permits the full range of low offset residues. Two offsets $q,q'$ give the same bit for **every** $C$ exactly when $q\equiv q'\pmod{2^\ell}$. The difference of their complete residues is $2^d v(q'-q)$. It vanishes modulo $2^m$ exactly under that congruence. Conversely, write a nonzero residue difference as $0<\delta<2^m$ and set $H=2^{m-1}$. For $\delta\le H$, choose $C$ to send the first residue to $H-\delta$, so the second is $H$. For $\delta>H$, send the first to zero, so the second is already in the upper half. The two bits differ in either case. The wide return stays fixed in both tests.

Thus freedom to omit all offset-dependent information starts at $d+s\ge m$, with $v=0$ also free. Below that threshold, a side return independent of $C$ needs at least $\ell$ bits when all $2^\ell$ offset residues are admissible. The decoder above attains the bound for this fixed wide return. This bound concerns the specified carrier $P=x(y+v)$. A different wide encoding or a carry fixed in advance has a different contract.

For $m=8,d=7,x=83,y=117,v=155,C=177$, both $u=83$ and $u=211$ have the same wide residue 48 and give bits 1 and 0 respectively. Omitting the single correction bit gives 1 on both inputs.

### Ordinary word price

Compare two separate width-$m$ products with one width-$m$ product. The candidate uses $x\bmod 2^m$ and $(y+v)\bmod 2^m$; a sum crossing the boundary therefore incurs no higher grade. The original and candidate both return a fixed-width product and consume the data before releasing its storage. The candidate additionally reads the two slices for $a$, produces $y+v\bmod 2^m$ and adds the correction to the same carry consumer. A straight shift-add correction scans only the $\ell-j$ surviving bits in row $j=0,\ldots,\ell-1$, using at most $\ell(\ell+1)/2$ partial bit products and the same number of ripple positions. One-bit correction uses the gates stated above. All copying, sign conversion if needed, carry scans, initialization, rewind and erasure take $O(m+\ell^2)$ additional work and $O(m)$ space with a fixed number of sequential banks. An encoded carry longer than $m$ can be consumed according to its interface in both versions. Only its low $m$ bits affect this observation.

Under a common fixed-width charge $W(m)$, the two-product oracle fee is $2W(m)$ and the fused fee is $W(m)$. The complete comparison is a saving of one fee minus the additional $O(m+\ell^2)$ work. For example, if $W(m)=\omega(m)$ and $\ell^2=o(W(m))$, the replacement is eventually cheaper in that tariff. If a provider trims the widths, compare the actual grades and substitutes for all calls. A cost upper bound for a multiplier alone gives no lower bound on its fee.

## Exact signed fusion in the pinned Gaussian diagonal

The #7834 scalar consumer evaluates four real word products for a payload $(x,y)$ and public phase $(u,v)$. It sends $xu-yv$ and $xv+yu$ to the same signed truncation routine. [Pinned scalar consumer](https://github.com/CrocSwap/integer-mult-bounds/blob/4f0c67d5bb41d4af5501dcd40b3b388b35e0ff02/research/fine-prime-gaussian-product/fine_ring.py)

Choose $\sigma=1$ if $u,v$ have the same sign, and $\sigma=-1$ otherwise. Set $\Delta=u-\sigma v$. The two exact raw outputs are

$$
  v(\sigma x-y)+\Delta x,\qquad v(x+\sigma y)+\Delta y.
$$

This identity is the signed version of the one-sided offset. Small $\Delta$ gives two wide word calls and two short shift-add corrections for both outputs. For $\Delta=\pm1$, the correction uses one signed add per component. All corrections precede the original rounding. Equality holds as signed integers for both normal and conjugated phases and remains exact after any common incoming carry. The path preserves input access order and output cleanup.

The checked guard requires $|\Delta|\le 2$, equal magnitude widths $w$ for $u,v$, and magnitude widths at most $w$ for both new factors $\sigma x-y,x+\sigma y$. Their sum and difference show that $x,y$ also have width at most $w$. All four old and both new calls therefore have exactly the same width $w$. The guard returns to the original four calls when it fails.

Let $L$ be the signed record width. Testing signs, forming the difference, inspecting operand widths, and making the new factors use a fixed number of linear signed tape scans. The same bound covers holding the payload until both corrections finish, consuming the complete child returns, and erasing and rewinding the banks. With a correction cap $B_\Delta\le 2^w$, the candidate costs two width-$w$ fees plus $O(L+w(1+\log(B_\Delta+1)))$ movement and arithmetic. The source costs four such fees plus linear adapter work. Extra guard work on a failed record is $O(L)$. On the two exact twist diagonals discussed below, $\Delta=0$ and $L=\Theta(w)$.

The rounded public chirp product has a natural source of small nonzero offsets. An exact phase on a diagonal of the complex plane would have equal component magnitudes. For $D$ cached rounded factors, the source bounds the root error by three grid units per factor and its multiplication drop by two. All rounded factors have complex modulus at most one, so the product defect is less than $5D$ grid units. On a diagonal the integer component-magnitude difference is therefore less than $5\sqrt{2}D<8D$. The guard uses the actual integer difference on tape and never assumes the error vanishes.

### Dispatches at reachable geometries

In the first source twist pass of `chirp_middle`, `make_diagonals` supplies `root_word(k, 2*r, f)` for the fastest coordinate $k=0,\ldots,r-1$. For $r\ge8$, the roots at $k=r/4,3r/4$ lie at angles $\pi/4,3\pi/4$. The symmetric interval recursion gives equal magnitudes for these two stored integer pairs, each of width $f$. The first is obtained by applying the same square-root interval to each component of the half-angle of $\pi/2$, and the second by quadrant rotation. The inward root error is under three units and $f\ge16$, so their magnitudes exceed $2^{f-1}$. The prior normalized phase diagonal preserves the half disk by the modulus bound and truncation toward zero. On that disk $|x\pm y|\le 2^f/\sqrt{2}<2^f$. This guarantees the same-width guard, including when one component of the payload is zero.

The pass therefore admits two replacements per outer tuple, each removing two width-$f$ word calls. This gives $4T/r$ fewer scalar dispatches in this pass per middle call, where $T$ is the complete tensor volume. The finite top-level first geometry has $r=8$. The fine selector has $r\ge8$ on its Gaussian branch and $f\to\infty$. At widths $f>8192$, each removed call goes to the cold physical word wrapper. [Pinned word dispatcher](https://github.com/CrocSwap/integer-mult-bounds/blob/4f0c67d5bb41d4af5501dcd40b3b388b35e0ff02/research/fine-prime-gaussian-product/word_multiply.py)

A public fixed block schedule can target these coordinates. The guarded implementation in this receipt tests every supplied phase, so its price includes the linear guard on every failed record too. The resulting count is exact. In the large family $r$ grows faster than a fixed power of the scalar precision, so a per-record guard is not justified by the sparse dispatch count alone.

The direct nonzero fixture has slopes $(3,7)$, target sides $(8,8)$, $q=8186$, $f=8200$ and index 9. Coordinate $(1,1)$ has exact angle $3\pi/4$. The cached components differ in magnitude by one. The control verifies the coefficient independently using the exact floor square roots for $\cos^2(\pi/8)=(2+\sqrt{2})/4$ and $\sin^2(\pi/8)=(2-\sqrt{2})/4$. Omitting the correction changes a signed truncated result. In both orientations, the original dispatcher sends four width-8200 words and the guarded version sends two width-8200 words. The diagnostic substitutes exact integers at the cold physical worker return. The top-level selector uses different slopes for its finite geometries. Its fine guard $4W < B \le \min t_i$ excludes the direct 8-by-8 fixture. The large-width diagnostic covers the legal `chirp_middle` interface and this literal scalar consumer.

The #7834 invoice already charges these scalar words as local acyclic work. The width-preserving change gives no P104 or BIT tariff credit, and no complete asymptotic saving is established for the Gaussian construction.

## Reproduction

Run `python3 -I -B verify.py --source-dir /path/to/checkout/research/fine-prime-gaussian-product`. The verifier authenticates three source modules at #7834 head `4f0c67d5bb41d4af5501dcd40b3b388b35e0ff02`. The complete middle calls use the source's bounded-base word implementation in both directions. The high-width control uses an exact integer return at the cold worker boundary. [Recorded output](RESULT.json) · [Checkout and replay](../CALLERS.md)
