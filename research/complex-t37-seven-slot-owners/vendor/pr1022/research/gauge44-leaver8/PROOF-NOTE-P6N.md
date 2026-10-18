# PROOF-NOTE-P6N: six b-type dim-8 cold ends on the layered no-triangle word (p6n)

Construction by NoTriReopen. Driver: `construction/layers_p6n/reproduce_p6n.py`. Review: Q6Reviewer.

## What p6n adds
On research/gauge44-notri-layered's word NP (`a9de804f…`), p123's lane is rebuilt as three factored dim-8 pairs
(`P6N-SPEC.json`):
- [512, 513] at U = (256,128,66,34,16,8,6,1). The old pair [310,512] split a rank-3 end; [512,513] replaces it;
- [311, 510] at U = (256,128,72,40,24,4,2,1);
- [522, 327] at U = (256,128,66,34,18,10,6,1).

They are built with the same premix-only factored construction as p123/q4/b6 (JP8Ends' stackJ/stackE, CarrierBypass
pattern; PR635's unchanged `build_cold_end.apply`). The cold-layer recipe `COLD-LAYERS-RECIPE-P6N.json.gz` is NP's
recipe plus these six ends; its meta lists 72 cold ends and the 8 entering ends. Applied to NP's swapped HPE word, it
gives p6n `34b683fa…`:
- profile {1:2540, 2:358, 3:446, 4:178, 5:56, 8:8};
- widths {4:64, 5:48, 7:54, 8:122, 9:216};
- width 3794 (NP 3800);
- Δ per call {1:+6, 2:+12, 3:−12}, w −6, every end b-type.

## Checks
- **NoTriReopen:** native chain including phases PASS; audit_local PASS; 95/95 layer-end controls rejected.
- **Q6Reviewer:**
  - exact;
  - (N) passes on all 21 pairs;
  - payload 55/72 bits, against 192;
  - the per-end control variant `layer_end_controls.py` (fc58c569…, which Q6Reviewer signed for research/gauge44-pq6) rejects 95/95;
  - 165 further mutants on the six ends are all rejected.
  The LayerReviewer-signed `../layers/layer_end_controls.py` controls one end per dim-8 frame family, so it would not
  control each new end. This package therefore uses the per-end variant for p6n and for the promoted word built on it.
- **Rebuild:** `reproduce_p6n.py` pins the input NP word, the output sha, profile and widths, and 95 controls.

## Remaining capacity (NoTriReopen)
After p6n, the only residual cold capacity on the word is 2 a-type units, and every end there prices about −9e-7.
