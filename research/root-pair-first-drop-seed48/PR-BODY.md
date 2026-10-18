For distinct nonorthogonal E8 root normals, the first puncture count at
which one exact label-pairing term can cost at most six copies is 26.
The 25-puncture boundary immediately beyond PR968's theorem has exactly
126 potentially low-rank support masks, all of rank seven. A 26-puncture
witness drops the surviving support dimensions from `(9,7)` to `(8,7)`
and has rank six. An explicitly checked reflection orbit transports this
statement to all 6,720 ordered odd root-line pairs.

The package includes the completeness proof, source pins, full finite
certificate, two rank implementations and adversarial controls. It also
completes the term to an exact rational eight-term decoder and prices all
terms: 69 copies on 94 ports. This is a structural threshold result, not
a supplier improvement, a whole-decoder optimum, or a new kappa claim.

Validation from the repository root:

```text
python research/root-pair-first-drop-seed48/verify.py
python -O research/root-pair-first-drop-seed48/verify.py
python research/root-pair-first-drop-seed48/check_sources.py
```

The main replay reports threshold=26, candidates25=126, orbit=6720 and
completion_cost=69. The source compatibility check compares all 14,400
pairing entries against PR968 and rejects three pin/certificate mutations.
Python-only exact arithmetic; no native supplier or precision admission
has been run. Prepared for @woklerx with substantial OpenAI Codex
assistance. The model is credited to DreamingOfClouds's PR717 and
themilkman216's PR968; all predecessor files remain unchanged.
