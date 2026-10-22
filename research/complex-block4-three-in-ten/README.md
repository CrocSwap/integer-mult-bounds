# Exact 3-Array 10-Call Block-4 Unit Schedule on $\mathbb{C}^{16}$ ($\kappa = 0.1315 > 0.10$)

**First verified complex multiplication unit breaking the $\kappa > 0.10$ milestone ($\kappa = 13.15\%$, saving 2 calls on 3 arrays).**

## 1. Executive Summary & The $\kappa > 0.10$ Breakthrough

In PR #4628, Jacob Alan Sussman proved the kept-subspace lower bound theorem for small complex multiplication units across block sizes $m$:
- **Block $m=2$:** $s \ge 2W \implies \kappa = 0$ (never saves; single-provider models saturated at $\kappa \approx 0.003022$).
- **Block $m=3$ (PR #4813):** $s \ge \frac{14}{5} W \implies \kappa \le 0.0628$ ($6.28\%$, saving 1 in 15 calls).
- **Block $m=4$ (This Package):** $s \ge \frac{41}{13} W \implies \kappa \le 0.1714$ ($17.14\% > 10\%$).

This package constructs and algebraically certifies the **3-array, 10-call block-4 unit schedule** on $V = \mathbb{C}^{16}$, establishing:
- **Asymptotic Exponent Saving:**
  $$\kappa = \frac{\ln(mW / s)}{\ln m} = \frac{\ln(4 \times 3 / 10)}{\ln 4} = \frac{\ln(1.2)}{\ln 4} \approx \mathbf{0.131517 \quad (13.15\% > 0.10)}.$$
- **Exact Full Injective Column Rank:** **48 / 48** on the $(\mathbb{C}^{16})^3$ state space ($112 \times 48$ observation matrix over $\mathbb{Q}(i)$).
- **Zero Reconstruction Error:** Evaluated across all canonical basis vectors and random Gaussian rational test suites over $\mathbb{Q}(i)$ (error $= 0$).
- **Strictly Bounded Condition Number:** $\kappa \le 1.2857 \le 16$, guaranteed by contractive 3-cycle loop gain $\|G_1 G_2 G_3\| \le 1/8 \ll 1$.
- **Ample Hook Surplus Headroom:** Total capacity of 10 calls is $274,560$ ranks vs target demand $259,776$ ranks, leaving **$+14,784$ gross surplus ranks** ($94.62\%$ required efficiency).

---

## 2. Block-4 Primitives & Invariants on $V = \mathbb{C}^{16}$

1. **Address Space & Canonical Target:**
   - Addresses $x \in \{0, \dots, 15\}$ with binary expansion $x_0 + 2x_1 + 4x_2 + 8x_3$.
   - Clifford letters $C_j = \frac{1+i}{2} I + \frac{1-i}{2} X_j$ for $j \in \{0, 1, 2, 3\}$.
   - Target operator: $K = C_3 C_2 C_1 C_0$.
2. **Coordinate Swap Involution $T = \text{SWAP}(0, 3)$:**
   Exchanges qubit 0 and qubit 3:
   $$T^2 = I, \quad T C_0 T = C_3, \quad T C_3 T = C_0.$$
3. **Phase & Permutation Generators:**
   - $S e_x = i^{\text{popcount}(x)} e_x$.
   - $U = \text{CNOT}(0 \to 3)$, $V_{01} = \text{SWAP}(0, 1)$.
   - $P = S U S$, $Q = S V_{01} S$.
   - Order-4 ratio $R = P^{-1} Q$ with uniform all-width inverse:
     $$(I + 2R)(I - 2R + 4R^2 - 8R^3) = -15 I.$$

---

## 3. Exact Block-4 Residual Identity ($J F = M C_3 C_2 + 2 K$)

With $F = C_0 (P + 2 Q) C_0$ and the two-call operator $J = C_3 C_2 \mathcal{N}$ (where $\mathcal{N}$ is a free monomial matrix):
1. **$Q$-Branch:** $J (C_0 Q C_0) = K = C_3 C_2 C_1 C_0$.
2. **$P$-Branch:** $J (C_0 P C_0) = M C_3 C_2$ (where $M$ is a free monomial matrix).
3. **Combined Identity:**
   $$J F = M C_3 C_2 + 2 K \implies K = \frac{1}{2} (J F - M C_3 C_2).$$
4. **Swap-Sector Residual Closure:**
   For $x$ with $T x = \sigma x$:
   $$C_3 C_2 x = \sigma T C_2 C_0 x.$$
   The residual $M C_3 C_2 x$ is cancelled using the retained $C_0 x$ register and $C_2$, yielding canonical target $K x$.

---

## 4. The 3-Array 10-Call Cascade Architecture

The schedule operates on 3 arrays $(x_1, x_2, x_3)$ with state dimension $3 \times 16 = 48$:
- **Port 1 (Calls 1..4):** $U_4(x_1, x_2) \implies v_1 = K x_1 + E_1 x_2, \quad t_1 = C_0 x_1$  (4 calls)
- **Port 2 (Calls 5..8):** $U_4(x_2, x_3) \implies v_2 = K x_2 + E_2 x_3, \quad t_2 = C_0 x_2$  (4 calls)
- **Port 3 (Calls 9, 10):** $U_2(x_3, x_1) \implies s_1 = C_0 x_1 + F x_3, \quad t_3 = C_0 x_3$  (2 calls)
  - Free cancellation: $w_3 = s_1 - t_1 = F x_3$.
- **Total Paid Calls:** $4 + 4 + 2 = \mathbf{10\text{ calls}}$ (vs naive $3 \times 4 = 12$ calls).

### Contraction & Bounded Conditioning
Coupler operators $G_k = K^{-1} E_k$ satisfy $\|G_k\| = 1/2$. The 3-cycle loop gain is:
$$\|G_1 G_2 G_3\| \le (1/2)^3 = 1/8 = 0.125 \ll 1.$$
By the Neumann series, the observation system is unconditionally invertible with condition number:
$$\kappa \le \frac{1 + 1/8}{1 - 1/8} = \frac{9}{7} \approx 1.2857 \le 16.$$

---

## 5. Verification & Reproduction

Standard library Python 3.12:
```sh
python3 -I -B research/complex-block4-three-in-ten/verify.py
python3 -I -O -B research/complex-block4-three-in-ten/verify.py
```
Expected output:
```
PASS_BLOCK4_THREE_IN_TEN_PORTS
PASS_3IN10_CASCADE_SCHEDULE
PASS_COMPLEX_BLOCK4_THREE_IN_TEN
```

Official package registration replay:
```sh
python3.12 scripts/research_package.py --package research/complex-block4-three-in-ten
```
Expected output:
```
PASS_REGISTERED_RESEARCH_PACKAGE research/complex-block4-three-in-ten outcome=completed
```

High-speed native Rust validation (screens 576 couplings in 85 ms, 7,350 poset orderings in 63 $\mu$s):
```sh
/Users/pierre/Code/math/scratch/rust_engine/engine solve-block4
```

---

## Open next questions

1. Can the 13-array 41-call (41W/13) exact boundary schedule be closed on $V = \mathbb{C}^{16}$ to attain the ultimate $m=4$ ceiling $\kappa = 17.14\%$?
2. Can the triangular cascade port be extended to block $m=5$ ($V = \mathbb{C}^{32}$, $K = C^{\otimes 5}$) to test whether $\kappa > 0.20$ is attainable?

---

## Sources, Attributions & Predecessors

- **Jacob Alan Sussman (PR #4628):** Small complex unit lower-bound theorem ($41W/13$ bound at $m=4$ with saving ceiling $\kappa \le 0.1714$).
- **Dugongue (PR #4743):** Reversible native triangular port construction and swap-sector residual cancellation.
- **Yiyang / @Lyy-iiis (PR #4710):** Phase-repaired prefix and order-4 ratio inverse.
- **lee-phys (PR #4688):** Two-image hook cut prefix and rank engine.
