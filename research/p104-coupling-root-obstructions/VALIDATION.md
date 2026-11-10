# Verification record

Scientific base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
Environment: CPython 3.12.14, standard library, Linux. New files use ordinary `100644` Git modes; invoke the scripts through Python.

## Executed replay

```sh
python3 -B research/p104-coupling-root-obstructions/verify_all.py
python3 -O -B research/p104-coupling-root-obstructions/verify_all.py
```

Both return `PASS_COUPLING_ROOT_OBSTRUCTIONS`. Both retained source hashes are checked, followed by all six component checks. No source replay outside this package, dependency installation, network access, or evidence regeneration is required.

The same commands pass from a clean export of the staged Git tree containing only this package. Exported bytes and modes are compared with the staged entries before the commit is made, so the replay does not depend on sparse-checkout files or local research paths. The unchanged staged tree is then committed. The committed changed-file list contains only this package.

## Mathematical and adversarial review

The shortest-root proof was independently reconstructed by the lead and a separate mathematical reviewer: both checked the ordered product formula, corank-one displacement, signs, actual common-gauge hypothesis, minimum-query count and physical `Q=±1,D=1` specializations. A third reviewer checked its scope. The support-cut argument uses independent block-rank minors and does not assume idle fusion. Its author also independently checked the carrier residual identity. The price proof received an independent derivation of the binary side envelope, infinite discrete concavity, exact integer-root enclosure and normalized monotonicity.

Review incorporated these material qualifications:

- The common carrier must be identified by the actual accumulated ordinary transport; mere abstract conjugacy is insufficient.
- Extra spectator targets can compensate thin-query charges, so a cut counting four thins alone is not a complete price argument. The root trace theorem preserves the extra-query deficit after spectator compensation.
- Reversing the proposed residual repair for the same ordered product requires an inverse operator. The carrier note claims only the explicitly implemented `V` repair.
- Binary root groups and native leaves are distinct counts. Internal child queries and targets remain charged.
- Concurrent CrocSwap/integer-mult-bounds#6836 already proves the shared shortest-root Gram identity. That identity is credited, and novelty is confined to the stated carrier/support applications and complete price bound.

All reviewers used OpenAI assistance; no independent human acceptance or proof-assistant kernel claim is made. Finite checks corroborate the written universal arguments and preserve their explicit scope. The selected frontier and its five inherited framework assumptions are unchanged.

The all-aligned extension was separately checked through the symmetric-part rank inequality and the exact cyclic prefix-sum calculation. Its price extension was independently checked via the global supporting line, the negative arm-count intercept, the separate three-arm maximum and outward integer-root bounds.

## Registered publication gate

The final package passes the canonical registered launcher, committed-byte/mode preflight, and committed package exporter:

```sh
python3 -B scripts/research_package.py --package research/p104-coupling-root-obstructions
python3 -B scripts/check_research_commit.py --package research/p104-coupling-root-obstructions --check-modes
python3 -B scripts/export_research_package.py export --package research/p104-coupling-root-obstructions --output /tmp/coupling-root-proof.tar
python3 -B scripts/export_research_package.py check /tmp/coupling-root-proof.tar --check-inputs
```

The export is checked offline and both aggregate modes pass from its extracted bytes. `SOURCES.json` declares only canonical selected-record/task provenance; scientific pending-source bytes are retained locally and authenticated through `SOURCE-PINS.json`. No live unmerged Git head or undeclared external input is required. The original retained notices and Apache-2.0 license are preserved. The exporter reads exact package blobs without a full checkout or unrelated research archive.

At the final source checkpoint, canonical main remained the pinned base. CrocSwap/integer-mult-bounds#6833 advanced to `51f54e3c31f2f3a3e056a483b3ed66ae916ad06a`; the lead's comparison found only a new idle-rank addendum/checker and a README link, with no change to the frozen caller, native profile, pricing or retained sources. This package keeps its exact `ad24ad966b857dbfed50d9121624db84b2eccc92` scientific inputs.
