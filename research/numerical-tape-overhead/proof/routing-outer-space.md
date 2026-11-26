# An absolute visited-cell bound for the complete fast integer program

Fix one original input of two $n$-bit words, set $B=Nk$ for the actual $N=2^k$ padded digit array, and assume all numerical suppliers' fast guards. For the complete signed complex integer caller,

$$
\#\{(\mathrm{tape},\mathrm{position})\text{ visited through halt}\}
\le 2^{29} B < 2^{32} n. \tag{1}
$$

The 64 Walsh banks, the ordinary Fourier arrays, both routing call sites, the phase and coefficient constructors and their input/output tapes are included. The proof also counts the zero positions of unused heads. Source banks and stacks return to marked origins between uses. For a head starting at zero, a single-run interval of length $a$ lies in $[-a,a]$. Thus its union over arbitrarily many invocations with per-head length at most $a$ has size at most $2a+1$. We apply this to individual heads or to explicit common-origin stacks. An aggregate space bound at one invocation alone need not control the union.

## One reusable guarded-routing family

Let $D$ be an upper bound on the incoming bit volumes of every call to one routing family during this input. All complete field interchanges within those calls see binary bit volume at most $D$. The true native ternary volume is at most $W_*=9D$, by the [range wrapper](address-range.md).

The [native arena](node-integrated.md#arena-stack-and-visited-cells) has at most 1024 ordinary and control private heads. Each has one interval of length at most $8W+4$ through a nonbase request with root volume $W$. Across requests of different spectator shapes they contribute at most $1024(16W_*+9)\le25600W_*$. Two end-access stacks together have one-request high-water bound $(3\cdot2^{12}+2)W$. Even treating the stacks independently and both sides as reachable costs at most $2(2(3\cdot2^{12}+2)W_*+1)\le49162 W_*$. The [direct-only base](node-streams.md) uses 17 heads and at most $51W$ cells, which adds at most $17(102W_*+1)\le1751W_*$ under the same argument. Include at most 128 additional input, descriptor or marker-port heads even if separately instantiated. Original/marked buffers have length at most $W_*+2$ and each original dimension has at most $W_*$ digits, so this last group fits $128(2W_*+5)\le896W_*$. These bounds sum to less than $2^{18}W_*$. They remain valid when different calls attain different maxima on the native tapes. The width cutoff compares an incoming descriptor on a finite-state chain and initializes no giant numerical word.

Two disjoint 15-head range directions suffice. Each of their raw, unary and parameter heads has single-call interval length at most $9D+2$: the largest whole array is $W$, the two genuine extents are at most $D$, and the padded extent is less than three times the genuine one. Its two-sided union across times is at most $18D+5$ per head. Another 32 heads cover raw/marked transfers, input dimension copies, output normalization and home cells. All have this same envelope. Hence the two range ports and boundary logic jointly fit $62(18D+5)<2^{12}D$, separately from the native area.

The noninterchange portion of the [guarded permutation executor](routing-outer-permutations.md) needs fewer than 32 bulk banks at each of five fixed nested wrapper levels. On the whole input keep these banks, tags, rulers, exceptional-sort buckets and intermediate fields home-based, using the first at most $4D+2$ positions per bank. A tag has at most one original record's length and each stored partition of records plus tags occupies at most $2D$. Even the two-sided union $160(8D+5)$ is below $2^{16}D$. The single control catalogue, bounded scratch registers, graph and word indices have fixed origins. Their absolute extent through all calls is at most $k^{400}$ by the explicit $k^{304}$-word field allocation and $8k+8$-bit words. The frozen address/shape port uses two-sided intervals of at most the $2k+1$-bit full bit-volume descriptors even for a thin role.

Therefore the whole family's cumulative union over every call is less than

$$
 (9\cdot 2^{18}+2^{12}+2^{16}) D+k^{400}
 <5\cdot2^{19}D+k^{400}. \tag{2}
$$

Use two disjoint physical routing families for this count. The three CRTs and outer block permutation layers all use the first, on $D\le1024 B$. Both initial/final Walsh position permutations and every packed slot operation in its recursion use the second, on $D\le100B$. Values can be independently occupied and different at every invocation. No loop ranges increase the number of physical heads.

An independent review retains the unrounded per-head factors and improves (2). Each native end-access stack grows right from a fixed bottom and returns by popping its last appended frame. Its union over time is therefore one initial interval, even when its own maximum occurs in a different call from every other head's. Bound each of the two maxima separately by the full pair's one-request bound. With $W_*=9D$ and $D\ge1$ the uniform native count per $D$ is at most

$$
1024(144+9)+2[(3\cdot2^{12}+2)9+2]+17(918+1)+128(18+5)=396463 .
$$

Here the ordinary, direct and auxiliary native heads still have their conservative two-sided envelopes. The two range ports add $62(18+5)=1426$ per $D$. The fixed guarded banks add $160(8+5)=2080$. Thus (2) can use the smaller numerical term $399969D+k^{400}$ at every call site. No correlation between tape maxima is needed.

## Walsh, outer arithmetic and stationary heads

Let $V_0=100B$ be one real modular Walsh array. The [physical role review](routing-review-walsh.md) and its [source ledger](walsh-node.md) give 64 marked ordinary banks per live finite generation. At spatial depth $i$ its incoming volume is $V_i\le2^{-i}V_0$, and a finite depth $r$ has incoming volume $U_{ir}=8^{-r}V_i$. They use the same bank set, paying for suspended words on one payload stack. An active bank's home interval is no longer than $V_0+2$. The 64 active-bank unions therefore contain at most $64(2V_0+5)$. On the stack one frame takes at most $64(U_{ir}+1)\le128U_{ir}$ positions because every issued level has positive volume. Since $\sum_{i,r}U_{ir}<16V_0/7$, the payload stack remains below $293V_0+2$ including its top cell. Its heads push/pop from the current end, so siblings and later real components revisit the same prefix. Even allowing another copy of the entire stack, separate neutral and base work, plus 128 whole-volume private port banks under the two-sided union rule, the ordinary recursive payload fits $2^{12}V_0$. Core inputs, signed component copies, intergroup lifts, normalization words and their outer-port copies add less than $2^{16}B$: 32 full record banks at $1024B$ each already cover these sweeps. All four group/component calls can use the same physical banks.

There are at most $k+1$ finite and spatial descriptors on the current path. Each description occupies at most $2^{k/4}$ bits, and its independent [finite constructor](walsh-node.md) runs within $2^{k/4}$ transitions. Old descriptors are serialized on one end stack, so $(k+1)2^{k/4}<2^{k/3}$ covers all parked descriptions for the entire traversal. For active enumeration even 512 fixed heads all making a unit move on every constructor step use at most $512(2\cdot 2^{k/4}+1)<2^{k/3}$ positions in total across all invocations. The adaptive spectral scalar file has $(64(m+1)+128)H$ short digits with $H=8(m+1)^2(y+2)$. For $m\ge2$, $y=\log_2(m+1)\le m$ gives $y+2\le2m$. The file is below $2^{14}m^4\le m^{18}\le m^{55}\le k/32$ under the [adaptive range](address-native-staircase.md) with $m^{56}\le k/32$. Below the chosen global adaptive cutoff the integral direct branch creates no spectral directory. The complete mask catalogue for one form has at most $8(A+1)^2(k+2)$ bits. Staging a different form starts at its original mark. These active words, the common modulus, bisection tables and the eleven scalar tapes fit another $2^{k/3}$ positions including multiple simultaneous arrays. At the admitted guards $3\cdot2^{k/3}<B$.

The [ordinary Fourier and input/output ledger](outer-layers.md) supplies through-halt space $2^{16} B+k^{250}$ for compact coefficient tables, alternating full prefix powers, input, pointwise product, reverse scans, output and setup. The wide finite setup has two permanently allocated $k^{200}$-word arenas with $k^8$ bits per word; the numerical streaming uses compact words and a fixed number of whole-array banks. These intervals are reused across all three schedules. One can add separately the six [short-word multiplier](word-toom.md) tapes at every final or phase call, uniformly over operand widths up to $4096k$. The one-call sum $256(w+1)$ gives per-tape union at most $2\cdot256(4096k+1)+1$; even summing that on all six costs less than $2^{24}k\le B$ on this range.

Explicitly include zero even on every dormant physical tape. Each designated routing family may use 1024 native private heads, two native stacks, 17 direct partners, up to 128 native ABI heads, 62 raw range and marker heads, 160 guarded bulk heads and up to 256 guarded controller heads. The last number allows one access arena, a switch graph, the binary index, masks, general arithmetic using separate marked registers, and their static nested return modes. Their sum is 1649, below 2048. Set registers and arrays of unbounded *number of entries* on delimited tapes as in the supplier, with no head per entry. Allocate under 512 more nonrouting Walsh heads (64 payload, two stacks, 128 optional port banks, 32 whole arrays, eleven scalar, six word, 64 finite witness/index registers, and 128 remaining masks/selectors, descriptors and finite control). Similarly under 512 outer ordinary heads cover two setup catalogues, fixed word and phase registers, raw input/output, prefix streams, and digit/carry work. With both routing families this leaves fewer than $2^{13}$ fast-program heads. A separately compiled bounded-size schoolbook fallback can keep up to 512 further heads at zero on the fast branch within $2^{14}$ initial positions. The number of control states, including fixed cutoff comparisons, does not change the number of heads. Counting these homes again is harmless.

For the sum outside (2), $2k^{400}+k^{250}\le3\cdot2^k$ because $400\log_2k\le k$. Combine the two $2^{16}B$ outer/copy terms, the $2^{12}\cdot100B$ Walsh bank term, metadata, the six word tapes, the initial homes, and even four further full raw input/output copies using $n\le B$. These are below $2^{22}B$. Hence

$$
S(n)\le [399969(1024+100)+2^{22}]B
=453{,}759{,}460\,B<2^{29}B .
$$

For the actual fast lengths let $d=\lceil\log_2 n\rceil\ge16$. Then $4h\le4(n/d+1)\le n/2\le2^{d-1}$, so $k\le d-1$. Since $n\ge d(d-1)$, the [literal packing](../CONSTRUCTION.md) gives $Nk<8(n/d+1)(d-1)\le8n$. This proves (1). On the short-input branch the fast heads may remain at zero, adding at most $2^{13}$ home cells to the [schoolbook fallback](schoolbook.md) and dispatcher's own interval union. Their respective maxima $8n+9$ and $32(n+50)$ keep the same $2^{32}n$ bound for all positive lengths. [Exact arithmetic replay](../checks/routing-outer-space.py). Prepared for Jerry Chen (@CubeJerry) with ChatGPT research assistance.
