# P104 direct tail side correction

This package gives an exact finite construction for the missing `I-G/2` map
after the pinned P104 native `G/2` channel. It does not claim a new conditional
bound or a globally admitted supplier.

## Construction and cost

The cut is immediately after the frozen 4,058-event channel prefix. At that
point all 104 source registers `X_s` are full-frame and each target `Y_t` is in
its final rank-eight hyperplane. Let `G[t,s]` be the exact root inner-product
matrix on the 104 retained ports. For each target in order, the construction:

1. Promotes `Y_t` from its rank-eight frame to the full nine-dimensional frame.
2. Adds `delta[t,s] - G[t,s]/2` times `X_s` for every nonzero coefficient.
3. Restores `Y_t` to its original rank-eight frame.

Each row has 48 nonzero coefficients, so the correction uses 4,992 scalar
additions and 208 rank-one native frame changes. Exact symbolic replay over all
280 arbitrary input columns proves the final rows are `Y_t + X_t`; all other
rows and all target frames are restored. Four negative controls reject a wrong
sign, missing promotion, missing restoration, and missing matrix entry.

The augmented local paid profile is
`{1:1282, 2:58, 3:86, 4:104, 5:48, 6:24, 7:8, 8:8}` with rank mass 2,576.
The exact favorable local-word ceiling is lower than the uncorrected channel's
under the same pinned relaxation. See [RESULT.json](RESULT.json) for rational
brackets and artifact hashes, [CORRECTION-ROWS.json](CORRECTION-ROWS.json) for
the sparse matrix, [AUGMENTED-WITNESS.json.gz](AUGMENTED-WITNESS.json.gz) for
the literal word, and [SIDE-TRANSPORTS.json.gz](SIDE-TRANSPORTS.json.gz) for
the native recipes.

This is a local tail construction. It does not assign global owners or hosts
to all source reads, certify copied-information delivery, account for a global
assembly, or establish an all-size supplier. Those obligations prevent any
new kappa claim. The merged [#1940 chronological schedule](https://github.com/CrocSwap/integer-mult-bounds/pull/1940)
attains the 32-chain target-order bound, but leaves exact-copy formation, dirty
restoration, side corrections, hosting, and precision unresolved. This package
does not integrate with that schedule.

The frozen channel in `research/p104-native-channel` retains Rohan Arun's
scalar/frame channel from [#1972](https://github.com/CrocSwap/integer-mult-bounds/pull/1972)
and the native Clifford realization accepted in
[#1991](https://github.com/CrocSwap/integer-mult-bounds/pull/1991). This
package keeps that witness and its certificates unchanged. Source commit, Git
blob, and SHA256 pins are listed in [SOURCES.json](SOURCES.json).

The focused result is under review in [PR #2089](https://github.com/CrocSwap/integer-mult-bounds/pull/2089).
Its canonical investigation thread is
[Discussion #2092](https://github.com/CrocSwap/integer-mult-bounds/discussions/2092);
the completed Cycle 16 claim is linked from the mechanism hub.

## Reproduce

From repository root, with Python 3.12:

```sh
python3 scripts/research_package.py --package research/p104-tail-side-correction-seed749717 --check-only
python3.12 scripts/research_package.py --package research/p104-tail-side-correction-seed749717
```

The registered replay checks the pinned native positive control, rebuilds the
row correction, verifies every native rank-one operator with the independent
native interpreter, runs the exact rational endpoint induction and failure
controls, and checks the deterministic artifact hashes.

## Open next questions

Can another sparse factorization or a different cut reduce the 208 paid
rank-one frame changes while admitting a global owner/host schedule? The first
step is to screen the changed inventory's optimistic paid profile before
building a second word. The current global owner/host assignment is unresolved.

## Credit

Prepared by Cinna Davis with substantial OpenAI Codex assistance in verifier
implementation, exact cost screening, and package preparation. The exact
claims are those replayed by the included verifier. New package work is
Apache-2.0; predecessor source notices remain in the pinned inputs.
