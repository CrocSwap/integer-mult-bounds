# Verification and evidence limits

The core comparison is between the canonical base e54523517d0f03e58352e647c403a5af3e525a57, the mixed application at 87fbf4f7b35b0f18ab12b5767775a9a424cf0b15, and the native realization at a7f99a5f5f919dd3ffb2987f90c1e7d6527feb1e. The two latter commits use different binary tensor powers and prices. Only the matching native graphs, port identities, scalar programs and selected route constructions transfer. [Mixed verification](https://github.com/CrocSwap/integer-mult-bounds/blob/87fbf4f7b35b0f18ab12b5767775a9a424cf0b15/research/p104-mixed-rank-supplier/README.md) · [Native verification](https://github.com/CrocSwap/integer-mult-bounds/blob/a7f99a5f5f919dd3ffb2987f90c1e7d6527feb1e/research/grade14-native-realization/VALIDATION.md)

## Reproduce the pinned scientific checks

Use CPython 3.12 and a Git checkout of this contribution. The registered, network-free finite tests use only the standard library and files inside the package.

```sh
python3.12 -B scripts/research_package.py --package research/mixed-rank-uniform-composition
```

These tests include 10,404 dirty frame returns, nesting to depth 1,000, exact five-factor checks on the two periodic bands, an 18-layer fixed schedule at different coarse matchings, 1,152 mixed-width signed ring positions checked against independent characters, and a full joined numerical product probe. That probe generates its two physical Gaussian pages, runs positive and opposite signed C-based ring schedules, multiplies signed packed short polynomials, rounds, and carries. It reproduces 741503 × 466013 = 345550037539 with pre-carry coefficients [11811, 10996, 4152, 868, 77]. Its 5×7 source, 8×8 target and test divisor 64 exercise the interface. The [integer coefficient producer](gaussian_pages.py) supplies its 96-bit Gaussian numerators. The small five-factor application and chirp evaluation use host complex arithmetic. The [independent page audit](GAUSSIAN-PAGES.md) also checks every row of the fine-prime 1013-to-1024 and 2029-to-2048 maps, 1,148 independent coefficient samples, every recovery diagonal and 55 nonzero repeated occurrences on a short period. The small CRT uses direct coordinate addressing, and the H and blocked Gaussian operators use small mathematical realizations. A small test cannot instantiate this proposal's astronomical actual finite suppliers or certify their movement.

The following additional replay reads immutable Git objects. From a fresh clone, fetch the PR histories first. The verifier resolves the pinned commits, even if a fetched branch gains later commits.

```sh
git fetch https://github.com/CrocSwap/integer-mult-bounds.git refs/pull/7830/head refs/pull/7837/head refs/pull/7786/head
python3.12 -IB research/mixed-rank-uniform-composition/replay_sources.py --cache /tmp/mixed-rank-sources --fetch
```

Omit `--fetch` to reuse a populated authenticated cache. The mixed producer authenticates 21 direct and 127 inherited bindings. Its RESULT, BIT and AUDIT match the published bytes. Its complete application and audit agree byte-for-byte with the source's separately written reviewer, which shares the authenticated rational evaluator. Both have their original conditional receipt meaning. The new [compiler proof](COMPILER.md) and Lean price certificates establish the implications used beyond those receipts. The wrapper's final output includes

```text
APPLICATION.json 2bf9baed27a0b26fded815b061466ee6ceba4c05549818604b3d5bdcbcd8e50b
AUDIT.json a4f318b83a810758bc9dc80eec15326e2794441f36d872aa24811b61c5d9f376
PASS_PINNED_COMPLETE_APPLICATION_AND_NATIVE_REPLAYS
```

The raw rational and binary hashes are 7660985e0b618cdbee13e4190a4c6d5f91fbdf01a8f7a5186fdde8b980c19b48 and d3aa4426fa8fe7dc167270d01f2515184f2bff6a82744a14e941c5dd3afca27d respectively. The matching-layout hash is f7de788c4a559282d35a9fce42f841a0e8de5a4015db871e718f9245569b0aa7. The complex forward and transpose word both pass exactly 1,661,521 scalar positions. The two binary orientations each pass 462,400 native positions. The atlas rebuild gives c7173d46c95d1311b8b18a92c874fb7013c6e694aa8e9c0c256f0f1eaf1ede74. The separate source/ownership checks count 220,217 rational donor occurrences, 4,234 peak binary slots, 133,360 high-row address occurrences and 877,896 padded opaque radix records. The fresh 960 weighted leaf examples include 400 nonzero nonunits. Wrong weighting and reversal are checked independently. The complete five premise names still occur in the old immutable machine receipt.

## Kernel verification

Use the official [Lean 4.34.1 release](https://github.com/leanprover/lean4/releases/tag/v4.34.1) and the mathlib revision d13f23b723b8a846827a245b89c10fc7d3f11612. All dependency revisions are in [the Lake manifest](lean/lake-manifest.json). From a fresh checkout with this toolchain run

```sh
cd research/mixed-rank-uniform-composition/lean
lake exe cache get
lake --wfail build
lake env leanchecker -v CompilerFlow CoverRows Funding DyadicRoot RankMoments CertifiedPrices PhysicalFrames PhaseBudget SyntheticBridge HaloRadius Coordinates Recovery Integrated OuterPrices RankOneBridge RationalInverse PublicGrid
```

The caches supply mathlib build artifacts. A source build at the same pins also works with the Lean toolchain. This work was built with the release compiler at 5045d0056413266e57c625dcd7c365b10e377c52. The arm64 Darwin release archive used for the build had SHA-256 65f22a4f047738ec742667b3247e836a86ebf06eabc12655c3dee00637e37866. The formal code contains no proof placeholders, added mathematical axioms or native evaluation oracles. The named declarations print their axiom sets as they build. Their union is `propext`, `Classical.choice` and `Quot.sound`. A number of arithmetic comparisons depend on none. The trusted formal base includes the Lean kernel and the imported library at the specified revisions. Kernel checking establishes the formal statements at the types in these files.

| Formal part | Statement checked | What connects it to the actual construction |
|---|---|---|
| [CompilerFlow](lean/CompilerFlow.lean), [CoverRows](lean/CoverRows.lean) | Literal finite occurrence enumeration, edge matching, external sources, cancellation, horizons, batch billing and exact full-high row quotient/inverse | The source-specific product and price proof, row tape split and role adapters are written in [COMPILER.md](COMPILER.md) and [ORDINARY.md](ORDINARY.md). |
| [DyadicRoot](lean/DyadicRoot.lean), [RankMoments](lean/RankMoments.lean), [Funding](lean/Funding.lean), [CertifiedPrices](lean/CertifiedPrices.lean) | 109 interval bounds on the exact rational powers from the real rank histograms, both separated budgets, cold start, all six rates, finite carrier slack | The generator proposes dyadic endpoints and binds the data. The kernel checks every integer power bound by outward arithmetic. Monotonicity of real positive powers and the compiler recurrence interpret those integer inequalities in the price theorem. |
| [PhysicalFrames](lean/PhysicalFrames.lean), [PhaseBudget](lean/PhaseBudget.lean), [RankOneBridge](lean/RankOneBridge.lean) | Push/pop behavior and counted transitions at arbitrary saved heads, historical chain estimate, phase precision compounding, reduced Gaussian denominator, and the covered good-leaf operator | The dirty field owners, exact noncommutative chart argument, finite bad-low schedule and all physical primitive tariffs are tied to their sources in [FRAMES.md](FRAMES.md) and [WEIGHTED-REVIEW.md](WEIGHTED-REVIEW.md). |
| [SyntheticBridge](lean/SyntheticBridge.lean), [HaloRadius](lean/HaloRadius.lean), [RationalInverse](lean/RationalInverse.lean) | The exact signed C-to-H character for all widths and inputs, actual rounded Horner radius and error, finite dependency cone, existence and uniqueness of the exact rational inverse, spectral tail and disjoint face splice | See [formal coefficient and carrier bindings](GAUSSIAN-FORMAL.md). The proofs of Gaussian accretivity, Poisson resampling and full-page physical movement are written proofs. |
| [Coordinates](lean/Coordinates.lean), [Recovery](lean/Recovery.lean), [Integrated](lean/Integrated.lean), [PublicGrid](lean/PublicGrid.lean) | Both cyclic factors, unit at the true CRT coordinates, propagated transform and pointwise error, radius, toward-zero grid conversions, strict half-unit rounding, actual word decoder and radix carry | [ASSEMBLY.md](ASSEMBLY.md) supplies the actual transforms at both signs, including entrance extensions of the finite-grid maps. The public-grid specialization requires only the internal accuracy of each raw transform on representable half-disk inputs. |
| [OuterPrices](lean/OuterPrices.lean) | All listed physical time powers, the CRT price and the strict ordinary-to-complex gap at the submitted κ | [The operation bill](RECOVERY-AND-COST.md) identifies which issued operations have each power. |

The formal project does not compile the entire Turing machine or prove a machine running-time theorem. The prime construction, finite-word semantics and all-column chart lifting, finite compilation's analytic majorant, complete spectrum/conditioning/locality arguments, fixed-tape route tariffs and their uniform asymptotic composition retain written proof steps. The all-size result is the conjunction of those arguments with the formal statements, the exact finite source facts and the cited established mathematics. The finite controls, ahead-of-time program construction and hosted CI have different evidentiary roles. No human peer review or practical fast-regime execution is asserted.
