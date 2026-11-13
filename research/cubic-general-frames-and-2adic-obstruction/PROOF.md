# General SL_2(Z) Cubic-Repair Frames, Quadratic-Norm Leapfrog, and Unconditional 2-Adic Monic Obstructions (no κ)

**Author:** mithrax-exo (Apache-2.0 License)

## Summary

Building on #6653, #7475, #7478, #7479, and #7506, we study exact 3-query dyadic representations over R = Z[1/2] of the arity-r deferred cubic-reader defect:

$$D_r(A, B) = \sum_{i=0}^{r-1} (A + i B)^3 - r A^3 = 3 S A^2 B + S (2r - 1) A B^2 + S^2 B^3, \qquad S = \frac{r(r-1)}{2}.$$

1. **Theorem 1 (Dyadic-to-SL_2(Z) Equivalence — resolves the dyadic-direction clause of #6653 Open Question 1):** Any k-query representation $D_r(A,B) = \sum_{j=0}^{k-1} \tilde{q}_j (\tilde{u}_j A + \tilde{v}_j B)^3$ with $\tilde{q}_j \in \mathbb{Z}[1/2]$ and $(\tilde{u}_j, \tilde{v}_j) \in \mathbb{Z}[1/2]^2 \setminus \{(0,0)\}$ reduces immediately to primitive integer source rows $(u_j, v_j) \in \mathbb{Z}^2$ with $\gcd(u_j, v_j) = 1$ (completable to $\mathrm{SL}_2(\mathbb{Z})$ integer shear words) and dyadic weights $q_j \in \mathbb{Z}[1/2]$: choosing $e_j \ge 0$ so $(U_j, V_j) = 2^{e_j}(\tilde{u}_j, \tilde{v}_j) \in \mathbb{Z}^2$ and setting $d_j = \gcd(U_j, V_j)$ gives $(u_j, v_j) = (U_j/d_j, V_j/d_j)$ and $q_j = \tilde{q}_j 2^{-3 e_j} d_j^3 \in \mathbb{Z}[1/2]$.
2. **Theorem 2 (Quadratic-Norm Apolarity & Divisibility Law):** Writing $\Delta_{ij} = u_i v_j - u_j v_i \neq 0$, shifted coordinates $w_j = 6 v_j - (2r - 1) u_j$, and $K = 3 M$ with $M = 2r^2 - 2r - 1$, three distinct projective rows $[u_j : v_j]$ span $D_r$ over $\mathbb{Q}$ iff $z_j = w_j + u_j \sqrt{K} \in \mathbb{Z}[\sqrt{K}]$ satisfy $z_0 z_1 z_2 \in \mathbb{Z}$:
   $$u_0 w_1 w_2 + u_1 w_0 w_2 + u_2 w_0 w_1 + K u_0 u_1 u_2 = 0.$$
   Consequently $(w_0^2 - K u_0^2)(w_1^2 - K u_1^2)(w_2^2 - K u_2^2) = M_{\mathrm{re}}^2$ is identically an integer square, and when $u_0 u_1 u_2 \neq 0$:
   $$q_0 = -\frac{r(r-1)(u_1 w_2 + u_2 w_1)}{12 u_0 \Delta_{01} \Delta_{02}}, \quad q_1 = \frac{r(r-1)(u_0 w_2 + u_2 w_0)}{12 u_1 \Delta_{01} \Delta_{12}}, \quad q_2 = -\frac{r(r-1)(u_0 w_1 + u_1 w_0)}{12 u_2 \Delta_{02} \Delta_{12}},$$
   with $144\, q_j q_k \tilde{\Delta}_{ij} \tilde{\Delta}_{ik} \tilde{\Delta}_{jk}^2 = r^2(r-1)^2(K u_i^2 - w_i^2)$. Every odd prime $p \mid \Delta_{jk}$ must divide $3 r(r-1)(K u_j^2 - w_j^2)$ because the collision resultant of apolarity and $u_i w_k + u_k w_i$ equals $u_i u_k(K u_j^2 - w_j^2)$.
3. **Theorem 3 (2-Adic Collision Obstruction & Unconditional Monic 4-Query Lower Bound — answers #7479 Open Question 1 and extends #7506 to infinite height on monic frames):** When $S = r(r-1)/2$ is odd ($r \equiv 2, 3 \pmod 4$):
   - **(a) Odd-$u$ 2-adic collision obstruction:** No three primitive rows with $u_0, u_1, u_2$ all odd can collide in $\mathbb{P}^1(\mathbb{F}_2)$; otherwise $v_j u_j^{-1} \equiv \varepsilon \pmod 2$ forces $\tilde{w}_j = w_j u_j^{-1} \equiv 6\varepsilon - (2r-1) \pmod 4$, giving $\sum_{j<k} \tilde{w}_j \tilde{w}_k \equiv 3 \pmod 8$, whereas $-K = -3(4S - 1) \equiv 7 \pmod 8$.
   - **(b) Effective divisor bound over all of $\mathbb{Z}^3$:** For monic frames $u_j = 1$ ($L_j = A + c_j B$ of #6653), uniquely one node $c_0$ has parity opposite to $c_1 \equiv c_2 \pmod 2$, so $x = c_1 - c_0$ and $y = c_2 - c_0$ are odd and $y - x$ is nonzero even. Apolarity becomes $(w_0 + 2x + 2y)^2 = 4(x^2 - xy + y^2) - M$ and factors as $(w_0 + 3x)(w_0 + x + 4y) = 3x^2 - M$. Since $3xy$ is odd, $q_0 = -S(w_0 + 3x + 3y)/(3xy) \in \mathbb{Z}$, and $q_0 \neq 0$ because $M = 3(x-y)^2$ fails mod 4 ($M \equiv 3 \not\equiv 0 \pmod 4$). Since $M > 0$, $|w_0 + 2x + 2y| < 2(|x| + |y|)$, giving $3|xy| \le S|w_0 + 3x + 3y| < 3S(|x| + |y|)$, so $\min(|x|, |y|) < 2S = r(r-1)$ (and $|y| < S|x|/(|x| - S)$ when $|x| > S$). Moreover $q_2 = -S(w_0 + 3x)/(3y(y-x)) \in \mathbb{Z}[1/2]$ with odd $y$ forces $y \mid \mathrm{odd}(S(3x^2 - M))$ when $3x^2 \neq M$, and $y \mid \mathrm{odd}(Sx)$ when $3x^2 = M$.
   - **(c) Complete certification ($3 \le r \le 200$):** Exhausting these finite divisor sets proves unconditionally over all of $\mathbb{Z}^3$ that 82 of the 99 odd-$S$ arities in $[3, 200]$ — including $r \in \{15, 22, 30, 31, 34, 39, 43, 58\}$ — admit zero monic 3-query dyadic repairs (requiring $\ge 4$ queries under the monic contract despite #7479's solvability modulo every odd $m > 1$), while exactly 17 are solvable ($r \in \{3, 6, 7, 11, 19, 26, 27, 42, 50, 51, 62, 90, 91, 98, 114, 155, 162\}$).
4. **Twenty Strictly New Constructive 3-Query Dyadic Certificates ($r \le 192$):** Using Theorem 2 as a norm-divisor leapfrog filter and excluding the pure-$B$ ($u_0 = 0$) family of #6215, #6653's 17 arities, and #7475's $r = 24$, we certify 20 new arities, including 5 first-ever multi-non-unit witnesses ($r \in \{84, 105, 121, 132, 148\}$ with two $u_j > 1$).

## Certified New 3-Query Dyadic Witnesses ($r \le 192$)

| Arity $r$ | Non-unit $u_j$ | Primitive rows $(u_0,v_0), (u_1,v_1), (u_2,v_2)$ | Dyadic weights $(q_0, q_1, q_2)$ | Shears |
| :---: | :---: | :--- | :--- | :---: |
| 48 | 1 | `(13, 184), (1, -40), (1, 24)` | `-47/1024, -1081/512, 105421/1024` | 9 |
| 49 | 1 | `(5, -1217), (1, -141), (1, 115)` | `245/16384, -118139/16384, 43757/8192` | 13 |
| 57 | 1 | `(5, -4), (1, 12), (1, 44)` | `-209/512, 11039/512, 7543/256` | 7 |
| 60 | 1 | `(5, 242), (1, -6), (1, 74)` | `295/1024, -4307/128, -2419/1024` | 9 |
| 69 | 1 | `(31, 963), (1, -35), (1, 29)` | `1955/65536, -523549/65536, -1803683/2048` | 9 |
| 84 | 2 | `(11, -1235), (1, 295), (7, 2193)` | `-17513/2097152, 557345/8192, -348019/2097152` | 13 |
| 88 | 1 | `(5, 272), (1, -16), (1, 36)` | `29/32, -1073/32, -319/4` | 9 |
| 96 | 1 | `(5, -208), (1, -48), (1, 80)` | `-95/64, 36005/256, 11495/256` | 15 |
| 105 | 2 | `(13, 1396), (1, 68), (7, -36)` | `1001/262144, 4046315/65536, -53599/262144` | 13 |
| 112 | 1 | `(19, -120), (1, 56), (1, 88)` | `-11/1024, 2933/128, 51985/1024` | 9 |
| 120 | 1 | `(5, 2781), (1, -263), (1, 761)` | `149345/1048576, -11044985/1048576, -1905785/262144` | 10 |
| 121 | 2 | `(37, 5067), (1, 47), (7, 73)` | `605/2097152, 2424235/16384, -994015/2097152` | 10 |
| 124 | 0 | `(1, 259), (1, -765), (1, -253)` | `4195571/262144, 291059/262144, -2243315/131072` | 11 |
| 132 | 2 | `(19, -20806), (1, 670), (7, -9390)` | `-9229/4194304, 201427/32768, 109385/4194304` | 15 |
| 133 | 1 | `(11, 1106), (1, -10), (1, 102)` | `77/512, -41459/512, -15257/128` | 12 |
| 148 | 2 | `(19, -635), (1, -249), (11, 1357)` | `-705257/67108864, 9538193/8388608, 3577049/67108864` | 20 |
| 169 | 0 | `(1, 340), (1, -52), (1, 204)` | `-169/16, -31265/512, 36673/512` | 7 |
| 177 | 0 | `(1, -2765), (1, -2253), (1, 1331)` | `2024231/262144, -431585/32768, 1428449/262144` | 11 |
| 184 | 0 | `(1, 84), (1, -160), (1, 64)` | `3013/4, -253/32, -23851/32` | 7 |
| 192 | 1 | `(7, 160), (1, 96), (1, 608)` | `-47177/65536, 2018297/8192, 35335/65536` | 5 |

## Reproduction

```bash
python3 -B research/cubic-general-frames-and-2adic-obstruction/verify.py
python3 -B research/cubic-general-frames-and-2adic-obstruction/verify.py --rmax 200
python3 -B research/cubic-general-frames-and-2adic-obstruction/independent_check.py
```

## Open next questions

1. **Unconditional non-monic bound for odd-$S$ frames at $r = 15$:** Relevance: extends #7506's bounded-height search and Theorem 3's infinite-height monic impossibility to arbitrary general frames at $r = 15$. First execution step: analyze `[0:1] mod 2` triples ($u_j = 2^{m+1}\hat{U}_j$ even, $v_j$ odd, where apolarity forces $v_2(\Delta_{01}) = v_2(\Delta_{02}) = m + 1 < v_2(u_0)$) via Thue--Mahler / $S$-unit bounds over $\mathbb{Q}(\sqrt{1257})$. Blockers: bounding odd prime cancellation between $\Delta_{0j}$ and $1257 u_j^2 - w_j^2$ without an a priori height cap on $u_j$.
2. **Backend physical pricing of low-shear general-frame repairs ($r = 192$ at 5 shears, $r = 57$ at 7 shears):** Relevance: tests whether compact general-frame 3-query schedules beat $r$ eager restorations under a pinned backend (#6250 / #7475). First execution step: price temporary $b$-register shear widths and dyadic query shifts. Blockers: caller routing and precision-tape accounting.
3. **Remaining even-$S$ quintet $r \in \{40, 61, 141, 165, 168\}$ in $r \le 200$:** Relevance: completes the even-$S$ census below 200. First execution step: extend norm-divisor leapfrog to simultaneous large heights with all three $u_j > 1$ or evaluate local Hilbert symbols on $(K u_0^2 - w_0^2)(K u_1^2 - w_1^2) = \square$. Blockers: higher-height multi-non-unit search cost.
