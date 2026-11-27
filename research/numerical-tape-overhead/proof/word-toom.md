# A counted short-product machine for the outer integer caller

For each $w\ge1$, the [six-tape program](../checks/word-toom.py) multiplies two arbitrary independent unsigned $w$-bit words, including padded words. It writes precisely $2w$ little-endian bits, empties both argument banks and all working banks, and returns every head to its origin. On marked banks its time and total distinct tape/address cells satisfy

$$
 T_{\rm word}(w)\le2^{28}(w+1)^{3/2},\qquad S_{\rm word}(w)\le256(w+1).
$$

This instantiates the full-width products in [the integer caller](../CONSTRUCTION.md#time-on-the-three-branches), including streamed prefix phases, complex pointwise products, final scaling and odd-width Walsh rounding. Retaining both inputs by copying, normalizing two signs, and returning the result to a larger stream cost at most $128(w+1)$ additional transitions by sequential sweeps. Recursive Walsh nodes use a separate short-coefficient routine.

## Rule and identity

Tape F holds an end-access stack of frames. Its alphabet includes the product of 22 binary tracks, boundary symbols, and a left tag with a stage in $[0,4]$ and a sign. The other five tapes hold two inputs, the product, a unary ruler and one temporary word. Each tape has a home delimiter at position $-1$. A read, write or unit move can be compiled as a single transition. The program's control uses only local symbols and fixed finite flags. Recursion reads the continuation from tape F. Absolute positions and counters occur only in the simulator and fixtures. Installing the six initial home delimiters, if needed, costs three extra steps using simultaneous moves.

For $w\le8$, the direct rule accumulates at most eight bits per input, performs eight shift/add steps on sixteen-bit control words and writes the product. Allow 2,048 steps even if these bounded additions are bit-serial. Otherwise use Toom-3 at $0,1,-1,2,\infty$ as in the [earlier arithmetic audit](foundations/review-axes-and-arithmetic.md). Each limb has $m=\lceil w/3\rceil$ bits. Each evaluation has magnitude below $7\cdot2^m<2^{m+3}$. Issue five width-$m+3$ calls with the actual signs recorded in the parent. Denote the signed replies by $v_0,v_1,v_-,v_2,v_\infty$. For true product coefficients $c_i$, $c_0=v_0$, $c_4=v_\infty$, and

$$
 c_2=(v_1+v_-)/2-c_0-c_4,\quad t=(v_1-v_-)/2,\quad
 u=(v_2-c_0-4c_2-16c_4)/2,\quad c_3=(u-t)/3,\quad c_1=t-c_3 .
$$

Indeed $t=c_1+c_3$ and $u=c_1+4c_3$. All four divisions have nonnegative, exact-multiple inputs. A signed linear combination takes a low-to-high carry sweep. Division takes a high-to-low sweep. Evaluation/interpolation intermediates fit $2w+12$ magnitude bits, by the limb and evaluation bounds and the displayed fixed coefficients. Four Horner recombinations at radix $2^m$ have nonnegative partials at most the final $2w$-bit product. Thus $W=8w+64$ frame columns suffice for signed arithmetic.

## Transition and space ledger

The frame has $W$ data columns between two markers. A walk to a marker and back costs at most $4(W+2)$ separate reads/moves. A signed row update uses one read, write and forward move per column, then two actions per column to return. The fixed linear combinations have at most four terms and bounded signed carry. Scanned symbols and carry index a fixed finite transition table. A division has the same bound with the two sweeps reversed. For a shifted addition, first copy the old result track to temporary and rewind both heads. During the second pass keep the temporary stationary on the first $m$ columns, then advance it alongside the frame. Restore heads and erase the whole temporary. These walks take at most $32(W+4)$ actions. Use this same allowance for one complete handoff scan, linear update, sign query, division, shifted addition or extent-marking operation. Marker tests are charged.

| Step at a non-base node | Upper count in units of $32(W+4)$ |
|---|---:|
| Inspect up to nine input digits, initialize $8w+64$ columns by eight complete input scans, build the unary ruler in one pass, mark limb/child/output lengths, split three limbs, and erase argument and ruler tapes | 16 |
| Issue one child, including two linear combinations, two sign scans, up to two negations, copying its $m+3$ digits and advancing to the parent's right boundary | 10 |
| Recover one continuation, deposit the reply, clear its tape and negate its signed track when necessary | 4 |
| Interpolate, perform four shifted additions, write $2w$ output digits, clear the whole frame to its left tag and dispatch the return | 24 |

The interface's two input tapes are home and empty before each new issue. Fresh frames start immediately to the right of the parent. Returning to its left end never crosses any earlier ancestor frame. The bookkeeping at a base return can be charged to its immediate caller once; the top return costs at most three steps. The displayed unit costs give a conservative nonrecursive ceiling of $512\cdot32(W+4)\le2^{20}(w+1)$ for $w\ge9$. This also covers bounded-control initialization and all frame-marker transfers.

Let $p(w)=\max(1,w-6)$. At $w\ge9$, $p(\lceil w/3\rceil+3)\le p(w)/3$ and $w+1\le4p(w)$. Also $5/\sqrt{27}<31/32$ by squaring. The five children together use at most $31/32$ of $2^{28}p(w)^{3/2}$ by induction. The remaining $1/32$ dominates $2^{20}(w+1)$; the base is below 2,048. This proves the time bound at every positive width, independently of the data.

At $w\ge9$ the child width is at most $3w/4$ and each live frame spans at most $16w$ cells. Parent frames on any path therefore occupy at most $64w$ cells on F. The two argument words, output, ruler and temporary each fit the maximum of the bounds at the root. Each tape reuses positions after a pop or clear; summing visited intervals with their boundary cells gives the stated $256(w+1)$.

The executable checks all 340 pairs through width four plus padded, negative-evaluation, all-ones and randomly chosen words at 15 more widths through 81. The largest replay used 1,862,202 individual tape actions. Oracle multiplication, dictionaries and absolute head coordinates occur outside the program's movement rule. The algorithmic identity is classical Toom-3. The new result is its executable transition and distinct-cell certificate at this caller.
