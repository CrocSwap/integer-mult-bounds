# Contributor replay: twelve-move PR610 owner consolidation

Jeremy Diviney, with OpenAI Codex assistance, rebuilt the revised
[complex-571-cold14 package](../complex-571-cold14/OWNER-CONSOLIDATION.md) from its
pinned sources with the default committed SPEC and no reused baseline or providers.
All 41 stages pass. Conditional κ is 0.001625434703655052, above PR610's
0.00162536523418317 at b7c680ea38b9a25a89fce189bb927b45842362d0.

This is contributor validation of the new map, awaiting independent review.
It does not update the repository's selected certificate. Package inputs are bound
by the manifest and SPEC hashes in VALIDATION.json and RECEIPT.json; the latter
also records all 41 stage exits and hashes of the regenerated proof artifacts.
RESULT.json records exact rational endpoints, conditional scope and no-reuse flags.
ASSEMBLY-CONTROLS.json records all 114 rejected mutations. The owner check rejects
23 mutations; phase and generated-identity controls pass. make gen4-bank-verify
also passes its nine stages and 112 immutable source pins. The full repository-wide
make verify target was not rerun for this standalone research-package change.

The discovery tool reproduces the frozen nomination exactly. Of 36,288 owner
records, twelve change placement and two change only offset. Provider circuits,
recipes, dispatch, source pins and verifier code remain byte-identical to PR610.
The exact rational and decimal κ fields agree. No solver or floating objective is
trusted for admission.

Follow the package's OWNER-CONSOLIDATION.md to reproduce. The predecessor sources,
licenses, AI disclosures, cited bit supplier and all-size/compiler/hosting/precision/
analytic assumptions remain as described in its NOTICE.md. This is not an
unconditional multiplication theorem, optimality proof or full Lean certification.

The full repository `make verify` subsequently passed on submitted PR618 commit `c0874b2491382210546a592df0aba8223fee4f9f`, including all 84 isolated test modules, the gen4 checkpoint and historical patch checks. That checkout remained clean. `MAKE-VERIFY.log.gz` retains the complete log; its decompressed SHA-256 is in VALIDATION.json.
