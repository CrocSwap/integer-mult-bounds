# The selected k8 provider lies outside the historical owner catalogue

The frozen heterogeneous-owner catalogue contains 71 records and 25 distinct
inventory/profile interfaces. Neither the selected k8 interface nor its pre-slot
R480 source is one of them. This receipt follows the selected-result source
manifest to the exact selected SPEC; matching only the mass identity would give
an incorrect applicability conclusion.

This is a source-bound navigation result, not a new catalogue theorem or bound.
The historical package already identifies R480 as outside its domain. The added
bridge explicitly identifies today's selected source and its seven-slot change.

## Exact comparison

The baseline U8 helper width is 3778; the selected width is 3730. All three
interfaces satisfy local rank mass minus helper width = 1856. The pre-slot and
selected helper inventories are identical, while the paid profile changes by
H3 += 14, H4 -= 28, H5 += 14. Both profile count and rank mass are preserved.
The machine-readable dictionaries are in RESULT.json.

For the historical reduced-cost function phi_b(r) = 73^b r^(1-b), with 0 < b < 1,
the unchanged helper inventory cancels. The selected-minus-pre-slot reduced-cost
change is exactly 14*(phi_b(3)-2*phi_b(4)+phi_b(5)), which is strictly negative:
phi_b has negative second derivative on positive r, so its midpoint inequality
is strict at 3,4,5. This comparison does not extend the frozen catalogue's dual
inequality to either outside interface.

## Reproduce

From the repository root with Python 3.12:

```sh
python -X utf8 scripts/research_package.py --package research/selected-k8-catalogue-scope
```

The optimized checker verifies SHA-256 and Git blob pins, the selected manifest
binding, all 25 interface memberships, the exact delta, and three controls:
mass-only matching, baseline inventory with selected profile, and the reverse
mixture. It does not replay the selected circuit or change selected kappa.

## Credit

The historical catalogue, R480 and selected k8 construction are existing frozen
repository results, pinned in SOURCES.json. This work adds a source-chain receipt
and one navigation paragraph. Prepared by woklerx with substantial OpenAI Codex
assistance.

## Open next questions

Can a new catalogue containing the selected k8 interface admit a useful signed
dual? First add that exact interface in a new package, then independently verify
the resulting dual. The historical catalogue alone cannot answer this.
