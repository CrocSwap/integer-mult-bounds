# All-Puncture $E_8$ Star Label-Decoder Exclusion and Exact $p=56$ Dimension-Loss Classification

## Status and Scope

- **Category:** Research note and scoped negative result (structural decoder research, Track 40–49, seed `49`).
- **Headline $\kappa$ impact:** **None.** This package does not modify `certificates/selected-result.json` or claim a new conditional bound on integer multiplication.
- **Predecessors extended:**
  - **PR #631** (Chi Zhao, commit `fb893b5ee1317c2da3b297e6fe78eca0857d1a76`): defined the 120 positive $E_8$ root lines, the 9-dimensional binary reader code $C \subset \mathbb{F}_2^{120}$, the 256 standard parabolic flats, the single-reader puncture thresholds $\delta_d = (56, 55, 53, 50, 44, 36, 26, 1, 0)$, and proved $C_{\text{star}}(P)/(120-|P|) \ge 63/111$ for $|P| \le 35$.
  - **PR #875** (Philipp / `@mightyOil`, commit `7f334e4c749fd83d03feb6c1de4e4cda9534c9dc`, `research/e8-rank5-boundary`): proved that at $|P|=36$, at most one nonzero reader can drop to rational rank $\le 5$ because any two distinct nonzero readers cover at least $84 = 120 - 36$ root lines.
  - **PR #939** (Ross Richardson, commit `3a8ec54d62fb8824c658dc7ed356f99423cac8cf`, merged as `c9b187382b2d370e21e866fa4070a7bfceaf86ad`, `research/e8-joint-reader-bound`): generalized the pairwise capacity bound $M_a + M_b \ge 84 - p$ to prove $C_{\text{star}}(P)/(120-p) \ge 63/111$ for $0 \le p \le 55$, and stopped at $p=55$ because at $p=56$ a minimum-weight codeword $c_0 \in C$ ($\operatorname{wt}(c_0)=56$) can be completely punctured, dropping the live binary label dimension $\dim_{\mathbb{F}_2}(C|_L)$ from $9$ to $8$.

---

## 1. Definitions and Inherited Model

Let $L_0, \dots, L_{119} \subset \mathbb{Q}^8$ denote the $120$ antipodal root lines of $E_8$, represented by positive roots of norm $\langle v, v \rangle = 8$ in doubled coordinates, and let $\alpha_0, \dots, \alpha_7$ be a simple root system of $E_8$. Following PR #631 and PR #939:

1. **Binary decoder $B$ and reader code $C$:** The $9 \times 120$ binary generator matrix $B$ over $\mathbb{F}_2$ has rows $b_0, \dots, b_7$ given by the mod-$2$ root inner products $b_j(i) = (\langle \alpha_j, L_i \rangle / 4) \bmod 2$ ($0 \le j \le 7$) and $b_8 = \mathbf{1}_{120}$. Its row space $C = \operatorname{rowspace}_{\mathbb{F}_2}(B) \subset \mathbb{F}_2^{120}$ has dimension $9$ ($|C|=512$) and weight distribution $0^1\, 56^{255}\, 64^{255}\, 120^1$, and is invariant under the Weyl group $W(E_8)$.
2. **Column functionals:** Each port $i \in \{0, \dots, 119\}$ defines a column evaluation functional $u_i \in C^* \setminus \{0\}$, $u_i(c) = c_i$. The 120 columns $u_0, \dots, u_{119}$ are **120 distinct nonzero elements** of $C^* \cong \mathbb{F}_2^9$, all satisfying $u_i(\mathbf{1}_{120}) = 1$.
3. **Punctured star reader rank:** For a puncture set $P \subset \{0, \dots, 119\}$ of size $p = |P| \in \{0, \dots, 119\}$ with live port set $L = \{0, \dots, 119\} \setminus P$ of size $v = 120 - p \ge 1$, the surviving rational star rank of a reader $c \in C$ is
   $$s_P(c) = \dim_{\mathbb{Q}} \operatorname{span}_{\mathbb{Q}}\{ L_i : i \in \operatorname{supp}(c) \setminus P \} \in \{0, 1, \dots, 8\}.$$
4. **Parabolic flat capacities and single-reader thresholds (PR #631):** Any rational subspace spanned by a subset of $E_8$ root lines of dimension $d \in \{0, \dots, 8\}$ is $W(E_8)$-conjugate to a subspace of a standard parabolic root subsystem of rank $d$, so it contains at most $M_d$ root lines, where
   $$(M_0, M_1, M_2, M_3, M_4, M_5, M_6, M_7, M_8) = (0, 1, 3, 6, 12, 20, 36, 63, 120).$$
   Moreover, if $c \in C \setminus \{0\}$ has $s_P(c) = d$, then $|\operatorname{supp}(c) \cap P| \ge \delta_d$, where
   $$(\delta_0, \delta_1, \delta_2, \delta_3, \delta_4, \delta_5, \delta_6, \delta_7, \delta_8) = (56, 55, 53, 50, 44, 36, 26, 1, 0).$$

---

## 2. Proposition 1 (Live-Quotient Star Cost Equivalence under Dimension Loss)

Let $P \subset \{0, \dots, 119\}$ have size $0 \le p \le 119$ ($v = 120 - p \ge 1$), and let $\pi_L : C \to C|_L \subset \mathbb{F}_2^L$ be the coordinate restriction to the live ports $L = \{0, \dots, 119\} \setminus P$. Define the restriction kernel
$$K_P = \ker(\pi_L) = \{ c \in C : \operatorname{supp}(c) \subseteq P \}, \qquad k_0 = \dim_{\mathbb{F}_2}(K_P) = 9 - \dim_{\mathbb{F}_2}(C|_L).$$

**Proposition 1.**
1. *For every $0 \le p \le 119$, $0 \le k_0 \le 8$ (equivalently $\dim_{\mathbb{F}_2}(C|_L) \ge 1$). More generally, $k_0 \ge k$ is possible if and only if $p \ge U_k$, where $U_k$ is the minimum support union of a $k$-dimensional subspace of $C$.*
2. *For every $c \in C$ and every $z \in K_P$, $\operatorname{supp}(c) \setminus P = \operatorname{supp}(c \oplus z) \setminus P$, so $s_P(c) = s_P(c \oplus z)$ is constant on each coset of $C / K_P \cong C|_L$, and $s_P(z) = 0$ if and only if $z \in K_P$.*
3. *Defining the live-quotient star cost $C_{\text{star}}^{\text{live}}(P)$ as the minimum of $\sum_{j=1}^{9-k_0} s_P(\bar{c}_j)$ over all $\mathbb{F}_2$-bases $(\bar{c}_1, \dots, \bar{c}_{9-k_0})$ of $C|_L$, we have the exact identity*
   $$C_{\text{star}}^{\text{live}}(P) = C_{\text{star}}(P) = \min_{\substack{c_1, \dots, c_9 \text{ basis of } C}} \sum_{i=1}^9 s_P(c_i) = \sum_{d=0}^7 \bigl(9 - r_d(P)\bigr),$$
   *where $r_d(P) = \dim_{\mathbb{F}_2} \operatorname{span}_{\mathbb{F}_2}\{ c \in C : s_P(c) \le d \}$.*

*Proof.*
(1) Since $p \le 119$, at least one port $i \in L$ survives, and its column functional $u_i \in C^* \setminus \{0\}$ is nonzero on $C$ (in fact $u_i(\mathbf{1}_{120}) = 1$), so $K_P \subseteq \ker(u_i)$ has dimension at most $8$. A $k$-dimensional subspace lies in $K_P$ iff the union of its nonzero supports lies in $P$, requiring $p \ge U_k$.

(2) If $z \in K_P$, then $z|_L = 0$, so $(c \oplus z)|_L = c|_L$. Hence $\operatorname{supp}(c \oplus z) \setminus P = \operatorname{supp}(c) \setminus P$, and the rational span of the surviving root lines is identical. Moreover, a set of root lines has rational rank $0$ iff it is empty, so $s_P(z) = 0 \iff \operatorname{supp}(z) \setminus P = \emptyset \iff z \in K_P$.

(3) Any basis $(z_1, \dots, z_{k_0})$ of $K_P$ has $s_P(z_i) = 0$ and extends by preimages $(c_{k_0+1}, \dots, c_9)$ of any basis of $C|_L$ to a basis of $C$ of the same total star cost. Conversely, in the vector matroid of $C$ weighted by the non-negative function $s_P$, the greedy algorithm selects a basis of $K_P$ first (at weight $0$, since $r_0(P) = k_0$) and then selects $9 - k_0$ coset representatives projecting to a minimum-weight basis of $C / K_P \cong C|_L$. Summation by parts over the matroid rank filtration $r_0(P) \le r_1(P) \le \dots \le r_8(P) = 9$ yields $\sum_{i=1}^9 d_i = \sum_{d=0}^7 (9 - r_d(P))$. $\square$

---

## 3. Proposition 2 (Complete Two-Orbit Classification at the $p=56$ Dimension-Loss Boundary)

At $p = 56$ ($v = 64$ live ports), dimension loss $\dim_{\mathbb{F}_2}(C|_L) < 9$ occurs if and only if $P = \operatorname{supp}(c_0)$ for one of the $255$ minimum-weight codewords $c_0 \in C$ of weight $56$. Because the minimum support union of a $2$-dimensional subspace of $C$ is $U_2 = 84 > 56$, every such $P$ has $\dim_{\mathbb{F}_2}(K_P) = 1$ and $\dim_{\mathbb{F}_2}(C|_L) = 8$.

**Proposition 2.** *Under the action of $W(E_8)$ on the 120 root lines, the $255$ weight-$56$ puncture sets $P = \operatorname{supp}(c_0)$ partition into exactly two orbits:*

1. **Orbit 1 ($135$ even-frame codewords in $\mathbf{1}_{120} \oplus C_{\text{lin}}$):**
   - *Across all $511$ nonzero readers $c \in C \setminus \{0\}$, the surviving rational rank histogram is*
     $$\#\{c \in C \setminus \{0\} : s_P(c) = d\} = \begin{cases} 1 & d = 0 \;\; (c = c_0), \\ 112 & d = 7, \\ 398 & d = 8, \\ 0 & \text{otherwise.} \end{cases}$$
   - *The cumulative $\mathbb{F}_2$-dimensions are $(r_0, \dots, r_8) = (1, 1, 1, 1, 1, 1, 1, 8, 9)$: the $113$ readers of rank $\le 7$ span an $8$-dimensional hyperplane of $C$.*
   - *The optimal $9$-reader basis weights are $(0, 7, 7, 7, 7, 7, 7, 7, 8)$ (live-quotient basis $(7, 7, 7, 7, 7, 7, 7, 8)$), giving exact star cost*
     $$C_{\text{star}}(P) = C_{\text{star}}^{\text{live}}(P) = 57, \qquad \frac{57}{64} = 0.890625 > \frac{63}{111} \approx 0.567568.$$
   - *Restoring any single punctured port $x \in P$ ($56$ choices, leaving $p = 55$) restores $\dim_{\mathbb{F}_2}(C|_L) = 9$ and yields exact star cost $58$.*

2. **Orbit 2 ($120$ root-nonorthogonality supports $S_a = \{i : |\langle L_i, L_a \rangle| = 4\}$ in $C_{\text{lin}}$):**
   - *The $64$ surviving live ports are $\{a\} \cup \{i : \langle L_i, L_a \rangle = 0\}$, consisting of root line $L_a$ together with the $63$ root lines of the orthogonal $E_7$ subsystem $a^\perp$.*
   - *Across all $511$ nonzero readers $c \in C \setminus \{0\}$, the surviving rational rank histogram is*
     $$\#\{c \in C \setminus \{0\} : s_P(c) = d\} = \begin{cases} 1 & d = 0 \;\; (c = S_a), \\ 56 & d = 6, \\ 198 & d = 7, \\ 256 & d = 8, \\ 0 & \text{otherwise.} \end{cases}$$
   - *Every codeword $c \in C$ with $c_a = 0$ ($256$ words, forming a hyperplane of $C$) has live support contained inside $a^\perp \cong E_7$ (hence $s_P(c) \le 7$), and the $56$ words of rank $6$ already span that entire $8$-dimensional hyperplane $c_a = 0$. Conversely, all $256$ words with $c_a = 1$ have $s_P(c) = 8$. Thus $(r_0, \dots, r_8) = (1, 1, 1, 1, 1, 1, 8, 8, 9)$.*
   - *The optimal $9$-reader basis weights are $(0, 6, 6, 6, 6, 6, 6, 6, 8)$ (live-quotient basis $(6, 6, 6, 6, 6, 6, 6, 8)$), giving exact star cost*
     $$C_{\text{star}}(P) = C_{\text{star}}^{\text{live}}(P) = 50, \qquad \frac{50}{64} = \frac{25}{32} = 0.78125 > \frac{63}{111} \approx 0.567568.$$
   - *Restoring any single punctured port $x \in S_a$ ($56$ choices, leaving $p = 55$) restores $\dim_{\mathbb{F}_2}(C|_L) = 9$ and yields exact star cost $51$.*

---

## 4. Proposition 3 (Sharp Subspace Support-Union Hierarchy for $k = 1, \dots, 9$)

For $k \in \{1, \dots, 9\}$, define the minimum support union over $k$-dimensional $\mathbb{F}_2$-subspaces of $C$:
$$U_k = \min_{\substack{W \subseteq C \\ \dim_{\mathbb{F}_2}(W) = k}} \left| \bigcup_{w \in W \setminus \{0\}} \operatorname{supp}(w) \right|.$$

**Proposition 3.** *The numbers $U_1, \dots, U_9$ are given sharply by*
$$(U_1, U_2, U_3, U_4, U_5, U_6, U_7, U_8, U_9) = (56, 84, 100, 108, 112, 116, 118, 119, 120),$$
*and there exists a single nested full flag $0 \subset W_1 \subset W_2 \subset \dots \subset W_9 = C$ that simultaneously attains $\left|\bigcup_{w \in W_k \setminus \{0\}} \operatorname{supp}(w)\right| = U_k$ for every $k = 1, \dots, 9$.*

*Proof.*
For any $k$-dimensional subspace $W \subseteq C$, a port $i \in \{0, \dots, 119\}$ belongs to $\bigcup_{w \in W \setminus \{0\}} \operatorname{supp}(w)$ if and only if the restriction of the column functional $u_i \in C^*$ to $W$ is nonzero. When $u_i|_W \ne 0$, exactly $2^{k-1}$ elements of $W$ evaluate to $1$ at port $i$, yielding the fundamental first-moment identity
$$\left| \bigcup_{w \in W \setminus \{0\}} \operatorname{supp}(w) \right| = \frac{1}{2^{k-1}} \sum_{w \in W \setminus \{0\}} \operatorname{wt}(w). \tag{1}$$

- **Case $k = 1, 2$:** Since every nonzero codeword $w \in C \setminus \{0\}$ has $\operatorname{wt}(w) \ge 56$, (1) gives $U_1 \ge 56$ and $U_2 \ge \lceil 3 \times 56 / 2 \rceil = 84$.
- **Case $k = 3$:** By the exhaustive 5-orbit $W(E_8)$ census of all $\begin{bmatrix} 9 \\ 3 \end{bmatrix}_2 = 788{,}035$ three-dimensional subspaces of $C$ (verified via the $511 \times 10{,}795 = 5{,}516{,}245$ pointed pairs $(a, W_3)$ across the 5 orbit representatives of $C \setminus \{0\}$), no 3-dimensional subspace of $C$ consists solely of seven weight-$56$ codewords: every 3-dimensional subspace contains at least one codeword of weight $\ge 64$, so $\sum_{w \in W_3 \setminus \{0\}} \operatorname{wt}(w) \ge 6 \times 56 + 64 = 400$, giving $U_3 \ge 400 / 4 = 100$ by (1). Across all $788{,}035$ three-dimensional subspaces, the exact union-size distribution is
  $$100^{85,680}\; 104^{423,045}\; 108^{257,040}\; 112^{11,475}\; 120^{10,795}.$$
- **Case $k = 4$ (Hyperplane-Incidence Bound):** Let $W_4 \subseteq C$ have dimension $4$. In $W_4$, there are $\begin{bmatrix} 4 \\ 3 \end{bmatrix}_2 = 15$ three-dimensional hyperplanes $H \subset W_4$, and every nonzero vector $w \in W_4 \setminus \{0\}$ lies in exactly $\begin{bmatrix} 3 \\ 2 \end{bmatrix}_2 = 7$ of them. Summing the $k=3$ weight inequality $\sum_{u \in H \setminus \{0\}} \operatorname{wt}(u) \ge 400$ over all 15 hyperplanes $H \subset W_4$ gives
  $$7 \sum_{w \in W_4 \setminus \{0\}} \operatorname{wt}(w) = \sum_{\substack{H \subset W_4 \\ \dim H = 3}} \sum_{u \in H \setminus \{0\}} \operatorname{wt}(u) \ge 15 \times 400 = 6000.$$
  Applying (1) with $2^{4-1} = 8$ gives
  $$56 \left| \bigcup_{w \in W_4 \setminus \{0\}} \operatorname{supp}(w) \right| = 7 \sum_{w \in W_4 \setminus \{0\}} \operatorname{wt}(w) \ge 6000 \implies U_4 \ge \left\lceil \frac{6000}{56} \right\rceil = \left\lceil 107.1428\dots \right\rceil = 108.$$
- **Cases $k = 5, 6, 7, 8, 9$ (Annihilator Affine-Hyperplane Bound):** A port $i \in \{0, \dots, 119\}$ is *missed* by $W_k$ ($i \notin \bigcup_{w \in W_k \setminus \{0\}} \operatorname{supp}(w)$) if and only if its column functional $u_i \in C^*$ lies in the annihilator
  $$W_k^\perp = \{ \varphi \in C^* : \varphi|_{W_k} = 0 \}, \qquad \dim_{\mathbb{F}_2}(W_k^\perp) = 9 - k.$$
  Because the all-ones codeword $\mathbf{1}_{120} \in C$ satisfies $u_i(\mathbf{1}_{120}) = 1$ for all $120$ ports $i$, and the $120$ column functionals $u_i$ are distinct in $C^*$, every missed port functional $u_i$ must lie in the affine slice
  $$A(W_k) = \{ \varphi \in W_k^\perp : \varphi(\mathbf{1}_{120}) = 1 \}.$$
  - If $\mathbf{1}_{120} \in W_k$, then $\varphi(\mathbf{1}_{120}) = 0$ for all $\varphi \in W_k^\perp$, so $A(W_k) = \emptyset$ and all $120$ ports are covered.
  - If $\mathbf{1}_{120} \notin W_k$ (which requires $k \le 8$), the linear functional $\varphi \mapsto \varphi(\mathbf{1}_{120})$ is non-constant on $W_k^\perp$, so $A(W_k)$ is an affine hyperplane of $W_k^\perp$ of cardinality
    $$|A(W_k)| = 2^{(9-k)-1} = 2^{8-k}.$$
  Consequently, at most $2^{8-k}$ ports can miss $\bigcup_{w \in W_k \setminus \{0\}} \operatorname{supp}(w)$, proving
  $$U_k \ge 120 - 2^{8-k} \quad (5 \le k \le 8), \qquad U_9 = 120,$$
  which evaluates to $(U_5, U_6, U_7, U_8, U_9) = (112, 116, 118, 119, 120)$.
- **Sharpness:** In `CERTIFICATE.json` (`proposition_3_subspace_union_hierarchy.attaining_subspace_witnesses`), we exhibit an explicit nested basis $b_1, \dots, b_9 \in C$ whose prefixes $W_k = \operatorname{span}_{\mathbb{F}_2}(b_1, \dots, b_k)$ have support unions of sizes $(56, 84, 100, 108, 112, 116, 118, 119, 120)$. $\square$

---

## 5. Theorem 4 (All-Puncture $0 \le p \le 119$ Star Ratio Exclusion)

**Theorem 4.** *For every puncture set $P \subset \{0, \dots, 119\}$ of size $0 \le p \le 119$ ($1 \le v = 120 - p \le 120$), every sorted $9$-reader basis rank profile $0 \le d_1 \le d_2 \le \dots \le d_9 \le 8$ of $C$ satisfies*
$$\delta_{d_i} \le p \quad (1 \le i \le 9) \qquad \text{and} \qquad \sum_{i=1}^k M_{d_i} \ge U_k - p \quad (1 \le k \le 9). \tag{2}$$
*Consequently, for all $0 \le p \le 119$,*
$$\frac{C_{\text{star}}^{\text{live}}(P)}{120 - p} = \frac{C_{\text{star}}(P)}{120 - p} \ge \frac{63}{111},$$
*with equality possible only at $p = 9$ ($C_{\text{star}}(P) = 63$ on $v = 111$ live ports).*

*Proof.*
Let $c_1, \dots, c_9 \in C$ be a basis of $C$ with sorted surviving rational ranks $d_1 \le \dots \le d_9$, so $C_{\text{star}}(P) = \sum_{i=1}^9 d_i$. For each $i$, the surviving root lines $\operatorname{supp}(c_i) \setminus P$ span a rational subspace $V_i \subseteq \mathbb{Q}^8$ of dimension $d_i$, which contains at most $M_{d_i}$ root lines and forces $|\operatorname{supp}(c_i) \cap P| \ge \delta_{d_i}$, so $\delta_{d_i} \le p$.

For each $k \in \{1, \dots, 9\}$, let $W_k = \operatorname{span}_{\mathbb{F}_2}(c_1, \dots, c_k)$. Because $\operatorname{supp}(u \oplus v) \subseteq \operatorname{supp}(u) \cup \operatorname{supp}(v)$, every $w \in W_k \setminus \{0\}$ satisfies
$$\operatorname{supp}(w) \setminus P \subseteq \bigcup_{i=1}^k \bigl(\operatorname{supp}(c_i) \setminus P\bigr) \subseteq \bigcup_{i=1}^k (V_i \cap \Phi^+).$$
Therefore,
$$U_k - p \le \left| \bigcup_{w \in W_k \setminus \{0\}} \operatorname{supp}(w) \right| - |P| \le \left| \bigcup_{i=1}^k \bigl(\operatorname{supp}(c_i) \setminus P\bigr) \right| \le \sum_{i=1}^k M_{d_i},$$
establishing (2).

There are $\binom{9+9-1}{9} = 24{,}310$ sorted profiles $0 \le d_1 \le \dots \le d_9 \le 8$. For each $p \in \{0, \dots, 119\}$, minimizing $\sum_{i=1}^9 d_i$ over all profiles satisfying (2) (combined for $0 \le p \le 8$ with PR #631's direct single-port deletion bound $C_{\text{star}}(P) \ge 72 - p$) yields a lower bound $B(p) \le C_{\text{star}}(P)$ satisfying $B(p)/(120 - p) \ge 63/111$ for every $0 \le p \le 119$, with $B(p)/(120 - p) > 63/111$ for all $p \ne 9$. By Proposition 1, $C_{\text{star}}^{\text{live}}(P) = C_{\text{star}}(P)$, completing the proof. $\square$

### Why Higher-$k$ Constraints ($k \ge 3$) Are Necessary Beyond $p = 55$

If one uses only the single-reader and pairwise constraints ($k \le 2$, as in PR #939), the relaxation fails at **43 puncture budgets** in $0 \le p \le 119$:
- At $p = 72$ ($v = 48$), $84 - p = 12$, so $k \le 2$ allows $(3)^9$ ($M_3 + M_3 = 6 + 6 = 12 \ge 12$, cost $27$, ratio $27/48 = 9/16 = 0.5625 < 63/111$). The $k=3$ constraint $M_{d_1} + M_{d_2} + M_{d_3} \ge 100 - 72 = 28$ eliminates $(3)^9$ (since $3 M_3 = 18 < 28$) and forces $(3, 4, 4, 4, 4, 4, 4, 4, 4)$ of cost $35$ ($35/48 \approx 0.7292 > 63/111$).
- For $78 \le p \le 119$, the $k \le 2$ bound drops strictly below $63/111$ (and collapses to $0$ for $p \ge 84$), whereas the full $k = 1, \dots, 9$ hierarchy keeps $B(p)/(120 - p) > 63/111$ all the way to $p = 119$ ($v = 1$, where $U_9 = 120$ forces $d_9 \ge 1$, giving ratio $1/1 > 63/111$).
