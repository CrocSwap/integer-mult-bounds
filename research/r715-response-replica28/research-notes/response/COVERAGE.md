# Search coverage

Searched all five registered source catalogues: workspace-sources, anthropic-flt, community-math, prove2me-public, today-cscc. Queries: Schur, Woodbury, transvection, rank factorization, block matrices, quivers. Exact bounded results and source locations are saved in catalogue-hits.json. These are not claims that every source file was read.

Queried the canonical typed DAG by operator combinations, not only names: Matrix.mul+Matrix.fromBlocks, Matrix.mul+Matrix.single, LinearMap.ker+LinearMap.comp, Matrix.mulVec+Matrix.add. Results saved in typed-structure-hits.json. The broad kernel/composition query is capped at40 results; this is explicitly a structural shortlist, not exhaustive DAG inspection.

Read actual declarations and proof bodies from four external/library sources; source hashes and lines are in SOURCES.json. ReasBook contains proofs rather than just names. The prove2me Woodbury catalogue record ends in sorry and was treated solely as a nomination, never as proof evidence. RankFactorization hits in EconCSLib concern Mallows rankings, not matrix rank, and were rejected as a semantic false match. Anthropic FLT Schur hits concerned Schur multipliers, not Schur complements, and were likewise not used.

The canonical DAG was queried read-only. No Lean source, import, build, or catalogue was changed. No full kernel replay was performed because this task requests pure mathematics and executable finite certificates.

Research-route controller note: invoked its init command on the saved pure-math route-plan.json. The controller rejected the English target because it requires a Lean theorem header. No dummy theorem was substituted; this task does not request Lean formalization. The sufficient assembly and bounded methods remain recorded directly in route-plan.json and PROOF.md.
