# All-Puncture $E_8$ Star Label-Decoder Exclusion and $p=56$ Dimension-Loss Classification

- **Status:** Research note and scoped negative result (**no new $\kappa$**; `certificates/selected-result.json` is unchanged).
- **Track & Seed:** Track 40–49 (Structural decoder research), OS random seed `49`.
- **Base Commit:** `ce7ad1b6ab09452c3478723a2e96ed5ff212dc08`

## 1. Summary of What Was Learned

Previous structural decoder certificates excluded the $E_8$ root-only star label-decoder from improving on the known $9$-puncture ratio $63/111$ up to $p \le 35$ (**PR #631**, Chi Zhao), at $p = 36$ (**PR #875**, Philipp / `@mightyOil`), and up to $p \le 55$ (**PR #939**, Ross Richardson). PR #939 stopped at $p = 55$ because at $p = 56$ a minimum-weight codeword $c_0 \in C$ ($\operatorname{wt}(c_0) = 56$) can vanish identically on the $64$ live ports $L = \{0, \dots, 119\} \setminus P$, dropping the live binary label rank $\dim_{\mathbb{F}_2}(C|_L)$ from $9$ to $8$. Moreover, the pairwise ($k \le 2$) capacity inequality $M_a + M_b \ge 84 - p$ used in PR #939 fails at $p = 72$ ($27/48 = 9/16 < 63/111$) and across $78 \le p \le 119$ (collapsing to $0$ for $p \ge 84$).

This package resolves the remaining range $56 \le p \le 119$ and classifies the $p = 56$ dimension-loss boundary:

1. **Live-Quotient Star Cost Equivalence (Proposition 1):** For any puncture set $P$ with $0 \le p \le 119$ ($1 \le v \le 120$) and restriction kernel $K_P = \{c \in C : \operatorname{supp}(c) \subseteq P\}$ of dimension $k_0 = 9 - \dim_{\mathbb{F}_2}(C|_L) \in \{0, \dots, 8\}$, surviving rational star rank $s_P(c)$ is constant on cosets of $C / K_P \cong C|_L$ and vanishes iff $c \in K_P$. Thus the minimum star cost over $(9-k_0)$-element bases of the live quotient $C|_L$ equals the minimum star cost $C_{\text{star}}(P)$ over $9$-element bases of $C$.
2. **Exact $p=56$ Two-Orbit Dimension-Loss Classification (Proposition 2):** The $255$ puncture sets of size $p = 56$ that lose binary label dimension ($\dim_{\mathbb{F}_2}(C|_L) = 8$, $k_0 = 1$) are precisely the supports of the $255$ weight-$56$ codewords of $C$, which partition under $W(E_8)$ into two orbits:
   - **Orbit 1 ($135$ even-frame codewords):** $511$-reader rank histogram $\{0:1,\; 7:112,\; 8:398\}$, cumulative $\mathbb{F}_2$-dimensions $(1,1,1,1,1,1,1,8,9)$, exact optimal basis $(0,7,7,7,7,7,7,7,8)$ of star cost **$57$ on $64$ live ports** ($57/64 = 0.890625 > 63/111$). Every single-port restoration ($p=55$) restores $\dim_{\mathbb{F}_2}(C|_L)=9$ with cost $58$.
   - **Orbit 2 ($120$ root-nonorthogonality supports $S_a = \{i : |\langle L_i, L_a \rangle| = 4\}$):** live ports $\{a\} \cup a^\perp$ ($1 + 63 = 64$ lines), $511$-reader rank histogram $\{0:1,\; 6:56,\; 7:198,\; 8:256\}$, cumulative $\mathbb{F}_2$-dimensions $(1,1,1,1,1,1,8,8,9)$, exact optimal basis $(0,6,6,6,6,6,6,6,8)$ of star cost **$50$ on $64$ live ports** ($50/64 = 25/32 = 0.78125 > 63/111$). Every single-port restoration ($p=55$) restores $\dim_{\mathbb{F}_2}(C|_L)=9$ with cost $51$.
3. **Sharp Subspace Support-Union Hierarchy (Proposition 3):** Across all dimensions $1 \le k \le 9$, the minimum support union of a $k$-dimensional subspace $W_k \subseteq C$ is sharply
   $$(U_1, U_2, U_3, U_4, U_5, U_6, U_7, U_8, U_9) = (56, 84, 100, 108, 112, 116, 118, 119, 120),$$
   attained simultaneously by a single nested full flag $0 \subset W_1 \subset \dots \subset W_9 = C$.
4. **All-Puncture Ratio Exclusion (Theorem 4):** Imposing $\delta_{d_i} \le p$ and $\sum_{i=1}^k M_{d_i} \ge U_k - p$ ($1 \le k \le 9$) across all $24{,}310$ sorted rank profiles (with PR #631's $72-p$ for $0 \le p \le 8$) proves
   $$\frac{C_{\text{star}}^{\text{live}}(P)}{120 - p} = \frac{C_{\text{star}}(P)}{120 - p} \ge \frac{63}{111} \qquad \text{for all } 0 \le p \le 119,$$
   with equality possible only at $p = 9$.

## 2. Reproducible Commands and Expected Results

Run from the repository root (standard library Python 3 only; all checks remain active under `-I -O -B`):

```bash
python3 -I -O -B research/e8-star-all-punctures-seed49/verify.py
python3 -I -O -B research/e8-star-all-punctures-seed49/independent_check.py
python3 -I -O -B research/e8-star-all-punctures-seed49/test_package.py
```

Expected outputs:
- `verify.py`:
  ```text
  PASS: verified E8 all-puncture (0 <= p <= 119) star ratio >= 63/111, exact p=56 two-orbit dimension-loss classification (costs 57/64 and 50/64), sharp subspace union hierarchy U_1..U_9 = (56,84,100,108,112,116,118,119,120), and 8 negative controls.
  ```
- `independent_check.py`:
  ```text
  PASS (independent_check.py): independently verified 240->120 E8 root lines, mod-2 Gram reader code, Fraction-RREF p=56 orbit costs (57 and 50), U_1..U_9 hierarchy, and all 120 puncture budgets (0 <= p <= 119).
  ```
- `test_package.py`:
  ```text
  PASS (test_package.py): relocation, -I -O -B execution, byte-identical regeneration, tampered-certificate rejection, source-pin corruption rejection, and PR #631 replay all succeeded.
  ```

## 3. Base Commit and Retained Predecessor Sources

All retained predecessor files are stored in `sources/` and verified by SHA-256 and Git blob SHA-1 in [`SOURCES.json`](SOURCES.json):
- Base commit: `ce7ad1b6ab09452c3478723a2e96ed5ff212dc08`
- `sources/pr631/README.md` and `sources/pr631/verify.py` (from PR #631, commit `fb893b5ee1317c2da3b297e6fe78eca0857d1a76`)
- `sources/pr875/README.md` (from PR #875, commit `7f334e4c749fd83d03feb6c1de4e4cda9534c9dc`)
- `sources/pr939/README.md` and `sources/pr939/PROOF.md` (from PR #939, commit `3a8ec54d62fb8824c658dc7ed356f99423cac8cf`, merged via `c9b187382b2d370e21e866fa4070a7bfceaf86ad`)

## 4. Scope, Inherited Assumptions, and Unresolved Obligations

- **Model scope:** This result applies strictly to the real $E_8$ root-only star label-decoder cost model $C_{\text{star}}(P) = \min_{\text{basis}} \sum_{i} \dim_{\mathbb{Q}} \operatorname{span}_{\mathbb{Q}}\{L_t : t \in \operatorname{supp}(c_i) \setminus P\}$ defined in PR #631 and PR #939.
- **Inherited assumptions:** Uses PR #631's Borel–de Siebenthal / parabolic reduction (every rational flat spanned by $E_8$ root lines is $W(E_8)$-conjugate to a subspace of one of the $256$ standard parabolic flats) and PR #631's direct $72 - p$ bound for $0 \le p \le 8$ (replayed directly in `test_package.py`).
- **What is NOT claimed:** This is a finite-dimensional coding/root-system proof and exact certificate within the $E_8$ star label-decoder model, not a formal proof of the full asymptotic multiplication theorem and not an exclusion of non-star, multi-stage, or non-$E_8$ decoders.

## 5. Attribution and AI Disclosure

- **Predecessor credit:** Builds directly on PR #631 by Chi Zhao, PR #875 by Philipp (`@mightyOil`), and PR #939 by Ross Richardson.
- **Contributor & AI Assistance Disclosure:** Prepared by `@3xcalibur-tech` with substantial AI assistance from **Antigravity (Google DeepMind / Gemini)**, which assisted with mathematical formulation, verification script implementation, independent checker design, and documentation. Licensed under Apache-2.0; see [`NOTICE.md`](NOTICE.md).
