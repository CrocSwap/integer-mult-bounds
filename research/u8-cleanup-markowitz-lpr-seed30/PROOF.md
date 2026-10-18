# Mathematical Proofs: Two-Sided Markowitz $R^{-1} P L^{-1}$ Cleanup Refactorization and Partial-$E_4$ Climb-Splitting Lemma

**Package:** `research/u8-cleanup-markowitz-lpr-seed30`  
**Base Commit:** `abdc6a7002abdbcd9e21bfc5e1a795784deacfdf`  
**Assignment Seed:** `30` (Track `20–39: Complex supplier`)  
**Status:** Finite circuit construction and scoped negative result (`no new kappa`)

---

## 1. Setting and Problem Statement

In the selected U8 complex supplier word (`native/barch/FULL-WORD.json.gz`, content SHA-256 `090fd574747fbf9628e70cb9beb792732914cfa52e1df147579fe4dbccc68c5a`; canonical word `native/local/CANONICAL-WORD.json.gz`, content SHA-256 `24db880b7dab31e6af4eec8a1aba1bbbae29cd50d9a7b77cf0e9b571b3e5ae7c`), the register space has dimension $n = 2v + R = 2(112) + 504 = 728$:

- **Data registers:** $D = \{0, \dots, 111\}$ ($v = 112$),
- **Target registers:** $T = \{112, \dots, 223\}$ ($v = 112$),
- **Helper registers:** $H = \{224, \dots, 727\}$ ($R = 504$), partitioned at the end of section `B` + `cleanup_tail` into $126$ hyperplane-ended helpers $H_{\text{hpe}}$ (whose terminal frame in `canonical['final']` is a proper subspace $U \subsetneq \text{FULL}$) and $378$ `FULL`-ended helpers $H_{\text{full}}$.

After the prefix
$$\mathcal{W}_{\text{prefix}} = \text{precondition} + \text{compensation} + A + \text{cut} + B + \text{tail}$$
has executed, every register in $T \cup H_{\text{hpe}}$ has already reached its exact endpoint state, while the remaining $m = |D \cup H_{\text{full}}| = 112 + 378 = 490$ registers sit at frame `1` (`FULL`) in an invertible dyadic linear state $M_{\text{after}} \in GL_{728}(\mathbb{Z}[1/2])$ supported on $S = D \cup H_{\text{full}}$. The `full_frame_cleanup` section (`canonical['cleanup']`) must implement the exact inverse linear transformation
$$M_0 = M_{\text{after}}^{-1} \in GL_{728}(\mathbb{Z}[1/2]),$$
which acts as the identity on $\overline{S} = T \cup H_{\text{hpe}}$ and maps $M_{\text{after}}$ back to the identity on $S$ (leaving the compensated target accumulations $y_t \leftarrow y_t + x_t$ untouched on $T$).

### Why the Baseline U8 `cleanup` Has Coefficient Blowup

In `cold44x.py` (`high_inverse = "dyadic_sparse_Gauss_Jordan"`), the baseline U8 `cleanup` was synthesized by running **one-sided (row-only) Gauss-Jordan elimination** on $M_{\text{after}}$ (which has $9,430$ off-diagonal nonzeros) in the fixed register order $c = 0, 1, \dots, 727$. Because no column operations or sparsity-preserving pivot orderings were used:

1. Eliminating dense columns early caused severe fill-in across the remaining active submatrix, requiring **$6,105$ scalar macros** ($6,005$ `add` and $100$ `scale`) and **$68,714$ real-component primitives per orientation**.
2. Repeated row additions compounded odd numerators up to **$\max |\text{num}| = 131,646$** and denominators up to **$\max \text{den} = 64$**.
3. By contrast, inspecting $M_0 = M_{\text{after}}^{-1}$ directly reveals that $M_0$ has **only $2,844$ off-diagonal nonzeros**, and **every single entry of $M_0$ has numerator in $\{0, \pm 1, \pm 2, \pm 3, \pm 4\}$ and denominator in $\{1, 2, 4\}$**!

---

## 2. Two-Sided Markowitz $R^{-1} P L^{-1}$ Schur-Complement Factorization

Let $E_{\text{add}}(d, s, q) = I + q e_d e_s^T$ ($d \ne s$, $q \in \mathbb{Z}[1/2]$) and $E_{\text{scale}}(d, q) = I + (q - 1) e_d e_d^T$ ($q = \pm 2^k$, $k \in \mathbb{Z}$) denote the elementary row matrices corresponding to `["add", d, s, num, den, 1]` and `["scale", d, num, den, 1]`. Under `hpe_audit_and_transport.py` and `hpe_emit_local.py`, a gate list $W = [g_1, g_2, \dots, g_N]$ acts sequentially from left to right on the row-state matrix $X$ via $X \mapsto E(g_N) \cdots E(g_2) E(g_1) X$, so the linear operator implemented by $W$ is the ordered matrix product
$$\operatorname{Mat}(W) = E(g_N) \cdots E(g_2) E(g_1).$$

### Proposition 1 (Zero-Fill-In Right Column Clearing and $R^{-1} P L^{-1}$ Exactness)

Let $M^{(0)} = M_0 \in GL_n(\mathbb{Z}[1/2])$ be trivial outside the active index set $S$ ($|S| = m$). Suppose for steps $t = 1, \dots, m$ we choose a pivot pair $(r_t, c_t) \in S_r^{(t-1)} \times S_c^{(t-1)}$ such that the pivot entry
$$p_t = M^{(t-1)}[r_t, c_t] = \sigma_t 2^{e_t}, \qquad \sigma_t \in \{+1, -1\},\; e_t \in \mathbb{Z},$$
is a unit in $\mathbb{Z}[1/2]$. At step $t$:

1. **Left column-clearing product $L_t$:** For each $i \in S_r^{(t-1)} \setminus \{r_t\}$ with $M^{(t-1)}[i, c_t] \ne 0$, apply the left row operation adding $(-M^{(t-1)}[i, c_t] / p_t) \cdot \text{row}_{r_t}$ to $\text{row}_i$. Then in $\widetilde{M}^{(t)} = L_t M^{(t-1)}$:
   - Column $c_t$ has a single nonzero entry $\widetilde{M}^{(t)}[r_t, c_t] = p_t$, i.e., $\widetilde{M}^{(t)}[\cdot, c_t] = p_t e_{r_t}$.
   - Row $r_t$ is unchanged: $\widetilde{M}^{(t)}[r_t, \cdot] = M^{(t-1)}[r_t, \cdot]$.
   - On $(S_r^{(t-1)} \setminus \{r_t\}) \times (S_c^{(t-1)} \setminus \{c_t\})$, the active submatrix updates by the rank-1 Schur complement
     $$\widetilde{M}^{(t)}[i, j] = M^{(t-1)}[i, j] - \frac{M^{(t-1)}[i, c_t]\, M^{(t-1)}[r_t, j]}{p_t}.$$

2. **Right row-clearing product $R_t$ (zero fill-in):** For each $j \in S_c^{(t-1)} \setminus \{c_t\}$ with $M^{(t-1)}[r_t, j] \ne 0$, right-multiply $\widetilde{M}^{(t)}$ by $E_{\text{add}}(c_t, j, -M^{(t-1)}[r_t, j] / p_t)$ (which adds $(-M^{(t-1)}[r_t, j] / p_t) \cdot \text{col}_{c_t}$ to $\text{col}_j$). Because $\widetilde{M}^{(t)}[\cdot, c_t] = p_t e_{r_t}$ is already zero in every row $i \ne r_t$, this right column operation:
   - Zeros out $\widetilde{M}^{(t)}[r_t, j]$ for all $j \ne c_t$, leaving $M^{(t)} = L_t M^{(t-1)} R_t$ with $M^{(t)}[r_t, \cdot] = p_t e_{c_t}^T$ and $M^{(t)}[\cdot, c_t] = p_t e_{r_t}$, and
   - Causes **strictly zero fill-in** on all rows $i \ne r_t$: $M^{(t)}[i, j] = \widetilde{M}^{(t)}[i, j]$ for all $i \ne r_t$.

3. **Binary scale placement for $|p_t| = 2^{e_t} \ne 1$:** To reduce the decoupled pivot entry $p_t = \sigma_t 2^{e_t}$ to $\sigma_t \in \{+1, -1\}$, a single binary scale gate $E_{\text{scale}}(\cdot, 2^{-e_t})$ may be placed at any of three algebraically equivalent positions without altering the Schur complement $M^{(t)}[i, j]$ ($i \ne r_t, j \ne c_t$):
   - **(Option A — Pre-$L_t$ row scale):** Apply $E_{\text{scale}}(r_t, 2^{-e_t})$ on the left *before* $L_t$; then $L_t$ uses multipliers $-M^{(t-1)}[i, c_t] / \sigma_t$ and $R_t$ uses $-M^{(t-1)}[r_t, j] / p_t$.
   - **(Option B — Pre-$R_t$ column scale):** Apply $E_{\text{scale}}(c_t, 2^{-e_t})$ on the right *between* $L_t$ and $R_t$; then $L_t$ uses $-M^{(t-1)}[i, c_t] / p_t$ and $R_t$ uses $-M^{(t-1)}[r_t, j] / \sigma_t$.
   - **(Option C — Post-elimination unit-row scale):** Apply $E_{\text{scale}}(r_t, 2^{-e_t})$ on the left *after* all $L_t, R_t$ (when row $r_t$ has only the single entry $p_t$ at column $c_t$); then both $L_t$ and $R_t$ use unscaled multipliers $-M^{(t-1)}[i, c_t] / p_t$ and $-M^{(t-1)}[r_t, j] / p_t$.

4. **Global factorization and execution order:** After $m$ steps, let $L = L_{\text{post}} L_m \cdots L_1 = E(\ell_a) \cdots E(\ell_1)$ and $R = R_1 \cdots R_m = E(\rho_1) \cdots E(\rho_b)$. Then
   $$L M_0 R = P \implies M_0 = L^{-1} P R^{-1} = E(\ell_1)^{-1} \cdots E(\ell_a)^{-1} \, P \, E(\rho_b)^{-1} \cdots E(\rho_1)^{-1},$$
   where $P$ is the signed permutation matrix with $P[r_t, c_t] = \sigma_t \in \{+1, -1\}$ for $t = 1, \dots, m$ and $P[i, i] = 1$ for $i \notin S$. Therefore, the gate list
   $$W_{\text{cleanup}} = \big[\rho_1^{-1}, \dots, \rho_b^{-1}\big] + W_P + \big[\ell_a^{-1}, \dots, \ell_1^{-1}\big]$$
   satisfies $\operatorname{Mat}(W_{\text{cleanup}}) = L^{-1} P R^{-1} = M_0$ exactly. $\square$

---

## 3. Weyl-Group Signed Cycle Decomposition of $P$

### Proposition 2 (Scale-Free 3-Add Signed Cycle Realization)

Let $P$ be a signed permutation matrix on $S$ defined by $P e_c = s_c e_{\pi(c)}$ with bijection $\pi : S \to S$ and signs $s_c \in \{+1, -1\}$. Decompose $\pi$ into disjoint cycles.

1. For any fixed point $\pi(c) = c$: if $s_c = +1$, no gate is needed; if $s_c = -1$, the single gate `["scale", c, -1, 1, 1]` realizes $e_c \mapsto -e_c$.
2. For any cycle $(c_0, c_1, \dots, c_{k-1})$ of length $k \ge 2$ with $\pi(c_m) = c_{(m+1) \bmod k}$, define on any register pair $(a, b)$ the two 3-add Weyl-group generators of $SL_2(\mathbb{Z})$:
   $$W_+(a, b) = \big[\text{add}(a, b, -1),\; \text{add}(b, a, +1),\; \text{add}(a, b, -1)\big] : (x_a, x_b) \mapsto (-x_b, +x_a),$$
   $$W_-(a, b) = \big[\text{add}(a, b, +1),\; \text{add}(b, a, -1),\; \text{add}(a, b, +1)\big] : (x_a, x_b) \mapsto (+x_b, -x_a).$$
   Execute for $\text{idx} = k - 1, k - 2, \dots, 1$ on $(a, b) = (c_{\text{idx}-1}, c_{\text{idx}})$:
   - Choose $W_+(c_{\text{idx}-1}, c_{\text{idx}})$ if $s_{c_{\text{idx}-1}} = +1$, or $W_-(c_{\text{idx}-1}, c_{\text{idx}})$ if $s_{c_{\text{idx}-1}} = -1$.
   
   **Proof of exactness:** Before step $\text{idx}$, registers $c_0, \dots, c_{\text{idx}-1}$ have not yet been touched and hold their initial values $+1 \cdot x_{c_0}, \dots, +1 \cdot x_{c_{\text{idx}-1}}$, while register $c_{\text{idx}}$ holds $\tau_{\text{idx}} x_{c_{k-1}}$ where $\tau_{k-1} = +1$. Applying $W_{s_{c_{\text{idx}-1}}}(c_{\text{idx}-1}, c_{\text{idx}})$ writes $s_{c_{\text{idx}-1}} x_{c_{\text{idx}-1}}$ into $c_{\text{idx}}$ (which is never touched again in subsequent steps $\text{idx}' < \text{idx}$) and writes $(-s_{c_{\text{idx}-1}} \tau_{\text{idx}}) x_{c_{k-1}}$ into $c_{\text{idx}-1}$. By downward induction to $\text{idx} = 1$, every register $c_1, \dots, c_{k-1}$ receives its exact signed target $s_{c_0} x_{c_0}, \dots, s_{c_{k-2}} x_{c_{k-2}}$ using $3(k-1)$ `add` gates and **zero** `scale` gates, while $c_0$ holds $\tau_0 x_{c_{k-1}}$ with
   $$\tau_0 = \prod_{m=0}^{k-2} (-s_{c_m}) \in \{+1, -1\}.$$
   Appending `["scale", c_0, -1, 1, 1]` if and only if $\tau_0 \ne s_{c_{k-1}}$ realizes the entire signed cycle in $3(k-1)$ `add` gates and at most one `scale` gate. $\square$

---

## 4. Dual Orientation Symmetry and $L_1$ Prefix Reduction

### Proposition 3 (Forward/Backward Primitive Symmetry and $L_1$ Norm Control)

In `hpe_emit_local.py`, each gate $e$ in `cleanup` is emitted as `scalar(e, False)` in the forward program and `scalar(e, True) = dual(e)` in the backward program, where:
- $\operatorname{dual}(\text{add}(d, s, a, b)) = \text{add}(s, d, -a, b)$ has the identical odd numerator $|{-a}| = |a|$ and denominator $b$, hence identical binary Horner `primitive_bound` $3 + (\operatorname{bit\_length}(|a|) - 1) + \operatorname{popcount}(|a|) + (\operatorname{bit\_length}(b) - 1)$.
- Every `scale` gate in $W_{\text{cleanup}}$ has multiplier $q \in \{-1, \pm 2, \pm 4, \pm 8, \pm 1/2, \pm 1/4, \pm 1/8\}$, and $\operatorname{dual}(\text{scale}(d, a, b)) = \text{scale}(d, b, a)$ (or $(-b, |a|)$ for $q < 0$) preserves $|\operatorname{bit\_length}(|a|) - \operatorname{bit\_length}(b)| + \mathbf{1}[q < 0]$.

Consequently, $W_{\text{cleanup}}$ has the **exact same real-component primitive bound ($31,394$) in both forward and backward orientations**, reducing both orientations by **$37,320$ real primitives** ($-54.31\%$ of `cleanup`, or **$-74,640$ real primitives** across the forward+backward invocation pair).

Furthermore, because `hpe_emit_local.py` emits the backward `full_frame_cleanup` by applying `dual(e)` to `c['cleanup']` in forward list order (transposing source and destination of each `add` gate without reversing the list), the baseline one-sided Gauss-Jordan `cleanup` (with multipliers up to $131,646$) compounds row $L_1$ norms in the backward orientation to
$$\text{prefix\_l1\_upper}_{\text{bwd}}(\text{U8}) = \frac{48,299,247,708,521,178,587,951}{16} \approx 3.0187 \times 10^{21} \quad (72 \text{ bits}).$$
Under our two-sided $R^{-1} P L^{-1}$ factorization (`seed = 30`, `trial = 16`), every gate in $W_{\text{cleanup}}$ has $|\text{num}| \le 8$ and $\text{den} \le 8$, reducing the backward peak prefix $L_1$ norm by a factor of **$210,704\times$** to
$$\text{prefix\_l1\_upper}_{\text{bwd}}(\text{LPR}) = \frac{57,316,408,753,392,281}{4} \approx 1.4329 \times 10^{16} \quad (54 \text{ bits}, \; -18 \text{ bits}),$$
and reducing the forward peak prefix $L_1$ norm by **$13.7\times$** from $6,812,058,044,968,180,837 / 256$ ($55$ bits) to $1,938,756,620,440,273$ ($51$ bits, $-4$ bits).

---

## 5. Scoped Negative Result (Candidate 1): Partial-$E_4$ Entrance-Promotion Reversion Climb-Splitting Lemma

### Proposition 4 (Bipartite Delivery Climb Splitting on Partial $E_4 \to E_5$ Reversion)

In U8 (`native/barch/FULL-WORD.json.gz`), the 4-helper group $G = \{659, 661, 662, 663\}$ enters at the 5-dimensional frame $E_5 = [298, 170, 102, 30, 1]$ (`start_extra`), extending $E_4 = [298, 170, 102, 30]$ ($\dim E_4 = 4$). The first gates in `A + B` that read $G$ are the 12 bipartite delivery gates `B[420..431]`, which consist of 3 gates into each destination helper $d \in D_G = \{656, 657, 658, 660\}$ from $G$ at frame $E_5$, followed by the 8 gates `B[710..717]` on $G$ at a 7-dimensional frame $F_7 \supset E_5$.

Immediately before `B[420]`, each destination helper $d \in D_G$ sits at a 1-dimensional frame $F_1(d) \subset E_4 \subset E_5$, and in `B[420..431]` the bipartite subgraph between $D_G$ and $G$ has minimum degree $3$ (every $d \in D_G$ reads $3$ distinct sources in $G$, and every $s \in G$ feeds $3$ distinct destinations in $D_G$).

Suppose $m \in \{1, 2, 3, 4\}$ helpers $G_4 \subseteq G$ ($|G_4| = m$) have their entrance frame reverted from $E_5$ to $E_4$, and their delivery gates in `B[420..431]` lowered from frame $E_5$ to frame $E_4$ (sorted before the remaining $E_5$ gates of `B[420..431]` so frame monotonicity holds):

1. **Full group reversion of `B[420..431]` ($m = 4$):** All 12 gates in `B[420..431]` run at $E_4$. Each $d \in D_G$ climbs $F_1(d) \to E_4$ (rank 3 instead of rank 4, $\Delta = \{3:+4, 4:-4\}$) and later climbs from $E_4$ to its subsequent 6-dimensional frame (rank 2 instead of rank 1, $\Delta = \{1:-4, 2:+4\}$), while each $s \in G$ climbs from $E_4$ instead of $E_5$ to its subsequent 6-dimensional frame ($\Delta = \{1:-4, 2:+4\}$), yielding the net local profile delta
   $$\Delta_{\text{local}}(m = 4) = \{1: -8,\; 2: +8,\; 3: +4,\; 4: -4\}.$$

2. **Partial group reversion ($m \in \{1, 2, 3\}$):** Because every $d \in D_G$ has degree 3 into $G$, for $m \in \{1, 2, 3\}$ at least $3$ destination helpers in $D_G$ read at least one source in $G_4$ (at frame $E_4$) AND at least one source in $G \setminus G_4$ (at frame $E_5$), splitting their single rank-4 climb $1 \to 5$ into a rank-3 climb $1 \to 4$ plus a rank-1 climb $4 \to 5$:
   $$\Delta_{\text{local}}(m = 1) = \{1: +2,\; 2: +1,\; 3: +3,\; 4: -3\},$$
   $$\Delta_{\text{local}}(m = 2) = \{1: +2,\; 2: +2,\; 3: +4,\; 4: -4\},$$
   $$\Delta_{\text{local}}(m = 3) = \{1: -1,\; 2: +4,\; 3: +4,\; 4: -4\}.$$
   In every case $m \in \{1, 2, 3, 4\}$, the split climbs on $D_G$ inject $+3$ or $+4$ extra rank-3 children and $+1$ to $+8$ extra rank-2 children, strictly increasing the complex moment at $b_{\text{front}}$. $\square$
