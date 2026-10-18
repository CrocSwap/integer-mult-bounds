# Seed 51: calibrated P120 two-target shared-total audit

**Outcome:** scoped negative result. This audit finds no exact pair in one calibrated two-target decoder family; it establishes no global lower bound and no new \(\kappa\).

## Assignment and scope

- Track: structural decoder research.
- OS-random assignment seed: `51`.
- Base commit: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
- Object: the P120 E8 root lines with `e=L_51` and `d0=L_1`, where `L_1` is the first root line having nonzero Gram pairing with `L_51`.
- Search: all 120 targets and all 511 nonzero nine-bit sink labels, retaining rows whose off-target sources with nonzero `L_s·e` force one consistent rational `mu`. Then test every distinct-target pair using the union of their required `e`-orthogonal sources as one shared total.

The finite search found 27 calibrated single-target rows. Every one of the 351 distinct-target pairs makes the shared total available to both sinks, but every pair places both target indices in the other row's required-source set. Each target diagonal is then canceled, so no pair is exact. Rows with no calibrating source, other root pencils, more than two targets, and other total designs are outside scope.

## Reproduce

Run from the repository root:

```sh
python3 -I -O -B research/p120-calibrated-two-target-seed51/verify.py
```

Expected leading line:

```text
PASS_P120_CALIBRATED_TWO_TARGET_SEED51
```

The verifier uses only the Python standard library. It validates all root and label pairings in the 120-row `certificate.tsv`, exhausts the finite row and pair domains, replays the established P112 witness as a full 112-by-112 positive control, and checks root/label corruption controls. `SOURCES.json` pins the source geometry, prior construction, and originating task card to the base commit.

## Predecessor and attribution

This is a parameter-specific extension and independent replay of the row and shared-total mechanism in `research/format-limits/scripts/c6_asym.py`, committed by Douglas R. Colkitt; it uses the E8 construction and label convention in `research/format-limits/scripts/e8units.py`, committed by Mason Ellerbroek. The P112 positive control reproduces the predecessor's relaxed targets 75 and 76, sink words 329 and 438, and shared source set of size 24. Contributor: Cinna Davis. Substantial OpenAI Codex assistance was used for search design, exact replay implementation, proof explanation, and packaging.

## Open next questions

- Can the same fixed pencil produce an exact pair when a row has no off-target calibrator and its rational `mu` is selected by another complete argument? This matters because the present finite proof only covers forced-`mu` rows. First derive the full admissible `mu` set for one no-calibrator row from its diagonal and off-target constraints. That case is not covered here.
