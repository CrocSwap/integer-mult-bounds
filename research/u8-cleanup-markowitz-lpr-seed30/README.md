# Two-Sided Markowitz $R^{-1} P L^{-1}$ Cleanup Refactorization for the Selected U8 Complex Supplier Word (`seed = 30`)

- **Track & Seed:** `20–39: Complex supplier: improve one specific circuit, frame schedule, decoder, or paid recursive profile` (OS random seed: **`30`**)
- **Base Commit:** `abdc6a7002abdbcd9e21bfc5e1a795784deacfdf`
- **Selected Frontier Certificate:** `certificates/selected-result.json` (conditional $\kappa = 1661960547713947 / 10^{18} = 0.001661960547713947$, PR #942 on PR #869/#870 and PR #890 / PR #858; **unchanged by this package**)
- **Status:** Finite circuit improvement (`no new kappa`) + scoped negative result on partial $E_4 \to E_5$ entrance-promotion reversion

---

## 1. Concise Summary of What Changed and Was Learned

In the selected U8 complex supplier word (`native/barch/FULL-WORD.json.gz`, content SHA-256 `090fd574747fbf9628e70cb9beb792732914cfa52e1df147579fe4dbccc68c5a`; `native/local/CANONICAL-WORD.json.gz`, content SHA-256 `24db880b7dab31e6af4eec8a1aba1bbbae29cd50d9a7b77cf0e9b571b3e5ae7c`), the `full_frame_cleanup` section (`canonical['cleanup']`, running at frame `1` = `FULL` on the $490$ `FULL`-ended non-target registers) was originally synthesized by `cold44x.py` via one-sided (row-only) Gauss-Jordan elimination (`high_inverse = "dyadic_sparse_Gauss_Jordan"`) on $M_{\text{after}} = M_0^{-1}$ in fixed register index order $c = 0, 1, \dots, 727$.

We show that while $M_{\text{after}}$ has $9,430$ off-diagonal nonzeros, the target cleanup operator $M_0 = M_{\text{after}}^{-1} \in GL_{728}(\mathbb{Z}[1/2])$ itself has **only $2,844$ off-diagonal nonzeros**, all with numerators in $\{\pm 1, \pm 2, \pm 3, \pm 4\}$ and denominators in $\{1, 2, 4\}$. One-sided elimination in fixed index order caused severe fill-in ($6,105$ scalar macros, $68,714$ real-component primitives per orientation), coefficient blowup up to $\max |\text{num}| = 131,646$, and a $72$-bit peak prefix $L_1$ coefficient norm (`48299247708521178587951/16`) in the backward orientation.

Replacing one-sided Gauss-Jordan elimination with a **two-sided Markowitz $R^{-1} P L^{-1}$ Schur-complement factorization and Weyl-group signed cycle realization** (`seed = 30`, `trial = 16`, `swap_pen = 6`, `scale_pen = 0`) achieves the following exact improvements across the U8 complex supplier word while preserving all $728$ columns, native frames, paid recursive profile, and residual adapter recipes:

| Metric | Baseline U8 (`dyadic_sparse_Gauss_Jordan`) | Refactored U8 (`two_sided_Markowitz_LPR_Weyl_seed30`) | Exact Change |
| :--- | ---: | ---: | ---: |
| `full_frame_cleanup` scalar macros (per orientation) | `6,105` (`6,005 add + 100 scale`) | **`3,525`** (`3,355 add + 170 scale`) | **`-2,580` (`-42.26%`)** |
| `full_frame_cleanup` real primitives (per orientation) | `68,714` | **`31,394`** | **`-37,320` (`-54.31%`)** |
| `full_frame_cleanup` max $\|\text{numerator}\|$ | `131,646` | **`8`** | **`16,455.75x` smaller** |
| `full_frame_cleanup` max denominator | `64` | **`8`** | **`8x` smaller** |
| Total raw scalar operations (`SCALAR-FRAME-AUDIT`) | `19,189` | **`16,609`** | **`-2,580` (`-13.45%`)** |
| Emitted events per orientation (`LOCAL-CHECKS`) | `24,415` | **`21,835`** | **`-2,580` (`-5,160` pair)** |
| Emitted scalar macros per orientation (`LOCAL-CHECKS`) | `19,213` | **`16,633`** | **`-2,580` (`-13.43%`)** |
| Forward real-component primitive bound | `193,306` | **`155,986`** | **`-37,320` (`-19.31%`)** |
| Backward real-component primitive bound | `193,354` | **`156,034`** | **`-37,320` (`-19.30%`)** |
| Forward + backward pair real-component primitives | `386,660` | **`312,020`** | **`-74,640` (`-19.30%`)** |
| Forward `prefix_l1_upper` (`prefix_bits_upper`) | `6812058044968180837/256` (`55` bits) | **`1938756620440273` (`51` bits)** | **`-4` bits (`13.7x` smaller)** |
| Backward `prefix_l1_upper` (`prefix_bits_upper`) | `48299247708521178587951/16` (`72` bits) | **`57316408753392281/4` (`54` bits)** | **`-18` bits (`210,704x` smaller)** |
| Paid recursive child profile (`local_rank_mass = 5634`) | `{1:2548, 2:338, 3:446, 4:162, 5:72, 8:8}` | **`{1:2548, 2:338, 3:446, 4:162, 5:72, 8:8}`** | **Identical (`0` delta)** |
| `RESIDUAL-ADAPTERS.json` SHA-256 | `8b06181f6983...` | **`8b06181f6983...`** | **Byte-identical** |

### Scoped Negative Finding (Candidate 1)

Before selecting Candidate 3, we tested whether reverting $m \in \{1, 2, 3\}$ helpers of the 4-helper group $G = \{659, 661, 662, 663\}$ in U8 from entrance frame $E_5 = [298, 170, 102, 30, 1]$ (dim 5) back to $E_4 = [298, 170, 102, 30]$ (dim 4) could profitably fill the 2 remaining rank-1 idle slots in T37 (after PR #1072). We proved and verified (see [`PROOF.md`](PROOF.md) Section 5) that because the 12 bipartite delivery gates `B[420..431]` into $D_G = \{656, 657, 658, 660\}$ find $D_G$ at frame dimension $1$, partial reversion $1 \le m \le 3$ splits the climb $1 \to 5$ on $D_G$ into $1 \to 4 \to 5$, yielding local profile deltas $\Delta(m=1) = \{1:+2, 2:+1, 3:+3, 4:-3\}$, $\Delta(m=2) = \{1:+2, 2:+2, 3:+4, 4:-4\}$, and $\Delta(m=3) = \{1:-1, 2:+4, 3:+4, 4:-4\}$, which strictly worsen the complex moment at $b_{\text{front}}$.

---

## 2. One Reproducible Command and Expected Result

From the repository root:

```bash
python3 -I -B research/u8-cleanup-markowitz-lpr-seed30/verify.py
```

Expected terminal output:

```json
{
  "status": "PASS_U8_CLEANUP_MARKOWITZ_LPR_REFACTORIZATION",
  "seed": 30,
  "track": "20-39: Complex supplier",
  "base_commit": "abdc6a7002abdbcd9e21bfc5e1a795784deacfdf",
  "changes_kappa": false,
  "cleanup_macros_before": 6105,
  "cleanup_macros_after": 3525,
  "cleanup_macros_saved_per_orientation": 2580,
  "cleanup_real_primitives_before": 68714,
  "cleanup_real_primitives_after": 31394,
  "cleanup_real_primitives_saved_per_orientation": 37320,
  "full_local_real_primitives_saved_pair": 74640,
  "forward_prefix_bits": {
    "before": 55,
    "after": 51,
    "delta": -4
  },
  "backward_prefix_bits": {
    "before": 72,
    "after": 54,
    "delta": -18
  },
  "independent_verifier": "PASS_INDEPENDENT_INTEGER_LATTICE_VERIFICATION",
  "negative_controls": {
    "upstream_local_rejected": 25,
    "upstream_wrapper_rejected": 17,
    "package_controls_rejected": 12
  }
}
```

The verifier is also compatible with `python3 -I -O -B research/u8-cleanup-markowitz-lpr-seed30/verify.py`.

---

## 3. Scope, Inherited Assumptions, and Unresolved Obligations

- **Scope:** Finite circuit improvement for the `full_frame_cleanup` section of the selected U8 complex supplier word (`native/barch/FULL-WORD.json.gz`), verified by both the unchanged upstream 4-stage HPE local pipeline and a code-disjoint pure-integer lattice verifier (`independent.py`), plus a 12-control adversarial mutation suite (`test_package.py`).
- **No Claim of New $\kappa$:** Because `full_frame_cleanup` executes entirely at frame `1` (`FULL`) and involves no frame climbs or recursive child calls, the paid recursive child profile `{1: 2548, 2: 338, 3: 446, 4: 162, 5: 72, 8: 8}` and the asymptotic exponent $\kappa = 1661960547713947 / 10^{18}$ are unchanged. `certificates/selected-result.json` and `upstream/` are untouched.
- **Inherited Assumptions:** All all-size and analytic bridge assumptions of `certificates/selected-result.json` remain unchanged.

---

## 4. Attribution and Disclosure

- **Contributor:** `steph4n-gh`
- **AI Assistance Disclosure:** Substantial AI assistance from **Gemini 4 Argon** (Google DeepMind / Antigravity). See [`NOTICE.md`](NOTICE.md) for complete predecessor attributions.
