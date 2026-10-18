# Validation Log

## Environment and Base Pin

- **Base Commit:** `ce7ad1b6ab09452c3478723a2e96ed5ff212dc08`
- **Track & Seed:** Track 40–49 (Structural decoder research), OS random seed `49`
- **Interpreter:** Python 3 standard library only, verified under `python3 -I -O -B` (isolated mode, optimized mode with `assert` stripped, no bytecode writes)

## Executed Checks

1. **Primary Verifier (`verify.py`):**
   ```bash
   python3 -I -O -B research/e8-star-all-punctures-seed49/verify.py
   ```
   - Verifies SHA-256 and Git blob SHA-1 pins for all 5 retained predecessor files in `sources/`.
   - Constructs 120 positive $E_8$ root lines, 8 simple roots, $W(E_8)$ reflection permutations, 9-row decoder $B$, 512-word reader code $C$, and 120 distinct nonzero column functionals.
   - Verifies all 256 parabolic flats, $M_d = (0,1,3,6,12,20,36,63,120)$, and $\delta_d = (56,55,53,50,44,36,26,1,0)$.
   - Classifies the 5 $W(E_8)$ orbits on $C\setminus\{0\}$ and verifies the two weight-56 orbits at $p=56$ (Orbit 1 of size 135, cost $57/64$; Orbit 2 of size 120, cost $50/64$), coset invariance on $C/K_P$, seed-49 orbit members, and all 112 single-port restorations ($p=55$).
   - Certifies the sharp subspace support-union hierarchy $U_1,\dots,U_9 = (56,84,100,108,112,116,118,119,120)$ across all $788{,}035$ three-dimensional subspaces ($5{,}516{,}245$ pointed pairs) and a nested attaining flag $W_1 \subset \dots \subset W_9$.
   - Certifies all 120 puncture budgets $0 \le p \le 119$ across all $24{,}310$ sorted 9-rank profiles and runs 8 negative controls.

2. **Independent Checker (`independent_check.py`):**
   ```bash
   python3 -I -O -B research/e8-star-all-punctures-seed49/independent_check.py
   ```
   - Does not import `verify.py` or any predecessor code.
   - Constructs all 240 signed $E_8$ roots first, quotients by antipodal sign in reverse lexicographic order, builds $C$ from the $120 \times 120$ mod-2 Gram matrix $(I+A)\bmod 2$ via low-bit GF(2) reduction, and uses `fractions.Fraction` RREF and matrix inversion.
   - Independently verifies $M_d$, $\delta_d$, the $p=56$ two-orbit histograms and matroid rank-sum costs $\sum_{d=0}^7 (9-r_d) = 57$ and $50$, all 112 single-port restorations, the $U_1,\dots,U_9$ lower-bound formulas, and all 120 puncture budgets $0 \le p \le 119$.

3. **Relocation, Tamper Rejection, and Predecessor Replay Suite (`test_package.py`):**
   ```bash
   python3 -I -O -B research/e8-star-all-punctures-seed49/test_package.py
   ```
   - Relocates the package to a temporary directory outside the Git repository and runs both checkers under `python3 -I -O -B`.
   - Deletes and regenerates `CERTIFICATE.json`, confirming byte-for-byte identity with the committed file.
   - Confirms both `verify.py` and `independent_check.py` fail when `CERTIFICATE.json` is tampered with (`star_cost` $50 \to 49$ at $p=56$, or `min_cost_k9` $35 \to 34$ at $p=72$).
   - Confirms `verify.py` fails when a retained source file in `sources/` is modified.
   - Replays the pinned predecessor verifier `sources/pr631/verify.py`.
