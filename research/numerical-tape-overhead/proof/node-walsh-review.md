# Independent review of the numerical Walsh assembly

I reconstructed the source pencil and its two finite repair conversions, reviewed the [Walsh node](walsh-node.md), and implemented the direct $2$- and $4$-point residue transforms on fixed one-head tapes. The full Walsh clock follows on the supplied binary interchanger, guarded-position and word-multiplication bounds. The Walsh-specific global guard can be reduced to $X=\lceil\log_2(k+2)\rceil\ge 2^{66}$. The finite checks below apply to the direct branch and its group composition. The adaptive branch and its parameter inequalities have a written proof.

## Physical direct branch

The [rule program](https://github.com/CubeJerry/integer-mult-bounds/blob/a2a17b61d943676c757e0bbfaef3f4fae03ab8e5/research/moonshot-overhead-program/sessions/2026-11-26-S008/node-walsh-base.py) takes a $K$-digit odd modulus $M\ge3$, canonical residues of fixed width $K\ge2$, and a canonical binary suffix count $s\ge1$. Modulus and data digits are least significant first, with optional high zero padding. For $q=2$ or $4$, its data stream is $[p][u:q][s][K]$, where $p\ge1$ is inferred from the input end. For each prefix and suffix it returns the words indexed by $v=0,\ldots,q-1$ in precisely the same physical order, with residues

$$
 z_v= \left(\sum_{u<q}(-1)^{\operatorname{popcount}(u\mathbin{\&}v)}x_u\right)c
       \pmod M,\qquad c\in\{1,1/2\}.
$$

The normalized four-point operation has $q=4,c=1/2$. An odd outstanding bit uses $q=2,c=1$. The additional $q=2,c=1/2$ rule tests division by two independently.

All three choices compile before any inputs are seen. Each rule tests one scanned symbol and gives finitely many writes and unit moves. A copy from another scanned binary symbol abbreviates the two cases for that symbol. First split into $q$ lanes in input order, then stage one tuple of $q$ words from their aligned heads. For an output $v$, simultaneously scan the $q$ words and the modulus, writing $T=4M+\sum_u(-1)^{u\cdot v}x_u$ in $K+3$ places. The carry is in $[-4,7]$ by the signed binary update. Since $0\le T<8M<2^{K+3}$, the final carry is nonnegative and its three digits suffice. Seven conditional subtractions of $M$, adding it back when the subtraction borrows, leave the canonical residue. If halving, add $M$ precisely for an odd residue and emit the $K$ digits starting at position one. Otherwise emit them starting at zero. Merge the result lanes in increasing $v$ order and erase all scratch. Every input descriptor and the modulus are preserved, and each head returns to its raw home.

Here is a numerical bound with $V=pqsK$. Forming the $K$-ruler by scanning $M$, converting $s$ to unary, and cleaning both rulers costs less than $40(s+K+4)$ transitions by the [independent unary count](recount-node.md). A split or merge class at one prefix costs $s(2K+3)+3s+3$ for its nested word/suffix loop. Rewinds over all data lanes and the array cross at most $6V+8q+12$ cells over the two rearrangements and the computation boundary. Together with prefix tests and markers, setup, cleanup and the two rearrangements fit $128V$. For the smallest $q=K=2,p=s=1$, the direct formula for the non-data cost gives less than $128V$ as well.

* Per staged tuple, copying its $K$ aligned digits to the $q$ local words, returning their heads and eventually clearing all $q$ costs at most $24(K+6)$.
* Per output, the signed-sum rule reads the $M$ bit, $q$ data bits and emits one transition per digit. Three high writes and the $q+2$ rewinds give at most $16(K+6)$.
* A complete add/subtract uses at most $3K$ low-digit tests/writes, four high-digit tests and both rewinds. The total is at most $8(K+6)$. Seven trial subtractions and all possible undo passes therefore cost at most $112(K+6)$.
* The parity test, optional modulus addition, selection of the emitting position, $K$ data digits with ruler rewind, and the $T$ rewind/erasure together use at most $16(K+6)$.

Thus $160(K+6)$ per output plus $24(K+6)$ per tuple suffice. Since $K+6\le4K$, the whole pass, including its raw port, is bounded by $2^{14}V$ transitions. There are at most 19 tapes. Each reaches no more than the raw origin's left marker and $V+2$ cells to its right. The visited union is at most $128V$. Converting a marked caller data bank to this port and back adds two forward/return scans of its actual extent. The adjacent boundary markers on the two descriptors have the same linear bill. Calculating a selected pair's suffix count from a bit offset takes a fixed number of scans of a $k+1$-bit descriptor, or fits the more generous $(k+4)^2$ setup per stage. A normalized direct transform on an even contiguous $a$-bit slice uses $a/2$ adjacent pairs, each accepting every outside prefix/suffix value. The $0$-bit case is the identity.

The executable checks compare every output word with an independent integer matrix product, test unchanged descriptors, head homes and erased work. At $M=3$ they exhaust all 81 four-point input vectors. Another 72 cases use six odd moduli, padded and exact widths, and simultaneous varying prefix/suffix ranges. These 153 runs execute 498,564 transitions. A second replay composes 39 real tape passes on 25 arbitrary selected-bit subsets into one or two groups. It uses the specified position permutation, shift, and centered lift as integer reference operations, then compares the completed unnormalized transform in original address order against a full independently enumerated matrix. The group passes execute 2,091,846 additional transitions. Run $\texttt{python3 -I -B node-walsh-base.py}$ in this directory.

## Finite descriptions and role schedule

Write $M_r=W_a$ for the complete row divisor at the currently reviewed arity, reserving $M$ for the numerical modulus. One such row is determined by the finite-copy, label, and seed indices. Check and duplicate-return arms have at most $2M_r$ possible row roles. Let $n_r=2M_r+1$, $t=A+1$. The following enumeration is independent of the numerical original address and of the number of outside rows.

| Stage inspected | Ordinary combinations sufficient at one stage or rectangle/query | Charged transform rows |
|---|---|---|
| Input preparation, pointwise Newton update, fixed checks/lifts, and output sums | Source/destination roles, one optional temporary arm, and a choice of coefficient or sign. A dense check matrix has at most $n_r^2$ entries. | None |
| Charged rectangle at one query | Collect one source/common pair at a time, then distribute through the row matrix. Even retaining the contributing label, common seed, targeted seed and destination label separately gives at most $n_r^4$ choices. | One common role transforms on its prescribed $2D_F\le A$ axes after summation. |
| Free rectangle | Prepare one source role, keep each transformed role through all queries, apply common-representative and row operations for each source/destination pair, and finish one accumulated destination role. Two further choices for the retained and accumulating roles fit $n_r^6$. | Prepare once per source incidence and finish once per destination incidence. Neither loop is inside the query loop. |
| Spectral repair and direct terminal | Select one input/output check entry, actual $m$-bit frequency word and optional copy arm. The key is read with the numerical record. A terminal transform executes its axes in order. | Each finite conversion carries exactly an eighth of the input. Direct terminal axes operate on its current rows. |

For each of the two predictor evaluations there are at most $m$ Newton stages. The two conversion calls and fixed output operations give at most $4m$ stages; the finite binary tree has at most $4m$ nodes. There are at most $2m^6$ nonempty rectangles including the charged ones. The query list has $m$ entries. Four axis/matrix indices suffice for the active linear map or one of its axis calls. Within a tuple a source or destination execution uses at most a gather, at most a pre-map and sign, an accumulation or one actual child, at most a post-map and sign, and a clear/return. Even distributing copies, zeros and both input arms across the fixed four broad cases above stays below $2^{10}$ operations per tuple. A monomial map is charged separately for its elementary transvections. This reconstructs the bound

$$
 E\le 2^{10}(4m)^2(2m^6+1)(m+1)n_r^6 t^4 \le m^{48},
 \qquad W_a\le16m^4,\quad A\le4m ,
$$

at every adaptive node. The high exponent bounds actual ordinary work. The sharper source multiplicity remains necessary for every recursive call.

The original common-kernel phases are bilinear in paired coordinates in each column. A change of linear coset representative adds its pairing with the partial frequency. Under composition of linear maps these signs are still polynomials in the original column bits of degree at most two over $\mathbb F_2$. They can be reconstructed on zero, coordinate units and pairs of coordinate units. The matrices and phases thereby compiled have $A^2+A+1$ binary entries apiece. Their correctness uses the paired dual in the full nondegenerate space, so a degenerate restricted form on the free span causes no additional assumption. The source's normalized child transformations furnish the common kernel's entire $2^{-D_F f}$, and the two normalized conversion factors cancel across their spectral correction. The ordinary phases, half-address exchange and row maps account for the remaining monomial equivalence. [Fourier kernel](https://github.com/openai/math/blob/3344da59991ed94f9ba711217b29c1d760badfa6/preprints/The-logarithmic-exponent-of-finite-Fourier-transforms-November-24-2026/build/kernel.tex), [binary normalization](https://github.com/openai/math/blob/3344da59991ed94f9ba711217b29c1d760badfa6/preprints/The-logarithmic-exponent-of-finite-Fourier-transforms-November-24-2026/build/binary.tex)

The $m^{55}$-bit description has room for the original symmetric form and directions ($\le m^2+m^4$ bits), all rectangle/label bases and duals (even $\le 32m^6 m^3 (4m)^2$ bits), and $m^{48}$ events of $m^6$ bits each. Enumerating all bits of a joint candidate has at most $2^{m^{55}+1}$ iterations. Testing a span of at most $m^3$ generators uses at most $2^{m^3}$ binary masks. Sixteen such checks, nested even when they could be sequential, still fit the stated $2^{m^{128}}$ one-time bound including all file scans and products. This is an additive construction cost. The execution uses the compact accepted data, with at most a polynomial in $m$ per numerical record. Its frequency corrections generate the actual defective seeds and a requested inverse-Vandermonde entry; there is no per-record search across candidate geometries.

## A sufficient global guard and a local volume floor

Let $k$ be the logarithm of the outer record count, and $X=\lceil\log_2(k+2)\rceil$. The local growing parameters use $x=\lceil\log_2(a+2)\rceil$, $y=\lceil(x^2\lceil\log_2(x+2)\rceil)^{1/3}\rceil$, $m=2^y-1$. The preceding $2^{m^{128}}$ offline bill cannot be charged from the local condition $x\ge2^{24}$ alone. The following common guard suffices, independently of the integer caller's own CRT cutoff:

$$
                        X\ge 2^{66}.
$$

Indeed $\lceil\log_2(X+2)\rceil\le 2\log_2X\le X/2^{57}$. At the left endpoint $132<512$, and $(\log X)/X$ is decreasing. By monotonicity,

$$
 y\le X/2^{19}+1,\qquad
 128y\le X/4096+128 \le (X-2)/2048.
$$

Since $k\ge2^{X-2}$, this proves $m^{128}\le k^{1/2048}\le k/32$. Also $2000X\le k/32$, so $k^{1200}\le2^{k/32}$. Even allowing $m^{60}\le k^{60}$ duplicate setup/route calls,

$$
 m^{60}\bigl(2^{m^{128}}+k^{1110}+2^{16}(m+1)(k+4)^3\bigr)\le 2^{k/4}.
$$

For instance each prefactor $k^{60}$ and each polynomial term in the parentheses fit $k^{1200}$; summing the three resulting bounds uses less than two additional logarithmic bits. The same estimate pays computation of all arity divisors once per active chain. The actual spectral entry is computed from its $m$ key bits in polynomial time per word, independently of the offline enumeration.

Split the chosen positions into two groups of size at most $\lceil k/2\rceil$. A root group of size $s$ has $2^{k-s}$ unused leading spectators. At one adaptive node $W_a=2^y q^{L_F}8^h$ is a power of two and

$$
 \log_2W_a=y+L_FQ+3h\le4y,\qquad A\ge2^y,\qquad Af\le a .
$$

Telescoping over a positive chain gives $\prod W_{a_i}\le a_0^4\le k^4$. The path may include a finite repair stage which already fixes part of the current batch. Including the whole current $W_a$ in the product pays that restriction and every seed, rank, label and finite-copy role at that stage. For each fixed role its stream therefore still contains at least

$$
             2^{\lfloor k/2\rfloor}/k^4 \ge 2^{k/3}
$$

independent records. Every one of these prefix rows contains the full suffix and each required $f$-bit slot. Preserve older address fields in place and split the new finite rows from the remaining leading reserve. Ordered gather/scatter of a fixed finite role through every prefix retains the bound. No spatial call is made on a frequency-selected subset. The common bound $2^{k/4}$ on setup is smaller than a single role's volume. Every packed-XOR has an actual distinct third complete slot because $A\ge 2m$ and a monomial update uses two slots. Its uniform logarithmic and additive terms can use global $b=\lceil\log_2(2k)\rceil$ and $k$, while the variable interchange factor uses the genuine slot width $f\le a$.

## Complete induction and visited cells

Under the numerical imports in the [Walsh node](walsh-node.md), let $J(a)=A_I\sqrt{1+a}\,2^{B_I\Phi(\log_2(a+2))}$, with $A_I\ge1,B_I\ge0$. Ordinary operations admit $m^{61}V$ per event. This includes a scan through the accepted finite map, all scalar arithmetic on the actual key and both complete containing banks at every role transfer. An address transvection has a further $2^{34}bV(1+J(f))+k^{1105}$ bill. At most $4A^2\le64m^2$ such transvections expand a monomial event. Summing all $E$ events, the additive setups just bounded, and at most $4m$ direct pairs in the even remainder $a-Af<2A$, gives

$$
                   (m+1)^{128} bV(1+J(a)).
$$

Here the three nonconstant terms fit respectively $m^{109}V,\ 2^{40}m^{50}bV(1+J(a)),\ 2^{17}mV$, with $2^{k/4}\le V$ for the additive part. An elementary swap or sign is ordinary work. Every axis transform is accounted by the child invoice exactly once.

The sum of all child volumes is bounded as in the original finite repair, $\sum V_i/V\le 2dR\sum_{j<h}4^{-j}+A4^{-h}$, and every child has the same even width $f$. With $d\le7\sqrt m$, $2m\le A\le4m$ and $Af\le a$, multiplying by $\sqrt{f/a}$ gives at most $16R$. The evaluated binary label bound gives $16R\le 2^{10\sqrt{y\log_2(y+2)}}$. Writing $x'=\lceil\log_2(f+2)\rceil$, $x'\le x-y+1\le x-y/2$. On $[x-y/2,x]$, $\Phi'(u)\ge(2/3)x^{-1/3}(\log_2(x+2)/2)^{1/3}$. As $y\ge x^{2/3}\log_2(x+2)^{1/3}$ and $\log_2(y+2)\le\log_2(x+2)$, this gives $\Phi(x)-\Phi(x')\ge\tfrac14\sqrt{y\log_2(y+2)}$. Hence the children use at most one quarter of $bA_WV\sqrt a\,2^{B_W\Phi(x)}$ whenever $B_W\ge48$.

For $x\ge2^{24}$, $y\le2\Phi(x)$ by $\lceil\log_2(x+2)\rceil\le\log_2(x+2)+1$ and the unit ceiling in $y$. The ordinary bill is bounded by

$$
        2(1+A_I)bV\sqrt a\,2^{(B_I+256)\Phi(x)} .
$$

With $B_W=\max(48,B_I+256)$ and $A_W=2^{2^{24}+28}(1+A_I)$, this uses less than a quarter of the proposed node bound. In the fixed direct branch $a<2^{2^{24}}$, the at most $a/2$ pair passes, marked adapters and one $(k+4)^2$ shape allowance per pass fit $2^{2^{24}+20}V$ including entry and return. There is no circular numerical call in the direct program. The same inequality covers every bounded-width descendant at the unchanged global $k$.

For space, retain at most 64 complete current banks at one finite level, which covers the immutable input/output, Newton, check/lift, stored free source, destination and transient exchange roles. A finite child contracts by $1/8$. Live finite payload at one spatial level is bounded by $(8/7)64V<74V$. A spatial child fixes one full finite role, or is issued within an already $1/8$-contracted terminal. Its volume is at most half its parent's. The entire collection of active and parked payload frames is therefore at most $148V_{\rm root}$, plus marks and a fixed number of transient copy banks. Stack each bank on a tape at its current stack top as in the [handoff implementation](recount-handoff.md). A return clears exactly the corresponding parity-marked frame, so future smaller calls reuse cells at the same offsets. This proves the bound for the union of visited cells through halt. One can also overcount all parked descriptors by $k+1$ frames, since $\sum_i (h_i+1)\le2\log_2(k)+1$ follows from $\sum_i\log_2 A_i\le\log_2 k$. Each finite descriptor, candidate counter and scratch arena is under $2^{k/4}$ cells. Thus all such descriptors together are bounded by $2^{k/3}$. The guarded routing supplier is invoked sequentially on at most the current payload volume, with linear visited coefficient $S_I+2^{16}$ and additive $k^{400}$. The direct program, word product and aligned scalar have fixed visited coefficients and reusable origins. Root position permutations may include both components; at most $200k$ bits per input record suffice. This yields $O(Nk)$ visited cells in the full selected layer, including the input, output and two groups' workspace. Keeping $2^{32}(1+S_I)Nk$ as a coarse common ceiling for these particular suppliers covers even simultaneous root-sized copies and their stacks.

## Sharper version of the Walsh node and boundary rounding

The revised [Walsh node](walsh-node.md) separates the pure scalar cost from the cost multiplied by $J(a)$. I also obtain its smaller guard $X\ge2^{48}$ and coefficients $B_W=\max(102,B_I+41)$ and $A_W=2^{2^{24}+28}(1+A_I)$. For $m\ge2$ the coefficient of $m^{37}$ in the finite-event majorant is at most $2^{14}\cdot3\cdot(3/2)\cdot33^6\cdot(9/2)^4<2^{60}$, by $n_r\le 33m^4,t\le(9/2)m$. Therefore its two main ordinary bills are at most $2^{60}m^{98}V$ and $2^{100}m^{39}bV(1+J(a))$, in addition to the direct remainder and absorbed setup. Since $\lceil\log_2(x+2)\rceil\le(25/24)\log_2(x+2)<(65/64)^3\log_2(x+2)$ and $\Phi(x)\ge64$, the outer cubic rounding gives $y\le(33/32)\Phi(x)$. The two exponents satisfy $98(33/32)<102$ and $39(33/32)<41$, which proves the stated improvement without weakening the quarter child budget. At $X\ge2^{48}$, set $r=\lfloor\log_2X\rfloor$. The ceiling $v_X\le r+2\le2^{r-39}$ gives $128y\le X/32$ after its unit cubic rounding. Consequently $m^{128}\le k^{1/16}\le k/32$. All earlier exponential-volume absorptions continue to hold.

For an input group of $s_i$ selected bits, copy the signed mantissa to its residue port with $\lfloor s_i/2\rfloor$ low zero digits. This single shift replaces all per-axis doublings. Negative values take their canonical complement modulo the group's modulus. Multiplying by the normalized even factors and the one unmatched unnormalized bit leaves the exact unnormalized group sum modulo $M$. Its absolute magnitude is bounded by $2^{w_i+s_i}$ before and after all results are lifted. Since $M>2^{k+w_i+s_i+2}$, centering each output recovers its integer representative. After the first group the mantissa width for the next can be fixed at $w+s_1$. The sum of the group sizes, including the case of two odd groups, gives the exponent for the single final normalization.

Let $Z$ be the final integer, $t=|Z|$, $s=s_1+s_2$, and $p=w+s+3$. For odd $s$, computing $A_0=\lfloor\sqrt{2^{2p-s}}\rfloor$ once yields

$$
 0\le t2^{-s/2}-t A_0/2^p <t 2^{-p}\le\tfrac18 \quad(t>0).
$$

The candidate $j=\lfloor t A_0/2^p+1/2\rfloor$ is the exact nearest integer or its predecessor. It must be increased exactly when $4t^2>2^s(2j+1)^2$. Equality is impossible for odd $s$, by the binary valuation of a nonzero square. For even $s$, shift by $s/2$ bits and resolve a midpoint by rounding away from zero. The zero numerator returns zero directly. Thus the odd case needs one multiplication and two squarings per real word, plus shifts and a comparison. The magnitudes fit $256k$-bit ports and each product costs at most $2^{41}k^{3/2}$ by the numerical [Toom supplier](word-toom.md). Exact integer bisection is performed once for $A_0$. The complex output has Euclidean error bounded by $2^{-72k}\sqrt{2N}/2<2^{-50k}$.

There are at most four numerical group/component executions of volume $100Nk$ and eight complete root position permutations. Each restores the incoming position order before the next group. The $400A_W bNk\sqrt{k}\,2^{B_W\Phi(X)}$ core subtotal plus position permutations, signed shifts/lifts, exact word rounding and one-time preparations is below $2^{18}A_W bNk\sqrt{k}\,2^{B_W\Phi(X)}$, including the empty selection and exactly one chosen bit. This is the written whole-layer result conditional on the stated interchange, guarded permutations, and finite algebraic identities. The implemented direct branches have the narrower test coverage above.

## Actual volumes of column maps

The source Newton pencils have diagonal row weights on the seed index, since each seed uses its own signed sum of the $Q_j$. Dense checks, lifts and the frequency correction can mix these rows pointwise without a column address map. Consider an actual finite node with $P=q^{L_F}$ labels, $S$ current seeds and $D$ independent finite copies, and volume $V_r$. One complete extracted label/seed/copy role has volume $V_r/(PSD)$. For one query, each ordered pair of labels belongs to at most one free rectangle and at most $2^{L_F}$ charged rectangles. Between $2D_F\le A$ source/kernel/destination axis boundaries the monomial coordinate/phase operations compose; $16(A+1)$ maps per chosen pair, query, seed and copy overcounts even if all boundary maps are replayed. Shared preparations need only be charged once in the actual child ledger. Multiplying this per-role volume by all those indices, including an explicit overcount of every incidence by ordered pairs, gives

$$
 16(A+1)(1+2^{L_F})mP\,V_r\le160m^6V_r
$$

per pencil. Here $L_F\le y-1,\ P\le m^3,\ A+1\le5m$. Each elementary address list expands into at most $64m^2$ transvections. The two predictor evaluations use at most $14\sqrt m$ pencils, and summed current volume of all finite nodes, including their terminal levels, is at most $4V/3$. The other boundary half exchanges and phases need at most $8(A+1)$ maps per role over these same finite levels, with no extra seed-to-seed address change. The part charged to packed XORs is consequently bounded by $2^{54}m^{17/2}bV(1+J(f))$. Whole-parent scans extracting and scattering each such role remain in the ordinary $E$-event bill. Every additive $k^{1105}$ is paid by its unweighted event count and the common volume floor.

Dividing by the parent $\sqrt a$, $\sqrt{f/a}\le(2m)^{-1/2}$ reduces the exponent $17/2$ to 8; $8y\le(33/4)\Phi(x)$ makes an increment of 9 on $B_I$ sufficient. I obtain a separate ordinary-work floor of 62 even without a more efficient record bill. On $x\ge2^{24}$, $\log_2(x+2)\le x/2^{19}$ by monotonicity, so $x/\Phi(x)>80$. Also $\log_2a\ge x-2$, hence $\sqrt a\ge2^{40\Phi(x)-1}$. Dividing $m^{98}$ by this factor reduces its exponent below 62 because $98(33/32)-40<62$. The sharper direct per-record bound in [the Walsh node](walsh-node.md) uses $m^{55}\le K$ and charges at most the $A^4$ monotone mask scans, the separate polynomial-in-$m$ scalar, and the fixed set of containing-bank transfers. It yields the still smaller floor 48. In particular $B_W=B_I+9$ suffices for the [native fixed root degrees](node-root-parameter.md) $R=240,256,512,4096$, with values $70,71,87,165$, respectively.

The [fixed global guard proof](address-native-staircase.md) prices the finite constructor from $X=2^{24}$ and covers the direct branch below it.
