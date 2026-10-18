## Scope and result

**Scoped negative result; no new kappa.** In `F2[D16]`, with the order-16 dihedral presentation `r^8=s^2=1, srs=r^-1`, paid reflections `x=s` and `y=rs`, and target central involution `z=r^4=(xy)^4`, the exact minimum for `diag([z],[z])` on two arbitrary dirty scalar registers is 16 rank-one calls. Every one of the six rank-one idempotents in `M2(F2)` is allowed for each paid label.

The direct word gives 16 calls. An exact meet-in-the-middle search finds no common state between identity radius 7 and target radius 8, excluding every word of length at most 15. The state spaces are the full coefficient matrices over `F2[D16]`, not a selected representation. The independent tuple-state verifier reproduces all layer counts and discovery-order hashes.

This is a new bounded group/endpoint relative to the local two-register D8 result. Live claim #1738 changes the register count but retains D8; #1759 concerns a UT4 endpoint. Neither is treated as superseded or resolved here.

## Reproduce

```sh
python3 -I -B research/bit-d16-central-pair-seed1f8b/verify.py
python3 scripts/research_package.py --package research/bit-d16-central-pair-seed1f8b --check-only
```

The independent verifier and metadata/pin check passed locally under Python 3.14.7. The registered package runner requests Python 3.12, which is not installed in this environment.

## Pins, costs, and limits

- Base: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`.
- Selected record SHA-256: `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
- Predecessor note: `research/bit-dihedral-commutator/README.md`, SHA-256 `4f3f9df6d6d96a26ccb0fcd2ef947cce5d53b0d992da22e866f1e025be4c0492`.
- Direct paid bill: 16. For this optimistic formal model, helper, frame, copy, restoration, hosting, precision, and recursive-interface charges are zero.
- No mapping to the selected supplier is supplied; this cannot imply a new multiplication exponent or `kappa`.

Prepared by woklerx with substantial OpenAI Codex assistance. No independent human review is claimed. Apache-2.0.
