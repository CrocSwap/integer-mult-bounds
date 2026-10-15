# QQ16 cover-map parity floor at the B1 cut

**Scoped all-depth obstruction; no new kappa.** Every finite composition of the pinned cover maps preserves the 18 odd Z4 frame terms in each of the eight `Y_A` observations at the post-`B_1_2` cut. In the one-term native-line model, clearing them into the existing private `C0..C7` fields requires at least 144 rank-one calls. That is far beyond the two additional rank-one-equivalent operations allowed by the favorable rank-eight output screen.

This completes the specific depth-two/three follow-up left open by the released claim in Discussion #2192 and PR #2197. The proof uses an all-depth invariant, so no finite map-path search is needed.

## Model and cost

The exact eight source frame IDs are `f117`, `f124`, `f137`, `f144`, `f153`, `f163`, `f174`, and `f228`; each has 18 odd coefficients. The private target `f0` has none. A cover map applies an invertible binary owner transformation and adds only coefficient 2. Modulo two, it permutes the odd support without changing its size. A one-term line correction can remove at most one odd coefficient. The full proof is in [PROOF.md](PROOF.md).

The scoped bill is at least 144 rank-one line calls plus their 288 full-cover map operations, eight scalar copies priced at 32 real scalar primitives, and up to eight clear primitives if no existing next core follows. If that next core runs, its clears absorb the cleanup. The favorable rank-eight envelope leaves at most two additional rank-one-equivalent calls. Physical source access, map implementation, global hosting, and precision remain unpriced, and cannot rescue the line-call floor.

This is limited to the pinned registered map actions and one-term line model. Alternate private-field layouts or a native multi-term operation would be a different interface. No complete controller, supplier admission, or selected-bound change is claimed.

## Pins and predecessor

- Assignment seed: `ed361f3c876dd81e664556c9f95bd36e`, track `recursive-interfaces`, task `joint-query-controller`, priority revision 4.
- Scientific base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`.
- Selected-result SHA-256: `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
- Catalogue SHA-256: `d46eb6d5b3e279428753d770653663fbdf1063e55c255ea073d768f344927ef7`.
- Map/frame input: `research/joint-query/certificate.json.gz`, SHA-256 `a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7`.
- Direct predecessor: [PR #2197](https://github.com/CrocSwap/integer-mult-bounds/pull/2197), head `0a6f487ddff27cde0369e225f9ccb328ca2d8043`, which rejects one-map normalization and derives the one-term line floor. This package adds the parity invariant for arbitrary map depth.
- Interface motivation: [PR #2174](https://github.com/CrocSwap/integer-mult-bounds/pull/2174), the conditional two-query decoder; [PR #1969](https://github.com/CrocSwap/integer-mult-bounds/pull/1969), retained QQ16 maps and private fields.

## Reproduce

From the repository root:

```sh
python3 -I -B research/qq16-map-parity-floor-seed-ed361f3c/verify.py
python3 scripts/research_package.py --package research/qq16-map-parity-floor-seed-ed361f3c --check-only
```

Expected verifier line:

```text
PASS_QQ16_MAP_PARITY_FLOOR ports=8 maps=3650 frame_checks=29200 lines=144 cover_maps=288 no_kappa
```

The exact verifier and metadata/source-pin check passed locally on CPython 3.14.7. The registered package runner requests Python 3.12; it is unavailable locally.

## Open next questions

- **Can a changed private-field layout avoid the parity floor without using multi-term line operations?** This matters because the invariant closes only the fixed `C0..C7` relay. First step: propose exact target frames for all eight fields and compute the mod-2 support distance from each source frame under the same registered map action. Blocker: no native controller currently supplies an alternate owned-field layout with a full hosting and restoration invoice.

## Credit

Prepared by Cinna Davis with substantial OpenAI Codex assistance in scope selection, proof development, exact verifier implementation, and packaging. New work is Apache-2.0.
