# Word And Frame Search

Historical campaign entries 1–15; original statuses and scope are preserved. This is a topic index, not a claim that all proposals ran. Baselines vary and must be read in the linked reports.

## 1. Free-form word

Status: `partial_gain`. Bounded frame retiming improved the tested word. Full gate/operand/coefficient synthesis was not run. Later combined with CP-SAT in PR366.

Evidence: [reports/G-RESULT.md](https://github.com/rohanarun/integer-mult-bounds/blob/fa8ab946df57ebadae1a470b637c2a590a0a5317/research/campaign-100-results/reports/G-RESULT.md), [continuation/README.md](https://github.com/rohanarun/integer-mult-bounds/blob/fa8ab946df57ebadae1a470b637c2a590a0a5317/research/campaign-100-results/continuation/README.md)

## 2. Exhaustive cube-local design

Status: `bounded_no_gain`. All 11,471 node-minimal 24-node designs were priced in the reported finite class; no replacement beat the baseline. This is not an optimum over all words.

Evidence: [reports/L-RESULT.md](https://github.com/rohanarun/integer-mult-bounds/blob/fa8ab946df57ebadae1a470b637c2a590a0a5317/research/campaign-100-results/reports/L-RESULT.md)

## 3. Frame-lattice table

Status: `partial_gain`. Depth-2 meet/join candidates and zero-cost drift helped; this was not a table of every rational subspace.

Evidence: [reports/G-RESULT.md](https://github.com/rohanarun/integer-mult-bounds/blob/fa8ab946df57ebadae1a470b637c2a590a0a5317/research/campaign-100-results/reports/G-RESULT.md)

## 4. Whole-word ILP

Status: `partial_gain`. Bounded gate-frame CP-SAT models ran; the proposed months-long whole-word solve did not. PR366 extracted beneficial components from a time-limited FEASIBLE solve, without an optimality claim.

Evidence: [reports/H-RESULT.md](https://github.com/rohanarun/integer-mult-bounds/blob/fa8ab946df57ebadae1a470b637c2a590a0a5317/research/campaign-100-results/reports/H-RESULT.md), [continuation/README.md](https://github.com/rohanarun/integer-mult-bounds/blob/fa8ab946df57ebadae1a470b637c2a590a0a5317/research/campaign-100-results/continuation/README.md)

## 5. SAT-enumerate the pair module

Status: `bounded_no_gain`. Addition-minimal modules priced worse. Corrected SA/LNS found no module below 92 uncarried nodes; apparent 90/91-node results were invalid dangling-node artifacts.

Evidence: [reports/E-RESULT.md](https://github.com/rohanarun/integer-mult-bounds/blob/fa8ab946df57ebadae1a470b637c2a590a0a5317/research/campaign-100-results/reports/E-RESULT.md), [reports/O-RESULT.md](https://github.com/rohanarun/integer-mult-bounds/blob/fa8ab946df57ebadae1a470b637c2a590a0a5317/research/campaign-100-results/reports/O-RESULT.md)

## 6. Universal bank tiling table

Status: `not_evidenced`. No execution result located in the archived campaign evidence; do not count this proposal as a completed test.

Evidence: No located execution result.

## 7. Exact constant search in the outer polytope

Status: `analysis_only`. Related constant and margin what-ifs were priced, but no exhaustive exact outer-polytope search is evidenced.

Evidence: [reports/B-RESULT.md](https://github.com/rohanarun/integer-mult-bounds/blob/fa8ab946df57ebadae1a470b637c2a590a0a5317/research/campaign-100-results/reports/B-RESULT.md)

## 8. True root instead of certified root

Status: `bounded_no_gain`. Independent high-precision moment root agreed with certification; rounding slack was about one 1e-18 tick on the tested baseline.

Evidence: [reports/B-RESULT.md](https://github.com/rohanarun/integer-mult-bounds/blob/fa8ab946df57ebadae1a470b637c2a590a0a5317/research/campaign-100-results/reports/B-RESULT.md)

## 9. Largest-ever complex supplier

Status: `blocked`. The original largest-size complex-supplier experiment was blocked by unavailable recipe provenance. Later complex certificates do not establish this particular experiment ran.

Evidence: [reports/TRACKING-historical.md](https://github.com/rohanarun/integer-mult-bounds/blob/fa8ab946df57ebadae1a470b637c2a590a0a5317/research/campaign-100-results/reports/TRACKING-historical.md)

## 10. Joint enumeration of orientation × design × matching

Status: `not_evidenced`. No execution result located in the archived campaign evidence; do not count this proposal as a completed test.

Evidence: No located execution result.

## 11. Lagrangian DP per register

Status: `partial_experiment`. Compound/free-form frame moves were tested; a full Lagrangian register-path DP was not implemented in the surviving evidence.

Evidence: [reports/G-RESULT.md](https://github.com/rohanarun/integer-mult-bounds/blob/fa8ab946df57ebadae1a470b637c2a590a0a5317/research/campaign-100-results/reports/G-RESULT.md)

## 12. GPU exhaustive entrance census

Status: `bounded_no_gain`. CPU read-span census added 5,496 rank-2/3/4 candidates and changed packing value by zero on tested seeds. No broad GPU search over arbitrary rank-3 to rank-8 subspaces.

Evidence: [reports/F-RESULT.md](https://github.com/rohanarun/integer-mult-bounds/blob/fa8ab946df57ebadae1a470b637c2a590a0a5317/research/campaign-100-results/reports/F-RESULT.md)

## 13. 10⁶ restart packings

Status: `partial_gain`. About 16,000 packings, not one million. Best proxy improvement about 4.9 phi; kappa unchanged because that historical complex supplier capped it.

Evidence: [reports/K-RESULT.md](https://github.com/rohanarun/integer-mult-bounds/blob/fa8ab946df57ebadae1a470b637c2a590a0a5317/research/campaign-100-results/reports/K-RESULT.md)

## 14. Symmetry-reduced word

Status: `bounded_no_gain`. The tested word had trivial effective automorphism structure after identical-record ambiguity; no symmetry compression gain.

Evidence: [reports/F-RESULT.md](https://github.com/rohanarun/integer-mult-bounds/blob/fa8ab946df57ebadae1a470b637c2a590a0a5317/research/campaign-100-results/reports/F-RESULT.md)

## 15. Hard-coded optimal small instance, then lift

Status: `partial_gain`. p=6 gate-frame model solved optimally within its candidate set; p=5 had no positive price and larger solves were bounded/time-limited. No exact optimum over every legal small word or general lift.

Evidence: [reports/H-RESULT.md](https://github.com/rohanarun/integer-mult-bounds/blob/fa8ab946df57ebadae1a470b637c2a590a0a5317/research/campaign-100-results/reports/H-RESULT.md)

