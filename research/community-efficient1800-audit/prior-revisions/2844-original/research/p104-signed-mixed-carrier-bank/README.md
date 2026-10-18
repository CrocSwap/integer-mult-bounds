# P104 signed mixed-carrier research laboratory

**Status:** A tested *finite schematic construction*, **not** a completed P104 supplier, an improved conditional exponent, or a new integer-multiplication algorithm. Based on CrocSwap/integer-mult-bounds PR #968 (frame-pair decoders), PR #1125 (asynchronous terminal-read model), and PR #2820 (255 survivor-projection widths). Full predecessor attribution must be preserved.

## New mechanism

Start with eight independent term carriers `x_i` at binary frame lines `E_i = <u_i>`. For each cube edge `(i,j)`, optionally create two *redundant* carriers:

- `m⁺_ij = x_i + x_j`;
- `m⁻_ij = x_i - x_j`.

Both live on the composite line `E_ij = <u_i + u_j>` in the relaxed binary frame model. They do **not** replace the eight source carriers: they are new auxiliaries. A target that requires both i and j can use exactly one of `m⁺_ij` or `m⁻_ij`, possibly negated, instead of two separate term reads. If a target needs only one of i,j, it uses the corresponding original carrier instead. This lets targets select *different disjoint subsets of pairs*.

The crucial accessibility identity follows immediately from the reviewed P104 incidence: `E_i ⊂ H_t` exactly when `i ∈ S_t`. Therefore `E_ij ⊂ H_t` iff `i,j` are both in `S_t` **or** both outside `S_t`. In the both-in case, the signed pair-sum is a legitimate one-read *schematic* replacement for the two term contributions. `e8_instance.py` independently constructs one actual root-frame decoder and verifies this identity for all 12 edges and 104 targets, including ± coefficient signs.

## Fully priced **within the explicitly relaxed frame experiment**

Each output target starts at the zero frame and grows monotonically to its rank-eight sink. Original and precomputed auxiliary carriers begin each read at their home one-dimensional line, join the target's current frame to read, and return home. Target arithmetic uses exact integer coefficient vectors. Each pair's **two** signed auxiliaries are prepared together, adding four signed ADDs and ten frame-rank units; no part of that preparation is silently omitted. All finite moves are charged by `d(U,W) = dim U + dim W − 2 dim(U∩W)`.

| Finite schedule | Target ADDs | Mixer ADDs | Total ADDs | Target sink frame rank | Source reposition rank | Mixer preparation rank | Total frame rank | Extra auxiliary carriers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Eight unmixed originals, return home | 416 | 0 | **416** | 832 | 1,392 | 0 | **2,224** | 0 |
| One fixed perfect matching of four cube edges | 304 | 16 | **320** | 832 | 648 | 40 | **1,520** | 8 |
| Eight selected cube edges (16 auxiliaries) | 256 | 32 | **288** | 832 | 416 | 80 | **1,328** | 16 |
| All twelve cube edges (24 auxiliaries) | 240 | 48 | **288** | 832 | 360 | 120 | **1,312** | 24 |

The last row is optimal for the **12-edge bank-subset class and stated frame invoice**: exhaustive evaluation of all `2^12 = 4096` subsets finds mask 4095 the **unique** minimum-frame-rank bank. The minimum ADD count 288 ties with certain smaller banks. A separate vertex-recursion optimizer independently corroborates all 4096 cases. No optimality beyond the two-signed-variant cube-edge-bank model is claimed. The eight-edge solution wins over the twelve-edge solution when each auxiliary helper has even a small positive price (two or more frame-rank-equivalent units), so actual host/tape costs matter.

### Relative to this one restricted baseline

- All-edge bank: **30.77% fewer ADDs**, **41.01% less charged frame-move rank**.
- Eight-edge bank: same 30.77% ADD savings with 16 auxiliaries, but 16 more frame-rank units than the 12-edge bank.
- These percentages **are not** savings in multiplication runtime, actual P104 recursive cost, or a review-accepted κ.

## Separate structural result: why eight global replacement carriers fail

For unsigned outputs `y_S = Σ_{i∈S} x_i`, suppose we replace all eight original independent carriers by exactly eight new independent fixed home-line carriers, with no redundant channels, and each target reads only carriers whose line lies in its sink. For any proposed line `v` from the eight-dimensional source span, its coefficient functional must vanish on all targets `S` for which `<u_t,v> != 0`. The unsigned target coefficient vectors of those forbidden targets have rank **eight over the rationals** for each of the **247 non-coordinate** lines `v`. The other eight coordinate lines have rank seven. Therefore a nonzero fixed coefficient functional exists only at an original coordinate line: an invertible, fixed eight-channel recoding cannot beat the direct-home accessibility requirement in this precisely stated class. A full-rank minor over F₃ is a short exact rational certificate; `independent.py` independently checks all ranks with SymPy over Q.

This no-go result does not apply to the **redundant signed dictionary**, to unequal geometry-dependent coefficients, to moving frames, or to target-specific encoding.

## Reproduce this GitHub submission

The upstream contribution contains the primary standalone standard-library verifier, a 4096-bank invoice census, the E8 root-line gate, and two further zero-restored construction checkers.

From the repository root, Python 3.10+:

```bash
python3 -I -B research/p104-signed-mixed-carrier-bank/RUN_SUBMITTED.py
```

Expected final line:

```text
PASS_P104_SCHEMATIC_SUBMISSION no_kappa no_native_supplier
```

The committed checks emit:
- `verify.py`: 2288 signed target configurations, 105 perfect matchings, abstract scalar/frame traces, 247 forbidden static noncoordinate line choices.
- `optimize_bank.py`: every one of 4096 edge banks, unique minimum-frame rank 1312, total ADDs 288.
- `root_line_gate.py`: all 7140 distinct E8 root-line pairs have pair-sum labels absent from the root-line family.\n- `zero_restore.py`: exact rank-one mixed helper cleanup after all outputs.\n- `rank2_gate.py`: exact rank-two framed alternative, full helper cleanup and signed cases.

These are the reviewable checks committed in this PR. The expanded local laboratory was also exercised with separate optimization, E8-example and negative-control scripts, but those auxiliary scripts are **not included** in this focused GitHub submission; the PR makes no claim that its committed runner executes them. The selected frontier and `upstream/` are unchanged.

## Stronger zero-restored constructions added in this PR

The first one-dimensional composite-label bank is a schematic relaxation. `root_line_gate.py` proves that no sum of two distinct E8 root labels is itself an E8 root label.

- `zero_restore.py` reverses every rank-one mixer preparation and zeros all 16 helper values. The exact full-bank audit chooses an eight-edge bank (one of six equivalent minima), costing **320 ADDs and 1408 rank units**, with zero-restored auxiliary endpoints. New composite rank-one physical labels remain unimplemented.
- `rank2_gate.py` instead keeps each mixed scalar on the *rank-two* span of its two genuine root lines, which is included in a target sink whenever both originals are read. It also restores every helper to zero. Exhaustive 4096-bank search and 2288 signed cases give **320 ADDs and 1520 rank units** with 16 auxiliaries, versus 416 / 2224 for the fixed unmixed baseline.

Neither route establishes a valid native E8 scalar operator, paid source/phase routing, hosting or new recursive exponent. The rank-two variant removes the nonexistent-root-line naming obstacle, not the full realization obligation.

## Critical remaining gates before claiming a new integer multiplication result

1. **Physical lowering:** construct a valid register word realizing new line `E_i+E_j` and preserving scalar information and frame phase. The abstract frame move alone does not establish physical realizability.
2. **Full paid invoice:** account for source access, both signed auxiliaries' construction, all source/copy/erase/restore work, helper provisioning, live width, recursive children, all phase changes, and eventual cleanup of auxiliary data (this experiment permits them to terminate with data).
3. **Competitive baseline:** compare with an optimized unrestricted *unmixed* delivery word and the currently accepted P104-related constructions, not merely this fixed return-home schedule.
4. **Finite/native semantics and full geometry:** replay every required original signed decoder, not only supports and one concrete E8 instance.
5. **Moment/outer requirements:** show a strict gain under the current selected certificate and all analytic, compiler, hosting, bit-interface, and precision assumptions. The previously reviewed P104 optimistic budget is extremely tight; nominal savings here do not imply a positive κ.

**Attribution/license:** Prepared with substantial OpenAI GPT-6 assistance. Concept and finite construction developed in this sprint; prior P104 geometry/theorem: Ali Romman (#1125), decoder constraints: #968 and predecessors, 255 projections: Chrisbryan17 (#2820). Research package offered under Apache-2.0, with upstream sources unmodified. No human review of this new construction is claimed.