# Host-strip deficiencies and shared-hub rank

Under the nondegenerate two-column signed-Gram host hypotheses, with
excess e and k >= e+2, the sum of host-strip deficiencies is at most e.
With the set-RC2 piece data this forces at least 2k−e qualifying singleton
incidences. The common-two-hub sign argument extends to arbitrary ordered
sets of m hosts and gives rank at least m in characteristic different
from two, including a common-kernel extension. It yields a stage-pair
packing cut and excludes two explicit high-price LawQ profiles at k=76.

The exact rank-three, three-stage signed frame witnesses the e=1 boundary.
The [thin-window checks](THIN-WINDOW.md) include actual mask corrections.
The [pricing note](PRICE-PRUNING.md) records separate narrower scope bounds.
See the [shared-hub proof](SHARED-HUB-PROOF.md) and [strip proof](STRIP-DEFICITS.md)
for the hypotheses and controls. Verifier-word realization and a general
k=76 price theorem remain open.

## Open next questions

Use the rank and common-kernel inequalities on larger overlapping event pieces, then derive a general lawful k=76 invoice bound.

Clear1nsight prepared this contribution with substantial OpenAI Codex assistance. Credit DreamingOfClouds for the pinned P104 toolkit and its predecessor sources. Copied Apache-2.0 sources retain their notices.

## Reproduction

Use Python 3.12 with SymPy 1.12 for the signed-frame controls. Replay in
a clean copy of this directory and compare the generated receipts.

```sh
python3 -B shared_hub_check.py
python3 -B check_transition.py
python3 -B check_transition.py --mutate  # expected rejection
python3 -B check_thin.py
python3 -B pricing/check_price.py
```
