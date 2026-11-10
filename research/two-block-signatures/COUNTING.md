# Exact labeled counts and the size of the binary exception

Let $L,R$ count messages of types $(AA,AM,MA)$ and $(BB,BM,MB)$ respectively, and let $n=p+q$. Once $L,R$ positions are selected, the rest are $MM$. Write $T(n,L,R)=\binom nL\binom{n-L}R$ and $H(k)=3^k-2\cdot2^k+1$. The latter counts length-$k$ words on three letters using both specified nondefault letters. The classification in [PROOF.md](PROOF.md) gives the following $O(pq)$ formula in arithmetic operations for the number $G_{p,q}$ of ordinary signatures.
$$
G_{p,q}=\sum_{L=0}^p\sum_{R=0}^q T(n,L,R)\,B_{L,R}.
$$

| Occupancy | $B_{L,R}$ |
| --- | --- |
| $L<p,\ R<q$ | $3^{L+R}$ |
| $L=p,\ R<q$ | $H(p)3^R$ |
| $L<p,\ R=q$ | $3^L H(q)$ |
| $L=p,\ R=q$ | $1+2(2^p-1)(2^q-1)+H(p)H(q)$ |

In the interior neither saturation can occur. If only $L=p$, at least one $AM$ and one $MA$ are required. The second edge follows by exchanging block names. At the corner the presence of $AM$ must agree with the presence of $MB$, and $MA$ with $BM$. Splitting into neither, just one, or both gives the last entry.

Let $D_{p,q}$ be the number of ordinary signatures excluded over $\mathbb F_2$. The three exceptional cases in the proof are disjoint. Write $l=p-1$, $r=q-1$, and set
$$
\begin{aligned}
C(l,r)&=3^l+3^r+2^{l+r+1}-2^{l+1}-2^{r+1}+1,\\
S(p,q)&=\sum_{\substack{3\le v\le q\\v\ {\rm odd}}} T(n,p-1,q-v)\,3^{q-v}.
\end{aligned}
$$
Then
$$
D_{p,q}=T(n,l,r)C(l,r)+S(p,q)+S(q,p),\qquad
\#\{\text{binary signatures}\}=G_{p,q}-D_{p,q}.
$$

For a $1$-by-$1$ core, all saturation tests are automatic. If the left slots have neither $AM$ nor $MA$, the right slots have $3^r$ choices. Only $AM$ on the left gives $(2^l-1)2^r$ failing choices, since $MB$ must be absent on the right. Only $MA$ gives the same count. Both on the left force every right slot to be $BB$, contributing $H(l)$. Adding gives $C(l,r)$. For the odd $1$-by-$v$ core, every one of the $p-1$ left slots must be $AA$ and each of the $q-v$ right slots is arbitrary. This gives $S(p,q)$, and exchange of blocks gives the other side.

At $(3,3)$ the terms are $3150+15+15=3180$, against $G_{3,3}=33727$. At $(2,2)$ the deficit is 84, recovering the 439 ordinary and 355 binary-field codes in #6691. The 391 zero-one rational signatures from #3990 concern a different coefficient domain.

**Balanced growth.** As $d\to\infty$,
$$
G_{d,d}\sim49^d,\qquad
D_{d,d}\sim \frac{d^{3/2}16^d}{4\sqrt{\pi}},\qquad
\frac{D_{d,d}}{G_{d,d}}\sim
\frac{d^{3/2}}{4\sqrt{\pi}}\left(\frac{16}{49}\right)^d .
$$
Of the $7^{2d}$ seven-letter words, every one with $L,R<d$ is ordinary. There are at most $48^d$ words with $L\ge d$ by weighting each left symbol by $4/3$ and bounding the resulting sum $(3(4/3)+4)^{2d}/(4/3)^d$. The same bound holds for $R\ge d$. For the deficit, $T(2d,d-1,d-1)=\tfrac12 d^2\binom{2d}{d}$ and $C(d-1,d-1)\sim 4^d/2$. Each side sum is at most $\binom{2d}{d-1}4^{d+1}$, by allowing all four choices for each remaining position. The corner dominates by a factor of order $d^2$. Stirling's formula for the central binomial coefficient gives the displayed equivalences. The absolute number of missing signatures grows even as their fraction tends to zero.
