# Independent transition count for role selection and the direct base

This recount starts from the generated rule table in [node-tapes.py](../checks/node-tapes.py). It expands the loops, derives an exact clock before replay, and runs the table in [a separate interpreter](https://github.com/CubeJerry/integer-mult-bounds/blob/a2a17b61d943676c757e0bbfaef3f4fae03ab8e5/research/moonshot-overhead-program/sessions/2026-11-26-S008/recount-node.py). The interpreter checks both that the last transition halts and that no earlier transition halted. A coordinate oracle checks the output word and every retained descriptor. The bank’s data begin at its entry head; the raw words end at the first blank. Binary dimension fields are canonical unsigned MSB-first strings, with zero represented by a single 0.

## Unary instruction costs

Write $r(x)=\max(1,\lfloor\log_2 x\rfloor+1)$ for the length of the canonical numeral, with $r(0)=1$, and $b(x)$ for its number of 1 bits. Rewinding a bank from its terminal blank after $z$ symbols costs $z+2$ transitions, one for each move back to the home marker at $-1$ and one returning to the first data cell. A unary run over $s$ marks costs $2s+3$ with its own reset. A unary outer loop over $z$ body invocations has overhead $3z+3$ beyond those bodies. These identities also hold for an empty loop.

Scaling a unary string of length $t$ by $k$ and adding $v\in\{0,1\}$ takes $(5k+1)t+5v+10$. There are $kt+1+v$ emitting/checking steps, $t+2+kt+v+2$ rewinding steps, $kt+v+1$ destructive return steps, and $2(kt+v+2)$ final reset steps. Therefore the complete binary-to-unary setup takes exactly
$$
C(x)=11x-6b(x)+12r(x)+3.
$$
Indeed the sum of incoming MSB-first prefixes over all digits is $\sum_{j\ge1}\lfloor x/2^j\rfloor=x-b(x)$. There is a dispatch per digit, a blank dispatch and a final descriptor rewind. For $x\ge1$, $C(x)\le26x$, while $C(0)=15$. Division of a positive unary multiple $t$ of three costs $10t/3+10$. Its scan has $t+1$ steps; its first reset costs $t+t/3+4$, its destructive copy costs $t/3+1$, and its last reset costs $2t/3+4$.

## A complete role pass

For $P,J,K,s\ge1$, $0\le i<J$ and $0\le d<K$, operate on two arrays of shapes $[P,J,s]$ and $[P,K,s]$. Over every prefix copy the source run at $i$ into the existing destination run at $d$ or XOR those bits into it. Write $W=Ps(J+K)$. The rule uses exactly
$$
\begin{aligned}
T={}&C(J)+C(K)+C(i)+C(d)+C(s)\\
 &+P\{s[3(J+K)-2]+6(J+K)+4\}\\
 &+7(J+K)+2s+38
 \ \le\ 103W.
\end{aligned}
$$
It visits at most $30W$ cells including the 15 raw and scratch tapes. This includes construction of the after-role extents, paired scanning, rewinds, unary scratch cleanup, and boundary installation and removal.

For each input arity, after-range construction takes $3J+6$ or $3K+6$. For example a forward skip over $i$ marks, an extra step skipping the selected slot, a preserved-source copy forward over $J-i-1$ marks, its terminal branch, and the three rewinds give $(i+1)+(J-i)+(J+2)+(i+2)+(J-i-1+2)=3J+6$. Each prefix has four skip loops, one selected run and one prefix dispatch. The sum of the four skip lengths is $J+K-2$. Thus the per-prefix cost is $2s(J+K-1)+6(J+K)+4$, and the final prefix test costs one. Both bank resets cost $W+4$. Erasing seven unary descriptors costs $4(J+K)+2s+17$. Two boundary steps open the computation and two close it. Combining terms gives the equality. For the inequality, $C(J)+C(i)\le52J$ and $C(K)+C(d)\le52K$, since $C(0)=15$; $C(s)\le26s$. The five conversions cost at most $65W$, the prefix term at most $11W$, and the last term at most $27W$. Each tape head stays between $-1$ and $W$, and $W\ge2$, proving the space claim. Empty before-ranges and after-ranges require their fixed branch and rewind actions, already included.

## A complete direct interchange

Let $V=P G S\,9^e$ with $P,G,S\ge1$. At trit $j=0,\ldots,e-1$, read $[p][3][g][3][s]$ where $p=P3^j$, $g=G3^{e-1}$, and $s=S3^{e-1-j}$. The gap length stays fixed as the higher trits move from suffix to prefix. The nine lanes gather by the two trit values, and emit with their roles exchanged. Their internal order preserves prefix, gap and suffix. Repeating over $j$ exchanges all corresponding trits and leaves the occupied spectators unchanged.

One traversal costs $p(18gs+36g+10)+1$. There are three outer trit values, three suffix runs per gap group, the $3g+3$ outer overhead for each trit, and one dispatch per prefix and at the terminus. The input bank goes to offset $V$ and each of nine lanes to $V/9$. Rewinding all ten costs $2V+20$. Two sweeps plus two such resets cost exactly
$$ D(p,g,s)=8V+72pg+20p+42.$$

For reproducibility, [the checker](https://github.com/CubeJerry/integer-mult-bounds/blob/a2a17b61d943676c757e0bbfaef3f4fae03ab8e5/research/moonshot-overhead-program/sessions/2026-11-26-S008/recount-node.py) gives the exact sum over every setup, digit and teardown transition. In words, use the three conversions $C(e),C(G),C(S)$, the increases of both gap and suffix unary sizes for $e-1$ steps, the $e$ digit passes, and the $e-1$ divisions of suffix size by three. Final cleanup erases the three unary descriptors. The positive-width entry and exit tests and resets contribute their literal constant and length-dependent terms. For $e=0$ the identity path takes exactly five transitions, including markers, and every head sees only two cells.

Here is one uniform bound for the positive branch. Each digit has $D(p,g,s)\le23V$ since $pg\le V/9$, $p\le V/9$ and $V\ge9$. Its two control transitions therefore give at most $25V$. Also $e,G,S,3^{e-1}G,3^{e-1}S\le V/9$. The three unary conversions cost at most $26V/3$. The sums for the growth loops and their final reset are $8(3^{e-1}-1)(G+S)+22(e-1)+1+(e+2)\le6V$. The suffix divisions cost $5S(3^{e-1}-1)+10(e-1)\le2V$. The remaining scalar dispatch, final $e$ rewind, three erasures and closing markers total at most $4V$. These estimates imply the advertised $128(e+1)V$ uniformly. The 17 heads remain in $[-1,V]$, also during unary construction, so they visit at most $17(V+2)\le51V$ cells. These bounds allow every positive spectator extent and every binary payload.

## Joining the two bank representations

The [parent/child wrapper](recount-handoff.md) represents a word by explicit left and right delimiters, with entry at the left delimiter. The direct machine above represents a raw word ending at blank and begins on the first bit. The direct machine designates the cell immediately before its entry as its private marker area. The same physical tape supports both conventions at a counted cost. Starting at the wrapper’s left delimiter, step right, traverse $g$ bits, replace the explicit right delimiter by blank and step left, rewind the $g$ bits, then erase the left delimiter and step right. This costs $2g+3$ and leaves exactly the raw input expected by the direct machine, including its private blank marker cell. On raw return step left, install a left delimiter and step right, traverse the $g$ bits, write the new right delimiter at the first blank and step left, rewind $g$ bits, and enter the continuation from the left delimiter. This takes $2g+4$. The two adapters together cost $4g+7$ and do not move beyond the two boundary cells. The same conversion applies to any saved binary dimension with its own actual length when required.
