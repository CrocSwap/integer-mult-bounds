# Coordinated owner repair on PR614

Conditional **κ = 0.001625744726006285**; conservative **κ = 0.001625744723187284**. The exact gain over PR614 is `450920841/15625000000000000` (0.000000028858933824).

This package retains jeremykothe2's PR614 dispatch and DreamingOfClouds' PR604 cold-ended provider construction: 70 JP8 calls and two ATM3 calls. It changes the literal owner map. Six accepted repairs involving three calls, followed by five involving four calls, improve the remaining idle-child profile. Floating-point integer-program objectives nominate candidates; exact constraints and rational moment enclosures certify acceptance.

All inherited native programs, constructors, provider contracts, moment engines, admission rules and negative-control implementations are unchanged. The independent map checker and declarative consistency checker are additional checks. No solver is needed to replay the final witness.

## Reproduce

With Python 3.11 or later, a C++ compiler and Boost headers:

```sh
bash research/complex-cold-owner-repair/verify.sh /tmp/cold-owner-repair-fresh
```

The output directory must not exist. This checks that `WITNESS.json` and `EXPECTED.json` reconstruct the replay `SPEC.json`, rebuilds the baseline and both native providers, and executes strict physical, invoice, moment and outer admission. The separate map checker then reads the newly produced native programs through `--work` and checks all 36,288 literal roles and exact moment signs under `-I -O -B`. Inherited pipeline assertions remain enabled.

Pinned dependencies are bundled under `vendor/`. The multicold tree is complete; other bundles retain the manifest, notices and pinned files used by the typed constructors. Explicit source bindings in `verify.sh` allow relocation. Historical PR614 search inputs live under `history/pr614/` and describe that earlier witness.

See [validation evidence](../complex-cold-owner-repair-validation/README.md) for actual runs and platform boundaries.

## Research method and scope

At the user's request, we applied [Fork-and-Flush](https://arxiv.org/html/2610.07447v1): four fresh-context branches received identical all-JP8 workspaces; their exact results were independently graded; only the strongest session continued. The local adaptation used nominal eight-minute horizons and three concurrent worker slots. It is not an equal-compute replication or evidence of escape into a distinct idea basin.

PR614 appeared during that round. Its independently verified inputs were supplied to the selected session after selection. This final improvement therefore uses both the new public PR614 starting point and the continued repair search. Losing branch workspaces were archived, not combined into this candidate.

The witness remains conditional on the inherited all-size compiler, common-label and mutable-source realization, whole-call hosting, precision/tape/exact recovery, analytic transfer and the cited unchanged PR543 bit supplier and H1–H5 assumptions. It is not an unconditional multiplication theorem, a complete Lean proof, an optimal packing claim or a practical speedup. κ=1 is not established.

## Attribution

PR614: jeremykothe2, immutable head `6cfd7e2039078f80a8a39dec5e958d8df304cb90`. Native cold-ended construction: DreamingOfClouds PR604, built on jeremykothe2 PR601 and the pinned PR568/569/571/575/583 contributions. Full inherited attribution and AI disclosures remain in NOTICE.md and vendor notices. `UPSTREAM-614.json` binds the exact source blobs.

Owner repair, independent checks and packaging: chafreaky with OpenAI Codex assistance. Apache-2.0.
