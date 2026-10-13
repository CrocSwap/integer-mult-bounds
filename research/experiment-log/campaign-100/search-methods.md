# Search Methods

Historical campaign entries 61–75; original statuses and scope are preserved. This is a topic index, not a claim that all proposals ran. Baselines vary and must be read in the linked reports.

## 61. GNN surrogate of physical κ

Status: `partial_experiment`. Ridge, boosted regression and MLP surrogates were evaluated, not a GNN. Coarse rankings help, fine rankings and module features fail; 20 historical module labels disagreed on replay.

Evidence: [reports/D-RESULT.md](https://github.com/rohanarun/integer-mult-bounds/blob/fa8ab946df57ebadae1a470b637c2a590a0a5317/research/campaign-100-results/reports/D-RESULT.md)

## 62. AlphaDev-style reinforcement learning

Status: `not_evidenced`. No execution result located in the archived campaign evidence; do not count this proposal as a completed test.

Evidence: No located execution result.

## 63. Evolutionary search with crossover

Status: `partial_gain`. 1,695 evaluations across population methods found plane-order gains on the old baseline; crossover added no benefit beyond that plateau, and gains did not simply compose through later stages.

Evidence: [reports/C-RESULT.md](https://github.com/rohanarun/integer-mult-bounds/blob/fa8ab946df57ebadae1a470b637c2a590a0a5317/research/campaign-100-results/reports/C-RESULT.md), [reports/P-RESULT.md](https://github.com/rohanarun/integer-mult-bounds/blob/fa8ab946df57ebadae1a470b637c2a590a0a5317/research/campaign-100-results/reports/P-RESULT.md)

## 64. LLM program synthesis

Status: `not_evidenced`. No execution result located in the archived campaign evidence; do not count this proposal as a completed test.

Evidence: No located execution result.

## 65. MCTS

Status: `not_evidenced`. No execution result located in the archived campaign evidence; do not count this proposal as a completed test.

Evidence: No located execution result.

## 66. Large-neighbourhood search

Status: `partial_experiment`. CP-SAT LNS was run on module roots/supports, not the proposed sliding windows of about 1,000 word gates. No corrected module gain.

Evidence: [reports/O-RESULT.md](https://github.com/rohanarun/integer-mult-bounds/blob/fa8ab946df57ebadae1a470b637c2a590a0a5317/research/campaign-100-results/reports/O-RESULT.md)

## 67. Tabu search

Status: `bounded_no_gain`. Tested packing tabu moves did not improve their starting seeds.

Evidence: [reports/K-RESULT.md](https://github.com/rohanarun/integer-mult-bounds/blob/fa8ab946df57ebadae1a470b637c2a590a0a5317/research/campaign-100-results/reports/K-RESULT.md)

## 68. QUBO on a quantum annealer

Status: `not_evidenced`. No execution result located in the archived campaign evidence; do not count this proposal as a completed test.

Evidence: No located execution result.

## 69. Bayesian optimisation

Status: `partial_gain`. Bayesian knob search found a small PLAIN=12 gain on the old source; it lost on the later oriented source.

Evidence: [reports/C-RESULT.md](https://github.com/rohanarun/integer-mult-bounds/blob/fa8ab946df57ebadae1a470b637c2a590a0a5317/research/campaign-100-results/reports/C-RESULT.md), [reports/P-RESULT.md](https://github.com/rohanarun/integer-mult-bounds/blob/fa8ab946df57ebadae1a470b637c2a590a0a5317/research/campaign-100-results/reports/P-RESULT.md)

## 70. Differentiable frames

Status: `not_evidenced`. No execution result located in the archived campaign evidence; do not count this proposal as a completed test.

Evidence: No located execution result.

## 71. Learned restart distributions

Status: `bounded_no_gain`. Learned restart distributions matched the plain-restart plateau; no superior verified kappa.

Evidence: [reports/K-RESULT.md](https://github.com/rohanarun/integer-mult-bounds/blob/fa8ab946df57ebadae1a470b637c2a590a0a5317/research/campaign-100-results/reports/K-RESULT.md)

## 72. Cross-size transfer

Status: `partial_experiment`. Coordinate restrictions transferred modules across sizes; the proposed learned embedding was not trained.

Evidence: [reports/A-RESULT.md](https://github.com/rohanarun/integer-mult-bounds/blob/fa8ab946df57ebadae1a470b637c2a590a0a5317/research/campaign-100-results/reports/A-RESULT.md)

## 73. Quality-diversity (MAP-Elites)

Status: `partial_gain`. MAP-Elites reached the plane-order gain but did not improve the shared plateau; no distinct methodology advantage established.

Evidence: [reports/C-RESULT.md](https://github.com/rohanarun/integer-mult-bounds/blob/fa8ab946df57ebadae1a470b637c2a590a0a5317/research/campaign-100-results/reports/C-RESULT.md)

## 74. Cross-entropy method

Status: `partial_gain`. Matching/search variants include a reproducible min-cost matching gain of about 0.0082 percent on the old baseline; not evidence that the exact proposed cross-entropy method succeeded.

Evidence: [reports/C-RESULT.md](https://github.com/rohanarun/integer-mult-bounds/blob/fa8ab946df57ebadae1a470b637c2a590a0a5317/research/campaign-100-results/reports/C-RESULT.md), [reports/I-RESULT.md](https://github.com/rohanarun/integer-mult-bounds/blob/fa8ab946df57ebadae1a470b637c2a590a0a5317/research/campaign-100-results/reports/I-RESULT.md)

## 75. 10,000-sandbox population search

Status: `not_evidenced`. No execution result located in the archived campaign evidence; do not count this proposal as a completed test.

Evidence: No located execution result.

