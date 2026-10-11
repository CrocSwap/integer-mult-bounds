κ = 7.76518649004426e-4

# #325's p = 10 bit word with the transcript stage stack and #327's p = 10 complex supplier

A conditional finite construction with **κ = 388259324502213/(5·10¹⁷) ≈ 7.76518649004426 × 10⁻⁴**, +0.888% over
#325 (7.69684039383334e-4) and +0.905% over our #320 (7.69553898621543e-4). The bit supplier binds.

It combines three pieces, each re-checked here from primary inputs:

- **#325's bit word** (DreamingOfClouds): the paired-cube bit word at p = 10 (h = 20, v = 960, m = 100) with a
  re-annealed pair module, a p = 10 local design, a balanced cube orientation and a tiered reuse matching (960 reuse
  pairs, 1,200 rank-16 entrances), in #315's five-stage completed-bank pipeline;
- **our #320 stage stack**, re-derived on #325's word, plus two stages that are empty on #315's word but pay here:

      parity -> descent -> target -> kernel -> restore -> sink -> descent2 -> reorder -> reorder2 -> lowering

- **#327's complex supplier** (DreamingOfClouds): the p = 10 centre-sharing complex program (h = 20, m = 100),
  b = 779597612622781/10¹⁸. With #325's p = 11 supplier (b = 772714351296671/10¹⁸) the staged bit root would exceed
  the complex leaf cap and κ would be capped at 7.72117723737704e-4 (this package's word with that supplier was
  verified at that value). `COMPLEX-P10.md` lists the five places where #315's complex checks pinned the p = 11
  program and how they are now derived from the certificate and pinned.

| stage | on this word | predicted bit root / κ (φ ledger) | verified bit root / κ (full replay) |
| --- | --- | ---: | ---: |
| #325 (no stages) | R 8,100, 1,200 entrances | 7.70276909563042e-4 / 7.69684039383334e-4 | 7.70276909563042e-4 / 7.69684039383334e-4 |
| + descent (#287) | 480 gates, −480 calls | 7.71206727248877e-4 / 7.70612425424136e-4 | 7.71206727248877e-4 / 7.70612425424136e-4 |
| + target squares (#268/#287) | 120 groups | 7.71873297992310e-4 / 7.71277968783544e-4 | 7.71873297992310e-4 / 7.71277968783544e-4 |
| + shared-donor kernel (#272/#299/#319/#320) | 1,339 entries, rank 1,445, φ −2,376.62 | 7.75353328869776e-4 / 7.74752621500104e-4 | 7.75353328869776e-4 / 7.74752621500104e-4 |
| + early restorations (#280/#283) | 240 helpers | 7.76000852680037e-4 / 7.75399141938020e-4 | 7.76000852680037e-4 / 7.75399141938020e-4 |
| + terminal sinks (#283/#295) | 10 sinks, R → 8,090 | 7.76601004205538e-4 / 7.75998362749977e-4 | 7.76601004205538e-4 / 7.75998362749977e-4 |
| + post-sink descent (#287/#291/#299) | 47 gates, φ −49.68 | 7.76674466583451e-4 / 7.76071711153240e-4 | 7.76674466583451e-4 / 7.76071711153240e-4 |
| + reorder (#299) | 130 moves, φ −296.89 | 7.77113877988846e-4 / 7.76510440600338e-4 | 7.77113877988846e-4 / 7.76510440600338e-4 |
| + reorder round 2 (#306) | 2 moves, φ −5.55 | 7.77122099155703e-4 / 7.76518649004426e-4 | 7.77122099155703e-4 / **7.76518649004426e-4** |

The predictions come from the deficit-fixed φ ledger (one-stage histogram delta of each frozen selection, ×5,
normalized ×12, W = (mass + 12·2,040)/100, the bit-bound assembly of `math_check.py`), calibrated on #325's own
raw ledger, which it reproduces exactly. The verified values are full `verify.replay` runs of the package truncated
after each stage (record mode), all with #327's complex supplier; the last row is also the strict `verify.py` run.

| one invocation | #325 | this package |
| --- | ---: | ---: |
| independent dirty registers R | 8,100 | **8,090** |
| independent entrances | 1,200 (rank 16) | 2,539 (adds 1,339 kernel pivots of ranks 1–8) |
| early-restored endpoints | 0 | 240 |
| banks per stage / literal stock (60 replicas) | 85,680 / 658,800 | 84,549 / 653,145 |
| bit coarse saving (certified root) | 7.70276909563042e-4 | **7.77122099155703e-4** |
| complex coarse saving | 7.72714351296671e-4 (p = 11 program) | **7.79597612622781e-4** (#327's p = 10 program) |
| binding side | bit | **bit** (root 0.32% below the complex leaf cap) |
| κ | 7.69684039383334e-4 | **7.76518649004426e-4** |

Run with Python 3.12 or newer, sympy 1.14.0 and assertions enabled:

```sh
python3 -m pip install -r requirements.txt
python3 -B verify.py --output /tmp/p10b-stages-verification
```

The output directory must be new and outside the package. Verification takes about three minutes, uses no network
and runs no producer or search. Besides #325's checks (`README-PR325.md`, `PROOF.md`), every transcript stage is a
mandatory stage with its own receipt and omission control: frozen selections bound to the exact input word,
all-column F₂ replays forward and inverse, integer replays, exact operand source spans, nested frame chains rebuilt
from scalar/COPY events with both reflected ledgers, the raw ledger rebound after every stage, endpoint charts and
the re-tiled banks. The complex stage admits #327's program with Sussman's `gx.check1` (exact scalar identity) and
his `gxcore` mirror, replays its labels, scalar words and splice, and certifies its coarse saving with both moment
engines. Every word-dependent value is a strict pin in `word-pins.json` (recorded by `discovery/repin.py`).
`python3 -B bitword/producer/regenerate.py --work W` reproduces the five pinned bit-word files byte for byte.

See:

- `STAGES-PROOF.md` for the stages and the ledger;
- `COMPLEX-P10.md` for the complex supplier transplant;
- `BANK-PROOF.md` (last section) for the residual widths and the economy tiling;
- `discovery/README.md` for the searches that produced the selections;
- `README-PR325.md`, `PR-STATEMENT-PR325.md`, `PROOF.md`, `bitword/README.md` for the base package;
- `NOTICE.md` for attribution.

The result is conditional on the retained all-size compiler, common weighted chart, restored rows, selectors,
tape routing, prime supply, precision/recovery, complex symbolic correctness (including the generic h = 20 B₂
layout of the complex program) and analytic reduction. The included finite checks do not replace those hypotheses.

Prepared by Chafik Boukhalfa (chafreaky) with Anthropic Claude assistance; Apache-2.0.
