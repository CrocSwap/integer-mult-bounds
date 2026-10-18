# Review items on PR #2044: the disabled `or True` assertion and the per-record g^2 sweep

Scope: two review items on `research/capped-fusion-t74-k554` at PR #2044 head `322949a5`. All paths below are
relative to that directory. This is a read-only audit. It is not a proof of the T74 claim and not a multiplication theorem.
Replay: `python3 -I -B research/t74-side-condition-coverage-audit/review_items.py`. This default mode is self-contained.
It runs 88 exact checks in about 6 s, using only the standard library. Add `--source-root DIR` to also re-check the file-level facts below.
That mode checks SHA-256 and git-blob pins, exact line text, `ast` parses and 108 file:line anchors within +-2 lines. With it, the run has 122 checks.
Credit: the disabled assertion was found by PR1897 (M6LI). The corrected s = -dl/lam bracket is PR1876's supplemental identity (Rohan Arun).

## Item 1: `outer/check_gaugefree.py:23` (`... or True`)

**What line 23 asserts.** Line 20 sets `claim = -b0*[bracket]`, the general-s Lemma 2.1 identity, and line 21 asserts it live.
Line 22 sets `sub = expand(claim.subs(s, -dl/lam))`. Line 23 then asserts
`sub == -b0*[(1-lam)x^2 - lam(1-lam)y^2 + dl^2 + dl^2/lam + 0*x - 2dl(1-lam)y - 2dl^2*0]` and appends `or True`.
The `ast` scan confirms that the test is vacuous.

**Correct bracket.** At s = -dl/lam, (x - lam y + dl)^2 - lam(x - y - s)^2 equals
**(1-lam)x^2 - lam(1-lam)y^2 + dl^2 - dl^2/lam + 2dl(1-lam)y**.
- The constant term dl^2 - dl^2/lam equals -theta dl^2 when lam = 1/(1+theta).
- The x-linear term is 0.

This is certified by an exact Laurent-polynomial expansion over Q. It is also checked at 1500 random rational points with seed 20441876.

**The two sign errors in the disabled expression:**
- **Constant term:** it has `+dl^2/lam`; the correct term is `-dl^2/lam`.
- **y-linear term:** it has `-2dl(1-lam)y`; the correct term is `+2dl(1-lam)y`.

The residual `sub - (-b0)D` equals `2 b0 dl^2/lam - 4 b0 dl(1-lam) y`, which is not zero, so without `or True` the assertion would fail.
The quadratic and x-linear parts agree, so these are the only two differences.

Three mutation controls are rejected at every random point: the full disabled bracket, a constant-only flip and a y-linear-only flip.
With `--source-root`, line 23's bracket is parsed from the file by `ast`. It equals the transcription above and differs from the certified bracket.

**Nothing depends on it.**
- The proof never uses s = -dl/lam:
  - The broad block uses s = -delta(1-theta) (`outer/GAUGEFREE-INTERIORS.md:31`), checked live at `check_gaugefree.py:44-46`.
  - The narrow block uses s = -beta0/rho (`GAUGEFREE-INTERIORS.md:37`), checked live at `check_gaugefree.py:35`.
  - s = -delta/lambda appears only in the parenthetical at `GAUGEFREE-INTERIORS.md:32`. That parenthetical makes two claims: an x-coefficient of 0, and a y-coefficient of 2 b0 delta(1-lambda) in the b0-bracket convention.
- **Live line 25 certifies both claims** with the correct sign. The parsed expected slope `(-b0)(-2lam(dl-dl/lam))` equals -b0 times the certified y-coefficient, so line 25 contradicts the disabled line 23.
- **The constant term is never used.** It is an absorbed scalar.
- **`outer/check_ledger.py` does not touch the identity.**
  - It imports only fractions, decimal, pathlib, math, hashlib, json, sys and gmpy2.
  - It never names `check_gaugefree` and has no `dl`, `b0`, `claim` or `sub` symbols.
  - Its only `lam` is the supplier lambda = 1-(q_+a)/2 at line 126.
- **`outer/run_outer.py:19` is the only reference** to the script in any `*.py`. It runs `check_gaugefree.py` as a pass/fail subprocess with stdout discarded, and the script writes nothing.

PR1876's supplemental `check_broad_shift.py` is not in #2044, so the release still ships the wrong disabled expression.
Fix: make line 23 live with the correct bracket, or delete it.

**Minor gaps.**
- **Stage B covers only s = -dl/lam.** The "600 exact rational mixed-difference checks" (`GAUGEFREE-INTERIORS.md:30`) all use `S=-D/L` (`check_gaugefree.py:53`). Separability for every s follows from live line 21, which has no x*y term (certified).
- **The narrow kernel completion is not asserted.** k(h) = e^{a be0^2/rho} e^{-gamma(h-s)^2} appears only as an OUT string (`check_gaugefree.py:36`). It is certified here, together with 1-2|s| >= theta/rho >= theta/2.
- **Constants only.** `GAUGEFREE-INTERIORS.md:31` gives the summed linear range as "<= 2 b0 theta B (total)", and `:84` gives "<= 2 b0 theta B'". The exact sum is 3 b0 theta B/(1+theta), which is larger than 2 b0 theta B for theta < 1/2. Each axis separately is <= 2 b0 theta B, and Section 5 (`:92`) uses 4 b0 theta B, so the exponents are unaffected.
- **A second vacuous assertion.** `outer/struct_check.py:130` also ends in `or True`; it is the only other one in `outer/*.py`. It belongs to the structured boundary, which does not enter kappa (`outer/FINE-PADDING-COMPOSITION.md:13`).
- **Undocumented dependencies.** `check_gaugefree.py:12` imports sympy, mpmath and numpy. `README.md:16` mentions only SymPy, and only for the vendored PR1673 checks.

Also certified exactly:
- Lemma 2.1 (general s, no cross term);
- Lemma 2.2;
- the normalisation identity;
- the old-weights identities (`check_gaugefree.py:40`, `:42`);
- the shrunk-shift coefficients 4 dl theta/(1+theta) and -2 dl theta/(1+theta), together with |cx| <= 2theta, |cy| <= theta and 1-2|s| >= theta.

## Item 2: per-record g^2 / g|F| / 2beta / g-fold charges at the final point

Final point: rebuilt from `POINTS.json` (11 SHA-256 fingerprints).
- eps = 1-2r, beta = 1-6r, r = r0 = 1e-30010, zeta = 1e-30012.
- xi = eps(1+q) - 3/32 + r = 0.9079...
- kappa = floor(eps q 10^30046)/10^30046 - 1e-30022, so 0 < eps q - kappa < 1e-30020.

A condition holds iff its value is > 0. Values are exact; the closed forms are checked by `review_items.py`.
`V/` = `vendor/pr1673/capped-phase-fusion/`. `FPP` = `vendor/pr1786/FINE-PRIME-PADDING.md`.

**Superseded (false at the final point; a rejecting control in `outer/LEDGER.json` fires for each).**

| id | charge | file:line | condition | value | control |
|---|---|---|---|---|---|
| U1 | old union row (g-fold scan of U, g^2 per window) | V/PHASE-LAYOUT-AUDIT.md:4,86,103-108,229; V/CAPPED-SIGNOFF.md:30-31; V/CAPPED-INTERIORS.md:38,41; V/OUTER-AUDIT.md:86; V/MATRIX-LAYOUT-SIGNOFF.md:19-21,31-33; outer/UNION-SCHEDULE.md:17-18,98,110,122; outer/RECT-BOUNDARY.md:65; outer/FINE-PADDING-COMPOSITION.md:12; outer/check_ledger.py:139 | 1-(eps+beta+1/2-xi)-kappa | -19/32+7r+(eps q-kappa) = -0.5937 | `old_g_factor_union_row` |
| U2 | g\|F\| <= g^2 tag work charged to one record | outer/GAUGEFREE-INTERIORS.md:17,103-104,110; outer/UNION-SCHEDULE.md:103,124; outer/RECT-BOUNDARY.md:66; outer/FINE-PADDING-COMPOSITION.md:12; FPP:266; outer/check_ledger.py:193,220; verify_release.py:112 | 1-2beta | -1+12r | `old_union_tag_2beta` |
| U7 | full-key sort surcharge (V/CAPPED-SIGNOFF.md:49 "remains below the target" is stale) | V/CAPPED-SIGNOFF.md:49-50; V/OUTER-AUDIT.md:87; V/CAPPED-INTERIORS.md:43,64; V/MATRIX-LAYOUT-SIGNOFF.md:34-35 | (xi+1/2-eps)-(beta+1-eps)-kappa | -19/32+5r+(eps q-kappa) = -0.5937 | `full_key_sort` |
| U11 | g a d precision bits | V/TENSOR-COMPILER.md:25-27; V/LOG-A-PHASE-SCHUR-AUDIT.md:112; V/SUPPLIER-SUPPORT-AUDIT.md:109 (superseded per V/CAPPED-GAUGE-AUDIT.md:67,107); outer/check_ledger.py:190 | 1-(beta+eps) | -1+8r | `full_cell_gauge` |
| U12 | linear gauge g a B | V/CAPPED-GAUGE-AUDIT.md:99-107; V/CAPPED-INTERIORS.md:68; outer/GAUGEFREE-INTERIORS.md:17 | 1-xi-r-beta | -0.9079 | `old_linear_guard` |
| U13 | GAUGEFREE bold guard beta+2xi-eps <= 1-r-zeta | outer/GAUGEFREE-INTERIORS.md:17,93-95,101; superseded per :1 and outer/FINE-PADDING-COMPOSITION.md:46 | 1-(2xi-eps)-r-zeta-beta | -0.8159 | `old_theta_chirp_guard` |

**Active and encoded (true; each is equal to a `check_ledger.py` strict-check row, recomputed and compared with LEDGER.json).**

| id | charge | file:line | condition | value | ledger row |
|---|---|---|---|---|---|
| U3 | tag O(g) per visit; header O(g log L) | outer/UNION-SCHEDULE.md:11,46-47,58,103; outer/GAUGEFREE-INTERIORS.md:110; FPP:264-266; V/PHASE-LAYOUT-AUDIT.md:119-120 | 1-beta | 6r | `union_tag_work_per_visit_fits_record`, `union_header_fits_record` |
| U4 | new union row (no g^2, no per-axis scan) | outer/UNION-SCHEDULE.md:94-98 | xi+1/2-eps-kappa | 13/32+r+(eps q-kappa) = 0.4063 | `sparse_union_movement_above_kappa` |
| U5 | membership g h^2 per record | V/PHASE-LAYOUT-AUDIT.md:123-130,177; V/CAPPED-SIGNOFF.md:44-47; V/CAPPED-INTERIORS.md:64; V/MATRIX-LAYOUT-SIGNOFF.md:20 | 1-beta-2(1-eps) | 2r | `membership_arithmetic_fits_record` |
| U6 | group key g h | V/CAPPED-SIGNOFF.md:48; V/OUTER-AUDIT.md:62,76; V/HALO-THEOREM.md:31,150 | 1-(beta+1-eps) | 4r | `group_key_fits_record` |
| U8b | halo metadata K0^2 within the p^2 face allowance | V/HALO-THEOREM.md:44,150-157; V/CAPPED-INTERIORS.md:43 | 2-2(beta+1-eps) | 8r | 2 x `group_below_dimension` |
| U8c | halo metadata term (explicit-metadata branch) | V/HALO-THEOREM.md:44 | 1-kappa-[(eps-beta)+(beta+48-128)+2(beta+1-eps)-1] | 79+10r-kappa | covered by the face row |
| U9 | g sequential passes on halo copies (g^2 A/L) | V/OUTER-AUDIT.md:58-62,89; V/PHASE-LAYOUT-AUDIT.md:213-219; V/HALO-THEOREM.md:185-186; V/CAPPED-INTERIORS.md:43; V/CAPPED-SIGNOFF.md:63-65; FPP:230-233; outer/check_ledger.py:137 | 1-(eps+beta+48-128+2)-kappa | 77+8r-kappa | `microbox_face_corrections_above_kappa` |
| U10 | support router O(g polylog p) | V/CAPPED-SIGNOFF.md:52-57; V/CAPPED-INTERIORS.md:66; V/SUPPLIER-SUPPORT-AUDIT.md:121; V/SUPPORT-ADVERSARIAL-AUDIT.md:189-200,227; outer/UNION-SCHEDULE.md:123 | 1-beta | 6r | `support_router_span` |
| U14 | fine chirp g a theta B^2 | outer/GAUGEFREE-INTERIORS.md:1,41,94; FPP:163-169 | 1-(2xi-2)-r-beta (also with -zeta, outer/GAUGEFREE-INTERIORS.md:95 form) | 0.1841 | `group_gauge_power_slack` |
| U15 | linear leftover dominated by the chirp | outer/GAUGEFREE-INTERIORS.md:96,101 | xi > 0 (via xi-1/2) | 0.4079 | `cap_above_band` |

The §6.1 row names `shift_leftover_linear_dominated_by_chirp` and `shift_gap_theta_polynomial` are absent from LEDGER.json.
Their conditions are implied by `cap_above_band` and `theta_positive_polynomial_power`.

**False option (must not be the branch used).**
- U8a: `V/HALO-THEOREM.md:31-32` offers "Require `K0^2=O(B)`", where K0^2 = g^2 h^2. The condition 1-2(beta+1-eps) evaluates to -1+8r, so it is **false**.
- The package should state that it uses the explicit-metadata alternative at `V/HALO-THEOREM.md:44` (U8b/U8c), which holds because eps > beta.

**Non-exponent obligations** (listed, not evaluated):
- the head-travel bookkeeping of UNION-SCHEDULE §2.3 (`outer/UNION-SCHEDULE.md:85`) and the requirement that every visit moves the full record;
- `outer/GAUGEFREE-INTERIORS.md:96` still says "a d = o(p)". Under fine theta the offline term a/theta ~ a p^2 is moved to an amortized P_setup (`FPP:159-187`);
- Theorem 4.1 rests on SHALLOW-TOEPLITZ (`outer/GAUGEFREE-INTERIORS.md:72`);
- the dependencies of `check_gaugefree.py` (see Item 1).

**Stale numeric text** (anchors checked): `outer/STRUCTURED-BOUNDARY.md:97`, `V/CAPPED-SIGNOFF.md:63-65,75-78`, `V/PHASE-LAYOUT-AUDIT.md:128-130` (assumes g = p^(1-epsilon-r-zeta) and epsilon > 2/3), `V/SUPPORT-ADVERSARIAL-AUDIT.md:189-227`, `outer/RECT-BOUNDARY.md:65-66`, `outer/GAUGEFREE-INTERIORS.md:105,117` (labelled pkg8-era).

**Conclusion.** No active step charges g^2 or g|F| against one p-bit record.
- **Union schedule.** The worst-case total tag work g|F| <= g^2 per record does exceed one record (2beta > 1). It is paid per visit instead: each visit moves the record at Theta(p), so only beta < 1 is required, and that is encoded.
- **Halo/core-face path.** The g^2-type charges that remain active sit on this path, which carries sparse volume p^(beta-80); they fit with a margin of about 77.
- **One false condition to fix.** The HALO "K0^2 = O(B)" option is false at the final point and should be disowned in the text.

**Prior and concurrent work.** Philippe Van Velzen (philippeVV) posted an independent exact broad-shift reconciliation
for this head before this audit. It is a #1897 comment from 2026-10-14 19:40 UTC (fork
`philippeVV/integer-mult-bounds@a3c40a6f`, `research/t74-broad-shift-reconcile/`), and it reaches the same Item 1
conclusion, including the 3b₀θB correction to :31/:84. His #2044 comments of 2026-10-15 also report the HALO
`K₀² = O(B)` issue. This file corroborates both with a different method: an exact Laurent certificate, without sympy.
