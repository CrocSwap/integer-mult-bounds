# One native word for both sides: the joint supplier cannot beat the average of the two invoices (negative result)

`research/kappa01-outer-repair` §2 leaves a door open: a self-contained supplier that implements the address interchange
and the butterfly layer in one native call removes the separate bit endpoint, and the outer assembly then admits
`a = b = s` for its joint saving `s`, with the scoped limit `κ < s/(1+s)`. The natural hope is that such a word adds the
credits of the two sides while the large neutral work (idle stages, local small jobs) is done once, so that
`C_joint ≈ (S_complex + S_bit) / G_shared` could exceed both sides.

**Result: on the current p16 controller this cannot happen.** Any joint ledger that respects the rank-mass identity of
the admission has a saving between the two side roots, at most **0.003232** (+7.0% over the selected 0.00302015 of
#4470), which is **below the BIT gate 0.003475458** (+15.1%) that an ordinary complex-side improvement already reaches.
The selected κ and the BIT admission are unchanged. The script runs in seconds on the standard library.

## The two invoices side by side

| | complex #4470 (`joint-helper-lattice/RESULT.json`) | BIT #4814 (`bit-finite-ordinary-bootstrap/RESULT.json`, `raw_invoice`) |
|---|---|---|
| controller | p16, 18 full calls, 15 thin query stages, 2 main fields per port | same |
| ports | 112 (E8 word, 9-bit labels, 8 fresh axes) | 111 (h = 8 word, 7 fresh axes) |
| targets | 224 main (rank 145) + 3360 idle (8j+1) + 7344 helpers | 222 main (127) + 3330 idle (7j+1) + 7848 helpers |
| paid | 3360 idle (8j) + 59 436 local (ranks 1–5) + 1680 shears + 144 centre | 3330 idle (7j) + 52 344 local (1–7) + 1665 shears, no centre |
| surplus S = mass(T) − mass(P) | 752 = 112·32 − 18·64 − 1680 | 753 (recorded `rank_surplus`) |
| G = Σ_T r ln r − Σ_P r ln r | 250 637 | 218 265 |
| S/G vs exact root | 0.003000 vs 0.003020166 | 0.003450 vs 0.003475458 |

The roots are the raw crossings of `Σ_T n_r r^(1−C) = Σ_P n_r r^(1−C)`; the package reproduces both to 10⁻¹³.
Because `C ≈ 0.003`, the equation is nearly linear: `C ≈ S/G` to within 1%.

Identical `(rank, role)` paid jobs on the two sides: 35 589 jobs of mass 74 499 (local ranks 1–5, the 1665 shears, and
the accidental idle coincidence 56 = 8·7 = 7·8). The idle stages, 56–59% of either side's paid moment, otherwise never
coincide in rank, because stage j costs 8(j+1) on complex and 7(j+1) on BIT.

## Six joint models and their ceilings

Targets of both sides are productive in the joint call; the rules differ in how the paid jobs combine. All are ideal
relaxations (no extra charges), so each number is a ceiling for its model, never a construction.

| model | C_joint | × 0.00302 | × 0.003475 | S | G | mass identity |
|---|---:|---:|---:|---:|---:|---|
| A. two networks side by side on disjoint wires (sum of the two equations) | 0.003232 | 1.070 | 0.930 | 1505 | 468 902 | kept |
| B. literal "identical (rank, role) paid once", targets of both sides | 0.182 | 60.3 | 52.4 | 76 004 | 592 405 | **violated** (−74 499 paid mass) |
| C. aligned twins: matched wires carry both frames, rank = max | no saving | 0 | 0 | −5314 | — | kept |
| D. stacked frames: matched wires, rank = r_c + r_b for targets and paid | 0.003199 | 1.059 | 0.920 | 1505 | 474 776 | kept |
| E. paid jobs merged pairwise at rank r_c + r_b, targets separate | 0.009325 | 3.09 | 2.68 | 1505 | 162 702 | kept |
| F. as E, largest complex job paired with smallest BIT job | 0.007541 | 2.50 | 2.17 | 1505 | 201 811 | kept |

How to read them.

- **B is the intuitive rule and it is not a ceiling.** Paying the common work once while crediting both target sets
  removes 74 499 units of paid mass with the target mass unchanged. But `S = mass(T) − mass(P)` is set by the
  controller (credits per port window minus centre minus thin shears, `controller.py` surplus identity; see
  `research/admission-constant-derivation`), not by the word. A joint word on the same ports has the same windows, so
  `S_joint ≤ S_c + S_b = 1505` and the paid mass must be at least `456 672 − 1505`. The heuristic "same S, G once" is
  self-contradictory: S and G are the same function `f(C)` at two points, and paid moment cannot be removed without
  removing paid mass.
- **A and D are the honest two-sided models**, and both give the mass-weighted average of the two roots
  (`C ≈ (S_c + S_b)/(G_c + G_b)`), 6–7% above the complex root and 7–8% below the BIT root. The verifier checks that
  both side equations are decreasing on `[0, 0.05]`, so the root of their sum lies strictly between the two side roots.
  Model A moreover requires the caller to supply an interchange task and a layer task simultaneously and
  independently; in the pipeline they are always sequential on the same data (basis change, then children, then the
  inverse basis change inside a layer node in `05-layers.tex`; layout move, then layer, then twiddle between rounds in
  `06-transforms.tex`), so even the +7% is not available.
- **C, the aligned twins** (one wire carries an F2⁹ frame and a rational h = 8 frame, one child moves both at the price
  of the larger rank): the credits do not add, they coincide (the same central +1 on the same window), and the mismatch
  between the local-job distributions (40 266 rank-1 jobs on complex against 24 156 rank-2 jobs on BIT) costs more than
  the whole surplus, so `S < 0` and there is no saving at all.
- **E and F are not a two-sided effect.** Their gain is the concavity of `r^(1−C)` when small paid jobs are merged into
  larger ones, the known small-job merge lever (`research/productive-lever-reprice`, "rank-16 children"). The same
  pairwise merge inside the complex side alone already gives 0.004109 (×1.36), above the BIT root, with no second side.
  That lever is closed by the whole-job premise of #4416 and the centre and thin-shear floors; a joint word does not
  reopen it.

## Why this closes the door of `kappa01-outer-repair` §2 on the current controller

The outer side is fine: the balanced engine (`balanced_shared.py`) has standalone-swap margins `g2 = g4 = a` and the
controlling margin `G = ε·q` from the layer, so a joint supplier with saving `s` on both endpoints would indeed give
`κ < s/(1+s)`. What the invoices show is that `s` itself cannot exceed the average of the two sides: the surplus lives in
the controller's port windows, the denominator lives in the paid mass, and the mass identity ties the two. "Credits
add while the common work is paid once" would need twice the windows, i.e. two words.

This is a statement about the p16 controller with the #4470 and #4814 words. A joint word with a different controller
(more credits per window, or a controller whose idle stages are shared) is outside this ceiling; see the open question.

## Reproduce

```sh
python3 scripts/research_package.py --package research/joint-supplier-average-ceiling --check-only
python3.12 scripts/research_package.py --package research/joint-supplier-average-ceiling
python3.12 -B research/joint-supplier-average-ceiling/verify.py --json /tmp/receipt.json
```

`verify.py` authenticates the four pinned inputs, reproduces both raw roots, checks the surplus identities
(752 = 112·32 − 18·64 − 1680, 753 recorded), partitions both invoices into roles, recomputes the six models, checks
the averaging property for A and D, the identity violation of B, the negative surplus of C, the within-side merge
control for E/F, binds the two quoted outer statements to their source bytes, and runs six rejecting controls
(broken surplus, wrong recorded surplus, foreign idle rank, swapped targets/paid, literal model as ceiling, tampered
source pin). The stored receipt in `RESULT.json` must match. Decimal arithmetic at 40 digits, roots bisected to
10⁻¹²; no numpy.

Not run: the 47-inequality outer engine with `a = b = s`; the outer admission is cited from
`kappa01-outer-repair` §2 and not replayed, because the invoice ceiling alone decides the question.

## Open next questions

- **Can a changed controller give a joint word more credits per port window than either side has?** Why it matters:
  the ceiling above is tied to `S ≤ S_c + S_b` on the same windows; a controller whose idle stages or thin shears are
  genuinely shared between the two endpoints would change S, not only G. First step: write the surplus identity of
  `controller.py` for a two-endpoint port (one window serving both the complex target and the address target) and
  check whether the +1 credit can be claimed twice without a second main field. Blocked by: no two-endpoint native
  word or controller exists; `research/thin-query-shear-floor` and the centre floors (#4700, #5060) bound the
  per-endpoint terms separately.

## Credit

Invoices: #4470 (zxv lineage, `joint-helper-lattice`) and #4814 (ai-nanachi, `bit-finite-ordinary-bootstrap`, on
PR4760's compact436 word). Outer reduction and the conditional one-supplier remark: `kappa01-outer-repair` (OpenAI
assistance) and the balanced engine of `coordinated-frames-and-entrance-banks` (Zhihao Chen, RaD/hipotures, icekylinx,
eumemic). Moment model and lever table: `productive-lever-reprice` (Matarener). Prepared by Mark (Matarener) with
substantial Claude (Anthropic) assistance; Apache-2.0. No human review beyond the author is claimed.
