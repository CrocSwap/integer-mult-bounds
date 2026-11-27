# A numerical fixed-tape executor for dyadic address changes

Let $P,G,S$ be positive, $f,j$ be nonnegative, $M=3^f$, and $a$ be a signed integer. On an arbitrary bit array in the order $[P][M][G][M][S]$, the executor moves the bit at $(p,x,g,y,s)$ to

$$
 (p,x,g,\,(y+a\,2^{-j}x)\bmod M,\,s).
$$

Its volume is $V=PGSM^2$. Let $\ell$ be the canonical binary length of $|a|$, with one digit for zero. Let $J$ be the canonical binary length of $j$. Put $k=2j+2\ell+\operatorname{popcount}(|a|)$.

The executor costs at most **$512(1+k)V+128(\ell+J+1)$ transitions** and visits at most **$24V+4(\ell+J+1)+96$ distinct tape/address pairs**. It also has three single-field entry points. They multiply $y$ by $2,2^{-1}$ or $-1$ on $[P][M][S]$, with $V=PMS$ and $k=1$. Unused descriptor words may be the one-digit word zero. For $M=1$ every address permutation is the identity.

All heads start and halt at their left delimiter. The input/output bit bank A and the six canonical MSB-first descriptor words have a left and right delimiter. The eleven scratch banks have an empty body after their left delimiter. The sign and chosen entry are in finite control. A holds the result, the descriptor words persist, and all eleven scratch bodies are empty on return. Every address may contain independent data, including the intervening and trailing fields.

The source paper represents a lower-target address change by a translation determined by an earlier field and describes increasing pieces for a scalar multiplier and its inverse. S003 B2 specializes its elementary diagonals to signed powers of two. Its shear coefficients are signed $1,2,1/2,2/d$, with dyadic $d$. The explicit executor covers these coefficients and all signed dyadic shears. An upper-target shear incurs a spatial interchange before and after the lower-target operation. [Source stream operations](https://github.com/openai/math/blob/3344da59991ed94f9ba711217b29c1d760badfa6/preprints/The-logarithmic-exponent-of-integer-multiplication-on-tapes-November-24-2026/build/interchange.tex) · [S003 dyadic factors](foundations/explicit-dyadic-geometry.md) · [S008 geometry instruction count](compiler-geometry.md)

## Four streaming operations

A block consists of all $S$ suffix bits in their original order. Write $M=2h+1$.

* For $D(y)=2y$, put the first $h+1$ input blocks on E and the other $h$ on O. Interleave E and O, beginning and ending with E. Even output addresses get the first group in sequence. Odd output addresses get the second group because $2(h+1+t)\equiv 2t+1\bmod M$. For $D^{-1}$, split even and odd input blocks, then concatenate the two runs. Both maps work for every $f$, including $h=0$.
* For $N(y)=-y$, transfer block zero directly and store the other $M-1$ blocks on E. Read E backwards one block at a time into O, then read O backwards into the output. Every bit within each suffix block regains its original order.
* For $H_+(x,y)=(x,y+x)$, split each current $y$-fibre after $M-x$ blocks. Delay the prefix on E, stream the tail directly to B, then append the prefix. The marked unary cut begins at the right boundary for $x=0$ and moves one cell left after each complete $x$. Every gap value $g$ uses that same cut. For $H_-$ use the cut at $x$, moving right. This gives $y-x$ in the same format. The cut tape has one marker on its $M+1$ possible positions.

Every operation writes to B. A scan moves the result back into the original marked A, erases B and restores the current heads.

For a numerator with magnitude digits $b_1,\ldots,b_\ell$ in decreasing order, first apply $D^jD^{-\ell}$ on the target. For each digit apply $D$, followed by $H_+$ or $H_-$ when the digit is one. After the $\ell$ digits the target is $2^j y+a x$. Applying $D^{-j}$ finishes the requested map. The program issues exactly $k$ stages, including canonical zero numerators. Its number of stages is linear in the stated exponent and numerator length.

## Transition count

The [executable program](https://github.com/CubeJerry/integer-mult-bounds/blob/a2a17b61d943676c757e0bbfaef3f4fae03ab8e5/research/moonshot-overhead-program/sessions/2026-11-26-S008/address-dyadic.py) names 18 tapes and uses the fixed alphabet `0 1 [ ] _ u c C z Z`. A call to `see` is one stationary transition branching on a scanned symbol. An `act` reads the old tuple and writes and moves at most once per head. The finite choices of routine, tape names, parity, direction, input sign, and remembered symbol can be inlined at their finitely many call sites. The loops inside the executor branch on scanned symbols. The driver and emulated tape implementation use array indices for observation and testing.

| Routine | Executed path | Transitions |
|---|---|---|
| `first` from cell $u$ | Test before each left step, test the left delimiter, step right | $2u+2$ |
| `unary` clock of length $r$ | $r$ tests and advances, one terminal test, return from cell $r+1$ to first | $4r+5$ plus its $r$ bodies |
| `block` | Same unary clock of length $S$. Each transfer also moves the clock head | $4S+5\le9S$ |
| `append_bank` | From the right end rewind, copy and erase $r$ bits, rewind | $6r+9$ |
| `erase_from_first` | Clear forward until blank, return over precisely the traversed cells | $4r+5$ |
| `counted` for $t$ in $b$ digits | Reverse-copy in $6b+8$ steps. A successful decrement at $v$ costs $4\nu_2(v)+7$. The final failed decrement crosses $b$ zeros and erases the counter in $4b+5$ | At most $11t+10b+13$, excluding its $t$ bodies |
| `triple` on $r$ unary cells | Consume $r$, emit $3r$ on tmp, return both heads. Consume tmp into M and return both again | $30r+18$ |

Here $\sum_{v=1}^t\nu_2(v)\le t$. Building a positive unary clock $n=P,G,S$ costs at most $24n+17$ including its counted loop, appends, and final return. The single-field entries skip G. Starting with one unit, the lengths before the $f$ triplings sum to $(M-1)/2$. Their transition total is at most $15M+18f$. Constructing the half clock takes at most $6M+9$. Including the 18 starting head moves, one-unit setup and counting descriptor $f$, the setup costs at most $24(P+G+S)+60M+98$ for a paired job. For a single-field job omit $G$. Since every included dimension is at most $V$, this is at most $230V$.

On one $MS$-bit fibre, a unit shear transfers $M$ blocks, tests and advances the $M$ cut positions, rewinds the cut and appends a prefix of at most $MS$ bits. This costs at most $15MS+4M+15\le34MS$. Constructing the cut costs $6M+10$ for each $p$. Moving its mark costs at most $4M+9$ for each $x$. Discarding it costs $4M+9$ at the end of the $p$ group. With the $x$- and $g$-loops, the per-$p$ work is at most

$$
 34GM^2S+4M^2+4MG+28M+24\le94GM^2S.
$$

For a doubling, the two rounds transfer $2M$ blocks, use three half-clock loops and four rewinds of the buffers. This costs at most $22MS+12h+31\le59MS$. The inverse uses at most $15MS+4h+23\le40MS$. Negation uses at most $27MS+2M+8h+12\le45MS$. These bounds include $M=1$.

The top $p$-loop adds at most $9P$ steps. For a paired scalar operation all three nested-loop overheads sum to at most $27V$. After any operation the canonical commit uses $10V+17$ transitions, since A and B have exactly $V$ bits. Thus every stage costs at most $160V$. Erasing the five unary banks and homing all 18 heads uses at most $20V+79$. The coefficient loop contributes at most $22j+9\ell+20J+36$ outside its $k$ stages. Combining these bounds, using $V\ge1$ and $2j\le k$ for the shear entry, gives the displayed $512(1+k)V+128(\ell+J+1)$.

## Ever-visited cells and integration

The data banks A, B, E, O each have largest extent at most $V+2$ cells. The four shape descriptors use at most $4V+8$. The two coefficient words use at most $\ell+J+4$. P, G, S, M, half, cut and tmp use at most $7V+15$ together, including the marked cut terminal. The binary counter uses at most $V+J+2$. Every tape starts at its left delimiter and reuses that same interval. Summing these maxima gives the stated $24V+4(\ell+J+1)+96$ bound on the union of visited cells across all $k$ stages. It also holds for a single-field call with unused words because their heads visit only their left delimiters and first cells. Occupied data on separate arena and stack tapes stay in place throughout.

The interface takes the prefix, intervening and suffix extents as binary words. The cost of delivering the field instruction and those shape words belongs to the enclosing compiler. The bound permits rebuilding the unary clocks for every elementary instruction. At $d\le m$ the B2 coefficients give $\ell\le2$ and $j\le\lceil\log_2 m\rceil+1$. For $m\ge2$, this yields a local bill of at most $2^{14}(1+\lceil\log_2 m\rceil)V$ per elementary affine instruction. A signed diagonal in the stated lists uses at most two of $D,D^{-1},N$. [Geometry emitter](compiler-geometry.md)

The separate replay compares the final physical bit bank to destination indices computed by exact modular arithmetic and checks every descriptor, scratch word and head on exit. Its finite scope supplements the proof for all widths. The whole-interchanger and whole-integer constants require the other operations in their respective callers.


The independent counter reconstructed the double, halve, negate and signed-cut loops directly from the program, including the empty half-clock at $f=0$ and restoration of multi-bit suffix order. The [recount](recount-handoff.md) uses explicit right delimiters for its initially empty parked banks. If those same eleven physical scratch banks are supplied here, remove each empty right delimiter before entry and reinsert it on exit. From its left delimiter, a bank needs one step right and one return-and-write per conversion. Even serializing the eleven banks adds at most 44 transitions. The seven occupied data and descriptor banks already match the interface.
