κ = 7.69198971896986e-4

# The p = 10 bit word with the transcript stage stack

A conditional finite construction with **κ = 384599485948493/(5·10¹⁷) ≈ 7.69198971896986 × 10⁻⁴**, +0.650% over
#315 (7.64230861320245e-4). The bit supplier binds.

#315 (DreamingOfClouds) put the paired-cube bit word at cube size p = 10 (h = 20, v = 960, m = 100) into the gen5
five-stage completed-bank pipeline, with no transcript stages. This package keeps #315's word, banks, complex
supplier and verification chain unchanged and inserts the stage stack of the p = 12 gen5 pipeline, re-derived on
the p = 10 word:

    parity -> descent -> target squares -> kernel entries -> early restorations -> terminal sinks -> reorder -> lowering

| stage | on this word | predicted κ (φ ledger) | verified κ (full replay) |
| --- | --- | ---: | ---: |
| #315 (no stages) | R 8,230, 1,270 entrances | 7.64230861320245e-4 | 7.64230861320245e-4 |
| + descent (#287 rule) | 480 gates, −480 calls | 7.65146115390441e-4 | 7.65146115390441e-4 |
| + target squares (#268/#287) | 120 groups | 7.65802240659923e-4 | 7.65802240659923e-4 |
| + kernel entries (#272/#299/#300) | 775 entries (536 pairs, 239 families), rank 970 | 7.67751918266997e-4 | 7.67751918266997e-4 |
| + early restorations (#280/#283) | 240 helpers | 7.68386813092527e-4 | 7.68386813092527e-4 |
| + terminal sinks (#283) | 7 sinks, R → 8,223 | 7.68798619422518e-4 | 7.68798619422518e-4 |
| + reorder (#299) | 133 moves | 7.69198971896986e-4 | **7.69198971896986e-4** |

The predictions come from the deficit-fixed φ ledger (the one-stage histogram delta of each frozen selection,
×5, normalized ×12, W = (mass + 12·2,040)/100, the bit-bound assembly of `math_check.py`), calibrated on #315's
own ledger (it reproduces #315's κ exactly). The verified values are full `verify.replay` runs of the package
truncated after each stage. A second descent and a second reorder round were searched and found nothing on this
word, so they are not stages.

| one invocation | #315 | this package |
| --- | ---: | ---: |
| independent dirty registers R | 8,230 | **8,223** |
| independent entrances | 1,270 (16, 17) | 2,045 (adds 775 kernel pivots of ranks 1–14) |
| early-restored endpoints | 0 | 240 |
| banks per stage / literal stock (60 replicas) | 86,526 / 663,030 | 85,716 / 658,980 |
| bit coarse saving (certified root) | 7.64815357146385e-4 | **7.69791094751301e-4** |
| complex coarse saving (unchanged) | 7.72714351296671e-4 | 7.72714351296671e-4 |
| binding side | bit | **bit** (root 0.38% below the complex leaf cap) |
| κ | 7.64230861320245e-4 | **7.69198971896986e-4** |

Run with Python 3.12 or newer, sympy 1.14.0 and assertions enabled:

```sh
python3 -m pip install -r requirements.txt
python3 -B verify.py --output /tmp/p10-stages-verification
```

The output directory must be new and outside the package. Verification takes about four minutes, uses no network
and runs no producer or search. Besides #315's checks (`README-PR315.md`), every transcript stage is a mandatory
stage with its own receipt: frozen selections bound to the exact input word, all-column F₂ replays forward and
inverse with omission controls, integer replays, exact operand source spans, nested frame chains rebuilt from
scalar/COPY events with both reflected ledgers, the raw ledger rebound after every stage, endpoint charts and the
re-tiled banks. Every word-dependent value is a strict pin in `word-pins.json` (recorded by
`discovery/repin.py`).

See:

- `STAGES-PROOF.md` for the stages, what changed from p = 12, and the ledger;
- `BANK-PROOF.md` (last section) for the residual widths and the economy tiling;
- `discovery/README.md` for the searches that produced the selections;
- `README-PR315.md`, `PROOF.md`, `bitword/README.md` for the base package;
- `NOTICE.md` for attribution.

The result is conditional on the retained all-size compiler, common weighted chart, restored rows, selectors,
tape routing, prime supply, precision/recovery, complex symbolic correctness and analytic reduction. The included
finite checks do not replace those hypotheses.

Prepared by Chafik Boukhalfa (chafreaky) with Anthropic Claude assistance; Apache-2.0.
