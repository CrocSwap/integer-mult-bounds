## Problem

The actual complete finite Core returns an unnormalized global tensor on its
native two's-complement grid. The source-bound first-face halo of
CrocSwap/integer-mult-bounds#6904 uses normalized sign-magnitude records and
immutable pre-Core data. The generic splice and a bit-complementing Core fixture
do not establish that physical source/precision boundary.

## Result and changes

This package proves and implements a conditional source-bound bridge: full-field
input radius R sqrt(T), exact original Reference/axis/context matching, exact
external-to-native grid lift, real native Core invocation, one division by the
complete dyadic normalizer 2^U, paid final toward-zero rounding, protected return
consumption and current-field commit. Its additional component-l1 defect is
`2^(-t-U)+2^(1-q)` and its full new payload tariff is `O(TF)` for
`F=d+w+(P-q)+(P+U-q)+1`, with ten fixed roles and historical blank backing
retained. The full inherited Core, halo and source-production bills remain.

The whole-field input volume and the complex norm2/component-l1 factor are
explicit. The proof does not assign an unsupported per-axis normalized-radius
induction to the unnormalized native Core. The least dyadic normalizers are
polynomially bounded from the inherited gap; larger choices retain an explicit
uniform `a_i<=p^C` premise.

## Novelty and dependencies

CrocSwap/integer-mult-bounds#6880 owns the locality and generic normalized splice;
CrocSwap/integer-mult-bounds#6904 and its predecessors own the sparse transport
and shrinking halo. The concurrent complete-Core package owns its real five
factor caller, original-coordinate routes and global error/cost theorem. This
contribution is the actual source/format/normalization/lifecycle seam and its
complete scan accounting, not a new version of those predecessor results.

Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
Complete Core: [public immutable head](https://github.com/CubeJerry/integer-mult-bounds/commit/6fb9ab776b7d0956b8bcc2d3cfde0f3034421630).
All 77 retained Core blobs match that public tree. The initially local snapshot's
only publication delta adds an explicit address/width cost guard; executable
and numerical bodies did not change. Exact pins and the comparison are included.

## Reproduction and executed checks

```sh
python3 -B scripts/research_package.py --package research/core-halo-source-bridge
python3 -B scripts/check_research_commit.py --package research/core-halo-source-bridge --check-modes
python3 -B research/core-halo-source-bridge/verify_actual_core.py --output /tmp/core-halo-actual.json
```

Normal and optimized codec/binding checks pass: 3,936 signed/grid cases, 160
native extremes, 34 failure/detection controls, all 512 natural coordinates,
two actual References, 16 original source partitions and 11 binding controls.
Cost fixtures include borrowed-port actions and final commit. Failures after
the native callee takes ownership preserve the original and saved streams and
erase pending bridge payload.

The actual packed native Core witness completed in about 311 seconds: three
dense calls with 189 events, both sparse native calls, all borrowed source
ports restored and all bridge-owned payload blank. An independent exact
2-by-2 inverse checks the endpoint. Use `replay.py --physical` for the combined
bounded replay and scientific/machine-count receipt comparison. The default
quick replay does not rerun the expensive native witness.

## Limits and kappa status

**No new kappa. All five selected foundational assumptions remain.** The real
native fixture is K=1,g=1,L=2 with coupled nonidentity Q but scalar interior A=1;
it is not a complete original-layout Core plus halo geometry execution. Source
program preparation remains an admitted, paid predecessor contract. Production
carving including empty-interior contexts, outer-group radius/grid continuation,
ideal-transform comparison and final integer-recovery scales remain open.
Finite evidence is not a universal source admission or an unconditional theorem.

## Credit

Prepared for **@CubeJerry** with substantial OpenAI assistance. Jose Manuel /
jmbarrancoml, Mason Hale, Cinna Davis, Vlado Vojdanovski, Jeremy Kothe, Ryanson
Jonathan, Mihir Srivastava, JoyboyBrian, Chafik and the retained physical/source
contributors retain their original attribution. Full notices and unchanged
predecessor source bodies are included. The parent separately reviewed the
proof algebra and source contract; that scoped AI review is not human
acceptance or proof-assistant verification. Apache-2.0.
