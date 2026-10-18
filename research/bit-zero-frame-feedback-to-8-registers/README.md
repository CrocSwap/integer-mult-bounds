# Zero-frame target feedback: every shape with at most eight registers

**Finite exact negative result plus a uniform lemma. No new supplier or κ.**

In the model of [bit-zero-frame-feedback](../bit-zero-frame-feedback/README.md) (PR1306), consider
the fully restored dirty shear `(h, y) -> (h, y + K h)`:

* `H` helpers and `T` targets, all inputs arbitrary;
* unit-cost single-source XORs;
* no extra registers.

Allowing targets to feed helpers **never lowers the minimum gate count for any shape with
`H + T ≤ 8`.** This package certifies the four shapes no predecessor covered (2×4, 2×5, 2×6, 3×5).
It adds a lemma that settles `H = 1` and `T = 1` at every size, and a duality that covers
transposes. With PR1306, PR1557 and PR1706, the eight-register domain is closed. That answers the
open question of [bit-zero-frame-feedback-4x4](../bit-zero-frame-feedback-4x4/README.md).

## Where each shape is settled

Shapes are listed up to transpose (`H×T` and `T×H` are equivalent; see Duality below).

| Registers | Shapes | Settled by |
|---:|---|---|
| ≤ 6 | 1×1 … 3×3 | PR1306 (all `1 ≤ H, T ≤ 3`) |
| 5, 6, 7, 8 | 1×4, 1×5, 1×6, 1×7 | the uniform lemma below (every `1×T` and `H×1`) |
| 6 | 2×4 | **this package** |
| 7 | 2×5 | **this package** |
| 7 | 3×4 | PR1557 |
| 8 | 2×6, 3×5 | **this package** |
| 8 | 4×4 | PR1706 |

## Certified results

For every labeled `K` of each shape, the restricted and unrestricted minima are equal:

| Shape | K | Orbits | Minimum-cost histogram (0, 1, 2, …) | Max |
|---|---:|---:|---|---:|
| 2×4 | 256 | 22 | 1, 8, 28, 56, 70, 60, 33 | 6 |
| 2×5 | 1,024 | 34 | 1, 10, 45, 120, 210, 262, 245, 131 | 7 |
| 2×6 | 4,096 | 50 | 1, 12, 66, 220, 495, 812, 1,039, 978, 473 | 8 |
| 3×5 | 32,768 | 190 | 1, 15, 105, 455, 1,365, 3,043, 5,340, 7,483, 8,090, 6,181, 690 | 10 |

Every `K` is resolved within the exact horizon of `2R` gates, with `R = 4` for six registers and
`R = 5` above. Orbits are taken under target and helper permutations.
[CERTIFICATE.json](CERTIFICATE.json) has, per shape:

* the cost of every `K` (`costs_hex`, indexed by `K[i][j]` = bit `iH + j`) and its SHA256;
* the sphere sizes;
* one attaining restricted word per orbit, each replayed on all dirty inputs.

The search is PR1706's coset meet-in-the-middle, and its exactness argument applies unchanged. Two
balls are grouped by cosets of the shear group, keyed by the helper rows plus the target rows
reduced modulo their span. Pairs whose depths differ by at most one suffice, because both halves of
a geodesic are geodesic.

## Uniform lemma: one helper or one target

**Lemma.** If `H = 1` or `T = 1`, both minima equal the number of ones in `K`, for every size.

**Proof.** Each gate is `E = I + e_d e_s^T` and reads only its source `s`.

* *Lower bound when `T = 1`.* If no gate has source `j`, every factor fixes `e_j`, so the product's
  column `j` is `e_j`. But helper column `j` of `T_K` is `e_{h_j} + Σ_i K_ij e_{y_i}`. So every
  helper with a nonzero column of `K` is the source of at least one gate. Each gate has one source,
  so at least `wt(K)` gates are needed.
* *Lower bound when `H = 1`.* Dually, a register that is never a destination keeps its row `e_i^T`.
  So every target with a nonzero row is the destination of at least one gate, again giving at least
  `wt(K)` gates.
* *Upper bound.* In both cases the direct circuit `y_i ^= h_j` for each one in `K` uses `wt(K)`
  gates and is restricted.

Feedback is allowed throughout, so the bound holds in both alphabets. ∎

The `controls` stage checks the lemma against exhaustive censuses for 1×4, 1×5, 1×6, 4×1, 5×1 and
6×1 in both alphabets. The histograms are binomial, as predicted.

## Duality: H×T and T×H

`M -> M^-T` maps the gate `(d, s)` to `(s, d)` and preserves word length. It maps `T_K` to
`[[I, K^T], [0, I]]`. Exchanging the roles of helpers and targets turns that into the shear `T_{K^T}`
of shape `T×H`. A forbidden gate (helper destination, target source) maps to (old target
destination, old helper source), which after relabeling is again a helper destination with a
target source. So `cost_{H×T}(K) = cost_{T×H}(K^T)` in each alphabet.

The `controls` stage checks this elementwise for 2×5 against 5×2 (all 1,024 `K`, both alphabets).

## Independent evidence and controls

[independent.py](independent.py) imports nothing from `verify.py` or any predecessor. It uses
column-packed matrices and per-orbit lower bounds by direct lookup of `T_K X` in unrestricted balls,
with no coset grouping. An unrestricted lower bound also bounds the restricted alphabet. It
transports each orbit witness by register renaming to all 38,144 labeled `K` and replays each on
every dirty input.

**Primary controls:**

* the PR1306 3×3 histogram is reproduced in both alphabets, read from its pinned certificate;
* a radius-4 census leaves 3×5 unresolved;
* permutation invariance of all costs;
* five witness-rule rejections: truncated word, wrong map, a cancelling feedback pair (accepted only
  unrestricted), self-XOR, and a Boolean index.

Both scripts refuse to run under `-O`.

## Reproduce

Python 3.12 with `numpy==2.4.0`, from the repository root:

```sh
python3 scripts/research_package.py --package research/bit-zero-frame-feedback-to-8-registers --check-only
python3.12 scripts/research_package.py --package research/bit-zero-frame-feedback-to-8-registers --install-deps
```

The registered replay runs three commands. On the donation host (Windows 11, CPython 3.14, numpy
2.4.0) they took about 2.3, 0.7 and 2.0 minutes:

```sh
python3 -I -B research/bit-zero-frame-feedback-to-8-registers/verify.py --stage census
python3 -I -B research/bit-zero-frame-feedback-to-8-registers/verify.py --stage controls
python3 -I -B research/bit-zero-frame-feedback-to-8-registers/independent.py
```

Expected lines:

```text
PASS_ZERO_FRAME_FEEDBACK_TO_8_REGISTERS shapes=2x4,2x5,2x6,3x5 feedback_gains=0 no_new_kappa
PASS_ZERO_FRAME_FEEDBACK_TO_8_REGISTERS_CONTROLS lemma=H1/T1 duality=2x5/5x2 pr1306=3x3
PASS_INDEPENDENT_ZERO_FRAME_FEEDBACK_TO_8_REGISTERS 2x4:22 2x5:34 2x6:50 3x5:190 feedback_gains=0
```

`verify.py --write` regenerates the certificate deterministically. CPython 3.12 was unavailable on
the host, so the registered 3.12 replay was not run locally. PR1706's identical numpy-pinned setup
passed the maintainers' replay.

## Limits

This covers only `H + T ≤ 8`, the lemma's `H = 1` / `T = 1`, F2, PR1306's two unit-cost
single-source alphabets, and no extra registers.

* **Out of scope:** larger shapes, other costs, multi-source gates, nonzero frames and other fields.
* **Not built or checked:** physical precision, hosting and supplier pricing.
* **Unchanged:** the selected frontier.

## Open next questions

1. **Does equality hold at nine registers (2×7, 3×6, 4×5), or in general?**
   * *Why it matters:* a general no-feedback theorem would close this D-local relaxation for every
     prefix size: every restored shear endpoint would have a shortest unit-transvection
     word staying in the restricted block-lower-triangular subgroup. This does not by itself
     establish geodesic convexity for all endpoints in that subgroup.
   * *First step:* 2×7. Its expected maximum (about 9–10) should fit a radius-5 census once
     matrices are packed into two 64-bit words.
   * *Blocked by:* 3×6 and 4×5 need radius-6 unrestricted balls or a new reduction, and no proof
     beyond the one-helper/one-target lemma is known.

## Credit

* **@commdata2338 (PR1306):** the model, the substitution lemma and the meet-in-the-middle setup.
* **@bbMisk (PR1557):** the 3×4 census.
* **PR1706 (this account):** the 4×4 census and the coset method reused here.
* **Lineage:** the semantic-D and bit-word lineage credited in those packages is retained.

No predecessor code is imported; the PR1306 certificate is read as a pinned control input.
Prepared for rtyu193-rgb with Claude Code (Anthropic Claude Opus 5.5) in one session, with no
subagents and no independent human review. Apache-2.0.
