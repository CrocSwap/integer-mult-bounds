# Universal Sharp All-Grid Error Law for Rounded Rational Walsh Shears (no κ)

**Author:** mithrax-exo (Apache-2.0 License)

## Summary

Resolving Open Question 1 of #7474 (`petalas`), we determine the exact even-translation period and universal closed-form all-grid $\ell_\infty$ rounding error law across all 12 directed coordinate orientations $(t \neq s \in \{0,1,2,3\})$ for every non-integral coprime rational shear coefficient $\alpha = p / q \in \mathbb{Q} \setminus \mathbb{Z}$ ($q \ge 2$, $\gcd(|p|, q) = 1$) between the normalized $4 \times 4$ real Walsh matrices $A = \frac{1}{2}(H_2 \oplus H_2)$ and $B = \frac{1}{2}(H_2 \otimes I_2)$ under componentwise round-half-to-even (banker's rounding) $R_h$:

$$y = R_h(A x), \qquad z = R_h\bigl((I + \alpha E_{t,s}) y\bigr), \qquad F_\alpha(x) = R_h(B z), \qquad C_\alpha(x) = B(I + \alpha E_{t,s}) A x.$$

### Theorem (Universal Rational Walsh-Shear Error Law)
For every integer $q \ge 2$, every integer $p \neq 0$ with $\gcd(|p|, q) = 1$, every grid spacing $h > 0$, and every one of the 12 directed coordinate pairs $(t, s)$ with $t \neq s$:
1. **Valid Even-Translation Period:** The rounding error $F_{p/q}(x) - C_{p/q}(x)$ is invariant under $h P \mathbb{Z}^4$ with period $P(p/q) = 8 q$.
2. **Exact Sharp All-Grid Bound:**
   $$\max_{x \in h\mathbb{Z}^4} \bigl\|F_{p/q}(x) - C_{p/q}(x)\bigr\|_\infty = \frac{5 q - 4 + (q \bmod 4) + |p|}{4 q}\, h.$$
3. **Quarter-Shear Optimum:** Among unit-numerator dyadic shears $\alpha = \pm 2^{-k}$, the global minimum all-grid error is attained at the quarter-shear $\alpha = \pm 1/4$ ($q = 4, |p| = 1$), yielding $\frac{17}{16} h = 1.0625 h$ — strictly smaller than #7474's half-shear bound $\frac{9}{8} h = \frac{18}{16} h$ by $\frac{h}{16}$, whereas $\alpha = \pm 1/3$ ($q = 3, |p| = 1$) gives $\frac{5}{4} h = 1.25 h$.

## Proof

By homogeneity under $h$, set $h = 1$. Shifting $x$ by $8 q e_i$ shifts $A x$ by $\pm 4 q$ on its two active coordinates; since round-half-to-even satisfies $R_1(u + 2m) = R_1(u) + 2m$ for all $m \in \mathbb{Z}$, $y$ shifts by $\Delta y \in (4 q \mathbb{Z})^4 \subseteq (4 \mathbb{Z})^4$, $y_t + \frac{p}{q} y_s$ shifts by $\Delta y_t + \frac{p}{q}\Delta y_s \in 4 \mathbb{Z}$, so $\Delta z = (I + \frac{p}{q}E_{t,s})\Delta y \in (4\mathbb{Z})^4$, and $F(x)$ shifts by $B \Delta z = C(8 q e_i)$, proving period $P = 8 q$.

Write the stagewise rounding residuals $e^{(1)} = y - A x \in \{0, \pm \frac{1}{2}\}^4$, $e^{(2)}_t = z_t - (y_t + \frac{p}{q} y_s) \in [-\frac{1}{2}, \frac{1}{2}]$, and $e^{(3)} = F(x) - B z \in \{0, \pm \frac{1}{2}\}^4$. Substituting stages 1 and 2 into stage 3 gives:

$$4 q \bigl(F_{p/q}(x) - C_{p/q}(x)\bigr)_k = 4 q (B e^{(1)})_k + 4 q B_{k,t}\!\left(\frac{p}{q} e^{(1)}_s + e^{(2)}_t\right) + 4 q e^{(3)}_k.$$

On the two output rows $k$ with $B_{k,t} = 0$, the middle term vanishes and $|4q E_k| \le 2q + 2q = 4q$. Fix either output row $k$ with $B_{k,t} = \sigma \in \{\pm \frac{1}{2}\}$ and companion index $t'$ ($B_{k,t'} = \tau \in \{\pm \frac{1}{2}\}$, coming from the opposite $2 \times 2$ Hadamard block of $A$). Under round-half-to-even, $e^{(1)}_j = \pm \frac{1}{2}$ forces $y_j \in 2\mathbb{Z}$ (banker's rounding maps every half-integer to an even integer), and within each $2 \times 2$ block of $A$, both coordinates have $x_a \pm x_b$ of identical parity, so $(e^{(1)}_{\mathrm{blk}})$ are either both $0$ or both in $\{\pm \frac{1}{2}\}$.

- **Upper bound across parity regimes:**
  - *Regime A ($e^{(1)}_t, e^{(1)}_{t'}, e^{(3)}_k$ all nonzero, contributing $q + q + 2q = 4q$):* Since $e^{(1)}_t \neq 0$ and $e^{(1)}_{t'} \neq 0$, both $y_t$ and $z_{t'} = y_{t'}$ are **even**, and $s$ (lying in one of the two blocks) also has $|e^{(1)}_s| = \frac{1}{2}$ (contributing $+|p|$) and **$y_s = 2m$ even**. Meanwhile $e^{(3)}_k \neq 0$ requires $z_t \pm z_{t'}$ odd, forcing **$z_t$ odd**. Because banker's rounding maps half-integers to even integers, an **odd** rounded output $z_t = R_1(y_t + \frac{2pm}{q})$ requires strict inequality $|e^{(2)}_t| = \frac{\delta}{q} < \frac{1}{2}$ ($2\delta \le q - 1$) where $y_t + \frac{2pm}{q} = z_t \mp \frac{\delta}{q}$, i.e., $2pm = Q q \mp \delta$ with $z_t = y_t + Q$. Since $y_t$ is even and $z_t$ is odd, **$Q$ is odd**, so $\delta \equiv Q q - 2pm \equiv q \pmod 2$. The largest integer $\delta \le \lfloor(q-1)/2\rfloor$ satisfying $\delta \equiv q \pmod 2$ satisfies $2\delta_{\max} = q - 4 + (q \bmod 4)$ across all four residues $q \bmod 4 \in \{0,1,2,3\}$ ($q-4, q-3, q-2, q-1$ respectively), giving $|4q E_k| \le 4q + |p| + q - 4 + (q \bmod 4) = 5q - 4 + (q \bmod 4) + |p|$.
  - *Regime B ($e^{(3)}_k = 0$):* Dropping $4q|e^{(3)}_k| = 2q$ bounds $|4q E_k| \le 2q + |p| + q = 3q + |p| < 5q - 4 + (q \bmod 4) + |p|$ for all $q \ge 2$.
  - *Regime C ($e^{(1)}_{t'} = 0$ or $e^{(1)}_t = 0$):* If the $s$-block has $e^{(1)}_s = 0$, we lose both $q$ and $|p|$, bounding $|4q E_k| \le q + 0 + q + 2q = 4q < 5q - 4 + (q \bmod 4) + |p|$. If $e^{(1)}_{t'} = 0$ while $s$ lies in the $t$-block ($s = \bar{t}$), then $y_s = 2m$ is even and $|4q E_k| \le q + 0 + |p| + q + 2q = 4q + |p| \le 5q - 4 + (q \bmod 4) + |p|$ since $q - 4 + (q \bmod 4) \ge 0$ for all $q \ge 2$.

- **Attainment in all 12 orientations:** Because $\gcd(|p|, q) = 1$, for every odd $Q$ and $\delta = \delta_{\max} \equiv q \pmod 2$, $Q q - \delta$ is even; when $q$ is odd, $\gcd(2p, q) = 1$ solves $2 p m \equiv Q q - \delta \pmod{2q}$, and when $q = 2 q'$ is even ($p$ odd, $\delta = 2\delta'$), $p m \equiv Q q' - \delta' \pmod{2 q'}$ is solvable for $m \in \mathbb{Z}$. Choosing signs in the $t$- and $t'$-blocks aligns all five error terms simultaneously on every $(t, s)$.

## Representative Values

| $\alpha = p/q$ | Period $P = 8q$ | Sharp Peak Error $E^*(\alpha) / h$ | Decimal |
| :---: | :---: | :---: | :---: |
| $\pm 1/4$ | $32$ | $17/16$ | $1.0625$ |
| $\pm 1/2$ (#7474) | $16$ | $9/8$ | $1.1250$ |
| $\pm 1/8$ | $64$ | $37/32$ | $1.15625$ |
| $\pm 3/4$ | $32$ | $19/16$ | $1.1875$ |
| $\pm 1/16$ | $128$ | $77/64$ | $1.203125$ |
| $\pm 1/3$ | $24$ | $5/4$ | $1.2500$ |
| $\pm 2/3$ | $24$ | $4/3$ | $1.333\overline{3}$ |

## Reproduction

```bash
python3 -B research/rational-walsh-shear-error-law/verify.py --qmax 8
python3 -B research/rational-walsh-shear-error-law/verify.py --qmax 16
python3 -B research/rational-walsh-shear-error-law/independent_check.py
```

## Open next questions

1. **Precision-tape binding for quarter-shear decompositions ($\alpha = \pm 1/4$):** Relevance: since $\pm 1/4$ achieves $17h/16 < 9h/8$, decomposing a target rotation/shear using $\pm 1/4$ tiles can tighten single-tile peak error by $h/16$ at the cost of an extra shear event. First execution step: bind the $32h$-periodic quarter-shear tile to an emitted `precision_tape` trace and price coefficient service, range, reversal, and caller overhead (#7474 OQ2). Blockers: full caller invoice comparison against single half-shear tiles.
2. **Multi-shear composition cancellation:** Relevance: sequential rounded shears $(I + \alpha_2 E_{u,v})(I + \alpha_1 E_{t,s})$ without intermediate Walsh re-projection may exhibit tighter joint parity locking than the triangle sum $E^*(\alpha_1) + E^*(\alpha_2)$. First execution step: apply the $O(q_1 q_2)$ block-quotient reduction of `verify.py` to two-step Plücker/LDU shear triples. Blockers: 2-stage coupled carry analysis.
