# Exact audit of the P112 asymmetric unit at d0=77

**Status: finite witness audit; no new decoder theorem or κ.** This package independently replays the `research/format-limits` C.6 asymmetric two-target P112 witness at `e=line 0`, `d0=line 77`. The adjacent d0=76 witness is already covered by PR1342; this package audits the distinct d0=77 witness with standard-library `Fraction` arithmetic and integer-bit F2 elimination.

| Receipt | Exact result |
|---|---:|
| P112 pairing entries checked | 112 × 112 = 12,544 |
| Relaxed target lines / sink words | 74, 77 / 378, 389 |
| Shared extra-total sources | 24 |
| F2 window rank | 9 |
| Coordinate COPY ranks | 8 × 8 |
| Shared-total COPY rank | 1 |
| Total COPY cost | 65 |
| Corrections at relaxed targets | 28 + 28 (symmetric E8 unit: 52 + 52) |

The verifier recomputes the E8 Gram entries and the 9-bit label pairing from the pinned input rows, checks the exact rational decoder support relation on all 12,544 entries, computes the F2 ranks directly, and rejects a changed sink and an omitted shared source. These are finite checks of this witness, not a universal P112 or P120 theorem.

## Reproduce

With Python 3.12 or newer and no third-party dependencies:

```sh
python3 -I -O -B research/p112-asymmetric-unit-audit-seed43/verify.py
python3 -I -O -B research/p112-asymmetric-unit-audit-seed43/test_package.py
```

The repository-registered command is:

```sh
python3.12 scripts/research_package.py --package research/p112-asymmetric-unit-audit-seed43
```

Expected verifier marker: `PASS_P112_ASYMMETRIC_UNIT_AUDIT_SEED43`.

## Scope, sources, and credit

Base: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. The input line and label arrays are extracted from the Apache-2.0 `research/format-limits/scripts/e8units.py` source and pinned by hash. PR1342's d0=76 independent audit is credited and pinned as the neighboring predecessor. The current selected κ remains 0.001672660197076918; this audit changes no supplier, paid profile, or selected result.

Prepared by **Cinna Davis / @1337isnot1337** with substantial **OpenAI Codex** assistance in research, implementation, verification, and writing. No independent human review is claimed. Preserve the repository Apache-2.0 license and attribution to the `format-limits` source authors and PR1342.

## Open next questions

Can this local asymmetric unit be embedded into a complete paid decoder while retaining all source access, boundary, and restoration costs? That requires a separate complete construction and invoice.
