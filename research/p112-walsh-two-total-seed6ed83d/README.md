# P112 two-total Walsh shears have a uniform copy profile

**Scoped finite negative result. No κ, supplier, or new frontier is claimed.**

For the P112 coordinate matrix `X`, let `chi_a(b)=(-1)^<a,b>` be the eight Walsh characters of `F_2^3`. Choose ordered pairs of distinct characters for columns of `U,V` (56 choices each). Also allow the identity basis and the four elementary unimodular shears

```text
M = [[1, s], [0, 1]] or [[1, 0], [s, 1]],  s in {-1,+1},
U' = U M,  V' = V M^(-T).
```

Each of the resulting **15,680 parameter tuples** gives the exact asymmetric ten-term identity

```text
D = [X, XU']
T = [X(I - V'U'^T), XV']
DT^T = XX^T = 2G.
```

The shear changes the two rank-two factor bases while preserving `U'V'^T=UV^T`; the verifier recomputes every term's support cost after the change. Across all 15,680 tuples, the exact ten-term pairing-rank histogram is always

```text
{8: 8, 9: 2}; total invoice 82.
```

Replacing the incumbent's eight rank-8 center terms (invoice 64) with this decoder, while leaving the other 5,522 local rank units unchanged, gives local profile `{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8, 9:2}` and center charge 82. Under the selected width-73, 896-family, nine-stage coverage law and rank-51 idle cap, the exact packing ceiling is

```text
834274164361/1000000000000000 <= a <= 417137082181/500000000000000
```

The upper endpoint is about `0.000834274164362`, below the incumbent ceiling `0.001690054109089` and the 5% gate `0.001774556814543`. This is a scoped obstruction for the listed finite Walsh-character bases. Its favorable ceiling already waives added source access, frames, adaptation, restoration, hosting, precision and interface costs. The result does not bound arbitrary real rank-two lifts.

## Evidence and reproduction

`verify.py` reconstructs the pinned P112 geometry, checks `XX^T=2G`, and enumerates all 56-by-56 character-pair choices in five bases: identity plus the four matrices above. Every candidate's coefficient identity and invariant `UV^T` are checked exactly. The 10 support-pairing ranks are computed with a local binary-elimination implementation and cross-checked against the pinned geometry routine. Each distinct profile is priced with the pinned exact-rational `ceiling()` implementation.

The certificate contains the per-basis census and a SHA-256 digest of the deterministic 15,680-row rank receipt. Positive controls check the symbolic identity and one full 112-by-112 matrix identity. Negative controls reject a wrong sign, a dropped rank-two term, and a repeated-character pair. `-O` is supported because all guards use explicit exceptions.

From the repository root:

```sh
python3 -I -B research/p112-walsh-two-total-seed6ed83d/verify.py --write
python3 -I -O -B research/p112-walsh-two-total-seed6ed83d/verify.py
python3 scripts/research_package.py --package research/p112-walsh-two-total-seed6ed83d --check-only
python3 scripts/research_package.py --package research/p112-walsh-two-total-seed6ed83d
```

The first command writes `RESULT.json`; the next two recompute and validate it. The registered generic replay targets Python 3.12. Direct local verification was run with CPython 3.14.7 because Python 3.12 is not installed on this host.

## Overlap and contribution boundary

- **PR #1197**, merged at head `a0935afff6cc5540a582c5881bc8d5f98b587357`, proves the two-extra-total floor for rank-one additions, off-column readers and disjoint supports. Its remaining coupled rank-two, overlapping-support case includes this parameter family. This package searches only its finite Walsh subfamily.
- **PR #1923**, merged at head `0d33d6020aa50d383067510df78dcc0515bba4f4`, searches 29,524 rational Householder gauges of one fixed symmetric ten-term witness and finds invoice 82 throughout. Here `D` and `T` use an asymmetric rank-two shear with independently chosen character planes, followed by four nonorthogonal basis changes. The parameterizations differ; this package does not claim that their candidate sets are disjoint.
- **PR #2022**, open at head `92ee132d0baf07f7ddf0fbbcd12756be8429bbf7`, gives a broader at-most-eleven-total cost floor and cost-40 witnesses for its fixed Eisenstein decoder. This package makes no competing optimum claim; its added evidence is the exact profile census for the stated asymmetric family.
- **PR #2021** concerns masked two-column completion rank, not this all-pairs ten-term factor invoice.
- Active adjacent claims checked in the final board scan: #2003 studies a paired-tetrad masked decoder, #1952 a cyclic masked rank-three child profile, and #1987 a Karatsuba block inside the selected local word. They change different exactness, factor-count, or source-interface assumptions. #1693 is completed by PR #1703 and concerns retiming the selected word.

The final overlap refresh at 17:53:48–17:55:25 UTC had complete pagination, no warnings, 364 open PRs and 680 Discussion records. No competing Walsh-shear claim appeared. The live claim and its intermediate result are recorded in [Discussion #2028](https://github.com/CrocSwap/integer-mult-bounds/discussions/2028). The scoped claim is not a novelty certificate for other coefficient families.

## Open next questions

Does an arbitrary full-rank real or rational pair `U,V` with overlapping coefficient support produce a lower recursive profile than the finite Walsh-shear family? It matters because PR #1197 leaves precisely this coupled class open, and a profile with lower charged center invoice could change the complex-side packing ceiling. A first step is to derive support strata for `U,V` and search rational points in strata that permit cancellation; then price the complete profile and charge frame/restoration work. The blocker is that support changes on continuous algebraic loci, so the finite character scan does not bound the whole class.

## Provenance and credit

Assignment seed `6ed83d31ab93b3878e4fc74abdee2988`, track `complex-mechanisms`, task `complex-rank-shape-decoder`, priority revision 3. Exact base `ec8707299e2f40918f5f96cdab99ee49cdbabcf0`; selected-record SHA-256 `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`. Source pins are in `SOURCES.json`.

Credit DreamingOfClouds / PR717 and Mihir Srivastava / PR845 for the P112 geometry and pairing-cost model; Philipp / @mightyOil / PR1197 for the remaining coupled rank-two boundary; Hanson Sun / PR1633 and its PR1923 follow-up; and Charles Bethin / PR2022 for the broader fixed-decoder floor. Prepared by Cinna with substantial OpenAI Codex assistance in scope selection, derivation, implementation, exact verification and writing. No independent human review or proof-assistant validation is claimed. New work is Apache-2.0.
