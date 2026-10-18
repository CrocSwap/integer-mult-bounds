# Finite two-sided signed bi-forest compensation identity and price

Let $y$ be the $112$ target registers (`L[112..223]`) and $h$ be the $216$ active
helper registers read by the selected U8 compensation panel (`native/local/CANONICAL-WORD.json.gz`
in `research/community-frontier942-audit/t37-replay.tar.gz`, bound by
`research/gauge44-barch/construction/barch/LOCAL-PINS-barch-U8.json`). Its linear
map is $(y, h) \mapsto (y + C h, h)$, where every entry of the $112 \times 216$
matrix $C$ lies in $\frac{1}{4}\mathbb{Z}$. All $112$ targets and $216$ active
helpers start in frame $0$ (`start[r] == 0`), and all $216$ active helpers have
`final[r] == 1` (`plain` role): none is a cold wrapped helper requiring an
entry wrapper before read or write access. The preceding `zero_frame_precondition`
phase also operates in frame $0$ and is retained unchanged, so $y$ and $h$ enter
the compensation panel as arbitrary inputs.

## 1. Leaf-before-parent helper-accumulating forest identity

Previous two-sided compensation constructions restricted the helper-side basis
change to **register-disjoint pairs** (`research/complex-ck-two-sided`, PR917,
at most $\lfloor n_H/2 \rfloor$ helper edges) or **depth-1 stars** (PR967) so
that elementary helper shears commute and $(H - I)^2 = 0$. We prove that an
**arbitrary-depth rooted signed forest** $F_H$ on the helper bank has an exact
inverse $H^{-1}$ with **zero ancestor cross-terms** when its elementary shears
are scheduled in **leaf-before-parent (bottom-up)** order.

Let $F_H$ be any rooted directed forest on the $216$ active helpers where each
nonroot helper $b$ has a unique parent $p(b) \neq b$ and sign $s_b \in \{-1, +1\}$.
Order the $e_H$ nonroot helpers $b_1, \dots, b_{e_H}$ in **leaf-before-parent
(non-increasing depth)** order: if $b_i$ is a child of $b_j$, then $i < j$. In
particular, a child always precedes its parent in the list, so
$$
b_i \neq p(b_j) \quad \text{for all } 1 \le i < j \le e_H.
$$

For each $i \in \{1, \dots, e_H\}$, define the elementary helper-accumulating shear
$$
E_i = I + s_{b_i}\, e_{p(b_i)} e_{b_i}^T,
$$
which executes the frame-zero addition `h[p(b_i)] += s_{b_i} * h[b_i]`. Executing
$E_1, E_2, \dots, E_{e_H}$ chronologically applies the product
$$
H = E_{e_H} \cdots E_2 E_1
$$
to the helper bank $h \leftarrow H h$.

**Lemma (Zero ancestor cross-terms in $H^{-1}$).** *Under leaf-before-parent
ordering of $E_1, \dots, E_{e_H}$, the inverse operator satisfies*
$$
H^{-1} = E_1^{-1} E_2^{-1} \cdots E_{e_H}^{-1}
       = \prod_{i=1}^{e_H} \bigl(I - s_{b_i}\, e_{p(b_i)} e_{b_i}^T\bigr)
       = I - \sum_{i=1}^{e_H} s_{b_i}\, e_{p(b_i)} e_{b_i}^T.
$$

*Proof.* For any $1 \le i < j \le e_H$, the product of the rank-one terms from
$E_i^{-1}$ and $E_j^{-1}$ is
$$
\bigl(e_{p(b_i)} e_{b_i}^T\bigr)\bigl(e_{p(b_j)} e_{b_j}^T\bigr)
= \bigl(e_{b_i}^T e_{p(b_j)}\bigr)\, e_{p(b_i)} e_{b_j}^T
= \delta_{b_i,\, p(b_j)}\, e_{p(b_i)} e_{b_j}^T = 0,
$$
because $b_i \neq p(b_j)$ whenever $i < j$ in leaf-before-parent order. Since
every pairwise product with $i < j$ vanishes, all degree-$\ge 2$ products in
$\prod_{i=1}^{e_H} (I - s_{b_i} e_{p(b_i)} e_{b_i}^T)$ vanish identically. $\square$

**Corollary (Pure two-column difference on the residual).** *For any matrix $D$,
right-multiplying by $H^{-1}$ transforms each column $b$ independently according to*
$$
(D H^{-1})_{\cdot, b} =
\begin{cases}
D_{\cdot, b} - s_b\, D_{\cdot, p(b)} & \text{if } b \text{ is a nonroot of } F_H,\\[2pt]
D_{\cdot, b} & \text{if } b \text{ is a root of } F_H.
\end{cases}
$$
*Moreover, helper restoration $h \leftarrow H^{-1} h = E_1^{-1} \cdots E_{e_H}^{-1} h$
is realized chronologically by reversing the preparation list and negating each sign
(`h[p(b_i)] -= s_{b_i} * h[b_i]` in **parent-before-leaf** order $i = e_H, \dots, 1$).*

## 2. Two-sided bi-forest circuit and backward dual

On the target bank $y$, let $F_T$ be a rooted signed forest with $e_T$ nonroot
targets. For each nonroot target $t$ with parent $p(t)$ and sign $s_t \in \{-1, +1\}$,
executing `y[t] -= s_t * y[p(t)]` in **leaf-before-parent (deepest-first)** order
reads every parent $p(t)$ before $p(t)$ itself is modified, realizing
$$
(T y)_t =
\begin{cases}
y_t - s_t\, y_{p(t)} & \text{if } t \text{ is a nonroot of } F_T,\\[2pt]
y_t & \text{if } t \text{ is a root of } F_T,
\end{cases}
$$
so $(T C)_{t, \cdot} = C_{t, \cdot} - s_t\, C_{p(t), \cdot}$ on nonroots and $C_{t, \cdot}$
on roots. Restoring in **parent-before-leaf** order with $+s_t$ realizes $T^{-1}$.

By matrix associativity $(T C) H^{-1} = T (C H^{-1}) =: E$, the two-sided residual
entry for any $(t, b)$ is the four-term stencil
$$
E_{t, b} = (T C H^{-1})_{t, b}
= C_{t, b} - s_t\, C_{p(t), b} - s_b\, C_{t, p(b)} + s_t s_b\, C_{p(t), p(b)}
$$
(with the $p(t)$ or $p(b)$ terms omitted when $t$ or $b$ is a root). The emitted
chronological frame-zero circuit is
```text
y <- T y                 (e_T unit shears, leaf-before-parent)
h <- H h                 (e_H unit shears, leaf-before-parent)
y <- y + (T C H^-1) h    (nonzero entries of E = T C H^-1)
h <- H^-1 h              (e_H unit shears, parent-before-leaf)
y <- T^-1 y              (e_T unit shears, parent-before-leaf)
```
Its forward action is
$$
(y, h) \mapsto \bigl(T^{-1}(T y + T C H^{-1} H h),\, H^{-1} H h\bigr) = (y + C h,\, h).
$$
For the inverse-transpose (`backward`) program, every logical addition
$A = I + q\, e_u e_v^T$ is mapped to $A^{-T} = I - q\, e_v e_u^T$ in the **same
chronological order**. Since $(A_k \cdots A_1)^{-T} = A_k^{-T} \cdots A_1^{-T}$,
the dualized panel realizes the exact inverse-transpose compensation map
$(y, h) \mapsto (y,\, h - C^T y)$.

## 3. Exact complete price and alternating MST fixed point

Under the inherited unoptimized binary-Horner lowering (`lower` in `experiment.py`),
each nonzero dyadic addition with reduced coefficient $q = a / 2^d$ ($a \neq 0$,
$\gcd(|a|, 2^d) = 1$) costs
$$
p(q) = 3 + \lfloor \log_2 |a| \rfloor + \operatorname{popcount}(|a|) + d
$$
component primitives (including the initial `clear(W[0])`, all source accumulations,
doublings, halvings, signed target accumulation, and final `clear(W[0])`), with
$p(0) = 0$. Every unit shear $q = \pm 1$ costs $p(\pm 1) = 4$ component primitives,
so its preparation plus restoration costs $8$ component primitives. Real and
imaginary components execute identical scalar instructions, doubling component
primitive counts to real-component primitive counts.

For any signed target forest $F_T$ with $e_T$ edges and signed helper forest
$F_H$ with $e_H$ edges, the complete one-component compensation price is
$$
\operatorname{Price}(F_T, F_H)
= 8 e_T + 8 e_H + \sum_{t, b} p\bigl((T C H^{-1})_{t, b}\bigr).
$$

- **Target step for fixed $F_H$:** Let $R = C H^{-1}$. Each target $t$ independently
  chooses either to be a root with cost $\sum_b p(R_{t, b})$ or to attach to a
  parent $u$ with sign $s_t \in \{-1, +1\}$ at cost $8 + \sum_b p(R_{t, b} - s_t R_{u, b})$.
  Because $p(-q) = p(q)$, edge weights are symmetric, so minimizing $\operatorname{Price}(F_T, F_H)$
  over all rooted signed forests $F_T$ for fixed $F_H$ is an exact minimum spanning
  tree problem on $112$ target vertices plus a superroot ($112 + 2\binom{112}{2} = 12{,}544$
  evaluated edges).
- **Helper step for fixed $F_T$:** Let $D = T C$. By the Corollary above, each
  helper $b$ independently chooses either to be a root with cost $\sum_t p(D_{t, b})$
  or to attach to a parent $a$ with sign $s_b \in \{-1, +1\}$ at cost
  $8 + \sum_t p(D_{t, b} - s_b D_{t, a})$. Because $p(-q) = p(q)$, minimizing
  $\operatorname{Price}(F_T, F_H)$ over all rooted signed forests $F_H$ for fixed
  $F_T$ is an exact minimum spanning tree problem on $216$ helper vertices plus a
  superroot ($216 + 2\binom{216}{2} = 46{,}656$ evaluated edges).

Starting from the target-only minimum spanning forest $T_0$ on $C$ (which matches
Ross Richardson's PR932 and woklerx's PR961 target-only floor of $10{,}883$
component primitives), alternating exact MST optimization strictly decreases the
complete compensation price to a coordinate-wise MST fixed point $(T_5, H_5)$:

| Stage / construction | Target edges $e_T$ | Helper edges $e_H$ | Residual additions | Residual price | Basis price $8(e_T+e_H)$ | Total component primitives | Real primitives saved vs baseline | Additional real saved vs target floor |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline U8 `C` | 0 | 0 | 6,320 | 34,728 | 0 | **34,728** | 0 | — |
| Step 0: Target-only forest $T_0$ (PR932/PR961 floor) | 106 | 0 | 2,112 | 10,035 | 848 | **10,883** | 47,690 | 0 |
| Comparator: $T_0$ + greedy disjoint helper pairs (PR917 method on U8) | 106 | 86 | 1,683 | 7,431 | 1,536 | **8,967** | 51,522 | 3,832 |
| Step 1a: One-pass bi-forest $(T_0, H_1)$ | 106 | 138 | 1,455 | 6,421 | 1,952 | **8,373** | 52,710 | 5,020 |
| Step 1b: Re-optimized target forest $(T_1, H_1)$ | 100 | 138 | 1,389 | 6,316 | 1,904 | **8,220** | 53,016 | 5,326 |
| Step 2a: Re-optimized helper forest $(T_1, H_2)$ | 100 | 144 | 1,346 | 6,155 | 1,952 | **8,107** | 53,242 | 5,552 |
| Step 2b: Re-optimized target forest $(T_2, H_2)$ | 99 | 144 | 1,347 | 6,151 | 1,944 | **8,095** | 53,266 | 5,576 |
| Step 3a: Re-optimized helper forest $(T_2, H_3)$ | 99 | 149 | 1,303 | 6,037 | 1,984 | **8,021** | 53,414 | 5,724 |
| Step 3b: Re-optimized target forest $(T_3, H_3)$ | 99 | 149 | 1,303 | 6,024 | 1,984 | **8,008** | 53,440 | 5,750 |
| Step 4a: Re-optimized helper forest $(T_3, H_4)$ | 99 | 145 | 1,309 | 6,010 | 1,952 | **7,962** | 53,532 | 5,842 |
| Step 4b: Re-optimized target forest $(T_4, H_4)$ | 100 | 145 | 1,303 | 5,986 | 1,960 | **7,946** | 53,564 | 5,874 |
| **Step 5: Fixed point $(T_5, H_5)$** | **100** | **148** | **1,284** | **5,946** | **1,984** | **7,930** | **53,596** | **5,906** |

At $(T_5, H_5)$:
- $T_5$ has $100$ directed edges ($12$ roots, maximum edge depth $6$), and is certified
  globally minimal for fixed $H_5$ by Prim's algorithm and all $12{,}544$
  cycle-exchange inequalities on $C H_5^{-1}$.
- $H_5$ has $148$ directed edges ($68$ roots, maximum edge depth $7$, exceeding the
  $216/2 = 108$ cardinality cap of disjoint helper pairs), and is certified
  globally minimal for fixed $T_5$ by Prim's algorithm and all $46{,}656$
  cycle-exchange inequalities on $T_5 C$.
- Coordinate-wise MST optimality at $(T_5, H_5)$ does **not** claim joint global
  optimality over all pairs $(F_T, F_H)$ simultaneously.

## 4. Prefix envelopes, denominator depths, children, and verification limits

Propagating a positive norm envelope from $1$ on each of the $737$ independent
input columns ($728$ logical registers `L[0..727]`, $8$ private centers `C[0..7]`,
and $1$ scratch register `W[0]`) through every literal primitive yields:
- Forward positive prefix peak: `1272245877576558407/16` (`57` bits vs `55` bits baseline).
- Backward positive prefix peak: `204764373028968404875897/32` (`73` bits vs `72` bits baseline, and $1$ bit tighter than the `74`-bit backward peak of the target-only forest).
Both are strictly inside the inherited `192`-bit local payload allowance.
The maximum reduced dyadic denominator exponent across all intermediate symbolic
states remains `3` forward and `19` backward, unchanged from the baseline U8 programs.

The native paid child histogram remains `{1: 2548, 2: 338, 3: 446, 4: 162, 5: 72, 8: 8}`
($3{,}574$ paid children) in both orientations. All non-scalar events retain their
exact order. Because $\kappa$ depends on the paid recursive child profile rather
than finite frame-zero scalar additions, **no new $\kappa$ is claimed**.

Two independent arithmetic engines (`experiment.py` using `Fraction` and
`independent.py` using sparse integer rows over powers of two) verify the full
$737$-column forward and backward endpoints. The unchanged native emitter and
auditor (`hpe_emit_local.py`, `hpe_audit_local.py`) verify the $728$-column
common-frame/wrapper contract and reject all $25$ inherited negative controls.
Twelve package-level mutation controls—including reversing helper preparation or
restoration (which fails specifically because $H_5$ has edge depth $7 \ge 2$) and
omitting target preparation (which passes a helper-only check on `224..727` and
fails the full $737$-column check)—confirm sensitivity to every circuit invariant.
These finite replays do not constitute a formal proof of the asymptotic
multiplication theorem.
