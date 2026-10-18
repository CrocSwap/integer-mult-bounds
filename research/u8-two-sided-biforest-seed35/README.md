# Two-sided signed bi-forest U8 compensation: 5,906 real primitives beyond target-forest floor

**Finite complex-supplier circuit construction; no new $\kappa$.** On the selected
U8 complex word (`native/local/CANONICAL-WORD.json.gz` in
`research/community-frontier942-audit/t37-replay.tar.gz`, bound by
`research/gauge44-barch/construction/barch/LOCAL-PINS-barch-U8.json`), an
alternating **two-sided signed bi-forest**—pairing a deepest-first signed target
forest with a **leaf-before-parent helper-accumulating signed forest**—reduces
the frame-zero compensation panel from **6,320 to 1,780 additions** and from
**34,728 to 7,930 component primitives** (**69,456 to 15,860 real primitives**).

The complete U8 local scalar programs save **53,596 real-component primitives per
orientation**:
- **5,906 real primitives beyond the 10,883 component-primitive target-only forest floor**
  established by Ross Richardson ([PR932](https://github.com/CrocSwap/integer-mult-bounds/pull/932))
  and proved unbreakable by target-only dyadic forests in woklerx
  ([PR961](https://github.com/CrocSwap/integer-mult-bounds/pull/961)).
- **2,074 real primitives beyond transporting Ross Richardson's disjoint helper-pair
  method** ([PR917](https://github.com/CrocSwap/integer-mult-bounds/pull/917)) to U8
  (`8,967` component primitives).
- **886 real primitives beyond a single target-then-helper bi-forest pass**
  (`8,373` component primitives) via alternating MST refinement to the coordinate-wise
  fixed point `(T5, H5)`.

| Complete U8 scalar program | Baseline | Target-only floor (PR932/PR961) | Target forest + disjoint helper pairs | Two-sided signed bi-forest `(T5, H5)` | Total saving vs baseline | Saving beyond target floor |
|---|---:|---:|---:|---:|---:|---:|
| Panel component primitives | 34,728 | 10,883 | 8,967 | **7,930** | 26,798 | **2,953** |
| Forward real primitives | 193,306 | 145,616 | 141,784 | **139,710** | **53,596** | **5,906** |
| Inverse-transpose real primitives | 193,354 | 145,664 | 141,832 | **139,758** | **53,596** | **5,906** |
| Scalar macros, either orientation | 19,213 | 15,217 | 14,960 | **14,673** | **4,540** | **544** |

These are exact circuit counts. Every source access, binary-Horner coefficient
preparation, target and helper basis preparation and restoration, private scratch
clear, and unchanged scalar operation is charged. The paid recursive child
histogram (`{1: 2548, 2: 338, 3: 446, 4: 162, 5: 72, 8: 8}`, 3,574 children),
all non-scalar events, helper inventory, and physical frames are unchanged. All
504 helpers restore at the complete local endpoint. Positive prefix bounds are
`1272245877576558407/16` (**57 bits**, vs 55 baseline) forward and
`204764373028968404875897/32` (**73 bits**, vs 72 baseline and 74 target-only
forest) backward—both strictly below the inherited **192-bit local allowance**.
Maximum exact symbolic denominator powers remain **3 forward and 19 backward**
across every intermediate primitive.

## Reproduction

From the repository root, with Python 3.10+ and its standard library:

```sh
python3 -I -B research/u8-two-sided-biforest-seed35/verify.py
```

Expected final line:

```text
PASS_U8_TWO_SIDED_BIFOREST target_edges=100 helper_edges=148 panel=34728->10883->8967->8373->7930 saved_real=53596 additional_vs_target_floor=5906 additional_vs_disjoint_pairs=2074 columns=728+9 orientations=2 controls=12+25 no_new_kappa
```

The default command checks `RECIPE.json` and `EXPECTED.json` without rewriting
them. It recomputes the entire alternating bi-forest search and disjoint-pair
comparator, verifies coordinate-wise MST optimality at `(T5, H5)` using an
independent Prim implementation and all `12,544 + 46,656 = 59,200` cycle-exchange
inequalities, replays both complete original and candidate programs on all 737
arbitrary input columns under both `Fraction` and sparse integer-dyadic arithmetic,
runs the unchanged native U8 emitter and auditor (`hpe_emit_local.py`,
`hpe_audit_local.py`) in a temporary directory, and executes 12 package-level
plus 25 native negative controls.

## What is new, and what is inherited

1. **Arbitrary-depth leaf-before-parent helper-accumulating forests:**
   Earlier two-sided compensation restricted the helper basis to disjoint pairs
   (David Awad [PR807](https://github.com/CrocSwap/integer-mult-bounds/pull/807),
   Ross Richardson [PR917](https://github.com/CrocSwap/integer-mult-bounds/pull/917))
   or depth-1 stars (Sricharan Vagvala [PR967](https://github.com/CrocSwap/integer-mult-bounds/pull/967))
   to avoid cascading cross-terms in $H^{-1}$. In [PROOF.md](PROOF.md) we prove
   that for *any* rooted signed forest $F_H$ of arbitrary depth and branching,
   executing `h[p(b)] += s_b * h[b]` in **leaf-before-parent (bottom-up)** order
   yields $H^{-1} = I - \sum_{i=1}^{e_H} s_{b_i} e_{p(b_i)} e_{b_i}^T$ with
   **zero ancestor cross-terms**, because $b_i \neq p(b_j)$ for all $i < j$.
   Right-multiplying $D = T C$ by $H^{-1}$ replaces each nonroot column $b$ by
   the pure two-column difference $D_{\cdot, b} - s_b D_{\cdot, p(b)}$, reducing
   the helper basis search for fixed $T$ to an exact superroot MST over all
   `46,656` signed helper edges and allowing $e_H = 148 > 216/2 = 108$ edges
   (maximum edge depth 7).
2. **Alternating MST coordinate descent to a two-sided fixed point:**
   Because $(T C) H^{-1} = T (C H^{-1})$, fixing $H$ makes target-forest
   optimization an exact MST on $C H^{-1}$, and fixing $T$ makes helper-forest
   optimization an exact MST on $(T C)^T$. Starting from the `10,883` target-only
   forest $T_0$, five alternating iterations reach the strict coordinate-wise
   MST fixed point `(T5, H5)` at **7,930 component primitives** (`10,883 -> 8,373 -> 8,220 -> 8,107 -> 8,095 -> 8,021 -> 8,008 -> 7,962 -> 7,946 -> 7,930`).

The exact base commit is **`2921874911956718fcaaaf9396fe8267b3cfa9f0`**, where the
selected conditional frontier is PR942 ($\kappa = 0.001661960547713947$).
See [PROOF.md](PROOF.md) for the algebraic identity and pricing table,
[CLAIM.md](CLAIM.md) for the sprint claim and candidate comparison,
[VALIDATION.md](VALIDATION.md) for executed checks, and [NOTICE.md](NOTICE.md)
for contributor attribution and AI-assistance disclosure.
