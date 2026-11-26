# Numerical binary-to-ternary interchange wrapper

For $u\ge0$ and $p,g,s\ge1$, put $n=2^u$, $e=\min\{i:3^i\ge n\}$, $t=3^e$, $r=t-n$, $V=pgsn^2$ and $W=pgst^2$. One [135-state, 15-tape program](https://github.com/CubeJerry/integer-mult-bounds/blob/a2a17b61d943676c757e0bbfaef3f4fae03ab8e5/research/moonshot-overhead-program/sessions/2026-11-26-S008/address-range.py) embeds $[p][n][g][n][s]$ in $[p][t][g][t][s]$ in **at most $152V$ transitions and $41V$ distinct tape cells**. A second program of the same size and cost restricts an arbitrary padded input to the two genuine ranges. Both bounds are sharp on their stated inclusive domain. They count setup, data movement, head returns and erasure of scratch. Both programs return $e$ in canonical binary.

Given a native ternary implementation with time $T_3(W,e)$ and ever-visited space $S_3(W,e)$, the full two-field binary interchange costs at most
\[
 T_3(W,e)+512V \quad\text{transitions},\qquad
 S_3(W,e)+128V \quad\text{distinct cells}.
\]
Here $e\le u$, $t<3n$ and $W<9V$, including $u=0$. These costs also allow explicit conversions to and from the marked native root, copying of its four descriptors and optional normalization into the original external data bank. This supplies the external range conversion at [AI §6](foundations/adaptive-interchange.md). All recursive native children keep the same radix.

## Fixed-tape operations and contract

External raw banks begin at their first symbol and end at the first blank. The cell immediately to the left is available for a temporary marker. Binary descriptors are canonical MSB first, with the string 0 for zero. The two programs read $u,g,s$, detect $p$ at the end of a complete prefix, preserve the raw input, and write the result and $e$ into separate initially empty banks. All heads return to their first position. In a complete binary call the original prefix descriptor $p$ is already available to the native call.

Materialize unary $u,g,s$. Starting with one mark, double $u$ times to make $n$. Compare a unary power of three, initially one, against $n$ until it reaches or exceeds $n$. On each failed comparison reset both heads, triple the power, and increment a separate low-digit-first binary counter. The final comparison leaves $t-n$ marks after the matched prefix of the ternary tape. Copy them to a separate unary bank. Make a second copy of $n$ so the two real-coordinate loops use independent heads. Export the exponent counter in canonical order and erase it. Its initial empty representation exports the one-digit word 0.

For each external prefix, loop through $n$ genuine earlier-field positions. At each of their $g$ intervening values handle the $n$ genuine later-field blocks followed by $r$ padding blocks. Then handle the $r$ padded earlier-field positions; each has $g$ complete $t$-block fibres. Each block contains $s$ bits. Embedding copies genuine blocks and writes explicit zeros elsewhere. Restriction copies genuine blocks and physically advances past each other input block, whose contents may be independent. After the native interchange the genuine square remains the genuine square because both axes use the same embedding. The external bit order is therefore the required binary interchange. This argument allows arbitrary occupied prefixes, gaps and suffixes.

## Exact transition formula

Write $b(z)=\max(1,\operatorname{bitlength}(z))$ and $C(z)=11z-6\operatorname{popcount}(z)+12b(z)+3$. The number $C$ is the [independently recounted cost](recount-node.md) of converting a canonical binary numeral to unary with the shared [fixed rule builder](../checks/node-tapes.py). Put $X(0)=1$ and $X(e)=3b(e)+4$ for $e>0$. The exact clock in either direction is
\[
\begin{aligned}
T={}&C(u)+C(g)+C(s)+17(n+t)+15u+21e-2\operatorname{popcount}(e)\\
 &+2(g+s)+X(e)+26+V+W\\
 &+p\{g t^2(2s+6)+g(6t+3n)+6t+7\}.
\end{aligned}
\]
The fixed loops break down as follows.

| Work | Exact transitions |
|---|---:|
| Open and close the 15 temporary boundaries, build three unary descriptors, install the two initial power marks | $5+C(u)+C(g)+C(s)$ |
| $u$ doublings of growing $n$, including their outer loop | $11(n-1)+13u+3$ |
| Failed ternary power comparisons, triplings and exponent increments | $10(t-1)+21e-2\operatorname{popcount}(e)$ |
| Successful comparison, tail copy and three rewinds | $n+3t+8$ |
| Second copy of $n$ and its two returns | $3n+5$ |
| Export the native-width counter | $X(e)$ |
| All genuine and padded blocks, including prefix tests | $p\{gt^2(2s+6)+g(6t+3n)+6t+7\}+1$ |
| Rewind data/output, erase all seven unary bodies and return their heads | $V+W+4+2(u+g+s+2n+t+r)+21$ |

At the $i$th failed comparison the current ternary length is $t_i=3^i<n$. Parallel comparison costs $2t_i+2$ and the two rewinds cost $2t_i+4$. Unary tripling costs $16t_i+10$. Incrementing the exponent costs $2\nu_2(i+1)+3$, including returning its head to the low end. Sum $\sum_{i<e}t_i=(t-1)/2$ and $\sum_{i<e}\nu_2(i+1)=e-\operatorname{popcount}(e)$. At the successful comparison, the binary-size tape stops the test after $2n+1$ steps; the tail transfer costs $r+1$, and resetting the three heads costs $2t+6$.

For an earlier genuine position at one gap value, two unary later loops cost $t(2s+6)+6$. For a padded earlier position one complete unary later loop costs $t(2s+6)+3$. Restoring the gap and the two earlier-position loops yields the prefix term in the table. Output and input exchange their lengths on restriction, so the sum of their two reset costs stays $V+W+4$.

For $z\ge1$, $C(z)\le22z$, since $b(z)\le z/2+1$ for $z\ge2$ and $z=1$ is immediate. When $n\ge4$ use $t<3n$, $W<9V$, $e\le u$ and $u\le n/2$. The full formula divided by $V$ is at most
\[
82+\frac{107}{n}+\frac{85+61u}{n^2}
\le82+\frac{137.5}{n}+\frac{85}{n^2}<122.
\]
The $82$ bounds $1+9W/V$. The prefix terms outside the $t^2$ term contribute at most $39/n+7/n^2$, and $17(n+t)$ contributes at most $68/n$. The remaining descriptor, export and constant terms contribute at most $(78+61u)/n^2$. For $n=2$ insert $u=e=1,\ t=3$. The terms involving data, $p$, and $C(g)+C(s)+2(g+s)$ contribute at most $(21.25+6+6.25+12)V$, and the other 172 steps use at most $43V$. For $n=1$, $T=C(g)+C(s)+2(g+s)+76+4V+15pg+13p$. This is at most $118V$ when $V\ge2$. At $V=1$ it is exactly 152.

## All visited cells

With $\operatorname{bitlength}(0)=0$, the exact sum of the 15 head intervals in either direction is
\[
 V+W+b(u)+b(g)+b(s)+2\operatorname{bitlength}(e)
 +u+g+s+n+2t+\max(g,s,t)+30 .
\]
The 30 accounts for cell 0 and the temporary $-1$ boundary on all 15 banks. Input and output reach their terminal blanks. The two copies of the binary extent, the ternary extent and its tail contribute $2n+t+r=n+2t$. The conversion temporary reaches the largest completed length among $g,s,t$. For $e>0$ the binary accumulator and the exported descriptor both reach their terminal blank. For $e=0$ their heads only reach offset zero at the right end.

For $n\ge2$, this sum is at most $10V+12n+6gs+30\le25V$ using $u\le n/2$. For $n=1$ it is at most $2V+3(g+s)+34$, hence at most $25V$ when $V\ge2$. For $V=1$ it is exactly 41. All nested loops recycle the same banks.

## Joining the marked native program

The range program uses the raw array format of the [direct fallback](node-streams.md). For the [native marked arena](recount-handoff.md), place its left delimiter immediately before the padded array. The [raw/marked transition count](recount-node.md) is $2W+4$ on entering and $2W+3$ on leaving. The native program can take the padded result in place. Let $B=b(p)+b(g)+b(s)+b(e)\le4V$. Copy each of these four raw words to its own marked native descriptor, then erase the returned copy when done. Per word of length $b$ this uses at most $4b+10$ transitions. Install the destination's left delimiter at $-1$, copy its $b$ digits, write its right delimiter and walk both heads left, returning the raw head to zero. After the native call clear the marked copy through the right end and return to its boundary. Treat these four input descriptors as read-only native arguments. Any working copy made inside the native program belongs to its own clock and visited-space bound.

The two range calls cost at most $304V$. The data-marker pair costs at most $4W+7$, the four copies and erasures at most $4B+40$, clearing the padded result after restriction at most $2W+7$, and removing the auxiliary raw $e$ at most $2b(e)+7$. Both range calls may write the same raw $e$ bank, because they overwrite exactly its same digits. Normalizing a separate output back into the original raw bank if requested takes at most $3V+8$, including clearing the temporary output. These bounds sum to at most $512V$, using $W<9V$, $B\le4V$ and $V\ge1$.

Even counting the two adapters' visited sets separately costs at most $82V$. The four original/native descriptor pairs add at most $2B+16$. Data-mark conversion, clearing and normalization traverse the same marked intervals, allowing four further boundary cells. Thus $128V$ covers the full external union in addition to the native machine's own $S_3(W,e)$. When composing inside the integer caller the same set of origin-based external scratch tapes can be reused across consecutive interchange requests.
