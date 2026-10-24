# Phase-exact native Clifford compilation and complete contact neighborhoods

This package gives a constructive compiler for changed physical charts and exact, complete transvection-neighbor enumerators for the complex supplier search. **It does not improve κ.** The requested new best bound was not achieved in this session. The strongest inspected complex source remains PR #4610, with crossing in (0.00302177587077, 0.00302177587078); PR #4713 transfers κ = 0.0030217758 through its conditional native Word RAM caller. The newer conditional ordinary BIT saving 0.003475458 of PR #4814 has a different scope and leaves the complex provider and selected whole κ unchanged. The large new claims in PR #4813 and PR #4818 need a priced all-width decoder; their finite observation inversion alone is not a complete supplier certificate (see [PR #4813 review](frontier/PR4813.md) and [PR #4818 review](frontier/PR4818.md)).

## Constructive results

1. [Compiler and assembly proof](compiler/CLIFFORD-COMPILER.md): a literal dyadic Clifford on b bits has an exact factorization into free affine/phase adapters and **one rank-d Gaussian call**, where d is its Fourier rank. Absolute global phase is retained. For b = 9, the native free adapters use fewer than 260 elementary linear passes per transition. The chronological gauge-substitution theorem preserves arbitrary independent inputs when its explicit chart, ownership and endpoint hypotheses hold.
2. [Complete single-contact neighborhood](decoder/COMPLETE-NEIGHBORS.md): every n-dimensional binary Lagrangian has exactly 2(2^n − 1) distinct changed transvection neighbors. At n = 9, 1,022 representatives replace 262,143 axes, with exact set completeness and multiplicity 256. This is a reduction in candidate count, not a measured 256-fold end-to-end speedup.
3. [Complete paired neighborhood](decoder/COMPLETE-PAIRED-NEIGHBORS.md): for distance r, exactly 2^(n+r+1) − 2^(2r) − 1 nontrivial joint neighbors suffice. At n = 9 and r = 1, this is 2,043. Every other incident edge, including incoherent parallel edges, remains priced.

4. [Compensated scalar retiming](retiming/RETIMING.md): an all-input chronological rewrite with explicit compensation, observable-read conditions, and wrong-sign controls. This provides changed controller graphs without assuming commutation of unrelated operators. Its current instantiated words are neutral in the paid moment.

These are sufficient constructive algorithms, not a claim that a low-rank chart objective alone certifies a supplier. Classical Clifford normal forms and finite symplectic geometry are predecessors; we claim no priority for those underlying ideas.

## Replay

From the repository root, run:

```sh
python3 -I -B research/native-clifford-gauge-compiler/verify.py
python3 -I -O -B research/native-clifford-gauge-compiler/verify.py
```

Python 3.12 standard library only; default replay does not invoke Git, a solver, a compiler, or the network. It checks exact dyadic matrices and phases, tensor lifts, physical-chart orientation, caller arithmetic and complete small symplectic neighborhoods. The actual source-derived contact graph checks 4,429 Lagrangians, 145 native maps and 79,360 sampled mapped-edge axes. It is a frozen search graph, not an executable replacement supplier. `regenerate_graph.py` rebuilds it from the included upstream actual-word payload and byte-identical retained `vendor/model.py`; regeneration is an optional offline provenance check. Tests remain active under `-O`.

Optional portable C++20 completeness replay:

```sh
c++ -O3 -std=c++20 research/native-clifford-gauge-compiler/decoder/neighbor_check.cpp -o neighbor_check
./neighbor_check research/native-clifford-gauge-compiler/decoder/ALL-SMALL-LAGRANGIANS.txt research/native-clifford-gauge-compiler/inputs/round3-contact-graph.txt
```

The optional `dynamic_neighbors.cpp` is bounded discovery tooling, with arguments `graph output seed passes [temperature]`. Its floating search objective is not an exponent certificate. Positive temperature accepts a best positive local move when no nonpositive move exists; it is not uniform random-neighbor annealing. Every accepted rank change is repriced by actual binary ranks. No host-specific compiler flags are required.

## Frontier combination and actual outcome

The session combined the round-3 warp supplier, general Gaussian contact graph, native caller, exact absolute-phase compilation, compensated scalar retiming, and complete single/paired contact neighborhoods. The inherited round-3 paid profile is {1: 2201, 2: 412, 3: 510, 4: 127, 5: 40, 8: 8}; helper targets are {4: 28, 7: 7, 8: 47, 9: 326}. No inspected complete candidate lowered its paid moment while preserving the target invoice. Neutral scalar alternatives and bounded searches are retained separately as supporting context; they do not establish a new κ or a global impossibility theorem.

The [review](decoder/CROSS-REVIEW-DYNAMIC.md) records the essential quadratic correction in the transvection tariff. A rejected exploratory quadratic-free tariff was not valid and is excluded from this package. Search receipt counts are not proof of a universal obstruction. Compiler arithmetic fixtures explicitly label hypothetical deletion scenarios; no physical completion deletion is exhibited.

## Attribution and overlap

Cao Yifan (intqwq), PR #4610, supplies the actual round-3 word and improved profile. Cinna Davis, PR #4690, supplies the general Gaussian contact model, and PR #4672 supplies the earlier round-2 contact optimization. PR #4713 and its retained PR #4630/#4635 dependencies supply the native caller. PR #4710 fixes the literal Gaussian phase convention. PR #4760 supplies the separate BIT-only source; ai-nanachi’s PR #4814 improves its ordinary backend through rohanarun’s #185 finite-leaf bootstrap and the #199/#204 recurrence lineage. PR #4703 and PR #4797 provide useful partial ports but not a complete improved complex supplier. PR #4792 is our preceding literature/port dossier, not an independent new provider. All original supplier, Clifford, borrowed-owner, tensor, precision and analytic/recovery contributors retain their upstream credit and licenses. See [NOTICE](NOTICE.md) for exact links and source scope. Classical Clifford structure is credited to Bravyi and Maslov; no broad mathematical novelty or independent human review is claimed. Prepared by Dugongue with OpenAI Codex and three Codex agents.

Local discovery also consulted the existing MathProof DAG and tensor-isomorphism/symplectic proof tree as inspiration. No local Lean theorem is imported or advertised as a certificate here, no private proof headers are copied, and no Lean formalization or fresh kernel audit is claimed.

## Final upstream checkpoint

Canonical main advanced to `9e33ecf009d36118f49ac86e9a0ee36e38dca44f` during the session. The branch was refreshed onto it; the guides, priority revision 7 and selected-result certificate were unchanged. Discovery inputs remain frozen at the earlier canonical `624de9dc66858af0945e5f8a0942488d62280d43`. New PR #4813 was inspected as source evidence, without changing the selected frontier. The release does not treat newly merged observation-code claims as an automatic maintainer-reviewed frontier replacement.

## Open next questions

- Find a concrete changed chart/controller program with a strict full paid-moment gain; every bridge, helper endpoint and owner obligation must be included.
- Bind a successful geometric candidate to literal phase-correct chronological charts and verify its arbitrary-input endpoint, dual interface and productive targets.
- Recompute source-uniform compiler constants, precision, mirror inequalities and the native caller on that actual source before asserting a higher κ. The compiler theorem does not discharge these source-specific obligations automatically.
