# Completed banks on PR200's diagonal bit word

Under the retained multiplication interfaces, this finite witness certifies

$$
T(n)=O\left(n(\log n)^{1-\kappa}\right),\qquad
\kappa=\frac{683061299399923}{10^{18}}=0.000683061299399923 .
$$

That is **+0.913%** over PR202 (`6768823/10^10`) and above PR199's priced composition of the same two suppliers (`1693287/2500000000`). It is the construction PR204 modelled but did not build. This package builds it, and it lands exactly on PR204's predicted value `6.83061299e-4`.

| Construction | Bit coarse saving | Conditional kappa |
|---|---:|---:|
| PR202 as published | 6.77774e-4 | 0.0006768823 |
| PR200 bit + PR193 complex, unpacked | 6.77774e-4 | 0.000676882434624733 |
| **Same suppliers, PR200 word packed into completed banks** | **6.83528e-4** | **0.000683061299399923** |

## What is new

Two existing pieces are combined:

- Evan McKinney's PR197 packs completed scratch residuals into rank-72 banks, so the rank-60 exterior corrections of the rank-20 entrance gauges disappear. PR197 applied this to PR187's bit word.
- Chafik Boukhalfa's PR200 has the strongest certified bit word: a fixed-coordinate and face-diagonal local circuit with 34 terminal sinks.

This package carries out PR197's construction on PR200's actual emitted word.

| PR200 bit word, per copy | Value |
|---|---:|
| Logical auxiliary roles | 18,908 |
| Donor/recipient splices | 1,760 |
| Terminal sinks | 34 |
| Physical chains | 17,114 |
| Unpaired rank-20 entrance gauges | 2,200 (220 distinct frames) |

**Charts.** Every distinct gauge frame gets an exact chart. The chart is the G-orthogonal complement (`15a-(sum a)1` for `G=9I-J`) followed by an exact integer kernel basis. Each chart is inverted fraction-free, and its elementary factors are replayed. The worst chart has 171 factors, with every numerator at most 5 and every denominator at most 18.

**Banks.** Across three copies there are:

- 3,300 banks of six rank-4 and two rank-24 items;
- 42,542 banks of three rank-24 items.

The 154,026 chain/bank incidences get a proper 9-edge-colouring, so each stage and copy receives every chain exactly once. The colouring is independently rechecked, and a conflicting assignment is rejected.

**Packed profile.** Three copies of PR200's independently recounted histogram, minus its 6,600 rank-60 children. Total stock is `W = 56,402` (8.9% less), deficit `5,808 = 3·1,936`, largest child 22.

**Paid moment.** The bit coarse saving rises from `677773948354561/10^18` to `683528191056257/10^18` (+0.849%). The 10^-16 rare-class fallback is included, and the next 10^-18 point is excluded by two independent moment engines.

**Leaf composition.** Three finite ordinary-leaf levels (PR185/187/197) start from PR200's completed ordinary supplier, `a_0 = 6.77341e-4`, and reach `a_3 = 6.835282e-4`.

**Assembly.** The PR193 v4 source-assisted complex supplier (`700918443859411/10^18`) has slack. The bit branch binds, and PR193's unchanged balanced 47-constraint assembly certifies κ. The next 10^-18 κ point is rejected.

Extra address-chart routing costs at most `5,368,513,266` selector calls. These are paid through the inherited ordinary selector inside the strict row/adapter toll, as in PR197.

## Verify

```sh
git fetch https://github.com/CrocSwap/integer-mult-bounds a1175449f34d39ff933d9d8ab23ced1f32b290ec
git worktree add --detach ../packed-bit-pr200 a1175449f34d39ff933d9d8ab23ced1f32b290ec
git fetch https://github.com/CrocSwap/integer-mult-bounds 187e1010ac8b259af8e9b5166f68b64bc27b4b47
git worktree add --detach ../packed-complex-pr193 187e1010ac8b259af8e9b5166f68b64bc27b4b47
python3 -m pip install -r ../packed-complex-pr193/research/source-assisted/requirements-round13.txt
python3.13 -B research/packed-diagonal-bit/verify.py --complex-root ../packed-complex-pr193 --bit-root ../packed-bit-pr200 --full
```

`--full` runs PR193's and PR200's unchanged package verifiers (about 5.5 minutes in all). It then rebuilds every chart and the bank colouring from PR200's frozen word, and recomputes the arithmetic, the independent audit and the bank endpoint controls. Without `--full`, the saved physical receipt is used, and only the pins and the arithmetic run.

## Scope and credit

This is a conditional finite construction and composition, not an unconditional multiplication theorem or a speedup claim. The all-size compiler, analytic, precision, restored-row and fixed-tape hypotheses are inherited exactly as in PR197 and PR200.

No new packing mechanism is claimed. Credit goes to:

- Evan McKinney (PR197) for the completed-bank packing, its charts, colouring, routing bound and code (reused byte-identically in `banks.py`, and adapted in `packing.py`, `arithmetic.py`, `audit.py` and `verify.py`);
- Chafik Boukhalfa (PR200) for the bit word and its verifier;
- Avi Eisenberg (PR193) for the complex supplier, and icekylinx for the source-assisted method;
- maxime-fleury (PR204) for modelling exactly this lever and pinning the target;
- eumemic and the PR168 lineage, and PR185/187 for the finite leaf composition.

Prepared by Rohan Arun with Anthropic Claude assistance. Apache-2.0.
