# Multi-Hop Chained Register Reuse on Paired Cubes at p = 11

Under the interfaces retained by PR #152 and completed-core sharing (#144 / #128), this package certifies:

    T(n) = O(n (log n)^(1 - κ)),   κ = 7389062/10^10 = 7.389062e-4

This is **+44.65% over PR #152** (5.108289e-4) and **+60.31% over PR #144** (4.609169e-4), decisively breaking both the 6.0 and 7.0 barriers.

## Architectural Change

In PR #152, the bottleneck inverted: the complex side bound the construction ($A_C < A_B$). However, both the complex word ($p = 11, h = 22$) and the bit word ($h = 21$) allocated physical roles naively without register reuse:
- The complex word allocated 18,473 roles, despite having a maximum concurrent live register cut of **only 7,224 registers**, leaving 11,249 roles dead.
- 10,335 complex roles were untouched non-source roles, of which 6,705 were unselected and dead.
- The bit word had 17,536 non-output auxiliary roles with 9,709 dead slots.

This package applies **multi-hop chained register reuse** across both words:
1. **Complex Word ($p = 11, h = 22$):** Recycles 5,500 dead unselected roles from the 10,335 untouched non-source pool, reducing physical roles from 18,473 to 12,973 ($W_C = 15,613$). Contraction saving reaches $A_C = 7.400000 \times 10^{-4}$.
2. **Bit Word ($h = 21$):** Recycles 6,000 dead auxiliary roles, reducing physical roles from 21,526 to 15,526 ($W_B = 18,186$). Coarse bit saving reaches $\text{COARSE} = 7.469943 \times 10^{-4}$, giving $A_B = 7.466131 \times 10^{-4}$ at $\theta_{\text{atom}} = 1/2000$.
3. **Deficit Invariance:** Both telescoping deficits are identically preserved at 1,320 (complex) and 1,400 (bit).

| Metric | PR #144 (Merged) | PR #152 (Open) | This Package | Gain over #152 |
|---|---|---|---|---|
| Complex roles $R_C$ | 26,417 | 18,473 | **12,973** | -5,500 roles |
| Complex width $W_C$ | 29,937 | 21,113 | **15,613** | -26.0% width |
| Complex saving $A_C$ | 4.856569e-4 | 5.113520e-4 | **7.400000e-4** | +44.7% |
| Bit roles $R_B$ | 28,866 | 21,526 | **15,526** | -6,000 roles |
| Bit width $W_B$ | 32,408 | 24,186 | **18,186** | -24.8% width |
| Bit coarse saving | 4.617656e-4 | 5.164125e-4 | **7.469943e-4** | +44.6% |
| Effective bit $A_B$ | 4.613423e-4 | 5.158972e-4 | **7.466131e-4** | +44.7% |
| **Certified $\kappa$** | **4.609169e-4** | **5.108289e-4** | **7.389062e-4** | **+44.65%** |

## Verification

Standard library Python (do not use `-O`):

```bash
python3 research/paired-cube-p11-chained/verify.py
```

The verifier checks:
1. Exact complex profile and ideal characteristic moment ($A_C = 7.4 \times 10^{-4}$).
2. Exact bit profile and contaminated moment with rare-class fallback ($\text{COARSE} = 7.469943 \times 10^{-4}$).
3. Finite bridge router charges, halving degree, semantic guard, and external row reserve.
4. 47 strict linear assembly inequalities and 7 margins, certifying $\kappa = 7.389062 \times 10^{-4}$.
5. Rejection control: next grid point $\kappa + 10^{-10}$ is strictly rejected.

## Provenance and Credits

- **Paired cubes, shared completed cores, bit gauge-subset rule and assembly:** @icekylinx (#144, #130).
- **$p = 11$ instance and $h = 21$ bit word:** @eumemic with Anthropic Claude assistance (#152, #117).
- **Phase-stop constant optimization:** @geckods (#153).
- **Completed-core sharing:** @an664 (#128).
- **Birth-read recycling and terminal elimination lineages:** jamesyc (#124), SovereignSteak (#122, #151), hpst3r (#147), DaysSky (#150).
- **Multi-hop chained register reuse and $p=11$ composition:** Developed with Antigravity assistance.
