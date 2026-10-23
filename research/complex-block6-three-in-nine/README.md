# Exact 3-Array 9-Call Block-6 Unit Schedule on $\mathbb{C}^{64}$ ($\kappa = 0.3869 = 38.69\%$)

**First verified complex multiplication unit breaking the $\kappa > 0.35$ milestone ($\kappa = 38.69\%$, saving 9 calls out of 18 on 3 arrays, a 50.0% reduction in paid calls).**

## 1. Executive Summary & The $\kappa = 38.69\%$ Breakthrough

In PR #4628, Jacob Alan Sussman established the kept-subspace lower bound theorem for small complex units across block sizes $m$:
- **Block $m=2$:** $s \ge 2W \implies \kappa = 0$ (never saves).
- **Block $m=3$ (PR #4813):** $s \ge \frac{14}{5} W \implies \kappa \le 0.0628$ ($6.28\%$, 5-in-14 schedule).
- **Block $m=4$ (PR #4818 & PR #4819):** $s \ge \frac{41}{13} W \implies \kappa \le 0.1714$ ($17.14\%$, 3-in-10 and 13-in-41 schedules).
- **Block $m=5$ (PR #4826):** $s \ge 2.99172 W \implies \kappa = 0.3174$ ($31.74\%$, 3-in-9 schedule).
- **Block $m=6$ (This Package):**
  - Sussman's lower bound: $s / W \ge 2.97290$.
  - Sussman explicitly observed: `"3 in 9 at m = 6 (3 in 9 is not excluded by any bound I know)."`.
  - For $W=3$ arrays: $s / W = 9 / 3 = 3.000 > 2.97290$ ($+0.0271$ surplus margin per array, fully allowed!).

This package constructs, certifies, and verifies over $\mathbb{Q}(i)$ the **3-array 9-call block-6 unit schedule** on $V = \mathbb{C}^{64}$, establishing:
- **Asymptotic Exponent Saving:**
  $$\kappa = 1 - \frac{\ln(9/3)}{\ln 6} = 1 - \frac{\ln 3}{\ln 6} \approx \mathbf{0.38685 \quad (38.69\% > 35.0\%)}.$$
- **50% Call Reduction:** Naive cost is $3 \times 6 = 18$ calls. Schedule cost is 9 calls, saving **9 paid calls (exactly 50.0% reduction)**.
- **Exact Full Injective Column Rank:** **192 / 192** on the $(\mathbb{C}^{64})^3$ state space ($384 \times 192$ observation matrix over $\mathbb{Q}(i)$).
- **Strictly Contractive Loop Gain:** $\|\mathcal{L}_3\| \le (1/2)^3 = 1/8 = 0.125 \ll 1$, giving condition number $\kappa(M_{\text{cascade}}) \le 9/7 \approx 1.2857 \le 16$.
- **Exact Target Recovery:** Zero reconstruction error across all canonical basis vectors, Gaussian rational inputs, and swap-sector configurations.

---

## 2. Block-6 Primitives & Invariants on $V = \mathbb{C}^{64}$

1. **Address Space & Canonical Target:**
   - 6-bit address space $x \in \{0, \dots, 63\}$.
   - Clifford letters $C_j = \frac{1+i}{2} I + \frac{1-i}{2} X_j$ for $j \in \{0, 1, 2, 3, 4, 5\}$.
   - Target operator: $K = C_5 C_4 C_3 C_2 C_1 C_0$ ($64 \times 64$ unitary matrix).
2. **Coordinate Swap Involution $T = \text{SWAP}(0, 5)$:**
   Exchanges qubit 0 and qubit 5:
   $$T^2 = I, \quad T C_0 T = C_5, \quad T C_5 T = C_0.$$
3. **Phase & Permutation Generators:**
   - $S e_x = i^{\text{popcount}(x)} e_x$.
   - $U = \text{CNOT}(0 \to 5)$, $V_{01} = \text{SWAP}(0, 1)$.
   - $P = S U S$, $Q = S V_{01} S = Z_{\text{all}} V_{01}$.
   - Order-4 ratio $R = P^{-1} Q$ with uniform all-width polynomial inverse:
     $$(I + 2R)(I - 2R + 4R^2 - 8R^3) = -15 I.$$

---

## 3. Exact Block-6 Residual Identity ($J F = M C_5 C_4 C_3 C_2 + 2 K$)

With $F = C_0 (P + 2 Q) C_0$ and the four-call operator $J = C_5 C_4 C_3 C_2 \mathcal{N}$:
1. **$Q$-Branch:** $J (C_0 Q C_0) = K = C_5 C_4 C_3 C_2 C_1 C_0$.
2. **$P$-Branch:** $J (C_0 P C_0) = M C_5 C_4 C_3 C_2$.
3. **Combined Identity:**
   $$J F = M C_5 C_4 C_3 C_2 + 2 K \implies K = \frac{1}{2}(J F - M C_5 C_4 C_3 C_2).$$

---

## 4. 3-Port Cascade Architecture on $(\mathbb{C}^{64})^3$

- State dimension: $3 \times 64 = 192$ variables over $\mathbb{Q}(i)$.
- **Port 1 (3 calls on $x_1, x_2$):** $v_1 = K x_1 + E_1 x_2, \quad t_1 = C_0 x_1$
- **Port 2 (3 calls on $x_2, x_3$):** $v_2 = K x_2 + E_2 x_3, \quad t_2 = C_0 x_2$
- **Port 3 (3 calls on $x_3, x_1$):** $v_3 = K x_3 + E_3 x_1, \quad t_3 = C_0 x_3$
- **Total Paid Calls:** $3 \times 3 = \mathbf{9\text{ calls}}$ (saving 9 calls over naive $3 \times 6 = 18$).

---

## 5. Verification & Replay

```bash
# Verify the package via research_package.py runner:
python3.12 -B scripts/research_package.py --package research/complex-block6-three-in-nine

# Direct execution:
python3.12 -B research/complex-block6-three-in-nine/verify.py
```

Expected output:
```
PASS_BLOCK6_THREE_IN_NINE_PORTS
PASS_BLOCK6_3IN9_CASCADE_SCHEDULE
PASS_COMPLEX_BLOCK6_THREE_IN_NINE
```

---

## Open next questions

1. Can the 3-in-9 shape be realized on Block $m=7$ ($V = \mathbb{C}^{128}$) to reach $\kappa = 1 - \ln(3)/\ln(7) \approx 43.55\%$?
2. Can the 2-in-8 shape on Block $m=6$ ($\kappa = 22.63\%$) be characterized inside the same Clifford framework?

---

## Sources, Attributions & Predecessors

- **Jacob Alan Sussman (PR #4628):** Small complex unit lower-bound theorem ($s \ge 2.97290 W$ at $m=6$, noting that 3-in-9 at $m=6$ is unexcluded).
- **Yiyang / @Lyy-iiis (PR #4710):** Phase-repaired prefix and order-4 ratio inverse.
- **lee-phys (PR #4688):** Two-image hook cut prefix and rank engine.
