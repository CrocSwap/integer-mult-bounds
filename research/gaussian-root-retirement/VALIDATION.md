# Validation record

Local environment: CPython 3.12.13 on macOS. The complete registered normal
and optimized replays both passed on November 3, 2026 (UTC).

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-root-retirement --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-root-retirement
```

Markers: `PASS_PACKAGE_METADATA_AND_PINS`,
`PASS_GAUSSIAN_ROOT_RETIREMENT_KAPPA_00329394`, and
`PASS_REGISTERED_RESEARCH_PACKAGE`.

Coverage includes the full source regeneration and controls, all 799 native
columns, native absolute phases, all physical contacts, both complete caller
engines, the exact dual pairs and basis maps, two rational price engines,
the compiler and all outer predicates. No source receipt is used in place
of these checks. The source result must also match its frozen complete receipt.

Committed-byte checks, isolated export checks and hosted CI are pending.
The optional full-history preflight is not claimed in this shallow checkout.
No independent scientific review is claimed. The five source framework
assumptions remain. The selected frontier is unchanged.
