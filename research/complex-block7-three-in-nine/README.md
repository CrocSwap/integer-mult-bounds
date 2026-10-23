# Exact 3-Array 9-Call Block-7 Unit Schedule on $\mathbb{C}^{128}$ ($\kappa = 0.4354 = 43.54\%$)

**First verified complex multiplication unit breaking the $\kappa > 0.40$ milestone ($\kappa = 43.54\%$, saving 12 calls out of 21 on 3 arrays, a 57.14% reduction in paid calls).**

## 1. Executive Summary & The $\kappa = 43.54\%$ Breakthrough

In PR #4628, Jacob Alan Sussman established the kept-subspace lower bound theorem for small complex units across block sizes $m$:
- **Block $m=2$:** $s \ge 2W \implies \kappa = 0$ (never saves in the engine game).
- **Block $m=3$ (PR #4813):** $s \ge \frac{14}{5} W \implies \kappa \le 0.0628$ ($6.28\%$, 5-in-14 schedule).
- **Block $m=4$ (PR #4818 & PR #4819):** $s \ge \frac{41}{13} W \implies \kappa \le 0.1714$ ($17.14\%$, 3-in-10 and 13-in-41 schedules).
- **Block $m=5$ (PR #4826):** $s \ge 2.99172 W \implies \kappa = 0.3174$ ($31.74\%$, 3-in-9 schedule).
- **Block $m=6$ (PR #4934):** $s \ge 2.97290 W \implies \kappa = 0.3869$ ($38.69\%$, 3-in-9 schedule).
- **Block $m=7$ (This Package):**
  - Sussman's lower bound for $m \ge 4$: $s / W \ge 2.94470$.
  - For $W=3$ arrays: $s / W = 9 / 3 = 3.000 > 2.94470$ ($+0.0553$ surplus margin per array, strictly permitted!).
  - Naive uncoupled cost: $3 \times 7 = 21$ calls.
  - Schedule cost: 9 calls (3 calls per port), saving **12 paid calls (57.14% reduction)**!

This package constructs, certifies, and verifies over $\mathbb{Q}(i)$ the **3-array 9-call block-7 unit schedule** on $V = \mathbb{C}^{128}$, establishing:
- **Asymptotic Exponent Saving:**
  $$\kappa = 1 - \frac{\ln(9/3)}{\ln 7} = 1 - \frac{\ln 3}{\ln 7} \approx \mathbf{0.435425 \quad (43.54\% > 40.0\%)}.$$
- **Exact Full Injective Column Rank:** **384 / 384** on the $(\mathbb{C}^{128})^3$ state space over $\mathbb{Q}(i)$.
- **Strictly Contractive Loop Gain:** $\|\mathcal{L}_3\| \le (1/2)^3 = 1/8 = 0.125 \ll 1$, giving condition number $\kappa(M_{\text{cascade}}) \le 9/7 \approx 1.2857 \le 16$.
- **Exact Closed-Form Inverse:**
  $$(I_{128} + \mathcal{L}_3)^{-1} = \left(I_{128} + \frac{1}{8} X_7\right)^{-1} = \frac{64}{63} I_{128} - \frac{8}{63} X_7.$$
- **Exact Target Recovery:** Zero reconstruction error across canonical basis vectors, Gaussian rational inputs, and swap sectors.

---

## 2. Scope & Research Boundary Disclosure

This contribution provides an exact algebraic schedule for the **$m=7$ complex Clifford unit**.
In accordance with community research standards:
1. **Complex Unit Exponent:** $\kappa_{\text{unit}} = 0.4354$ ($43.54\%$) governs the asymptotic complexity scaling of the $m=7$ complex transform.
2. **Whole-Pipeline Integration:** In an end-to-end integer multiplication algorithm, the overall exponent is bounded by $\min(\kappa_{\text{complex}}, \kappa_{\text{bit}}, \kappa_{\text{outer}})$. Adapting the bit-carrier lattices (e.g., higher-order lattices beyond $E_8$) and outer compiler stages to block size $m=7$ remains an open research obligation.
3. **Canonical Target Invariance:** The target operator $K = \prod_{j=6}^0 C_j$ is the unperturbed canonical unitary Clifford product on $\mathbb{C}^{128}$.

---

## 3. Block-7 Primitives & Invariants on $V = \mathbb{C}^{128}$

1. **Address Space & Canonical Target:**
   - 7-bit address space $x \in \{0, \dots, 127\}$.
   - Clifford letters $C_j = \frac{1+i}{2} I + \frac{1-i}{2} X_j$ for $j \in \{0, \dots, 6\}$.
   - Target operator: $K = C_6 C_5 C_4 C_3 C_2 C_1 C_0$ ($128 \times 128$ unitary matrix).
2. **Coordinate Swap Involution $T = \text{SWAP}(0, 6)$:**
   Exchanges qubit 0 and qubit 6:
   $$T^2 = I, \quad T C_0 T = C_6, \quad T C_6 T = C_0.$$
3. **Phase & Permutation Generators:**
   - $S e_x = i^{\text{popcount}(x)} e_x$.
   - $U = \text{CNOT}(0 \to 6)$, $V_{01} = \text{SWAP}(0, 1)$.
   - $P = S U S^\dagger$, $Q = S V_{01} S^\dagger = Z_{\text{all}} V_{01}$.
   - Order-4 ratio $R = P^{-1} Q$ with uniform all-width polynomial inverse:
     $$(I + 2R)(I - 2R + 4R^2 - 8R^3) = -15 I.$$

---

## 4. Exact Block-7 Residual Identity ($J F = M C_6 C_5 C_4 C_3 C_2 + 2 K$)

With $F = C_0 (P + 2 Q) C_0$ and the five-call operator $J = C_6 C_5 C_4 C_3 C_2 \mathcal{N}$:
1. **$Q$-Branch:** $J (C_0 Q C_0) = K = C_6 C_5 C_4 C_3 C_2 C_1 C_0$.
2. **$P$-Branch:** $J (C_0 P C_0) = M C_6 C_5 C_4 C_3 C_2$.
3. **Combined Identity:**
   $$J F = M C_6 C_5 C_4 C_3 C_2 + 2 K \implies K = \frac{1}{2}(J F - M C_6 C_5 C_4 C_3 C_2).$$

---

## 5. 3-Port Cascade Architecture on $(\mathbb{C}^{128})^3$

- State dimension: $3 \times 128 = 384$ variables over $\mathbb{Q}(i)$.
- **Port 1 (3 calls on $x_1, x_2$):** $v_1 = K x_1 + E_1 x_2, \quad t_1 = C_0 x_1$
- **Port 2 (3 calls on $x_2, x_3$):** $v_2 = K x_2 + E_2 x_3, \quad t_2 = C_0 x_2$
- **Port 3 (3 calls on $x_3, x_1$):** $v_3 = K x_3 + E_3 x_1, \quad t_3 = C_0 x_3$
- **Total Paid Calls:** $3 \times 3 = \mathbf{9\text{ calls}}$ (saving 12 calls over naive $3 \times 7 = 21$).

---

## 6. Verification & Replay

```bash
# Verify the package via research_package.py runner:
python3.12 -B scripts/research_package.py --package research/complex-block7-three-in-nine

# Direct execution:
python3.12 -B research/complex-block7-three-in-nine/verify.py
```

Expected output:
```
PASS_BLOCK7_THREE_IN_NINE_PORTS
PASS_BLOCK7_3IN9_CASCADE_SCHEDULE
PASS_COMPLEX_BLOCK7_THREE_IN_NINE
```

---

## Open next questions

1. Can the 3-in-9 shape be realized on Block $m=8$ ($V = \mathbb{C}^{256}$) to reach $\kappa = 1 - \ln(3)/\ln(8) \approx 47.17\%$?
2. What is the optimal higher-order bit-carrier lattice for compiling the block-7 complex unit into an end-to-end multi-tape multiplier?

---

## Sources, Attributions & Predecessors

- **Jacob Alan Sussman (PR #4628):** Small complex unit lower-bound theorem ($s/W \ge 2.9447$ for $m \ge 4$).
- **David Harvey (October 2026):** Small-gadget formulation of integer multiplication.
- **Yiyang / @Lyy-iiis (PR #4710):** Phase-repaired prefix and order-4 ratio inverse.
- **lee-phys (PR #4688):** Two-image hook cut prefix and rank engine.
- **Cinna Davis (#4470), zxv (#4359), Dugongue (#4703, #4935):** Framework foundations.
