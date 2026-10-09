κ = 6.83190455036641e-4

# Coordinated frame cuts and entrance banks on PR200

Conditional kappa: **6.83190455036641e-4**, exactly `683190455036641/1000000000000000000`.

Latest pinned comparator: PR207 at `cd14825023b75af4f5919a30e5e6d548b6ade5bc`, kappa 6.831904550365e-4. This package is approximately **2.06e-11% higher**. The additional gain here comes from one extra finite stopped-leaf bootstrap level on PR207’s fully replayed supplier; PR205 and PR207 independently carry completed PR200 banks.

This composes 302 admitted rational operation-frame changes and completed stage-private entrance banks on PR200 with PR202's source-assisted complex supplier, then applies four fixed ordinary-leaf bootstrap levels and the unchanged balanced assembly. Gains are composed through actual profiles; they are not added.

## Reproduce

Python 3.11 or later; assertions enabled. Install `numpy==2.3.5` and `scipy==1.17.0`, then run:

```sh
python -B research/coordinated-crossover-pr200/verify.py
```

The pinned source and witnesses are included in five archive parts. No git, network, account, or download is used by verification. Allow about 250 MB scratch space; on Windows with a nearly full system drive, use `--temp-root F:/your-existing-scratch-directory`. Verification uses a temporary extraction and leaves the submitted files unchanged.

The verifier executes the complete bit formal-column replay, modified rational frames, terminal actions, actual prime witnesses, explicit bank assignment and chart/inverse/routing checks. It replays the exact complex local lifts and fresh-column/target contract against pinned witnesses, recomputes paid moments with two independent rational enclosures, and checks all 47 strict assembly inequalities. Rank corruption and adjacent-grid controls must fail. The numerical complex search is not rerun; its frozen witness is rechecked exactly.

## Scope

This is a **conditional finite supplier certificate**, with the same all-size compiler, completed weighted/restored selector, routing, precision, fixed analytic tape and finite bridge conditions as the cited public work. It does not independently prove those conditions or provide a new Lean certificate. The complex branch retains the source-assisted local-flow contract: no newly flattened global scalar transcript or full Clifford/router replay is claimed.

Base bit: PR200, `a1175449f34d39ff933d9d8ab23ced1f32b290ec`. Base complex/assembly: PR202, `8d8d67bcf69c5ea67d3a29dbc64ba588156d6e8d`. The included tracked source is the LF checkout of PR202; its PR200 bit program agrees with the separate PR200 pin (only SOURCE.json differs). Original attribution and licensing are retained. Prepared with substantial OpenAI Codex assistance; no new personal byline.
