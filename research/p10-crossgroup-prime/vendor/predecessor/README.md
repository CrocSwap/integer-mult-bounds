κ = 7.69556690340075e-4

# Four pre-sink frame retimings on the p = 10 construction

This conditional finite construction certifies **κ = 30782267613603/40000000000000000
= 7.69556690340075 × 10⁻⁴**. It is a successor to PR #320 at immutable commit
`1b37957d1520c80b6ea796bf418e52be5109c2d4`, whose certified κ is
769553898621543/10¹⁸ = 7.69553898621543 × 10⁻⁴. The exact improvement is
2791718532/10¹⁸. The bit supplier binds; the complex supplier is unchanged.

The change is four exact constructed-frame retimings after early restoration and before terminal sinks.
Three `kernel_setup` ADD frames change from rank 8 to rank 9 and one from rank 13 to rank 14.
The inherited seven sinks are rebound to the new intermediate records. Re-running the inherited reorder
selector chooses the same 133 scalar incidences and exact ledger delta; 24 equal-cost side-root placements
use rank-19 anchors instead of the predecessor's rank-18 anchors. Their final scalar ordering differs.
Every scalar/COPY instruction, entrance, endpoint and completion is preserved by the new stage.

    parity -> descent -> target -> kernel -> restore -> presink -> sink -> reorder -> five-stage lowering

| quantity | pinned PR #320 | this successor |
| --- | ---: | ---: |
| κ | 7.69553898621543e-4 | **7.69556690340075e-4** |
| bit coarse root | 7.70146568251934e-4 | **7.70149364272199e-4** |
| independent dirty registers R | 8,223 | 8,223 |
| final scalar ADDs | 336,253 | 336,253 |
| final local records | 386,905 | 386,909 |
| banks per stage | 85,578 | 85,578 |
| literal stock (60 replicas) | 658,290 | 658,290 |
| normalized W | 131,658 | 131,658 |

The new one-stage paid-call histogram delta is
`{1:+12, 2:-8, 8:-3, 9:+3, 13:-1, 14:+1}`: four extra calls but the same rank mass.
Its φ change is approximately −1.9305726664; the claim above comes from both exact moment engines and
all 47 outer constraints, not from that search score.

Run with Python 3.11 or newer, sympy 1.14.0 and assertions enabled:

```sh
python3 -m pip install -r requirements.txt
python3 -B verify.py --output /tmp/p10-presink-verification
```

The output directory must be new and outside this package. Verification uses no network and runs no search.
It validates the immutable upstream archive, the complete package manifest, every mandatory transcript receipt,
all-column forward/inverse F₂ replays and omission controls, integer restoration, exact operand source spans,
both reflected ledgers, new and inherited frame determinants, endpoint charts, completed banks, both moment
engines and adjacent-grid rejection, all 47 outer inequalities and seven strict margins, and the finite bill.
Word-dependent quantities are strict pins in `word-pins.json`; `discovery/repin.py` is a development utility
and is not invoked by the verifier.

`STAGES-PROOF.md` and `PRESINK-PROOF.md` describe this successor. `SOURCE.json` binds the full source commit,
archive and exact modified/added path sets. The untouched predecessor package is archived in
`upstream/pr320-package.tar.gz`; its README, stage proof and PR statement are also retained as
`UPSTREAM-PR320-README.md`, `UPSTREAM-PR320-STAGES-PROOF.md` and `UPSTREAM-PR320-PR-STATEMENT.md`.
Other inherited proof texts retain their predecessor meaning. `NOTICE.md` preserves all inherited attribution.

The result remains conditional on the retained all-size compiler, common weighted chart, restored rows,
selectors, tape routing, prime supply, precision/recovery, complex symbolic correctness and analytic reduction.
The finite checks do not discharge those hypotheses.

Successor selection and integration prepared with OpenAI Codex assistance; Apache-2.0. The base package and
its shared-donor selection are Chafik Boukhalfa's work with Anthropic Claude assistance, building on the
p = 10 construction by DreamingOfClouds and the earlier authors credited in `NOTICE.md`.
