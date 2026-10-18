# Independent positive-binomial and 1024-bit endpoint-to-$\kappa$ audit of the selected PR #942 (T37) record

**Status: independent verification; no new $\kappa$.**

- **Track & seed:** Track 75–84 (*Independent verification or formalization*), OS-random seed **78**
- **Base commit:** `2921874911956718fcaaaf9396fe8267b3cfa9f0`
- **Audited selected frontier:** PR [#942](https://github.com/CrocSwap/integer-mult-bounds/pull/942) at source head `1960cfa919a0945d0ca4cb14ea96237000037903`, conditional $\kappa = 1661960547713947 / 10^{18} = 0.001661960547713947$
- **Certificate verified:** `research/community-frontier942-audit/ASSEMBLY.json` (`sha256: 4b2894956e594e408e111d806c842f2ed2c32aefcadff93fad69ff0b46f1991a`) and `research/community-frontier942-audit/ALL-T-BOUND.json` (`sha256: 5101909cf84a2bfce777dcc34075ffcfe5c135debd16fa56ef7273523b434a35`)

## What was verified and learned

Previous batch970 audits (`research/t21-binomial-audit` from PR #960 and `research/audit-frontier890-endpoint-seed73` from PR #957) verified the *historical* PR #890 ($T = 21$, 512-bit reserve) checkpoint, and `research/t21-binomial-audit` intentionally rejects the updated selection when run with `--repository .`. Meanwhile, `research/complex-t37-owners/independent/all_t_bound.py` certifies the PR #942 all-$T$ supporting inequalities by importing the two retained logarithm/exponential engines (`moment.py` and `base_two_moment.py`).

This package provides a self-contained Python 3 standard-library verifier (`verify.py`) for the **current selected PR #942 ($T = 37$, 1024-bit reserve) frontier** that imports **no** production logarithm, exponential, moment, outer-assembly, supplier, or owner module:

1. **All 6 supplier moment endpoint decisions via positive generalized-binomial enclosures:**
   Using outward dyadic rounding on $D = 2^{240}$ with geometric tail $\le 2^{-170}$ per power factor, `verify.py` encloses $(m/r)^a = (1 - (1 - r/m))^{-a} = \sum_{k \ge 0} \binom{a+k-1}{k}(1 - r/m)^k$ and certifies:
   - **T37 native complex ($m = 73, W = 33152$):** strict acceptance ($M < 1$) at $b = 416181814685169713943 / 250000000000000000000000 = 1664727258740678855772 / 10^{24}$ and strict rejection ($M > 1$) at $b + 10^{-24}$.
   - **T37 conservative complex ($m = 73, W = 33152$, surcharged):** strict acceptance ($M_{\text{bad}} < 1$) at $b_c = 1664727255848707292019 / 10^{24}$ and strict rejection ($M_{\text{bad}} > 1$) at $b_c + 10^{-24}$.
   - **PR589 bit supplier ($m = 64, W = 28416$, blob `e293ddc557742637f9f679f083a1a282d87b1b13`):** derives the exact rank-mass deficit $32(2 \cdot 4 \cdot 111 - 9 \cdot 63) = 10272 = 64 \cdot 28416 - 1808352$ from the punctured R439 word parameters ($v = 111, \text{cst} = 63$) and certifies strict acceptance ($M_{\text{bit}} < 1$) at $c = 1733427039589844234749 / 10^{24}$ and strict rejection ($M_{\text{bit}} > 1$) at $c + 10^{-24}$.
   - Every binomial residual interval overlaps both recorded intervals (`mercator` and `base_two`) in `ASSEMBLY.json`.

2. **All 42 strict rank inequalities of the PR #942 all-$T$ signed-dual supporting lemma via positive binomial enclosures, plus the exact $T_{21}/T_{16}/T_{37}$ remainder-trade bridge:**
   - Independently enumerates all $1,163$ legal helper-width vectors across capacities $\{8, 16, 32, 48\}$ by both Cartesian product and dynamic programming, recovering all $45$ realized remainders $u(r)$, $M_0 = 14382$, $S_0 = -3892$, $V_0 = 48 S_0 + 13 M_0 = 150$, and $150 / 925 = 6 / 37$.
   - Certifies all $42$ strict pointwise rank inequalities
     $$\operatorname{margin}(r, z) := c(r, z) - \frac{v(r)}{925}\,c(1, z) > 0 \quad (r \in \operatorname{dom}(u) \setminus \{0, 1, 48\})$$
     at $z = 1664727258740678855773 / 10^{24}$ using only positive generalized-binomial enclosures of $\Phi(r, z) = r(73/r)^z$ (minimum strict margin at $r = 2$: $\approx 0.29137338586 > 0$).
   - **Exact algebraic bridge between the 8-role remainder trade and the all-$T$ supporting lemma:** Both predecessor blocks $T = 21$ (`{48: 6292, 3: 1, 1: 3}`) and $T = 16$ (`{48: 4793, 44: 1, 2: 1, 1: 2}`) are already **signed-dual tight** ($\sum_r v(r) n_r = 150 T$), because $v(3) + 3 v(1) = 375 + 2775 = 3150 = 150 \times 21$ and $v(44) + v(2) + 2 v(1) = -100 + 650 + 1850 = 2400 = 150 \times 16$. Consequently, in the $\Phi(r, z)$ basis, for every saving exponent $z$:
     $$M_{21}(z) - M_{37}(z) \equiv \frac{\operatorname{margin}(3, z)}{48 \cdot 73 \cdot 18816}, \qquad M_{16}(z) - M_{37}(z) \equiv \frac{\operatorname{margin}(44, z) + \operatorname{margin}(2, z)}{48 \cdot 73 \cdot 14336},$$
     and the moment reduction achieved by the 8-role remainder trade `44 + 3 + 2 -> 48 + 1` in `EDITS.json` is identically
     $$M_{\text{untraded}}(z) - M_{37}(z) \equiv \frac{\operatorname{margin}(44, z) + \operatorname{margin}(3, z) + \operatorname{margin}(2, z)}{48 \cdot 73 \cdot 33152} \approx +1.00878819 \times 10^{-8}.$$
     Without this 8-role remainder trade, the un-traded $T_{21}+T_{16}$ concatenation (`{48: 11085, 44: 1, 3: 1, 2: 1, 1: 5}`) has the exact same rank mass $2,408,256$ and signed-dual credit $5,550$, but is strictly rejected at the accepted $T = 37$ endpoint $b$ ($M_{\text{untraded}}(b) - 1 \approx +1.008788 \times 10^{-8} > 0$).

3. **Complete 1024-bit reserve, 7-step bootstrap, 94-slack outer reduction, and surcharge stakes:**
   - Reconstructs the $T = 37$ accounting ($333$ calls, $167,832$ roles, prefix $72 + 37 + 333 + 333 + 4 = 779 < 1024$, $|Sp_{72}(2)| \times 33666$ stock of $2,643$ bits, required $C_0$ precision $200,012 < 210,000$ bits, physical row coefficient $2 \cdot 2643 + 9909 + 252 + 2048 = 17495 < 20161$, and admissible integer payload reserve window $P \in [780, 2356]$).
   - Recomputes all $14$ bootstrap steps (`bootstrap` and `conservative_bootstrap`), verifying that the quadratic cutoff $\lceil 36/\text{gap}^2 \rceil$ strictly dominates the enlarged 1024-bit linear cutoff $\lceil 2(4+1024)/\text{gap} \rceil$ at every step (with minimum dominance margin $+4,910,947,306,998$ at step 1), leaving all 7 integer `cutoff_log2` values unchanged when upgrading the reserve from `512` to `1024`.
   - Recomputes all $94$ strict outer slacks (`47` accepted + `47` conservative) and $8$ outer control rejections (`next_grid`, `zero_eta`, `zero_beta`, `unit_beta`), confirming:
     - Accepted $\kappa = 1661960547713947 / 10^{18} = 0.001661960547713947$ (gain over PR #890 $T = 21$: $+2,773,066,918 / 10^{18}$, or $2,773$ grid ticks on $10^{-18}$).
     - Conservative $\kappa = 83098027241579 / 5 \cdot 10^{16} = 0.001661960544831580$.
     - Native complex correction gain $\kappa - \kappa_{\text{cons}} = 2,882,367 / 10^{18} = 2.882367 \times 10^{-12}$ ($2,882,367$ grid ticks on $10^{-18}$, two ticks wider than $T = 21$'s $2,882,365$ ticks).

## Reproduce

Python 3.11+ standard library only. From the repository root:

```sh
python3 -I -B research/t37-binomial-endpoint-audit-seed78/verify.py --repository .
python3 -I -O -B research/t37-binomial-endpoint-audit-seed78/test_package.py
```

Expected output of the first command:

```text
PASS_T37_REPOSITORY_BINDINGS files=14
PASS_T37_BINOMIAL_AND_ENDPOINT_AUDIT 6 moment decisions; 42 all-T binomial rank inequalities; 14 bootstrap steps; 94 outer slacks; 770 algebraic comparisons; 8 mathematical controls; 14 rejected inputs.
```

Expected output of the second command:

```text
PASS_T37_BINOMIAL_PACKAGE controls=12 relocated_optimized=PASS regeneration=PASS failure_preserves_certificate=PASS
```

## Scope, concurrent work, and inherited obligations

This package certifies the exact arithmetic consequences of the pinned PR #942 ($T = 37$) profiles, the 8-role remainder trade, the all-$T$ signed-dual supporting lemma, and the 1024-bit outer assembly reduction. It does not replay the full physical circuit/tape invoice (`t37-replay.tar.gz`), rebuild the PR589 bit circuit, or discharge inherited all-size compiler, common-label/mutable-source hosting, precision/tape, or analytic transfer assumptions ($H_1$–$H_5$).

**Comparison with concurrent PR [#1051](https://github.com/CrocSwap/integer-mult-bounds/pull/1051) (`3b8fab9b48d54160d0765c316eed45078f32aa5e` by Sagar Thakrar / `thakrarsagar`):**
Identified during pre-submission PR refresh. PR #1051 checks the three T37 moment brackets and the binding $\kappa$ margin using prime-decomposition `atanh` logarithms followed by Taylor exponentials. This package corroborates those endpoint decisions via a genuinely different single-stage numerical method (positive generalized-binomial series $(1 - (1 - r/m))^{-a}$ with no logarithm or exponential intermediates, backed by 770 exact integer-power algebraic comparisons $L^q \le (m/r)^p \le U^q$) and adds substantial coverage that PR #1051 explicitly leaves out of scope:
- positive-binomial certification of all **42 strict rank inequalities** of the PR #942 all-$T$ signed-dual supporting lemma (plus independent 1,163-vector Cartesian and DP dual enumerations),
- verification of the **8-role `44+3+2 -> 48+1` remainder trade** in `EDITS.json` and the **exact symbolic and numerical $T_{21}/T_{16}/T_{37}$ supporting-margin decomposition** ($M_{\text{untraded}}(z) - M_{37}(z) \equiv \sum_{r \in \{44,3,2\}} \operatorname{margin}(r, z) / (48 \cdot 73 \cdot 33152)$),
- verification of all **14 bootstrap steps** (`7` accepted + `7` conservative) and the exact quadratic-over-1024-bit-linear cutoff dominance margins,
- verification of all **94 strict outer assembly slacks** (`47` accepted + `47` conservative) and all 8 outer control rejections,
- verification of the **1024-bit reserve, $|Sp_{72}(2)|$ stock (`2643` bits), $C_0$ precision (`200012 < 210000` bits), physical row coefficient (`17495 < 20161`), and admissible payload interval $[780, 2356]$**.

## Attribution and license

- **Predecessor and concurrent work credited:** Jonathan Capalbo (`jon314159`, PR #942), Chafik Boukhalfa (PR #890), Jeremy Kothe (PR #869/#870), Hao Yan (PR #858), David Breslauer (PR #960, `research/t21-binomial-audit`), Aaron Wang (`navinor`, PR #957), Sagar Thakrar (`thakrarsagar`, concurrent PR #1051), `0x-chad` (PR #678), `arkfx` (PR #706), Gareth Davidson (`bitplane`, PR #813), `DreamingOfClouds`, `eumemic`, Rohan Arun, and `icekylinx`.
- **Contributor:** Prepared for `steph4n-gh` with substantial Google Gemini assistance (Track 75–84, Seed 78).
- **License:** Apache-2.0.
