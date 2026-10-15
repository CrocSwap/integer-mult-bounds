## Scope and result

**Scoped all-depth obstruction; no new kappa.** At the exact post-`B_1_2` QQ16 cut, the eight `Y_A` output frames each have 18 odd Z4 terms, while the existing private fields `C0..C7` return in the zero frame. Every registered cover map applies an invertible binary owner transform and adds only coefficient 2. Modulo two, the payload shift vanishes and the owner transform preserves odd-support size. Therefore every finite composition of cover maps leaves all eight frames at odd-support weight 18; this rules out depth-one, depth-two, depth-three, and longer map-only normalization.

In the declared one-term native-line model, one rank-one correction changes at most one parity bit. Reaching the private zero frames requires at least 18 corrections per output, or **144 rank-one line calls** total. This exceeds by 72 times the favorable budget of at most two extra rank-one-equivalent operations after the rank-eight output charge. The bill also includes 288 associated full-cover map operations, eight scalar copies priced at 32 real primitives, and up to eight terminal clear primitives (zero additional clears if the existing next core follows). Further map implementation, hosting, source routing, and precision charges cannot lower the line floor.

This extends the released one-map / one-term result in PR #2197 with an all-depth invariant. It is limited to the pinned eight frames, registered invertible cover maps, and one-term Z4 corrections. Alternate field layouts and multi-term native operations remain open. No full controller, supplier admission, or selected-bound change is claimed.

## Exact evidence and reproduction

The source-pinned verifier reconstructs the eight port frames from the native recipes, checks all 3,650 owner maps for rank 73, applies every map to every port frame (29,200 checks), and validates a two-map positive control. Negative controls demonstrate that an odd coefficient shift could cancel a parity bit and that a singular owner map violates the invariant's hypothesis.

```sh
python3 -I -B research/qq16-map-parity-floor-seed-ed361f3c/verify.py
python3 scripts/research_package.py --package research/qq16-map-parity-floor-seed-ed361f3c --check-only
```

Both commands pass locally under CPython 3.14.7. The registered package replay requests Python 3.12, which is unavailable locally.

## Pins and predecessor attribution

- Seed `ed361f3c876dd81e664556c9f95bd36e`; `recursive-interfaces`, `joint-query-controller`, priority revision 4.
- Scientific base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`.
- Selected-result SHA-256 `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
- Catalogue SHA-256 `d46eb6d5b3e279428753d770653663fbdf1063e55c255ea073d768f344927ef7`.
- Map/frame input SHA-256 `a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7`.
- Predecessor [PR #2197](https://github.com/CrocSwap/integer-mult-bounds/pull/2197), head `0a6f487ddff27cde0369e225f9ccb328ca2d8043`, identifies the one-map obstruction and releases the depth-two/three question. This package proves the parity floor for every composition depth using the map law in the selected source certificate.
- [PR #2174](https://github.com/CrocSwap/integer-mult-bounds/pull/2174) supplies the conditional two-query decoder; merged [PR #1969](https://github.com/CrocSwap/integer-mult-bounds/pull/1969) supplies retained QQ16 map and private-field conventions.

Prepared by Cinna Davis with substantial OpenAI Codex assistance in scope selection, proof development, exact verifier implementation, and packaging. Apache-2.0.
