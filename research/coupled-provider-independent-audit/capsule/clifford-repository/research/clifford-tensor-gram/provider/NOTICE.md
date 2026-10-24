# Provider sources and attribution

New material: Ali Romman, with substantial OpenAI Codex assistance in the
proof, implementation, checks and publication. Apache-2.0. The checks do not
constitute independent human review or a proof-kernel verification.

The source checkpoint is canonical main
`1ec1119972c9aefe42525172d07b332fcff81cb4`. `SOURCES.json` records exact
source paths, Git objects and SHA-256 values for the copied data.

- **Cao Yifan / intqwq** supplies the final
  [PR #4610](https://github.com/CrocSwap/integer-mult-bounds/pull/4610)
  native word and phase data. His
  [construction proof](https://github.com/CrocSwap/integer-mult-bounds/blob/1ec1119972c9aefe42525172d07b332fcff81cb4/research/kappa-round3-warp-20261022/PROOF.md)
  records the changed construction and its OpenAI assistance. `WORD.json.gz`
  and `PHASES.json.gz` are byte-exact copies of that selected source.
- **Chris R / Clear1nsight** supplies the
  [PR #5241](https://github.com/CrocSwap/integer-mult-bounds/pull/5241)
  independent admission and paid catalogue. `PAID.jsonl.gz` is a byte-exact
  copy. The [admission proof](https://github.com/CrocSwap/integer-mult-bounds/blob/1ec1119972c9aefe42525172d07b332fcff81cb4/research/final4610-independent-admission/PROOF.md)
  already contains a quantified free-group lift. The new work does not claim
  priority for that argument. The prior source uses substantial OpenAI
  Codex assistance and retains Apache-2.0.
- **Cinna Davis / 1337isnot1337** supplies the joint-helper, native warp,
  query-thinned controller and preceding construction chain. `HELPERS.json.gz`
  retains the recipes from the
  [joint-helper source](https://github.com/CrocSwap/integer-mult-bounds/blob/1ec1119972c9aefe42525172d07b332fcff81cb4/research/joint-helper-lattice/PROOF.md).
  **zxv**, **Jacob Alan Sussman** and **Dugongue** retain credit for productive
  helpers, mixed-target recursion and frame/physical interfaces. See the
  [selected contributor map](https://github.com/CrocSwap/integer-mult-bounds/blob/1ec1119972c9aefe42525172d07b332fcff81cb4/docs/research/community-native4610-contributors.md).
- **Rohan Arun**, **Jeremy Kothe** and the full native lineage supply the
  retained exact Clifford kernel. **Tekalign / tekuuu** retains it in the
  source package. The byte-exact kernel, scalar layer and full lineage
  notice remain in `../vendor/`. The scalar layer is from **zxv**.
- **icekylinx** supplies the earlier phase-lowering source, with Codex
  assistance. **DreamingOfClouds** supplies the wrapper source, with Claude
  Opus 5.5 assistance; that source credits **chafreaky** for the residual
  wrapper construction. Cinna Davis adds native warp support. The
  [phase source](https://github.com/CrocSwap/integer-mult-bounds/blob/1ec1119972c9aefe42525172d07b332fcff81cb4/research/t74-native-fast/vendor/native/new/code/borrow/bw_phases.py)
  gives the exact main-adapter formula used here. The
  [wrapper source](https://github.com/CrocSwap/integer-mult-bounds/blob/1ec1119972c9aefe42525172d07b332fcff81cb4/research/t74-native-fast/vendor/native/new/code/borrow/bw_adapters.py)
  retains the source notice and predecessor credit.

The [PR #5243 handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19147021)
motivates the initial paid-pair test. The separate
[PR #5393](https://github.com/CrocSwap/integer-mult-bounds/pull/5393) concerns
zero-row deletion and single-field reachability on a frozen eight-relation
provider. It is related work, not an input to this proof or an additional gain.

The source construction, proposed recipe compiler, new quadratic-sum checker,
complete word interpreters and literal witness checker have different roles.
The Gaussian scalar layer is shared. The proof and implementation are not
independent of all earlier source definitions. No general stabilizer-method
priority is claimed; the classical code and quadratic-form work is credited
in `../ADVANCES.md`.
