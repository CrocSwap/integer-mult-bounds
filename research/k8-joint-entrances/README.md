# Joint entrance choices on the eight-endpoint k8 word

The admitted conditional value is **κ = 0.001675560947524449**, **0.0262249453%** above the preceding three-demotion result, 0.001675121647789207.

The search now tests all 64 subsets of the six individually selected dimension-five entrance reductions. The best tested composition uses groups 603, 611, and 635. Relative to the preceding package, group 619 is restored and group 635 enters the four-dimensional space `[298,170,102,30]`. Joint frame refitting replaces eight local rank-one children with four rank-two children. The occupied-width inventory is unchanged, so an exact permutation transfers the existing whole-helper slots; there is no new packing optimization in the admitted witness.

The paid local profile is `{1:2364,2:498,3:412,4:130,5:82,8:8}`. The achieved value is distinct from the new exact fixed-family all-replica grid upper bound, **0.001675568675201533**. That bound does not cover different local words or recursion geometries.

Fresh native replay checks all 704 columns in both orientations and 2,904 directed phase checks. The independent local audit, 27 local semantic controls, unchanged global admission engines, all 102 global negative controls, and 47 strict outer inequalities pass. See `CLAIM.json`, `PROOF.md`, and `evidence/`.

All 18 repository `make verify` groups also completed across the initial and resumed runs, including all 87 isolated test modules and 20 patch applicability checks. The initial runs stopped on an older Python's missing `int.bit_count` and Apple clang's unsupported OpenMP option. The remaining stages passed under Python 3.11.14 and GCC 16.2.0. This was not a single successful `make verify` invocation; `evidence/REPOSITORY-VERIFICATION.json` and its archived logs record the coverage and both environment failures separately from the witness admission.

The inherited all-size compiler, common-label/mutable-source realization, whole-call hosting, precision/tape, analytic-transfer, and bit H1–H5 assumptions remain. Scalar operations, coefficients, and order are unchanged. This is an incremental conditional result, not a new scalar circuit topology or an unconditional multiplication theorem.

## Reproduce

Use Python 3.11+, a C++ compiler, and Boost headers. Choose a new output directory outside the repository. No optimization solver runs during verification.

```sh
CPLUS_INCLUDE_PATH=/path/to/boost python -B research/k8-joint-entrances/verify.py \
  --base "$BASE" --work /absolute/new/output-directory
```

`BASE` is the original R480 k8 + seven-slot raw word pinned in `../k8-eight-ends/RECIPE.json`. The command rebuilds the preceding T16 witness, applies the literal new recipe, replays the new local word, and runs full strict global admission. As in the predecessor, explicitly completed replays can be supplied with `--parent-from /path/to/completed-t16-wrapper` and `--native-from /path/to/completed-new-native-replay`; the verifier checks every consumed parent file and the native semantic identities and reruns local controls and complete global admission.

The global driver is the unmodified `../k8-three-demotions/run_global.py`. All global admission, controller, invoice, arithmetic, mutation, and independent-window engines remain byte-identical to the credited PR1074 files pinned in `../k8-eight-ends-t16`.

## Search scope

`discovery/` records nominations separately from the admitted claim. The 64-subset search is exhaustive only over the one selected entrance space for each of the six groups. The subsequent same-dimension rotation and joint entrance/frame searches examine broader choices; their floating optimization results are not exact optimality certificates. The fixed-family bound in `evidence/ALL-T-BOUND.json` is a separate exact proof about the final frozen word and inventory.

There were 354 additional same-dimension rotation trials, with no improving nomination. A joint search over 68 independent helper entrances and their gate frames also retained the same profile. A further joint dimension/packing model allowed 56 helpers to choose dimension four or five individually, with fractional aggregate packing. Its floating mixed-integer solver found a different local inventory and profile but the same relaxed exponent to numerical precision. These results narrow this tested family; they do not rule out a different scalar word or geometry.

A broader formulation over 192 entrances produced a 1,806,543-column LP. The first solve was stopped after more than ten minutes without a returned solution; a second method reached its 180-second solver limit with no primal solution. This attempt is inconclusive and supplies neither a better witness nor an impossibility proof. Its scripts and traces are retained separately.

Follow-up searches completed for all dimension-three/four/five choices, and then all 374 subspaces of each five-dimensional ceiling, on the fourteen larger entrance groups. Both floating mixed-integer searches retained the same relaxed exponent. Another 145 screens removed one-dimensional entrances individually, by shared-point cohort, or all together; none improved it. These results are scoped to the tested entrances and unchanged scalar word.

To rerun discovery, give each script an external `--work` directory. Run `search_compositions.py`, copy its `best-composition.json.gz` to `candidate.json.gz` in that directory, and then run `interface_census.py`. The rotation and joint search scripts consume that candidate and census. SciPy is needed for discovery, but not for the frozen verification command above. `prepare_equal_inventory.py` accepts `--native` and `--out` and binds a completed native word to slots only when the old and new width inventories agree.

PR1111 by seslly/shipstuff supplied the group-635 entrance-demotion lead. This contribution composes that lead with two further entrance groups, the eight rank-seven endpoints, refitted frames, and the existing T16 owner construction. It does not claim to originate the group-635 demotion. See `NOTICE.md` for the retained sources and AI-assistance disclosure.
