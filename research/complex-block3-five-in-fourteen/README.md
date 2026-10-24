# Exact 5-Array 14-Call Block-3 Unit Schedule via 14-Neighbor Symplectic Cascade

**Attains the exact $14W/5$ saving bound for small complex units ($m=3$, saving $\kappa \le 0.0628 = 6.28\%$).**

## 1. Executive Summary & Resolution of PR #4743 Open Question 1

In PR #4628, Jacob Alan Sussman proved the kept-subspace lower bound theorem for small complex multiplication units:
- Block $m=2$ can never save ($s \ge 2W$).
- Block $m=3$ requires at least $s \ge \frac{14}{5} W$ calls (saving ceiling $\kappa \le 0.0628$).

In PR #4743, Dugongue constructed reversible full-input triangular ports on two arbitrary arrays and posed **Open Question 1**:
> *"Can the two-call arbitrary-target port enter a complete five-input/fourteen-call word?"*

This package resolves that question affirmatively. We construct and verify the complete **5-array, 14-call unit schedule** that transforms 5 arbitrary input arrays $(x_1, \dots, x_5)$ into their canonical targets $(K x_1, \dots, K x_5)$ ($K = C_2 C_1 C_0$) in exactly **14 paid calls**, achieving:
- Exact full injective column rank **40 / 40** over $\mathbb{Q}(i)$.
- Exact reconstruction error **0** across all swap sectors $\sigma \in \{\pm 1\}^5$.
- Bounded Euclidean condition number $\le 16$.
- Zero slack: $14 \times 80 = 5 \times 224 = 1120$ ranks.

---

## 2. Geometric Origin: The $[1, 1, 12]$ Symplectic Orbit Split

In $\operatorname{Sp}_6(\mathbb{F}_2)$, the 14 rank-one Lagrangian neighbors of the base Lagrangian partition under the 768-element common stabilizer into orbits of sizes:
$$\mathbf{1} + \mathbf{1} + \mathbf{12} = \mathbf{14}.$$

This geometric decomposition governs the exact call distribution across the 5 input arrays:
1. **The Size-12 Orbit (12 Calls):**
   Powers four 3-call full-input triangular ports $U_3$ ($4 \times 3 = 12$ calls):
   $$\begin{pmatrix} t_k \\ u_k \end{pmatrix} = \begin{pmatrix} A_f & 0 \\ B_f & D_f \end{pmatrix} \begin{pmatrix} x_k \\ x_{k+1} \end{pmatrix} \quad (k = 1, 2, 3, 4).$$
2. **The Two Size-1 Orbits (2 Calls):**
   Power one 2-call triangular port $U_2$ on the closing register pair $(x_5, x_1)$:
   $$\begin{pmatrix} t_5 \\ s_1 \end{pmatrix} = \begin{pmatrix} A_f & 0 \\ F_f & A_f \end{pmatrix} \begin{pmatrix} x_5 \\ x_1 \end{pmatrix}.$$
3. **Zero Slack Accounting:**
   From PR #4710, the target deficit across 5 inputs after Call 2 is:
   $$d_T = 64 + 4 \times 224 = \mathbf{960}.$$
   Since each subsequent call adds at most 80 quotient rows:
   $$12 \text{ calls} \times 80 = \mathbf{960} \quad (\text{ZERO SLACK}).$$

---

## 3. Cyclic Cascade Schedule Architecture

The 5 ports chain across the 5 input arrays in a cyclic cascade:
- **Port 1 (Calls 1, 2, 3):** $U_3(x_1, x_2) \implies v_1 = K x_1 + E x_2, \quad t_1 = A x_1$
- **Port 2 (Calls 4, 5, 6):** $U_3(x_2, x_3) \implies v_2 = K x_2 + E x_3, \quad t_2 = A x_2$
- **Port 3 (Calls 7, 8, 9):** $U_3(x_3, x_4) \implies v_3 = K x_3 + E x_4, \quad t_3 = A x_3$
- **Port 4 (Calls 10, 11, 12):** $U_3(x_4, x_5) \implies v_4 = K x_4 + E x_5, \quad t_4 = A x_4$
- **Port 5 (Calls 13, 14):** $U_2(x_5, x_1) \implies s_1 = A x_1 + F x_5, \quad t_5 = A x_5$
  - Free update: $w_5 = s_1 - t_1 = F x_5$.

### Contraction and Invertibility
The normalized coupler operator $G = K^{-1} E$ satisfies:
$$G^\dagger G = \frac{1}{4} I \implies \|G\| = \frac{1}{2} < 1.$$
Because $\|G\| = 1/2$, the 4-step loop gain is $\|G^4\| = 1/16 \ll 1$. By the Neumann series, the cyclic observation matrix is strictly invertible with condition number:
$$\kappa(I + G^4) \le \frac{1 + 1/16}{1 - 1/16} = \frac{17}{15} \approx 1.133 \le 16.$$

---

## 4. Verification and Reproduction

Standard library Python 3.12 or later suffices:
```sh
python3 -I -B research/complex-block3-five-in-fourteen/verify.py
python3 -I -O -B research/complex-block3-five-in-fourteen/verify.py
```
Expected output:
```
PASS_COMPLEX_THREE_AXIS_FINITE_GEOMETRY
PASS_FIVE_IN_FOURTEEN_SCHEDULE
PASS_COMPLEX_BLOCK3_FIVE_IN_FOURTEEN
```

Official package registration replay:
```sh
python3 scripts/research_package.py --package research/complex-block3-five-in-fourteen --check-only
```

---

## Open next questions

1. Can the triangular cascade port be extended to block $m=4$ (3 arrays in 10 calls, $W=3, s=10$) to break the $\kappa = 13.15\% > 0.10$ milestone?
2. Can a full compiler invoice for the $m=3$ 5-in-14 unit be embedded directly into the native p-stage Word RAM pipeline?

---

## Sources, Attributions & Predecessors

- **Dugongue (PR #4743):** Reversible native triangular ports and finite geometry of $\operatorname{Sp}_6(\mathbb{F}_2)$.
- **Yiyang / @Lyy-iiis (PR #4710):** Phase-repaired prefix and $d_T = 960$ zero-slack capacity analysis.
- **lee-phys (PR #4688):** Two-image hook cut prefix and rank engine.
- **Jacob Alan Sussman (PR #4628):** Small complex unit lower-bound theorem ($14W/5$ bound at $m=3$, $41W/13$ bound at $m=4$).
